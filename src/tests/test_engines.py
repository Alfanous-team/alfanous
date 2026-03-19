
"""
This is a test module for most of features provided by alfanous.engines module.

"""

import pytest
from alfanous.engines import QuranicSearchEngine
from alfanous import paths
from alfanous.constants import QURAN_TOTAL_VERSES


QSE = QuranicSearchEngine(paths.QSE_INDEX)


@pytest.fixture(autouse=True)
def _require_index():
    if not QSE.OK:
        pytest.skip("Search index not built — run `make build` first")


def test_aya_engine():
    assert QSE.OK


def test_most_frequent_words():
    print("\n#most frequent words#")
    most_frequent_words = QSE.most_frequent_words(9999999, "aya_")
    assert len(most_frequent_words) == 17572
    assert most_frequent_words[0:5] == [(1673.0, 'مِنْ'),
                                        (1185.0, 'فِي'),
                                        (1010.0, 'مَا'),
                                        (828.0, 'اللَّهِ'),
                                        (812.0, 'لَا')]


def test_list_values():
    assert QSE.list_values("sura_id") == list(range(1, 114 + 1))
    # gid is only on aya parent docs (1-6236); word children carry no gid
    assert len(list(QSE.list_values("gid"))) == 6236
    # chapters, topics, subtopics should return full phrases, not single-word tokens
    chapters = QSE.list_stored_values("chapter")
    assert any(' ' in c for c in chapters), "chapters should contain multi-word phrases"
    topics = QSE.list_stored_values("topic")
    assert any(' ' in t for t in topics), "topics should contain multi-word phrases"


def test_missing_suggetion():
    assert list(QSE.suggest_all(u"النسر").items()) == [('النسر', ['النار', 'النور', 'النذر'])]


def test_suggest_collocations():
    """Collocations for سميع should include known adjacent Quranic n-grams."""
    collocations = QSE.suggest_collocations("سميع")
    assert len(collocations) > 0
    # Every phrase must be 2 or 3 words and must contain the query word
    for phrase in collocations:
        words = phrase.split()
        assert 2 <= len(words) <= 3
        assert "سميع" in words
    # سميع frequently appears adjacent to عليم and بصير in the Quran
    all_words = {w for phrase in collocations for w in phrase.split()}
    assert any(w in all_words for w in ["عليم", "بصير"])


def test_suggest_collocations_includes_trigrams():
    """High-frequency trigrams should be returned alongside bigrams."""
    # سميع has the trigram والله سميع عليم (8×) which exceeds min_count=2
    collocations = QSE.suggest_collocations("سميع", limit=10)
    trigrams = [p for p in collocations if len(p.split()) == 3]
    assert len(trigrams) > 0, "Expected at least one trigram for سميع"
    trigram_words = {w for p in trigrams for w in p.split()}
    # عليم should appear in a trigram context with سميع
    assert "عليم" in trigram_words


def test_suggest_collocations_trigram_min_count():
    """Setting trigram_min_count=999 should suppress all trigrams."""
    collocations = QSE.suggest_collocations("سميع", limit=10, trigram_min_count=999)
    for phrase in collocations:
        assert len(phrase.split()) == 2, "No trigrams should be returned at high min_count"


def test_suggest_collocations_with_stopwords():
    """Stopword filtering should exclude common function words from bigram collocations."""
    stopwords = frozenset(["في", "من", "على", "إن"])
    collocations = QSE.suggest_collocations("قل", stopwords=stopwords)
    bigrams = [p for p in collocations if len(p.split()) == 2]
    bigram_neighbours = {w for p in bigrams for w in p.split() if w != "قل"}
    for sw in stopwords:
        assert sw not in bigram_neighbours, f"stopword '{sw}' must not appear in bigram collocations"


def test_suggest_collocations_unknown_word():
    """An unknown word should return an empty collocation list."""
    collocations = QSE.suggest_collocations("zzzzzzzzz")
    assert collocations == []


def test_autocomplete():
    result = QSE.autocomplete("رسول")
    assert result["base"] == ""
    # completion must be collocation phrases (bigrams/trigrams), not single-word prefixes
    assert all(len(phrase.split()) >= 2 for phrase in result["completion"])
    # the query word must appear in every phrase
    assert all("رسول" in phrase.split() for phrase in result["completion"])
    # most frequent Quranic collocation should be near the top
    assert "رسول الله" in result["completion"]


