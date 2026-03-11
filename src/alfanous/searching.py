from alfanous.results_processing import QSort, QScore
from alfanous.constants import QURAN_TOTAL_VERSES
from whoosh.sorting import Facets
from whoosh import query as wquery
from whoosh.collectors import TimeLimitCollector, FilterCollector
from whoosh.searching import TimeLimit
from whoosh.qparser import QueryParser as _QueryParser
import logging

logger = logging.getLogger(__name__)


def _decode_if_bytes(x):
    if isinstance(x, bytes):
        return x.decode('utf-8')
    return x


def _is_valid_term(x):
    """Return True for non-integer values and non-negative integers.

    Whoosh stores some numeric field values as Python ``int`` objects using an
    internal encoding where negative integers are sentinels that should not be
    surfaced as searchable term values.  Non-integer term values (strings) are
    always valid.  This predicate is used by :meth:`QReader.list_values` and
    :meth:`QReader.list_stored_values` to filter such internal sentinels from
    the public-facing term lists.

    Defined once at module level to avoid allocating a new closure on every
    ``list_values`` / ``list_stored_values`` call.
    """
    return not isinstance(x, int) or x >= 0


def _strip_phrase_queries(q):
    """Replace every ``Phrase`` node in *q* with an ``And`` of ``Term`` nodes.

    The ``aya_fuzzy`` field is indexed with ``phrase=False`` — it stores no
    positional information, so Whoosh raises ``QueryError`` whenever it tries
    to execute a ``Phrase`` query against it.  This helper walks the query
    tree and converts each ``Phrase`` node into an unordered ``And`` of
    ``Term`` nodes (preserving the individual tokens while dropping the
    adjacency/order requirement that the field cannot satisfy).

    The transformation is applied recursively so that phrases nested inside
    compound queries (``And``, ``Or``, ``AndNot``, etc.) are also converted.

    :param q: A Whoosh :class:`~whoosh.query.Query` object.
    :returns: A new query tree with all ``Phrase`` nodes replaced.
    """
    if isinstance(q, wquery.Phrase):
        terms = [wquery.Term(q.fieldname, word) for word in q.words]
        if not terms:
            return wquery.NullQuery
        if len(terms) == 1:
            return terms[0]
        return wquery.And(terms)

    if isinstance(q, wquery.BinaryQuery):
        # BinaryQuery subclasses (AndNot, AndMaybe, Require, Otherwise) store
        # their two children in .subqueries as a (a, b) tuple and accept the
        # same two positional arguments in their constructor.
        new_a = _strip_phrase_queries(q.subqueries[0])
        new_b = _strip_phrase_queries(q.subqueries[1])
        return type(q)(new_a, new_b)

    if isinstance(q, wquery.CompoundQuery):
        # And, Or, DisjunctionMax, Ordered, etc. store children in .subqueries
        # as a list and accept that list as their first constructor argument.
        new_subs = [_strip_phrase_queries(s) for s in q.subqueries]
        return type(q)(new_subs)

    if isinstance(q, wquery.Not):
        return wquery.Not(_strip_phrase_queries(q.query))

    return q


