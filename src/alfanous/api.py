""" hint:

    Use `alfanous.search` for searching in Quran verses and translations.
    Use `alfanous.get_info` for getting meta info.
    Use `alfanous.do` method for search, suggestion and get most useful info.
    Use `alfanous.index` to add a new translation zip file to the local index.
    """

from typing import Dict, Optional, Any

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
def do(flags: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a search, suggestion, or info retrieval operation.
    
    @param flags: Dictionary of operation parameters
    @return: Dictionary of results
    """
    return _R.do(flags)


def search(query: str, unit: str = "aya", page: int = 1, sortedby: str = "relevance", 
           fuzzy: bool = False, view: str = "normal", highlight: str = "bold", 
           flags: Optional[Dict[str, Any]] = None, facets: Optional[str] = None, 
           filter: Optional[str] = None) -> Dict[str, Any]:
    """
    Search in Quran verses and translations.
    
    @param query: The search query string
    @param unit: Search unit ('aya', 'word', 'translation')
    @param page: Page number for pagination
    @param sortedby: Sort order ('relevance', 'mushaf', etc.)
    @param fuzzy: Enable fuzzy search
    @param view: View mode ('normal', 'minimal', etc.)
    @param highlight: Highlight style ('bold', 'css', etc.)
    @param flags: Additional flags dictionary
    @param facets: Facets to group results by
    @param filter: Filter to apply to results
    @return: Dictionary of search results
    """
    all_flags = flags if flags is not None else {}
    all_flags.update({"action": "search",
                      "unit": unit,
                      "query": query,
                      "page": page,
                      "sortedby": sortedby,
                      "fuzzy": fuzzy,
                      "view": view,
                      "highlight": highlight,
                      "facets": facets,
                      "filter": filter
                      })
    return do(all_flags)


def get_info(query: str = "all") -> Dict[str, Any]:
    """
    Show useful meta info.
    
    @param query: info to be retrieved, possible_values = ['chapters', 'defaults', 'domains', 'errors', 'arabic_to_english_fields', 'fields_reverse', 'flags', 'help_messages', 'hints', 'information', 'recitations', 'roots', 'surates', 'translations', 'keywords']
    @return: Dictionary of information
    """
    return do({"action": "show", "query": query})


def index(translation_zipfile: str,
          _index_path: Optional[str] = None,
          _translations_list_file: Optional[str] = None) -> bool:
    """
    Index a translation zip file into the local extend index.

    The zip file must be a Zekr-compatible `.trans.zip` file containing a
    ``translation.properties`` descriptor and a verse text file with exactly
    6,236 lines (one per Quranic verse).

    After indexing, ``configs/translations.json`` is updated so that the new
    translation is immediately visible via :func:`get_info` and
    :func:`search`.

    Example::

        import alfanous.api as alfanous
        alfanous.index("/path/to/en.yusufali.trans.zip")

    @param translation_zipfile: Absolute or relative path to the ``.trans.zip`` file.
    @type translation_zipfile: str
    @param _index_path: Override the extend index directory (for testing only).
    @param _translations_list_file: Override the translations config path (for testing only).
    @return: True if the translation was newly indexed, False if it was already present.
    @raises ImportError: If the ``alfanous_import`` package is not installed.
    @raises AssertionError: If the zip file does not contain 6,236 verses.
    """
    try:
        from alfanous_import.importer import ZekrModelsImporter
        from alfanous_import.updater import update_translations_list
    except ImportError:
        raise ImportError(
            "The 'alfanous_import' package is required to index translation files. "
            "Install it from the repository: src/alfanous_import/"
        )

    index_path = _index_path if _index_path is not None else PATHS.TSE_INDEX
    translations_list_file = (
        _translations_list_file if _translations_list_file is not None
        else PATHS.TRANSLATIONS_LIST_FILE
    )

    importer = ZekrModelsImporter(pathindex=index_path, pathstore="")
    newly_indexed = importer.index_single_translation(translation_zipfile)

    if newly_indexed:
        update_translations_list(
            TSE_index=index_path,
            translations_list_file=translations_list_file,
        )

    return newly_indexed
