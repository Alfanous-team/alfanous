# coding: utf-8


""" a space for tests and misc functions """

import sys
import locale

from  alfanous.Constantes import BUCKWALTER2UNICODE


#translation functions
import gettext
gettext.bindtextdomain( "fanous", "./locale" )
gettext.textdomain( "fanous" )
_ = gettext.gettext
N_ = gettext.ngettext


#get location
LOC = locale.getdefaultlocale()[0]

#get platform
SYS = sys.platform

def buck2uni( string, ignore = "" ):
    """ decode buckwalter """
    result = ""
    for char in string :
        if BUCKWALTER2UNICODE.has_key( char ) and char not in ignore:
            result += BUCKWALTER2UNICODE[char]
        else :
            result += char

    return result



#filter doubles
def filter_doubles( lst ):
    """ deprecated : use list(set()) or filter(cond,list) instead"""
    for i in range( len( lst ) ):
        if lst[i] not in lst[i + 1:]:
            yield lst[i]




if __name__ == '__main__':
    print "system is : ", SYS, " &language is :", LOC
    #Assem testing gettext
    print _( u"hello,i love Python" )
    print _( u"سلام" )
    print N_( u"man", u"men", 5 )

