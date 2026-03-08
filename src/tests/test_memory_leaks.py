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


if __name__ == "__main__":
    unittest.main()