class QReader:
    """ reader of the index """

    def __init__(self, docindex):
        self._docindex = docindex
        self._own_reader = None  # Opened lazily only when no searcher is attached
        self._qsearcher = None
        self.schema = docindex.get_schema()

    def _ensure_own_reader(self):
        """Open and return our own IndexReader, creating it on first call."""
        if self._own_reader is None:
            self._own_reader = self._docindex.get_index().reader()
        return self._own_reader

    @property
    def reader(self):
        """Return the active Whoosh IndexReader.

        When :meth:`attach_to_searcher` has been called the reader is
        borrowed from the shared :class:`QSearcher`'s cached Whoosh
        Searcher so both components use a single underlying IndexReader.
        Otherwise an independently-opened reader is returned (opened lazily
        on first access).
        """
        if self._qsearcher is not None:
            return self._qsearcher.get_reader()
        return self._ensure_own_reader()

    def attach_to_searcher(self, qsearcher):
        """Share the IndexReader already open inside *qsearcher*'s cached searcher.

        After this call the QReader no longer maintains its own IndexReader;
        instead it borrows the one held by the QSearcher's cached Whoosh
        Searcher via the :attr:`reader` property.  This reduces the number of
        open IndexReaders per :class:`~alfanous.engines.BasicSearchEngine`
        from two to one.  When the QSearcher refreshes its searcher (because
        the index has changed), the QReader automatically picks up the new
        reader on the next attribute access.

        Because the reader is now lazily opened in standalone mode, calling
        this method before any :attr:`reader` access means *no* own reader is
        ever opened, making the attach completely free.

        :param qsearcher: The :class:`QSearcher` instance whose shared reader
            to borrow.
        """
        self._qsearcher = qsearcher
        if self._own_reader is not None:
            try:
                self._own_reader.close()
            except Exception:
                pass
            self._own_reader = None

    def close(self):
        """Close the owned IndexReader and release any held resources.

        When attached to a :class:`QSearcher` via :meth:`attach_to_searcher`
        the reader is owned by the searcher and is *not* closed here.
        """
        if self._qsearcher is not None:
            return
        if self._own_reader is not None:
            try:
                self._own_reader.close()
            except Exception:
                pass
            self._own_reader = None

    def __del__(self):
        """Ensure any owned reader is closed when the object is garbage collected."""
        try:
            self.close()
        except Exception:
            pass

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def list_values(self, fieldname):
        reader = self.reader
        try:
            return list(filter(_is_valid_term,
                               (_decode_if_bytes(v) for v in reader.field_terms(fieldname))))
        except KeyError:
            return []

    def list_stored_values(self, fieldname):
        """ List unique stored (non-tokenized) values for a field, preserving full phrases. """
        reader = self.reader
        values = set()
        try:
            # Optimised path: use kind="aya" posting list to visit only parent
            # aya documents.  Thematic fields (chapter, topic, subtopic) only
            # appear on aya docs (~6 236 entries), so iterating all ~300 k docs
            # via iter_docs() would waste ~50× more work.
            postings = reader.postings("kind", "aya")
            while postings.is_active():
                stored = reader.stored_fields(postings.id())
                value = stored.get(fieldname)
                if value is not None and value != "":
                    values.add(value)
                postings.next()
        except (KeyError, TypeError, AttributeError):
            # Fallback for indexes built without a "kind" field or with an
            # incompatible reader implementation.
            logger.debug(
                "list_stored_values(%r): 'kind' field unavailable, "
                "falling back to full iter_docs() scan",
                fieldname,
            )
            for _, stored_fields in reader.iter_docs():
                value = stored_fields.get(fieldname)
                if value is not None and value != "":
                    values.add(value)
        return sorted(filter(_is_valid_term, values))

    def term_stats(self, terms):
        """ return all statistiques of a term
         - document frequency
         - matches frequency
         """
        reader = self.reader
        for term in terms:
            lst = list(term)
            lst.extend([reader.frequency(*term), reader.doc_frequency(*term)])
            yield tuple(lst)

    def autocomplete(self, word):
        reader = self.reader
        return [_decode_if_bytes(x) for x in reader.expand_prefix('aya_ac', word)]


class _SearcherProxy:
    """Proxy that wraps a shared Whoosh searcher.

    ``close()`` and ``__exit__()`` are intentional no-ops so that callers
    who follow the standard ``results, terms, searcher = …; searcher.close()``
    pattern do not accidentally destroy the single cached searcher owned by
    :class:`QSearcher`.  All other attribute access is delegated transparently
    to the underlying searcher.
    """

    __slots__ = ("_s",)

    def __init__(self, searcher):
        object.__setattr__(self, "_s", searcher)

    def close(self):
        """No-op: the shared searcher is managed by :class:`QSearcher`."""
        pass

    def __enter__(self):
        return self

    def __exit__(self, *args):
        """No-op: the shared searcher is managed by :class:`QSearcher`."""
        pass

    def __getattr__(self, name):
        return getattr(object.__getattribute__(self, "_s"), name)

    def __bool__(self):
        return bool(object.__getattribute__(self, "_s"))


