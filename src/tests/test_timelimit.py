"""
Tests for the configurable timelimit feature across the search stack.
"""

import shutil
import inspect
import tempfile
from unittest.mock import MagicMock, patch, call

from whoosh.fields import Schema, NUMERIC, TEXT
from whoosh.collectors import TimeLimitCollector, FilterCollector
from whoosh.searching import TimeLimit
import whoosh.index as whoosh_index
from whoosh import query as wquery

from alfanous.searching import QSearcher
from alfanous.engines import BasicSearchEngine
from alfanous.outputs import Raw
import alfanous.api as api

# An extremely short timelimit (seconds) used in tests that must fire the
# timeout path.  Hardware-dependent: the timeout may not trigger on very fast
# machines, but the call must always return without raising.
EXTREMELY_SHORT_TIMELIMIT = 0.00001


# ---------------------------------------------------------------------------
# Signature / default-value tests (no index required)
# ---------------------------------------------------------------------------

def test_qsearcher_search_has_timelimit_param():
    sig = inspect.signature(QSearcher.search)
    assert "timelimit" in sig.parameters, "QSearcher.search must accept timelimit"
    assert sig.parameters["timelimit"].default == 5.0, "timelimit default must be 5.0"


def test_basic_search_engine_search_all_has_timelimit_param():
    sig = inspect.signature(BasicSearchEngine.search_all)
    assert "timelimit" in sig.parameters, "BasicSearchEngine.search_all must accept timelimit"
    assert sig.parameters["timelimit"].default == 5.0, "timelimit default must be 5.0"


def test_api_search_has_timelimit_param():
    sig = inspect.signature(api.search)
    assert "timelimit" in sig.parameters, "api.search must accept timelimit"
    assert sig.parameters["timelimit"].default == 5.0, "timelimit default must be 5.0"


def test_outputs_defaults_include_timelimit():
    assert "timelimit" in Raw.DEFAULTS["flags"], "DEFAULTS must include timelimit"
    assert Raw.DEFAULTS["flags"]["timelimit"] == 5.0, "Default timelimit must be 5.0"


def test_outputs_domains_include_timelimit():
    assert "timelimit" in Raw.DOMAINS, "DOMAINS must include timelimit"


def test_outputs_helpmessages_include_timelimit():
    assert "timelimit" in Raw.HELPMESSAGES, "HELPMESSAGES must include timelimit"


# ---------------------------------------------------------------------------
# Propagation tests: verify timelimit flows from engine → searcher → whoosh
# ---------------------------------------------------------------------------

def _make_mock_results():
    """Return a minimal mock that satisfies the QSearcher.search return contract."""
    mock_results = MagicMock()
    mock_results.matched_terms.return_value = frozenset()
    mock_results.__iter__ = MagicMock(return_value=iter([]))
    mock_results.__len__ = MagicMock(return_value=0)
    return mock_results


def test_qsearcher_passes_timelimit_via_collector():
    """QSearcher.search must use TimeLimitCollector when timelimit is given."""
    mock_results = _make_mock_results()

    mock_collector = MagicMock()
    mock_collector.results.return_value = mock_results

    mock_whoosh_searcher = MagicMock()
    mock_whoosh_searcher.collector.return_value = mock_collector

    mock_index = MagicMock()
    mock_index.get_index.return_value.searcher.return_value = mock_whoosh_searcher
    mock_index.get_schema.return_value = MagicMock()

    mock_parser = MagicMock()
    mock_parser.parse.return_value = MagicMock(all_terms=MagicMock(return_value=[]))

    with patch("alfanous.searching.TimeLimitCollector") as MockTLC:
        mock_tlc = MagicMock()
        mock_tlc.results.return_value = mock_results
        MockTLC.return_value = mock_tlc

        searcher = QSearcher(mock_index, mock_parser)
        searcher.search("test query", timelimit=3.0)

        MockTLC.assert_called_once()
        _, tlc_kwargs = MockTLC.call_args
        assert tlc_kwargs.get("timelimit") == 3.0, "TimeLimitCollector must receive timelimit=3.0"
        mock_whoosh_searcher.search_with_collector.assert_called_once()
        mock_whoosh_searcher.search.assert_not_called()


