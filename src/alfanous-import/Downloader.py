#!/usr/bin/env python
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


@note:  read the licences of those ressources before download them
'''

#import twill  ## disabled tempararily because a bug in twill with python2.6 


def download_tanzil( quranType = "simple-clean", outType = "xml", outPath = "./tanzil.xml" ):
    """
    quranType : simple, simple-enhanced,  simple-min, simple-clean , uthmani, uthmani-min
    outType : txt, xml, sql

    """
    bw = twill.get_browser()
    bw.go( "http://tanzil.net/pub/download/download.htm" )
    form = bw.get_all_forms()[0]
    #print bw.get_title()
    form.set_value( [quranType], id = "quranType" )
    form.set_value( [outType], id = "outType" )
    form.set_value( ["true"], id = "agree" )
    bw.submit()
    f = open( outPath, "w+" )
    f.write( bw.get_html() )
    return "file :  " + outPath

def download_quranic_corpus():
    """
    ## javascript executing
    """
    bw = twill.get_browser()
    bw.go( "http://corpus.quran.com/download/default.jsp" )
    form = bw.get_all_forms()[1]
    #print bw.get_title()
    twill.commands.fv( "downloadForm", "txtEmail", "test@test.tt" )
    bw.submit()
    bw.go( "javascript:downloadFile('3');" )

    return "not yet"


def download_tanzil_translations():
    """  http://tanzil.net/trans/ """
    pass


