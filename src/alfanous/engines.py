from whoosh import qparser
from whoosh.qparser import QueryParser

from alfanous.searching import QSearcher, QReader
from alfanous.indexing import QseDocIndex, ExtDocIndex, BasicDocIndex
from alfanous.results_processing import Qhighlight
from alfanous.query_processing import QuranicParser, StandardParser, FuzzyQuranicParser

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

    def search_all(self, querystr, limit=6236, sortedby="score", reverse=False, facets=None, filter_dict=None):
        results, terms, searcher = self._searcher.search(querystr, limit=limit, sortedby=sortedby, reverse=reverse, facets=facets, filter_dict=filter_dict)
        return results, list(self._reader.term_stats(terms)), searcher

    def most_frequent_words(self, nb, fieldname):
        return list([ (x[0], x[1].decode('utf-8')) for x in self._reader.reader.most_frequent_terms(fieldname, nb)])

    def suggest_all(self, querystr):
        return self._searcher.suggest(querystr)

    def autocomplete(self, querystr):
        return { "base": "".join(querystr.split()[:-1]),
                 "completion": self._reader.autocomplete(querystr.split()[-1])
                 }

    def autocomplete_phrase(self, querystr, limit=10):
        """
        Autocomplete that accepts phrases and returns actual phrase completions from Quran.
        Returns complete phrases that actually exist in the Quran text.
        
        @param querystr: The input phrase (can contain multiple words)
        @param limit: Maximum number of phrase suggestions to return (default: 10)
        @return: List of actual phrase completions from Quran
        """
        if not querystr or not querystr.strip():
            return []
        
        querystr = querystr.strip()
        words = querystr.split()
        
        # Check if the last word is incomplete (for prefix matching)
        # We consider a word incomplete if it's not followed by a space
        # For multi-word queries, we'll use the complete words for phrase search
        # and the last word for prefix matching
        
        if len(words) == 1:
            # Single word - just do a simple search with wildcard
            search_query = words[0]
        else:
            # Multiple words - build a phrase search with the complete words
            # and use the last word as a prefix
            complete_words = words[:-1]
            last_word = words[-1]
            # Build phrase search for complete words
            search_query = " ".join(complete_words) + " " + last_word
        
        # Search for ayas containing the query (using regular search for flexibility)
        results, terms, searcher = self.search_all(search_query, limit=100, sortedby="score")
        
        # Extract unique phrase completions from the results
        completions = []
        seen = set()
        
        for result in results:
            aya_text = result.get('aya', '')
            if not aya_text:
                continue
            
            # Split aya into words
            aya_words = aya_text.split()
            
            # Find sequences that match our query pattern
            # For each position in the aya, check if it matches our query words
            for i in range(len(aya_words)):
                match_found = False
                
                # Check if this position matches all our complete words
                if len(words) == 1:
                    # Single word query - check if aya word starts with query
                    if aya_words[i].startswith(words[0]):
                        match_found = True
                        start_pos = i
                else:
                    # Multi-word query - check if sequence matches
                    if i + len(words) - 1 < len(aya_words):
                        all_match = True
                        # Check complete words (all but last)
                        for j in range(len(words) - 1):
                            if aya_words[i + j] != words[j]:
                                all_match = False
                                break
                        # Check if last word in aya starts with our last query word
                        if all_match and aya_words[i + len(words) - 1].startswith(words[-1]):
                            match_found = True
                            start_pos = i
                
                if match_found:
                    # Extract completion (get next 3-5 words from match position)
                    end_pos = min(start_pos + len(words) + 3, len(aya_words))
                    completion_words = aya_words[start_pos:end_pos]
                    completion = " ".join(completion_words)
                    
                    # Only add if it's longer than the query and not already seen
                    if completion not in seen and len(completion) > len(querystr):
                        seen.add(completion)
                        completions.append(completion)
                        if len(completions) >= limit:
                            break
            
            if len(completions) >= limit:
                break
        
        return completions[:limit]

    def highlight(self, text, terms, highlight_type="css", strip_vocalization=True):
        return self._highlight(text, terms, highlight_type, strip_vocalization)

    def find_extended(self, query, defaultfield):
        """
        a simple search operation on extended document index

        """
        searcher = self._docindex.get_searcher()()
        return searcher.find(defaultfield, query,limit=6236), searcher

    def list_values(self, fieldname):
        """ list all stored values of a field  """
        if "_reader" in self.__dict__:
            return self._reader.list_values(fieldname )
        else:
            return []

    def __call__(self):
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
def TraductionSearchEngine(indexpath="../indexes/extend/", qparser=QueryParser):
    """             """
    return BasicSearchEngine(qdocindex=ExtDocIndex(indexpath)
                             , query_parser=qparser
                             , main_field="text"
                             , otherfields=[]
                             , qsearcher=QSearcher
                             , qreader=QReader
                             , qhighlight=Qhighlight
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
