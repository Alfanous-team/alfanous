#coding:utf-8

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


POS = {
"N":( "اسم", "Noun" ),
"PN":( "اسم علم", "Proper noun" ),
"IMPN":( "اسم فعل أمر", "Imperative verbal noun" ),
"PRON":( "ضمير", "Personal pronoun" ),
"DEM":( "اسم اشارة", "Demonstrative pronoun" ),
"REL":( "اسم موصول", "Relative pronoun" ),
"ADJ":( "صفة", "Adjective" ),
"NUM":( "رقم", "Number" ),
"T":( "ظرف زمان", "Time adverb" ),
"LOC":( "ظرف مكان", "Location adverb" ),
"V":( "فعل", "Verb" ),
"P":( "حرف جر", "Preposition" ),
"EMPH":( "لام التوكيد", 	"Emphatic lām prefix" ),
"IMPV":( "لام الامر", "Imperative lām prefix" ),
"PRP":( "لام التعليل", "Purpose lām prefix" ),
"CONJ":( "حرف عطف", "Coordinating conjunction" ),
"SUB":( "حرف مصدري", "Subordinating conjunction" ),
"ACC":( "حرف نصب", "Accusative particle" ),
"AMD":( "حرف استدراك", "Amendment particle" ),
"ANS":( "حرف جواب", "Answer particle" ),
"AVR":( "حرف ردع", "Aversion particle" ),
"CAUS":( "حرف سببية", "Particle of cause" ),
"CERT":( "حرف تحقيق", "Particle of certainty" ),
"CIRC":( "حرف حال", "Circumstantial particle" ),
"COM":( "واو المعية", "Comitative particle" ),
"COND":( "حرف شرط", "Conditional particle" ),
"EQ":( "حرف تسوية", "Equalization particle" ),
"EXH":( "حرف تحضيض", "Exhortation particle" ),
"EXL":( "حرف تفصيل", "Explanation particle" ),
"EXP":( "أداة استثناء", "Exceptive particle" ),
"FUT":( "حرف استقبال", "Future particle" ),
"INC":( "حرف ابتداء", "Inceptive particle" ),
"INT":( "حرف تفسير", "Particle of interpretation" ),
"INTG":( "حرف استفهام", "Interogative particle" ),
"NEG":( "حرف نفي", "Negative particle" ),
"PREV":( "حرف كاف", "Preventive particle" ),
"PRO":( "حرف نهي", "Prohibition particle" ),
"REM":( "حرف استئنافية", "Resumption particle" ),
"RES":( "أداة حصر", "Restriction particle" ),
"RET":( "حرف اضراب", "Retraction particle" ),
"RSLT":( "حرف واقع في جواب الشرط", "Result particle" ),
"SUP":( "حرف زائد", "Supplemental particle" ),
"SUR":( "حرف فجاءة", "Surprise particle" ),
"VOC":( "حرف نداء", "Vocative particle" ),
"INL":( "حروف مقطعة", "Quranic initials" )
}

POSclass = {
"Nouns":["N", "PN", "IMPN"],
"Pronouns":["DEM", "REL", "PRON"],
"Nominals":["ADJ", "NUM"],
"Adverbs":["T", "LOC"],
"Verbs":["V"],
"Prepositions":["P"],
"lām Prefixes":["EMPH", "IMPV", "PRP"],
"Conjunctions":["CONJ", "SUB"],
"Particles":["ACC", "AMD", "ANS", "AVR", "CAUS", "CERT", "CIRC", "COM", "COND", "EQ", "EXH", "EXL", "EXP", "FUT", "INC", "INT", "INTG", "NEG", "PREV", "PRO", "REM", "RES", "RET", "RSLT", "SUP", "SUR", "VOC"],
"Disconnected Letters":["INL"]
}

