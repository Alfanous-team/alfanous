from whoosh import qparser
from whoosh.qparser import QueryParser

from alfanous.searching import QSearcher, QReader
from alfanous.indexing import QseDocIndex, ExtDocIndex, BasicDocIndex
from alfanous.results_processing import Qhighlight, QTranslationHighlight
from alfanous.query_processing import QuranicParser, StandardParser, FuzzyQuranicParser
from alfanous.constants import QURAN_TOTAL_VERSES

class BasicSearchEngine:
    def __init__(self, qdocindex, query_parser, main_field, otherfields, qsearcher, qreader, qhighlight):

        self.OK = False
        if qdocindex.OK:
            self._docindex = qdocindex
            #
            self._schema = self._docindex.get_schema()
            #
            # Try to instantiate parser with otherfields (for custom parsers like QuranicParser)
            # Fall back to standard Whoosh QueryParser signature if that fails
            try:
                self._parser = query_parser(schema=self._schema, mainfield=main_field, otherfields=otherfields)
            except TypeError:
                self._parser = query_parser(main_field, self._schema, group=qparser.OrGroup)
            
            # Note: Plugins are added in the parser's own __init__ method
            # (see ArabicParser and its subclasses in query_processing.py)
            
            self._searcher = qsearcher(self._docindex, self._parser)
            #
            self._reader = qreader(self._docindex)
            #
            self._highlight = qhighlight
            self.OK = True

    # end  __init__

    def search_all(self, querystr, limit=QURAN_TOTAL_VERSES, sortedby="score", reverse=False, facets=None, filter_dict=None, fuzzy=False, fuzzy_maxdist=1):
        """
        Perform a search in the index.
        
        @param querystr: The search query string
        @param limit: Maximum number of results to return
        @param sortedby: Field to sort results by
        @param reverse: Whether to reverse the sort order
        @param facets: Facets to group results by
        @param filter_dict: Filters to apply to the search
        @param fuzzy: When True, also search the normalised/stemmed 'aya' field
               and apply Levenshtein distance matching on 'aya_ac'
        @param fuzzy_maxdist: Maximum Levenshtein edit distance for fuzzy term
               matching (default 1). Only used when fuzzy=True.
        @return: Tuple of (results, term_stats, searcher)
        """
        results, terms, searcher = self._searcher.search(querystr, limit=limit, sortedby=sortedby, reverse=reverse, facets=facets, filter_dict=filter_dict, fuzzy=fuzzy, fuzzy_maxdist=fuzzy_maxdist)
        return results, list(self._reader.term_stats(terms)), searcher

    def most_frequent_words(self, nb, fieldname):
        """
        Get the most frequent words in a field.
        
        @param nb: Number of words to return
        @param fieldname: Field to search in
        @return: List of (frequency, word) tuples
        """
        return list([ (x[0], x[1].decode('utf-8')) for x in self._reader.reader.most_frequent_terms(fieldname, nb)])

    def suggest_all(self, querystr):
        """
        Get search suggestions for a query.
        
        @param querystr: The query string to get suggestions for
        @return: List of suggested queries
        """
        return self._searcher.suggest(querystr)

    def autocomplete(self, querystr):
        """
        Get autocomplete suggestions for the last word in a query.
        
        @param querystr: The query string to autocomplete
        @return: Dict with 'base' (all but last word) and 'completion' (suggestions for last word)
        """
        return { "base": "".join(querystr.split()[:-1]),
                 "completion": self._reader.autocomplete(querystr.split()[-1])
                 }

    def highlight(self, text, terms, highlight_type="css", strip_vocalization=True):
        """
        Highlight search terms in text.
        
        @param text: The text to highlight
        @param terms: The terms to highlight
        @param highlight_type: Type of highlighting ('css', 'bold', etc.)
        @param strip_vocalization: Whether to strip vocalization marks
        @return: Highlighted text
        """
        return self._highlight(text, terms, highlight_type, strip_vocalization)

    def find_extended(self, query, defaultfield):
        """
        a simple search operation on extended document index

        """
        searcher = self._docindex.get_searcher()()
        return searcher.find(defaultfield, query,limit=QURAN_TOTAL_VERSES), searcher

    def list_values(self, fieldname):
        """ list all stored values of a field  """
        if "_reader" in self.__dict__:
            return self._reader.list_values(fieldname )
        else:
            return []

    def list_stored_values(self, fieldname):
        """ List all unique stored (non-tokenized) values of a field, preserving full phrases. """
        if "_reader" in self.__dict__:
            return self._reader.list_stored_values(fieldname)
        else:
            return []

    def __call__(self):
        """
        Check if the search engine is properly initialized.
        
        @return: True if OK, False otherwise
        """
        return self.OK


