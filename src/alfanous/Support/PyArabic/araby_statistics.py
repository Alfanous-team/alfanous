# coding: utf-8
'''
Created on 17 avr. 2010

a module to calculate different statistics on coranic text

@author: assem
'''
import re
import araby

__all__ = ['letters', 'diacritics', 'letter_count', 'hamza_count', 'words',
    'gwords', 'sunletters', 'moonletters']

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
    ''' (string) -> int
    Return the number of arabic letters in the given text.

    >>> letters( '' )
    0
    >>> letters( 'abc' )
    0
    >>> letters( araby.BEH )
    1
    >>> letters( araby.ALEF + araby.BEH )
    2
    >>> letters( 'a' + araby.ALEF + 'b' + araby.BEH + 'c' + araby.ALEF )
    3
    >>> letters( TEST_FIXTURES['text'] )
    30
    '''
    return count( lambda char: char in araby.LETTERS, text )


def diacritics( text ):
    ''' (string) -> int
    Return the number of diacritics in the given text.
    diacritics definition: http://www.learnersdictionary.com/definition/diacritic

    >>> diacritics( '' )
    0
    >>> diacritics( 'abc' )
    0
    >>> diacritics( araby.DAMMA )
    1
    >>> diacritics( 'ab' + araby.ALEF + araby.DAMMA + 'a' + araby.FATHA )
    2
    >>> diacritics( TEST_FIXTURES['text'] )
    3
    '''
    return count( lambda char: char in araby.TASHKEEL, text )


def letter_count( text, letter ):
    ''' (string, string) -> int
    Return the number of occurrences of letter in the given text.

    >>> letter_count( '', '' )
    0
    >>> letter_count( 'abc', '' )
    0
    >>> letter_count( '', 'abc' )
    0
    >>> letter_count( araby.ALEF + 'a' + araby.ALEF + 'b' + araby.ALEF,\
        araby.ALEF )
    3
    >>> letter_count( TEST_FIXTURES['text'], TEST_FIXTURES['letter'] )
    5
    '''
    return count( lambda char: char == letter, text )


def hamza_count( text ):
    ''' (string) -> int
    Return the number of hamza occurrences in the given text.
    You could think of hamza as a group of arabic letters.

    >>> hamza_count( '' )
    0
    >>> hamza_count( 'abc' + araby.ALEF + araby.BEH )
    0
    >>> hamza_count( araby.HAMZA )
    1
    >>> hamza_count( araby.HAMZA + 'ab' + araby.ALEF + araby.WAW_HAMZA +\
        araby.YEH_HAMZA )
    3
    >>> hamza_count( TEST_FIXTURES['text'] )
    2
    '''
    return count( lambda char: char in araby.HAMZAT, text )


def words( text ):
    ''' (string) -> int
    Return the number of words in the given text.

    >>> words( '' )
    0
    >>> words( '  \\n\\t\\r' )
    0
    >>> words( araby.ALEF )
    1
    >>> words( 'ab c' + araby.ALEF + 'd' )
    2
    >>> words( "abc de\\n \\t f\\tg   hij" )
    5
    >>> words( TEST_FIXTURES['text'] )
    7
    '''
    return len( text.split() )


def gwords( text ):
    ''' (string) -> int
    Return the number of variants (not occurrences) of gwords in the given text.

    >>> gwords( '' )
    0
    >>> gwords( ' abc ' )
    0
    >>> gwords( TEST_FIXTURES['gwords'][0] + ' ' + TEST_FIXTURES['gwords'][1] )
    2
    >>> gwords( "%s %s %s" % (TEST_FIXTURES['gwords'][0],\
        TEST_FIXTURES['gwords'][1], TEST_FIXTURES['gwords'][1]) )
    2
    >>> gwords( "%s%s %s" % (TEST_FIXTURES['gwords'][0],\
        TEST_FIXTURES['gwords'][1], TEST_FIXTURES['gwords'][1]) )
    1
    >>> gwords( "%s%s %s %s" % (TEST_FIXTURES['gwords'][0],\
        araby.DAMMA, TEST_FIXTURES['gwords'][1], TEST_FIXTURES['gwords'][1]) )
    2
    >>> gwords( "%s%s %s%s %s" % (TEST_FIXTURES['gwords'][0],\
        araby.DAMMA, 'abc', TEST_FIXTURES['gwords'][1], TEST_FIXTURES['gwords'][1]) )
    2
    '''
    """ Search by regular expression then filter the possibilities """
    words_set = set( araby.stripTashkeel( text ).split() )
    return len( words_set & GWORDS_FORMS )


def sunletters( text ):
    ''' (string) -> int
    Return the number of occurrences of sun letters in the given text.

    >>> sunletters( '' )
    0
    >>> sunletters( TEST_FIXTURES['text'] )
    14
    '''
    return count( lambda char: char in araby.SUN, text )


def moonletters( text ):
    ''' (string) -> int
    Return the number of occurrences of moon letters in the given text.

    >>> moonletters( '' )
    0
    >>> moonletters( TEST_FIXTURES['text'] )
    15
    '''
    return count( lambda char: char in araby.MOON, text )


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
