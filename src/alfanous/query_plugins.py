"""
Whoosh 2.7 query parser plugins for Arabic and Quranic search.

This module contains custom plugins that extend Whoosh's query parser
with Arabic-specific features like synonyms, derivations, spell errors,
tashkil (diacritics), and more.
"""

import re

from whoosh.qparser import TaggingPlugin, syntax
from whoosh.query import MultiTerm, Or, Term, Wildcard

from alfanous.data import syndict, antdict
from alfanous.text_processing import QArabicSymbolsFilter

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
_ASF_NORMALIZE = QArabicSymbolsFilter(
    shaping=True, tashkil=True, spellerrors=False, hamza=False
)


def _query_word_index(filter_dict, field="word", limit=5000):
    """Query the word child documents in the QSE index and return unique values
    of *field* from matching documents.

    Iterates stored documents directly via the index reader so that all field
    types (TEXT, ID, NUMERIC) are compared against their *stored* values
    without relying on Whoosh's query-time term encoding.  This guarantees
    correct results regardless of analyser behaviour.

    :param filter_dict: Mapping of ``{fieldname: value}`` to filter word children.
    :param field: The document field whose value to collect (default ``"word"``).
    :param limit: Maximum number of unique values to collect before stopping.
    :returns: Deduplicated list of *field* values from matching word children.
    """
    try:
        from alfanous.data import QSE as _QSE
        engine = _QSE()
        if not engine.OK:
            return []
        reader = engine._reader.reader
        values = set()
        for _, stored in reader.iter_docs():
            if stored.get("kind") != "word":
                continue
            if all(stored.get(k) == v for k, v in filter_dict.items() if v is not None):
                val = stored.get(field)
                if val is not None:
                    values.add(val)
                    if len(values) >= limit:
                        break
        return list(values)
    except Exception:
        return []


