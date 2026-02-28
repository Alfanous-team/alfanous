#!/usr/bin/env python3

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
from .strip_functions import *
from .normalizers import *
from .predicates import *
from .constants import *


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
    if archar in AlphabeticOrder:
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
    if archar in NAMES:
        return NAMES[archar]
    else:
        return ''

def arabicrange():
    """return a list of arabic characteres .
    Return a list of characteres between \u060c to \u0652
    @return: list of arabic characteres.
    @rtype: unicode;
    
    >>> expected = list(map( lambda char: chr( char ), range( 0x0600, 0x00653 ) ))
    >>> arabicrange() == expected
    True
    >>> arabicrange() == expected
    True
    """
    if _arabic_range: return _arabic_range
    else: return list(map( chr, range( 0x0600, 0x00653 ) ))
