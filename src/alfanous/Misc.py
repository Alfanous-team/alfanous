# coding: utf-8

""" Misc functions """

#localization functions
#import gettext
#gettext.bindtextdomain( "fanous", "./locale" )
#gettext.textdomain( "fanous" )
#_ = gettext.gettext
#N_ = gettext.ngettext


##get location
#import locale
#LOC = locale.getdefaultlocale()[0]

##get platform
#import sys
#SYS = sys.platform

FILTER_DOUBLES = filter_doubles = lambda lst:list( set( lst ) )
LOCATE = lambda source, dist, itm: dist[source.index( itm )] \
												if itm in source else None
FIND = lambda source, dist, itm: [dist[i] for i in [i for i in range( len( source ) ) if source[i] == itm]]
