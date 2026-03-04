import json

from alfanous import paths


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