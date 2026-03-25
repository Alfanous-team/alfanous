"""
Whoosh 2.7 query parser plugins for Arabic and Quranic search.

This module contains custom plugins that extend Whoosh's query parser
with Arabic-specific features like synonyms, derivations, spell errors,
tashkil (diacritics), and more.
"""

import logging
import re
from functools import lru_cache

from whoosh.qparser import TaggingPlugin, syntax
from whoosh.query import MultiTerm, NullQuery, Or, Term, Wildcard

from alfanous.data import syndict, antdict
from alfanous.text_processing import QArabicSymbolsFilter

logger = logging.getLogger(__name__)

# Regex for stripping Uthmanic annotation marks (U+06D6–U+06ED) from derivation
# result words.  These marks are Quran-specific symbols (small high letters,
# stops, verse counters) that must not appear in search terms.
_UTHMANI_ANNOTATION_RE = re.compile(r'[\u06D6-\u06ED]')

# Pre-instantiated filter used by TashkilQuery and DerivationQuery — avoids
# allocating a new QArabicSymbolsFilter object on every search execution.
_ASF_TASHKIL = QArabicSymbolsFilter(
    shaping=False, tashkil=True, spellerrors=False, hamza=False
)
# Pre-instantiated filter used by DerivationQuery for normalising the query word.
# uthmani_symbols=True ensures Uthmanic annotation marks (U+06D6–U+06ED) and
# ALEF_WASLA (U+0671) are stripped/replaced so that derivation lookups work
# when the input word is in Uthmanic script (e.g. ٱلۡهَدۡيِۖ).
_ASF_NORMALIZE = QArabicSymbolsFilter(
    shaping=True, tashkil=True, spellerrors=False, hamza=False, uthmani_symbols=True
)
# Pre-instantiated filter used by SpellErrorsQuery — avoids allocating a new
# QArabicSymbolsFilter on every SpellErrorsQuery instantiation.
_ASF_SPELL_ERRORS = QArabicSymbolsFilter(
    shaping=True, tashkil=False, spellerrors=True, hamza=True
)

# Word-child stored fields scanned when building the derivation lookup table
# at engine instantiation.
_DERIVATION_SEARCH_FIELDS = ('word', 'normalized', 'lemma', 'root', 'standard')

# Lazily-cached Arabic Snowball stemmer for DerivationQuery.  Populated on
# first use so that a missing pystemmer package does not cause an import error.
_arabic_stemmer = None


def _get_arabic_stemmer():
    """Return a cached Arabic Snowball Stemmer, or None if pystemmer is absent.

    Failure to import or initialise pystemmer is expected and handled
    gracefully: the stemmer is optional; when absent, derivation queries fall
    back to the un-stemmed normalised form.  The False sentinel ensures the
    import is attempted only once per process.
    """
    global _arabic_stemmer
    if _arabic_stemmer is None:
        try:
            import Stemmer as _Stemmer
            _arabic_stemmer = _Stemmer.Stemmer('arabic')
        except Exception as exc:  # ImportError or any initialisation error
            logger.debug("pystemmer Arabic stemmer unavailable: %s", exc)
            _arabic_stemmer = False  # sentinel: attempted but unavailable
    return _arabic_stemmer if _arabic_stemmer is not False else None


@lru_cache(maxsize=256)
def _query_word_index_cached(filter_key, field, limit):
    """Cached implementation of word-index lookup.

    *filter_key* is a sorted tuple of ``(fieldname, value)`` pairs — the
    hashable equivalent of the ``filter_dict`` argument to
    :func:`_query_word_index`.  Returns a ``tuple`` of unique values (tuples
    are hashable and therefore storable in the LRU cache).
    """
    try:
        from alfanous.data import QSE as _QSE
        engine = _QSE()
        if not engine.OK:
            return ()
        reader = engine._reader.reader
        values = set()
        for _, stored in reader.iter_docs():
            if stored.get("kind") != "word":
                continue
            if all(stored.get(k) == v for k, v in filter_key):
                val = stored.get(field)
                if val is not None:
                    values.add(val)
                    if len(values) >= limit:
                        break
        return tuple(values)
    except Exception:
        return ()


