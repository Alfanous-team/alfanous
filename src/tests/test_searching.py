
"""
This is a test module for alfanous.Searching

"""
import os
import pytest
from alfanous import paths
from alfanous.indexing import QseDocIndex
from alfanous.searching import QReader

def test_searching():
    if not os.path.isdir(paths.QSE_INDEX) or not QseDocIndex(paths.QSE_INDEX).OK:
        pytest.skip("Search index not built — run `make build` first")
    index = QseDocIndex( paths.QSE_INDEX )
    reader = QReader( index )
    assert list(reader.list_values( "sura_name" ))[:10] == []

