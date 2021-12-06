
"""
This is a test module for alfanous.Searching

"""
from alfanous import paths
from alfanous.indexing import QseDocIndex
from alfanous.searching import QReader

def test_searching():
    index = QseDocIndex( paths.QSE_INDEX )
    reader = QReader( index )
    assert list(reader.list_terms( "sura_name" ))[:10] == []

