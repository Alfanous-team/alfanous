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


'''
@author: Assem Chelli
@contact: assem.ch [at] gmail.com
@license: AGPL

'''


from alfanous.Exceptions import Ta7rif
from alfanous.Support.whoosh.filedb.filestore import FileStorage
from alfanous.Support.whoosh import index


class BasicDocIndex:
    """all props of  Document Index"""
    OK = False
    def __init__( self, ixpath ):
        self._ixpath = ixpath
        self._ix, self.OK = self.load()
        self.verify()


    def load( self ):
        """
            Load the Index from the path ixpath
            return self.OK = True if success
        """
        ix, ok = None, False
        if  index.exists_in( self._ixpath ):
            storage = FileStorage( self._ixpath )
            ix = storage.open_index()
            ok = True

        return ix, ok

    def verify( self ):
        """
        verify the data of index after loading
        """
        pass

    def __str__( self ):
        return "<alfanous.Indexing.BasicDocIndex '" \
                + self._ixpath + "'" \
                + str( self._ix.doc_count() ) + ">"

    def get_index( self ):
        """return index"""
        return self._ix
    def get_schema( self ):
        """ return schema """
        return self._ix.schema

    def get_reader( self ):
        """ return reader """
        return self._ix.reader()

    def get_searcher( self ):
        """ return searcher """
        return self._ix.searcher

    def __len__( self ):
        return self._ix.doc_count()

    def add_document( self, doc ):
        """ add a new document
        @param doc: the document
        @type doc: dict

        """
        writer = self.index.writer()
        writer.add_document( **doc )
        writer.commit()

    def add_documents( self, doclist ):
        """ add a new documents

        @param doclist: the documents
        @type doclist: list(dict)

        """
        writer = self._ix.writer()
        for doc in doclist:
            writer.add_document( **doc )
        writer.commit()


    def update_documents( self, doclist ):
        """ update documents

        @param doclist: the documents
        @type doclist: list(dict)

        """
        writer = self._ix.writer()
        for doc in doclist:
            writer.update_document( **doc )
        writer.commit()

    def delete_by_query( self, query ):
        """ delete a set of documents retrieved by a query """
        writer = self._ix.writer()
        writer.delete_by_query( query )
        writer.commit()

    def __call__( self ):
        return self.OK


class QseDocIndex( BasicDocIndex ):
    """all props of  Document Index"""


    def __str__( self ):
        return "<alfanous.Indexing.QseDocIndex '" \
                + self._ixpath + "'" \
                + str( self._ix.doc_count() ) + ">"

    def verify( self ):
        """raise a  ta7rif exception if it is wrong"""
        nb = -1
        if self.OK:
            nb = len( self )
            if nb != 6236 :
                raise Ta7rif( "Ayas count is not exact", value = nb, original = 6236, msg = "you must update your indexes" )
        return nb







class ExtDocIndex( BasicDocIndex ):
    """ all properties of extended doc index """


    def __str__( self ):
        return "<alfanous.Indexing.ExtendedDocIndex '" \
                + self._ixpath + "'" \
                + str( self._ix.doc_count() ) + ">"



if __name__ == "__main__":
    E = ExtDocIndex( ixpath = "../indexes/extend/" )
    D = QseDocIndex( ixpath = "../indexes/main/" )




