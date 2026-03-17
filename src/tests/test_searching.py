
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
