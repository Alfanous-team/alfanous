
import copy
import json
import logging
import re

from whoosh.analysis import RegexTokenizer, Filter, LowercaseFilter, MultiFilter  # StandardAnalyzer,
from alfanous.Support.pyarabic.main import strip_tashkeel, strip_tatweel, normalize_spellerrors, \
    normalize_hamza, normalize_lamalef, normalize_uthmani_symbols  # , HARAKAT_pat,

from alfanous.constants import INVERTEDSHAPING

logger = logging.getLogger(__name__)


def normalize_shaping(text):
    """
    Normalize Arabic text by converting shaped forms to base forms.

    Also maps alef-madda (آ U+0622) to plain alef (ا U+0627) so that
    corpus forms like ``ملآئكة`` match the standard-text forms like
    ``ملائكة`` stored in the ``aya`` search field.

    @param text: Text to normalize
    @return: Normalized text
    """
    # Alef with madda above (آ U+0622) → plain alef (ا U+0627)
    text = text.replace('\u0622', '\u0627')
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
QStandardAnalyzer = QSpaceTokenizer() | QArabicSymbolsFilter(uthmani_symbols=True)
APermissibleAnalyzer = QSpaceTokenizer() | QArabicSymbolsFilter(shaping=True, tashkil=True, spellerrors=True,
                                                                hamza=True, uthmani_symbols=True)
QDiacAnalyzer = QSpaceTokenizer() | QArabicSymbolsFilter(tashkil=False)
QHighLightAnalyzer = QSpaceTokenizer() | QArabicSymbolsFilter(uthmani_symbols=True)
QDiacHighLightAnalyzer = QSpaceTokenizer() | QArabicSymbolsFilter(tashkil=False)
QUthmaniAnalyzer = QSpaceTokenizer() | QArabicSymbolsFilter(shaping=True, tashkil=True, spellerrors=False, hamza=False,
                                                            uthmani_symbols=True)
QUthmaniDiacAnalyzer = QSpaceTokenizer() | QArabicSymbolsFilter(tashkil=False, uthmani_symbols=True)
TranslationHighLightAnalyzer = RegexTokenizer() | LowercaseFilter()
QFuzzyAnalyzer = _build_fuzzy_analyzer()


# ---------------------------------------------------------------------------
# Language-specific translation analyzers (pystemmer / Snowball)
# ---------------------------------------------------------------------------

# Mapping from ISO 639-1 language codes to PyStemmer / Snowball algorithm names.
# Only languages that have a confirmed Snowball algorithm are listed here.
# Translation languages in this dataset that have NO Snowball support and will
# therefore use the fallback (RegexTokenizer + LowercaseFilter) analyzer:
#   am (Amharic), ber (Berber), bn (Bengali), fa (Persian), ms (Malay),
#   sw (Swahili), ur (Urdu).
_LANG_TO_SNOWBALL = {
    'ar': 'arabic',
    'da': 'danish',
    'nl': 'dutch',
    'en': 'english',
    'fi': 'finnish',
    'fr': 'french',
    'de': 'german',
    'el': 'greek',
    'hi': 'hindi',
    'hu': 'hungarian',
    'id': 'indonesian',
    'it': 'italian',
    'lt': 'lithuanian',
    'ne': 'nepali',
    'no': 'norwegian',
    'pt': 'portuguese',
    'ro': 'romanian',
    'ru': 'russian',
    'es': 'spanish',
    'sv': 'swedish',
    'ta': 'tamil',
    'tr': 'turkish',
}


