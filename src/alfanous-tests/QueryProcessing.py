# coding: utf-8

from alfanous.QueryProcessing import *

if __name__ == "__main__":
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
