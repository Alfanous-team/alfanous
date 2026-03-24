#!/usr/bin/python2
# -*- coding: UTF-8 -*- 

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


"""
@author: assem chelli
@contact: assem.ch [at] gmail.com
@license: AGPL

TODO add  ID of requester for  better experience
TODO multithreading server-clients
TODO send error messages (no results, parsing exception)

"""
from sys import path

import cgi
import cgitb
cgitb.enable()

path.append( "alfanous.egg/alfanous" )
from alfanous.Outputs import Json



JSONoutput = Json() #use default paths

JSON_HEADER = """Content-Type: application/json; charset=utf-8
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET

""" #Allow cross domain XHR
HTTP_HEADER = """Content-Type: text/html; charset=utf-8\n\n

"""

# Get form arguments and build the flags dict
form = cgi.FormContentDict()
flags = {}
for key, value in form.items():
    flags[key] = value[0]


if len(flags):    
    print JSON_HEADER
    print JSONoutput.do( flags )

else:
    print HTTP_HEADER
    print JSONoutput._information["json_output_system_note"]




