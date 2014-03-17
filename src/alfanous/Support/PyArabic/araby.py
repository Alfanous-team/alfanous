#!/usr/bin/python
# -*- coding=utf-8 -*-

# ------------
# Description:
# ------------
#
# Arabic codes
#
# (C) Copyright 2010, Taha Zerrouki
# -----------------
#  $Date: 2010/03/01
#  $Author: Taha Zerrouki$
#  $Revision: 0.1 $
#  This program is written under the Gnu Public License.
#
"""
Arabic module

@todo: normalize_spellerrors,normalize_hamza,normalize_shaping
@todo: statistics calculator

"""
import string
import re
from araby_constants import *
from araby_predicates import *


_arabic_range = None
_PUNCTUATION  = string.punctuation + string.whitespace

#####################################
#{ general  letter functions
#####################################
def order( archar ):
    """return Arabic letter order between 1 and 29.
    Alef order is 1, Yeh is 28, Hamza is 29.
    Teh Marbuta has the same ordre with Teh, 3.
    @param archar: arabic unicode char
    @type archar: unicode
    @return: arabic order.
    @rtype: integer;
    """
    if AlphabeticOrder.has_key( archar ):
        return AlphabeticOrder[archar]
    else: return 0

def name( archar ):
    """return Arabic letter name in arabic.
    Alef order is 1, Yeh is 28, Hamza is 29.
    Teh Marbuta has the same ordre with Teh, 3.
    @param archar: arabic unicode char
    @type archar: unicode
    @return: arabic name.
    @rtype: unicode;
    """
    if NAMES.has_key( archar ):
        return NAMES[archar]
    else:
        return u''

def arabicrange():
    """return a list of arabic characteres .
    Return a list of characteres between \u060c to \u0652
    @return: list of arabic characteres.
    @rtype: unicode;
    
    >>> expected = map( lambda char: unichr( char ), range( 0x0600, 0x00653 ) )
    >>> arabicrange() == expected
    True
    >>> arabicrange() == expected
    True
    """
    if _arabic_range: return _arabic_range
    else: return map( unichr, range( 0x0600, 0x00653 ) )

#####################################
#{ word and text functions
#####################################
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

#####################################
#{Strip functions
#####################################
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

def normalizeLigature( text ):
    """Normalize Lam Alef ligatures into two letters (LAM and ALEF), and Tand return a result text.
    Some systems present lamAlef ligature as a single letter, this function convert it into two letters,
    The converted letters into  LAM and ALEF are :
        - LAM_ALEF, LAM_ALEF_HAMZA_ABOVE, LAM_ALEF_HAMZA_BELOW, LAM_ALEF_MADDA_ABOVE

    @param text: arabic text.
    @type text: unicode.
    @return: return a converted text.
    @rtype: unicode.

    >>> normalizeLigature( '' )
    ''
    >>> normalizeLigature( 'abc' )
    'abc'
    >>> normalizeLigature( 'a' + LAM_ALEF + 'b' + LAM_ALEF_MADDA_ABOVE ) == ('a' + LAM + ALEF + 'b' + LAM + ALEF)
    True
    >>> normalizeLigature( 'a' + LAM_ALEF + 'bc' + LAM_ALEF_MADDA_ABOVE ) == ('a' + LAM + ALEF + 'bc' + LAM + ALEF)
    True
    >>> normalizeLigature( ALEF + LAM_ALEF + BEH + TEH + LAM_ALEF_MADDA_ABOVE ) == (ALEF + LAM + ALEF + BEH + TEH + LAM + ALEF)
    True
    """
    s = ''

    for letter in text:
        s += (LAM + ALEF) if letter in LIGUATURES else letter

    return s

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
