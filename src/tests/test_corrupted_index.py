"""
Regression tests for graceful handling of corrupted / truncated Whoosh indexes.

The error "Error -5 while decompressing data: incomplete or truncated stream"
(zlib.error, code -5) is raised when Whoosh tries to decompress stored field
data that has been written incompletely (e.g. the process was killed mid-build
or the disk ran out of space).

These tests verify that:
 1. BasicDocIndex.load() returns OK=False instead of raising an exception when
    the index directory exists but the files are corrupted.
 2. QReader.list_stored_values() returns an empty / partial list instead of
    propagating zlib.error or struct.error to the caller.
"""

import os
import struct
import tempfile
import zlib
from unittest.mock import MagicMock, patch

import pytest

from alfanous.indexing import BasicDocIndex, QseDocIndex
from alfanous.searching import QReader, _INDEX_DATA_ERRORS


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_minimal_index(tmpdir):
    """Build a tiny but valid Whoosh index in *tmpdir* and return it."""
    from whoosh.filedb.filestore import FileStorage
    from whoosh.fields import Schema, TEXT, STORED, ID

    schema = Schema(kind=ID(stored=True), content=TEXT(stored=True))
    ix = FileStorage(tmpdir).create_index(schema)
    w = ix.writer()
    w.add_document(kind="aya", content="test content")
    w.commit()
    return ix


# ---------------------------------------------------------------------------
# BasicDocIndex.load() – corrupted index files
# ---------------------------------------------------------------------------

class TestBasicDocIndexLoadCorrupted:
    """BasicDocIndex.load() must never raise; it must return OK=False."""

    def test_load_returns_false_on_corrupted_files(self, tmp_path):
        """Corrupting every file in the index dir must set OK=False."""
        index_dir = str(tmp_path / "main")
        os.makedirs(index_dir)
        _make_minimal_index(index_dir)

        # Overwrite all files with garbage to simulate disk corruption.
        for fname in os.listdir(index_dir):
            fpath = os.path.join(index_dir, fname)
            if os.path.isfile(fpath):
                with open(fpath, "wb") as fh:
                    fh.write(b"\x00\xff" * 32)

        # Should not raise — must degrade gracefully.
        doc_index = BasicDocIndex(index_dir)
        assert doc_index.OK is False

    def test_load_returns_false_on_truncated_index_state(self, tmp_path):
        """A truncated _INDEXSTATE file must set OK=False."""
        index_dir = str(tmp_path / "main")
        os.makedirs(index_dir)
        _make_minimal_index(index_dir)

        # Truncate the index state file (Whoosh reads it on open_index()).
        state_files = [
            f for f in os.listdir(index_dir)
            if f.startswith("_") or f.endswith(".toc")
        ]
        for fname in state_files:
            fpath = os.path.join(index_dir, fname)
            with open(fpath, "wb") as fh:
                fh.write(b"")  # zero-byte file = truncated

        doc_index = BasicDocIndex(index_dir)
        assert doc_index.OK is False

    def test_load_succeeds_on_valid_index(self, tmp_path):
        """A valid index must load with OK=True."""
        index_dir = str(tmp_path / "main")
        os.makedirs(index_dir)
        _make_minimal_index(index_dir)

        doc_index = BasicDocIndex(index_dir)
        assert doc_index.OK is True


# ---------------------------------------------------------------------------
# QReader.list_stored_values() – zlib / struct errors from stored fields
# ---------------------------------------------------------------------------

class TestListStoredValuesErrorHandling:
    """list_stored_values() must degrade gracefully on index data errors."""

    def _make_reader_with_zlib_error(self):
        """Return a QReader backed by a mock that raises zlib.error on read."""
        mock_docindex = MagicMock()
        qreader = QReader(mock_docindex)
        mock_reader = MagicMock()

        # postings() raises zlib.error to trigger the optimised-path exception.
        mock_reader.postings.side_effect = zlib.error("Error -5 while decompressing data")
        # iter_docs() also raises, to cover the fallback path.
        mock_reader.iter_docs.side_effect = zlib.error("Error -5 while decompressing data")

        qreader._own_reader = mock_reader
        return qreader

    def _make_reader_with_struct_error(self):
        """Return a QReader that raises struct.error from stored_fields()."""
        mock_docindex = MagicMock()
        qreader = QReader(mock_docindex)
        mock_reader = MagicMock()

        # postings() works but stored_fields() raises struct.error.
        mock_postings = MagicMock()
        mock_postings.is_active.side_effect = [True, False]
        mock_postings.id.return_value = 0
        mock_reader.postings.return_value = mock_postings
        mock_reader.stored_fields.side_effect = struct.error("unpack error")

        qreader._own_reader = mock_reader
        return qreader

    def test_zlib_error_in_optimised_path_returns_empty(self):
        """zlib.error in the optimised postings path returns []."""
        qreader = self._make_reader_with_zlib_error()
        result = qreader.list_stored_values("chapter")
        assert result == []

    def test_struct_error_in_stored_fields_returns_empty(self):
        """struct.error when reading stored_fields() returns []."""
        qreader = self._make_reader_with_struct_error()
        result = qreader.list_stored_values("chapter")
        assert result == []

    def test_zlib_error_in_fallback_iter_docs_returns_empty(self):
        """zlib.error in the iter_docs fallback returns []."""
        mock_docindex = MagicMock()
        qreader = QReader(mock_docindex)
        mock_reader = MagicMock()

        # postings() raises KeyError → triggers fallback
        mock_reader.postings.side_effect = KeyError("kind")
        # iter_docs() raises zlib.error in the fallback
        mock_reader.iter_docs.side_effect = zlib.error("Error -5")

        qreader._own_reader = mock_reader
        result = qreader.list_stored_values("chapter")
        assert result == []

    def test_index_data_errors_tuple_contains_expected_types(self):
        """_INDEX_DATA_ERRORS must include zlib.error, struct.error, EOFError, OSError."""
        assert zlib.error in _INDEX_DATA_ERRORS
        assert struct.error in _INDEX_DATA_ERRORS
        assert EOFError in _INDEX_DATA_ERRORS
        assert OSError in _INDEX_DATA_ERRORS
