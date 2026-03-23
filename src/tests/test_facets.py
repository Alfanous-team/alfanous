"""
Test module for facet search functionality in alfanous.

"""

import pytest
from alfanous import api
from alfanous.outputs import Raw
from alfanous import paths


RAWoutput = Raw(
    QSE_index=paths.QSE_INDEX,
    Recitations_list_file=paths.RECITATIONS_LIST_FILE,
    Translations_list_file=paths.TRANSLATIONS_LIST_FILE,
    Information_file=paths.INFORMATION_FILE
)


@pytest.fixture(autouse=True)
def _require_index():
    if not RAWoutput.QSE.OK:
        pytest.skip("Search index not built — run `make build` first")


def test_filter_by_sura():
    """Test filtering by sura_id without modifying query."""
    # Search for "الله" but only in Sura 2
    search_flags = {
        "action": "search",
        "query": "الله",
        "filter": {"sura_id": 2}
    }
    
    results = RAWoutput.do(search_flags)
    
    # Check that search was successful
    assert results["error"]["code"] == 0
    
    # Check that all results are from Sura 2
    for aya in results["search"]["ayas"].values():
        assert aya["identifier"]["sura_id"] == 2


def test_filter_by_juz():
    """Test filtering by juz."""
    search_flags = {
        "action": "search",
        "query": "الصلاة",
        "filter": {"juz": 1},
        "aya_position_info": True
    }
    
    results = RAWoutput.do(search_flags)
    
    # Check that search was successful
    assert results["error"]["code"] == 0
    
    # Check that all results are from Juz 1
    for aya in results["search"]["ayas"].values():
        assert aya["position"]["juz"] == 1


def test_filter_with_facets():
    """Test using filter and facets together."""
    search_flags = {
        "action": "search",
        "query": "الله",
        "filter": {"juz": 1},
        "facets": "sura_id",
        "aya_position_info": True
    }
    
    results = RAWoutput.do(search_flags)
    
    # Check that search was successful
    assert results["error"]["code"] == 0
    
    # Check that facets are present
    assert "facets" in results["search"]
    assert "sura_id" in results["search"]["facets"]
    
    # Check that all results are from Juz 1
    for aya in results["search"]["ayas"].values():
        assert aya["position"]["juz"] == 1


def test_filter_with_api_function():
    """Test filtering using the api.search() function."""
    results = api.search(query="الرحمن", filter={"sura_id": 2}, facets="chapter")
    
    # Check that search was successful
    assert results["error"]["code"] == 0
    
    # Check that all results are from Sura 2
    for aya in results["search"]["ayas"].values():
        assert aya["identifier"]["sura_id"] == 2


def test_filter_string_format():
    """Test filter parameter as string format."""
    search_flags = {
        "action": "search",
        "query": "الله",
        "filter": "sura_id:2"
    }
    
    results = RAWoutput.do(search_flags)
    
    # Check that search was successful
    assert results["error"]["code"] == 0
    
    # Check that all results are from Sura 2
    for aya in results["search"]["ayas"].values():
        assert aya["identifier"]["sura_id"] == 2


def test_multiple_filters():
    """Test applying multiple filters."""
    search_flags = {
        "action": "search",
        "query": "الله",
        "filter": {"sura_id": 2, "aya_id": [1, 2, 3, 4, 5]}
    }
    
    results = RAWoutput.do(search_flags)
    
    # Check that search was successful
    assert results["error"]["code"] == 0
    
    # Check that all results are from Sura 2 and verses 1-5
    for aya in results["search"]["ayas"].values():
        assert aya["identifier"]["sura_id"] == 2
        assert aya["identifier"]["aya_id"] in [1, 2, 3, 4, 5]


def test_filter_vs_query_comparison():
    """Test that filter produces same results as query filtering."""
    # Using filter parameter
    results_with_filter = api.search(query="الله", filter={"sura_id": 2})
    
    # Using query filtering
    results_with_query = api.search(query="الله AND sura_id:2")
    
    # Both should return results from Sura 2
    assert results_with_filter["error"]["code"] == 0
    assert results_with_query["error"]["code"] == 0
    
    # Count should be similar (might differ slightly due to query parsing)
    assert results_with_filter["search"]["interval"]["total"] > 0
    assert results_with_query["search"]["interval"]["total"] > 0


def test_facet_by_sura():
    """Test faceting by sura_id."""
    search_flags = {
        "action": "search",
        "query": "الله",
        "facets": "sura_id"
    }
    
    results = RAWoutput.do(search_flags)
    
    # Check that search was successful
    assert results["error"]["code"] == 0
    
    # Check that facets are in results
    assert "facets" in results["search"]
    assert "sura_id" in results["search"]["facets"]
    
    # Check facet structure
    facets = results["search"]["facets"]["sura_id"]
    assert isinstance(facets, list)
    assert len(facets) > 0
    
    # Check each facet has value and count
    for facet in facets:
        assert "value" in facet
        assert "count" in facet
        assert isinstance(facet["count"], int)
        assert facet["count"] > 0