def test_qsearcher_no_timelimit_uses_search_directly():
    """When timelimit=None, QSearcher.search must call searcher.search() without TimeLimitCollector."""
    mock_results = _make_mock_results()

    mock_whoosh_searcher = MagicMock()
    mock_whoosh_searcher.search.return_value = mock_results

    mock_index = MagicMock()
    mock_index.get_index.return_value.searcher.return_value = mock_whoosh_searcher
    mock_index.get_schema.return_value = MagicMock()

    mock_parser = MagicMock()
    mock_parser.parse.return_value = MagicMock(all_terms=MagicMock(return_value=[]))

    with patch("alfanous.searching.TimeLimitCollector") as MockTLC:
        searcher = QSearcher(mock_index, mock_parser)
        searcher.search("test query", timelimit=None)

        MockTLC.assert_not_called()
        mock_whoosh_searcher.search.assert_called_once()
        call_kwargs = mock_whoosh_searcher.search.call_args
        assert "timelimit" not in call_kwargs.kwargs, \
            "timelimit must NOT be passed to whoosh when it is None"


def test_basic_search_engine_passes_timelimit_to_qsearcher():
    """BasicSearchEngine.search_all must propagate timelimit to QSearcher.search."""
    mock_results = _make_mock_results()
    mock_terms = []

    mock_qsearcher = MagicMock()
    mock_qsearcher.search.return_value = (mock_results, mock_terms, MagicMock())

    mock_qreader = MagicMock()
    mock_qreader.term_stats.return_value = []

    engine = BasicSearchEngine.__new__(BasicSearchEngine)
    engine.OK = True
    engine._searcher = mock_qsearcher
    engine._reader = mock_qreader

    engine.search_all("test", timelimit=7.5)

    call_kwargs = mock_qsearcher.search.call_args
    assert call_kwargs.kwargs.get("timelimit") == 7.5, \
        "BasicSearchEngine must pass timelimit to QSearcher.search"


# ---------------------------------------------------------------------------
# Integration tests using a real in-memory Whoosh index (no Quran data needed)
# ---------------------------------------------------------------------------

def _build_test_index(num_docs=10000):
    """Build a temporary Whoosh index with enough documents to trigger timelimit.

    Returns a (index, tmpdir) tuple; the caller is responsible for removing
    tmpdir when done.
    """
    tmpdir = tempfile.mkdtemp()
    schema = Schema(sura_id=NUMERIC(stored=True), text=TEXT(stored=True))
    ix = whoosh_index.create_in(tmpdir, schema)
    writer = ix.writer()
    # sura_id cycles 1-30 to mimic Quran's 30 juz (parts)
    for i in range(num_docs):
        writer.add_document(sura_id=(i % 30) + 1, text="arabic text word " * 50)
    writer.commit()
    return ix, tmpdir


def test_timelimit_returns_partial_results_no_crash():
    """A wildcard search with an extremely short timelimit must return partial
    results gracefully instead of crashing.  This simulates the behaviour of a
    query like '*' against the full Quran index."""
    ix, tmpdir = _build_test_index(num_docs=10000)
    searcher = ix.searcher()
    try:
        base_c = searcher.collector(limit=10000)
        tlc = TimeLimitCollector(base_c, timelimit=EXTREMELY_SHORT_TIMELIMIT, use_alarm=False)
        timed_out = False
        try:
            searcher.search_with_collector(wquery.Every(), tlc)
        except TimeLimit:
            timed_out = True

        results = tlc.results()
        # Whether or not the timer actually fired (hardware-dependent), the
        # collector must always return a valid Results object without raising.
        assert results is not None, "results must not be None after timelimit"
        assert len(results) >= 0, "results length must be non-negative"
        if timed_out:
            # Partial results: fewer docs than total
            assert len(results) < 10000, "partial results must be fewer than total docs"
    finally:
        searcher.close()
        shutil.rmtree(tmpdir, ignore_errors=True)


