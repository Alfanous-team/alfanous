# coding: utf-8

##     Copyright (C) 2009-2012 Assem Chelli <assem.ch [at] gmail.com>

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

""" hint: use `alfanous.do` method for search, suggestion and get most useful info"""

# import Output object
from alfanous.Outputs import Raw as _search_engine
# import default Paths
from alfanous.Data import Paths as PATHS

DEFAULTS, DOMAINS, HELPMESSAGES, ERRORS = _search_engine.DEFAULTS, _search_engine.DOMAINS, _search_engine.HELPMESSAGES, _search_engine.ERRORS
FLAGS = DEFAULTS["flags"].keys()

from alfanous.Outputs import Fields as _fields

FIELDS_ARABIC = _fields.keys()
FIELDS_ENGLISH = _fields.values()


_R = _search_engine()

# Pivot function for search, suggestion, show info
def do(flags):
    """
    Perform action defined in `flags` and return results as `dict`.
    
    flags is a dict with values for those keys:
    - "action": action to be performed, could be "search" or "suggest" or "show". default is "search"
    - "query": query for action to be pefromed
    - "unit": search unit, could be "aya" or "translation". default is "aya"
    Check alfanous.FLAGS for the list of all flags, alfanous.HELPMESSAGES for their discriptions, alfanous.DOMAINS for their possible values and alfanous.DEFAULTS for their default values.
    
        >>> results = do({"query":u"الحمد لله"})
        >>> results["error"]
        {'msg': 'success', 'code': 0}
        >>> results["search"]["ayas"][1]["identifier"]
        {'sura_id': 1, 'gid': 2, 'sura_arabic_name': u'\u0627\u0644\u0641\u0627\u062a\u062d\u0629', 'sura_name': u'Al-Fat
ihah', 'aya_id': 2}

    """
    return _R.do(flags)

# search in aya
def search_aya(query):
    "search in verses of Quran"
    return do({"query":query})

def search_aya_minimal(query):
    "search in verses of Quran (minimal info)"
    return do({"query":query, "view":"minimal", "highlight":"none"})

# search in translation
def search_translation(query):
    "search in translations of Quran"
    return do({"query":query,"unit":"translation"})

def show_all_info():
    return do({"action":"show","query":"all"})
