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

--------------
Quering Syntax
--------------
To get JSON information , use this syntax : http://www.alfanous.org/json?ARGUMENT such as ARGUMENT is compound of those flags:

======== =================== ================= ============================================ ================= ========================================================================================================================================================================
 number    flag               related action    description                                   default value    accepted values 
-------- ------------------- ----------------- -------------------------------------------- ----------------- ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
 1         **action**         <none>            action to perform                             "error"          search | suggest | show
 2         ident              <all>             identifier of requester   [exprimental]       "undefined"      undefined
 3         platform           <all>             platform used by requester                    "undefined"      undefined | wp7 | s60 | android | ios | linux | window
 4         domain             <all>             web domain of requester if applicable         "undefined"      \*
 5a        **query**          search,suggest    query attached to action                       ""              \*
 5b        **query**          show              query attached to action                       ""              all | translations |recitations | information | hints | surates | chapters | defaults | flags | fields | fields_reverse | errors | domains | help_messages 
 6         highlight          search            highlight method                              "css"            css | html | genshi | bold | bbcode
 7         script             search            script of aya text                            "standard"       standard | uthmani
 8         vocalized          search            enable vocalization of aya text               "True"           True | False
 9         recitation         search            recitation id                                 "1"              1 to 30
 10        translation        search            translation id                                "None"           \*
 11        prev_aya           search            enable previous aya retrieving                "False"          True | False
 12        next_aya           search            enable next aya retrieving                    "False"          True | False
 13        sura_info          search            enable sura information retrieving            "True"           True | False
 14        word_info          search            enable word information retrieving            "True"           True | False
 15        aya_position_info  search            enable aya position information retrieving    "True"           True | False
 16        aya_theme_info     search            enable aya theme information retrieving       "True"           True | False
 17        aya_stat_info      search            enable aya stat information retrieving        "True"           True | False
 18        aya_sajda_info     search            enable aya sajda information retrieving       "True"           True | False
 19        annotation_word    search            enable query terms annotations retrieving     "False"          True | False
 20        annotation_aya     search            enable aya words annotations retrieving       "False"          True | False
 21        sortedby           search            sorting order of results                      "score"          total | score | mushaf | tanzil | subject
 22        offset             search            starting offset of results                    "1"              1 to 6236
 23        range              search            range of results                              "10"             1 to 25
 24        page               search            page number  [override offset]                "1"              1 to 6236
 25        perpage            search            results per page  [override range]            "10"             1 to 25
 26        fuzzy              search            fuzzy search [exprimental]     	         	    "False"          True | False

======== =================== ================= ============================================ ================= ========================================================================================================================================================================

--------
Examples
--------
*  json2?action=search& query=الحمد &highlight=bbcode &sortedby=tanzil &page=2 &traduction=1&fuzzy=True
*  json2?show=recitations
*  json2?show=fields
*  json2?show=all
*  json2?show=translations 
*  json2?show=errors
*  json2?suggest=مءصدة

------
Demoes
------
(No demoes yet! if you have a demo, we'll be happy to refer it here)

-----------------------
Advanced Query Examples
-----------------------
*  Simple search: query=الحمد    
*  Phrases : query="الحمد لله"    
*  Logical relations - ANDNOT :  query=(الصلاة - الزكاة)    
*  Logical relations - AND :   query=الصلاة + الزكاة    
*  Logical relations - OR :  query=الصلاة | الزكاة    
*  Joker \* :      query=\*نبي\*    
*  Joker \? :     query=نعم؟    
*  Fielded search :       query=سورة:يس     , look for Fields_     
*  Fielded search (2) :     query=سجدة:نعم    ,
*  Intervals :       query=رقم_السورة:[1 الى 5] و الله    
*  Partial vocalization :      query=آية_:'مَن'    
*  Tuples (root,type=أداة | اسم | فعل): query={قول،اسم}    
*  Derivations - lemma :      query=>مالك    
*  Derivations - root :       query=>>مالك    

------
Fields
------

===== ================= =================== ============== ============================================================
 n     عربي              English             Values         Description   
----- ----------------- ------------------- -------------- ------------------------------------------------------------
 1     رقم               gid                 1 to 6236      Global order of Aya in the whole Quran 
 2     رقم_الآية           aya_id              1 to 300       order of Aya inside its Sura  
 3     آية                aya                 Text           Aya non-vocalized standard text ( used for search) 
 4     آية_               aya_                Text           Aya vocalized standard text ( used for show/search) 
 5     عثماني             uth                 Text           Aya vocalized uthmani text ( used for show/search) 
 6     عثماني_            uth_                Text           Aya vocalized uthmani text ( used for show)
 7     موضوع             subject             Text           Thematic Division: **Chapter** > **Topic** > **Subtopic** 
 8     فصل              chapter              Text           Thematic Division: **Chapter** > Topic > Subtopic 
 9     فرع               topic                Text           Thematic Division: Chapter > **Topic** > Subtopic 
 10    باب               subtopic             Text           Thematic Division:  Chapter > Topic > **Subtopic** 
 11    رقم_السورة        sura_id              1 to 114       Order of  Sura in Mus-haf
 12    سورة              sura                Text           Possible Names of Sura 
 13    نوع_السورة         sura_type           مدنية | مكية    Revelation place of Sura 
 14    ترتيب_السورة       sura_order           1 to 114       Revelation order of Sura 
 15    جزء               juz                  1 to 30        Structural Division : **Juz** > Hizb  > Rub  
 16    حزب              hizb                 1 to 60        Structural Division : Juz > **Hizb** > Rub 
 17    نصف              nisf                 1 to 2         Deprecated   
 18    ربع                rub                  1 to 4         Structural Division : Juz > Hizb  > **Rub**  
 19    صفحة              page                Number          Structural Division : Page
 20    منزل               manzil              1 to 7          Structural Division : **Manzil** > Ruku  
 21    ركوع               ruku                Number          Structural Division : Manzil > **Ruku** 
 22    سجدة              sajda               نعم | لا        Test existence of a Sajda
 23    رقم_السجدة         sajda_id            1 | 14         Order of the Sajda if exist 
 24    نوع_السجدة         sajda_type         واجبة|مستحبة   Type of the Sajda if exist 
 25    ح_س              s_l                  Number          Number of **letters** in **Sura** 
 26    ك_س              s_w                  Number          Number of **words** in **Sura** 
 27    ج_س               s_g                 Number          Number of **God's names** in **Sura** 
 28    آ_س               s_a                 Number          Number of **Ayas** in **Sura** 
 29    ر_س               s_r                 Number          Number of **Ruku-s** in **Sura** 
 30    ح_آ                a_l                 Number          Number of **letters** in **Aya**  
 31    ك_آ                a_w                 Number          Number of **words** in **Aya** 
 32    ج_آ                a_g                 Number          Number of **God's names** in **Aya**
===== ================= =================== ============== ============================================================


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