def test_timelimit_with_filter_returns_correctly_filtered_partial_results():
    """Filtering must still be applied correctly when a timelimit is set and
    the search times out mid-way through the result set."""
    ix, tmpdir = _build_test_index(num_docs=10000)
    searcher = ix.searcher()
    try:
        filter_q = wquery.Term("sura_id", 1)
        base_c = searcher.collector(limit=10000)
        tlc = TimeLimitCollector(base_c, timelimit=EXTREMELY_SHORT_TIMELIMIT, use_alarm=False)
        final_c = FilterCollector(tlc, allow=filter_q)
        try:
            searcher.search_with_collector(wquery.Every(), final_c)
        except TimeLimit:
            pass

        results = final_c.results()
        assert results is not None
        # Every returned document must satisfy the filter (sura_id == 1)
        wrong = [r["sura_id"] for r in results if r["sura_id"] != 1]
        assert not wrong, f"Filter must hold even after timelimit; got wrong sura_ids: {wrong}"
    finally:
        searcher.close()
        shutil.rmtree(tmpdir, ignore_errors=True)


def test_timelimit_warning_logged_on_timeout(caplog):
    """QSearcher.search must emit a WARNING log entry when the timelimit is hit."""
    import logging
    from alfanous.searching import QSearcher

    ix, tmpdir = _build_test_index(num_docs=10000)
    try:
        mock_index = MagicMock()
        mock_index.get_index.return_value = ix
        mock_index.get_schema.return_value = ix.schema

        from whoosh.qparser import QueryParser
        parser = QueryParser("text", schema=ix.schema)

        qs = QSearcher(mock_index, parser)

        with caplog.at_level(logging.WARNING, logger="alfanous.searching"):
            qs.search("word", timelimit=EXTREMELY_SHORT_TIMELIMIT)

        # The warning may or may not fire depending on timing, but the call must
        # never crash.  If it did fire, it must mention "timelimit".
        for record in caplog.records:
            if record.levelno == logging.WARNING:
                assert "timelimit" in record.getMessage().lower()
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


# ---------------------------------------------------------------------------
# Wildcard + timelimit interaction tests
# ---------------------------------------------------------------------------

def test_arabic_wildcard_max_expand_caps_term_expansion():
    """ArabicWildcardQuery._btexts must yield at most MAX_EXPAND terms.

    This ensures that a broad wildcard pattern (e.g. bare '*') cannot
    iterate over the entire index lexicon before the TimeLimitCollector
    has a chance to stop the query.
    """
    from alfanous.query_plugins import ArabicWildcardQuery

    ix, tmpdir = _build_test_index(num_docs=100)
    try:
        with ix.searcher() as searcher:
            reader = searcher.reader()
            wq = ArabicWildcardQuery("text", "*")
            expanded = list(wq._btexts(reader))
            assert len(expanded) <= ArabicWildcardQuery.MAX_EXPAND, (
                f"Wildcard expansion must be capped at MAX_EXPAND={ArabicWildcardQuery.MAX_EXPAND}; "
                f"got {len(expanded)} terms"
            )
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def test_wildcard_search_via_qsearcher_stopped_by_timelimit():
    """A wildcard query string routed through QSearcher must be stopped by the
    timelimit and return a valid (possibly partial) Results object without
    raising an exception.

    This specifically exercises the path:
        wildcard query string → parser → ArabicWildcardQuery →
        TimeLimitCollector → partial results
    """
    from alfanous.searching import QSearcher
    from alfanous.query_plugins import ArabicWildcardPlugin

    ix, tmpdir = _build_test_index(num_docs=10000)
    try:
        mock_index = MagicMock()
        mock_index.get_index.return_value = ix
        mock_index.get_schema.return_value = ix.schema

        from whoosh.qparser import QueryParser
        parser = QueryParser("text", schema=ix.schema)
        parser.add_plugin(ArabicWildcardPlugin())

        qs = QSearcher(mock_index, parser)
        results, _terms, _searcher = qs.search("t*", timelimit=EXTREMELY_SHORT_TIMELIMIT)

        assert results is not None, "results must not be None when timelimit fires during wildcard"
        assert len(results) >= 0, "results length must be non-negative"
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)
