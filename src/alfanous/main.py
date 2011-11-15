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
@author: assem
@contact: assem.ch [at] gmail.com
@license: AGPL


@todo: use optparse to organise this script as a console command
@todo: Upgrading to last whoosh 
@todo: Dynamic fields
@todo: Quranic Corpus integration

'''

from dynamic_ressources.arabicnames_dyn import ara2eng_names
from Searching import QSearcher, QReader
from Indexing import QseDocIndex, ExtDocIndex

from ResultsProcessing import Qhighlight, QPaginate, QFilter
from QueryProcessing import QuranicParser,StandardParser,ArabicParser,FuzzyQuranicParser
from Suggestions import QSuggester,QAyaSpellChecker,QSubjectSpellChecker,concat_suggestions




class BasicSearchEngine:
    """
    the basic search engine

    """
    def __init__(self,qdocindex,qparser,mainfield,otherfields,qsearcher,qreader,qspellcheckers,qhighlight):
       
        self.OK=False
        if qdocindex.OK: 
            self._docindex = qdocindex 
            #
            self._schema = self._docindex.get_schema()
            #        
            self._parser = qparser(self._schema,mainfield=mainfield,otherfields=otherfields)
            #
            self._searcher = qsearcher(self._docindex, self._parser)
            #
            self._reader = qreader(self._docindex)
            #
            self._spellcheckers = map(lambda X:X(self._docindex,self._parser),qspellcheckers)
            #
            self._highlight = qhighlight
            self.OK=True
        
    #end  __init__  

    
    def search_all(self, querystr,limit=6236, sortedby="score",reverse=False):
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
            querystr=querystr.decode("utf-8")   

        results, termes = self._searcher.search(querystr, limit, sortedby,reverse)
        return (results, list(self._reader.term_stats(termes)))
        
    def most_frequent_words(self, nb, fieldname):
        return list(self._reader.reader.most_frequent_terms(fieldname, nb)) 
    
    
    def suggest_all(self, querystr):
        """suggest the missed words
     
            >>> for key, value in suggest_all(u" عاصمو ").items():
            >>>    print key, ":", ",".join(value)
            عاصمو : عاصم
        """
        if querystr.__class__ is not unicode:
            querystr=querystr.decode("utf-8")
        return concat_suggestions(map(lambda X:X.QSuggest(querystr),self._spellcheckers))

    def highlight(self, text, terms,type="css"):  
        return self._highlight(text, terms,type)
    
    
    def find_extended(self, query, defaultfield):
        """ 
        a simple search operation on extended document index

        """
        searcher = self._docindex.get_searcher()
        return searcher().find(defaultfield, query)
    
    
    def list_values(self, fieldname,double=False,conditions=[]):
        """ list all stored values of a field  """
        return self._reader.list_values(fieldname,double=double,conditions=conditions,)
    
    def __call__(self):
        return self.OK
    


def QuranicSearchEngine(indexpath="../indexes/main/",qparser=QuranicParser):
    return BasicSearchEngine(qdocindex=QseDocIndex(indexpath)
                            ,qparser=qparser#termclass=QuranicParser.FuzzyAll
                            ,mainfield="aya"
                            ,otherfields=[]
                            ,qsearcher=QSearcher
                            ,qreader=QReader
                            ,qspellcheckers=[QAyaSpellChecker,QSubjectSpellChecker]
                            ,qhighlight=Qhighlight  
                            )
    
def FuzzyQuranicSearchEngine(indexpath="../indexes/main/",qparser=FuzzyQuranicParser):
    return BasicSearchEngine(qdocindex=QseDocIndex(indexpath)
                            ,qparser=qparser#termclass=QuranicParser.FuzzyAll
                            ,mainfield="aya"
                            ,otherfields=["subject",]
                            ,qsearcher=QSearcher
                            ,qreader=QReader
                            ,qspellcheckers=[QAyaSpellChecker,QSubjectSpellChecker]
                            ,qhighlight=Qhighlight  
                            )
   
    
def TraductionSearchEngine(indexpath="../indexes/extend/",qparser=StandardParser):
    """             """
    return BasicSearchEngine(qdocindex=ExtDocIndex(indexpath )
                            ,qparser=qparser
                            ,mainfield="text"
                            ,otherfields=[]
                            ,qsearcher=QSearcher
                            ,qreader=QReader
                            ,qspellcheckers=[]
                            ,qhighlight=Qhighlight  
                            )
        
    

if __name__ == '__main__':
    QSE = QuranicSearchEngine("../indexes/main/") 
    FQSE = FuzzyQuranicSearchEngine("../indexes/main/") 
    TSE = TraductionSearchEngine("../indexes/extend/")
    
    if QSE.OK:
        print "\n#most frequent words#"
        
        mfw = QSE.most_frequent_words(9999999, "aya")
        print len(mfw)
        for term in mfw[0:8]:
            print "\t", term[1], " - frequence = ", term[0], "."

        print "\n#list field stored values#"
        print ",".join([str(item) for item in QSE.list_values("gid")])

    
           
    if TSE.OK:
        print "\n#extended search#"
        results = TSE.find_extended(u"gid:1 OR gid:2", defaultfield="gid")
        print "\n".join([str(result) for result in results])
        
        print "\n#list all translations id#"
        print ",".join(TSE.list_values("id"))
    


    string1 = "  الجنة"
    # %المأصدة
    # لله
    # ال*لك
    # رب     
    # "رسول * الله"  
    # الصلاة وليس الزكاة
    # #السعير  
    # ~السعير
    # نعمت
    #رقم_السورة:[1 الى 5] و الله 
    #آية_:'مَن '
    # {ملك,فعل}
    # >>سماكم
    #>سماكم
    #سماكم
    #سجدة:نعم
    #fawoqa
    #\" رب العالمين\"
    #جزء:8
    
    if QSE.OK:
        print "#suggestions#"
        for key, value in QSE.suggest_all(string1).items():
            print key, ":", ",".join(value)
        print "\n#search#"   
        res, terms = FQSE.search_all(string1, limit=6236, sortedby="score",reverse=True)
        

        #for key,freq in res.key_terms("aya", docs=1, numterms=15000): print key,"(",freq,"),",

        
        '''
        string2 = u"عاصم"
        res2,terms2  = QSE.search_all(string2, sortedby="mushaf")
        res=QFilter(res1,res2)

        terms=terms1|terms2
        '''

        
        print "\n#of#"
        for term in terms:
            print "%s  (%d in %d)," %  term[1:],
            
        values = [term[1] for term in list(terms)]
        print "\n#is#"
        #print res.key_terms("aya")
        html = u"Results(time=%f,number=%d):\n" % (res.runtime, len(res)) 
        for num, respage in QPaginate(res, 5):
            html += "~~~~~page " + str(num) + "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n"
            for r in respage:
                html += "(" + str(r["aya_id"]) + "," + str(r["sura_id"]) + ") :" + u"<p>" + QSE.highlight(r["aya_"], values,"html") + u"</p>\n"
            print html
            html = ""
            raw_input("press any key...")
    
        
    
       
        
    
