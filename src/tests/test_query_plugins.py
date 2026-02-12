"""
Tests for Whoosh 2.7 plugin-based query parser implementation
"""
import pytest
from whoosh.qparser import QueryParser
from whoosh.fields import Schema, TEXT

from alfanous.query_plugins import (
    SynonymsPlugin,
    AntonymsPlugin,
    DerivationPlugin,
    SpellErrorsPlugin,
    TashkilPlugin,
    TuplePlugin,
    ArabicWildcardPlugin,
    SynonymsQuery,
    AntonymsQuery,
    DerivationQuery,
    SpellErrorsQuery,
    TashkilQuery,
    TupleQuery,
    ArabicWildcardQuery
)


def create_test_parser():
    """Create a test parser with all plugins"""
    from whoosh.qparser.plugins import SingleQuotePlugin
    
    schema = Schema(text=TEXT(stored=True))
    parser = QueryParser('text', schema)
    
    # Remove SingleQuotePlugin to allow our TashkilPlugin to work
    parser.remove_plugin_class(SingleQuotePlugin)
    
    # Add all plugins
    parser.add_plugin(SynonymsPlugin)
    parser.add_plugin(AntonymsPlugin)
    parser.add_plugin(DerivationPlugin)
    parser.add_plugin(SpellErrorsPlugin)
    parser.add_plugin(TashkilPlugin)
    parser.add_plugin(TuplePlugin)
    parser.add_plugin(ArabicWildcardPlugin)
    
    return parser


def test_synonyms_plugin():
    """Test synonyms plugin (~word)"""
    parser = create_test_parser()
    query = parser.parse("~test")
    assert isinstance(query, SynonymsQuery)
    assert query.text == "test"


def test_antonyms_plugin():
    """Test antonyms plugin (#word)"""
    parser = create_test_parser()
    query = parser.parse("#test")
    assert isinstance(query, AntonymsQuery)
    assert query.text == "test"


def test_derivation_plugin_single():
    """Test derivation plugin with single > (>word)"""
    parser = create_test_parser()
    query = parser.parse(">test")
    assert isinstance(query, DerivationQuery)
    assert query.level == 1


def test_derivation_plugin_double():
    """Test derivation plugin with double >> (>>word)"""
    parser = create_test_parser()
    query = parser.parse(">>test")
    assert isinstance(query, DerivationQuery)
    assert query.level == 2


def test_spell_errors_plugin():
    """Test spell errors plugin (%word)"""
    parser = create_test_parser()
    query = parser.parse("%test")
    assert isinstance(query, SpellErrorsQuery)
    assert query.text == "test"


def test_tashkil_plugin_single_word():
    """Test tashkil plugin with single word ('word')"""
    parser = create_test_parser()
    query = parser.parse("'test'")
    assert isinstance(query, TashkilQuery)
    assert 'test' in query.text or query.text == ['test']


def test_tashkil_plugin_multiple_words():
    """Test tashkil plugin with multiple words ('word1 word2')"""
    parser = create_test_parser()
    query = parser.parse("'hello world'")
    assert isinstance(query, TashkilQuery)


def test_tuple_plugin_single_item():
    """Test tuple plugin with single item ({item})"""
    parser = create_test_parser()
    query = parser.parse("{test}")
    assert isinstance(query, TupleQuery)


def test_tuple_plugin_multiple_items():
    """Test tuple plugin with multiple items ({item1,item2,item3})"""
    parser = create_test_parser()
    query = parser.parse("{test1,test2,test3}")
    assert isinstance(query, TupleQuery)


def test_tuple_plugin_arabic_comma():
    """Test tuple plugin with Arabic comma ({item1،item2})"""
    parser = create_test_parser()
    query = parser.parse("{test1،test2}")
    assert isinstance(query, TupleQuery)


def test_arabic_wildcard_asterisk():
    """Test Arabic wildcard with * (te*t)"""
    parser = create_test_parser()
    query = parser.parse("te*t")
    # Should be parsed as ArabicWildcardQuery or standard Wildcard
    assert query is not None


def test_arabic_wildcard_question_mark():
    """Test Arabic wildcard with Arabic question mark (te؟t)"""
    parser = create_test_parser()
    query = parser.parse("te؟t")
    assert isinstance(query, ArabicWildcardQuery)


def test_multiple_plugins_combination():
    """Test combination of multiple plugins in one query"""
    parser = create_test_parser()
    
    # Test AND combination
    query = parser.parse("~synonym AND >derivation")
    assert query is not None
    
    # Test OR combination  
    query = parser.parse("#antonym OR %spellerror")
    assert query is not None


def test_plugin_with_regular_words():
    """Test that regular words still work with plugins enabled"""
    parser = create_test_parser()
    query = parser.parse("regular word")
    assert query is not None


def test_query_normalization():
    """Test that queries can be normalized (hash/eq work)"""
    parser = create_test_parser()
    query1 = parser.parse("~test")
    query2 = parser.parse("~test")
    
    # Test hash works
    hash(query1)
    hash(query2)
    
    # Test equality
    assert query1 == query2


def test_arabic_text_parsing():
    """Test parsing Arabic text with plugins"""
    parser = create_test_parser()
    
    # Test Arabic synonym
    query = parser.parse("~الله")
    assert isinstance(query, SynonymsQuery)
    
    # Test Arabic derivation
    query = parser.parse(">>الصلاة")
    assert isinstance(query, DerivationQuery)
    
    # Test Arabic tuple
    query = parser.parse("{ملك،فعل}")
    assert isinstance(query, TupleQuery)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
