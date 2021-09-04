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

                ":"  : "\\u06DC", # SmallHighSeen
                "@"  : "\\u06DF", # SmallHighRoundedZero
                "\"" : "\\u06E0", # SmallHighUprightRectangularZero
                "["  : "\\u06E2", # SmallHighMeemIsolatedForm
                ";"  : "\\u06E3", # SmallLowSeen
                ","  : "\\u06E5", # SmallWaw
                "."  : "\\u06E6", # SmallYa
                "!"  : "\\u06E8", # SmallHighNoon
                "-"  : "\\u06EA", # EmptyCentreLowStop
                "+"  : "\\u06EB", # EmptyCentreHighStop
                "%"  : "\\u06EC", # RoundedHighStopWithFilledCentre
                "]"  : "\\u06ED"          #

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
"COND":( "حرف شرط", "Conditional particle" ),
"EQ":( "حرف تسوية", "Equalization particle" ),
"EXH":( "حرف تحضيض", "Exhortation particle" ),
"EXL":( "حرف تفصيل", "Explanation particle" ),
"EXP":( "أداة استثناء", "Exceptive particle" ),
"FUT":( "حرف استقبال", "Future particle" ),
"INC":( "حرف ابتداء", "Inceptive particle" ),
"INTG":( "حرف استفهام", "Interogative particle" ),
"NEG":( "حرف نفي", "Negative particle" ),
"PREV":( "حرف كاف", "Preventive particle" ),
"PRO":( "حرف نهي", "Prohibition particle" ),
"REM":( "حرف استئنافية", "Resumption particle" ),
"RES":( "أداة حصر", "Restriction particle" ),
"RET":( "حرف اضراب", "Retraction particle" ),
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
"Particles":["ACC", "AMD", "ANS", "AVR", "CAUS", "CERT", "COND", "EQ", "EXH", "EXL", "EXP", "FUT", "INC", "INTG", "NEG", "PREV", "PRO", "REM", "RES", "RET", "SUP", "SUR", "VOC"],
"Disconnected Letters":["INL"]
}

PREFIXclass = {
"determiner":["Al+"],
"preposition":["bi+", "ka+", "ta+", "l:P+"],
"future particle":["sa+"],
"vocative particle":["ya+", "ha+"],
"interrogative particle":["A:INTG+"],
"equalization particle":["A:EQ+"],
"conjunction":["wa+", "f:CONJ+"],
"resumption":["w:P+"],
"cause":["f:CAUS+"],
"emphasis":["l:EMPH+"],
"purpose":["l:PRP+"],
"imperative":["l:IMPV+"],
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
"fa+":( "ف", "fa" ),
"f:CONJ+":( "ف", "fa" ),
"f:REM+":( "ف", "fa" ),
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
"1":"متكلم",
"2":"مخاطب",
"3":"غائب",
"M":"مذّكر",
"F":"مؤنّث",
"S":"مفرد",
"D":"مثنّى",
"P":"جمع"
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
"(I)":( "", "First form" ),
"(II)" :( "", "Second form" ),
"(III)" :( "", "Third form" ),
"(IV)" :( "", "Fourth form" ),
"(V)" :( "", "Fifth form" ),
"(VI)" :( "", "Sixth form" ),
"(VII)" :( "", "Seventh form" ),
"(VIII)":( "", "Eighth form" ),
"(IX)" :( "", "Ninth form" ),
"(X)" :( "", "Tenth form" ),
"(XI)" :( "", "Eleventh form" ),
"(XII)" :( "", "Twelfth form" )
}

DERIVclass = {
"derivation":["ACT PCPL", "PASS PCPL", "VN"]
}

DERIV = {
"ACT PCPL":( "اسم فاعل", "Active participle" ),
"PASS PCPL":( "اسم مفعول", "Passive participle" ),
"VN":( "مصدر", "Verbal noun" )
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
"*":set( ["ني", "نا", "ك", "كما", "كم", "ه", "هما", "هم", "كن", "ها", "هن"] ),
"1":set( ["ني", "نا"] ),
"2":set( ["ك", "كما", "كم", "كن"] ),
"3":set( ["ه", "ها", "هما", "هم", "هن"] ),
"M":set( ["ني", "نا", "ك", "كما", "كم", "ه", "هما", "هم"] ),
"F":set( ["ني", "نا", "ك", "كما", "كن", "ها", "هما", "هن"] ),
"S":set( ["ني", "ك", "ه", "ها"] ),
"D":set( ["نا", "كما", "هما"] ),
"P":set( ["نا", "كم", "هم", "كن", "هن"] ),
}