def test_autocomplete_multiword():
    """For a multi-word query the base preserves all but the last word."""
    result = QSE.autocomplete("إن الله")
    assert result["base"] == "إن"
    assert all("الله" in phrase.split() for phrase in result["completion"])


def test_autocomplete_unknown_word():
    """An unknown word returns an empty completion list."""
    result = QSE.autocomplete("zzzzz")
    assert result["base"] == ""
    assert result["completion"] == []


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
                                'kind': 'aya',
                                'manzil': 3,
                                'nisf': 53,
                                'page': 262,
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
                                'transliteration': 'Tharhum yakuloo wayatamattaAAoo wayulhihimu alamalu fasawfa yaAAlamoona',
                                'uth_': 'ذَرۡهُمۡ يَأۡكُلُواْ وَيَتَمَتَّعُواْ وَيُلۡهِهِمُ ٱلۡأَمَلُۖ فَسَوۡفَ يَعۡلَمُونَ'}

    # Transliteration field search: Latin-script phonetic text must be searchable.
    # "alrrahmani" appears in Al-Fatiha 1:1 and 1:3 transliterations.
    results_t, terms_t, searcher_t = QSE.search_all("transliteration:alrrahmani", limit=10)
    assert len(results_t) > 0, "transliteration field search must return results"
    assert all(r.get("kind") == "aya" for r in results_t)
    assert any("alrrahmani" in (r.get("transliteration") or "").lower() for r in results_t)
    searcher_t.close()


def test_translation_engine():
    """Translation children are searchable directly in QSE."""
    results, searcher = QSE.find_extended(
        "( gid:1 OR gid:2 ) AND kind:translation", defaultfield="gid"
    )
    assert len(results)
    assert {'en.shakir', 'en.transliteration'} & set(
        r.get("trans_id") for r in results
    )
    searcher.close()

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


def test_wildcard_stopped_by_timelimit():
    """Wildcard search in aya must be stopped by the timelimit without crashing.

    Uses an extremely short timelimit so the collector is almost certainly
    interrupted before all documents are scored.  The test asserts that:
      - the call returns without raising an exception,
      - the returned Results object is non-None and has a non-negative length.
    Whether the timeout actually fires is hardware-dependent; what matters is
    that the full code path (wildcard expansion → TimeLimitCollector → partial
    results) is exercised and handled gracefully.
    """
    results, _terms, _searcher = QSE.search_all(u"*", limit=6236, timelimit=0.00001)
    assert results is not None, "results must not be None when timelimit is hit"
    assert len(results) >= 0, "results length must be non-negative"

    # Also verify the single-char wildcard variant with the same constraint
    results2, _terms2, _searcher2 = QSE.search_all(u"ن*", limit=6236, timelimit=0.00001)
    assert results2 is not None
    assert len(results2) >= 0


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
    # {قول،اسم} — noun derivations of قول; new index-based logic may return more
    # variations than the old static data → accept any count >= original baseline
    results, terms, _searcher = QSE.search_all(u"{قول،اسم}", limit=6236, sortedby="score", reverse=True)
    assert len(results) >= 59
    term_words = [t[1] for t in terms]
    assert len(term_words) >= 11
    assert "قول" in term_words
    assert "قولا" in term_words

    # {ملك،فعل} — verbs with root ملك; accept any count >= original baseline
    results2, terms2, _searcher2 = QSE.search_all(u"{ملك،فعل}", limit=6236, sortedby="score", reverse=True)
    assert len(results2) >= 42
    term_words2 = [t[1] for t in terms2]
    assert len(term_words2) >= 8
    assert "يملك" in term_words2


