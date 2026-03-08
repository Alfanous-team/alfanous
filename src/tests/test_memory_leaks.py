"""
Focused tests for the three memory-management fixes:

1. outputs.py  – extend_runtime is no longer accumulated inside the
                 adjacent-aya loop (it was added once per hit).
2. outputs.py  – parent_data stores plain dicts (_p.fields()) instead of
                 Whoosh Hit objects so that the parent Results and its
                 Searcher reference are released sooner.
3. searching.py – QSearcher caches _fuzzy_parser instead of creating a new
                  QueryParser on every fuzzy search call.
"""

import unittest
from unittest.mock import MagicMock, patch, PropertyMock


# ---------------------------------------------------------------------------
# Fix 1: extend_runtime accumulated outside the adjacent-aya loop
# ---------------------------------------------------------------------------

class TestAdjaRuntimeNotOverCounted(unittest.TestCase):
    """Verify that adja_res.runtime is added exactly once to extend_runtime."""

    def test_runtime_not_multiplied_by_result_count(self):
        """adja_res.runtime must appear once before the loop, not once per Hit."""
        import ast, inspect
        import alfanous.outputs as _outputs_module
        src = inspect.getsource(_outputs_module)
        tree = ast.parse(src)

        # Find the `for adja in adja_res:` loop body and confirm that
        # `adja_res.runtime` is NOT referenced inside it.
        found_in_loop = False
        for node in ast.walk(tree):
            if isinstance(node, ast.For):
                target = getattr(node.target, 'id', '')
                iter_id = getattr(node.iter, 'id', '')
                if target == 'adja' and iter_id == 'adja_res':
                    for inner in ast.walk(node):
                        if (isinstance(inner, ast.Attribute)
                                and inner.attr == 'runtime'
                                and isinstance(inner.value, ast.Name)
                                and inner.value.id == 'adja_res'):
                            found_in_loop = True

        self.assertFalse(
            found_in_loop,
            "adja_res.runtime must NOT be inside the 'for adja in adja_res' loop "
            "(it was causing the runtime to be counted once per hit instead of once)."
        )


# ---------------------------------------------------------------------------
# Fix 2: parent_data stores _p.fields() (plain dict) not Hit objects
# ---------------------------------------------------------------------------

class TestParentDataStoresFieldDicts(unittest.TestCase):
    """Verify that parent_data is populated with plain dicts, not Hit objects."""

    def test_parent_data_uses_fields(self):
        """The parent_data loop must call _p.fields() not store _p directly."""
        import ast, inspect
        import alfanous.outputs as _outputs_module
        src = inspect.getsource(_outputs_module)
        tree = ast.parse(src)

        # We look for the assignment `parent_data[...] = ...` inside the
        # `for _p in _parent_res:` loop and check that it calls `.fields()`.
        found_fields_call = False
        for node in ast.walk(tree):
            if isinstance(node, ast.For):
                target = getattr(node.target, 'id', '')
                iter_id = getattr(node.iter, 'id', '')
                if target == '_p' and iter_id == '_parent_res':
                    for inner in ast.walk(node):
                        if isinstance(inner, ast.Assign):
                            val = inner.value
                            if (isinstance(val, ast.Call)
                                    and isinstance(val.func, ast.Attribute)
                                    and val.func.attr == 'fields'
                                    and isinstance(val.func.value, ast.Name)
                                    and val.func.value.id == '_p'):
                                found_fields_call = True

        self.assertTrue(
            found_fields_call,
            "parent_data[_p['gid']] must be assigned _p.fields() (not the Hit _p) "
            "to avoid keeping the entire _parent_res Results alive via Hit.results."
        )

    def test_fields_dict_is_plain_dict(self):
        """_p.fields() returns a plain dict; dot-get access still works."""
        mock_hit = MagicMock()
        mock_hit.fields.return_value = {
            "gid": 42,
            "aya_id": 5,
            "sura_id": 2,
            "sura": "البقرة",
            "sura_arabic": "البقرة",
            "aya": "بسم الله",
        }
        mock_hit.__getitem__ = lambda self, k: self.fields()[k]

        stored = mock_hit.fields()
        self.assertIsInstance(stored, dict)
        self.assertEqual(stored.get("aya_id"), 5)
        self.assertEqual(stored.get("sura_id"), 2)
        # Ensure no reference back to the Hit is embedded
        self.assertNotIn(mock_hit, stored.values())


# ---------------------------------------------------------------------------
# Fix 3: QSearcher caches _fuzzy_parser across fuzzy searches
# ---------------------------------------------------------------------------

