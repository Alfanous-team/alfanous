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
'''
from alfanous.Indexing import QseDocIndex
from alfanous.QueryProcessing import QuranicParser
from alfanous.ResultsProcessing import QSort, QScore


class QReader:
    """ reader of the index """
    def __init__( self, docindex ):
        self.reader = docindex.get_index().reader()
        self.schema = docindex.get_schema()


    def list_values( self, fieldname = None, double = False, conditions = [] ):
        """
        a chosen field stored values generator

        @param fieldname: the name of the chosen field
        @param double: Eliminate the doubles or not
        @param conditions: conditions of match
        @type conditions: list of couples
        @return : stored values

        """
        prec = []


        if fieldname:
            for  D in self.reader.all_stored_fields():
                cond = True
                for cfield, cvalue in conditions:
                    if D[cfield] != cvalue : cond = False ; break;

                if cond:
                    value = D[fieldname]
                    if value not in prec:
                        prec.append( value )
                        yield value
        else:
            for  D in self.reader.all_stored_fields():
                cond = True
                for cfield, cvalue in conditions:
                    if D[cfield] != cvalue : cond = False ; break;


                if cond:
                    for value in D.values() :
                        if value not in prec:
                            prec.append( value )
                            yield value


    def list_terms( self, fieldname = None, double = False ):
        """
        a choosen field indexed terms generator

        @param fieldname: the name of the choosen field
        @return : indexed terms

        """
        prec = []
        if fieldname:
            for  field, value in self.reader.all_terms():
                    if field == fieldname:
                        if value not in prec:
                            prec.append( value )
                            yield value
        else:
            for  field, value in self.reader.all_terms():
                if value not in prec:
                        prec.append( value )
                        yield value

    def term_stats( self, terms ):
        """ return all statistiques of a term
         - document frequency
         - matches frequency
         """
        for term in terms:
            lst = list( term )
            lst.extend( [self.reader.frequency( *term ), self.reader.doc_frequency( *term )] )
            yield tuple( lst )


#


class QSearcher:
    """ search"""
    def __init__( self, docindex, qparser ):
        self._searcher = docindex.get_index().searcher
        self._qparser = qparser

    def search( self, querystr, limit = 6236, sortedby = "score", reverse = False ):
        searcher = self._searcher( weighting = QScore() )
        query = self._qparser.parse( querystr )
        results = searcher.search( query, limit, QSort( sortedby ), reverse )
        terms = set()
        try:
            query.all_terms( terms )
        except:
            pass

        return results, terms, searcher










