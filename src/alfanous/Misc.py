# coding: utf-8


""" a space for tests and misc functions """

import sys
import locale

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

FILTER_DOUBLES = filter_doubles = lambda lst:list( set( lst ) )
LOCATE = lambda source, dist, itm: dist[source.index( itm )] \
												if itm in source else None
FIND = lambda source, dist, itm: [dist[i] for i in [i for i in range( len( source ) ) if source[i] == itm]]



if __name__ == '__main__':
    print "system is : ", SYS, " &language is :", LOC
    #Assem testing gettext
    print _( u"hello,i love Python" )
    print _( u"سلام" )
    print N_( u"man", u"men", 5 )

