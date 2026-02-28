"""
This is a test module for the keywords endpoint feature.
Tests the ability to query top most frequent keywords or all unique keywords in a field.
"""

from alfanous import api


def test_keywords_top_frequent_default():
    """Test getting top 20 most frequent keywords in default field (aya_)"""
    result = api.do({'action': 'show', 'query': 'keywords'})
    
    assert 'show' in result
    assert result['error']['code'] == 0
    
    show_data = result['show']
    assert show_data['field'] == 'aya_'
    assert show_data['mode'] == 'frequent'
    assert show_data['limit'] == 20
    assert show_data['count'] == 20
    assert len(show_data['keywords']) == 20
    
    # Check structure of keywords
    first_keyword = show_data['keywords'][0]
    assert 'word' in first_keyword
    assert 'frequency' in first_keyword
    assert isinstance(first_keyword['frequency'], int)
    
    # Check that the most frequent word is correct
    assert first_keyword['word'] == 'مِنْ'
    assert first_keyword['frequency'] == 1673


def test_keywords_top_frequent_custom_limit():
    """Test getting top N most frequent keywords with custom limit"""
    result = api.do({'action': 'show', 'query': 'keywords', 'field': 'topic', 'limit': 5})
    
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
    """Test getting most frequent keywords in subject field"""
    result = api.do({'action': 'show', 'query': 'keywords', 'field': 'subject', 'limit': 15})
    
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
