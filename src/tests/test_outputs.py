
"""
A sample script that emphasize the basic operations of Alfanous API.

"""

import re
import pytest

# import Output object
from alfanous.outputs import Raw

# import default paths
from alfanous import paths

# Initialize search engines
RAWoutput = Raw(
                    QSE_index = paths.QSE_INDEX, # Quranic Main index path
                    Recitations_list_file = paths.RECITATIONS_LIST_FILE,
                    Translations_list_file = paths.TRANSLATIONS_LIST_FILE ,
                    Information_file = paths.INFORMATION_FILE
                )


# Skip every test in this file when the Quranic search engine is not available
# (i.e. the index has not been built yet).  Run `make build` first.
@pytest.fixture(autouse=True)
def _require_index():
    if not RAWoutput.QSE.OK:
        pytest.skip("Search index not built — run `make build` first")


def test_suggestion():
    ## prepare a suggestion query
    suggest_flags = {
                "action":"suggest",
                "query": "ابراهيم"
                }

    results = RAWoutput.do( suggest_flags )

    assert results["suggest"] == {'ابراهيم': ['إبراهيم']}

def test_suggestion_strips_symbols():
    ## extra symbols should be stripped before processing
    suggest_flags = {
                "action":"suggest",
                "query": "ابراهيم!!!"
                }

    results = RAWoutput.do( suggest_flags )

    assert results["suggest"] == {'ابراهيم': ['إبراهيم']}

def test_suggestion_strips_non_arabic_words():
    ## non-Arabic words should be ignored
    suggest_flags = {
                "action":"suggest",
                "query": "ابراهيم hello"
                }

    results = RAWoutput.do( suggest_flags )

    assert results["suggest"] == {'ابراهيم': ['إبراهيم']}

def test_suggestion_all_non_arabic():
    ## query with only non-Arabic words should return empty suggestions
    suggest_flags = {
                "action":"suggest",
                "query": "hello world"
                }

    results = RAWoutput.do( suggest_flags )

    assert results["suggest"] == {}


def test_collocation_suggestion_returned_with_suggest():
    """The suggest action must include a 'collocations' key in the response."""
    suggest_flags = {"action": "suggest", "query": "سميع"}
    results = RAWoutput.do(suggest_flags)
    assert "collocations" in results


def test_collocation_suggestion_basic():
    """Collocations for 'سميع' should include known adjacent Quranic n-grams."""
    suggest_flags = {"action": "suggest", "query": "سميع"}
    results = RAWoutput.do(suggest_flags)
    collocations = results["collocations"]
    assert "سميع" in collocations
    phrases = collocations["سميع"]
    assert len(phrases) > 0
    # Every phrase must be 2 or 3 words containing the query word,
    # and must not contain single-character words (e.g. Quranic surah initials like ص, ق, ن)
    for phrase in phrases:
        words = phrase.split()
        assert 2 <= len(words) <= 3
        assert "سميع" in words
        assert all(len(w) > 1 for w in words), f"Single-char word in phrase: {phrase!r}"
    # Common adjacent Quranic collocations of سميع
    all_words = {w for phrase in phrases for w in phrase.split()}
    assert any(w in all_words for w in ["عليم", "بصير"])


def test_collocation_suggestion_includes_trigrams():
    """Suggest action must return trigrams when they are relevant (count >= 2)."""
    suggest_flags = {"action": "suggest", "query": "سميع"}
    results = RAWoutput.do({"action": "suggest", "query": "سميع"})
    phrases = results["collocations"].get("سميع", [])
    trigrams = [p for p in phrases if len(p.split()) == 3]
    assert len(trigrams) > 0, "Expected at least one trigram for سميع in suggest output"


def test_collocation_suggestion_all_non_arabic():
    """A non-Arabic query should return an empty collocations dict."""
    suggest_flags = {"action": "suggest", "query": "hello world"}
    results = RAWoutput.do(suggest_flags)
    assert results["collocations"] == {}


def test_collocation_suggestion_strips_symbols():
    """Symbols around Arabic words should be stripped before collocation lookup."""
    suggest_flags = {"action": "suggest", "query": "سميع!!!"}
    results = RAWoutput.do(suggest_flags)
    collocations = results["collocations"]
    assert "سميع" in collocations

