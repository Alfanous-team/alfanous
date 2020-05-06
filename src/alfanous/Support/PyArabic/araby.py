#!/usr/bin/python2
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
from araby_strip_functions import *
from araby_normalizers import *
from araby_predicates import *
from araby_constants import *


_arabic_range = None


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
