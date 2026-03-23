
"""
This is a test module for alfanous.TextProcessing

"""

import pytest

from alfanous.text_processing import (
    QArabicSymbolsFilter,
    QArabicStemFilter,
    QShingleFilter,
    QStopFilter,
    QSynonymsFilter,
    QFuzzyAnalyzer,
    QShingleAnalyzer,
    QStandardAnalyzer,
    QUthmaniAnalyzer,
    TranslationStemFilter,
    make_translation_analyzer,
)
from whoosh.analysis import Token


def _tokenize(analyzer, text):
    """Helper: run *text* through *analyzer* and return list of token texts."""
    return [t.text for t in analyzer(text, mode="index")]


def _tokenize_query(analyzer, text):
    """Helper: run *text* through *analyzer* in query mode."""
    return [t.text for t in analyzer(text, mode="query")]


def test_arabic_symbol_filter():
    ASF = QArabicSymbolsFilter()
    assert ASF.normalize_all(u"عاصِمٌ") == u"عاصم"


# ---------------------------------------------------------------------------
# QArabicStemFilter
# ---------------------------------------------------------------------------

def test_stem_filter_reduces_suffixes():
    """Morphological variants of the same word should all stem to the same root."""
    stem_filter = QArabicStemFilter()
    if stem_filter._stemmer is None:
        pytest.skip("pystemmer not installed — skipping Arabic stemming test")
    stems = set()
    for word in ["رسول", "رسولا", "رسولكم", "رسولنا", "رسوله"]:
        tok = Token()
        tok.text = word
        tok.boost = 1.0
        tok.stopped = False
        (out,) = list(stem_filter(iter([tok])))
        stems.add(out.text)
    # All رسول* forms collapse to a single stem
    assert len(stems) == 1


def test_stem_filter_graceful_without_pystemmer(monkeypatch):
    """If pystemmer is not available the filter should be a no-op."""
    import builtins
    real_import = builtins.__import__

    def mock_import(name, *args, **kwargs):
        if name == "Stemmer":
            raise ImportError("mocked")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", mock_import)
    f = QArabicStemFilter()
    assert f._stemmer is None
    tok = Token()
    tok.text = "كتاب"
    tok.boost = 1.0
    tok.stopped = False
    (out,) = list(f(iter([tok])))
    assert out.text == "كتاب"


# ---------------------------------------------------------------------------
# QStopFilter
# ---------------------------------------------------------------------------

def test_stop_filter_removes_stop_words():
    stop_filter = QStopFilter(["من", "في", "على"])
    tokens = []
    for word in ["الله", "من", "السماء", "في", "الأرض"]:
        tok = Token()
        tok.text = word
        tok.boost = 1.0
        tok.stopped = False
        tokens.append(tok)
    result = [t.text for t in stop_filter(iter(tokens))]
    assert result == ["الله", "السماء", "الأرض"]


def test_stop_filter_empty_stopwords():
    stop_filter = QStopFilter()
    tokens = []
    for word in ["من", "الله"]:
        tok = Token()
        tok.text = word
        tok.boost = 1.0
        tok.stopped = False
        tokens.append(tok)
    result = [t.text for t in stop_filter(iter(tokens))]
    assert result == ["من", "الله"]


# ---------------------------------------------------------------------------
# QSynonymsFilter
# ---------------------------------------------------------------------------

def test_synonyms_filter_expands_tokens():
    syndict = {"ملك": ["سلطان", "أمير"]}
    syn_filter = QSynonymsFilter(syndict)
    tok = Token()
    tok.text = "ملك"
    tok.boost = 1.0
    tok.stopped = False
    result = [t.text for t in syn_filter(iter([tok]))]
    assert "ملك" in result
    assert "سلطان" in result
    assert "أمير" in result


def test_synonyms_filter_no_match():
    syn_filter = QSynonymsFilter({"ملك": ["سلطان"]})
    tok = Token()
    tok.text = "كتاب"
    tok.boost = 1.0
    tok.stopped = False
    result = [t.text for t in syn_filter(iter([tok]))]
    assert result == ["كتاب"]


# ---------------------------------------------------------------------------
# QFuzzyAnalyzer (integration)
# ---------------------------------------------------------------------------

def test_fuzzy_analyzer_strips_tashkeel():
    """QFuzzyAnalyzer should produce unvocalized tokens."""
    tokens = _tokenize(QFuzzyAnalyzer, "الْكِتَابُ")
    assert all(c < "\u064b" or c > "\u065f" for t in tokens for c in t), \
        "Tashkeel marks should be stripped"


