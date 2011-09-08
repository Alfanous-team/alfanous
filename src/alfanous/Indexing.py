# coding: utf-8
#    Copyright (C) 2009-2010 Assem Chelli <assem.ch@gmail.com>
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

'''
@author: Assem Chelli
@contact: assem.ch [at] gmail.com
@license: GPL
@version: 0.1
@organization: wait Support
'''


from Exceptions import Ta7rif 
from Support.whoosh.filedb.filestore import FileStorage
from Support.whoosh import index



class BasicDocIndex:
    """all props of  Document Index"""
    OK=False
    def __init__(self, ixpath):
        self.load(ixpath)

        
    def load(self,ixpath):
        if  index.exists_in(ixpath):
            storage = FileStorage(ixpath)
            self._ix = storage.open_index()
            self._ixpath = ixpath
            self.OK = True
        else:
            self.OK = False
    
    def __str__(self):
        return "<alfanous.Indexing.BasicDocIndex '" + self._ixpath + "'" + str(self._ix.doc_count()) + ">"     
    
    def get_index(self):
        """return index"""
        return self._ix
    def get_schema(self):
        """ return schema """
        return self._ix.schema
    
    def get_reader(self):
        """ return reader """
        return self._ix.reader()
    
    def get_searcher(self):
        """ return searcher """
        return self._ix.searcher
    
    def __len__(self):
        return self._ix.doc_count()
    
    def add_document(self,doc):
        """ add a new document 
        
        
        @param doc: the document
        @type doc: dict 
        
        """
        writer = self.index.writer()
        writer.add_document(**doc)   
        writer.commit()
    
    def add_documents(self,doclist):
        """ add a new documents

        @param doclist: the documents
        @type doclist: list(dict) 
        
        """
        writer = self._ix.writer()
        for doc in doclist:
            writer.add_document(**doc)   
        writer.commit()
        
        
    def update_documents(self,doclist):
        """ update documents

        @param doclist: the documents
        @type doclist: list(dict) 
        
        """
        writer = self._ix.writer()
        for doc in doclist:
            writer.update_document(**doc)   
        writer.commit()
    
    def delete_by_query(self,query):
        writer = self._ix.writer()
        writer.delete_by_query(query)  
        writer.commit()
        
    def __call__(self):
        return self.OK


class QseDocIndex(BasicDocIndex):
    """all props of  Document Index"""
    def __init__(self, ixpath="../indexes/main/"):
        self.load(ixpath)
        if self.OK:
            self.verify_docs_nb()

    def __str__(self):
        return "<alfanous.Indexing.QseDocIndex '" + self._ixpath + "'" + str(self._ix.doc_count()) + ">"     
    
         
    def verify_docs_nb(self):
        """raise a  ta7rif exception if it is wrong"""
        nb = len(self)
        if nb != 6236 : raise Ta7rif("number of ayas wrong", value=nb, original=6236, msg="you must update your index") 
        return nb   


    

     
        

class ExtDocIndex(BasicDocIndex):
    """ all properties of extended doc index """
    
    def __init__(self, ixpath="indexes/extend/"):
        self.load(ixpath)
        
    def __str__(self):
        return "<alfanous.Indexing.ExtendedDocIndex '" + self._ixpath + "'" + str(self._ix.doc_count()) + ">"  
        

    
if __name__ == "__main__":
    E = ExtDocIndex()
    D = QseDocIndex()




