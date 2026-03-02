
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
    # chapters, topics, subtopics should return full phrases, not single-word tokens
    chapters = QSE.list_stored_values("chapter")
    assert any(' ' in c for c in chapters), "chapters should contain multi-word phrases"
    topics = QSE.list_stored_values("topic")
    assert any(' ' in t for t in topics), "topics should contain multi-word phrases"


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


def _qse_search(query, **kwargs):
    """Helper: run a QSE search and return result count."""
    results, _terms, _searcher = QSE.search_all(
        query, limit=6236, sortedby="score", reverse=True, **kwargs
    )
    return len(results)


def test_advanced_search_exact():
    """1. Exact search — simple word lookup."""
    assert _qse_search(u"رب") == 126
    assert _qse_search(u"فأسقيناكموه") == 1


def test_advanced_search_phrase():
    """2. Phrase search — quoted exact multi-word sequence."""
    assert _qse_search(u'"رب العالمين"') == 34
    assert _qse_search(u'"رسول الله"') == 17


def test_advanced_search_logical_relations():
    """3. Logical relations — AND (+), OR (|), Arabic و / أو."""
    and_results = _qse_search(u"الصلاة + الزكاة")
    assert and_results == _qse_search(u"الصلاة AND الزكاة")
    assert and_results < _qse_search(u"الصلاة OR الزكاة")

    or_results = _qse_search(u"سميع | بصير")
    assert or_results == _qse_search(u"سميع OR بصير")

    # Arabic operator keywords
    assert _qse_search(u"الصلاة و الزكاة") == and_results
    assert _qse_search(u"سميع أو بصير") == or_results


def test_advanced_search_wildcards():
    """4. Wildcards — * for any chars, ؟ for single char."""
    assert _qse_search(u"*نبي*") == 76
    assert _qse_search(u"نعم؟") == 30


def test_advanced_search_fields():
    """5. Fields — Arabic field name followed by colon."""
    # سورة:يس  →  sura_arabic:يس  (Surah Ya-Sin, 83 verses)
    assert _qse_search(u"سورة:يس") == 83
    # سجدة:نعم  →  sajda:نعم  (14 prostration verses)
    assert _qse_search(u"سجدة:نعم") == 14


def test_advanced_search_intervals():
    """6. Intervals — numeric range with Arabic keyword الى."""
    range_only = _qse_search(u"رقم_السورة:[1 الى 5]")
    assert range_only == 789  # verses in suras 1–5

    # Combined with AND: only those verses that also contain الله
    combined = _qse_search(u"رقم_السورة:[1 الى 5] + الله")
    assert 0 < combined < range_only


def test_advanced_search_partial_vocalization():
    """7. Partial vocalization (tashkil) — single-quoted words with diacritics."""
    # 'مَن' — all verses containing the base word من
    results = _qse_search(u"'مَن'")
    assert results > 0

    # Explicit field: آية_:'الْمَلكُ'  →  aya_:الملك  (verses with الملك)
    results_field = _qse_search(u"آية_:'الْمَلكُ'")
    assert results_field > 0


def test_advanced_search_word_properties():
    """8. Word properties — tuple {root,type} morphological search.

    The matched derivation words must also be returned as keyword terms so
    that callers can highlight them in the result text.
    """
    # {قول،اسم} — 11 noun derivations of قول, present in 59 verses
    results, terms, _searcher = QSE.search_all(u"{قول،اسم}", limit=6236, sortedby="score", reverse=True)
    assert len(results) == 59
    term_words = [t[1] for t in terms]
    assert len(term_words) == 11
    assert "قول" in term_words
    assert "قولا" in term_words
    assert "الأقاويل" in term_words

    # {ملك،فعل} — verbs with root ملك, present in 42 verses
    results2, terms2, _searcher2 = QSE.search_all(u"{ملك،فعل}", limit=6236, sortedby="score", reverse=True)
    assert len(results2) == 42
    term_words2 = [t[1] for t in terms2]
    assert len(term_words2) == 8
    assert "يملك" in term_words2


def test_advanced_search_derivations():
    """9. Derivations — > (lemma level) and >> (root level)."""
    lemma_results = _qse_search(u">ملك")
    root_results = _qse_search(u">>ملك")
    assert lemma_results == 179
    assert root_results == 117


def test_advanced_search_buckwalter():
    """10. Buckwalter transliteration — Latin ASCII input converted to Arabic."""
    from alfanous.romanization import transliterate

    def bw_search(q):
        arabic_q = transliterate("buckwalter", q, ignore="'_\"%*?#~[]{}:>+-|")
        return _qse_search(arabic_q)

    assert bw_search("qawol") == 12    # قول
    assert bw_search("Allah") == 1566  # الله
