import os
import json

from alfanous import paths



def recitations(path=paths.RECITATIONS_LIST_FILE):
    try:
        with open(path) as myfile:
            return json.load(myfile)
    except IOError:
        return {}


def translations(path=paths.TRANSLATIONS_LIST_FILE):
    try:
        with open(path) as myfile:
            return json.load(myfile)
    except IOError:
        return {}


def hints(path=paths.HINTS_FILE):
    try:
        with open(path) as myfile:
            return json.load(myfile)
    except IOError:
        return {}


def stats(path=paths.STATS_FILE, ref_path=paths.STATS_REFERENCE_FILE):
    if os.path.exists(path):
        with open(path) as myfile:
            return json.load(myfile)
    else:
        path_dirpart = os.path.dirname(path)
        if not os.path.exists(path_dirpart):
            os.makedirs(path_dirpart)

        with open(ref_path, "r") as ref_file:
            with open(path, "w+") as myfile:
                myfile.write(ref_file.read())
                myfile.seek(0)
                return json.load(myfile)


def information(path=paths.INFORMATION_FILE):
    try:
        with open(path) as myfile:
            return json.load(myfile)
    except IOError:
        return {}


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
    with open(paths.ARABIC_NAMES_FILE) as f:
        arabic_to_english_fields = json.load(f)
except:
    arabic_to_english_fields = {}
try:
    with open(paths.STANDARD_TO_UTHMANI_FILE) as f:
        std2uth_words = json.load(f)
except:
    std2uth_words = {}
try:
    with open(paths.VOCALIZATIONS_FILE) as f:
        vocalization_dict = json.load(f)
except:
    vocalization_dict = {}
try:
    with open(paths.SYNONYMS_FILE) as f:
        syndict = json.load(f)
except:
    syndict = {}
try:
    with open(paths.ANTONYMS_FILE) as f:
        antdict = json.load(f)
except:
    antdict = {}
try:
    with open(paths.DERIVATIONS_FILE) as f:
        derivedict = json.load(f)
except:
    derivedict = {"root": []}

try:
    with open(paths.WORD_PROPS_FILE) as f:
        worddict = json.load(f)
except:
    worddict = {}
