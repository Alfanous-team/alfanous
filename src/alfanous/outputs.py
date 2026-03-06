import logging
import re

from alfanous.text_processing import QArabicSymbolsFilter
from alfanous.data import *
from alfanous.constants import QURAN_TOTAL_VERSES
from alfanous.romanization import transliterate, arabizi_to_arabic_list, filter_candidates_by_wordset
from alfanous.misc import locate, find, filter_doubles
from whoosh import query as wquery
from whoosh.sorting import Facets
from alfanous.results_processing import QScore

STANDARD2UTHMANI = lambda x: std2uth_words.get(x) or x

FALSE_PATTERN = '^false|no|off|0$'


def _edit_distance(s, t):
    """Compute the Levenshtein edit distance between two strings."""
    m, n = len(s), len(t)
    if abs(m - n) > max(m, n, 1):
        return abs(m - n)
    d = list(range(n + 1))
    for i in range(1, m + 1):
        prev = d[:]
        d[0] = i
        for j in range(1, n + 1):
            d[j] = min(prev[j] + 1, d[j - 1] + 1, prev[j - 1] + (s[i - 1] != t[j - 1]))
    return d[n]


## a function to decide what is True and what is false
def IS_FLAG(flags, key):
    default = Raw.DEFAULTS['flags'][key]
    val = flags.get(key, default)
    if val is None or val == '':
        return default
    if not val or re.match(FALSE_PATTERN, str(val), re.IGNORECASE):
        return False
    return True



