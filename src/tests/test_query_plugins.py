"""
Tests for Whoosh 2.7 plugin-based query parser implementation
"""
import pytest
from unittest.mock import patch
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

# ---------------------------------------------------------------------------
# Mock data for _collect_derivations_two_pass and _query_word_index.
# _collect_derivations_two_pass is used by DerivationQuery._get_derivations.
# _query_word_index is used by TupleQuery._get_words_by_properties.
# ---------------------------------------------------------------------------

# Minimal word-index data for مالك (used by derivation tests)
_MALIK_LEMMA = "مالك"
_MALIK_ROOT  = "ملك"
_MALIK_LEMMA_WORDS = ["مالك", "مالكون"]
_MALIK_ROOT_WORDS  = [
    "مالك", "مالكون", "يملك", "الملك", "ملكوت", "ملك", "ملكتم",
    "تملك", "أملك", "ملكت", "يملكون", "ملكناهم", "تملكون",
    "ملكه", "ملكهم", "ملكتني", "ملكتهم", "يملكه",
    "ملوك", "مملكة", "تملكه", "يملكوه", "ملككم",
]  # 23 unique items

# Minimal word-index data for TupleQuery tests
_QAWL_NOUNS = [
    "قول", "قولا", "قولكم", "قوله", "الأقاويل", "أقوالهم",
    "قولهم", "قولك", "قولي", "قولنا", "أقوال",
]  # 11 items
_MALIK_VERBS = [
    "يملك", "ملكتم", "تملك", "أملك", "ملكت", "يملكون",
    "ملكناهم", "تملكون",
]  # 8 items


def _make_derivation_mock(lemma_words, root_words, fallback_word=""):
    """Return a side_effect for patching _collect_derivations_two_pass.

    The function signature is ``(candidates, index_key)`` and it returns the
    list of derivation word forms directly.
    """
    def _mock(candidates, index_key):
        # Verify that candidates is non-empty — a regression here would mean
        # _get_derivations built an empty candidate set, skipping the lookup.
        assert candidates, "_collect_derivations_two_pass called with empty candidates"
        if index_key == 'lemma':
            return list(lemma_words)
        elif index_key == 'root':
            return list(root_words)
        return [fallback_word] if fallback_word else []
    return _mock


def _make_word_index_mock(word, lemma, root, lemma_words, root_words):
    """Return a side_effect function for patching _query_word_index.

    Used by TupleQuery tests; DerivationQuery tests use
    _make_derivation_mock instead.
    """
    def _mock(filter_dict, field="word", limit=5000):
        if filter_dict.get("normalized") == word or filter_dict.get("word") == word:
            if field == "lemma":
                return [lemma]
            if field == "root":
                return [root]
        if filter_dict.get("lemma") == lemma and field == "normalized":
            return list(lemma_words)
        if filter_dict.get("root") == root and field == "normalized":
            return list(root_words)
        return []
    return _mock


def _make_tuple_mock(root_words_map):
    """Return a side_effect function for TupleQuery tests.

    TupleQuery._get_words_by_properties maps the user-facing ``type`` property
    to the ``type`` index field (which stores English category values like
    "Nouns" / "Verbs") via _ARABIC_TO_TYPE.  The mock therefore reads the
    ``type`` key from filter_dict.
    """
    def _mock(filter_dict, field="word_standard", limit=5000):
        root = filter_dict.get("root", "")
        type_ = filter_dict.get("type", "")  # English value: "Nouns", "Verbs", …
        key = (root, type_)
        return list(root_words_map.get(key, []))
    return _mock


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
    """Test derivation plugin with single > (>word) — lemma-level derivations."""
    _mock = _make_derivation_mock(_MALIK_LEMMA_WORDS, _MALIK_ROOT_WORDS, "مالك")
    with patch("alfanous.query_plugins._collect_derivations_two_pass", side_effect=_mock):
        parser = create_test_parser()
        query = parser.parse(">مالك")
    assert isinstance(query, DerivationQuery)
    assert query.level == 1
    assert query.text == "مالك"
    assert sorted(query.words) == sorted(_MALIK_LEMMA_WORDS)
    assert len(query.words) == 2


