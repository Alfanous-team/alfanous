# coding: utf-8
"""Arabic morphological constants and label mappings for the Quranic corpus.

These constants encode the annotation scheme used by the Quranic Arabic
Corpus (corpus.quran.com).  They are kept here (in the ``alfanous`` runtime
package) so that API consumers do not need the ``alfanous_import`` resource-
management package installed at runtime.

``alfanous_import`` re-imports these constants from this module to maintain a
single source of truth.
"""

POS = {
    "N":    ("اسم",                        "Noun"),
    "PN":   ("اسم علم",                    "Proper noun"),
    "IMPN": ("اسم فعل أمر",               "Imperative verbal noun"),
    "PRON": ("ضمير",                       "Personal pronoun"),
    "DEM":  ("اسم اشارة",                  "Demonstrative pronoun"),
    "REL":  ("اسم موصول",                  "Relative pronoun"),
    "ADJ":  ("صفة",                        "Adjective"),
    "NUM":  ("رقم",                        "Number"),
    "T":    ("ظرف زمان",                   "Time adverb"),
    "LOC":  ("ظرف مكان",                   "Location adverb"),
    "V":    ("فعل",                        "Verb"),
    "P":    ("حرف جر",                     "Preposition"),
    "EMPH": ("لام التوكيد",                "Emphatic lām prefix"),
    "IMPV": ("لام الامر",                  "Imperative lām prefix"),
    "PRP":  ("لام التعليل",               "Purpose lām prefix"),
    "CONJ": ("حرف عطف",                    "Coordinating conjunction"),
    "SUB":  ("حرف مصدري",                  "Subordinating conjunction"),
    "ACC":  ("حرف نصب",                    "Accusative particle"),
    "AMD":  ("حرف استدراك",                "Amendment particle"),
    "ANS":  ("حرف جواب",                   "Answer particle"),
    "AVR":  ("حرف ردع",                    "Aversion particle"),
    "CAUS": ("حرف سببية",                  "Particle of cause"),
    "CERT": ("حرف تحقيق",                  "Particle of certainty"),
    "CIRC": ("حرف حال",                    "Circumstantial particle"),
    "COM":  ("واو المعية",                  "Comitative particle"),
    "COND": ("حرف شرط",                    "Conditional particle"),
    "EQ":   ("حرف تسوية",                  "Equalization particle"),
    "EXH":  ("حرف تحضيض",                 "Exhortation particle"),
    "EXL":  ("حرف تفصيل",                  "Explanation particle"),
    "EXP":  ("أداة استثناء",              "Exceptive particle"),
    "FUT":  ("حرف استقبال",               "Future particle"),
    "INC":  ("حرف ابتداء",                "Inceptive particle"),
    "INT":  ("حرف تفسير",                  "Particle of interpretation"),
    "INTG": ("حرف استفهام",               "Interogative particle"),
    "NEG":  ("حرف نفي",                   "Negative particle"),
    "PREV": ("حرف كاف",                    "Preventive particle"),
    "PRO":  ("حرف نهي",                    "Prohibition particle"),
    "REM":  ("حرف استئنافية",             "Resumption particle"),
    "RES":  ("أداة حصر",                  "Restriction particle"),
    "RET":  ("حرف اضراب",                 "Retraction particle"),
    "RSLT": ("حرف واقع في جواب الشرط",   "Result particle"),
    "SUP":  ("حرف زائد",                  "Supplemental particle"),
    "SUR":  ("حرف فجاءة",                 "Surprise particle"),
    "VOC":  ("حرف نداء",                  "Vocative particle"),
    "INL":  ("حروف مقطعة",               "Quranic initials"),
}

POSclass = {
    "Nouns":               ["N", "PN", "IMPN"],
    "Pronouns":            ["DEM", "REL", "PRON"],
    "Nominals":            ["ADJ", "NUM"],
    "Adverbs":             ["T", "LOC"],
    "Verbs":               ["V"],
    "Prepositions":        ["P"],
    "lām Prefixes":        ["EMPH", "IMPV", "PRP"],
    "Conjunctions":        ["CONJ", "SUB"],
    "Particles":           ["ACC", "AMD", "ANS", "AVR", "CAUS", "CERT", "CIRC",
                            "COM", "COND", "EQ", "EXH", "EXL", "EXP", "FUT",
                            "INC", "INT", "INTG", "NEG", "PREV", "PRO", "REM",
                            "RES", "RET", "RSLT", "SUP", "SUR", "VOC"],
    "Disconnected Letters": ["INL"],
}

PREFIXclass = {
    "determiner":          ["Al+"],
    "preposition":         ["bi+", "ka+", "ta+", "l:P+", "w:P+"],
    "future particle":     ["sa+"],
    "vocative particle":   ["ya+", "ha+"],
    "interrogative particle": ["A:INTG+"],
    "equalization particle":  ["A:EQ+"],
    "conjunction":         ["wa+", "f:CONJ+", "w:CONJ+"],
    "resumption":          ["f:REM+", "w:REM+"],
    "cause":               ["f:CAUS+"],
    "emphasis":            ["l:EMPH+"],
    "purpose":             ["l:PRP+"],
    "imperative":          ["l:IMPV+"],
    "circumstantial":      ["w:CIRC+"],
    "supplemental":        ["f:SUP+", "w:SUP+"],
    "comitative":          ["w:COM+"],
    "result":              ["f:RSLT+"],
    "--undefined--":       ["A+", "fa+"],
}

