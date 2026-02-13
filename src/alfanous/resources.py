import json

from alfanous import paths


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