class QMultiTerm(MultiTerm):
    """Base class for multi-term queries with Arabic support"""

    def _btexts(self, ixreader):
        fieldname = self.fieldname
        to_bytes = ixreader.schema[fieldname].to_bytes
        for word in self.words:
            try:
                btext = to_bytes(word)
            except ValueError:
                continue
            if (fieldname, btext) in ixreader:
                yield btext

    def __str__(self):
        return u"%s:<%s>" % (self.fieldname, self.text)

    def __repr__(self):
        return "%s(%r, %r, boost=%r)" % (
            self.__class__.__name__,
            self.fieldname,
            self.text,
            self.boost
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

    def __init__(self, fieldname, text, boost=1.0):
        self.fieldname = fieldname
        self.text = text
        self.boost = boost
        self.words = self._get_synonyms(text)

    @staticmethod
    def _get_synonyms(word):
        """Get synonyms for a word"""
        return syndict.get(word, [word])


class AntonymsQuery(QMultiTerm):
    """Query that searches for antonyms of the given word"""

    def __init__(self, fieldname, text, boost=1.0):
        self.fieldname = fieldname
        self.text = text
        self.boost = boost
        self.words = self._get_antonyms(text)

    @staticmethod
    def _get_antonyms(word):
        """Get antonyms for a word"""
        return antdict.get(word, [word])


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

        Lookup strategy: build three candidate forms of the input word
        (original, normalized, stemmed) then match each against the
        ``word``, ``normalized``, ``lemma``, and ``root`` fields of word
        children to collect the target key (lemma or root).  Results are
        returned as the union of ``word_standard`` and ``normalized`` values
        for all word children sharing that key.

        Returns ``[word]`` when the index is unavailable.
        """
        use_root_level = leveldist >= 2

        word_norm = _ASF_NORMALIZE.normalize_all(word)

        try:
            import Stemmer as _Stemmer
            word_stem = _Stemmer.Stemmer('arabic').stemWord(word_norm)
        except Exception:
            word_stem = word_norm

        candidates = {word, word_norm, word_stem} - {''}
        index_key = 'root' if use_root_level else 'lemma'

        # Collect key values by matching every candidate against every field,
        # including word_standard so users can type standard-script forms and
        # find the corpus root via the stored word_standard values.
        key_values = set()
        for val in candidates:
            for sf in ('word', 'normalized', 'lemma', 'root', 'word_standard'):
                key_values.update(_query_word_index({sf: val}, field=index_key))
        key_values.discard(None)
        key_values.discard('')

        if not key_values:
            return [word]

        # Collect result words: merge word_standard (primary) + normalized +
        # word (Uthmanic form).  Including the Uthmanic form lets derivation
        # keywords be used to highlight Uthmanic aya text.  All collected
        # values are stripped of U+06D6–U+06ED Quranic annotation marks so
        # that no Uthmanic-specific symbol leaks into search terms.
        words = set()
        for kv in key_values:
            ws = _query_word_index({index_key: kv}, field='word_standard')
            nm = _query_word_index({index_key: kv}, field='normalized')
            wu = _query_word_index({index_key: kv}, field='word')
            words.update(_UTHMANI_ANNOTATION_RE.sub('', w) for w in ws if w)
            words.update(_UTHMANI_ANNOTATION_RE.sub('', w) for w in nm if w)
            words.update(_UTHMANI_ANNOTATION_RE.sub('', w) for w in wu if w)

        return list(words) if words else [word]


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
        self.ASF = QArabicSymbolsFilter(
            shaping=True,
            tashkil=False,
            spellerrors=True,
            hamza=True
        )
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

    def __init__(self, fieldname, text, boost=1.0):
        self.fieldname = fieldname
        self.text = text if isinstance(text, list) else [text]
        self.boost = boost
        ASF = QArabicSymbolsFilter(
            shaping=False,
            tashkil=True,
            spellerrors=False,
            hamza=False
        )
        self.words = [ASF.normalize_all(word) for word in self.text]

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
        # Pre-compute the normalised form of every query word once instead of
        # recomputing it O(index_terms) times inside the inner loop.
        normalized_query_words = {_ASF_TASHKIL.normalize_all(w) for w in self.text}
        seen_words = set(self.words)
        for field, btext in ixreader.all_terms():
            if field == fieldname:
                indexed_text = from_bytes(btext)
                normalized_indexed = _ASF_TASHKIL.normalize_all(indexed_text)
                if normalized_indexed in normalized_query_words:
                    if indexed_text not in seen_words:
                        self.words.append(indexed_text)
                        seen_words.add(indexed_text)
                    yield btext


class TupleQuery(QMultiTerm):
    """Query for words matching specific morphological properties"""

    # Map Arabic query type labels to the English "type" field stored in the
    # word-children index (populated from corpus first.get("type")).
    # Corpus values: 'Nouns', 'Verbs', 'Particles', 'Nominals', 'Pronouns',
    #                'Adverbs', 'Prepositions', 'Conjunctions', 'Disconnected Letters'
    _ARABIC_TO_TYPE = {
        "اسم": "Nouns",
        "فعل": "Verbs",
        "أداة": "Particles",
        "فواتيح": "Disconnected Letters",
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
        # "type" maps to the "type" field which stores English category values
        # ("Nouns", "Verbs", "Particles") via _ARABIC_TO_TYPE mapping.
        _filter = {}
        if props.get("root"):
            _filter["root"] = props["root"]
        if props.get("type"):
            english_type = TupleQuery._ARABIC_TO_TYPE.get(props["type"])
            if english_type:
                _filter["type"] = english_type
        if _filter:
            # Merge word_standard (primary) and normalized so that words whose
            # word_standard is None (e.g. تملك) are still included.
            words = set(_query_word_index(_filter, field="word_standard"))
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
        new_text = text.replace(u"؟", u"?")
        super(ArabicWildcardQuery, self).__init__(fieldname, new_text, boost)
        # Store original text for hash/eq
        self._original_text = text

    def _btexts(self, ixreader):
        """Yield matching byte-encoded terms from the index, capped at MAX_EXPAND.

        Overrides PatternQuery._btexts to prevent broad wildcard patterns from
        expanding to thousands of terms, which would cause the search to exceed
        the configured timelimit before any results are collected.
        """
        count = 0
        for btext in super(ArabicWildcardQuery, self)._btexts(ixreader):
            if count >= self.MAX_EXPAND:
                break
            yield btext
            count += 1

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
            return "~%r" % self.text

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
    """Plugin for derivation search (>word or >>word)"""

    class DerivationNode(syntax.WordNode):
        def __init__(self, text, **kwargs):
            super(DerivationPlugin.DerivationNode, self).__init__(text, **kwargs)
            # Count the number of > symbols to determine level
            self.level = len(text) - len(text.lstrip('>'))
            self.actual_text = text.lstrip('>')

        def query(self, parser):
            fieldname = parser.fieldname
            return DerivationQuery(
                fieldname,
                self.actual_text,
                level=self.level,
                boost=self.boost
            )

        def r(self):
            return "%s%r" % ('>' * self.level, self.actual_text)

    expr = r"(?P<text>>+\S+)"
    nodetype = DerivationNode
    priority = 100


class SpellErrorsPlugin(TaggingPlugin):
    """Plugin for spell error tolerant search (%word)"""

    class SpellErrorsNode(syntax.WordNode):
        qclass = SpellErrorsQuery

        def r(self):
            return "%%%r" % self.text

    expr = r"%(?P<text>\S+)"
    nodetype = SpellErrorsNode
    priority = 100


class TashkilPlugin(TaggingPlugin):
    """Plugin for tashkil (diacritics) search ('word' or 'word1 word2')"""

    class TashkilNode(syntax.TextNode):
        def query(self, parser):
            from whoosh import query as wquery
            fieldname = parser.fieldname
            # Split text and filter out empty tokens
            words = [w for w in self.text.split() if w.strip()]
            
            # If multiple words, create an Or query with Term subqueries
            # This allows proper search across multiple terms with tashkil
            if len(words) > 1:
                subqueries = [wquery.Term(fieldname, word) for word in words]
                return wquery.Or(subqueries, boost=self.boost)
            elif len(words) == 1:
                # Single word - use TashkilQuery for tashkil-aware search
                return TashkilQuery(fieldname, words, boost=self.boost)
            else:
                # No words - return empty query
                return wquery.NullQuery()

        def r(self):
            return "'%s'" % self.text

    expr = r"'(?P<text>[^']+)'"
    nodetype = TashkilNode
    priority = 100


class TuplePlugin(TaggingPlugin):
    """Plugin for tuple search ({root,type,pattern})"""

    class TupleNode(syntax.TextNode):
        def query(self, parser):
            fieldname = parser.fieldname
            # Split by comma or Arabic comma
            items = [
                item.strip()
                for item in self.text.replace(u'،', ',').split(',')
            ]
            return TupleQuery(fieldname, items, boost=self.boost)

        def r(self):
            return "{%s}" % self.text

    expr = r"\{(?P<text>[^}]+)\}"
    nodetype = TupleNode
    priority = 100


class ArabicWildcardPlugin(TaggingPlugin):
    """Plugin for Arabic wildcard search with ؟ support"""

    class ArabicWildcardNode(syntax.WordNode):
        def query(self, parser):
            fieldname = parser.fieldname
            return ArabicWildcardQuery(fieldname, self.text, boost=self.boost)

        def r(self):
            return "%r" % self.text

    # Match words containing * or ؟
    expr = r"(?P<text>\S*[*؟]\S*)"
    nodetype = ArabicWildcardNode
    priority = 90  # Lower than other plugins to let them match first