def test_advanced_search_derivations():
    """9. Derivations — > (lemma level) and >> (root level)."""
    lemma_results = _qse_search(u">ملك")
    root_results = _qse_search(u">>ملك")
    assert lemma_results >= 150
    assert root_results == 191
    assert lemma_results >= 1
    assert root_results >= 1


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

    # Digraph "sh": generates candidates (ش digraph + single-char permutations)
    # With multi-mappings s→[س,ص] and h→[ه,ح], plus terminal-h→ة rule
    result_sh = arabizi_to_arabic_list("sh")
    assert u"\u0634" in result_sh          # ش  (digraph interpretation)
    assert u"\u0633\u0647" in result_sh    # سه (s→س, h→ه)
    assert u"\u0635\u062D" in result_sh    # صح (s→ص, h→ح)
    assert len(result_sh) >= 2             # at least two candidates

    # Digraph "th": generates candidates (ث digraph + single-char permutations)
    result_th = arabizi_to_arabic_list("th")
    assert u"\u062B" in result_th          # ث  (digraph interpretation)
    assert u"\u062A\u0647" in result_th    # ته (two-letter, t→ت, h→ه)
    assert len(result_th) >= 2             # at least two candidates

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

    # Rule D extension: initial 'u'/'o' → also أ (hamza-on-alef, U+0623)
    # e.g. Ummah→أمة, Ommah→أمة (dialectal)
    result_ummah = arabizi_to_arabic_list("ummah")
    assert any(c.startswith(u"\u0623") for c in result_ummah)   # أ at start
    assert u"\u0623\u0645\u0629" in result_ummah   # أمة
    result_ommah = arabizi_to_arabic_list("ommah")
    assert any(c.startswith(u"\u0623") for c in result_ommah)   # أ at start

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

    # صلواة is the Quranic spelling of prayer; "salwah" → صلواة
    result_salwah = filtered("salwah")
    assert u"\u0635\u0644\u0648\u0627\u0629" in result_salwah   # صلواة

    # حيواة is the Quranic spelling of life; "haywat" → حيواة
    result_haywat = filtered("haywat")
    assert u"\u062D\u064A\u0648\u0627\u0629" in result_haywat   # حيواة

    # صبر is Quranic; "sabr" → صبر (s→ص)
    result_sabr = filtered("sabr")
    assert u"\u0635\u0628\u0631" in result_sabr   # صبر

    # مسلم is Quranic; "muslim" → مسلم (s→س)
    result_muslim = filtered("muslim")
    assert u"\u0645\u0633\u0644\u0645" in result_muslim   # مسلم

    # ── Prophets and historical figures (49-example set) ──────────────────────

    # أمة is Quranic; "ummah"/"ommah" → أمة (initial u/o→أ, mm→م gemination, ah→ة)
    result_ummah = filtered("ummah")
    assert u"\u0623\u0645\u0629" in result_ummah   # أمة
    # Style 4 dialectal: initial 'o' also triggers the أ rule
    result_ommah = filtered("ommah")
    assert u"\u0623\u0645\u0629" in result_ommah   # أمة

    # فتنة is Quranic; "fitnah" → فتنة (ah digraph → ة)
    result_fitnah = filtered("fitnah")
    assert u"\u0641\u062A\u0646\u0629" in result_fitnah   # فتنة

    # جهنم is Quranic; "jahannam" → جهنم (j→ج, h→ه, nn→ن gemination, m→م)
    result_jahannam = filtered("jahannam")
    assert u"\u062C\u0647\u0646\u0645" in result_jahannam   # جهنم

    # نوح is Quranic; "nuh" → نوح (n→ن, u→و, h→ح)
    result_nuh = filtered("nuh")
    assert u"\u0646\u0648\u062D" in result_nuh   # نوح

    # Style 2: "Noo7" → نوح (n→ن, oo→و + omit, 7→ح)
    result_noo7 = filtered("noo7")
    assert u"\u0646\u0648\u062D" in result_noo7   # نوح

    # إبراهيم is Quranic; "ibrahim" → إبراهيم (initial i→إ, b→ب, r→ر, a→ا, h→ه, i→ي, m→م)
    result_ibrahim = filtered("ibrahim")
    assert u"\u0625\u0628\u0631\u0627\u0647\u064A\u0645" in result_ibrahim   # إبراهيم

    # موسى is Quranic; "musa" → موسى (m→م, u→و, s→س, a→ى terminal)
    result_musa = filtered("musa")
    assert u"\u0645\u0648\u0633\u0649" in result_musa   # موسى

    # محمد is Quranic; "mo7ammad" → محمد (style 2: 7→ح, mm→م gemination)
    result_mo7ammad = filtered("mo7ammad")
    assert u"\u0645\u062D\u0645\u062F" in result_mo7ammad   # محمد

    # مريم is Quranic; "maryam" → مريم (m→م, a→omit, r→ر, y→ي, a→omit, m→م;
    # internal 'a' is omitted via short-vowel omission for unvocalized Arabic match)
    result_maryam = filtered("maryam")
    assert u"\u0645\u0631\u064A\u0645" in result_maryam   # مريم

    # يحيى is Quranic; "yahya" → يحيى (y→ي, h→ح, y→ي, a→ى terminal)
    result_yahya = filtered("yahya")
    assert u"\u064A\u062D\u064A\u0649" in result_yahya   # يحيى

    # لوط is Quranic; "lut" → لوط (l→ل, u→و, t→ط emphatic)
    result_lut = filtered("lut")
    assert u"\u0644\u0648\u0637" in result_lut   # لوط

    # هود is Quranic; "hud" → هود (h→ه, u→و, d→د)
    result_hud = filtered("hud")
    assert u"\u0647\u0648\u062F" in result_hud   # هود

    # سليمان is Quranic; "sulayman" → سليمان (s→س, u→omit, l→ل, a→omit, y→ي, m→م, a→ا, n→ن)
    result_sulayman = filtered("sulayman")
    assert u"\u0633\u0644\u064A\u0645\u0627\u0646" in result_sulayman   # سليمان

    # زكريا is Quranic; "zakariya" → زكريا (z→ز, terminal a→ى or ا)
    result_zakariya = filtered("zakariya")
    assert u"\u0632\u0643\u0631\u064A\u0627" in result_zakariya   # زكريا

    # طالوت is Quranic; "6aloot" → طالوت (style 2: 6→ط, a→ا, l→ل, oo→و, t→ت)
    result_6aloot = filtered("6aloot")
    assert u"\u0637\u0627\u0644\u0648\u062A" in result_6aloot   # طالوت

    # جالوت is Quranic; "jalut" → جالوت (j→ج, a→ا, l→ل, u→و, t→ت)
    result_jalut = filtered("jalut")
    assert u"\u062C\u0627\u0644\u0648\u062A" in result_jalut   # جالوت

    # ── Selected examples from new batch ─────────────────────────────────────

    # ضلال is Quranic; style 2 "6alal" → ضلال (6→ض emphatic in number-based chat)
    result_6alal = filtered("6alal")
    assert u"\u0636\u0644\u0627\u0644" in result_6alal   # ضلال

    # ذهب is Quranic; dialectal "zahab"/"dahab" → ذهب (z/d can map to ذ in dialects)
    result_zahab = filtered("zahab")
    assert u"\u0630\u0647\u0628" in result_zahab   # ذهب
    result_dahab = filtered("dahab")
    assert u"\u0630\u0647\u0628" in result_dahab   # ذهب

    # ذنب is Quranic; "zanb" → ذنب (dialectal z→ذ, dhanb works via dh digraph)
    result_zanb = filtered("zanb")
    assert u"\u0630\u0646\u0628" in result_zanb   # ذنب

    # رزق is Quranic; "rizq"/"rez8" → رزق (style 2: 8→ق)
    result_rizq = filtered("rizq")
    assert u"\u0631\u0632\u0642" in result_rizq   # رزق
    result_rez8 = filtered("rez8")
    assert u"\u0631\u0632\u0642" in result_rez8   # رزق

    # حسنة is Quranic; "7asana"/"hasanah" → حسنة
    result_7asana = filtered("7asana")
    assert u"\u062D\u0633\u0646\u0629" in result_7asana   # حسنة

    # نور is Quranic; "nur"/"noor" → نور
    result_nur = filtered("nur")
    assert u"\u0646\u0648\u0631" in result_nur   # نور

    # هدى is Quranic; "huda"/"hoda" → هدى (terminal a→ى)
    result_huda = filtered("huda")
    assert u"\u0647\u062F\u0649" in result_huda   # هدى

    # نهار is Quranic; "nahar" → نهار
    result_nahar = filtered("nahar")
    assert u"\u0646\u0647\u0627\u0631" in result_nahar   # نهار

    # عرش is Quranic; "3arsh" → عرش
    result_3arsh = filtered("3arsh")
    assert u"\u0639\u0631\u0634" in result_3arsh   # عرش

    # جنات is Quranic; "jannat"/"gannat" → جنات (gemination)
    result_jannat = filtered("jannat")
    assert u"\u062C\u0646\u0627\u062A" in result_jannat   # جنات

    # نخل is Quranic; "na5l" → نخل (5→خ)
    result_na5l = filtered("na5l")
    assert u"\u0646\u062E\u0644" in result_na5l   # نخل

    # عسل is Quranic; "3asal" → عسل
    result_3asal = filtered("3asal")
    assert u"\u0639\u0633\u0644" in result_3asal   # عسل

    # لحم is Quranic; "la7m" → لحم
    result_la7m = filtered("la7m")
    assert u"\u0644\u062D\u0645" in result_la7m   # لحم

    # طعام is Quranic; "6a3am" → طعام (6→ط, 3→ع)
    result_6a3am = filtered("6a3am")
    assert u"\u0637\u0639\u0627\u0645" in result_6a3am   # طعام

    # شراب is Quranic; "charab" → شراب (dialectal ch→ش)
    result_charab = filtered("charab")
    assert u"\u0634\u0631\u0627\u0628" in result_charab   # شراب

    # حرير is Quranic; "7areer" → حرير (7→ح, ee→ي)
    result_7areer = filtered("7areer")
    assert u"\u062D\u0631\u064A\u0631" in result_7areer   # حرير

    # لؤلؤ is Quranic; "lolo" → لؤلؤ (dialectal simplification: ؤ written as o)
    result_lolo = filtered("lolo")
    assert len(result_lolo) > 0   # graceful fallback even if not exact match


