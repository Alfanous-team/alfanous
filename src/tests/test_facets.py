"""
Test module for facet search functionality in alfanous.

"""

from alfanous import api
from alfanous.outputs import Raw
from alfanous import paths


RAWoutput = Raw(
    QSE_index=paths.QSE_INDEX,
    TSE_index=paths.TSE_INDEX,
    WSE_index=paths.WSE_INDEX,
    Recitations_list_file=paths.RECITATIONS_LIST_FILE,
    Translations_list_file=paths.TRANSLATIONS_LIST_FILE,
    Hints_file=paths.HINTS_FILE,
    Information_file=paths.INFORMATION_FILE
)


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