def test_fuzzy_analyzer_removes_stop_words_at_index():
    """Common stop words should be absent from index-time tokens."""
    # "من" is in stop_words.json; confirm it is dropped
    tokens_index = _tokenize(QFuzzyAnalyzer, "من الله")
    tokens_query = _tokenize_query(QFuzzyAnalyzer, "من الله")
    # Stop words removed at both index and query time
    assert "من" not in tokens_index
    assert "من" not in tokens_query


def test_fuzzy_analyzer_synonym_expansion_index_only():
    """Synonyms should be expanded at index time but NOT at query time."""
    # Load the actual synonyms dict to pick a known pair
    from alfanous import paths
    import json
    try:
        with open(paths.SYNONYMS_FILE, encoding="utf-8") as f:
            syndict = json.load(f)
    except Exception:
        return  # Skip if synonyms file unavailable

    if not syndict:
        return

    # Pick the first key that has at least one synonym
    key = next((k for k, v in syndict.items() if v and k not in v), None)
    if key is None:
        return

    idx_tokens = _tokenize(QFuzzyAnalyzer, key)
    qry_tokens = _tokenize_query(QFuzzyAnalyzer, key)
    # At index time we get at least the original (possibly as a stem)
    assert len(idx_tokens) >= len(qry_tokens), \
        "Index-time tokens should be >= query-time tokens (synonyms add extras)"


def test_standard_analyzer_preserves_word_forms():
    """QStandardAnalyzer (used by aya_ac) should NOT stem."""
    tokens = _tokenize(QStandardAnalyzer, "رسولكم رسولنا")
    # Both words should appear as-is (no stemming)
    assert "رسولكم" in tokens
    assert "رسولنا" in tokens


# ---------------------------------------------------------------------------
# QStandardAnalyzer – Uthmani text normalization (issue: fuzzy=off no results)
# ---------------------------------------------------------------------------

def test_standard_analyzer_strips_uthmani_word():
    """QStandardAnalyzer must normalize Uthmanic text to bare Arabic letters.

    Searching 'مُّخۡتَلِفٖ' (Uthmani script, contains U+06E1 ARABIC SMALL
    HIGH NOON and U+0656 ARABIC SUBSCRIPT ALEF) with fuzzy=False on the
    standard aya field must produce the same token as the indexed plain form
    'مختلف' so that the search returns results.
    """
    uthmani_word = 'مُّخۡتَلِفٖ'  # U+06E1 and U+0656 are the extra marks
    tokens = _tokenize_query(QStandardAnalyzer, uthmani_word)
    assert tokens == ['مختلف'], (
        f"Expected ['مختلف'] but got {tokens!r}; "
        "QStandardAnalyzer must strip extended diacritics and Uthmani annotation "
        "marks so that queries against the standard aya field return results"
    )


def test_standard_analyzer_strips_subscript_alef():
    """QStandardAnalyzer must strip U+0656 (ARABIC SUBSCRIPT ALEF)."""
    # U+0656 is an extended diacritic not in the classic TASHKEEL range
    word_with_subscript_alef = 'ف\u0656'
    tokens = _tokenize_query(QStandardAnalyzer, word_with_subscript_alef)
    assert tokens == ['ف'], (
        f"Expected ['ف'] but got {tokens!r}; U+0656 should be stripped"
    )


def test_standard_analyzer_strips_small_high_noon():
    """QStandardAnalyzer must strip U+06E1 (ARABIC SMALL HIGH NOON)."""
    # U+06E1 is a Quranic annotation mark (in the U+06D6-U+06ED range)
    word_with_small_high_noon = 'خ\u06E1ت'
    tokens = _tokenize_query(QStandardAnalyzer, word_with_small_high_noon)
    assert tokens == ['خت'], (
        f"Expected ['خت'] but got {tokens!r}; U+06E1 should be stripped"
    )


def test_strip_tashkeel_strips_extended_diacritics():
    """strip_tashkeel must strip extended Arabic diacritics U+0653–U+0659."""
    from alfanous.Support.pyarabic.strip_functions import strip_tashkeel

    for cp in (0x0653, 0x0654, 0x0655, 0x0656, 0x0657, 0x0658, 0x0659):
        char = chr(cp)
        word = 'ك' + char + 'ت'
        result = strip_tashkeel(word)
        assert char not in result, (
            f"U+{cp:04X} was not stripped by strip_tashkeel; "
            "extended Arabic diacritics must be removed when tashkeel is stripped"
        )