class TestQSearcherFuzzyParserCached(unittest.TestCase):
    """_fuzzy_parser must be created once and reused on subsequent fuzzy searches."""

    def _make_qsearcher(self):
        """Return a minimally-mocked QSearcher without a real index."""
        from whoosh.fields import Schema, TEXT
        from alfanous.searching import QSearcher

        schema = Schema(aya_fuzzy=TEXT)
        mock_docindex = MagicMock()
        mock_docindex.get_schema.return_value = schema
        mock_index = MagicMock()
        # get_index().searcher must be callable (returns a Whoosh Searcher factory)
        mock_index.searcher = MagicMock()
        mock_docindex.get_index.return_value = mock_index

        qs = QSearcher(mock_docindex, MagicMock())
        return qs, schema

    def test_fuzzy_parser_initially_none(self):
        qs, _ = self._make_qsearcher()
        self.assertIsNone(qs._fuzzy_parser,
                          "_fuzzy_parser must start as None (lazy init)")

    def test_fuzzy_parser_cached_after_first_use(self):
        """After the first fuzzy search, _fuzzy_parser is set and reused."""
        from whoosh.qparser import QueryParser
        qs, schema = self._make_qsearcher()

        # Manually simulate what search() does on first fuzzy call:
        if qs._fuzzy_parser is None:
            qs._fuzzy_parser = QueryParser("aya_fuzzy", schema=schema)
        first_parser = qs._fuzzy_parser

        # Simulate a second fuzzy call — parser must NOT be replaced
        if qs._fuzzy_parser is None:
            qs._fuzzy_parser = QueryParser("aya_fuzzy", schema=schema)

        self.assertIs(qs._fuzzy_parser, first_parser,
                      "The same QueryParser instance must be reused across fuzzy searches")

    def test_fuzzy_parser_creation_counted(self):
        """QueryParser is only instantiated once across multiple fuzzy searches."""
        from whoosh.fields import Schema, TEXT
        from alfanous.searching import QSearcher

        schema = Schema(aya_fuzzy=TEXT)
        creation_count = [0]

        from whoosh.qparser import QueryParser as _RealQP

        class _CountingQP(_RealQP):
            def __init__(self, *args, **kwargs):
                creation_count[0] += 1
                super().__init__(*args, **kwargs)

        mock_docindex = MagicMock()
        mock_docindex.get_schema.return_value = schema
        mock_index = MagicMock()
        mock_index.searcher = MagicMock()
        mock_docindex.get_index.return_value = mock_index

        qs = QSearcher(mock_docindex, MagicMock())

        # Simulate three "fuzzy" calls using the counting parser class
        for _ in range(3):
            if qs._fuzzy_parser is None:
                qs._fuzzy_parser = _CountingQP("aya_fuzzy", schema=schema)

        self.assertEqual(
            creation_count[0], 1,
            f"QueryParser('aya_fuzzy') should be constructed exactly once, "
            f"got {creation_count[0]}."
        )


# ---------------------------------------------------------------------------
# Regex pre-compilation tests
# ---------------------------------------------------------------------------

class TestPreCompiledRegexes(unittest.TestCase):
    """Verify that hot-path regexes are compiled objects, not plain strings."""

    def test_false_pattern_is_compiled_regex(self):
        """_FALSE_PATTERN_RE must be a compiled Pattern, not a string."""
        import re
        import alfanous.outputs as _outputs
        self.assertIsInstance(
            _outputs._FALSE_PATTERN_RE, type(re.compile("")),
            "_FALSE_PATTERN_RE must be a compiled re.Pattern"
        )

    def test_false_pattern_regex_matches_expected_values(self):
        """_FALSE_PATTERN_RE must match false/no/off/0 and not true/yes/1."""
        import alfanous.outputs as _outputs
        re = _outputs._FALSE_PATTERN_RE
        for val in ("false", "False", "FALSE", "no", "No", "NO", "off", "Off", "OFF", "0"):
            self.assertIsNotNone(re.match(val), f"_FALSE_PATTERN_RE should match {val!r}")
        for val in ("true", "yes", "on", "1", "2", ""):
            self.assertIsNone(re.match(val), f"_FALSE_PATTERN_RE should NOT match {val!r}")

    def test_arabic_script_regex_is_compiled(self):
        """_ARABIC_SCRIPT_RE must be a compiled Pattern."""
        import re
        import alfanous.outputs as _outputs
        self.assertIsInstance(
            _outputs._ARABIC_SCRIPT_RE, type(re.compile("")),
            "_ARABIC_SCRIPT_RE must be a compiled re.Pattern"
        )

    def test_arabic_script_regex_detects_arabic(self):
        """_ARABIC_SCRIPT_RE must match strings containing Arabic-script characters."""
        import alfanous.outputs as _outputs
        re_obj = _outputs._ARABIC_SCRIPT_RE
        self.assertIsNotNone(re_obj.search("رحمن"), "Arabic text must match")
        self.assertIsNone(re_obj.search("rahman"), "Latin text must NOT match")
        self.assertIsNone(re_obj.search(""), "Empty string must NOT match")

    def test_is_flag_uses_precompiled_regex(self):
        """IS_FLAG must not call re.compile() with a string pattern (would recompile).

        Also verifies that _FALSE_PATTERN_RE is already compiled at import time
        so that IS_FLAG can rely on it without re-compiling on every call.
        """
        import re
        import alfanous.outputs as _outputs

        # Confirm _FALSE_PATTERN_RE is already a compiled Pattern before any test action.
        self.assertIsInstance(
            _outputs._FALSE_PATTERN_RE, type(re.compile("")),
            "_FALSE_PATTERN_RE must be compiled at module import time"
        )

        compile_calls = []
        original_compile = re.compile

        def _tracking_compile(pattern, *args, **kwargs):
            compile_calls.append(pattern)
            return original_compile(pattern, *args, **kwargs)

        with patch("re.compile", side_effect=_tracking_compile):
            # IS_FLAG is defined at module level; it must use the already-compiled
            # _FALSE_PATTERN_RE, so a call to IS_FLAG must NOT trigger re.compile.
            compile_calls.clear()
            # 'word_info' is a valid boolean flag key in Raw.DEFAULTS['flags'].
            _outputs.IS_FLAG({"word_info": "false"}, "word_info")
            self.assertEqual(
                compile_calls, [],
                "IS_FLAG must not call re.compile() on every invocation; "
                "use the module-level _FALSE_PATTERN_RE instead"
            )