def _query_word_index(filter_dict, field="word", limit=5000):
    """Query the word child documents in the QSE index and return unique values
    of *field* from matching documents.

    Iterates stored documents directly via the index reader so that all field
    types (TEXT, ID, NUMERIC) are compared against their *stored* values
    without relying on Whoosh's query-time term encoding.  This guarantees
    correct results regardless of analyser behaviour.

    Results are cached per ``(filter_dict, field, limit)`` combination for the
    lifetime of the process so that repeated calls with identical arguments
    (e.g. from :class:`TupleQuery` resolving the same root across multiple
    requests) pay the full iter_docs cost only once.

    :param filter_dict: Mapping of ``{fieldname: value}`` to filter word children.
    :param field: The document field whose value to collect (default ``"word"``).
    :param limit: Maximum number of unique values to collect before stopping.
    :returns: Deduplicated list of *field* values from matching word children.
    """
    filter_key = tuple(sorted((k, v) for k, v in filter_dict.items() if v is not None))
    return list(_query_word_index_cached(filter_key, field, limit))


def _build_word_lookup_table(reader):
    """Build lookup tables for the word child documents in one index scan.

    Called once at engine instantiation (``BasicSearchEngine.__init__``) with
    the engine's open ``IndexReader``.  The returned tables are stored as
    ``engine._word_lookup_table`` and freed when the engine is closed.

    Performs a single ``iter_docs()`` pass over all ~77 k word-child documents
    and populates three in-memory dicts:

    * ``form_to_key``: stored word form → ``{'lemma': ..., 'root': ...}``
    * ``lemma_to_forms``: vocalized lemma → frozenset of unvocalized word forms
    * ``root_to_forms``: root string → frozenset of unvocalized word forms

    The tables are used by :func:`_collect_derivations_two_pass` for
    highlighting derivation-level aya-search results.

    :param reader: An open Whoosh ``IndexReader``.
    :returns: Tuple ``(form_to_key, lemma_to_forms, root_to_forms)``
    """
    form_to_key = {}       # word_form → {'lemma': vocalized_lemma, 'root': root}
    _lemma_forms = {}      # vocalized_lemma → set of unvocalized word forms
    _root_forms = {}       # root            → set of unvocalized word forms

    for _, stored in reader.iter_docs():
        if stored.get("kind") != "word":
            continue
        lemma = stored.get("lemma")
        root = stored.get("root")

        # Map every searchable stored form → {lemma, root}
        for sf in _DERIVATION_SEARCH_FIELDS:
            key = stored.get(sf)
            if key and key not in form_to_key:
                form_to_key[key] = {"lemma": lemma, "root": root}

        # Map lemma/root → unvocalized word forms (for derivation highlighting)
        for field in ("standard", "normalized"):
            val = stored.get(field)
            if not val:
                continue
            if lemma:
                _lemma_forms.setdefault(lemma, set()).add(val)
            if root:
                _root_forms.setdefault(root, set()).add(val)

    lemma_to_forms = {k: frozenset(v) for k, v in _lemma_forms.items()}
    root_to_forms  = {k: frozenset(v) for k, v in _root_forms.items()}
    return form_to_key, lemma_to_forms, root_to_forms


def _collect_derivations_two_pass(candidates, index_key, lookup_table=None):
    """Collect unvocalized word forms sharing the same lemma or root as *candidates*.

    Used for **highlighting** after a derivation-level aya search: the matched
    aya_lemma / aya_root field values are expanded back to the actual word
    forms that appear in the aya text so that those words are highlighted.

    Uses the engine-level lookup table (built once at engine init) rather than
    rescanning the index on every request.

    :param candidates: Set/frozenset of candidate word forms (normalized).
    :param index_key: ``'lemma'`` or ``'root'``.
    :param lookup_table: Pre-built ``(form_to_key, lemma_to_forms,
        root_to_forms)`` tuple from ``engine._word_lookup_table``.  When
        ``None`` the function falls back to the current QSE engine's table.
    :returns: List of unique unvocalized word forms.
    """
    if lookup_table is None:
        try:
            from alfanous.data import QSE as _QSE
            _engine = _QSE()
            lookup_table = getattr(_engine, '_word_lookup_table', None)
        except Exception:
            pass
    if not lookup_table:
        return []

    form_to_key, lemma_to_forms, root_to_forms = lookup_table

    # Pass 1: find all index_key values matching any candidate.
    key_values = set()
    for candidate in candidates:
        entry = form_to_key.get(candidate)
        if entry:
            kv = entry.get(index_key)
            if kv:
                key_values.add(kv)

    if not key_values:
        return []

    # Pass 2: collect unvocalized word forms for each key value.
    key_map = lemma_to_forms if index_key == "lemma" else root_to_forms
    words = set()
    for kv in key_values:
        forms = key_map.get(kv)
        if forms:
            words.update(forms)

    return list(words)


