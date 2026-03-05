
import re

from whoosh.analysis import RegexTokenizer, Filter, LowercaseFilter  # StandardAnalyzer,
from alfanous.Support.pyarabic.main import strip_tashkeel, strip_tatweel, strip_shadda, normalize_spellerrors, \
    normalize_hamza, normalize_lamalef, normalize_uthmani_symbols  # , HARAKAT_pat,

from alfanous.constants import INVERTEDSHAPING


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


def get_arabic_stemmer():
    """Return a PyStemmer Arabic stemmer instance, or None if not available.

    Uses the Snowball Arabic stemming algorithm via the PyStemmer package.
    Install with: pip install PyStemmer
    """
    try:
        import Stemmer
        return Stemmer.Stemmer('arabic')
    except ImportError:
        return None


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
TranslationHighLightAnalyzer = RegexTokenizer() | LowercaseFilter()