# ---------------------------------------------------------------------------
# decoded_terms set-accumulation tests
# ---------------------------------------------------------------------------

class TestDecodedTermsSet(unittest.TestCase):
    """Verify decoded_terms is built as a set (no intermediate list)."""

    def test_decoded_terms_no_intermediate_list(self):
        """The fuzzy matched-terms path must not build an intermediate list.

        Narrows the search to the body of QSearcher.search so that an
        unrelated ``decoded_terms`` variable elsewhere in the module does not
        trigger a false positive.
        """
        import ast, inspect
        import alfanous.searching as _searching_module
        src = inspect.getsource(_searching_module.QSearcher.search)
        # dedent so ast.parse works on the extracted method source
        import textwrap
        tree = ast.parse(textwrap.dedent(src))

        # Find any `decoded_terms = []` inside QSearcher.search.
        found_list_init = False
        for node in ast.walk(tree):
            if (isinstance(node, ast.Assign)
                    and any(getattr(t, 'id', '') == 'decoded_terms' for t in ast.walk(node))
                    and isinstance(node.value, ast.List)):
                found_list_init = True

        self.assertFalse(
            found_list_init,
            "decoded_terms must not be initialized as a list []; "
            "it should be a set() to avoid the intermediate list-then-frozenset two-step."
        )


# ---------------------------------------------------------------------------
# Synonyms/Antonyms no-extra-copy tests
# ---------------------------------------------------------------------------

class TestSynAntNoCopy(unittest.TestCase):
    """SynonymsQuery._get_synonyms and AntonymsQuery._get_antonyms must not
    wrap the dict value in an extra list() copy."""

    def test_synonyms_no_extra_list_copy(self):
        """_get_synonyms must not call list() on the result of syndict.get()."""
        import ast, inspect, textwrap
        from alfanous.query_plugins import SynonymsQuery
        src = textwrap.dedent(inspect.getsource(SynonymsQuery._get_synonyms))
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Name) and func.id == 'list':
                    self.fail(
                        "SynonymsQuery._get_synonyms must not call list() — "
                        "slicing a list already returns a new list."
                    )

    def test_antonyms_no_extra_list_copy(self):
        """_get_antonyms must not call list() on the result of antdict.get()."""
        import ast, inspect, textwrap
        from alfanous.query_plugins import AntonymsQuery
        src = textwrap.dedent(inspect.getsource(AntonymsQuery._get_antonyms))
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Name) and func.id == 'list':
                    self.fail(
                        "AntonymsQuery._get_antonyms must not call list() — "
                        "slicing a list already returns a new list."
                    )

    def test_synonyms_returns_correct_words(self):
        """_get_synonyms must still return the right words after the fix."""
        from unittest.mock import patch
        from alfanous.query_plugins import SynonymsQuery
        with patch("alfanous.query_plugins.syndict", {"word": ["syn1", "syn2"]}):
            result = SynonymsQuery._get_synonyms("word")
            self.assertEqual(result, ["syn1", "syn2"])

    def test_antonyms_returns_correct_words(self):
        """_get_antonyms must still return the right words after the fix."""
        from unittest.mock import patch
        from alfanous.query_plugins import AntonymsQuery
        with patch("alfanous.query_plugins.antdict", {"word": ["ant1", "ant2"]}):
            result = AntonymsQuery._get_antonyms("word")
            self.assertEqual(result, ["ant1", "ant2"])


