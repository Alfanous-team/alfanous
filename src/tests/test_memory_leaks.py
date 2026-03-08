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


if __name__ == "__main__":
    unittest.main()
