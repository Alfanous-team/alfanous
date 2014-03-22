from araby_constants import *

__all__ = ['stripHarakat','stripTashkeel','strip_tashkeel','stripTatweel','strip_tatweel','strip_shadda']

def stripHarakat( text ):
    """Strip Harakat from arabic word except Shadda.
    The striped marks are :
        - FATHA, DAMMA, KASRA
        - SUKUN
        - FATHATAN, DAMMATAN, KASRATAN, , , .
    @param text: arabic text.
    @type text: unicode.
    @return: return a striped text.
    @rtype: unicode.
    
    >>> stripHarakat( '' )
    ''
    >>> stripHarakat( 'abc' )
    'abc'
    >>> stripHarakat( 'abc' + FATHA )
    u'abc'
    >>> stripHarakat( 'abc' + SHADDA ) == 'abc' + SHADDA
    True
    >>> stripHarakat( ALEF + BEH + TEH ) == ( ALEF + BEH + TEH )
    True
    >>> stripHarakat( FATHA + ALEF + BEH + DAMMA + TEH + KASRATAN ) == ( ALEF + BEH + TEH )
    True
    """
    return  filter( lambda letter: letter not in HARAKAT, text)

def stripTashkeel( text ):
    """Strip vowels from a text, include Shadda.
    The striped marks are :
        - FATHA, DAMMA, KASRA
        - SUKUN
        - SHADDA
        - FATHATAN, DAMMATAN, KASRATAN, , , .
    @param text: arabic text.
    @type text: unicode.
    @return: return a striped text.
    @rtype: unicode.
    
    >>> stripTashkeel( '' )
    ''
    >>> stripTashkeel( 'abc' )
    'abc'
    >>> stripTashkeel( 'abc' + FATHA )
    u'abc'
    >>> stripTashkeel( 'abc' + SHADDA )
    u'abc'
    >>> stripTashkeel( ALEF + BEH + TEH ) == ( ALEF + BEH + TEH )
    True
    >>> stripTashkeel( FATHA + ALEF + SHADDA + BEH + DAMMA + TEH + KASRATAN ) == ( ALEF + BEH + TEH )
    True
    """
    return filter( lambda letter: letter not in TASHKEEL, text )

def stripTatweel( text ):
    """
    Strip tatweel from a text and return a result text.

    @param text: arabic text.
    @type text: unicode.
    @return: return a striped text.
    @rtype: unicode.
    
    >>> stripTatweel( '' )
    ''
    >>> stripTatweel( 'abc' )
    'abc'
    >>> stripTatweel( TATWEEL + 'ab' + TATWEEL + 'c' + TATWEEL )
    u'abc'
    >>> stripTatweel( ALEF + BEH + TEH ) == (ALEF + BEH + TEH)
    True
    >>> stripTatweel( TATWEEL + ALEF + BEH +  TATWEEL + TEH + TATWEEL ) == (ALEF + BEH + TEH)
    True
    """
    return filter( lambda letter: letter != TATWEEL, text )

def strip_tashkeel(w):
    '''
    strip vowel from a word and return a result word
    
    >>> strip_tashkeel( '' )
    ''
    >>> strip_tashkeel( 'abc' )
    'abc'
    >>> strip_tashkeel( 'abc' + FATHA )
    u'abc'
    >>> strip_tashkeel( 'abc' + SHADDA )
    u'abc'
    >>> strip_tashkeel( ALEF + BEH + TEH ) == ( ALEF + BEH + TEH )
    True
    >>> strip_tashkeel( FATHA + ALEF + SHADDA + BEH + DAMMA + TEH + KASRATAN ) == ( ALEF + BEH + TEH )
    True
    '''
    return stripTashkeel(w)

def strip_tatweel(w):
    '''
    strip tatweel from a word and return a result word
    
    >>> strip_tatweel( '' )
    ''
    >>> strip_tatweel( 'abc' )
    'abc'
    >>> strip_tatweel( TATWEEL + 'ab' + TATWEEL + 'c' + TATWEEL )
    u'abc'
    >>> strip_tatweel( ALEF + BEH + TEH ) == (ALEF + BEH + TEH)
    True
    >>> strip_tatweel( TATWEEL + ALEF + BEH +  TATWEEL + TEH + TATWEEL ) == (ALEF + BEH + TEH)
    True
    '''
    return stripTatweel(w)

def strip_shadda(w):
    '''
    strip tatweel from a word and return a result word
    
    >>> strip_shadda('')
    ''
    >>> strip_shadda(SHADDA + ALEF + BEH + SHADDA + TEH + SHADDA) == (ALEF + BEH + TEH)
    True
    '''
    return filter(lambda letter: letter != SHADDA, w)