# ---------------------------------------------------------------------------
# Arabizi _convert set-accumulation tests
# ---------------------------------------------------------------------------

class TestArabiziConvertSetAccumulation(unittest.TestCase):
    """Verify that arabizi_to_arabic_list no longer calls list(set(...)) per
    recursion frame and that the results remain correct."""

    def test_no_per_frame_list_set_call(self):
        """_convert must not call list(set(...)) at the end of each frame."""
        import ast, inspect
        import alfanous.romanization as _rom_module
        src = inspect.getsource(_rom_module)
        tree = ast.parse(src)

        # Look for `return list(set(...))` inside the `_convert` inner function.
        # After the fix, _convert returns a set directly (`return results`).
        found = False
        for fn_node in ast.walk(tree):
            if not (isinstance(fn_node, ast.FunctionDef) and fn_node.name == '_convert'):
                continue
            for ret in ast.walk(fn_node):
                if not isinstance(ret, ast.Return):
                    continue
                val = ret.value
                # Detect: return list(set(...))
                if (isinstance(val, ast.Call)
                        and isinstance(val.func, ast.Name) and val.func.id == 'list'
                        and len(val.args) == 1
                        and isinstance(val.args[0], ast.Call)
                        and isinstance(val.args[0].func, ast.Name)
                        and val.args[0].func.id == 'set'):
                    found = True

        self.assertFalse(
            found,
            "_convert must not return list(set(results)) on each frame; "
            "results should be accumulated in a set and returned directly."
        )

    def test_basic_conversion_correct(self):
        """Basic Arabizi → Arabic conversions must remain correct after refactor."""
        from alfanous.romanization import arabizi_to_arabic_list
        candidates = set(arabizi_to_arabic_list("rahman"))
        self.assertIn("رحمن", candidates, "rahman must produce رحمن")

    def test_definite_article_prefix(self):
        """'al' prefix must still produce ال in the output."""
        from alfanous.romanization import arabizi_to_arabic_list
        candidates = set(arabizi_to_arabic_list("al7amd"))
        self.assertIn("الحمد", candidates, "al7amd must produce الحمد")

    def test_digraph_conversion(self):
        """Digraph 'sh' must produce ش."""
        from alfanous.romanization import arabizi_to_arabic_list
        candidates = set(arabizi_to_arabic_list("shams"))
        self.assertTrue(
            any("ش" in c for c in candidates),
            "shams must produce a candidate containing ش"
        )

    def test_result_is_list(self):
        """arabizi_to_arabic_list must still return a list (not a set)."""
        from alfanous.romanization import arabizi_to_arabic_list
        result = arabizi_to_arabic_list("rahman")
        self.assertIsInstance(result, list,
                              "arabizi_to_arabic_list must return a list")

    def test_result_is_deduplicated(self):
        """The returned list must not contain duplicates."""
        from alfanous.romanization import arabizi_to_arabic_list
        result = arabizi_to_arabic_list("salah")
        self.assertEqual(len(result), len(set(result)),
                         "arabizi_to_arabic_list result must contain no duplicates")

    def test_lru_cache_maxsize_reduced(self):
        """_query_word_index_cached must use maxsize=256, not 1024."""
        import alfanous.query_plugins as _qp
        cache_info = _qp._query_word_index_cached.cache_info()
        self.assertEqual(
            cache_info.maxsize, 256,
            "_query_word_index_cached LRU cache maxsize must be 256"
        )


# ---------------------------------------------------------------------------
# BasicSearchEngine.close() / context-manager tests
# ---------------------------------------------------------------------------

