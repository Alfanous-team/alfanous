#!/bin/python
# coding: utf-8
'''
Created on Jul 29, 2011

@author: Assem chelli 
'''

from optparse import OptionParser,OptionGroup

import Gui

		



usage = "usage: %prog [options]"
parser = OptionParser(usage=usage, version="AlfanousDesktop 0.4")

paths = OptionGroup(parser, "Paths", "Choose your paths:  ")


paths.add_option("-c", "--config",dest="config",type="string",
                  help="configuration file path",metavar="PATH") 

paths.add_option("-i", "--index",dest="index",type="string",
                  help="indexes path",metavar="PATH") 

paths.add_option("-l", "--local",dest="local",type="string",
                  help="localization path",metavar="PATH") 



parser.add_option_group(paths)
(options, args) = parser.parse_args()



CONFIGPATH=options.config if options.config else "./"
INDEXPATH=options.index if options.index else"../../indexes/"
LOCALPATH=options.local if options.local else"./locale/"

print CONFIGPATH,INDEXPATH,LOCALPATH

Gui.main(CONFIGPATH,INDEXPATH,LOCALPATH)



