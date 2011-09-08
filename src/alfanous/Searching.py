# coding: utf-8
'''
@author: assem
'''



from Indexing import QseDocIndex
from QueryProcessing import QuranicParser
from ResultsProcessing import QSort, QScore
from Misc import buck2uni




class QReader:
    """ reader of the index """
    def __init__(self, docindex):
        self.reader = docindex.get_index().reader()
        self.schema = docindex.get_schema()
    
    
    def list_values(self, fieldname=None, double=False,conditions=[]):
        """
        a choosen field stored values generator 
        
        @param fieldname: the name of the choosen field
        @param double: Eliminate the doubles or not
        @param conditions: conditions of match
        @type conditions: list of couples  
        @return : stored values
        
        """
        prec = []
        
        
        if fieldname:
            for  D in self.reader.all_stored_fields():
                cond = True
                for cfield,cvalue in conditions:
                    if D[cfield]!=cvalue : cond =False ; break; 
                
                if cond:
                    value = D[fieldname]
                    if value not in prec:
                        prec.append(value)
                        yield value
        else:
            for  D in self.reader.all_stored_fields():
                cond = True
                for cfield,cvalue in conditions:
                    if D[cfield]!=cvalue : cond =False ; break; 
                    
                
                if cond:
                    for value in D.values() :
                        if value not in prec:
                            prec.append(value)
                            yield value

    
    def list_terms(self, fieldname=None, double=False):
        """
        a choosen field indexed terms generator 
        
        @param fieldname: the name of the choosen field
        @return : indexed terms
        
        """
        prec = []
        if fieldname:
            for  field, value in self.reader.all_terms():
                    if field == fieldname:
                        if value not in prec:
                            prec.append(value)
                            yield value
        else:
            for  field, value in self.reader.all_terms():
                if value not in prec:
                        prec.append(value)
                        yield value
                        
    def term_stats(self, terms):
        """ return all statistiques of a term 
         - document frequency
         - matches frequency
         """
        for term in terms:
            lst=list(term)
            lst.extend([self.reader.frequency(*term),self.reader.doc_frequency(*term)])
            yield tuple(lst)
        

#
        

class QSearcher:
    """ search"""
    def __init__(self, docindex, qparser):
        self._searcher = docindex.get_index().searcher
        self._qparser = qparser
        self.searcher = self._searcher(weighting=QScore())        
                
    def search(self, querystr, limit=6236, sortedby="score",reverse=False):
        if ":" not in querystr:
            querystr=unicode(buck2uni(querystr,ignore="'_\"%*?#~[]{}:>+-|")) 
        
        query = self._qparser.parse(querystr)
        results = self.searcher.search(query, limit, QSort(sortedby),reverse)
        terms = set()
        try:query.all_terms(terms)
        except:pass
        
        return results, terms

 
 
 
if __name__ == "__main__": 
    D = QseDocIndex() 
    S = QSearcher(D, QuranicParser(D.get_schema()))
    
    
    R = QReader(D)
    print ",".join([str(val) for val in R.list_terms("sura_name")][:10])
            


    


    
    