class Raw:
    DEFAULTS = {
        "minrange": 1,
        "maxrange": 25,
        "maxkeywords": 100,
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
            "aya_position_info": False,
            "aya_theme_info": True,
            "aya_stat_info": True,
            "aya_sajda_info": True,
            "annotation_word": False,
            "annotation_aya": False,
            "sortedby": "score",
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
        "action": ["search", "suggest", "show"],
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
        "aya_position_info": [True, False],
        "aya_theme_info": [True, False],
        "aya_stat_info": [True, False],
        "aya_sajda_info": [True, False],
        "annotation_word": [True, False],
        "annotation_aya": [True, False],
        "sortedby": ["score", "relevance", "mushaf", "tanzil", "ayalength"],
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
        "aya_position_info": "enable aya position information retrieving",
        "aya_theme_info": "enable aya theme information retrieving",
        "aya_stat_info": "enable aya stat information retrieving",
        "aya_sajda_info": "enable aya sajda information retrieving",
        "annotation_word": "enable query terms annotations retrieving",
        "annotation_aya": "enable aya words annotations retrieving",
        "sortedby": "sorting order of results",
        "offset": "starting offset of results",
        "range": "range of results",
        "page": "page number  [override offset]",
        "perpage": "results per page  [override range]",
        "fuzzy": "fuzzy search — searches aya_ (exact) and aya (normalised/stemmed) with Levenshtein distance matching",
        "fuzzy_maxdist": "maximum Levenshtein edit distance for fuzzy term matching (default: 1, only used when fuzzy=True)",
        "timelimit": "maximum number of seconds to spend on a search query (default: 5.0, use None or 0 to disable)",
        "aya": "enable retrieving of aya text in the case of translation search",
    }

    IDS = ["ALFANOUS_WUI_2342R52"]

    def __init__(self,
                 QSE_index=paths.QSE_INDEX,
                 WSE_index=paths.WSE_INDEX,
                 Recitations_list_file=paths.RECITATIONS_LIST_FILE,
                 Translations_list_file=paths.TRANSLATIONS_LIST_FILE,
                 Information_file=paths.INFORMATION_FILE,
                 AI_Rules_file=paths.AI_QUERY_TRANSLATION_RULES_FILE):
        """
		initialize the search engines
		"""
        ##
        self.QSE = QSE(QSE_index)
        self.WSE = WSE(WSE_index)
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
            "Arabic": list(self.QSE.list_values("sura_arabic")),
            "English": list(self.QSE.list_values("sura_english")),
            "Romanized": list(self.QSE.list_values("sura"))
        }
        self._chapters = list(self.QSE.list_stored_values("chapter"))
        self._topics = list(self.QSE.list_stored_values("topic"))
        self._subtopics = list(self.QSE.list_stored_values("subtopic"))

        self._defaults = self.DEFAULTS
        self._flags = self.DEFAULTS["flags"].keys()
        self._fields = arabic_to_english_fields
        self._fields_reverse = {v: k for k, v in arabic_to_english_fields.items()}
        self._roots = sorted(filter(bool, set(derivedict["root"])))
        self._errors = self.ERRORS
        self._domains = self.DOMAINS
        self._helpmessages = self.HELPMESSAGES
        self._ids = self.IDS  # dont send it to output , it's private
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
        query = flags.get("query") or self._defaults["flags"]["query"]
        # init the error message with Succes
        output = self._check(0, flags)
        if action == "search":
            output.update(self._search(flags, unit))
        elif action == "suggest":
            output.update(self._suggest(flags, unit))
        elif action == "show":
            output.update(self._show(flags))
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
            search_engine = self.WSE
            if field == "aya_":  # Use default field for word index
                field = "normalized"
        elif unit == "translation":
            search_engine = self.QSE
            if field == "aya_":  # Use trans_text as default field for translation children
                field = "trans_text"
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
            
            from whoosh.fields import TEXT
            is_text_field = field_obj is not None and isinstance(field_obj, TEXT)
            
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
                searcher = search_engine._docindex.get_index().searcher(weighting=QScore())
                
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
                    else:
                        kind_filter = wquery.Term("kind", "aya")
                    
                    # Search matching documents
                    results = searcher.search(kind_filter, limit=None, groupedby=groupedby)
                    
                    # Get facet groups
                    field_groups = results.groups(field)
                    
                    if mode == "unique":
                        # Get all unique values for the field
                        values = list(field_groups.keys())
                        result["keywords"] = values
                        result["count"] = len(values)
                    else:  # mode == "frequent"
                        # Get top N most frequent values with document counts
                        # Sort by frequency (number of documents) descending
                        sorted_items = sorted(field_groups.items(), key=lambda x: len(x[1]), reverse=True)
                        
                        # Take top N
                        top_items = sorted_items[:limit]
                        
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
        query = re.sub(r'[^\u0621-\u065F\u0670-\u06FF\s]', ' ', query)
        query = ' '.join(w for w in query.split() if w)

        return self.QSE.suggest_all(query)

    def _search(self, flags, unit):
        if unit == "aya":
            search_results = self._search_aya(flags)
        elif unit == "translation":
            search_results = self._search_translation(flags)
        elif unit == "word":
            search_results = self._search_word(flags)
        else:
            search_results = {}

        return {"search": search_results}

    def _search_aya(self, flags):

        flags = {**self._defaults["flags"], **flags}
        query = flags["query"]
        sortedby = flags["sortedby"]
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
            vocalized = False
            recitation = None
            translation = None
            lang = None
            prev_aya = next_aya = False
            sura_info = False
            word_info = False
            word_synonyms = False
            word_derivations = False
            word_vocalizations = False
            aya_position_info = aya_theme_info = aya_sajda_info = False
            aya_stat_info = False
            sura_stat_info = False
            annotation_aya = annotation_word = False
        elif view == "normal":
            prev_aya = next_aya = True
            sura_info = True
            word_info = True
            word_synonyms = False
            word_derivations = True
            word_vocalizations = True
            aya_position_info = aya_theme_info = aya_sajda_info = True
            aya_stat_info = True
            sura_stat_info = False
            annotation_aya = annotation_word = False
        elif view == "full":
            prev_aya = next_aya = True
            sura_info = True
            word_info = True
            word_synonyms = True
            word_derivations = True
            word_vocalizations = True
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

            aya_position_info = IS_FLAG(flags, 'aya_position_info')
            aya_theme_info = IS_FLAG(flags, 'aya_theme_info')
            aya_stat_info = IS_FLAG(flags, 'aya_stat_info')
            aya_sajda_info = IS_FLAG(flags, 'aya_sajda_info')
            annotation_aya = IS_FLAG(flags, 'annotation_aya')
            annotation_word = IS_FLAG(flags, 'annotation_word')

        # print query
        # preprocess query
        query = query.replace("\\", "")

        if ":" not in query and not re.search(r'[\u0600-\u06FF]', query):
            # Non-Arabic query: route to nested child translation docs via
            # NestedParent so results are parent aya documents that have
            # translations matching the query text.
            from whoosh import query as wq
            from whoosh.qparser import QueryParser as _QP, OrGroup as _OrGroup
            _trans_parser = _QP("trans_text", self.QSE._schema,
                                group=_OrGroup)
            _trans_q = _trans_parser.parse(query)
            _nested_q = wq.NestedParent(wq.Term("kind", "aya"), _trans_q)
            res, termz, searcher = self.QSE.search_with_query(
                _nested_q,
                limit=self._defaults["results_limit"]["aya"],
                sortedby=sortedby,
                timelimit=timelimit,
            )
            terms, _all_ac_variations = [], []
            terms_uthmani = iter([])
        else:
            # Arabic (or field-qualified) query — search aya fields directly.
            res, termz, searcher = self.QSE.search_all(query, limit=self._defaults["results_limit"]["aya"], sortedby=sortedby, facets=facets_list, filter_dict=filter_dict, fuzzy=fuzzy, fuzzy_maxdist=fuzzy_maxdist, timelimit=timelimit)
            terms = [term[1] for term in list(termz)[:self._defaults["maxkeywords"]]]
            terms_uthmani = map(STANDARD2UTHMANI, terms)
            # All matched aya_ac variation terms (only populated when fuzzy=True).
            # Used in the word_info loop to derive per-word variation lists.
            _all_ac_variations = [term[1] for term in termz if term[0] == "aya_ac"]
        # pagination
        offset = 1 if offset < 1 else offset
        range = self._defaults["minrange"] if range < self._defaults["minrange"] else range
        range = self._defaults["maxrange"] if range > self._defaults["maxrange"] else range
        interval_end = offset + range - 1
        end = interval_end if interval_end < len(res) else len(res)
        start = offset if offset <= len(res) else -1
        reslist = [] if end == 0 or start == -1 else list(res)[start - 1:end]
        # todo pagination should be done inside search operation for better performence
        # closing the searcher
        # Pre-built gid query for the current result page, used for translation and
        # fixed-translation lookups without re-iterating reslist multiple times.
        _gid_base_query = "( 0" + "".join(" OR gid:%s" % str(r["gid"]) for r in reslist) + " )"

        output = {}

        ## disable annotations for aya words if there is more then one result
        if annotation_aya and len(res) > 1:
            annotation_aya = False

        # if True:
        ## strip vocalization when vocalized = true
        V = QArabicSymbolsFilter(
            shaping=False,
            tashkil=not vocalized,
            spellerrors=False,
            hamza=False
        ).normalize_all
        strip_vocalization = QArabicSymbolsFilter(
            shaping=False,
            tashkil=True,
            spellerrors=False,
            hamza=False
        ).normalize_all
        # highligh function that consider None value and non-definition
        H = lambda X: self.QSE.highlight(X, terms, highlight) if highlight != "none" and X else X if X else "-----"
        # Numbers are 0 if not defined
        N = lambda X: X if X else 0
        # parse keywords lists , used for Sura names
        kword = re.compile("[^,،]+")
        keywords = lambda phrase: kword.findall(phrase)
        ##########################################
        extend_runtime = res.runtime
        # Pre-compute result docnums for counting matches within the result set
        _result_docnums = set(hit.docnum for hit in res)
        _index_reader = searcher.reader()

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

        # Words & Annotations
        words_output = {"individual": {}}
        if word_info:
            matches = 0
            matches_in_results = 0
            docs = 0
            docs_in_results = 0
            nb_vocalizations_globale = 0
            cpt = 1
            annotation_word_query = "( 0 "
            for term in termz:
                if term[0] == "aya" or term[0] == "aya_":
                    if term[2]:
                        matches += term[2]
                    docs += term[3]
                    term_matches_in_results = _count_term_in_results(term[0], term[1])
                    matches_in_results += term_matches_in_results
                    term_ayas_in_results = _count_ayas_in_results(term[0], term[1])
                    docs_in_results += term_ayas_in_results
                    if term[0] == "aya_":
                        annotation_word_query += " OR word:%s " % term[1]
                    else:  # if aya
                        annotation_word_query += " OR normalized:%s " % STANDARD2UTHMANI(term[1])
                    if word_vocalizations:
                        vocalizations = vocalization_dict.get(strip_vocalization(term[1])) or []
                        if isinstance(vocalizations, str):
                            vocalizations = [vocalizations]
                        nb_vocalizations_globale += len(vocalizations)
                    if word_synonyms:
                        synonyms = syndict.get(term[1]) or []
                    derivations_extra = []
                    if word_derivations:
                        lemma = locate(derivedict["word_"], derivedict["lemma"], term[1])
                        if lemma:  # if different of none
                            derivations = filter_doubles(find(derivedict["lemma"], derivedict["word_"], lemma))
                        else:
                            derivations = []
                        # go deeper with derivations
                        root = locate(derivedict["word_"], derivedict["root"], term[1])
                        if root:  # if different of none
                            derivations_extra = list(
                                set(filter_doubles(find(derivedict["root"], derivedict["word_"], lemma))) - set(
                                    derivations))

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
            annotation_word_query += " ) "
            words_output["global"] = {"nb_words": cpt - 1, "nb_matches_overall": int(matches),
                                      "nb_matches": matches_in_results,
                                      "nb_ayas_overall": docs,
                                      "nb_ayas": docs_in_results,
                                      "nb_vocalizations": nb_vocalizations_globale}
        output["words"] = words_output
        # Magic_loop to built queries of Adjacents,translations and annotations in the same time
        _want_translation = bool(translation or lang)
        if prev_aya or next_aya or annotation_aya:
            adja_query = annotation_aya_query = "( 0"

            for r in reslist:
                if prev_aya:
                    adja_query += " OR gid:%s " % str(r["gid"] - 1)
                if next_aya:
                    adja_query += " OR gid:%s " % str(r["gid"] + 1)

            # Restrict to parent aya documents only (gid also matches children).
            adja_query += " ) AND kind:aya"
            annotation_aya_query += " )"

        if prev_aya or next_aya:
            adja_res, adja_searcher = self.QSE.find_extended(adja_query, "gid")
            adja_ayas = {0:
                             {"aya_": "----",
                              "uth_": "----",
                              "sura": "---",
                              "aya_id": 0, "sura_arabic": "---"},
                         6237: {"aya_": "----", "uth_": "----", "sura": "---", "aya_id": 9999,
                                "sura_arabic": "---"}}
            for adja in adja_res:
                adja_ayas[adja["gid"]] = {"aya_": adja["aya_"], "uth_": adja["uth_"], "aya_id": adja["aya_id"],
                                          "sura": adja["sura"], "sura_arabic": adja["sura_arabic"]}
                extend_runtime += adja_res.runtime
            adja_searcher.close()

        # translations + always-present transliteration/tafssir
        trad_text = {}
        all_children = {}  # {gid: {trans_id: {text, id, lang, author}}}

        if reslist:
            # One query fetches ALL children for the result page.
            child_q = _gid_base_query + " AND kind:translation"
            child_res, child_searcher = self.QSE.find_extended(child_q, "gid")
            extend_runtime += child_res.runtime
            for ch in child_res:
                g = ch["gid"]
                tid = ch.get("trans_id") or ""
                if g not in all_children:
                    all_children[g] = {}
                all_children[g][tid] = {
                    "text": ch.get("trans_text") or "",
                    "id": tid,
                    "lang": ch.get("trans_lang") or "",
                    "author": ch.get("trans_author") or "",
                }
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
                    # facet_groups is a dict where keys are values and values are lists of docnums
                    output["facets"][facet_field] = [
                        {"value": value, "count": len(doclist)}
                        for value, doclist in sorted(facet_groups.items(), key=lambda x: len(x[1]), reverse=True)
                    ]
                except:
                    # If facet field doesn't exist or error, skip it
                    pass
        ### Ayas
        cpt = start - 1
        output["ayas"] = {}
        for r in reslist:
            cpt += 1
            output["ayas"][cpt] = {

                "identifier": {"gid": r["gid"],
                               "aya_id": r["aya_id"],
                               "sura_id": r["sura_id"],
                               "sura_name": keywords(r["sura"])[0],
                               "sura_arabic_name": keywords(r["sura_arabic"])[0],
                               },

                "aya": {
                    "id": r["aya_id"],
                    "text": H(V(r["aya_"])) if script == "standard"
                    else H(r["uth_"]),
                    "text_no_highlight": r["aya"] if script == "standard"
                    else r["uth_"],
                    "translation": trad_text.get(r["gid"], {}).get("text") if _want_translation else None,
                    "transliteration": all_children.get(r["gid"], {}).get("en.transliteration", {}).get("text"),
                    "tafssir": all_children.get(r["gid"], {}).get("ar.jalalayn", {}).get("text"),

                    "recitation": None if not recitation or not self._recitations.get(recitation) \
                        else f'https://www.everyayah.com/data/{self._recitations[recitation]["subfolder"]}/%03d%03d.mp3' % (
                    int(r["sura_id"]), int(r["aya_id"])),
                    "prev_aya": {
                        "id": adja_ayas[r["gid"] - 1]["aya_id"],
                        "sura": adja_ayas[r["gid"] - 1]["sura"],
                        "sura_arabic": adja_ayas[r["gid"] - 1]["sura_arabic"],
                        "text": V(adja_ayas[r["gid"] - 1]["aya_"]) if script == "standard"
                        else adja_ayas[r["gid"] - 1]["uth_"],
                    } if prev_aya else None
                    ,
                    "next_aya": {
                        "id": adja_ayas[r["gid"] + 1]["aya_id"],
                        "sura": adja_ayas[r["gid"] + 1]["sura"],
                        "sura_arabic": adja_ayas[r["gid"] + 1]["sura_arabic"],
                        "text": V(adja_ayas[r["gid"] + 1]["aya_"]) if script == "standard"
                        else adja_ayas[r["gid"] + 1]["uth_"],
                    } if next_aya else None
                    ,

                },

                "sura": {} if not sura_info
                else {
                    "name": keywords(r["sura"])[0],
                    "arabic_name": keywords(r["sura_arabic"])[0],
                    "english_name": keywords(r["sura_english"])[0],
                    "id": r["sura_id"],
                    "type": r["sura_type"],
                    "arabic_type": r["sura_type_arabic"],
                    "order": r["sura_order"],
                    "ayas": r["s_a"],
                    "stat": {} if not sura_stat_info
                    else {
                        "words": N(r["s_w"]),
                        "godnames": N(r["s_g"]),
                        "letters": N(r["s_l"])
                    }

                },

                "position": {} if not aya_position_info
                else {
                    "manzil": r["manzil"],
                    "juz": r["juz"],
                    "hizb": r["hizb"],
                    "rub": int(r["rub"]) % 4,
                    "page": r["page"],
                    "page_IN": r["page_IN"]
                },

                "theme": {} if not aya_theme_info
                else {
                    "chapter": r.get("chapter"),
                    "topic": r.get("topic"),
                    "subtopic": r.get("subtopic")
                },

                "stat": {} if not aya_stat_info
                else {
                    "words": N(r["a_w"]),
                    "letters": N(r["a_l"]),
                    "godnames": N(r["a_g"])
                },

                "sajda": {} if not aya_sajda_info
                else {
                    "exist": (r["sajda"] == "نعم"),
                    "type": r["sajda_type"] if (r["sajda"] == "نعم") else None,
                    "id": N(r["sajda_id"]) if (r["sajda"] == "نعم") else None,
                },

                "annotations": {}
            }
        searcher.close()
        return output

    def _search_translation(self, flags):
        flags = {**self._defaults["flags"], **flags}
        query = flags["query"]
        sortedby = flags["sortedby"]
        range = int(flags["perpage"]) if flags.get("perpage") \
            else flags["range"]
        offset = ((int(flags["page"]) - 1) * range) + 1 if flags.get("page") \
            else int(flags["offset"])
        highlight = flags["highlight"]
        timelimit = self._parse_timelimit(flags)

        query = query.replace("\\", "")

        # Search trans_text in nested child docs directly.
        from whoosh import query as wq
        from whoosh.qparser import QueryParser as _QP, OrGroup as _OrGroup
        _trans_parser = _QP("trans_text", self.QSE._schema,
                            group=_OrGroup)
        _trans_q = wq.And([wq.Term("kind", "translation"), _trans_parser.parse(query)])
        res, termz, searcher = self.QSE.search_with_query(
            _trans_q,
            limit=self._defaults["results_limit"]["translation"],
            sortedby=sortedby,
            timelimit=timelimit,
        )
        terms = []
        H = lambda X: self.QSE.highlight(X, terms, highlight) if highlight != "none" and X else X if X else "-----"

        offset = 1 if offset < 1 else offset
        range = self._defaults["minrange"] if range < self._defaults["minrange"] else range
        range = self._defaults["maxrange"] if range > self._defaults["maxrange"] else range
        interval_end = offset + range - 1
        end = interval_end if interval_end < len(res) else len(res)
        start = offset if offset <= len(res) else -1
        reslist = [] if end == 0 or start == -1 else list(res)[start - 1:end]

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
            output["translations"][cpt] = {
                "identifier": {
                    "gid": r["gid"],
                    "translation_id": r.get("trans_id"),
                },
                "translation": {
                    "text": H(r.get("trans_text")),
                    "text_no_highlight": r.get("trans_text"),
                    "author": r.get("trans_author"),
                    "lang": r.get("trans_lang"),
                },
            }
        searcher.close()
        return output

    def _search_word(self, flags):
        flags = {**self._defaults["flags"], **flags}
        query = flags["query"]
        sortedby = flags["sortedby"]
        range = int(flags["perpage"]) if flags.get("perpage") \
            else flags["range"]
        offset = ((int(flags["page"]) - 1) * range) + 1 if flags.get("page") \
            else int(flags["offset"])
        highlight = flags["highlight"]
        timelimit = self._parse_timelimit(flags)

        # preprocess query
        query = query.replace("\\", "")

        if ":" not in query:
            query = transliterate("buckwalter", query, ignore="'_\"%*?#~[]{}:>+-|")

        SE = self.WSE
        if not SE.OK:
            return {
                "words": {},
                "interval": {"start": 0, "end": 0, "total": 0, "page": 1, "nb_pages": 0},
                "runtime": 0
            }

        res, termz, searcher = SE.search_all(query, limit=self._defaults["results_limit"]["word"], sortedby=sortedby, timelimit=timelimit)
        terms = [term[1] for term in list(termz)[:self._defaults["maxkeywords"]]]

        # pagination
        offset = 1 if offset < 1 else offset
        range = self._defaults["minrange"] if range < self._defaults["minrange"] else range
        range = self._defaults["maxrange"] if range > self._defaults["maxrange"] else range
        interval_end = offset + range - 1
        end = interval_end if interval_end < len(res) else len(res)
        start = offset if offset <= len(res) else -1
        reslist = [] if end == 0 or start == -1 else list(res)[start - 1:end]

        output = {}
        H = lambda X: SE.highlight(X, terms, highlight) if highlight != "none" and X else X if X else "-----"

        output["runtime"] = round(res.runtime, 5)
        output["interval"] = {
            "start": start,
            "end": end,
            "total": len(res),
            "page": ((start - 1) / range) + 1,
            "nb_pages": ((len(res) - 1) / range) + 1
        }

        cpt = start - 1
        output["words"] = {}
        for r in reslist:
            cpt += 1
            output["words"][cpt] = {
                "identifier": {
                    "gid": r["gid"],
                    "word_id": r.get("word_id"),
                    "aya_id": r.get("aya_id"),
                    "sura_id": r.get("sura_id"),
                },
                "word": {
                    "text": H(r["word"]),
                    "text_no_highlight": r["word"],
                    "normalized": r.get("normalized"),
                    "spelled": r.get("spelled"),
                    "pos": r.get("pos"),
                    "type": r.get("type"),
                    "arabicroot": r.get("arabicroot"),
                    "arabiclemma": r.get("arabiclemma"),
                },
            }

        searcher.close()
        return output


class Json(Raw):
    """ JSON output format """

    def do(self, flags):
        return json.dumps(self._do(flags), sort_keys=False, indent=4)