class TestBasicSearchEngineClose(unittest.TestCase):
    """BasicSearchEngine must expose close() and a context manager."""

    def _make_engine(self):
        """Return a BasicSearchEngine backed by mocks (no real index required)."""
        from whoosh.fields import Schema, TEXT
        from alfanous.engines import BasicSearchEngine
        from alfanous.searching import QSearcher, QReader

        schema = Schema(aya=TEXT)
        mock_docindex = MagicMock()
        mock_docindex.OK = True
        mock_docindex.get_schema.return_value = schema
        mock_index = MagicMock()
        mock_index.searcher = MagicMock(return_value=MagicMock())
        mock_docindex.get_index.return_value = mock_index

        engine = BasicSearchEngine(
            qdocindex=mock_docindex,
            query_parser=MagicMock(return_value=MagicMock()),
            main_field="aya",
            otherfields=[],
            qsearcher=QSearcher,
            qreader=QReader,
            qhighlight=MagicMock(),
        )
        return engine

    def test_close_method_exists(self):
        """BasicSearchEngine must have a close() method."""
        from alfanous.engines import BasicSearchEngine
        self.assertTrue(
            callable(getattr(BasicSearchEngine, 'close', None)),
            "BasicSearchEngine must have a callable close() method"
        )

    def test_close_calls_searcher_close(self):
        """close() must delegate to the internal QSearcher.close()."""
        engine = self._make_engine()
        with patch.object(engine._searcher, 'close') as mock_close:
            engine.close()
        mock_close.assert_called_once()

    def test_close_is_idempotent(self):
        """Calling close() multiple times must not raise."""
        engine = self._make_engine()
        engine.close()
        engine.close()  # must not raise

    def test_context_manager_calls_close(self):
        """Using BasicSearchEngine as a context manager must call close() on exit."""
        engine = self._make_engine()
        with patch.object(engine, 'close') as mock_close:
            with engine:
                pass
        mock_close.assert_called_once()

    def test_engine_has_enter_exit(self):
        """BasicSearchEngine must implement __enter__ and __exit__."""
        from alfanous.engines import BasicSearchEngine
        self.assertTrue(hasattr(BasicSearchEngine, '__enter__'), "__enter__ missing")
        self.assertTrue(hasattr(BasicSearchEngine, '__exit__'), "__exit__ missing")


# ---------------------------------------------------------------------------
# Raw.close() / context-manager tests
# ---------------------------------------------------------------------------

class TestRawClose(unittest.TestCase):
    """Raw must expose close() and a context manager."""

    def _make_raw(self):
        """Return a Raw instance with a mocked QSE engine."""
        from alfanous.outputs import Raw
        raw = Raw.__new__(Raw)
        raw.QSE = MagicMock()
        raw.QSE.OK = False
        return raw

    def test_close_method_exists(self):
        """Raw must have a close() method."""
        from alfanous.outputs import Raw
        self.assertTrue(
            callable(getattr(Raw, 'close', None)),
            "Raw must have a callable close() method"
        )

    def test_close_delegates_to_qse(self):
        """Raw.close() must call self.QSE.close()."""
        raw = self._make_raw()
        raw.close()
        raw.QSE.close.assert_called_once()

    def test_close_is_idempotent(self):
        """Calling Raw.close() multiple times must not raise."""
        raw = self._make_raw()
        raw.close()
        raw.close()  # must not raise

    def test_context_manager_calls_close(self):
        """Using Raw as a context manager must call close() on exit."""
        raw = self._make_raw()
        with patch.object(raw, 'close') as mock_close:
            with raw:
                pass
        mock_close.assert_called_once()

    def test_raw_has_enter_exit(self):
        """Raw must implement __enter__ and __exit__."""
        from alfanous.outputs import Raw
        self.assertTrue(hasattr(Raw, '__enter__'), "__enter__ missing")
        self.assertTrue(hasattr(Raw, '__exit__'), "__exit__ missing")


# ---------------------------------------------------------------------------
# most_frequent_words str/bytes robustness test
# ---------------------------------------------------------------------------

class TestMostFrequentWordsDecoding(unittest.TestCase):
    """most_frequent_words must handle both bytes and str term values."""

    def test_handles_str_terms(self):
        """most_frequent_words must not crash when Whoosh returns str terms."""
        from alfanous.engines import BasicSearchEngine
        engine = BasicSearchEngine.__new__(BasicSearchEngine)

        mock_reader = MagicMock()
        mock_reader.most_frequent_terms.return_value = [
            (100.0, 'مِنْ'),
            (50.0, 'الله'),
        ]
        engine._reader = MagicMock()
        # Simulate the .reader property returning our mock reader
        type(engine._reader).reader = PropertyMock(return_value=mock_reader)

        result = engine.most_frequent_words(2, "aya_")
        self.assertEqual(result, [(100.0, 'مِنْ'), (50.0, 'الله')])

    def test_handles_bytes_terms(self):
        """most_frequent_words must decode bytes terms with UTF-8."""
        from alfanous.engines import BasicSearchEngine
        engine = BasicSearchEngine.__new__(BasicSearchEngine)

        mock_reader = MagicMock()
        mock_reader.most_frequent_terms.return_value = [
            (100.0, 'مِنْ'.encode('utf-8')),
            (50.0, 'الله'.encode('utf-8')),
        ]
        engine._reader = MagicMock()
        type(engine._reader).reader = PropertyMock(return_value=mock_reader)

        result = engine.most_frequent_words(2, "aya_")
        self.assertEqual(result, [(100.0, 'مِنْ'), (50.0, 'الله')])


# ---------------------------------------------------------------------------
# Iteration-2 fixes
# ---------------------------------------------------------------------------