def test_search():
    ## prepare a search query
    search_flags = {
                 "action":"search",
                 "query": "الحمد لله",
                 "sortedby":"mushaf",
                 "reverse_order": False,
                 "page": 1,
                 "word_info": True,
                 "highlight": "css",
                 "script": "standard",
                 "sura_info": True,
                 "aya_position_info": True,
                 "aya_theme_info": False,
                 "aya_stat_info": False,
                 "aya_sajda_info": True,
                 "translation": "en.sahih",
                 }

    results = RAWoutput.do( search_flags )
    assert results["search"]["interval"]["total"] == 116

    del results["search"]["runtime"]
    
    # Extract words->individual for separate comparison (order-independent)
    actual_words_individual = results["search"]["words"]["individual"]
    expected_words_individual = {1: {'derivations': [],
                                     'derivations_extra': [],
                                     'lemma': '',
                                     'nb_ayas_overall': 113,
                                     'nb_ayas': 113,
                                     'nb_derivations': 0,
                                     'nb_derivations_extra': 0,
                                     'nb_matches_overall': 116,
                                     'nb_synonyms': 0,
                                     'nb_vocalizations': 0,
                                     'romanization': None,
                                     'root': '',
                                     'synonyms': [],
                                     'vocalizations': [],
                                     'word': 'لله'},
                                 2: {'derivations': [],
                                     'derivations_extra': [],
                                     'lemma': '',
                                     'nb_ayas_overall': 25,
                                     'nb_ayas': 25,
                                     'nb_derivations': 0,
                                     'nb_derivations_extra': 0,
                                     'nb_matches_overall': 26,
                                     'nb_synonyms': 0,
                                     'nb_vocalizations': 0,
                                     'romanization': None,
                                     'root': '',
                                     'synonyms': [],
                                     'vocalizations': [],
                                     'word': 'الحمد'}}
    
    # Remove words->individual from results for main comparison
    results_without_words_individual = results.copy()
    results_without_words_individual["search"] = results["search"].copy()
    results_without_words_individual["search"]["words"] = results["search"]["words"].copy()
    del results_without_words_individual["search"]["words"]["individual"]

    # Strip translator-specific text before comparing: the exact wording depends on
    # which translation is active (en.sahih, en.shakir, …) and must not be hardcoded.
    def _strip_translation_text(obj):
        if isinstance(obj, dict):
            return {k: (None if k == 'translation' else _strip_translation_text(v))
                    for k, v in obj.items()}
        if isinstance(obj, list):
            return [_strip_translation_text(i) for i in obj]
        return obj

    # Verify each result aya has a non-empty translation string.
    for aya_data in results["search"]["ayas"].values():
        t = aya_data["aya"]["translation"]
        assert isinstance(t, str) and t, f"Expected non-empty translation string, got {t!r}"

    assert _strip_translation_text(results_without_words_individual) == _strip_translation_text({'error': {'code': 0, 'msg': 'success'},
 'search': {'ayas': {1: {'annotations': [],
                         'aya': {'id': 2,
                                 'next_aya': {'id': 3,
                                              'sura': 'Al-Fatihah',
                                              'sura_arabic': 'الفاتحة',
                                              'text': 'الرَّحْمَنِ الرَّحِيمِ'},
                                 'prev_aya': {'id': 1,
                                              'sura': 'Al-Fatihah',
                                              'sura_arabic': 'الفاتحة',
                                              'text': 'بِسْمِ اللَّهِ '
                                                      'الرَّحْمَنِ الرَّحِيمِ'},
                                 'recitation': 'https://www.everyayah.com/data/Abdul_Basit_Murattal_192kbps/001002.mp3',
                                 'text': '<span class="match '
                                         'term0">الْحَمْدُ</span> <span '
                                         'class="match term1">لِلَّهِ</span> '
                                         'رَبِّ الْعَالَمِينَ',
                                 'text_no_highlight': 'الحمد لله رب العالمين',
                                 'transliteration': 'Alhamdu lillahi rabbi alAAalameena',
                                 'translation': 'All praise is due to Allah, '
                                                'the Lord of the Worlds.'},
                         'identifier': {'aya_id': 2,
                                        'gid': 2,
                                        'sura_arabic_name': 'الفاتحة',
                                        'sura_id': 1,
                                        'sura_name': 'Al-Fatihah'},
                         'position': {'hizb': 1,
                                      'juz': 1,
                                      'manzil': 1,
                                      'page': 1,
                                      'rub': 1},
                         'sajda': {'exist': False, 'id': None, 'type': None},
                         'stat': {},
                         'sura': {'arabic_name': 'الفاتحة',
                                  'arabic_type': 'مكية',
                                  'ayas': 7,
                                  'english_name': 'The Opening',
                                  'id': 1,
                                  'name': 'Al-Fatihah',
                                  'order': 5,
                                  'stat': {},
                                  'type': 'Meccan'},
                         'theme': {}},
                     2: {'annotations': [],
                         'aya': {'id': 22,
                                 'next_aya': {'id': 23,
                                              'sura': 'Al-Baqarah',
                                              'sura_arabic': 'البقرة',
                                              'text': 'وَإِنْ كُنْتُمْ فِي '
                                                      'رَيْبٍ مِمَّا '
                                                      'نَزَّلْنَا عَلَى '
                                                      'عَبْدِنَا فَأْتُوا '
                                                      'بِسُورَةٍ مِنْ مِثْلِهِ '
                                                      'وَادْعُوا شُهَدَاءَكُمْ '
                                                      'مِنْ دُونِ اللَّهِ إِنْ '
                                                      'كُنْتُمْ صَادِقِينَ'},
                                 'prev_aya': {'id': 21,
                                              'sura': 'Al-Baqarah',
                                              'sura_arabic': 'البقرة',
                                              'text': 'يَا أَيُّهَا النَّاسُ '
                                                      'اعْبُدُوا رَبَّكُمُ '
                                                      'الَّذِي خَلَقَكُمْ '
                                                      'وَالَّذِينَ مِنْ '
                                                      'قَبْلِكُمْ لَعَلَّكُمْ '
                                                      'تَتَّقُونَ'},
                                 'recitation': 'https://www.everyayah.com/data/Abdul_Basit_Murattal_192kbps/002022.mp3',
                                 'text': 'الَّذِي جَعَلَ لَكُمُ الْأَرْضَ '
                                         'فِرَاشًا وَالسَّمَاءَ بِنَاءً '
                                         'وَأَنْزَلَ مِنَ السَّمَاءِ مَاءً '
                                         'فَأَخْرَجَ بِهِ مِنَ الثَّمَرَاتِ '
                                         'رِزْقًا لَكُمْ فَلَا تَجْعَلُوا '
                                         '<span class="match '
                                         'term0">لِلَّهِ</span> أَنْدَادًا '
                                         'وَأَنْتُمْ تَعْلَمُونَ',
                                 'text_no_highlight': 'الذي جعل لكم الأرض '
                                                      'فراشا والسماء بناء '
                                                      'وأنزل من السماء ماء '
                                                      'فأخرج به من الثمرات '
                                                      'رزقا لكم فلا تجعلوا لله '
                                                      'أندادا وأنتم تعلمون',
                                 'transliteration': 'Allathee jaAAala lakumu alarda firashan waalssamaa binaan waanzala mina alssamai maan faakhraja bihi mina alththamarati rizqan lakum fala tajAAaloo lillahi andadan waantum taAAlamoona',
                                 'translation': 'Who made the earth a resting '
                                                'place for you and the heaven '
                                                'a canopy and (Who) sends down '
                                                'rain from the cloud, then '
                                                'brings forth with it '
                                                'subsistence for you of the '
                                                'fruits; therefore do not set '
                                                'up rivals to Allah while you '
                                                'know.'},
                         'identifier': {'aya_id': 22,
                                        'gid': 29,
                                        'sura_arabic_name': 'البقرة',
                                        'sura_id': 2,
                                        'sura_name': 'Al-Baqarah'},
                         'position': {'hizb': 1,
                                      'juz': 1,
                                      'manzil': 1,
                                      'page': 4,
                                      'rub': 1},
                         'sajda': {'exist': False, 'id': None, 'type': None},
                         'stat': {},
                         'sura': {'arabic_name': 'البقرة',
                                  'arabic_type': 'مدنية',
                                  'ayas': 286,
                                  'english_name': 'The Cow',
                                  'id': 2,
                                  'name': 'Al-Baqarah',
                                  'order': 87,
                                  'stat': {},
                                  'type': 'Medinan'},
                         'theme': {}},
                     3: {'annotations': [],
                         'aya': {'id': 98,
                                 'next_aya': {'id': 99,
                                              'sura': 'Al-Baqarah',
                                              'sura_arabic': 'البقرة',
                                              'text': 'وَلَقَدْ أَنْزَلْنَا '
                                                      'إِلَيْكَ آيَاتٍ '
                                                      'بَيِّنَاتٍ وَمَا '
                                                      'يَكْفُرُ بِهَا إِلَّا '
                                                      'الْفَاسِقُونَ'},
                                 'prev_aya': {'id': 97,
                                              'sura': 'Al-Baqarah',
                                              'sura_arabic': 'البقرة',
                                              'text': 'قُلْ مَنْ كَانَ '
                                                      'عَدُوًّا لِجِبْرِيلَ '
                                                      'فَإِنَّهُ نَزَّلَهُ '
                                                      'عَلَى قَلْبِكَ بِإِذْنِ '
                                                      'اللَّهِ مُصَدِّقًا '
                                                      'لِمَا بَيْنَ يَدَيْهِ '
                                                      'وَهُدًى وَبُشْرَى '
                                                      'لِلْمُؤْمِنِينَ'},
                                 'recitation': 'https://www.everyayah.com/data/Abdul_Basit_Murattal_192kbps/002098.mp3',
                                 'text': 'مَنْ كَانَ عَدُوًّا <span '
                                         'class="match term0">لِلَّهِ</span> '
                                         'وَمَلَائِكَتِهِ وَرُسُلِهِ '
                                         'وَجِبْرِيلَ وَمِيكَالَ فَإِنَّ '
                                         'اللَّهَ عَدُوٌّ لِلْكَافِرِينَ',
                                 'text_no_highlight': 'من كان عدوا لله '
                                                      'وملائكته ورسله وجبريل '
                                                      'وميكال فإن الله عدو '
                                                      'للكافرين',
                                 'transliteration': 'Man kana AAaduwwan lillahi wamalaikatihi warusulihi wajibreela wameekala fainna Allaha AAaduwwun lilkafireena',
                                 'translation': 'Whoever is the enemy of Allah '
                                                'and His angels and His '
                                                'apostles and Jibreel and '
                                                'Meekaeel, so surely Allah is '
                                                'the enemy of the '
                                                'unbelievers.'},
                         'identifier': {'aya_id': 98,
                                        'gid': 105,
                                        'sura_arabic_name': 'البقرة',
                                        'sura_id': 2,
                                        'sura_name': 'Al-Baqarah'},
                         'position': {'hizb': 2,
                                      'juz': 1,
                                      'manzil': 1,
                                      'page': 15,
                                      'rub': 2},
                         'sajda': {'exist': False, 'id': None, 'type': None},
                         'stat': {},
                         'sura': {'arabic_name': 'البقرة',
                                  'arabic_type': 'مدنية',
                                  'ayas': 286,
                                  'english_name': 'The Cow',
                                  'id': 2,
                                  'name': 'Al-Baqarah',
                                  'order': 87,
                                  'stat': {},
                                  'type': 'Medinan'},
                         'theme': {}},
                     4: {'annotations': [],
                         'aya': {'id': 112,
                                 'next_aya': {'id': 113,
                                              'sura': 'Al-Baqarah',
                                              'sura_arabic': 'البقرة',
                                              'text': 'وَقَالَتِ الْيَهُودُ '
                                                      'لَيْسَتِ النَّصَارَى '
                                                      'عَلَى شَيْءٍ وَقَالَتِ '
                                                      'النَّصَارَى لَيْسَتِ '
                                                      'الْيَهُودُ عَلَى شَيْءٍ '
                                                      'وَهُمْ يَتْلُونَ '
                                                      'الْكِتَابَ كَذَلِكَ '
                                                      'قَالَ الَّذِينَ لَا '
                                                      'يَعْلَمُونَ مِثْلَ '
                                                      'قَوْلِهِمْ فَاللَّهُ '
                                                      'يَحْكُمُ بَيْنَهُمْ '
                                                      'يَوْمَ الْقِيَامَةِ '
                                                      'فِيمَا كَانُوا فِيهِ '
                                                      'يَخْتَلِفُونَ'},
                                 'prev_aya': {'id': 111,
                                              'sura': 'Al-Baqarah',
                                              'sura_arabic': 'البقرة',
                                              'text': 'وَقَالُوا لَنْ يَدْخُلَ '
                                                      'الْجَنَّةَ إِلَّا مَنْ '
                                                      'كَانَ هُودًا أَوْ '
                                                      'نَصَارَى تِلْكَ '
                                                      'أَمَانِيُّهُمْ قُلْ '
                                                      'هَاتُوا بُرْهَانَكُمْ '
                                                      'إِنْ كُنْتُمْ '
                                                      'صَادِقِينَ'},
                                 'recitation': 'https://www.everyayah.com/data/Abdul_Basit_Murattal_192kbps/002112.mp3',
                                 'text': 'بَلَى مَنْ أَسْلَمَ وَجْهَهُ <span '
                                         'class="match term0">لِلَّهِ</span> '
                                         'وَهُوَ مُحْسِنٌ فَلَهُ أَجْرُهُ '
                                         'عِنْدَ رَبِّهِ وَلَا خَوْفٌ '
                                         'عَلَيْهِمْ وَلَا هُمْ يَحْزَنُونَ',
                                 'text_no_highlight': 'بلى من أسلم وجهه لله '
                                                      'وهو محسن فله أجره عند '
                                                      'ربه ولا خوف عليهم ولا '
                                                      'هم يحزنون',
                                 'transliteration': 'Bala man aslama wajhahu lillahi wahuwa muhsinun falahu ajruhu AAinda rabbihi wala khawfun AAalayhim wala hum yahzanoona',
                                 'translation': 'Yes! whoever submits himself '
                                                'entirely to Allah and he is '
                                                'the doer of good (to others) '
                                                'he has his reward from his '
                                                'Lord, and there is no fear '
                                                'for him nor shall he grieve.'},
                         'identifier': {'aya_id': 112,
                                        'gid': 119,
                                        'sura_arabic_name': 'البقرة',
                                        'sura_id': 2,
                                        'sura_name': 'Al-Baqarah'},
                         'position': {'hizb': 2,
                                      'juz': 1,
                                      'manzil': 1,
                                      'page': 17,
                                      'rub': 3},
                         'sajda': {'exist': False, 'id': None, 'type': None},
                         'stat': {},
                         'sura': {'arabic_name': 'البقرة',
                                  'arabic_type': 'مدنية',
                                  'ayas': 286,
                                  'english_name': 'The Cow',
                                  'id': 2,
                                  'name': 'Al-Baqarah',
                                  'order': 87,
                                  'stat': {},
                                  'type': 'Medinan'},
                         'theme': {}},
                     5: {'annotations': [],
                         'aya': {'id': 142,
                                 'next_aya': {'id': 143,
                                              'sura': 'Al-Baqarah',
                                              'sura_arabic': 'البقرة',
                                              'text': 'وَكَذَلِكَ '
                                                      'جَعَلْنَاكُمْ أُمَّةً '
                                                      'وَسَطًا لِتَكُونُوا '
                                                      'شُهَدَاءَ عَلَى '
                                                      'النَّاسِ وَيَكُونَ '
                                                      'الرَّسُولُ عَلَيْكُمْ '
                                                      'شَهِيدًا وَمَا '
                                                      'جَعَلْنَا الْقِبْلَةَ '
                                                      'الَّتِي كُنْتَ '
                                                      'عَلَيْهَا إِلَّا '
                                                      'لِنَعْلَمَ مَنْ '
                                                      'يَتَّبِعُ الرَّسُولَ '
                                                      'مِمَّنْ يَنْقَلِبُ '
                                                      'عَلَى عَقِبَيْهِ وَإِنْ '
                                                      'كَانَتْ لَكَبِيرَةً '
                                                      'إِلَّا عَلَى الَّذِينَ '
                                                      'هَدَى اللَّهُ وَمَا '
                                                      'كَانَ اللَّهُ لِيُضِيعَ '
                                                      'إِيمَانَكُمْ إِنَّ '
                                                      'اللَّهَ بِالنَّاسِ '
                                                      'لَرَءُوفٌ رَحِيمٌ'},
                                 'prev_aya': {'id': 141,
                                              'sura': 'Al-Baqarah',
                                              'sura_arabic': 'البقرة',
                                              'text': 'تِلْكَ أُمَّةٌ قَدْ '
                                                      'خَلَتْ لَهَا مَا '
                                                      'كَسَبَتْ وَلَكُمْ مَا '
                                                      'كَسَبْتُمْ وَلَا '
                                                      'تُسْأَلُونَ عَمَّا '
                                                      'كَانُوا يَعْمَلُونَ'},
                                 'recitation': 'https://www.everyayah.com/data/Abdul_Basit_Murattal_192kbps/002142.mp3',
                                 'text': 'سَيَقُولُ السُّفَهَاءُ مِنَ النَّاسِ '
                                         'مَا وَلَّاهُمْ عَنْ قِبْلَتِهِمُ '
                                         'الَّتِي كَانُوا عَلَيْهَا قُلْ <span '
                                         'class="match term0">لِلَّهِ</span> '
                                         'الْمَشْرِقُ وَالْمَغْرِبُ يَهْدِي '
                                         'مَنْ يَشَاءُ إِلَى صِرَاطٍ '
                                         'مُسْتَقِيمٍ',
                                 'text_no_highlight': 'سيقول السفهاء من الناس '
                                                      'ما ولاهم عن قبلتهم التي '
                                                      'كانوا عليها قل لله '
                                                      'المشرق والمغرب يهدي من '
                                                      'يشاء إلى صراط مستقيم',
                                 'transliteration': 'Sayaqoolu alssufahao mina alnnasi ma wallahum AAan qiblatihimu allatee kanoo AAalayha qul lillahi almashriqu waalmaghribu yahdee man yashao ila siratin mustaqeemin',
                                 'translation': 'The fools among the people '
                                                'will say: What has turned '
                                                'them from their qiblah which '
                                                'they had? Say: The East and '
                                                'the West belong only to '
                                                'Allah; He guides whom He '
                                                'likes to the right path.'},
                         'identifier': {'aya_id': 142,
                                        'gid': 149,
                                        'sura_arabic_name': 'البقرة',
                                        'sura_id': 2,
                                        'sura_name': 'Al-Baqarah'},
                         'position': {'hizb': 3,
                                      'juz': 2,
                                      'manzil': 1,
                                      'page': 22,
                                      'rub': 1},
                         'sajda': {'exist': False, 'id': None, 'type': None},
                         'stat': {},
                         'sura': {'arabic_name': 'البقرة',
                                  'arabic_type': 'مدنية',
                                  'ayas': 286,
                                  'english_name': 'The Cow',
                                  'id': 2,
                                  'name': 'Al-Baqarah',
                                  'order': 87,
                                  'stat': {},
                                  'type': 'Medinan'},
                         'theme': {}},
                     6: {'annotations': [],
                         'aya': {'id': 156,
                                 'next_aya': {'id': 157,
                                              'sura': 'Al-Baqarah',
                                              'sura_arabic': 'البقرة',
                                              'text': 'أُولَئِكَ عَلَيْهِمْ '
                                                      'صَلَوَاتٌ مِنْ '
                                                      'رَبِّهِمْ وَرَحْمَةٌ '
                                                      'وَأُولَئِكَ هُمُ '
                                                      'الْمُهْتَدُونَ'},
                                 'prev_aya': {'id': 155,
                                              'sura': 'Al-Baqarah',
                                              'sura_arabic': 'البقرة',
                                              'text': 'وَلَنَبْلُوَنَّكُمْ '
                                                      'بِشَيْءٍ مِنَ الْخَوْفِ '
                                                      'وَالْجُوعِ وَنَقْصٍ '
                                                      'مِنَ الْأَمْوَالِ '
                                                      'وَالْأَنْفُسِ '
                                                      'وَالثَّمَرَاتِ '
                                                      'وَبَشِّرِ '
                                                      'الصَّابِرِينَ'},
                                 'recitation': 'https://www.everyayah.com/data/Abdul_Basit_Murattal_192kbps/002156.mp3',
                                 'text': 'الَّذِينَ إِذَا أَصَابَتْهُمْ '
                                         'مُصِيبَةٌ قَالُوا إِنَّا <span '
                                         'class="match term0">لِلَّهِ</span> '
                                         'وَإِنَّا إِلَيْهِ رَاجِعُونَ',
                                 'text_no_highlight': 'الذين إذا أصابتهم مصيبة '
                                                      'قالوا إنا لله وإنا إليه '
                                                      'راجعون',
                                 'transliteration': 'Allatheena itha asabathum museebatun qaloo inna lillahi wainna ilayhi rajiAAoona',
                                 'translation': 'Who, when a misfortune '
                                                'befalls them, say: Surely we '
                                                "are Allah's and to Him we "
                                                'shall surely return.'},
                         'identifier': {'aya_id': 156,
                                        'gid': 163,
                                        'sura_arabic_name': 'البقرة',
                                        'sura_id': 2,
                                        'sura_name': 'Al-Baqarah'},
                         'position': {'hizb': 3,
                                      'juz': 2,
                                      'manzil': 1,
                                      'page': 24,
                                      'rub': 1},
                         'sajda': {'exist': False, 'id': None, 'type': None},
                         'stat': {},
                         'sura': {'arabic_name': 'البقرة',
                                  'arabic_type': 'مدنية',
                                  'ayas': 286,
                                  'english_name': 'The Cow',
                                  'id': 2,
                                  'name': 'Al-Baqarah',
                                  'order': 87,
                                  'stat': {},
                                  'type': 'Medinan'},
                         'theme': {}},
                     7: {'annotations': [],
                         'aya': {'id': 165,
                                 'next_aya': {'id': 166,
                                              'sura': 'Al-Baqarah',
                                              'sura_arabic': 'البقرة',
                                              'text': 'إِذْ تَبَرَّأَ '
                                                      'الَّذِينَ اتُّبِعُوا '
                                                      'مِنَ الَّذِينَ '
                                                      'اتَّبَعُوا وَرَأَوُا '
                                                      'الْعَذَابَ '
                                                      'وَتَقَطَّعَتْ بِهِمُ '
                                                      'الْأَسْبَابُ'},
                                 'prev_aya': {'id': 164,
                                              'sura': 'Al-Baqarah',
                                              'sura_arabic': 'البقرة',
                                              'text': 'إِنَّ فِي خَلْقِ '
                                                      'السَّمَاوَاتِ '
                                                      'وَالْأَرْضِ '
                                                      'وَاخْتِلَافِ اللَّيْلِ '
                                                      'وَالنَّهَارِ '
                                                      'وَالْفُلْكِ الَّتِي '
                                                      'تَجْرِي فِي الْبَحْرِ '
                                                      'بِمَا يَنْفَعُ النَّاسَ '
                                                      'وَمَا أَنْزَلَ اللَّهُ '
                                                      'مِنَ السَّمَاءِ مِنْ '
                                                      'مَاءٍ فَأَحْيَا بِهِ '
                                                      'الْأَرْضَ بَعْدَ '
                                                      'مَوْتِهَا وَبَثَّ '
                                                      'فِيهَا مِنْ كُلِّ '
                                                      'دَابَّةٍ وَتَصْرِيفِ '
                                                      'الرِّيَاحِ وَالسَّحَابِ '
                                                      'الْمُسَخَّرِ بَيْنَ '
                                                      'السَّمَاءِ وَالْأَرْضِ '
                                                      'لَآيَاتٍ لِقَوْمٍ '
                                                      'يَعْقِلُونَ'},
                                 'recitation': 'https://www.everyayah.com/data/Abdul_Basit_Murattal_192kbps/002165.mp3',
                                 'text': 'وَمِنَ النَّاسِ مَنْ يَتَّخِذُ مِنْ '
                                         'دُونِ اللَّهِ أَنْدَادًا '
                                         'يُحِبُّونَهُمْ كَحُبِّ اللَّهِ '
                                         'وَالَّذِينَ آمَنُوا أَشَدُّ حُبًّا '
                                         '<span class="match '
                                         'term0">لِلَّهِ</span> وَلَوْ يَرَى '
                                         'الَّذِينَ ظَلَمُوا إِذْ يَرَوْنَ '
                                         'الْعَذَابَ أَنَّ الْقُوَّةَ <span '
                                         'class="match term0">لِلَّهِ</span> '
                                         'جَمِيعًا وَأَنَّ اللَّهَ شَدِيدُ '
                                         'الْعَذَابِ',
                                 'text_no_highlight': 'ومن الناس من يتخذ من '
                                                      'دون الله أندادا يحبونهم '
                                                      'كحب الله والذين آمنوا '
                                                      'أشد حبا لله ولو يرى '
                                                      'الذين ظلموا إذ يرون '
                                                      'العذاب أن القوة لله '
                                                      'جميعا وأن الله شديد '
                                                      'العذاب',
                                 'transliteration': 'Wamina alnnasi man yattakhithu min dooni Allahi andadan yuhibboonahum kahubbi Allahi waallatheena amanoo ashaddu hubban lillahi walaw yara allatheena thalamoo ith yarawna alAAathaba anna alquwwata lillahi jameeAAan waanna Allaha shadeedu alAAathabi',
                                 'translation': 'And there are some among men '
                                                'who take for themselves '
                                                'objects of worship besides '
                                                'Allah, whom they love as they '
                                                'love Allah, and those who '
                                                'believe are stronger in love '
                                                'for Allah and O, that those '
                                                'who are unjust had seen, when '
                                                'they see the chastisement, '
                                                'that the power is wholly '
                                                "Allah's and that Allah is "
                                                'severe in requiting (evil).'},
                         'identifier': {'aya_id': 165,
                                        'gid': 172,
                                        'sura_arabic_name': 'البقرة',
                                        'sura_id': 2,
                                        'sura_name': 'Al-Baqarah'},
                         'position': {'hizb': 3,
                                      'juz': 2,
                                      'manzil': 1,
                                      'page': 25,
                                      'rub': 2},
                         'sajda': {'exist': False, 'id': None, 'type': None},
                         'stat': {},
                         'sura': {'arabic_name': 'البقرة',
                                  'arabic_type': 'مدنية',
                                  'ayas': 286,
                                  'english_name': 'The Cow',
                                  'id': 2,
                                  'name': 'Al-Baqarah',
                                  'order': 87,
                                  'stat': {},
                                  'type': 'Medinan'},
                         'theme': {}},
                     8: {'annotations': [],
                         'aya': {'id': 172,
                                 'next_aya': {'id': 173,
                                              'sura': 'Al-Baqarah',
                                              'sura_arabic': 'البقرة',
                                              'text': 'إِنَّمَا حَرَّمَ '
                                                      'عَلَيْكُمُ الْمَيْتَةَ '
                                                      'وَالدَّمَ وَلَحْمَ '
                                                      'الْخِنْزِيرِ وَمَا '
                                                      'أُهِلَّ بِهِ لِغَيْرِ '
                                                      'اللَّهِ فَمَنِ اضْطُرَّ '
                                                      'غَيْرَ بَاغٍ وَلَا '
                                                      'عَادٍ فَلَا إِثْمَ '
                                                      'عَلَيْهِ إِنَّ اللَّهَ '
                                                      'غَفُورٌ رَحِيمٌ'},
                                 'prev_aya': {'id': 171,
                                              'sura': 'Al-Baqarah',
                                              'sura_arabic': 'البقرة',
                                              'text': 'وَمَثَلُ الَّذِينَ '
                                                      'كَفَرُوا كَمَثَلِ '
                                                      'الَّذِي يَنْعِقُ بِمَا '
                                                      'لَا يَسْمَعُ إِلَّا '
                                                      'دُعَاءً وَنِدَاءً صُمٌّ '
                                                      'بُكْمٌ عُمْيٌ فَهُمْ '
                                                      'لَا يَعْقِلُونَ'},
                                 'recitation': 'https://www.everyayah.com/data/Abdul_Basit_Murattal_192kbps/002172.mp3',
                                 'text': 'يَا أَيُّهَا الَّذِينَ آمَنُوا '
                                         'كُلُوا مِنْ طَيِّبَاتِ مَا '
                                         'رَزَقْنَاكُمْ وَاشْكُرُوا <span '
                                         'class="match term0">لِلَّهِ</span> '
                                         'إِنْ كُنْتُمْ إِيَّاهُ تَعْبُدُونَ',
                                 'text_no_highlight': 'يا أيها الذين آمنوا '
                                                      'كلوا من طيبات ما '
                                                      'رزقناكم واشكروا لله إن '
                                                      'كنتم إياه تعبدون',
                                 'transliteration': 'Ya ayyuha allatheena amanoo kuloo min tayyibati ma razaqnakum waoshkuroo lillahi in kuntum iyyahu taAAbudoona',
                                 'translation': 'O you who believe! eat of the '
                                                'good things that We have '
                                                'provided you with, and give '
                                                'thanks to Allah if Him it is '
                                                'that you serve.'},
                         'identifier': {'aya_id': 172,
                                        'gid': 179,
                                        'sura_arabic_name': 'البقرة',
                                        'sura_id': 2,
                                        'sura_name': 'Al-Baqarah'},
                         'position': {'hizb': 3,
                                      'juz': 2,
                                      'manzil': 1,
                                      'page': 26,
                                      'rub': 2},
                         'sajda': {'exist': False, 'id': None, 'type': None},
                         'stat': {},
                         'sura': {'arabic_name': 'البقرة',
                                  'arabic_type': 'مدنية',
                                  'ayas': 286,
                                  'english_name': 'The Cow',
                                  'id': 2,
                                  'name': 'Al-Baqarah',
                                  'order': 87,
                                  'stat': {},
                                  'type': 'Medinan'},
                         'theme': {}},
                     9: {'annotations': [],
                         'aya': {'id': 193,
                                 'next_aya': {'id': 194,
                                              'sura': 'Al-Baqarah',
                                              'sura_arabic': 'البقرة',
                                              'text': 'الشَّهْرُ الْحَرَامُ '
                                                      'بِالشَّهْرِ الْحَرَامِ '
                                                      'وَالْحُرُمَاتُ قِصَاصٌ '
                                                      'فَمَنِ اعْتَدَى '
                                                      'عَلَيْكُمْ فَاعْتَدُوا '
                                                      'عَلَيْهِ بِمِثْلِ مَا '
                                                      'اعْتَدَى عَلَيْكُمْ '
                                                      'وَاتَّقُوا اللَّهَ '
                                                      'وَاعْلَمُوا أَنَّ '
                                                      'اللَّهَ مَعَ '
                                                      'الْمُتَّقِينَ'},
                                 'prev_aya': {'id': 192,
                                              'sura': 'Al-Baqarah',
                                              'sura_arabic': 'البقرة',
                                              'text': 'فَإِنِ انْتَهَوْا '
                                                      'فَإِنَّ اللَّهَ غَفُورٌ '
                                                      'رَحِيمٌ'},
                                 'recitation': 'https://www.everyayah.com/data/Abdul_Basit_Murattal_192kbps/002193.mp3',
                                 'text': 'وَقَاتِلُوهُمْ حَتَّى لَا تَكُونَ '
                                         'فِتْنَةٌ وَيَكُونَ الدِّينُ <span '
                                         'class="match term0">لِلَّهِ</span> '
                                         'فَإِنِ انْتَهَوْا فَلَا عُدْوَانَ '
                                         'إِلَّا عَلَى الظَّالِمِينَ',
                                 'text_no_highlight': 'وقاتلوهم حتى لا تكون '
                                                      'فتنة ويكون الدين لله '
                                                      'فإن انتهوا فلا عدوان '
                                                      'إلا على الظالمين',
                                 'transliteration': 'Waqatiloohum hatta la takoona fitnatun wayakoona alddeenu lillahi faini intahaw fala AAudwana illa AAala alththalimeena',
                                 'translation': 'And fight with them until '
                                                'there is no persecution, and '
                                                'religion should be only for '
                                                'Allah, but if they desist, '
                                                'then there should be no '
                                                'hostility except against the '
                                                'oppressors.'},
                         'identifier': {'aya_id': 193,
                                        'gid': 200,
                                        'sura_arabic_name': 'البقرة',
                                        'sura_id': 2,
                                        'sura_name': 'Al-Baqarah'},
                         'position': {'hizb': 3,
                                      'juz': 2,
                                      'manzil': 1,
                                      'page': 30,
                                      'rub': 0},
                         'sajda': {'exist': False, 'id': None, 'type': None},
                         'stat': {},
                         'sura': {'arabic_name': 'البقرة',
                                  'arabic_type': 'مدنية',
                                  'ayas': 286,
                                  'english_name': 'The Cow',
                                  'id': 2,
                                  'name': 'Al-Baqarah',
                                  'order': 87,
                                  'stat': {},
                                  'type': 'Medinan'},
                         'theme': {}},
                     10: {'annotations': [],
                          'aya': {'id': 196,
                                  'next_aya': {'id': 197,
                                               'sura': 'Al-Baqarah',
                                               'sura_arabic': 'البقرة',
                                               'text': 'الْحَجُّ أَشْهُرٌ '
                                                       'مَعْلُومَاتٌ فَمَنْ '
                                                       'فَرَضَ فِيهِنَّ '
                                                       'الْحَجَّ فَلَا رَفَثَ '
                                                       'وَلَا فُسُوقَ وَلَا '
                                                       'جِدَالَ فِي الْحَجِّ '
                                                       'وَمَا تَفْعَلُوا مِنْ '
                                                       'خَيْرٍ يَعْلَمْهُ '
                                                       'اللَّهُ وَتَزَوَّدُوا '
                                                       'فَإِنَّ خَيْرَ '
                                                       'الزَّادِ التَّقْوَى '
                                                       'وَاتَّقُونِ يَا أُولِي '
                                                       'الْأَلْبَابِ'},
                                  'prev_aya': {'id': 195,
                                               'sura': 'Al-Baqarah',
                                               'sura_arabic': 'البقرة',
                                               'text': 'وَأَنْفِقُوا فِي '
                                                       'سَبِيلِ اللَّهِ وَلَا '
                                                       'تُلْقُوا بِأَيْدِيكُمْ '
                                                       'إِلَى التَّهْلُكَةِ '
                                                       'وَأَحْسِنُوا إِنَّ '
                                                       'اللَّهَ يُحِبُّ '
                                                       'الْمُحْسِنِينَ'},
                                  'recitation': 'https://www.everyayah.com/data/Abdul_Basit_Murattal_192kbps/002196.mp3',
                                  'text': 'وَأَتِمُّوا الْحَجَّ وَالْعُمْرَةَ '
                                          '<span class="match '
                                          'term0">لِلَّهِ</span> فَإِنْ '
                                          'أُحْصِرْتُمْ فَمَا اسْتَيْسَرَ مِنَ '
                                          'الْهَدْيِ وَلَا تَحْلِقُوا '
                                          'رُءُوسَكُمْ حَتَّى يَبْلُغَ '
                                          'الْهَدْيُ مَحِلَّهُ فَمَنْ كَانَ '
                                          'مِنْكُمْ مَرِيضًا أَوْ بِهِ أَذًى '
                                          'مِنْ رَأْسِهِ فَفِدْيَةٌ مِنْ '
                                          'صِيَامٍ أَوْ صَدَقَةٍ أَوْ نُسُكٍ '
                                          'فَإِذَا أَمِنْتُمْ فَمَنْ تَمَتَّعَ '
                                          'بِالْعُمْرَةِ إِلَى الْحَجِّ فَمَا '
                                          'اسْتَيْسَرَ مِنَ الْهَدْيِ فَمَنْ '
                                          'لَمْ يَجِدْ فَصِيَامُ ثَلَاثَةِ '
                                          'أَيَّامٍ فِي الْحَجِّ وَسَبْعَةٍ '
                                          'إِذَا رَجَعْتُمْ تِلْكَ عَشَرَةٌ '
                                          'كَامِلَةٌ ذَلِكَ لِمَنْ لَمْ يَكُنْ '
                                          'أَهْلُهُ حَاضِرِي الْمَسْجِدِ '
                                          'الْحَرَامِ وَاتَّقُوا اللَّهَ '
                                          'وَاعْلَمُوا أَنَّ اللَّهَ شَدِيدُ '
                                          'الْعِقَابِ',
                                  'text_no_highlight': 'وأتموا الحج والعمرة '
                                                       'لله فإن أحصرتم فما '
                                                       'استيسر من الهدي ولا '
                                                       'تحلقوا رءوسكم حتى يبلغ '
                                                       'الهدي محله فمن كان '
                                                       'منكم مريضا أو به أذى '
                                                       'من رأسه ففدية من صيام '
                                                       'أو صدقة أو نسك فإذا '
                                                       'أمنتم فمن تمتع بالعمرة '
                                                       'إلى الحج فما استيسر من '
                                                       'الهدي فمن لم يجد فصيام '
                                                       'ثلاثة أيام في الحج '
                                                       'وسبعة إذا رجعتم تلك '
                                                       'عشرة كاملة ذلك لمن لم '
                                                       'يكن أهله حاضري المسجد '
                                                       'الحرام واتقوا الله '
                                                       'واعلموا أن الله شديد '
                                                       'العقاب',
                                  'transliteration': 'Waatimmoo alhajja waalAAumrata lillahi fain ohsirtum fama istaysara mina alhadyi wala tahliqoo ruoosakum hatta yablugha alhadyu mahillahu faman kana minkum mareedan aw bihi athan min rasihi fafidyatun min siyamin aw sadaqatin aw nusukin faitha amintum faman tamattaAAa bialAAumrati ila alhajji fama istaysara mina alhadyi faman lam yajid fasiyamu thalathati ayyamin fee alhajji wasabAAatin itha rajaAAtum tilka AAasharatun kamilatun thalika liman lam yakun ahluhu hadiree almasjidi alharami waittaqoo Allaha waiAAlamoo anna Allaha shadeedu alAAiqabi',
                                 'translation': 'And accomplish the '
                                                 'pilgrimage and the visit for '
                                                 'Allah, but if, you are '
                                                 'prevented, (send) whatever '
                                                 'offering is easy to obtain, '
                                                 'and do not shave your heads '
                                                 'until the offering reaches '
                                                 'its destination; but whoever '
                                                 'among you is sick or has an '
                                                 'ailment of the head, he '
                                                 '(should effect) a '
                                                 'compensation by fasting or '
                                                 'alms or sacrificing, then '
                                                 'when you are secure, whoever '
                                                 'profits by combining the '
                                                 'visit with the pilgrimage '
                                                 '(should take) what offering '
                                                 'is easy to obtain; but he '
                                                 'who cannot find (any '
                                                 'offering) should fast for '
                                                 'three days during the '
                                                 'pilgrimage and for seven '
                                                 'days when you return; these '
                                                 '(make) ten (days) complete; '
                                                 'this is for him whose family '
                                                 'is not present in the Sacred '
                                                 'Mosque, and be careful (of '
                                                 'your duty) to Allah, and '
                                                 'know that Allah is severe in '
                                                 'requiting (evil).'},
                          'identifier': {'aya_id': 196,
                                         'gid': 203,
                                         'sura_arabic_name': 'البقرة',
                                         'sura_id': 2,
                                         'sura_name': 'Al-Baqarah'},
                          'position': {'hizb': 3,
                                       'juz': 2,
                                       'manzil': 1,
                                       'page': 30,
                                       'rub': 0},
                          'sajda': {'exist': False, 'id': None, 'type': None},
                          'stat': {},
                          'sura': {'arabic_name': 'البقرة',
                                   'arabic_type': 'مدنية',
                                   'ayas': 286,
                                   'english_name': 'The Cow',
                                   'id': 2,
                                   'name': 'Al-Baqarah',
                                   'order': 87,
                                   'stat': {},
                                   'type': 'Medinan'},
                          'theme': {}}},
            'interval': {'end': 10,
                         'nb_pages': 12,
                         'page': 1.0,
                         'start': 1,
                         'total': 116},
            'translation_info': {},
            'words': {'global': {'nb_matches': 142,
                                 'nb_matches_overall': 142,
                                 'nb_ayas_overall': 138,
                                 'nb_ayas': 138,
                                 'nb_vocalizations': 0,
                                 'nb_words': 2}}}})  # end _strip_translation_text(expected)
    
    # # Compare words->individual separately (order-independent check)
    # assert sorted(actual_words_individual.keys()) == sorted(expected_words_individual.keys())
    # for key in expected_words_individual:
    #     assert actual_words_individual[key] == expected_words_individual[key]


