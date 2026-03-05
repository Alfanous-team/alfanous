
import copy
import json
import re

from whoosh.analysis import RegexTokenizer, Filter, LowercaseFilter, MultiFilter  # StandardAnalyzer,
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


def Gword_tamdid(aya):
    """ add a tamdid to lafdh aljalala to eliminate the double vocalization """
    return aya.replace(u"لَّه", u"لَّـه").replace(u"لَّه", u"لَّـه")


class QArabicStemFilter(Filter):
    """
    Whoosh filter that applies Arabic stemming using PyStemmer (Snowball).

    Requires the ``pystemmer`` package (``pip install pystemmer``).
    Falls back to a no-op if the package is not installed.
    """

    def __init__(self):
        self._available = self._make_stemmer()

    def _make_stemmer(self):
        try:
            import Stemmer
            self._stemmer = Stemmer.Stemmer('arabic')
            return True
        except ImportError:
            self._stemmer = None
            return False

    # pystemmer's Stemmer (Cython) is not picklable; only persist availability flag.
    def __getstate__(self):
        return {'_available': self._available}

    def __setstate__(self, state):
        self._available = state['_available']
        if self._available:
            self._make_stemmer()
        else:
            self._stemmer = None

    def __call__(self, tokens):
        if self._stemmer is None:
            yield from tokens
            return
        for t in tokens:
            if t.text:
                t.text = self._stemmer.stemWord(t.text)
            yield t


class QStopFilter(Filter):
    """
    Whoosh filter that removes Arabic stop words.

    Tokens whose text matches an entry in *stopwords* are discarded.
    The ``stopped`` attribute of the token is set to ``True`` before
    the token is dropped so that downstream phrase-position accounting
    remains correct.
    """

    def __init__(self, stopwords=None):
        self._stopwords = frozenset(stopwords) if stopwords else frozenset()

    def __call__(self, tokens):
        for t in tokens:
            if t.text in self._stopwords:
                t.stopped = True
            else:
                yield t


class QSynonymsFilter(Filter):
    """
    Whoosh filter that expands each token with its synonyms.

    Each input token is yielded unchanged, followed by one additional
    token per synonym (with the same position, so they are treated as
    alternatives).  Designed for **index-time** use inside a
    :class:`~whoosh.analysis.MultiFilter`.
    """

    def __init__(self, syndict=None):
        self._syndict = syndict if syndict is not None else {}

    def __call__(self, tokens):
        for t in tokens:
            yield t
            for syn in self._syndict.get(t.text, []):
                if syn != t.text:
                    u = copy.copy(t)
                    u.text = syn
                    yield u


def _load_stop_words():
    """Load stop words from resources/stop_words.json, returning an empty list on failure."""
    try:
        from alfanous import paths
        with open(paths.STOP_WORDS_FILE, encoding='utf-8') as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return []


def _load_syndict():
    """Load synonyms dictionary from resources/synonyms.json, returning an empty dict on failure."""
    try:
        from alfanous import paths
        with open(paths.SYNONYMS_FILE, encoding='utf-8') as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}


def _build_fuzzy_analyzer():
    """Build and return the QFuzzyAnalyzer pipeline."""
    stop_filter = QStopFilter(_load_stop_words())
    # Synonym expansion only at index time (MultiFilter with mode="index");
    # stemming applies at both index and query time.
    syn_filter = MultiFilter(index=QSynonymsFilter(_load_syndict()))
    stem_filter = QArabicStemFilter()
    return (
        QSpaceTokenizer()
        | QArabicSymbolsFilter(shaping=True, tashkil=True, spellerrors=True, hamza=True)
        | stop_filter
        | syn_filter
        | stem_filter
    )


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
QFuzzyAnalyzer = _build_fuzzy_analyzer()
