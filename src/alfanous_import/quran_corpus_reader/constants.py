#coding:utf-8

# Arabic morphological constants and MORPHOLOGY_MAPPINGS now live in the
# alfanous runtime package so that they are available without alfanous_import.
# Re-export them from there to keep existing imports working.
from alfanous.morphology import (  # noqa: F401
    POS, POSclass, POSclass_arabic,
    PREFIXclass, PREFIX,
    PGNclass, PGN,
    VERBclass, VERB,
    DERIVclass, DERIV,
    NOMclass, NOM,
    MORPHOLOGY_MAPPINGS,
)

BUCKWALTER2UNICODE = {"'": "\u0621", # hamza-on-the-line
                "|": "\u0622", # madda
                ">": "\u0623", # hamza-on-'alif
                "&": "\u0624", # hamza-on-waaw
                "<": "\u0625", # hamza-under-'alif
                "}": "\u0626", # hamza-on-yaa'
                "A": "\u0627", # bare 'alif
                "b": "\u0628", # baa'
                "p": "\u0629", # taa' marbuuTa
                "t": "\u062A", # taa'
                "v": "\u062B", # thaa'
                "j": "\u062C", # jiim
                "H": "\u062D", # Haa'
                "x": "\u062E", # khaa'
                "d": "\u062F", # daal
                "*": "\u0630", # dhaal
                "r": "\u0631", # raa'
                "z": "\u0632", # zaay
                "s": "\u0633", # siin
                "$": "\u0634", # shiin
                "S": "\u0635", # Saad
                "D": "\u0636", # Daad
                "T": "\u0637", # Taa'
                "Z": "\u0638", # Zaa' (DHaa')
                "E": "\u0639", # cayn
                "g": "\u063A", # ghayn
                "_": "\u0640", # taTwiil
                "f": "\u0641", # faa'
                "q": "\u0642", # qaaf
                "k": "\u0643", # kaaf
                "l": "\u0644", # laam
                "m": "\u0645", # miim
                "n": "\u0646", # nuun
                "h": "\u0647", # haa'
                "w": "\u0648", # waaw
                "Y": "\u0649", # 'alif maqSuura
                "y": "\u064A", # yaa'
                "F": "\u064B", # fatHatayn
                "N": "\u064C", # Dammatayn
                "K": "\u064D", # kasratayn
                "a": "\u064E", # fatHa
                "u": "\u064F", # Damma
                "i": "\u0650", # kasra
                "~": "\u0651", # shaddah
                "o": "\u0652", # sukuun
                "`": "\u0670", # dagger 'alif
                "{": "\u0671", # waSla
                #extended here
                "^": "\u0653", # Maddah
                "#": "\u0654", # HamzaAbove

                ":"  : "\u06DC", # SmallHighSeen
                "@"  : "\u06DF", # SmallHighRoundedZero
                "\"" : "\u06E0", # SmallHighUprightRectangularZero
                "["  : "\u06E2", # SmallHighMeemIsolatedForm
                ";"  : "\u06E3", # SmallLowSeen
                ","  : "\u06E5", # SmallWaw
                "."  : "\u06E6", # SmallYa
                "!"  : "\u06E8", # SmallHighNoon
                "-"  : "\u06EA", # EmptyCentreLowStop
                "+"  : "\u06EB", # EmptyCentreHighStop
                "%"  : "\u06EC", # RoundedHighStopWithFilledCentre
                "]"  : "\u06ED"           #

                }


# Quadriliteral verb form patterns — used when the root has 4 letters.
# The corpus still tags these as (I)–(IV); root length is the discriminator.
VERB_QUAD = {
"(I)":  ( "فَعْلَلَ",     "First form (quadriliteral)" ),
"(II)": ( "تَفَعْلَلَ",   "Second form (quadriliteral)" ),
"(III)":( "إِفْعَنْلَلَ", "Third form (quadriliteral)" ),
"(IV)": ( "إِفْعَلَلَّ",  "Fourth form (quadriliteral)" ),
}

