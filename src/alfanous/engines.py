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
        Autocomplete that accepts phrases and returns complete phrase suggestions.
        Combines prefix matching and spell correction.
        
        @param querystr: The input phrase (can contain multiple words)
        @param limit: Maximum number of phrase suggestions to return (default: 10)
        @return: List of complete phrase suggestions
        """
        words = querystr.strip().split()
        if not words:
            return []
        
        last_word = words[-1]
        base_phrase = " ".join(words[:-1])
        
        # Collect suggestions from both prefix expansion and spell correction
        suggestions = []
        seen = set()
        
        # 1. Get prefix completions (higher priority)
        prefix_completions = self._reader.autocomplete(last_word)
        for completion in prefix_completions:
            if completion not in seen:
                suggestions.append(completion)
                seen.add(completion)
                if len(suggestions) >= limit:
                    break
        
        # 2. Add spell correction suggestions if we need more
        if len(suggestions) < limit:
            correction_dict = self._searcher.suggest(last_word)
            # Get corrections for the last word (handle case where key might be different)
            corrections = correction_dict.get(last_word, [])
            for correction in corrections:
                if correction not in seen and len(suggestions) < limit:
                    suggestions.append(correction)
                    seen.add(correction)
        
        # Build complete phrases by combining base phrase with suggestions
        if base_phrase:
            complete_phrases = [f"{base_phrase} {suggestion}" for suggestion in suggestions]
        else:
            complete_phrases = suggestions
        
        return complete_phrases

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