PREFIXclass = {
"determiner":["Al+"],
"preposition":["bi+", "ka+", "ta+", "l:P+", "w:P+"],
"future particle":["sa+"],
"vocative particle":["ya+", "ha+"],
"interrogative particle":["A:INTG+"],
"equalization particle":["A:EQ+"],
"conjunction":["wa+", "f:CONJ+", "w:CONJ+"],
"resumption":["f:REM+", "w:REM+"],
"cause":["f:CAUS+"],
"emphasis":["l:EMPH+"],
"purpose":["l:PRP+"],
"imperative":["l:IMPV+"],
"circumstantial":["w:CIRC+"],
"supplemental":["f:SUP+", "w:SUP+"],
"comitative":["w:COM+"],
"result":["f:RSLT+"],
"--undefined--":["A+", "fa+"]
}

PREFIX = {
"Al+":( "ال", "al" ),
"bi+":( "ب", "bi" ),
"ka+":( "ك", "ka" ),
"ta+":( "ت", "ta" ),
"sa+":( "س", "sa" ),
"ya+":( "يا", "yā" ),
"ha+":( "ها", "hā" ),
"A+":( "أ", "alif" ),
"A:INTG+":( "أ", "alif" ),
"A:EQ+":( "أ", "alif" ),
"wa+":( "و", "wa" ),
"w:P+":( "و", "wa" ),
"w:CONJ+":( "و", "wa" ),
"w:REM+":( "و", "wa" ),
"w:CIRC+":( "و", "wa" ),
"w:SUP+":( "و", "wa" ),
"w:COM+":( "و", "wa" ),
"fa+":( "ف", "fa" ),
"f:CONJ+":( "ف", "fa" ),
"f:REM+":( "ف", "fa" ),
"f:RSLT+":( "ف", "fa" ),
"f:SUP+":( "ف", "fa" ),
"f:CAUS+":( "ف", "fa" ),
"l:P+":( "ل", "lām" ),
"l:EMPH+":( "ل", "lām" ),
"l:PRP+":( "ل", "lām" ),
"l:IMPV+":( "ل", "lām" ),
}

PGNclass = {
"person":["1", "2", "3"],
"number":["S", "D", "P"],
"gender":["M", "F"]
}

PGN = {
"1":( "المتكلم", "first person" ),
"2":( "المخاطب", "second person" ),
"3":( "الغائب", "third person" ),
"M":( "مذكر", "masculine" ),
"F":( "مؤنث", "feminine" ),
"S":( "مفرد", "singular" ),
"D":( "مثنى", "dual" ),
"P":( "جمع", "plural" ),
}

VERBclass = {
"aspect":["PERF", "IMPF", "IMPV"],
"mood":["IND", "SUBJ", "JUS", "ENG"],
"voice":["ACT", "PASS"],
"form":["(I)", "(II)", "(III)", "(IV)", "(V)", "(VI)", "(VII)", "(VIII)", "(IX)", "(X)", "(XI)", "(XII)"]
}

VERB = {
"PERF":( "فعل ماض", "Perfect verb" ),
"IMPF":( "فعل مضارع", "Imperfect verb" ),
"IMPV":( "فعل أمر", "Imperative verb" ),
"IND":( "مرفوع", "Indicative mood" ),
"SUBJ":( "منصوب", "Subjunctive mood" ),
"JUS":( "مجزوم", "Jussive mood" ),
"ENG":( "مؤكد", "Energetic mood" ),
"ACT":( "مبني للمعلوم", "Active voice" ),
"PASS":( "مبني للمجهول", "Passive voice" ),
"(I)":   ( "فَعَلَ",       "First form" ),
"(II)":  ( "فَعَّلَ",      "Second form" ),
"(III)": ( "فَاعَلَ",      "Third form" ),
"(IV)":  ( "أَفْعَلَ",     "Fourth form" ),
"(V)":   ( "تَفَعَّلَ",    "Fifth form" ),
"(VI)":  ( "تَفَاعَلَ",    "Sixth form" ),
"(VII)": ( "إِنْفَعَلَ",   "Seventh form" ),
"(VIII)":( "إِفْتَعَلَ",   "Eighth form" ),
"(IX)":  ( "إِفْعَلَّ",    "Ninth form" ),
"(X)":   ( "إِسْتَفْعَلَ", "Tenth form" ),
"(XI)":  ( "إِفْعَالَّ",   "Eleventh form" ),
"(XII)": ( "إِفْعَوْعَلَ", "Twelfth form" ),
}