class QMultiTerm(MultiTerm):
    """Base class for multi-term queries with Arabic support"""

    def _btexts(self, ixreader):
        fieldname = self.fieldname
        field = ixreader.schema[fieldname]
        to_bytes = field.to_bytes
        seen = set()
        for word in self.words:
            # Obtain the analyzed form(s) of this word for the given field.
            # Without analysis, to_bytes() only does UTF-8 encoding, so a
            # vocalized Arabic word like "عَذَابٌ" (returned by _get_derivations
            # from the word index) would not match the diacritics-stripped term
            # "عذاب" that QStandardAnalyzer stored in the aya field at index
            # time.  process_text() re-runs the same analyzer pipeline so the
            # lookup bytes match the stored bytes.
            if hasattr(field, 'process_text'):
                try:
                    analyzed = list(field.process_text(word, mode='index'))
                except Exception:
                    analyzed = [word]
            else:
                analyzed = [word]
            for text in (analyzed or [word]):
                if text in seen:
                    continue
                seen.add(text)
                try:
                    btext = to_bytes(text)
                except ValueError:
                    continue
                if (fieldname, btext) in ixreader:
                    yield btext

    def __str__(self):
        return f"{self.fieldname}:<{self.text}>"

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f"{self.fieldname!r}, {self.text!r}, boost={self.boost!r})"
        )

    def __hash__(self):
        return hash((self.__class__.__name__, self.fieldname, self.text, self.boost))

    def __eq__(self, other):
        return (
            self.__class__ is other.__class__
            and self.fieldname == other.fieldname
            and self.text == other.text
            and self.boost == other.boost
        )

    def _all_terms(self, termset, phrases=True):
        for word in self.words:
            termset.add((self.fieldname, word))

    def has_terms(self):
        return True

    def terms(self, phrases=False):
        for word in self.words:
            yield (self.fieldname, word)

    def _existing_terms(self, ixreader, termset, reverse=False, phrases=True):
        fieldname, words = self.fieldname, self.words
        fieldnum = ixreader.fieldname_to_num(fieldname)
        for word in words:
            contains = (fieldnum, word) in ixreader
            if reverse:
                contains = not contains
            if contains:
                termset.add((fieldname, word))


class SynonymsQuery(QMultiTerm):
    """Query that searches for synonyms of the given word"""

    # Safety cap: prevents unexpectedly large synonym lists from causing
    # runaway query expansion.
    MAX_WORDS = 100

    def __init__(self, fieldname, text, boost=1.0):
        self.fieldname = fieldname
        self.text = text
        self.boost = boost
        self.words = self._get_synonyms(text)

    @staticmethod
    def _get_synonyms(word):
        """Get synonyms for a word"""
        # syndict values are already lists; slicing creates the required new
        # list without the extra copy that list(...) would introduce.
        return syndict.get(word, [word])[:SynonymsQuery.MAX_WORDS]


class AntonymsQuery(QMultiTerm):
    """Query that searches for antonyms of the given word"""

    # Safety cap: prevents unexpectedly large antonym lists from causing
    # runaway query expansion.
    MAX_WORDS = 100

    def __init__(self, fieldname, text, boost=1.0):
        self.fieldname = fieldname
        self.text = text
        self.boost = boost
        self.words = self._get_antonyms(text)

    @staticmethod
    def _get_antonyms(word):
        """Get antonyms for a word"""
        # antdict values are already lists; slicing creates the required new
        # list without the extra copy that list(...) would introduce.
        return antdict.get(word, [word])[:AntonymsQuery.MAX_WORDS]


