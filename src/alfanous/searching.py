from alfanous.results_processing import QSort, QScore
from whoosh.sorting import Facets, FieldFacet


class QReader:
    """ reader of the index """

    def __init__(self, docindex):
        self.reader = docindex.get_index().reader()
        self.schema = docindex.get_schema()

    def list_values(self, fieldname):

        return list(filter(lambda x: type(x) is not int or x>=0, self.reader.field_terms(fieldname)))


    def list_terms(self, fieldname=None, double=False):
        """
        a choosen field indexed terms generator

        @param fieldname: the name of the choosen field
        @return : indexed terms

        """
        prec = []
        for field, value in self.reader.all_terms():
            if field == fieldname or not fieldname:
                if value not in prec:
                    prec.append(value)
                    yield value


    def term_stats(self, terms):
        """ return all statistiques of a term
         - document frequency
         - matches frequency
         """
        for term in terms:
            lst = list(term)
            lst.extend([self.reader.frequency(*term), self.reader.doc_frequency(*term)])
            yield tuple(lst)

    def autocomplete(self, word):
        return [x.decode('utf-8') for x in self.reader.expand_prefix('aya', word)]


class QSearcher:
    """ search"""

    def __init__(self, docindex, qparser):
        self._searcher = docindex.get_index().searcher
        self._qparser = qparser

    def search(self, querystr, limit=6236, sortedby="score", reverse=False, facets=None):
        searcher = self._searcher(weighting=QScore())
        query = self._qparser.parse(querystr)
        
        # Prepare facets if requested
        groupedby = None
        if facets:
            groupedby = Facets()
            for facet_field in facets:
                groupedby.add_field(facet_field)
        
        results = searcher.search(q=query, limit=limit, sortedby=QSort(sortedby), reverse=reverse, groupedby=groupedby)

        terms = query.all_terms()


        return results, terms, searcher


    def suggest(self, querystr):
        d = {}
        corrector = self._searcher(weighting=QScore()).corrector('aya')
        for mistyped_word in querystr.split():
            d[mistyped_word] =  corrector.suggest(mistyped_word, limit=3,maxdist=1, prefix=False)
        return d
