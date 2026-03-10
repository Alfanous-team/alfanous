import heapq
import logging
import re
from collections import defaultdict

from alfanous.text_processing import QArabicSymbolsFilter
from alfanous.data import *
from alfanous.constants import QURAN_TOTAL_VERSES
from alfanous.romanization import (
    transliterate,
    arabizi_to_arabic_list,
    filter_candidates_by_wordset,
)

from whoosh import query as wquery
from whoosh.fields import TEXT as _WhooshTEXT
from whoosh.sorting import Facets
from alfanous.results_processing import QTranslationHighlight


from alfanous.text_processing import _TRANSLATION_LANGS
# All language-specific indexed translation fields (text_en, text_fr, …).
_TEXT_LANG_FIELDS = [f'text_{l}' for l in _TRANSLATION_LANGS]

# Characters passed through unchanged during Arabizi conversion inside queries.
# Whoosh search operators (AND/OR/NOT symbols, field selectors, wildcards, etc.)
# must not be transliterated to Arabic letters.
_ARABIZI_IGNORE_CHARS = "'_\"%*?#~[]{}:>+-|"

FALSE_PATTERN = '^false|no|off|0$'
# Compiled once at import time — used by IS_FLAG on every request.
_FALSE_PATTERN_RE = re.compile(FALSE_PATTERN, re.IGNORECASE)

# Compiled once at import time — used in every _search_aya / _search_translation
# call to split comma-separated Sura name strings.
_KEYWORD_SPLIT_RE = re.compile("[^,،]+")

# Pre-compiled regex for stripping non-Arabic characters from suggestion queries.
_SUGGEST_STRIP_RE = re.compile(r'[^\u0621-\u065F\u0670-\u06FF\s]')

# Pre-compiled regex for detecting whether a query contains Arabic-script
# characters.  Used in _search_aya on every request to decide between the
# arabizi/translation path and the direct Arabic path.
_ARABIC_SCRIPT_RE = re.compile(r'[\u0600-\u06FF]')

# Pre-instantiated Arabic text normalisation filters.  Only two configurations
# are ever used inside _search_aya:
#   _STRIP_VOCALIZATION  — always strips diacritics (tashkil=True)
#   _KEEP_VOCALIZATION   — identity function when vocalized=True (all flags False)
# Creating these once at module load avoids two object allocations per request.
_STRIP_VOCALIZATION = QArabicSymbolsFilter(
    shaping=False, tashkil=True, spellerrors=False, hamza=False
).normalize_all
_KEEP_VOCALIZATION = QArabicSymbolsFilter(
    shaping=False, tashkil=False, spellerrors=False, hamza=False
).normalize_all

# All word-child index fields targetable by _search_words.
# Defined at module level so the list is not rebuilt on every request.
_WORD_ALL_INDEXED_FIELDS = [
    "word", "normalized", "word_standard",
    "pos", "type",
    "root", "arabicroot",
    "lemma", "arabiclemma",
    "gender", "number", "person",
    "form", "voice", "state",
    "derivation", "aspect",
    "mood", "case",
]

# Word-child fields that support faceting (ID/KEYWORD fields, stored and indexed).
# Note: lemma is intentionally excluded here because it is a full search field
# (included in _WORD_ALL_INDEXED_FIELDS) rather than a low-cardinality facet.
_WORD_FACET_FIELDS = frozenset(["root", "type"])

# Maximum number of documents Whoosh will collect when building facets.
# Using limit=None causes Whoosh to load every matching document into memory,
# which can be 300,000+ docs for a corpus-wide facet query.  This constant is
# a safe upper bound that covers the entire Quran corpus
# (~6,236 ayas + ~77,000 words + ~100,000 translations + parent docs) while
# protecting the process from runaway memory allocation.
_MAX_FACET_DOCS = 100_000

# Sort-key functions defined once at module level so every list.sort() and
# heapq.nlargest() call in the hot path reuses the same function object
# rather than allocating a new lambda on every request.
def _WORD_ID_KEY(e):
    return e.get("word_id") or 0

def _FACET_COUNT_KEY(x):
    return len(x[1])

# Zero-coalesce helper — replaces `N = lambda X: X if X else 0` that was
# allocated on every _search_aya call and called ~6× per result (≈150 calls
# per 25-result page).
def _ZERO_IF_NONE(x):
    return x if x else 0

# Text-coalesce helper — replaces `lambda X: X if X else "-----"` that was
# allocated on every _search_aya / _search_translation / _search_words call
# for the no-highlight (H / TH) path.  Defining it once at module level avoids
# one function-object allocation per request on each of the three search methods.
def _COALESCE_TEXT(x):
    return x if x else "-----"

# Keyword-split helper — replaces the per-request lambda
# `keywords = lambda phrase: _KEYWORD_SPLIT_RE.findall(phrase)`.
# Binding the method once at module level avoids allocating a new closure
# on every _search_aya and _search_translation call.
_KEYWORD_FIND = _KEYWORD_SPLIT_RE.findall


def _build_filter_query(filter_dict):
    """Convert a filter dict to a list of Whoosh Term/Or query objects.

    Each key-value pair in *filter_dict* becomes a :class:`whoosh.query.Term`
    (scalar value) or :class:`whoosh.query.Or` of Terms (list value).
    Returns an empty list when *filter_dict* is falsy.
    """
    if not filter_dict:
        return []
    parts = []
    for field, value in filter_dict.items():
        if isinstance(value, list):
            parts.append(wquery.Or([wquery.Term(field, v) for v in value]))
        else:
            parts.append(wquery.Term(field, value))
    return parts


def _edit_distance(s, t):
    """Compute the Levenshtein edit distance between two strings."""
    m, n = len(s), len(t)
    d = list(range(n + 1))
    for i in range(1, m + 1):
        prev = d[:]
        d[0] = i
        for j in range(1, n + 1):
            d[j] = min(prev[j] + 1, d[j - 1] + 1, prev[j - 1] + (s[i - 1] != t[j - 1]))
    return d[n]


## a function to decide what is True and what is false
def IS_FLAG(flags, key):
    default = _FLAG_DEFAULTS[key]
    val = flags.get(key, default)
    if val is None or val == '':
        return default
    if not val or _FALSE_PATTERN_RE.match(str(val)):
        return False
    return True



