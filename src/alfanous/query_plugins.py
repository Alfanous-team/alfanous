"""
Whoosh 2.7 query parser plugins for Arabic and Quranic search.

This module contains custom plugins that extend Whoosh's query parser
with Arabic-specific features like synonyms, derivations, spell errors,
tashkil (diacritics), and more.
"""

from whoosh.qparser import TaggingPlugin, syntax
from whoosh.query import MultiTerm, Variations, Or, Term, Wildcard, Prefix

from alfanous.data import syndict, derivedict, worddict
from alfanous.text_processing import QArabicSymbolsFilter
from alfanous.misc import locate, find, filter_doubles


class QMultiTerm(MultiTerm):
    """Base class for multi-term queries with Arabic support"""

    def _words(self, ixreader):
        fieldname = self.fieldname
        return [
            word for word in self.words
            if (fieldname, word) in ixreader
        ]

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
        self.words = [text]  # TODO: implement proper antonyms lookup


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
        """Get derivations for a word at a specific level"""
        # Define source level index
        if word in derivedict.get("word_", {}):
            indexsrc = "word_"
        elif word in derivedict.get("lemma", {}):
            indexsrc = "lemma"
        elif word in derivedict.get("root", {}):
            indexsrc = "root"
        else:
            return [word]

        # Define destination level index
        if leveldist == 0:
            indexdist = "word_"
        elif leveldist == 1:
            indexdist = "lemma"
        elif leveldist >= 2:
            indexdist = "root"

        lst = []
        if indexsrc:
            itm = locate(derivedict[indexsrc], derivedict[indexdist], word)
            if itm:
                lst = filter_doubles(
                    find(derivedict[indexdist], derivedict["word_"], itm)
                )
            else:
                lst = [word]

        return lst if lst else [word]


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

    def _words(self, ixreader):
        for field, indexed_text in ixreader.all_terms():
            if field == self.fieldname:
                if self._compare(self.text, indexed_text):
                    yield indexed_text

    def _compare(self, first, second):
        """Normalize and compare"""
        matched = (
            self.ASF.normalize_all(first) == self.ASF.normalize_all(second)
        )
        if matched:
            self.words.append(second)
        return matched


class TashkilQuery(QMultiTerm):
    """Query that searches for different tashkil (diacritics) of words"""

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

    def _words(self, ixreader):
        for field, indexed_text in ixreader.all_terms():
            if field == self.fieldname:
                for word in self.text:
                    if word == indexed_text:  # TODO: tashkil comparing
                        self.words.append(indexed_text)
                        yield indexed_text


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
        """Search words that have specific properties"""
        wset = None
        for propkey in props.keys():
            if worddict.get(propkey):
                partial_wset = set(
                    find(worddict[propkey], worddict["word_"], props[propkey])
                )
                if wset is None:
                    wset = partial_wset
                else:
                    wset &= partial_wset
        return list(wset) if wset else []


class ArabicWildcardQuery(Wildcard):
    """Wildcard query with Arabic question mark support"""

    def __init__(self, fieldname, text, boost=1.0):
        # Replace Arabic question mark with standard wildcard
        new_text = text.replace(u"؟", u"?")
        super(ArabicWildcardQuery, self).__init__(fieldname, new_text, boost)
        # Store original text for hash/eq
        self._original_text = text

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
            fieldname = parser.fieldname
            # Split text and filter out empty tokens
            words = [w for w in self.text.split() if w.strip()]
            return TashkilQuery(fieldname, words, boost=self.boost)

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
