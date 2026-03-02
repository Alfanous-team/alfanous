#!/usr/bin/env python3
# coding: utf-8

"""
Test AI Query Translation Rules Integration with Show Endpoint
"""

from alfanous.api import get_info
from alfanous.outputs import Raw


def test_ai_rules_in_show_all():
    """Test that AI rules are accessible via get_info('all')"""
    result = get_info('all')
    
    assert 'show' in result, "Response should contain 'show' key"
    assert 'ai_query_translation_rules' in result['show'], \
        "AI rules should be in show endpoint"
    
    ai_rules = result['show']['ai_query_translation_rules']
    assert isinstance(ai_rules, dict), "AI rules should be a dictionary"
    assert 'content' in ai_rules, "AI rules should contain 'content' key"
    assert 'length' in ai_rules, "AI rules should contain 'length' key"
    assert 'lines' in ai_rules, "AI rules should contain 'lines' key"
    
    # Verify content is not empty
    assert ai_rules['length'] > 0, "AI rules content should not be empty"
    assert ai_rules['lines'] > 0, "AI rules should have lines"
    assert len(ai_rules['content']) > 0, "AI rules content should have text"


def test_ai_rules_specific_query():
    """Test that AI rules can be queried specifically"""
    result = get_info('ai_query_translation_rules')
    
    assert 'show' in result, "Response should contain 'show' key"
    assert 'ai_query_translation_rules' in result['show'], \
        "AI rules should be queryable specifically"
    
    ai_rules = result['show']['ai_query_translation_rules']
    assert isinstance(ai_rules, dict), "AI rules should be a dictionary"
    assert 'content' in ai_rules, "AI rules should contain content"


def test_ai_rules_raw_show_method():
    """Test that Raw._show() method exposes AI rules"""
    raw = Raw()
    
    # Test with 'all'
    result = raw._show({'query': 'all'})
    assert 'show' in result, "Response should contain 'show' key"
    assert 'ai_query_translation_rules' in result['show'], \
        "AI rules should be in Raw._show() result"
    
    # Test specific query
    result2 = raw._show({'query': 'ai_query_translation_rules'})
    assert 'show' in result2, "Response should contain 'show' key"
    assert 'ai_query_translation_rules' in result2['show'], \
        "AI rules should be queryable via Raw._show()"


def test_ai_rules_content_structure():
    """Test the structure of AI rules content"""
    result = get_info('ai_query_translation_rules')
    ai_rules = result['show']['ai_query_translation_rules']
    
    # Check content starts with expected header
    content = ai_rules['content']
    assert content.startswith('AI RULES FOR TRANSLATING HUMAN LANGUAGE'), \
        "Content should start with expected header"
    
    # Check metadata matches content
    actual_lines = len(content.split('\n'))
    assert ai_rules['lines'] == actual_lines, \
        f"Lines count should match actual lines in content"
    
    actual_length = len(content)
    assert ai_rules['length'] == actual_length, \
        f"Length should match actual content length"


if __name__ == "__main__":
    # Run tests
    test_ai_rules_in_show_all()
    print("✓ AI rules accessible via get_info('all')")
    
    test_ai_rules_specific_query()
    print("✓ AI rules queryable specifically")
    
    test_ai_rules_raw_show_method()
    print("✓ AI rules exposed via Raw._show() method")
    
    test_ai_rules_content_structure()
    print("✓ AI rules content structure is correct")
    
    print("\nAll show endpoint integration tests passed!")
