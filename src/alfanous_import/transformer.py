#!/usr/bin/env python
import json
import logging
import os
import os.path

# Standard-text particles that fuse with the following word in the corpus.
# Defined at module level so the pre-pass loop never recreates the set.
_PARTICLES = {"يا", "ويا", "ها"}

# Transliteration equivalents of _PARTICLES (lowercase; compared
# case-insensitively so that sentence-initial "Ya"/"Waya" and mid-sentence
# "ya"/"waya" are both matched).
#   يا  → "ya"
#   ويا → "waya"  (the و prefix is fused: wa + ya)
#   ها  → "ha"
_TRANSLIT_PARTICLES = {"ya", "waya", "ha"}

# Line fields that require whitespace stripping during doc building.
_STRIP_FIELDS = frozenset({"chapter", "topic", "subtopic"})

from whoosh import fields
from whoosh.fields import Schema
from whoosh.filedb.filestore import FileStorage

from alfanous import text_processing
from alfanous.constants import QURAN_TOTAL_VERSES


logging.basicConfig(level=logging.INFO)


def _load_corpus_words(corpus_path):
    """Read a Quranic Corpus morphology file and return word occurrences grouped
    by ``(sura_id, aya_id)``.

    Supports two formats, detected by file extension:

    * ``.txt`` — tab-separated v0.4 format (``quranic-corpus-morphology-0.4.txt``)
    * ``.txt`` — tab-separated v0.4 format (``quranic-corpus-morphology-0.4.txt``)

    Each entry is a flat dict whose keys match the word-child search fields
    defined in ``fields.json`` (table_name="aya", ids 100-124).

    :param corpus_path: Absolute or relative path to the corpus file.
    :returns: ``defaultdict(list)`` keyed by ``(sura_id, aya_id)``.
    """
    if corpus_path and corpus_path.endswith(".txt"):
        return _load_corpus_words_txt(corpus_path)
    return _load_corpus_words_xml(corpus_path)


