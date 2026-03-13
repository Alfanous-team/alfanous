"""
Tests for alfanous.indexing — focusing on robust error handling during
index load, including the UnpicklingError that arises when the TOC
schema section contains zlib-compressed (``\\x78``-prefixed) bytes.
"""

import os
import pickle
import zlib

import pytest

from whoosh import index as whoosh_index
from whoosh.fields import Schema, TEXT, ID
from whoosh.filedb.structfile import StructFile
from whoosh.util.varints import varint
from whoosh.system import _INT_SIZE, _LONG_SIZE, _FLOAT_SIZE

from alfanous.indexing import BasicDocIndex


# ---------------------------------------------------------------------------
# Helpers to construct fake Whoosh index directories
# ---------------------------------------------------------------------------

def _write_valid_toc_prefix(f):
    """Write the fixed-size header bytes of a Whoosh v-111 TOC file.

    Writes everything up to (but not including) the schema bytes so that
    tests can substitute different schema payloads.
    """
    sf = StructFile(f)
    sf.write(varint(_INT_SIZE))    # int size (4)
    sf.write(varint(_LONG_SIZE))   # long size (8)
    sf.write(varint(_FLOAT_SIZE))  # float size (4)
    sf.write_int(-12345)           # architecture check
    sf.write_int(-111)             # _CURRENT_TOC_VERSION
    sf.write(varint(2))            # Whoosh major
    sf.write(varint(7))            # Whoosh minor
    sf.write(varint(4))            # Whoosh patch


def _write_toc_suffix(f):
    """Write the generation counter, unused int and empty segment list."""
    sf = StructFile(f)
    sf.write_int(1)                      # index generation
    sf.write_int(0)                      # unused slot
    sf.write(pickle.dumps([], 2))        # empty segment list


def _make_corrupt_index(directory, schema_payload: bytes):
    """Create a minimal fake Whoosh index whose schema section is *schema_payload*.

    The generation is set to 1 so Whoosh's ``exists_in`` / ``TOC.read``
    finds and tries to load the file.
    """
    toc_path = os.path.join(directory, "_MAIN_1.toc")
    with open(toc_path, "wb") as f:
        _write_valid_toc_prefix(f)
        # write_string: varint length + raw bytes
        sf = StructFile(f)
        sf.write(varint(len(schema_payload)))
        sf.write(schema_payload)
        _write_toc_suffix(f)
    return directory


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestBasicDocIndexLoadErrors:
    """BasicDocIndex.load() must return ok=False (not raise) for bad indexes."""

    def test_unpickling_error_sets_ok_false(self, tmp_path):
        """UnpicklingError: invalid load key, 'x' must not propagate."""
        # The schema payload is zlib-compressed data (starts with 0x78).
        # When pickle.loads() receives this, it raises:
        #   UnpicklingError: invalid load key, 'x'.
        corrupt_schema = zlib.compress(b"this is definitely not a pickle stream")
        _make_corrupt_index(str(tmp_path), corrupt_schema)

        idx = BasicDocIndex(str(tmp_path))

        assert not idx.OK, "OK must be False when the index is corrupt"
        assert idx._ix is None, "_ix must be None when loading failed"

    def test_unpickling_error_is_logged(self, tmp_path, caplog):
        """A clear error message must be logged when UnpicklingError is raised."""
        import logging

        corrupt_schema = zlib.compress(b"not a pickle")
        _make_corrupt_index(str(tmp_path), corrupt_schema)

        with caplog.at_level(logging.ERROR, logger="alfanous.indexing"):
            BasicDocIndex(str(tmp_path))

        assert any(
            "corrupted" in record.message.lower()
            or "incompatible" in record.message.lower()
            or "unpickling" in record.message.lower()
            or "invalid load key" in record.message.lower()
            for record in caplog.records
        ), "Expected an error log mentioning corruption or the UnpicklingError"

    def test_missing_index_dir_is_ok_false(self, tmp_path):
        """Pointing at a non-existent path must give OK=False without errors."""
        idx = BasicDocIndex(str(tmp_path / "does_not_exist"))
        assert not idx.OK

    def test_empty_index_dir_is_ok_false(self, tmp_path):
        """An empty directory (no .toc file) must give OK=False."""
        idx = BasicDocIndex(str(tmp_path))
        assert not idx.OK

    def test_valid_index_loads(self, tmp_path):
        """A properly-built index must load with OK=True.

        This test is skipped when the real QSE index is not available so it
        does not require ``make build`` to run.
        """
        schema = Schema(id=ID(stored=True), body=TEXT)
        ix = whoosh_index.create_in(str(tmp_path), schema)
        w = ix.writer()
        w.add_document(id="1", body="hello world")
        w.commit()
        ix.close()

        idx = BasicDocIndex(str(tmp_path))
        assert idx.OK, "A valid index must load with OK=True"
