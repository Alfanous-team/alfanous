""" hint:

    Use `alfanous.search` for searching in Quran verses and translations.
    Use `alfanous.get_info` for getting meta info.
    Use `alfanous.do` method for search, suggestion and get most useful info.
    """

from typing import Dict, Optional, Any

# import Output object
from alfanous.outputs import Raw as _search_engine

# Public alias: users should import Engine from alfanous.api (or alfanous)
# instead of reaching into alfanous.outputs directly.
Engine = _search_engine

DEFAULTS, DOMAINS, HELPMESSAGES = _search_engine.DEFAULTS, _search_engine.DOMAINS, _search_engine.HELPMESSAGES
FLAGS = DEFAULTS["flags"].keys()

from alfanous.outputs import arabic_to_english_fields as _fields

FIELDS_ARABIC = _fields.keys()
FIELDS_ENGLISH = _fields.values()

_R = _search_engine()


# Pivot function for search, suggestion, show info
def do(flags: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a search, suggestion, or info retrieval operation.
    
    @param flags: Dictionary of operation parameters
    @return: Dictionary of results
    """
    return _R.do(flags)


def search(query: str, unit: str = "aya", page: int = 1, sortedby: str = "relevance",
           reverse: bool = False,
           fuzzy: bool = False, fuzzy_maxdist: int = 1, view: str = "normal",
           highlight: str = "bold", flags: Optional[Dict[str, Any]] = None,
           facets: Optional[str] = None, filter: Optional[str] = None,
           timelimit: Optional[float] = 5.0,
           translation: Optional[str] = None,
           lang: Optional[str] = None) -> Dict[str, Any]:
    """
    Search in Quran verses and translations.
    
    @param query: The search query string
    @param unit: Search unit ('aya', 'word', 'translation')
    @param page: Page number for pagination
    @param sortedby: Sort order.  One of:
           - 'score' / 'relevance': rank by Whoosh BM25 relevance (highest score first by default).
           - 'mushaf': traditional Qur'an order (sura then verse number).
           - 'tanzil': revelation chronology order.
           - 'ayalength': verse length in words (shortest first by default).
    @param reverse: Reverse the sort order (default False).  When True, the
           lowest/earliest value comes first (e.g. shortest verse first for
           'ayalength', or least-relevant result first for 'score').
    @param fuzzy: Enable fuzzy search — uses aya_ (exact), aya (normalised/stemmed),
           and Levenshtein distance matching on aya_ac simultaneously
    @param fuzzy_maxdist: Maximum Levenshtein edit distance for fuzzy term matching
           (default 1, only used when fuzzy=True)
    @param view: View mode ('normal', 'minimal', etc.)
    @param highlight: Highlight style ('bold', 'css', etc.)
    @param flags: Additional flags dictionary
    @param facets: Facets to group results by
    @param filter: Filter to apply to results
    @param timelimit: Maximum number of seconds to spend on the search query
           (default 5.0). Pass None to disable the limit.
    @param translation: Translation ID (e.g. 'en.shakir') to include with aya results.
    @param lang: Language code (e.g. 'en', 'fr', 'ar') to retrieve translations by
           language at query time. If both ``translation`` and ``lang`` are given,
           ``translation`` takes precedence.
    @return: Dictionary of search results. Each aya entry includes an optional
           ``translation`` field controlled by the ``translation``/``lang``
           parameters. Use ``translation=en.transliteration`` or ``lang=en``
           to retrieve the English transliteration, and
           ``translation=ar.jalalayn`` or ``lang=ar`` to retrieve a tafsir.
    """
    all_flags = flags if flags is not None else {}
    all_flags.update({"action": "search",
                      "unit": unit,
                      "query": query,
                      "page": page,
                      "sortedby": sortedby,
                      "reverse": reverse,
                      "fuzzy": fuzzy,
                      "fuzzy_maxdist": fuzzy_maxdist,
                      "view": view,
                      "highlight": highlight,
                      "facets": facets,
                      "filter": filter,
                      "timelimit": timelimit,
                      "translation": translation,
                      "lang": lang,
                      })
    return do(all_flags)


def correct_query(query: str, unit: str = "aya",
                  flags: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Return a corrected version of *query* using Whoosh's built-in query
    corrector.

    Compares each term in the parsed query against the index vocabulary and
    replaces unknown terms with the closest known alternative.  When the query
    is already valid (all terms appear in the index) the ``corrected`` value in
    the response is identical to the original input.

    @param query: The raw query string to correct.
    @param unit: Search unit ('aya', 'word', 'translation').  Only 'aya' is
                 currently supported; other units return ``None``.
    @param flags: Additional flags dictionary.
    @return: Dictionary containing ``correct_query`` with sub-keys ``original``
             and ``corrected``, plus the standard ``error`` envelope.
    """
    all_flags = flags if flags is not None else {}
    all_flags.update({"action": "correct_query", "query": query, "unit": unit})
    return do(all_flags)


def suggest_collocations(query: str, unit: str = "aya",
                         flags: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Return adjacency-based collocation suggestions (bigrams and trigrams) for a query.

    Searches the Quranic index for verses containing the query word(s) and
    returns the most frequent adjacent phrases — both two-word bigrams and
    three-word trigrams when they are relevant (appear at least twice).
    Phrases preserve natural Quranic word order.

    Example: querying ``'سميع'`` (all-hearing) may return phrases like
    ``'والله سميع عليم'`` (trigram, 8×), ``'سميع عليم'`` (bigram), and
    ``'سميع بصير'`` (bigram) because these patterns appear directly adjacent
    to سميع in the Quranic text.

    The response also includes standard spelling suggestions under the
    ``'suggest'`` key so callers can obtain both in a single request.

    @param query: The Arabic word or phrase to find collocations for.
    @param unit: Search unit ('aya', 'word', 'translation').
    @param flags: Additional flags dictionary.
    @return: Dictionary containing:
             - ``'collocations'``: mapping of each input word to a list of
               adjacency-based 2- or 3-word phrase strings ordered by
               adjacency frequency.
             - ``'suggest'``: standard spelling suggestions (same as the
               ``suggest`` action).
             - ``'error'``: standard error envelope.
    """
    all_flags = flags if flags is not None else {}
    all_flags.update({"action": "suggest", "query": query, "unit": unit})
    return do(all_flags)


def get_info(query: str = "all") -> Dict[str, Any]:
    """
    Show useful meta info.
    
    @param query: info to be retrieved, possible_values = ['chapters', 'defaults', 'domains', 'errors', 'arabic_to_english_fields', 'fields_reverse', 'flags', 'help_messages', 'hints', 'information', 'recitations', 'roots', 'surates', 'translations', 'keywords']
    @return: Dictionary of information
    """
    return do({"action": "show", "query": query})


def list_values(field: str) -> Dict[str, Any]:
    """
    List all unique indexed values for a given field.

    Useful for discovering the possible values of annotation fields such as
    ``pos``, ``gender``, ``number``, ``person``, ``form``, ``voice``,
    ``state``, ``derivation``, ``aspect``, ``mood``, ``case``, ``root``,
    ``lemma``, etc.

    @param field: The indexed field name to query (e.g. 'pos', 'gender').
    @return: Dictionary with key ``list_values`` containing:
             - ``field``  – the queried field name
             - ``values`` – sorted list of unique values in the index
             - ``count``  – number of values returned
             - ``error``  – (only on failure) human-readable error message
    """
    return do({"action": "list_values", "field": field})