# ---------------------------------------------------------------------------
# TranslationStemFilter
# ---------------------------------------------------------------------------

def test_translation_stem_filter_english():
    """English TranslationStemFilter should stem English words."""
    stem_filter = TranslationStemFilter('en')
    assert stem_filter._available, "pystemmer must be installed for English stemming"
    tokens = []
    for word in ['running', 'runs']:
        tok = Token()
        tok.text = word
        tok.boost = 1.0
        tok.stopped = False
        tokens.append(tok)
    stems = set(t.text for t in stem_filter(iter(tokens)))
    # Both 'running' and 'runs' should reduce to the same stem
    assert len(stems) == 1, f"Expected one stem for 'running'/'runs', got {stems}"


def test_translation_stem_filter_french():
    """French TranslationStemFilter should stem French words to the same root."""
    stem_filter = TranslationStemFilter('fr')
    assert stem_filter._available, "pystemmer must be installed for French stemming"
    tokens = []
    for word in ['aimer', 'aimez', 'aimait', 'aimera']:
        tok = Token()
        tok.text = word
        tok.boost = 1.0
        tok.stopped = False
        tokens.append(tok)
    stems = set(t.text for t in stem_filter(iter(tokens)))
    # All forms of 'aimer' should reduce to the same stem
    assert len(stems) == 1, f"Expected one stem for French aimer variants, got {stems}"


def test_translation_stem_filter_unsupported_language():
    """TranslationStemFilter for an unsupported language should be a no-op."""
    stem_filter = TranslationStemFilter('ber')  # Berber is not in Snowball
    assert not stem_filter._available
    tok = Token()
    tok.text = 'hello'
    tok.boost = 1.0
    tok.stopped = False
    (out,) = list(stem_filter(iter([tok])))
    assert out.text == 'hello'


def test_translation_stem_filter_unknown_language():
    """TranslationStemFilter with an entirely unknown language code is a no-op."""
    stem_filter = TranslationStemFilter('zz')
    assert not stem_filter._available
    tok = Token()
    tok.text = 'word'
    tok.boost = 1.0
    tok.stopped = False
    (out,) = list(stem_filter(iter([tok])))
    assert out.text == 'word'


def test_translation_stem_filter_pickle():
    """TranslationStemFilter must survive pickle/unpickle with correct stems."""
    import pickle
    stem_filter = TranslationStemFilter('en')
    restored = pickle.loads(pickle.dumps(stem_filter))
    assert restored._available == stem_filter._available
    tok = Token()
    tok.text = 'running'
    tok.boost = 1.0
    tok.stopped = False
    (out,) = list(restored(iter([tok])))
    assert out.text  # non-empty stemmed form
    # Inflected form must produce the same stem as the base form after unpickling.
    tok2 = Token(); tok2.text = 'fires'; tok2.boost = 1.0; tok2.stopped = False
    tok3 = Token(); tok3.text = 'fire';  tok3.boost = 1.0; tok3.stopped = False
    (stem_fires,) = list(restored(iter([tok2])))
    (stem_fire,)  = list(restored(iter([tok3])))
    assert stem_fires.text == stem_fire.text, (
        f"After unpickling, 'fires' and 'fire' must produce the same stem "
        f"(got {stem_fires.text!r} vs {stem_fire.text!r})"
    )


def test_translation_stem_filter_whoosh_fallback():
    """Whoosh's Snowball is the primary backend for English; stems must match."""
    stem_filter = TranslationStemFilter('en')
    assert stem_filter._available, "Whoosh's Snowball should be available for English"
    # The stem function module should come from whoosh (not pystemmer).
    assert 'whoosh' in getattr(stem_filter._stem_fn, '__module__', ''), (
        f"English should use Whoosh's Snowball as primary; got {stem_filter._stem_fn}"
    )
    # 'fires' and 'fire' must both produce the same stem.
    def stem(word):
        t = Token(); t.text = word; t.boost = 1.0; t.stopped = False
        return list(stem_filter(iter([t])))[0].text
    assert stem('fires') == stem('fire') == 'fire', (
        f"Whoosh primary: fires->{stem('fires')!r}, fire->{stem('fire')!r}"
    )


