from araby_constants import *
from araby_strip_functions import *
from araby_predicates import *
import string

_PUNCTUATION  = string.punctuation + string.whitespace

def _andmap(iterable):
    return reduce( lambda x,y: x and y, iterable )

def _ormap(iterable):
    return reduce( lambda x,y: x or y, iterable )

def isSukun( archar ):
    """Checks for Arabic Sukun Mark.
    @param archar: arabic unicode char
    @type archar: unicode
    
    >>> _ormap( [isSukun( x ) for x in LETTERS] )
    False
    >>> isSukun( SUKUN )
    True
    """
    return archar == SUKUN

def isShadda( archar ):
    """Checks for Arabic Shadda Mark.
    @param archar: arabic unicode char
    @type archar: unicode
    
    >>> _ormap( [isShadda( x ) for x in LETTERS] )
    False
    >>> isShadda( SHADDA )
    True
    """
    return archar == SHADDA

def isTatweel( archar ):
    """Checks for Arabic Tatweel letter modifier.
    @param archar: arabic unicode char
    @type archar: unicode
    
    >>> _ormap( [isTatweel( x ) for x in LETTERS] )
    False
    >>> isTatweel( TATWEEL )
    True
    """
    return archar == TATWEEL

def isTanwin( archar ):
    return archar in TANWIN

def isTashkeel( archar ):
    return archar in TASHKEEL

def isHaraka( archar ):
    return archar in HARAKAT

def isShortharaka( archar ):
    return archar in SHORTHARAKAT

def isLigature( archar ):
    return archar in LIGUATURES

def isHamza( archar ):
    return archar in HAMZAT

def isAlef( archar ):
    return archar in ALEFAT

def isYehlike( archar ):
    return archar in YEHLIKE

def isWawlike( archar ):
    return archar in WAWLIKE

def isTeh( archar ):
    return archar in TEHLIKE

def isSmall( archar ):
    return archar in SMALL

def isWeak( archar ):
    return archar in WEAK

def isMoon( archar ):
    return archar in MOON

def isSun( archar ):
    return archar in SUN

def hasShadda( word ):
    for char in word:
        if char == SHADDA:
            return True
    
    return False
def isVocalized( word ):
    harakat_count = 0
    
    for letter in word:
        if letter in _PUNCTUATION:
            return False
        elif letter in HARAKAT:
            harakat_count += 1

    return harakat_count > 0

def isVocalizedtext( text ):
    harakat_count = 0

    for letter in text:
        if letter in string.punctuation:
            return False
        elif letter in HARAKAT:
            harakat_count += 1

    return harakat_count > 0

def isArabicstring( text):
    """ Checks for an  Arabic Unicode block characters;
    @param text: input text
    @type text: unicode
    @return: True if all charaters are in Arabic block
    @rtype: Boolean
    """
    return not re.search(u"([^\u0600-\u0652%s%s%s\w])"%(LAM_ALEF,LAM_ALEF_HAMZA_ABOVE,LAM_ALEF_MADDA_ABOVE),text)

def isArabicword( word ):
    """ Checks for an valid Arabic  word.
    An Arabic word
    @param word: input word
    @type word: unicode
    @return: True if all charaters are in Arabic block
    @rtype: Boolean
    """
    if len( word ) == 0 : return False;
    elif re.search( u"([^\u0600-\u0652%s%s%s\w])" % ( LAM_ALEF, LAM_ALEF_HAMZA_ABOVE, LAM_ALEF_MADDA_ABOVE ), word ):
        return False;
    elif isHaraka( word[0] ) or word[0] in ( WAW_HAMZA, YEH_HAMZA ):
        return False;
#  if Teh Marbuta or Alef_Maksura not in the end
    elif re.match( u"^(.)*[%s](.)+$" % ALEF_MAKSURA, word ):
        return False;
    elif re.match( u"^(.)*[%s]([^%s%s%s])(.)+$" % ( TEH_MARBUTA, DAMMA, KASRA, FATHA ), word ):
        return False;
    else:
        return True;

def vocalizedlike( word, vocalized ):
    """return True if the given word have the same or the partial vocalisation like the pattern vocalized

    @param word: arabic word, full/partial vocalized.
    @type word: unicode.
    @param vocalized: arabic full vocalized word.
    @type vocalized: unicode.
    @return: True if vocalized.
    @rtype: unicode.

    >>> vocalizedlike('', '')
    True
    >>> vocalizedlike( REH + JEEM + LAM, REH + JEEM + DAMMA + LAM + DAMMATAN )
    True
    >>> vocalizedlike( REH + JEEM + TEH + LAM, REH + JEEM + DAMMA + LAM + DAMMATAN )
    False
    >>> 
    """
    if not isVocalized( vocalized ) or not isVocalized( word ):
        return stripTashkeel( word ) == stripTashkeel( vocalized )

    else:
        for mark in TASHKEEL:
            vocalized = vocalized.replace( mark, mark + '?' )

        pat = re.compile( "^" + vocalized + "$" )

        return pat.match( word )
