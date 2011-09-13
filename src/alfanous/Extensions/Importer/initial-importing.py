# coding: utf-8



##     Copyright (C) 2009-2012 Assem Chelli <assem.ch [at] gmail.com>

##     This program is free software: you can redistribute it and/or modify
##     it under the terms of the GNU Affero General Public License as published by
##     the Free Software Foundation, either version 3 of the License, or
##     (at your option) any later version.

##     This program is distributed in the hope that it will be useful,
##     but WITHOUT ANY WARRANTY; without even the implied warranty of
##     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##     GNU Affero General Public License for more details.

##     You should have received a copy of the GNU Affero General Public License
##     along with this program.  If not, see <http://www.gnu.org/licenses/>.


'''
Its one time importing system,dont use it else if you are sure what you're doing

@author: Assem Chelli
@contact: assem.ch [at] gmail.com


'''
import re
import sqlite3 as lite
import os
import xlrd
import re
import Misc
import xml.dom.minidom as dom
import pyparsing as pyp
from pyparsing import *
from Indexing import QseDocIndex
from Searching import QReader
from TextProcessing import QArabicSymbolsFilter, unicode_
from Misc import buck2uni

   


word = re.compile(u"[^ ,،]+")
gname = re.compile(u"لله")
letter = re.compile("[^ ]")

def number(pattern, string):
    return len(re.findall(pattern, string))
        

     
    


def import_from_xls(filename=None, sheet="ALL"):
    """extract the data from exel files to dict(lists(tuples))"""
    if filename:
        wb = xlrd.open_workbook(filename)
        if sheet == "ALL":
            results = {}    #:returned value 
            for sh in wb.sheets():
                result = []
                for rownum in range(sh.nrows):
                        result.append(sh.row_values(rownum))    
                results[sh.name] = result;
        else :
            sh = wb.sheet_by_name(sheet)
            result = []
            for rownum in range(sh.nrows):
                result.append(sh.row_values(rownum))    
            results = result
    else : 
        results = None
        print "import_from_xls:no file is selected"
    #
    return results

def fields_existence(list, cursor=None):
    for feild in list:
            print feild, ";",

    
def create_maindb(path="indexes/", name="temp.db"):
        print "test paths  ... ",
        if not os.path.exists(path):
            os.makedirs(path)
        if os.path.exists(path + name):
            """print "\nthe database is already exist!"
            if raw_input("wonna replace it?*/n \n")=="n": 
                pass
            else:""" 
            os.remove(path + name)
        print "connecting to database ...",
        maindb = lite.connect(path + name)
        cur = maindb.cursor()
        print "OK"
        errors = 0
        
        print "creating tables:"
        try:
            cur.execute(
                        """ create table if not exists aya(
                    --global aya id
                         gid int,
                         
                    --sura_aya key    
                         sura_id int,
                         aya_id int,
                       
                         
                    --aya texts
                         standard text ,
                         standard_full text ,
                         uthmani text ,
                         uthmani_min text,
                         
                    --subjects
                         chapter text,
                         topic text,
                         subtopic text ,
                         subject text,
                         
                    --structures
                         rub_gid int ,
                         nisf_gid int ,
                         hizb_gid int ,
                         juz_gid int ,
                         rub_id int ,
                          nisf_id int,
                          hizb_id int,
                         juz_id int ,
                          page_id int,
                          ruku_id int,
                         manzil_id int ,
                         sajda varchar(10),--bool
                         sajda_id int ,
                         sajda_type varchar(10),
                         
                    --sura info
                         sura_name varchar(20),
                         sura_type varchar(30) ,
                          sura_order int,
                         
                         
                    --statistiques
                          sura_ayas_nb int,
                         sura_gnames_nb int ,
                         sura_words_nb int,
                         sura_letters_nb int,
                         sura_rukus_nb int ,
                          aya_gnames_nb int,
                          aya_words_nb int,
                          aya_letters_nb int,
        
                    
                        primary key(gid)
                      unique(sura_id,aya_id)
                    
                    )
        
                    """)
            print ">aya table ... OK"
            print cur.fetchall()
            maindb.commit()
        except lite.OperationalError as OpError:
            print ">aya table ... NOT OK" 
            errors += 1
            print OpError
        
        
        try:
            cur.execute("""create table if not exists word 
                        (-- global word id
                         id int ,
                        
                        --sura_aya_word key
                        --sura_id int,
                        --aya_id int ,
                        --word_id int,
                        
                        
                        --word tokens
                         word varchar(20),

                        uthmani varchar(20) ,
                        
                        --stems
                        lemma varchar(20) ,
                        root varchar(10) ,
                        
                        --class
                        type varchar(50) ,
                        pattern varchar(20) ,            
                        gender varchar(20) ,
                        number varchar(20) ,
                        person varchar(20) ,
                        i3rab varchar(20) ,
                     
                       
                        --affixes
                        prefix varchar(10) ,
                        suffix varchar(20) ,
                        
                        --synonymes
                        synonymes varchar(100) ,
                        
                        --statistiques
                        word_letters_nb  int ,
                        
                        primary key(gid),
                        unique(sura_id,aya_id,word_id)
                         
                         
                         
                         )
                        """)
            print ">word table ... OK"
            maindb.commit()
        
        
        except lite.OperationalError as OpError: 
            print ">word table ... NOT OK"
            errors += 1
            print OpError
        try:
            cur.execute("""create table if not exists field 
                        (
                        id int  ,
                        name varchar(20) ,
                        name_arabic varchar(20) ,
                        table_name varchar(10) ,
                        comment text ,
                        type varchar(20) ,
                        format varchar(20) ,
                        is_indexed int ,--bool
                        is_stored int ,--bool
                        is_spellchecked int ,--bool
                        is_scorable int ,--bool
                        is_unique int ,--bool
                        source varchar(30),
                        source_comment text,
                        revised int,
                        revised_by varchar(30),
                        
                        primary key(id)
                        )
                        """)
            print ">field table ... OK"
  
            maindb.commit()
            print "detecting database tables ...",
            cur.execute("select  name from sqlite_master where type='table'")
            print "OK",
            print ": ", cur.fetchall()
        
        
        except lite.OperationalError as OpError: 
            print ">word table ... OK"
            errors += 1
            print "ERRORS=" + str(OpError)
        
        return errors