def test_translation_stem_filter_pystemmer_fallback():
    """pystemmer is used as fallback for languages Whoosh does not cover (e.g. Turkish)."""
    # Turkish is in _LANG_TO_SNOWBALL but not supported by Whoosh's lang module.
    stem_filter = TranslationStemFilter('tr')
    if not stem_filter._available:
        import pytest
        pytest.skip("Neither Whoosh nor pystemmer supports Turkish in this environment")
    # Just verify it produces a non-empty stem without error.
    def stem(word):
        t = Token(); t.text = word; t.boost = 1.0; t.stopped = False
        return list(stem_filter(iter([t])))[0].text
    result = stem('yaziyor')
    assert result, "pystemmer fallback should produce a non-empty stem for Turkish"


# ---------------------------------------------------------------------------
# make_translation_analyzer
# ---------------------------------------------------------------------------

def test_make_translation_analyzer_english():
    """make_translation_analyzer('en') should lowercase and stem English words."""
    analyzer = make_translation_analyzer('en')
    # 'running' and 'runs' should produce the same stem
    tokens_run = [t.text for t in analyzer('running', mode='index')]
    tokens_runs = [t.text for t in analyzer('runs', mode='index')]
    assert tokens_run and tokens_runs, "Analyzer should produce tokens"
    assert all(t == t.lower() for t in tokens_run + tokens_runs), "Tokens should be lowercase"
    assert tokens_run == tokens_runs, "Both 'running' and 'runs' should produce the same stem"


def test_make_translation_analyzer_unsupported_falls_back():
    """make_translation_analyzer for an unsupported language should still tokenize/lowercase."""
    analyzer = make_translation_analyzer('ber')  # Berber — no Snowball
    tokens = [t.text for t in analyzer('Hello World', mode='index')]
    assert 'hello' in tokens
    assert 'world' in tokens


def test_make_translation_analyzer_named_instances():
    """Named TranslationAnalyzer_{lang} instances should be accessible from text_processing."""
    from alfanous import text_processing
    from alfanous.text_processing import _TRANSLATION_LANGS
    for lang in _TRANSLATION_LANGS:
        attr = f'TranslationAnalyzer_{lang}'
        assert hasattr(text_processing, attr), f"text_processing.{attr} not found"
        analyzer = getattr(text_processing, attr)
        tokens = [t.text for t in analyzer('Test word', mode='index')]
        assert tokens, f"Analyzer {attr} produced no tokens"


def test_make_translation_analyzer_arabic():
    """make_translation_analyzer('ar') should lowercase and stem Arabic text."""
    analyzer = make_translation_analyzer('ar')
    tokens = [t.text for t in analyzer('الكتاب', mode='index')]
    assert tokens, "Arabic analyzer should produce tokens"


# ---------------------------------------------------------------------------
# normalize_uthmani_symbols – full U+06D6–U+06ED range
# ---------------------------------------------------------------------------

def test_normalize_uthmani_symbols_strips_full_range():
    """normalize_uthmani_symbols must strip every char in U+06D6–U+06ED.

    All code points in that block are Quranic annotation marks (small high
    letters, stops, verse markers).  None of them should survive normalisation.
    """
    from alfanous.Support.pyarabic.normalizers import normalize_uthmani_symbols

    for cp in range(0x06D6, 0x06EE):  # inclusive of 0x06ED
        char = chr(cp)
        word_with_mark = 'قول' + char + 'هم'
        result = normalize_uthmani_symbols(word_with_mark)
        assert chr(cp) not in result, (
            f"U+{cp:04X} ({char!r}) was not stripped by normalize_uthmani_symbols"
        )


def test_normalize_uthmani_symbols_preserves_arabic_letters():
    """normalize_uthmani_symbols must not alter normal Arabic letters."""
    from alfanous.Support.pyarabic.normalizers import normalize_uthmani_symbols

    text = 'قولهم'
    assert normalize_uthmani_symbols(text) == text


def test_normalize_uthmani_symbols_replaces_mini_alef_and_wasla():
    """MINI_ALEF and ALEF_WASLA should be replaced with plain ALEF."""
    from alfanous.Support.pyarabic.normalizers import normalize_uthmani_symbols

    # MINI_ALEF (U+0670) → ALEF
    assert normalize_uthmani_symbols('\u0670') == '\u0627'
    # ALEF_WASLA (U+0671) → ALEF
    assert normalize_uthmani_symbols('\u0671') == '\u0627'
    # ALEF_MADDA (U+0622) → ALEF
    assert normalize_uthmani_symbols('\u0622') == '\u0627'


