"""
Test module for translation fields in main index.
This tests that translations are properly indexed in the main aya index.
"""

from alfanous.engines import QuranicSearchEngine
from alfanous import paths
from whoosh.qparser import QueryParser


QSE = QuranicSearchEngine(paths.QSE_INDEX)


def test_translation_fields_exist():
    """Test that translation fields are present in the index schema."""
    schema = QSE._schema
    assert 'translation_en_shakir' in schema.names(), "translation_en_shakir field not found in schema"
    assert 'translation_en_transliteration' in schema.names(), "translation_en_transliteration field not found in schema"


def test_translation_data_indexed():
    """Test that translation data is actually indexed."""
    searcher = QSE._docindex.get_searcher()()
    
    # Get the first verse
    doc = searcher.document(gid=1)
    assert doc is not None, "Could not retrieve first verse"
    
    # Check Shakir translation
    shakir = doc.get('translation_en_shakir')
    assert shakir is not None, "Shakir translation not found"
    assert 'Allah' in shakir, "Expected 'Allah' in Shakir translation"
    assert 'Beneficent' in shakir or 'beneficent' in shakir.lower(), "Expected 'Beneficent' in Shakir translation"
    
    # Check transliteration
    transliteration = doc.get('translation_en_transliteration')
    assert transliteration is not None, "Transliteration not found"
    assert 'Bismi' in transliteration, "Expected 'Bismi' in transliteration"
    
    searcher.close()


def test_search_in_translation_field():
    """Test that we can search in translation fields."""
    searcher = QSE._docindex.get_searcher()()
    
    # Search for "Allah" in Shakir translation
    qp = QueryParser("translation_en_shakir", QSE._schema)
    q = qp.parse("Allah")
    results = searcher.search(q, limit=10)
    
    assert len(results) > 0, "No results found for 'Allah' in translation_en_shakir"
    
    # Verify results contain the search term
    for hit in results[:5]:
        translation_text = hit.get('translation_en_shakir', '')
        assert 'Allah' in translation_text, f"Search result does not contain 'Allah': {translation_text[:100]}"
    
    searcher.close()


def test_verse_count_with_translations():
    """Test that all 6236 verses have translations."""
    searcher = QSE._docindex.get_searcher()()
    
    # Count total documents
    total_docs = searcher.doc_count_all()
    assert total_docs == 6236, f"Expected 6236 verses, got {total_docs}"
    
    # Sample check: verify some verses have translations
    for gid in [1, 100, 1000, 6236]:
        doc = searcher.document(gid=gid)
        assert doc is not None, f"Could not retrieve verse {gid}"
        
        shakir = doc.get('translation_en_shakir')
        assert shakir is not None and len(shakir) > 0, f"Verse {gid} missing Shakir translation"
        
        transliteration = doc.get('translation_en_transliteration')
        assert transliteration is not None and len(transliteration) > 0, f"Verse {gid} missing transliteration"
    
    searcher.close()