class DerivationQuery(QMultiTerm):
    """Query that searches for derivations of the given word"""

    def __init__(self, fieldname, text, level=1, boost=1.0):
        self.fieldname = fieldname
        self.text = text
        self.boost = boost
        self.level = level
        self.words = self._get_derivations(text, level)

    @staticmethod
    def _get_derivations(word, leveldist):
        """Get derivations for a word at a specific level via the word index.

        Level 0 / 1 → lemma-level derivations (narrow set).
        Level >= 2  → root-level derivations (wider set).

        Delegates the index scan to :func:`_collect_derivations_two_pass`,
        which performs exactly two ``iter_docs()`` passes instead of the
        previous approach of calling :func:`_query_word_index` up to 15+
        times (once per candidate × field combination, then 3× per matching
        key value), each doing a full scan of ~75 k documents.

        Returns ``[word]`` when the index is unavailable or no derivations
        are found.
        """
        use_root_level = leveldist >= 2

        word_norm = _ASF_NORMALIZE.normalize_all(word)

        stemmer = _get_arabic_stemmer()
        word_stem = stemmer.stemWord(word_norm) if stemmer is not None else word_norm

        candidates = {word, word_norm, word_stem} - {''}
        index_key = 'root' if use_root_level else 'lemma'

        try:
            words = _collect_derivations_two_pass(candidates, index_key)
            # Strip Uthmanic annotation marks (U+06D6–U+06ED) at this level so
            # that mocked implementations (tests) and the real implementation
            # both produce clean results.
            words = [_UTHMANI_ANNOTATION_RE.sub('', w) for w in words if w]
            return words if words else [word]
        except Exception:
            return [word]


class SpellErrorsQuery(QMultiTerm):
    """Query that ignores spell errors of Arabic letters"""

    # Cap expansion to prevent unbounded memory growth and slow query execution
    # when many index terms normalise to the same form.  100 is generous compared
    # to ArabicWildcardQuery.MAX_EXPAND (20) while still bounding worst-case
    # behaviour on a large Arabic index.
    MAX_MATCHES = 100

    def __init__(self, fieldname, text, boost=1.0):
        self.fieldname = fieldname
        self.text = text
        self.boost = boost
        self.words = [text]
        self.ASF = _ASF_SPELL_ERRORS
        # Pre-compute once; used in every _compare() call instead of recomputing
        # it O(index_terms) times during _btexts() iteration.
        self._text_normalized = self.ASF.normalize_all(text)

    def _btexts(self, ixreader):
        fieldname = self.fieldname
        from_bytes = ixreader.schema[fieldname].from_bytes
        count = 0
        for field, btext in ixreader.all_terms():
            if count >= self.MAX_MATCHES:
                break
            if field == fieldname:
                indexed_text = from_bytes(btext)
                if self._compare(indexed_text):
                    count += 1
                    yield btext

    def _compare(self, second):
        """Normalize and compare against the pre-computed query normalisation."""
        matched = self.ASF.normalize_all(second) == self._text_normalized
        if matched and len(self.words) < self.MAX_MATCHES + 1:
            self.words.append(second)
        return matched


class TashkilQuery(QMultiTerm):
    """Query that searches for different tashkil (diacritics) of words
    
    Note: The current implementation uses simple equality checking. For proper
    tashkil-aware comparison, the _compare method needs to implement normalized
    comparison that ignores or properly handles diacritical marks while matching
    the underlying characters.
    """

    # A single word can have many diacritisation variants; cap at 1000 to
    # prevent full-lexicon scans from accumulating unbounded term sets.
    MAX_MATCHES = 1000

    def __init__(self, fieldname, text, boost=1.0):
        self.fieldname = fieldname
        self.text = text if isinstance(text, list) else [text]
        self.boost = boost
        self.words = [_ASF_TASHKIL.normalize_all(word) for word in self.text]
        # Pre-compute once at construction time: the frozenset of normalized
        # query-word forms used in _btexts for membership testing.  Since
        # self.text never changes, recomputing this on every _btexts call
        # (which Whoosh may invoke multiple times per search) is wasteful.
        # self.words at this point contains exactly the initial normalized
        # forms — before _btexts appends any expanded index terms.
        self._normalized_query_words = frozenset(self.words)

    def __hash__(self):
        return hash((self.__class__.__name__, self.fieldname, tuple(self.text), self.boost))

    def __eq__(self, other):
        return (
            self.__class__ is other.__class__
            and self.fieldname == other.fieldname
            and self.text == other.text
            and self.boost == other.boost
        )

    def _btexts(self, ixreader):
        fieldname = self.fieldname
        from_bytes = ixreader.schema[fieldname].from_bytes
        # Use the frozenset pre-computed at __init__ time instead of
        # recomputing {normalize(w) for w in self.text} on every call.
        normalized_query_words = self._normalized_query_words
        seen_words = set(self.words)
        count = 0
        for field, btext in ixreader.all_terms():
            if count >= self.MAX_MATCHES:
                break
            if field == fieldname:
                indexed_text = from_bytes(btext)
                normalized_indexed = _ASF_TASHKIL.normalize_all(indexed_text)
                if normalized_indexed in normalized_query_words:
                    if indexed_text not in seen_words:
                        self.words.append(indexed_text)
                        seen_words.add(indexed_text)
                    count += 1
                    yield btext


