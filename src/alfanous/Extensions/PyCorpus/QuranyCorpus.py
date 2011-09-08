# coding: utf-8

#    Copyright (C) 2009-2010 Assem Chelli <assem.ch@gmail.com>
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

'''

        
HowTo
=====
- parse a morphology line
        
        >>> API.MorphologyParser.parse("fa+ POS:INTG LEM:maA l:P+")
        {'prefixes': [{'token': 'fa', 'type': '--undefined--'}], 'base': [{'lemma': 'maA', 'arabiclemma': u'\u0645\u064e\u0627', 'arabicpos': u'\u062d\u0631\u0641 \u0627\u0633\u062a\u0641\u0647\u0627\u0645', 'type': 'Particles', 'pos': 'Interogative particle'}], 'suffixes': []}
        
        
@author: Assem Chelli
@contact: assem.ch [at] gmail.com
@license: GPL      


@bug: the generated python dict is too big and "perdre(-fr-)" time

@todo: dont load the total XML file,Just Ask! key:XPath
 

'''



import re
import os,sys


import libxml2,xpath
import xml.etree.ElementTree

import pyparsing as pyp
from pyparsing import *

from QuranyCorpusConstantes import *



     
"""                
TO DO:
test_existance
analyzer
"""


        
def TagKeywords(list):
    """a specific pyparsing term to match tages return Keywords 
     """
    res=list[0]
    for item in list[1:]:
        res|=Keyword(item)
    return res

def TagLiterals(list):
    """a specific pyparsing term to match tages return Literals"""
    
    res=list[0]
    for item in list[1:]:
        res|=Literal(item)
    return res