def test_nb_matches_in_results():
    """Test that nb_matches counts word occurrences within the result set, not globally."""
    # Search for a word that appears in many places across the Quran
    # but filter to a single sura to ensure nb_matches < global nb_matches_overall
    search_flags = {
        "action": "search",
        "query": "الله",
        "word_info": True,
        "filter": {"sura_id": 1},  # Only Al-Fatihah (sura 1)
        "highlight": "none",
    }
    results = RAWoutput.do(search_flags)
    assert results["error"]["code"] == 0

    words = results["search"]["words"]
    global_info = words["global"]

    # nb_matches must be present (scoped to result set)
    assert "nb_matches" in global_info, "words.global must include nb_matches"

    # nb_matches_overall is global (all Quran), nb_matches is for the result set
    # Al-Fatihah has 1 aya with الله, Quran-wide has many more
    assert global_info["nb_matches"] <= global_info["nb_matches_overall"], (
        "nb_matches must not exceed nb_matches_overall"
    )
    assert global_info["nb_matches"] > 0, "should find at least one match in results"

    # Per-word data must also include nb_matches (scoped) and nb_matches_overall (global)
    for word_data in words["individual"].values():
        assert "nb_matches" in word_data, "words.individual entries must include nb_matches"
        assert "nb_matches_overall" in word_data, "words.individual entries must include nb_matches_overall"
        assert word_data["nb_matches"] <= word_data["nb_matches_overall"], (
            "per-word nb_matches must not exceed nb_matches_overall"
        )


