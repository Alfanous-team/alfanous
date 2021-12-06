
import re

__all__ = ['letters', 'diacritics', 'letter_count', 'hamza_count', 'words',
    'gwords', 'sunletters', 'moonletters']

from alfanous.Support.pyarabic.constants import LETTERS, TASHKEEL, HAMZAT

gword_pattern = re.compile( u"لله" )
GWORDS_FORMS = set( [u"أبالله", u"وتالله", u"بالله", u"تالله", u"والله", u"الله",
    u"ولله", u"اللهم", u"آلله", u"فلله", u"لله", u"فالله", ] )

'''
A sample data to be used in docstring tests. Since this variables isn't
declared in __all__, it is private to this module.
'''
TEST_FIXTURES = {'text': u" اللّهم يضلله يً ْيسئء سبي شبيشيش شسيشسي",
    'letter': u"ش", 'gwords': [u"أبالله", u"وتالله", u"بالله"]}


def count( f, iterable ):
    ''' ((object) -> boolean, iterable) -> int
    Return the count of elements in the given iterable that return True for
    the function f.
    '''
    return sum( 1 for x in iterable if f(x) )


def letters( text ):
    return count( lambda char: char in LETTERS, text )


def diacritics( text ):
    return count( lambda char: char in TASHKEEL, text )


def letter_count( text, letter ):
    return count( lambda char: char == letter, text )


def hamza_count( text ):

    return count( lambda char: char in HAMZAT, text )


def words( text ):
    return len( text.split() )


def gwords( text ):

    """ Search by regular expression then filter the possibilities """
    words_set = set( stripTashkeel( text ).split() )
    return len( words_set & GWORDS_FORMS )


def sunletters( text ):
    return count( lambda char: char in SUN, text )


def moonletters( text ):
    return count( lambda char: char in MOON, text )


if __name__ == "__main__":
    str = u" اللّهم يضلله يً ْيسئء سبي شبيشيش شسيشسي"
    print( "letters=", letters( str ) )
    print( "diacritics=", diacritics( str ) )
    print( "letter_count=", letter_count( str, u"ش" ) )
    print( "hamza_count=", hamza_count( str ) )
    print( "words=", words( str ) )
    print( "gwords=", gwords( str ) )
    print( "sunletters=", sunletters( str ) )
    print( "moonletters=", moonletters( str ) )