def build_aya(_out="indexes/temp.db", _in="in/") :
        """load data form  folder '_in' to the database '_out'""" 
        print "testing paths ...",
        assert  os.path.exists(_out), "the database '" + _out + "' is not exist"
        assert  os.path.exists(_in), "excel directory is not exists'" + _in + "' is not exist"
        print "OK"
        
        print "connecting to database ...",
        maindb = lite.connect(_out)
        cur = maindb.cursor()
        print "OK"
        
        print "detecting database tables ...",
        cur.execute("select  name from sqlite_master where type='table'")
        print "OK",
        print ": ", cur.fetchall()
        
        print "building aya table :"
        print ">inserting values of gid...",
        for gid in range(6236):
            query = "insert into aya(gid) values ('" + str(gid + 1) + "')"
            #print query
            cur.execute(query) 
        print "OK"
        
        #aya.xls
        print ">inserting values of fields list : ",
        res = import_from_xls(_in + "aya/aya.xls", "fanous")
        fields_existence(res[0])
        print "...",
        for i in range(1, len(res)):
            query = "update aya set "
            for j in range(len(res[i])):
                query += "'" + str(res[0][j]) + "'='" + str(res[i][j]) + "' ,"
            
            query = query[:-1]#eliminate the last comma
            query += "where  gid='" + str(i) + "'"
            #print query
            cur.execute(query) 
        print "OK"
        #sura.xls
        print ">inserting values of fields list : ",
        res = import_from_xls(_in + "aya/sura.xls", "fanous")
        fields_existence(res[0][1:])
        print "...",
        for i in range(1, len(res)):
            query = "update aya set "
            for j in range(1, len(res[i])):
                query += "'" + str(res[0][j]) + "'='" + str(res[i][j]) + "' ,"
            
            query = query[:-1]#eliminate the last comma
            query += "where  sura_id=" + str(res[i][0])
            #print query
            cur.execute(query) 
        print "OK"
           
        #manzil.xls
        print ">inserting values of fields list : ",
        res = import_from_xls(_in + "aya/manzil.xls", "fanous")
        fields_existence(res[0][2:])
        print "...",
        for i in range(1, len(res) - 1):
            query = "update aya set "
            for j in range(2, len(res[i])):
                query += "'" + str(res[0][j]) + "'='" + str(res[i][j]) + "' ,"
            
            query = query[:-1]#eliminate the last comma
            query += "where  (sura_id>=" + str(res[i][0]) + " and sura_id<" + str(res[i + 1][0]) + ")"
            #print "\n",query,
            cur.execute(query) 
        print "OK"
         #page.xls
        print ">inserting values of fields list : ",
        res = import_from_xls(_in + "aya/page.xls", "fanous")
        fields_existence(res[0][2:])
        print "...",
        for i in range(1, len(res) - 1):
            query = "update aya set "
            for j in range(2, len(res[i])):
                query += "'" + str(res[0][j]) + "'='" + str(res[i][j]) + "' ,"
            
            query = query[:-1]#eliminate the last comma
            query += "where  (((sura_id>" + str(res[i][0]) + " and sura_id<" + str(res[i + 1][0]) + ") "
            query += " or (sura_id=" + str(res[i][0]) + " and aya_id>=" + str(res[i][1]) + ") "
            query += " or (sura_id=" + str(res[i + 1][0]) + " and aya_id<" + str(res[i + 1][1]) + ") "
            query += "and (" + str(res[i][0]) + "<>" + str(res[i + 1][0]) + "))"
            query += "or ((sura_id=" + str(res[i][0]) + ") and (" + str(res[i][0]) + "=" + str(res[i + 1][0]) + ")"
            query += " and (aya_id>=" + str(res[i][1]) + " and aya_id<" + str(res[i + 1][1]) + ")))"
                 
            #print "\n",query,
            cur.execute(query) 
        print "OK"
         
         #rub.xls
        print ">inserting values of fields list : ",
        res = import_from_xls(_in + "aya/rub.xls", "fanous")
        fields_existence(res[0][2:])
        print "...",
        for i in range(1, len(res) - 1):
            query = "update aya set "
            for j in range(2, len(res[i])):
                query += "'" + str(res[0][j]) + "'='" + str(res[i][j]) + "' ,"
            
            query = query[:-1]#eliminate the last comma
            query += "where  (((sura_id>" + str(res[i][0]) + " and sura_id<" + str(res[i + 1][0]) + ") "
            query += " or (sura_id=" + str(res[i][0]) + " and aya_id>=" + str(res[i][1]) + ") "
            query += " or (sura_id=" + str(res[i + 1][0]) + " and aya_id<" + str(res[i + 1][1]) + ") "
            query += "and (" + str(res[i][0]) + "<>" + str(res[i + 1][0]) + "))"
            query += "or ((sura_id=" + str(res[i][0]) + ") and (" + str(res[i][0]) + "=" + str(res[i + 1][0]) + ")"
            query += " and (aya_id>=" + str(res[i][1]) + " and aya_id<" + str(res[i + 1][1]) + ")))"
                 
            #print "\n",query,
            cur.execute(query) 
        print "OK"
        
         #ruku.xls
        print ">inserting values of fields list : ",
        res = import_from_xls(_in + "aya/ruku.xls", "fanous")
        fields_existence(res[0][2:])
        print "...",
        for i in range(1, len(res) - 1):
            query = "update aya set "
            for j in range(2, len(res[i])):
                query += "'" + str(res[0][j]) + "'='" + str(res[i][j]) + "' ,"
            
            query = query[:-1]#eliminate the last comma
            query += "where  (((sura_id>" + str(res[i][0]) + " and sura_id<" + str(res[i + 1][0]) + ") "
            query += " or (sura_id=" + str(res[i][0]) + " and aya_id>=" + str(res[i][1]) + ") "
            query += " or (sura_id=" + str(res[i + 1][0]) + " and aya_id<" + str(res[i + 1][1]) + ") "
            query += "and (" + str(res[i][0]) + "<>" + str(res[i + 1][0]) + "))"
            query += "or ((sura_id=" + str(res[i][0]) + ") and (" + str(res[i][0]) + "=" + str(res[i + 1][0]) + ")"
            query += " and (aya_id>=" + str(res[i][1]) + " and aya_id<" + str(res[i + 1][1]) + ")))"
                 
            #print "\n",query,
            cur.execute(query) 
        print "OK"
        
        
          #sajda.xls
        print ">inserting values of fields list : ",
        res = import_from_xls(_in + "aya/sajda.xls", "fanous")
        fields_existence(res[0][2:])
        
        print "...",
        #remplir les cases vides
        query = "update aya set sajda='لا'"  
        cur.execute(query)
        #       
        for i in range(1, len(res) - 1):
            query = "update aya set "
            for j in range(2, len(res[i])):
                query += "'" + str(res[0][j]) + "'='" + str(res[i][j]) + "' ,"
            
            query = query[:-1]#eliminate the last comma
            query += "where (sura_id=" + str(res[i][0]) + " and aya_id=" + str(res[i][1]) + ") "           
            #print "\n",query,
            cur.execute(query) 
        print "OK"
     
       
        #subject.xls
        print ">inserting values of fields list : ",
        res = import_from_xls(_in + "aya/subject.xls", "fanous")
        fields_existence(res[0][2:])
        
        print "...",
        #remplir les cases vides
        query = "update aya set "
        for j in range(3, len(res[i])):
            query += "'" + str(res[0][j]) + "'='',"
        query = query[:-1]#eliminate the last comma
        cur.execute(query)
        
        for i in range(1, len(res) - 1):
            query = "update aya set "
            for j in range(3, len(res[i])):
                query += "'" + str(res[0][j]) + "'='" + str(res[i][j]) + "' ,"
            
            query = query[:-1]#eliminate the last comma
            query += "where (sura_id=" + str(res[i][0]) + " and aya_id>=" + str(res[i][1]) + " and aya_id<=" + str(res[i][2]) + " ) "           
            #print "\n",query,
            cur.execute(query) 
        print "OK"
        
        
        
        #calculate statistiques
        print ">calculating statistiques  aya_gnames_nb,aya_words_nb,aya_letters_n ... "
        cur.execute("select gid,standard from aya")
        res = cur.fetchall()
        for row in res:
            gid, aya = row
            query = "update aya set 'aya_gnames_nb'='" + str(number(gname, aya)) + "','aya_words_nb'='" + str(number(word, aya)) + "','aya_letters_nb'='" + str(number(letter, aya)) + "'"
            query += " where gid=" + str(gid)
            #print query
            cur.execute(query)
        cur.execute("select sum(aya_words_nb),sum(sura_words_nb)/114 from aya")
        print cur.fetchall()                
        print "OK"    

 
        print "commit changes for aya table ...",
        maindb.commit()
        print "OK"
        
        
        
        
