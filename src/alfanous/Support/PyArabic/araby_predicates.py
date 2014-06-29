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
    """Checks for Arabic Tanwin Marks (FATHATAN, DAMMATAN, KASRATAN).
    @param archar: arabic unicode char
    @type archar: unicode
    
    >>> _ormap( [isTanwin( x ) for x in LETTERS] )
    False
    >>> _andmap( [isTanwin(letter) for letter in TANWIN] )
    True
    """
    return archar in TANWIN

def isTashkeel( archar ):
    """Checks for Arabic Tashkeel Marks (FATHA,DAMMA,KASRA, SUKUN, SHADDA, FATHATAN,DAMMATAN, KASRATAn).
    @param archar: arabic unicode char
    @type archar: unicode
    >>> _ormap( [isTashkeel( char ) for char in LETTERS] )
    False
    >>> _andmap( [isTashkeel( char ) for char in TASHKEEL] )
    True
    """
    return archar in TASHKEEL

def isHaraka( archar ):
    """Checks for Arabic Harakat Marks (FATHA,DAMMA,KASRA,SUKUN,TANWIN).
    @param archar: arabic unicode char
    @type archar: unicode
    
    >>> _ormap( [isHaraka(letter) for letter in LETTERS] )
    False
    >>> _andmap( [isHaraka(letter) for letter in HARAKAT] )
    True
    """
    return archar in HARAKAT

def isShortharaka( archar ):
    """Checks for Arabic  short Harakat Marks (FATHA,DAMMA,KASRA,SUKUN).
    @param archar: arabic unicode char
    @type archar: unicode
    
    >>> _ormap( [isShortharaka(letter) for letter in LETTERS] )
    False
    >>> _andmap( [isShortharaka(letter) for letter in SHORTHARAKAT] )
    True
    """
    return archar in SHORTHARAKAT

def isLigature( archar ):
    """Checks for Arabic  Ligatures like LamAlef.
    (LAM_ALEF, LAM_ALEF_HAMZA_ABOVE, LAM_ALEF_HAMZA_BELOW, LAM_ALEF_MADDA_ABOVE)
    @param archar: arabic unicode char
    @type archar: unicode
    
    >>> _ormap([isLigature( char ) for char in LETTERS])
    False
    >>> _andmap([isLigature( char ) for char in LIGUATURES])
    True
    """
    return archar in LIGUATURES

def isHamza( archar ):
    """Checks for Arabic  Hamza forms.
    HAMZAT are (HAMZA, WAW_HAMZA, YEH_HAMZA, HAMZA_ABOVE, HAMZA_BELOW,ALEF_HAMZA_BELOW, ALEF_HAMZA_ABOVE )
    @param archar: arabic unicode char
    @type archar: unicode
    
    >>> _ormap([isHamza( char ) for char in LETTERS if char not in HAMZAT])
    False
    >>> _andmap([isHamza( char ) for char in HAMZAT])
    True
    """
    return archar in HAMZAT

def isAlef( archar ):
    """Checks for Arabic Alef forms.
    ALEFAT=(ALEF, ALEF_MADDA, ALEF_HAMZA_ABOVE, ALEF_HAMZA_BELOW,ALEF_WASLA, ALEF_MAKSURA );
    @param archar: arabic unicode char
    @type archar: unicode
    
    >>> _ormap(isAlef( char ) for char in LETTERS if char not in ALEFAT)
    False
    >>> _andmap(isAlef( char ) for char in ALEFAT)
    True
    """
    return archar in ALEFAT

def isYehlike( archar ):
    """Checks for Arabic Yeh forms.
    Yeh forms : YEH, YEH_HAMZA, SMALL_YEH, ALEF_MAKSURA
    @param archar: arabic unicode char
    @type archar: unicode
    
    >>> _ormap(isYehlike( char ) for char in LETTERS if char not in YEHLIKE)
    False
    >>> _andmap(isYehlike( char ) for char in YEHLIKE)
    True
    """
    return archar in YEHLIKE

def isWawlike( archar ):
    """Checks for Arabic Waw like forms.
    Waw forms : WAW, WAW_HAMZA, SMALL_WAW
    @param archar: arabic unicode char
    @type archar: unicode
    
    >>> _ormap(isWawlike( char ) for char in LETTERS if char not in WAWLIKE)
    False
    >>> _andmap(isWawlike( char ) for char in WAWLIKE)
    True
    """
    return archar in WAWLIKE