class TupleQuery(QMultiTerm):
    """Query for words matching specific morphological properties"""

    # Map Arabic query type labels to the Arabic "type" field stored in the
    # word-children index (populated via POSclass_arabic in transformer.py).
    # Index values: 'أسماء', 'أفعال', 'أدوات', 'حروف_مقطعة', etc.
    _ARABIC_TO_TYPE = {
        "اسم": "أسماء",
        "فعل": "أفعال",
        "أداة": "أدوات",
        "فواتيح": "حروف_مقطعة",
    }

    def __init__(self, fieldname, items, boost=1.0):
        self.fieldname = fieldname
        self.props = self._properties(items)
        self.text = "(" + ",".join(items) + ")"
        self.boost = boost
        self.words = self._get_words_by_properties(self.props)

    def _properties(self, items):
        """Convert list of properties to a dictionary"""
        D = {}
        if len(items) >= 1:
            D["root"] = items[0]
        if len(items) >= 2:
            D["type"] = items[1]
        if len(items) >= 3:
            D["pattern"] = items[2]
        return D

    @staticmethod
    def _get_words_by_properties(props):
        """Search word children that match specific morphological properties
        via the live word-children index.

        :param props: Dict with optional keys ``root``, ``type``.
        :returns: List of matching standard Arabic word forms.
        """
        # "root" maps directly to the "root" field (stores arabicroot, Arabic script).
        # "type" maps to the "type" field which stores Arabic category values
        # ("أسماء", "أفعال", "أدوات") via _ARABIC_TO_TYPE mapping.
        _filter = {}
        if props.get("root"):
            _filter["root"] = props["root"]
        if props.get("type"):
            arabic_type = TupleQuery._ARABIC_TO_TYPE.get(props["type"])
            if arabic_type:
                _filter["type"] = arabic_type
        if _filter:
            # Merge standard (primary) and normalized so that words whose
            # standard is None (e.g. تملك) are still included.
            words = set(_query_word_index(_filter, field="standard"))
            words.update(_query_word_index(_filter, field="normalized"))
            words.discard(None)
            return list(words)
        return []