def build_word(_out="indexes/main.db", _in="in/") :
        """load data form  folder '_in' to the database '_out'""" 
        print "testing paths ...",
        assert  os.path.exists(_out), "the database '" + _out + "' is not exist"
        assert  os.path.exists(_in), "excel directory is not exists'" + _in + "' is not exist"
        print "OK"
        
        print "connecting to database ...",
        maindb = lite.connect(_out)
        cur = maindb.cursor()
        print "OK"
        
        '''
        cur.execute("drop table if exists word")
        cur.execute("""create table if not exists word 
                        (-- global word id
                         id int ,
                        
                        --sura_aya_word key
                        --sura_id int,
                        --aya_id int ,
                        --word_id int,
                        
                        
                        --word tokens
                         word varchar(20),
                         word_ varchar(20),

                        uthmani varchar(20) ,

                        --stems
                        lemma varchar(20) ,
                        root varchar(10) ,
                        
                        --class
                        type varchar(50) ,
                        pattern varchar(20) ,            
                        gender varchar(20) ,
                        number varchar(20) ,
                        person varchar(20) ,
                        i3rab varchar(20) ,
                     
                       
                        --affixes
                        --prefix varchar(10) ,
                        --suffix varchar(20) ,
                        
                        --synonymes
                        --synonymes varchar(100) ,
                        
                        --statistiques
                        --word_letters_nb  int ,
                        
                        primary key(id)
                        --unique(sura_id,aya_id,word_id)
         
                         )
                        """)
        print ">word table ... OK"
        
        
         
        print "building word table :"
        #import qurany corpus
        print ">import fields: word"
        ASF = QArabicSymbolsFilter(shaping=True, tashkil=True, spellerrors=False, hamza=False)
        D = QseDocIndex() 
        R = QReader(D)
        cpt = 0
        for term in R.reader.all_terms():
            if term[0] in ["aya_"]:
                cpt += 1
                print cpt, "::", term[0], ":", term[1]
                query = "insert into word(id,word,word_) values(" + str(cpt) + u",'" + str(term[1]) + "','" + str(ASF.normalize_all(term[1])) + "')"
                cur.execute(query)
        
        print ">import fields uthmani,lemma,root,"
        
        
        
        print ">inserting values of fields list : ",
        res = import_from_xls(_in + "word/qindexZerrouki.xls", "fanous")
        fields_existence(res[0])
        print "...",
        for i in range(1, len(res)):
            query = "update word set "
            for j in range(2, len(res[i])):
                query += u"'" + unicode(res[0][j]) + u"'='" + unicode(res[i][j]) + u"' ,"
            
            query = query[:-1]#eliminate the last comma
            query += u"where word_='" + res[i][1] + "'"
            print query
            cur.execute(query) 
        print "OK"
        
        #if lemma=word_
        print ">inserting values of fields list : ",
        res = import_from_xls(_in + "word/qindexZerrouki.xls", "fanous")
        fields_existence(res[0])
        print "...",
        for i in range(1, len(res)):
            query = "update word set 'uthmani'='" + unicode(res[i][4]) + "', "
            for j in range(3, len(res[i])):
                query += u"'" + unicode(res[0][j]) + u"'='" + unicode(res[i][j]) + u"' ,"
            
            query = query[:-1]#eliminate the last comma
            query += u"where word_='" + res[i][4] + "'"
            print query
            cur.execute(query) 
        print "OK"
        
        '''
        print ">import qurany corpus ... "
                    
        def ext(key, x):
            try:
                return buck2uni(re.compile(key + u":[^ ]+").findall(x)[0][len(key) + 1:])
            except:
                return ""
        #
        
        mushaf = QuranyCorpus(_in + "word/quranic-corpus-morpology.xml")
        gid = 0
        for i in range(1, len(mushaf) + 1):
            for j in range(1, len(mushaf[i]) + 1):
                for k in range(1, len(mushaf[i][j]) + 1):
                    gid += 1
                    print query
                    #cur.execute(query)
                    
                  
        print "OK"  
        
          
        print "commit changes for word table ...",
        maindb.commit()
        print "OK"
        