class API:
    """ the api """
    def __init__(self,source="quranic-corpus-morpology.xml"):
        """ init the API based on XMLfile 
   
        @param source: the path of the xml file
        
        """


        self.corpus=xml.etree.ElementTree.parse(source)
                #libxml2.parseFile(source)  
        #print xpath.find('//item', source) 
     
            
        
    class MorphologyParser():
        """ parse the Morphology tags """
        def __init__(self,corpus):
            """"""
            self.corpus=corpus
        @staticmethod               
        def parse_step1(morph):
            """parse the field morphology of qurany corpus
            
            """
            
            
            string="$ "+str(morph).replace("POS:","£ POS:").replace("PRON:","µ PRON:").replace("&lt;", "<").replace("&gt;",">")+" #"
            #regular expressions 
            begin =Keyword('$').suppress() 
            center = Keyword('£').suppress() 
            last =Keyword('µ').suppress()
            end = Keyword('#').suppress()
            skip=SkipTo(end).suppress()
            
            prefix = Word(alphas+"+"+":")
            prefixes= Group(ZeroOrMore(~center+prefix))
            
            genderK=TagKeywords(["M","F"])
            numberK=TagKeywords(["S","D","P"])
            personK=TagKeywords(["1","2","3"])   
            
            genderL=TagLiterals(["M","F"])
            numberL=TagLiterals(["S","D","P"])
            personL=TagLiterals(["1","2","3"])
            
            person_=personL+Optional(genderL)+Optional(numberL)
            gender_=genderL+numberL
            
                            
            
            gen=person_ | gender_ | numberK |genderK 
            pos = "POS:" + Word(alphas)
            lem = "LEM:" + CharsNotIn(" ")
            root = "ROOT:" + CharsNotIn(" ")
            sp = "SP:" + CharsNotIn(" ")
            mood="MOOD:" +  CharsNotIn(" ")
            
            aspect=TagKeywords(["PERF","IMPF","IMPV"]) 
            
            voice=TagKeywords(["ACT","PASS"]) 
            form=TagKeywords(["(I)","(II)","(III)","(IV)","(V)","(VI)","(VII)","(VIII)","(IX)","(X)","(XI)","(XII)"]) 
            verb= aspect  | voice | form 
    
            voc=Keyword("+voc").suppress()
    
            deriv=TagKeywords(["ACT","PCPL","PASS","VN"])
            
            state=TagKeywords(["DEF","INDEF"])
            case=TagKeywords(["NOM","ACC","GEN"])
            nom= case |state 
          
            
            tag= lem | root | sp | mood |gen | verb | deriv |nom | voc | skip
            part=Group(center+pos+ZeroOrMore(~center+ ~last+~end+tag))
            
            base=Group(OneOrMore(~end+~last+part))
            
            pron = "PRON:" + Group(gen)
            suffixes = Group(ZeroOrMore(~end+last+ pron))
        
            all=begin+prefixes+base+suffixes+end
           
            parsed=all.parseString(string)
            
            
            return parsed
        
        @staticmethod       
        def parse_step2(parsedlist):
            """ return a dict """
            Dict={}
            #prefixes
            prefixes=parsedlist[0]
            Dict["prefixes"]=[]
            if prefixes:
                prefixDict={}
                for prefix in prefixes:
                    prefixDict["token"]=PREFIX[prefix][1]
                    prefixDict["arabictoken"]=PREFIX[prefix][0]
                    prefixDict["type"]=InverseClass(PREFIXclass)[prefix][0]
                    Dict["prefixes"].append(prefixDict)
                    
                
            #word base
            parts=parsedlist[1]
            Dict["base"]=[]
            for part in parts:
                partDict={}
                for i in range(len(part)):
                    tag=part[i]
                    if tag[-1]==":":
                        nexttag=part[i+1]
                        if tag=="POS:":
                            partDict["type"]=InverseClass(POSclass)[nexttag][0]
                            partDict["pos"]=POS[nexttag][1]
                            partDict["arabicpos"]=POS[nexttag][0]
                        elif tag=="ROOT:":
                            partDict["root"]=nexttag
                            partDict["arabicroot"]=buck2uni(nexttag)
                        elif tag=="LEM:":
                            partDict["lemma"]=nexttag
                            partDict["arabiclemma"]=buck2uni(nexttag)
                        elif tag=="SP:":
                            partDict["special"]=nexttag
                            partDict["arabicspecial"]=buck2uni(nexttag)
                        elif tag=="MOOD:":
                            partDict["mood"]=VERB[nexttag][1]
                            partDict["arabicmood"]=VERB[nexttag][0]
                        else:
                            print "new tag!! "+tag
                        i+=1
                    else:
                        if tag in PGN:
                            partDict[InverseClass(PGNclass)[tag][0]]=PGN[tag]
                        elif tag in ["ACT","PASS"]:
                            nexttag=part[i+1] if i+1<len(part) else None
                            if  nexttag=="PCPL":
                                partDict[InverseClass(DERIVclass)[tag+" PCPL"][0]]=DERIV[tag+" PCPL"][1]
                                i+=1                  
                        elif tag in VERB:
                            partDict[InverseClass(VERBclass)[tag][0]]=VERB[tag][1]
    
                        elif tag in NOM:
                            arabize=lambda X: "arabicstate" if X=="state" else "arabiccase" 
                            partDict[InverseClass(NOMclass)[tag][0]]=NOM[tag][1]
                            partDict[arabize(InverseClass(NOMclass)[tag][0])]=NOM[tag][0]
                            
                        elif tag=="VN":
                            partDict[InverseClass(DERIVclass)[tag][0]]=DERIV[tag][1]
                          
                        
                            
                            
                Dict["base"].append(partDict)
                
            #suffixes   
            suffixes=parsedlist[2]
            Dict["suffixes"]=[]
            if suffixes:
                for i in range(len(suffixes)):
                    tag=suffixes[i]
                    if tag=="PRON:":
                        pronDict={}
                        Pset=set(PRON["*"])
                        pronprops=suffixes[i+1]
                        for tag in pronprops:
                            if tag in PGN:
                                pronDict[InverseClass(PGNclass)[tag][0]]=PGN[tag]
                                Pset&=PRON[tag]

                        pronDict["arabictoken"]=Pset.pop() if Pset else ""
                        Dict["suffixes"].append(pronDict)
                        
                        

                
            return Dict
    
        @staticmethod
        def parse(string):
                return API.MorphologyParser.parse_step2(API.MorphologyParser.parse_step1(string))
                
        


        
    def unique_words(self):
            """return a dictionary: the keys is word tokens and the values is the properties"""
            D={}
            for chapter in  self.corpus.findall("//chapter"):
                for verse in chapter.findall("verse"):
                    for word in verse.findall("word"):
                        D[word.attrib["token"]]=API.MorphologyParser.parse(word.attrib["morphology"])
            return D
                    
        
    def all_words_generator(self):
            """ 
            Generate words properties ,word by word 
            """
            for chapter in  self.corpus.findall("//chapter"):
                for verse in chapter.findall("verse"):
                    for word in verse.findall("word"):
                        res=word.attrib
                        res["sura_id"]=int(chapter.attrib["number"])
                        res["aya_id"]=int(verse.attrib["number"])
                        res["word_id"]=int(word.attrib["number"])
                        res["word"]=word.attrib["token"]
                        res["morphology"]=API.MorphologyParser.parse(word.attrib["morphology"])
                        yield res
        
        

    
    
    
if __name__=="__main__":
        A=API(source="../../../store/quranic-corpus-morpology.xml") 
        """keys=set()
        for iter in A.all_words_generator():
            keys|=set(iter.keys())
            for i in iter["morphology"]["base"]:
                keys|=set(i.keys())
            for i in iter["morphology"]["prefixes"]:
                keys|=set(i.keys())
            for i in iter["morphology"]["suffixes"]:
                keys|=set(i.keys())
            print keys"""
 
    
        """
        for i in A.unique_words():
             print i
        """
            
        print API.MorphologyParser.parse("fa+ POS:INTG LEM:&lt;maA ROOT:qawol l:P+ ")
        #print A.corpus.findtext("@number=’114’")
                     
            
    