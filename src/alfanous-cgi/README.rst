===================
JSON Web Service II
===================
This is the JSON output system version 2 of Alfanous project. This feature is in Alpha test and the JSON schema may be it's not stable. We are waiting for real feadbacks and suggestions to improve its efficacy, quality and stability. To contact us, please send an email to the mailing list <alfanous@googlegroups.com>. If you don't know what is JSON, See: Wikipedia_ or the Official_Website_of_JSON_. It contains many JSON parsing libraries for most programming languages. 

.. _Wikipedia: http://en.wikipedia.org/wiki/JSON
.. _Official_Website_of_JSON: http://www.json.org/

-------
License
-------
This service is free to use.We highly recommend to refer Alfanous engine somewhere in your pages using icons or texts like "Alfanous engine", "Powered by Alfanous" linked to http://www.alfanous.org/json. Art works you may need are available here_.

.. _here: http://www.alfanous.org/art/

-----------
Limitations
-----------
1. *(no limits)*

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

========== =================================================================================
 Option     Description
---------- ---------------------------------------------------------------------------------
 score      The relevance of the results compared to the query keywords
 mushaf     The default order of ayas in Mus-haf
 tanzil     The revelation order
 subject    The alphabetic order of the values for subjects fields
 FIELD      The numerical order or alphabetic order of a costum field (see Fields_)

========== =================================================================================


-------------
Who use this?
-------------
If you are using this service, We want to make Alfanous more helpful. We will be happy to know about your applications.
   * (no application yet!)


==============
Schema Samples
==============

-----------
Suggestions
-----------
response for: action=suggest&query=مءصدة

.. code-block:: json

    {
    "suggest": [
                  ["\u0645\u0621\u0635\u062f\u0629", 
                      ["\u0645\u0642\u062a\u0635\u062f\u0629", "\u0645\u0624\u0635\u062f\u0629"]
                  ]
                ], 
    "error": {
                "msg": "success ## action=suggest ; query=\u0645\u0621\u0635\u062f\u0629", 
                "code": 0
               }
    }
-------
Results
-------

.. code-block:: json
    {}

------------
Translations
------------
TODO

-----------
Information
-----------
TODO

-----------
Recitations
-----------
TODO

------
Fields
------
TODO

