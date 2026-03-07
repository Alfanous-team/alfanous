from whoosh import qparser
from whoosh.qparser import QueryParser

from alfanous.searching import QSearcher, QReader
from alfanous.indexing import QseDocIndex, BasicDocIndex
from alfanous.results_processing import Qhighlight, QTranslationHighlight
from alfanous.query_processing import QuranicParser, StandardParser
from alfanous.constants import QURAN_TOTAL_VERSES

class BasicSearchEngine:
    def __init__(self, qdocindex, query_parser, main_field, otherfields, qsearcher, qreader, qhighlight, default_filter=None):

        self.OK = False
        self._default_filter = default_filter or {}
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

    def search_all(self, querystr, limit=QURAN_TOTAL_VERSES, sortedby="score", reverse=False, facets=None, filter_dict=None, fuzzy=False, fuzzy_maxdist=1, timelimit=5.0):
        """
        Perform a search in the index.
        
        @param querystr: The search query string
        @param limit: Maximum number of results to return
        @param sortedby: Field to sort results by
        @param reverse: Whether to reverse the sort order
        @param facets: Facets to group results by
        @param filter_dict: Filters to apply to the search (merged with any
               default_filter configured on this engine)
        @param fuzzy: When True, also search the normalised/stemmed 'aya' field
               and apply Levenshtein distance matching on 'aya_ac'
        @param fuzzy_maxdist: Maximum Levenshtein edit distance for fuzzy term
               matching (default 1). Only used when fuzzy=True.
        @param timelimit: Maximum number of seconds to spend on the search
               (default 5.0). Pass None to disable the limit.
        @return: Tuple of (results, term_stats, searcher)
        """
        # Merge the engine-level default filter (e.g. kind="aya") with any
        # caller-supplied filter.  Caller values take precedence.
        # Use getattr so tests that bypass __init__ via __new__ still work.
        _default = getattr(self, '_default_filter', None)
        if _default:
            merged = {**_default, **(filter_dict or {})}
        else:
            merged = filter_dict
        results, terms, searcher = self._searcher.search(querystr, limit=limit, sortedby=sortedby, reverse=reverse, facets=facets, filter_dict=merged, fuzzy=fuzzy, fuzzy_maxdist=fuzzy_maxdist, timelimit=timelimit)
        return results, list(self._reader.term_stats(terms)), searcher

    def search_with_query(self, q_obj, limit=QURAN_TOTAL_VERSES, sortedby="score", timelimit=5.0):
        """Run a pre-built Whoosh query object (e.g. NestedParent/NestedChildren).

        Useful when the query cannot be expressed as a plain string, for example
        cross-field nested document queries.  Returns the same
        ``(results, term_stats, searcher)`` tuple as :meth:`search_all`.
        """
        results, terms, searcher = self._searcher.search_obj(q_obj, limit=limit, sortedby=sortedby, timelimit=timelimit)
        return results, [], searcher

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

    def correct_query(self, querystr):
        """
        Return a corrected version of *querystr* using Whoosh's query corrector.

        @param querystr: The raw query string to correct.
        @return: Dictionary with 'original' and 'corrected' keys.
        """
        return self._searcher.correct_query(querystr)

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

    def list_terms(self, fieldname=None):
        """ List all indexed terms for a field (or all fields if fieldname is None). """
        if "_reader" in self.__dict__:
            return self._reader.list_terms(fieldname)
        else:
            return iter([])

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
                             , otherfields=[]
                             , qsearcher=QSearcher
                             , qreader=QReader
                             , qhighlight=Qhighlight
                             , default_filter={"kind": "aya"}
                             )


