===================
JSON Web Service II
===================
This is the JSON output system version 2 of Alfanous project. This feature is in Alpha test and the JSON schema may be it's not stable. We are waiting for real feadbacks and suggestions to improve its efficacy, quality and stability. To contact us, please send an email to the mailing list <alfanous@googlegroups.com>. If you don't know what is JSON, See: Wikipedia_ or the Official_Website_of_JSON_. It contains many JSON parsing libraries for most programming languages. 

.. _Wikipedia: http://en.wikipedia.org/wiki/JSON
.. _Official_Website_of_JSON: http://www.json.org/

-------
License
-------
This service is free to use.We highly recommend to refer Alfanous engine somewhere in your pages using icons or texts like "Alfanous engine", "Powered by Alfanous" linked to http://www.alfanous.org/json.Art works you may need are available here_.

.. _here: http://www.alfanous.org/art/

-----------
Limitations
-----------
1. JSON service does not provide more then 1000 results. It gives the real pages number found but query for page=101 get a reply with NULL.

------
Syntax
------

To get JSON information , use this syntax : http://www.alfanous.org/json?ARGUMENT such as ARGUMENT is:
<code>
list= translations | recitations | information | fields
search= QUERY
  &highlight= none | css | html | bold | bbcode
  &sortedby= mushaf | tanzil | subject | score | FIELD (use list=fields)
  &page= NUMBER
  &recitation= RECITATION (use list=recitations)
  &translation= TRANSLATION (use list=translations)
  &fuzzy=yes | no
suggest== TERMS
</code>
 <del>&traduction=...</del>

Here you find [[Json_fixes|the fixes history]]

