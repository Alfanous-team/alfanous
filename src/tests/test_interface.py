



import alfanous.api


def test_search():
    alfanous.api.search(u"الله", sortedby='mushaf')

    results = alfanous.api.do({"action": "search", "query": u"الله"})
    del results['search']['runtime']

    assert results['search']['interval'] == {'end': 10, 'nb_pages': 157.5, 'page': 1.0, 'start': 1, 'total': 1566}
    assert results == {'error': {'code': 0, 'msg': 'success'},
 'search': {'ayas': {1: {'annotations': {},
                         'aya': {'id': 4,
                                 'next_aya': {'id': 5,
                                              'sura': 'Al-Hashr',
                                              'sura_arabic': 'الحشر',
                                              'text': 'مَا قَطَعْتُمْ مِنْ '
                                                      'لِينَةٍ أَوْ '
                                                      'تَرَكْتُمُوهَا '
                                                      'قَائِمَةً عَلَى '
                                                      'أُصُولِهَا فَبِإِذْنِ '
                                                      'اللَّهِ وَلِيُخْزِيَ '
                                                      'الْفَاسِقِينَ'},
                                 'prev_aya': {'id': 3,
                                              'sura': 'Al-Hashr',
                                              'sura_arabic': 'الحشر',
                                              'text': 'وَلَوْلَا أَنْ كَتَبَ '
                                                      'اللَّهُ عَلَيْهِمُ '
                                                      'الْجَلَاءَ '
                                                      'لَعَذَّبَهُمْ فِي '
                                                      'الدُّنْيَا وَلَهُمْ فِي '
                                                      'الْآخِرَةِ عَذَابُ '
                                                      'النَّارِ'},
                                 'recitation': 'https://www.everyayah.com/data/Abdul_Basit_Murattal_64kbps/059004.mp3',
                                 'text': 'ذَلِكَ بِأَنَّهُمْ شَاقُّوا <span '
                                         'class="match term0">اللَّهَ</span> '
                                         'وَرَسُولَهُ وَمَنْ يُشَاقِّ <span '
                                         'class="match term0">اللَّهَ</span> '
                                         'فَإِنَّ <span class="match '
                                         'term0">اللَّهَ</span> شَدِيدُ '
                                         'الْعِقَابِ',
                                 'text_no_highlight': 'ذلك بأنهم شاقوا الله '
                                                      'ورسوله ومن يشاق الله '
                                                      'فإن الله شديد العقاب',
                                 'translation': None},
                         'identifier': {'aya_id': 4,
                                        'gid': 5130,
                                        'sura_arabic_name': 'الحشر',
                                        'sura_id': 59,
                                        'sura_name': 'Al-Hashr'},
                         'position': {},
                         'sajda': {'exist': False, 'id': None, 'type': None},
                         'stat': {'godnames': 3, 'letters': 51, 'words': 12},
                         'sura': {},
                         'theme': {'chapter': 'الجهاد في الإسلام ',
                                   'subtopic': '',
                                   'topic': 'فضل الجهاد والدعوة إليه'}},
                     2: {'annotations': {},
                         'aya': {'id': 106,
                                 'next_aya': {'id': 107,
                                              'sura': "An-Nisa'",
                                              'sura_arabic': 'النساء',
                                              'text': 'وَلَا تُجَادِلْ عَنِ '
                                                      'الَّذِينَ يَخْتَانُونَ '
                                                      'أَنْفُسَهُمْ إِنَّ '
                                                      'اللَّهَ لَا يُحِبُّ '
                                                      'مَنْ كَانَ خَوَّانًا '
                                                      'أَثِيمًا'},
                                 'prev_aya': {'id': 105,
                                              'sura': "An-Nisa'",
                                              'sura_arabic': 'النساء',
                                              'text': 'إِنَّا أَنْزَلْنَا '
                                                      'إِلَيْكَ الْكِتَابَ '
                                                      'بِالْحَقِّ لِتَحْكُمَ '
                                                      'بَيْنَ النَّاسِ بِمَا '
                                                      'أَرَاكَ اللَّهُ وَلَا '
                                                      'تَكُنْ لِلْخَائِنِينَ '
                                                      'خَصِيمًا'},
                                 'recitation': 'https://www.everyayah.com/data/Abdul_Basit_Murattal_64kbps/004106.mp3',
                                 'text': 'وَاسْتَغْفِرِ <span class="match '
                                         'term0">اللَّهَ</span> إِنَّ <span '
                                         'class="match term0">اللَّهَ</span> '
                                         'كَانَ غَفُورًا رَحِيمًا',
                                 'text_no_highlight': 'واستغفر الله إن الله '
                                                      'كان غفورا رحيما',
                                 'translation': None},
                         'identifier': {'aya_id': 106,
                                        'gid': 599,
                                        'sura_arabic_name': 'النساء',
                                        'sura_id': 4,
                                        'sura_name': "An-Nisa'"},
                         'position': {},
                         'sajda': {'exist': False, 'id': None, 'type': None},
                         'stat': {'godnames': 2, 'letters': 30, 'words': 7},
                         'sura': {},
                         'theme': {'chapter': 'الأخلاق المذمومة ',
                                   'subtopic': '',
                                   'topic': 'خيانة النفس بفعل المعصية'}},
                     3: {'annotations': {},
                         'aya': {'id': 13,
                                 'next_aya': {'id': 14,
                                              'sura': 'Ash-Shams',
                                              'sura_arabic': 'الشمس',
                                              'text': 'فَكَذَّبُوهُ '
                                                      'فَعَقَرُوهَا فَدَمْدَمَ '
                                                      'عَلَيْهِمْ رَبُّهُمْ '
                                                      'بِذَنْبِهِمْ '
                                                      'فَسَوَّاهَا'},
                                 'prev_aya': {'id': 12,
                                              'sura': 'Ash-Shams',
                                              'sura_arabic': 'الشمس',
                                              'text': 'إِذِ انْبَعَثَ '
                                                      'أَشْقَاهَا'},
                                 'recitation': 'https://www.everyayah.com/data/Abdul_Basit_Murattal_64kbps/091013.mp3',
                                 'text': 'فَقَالَ لَهُمْ رَسُولُ <span '
                                         'class="match term0">اللَّهِ</span> '
                                         'نَاقَةَ <span class="match '
                                         'term0">اللَّهِ</span> وَسُقْيَاهَا',
                                 'text_no_highlight': 'فقال لهم رسول الله ناقة '
                                                      'الله وسقياها',
                                 'translation': None},
                         'identifier': {'aya_id': 13,
                                        'gid': 6056,
                                        'sura_arabic_name': 'الشمس',
                                        'sura_id': 91,
                                        'sura_name': 'Ash-Shams'},
                         'position': {},
                         'sajda': {'exist': False, 'id': None, 'type': None},
                         'stat': {'godnames': 2, 'letters': 30, 'words': 7},
                         'sura': {},
                         'theme': {'chapter': '',
                                   'subtopic': '',
                                   'topic': ''}},
                     4: {'annotations': {},
                         'aya': {'id': 13,
                                 'next_aya': {'id': 14,
                                              'sura': 'Al-Anfal',
                                              'sura_arabic': 'الأنفال',
                                              'text': 'ذَلِكُمْ فَذُوقُوهُ '
                                                      'وَأَنَّ لِلْكَافِرِينَ '
                                                      'عَذَابَ النَّارِ'},
                                 'prev_aya': {'id': 12,
                                              'sura': 'Al-Anfal',
                                              'sura_arabic': 'الأنفال',
                                              'text': 'إِذْ يُوحِي رَبُّكَ '
                                                      'إِلَى الْمَلَائِكَةِ '
                                                      'أَنِّي مَعَكُمْ '
                                                      'فَثَبِّتُوا الَّذِينَ '
                                                      'آمَنُوا سَأُلْقِي فِي '
                                                      'قُلُوبِ الَّذِينَ '
                                                      'كَفَرُوا الرُّعْبَ '
                                                      'فَاضْرِبُوا فَوْقَ '
                                                      'الْأَعْنَاقِ '
                                                      'وَاضْرِبُوا مِنْهُمْ '
                                                      'كُلَّ بَنَانٍ'},
                                 'recitation': 'https://www.everyayah.com/data/Abdul_Basit_Murattal_64kbps/008013.mp3',
                                 'text': 'ذَلِكَ بِأَنَّهُمْ شَاقُّوا <span '
                                         'class="match term0">اللَّهَ</span> '
                                         'وَرَسُولَهُ وَمَنْ يُشَاقِقِ <span '
                                         'class="match term0">اللَّهَ</span> '
                                         'وَرَسُولَهُ فَإِنَّ <span '
                                         'class="match term0">اللَّهَ</span> '
                                         'شَدِيدُ الْعِقَابِ',
                                 'text_no_highlight': 'ذلك بأنهم شاقوا الله '
                                                      'ورسوله ومن يشاقق الله '
                                                      'ورسوله فإن الله شديد '
                                                      'العقاب',
                                 'translation': None},
                         'identifier': {'aya_id': 13,
                                        'gid': 1173,
                                        'sura_arabic_name': 'الأنفال',
                                        'sura_id': 8,
                                        'sura_name': 'Al-Anfal'},
                         'position': {},
                         'sajda': {'exist': False, 'id': None, 'type': None},
                         'stat': {'godnames': 3, 'letters': 58, 'words': 13},
                         'sura': {},
                         'theme': {'chapter': 'خاتم الأنبياء محمد صلى الله '
                                              'عليه وسلم ',
                                   'subtopic': 'غزوة بدر ',
                                   'topic': 'غزوات الرسول '}},
                     5: {'annotations': {},
                         'aya': {'id': 59,
                                 'next_aya': {'id': 60,
                                              'sura': 'At-Tawba',
                                              'sura_arabic': 'التوبة',
                                              'text': 'إِنَّمَا الصَّدَقَاتُ '
                                                      'لِلْفُقَرَاءِ '
                                                      'وَالْمَسَاكِينِ '
                                                      'وَالْعَامِلِينَ '
                                                      'عَلَيْهَا '
                                                      'وَالْمُؤَلَّفَةِ '
                                                      'قُلُوبُهُمْ وَفِي '
                                                      'الرِّقَابِ '
                                                      'وَالْغَارِمِينَ وَفِي '
                                                      'سَبِيلِ اللَّهِ وَابْنِ '
                                                      'السَّبِيلِ فَرِيضَةً '
                                                      'مِنَ اللَّهِ وَاللَّهُ '
                                                      'عَلِيمٌ حَكِيمٌ'},
                                 'prev_aya': {'id': 58,
                                              'sura': 'At-Tawba',
                                              'sura_arabic': 'التوبة',
                                              'text': 'وَمِنْهُمْ مَنْ '
                                                      'يَلْمِزُكَ فِي '
                                                      'الصَّدَقَاتِ فَإِنْ '
                                                      'أُعْطُوا مِنْهَا رَضُوا '
                                                      'وَإِنْ لَمْ يُعْطَوْا '
                                                      'مِنْهَا إِذَا هُمْ '
                                                      'يَسْخَطُونَ'},
                                 'recitation': 'https://www.everyayah.com/data/Abdul_Basit_Murattal_64kbps/009059.mp3',
                                 'text': 'وَلَوْ أَنَّهُمْ رَضُوا مَا آتَاهُمُ '
                                         '<span class="match '
                                         'term0">اللَّهُ</span> وَرَسُولُهُ '
                                         'وَقَالُوا حَسْبُنَا <span '
                                         'class="match term0">اللَّهُ</span> '
                                         'سَيُؤْتِينَا <span class="match '
                                         'term0">اللَّهُ</span> مِنْ فَضْلِهِ '
                                         'وَرَسُولُهُ إِنَّا إِلَى <span '
                                         'class="match term1">اللَّهِ</span> '
                                         'رَاغِبُونَ',
                                 'text_no_highlight': 'ولو أنهم رضوا ما آتاهم '
                                                      'الله ورسوله وقالوا '
                                                      'حسبنا الله سيؤتينا الله '
                                                      'من فضله ورسوله إنا إلى '
                                                      'الله راغبون',
                                 'translation': None},
                         'identifier': {'aya_id': 59,
                                        'gid': 1294,
                                        'sura_arabic_name': 'التوبة',
                                        'sura_id': 9,
                                        'sura_name': 'At-Tawba'},
                         'position': {},
                         'sajda': {'exist': False, 'id': None, 'type': None},
                         'stat': {'godnames': 4, 'letters': 82, 'words': 19},
                         'sura': {},
                         'theme': {'chapter': '',
                                   'subtopic': '',
                                   'topic': ''}},
                     6: {'annotations': {},
                         'aya': {'id': 158,
                                 'next_aya': {'id': 159,
                                              'sura': "An-Nisa'",
                                              'sura_arabic': 'النساء',
                                              'text': 'وَإِنْ مِنْ أَهْلِ '
                                                      'الْكِتَابِ إِلَّا '
                                                      'لَيُؤْمِنَنَّ بِهِ '
                                                      'قَبْلَ مَوْتِهِ '
                                                      'وَيَوْمَ الْقِيَامَةِ '
                                                      'يَكُونُ عَلَيْهِمْ '
                                                      'شَهِيدًا'},
                                 'prev_aya': {'id': 157,
                                              'sura': "An-Nisa'",
                                              'sura_arabic': 'النساء',
                                              'text': 'وَقَوْلِهِمْ إِنَّا '
                                                      'قَتَلْنَا الْمَسِيحَ '
                                                      'عِيسَى ابْنَ مَرْيَمَ '
                                                      'رَسُولَ اللَّهِ وَمَا '
                                                      'قَتَلُوهُ وَمَا '
                                                      'صَلَبُوهُ وَلَكِنْ '
                                                      'شُبِّهَ لَهُمْ وَإِنَّ '
                                                      'الَّذِينَ اخْتَلَفُوا '
                                                      'فِيهِ لَفِي شَكٍّ '
                                                      'مِنْهُ مَا لَهُمْ بِهِ '
                                                      'مِنْ عِلْمٍ إِلَّا '
                                                      'اتِّبَاعَ الظَّنِّ '
                                                      'وَمَا قَتَلُوهُ '
                                                      'يَقِينًا'},
                                 'recitation': 'https://www.everyayah.com/data/Abdul_Basit_Murattal_64kbps/004158.mp3',
                                 'text': 'بَلْ رَفَعَهُ <span class="match '
                                         'term0">اللَّهُ</span> إِلَيْهِ '
                                         'وَكَانَ <span class="match '
                                         'term0">اللَّهُ</span> عَزِيزًا '
                                         'حَكِيمًا',
                                 'text_no_highlight': 'بل رفعه الله إليه وكان '
                                                      'الله عزيزا حكيما',
                                 'translation': None},
                         'identifier': {'aya_id': 158,
                                        'gid': 651,
                                        'sura_arabic_name': 'النساء',
                                        'sura_id': 4,
                                        'sura_name': "An-Nisa'"},
                         'position': {},
                         'sajda': {'exist': False, 'id': None, 'type': None},
                         'stat': {'godnames': 2, 'letters': 32, 'words': 8},
                         'sura': {},
                         'theme': {'chapter': 'الأديان ',
                                   'subtopic': 'مناقشة القرآن لهم',
                                   'topic': 'النصارى '}},
                     7: {'annotations': {},
                         'aya': {'id': 2,
                                 'next_aya': {'id': 3,
                                              'sura': 'Al-Ikhlas',
                                              'sura_arabic': 'الإخلاص',
                                              'text': 'لَمْ يَلِدْ وَلَمْ '
                                                      'يُولَدْ'},
                                 'prev_aya': {'id': 1,
                                              'sura': 'Al-Ikhlas',
                                              'sura_arabic': 'الإخلاص',
                                              'text': 'قُلْ هُوَ اللَّهُ '
                                                      'أَحَدٌ'},
                                 'recitation': 'https://www.everyayah.com/data/Abdul_Basit_Murattal_64kbps/112002.mp3',
                                 'text': '<span class="match '
                                         'term0">اللَّهُ</span> الصَّمَدُ',
                                 'text_no_highlight': 'الله الصمد',
                                 'translation': None},
                         'identifier': {'aya_id': 2,
                                        'gid': 6223,
                                        'sura_arabic_name': 'الإخلاص',
                                        'sura_id': 112,
                                        'sura_name': 'Al-Ikhlas'},
                         'position': {},
                         'sajda': {'exist': False, 'id': None, 'type': None},
                         'stat': {'godnames': 1, 'letters': 9, 'words': 2},
                         'sura': {},
                         'theme': {'chapter': 'أسماء الله تعالى وصفاته',
                                   'subtopic': '',
                                   'topic': 'أسماء الله الحسنى'}},
                     8: {'annotations': {},
                         'aya': {'id': 244,
                                 'next_aya': {'id': 245,
                                              'sura': 'Al-Baqarah',
                                              'sura_arabic': 'البقرة',
                                              'text': 'مَنْ ذَا الَّذِي '
                                                      'يُقْرِضُ اللَّهَ '
                                                      'قَرْضًا حَسَنًا '
                                                      'فَيُضَاعِفَهُ لَهُ '
                                                      'أَضْعَافًا كَثِيرَةً '
                                                      'وَاللَّهُ يَقْبِضُ '
                                                      'وَيَبْسُطُ وَإِلَيْهِ '
                                                      'تُرْجَعُونَ'},
                                 'prev_aya': {'id': 243,
                                              'sura': 'Al-Baqarah',
                                              'sura_arabic': 'البقرة',
                                              'text': 'أَلَمْ تَرَ إِلَى '
                                                      'الَّذِينَ خَرَجُوا مِنْ '
                                                      'دِيَارِهِمْ وَهُمْ '
                                                      'أُلُوفٌ حَذَرَ '
                                                      'الْمَوْتِ فَقَالَ '
                                                      'لَهُمُ اللَّهُ مُوتُوا '
                                                      'ثُمَّ أَحْيَاهُمْ إِنَّ '
                                                      'اللَّهَ لَذُو فَضْلٍ '
                                                      'عَلَى النَّاسِ '
                                                      'وَلَكِنَّ أَكْثَرَ '
                                                      'النَّاسِ لَا '
                                                      'يَشْكُرُونَ'},
                                 'recitation': 'https://www.everyayah.com/data/Abdul_Basit_Murattal_64kbps/002244.mp3',
                                 'text': 'وَقَاتِلُوا فِي سَبِيلِ <span '
                                         'class="match term0">اللَّهِ</span> '
                                         'وَاعْلَمُوا أَنَّ <span class="match '
                                         'term1">اللَّهَ</span> سَمِيعٌ '
                                         'عَلِيمٌ',
                                 'text_no_highlight': 'وقاتلوا في سبيل الله '
                                                      'واعلموا أن الله سميع '
                                                      'عليم',
                                 'translation': None},
                         'identifier': {'aya_id': 244,
                                        'gid': 251,
                                        'sura_arabic_name': 'البقرة',
                                        'sura_id': 2,
                                        'sura_name': 'Al-Baqarah'},
                         'position': {},
                         'sajda': {'exist': False, 'id': None, 'type': None},
                         'stat': {'godnames': 2, 'letters': 38, 'words': 9},
                         'sura': {},
                         'theme': {'chapter': 'الجهاد في الإسلام ',
                                   'subtopic': '',
                                   'topic': 'فضل الجهاد والدعوة إليه'}},
                     9: {'annotations': {},
                         'aya': {'id': 98,
                                 'next_aya': {'id': 99,
                                              'sura': "Al-Ma'idah",
                                              'sura_arabic': 'المائدة',
                                              'text': 'مَا عَلَى الرَّسُولِ '
                                                      'إِلَّا الْبَلَاغُ '
                                                      'وَاللَّهُ يَعْلَمُ مَا '
                                                      'تُبْدُونَ وَمَا '
                                                      'تَكْتُمُونَ'},
                                 'prev_aya': {'id': 97,
                                              'sura': "Al-Ma'idah",
                                              'sura_arabic': 'المائدة',
                                              'text': 'جَعَلَ اللَّهُ '
                                                      'الْكَعْبَةَ الْبَيْتَ '
                                                      'الْحَرَامَ قِيَامًا '
                                                      'لِلنَّاسِ وَالشَّهْرَ '
                                                      'الْحَرَامَ وَالْهَدْيَ '
                                                      'وَالْقَلَائِدَ ذَلِكَ '
                                                      'لِتَعْلَمُوا أَنَّ '
                                                      'اللَّهَ يَعْلَمُ مَا '
                                                      'فِي السَّمَاوَاتِ وَمَا '
                                                      'فِي الْأَرْضِ وَأَنَّ '
                                                      'اللَّهَ بِكُلِّ شَيْءٍ '
                                                      'عَلِيمٌ'},
                                 'recitation': 'https://www.everyayah.com/data/Abdul_Basit_Murattal_64kbps/005098.mp3',
                                 'text': 'اعْلَمُوا أَنَّ <span class="match '
                                         'term0">اللَّهَ</span> شَدِيدُ '
                                         'الْعِقَابِ وَأَنَّ <span '
                                         'class="match term0">اللَّهَ</span> '
                                         'غَفُورٌ رَحِيمٌ',
                                 'text_no_highlight': 'اعلموا أن الله شديد '
                                                      'العقاب وأن الله غفور '
                                                      'رحيم',
                                 'translation': None},
                         'identifier': {'aya_id': 98,
                                        'gid': 767,
                                        'sura_arabic_name': 'المائدة',
                                        'sura_id': 5,
                                        'sura_name': "Al-Ma'idah"},
                         'position': {},
                         'sajda': {'exist': False, 'id': None, 'type': None},
                         'stat': {'godnames': 2, 'letters': 37, 'words': 9},
                         'sura': {},
                         'theme': {'chapter': '',
                                   'subtopic': '',
                                   'topic': ''}},
                     10: {'annotations': {},
                          'aya': {'id': 74,
                                  'next_aya': {'id': 75,
                                               'sura': 'Al-Hajj',
                                               'sura_arabic': 'الحج',
                                               'text': 'اللَّهُ يَصْطَفِي مِنَ '
                                                       'الْمَلَائِكَةِ رُسُلًا '
                                                       'وَمِنَ النَّاسِ إِنَّ '
                                                       'اللَّهَ سَمِيعٌ '
                                                       'بَصِيرٌ'},
                                  'prev_aya': {'id': 73,
                                               'sura': 'Al-Hajj',
                                               'sura_arabic': 'الحج',
                                               'text': 'يَا أَيُّهَا النَّاسُ '
                                                       'ضُرِبَ مَثَلٌ '
                                                       'فَاسْتَمِعُوا لَهُ '
                                                       'إِنَّ الَّذِينَ '
                                                       'تَدْعُونَ مِنْ دُونِ '
                                                       'اللَّهِ لَنْ '
                                                       'يَخْلُقُوا ذُبَابًا '
                                                       'وَلَوِ اجْتَمَعُوا '
                                                       'لَهُ وَإِنْ '
                                                       'يَسْلُبْهُمُ '
                                                       'الذُّبَابُ شَيْئًا لَا '
                                                       'يَسْتَنْقِذُوهُ مِنْهُ '
                                                       'ضَعُفَ الطَّالِبُ '
                                                       'وَالْمَطْلُوبُ'},
                                  'recitation': 'https://www.everyayah.com/data/Abdul_Basit_Murattal_64kbps/022074.mp3',
                                  'text': 'مَا قَدَرُوا <span class="match '
                                          'term0">اللَّهَ</span> حَقَّ '
                                          'قَدْرِهِ إِنَّ <span class="match '
                                          'term0">اللَّهَ</span> لَقَوِيٌّ '
                                          'عَزِيزٌ',
                                  'text_no_highlight': 'ما قدروا الله حق قدره '
                                                       'إن الله لقوي عزيز',
                                  'translation': None},
                          'identifier': {'aya_id': 74,
                                         'gid': 2669,
                                         'sura_arabic_name': 'الحج',
                                         'sura_id': 22,
                                         'sura_name': 'Al-Hajj'},
                          'position': {},
                          'sajda': {'exist': False, 'id': None, 'type': None},
                          'stat': {'godnames': 2, 'letters': 31, 'words': 9},
                          'sura': {},
                          'theme': {'chapter': 'أسماء الله تعالى وصفاته',
                                    'subtopic': '',
                                    'topic': 'أسماء الله الحسنى'}}},
            'interval': {'end': 10,
                         'nb_pages': 157.5,
                         'page': 1.0,
                         'start': 1,
                         'total': 1566},
            'translation_info': {},
            'words': {'individual': {}}}}