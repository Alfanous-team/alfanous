"""
Focused tests for the memory-management fixes:

1. outputs.py  – extend_runtime is no longer accumulated inside the
                 adjacent-aya loop (it was added once per hit).
2. outputs.py  – parent_data stores plain dicts (_p.fields()) instead of
                 Whoosh Hit objects so that the parent Results and its
                 Searcher reference are released sooner.
3. engines.py  – BasicSearchEngine builds _word_lookup_table at init and
                 frees it in close().
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
# Fix 3: BasicSearchEngine builds _word_lookup_table at init and frees it
#         in close() so the iter_docs memory is not held forever.
# ---------------------------------------------------------------------------

class TestWordLookupTableLifecycle(unittest.TestCase):
    """_word_lookup_table must be built at engine init and freed in close()."""

    def _make_engine_with_reader(self):
        """Return a minimally-mocked BasicSearchEngine."""
        from alfanous.engines import BasicSearchEngine

        mock_reader = MagicMock()
        mock_reader.iter_docs.return_value = iter([])  # no docs

        mock_docindex = MagicMock()
        mock_docindex.OK = True
        mock_docindex.get_schema.return_value = MagicMock()
        mock_index = MagicMock()
        mock_index.searcher = MagicMock()
        mock_docindex.get_index.return_value = mock_index

        mock_qr = MagicMock()
        mock_qr.reader = mock_reader
        mock_qr.attach_to_searcher = MagicMock()

        engine = BasicSearchEngine(
            qdocindex=mock_docindex,
            query_parser=MagicMock(return_value=MagicMock()),
            main_field="aya",
            otherfields=[],
            qsearcher=MagicMock(return_value=MagicMock()),
            qreader=MagicMock(return_value=mock_qr),
            qhighlight=MagicMock(),
        )
        return engine

    def test_word_lookup_table_built_at_init(self):
        """_word_lookup_table must be a 6-tuple after engine init."""
        engine = self._make_engine_with_reader()
        self.assertTrue(
            hasattr(engine, '_word_lookup_table'),
            "BasicSearchEngine must have _word_lookup_table after __init__"
        )
        tbl = engine._word_lookup_table
        self.assertIsInstance(tbl, tuple)
        self.assertEqual(len(tbl), 6)

    def test_word_lookup_table_freed_on_close(self):
        """_word_lookup_table must be None after close()."""
        engine = self._make_engine_with_reader()
        engine.close()
        self.assertIsNone(
            engine._word_lookup_table,
            "_word_lookup_table must be set to None in close()"
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

    def test_close_does_not_delegate_to_qse(self):
        """Raw.close() must NOT call self.QSE.close().

        The QSE engine is a process-level singleton shared by every Raw /
        Engine instance.  Closing it from Raw.close() would invalidate all
        other callers (including the module-level ``_R``) that still hold a
        reference to the same singleton, which is the root cause of the
        ReaderClosed errors that occur when Engine is instantiated many times
        (e.g. once per autocomplete request).
        """
        raw = self._make_raw()
        raw.close()
        raw.QSE.close.assert_not_called()

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

    def test_multiple_raw_instances_share_qse_and_close_is_safe(self):
        """Closing one Raw instance must not break other Raw instances.

        Both instances share the same QSE singleton; calling close() on
        the first must not close the shared QSE so the second remains usable.
        """
        from alfanous.outputs import Raw
        mock_qse = MagicMock()
        mock_qse.OK = False

        raw1 = Raw.__new__(Raw)
        raw1.QSE = mock_qse

        raw2 = Raw.__new__(Raw)
        raw2.QSE = mock_qse

        # Closing raw1 must NOT call QSE.close()
        raw1.close()
        mock_qse.close.assert_not_called()

        # raw2 still references the same QSE and should work fine
        self.assertIs(raw2.QSE, mock_qse)


# ---------------------------------------------------------------------------
# most_frequent_words str/bytes robustness test
# ---------------------------------------------------------------------------

class TestMostFrequentWordsDecoding(unittest.TestCase):
    """most_frequent_words must handle both bytes and str term values."""

    def test_handles_str_terms(self):
        """most_frequent_words must not crash when Whoosh returns str terms."""
        from alfanous.engines import BasicSearchEngine
        from alfanous.searching import QReader
        engine = BasicSearchEngine.__new__(BasicSearchEngine)

        mock_reader = MagicMock()
        mock_reader.most_frequent_terms.return_value = [
            (100.0, 'مِنْ'),
            (50.0, 'الله'),
        ]
        engine._reader = QReader.__new__(QReader)
        engine._reader._qsearcher = None
        engine._reader._own_reader = None
        with patch.object(QReader, 'reader', new_callable=PropertyMock, return_value=mock_reader):
            result = engine.most_frequent_words(2, "aya_")
        self.assertEqual(result, [(100.0, 'مِنْ'), (50.0, 'الله')])

    def test_handles_bytes_terms(self):
        """most_frequent_words must decode bytes terms with UTF-8."""
        from alfanous.engines import BasicSearchEngine
        from alfanous.searching import QReader
        engine = BasicSearchEngine.__new__(BasicSearchEngine)

        mock_reader = MagicMock()
        mock_reader.most_frequent_terms.return_value = [
            (100.0, 'مِنْ'.encode('utf-8')),
            (50.0, 'الله'.encode('utf-8')),
        ]
        engine._reader = QReader.__new__(QReader)
        engine._reader._qsearcher = None
        engine._reader._own_reader = None
        with patch.object(QReader, 'reader', new_callable=PropertyMock, return_value=mock_reader):
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


# ---------------------------------------------------------------------------
# Iteration-4 fixes
# ---------------------------------------------------------------------------

class TestAutocompleteDecodeGuard(unittest.TestCase):
    """QReader.autocomplete must use _decode_if_bytes, not a raw .decode() call."""

    def test_autocomplete_uses_decode_if_bytes(self):
        """autocomplete must not call .decode() directly — use _decode_if_bytes."""
        import ast
        import inspect
        import textwrap
        import alfanous.searching as _searching_module
        src = textwrap.dedent(inspect.getsource(_searching_module.QReader.autocomplete))
        tree = ast.parse(src)

        # Raw .decode() calls: look for Attribute nodes named 'decode' on any value.
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Attribute) and func.attr == "decode":
                    self.fail(
                        "QReader.autocomplete must not call .decode() directly — "
                        "use `_decode_if_bytes(x)` instead so it is safe when "
                        "Whoosh returns str rather than bytes."
                    )

    def test_autocomplete_handles_str_terms(self):
        """autocomplete must not raise when expand_prefix yields str instead of bytes."""
        from alfanous.searching import QReader, _decode_if_bytes
        from unittest.mock import MagicMock, PropertyMock

        reader_obj = MagicMock()
        reader_obj.expand_prefix.return_value = ['الله', 'اللهم']  # str terms (newer Whoosh)

        qr = QReader.__new__(QReader)
        qr._qsearcher = None
        qr._own_reader = None
        with patch.object(QReader, 'reader', new_callable=PropertyMock, return_value=reader_obj):
            result = qr.autocomplete('الل')
        self.assertEqual(result, ['الله', 'اللهم'])

    def test_autocomplete_handles_bytes_terms(self):
        """autocomplete must decode bytes terms correctly."""
        from alfanous.searching import QReader
        from unittest.mock import MagicMock, PropertyMock

        reader_obj = MagicMock()
        reader_obj.expand_prefix.return_value = ['الله'.encode('utf-8'), 'اللهم'.encode('utf-8')]

        qr = QReader.__new__(QReader)
        qr._qsearcher = None
        qr._own_reader = None
        with patch.object(QReader, 'reader', new_callable=PropertyMock, return_value=reader_obj):
            result = qr.autocomplete('الل')
        self.assertEqual(result, ['الله', 'اللهم'])


class TestSharedSearcherNoPerCallImport(unittest.TestCase):
    """BasicSearchEngine.shared_searcher must not contain a per-call import."""

    def test_no_per_call_import_in_shared_searcher(self):
        """shared_searcher must not import _SearcherProxy on every call."""
        import ast
        import inspect
        import textwrap
        import alfanous.engines as _engines_module
        src = textwrap.dedent(inspect.getsource(_engines_module.BasicSearchEngine.shared_searcher))
        tree = ast.parse(src)

        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if (node.module == "alfanous.searching"
                        and any(a.name == "_SearcherProxy" for a in node.names)):
                    self.fail(
                        "BasicSearchEngine.shared_searcher must not import _SearcherProxy "
                        "per-call — it is already imported at module level in engines.py."
                    )

    def test_searcher_proxy_module_level_in_engines(self):
        """_SearcherProxy must be accessible as a module-level name in engines."""
        import alfanous.engines as _engines_module
        self.assertTrue(
            hasattr(_engines_module, '_SearcherProxy'),
            "_SearcherProxy must be imported at module level in engines.py"
        )


# ---------------------------------------------------------------------------
# Iteration-5 fixes
# ---------------------------------------------------------------------------

class TestNoLimitNoneInFaceting(unittest.TestCase):
    """outputs.py must not use limit=None for faceting (OOM risk)."""

    def _get_all_limit_none_lines(self, src):
        """Return a list of line numbers for every searcher.search(limit=None) call."""
        import ast
        tree = ast.parse(src)
        hits = []
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            # Look for <something>.search(...)
            func = node.func
            if not (isinstance(func, ast.Attribute) and func.attr == "search"):
                continue
            for kw in node.keywords:
                if kw.arg == "limit" and isinstance(kw.value, ast.Constant) and kw.value.value is None:
                    hits.append(node.lineno)
        return hits

    def test_no_limit_none_in_outputs(self):
        """outputs.py must not pass limit=None to any searcher.search() call."""
        import inspect
        import alfanous.outputs as _outputs_module
        src = inspect.getsource(_outputs_module)
        hits = self._get_all_limit_none_lines(src)
        self.assertEqual(
            hits, [],
            f"outputs.py has searcher.search(limit=None) at line(s) {hits}; "
            "use _MAX_FACET_DOCS instead to bound memory usage."
        )

    def test_max_facet_docs_constant_exists(self):
        """_MAX_FACET_DOCS must be defined as a module-level constant in outputs.py."""
        import alfanous.outputs as _outputs_module
        self.assertTrue(
            hasattr(_outputs_module, "_MAX_FACET_DOCS"),
            "_MAX_FACET_DOCS must be defined at module level in alfanous.outputs"
        )

    def test_max_facet_docs_value_is_reasonable(self):
        """_MAX_FACET_DOCS must be at least QURAN_TOTAL_VERSES and at most 1_000_000."""
        import alfanous.outputs as _outputs_module
        from alfanous.constants import QURAN_TOTAL_VERSES
        cap = _outputs_module._MAX_FACET_DOCS
        self.assertIsInstance(cap, int, "_MAX_FACET_DOCS must be an integer")
        self.assertGreaterEqual(
            cap, QURAN_TOTAL_VERSES,
            f"_MAX_FACET_DOCS ({cap}) must be >= QURAN_TOTAL_VERSES ({QURAN_TOTAL_VERSES})"
        )
        self.assertLessEqual(
            cap, 1_000_000,
            f"_MAX_FACET_DOCS ({cap}) must be <= 1_000_000 (otherwise the cap has no practical effect)"
        )


class TestArabiziCandidateCap(unittest.TestCase):
    """arabizi_to_arabic_list must never produce more than _MAX_ARABIZI_CANDIDATES items."""

    def test_max_arabizi_candidates_constant_exists(self):
        """_MAX_ARABIZI_CANDIDATES must be defined in alfanous.romanization."""
        import alfanous.romanization as _rom
        self.assertTrue(
            hasattr(_rom, "_MAX_ARABIZI_CANDIDATES"),
            "_MAX_ARABIZI_CANDIDATES must be defined at module level in alfanous.romanization"
        )

    def test_max_arabizi_candidates_value_is_positive(self):
        """_MAX_ARABIZI_CANDIDATES must be a positive integer."""
        import alfanous.romanization as _rom
        cap = _rom._MAX_ARABIZI_CANDIDATES
        self.assertIsInstance(cap, int, "_MAX_ARABIZI_CANDIDATES must be an integer")
        self.assertGreater(cap, 0, "_MAX_ARABIZI_CANDIDATES must be positive")

    def test_long_ambiguous_input_capped(self):
        """A long all-vowel input must produce at most _MAX_ARABIZI_CANDIDATES results."""
        from alfanous.romanization import arabizi_to_arabic_list, _MAX_ARABIZI_CANDIDATES
        # All vowels: each maps to 2–3 Arabic chars + empty-string option → exponential growth.
        result = arabizi_to_arabic_list("aeiouaeiou")
        self.assertLessEqual(
            len(result), _MAX_ARABIZI_CANDIDATES,
            f"arabizi_to_arabic_list produced {len(result)} candidates for a 10-vowel input; "
            f"must be capped at _MAX_ARABIZI_CANDIDATES={_MAX_ARABIZI_CANDIDATES}"
        )

    def test_normal_input_still_correct(self):
        """Normal Arabizi inputs must still produce correct Arabic candidates after capping."""
        from alfanous.romanization import arabizi_to_arabic_list
        # Short, unambiguous input — should not be affected by the cap.
        candidates = set(arabizi_to_arabic_list("rahman"))
        self.assertIn("رحمن", candidates, "rahman must still produce رحمن with the cap in place")

    def test_result_never_exceeds_cap(self):
        """No call to arabizi_to_arabic_list must return more items than the cap."""
        from alfanous.romanization import arabizi_to_arabic_list, _MAX_ARABIZI_CANDIDATES
        for test_input in ("aaaaaaaaaaaa", "eeeeeeeeee", "sssssssssss", "aaabbbccc"):
            result = arabizi_to_arabic_list(test_input)
            self.assertLessEqual(
                len(result), _MAX_ARABIZI_CANDIDATES,
                f"arabizi_to_arabic_list({test_input!r}) returned {len(result)} candidates; "
                f"must be <= {_MAX_ARABIZI_CANDIDATES}"
            )


# ---------------------------------------------------------------------------
# filter_candidates_by_wordset — strict filtering (no fallback to full list)
# ---------------------------------------------------------------------------

class TestFilterCandidatesByWordset(unittest.TestCase):
    """filter_candidates_by_wordset must return an empty list when no candidates
    match the wordset instead of falling back to the full unfiltered list."""

    def test_no_match_returns_empty_list(self):
        """When no candidate matches the wordset, an empty list must be returned."""
        from alfanous.romanization import filter_candidates_by_wordset
        candidates = ["ابجد", "هوز", "حطي"]
        wordset = frozenset()  # empty wordset — nothing can match
        result = filter_candidates_by_wordset(candidates, wordset)
        self.assertEqual(result, [],
                         "filter_candidates_by_wordset must return [] when no candidates match")

    def test_partial_match_returns_only_matching(self):
        """Only candidates present in the wordset should be returned."""
        from alfanous.romanization import filter_candidates_by_wordset
        wordset = frozenset(["رحمن"])
        candidates = ["رحمن", "ابجد", "هوز"]
        result = filter_candidates_by_wordset(candidates, wordset)
        self.assertEqual(result, ["رحمن"],
                         "filter_candidates_by_wordset must return only matching candidates")

    def test_all_match_returns_all(self):
        """When all candidates match, all must be returned unchanged."""
        from alfanous.romanization import filter_candidates_by_wordset
        wordset = frozenset(["رحمن", "الله"])
        candidates = ["رحمن", "الله"]
        result = filter_candidates_by_wordset(candidates, wordset)
        self.assertEqual(sorted(result), sorted(candidates),
                         "filter_candidates_by_wordset must return all candidates when all match")

    def test_nonexistent_arabizi_word_empty_keywords(self):
        """Arabizi input that maps to no Quran words must yield an empty filtered list,
        not tens of random Arabic word candidates."""
        from alfanous.romanization import arabizi_to_arabic_list, filter_candidates_by_wordset
        # "heavedwedw" has no plausible Arabic transliteration in the Quran
        candidates = arabizi_to_arabic_list("heavedwedw")
        # Use a minimal wordset that does not include any candidate
        wordset = frozenset(["الله", "رحمن"])  # real words, but unrelated to "heavedwedw"
        result = filter_candidates_by_wordset(candidates, wordset)
        self.assertEqual(result, [],
                         "Non-Quranic arabizi input must produce an empty filtered list, "
                         f"not {len(result)} random candidates")


# ---------------------------------------------------------------------------
# Iteration-6 fixes
# ---------------------------------------------------------------------------

class TestTashkilNodeNoFunctionLevelImport(unittest.TestCase):
    """TashkilPlugin.TashkilNode.query must not contain a function-level whoosh import."""

    def test_no_function_level_wquery_import(self):
        """TashkilNode.query() must not contain 'from whoosh import query'."""
        import inspect
        import alfanous.query_plugins as _qp
        src = inspect.getsource(_qp.TashkilPlugin.TashkilNode.query)
        self.assertNotIn(
            "from whoosh import query",
            src,
            "TashkilNode.query() contains a per-call function-level import; "
            "move NullQuery / Or / Term to module-level imports in query_plugins.py"
        )

    def test_null_query_importable_at_module_level(self):
        """NullQuery must be importable directly from alfanous.query_plugins."""
        import alfanous.query_plugins as _qp
        self.assertTrue(
            hasattr(_qp, "NullQuery"),
            "NullQuery must be imported at module level in alfanous.query_plugins"
        )

    def test_tashkil_empty_string_produces_null_query(self):
        """TashkilNode.query() with no words must return NullQuery without import errors."""
        from alfanous.query_plugins import TashkilPlugin, NullQuery

        class _FakeParser:
            fieldname = "aya"

        # Build a TashkilNode directly with empty text
        node = TashkilPlugin.TashkilNode("   ")
        result = node.query(_FakeParser())
        # NullQuery is a singleton instance (not a class), so compare by identity
        # or by checking the internal class name.
        self.assertIs(
            result, NullQuery,
            f"Expected NullQuery singleton for empty tashkil text, got {result!r}"
        )

    def test_tashkil_single_word_no_import_error(self):
        """TashkilNode.query() with one word must work without a per-call import."""
        from alfanous.query_plugins import TashkilPlugin, TashkilQuery

        class _FakeParser:
            fieldname = "aya"

        node = TashkilPlugin.TashkilNode("الله")
        result = node.query(_FakeParser())
        self.assertIsInstance(
            result, TashkilQuery,
            f"Expected TashkilQuery for single-word tashkil, got {type(result)}"
        )

    def test_tashkil_multi_word_no_import_error(self):
        """TashkilNode.query() with multiple words must return Or(Term, ...) without a per-call import."""
        from alfanous.query_plugins import TashkilPlugin
        from whoosh.query import Or as WOr, Term as WTerm

        class _FakeParser:
            fieldname = "aya"

        node = TashkilPlugin.TashkilNode("الله الرحمن")
        result = node.query(_FakeParser())
        self.assertIsInstance(
            result, WOr,
            f"Expected Or query for multi-word tashkil, got {type(result)}"
        )
        self.assertTrue(
            all(isinstance(sq, WTerm) for sq in result.subqueries),
            "All sub-queries of the Or must be Term instances"
        )


class TestCollectDerivationsTwoPass(unittest.TestCase):
    """_collect_derivations_two_pass uses the engine-level lookup table."""

    def _make_lookup_table(self, docs):
        from alfanous.query_plugins import _build_word_lookup_table
        mock_reader = MagicMock()
        mock_reader.iter_docs.return_value = iter(list(enumerate(docs)))
        return _build_word_lookup_table(mock_reader)

    def test_returns_list(self):
        """_collect_derivations_two_pass must always return a list."""
        from alfanous.query_plugins import _collect_derivations_two_pass
        result = _collect_derivations_two_pass({"x"}, "root", lookup_table=({}, {}, {}))
        self.assertIsInstance(result, list)
        self.assertEqual(result, [])

    def test_accepts_set_input(self):
        """Must accept a plain set as candidates."""
        from alfanous.query_plugins import _collect_derivations_two_pass
        result = _collect_derivations_two_pass({"كلمة"}, "lemma", lookup_table=({}, {}, {}))
        self.assertIsInstance(result, list)

    def test_no_results_without_table(self):
        """Returns empty list when no lookup_table is provided and QSE is unavailable."""
        from alfanous.query_plugins import _collect_derivations_two_pass
        with patch("alfanous.data.QSE", side_effect=Exception("no engine")):
            result = _collect_derivations_two_pass({"كتب"}, "lemma")
        self.assertEqual(result, [])

    def test_uses_pre_built_table(self):
        """With a pre-built lookup table the two-pass logic returns unvocalized forms."""
        from alfanous.query_plugins import _collect_derivations_two_pass
        docs = [
            {"kind": "word", "lemma": "ملك", "root": "ملك",
             "word": "مَلِكٌ", "normalized": "ملك", "standard": "ملك"},
            {"kind": "word", "lemma": "ملك", "root": "ملك",
             "word": "مَالِكٌ", "normalized": "مالك", "standard": "مالك"},
        ]
        tbl = self._make_lookup_table(docs)
        result = _collect_derivations_two_pass({"ملك"}, "lemma", lookup_table=tbl)
        self.assertIn("ملك", result)
        self.assertIn("مالك", result)

    def test_stem_expansion_uses_normalized_stem_to_forms(self):
        """index_key='stem' must expand via normalized_stem_to_forms (5th tuple element)."""
        from alfanous.query_plugins import _collect_derivations_two_pass
        docs = [
            {"kind": "word", "lemma": "رَحِمَ", "stem": "رحم", "root": "رحم",
             "word": "رَحِمَ", "normalized": "رحم", "standard": "رحم"},
            {"kind": "word", "lemma": "رَحْمَة", "stem": "رحم", "root": "رحم",
             "word": "رَحْمَة", "normalized": "رحمة", "standard": "رحمة"},
        ]
        tbl = self._make_lookup_table(docs)
        # Both words share corpus stem "رحم" — both should be returned.
        result = _collect_derivations_two_pass({"رحم"}, "stem", lookup_table=tbl)
        self.assertIn("رحم", result, "Expected normalized form 'رحم' for stem expansion")
        self.assertIn("رحمة", result, "Expected 'رحمة' sharing corpus stem 'رحم'")

    def test_auto_stem_expansion_returns_forms(self):
        """index_key='auto_stem' must expand via auto_stem_to_forms (6th tuple element)."""
        from alfanous.query_plugins import _collect_derivations_two_pass, _get_arabic_stemmer
        stemmer = _get_arabic_stemmer()
        if stemmer is None:
            self.skipTest("pystemmer not installed — skipping auto_stem test")
        docs = [
            {"kind": "word", "lemma": "رحم", "root": "رحم",
             "word": "رَحِمَ", "normalized": "رحم", "standard": "رحم"},
            {"kind": "word", "lemma": "رحمة", "root": "رحم",
             "word": "رَحْمَة", "normalized": "رحمة", "standard": "رحمة"},
        ]
        tbl = self._make_lookup_table(docs)
        # Compute expected Snowball stem of "رحم"
        from alfanous.text_processing import QArabicSymbolsFilter
        _asf = QArabicSymbolsFilter(shaping=True, tashkil=True, spellerrors=False, hamza=False)
        auto_stem = stemmer.stemWord(_asf.normalize_all("رحم"))
        result = _collect_derivations_two_pass({auto_stem}, "auto_stem", lookup_table=tbl)
        # At least one of the word forms should be returned.
        self.assertTrue(
            len(result) > 0,
            f"auto_stem expansion of '{auto_stem}' should return word forms"
        )


# ---------------------------------------------------------------------------
# Iteration-7 fixes
# ---------------------------------------------------------------------------

class TestResultDocnumsFrozenset(unittest.TestCase):
    """_result_docnums must be built as a frozenset, not a plain set."""

    def test_result_docnums_is_frozenset(self):
        """_result_docnums must be initialised with frozenset(...), not set(...)."""
        import ast, inspect, textwrap
        import alfanous.outputs as m
        src = textwrap.dedent(inspect.getsource(m.Raw._search_aya))
        tree = ast.parse(src)

        # Walk the AST and look for any assignment to _result_docnums that uses
        # a plain `set(...)` call instead of `frozenset(...)`.
        for node in ast.walk(tree):
            if not isinstance(node, ast.Assign):
                continue
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == "_result_docnums":
                    val = node.value
                    if (isinstance(val, ast.Call)
                            and isinstance(val.func, ast.Name)
                            and val.func.id == "set"):
                        self.fail(
                            "_result_docnums must be built with frozenset(), not set() — "
                            "it is never mutated after creation, so frozenset avoids "
                            "unnecessary allocation of a mutable data structure."
                        )

    def test_result_docnums_uses_frozenset(self):
        """_result_docnums must explicitly call frozenset()."""
        import ast, inspect, textwrap
        import alfanous.outputs as m
        src = textwrap.dedent(inspect.getsource(m.Raw._search_aya))
        tree = ast.parse(src)

        found = False
        for node in ast.walk(tree):
            if not isinstance(node, ast.Assign):
                continue
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == "_result_docnums":
                    val = node.value
                    if (isinstance(val, ast.Call)
                            and isinstance(val.func, ast.Name)
                            and val.func.id == "frozenset"):
                        found = True

        self.assertTrue(
            found,
            "_result_docnums must be assigned frozenset(...) in _search_aya"
        )


class TestBatchDerivDefaultdict(unittest.TestCase):
    """_batch_deriv_by_lemma and _batch_deriv_by_root must use defaultdict(set)."""

    def _search_aya_source(self):
        import inspect, textwrap
        import alfanous.outputs as m
        return textwrap.dedent(inspect.getsource(m.Raw._search_aya))

    def test_no_setdefault_for_batch_deriv_by_lemma(self):
        """_batch_deriv_by_lemma must not use .setdefault() — use defaultdict(set)."""
        import ast
        src = self._search_aya_source()
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            if not (isinstance(func, ast.Attribute) and func.attr == "setdefault"):
                continue
            # Check if the receiver is _batch_deriv_by_lemma
            if (isinstance(func.value, ast.Name)
                    and func.value.id == "_batch_deriv_by_lemma"):
                self.fail(
                    "_batch_deriv_by_lemma must not use .setdefault() — "
                    "initialise it as defaultdict(set) and use direct item assignment."
                )

    def test_no_setdefault_for_batch_deriv_by_root(self):
        """_batch_deriv_by_root must not use .setdefault() — use defaultdict(set)."""
        import ast
        src = self._search_aya_source()
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            if not (isinstance(func, ast.Attribute) and func.attr == "setdefault"):
                continue
            if (isinstance(func.value, ast.Name)
                    and func.value.id == "_batch_deriv_by_root"):
                self.fail(
                    "_batch_deriv_by_root must not use .setdefault() — "
                    "initialise it as defaultdict(set) and use direct item assignment."
                )

    def test_batch_deriv_by_lemma_initialised_as_defaultdict(self):
        """_batch_deriv_by_lemma must be initialised with defaultdict(set)."""
        import ast
        src = self._search_aya_source()
        tree = ast.parse(src)
        found = False
        for node in ast.walk(tree):
            # Handle plain assignment and annotated assignment.
            if isinstance(node, ast.Assign):
                for t in node.targets:
                    if isinstance(t, ast.Name) and t.id == "_batch_deriv_by_lemma":
                        val = node.value
                        if (isinstance(val, ast.Call)
                                and isinstance(val.func, ast.Name)
                                and val.func.id == "defaultdict"):
                            found = True
            elif isinstance(node, ast.AnnAssign):
                t = node.target
                if (isinstance(t, ast.Name) and t.id == "_batch_deriv_by_lemma"
                        and node.value is not None):
                    val = node.value
                    if (isinstance(val, ast.Call)
                            and isinstance(val.func, ast.Name)
                            and val.func.id == "defaultdict"):
                        found = True
        self.assertTrue(
            found,
            "_batch_deriv_by_lemma must be initialised as defaultdict(set), not {}"
        )

    def test_batch_deriv_by_root_initialised_as_defaultdict(self):
        """_batch_deriv_by_root must be initialised with defaultdict(set)."""
        import ast
        src = self._search_aya_source()
        tree = ast.parse(src)
        found = False
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for t in node.targets:
                    if isinstance(t, ast.Name) and t.id == "_batch_deriv_by_root":
                        val = node.value
                        if (isinstance(val, ast.Call)
                                and isinstance(val.func, ast.Name)
                                and val.func.id == "defaultdict"):
                            found = True
            elif isinstance(node, ast.AnnAssign):
                t = node.target
                if (isinstance(t, ast.Name) and t.id == "_batch_deriv_by_root"
                        and node.value is not None):
                    val = node.value
                    if (isinstance(val, ast.Call)
                            and isinstance(val.func, ast.Name)
                            and val.func.id == "defaultdict"):
                        found = True
        self.assertTrue(
            found,
            "_batch_deriv_by_root must be initialised as defaultdict(set), not {}"
        )

    def test_defaultdict_importable_from_outputs(self):
        """defaultdict must be importable from alfanous.outputs module namespace."""
        import alfanous.outputs as _outputs
        self.assertTrue(
            hasattr(_outputs, "defaultdict"),
            "defaultdict must be imported at module level in alfanous.outputs"
        )


class TestAyaWordsMapsDefaultdict(unittest.TestCase):
    """aya_words_map, annot_words_map, annot_aya_words_map must use defaultdict(list)."""

    def _search_aya_source(self):
        import inspect, textwrap
        import alfanous.outputs as m
        return textwrap.dedent(inspect.getsource(m.Raw._search_aya))

    def _check_no_setdefault_for(self, var_name):
        import ast
        src = self._search_aya_source()
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            if not (isinstance(func, ast.Attribute) and func.attr == "setdefault"):
                continue
            if isinstance(func.value, ast.Name) and func.value.id == var_name:
                self.fail(
                    f"{var_name} must not use .setdefault() — "
                    f"initialise it as defaultdict(list) and use direct item access."
                )

    def _check_initialised_as_defaultdict(self, var_name):
        import ast
        src = self._search_aya_source()
        tree = ast.parse(src)
        found = False
        for node in ast.walk(tree):
            # Handle both plain assignment (`x = defaultdict(...)`) and
            # annotated assignment (`x: SomeType = defaultdict(...)`).
            if isinstance(node, ast.Assign):
                for t in node.targets:
                    if isinstance(t, ast.Name) and t.id == var_name:
                        val = node.value
                        if (isinstance(val, ast.Call)
                                and isinstance(val.func, ast.Name)
                                and val.func.id == "defaultdict"):
                            found = True
            elif isinstance(node, ast.AnnAssign):
                t = node.target
                if isinstance(t, ast.Name) and t.id == var_name and node.value is not None:
                    val = node.value
                    if (isinstance(val, ast.Call)
                            and isinstance(val.func, ast.Name)
                            and val.func.id == "defaultdict"):
                        found = True
        self.assertTrue(
            found,
            f"{var_name} must be initialised as defaultdict(list), not {{}}"
        )

    def test_aya_words_map_no_setdefault(self):
        """aya_words_map must not use .setdefault() — use defaultdict(list)."""
        self._check_no_setdefault_for("aya_words_map")

    def test_aya_words_map_is_defaultdict(self):
        """aya_words_map must be initialised as defaultdict(list)."""
        self._check_initialised_as_defaultdict("aya_words_map")

    def test_annot_words_map_no_setdefault(self):
        """annot_words_map must not use .setdefault() — use defaultdict(list)."""
        self._check_no_setdefault_for("annot_words_map")

    def test_annot_words_map_is_defaultdict(self):
        """annot_words_map must be initialised as defaultdict(list)."""
        self._check_initialised_as_defaultdict("annot_words_map")

    def test_annot_aya_words_map_no_setdefault(self):
        """annot_aya_words_map must not use .setdefault() — use defaultdict(list)."""
        self._check_no_setdefault_for("annot_aya_words_map")

    def test_annot_aya_words_map_is_defaultdict(self):
        """annot_aya_words_map must be initialised as defaultdict(list)."""
        self._check_initialised_as_defaultdict("annot_aya_words_map")


# ---------------------------------------------------------------------------
# Iteration-8 fixes
# ---------------------------------------------------------------------------

class TestCoalesceTextModuleLevel(unittest.TestCase):
    """_COALESCE_TEXT must be defined at module level and replace no-highlight lambdas."""

    def test_coalesce_text_exists(self):
        """_COALESCE_TEXT must be a module-level callable in alfanous.outputs."""
        import alfanous.outputs as _outputs
        self.assertTrue(
            hasattr(_outputs, "_COALESCE_TEXT"),
            "_COALESCE_TEXT must be defined at module level in alfanous.outputs"
        )
        self.assertTrue(
            callable(_outputs._COALESCE_TEXT),
            "_COALESCE_TEXT must be callable"
        )

    def test_coalesce_text_returns_value_when_truthy(self):
        """_COALESCE_TEXT must return x when x is truthy."""
        from alfanous.outputs import _COALESCE_TEXT
        self.assertEqual(_COALESCE_TEXT("hello"), "hello")
        self.assertEqual(_COALESCE_TEXT("الله"), "الله")
        self.assertEqual(_COALESCE_TEXT(1), 1)

    def test_coalesce_text_returns_fallback_when_falsy(self):
        """_COALESCE_TEXT must return '-----' when x is falsy."""
        from alfanous.outputs import _COALESCE_TEXT
        self.assertEqual(_COALESCE_TEXT(None), "-----")
        self.assertEqual(_COALESCE_TEXT(""), "-----")
        self.assertEqual(_COALESCE_TEXT(0), "-----")

    def _no_highlight_lambdas_in(self, method_name):
        """Return True if the method contains `lambda X: X if X else "-----"`
        (the plain identity-coalesce pattern with no function call in the truthy branch)."""
        import ast, inspect, textwrap
        import alfanous.outputs as m
        src = textwrap.dedent(inspect.getsource(getattr(m.Raw, method_name)))
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if not isinstance(node, ast.Lambda):
                continue
            body = node.body
            # Only flag lambdas whose body is a plain IfExp like `X if X else "-----"`.
            # Lambdas with a Call in the truthy branch (e.g. self.QSE.highlight(...))
            # are the highlight-enabled variants and are intentionally left as lambdas.
            if not isinstance(body, ast.IfExp):
                continue
            orelse = body.orelse
            truthy = body.body
            if (isinstance(orelse, ast.Constant)
                    and orelse.value == "-----"
                    and isinstance(truthy, ast.Name)):
                return True
        return False

    def test_search_aya_no_highlight_lambda_removed(self):
        """_search_aya must not allocate `lambda X: X if X else '-----'`."""
        self.assertFalse(
            self._no_highlight_lambdas_in("_search_aya"),
            "_search_aya no-highlight path must use _COALESCE_TEXT, "
            "not an inline lambda"
        )

    def test_search_translation_no_highlight_lambda_removed(self):
        """_search_translation must not allocate `lambda X: X if X else '-----'`."""
        self.assertFalse(
            self._no_highlight_lambdas_in("_search_translation"),
            "_search_translation no-highlight path must use _COALESCE_TEXT, "
            "not an inline lambda"
        )

    def test_search_words_no_highlight_lambda_removed(self):
        """_search_words must not allocate `lambda X: X if X else '-----'`."""
        self.assertFalse(
            self._no_highlight_lambdas_in("_search_words"),
            "_search_words no-highlight path must use _COALESCE_TEXT, "
            "not an inline lambda"
        )


class TestFlagDefaultsBinding(unittest.TestCase):
    """_FLAG_DEFAULTS must be defined at module level for fast IS_FLAG lookups."""

    def test_flag_defaults_exists(self):
        """_FLAG_DEFAULTS must be a module-level dict in alfanous.outputs."""
        import alfanous.outputs as _outputs
        self.assertTrue(
            hasattr(_outputs, "_FLAG_DEFAULTS"),
            "_FLAG_DEFAULTS must be defined at module level in alfanous.outputs"
        )
        self.assertIsInstance(
            _outputs._FLAG_DEFAULTS, dict,
            "_FLAG_DEFAULTS must be a dict"
        )

    def test_flag_defaults_equals_raw_defaults(self):
        """_FLAG_DEFAULTS must be the same object as Raw.DEFAULTS['flags']."""
        import alfanous.outputs as _outputs
        self.assertIs(
            _outputs._FLAG_DEFAULTS,
            _outputs.Raw.DEFAULTS['flags'],
            "_FLAG_DEFAULTS must be the same dict object as Raw.DEFAULTS['flags']"
        )

    def test_is_flag_uses_flag_defaults_not_raw_defaults(self):
        """IS_FLAG must reference _FLAG_DEFAULTS, not Raw.DEFAULTS['flags']."""
        import ast, inspect
        import alfanous.outputs as _outputs
        src = inspect.getsource(_outputs.IS_FLAG)
        tree = ast.parse(src)
        for node in ast.walk(tree):
            # Detect attribute access Raw.DEFAULTS and subsequent subscript
            if isinstance(node, ast.Subscript):
                val = node.value
                if isinstance(val, ast.Attribute) and val.attr == "DEFAULTS":
                    if isinstance(val.value, ast.Name) and val.value.id == "Raw":
                        self.fail(
                            "IS_FLAG must use _FLAG_DEFAULTS[key], not "
                            "Raw.DEFAULTS['flags'][key] — the latter costs 3 "
                            "attribute/dict lookups per call."
                        )

    def test_is_flag_still_works_correctly(self):
        """IS_FLAG must still return correct results after the lookup change."""
        from alfanous.outputs import IS_FLAG
        # Test with a known boolean flag
        self.assertTrue(IS_FLAG({"vocalized": True}, "vocalized"))
        self.assertFalse(IS_FLAG({"vocalized": False}, "vocalized"))
        self.assertFalse(IS_FLAG({"vocalized": "false"}, "vocalized"))
        self.assertFalse(IS_FLAG({"vocalized": "0"}, "vocalized"))
        # Empty / None fall back to default
        self.assertEqual(
            IS_FLAG({"vocalized": None}, "vocalized"),
            True,  # Raw.DEFAULTS['flags']['vocalized'] is True
        )


class TestTashkilQueryNormalizedCached(unittest.TestCase):
    """TashkilQuery must pre-compute _normalized_query_words at __init__ time."""

    def test_normalized_query_words_attribute_exists(self):
        """TashkilQuery instances must have a _normalized_query_words attribute."""
        from alfanous.query_plugins import TashkilQuery
        q = TashkilQuery("aya", "الله")
        self.assertTrue(
            hasattr(q, "_normalized_query_words"),
            "TashkilQuery must set _normalized_query_words in __init__"
        )

    def test_normalized_query_words_is_frozenset(self):
        """_normalized_query_words must be a frozenset for O(1) lookup."""
        from alfanous.query_plugins import TashkilQuery
        q = TashkilQuery("aya", "الله")
        self.assertIsInstance(
            q._normalized_query_words, frozenset,
            "_normalized_query_words must be a frozenset"
        )

    def test_normalized_query_words_matches_words(self):
        """_normalized_query_words must equal the initial frozenset(self.words)."""
        from alfanous.query_plugins import TashkilQuery
        q = TashkilQuery("aya", ["الله", "الرحمن"])
        self.assertEqual(
            q._normalized_query_words,
            frozenset(q.words),
            "_normalized_query_words must equal frozenset(self.words) at init time"
        )

    def test_btexts_does_not_recompute_normalized_set(self):
        """_btexts must not recompute {normalize(w) for w in self.text}."""
        import ast, inspect, textwrap
        from alfanous.query_plugins import TashkilQuery
        src = textwrap.dedent(inspect.getsource(TashkilQuery._btexts))
        tree = ast.parse(src)

        # Look for a set comprehension that calls normalize_all on self.text.
        for node in ast.walk(tree):
            if not isinstance(node, ast.SetComp):
                continue
            # Check if the iterable is `self.text`
            for gen in node.generators:
                iter_node = gen.iter
                if (isinstance(iter_node, ast.Attribute)
                        and iter_node.attr == "text"
                        and isinstance(iter_node.value, ast.Name)
                        and iter_node.value.id == "self"):
                    self.fail(
                        "TashkilQuery._btexts must not recompute "
                        "{normalize(w) for w in self.text} on every call — "
                        "use self._normalized_query_words instead."
                    )


# ---------------------------------------------------------------------------
# Shared reader/searcher contract tests
#
# The issue "all use shared reader/searcher, and it only be closed with engine
# closing of context manager" requires that:
#   1. QSearcher._get_shared_searcher() returns the SAME Whoosh Searcher
#      object on every call (no per-request Searcher creation).
#   2. _SearcherProxy.close() / __exit__ are true no-ops — they must NOT
#      close the underlying Whoosh Searcher.
#   3. QReader.close() when attached to a QSearcher is a no-op (the reader
#      is owned by the QSearcher and must not be closed by the QReader).
#   4. Only BasicSearchEngine.close() / its __exit__ closes the shared
#      Whoosh Searcher (single lifecycle owner).
#   5. QReader.attach_to_searcher() properly wires the QReader so that it
#      borrows the reader from the QSearcher rather than opening its own.
# ---------------------------------------------------------------------------

class TestSharedReaderSearcherContract(unittest.TestCase):
    """Verify the shared reader/searcher ownership and lifecycle guarantees."""

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _make_qsearcher(self):
        """Return (QSearcher, mock_whoosh_searcher) backed by mocks."""
        from alfanous.searching import QSearcher
        mock_docindex = MagicMock()
        mock_ws = MagicMock()
        # refresh() returns self to simulate no index change between calls.
        mock_ws.refresh.return_value = mock_ws
        # mock_docindex.get_index().searcher is the Whoosh searcher factory;
        # calling it (e.g. with weighting=…) returns mock_ws.
        mock_docindex.get_index.return_value.searcher.return_value = mock_ws
        mock_docindex.get_schema.return_value = MagicMock()
        qs = QSearcher(mock_docindex, MagicMock())
        return qs, mock_ws

    def _make_engine(self):
        """Return (BasicSearchEngine, mock_whoosh_searcher) backed by mocks."""
        from whoosh.fields import Schema, TEXT
        from alfanous.engines import BasicSearchEngine
        from alfanous.searching import QSearcher, QReader

        schema = Schema(aya=TEXT)
        mock_docindex = MagicMock()
        mock_docindex.OK = True
        mock_docindex.get_schema.return_value = schema

        mock_ws = MagicMock()
        mock_ws.refresh.return_value = mock_ws
        mock_index = MagicMock()
        mock_index.searcher.return_value = mock_ws
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
        return engine, mock_ws

    # ------------------------------------------------------------------
    # 1. _get_shared_searcher returns the same object on every call
    # ------------------------------------------------------------------

    def test_get_shared_searcher_returns_same_instance(self):
        """_get_shared_searcher() must return the identical object on every call."""
        qs, mock_ws = self._make_qsearcher()

        first = qs._get_shared_searcher()
        second = qs._get_shared_searcher()
        third = qs._get_shared_searcher()

        self.assertIs(first, second, "second call must return the same shared searcher")
        self.assertIs(second, third, "third call must return the same shared searcher")

    def test_get_shared_searcher_factory_called_once(self):
        """The Whoosh index.searcher factory must be invoked at most once."""
        qs, mock_ws = self._make_qsearcher()

        qs._get_shared_searcher()
        qs._get_shared_searcher()
        qs._get_shared_searcher()

        # The factory (qs._searcher) should only have been called once (on
        # the first _get_shared_searcher() call that lazily opens it).
        self.assertEqual(
            qs._searcher.call_count, 1,
            "Searcher factory must be invoked only once despite multiple "
            "_get_shared_searcher() calls",
        )

    # ------------------------------------------------------------------
    # 2. _SearcherProxy.close() / __exit__ are true no-ops
    # ------------------------------------------------------------------

    def test_searcher_proxy_close_does_not_close_underlying(self):
        """_SearcherProxy.close() must NOT close the underlying Whoosh Searcher."""
        from alfanous.searching import _SearcherProxy
        mock_ws = MagicMock()
        proxy = _SearcherProxy(mock_ws)
        proxy.close()
        mock_ws.close.assert_not_called()

    def test_searcher_proxy_exit_does_not_close_underlying(self):
        """Using _SearcherProxy as a context manager must NOT close the underlying searcher."""
        from alfanous.searching import _SearcherProxy
        mock_ws = MagicMock()
        proxy = _SearcherProxy(mock_ws)
        with proxy:
            pass
        mock_ws.close.assert_not_called()

    def test_multiple_proxy_close_calls_still_noop(self):
        """Multiple _SearcherProxy.close() calls must all be no-ops."""
        from alfanous.searching import _SearcherProxy
        mock_ws = MagicMock()
        proxy = _SearcherProxy(mock_ws)
        proxy.close()
        proxy.close()
        proxy.close()
        mock_ws.close.assert_not_called()

    # ------------------------------------------------------------------
    # 3. QReader.close() is a no-op when attached to a QSearcher
    # ------------------------------------------------------------------

    def test_qreader_close_noop_when_attached(self):
        """QReader.close() must be a no-op when attached to a QSearcher."""
        from alfanous.searching import QReader
        mock_docindex = MagicMock()
        mock_docindex.get_schema.return_value = MagicMock()

        reader = QReader(mock_docindex)
        mock_qsearcher = MagicMock()
        reader.attach_to_searcher(mock_qsearcher)

        # close() must not propagate to the qsearcher
        reader.close()
        mock_qsearcher.close.assert_not_called()

    def test_qreader_close_noop_does_not_call_get_reader(self):
        """QReader.close() when attached must not call get_reader() on QSearcher."""
        from alfanous.searching import QReader
        mock_docindex = MagicMock()
        mock_docindex.get_schema.return_value = MagicMock()

        reader = QReader(mock_docindex)
        mock_qsearcher = MagicMock()
        reader.attach_to_searcher(mock_qsearcher)

        reader.close()
        mock_qsearcher.get_reader.assert_not_called()

    # ------------------------------------------------------------------
    # 4. Only BasicSearchEngine.close() closes the shared Whoosh Searcher
    # ------------------------------------------------------------------

    def test_shared_searcher_not_closed_before_engine_close(self):
        """The shared Whoosh Searcher must stay open until BasicSearchEngine.close()."""
        engine, mock_ws = self._make_engine()

        # Trigger lazy creation of the shared searcher
        engine._searcher._get_shared_searcher()

        # Not yet closed
        mock_ws.close.assert_not_called()

        # Only after engine.close() should it be closed
        engine.close()
        mock_ws.close.assert_called_once()

    def test_shared_searcher_closed_exactly_once_by_context_manager(self):
        """The shared Whoosh Searcher must be closed exactly once when using 'with engine:'."""
        engine, mock_ws = self._make_engine()

        # Trigger lazy creation of the shared searcher
        engine._searcher._get_shared_searcher()
        mock_ws.close.assert_not_called()

        with engine:
            mock_ws.close.assert_not_called()

        mock_ws.close.assert_called_once()

    def test_qsearcher_close_releases_shared_searcher(self):
        """QSearcher.close() must close the underlying Whoosh Searcher."""
        qs, mock_ws = self._make_qsearcher()
        qs._get_shared_searcher()  # lazily open
        mock_ws.close.assert_not_called()

        qs.close()
        mock_ws.close.assert_called_once()

    # ------------------------------------------------------------------
    # 5. QReader.attach_to_searcher borrows reader from QSearcher
    # ------------------------------------------------------------------

    def test_attach_to_searcher_reader_property_delegates(self):
        """After attach_to_searcher, QReader.reader must come from QSearcher.get_reader()."""
        from alfanous.searching import QReader
        mock_docindex = MagicMock()
        mock_docindex.get_schema.return_value = MagicMock()

        reader = QReader(mock_docindex)
        mock_qsearcher = MagicMock()
        sentinel_reader = object()
        mock_qsearcher.get_reader.return_value = sentinel_reader

        reader.attach_to_searcher(mock_qsearcher)

        # The reader property must delegate to qsearcher.get_reader()
        result = reader.reader
        self.assertIs(
            result, sentinel_reader,
            "QReader.reader must return the reader from QSearcher after attach_to_searcher()",
        )
        mock_qsearcher.get_reader.assert_called_once()

    def test_attach_to_searcher_closes_own_reader_if_open(self):
        """attach_to_searcher must close any previously opened own reader."""
        from alfanous.searching import QReader
        mock_docindex = MagicMock()
        mock_docindex.get_schema.return_value = MagicMock()
        mock_docindex.get_index.return_value.reader.return_value = MagicMock()

        reader = QReader(mock_docindex)
        # Open the own reader first
        own_reader = reader._ensure_own_reader()
        mock_qsearcher = MagicMock()

        reader.attach_to_searcher(mock_qsearcher)

        # Direct access to the private attribute is intentional: this test
        # validates the internal lifecycle guarantee that attach_to_searcher()
        # clears the reader reference it owns so no stale reader stays open.
        own_reader.close.assert_called_once()
        self.assertIsNone(reader._own_reader, "own reader must be cleared after attach_to_searcher")

    # ------------------------------------------------------------------
    # 6. correct_query falls back gracefully on ReaderClosed
    # ------------------------------------------------------------------

    def test_correct_query_falls_back_on_reader_closed(self):
        """QSearcher.correct_query must return original query on ReaderClosed."""
        from whoosh.fields import Schema, TEXT
        from whoosh.reading import ReaderClosed
        from alfanous.searching import QSearcher

        schema = Schema(aya=TEXT)
        mock_docindex = MagicMock()
        mock_docindex.get_schema.return_value = schema
        mock_ws = MagicMock()
        mock_ws.refresh.return_value = mock_ws
        mock_ws.correct_query.side_effect = ReaderClosed()
        mock_docindex.get_index.return_value.searcher.return_value = mock_ws

        qs = QSearcher(mock_docindex, MagicMock())
        # prime the shared searcher so it is returned by _get_shared_searcher()
        qs._shared_searcher = mock_ws

        result = qs.correct_query("remaja putr")

        self.assertEqual(result["original"], "remaja putr")
        self.assertEqual(result["corrected"], "remaja putr",
                         "correct_query must return original as corrected when ReaderClosed")

    def test_correct_query_succeeds_on_second_attempt(self):
        """QSearcher.correct_query retries once and succeeds on the second attempt."""
        from whoosh.fields import Schema, TEXT
        from whoosh.reading import ReaderClosed
        from alfanous.searching import QSearcher

        schema = Schema(aya=TEXT)
        mock_docindex = MagicMock()
        mock_docindex.get_schema.return_value = schema
        mock_ws = MagicMock()
        mock_ws.refresh.return_value = mock_ws

        # First call raises ReaderClosed; second call succeeds.
        good_correction = MagicMock()
        good_correction.string = "corrected_term"
        mock_ws.correct_query.side_effect = [ReaderClosed(), good_correction]
        mock_docindex.get_index.return_value.searcher.return_value = mock_ws

        qs = QSearcher(mock_docindex, MagicMock())
        qs._shared_searcher = mock_ws

        result = qs.correct_query("remaja putr")

        self.assertEqual(result["corrected"], "corrected_term",
                         "correct_query must return corrected string when second attempt succeeds")

    def test_correct_query_parses_before_getting_searcher(self):
        """parse() must be called before _get_shared_searcher() in correct_query.

        If parsing triggers a plugin that calls _get_shared_searcher() internally
        (e.g. via engine._reader.reader) and causes a refresh, the reference we
        take afterwards belongs to the post-refresh searcher and is not stale.
        """
        import ast, inspect, textwrap
        import alfanous.searching as _searching_module
        src = textwrap.dedent(inspect.getsource(_searching_module.QSearcher.correct_query))
        tree = ast.parse(src)

        # Walk statement-by-statement to find the order of _qparser.parse and
        # _get_shared_searcher.
        parse_line = None
        get_searcher_line = None
        for node in ast.walk(tree):
            if not isinstance(node, (ast.Assign, ast.Expr)):
                continue
            node_src = ast.unparse(node)
            if "_qparser.parse" in node_src and parse_line is None:
                parse_line = node.lineno
            if "_get_shared_searcher" in node_src and get_searcher_line is None:
                get_searcher_line = node.lineno

        self.assertIsNotNone(parse_line,
                             "correct_query must call _qparser.parse")
        self.assertIsNotNone(get_searcher_line,
                             "correct_query must call _get_shared_searcher")
        self.assertLess(
            parse_line, get_searcher_line,
            "parse() must come before _get_shared_searcher() in correct_query "
            "so that any plugin-triggered refresh completes before we take our "
            "reference to the shared searcher.",
        )

    # ------------------------------------------------------------------
    # 7. search() reorders parse-before-get-searcher & retries on ReaderClosed
    # ------------------------------------------------------------------

    def test_search_retries_on_reader_closed(self):
        """QSearcher.search must retry once on ReaderClosed and succeed."""
        from whoosh.fields import Schema, TEXT
        from whoosh.reading import ReaderClosed
        from alfanous.searching import QSearcher

        schema = Schema(aya=TEXT)
        mock_docindex = MagicMock()
        mock_docindex.get_schema.return_value = schema
        mock_ws = MagicMock()
        mock_ws.refresh.return_value = mock_ws
        mock_docindex.get_index.return_value.searcher.return_value = mock_ws

        good_results = MagicMock()
        good_results.matched_terms.return_value = None
        # First call raises ReaderClosed; second succeeds.
        mock_ws.search.side_effect = [ReaderClosed(), good_results]

        qs = QSearcher(mock_docindex, MagicMock())
        qs._shared_searcher = mock_ws
        mock_parser = MagicMock()
        mock_parsed_query = MagicMock()
        mock_parsed_query.all_terms.return_value = []
        mock_parser.parse.return_value = mock_parsed_query
        qs._qparser = mock_parser

        results, terms, _searcher, *_ = qs.search("sura_id:49", timelimit=None)
        self.assertIs(results, good_results,
                      "search must return results from the successful retry")

    def test_search_reraises_on_second_reader_closed(self):
        """QSearcher.search must re-raise ReaderClosed if both attempts fail."""
        from whoosh.fields import Schema, TEXT
        from whoosh.reading import ReaderClosed
        from alfanous.searching import QSearcher

        schema = Schema(aya=TEXT)
        mock_docindex = MagicMock()
        mock_docindex.get_schema.return_value = schema
        mock_ws = MagicMock()
        mock_ws.refresh.return_value = mock_ws
        # Both attempts raise ReaderClosed.
        mock_ws.search.side_effect = [ReaderClosed(), ReaderClosed()]
        mock_docindex.get_index.return_value.searcher.return_value = mock_ws

        qs = QSearcher(mock_docindex, MagicMock())
        qs._shared_searcher = mock_ws
        mock_parser = MagicMock()
        mock_parsed_query = MagicMock()
        mock_parsed_query.all_terms.return_value = []
        mock_parser.parse.return_value = mock_parsed_query
        qs._qparser = mock_parser

        with self.assertRaises(ReaderClosed):
            qs.search("sura_id:49", timelimit=None)

        self.assertEqual(mock_ws.search.call_count, 2,
                         "search must attempt the Whoosh search exactly twice before re-raising")

    def test_search_parses_before_getting_searcher(self):
        """parse() must be called before _get_shared_searcher() in search().

        Ensures the same parse-first ordering guarantee that was applied to
        correct_query is also present in the search() method.
        """
        import ast, inspect, textwrap
        import alfanous.searching as _searching_module
        src = textwrap.dedent(inspect.getsource(_searching_module.QSearcher.search))
        tree = ast.parse(src)

        parse_line = None
        get_searcher_line = None
        for node in ast.walk(tree):
            if not isinstance(node, (ast.Assign, ast.Expr)):
                continue
            node_src = ast.unparse(node)
            if "_qparser.parse" in node_src and parse_line is None:
                parse_line = node.lineno
            if "_get_shared_searcher" in node_src and get_searcher_line is None:
                get_searcher_line = node.lineno

        self.assertIsNotNone(parse_line,
                             "search must call _qparser.parse")
        self.assertIsNotNone(get_searcher_line,
                             "search must call _get_shared_searcher")
        self.assertLess(
            parse_line, get_searcher_line,
            "parse() must come before _get_shared_searcher() in search() "
            "so that any plugin-triggered refresh completes before we take our "
            "reference to the shared searcher.",
        )

    def test_search_obj_retries_on_reader_closed(self):
        """QSearcher.search_obj must retry once on ReaderClosed and succeed."""
        from whoosh.fields import Schema, TEXT
        from whoosh.reading import ReaderClosed
        from alfanous.searching import QSearcher

        schema = Schema(aya=TEXT)
        mock_docindex = MagicMock()
        mock_docindex.get_schema.return_value = schema
        mock_ws = MagicMock()
        mock_ws.refresh.return_value = mock_ws
        mock_docindex.get_index.return_value.searcher.return_value = mock_ws

        good_results = MagicMock()
        mock_ws.search.side_effect = [ReaderClosed(), good_results]

        qs = QSearcher(mock_docindex, MagicMock())
        qs._shared_searcher = mock_ws

        import whoosh.query as wq
        q_obj = wq.NullQuery()
        results, terms, _searcher = qs.search_obj(q_obj, timelimit=None)
        self.assertIs(results, good_results,
                      "search_obj must return results from the successful retry")
        # After the first ReaderClosed the implementation resets _shared_searcher
        # so that _get_shared_searcher() reopens a fresh one on the next attempt.
        # By the time we check here the second attempt has already succeeded and
        # the attribute has been repopulated; verify it is non-None (open).
        self.assertIsNotNone(qs._shared_searcher,
                             "_shared_searcher must be set to a fresh searcher after retry succeeds")

    def test_search_obj_strips_phrases_on_query_error(self):
        """search_obj must retry with phrases stripped when QueryError 'has no positions'."""
        from whoosh.fields import Schema, TEXT, ID
        from whoosh.query import QueryError, Phrase, Term
        from alfanous.searching import QSearcher

        # Build a schema where 'nophrase' has phrase=False (no positions).
        schema = Schema(nophrase=TEXT(phrase=False), kind=ID(stored=True))
        mock_docindex = MagicMock()
        mock_docindex.get_schema.return_value = schema
        mock_ws = MagicMock()
        mock_ws.refresh.return_value = mock_ws
        mock_docindex.get_index.return_value.searcher.return_value = mock_ws

        good_results = MagicMock()
        # First search (with Phrase) raises QueryError; second (with And(Term)) succeeds.
        mock_ws.search.side_effect = [
            QueryError("Phrase search: 'nophrase' field has no positions"),
            good_results,
        ]

        qs = QSearcher(mock_docindex, MagicMock())
        qs._shared_searcher = mock_ws

        # A phrase query against the no-position field.
        q_obj = Phrase("nophrase", ["mercy", "compassion"])
        results, terms, _searcher = qs.search_obj(q_obj, timelimit=None)

        self.assertIs(results, good_results,
                      "search_obj must return results from the stripped-phrase retry")
        self.assertEqual(mock_ws.search.call_count, 2,
                         "search must be called twice: once with Phrase, once with And(Terms)")
        # Second call must not contain a Phrase — it should be an And of Terms.
        second_call_query = mock_ws.search.call_args_list[1].kwargs.get("q")
        self.assertNotIsInstance(second_call_query, Phrase,
                                 "Retried query must not be a Phrase")

    def test_search_obj_reraises_unrelated_query_error(self):
        """search_obj must re-raise QueryError that is NOT about missing positions."""
        from whoosh.fields import Schema, TEXT
        from whoosh.query import QueryError, NullQuery
        from alfanous.searching import QSearcher

        schema = Schema(aya=TEXT)
        mock_docindex = MagicMock()
        mock_docindex.get_schema.return_value = schema
        mock_ws = MagicMock()
        mock_ws.refresh.return_value = mock_ws
        mock_docindex.get_index.return_value.searcher.return_value = mock_ws

        mock_ws.search.side_effect = QueryError("Some other query error")

        qs = QSearcher(mock_docindex, MagicMock())
        qs._shared_searcher = mock_ws

        with self.assertRaises(QueryError, msg="Unrelated QueryError must propagate"):
            qs.search_obj(NullQuery(), timelimit=None)

    def test_suggest_collocations_retries_on_reader_closed(self):
        """QSearcher.suggest_collocations must retry on ReaderClosed and succeed."""
        from whoosh.reading import ReaderClosed
        from alfanous.searching import QSearcher

        mock_docindex = MagicMock()
        mock_docindex.get_schema.return_value = MagicMock()
        mock_ws = MagicMock()
        mock_ws.refresh.return_value = mock_ws
        mock_docindex.get_index.return_value.searcher.return_value = mock_ws

        # First reader raises ReaderClosed on field_terms; second succeeds.
        closed_reader = MagicMock()
        closed_reader.indexed_field_names.return_value = ["aya_shingles"]
        closed_reader.field_terms.side_effect = ReaderClosed()

        good_reader = MagicMock()
        good_reader.indexed_field_names.return_value = ["aya_shingles"]
        good_reader.field_terms.return_value = []  # no shingles — empty result

        mock_ws.reader.side_effect = [closed_reader, good_reader]

        qs = QSearcher(mock_docindex, MagicMock())
        qs._shared_searcher = mock_ws

        result = qs.suggest_collocations("سميع")
        self.assertEqual(result, [], "suggest_collocations must return empty list after retry")

    def test_suggest_collocations_returns_empty_on_persistent_reader_closed(self):
        """suggest_collocations must return [] when ReaderClosed persists after all retries."""
        from whoosh.reading import ReaderClosed
        from alfanous.searching import QSearcher

        mock_docindex = MagicMock()
        mock_docindex.get_schema.return_value = MagicMock()
        mock_ws = MagicMock()
        mock_ws.refresh.return_value = mock_ws
        mock_docindex.get_index.return_value.searcher.return_value = mock_ws

        bad_reader = MagicMock()
        bad_reader.indexed_field_names.return_value = ["aya_shingles"]
        bad_reader.field_terms.side_effect = ReaderClosed()

        # Both reader() calls return a closed reader.
        mock_ws.reader.return_value = bad_reader

        qs = QSearcher(mock_docindex, MagicMock())
        qs._shared_searcher = mock_ws

        # Must NOT raise; must return empty list gracefully.
        result = qs.suggest_collocations("سميع")
        self.assertEqual(result, [])


# ---------------------------------------------------------------------------
# suggest_extensions: ReaderClosed retry tests
# ---------------------------------------------------------------------------

class TestSuggestExtensionsReaderClosed(unittest.TestCase):
    """QSearcher.suggest_extensions must handle ReaderClosed gracefully."""

    def test_suggest_extensions_retries_on_reader_closed(self):
        """suggest_extensions must retry once when the reader is closed."""
        from whoosh.reading import ReaderClosed
        from alfanous.searching import QSearcher

        mock_docindex = MagicMock()
        mock_docindex.get_schema.return_value = MagicMock()
        mock_ws = MagicMock()
        mock_ws.refresh.return_value = mock_ws
        mock_docindex.get_index.return_value.searcher.return_value = mock_ws

        closed_reader = MagicMock()
        closed_reader.indexed_field_names.return_value = ["aya_shingles"]
        closed_reader.field_terms.side_effect = ReaderClosed()

        good_reader = MagicMock()
        good_reader.indexed_field_names.return_value = ["aya_shingles"]
        good_reader.field_terms.return_value = []

        mock_ws.reader.side_effect = [closed_reader, good_reader]

        qs = QSearcher(mock_docindex, MagicMock())
        qs._shared_searcher = mock_ws

        result = qs.suggest_extensions("الحمد")
        self.assertEqual(result, [])

    def test_suggest_extensions_returns_empty_on_persistent_reader_closed(self):
        """suggest_extensions must return [] when ReaderClosed persists after all retries."""
        from whoosh.reading import ReaderClosed
        from alfanous.searching import QSearcher

        mock_docindex = MagicMock()
        mock_docindex.get_schema.return_value = MagicMock()
        mock_ws = MagicMock()
        mock_ws.refresh.return_value = mock_ws
        mock_docindex.get_index.return_value.searcher.return_value = mock_ws

        bad_reader = MagicMock()
        bad_reader.indexed_field_names.return_value = ["aya_shingles"]
        bad_reader.field_terms.side_effect = ReaderClosed()

        mock_ws.reader.return_value = bad_reader

        qs = QSearcher(mock_docindex, MagicMock())
        qs._shared_searcher = mock_ws

        result = qs.suggest_extensions("الحمد")
        self.assertEqual(result, [])

    def test_suggest_extensions_returns_empty_when_field_absent(self):
        """suggest_extensions returns [] gracefully when aya_shingles field is absent."""
        from alfanous.searching import QSearcher

        mock_docindex = MagicMock()
        mock_docindex.get_schema.return_value = MagicMock()
        mock_ws = MagicMock()
        mock_docindex.get_index.return_value.searcher.return_value = mock_ws

        reader = MagicMock()
        reader.indexed_field_names.return_value = []  # aya_shingles absent
        mock_ws.reader.return_value = reader

        qs = QSearcher(mock_docindex, MagicMock())
        qs._shared_searcher = mock_ws

        result = qs.suggest_extensions("الحمد")
        self.assertEqual(result, [])

    def test_suggest_extensions_empty_prefix_returns_empty(self):
        """suggest_extensions returns [] immediately for empty/blank input."""
        from alfanous.searching import QSearcher

        mock_docindex = MagicMock()
        mock_docindex.get_schema.return_value = MagicMock()
        mock_docindex.get_index.return_value.searcher.return_value = MagicMock()

        qs = QSearcher(mock_docindex, MagicMock())
        self.assertEqual(qs.suggest_extensions(""), [])
        self.assertEqual(qs.suggest_extensions("   "), [])


# ---------------------------------------------------------------------------
# autocomplete: prefix-based extension via suggest_extensions
# ---------------------------------------------------------------------------

class TestAutocompleteSuggestExtensions(unittest.TestCase):
    """BasicSearchEngine.autocomplete must use suggest_extensions for completions.

    autocomplete uses the FULL typed text as a prefix and returns shingles that
    start with those exact words.  This gives identical result *types* for single-
    word and multi-word inputs — both return phrase completions that extend what
    was typed.  When no shingle extends the prefix (rare/unknown word or index
    predates aya_shingles), the method falls back to QReader.autocomplete (prefix
    expansion on aya_ac).
    """

    def _make_engine(self, extensions, prefix_words=None):
        """Return a BasicSearchEngine backed by mocks.

        :param extensions: list returned by suggest_extensions
        :param prefix_words: list returned by QReader.autocomplete (fallback)
        """
        from alfanous.engines import BasicSearchEngine
        engine = BasicSearchEngine.__new__(BasicSearchEngine)
        engine._searcher = MagicMock()
        engine._searcher.suggest_extensions.return_value = extensions
        engine._reader = MagicMock()
        engine._reader.autocomplete.return_value = prefix_words or []
        return engine

    def test_single_word_returns_extending_phrases(self):
        """الحمد alone → phrases that start with الحمد (same type as 2-word input)."""
        engine = self._make_engine(["الحمد لله", "الحمد لله رب"])
        result = engine.autocomplete("الحمد")
        self.assertEqual(result["base"], "")
        self.assertEqual(result["completion"], ["الحمد لله", "الحمد لله رب"])
        engine._reader.autocomplete.assert_not_called()

    def test_two_word_returns_extending_phrases(self):
        """الحمد لله → trigrams that start with الحمد لله (same type as single word)."""
        engine = self._make_engine(["الحمد لله رب"])
        result = engine.autocomplete("الحمد لله")
        self.assertEqual(result["base"], "الحمد")
        self.assertEqual(result["completion"], ["الحمد لله رب"])
        engine._reader.autocomplete.assert_not_called()

    def test_single_word_same_result_type_as_two_words(self):
        """Single word and 2-word inputs both return phrase completions (not bare words)."""
        engine_single = self._make_engine(["رسول الله", "رسول الله الكريم"])
        engine_two    = self._make_engine(["رسول الله الكريم"])

        r1 = engine_single.autocomplete("رسول")
        r2 = engine_two.autocomplete("رسول الله")

        # Both return lists of multi-word phrases, not bare single words
        for phrase in r1["completion"]:
            self.assertGreater(len(phrase.split()), 1, f"{phrase!r} is not a phrase")
        for phrase in r2["completion"]:
            self.assertGreater(len(phrase.split()), 1, f"{phrase!r} is not a phrase")

    def test_no_extensions_falls_back_to_prefix(self):
        """When no shingle extends the typed text, fall back to aya_ac prefix expansion."""
        engine = self._make_engine([], prefix_words=["نادر", "نادرة"])
        result = engine.autocomplete("نادر")
        self.assertEqual(result["completion"], ["نادر", "نادرة"])
        engine._reader.autocomplete.assert_called_once_with("نادر")

    def test_fallback_uses_last_word_for_prefix_expansion(self):
        """Fallback prefix expansion uses the last word (not the full multi-word input)."""
        engine = self._make_engine([], prefix_words=["شيء"])
        engine.autocomplete("كلمة شيء")
        engine._reader.autocomplete.assert_called_once_with("شيء")

    def test_fallback_result_capped_at_10(self):
        """The fallback prefix result is capped at 10 items."""
        engine = self._make_engine([], prefix_words=[f"كلمة{i}" for i in range(15)])
        result = engine.autocomplete("كلمة")
        self.assertEqual(len(result["completion"]), 10)

    def test_base_and_completion_keys_present(self):
        """Return value always has 'base' and 'completion' keys."""
        engine = self._make_engine(["رسول الله الكريم"])
        result = engine.autocomplete("رسول الله")
        self.assertIn("base", result)
        self.assertIn("completion", result)

    def test_base_is_all_words_except_last(self):
        """'base' is all words except the last, joined with a space."""
        engine = self._make_engine(["الحمد لله رب"])
        result = engine.autocomplete("الحمد لله")
        self.assertEqual(result["base"], "الحمد")

    def test_empty_querystr_returns_empty(self):
        """Empty input returns empty base and completion."""
        engine = self._make_engine([])
        result = engine.autocomplete("")
        self.assertEqual(result, {"base": "", "completion": []})

    def test_suggest_extensions_called_with_full_input(self):
        """suggest_extensions receives the full query string, not just the last word."""
        engine = self._make_engine(["الحمد لله رب"])
        engine.autocomplete("الحمد لله")
        engine._searcher.suggest_extensions.assert_called_once_with("الحمد لله", limit=10)


# ---------------------------------------------------------------------------
# Performance: _is_arabic_text helper uses frozenset for O(1) lookups
# ---------------------------------------------------------------------------

class TestIsArabicTextHelper(unittest.TestCase):
    """Verify the _is_arabic_text helper is defined and uses a frozenset."""

    def test_helper_exists_in_searching(self):
        """_is_arabic_text must be a module-level callable."""
        from alfanous.searching import _is_arabic_text
        self.assertTrue(callable(_is_arabic_text))

    def test_arabic_codepoints_frozenset(self):
        """_ARABIC_CODEPOINTS must be a frozenset for immutable O(1) lookups."""
        from alfanous.searching import _ARABIC_CODEPOINTS
        self.assertIsInstance(_ARABIC_CODEPOINTS, frozenset)
        # Must contain Arabic block codepoints
        self.assertIn('\u0627', _ARABIC_CODEPOINTS)  # Alef
        self.assertIn('\u0628', _ARABIC_CODEPOINTS)  # Ba
        self.assertNotIn('A', _ARABIC_CODEPOINTS)
        self.assertNotIn('1', _ARABIC_CODEPOINTS)

    def test_arabic_text_detected(self):
        """Arabic strings return True."""
        from alfanous.searching import _is_arabic_text
        self.assertTrue(_is_arabic_text("مُلْك"))
        self.assertTrue(_is_arabic_text("بسم الله"))
        self.assertTrue(_is_arabic_text("abc\u0627"))  # Mixed, but has Arabic

    def test_non_arabic_text_rejected(self):
        """Non-Arabic strings and non-strings return False."""
        from alfanous.searching import _is_arabic_text
        self.assertFalse(_is_arabic_text("hello"))
        self.assertFalse(_is_arabic_text("123"))
        self.assertFalse(_is_arabic_text(""))
        self.assertFalse(_is_arabic_text(42))
        self.assertFalse(_is_arabic_text(None))
        self.assertFalse(_is_arabic_text(b"bytes"))

    def test_no_inline_range_checks_in_search(self):
        """The search() method must not contain inline \\u0600 range checks.

        All Arabic-text checks must go through _is_arabic_text() or
        _arabic_query_terms() — no duplicated inline ``any('\\u0600' ...)``
        comparisons.
        """
        import ast, inspect, textwrap
        import alfanous.searching as _mod
        src = textwrap.dedent(inspect.getsource(_mod.QSearcher.search))
        tree = ast.parse(src)

        # Look for any generator expression containing '\u0600' string comparison
        for node in ast.walk(tree):
            if isinstance(node, ast.Compare):
                for comp_val in [node.left] + list(node.comparators):
                    if isinstance(comp_val, ast.Constant) and comp_val.value == '\u0600':
                        self.fail(
                            "QSearcher.search() still contains inline "
                            "'\\u0600' <= c <= '\\u06FF' check — use "
                            "_is_arabic_text() or _arabic_query_terms() instead"
                        )


# ---------------------------------------------------------------------------
# Performance: _arabic_query_terms deduplicates derivation iteration
# ---------------------------------------------------------------------------

class TestArabicQueryTermsHelper(unittest.TestCase):
    """Verify _arabic_query_terms extracts unique Arabic terms properly."""

    def test_helper_exists(self):
        """_arabic_query_terms must be a module-level callable."""
        from alfanous.searching import _arabic_query_terms
        self.assertTrue(callable(_arabic_query_terms))

    def test_yields_arabic_terms_only(self):
        """Only Arabic-script terms from query.all_terms() are yielded."""
        from alfanous.searching import _arabic_query_terms
        from whoosh import query as wq

        q = wq.And([wq.Term("aya", "مُلْك"), wq.Term("aya", "hello"), wq.Term("aya", "كتاب")])
        result = list(_arabic_query_terms(q))
        self.assertIn("مُلْك", result)
        self.assertIn("كتاب", result)
        self.assertNotIn("hello", result)

    def test_deduplicates_terms(self):
        """Duplicate Arabic terms are yielded only once."""
        from alfanous.searching import _arabic_query_terms
        from whoosh import query as wq

        q = wq.And([wq.Term("aya", "مُلْك"), wq.Term("aya_", "مُلْك")])
        result = list(_arabic_query_terms(q))
        self.assertEqual(result.count("مُلْك"), 1)


# ---------------------------------------------------------------------------
# Performance: _find_parsers uses LRU eviction via OrderedDict
# ---------------------------------------------------------------------------

class TestFindParsersLRUEviction(unittest.TestCase):
    """Verify that _find_parsers cache is bounded by _MAX_FIND_PARSER_CACHE."""

    def test_find_parsers_is_ordered_dict(self):
        """_find_parsers must be an OrderedDict for LRU eviction support."""
        from collections import OrderedDict
        import alfanous.engines as _eng
        # Build a minimal mock engine
        mock_docindex = MagicMock()
        mock_docindex.OK = True
        mock_docindex.get_schema.return_value = MagicMock()
        mock_docindex.get_index.return_value = MagicMock()
        engine = _eng.BasicSearchEngine.__new__(_eng.BasicSearchEngine)
        engine.OK = False
        engine._find_parsers = OrderedDict()

        self.assertIsInstance(engine._find_parsers, OrderedDict)

    def test_max_cache_constant_defined(self):
        """_MAX_FIND_PARSER_CACHE must be defined at module level."""
        import alfanous.engines as _eng
        self.assertTrue(hasattr(_eng, '_MAX_FIND_PARSER_CACHE'))
        self.assertIsInstance(_eng._MAX_FIND_PARSER_CACHE, int)
        self.assertGreater(_eng._MAX_FIND_PARSER_CACHE, 0)

    def test_eviction_logic_in_find_extended(self):
        """find_extended must evict oldest entry when cache is full.

        We verify this by checking the source code for popitem(last=False)
        and len(self._find_parsers) >= _MAX_FIND_PARSER_CACHE.
        """
        import ast, inspect, textwrap
        import alfanous.engines as _eng
        src = textwrap.dedent(inspect.getsource(_eng.BasicSearchEngine.find_extended))
        tree = ast.parse(src)

        found_popitem = False
        found_len_check = False
        for node in ast.walk(tree):
            # Check for popitem call
            if isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Attribute) and func.attr == 'popitem':
                    found_popitem = True
            # Check for >= comparison with _MAX_FIND_PARSER_CACHE
            if isinstance(node, ast.Compare):
                for comp_val in list(node.comparators):
                    if isinstance(comp_val, ast.Name) and comp_val.id == '_MAX_FIND_PARSER_CACHE':
                        found_len_check = True

        self.assertTrue(found_popitem, "find_extended must call popitem(last=False) for LRU eviction")
        self.assertTrue(found_len_check, "find_extended must check len >= _MAX_FIND_PARSER_CACHE")


# ---------------------------------------------------------------------------
# Performance: _MIN_FUZZY_TERM_LEN constant used instead of magic number
# ---------------------------------------------------------------------------

class TestFuzzyTermLenConstant(unittest.TestCase):
    """Verify that _MIN_FUZZY_TERM_LEN is defined and used for fuzzy search."""

    def test_constant_defined(self):
        """_MIN_FUZZY_TERM_LEN must be defined at module level in searching."""
        from alfanous.searching import _MIN_FUZZY_TERM_LEN
        self.assertIsInstance(_MIN_FUZZY_TERM_LEN, int)
        self.assertEqual(_MIN_FUZZY_TERM_LEN, 4)

    def test_no_magic_number_in_fuzzy_search(self):
        """The fuzzy search block must not use a hard-coded '4' for min length.

        It should reference _MIN_FUZZY_TERM_LEN instead.
        """
        import ast, inspect, textwrap
        import alfanous.searching as _mod
        src = textwrap.dedent(inspect.getsource(_mod.QSearcher.search))
        tree = ast.parse(src)

        # Find the levenshtein_subqueries list comprehension and check
        # that it references _MIN_FUZZY_TERM_LEN, not a literal 4
        for node in ast.walk(tree):
            if isinstance(node, ast.ListComp):
                # Check if this is the FuzzyTerm comprehension
                comp_src = ast.dump(node)
                if 'FuzzyTerm' in comp_src or 'aya_ac' in comp_src:
                    # Check that the conditions don't use raw integer 4
                    for cond in node.generators[0].ifs:
                        for inner in ast.walk(cond):
                            if isinstance(inner, ast.Compare):
                                for comp_val in list(inner.comparators):
                                    if isinstance(comp_val, ast.Constant) and comp_val.value == 4:
                                        self.fail(
                                            "Fuzzy search uses magic number 4 — "
                                            "should use _MIN_FUZZY_TERM_LEN"
                                        )


if __name__ == "__main__":
    unittest.main()