def _load_corpus_words_txt(corpus_path):
    """Parse the tab-separated Quranic Corpus morphology v0.4 text file.

    Format (one row per morpheme segment)::

        LOCATION        FORM    TAG     FEATURES
        (1:1:1:1)       bi      P       PREFIX|bi+
        (1:1:1:2)       somi    N       STEM|POS:N|LEM:{som|ROOT:smw|M|GEN
        (1:1:2:1)       {ll~ahi PN      STEM|POS:PN|LEM:{ll~ah|ROOT:Alh|GEN

    Words are grouped by ``(sura, aya, word_pos)``.  The full Arabic word form
    is reconstructed by converting all segment FORM values from Buckwalter
    transliteration.  Morphological features are taken from the STEM segment.

    :param corpus_path: Path to the ``.txt`` corpus file.
    :returns: ``defaultdict(list)`` keyed by ``(sura_id, aya_id)``.
    """
    import re as _re2
    from collections import defaultdict, OrderedDict
    from alfanous_import.quran_corpus_reader.constants import (
        BUCKWALTER2UNICODE, POS, PGN, PGNclass, VERB, NOM, DERIV, PREFIX,
    )
    # _INV_POS maps raw tag (e.g. "V") → category name (e.g. "Verbs"), matching
    # what the XML reader stored in the "type" field via _reverse_class(POSclass).
    from alfanous_import.quran_corpus_reader.main import _INV_POS
    from alfanous.text_processing import QArabicSymbolsFilter

    def _b2u(s):
        import unicodedata
        raw = "".join(BUCKWALTER2UNICODE.get(ch, ch) for ch in s)
        return unicodedata.normalize('NFC', raw)

    _LOC_RE = _re2.compile(r'\((\d+):(\d+):(\d+):(\d+)\)')

    def _parse_stem_features(features):
        """Return a dict of morphological attributes from a STEM feature string."""
        f = {}
        parts = features.split('|')
        # Scan for ACT PCPL / PASS PCPL two-token combos first
        prev = None
        deriv_skip = set()
        for idx, part in enumerate(parts):
            if prev in ('ACT', 'PASS') and part == 'PCPL':
                combo = prev + ' PCPL'
                deriv_info = DERIV.get(combo, (None, None))
                f['derivation'] = deriv_info[1]
                deriv_skip.add(idx - 1)
                deriv_skip.add(idx)
            prev = part

        for idx, part in enumerate(parts):
            if idx in deriv_skip or part in ('STEM', 'PCPL'):
                continue
            if ':' in part:
                key, val = part.split(':', 1)
                if key == 'POS':
                    pos_info = POS.get(val, (None, None))
                    f['arabicpos']  = pos_info[0]
                    f['englishpos'] = pos_info[1]
                    # type stores the English category name (e.g. "Verbs") to
                    # match what the XML reader stored via _INV_POS lookup.
                    type_list = _INV_POS.get(val)
                    f['type'] = type_list[0] if type_list else val
                elif key == 'LEM':
                    f['arabiclemma'] = _b2u(val)
                elif key == 'ROOT':
                    f['arabicroot'] = _b2u(val)
                elif key == 'MOOD':
                    verb_info = VERB.get(val, (None, None))
                    f['arabicmood']   = verb_info[0]
                    f['englishmood']  = verb_info[1]
                elif key == 'SP':
                    f['arabicspecial'] = _b2u(val)
            elif part in PGN:
                for field, tags in PGNclass.items():
                    if part in tags:
                        f[field] = PGN[part]
            elif part in ('NOM', 'ACC', 'GEN'):
                nom_info = NOM.get(part, (None, None))
                f['arabiccase']   = nom_info[0]
                f['englishcase']  = nom_info[1]
            elif part in ('DEF', 'INDEF'):
                nom_info = NOM.get(part, (None, None))
                f['arabicstate']   = nom_info[0]
                f['englishstate']  = nom_info[1]
            elif part in ('PERF', 'IMPF', 'IMPV'):
                f['aspect'] = VERB.get(part, (None, None))[1]
            elif part in ('ACT', 'PASS'):
                f['voice'] = VERB.get(part, (None, None))[1]
            elif part in ('(I)', '(II)', '(III)', '(IV)', '(V)', '(VI)',
                          '(VII)', '(VIII)', '(IX)', '(X)', '(XI)', '(XII)'):
                f['form'] = VERB.get(part, (None, None))[1]
            elif part == 'VN':
                f['derivation'] = DERIV.get('VN', (None, None))[1]
        return f

    qasf = QArabicSymbolsFilter(
        shaping=True, tashkil=True, spellerrors=False,
        hamza=False, uthmani_symbols=True,
    )
    qasf_spelled = QArabicSymbolsFilter(
        shaping=True, tashkil=True, spellerrors=True,
        hamza=True, uthmani_symbols=True,
    )

    # words_buf: OrderedDict keyed by (sura, aya, word_pos) →
    #   {'segs': [(seg_pos, bw_form, feat_type, features), ...]}
    words_buf = OrderedDict()
    result = defaultdict(list)

    try:
        with open(corpus_path, encoding='utf-8') as fh:
            for raw_line in fh:
                line = raw_line.rstrip('\n')
                if not line or line.startswith('#') or line.startswith('LOCATION'):
                    continue
                parts = line.split('\t')
                if len(parts) < 4:
                    continue
                loc, bw_form, _tag, features = parts[0], parts[1], parts[2], parts[3]
                m = _LOC_RE.match(loc)
                if not m:
                    continue
                sura, aya, word_pos, seg_pos = (int(m.group(i)) for i in range(1, 5))
                key = (sura, aya, word_pos)
                feat_type = features.split('|', 1)[0]  # PREFIX / STEM / SUFFIX
                if key not in words_buf:
                    words_buf[key] = {'segs': []}
                words_buf[key]['segs'].append((seg_pos, bw_form, feat_type, features))

        gid = 0
        for (sura, aya, word_pos), wdata in words_buf.items():
            segs = sorted(wdata['segs'], key=lambda x: x[0])

            # Full Uthmanic word form = all segment BW forms concatenated → Arabic
            word_text = _b2u("".join(s[1] for s in segs))

            # Extract morphological info from the STEM segment
            stem_feats = {}
            prefix_parts = []
            suffix_parts = []
            for _, bw_form, feat_type, features in segs:
                if feat_type == 'STEM':
                    stem_feats = _parse_stem_features(features)
                elif feat_type == 'PREFIX':
                    arabic_tok = _b2u(bw_form)
                    if arabic_tok:
                        prefix_parts.append(arabic_tok)
                elif feat_type == 'SUFFIX':
                    arabic_tok = _b2u(bw_form)
                    if arabic_tok:
                        suffix_parts.append(arabic_tok)

            prefix_str = ";".join(prefix_parts) or None
            suffix_str = ";".join(suffix_parts) or None

            gid += 1
            entry = {
                "word_gid":     gid,
                "word_id":      word_pos,
                "aya_id":       aya,
                "sura_id":      sura,
                "word":         word_text,
                "normalized":   qasf.normalize_all(word_text) or None,
                "spelled":      qasf_spelled.normalize_all(word_text) or None,
                # English (stored-only, not indexed)
                "englishpos":   stem_feats.get("englishpos"),
                "type":         stem_feats.get("type"),
                "englishcase":  stem_feats.get("englishcase"),
                # Arabic (primary, indexed)
                "pos":          stem_feats.get("arabicpos"),
                "root":         stem_feats.get("arabicroot"),
                # arabiclemma stores the original vocalized Arabic form; lemma
                # stores the normalized (tashkeel-stripped) form so that
                # KEYWORD-field exact-match queries (e.g. lemma:يمين) succeed
                # regardless of whether the user types diacritics or not.
                "arabiclemma":  stem_feats.get("arabiclemma"),
                "lemma":        qasf.normalize_all(stem_feats.get("arabiclemma") or "") or None,
                "special":      stem_feats.get("arabicspecial"),
                "mood":         stem_feats.get("arabicmood"),
                "case":         stem_feats.get("arabiccase"),
                "state":        stem_feats.get("arabicstate"),
                # Unchanged fields
                "prefix":       prefix_str,
                "suffix":       suffix_str,
                "gender":       stem_feats.get("gender"),
                "number":       stem_feats.get("number"),
                "person":       stem_feats.get("person"),
                "form":         stem_feats.get("form"),
                "voice":        stem_feats.get("voice"),
                "derivation":   stem_feats.get("derivation"),
                "aspect":       stem_feats.get("aspect"),
            }
            result[(sura, aya)].append(entry)

        logging.info("Loaded %d word occurrences from corpus.", gid)
    except Exception as exc:
        logging.warning("Failed to load corpus words from %s: %s", corpus_path, exc)
    return result