def test_derivation_plugin_double():
    """Test derivation plugin with double >> (>>word) — root-level derivations."""
    _mock = _make_derivation_mock(_MALIK_LEMMA_WORDS, _MALIK_ROOT_WORDS, "مالك")
    with patch("alfanous.query_plugins._collect_derivations_two_pass", side_effect=_mock):
        parser = create_test_parser()
        query = parser.parse(">>مالك")
    assert isinstance(query, DerivationQuery)
    assert query.level == 2
    assert query.text == "مالك"
    assert len(query.words) == 23
    assert "مالك" in query.words
    assert "ملكوت" in query.words
    assert "يملك" in query.words
    assert "الملك" in query.words
    query_lemma_words = _MALIK_LEMMA_WORDS
    assert len(query.words) > len(query_lemma_words)


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
    """Test tuple plugin — root قول, type اسم (noun): 11 results."""
    _mock = _make_tuple_mock({("قول", "Nouns"): _QAWL_NOUNS})
    with patch("alfanous.query_plugins._query_word_index", side_effect=_mock):
        parser = create_test_parser()
        query = parser.parse("{قول،اسم}")
    assert isinstance(query, TupleQuery)
    assert query.props.get("root") == "قول"
    assert query.props.get("type") == "اسم"
    assert len(query.words) == 11
    assert "قول" in query.words
    assert "قولا" in query.words
    assert "قولكم" in query.words
    assert "قوله" in query.words
    assert "الأقاويل" in query.words


def test_tuple_plugin_root_and_type():
    """Test tuple plugin — root ملك, type فعل (verb): 8 results."""
    _mock = _make_tuple_mock({("ملك", "Verbs"): _MALIK_VERBS})
    with patch("alfanous.query_plugins._query_word_index", side_effect=_mock):
        parser = create_test_parser()
        query = parser.parse("{ملك،فعل}")
    assert isinstance(query, TupleQuery)
    assert query.props.get("root") == "ملك"
    assert query.props.get("type") == "فعل"
    assert len(query.words) == 8
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


def test_arabic_wildcard_lowercase_on_construction():
    """ArabicWildcardQuery must lowercase the pattern text at construction time.

    Translation fields (text_en, text_fr, etc.) use LowercaseFilter so their
    index terms are stored lowercase ('god', 'pray', ...).  Without lowercasing
    the query pattern, 'God*' would produce the regex 'God.*' which is
    case-sensitive and never matches the indexed 'god*' terms.
    Arabic text is unaffected by .lower() (Arabic has no case concept), and
    wildcard characters * and ? are ASCII punctuation also unaffected.
    """
    tests = [
        # (input_text, expected_text_after_init)
        ("God*",   "god*"),
        ("GOD*",   "god*"),
        ("Pray?",  "pray?"),
        ("*Test*", "*test*"),
        ("G?d",    "g?d"),
        # Arabic should be unchanged by .lower()
        ("نبي*",   "نبي*"),
        ("الله*",  "الله*"),
        # Arabic question mark converted first, then lowercase (no-op on Arabic)
        ("نعم؟",   "نعم?"),
        # Pure wildcards should be unchanged
        ("*",      "*"),
        ("??",     "??"),
    ]
    for input_text, expected in tests:
        q = ArabicWildcardQuery("text_en", input_text)
        assert q.text == expected, (
            f"ArabicWildcardQuery('text_en', {input_text!r}).text should be "
            f"{expected!r} but got {q.text!r}. Wildcards must be lowercased "
            "so they match index terms processed by LowercaseFilter."
        )


def test_arabic_wildcard_case_insensitive_matches_lowercase_indexed_term():
    """God* must match the index term 'god' in a field with LowercaseFilter.

    Regression test for: LowercaseFilter — God* can't match indexed term god.

    Translation fields use LowercaseFilter so 'God' is stored as 'god'.
    Before the fix, ArabicWildcardQuery('field', 'God*') kept the pattern
    as 'God*' which compiled to regex 'God.*' — a case-sensitive pattern
    that never matched the lowercase indexed term 'god'.
    """
    import shutil
    import tempfile
    from whoosh import index as whoosh_index
    from whoosh.analysis import RegexTokenizer, LowercaseFilter
    from whoosh.fields import Schema, TEXT

    analyzer = RegexTokenizer() | LowercaseFilter()
    tmpdir = tempfile.mkdtemp()
    try:
        schema = Schema(text_en=TEXT(stored=True, analyzer=analyzer))
        ix = whoosh_index.create_in(tmpdir, schema)
        writer = ix.writer()
        writer.add_document(text_en="God is great")
        writer.add_document(text_en="praise the lord")
        writer.commit()

        with ix.searcher() as searcher:
            # All of these should match the document containing "God" (indexed as "god")
            for pattern in ("God*", "GOD*", "GoD*", "g*", "go*", "god*"):
                q = ArabicWildcardQuery("text_en", pattern)
                results = searcher.search(q)
                assert len(results) >= 1, (
                    f"Pattern {pattern!r} should match doc with 'God' (indexed as 'god') "
                    f"but got {len(results)} results. "
                    "ArabicWildcardQuery must lowercase the pattern at construction time."
                )
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def test_arabic_wildcard_multifield_asterisk():
    """Regression: pray* via MultifieldParser must not produce a None-fieldname query.

    MultifieldParser initialises the parser with fieldname=None and uses
    MultifieldPlugin to copy each unfielded node and call set_fieldname() on it.
    The ArabicWildcardNode.query() method must read self.fieldname (set by
    MultifieldPlugin) and fall back to parser.fieldname — not bypass self.fieldname.
    Before the fix, parser.fieldname was used directly, which is None for a
    MultifieldParser, causing KeyError/'No field named None' at search time.
    """
    from whoosh.qparser import MultifieldParser
    from whoosh.qparser.plugins import WildcardPlugin, EveryPlugin

    schema = Schema(text_en=TEXT(stored=True), text_fr=TEXT(stored=True))
    p = MultifieldParser(['text_en', 'text_fr'], schema)
    p.remove_plugin_class(WildcardPlugin)
    p.remove_plugin_class(EveryPlugin)
    p.add_plugin(ArabicWildcardPlugin())

    # parse() must not raise; the resulting query must have valid (non-None) fieldnames
    q = p.parse('pray*')
    assert q is not None
    # For a multi-field wildcard the result is an Or of per-field queries
    for subq in q:
        assert subq.fieldname is not None, (
            f"Query {subq!r} has fieldname=None; ArabicWildcardNode must "
            "use self.fieldname (set by MultifieldPlugin) rather than parser.fieldname"
        )