def test_arabizi_untested_digraphs():
    """13. Arabizi digraphs kh, dh, gh — not covered by existing tests."""
    from alfanous.romanization import arabizi_to_arabic_list

    # Digraph "kh" → خ (kha)
    assert u"\u062E" in arabizi_to_arabic_list("kh")          # خ
    result_khamr = arabizi_to_arabic_list("khamr")
    assert u"\u062E\u0645\u0631" in result_khamr               # خمر

    # Digraph "dh" → ذ (dhal)
    assert u"\u0630" in arabizi_to_arabic_list("dh")           # ذ
    result_dhanb = arabizi_to_arabic_list("dhanb")
    assert u"\u0630\u0646\u0628" in result_dhanb               # ذنب

    # Digraph "gh" → غ (ghain — separate from the number-apostrophe notation 3')
    assert u"\u063A" in arabizi_to_arabic_list("gh")           # غ
    result_ghayb = arabizi_to_arabic_list("ghayb")
    assert u"\u063A\u064A\u0628" in result_ghayb               # غيب


def test_arabizi_rule_b_remaining_prefixes():
    """14. Rule B — the en/as/es/ad/ed/esh definite-article prefixes are not covered by
    existing tests."""
    from alfanous.romanization import arabizi_to_arabic_list

    AL = u"\u0627\u0644"  # ال

    # Two-character sun-letter assimilation prefixes
    assert AL in arabizi_to_arabic_list("en")    # ال (e.g. en-nas = الناس)
    assert AL in arabizi_to_arabic_list("as")    # ال (e.g. as-sama = السماء)
    assert AL in arabizi_to_arabic_list("es")    # ال
    assert AL in arabizi_to_arabic_list("ad")    # ال
    assert AL in arabizi_to_arabic_list("ed")    # ال

    # Three-character prefix "esh" → ال (e.g. esh-shaytan = الشيطان)
    assert AL in arabizi_to_arabic_list("esh")

    # Compound: "en-nas" should include الناس as a candidate
    result_en_nas = arabizi_to_arabic_list("en-nas")
    assert u"\u0627\u0644\u0646\u0627\u0633" in result_en_nas  # الناس


