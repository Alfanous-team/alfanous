#!/usr/bin/env python
import json
import logging
import os
import os.path


from whoosh import fields
from whoosh.fields import Schema
from whoosh.filedb.filestore import FileStorage

from alfanous import text_processing
from alfanous.constants import QURAN_TOTAL_VERSES


logging.basicConfig(level=logging.INFO)


def _load_corpus_words(corpus_path):
    """Read ``quranic-corpus-morpology.xml`` and return word occurrences grouped
    by ``(sura_id, aya_id)``.

    Each entry is a flat dict whose keys match the word-child search fields
    defined in ``fields.json`` (table_name="aya", ids 100-124).

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
                "englishmood":  first.get("mood") or None,
                "englishcase":  first.get("case") or None,
                "englishstate": first.get("state") or None,
                # Arabic (primary, indexed)
                "pos":          first.get("arabicpos") or None,
                "root":         first.get("arabicroot") or None,
                "lemma":        first.get("arabiclemma") or None,
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


def _load_all_translations(translations_store_path):
    """Return a mapping ``{trans_id: {"lines": [...], "lang": ..., "author": ...}}``
    for every ``.trans.zip`` found under *translations_store_path*.

    Each entry's ``"lines"`` list has exactly :data:`QURAN_TOTAL_VERSES` items,
    indexed from 0 (gid = index + 1).  Zips that cannot be parsed or have the
    wrong line count are skipped with a warning.
    """
    from alfanous_import.zekr_model_reader.main import TranslationModel

    result = {}
    if not os.path.isdir(translations_store_path):
        logging.warning("Translations store path not found, skipping: %s", translations_store_path)
        return result
    for filename in sorted(os.listdir(translations_store_path)):
        if not filename.endswith(".trans.zip"):
            continue
        zip_path = os.path.join(translations_store_path, filename)
        try:
            tm = TranslationModel(zip_path)
            props = tm.translation_properties()
            lines = tm.translation_lines(props)
            if len(lines) != QURAN_TOTAL_VERSES:
                logging.warning(
                    "Translation %s has %d lines (expected %d), skipping",
                    props.get("id", filename), len(lines), QURAN_TOTAL_VERSES,
                )
                continue
            trans_id = props["id"]
            result[trans_id] = {
                "lines": lines,
                "lang": props.get("language", ""),
                "author": props.get("name", ""),
            }
            logging.info("Loaded translation: %s (%d verses)", trans_id, len(lines))
        except (OSError, ValueError, AssertionError, KeyError) as exc:
            logging.warning("Failed to load translation %s: %s", filename, exc)
    return result


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
        field_file = open(f"{self.resource_path}fields.json")
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

            params = {}
            for k, v in line.items():
                if k not in _PASSABLE or v is None:
                    continue
                params[k] = getattr(text_processing, v) if k == 'analyzer' else v

            kwargs[search_name] = getattr(fields, field_type)(**params)

        return Schema(**kwargs)

    def transfer(self, ix, tablename="aya", translations_store_path=None,
                 corpus_path=None):
        data_file = open(f"{self.resource_path}{tablename}.json")
        data_list = json.load(data_file)

        logging.info(f"writing documents in index (total: {len(data_list)}) ....")
        writer = ix.writer()

        cpt = 0

        # Build a mapping from source field name → list of search field names.
        # A single source field (e.g. "standard") may feed multiple index fields
        # with different analyzers (e.g. aya, aya_ac, aya_fuzzy).
        from collections import defaultdict
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
        # When counts differ the aya is simply skipped (no word_standard stored).
        # {(sura_id, aya_id): [word, ...]}
        aya_standard_words: dict = {}
        aya_translit_words: dict = {}
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
                tr_tokens = line.get("transliteration", "").split()
                if len(tr_tokens) == corpus_count:
                    aya_translit_words[key] = tr_tokens

        if tablename == "aya":
            # Pre-compute schema field names once to:
            # (a) filter language-specific text_{lang} fields for translation children, and
            # (b) drop fields absent from the aya schema when writing word children
            #     (e.g. englishcase/englishpos/englishmood/englishstate live in the
            #     wordqc schema but not in the aya schema).
            _schema_names = set(ix.schema.names())
            # Boolean flags so the per-word loop avoids repeated set lookups.
            _has_word_standard       = "word_standard"       in _schema_names
            _has_word_transliteration = "word_transliteration" in _schema_names

        for line in data_list:
            # Normalize chapter/topic/subtopic
            if tablename == "aya":
                line = {**line,
                        'chapter': line.get('chapter', '').strip(),
                        'topic': line.get('topic', '').strip(),
                        'subtopic': line.get('subtopic', '').strip()}
            doc = {}
            for k, v in line.items():
                if k in fields_mapping:
                    for search_name in fields_mapping[k]:
                        doc[search_name] = v

            if tablename == "aya":
                # Write parent aya doc + child docs (translations + words) as a nested group.
                gid = line.get("gid")
                sura_id = line.get("sura_id")
                aya_id = line.get("aya_id")
                doc["kind"] = "aya"
                writer.start_group()
                writer.add_document(**doc)
                if gid is not None and translations:
                    idx = gid - 1  # 0-based index into translation lines
                    for trans_id, tdata in translations.items():
                        lang = tdata["lang"]
                        text = tdata["lines"][idx]
                        lang_field = f"text_{lang}" if lang else None
                        child_doc = dict(
                            kind="translation",
                            gid=gid,
                            trans_id=trans_id,
                            trans_lang=lang,
                            # trans_text kept as stored-only field for backward compat
                            trans_text=text,
                            trans_author=tdata["author"],
                        )
                        # Populate the language-specific stemmed field when
                        # it exists in the schema.
                        if lang_field and lang_field in _schema_names:
                            child_doc[lang_field] = text
                        writer.add_document(**child_doc)
                # Add word children from quranic corpus (nested alongside translations).
                if words_by_aya and sura_id is not None and aya_id is not None:
                    key = (sura_id, aya_id)
                    corpus_words_for_aya = words_by_aya.get(key, [])
                    std_tokens = aya_standard_words.get(key, [])
                    tr_tokens  = aya_translit_words.get(key, [])
                    for pos, w in enumerate(corpus_words_for_aya):
                        # Store the parent aya gid so word children can be
                        # fetched with the same gid-based nested query used
                        # for translations.  The word's own sequential
                        # identifier is preserved in the word_gid field.
                        word_doc = {k: v for k, v in w.items()
                                    if v is not None and k in _schema_names}
                        # Attach standard-script and transliteration words
                        # by matching position (only when count aligned).
                        if _has_word_standard and pos < len(std_tokens):
                            word_doc["word_standard"] = std_tokens[pos]
                        if _has_word_transliteration and pos < len(tr_tokens):
                            word_doc["word_transliteration"] = tr_tokens[pos]
                        # word_gid (word's own sequential counter) is included
                        # in word_doc via the comprehension above; it does not
                        # conflict with the parent aya gid assigned below.
                        word_doc["gid"] = gid
                        writer.add_document(kind="word", **word_doc)
                writer.end_group()
            else:
                writer.add_document(**doc)

            cpt += 1
            if not cpt % 1559:
                logging.info(f" - milestone:  {cpt} ( {cpt * 100 / len(data_list)}% )")

        logging.info("done.")
        writer.commit()

    def build_docindex(self, schema, tablename="aya", translations_store_path=None,
                       corpus_path=None):
        assert schema, "schema is empty"
        ix = FileStorage(self.index_path).create_index(schema)
        self.transfer(ix, tablename, translations_store_path=translations_store_path,
                      corpus_path=corpus_path)
        # ix.optimize()  # merges all segments into one; slow on large corpora —
        # uncomment if a single-segment index (smaller file count) is required
        return "OK"


if __name__ == "__main__":
    T = Transformer(index_path="../../indexes/main/", resource_path="../../../store/")
