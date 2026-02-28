"""
Test linguistic operations in Alfanous API
"""

import alfanous.api as api


def test_linguistic_vocalize():
    """Test vocalization operation"""
    result = api.linguistic('الحمد لله', 'vocalize')
    
    # Check structure
    assert 'error' in result
    assert result['error']['code'] == 0
    assert 'linguistic' in result
    
    linguistic_data = result['linguistic']
    assert 'text' in linguistic_data
    assert 'vocalized' in linguistic_data
    assert 'operation' in linguistic_data
    
    # Check content
    assert linguistic_data['text'] == 'الحمد لله'
    assert linguistic_data['operation'] == 'vocalize'
    # The vocalized text should contain tashkeel marks
    assert 'َ' in linguistic_data['vocalized'] or 'ُ' in linguistic_data['vocalized'] or 'ِ' in linguistic_data['vocalized']


def test_linguistic_vocalize_single_word():
    """Test vocalization with single word"""
    result = api.linguistic('الحمد', 'vocalize')
    
    linguistic_data = result['linguistic']
    assert linguistic_data['text'] == 'الحمد'
    assert linguistic_data['vocalized'] == 'الْحَمْدُ'
    assert linguistic_data['operation'] == 'vocalize'


def test_linguistic_derive():
    """Test derivation operation"""
    result = api.linguistic('الحمد', 'derive')
    
    # Check structure
    assert 'error' in result
    assert result['error']['code'] == 0
    assert 'linguistic' in result
    
    linguistic_data = result['linguistic']
    assert 'text' in linguistic_data
    assert 'words' in linguistic_data
    assert 'operation' in linguistic_data
    
    # Check content
    assert linguistic_data['text'] == 'الحمد'
    assert linguistic_data['operation'] == 'derive'
    assert len(linguistic_data['words']) == 1
    
    word_info = linguistic_data['words'][0]
    assert 'word' in word_info
    assert 'lemma' in word_info
    assert 'root' in word_info
    assert 'lemma_derivations' in word_info
    assert 'root_derivations' in word_info
    
    assert word_info['word'] == 'الحمد'
    assert word_info['lemma'] == 'حمد'
    assert word_info['root'] == 'حمد'
    assert isinstance(word_info['lemma_derivations'], list)
    assert isinstance(word_info['root_derivations'], list)


def test_linguistic_derive_multiple_words():
    """Test derivation with multiple words"""
    result = api.linguistic('الحمد لله', 'derive')
    
    linguistic_data = result['linguistic']
    assert linguistic_data['text'] == 'الحمد لله'
    assert len(linguistic_data['words']) == 2
    
    # Check first word
    assert linguistic_data['words'][0]['word'] == 'الحمد'
    assert linguistic_data['words'][0]['lemma'] == 'حمد'
    
    # Check second word
    assert linguistic_data['words'][1]['word'] == 'لله'


def test_linguistic_via_do():
    """Test linguistic operations via do() function"""
    # Test vocalize via do
    result = api.do({
        "action": "linguistic",
        "query": "الحمد",
        "operation": "vocalize"
    })
    assert result['linguistic']['vocalized'] == 'الْحَمْدُ'
    
    # Test derive via do
    result = api.do({
        "action": "linguistic",
        "query": "الحمد",
        "operation": "derive"
    })
    assert result['linguistic']['words'][0]['root'] == 'حمد'


def test_linguistic_default_operation():
    """Test that default operation is vocalize"""
    result = api.linguistic('الحمد')
    linguistic_data = result['linguistic']
    assert linguistic_data['operation'] == 'vocalize'


def test_linguistic_empty_query():
    """Test linguistic operation with empty query"""
    result = api.linguistic('', 'vocalize')
    linguistic_data = result['linguistic']
    assert 'error' in linguistic_data


def test_linguistic_unknown_operation():
    """Test linguistic operation with unknown operation type"""
    result = api.do({
        "action": "linguistic",
        "query": "test",
        "operation": "unknown_operation"
    })
    linguistic_data = result['linguistic']
    assert 'error' in linguistic_data