class ArabicWildcardQuery(Wildcard):
    """Wildcard query with Arabic question mark support"""

    # Limit wildcard expansion to prevent broad patterns (e.g. bare "*") from
    # iterating over the entire index lexicon before the timelimit collector
    # can stop the query.  20 terms is sufficient for typical prefix-wildcard
    # searches and keeps response times well within the configured timelimit.
    MAX_EXPAND = 20

    def __init__(self, fieldname, text, boost=1.0):
        # Replace Arabic question mark with standard wildcard
        new_text = text.replace("؟", "?")
        # Lowercase so that queries like "God*" match index terms lowercased
        # by LowercaseFilter (e.g. translation fields).  Arabic text has no
        # case concept so .lower() is a no-op for Arabic; wildcard characters
        # (* and ?) are ASCII punctuation and are also unaffected by .lower().
        new_text = new_text.lower()
        super().__init__(fieldname, new_text, boost)
        # Store original text for hash/eq
        self._original_text = text

    def _btexts(self, ixreader):
        """Yield matching byte-encoded terms from the index, capped at MAX_EXPAND.

        Overrides PatternQuery._btexts to prevent broad wildcard patterns from
        expanding to thousands of terms, which would cause the search to exceed
        the configured timelimit before any results are collected.
        """
        count = 0
        for btext in super()._btexts(ixreader):
            if count >= self.MAX_EXPAND:
                break
            yield btext
            count += 1

    def normalize(self):
        """Override Wildcard.normalize() to keep ArabicWildcardQuery intact.

        Whoosh's Wildcard.normalize() converts:
        - bare ``*`` → ``Every(field)``  (completely unbounded)
        - ``prefix*``  → ``Prefix(field, prefix)``  (also unbounded)

        Both conversions bypass the MAX_EXPAND cap in _btexts(), allowing
        translation and word searches to iterate over the entire index lexicon.
        By returning ``self`` for all wildcard-containing patterns the
        MAX_EXPAND guard remains active regardless of the query shape.
        """
        if "*" not in self.text and "?" not in self.text:
            from whoosh.query import Term
            return Term(self.fieldname, self.text, boost=self.boost)
        return self

    def matcher(self, searcher, context=None):
        """Override Wildcard.matcher() to avoid the bare-``*`` → Every shortcut.

        Whoosh's Wildcard.matcher() special-cases ``text == "*"`` and creates
        an Every query whose matcher iterates all documents — bypassing _btexts
        entirely.  Calling MultiTerm.matcher() directly routes through our
        capped _btexts() instead.
        """
        from whoosh.query.terms import MultiTerm
        return MultiTerm.matcher(self, searcher, context)

    def __hash__(self):
        return hash((self.__class__.__name__, self.fieldname, self._original_text, self.boost))

    def __eq__(self, other):
        return (
            self.__class__ is other.__class__
            and self.fieldname == other.fieldname
            and getattr(self, '_original_text', self.text) == getattr(other, '_original_text', other.text)
            and self.boost == other.boost
        )


# Plugin classes

class SynonymsPlugin(TaggingPlugin):
    """Plugin for synonym search (~word)"""

    class SynonymsNode(syntax.WordNode):
        qclass = SynonymsQuery

        def r(self):
            return f"~{self.text!r}"

    expr = r"~(?P<text>\S+)"
    nodetype = SynonymsNode
    priority = 100


class AntonymsPlugin(TaggingPlugin):
    """Plugin for antonym search (#word)"""

    class AntonymsNode(syntax.WordNode):
        qclass = AntonymsQuery

        def r(self):
            return "#%r" % self.text

    expr = r"#(?P<text>\S+)"
    nodetype = AntonymsNode
    priority = 100


class DerivationPlugin(TaggingPlugin):
    """Plugin for derivation search (>word, >>word, or >>>word).

    Derivation levels map to pre-indexed aya fields:

    * ``>word``   (level 1) → stem: search ``aya_stem``  (corpus-derived stem)
    * ``>>word``  (level 2) → lemma: search ``aya_lemma`` (corpus lemma)
    * ``>>>word`` (level 3) → root: search ``aya_root``  (corpus root)

    Each target field uses QStandardAnalyzer, so the query term is normalised
    through that analyzer before the Term query is built — no intermediate
    key-value lookup is needed.  All three fields are always in the schema.
    """

    # Map derivation level → target aya field name (always in schema)
    _LEVEL_FIELDS = {
        1: "aya_stem",    # stem  — QStandardAnalyzer (corpus-derived stem)
        2: "aya_lemma",   # lemma — QStandardAnalyzer
        3: "aya_root",    # root  — QStandardAnalyzer
    }

    class DerivationNode(syntax.WordNode):
        def __init__(self, text, **kwargs):
            super().__init__(text, **kwargs)
            # Count the number of > symbols to determine level
            self.level = len(text) - len(text.lstrip('>'))
            self.actual_text = text.lstrip('>')

        def query(self, parser):
            fieldname = self.fieldname or parser.fieldname
            deriv_field = DerivationPlugin._LEVEL_FIELDS.get(self.level)
            if deriv_field is not None:
                schema = getattr(parser, 'schema', None)
                if schema is not None and deriv_field in schema:
                    # PRIMARY: apply the target field's own analyzer.
                    # For level 1 (aya_stem / QStemAnalyzer) this runs Snowball.
                    # For levels 2/3 (aya_lemma/aya_root / QStandardAnalyzer)
                    # it just strips tashkeel — no intermediate lookup needed.
                    field_obj = schema[deriv_field]
                    seen: "set[str]" = set()
                    terms = []
                    for tok in field_obj.analyzer(self.actual_text, mode="query"):
                        if tok.text not in seen:
                            seen.add(tok.text)
                            terms.append(Term(deriv_field, tok.text))
                    # FALLBACK (level 1 only): normalized-only form (no Snowball),
                    # added when it differs from the Snowball-stemmed primary term.
                    if self.level == 1:
                        norm = _ASF_NORMALIZE.normalize_all(self.actual_text)
                        if norm and norm not in seen:
                            seen.add(norm)
                            terms.append(Term(deriv_field, norm))
                    # Always include the exact-match term on the main field so
                    # that derivation results are a superset of exact results.
                    _main_seen: "set[str]" = set()
                    if fieldname in schema:
                        main_obj = schema[fieldname]
                        for tok in main_obj.analyzer(self.actual_text, mode="query"):
                            if tok.text not in _main_seen:
                                _main_seen.add(tok.text)
                                terms.append(Term(fieldname, tok.text))
                    if len(terms) == 1:
                        return terms[0]
                    if terms:
                        return Or(terms, boost=self.boost)
            # Field not found — return a simple Term on the original field.
            return Term(fieldname, self.actual_text, boost=self.boost)

        def r(self):
            return f"{'>' * self.level}{self.actual_text!r}"

    # Exclude parentheses so that grouping syntax e.g. ``kind:aya AND (>word)``
    # does not swallow the closing ``)`` into the derivation text.
    expr = r"(?P<text>>+[^\s()]+)"
    nodetype = DerivationNode
    priority = 100