class Raw:
    DEFAULTS = {
        "minrange": 1,
        "maxrange": 25,
        "maxkeywords": 20,  # Limit highlighted/annotated terms for performance
        "results_limit": {
            "aya": QURAN_TOTAL_VERSES,
            "translation": 1000,
            "word": 1000,
        },

        "flags": {
            "action": "search",
            "unit": "aya",
            "ident": "undefined",
            "platform": "undefined",
            "domain": "undefined",
            "query": "",
            "script": "standard",
            "vocalized": True,
            "highlight": "css",
            "view": "custom",
            "recitation": "1",
            "translation": None,
            "lang": None,
            "romanization": None,
            "prev_aya": True,
            "next_aya": True,
            "sura_info": False,
            "sura_stat_info": False,
            "word_info": False,
            "word_synonyms": False,
            "word_derivations": False,
            "word_vocalizations": False,
            "word_linguistics": False,
            "aya_position_info": False,
            "aya_theme_info": True,
            "aya_stat_info": True,
            "aya_sajda_info": True,
            "annotation_word": False,
            "annotation_aya": False,
            "sortedby": "score",
            "reverse": False,
            "offset": 1,
            "range": 10,  # used as "perpage" in paging mode
            "page": 1,  # overridden with offset
            "perpage": 10,  # overridden with range
            "fuzzy": False,
            "fuzzy_maxdist": 1,
            "timelimit": 5.0,
            "aya": True,
            "facets": None,
            "filter": None,
        }
    }

    ERRORS = {
        0: "success",
        1: "no action is chosen or action undefined",
        3: "Parsing Query failed, please reformulate  the query",
        4: "One of specified arabic_to_english_fields doesn't exist"
    }

    DOMAINS = {
        "action": ["search", "suggest", "correct_query", "show"],
        "unit": ["aya", "word", "translation"],
        "ident": ["undefined"],
        "platform": ["undefined", "wp7", "s60", "android", "ios", "linux", "window"],
        "domain": [],
        "query": [],
        "highlight": ["css", "html", "genshi", "bold", "bbcode"],
        "script": ["standard", "uthmani"],
        "vocalized": [True, False],
        "view": ["minimal", "normal", "full", "statistic", "linguistic", "recitation", "custom"],
        "recitation": [],  # range( 30 ),
        "translation": [],
        "lang": [],
        "romanization": ["none", "buckwalter", "iso", "arabtex"],  # arabizi is forbidden for show
        "prev_aya": [True, False],
        "next_aya": [True, False],
        "sura_info": [True, False],
        "sura_stat_info": [True, False],
        "word_info": [True, False],
        "word_synonyms": [True, False],
        "word_derivations": [True, False],
        "word_vocalizations": [True, False],
        "word_linguistics": [True, False],
        "aya_position_info": [True, False],
        "aya_theme_info": [True, False],
        "aya_stat_info": [True, False],
        "aya_sajda_info": [True, False],
        "annotation_word": [True, False],
        "annotation_aya": [True, False],
        "sortedby": ["score", "relevance", "mushaf", "tanzil", "ayalength"],
        "reverse": [True, False],
        "offset": [],  # range(6237)
        "range": [],  # range(DEFAULTS["maxrange"]) , # used as "perpage" in paging mode
        "page": [],  # range(6237),  # overridden with offset
        "perpage": [],  # range( DEFAULTS["maxrange"] ) , # overridden with range
        "fuzzy": [True, False],
        "fuzzy_maxdist": [],
        "timelimit": [],
        "aya": [True, False],
    }

    HELPMESSAGES = {
        "action": "action to perform",
        "unit": "search unit",
        "ident": "identifier of requester",
        "platform": "platform used by requester",
        "domain": "web domain of requester if applicable",
        "query": "query attached to action",
        "highlight": "highlight method",
        "script": "script of aya text",
        "vocalized": "enable vocalization of aya text",
        "view": "pre-defined configuration for what information to retrieve",
        "recitation": "recitation id",
        "translation": "translation id",
        "lang": "language code (e.g. 'en', 'fr', 'ar') to select translation by language at query time",
        "romanization": "type of romanization",
        "prev_aya": "enable previous aya retrieving",
        "next_aya": "enable next aya retrieving",
        "sura_info": "enable sura information retrieving (override sura_stat_info if False)",
        "sura_stat_info": "enable sura stats retrieving (has no effect if sura_info is False)",
        "word_info": "enable word information retrieving",
        "word_synonyms": "enable  retrieving of keyword synonyms",
        "word_derivations": "enable  retrieving of keyword derivations",
        "word_vocalizations": "enable  retrieving of keyword vocalizations",
        "word_linguistics": "include per-aya word children with full morphological data (sorted by position)",
        "aya_position_info": "enable aya position information retrieving",
        "aya_theme_info": "enable aya theme information retrieving",
        "aya_stat_info": "enable aya stat information retrieving",
        "aya_sajda_info": "enable aya sajda information retrieving",
        "annotation_word": "enable query terms annotations retrieving",
        "annotation_aya": "enable aya words annotations retrieving",
        "sortedby": "sorting order of results — one of 'score', 'relevance', 'mushaf', 'tanzil', or 'ayalength'. "
                    "'score' and 'relevance' rank by Whoosh BM25 relevance score (highest first by default). "
                    "'mushaf' orders by the traditional Qur'an page order (sura then verse). "
                    "'tanzil' orders by revelation chronology. "
                    "'ayalength' orders by verse length in words.",
        "reverse": "reverse the sort order (default False — inverts the default ordering for each sort type; "
                    "e.g. with 'score' returns least-relevant results first, with 'mushaf' returns the last verse first)",
        "offset": "starting offset of results",
        "range": "range of results",
        "page": "page number  [override offset]",
        "perpage": "results per page  [override range]",
        "fuzzy": "fuzzy search — searches aya_ (exact) and aya (normalised/stemmed) with Levenshtein distance matching",
        "fuzzy_maxdist": "maximum Levenshtein edit distance for fuzzy term matching (default: 1, only used when fuzzy=True)",
        "timelimit": "maximum number of seconds to spend on a search query (default: 5.0, use None or 0 to disable)",
        "aya": "enable retrieving of aya text in the case of translation search",
    }

    def __init__(self,
                 QSE_index=paths.QSE_INDEX,
                 Recitations_list_file=paths.RECITATIONS_LIST_FILE,
                 Translations_list_file=paths.TRANSLATIONS_LIST_FILE,
                 Information_file=paths.INFORMATION_FILE,
                 AI_Rules_file=paths.AI_QUERY_TRANSLATION_RULES_FILE):
        """
		initialize the search engines
		"""
        ##
        self.QSE = QSE(QSE_index)
        ##
        self._recitations = recitations(Recitations_list_file)
        _translations_names = translations(Translations_list_file)
        self._translations = {
            _id: _translations_names.get(_id, _id)
            for _id in self.QSE.list_values("trans_id")
            if _id
        }
        ##
        self._information = information(Information_file)
        self._ai_query_translation_rules = ai_query_translation_rules(AI_Rules_file)
        ##
        self._surates = {
            "Arabic": self.QSE.list_values("sura_arabic"),
            "English": self.QSE.list_values("sura_english"),
            "Romanized": self.QSE.list_values("sura")
        }
        self._chapters = self.QSE.list_stored_values("chapter")
        self._topics = self.QSE.list_stored_values("topic")
        self._subtopics = self.QSE.list_stored_values("subtopic")

        self._defaults = self.DEFAULTS
        self._flags = self.DEFAULTS["flags"].keys()
        self._fields = arabic_to_english_fields
        self._fields_reverse = {v: k for k, v in arabic_to_english_fields.items()}
        # Prefer word index for roots.
        # list_values() uses Whoosh's field_terms() which scans only the target
        # field, making it ~100x faster than list_terms() which walks all_terms().
        self._roots = sorted(filter(bool, self.QSE.list_values("root"))) if self.QSE.OK else []

        self._errors = self.ERRORS
        self._domains = self.DOMAINS
        self._helpmessages = self.HELPMESSAGES
        self._all = {
            "translations": self._translations,
            "recitations": self._recitations,
            "information": self._information,
            "surates": self._surates,
            "chapters": self._chapters,
            "topics": self._topics,
            "subtopics": self._subtopics,
            "defaults": self._defaults,
            "flags": self._flags,
            "arabic_to_english_fields": self._fields,
            "fields_reverse": self._fields_reverse,
            "errors": self._errors,
            "domains": self._domains,
            "help_messages": self._helpmessages,
            "roots": self._roots,
            "ai_query_translation_rules": self._ai_query_translation_rules
        }

        # ---------------------------------------------------------------------------
        # Pre-build parsers that are invariant for the lifetime of this Raw instance.
        # Both depend only on self.QSE._schema which is fixed after index open.
        # Caching them avoids one MultifieldParser construction per request.
        # ---------------------------------------------------------------------------
        if self.QSE.OK:
            from whoosh.qparser import MultifieldParser as _MFP, OrGroup as _OrGroup
            _schema = self.QSE._schema
            _schema_fields = set(_schema.names())

            # Translation search parser (used in _search_aya non-Arabic path and
            # _search_translation).
            _avail_trans = [f for f in _TEXT_LANG_FIELDS if f in _schema_fields]
            self._trans_parser = _MFP(_avail_trans, _schema, group=_OrGroup) if _avail_trans else None
            # Frozenset of the same fields — used for fast membership tests
            # when extracting matched terms for highlighting.
            self._trans_fields = frozenset(_avail_trans)

            # Word search parser (used in _search_words).
            _all_word_f = [f for f in _WORD_ALL_INDEXED_FIELDS if f in _schema_fields]
            _default_word_f = (
                [f for f in ["word_standard", "word", "normalized"] if f in _schema_fields]
                or _all_word_f
            )
            # Only build the parser when there is at least one usable field.
            # _search_words already checks for None and returns an empty response.
            self._word_parser = (
                _MFP(_default_word_f, schema=_schema, group=_OrGroup)
                if _default_word_f else None
            )
            # Also cache the full list for schema filtering in _search_words.
            self._all_word_fields = _all_word_f
        else:
            self._trans_parser = None
            self._trans_fields = frozenset()
            self._word_parser = None
            self._all_word_fields = []

    def close(self):
        """Close all held search engine resources.

        Releases the underlying Whoosh index searcher and reader held by
        the ``QSE`` engine.  After this call the ``Raw`` instance is no
        longer usable.

        :meth:`close` is idempotent: calling it multiple times is safe.
        Typical usage with a context manager::

            with Raw(QSE_index=…) as raw:
                result = raw.do(flags)
        """
        if hasattr(self, 'QSE'):
            self.QSE.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def do(self, flags):
        return self._do(flags)

    def _parse_timelimit(self, flags):
        """Parse and validate the timelimit flag from a flags dict.

        Returns a float (seconds) to pass to Whoosh, or None to run without a
        limit.  A value of 0 or the empty string is treated as "no limit".
        """
        raw = flags.get('timelimit', self._defaults['flags']['timelimit'])
        try:
            return float(raw) if raw not in (None, 0, '0', '') else None
        except (TypeError, ValueError):
            return self._defaults['flags']['timelimit']

    def _do(self, flags):
        action = flags.get("action") or self._defaults["flags"]["action"]
        unit = flags.get("unit") or self._defaults["flags"]["unit"]
        # init the error message with Succes
        output = self._check(0, flags)
        if action == "search":
            output.update(self._search(flags, unit))
        elif action == "suggest":
            output.update(self._suggest(flags, unit))
        elif action == "correct_query":
            output.update(self._correct_query(flags, unit))
        elif action == "show":
            output.update(self._show(flags))
        elif action == "list_values":
            output.update(self._list_values(flags))
        else:
            output.update(self._check(1, flags))

        return output

    def _check(self, error_code, flags):
        """ prepare the error messages """
        return {
            "error": {"code": error_code, "msg": self._errors[error_code] % flags}

        }

    def _show(self, flags):
        """  show metadata"""
        query = flags.get("query") or self._defaults["flags"]["query"]
        if query == "all":
            return {"show": self._all}
        elif query in self._all:
            return {"show": {query: self._all[query]}}
        elif query == "keywords":
            # Handle keywords query - get top frequent or all unique keywords
            return {"show": self._show_keywords(flags)}
        else:
            return {"show": None}

    def _show_keywords(self, flags):
        """
        Show keywords (most frequent or all unique) for a given field.
        Uses Whoosh facets for categorical fields and reader methods for text fields.
        
        Parameters via flags:
        - unit: Search unit to query from (default: 'aya')
                Valid values: 'aya', 'translation', 'word'
                Invalid values default to 'aya'
        - field: The field name to query (e.g., 'aya_', 'topic', 'chapter')
                 Auto-adjusted based on unit if using default 'aya_':
                 - 'word' unit: defaults to 'normalized' field
                 - 'translation' unit: defaults to 'text' field
        - mode: 'frequent' for top N most frequent, 'unique' for all unique values (default: 'unique')
        - limit: Number of results for 'frequent' mode (default: 20)
        
        Returns:
        - unit: The search unit used
        - field: The field queried
        - mode: The query mode used
        - keywords: List of keywords (format depends on mode)
        - count: Number of keywords returned
        - limit: (only in frequent mode) The limit applied
        - error: (if error occurred) Error message
        """
        unit = flags.get("unit", "aya")
        field = flags.get("field", "aya_")
        mode = flags.get("mode", "unique")
        
        # Select the appropriate search engine based on unit
        if unit == "word":
            search_engine = self.QSE
            if field == "aya_":  # Use default field for word children
                field = "normalized"
        elif unit == "translation":
            search_engine = self.QSE
            if field == "aya_":  # Use text_en as default indexed field for translation children
                field = "text_en"
        else:  # unit == "aya" or any other value defaults to QSE
            search_engine = self.QSE
            unit = "aya"  # Normalize unit name
        
        # Validate and convert limit parameter
        try:
            limit = int(flags.get("limit", 20))
        except (ValueError, TypeError):
            limit = 20  # Use default if invalid
        
        result = {
            "unit": unit,
            "field": field,
            "mode": mode
        }
        
        try:
            # Check if search engine is properly initialized
            if not search_engine.OK:
                result["error"] = f"Search engine for unit '{unit}' is not available"
                result["keywords"] = []
                result["count"] = 0
                return result
            
            # Determine if this is a tokenized text field or a categorical field
            # TEXT fields are tokenized and we want individual tokens
            # For KEYWORD, NUMERIC, ID fields we use facets to get unique values
            schema = search_engine._schema
            field_obj = schema[field] if field in schema.names() else None
            
            is_text_field = field_obj is not None and isinstance(field_obj, _WhooshTEXT)
            
            if is_text_field:
                # For text fields, use reader methods to get individual tokens
                if mode == "unique":
                    # Get all unique tokens/terms for the field
                    values = search_engine.list_values(field)
                    result["keywords"] = values
                    result["count"] = len(values)
                else:  # mode == "frequent"
                    # Get top N most frequent tokens
                    frequent_words = search_engine.most_frequent_words(limit, field)
                    result["keywords"] = [
                        {"word": word, "frequency": int(freq)}
                        for freq, word in frequent_words
                    ]
                    result["limit"] = limit
                    result["count"] = len(frequent_words)
            else:
                # For categorical/keyword fields, use Whoosh facets
                # This provides better performance and uses standard Whoosh functionality
                searcher = search_engine.shared_searcher()
                
                try:
                    # Create facets for the requested field
                    groupedby = Facets()
                    groupedby.add_field(field)
                    
                    # In the nested QSE index every group contains both parent aya
                    # docs and child translation docs.  Restrict the facet query to
                    # the relevant document kind so child docs don't create spurious
                    # extra groups in aya-only fields (e.g. sura_type, sura_id).
                    if unit == "translation":
                        kind_filter = wquery.Term("kind", "translation")
                    elif unit == "word":
                        kind_filter = wquery.Term("kind", "word")
                    else:
                        kind_filter = wquery.Term("kind", "aya")
                    
                    # Search matching documents.  _MAX_FACET_DOCS is a safe upper bound
                    # that covers the full Quran corpus; limit=None would load every doc
                    # into memory (OOM risk under load).
                    results = searcher.search(kind_filter, limit=_MAX_FACET_DOCS, groupedby=groupedby)
                    
                    # Get facet groups
                    field_groups = results.groups(field)
                    
                    if mode == "unique":
                        # Get all unique values for the field
                        values = list(field_groups.keys())
                        result["keywords"] = values
                        result["count"] = len(values)
                    else:  # mode == "frequent"
                        # Get top N most frequent values with document counts
                        # heapq.nlargest is O(n log k) vs O(n log n) for a full sort
                        top_items = heapq.nlargest(
                            limit, field_groups.items(), key=_FACET_COUNT_KEY
                        )
                        
                        result["keywords"] = [
                            {"word": str(value), "frequency": len(doclist)}
                            for value, doclist in top_items
                        ]
                        result["limit"] = limit
                        result["count"] = len(top_items)
                finally:
                    # Always close the searcher to prevent resource leaks
                    searcher.close()
            
        except Exception as e:
            # Handle any errors
            result["error"] = f"Error retrieving keywords for field '{field}' in unit '{unit}': {str(e)}"
            result["keywords"] = []
            result["count"] = 0
        
        return result

    def _list_values(self, flags):
        """
        List all unique indexed values for a given field.

        Parameters via flags:
        - field: The field name to list values for (required).
                 Must be an indexed field in the Whoosh schema.

        Returns a dict with key ``list_values`` containing:
        - field:  the field that was queried
        - values: sorted list of unique non-empty values found in the index
                  (empty strings and None entries that Whoosh may emit for
                  documents where the field is unset are excluded)
        - count:  number of values returned
        - error:  (only present on failure) human-readable error message
        """
        field = flags.get("field")
        if not field:
            return {"list_values": {"field": None, "values": [], "count": 0,
                                    "error": "A 'field' parameter is required"}}

        if not self.QSE.OK:
            return {"list_values": {"field": field, "values": [], "count": 0,
                                    "error": "Search engine is not available"}}

        # Filter out empty/null index terms that Whoosh may emit for un-set fields,
        # then sort so the output is deterministic for callers.
        values = sorted(filter(bool, self.QSE.list_values(field)))
        return {"list_values": {"field": field, "values": values, "count": len(values)}}

    def _suggest(self, flags, unit):
        """ return suggestions for any search unit """
        if unit == "aya":
            suggestions = self._suggest_aya(flags)
        elif unit == "translation":
            suggestions = None
        else:
            suggestions = {}

        return {"suggest": suggestions}

    def _suggest_aya(self, flags):
        """ return suggestions for aya words """
        query = flags.get("query") or self._defaults["flags"]["query"]
        # strip all non-Arabic characters (keeps Arabic letters, diacritical marks,
        # and extended Arabic characters; removes ASCII symbols, punctuation, Latin
        # words, and Arabic punctuation like ، ؛ ؟)
        query = _SUGGEST_STRIP_RE.sub(' ', query)
        query = ' '.join(w for w in query.split() if w)

        return self.QSE.suggest_all(query)

    def _correct_query(self, flags, unit):
        """ return a corrected query for any search unit """
        if unit == "aya":
            correction = self._correct_query_aya(flags)
        else:
            correction = None

        return {"correct_query": correction}

    def _correct_query_aya(self, flags):
        """ return a corrected query for aya search """
        query = flags.get("query") or self._defaults["flags"]["query"]
        return self.QSE.correct_query(query)

    def _search(self, flags, unit):
        if unit == "aya":
            search_results = self._search_aya(flags)
        elif unit == "translation":
            search_results = self._search_translation(flags)
        elif unit == "word":
            search_results = self._search_words(flags)
        else:
            search_results = {}

        return {"search": search_results}

    def _search_aya(self, flags):

        flags = {**self._defaults["flags"], **flags}
        query = flags["query"]
        sortedby = flags["sortedby"]
        reverse = IS_FLAG(flags, 'reverse')
        range = int(flags["perpage"]) if flags.get("perpage") \
            else flags["range"]
        ## offset = (page-1) * perpage   --  mode paging
        offset = ((int(flags["page"]) - 1) * range) + 1 if flags.get("page") \
            else int(flags["offset"])
        recitation = flags["recitation"]
        translation = flags["translation"]
        lang = flags.get("lang") or self._defaults["flags"]["lang"]
        romanization = flags["romanization"]
        highlight = flags["highlight"]
        script = flags["script"]
        vocalized = IS_FLAG(flags, 'vocalized')
        fuzzy = IS_FLAG(flags, 'fuzzy')
        fuzzy_maxdist = int(flags.get('fuzzy_maxdist', self._defaults['flags']['fuzzy_maxdist']))
        timelimit = self._parse_timelimit(flags)
        view = flags["view"]
        # Validate view parameter; fall back to "custom" if not recognised
        if view not in self.DOMAINS["view"]:
            view = self._defaults["flags"]["view"]

        # Parse facets parameter
        facets_param = flags.get("facets")
        facets_list = None
        if facets_param:
            if isinstance(facets_param, str):
                facets_list = [f.strip() for f in facets_param.split(",") if f.strip()]
            elif isinstance(facets_param, list):
                facets_list = facets_param
        
        # Parse filter parameter
        filter_param = flags.get("filter")
        filter_dict = None
        if filter_param:
            if isinstance(filter_param, dict):
                filter_dict = filter_param
            elif isinstance(filter_param, str):
                # Parse "field:value,field2:value2" format
                filter_dict = {}
                for item in filter_param.split(","):
                    if ":" in item:
                        field, value = item.split(":", 1)
                        field = field.strip()
                        value = value.strip()
                        # Try to convert to int if possible
                        try:
                            value = int(value)
                        except ValueError:
                            pass
                        filter_dict[field] = value

        # pre-defined views # TODO remove this feature , complexity for no real benifit
        if view == "minimal":
            # fuzzy = True
            # page = 25
            recitation = None
            prev_aya = next_aya = False
            sura_info = False
            word_info = False
            word_synonyms = False
            word_derivations = False
            word_vocalizations = False
            word_linguistics = False
            aya_position_info = aya_theme_info = aya_sajda_info = False
            aya_stat_info = False
            sura_stat_info = False
            annotation_aya = annotation_word = False
        elif view == "normal":
            prev_aya = next_aya = True
            sura_info = False
            word_info = True
            word_synonyms = False
            word_derivations = True
            word_vocalizations = True
            word_linguistics = False
            aya_position_info = aya_theme_info = aya_sajda_info = True
            aya_stat_info = False
            sura_stat_info = False
            annotation_aya = annotation_word = False
        elif view == "full":
            prev_aya = next_aya = True
            sura_info = True
            word_info = True
            word_synonyms = True
            word_derivations = True
            word_vocalizations = True
            word_linguistics = True
            aya_position_info = aya_theme_info = aya_sajda_info = True
            aya_stat_info = sura_stat_info = True
            annotation_aya = annotation_word = True
            romanization = "iso"
        elif view == "statistic":
            prev_aya = next_aya = False
            sura_info = True
            word_info = True
            word_synonyms = False
            word_derivations = True
            word_vocalizations = True
            word_linguistics = False
            aya_position_info = True
            aya_theme_info = aya_sajda_info = False
            aya_stat_info = True
            sura_stat_info = True
            annotation_aya = False
            annotation_word = False
        elif view == "linguistic":
            prev_aya = next_aya = False
            sura_info = False
            word_info = True
            word_synonyms = True
            word_derivations = True
            word_vocalizations = True
            word_linguistics = True   # include per-aya morphological word children
            aya_position_info = False
            aya_theme_info = aya_sajda_info = True
            aya_stat_info = False
            sura_stat_info = False
            annotation_aya = True
            annotation_word = True
            romanization = "buckwalter"
        elif view == "recitation":
            script = "uthmani"
            prev_aya = next_aya = True
            sura_info = True
            word_info = False
            word_synonyms = False
            word_derivations = False
            word_vocalizations = False
            word_linguistics = False
            aya_position_info = True
            aya_theme_info = False
            aya_sajda_info = True
            aya_stat_info = False
            sura_stat_info = False
            annotation_aya = False
            annotation_word = False
        else:  # if view == custom or undefined
            prev_aya = IS_FLAG(flags, 'prev_aya')
            next_aya = IS_FLAG(flags, 'next_aya')
            sura_info = IS_FLAG(flags, 'sura_info')
            sura_stat_info = IS_FLAG(flags, 'sura_stat_info')
            word_info = IS_FLAG(flags, 'word_info')
            word_synonyms = IS_FLAG(flags, 'word_synonyms')
            word_derivations = IS_FLAG(flags, 'word_derivations')
            word_vocalizations = IS_FLAG(flags, 'word_vocalizations')
            word_linguistics = IS_FLAG(flags, 'word_linguistics')

            aya_position_info = IS_FLAG(flags, 'aya_position_info')
            aya_theme_info = IS_FLAG(flags, 'aya_theme_info')
            aya_stat_info = IS_FLAG(flags, 'aya_stat_info')
            aya_sajda_info = IS_FLAG(flags, 'aya_sajda_info')
            annotation_aya = IS_FLAG(flags, 'annotation_aya')
            annotation_word = IS_FLAG(flags, 'annotation_word')

        # print query
        # preprocess query
        query = query.replace("\\", "")

        if ":" not in query and not _ARABIC_SCRIPT_RE.search(query):
            # Non-Arabic query: search translations AND try arabizi conversion
            # to also search the Arabic aya fields ("the word and arabizi(word)").
            _query_parts = []

            # 1. Translation search: NestedParent over child translation docs
            _trans_terms = []
            if self._trans_parser is not None:
                _trans_q = self._trans_parser.parse(query)
                _trans_terms = [t for f, t in _trans_q.all_terms() if f in self._trans_fields]
                _query_parts.append(wquery.NestedParent(wquery.Term("kind", "aya"), _trans_q))

            # 2. Arabizi search: convert non-Arabic words to Arabic candidates
            # and search aya text fields directly (no NestedParent needed for aya docs).
            _arabizi_candidates = arabizi_to_arabic_list(
                query.lower(), ignore=_ARABIZI_IGNORE_CHARS
            )
            _qwords = quran_unvocalized_words()
            if _qwords:
                _arabizi_candidates = filter_candidates_by_wordset(_arabizi_candidates, _qwords)
            if _arabizi_candidates:
                _arabic_terms = [wquery.Term("aya", c) for c in _arabizi_candidates]
                _arabic_q = wquery.Or(_arabic_terms) if len(_arabic_terms) > 1 else _arabic_terms[0]
                # Scope to parent aya documents so nested child docs are excluded.
                if "kind" in self.QSE._schema:
                    _arabic_q = wquery.And([wquery.Term("kind", "aya"), _arabic_q])
                _query_parts.append(_arabic_q)

            if not _query_parts:
                # No fields available and no arabizi candidates — return empty.
                _final_q = wquery.NullQuery()
            elif len(_query_parts) == 1:
                _final_q = _query_parts[0]
            else:
                _final_q = wquery.Or(_query_parts)

            # Apply filter_dict to restrict results (e.g. sura_id:2).
            _filter_parts = _build_filter_query(filter_dict)
            if _filter_parts:
                _final_q = wquery.And([_final_q] + _filter_parts)

            res, termz, searcher = self.QSE.search_with_query(
                _final_q,
                limit=self._defaults["results_limit"]["aya"],
                sortedby=sortedby,
                reverse=reverse,
                timelimit=timelimit,
            )
            terms, _all_ac_variations = [], []
        else:
            # Arabic (or field-qualified) query — search aya fields directly.
            # Restrict to parent aya documents only so that nested child
            # translation docs (which lack aya_id/sura_id) are never returned.
            aya_query = (
                f"kind:aya AND ({query})"
                if "kind" in self.QSE._schema
                else query
            )
            res, termz, searcher = self.QSE.search_all(aya_query, limit=self._defaults["results_limit"]["aya"], sortedby=sortedby, reverse=reverse, facets=facets_list, filter_dict=filter_dict, fuzzy=fuzzy, fuzzy_maxdist=fuzzy_maxdist, timelimit=timelimit)
            terms = [term[1] for term in termz[:self._defaults["maxkeywords"]]]
            # All matched aya_ac variation terms (only populated when fuzzy=True).
            # Used in the word_info loop to derive per-word variation lists.
            _all_ac_variations = [term[1] for term in termz if term[0] == "aya_ac"]
            _trans_terms = []
        try:
            # pagination
            offset = 1 if offset < 1 else offset
            range = self._defaults["minrange"] if range < self._defaults["minrange"] else range
            range = self._defaults["maxrange"] if range > self._defaults["maxrange"] else range
            interval_end = offset + range - 1
            end = interval_end if interval_end < len(res) else len(res)
            start = offset if offset <= len(res) else -1
            reslist = [] if end == 0 or start == -1 else res[start - 1:end]
            # todo pagination should be done inside search operation for better performance

            output = {}

            ## disable annotations for aya words if there is more then one result
            if annotation_aya and len(res) > 1:
                annotation_aya = False

            ## strip vocalization when vocalized = true
            V = _KEEP_VOCALIZATION if vocalized else _STRIP_VOCALIZATION
            strip_vocalization = _STRIP_VOCALIZATION
            # Pre-check highlight once — avoids re-evaluating `highlight != "none"` on every H/TH call.
            _do_highlight = highlight != "none"
            # highligh function that consider None value and non-definition
            if _do_highlight:
                H = lambda X: self.QSE.highlight(X, terms, highlight) if X else "-----"
                # translation highlight function: applies QTranslationHighlight with non-Arabic query terms
                TH = lambda X: QTranslationHighlight(X, _trans_terms, type=highlight) if X and _trans_terms else (X if X else "-----")
            else:
                H = _COALESCE_TEXT
                TH = _COALESCE_TEXT
            # Pre-check script once — avoids re-evaluating `script == "standard"` per aya in the result loop.
            _use_standard_script = script == "standard"
            ##########################################
            extend_runtime = res.runtime

            # Words & Annotations
            words_output = {"individual": {}}
            if word_info:
                # _result_docnums and _index_reader are only needed here; building them
                # unconditionally would iterate ALL results and hold a reader reference
                # on every request even when word_info is False (the default).
                _result_docnums = frozenset(hit.docnum for hit in res)

                # Acquire _wi_searcher BEFORE capturing _index_reader.
                # shared_searcher() calls _get_shared_searcher().refresh() internally;
                # if the Whoosh index has changed since the main search, the old shared
                # searcher (and the reader returned by searcher.reader()) is closed at
                # that point.  Grabbing _index_reader first would leave a stale, closed
                # reader that raises ReaderClosed on any subsequent postings() call.
                # By obtaining _wi_searcher first we ensure any pending refresh runs
                # before we ask for the reader, so get_shared_reader() always returns
                # an open reader belonging to the current shared searcher.
                _wi_searcher = (
                    self.QSE.shared_searcher()
                    if (word_vocalizations or word_derivations) and self.QSE.OK
                    else None
                )
                # get_shared_reader() resolves through _get_shared_searcher(), so it
                # returns the reader of the NOW-current (post-refresh) shared searcher.
                _index_reader = self.QSE.get_shared_reader()

                def _count_term_in_results(field, term_text):
                    """Count occurrences of a term within the search result documents."""
                    count = 0
                    try:
                        m = _index_reader.postings(field, term_text)
                        while m.is_active():
                            if m.id() in _result_docnums:
                                count += m.value_as("frequency")
                            m.next()
                    except Exception:
                        pass
                    return count

                def _count_ayas_in_results(field, term_text):
                    """Count unique ayas (documents) containing a term within the search result documents."""
                    count = 0
                    try:
                        m = _index_reader.postings(field, term_text)
                        while m.is_active():
                            if m.id() in _result_docnums:
                                count += 1
                            m.next()
                    except Exception:
                        pass
                    return count


                matches = 0
                matches_in_results = 0
                docs = 0
                docs_in_results = 0
                nb_vocalizations_globale = 0
                cpt = 1

                # ── Batch fetch word-child data for ALL query terms ───────────
                # Instead of issuing up to 4 separate word-index queries *per
                # query term* (vocalization lookup, word-data lookup, lemma
                # derivation, root derivation), we issue at most 2 batch queries
                # before the term loop and build in-memory lookup dicts.
                # For a 20-term query this reduces ≤80 round-trips to ≤2.
                #
                # _batch_word_data : norm → {"lemma": str|None,
                #                            "root":  str|None,
                #                            "words": set(vocalized forms)}
                # _batch_deriv_by_lemma : lemma → set(normalized forms)
                # _batch_deriv_by_root  : root  → set(normalized forms)
                _batch_word_data: dict = {}
                _batch_deriv_by_lemma: defaultdict = defaultdict(set)
                _batch_deriv_by_root: defaultdict = defaultdict(set)

                if (word_vocalizations or word_derivations) and _wi_searcher is not None:
                    _batch_norms = sorted({
                        strip_vocalization(t[1])
                        for t in termz if t[0] in ("aya", "aya_")
                    })
                    if _batch_norms:
                        # Batch query 1 – word forms, lemma, root for every term.
                        _bq1_norm = (
                            wquery.Or([wquery.Term("normalized", n) for n in _batch_norms])
                            if len(_batch_norms) > 1
                            else wquery.Term("normalized", _batch_norms[0])
                        )
                        _bq1 = wquery.And([wquery.Term("kind", "word"), _bq1_norm])
                        _bq1_res = self.QSE.search_with_shared_searcher(
                            _wi_searcher, _bq1, limit=len(_batch_norms) * 50
                        )
                        for _bw in _bq1_res:
                            _bn = _bw.get("normalized")
                            if not _bn:
                                continue
                            if _bn not in _batch_word_data:
                                _batch_word_data[_bn] = {
                                    "lemma": None, "root": None, "words": set()
                                }
                            _be = _batch_word_data[_bn]
                            if _be["lemma"] is None:
                                _be["lemma"] = _bw.get("lemma") or None
                            if _be["root"] is None:
                                _be["root"] = _bw.get("root") or None
                            _wf = _bw.get("word")
                            if _wf:
                                _be["words"].add(_wf)

                        if word_derivations:
                            # Batch query 2 – derivation siblings by lemma & root.
                            _all_lemmas = sorted({
                                d["lemma"] for d in _batch_word_data.values()
                                if d["lemma"]
                            })
                            _all_roots = sorted({
                                d["root"] for d in _batch_word_data.values()
                                if d["root"]
                            })
                            _bq2_parts = []
                            if _all_lemmas:
                                _bq2_parts.append(
                                    wquery.Or([wquery.Term("lemma", l) for l in _all_lemmas])
                                    if len(_all_lemmas) > 1
                                    else wquery.Term("lemma", _all_lemmas[0])
                                )
                            if _all_roots:
                                _bq2_parts.append(
                                    wquery.Or([wquery.Term("root", r) for r in _all_roots])
                                    if len(_all_roots) > 1
                                    else wquery.Term("root", _all_roots[0])
                                )
                            if _bq2_parts:
                                _bq2_filter = (
                                    wquery.Or(_bq2_parts)
                                    if len(_bq2_parts) > 1
                                    else _bq2_parts[0]
                                )
                                _bq2 = wquery.And([
                                    wquery.Term("kind", "word"), _bq2_filter
                                ])
                                _bq2_res = self.QSE.search_with_shared_searcher(
                                    _wi_searcher, _bq2,
                                    limit=(len(_all_lemmas) + len(_all_roots)) * 500,
                                )
                                for _d in _bq2_res:
                                    _dn = _d.get("normalized")
                                    if not _dn:
                                        continue
                                    _dl = _d.get("lemma")
                                    _dr = _d.get("root")
                                    if _dl:
                                        _batch_deriv_by_lemma[_dl].add(_dn)
                                    if _dr:
                                        _batch_deriv_by_root[_dr].add(_dn)
                # ── End batch fetch ───────────────────────────────────────────

                try:
                    for term in termz:
                        if term[0] == "aya" or term[0] == "aya_":
                            if term[2]:
                                matches += term[2]
                            docs += term[3]
                            term_matches_in_results = _count_term_in_results(term[0], term[1])
                            matches_in_results += term_matches_in_results
                            term_ayas_in_results = _count_ayas_in_results(term[0], term[1])
                            docs_in_results += term_ayas_in_results
                            if word_vocalizations:
                                _term_normalized = strip_vocalization(term[1])
                                _wdata = _batch_word_data.get(_term_normalized, {})
                                vocalizations = list(
                                    _wdata.get("words", set()) - {term[1]}
                                )
                                nb_vocalizations_globale += len(vocalizations)
                            if word_synonyms:
                                synonyms = syndict.get(term[1]) or []
                            derivations_extra = []
                            if word_derivations:
                                _norm_term = strip_vocalization(term[1])
                                _wdata = _batch_word_data.get(_norm_term, {})
                                lemma = _wdata.get("lemma")
                                root = _wdata.get("root")
                                derivations_set = (
                                    _batch_deriv_by_lemma.get(lemma, set())
                                    if lemma else set()
                                )
                                derivations = list(derivations_set)
                                if root:
                                    derivations_extra = list(
                                        _batch_deriv_by_root.get(root, set())
                                        - derivations_set
                                    )
                            else:
                                lemma = root = None
                                derivations = []

                            # Compute variations specific to this word: among all
                            # matched aya_ac terms, keep only those within
                            # fuzzy_maxdist edit distance of this word's unvocalized
                            # form.  This correctly scopes variations to each
                            # individual query word in multi-word queries.
                            word_normalized = strip_vocalization(term[1])
                            word_variations = [
                                v for v in _all_ac_variations
                                if _edit_distance(word_normalized, v) <= fuzzy_maxdist
                            ]
    
                            words_output["individual"][cpt] = {
                                "word": term[1],
                                "romanization": transliterate(romanization, term[1], ignore="", reverse=True) if romanization in
                                                                                                                 self.DOMAINS[
                                                                                                                     "romanization"] else None,
                                "nb_matches_overall": int(term[2]) if term[2] else 0,
                                "nb_matches": term_matches_in_results,
                                "nb_ayas_overall": term[3],
                                "nb_ayas": term_ayas_in_results,
                                "nb_vocalizations": len(vocalizations) if word_vocalizations else 0,  # unneeded
                                "vocalizations": vocalizations if word_vocalizations else [],
                                "nb_synonyms": len(synonyms) if word_synonyms else 0,  # unneeded
                                "synonyms": synonyms if word_synonyms else [],
                                "lemma": lemma if word_derivations else "",
                                "root": root if word_derivations else "",
                                "nb_derivations": len(derivations) if word_derivations else 0,  # unneeded
                                "derivations": derivations if word_derivations else [],
                                "nb_derivations_extra": len(derivations_extra),
                                "derivations_extra": derivations_extra,
                                "nb_variations": len(word_variations),
                                "variations": word_variations,
                            }
                            cpt += 1
                    words_output["global"] = {"nb_words": cpt - 1, "nb_matches_overall": int(matches),
                                              "nb_matches": matches_in_results,
                                              "nb_ayas_overall": docs,
                                              "nb_ayas": docs_in_results,
                                              "nb_vocalizations": nb_vocalizations_globale}
                finally:
                    if _wi_searcher is not None:
                        _wi_searcher.close()
            output["words"] = words_output
            # Build adjacent-aya lookup for prev/next aya text.
            _want_translation = bool(translation or lang)
            if prev_aya or next_aya:
                # Default sentinel values for boundary ayas (gid 0 and 6237 don't exist in the index).
                adja_ayas = {
                    0:    {"aya_": "----", "uth_": "----", "sura": "---", "aya_id": 0,    "sura_arabic": "---"},
                    6237: {"aya_": "----", "uth_": "----", "sura": "---", "aya_id": 9999, "sura_arabic": "---"},
                }
                if reslist:
                    # Collect the unique adjacent gids for this result page and build
                    # a pre-compiled query — avoids string concatenation + re-parsing
                    # overhead of the previous find_extended("( 0 OR gid:X ... )") approach.
                    _adja_gid_set = set()
                    for r in reslist:
                        if prev_aya:
                            _adja_gid_set.add(str(r["gid"] - 1))
                        if next_aya:
                            _adja_gid_set.add(str(r["gid"] + 1))
                    _adja_q = wquery.And([
                        wquery.Or([wquery.Term("gid", g) for g in _adja_gid_set]),
                        wquery.Term("kind", "aya"),
                    ])
                    adja_res, _, adja_searcher = self.QSE.search_with_query(
                        _adja_q, limit=len(_adja_gid_set) + 1, timelimit=timelimit
                    )
                    try:
                        extend_runtime += adja_res.runtime
                        for adja in adja_res:
                            adja_ayas[adja["gid"]] = {
                                "aya_": adja["aya_"],
                                "uth_": adja["uth_"],
                                "aya_id": adja["aya_id"],
                                "sura": adja["sura"],
                                "sura_arabic": adja["sura_arabic"],
                            }
                    finally:
                        adja_searcher.close()

            # translations: fetch all nested children for the result page
            trad_text = {}
            all_children = {}  # {gid: {trans_id: {text, id, lang, author}}}

            if reslist:
                # One pre-built query fetches ALL translation children for the result page.
                # Using search_with_query with a pre-compiled query object avoids the
                # string-building + re-parsing overhead of the old find_extended approach.
                child_q = wquery.And([
                    wquery.Or([wquery.Term("gid", str(r["gid"])) for r in reslist]),
                    wquery.Term("kind", "translation"),
                ])
                child_res, _, child_searcher = self.QSE.search_with_query(
                    child_q, limit=QURAN_TOTAL_VERSES, timelimit=timelimit
                )
                try:
                    extend_runtime += child_res.runtime
                    for ch in child_res:
                        g = ch["gid"]
                        tid = ch.get("trans_id") or ""
                        lang = ch.get("trans_lang") or ""
                        # Read text from the language-specific field when available,
                        # falling back to the stored trans_text for backward compat.
                        text_field = f"text_{lang}" if lang else None
                        field_text = ch.get(text_field) if text_field else None
                        text = field_text or ch.get("trans_text") or ""
                        if g not in all_children:
                            all_children[g] = {}
                        all_children[g][tid] = {
                            "text": text,
                            "id": tid,
                            "lang": lang,
                            "author": ch.get("trans_author") or "",
                        }
                finally:
                    child_searcher.close()

                # Build trad_text for user-selected translation/lang filter
                if _want_translation:
                    for g, trans_map in all_children.items():
                        if translation and translation in trans_map:
                            trad_text[g] = trans_map[translation]
                        elif lang:
                            for tid, tdata in trans_map.items():
                                if tdata["lang"] == lang:
                                    trad_text[g] = tdata
                                    break
    
            # Fetch word children (kind="word") for each aya on the result page when
            # the linguistic view is requested.  Word children carry the parent aya's
            # gid so they can be fetched with the same query used for translations.
            aya_words_map: defaultdict = defaultdict(list)  # {(sura_id, aya_id): [word_entry, ...]}
            if word_linguistics and reslist:
                try:
                    _wl_parent_q = wquery.And([
                        wquery.Term("kind", "aya"),
                        wquery.Or([wquery.NumericRange("gid", r["gid"], r["gid"])
                                   for r in reslist]),
                    ])
                    _wl_q = wquery.And([
                        wquery.NestedChildren(wquery.Term("kind", "aya"), _wl_parent_q),
                        wquery.Term("kind", "word"),
                    ])
                    wc_res, _, wc_searcher = self.QSE.search_with_query(
                        _wl_q, limit=min(len(reslist) * 300, 7500)
                    )
                    try:
                        extend_runtime += wc_res.runtime
                        for w in wc_res:
                            key = (w.get("sura_id"), w.get("aya_id"))
                            entry = {
                                "word_id":      w.get("word_id"),
                                "word":         w.get("word"),
                                "transliteration": w.get("word_transliteration"),
                                "normalized":   w.get("normalized"),
                                "spelled":      w.get("spelled"),
                                # Arabic (primary, indexed)
                                "pos":          w.get("pos"),
                                "type":         w.get("type"),
                                "root":         w.get("root"),
                                "lemma":        w.get("lemma"),
                                "mood":         w.get("mood"),
                                "case":         w.get("case"),
                                "state":        w.get("state"),
                                "special":      w.get("special"),
                                # English (stored-only)
                                "englishpos":   w.get("englishpos"),
                                "englishmood":  w.get("englishmood"),
                                "englishcase":  w.get("englishcase"),
                                "englishstate": w.get("englishstate"),
                                # Unchanged fields
                                "prefix":       w.get("prefix"),
                                "suffix":       w.get("suffix"),
                                "gender":       w.get("gender"),
                                "number":       w.get("number"),
                                "person":       w.get("person"),
                                "form":         w.get("form"),
                                "voice":        w.get("voice"),
                                "derivation":   w.get("derivation"),
                                "aspect":       w.get("aspect"),
                            }
                            aya_words_map[key].append(entry)
                        # Sort each aya's word list by word_id (ascending position order).
                        for key in aya_words_map:
                            aya_words_map[key].sort(key=_WORD_ID_KEY)
                    finally:
                        wc_searcher.close()
                except Exception:
                    pass  # index built without corpus words — silently skip
    
            # Fetch word children matching query terms for annotation_word.
            # Word children carry the parent aya gid (not the word's own word_gid)
            # so the same NestedChildren query used above applies here too.
            # Only words whose normalized form matches a search term are returned;
            # results are grouped by aya gid and sorted by word_id (position).
            annot_words_map: defaultdict = defaultdict(list)  # {gid: [{"word_id", "word", "normalized"}, ...]}
            if annotation_word and terms and reslist and self.QSE.OK:
                try:
                    # sorted() for deterministic term ordering across Python runs
                    _norm_terms = sorted(set(strip_vocalization(t) for t in terms if t))
                    if _norm_terms:
                        _aw_parent_q = wquery.And([
                            wquery.Term("kind", "aya"),
                            wquery.Or([wquery.NumericRange("gid", r["gid"], r["gid"])
                                       for r in reslist]),
                        ])
                        _aw_q = wquery.And([
                            wquery.NestedChildren(wquery.Term("kind", "aya"), _aw_parent_q),
                            wquery.Term("kind", "word"),
                            wquery.Or([wquery.Term("normalized", t) for t in _norm_terms]),
                        ])
                        # Generous limit: an aya has at most ~50 words; most terms
                        # match far fewer, but we allow 20 hits per term per aya.
                        # Cap at 10 000 to prevent runaway queries with many terms.
                        _aw_limit = min(len(reslist) * max(len(_norm_terms), 1) * 20, 10000)
                        _aw_res, _, _aw_srch = self.QSE.search_with_query(
                            _aw_q, limit=_aw_limit
                        )
                        try:
                            extend_runtime += _aw_res.runtime
                            for _w in _aw_res:
                                _g = _w.get("gid")
                                if _g is not None:
                                    annot_words_map[_g].append({
                                        "word_id":    _w.get("word_id"),
                                        "word":       _w.get("word"),
                                        "transliteration": _w.get("word_transliteration"),
                                        "normalized": _w.get("normalized"),
                                    })
                            for _g in annot_words_map:
                                annot_words_map[_g].sort(key=_WORD_ID_KEY)
                        finally:
                            _aw_srch.close()
                except Exception:
                    pass
    
            # Fetch all word children for annotation_aya (single-result view only;
            # annotation_aya is disabled when len(res) > 1 earlier in this method).
            # Returns every word of the matched aya with position, Uthmani text,
            # and normalized form — a lightweight alternative to word_linguistics.
            annot_aya_words_map: defaultdict = defaultdict(list)  # {gid: [{"word_id", "word", "normalized"}, ...]}
            if annotation_aya and reslist and self.QSE.OK:
                try:
                    _aa_parent_q = wquery.And([
                        wquery.Term("kind", "aya"),
                        wquery.Or([wquery.NumericRange("gid", r["gid"], r["gid"])
                                   for r in reslist]),
                    ])
                    _aa_q = wquery.And([
                        wquery.NestedChildren(wquery.Term("kind", "aya"), _aa_parent_q),
                        wquery.Term("kind", "word"),
                    ])
                    # An aya has at most ~300 words (safe upper bound for a
                    # single-aya annotation_aya request).
                    _aa_res, _, _aa_srch = self.QSE.search_with_query(_aa_q, limit=300)
                    try:
                        extend_runtime += _aa_res.runtime
                        for _w in _aa_res:
                            _g = _w.get("gid")
                            if _g is not None:
                                annot_aya_words_map[_g].append({
                                    "word_id":    _w.get("word_id"),
                                    "word":       _w.get("word"),
                                    "transliteration": _w.get("word_transliteration"),
                                    "normalized": _w.get("normalized"),
                                })
                        for _g in annot_aya_words_map:
                            annot_aya_words_map[_g].sort(key=_WORD_ID_KEY)
                    finally:
                        _aa_srch.close()
                except Exception:
                    pass
    
            output["runtime"] = round(extend_runtime, 5)
            output["interval"] = {
                "start": start,
                "end": end,
                "total": len(res),
                "page": ((start - 1) / range) + 1,
                "nb_pages": ((len(res) - 1) / range) + 1
            }
            output["translation_info"] = {}
            
            # Add facets to output if requested
            if facets_list and res:
                output["facets"] = {}
                for facet_field in facets_list:
                    try:
                        facet_groups = res.groups(facet_field)
                        # heapq.nlargest is O(n log k) vs O(n log n) for a full sort
                        # when returning only the top-50 facet values — and avoids
                        # materialising a sorted copy of the entire groups dict.
                        output["facets"][facet_field] = [
                            {"value": value, "count": len(doclist)}
                            for value, doclist in heapq.nlargest(
                                50, facet_groups.items(), key=_FACET_COUNT_KEY
                            )
                        ]
                    except Exception:
                        # If facet field doesn't exist or error, skip it
                        pass
            ### Ayas
            cpt = start - 1
            output["ayas"] = {}
            # Pre-compute recitation URL template once; the per-aya URL only
            # differs in sura_id / aya_id, so the subfolder lookup is invariant.
            _recitation_subfolder = (
                self._recitations[recitation]["subfolder"]
                if recitation and self._recitations.get(recitation)
                else None
            )
            for r in reslist:
                cpt += 1
                # Cache the gid and frequently-accessed identifiers once per
                # iteration so that subsequent accesses are plain local-variable
                # lookups instead of repeated Hit.__getitem__ → fields() calls.
                _gid = r["gid"]
                _aya_id = r["aya_id"]
                _sura_id = r["sura_id"]
                _sura_name = _KEYWORD_FIND(r["sura"])[0]
                _sura_arabic_name = _KEYWORD_FIND(r["sura_arabic"])[0]
                _sura_english_name = _KEYWORD_FIND(r["sura_english"])[0] if sura_info else None
                # Evaluate once per aya — reused in text, prev/next fields.
                _is_sajda = aya_sajda_info and r["sajda"] == "نعم"
                # Cache adjacent-aya dicts once per iteration; each is accessed
                # 4× (id, sura, sura_arabic, text) when prev_aya/next_aya is True.
                # The _prev_adja/_next_adja dict accesses below are guarded by the
                # same `if prev_aya` / `if next_aya` condition, so when the flag is
                # False the variable is never dereferenced (Python short-circuits
                # the conditional expression `{ ... } if flag else None`).
                _prev_adja = adja_ayas[_gid - 1] if prev_aya else None
                _next_adja = adja_ayas[_gid + 1] if next_aya else None
                output["ayas"][cpt] = {

                    "identifier": {"gid": _gid,
                                   "aya_id": _aya_id,
                                   "sura_id": _sura_id,
                                   "sura_name": _sura_name,
                                   "sura_arabic_name": _sura_arabic_name,
                                   },

                    "aya": {
                        "id": _aya_id,
                        "text": H(V(r["aya_"])) if _use_standard_script
                        else H(r["uth_"]),
                        "text_no_highlight": r["aya"] if _use_standard_script
                        else r["uth_"],
                        "transliteration": r.get("transliteration"),
                        "translation": TH(trad_text.get(_gid, {}).get("text")) if _want_translation else None,
                        "recitation": (
                            f'https://www.everyayah.com/data/{_recitation_subfolder}/%03d%03d.mp3' % (
                                int(_sura_id), int(_aya_id))
                            if _recitation_subfolder else None
                        ),
                        "prev_aya": {
                            "id": _prev_adja["aya_id"],
                            "sura": _prev_adja["sura"],
                            "sura_arabic": _prev_adja["sura_arabic"],
                            "text": V(_prev_adja["aya_"]) if _use_standard_script
                            else _prev_adja["uth_"],
                        } if prev_aya else None
                        ,
                        "next_aya": {
                            "id": _next_adja["aya_id"],
                            "sura": _next_adja["sura"],
                            "sura_arabic": _next_adja["sura_arabic"],
                            "text": V(_next_adja["aya_"]) if _use_standard_script
                            else _next_adja["uth_"],
                        } if next_aya else None
                        ,

                    },

                    "sura": {} if not sura_info
                    else {
                        "name": _sura_name,
                        "arabic_name": _sura_arabic_name,
                        "english_name": _sura_english_name,
                        "id": _sura_id,
                        "type": r["sura_type"],
                        "arabic_type": r["sura_type_arabic"],
                        "order": r["sura_order"],
                        "ayas": r["s_a"],
                        "stat": {} if not sura_stat_info
                        else {
                            "words": _ZERO_IF_NONE(r["s_w"]),
                            "godnames": _ZERO_IF_NONE(r["s_g"]),
                            "letters": _ZERO_IF_NONE(r["s_l"])
                        }

                    },

                    "position": {} if not aya_position_info
                    else {
                        "manzil": r["manzil"],
                        "juz": r["juz"],
                        "hizb": r["hizb"],
                        "rub": int(r["rub"]) % 4,
                        "page": r["page"]
                    },

                    "theme": {} if not aya_theme_info
                    else {
                        "chapter": r.get("chapter"),
                        "topic": r.get("topic"),
                        "subtopic": r.get("subtopic")
                    },

                    "stat": {} if not aya_stat_info
                    else {
                        "words": _ZERO_IF_NONE(r["a_w"]),
                        "letters": _ZERO_IF_NONE(r["a_l"]),
                        "godnames": _ZERO_IF_NONE(r["a_g"])
                    },

                    "sajda": {} if not aya_sajda_info
                    else {
                        "exist": _is_sajda,
                        "type": r["sajda_type"] if _is_sajda else None,
                        "id": _ZERO_IF_NONE(r["sajda_id"]) if _is_sajda else None,
                    },

                    "annotations": (
                        annot_words_map.get(_gid, []) if annotation_word
                        else annot_aya_words_map.get(_gid, []) if annotation_aya
                        else []
                    )
                }
                if word_linguistics:
                    output["ayas"][cpt]["words"] = aya_words_map.get(
                        (_sura_id, _aya_id), []
                    )
            return output
        finally:
            searcher.close()

    def _search_translation(self, flags):
        flags = {**self._defaults["flags"], **flags}
        query = flags["query"]
        sortedby = flags["sortedby"]
        reverse = IS_FLAG(flags, 'reverse')
        range = int(flags["perpage"]) if flags.get("perpage") \
            else flags["range"]
        offset = ((int(flags["page"]) - 1) * range) + 1 if flags.get("page") \
            else int(flags["offset"])
        highlight = flags["highlight"]
        timelimit = self._parse_timelimit(flags)

        query = query.replace("\\", "")

        # Use the cached translation parser built at __init__ time.
        if self._trans_parser is None:
            # No translation fields in schema — return empty result.
            return {
                "runtime": 0, "interval": {"start": 0, "end": 0, "total": 0, "page": 1, "nb_pages": 0},
                "translations": {},
            }
        _child_q = wquery.And([wquery.Term("kind", "translation"), self._trans_parser.parse(query)])
        res, termz, searcher = self.QSE.search_with_query(
            _child_q,
            limit=self._defaults["results_limit"]["translation"],
            sortedby=sortedby,
            reverse=reverse,
            timelimit=timelimit,
        )
        try:
            # Extract matched terms from the translation sub-query for highlight.
            terms = [t for field, t in _child_q.all_terms() if field in self._trans_fields]
            if highlight == "none":
                H = _COALESCE_TEXT
            else:
                H = lambda X: QTranslationHighlight(X, terms, type=highlight) if X else "-----"
    
            offset = 1 if offset < 1 else offset
            range = self._defaults["minrange"] if range < self._defaults["minrange"] else range
            range = self._defaults["maxrange"] if range > self._defaults["maxrange"] else range
            interval_end = offset + range - 1
            end = interval_end if interval_end < len(res) else len(res)
            start = offset if offset <= len(res) else -1
            reslist = [] if end == 0 or start == -1 else res[start - 1:end]
    
            # Fetch parent aya docs for the current result page using NestedParent.
            # NestedParent(_child_q) returns the parent aya of every matching translation child.
            parent_data = {}
            if reslist:
                _all_parents_q = wquery.Term("kind", "aya")
                _page_gids = {r["gid"] for r in reslist}
                _page_child_q = wquery.And([
                    wquery.Term("kind", "translation"),
                    wquery.Or([wquery.Term("gid", str(g)) for g in _page_gids]),
                ])
                _parent_q = wquery.NestedParent(_all_parents_q, _page_child_q)
                _parent_res, _, _parent_searcher = self.QSE.search_with_query(
                    _parent_q,
                    limit=self._defaults["results_limit"]["aya"],
                    timelimit=timelimit,
                )
                try:
                    for _p in _parent_res:
                        # Extract the stored-field dict immediately so that
                        # parent_data holds plain dicts rather than Hit objects.
                        # Hit objects carry a back-reference to their parent
                        # Results (hit.results), which keeps the entire _parent_res
                        # Results object (and its Whoosh Searcher reference) alive
                        # for the duration of this function.  Using _p.fields()
                        # breaks that reference, allowing _parent_res to be freed
                        # once no Hit references remain.
                        parent_data[_p["gid"]] = _p.fields()
                finally:
                    _parent_searcher.close()
    
            output = {}
            output["runtime"] = round(res.runtime, 5)
            output["interval"] = {
                "start": start,
                "end": end,
                "total": len(res),
                "page": ((start - 1) / range) + 1,
                "nb_pages": ((len(res) - 1) / range) + 1
            }
            cpt = start - 1
            output["translations"] = {}
            for r in reslist:
                cpt += 1
                _parent = parent_data.get(r["gid"], {})
                # Read text from the language-specific field when available,
                # falling back to the stored trans_text for backward compat.
                _r_lang = r.get("trans_lang") or ""
                _r_text_field = f"text_{_r_lang}" if _r_lang else None
                _r_field_text = r.get(_r_text_field) if _r_text_field else None
                _r_text = _r_field_text or r.get("trans_text") or ""
                output["translations"][cpt] = {
                    "identifier": {
                        "gid": r["gid"],
                        "translation_id": r.get("trans_id"),
                        "aya_id": _parent.get("aya_id"),
                        "sura_id": _parent.get("sura_id"),
                        "sura_name": (_KEYWORD_FIND(_parent["sura"]) or [None])[0] if _parent.get("sura") else None,
                        "sura_arabic_name": (_KEYWORD_FIND(_parent["sura_arabic"]) or [None])[0] if _parent.get("sura_arabic") else None,
                    },
                    "aya": {
                        "text": _parent.get("aya"),
                        "transliteration": _parent.get("transliteration"),
                    },
                    "translation": {
                        "text": H(_r_text),
                        "text_no_highlight": _r_text,
                        "author": r.get("trans_author"),
                        "lang": r.get("trans_lang"),
                    },
                }
            return output
        finally:
            searcher.close()

    def _search_words(self, flags):
        """Search word occurrence child documents nested within QSE aya groups.

        Word children are indexed with ``kind="word"`` alongside translation
        children.  This method searches them using a ``MultifieldParser`` that
        targets all indexed word fields — free-text fields (``word``,
        ``normalized``, ``word_standard``) as well as linguistic ID/KEYWORD
        fields (``pos``, ``type``, ``root``, ``arabicroot``, ``lemma``,
        ``arabiclemma``, ``gender``, ``number``, ``person``, ``form``,
        ``voice``, ``state``, ``derivation``, ``aspect``, ``mood``, ``case``)
        — combined with a ``kind="word"`` filter so only word children are
        returned.

        Field-qualified queries (e.g. ``root:رحم``) are supported for all
        indexed word fields.  Unqualified queries search across the primary
        text fields (``word``, ``normalized``, and ``word_standard``).

        The result structure includes:
        - ``words``: per-word morphological data plus the parent aya text.
          Each entry's ``aya.text`` / ``aya.text_no_highlight`` reflects the
          ``script`` flag: ``"standard"`` (default) gives the standard Arabic
          text; ``"uthmani"`` gives the Uthmani script text.
        - ``interval``: pagination metadata.
        - ``facets``: (optional) per-field value counts for ``root`` and
          ``type`` when requested via the ``facets`` flag.
        - ``runtime``: query execution time.
        """
        flags = {**self._defaults["flags"], **flags}
        query = flags["query"]
        sortedby = flags["sortedby"]
        reverse = IS_FLAG(flags, 'reverse')
        range_ = int(flags["perpage"]) if flags.get("perpage") \
            else flags["range"]
        offset = ((int(flags["page"]) - 1) * range_) + 1 if flags.get("page") \
            else int(flags["offset"])
        highlight = flags["highlight"]
        script = flags["script"]
        timelimit = self._parse_timelimit(flags)

        # Parse and validate the facets parameter against the allowed set.
        facets_param = flags.get("facets")
        facets_list = None
        if facets_param:
            if isinstance(facets_param, str):
                facets_list = [s for f in facets_param.split(",")
                               if (s := f.strip()) in _WORD_FACET_FIELDS]
            elif isinstance(facets_param, list):
                facets_list = [f for f in facets_param if f in _WORD_FACET_FIELDS]

        # Transliterate if no field filter is present
        query = query.replace("\\", "")
        if ":" not in query:
            query = transliterate("buckwalter", query, ignore="'_\"%*?#~[]{}:>+-|")

        empty_response = {
            "words": {},
            "interval": {"start": 0, "end": 0, "total": 0, "page": 1, "nb_pages": 0},
            "runtime": 0,
        }

        if not self.QSE.OK:
            return empty_response

        # Use the cached word parser built at __init__ time (avoids rebuilding
        # the MultifieldParser and re-filtering schema fields on every request).
        if self._word_parser is None:
            return empty_response

        try:
            word_query = self._word_parser.parse(query)
        except Exception:
            return empty_response

        # Restrict results to word children only.
        kind_filter = wquery.Term("kind", "word")
        combined = wquery.And([word_query, kind_filter])

        res, _terms, searcher = self.QSE.search_with_query(
            combined,
            limit=self._defaults["results_limit"]["word"],
            sortedby=sortedby,
            reverse=reverse,
            timelimit=timelimit,
        )

        try:
            # Extract query terms for highlighting (best-effort from the parsed query).
            terms = [t[1] for t in word_query.all_terms()
                     if isinstance(t[1], str)][:self._defaults["maxkeywords"]]
    
            # Pagination
            offset = 1 if offset < 1 else offset
            range_ = max(self._defaults["minrange"], min(range_, self._defaults["maxrange"]))
            interval_end = offset + range_ - 1
            end = min(interval_end, len(res))
            start = offset if offset <= len(res) else -1
            reslist = [] if end == 0 or start == -1 else res[start - 1:end]
    
            # When a result was matched by word_standard, add its Uthmanic 'word'
            # value to the keywords list so that the Uthmanic form of the word can
            # also be highlighted in the result text.
            _terms_set = set(terms)
            for _r in reslist:
                if len(terms) >= self._defaults["maxkeywords"]:
                    break
                _ws = _r.get("word_standard")
                _wu = _r.get("word")
                if _ws and _wu and _ws in _terms_set and _wu not in _terms_set:
                    terms.append(_wu)
                    _terms_set.add(_wu)
    
            if highlight == "none":
                H = _COALESCE_TEXT
            else:
                H = lambda X: self.QSE.highlight(X, terms, highlight) if X else "-----"

            # Pre-check script once — avoids re-evaluating per word in the result loop.
            _use_standard_script = script == "standard"

            # Build a gid→aya_text map so each word result can include the full
            # parent aya text in both standard and Uthmani scripts.  Word children
            # store the parent aya's gid, so a single batch query retrieves all
            # needed parent docs at once.
            gid_to_aya = {}
            if reslist:
                unique_gids = {r.get("gid") for r in reslist
                               if r.get("gid") is not None}
                if unique_gids:
                    try:
                        _parent_q = wquery.And([
                            wquery.Term("kind", "aya"),
                            wquery.Or([wquery.NumericRange("gid", gid, gid)
                                       for gid in unique_gids]),
                        ])
                        _parent_res = searcher.search(
                            _parent_q, limit=len(unique_gids) + 1
                        )
                        for _pr in _parent_res:
                            _g = _pr.get("gid")
                            if _g is not None:
                                gid_to_aya[_g] = {
                                    "standard": _pr.get("aya") or _pr.get("aya_") or "",
                                    "uthmani":  _pr.get("uth_") or "",
                                }
                    except Exception:
                        pass  # aya text enrichment is best-effort
    
            output = {
                "runtime": round(res.runtime, 5),
                "interval": {
                    "start": start,
                    "end": end,
                    "total": len(res),
                    "page": ((start - 1) / range_) + 1 if start > 0 else 1,
                    "nb_pages": ((len(res) - 1) / range_) + 1 if len(res) > 0 else 0,
                },
                "words": {},
            }
    
            cpt = start - 1
            for r in reslist:
                cpt += 1
                _gid = r.get("gid")
                _aya_data = gid_to_aya.get(_gid) or {}
                _aya_raw = (
                    _aya_data.get("standard") if _use_standard_script
                    else _aya_data.get("uthmani")
                )
                output["words"][cpt] = {
                    "identifier": {
                        "word_id": r.get("word_id"),
                        "aya_id":  r.get("aya_id"),
                        "sura_id": r.get("sura_id"),
                    },
                    "aya": {
                        "text":              H(_aya_raw or ""),
                        "text_no_highlight": _aya_raw,
                    },
                    "word": {
                        "text":              H(r.get("word", "")),
                        "text_no_highlight": r.get("word", ""),
                        "transliteration":   r.get("word_transliteration"),
                        "normalized":        r.get("normalized"),
                        "spelled":          r.get("spelled"),
                        # Arabic (primary, indexed)
                        "pos":              r.get("pos"),
                        "type":             r.get("type"),
                        "root":             r.get("root"),
                        "lemma":            r.get("lemma"),
                        "mood":             r.get("mood"),
                        "case":             r.get("case"),
                        "state":            r.get("state"),
                        "special":          r.get("special"),
                        # English (stored-only)
                        "englishpos":       r.get("englishpos"),
                        "englishmood":      r.get("englishmood"),
                        "englishcase":      r.get("englishcase"),
                        "englishstate":     r.get("englishstate"),
                        # Unchanged fields
                        "prefix":           r.get("prefix"),
                        "suffix":           r.get("suffix"),
                        "gender":           r.get("gender"),
                        "number":           r.get("number"),
                        "person":           r.get("person"),
                        "form":             r.get("form"),
                        "voice":            r.get("voice"),
                        "derivation":       r.get("derivation"),
                        "aspect":           r.get("aspect"),
                    },
                }

            # Compute facets over the full (un-paginated) result set so that
            # counts reflect the entire matched corpus, not just the current page.
            if facets_list and len(res) > 0:
                try:
                    groupedby = Facets()
                    for fld in facets_list:
                        groupedby.add_field(fld)
                    # _MAX_FACET_DOCS is a safe upper bound that covers the full corpus;
                    # limit=None would load every matching document into memory (OOM risk).
                    facet_res = searcher.search(combined, limit=_MAX_FACET_DOCS,
                                               groupedby=groupedby)
                    output["facets"] = {}
                    for fld in facets_list:
                        try:
                            groups = facet_res.groups(fld)
                            output["facets"][fld] = [
                                {"value": v, "count": len(docs)}
                                for v, docs in heapq.nlargest(
                                    50, groups.items(), key=_FACET_COUNT_KEY
                                )
                            ]
                        except Exception:
                            pass
                except Exception:
                    pass

            return output
        finally:
            searcher.close()


# ---------------------------------------------------------------------------
# Module-level binding resolved after Raw is defined.
#
# IS_FLAG() accesses this instead of Raw.DEFAULTS['flags'][key] (3 lookups)
# so each of its ~20 calls per _search_aya request costs only 1 dict lookup.
# ---------------------------------------------------------------------------
_FLAG_DEFAULTS = Raw.DEFAULTS['flags']

