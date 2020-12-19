# coding: utf-8

"""
This is a test module for alfanous.Searching

"""
from alfanous.indexing import QseDocIndex
from alfanous.searching import QReader

def test_searching():
    index = QseDocIndex( "alfanous/indexes/main/" )
    reader = QReader( index )
    assert list(reader.list_terms( "sura_name" ))[:10] == []

