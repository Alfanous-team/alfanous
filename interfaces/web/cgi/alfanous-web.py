#!/usr/bin/python
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
@author: assem
@contact: assem.ch [at] gmail.com
@license: AGPL
@deprecated: use alfanous-json instead

@todo: multithreading server-clients


"""

print "Content-Type: text/html; charset=utf-8\n\n" 
print 

import cgi
import cgitb
cgitb.enable()
from sys import path

path.append("alfanous.egg/alfanous")

from Gate import *
	
form = cgi.FormContentDict()



if form.has_key("suggest"):
    print suggest_text(form["suggest"][0])	

elif  form.has_key("suggest_site"):
	print suggest_html(form["suggest_site"][0])	

elif  form.has_key("search"):
	print results(form["search"][0])

elif  form.has_key("search_site"):
	if form.has_key("sortedby"):
		sortedby = form["sortedby"][0]
	else: sortedby = "score"
	if form.has_key("page"):
		page = form["page"][0]
	else: page = 1
	if form.has_key("recitation"):
		recitation = form["recitation"][0]
	else: recitation = "Mishary Rashid Alafasy"
	if form.has_key("traduction"):
		traduction = form["traduction"][0]
	else: traduction = "None"
	print results(form["search_site"][0], type="html", sortedby=sortedby, recitation=recitation,page=page,traduction=traduction)
	
elif  form.has_key("search_bot"):
	print results(form["search_bot"][0], type="newbot")

elif form.has_key("recit_site"):
	print recitations(type="site")
	
elif form.has_key("recit"):
	print recitations(type="text")
	
elif form.has_key("visit"):
	visitsplus()
	print visit()
else:
	print whoami()


