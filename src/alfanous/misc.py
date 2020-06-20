# coding: utf-8


FILTER_DOUBLES = filter_doubles = lambda lst:list( set( lst ) )
LOCATE = lambda source, dist, itm: dist[source.index( itm )] \
												if itm in source else None
FIND = lambda source, dist, itm: [dist[i] for i in [i for i in range( len( source ) ) if source[i] == itm]]