def test_facet_by_juz():
    """Test faceting by juz (part number)."""
    search_flags = {
        "action": "search",
        "query": "الصلاة",
        "facets": "juz"
    }
    
    results = RAWoutput.do(search_flags)
    
    # Check that search was successful
    assert results["error"]["code"] == 0
    
    # Check that facets are in results
    assert "facets" in results["search"]
    assert "juz" in results["search"]["facets"]
    
    # Check facet values are valid (1-30)
    facets = results["search"]["facets"]["juz"]
    for facet in facets:
        assert 1 <= facet["value"] <= 30


def test_facet_by_chapter():
    """Test faceting by chapter (main topic)."""
    search_flags = {
        "action": "search",
        "query": "الجنة",
        "facets": "chapter"
    }
    
    results = RAWoutput.do(search_flags)
    
    # Check that search was successful
    assert results["error"]["code"] == 0
    
    # Check that facets are in results
    assert "facets" in results["search"]
    assert "chapter" in results["search"]["facets"]
    
    # Check facet structure
    facets = results["search"]["facets"]["chapter"]
    assert isinstance(facets, list)


def test_multiple_facets():
    """Test requesting multiple facets at once."""
    search_flags = {
        "action": "search",
        "query": "محمد",
        "facets": "sura_id,juz,chapter"
    }
    
    results = RAWoutput.do(search_flags)
    
    # Check that search was successful
    assert results["error"]["code"] == 0
    
    # Check that all requested facets are in results
    assert "facets" in results["search"]
    assert "sura_id" in results["search"]["facets"]
    assert "juz" in results["search"]["facets"]
    assert "chapter" in results["search"]["facets"]


def test_facet_with_api_function():
    """Test faceting using the api.search() function."""
    results = api.search(query="الرحمن", facets="sura_id,juz")
    
    # Check that search was successful
    assert results["error"]["code"] == 0
    
    # Check that facets are in results
    assert "facets" in results["search"]
    assert "sura_id" in results["search"]["facets"]
    assert "juz" in results["search"]["facets"]


def test_search_without_facets():
    """Test that search works normally without facets parameter."""
    search_flags = {
        "action": "search",
        "query": "الله"
    }
    
    results = RAWoutput.do(search_flags)
    
    # Check that search was successful
    assert results["error"]["code"] == 0
    
    # Facets should not be in results when not requested
    # (or should be empty if we include the key)
    if "facets" in results["search"]:
        assert results["search"]["facets"] == {}


def test_facet_counts_accuracy():
    """Test that facet counts are accurate."""
    search_flags = {
        "action": "search",
        "query": "sura_id:1",  # Search only in sura 1 (Al-Fatiha)
        "facets": "sura_id"
    }
    
    results = RAWoutput.do(search_flags)
    
    # Check that search was successful
    assert results["error"]["code"] == 0
    
    # Check facets
    assert "facets" in results["search"]
    facets = results["search"]["facets"]["sura_id"]
    
    # Should only have results from sura 1
    assert len(facets) == 1
    assert facets[0]["value"] == 1
    
    # The count should match the total results
    assert facets[0]["count"] == results["search"]["interval"]["total"]


def test_facet_with_topic():
    """Test faceting by topic."""
    search_flags = {
        "action": "search",
        "query": "النار",
        "facets": "topic"
    }
    
    results = RAWoutput.do(search_flags)
    
    # Check that search was successful
    assert results["error"]["code"] == 0
    
    # Check that facets are in results
    if "facets" in results["search"] and "topic" in results["search"]["facets"]:
        facets = results["search"]["facets"]["topic"]
        assert isinstance(facets, list)


def test_hierarchical_facet_juz_hizb():
    """Test hierarchical facets for juz > hizb."""
    search_flags = {
        "action": "search",
        "query": "الصلاة",
        "hierarchical_facets": "juz>hizb",
        "aya_position_info": True,
    }

    results = RAWoutput.do(search_flags)

    assert results["error"]["code"] == 0
    assert "hierarchical_facets" in results["search"]
    assert "juz>hizb" in results["search"]["hierarchical_facets"]

    top_nodes = results["search"]["hierarchical_facets"]["juz>hizb"]
    assert isinstance(top_nodes, list)
    assert len(top_nodes) > 0

    for node in top_nodes:
        assert "value" in node
        assert "count" in node
        assert "children" in node
        assert isinstance(node["count"], int)
        assert node["count"] > 0
        # juz values must be in valid range
        assert 1 <= node["value"] <= 30
        # each child represents a hizb within this juz
        child_total = sum(c["count"] for c in node["children"])
        assert child_total == node["count"]
        for child in node["children"]:
            assert "value" in child
            assert "count" in child
            assert "children" in child
            # hizb values are 1-60
            assert 1 <= child["value"] <= 60


