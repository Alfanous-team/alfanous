# coding: utf-8
#    Copyright (C) 2009-2010 Assem Chelli <assem.ch@gmail.com>
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

'''
it contains the linguistic analysers of Quran and Arabic...etc.


@author: Assem Chelli
@contact: assem.ch [at] gmail.com
@license: GPL


'''
from dynamic_ressources import synonymes_dyn as sydy
from dynamic_ressources import stopwords_dyn as swdy
from whoosh.analysis import StandardAnalyzer, StopFilter, RegexTokenizer, LowercaseFilter
#from pyarabic.araby  import araby

from Support.ar_ctype import strip_tashkeel, normalize_spellerrors, normalize_hamza, HARAKAT_pat, normalize_lamalef
from Support.arabic_const import  * 

from Constantes import inversed_shaping_table
from Exceptions import NotImplemented
import re

   
class QSpaceTokenizer(RegexTokenizer):
    def __init__(self, expression=r"[^ \t\r\n]+"):
        super(QSpaceTokenizer, self).__init__(expression=expression)
    
    
class QAffixesTokenizer(QSpaceTokenizer):
    def __init__(self, expression=r"[^ \t\r\n]+"):
        super(QAffixesTokenizer, self).__init__(expression=expression)
        raise NotImplemented()  
    
class QStopFilter(StopFilter):
    """ استبعاد بعض الكلمات  """
    
    def __init__(self, stoplist=swdy.stoplist, minsize=2, renumber=False):
        super(QStopFilter, self).__init__(stoplist=stoplist, minsize=minsize, renumber=renumber)
        
#        

        
    
class QArabicSymbolsFilter():
    """        """
    def __init__(self, shaping=True, tashkil=True, spellerrors=False, hamza=False):
        self.__shaping = shaping
        self.__tashkil = tashkil
        self.__spellerrors = spellerrors
        self.__hamza = hamza
        pass
    
    def normalize_all(self, text):
        if self.__shaping:
                text = normalize_lamalef(text) 
                text = unicode_.normalize_shaping(text) 
            
        if self.__tashkil:
                text = strip_tashkeel(text)
                
        if self.__spellerrors:
                text = normalize_spellerrors(text)
            
        if self.__hamza:
                text = normalize_hamza(text)
        return text
    
    def __call__(self, tokens):
        for t in tokens:
            t.text = self.normalize_all(t.text)
            yield t     
            
def Gword_tamdid(aya):
    """ add a tamdid to lafdh aljalala to eliminate the double vocalization """
    return aya.replace(u"لَّه", u"لَّـه").replace(u"لَّه", u"لَّـه")

            
 
   
def PartialVocalisation():
    """  """   
    
    def __init__():
        pass

    transitions={
                 "harf":{
                         "harf":["comp","i++","j++"],
                 
                        "haraka":["j++"],
    
                        "shadda":["j++"]
                        
                        },
                 
                 
                 "haraka":{
                         "harf":["i++"],
                 
                 
                        "haraka":["comp","i++","j++"],
    
                        "shadda":["i++"]
                        },
    
                 "shadda":{
                         "harf":["exit"],
                 
                 
                        "haraka":["j++"],
    
                        "shadda":["i++","j++"]
    
                        },

                 }
    
    
   
    
class unicode_(unicode):
    """    a subclass of unicode that handle al-tashkil   
    @deprecated: its not well organized
     """
    
    def __eq__(self, other):
        return self.shakl_compare(self, other)
    
    @staticmethod
    def normalize_shaping(text):
        """"""
        str = ""
        for ch in text:
            if inversed_shaping_table.has_key(ch):
                str += inversed_shaping_table[ch]
            else:
                str += ch
        return str

    
    
    def list_harakat(self):
            """return the dict of harakat with thier position in word"""
            cptH = 0
            hdic = {}
            for ch in self:
                if unicode(ch) in [FATHATAN, DAMMATAN, KASRATAN, FATHA, DAMMA, KASRA, SUKUN]:#, SHADDA
                    cptH -= 1
                    if hdic.has_key(cptH):
        
                        hdic[cptH].append(ch)
                    else:
                        hdic[cptH] = ch    
    
                cptH += 1
            return hdic
        
    @staticmethod
    def compare_harakat(list1, list2):
        """compare tow list of harakat"""
        indices = [indice for indice in list1.keys() + list2.keys()]
        ret = True
        for i in indices:
            if list1.has_key(i) and list2.has_key(i):
                for haraka in list1[i]:
                    if haraka in list2[i]:
                        pass
                    elif haraka == SHADDA:
                        ret = False
                        break
                    else:
                        for haraka2 in list2[i]:
                            if haraka2 == SHADDA:
                                ret = False
                            else:
                                ret = False
                            break
            elif list1.has_key(i):
                if SHADDA in list1[i]:
                    ret = False
                    break
            elif list2.has_key(i):
                if SHADDA in list2[i]:
                    ret = False
                    break
        return ret    
    @staticmethod
    def shakl_compare(self, other):

        first = self.normalize_shaping(self)
        second = self.normalize_shaping(other)
        firstN = strip_tashkeel(first)
        secondN = strip_tashkeel(second)
        
        if firstN != secondN:
            return False
        else:
            l1 = self.list_harakat()
            l2 = other.list_harakat()
            return self.compare_harakat(l1, l2) 
       
       
    def apply_harakat_list(self, lst):
        new = u""
        for i in range(len(self)):
            new += self[i]
            if lst.has_key(i):
                new += unicode_("".join(lst[i]))
        return new
    
    word_sh_pattern = re.compile(u"[^ \t\r\n]+")
    
    def tokenize_shakl(self):
        return self.word_sh_pattern.findall(self)
    
#analyzers    
QStandardAnalyzer = QSpaceTokenizer() | QArabicSymbolsFilter() #| QStopFilter() 
QDiacAnalyzer = QSpaceTokenizer() | QArabicSymbolsFilter(tashkil=False)
QHighLightAnalyzer = QSpaceTokenizer() | QArabicSymbolsFilter()
QUthmaniAnalyzer = QSpaceTokenizer() | QArabicSymbolsFilter()
QUthmaniDiacAnalyzer = QSpaceTokenizer() | QArabicSymbolsFilter(tashkil=False)



if __name__ == "__main__":  
    ASF = QArabicSymbolsFilter()
    text = u"عاصِمٌ"
    text = ASF.normalize_all(text)     
    print text
    
    word1 = unicode_("عَاصِمُ")
    word2 = unicode_("عَاصمُ")
    l1 = word1.list_harakat()
    l2 = word2.list_harakat()
    word3 = unicode_("فاعل")
    phrase = unicode_("كانَ ذئبا")
    print word3.apply_harakat_list(l1)
    print l1, "\n", l2, "\n", unicode_.compare_harakat(l1, l2)   
    print word1.shakl_compare(word1, word2)
    for i in phrase.tokenize_shakl():
        print i,
    t = unicode_(u"عاصم")
    u = unicode_(u"عاصِم")
    
    print t == u
 
