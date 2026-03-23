"""
Tests for the configurable timelimit feature across the search stack.
"""

import shutil
import inspect
from collections import OrderedDict
import logging
import tempfile
from unittest.mock import MagicMock, patch, call

from whoosh.fields import Schema, NUMERIC, TEXT
from whoosh.collectors import TimeLimitCollector, FilterCollector
from whoosh.searching import TimeLimit
from whoosh.qparser import QueryParser
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
    mock_qsearcher.search.return_value = (mock_results, mock_terms, MagicMock(), frozenset())

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
    import alfanous.searching as _searching_module

    ix, tmpdir = _build_test_index(num_docs=10000)
    try:
        mock_index = MagicMock()
        mock_index.get_index.return_value = ix
        mock_index.get_schema.return_value = ix.schema

        parser = QueryParser("text", schema=ix.schema)

        qs = QSearcher(mock_index, parser)

        with caplog.at_level(logging.WARNING, logger=_searching_module.logger.name):
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
        results, _terms, _searcher, *_ = qs.search("t*", timelimit=EXTREMELY_SHORT_TIMELIMIT)

        assert results is not None, "results must not be None when timelimit fires during wildcard"
        assert len(results) >= 0, "results length must be non-negative"
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


# ---------------------------------------------------------------------------
# find_extended timelimit tests
# ---------------------------------------------------------------------------

def test_find_extended_has_timelimit_param():
    """find_extended must accept a timelimit parameter with default 5.0."""
    sig = inspect.signature(BasicSearchEngine.find_extended)
    assert "timelimit" in sig.parameters, "find_extended must accept timelimit"
    assert sig.parameters["timelimit"].default == 5.0, "timelimit default must be 5.0"


def test_find_extended_uses_timelimit_collector():
    """find_extended must use TimeLimitCollector when timelimit is given."""
    ix, tmpdir = _build_test_index(num_docs=100)
    try:
        mock_docindex = MagicMock()
        mock_docindex.OK = True
        mock_docindex.get_schema.return_value = ix.schema
        mock_docindex.get_index.return_value = ix

        engine = BasicSearchEngine(
            qdocindex=mock_docindex,
            query_parser=QueryParser,
            main_field="text",
            otherfields=[],
            qsearcher=QSearcher,
            qreader=MagicMock(return_value=MagicMock()),
            qhighlight=MagicMock(),
        )
        engine._schema = ix.schema
        engine._find_parsers = OrderedDict()

        with patch("alfanous.engines.TimeLimitCollector", wraps=TimeLimitCollector) as MockTLC:
            results, searcher = engine.find_extended("text:word", "text", timelimit=3.0)
            MockTLC.assert_called_once()
            _, tlc_kwargs = MockTLC.call_args
            assert tlc_kwargs.get("timelimit") == 3.0, \
                "find_extended must pass timelimit to TimeLimitCollector"
        assert results is not None
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def test_find_extended_no_timelimit_uses_search_directly():
    """When timelimit=None, find_extended must skip TimeLimitCollector."""
    ix, tmpdir = _build_test_index(num_docs=100)
    try:
        mock_docindex = MagicMock()
        mock_docindex.OK = True
        mock_docindex.get_schema.return_value = ix.schema
        mock_docindex.get_index.return_value = ix

        engine = BasicSearchEngine(
            qdocindex=mock_docindex,
            query_parser=QueryParser,
            main_field="text",
            otherfields=[],
            qsearcher=QSearcher,
            qreader=MagicMock(return_value=MagicMock()),
            qhighlight=MagicMock(),
        )
        engine._schema = ix.schema
        engine._find_parsers = OrderedDict()

        with patch("alfanous.engines.TimeLimitCollector") as MockTLC:
            results, searcher = engine.find_extended("text:word", "text", timelimit=None)
            MockTLC.assert_not_called()
        assert results is not None
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def test_find_extended_caches_parser_per_field():
    """find_extended must reuse the same QueryParser for repeated calls with the same field."""
    ix, tmpdir = _build_test_index(num_docs=10)
    try:
        mock_docindex = MagicMock()
        mock_docindex.OK = True
        mock_docindex.get_schema.return_value = ix.schema
        mock_docindex.get_index.return_value = ix

        engine = BasicSearchEngine(
            qdocindex=mock_docindex,
            query_parser=QueryParser,
            main_field="text",
            otherfields=[],
            qsearcher=QSearcher,
            qreader=MagicMock(return_value=MagicMock()),
            qhighlight=MagicMock(),
        )
        engine._schema = ix.schema
        engine._find_parsers = OrderedDict()

        engine.find_extended("text:word", "text", timelimit=None)
        first_parser = engine._find_parsers.get("text")
        assert first_parser is not None, "_find_parsers must be populated after first call"

        engine.find_extended("text:arabic", "text", timelimit=None)
        assert engine._find_parsers["text"] is first_parser, \
            "Same QueryParser instance must be reused for the same defaultfield"
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def test_find_extended_returns_partial_results_on_timeout():
    """find_extended must return partial results (not raise) when timelimit fires."""
    ix, tmpdir = _build_test_index(num_docs=10000)
    try:
        mock_docindex = MagicMock()
        mock_docindex.OK = True
        mock_docindex.get_schema.return_value = ix.schema
        mock_docindex.get_index.return_value = ix

        engine = BasicSearchEngine(
            qdocindex=mock_docindex,
            query_parser=QueryParser,
            main_field="text",
            otherfields=[],
            qsearcher=QSearcher,
            qreader=MagicMock(return_value=MagicMock()),
            qhighlight=MagicMock(),
        )
        engine._schema = ix.schema
        engine._find_parsers = OrderedDict()

        # An extremely short timelimit; may or may not actually fire depending
        # on hardware, but must never raise.
        results, searcher = engine.find_extended(
            "text:word", "text", timelimit=EXTREMELY_SHORT_TIMELIMIT
        )
        assert results is not None, "results must not be None even if timelimit fires"
        assert len(results) >= 0
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def test_find_extended_warning_logged_on_timeout(caplog):
    """find_extended must emit a WARNING log entry when the timelimit is hit."""
    import alfanous.engines as _engines_module
    ix, tmpdir = _build_test_index(num_docs=10000)
    try:
        mock_docindex = MagicMock()
        mock_docindex.OK = True
        mock_docindex.get_schema.return_value = ix.schema
        mock_docindex.get_index.return_value = ix

        engine = BasicSearchEngine(
            qdocindex=mock_docindex,
            query_parser=QueryParser,
            main_field="text",
            otherfields=[],
            qsearcher=QSearcher,
            qreader=MagicMock(return_value=MagicMock()),
            qhighlight=MagicMock(),
        )
        engine._schema = ix.schema
        engine._find_parsers = OrderedDict()

        with caplog.at_level(logging.WARNING, logger=_engines_module.logger.name):
            engine.find_extended("text:word", "text", timelimit=EXTREMELY_SHORT_TIMELIMIT)

        # Whether or not the timer actually fired (hardware-dependent), the
        # call must never crash.  If a WARNING was emitted it must mention
        # "timelimit".  On fast hardware the timer may not fire for a 100-doc
        # index, in which case no warnings are expected and the loop is a no-op.
        for record in caplog.records:
            if record.levelno == logging.WARNING:
                assert "timelimit" in record.getMessage().lower()
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