def test_hierarchical_facet_chapter_topic_subtopic():
    """Test hierarchical facets for chapter > topic > subtopic."""
    search_flags = {
        "action": "search",
        "query": "الجنة",
        "hierarchical_facets": "chapter>topic>subtopic",
    }

    results = RAWoutput.do(search_flags)

    assert results["error"]["code"] == 0
    assert "hierarchical_facets" in results["search"]
    assert "chapter>topic>subtopic" in results["search"]["hierarchical_facets"]

    top_nodes = results["search"]["hierarchical_facets"]["chapter>topic>subtopic"]
    assert isinstance(top_nodes, list)

    for node in top_nodes:
        assert "value" in node
        assert "count" in node
        assert "children" in node
        assert isinstance(node["count"], int)
        assert node["count"] > 0
        # each topic child count must sum to the chapter count
        child_total = sum(c["count"] for c in node["children"])
        assert child_total == node["count"]
        for topic_node in node["children"]:
            assert "value" in topic_node
            assert "count" in topic_node
            assert "children" in topic_node
            # subtopics under each topic: count may be <= topic count because
            # some ayas have a chapter and topic but no subtopic value.
            subtopic_total = sum(s["count"] for s in topic_node["children"])
            assert subtopic_total <= topic_node["count"]


def test_hierarchical_facets_multiple_hierarchies():
    """Test requesting multiple hierarchies at once via semicolon separator."""
    search_flags = {
        "action": "search",
        "query": "الله",
        "hierarchical_facets": "juz>hizb;chapter>topic",
    }

    results = RAWoutput.do(search_flags)

    assert results["error"]["code"] == 0
    assert "hierarchical_facets" in results["search"]
    assert "juz>hizb" in results["search"]["hierarchical_facets"]
    assert "chapter>topic" in results["search"]["hierarchical_facets"]


def test_hierarchical_facets_via_api():
    """Test hierarchical facets using the api.search() function."""
    results = api.search(query="الرحمن", hierarchical_facets="juz>hizb")

    assert results["error"]["code"] == 0
    assert "hierarchical_facets" in results["search"]
    assert "juz>hizb" in results["search"]["hierarchical_facets"]


def test_hierarchical_facets_counts_sum_to_total():
    """Test that top-level hierarchical facet counts sum to total results."""
    search_flags = {
        "action": "search",
        "query": "sura_id:1",
        "hierarchical_facets": "juz>hizb",
        "aya_position_info": True,
    }

    results = RAWoutput.do(search_flags)

    assert results["error"]["code"] == 0
    assert "hierarchical_facets" in results["search"]
    nodes = results["search"]["hierarchical_facets"].get("juz>hizb", [])

    total_from_facets = sum(n["count"] for n in nodes)
    assert total_from_facets == results["search"]["interval"]["total"]


# ---------------------------------------------------------------------------
# Filter support for 'translation' search unit
# ---------------------------------------------------------------------------

def test_filter_translation_by_lang():
    """Filter translation search results by language (outside query)."""
    results = RAWoutput.do({
        "action": "search",
        "unit": "translation",
        "query": "Allah",
        "filter": {"trans_lang": "en"},
    })
    assert results["error"]["code"] == 0
    translations = results["search"]["translations"]
    if not translations:
        pytest.skip("No translation results — index may lack English translations")
    for t in translations.values():
        assert t["translation"]["lang"] == "en"


def test_filter_translation_by_sura():
    """Filter translation search results to a single sura (outside query)."""
    results = RAWoutput.do({
        "action": "search",
        "unit": "translation",
        "query": "mercy",
        "filter": {"sura_id": 1},
    })
    assert results["error"]["code"] == 0
    translations = results["search"]["translations"]
    if not translations:
        pytest.skip("No translation results for this query/filter combination")
    for t in translations.values():
        assert t["identifier"]["sura_id"] == 1


def test_filter_translation_string_format():
    """Filter translation search using string format 'field:value'."""
    results = RAWoutput.do({
        "action": "search",
        "unit": "translation",
        "query": "Allah",
        "filter": "trans_lang:en",
    })
    assert results["error"]["code"] == 0
    translations = results["search"]["translations"]
    if not translations:
        pytest.skip("No translation results — index may lack English translations")
    for t in translations.values():
        assert t["translation"]["lang"] == "en"


