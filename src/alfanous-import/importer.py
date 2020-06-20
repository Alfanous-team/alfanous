#!/usr/bin/env python2
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
@author: assem
@contact: assem.ch [at] gmail.com
@license: AGPL

'''
import os.path

from zekr_model_reader.main import TranslationModel

from alfanous.Support.whoosh.fields import Schema, STORED, ID, KEYWORD, TEXT, NUMERIC
from alfanous.Support.whoosh.filedb.filestore import FileStorage
from alfanous.Support.whoosh import index 
from alfanous.Support.whoosh.analysis import RegexTokenizer, LowercaseFilter

from alfanous.text_processing import QArabicSymbolsFilter



class QuranicCorpusImporter:

    def __init__( self, QC_PATH = "../../../store/quranic-corpus-morpology.xml", DB = "main.db" ):

        import sqlite3

        print "connecting to database ...",
        maindb = sqlite3.connect( DB )
        cur = maindb.cursor()
        print "OK"

        print "creating tables:"
	cur.execute( """ drop table if exists wordQC""" )
        cur.execute( 
                        """ create table if not exists  wordQC(
                        gid int unique,
                        word_gid int,
                        word_id int,
                        aya_id int,
                        sura_id int,

                        word varchar(25),
                        normalised varchar(25),
                        spelled varchar(25),
                        'order' int,
                        token varchar(25),
                        arabictoken varchar(25),
                        prefixes varchar(25),
                        suffixes varchar(25),


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

                    """ )
        print ">wordQC table ... OK"


        print ">loading Qurany Corpus...",
        from quran_corpus_reader.main import API as QC
        A = QC( source = QC_PATH )
        print ".OK\n"
        IFEXIST = lambda d, attrib: d[attrib].encode( "utf-8" ) if attrib in d else ""
        gid, word_gid = 0, 0
        print ">inserting values of gid...",
        for iteration in A.all_words_generator():
            QASF = QArabicSymbolsFilter( shaping = True, 
                                         tashkil = True, 
                                         spellerrors = False, 
                                         hamza = False, 
                                         uthmani_symbols = True )
            QASF_spelled = QArabicSymbolsFilter( shaping = True, 
                                                 tashkil = True, 
                                                 spellerrors = True, 
                                                 hamza = True, 
                                                 uthmani_symbols = True
                                                 )

            QUERY = lambda d, glob: """insert into wordQC(gid,word_gid,word_id,aya_id,sura_id,'order',token,arabictoken,prefixes, suffixes,type,pos,arabicpos,mood,
                arabicmood, 'case', arabiccase, root ,arabicroot, lemma ,arabiclemma, special, arabicspecial,
                word,normalised,spelled, derivation, form ,gender, person, number,voice, state, aspect) values
                ("%(gid)d","%(word_gid)d","%(word_id)d","%(aya_id)d","%(sura_id)d","%(order)d","%(token)s","%(arabictoken)s", "%(prefixes)s", "%(suffixes)s",  "%(type)s","%(pos)s","%(arabicpos)s","%(mood)s","%(arabicmood)s",
                "%(case)s","%(arabiccase)s","%(root)s","%(arabicroot)s","%(lemma)s","%(arabiclemma)s","%(special)s","%(arabicspecial)s","%(word)s","%(normalised)s","%(spelled)s",
                "%(derivation)s","%(form)s","%(gender)s","%(person)s","%(number)s","%(voice)s","%(state)s","%(aspect)s")""" % {
										    "gid":gid,
										    "word_gid":word_gid,
										    "word_id":iteration["word_id"],
										    "aya_id":iteration["aya_id"],
										    "sura_id":iteration["sura_id"],
										    "order":order,
										    "token":IFEXIST( d, "token" ),
										    "arabictoken":IFEXIST( d, "arabictoken" ),
										    "prefixes":";".join([prefix["arabictoken"] for prefix in glob["prefixes"] ]).encode( "utf-8" ),
										    "suffixes":";".join([suffix["arabictoken"] for suffix in glob["suffixes"] ]).encode( "utf-8" ),
										    "type":IFEXIST( d, "type" ),
										    "pos":IFEXIST( d, "pos" ),
										    "arabicpos":IFEXIST( d, "arabicpos" ),
										    "mood":IFEXIST( d, "mood" ),
										    "arabicmood":IFEXIST( d, "arabicmood" ),
										    "case":IFEXIST( d, "case" ),
										    "arabiccase":IFEXIST( d, "arabiccase" ),
										    "root":IFEXIST( d, "root" ),
										    "arabicroot":IFEXIST( d, "arabicroot" ),
										    "lemma":IFEXIST( d, "lemma" ),
										    "arabiclemma":IFEXIST( d, "arabiclemma" ),
										    "special":IFEXIST( d, "special" ),
										    "arabicspecial":IFEXIST( d, "arabicspecial" ),
										    "word":iteration["word"].encode( "utf-8" ),
										    "normalised":  QASF.normalize_all( iteration["word"] ).encode( "utf-8" ),
										    "spelled": QASF_spelled.normalize_all( iteration["word"] ).encode( "utf-8" ),
										    "derivation":IFEXIST( d, "derivation" ),
										    "form":IFEXIST( d, "form" ),
										    "gender":IFEXIST( d, "gender" ),
										    "person":IFEXIST( d, "person" ),
										    "number":IFEXIST( d, "number" ),
										    "voice":IFEXIST( d, "voice" ),
										    "state":IFEXIST( d, "state" ),
										    "aspect":IFEXIST( d, "aspect" )
										    }
            word_gid += 1
            if word_gid % 1000 == 0:
                print word_gid,
            print("\n")

            order = 0
            for d in iteration["morphology"]["base"]:
                gid += 1
                order += 1
                cur.execute( QUERY( d, iteration["morphology"] ) )

        print("OK")
        maindb.commit()




class ZekrModelsImporter:
    """  Import  translations of quran as Zekr models """
    schema = Schema( 
						gid = NUMERIC( stored = True ),
						id = TEXT( stored = True ),
						text = TEXT( stored = True, analyzer= RegexTokenizer() | LowercaseFilter()  ),
						type = KEYWORD( stored = True ),
						lang = KEYWORD( stored = True ),
						country = KEYWORD( stored = True ),
						author = KEYWORD( stored = True ),
						copyright = STORED,
						binary = STORED
					)

    def __init__( self, pathindex, pathstore ):
        self.pathindex = pathindex
        self.pathstore = pathstore

        if not os.path.exists( pathindex ):
            os.mkdir( pathindex )

        storage = FileStorage( pathindex )
        if not index.exists( storage ):
            self.index = storage.create_index( self.schema )
        else:
            self.index = storage.open_index()



    def test_existence( self, id ):
        """ test existance of all documents of a translation in the index

        @param id: the id of the translation

        """
        searcher = self.index.searcher()
        results = searcher.find( "id", unicode( id ) )
        l = len( results )
        if l == 6236:
            return True
        elif l == 0:
            return False
        else:#partial
            print("\nwarning: the translation (id= %(id)s ) has incomplete documents nb= %(l)d" % {"id": id,"l":l})
            return l

    def index_it( self, doclist ):
        """ index a list of documents """
        try:
            writer = self.index.writer()
            for doc in doclist:
                writer.add_document( gid = doc["gid"], id = doc["id"], text = doc["text"], type = doc["type"], lang = doc["lang"], country = doc["country"], author = doc["author"] )
            print doc['id'], doc['gid']
            writer.commit()
        except Exception as E:
            print(E)



    def load_translationModels( self ):

        for filename in  os.listdir( self.pathstore ):
            try:
                if filename.endswith( ".trans.zip" ):
		    TM = TranslationModel( self.pathstore + filename )
		    props = TM.translation_properties()

		    test = self.test_existence( props["id"] )
		    if not test:
			print "indexing translation (%s)..." % props["id"],
			self.index_it( TM.document_list() )
			print("  OK")
		else:
		    print("ignoring %s.." % filename )
            except Exception as E:
                print E



if __name__ == "__main__":
    QCI = QuranicCorpusImporter()

    #E = ZekrModelsImporter(pathindex="../../indexes/extend/",pathstore="../../store/Translations/")
    #E.load_translationModels()



