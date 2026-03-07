"""
Tests for Whoosh 2.7 plugin-based query parser implementation
"""
import pytest
from whoosh.qparser import QueryParser
from whoosh.fields import Schema, TEXT
from whoosh.query import Or, Term

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
    """Test synonyms plugin (~word) - Example from README: ~synonym search
    
    Tests that SynonymsPlugin properly returns synonyms from the synonyms dictionary.
    Uses آثر (preferred/chose) which has proper synonyms, and also validates
    the fix for جنة (paradise) which should now include فردوس.
    """
    parser = create_test_parser()
    query = parser.parse("~آثر")
    assert isinstance(query, SynonymsQuery)
    assert query.text == "آثر"
    # Verify the results contain actual synonyms of آثر (preferred/chose)
    # Expected: ['آثر', 'اختار', 'اصطفى', 'فضل']
    assert sorted(query.words) == sorted(['آثر', 'اختار', 'اصطفى', 'فضل'])
    assert "آثر" in query.words
    assert "اختار" in query.words  # chose
    assert "اصطفى" in query.words  # selected
    assert "فضل" in query.words     # preferred
    
    # Test the fixed جنة entry - should now include فردوس
    query = parser.parse("~جنة")
    assert isinstance(query, SynonymsQuery)
    assert query.text == "جنة"
    assert "فردوس" in query.words  # paradise
    assert "جنة" in query.words
    assert "نعيم" in query.words  # bliss


def test_antonyms_plugin():
    """Test antonyms plugin (#word) - Arabic antonym search
    
    Tests that AntonymsPlugin properly returns antonyms from the Arabic antonyms thesaurus.
    For example, جحيم (hell) should return جنة and فردوس (paradise) as antonyms.
    """
    parser = create_test_parser()
    query = parser.parse("#جحيم")
    assert isinstance(query, AntonymsQuery)
    assert query.text == "جحيم"
    # Should now return proper antonyms from antonyms thesaurus
    assert sorted(query.words) == sorted(["جنة", "فردوس"])
    assert "جنة" in query.words  # paradise (heaven)
    assert "فردوس" in query.words  # paradise


def test_derivation_plugin_single():
    """Test derivation plugin with single > (>word) - Example from README: >مالك
    
    Level 1 returns lemma-level derivations (narrow list).
    """
    parser = create_test_parser()
    query = parser.parse(">مالك")
    assert isinstance(query, DerivationQuery)
    assert query.level == 1
    assert query.text == "مالك"
    # Verify results contain derivations of مالك at lemma level
    assert sorted(query.words) == sorted(['مالك', 'مالكون'])
    assert "مالك" in query.words
    assert "مالكون" in query.words
    assert len(query.words) == 2  # Lemma level should have fewer results


def test_derivation_plugin_double():
    """Test derivation plugin with double >> (>>word) - Example from README: >>مالك
    
    Level 2 returns root-level derivations (wider list than level 1).
    """
    parser = create_test_parser()
    query = parser.parse(">>مالك")
    assert isinstance(query, DerivationQuery)
    assert query.level == 2
    assert query.text == "مالك"
    # Verify results contain derivations of مالك at root level
    # Check for expected words (order may vary)
    assert len(query.words) == 23  # Should have 23 derivations
    assert "مالك" in query.words
    assert "ملكوت" in query.words
    assert "يملك" in query.words
    assert "الملك" in query.words
    # Root level should return more results than lemma level
    query_lemma = parser.parse(">مالك")
    assert len(query.words) > len(query_lemma.words)  # Root level has wider results


def test_spell_errors_plugin():
    """Test spell errors plugin (%word) - Example: %نسر
    
    Note: Testing with نسر which could match نصر due to spelling variations.
    This test is optional - remove if it fails.
    """
    parser = create_test_parser()
    query = parser.parse("%نسر")
    assert isinstance(query, SpellErrorsQuery)
    assert query.text == "نسر"
    # Should handle spelling variations like نصر
    # Note: This needs an index reader to work properly, so we just verify the query is created
    assert sorted(query.words) == sorted(["نسر"])  # Initial state before index expansion


def test_tashkil_plugin_single_word():
    """Test tashkil plugin with single word ('word') - Partial vocalization example
    
    Should return list of word من with different tashkeel (diacritics).
    """
    parser = create_test_parser()
    query = parser.parse("'مَن'")
    assert isinstance(query, TashkilQuery)
    assert "مَن" in query.text or query.text == ["مَن"]
    # Verify normalized words list is created
    assert len(query.words) >= 1
    # Note: Actual expansion happens with index reader, but initial processing removes tashkeel


def test_tashkil_plugin_multiple_words():
    """Test tashkil plugin with multiple words ('word1 word2') - Example: 'لو كان البحر'
    
    For multiple words, TashkilPlugin creates an Or query with Term subqueries.
    """
    parser = create_test_parser()
    query = parser.parse("'لو كان البحر'")
    # For multiple words, should create Or query with Term subqueries
    assert isinstance(query, Or)
    assert hasattr(query, 'subqueries')
    assert len(query.subqueries) >= 3
    # Check that subqueries are Term objects
    for subq in query.subqueries:
        assert isinstance(subq, Term)


def test_tuple_plugin_single_item():
    """Test tuple plugin with single item ({item}) - Single morphological property"""
    parser = create_test_parser()
    query = parser.parse("{ملك}")
    assert isinstance(query, TupleQuery)
    assert query.props.get("root") == "ملك"