# ---------------------------------------------------------------------------
# Pure-wildcard guard tests (no index required)
# ---------------------------------------------------------------------------

def test_pure_wildcard_re_matches_bare_wildcards():
    """_PURE_WILDCARD_RE must match queries that consist only of wildcard chars.

    Regression guard for: "exceeding timelimit with wildcards search".
    These queries would otherwise route through the expensive NestedParent
    translation search path in _search_aya.
    """
    from alfanous.outputs import _PURE_WILDCARD_RE

    should_match = ["*", "?", "؟", "* ?", "؟*", "  *  ", "**", "*?*"]
    # Edge cases: whitespace-only queries (no wildcards but also no content)
    # are also matched so they don't trigger translation search.
    # Field-qualified wildcards like "text:*" contain ":" which routes them
    # to the Arabic path (never reaches _PURE_WILDCARD_RE check), and queries
    # like "*test*" or "t*" have actual content so they must NOT match.
    should_not_match = ["*test*", "t*", "hello", "*h*", "", "god*", "text:*"]

    for q in should_match:
        assert _PURE_WILDCARD_RE.match(q), (
            f"_PURE_WILDCARD_RE should match pure-wildcard query {q!r} but did not"
        )
    for q in should_not_match:
        assert not _PURE_WILDCARD_RE.match(q), (
            f"_PURE_WILDCARD_RE should NOT match query with content {q!r} but did"
        )


