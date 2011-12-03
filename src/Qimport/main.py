#!/bin/python
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
Created on Jul 28, 2011

@author: Assem chelli 
'''

from Importer import *
from Transformer import *


from optparse import OptionParser,OptionGroup

usage = "usage: %prog [options]  SOURCE_PATH DESTINATION_PATH "
parser = OptionParser(usage=usage, version="Alfanous 0.4 - Importer")

commands = OptionGroup(parser, "Options", "Choose what to do:  ")



commands.add_option("-x", "--index",dest="index",type="choice",choices=["main", "extend" , "word"],
                  help="create  indexes",metavar="TYPE") 

commands.add_option("-t", "--transfer",dest="transfer",type="choice",choices=["stopwords", "synonyms", "word_props", "derivations", "ara2eng_names"],
                  help="transfer from database to dynamic resources",metavar="RESOURCE") 

commands.add_option("-p", "--speller",dest="speller",type="choice",choices=["aya", "subject"],
                  help="build a speller for a field",metavar="FIELD") 





parser.add_option_group(commands)


parser.set_defaults(help=True)

(options, args) = parser.parse_args()


if (options.index and options.transfer) or  (options.index and options.speller) or ( options.speller and options.transfer):
        parser.error("-x , -t  and -p  are exclusives!")


if options.index:
    if len(args)==2:
        SOURCE=args[0]
        DESTINATION=args[1]
    else:
        parser.error("Choose SOURCE_PATH and DISTINATION_PATH")
        
    if options.index=="main":
        T= Transformer( ixpath=DESTINATION , dypypath=None,dbpath=SOURCE)
        ayaSchema=T.build_schema(tablename='aya')
        T.build_docindex(ayaSchema) 

    elif options.index=="extend":
        E = ZekrModelsImporter(pathindex=DESTINATION, pathstore=SOURCE)
        E.load_translationModels()
    
    elif options.index=="word" :
        pass


if options.transfer:

    if len(args)==2:
        SOURCE=args[0]
        DESTINATION=args[1]
    else:
        parser.error("Choose SOURCE_PATH and DISTINATION_PATH")
        
    T= Transformer(ixpath=".", dypypath=DESTINATION,dbpath=SOURCE)
    if options.transfer=="stopwords":
        T.transfer_stopwords()
    elif options.transfer=="synonyms":
        T.transfer_synonymes()
    elif options.transfer=="word_props":
        T.transfer_word_props()
    elif options.transfer=="derivations":
        T.transfer_derivations()
    elif options.transfer=="ara2eng_names":
        T.transfer_ara2eng_names()

if options.speller:
    
    if len(args)==2:
        SOURCE=args[0]
        DESTINATION=args[1]
    elif len(args)==1:
        DESTINATION=args[0]
    else:
        parser.error("Choose DISTINATION_PATH")
    
    T= Transformer(ixpath=DESTINATION, dypypath=None,dbpath=None)
    
    if options.speller=="aya":
        T.build_ayaspeller()
    elif options.speller=="subject":
        T.build_subjectspeller()

