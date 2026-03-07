import json
from functools import lru_cache

from alfanous import paths



@lru_cache(maxsize=1)
def recitations(path=paths.RECITATIONS_LIST_FILE):
    """
    Load recitations metadata from JSON file.
    
    @param path: Path to the recitations JSON file
    @return: Dictionary of recitations or empty dict on error
    """
    try:
        with open(path) as myfile:
            return json.load(myfile)
    except IOError:
        return {}


@lru_cache(maxsize=1)
def translations(path=paths.TRANSLATIONS_LIST_FILE):
    """
    Load translations metadata from JSON file.
    
    @param path: Path to the translations JSON file
    @return: Dictionary of translations or empty dict on error
    """
    try:
        with open(path) as myfile:
            return json.load(myfile)
    except IOError:
        return {}


@lru_cache(maxsize=1)
def information(path=paths.INFORMATION_FILE):
    """
    Load API information from JSON file.
    
    @param path: Path to the information JSON file
    @return: Dictionary of API information or empty dict on error
    """
    try:
        with open(path) as myfile:
            return json.load(myfile)
    except IOError:
        return {}


@lru_cache(maxsize=1)
def ai_query_translation_rules(path=paths.AI_QUERY_TRANSLATION_RULES_FILE):
    """
    Load AI query translation rules from text file.
    
    @param path: Path to the AI query translation rules text file
    @return: Dictionary containing the rules text or empty dict on error
    """
    try:
        with open(path, 'r', encoding='utf-8') as myfile:
            content = myfile.read()
            return {
                "content": content,
                "length": len(content),
                "lines": len(content.split('\n'))
            }
    except IOError:
        return {}


@lru_cache(maxsize=1)
def QSE(path=paths.QSE_INDEX):
    """
    Create a Quranic Search Engine instance.
    
    @param path: Path to the Quranic search index
    @return: QuranicSearchEngine instance
    """
    from alfanous.engines import QuranicSearchEngine
    return QuranicSearchEngine(path)


@lru_cache(maxsize=1)
def quran_unvocalized_words():
    """Return the set of unvocalized words appearing in the Quran.

    Collects all unique ``normalized`` values from word children in the live
    QSE index.  Returns an empty frozenset when the index is unavailable;
    callers should treat an empty set as "filtering unavailable" and fall
    back to all candidates.

    :return: frozenset of unvocalized Quranic word strings
    """
    try:
        _engine = QSE()
        if _engine.OK:
            reader = _engine.qdocindex.get_reader()
            try:
                words = frozenset(
                    t.decode("utf-8") if isinstance(t, bytes) else t
                    for t in reader.lexicon("normalized")
                    if t
                )
            finally:
                reader.close()
            if words:
                return words
    except Exception:
        pass

    return frozenset()


try:
    with open(paths.ARABIC_NAMES_FILE, encoding="utf-8") as f:
        # File format: {search_name: arabic_name}. Reverse so that the
        # runtime mapping is {arabic_name: search_name} for query parsing.
        arabic_to_english_fields = {ar: en for en, ar in json.load(f).items()}
except (IOError, json.JSONDecodeError):
    arabic_to_english_fields = {}
try:
    with open(paths.SYNONYMS_FILE) as f:
        syndict = json.load(f)
except (IOError, json.JSONDecodeError):
    syndict = {}
try:
    with open(paths.ANTONYMS_FILE) as f:
        antdict = json.load(f)
except (IOError, json.JSONDecodeError):
    antdict = {}
