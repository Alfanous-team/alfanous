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
    """Test synonyms plugin (~word) - Example from README: ~synonym search"""
    parser = create_test_parser()
    query = parser.parse("~جحيم")
    assert isinstance(query, SynonymsQuery)
    assert query.text == "جحيم"
    # Verify it's a synonym query
    assert query.fieldname == "text"


def test_antonyms_plugin():
    """Test antonyms plugin (#word) - Arabic antonym search"""
    parser = create_test_parser()
    query = parser.parse("#جحيم")
    assert isinstance(query, AntonymsQuery)
    assert query.text == "جحيم"
    # Currently returns original word (placeholder implementation)
    assert query.words == ["جحيم"]


def test_derivation_plugin_single():
    """Test derivation plugin with single > (>word) - Example from README: >مالك"""
    parser = create_test_parser()
    query = parser.parse(">مالك")
    assert isinstance(query, DerivationQuery)
    assert query.level == 1
    assert query.text == "مالك"
    # Lemma level derivation


def test_derivation_plugin_double():
    """Test derivation plugin with double >> (>>word) - Example from README: >>مالك"""
    parser = create_test_parser()
    query = parser.parse(">>مالك")
    assert isinstance(query, DerivationQuery)
    assert query.level == 2
    assert query.text == "مالك"
    # Root level derivation


def test_spell_errors_plugin():
    """Test spell errors plugin (%word) - Example: %عاصم"""
    parser = create_test_parser()
    query = parser.parse("%عاصم")
    assert isinstance(query, SpellErrorsQuery)
    assert query.text == "عاصم"
    # Should handle spelling variations


def test_tashkil_plugin_single_word():
    """Test tashkil plugin with single word ('word') - Partial vocalization example"""
    parser = create_test_parser()
    query = parser.parse("'مَن'")
    assert isinstance(query, TashkilQuery)
    assert "مَن" in query.text or query.text == ["مَن"]


def test_tashkil_plugin_multiple_words():
    """Test tashkil plugin with multiple words ('word1 word2') - Example: 'لو كان البحر'"""
    parser = create_test_parser()
    query = parser.parse("'لو كان البحر'")
    assert isinstance(query, TashkilQuery)
    # Should parse multiple words
    assert len(query.text) >= 3


def test_tuple_plugin_single_item():
    """Test tuple plugin with single item ({item}) - Single morphological property"""
    parser = create_test_parser()
    query = parser.parse("{ملك}")
    assert isinstance(query, TupleQuery)
    assert query.props.get("root") == "ملك"


def test_tuple_plugin_multiple_items():
    """Test tuple plugin with multiple items - Example from README: {قول،اسم}"""
    parser = create_test_parser()
    query = parser.parse("{قول،اسم}")
    assert isinstance(query, TupleQuery)
    # Should have root and type properties
    assert query.props.get("root") == "قول"
    assert query.props.get("type") == "اسم"


def test_tuple_plugin_root_and_type():
    """Test tuple plugin with root and type - Example from README: {ملك،فعل}"""
    parser = create_test_parser()
    query = parser.parse("{ملك،فعل}")
    assert isinstance(query, TupleQuery)
    assert query.props.get("root") == "ملك"
    assert query.props.get("type") == "فعل"
    # This should find words with root ملك and type فعل


def test_arabic_wildcard_asterisk():
    """Test Arabic wildcard with * - Example from README: *نبي*"""
    parser = create_test_parser()
    query = parser.parse("*نبي*")
    # Should be parsed as ArabicWildcardQuery or standard Wildcard
    assert query is not None
    assert hasattr(query, 'text')


def test_arabic_wildcard_question_mark():
    """Test Arabic wildcard with Arabic question mark - Example from README: نعم؟"""
    parser = create_test_parser()
    query = parser.parse("نعم؟")
    assert isinstance(query, ArabicWildcardQuery)
    # Should convert ؟ to ?
    assert query.text == "نعم?"


def test_multiple_plugins_combination():
    """Test combination of multiple plugins - Example: AND/OR logic from README"""
    parser = create_test_parser()
    
    # Test AND combination - Example: الصلاة + الزكاة
    query = parser.parse("الصلاة AND الزكاة")
    assert query is not None
    
    # Test OR combination - Example: الصلاة | الزكاة
    query = parser.parse("الصلاة OR الزكاة")
    assert query is not None


def test_simple_arabic_search():
    """Test simple Arabic search - Example from README: الحمد"""
    parser = create_test_parser()
    query = parser.parse("الحمد")
    assert query is not None
    # Should parse as simple term


def test_phrase_search():
    """Test phrase search - Example from README: "الحمد لله" """
    parser = create_test_parser()
    query = parser.parse('"الحمد لله"')
    assert query is not None
    # Should be parsed as phrase query


def test_query_normalization():
    """Test that queries can be normalized (hash/eq work)"""
    parser = create_test_parser()
    query1 = parser.parse("~الله")
    query2 = parser.parse("~الله")
    
    # Test hash works
    hash(query1)
    hash(query2)
    
    # Test equality
    assert query1 == query2


def test_complex_query():
    """Test complex query with multiple features from README"""
    parser = create_test_parser()
    
    # Test derivation
    query = parser.parse(">>الصلاة")
    assert isinstance(query, DerivationQuery)
    assert query.text == "الصلاة"
    
    # Test synonym
    query = parser.parse("~الله")
    assert isinstance(query, SynonymsQuery)
    assert query.text == "الله"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
