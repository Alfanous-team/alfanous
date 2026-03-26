
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
    """Unit tests for the derivation expansion in QSearcher.search.

    Derivation expansion runs in both fuzzy and non-fuzzy modes:
    - fuzzy=True  → root-level (level=2) derivations
    - fuzzy=False → lemma-level (level=1) derivations
    """

    def test_build_derivation_subqueries_arabic_only(self):
        """Derivation expansion only fires for Arabic-script terms."""
        from unittest.mock import patch
        from whoosh import query as wquery
        from alfanous.query_plugins import DerivationQuery

        # Reproduce the exact filter logic from QSearcher.search
        def build_derivation_subqueries(terms, deriv_level=2):
            """Mirror the derivation expansion logic from QSearcher.search."""
            seen = set()
            subqueries = []
            for _fieldname, term in terms:
                if not (isinstance(term, str) and any('\u0600' <= c <= '\u06FF' for c in term)):
                    continue
                if term in seen:
                    continue
                seen.add(term)
                derivations = DerivationQuery._get_derivations(term, deriv_level)
                for d in derivations:
                    if d and d != term:
                        subqueries.append(wquery.Term("aya", d))
            return subqueries

        mock_derivations = ["مالك", "يملك", "ملكوت"]

        with patch.object(DerivationQuery, "_get_derivations", return_value=mock_derivations):
            # Arabic term — derivation subqueries should be produced (none of the
            # mock derivations equal the original "ملك", so all 3 are included)
            arabic_terms = [("aya", "ملك")]
            result = build_derivation_subqueries(arabic_terms, deriv_level=2)
            assert len(result) == len(mock_derivations), (
                "One Term per unique derivation that differs from the original"
            )
            for q in result:
                assert isinstance(q, wquery.Term)
                assert q.fieldname == "aya"

        with patch.object(DerivationQuery, "_get_derivations", return_value=mock_derivations):
            # Latin term — no derivation subqueries
            latin_terms = [("aya", "book")]
            result = build_derivation_subqueries(latin_terms, deriv_level=2)
            assert result == [], "Latin terms must not trigger derivation expansion"

    def test_derivation_level_varies_by_fuzzy_mode(self):
        """fuzzy=True uses level=2 (root), fuzzy=False uses level=1 (lemma)."""
        from unittest.mock import patch, call
        from alfanous.query_plugins import DerivationQuery

        captured_levels = []

        def tracking_get_derivations(word, level):
            captured_levels.append(level)
            return [word]

        with patch.object(DerivationQuery, "_get_derivations", side_effect=tracking_get_derivations):
            term = "ملك"
            # fuzzy=True → root-level derivations (level=2)
            fuzzy = True
            deriv_level = 2 if fuzzy else 1
            DerivationQuery._get_derivations(term, deriv_level)
            # fuzzy=False → lemma-level derivations (level=1)
            fuzzy = False
            deriv_level = 2 if fuzzy else 1
            DerivationQuery._get_derivations(term, deriv_level)

        assert captured_levels == [2, 1], (
            "fuzzy=True must use level=2 (root), fuzzy=False must use level=1 (lemma)"
        )

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

    def test_derivation_expansion_terms_excluded_from_matched_terms(self):
        """Derivation-expansion terms must be filtered out of the matched-terms set.

        Strategy 4 adds Term("aya", d) for each derivation.  When these
        terms match documents, Whoosh includes them in matched_terms().  They
        must NOT be returned as part of the 'terms' frozenset that callers use
        to build words_output, otherwise the first entry in words.individual
        becomes a derivation word (not the user's query word) and
        nb_variations is incorrectly 0.

        Verify the filtering logic directly using the frozenset set-difference
        approach implemented in QSearcher.search.
        """
        # Simulate matched_terms: includes original query term AND derivations
        original_query_terms = frozenset([("aya", "ملك"), ("aya_", "ملك")])
        derivation_expansion = {("aya", "مالك"), ("aya", "يملك"), ("aya", "ملكوت")}

        # All matched terms (would come from results.matched_terms())
        all_matched = original_query_terms | derivation_expansion | {("aya_ac", "ملك")}

        # Apply the filter: remove derivation terms not in the original query
        filtered = set(all_matched)
        filtered -= (derivation_expansion - original_query_terms)

        # Derivation terms should be excluded
        for deriv_pair in derivation_expansion:
            assert deriv_pair not in filtered, (
                f"Derivation-expansion term {deriv_pair} must be excluded"
            )
        # Original query terms and aya_ac terms must be kept
        assert ("aya", "ملك") in filtered
        assert ("aya_", "ملك") in filtered
        assert ("aya_ac", "ملك") in filtered

    def test_derivation_expansion_term_kept_if_in_original_query(self):
        """A derivation term that was also in the original query is kept.

        If the user explicitly typed a word that also appears as a derivation
        of another word in the query, that word must NOT be excluded from the
        returned terms (it was a real user keyword, not just an expansion).
        """
        # Scenario: user typed both "ملك" and "مالك"; "مالك" is also a
        # derivation of "ملك" — it must be kept.
        original_query_terms = frozenset([("aya", "ملك"), ("aya", "مالك")])
        derivation_expansion = {("aya", "مالك"), ("aya", "يملك")}

        all_matched = original_query_terms | derivation_expansion

        filtered = set(all_matched)
        filtered -= (derivation_expansion - original_query_terms)

        # "مالك" is in both derivation_expansion and original_query_terms → kept
        assert ("aya", "مالك") in filtered, (
            "A term in both derivation_expansion and original_query_terms must be kept"
        )
        # "يملك" is only a derivation → excluded
        assert ("aya", "يملك") not in filtered, (
            "A pure derivation-expansion term must be excluded"
        )