def test_nb_matches_in_results_equals_global_when_unfiltered():
    """Test that nb_matches equals nb_matches_overall when results cover all occurrences."""
    # For a rare word that appears only a few times, an OR search returns all occurrences
    # so nb_matches should equal nb_matches_overall
    search_flags = {
        "action": "search",
        "query": "وزوجك",  # Rare word, appears only twice in the Quran
        "word_info": True,
        "highlight": "none",
    }
    results = RAWoutput.do(search_flags)
    assert results["error"]["code"] == 0

    words = results["search"]["words"]
    global_info = words["global"]

    assert "nb_matches" in global_info
    assert "nb_matches_overall" in global_info
    # Since the OR query returns all documents that contain the word,
    # nb_matches must equal nb_matches_overall
    assert global_info["nb_matches"] == global_info["nb_matches_overall"]


def test_nb_ayas_in_results():
    """Test that nb_ayas counts unique ayas within the result set, not globally."""
    search_flags = {
        "action": "search",
        "query": "الله",
        "word_info": True,
        "filter": {"sura_id": 1},  # Only Al-Fatihah (sura 1)
        "highlight": "none",
    }
    results = RAWoutput.do(search_flags)
    assert results["error"]["code"] == 0

    words = results["search"]["words"]
    global_info = words["global"]

    # nb_ayas must be present (scoped to result set)
    assert "nb_ayas" in global_info, "words.global must include nb_ayas"
    assert "nb_ayas_overall" in global_info, "words.global must include nb_ayas_overall"

    # nb_ayas_overall is global (all Quran), nb_ayas is for the result set
    # Al-Fatihah has 1 aya with الله, Quran-wide has many more
    assert global_info["nb_ayas"] <= global_info["nb_ayas_overall"], (
        "nb_ayas must not exceed nb_ayas_overall"
    )
    assert global_info["nb_ayas"] > 0, "should find at least one aya in results"

    # Per-word data must also include nb_ayas (scoped) and nb_ayas_overall (global)
    for word_data in words["individual"].values():
        assert "nb_ayas" in word_data, "words.individual entries must include nb_ayas"
        assert "nb_ayas_overall" in word_data, "words.individual entries must include nb_ayas_overall"
        assert word_data["nb_ayas"] <= word_data["nb_ayas_overall"], (
            "per-word nb_ayas must not exceed nb_ayas_overall"
        )


