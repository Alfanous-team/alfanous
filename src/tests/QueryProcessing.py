# coding: utf-8

"""
This is a test module for alfanous.QueryProcessing 

"""

from alfanous.query_processing import _make_arabic_parser
from alfanous.query_processing import QseDocIndex
from alfanous.query_processing import FuzzyQuranicParser



if __name__ == "__main__":
    parse = _make_arabic_parser()

    print parse( u"\"عاصم\"" )
    print parse( u"[1 الى 3]" )
    print parse( u"{a,b،c}" )
    print parse( u"#122 ~dsd" )
    print parse( u">>اية" )
    print parse( u"%عاصم" )
    print parse( u"ليس عاصم و الموت أو الحياة وليس غيرهما" )
    print parse( u"اية:عاصم" )
    print parse( u"'h h  j'" )
    print parse( u"a*a" )
    print parse( u"a*" )
    
    D = QseDocIndex( "../alfanous/indexes/main/" )
    QP = FuzzyQuranicParser( D.get_schema(), otherfields = ['subject'] )

    print QP.parse( u"'لو كان البحر '" )
    print QP.parse( u"\"عاصم\"" )
    print QP.parse( u"[1 الى 3]" )
    print QP.parse( u"{ملك,فعل}" )
    print QP.parse( u"#122 ~dsd" )
    print QP.parse( u">>سماكم" )
    print QP.parse( u"%عاصم" )
    print QP.parse( u"ليس عاصم و الموت أو الحياة وليس غيرهما" )
    print QP.parse( u"آية:عاصم" )
    print QP.parse( u"'h h  j'" )
    print QP.parse( u"a*a" )
    print QP.parse( u"b*" )
    print QP.parse( u"*" )