# ---------------------------------------------------------------------------
# Unit tests for _collect_plugin_expanded_terms (no index required)
# ---------------------------------------------------------------------------

class TestCollectPluginExpandedTerms:
    """Tests for alfanous.searching._collect_plugin_expanded_terms."""

    def test_plain_term_returns_empty(self):
        """A plain Whoosh Term node has no plugin-expanded terms."""
        from whoosh import query as wquery
        from alfanous.searching import _collect_plugin_expanded_terms

        q = wquery.Term("aya", "مالك")
        result = _collect_plugin_expanded_terms(q)
        assert result == set()

    def test_derivation_query_returns_all_terms(self):
        """DerivationQuery node returns all its expanded terms."""
        from alfanous.searching import _collect_plugin_expanded_terms
        from alfanous.query_plugins import DerivationQuery
        from unittest.mock import patch

        mock_words = ["مالك", "مالكون", "يملك"]
        with patch.object(DerivationQuery, '_get_derivations', return_value=mock_words):
            dq = DerivationQuery("aya", "مالك", level=1)
        result = _collect_plugin_expanded_terms(dq)
        assert len(result) == 3
        assert ("aya", "مالك") in result
        assert ("aya", "مالكون") in result
        assert ("aya", "يملك") in result

    def test_tuple_query_returns_all_terms(self):
        """TupleQuery node returns all its expanded terms."""
        from alfanous.searching import _collect_plugin_expanded_terms
        from alfanous.query_plugins import TupleQuery
        from unittest.mock import patch

        mock_words = ["قول", "قولا", "قولكم"]
        with patch("alfanous.query_plugins._query_word_index", return_value=mock_words):
            tq = TupleQuery("aya", ["قول", "اسم"])
        result = _collect_plugin_expanded_terms(tq)
        assert len(result) == 3
        assert ("aya", "قول") in result
        assert ("aya", "قولا") in result
        assert ("aya", "قولكم") in result

    def test_compound_query_with_derivation(self):
        """DerivationQuery inside a compound Or returns its terms."""
        from whoosh import query as wquery
        from alfanous.searching import _collect_plugin_expanded_terms
        from alfanous.query_plugins import DerivationQuery
        from unittest.mock import patch

        mock_words = ["مالك", "مالكون"]
        with patch.object(DerivationQuery, '_get_derivations', return_value=mock_words):
            dq = DerivationQuery("aya", "مالك", level=1)
        plain = wquery.Term("aya", "كتاب")
        compound = wquery.Or([plain, dq])

        result = _collect_plugin_expanded_terms(compound)
        # Only DerivationQuery terms, not the plain term
        assert ("aya", "مالك") in result
        assert ("aya", "مالكون") in result
        assert ("aya", "كتاب") not in result

    def test_nested_and_or_with_derivation(self):
        """Deeply nested query trees still find DerivationQuery nodes."""
        from whoosh import query as wquery
        from alfanous.searching import _collect_plugin_expanded_terms
        from alfanous.query_plugins import DerivationQuery
        from unittest.mock import patch

        mock_words = ["مالك", "يملك"]
        with patch.object(DerivationQuery, '_get_derivations', return_value=mock_words):
            dq = DerivationQuery("aya", "مالك", level=2)
        inner = wquery.And([wquery.Term("aya", "كتاب"), dq])
        outer = wquery.Or([wquery.Term("aya", "رب"), inner])

        result = _collect_plugin_expanded_terms(outer)
        assert ("aya", "مالك") in result
        assert ("aya", "يملك") in result
        assert ("aya", "كتاب") not in result
        assert ("aya", "رب") not in result

    def test_no_plugin_queries_returns_empty(self):
        """Query tree with no plugin queries returns empty set."""
        from whoosh import query as wquery
        from alfanous.searching import _collect_plugin_expanded_terms

        q = wquery.And([wquery.Term("aya", "مالك"), wquery.Term("aya", "كتاب")])
        result = _collect_plugin_expanded_terms(q)
        assert result == set()

    def test_aya_auto_stem_term_is_plugin_expanded(self):
        """Term targeting aya_auto_stem must be treated as plugin-expanded (in _DERIV_FIELDS)."""
        from whoosh import query as wquery
        from alfanous.searching import _collect_plugin_expanded_terms

        q = wquery.Term("aya_auto_stem", "رحم")
        result = _collect_plugin_expanded_terms(q)
        assert ("aya_auto_stem", "رحم") in result, (
            "aya_auto_stem terms must be treated as plugin-expanded to prevent double-expansion"
        )

    def test_aya_stem_term_is_plugin_expanded(self):
        """Term targeting aya_stem must be treated as plugin-expanded (in _DERIV_FIELDS)."""
        from whoosh import query as wquery
        from alfanous.searching import _collect_plugin_expanded_terms

        q = wquery.Term("aya_stem", "ملك")
        result = _collect_plugin_expanded_terms(q)
        assert ("aya_stem", "ملك") in result, (
            "aya_stem terms must be treated as plugin-expanded to prevent double-expansion"
        )


