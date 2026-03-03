
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
                                'chapter': 'الأخلاق المذمومة',
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


def test_advanced_search_arabizi():
    """10. Arabizi transliteration — Latin input expanded to Arabic candidates for QSE."""
    from alfanous.romanization import arabizi_to_arabic_list

    def arabizi_search(q):
        candidates = arabizi_to_arabic_list(q, ignore="'_\"%*?#~[]{}:>+-|")
        arabic_q = " ".join(candidates) if candidates else q
        return _qse_search(arabic_q)

    # Digit-based Arabizi: unambiguous phoneme representation
    assert arabizi_search("9br") > 0      # صبر (sabr/patience)
    assert arabizi_search("el 7md") > 0   # الحمد (al-hamd/praise)


def test_arabizi_transliteration():
    """11. Arabizi transliteration — generates a list of potential Arabic words."""
    from alfanous.romanization import arabizi_to_arabic_list

    # Number mappings: each digit maps to a single Arabic letter unambiguously
    assert u"\u062D" in arabizi_to_arabic_list("7")   # ح
    assert u"\u0639" in arabizi_to_arabic_list("3")   # ع
    assert u"\u0635" in arabizi_to_arabic_list("9")   # ص

    # Simple word without digraphs: only one result expected
    result_kitab = arabizi_to_arabic_list("ktab")   # كتاب
    assert u"\u0643\u062A\u0627\u0628" in result_kitab  # كتاب

    # Digraph "sh": generates two candidates (ش vs. س+ه)
    result_sh = arabizi_to_arabic_list("sh")
    assert u"\u0634" in result_sh          # ش  (digraph interpretation)
    assert u"\u0633\u0647" in result_sh    # سه (two-letter interpretation)
    assert len(result_sh) == 2

    # Digraph "th": generates two candidates (ث vs. ت+ه)
    result_th = arabizi_to_arabic_list("th")
    assert u"\u062B" in result_th          # ث  (digraph interpretation)
    assert u"\u062A\u0647" in result_th    # ته (two-letter interpretation)
    assert len(result_th) == 2

    # Word with digraph: "sha3b" → شاعب (sh=ش, a=ا, 3=ع, b=ب)
    #                         or  → سهاعب (s=س, h=ه, a=ا, 3=ع, b=ب)
    result_sha3b = arabizi_to_arabic_list("sha3b")
    assert u"\u0634\u0627\u0639\u0628" in result_sha3b   # شاعب
    assert u"\u0633\u0647\u0627\u0639\u0628" in result_sha3b  # سهاعب

    # Ignored characters are preserved unchanged
    result_ignore = arabizi_to_arabic_list("k*b", ignore="*")
    assert u"\u0643*\u0628" in result_ignore  # ك*ب

    # 'e' maps to ي (ya), NOT to ع — 'e' is a vowel sound in Arabizi;
    # ع is already covered by the digit '3'.
    assert u"\u064A" in arabizi_to_arabic_list("e")   # ي
    assert u"\u0639" not in arabizi_to_arabic_list("e")  # not ع

    # 'u' maps to و (waw) — e.g. "shu" → شو (or سهو)
    assert u"\u0648" in arabizi_to_arabic_list("u")   # و
    result_shu = arabizi_to_arabic_list("shu")
    assert u"\u0634\u0648" in result_shu   # شو (digraph sh + u→و)

    # Rule B: word-initial el/al → ال (Arabic definite article)
    assert u"\u0627\u0644" in arabizi_to_arabic_list("el")   # ال
    assert u"\u0627\u0644" in arabizi_to_arabic_list("al")   # ال
    # In a multi-word string, el- at the start of the second word also triggers Rule B
    result_el_7al = arabizi_to_arabic_list("el 7al")
    # At least one candidate must start with ال (definite article prefix)
    assert any(c.startswith(u"\u0627\u0644 ") for c in result_el_7al)  # 'ال حال' candidate

    # Rule C: gemination — doubled consonant → letter + shadda (ّ U+0651)
    result_ll = arabizi_to_arabic_list("ll")
    assert u"\u0644\u0651" in result_ll   # لّ (lam + shadda)
    result_tt = arabizi_to_arabic_list("tt")
    assert u"\u062A\u0651" in result_tt   # تّ (ta + shadda)
    # Doubled vowels are NOT geminated (vowels don't take shadda in Arabic)
    result_aa = arabizi_to_arabic_list("aa")
    assert u"\u0627\u0651" not in result_aa  # no shadda on alef

    # Rule D: digraph "eh" → ة (ta marbuta — common terminal feminine suffix)
    assert u"\u0629" in arabizi_to_arabic_list("eh")   # ة
    result_salameh = arabizi_to_arabic_list("salameh")
    assert any(c.endswith(u"\u0629") for c in result_salameh)  # at least one ends with ة

    # Rule D: terminal 'a' → also ى (alef maqsura)
    result_3la = arabizi_to_arabic_list("3la")
    assert any(c.endswith(u"\u0649") for c in result_3la)   # ى at end (e.g. على)

    # Rule D: initial 'a' → also أ (hamza-on-alef)
    result_a5barak = arabizi_to_arabic_list("a5barak")
    assert any(c.startswith(u"\u0623") for c in result_a5barak)  # أخبارك starts with أ

    # Short vowel omission: vowels also generate an empty-string candidate so
    # that unvocalized Arabic forms are produced.  e.g. "salameh":
    #   s → س, a → '' (omitted), l → ل, a → ا, m → م, eh → ة  →  سلامة
    result_salameh = arabizi_to_arabic_list("salameh")
    assert u"\u0633\u0644\u0627\u0645\u0629" in result_salameh   # سلامة
    # Verify a5barak produces the unvocalized form where internal 'a' is omitted
    assert u"\u0623\u062E\u0628\u0627\u0631\u0643" in result_a5barak   # أخبارك
    assert u"\u0627\u062E\u0628\u0627\u0631\u0643" in result_a5barak   # اخبارك

    # Style 2 (number-based): '8' maps to ق (qaf) — e.g. "8ala" → قال
    assert u"\u0642" in arabizi_to_arabic_list("8")   # ق
    assert u"\u0642\u0627\u0644" in arabizi_to_arabic_list("8ala")   # قال

    # Style 2 (number-based): '2' at word start → أ (hamza-on-alef) as well as ء
    # e.g. "2anta" → أنت (Style 2: 2anta=أنت)
    result_2anta = arabizi_to_arabic_list("2anta")
    assert any(c.startswith(u"\u0623") for c in result_2anta)   # أ at start
    assert u"\u0623\u0646\u062A" in result_2anta   # أنت specifically

    # Extended Rule B: 'ar'/'er' prefix → ال (sun-letter assimilation)
    assert u"\u0627\u0644" in arabizi_to_arabic_list("ar")   # ال
    assert u"\u0627\u0644" in arabizi_to_arabic_list("er")   # ال
    # 'an' prefix → ال  (e.g. "an-nas" = الناس)
    assert u"\u0627\u0644" in arabizi_to_arabic_list("an")   # ال
    # 3-char 'ash'/'esh' prefix → ال  (e.g. "ash-shaytan" = الشيطان)
    assert u"\u0627\u0644" in arabizi_to_arabic_list("ash")   # ال

    # Transparent '-': "al-7amd" generates الحمد (ال + حمد with vowel omission)
    result_al_hamd = arabizi_to_arabic_list("al-7amd")
    assert u"\u0627\u0644\u062D\u0645\u062F" in result_al_hamd   # الحمد

    # "ar-ra7man" generates الرحمن (ar=ال + transparent '-' + رحمن)
    result_ar_ra7man = arabizi_to_arabic_list("ar-ra7man")
    assert u"\u0627\u0644\u0631\u062D\u0645\u0646" in result_ar_ra7man   # الرحمن

    # Digraph "3'" → غ (ghain, number-apostrophe notation: 3'ayr=غير)
    assert u"\u063A" in arabizi_to_arabic_list(u"3'")   # غ
    result_3prime_ayr = arabizi_to_arabic_list(u"3'ayr")
    assert u"\u063A\u064A\u0631" in result_3prime_ayr   # غير

    # Dialectal 'g' → ج (Egyptian/Gulf: Ganna=جنة, Gihaad=جهاد, Gabril=جبريل)
    assert u"\u062C" in arabizi_to_arabic_list("g")   # ج
    assert u"\u062C\u0647\u0627\u062F" in arabizi_to_arabic_list("gihaad")   # جهاد

    # Digraph "ah" → ة (terminal -ah feminine suffix: Rahmah=رحمة, tobah=توبة)
    assert u"\u0629" in arabizi_to_arabic_list("ah")   # ة
    result_tobah = arabizi_to_arabic_list("tobah")
    assert any(c.endswith(u"\u0629") for c in result_tobah)   # at least one ends with ة

    # Digraph "ch" → ش (dialectal variant: Chokr=شكر)
    assert u"\u0634" in arabizi_to_arabic_list("ch")   # ش
    result_chokr = arabizi_to_arabic_list("chokr")
    assert u"\u0634\u0643\u0631" in result_chokr   # شكر

    # Rule D extension: initial 'i'/'e' → also إ (hamza-under-alef, U+0625)
    # e.g. Iblis→إبليس, Enta→إنت
    result_iblis = arabizi_to_arabic_list("iblis")
    assert any(c.startswith(u"\u0625") for c in result_iblis)   # إ at start
    assert u"\u0625\u0628\u0644\u064A\u0633" in result_iblis   # إبليس
    result_enta = arabizi_to_arabic_list("enta")
    assert u"\u0625\u0646\u062A" in result_enta   # إنت

    # Gemination also produces unvocalized (shadda-free) form for wordset matching:
    # "Jannah" → جنّة (with shadda) AND جنة (without shadda, for Quran filter)
    result_jannah = arabizi_to_arabic_list("jannah")
    assert u"\u062C\u0646\u0651\u0629" in result_jannah   # جنّة with shadda
    assert u"\u062C\u0646\u0629" in result_jannah          # جنة without shadda (unvocalized)