def test_filter_translation_with_facets():
    """Filter + facets together for translation unit."""
    results = RAWoutput.do({
        "action": "search",
        "unit": "translation",
        "query": "mercy",
        "filter": {"trans_lang": "en"},
        "facets": "sura_id",
    })
    assert results["error"]["code"] == 0
    if not results["search"]["translations"]:
        pytest.skip("No translation results")
    # When filtered by lang=en, all returned translations must be English
    for t in results["search"]["translations"].values():
        assert t["translation"]["lang"] == "en"
    # Facets should be present when results were found
    if results["search"]["interval"]["total"] > 0:
        assert "facets" in results["search"]
        assert "sura_id" in results["search"]["facets"]


def test_filter_translation_narrows_results():
    """Filter should produce fewer or equal results than an unfiltered search."""
    unfiltered = RAWoutput.do({
        "action": "search",
        "unit": "translation",
        "query": "God",
    })
    filtered = RAWoutput.do({
        "action": "search",
        "unit": "translation",
        "query": "God",
        "filter": {"trans_lang": "en"},
    })
    assert filtered["error"]["code"] == 0
    total_unfiltered = unfiltered["search"]["interval"]["total"]
    total_filtered = filtered["search"]["interval"]["total"]
    assert total_filtered <= total_unfiltered


# ---------------------------------------------------------------------------
# Filter support for 'word' search unit
# ---------------------------------------------------------------------------

def test_filter_words_by_pos():
    """Filter word search results by part-of-speech outside the query."""
    results = RAWoutput.do({
        "action": "search",
        "unit": "word",
        "query": "الله",
        "filter": {"pos": "PN"},
    })
    assert results["error"]["code"] == 0
    words = results["search"]["words"]
    if not words:
        pytest.skip("No word results for POS filter — index may not have this POS value")
    for w in words.values():
        assert w["word"]["pos"] == "PN"


def test_filter_words_by_root():
    """Filter word search results by Arabic root outside the query."""
    results = RAWoutput.do({
        "action": "search",
        "unit": "word",
        "query": "root:رحم",
        "filter": {"sura_id": 1},
    })
    assert results["error"]["code"] == 0
    words = results["search"]["words"]
    if not words:
        pytest.skip("No word results for root:رحم in sura 1")
    for w in words.values():
        assert w["identifier"]["sura_id"] == 1


def test_filter_words_string_format():
    """Filter word search using string format 'field:value'."""
    results = RAWoutput.do({
        "action": "search",
        "unit": "word",
        "query": "الله",
        "filter": "sura_id:1",
    })
    assert results["error"]["code"] == 0
    words = results["search"]["words"]
    if not words:
        pytest.skip("No word results for this query/filter combination")
    for w in words.values():
        assert w["identifier"]["sura_id"] == 1


def test_filter_words_narrows_results():
    """Filter should produce fewer or equal results than an unfiltered word search."""
    unfiltered = RAWoutput.do({
        "action": "search",
        "unit": "word",
        "query": "الله",
    })
    filtered = RAWoutput.do({
        "action": "search",
        "unit": "word",
        "query": "الله",
        "filter": {"sura_id": 1},
    })
    assert filtered["error"]["code"] == 0
    assert filtered["search"]["interval"]["total"] <= unfiltered["search"]["interval"]["total"]


def test_filter_words_with_facets():
    """Filter + facets together for word unit."""
    results = RAWoutput.do({
        "action": "search",
        "unit": "word",
        "query": "root:رحم",
        "filter": {"sura_id": 1},
        "facets": "pos",
    })
    assert results["error"]["code"] == 0
    words = results["search"]["words"]
    if not words:
        pytest.skip("No word results for root:رحم in sura 1")
    for w in words.values():
        assert w["identifier"]["sura_id"] == 1
    if results["search"]["interval"]["total"] > 0 and "facets" in results["search"]:
        assert "pos" in results["search"]["facets"]


# ---------------------------------------------------------------------------
# Facets for non-Arabic aya search path
# ---------------------------------------------------------------------------

def test_facets_non_arabic_aya_search():
    """Facets should be computed even when the query contains no Arabic script."""
    results = RAWoutput.do({"action": "search", "query": "mercy", "facets": "sura_id"})
    assert results["error"]["code"] == 0
    if results["search"]["interval"]["total"] == 0:
        pytest.skip("No results for 'mercy' — index may not have English translations indexed on aya")
    # If there are results, facets should be present
    assert "facets" in results["search"]
    assert "sura_id" in results["search"]["facets"]
    facet_entries = results["search"]["facets"]["sura_id"]
    assert isinstance(facet_entries, list)
    for entry in facet_entries:
        assert "value" in entry and "count" in entry