# QUthmaniAnalyzer – used by the uthmani aya field

def test_quthmani_analyzer_strips_tashkeel():
    """QUthmaniAnalyzer (used by the uthmani field) must strip diacritics (tashkeel)."""
    # بِسْمِ  with tashkeel should normalize to  بسم
    tokens = _tokenize(QUthmaniAnalyzer, 'بِسْمِ')
    assert tokens == ['بسم'], f"Expected ['بسم'], got {tokens}"


def test_quthmani_analyzer_strips_uthmani_symbols():
    """QUthmaniAnalyzer must strip Uthmanic annotation marks (U+06D6–U+06ED)."""
    # Insert a small high seen (U+06DB) into a word
    tokens = _tokenize(QUthmaniAnalyzer, 'قُلْ\u06DBهُوَ')
    assert '\u06db' not in tokens[0], f"Uthmani symbol U+06DB survived: {tokens}"


def test_quthmani_analyzer_strips_tashkeel_and_uthmani_together():
    """QUthmaniAnalyzer must strip both tashkeel and uthmani symbols together."""
    # Word with both diacritics and a small high alef (U+06D8)
    tokens = _tokenize(QUthmaniAnalyzer, 'ٱلرَّحْمَ\u06D8نِ')
    for tok in tokens:
        # No diacritics (U+064B–U+0652)
        for cp in range(0x064B, 0x0653):
            assert chr(cp) not in tok, f"Diacritic U+{cp:04X} survived in {tok!r}"
        # No uthmani annotation marks (U+06D6–U+06ED)
        for cp in range(0x06D6, 0x06EE):
            assert chr(cp) not in tok, f"Uthmani symbol U+{cp:04X} survived in {tok!r}"


def test_uthmani_field_uses_normalizing_analyzer():
    """The uthmani aya field in fields.json must use QUthmaniAnalyzer (not QUthmaniDiacAnalyzer)."""
    import json
    import os
    store_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), '..', '..', 'store', 'fields.json'
    )
    with open(store_path, encoding='utf-8') as fh:
        fields = json.load(fh)
    uthmani_aya = next(
        (f for f in fields if f.get('id') == 6 and f.get('table_name') == 'aya'),
        None,
    )
    assert uthmani_aya is not None, "Field id=6 (uthmani, table aya) not found in fields.json"
    assert uthmani_aya['analyzer'] == 'QUthmaniAnalyzer', (
        f"Expected QUthmaniAnalyzer but got {uthmani_aya['analyzer']!r}; "
        "the uthmani field should normalize by removing both tashkeel and uthmani symbols"
    )


# ---------------------------------------------------------------------------
# _NORMALIZE_WORD_QUERY – word search pre-normalization (issue: ٱلۡهَدۡيِۖ)
# ---------------------------------------------------------------------------

def test_normalize_word_query_strips_uthmani_issue_word():
    """_NORMALIZE_WORD_QUERY must reduce ٱلۡهَدۡيِۖ to الهدي.

    This is the concrete Uthmani word from the bug report.  The query word
    contains ALEF_WASLA (U+0671), Uthmani sukun (U+06E1), standard tashkeel
    (FATHA U+064E, KASRA U+0650) and a Uthmanic stop mark (U+06D6).  After
    pre-normalization all those marks must be gone so that KEYWORD fields
    like *word_standard* (which stores the plain Arabic form) also match.
    """
    from alfanous.outputs import _NORMALIZE_WORD_QUERY

    uthmani_word = 'ٱلۡهَدۡيِۖ'
    result = _NORMALIZE_WORD_QUERY(uthmani_word)
    assert result == 'الهدي', (
        f"Expected 'الهدي' but got {result!r}; _NORMALIZE_WORD_QUERY must strip "
        "Uthmani annotation marks and standard tashkeel from the query so that "
        "word_standard KEYWORD field matches Uthmanic input"
    )


def test_normalize_word_query_preserves_field_syntax():
    """_NORMALIZE_WORD_QUERY must not corrupt Whoosh field-qualifier syntax.

    A field-qualified query like 'root:رحم' must have its ASCII field name
    and colon left intact while any Uthmani/tashkeel in the value part is
    stripped.
    """
    from alfanous.outputs import _NORMALIZE_WORD_QUERY

    query = 'root:رحم'
    result = _NORMALIZE_WORD_QUERY(query)
    assert result == 'root:رحم', (
        f"Expected 'root:رحم' but got {result!r}; ASCII field names and colons "
        "must not be affected by Uthmani pre-normalization"
    )


