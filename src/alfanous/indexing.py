from whoosh.filedb.filestore import FileStorage
from whoosh.filedb.structfile import BufferFile
from whoosh import index
from alfanous.constants import QURAN_TOTAL_VERSES


class _MemoryViewFile:
    """Zero-copy file-like wrapper around a memoryview or buffer.

    ``BytesIO(buf)`` copies the entire buffer into anonymous heap memory.
    This class provides the same *read-only* file interface (``read``,
    ``seek``, ``tell``, ``readline``) while keeping a reference to the
    original buffer, avoiding the duplication of large mmap'd index
    segments (~155 MB each).
    """

    __slots__ = ("_buf", "_len", "_pos")

    def __init__(self, buf):
        self._buf = buf
        self._len = len(buf)
        self._pos = 0

    # -- file-like read interface -------------------------------------------

    def read(self, n=-1):
        if n is None or n < 0:
            data = bytes(self._buf[self._pos:])
            self._pos = self._len
            return data
        end = min(self._pos + n, self._len)
        data = bytes(self._buf[self._pos:end])
        self._pos = end
        return data

    def readline(self):
        buf = self._buf
        pos = self._pos
        end = self._len
        while pos < end:
            # In Python 3 both bytes[i] and memoryview[i] return int.
            if buf[pos] == 10:  # ord(b"\n")
                pos += 1
                break
            pos += 1
        data = bytes(buf[self._pos:pos])
        self._pos = pos
        return data

    def seek(self, pos, whence=0):
        if whence == 0:
            self._pos = pos
        elif whence == 1:
            self._pos += pos
        elif whence == 2:
            self._pos = self._len + pos
        # Clamp to [0, _len]
        if self._pos < 0:
            self._pos = 0
        elif self._pos > self._len:
            self._pos = self._len
        return self._pos

    def tell(self):
        return self._pos

    def close(self):
        pass


def _zero_copy_bufferfile_init(self, buf, name=None, onclose=None):
    """Drop-in replacement for ``BufferFile.__init__`` that avoids the
    ``BytesIO(buf)`` copy.  All other attributes are set identically to
    the original constructor.
    """
    self._buf = buf
    self._name = name
    self.file = _MemoryViewFile(buf)
    self.onclose = onclose
    self.is_real = False
    self.is_closed = False


# Applied at import time which is serialised by the GIL; safe for threads.
BufferFile.__init__ = _zero_copy_bufferfile_init


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
        if index.exists_in(self._ixpath):
            storage = FileStorage(self._ixpath)
            ix = storage.open_index()
            ok = True

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
