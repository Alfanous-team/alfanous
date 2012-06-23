# coding: utf-8

##      Copyright (C) 2009-2010 Assem Chelli <assem.ch@gmail.com>
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

'''
Created on 24 févr. 2010

@author: Assem Chelli
@contact: assem.ch [at] gmail.com
@license: AGPL

TODO show RAW|JSON | BEST-presentation format
TODO __file__ to use resources and indexes integrated with Alfanous Module
'''

import sys, json, os


from argparse import ArgumentParser
from alfanous.Outputs import Raw

RAWoutput = Raw() #use default paths 

INFORMATION = RAWoutput.do( {"action":"show", "query":"information" } )["show"]["information"]
DOMAINS = RAWoutput.do( {"action":"show", "query":"domains" } )["show"]["domains"]
HELPMESSAGES = RAWoutput.do( {"action":"show", "query":"help_messages" } )["show"]["help_messages"]

## a function to decide what is True and what is False
TRUE_FALSE = lambda x:False if x.lower() in ["no", "none", "null", "0", "-1", "", "false"] else True;




arg_parser = ArgumentParser( 
                              description = INFORMATION["description"],
                              prog = 'alfanous-console',
                              version = '%(prog)s ' + INFORMATION["version"],
                              usage = sys.argv[0] + " [flags]"
                            )

# add arguments
arg_parser.add_argument( "-a", "--action", dest = "action", type = str , choices = DOMAINS["action"], help = HELPMESSAGES["action"] )
arg_parser.add_argument( "-q", "--query", dest = "query", type = str  , help = HELPMESSAGES["query"] )
arg_parser.add_argument( "-o", "--offset", dest = "offset", metavar = 'NUMBER', type = int, help = HELPMESSAGES["offset"] )
arg_parser.add_argument( "-r", "--range", dest = "range", type = int, metavar = 'NUMBER', help = HELPMESSAGES["range"] )
arg_parser.add_argument( "-s", "--sortedby", dest = "sortedby", type = str, choices = DOMAINS["sortedby"], help = HELPMESSAGES["sortedby"] )
arg_parser.add_argument( "--page", dest = "page", type = int, metavar = 'NUMBER', help = HELPMESSAGES["page"] )
arg_parser.add_argument( "--perpage", dest = "perpage", type = int, metavar = 'NUMBER', help = HELPMESSAGES["perpage"] )
arg_parser.add_argument( "--recitation", dest = "recitation", type = str, help = HELPMESSAGES["recitation"] )
arg_parser.add_argument( "--translation", dest = "translation", metavar = 'NUMBER', type = str, help = HELPMESSAGES["translation"] )
arg_parser.add_argument( "--highlight", dest = "highlight", type = str, choices = DOMAINS["highlight"], help = HELPMESSAGES["highlight"] )
arg_parser.add_argument( "--script", dest = "script", type = str, choices = DOMAINS["script"] , help = HELPMESSAGES["script"] )
arg_parser.add_argument( "--vocalized", dest = "vocalized", type = bool, choices = DOMAINS["vocalized"], help = HELPMESSAGES["vocalized"] )
arg_parser.add_argument( "--prev_aya", dest = "prev_aya", type = bool, choices = DOMAINS["prev_aya"], help = HELPMESSAGES["prev_aya"] )
arg_parser.add_argument( "--next_aya", dest = "next_aya", type = bool, choices = DOMAINS["next_aya"], help = HELPMESSAGES["next_aya"] )
arg_parser.add_argument( "--sura_info", dest = "sura_info", type = bool, choices = DOMAINS["sura_info"], help = HELPMESSAGES["sura_info"] )
arg_parser.add_argument( "--word_info", dest = "word_info", type = bool, choices = DOMAINS["word_info"], help = HELPMESSAGES["word_info"] )
arg_parser.add_argument( "--aya_position_info", dest = "aya_position_info", type = bool, choices = DOMAINS["aya_position_info"], help = HELPMESSAGES["aya_position_info"] )
arg_parser.add_argument( "--aya_theme_info", dest = "aya_theme_info", type = bool, choices = DOMAINS["aya_theme_info"], help = HELPMESSAGES["aya_theme_info"] )
arg_parser.add_argument( "--aya_stat_info", dest = "aya_stat_info", type = bool, choices = DOMAINS["aya_stat_info"], help = HELPMESSAGES["aya_stat_info"] )
arg_parser.add_argument( "--aya_sajda_info", dest = "aya_sajda_info", type = bool, choices = DOMAINS["aya_sajda_info"], help = HELPMESSAGES["aya_sajda_info"] )
arg_parser.add_argument( "--annotation_aya", dest = "annotation_aya", type = bool, choices = DOMAINS["annotation_aya"], help = HELPMESSAGES["annotation_aya"] )
arg_parser.add_argument( "--annotation_word", dest = "annotation_word", type = bool, choices = DOMAINS["annotation_word"], help = HELPMESSAGES["annotation_word"] )
arg_parser.add_argument( "--fuzzy", dest = "fuzzy", type = bool, choices = DOMAINS["fuzzy"], help = HELPMESSAGES["fuzzy"] )
arg_parser.add_argument( "--ident", dest = "ident", type = str  , help = HELPMESSAGES["ident"] )
arg_parser.add_argument( "--platform", dest = "platform", type = str, choices = DOMAINS["platform"], help = HELPMESSAGES["platform"] )
arg_parser.add_argument( "--domain", dest = "domain", type = str, help = HELPMESSAGES["domain"] )




#execute command
def main():
    args = arg_parser.parse_args()
    if args.action and args.query:
        flags = {}
        if args.action: flags["action"] = args.action
        if args.query: flags["query"] = args.query
        if args.ident: flags["ident"] = args.ident
        if args.platform: flags["platform"] = args.platform
        if args.domain: flags["domain"] = args.domain
        if args.sortedby: flags["sortedby"] = args.sortedby
        if args.page: flags["page"] = args.page
        if args.perpage: flags["perpage"] = args.perpage
        if args.offset: flags["offset"] = args.offset
        if args.range:  flags["range"] = args.range
        if args.recitation: flags["recitation"] = args.recitation
        if args.translation: flags["translation"] = args.translation
        if args.highlight: flags["highlight"] = args.highlight
        if args.script: flags["script"] = args.script
        if args.vocalized: flags["vocalized"] = TRUE_FALSE( args.vocalized )
        if args.prev_aya: flags["prev_aya"] = TRUE_FALSE( args.prev_aya )
        if args.next_aya: flags["next_aya"] = TRUE_FALSE( args.next_aya )
        if args.sura_info: flags["sura_info"] = TRUE_FALSE( args.sura_info )
        if args.word_info: flags["word_info"] = TRUE_FALSE( args.word_info )
        if args.aya_position_info: flags["aya_position_info"] = TRUE_FALSE( args.aya_position_info )
        if args.aya_theme_info: flags["aya_theme_info"] = TRUE_FALSE( args.aya_theme_info )
        if args.aya_stat_info: flags["aya_stat_info"] = TRUE_FALSE( args.aya_stat_info )
        if args.aya_sajda_info: flags["aya_sajda_info"] = TRUE_FALSE( args.aya_sajda_info )
        if args.annotation_aya: flags["annotation_aya"] = TRUE_FALSE( args.annotation_aya )
        if args.annotation_word: flags["annotation_word"] = TRUE_FALSE( args.annotation_word )
        if args.fuzzy: flags["fuzzy"] = TRUE_FALSE( args.fuzzy )

        print json.dumps( RAWoutput.do( flags ) )
    else:
        print RAWoutput._information["console_note"]




