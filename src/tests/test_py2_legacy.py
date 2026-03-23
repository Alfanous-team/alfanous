"""
Tests that verify Python 2 legacy code has been cleaned up across the
alfanous package.  Each test inspects the AST or source text of a specific
module to ensure the deprecated pattern is absent.
"""

import unittest


# ---------------------------------------------------------------------------
# No u"..." unicode string literals
# ---------------------------------------------------------------------------

class TestNoUnicodeLiterals(unittest.TestCase):
    """u"..." and u'...' prefixes are Python 2 legacy and must not appear
    in the main alfanous source (Support/pyarabic is an externally-sourced
    subpackage and is exempt)."""

    def _count_u_prefixed_strings(self, module_path):
        """Count u-prefixed string literals in *module_path* via the AST."""
        import ast
        with open(module_path, encoding="utf-8") as fh:
            tree = ast.parse(fh.read())
        count = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                # ast.Constant does not track the original prefix, so we
                # fall back to a source-text scan for this check.
                pass
        return count  # AST check done below via source scan

    def _source_u_string_count(self, source_path):
        """Count u-prefixed string literals using a text scan.

        Uses a negative lookbehind to ensure the ``u`` is a string prefix,
        not a regular character inside a string literal (e.g. ``"u"``).
        The lookbehind ``(?<![\"'\\w])`` excludes ``u`` that is preceded by
        a quote character (inside a string) or a word character (identifier).
        """
        import re
        with open(source_path, encoding="utf-8") as fh:
            source = fh.read()
        # Match u" or u' that are NOT preceded by a quote or word character.
        return len(re.findall(r'(?<!["\'\w])u["\']', source))

    def test_romanization_no_u_prefix(self):
        """romanization.py must not contain u\"...\" string literals."""
        import alfanous
        import os
        path = os.path.join(os.path.dirname(alfanous.__file__), "romanization.py")
        count = self._source_u_string_count(path)
        self.assertEqual(
            count, 0,
            f"romanization.py still has {count} u-prefixed string literal(s); "
            "remove the u prefix — all strings are unicode in Python 3."
        )

    def test_buckwalter_u_key_is_damma(self):
        """BUCKWALTER2UNICODE['u'] must map to Damma (U+064F), not empty string."""
        from alfanous.romanization import BUCKWALTER2UNICODE
        self.assertEqual(
            BUCKWALTER2UNICODE.get("u"), "\u064F",
            "BUCKWALTER2UNICODE['u'] must be the Damma character U+064F"
        )
        self.assertNotIn(
            "", BUCKWALTER2UNICODE,
            "BUCKWALTER2UNICODE must not have an empty-string key "
            "(legacy u\"u\" → \"\" bug from Python 2 migration)"
        )

    def test_iso_u_key_is_damma(self):
        """ISO2UNICODE['u'] must map to Damma (U+064F), not empty string."""
        from alfanous.romanization import ISO2UNICODE
        self.assertEqual(
            ISO2UNICODE.get("u"), "\u064F",
            "ISO2UNICODE['u'] must be the Damma character U+064F"
        )

    def test_arabizi_u_key_is_waw(self):
        """ARABIZI2UNICODE['u'] must map to Waw (U+0648), not empty string."""
        from alfanous.romanization import ARABIZI2UNICODE
        self.assertEqual(
            ARABIZI2UNICODE.get("u"), ["\u0648"],
            "ARABIZI2UNICODE['u'] must be [U+0648 Waw]"
        )
        self.assertNotIn(
            "", ARABIZI2UNICODE,
            "ARABIZI2UNICODE must not have an empty-string key"
        )

    def test_query_plugins_no_u_prefix(self):
        """query_plugins.py must not contain u\"...\" string literals."""
        import alfanous
        import os
        path = os.path.join(os.path.dirname(alfanous.__file__), "query_plugins.py")
        count = self._source_u_string_count(path)
        self.assertEqual(
            count, 0,
            f"query_plugins.py still has {count} u-prefixed string literal(s)."
        )

    def test_text_processing_no_u_prefix(self):
        """text_processing.py must not contain u\"...\" string literals."""
        import alfanous
        import os
        path = os.path.join(os.path.dirname(alfanous.__file__), "text_processing.py")
        count = self._source_u_string_count(path)
        self.assertEqual(
            count, 0,
            f"text_processing.py still has {count} u-prefixed string literal(s)."
        )


# ---------------------------------------------------------------------------
# No Python 2 explicit-object inheritance
# ---------------------------------------------------------------------------

class TestNoExplicitObjectBase(unittest.TestCase):
    """Classes that inherit only from object must use bare `class Foo:` syntax."""

    def test_qboldformatter_no_object_base(self):
        """QBoldFormatter must not inherit from object explicitly."""
        import ast, inspect
        import alfanous.results_processing as _rp
        src = inspect.getsource(_rp.QBoldFormatter)
        tree = ast.parse(src)
        class_node = next(
            n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)
        )
        for base in class_node.bases:
            if isinstance(base, ast.Name) and base.id == "object":
                self.fail(
                    "QBoldFormatter must not inherit from object explicitly — "
                    "use `class QBoldFormatter:` (Python 3 implicit new-style)."
                )

    def test_qboldformatter_is_still_callable(self):
        """QBoldFormatter must still be instantiable after removing (object)."""
        from alfanous.results_processing import QBoldFormatter
        formatter = QBoldFormatter()
        self.assertIsNotNone(formatter)


# ---------------------------------------------------------------------------
# No Python 2 style super() calls
# ---------------------------------------------------------------------------

