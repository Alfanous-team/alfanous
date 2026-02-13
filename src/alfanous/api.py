""" hint:

    Use `alfanous.search` for searching in Quran verses and translations.
    Use `alfanous.get_info` for getting meta info.
    Use `alfanous.do` method for search, suggestion and get most useful info.
    """

# import Output object
from alfanous.outputs import Raw as _search_engine
# import default Paths
from alfanous.data import paths as PATHS

DEFAULTS, DOMAINS, HELPMESSAGES = _search_engine.DEFAULTS, _search_engine.DOMAINS, _search_engine.HELPMESSAGES
FLAGS = DEFAULTS["flags"].keys()

from alfanous.outputs import arabic_to_english_fields as _fields

FIELDS_ARABIC = _fields.keys()
FIELDS_ENGLISH = _fields.values()

_R = _search_engine()


# Pivot function for search, suggestion, show info
def do(flags):
    return _R.do(flags)


def search(query, unit="aya", page=1, sortedby="relevance", fuzzy=False, view="normal", highlight="bold", flags={}, facets=None):
    all_flags = flags
    all_flags.update({"action": "search",
                      "unit": unit,
                      "query": query,
                      "page": page,
                      "sortedby": sortedby,
                      "fuzzy": fuzzy,
                      "view": view,
                      "highlight": highlight,
                      "facets": facets
                      })
    return do(all_flags)


def get_info(query="all"):
    """
    Show useful meta info.
    
    @param query: info to be retrieved, possible_values = ['chapters', 'defaults', 'domains', 'errors', 'arabic_to_english_fields', 'fields_reverse', 'flags', 'help_messages', 'hints', 'information', 'recitations', 'roots', 'surates', 'translations']
    """
    return do({"action": "show", "query": query})
