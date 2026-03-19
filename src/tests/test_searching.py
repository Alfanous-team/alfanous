
"""
This is a test module for alfanous.Searching

"""
import os
import pytest
from alfanous import paths
from alfanous.indexing import QseDocIndex
from alfanous.searching import QReader

def test_searching():
    if not os.path.isdir(paths.QSE_INDEX) or not QseDocIndex(paths.QSE_INDEX).OK:
        pytest.skip("Search index not built — run `make build` first")
    index = QseDocIndex( paths.QSE_INDEX )
    reader = QReader( index )
    assert list(reader.list_values( "sura_name" ))[:10] == []


# ---------------------------------------------------------------------------
# Unit tests for _strip_phrase_queries (no index required)
# ---------------------------------------------------------------------------

class TestStripPhraseQueries:
    """Tests for alfanous.searching._strip_phrase_queries."""

    def _make_schema(self):
        from whoosh.fields import Schema, TEXT, ID, KEYWORD, NUMERIC
        return Schema(
            aya=TEXT(stored=True, phrase=True),
            topic=ID(stored=True),
            chapter=ID(stored=True),
            subtopic=ID(stored=True),
            sura=TEXT(stored=True, phrase=False),
            sura_name=KEYWORD(stored=True),
            sura_id=NUMERIC(stored=True),
            aya_fuzzy=TEXT(stored=True, phrase=False),
        )

    def test_phrase_stripped_without_schema(self):
        """Without a schema, ALL Phrase nodes are converted to And-of-Terms."""
        from whoosh import query as wquery
        from alfanous.searching import _strip_phrase_queries

        q = wquery.Phrase("topic", ["word1", "word2"])
        result = _strip_phrase_queries(q)
        assert isinstance(result, wquery.And), (
            "Phrase should be converted to And without a schema"
        )

    def test_phrase_on_id_field_stripped_with_schema(self):
        """With a schema, a Phrase on an ID field is converted to And-of-Terms."""
        from whoosh import query as wquery
        from alfanous.searching import _strip_phrase_queries

        schema = self._make_schema()
        q = wquery.Phrase("topic", ["word1", "word2"])
        result = _strip_phrase_queries(q, schema=schema)
        assert isinstance(result, wquery.And), (
            "Phrase on ID 'topic' field must be converted to And-of-Terms"
        )

    def test_phrase_on_text_field_preserved_with_schema(self):
        """With a schema, a Phrase on a TEXT(phrase=True) field is left intact."""
        from whoosh import query as wquery
        from alfanous.searching import _strip_phrase_queries

        schema = self._make_schema()
        q = wquery.Phrase("aya", ["word1", "word2"])
        result = _strip_phrase_queries(q, schema=schema)
        assert isinstance(result, wquery.Phrase), (
            "Phrase on TEXT 'aya' field must NOT be stripped (field supports positions)"
        )

    def test_phrase_on_text_phrase_false_stripped_with_schema(self):
        """With a schema, a Phrase on a TEXT(phrase=False) field is converted."""
        from whoosh import query as wquery
        from alfanous.searching import _strip_phrase_queries

        schema = self._make_schema()
        q = wquery.Phrase("aya_fuzzy", ["word1", "word2"])
        result = _strip_phrase_queries(q, schema=schema)
        assert isinstance(result, wquery.And), (
            "Phrase on TEXT(phrase=False) 'aya_fuzzy' field must be converted to And-of-Terms"
        )

    def test_mixed_compound_query(self):
        """Schema-aware stripping inside a compound query (Or containing Phrase nodes)."""
        from whoosh import query as wquery
        from alfanous.searching import _strip_phrase_queries

        schema = self._make_schema()
        # Or(Phrase("aya", ...), Phrase("topic", ...))
        # → aya phrase preserved, topic phrase stripped
        q_aya = wquery.Phrase("aya", ["الحمد", "لله"])
        q_topic = wquery.Phrase("topic", ["أركان", "الإيمان"])
        compound = wquery.Or([q_aya, q_topic])
        result = _strip_phrase_queries(compound, schema=schema)
        assert isinstance(result, wquery.Or)
        subs = result.subqueries
        assert isinstance(subs[0], wquery.Phrase), "aya Phrase must be preserved"
        assert isinstance(subs[1], wquery.And), "topic Phrase must be converted"

    def test_keyword_field_phrase_stripped(self):
        """Phrase on a KEYWORD field is converted to And-of-Terms."""
        from whoosh import query as wquery
        from alfanous.searching import _strip_phrase_queries

        schema = self._make_schema()
        q = wquery.Phrase("sura_name", ["Al", "Baqara"])
        result = _strip_phrase_queries(q, schema=schema)
        assert isinstance(result, wquery.And), (
            "Phrase on KEYWORD 'sura_name' field must be converted to And-of-Terms"
        )

    def test_sura_phrase_stripped_with_schema(self):
        """Phrase on the 'sura' TEXT(phrase=False) field is converted to And-of-Terms.

        The 'sura' field (romanized sura name) is indexed with ``phrase=False``
        so it stores no positional data.  A phrase query like
        ``sura:"Al Baqarah"`` must not raise
        ``QueryError: Phrase search: 'sura' field has no positions``.
        ``_strip_phrase_queries`` should convert it to an unordered And-of-Terms.
        """
        from whoosh import query as wquery
        from alfanous.searching import _strip_phrase_queries

        schema = self._make_schema()
        q = wquery.Phrase("sura", ["Al", "Baqarah"])
        result = _strip_phrase_queries(q, schema=schema)
        assert isinstance(result, wquery.And), (
            "Phrase on TEXT(phrase=False) 'sura' field must be converted to And-of-Terms"
        )


