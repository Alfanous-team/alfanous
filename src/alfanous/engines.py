from whoosh import qparser
from whoosh.qparser import QueryParser

from alfanous.searching import QSearcher, QReader
from alfanous.indexing import QseDocIndex, ExtDocIndex, BasicDocIndex
from alfanous.results_processing import Qhighlight
from alfanous.query_processing import QuranicParser, StandardParser, FuzzyQuranicParser
from alfanous.query_plugins import (
    SynonymsPlugin,
    AntonymsPlugin,
    DerivationPlugin,
    SpellErrorsPlugin,
    TashkilPlugin,
    TuplePlugin,
    ArabicWildcardPlugin
)

class BasicSearchEngine:
    def __init__(self, qdocindex, query_parser, main_field, otherfields, qsearcher, qreader, qhighlight):

        self.OK = False
        if qdocindex.OK:
            self._docindex = qdocindex
            #
            self._schema = self._docindex.get_schema()
            #
            self._parser = query_parser(main_field, self._schema, group=qparser.OrGroup)
            
            # Add all Arabic query plugins
            self._parser.add_plugin(SynonymsPlugin)
            self._parser.add_plugin(AntonymsPlugin)
            self._parser.add_plugin(DerivationPlugin)
            self._parser.add_plugin(SpellErrorsPlugin)
            self._parser.add_plugin(TashkilPlugin)
            self._parser.add_plugin(TuplePlugin)
            self._parser.add_plugin(ArabicWildcardPlugin)
            
            self._searcher = qsearcher(self._docindex, self._parser)
            #
            self._reader = qreader(self._docindex)
            #
            self._highlight = qhighlight
            self.OK = True

    # end  __init__

    def search_all(self, querystr, limit=6236, sortedby="score", reverse=False):
        results, terms, searcher = self._searcher.search(querystr, limit=limit, sortedby=sortedby, reverse=reverse)
        return results, list(self._reader.term_stats(terms)), searcher

    def most_frequent_words(self, nb, fieldname):
        return list([ (x[0], x[1].decode('utf-8')) for x in self._reader.reader.most_frequent_terms(fieldname, nb)])

    def suggest_all(self, querystr):
        return self._searcher.suggest(querystr)

    def autocomplete(self, querystr):
        return { "base": "".join(querystr.split()[:-1]),
                 "completion": self._reader.autocomplete(querystr.split()[-1])
                 }

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
                        qparser=QueryParser):
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