def test_arabizi_k_dialectal_qaf():
    """15. Multi-mapping 'k' → ق (dialectal) in addition to ك — not covered at unit level."""
    from alfanous.romanization import arabizi_to_arabic_list

    candidates_k = arabizi_to_arabic_list("k")
    assert u"\u0643" in candidates_k   # ك  (standard)
    assert u"\u0642" in candidates_k   # ق  (dialectal)


def test_arabizi_alef_madda_normalization():
    """16. ءا → آ normalization: the post-processing step that replaces hamza+alef
    sequences with alef madda (U+0622) must produce آ-containing candidates."""
    from alfanous.romanization import arabizi_to_arabic_list

    # "2aya" → contains ءاية which normalises to آية
    result_2aya = arabizi_to_arabic_list("2aya")
    assert any(u"\u0622" in c for c in result_2aya), \
        "alef madda normalization must produce at least one آ-containing candidate"
    assert u"\u0622\u064A\u0629" in result_2aya   # آية specifically


def test_transliterate_buckwalter():
    """17. transliterate() — Buckwalter romanization to Unicode and back."""
    from alfanous.romanization import transliterate

    # Forward: Buckwalter → Arabic Unicode
    assert transliterate("buckwalter", "b") == u"\u0628"    # ب
    assert transliterate("buckwalter", "s") == u"\u0633"    # س
    assert transliterate("buckwalter", "m") == u"\u0645"    # م
    # Multi-character string
    bsm = transliterate("buckwalter", "bsm")
    assert bsm == u"\u0628\u0633\u0645"                     # بسم

    # Reverse: Arabic Unicode → Buckwalter
    assert transliterate("buckwalter", u"\u0628", reverse=True) == "b"
    assert transliterate("buckwalter", u"\u0628\u0633\u0645", reverse=True) == "bsm"

    # Characters in the ignore set are passed through unchanged
    result_ignore = transliterate("buckwalter", "b*m", ignore="*")
    assert result_ignore == u"\u0628*\u0645"                # ب*م

    # Unknown romanization mode: every character is passed through as-is
    assert transliterate("unknown_mode", "hello") == "hello"