def QuranicSearchEngine(indexpath="../indexes/main/",
                        qparser=QuranicParser):
    return BasicSearchEngine(qdocindex=QseDocIndex(indexpath)
                             , query_parser=qparser
                             , main_field="aya"
                             , otherfields=["subject", ]
                             , qsearcher=QSearcher
                             , qreader=QReader
                             , qhighlight=Qhighlight
                             )

# TODO merge into main
def TraductionSearchEngine(indexpath="../indexes/extend/", qparser=None, lang=None):
    """
    Build a search engine for Quran translations.

    By default the engine searches across **all** ``text*`` fields present in
    the index (``text``, ``text_en``, ``text_fr``, ``text_ar``, …) using a
    :func:`~whoosh.qparser.MultifieldParser`.  This ensures that every
    language-specific stemmed field contributes to recall.

    When *lang* is supplied (ISO 639-1 code, e.g. ``'en'``, ``'fr'``), the
    ``text_<lang>`` field receives a 2× relevance boost while still searching
    all other ``text*`` fields.

    *qparser* can be used to override the default ``MultifieldParser``-based
    factory when a custom single-field parser is required (e.g. during testing).
    """
    from whoosh.qparser import MultifieldParser as _MultifieldParser
    from whoosh import qparser as _qparser

    docindex = ExtDocIndex(indexpath)

    # Collect all text* field names from the live index schema.
    # Fall back to ["text"] when the index is unavailable.
    text_fields = ["text"]
    if docindex.OK:
        schema_names = docindex.get_schema().names()
        all_text_fields = sorted(
            f for f in schema_names if f == "text" or f.startswith("text_")
        )
        if all_text_fields:
            text_fields = all_text_fields

    # Optional per-language relevance boost
    fieldboosts = None
    if lang:
        lang_field = f"text_{lang}"
        if lang_field in text_fields:
            fieldboosts = {lang_field: 2.0}

    def _parser_factory(schema, mainfield, otherfields):
        # mainfield/otherfields are passed by BasicSearchEngine but intentionally
        # ignored here: MultifieldParser already covers all text* fields via the
        # captured text_fields list, so the outer "mainfield" concept is redundant.
        return _MultifieldParser(
            text_fields, schema, fieldboosts=fieldboosts, group=_qparser.OrGroup
        )

    effective_parser = qparser if qparser is not None else _parser_factory

    # text_fields[0] ("text") is passed as main_field only to satisfy
    # BasicSearchEngine's interface; the actual search scope is determined by
    # _parser_factory using all text* fields via MultifieldParser.
    return BasicSearchEngine(qdocindex=docindex
                             , query_parser=effective_parser
                             , main_field=text_fields[0]
                             , otherfields=[]
                             , qsearcher=QSearcher
                             , qreader=QReader
                             , qhighlight=QTranslationHighlight
                             )


def WordSearchEngine(indexpath="../indexes/word/", qparser=StandardParser):
    return BasicSearchEngine(qdocindex=BasicDocIndex(indexpath)
                             , query_parser=qparser  # termclass=QuranicParser.FuzzyAll
                             , main_field="normalized"
                             , otherfields=["word", "spelled"]
                             , qsearcher=QSearcher
                             , qreader=QReader
                             , qhighlight=Qhighlight
                             )