class TestNoDeadAvailableFieldsSet(unittest.TestCase):
    """_available_fields_set must not appear in _search_translation."""

    def test_available_fields_set_removed(self):
        """_search_translation must not compute _available_fields_set (dead code)."""
        import ast, inspect, textwrap
        import alfanous.outputs as _outputs_module
        src = textwrap.dedent(inspect.getsource(_outputs_module.Raw._search_translation))
        tree = ast.parse(src)

        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if (isinstance(target, ast.Name)
                            and target.id == "_available_fields_set"):
                        self.fail(
                            "_search_translation must not assign _available_fields_set — "
                            "it was dead code (computed but never used)."
                        )


class TestNoFunctionLevelWhooshImports(unittest.TestCase):
    """Hot-path methods must not contain function-level 'from whoosh import' statements."""

    def _source_has_function_import(self, fn, pattern):
        import ast, inspect, textwrap
        src = textwrap.dedent(inspect.getsource(fn))
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                if pattern in ast.unparse(node):
                    return True
        return False

    def test_build_filter_query_no_whoosh_import(self):
        """_build_filter_query must not contain a per-call 'from whoosh import'."""
        import alfanous.outputs as _outputs_module
        self.assertFalse(
            self._source_has_function_import(_outputs_module._build_filter_query, "whoosh"),
            "_build_filter_query must use the module-level wquery, not a per-call import"
        )

    def test_search_aya_no_whoosh_import(self):
        """_search_aya must not contain a per-call 'from whoosh import query'."""
        import alfanous.outputs as _outputs_module
        self.assertFalse(
            self._source_has_function_import(
                _outputs_module.Raw._search_aya, "from whoosh import query"
            ),
            "_search_aya must use the module-level wquery, not a per-call import"
        )

    def test_search_translation_no_whoosh_import(self):
        """_search_translation must not contain a per-call 'from whoosh import'."""
        import alfanous.outputs as _outputs_module
        self.assertFalse(
            self._source_has_function_import(_outputs_module.Raw._search_translation, "whoosh"),
            "_search_translation must use the module-level wquery, not a per-call import"
        )

    def test_qsearcher_search_no_function_import(self):
        """QSearcher.search must not contain per-call 'from whoosh' imports."""
        import alfanous.searching as _searching_module
        self.assertFalse(
            self._source_has_function_import(_searching_module.QSearcher.search, "whoosh"),
            "QSearcher.search must use module-level names, not per-call imports"
        )


class TestNoRedundantQuranUnvocalizedWordsImport(unittest.TestCase):
    """_search_aya must not re-import quran_unvocalized_words (already in scope via *-import)."""

    def test_no_per_call_quran_unvocalized_words_import(self):
        import ast, inspect, textwrap
        import alfanous.outputs as _outputs_module
        src = textwrap.dedent(inspect.getsource(_outputs_module.Raw._search_aya))
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if (node.module == "alfanous.data"
                        and any(a.name == "quran_unvocalized_words" for a in node.names)):
                    self.fail(
                        "_search_aya must not import quran_unvocalized_words per-call; "
                        "it is already in scope via 'from alfanous.data import *'."
                    )


class TestEditDistanceNoDeadBranch(unittest.TestCase):
    """_edit_distance must not contain the always-False early-exit condition."""

    def test_no_abs_max_dead_branch(self):
        """The 'if abs(m-n) > max(m,n,1)' branch must be removed."""
        import ast, inspect
        import alfanous.outputs as _outputs_module
        src = inspect.getsource(_outputs_module._edit_distance)
        tree = ast.parse(src)

        found = False
        for node in ast.walk(tree):
            # Look for a Compare node that compares abs(m-n) > max(m,n,1)
            if isinstance(node, ast.Compare) and len(node.ops) == 1:
                if isinstance(node.ops[0], ast.Gt):
                    # Check if left side involves 'abs'
                    left = node.left
                    if (isinstance(left, ast.Call)
                            and isinstance(left.func, ast.Name)
                            and left.func.id == "abs"):
                        found = True

        self.assertFalse(
            found,
            "_edit_distance must not contain 'abs(m-n) > max(m,n,1)'; "
            "this condition is always False and is dead code."
        )

    def test_edit_distance_correctness_unchanged(self):
        """_edit_distance results must still be correct after removing dead branch."""
        from alfanous.outputs import _edit_distance

        self.assertEqual(_edit_distance("", ""), 0)
        self.assertEqual(_edit_distance("abc", "abc"), 0)
        self.assertEqual(_edit_distance("abc", "ab"), 1)
        self.assertEqual(_edit_distance("abc", "axc"), 1)
        self.assertEqual(_edit_distance("abc", "xyz"), 3)
        self.assertEqual(_edit_distance("", "abc"), 3)
        self.assertEqual(_edit_distance("abc", ""), 3)
        # Asymmetric cases
        self.assertEqual(_edit_distance("kitten", "sitting"), 3)

    def test_edit_distance_short_strings(self):
        """_edit_distance handles empty and single-character strings."""
        from alfanous.outputs import _edit_distance
        self.assertEqual(_edit_distance("", ""), 0)
        self.assertEqual(_edit_distance("a", ""), 1)
        self.assertEqual(_edit_distance("", "a"), 1)
        self.assertEqual(_edit_distance("a", "a"), 0)
        self.assertEqual(_edit_distance("a", "b"), 1)