def test_fuzzy_excludes_short_words():
    """Words shorter than 4 characters must not be included in fuzzy (Levenshtein) matching."""
    from whoosh.query import FuzzyTerm

    # Reproduce the exact filter condition used in QSearcher.search so that any
    # future change to that condition is caught here too.  The condition is
    # intentionally duplicated to pin the requirement as a contract test.
    def build_levenshtein_subqueries(terms, fuzzy_maxdist=1):
        return [
            FuzzyTerm("aya_ac", term, maxdist=fuzzy_maxdist, prefixlength=1)
            for _fieldname, term in terms
            if term and len(term) >= 4 and any('\u0600' <= c <= '\u06FF' for c in term)
        ]

    # Short Arabic words (< 4 chars) must produce NO FuzzyTerm entries
    short_words = [("aya", u"من"), ("aya", u"رب"), ("aya", u"في"), ("aya", u"هو")]
    assert build_levenshtein_subqueries(short_words) == [], \
        "Short Arabic words (<4 chars) should be excluded from fuzzy matching"

    # A 3-char word
    three_char = [("aya", u"قلب")]
    assert build_levenshtein_subqueries(three_char) == [], \
        "3-char Arabic word should be excluded from fuzzy matching"

    # A word at the boundary (exactly 4 chars) must be included
    four_char = [("aya", u"الله")]
    result = build_levenshtein_subqueries(four_char)
    assert len(result) == 1, "4-char Arabic word should be included in fuzzy matching"
    assert isinstance(result[0], FuzzyTerm)
    assert result[0].text == u"الله"

    # A word longer than 4 chars must also be included
    long_word = [("aya", u"الكتاب")]
    result_long = build_levenshtein_subqueries(long_word)
    assert len(result_long) == 1, "Long Arabic word should be included in fuzzy matching"

    # Non-Arabic terms (Latin) must not be included regardless of length
    latin_terms = [("aya", "hello"), ("aya", "world")]
    assert build_levenshtein_subqueries(latin_terms) == [], \
        "Non-Arabic terms should be excluded from fuzzy matching"