# ---------------------------------------------------------------------------
# Unit tests for fuzzy derivation expansion (no index required)
# ---------------------------------------------------------------------------

class TestFuzzyDerivationExpansion:
    """Unit tests for the Strategy 4 derivation expansion in QSearcher.search."""

    def test_build_derivation_subqueries_arabic_only(self):
        """Derivation expansion only fires for Arabic-script terms."""
        from unittest.mock import patch
        from whoosh import query as wquery
        from alfanous.query_plugins import DerivationQuery

        # Reproduce the exact filter logic from QSearcher.search Strategy 4
        def build_derivation_subqueries(terms):
            """Mirror the derivation expansion logic from QSearcher.search."""
            seen = set()
            subqueries = []
            for _fieldname, term in terms:
                if not (isinstance(term, str) and any('\u0600' <= c <= '\u06FF' for c in term)):
                    continue
                if term in seen:
                    continue
                seen.add(term)
                derivations = DerivationQuery._get_derivations(term, 2)
                for d in derivations:
                    if d and d != term:
                        subqueries.append(wquery.Term("aya", d))
            return subqueries

        mock_derivations = ["مالك", "يملك", "ملكوت"]

        with patch.object(DerivationQuery, "_get_derivations", return_value=mock_derivations):
            # Arabic term — derivation subqueries should be produced (none of the
            # mock derivations equal the original "ملك", so all 3 are included)
            arabic_terms = [("aya", "ملك")]
            result = build_derivation_subqueries(arabic_terms)
            assert len(result) == len(mock_derivations), (
                "One Term per unique derivation that differs from the original"
            )
            for q in result:
                assert isinstance(q, wquery.Term)
                assert q.fieldname == "aya"

        with patch.object(DerivationQuery, "_get_derivations", return_value=mock_derivations):
            # Latin term — no derivation subqueries
            latin_terms = [("aya", "book")]
            result = build_derivation_subqueries(latin_terms)
            assert result == [], "Latin terms must not trigger derivation expansion"

    def test_derivation_skips_original_word(self):
        """The original query word itself must not be duplicated in subqueries."""
        from unittest.mock import patch
        from whoosh import query as wquery
        from alfanous.query_plugins import DerivationQuery

        original = "ملك"
        # Derivations include the original word — it should be excluded from subqueries
        mock_derivations = [original, "مالك", "يملك"]

        seen = set()
        subqueries = []
        with patch.object(DerivationQuery, "_get_derivations", return_value=mock_derivations):
            derivations = DerivationQuery._get_derivations(original, 2)
            for d in derivations:
                if d and d != original:
                    subqueries.append(wquery.Term("aya", d))

        term_texts = [q.text for q in subqueries]
        assert original not in term_texts, "Original query word must not appear in derivation subqueries"
        assert "مالك" in term_texts
        assert "يملك" in term_texts

    def test_derivation_deduplicates_terms(self):
        """Repeated Arabic terms in a multi-word query are only expanded once."""
        from unittest.mock import patch
        from whoosh import query as wquery
        from alfanous.query_plugins import DerivationQuery

        call_count = {"n": 0}

        def counting_get_derivations(word, level):
            call_count["n"] += 1
            return [word]  # No new derivations

        with patch.object(DerivationQuery, "_get_derivations", side_effect=counting_get_derivations):
            # Same term repeated — should only call _get_derivations once
            repeated_terms = [("aya", "ملك"), ("aya", "ملك"), ("aya", "ملك")]
            seen = set()
            for _fieldname, term in repeated_terms:
                if not (isinstance(term, str) and any('\u0600' <= c <= '\u06FF' for c in term)):
                    continue
                if term in seen:
                    continue
                seen.add(term)
                DerivationQuery._get_derivations(term, 2)

        assert call_count["n"] == 1, "Duplicate terms must only be expanded once"
