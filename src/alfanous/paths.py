import os

ROOT = os.path.dirname(__file__) + "/"
HOME = (os.getenv('USERPROFILE') or os.getenv('HOME') or ".") + "/"
# base paths
ROOT_INDEX = ROOT + "indexes/"
ROOT_CONFIG = ROOT + "configs/"
HOME_CONFIG = HOME + ".alfanous/"
ROOT_RESOURCE = ROOT + "resources/"
# indexes paths
QSE_INDEX = ROOT_INDEX + "main/"
TSE_INDEX = ROOT_INDEX + "extend/"
WSE_INDEX = ROOT_INDEX + "word/"
# resources paths
INFORMATION_FILE = ROOT_RESOURCE + "information.json"
ARABIC_NAMES_FILE = ROOT_RESOURCE + "arabic_names.json"
DERIVATIONS_FILE = ROOT_RESOURCE + "derivations.json"
STANDARD_TO_UTHMANI_FILE = ROOT_RESOURCE + "standard_to_uthmani.json"
STOP_WORDS_FILE = ROOT_RESOURCE + "stop_words.json"
SYNONYMS_FILE = ROOT_RESOURCE + "synonyms.json"
ANTONYMS_FILE = ROOT_RESOURCE + "antonyms.json"
VOCALIZATIONS_FILE = ROOT_RESOURCE + "vocalizations.json"
WORD_PROPS_FILE = ROOT_RESOURCE + "word_props.json"

# configs path suffixes
RECITATIONS_LIST_FILE = ROOT_CONFIG + "recitations.json"
TRANSLATIONS_LIST_FILE = ROOT_CONFIG + "translations.json"
HINTS_FILE = ROOT_CONFIG + "hints.json"
STATS_FILE = HOME_CONFIG + "stats.json"
STATS_REFERENCE_FILE = ROOT_CONFIG + "stats.json"