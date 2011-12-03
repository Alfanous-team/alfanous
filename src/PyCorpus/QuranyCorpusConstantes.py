#coding:utf-8

#    Copyright (C) 2009-2010 Assem Chelli <assem.ch@gmail.com>
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.


"""
@author: Assem Chelli
@contact:  assem.ch [at] gmail.com
@license:  GPL

"""




def InverseClass(dict):
    """ inverse a dictionary """
    newdict={}
    for key,value in dict.iteritems():
        if value.__class__!=list:value=[value]
        for v in value:
            if newdict.has_key(v):
                newdict[v].append(key)
            else: 
                newdict[v]=[key] 
    return newdict


def buck2uni(string):
    """ decode buckwalter """
    result = ""
    for ch in string:
        result += buck2uni_table[ch]
    return result
            
                
#:buckwalter code
buck2uni_table = {"'": u"\u0621", # hamza-on-the-line
                "|": u"\u0622", # madda
                ">": u"\u0623", # hamza-on-'alif
                "&": u"\u0624", # hamza-on-waaw
                "<": u"\u0625", # hamza-under-'alif
                "}": u"\u0626", # hamza-on-yaa'
                "A": u"\u0627", # bare 'alif
                "b": u"\u0628", # baa'
                "p": u"\u0629", # taa' marbuuTa
                "t": u"\u062A", # taa'
                "v": u"\u062B", # thaa'
                "j": u"\u062C", # jiim
                "H": u"\u062D", # Haa'
                "x": u"\u062E", # khaa'
                "d": u"\u062F", # daal
                "*": u"\u0630", # dhaal
                "r": u"\u0631", # raa'
                "z": u"\u0632", # zaay
                "s": u"\u0633", # siin
                "$": u"\u0634", # shiin
                "S": u"\u0635", # Saad
                "D": u"\u0636", # Daad
                "T": u"\u0637", # Taa'
                "Z": u"\u0638", # Zaa' (DHaa')
                "E": u"\u0639", # cayn
                "g": u"\u063A", # ghayn
                "_": u"\u0640", # taTwiil
                "f": u"\u0641", # faa'
                "q": u"\u0642", # qaaf
                "k": u"\u0643", # kaaf
                "l": u"\u0644", # laam
                "m": u"\u0645", # miim
                "n": u"\u0646", # nuun
                "h": u"\u0647", # haa'
                "w": u"\u0648", # waaw
                "Y": u"\u0649", # 'alif maqSuura
                "y": u"\u064A", # yaa'
                "F": u"\u064B", # fatHatayn
                "N": u"\u064C", # Dammatayn
                "K": u"\u064D", # kasratayn
                "a": u"\u064E", # fatHa
                "u": u"\u064F", # Damma
                "i": u"\u0650", # kasra
                "~": u"\u0651", # shaddah
                "o": u"\u0652", # sukuun
                "`": u"\u0670", # dagger 'alif
                "{": u"\u0671", # waSla
                #extended here
                "^": u"\u0653", # Maddah
                "#": u"\u0654", # HamzaAbove
                
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
                "]"  : "\u06ED"          #
               
                }


POS={
"N":(u"اسم","Noun"),
"PN":(u"اسم علم","Proper noun"),
"IMPN":(u"اسم فعل أمر","Imperative verbal noun"),
"PRON":(u"ضمير","Personal pronoun"),
"DEM":(u"اسم اشارة","Demonstrative pronoun"),
"REL":(u"اسم موصول","Relative pronoun"),
"ADJ":(u"صفة","Adjective"),
"NUM":(u"رقم","Number"),
"T":(u"ظرف زمان","Time adverb"),
"LOC":(u"ظرف مكان","Location adverb"),
"V":(u"فعل","Verb"),
"P":(u"حرف جر","Preposition"),
"EMPH":(u"لام التوكيد",	"Emphatic lām prefix"),
"IMPV":(u"لام الامر","Imperative lām prefix"),
"PRP":(u"لام التعليل","Purpose lām prefix"),
"CONJ":(u"حرف عطف","Coordinating conjunction"),
"SUB":(u"حرف مصدري","Subordinating conjunction"),
"ACC":(u"حرف نصب","Accusative particle"),
"AMD":(u"حرف استدراك","Amendment particle"),
"ANS":(u"حرف جواب","Answer particle"),
"AVR":(u"حرف ردع","Aversion particle"),
"CAUS":(u"حرف سببية","Particle of cause"),
"CERT":(u"حرف تحقيق","Particle of certainty"),
"COND":(u"حرف شرط","Conditional particle"),
"EQ":(u"حرف تسوية","Equalization particle"),
"EXH":(u"حرف تحضيض","Exhortation particle"),
"EXL":(u"حرف تفصيل","Explanation particle"),
"EXP":(u"أداة استثناء","Exceptive particle"),
"FUT":(u"حرف استقبال","Future particle"),
"INC":(u"حرف ابتداء","Inceptive particle"),
"INTG":(u"حرف استفهام","Interogative particle"),
"NEG":(u"حرف نفي","Negative particle"),
"PREV":(u"حرف كاف","Preventive particle"),
"PRO":(u"حرف نهي","Prohibition particle"),
"REM":(u"حرف استئنافية","Resumption particle"),
"RES":(u"أداة حصر","Restriction particle"),
"RET":(u"حرف اضراب","Retraction particle"),
"SUP":(u"حرف زائد","Supplemental particle"),
"SUR":(u"حرف فجاءة","Surprise particle"),
"VOC":(u"حرف نداء","Vocative particle"),
"INL":(u"حروف مقطعة","Quranic initials")
}