# Quadriliteral verb form patterns — used when the root has 4 letters.
# The corpus still tags these as (I)–(IV); root length is the discriminator.
VERB_QUAD = {
"(I)":  ( "فَعْلَلَ",     "First form (quadriliteral)" ),
"(II)": ( "تَفَعْلَلَ",   "Second form (quadriliteral)" ),
"(III)":( "إِفْعَنْلَلَ", "Third form (quadriliteral)" ),
"(IV)": ( "إِفْعَلَلَّ",  "Fourth form (quadriliteral)" ),
}

DERIVclass = {
"derivation":["ACT PCPL", "PASS PCPL", "VN"]
}

DERIV = {
"ACT PCPL":( "اسم فاعل", "Active participle" ),
"PASS PCPL":( "اسم مفعول", "Passive participle" ),
"VN":( "مصدر", "Verbal noun" )
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

NOMclass = {
"state":["DEF", "INDEF"],
"case":["NOM", "ACC", "GEN"]
}

NOM = {
"DEF":( "معرفة", "Definite state" ),
"INDEF":( "نكرة", "Indefinite state" ),
"NOM":( "مرفوع", "Nominative case" ),
"ACC":( "منصوب", "Accusative case" ),
"GEN":( "مجرور", "Genitive case" ),
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


# ---------------------------------------------------------------------------
# MORPHOLOGY_MAPPINGS — Arabic→English for every morphological field.
# Exposed through the API's ``show?query=morphology_mappings`` endpoint so
# that consumers can translate Arabic values without hard-coding them.
# ---------------------------------------------------------------------------

def _ar_to_en(d):
    """Build {Arabic: English} from a dict whose values are (Arabic, English) tuples."""
    return {v[0]: v[1] for v in d.values()}


MORPHOLOGY_MAPPINGS = {
    "pos":        _ar_to_en(POS),
    "gender":     _ar_to_en(PGN),           # subset filtered below
    "number":     _ar_to_en(PGN),
    "person":     _ar_to_en(PGN),
    "form":       _ar_to_en(VERB),
    "voice":      _ar_to_en(VERB),
    "aspect":     _ar_to_en(VERB),
    "mood":       _ar_to_en(VERB),
    "case":       _ar_to_en(NOM),
    "state":      _ar_to_en(NOM),
    "derivation": _ar_to_en(DERIV),
    "prefix":     _ar_to_en(PREFIX),
}
# Narrow per-field mappings to only the values that actually appear for that field.
MORPHOLOGY_MAPPINGS["gender"] = {PGN[k][0]: PGN[k][1] for k in PGNclass["gender"]}
MORPHOLOGY_MAPPINGS["number"] = {PGN[k][0]: PGN[k][1] for k in PGNclass["number"]}
MORPHOLOGY_MAPPINGS["person"] = {PGN[k][0]: PGN[k][1] for k in PGNclass["person"]}
MORPHOLOGY_MAPPINGS["form"]   = {VERB[k][0]: VERB[k][1] for k in VERBclass["form"]}
MORPHOLOGY_MAPPINGS["voice"]  = {VERB[k][0]: VERB[k][1] for k in VERBclass["voice"]}
MORPHOLOGY_MAPPINGS["aspect"] = {VERB[k][0]: VERB[k][1] for k in VERBclass["aspect"]}
MORPHOLOGY_MAPPINGS["mood"]   = {VERB[k][0]: VERB[k][1] for k in VERBclass["mood"]}
MORPHOLOGY_MAPPINGS["case"]   = {NOM[k][0]: NOM[k][1]   for k in NOMclass["case"]}
MORPHOLOGY_MAPPINGS["state"]  = {NOM[k][0]: NOM[k][1]   for k in NOMclass["state"]}