--------
Examples
--------

  *  [[http://www.alfanous.org/json?search=%D8%A7%D9%84%D8%AD%D9%85%D8%AF&highlight=bbcode&sortedby=tanzil&page=2&traduction=shakir&recitation=Mishary+Rashid+Alafasy|http://www.alfanous.org/json?search=الحمد&highlight=bbcode&sortedby=tanzil&page=2&traduction=shakir&recitation=Mishary+Rashid+Alafasy]]
  *  http://www.alfanous.org/json?list=recitations
  *  http://www.alfanous.org/json?list=fields
  *  http://www.alfanous.org/json?list=information
  *  http://www.alfanous.org/json?list=translations <del>...?list=traductions</del>
  *  http://www.alfanous.org/json?suggest=%D8%A7%D8%A8%D8%B1%D8%A7%D9%87%D8%A7%D9%85
 

------
Demoes
------

  * [[http://www.sneetsher.com/abdellah/alfanous_jquery_demo/| alfanous_jquery_demo v1]] by Abdellah Ch.
  * [[http://www.sneetsher.com/abdellah/alfanous_jquery_demo2/| alfanous_jquery_demo v2]] by Abdellah Ch.
  * [[http://www.sneetsher.com/abdellah/alfanous_jquery_demo3/| alfanous_jquery_demo v3]] by Abdellah Ch.
  * [[http://mobile.alfanous.org/| Alfanous Mobile Web Interface (PHP)]] , [[http://alfanous.svn.sourceforge.net/viewvc/alfanous/trunk/interfaces/web/mobile_wui/| Its source code is in SVN]]

-----------------------
Advanced Query Examples
-----------------------

  *  Simple search : [[http://www.alfanous.org/json?search=الحمد|search=الحمد]]
  *  Phrases : [[http://www.alfanous.org/json?search="الحمد لله"|search="الحمد لله"]]
  *  Logical relations - ANDNOT : [[http://www.alfanous.org/json?search=(الصلاة - الزكاة)|search=(الصلاة - الزكاة)]]
  *  Logical relations - AND : [[http://www.alfanous.org/json?search=الصلاة + الزكاة|search=الصلاة + الزكاة]]
  *  Logical relations - OR : [[http://www.alfanous.org/json?search=الصلاة %7C الزكاة|search=الصلاة | الزكاة]]
  *  Joker * : [[http://www.alfanous.org/json?search=*نبي*|search=*نبي*]]
  *  Joker ? : [[http://www.alfanous.org/json?search=نعم؟|search=نعم؟]]
  *  Fielded search : [[http://www.alfanous.org/json?search=سورة:يس|search=سورة:يس]] , look for [[http://wiki.alfanous.org/doku.php?id=json_web_service#fields|fields list]]
  *  Fielded search (2) : [[http://www.alfanous.org/json?search=سجدة:نعم|search=سجدة:نعم]],
  *  Intervals : [[http://www.alfanous.org/json?search=رقم_السورة:[1 الى 5] و الله|search=رقم_السورة:[1 الى 5] و الله]]
  *  Partial vocalization : [[http://www.alfanous.org/json?search=آية_:'مَن'|search=آية_:'مَن']]
  *  Tuples (root,type=أداة | اسم | فعل) : [[http://www.alfanous.org/json?search={قول،اسم}|search={قول،اسم}]]
  *  Derivations - lemma : [[http://www.alfanous.org/json?search=>مالك|search=>مالك]]
  *  Derivations - root : [[http://www.alfanous.org/json?search=>>مالك|search=>>مالك]]

------
Fields
------
^ Arabic  ^ English ^ Values ^ Description ^ 
| رقم | gid | 1 to 6236 | Global order of Aya in the whole Quran |
| رقم_الآية | aya_id | 1 to $(s_a) | order of Aya inside its Sura  |
| آية| aya | Text | Aya non-vocalized standard text ( used for search) |
| آية_| aya_ | Text | Aya vocalized standard text ( used for show/search) |
| عثماني  | uth | Text |  Aya vocalized uthmani text ( used for show/search)  |
| عثماني_ | uth_ | Text | Aya vocalized uthmani text ( used for show)|
| موضوع  | subject | Text | Thematic Division : **Chapter** > **Topic** > **Subtopic** |
| فصل | chapter | Text | Thematic Division : **Chapter** > Topic > Subtopic |
| فرع | topic | Text | Thematic Division : Chapter > **Topic** > Subtopic |
| باب  | subtopic | Text | Thematic Division :  Chapter > Topic >** Subtopic** |
| رقم_السورة | sura_id | 1 to 114 | Order of  Sura in Mus-haf |
| سورة | sura | Text | Possible Names of Sura |
| نوع_السورة  | sura_type | مدنية or مكية | Revelation place of Sura |
| ترتيب_السورة | sura_order | 1 to 114 | Revelation order of Sura |
| جزء | juz | 1 to 30 | Structural Division : **Juz** > Hizb  > Rub  |
| حزب | hizb | 1 to 60| Structural Division : Juz > **Hizb** > Rub   |
| نصف| nisf| 1 to 2 | Deprecated   |
| ربع | rub | 1 to 4| Structural Division : Juz > Hizb  > **Rub**  |
| صفحة| page| Number | Structural Division : Page |
| منزل  | manzil | 1 to 7| Structural Division : **Manzil** > Ruku  |
| ركوع | ruku | Number| Structural Division : Manzil > **Ruku** |
| سجدة | sajda | نعم or لا | Test existence of a Sajda |
| رقم_السجدة | sajda_id |1 to 14 | the order of the Sajda if exist |
| نوع_السجدة | sajda_type | واجبة or مستحبة  | the type of the Sajda if exist |
| ح_س| s_l | Number | Number of **letters** in **Sura** |
| ك_س| s_w | Number | Number of **words** in **Sura** |
| ج_س | s_g | Number | Number of **God's names** in **Sura** |
| آ_س | s_a | Number | Number of **Ayas** in **Sura** |
| ر_س| s_r | Number | Number of **Ruku-s** in **Sura** |
| ح_آ | a_l | Number | Number of **letters** in **Aya**  |
| ك_آ | a_w | Number | Number of **words** in **Aya** |
| ج_آ | a_g | Number | Number of **God's names** in **Aya**  |

----------------
SortedBy Options
----------------
^ Option ^ Description ^
| score | The relevance of the results compared to the query keywords |
| mushaf | The default order of ayas in Mus-haf |           
| tanzil | The revelation order |
| subject | The alphabetic order of the values for subjects fields |
| FIELD (field's name) | The numerical order or alphabetic order of a costum field   (use "list=fields"  to  fetch the possible names of fields) |



========
Schema's
========
-----------
Suggestions
-----------
<code java alfanous_suggestions_example.json>
[

        ["ابراهام", ["\u0625\u0628\u0631\u0627\u0647\u064a\u0645"]]

]
</code>

-------
Results
-------
<code java alfanous_results_example.json>
{
 "runtime": "0.00055",
 "suggestions": [],
 "words": {
           "1": {
                 "nb_matches": 3,
                 "word": "\u0639\u0627\u0635\u0645",
                 "nb_ayas": 3
                 },
           "global": {
                      "nb_matches": 3,
                      "nb_words": 1
                      }
           },
"interval": {
              "start": 1,
              "total": 3,
              "end": 3
              },
"ayas": {
          "1": {

                 "sura": {
                          "id": 40,
                          "name": "\u063a\u0627\u0641\u0631",
                          "type": "\u0645\u0643\u064a\u0629",
                           "order": 60
                           "stat":{
                                  "letters": 5041,
                                  "words": 1219,
                                  "godnames": 53,
                                  "ayas": 85,
                                  }
                         },
                 "aya": {
                     "id": 33,
                     "text": "\u064a\u064e\u0648\u0652\u0645\u064e \u062a\u064f\u0648\u064e\u0644\u0651\u064f\u0648\u0646\u064e \u0645\u064f\u062f\u0652\u0628\u0650\u0631\u0650\u064a\u0646\u064e \u0645\u064e\u0627 \u0644\u064e\u0643\u064f\u0645\u0652 \u0645\u0650\u0646\u064e \u0627\u0644\u0644\u0651\u064e\u0640\u0647\u0650 \u0645\u0650\u0646\u0652 <b>\u0639\u064e\u0627\u0635\u0650\u0645\u064d</b> \u0648\u064e\u0645\u064e\u0646\u0652 \u064a\u064f\u0636\u0652\u0644\u0650\u0644\u0650 \u0627\u0644\u0644\u0651\u064e\u0640\u0647\u064f \u0641\u064e\u0645\u064e\u0627 \u0644\u064e\u0647\u064f \u0645\u0650\u0646\u0652 \u0647\u064e\u0627\u062f\u064d",
                         "text_uthmani": "\u064a\u064e\u0648\u0652\u0645\u064e \u062a\u064f\u0648\u064e\u0644\u0651\u064f\u0648\u0646\u064e \u0645\u064f\u062f\u0652\u0628\u0650\u0631\u0650\u064a\u0646\u064e \u0645\u064e\u0627 \u0644\u064e\u0643\u064f\u0645 \u0645\u0651\u0650\u0646\u064e \u0671\u0644\u0644\u0651\u064e\u0640\u0647\u0650 \u0645\u0650\u0646\u0652 <b>\u0639\u064e\u0627\u0635\u0650\u0645\u064d</b> \u06d7 \u0648\u064e\u0645\u064e\u0646 \u064a\u064f\u0636\u0652\u0644\u0650\u0644\u0650 \u0671\u0644\u0644\u0651\u064e\u0640\u0647\u064f \u0641\u064e\u0645\u064e\u0627 \u0644\u064e\u0647\u064f\u06e5 \u0645\u0650\u0646\u0652 \u0647\u064e\u0627\u062f\u064d",
                         "recitation": "http://www.versebyversequran.com/data/Alafasy_128kbps/040033.mp3",
                         "traduction": null
                         },
                 "stat": {
                          "letters": 52,
                          "godnames": 2,
                          "words": 16},
                "theme": {
                            "chapter": "-----",
                            "topic": "-----",
                            "subtopic": "-----"
                            },
                "position": {
                             "rubu": 0,
                             "manzil": 6,
                             "hizb": 47,
                             "page": 470
                             }
                 "sajda": {
                           "exist": false,
                           "type": null,
                           "id": null
                           },
                }
        }
}
</code>
------------
Translations
------------
<code java alfanous_translations_list_example.json>
{
indonesian: "Bahasa Indonesia-Indonesian"
noghmani: "Noghmani-tt"
korkut: "Besim Korkut-Bosnian"
jalandhry: "Jalandhry-ur"
makarem: "Ayatollah Makarem Shirazi-Persian"
osmanov: "M.-N.O. Osmanov-Russian"
amroti: "Maulana Taj Mehmood Amroti-sd"
ozturk: "Prof. Yasar Nuri Ozturk-Turkish"
shakir: "Mohammad Habib Shakir-English"
pickthall: "Mohammed Marmaduke William Pickthall-English"
muhiuddinkhan: "Maulana Muhiuddin Khan-bn"
irfan_ul_quran: "Maulana Doctor Tahir ul Qadri-ur"
ghomshei: "Mahdi Elahi Ghomshei-Persian"
arberry: "Arthur John Arberry-English"
porokhova: "V. Porokhova-Russian"
ansarian: "Hussain Ansarian-Persian"
kuliev: "E. Kuliev-Russian"
transliteration-en: "Transliteration-English"
}
</code>
-----------
Information
-----------
<code java alfanous_information_example.json>
{
"engine": "Alfanous",
"wiki": "http://wiki.alfanous.org/doku.php?id=json_web_service",
"version": "0.1",
"contact": "assem.ch@gmail.com",
"author": "Assem chelli"
}
</code>
-----------
Recitations
-----------
<code java alfanous_recitations_list_example.json>
{
"Mishary Rashid Alafasy": "http://www.versebyversequran.com/data/Alafasy_128kbps",
"Ahmed_ibn_Ali_al-Ajamy (From QuranExplorer.com)": "http://www.versebyversequran.com/data/Ahmed_ibn_Ali_al-Ajamy_64kbps_QuranExplorer.Com",
"Menshawi (external source)": "http://www.everyayah.com/data/Menshawi_32kbps",
"Saad Al Ghamadi": "http://www.everyayah.com/data/Ghamadi_40kbps",
"AbdulBasit AbdusSamad (From QuranExplorer.com)": "http://www.versebyversequran.com/data/AbdulSamad_64kbps_QuranExplorer.Com",
"Hani Rifai": "http://www.everyayah.com/data/Hani_Rifai_192kbps",
"Muhammad Ayyoub": "http://www.everyayah.com/data/Muhammad_Ayyoub_128kbps",
"Husary": "http://www.everyayah.com/data/Husary_128kbps",
"Saood bin Ibraaheem Ash-Shuraym": "http://www.everyayah.com/data/Saood bin Ibraaheem Ash-Shuraym_128kbps",
"Hudhaify": "http://www.everyayah.com/data/Hudhaify_128kbps",
"Abu Bakr Ash-Shaatree": "http://www.versebyversequran.com/data/Abu Bakr Ash-Shaatree_128kbps",
"Ibrahim_Walk": "http://www.everyayah.com/data/English/Ibrahim_Walk_192kbps_TEST",
"Husary Mujawwad": "http://www.everyayah.com/data/Husary_128kbps_Mujawwad",
"Abdullah Basfar": "http://www.everyayah.com/data/Abdullah_Basfar_192kbps",
"AbdulBasit AbdusSamad (Murattal style)": "http://www.versebyversequran.com/data/Abdul_Basit_Murattal",
"Muhammad Ayyoub (external source)": "http://www.everyayah.com/data/Muhammad_Ayyoub_32kbps"
}
</code>
------
Fields
------
Note: Arabic fields are shown here as LTR due to the page direction. See [[json_web_service#Fields|Fields]] for correct displayed Arabic names of fields. To be clear JSON UNICODE characters "\uxxxx" are transformed.
<code java alfanous_fields_list_example.json>
{
"جزء": "juz",
"عثماني ": "uth",
"نوع_السورة": "sura_type",
"رقم_السجدة": "sajda_id",
"صفحة": "page",
"ربع": "rub",
"ر_س": "s_r",
"ركوع": "ruku",
"رقم_السورة": "sura_id",
"آ_س": "s_a",
"آية_": "aya_",
"موضوع": "subject",
"ج_س": "s_g",
"ك_آ": "a_w",
"فصل": "chapter",
"ح_آ": "a_l",
"سورة": "sura",
"فرع": "topic",
"آية": "aya",
"رقم_الآية": "aya_id",
"عثماني_": "uth_",
"ك_س": "s_w",
"نوع_السجدة": "sajda_type",
"رقم": "gid",
"باب": "subtopic",
"نصف": "nisf",
"ح_س": "s_l",
"حزب": "hizb",
"منزل": "manzil",
"ج_آ": "a_g",
"سجدة": "sajda",
"ترتيب_السورة": "sura_order"
}
</code>
=============
Who use this?
=============

If you are using this service, We want to make Alfanous more helpful. We will be happy to know about your applications.
  * [[http://www.sneetsher.com/abdellah/alfanous_jquery_demo3/|A Simple jQuery/JavaScript Demo Example]] 
  * [[http://wui.alfanous.org/| Alfanous web user interface ]]
  * [[http://m.alfanous.org/| Alfanous web user interface for mobiles ]]
  * [[http://chatty.alfanous.org/?step=1&msg=%D8%B9%D8%A7%D8%B5%D9%85&user=Assem| Alfanous chat bot ]]
  * [[http://www.bayt-al-hikma.com/SearchQuran.aspx|Bayt Al-Hikma]]