class TranslationStemFilter(Filter):
    """Whoosh filter that applies language-specific Snowball stemming.

    Priority order:
    1. Whoosh's built-in pure-Python Snowball stemmer (``whoosh.lang``) —
       always available, no extra dependency, covers most translation
       languages (ar, de, en, fr, ru, …).
    2. pystemmer (C extension) — used only for languages Whoosh does not
       support (currently hi, id, tr in the dataset).
    3. No-op — when no Snowball algorithm is available for the language.

    Because both backends implement the same Snowball specification, the
    stems they produce are identical for the languages they share, so
    index-time and query-time stems are always consistent regardless of
    which backend is active.

    @param lang: ISO 639-1 language code (e.g. ``'en'``, ``'fr'``, ``'de'``).
    """

    def __init__(self, lang):
        self._lang = lang
        self._available = self._make_stemmer(lang)

    def _make_stemmer(self, lang):
        """Set up self._stem_fn and return True if a stemmer is available."""
        snowball_name = _LANG_TO_SNOWBALL.get(lang)
        if not snowball_name:
            self._stem_fn = None
            return False
        # Prefer Whoosh's pure-Python Snowball (always present, no extra dep).
        # Probe with a throwaway word to catch broken implementations such as
        # whoosh.lang.isri (Arabic) which uses invalid regex escapes in
        # Python 3.12 and would raise re.error at call time.
        try:
            from whoosh.lang import stemmer_for_language
            _fn = stemmer_for_language(snowball_name)
            _fn('test')  # validate — raises for broken stemmers
            self._stem_fn = _fn
            return True
        except Exception as e:
            logger.debug('Whoosh stemmer unavailable for %s (%s): %s', lang, snowball_name, e)
        # Fall back to pystemmer for languages Whoosh does not cover or where
        # Whoosh's implementation is broken (e.g. Arabic ISRIStemmer on Py 3.12).
        try:
            import Stemmer
            _obj = Stemmer.Stemmer(snowball_name)
            self._stem_fn = _obj.stemWord
            return True
        except (ImportError, KeyError, ValueError) as e:
            logger.debug('pystemmer unavailable for %s (%s): %s', lang, snowball_name, e)
        self._stem_fn = None
        return False

    # Stemmer callables are not safely picklable; only persist lang so
    # __setstate__ can rebuild the stemmer on load.
    def __getstate__(self):
        return {'_lang': self._lang, '_available': self._available}

    def __setstate__(self, state):
        self._lang = state['_lang']
        # Rebuild the stemmer; update _available to reflect the current
        # environment (pystemmer may have been installed/removed since the
        # schema was last saved).
        self._available = self._make_stemmer(self._lang)

    def __call__(self, tokens):
        if self._stem_fn is None:
            yield from tokens
            return
        for t in tokens:
            if t.text:
                t.text = self._stem_fn(t.text)
            yield t


def make_translation_analyzer(lang):
    """Build a language-specific translation analyzer using Snowball stemming.

    Returns a Whoosh analyzer that tokenizes with :class:`RegexTokenizer`,
    lowercases, and applies a Snowball stemmer for *lang* (if supported).
    Uses Whoosh's built-in pure-Python Snowball for most languages; falls
    back to pystemmer for languages Whoosh does not cover; falls back to
    no stemming when no Snowball implementation is available.

    @param lang: ISO 639-1 language code (e.g. ``'en'``, ``'fr'``).
    @return: Whoosh analyzer pipeline.
    """
    stem_filter = TranslationStemFilter(lang)
    base = RegexTokenizer() | LowercaseFilter()
    if stem_filter._available:
        return base | stem_filter
    return base


# Named language-specific translation analyzer instances.
# These names are referenced by the 'analyzer' key in fields.json so that
# Transformer.build_schema() can retrieve them via getattr(text_processing, name).
# Active languages (zip files present in store/Translations/) + future targets.
_TRANSLATION_LANGS = [
    'ar', 'en', 'fr', 'id', 'ms', 'tr',   # active — zip files present in store
    'es', 'ja', 'ku', 'ml', 'pt',           # planned — zip files not yet in store
]

for _tl in _TRANSLATION_LANGS:
    globals()[f'TranslationAnalyzer_{_tl}'] = make_translation_analyzer(_tl)
