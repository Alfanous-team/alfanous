import logging

from whoosh import qparser
from whoosh.qparser import QueryParser
from whoosh.collectors import TimeLimitCollector
from whoosh.searching import TimeLimit

from alfanous.searching import QSearcher, QReader, _SearcherProxy
from alfanous.indexing import QseDocIndex, BasicDocIndex
from alfanous.results_processing import Qhighlight, QTranslationHighlight
from alfanous.query_processing import QuranicParser, StandardParser
from alfanous.constants import QURAN_TOTAL_VERSES

logger = logging.getLogger(__name__)

class BasicSearchEngine:
    def __init__(self, qdocindex, query_parser, main_field, otherfields, qsearcher, qreader, qhighlight, default_filter=None):

        self.OK = False
        self._default_filter = default_filter or {}
        if qdocindex.OK:
            self._docindex = qdocindex
            #
            self._schema = self._docindex.get_schema()
            #
            # Try to instantiate parser with otherfields (for custom parsers like QuranicParser)
            # Fall back to standard Whoosh QueryParser signature if that fails
            try:
                self._parser = query_parser(schema=self._schema, mainfield=main_field, otherfields=otherfields)
            except TypeError:
                self._parser = query_parser(main_field, self._schema, group=qparser.OrGroup)
            
            # Note: Plugins are added in the parser's own __init__ method
            # (see ArabicParser and its subclasses in query_processing.py)
            
            self._searcher = qsearcher(self._docindex, self._parser)
            #
            self._reader = qreader(self._docindex)
            # Share the IndexReader already held by the searcher's cached
            # Whoosh Searcher so the engine keeps only one IndexReader open.
            self._reader.attach_to_searcher(self._searcher)
            #
            self._highlight = qhighlight
            # Per-field QueryParser cache used by find_extended.  Parsers are
            # stateless once created (they depend only on the field name and the
            # fixed index schema), so caching them avoids repeated allocations.
            self._find_parsers = {}
            self.OK = True

    # end  __init__

    def search_all(self, querystr, limit=QURAN_TOTAL_VERSES, sortedby="score", reverse=False, facets=None, filter_dict=None, fuzzy=False, fuzzy_maxdist=1, timelimit=5.0):
        """
        Perform a search in the index.
        
        @param querystr: The search query string
        @param limit: Maximum number of results to return
        @param sortedby: Field to sort results by
        @param reverse: Whether to reverse the sort order
        @param facets: Facets to group results by
        @param filter_dict: Filters to apply to the search (merged with any
               default_filter configured on this engine)
        @param fuzzy: When True, also search the normalised/stemmed 'aya' field
               and apply Levenshtein distance matching on 'aya_ac'
        @param fuzzy_maxdist: Maximum Levenshtein edit distance for fuzzy term
               matching (default 1). Only used when fuzzy=True.
        @param timelimit: Maximum number of seconds to spend on the search
               (default 5.0). Pass None to disable the limit.
        @return: Tuple of (results, term_stats, searcher)
        """
        # Merge the engine-level default filter (e.g. kind="aya") with any
        # caller-supplied filter.  Caller values take precedence.
        # Use getattr so tests that bypass __init__ via __new__ still work.
        _default = getattr(self, '_default_filter', None)
        if _default:
            merged = {**_default, **(filter_dict or {})}
        else:
            merged = filter_dict
        results, terms, searcher = self._searcher.search(querystr, limit=limit, sortedby=sortedby, reverse=reverse, facets=facets, filter_dict=merged, fuzzy=fuzzy, fuzzy_maxdist=fuzzy_maxdist, timelimit=timelimit)
        return results, list(self._reader.term_stats(terms)), searcher

    def search_with_query(self, q_obj, limit=QURAN_TOTAL_VERSES, sortedby="score", reverse=False, timelimit=5.0):
        """Run a pre-built Whoosh query object (e.g. NestedParent/NestedChildren).

        Useful when the query cannot be expressed as a plain string, for example
        cross-field nested document queries.  Returns the same
        ``(results, term_stats, searcher)`` tuple as :meth:`search_all`.
        """
        results, terms, searcher = self._searcher.search_obj(q_obj, limit=limit, sortedby=sortedby, reverse=reverse, timelimit=timelimit)
        return results, [], searcher

    def shared_searcher(self):
        """Return the engine's cached Whoosh Searcher wrapped in a non-closing proxy.

        All attribute access on the returned object is delegated to the shared
        Whoosh Searcher managed by the internal :class:`~alfanous.searching.QSearcher`;
        ``close()`` and ``__exit__()`` are no-ops so the underlying shared
        searcher is not destroyed when the caller is done.

        Typical usage::

            searcher = engine.shared_searcher()
            for item in items:
                results = engine.search_with_shared_searcher(searcher, query)
                ...
            # searcher.close() is safe but has no effect

        :returns: A :class:`~alfanous.searching._SearcherProxy` wrapping the
            engine's single cached Whoosh Searcher.
        """
        return _SearcherProxy(self._searcher._get_shared_searcher())

    def search_with_shared_searcher(self, whoosh_searcher, q_obj, limit=QURAN_TOTAL_VERSES):
        """Run a pre-built query against a pre-opened shared Whoosh searcher.

        Use :meth:`shared_searcher` to obtain *whoosh_searcher* and close it
        when finished.  This method does **not** open or close the searcher,
        so it can be called many times inside a loop without per-call segment
        overhead.

        :param whoosh_searcher: An open Whoosh Searcher from :meth:`shared_searcher`.
        :param q_obj: A pre-built Whoosh query object.
        :param limit: Maximum number of results to return.
        :returns: A Whoosh ``Results`` object.
        """
        return whoosh_searcher.search(q=q_obj, limit=limit)

    def most_frequent_words(self, nb, fieldname):
        """
        Get the most frequent words in a field.
        
        @param nb: Number of words to return
        @param fieldname: Field to search in
        @return: List of (frequency, word) tuples
        """
        return [
            (x[0], x[1].decode('utf-8') if isinstance(x[1], bytes) else x[1])
            for x in self._reader.reader.most_frequent_terms(fieldname, nb)
        ]

    def suggest_all(self, querystr):
        """
        Get search suggestions for a query.
        
        @param querystr: The query string to get suggestions for
        @return: List of suggested queries
        """
        return self._searcher.suggest(querystr)

    def suggest_collocations(self, word, limit=5, stopwords=None, trigram_min_count=2):
        """Find n-grams (bigrams and trigrams) centred on *word* in the same verse.

        Delegates to :meth:`~alfanous.searching.QSearcher.suggest_collocations`.

        :param word: A single unvocalized Arabic word to find collocations for.
        :param limit: Maximum number of phrases to return (default 5).
        :param stopwords: Words to exclude from bigram neighbours.
        :param trigram_min_count: Minimum count for a trigram to be included
            (default 2 — only trigrams that appear at least twice are returned).
        :returns: List of adjacency-based 2- or 3-word phrase strings.
        """
        return self._searcher.suggest_collocations(
            word, limit=limit, stopwords=stopwords, trigram_min_count=trigram_min_count
        )

    def suggest_extensions(self, prefix_text, limit=10):
        """Find shingles that extend a typed prefix.

        Delegates to :meth:`~alfanous.searching.QSearcher.suggest_extensions`.

        Returns only shingles whose first words exactly match *prefix_text*,
        making this the right function for autocomplete (the user's typed text
        is kept intact and the suggestions are longer completions).

        :param prefix_text: One or more space-separated Arabic words already typed.
        :param limit: Maximum number of completions to return (default 10).
        :returns: Ordered list of phrase strings extending *prefix_text*.
        """
        return self._searcher.suggest_extensions(prefix_text, limit=limit)

    def correct_query(self, querystr):
        """
        Return a corrected version of *querystr* using Whoosh's query corrector.

        @param querystr: The raw query string to correct.
        @return: Dictionary with 'original' and 'corrected' keys.
        """
        return self._searcher.correct_query(querystr)

    def autocomplete(self, querystr):
        """Get autocomplete suggestions that extend what the user has typed.

        Uses the full *querystr* as a prefix and returns shingles from the
        ``aya_shingles`` field whose first words exactly match that prefix.
        This gives consistent, "extend what was typed" behaviour for both
        single-word and multi-word input:

        * ``autocomplete("الحمد")``
          → ``["الحمد لله", "الحمد لله رب"]``
          *(bigrams and trigrams that start with الحمد)*

        * ``autocomplete("الحمد لله")``
          → ``["الحمد لله رب"]``
          *(trigrams that start with the full bigram)*

        * ``autocomplete("رسول")``
          → ``["رسول الله", "رسول الله الكريم"]``
          *(only phrases where رسول is the first word — not "محمد رسول")*

        When no shingle extends the typed text (rare word or index predates
        ``aya_shingles``), the method falls back to prefix-based single-word
        completion from the ``aya_ac`` field.

        @param querystr: The Arabic text the user has typed (one or more words).
        @return: Dict with:
            - ``'base'``: all words except the last, joined with a space
              (unchanged prefix already committed).
            - ``'completion'``: ordered list of phrase completions (at most 10),
              sorted by Quranic corpus frequency.
        """
        words = querystr.split()
        if not words:
            return {"base": "", "completion": []}
        base = " ".join(words[:-1])
        completion = self.suggest_extensions(querystr.strip(), limit=10)
        if not completion:
            # No shingle extends this prefix — fall back to single-word prefix
            # expansion on aya_ac (handles rare/unknown words gracefully).
            completion = self._reader.autocomplete(words[-1])[:10]
        return {
            "base": base,
            "completion": completion,
        }

    def highlight(self, text, terms, highlight_type="css", strip_vocalization=True):
        """
        Highlight search terms in text.
        
        @param text: The text to highlight
        @param terms: The terms to highlight
        @param highlight_type: Type of highlighting ('css', 'bold', etc.)
        @param strip_vocalization: Whether to strip vocalization marks
        @return: Highlighted text
        """
        return self._highlight(text, terms, highlight_type, strip_vocalization)

    def find_extended(self, query, defaultfield, timelimit=5.0):
        """Search the index using a query string and return ``(results, searcher)``.

        ``searcher.close()`` on the returned proxy is a no-op; callers may call
        it safely without destroying the underlying shared searcher.

        :param query: Whoosh query string (parsed with *defaultfield* as the
            default field).
        :param defaultfield: Default field name used by the internal QueryParser.
        :param timelimit: Maximum seconds to spend on the query (default 5.0).
            Pass ``None`` to disable.  When the limit is exceeded, a WARNING is
            logged and partial results are returned rather than raising an
            exception.
        """
        # Get the underlying shared Whoosh Searcher directly so we can pass it
        # to search_with_collector — the _SearcherProxy wrapper does not expose
        # that method.
        whoosh_searcher = self._searcher._get_shared_searcher()

        # Lazily cache one QueryParser per defaultfield so we do not allocate
        # a new parser object on every call.
        if defaultfield not in self._find_parsers:
            self._find_parsers[defaultfield] = QueryParser(defaultfield, schema=self._schema)
        q = self._find_parsers[defaultfield].parse(query)

        if timelimit is not None:
            c = whoosh_searcher.collector(limit=QURAN_TOTAL_VERSES)
            tlc = TimeLimitCollector(c, timelimit=timelimit, use_alarm=False)
            try:
                whoosh_searcher.search_with_collector(q, tlc)
            except TimeLimit:
                logger.warning(
                    "find_extended timelimit of %s seconds reached; returning partial results",
                    timelimit,
                )
            results = tlc.results()
        else:
            results = whoosh_searcher.search(q, limit=QURAN_TOTAL_VERSES)

        return results, _SearcherProxy(whoosh_searcher)

    def get_shared_reader(self):
        """Return the IndexReader from the engine's current shared Whoosh Searcher.

        Unlike ``searcher.reader()`` on a cached :class:`~alfanous.searching._SearcherProxy`,
        this method always resolves through :meth:`~alfanous.searching.QSearcher.get_reader`
        which calls ``_get_shared_searcher()`` internally.  Any pending index
        refresh is therefore applied *before* the reader is returned, guaranteeing
        that the caller receives a reader that belongs to the *current* (open)
        shared searcher rather than a potentially stale one that may have been
        closed by a concurrent refresh.

        Callers should not cache the returned reader across multiple requests.
        """
        return self._searcher.get_reader()

    def list_values(self, fieldname):
        """ list all stored values of a field  """
        if "_reader" in self.__dict__:
            return self._reader.list_values(fieldname )
        else:
            return []

    def list_stored_values(self, fieldname):
        """ List all unique stored (non-tokenized) values of a field, preserving full phrases. """
        if "_reader" in self.__dict__:
            return self._reader.list_stored_values(fieldname)
        else:
            return []

    def close(self):
        """Close the searcher and reader, releasing all held Whoosh index resources.

        After this call the engine is no longer usable.  Any in-flight
        :class:`~alfanous.searching._SearcherProxy` instances obtained via
        :meth:`shared_searcher` will also stop working because they reference
        the now-closed underlying Whoosh Searcher.

        :meth:`close` is idempotent: calling it multiple times is safe.
        """
        if hasattr(self, '_searcher'):
            self._searcher.close()
        if hasattr(self, '_reader'):
            self._reader.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __call__(self):
        """
        Check if the search engine is properly initialized.
        
        @return: True if OK, False otherwise
        """
        return self.OK


def QuranicSearchEngine(indexpath="../indexes/main/",
                        qparser=QuranicParser):
    return BasicSearchEngine(qdocindex=QseDocIndex(indexpath)
                             , query_parser=qparser
                             , main_field="aya"
                             , otherfields=[]
                             , qsearcher=QSearcher
                             , qreader=QReader
                             , qhighlight=Qhighlight
                             , default_filter={"kind": "aya"}
                             )


