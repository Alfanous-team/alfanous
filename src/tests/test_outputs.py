
"""
A sample script that emphasize the basic operations of Alfanous API.

"""


# import Output object
from alfanous.outputs import Raw

# import default paths
from alfanous import paths

# Initialize search engines
RAWoutput = Raw(
                    QSE_index = paths.QSE_INDEX, # Quranic Main index path
                    TSE_index = paths.TSE_INDEX, # Translations index path
                    WSE_index = paths.WSE_INDEX, # Quranic words index path
                    Recitations_list_file = paths.RECITATIONS_LIST_FILE,
                    Translations_list_file = paths.TRANSLATIONS_LIST_FILE ,
                    Hints_file = paths.HINTS_FILE,
                    Information_file = paths.INFORMATION_FILE
                )



def test_suggestion():
    ## prepare a suggestion query
    suggest_flags = {
                "action":"suggest",
                "query": "ابراهيم"
                }

    results = RAWoutput.do( suggest_flags )

    assert results["suggest"] == {'\u0627\u0628\u0631\u0627\u0647\u064a\u0645': ['\u0644\u0625\u0628\u0631\u0627\u0647\u064a\u0645',
                                                 '\u0625\u0628\u0631\u0627\u0647\u064a\u0645',
                                                 '\u0648\u0625\u0628\u0631\u0627\u0647\u064a\u0645']}

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
                 "translation": "en.shakir",
                 }

    results = RAWoutput.do( search_flags )
    assert results["search"]["interval"]["total"] == 116

    del results["search"]["runtime"]

    assert results == {'error': {'code': 0, 'msg': 'success'},
 'search': {'ayas': {1: {'annotations': {},
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
                                 'recitation': 'https://www.everyayah.com/data/Abdul_Basit_Murattal_64kbps/001002.mp3',
                                 'text': '<span class="match '
                                         'term0">الْحَمْدُ</span> <span '
                                         'class="match term1">لِلَّهِ</span> '
                                         'رَبِّ الْعَالَمِينَ',
                                 'text_no_highlight': 'الحمد لله رب العالمين',
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
                                      'page_IN': 2,
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
                     2: {'annotations': {},
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
                                 'recitation': 'https://www.everyayah.com/data/Abdul_Basit_Murattal_64kbps/002022.mp3',
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
                                      'page_IN': 6,
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
                     3: {'annotations': {},
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
                                 'recitation': 'https://www.everyayah.com/data/Abdul_Basit_Murattal_64kbps/002098.mp3',
                                 'text': 'مَنْ كَانَ عَدُوًّا <span '
                                         'class="match term0">لِلَّهِ</span> '
                                         'وَمَلَائِكَتِهِ وَرُسُلِهِ '
                                         'وَجِبْرِيلَ وَمِيكَالَ فَإِنَّ '
                                         'اللَّهَ عَدُوٌّ لِلْكَافِرِينَ',
                                 'text_no_highlight': 'من كان عدوا لله '
                                                      'وملائكته ورسله وجبريل '
                                                      'وميكال فإن الله عدو '
                                                      'للكافرين',
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
                                      'page_IN': 20,
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
                     4: {'annotations': {},
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
                                 'recitation': 'https://www.everyayah.com/data/Abdul_Basit_Murattal_64kbps/002112.mp3',
                                 'text': 'بَلَى مَنْ أَسْلَمَ وَجْهَهُ <span '
                                         'class="match term0">لِلَّهِ</span> '
                                         'وَهُوَ مُحْسِنٌ فَلَهُ أَجْرُهُ '
                                         'عِنْدَ رَبِّهِ وَلَا خَوْفٌ '
                                         'عَلَيْهِمْ وَلَا هُمْ يَحْزَنُونَ',
                                 'text_no_highlight': 'بلى من أسلم وجهه لله '
                                                      'وهو محسن فله أجره عند '
                                                      'ربه ولا خوف عليهم ولا '
                                                      'هم يحزنون',
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
                                      'page_IN': 23,
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
                     5: {'annotations': {},
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
                                 'recitation': 'https://www.everyayah.com/data/Abdul_Basit_Murattal_64kbps/002142.mp3',
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
                                      'page_IN': 29,
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
                     6: {'annotations': {},
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
                                 'recitation': 'https://www.everyayah.com/data/Abdul_Basit_Murattal_64kbps/002156.mp3',
                                 'text': 'الَّذِينَ إِذَا أَصَابَتْهُمْ '
                                         'مُصِيبَةٌ قَالُوا إِنَّا <span '
                                         'class="match term0">لِلَّهِ</span> '
                                         'وَإِنَّا إِلَيْهِ رَاجِعُونَ',
                                 'text_no_highlight': 'الذين إذا أصابتهم مصيبة '
                                                      'قالوا إنا لله وإنا إليه '
                                                      'راجعون',
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
                                      'page_IN': 32,
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
                     7: {'annotations': {},
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
                                 'recitation': 'https://www.everyayah.com/data/Abdul_Basit_Murattal_64kbps/002165.mp3',
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
                                      'page_IN': 33,
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
                     8: {'annotations': {},
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
                                 'recitation': 'https://www.everyayah.com/data/Abdul_Basit_Murattal_64kbps/002172.mp3',
                                 'text': 'يَا أَيُّهَا الَّذِينَ آمَنُوا '
                                         'كُلُوا مِنْ طَيِّبَاتِ مَا '
                                         'رَزَقْنَاكُمْ وَاشْكُرُوا <span '
                                         'class="match term0">لِلَّهِ</span> '
                                         'إِنْ كُنْتُمْ إِيَّاهُ تَعْبُدُونَ',
                                 'text_no_highlight': 'يا أيها الذين آمنوا '
                                                      'كلوا من طيبات ما '
                                                      'رزقناكم واشكروا لله إن '
                                                      'كنتم إياه تعبدون',
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
                                      'page_IN': 34,
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
                     9: {'annotations': {},
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
                                 'recitation': 'https://www.everyayah.com/data/Abdul_Basit_Murattal_64kbps/002193.mp3',
                                 'text': 'وَقَاتِلُوهُمْ حَتَّى لَا تَكُونَ '
                                         'فِتْنَةٌ وَيَكُونَ الدِّينُ <span '
                                         'class="match term0">لِلَّهِ</span> '
                                         'فَإِنِ انْتَهَوْا فَلَا عُدْوَانَ '
                                         'إِلَّا عَلَى الظَّالِمِينَ',
                                 'text_no_highlight': 'وقاتلوهم حتى لا تكون '
                                                      'فتنة ويكون الدين لله '
                                                      'فإن انتهوا فلا عدوان '
                                                      'إلا على الظالمين',
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
                                      'page_IN': 40,
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
                     10: {'annotations': {},
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
                                  'recitation': 'https://www.everyayah.com/data/Abdul_Basit_Murattal_64kbps/002196.mp3',
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
                                       'page_IN': 41,
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
                         'nb_pages': 12.5,
                         'page': 1.0,
                         'start': 1,
                         'total': 116},
            'translation_info': {},
            'words': {'global': {'nb_matches': 142.0,
                                 'nb_vocalizations': 0,
                                 'nb_words': 2},
                      'individual': {1: {'derivations': [],
                                         'derivations_extra': [],
                                         'lemma': '',
                                         'nb_ayas': 113,
                                         'nb_derivations': 0,
                                         'nb_derivations_extra': 0,
                                         'nb_matches': 116.0,
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
                                         'nb_ayas': 25,
                                         'nb_derivations': 0,
                                         'nb_derivations_extra': 0,
                                         'nb_matches': 26.0,
                                         'nb_synonyms': 0,
                                         'nb_vocalizations': 0,
                                         'romanization': None,
                                         'root': '',
                                         'synonyms': [],
                                         'vocalizations': [],
                                         'word': 'الحمد'}}}}}