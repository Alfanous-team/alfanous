import os
import json

from alfanous import paths



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


def hints(path=paths.HINTS_FILE):
    """
    Load search hints from JSON file.
    
    @param path: Path to the hints JSON file
    @return: Dictionary of hints or empty dict on error
    """
    try:
        with open(path) as myfile:
            return json.load(myfile)
    except IOError:
        return {}


def stats(path=paths.STATS_FILE, ref_path=paths.STATS_REFERENCE_FILE):
    """
    Load statistics data from JSON file, creating from reference if needed.
    
    @param path: Path to the stats JSON file
    @param ref_path: Path to the reference stats file (used if main stats file doesn't exist)
    @return: Dictionary of statistics
    """
    if os.path.exists(path):
        with open(path) as myfile:
            return json.load(myfile)
    else:
        path_dirpart = os.path.dirname(path)
        if not os.path.exists(path_dirpart):
            os.makedirs(path_dirpart)

        with open(ref_path, "r") as ref_file:
            content = ref_file.read()
        
        with open(path, "w") as myfile:
            myfile.write(content)
        
        return json.loads(content)


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


def QSE(path=paths.QSE_INDEX):
    """
    Create a Quranic Search Engine instance.
    
    @param path: Path to the Quranic search index
    @return: QuranicSearchEngine instance
    """
    from alfanous.engines import QuranicSearchEngine
    return QuranicSearchEngine(path)


def TSE(path=paths.TSE_INDEX):
    """
    Create a Translation Search Engine instance.
    
    @param path: Path to the translation search index
    @return: TraductionSearchEngine instance
    """
    from alfanous.engines import TraductionSearchEngine
    return TraductionSearchEngine(path)


def WSE(path=paths.WSE_INDEX):
    """
    Create a Word Search Engine instance.
    
    @param path: Path to the word search index
    @return: WordSearchEngine instance
    """
    from alfanous.engines import WordSearchEngine
    return WordSearchEngine(path)


try:
    with open(paths.ARABIC_NAMES_FILE) as f:
        arabic_to_english_fields = json.load(f)
except (IOError, json.JSONDecodeError):
    arabic_to_english_fields = {}
try:
    with open(paths.STANDARD_TO_UTHMANI_FILE) as f:
        std2uth_words = json.load(f)
except (IOError, json.JSONDecodeError):
    std2uth_words = {}
try:
    with open(paths.VOCALIZATIONS_FILE) as f:
        vocalization_dict = json.load(f)
except (IOError, json.JSONDecodeError):
    vocalization_dict = {}
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
try:
    with open(paths.DERIVATIONS_FILE) as f:
        derivedict = json.load(f)
except (IOError, json.JSONDecodeError):
    derivedict = {"root": []}

try:
    with open(paths.WORD_PROPS_FILE) as f:
        worddict = json.load(f)
except (IOError, json.JSONDecodeError):
    worddict = {}
