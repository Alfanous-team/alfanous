from alfanous.results_processing import QSort, QScore
from alfanous.constants import QURAN_TOTAL_VERSES
from whoosh.sorting import Facets
from whoosh import query as wquery
from whoosh.collectors import TimeLimitCollector, FilterCollector
from whoosh.searching import TimeLimit
from whoosh.qparser import QueryParser as _QueryParser
from whoosh.reading import ReaderClosed
import logging

logger = logging.getLogger(__name__)

# Maximum number of attempts for operations that can fail with ReaderClosed.
# On attempt 1 the shared searcher is reset and reopened; if attempt 2 also
# fails the exception is propagated to the caller (except correct_query which
# falls back gracefully to the original query string).
_MAX_READER_CLOSED_RETRIES = 2


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


def _strip_phrase_queries(q, schema=None):
    """Replace Phrase nodes that target fields without positional info with And-of-Terms.

    Whoosh raises ``QueryError: Phrase search: '<field>' field has no
    positions`` when a ``Phrase`` query is executed against any field that
    does not store positional data — this includes ``ID``, ``KEYWORD``, and
    ``NUMERIC`` field types as well as ``TEXT`` fields built with
    ``phrase=False`` (e.g. ``aya_fuzzy``).

    This helper walks the query tree and converts each such ``Phrase`` node
    into an unordered ``And`` of ``Term`` nodes, preserving the individual
    tokens while dropping the adjacency/order constraint that the field cannot
    satisfy.

    When *schema* is ``None`` every ``Phrase`` node is converted regardless of
    field — this is the backward-compatible behaviour used when stripping the
    ``aya_fuzzy`` sub-query where the entire sub-query targets a single
    ``phrase=False`` field.

    When *schema* is provided a ``Phrase`` node is only replaced when the
    targeted field does **not** support positional information (i.e.
    ``schema[fieldname].supports('positions')`` returns ``False`` or the
    field has no format at all).  Phrase nodes targeting TEXT fields that
    do store positions (e.g. ``aya``, ``aya_``, translation fields) are left
    intact so that exact phrase matching still works for those fields.

    The transformation is applied recursively so that phrases nested inside
    compound queries (``And``, ``Or``, ``AndNot``, etc.) are also converted.

    :param q: A Whoosh :class:`~whoosh.query.Query` object.
    :param schema: Optional Whoosh :class:`~whoosh.fields.Schema`.  When
        provided, only Phrase nodes whose field lacks positional support are
        replaced.
    :returns: A new query tree with qualifying ``Phrase`` nodes replaced.
    """
    if isinstance(q, wquery.Phrase):
        if schema is not None and q.fieldname in schema:
            # Leave the Phrase intact for fields that DO support positions
            # (TEXT fields with phrase=True).  Only strip phrases for fields
            # that have no positional data (ID, KEYWORD, NUMERIC, STORED, or
            # TEXT with phrase=False).
            # STORED fields have format=None so FieldType.supports() raises
            # AttributeError.  Check format is not None before calling it.
            field = schema[q.fieldname]
            if getattr(field, 'format', None) is not None and field.supports('positions'):
                return q

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
        new_a = _strip_phrase_queries(q.subqueries[0], schema)
        new_b = _strip_phrase_queries(q.subqueries[1], schema)
        return type(q)(new_a, new_b)

    if isinstance(q, wquery.CompoundQuery):
        # And, Or, DisjunctionMax, Ordered, etc. store children in .subqueries
        # as a list and accept that list as their first constructor argument.
        new_subs = [_strip_phrase_queries(s, schema) for s in q.subqueries]
        return type(q)(new_subs)

    if isinstance(q, wquery.Not):
        return wquery.Not(_strip_phrase_queries(q.query, schema))

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

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def search(self, querystr, limit=QURAN_TOTAL_VERSES, sortedby="score", reverse=False, facets=None, filter_dict=None, fuzzy=False, fuzzy_maxdist=1, fuzzy_derivation=True, timelimit=5.0):
        # Parse FIRST, before obtaining the shared searcher.  Query plugins
        # (DerivationPlugin, TuplePlugin, …) call engine._reader.reader →
        # QSearcher.get_reader() → _get_shared_searcher() during parse().
        # If the underlying Whoosh index has changed since the last request,
        # that internal call refreshes the shared searcher and closes the
        # previous one.  Parsing before we take our own reference ensures that
        # any plugin-triggered refresh has already happened, so the reference
        # we obtain below belongs to the post-refresh searcher and is not stale.
        query = self._qparser.parse(querystr)

        # Strip phrase queries for fields that do not support positional
        # information.  ID, KEYWORD, NUMERIC, and TEXT(phrase=False) fields
        # (e.g. 'topic', 'chapter', 'subtopic', 'aya_fuzzy') cannot execute
        # phrase queries and Whoosh would raise QueryError at search time.
        # Phrases targeting TEXT fields with phrase=True (e.g. 'aya', 'aya_',
        # translation fields) are preserved so exact phrase matching works.
        query = _strip_phrase_queries(query, schema=self._schema)

        # Capture the original query terms before any expansion (fuzzy or
        # derivation) so that derivation-expansion terms can be excluded from
        # the matched terms returned to callers.  Callers (e.g. outputs.py)
        # use the returned terms to build per-word statistics and the
        # words.individual list; if derivation-expansion terms polluted that
        # list the wrong word would appear at index 1 and its
        # 'nb_variations' would be 0.
        _original_query_terms: "frozenset[tuple]" = frozenset(query.all_terms())

        # Derivation expansion — always active when fuzzy_derivation=True.
        # fuzzy=True  → root-level (level=2) derivations (like >>word)
        # fuzzy=False → lemma-level (level=1) derivations (like >word)
        #
        # _derivation_expansion tracks every (fieldname, text) pair added
        # so they can be excluded from the matched-terms set returned to
        # callers.  Derivation terms are search-expansion internals, not
        # user keywords; including them in words_output would replace the
        # original query word with a derivation at position 1 and produce
        # incorrect per-word statistics (e.g. nb_variations == 0).
        derivation_subqueries = []
        _derivation_expansion: "set[tuple]" = set()
        if fuzzy_derivation:
            from alfanous.query_plugins import DerivationQuery
            deriv_level = 2 if fuzzy else 1  # 2 = root (>>word), 1 = lemma (>word)
            seen_derivation_terms = set()
            for _fieldname, term in query.all_terms():
                if not (isinstance(term, str) and any('\u0600' <= c <= '\u06FF' for c in term)):
                    continue
                if term in seen_derivation_terms:
                    continue
                seen_derivation_terms.add(term)
                derivations = DerivationQuery._get_derivations(term, deriv_level)
                for d in derivations:
                    if d and d != term:
                        derivation_subqueries.append(wquery.Term("aya", d))
                        _derivation_expansion.add(("aya", d))

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
            if derivation_subqueries:
                parts.append(
                    wquery.Or(derivation_subqueries)
                    if len(derivation_subqueries) > 1
                    else derivation_subqueries[0]
                )
            query = wquery.Or(parts)
        elif derivation_subqueries:
            # Non-fuzzy mode with lemma-level derivation expansion: OR the
            # derivation terms with the original query.
            deriv_part = (
                wquery.Or(derivation_subqueries)
                if len(derivation_subqueries) > 1
                else derivation_subqueries[0]
            )
            query = wquery.Or([query, deriv_part])

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

        _has_derivation_expansion = bool(_derivation_expansion)
        collector_kwargs = dict(limit=limit, sortedby=QSort(sortedby), reverse=reverse, groupedby=groupedby, terms=(fuzzy or _has_derivation_expansion))

        # Obtain the shared searcher AFTER parsing so that any plugin-triggered
        # refresh has already completed (see comment at the top of this method).
        # Retry once on ReaderClosed: a concurrent refresh between _get_shared_searcher()
        # and the actual search call can still close the reader in rare conditions
        # (e.g. mmap I/O releasing the GIL).  On the second failure the exception
        # is re-raised so the caller sees a clean error rather than silent wrong results.
        for attempt in range(_MAX_READER_CLOSED_RETRIES):
            searcher = self._get_shared_searcher()
            try:
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
                break  # success — exit retry loop
            except ReaderClosed:
                if attempt == 0:
                    # Force _get_shared_searcher() to reopen on the next attempt.
                    self._shared_searcher = None
                    logger.warning(
                        "search: Underlying index reader was closed during search "
                        "for query %r; retrying with a fresh searcher.",
                        querystr,
                    )
                    continue
                # Second failure: re-raise so the caller receives a clean error.
                logger.error(
                    "search: Underlying index reader still closed on retry for "
                    "query %r; propagating ReaderClosed.",
                    querystr,
                )
                raise

        if fuzzy or _has_derivation_expansion:
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
                # Exclude derivation-expansion terms from the terms returned to
                # callers.  These are search-expansion internals (added to
                # broaden recall) and must NOT appear in words_output as
                # separate keyword entries: if they did, the first entry in
                # words.individual would be a derivation word rather than the
                # user's actual query word, causing incorrect nb_variations == 0.
                # Exception: keep a derivation term if it was also part of the
                # user's original query (e.g. the user explicitly typed it).
                if _derivation_expansion:
                    decoded_terms -= (_derivation_expansion - _original_query_terms)
                terms = frozenset(decoded_terms)
            else:
                terms = _original_query_terms
        else:
            terms = query.all_terms()

        return results, terms, _SearcherProxy(searcher)

    def search_obj(self, q_obj, limit=QURAN_TOTAL_VERSES, sortedby="score", reverse=False, timelimit=5.0):
        """Run a pre-built Whoosh query object (e.g. NestedParent) directly,
        bypassing string parsing.  Returns the same ``(results, terms, searcher)``
        tuple as :meth:`search` but with an empty *terms* list."""
        search_kwargs = dict(limit=limit, sortedby=QSort(sortedby), reverse=reverse)
        for attempt in range(_MAX_READER_CLOSED_RETRIES):
            searcher = self._get_shared_searcher()
            try:
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
            except ReaderClosed:
                if attempt == 0:
                    self._shared_searcher = None
                    logger.warning(
                        "search_obj: Underlying index reader was closed; "
                        "retrying with a fresh searcher.",
                    )
                    continue
                logger.error(
                    "search_obj: Underlying index reader still closed on retry; "
                    "propagating ReaderClosed.",
                )
                raise

    def suggest(self, querystr):
        d = {}
        searcher = self._get_shared_searcher()
        # Use aya_ac: unvocalized, non-stemmed field with spelling index
        corrector = searcher.corrector("aya_ac")
        for mistyped_word in querystr.split():
            d[mistyped_word] = corrector.suggest(mistyped_word, limit=3, maxdist=1, prefix=False)
        return d

    def suggest_collocations(self, word, limit=5, stopwords=None, trigram_min_count=2):
        """Find bigrams and trigrams containing *word* using the Whoosh shingle index.

        Uses the ``aya_shingles`` index field — built at index time with
        :data:`~alfanous.text_processing.QShingleAnalyzer` (Whoosh's
        :class:`~alfanous.text_processing.QShingleFilter`) — to look up
        pre-computed word n-grams and their corpus frequencies directly from
        the index, without scanning individual documents.

        All shingle terms in the index that contain *word* as one of their
        space-separated components are considered:

        * **Bigrams** (2-word shingles): included unless the *other* word is in
          *stopwords* or is a single character.
        * **Trigrams** (3-word shingles): included only when their total
          occurrence count across the corpus is ≥ *trigram_min_count*.

        Results are sorted by the Whoosh-computed total term frequency (number
        of occurrences in the full corpus) so the most characteristic Quranic
        phrases appear first.

        :param word: An Arabic word (ideally unvocalized) to find collocations
            for.  The word is matched exactly against the ``aya_shingles`` term
            dictionary, which is indexed with :data:`QStandardAnalyzer`-style
            normalization (Uthmani symbol removal, lamalef, tatweel).  Passing a
            fully vocalized word will return no results if the normalized form
            differs.  Multi-word strings will simply not match any shingle entry.
        :param limit: Maximum number of phrases to return (default 5).
        :param stopwords: Words to exclude from bigram neighbours.
            ``None`` means no filtering.
        :param trigram_min_count: Minimum total corpus occurrence count for a
            trigram to be considered relevant (default 2).
        :returns: List of 2- or 3-word phrase strings ordered by corpus
            frequency, e.g. ``['والله سميع عليم', 'سميع عليم', 'سميع بصير']``.
        """
        for attempt in range(_MAX_READER_CLOSED_RETRIES):
            searcher = self._get_shared_searcher()
            reader = searcher.reader()
            try:
                # Check that the aya_shingles field exists in this index.
                if "aya_shingles" not in reader.indexed_field_names():
                    # Graceful fallback: the index predates the aya_shingles field.
                    return []

                _stop = stopwords or frozenset()

                candidates: list = []

                for term_text in reader.field_terms("aya_shingles"):
                    parts = term_text.split()
                    n = len(parts)

                    # Only include shingles that contain the query word as a component.
                    if word not in parts:
                        continue

                    freq = reader.frequency("aya_shingles", term_text)

                    if n == 2:
                        # Bigram: skip if the other word is a stopword or single char
                        other = parts[1] if parts[0] == word else parts[0]
                        if other in _stop or len(other) <= 1:
                            continue
                    elif n == 3:
                        # Trigram: apply relevance threshold
                        if freq < trigram_min_count:
                            continue
                        # Skip trigrams where any non-query part is a stopword or single char
                        others = [p for p in parts if p != word]
                        if any(p in _stop or len(p) <= 1 for p in others):
                            continue

                    candidates.append((freq, term_text))

                candidates.sort(key=lambda x: x[0], reverse=True)

                result: list = []
                for _, phrase in candidates:
                    result.append(phrase)
                    if len(result) == limit:
                        break
                return result
            except ReaderClosed:
                if attempt == 0:
                    self._shared_searcher = None
                    logger.warning(
                        "suggest_collocations: Underlying index reader was closed "
                        "for word %r; retrying with a fresh searcher.",
                        word,
                    )
                    continue
                logger.error(
                    "suggest_collocations: Underlying index reader still closed on "
                    "retry for word %r; returning empty list.",
                    word,
                )
        return []

    def suggest_extensions(self, prefix_text, limit=10):
        """Find shingles in ``aya_shingles`` that *extend* a typed prefix.

        Unlike :meth:`suggest_collocations` — which finds all shingles
        containing a given word anywhere — this method returns only shingles
        whose **first words exactly match** *prefix_text*.  That makes it the
        right tool for autocomplete: whatever the user has already typed is kept
        intact, and the suggestions are longer phrases that complete it.

        Examples with a corpus that contains "الحمد لله رب العالمين" and
        "رسول الله الكريم"::

            suggest_extensions("الحمد")
                → ["الحمد لله", "الحمد لله رب"]   # bigram + trigram starting with الحمد

            suggest_extensions("الحمد لله")
                → ["الحمد لله رب"]                 # trigram that extends the bigram

            suggest_extensions("رسول")
                → ["رسول الله", "رسول الله الكريم"]  # NOT "محمد رسول" (doesn't start with رسول)

            suggest_extensions("نادر")
                → []                               # word not at the start of any shingle

        The method is safe to call with multi-word input; prefix length > 1
        will only match longer shingles (e.g. trigrams when prefix is a bigram).
        Results are sorted by corpus frequency (highest first).

        :param prefix_text: One or more space-separated Arabic words that the
            user has already typed.  All words are matched as a prefix against
            the ``aya_shingles`` term dictionary.
        :param limit: Maximum number of phrase completions to return (default 10).
        :returns: Ordered list of shingle strings that extend *prefix_text*,
            e.g. ``['الحمد لله', 'الحمد لله رب']`` for input ``'الحمد'``.
        """
        prefix_words = prefix_text.strip().split()
        if not prefix_words:
            return []
        n = len(prefix_words)

        for attempt in range(_MAX_READER_CLOSED_RETRIES):
            searcher = self._get_shared_searcher()
            reader = searcher.reader()
            try:
                if "aya_shingles" not in reader.indexed_field_names():
                    return []

                candidates: list = []

                for term_text in reader.field_terms("aya_shingles"):
                    parts = term_text.split()
                    # Must be strictly longer than the prefix (so it actually extends it)
                    # and must start with the exact prefix words.
                    if len(parts) <= n or parts[:n] != prefix_words:
                        continue
                    freq = reader.frequency("aya_shingles", term_text)
                    candidates.append((freq, term_text))

                candidates.sort(key=lambda x: x[0], reverse=True)
                return [phrase for _, phrase in candidates[:limit]]

            except ReaderClosed:
                if attempt == 0:
                    self._shared_searcher = None
                    logger.warning(
                        "suggest_extensions: Underlying index reader was closed "
                        "for prefix %r; retrying with a fresh searcher.",
                        prefix_text,
                    )
                    continue
                logger.error(
                    "suggest_extensions: Underlying index reader still closed on "
                    "retry for prefix %r; returning empty list.",
                    prefix_text,
                )
        return []

    def correct_query(self, querystr):
        """Return a corrected version of *querystr* using Whoosh's built-in
        query corrector.

        Whoosh's ``searcher.correct_query()`` analyses each term in the parsed
        query against the index vocabulary and replaces unknown terms with the
        closest known alternative.  It returns a :class:`whoosh.searching.Correction`
        object whose ``.string`` attribute contains the rewritten query string
        ready to pass back to the search engine.

        The shared Whoosh Searcher can be closed or refreshed by a concurrent
        request between the moment we obtain it and the moment Whoosh's
        ``correct_query`` accesses the underlying reader.  When that happens
        Whoosh raises :exc:`whoosh.reading.ReaderClosed`.  We retry once with a
        freshly obtained shared searcher and, if the error persists, fall back
        to returning the original query string unchanged so the caller always
        receives a well-formed response.

        @param querystr: The raw query string entered by the user.
        @return: Dictionary with keys ``original`` (the input) and
                 ``corrected`` (the best rewritten query string, identical to
                 the input when no correction is needed or when the index
                 reader is temporarily unavailable).
        """
        # Parse first: query plugins may call _get_shared_searcher() internally
        # (e.g. via engine._reader.reader → QSearcher.get_reader()).  By parsing
        # before we take our own reference to the shared searcher we ensure that
        # any index refresh triggered during parsing has already happened, so the
        # reference we obtain below belongs to the post-refresh searcher and is
        # less likely to be immediately stale.
        parsed = self._qparser.parse(querystr)
        for attempt in range(_MAX_READER_CLOSED_RETRIES):
            searcher = self._get_shared_searcher()
            try:
                correction = searcher.correct_query(parsed, querystr)
                return {"original": querystr, "corrected": correction.string}
            except ReaderClosed:
                if attempt == 0:
                    # Force _get_shared_searcher() to reopen on the next attempt.
                    self._shared_searcher = None
                    logger.warning(
                        "correct_query: Underlying index reader was closed during "
                        "correction for query %r; retrying with a fresh searcher.",
                        querystr,
                    )
                    continue
                # Second failure: fall back gracefully rather than propagating.
                logger.error(
                    "correct_query: Underlying index reader still closed on retry "
                    "for query %r; returning original query unchanged.",
                    querystr,
                )
        return {"original": querystr, "corrected": querystr}