def isTeh( archar ):
    """Checks for Arabic Teh forms.
    Teh forms : TEH, TEH_MARBUTA
    @param archar: arabic unicode char
    @type archar: unicode
    
    >>> _ormap(isTeh( char ) for char in LETTERS if char not in TEHLIKE)
    False
    >>> _andmap(isTeh( char ) for char in TEHLIKE)
    True
    """
    return archar in TEHLIKE

def isSmall( archar ):
    """Checks for Arabic Small letters.
    SMALL Letters : SMALL ALEF, SMALL WAW, SMALL YEH
    @param archar: arabic unicode char
    @type archar: unicode
    
    >>> _ormap(isSmall( char ) for char in LETTERS if char not in SMALL)
    False
    >>> _andmap(isSmall( char ) for char in SMALL)
    True
    """
    return archar in SMALL

def isWeak( archar ):
    """Checks for Arabic Weak letters.
    Weak Letters : ALEF, WAW, YEH, ALEF_MAKSURA
    @param archar: arabic unicode char
    @type archar: unicode
    
    >>> _ormap(isWeak( char ) for char in LETTERS if char not in WEAK)
    False
    >>> _andmap(isWeak( char ) for char in WEAK)
    True
    """
    return archar in WEAK

def isMoon( archar ):
    """Checks for Arabic Moon letters.
    Moon Letters :
    @param archar: arabic unicode char
    @type archar: unicode
    
    >>> _ormap(isMoon( char ) for char in LETTERS if char not in MOON)
    False
    >>> _andmap(isMoon( char ) for char in MOON)
    True
    """

    return archar in MOON

def isSun( archar ):
    """Checks for Arabic Sun letters.
    Moon Letters :
    @param archar: arabic unicode char
    @type archar: unicode
    
    >>> _ormap(isSun( char ) for char in LETTERS if char not in SUN)
    False
    >>> _andmap(isSun( char ) for char in SUN)
    True
    """
    return archar in SUN

def hasShadda( word ):
    """Checks if the arabic word  contains shadda.
    @param word: arabic unicode char
    @type word: unicode
    
    >>> hasShadda( '' )
    False
    >>> hasShadda( 'Hello World!' )
    False
    >>> hasShadda( SHADDA + 'Hi' )
    True
    >>> hasShadda( 'Hi' + SHADDA + 'abc' )
    True
    >>> hasShadda( 'Hi' * 1000 + SHADDA )
    True
    """
    for char in word:
        if char == SHADDA:
            return True
    
    return False
def isVocalized( word ):
    """Checks if the arabic word is vocalized.
    the word musn't  have any spaces and pounctuations.
    @param word: arabic unicode char
    @type word: unicode
    
    >>> isVocalized( '' )
    False
    >>> isVocalized('abc')
    False
    >>> isVocalized( FATHA )
    True
    >>> isVocalized( ALEF + FATHATAN + BEH )
    True
    >>> isVocalized( ALEF + BEH + FATHATAN )
    True
    >>> isVocalized( FATHATAN + ALEF + BEH )
    True
    >>> isVocalized( FATHA + ' ' )
    False
    >>> isVocalized( ALEF + ' ' + FATHATAN + BEH )
    False
    >>> isVocalized( ALEF + BEH + ' ' + FATHATAN )
    False
    >>> isVocalized( FATHATAN + ' ' + ALEF + BEH )
    False
    >>> isVocalized( FATHATAN + '!' + ALEF + BEH )
    False
    """
    harakat_count = 0
    
    for letter in word:
        if letter in _PUNCTUATION:
            return False
        elif letter in HARAKAT:
            harakat_count += 1

    return harakat_count > 0

def isVocalizedtext( text ):
    """Checks if the arabic text is vocalized.
    The text can contain many words and spaces
    @param text: arabic unicode char
    @type text: unicode
    
    >>> isVocalizedtext( '' )
    False
    >>> isVocalizedtext('abc')
    False
    >>> isVocalizedtext( FATHA )
    True
    >>> isVocalizedtext( ALEF + FATHATAN + BEH )
    True
    >>> isVocalizedtext( ALEF + BEH + FATHATAN )
    True
    >>> isVocalizedtext( FATHATAN + ALEF + BEH )
    True
    >>> isVocalizedtext( FATHA + ' ' )
    True
    >>> isVocalizedtext( ALEF + ' ' + FATHATAN + BEH )
    True
    >>> isVocalizedtext( ALEF + BEH + ' ' + FATHATAN )
    True
    >>> isVocalizedtext( FATHATAN + ' ' + ALEF + BEH )
    True
    >>> isVocalizedtext( FATHATAN + '!' + ALEF + BEH )
    False
    """
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