def test_arabic_wildcard_multifield_question_mark():
    """Regression: produc? via MultifieldParser must not produce a None-fieldname query.

    Same root cause as test_arabic_wildcard_multifield_asterisk but exercises the
    single-character wildcard (?) path, which maps to ArabicWildcardQuery.
    Before the fix this caused KeyError/'No field named None' when the query was
    executed against a Whoosh index.
    """
    from whoosh.qparser import MultifieldParser
    from whoosh.qparser.plugins import WildcardPlugin, EveryPlugin

    schema = Schema(text_en=TEXT(stored=True), text_fr=TEXT(stored=True))
    p = MultifieldParser(['text_en', 'text_fr'], schema)
    p.remove_plugin_class(WildcardPlugin)
    p.remove_plugin_class(EveryPlugin)
    p.add_plugin(ArabicWildcardPlugin())

    q = p.parse('produc?')
    assert q is not None
    for subq in q:
        assert subq.fieldname is not None, (
            f"Query {subq!r} has fieldname=None; ArabicWildcardNode must "
            "use self.fieldname (set by MultifieldPlugin) rather than parser.fieldname"
        )
        assert isinstance(subq, ArabicWildcardQuery), (
            f"Expected ArabicWildcardQuery, got {type(subq).__name__}"
        )


def test_every_plugin_removed():
    """EveryPlugin is removed from ArabicParser so *:* must not parse to Every."""
    from whoosh.query import Every
    from alfanous.query_processing import ArabicParser
    from whoosh.fields import Schema, TEXT

    schema = Schema(text=TEXT(stored=True))
    parser = ArabicParser(schema, mainfield='text')
    query = parser.parse('*:*')
    assert not isinstance(query, Every), "*:* should not produce an Every (match-all) query"


def test_arabic_parser_double_question_is_arabic_wildcard():
    """ArabicParser: ?? must produce ArabicWildcardQuery, not a plain Whoosh Wildcard.

    The built-in WildcardPlugin has tagger priority 0 and therefore runs before
    ArabicWildcardPlugin (priority 90) in the tagging phase.  Without explicitly
    removing WildcardPlugin from ArabicParser, standalone ?? and ??? queries are
    consumed by WildcardPlugin and produce plain Wildcard objects that have no
    MAX_EXPAND cap — allowing them to iterate over the full index lexicon and
    exceed the timelimit.
    """
    from alfanous.query_processing import ArabicParser
    from whoosh.fields import Schema, TEXT

    schema = Schema(text=TEXT(stored=True))
    parser = ArabicParser(schema, mainfield='text')

    query = parser.parse('??')
    assert isinstance(query, ArabicWildcardQuery), (
        f"?? should produce ArabicWildcardQuery but got {type(query).__name__}. "
        "WildcardPlugin must be removed from ArabicParser so ArabicWildcardPlugin "
        "handles standalone wildcard tokens."
    )
    assert query.text == '??', f"Expected text '??' but got {query.text!r}"


