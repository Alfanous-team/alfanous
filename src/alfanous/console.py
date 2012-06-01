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

'''


#from  alfanous.Misc import *
from  alfanous.main import QuranicSearchEngine


import sys
from optparse import OptionParser

def main():
    #initial options
    parser = OptionParser( 
                              description = ' a search engine in the Holy Quran',
                              prog = 'alfanous-cmd',
                              version = '%prog 0.1',
                              usage = sys.argv[0] + " [options] \"QUERY\""
                        )


    parser.add_option( "-s", type = "string", dest = "search", nargs = 0, default = None, help = "search in the quran" )
    parser.add_option( "-g", type = "string", dest = "suggest", nargs = 0, default = None, help = "suggest the missing words" )
    parser.add_option( "-t", type = "int", dest = "OPTION", nargs = 1, default = 12, help = "just a test" )


    #execute command
    ( options, args ) = parser.parse_args()

    if len( args ) >= 1:
            QSE = QuranicSearchEngine( "/usr/share/alfanous-indexes/main/" )
            if options.search != None:
                print "\n#search#"
                res, terms = QSE.search_all( args[0], sortedby = "score" )
                html = u"Results(time=%f,number=%d):\n" % ( res.runtime, len( res ) )
                for r in res:
                        html += "(" + r["sura"] + "," + unicode( r["aya_id"] ) + "):"
                        html += r["aya_"] + "\n"
                print html

            if options.suggest != None:
                print "#suggestions#"
                for key, value in QSE.suggest_all( args[0] ).items():
                        print key, ":", ",".join( value )
    else:
        print parser.print_help()


if  __name__ == "__main__":
    main()