def _load_corpus_words_xml(corpus_path):
    """Read the legacy XML Quranic Corpus morphology file.

    :param corpus_path: Absolute or relative path to the corpus XML file.
    :returns: ``defaultdict(list)`` keyed by ``(sura_id, aya_id)``.
    """
    from collections import defaultdict
    from alfanous_import.quran_corpus_reader.main import API as CorpusAPI
    from alfanous.text_processing import QArabicSymbolsFilter

    result = defaultdict(list)
    try:
        api = CorpusAPI(source=corpus_path)
        qasf = QArabicSymbolsFilter(
            shaping=True, tashkil=True, spellerrors=False,
            hamza=False, uthmani_symbols=True,
        )
        qasf_spelled = QArabicSymbolsFilter(
            shaping=True, tashkil=True, spellerrors=True,
            hamza=True, uthmani_symbols=True,
        )
        gid = 0
        for iteration in api.all_words_generator():
            gid += 1
            word_text = iteration["word"]
            base = iteration["morphology"]["base"]
            first = base[0] if base else {}
            prefixes = iteration["morphology"].get("prefixes", [])
            suffixes = iteration["morphology"].get("suffixes", [])

            prefix_str = ";".join(p.get("arabictoken", "") for p in prefixes) or None
            suffix_str = ";".join(s.get("arabictoken", "") for s in suffixes) or None

            entry = {
                "word_gid":     gid,
                "word_id":      iteration["word_id"],
                "aya_id":       iteration["aya_id"],
                "sura_id":      iteration["sura_id"],
                "word":         word_text,
                "normalized":   qasf.normalize_all(word_text) or None,
                "spelled":      qasf_spelled.normalize_all(word_text) or None,
                # English (stored-only, not indexed)
                "englishpos":   first.get("pos") or None,
                "type":         first.get("type") or None,
                "englishcase":  first.get("case") or None,
                # Arabic (primary, indexed)
                "pos":          first.get("arabicpos") or None,
                "root":         first.get("arabicroot") or None,
                # arabiclemma stores the original vocalized Arabic form; lemma
                # stores the normalized (tashkeel-stripped) form so that
                # KEYWORD-field exact-match queries (e.g. lemma:يمين) succeed
                # regardless of whether the user types diacritics or not.
                "arabiclemma":  first.get("arabiclemma") or None,
                "lemma":        qasf.normalize_all(first.get("arabiclemma") or "") or None,
                "special":      first.get("arabicspecial") or None,
                "mood":         first.get("arabicmood") or None,
                "case":         first.get("arabiccase") or None,
                "state":        first.get("arabicstate") or None,
                # Unchanged fields
                "prefix":       prefix_str,
                "suffix":       suffix_str,
                "gender":       first.get("gender") or None,
                "number":       first.get("number") or None,
                "person":       first.get("person") or None,
                "form":         first.get("form") or None,
                "voice":        first.get("voice") or None,
                "derivation":   first.get("derivation") or None,
                "aspect":       first.get("aspect") or None,
            }
            result[(iteration["sura_id"], iteration["aya_id"])].append(entry)

        logging.info("Loaded %d word occurrences from corpus.", gid)
    except Exception as exc:
        logging.warning("Failed to load corpus words from %s: %s", corpus_path, exc)
    return result

