"""
This is a test module for the keywords endpoint feature.
Tests the ability to query top most frequent keywords or all unique keywords in a field.
"""

from alfanous import api


def test_keywords_top_frequent_default():
    """Test getting all unique keywords in default field (aya_) by default"""
    result = api.do({'action': 'show', 'query': 'keywords'})
    
    assert 'show' in result
    assert result['error']['code'] == 0
    
    show_data = result['show']
    assert show_data['field'] == 'aya_'
    assert show_data['mode'] == 'unique'
    assert show_data['count'] == 17574  # Total unique words in aya_ field
    assert len(show_data['keywords']) == 17574
    
    # Check that it returns a list of unique words
    assert isinstance(show_data['keywords'], list)
    assert 'مِنْ' in show_data['keywords']


def test_keywords_top_frequent_custom_limit():
    """Test getting top N most frequent keywords with custom limit and explicit mode"""
    result = api.do({'action': 'show', 'query': 'keywords', 'field': 'topic', 'mode': 'frequent', 'limit': 5})
    
    assert 'show' in result
    assert result['error']['code'] == 0
    
    show_data = result['show']
    assert show_data['field'] == 'topic'
    assert show_data['mode'] == 'frequent'
    assert show_data['limit'] == 5
    assert show_data['count'] == 5
    assert len(show_data['keywords']) == 5


def test_keywords_all_unique():
    """Test getting all unique keywords in a field"""
    result = api.do({'action': 'show', 'query': 'keywords', 'field': 'sura_type', 'mode': 'unique'})
    
    assert 'show' in result
    assert result['error']['code'] == 0
    
    show_data = result['show']
    assert show_data['field'] == 'sura_type'
    assert show_data['mode'] == 'unique'
    assert show_data['count'] == 2
    assert len(show_data['keywords']) == 2
    assert set(show_data['keywords']) == {'Meccan', 'Medinan'}


def test_keywords_chapter_field_unique():
    """Test getting all unique keywords in chapter field"""
    result = api.do({'action': 'show', 'query': 'keywords', 'field': 'chapter', 'mode': 'unique'})
    
    assert 'show' in result
    assert result['error']['code'] == 0
    
    show_data = result['show']
    assert show_data['field'] == 'chapter'
    assert show_data['mode'] == 'unique'
    assert show_data['count'] == 50
    assert len(show_data['keywords']) == 50
    assert 'الإيمان' in show_data['keywords']


def test_keywords_topic_field_unique():
    """Test getting all unique keywords in topic field"""
    result = api.do({'action': 'show', 'query': 'keywords', 'field': 'topic', 'mode': 'unique'})
    
    assert 'show' in result
    assert result['error']['code'] == 0
    
    show_data = result['show']
    assert show_data['field'] == 'topic'
    assert show_data['mode'] == 'unique'
    assert show_data['count'] == 751
    assert len(show_data['keywords']) == 751


def test_keywords_sura_id_field():
    """Test getting unique sura IDs"""
    result = api.do({'action': 'show', 'query': 'keywords', 'field': 'sura_id', 'mode': 'unique'})
    
    assert 'show' in result
    assert result['error']['code'] == 0
    
    show_data = result['show']
    assert show_data['field'] == 'sura_id'
    assert show_data['mode'] == 'unique'
    assert show_data['count'] == 114
    assert len(show_data['keywords']) == 114
    # Verify it's a list of integers from 1 to 114
    assert show_data['keywords'] == list(range(1, 115))


def test_keywords_frequent_subject_field():
    """Test getting most frequent keywords in subject field with explicit mode"""
    result = api.do({'action': 'show', 'query': 'keywords', 'field': 'subject', 'mode': 'frequent', 'limit': 15})
    
    assert 'show' in result
    assert result['error']['code'] == 0
    
    show_data = result['show']
    assert show_data['field'] == 'subject'
    assert show_data['mode'] == 'frequent'
    assert show_data['limit'] == 15
    assert show_data['count'] == 15
    assert len(show_data['keywords']) == 15
    
    # Verify structure
    for keyword in show_data['keywords']:
        assert 'word' in keyword
        assert 'frequency' in keyword
        assert keyword['frequency'] > 0


def test_keywords_invalid_limit_parameter():
    """Test that invalid limit parameter defaults to 20 when in frequent mode"""
    result = api.do({'action': 'show', 'query': 'keywords', 'field': 'aya_', 'mode': 'frequent', 'limit': 'invalid'})
    
    assert 'show' in result
    assert result['error']['code'] == 0
    
    show_data = result['show']
    assert show_data['mode'] == 'frequent'
    assert show_data['limit'] == 20  # Should default to 20
    assert show_data['count'] == 20


def test_keywords_default_unit():
    """Test that default unit is 'aya'"""
    result = api.do({'action': 'show', 'query': 'keywords', 'field': 'sura_type'})
    
    assert 'show' in result
    assert result['error']['code'] == 0
    
    show_data = result['show']
    assert show_data['unit'] == 'aya'
    assert show_data['field'] == 'sura_type'
    assert show_data['count'] == 2


def test_keywords_explicit_aya_unit():
    """Test explicit aya unit with frequent mode"""
    result = api.do({'action': 'show', 'query': 'keywords', 'unit': 'aya', 'field': 'topic', 'mode': 'frequent', 'limit': 5})
    
    assert 'show' in result
    assert result['error']['code'] == 0
    
    show_data = result['show']
    assert show_data['unit'] == 'aya'
    assert show_data['field'] == 'topic'
    assert show_data['mode'] == 'frequent'
    assert show_data['limit'] == 5
    assert show_data['count'] == 5
    assert len(show_data['keywords']) == 5


def test_keywords_translation_unit_unique():
    """Test translation unit with unique mode"""
    result = api.do({'action': 'show', 'query': 'keywords', 'unit': 'translation', 'field': 'id', 'mode': 'unique'})
    
    assert 'show' in result
    assert result['error']['code'] == 0
    
    show_data = result['show']
    assert show_data['unit'] == 'translation'
    assert show_data['field'] == 'id'
    assert show_data['mode'] == 'unique'
    assert show_data['count'] > 0
    assert len(show_data['keywords']) == show_data['count']
    # Check that translation IDs are returned
    assert all(isinstance(keyword, str) for keyword in show_data['keywords'])


def test_keywords_translation_unit_frequent():
    """Test translation unit with frequent mode"""
    result = api.do({'action': 'show', 'query': 'keywords', 'unit': 'translation', 'field': 'text', 'mode': 'frequent', 'limit': 10})
    
    assert 'show' in result
    assert result['error']['code'] == 0
    
    show_data = result['show']
    assert show_data['unit'] == 'translation'
    assert show_data['field'] == 'text'
    assert show_data['mode'] == 'frequent'
    assert show_data['limit'] == 10
    assert show_data['count'] == 10
    assert len(show_data['keywords']) == 10
    
    # Verify structure
    for keyword in show_data['keywords']:
        assert 'word' in keyword
        assert 'frequency' in keyword
        assert keyword['frequency'] > 0


def test_keywords_word_unit_unavailable():
    """Test that word unit returns appropriate error when unavailable"""
    result = api.do({'action': 'show', 'query': 'keywords', 'unit': 'word'})
    
    assert 'show' in result
    assert result['error']['code'] == 0
    
    show_data = result['show']
    assert show_data['unit'] == 'word'
    assert show_data['count'] == 0
    assert 'error' in show_data
    assert 'not available' in show_data['error'].lower()

