#!/usr/bin/env python2
# coding: utf-8


from importer import *
from transformer import *
from updater import *


from optparse import OptionParser, OptionGroup

usage = "usage: %prog [options]  SOURCE_PATH DESTINATION_PATH "
parser = OptionParser( usage = usage, version = "Alfanous 0.4 - Importer" )

commands = OptionGroup( parser, "Options", "Choose what to do:  " )

commands.add_option( "-x", "--index", dest = "index", type = "choice", choices = ["main", "extend" , "word"],
                  help = "create  indexes", metavar = "TYPE" )

commands.add_option( "-t", "--transfer", dest = "transfer", type = "choice", choices = ["stopwords", "synonyms", "word_props", "derivations", "vocalizations", "ara2eng_names", "std2uth_words"],
                  help = "transfer from database to dynamic resources", metavar = "RESOURCE" )

commands.add_option( "-p", "--speller", dest = "speller", type = "choice", choices = ["aya", "subject", "word"],
                  help = "build a speller for a field", metavar = "FIELD" )

commands.add_option( "-d", "--download", dest = "download", type = "choice", choices = ["tanzil_simple_clean", "tanzil_uthmani"],
                  help = "download Quranic resources", metavar = "FIELD" )

commands.add_option( "-u", "--update", dest = "update", type = "choice", choices = ["translations", "wordqc"],
                  help = "update store information files", metavar = "FIELD" )


parser.add_option_group( commands )


parser.set_defaults( help = True )

( options, args ) = parser.parse_args()


if ( options.index and options.transfer ) or  ( options.index and options.speller ) or ( options.speller and options.transfer ):
        parser.error( "-x , -t  and -p  are exclusives!" )


if options.index:
    if len( args ) == 2:
        SOURCE = args[0]
        DESTINATION = args[1]
    else:
        parser.error( "Choose SOURCE_PATH and DISTINATION_PATH" )

    if options.index == "main":
        T = Transformer( ixpath = DESTINATION , dypypath = None, dbpath = SOURCE )
        ayaSchema = T.build_schema( tablename = 'aya' )
        T.build_docindex( ayaSchema )

    elif options.index == "extend":
        E = ZekrModelsImporter( pathindex = DESTINATION, pathstore = SOURCE )
        E.load_translationModels()

    elif options.index == "word" :
        T = Transformer( ixpath = DESTINATION , dypypath = None, dbpath = SOURCE )
        wordqcSchema = T.build_schema( tablename = 'wordqc' )
	T.build_docindex( wordqcSchema, tablename = 'wordqc' )


if options.transfer:

    if len( args ) == 2:
        SOURCE = args[0]
	SOURCE2 = "." # Secondary source, used for main index path
        DESTINATION = args[1]
    elif len( args ) == 3:
        SOURCE = args[0]
	SOURCE2 = args[1] # Secondary source, used for main index path
        DESTINATION = args[2]
    else:
        parser.error( "Choose SOURCE_PATH and DISTINATION_PATH" )

    T = Transformer( ixpath = SOURCE2 , dypypath = DESTINATION, dbpath = SOURCE )
    if options.transfer == "stopwords":
        T.transfer_stopwords()
    elif options.transfer == "synonyms":
        T.transfer_synonymes()
    elif options.transfer == "word_props":
        T.transfer_word_props()
    elif options.transfer == "derivations":
        T.transfer_derivations()
    elif options.transfer == "ara2eng_names":
        T.transfer_ara2eng_names()
    elif options.transfer == "std2uth_words":
        T.transfer_std2uth_words()
    elif options.transfer == "vocalizations":
        T.transfer_vocalizations()

if options.speller:

    if len( args ) == 2:
        SOURCE = args[0]
        DESTINATION = args[1]
    elif len( args ) == 1:
        DESTINATION = args[0]
    else:
        parser.error( "Choose DISTINATION_PATH" )

    T = Transformer( ixpath = DESTINATION, dypypath = None, dbpath = None )

    if options.speller == "aya":
        T.build_speller( indexname = "AYA_SPELL", fields = ["aya"] )
    elif options.speller == "subject":
        T.build_speller( indexname = "SUBJECT_SPELL", fields = ["subject"] )
    elif options.speller == "word":
        T.build_speller( indexname = "WORD_SPELL", fields = ["word"] )


if options.update:

    if len( args ) == 2:
        SOURCE = args[0]
        DESTINATION = args[1]
    else:
        parser.error( "Choose SOURCE_PATH and DISTINATION_PATH" )

    if options.update == "translations":
        update_translations_list( TSE_index = SOURCE, translations_list_file = DESTINATION )
    elif options.update == "wordqc":
        QCI = QuranicCorpusImporter( SOURCE, DESTINATION )