class QSearcher:
    """ search"""

    def __init__(self, docindex, qparser):
        self._searcher = docindex.get_index().searcher
        self._qparser = qparser
        self._schema = docindex.get_schema()
        self._shared_searcher = None
        # Lazily cached parser for the 'aya_fuzzy' field — created on first
        # fuzzy search and reused thereafter.  The parser is stateless (it
        # only holds a field name and a schema reference, both of which are
        # fixed for the lifetime of this QSearcher) so it is safe to cache.
        self._fuzzy_parser = None

    def _get_shared_searcher(self):
        """Return a cached Whoosh searcher, refreshing it when the index changes.

        The first call lazily opens the searcher.  Subsequent calls invoke
        ``searcher.refresh()``: if the underlying index generation has not
        changed the same object is returned (zero cost); if it has changed a
        new searcher is returned and the stale one is closed to free resources.
        """
        if self._shared_searcher is None:
            self._shared_searcher = self._searcher(weighting=QScore())
        else:
            refreshed = self._shared_searcher.refresh()
            if refreshed is not self._shared_searcher:
                old = self._shared_searcher
                self._shared_searcher = refreshed
                try:
                    old.close()
                except Exception:
                    pass
        return self._shared_searcher

    def get_reader(self):
        """Return the Whoosh IndexReader from the cached shared searcher.

        This is the public accessor used by :class:`QReader` when sharing
        the underlying IndexReader instead of maintaining its own.  The
        reader is valid as long as the shared searcher is open.
        """
        return self._get_shared_searcher().reader()

    def close(self):
        """Close the cached shared searcher and release all held resources."""
        if self._shared_searcher is not None:
            try:
                self._shared_searcher.close()
            except Exception:
                pass
            self._shared_searcher = None

    def __del__(self):
        """Ensure the shared searcher is closed on garbage collection."""
        try:
            self.close()
        except Exception:
            pass

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def search(self, querystr, limit=QURAN_TOTAL_VERSES, sortedby="score", reverse=False, facets=None, filter_dict=None, fuzzy=False, fuzzy_maxdist=1, timelimit=5.0):
        searcher = self._get_shared_searcher()
        query = self._qparser.parse(querystr)

        if fuzzy:
            # Strategy 2: Search the normalised/stemmed 'aya_fuzzy' field (fed
            # from the same vocalized source text as aya_, processed at index
            # time: diacritics stripped → stop words removed → synonyms expanded
            # → Snowball Arabic stem).  This broadens the result set without any
            # query-time CPU cost.
            # Guard against StopIteration from Whoosh's internal analyzer
            # pipeline: when every token in querystr is a stop word in the
            # aya_fuzzy field's analyzer, the MultiFilter inside that analyzer
            # calls next() on an empty stream and raises StopIteration.
            if self._fuzzy_parser is None:
                self._fuzzy_parser = _QueryParser("aya_fuzzy", schema=self._schema)
            try:
                aya_fuzzy_query = self._fuzzy_parser.parse(querystr)
                # 'aya_fuzzy' has phrase=False (no position data), so any
                # Phrase sub-query produced by parsing quoted text would raise
                # QueryError at execution time.  Convert each Phrase node to an
                # unordered And-of-Terms so the individual tokens are still
                # required but no positional constraint is enforced.
                if aya_fuzzy_query is not None:
                    aya_fuzzy_query = _strip_phrase_queries(aya_fuzzy_query)
            except StopIteration:
                aya_fuzzy_query = None

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
                wquery.FuzzyTerm("aya_ac", term, maxdist=fuzzy_maxdist, prefixlength=1)
                for fieldname, term in query.all_terms()
                if isinstance(term, str) and len(term) >= 4 and any('\u0600' <= c <= '\u06FF' for c in term)
            ]

            parts = [query]
            if aya_fuzzy_query is not None:
                parts.append(aya_fuzzy_query)
            if levenshtein_subqueries:
                parts.append(
                    wquery.Or(levenshtein_subqueries)
                    if len(levenshtein_subqueries) > 1
                    else levenshtein_subqueries[0]
                )
            query = wquery.Or(parts)

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

        collector_kwargs = dict(limit=limit, sortedby=QSort(sortedby), reverse=reverse, groupedby=groupedby, terms=fuzzy)
        if timelimit is not None:
            c = searcher.collector(**collector_kwargs)
            tlc = TimeLimitCollector(c, timelimit=timelimit, use_alarm=False)
            # FilterCollector must wrap TimeLimitCollector (not the other way)
            # so that filter logic in FilterCollector.collect_matches() is
            # applied correctly.  Wrapping in the reverse order causes
            # TimeLimitCollector.collect_matches() to call child.collect()
            # directly, bypassing FilterCollector's allow-set check.
            final_c = FilterCollector(tlc, allow=filter_query) if filter_query is not None else tlc
            try:
                searcher.search_with_collector(query, final_c)
            except TimeLimit:
                logger.warning("Search timelimit of %s seconds reached; returning partial results", timelimit)
            results = final_c.results()
        else:
            results = searcher.search(query, **collector_kwargs, filter=filter_query)

        if fuzzy:
            # Use matched_terms() to capture the actual index terms that were
            # hit, including all fuzzy variations expanded by FuzzyTerm.
            # Whoosh returns term texts as bytes; decode to unicode strings so
            # downstream code (highlighting, term stats) can handle them.
            # matched_terms() returns None when terms=True was not passed, and
            # an empty set when there are no results.
            # Non-UTF-8 bytes come from numeric fields (e.g. a_g:1 encodes the
            # integer as raw bytes); skip those entries because they are not
            # text terms and cannot be used for highlighting or term stats.
            raw_matched = results.matched_terms()
            if raw_matched is not None and raw_matched:
                # Accumulate directly into a set to avoid building a temporary
                # list that is then immediately converted to frozenset.
                decoded_terms = set()
                for fieldname, text in raw_matched:
                    if isinstance(text, bytes):
                        try:
                            decoded_terms.add((fieldname, text.decode("utf-8")))
                        except UnicodeDecodeError:
                            logger.debug(
                                "Skipping non-UTF-8 matched term in field %r (numeric encoding): %r",
                                fieldname, text,
                            )
                    else:
                        decoded_terms.add((fieldname, text))
                terms = frozenset(decoded_terms)
            else:
                terms = query.all_terms()
        else:
            terms = query.all_terms()

        return results, terms, _SearcherProxy(searcher)

    def search_obj(self, q_obj, limit=QURAN_TOTAL_VERSES, sortedby="score", reverse=False, timelimit=5.0):
        """Run a pre-built Whoosh query object (e.g. NestedParent) directly,
        bypassing string parsing.  Returns the same ``(results, terms, searcher)``
        tuple as :meth:`search` but with an empty *terms* list."""
        searcher = self._get_shared_searcher()
        search_kwargs = dict(limit=limit, sortedby=QSort(sortedby), reverse=reverse)
        if timelimit is not None:
            c = searcher.collector(**search_kwargs)
            tlc = TimeLimitCollector(c, timelimit=timelimit, use_alarm=False)
            try:
                searcher.search_with_collector(q_obj, tlc)
            except TimeLimit:
                logger.warning("Search timelimit of %s seconds reached; returning partial results", timelimit)
            results = tlc.results()
        else:
            results = searcher.search(q=q_obj, **search_kwargs)
        return results, [], _SearcherProxy(searcher)

    def suggest(self, querystr):
        d = {}
        searcher = self._get_shared_searcher()
        # Use aya_ac: unvocalized, non-stemmed field with spelling index
        corrector = searcher.corrector("aya_ac")
        for mistyped_word in querystr.split():
            d[mistyped_word] = corrector.suggest(mistyped_word, limit=3, maxdist=1, prefix=False)
        return d

    def suggest_collocations(self, word, limit=5, stopwords=None):
        """Find words that frequently co-occur with *word* in the same Quranic verse.

        Searches the 'aya_ac' field for all verses containing *word*, then
        counts how often every other word appears in those same verses.  The
        *limit* most frequent co-occurring words are returned as two-word
        collocation phrases (e.g. ``'سميع عليم'``).

        :param word: A single unvocalized Arabic word to find collocations for.
        :param limit: Maximum number of collocation phrases to return (default 5).
        :param stopwords: Optional set of words to exclude from collocations.
            When ``None`` the caller is responsible for pre-filtering.
        :returns: List of two-word collocation strings ordered by co-occurrence
            frequency, e.g. ``['سميع عليم', 'سميع بصير']``.
        """
        from collections import Counter

        searcher = self._get_shared_searcher()
        q = wquery.Term("aya_ac", word)
        results = searcher.search(q, limit=QURAN_TOTAL_VERSES)

        _stop = stopwords or frozenset()
        co_counts = Counter()
        for hit in results:
            aya_text = hit.get("aya") or ""
            for w in aya_text.split():
                if w != word and w not in _stop and len(w) > 1:
                    co_counts[w] += 1

        return ["{} {}".format(word, co_word) for co_word, _ in co_counts.most_common(limit)]

    def correct_query(self, querystr):
        """Return a corrected version of *querystr* using Whoosh's built-in
        query corrector.

        Whoosh's ``searcher.correct_query()`` analyses each term in the parsed
        query against the index vocabulary and replaces unknown terms with the
        closest known alternative.  It returns a :class:`whoosh.searching.Correction`
        object whose ``.string`` attribute contains the rewritten query string
        ready to pass back to the search engine.

        @param querystr: The raw query string entered by the user.
        @return: Dictionary with keys ``original`` (the input) and
                 ``corrected`` (the best rewritten query string, identical to
                 the input when no correction is needed).
        """
        searcher = self._get_shared_searcher()
        parsed = self._qparser.parse(querystr)
        correction = searcher.correct_query(parsed, querystr)
        return {"original": querystr, "corrected": correction.string}
