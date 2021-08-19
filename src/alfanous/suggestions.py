# coding: utf-8

# #     Copyright (C) 2009-2012 Assem Chelli <assem.ch [at] gmail.com>

# #     This program is free software: you can redistribute it and/or modify
# #     it under the terms of the GNU Affero General Public License as published by
# #     the Free Software Foundation, either version 3 of the License, or
# #     (at your option) any later version.

# #     This program is distributed in the hope that it will be useful,
# #     but WITHOUT ANY WARRANTY; without even the implied warranty of
# #     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# #     GNU Affero General Public License for more details.

# #     You should have received a copy of the GNU Affero General Public License
# #     along with this program.  If not, see <http://www.gnu.org/licenses/>.


from alfanous.Support.whoosh.spelling import SpellChecker


class QSuggester(SpellChecker):
    """ the basic system of suggestions """

    def __init__(self, docindex, qparser, fields, spellindexname):
        storage = docindex.get_index().storage
        self._qparser = qparser
        self._reader = docindex.get_reader()
        self.fields = fields
        super(QSuggester, self).__init__(storage,
                                         indexname=spellindexname,
                                         booststart=5.0,
                                         boostend=0.5,
                                         mingram=3, maxgram=4
                                         )

    def qsuggest(self, querystr):
        suggestion_result = {}
        missing = set()
        query = self._qparser.parse(querystr)
        query.existing_terms(self._reader,
                             missing,
                             reverse=True,
                             phrases=True)
        for fieldname, termtext in missing:
            if fieldname in self.fields:
                suggestions = list(set(self.suggest(termtext, number=3)))
                if suggestions:
                    suggestion_result[termtext] = suggestions

        return suggestion_result

    def qautocomplete(self, querystr):
        suggestion_result = {}

        query = self._qparser.parse(querystr)
        fieldname, termtext = query.all_terms().pop()
        print(termtext,fieldname)
        if fieldname in self.fields:
            return list(set(self.suggest(termtext, number=10, usescores=True)))

def QAyaSpellChecker(docindex, qparser):
    """spellchecking the words of aya fields"""
    return QSuggester(docindex,
                      qparser,
                      fields=["aya",  "aya_"],
                      spellindexname="AYA_SPELL")


def QSubjectSpellChecker(docindex, qparser):
    """spellchecking the words of aya fields"""
    return QSuggester(docindex,
                      qparser,
                      fields=["subject", "chapter", "topic", "subtopic"],
                      spellindexname="Sub_SPELL")


def QWordChecker(docindex, qparser):
    """spellchecking the words"""
    return QSuggester(docindex,
                      qparser,
                      fields=["word"],
                      spellindexname="WORD_SPELL")


def concat_suggestions(listofsuggestions):
    D = {}
    for unit in listofsuggestions:
        for key, values in unit.items():
            if D.has_key(key):
                D[key].extend(list(values))
            else:
                D[key] = list(values)
    return D