class TestModernSuperCalls(unittest.TestCase):
    """All super() calls must use the zero-argument Python 3 form."""

    def _check_no_old_super(self, module):
        """Assert that no super(ClassName, self/cls) calls exist in *module*."""
        import ast, inspect
        src = inspect.getsource(module)
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            if not (isinstance(func, ast.Name) and func.id == "super"):
                continue
            if node.args:
                self.fail(
                    f"Old-style super({ast.unparse(node.args[0])}, ...) found in "
                    f"{module.__name__} — use zero-argument super() instead."
                )

    def test_query_plugins_modern_super(self):
        """query_plugins.py must use zero-argument super()."""
        import alfanous.query_plugins as _qp
        self._check_no_old_super(_qp)

    def test_text_processing_modern_super(self):
        """text_processing.py must use zero-argument super()."""
        import alfanous.text_processing as _tp
        self._check_no_old_super(_tp)

    def test_query_processing_modern_super(self):
        """query_processing.py must use zero-argument super()."""
        import alfanous.query_processing as _qproc
        self._check_no_old_super(_qproc)


# ---------------------------------------------------------------------------
# f-strings in __str__ / __repr__ (no % formatting)
# ---------------------------------------------------------------------------

class TestFstringFormatting(unittest.TestCase):
    """__str__ and __repr__ methods in query_plugins.py must use f-strings."""

    def _has_percent_format(self, fn):
        """Return True if *fn*'s source uses %-formatting."""
        import ast, inspect, textwrap
        src = textwrap.dedent(inspect.getsource(fn))
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mod):
                # Left operand is a string template
                if isinstance(node.left, ast.Constant) and isinstance(node.left.value, str):
                    return True
        return False

    def test_qmultiterm_str_uses_fstring(self):
        """QMultiTerm.__str__ must use an f-string, not %-formatting."""
        from alfanous.query_plugins import QMultiTerm
        self.assertFalse(
            self._has_percent_format(QMultiTerm.__str__),
            "QMultiTerm.__str__ must use an f-string instead of %-formatting."
        )

    def test_qmultiterm_repr_uses_fstring(self):
        """QMultiTerm.__repr__ must use an f-string, not %-formatting."""
        from alfanous.query_plugins import QMultiTerm
        self.assertFalse(
            self._has_percent_format(QMultiTerm.__repr__),
            "QMultiTerm.__repr__ must use an f-string instead of %-formatting."
        )

    def test_synonyms_node_r_uses_fstring(self):
        """SynonymsNode.r() must use an f-string, not %-formatting."""
        from alfanous.query_plugins import SynonymsPlugin
        self.assertFalse(
            self._has_percent_format(SynonymsPlugin.SynonymsNode.r),
            "SynonymsNode.r() must use an f-string instead of %-formatting."
        )

    def test_derivation_node_r_uses_fstring(self):
        """DerivationNode.r() must use an f-string, not %-formatting."""
        from alfanous.query_plugins import DerivationPlugin
        self.assertFalse(
            self._has_percent_format(DerivationPlugin.DerivationNode.r),
            "DerivationNode.r() must use an f-string instead of %-formatting."
        )

    def test_spellerrors_node_r_uses_fstring(self):
        """SpellErrorsNode.r() must use an f-string, not %-formatting."""
        from alfanous.query_plugins import SpellErrorsPlugin
        self.assertFalse(
            self._has_percent_format(SpellErrorsPlugin.SpellErrorsNode.r),
            "SpellErrorsNode.r() must use an f-string instead of %-formatting."
        )

    def test_tashkil_node_r_uses_fstring(self):
        """TashkilNode.r() must use an f-string, not %-formatting."""
        from alfanous.query_plugins import TashkilPlugin
        self.assertFalse(
            self._has_percent_format(TashkilPlugin.TashkilNode.r),
            "TashkilNode.r() must use an f-string instead of %-formatting."
        )

    def test_tuple_node_r_uses_fstring(self):
        """TupleNode.r() must use an f-string, not %-formatting."""
        from alfanous.query_plugins import TuplePlugin
        self.assertFalse(
            self._has_percent_format(TuplePlugin.TupleNode.r),
            "TupleNode.r() must use an f-string instead of %-formatting."
        )

    def test_arabicwildcard_node_r_uses_fstring(self):
        """ArabicWildcardNode.r() must use an f-string, not %-formatting."""
        from alfanous.query_plugins import ArabicWildcardPlugin
        self.assertFalse(
            self._has_percent_format(ArabicWildcardPlugin.ArabicWildcardNode.r),
            "ArabicWildcardNode.r() must use an f-string instead of %-formatting."
        )

    def test_str_and_repr_still_produce_correct_output(self):
        """QMultiTerm subclass __str__ and __repr__ must still return correct strings."""
        from alfanous.query_plugins import SynonymsQuery
        q = SynonymsQuery("aya", "test")
        self.assertIn("aya", str(q))
        self.assertIn("SynonymsQuery", repr(q))
        self.assertIn("aya", repr(q))


if __name__ == "__main__":
    unittest.main()


# ---------------------------------------------------------------------------
# Module-level logger in outputs.py
# ---------------------------------------------------------------------------

class TestOutputsModuleLevelLogger(unittest.TestCase):
    """outputs.py must define a module-level ``logger`` so that the exception
    handlers inside ``_search_translation`` (lines that call
    ``logger.warning(...)``) do not raise ``NameError`` when a Whoosh I/O
    error such as ``ValueError: I/O operation on closed file`` is caught at
    runtime.
    """

    def test_logger_is_defined(self):
        """alfanous.outputs must expose a module-level 'logger' attribute."""
        import logging
        import alfanous.outputs as _outputs_module

        self.assertTrue(
            hasattr(_outputs_module, "logger"),
            "alfanous.outputs must define a module-level 'logger' variable",
        )
        self.assertIsInstance(
            _outputs_module.logger,
            logging.Logger,
            "alfanous.outputs.logger must be a logging.Logger instance",
        )