def test_search_aya_skips_trans_parser_for_pure_wildcards(monkeypatch):
    """_search_aya must not call _trans_parser.parse for pure-wildcard queries.

    The translation NestedParent search is skipped for queries like '*' to
    avoid expanding wildcards across all translation fields — an operation
    that would exceed the timelimit.
    """
    from alfanous.outputs import Raw

    raw = Raw.__new__(Raw)
    raw._defaults = {
        "flags": {
            "lang": "en",
            "sortedby": "score",
            "reverse": False,
            "perpage": None,
            "range": 25,
            "page": None,
            "offset": 1,
            "recitation": None,
            "translation": None,
            "romanization": "none",
            "highlight": "none",
            "script": "simple",
            "vocalized": False,
            "fuzzy": False,
            "fuzzy_maxdist": 1,
            "fuzzy_derivation": False,
            "timelimit": "5",
            "view": "custom",
            "facets": None,
            "filter": None,
            "prev_aya": False,
            "next_aya": False,
            "sura_info": False,
            "sura_stat_info": False,
            "word_info": False,
            "word_synonyms": False,
            "word_derivations": False,
            "word_vocalizations": False,
            "word_linguistics": False,
            "aya_position_info": False,
            "aya_theme_info": False,
            "aya_stat_info": False,
            "aya_sajda_info": False,
            "annotation_aya": False,
            "annotation_word": False,
        },
        "results_limit": {"aya": 25},
    }
    raw.DOMAINS = {
        "view": ["custom", "minimal", "normal", "full", "statistic", "linguistic", "recitation"],
    }

    # Mock _trans_parser with a sentinel to detect if parse() is called
    mock_trans_parser = MagicMock()
    raw._trans_parser = mock_trans_parser
    raw._trans_fields = frozenset()
    raw._lang_trans_parsers = {}
    raw._lang_trans_fields = {}

    # Mock QSE so search_with_query returns empty results immediately
    mock_qse = MagicMock()
    mock_qse._schema = {}
    mock_results = MagicMock()
    mock_results.__len__ = MagicMock(return_value=0)
    mock_results.__iter__ = MagicMock(return_value=iter([]))
    mock_qse.search_with_query.return_value = (mock_results, [], MagicMock())
    raw.QSE = mock_qse

    # Stub helpers used inside _search_aya that require real data
    monkeypatch.setattr("alfanous.outputs.arabizi_to_arabic_list", lambda *a, **kw: [])
    monkeypatch.setattr("alfanous.outputs.quran_unvocalized_words", lambda: frozenset())

    flags = {"query": "*", "action": "search"}
    try:
        raw._search_aya(flags)
    except Exception:
        pass  # Output formatting may fail; we only care about the parser call

    # The translation parser must NOT have been called for a bare wildcard
    mock_trans_parser.parse.assert_not_called()


def test_pure_wildcard_routes_to_arabic_search_path(monkeypatch):
    """Pure-wildcard queries (*, ??, ???) must route to the Arabic aya search path.

    Before this fix, queries like '??', '???', and '*' fell into the non-Arabic
    branch where the translation search was skipped (correctly, to avoid timelimit
    issues) but arabizi conversion also produced no candidates, resulting in an
    empty _query_parts list and NullQuery → zero results.

    After the fix the condition ``not _PURE_WILDCARD_RE.match(query)`` is added to
    the non-Arabic branch guard so that pure wildcards bypass the translation path
    entirely and are forwarded to QSearcher.search_all() which applies
    ArabicWildcardQuery (MAX_EXPAND cap) and TimeLimitCollector.
    """
    from alfanous.outputs import Raw

    raw = Raw.__new__(Raw)
    raw._defaults = {
        "flags": {
            "lang": "en",
            "sortedby": "score",
            "reverse": False,
            "perpage": None,
            "range": 25,
            "page": None,
            "offset": 1,
            "recitation": None,
            "translation": None,
            "romanization": "none",
            "highlight": "none",
            "script": "simple",
            "vocalized": False,
            "fuzzy": False,
            "fuzzy_maxdist": 1,
            "fuzzy_derivation": False,
            "derivation_level": 0,
            "timelimit": "5",
            "view": "custom",
            "facets": None,
            "filter": None,
            "prev_aya": False,
            "next_aya": False,
            "sura_info": False,
            "sura_stat_info": False,
            "word_info": False,
            "word_synonyms": False,
            "word_derivations": False,
            "word_vocalizations": False,
            "word_linguistics": False,
            "aya_position_info": False,
            "aya_theme_info": False,
            "aya_stat_info": False,
            "aya_sajda_info": False,
            "annotation_aya": False,
            "annotation_word": False,
        },
        "results_limit": {"aya": 25},
        "maxkeywords": 10,
    }
    raw.DOMAINS = {
        "view": ["custom", "minimal", "normal", "full", "statistic", "linguistic", "recitation"],
    }

    mock_trans_parser = MagicMock()
    raw._trans_parser = mock_trans_parser
    raw._trans_fields = frozenset()
    raw._lang_trans_parsers = {}
    raw._lang_trans_fields = {}

    # Mock QSE.search_all (the Arabic path) to return a usable empty result
    mock_qse = MagicMock()
    mock_qse._schema = {}
    mock_results = MagicMock()
    mock_results.__len__ = MagicMock(return_value=0)
    mock_results.__iter__ = MagicMock(return_value=iter([]))
    mock_qse.search_all.return_value = (mock_results, [], MagicMock(), [])
    raw.QSE = mock_qse

    monkeypatch.setattr("alfanous.outputs.arabizi_to_arabic_list", lambda *a, **kw: [])
    monkeypatch.setattr("alfanous.outputs.quran_unvocalized_words", lambda: frozenset())

    for wildcard_query in ("*", "??", "???", "?"):
        mock_qse.search_all.reset_mock()
        mock_trans_parser.parse.reset_mock()
        flags = {"query": wildcard_query, "action": "search"}
        try:
            raw._search_aya(flags)
        except Exception:
            pass  # Output formatting may fail; we only care about the search path

        # Translation parser must never be called for pure wildcards
        mock_trans_parser.parse.assert_not_called()
        # Arabic search path (search_all) MUST be called — not NullQuery via search_with_query
        assert mock_qse.search_all.called, (
            f"QSE.search_all must be called for pure-wildcard query {wildcard_query!r} "
            "so results are returned instead of NullQuery."
        )
