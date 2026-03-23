"""Tests for the zero-copy _MemoryViewFile wrapper used to replace
Whoosh's BytesIO-based BufferFile."""

import pickle
import struct
from io import BytesIO

from alfanous.indexing import _MemoryViewFile


class TestMemoryViewFile:
    """Unit tests for _MemoryViewFile read/seek/tell interface."""

    def test_read_all(self):
        data = b"hello world"
        f = _MemoryViewFile(data)
        assert f.read() == data
        assert f.tell() == len(data)

    def test_read_n(self):
        data = b"hello world"
        f = _MemoryViewFile(data)
        assert f.read(5) == b"hello"
        assert f.tell() == 5
        assert f.read(1) == b" "
        assert f.read(5) == b"world"

    def test_read_past_end(self):
        data = b"abc"
        f = _MemoryViewFile(data)
        assert f.read(100) == b"abc"
        assert f.tell() == 3
        assert f.read(1) == b""

    def test_read_none(self):
        data = b"xyz"
        f = _MemoryViewFile(data)
        assert f.read(None) == data

    def test_seek_absolute(self):
        f = _MemoryViewFile(b"abcdef")
        f.seek(3)
        assert f.tell() == 3
        assert f.read(2) == b"de"

    def test_seek_relative(self):
        f = _MemoryViewFile(b"abcdef")
        f.seek(2)
        f.seek(1, 1)  # relative +1
        assert f.tell() == 3
        assert f.read(1) == b"d"

    def test_seek_from_end(self):
        data = b"abcdef"
        f = _MemoryViewFile(data)
        f.seek(-2, 2)
        assert f.tell() == 4
        assert f.read() == b"ef"

    def test_seek_clamp_negative(self):
        f = _MemoryViewFile(b"abc")
        pos = f.seek(-100, 0)
        assert pos == 0
        assert f.tell() == 0

    def test_seek_clamp_past_end(self):
        f = _MemoryViewFile(b"abc")
        pos = f.seek(100, 0)
        assert pos == 3
        assert f.tell() == 3

    def test_readline(self):
        data = b"line1\nline2\nline3"
        f = _MemoryViewFile(data)
        assert f.readline() == b"line1\n"
        assert f.readline() == b"line2\n"
        assert f.readline() == b"line3"

    def test_readline_no_newline(self):
        data = b"no newline here"
        f = _MemoryViewFile(data)
        assert f.readline() == data

    def test_readline_empty(self):
        f = _MemoryViewFile(b"")
        assert f.readline() == b""

    def test_empty_buffer(self):
        f = _MemoryViewFile(b"")
        assert f.read() == b""
        assert f.tell() == 0

    def test_memoryview_input(self):
        """_MemoryViewFile must work with both bytes and memoryview."""
        data = b"hello memoryview"
        mv = memoryview(data)
        f = _MemoryViewFile(mv)
        assert f.read(5) == b"hello"
        f.seek(0)
        assert f.read() == data

    def test_close_is_noop(self):
        f = _MemoryViewFile(b"data")
        f.close()  # should not raise
        # Still readable after close (matches BytesIO behavior for our use)
        f.seek(0)
        assert f.read() == b"data"

    def test_pickle_load(self):
        """StructFile.read_pickle uses pickle.load(self.file) directly."""
        obj = {"key": [1, 2, 3], "nested": {"a": "b"}}
        data = pickle.dumps(obj)
        f = _MemoryViewFile(data)
        result = pickle.load(f)
        assert result == obj

    def test_struct_unpack_pattern(self):
        """StructFile read methods use self.file.read(n) + struct.unpack."""
        value = 42
        data = struct.pack(">I", value)
        f = _MemoryViewFile(data)
        raw = f.read(4)
        assert struct.unpack(">I", raw)[0] == value


class TestBufferFileMonkeyPatch:
    """Verify that the BufferFile monkey-patch is active."""

    def test_bufferfile_uses_memoryview_file(self):
        from whoosh.filedb.structfile import BufferFile
        data = b"test data for buffer file"
        bf = BufferFile(data, name="test")
        assert isinstance(bf.file, _MemoryViewFile)

    def test_bufferfile_read(self):
        from whoosh.filedb.structfile import BufferFile
        data = b"abcdefgh"
        bf = BufferFile(data, name="test")
        assert bf.read(4) == b"abcd"
        assert bf.read(4) == b"efgh"

    def test_bufferfile_seek_tell(self):
        from whoosh.filedb.structfile import BufferFile
        data = b"abcdefgh"
        bf = BufferFile(data, name="test")
        bf.seek(4)
        assert bf.tell() == 4
        assert bf.read(2) == b"ef"

    def test_bufferfile_get(self):
        """BufferFile.get() reads directly from _buf, not via self.file."""
        from whoosh.filedb.structfile import BufferFile
        data = b"abcdefgh"
        bf = BufferFile(data, name="test")
        assert bf.get(2, 3) == b"cde"

    def test_bufferfile_with_memoryview(self):
        from whoosh.filedb.structfile import BufferFile
        data = b"hello world from memoryview"
        mv = memoryview(data)
        bf = BufferFile(mv, name="test")
        assert bf.read(5) == b"hello"
        bf.seek(6)
        assert bf.read(5) == b"world"

    def test_no_bytesio_copy(self):
        """Verify that the patched BufferFile does NOT create a BytesIO."""
        from whoosh.filedb.structfile import BufferFile
        data = b"x" * 1000
        bf = BufferFile(data, name="test")
        assert not isinstance(bf.file, BytesIO)
        assert isinstance(bf.file, _MemoryViewFile)
