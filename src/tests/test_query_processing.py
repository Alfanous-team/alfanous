# coding: utf-8

"""
This is a test module for alfanous.QueryProcessing 

"""
from alfanous import paths
from alfanous.indexing import QseDocIndex
from alfanous.query_processing import _make_arabic_parser, QuranicParser


def test_parsing():
    parse = _make_arabic_parser()

    assert parse(u"\"عاصم\"")
    assert parse(u"[1 الى 3]")
    assert parse(u"{a,b،c}")
    assert parse(u"#122 ~dsd")
    assert parse(u">>اية")
    assert parse(u"%عاصم")
    assert parse(u"ليس عاصم و الموت أو الحياة وليس غيرهما")
    assert parse(u"اية:عاصم")\

    assert parse(u"'h h  j'")
    assert parse(u"a*a")
    assert parse(u"a*")


def test_parsing_with_schema():
    D = QseDocIndex(paths.QSE_INDEX)
    QP = QuranicParser(D.get_schema(), otherfields=['subject'])

    assert QP.parse(u"'لو كان البحر '").__dict__ == {'boost': 1.0,
                                                     'fieldname': 'aya',
                                                     'text': [u'\u0644\u0648',
                                                              u'\u0643\u0627\u0646',
                                                              u'\u0627\u0644\u0628\u062d\u0631'],
                                                     'words': [u'\u0644\u0648',
                                                               u'\u0643\u0627\u0646',
                                                               u'\u0627\u0644\u0628\u062d\u0631']} != [u'\u0644\u0648',
                                                                                                       u'\u0643\u0627\u0646',
                                                                                                       u'\u0627\u0644\u0628\u062d\u0631']
    assert QP.parse(u"\"عاصم\"").__dict__ == {'boost': 1.0, 'fieldname': 'aya', 'text': u'\u0639\u0627\u0635\u0645'}
    assert QP.parse(u"[1 الى 3]").__dict__ == {'boost': 1.0,
                                               'end': u'3',
                                               'endexcl': False,
                                               'fieldname': 'aya',
                                               'start': u'1',
                                               'startexcl': False}
    assert QP.parse(u"{ملك,فعل}").__dict__ == {'boost': 1.0,
                                               'fieldname': 'aya',
                                               'props': {'root': u'\u0645\u0644\u0643', 'type': u'\u0641\u0639\u0644'},
                                               'text': u'(\u0645\u0644\u0643,\u0641\u0639\u0644)',
                                               'words': [u'\u0645\u0644\u0643\u062a\u0645',
                                                         u'\u0623\u0645\u0644\u0643',
                                                         u'\u0645\u0644\u0643\u062a',
                                                         u'\u064a\u0645\u0644\u0643',
                                                         u'\u062a\u0645\u0644\u0643\u0648\u0646',
                                                         u'\u062a\u0645\u0644\u0643',
                                                         u'\u064a\u0645\u0644\u0643\u0648\u0646',
                                                         u'\u062a\u0645\u0644\u0643\u0647\u0645']}
    assert QP.parse(u"#جحيم").__dict__ == {'boost': 1.0,
                                           'fieldname': 'aya',
                                           'text': u'\u062c\u062d\u064a\u0645',
                                           'words': [u'\u062c\u062d\u064a\u0645']}

    assert QP.parse(u"~جحيم").__dict__ == {'boost': 1.0,
                                           'fieldname': 'aya',
                                           'text': u'\u062c\u062d\u064a\u0645',
                                           'words': [u'\u062c\u062d\u064a\u0645']}

    assert QP.parse(u">>سماكم").__dict__ == {'boost': 1.0,
 'fieldname': 'aya',
 'text': u'\u0633\u0645\u0627\u0643\u0645',
 'words': [u'\u0628\u0623\u0633\u0645\u0627\u0621',
           u'\u062a\u0633\u0645\u0649',
           u'\u0628\u0623\u0633\u0645\u0627\u0626\u0647\u0645',
           u'\u0648\u0627\u0644\u0633\u0645\u0627\u0621',
           u'\u0627\u0633\u0645\u0647',
           u'\u0628\u0633\u0645',
           u'\u062a\u0633\u0645\u064a\u0629',
           u'\u0633\u0645\u064a\u062a\u0645\u0648\u0647\u0627',
           u'\u0628\u0627\u0633\u0645',
           u'\u0627\u0644\u0627\u0633\u0645',
           u'\u0633\u0645\u0627\u0643\u0645',
           u'\u0627\u0644\u0623\u0633\u0645\u0627\u0621',
           u'\u0633\u0645\u0627\u0648\u0627\u062a',
           u'\u0627\u0633\u0645',
           u'\u0644\u064a\u0633\u0645\u0648\u0646',
           u'\u0623\u0633\u0645\u0627\u0621',
           u'\u0633\u0645\u0648\u0647\u0645',
           u'\u0633\u0645\u064a\u062a\u0647\u0627',
           u'\u0633\u0645\u0627\u0621',
           u'\u0623\u0633\u0645\u0627\u0626\u0647',
           u'\u0627\u0644\u0633\u0645\u0627\u0621']}

    assert QP.parse(u"آية:عاصم").__dict__ == {'boost': 1.0, 'fieldname': u'aya', 'text': u'\u0639\u0627\u0635\u0645'}
    assert QP.parse(u"'h h  j'").__dict__ == dict(boost=1.0, fieldname='aya', text=[u'h', u'h', u'j'],
                                                  words=[u'h', u'h', u'j'])
    assert QP.parse(u"*").__dict__ == {'boost': 1.0}
    assert QP.parse(u"%عاصم").words == [u'عاصم']
    assert QP.parse(u"ليس عاصم و الموت أو الحياة وليس غيرهما").__dict__
    assert QP.parse(u"a*a").prefix == 'a'
    assert QP.parse(u"b*").text == 'b'