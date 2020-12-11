# coding: utf-8

"""
This is a test module for alfanous.QueryProcessing 

"""

from alfanous.query_processing import _make_arabic_parser
from alfanous.indexing import QseDocIndex
from alfanous.query_processing import FuzzyQuranicParser



if __name__ == "__main__":
    parse = _make_arabic_parser()

    print(parse( "\"عاصم\"" ))
    print(parse( "[1 الى 3]" ))
    print(parse( "{a,b،c}" ))
    print(parse( "#122 ~dsd" ))
    print(parse( ">>اية" ))
    print(parse( "%عاصم" ))
    print(parse( "ليس عاصم و الموت أو الحياة وليس غيرهما" ))
    print(parse( "اية:عاصم" ))
    print(parse( "'h h  j'" ))
    print(parse( "a*a" ))
    print(parse( "a*" ))
    
    D = QseDocIndex( "../alfanous/indexes/main/" )
    QP = FuzzyQuranicParser( D.get_schema(), otherfields = ['subject'] )

    print(QP.parse( "'لو كان البحر '" ))
    print(QP.parse( "\"عاصم\"" ))
    print(QP.parse( "[1 الى 3]" ))
    print(QP.parse( "{ملك,فعل}" ))
    print(QP.parse( "#122 ~dsd" ))
    print(QP.parse( ">>سماكم" ))
    print(QP.parse( "%عاصم" ))
    print(QP.parse( "ليس عاصم و الموت أو الحياة وليس غيرهما" ))
    print(QP.parse( "آية:عاصم" ))
    print(QP.parse( "'h h  j'" ))
    print(QP.parse( "a*a" ))
    print(QP.parse( "b*" ))
    print(QP.parse( "*" ))
