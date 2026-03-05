from alfanous.results_processing import QSort, QScore
from alfanous.constants import QURAN_TOTAL_VERSES
from whoosh.sorting import Facets
from whoosh import query as wquery


class QReader:
    """ reader of the index """

    def __init__(self, docindex):
        self.reader = docindex.get_index().reader()
        self.schema = docindex.get_schema()

    def list_values(self, fieldname):

        return list(filter(lambda x: type(x) is not int or x>=0, self.reader.field_terms(fieldname)))

    def list_stored_values(self, fieldname):
        """ List unique stored (non-tokenized) values for a field, preserving full phrases. """
        values = set()
        for _, stored_fields in self.reader.iter_docs():
            value = stored_fields.get(fieldname)
            if value is not None and value != "":
                values.add(value)
        return sorted(filter(lambda x: type(x) is not int or x >= 0, values))


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
        return [x.decode('utf-8') for x in self.reader.expand_prefix('aya_ac', word)]


class QSearcher:
    """ search"""

    def __init__(self, docindex, qparser):
        self._searcher = docindex.get_index().searcher
        self._qparser = qparser
        self._schema = docindex.get_schema()

    def search(self, querystr, limit=QURAN_TOTAL_VERSES, sortedby="score", reverse=False, facets=None, filter_dict=None, fuzzy=False, fuzzy_maxdist=1):
        searcher = self._searcher(weighting=QScore())
        query = self._qparser.parse(querystr)

        if fuzzy:
            from whoosh.qparser import QueryParser
            from whoosh.query import Or, FuzzyTerm

            # Strategy 2: Search the normalised/stemmed 'aya_fuzzy' field (fed
            # from the same vocalized source text as aya_, processed at index
            # time: diacritics stripped → stop words removed → synonyms expanded
            # → Snowball Arabic stem).  This broadens the result set without any
            # query-time CPU cost.
            aya_fuzzy_parser = QueryParser("aya_fuzzy", schema=self._schema)
            aya_fuzzy_query = aya_fuzzy_parser.parse(querystr)

            # Strategy 3: Levenshtein distance matching on 'aya_ac'
            # (unvocalized, non-stemmed) to handle spelling variants and typos.
            # Only applied to Arabic-script terms; structured/numeric terms are
            # skipped.
            # prefixlength=1 keeps the first character fixed so that expansion
            # is bounded to plausible variants (e.g. "الكتاب" → "الكتابة") rather
            # than unrelated words that happen to be edit-close.  This trades a
            # small amount of recall for a large gain in precision and scan
            # performance.
            levenshtein_subqueries = [
                FuzzyTerm("aya_ac", term, maxdist=fuzzy_maxdist, prefixlength=1)
                for fieldname, term in query.all_terms()
                if term and any('\u0600' <= c <= '\u06FF' for c in term)
            ]

            parts = [query, aya_fuzzy_query]
            if levenshtein_subqueries:
                parts.append(
                    Or(levenshtein_subqueries)
                    if len(levenshtein_subqueries) > 1
                    else levenshtein_subqueries[0]
                )
            query = Or(parts)
        
        # Prepare facets if requested
        groupedby = None
        if facets:
            groupedby = Facets()
            for facet_field in facets:
                groupedby.add_field(facet_field)
        
        # Prepare filter if provided
        filter_query = None
        if filter_dict:
            filter_queries = []
            for field, value in filter_dict.items():
                if isinstance(value, list):
                    # Multiple values for same field (OR condition)
                    or_queries = [wquery.Term(field, v) for v in value]
                    filter_queries.append(wquery.Or(or_queries))
                else:
                    # Single value
                    filter_queries.append(wquery.Term(field, value))
            
            if len(filter_queries) == 1:
                filter_query = filter_queries[0]
            elif len(filter_queries) > 1:
                filter_query = wquery.And(filter_queries)
        
        results = searcher.search(q=query, limit=limit, sortedby=QSort(sortedby), reverse=reverse, groupedby=groupedby, filter=filter_query)

        terms = query.all_terms()


        return results, terms, searcher


    def suggest(self, querystr):
        d = {}
        searcher = self._searcher(weighting=QScore())
        try:
            # Use aya_ac: unvocalized, non-stemmed field with spelling index
            corrector = searcher.corrector("aya_ac")
            for mistyped_word in querystr.split():
                d[mistyped_word] = corrector.suggest(mistyped_word, limit=3, maxdist=1, prefix=False)
        finally:
            searcher.close()
        return d
