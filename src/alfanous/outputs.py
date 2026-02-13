import logging
import re

from alfanous.text_processing import QArabicSymbolsFilter
from alfanous.data import *

from alfanous.romanization import transliterate
from alfanous.misc import locate, find, filter_doubles

STANDARD2UTHMANI = lambda x: std2uth_words.get(x) or x

FALSE_PATTERN = '^false|no|off|0$'


## a function to decide what is True and what is false
def IS_FLAG(flags, key):
    default = Raw.DEFAULTS['flags'][key]
    val = flags.get(key, default)
    if val is None or val == '':
        return default
    if not val or re.match(FALSE_PATTERN, str(val), re.IGNORECASE):
        return False
    return True


#
def scan_no_wildcards(query):
    return not ({"*", "?", "؟"} & set(query))


class Raw:
    DEFAULTS = {
        "minrange": 1,
        "maxrange": 25,
        "maxkeywords": 100,
        "results_limit": {
            "aya": 6236,
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
            "aya": True,
            "facets": None,
            "filter": None,
        }
    }

    ERRORS = {
        0: "success",
        1: "no action is chosen or action undefined",
        2: """This query is not permitted, you have to add  3 letters 
	           or more to use * (only two are permitted) and 2 letters or more to use ? (؟)\n
	     	-- Exceptions: ? (1),  ??????????? (11)
	     	""",
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
        "view": ["minimal", "normal", "full", "statistic", "linguistic", "recitation" "custom"],
        "recitation": [],  # range( 30 ),
        "translation": [],
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
        "sortedby": ["score", "relevance", "mushaf", "tanzil", "subject", "ayalength"],
        "offset": [],  # range(6237)
        "range": [],  # range(DEFAULTS["maxrange"]) , # used as "perpage" in paging mode
        "page": [],  # range(6237),  # overridden with offset
        "perpage": [],  # range( DEFAULTS["maxrange"] ) , # overridden with range
        "fuzzy": [True, False],
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
        "fuzzy": "fuzzy search [exprimental]",
        "aya": "enable retrieving of aya text in the case of translation search",
    }

    IDS = ["ALFANOUS_WUI_2342R52"]

    def __init__(self,
                 QSE_index=paths.QSE_INDEX,
                 TSE_index=paths.TSE_INDEX,
                 WSE_index=paths.WSE_INDEX,
                 Recitations_list_file=paths.RECITATIONS_LIST_FILE,
                 Translations_list_file=paths.TRANSLATIONS_LIST_FILE,
                 Hints_file=paths.HINTS_FILE,
                 Information_file=paths.INFORMATION_FILE):
        """
		initialize the search engines
		"""
        ##
        self.QSE = QSE(QSE_index)
        self.TSE = TSE(TSE_index)
        self.WSE = WSE(WSE_index)
        ##
        self._recitations = recitations(Recitations_list_file)
        self._translations = { id: id for id in self.TSE.list_values("id")}
        self._hints = hints(Hints_file)
        ##
        self._information = information(Information_file)
        ##
        # self._stats = Configs.stats( Stats_file )
        # enable it if you need statistics , disable it you prefer performance
        # self._init_stats()
        ##
        self._surates = {
            "Arabic": list(self.QSE.list_values("sura_arabic")),
            "English": list(self.QSE.list_values("sura_english")),
            "Romanized": list(self.QSE.list_values("sura"))
        }
        self._chapters = list(self.QSE.list_values("chapter"))
        self._topics = list(self.QSE.list_values("topic"))
        self._subtopics = list(self.QSE.list_values("subtopic"))

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
            "hints": self._hints,
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
            "roots": self._roots
        }

    def do(self, flags):
        return self._do(flags)

    def _do(self, flags):
        action = flags.get("action") or self._defaults["flags"]["action"]
        unit = flags.get("unit") or self._defaults["flags"]["unit"]
        query = flags.get("query") or self._defaults["flags"]["query"]
        # init the error message with Succes
        output = self._check(0, flags)
        if action == "search":
            assert scan_no_wildcards(query), self._check(2, flags)
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

    def _init_stats(self):
        ### initialization of stats
        stats = {}
        for ident in ["TOTAL"]:  # self._idents.extend(["TOTAL"])
            stats[ident] = {}
            stats[ident]["total"] = 0
            stats[ident]["other"] = {}
            stats[ident]["other"]["total"] = 0
            for action in self.DOMAINS["action"]:
                stats[ident][action] = {}
                stats[ident][action]["total"] = 0
                stats[ident][action]["other"] = {}
                stats[ident][action]["other"]["total"] = 0
                for flag, domain in self.DOMAINS.items():
                    stats[ident][action][flag] = {}
                    stats[ident][action][flag]["total"] = 0
                    stats[ident][action][flag]['other'] = 0
                    for val in domain:
                        stats[ident][action][flag][str(val)] = 0
        stats.update(self._stats)
        self._stats = stats

    def _process_stats(self, flags):
        """ process flags for statistics """
        stats = self._stats
        # Incrementation
        for ident in ["TOTAL"]:  # ["TOTAL",flags[ident]]
            stats[ident]["total"] += 1
            if flags.get("action"):
                action = flags["action"]
                if action in self._domains["action"]:
                    stats[ident][action]["total"] += 1
                    for flag, val in flags.items():
                        if flag in self._domains.keys():
                            stats[ident][action][flag]["total"] += 1
                            if val in self._domains[flag]:
                                stats[ident][action][flag][str(val)] += 1
                            else:
                                stats[ident][action][flag]["other"] += 1
                        else:
                            stats[ident][action]["other"]["total"] += 1
                else:
                    stats[ident]["other"]["total"] += 1
        self._stats = stats
        f = open(paths.STATS_FILE, "w")
        f.write(json.dumps(self._stats))

    def _show(self, flags):
        """  show metadata"""
        query = flags.get("query") or self._defaults["flags"]["query"]
        if query == "all":
            return {"show": self._all}
        elif query in self._all:
            return {"show": {query: self._all[query]}}
        else:
            return {"show": None}

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
        # preprocess query
        query = query.replace("\\", "")

        return self.QSE.suggest_all(query)

    def _search(self, flags, unit):
        if unit == "aya":
            search_results = self._search_aya(flags)
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
        romanization = flags["romanization"]
        highlight = flags["highlight"]
        script = flags["script"]
        vocalized = IS_FLAG(flags, 'vocalized')
        fuzzy = IS_FLAG(flags, 'fuzzy')
        view = flags["view"]
        
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

        if ":" not in query:
            query = transliterate("buckwalter", query, ignore="'_\"%*?#~[]{}:>+-|")

        # Search
        SE = self.QSE
        res, termz, searcher = SE.search_all(query, limit=self._defaults["results_limit"]["aya"], sortedby=sortedby, facets=facets_list, filter_dict=filter_dict)
        terms = [term[1] for term in list(termz)[:self._defaults["maxkeywords"]]]
        terms_uthmani = map(STANDARD2UTHMANI, terms)
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
        # Words & Annotations
        words_output = {"individual": {}}
        if word_info:
            matches = 0
            docs = 0
            nb_vocalizations_globale = 0
            cpt = 1
            annotation_word_query = "( 0 "
            for term in termz:
                if term[0] == "aya" or term[0] == "aya_":
                    if term[2]:
                        matches += term[2]
                    docs += term[3]
                    if term[0] == "aya_":
                        annotation_word_query += " OR word:%s " % term[1]
                    else:  # if aya
                        annotation_word_query += " OR normalized:%s " % STANDARD2UTHMANI(term[1])
                    if word_vocalizations:
                        vocalizations = vocalization_dict.get(strip_vocalization(term[1])) or []
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

                    words_output["individual"][cpt] = {
                        "word": term[1],
                        "romanization": transliterate(romanization, term[1], ignore="", reverse=True) if romanization in
                                                                                                         self.DOMAINS[
                                                                                                             "romanization"] else None,
                        "nb_matches": term[2],
                        "nb_ayas": term[3],
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
                    }
                    cpt += 1
            annotation_word_query += " ) "
            words_output["global"] = {"nb_words": cpt - 1, "nb_matches": matches,
                                      "nb_vocalizations": nb_vocalizations_globale}
        output["words"] = words_output
        # Magic_loop to built queries of Adjacents,translations and annotations in the same time
        if prev_aya or next_aya or translation or annotation_aya:
            adja_query = trad_query = annotation_aya_query = "( 0"

            for r in reslist:
                if prev_aya:
                    adja_query += " OR gid:%s " % str(r["gid"] - 1)
                    logging.error(r['gid'])
                if next_aya:
                    adja_query += " OR gid:%s " % str(r["gid"] + 1)
                if translation:
                    trad_query += " OR gid:%s " % str(r["gid"])

            adja_query += " )"
            trad_query += " )" + " AND id:%s " % translation
            annotation_aya_query += " )"

        if prev_aya or next_aya:
            adja_res, searcher = self.QSE.find_extended(adja_query, "gid")
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

        # translations
        if translation:
            trad_res, searcher = self.TSE.find_extended(trad_query, "gid")
            extend_runtime += trad_res.runtime
            trad_text = {}
            for tr in trad_res:
                trad_text[tr["gid"]] = tr["text"]
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
        logging.error(adja_ayas.keys())
        for r in reslist:
            logging.error(r['gid'])
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
                    "translation": trad_text.get(r["gid"]) if (translation != "None" and translation ) else None,

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


class Json(Raw):
    """ JSON output format """

    def do(self, flags):
        return json.dumps(self._do(flags), sort_keys=False, indent=4)