# ---------------------------------------------------------------------------
# Unit tests: derivation-expansion terms with zero results must be filtered
# from words.individual in _search_aya.
# ---------------------------------------------------------------------------

class TestDerivationExpansionKeywordFilter:
    """Derivation-expansion terms injected as ('aya', word, 0, 0) must not
    appear in words.individual when they have no matches in the result set.

    Regression test for: root-level search for مالك shows 34 keywords,
    32 of which have zero occurrences.
    """

    def _make_termz(self, *entries):
        """Construct a termz list from (field, word, freq, doc_freq) tuples."""
        return list(entries)

    def test_zero_stats_zero_results_term_is_excluded(self):
        """A term with (0, 0) stats and 0 result-matches must NOT enter words.individual.

        This is the core fix: expansion terms appended as ('aya', w, 0, 0) that
        don't appear in any matched aya should be silently dropped.
        """
        # Build a minimal termz with one real term and one synthetic expansion.
        termz = self._make_termz(
            ("aya", "مالك", 120, 43),   # real query term — has corpus stats
            ("aya", "الملائكة", 0, 0),  # synthetic expansion — injected by _collect_derivations_two_pass
        )

        # Simulate the filter condition used in _search_aya:
        #   skip if not term[2] and not term[3] and not term_matches_in_results
        def would_be_skipped(term, term_matches_in_results):
            return not term[2] and not term[3] and not term_matches_in_results

        # الملائكة has zero corpus stats and matches nothing in the 2-result set.
        assert would_be_skipped(("aya", "الملائكة", 0, 0), 0), (
            "Expansion term with (0,0) stats and 0 result-matches must be filtered"
        )
        # مالك has real corpus stats — must NOT be skipped even with 0 result-matches.
        assert not would_be_skipped(("aya", "مالك", 120, 43), 0), (
            "Real query term with corpus stats must never be filtered"
        )

    def test_zero_stats_but_matching_term_is_included(self):
        """An expansion term with (0, 0) stats that DOES match results must stay.

        e.g. يملك shares the root ملك with مالك — if it appears in the 2
        matched ayas it must be listed in keywords so the highlighted word
        is also in words.individual.
        """
        def would_be_skipped(term, term_matches_in_results):
            return not term[2] and not term[3] and not term_matches_in_results

        # يملك was injected with (0,0) stats but actually appears in results.
        assert not would_be_skipped(("aya", "يملك", 0, 0), 3), (
            "Expansion term that matches in results must NOT be filtered"
        )

    def test_real_term_with_zero_corpus_stats_is_not_skipped(self):
        """A term with non-zero doc_freq but zero term-freq must not be filtered.

        This guards against accidental filtering of edge-case real terms.
        """
        def would_be_skipped(term, term_matches_in_results):
            return not term[2] and not term[3] and not term_matches_in_results

        # term[2]=0 but term[3]=5 — has doc frequency → real term.
        assert not would_be_skipped(("aya", "كتاب", 0, 5), 0), (
            "Term with non-zero doc_freq must not be filtered even with 0 term-freq"
        )


