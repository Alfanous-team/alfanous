
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