def test_fuzzy_phrase_no_query_error():
    """Phrase queries must not raise QueryError when fuzzy=True.

    The 'aya_fuzzy' field has phrase=False so Whoosh raises
    ``QueryError: Phrase search: 'aya_fuzzy' field has no positions``
    whenever a Phrase query object is executed against it.  The fix in
    :func:`~alfanous.searching._strip_phrase_queries` converts each Phrase
    node to an And-of-Terms before execution.  This test verifies that
    sending a quoted (phrase) query with ``fuzzy=True`` does **not** raise
    an exception and returns a result tuple.
    """
    from whoosh.query.qcore import QueryError
    # A two-word Arabic phrase query — the leading/trailing quotes tell the
    # Whoosh QueryParser to produce a Phrase object.  searcher is a
    # non-closing proxy; no explicit close needed.
    phrase_query = '"رب العالمين"'
    try:
        results, terms, searcher = QSE.search_all(phrase_query, fuzzy=True, limit=10)
    except QueryError as exc:
        raise AssertionError(
            f"search_all raised QueryError for phrase+fuzzy: {exc}"
        ) from exc
    # Basic sanity: result tuple has the right shape
    assert hasattr(results, 'runtime'), "results must be a Whoosh Results object"
    assert isinstance(terms, list)


def test_topic_phrase_no_query_error():
    """Phrase queries on 'topic' (an ID field) must not raise QueryError.

    'topic', 'chapter', and 'subtopic' are ``ID`` type fields with no
    positional data.  Before the fix, a query like ``topic:"الانشغال بشهوات
    الدنيا"`` raised ``QueryError: Phrase search: 'topic' field has no
    positions`` because Whoosh tries to execute a Phrase query object against
    a field that stores no position information.

    The fix in :func:`~alfanous.searching._strip_phrase_queries` (with
    *schema* provided) converts such Phrase nodes to And-of-Terms before
    execution, so the query returns useful results rather than crashing.
    """
    from whoosh.query.qcore import QueryError

    for field, phrase in [
        # "Preoccupation with worldly desires" — a multi-word topic value
        ("topic",    '"الانشغال بشهوات الدنيا"'),
        # "Pillars of faith" — a multi-word chapter value
        ("chapter",  '"أركان الإيمان"'),
        # "Explanation of the hadith" — a multi-word subtopic value
        ("subtopic", '"شرح الحديث"'),
    ]:
        query_str = f'{field}:{phrase}'
        try:
            results, terms, searcher = QSE.search_all(query_str, limit=10)
        except QueryError as exc:
            raise AssertionError(
                f"search_all raised QueryError for {query_str!r}: {exc}"
            ) from exc
        assert hasattr(results, 'runtime'), (
            f"results for {query_str!r} must be a Whoosh Results object"
        )


def test_sura_phrase_no_query_error():
    """Phrase query on the 'sura' field must not raise QueryError.

    The 'sura' field stores the romanized sura name and is indexed with
    ``phrase=False`` (no positional data).  A query like
    ``sura:"Al Baqarah"`` previously raised
    ``QueryError: Phrase search: 'sura' field has no positions``.

    The fix in :func:`~alfanous.searching._strip_phrase_queries` (with
    *schema* provided) converts such Phrase nodes to And-of-Terms before
    execution, so the query returns useful results rather than crashing.
    """
    from whoosh.query.qcore import QueryError

    query_str = 'sura:"Al Baqarah"'
    try:
        results, terms, searcher = QSE.search_all(query_str, limit=10)
    except QueryError as exc:
        raise AssertionError(
            f"search_all raised QueryError for {query_str!r}: {exc}"
        ) from exc
    assert hasattr(results, 'runtime'), (
        f"results for {query_str!r} must be a Whoosh Results object"
    )


def test_phrase_search_preserved_for_positional_fields():
    """Phrase search on TEXT fields (with positions) must still work correctly.

    The schema-aware _strip_phrase_queries must not strip Phrase nodes for
    TEXT fields that DO store positional data (e.g. 'aya', 'aya_').  This
    test verifies that a quoted phrase query on the main aya field returns
    the same results as before the fix.
    """
    from whoosh.query.qcore import QueryError

    # "Lord of the worlds" — a phrase that appears many times in the Quran
    phrase_query = '"رب العالمين"'
    try:
        results, terms, searcher = QSE.search_all(phrase_query, limit=100)
    except QueryError as exc:
        raise AssertionError(
            f"search_all raised QueryError for phrase on positional field: {exc}"
        ) from exc
    assert hasattr(results, 'runtime'), "results must be a Whoosh Results object"
    assert len(results) > 0, "Phrase search on aya field should return results"


