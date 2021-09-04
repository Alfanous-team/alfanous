# coding: utf-8

"""
This is a test module for most of features provided by alfanous.engines module.

"""
import profile

from alfanous.engines import QuranicSearchEngine
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
    print("\n#most frequent words#")
    most_frequent_words = QSE.most_frequent_words(9999999, "aya_")
    assert len(most_frequent_words) == 17574
    assert most_frequent_words[0:5] == [(1673.0, 'مِنْ'),
                                        (1185.0, 'فِي'),
                                        (1010.0, 'مَا'),
                                        (828.0, 'اللَّهِ'),
                                        (812.0, 'لَا')]


def test_list_values():
    assert QSE.list_values("sura_id") == list(range(1, 114 + 1))
    assert len(list(QSE.list_values("gid"))) == 6236


def test_missing_suggetion():
    assert QSE.suggest_all(u"النسر").items() == [('\u0627\u0644\u0646\u0633\u0631',
                                                  ['\u0627\u0644\u0646\u0648\u0631',
                                                   '\u0627\u0644\u0646\u0635\u0631',
                                                   '\u0627\u0644\u0646\u0630\u0631'])]


def test_autocomplete():
    assert QSE.autocomplete(u"رسول") == []


def test_search():
    QUERY1 = "الأمل"
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
    assert results.key_terms("aya", docs=1, numterms=15) == [('الأمل', 0.12383807073722287),
                                                             ('ويتمتعوا', 0.12383807073722287),
                                                             ('ويلههم', 0.12383807073722287),
                                                             ('يأكلوا', 0.12383807073722287),
                                                             ('ذرهم', 0.1131763058235371),
                                                             ('فسوف', 0.07387262366619061),
                                                             ('يعلمون', 0.05660024365436764)]

    assert terms == [('aya', u'\u0627\u0644\u0623\u0645\u0644', 2.0, 1)]
    assert dict(results[0]) == {'a_l': '39',
                                'a_w': '7',
                                'aya': 'ذرهم يأكلوا ويتمتعوا ويلههم الأمل فسوف يعلمون',
                                'aya_': 'ذَرْهُمْ يَأْكُلُوا وَيَتَمَتَّعُوا وَيُلْهِهِمُ الْأَمَلُ فَسَوْفَ '
                                        'يَعْلَمُونَ',
                                'aya_id': '3',
                                'chapter': 'الأخلاق المذمومة ',
                                'gid': '1805',
                                'hizb': '27',
                                'juz': '14',
                                'manzil': '3',
                                'nisf': '53',
                                'page': '262',
                                'page_IN': '365',
                                'rub': '105',
                                'ruku': '218',
                                's_a': '99',
                                's_g': '2',
                                's_l': '2829',
                                's_r': '6',
                                's_w': '654',
                                'sajda': 'لا',
                                'sura': 'Al-Hijr',
                                'sura_arabic': 'الحجر',
                                'sura_english': 'The Stoneland',
                                'sura_id': '15',
                                'sura_order': '54',
                                'sura_type': 'Meccan',
                                'sura_type_arabic': 'مكية',
                                'topic': 'الانشغال بشهوات الدنيا',
                                'uth': 'ذَرهُم يَأكُلوا وَيَتَمَتَّعوا وَيُلهِهِمُ الأَمَلُ فَسَوفَ يَعلَمونَ',
                                'uth_': 'ذَرْهُمْ يَأْكُلُوا۟ وَيَتَمَتَّعُوا۟ وَيُلْهِهِمُ ٱلْأَمَلُ ۖ '
                                        'فَسَوْفَ يَعْلَمُونَ'}


def test_translation_engine():
    assert TSE.OK

    results, searcher = TSE.find_extended(u"gid:1 OR gid:2", defaultfield="gid")
    assert len(results)
    assert set(TSE.list_values("id")) == {'en.shakir', 'en.transliteration'}

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