def test_arabic_parser_triple_question_is_arabic_wildcard():
    """ArabicParser: ??? must produce ArabicWildcardQuery (same root cause as ??)."""
    from alfanous.query_processing import ArabicParser
    from whoosh.fields import Schema, TEXT

    schema = Schema(text=TEXT(stored=True))
    parser = ArabicParser(schema, mainfield='text')

    query = parser.parse('???')
    assert isinstance(query, ArabicWildcardQuery), (
        f"??? should produce ArabicWildcardQuery but got {type(query).__name__}."
    )
    assert query.text == '???', f"Expected text '???' but got {query.text!r}"


def test_arabic_parser_wildcard_plugin_not_present():
    """ArabicParser must not contain WildcardPlugin after initialisation.

    WildcardPlugin's tagger runs before ArabicWildcardPlugin (lower priority
    number = earlier execution) so it must be removed to let ArabicWildcardPlugin
    handle all wildcard tokens with the MAX_EXPAND safety cap.
    """
    from whoosh.qparser.plugins import WildcardPlugin
    from alfanous.query_processing import ArabicParser
    from whoosh.fields import Schema, TEXT

    schema = Schema(text=TEXT(stored=True))
    parser = ArabicParser(schema, mainfield='text')

    plugin_types = [type(p) for p in parser.plugins]
    assert WildcardPlugin not in plugin_types, (
        "WildcardPlugin must be removed from ArabicParser so that "
        "ArabicWildcardPlugin is the sole handler for ?, ??, ???, * patterns."
    )


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
    """Test that DerivationQuery executes against a Whoosh RAM index."""
    _mock = _make_derivation_mock(_MALIK_LEMMA_WORDS, _MALIK_ROOT_WORDS, "مالك")
    ix = create_test_index()
    parser = create_index_parser(ix)

    with patch("alfanous.query_plugins._collect_derivations_two_pass", side_effect=_mock):
        query = parser.parse('>مالك')

    assert isinstance(query, DerivationQuery)

    with ix.searcher() as searcher:
        results = searcher.search(query)
        result_texts = [r['text'] for r in results]
        assert 'مالك' in result_texts
        assert 'مالكون' in result_texts


def test_derivation_query_root_level_executes_against_index():
    """Test that root-level DerivationQuery (>>) executes against a Whoosh RAM index."""
    _mock = _make_derivation_mock(_MALIK_LEMMA_WORDS, _MALIK_ROOT_WORDS, "مالك")
    ix = create_test_index()
    parser = create_index_parser(ix)

    with patch("alfanous.query_plugins._collect_derivations_two_pass", side_effect=_mock):
        query = parser.parse('>>مالك')

    assert isinstance(query, DerivationQuery)

    with ix.searcher() as searcher:
        results = searcher.search(query)
        assert len(results) >= 2


def test_derivation_query_vocalized_words_match_analyzed_index():
    """DerivationQuery must find results even when all derivation words are vocalized.

    Regression test for: >>عذاب gives no results in fuzzy=false mode.

    The aya field uses QStandardAnalyzer which strips diacritics at index time,
    so the stored terms are unvocalized (e.g. "عذاب").  DerivationQuery.words
    may contain vocalized forms (e.g. "عَذَابٌ") from the word index's word
    field.  Without the fix, _btexts() encoded these with to_bytes() (raw
    UTF-8, no analysis) producing bytes that never matched the index terms.

    The fix makes _btexts() run each word through field.process_text() so
    the same normalization (diacritics-stripping, shaping) that ran at
    index time is also applied at query time.
    """
    from whoosh.filedb.filestore import RamStorage
    from alfanous.text_processing import QStandardAnalyzer

    # Create an index whose field uses QStandardAnalyzer – exactly like the
    # real 'aya' field – so that indexed terms are unvocalized Arabic.
    schema = Schema(aya=TEXT(analyzer=QStandardAnalyzer, stored=True))
    st = RamStorage()
    ix = st.create_index(schema)
    writer = ix.writer()
    writer.add_document(aya='وَلَهُمْ عَذَابٌ عَظِيمٌ')
    writer.add_document(aya='يُعَذِّبُ مَنْ يَشَاءُ')
    writer.commit()

    # Simulate the worst case: _collect_derivations_two_pass returns ONLY
    # vocalized forms (as if the 'normalized' and 'word_standard' stored
    # fields were absent and only the 'word' vocalized field was present).
    # Before the fix _btexts() would find no index terms and return 0 results.
    _vocalized_only = lambda _candidates, _index_key: (
        'عَذَابٌ', 'عَذَابَ', 'عَذَابِ', 'يُعَذِّبُ'
    )

    from whoosh.qparser.plugins import SingleQuotePlugin
    parser = QueryParser('aya', ix.schema)
    parser.remove_plugin_class(SingleQuotePlugin)
    parser.add_plugin(DerivationPlugin())

    with patch("alfanous.query_plugins._collect_derivations_two_pass",
               side_effect=_vocalized_only):
        query = parser.parse('>>عذاب')

    assert isinstance(query, DerivationQuery)
    assert query.level == 2

    with ix.searcher() as searcher:
        results = searcher.search(query)
        assert len(results) >= 1, (
            ">>عذاب should return results even when derivation words are vocalized; "
            "_btexts() must normalize through the field analyzer"
        )


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