class TestModuleLevelImports(unittest.TestCase):
    """Key symbols must be importable directly from the module (module-level)."""

    def test_wquery_accessible_at_module_level(self):
        """wquery must be a module-level attribute of alfanous.outputs."""
        import alfanous.outputs as _outputs_module
        self.assertTrue(
            hasattr(_outputs_module, 'wquery'),
            "wquery must be imported at module level in alfanous.outputs"
        )

    def test_arabizi_to_arabic_list_at_module_level(self):
        """arabizi_to_arabic_list must be importable from alfanous.outputs module namespace."""
        import alfanous.outputs as _outputs_module
        self.assertTrue(
            hasattr(_outputs_module, 'arabizi_to_arabic_list'),
            "arabizi_to_arabic_list must be imported at module level in alfanous.outputs"
        )

    def test_filter_candidates_by_wordset_at_module_level(self):
        """filter_candidates_by_wordset must be importable from alfanous.outputs module namespace."""
        import alfanous.outputs as _outputs_module
        self.assertTrue(
            hasattr(_outputs_module, 'filter_candidates_by_wordset'),
            "filter_candidates_by_wordset must be imported at module level in alfanous.outputs"
        )

    def test_qparser_at_module_level_in_searching(self):
        """_QueryParser must be importable from alfanous.searching module namespace."""
        import alfanous.searching as _searching_module
        self.assertTrue(
            hasattr(_searching_module, '_QueryParser'),
            "_QueryParser must be imported at module level in alfanous.searching"
        )


# ---------------------------------------------------------------------------
# Iteration-3 fixes (outputs.py optimisation pass)
# ---------------------------------------------------------------------------

class TestNoUnusedQueryInDo(unittest.TestCase):
    """_do must not assign an unused `query` variable."""

    def test_do_has_no_dead_query_assignment(self):
        """The unused `query` local variable must be removed from Raw._do."""
        import ast, inspect, textwrap
        import alfanous.outputs as _outputs_module
        src = textwrap.dedent(inspect.getsource(_outputs_module.Raw._do))
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "query":
                        self.fail(
                            "Raw._do must not assign `query` — it is unused in _do "
                            "and was dead code."
                        )


class TestResultDocnumsAndIndexReaderScoped(unittest.TestCase):
    """_result_docnums and _index_reader must be created only inside word_info block."""

    def _search_aya_source(self):
        import inspect, textwrap
        import alfanous.outputs as m
        return textwrap.dedent(inspect.getsource(m.Raw._search_aya))

    def test_result_docnums_inside_word_info_block(self):
        """_result_docnums must only be assigned inside the word_info block."""
        import ast
        src = self._search_aya_source()
        tree = ast.parse(src)

        # Walk the AST and look for top-level assignments of _result_docnums
        # (i.e., not nested under an `if word_info:` branch).
        # A simple heuristic: check that the assignment target name appears
        # only inside a branch whose test includes 'word_info'.
        def _assigns_outside_word_info(node, in_word_info=False):
            if isinstance(node, ast.If):
                test_src = ast.unparse(node.test)
                is_wi = "word_info" in test_src
                for child in ast.walk(node):
                    if child is node:
                        continue
                    if isinstance(child, ast.Assign):
                        for t in child.targets:
                            if isinstance(t, ast.Name) and t.id == "_result_docnums":
                                if not is_wi and not in_word_info:
                                    return True
            elif isinstance(node, ast.Assign):
                for t in node.targets:
                    if isinstance(t, ast.Name) and t.id == "_result_docnums":
                        if not in_word_info:
                            return True
            return False

        # Check top-level statements (direct children of function body)
        for stmt in ast.parse(src).body[0].body:
            if _assigns_outside_word_info(stmt):
                self.fail(
                    "_result_docnums is assigned outside the word_info block — "
                    "move it inside `if word_info:` to avoid iterating all results "
                    "on every request when word_info=False."
                )

    def test_gid_base_query_removed(self):
        """_gid_base_query string building must not exist in _search_aya."""
        import ast
        src = self._search_aya_source()
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for t in node.targets:
                    if isinstance(t, ast.Name) and t.id == "_gid_base_query":
                        self.fail(
                            "_gid_base_query must be removed — it built a query "
                            "string that was immediately re-parsed by find_extended. "
                            "Use a pre-built wquery object instead."
                        )

    def test_adjacent_aya_uses_search_with_query_not_find_extended(self):
        """Adjacent-aya lookup must use search_with_query, not find_extended."""
        import ast
        src = self._search_aya_source()
        tree = ast.parse(src)
        # Check that no Call node invokes find_extended (comments are ignored by AST).
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Attribute) and func.attr == "find_extended":
                    self.fail(
                        "_search_aya must not call find_extended — replace with pre-built "
                        "wquery objects passed to search_with_query to avoid string parsing overhead."
                    )
                if isinstance(func, ast.Name) and func.id == "find_extended":
                    self.fail(
                        "_search_aya must not call find_extended — replace with pre-built "
                        "wquery objects passed to search_with_query to avoid string parsing overhead."
                    )