import re as _re
import zipfile as _zipfile
from collections import defaultdict

# Pre-compiled pattern used by every translation zip reader.
_PROPS_RE = _re.compile(r"[^=\r\n#]+")

# Cache of per-delimiter line-splitting patterns so each unique delimiter
# is compiled at most once across all translation zips.
_DELIMITER_PATTERNS: "dict[str, _re.Pattern[str]]" = {}


def _iter_translation_zips(store_path):
    """Yield ``(props_dict, lines_list)`` for every valid ``.trans.zip``
    found under *store_path*, reading entirely from memory without
    extracting to disk.

    Zips that are missing required keys or have the wrong line count are
    skipped with a warning.  Callers that only need properties (not the
    full lines list) should pass ``lines=False`` — not applicable here, but
    the helper is shared with :mod:`alfanous_import.updater`.
    """
    if not os.path.isdir(store_path):
        logging.warning("Translations store path not found, skipping: %s", store_path)
        return
    for filename in sorted(os.listdir(store_path)):
        if not filename.endswith(".trans.zip"):
            continue
        zip_path = os.path.join(store_path, filename)
        try:
            with _zipfile.ZipFile(zip_path, "r") as zf:
                # ── properties ──────────────────────────────────────────
                props: dict = {}
                with zf.open("translation.properties") as pf:
                    for raw_line in pf.read().decode("utf-8", errors="replace").splitlines():
                        parts = _PROPS_RE.findall(raw_line)
                        if len(parts) == 2:
                            props[parts[0]] = parts[1]
                required = {"id", "file", "lineDelimiter"}
                if not required.issubset(props):
                    logging.warning(
                        "Translation %s missing keys %s, skipping",
                        filename, required - props.keys(),
                    )
                    continue
                # ── verse lines ─────────────────────────────────────────
                with zf.open(props["file"]) as tf:
                    content = tf.read().decode("utf-8", errors="replace")
                delim = props["lineDelimiter"]
                if delim not in _DELIMITER_PATTERNS:
                    _DELIMITER_PATTERNS[delim] = _re.compile("[^" + delim + "]+")
                linerx = _DELIMITER_PATTERNS[delim]
                lines = linerx.findall(content)
                if len(lines) != QURAN_TOTAL_VERSES:
                    logging.warning(
                        "Translation %s has %d lines (expected %d), skipping",
                        props.get("id", filename), len(lines), QURAN_TOTAL_VERSES,
                    )
                    continue
        except (OSError, KeyError, _zipfile.BadZipFile) as exc:
            logging.warning("Failed to load translation %s: %s", filename, exc)
            continue
        yield props, lines


def _load_all_translations(translations_store_path):
    """Return a mapping ``{trans_id: {"lines": [...], "lang": ..., "author": ...}}``
    for every valid ``.trans.zip`` found under *translations_store_path*.

    Reads entirely in memory — no temp-directory extraction.
    Each entry's ``"lines"`` list has exactly :data:`QURAN_TOTAL_VERSES` items,
    indexed from 0 (gid = index + 1).
    """
    result = {}
    for props, lines in _iter_translation_zips(translations_store_path):
        trans_id = props["id"]
        result[trans_id] = {
            "lines":  lines,
            "lang":   props.get("language", ""),
            "author": props.get("name", ""),
        }
        logging.info("Loaded translation: %s (%d verses)", trans_id, len(lines))
    return result


