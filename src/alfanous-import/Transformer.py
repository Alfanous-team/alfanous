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

TODO reorganize the importer module ,keep it free of un-needed resources
'''
import os.path
import re
import operator
import sqlite3 as lite


## attention : these libraries will be pickled in the indexes
from alfanous.Support.whoosh.fields import Schema, STORED, ID, KEYWORD, TEXT, NUMERIC
from alfanous.Support.whoosh.formats import Positions, Frequency
from alfanous.Support.whoosh.filedb.filestore import FileStorage
from alfanous.Support.whoosh.store import LockError
from alfanous.Support.whoosh.spelling import SpellChecker
from alfanous.Support.whoosh import  index


from alfanous.main import QuranicSearchEngine
from alfanous.Indexing import QseDocIndex
from alfanous.TextProcessing import QStandardAnalyzer, QDiacAnalyzer, QArabicSymbolsFilter, QUthmaniDiacAnalyzer, QUthmaniAnalyzer, APermissibleAnalyzer
from alfanous.Exceptions import  Ta7rif
from alfanous.Support.PyArabic.araby import strip_tashkeel
from alfanous.Searching import QReader

nor_ = strip_tashkeel

class FrequencyZ( Frequency ):
    def clean( self ):
        pass


class Transformer:
    """load the data from the main database to create schema and document index

    """

    def __init__( self, ixpath, dypypath, dbpath = "main.db" ):
        if dbpath:
            self.__mainDb = self.__connect( dbpath )
        if not( os.path.exists( ixpath ) ):
            os.makedirs( ixpath )
        self.__storage = FileStorage( ixpath )
        self.__ixpath = ixpath
        self.__dypypath = dypypath
        pass

    def __str__( self ):
        return "< Alfanous.Transformer >"

    def __connect( self, dbpath ):
        return lite.connect( dbpath )

    def change_DB( self, dbpath ):
        return self.__connect( dbpath )

    def __3states( self, str ):
        if str == "yes":return "True"
        elif str == "no":return "False"
        else :return None



    def build_schema( self, tablename ):
        """build schema from field table"""

        print "require list of fields ..."
        cur = self.__mainDb.cursor()
        cur.execute( "select search_name,type,analyser,is_stored,boost,phrase,is_scorable,is_unique,format from field where table_name='" + tablename + "' and is_indexed='yes'" )
        res = cur.fetchall()

        print "processing list found  and building raw schema ..."
        Schema_raw = "Schema("
        for line  in res:

            print line
            search_name = str( line[0] )
            if search_name not in ["", "None"]:
                #1
                Schema_raw += search_name + "="
                #2
                type = str( line[1] ).upper()
                if type == "NONE":type = "STORED"
                Schema_raw += type + "("
                Comma = False
                #3
                analyser = str( line[2] )
                if not( analyser == "None" or analyser == "" ):
                    Schema_raw += "analyzer=" + analyser
                    Comma = True
                #4
                is_stored = self.__3states( str( line[3] ) )
                if is_stored in ["True", "False"]:
                    if Comma == True:Schema_raw += ","
                    Schema_raw += "stored=" + is_stored
                    Comma = True
                #5
                boost = str( line[4] )
                if not( boost == "None" or boost == "" ):
                    if Comma == True:Schema_raw += ","
                    Schema_raw += "field_boost=" + boost
                    Comma = True
                #6
                """phrase=self.__3states(str(line[5]))
                if phrase in ["True","False"]:
                    if Comma==True:Schema_raw+=","
                    Schema_raw+="phrase="+phrase
                    Comma=True"""
                """#7
                is_scorable=self.__3states(str(line[6]))
                if is_scorable in ["True","False"]:
                    if Comma==True:Schema_raw+=","
                    Schema_raw+="scorable="+is_scorable
                    Comma=True"""
                #8
                is_unique = self.__3states( str( line[7] ) )
                if is_unique in ["True", "False"]:
                    if Comma == True:Schema_raw += ","
                    Schema_raw += "unique=" + is_stored
                    Comma = True

                #9
                format = str( line[8] )
                if not( format == "None" or format == "" ):
                    if Comma == True:Schema_raw += ","
                    Schema_raw += "vector=" + format
                    Comma = True

                #last
                Schema_raw += "),"
        else: pass #ignored
        Schema_raw = Schema_raw[:-1] + ")"
        print Schema_raw
        resSchema = None
        exec "resSchema=" + Schema_raw

        #print resSchema
        return resSchema


    def transfer( self, ix, tablename = "aya" ):
        """transfer from database to index"""
        self.__unlock_docindex( ix )
                #print "search fields real names ..."

        schema = ix.schema
        cur = self.__mainDb.cursor()
        seq = []
        for field in schema.field_names():
            seq.append( field )
        query = "select name,search_name from field where search_name IN ('" + "','".join( seq ) + "')"
        cur.execute( query )

        #build dict{search_name:name}  and re-order it
        names_dict = {}
        for line in cur.fetchall():
            names_dict[line[1]] = line[0]

        seq = []
        for field in schema.field_names():
            seq.append( names_dict[field] )



        #print "loading DATA..."
        query = "select " + ",".join( map( lambda x: '"' + x + '"', seq ) ) + " from " + tablename
        #print query
        cur.execute( query )
        Data = cur.fetchall()


        print "writing documents in index (total: %d) ...." % len( Data )
        writer = ix.writer()

        cpt = 0
        for line in Data:
            write_cmd = "writer.add_document("
            i = 0
            for field in schema.field_names():
                f, v = field, line[i]
                if v.__class__ == str: write_cmd += f + "=u\"" + unicode( v ) + "\","
                elif v.__class__ == unicode: write_cmd += f + "=u\"" + unicode( v ) + "\","
                elif v.__class__ == int:write_cmd += f + "=" + unicode( v ) + "," #must change 1 to 0001
                else:pass
                i += 1

            write_cmd = write_cmd[:-1] + ")"
            #print write_cmd
            exec write_cmd
            try: pass
            except: print "ERROR"
            cpt += 1
            if not cpt % 1000:
            	print " - milestone:", cpt, "( %d%% )" % ( cpt * 100 / len( Data ) )
        print "done."
        writer.commit()
        self.__lock_docindex( ix )

    def build_docindex( self, schema, tablename = "aya" ):
        """build document index from aya table"""
        ix = self.__storage.create_index( schema )
        self.transfer( ix, tablename )
        return "OK"

    def update_docindex( self, schema, tablename = "aya" ):
        """update the data in document index
            index schema must have at least an id

            """
        ix = self.__storage.open_index()
        self.__transfer( ix, tablename )
        return "OK"

    def __lock_docindex( self, ix ):
        """ lock index """
        #try:
        #    ix.lock()
        #except LockError as LE:
        #    print LE

    def __unlock_docindex( self, ix ):
        ix = self.__storage.open_index()
        #return ix.unlock()


    dheader = u"""#coding:utf-8\n
    #THIS FILE IS DYNAMIC!! DONT EDIT IT.

    """

    def transfer_stopwords( self ):
        """ load stopwords from database and save them as a list in a dynamic py """

        cur = self.__mainDb.cursor()
        cur.execute( "select word from stopwords" )
        stoplist = "["
        for item in cur.fetchall():
            stoplist += "u'" + unicode( item[0] ) + "',"
        stoplist += "]"
        raw_str = self.dheader + u"\nstoplist=" + stoplist .replace( ",", ",\n" )

        fich = open( self.__dypypath + "stopwords_dyn.py", "w+" )
        fich.write( raw_str.encode( 'utf8' ) )

        return raw_str

    def transfer_std2uth_words( self ):
        """ load a mapping standard:uthmani and save it as a list in a dynamic py """
        cur = self.__mainDb.cursor()
        cur.execute( "select word_,uthmani   from word" )
        standard2uthmani = {}
        for item in cur.fetchall():
            if item[0] != item[1] and item[1]:
		standard2uthmani[item[0]] = item[1]


        raw_str = self.dheader + u"\nstd2uth_words=" + str( standard2uthmani ).replace( ",", ",\n" )

        fich = open( self.__dypypath + "std2uth_dyn.py", "w+" )
        fich.write( raw_str )

        return raw_str

    def transfer_synonymes( self ):
        """ load synonymes from database and save them as a list in a dynamic py """

        cur = self.__mainDb.cursor()
        cur.execute( "select word,synonymes from synonymes" )
        wordregex = re.compile( u"[^ ,،]+" )
        syndict = {}
        for item in cur.fetchall():
            synlist = []
            for w in wordregex.findall( item[1] ):
                synlist.append( nor_( w ) )

            syndict[nor_( item[0] )] = synlist #

        raw_str = self.dheader + u"\nsyndict=" + str( syndict ).replace( ",", ",\n" )

        fich = open( self.__dypypath + "synonymes_dyn.py", "w+" )
        fich.write( raw_str )

        return raw_str

    def transfer_ara2eng_names( self ):
        """ load the arabic names of fields and save the as a dictionary"""

        cur = self.__mainDb.cursor()
        cur.execute( "select name_arabic,search_name from field where table_name='aya'" )
        #wordregex=re.compile(u"[^ ,،]+")
        ara2engdict = {}
        for item in cur.fetchall():
            ara2engdict[item[0]] = item[1]

        raw_str = self.dheader + u"\nara2eng_names=" + str( ara2engdict ).replace( ",", ",\n" )

        fich = open( self.__dypypath + "arabicnames_dyn.py", "w+" )
        fich.write( raw_str )

        return raw_str

    def make_spellerrors_dict( self ):
        """ make the spell errors dictionary
        @deprecated: forget this!
        """

        D = QseDocIndex()
        R = QReader( D )
        nor = QArabicSymbolsFilter( True, True, True, True ).normalize_all
        spell_err = {}
        for term in R.reader.all_terms():
            if term[0] in ["aya"]:
                normalized = nor( term[1] )
                if spell_err.has_key( normalized ):
                    spell_err[normalized].append( term[1] )
                else:
                    spell_err[normalized] = [term[1]]

        #print "\n".join( [unicode( key ) + u":" + ",".join( value ) for key, value in spell_err.items()] )

        raw_str = self.dheader + u"\nspell_err=" + str( spell_err )

        fich = open( self.__dypypath + "spellerrors_dyn.py", "w+" )
        fich.write( raw_str )

    def build_speller( self, indexname = "NO_SPELL", fields = [] ):
        """ build a spellchecker based on specified fields it in storage """
        ayaspeller = SpellChecker( self.__storage, indexname = indexname )
        for field in fields:
            ayaspeller.add_field( self.__storage.open_index(), field )


    def transfer_word_props( self ):
        """ load word props from database and save them as a list in a dynamic py """
        cur = self.__mainDb.cursor()
        props = ["word", "word_", "root", "type"]
        cur.execute( "select " + ",".join( props ) + " from word" )
        worddict = {}
        for prop in props:
            worddict[prop] = []
        for item in cur.fetchall():
            # if one of values is None
            if reduce(operator.and_, map(bool, item),True ):
                i = 0
                for prop in props:
                    worddict[prop].append( item[i] );i += 1

        raw_str = self.dheader + u"\nworddict=" + str( worddict ).replace( ",", ",\n" )

        fich = open( self.__dypypath + "word_props_dyn.py", "w+" )
        fich.write( raw_str )

        return raw_str

    def transfer_derivations( self ):
        """ load word derivations from database and save them as a list in a dynamic py """
        cur = self.__mainDb.cursor()
        levels = ["word_", "lemma", "root"]
        cur.execute( "select " + ",".join( levels ) + " from word" )
        derivedict = {}
        for level in levels:
            derivedict[level] = []

        for item in cur.fetchall():
            i = 0
            for level in levels:
                derivedict[level].append( item[i] );i += 1

        raw_str = self.dheader + u"\nderivedict=" + str( derivedict ).replace( ",", ",\n" )

        fich = open( self.__dypypath + "derivations_dyn.py", "w+" )
        fich.write( raw_str )

        return raw_str

    def transfer_vocalizations( self ):
        """ load indexed vocalized words  from the main index and save them as a list in a dynamic py """
	QSE = QuranicSearchEngine( self.__ixpath )

	if QSE.OK:
		mfw = QSE.most_frequent_words( 9999999, "aya_" )
	else:
		mfw = []

	V = QArabicSymbolsFilter( \
                                shaping = False, \
                                tashkil = True, \
                                spellerrors = False, \
                                hamza = False \
	).normalize_all



        vocalization_dict = {}
        for w in mfw:
            word = w[1]
            if vocalization_dict.has_key( V( word ) ):
                vocalization_dict[V( word )].append( word )
            else:
                vocalization_dict[V( word )] = [word]

        raw_str = self.dheader + u"\nvocalization_dict=" + str( vocalization_dict ).replace( ",", ",\n" )

        fich = open( self.__dypypath + "vocalizations_dyn.py", "w+" )
        fich.write( raw_str )

        return raw_str






if __name__ == "__main__":
    T = Transformer( ixpath = "../../indexes/main/" , dypypath = "../alfanous/dynamic_resources/", dbpath = "../../resources/databases/main.db" )
    #T = Transformer( ixpath = "../../indexes/word/" , dypypath = "../alfanous/dynamic_resources/", dbpath = "../../resources/DB/main.db" )
    #T.transfer_stopwords()
    #T.transfer_synonymes()
    #T.transfer_word_props()
    #T.transfer_derivations()
    T.transfer_vocalizations()
    #T.transfer_ara2eng_names()
    #T.transfer_std2uth_words()
    #T.make_spellerrors_dict()


    #ayaSchema=T.build_schema(tablename='aya')
    #T.build_docindex(ayaSchema)
    #T.build_speller(indexname="AYA_SPELL", fields=["aya"])
    #T.build_speller(indexname="SUBJECT_SPELL", fields=["subject"])

    #wordqcSchema = T.build_schema( tablename = 'wordqc' )
    #T.build_docindex(wordqcSchema,tablename='wordqc')
    #T.build_speller(indexname="WORD_SPELL", fields=["word"])




