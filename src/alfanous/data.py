import os
import json

from alfanous import paths
from alfanous.engines import QuranicSearchEngine, FuzzyQuranicSearchEngine
from alfanous.engines import TraductionSearchEngine, WordSearchEngine


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
    return json.loads(myfile.read()) if myfile else {}


def QSE(path=paths.QSE_INDEX):
    return QuranicSearchEngine(path)


def FQSE(path=paths.QSE_INDEX):
    return FuzzyQuranicSearchEngine(path)


def TSE(path=paths.TSE_INDEX):
    return TraductionSearchEngine(path)


def WSE(path=paths.WSE_INDEX):
    return WordSearchEngine(path)


try:
    from alfanous.dynamic_resources.arabicnames_dyn import ara2eng_names as Fields
except:
    Fields = {}
try:
    from alfanous.dynamic_resources.std2uth_dyn import std2uth_words
except:
    std2uth_words = {}
try:
    from alfanous.dynamic_resources.vocalizations_dyn import vocalization_dict
except:
    vocalization_dict = {}
try:
    from alfanous.dynamic_resources.synonymes_dyn import syndict
except:
    syndict = {}
try:
    from alfanous.dynamic_resources.derivations_dyn import derivedict
except:
    derivedict = {"root": []}