def test_normalize_word_query_idempotent_on_plain_arabic():
    """_NORMALIZE_WORD_QUERY must leave already-normalized Arabic unchanged."""
    from alfanous.outputs import _NORMALIZE_WORD_QUERY

    plain = 'الهدي'
    assert _NORMALIZE_WORD_QUERY(plain) == plain, (
        "_NORMALIZE_WORD_QUERY must be idempotent: plain Arabic without "
        "diacritics or Uthmani marks must not be changed"
    )


def test_asf_normalize_strips_uthmani_issue_word():
    """_ASF_NORMALIZE in query_plugins must reduce ٱلۡهَدۡيِۖ to الهدي.

    DerivationQuery and _lookup_key_values use _ASF_NORMALIZE to build the
    candidate set for the two-pass derivation scan.  With uthmani_symbols=True
    the fully-normalized form الهدي is included as a candidate so that
    word_standard/normalized stored fields (which hold the un-vocalized
    standard form) are also matched in Pass 1 of the scan.
    """
    from alfanous.query_plugins import _ASF_NORMALIZE

    uthmani_word = 'ٱلۡهَدۡيِۖ'
    result = _ASF_NORMALIZE.normalize_all(uthmani_word)
    assert result == 'الهدي', (
        f"Expected 'الهدي' but got {result!r}; _ASF_NORMALIZE must normalize "
        "Uthmani diacritics so derivation lookups work with Uthmanic input"
    )



# ---------------------------------------------------------------------------
# QShingleFilter – adjacency tests
# ---------------------------------------------------------------------------

def test_shingle_filter_basic_bigram_and_trigram():
    """QShingleFilter produces bigrams and trigrams from a normal 3-word phrase."""
    shingles = _tokenize(QShingleAnalyzer, "الله سميع عليم")
    assert "الله سميع" in shingles
    assert "سميع عليم" in shingles
    assert "الله سميع عليم" in shingles


def test_shingle_filter_single_char_breaks_adjacency():
    """A single-character token must clear the shingle window.

    Uthmani pause marks such as ص, ق, ن appear as standalone single-letter
    'words' in the aya text.  They must not bridge two real words into a
    shingle; otherwise the autocomplete index fills up with nonsense entries
    like 'سميع ص بصير'.
    """
    for noise in ["ص", "ق", "ن", "م"]:
        shingles = _tokenize(QShingleAnalyzer, f"سميع {noise} بصير")
        assert shingles == [], f"noise='{noise}': expected [], got {shingles!r}"


def test_shingle_filter_truly_adjacent_words_still_form_shingles():
    """Words that are genuinely adjacent (no noise in between) must still combine."""
    shingles = _tokenize(QShingleAnalyzer, "سميع بصير")
    assert "سميع بصير" in shingles


def test_shingle_filter_single_char_at_start_does_not_pollute():
    """A single-char word at the start of a phrase must not contaminate subsequent shingles."""
    # ن + two real words: only the two real words should form a bigram.
    # Note: `word in s.split()` is an exact-word check (list membership), not substring.
    shingles = _tokenize(QShingleAnalyzer, "ن سميع بصير")
    assert "سميع بصير" in shingles
    shingle_words = {w for s in shingles for w in s.split()}
    assert "ن" not in shingle_words, f"Single-char 'ن' leaked into shingles: {shingles!r}"


def test_shingle_filter_single_char_at_end_does_not_pollute():
    """A single-char word at the end of a phrase must not contaminate preceding shingles."""
    shingles = _tokenize(QShingleAnalyzer, "سميع بصير ص")
    assert "سميع بصير" in shingles
    shingle_words = {w for s in shingles for w in s.split()}
    assert "ص" not in shingle_words, f"Single-char 'ص' leaked into shingles: {shingles!r}"


def _make_token_stream(specs, positions=True):
    """Yield synthetic Whoosh tokens with explicit (text, pos) pairs.

    :param specs: iterable of ``(text, pos)`` tuples.
    :param positions: whether to enable position tracking on each token.
    """
    for text, pos in specs:
        t = Token(positions=positions)
        t.text = text
        t.stopped = False
        if positions:
            t.pos = pos
        yield t