class SpellErrorsPlugin(TaggingPlugin):
    """Plugin for spell error tolerant search (%word)"""

    class SpellErrorsNode(syntax.WordNode):
        qclass = SpellErrorsQuery

        def r(self):
            return f"%{self.text!r}"

    expr = r"%(?P<text>\S+)"
    nodetype = SpellErrorsNode
    priority = 100


class TashkilPlugin(TaggingPlugin):
    """Plugin for tashkil (diacritics) search ('word' or 'word1 word2')"""

    class TashkilNode(syntax.TextNode):
        def query(self, parser):
            fieldname = self.fieldname or parser.fieldname
            # Split text and filter out empty tokens
            words = [w for w in self.text.split() if w.strip()]

            # If multiple words, create an Or query with Term subqueries
            # This allows proper search across multiple terms with tashkil
            if len(words) > 1:
                subqueries = [Term(fieldname, word) for word in words]
                return Or(subqueries, boost=self.boost)
            elif len(words) == 1:
                # Single word - use TashkilQuery for tashkil-aware search
                return TashkilQuery(fieldname, words, boost=self.boost)
            else:
                # No words - return empty query
                return NullQuery()

        def r(self):
            return f"'{self.text}'"

    expr = r"'(?P<text>[^']+)'"
    nodetype = TashkilNode
    priority = 100


class TuplePlugin(TaggingPlugin):
    """Plugin for tuple search ({root,type,pattern})"""

    class TupleNode(syntax.TextNode):
        def query(self, parser):
            fieldname = self.fieldname or parser.fieldname
            # Split by comma or Arabic comma
            items = [
                item.strip()
                for item in self.text.replace('،', ',').split(',')
            ]
            return TupleQuery(fieldname, items, boost=self.boost)

        def r(self):
            return f"{{{self.text}}}"

    expr = r"\{(?P<text>[^}]+)\}"
    nodetype = TupleNode
    priority = 100


class ArabicWildcardPlugin(TaggingPlugin):
    """Plugin for Arabic wildcard search with ؟ support"""

    class ArabicWildcardNode(syntax.WordNode):
        def query(self, parser):
            fieldname = self.fieldname or parser.fieldname
            return ArabicWildcardQuery(fieldname, self.text, boost=self.boost)

        def r(self):
            return f"{self.text!r}"

    # Match words containing *, ASCII ?, or Arabic ؟.
    # Exclude parentheses so that grouping syntax e.g. ``kind:aya AND (*word*)``
    # does not swallow the closing ``)`` into the wildcard text.
    expr = r"(?P<text>[^\s()]*[*?؟][^\s()]*)"
    nodetype = ArabicWildcardNode
    priority = 90  # Lower than other plugins to let them match first