POSclass={
"Nouns":["N","PN","IMPN"], 	
"Pronouns":["DEM","REL","PRON"], 	
"Nominals":["ADJ","NUM"], 
"Adverbs":["T","LOC"],
"Verbs":["V"], 
"Prepositions":["P"],
"lām Prefixes":["EMPH","IMPV","PRP"],
"Conjunctions":["CONJ","SUB"],
"Particles":["ACC","AMD","ANS","AVR","CAUS","CERT","COND","EQ","EXH","EXL","EXP","FUT","INC","INTG","NEG","PREV","PRO","REM","RES","RET","SUP","SUR","VOC"],
"Disconnected Letters":["INL"]
}

PREFIXclass={
"determiner":["Al+"],
"preposition":["bi+","ka+","ta+","l:P+"],
"future particle":["sa+"],
"vocative particle":["ya+","ha+"],
"interrogative particle":["A:INTG+"],
"equalization particle":["A:EQ+"],
"conjunction":["wa+","f:CONJ+"],
"resumption":["w:P+"],
"cause":["f:CAUS+"],
"emphasis":["l:EMPH+"],
"purpose":["l:PRP+"],
"imperative":["l:IMPV+"],
"--undefined--":["A+","fa+"]
}

PREFIX={
"Al+":("ال","al"),  	
"bi+":("ب","bi"), 	
"ka+":("ك","ka"), 	
"ta+":("ت", "ta"), 	
"sa+":("س", "sa"), 	
"ya+":("يا", "yā"), 	
"ha+":("ها", "hā"), 
"A+":("أ", "alif"), 	
"A:INTG+":("أ", "alif"), 	
"A:EQ+":("أ", "alif"), 	
"wa+":("و", "wa"), 	
"w:P+":("و", "wa"),
"fa+":("ف", "fa"), 	
"f:CONJ+":("ف", "fa"), 
"f:REM+":("ف", "fa"), 	
"f:CAUS+":("ف", "fa"), 	
"l:P+":("ل", "lām"), 	
"l:EMPH+":("ل", "lām"), 	
"l:PRP+":("ل", "lām"), 	
"l:IMPV+":("ل", "lām"), 	
}

PGNclass={
"person":["1","2","3"],
"number":["S","D","P"],
"gender":["M","F"]
} 

PGN={
"1":u"متكلم",
"2":u"مخاطب",
"3":u"غائب",
"M":u"مذّكر",
"F":u"مؤنّث",
"S":u"مفرد",
"D":u"مثنّى",
"P":u"جمع"	
}

VERBclass={
"aspect":["PERF","IMPF","IMPV"], 
"mood":["IND","SUBJ","JUS","ENG"], 
"voice":["ACT","PASS"], 
"form":["(I)","(II)","(III)","(IV)","(V)","(VI)","(VII)","(VIII)","(IX)","(X)","(XI)","(XII)"] 
}

VERB={
"PERF":(u"فعل ماض","Perfect verb"),
"IMPF":(u"فعل مضارع","Imperfect verb"),
"IMPV":(u"فعل أمر","Imperative verb"),
"IND":(u"مرفوع","Indicative mood"),
"SUBJ":(u"منصوب","Subjunctive mood"),
"JUS":(u"مجزوم","Jussive mood"),
"ENG":(u"مؤكد","Energetic mood"),
"ACT":(u"مبني للمعلوم","Active voice"),
"PASS":(u"مبني للمجهول","Passive voice"),
"(I)":(u"","First form"),
"(II)" :(u"","Second form"),
"(III)" :(u"","Third form"),
"(IV)" :(u"","Fourth form"),
"(V)" :(u"","Fifth form"),
"(VI)" :(u"","Sixth form"),
"(VII)" :(u"","Seventh form"),
"(VIII)":(u"","Eighth form"),
"(IX)" :(u"","Ninth form"),
"(X)" :(u"","Tenth form"),
"(XI)" :(u"","Eleventh form"),
"(XII)" :(u"","Twelfth form")
}

DERIVclass={
"derivation":["ACT PCPL","PASS PCPL","VN"]
}

DERIV={
"ACT PCPL":(u"اسم فاعل","Active participle"),
"PASS PCPL":(u"اسم مفعول","Passive participle"),
"VN":(u"مصدر","Verbal noun")
}

NOMclass={
"state":["DEF","INDEF"],
"case":["NOM","ACC","GEN"] 
}

NOM={
"DEF":(u"معرفة","Definite state"),
"INDEF":(u"نكرة","Indefinite state"),
"NOM":(u"مرفوع","Nominative case"),
"ACC":(u"منصوب","Accusative case"),
"GEN":(u"مجرور","Genitive case"),
}



PRON={
"*":set([u"ني",u"نا",u"ك",u"كما",u"كم",u"ه",u"هما",u"هم",u"كن",u"ها",u"هن"]),
"1":set([u"ني",u"نا"]),
"2":set([u"ك",u"كما",u"كم",u"كن"]),
"3":set([u"ه",u"ها",u"هما",u"هم",u"هن"]),
"M":set([u"ني",u"نا",u"ك",u"كما",u"كم",u"ه",u"هما",u"هم"]),
"F":set([u"ني",u"نا",u"ك",u"كما",u"كن",u"ها",u"هما",u"هن"]),
"S":set([u"ني",u"ك",u"ه",u"ها"]),
"D":set([u"نا",u"كما",u"هما"]),
"P":set([u"نا",u"كم",u"هم",u"كن",u"هن"]),   
}

