
"""
This is a test module for alfanous.TextProcessing

"""

from alfanous.text_processing import (
    QArabicSymbolsFilter,
    QArabicStemFilter,
    QStopFilter,
    QSynonymsFilter,
    QFuzzyAnalyzer,
    QStandardAnalyzer,
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