def test_derivation_plugin_inside_parentheses():
    """Regression: >قال inside parentheses must not consume the closing paren.

    outputs.py wraps Arabic queries as ``kind:aya AND (>قال)``.  Before the
    fix the DerivationPlugin regex ``>+\\S+`` matched ``>قال)`` — including
    the closing parenthesis — so the derivation text became ``قال)`` and the
    lookup returned no results.
    """
    _mock = _make_derivation_mock(_MALIK_LEMMA_WORDS, _MALIK_ROOT_WORDS, "مالك")
    with patch("alfanous.query_plugins._collect_derivations_two_pass", side_effect=_mock):
        parser = create_test_parser()
        query = parser.parse("foo AND (>مالك)")
    # The DerivationQuery must have text == 'مالك', NOT 'مالك)'
    from whoosh.query import And
    subqueries = query.subqueries if hasattr(query, 'subqueries') else [query]
    deriv_queries = [sq for sq in subqueries if isinstance(sq, DerivationQuery)]
    assert len(deriv_queries) == 1, f"Expected 1 DerivationQuery, got {[type(sq).__name__ for sq in subqueries]}"
    assert deriv_queries[0].text == "مالك", f"DerivationQuery.text should be 'مالك', got {deriv_queries[0].text!r}"


def test_wildcard_plugin_inside_parentheses():
    """Regression: *نبي* inside parentheses must not consume the closing paren.

    outputs.py wraps Arabic queries as ``kind:aya AND (*نبي*)``.  Before the
    fix the ArabicWildcardPlugin regex ``\\S*[*?؟]\\S*`` matched ``*نبي*)`` —
    including the closing parenthesis — so the wildcard pattern became
    ``*نبي*)`` and matched nothing in the index.
    """
    from whoosh.query import Wildcard as _Wildcard
    parser = create_test_parser()
    query = parser.parse("foo AND (*نبي*)")
    subqueries = query.subqueries if hasattr(query, 'subqueries') else [query]
    wildcard_queries = [sq for sq in subqueries if isinstance(sq, _Wildcard)]
    assert len(wildcard_queries) == 1, f"Expected 1 wildcard query, got {[type(sq).__name__ for sq in subqueries]}"
    assert wildcard_queries[0].text == "*نبي*", f"Wildcard text should be '*نبي*', got {wildcard_queries[0].text!r}"


def test_arabic_wildcard_normalize_star_stays_as_arabic_wildcard():
    """ArabicWildcardQuery.normalize() must NOT convert bare '*' to Every.

    Whoosh's Wildcard.normalize() converts ``*`` → ``Every(field)`` which is
    completely unbounded and bypasses the MAX_EXPAND cap.  The override must
    return ``self`` so the cap remains active for translation/word search.
    """
    from whoosh.query import Every
    wq = ArabicWildcardQuery("text_en", "*")
    result = wq.normalize()
    assert not isinstance(result, Every), (
        "ArabicWildcardQuery.normalize() must not convert '*' to Every; "
        "Every has no expansion limit and would match all documents."
    )
    assert isinstance(result, ArabicWildcardQuery), (
        f"normalize('*') should return ArabicWildcardQuery, got {type(result).__name__}"
    )


def test_arabic_wildcard_normalize_prefix_stays_as_arabic_wildcard():
    """ArabicWildcardQuery.normalize() must NOT convert 'word*' to Prefix.

    Whoosh's Wildcard.normalize() converts ``word*`` → ``Prefix(field, 'word')``.
    Prefix._btexts() is unbounded (calls ixreader.expand_prefix()) so it
    bypasses the MAX_EXPAND cap.  The override must return ``self``.
    """
    from whoosh.query.terms import Prefix
    wq = ArabicWildcardQuery("text_en", "word*")
    result = wq.normalize()
    assert not isinstance(result, Prefix), (
        "ArabicWildcardQuery.normalize() must not convert 'word*' to Prefix; "
        "Prefix._btexts() is unbounded and bypasses MAX_EXPAND."
    )
    assert isinstance(result, ArabicWildcardQuery), (
        f"normalize('word*') should return ArabicWildcardQuery, got {type(result).__name__}"
    )


