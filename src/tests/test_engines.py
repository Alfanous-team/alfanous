
"""
This is a test module for most of features provided by alfanous.engines module.

"""

from alfanous.engines import QuranicSearchEngine
from alfanous.engines import TraductionSearchEngine
from alfanous.engines import WordSearchEngine
from alfanous import paths


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
    assert list(QSE.suggest_all(u"النسر").items()) == [('النسر', ['النار', 'النور', 'النذر'])]


def test_autocomplete():
    assert QSE.autocomplete("رسول") == {'base': '',
 'completion': ['رسول',
                'رسولا',
                'رسولكم',
                'رسولنا',
                'رسوله',
                'رسولها',
                'رسولهم']}


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
    assert [ item[0] for item in results.key_terms("aya", docs=1, numterms=15)] == ['الأمل', 'ويتمتعوا', 'ويلههم', 'يأكلوا', 'ذرهم', 'فسوف', 'يعلمون']

    assert terms[0][:2] == ('aya', u'\u0627\u0644\u0623\u0645\u0644')
    assert dict(results[0]) == {'a_g': 0,
                                'a_l': 39,
                                'a_w': 7,
                                'aya': 'ذرهم يأكلوا ويتمتعوا ويلههم الأمل فسوف يعلمون',
                                'aya_': 'ذَرْهُمْ يَأْكُلُوا وَيَتَمَتَّعُوا وَيُلْهِهِمُ الْأَمَلُ فَسَوْفَ '
                                        'يَعْلَمُونَ',
                                'aya_id': 3,
                                'chapter': 'الأخلاق المذمومة ',
                                'gid': 1805,
                                'hizb': 27,
                                'juz': 14,
                                'manzil': 3,
                                'nisf': 53,
                                'page': 262,
                                'page_IN': 365,
                                'rub': 105,
                                'ruk': 218,
                                's_a': 99,
                                's_g': 2,
                                's_l': 2829,
                                's_r': 6,
                                's_w': 654,
                                'sajda': 'لا',
                                'subject': 'الأخلاق المذمومة ,الانشغال بشهوات الدنيا,',
                                'subtopic': '',
                                'sura': 'Al-Hijr',
                                'sura_arabic': 'الحجر',
                                'sura_english': 'The Stoneland',
                                'sura_id': 15,
                                'sura_order': 54,
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
    assert {'en.shakir', 'en.transliteration'} & set(TSE.list_values("id"))

def test_word_engine():
    """Test that word search engine is initialized correctly"""
    assert WSE.OK


def test_word_search_by_id():
    """Test searching for a specific word by ID"""
    results, terms, searcher = WSE.search_all("word_id:1",
                                               limit=100,
                                               sortedby="score",
                                               reverse=True)
    assert len(results) > 0
    assert results[0]['word_id'] == 1
    # Verify search terms are returned
    assert len(terms) > 0
    # Verify searcher is returned
    assert searcher is not None


def test_word_search_by_lemma():
    """Test searching for words by their lemma (root form)"""
    results, terms, searcher = WSE.search_all("lemma:أب",
                                               limit=100,
                                               sortedby="score",
                                               reverse=True)
    assert len(results) > 0
    # Verify all results have the correct lemma (keyword field should match exactly)
    assert all(result.get('lemma') == 'أب' for result in results)


def test_word_search_by_type():
    """Test searching for words by their grammatical type"""
    results, terms, searcher = WSE.search_all("type:اسم",
                                               limit=100,
                                               sortedby="score",
                                               reverse=True)
    assert len(results) > 0
    # Verify all results have the correct type (keyword field should match exactly)
    assert all(result.get('type') == 'اسم' for result in results)


def test_word_list_types():
    """Test listing all grammatical types in the word index"""
    types = list(WSE.list_values("type"))
    assert len(types) > 0
    # Common Arabic grammatical types should be present
    assert 'اسم' in types
