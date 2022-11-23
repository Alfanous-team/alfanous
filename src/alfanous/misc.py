
filter_doubles = lambda lst :list(set(lst))
locate = lambda source, dist, itm: dist[source.index(itm)] \
												if itm in source else None
find = lambda source, dist, itm: [dist[i] for i in [i for i in range(len(source)) if source[i] == itm]]
