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
import re
from araby_constants import *
from araby_predicates import *


_arabic_range = None

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
    else: return map( lambda char: unichr( char ), range( 0x0600, 0x00653 ) )

#####################################
#{ word and text functions
#####################################
def isVocalized( word ):
    """Checks if the arabic word is vocalized.
    the word musn't  have any spaces and pounctuations.
    @param word: arabic unicode char
    @type word: unicode
    """
    return not word.isalpha() and re.search( HARAKAT_pattern, word )

def isVocalizedtext( text ):
    """Checks if the arabic text is vocalized.
    The text can contain many words and spaces
    @param text: arabic unicode char
    @type text: unicode
    """
    return re.search( HARAKAT_pattern, text )

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
    Example:
    	#>>> text=u"الْعَرَبِيّةُ"
    	#>>> stripTashkeel(text)
    	العربيّة

    @param text: arabic text.
    @type text: unicode.
    @return: return a striped text.
    @rtype: unicode.
    """
    return  re.sub( HARAKAT_pattern, u'', text )

def stripTashkeel( text ):
    """Strip vowels from a text, include Shadda.
    The striped marks are :
    	- FATHA, DAMMA, KASRA
    	- SUKUN
    	- SHADDA
    	- FATHATAN, DAMMATAN, KASRATAN, , , .
    Example:
    	#>>> text=u"الْعَرَبِيّةُ"
    	#>>> stripTashkeel(text)
    	العربية#

    @param text: arabic text.
    @type text: unicode.
    @return: return a striped text.
    @rtype: unicode.
    """
    return re.sub( TASHKEEL_pattern, '', text );

def stripTatweel( text ):
    """
    Strip tatweel from a text and return a result text.

    Example:
    	#>>> text=u"العـــــربية"
    	#>>> stripTatweel(text)
    	العربية

    @param text: arabic text.
    @type text: unicode.
    @return: return a striped text.
    @rtype: unicode.
    """
    return re.sub( TATWEEL, '', text );

def normalizeLigature( text ):
	"""Normalize Lam Alef ligatures into two letters (LAM and ALEF), and Tand return a result text.
	Some systems present lamAlef ligature as a single letter, this function convert it into two letters,
	The converted letters into  LAM and ALEF are :
		- LAM_ALEF, LAM_ALEF_HAMZA_ABOVE, LAM_ALEF_HAMZA_BELOW, LAM_ALEF_MADDA_ABOVE

	Example:
		#>>> text=u"لانها لالء الاسلام"
		#>>> normalize_lamalef(text)
		لانها لالئ الاسلام

	@param text: arabic text.
	@type text: unicode.
	@return: return a converted text.
	@rtype: unicode.
	"""
	return LIGUATURES_pattern.sub( u'%s%s' % ( LAM, ALEF ), text )
#     #------------------------------------------------
def vocalizedlike( word, vocalized ):
    """return True if the given word have the same or the partial vocalisation like the pattern vocalized

	@param word: arabic word, full/partial vocalized.
	@type word: unicode.
	@param vocalized: arabic full vocalized word.
	@type vocalized: unicode.
	@return: True if vocalized.
	@rtype: unicode.
    """
    if not isVocalized( vocalized ) or not isVocalized( word ):
        if isVocalized( vocalized ):
            vocalized = stripTashkeel( vocalized );
        if isVocalized( word ):
            word = stripTashkeel( word );
        if word == vocalized:
            return True;
        else:
            return False;
    else:
        for mark in TASHKEEL:
            vocalized = re.sub( u"[%s]" % mark, u"[%s]?" % mark, vocalized )
    	vocalized = "^" + vocalized + "$";
    	pat = re.compile( "^" + vocalized + "$" );
    	if pat.match( "^" + vocalized + "$", word ):
    	    return True;
    	else: return False;