def test_arabic_wildcard_normalize_no_wildcard_becomes_term():
    """ArabicWildcardQuery.normalize() converts plain-text to Term (no wildcards)."""
    from whoosh.query import Term
    wq = ArabicWildcardQuery("text_en", "hello")
    result = wq.normalize()
    assert isinstance(result, Term), (
        f"normalize('hello') should return Term, got {type(result).__name__}"
    )
    assert result.text == "hello"


def test_arabic_wildcard_matcher_star_does_not_use_every():
    """ArabicWildcardQuery.matcher() for bare '*' must use _btexts(), not Every.

    Whoosh's Wildcard.matcher() short-circuits ``text == '*'`` and creates an
    Every matcher (all documents, unbounded).  The override must call
    MultiTerm.matcher() instead so the MAX_EXPAND cap in _btexts() is applied.
    """
    import shutil
    import tempfile
    from whoosh import index as whoosh_index
    from whoosh.fields import Schema, TEXT

    tmpdir = tempfile.mkdtemp()
    try:
        schema = Schema(text_en=TEXT(stored=True))
        ix = whoosh_index.create_in(tmpdir, schema)
        writer = ix.writer()
        for word in ("alpha", "beta", "gamma"):
            writer.add_document(text_en=word)
        writer.commit()

        with ix.searcher() as searcher:
            wq = ArabicWildcardQuery("text_en", "*")
            # matcher() must succeed (no exception from Every shortcut)
            m = wq.matcher(searcher)
            # It should match some documents (from _btexts capped at MAX_EXPAND)
            count = 0
            while m.is_active():
                count += 1
                m.next()
            assert count <= ArabicWildcardQuery.MAX_EXPAND, (
                f"matcher('*') matched {count} docs but MAX_EXPAND={ArabicWildcardQuery.MAX_EXPAND}"
            )
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def test_arabic_wildcard_multifield_star_no_every():
    """MultifieldParser with ArabicWildcardPlugin: '*' must not produce Every.

    Before the normalize() fix, parsing '*' with a MultifieldParser set up for
    translation/word search produced Every('field') queries — completely
    unbounded.  After the fix each sub-query must be ArabicWildcardQuery.
    """
    from whoosh.qparser import MultifieldParser
    from whoosh.qparser.plugins import WildcardPlugin, EveryPlugin
    from whoosh.query import Every
    from whoosh.fields import Schema, TEXT

    schema = Schema(text_en=TEXT(stored=True), text_fr=TEXT(stored=True))
    p = MultifieldParser(["text_en", "text_fr"], schema)
    p.remove_plugin_class(WildcardPlugin)
    p.remove_plugin_class(EveryPlugin)
    p.add_plugin(ArabicWildcardPlugin())

    result = p.parse("*")
    assert result is not None
    for subq in result:
        assert not isinstance(subq, Every), (
            f"Sub-query {subq!r} is Every — ArabicWildcardQuery.normalize() "
            "must prevent Every conversion so MAX_EXPAND cap applies."
        )
        assert isinstance(subq, ArabicWildcardQuery), (
            f"Expected ArabicWildcardQuery, got {type(subq).__name__}"
        )


