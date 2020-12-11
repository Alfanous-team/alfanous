# coding: utf-8


from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import re

from alfanous.Support.whoosh.analysis import StopFilter, RegexTokenizer  # LowercaseFilter, StandardAnalyzer,
from alfanous.Support.PyArabic.araby import strip_tashkeel, strip_tatweel,strip_shadda, normalize_spellerrors, normalize_hamza, normalize_lamalef, normalize_uthmani_symbols  # , HARAKAT_pat,
from alfanous.Support.PyArabic.araby  import FATHATAN, DAMMATAN, KASRATAN, FATHA, DAMMA, KASRA, SUKUN, SHADDA  # *
from alfanous.constants import INVERTEDSHAPING

import six
from six.moves import range


class QSpaceTokenizer( RegexTokenizer ):
    def __init__( self, expression = r"[^ \t\r\n]+" ):
        super( QSpaceTokenizer, self ).__init__( expression = expression )


class QAffixesTokenizer( QSpaceTokenizer ):
    def __init__( self, expression = r"[^ \t\r\n]+" ):
        super( QAffixesTokenizer, self ).__init__( expression = expression )
        raise NotImplemented()

class QStopFilter( StopFilter ):
    """ استبعاد بعض الكلمات  """

    def __init__( self, stoplist = [], minsize = 2, renumber = False ):
        super( QStopFilter, self ).__init__( stoplist = stoplist, minsize = minsize, renumber = renumber )





class QArabicSymbolsFilter():
    """        """
    def __init__( self, shaping = True, tashkil = True, spellerrors = False, hamza = False, shadda= False, uthmani_symbols = False ):
        self._shaping = shaping
        self._tashkil = tashkil
        self._spellerrors = spellerrors
        self._hamza = hamza
        self._uthmani_symbols = uthmani_symbols


    def normalize_all( self, text ):
        if self._shaping:
                text = normalize_lamalef( text )
                text = unicode_.normalize_shaping( text )
                text = strip_tatweel( text )

        if self._tashkil:
                text = strip_tashkeel( text )

        if self._spellerrors:
                text = normalize_spellerrors( text )

        if self._hamza:
                text = normalize_hamza( text )
                
        if self._uthmani_symbols:
                text = normalize_uthmani_symbols( text )

        return text

    def __call__( self, tokens ):
        for t in tokens:
            t.text = self.normalize_all( t.text )
            yield t

def Gword_tamdid( aya ):
    """ add a tamdid to lafdh aljalala to eliminate the double vocalization """
    return aya.replace( "لَّه", "لَّـه" ).replace( "لَّه", "لَّـه" )




def PartialVocalisation():
    """  TODO complete it"""

    def __init__():
        pass

    transitions = {
                 "harf":{
                         "harf":["comp", "i++", "j++"],

                        "haraka":["j++"],

                        "shadda":["j++"]

                        },


                 "haraka":{
                         "harf":["i++"],


                        "haraka":["comp", "i++", "j++"],

                        "shadda":["i++"]
                        },

                 "shadda":{
                         "harf":["exit"],


                        "haraka":["j++"],

                        "shadda":["i++", "j++"]

                        },

                 }




class unicode_( six.text_type):
    """    a subclass of unicode that handle al-tashkil
    @deprecated: its not well organized
     """

    def __eq__( self, other ):
        return self.shakl_compare( self, other )

    @staticmethod
    def normalize_shaping( text ):
        """"""
        output = ""
        for char in text:
            if char in INVERTEDSHAPING:
                output += INVERTEDSHAPING[char]
            else:
                output += char
        return output



    def list_harakat( self ):
            """return the dict of harakat with thier position in word"""
            cptH = 0
            hdic = {}
            for ch in self:
                if six.text_type(ch)in [FATHATAN, DAMMATAN, KASRATAN, FATHA, DAMMA, KASRA, SUKUN]:  # , SHADDA
                    cptH -= 1
                    if cptH in hdic:

                        hdic[cptH].append( ch )
                    else:
                        hdic[cptH] = ch

                cptH += 1
            return hdic

    @staticmethod
    def compare_harakat( list1, list2 ):
        """compare tow list of harakat"""
        indices = [indice for indice in list(list1.keys()) + list(list2.keys())]
        ret = True
        for i in indices:
            if i in list1 and i in list2:
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
            elif i in list1:
                if SHADDA in list1[i]:
                    ret = False
                    break
            elif i in list2:
                if SHADDA in list2[i]:
                    ret = False
                    break
        return ret
    @staticmethod
    def shakl_compare( self, other ):

        first = self.normalize_shaping( self )
        second = self.normalize_shaping( other )
        firstN = strip_tashkeel( first )
        secondN = strip_tashkeel( second )

        if firstN != secondN:
            return False
        else:
            l1 = self.list_harakat()
            l2 = other.list_harakat()
            return self.compare_harakat( l1, l2 )


    def apply_harakat_list( self, lst ):
        new = ""
        for i in range(len( self)):
            new += self[i]
            if i in lst:
                new += unicode_( "".join( lst[i] ) )
        return new

    word_sh_pattern = re.compile( "[^ \t\r\n]+" )

    def tokenize_shakl( self ):
        return self.word_sh_pattern.findall( self )

# analyzers
QStandardAnalyzer = QSpaceTokenizer() | QArabicSymbolsFilter()  # | QStopFilter(stoplist = stopwords_dyn)
APermissibleAnalyzer = QSpaceTokenizer() | QArabicSymbolsFilter( shaping = True, tashkil = True, spellerrors = True, hamza = True )
QDiacAnalyzer = QSpaceTokenizer() | QArabicSymbolsFilter( tashkil = False )
QHighLightAnalyzer =  QSpaceTokenizer() | QArabicSymbolsFilter()
QDiacHighLightAnalyzer =  QSpaceTokenizer() | QArabicSymbolsFilter( tashkil = False)
QUthmaniAnalyzer = QSpaceTokenizer() | QArabicSymbolsFilter( shaping = True, tashkil = True, spellerrors = False, hamza = False, uthmani_symbols = True)
QUthmaniDiacAnalyzer = QSpaceTokenizer() | QArabicSymbolsFilter( tashkil = False, uthmani_symbols = True )