# ---------------------------------------------------------------------------
# Derived nominal patterns — (form_arabic, derivation_arabic) → وزن
# For verbs the pattern is the form itself. For derived nominals the pattern
# depends on both form and derivation type.
# ---------------------------------------------------------------------------
_ACT  = DERIV["ACT PCPL"][0]   # "اسم فاعل"
_PASS = DERIV["PASS PCPL"][0]  # "اسم مفعول"
_VN   = DERIV["VN"][0]         # "مصدر"

NOMINAL_PATTERN = {
# Form I — VN omitted (irregular, varies per verb)
(VERB["(I)"][0],    _ACT):  "فَاعِل",
(VERB["(I)"][0],    _PASS): "مَفْعُول",
# Form II
(VERB["(II)"][0],   _ACT):  "مُفَعِّل",
(VERB["(II)"][0],   _PASS): "مُفَعَّل",
(VERB["(II)"][0],   _VN):   "تَفْعِيل",
# Form III — VN uses فِعَال (verified from corpus: حِسَاب, شِقَاق, etc.)
(VERB["(III)"][0],  _ACT):  "مُفَاعِل",
(VERB["(III)"][0],  _PASS): "مُفَاعَل",
(VERB["(III)"][0],  _VN):   "فِعَال",
# Form IV
(VERB["(IV)"][0],   _ACT):  "مُفْعِل",
(VERB["(IV)"][0],   _PASS): "مُفْعَل",
(VERB["(IV)"][0],   _VN):   "إِفْعَال",
# Form V
(VERB["(V)"][0],    _ACT):  "مُتَفَعِّل",
(VERB["(V)"][0],    _PASS): "مُتَفَعَّل",
(VERB["(V)"][0],    _VN):   "تَفَعُّل",
# Form VI
(VERB["(VI)"][0],   _ACT):  "مُتَفَاعِل",
(VERB["(VI)"][0],   _PASS): "مُتَفَاعَل",
(VERB["(VI)"][0],   _VN):   "تَفَاعُل",
# Form VII
(VERB["(VII)"][0],  _ACT):  "مُنْفَعِل",
(VERB["(VII)"][0],  _VN):   "اِنْفِعَال",
# Form VIII
(VERB["(VIII)"][0], _ACT):  "مُفْتَعِل",
(VERB["(VIII)"][0], _PASS): "مُفْتَعَل",
(VERB["(VIII)"][0], _VN):   "اِفْتِعَال",
# Form IX
(VERB["(IX)"][0],   _ACT):  "مُفْعَلّ",
(VERB["(IX)"][0],   _VN):   "اِفْعِلَال",
# Form X
(VERB["(X)"][0],    _ACT):  "مُسْتَفْعِل",
(VERB["(X)"][0],    _PASS): "مُسْتَفْعَل",
(VERB["(X)"][0],    _VN):   "اِسْتِفْعَال",
}

PRON = {
"*": {"ني", "نا", "ك", "كما", "كم", "ه", "هما", "هم", "كن", "ها", "هن"},
"1": {"ني", "نا"},
"2": {"ك", "كما", "كم", "كن"},
"3": {"ه", "ها", "هما", "هم", "هن"},
"M": {"ني", "نا", "ك", "كما", "كم", "ه", "هما", "هم"},
"F": {"ني", "نا", "ك", "كما", "كن", "ها", "هما", "هن"},
"S": {"ني", "ك", "ه", "ها"},
"D": {"نا", "كما", "هما"},
"P": {"نا", "كم", "هم", "كن", "هن"},
}


# ---------------------------------------------------------------------------
# Inverted class dicts — look up a raw tag → category name
# ---------------------------------------------------------------------------

def _reverse_class(dictionary):
    """Invert a class-mapping dict (values may be plain values or lists)."""
    result = {}
    for key, value in dictionary.items():
        if not isinstance(value, list):
            value = [value]
        for v in value:
            result.setdefault(v, []).append(key)
    return result


_INV_POS = _reverse_class(POSclass)
_INV_PREFIX = _reverse_class(PREFIXclass)


# ---------------------------------------------------------------------------
# Suffix tag → (Arabic, English) mappings
# ---------------------------------------------------------------------------

SUFFIX = {
"+n:EMPH": ( "نون التوكيد", "Emphatic nūn suffix" ),
"+VOC":    ( "حرف نداء", "Vocative suffix" ),
}
