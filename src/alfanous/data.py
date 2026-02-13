import os
import json

from alfanous import paths



def recitations(path=paths.RECITATIONS_LIST_FILE):
    try:
        myfile = open(path)
    except IOError:
        return {}
    return json.loads(myfile.read()) if myfile else {}


def translations(path=paths.TRANSLATIONS_LIST_FILE):
    try:
        myfile = open(path)
    except IOError:
        return {}
    return json.loads(myfile.read()) if myfile else {}


def hints(path=paths.HINTS_FILE):
    myfile = open(path)
    return json.loads(myfile.read()) if myfile else {}


def stats(path=paths.STATS_FILE, ref_path=paths.STATS_REFERENCE_FILE):
    if os.path.exists(path):
        myfile = open(path)
    else:
        path_dirpart = os.path.dirname(path)
        if not os.path.exists(path_dirpart):
            os.makedirs(path_dirpart)

        ref_file = open(ref_path, "r")
        myfile = open(path, "w+")
        myfile.write(ref_file.read())
        myfile.seek(0)
    return json.loads(myfile.read()) if myfile else {}


def information(path=paths.INFORMATION_FILE):
    myfile = open(path)
    return json.load(myfile) if myfile else {}


def QSE(path=paths.QSE_INDEX):
    from alfanous.engines import QuranicSearchEngine
    return QuranicSearchEngine(path)


def TSE(path=paths.TSE_INDEX):
    from alfanous.engines import TraductionSearchEngine
    return TraductionSearchEngine(path)


def WSE(path=paths.WSE_INDEX):
    from alfanous.engines import WordSearchEngine
    return WordSearchEngine(path)


try:
    arabic_to_english_fields = json.load(open(paths.ARABIC_NAMES_FILE))
except:
    arabic_to_english_fields = {}
try:
    std2uth_words = json.load(open(paths.STANDARD_TO_UTHMANI_FILE))
except:
    std2uth_words = {}
try:
    vocalization_dict = json.load(open(paths.VOCALIZATIONS_FILE))
except:
    vocalization_dict = {}
try:
    syndict = json.load(open(paths.SYNONYMS_FILE))
except:
    syndict = {}
try:
    antdict = json.load(open(paths.ANTONYMS_FILE))
except:
    antdict = {}
try:
    derivedict = json.load(open(paths.DERIVATIONS_FILE))
except:
    derivedict = {"root": []}

try:
    worddict = json.load(open(paths.WORD_PROPS_FILE))
except:
    worddict = {}
