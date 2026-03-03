
"""
This is a test module for alfanous.TextProcessing

"""

from alfanous.text_processing import QArabicSymbolsFilter

def test_arabic_symbol_filter():
    ASF = QArabicSymbolsFilter()
    assert ASF.normalize_all( u"عاصِمٌ" ) == u"عاصم"


# ---------------------------------------------------------------------------
# Tests for PyStemmerFilter, get_translation_analyzer, TRANSLATION_ANALYZERS
# ---------------------------------------------------------------------------

import pytest
from whoosh.analysis import Token


def _tokenize(analyzer, text):
    """Helper: run *text* through *analyzer* and return list of stemmed terms."""
    return [t.text for t in analyzer(text)]


def test_get_translation_analyzer_returns_analyzer_for_supported_language():
    """get_translation_analyzer returns a callable (Whoosh analyzer) for every code."""
    from alfanous.text_processing import get_translation_analyzer, LANG_TO_STEMMER

    for lang_code in LANG_TO_STEMMER:
        analyzer = get_translation_analyzer(lang_code)
        assert callable(analyzer), f"Expected callable for lang '{lang_code}'"


def test_get_translation_analyzer_fallback_for_unsupported_language():
    """get_translation_analyzer returns a plain lowercasing analyzer for unsupported langs."""
    from alfanous.text_processing import get_translation_analyzer

    analyzer = get_translation_analyzer("xx")  # not a real language code
    tokens = _tokenize(analyzer, "Hello World")
    assert tokens == ["hello", "world"]


def test_english_stemming():
    """English analyzer should stem 'running' → 'run'."""
    from alfanous.text_processing import TRANSLATION_ANALYZERS

    analyzer = TRANSLATION_ANALYZERS["en"]
    tokens = _tokenize(analyzer, "running")
    assert tokens == ["run"]


def test_french_stemming():
    """French analyzer should stem 'mangeant' → its French stem."""
    from alfanous.text_processing import TRANSLATION_ANALYZERS

    analyzer = TRANSLATION_ANALYZERS["fr"]
    tokens = _tokenize(analyzer, "mangeant")
    # The French Snowball stemmer reduces 'mangeant' to 'mang'
    assert tokens == ["mang"]


def test_german_stemming():
    """German analyzer should stem 'laufenden' correctly."""
    from alfanous.text_processing import TRANSLATION_ANALYZERS

    analyzer = TRANSLATION_ANALYZERS["de"]
    tokens = _tokenize(analyzer, "laufenden")
    assert len(tokens) == 1  # stemmed to some root form


def test_translation_analyzers_covers_all_lang_codes():
    """TRANSLATION_ANALYZERS has an entry for every language in the translation list."""
    from alfanous.text_processing import TRANSLATION_ANALYZERS, _TRANSLATION_LANG_CODES

    for lang_code in _TRANSLATION_LANG_CODES:
        assert lang_code in TRANSLATION_ANALYZERS, (
            f"Missing analyzer for lang code '{lang_code}'"
        )


def test_pystemmer_filter_raises_for_unsupported_lang():
    """PyStemmerFilter raises ValueError for a language code with no Snowball stemmer."""
    from alfanous.text_processing import PyStemmerFilter

    with pytest.raises(ValueError):
        PyStemmerFilter("xx")


def test_pystemmer_filter_stems_tokens():
    """PyStemmerFilter stems token text correctly for English."""
    from alfanous.text_processing import PyStemmerFilter

    filt = PyStemmerFilter("en")
    tok = Token()
    tok.text = "fishing"
    result = list(filt(iter([tok])))
    assert result[0].text == "fish"
