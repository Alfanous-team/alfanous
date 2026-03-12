import logging

from whoosh.filedb.filestore import FileStorage
from whoosh import index
from alfanous.constants import QURAN_TOTAL_VERSES

logger = logging.getLogger(__name__)


class BasicDocIndex:
    """all props of  Document Index"""
    OK = False

    def __init__(self, ixpath):
        self._ixpath = ixpath
        self._ix, self.OK = self.load()
        self.OK = self.OK and self.verify()

    def load(self):
        """
            Load the Index from the path ixpath
            return self.OK = True if success
        """
        ix, ok = None, False
        try:
            if index.exists_in(self._ixpath):
                storage = FileStorage(self._ixpath)
                ix = storage.open_index()
                ok = True
        except Exception as e:
            logger.error(
                "Failed to open index at %r: %s — index may be corrupted or "
                "truncated (run 'make build' to rebuild it)",
                self._ixpath,
                e,
            )
        return ix, ok

    def verify(self):
        return True

    def __str__(self):
        return "<alfanous.Indexing.BasicDocIndex '" \
               + self._ixpath + "'" \
               + str(self._ix.doc_count()) + ">"

    def get_index(self):
        """return index"""
        return self._ix

    def get_schema(self):
        """ return schema """
        return self._ix.schema

    def get_reader(self):
        """Open and return a new Whoosh IndexReader for this index.

        .. warning::
            Each call opens a **new** IndexReader.  The caller is responsible
            for closing the returned reader (e.g. via a ``try/finally`` or
            ``with`` block) to release the underlying file-descriptor and
            memory-map resources.  Failing to close the reader is a resource
            leak.

            In the normal hot path, prefer using the shared reader managed by
            :class:`~alfanous.searching.QSearcher` (via
            :class:`~alfanous.searching.QReader`) instead of calling this
            method directly.
        """
        return self._ix.reader()

    def get_searcher(self):
        """ return searcher """
        return self._ix.searcher

    def __len__(self):
        return self._ix.doc_count()

    def add_document(self, doc):
        """ add a new document
        @param doc: the document
        @type doc: dict

        """
        with self._ix.writer() as writer:
            writer.add_document(**doc)

    def add_documents(self, doclist):
        """ add a new documents

        @param doclist: the documents
        @type doclist: list(dict)

        """
        with self._ix.writer() as writer:
            for doc in doclist:
                writer.add_document(**doc)

    def update_documents(self, doclist):
        """ update documents

        @param doclist: the documents
        @type doclist: list(dict)

        """
        with self._ix.writer() as writer:
            for doc in doclist:
                writer.update_document(**doc)

    def delete_by_query(self, query):
        """ delete a set of documents retrieved by a query """
        with self._ix.writer() as writer:
            writer.delete_by_query(query)

    def __call__(self):
        return self.OK


class QseDocIndex(BasicDocIndex):
    """all props of  Document Index"""

    def __str__(self):
        return "<alfanous.Indexing.QseDocIndex '" \
               + self._ixpath + "'" \
               + str(self._ix.doc_count()) + ">"

    def verify(self):
        # A nested index stores translation child documents alongside the 6236
        # parent aya documents, so the total doc count will be larger.
        return len(self) >= QURAN_TOTAL_VERSES


class ExtDocIndex(BasicDocIndex):
    """ all properties of extended doc index """

    def __str__(self):
        return "<alfanous.Indexing.ExtendedDocIndex '" \
               + self._ixpath + "'" \
               + str(self._ix.doc_count()) + ">"
