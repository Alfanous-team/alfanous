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
a console interface for the API.

TODO show RAW|JSON | BEST-presentation format
'''

import sys
import json
from argparse import ArgumentParser

from alfanous.outputs import Raw

RAWoutput = Raw()  # use default paths

INFORMATION = RAWoutput.do({"action": "show", "query": "information"})["show"]["information"]
DOMAINS = RAWoutput.do({"action": "show", "query": "domains"})["show"]["domains"]
HELPMESSAGES = RAWoutput.do({"action": "show", "query": "help_messages"})["show"]["help_messages"]

arg_parser = ArgumentParser(
    description=INFORMATION["description"],
    prog='alfanous-console',
    version='%(prog)s ' + INFORMATION["version"],
    usage=sys.argv[0] + " [flags]"
)

#
Boolean_choices = ["true", "false"]

# add arguments ## TODO this should be automatized using the fields list
arg_parser.add_argument("-a", "--action", dest="action", type=str, choices=DOMAINS["action"],
                        help=HELPMESSAGES["action"])
arg_parser.add_argument("-u", "--unit", dest="unit", type=str, choices=DOMAINS["unit"], help=HELPMESSAGES["unit"])
arg_parser.add_argument("-q", "--query", dest="query", type=str, help=HELPMESSAGES["query"])
arg_parser.add_argument("-o", "--offset", dest="offset", metavar='NUMBER', type=int, help=HELPMESSAGES["offset"])
arg_parser.add_argument("-r", "--range", dest="range", type=int, metavar='NUMBER', help=HELPMESSAGES["range"])
arg_parser.add_argument("-s", "--sortedby", dest="sortedby", type=str, choices=DOMAINS["sortedby"],
                        help=HELPMESSAGES["sortedby"])
arg_parser.add_argument("-w", "--view", dest="view", type=str, choices=DOMAINS["view"], help=HELPMESSAGES["view"])
arg_parser.add_argument("--page", dest="page", type=int, metavar='NUMBER', help=HELPMESSAGES["page"])
arg_parser.add_argument("--perpage", dest="perpage", type=int, metavar='NUMBER', help=HELPMESSAGES["perpage"])
arg_parser.add_argument("--recitation", dest="recitation", metavar='NUMBER', type=str, help=HELPMESSAGES["recitation"])
arg_parser.add_argument("--translation", dest="translation", type=str, help=HELPMESSAGES["translation"])
arg_parser.add_argument("--romanization", dest="romanization", type=str, help=HELPMESSAGES["romanization"])
arg_parser.add_argument("--highlight", dest="highlight", type=str, choices=DOMAINS["highlight"],
                        help=HELPMESSAGES["highlight"])
arg_parser.add_argument("--script", dest="script", type=str, choices=DOMAINS["script"], help=HELPMESSAGES["script"])
arg_parser.add_argument("--vocalized", dest="vocalized", type=str, choices=Boolean_choices,
                        help=HELPMESSAGES["vocalized"])
arg_parser.add_argument("--prev_aya", dest="prev_aya", type=str, choices=Boolean_choices, help=HELPMESSAGES["prev_aya"])
arg_parser.add_argument("--next_aya", dest="next_aya", type=str, choices=Boolean_choices, help=HELPMESSAGES["next_aya"])
arg_parser.add_argument("--sura_info", dest="sura_info", type=str, choices=Boolean_choices,
                        help=HELPMESSAGES["sura_info"])
arg_parser.add_argument("--sura_stat_info", dest="sura_stat_info", type=str, choices=Boolean_choices,
                        help=HELPMESSAGES["sura_stat_info"])
arg_parser.add_argument("--word_info", dest="word_info", type=str, choices=Boolean_choices,
                        help=HELPMESSAGES["word_info"])
arg_parser.add_argument("--word_synonyms", dest="word_synonyms", type=str, choices=Boolean_choices,
                        help=HELPMESSAGES["word_synonyms"])
arg_parser.add_argument("--word_derivations", dest="word_derivations", type=str, choices=Boolean_choices,
                        help=HELPMESSAGES["word_derivations"])
arg_parser.add_argument("--word_vocalizations", dest="word_vocalizations", type=str, choices=Boolean_choices,
                        help=HELPMESSAGES["word_vocalizations"])
arg_parser.add_argument("--aya_position_info", dest="aya_position_info", type=str, choices=Boolean_choices,
                        help=HELPMESSAGES["aya_position_info"])
arg_parser.add_argument("--aya_theme_info", dest="aya_theme_info", type=str, choices=Boolean_choices,
                        help=HELPMESSAGES["aya_theme_info"])
arg_parser.add_argument("--aya_stat_info", dest="aya_stat_info", type=str, choices=Boolean_choices,
                        help=HELPMESSAGES["aya_stat_info"])
arg_parser.add_argument("--aya_sajda_info", dest="aya_sajda_info", type=str, choices=Boolean_choices,
                        help=HELPMESSAGES["aya_sajda_info"])
arg_parser.add_argument("--annotation_aya", dest="annotation_aya", type=str, choices=Boolean_choices,
                        help=HELPMESSAGES["annotation_aya"])
arg_parser.add_argument("--annotation_word", dest="annotation_word", type=str, choices=Boolean_choices,
                        help=HELPMESSAGES["annotation_word"])
arg_parser.add_argument("--fuzzy", dest="fuzzy", type=str, choices=Boolean_choices, help=HELPMESSAGES["fuzzy"])
arg_parser.add_argument("--ident", dest="ident", type=str, help=HELPMESSAGES["ident"])
arg_parser.add_argument("--platform", dest="platform", type=str, choices=DOMAINS["platform"],
                        help=HELPMESSAGES["platform"])
arg_parser.add_argument("--domain", dest="domain", type=str, help=HELPMESSAGES["domain"])


# execute command
def main():
    args = arg_parser.parse_args()

    # Get the arguments as a dictionary and remove None-valued keys.
    flags = {}
    for k, v in args.__dict__.items():
        if v is not None:
            flags[k] = v

    if args.action and args.query:
        print json.dumps(RAWoutput.do(flags), sort_keys=False, indent=4)
    else:
        print RAWoutput._information["console_note"]