def test_arabic_wildcard_multifield_prefix_no_unbounded_prefix():
    """MultifieldParser with ArabicWildcardPlugin: 'word*' must not produce Prefix.

    Before the normalize() fix, 'word*' was converted to Prefix('field', 'word')
    by Wildcard.normalize() — which is unbounded.  After the fix it must stay
    as ArabicWildcardQuery.
    """
    from whoosh.qparser import MultifieldParser
    from whoosh.qparser.plugins import WildcardPlugin, EveryPlugin
    from whoosh.query.terms import Prefix
    from whoosh.fields import Schema, TEXT

    schema = Schema(text_en=TEXT(stored=True), text_fr=TEXT(stored=True))
    p = MultifieldParser(["text_en", "text_fr"], schema)
    p.remove_plugin_class(WildcardPlugin)
    p.remove_plugin_class(EveryPlugin)
    p.add_plugin(ArabicWildcardPlugin())

    result = p.parse("word*")
    assert result is not None
    for subq in result:
        assert not isinstance(subq, Prefix), (
            f"Sub-query {subq!r} is Prefix — Prefix._btexts() is unbounded and "
            "bypasses MAX_EXPAND.  ArabicWildcardQuery.normalize() must prevent "
            "the Wildcard→Prefix conversion."
        )
        assert isinstance(subq, ArabicWildcardQuery), (
            f"Expected ArabicWildcardQuery, got {type(subq).__name__}"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


# ---------------------------------------------------------------------------
# _collect_derivations_two_pass_cached must not return vocalized word forms
# ---------------------------------------------------------------------------

def test_collect_derivations_two_pass_cached_returns_only_unvocalized():
    """Pass 2 of _collect_derivations_two_pass_cached must not include the
    vocalized 'word' field — only 'word_standard' and 'normalized' are collected.

    Regression/requirement test for: remove vocalized keywords from
    words.individual in morphological derivations level search.
    """
    from unittest.mock import MagicMock, patch as _patch
    from alfanous.query_plugins import _collect_derivations_two_pass_cached

    # Build fake word-child documents: one with vocalized 'word', unvocalized
    # 'normalized' and 'word_standard', keyed by lemma "ملك".
    _DOCS = [
        {
            "kind": "word",
            "lemma": "ملك",
            "root": "ملك",
            "word": "مَلِكٌ",       # vocalized — must NOT appear in results
            "normalized": "ملك",   # unvocalized — must appear
            "word_standard": "ملك",
        },
        {
            "kind": "word",
            "lemma": "ملك",
            "root": "ملك",
            "word": "مَالِكٌ",      # vocalized — must NOT appear in results
            "normalized": "مالك",  # unvocalized — must appear
            "word_standard": "مالك",
        },
    ]

    mock_reader = MagicMock()
    mock_reader.iter_docs.return_value = [(i, d) for i, d in enumerate(_DOCS)]

    mock_engine = MagicMock()
    mock_engine.OK = True
    mock_engine._reader.reader = mock_reader

    # Arabic diacritics range (tashkeel / harakat)
    import re as _re
    _DIACRITIC_RE = _re.compile(r'[\u064B-\u065F]')

    with _patch("alfanous.data.QSE", return_value=mock_engine):
        # Clear LRU cache so the patched engine is used
        _collect_derivations_two_pass_cached.cache_clear()
        results = list(_collect_derivations_two_pass_cached(frozenset({"ملك"}), "lemma"))

    assert results, "Expected at least one unvocalized derivation word"
    for w in results:
        assert not _DIACRITIC_RE.search(w), (
            f"_collect_derivations_two_pass_cached returned vocalized form {w!r}; "
            "only unvocalized forms (word_standard, normalized) should be collected"
        )
    # The unvocalized normalized forms must be present
    assert "ملك" in results, "Expected 'ملك' (normalized) in results"
    assert "مالك" in results, "Expected 'مالك' (normalized) in results"



def _make_word_index_mock_with_marks(word, lemma, root, lemma_words, root_words):
    """Like _make_word_index_mock but injects U+06D6–U+06ED marks into the
    returned word forms.  This simulates the state of the index *before* the
    normalize_uthmani_symbols fix, where word_standard entries could contain
    Uthmanic annotation characters."""
    # Embed a small selection of Uthmanic marks into each word form
    _MARKS = '\u06D6\u06DF\u06E8'  # SmallHighLigature, SmallHighRoundedZero, SmallHighNoon

    def _inject(words):
        return [w[0] + _MARKS + w[1:] if len(w) > 1 else w for w in words]

    def _mock(candidates, index_key):
        assert candidates, "_collect_derivations_two_pass called with empty candidates"
        if index_key == 'lemma':
            return _inject(list(lemma_words))
        elif index_key == 'root':
            return _inject(list(root_words))
        return [word]
    return _mock


_UTHMANI_MARKS_RANGE = range(0x06D6, 0x06EE)


def test_derivation_results_contain_no_uthmani_marks_lemma_level():
    """Lemma-level derivation results (>word) must not contain U+06D6–U+06ED.

    Even when the word index returns values that embed Uthmanic annotation
    marks (simulating an un-rebuilt index), _get_derivations must strip them
    before returning."""
    _mock = _make_word_index_mock_with_marks(
        "قولهم", "قول", "قول", ["قول", "قولهم", "قولكم"], ["قول", "قولهم", "قولكم"]
    )
    with patch("alfanous.query_plugins._collect_derivations_two_pass", side_effect=_mock):
        result = DerivationQuery._get_derivations("قولهم", leveldist=1)

    for w in result:
        for cp in _UTHMANI_MARKS_RANGE:
            assert chr(cp) not in w, (
                f"Derivation result {w!r} contains Uthmanic mark U+{cp:04X}"
            )


def test_derivation_results_contain_no_uthmani_marks_root_level():
    """Root-level derivation results (>>word) must not contain U+06D6–U+06ED."""
    _mock = _make_word_index_mock_with_marks(
        "قولهم", "قول", "قول",
        ["قول", "قولهم"],
        ["قول", "قولهم", "قولكم", "قولنا", "يقول", "يقولون"],
    )
    with patch("alfanous.query_plugins._collect_derivations_two_pass", side_effect=_mock):
        result = DerivationQuery._get_derivations("قولهم", leveldist=2)

    for w in result:
        for cp in _UTHMANI_MARKS_RANGE:
            assert chr(cp) not in w, (
                f"Derivation result {w!r} contains Uthmanic mark U+{cp:04X}"
            )


# ---------------------------------------------------------------------------
# Unit tests for _strip_phrase_queries (no index required)
# ---------------------------------------------------------------------------

class TestStripPhraseQueries:
    """Verify that _strip_phrase_queries converts Phrase nodes without an index."""

    def _make_schema(self):
        from whoosh.fields import Schema, TEXT
        return Schema(f=TEXT(phrase=False))

    def test_plain_term_unchanged(self):
        """A plain Term is returned as-is."""
        from whoosh import query as wq
        from alfanous.searching import _strip_phrase_queries
        q = wq.Term("f", "hello")
        result = _strip_phrase_queries(q)
        assert result == q

    def test_single_phrase_becomes_and_of_terms(self):
        """A Phrase with two words is replaced by And([Term, Term])."""
        from whoosh import query as wq
        from alfanous.searching import _strip_phrase_queries
        q = wq.Phrase("f", ["hello", "world"])
        result = _strip_phrase_queries(q)
        assert isinstance(result, wq.And), f"Expected And, got {type(result)}"
        assert set(result.subqueries) == {wq.Term("f", "hello"), wq.Term("f", "world")}

    def test_single_word_phrase_becomes_term(self):
        """A Phrase with a single word is collapsed to a plain Term."""
        from whoosh import query as wq
        from alfanous.searching import _strip_phrase_queries
        q = wq.Phrase("f", ["hello"])
        result = _strip_phrase_queries(q)
        assert isinstance(result, wq.Term)
        assert result.text == "hello"

    def test_empty_phrase_becomes_null(self):
        """A Phrase with no words is replaced by NullQuery."""
        from whoosh import query as wq
        from alfanous.searching import _strip_phrase_queries
        q = wq.Phrase("f", [])
        result = _strip_phrase_queries(q)
        assert result is wq.NullQuery

    def test_and_containing_phrase(self):
        """A Phrase nested inside an And is converted; the And wrapper is kept."""
        from whoosh import query as wq
        from alfanous.searching import _strip_phrase_queries
        phrase = wq.Phrase("f", ["رب", "العالمين"])
        q = wq.And([wq.Term("f", "foo"), phrase])
        result = _strip_phrase_queries(q)
        assert isinstance(result, wq.And)
        # The Phrase child must now be an And of Terms, not a Phrase
        sub_types = {type(s) for s in result.subqueries}
        assert wq.Phrase not in sub_types, "Phrase must not survive _strip_phrase_queries"

    def test_or_containing_phrase(self):
        """A Phrase nested inside an Or is converted; the Or wrapper is kept."""
        from whoosh import query as wq
        from alfanous.searching import _strip_phrase_queries
        phrase = wq.Phrase("f", ["رب", "العالمين"])
        q = wq.Or([wq.Term("f", "bar"), phrase])
        result = _strip_phrase_queries(q)
        assert isinstance(result, wq.Or)
        sub_types = {type(s) for s in result.subqueries}
        assert wq.Phrase not in sub_types

    def test_andnot_containing_phrase(self):
        """A Phrase inside an AndNot (BinaryQuery) is converted."""
        from whoosh import query as wq
        from alfanous.searching import _strip_phrase_queries
        phrase = wq.Phrase("f", ["رب", "العالمين"])
        q = wq.AndNot(phrase, wq.Term("f", "baz"))
        result = _strip_phrase_queries(q)
        assert isinstance(result, wq.AndNot)
        # First child was a Phrase — must be converted to And
        assert isinstance(result.subqueries[0], wq.And)
        # Second child (plain Term) must be unchanged
        assert isinstance(result.subqueries[1], wq.Term)

    def test_not_containing_phrase(self):
        """A Phrase inside a Not is converted."""
        from whoosh import query as wq
        from alfanous.searching import _strip_phrase_queries
        phrase = wq.Phrase("f", ["رب", "العالمين"])
        q = wq.Not(phrase)
        result = _strip_phrase_queries(q)
        assert isinstance(result, wq.Not)
        assert isinstance(result.query, wq.And)

    def test_non_phrase_compound_unchanged(self):
        """Compound queries without any Phrase children are returned unchanged."""
        from whoosh import query as wq
        from alfanous.searching import _strip_phrase_queries
        q = wq.And([wq.Term("f", "a"), wq.Term("f", "b")])
        result = _strip_phrase_queries(q)
        assert isinstance(result, wq.And)
        assert all(isinstance(s, wq.Term) for s in result.subqueries)
