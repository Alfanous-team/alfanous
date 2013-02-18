# coding: utf-8

##     Copyright (C) 2009-2012 Assem Chelli <assem.ch [at] gmail.com>

##     This program is free software: you can redistribute it and/or modify
##     it under the terms of the GNU Affero General Public License as published by
##     the Free Software Foundation, either version 3 of the License, or
##     (at your option) any later version.

##     This program is distributed in the hope that it will be useful,
##     but WITHOUT ANY WARRANTY; without even the implied warranty of
##     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##     GNU Affero General Public License for more details.

##     You should have received a copy of the GNU Affero General Public License
##     along with this program.  If not, see <http://www.gnu.org/licenses/>.

'''
The main module that relay all the modules.

'''
#from alfanous.dynamic_resources.arabicnames_dyn import ara2eng_names
from alfanous.Searching import QSearcher, QReader
from alfanous.Indexing import QseDocIndex, ExtDocIndex, BasicDocIndex
from alfanous.ResultsProcessing import Qhighlight , QPaginate# , QFilter
from alfanous.QueryProcessing import QuranicParser, StandardParser, FuzzyQuranicParser #,  ArabicParser
from alfanous.Suggestions import  QAyaSpellChecker, QSubjectSpellChecker, concat_suggestions, QWordChecker #, QSuggester

class BasicSearchEngine:
    """
    the basic search engine

    """
    def __init__( self, qdocindex, qparser, mainfield, otherfields, qsearcher, qreader, qspellcheckers, qhighlight ):

        self.OK = False
        if qdocindex.OK:
            self._docindex = qdocindex
            #
            self._schema = self._docindex.get_schema()
            #        
            self._parser = qparser( self._schema, mainfield = mainfield, otherfields = otherfields )
            #
            self._searcher = qsearcher( self._docindex, self._parser )
            #
            self._reader = qreader( self._docindex )
            #
            self._spellcheckers = map( lambda X:X( self._docindex, self._parser ), qspellcheckers )
            #
            self._highlight = qhighlight
            self.OK = True

    #end  __init__  


    def search_all( self, querystr, limit = 6236, sortedby = "score", reverse = False ):
        """
        search in the quran

                >>> results,terms=search_all(u"الحمد",limit=10,sortby="mushaf")
                >>> print ",".join([term[1] for term in list(terms)])
                الحمد
                >>> for r in results:
                >>>         print "(" + r["aya_id"] + "," + r["sura_id"] + ") :" + u"<p>" + Qhighlight(r["aya_"], terms) + u"</p>"
                (2,1) :<p><span style="color:red;font-size:100.0%"><b>الْحَمْدُ</b></span> لِلَّهِ رَبِّ الْعَالَمِينَ</p>

        @param querystr: the query
        @type querystr: unicode
        @param limit: the limit of results
        @type limit: int
        @param sortedby: the methode of sorting the results
        @type sortedby: string
        @return: the lists of terms and results

        """
        if querystr.__class__ is not unicode:
            querystr = querystr.decode( "utf-8" )

        results, termes = self._searcher.search( querystr, limit, sortedby, reverse )
        return ( results, list( self._reader.term_stats( termes ) ) )

    def most_frequent_words( self, nb, fieldname ):
        return list( self._reader.reader.most_frequent_terms( fieldname, nb ) )


    def suggest_all( self, querystr ):
        """suggest the missed words

            >>> for key, value in suggest_all(u" عاصمو ").items():
            >>>    print key, ":", ",".join(value)
            عاصمو : عاصم
        """
        if querystr.__class__ is not unicode:
            querystr = querystr.decode( "utf-8" )
        return concat_suggestions( map( lambda X:X.QSuggest( querystr ), self._spellcheckers ) )

    def highlight( self, text, terms, type = "css" ):
        return self._highlight( text, terms, type )


    def find_extended( self, query, defaultfield ):
        """
        a simple search operation on extended document index

        """
        searcher = self._docindex.get_searcher()
        return searcher().find( defaultfield, query )


    def list_values( self, fieldname, double = False, conditions = [] ):
        """ list all stored values of a field  """
        return self._reader.list_values( fieldname, double = double, conditions = conditions, )

    def __call__( self ):
        return self.OK



def QuranicSearchEngine( indexpath = "../../indexes/main/", qparser = QuranicParser ):
    return BasicSearchEngine( qdocindex = QseDocIndex( indexpath )
                            , qparser = qparser#termclass=QuranicParser.FuzzyAll
                            , mainfield = "aya"
                            , otherfields = []
                            , qsearcher = QSearcher
                            , qreader = QReader
                            , qspellcheckers = [QAyaSpellChecker, QSubjectSpellChecker]
                            , qhighlight = Qhighlight
                            )




def FuzzyQuranicSearchEngine( indexpath = "../indexes/main/", qparser = FuzzyQuranicParser ):
    return BasicSearchEngine( qdocindex = QseDocIndex( indexpath )
                            , qparser = qparser#termclass=QuranicParser.FuzzyAll
                            , mainfield = "aya"
                            , otherfields = ["subject", ]
                            , qsearcher = QSearcher
                            , qreader = QReader
                            , qspellcheckers = [QAyaSpellChecker, QSubjectSpellChecker]
                            , qhighlight = Qhighlight
                            )


def TraductionSearchEngine( indexpath = "../indexes/extend/", qparser = StandardParser ):
    """             """
    return BasicSearchEngine( qdocindex = ExtDocIndex( indexpath )
                            , qparser = qparser
                            , mainfield = "text"
                            , otherfields = []
                            , qsearcher = QSearcher
                            , qreader = QReader
                            , qspellcheckers = []
                            , qhighlight = Qhighlight
                            )

def WordSearchEngine( indexpath = "../indexes/word/", qparser = StandardParser ):
    return BasicSearchEngine( qdocindex = BasicDocIndex( indexpath )
                            , qparser = qparser#termclass=QuranicParser.FuzzyAll
                            , mainfield = "normalized"
                            , otherfields = ["word", "spelled"]
                            , qsearcher = QSearcher
                            , qreader = QReader
                            , qspellcheckers = [QWordChecker]
                            , qhighlight = Qhighlight
                            )


