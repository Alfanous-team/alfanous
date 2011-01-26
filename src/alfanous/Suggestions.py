'''
Created on 22 avr. 2010

it contains  suggestions systems 

@author: Assem Chelli
@contact: assem.ch [at] gmail.com
@license: GPL
@organization: Waiting support 



'''

from Support.whoosh.spelling import SpellChecker


class QSuggester(SpellChecker):
    """ the basic system of suggestions """
    def __init__(self, docindex, qparser,fields,spellindexname):
        storage = docindex.get_index().storage
        self._qparser = qparser
        self._reader = docindex.get_reader()
        self.fields=fields
        super(QSuggester, self).__init__(storage, indexname=spellindexname)
        
    
    def _filter_doubles(self,list):
        for i in range(len(list)):
            if list[i] not in list[i + 1:]:
                yield list[i]
   
    def QSuggest(self, querystr):
            suggestion_result = {}
            missing = set()
            query = self._qparser.parse(querystr)
            query.existing_terms(self._reader, missing, reverse=True, phrases=True)
            for fieldname, termtext in missing:
                if fieldname in self.fields:
                    suggestions = self._filter_doubles(self.suggest(termtext))
                else:
                    suggestions = None    
                if suggestions:
                    suggestion_result[termtext] = suggestions
                        
            return suggestion_result
    
    
def QAyaSpellChecker(docindex,qparser):
        """spellchecking the words of aya fields"""
        return QSuggester(docindex, qparser, fields=["aya","uth","aya_","uth_"], spellindexname="AYA_SPELL")


def QSubjectSpellChecker(docindex,qparser):
        """spellchecking the words of aya fields"""
        return QSuggester(docindex, qparser, fields=["subject","chapter","topic","subtopic"], spellindexname="Sub_SPELL")


def concat_suggestions(listofsuggestions):
    """     """
    D={}
    for unit in listofsuggestions:
        for key,values in unit.items():
            if D.has_key(key):
                D[key].extend[list(values)]
            else: D[key]=list(values)
    return D
    