def _make_writer(ix, procs: int, multisegment: bool):
    """Open an index writer, using multiple processes when *procs* > 1.

    :param ix: Open Whoosh index.
    :param procs: Number of writer processes.  Values > 1 create a
        ``MpWriter`` (multi-process).  ``procs=1`` creates a plain
        ``SegmentWriter``.
    :param multisegment: When *procs* > 1, skip merging sub-segments into
        one at commit time.  Ignored for ``procs=1``.
    """
    if procs > 1:
        return ix.writer(procs=procs, multisegment=multisegment)
    return ix.writer()


class Transformer:
    def __init__(self, index_path, resource_path):
        if not (os.path.exists(index_path)):
            os.makedirs(index_path)

        self.index_path = index_path
        self.resource_path = resource_path

    def print_to_json(self, d, filename):
        with  open(f"{self.resource_path}{filename}.generated.json", "w") as f:
            import json
            json.dump(d, f, indent=4, sort_keys=True, ensure_ascii=False)

        return "OK"

    def get_fields(self, tablename):
        with open(f"{self.resource_path}fields.json") as field_file:
            return [field for field in json.load(field_file) if field["table_name"] == tablename]

    def build_schema(self, tablename):
        """build schema from field table"""

        # Parameters accepted by Whoosh field constructors that may appear in
        # fields.json.  ``scorable`` is included so filter-only fields can be
        # explicitly marked non-scoring.  Boolean False values must be passed
        # through (not filtered), hence the ``is not None`` guard.
        _PASSABLE = {'analyzer', 'stored', 'unique', 'spelling', 'scorable', 'phrase'}

        kwargs = {}
        for line in self.get_fields(tablename):
            search_name = line.get('search_name')
            if not search_name:
                continue  # skip documentation-only rows without a search name
            field_type = str(line['type']).upper() or "STORED"

            # STORED fields take no constructor arguments — always use STORED()
            if field_type == "STORED":
                kwargs[search_name] = fields.STORED()
                continue

            params = {}
            for k, v in line.items():
                if k not in _PASSABLE or v is None:
                    continue
                params[k] = getattr(text_processing, v) if k == 'analyzer' else v

            kwargs[search_name] = getattr(fields, field_type)(**params)

        return Schema(**kwargs)

    def transfer(self, ix, tablename="aya", translations_store_path=None,
                 corpus_path=None, merge=True, optimize=False, procs=1,
                 multisegment=False, batch_size=0):
        """Write all records from *tablename*.json into the index *ix*.

        :param merge: Passed to ``writer.commit()`` on the final commit.
            Use ``merge=False`` to skip segment merging (faster, produces
            multiple segments).
        :param optimize: When ``True``, merge all segments into a single
            segment on the final commit.  Produces the smallest index size
            and fastest read performance.  Overrides *merge*.
        :param procs: Number of writer processes.  ``procs > 1`` enables
            ``MpWriter`` for parallel indexing across CPU cores.
        :param multisegment: When *procs* > 1, skip merging sub-process
            segments into one at commit time.  Faster for bulk imports.
        :param batch_size: Commit after every *batch_size* top-level records
            and reopen the writer.  ``0`` (default) means a single commit at
            the end.  Intermediate commits always use ``merge=False``
            regardless of the *merge* parameter.
        """
        with open(f"{self.resource_path}{tablename}.json") as data_file:
            data_list = json.load(data_file)

        logging.info(f"writing documents in index (total: {len(data_list)}) ....")
        writer = _make_writer(ix, procs, multisegment)
        cpt = 0
        try:
            # Build a mapping from source field name → list of search field names.
            # A single source field (e.g. "standard") may feed multiple index fields
            # with different analyzers (e.g. aya, aya_ac, aya_fuzzy).
            fields_mapping: dict = defaultdict(list)
            for f in self.get_fields(tablename):
                fields_mapping[f["name"]].append(f["search_name"])

            # Load all translation zips if a store path was provided.
            # translations: {trans_id: {"lines": [6236 texts], "lang": ..., "author": ...}}
            translations = {}
            if translations_store_path and tablename == "aya":
                translations = _load_all_translations(translations_store_path)

            # Load corpus word occurrences if a corpus path was provided.
            # words_by_aya: {(sura_id, aya_id): [word_entry, ...]}
            words_by_aya = {}
            if corpus_path and tablename == "aya":
                words_by_aya = _load_corpus_words(corpus_path)

            # Build position-based mappings from the aya standard text and
            # transliteration.  For each aya where the space-split word count
            # matches the corpus word count we can assign each corpus word the
            # corresponding standard-script and transliteration word by index.
            # When transliteration token count ≠ corpus word count the aya is
            # recorded in special_cases.json for manual mapping and no
            # word_transliteration is stored for that aya.
            # {(sura_id, aya_id): [word, ...]}
            aya_standard_words: dict = {}
            aya_translit_words: dict = {}
            _translit_special_cases: list = []
            if words_by_aya and tablename == "aya":
                for line in data_list:
                    sid = line.get("sura_id")
                    aid = line.get("aya_id")
                    key = (sid, aid)
                    corpus_words_for_key = words_by_aya.get(key, [])
                    if not corpus_words_for_key:
                        continue
                    corpus_count = len(corpus_words_for_key)
                    std_tokens = line.get("standard", "").split()
                    if len(std_tokens) == corpus_count:
                        aya_standard_words[key] = std_tokens
                    else:
                        # Try to recover when std token count ≠ corpus count.
                        # The standard text sometimes spells fused corpus tokens as
                        # separate words.  Three strategies are tried in order:
                        #
                        # 1. Particle collapse: يا / ويا / ها + next → next only.
                        #    e.g. "يا أيها" → "أيها"  (covers ~355 ayas, diff=1)
                        #
                        # 2. Extended particle merge: merge (diff+1) tokens starting
                        #    at the first particle, stored space-joined.
                        #    e.g. "يا ابن أم" (diff=2) → "يا ابن أم"
                        #
                        # 3. Prefix merge: no particle found; merge the leading
                        #    (diff+1) tokens space-joined.
                        #    e.g. "وأن لو" (diff=1) → "وأن لو"
                        diff = len(std_tokens) - corpus_count
                        resolved = None

                        # Strategy 1: particle collapse.
                        merged: list = []
                        i = 0
                        while i < len(std_tokens):
                            tok = std_tokens[i]
                            if tok in _PARTICLES and i + 1 < len(std_tokens):
                                merged.append(std_tokens[i + 1])
                                i += 2
                            else:
                                merged.append(tok)
                                i += 1
                        if len(merged) == corpus_count:
                            resolved = merged

                        # Strategy 2: extended particle merge.
                        if resolved is None and diff > 0:
                            for pi, tok in enumerate(std_tokens):
                                if tok in _PARTICLES and pi + diff < len(std_tokens):
                                    candidate = (
                                        std_tokens[:pi]
                                        + [" ".join(std_tokens[pi:pi + diff + 1])]
                                        + std_tokens[pi + diff + 1:]
                                    )
                                    if len(candidate) == corpus_count:
                                        resolved = candidate
                                        break

                        # Strategy 3: prefix merge (no particle anchor found).
                        if resolved is None and diff > 0:
                            candidate = (
                                [" ".join(std_tokens[:diff + 1])]
                                + std_tokens[diff + 1:]
                            )
                            if len(candidate) == corpus_count:
                                resolved = candidate

                        if resolved is not None:
                            aya_standard_words[key] = resolved

                    tr_tokens = line.get("transliteration", "").split()
                    if len(tr_tokens) == corpus_count:
                        aya_translit_words[key] = tr_tokens
                    elif tr_tokens:
                        # Token count mismatch.  Apply the same three alignment
                        # strategies used for the standard-text tokens above,
                        # substituting _TRANSLIT_PARTICLES for _PARTICLES and
                        # comparing case-insensitively (sentence-initial "Ya"
                        # and mid-sentence "ya" are the same particle).
                        tr_diff = len(tr_tokens) - corpus_count
                        tr_resolved = None

                        # Strategy 1: particle collapse — drop each particle and
                        # keep the following word, mirroring how يا/ها fuse with
                        # the next word in the Quranic Corpus.
                        tr_merged: list = []
                        j = 0
                        while j < len(tr_tokens):
                            ttok = tr_tokens[j]
                            if ttok.lower() in _TRANSLIT_PARTICLES and j + 1 < len(tr_tokens):
                                tr_merged.append(tr_tokens[j + 1])
                                j += 2
                            else:
                                tr_merged.append(ttok)
                                j += 1
                        if len(tr_merged) == corpus_count:
                            tr_resolved = tr_merged

                        # Strategy 2: extended particle merge — when diff > 1
                        # the particle plus the following *diff* tokens are
                        # joined with spaces into a single token.
                        if tr_resolved is None and tr_diff > 0:
                            for pi, ttok in enumerate(tr_tokens):
                                if (ttok.lower() in _TRANSLIT_PARTICLES
                                        and pi + tr_diff < len(tr_tokens)):
                                    candidate = (
                                        tr_tokens[:pi]
                                        + [" ".join(tr_tokens[pi:pi + tr_diff + 1])]
                                        + tr_tokens[pi + tr_diff + 1:]
                                    )
                                    if len(candidate) == corpus_count:
                                        tr_resolved = candidate
                                        break

                        # Strategy 3: prefix merge — no particle anchor found;
                        # merge the leading (diff+1) tokens.
                        if tr_resolved is None and tr_diff > 0:
                            candidate = (
                                [" ".join(tr_tokens[:tr_diff + 1])]
                                + tr_tokens[tr_diff + 1:]
                            )
                            if len(candidate) == corpus_count:
                                tr_resolved = candidate

                        if tr_resolved is not None:
                            aya_translit_words[key] = tr_resolved
                        else:
                            # All strategies failed — record for manual review.
                            _translit_special_cases.append({
                                "sura_id":                    sid,
                                "aya_id":                     aid,
                                "corpus_word_count":          corpus_count,
                                "transliteration_word_count": len(tr_tokens),
                                "transliteration":            line.get("transliteration", ""),
                            })

            # Write transliteration mismatches to store/special_cases.json so
            # they can be reviewed and resolved manually.
            if _translit_special_cases:
                _sc_path = self.resource_path + "special_cases.json"
                with open(_sc_path, "w", encoding="utf-8") as _sc_f:
                    json.dump(_translit_special_cases, _sc_f, indent=4, ensure_ascii=False)
                logging.info(
                    "Wrote %d transliteration special cases to %s",
                    len(_translit_special_cases), _sc_path,
                )

            if tablename == "aya":
                # Pre-compute schema field names once.
                _schema_names = set(ix.schema.names())
                _has_word_standard        = "word_standard"        in _schema_names
                _has_word_transliteration = "word_transliteration" in _schema_names
                _has_aya_lemma            = "aya_lemma"            in _schema_names
                _has_aya_root             = "aya_root"             in _schema_names

                # Pre-build aya_lemma and aya_root text for each aya from
                # word-child data.  Each word's lemma (or root) is used; when
                # the morphological value is missing, the word's normalised
                # form is used as a fallback so that every word position is
                # represented and phrase-length queries still align.
                _aya_lemma_text: dict = {}
                _aya_root_text: dict = {}
                if (_has_aya_lemma or _has_aya_root) and words_by_aya:
                    for _key, _words_list in words_by_aya.items():
                        if _has_aya_lemma:
                            _lemmas = []
                            for _w in _words_list:
                                # Use the word's normalized form as fallback
                                # to maintain word-position alignment.
                                _l = _w.get("lemma") or _w.get("normalized") or ""
                                _lemmas.append(_l)
                            _aya_lemma_text[_key] = " ".join(_lemmas)
                        if _has_aya_root:
                            _roots = []
                            for _w in _words_list:
                                _r = _w.get("root") or _w.get("normalized") or ""
                                _roots.append(_r)
                            _aya_root_text[_key] = " ".join(_roots)

                # Pre-compute per-translation metadata so the inner loop only
                # does an index lookup + cheap dict copy rather than recomputing
                # f-strings and set lookups for every one of the 6 236 parent docs.
                # Each entry: (lines_list, lang_field_or_None, base_child_dict)
                trans_meta: list = []
                for trans_id, tdata in translations.items():
                    lang = tdata["lang"]
                    lf = f"text_{lang}" if lang else None
                    if lf and lf not in _schema_names:
                        lf = None
                    trans_meta.append((
                        tdata["lines"],
                        lf,
                        {
                            "kind":         "translation",
                            "trans_id":     trans_id,
                            "trans_lang":   lang,
                            "trans_author": tdata["author"],
                        },
                    ))

                # Pre-compute the subset of word-entry keys that exist in the
                # schema.  All word entries share the same keys, so one sample
                # is sufficient.  This replaces a per-word `k in _schema_names`
                # check across all 75 973 word docs.
                _word_schema_keys: list = []
                for _words in words_by_aya.values():
                    if _words:
                        _word_schema_keys = [k for k in _words[0] if k in _schema_names]
                        break

            for line in data_list:
                doc = {}
                for k, v in line.items():
                    if k in fields_mapping:
                        # Strip whitespace from a small set of text fields inline
                        # rather than copying the entire line dict beforehand.
                        if k in _STRIP_FIELDS and isinstance(v, str):
                            v = v.strip()
                        for search_name in fields_mapping[k]:
                            doc[search_name] = v

                if tablename == "aya":
                    # Write parent aya doc + child docs (translations + words) as a nested group.
                    gid = line.get("gid")
                    sura_id = line.get("sura_id")
                    aya_id = line.get("aya_id")
                    doc["kind"] = "aya"
                    # Add pre-built aya_lemma / aya_root text from word-child data.
                    _aya_key = (sura_id, aya_id)
                    if _has_aya_lemma and _aya_key in _aya_lemma_text:
                        doc["aya_lemma"] = _aya_lemma_text[_aya_key]
                    if _has_aya_root and _aya_key in _aya_root_text:
                        doc["aya_root"] = _aya_root_text[_aya_key]
                    writer.start_group()
                    writer.add_document(**doc)
                    if gid is not None and trans_meta:
                        idx = gid - 1  # 0-based index into translation lines
                        for lines, lang_field, base in trans_meta:
                            text = lines[idx]
                            child_doc = {**base, "gid": gid, "trans_text": text}
                            # Store sura_id and aya_id directly on every
                            # translation child so they are available for
                            # faceting and filtering without a parent lookup.
                            if sura_id is not None:
                                child_doc["sura_id"] = sura_id
                            if aya_id is not None:
                                child_doc["aya_id"] = aya_id
                            if lang_field:
                                child_doc[lang_field] = text
                            writer.add_document(**child_doc)
                    # Add word children from quranic corpus (nested alongside translations).
                    if words_by_aya and sura_id is not None and aya_id is not None:
                        key = (sura_id, aya_id)
                        corpus_words_for_aya = words_by_aya.get(key, [])
                        std_tokens = aya_standard_words.get(key, [])
                        tr_tokens  = aya_translit_words.get(key, [])
                        for pos, w in enumerate(corpus_words_for_aya):
                            word_doc = {k: w[k] for k in _word_schema_keys
                                        if w[k] is not None}
                            if _has_word_standard and pos < len(std_tokens):
                                word_doc["word_standard"] = std_tokens[pos]
                            if _has_word_transliteration and pos < len(tr_tokens):
                                word_doc["word_transliteration"] = tr_tokens[pos]
                            word_doc["gid"] = gid
                            writer.add_document(kind="word", **word_doc)
                    writer.end_group()
                else:
                    writer.add_document(**doc)

                cpt += 1
                if batch_size > 0 and cpt % batch_size == 0:
                    writer.commit(merge=False)
                    writer = _make_writer(ix, procs, multisegment)
                    logging.info(f" - batch commit at {cpt} records")
                elif not cpt % 1559:
                    logging.info(f" - milestone:  {cpt} ( {cpt * 100 / len(data_list)}% )")

            logging.info("done.")
            writer.commit(merge=merge, optimize=optimize or None)
        except Exception:
            try:
                writer.cancel()
            except Exception:
                pass
            raise

    def build_docindex(self, schema, tablename="aya", translations_store_path=None,
                       corpus_path=None, merge=True, optimize=False, procs=1,
                       multisegment=False, batch_size=0):
        assert schema, "schema is empty"
        ix = FileStorage(self.index_path).create_index(schema)
        try:
            self.transfer(ix, tablename, translations_store_path=translations_store_path,
                          corpus_path=corpus_path, merge=merge, optimize=optimize,
                          procs=procs, multisegment=multisegment, batch_size=batch_size)
            # ix.optimize()  # merges all segments into one; slow on large corpora —
            # uncomment if a single-segment index (smaller file count) is required
        finally:
            ix.close()
        return "OK"


if __name__ == "__main__":
    T = Transformer(index_path="../../indexes/main/", resource_path="../../../store/")
