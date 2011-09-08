# coding: utf-8
'''
@author: assem
@contact: assem.ch [at] gmail.com
@license: GPL
@organization: Waiting support 

@to do : Antonymes and Synonymes
@to do : prefixes and suffixes

'''
from alfanous.Support.whoosh.fields import Schema, STORED, ID, KEYWORD, TEXT, NUMERIC
from alfanous.Support.whoosh.filedb.filestore import FileStorage
from alfanous.Support.whoosh import index


import os.path
from alfanous.Extensions.PyZekrModels.Models import TranslationModel

from alfanous.TextProcessing import QArabicSymbolsFilter as ASF
      
class GenericImporter:
    """  generic importer for loading any type of data
    @attention: Not implemented
    """
    pass


class TanzilImporter:
    """ import all info contained in Tanzil 
    @attention: Not implemented
    """
    pass


class QuranicCorpusImporter:
    """ import Quranic Corpus to use in Analyser
    
    @todo: Import derivation levels
    @todo: Import words properties
    
    """
    
    
    def __init__(self,db="main.db"):
        """ make word table """
           
        import sqlite3 
        
        print "connecting to database ...",
        maindb = sqlite3.connect(db)
        cur = maindb.cursor()
        print "OK"
        
        print "creating tables:"

        cur.execute(
                        """ create table if not exists wordQC(
                        gid int,
                        word_gid int,
                        word_id int,
                        aya_id int,
                        sura_id int,
                        
                        word varchar(25),
                        normalised varchar(25),
                        spelled varchar(25),
                        
                        part varchar(25), 
                        'order' int,
                        token varchar(25),
                        arabictoken varchar(25),
                       
                                             
                        pos varchar(25),
                        type varchar(25),
                        arabicpos varchar(25),
                        mood varchar(25),
                        arabicmood varchar(25),
                        'case' varchar(25),
                        arabiccase varchar(25),
                        root varchar(25),
                        arabicroot varchar(25),
                        lemma varchar(25),
                        arabiclemma varchar(25),
                        special varchar(25),
                        arabicspecial varchar(25),

                        derivation varchar(25),
                        form varchar(25),
                        gender varchar(25),
                        person varchar(25),
                        number varchar(25),
                        voice varchar(25),
                        state varchar(25),
                        aspect varchar(25),
                        
                        
                        
    
        
                    
                        primary key(gid)
                    
                    )
        
                    """)
        print ">wordQC table ... OK"


        print ">loading Qurany Corpus...",
        from PyCorpus.QuranyCorpus import API as QC
        A=QC()
        print ".OK\n"
        IFEXIST=lambda dict,attrib: dict[attrib] if dict.has_key(attrib) else ""
        gid,word_gid=0,0
        print ">inserting values of gid...",  
        for iter in A.all_words_generator():
            QUERY=lambda d,part: """insert into wordQC(gid,word_gid,word_id,aya_id,sura_id,'order',token,arabictoken,part,type,pos,arabicpos,mood,
                arabicmood, 'case', arabiccase, root ,arabicroot, lemma ,arabiclemma, special, arabicspecial,
                word,normalised,spelled, derivation, form ,gender, person, number,voice, state, aspect) values ("%d","%d","%d","%d","%d","%d","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s")""" % (gid,word_gid,iter["word_id"],iter["aya_id"],iter["sura_id"],order,IFEXIST(d,"token"),IFEXIST(d,"arabictoken"),part,IFEXIST(d,"type"),IFEXIST(d,"pos"),IFEXIST(d,"arabicpos"),IFEXIST(d,"mood"),
                IFEXIST(d,"arabicmood"),IFEXIST(d,"case"),IFEXIST(d,"arabiccase"),IFEXIST(d,"root"),IFEXIST(d,"arabicroot"),IFEXIST(d,"lemma"),IFEXIST(d,"arabiclemma"),IFEXIST(d,"special"),IFEXIST(d,"arabicspecial"),
                iter["word"],ASF(shaping=True, tashkil=True, spellerrors=False, hamza=False).normalize_all(iter["word"]),ASF(shaping=True, tashkil=True, spellerrors=True, hamza=True).normalize_all(iter["word"]),IFEXIST(d,"derivation"),IFEXIST(d,"form"),IFEXIST(d,"gender"),IFEXIST(d,"person"),IFEXIST(d,"number"),IFEXIST(d,"voice"),IFEXIST(d,"state"),IFEXIST(d,"aspect"))
            word_gid+=1
            print word_gid,"\n" if word_gid % 10 == 0 else "...",
            
            order=0
            for d in iter["morphology"]["prefixes"]:
                gid+=1;
                order+=1
                cur.execute(QUERY(d,u"سابق")) 
            
            order=0
            for d in iter["morphology"]["base"]:
                gid+=1
                order+=1
                q=QUERY(d,u"جذع")
                cur.execute(q) 
            
            order=0
            for d in iter["morphology"]["suffixes"]:
                gid+=1
                order+=1
                cur.execute(QUERY(d,u"لاحق")) 

        print "OK"
        maindb.commit()




class ZekrModelsImporter:
    """  Import  translations of quran as Zekr models """
    schema = Schema(gid=NUMERIC(stored=True), id=TEXT(stored=True), text=TEXT(stored=True), type=KEYWORD(stored=True), lang=KEYWORD(stored=True), country=KEYWORD(stored=True), author=KEYWORD(stored=True), copyright=STORED,binary=STORED)
    
    def __init__(self, pathindex, pathstore="./Store/Traductions/"):
        self.pathindex = pathindex
        self.pathstore = pathstore
        
        if not os.path.exists(pathindex): 
            os.mkdir(pathindex)
        
        storage = FileStorage(pathindex)
        if not index.exists(storage):
            self.index = storage.create_index(self.schema)
        else: 
            self.index = storage.open_index()
            

        
    def test_existence(self, id):
        """ test existance of all documents of a translation in the index 

        @param id: the id of the translation
    
        """
        searcher = self.index.searcher()
        results = searcher.find("id", unicode(id))
        l = len(results)
        if l == 6236:
            return True
        elif l == 0:
            return False
        else:#partial
            print "\nwarning: the translation (id=", id, ") has incomplete documents nb=", l
            return l
    
    def index_it(self, doclist):
        """ index a list of documents """
        try:
            writer = self.index.writer()
            for doc in doclist:
                writer.add_document(gid=doc["gid"], id=doc["id"], text=doc["text"], type=doc["type"], lang=doc["lang"], country=doc["country"], author=doc["author"])
            print doc['id'],doc['gid']
            writer.commit()
        except Exception as E:
            print E

            
    
    def load_translationModels(self):

        for file in  os.listdir(self.pathstore):
            try:
                TM = TranslationModel(self.pathstore + file)
                props = TM.translation_properties()

                test = self.test_existence(props["id"])
                if not test:
                    print "indexing translation (%s)..." % props["id"],
                    self.index_it(TM.document_list())
                    print "  OK"
            except Exception as E:
                print E
                

    
if __name__ == "__main__":
    #QCI=QuranicCorpusImporter()
 
    E = ZekrModelsImporter(pathindex="indexes/extend/")#../indexes/extend/
    E.load_translationModels()
    print "Done"

    