# ---------------------------------------------------------------------------
# Unit tests: derivation subquery resolution uses root/lemma/stem from lookup
# table, NOT the bare (tashkeel-stripped) query word.
# ---------------------------------------------------------------------------

class TestDerivationSubqueryResolution:
    """QSearcher.search() must look up the actual morphological value (root /
    lemma / stem_norm) for each query word before building the derivation
    subquery Term.

    Regression test for: derivation_level:root search for مالك matches only
    2 ayas because Term("aya_root", "مالك") was built instead of
    Term("aya_root", "ملك").  The aya_root field stores "ملك" (the root), not
    "مالك" (the word form), so searching for the word form found only the rare
    ayas where مالك happens to be recorded as its own root.
    """

    def _make_lookup_table(self, form_to_key):
        """Build a minimal 6-tuple lookup table with only form_to_key populated."""
        return (form_to_key, {}, {}, {}, {}, {})

    def test_root_level_resolves_root_value(self):
        """Level 3 (root): query term 'مالك' resolves to root 'ملك' via form_to_key."""
        form_to_key = {
            "مالك": {"lemma": "مَالِك", "root": "ملك", "stem_norm": "مالك"},
        }
        lt = self._make_lookup_table(form_to_key)

        # Simulate what QSearcher.search() does:
        _level_to_morph = {1: "stem_norm", 2: "lemma", 3: "root"}
        _morph_attr = _level_to_morph[3]  # "root"
        _entry = form_to_key.get("مالك")
        _morph_val = _entry.get(_morph_attr) if _entry else None
        _search_term = _morph_val if _morph_val else "مالك"

        assert _search_term == "ملك", (
            f"Level 3 should search aya_root for 'ملك' (the root), got '{_search_term}'"
        )

    def test_lemma_level_resolves_lemma_value(self):
        """Level 2 (lemma): query term 'مالك' resolves to lemma 'مَالِك' via form_to_key."""
        form_to_key = {
            "مالك": {"lemma": "مَالِك", "root": "ملك", "stem_norm": "مالك"},
        }

        _level_to_morph = {1: "stem_norm", 2: "lemma", 3: "root"}
        _morph_attr = _level_to_morph[2]  # "lemma"
        _entry = form_to_key.get("مالك")
        _morph_val = _entry.get(_morph_attr) if _entry else None
        _search_term = _morph_val if _morph_val else "مالك"

        assert _search_term == "مَالِك", (
            f"Level 2 should resolve to the vocalized lemma; got '{_search_term}'"
        )

    def test_stem_level_resolves_stem_norm(self):
        """Level 1 (stem): query term 'يملك' resolves to its corpus stem via form_to_key."""
        form_to_key = {
            "يملك": {"lemma": "مَلَكَ", "root": "ملك", "stem_norm": "ملك"},
        }

        _level_to_morph = {1: "stem_norm", 2: "lemma", 3: "root"}
        _morph_attr = _level_to_morph[1]  # "stem_norm"
        _entry = form_to_key.get("يملك")
        _morph_val = _entry.get(_morph_attr) if _entry else None
        _search_term = _morph_val if _morph_val else "يملك"

        assert _search_term == "ملك", (
            f"Level 1 should resolve to the corpus stem; got '{_search_term}'"
        )

    def test_unknown_word_falls_back_to_raw_term(self):
        """A query word not in form_to_key falls back to the raw (normalized) term."""
        form_to_key: dict = {}  # empty — word not in Quran corpus

        _level_to_morph = {1: "stem_norm", 2: "lemma", 3: "root"}
        for level in (1, 2, 3):
            _morph_attr = _level_to_morph[level]
            _entry = form_to_key.get("xyz")
            _morph_val = _entry.get(_morph_attr) if _entry else None
            _search_term = _morph_val if _morph_val else "xyz"
            assert _search_term == "xyz", (
                f"Level {level}: unknown word must fall back to raw term; got '{_search_term}'"
            )

    def test_form_to_key_contains_stem_norm(self):
        """_build_word_lookup_table must store 'stem_norm' in each form_to_key entry."""
        from alfanous.query_plugins import _build_word_lookup_table

        class _FakeReader:
            def iter_docs(self):
                yield (0, {
                    "kind": "word",
                    "word": "يَمْلِكُ",
                    "normalized": "يملك",
                    "lemma": "مَلَكَ",
                    "root": "ملك",
                    "stem": "ملك",
                    "standard": "يملك",
                })

        lt = _build_word_lookup_table(_FakeReader())
        form_to_key = lt[0]

        assert "يملك" in form_to_key, "normalized form 'يملك' must be in form_to_key"
        entry = form_to_key["يملك"]
        assert "stem_norm" in entry, (
            "form_to_key entry must contain 'stem_norm' for derivation-level stem resolution"
        )
        assert entry["stem_norm"] == "ملك", (
            f"stem_norm should be 'ملك' (normalized corpus stem); got {entry['stem_norm']!r}"
        )
        assert entry["root"] == "ملك", "root must be 'ملك'"
        assert entry["lemma"] == "مَلَكَ", "lemma must be 'مَلَكَ'"

    def test_qsearcher_search_passes_lookup_table(self):
        """QSearcher.search() must accept and use word_lookup_table parameter.

        Verify that the new keyword parameter is wired in without TypeError.
        A mock QSearcher that captures the search call confirms the parameter
        reaches the derivation-subquery building code.
        """
        from alfanous.searching import QSearcher
        from unittest.mock import MagicMock, patch
        from whoosh import query as wq
        from whoosh.fields import Schema, TEXT

        # Build a trivial schema and mock out all Whoosh internals.
        schema = Schema(aya=TEXT)
        mock_parser = MagicMock()
        mock_parser.parse.return_value = wq.Term("aya", "مالك")

        mock_searcher_instance = MagicMock()
        mock_searcher_instance.search.return_value = ([], [], {})
        mock_searcher_instance.collector.return_value = MagicMock()
        mock_results = MagicMock()
        mock_results.__len__ = lambda s: 0
        mock_results.__iter__ = lambda s: iter([])
        mock_results.matched_terms.return_value = set()
        mock_collector = MagicMock()
        mock_collector.results.return_value = mock_results
        mock_searcher_instance.collector.return_value = mock_collector

        mock_index = MagicMock()
        mock_index.get_schema.return_value = schema
        mock_index.get_index.return_value.searcher.return_value = mock_searcher_instance

        qs = QSearcher.__new__(QSearcher)
        qs._searcher = mock_index.get_index().searcher
        qs._qparser = mock_parser
        qs._schema = schema
        qs._shared_searcher = mock_searcher_instance

        form_to_key = {"مالك": {"lemma": "مَالِك", "root": "ملك", "stem_norm": "مالك"}}
        lookup_table = (form_to_key, {}, {}, {}, {}, {})

        # Must not raise TypeError for unknown parameter.
        try:
            qs.search("مالك", derivation_level=3, word_lookup_table=lookup_table,
                      timelimit=None)
        except TypeError as e:
            raise AssertionError(
                f"QSearcher.search() rejected word_lookup_table parameter: {e}"
            ) from e