PREFIX = {
    "Al+":    ("ال",  "al"),
    "bi+":    ("ب",   "bi"),
    "ka+":    ("ك",   "ka"),
    "ta+":    ("ت",   "ta"),
    "sa+":    ("س",   "sa"),
    "ya+":    ("يا",  "yā"),
    "ha+":    ("ها",  "hā"),
    "A+":     ("أ",   "alif"),
    "A:INTG+":("أ",   "alif"),
    "A:EQ+":  ("أ",   "alif"),
    "wa+":    ("و",   "wa"),
    "w:P+":   ("و",   "wa"),
    "w:CONJ+":("و",   "wa"),
    "w:REM+": ("و",   "wa"),
    "w:CIRC+":("و",   "wa"),
    "w:SUP+": ("و",   "wa"),
    "w:COM+": ("و",   "wa"),
    "fa+":    ("ف",   "fa"),
    "f:CONJ+":("ف",   "fa"),
    "f:REM+": ("ف",   "fa"),
    "f:RSLT+":("ف",   "fa"),
    "f:SUP+": ("ف",   "fa"),
    "f:CAUS+":("ف",   "fa"),
    "l:P+":   ("ل",   "lām"),
    "l:EMPH+":("ل",   "lām"),
    "l:PRP+": ("ل",   "lām"),
    "l:IMPV+":("ل",   "lām"),
}

PGNclass = {
    "person": ["1", "2", "3"],
    "number": ["S", "D", "P"],
    "gender": ["M", "F"],
}

PGN = {
    "1": ("المتكلم", "first person"),
    "2": ("المخاطب", "second person"),
    "3": ("الغائب",  "third person"),
    "M": ("مذكر",    "masculine"),
    "F": ("مؤنث",    "feminine"),
    "S": ("مفرد",    "singular"),
    "D": ("مثنى",    "dual"),
    "P": ("جمع",     "plural"),
}

VERBclass = {
    "aspect": ["PERF", "IMPF", "IMPV"],
    "mood":   ["IND", "SUBJ", "JUS", "ENG"],
    "voice":  ["ACT", "PASS"],
    "form":   ["(I)", "(II)", "(III)", "(IV)", "(V)", "(VI)",
               "(VII)", "(VIII)", "(IX)", "(X)", "(XI)", "(XII)"],
}

VERB = {
    "PERF":  ("فعل ماض",       "Perfect verb"),
    "IMPF":  ("فعل مضارع",     "Imperfect verb"),
    "IMPV":  ("فعل أمر",       "Imperative verb"),
    "IND":   ("مرفوع",         "Indicative mood"),
    "SUBJ":  ("منصوب",         "Subjunctive mood"),
    "JUS":   ("مجزوم",         "Jussive mood"),
    "ENG":   ("مؤكد",          "Energetic mood"),
    "ACT":   ("مبني للمعلوم",  "Active voice"),
    "PASS":  ("مبني للمجهول", "Passive voice"),
    "(I)":   ("فَعَلَ",         "First form"),
    "(II)":  ("فَعَّلَ",        "Second form"),
    "(III)": ("فَاعَلَ",        "Third form"),
    "(IV)":  ("أَفْعَلَ",       "Fourth form"),
    "(V)":   ("تَفَعَّلَ",      "Fifth form"),
    "(VI)":  ("تَفَاعَلَ",      "Sixth form"),
    "(VII)": ("إِنْفَعَلَ",     "Seventh form"),
    "(VIII)":("إِفْتَعَلَ",     "Eighth form"),
    "(IX)":  ("إِفْعَلَّ",      "Ninth form"),
    "(X)":   ("إِسْتَفْعَلَ",   "Tenth form"),
    "(XI)":  ("إِفْعَالَّ",     "Eleventh form"),
    "(XII)": ("إِفْعَوْعَلَ",   "Twelfth form"),
}

DERIVclass = {
    "derivation": ["ACT PCPL", "PASS PCPL", "VN"],
}

DERIV = {
    "ACT PCPL": ("اسم فاعل",  "Active participle"),
    "PASS PCPL":("اسم مفعول", "Passive participle"),
    "VN":       ("مصدر",      "Verbal noun"),
}

NOMclass = {
    "state": ["DEF", "INDEF"],
    "case":  ["NOM", "ACC", "GEN"],
}

NOM = {
    "DEF":   ("معرفة",  "Definite state"),
    "INDEF": ("نكرة",   "Indefinite state"),
    "NOM":   ("مرفوع",  "Nominative case"),
    "ACC":   ("منصوب",  "Accusative case"),
    "GEN":   ("مجرور",  "Genitive case"),
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