def test_nb_ayas_in_results_equals_overall_when_unfiltered():
    """Test that nb_ayas equals nb_ayas_overall when results cover all occurrences."""
    search_flags = {
        "action": "search",
        "query": "وزوجك",  # Rare word, appears only twice in the Quran
        "word_info": True,
        "highlight": "none",
    }
    results = RAWoutput.do(search_flags)
    assert results["error"]["code"] == 0

    words = results["search"]["words"]
    global_info = words["global"]

    assert "nb_ayas" in global_info
    assert "nb_ayas_overall" in global_info
    # Since the OR query returns all documents that contain the word,
    # nb_ayas must equal nb_ayas_overall
    assert global_info["nb_ayas"] == global_info["nb_ayas_overall"]


def test_search_translation_unit():
    search_flags = {
        "action": "search",
        "unit": "translation",
        "query": "praise",
        "page": 1,
        "highlight": "none",
    }
    results = RAWoutput.do(search_flags)
    assert "search" in results
    search = results["search"]
    assert search != {}, "translation search should not return empty dict"
    assert "interval" in search, "translation search should have 'interval' key"
    assert "translations" in search, "translation search should have 'translations' key"
    assert search["interval"]["total"] > 0, "translation search should find at least one result"
    # Verify structure of first result
    first = search["translations"][1]
    assert "identifier" in first
    assert "translation" in first
    assert "gid" in first["identifier"]
    assert "translation_id" in first["identifier"]
    assert "text" in first["translation"]


def test_search_translation_aya_text_is_uthmani():
    """_search_translation aya text should be Uthmani vocalized."""
    result = RAWoutput._search_translation({
        "query": "praise",
        "highlight": "none",
        "page": 1,
    })
    assert "translations" in result
    translations = result["translations"]
    if not translations:
        pytest.skip("No translation results — index may be unavailable")
    first = next(iter(translations.values()))
    assert "aya" in first, "Each translation result must include an 'aya' key"
    aya = first["aya"]
    assert "text" in aya, "'aya' must have a 'text' key"
    # The aya text should be non-None when the parent document is found
    # (None is acceptable only if the parent aya has no uth_ field stored)
    if aya["text"] is not None:
        assert aya["text"] != "", "aya.text should not be empty when present"


def test_search_word_unit_unavailable_engine():
    """Test that searching with unit='word' returns a structured response."""
    search_flags = {
        "action": "search",
        "unit": "word",
        "query": "الله",
        "page": 1,
        "highlight": "none",
    }
    results = RAWoutput.do(search_flags)
    assert "search" in results
    search = results["search"]
    assert search != {}, "word search should not return empty dict"
    # _search_words always returns a structured response with interval and words keys
    assert "interval" in search
    assert "words" in search


def test_search_words_returns_structured_response():
    """_search_words should return interval + words keys regardless of corpus availability."""
    result = RAWoutput._search_words({
        "query": "الله",
        "highlight": "none",
        "page": 1,
    })
    assert "interval" in result
    assert "words" in result
    assert isinstance(result["interval"], dict)
    assert isinstance(result["words"], dict)


def test_search_words_linguistic_field_query():
    """_search_words should accept field:value queries for linguistic properties."""
    result = RAWoutput._search_words({
        "query": "root:رحم",
        "highlight": "none",
        "page": 1,
    })
    assert "interval" in result
    assert "words" in result


def test_search_word_vocalizations_returns_list():
    """Test that vocalizations in search output returns a list of strings, not a single string."""
    search_flags = {
        "action": "search",
        "query": "الحمد لله",
        "page": 1,
        "word_info": True,
        "word_vocalizations": True,
        "highlight": "none",
    }
    results = RAWoutput.do(search_flags)
    assert "search" in results
    words_individual = results["search"]["words"]["individual"]
    for word_data in words_individual.values():
        vocalizations = word_data["vocalizations"]
        assert isinstance(vocalizations, list), (
            f"vocalizations should be a list, got {type(vocalizations).__name__}: {vocalizations!r}"
        )
        for v in vocalizations:
            assert isinstance(v, str), (
                f"each vocalization should be a string, got {type(v).__name__}: {v!r}"
            )
        assert word_data["nb_vocalizations"] == len(vocalizations)


def test_show_translations_shows_all_indexed_translations():
    """Test that show/translations returns exactly the indexed translations (no non-indexed ones)."""
    result = RAWoutput.do({"action": "show", "query": "translations"})
    assert "show" in result
    translations = result["show"]["translations"]

    # All indexed translations must be present in the result
    indexed_ids = set(RAWoutput.QSE.list_values("trans_id")) - {""}
    assert indexed_ids.issubset(set(translations.keys())), (
        "show/translations must include all indexed translations"
    )

    # The result must contain ONLY indexed translations (no non-indexed ones)
    assert set(translations.keys()) == indexed_ids, (
        "show/translations must not include non-indexed translations"
    )

    # Values should be human-readable names (not just the ID repeated)
    for id_key, name in translations.items():
        assert isinstance(name, str)
        # Human-readable name should either be a proper label or fall back to the ID
        assert name  # not empty


def test_show_roots_returns_strings_not_bytes():
    """show/roots must return plain Unicode strings, not binary b'...' values."""
    result = RAWoutput.do({"action": "show", "query": "roots"})
    assert "show" in result
    roots = result["show"]["roots"]
    assert isinstance(roots, list)
    for root in roots:
        assert isinstance(root, str), (
            f"Root value should be a str, got {type(root)!r}: {root!r}"
        )


def test_list_values_lemma_returns_strings_not_bytes():
    """list_values/lemma must return plain Unicode strings, not binary b'...' values."""
    result = RAWoutput.do({"action": "list_values", "field": "lemma"})
    assert "list_values" in result
    lv = result["list_values"]
    lemmas = lv["values"]
    assert isinstance(lemmas, list)
    assert len(lemmas) > 0, "Expected at least one lemma in the index"
    for lemma in lemmas:
        assert isinstance(lemma, str), (
            f"Lemma value should be a str, got {type(lemma)!r}: {lemma!r}"
        )


def test_list_values_lemma_is_fast():
    """list_values/lemma lookup must complete quickly (on-demand index scan).

    Unlike the old show/lemmas (a pre-built dict lookup, < 100 ms), this action
    performs a live Whoosh field_terms() scan of the word index on every call.
    The scan is still fast (single-pass through one B-tree), but inherently
    slower than a pre-loaded in-memory list, so the threshold is set to 2 s to
    accommodate slower CI machines without masking real regressions.
    """
    import time
    t0 = time.perf_counter()
    result = RAWoutput.do({"action": "list_values", "field": "lemma"})
    elapsed_ms = (time.perf_counter() - t0) * 1000
    assert elapsed_ms < 2000, (
        f"list_values/lemma took {elapsed_ms:.1f} ms, expected < 2000 ms"
    )
    assert result["list_values"]["values"]  # non-empty


def test_show_roots_is_fast():
    """show/roots lookup must complete quickly (field-specific index scan)."""
    import time
    t0 = time.perf_counter()
    result = RAWoutput.do({"action": "show", "query": "roots"})
    elapsed_ms = (time.perf_counter() - t0) * 1000
    assert elapsed_ms < 100, (
        f"show/roots took {elapsed_ms:.1f} ms, expected < 100 ms"
    )
    assert result["show"]["roots"]  # non-empty


def test_domains_view_has_correct_values():
    """DOMAINS['view'] must list all expected view modes as separate entries."""
    expected = {"minimal", "normal", "full", "statistic", "linguistic", "recitation", "custom"}
    assert set(Raw.DOMAINS["view"]) == expected, (
        f"DOMAINS['view'] has unexpected values: {Raw.DOMAINS['view']}"
    )


def test_view_minimal_limits_output():
    """view=minimal should suppress optional fields but keep text vocalized."""
    flags = {
        "action": "search",
        "query": "الله",
        "page": 1,
        "view": "minimal",
        "highlight": "none",
    }
    results = RAWoutput.do(flags)
    assert results["search"]["ayas"], "Expected at least one search result"
    aya = list(results["search"]["ayas"].values())[0]
    assert aya["aya"]["prev_aya"] is None
    assert aya["aya"]["next_aya"] is None
    assert aya["sura"] == {}
    assert aya["position"] == {}
    assert aya["stat"] == {}
    assert aya["sajda"] == {}
    assert aya["theme"] == {}
    # text should be vocalized (contain Arabic diacritical marks)
    assert re.search(r'[\u064B-\u0652]', aya["aya"]["text"]), \
        "Expected vocalized text in minimal view"


def test_view_minimal_keeps_translation():
    """view=minimal should preserve the translation when one is specified."""
    flags = {
        "action": "search",
        "query": "الله",
        "page": 1,
        "view": "minimal",
        "highlight": "none",
        "translation": "en.sahih",
    }
    results = RAWoutput.do(flags)
    assert results["search"]["ayas"], "Expected at least one search result"
    aya = list(results["search"]["ayas"].values())[0]
    assert aya["aya"]["translation"] is not None, \
        "Expected translation to be preserved in minimal view"


def test_view_normal_expands_output():
    """view=normal should include navigation but not sura info or stats."""
    flags = {
        "action": "search",
        "query": "الله",
        "page": 1,
        "view": "normal",
        "highlight": "none",
    }
    results = RAWoutput.do(flags)
    assert results["search"]["ayas"], "Expected at least one search result"
    aya = list(results["search"]["ayas"].values())[0]
    assert aya["aya"]["prev_aya"] is not None
    assert aya["aya"]["next_aya"] is not None
    assert aya["sura"] == {}
    assert aya["stat"] == {}
    assert aya["sajda"] != {}
    assert aya["theme"] != {}


def test_view_full_expands_output():
    """view=full should include all available fields in the search output."""
    flags = {
        "action": "search",
        "query": "الله",
        "page": 1,
        "view": "full",
        "highlight": "none",
    }
    results = RAWoutput.do(flags)
    assert results["search"]["ayas"], "Expected at least one search result"
    aya = list(results["search"]["ayas"].values())[0]
    assert aya["aya"]["prev_aya"] is not None
    assert aya["aya"]["next_aya"] is not None
    assert aya["sura"] != {}
    assert aya["sura"]["stat"] != {}
    assert aya["position"] != {}
    assert aya["theme"] != {}
    assert aya["stat"] != {}
    assert aya["sajda"] != {}
    assert "words" in aya, "word_linguistics should be True in full view"


def test_view_invalid_falls_back_to_custom():
    """An unrecognised view value should fall back to the 'custom' defaults."""
    flags_invalid = {
        "action": "search",
        "query": "الله",
        "page": 1,
        "view": "nonexistent_view",
        "highlight": "none",
    }
    flags_custom = {
        "action": "search",
        "query": "الله",
        "page": 1,
        "view": "custom",
        "highlight": "none",
    }
    result_invalid = RAWoutput.do(flags_invalid)
    result_custom = RAWoutput.do(flags_custom)
    assert result_invalid["search"]["ayas"], "Expected at least one search result"
    assert result_custom["search"]["ayas"], "Expected at least one search result"
    # Both should return the same set of aya keys (structure driven by custom defaults)
    keys_invalid = set(list(result_invalid["search"]["ayas"].values())[0].keys())
    keys_custom = set(list(result_custom["search"]["ayas"].values())[0].keys())
    assert keys_invalid == keys_custom