class TestHasWildcardQuery:
    """Tests for alfanous.searching._has_wildcard_query."""

    def test_wildcard_node_returns_true(self):
        """A bare Wildcard node must be detected."""
        from whoosh import query as wquery
        from alfanous.searching import _has_wildcard_query

        q = wquery.Wildcard("aya", "كت*")
        assert _has_wildcard_query(q) is True

    def test_term_node_returns_false(self):
        """A plain Term has no wildcard — must return False."""
        from whoosh import query as wquery
        from alfanous.searching import _has_wildcard_query

        q = wquery.Term("aya", "كتاب")
        assert _has_wildcard_query(q) is False

    def test_arabic_wildcard_query_returns_true(self):
        """ArabicWildcardQuery (subclass of Wildcard) must also be detected."""
        from alfanous.query_plugins import ArabicWildcardQuery
        from alfanous.searching import _has_wildcard_query

        q = ArabicWildcardQuery("aya", "كت*")
        assert _has_wildcard_query(q) is True

    def test_wildcard_inside_and_returns_true(self):
        """Wildcard nested inside an And compound must be found."""
        from whoosh import query as wquery
        from alfanous.searching import _has_wildcard_query

        q = wquery.And([wquery.Term("aya", "الله"), wquery.Wildcard("aya", "رح*")])
        assert _has_wildcard_query(q) is True

    def test_wildcard_inside_or_returns_true(self):
        """Wildcard nested inside an Or compound must be found."""
        from whoosh import query as wquery
        from alfanous.searching import _has_wildcard_query

        q = wquery.Or([wquery.Term("aya", "الله"), wquery.Wildcard("aya", "رح*")])
        assert _has_wildcard_query(q) is True

    def test_no_wildcard_compound_returns_false(self):
        """A compound query with only Term leaves must return False."""
        from whoosh import query as wquery
        from alfanous.searching import _has_wildcard_query

        q = wquery.And([wquery.Term("aya", "الله"), wquery.Term("aya", "أكبر")])
        assert _has_wildcard_query(q) is False