def test_shingle_filter_position_gap_breaks_adjacency():
    """A position gap (pos increment > 1) must clear the shingle window.

    Whoosh's built-in ShingleFilter does NOT check position gaps; our
    QShingleFilter must do so explicitly using token.pos when positions are
    tracked (token.positions is True).
    """
    sf = QShingleFilter(2, 3)
    # pos 0 then pos 2: gap of 2 — words are not truly adjacent
    tokens = list(sf(_make_token_stream([("سميع", 0), ("بصير", 2)])))
    assert tokens == [], (
        f"Expected no shingles across a position gap, got {[t.text for t in tokens]!r}"
    )


def test_shingle_filter_position_gap_mid_stream():
    """A position gap in the middle of a stream resets the window.

    Tokens before the gap must not combine with tokens after it.
    """
    sf = QShingleFilter(2, 3)
    # الله(0) سميع(1) [gap] بصير(3) عليم(4)
    # Adjacent pairs: الله+سميع, بصير+عليم.
    # The gap between سميع(1) and بصير(3) must prevent "سميع بصير" and any
    # trigram that bridges positions 1 and 3.
    tokens = list(sf(_make_token_stream([
        ("الله", 0), ("سميع", 1), ("بصير", 3), ("عليم", 4)
    ])))
    texts = [t.text for t in tokens]
    assert "الله سميع" in texts,      f"Expected 'الله سميع' in {texts!r}"
    assert "بصير عليم" in texts,      f"Expected 'بصير عليم' in {texts!r}"
    # These shingles must NOT appear because they bridge the gap
    assert "سميع بصير" not in texts,  f"'سميع بصير' must not span the gap: {texts!r}"
    assert not any("سميع" in t and "بصير" in t for t in texts), (
        f"No shingle should bridge the gap: {texts!r}"
    )


def test_shingle_filter_no_positions_falls_back_to_text_checks():
    """When positions are not tracked, window resets still use stopped/single-char logic."""
    sf = QShingleFilter(2, 3)
    # Build tokens without position tracking; simulate a stopped token in between.
    def _stream():
        for text in ["سميع", "بصير"]:
            t = Token(positions=False)
            t.text = text
            t.stopped = False
            yield t
        # Stopped token (no pos tracking)
        s = Token(positions=False)
        s.text = "في"
        s.stopped = True
        yield s
        for text in ["عليم"]:
            t = Token(positions=False)
            t.text = text
            t.stopped = False
            yield t

    tokens = list(sf(_stream()))
    texts = [t.text for t in tokens]
    assert "سميع بصير" in texts,   f"Expected 'سميع بصير' in {texts!r}"
    # "بصير عليم" must NOT form because the stopped token reset the window
    assert "بصير عليم" not in texts, f"'بصير عليم' must not span stopped token: {texts!r}"


# ---------------------------------------------------------------------------
# QShingleFilter – query-mode unigram fallback ("words alone")
# ---------------------------------------------------------------------------

def test_shingle_filter_single_word_query_mode_yields_unigram():
    """A single Arabic word in query mode must be yielded as a unigram.

    When QShingleAnalyzer is used in query mode and only one real word is
    present (no shingle can form), the word itself must be emitted so that
    the Whoosh query is not silently discarded.
    """
    assert _tokenize_query(QShingleAnalyzer, "الحمد") == ["الحمد"]
    assert _tokenize_query(QShingleAnalyzer, "رسول") == ["رسول"]


def test_shingle_filter_single_word_index_mode_yields_nothing():
    """A single Arabic word in index mode must NOT produce any token.

    The aya_shingles field stores only multi-word phrases; the aya field
    already handles individual words.
    """
    assert _tokenize(QShingleAnalyzer, "الحمد") == []
    assert _tokenize(QShingleAnalyzer, "رسول") == []


def test_shingle_filter_two_words_query_mode_yields_shingle_not_unigrams():
    """Two adjacent words in query mode yield the bigram, not bare unigrams."""
    result = _tokenize_query(QShingleAnalyzer, "الحمد لله")
    assert result == ["الحمد لله"], f"Expected bigram only, got {result!r}"


def test_shingle_filter_noise_only_query_mode_yields_nothing():
    """A single-character noise token alone yields nothing even in query mode."""
    assert _tokenize_query(QShingleAnalyzer, "ص") == []
    assert _tokenize_query(QShingleAnalyzer, "ق") == []
