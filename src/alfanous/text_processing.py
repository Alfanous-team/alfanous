
import re

from whoosh.analysis import RegexTokenizer, LowercaseFilter, Filter  # StandardAnalyzer,
from alfanous.Support.pyarabic.main import strip_tashkeel, strip_tatweel, strip_shadda, normalize_spellerrors, \
    normalize_hamza, normalize_lamalef, normalize_uthmani_symbols  # , HARAKAT_pat,

from alfanous.constants import INVERTEDSHAPING

try:
    import Stemmer as _Stemmer
    _PYSTEMMER_AVAILABLE = True
except ImportError:
    _PYSTEMMER_AVAILABLE = False

# Mapping from ISO 639-1 language codes to Snowball stemmer algorithm names
# (only languages that have a supported Snowball stemmer are listed here)
LANG_TO_STEMMER = {
    'ar': 'arabic',
    'de': 'german',
    'en': 'english',
    'fr': 'french',
    'hi': 'hindi',
    'id': 'indonesian',
    'ru': 'russian',
    'tr': 'turkish',
}


def normalize_shaping(text):
    """
    Normalize Arabic text by converting shaped forms to base forms.
    
    @param text: Text to normalize
    @return: Normalized text
    """
    output = ""
    for char in text:
        if char in INVERTEDSHAPING:
            output += INVERTEDSHAPING[char]
        else:
            output += char
    return output


class QSpaceTokenizer(RegexTokenizer):
    """
    Custom tokenizer for Quranic text that splits on whitespace.
    """
    def __init__(self, expression=r"[^ \t\r\n]+"):
        super(QSpaceTokenizer, self).__init__(expression=expression)




class QArabicSymbolsFilter(Filter):
    """
    Whoosh filter for normalizing Arabic text symbols.
    
    Handles Arabic text normalization including:
    - Shaping (lamalef, tatweel)
    - Tashkeel (vocalization marks)
    - Spelling errors
    - Hamza normalization
    - Uthmani symbols
    """

    def __init__(self, shaping=True, tashkil=True, spellerrors=False, hamza=False, shadda=False, uthmani_symbols=False):
        self._shaping = shaping
        self._tashkil = tashkil
        self._spellerrors = spellerrors
        self._hamza = hamza
        self._uthmani_symbols = uthmani_symbols

    def normalize_all(self, text):
        if self._shaping:
            text = normalize_lamalef(text)
            text = normalize_shaping(text)
            text = strip_tatweel(text)

        if self._tashkil:
            text = strip_tashkeel(text)

        if self._spellerrors:
            text = normalize_spellerrors(text)

        if self._hamza:
            text = normalize_hamza(text)

        if self._uthmani_symbols:
            text = normalize_uthmani_symbols(text)

        return text

    def __call__(self, tokens):
        for t in tokens:
            t.text = self.normalize_all(t.text)
            yield t


def Gword_tamdid(aya):
    """ add a tamdid to lafdh aljalala to eliminate the double vocalization """
    return aya.replace(u"لَّه", u"لَّـه").replace(u"لَّه", u"لَّـه")


# analyzers
QStandardAnalyzer = QSpaceTokenizer() | QArabicSymbolsFilter()
APermissibleAnalyzer = QSpaceTokenizer() | QArabicSymbolsFilter(shaping=True, tashkil=True, spellerrors=True,
                                                                hamza=True)
QDiacAnalyzer = QSpaceTokenizer() | QArabicSymbolsFilter(tashkil=False)
QHighLightAnalyzer = QSpaceTokenizer() | QArabicSymbolsFilter()
QDiacHighLightAnalyzer = QSpaceTokenizer() | QArabicSymbolsFilter(tashkil=False)
QUthmaniAnalyzer = QSpaceTokenizer() | QArabicSymbolsFilter(shaping=True, tashkil=True, spellerrors=False, hamza=False,
                                                            uthmani_symbols=True)
QUthmaniDiacAnalyzer = QSpaceTokenizer() | QArabicSymbolsFilter(tashkil=False, uthmani_symbols=True)


class PyStemmerFilter(Filter):
    """
    Whoosh filter that applies Snowball stemming via PyStemmer.

    Requires the ``PyStemmer`` package to be installed.
    Only valid for language codes present in :data:`LANG_TO_STEMMER`.
    """

    def __init__(self, lang_code):
        if not _PYSTEMMER_AVAILABLE:
            raise ImportError(
                "PyStemmer is required for language-specific stemming. "
                "Install it with: pip install PyStemmer"
            )
        if lang_code not in LANG_TO_STEMMER:
            raise ValueError(
                f"No Snowball stemmer available for language code '{lang_code}'. "
                f"Supported codes: {list(LANG_TO_STEMMER)}"
            )
        self._stemmer = _Stemmer.Stemmer(LANG_TO_STEMMER[lang_code])

    def __call__(self, tokens):
        for t in tokens:
            t.text = self._stemmer.stemWord(t.text)
            yield t


def get_translation_analyzer(lang_code):
    """
    Return a Whoosh analyzer suitable for the given ISO 639-1 language code.

    For languages with a supported Snowball stemmer (see :data:`LANG_TO_STEMMER`),
    the analyzer chains ``RegexTokenizer | LowercaseFilter | PyStemmerFilter``.
    For all other languages a plain ``RegexTokenizer | LowercaseFilter`` analyzer
    is returned so that at least basic tokenisation and case-folding are applied.

    @param lang_code: ISO 639-1 language code (e.g. ``'en'``, ``'fr'``, ``'ar'``).
    @return: A Whoosh analyzer.
    """
    base = RegexTokenizer() | LowercaseFilter()
    if _PYSTEMMER_AVAILABLE and lang_code in LANG_TO_STEMMER:
        return base | PyStemmerFilter(lang_code)
    return base


# All unique language codes present in configs/translations.json
_TRANSLATION_LANG_CODES = [
    'am', 'ar', 'ber', 'bn', 'de', 'en', 'fa', 'fr', 'hi', 'id', 'ms', 'ru', 'sw', 'tr', 'ur',
]

# Pre-built analyzers keyed by language code for every translation language
TRANSLATION_ANALYZERS = {
    lang: get_translation_analyzer(lang)
    for lang in _TRANSLATION_LANG_CODES
}