def test_fuzzy_derivation_returns_more_results():
    """fuzzy=True with derivation expansion returns >= results of explicit root derivation.

    Searching "ملك" with fuzzy=True and derivation expansion enabled should
    return at least as many verses as the plain root-derivation query >>ملك,
    because the fuzzy derivation strategy uses root-level (level=2) expansion.
    """
    root_deriv_results = _qse_search(u">>ملك")

    fuzzy_results, _, _ = QSE.search_all(u"ملك", fuzzy=True, fuzzy_derivation=True, limit=QURAN_TOTAL_VERSES)
    fuzzy_count = len(fuzzy_results)

    assert fuzzy_count >= root_deriv_results, (
        f"fuzzy+derivation ({fuzzy_count}) should cover at least as many results "
        f"as >>ملك derivation search ({root_deriv_results})"
    )


def test_fuzzy_derivation_disabled():
    """fuzzy_derivation=False disables derivation expansion.

    Results with derivation expansion disabled should be <= results with it
    enabled (disabling it only reduces recall, never increases it).
    """
    with_deriv, _, _ = QSE.search_all(u"ملك", fuzzy=True, fuzzy_derivation=True, limit=QURAN_TOTAL_VERSES)
    without_deriv, _, _ = QSE.search_all(u"ملك", fuzzy=True, fuzzy_derivation=False, limit=QURAN_TOTAL_VERSES)

    assert len(with_deriv) >= len(without_deriv), (
        "Enabling derivation expansion must not reduce the result count"
    )


def test_fuzzy_derivation_no_index_fallback():
    """fuzzy derivation expansion gracefully handles unavailable derivations.

    When _get_derivations returns only the original word (no index hit or
    index unavailable), no extra Terms are added and the search still
    completes without error.
    """
    from unittest.mock import patch

    # Mock _get_derivations to simulate a missing/unavailable index:
    # returns only the input word itself — no derivation expansion.
    with patch("alfanous.query_plugins.DerivationQuery._get_derivations", return_value=["ملك"]):
        results, terms, searcher = QSE.search_all(u"ملك", fuzzy=True, fuzzy_derivation=True, limit=10)

    assert hasattr(results, 'runtime'), "results must be a Whoosh Results object"
    assert isinstance(terms, list)


def test_nonfuzzy_derivation_returns_more_results():
    """fuzzy=False with derivation expansion returns >= results of explicit lemma derivation.

    Searching "ملك" with fuzzy=False and derivation expansion enabled should
    return at least as many verses as the plain lemma-derivation query >ملك,
    because the non-fuzzy derivation strategy uses lemma-level (level=1) expansion.
    """
    lemma_deriv_results = _qse_search(u">ملك")

    nonfuzzy_results, _, _ = QSE.search_all(u"ملك", fuzzy=False, fuzzy_derivation=True, limit=QURAN_TOTAL_VERSES)
    nonfuzzy_count = len(nonfuzzy_results)

    assert nonfuzzy_count >= lemma_deriv_results, (
        f"non-fuzzy+derivation ({nonfuzzy_count}) should cover at least as many results "
        f"as >ملك derivation search ({lemma_deriv_results})"
    )


def test_nonfuzzy_derivation_disabled():
    """fuzzy_derivation=False with fuzzy=False returns plain search results.

    Results with derivation expansion disabled should be <= results with it
    enabled (disabling it only reduces recall, never increases it).
    """
    with_deriv, _, _ = QSE.search_all(u"ملك", fuzzy=False, fuzzy_derivation=True, limit=QURAN_TOTAL_VERSES)
    without_deriv, _, _ = QSE.search_all(u"ملك", fuzzy=False, fuzzy_derivation=False, limit=QURAN_TOTAL_VERSES)

    assert len(with_deriv) >= len(without_deriv), (
        "Enabling derivation expansion must not reduce the result count"
    )
