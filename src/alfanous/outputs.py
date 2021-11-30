#!/usr/bin/python2
# -*- coding: UTF-8 -*-


"""
The programming interface, responsible of the output of all results
"""

import re
from pyparsing import ParseException

from alfanous.text_processing import QArabicSymbolsFilter
from alfanous.data import *
from alfanous.romanization import transliterate
from alfanous.misc import LOCATE, FIND, FILTER_DOUBLES
from alfanous.constants import LANGS

STANDARD2UTHMANI = lambda x: std2uth_words[x] if std2uth_words.has_key(x) else x

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
def SCAN_SUPERJOKERS(query):
    """
	a function to detect SuperJokers such as  *, ????, 
	a "*" query is a superjoker if it contains less then 3 letters
	a "?" query is a superjoker if it contains less then 2 letters
	a mixed query has the same conditions of a "?" query
	
	TODO that's a quick fix, the problem of superjokers must be fixed in 
			the query parser or by time delay 
	"""
    myreg = re.compile("\*+|[؟?]{2,9}|[ \t\n\r()+\-|]+|[^ ]+:|")
    filtred_query = myreg.sub("", query)
    super_joker = True if (len(filtred_query) < 3 and "*" in query) \
                          or (len(filtred_query) < 2 and (u"?" in query or u"؟" in query)) \
                          or query.count("*") > 2 \
        else False
    # Exceptions
    if query in [u"?", u"؟", u"???????????", u"؟؟؟؟؟؟؟؟؟؟؟؟"]:
        super_joker = False

    return super_joker


