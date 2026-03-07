"""
Whoosh 2.7 query parser plugins for Arabic and Quranic search.

This module contains custom plugins that extend Whoosh's query parser
with Arabic-specific features like synonyms, derivations, spell errors,
tashkil (diacritics), and more.
"""

from whoosh.qparser import TaggingPlugin, syntax
from whoosh.query import MultiTerm, Or, Term, Wildcard

from alfanous.data import syndict, antdict
from alfanous.text_processing import QArabicSymbolsFilter


def _query_word_index(filter_dict, field="word", limit=5000):
    """Query the word child documents in the QSE index and return unique values
    of *field* from matching documents.

    Uses the shared ``data.QSE()`` engine so no extra index handle is opened.
    Returns an empty list when the index is unavailable.

    :param filter_dict: Mapping of ``{fieldname: value}`` to filter word children.
    :param field: The document field whose value to collect (default ``"word"``).
    :param limit: Maximum number of matching word children to inspect.
    :returns: Deduplicated list of *field* values from matching word children.
    """
    try:
        from alfanous.data import QSE as _QSE
        from whoosh import query as _wq
        engine = _QSE()
        if not engine.OK:
            return []
        parts = [_wq.Term("kind", "word")]
        for fname, fval in filter_dict.items():
            if fval:
                parts.append(_wq.Term(fname, fval))
        q = _wq.And(parts)
        res, _, searcher = engine.search_with_query(q, limit=limit)
        values = list(set(r.get(field) for r in res if r.get(field)))
        searcher.close()
        return values
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
        Returns ``[word]`` when the index is unavailable.
        """
        use_root_level = leveldist >= 2

        # Find the word in the index to get its lemma / root
        # Use normalized (unvocalized) form for lookup
        try:
            from alfanous.text_processing import QArabicSymbolsFilter as _QASF
            _strip = _QASF(shaping=False, tashkil=True, spellerrors=False, hamza=False).normalize_all
            word_norm = _strip(word)
        except Exception:
            word_norm = word

        # Try index lookup for lemma/root of this word
        _word_docs = _query_word_index({"normalized": word_norm}, field="lemma")
        if not _word_docs:
            # Also try the vocalized form
            _word_docs = _query_word_index({"word": word}, field="lemma")

        lemma = _word_docs[0] if _word_docs else None

        if use_root_level:
            # Get root of the word
            _root_docs = _query_word_index({"normalized": word_norm}, field="root")
            if not _root_docs:
                _root_docs = _query_word_index({"word": word}, field="root")
            root = _root_docs[0] if _root_docs else None
            if root:
                words = _query_word_index({"root": root}, field="normalized")
                if words:
                    return list(set(words))
        else:
            if lemma:
                words = _query_word_index({"lemma": lemma}, field="normalized")
                if words:
                    return list(set(words))

        return [word]


class SpellErrorsQuery(QMultiTerm):
    """Query that ignores spell errors of Arabic letters"""

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

    def _btexts(self, ixreader):
        fieldname = self.fieldname
        from_bytes = ixreader.schema[fieldname].from_bytes
        for field, btext in ixreader.all_terms():
            if field == fieldname:
                indexed_text = from_bytes(btext)
                if self._compare(self.text, indexed_text):
                    yield btext

    def _compare(self, first, second):
        """Normalize and compare"""
        matched = (
            self.ASF.normalize_all(first) == self.ASF.normalize_all(second)
        )
        if matched:
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
        ASF = QArabicSymbolsFilter(shaping=False, tashkil=True, spellerrors=False, hamza=False)
        from_bytes = ixreader.schema[fieldname].from_bytes
        seen_words = set(self.words)
        for field, btext in ixreader.all_terms():
            if field == fieldname:
                indexed_text = from_bytes(btext)
                normalized_indexed = ASF.normalize_all(indexed_text)
                for word in self.text:
                    if ASF.normalize_all(word) == normalized_indexed:
                        if indexed_text not in seen_words:
                            self.words.append(indexed_text)
                            seen_words.add(indexed_text)
                        yield btext
                        break


class TupleQuery(QMultiTerm):
    """Query for words matching specific morphological properties"""

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

        :param props: Dict with optional keys ``root``, ``type``, ``pattern``.
        :returns: List of matching unvocalized word forms.
        """
        _supported_keys = {"root", "type"}
        _filter = {k: v for k, v in props.items() if k in _supported_keys and v}
        if _filter:
            return _query_word_index(_filter, field="normalized")
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
