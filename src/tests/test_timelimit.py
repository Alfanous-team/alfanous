"""
Tests for the configurable timelimit feature across the search stack.
"""

import inspect
from unittest.mock import MagicMock, patch, call

from alfanous.searching import QSearcher
from alfanous.engines import BasicSearchEngine
from alfanous.outputs import Raw
import alfanous.api as api


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


def test_qsearcher_passes_timelimit_to_whoosh():
    """QSearcher.search must forward timelimit to whoosh's searcher.search()."""
    mock_results = _make_mock_results()

    mock_whoosh_searcher = MagicMock()
    mock_whoosh_searcher.search.return_value = mock_results

    mock_index = MagicMock()
    mock_index.get_index.return_value.searcher.return_value = mock_whoosh_searcher
    mock_index.get_schema.return_value = MagicMock()

    mock_parser = MagicMock()
    mock_parser.parse.return_value = MagicMock(all_terms=MagicMock(return_value=[]))

    searcher = QSearcher(mock_index, mock_parser)
    searcher.search("test query", timelimit=3.0)

    call_kwargs = mock_whoosh_searcher.search.call_args
    assert "timelimit" in call_kwargs.kwargs, "timelimit must be passed to whoosh searcher.search"
    assert call_kwargs.kwargs["timelimit"] == 3.0


def test_qsearcher_no_timelimit_kwarg_when_none():
    """When timelimit=None, QSearcher.search must NOT pass timelimit to whoosh."""
    mock_results = _make_mock_results()

    mock_whoosh_searcher = MagicMock()
    mock_whoosh_searcher.search.return_value = mock_results

    mock_index = MagicMock()
    mock_index.get_index.return_value.searcher.return_value = mock_whoosh_searcher
    mock_index.get_schema.return_value = MagicMock()

    mock_parser = MagicMock()
    mock_parser.parse.return_value = MagicMock(all_terms=MagicMock(return_value=[]))

    searcher = QSearcher(mock_index, mock_parser)
    searcher.search("test query", timelimit=None)

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
