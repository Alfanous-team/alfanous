# coding: utf-8

##     Copyright (C) 2009-2012 Assem Chelli <assem.ch [at] gmail.com>

##     This program is free software: you can redistribute it and/or modify
##     it under the terms of the GNU Affero General Public License as published
##     by the Free Software Foundation, either version 3 of the License, or
##     (at your option) any later version.

##     This program is distributed in the hope that it will be useful,
##     but WITHOUT ANY WARRANTY; without even the implied warranty of
##     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##     GNU Affero General Public License for more details.

##     You should have received a copy of the GNU Affero General Public License
##     along with this program.  If not, see <http://www.gnu.org/licenses/>.


"""


Summary:
========
Alfanous is a Quranic search engine provides simple and advanced search services
in the diverse information of the Holy Quran and is built on the foundations of 
modern search engines to ensure high stability and high-speed search and we 
aspire to provide the benefits of facilitating the search for the user like highlight,suggestions ...Etc..

Alfanous is a search engine in the Arabic language necessarily and it provides 
the morphological analysis , starting from the extraction of roots and other 
processes different and this will give the user more liberty in the formulation 
of queries,and also increases the accuracy of the research and its 
comprehensiveness.

Alfanous is a programming interface (API) a tool of developers working on 
programs related to the Qur'an and want to take advantage of the search services
 provided by alfanous


Features:
=========
  - Advanced search features
     - Fielded Search 
     - jokers (regular expression) 
     - logical relations
     - Phrase Search
     - Intervals search 
  - Additional Features
     - spelling Suggestions
     - pagination
     - Sorting
     - Highlight
  - Language options 
     - Signification
     - Synonyms and Antonyms (to do)
     - Diacritics 
     - Affixes 
     - Arabic word Root 
     - Verb Conjugaisons
     - Nouns derivations
     - Arabic word type 
     - Arabic word Pattern (to do)
     - Spell Errors :hamza formes,some similar letters
  - Options Qur'anic
     - Search in Uthmani script 
     - Extend the search to all qur'anic sciences (to do)
     - the ability to search using special indexes 
     - Structural options 
     - Statistical Informations 
  - Other
     - Buckwalter query
 


Quick Start:
============

Install
-------
use easy_install to download and install alfanous API
        >>> easy_install alfanous

Examples
--------
to call the api from script
  - import and call it 
        
        >>> from alfanous.main import QuranicSearchEngine
        >>> QSE = QuranicSearchEngine() 
        <__main__.QuranicSearchEngine instance at 0xb77d168c>
        >>> QSE.OK
        True        
    
  - find the results of a query
            
            >>> results,_ =QSE.search_all(u"الحمد")
            >>> for r in results:
            >>>       print r["aya"]
            الحمد لله رب العالمين
    
  - show more information about a result : sura's name, aya's number ...
            
            >>>  for r in results:
            >>>        print r["sura_name"],":",r["aya_id"],":",r["aya_"]
            الفاتحة:2:الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ         
                       
  - find the terms used to search from a query
            
            >>> _,terms =QSE.search_all(u"الحمد")
            >>> print terms
            [("aya",u"الحمد")]
            >>> print ",".join([term[1] for term in list(terms)])
            الحمد
    
  - use the terms to highlight the aya text
            
            >>> Qhighlight(u"الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ", [u"الحمد", u"لله"])
            <span style="color:red;font-size:100.0%"><b>الْحَمْدُ</b></span> <span style="color:green;font-size:100.0%"><b>لِلَّـهِ</b></span> رَبِّ الْعَالَمِينَ

  - get the search time and the number of results
            
            >>> print "time=%f,number=%d" % (results.runtime,len(results))
            time=0.100318,number=160

  - limit the number of results 
           
            >>> results,_ =QSE.search_all(u"الله",limit=10)

  - order the results by a specific order: score,mushaf,tanzil
            
            >>> results,_ =QSE.search_all(u"الله",sortby="mushaf")
            

  - suggest the missed words in query
        
        >>> for key, value in QSE.suggest_all(u" عاصمو ").items():
        >>>    print key, ":", ",".join(value)
        عاصمو : عاصم
       

Advanced Search
---------------
 use  the advanced queries to find exactly the results that you want

                                  
simple search                 
        >>> سماكم

derivation level 1
        >>> >سماكم

derivation level 2            
        >>> >>سماكم

joker ?                       
        >>> ال؟لك

joker *                    
        >>> رسول * الله
  
phrase                     
        >>> "رب العالمين"

spell errors                 
        >>> %المأصدة

relation logic And        
        >>> الصلاة و الزكاة

relation logic AndNot     
        >>> الصلاة أو الزكاة

relation logic AndNot     
        >>> الصلاة وليس الزكاة

Synonyms                 
        >>> ~السعير

Antonyms                 
        >>> #السعير

fielded                 
        >>> سورة:الفاتحة 
        
interval                 
        >>> رقم_السورة:[112 إلى 114]

vocalization
        >>> 'المَلك'
        
word properties            
        >>> {ملك,فعل}
        
        
buckwalter
        >>> fawoqa


Available fields
----------------
Alfanous main index contains lot of info about Qur'an.the search on them is 
available using fielded search feature:
         
        >>> سورة:الفاتحة 

you can use these fields:
 - gid : رقم
aya global id 1 to 6236
 - sura_id : رقم_السورة
sura id 1 to 114
 - aya_id : رقم_الآية
aya id in a specified sura
 - aya : آية
aya text in standard script
 - aya_ : آية_
aya text in standard script vocalized
 - uth_ : عثماني_
aya text in othmani script vocalized
 - chapter : فصل 
the first level of division on subjects
 - topic : فرع 
the second  level of division on subjects
 - subtopic :  باب 
the third level of division on subjects
 - subject : موضوع
the subject tags
 - rub : ربع
Rubu'
 - nisf : نصف
Nisf
 - hizb : حزب
Hezb
 - juz : جزء
Juz'
 - page : صفحة
the page id in Mushaf
 - manzil : منزل
Manzil
 - ruku : ركوع
Ruku'
 - sajda : سجدة
the existance of sajdah (نعم or لا)
 - sajda_id : رقم_السجدة
the number of sajdah 
 - sajda_type : نوع_السجدة
the type of sajdah
 - sura : سورة
the surah
 - sura_type : نوع_السورة
the type of surah
 - sura_order : ترتيب_السورة
the order of tanzil
 - s_a : آ_س
ayas number in sura
 - s_g : ج_س
God name number  in sura
 - s_w : ك_س
words number in sura
 - s_l : ح_س
letters number in sura
 - s_r : ر_س
ruku's number in sura
 - a_g : ج_آ
God name number in aya 
 - a_w : ك_آ
words number in aya
 - a_l : ح_آ
letters number in aya
 


Use in development
==================
the API is divided to these main parties:
 - TextProcessing_ : contains the linguistic analysers of Quran and Arabic...etc.
 - QueryProcessing_ : contains specified query parsers , some linguistic operations and suggestions systems 
 - ResultsProcessing_ : contains the operations on the results (Scoring,Sorting,Pagination,extending,highlight)
 - Crawling_ : its a basic methode to find documents containing quran ayas.needed more development
 - related_ :  contains APIs used to import resources from related projects.these projects are :
     - PyCorpus_ : to import  morphology xmlfile from quranic corpus project
     - PyTanzil_ : to import quran from tanzil project 
     - PyAyaByAya_ : to connect the recitations on the site of VersePyVerse project
     - PyElixirFM_ : to use ElixirFM in python 
 
the API use a *critical* resource which are the index.alfanous project contains 
some indexes :
 - Quran index : its the main index.contains all info about Qur'an:
     - Quranic text in different scripts (standard and uthmani)
     - Structural infos like hizb,juz',rubu',manzil..etc
     - Subjects 
     - Statistical infos like words number in aya,letters number in aya ...
       
 - Extended index: contains the translations and taffassir
 
 
To make your index, you can create it using Whoosh_ . the analysers exist in 
TextProcessing_ if you want to use them in your schema 
 
.. _Whoosh: http://packages.python.org/Whoosh/quickstart.html

@author: Assem Chelli
@contact: assem.ch [at] gmail.com
@license: GPL
@version: 0.1
@organization: Waiting Support





"""