class Raw():
    """ Basic format for output, as  structures of python

	TODO Add word annotations to results
	FIXME terms are standard and Qurany corpus are uthmani   # resolve with uthmani mapping of Taha , + domains + errors
	
	"""

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
        }
    }

    ERRORS = {
        - 1: "fail, reason unknown",
        0: "success",
        1: "no action is chosen or action undefined",
        2: """This query is not permitted, you have to add  3 letters 
	           or more to use * (only two are permitted) and 2 letters or more to use ? (؟)\n
	     	-- Exceptions: ? (1),  ??????????? (11)
	     	""",
        3: "Parsing Query failed, please reformulate  the query",
        4: "One of specified fields doesn't exist"
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
        "recitation": [],  # xrange( 30 ),
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
        "offset": [],  # xrange(6237)
        "range": [],  # xrange(DEFAULTS["maxrange"]) , # used as "perpage" in paging mode
        "page": [],  # xrange(6237),  # overridden with offset
        "perpage": [],  # xrange( DEFAULTS["maxrange"] ) , # overridden with range
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
        self.FQSE = FQSE(QSE_index)
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
        self._fields = Fields
        self._fields_reverse = dict((v, k) for k, v in Fields.iteritems())
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
            "fields": self._fields,
            "fields_reverse": self._fields_reverse,
            "errors": self._errors,
            "domains": self._domains,
            "help_messages": self._helpmessages,
            "roots": self._roots
        }

    def do(self, flags):
        return self._do(flags)

    def _do(self, flags):
        action = flags["action"] if flags.has_key("action") else self._defaults["flags"]["action"]
        unit = flags["unit"] if flags.has_key("unit") else self._defaults["flags"]["unit"]
        query = flags["query"] if flags.has_key("query") else self._defaults["flags"]["query"]

        # init the error message with Succes
        output = self._check(0, flags)
        if action == "search":
            if SCAN_SUPERJOKERS(query):  # Quick fix!!
                output = self._check(2, flags)
            else:
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
            if flags.has_key("action"):
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
        query = flags["query"] if flags.has_key("query") else self._defaults["flags"]["query"]
        if query == "all":
            return {"show": self._all}
        elif self._all.has_key(query):
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
        query = flags["query"] if flags.has_key("query") else self._defaults["flags"]["query"]
        # preprocess query
        query = query.replace("\\", "")
        if not isinstance(query, unicode):
            query = unicode(query, 'utf8')
        try:
            output = self.QSE.suggest_all(query)
        except Exception:
            output = {}

        return output

    def _search(self, flags, unit):
        """ return the results of search for any unit """
        try:
            if unit == "aya":
                search_results = self._search_aya(flags)
            elif unit == "translation":
                search_results = self._search_translation(flags)
            elif unit == "word":
                search_results = self._search_word(flags)
            else:
                search_results = {}
            output = {"search": search_results}
            pass
        except ParseException:
            output = {"error": {"code": 3, "msg": self.ERRORS[3]}}
        except Exception:
            output = {"error": {"code": -1, "msg": self.ERRORS[-1]}}
        return output

    def _search_aya(self, flags):
        """
		return the results of aya search as a dictionary data structure
		"""
        # flags
        query = flags["query"] if flags.has_key("query") \
            else self._defaults["flags"]["query"]
        sortedby = flags["sortedby"] if flags.has_key("sortedby") \
            else self._defaults["flags"]["sortedby"]
        range = int(flags["perpage"]) if flags.has_key("perpage") \
            else flags["range"] if flags.has_key("range") \
            else self._defaults["flags"]["range"]
        ## offset = (page-1) * perpage   --  mode paging
        offset = ((int(flags["page"]) - 1) * range) + 1 if flags.has_key("page") \
            else int(flags["offset"]) if flags.has_key("offset") \
            else self._defaults["flags"]["offset"]
        recitation = flags["recitation"] if flags.has_key("recitation") \
            else self._defaults["flags"]["recitation"]
        translation = flags["translation"] if flags.has_key("translation") \
            else self._defaults["flags"]["translation"]
        romanization = flags["romanization"] if flags.has_key("romanization") \
            else self._defaults["flags"]["romanization"]
        highlight = flags["highlight"] if flags.has_key("highlight") \
            else self._defaults["flags"]["highlight"]
        script = flags["script"] if flags.has_key("script") \
            else self._defaults["flags"]["script"]
        vocalized = IS_FLAG(flags, 'vocalized')
        fuzzy = IS_FLAG(flags, 'fuzzy')
        view = flags["view"] if flags.has_key("view") \
            else self._defaults["flags"]["view"]

        # pre-defined views
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
        if not isinstance(query, unicode):
            query = unicode(query, 'utf8')

        if ":" not in query:
            query = unicode(transliterate("buckwalter", query, ignore="'_\"%*?#~[]{}:>+-|"))

        # Search
        SE = self.FQSE if fuzzy else self.QSE
        res, termz, searcher = SE.search_all(query, self._defaults["results_limit"]["aya"], sortedby=sortedby)
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
        searcher.close()
        output = {}

        ## disable annotations for aya words if there is more then one result
        if annotation_aya and len(res) > 1:
            annotation_aya = False

        # if True:
        ## strip vocalization when vocalized = true
        V = QArabicSymbolsFilter( \
            shaping=False, \
            tashkil=not vocalized, \
            spellerrors=False, \
            hamza=False \
            ).normalize_all
        strip_vocalization = QArabicSymbolsFilter( \
            shaping=False, \
            tashkil=True, \
            spellerrors=False, \
            hamza=False \
            ).normalize_all
        # highligh function that consider None value and non-definition
        H = lambda X: self.QSE.highlight(X, terms, highlight) if highlight != "none" and X else X if X else u"-----"
        # Numbers are 0 if not defined
        N = lambda X: X if X else 0
        # parse keywords lists , used for Sura names
        kword = re.compile(u"[^,،]+")
        keywords = lambda phrase: kword.findall(phrase)
        ##########################################
        extend_runtime = res.runtime
        # Words & Annotations
        words_output = {"individual": {}}
        if word_info:
            matches = 0
            docs = 0
            nb_vocalizations_globale = 0
            cpt = 1;
            annotation_word_query = u"( 0 "
            for term in termz:
                if term[0] == "aya" or term[0] == "aya_":
                    if term[2]:
                        matches += term[2]
                    docs += term[3]
                    if term[0] == "aya_":
                        annotation_word_query += u" OR word:%s " % term[1]
                    else:  # if aya
                        annotation_word_query += u" OR normalized:%s " % STANDARD2UTHMANI(term[1])
                    if word_vocalizations:
                        vocalizations = vocalization_dict[strip_vocalization(term[1])] if vocalization_dict.has_key(
                            strip_vocalization(term[1])) \
                            else []
                        nb_vocalizations_globale += len(vocalizations)
                    if word_synonyms:
                        synonyms = syndict[term[1]] if syndict.has_key(term[1]) \
                            else []
                    derivations_extra = []
                    if word_derivations:
                        lemma = LOCATE(derivedict["word_"], derivedict["lemma"], term[1])
                        if lemma:  # if different of none
                            derivations = FILTER_DOUBLES(FIND(derivedict["lemma"], derivedict["word_"], lemma))
                        else:
                            derivations = []
                        # go deeper with derivations
                        root = LOCATE(derivedict["word_"], derivedict["root"], term[1])
                        if root:  # if different of none
                            derivations_extra = list(
                                set(FILTER_DOUBLES(FIND(derivedict["root"], derivedict["word_"], lemma))) - set(
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
            annotation_word_query += u" ) "
            words_output["global"] = {"nb_words": cpt - 1, "nb_matches": matches,
                                      "nb_vocalizations": nb_vocalizations_globale}
        output["words"] = words_output;
        # Magic_loop to built queries of Adjacents,translations and annotations in the same time
        if prev_aya or next_aya or translation or annotation_aya:
            adja_query = trad_query = annotation_aya_query = u"( 0"

            for r in reslist:
                if prev_aya: adja_query += u" OR gid:%s " % unicode(r["gid"] - 1)
                if next_aya: adja_query += u" OR gid:%s " % unicode(r["gid"] + 1)
                if translation: trad_query += u" OR gid:%s " % unicode(r["gid"])
                if annotation_aya: annotation_aya_query += u" OR  ( aya_id:%s AND  sura_id:%s ) " % (
                    unicode(r["aya_id"]), unicode(r["sura_id"]))

            adja_query += u" )"
            trad_query += u" )" + u" AND id:%s " % unicode(translation)
            annotation_aya_query += u" )"

        # Adjacents
        if prev_aya or next_aya:
            adja_res, searcher = self.QSE.find_extended(adja_query, "gid")
            adja_ayas = {0: {"aya_": u"----", "uth_": u"----", "sura": u"---", "aya_id": 0, "sura_arabic": u"---"},
                         6237: {"aya_": u"----", "uth_": u"----", "sura": u"---", "aya_id": 9999,
                                "sura_arabic": u"---"}}
            for adja in adja_res:
                adja_ayas[adja["gid"]] = {"aya_": adja["aya_"], "uth_": adja["uth_"], "aya_id": adja["aya_id"],
                                          "sura": adja["sura"], "sura_arabic": adja["sura_arabic"]}
                extend_runtime += adja_res.runtime
            searcher.close()

        # translations
        if translation:
            trad_res, searcher = self.TSE.find_extended(trad_query, "gid")
            extend_runtime += trad_res.runtime
            trad_text = {}
            for tr in trad_res:
                trad_text[tr["gid"]] = tr["text"]
            searcher.close()

        # annotations for aya words
        if annotation_aya or (annotation_word and word_info):
            annotation_word_query = annotation_word_query if annotation_word and word_info else u"()"
            annotation_aya_query = annotation_aya_query if annotation_aya else u"()"
            annotation_query = annotation_aya_query + u" OR  " + annotation_word_query
            # print annotation_query.encode( "utf-8" )
            annot_res, searcher = self.WSE.find_extended(annotation_query, "gid")
            extend_runtime += annot_res.runtime
            ## prepare annotations for use
            annotations_by_word = {}
            annotations_by_position = {}
            for annot in annot_res:
                if (annotation_word and word_info):
                    if annot["normalized"] in terms_uthmani:
                        if annotations_by_word.has_key(annot["normalized"]):
                            if annotations_by_word[annot["normalized"]].has_key(annot["word"]):
                                annotations_by_word[annot["normalized"]][annot["word"]].append(annot);
                            else:
                                annotations_by_word[annot["normalized"]][annot["word"]] = [annot];
                        else:
                            annotations_by_word[annot["normalized"]] = {annot["word"]: [annot]}
                if annotation_aya:
                    if annotations_by_position.has_key((annot["sura_id"], annot["aya_id"])):
                        annotations_by_position[(annot["sura_id"], annot["aya_id"])][annot["word_id"]] = annot
                    else:
                        annotations_by_position[(annot["sura_id"], annot["aya_id"])] = {annot["word_id"]: annot}
            searcher.close()

        ## merge word annotations to word output
        if (annotation_word and word_info):
            for cpt in xrange(1, len(output["words"]["individual"]) + 1):
                current_word = STANDARD2UTHMANI(output["words"]["individual"][cpt]["word"])
                # print current_word.encode( "utf-8" ), "=>", annotations_by_word, "=>", list( annot_res )
                if annotations_by_word.has_key(current_word):
                    current_word_annotations = annotations_by_word[current_word]
                    output["words"]["individual"][cpt]["annotations"] = current_word_annotations
                    output["words"]["individual"][cpt]["nb_annotations"] = len(current_word_annotations)

        output["runtime"] = round(extend_runtime, 5)
        output["interval"] = {
            "start": start,
            "end": end,
            "total": len(res),
            "page": ((start - 1) / range) + 1,
            "nb_pages": ((len(res) - 1) / range) + 1
        }
        output["translation_info"] = {}
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
                    "translation": trad_text[r["gid"]] if (
                            translation != "None" and translation and trad_text.has_key(r["gid"])) else None,
                    "recitation": None if not recitation or not self._recitations.has_key(recitation) \
                        else u"https://www.everyayah.com/data/" + self._recitations[recitation]["subfolder"].encode(
                        "utf-8") + "/%03d%03d.mp3" % (r["sura_id"], r["aya_id"]),
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
                    "rub": r["rub"] % 4,
                    "page": r["page"],
                    "page_IN": r["page_IN"],
                    "ruku": r["ruku"],
                },

                "theme": {} if not aya_theme_info
                else {
                    "chapter": r["chapter"],
                    "topic": r["topic"],
                    "subtopic": r["subtopic"]
                },

                "stat": {} if not aya_stat_info
                else {
                    "words": N(r["a_w"]),
                    "letters": N(r["a_l"]),
                    "godnames": N(r["a_g"])
                },

                "sajda": {} if not aya_sajda_info
                else {
                    "exist": (r["sajda"] == u"نعم"),
                    "type": r["sajda_type"] if (r["sajda"] == u"نعم") else None,
                    "id": N(r["sajda_id"]) if (r["sajda"] == u"نعم") else None,
                },

                "annotations": {} if not annotation_aya or not annotations_by_position.has_key(
                    (r["sura_id"], r["aya_id"]))
                else annotations_by_position[(r["sura_id"], r["aya_id"])]
            }

        return output

    def _search_translation(self, flags):
        """
		return the results of translation search as a dictionary data structure
		"""
        # flags
        query = flags["query"] if flags.has_key("query") \
            else self._defaults["flags"]["query"]
        range = int(flags["perpage"]) if flags.has_key("perpage") \
            else flags["range"] if flags.has_key("range") \
            else self._defaults["flags"]["range"]
        ## offset = (page-1) * perpage   --  mode paging
        offset = ((int(flags["page"]) - 1) * range) + 1 if flags.has_key("page") \
            else int(flags["offset"]) if flags.has_key("offset") \
            else self._defaults["flags"]["offset"]
        highlight = flags["highlight"] if flags.has_key("highlight") \
            else self._defaults["flags"]["highlight"]
        view = flags["view"] if flags.has_key("view") \
            else self._defaults["flags"]["view"]

        # pre-defined views
        if view == "minimal":
            # page = 25
            aya = False
        elif view == "normal":
            pass
        elif view == "full":
            aya = True
        else:  # if view == custom or undefined
            aya = IS_FLAG(flags, 'aya')
        # preprocess query
        query = query.replace("\\", "")
        if not isinstance(query, unicode):
            query = unicode(query, 'utf8')

        # Search
        SE = self.TSE
        res, termz, searcher = SE.search_all(query, self._defaults["results_limit"]["translation"])
        terms = [term[1] for term in list(termz)[:self._defaults["maxkeywords"]]]
        # pagination
        offset = 1 if offset < 1 else offset;
        range = self._defaults["minrange"] if range < self._defaults["minrange"] else range;
        range = self._defaults["maxrange"] if range > self._defaults["maxrange"] else range;
        interval_end = offset + range - 1
        end = interval_end if interval_end < len(res) \
            else len(res) if len(res) < self._defaults["results_limit"]["translation"] \
            else self._defaults["results_limit"]["translation"]
        start = offset if offset <= len(res) else -1
        total = len(res)
        limited_total = total if total < self._defaults["results_limit"]["translation"] \
            else self._defaults["results_limit"]["translation"]

        reslist = [] if end == 0 or start == -1 else list(res)[start - 1:end]
        # closing the searcher
        searcher.close()

        output = {}

        # highligh function that consider None value and non-definition
        H = lambda X: SE.highlight(X, terms, highlight) if highlight != "none" and X else X if X else u"-----"
        # Numbers are 0 if not defined
        N = lambda X: X if X else 0
        extend_runtime = res.runtime

        # Magic_loop to built queries of ayas,etc in the same time
        if aya:
            aya_query = u"( 0"
            for r in reslist:
                if aya: aya_query += u" OR gid:%s " % unicode(r["gid"])
            aya_query += u" )"

        # original ayas
        if aya:
            aya_res, searcher = self.QSE.find_extended(aya_query, "gid")
            extend_runtime += aya_res.runtime
            aya_info = {}
            for ay in aya_res:
                aya_info[ay["gid"]] = {"text": ay["aya_"],
                                       "aya_id": ay["aya_id"],
                                       "sura_name": ay["sura"],
                                       "sura_arabic_name": ay["sura_arabic"],
                                       }
            searcher.close()

        output["runtime"] = round(extend_runtime, 5)
        output["interval"] = {
            "start": start,
            "end": end,
            "total": total,
            "page": ((start - 1) / range) + 1,
            "nb_pages": ((limited_total - 1) / range) + 1
        }
        output["terms"] = terms
        ### translations
        cpt = start - 1
        output["translations"] = {}
        for r in reslist:
            cpt += 1
            output["translations"][cpt] = {

                "identifier": {"gid": r["gid"],
                               "id": r["id"],
                               },

                "text": H(r["text"]),
                "aya": None if not aya \
                    else aya_info[r["gid"]],
                "info": {
                    "language": LANGS[r["lang"]],
                    "language_short": r["lang"],
                    "author": r["author"],
                    "country": r["country"],
                },

            }
        return output

    def _search_word(self, flags):
        """
		return the results of word search as a dictionary data structure
		"""
        # flags
        query = flags["query"] if flags.has_key("query") \
            else self._defaults["flags"]["query"]
        sortedby = flags["sortedby"] if flags.has_key("sortedby") \
            else self._defaults["flags"]["sortedby"]
        range = int(flags["perpage"]) if flags.has_key("perpage") \
            else flags["range"] if flags.has_key("range") \
            else self._defaults["flags"]["range"]
        offset = ((int(flags["page"]) - 1) * range) + 1 if flags.has_key("page") \
            else int(flags["offset"]) if flags.has_key("offset") \
            else self._defaults["flags"]["offset"]
        romanization = flags["romanization"] if flags.has_key("romanization") \
            else self._defaults["flags"]["romanization"]
        highlight = flags["highlight"] if flags.has_key("highlight") \
            else self._defaults["flags"]["highlight"]
        script = flags["script"] if flags.has_key("script") \
            else self._defaults["flags"]["script"]
        vocalized = IS_FLAG(flags, 'vocalized')
        view = flags["view"] if flags.has_key("view") \
            else self._defaults["flags"]["view"]

        # pre-defined views
        if view == "minimal":
            vocalized = False
            aya = False
        elif view == "normal":
            pass
        elif view == "full":
            romanization = "iso"
            aya = True
        elif view == "statistic":
            pass
        elif view == "linguistic":
            romanization = "buckwalter"
        elif view == "recitation":
            script = "uthmani"
        else:  # if view == custom or undefined
            aya = IS_FLAG(flags, 'aya')
        # preprocess query
        query = query.replace("\\", "")
        if not isinstance(query, unicode):
            query = unicode(query, 'utf8')

        if ":" not in query:
            query = unicode(transliterate("buckwalter", query, ignore="'_\"%*?#~[]{}:>+-|"))

        # Search
        SE = self.WSE
        res, termz, searcher = SE.search_all(query, self._defaults["results_limit"]["word"], sortedby=sortedby)
        terms = [term[1] for term in list(termz)[:self._defaults["maxkeywords"]]]

        # pagination
        offset = 1 if offset < 1 else offset;
        range = self._defaults["minrange"] if range < self._defaults["minrange"] else range;
        range = self._defaults["maxrange"] if range > self._defaults["maxrange"] else range;
        interval_end = offset + range - 1
        end = interval_end if interval_end < len(res) else len(res)
        start = offset if offset <= len(res) else -1
        reslist = [] if end == 0 or start == -1 else list(res)[start - 1:end]
        # closing the searcher
        searcher.close()

        output = {}

        # if True:
        ## strip vocalization when vocalized = true
        V = QArabicSymbolsFilter(**{
            'shaping': True,
            'tashkil': not vocalized,
            'spellerrors': False,
            'hamza': False,
            'uthmani_symbols': True,
        }).normalize_all
        V_shadda = QArabicSymbolsFilter(**{
            'shaping': False,
            'tashkil': False,
            'spellerrors': False,
            'hamza': False,
            'shadda': True,
            'uthmani_symbols': True
        }).normalize_all
        # highligh function that consider None value and non-definition
        H = lambda X: SE.highlight(X, terms, highlight) if highlight != "none" and X else X if X else u"-----"
        extend_runtime = res.runtime
        # Words & Annotations
        words_output = {"individual": {}}
        if True:
            matches = 0
            docs = 0
            cpt = 1;
            for term in termz:
                if True:  # term[0] == "normalized" or term[0] == "word":
                    if term[2]:
                        matches += term[2]
                    docs += term[3]
                    words_output["individual"][cpt] = {
                        "field": term[0],
                        "word": term[1],
                        "romanization": transliterate(romanization, term[1], ignore="", reverse=True) if romanization in
                                                                                                         self.DOMAINS[
                                                                                                             "romanization"] else None,
                        "nb_matches": term[2],
                        "nb_docs": term[3],
                    }
                    cpt += 1
            words_output["global"] = {"nb_words": cpt - 1, "nb_matches": matches}
        output["keywords"] = words_output;

        # Magic_loop to built queries of ayas,etc in the same time
        if aya:
            aya_query = u"( 0"
            for r in reslist:
                if aya: aya_query += u" OR ( sura_id:%s AND aya_id:%s )  " % (
                    unicode(r["sura_id"]), unicode(r["aya_id"]))
            aya_query += u" )"

        # original ayas
        if aya:
            aya_res, searcher = self.QSE.find_extended(aya_query, "gid")

            extend_runtime += aya_res.runtime
            aya_info = {}
            for ay in aya_res:
                if aya_info.has_key(ay["sura_id"]):
                    aya_info[ay["sura_id"]][ay["aya_id"]] = ay
                else:
                    aya_info[ay["sura_id"]] = {ay["aya_id"]: ay}
            searcher.close()

        output["runtime"] = round(extend_runtime, 5)
        output["interval"] = {
            "start": start,
            "end": end,
            "total": len(res),
            "page": ((start - 1) / range) + 1,
            "nb_pages": ((len(res) - 1) / range) + 1
        }
        ### Words
        cpt = start - 1
        output["words"] = {}
        for r in reslist:
            cpt += 1
            output["words"][cpt] = {
                "identifier": {
                    "gid": r["gid"],
                    "word_gid": r["word_gid"],
                    "aya_id": r["aya_id"],
                    "sura_id": r["sura_id"],
                    "word_id": r["word_id"],
                },

                "word": {
                    "text": r["word"],
                    "part": u"جذع",
                    "part_order": r["order"],
                    "token": r["arabictoken"],
                    "prefixes": r["prefix"],
                    "suffixes": r["suffix"],
                    "POS": {
                        "english": r["pos"],
                        "arabic": r["arabicpos"],
                    },
                    "mood": {
                        "english": r["mood"],
                        "arabic": r["arabicmood"],
                    },
                    "case": {
                        "english": r["case"],
                        "arabic": r["arabiccase"],
                    },
                    "root": {
                        # "english": r["root"],
                        "arabic": r["arabicroot"],
                    },
                    "lemma": {
                        # "english": r["lemma"],
                        "arabic": r["arabiclemma"],
                    },

                    "special": {
                        # "english": r["special"],
                        "arabic": r["arabicspecial"],
                    },
                    "derivation": r["derivation"],
                    "form": r["form"],
                    "gender": r["gender"],
                    "person": r["person"],
                    "number": r["number"],
                    "voice": r["voice"],
                    "state": r["state"],
                    "aspect": r["aspect"],
                },
                "aya": None if not aya \
                    else {
                    "text": SE.highlight(aya_info[r["sura_id"]][r["aya_id"]]["uth_"], [r["word"]], highlight, False),
                    "aya_id": aya_info[r["sura_id"]][r["aya_id"]]["aya_id"],
                    "sura_name": aya_info[r["sura_id"]][r["aya_id"]]["sura"],
                    "sura_arabic_name": aya_info[r["sura_id"]][r["aya_id"]]["sura_arabic"],

                },
            }
        return output


class Json(Raw):
    """ JSON output format """

    def do(self, flags):
        return json.dumps(self._do(flags), sort_keys=False, indent=4)


class Xml(Raw):
    """ XML output format

	@deprecated: Why Xml and CompleXity?! Use jSon and Simplicity!
	"""
    pass