def load_synonymes(path="in/word/synonymes.xls"):
    """load synonymes"""
    raw = import_from_xls(path, "fanous")
    syn = {}
    for list in raw:
        words = re.findall(word, list[0])
        for w in words:
            syn[w] = words
    return syn
    
    
def create_syn_n_stop(path="indexes/", name="temp.db"):
    print "connecting to database ...",
    maindb = lite.connect(path + name)
    cur = maindb.cursor()
    print "OK"
    cur.execute("create table synonymes(id int primary key,word varchar(15) unique,synonymes varchar(120))")
    cur.execute("create table stopwords(id int primary key,word varchar(10) unique,nb_in_quran int )")

                           
    dictz = load_synonymes()
    cpt = 0
    for key in dictz:
        cpt += 1
        query = "insert into synonymes values('" + unicode(cpt) + "','" + key + "','" + ",".join(dictz[key]) + "')"
        print query
        cur.execute(query)
        
    query = "select * from synonymes"
    cur.execute(query)

 
    from alfanous import QuranicSearchEngine
    QSE = QuranicSearchEngine()
    
    list = QSE.most_frequent_words(50)
    cpt = 0
    for item in list:
        cpt += 1
        query = "insert into stopwords(id,word,nb_in_quran) values('" + unicode(cpt) + "','" + unicode(item[1]) + "','" + unicode(item[0]) + "')"
        print query
        cur.execute(query)
    
    maindb.commit()

def copytomain():
    print "connecting to database ...",
    maindb = lite.connect("indexes/main.db")
    cur1 = maindb.cursor()
    tempdb = lite.connect("indexes/main_temp.db")
    cur2 = tempdb.cursor()
    print "OK"
      
    cur2.execute("select * from word")
    
    print cur2.fetchall()
    
   
    
if __name__ == "__main__":
    #print create_maindb()
    #print build_aya()
    #print build_word()
    #create_syn_n_stop()
    #syn=load_synonymes()
    """
    for k in syn.keys():
        print k,
        """
    '''
    for k in syn[u"صَعَدَ"]:
        print k,
        '''
    #copytomain()
