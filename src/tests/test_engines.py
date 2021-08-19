# coding: utf-8

"""
This is a test module for most of features provided by alfanous.engines module.

"""
import profile

from alfanous.engines import QuranicSearchEngine, FuzzyQuranicSearchEngine
from alfanous.engines import TraductionSearchEngine
from alfanous.engines import WordSearchEngine
from alfanous import paths

from alfanous.results_processing import QPaginate

QSE = QuranicSearchEngine(paths.QSE_INDEX)
TSE = TraductionSearchEngine(paths.TSE_INDEX)
WSE = WordSearchEngine(paths.WSE_INDEX)


def test_aya_engine():
    assert QSE.OK


def test_most_frequent_words():
    print "\n#most frequent words#"
    MFW = QSE.most_frequent_words(9999999, "uth_")
    assert len(MFW) == 19003
    assert MFW[0:5] == [(1972, u'\u06da'),
                        (1682, u'\u06d6'),
                        (1098, u'\u0641\u0650\u0649'),
                        (828, u'\u0627\u0644\u0644\u0651\u064e\u0647\u0650'),
                        (810, u'\u0627\u0644\u0651\u064e\u0630\u0650\u064a\u0646\u064e')]


def test_list_values():
    assert len(list(QSE.list_values("gid"))) == 6236


def test_missing_suggetion():
    assert QSE.suggest_all(u"النسر").items() == [(u'\u0627\u0644\u0646\u0633\u0631',
                                                  [u'\u0627\u0644\u0646\u0648\u0631',
                                                   u'\u0627\u0644\u0646\u0635\u0631',
                                                   u'\u0627\u0644\u0646\u0630\u0631'])]

def test_autocomplete():
    assert QSE.autocomplete(u"رسول") == []


def test_search():
    QUERY1 = ">>الأمل"
    results, terms, searcher = QSE.search_all(QUERY1,
                                              limit=6236,
                                              sortedby="score",
                                              reverse=True)

    # %المأصدة
    # لله
    # ال*لك
    # رب
    # "رسول * الله"
    # الصلاة وليس الزكاة
    # #السعير
    # ~السعير
    # نعمت
    # رقم_السورة:[1 الى 5] و الله
    # آية_:'مَن '
    # {ملك,فعل}
    # >>سماكم
    # >سماكم
    # سماكم
    # سجدة:نعم
    # fawoqa
    # \" رب العالمين\"
    # جزء:8

    assert results.runtime < 0.1
    assert len(results) == 1


    assert results.key_terms("aya", docs=1, numterms=15000) == [
        (u'\u064a\u0623\u0643\u0644\u0648\u0627', 0.11168926447286792),
        (u'\u0648\u064a\u0644\u0647\u0647\u0645', 0.11168926447286792),
        (u'\u0648\u064a\u062a\u0645\u062a\u0639\u0648\u0627', 0.11168926447286792),
        (u'\u0627\u0644\u0623\u0645\u0644', 0.11168926447286792),
        (u'\u0630\u0631\u0647\u0645', 0.10283396436843649),
        (u'\u0641\u0633\u0648\u0641', 0.07014845617722199),
        (u'\u064a\u0639\u0644\u0645\u0648\u0646', 0.05569502613635983)]

    assert terms == [('aya', u'\u0627\u0644\u0623\u0645\u0644', 1, 1)]

def test_translation_engine():
    assert TSE.OK

    results, searcher = TSE.find_extended(u"gid:1 OR gid:2", defaultfield="gid")
    assert len(results)
    assert set(TSE.list_values("id")) == {u'en.shakir', u'en.transliteration'}



# def test_word_engine():
#     assert WSE.OK
#     MFW = WSE.most_frequent_words(10, "word")
#     assert MFW == {}
#     for term in MFW:
#         print "\t", term[1], " - frequence = ", term[0], "."
#     print "most  frequent unvocalized words"
#     MFW = WSE.most_frequent_words(10, "normalized")
#     for term in MFW:
#         print "\t", term[1], " - frequence = ", term[0], "."
#
#     RESULTS, TERMS = WSE.search_all("word_id:1",
#                                      limit=6236,
#                                      sortedby="score",
#                                      reverse=True)
#     print len(RESULTS)
#
#     print "\n#list field stored VALUES# type"
#     print ",".join([str(item) for item in WSE.list_values("type")])