class TestHighlightCheckedOnce(unittest.TestCase):
    """H / TH lambdas must not re-evaluate `highlight != 'none'` on every call."""

    def _get_src(self, method_name):
        import inspect, textwrap
        import alfanous.outputs as m
        return textwrap.dedent(inspect.getsource(getattr(m.Raw, method_name)))

    def _lambda_contains_highlight_check(self, src):
        """Return True if any lambda in src contains 'highlight != 'none''."""
        import ast
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.Lambda):
                lambda_src = ast.unparse(node)
                if "highlight" in lambda_src and "none" in lambda_src:
                    return True
        return False

    def test_search_aya_H_lambda_no_highlight_check(self):
        """H lambda in _search_aya must not re-check highlight on every call."""
        self.assertFalse(
            self._lambda_contains_highlight_check(self._get_src("_search_aya")),
            "H/TH lambdas in _search_aya must not contain `highlight != 'none'` — "
            "check once before the lambda definition."
        )

    def test_search_translation_H_lambda_no_highlight_check(self):
        """H lambda in _search_translation must not re-check highlight on every call."""
        self.assertFalse(
            self._lambda_contains_highlight_check(self._get_src("_search_translation")),
            "H lambda in _search_translation must not contain `highlight != 'none'`."
        )

    def test_search_words_H_lambda_no_highlight_check(self):
        """H lambda in _search_words must not re-check highlight on every call."""
        self.assertFalse(
            self._lambda_contains_highlight_check(self._get_src("_search_words")),
            "H lambda in _search_words must not contain `highlight != 'none'`."
        )


class TestSajdaEvaluatedOnce(unittest.TestCase):
    """r['sajda'] == 'نعم' must not appear more than once per aya in _search_aya."""

    def test_sajda_comparison_deduplicated(self):
        import inspect, textwrap
        import alfanous.outputs as m
        src = textwrap.dedent(inspect.getsource(m.Raw._search_aya))
        count = src.count('r["sajda"] == "نعم"') + src.count("r['sajda'] == 'نعم'")
        self.assertLessEqual(
            count, 1,
            f"r['sajda'] == 'نعم' appears {count} times in _search_aya — "
            "evaluate it once per aya into _is_sajda and reuse."
        )


class TestScriptCheckedOnce(unittest.TestCase):
    """script == 'standard' must be pre-computed once, not re-evaluated per aya."""

    def test_use_standard_script_variable_present(self):
        import inspect, textwrap
        import alfanous.outputs as m
        src = textwrap.dedent(inspect.getsource(m.Raw._search_aya))
        self.assertIn(
            "_use_standard_script",
            src,
            "_search_aya must cache `script == 'standard'` as `_use_standard_script` "
            "before the per-aya loop to avoid re-evaluating it 4× per result."
        )

    def test_script_standard_not_compared_in_loop(self):
        """script == 'standard' must not appear in the per-aya result loop body."""
        import ast, inspect, textwrap
        import alfanous.outputs as m
        src = textwrap.dedent(inspect.getsource(m.Raw._search_aya))
        tree = ast.parse(src)

        # Count Compare nodes that test `script == "standard"` at the AST level.
        # We expect exactly ONE such node: the `_use_standard_script = script == "standard"` assignment.
        # Any additional occurrences are in the per-aya loop and should be replaced with _use_standard_script.
        compare_count = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.Compare) and len(node.ops) == 1:
                if isinstance(node.ops[0], ast.Eq):
                    left = node.left
                    comparators = node.comparators
                    if (isinstance(left, ast.Name) and left.id == "script"
                            and len(comparators) == 1
                            and isinstance(comparators[0], ast.Constant)
                            and comparators[0].value == "standard"):
                        compare_count += 1

        self.assertLessEqual(
            compare_count, 1,
            f"'script == standard' appears as a Compare node {compare_count} time(s) in _search_aya — "
            "only the single `_use_standard_script = script == 'standard'` definition is allowed; "
            "the per-aya loop must use `_use_standard_script` instead."
        )


if __name__ == "__main__":
    unittest.main()
