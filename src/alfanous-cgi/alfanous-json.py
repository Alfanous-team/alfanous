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
@author: assem chelli
@contact: assem.ch [at] gmail.com
@license: AGPL


@todo: add  ID of requester for  better experience
@todo: multithreading server-clients
@todo: send error messages (no results, parsing exception)

"""

import cgi,cgitb
cgitb.enable()

form = cgi.FormContentDict()


from sys import path
path.append("alfanous.egg/alfanous")

from alfanous.outputs import Json

JSONoutput=Json(QSE_index="./indexes/main/", TSE_index="./indexes/extend/",WSE_index="./indexes/word/", Recitations_list_file="./configs/recitations.js",Translations_list_file="./configs/translations.js", Information_file="./configs/information.js", Hints_file="./configs/hints.js",Stats_file="./configs/stats.js")

JSON_HEADER= """Content-Type: application/json; charset=utf-8 
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET

""" #Allow cross domain XHR
HTTP_HEADER= """Content-Type: text/html; charset=utf-8\n\n

"""

## a function to decide what is True and what is false
TRUE_FALSE = lambda x: False if x.lower() in ["no","none","null","0","-1","","false"] else True;

if len(form):
    flags={}
    if form.has_key("action"): flags["action"] = form["action"][0]
    if form.has_key("query"): flags["query"] = form["query"][0]
    if form.has_key("id"): flags["id"] = form["id"][0]
    if form.has_key("platform"): flags["platform"] = form["platform"][0]
    if form.has_key("domain"): flags["domain"] = form["domain"][0]
    if form.has_key("sortedby"): flags["sortedby"] = form["sortedby"][0]
    if form.has_key("page"): flags["page"] = form["page"][0]
    if form.has_key("perpage"): flags["perpage"] = form["perpage"][0]
    if form.has_key("offset"): flags["offset"] = form["offset"][0]
    if form.has_key("range"):  flags["range"] = form["range"][0]
    if form.has_key("recitation"): flags["recitation"] = form["recitation"][0] 
    if form.has_key("translation"): flags["translation"] = form["translation"][0] 
    if form.has_key("highlight"): flags["highlight"] = form["highlight"][0]
    if form.has_key("prev_aya"): flags["prev_aya"] = TRUE_FALSE(form["prev_aya"][0])
    if form.has_key("next_aya"): flags["next_aya"] = TRUE_FALSE(form["next_aya"][0])
    if form.has_key("sura_info"): flags["sura_info"] = TRUE_FALSE(form["sura_info"][0])
    if form.has_key("word_info"): flags["word_info"] = TRUE_FALSE(form["word_info"][0])
    if form.has_key("aya_info"): flags["aya_info"] = TRUE_FALSE(form["aya_info"][0])
    if form.has_key("annotation_aya"): flags["annotation_aya"] = TRUE_FALSE(form["annotation_aya"][0])
    if form.has_key("annotation_word"): flags["annotation_word"] = TRUE_FALSE(form["annotation_word"][0])
    if form.has_key("fuzzy"): flags["fuzzy"] = TRUE_FALSE(form["fuzzy"][0])     
    
    print JSON_HEADER
    print JSONoutput.do(flags)
    

else:
    print HTTP_HEADER
    print JSONoutput._information["json_output_system_note"]