def test_arabizi_quran_word_filter():
    """12. arabizi candidates filtered to unvocalized Quranic words."""
    from alfanous.romanization import arabizi_to_arabic_list, filter_candidates_by_wordset
    from alfanous.data import quran_unvocalized_words

    qwords = quran_unvocalized_words()
    assert len(qwords) > 0, "Quran word set should not be empty"

    def filtered(arabizi):
        cands = arabizi_to_arabic_list(arabizi.lower())
        return filter_candidates_by_wordset(cands, qwords)

    # يعطيك is a real Quranic word; Arabizi "ya36eek" should resolve to it
    result = filtered("ya36eek")
    assert u"\u064A\u0639\u0637\u064A\u0643" in result   # يعطيك

    # بكرة is a Quranic word; "bokreh" → بكرة after filtering
    result_bokra = filtered("bokreh")
    assert u"\u0628\u0643\u0631\u0629" in result_bokra   # بكرة

    # For non-Quranic Arabizi words the fallback is all candidates (no empty result)
    result_fallback = filtered("salameh")
    assert len(result_fallback) > 0   # should fall back gracefully

    # إبليس is a Quranic word; "iblis" → إبليس after filtering (initial i→إ rule)
    result_iblis = filtered("iblis")
    assert u"\u0625\u0628\u0644\u064A\u0633" in result_iblis   # إبليس

    # جنة is a Quranic word; "jannah" → جنة (gemination without shadda = unvocalized)
    result_jannah = filtered("jannah")
    assert u"\u062C\u0646\u0629" in result_jannah   # جنة

    # توبة is a Quranic word; "tobah" → توبة (ah digraph → ة)
    result_tobah = filtered("tobah")
    assert u"\u062A\u0648\u0628\u0629" in result_tobah   # توبة
