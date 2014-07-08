# -*- coding: utf-8 -*-

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
This module contains the html templates used in the GUI results. The reason 
that we don't separate them in independent files, is to avoid the headache of 
including separated files in packaging.
'''

import os
import codecs
from jinja2 import Template

base_path =  os.path.dirname( __file__ ) 
AYA_RESULTS_TEMPLATE = Template(codecs.open(base_path + "/templates/aya_results.html","r", "utf-8").read())
