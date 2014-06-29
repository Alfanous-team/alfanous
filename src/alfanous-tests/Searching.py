# coding: utf-8

"""
This is a test module for alfanous.Searching

"""

from alfanous.Searching import QseDocIndex, QuranicParser, QSearcher, QReader

if __name__ == "__main__":
    D = QseDocIndex( "../alfanous/indexes/main/" )
    S = QSearcher( D, QuranicParser( D.get_schema() ) )

    R = QReader( D )
    print ",".join( [str( val ) for val in R.list_terms( "sura_name" )][:10] )