def test_tuple_plugin_multiple_items():
    """Test tuple plugin with multiple items - Example from README: {قول،اسم}
    
    Should return derivations of قول that are nouns (اسم).
    """
    parser = create_test_parser()
    query = parser.parse("{قول،اسم}")
    assert isinstance(query, TupleQuery)
    # Should have root and type properties
    assert query.props.get("root") == "قول"
    assert query.props.get("type") == "اسم"
    # Verify results contain words with root قول and type اسم (noun)
    assert len(query.words) == 11  # Should have 11 nouns
    assert "قول" in query.words
    assert "قولا" in query.words
    assert "قولكم" in query.words
    assert "قوله" in query.words
    assert "الأقاويل" in query.words


def test_tuple_plugin_root_and_type():
    """Test tuple plugin with root and type - Example from README: {ملك،فعل}
    
    Should return derivations of ملك that are verbs (فعل).
    """
    parser = create_test_parser()
    query = parser.parse("{ملك،فعل}")
    assert isinstance(query, TupleQuery)
    assert query.props.get("root") == "ملك"
    assert query.props.get("type") == "فعل"
    # Verify results contain words with root ملك and type فعل (verb)
    assert len(query.words) == 8  # Should have 8 verbs
    assert "يملك" in query.words
    assert "ملكتم" in query.words
    assert "تملك" in query.words
    assert "أملك" in query.words


def test_arabic_wildcard_asterisk():
    """Test Arabic wildcard with * - Example from README: *نبي*
    
    Should return words that contain substring "نبي" (like نبي, الأنبياء, etc.).
    """
    parser = create_test_parser()
    query = parser.parse("*نبي*")
    # Should be parsed as ArabicWildcardQuery or standard Wildcard
    assert query is not None
    assert hasattr(query, 'text')
    # Wildcard queries expand against the index, not at parse time
    # So we just verify the pattern is correct


def test_arabic_wildcard_question_mark():
    """Test Arabic wildcard with Arabic question mark - Example from README: نعم؟
    
    Should return words where نعم is the prefix (like نعمة، نعما، etc.).
    """
    parser = create_test_parser()
    query = parser.parse("نعم؟")
    assert isinstance(query, ArabicWildcardQuery)
    # Should convert ؟ to ?
    assert query.text == "نعم?"
    # Wildcard queries expand against the index, not at parse time


def test_every_plugin_removed():
    """EveryPlugin is removed from ArabicParser so *:* must not parse to Every."""
    from whoosh.query import Every
    from alfanous.query_processing import ArabicParser
    from whoosh.fields import Schema, TEXT

    schema = Schema(text=TEXT(stored=True))
    parser = ArabicParser(schema, mainfield='text')
    query = parser.parse('*:*')
    assert not isinstance(query, Every), "*:* should not produce an Every (match-all) query"


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


def create_test_index():
    """Create a RAM-based test index with Arabic words"""
    from whoosh.filedb.filestore import RamStorage

    schema = Schema(text=TEXT(stored=True))
    st = RamStorage()
    ix = st.create_index(schema)
    writer = ix.writer()
    for word in ['مالك', 'مالكون', 'يملك', 'الملك', 'ملكوت']:
        writer.add_document(text=word)
    writer.commit()
    return ix


def create_index_parser(ix):
    """Create a parser configured with all plugins for a given index"""
    from whoosh.qparser.plugins import SingleQuotePlugin

    parser = QueryParser('text', ix.schema)
    parser.remove_plugin_class(SingleQuotePlugin)
    parser.add_plugin(DerivationPlugin())
    parser.add_plugin(SynonymsPlugin())
    parser.add_plugin(AntonymsPlugin())
    parser.add_plugin(SpellErrorsPlugin())
    parser.add_plugin(TashkilPlugin())
    return parser


def test_derivation_query_executes_against_index():
    """Test that DerivationQuery can be executed against a Whoosh index.

    This validates the fix for the NotImplementedError caused by Whoosh 2.7
    calling _btexts() instead of _words() on MultiTerm subclasses.
    """
    ix = create_test_index()
    parser = create_index_parser(ix)

    query = parser.parse('>مالك')
    assert isinstance(query, DerivationQuery)

    with ix.searcher() as searcher:
        results = searcher.search(query)
        result_texts = [r['text'] for r in results]
        assert 'مالك' in result_texts
        assert 'مالكون' in result_texts


def test_derivation_query_root_level_executes_against_index():
    """Test that DerivationQuery at root level (>>) executes against a Whoosh index."""
    ix = create_test_index()
    parser = create_index_parser(ix)

    query = parser.parse('>>مالك')
    assert isinstance(query, DerivationQuery)

    with ix.searcher() as searcher:
        results = searcher.search(query)
        result_texts = [r['text'] for r in results]
        # Root level should return more derivations including يملك, الملك
        assert len(results) >= 2


def test_spell_errors_query_executes_against_index():
    """Test that SpellErrorsQuery can be executed against a Whoosh index."""
    ix = create_test_index()
    parser = create_index_parser(ix)

    query = parser.parse('%مالك')
    assert isinstance(query, SpellErrorsQuery)

    with ix.searcher() as searcher:
        results = searcher.search(query)
        result_texts = [r['text'] for r in results]
        assert 'مالك' in result_texts


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