def test_fuzzy_search_highlights_variations():
    """Fuzzy search should highlight variation words (not just the exact query term).

    When fuzzy=True, Levenshtein-distance matching on 'aya_ac' expands the
    query to include related forms.  For example, searching for كتاب should
    also match and highlight كتابه (his book), كتابا (a book), كتابك
    (your book), and كتب (books).  Variation-matched results may rank lower
    than exact matches, so we search across all pages (using mushaf order)
    to ensure at least one variation word is highlighted.
    """
    from alfanous.text_processing import QArabicSymbolsFilter
    _strip = QArabicSymbolsFilter(shaping=False, tashkil=True, spellerrors=False, hamza=False).normalize_all

    search_flags = {
        "action": "search",
        "query": "كتاب",
        "fuzzy": True,
        "highlight": "css",
        "sortedby": "mushaf",
        "perpage": 300,
    }
    results = RAWoutput.do(search_flags)
    assert results["error"]["code"] == 0

    # Fuzzy search must return more results than non-fuzzy (includes variations)
    non_fuzzy_flags = {**search_flags, "fuzzy": False}
    non_fuzzy_results = RAWoutput.do(non_fuzzy_flags)
    assert results["search"]["interval"]["total"] > non_fuzzy_results["search"]["interval"]["total"], (
        "Fuzzy search should return more results than exact search"
    )

    highlighted_variation_found = False
    # Search across multiple pages to find variation-highlighted words,
    # since fuzzy-only matches may rank lower under relevance scoring.
    total = results["search"]["interval"]["total"]
    max_page = (total // 25) + 2
    for page in range(1, max_page):
        page_flags = {**search_flags, "page": page}
        page_results = RAWoutput.do(page_flags)
        for aya_data in page_results["search"]["ayas"].values():
            text = aya_data["aya"]["text"]
            if "<span" not in text:
                continue
            import re as _re
            spans = _re.findall(r"<span[^>]*>(.*?)</span>", text)
            for span in spans:
                stripped = _strip(span)
                if stripped != "كتاب":
                    highlighted_variation_found = True
                    break
            if highlighted_variation_found:
                break
        if highlighted_variation_found:
            break

    assert highlighted_variation_found, (
        "Fuzzy search must highlight variation words (e.g. كتابه، كتابا، كتب) "
        "in addition to the exact query term كتاب"
    )

def test_fuzzy_search_word_info_includes_variations():
    """Fuzzy search word_info should include a non-empty 'variations' list.

    When fuzzy=True and word_info=True, each word in words.individual must
    expose the fuzzy-matched variation terms via the 'variations' key.
    """
    search_flags = {
        "action": "search",
        "query": "كتاب",
        "fuzzy": True,
        "word_info": True,
        "highlight": "none",
    }
    results = RAWoutput.do(search_flags)
    assert results["error"]["code"] == 0

    words_individual = results["search"]["words"]["individual"]
    assert words_individual, "words.individual must not be empty"

    for word_data in words_individual.values():
        assert "variations" in word_data, (
            "words.individual entries must include 'variations' when fuzzy=True"
        )
        assert "nb_variations" in word_data, (
            "words.individual entries must include 'nb_variations' when fuzzy=True"
        )
        assert isinstance(word_data["variations"], list)
        assert word_data["nb_variations"] == len(word_data["variations"])

    # For كتاب with fuzzy, we expect variations like كتابا، كتابه، كتب, etc.
    first_word = words_individual[1]
    assert first_word["nb_variations"] > 0, (
        "Fuzzy search for كتاب must return at least one variation term"
    )
    assert "كتاب" in first_word["variations"], (
        "The query term itself should appear in the variations list"
    )


def test_non_fuzzy_search_variations_is_empty():
    """Non-fuzzy search must return empty variations list in word_info."""
    search_flags = {
        "action": "search",
        "query": "الحمد",
        "fuzzy": False,
        "word_info": True,
        "highlight": "none",
    }
    results = RAWoutput.do(search_flags)
    assert results["error"]["code"] == 0

    words_individual = results["search"]["words"]["individual"]
    assert words_individual, "words.individual must not be empty"

    for word_data in words_individual.values():
        assert "variations" in word_data, (
            "words.individual entries must always include 'variations' key"
        )
        assert "nb_variations" in word_data, (
            "words.individual entries must always include 'nb_variations' key"
        )
        assert word_data["variations"] == [], (
            "Non-fuzzy search must have empty variations list"
        )
        assert word_data["nb_variations"] == 0, (
            "Non-fuzzy search must have nb_variations == 0"
        )


def test_fuzzy_search_transliterated_query_no_stopiteration():
    """Fuzzy search with a fully transliterated (Latin-script) query must not raise StopIteration.

    Regression test for: fuzzy-mode search for 'muhammed rassoul allah' with
    fuzzy=True caused an unhandled StopIteration from inside the alfanous lib.

    The aya_fuzzy field uses an Arabic analyzer that includes a StopFilter and a
    stemmer.  When ALL tokens in the transliterated query are stop-words in that
    analyzer, Whoosh's internal MultiFilter calls next() on an empty token stream
    and raises StopIteration.  The fix wraps the aya_fuzzy parser call in a
    try/except so that Strategy 2 is gracefully skipped and the search continues
    with Strategies 1 and 3 instead of crashing.
    """
    search_flags = {
        "action": "search",
        "query": "muhammed rassoul allah",
        "fuzzy": True,
    }
    # Must not raise StopIteration (or any other unhandled exception)
    results = RAWoutput.do(search_flags)
    assert results["error"]["code"] == 0, (
        "Fuzzy search with transliterated query must succeed without error"
    )
    assert "search" in results


def test_fuzzy_search_field_query_no_crash():
    """Field query combined with fuzzy=True must not raise TypeError.

    Regression test for: searching with a field-qualified query such as
    ``a_g:1`` while ``fuzzy=True`` caused a crash:

        TypeError: '<=' not supported between instances of 'str' and 'int'

    When Whoosh parses a numeric field query (e.g. ``a_g:1``), it encodes the
    value as raw bytes (e.g. ``b'\\x00\\x80\\x00\\x00\\x01'``).  Iterating over
    a bytes object yields integers, and the Arabic-character check
    ``'\\u0600' <= c <= '\\u06FF'`` therefore raises TypeError because you
    cannot compare a str with an int.

    The fix adds an ``isinstance(term, str)`` guard in the Levenshtein subquery
    list-comprehension so that non-string (bytes/numeric) terms are skipped.
    """
    search_flags = {
        "action": "search",
        "query": "a_g:1",
        "fuzzy": True,
    }
    # Must not raise TypeError (or any other unhandled exception)
    results = RAWoutput.do(search_flags)
    assert results["error"]["code"] == 0, (
        "Field query with fuzzy=True must succeed without error"
    )
    assert "search" in results
    assert results["search"]["interval"]["total"] > 0, (
        "a_g:1 with fuzzy=True must return results, not an empty set"
    )


def test_fuzzy_field_query_matches_same_as_non_fuzzy():
    """Field-qualified numeric query ``a_g:1`` must return the same results
    in fuzzy mode as in non-fuzzy mode.

    Fuzzy mode's extra Levenshtein/aya_fuzzy strategies only apply to
    Arabic-script text terms; they must not interfere with the exact numeric
    match for field-qualified queries like ``a_g:1``.
    """
    base_flags = {"action": "search", "query": "a_g:1"}
    non_fuzzy = RAWoutput.do({**base_flags, "fuzzy": False})
    fuzzy = RAWoutput.do({**base_flags, "fuzzy": True})

    assert non_fuzzy["error"]["code"] == 0, "Non-fuzzy a_g:1 must succeed"
    assert fuzzy["error"]["code"] == 0, "Fuzzy a_g:1 must succeed"

    non_fuzzy_total = non_fuzzy["search"]["interval"]["total"]
    fuzzy_total = fuzzy["search"]["interval"]["total"]

    assert non_fuzzy_total > 0, "a_g:1 (non-fuzzy) must return results"
    assert fuzzy_total >= non_fuzzy_total, (
        f"Fuzzy search must return at least as many results as non-fuzzy "
        f"(fuzzy={fuzzy_total}, non_fuzzy={non_fuzzy_total})"
    )


def test_non_arabic_aya_search_highlights_translation():
    """Non-Arabic aya search with highlight=css should highlight keywords in translation text.

    When the query contains no Arabic characters (e.g. 'mercy'), the search
    matches ayas via their translation children.  The translation text returned
    in each result's aya.translation field must have the matching keywords
    wrapped in <span class="match ..."> tags when highlight != 'none'.
    """
    search_flags = {
        "action": "search",
        "unit": "aya",
        "query": "mercy",
        "highlight": "css",
        "translation": "en.sahih",
        "page": 1,
    }
    results = RAWoutput.do(search_flags)
    assert results["error"]["code"] == 0
    ayas = results["search"]["ayas"]
    assert ayas, "Non-Arabic search should return at least one result"

    highlighted_found = any(
        aya_data["aya"]["translation"] and "<span" in aya_data["aya"]["translation"]
        for aya_data in ayas.values()
    )

    assert highlighted_found, (
        "Translation text must contain highlighted <span> tags for non-Arabic aya search"
    )


def test_non_arabic_aya_search_no_highlight_when_highlight_none():
    """Non-Arabic aya search with highlight=none should return plain translation text."""
    search_flags = {
        "action": "search",
        "unit": "aya",
        "query": "mercy",
        "highlight": "none",
        "translation": "en.sahih",
        "page": 1,
    }
    results = RAWoutput.do(search_flags)
    assert results["error"]["code"] == 0
    ayas = results["search"]["ayas"]
    assert ayas, "Non-Arabic search should return at least one result"

    for aya_data in ayas.values():
        translation_text = aya_data["aya"]["translation"]
        if translation_text:
            assert "<span" not in translation_text, (
                "Translation text must not contain highlight spans when highlight=none"
            )


def test_search_words_includes_aya_text():
    """_search_words results should include the parent aya text in each word entry."""
    result = RAWoutput._search_words({
        "query": "root:رحم",
        "highlight": "none",
        "page": 1,
    })
    assert "words" in result
    words = result["words"]
    if not words:
        pytest.skip("No word results for root:رحم — index may be unavailable")
    for entry in words.values():
        assert "aya" in entry, "Each word result must include an 'aya' key"
        aya = entry["aya"]
        assert "text" in aya, "'aya' must have a 'text' key"
        assert "text_no_highlight" in aya, "'aya' must have a 'text_no_highlight' key"
        # text should not be empty when the index is built with corpus data
        assert aya["text"] not in (None, ""), "aya.text should be populated"


def test_search_words_aya_text_uthmani_script():
    """_search_words should always return Uthmani vocalized aya text."""
    result = RAWoutput._search_words({
        "query": "root:رحم",
        "highlight": "none",
        "page": 1,
        "script": "uthmani",
    })
    assert "words" in result
    words = result["words"]
    if not words:
        pytest.skip("No word results for root:رحم — index may be unavailable")
    for entry in words.values():
        assert "aya" in entry, "Each word result must include an 'aya' key"
        aya = entry["aya"]
        assert "text" in aya, "'aya' must have a 'text' key"
        assert "text_no_highlight" in aya, "'aya' must have a 'text_no_highlight' key"
        assert aya["text"] not in (None, ""), "aya.text should be populated"


def test_search_words_aya_text_always_uthmani():
    """_search_words aya text should be Uthmani vocalized regardless of script flag."""
    result_standard = RAWoutput._search_words({
        "query": "root:رحم",
        "highlight": "none",
        "page": 1,
        "script": "standard",
    })
    result_uthmani = RAWoutput._search_words({
        "query": "root:رحم",
        "highlight": "none",
        "page": 1,
        "script": "uthmani",
    })
    if not result_standard.get("words") or not result_uthmani.get("words"):
        pytest.skip("No word results — index may be unavailable")
    # Both script flags should produce the same Uthmani vocalized aya text
    first_std = next(iter(result_standard["words"].values()))
    first_uth = next(iter(result_uthmani["words"].values()))
    std_text = first_std["aya"]["text_no_highlight"]
    uth_text = first_uth["aya"]["text_no_highlight"]
    assert std_text, "Aya text must not be empty"
    assert uth_text, "Aya text must not be empty"
    assert std_text == uth_text, (
        "Aya text should be Uthmani vocalized regardless of the script flag; "
        "got different values"
    )


def test_search_words_facets_root():
    """_search_words should return facet counts for 'root' when requested."""
    result = RAWoutput._search_words({
        "query": "root:رحم",
        "highlight": "none",
        "page": 1,
        "facets": "root",
    })
    assert "words" in result
    if not result["words"]:
        pytest.skip("No word results — index may be unavailable")
    assert "facets" in result, "_search_words must include 'facets' key when facets= is set"
    assert "root" in result["facets"], "'root' must be present in facets output"
    facet_entries = result["facets"]["root"]
    assert isinstance(facet_entries, list), "facets['root'] must be a list"
    for entry in facet_entries:
        assert "value" in entry and "count" in entry


def test_search_words_facets_type():
    """_search_words should return facets for type when requested."""
    result = RAWoutput._search_words({
        "query": "الله",
        "highlight": "none",
        "page": 1,
        "facets": "type",
    })
    assert "words" in result
    if not result["words"]:
        pytest.skip("No word results — index may be unavailable")
    assert "facets" in result
    assert "type" in result["facets"]


def test_search_words_facets_lemma_included():
    """lemma is in _WORD_FACET_FIELDS, so it must appear in facets output."""
    result = RAWoutput._search_words({
        "query": "الله",
        "highlight": "none",
        "page": 1,
        "facets": "lemma,type",
    })
    assert "words" in result
    if not result["words"]:
        pytest.skip("No word results — index may be unavailable")
    assert "facets" in result
    # Both 'type' and 'lemma' are in _WORD_FACET_FIELDS → both must appear
    assert "type" in result["facets"]
    assert "lemma" in result["facets"]


def test_search_words_facets_unknown_field_ignored():
    """Facet fields not in _WORD_FACET_FIELDS should be silently ignored."""
    result = RAWoutput._search_words({
        "query": "root:رحم",
        "highlight": "none",
        "page": 1,
        "facets": "sura_id,root",   # sura_id is not in _WORD_FACET_FIELDS
    })
    assert "words" in result
    if not result["words"]:
        pytest.skip("No word results — index may be unavailable")
    assert "facets" in result
    # 'root' allowed; 'sura_id' should be silently dropped
    assert "root" in result["facets"]
    assert "sura_id" not in result["facets"]


def test_search_translation_facets_exception_does_not_propagate(monkeypatch):
    """When facet computation raises an exception (simulating a ValueError
    from a closed Whoosh reader), ``_search_translation`` must still return a
    valid output dict rather than propagating the error.  The logger.warning()
    calls in the except blocks must not raise ``NameError``.
    """
    from unittest.mock import patch
    from whoosh.sorting import Facets

    # Patch `Facets` used inside _search_translation to raise ValueError,
    # mimicking ``ValueError: I/O operation on closed file`` from Whoosh.
    with patch("alfanous.outputs.Facets", side_effect=ValueError("I/O operation on closed file")):
        result = RAWoutput._search_translation({
            "query": "praise",
            "highlight": "none",
            "page": 1,
            "facets": "trans_lang",
        })

    # The method must return a structured dict (not raise).
    assert isinstance(result, dict), "_search_translation must return a dict even when facets raise"
    assert "interval" in result or "translations" in result, (
        "_search_translation result must contain 'interval' or 'translations'"
    )


def test_search_aya_words_individual_always_populated():
    """words.individual must always contain matched terms, even without word_info=True.

    The words.individual list exposes which keywords were matched by the search
    engine — the same terms used internally for highlighting — so callers can
    see matched words without having to parse highlighted spans or request full
    word_info details.
    """
    result = RAWoutput.do({
        "action": "search",
        "query": "الحمد",
        "highlight": "none",
        # word_info deliberately omitted (defaults to False)
    })
    assert result["error"]["code"] == 0
    search = result["search"]
    individual = search["words"]["individual"]
    assert len(individual) > 0, "words.individual must not be empty for a matching query"
    words = [entry["word"] for entry in individual.values()]
    # The searched word should appear as-is (possibly vocalized) in the matched terms
    assert any(w == "الحمد" or w.replace("\u064e\u064f\u064b\u064c\u0650\u064d\u0651\u0652", "") == "الحمد"
               for w in words), (
        "Searched word الحمد must appear in words.individual"
    )
    # Minimal entry must have at least 'word' and 'variations' keys
    for entry in individual.values():
        assert "word" in entry
        assert "variations" in entry


def test_search_aya_fuzzy_words_individual_includes_variations():
    """Fuzzy aya search: words.individual must include variation terms even without word_info.

    When fuzzy=True, the engine expands the query via Levenshtein matching on
    the aya_ac field.  All actually-matched variation terms must appear in
    words.individual[N]["variations"] so callers can display all matched forms.
    Uses كتاب (4 chars) which qualifies for Levenshtein expansion.
    """
    result = RAWoutput.do({
        "action": "search",
        "query": "كتاب",
        "fuzzy": True,
        "highlight": "none",
        # word_info deliberately omitted (defaults to False)
    })
    assert result["error"]["code"] == 0
    search = result["search"]
    individual = search["words"]["individual"]
    assert len(individual) > 0, "words.individual must not be empty for a matching query"

    # Fuzzy search for كتاب should match several verb forms in the variations list
    all_variations = [v for entry in individual.values() for v in entry.get("variations", [])]
    assert len(all_variations) > 0, (
        "Fuzzy search for كتاب must expose variation terms in words.individual"
    )

    # Every non-fuzzy matched word must also appear in the fuzzy matched words,
    # confirming fuzzy is a superset of the exact search.
    non_fuzzy_result = RAWoutput.do({
        "action": "search",
        "query": "كتاب",
        "fuzzy": False,
        "highlight": "none",
    })
    non_fuzzy_individual = non_fuzzy_result["search"]["words"]["individual"]
    fuzzy_word_set = {entry["word"] for entry in individual.values()}
    for entry in non_fuzzy_individual.values():
        assert entry["word"] in fuzzy_word_set, (
            f"Non-fuzzy matched word {entry['word']!r} must also appear in fuzzy results"
        )
def test_aya_search_out_of_bounds_page_returns_consistent_interval():
    """When the requested page is beyond the last page, interval fields must be consistent.

    Before the fix, requesting a page far beyond the result count produced an
    ``end`` equal to ``total`` (instead of 0) and a non-integer ``page`` value
    like 0.8 — both of which are incorrect.
    """
    result = RAWoutput.do({
        "action": "search",
        "query": "الرحمن",   # ~45 results → 5 pages
        "page": 9999,
        "highlight": "none",
    })
    interval = result["search"]["interval"]
    assert interval["start"] == -1, "out-of-bounds page should yield start == -1"
    assert interval["end"] == 0, "out-of-bounds page should yield end == 0 (not total)"
    assert interval["page"] == 0, "out-of-bounds page should yield page == 0 (not fractional)"
    assert interval["nb_pages"] > 0, "nb_pages should reflect total pages available"
    assert result["search"]["ayas"] == {}, "no aya results expected for out-of-bounds page"


def test_translation_search_out_of_bounds_page_returns_consistent_interval():
    """Same out-of-bounds interval fix applies to the translation search unit."""
    result = RAWoutput.do({
        "action": "search",
        "query": "god",
        "unit": "translation",
        "page": 9999,
        "highlight": "none",
    })
    interval = result["search"]["interval"]
    assert interval["start"] == -1, "out-of-bounds page should yield start == -1"
    assert interval["end"] == 0, "out-of-bounds page should yield end == 0 (not total)"
    assert interval["page"] == 0, "out-of-bounds page should yield page == 0 (not fractional)"
    assert interval["nb_pages"] > 0, "nb_pages should reflect total pages available"
    assert result["search"]["translations"] == {}, "no translation results expected for out-of-bounds page"


def test_word_search_out_of_bounds_page_returns_consistent_interval():
    """Same out-of-bounds interval fix applies to the word search unit."""
    result = RAWoutput.do({
        "action": "search",
        "query": "الله",
        "unit": "word",
        "page": 9999,
        "highlight": "none",
    })
    interval = result["search"]["interval"]
    assert interval["start"] == -1, "out-of-bounds page should yield start == -1"
    assert interval["end"] == 0, "out-of-bounds page should yield end == 0 (not total)"
    assert interval["page"] == 0, "out-of-bounds page should yield page == 0 (not 1)"
    assert interval["nb_pages"] > 0, "nb_pages should reflect total pages available"
    assert result["search"]["words"] == {}, "no word results expected for out-of-bounds page"



def test_english_keyword_appears_in_words_individual():
    """English keywords like 'fire' must appear in words.individual.

    Regression test for: non-Arabic (English) query keywords were absent from
    words.individual because search_with_query always returned empty termz and
    the population loop only processed aya/aya_ field terms.
    """
    search_flags = {
        "action": "search",
        "query": "fire",
        "highlight": "none",
    }
    results = RAWoutput.do(search_flags)
    assert results["error"]["code"] == 0
    assert results["search"]["interval"]["total"] > 0, "Expected results for 'fire'"

    words_individual = results["search"]["words"]["individual"]
    assert words_individual, (
        "words.individual must not be empty for an English keyword search"
    )
    word_texts = [entry["word"] for entry in words_individual.values()]
    assert any("fire" in w for w in word_texts), (
        f"'fire' (or its stemmed form) must appear in words.individual; got: {word_texts}"
    )


def test_english_keyword_appears_in_words_individual_with_word_info():
    """English keywords must appear in words.individual even when word_info=True."""
    search_flags = {
        "action": "search",
        "query": "fire",
        "word_info": True,
        "highlight": "none",
    }
    results = RAWoutput.do(search_flags)
    assert results["error"]["code"] == 0

    words_individual = results["search"]["words"]["individual"]
    assert words_individual, (
        "words.individual must not be empty for an English keyword search with word_info=True"
    )
    word_texts = [entry["word"] for entry in words_individual.values()]
    assert any("fire" in w for w in word_texts), (
        f"'fire' (or its stemmed form) must appear in words.individual with word_info=True; got: {word_texts}"
    )
    # Each entry must have the standard word_info keys
    for entry in words_individual.values():
        assert "nb_matches_overall" in entry
        assert "nb_ayas_overall" in entry
        assert "variations" in entry
        assert isinstance(entry["variations"], list)


def test_arabizi_query_arabic_in_words_individual():
    """Arabizi query (e.g. 'qawl') should include the mapped Arabic word (قول)
    in words.individual so callers know which Arabic keywords were matched.
    """
    search_flags = {
        "action": "search",
        "query": "qawl",
        "highlight": "none",
    }
    results = RAWoutput.do(search_flags)
    assert results["error"]["code"] == 0

    if results["search"]["interval"]["total"] == 0:
        pytest.skip("'qawl' returned no results — arabizi conversion may not include قول")

    words_individual = results["search"]["words"]["individual"]
    assert words_individual, (
        "words.individual must not be empty for an arabizi query"
    )
    word_texts = [entry["word"] for entry in words_individual.values()]
    # The mapped Arabic word 'قول' (or one of its forms) must appear.
    # Use the range \u0621-\u064A which covers standard Arabic letters and
    # common diacritics, excluding non-letter Arabic block symbols.
    assert any("\u0621" <= c <= "\u064A" for w in word_texts for c in w), (
        f"words.individual must contain at least one Arabic word for arabizi query 'qawl'; "
        f"got: {word_texts}"
    )


def test_arabizi_query_highlights_arabic_text():
    """Arabizi query (e.g. 'qawl') should highlight the matched Arabic words
    in the aya text, not leave them un-highlighted.
    """
    search_flags = {
        "action": "search",
        "query": "qawl",
        "highlight": "css",
    }
    results = RAWoutput.do(search_flags)
    assert results["error"]["code"] == 0

    if results["search"]["interval"]["total"] == 0:
        pytest.skip("'qawl' returned no results — arabizi conversion may not include قول")

    # At least one result must have a highlighted Arabic span
    highlighted_found = False
    for aya_data in results["search"]["ayas"].values():
        text = aya_data["aya"]["text"]
        if "<span" in text:
            highlighted_found = True
            break

    assert highlighted_found, (
        "Arabizi query 'qawl' must produce highlighted Arabic text in search results"
    )


def test_fuzzy_derivation_highlights_derivation_words():
    """derivation_level=3 (root) must highlight derivation-matched words in aya text.

    When derivation_level=3 the query is expanded with morphological
    derivations of the search term.  For example, searching 'ملك' expands to
    include 'مالك', 'يملك', etc.
    """
    from alfanous.text_processing import QArabicSymbolsFilter
    _strip = QArabicSymbolsFilter(
        shaping=False, tashkil=True, spellerrors=False, hamza=False
    ).normalize_all

    query_term = "ملك"
    search_flags = {
        "action": "search",
        "query": query_term,
        "fuzzy": True,
        "derivation_level": 3,
        "highlight": "css",
        "perpage": 300,
    }
    results = RAWoutput.do(search_flags)
    assert results["error"]["code"] == 0

    # Derivation search must return more results than plain exact search
    exact_flags = {**search_flags, "fuzzy": False, "derivation_level": 0}
    exact_results = RAWoutput.do(exact_flags)
    assert (
        results["search"]["interval"]["total"]
        >= exact_results["search"]["interval"]["total"]
    ), "fuzzy search with derivation_level=3 must return at least as many results as exact search"

    # At least one derivation word (something OTHER than 'ملك' itself) must be
    # highlighted — confirming that derivation terms are in the highlight list.
    highlighted_derivation_found = False
    for aya_data in results["search"]["ayas"].values():
        text = aya_data["aya"]["text"]
        if "<span" not in text:
            continue
        spans = re.findall(r"<span[^>]*>(.*?)</span>", text)
        for span in spans:
            stripped = _strip(span)
            if stripped != query_term:
                highlighted_derivation_found = True
                break
        if highlighted_derivation_found:
            break

    assert highlighted_derivation_found, (
        f"When derivation_level=3, derivation words (e.g. مالك، يملك) must be highlighted "
        f"in addition to the exact query term {query_term!r}"
    )


def test_fuzzy_derivation_words_individual_includes_expansions():
    """words.individual must include derivation-expansion terms when derivation_level=3 (root).

    The requirement is that "words.individual should include the expansions"
    and "any thing highlighted should be in words.individual".  When
    derivation_level=3, matched derivation words (e.g. 'مالك', 'يملك' for
    a query of 'ملك') must appear as entries in words.individual.
    """
    query_term = "ملك"
    search_flags = {
        "action": "search",
        "query": query_term,
        "fuzzy": True,
        "derivation_level": 3,
        "word_info": True,
        "highlight": "none",
    }
    results = RAWoutput.do(search_flags)
    assert results["error"]["code"] == 0

    words_individual = results["search"]["words"]["individual"]
    assert words_individual, "words.individual must not be empty"

    # The query word must appear in words.individual
    word_texts = [entry["word"] for entry in words_individual.values()]
    assert query_term in word_texts, (
        f"User's query word {query_term!r} must appear in words.individual; got: {word_texts}"
    )

    from alfanous.text_processing import QArabicSymbolsFilter
    _strip = QArabicSymbolsFilter(
        shaping=False, tashkil=True, spellerrors=False, hamza=False
    ).normalize_all

    # At least one derivation word (something OTHER than the query term) must
    # also be present — confirming that expansion terms are included.
    derivation_found = any(
        _strip(entry["word"]) != query_term
        for entry in words_individual.values()
    )
    assert derivation_found, (
        f"words.individual must contain at least one derivation word (not just {query_term!r}) "
        f"when derivation_level=3 — all expanded keywords must be listed"
    )

    # No entry in words.individual should be a vocalized Arabic string.
    # Vocalized strings contain Arabic diacritic characters (U+064B–U+065F).
    _ARABIC_DIACRITIC_RE = re.compile(r'[\u064B-\u065F]')
    for entry in words_individual.values():
        w = entry.get("word", "")
        assert not _ARABIC_DIACRITIC_RE.search(w), (
            f"words.individual must not contain vocalized keywords in derivation search; "
            f"found vocalized word {w!r}"
        )


def test_pure_wildcard_search_returns_quickly_without_error():
    """A bare wildcard query (* or ?) must return quickly with no error.

    Pure-wildcard queries have no alphabetic content so they would expand
    the translation NestedParent search across every term in every translation
    field — an operation that exceeds any reasonable timelimit.  The fix
    short-circuits such queries before the expensive translation search,
    returning empty results immediately.

    Regression test for: "exceeding timelimit with wildcards search"
    """
    import time

    for query in ("*", "?", "؟", "* ?", "؟*"):
        search_flags = {
            "action": "search",
            "query": query,
            "timelimit": "5",
        }
        t0 = time.monotonic()
        results = RAWoutput.do(search_flags)
        elapsed = time.monotonic() - t0

        # Must complete well under the configured timelimit (5 s above).
        # 2 s is a generous ceiling: the short-circuit path should finish in
        # milliseconds; anything above 2 s indicates the translation search
        # was NOT skipped and the timelimit is being approached.
        assert elapsed < 2.0, (
            f"Pure-wildcard query {query!r} took {elapsed:.3f}s — "
            "translation NestedParent search was not skipped"
        )
        assert results["error"]["code"] == 0, (
            f"Pure-wildcard query {query!r} returned an error: {results['error']}"
        )


def test_lang_trans_parsers_populated_per_language():
    """Raw._lang_trans_parsers must contain an entry for each available text_* field.

    When the index is built with translation fields (e.g. text_en, text_fr),
    _lang_trans_parsers should have one per-language parser for every language
    whose field is present in the schema.  This ensures that the non-Arabic
    search path can use a search_lang-scoped parser when ``search_lang`` is specified.
    """
    from alfanous.text_processing import _TRANSLATION_LANGS

    schema_fields = set(RAWoutput.QSE._schema.names())
    expected_langs = [lc for lc in _TRANSLATION_LANGS if f"text_{lc}" in schema_fields]

    for lc in expected_langs:
        assert lc in RAWoutput._lang_trans_parsers, (
            f"_lang_trans_parsers must have an entry for lang={lc!r}"
        )
        assert lc in RAWoutput._lang_trans_fields, (
            f"_lang_trans_fields must have an entry for lang={lc!r}"
        )
        assert RAWoutput._lang_trans_fields[lc] == frozenset([f"text_{lc}"]), (
            f"_lang_trans_fields[{lc!r}] must be exactly {{text_{lc}}}"
        )


def test_non_arabic_search_with_lang_restricts_to_lang_field():
    """When search_lang='en' is passed, a non-Arabic query must search only text_en.

    Specifying ``search_lang`` on an aya search with a non-Arabic query restricts
    the translation search to the corresponding ``text_{lang}`` field and ignores
    all other translation fields.

    We verify this by checking that the query issued by the non-Arabic path
    only targets ``text_en`` (and not ``text_fr``, ``text_ar``, etc.) when
    ``search_lang='en'`` is given, by inspecting which fields the parsed query uses.
    This is done via the per-language parser stored on the Raw instance.
    """
    from whoosh.qparser import MultifieldParser

    # Confirm the search_lang-scoped parser for 'en' targets only text_en.
    if "en" not in RAWoutput._lang_trans_parsers:
        pytest.skip("text_en field not in index - cannot test lang scoping for 'en'")

    en_parser = RAWoutput._lang_trans_parsers["en"]
    q = en_parser.parse("mercy")
    all_fields = {f for f, _ in q.all_terms()}
    assert all_fields == {"text_en"}, (
        f"Lang-scoped parser for 'en' must produce terms only in text_en, got: {all_fields}"
    )

    # Verify the all-languages parser covers more than one field.
    if RAWoutput._trans_parser is not None:
        q_all = RAWoutput._trans_parser.parse("mercy")
        all_fields_all = {f for f, _ in q_all.all_terms()}
        assert len(all_fields_all) > 1, (
            "The all-languages _trans_parser must target more than one field"
        )


def test_non_arabic_aya_search_with_lang_returns_results():
    """Non-Arabic aya search with search_lang='en' must return results.

    Regression test: when search_lang is passed, the non-Arabic path must still
    produce search results (it should search text_en, not fall through to
    an empty parser or be silently skipped).
    """
    result = RAWoutput.do({
        "action": "search",
        "unit": "aya",
        "query": "mercy",
        "search_lang": "en",
        "highlight": "none",
        "page": 1,
    })
    assert result["error"]["code"] == 0, f"Search returned error: {result['error']}"
    ayas = result["search"]["ayas"]
    assert ayas, (
        "Non-Arabic search with search_lang='en' must return at least one aya result"
    )


def test_latin_keywords_have_translation_hint():
    """Latin keywords matching translation text should have a language hint in words.individual.

    When a Latin/English query (e.g. 'heaven') matches aya text via translation fields,
    the resulting words.individual entries must include a 'hint' key naming the translation
    language (e.g. 'english') so API consumers can distinguish translation matches from
    direct Arabic text matches.
    """
    # Search with a Latin/English word that matches translation text
    results = RAWoutput.do({
        "action": "search",
        "query": "heaven",
        "word_info": True,
        "highlight": "none",
    })
    assert results["error"]["code"] == 0
    search = results.get("search", {})
    words = search.get("words", {})
    individual = words.get("individual", {})

    # There must be at least one keyword entry
    assert individual, "Expected at least one keyword in words.individual for 'heaven'"

    # No keyword entry should have hint='aya' (that's for Arabic text matches)
    for key, word_data in individual.items():
        if "hint" in word_data:
            assert word_data["hint"] != "aya", (
                f"words.individual[{key}] should not have hint='aya' for a translation match: {word_data!r}"
            )

    # At least one keyword should have a translation-language hint (not None, not 'aya')
    _translation_hints = {wd["hint"] for wd in individual.values() if "hint" in wd}
    assert _translation_hints, (
        f"Expected at least one keyword with a translation hint, got individual: {individual}"
    )


def test_arabic_keywords_have_no_hint():
    """Arabic keywords in aya search should NOT have a 'hint' key in words.individual."""
    results = RAWoutput.do({
        "action": "search",
        "query": "الله",
        "word_info": True,
        "highlight": "none",
    })
    assert results["error"]["code"] == 0
    search = results.get("search", {})
    words = search.get("words", {})
    individual = words.get("individual", {})

    assert individual, "Expected at least one keyword in words.individual for 'الله'"

    for key, word_data in individual.items():
        assert "hint" not in word_data, (
            f"words.individual[{key}] should not have a 'hint' key for Arabic aya keyword, "
            f"got hint={word_data['hint']!r}"
        )


def test_hint_present_without_word_info():
    """Translation hint should appear in words.individual even without word_info=True."""
    results = RAWoutput.do({
        "action": "search",
        "query": "heaven",
        "word_info": False,
        "highlight": "none",
    })
    assert results["error"]["code"] == 0
    search = results.get("search", {})
    words = search.get("words", {})
    individual = words.get("individual", {})

    assert individual, "Expected at least one keyword in words.individual for 'heaven'"

    _translation_hints = {wd["hint"] for wd in individual.values() if "hint" in wd}
    assert _translation_hints, (
        f"Expected at least one keyword with a translation hint (word_info=False), "
        f"got individual: {individual}"
    )


def test_arabic_tafsir_keyword_hint():
    """Arabic translation (tafsir) keywords should have hint='tafsir' in words.individual."""
    # Use a common Arabic word that is likely to appear in Arabic tafsir text
    results = RAWoutput.do({
        "action": "search",
        "query": "الرحمن",
        "word_info": True,
        "highlight": "none",
    })
    assert results["error"]["code"] == 0
    search = results.get("search", {})
    words = search.get("words", {})
    individual = words.get("individual", {})
    assert individual, "Expected at least one keyword in words.individual for 'الرحمن'"

    # Arabic aya-field matches must have no hint; tafsir matches must have hint='tafsir'
    for key, word_data in individual.items():
        hint = word_data.get("hint")
        assert hint != "aya", (
            f"words.individual[{key}]: 'aya' is not a valid hint value: {word_data!r}"
        )
        if hint is not None:
            assert hint == "tafsir", (
                f"words.individual[{key}]: expected hint='tafsir' for Arabic translation, "
                f"got {hint!r}"
            )
