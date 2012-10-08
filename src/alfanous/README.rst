============
Alfanous API
============
-----
Build
-----
The API uses many critical resources that must be downloaded and/or prepared to be used. To do that, just run this command in the root path of the project

#. Install all building dependencies: `pyparsing <http://aminenacer.blogspot.com/2012/10/mon-voyage-akfadou-deuxieme-partie.html>`_, `pyqt4-dev-tools <http://www.riverbankcomputing.co.uk/software/pyqt/download>`_, `epydoc <http://epydoc.sourceforge.net/>`_,
   `sphinx <http://sphinx.pocoo.org/>`_.

   * (ubuntu 12.04): 
      
     .. code-block:: sh
     
        $ sudo apt-get install python-qt4 qt4-dev-tools python-qt4-dev pyqt4-dev-tools
        $ sudo apt-get install python-distutils-extra
        $ sudo easy_install pyparsing epydoc sphinx




#. Run the build command:

   .. code-block:: sh
        
        $ cd ../../
        $ make build



For more details check  `Makefile <https://github.com/Alfanous-team/alfanous/blob/master/Makefile>`_


-------
Install
-------
To install the API from the source (After Build_ ):

.. code-block:: sh

    $ sudo python setup.py install

A console interface will  be installed automatically with the API:

.. code-block:: sh

    $ alfanous-console -h
    usage: alfanous-console [flags]

-----------
Quick Start
-----------
.. code-block:: python

    # coding: utf-8
    
    # import Output object 
    from alfanous.Outputs import Raw
    
    # import default Paths
    from alfanous.Data import Paths
    
    # Initialize search engines 
    RAWoutput = Raw( 
                        QSE_index = Paths.QSE_INDEX    , # Quranic Main index path
                        TSE_index = Paths.TSE_INDEX,  # Translations index path
                        WSE_index = Paths.WSE_INDEX,  # Quranic words index path
                        Recitations_list_file = Paths.RECITATIONS_LIST_FILE, 
                        Translations_list_file = Paths.TRANSLATIONS_LIST_FILE , 
                        Hints_file = Paths.HINTS_FILE,
                        Stats_file = Paths.STATS_FILE,
                        Information_file = Paths.INFORMATION_FILE
                    ) 

     ## prepare a suggestion query
     suggest_flags = {
                "action":"suggest",
                "query": "ابراهيم"
                }
     results = RAWoutput.do( suggest_flags )

     print "number of missed words", len(results["suggest"]) 
     

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
                 "aya_position_info":  True,
                 "aya_theme_info":  False,
                 "aya_stat_info":  False,
                 "aya_sajda_info":  True,
                 "translation": 2,
                 }

      results = RAWoutput.do( search_flags )

      print "runtime", results["search"]["runtime"] 
      print "total", results["search"]["interval"]["total"] 

see `sample.py <https://github.com/Alfanous-team/alfanous/blob/master/src/alfanous-tests/sample.py>`_.

--------------
Flags
--------------

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
 26        fuzzy              search            fuzzy search [exprimental]                          "False"          True | False

======== =================== ================= ============================================ ================= ========================================================================================================================================================================

-----------------------
Advanced Query Examples
-----------------------
*  Simple search: الحمد    
*  Phrases : "الحمد لله"    
*  Logical relations - ANDNOT : (الصلاة - الزكاة)    
*  Logical relations - AND :   الصلاة + الزكاة    
*  Logical relations - OR : الصلاة | الزكاة    
*  Joker \* :   \*نبي\*    
*  Joker \? :   نعم؟    
*  Fielded search :      سورة:يس  ( look for other Fields_  )   
*  Fielded search (2) :  سجدة:نعم    
*  Intervals :       رقم_السورة:[1 الى 5] و الله    
*  Partial vocalization :      آية_:'مَن'    
*  Tuples (root,type= أداة | اسم | فعل) as: {قول،اسم}    
*  Derivations - lemma :      >مالك    
*  Derivations - root :       >>مالك   


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
 FIELD      The numerical order or alphabetic order of a costum field (see Fields_ )

========== =================================================================================


==============
Schema Samples
==============

-----------
Suggestions
-----------
flags:

.. code-block:: python

    {
        "action"="suggest",
        "query"="مءصدة"
    }

response:

.. code-block:: python

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
flags:

.. code-block:: python
 
    {
       "action":"search",
       "query": "الكوثر",
       "sortedby":"score",
       "page": 1,
       "word_info":True,
       "highlight":"css",
       "script": "standard",
       "prev_aya": True,
       "next_aya": True,
       "sura_info": True,
       "aya_position_info":  True,
       "aya_theme_info":  True,
       "aya_stat_info":  True,
       "aya_sajda_info":  True,
       "annotation_word": True,
       "annotation_aya": True,
       "translation":"None",
       "recitation": 1

     }

response:

.. code-block:: python
    
    {
        
        "search": {
                    "runtime": 1.0951571464538574, 
                    "interval": {
                                    "start": 1, 
                                    "total": 1, 
                                    "end": 1
                                }
                    "words": {
                                "global": {
                                            "nb_words": 1,
                                            "nb_matches": 1, 
                                            "nb_vocalizations": 1, 
                                            },
                                "1": {
                                        "word": "\u0627\u0644\u0643\u0648\u062b\u0631", 
                                        "nb_matches": 1, 
                                        "nb_ayas": 1,
                                        "nb_vocalizations": 1, 
                                        "vocalizations": ["\u0627\u0644\u0652\u0643\u064e\u0648\u0652\u062b\u064e\u0631\u064e"], 
                                      }, 

                             }, 

                    "ayas": {
                                "1": {
                                        
                                            "identifier": {
                                                                "gid": 6205, 
                                                                "aya_id": 1,
                                                                "sura_id": 108, 
                                                                "sura_name": "\u0627\u0644\u0643\u0648\u062b\u0631", 

                                                             }, 
                                            "aya": {
                                                    "id": 1,
                                                    "text": "\u0625\u0650\u0646\u0651\u064e\u0627 \u0623\u064e\u0639\u0652\u0637\u064e\u064a\u0652\u0646\u064e\u0627\u0643\u064e <span class=\"match term0\">\u0627\u0644\u0652\u0643\u064e\u0648\u0652\u062b\u064e\u0631\u064e</span>",
                                                    "recitation": "http://www.everyayah.com/data/Abdul_Basit_Murattal_64kbps/108001.mp3", 
                                                    "translation": null, 
                                                    "prev_aya": {
                                                                    "id": 7, 
                                                                    "sura": "\u0627\u0644\u0645\u0627\u0639\u0648\u0646",
                                                                    "text": "\u0648\u064e\u064a\u064e\u0645\u0652\u0646\u064e\u0639\u064f\u0648\u0646\u064e \u0627\u0644\u0652\u0645\u064e\u0627\u0639\u064f\u0648\u0646\u064e", 
                                                                }, 
                                                    "next_aya": {
                                                                    "id": 2, 
                                                                    "sura": "\u0627\u0644\u0643\u0648\u062b\u0631",
                                                                    "text": "\u0641\u064e\u0635\u064e\u0644\u0651\u0650 \u0644\u0650\u0631\u064e\u0628\u0651\u0650\u0643\u064e \u0648\u064e\u0627\u0646\u0652\u062d\u064e\u0631\u0652", 
                                                                }, 
                                                    },


                                            "sura": {
                                                        "id": 108,
                                                        "name": "\u0627\u0644\u0643\u0648\u062b\u0631", 
                                                        "type": "\u0645\u0643\u064a\u0629", 
                                                        "order": 15, 
                                                        "stat": {
                                                                    "ayas": 3, 
                                                                    "words": 10,
                                                                    "letters": 42, 
                                                                    "godnames": 0, 

                                                                  }, 
                                                    }, 
                                            "theme": {
                                                                "chapter": "\u0623\u0631\u0643\u0627\u0646 \u0627\u0644\u0625\u0633\u0644\u0627\u0645 ", 
                                                                "topic": "\u0627\u0644\u062d\u062c \u0648\u0627\u0644\u0639\u0645\u0631\u0629 ", 
                                                                "subtopic": null
                                                      }, 

                                            
                                            "position": {
                                                            "rub": 0, 
                                                            "manzil": 7, 
                                                            "ruku": 550, 
                                                            "hizb": 60, 
                                                            "page": 602
                                                        }, 
                                            "sajda": {
                                                        "exist": false, 
                                                        "id": null,
                                                        "type": null
                                                     }, 
            
                                            "stat": {
                                                        "letters": 16, 
                                                        "godnames": 0, 
                                                        "words": 3
                                                    }, 
                                            "annotations": {
                                                                "1": {
                                                                        "arabicroot": null, 
                                                                        "arabicmood": null, 
                                                                        "number": null, 
                                                                        "spelled": "\u0627\u0646\u0627\u0653", 
                                                                        "aspect": null, "word_gid": 75871, 
                                                                        "word_id": 1, 
                                                                        "mood": null, 
                                                                        "arabicspecial": "\u0625\u0650\u0646\u0651", 
                                                                        "state": null, 
                                                                        "arabiclemma": "\u0625\u0650\u0646\u0651", 
                                                                        "gid": 116333, 
                                                                        "type": "Particles", 
                                                                        "aya_id": 1, 
                                                                        "arabictoken": null, 
                                                                        "form": null, 
                                                                        "pos": "Accusative particle", 
                                                                        "arabiccase": "\u0645\u0646\u0635\u0648\u0628", 
                                                                        "part": "\u062c\u0630\u0639", 
                                                                        "normalized": "\u0625\u0646\u0627\u0653", 
                                                                        "case": "Accusative case", 
                                                                        "sura_id": 108, 
                                                                        "word": "\u0625\u0650\u0646\u0651\u064e\u0627\u0653", 
                                                                        "derivation": null, 
                                                                        "arabicpos": "\u062d\u0631\u0641 \u0646\u0635\u0628", 
                                                                        "person": null, 
                                                                        "token": null, 
                                                                        "gender": null, 
                                                                        "voice": null, 
                                                                        "order": 1
                                                                     }, 
                                                                "2": {
                                                                        "arabicroot": "\u0639\u0637\u0648", 
                                                                        "arabicmood": null, 
                                                                        "number": "\u062c\u0645\u0639", 
                                                                        "spelled": "\u0627\u0639\u0637\u064a\u0646\u0670\u0643", 
                                                                        "aspect": "Perfect verb", 
                                                                        "word_gid": 75872, 
                                                                        "word_id": 2, 
                                                                        "mood": null, 
                                                                        "arabicspecial": null, 
                                                                        "state": null, 
                                                                        "arabiclemma": null, 
                                                                        "gid": 116335, 
                                                                        "type": "Verbs", 
                                                                        "aya_id": 1, 
                                                                        "arabictoken": null, 
                                                                        "form": "Fourth form", 
                                                                        "pos": "Verb", 
                                                                        "arabiccase": null, 
                                                                        "part": "\u062c\u0630\u0639", 
                                                                        "normalized": "\u0623\u0639\u0637\u064a\u0646\u0670\u0643", 
                                                                        "case": null, 
                                                                        "sura_id": 108, 
                                                                        "word": "\u0623\u064e\u0639\u0652\u0637\u064e\u064a\u0652\u0646\u064e\u0670\u0643\u064e", 
                                                                        "derivation": null, 
                                                                        "arabicpos": "\u0641\u0639\u0644", 
                                                                        "person": "\u0645\u062a\u0643\u0644\u0645", 
                                                                        "token": null, 
                                                                        "gender": "\u0645\u0630\u0651\u0643\u0631", 
                                                                        "voice": null, 
                                                                        "order": 1
                                                                     }, 
                                                                "3": {
                                                                        "arabicroot": null, 
                                                                        "arabicmood": null, 
                                                                        "number": null, 
                                                                        "spelled": "\u0671\u0644\u0643\u0648\u062b\u0631", 
                                                                        "aspect": null, 
                                                                        "word_gid": 75873, 
                                                                        "word_id": 3, 
                                                                        "mood": null, 
                                                                        "arabicspecial": null, 
                                                                        "state": null, 
                                                                        "arabiclemma": null, 
                                                                        "gid": 116337, 
                                                                        "type": "determiner", 
                                                                        "aya_id": 1, 
                                                                        "arabictoken": "\u0627\u0644", 
                                                                        "form": null, 
                                                                        "pos": null, 
                                                                        "arabiccase": null, 
                                                                        "part": "\u0633\u0627\u0628\u0642", 
                                                                        "normalized": "\u0671\u0644\u0643\u0648\u062b\u0631", 
                                                                        "case": null, 
                                                                        "sura_id": 108, 
                                                                        "word": "\u0671\u0644\u0652\u0643\u064e\u0648\u0652\u062b\u064e\u0631\u064e", 
                                                                        "derivation": null, 
                                                                        "arabicpos": null, 
                                                                        "person": null, 
                                                                        "token": "al", 
                                                                        "gender": null, 
                                                                        "voice": null, 
                                                                        "order": 1
                                                                     }
                                                            },
                                                },
                            }, 
                    "translation_info": {}, 
                    }, 

        "error": {
                    "code": 0,
                    "msg": "success ## action=search ; query=\u0627\u0644\u0643\u0648\u062b\u0631", 
                 }
        }

------------
Translations
------------
TODO

-----------
Information
-----------
flags:

.. code-block:: python

    {
        "action"="show",
        "query"="information"
    }

response:

.. code-block:: python
      
      {
          "show": {
              "information": {
                  "engine": "Alfanous",
                  "wiki": "http://wiki.alfanous.org/doku.php?id=json_web_service",
                  "description": "Alfanous is a Quranic search engine provides simple and advanced search services in the diverse information of the Holy Quran .",
                  "author": "Assem chelli",
                  "version": "0.5",
                  "contact": "assem.ch@gmail.com",
                  "console_note": "this is console interface of Alfanous, try -h to get help ",
                  "json_output_system_note": "\n    This is the <a href='http://json.org/'>JSON</a> output system of <a href=\"http://wiki.alfanous.org\">Alfanous</a> project .This feature is in Alpha test and the Json schema may be it's not stable . We are waiting for real feadbacks and suggestions to improve its efficacity,quality and stability. To contact the author ,please send a direct email to <b> assem.ch[at]gmail.com</b> or to the mailing list <b>alfanous [at] googlegroups.com</b>\n    <br/><br/> For more details  visit the page of this service <a href=\"http://wiki.alfanous.org/doku.php?id=json_web_service\">here</a>\n    "
              }
          },
          "error": {
              "msg": "success ## action=show ; query=information",
              "code": 0
          }
      }

-----------
Recitations
-----------

flags:

.. code-block:: python

    {
        "action"="show",
        "query"="recitations"
    }

response (sample):

.. code-block:: python
      
      {
          "show": {
              "recitations": {
                  "45": {
                      "bitrate": "192kbps",
                      "name": "English/Ibrahim Walk TEST",
                      "subfolder": "English/Ibrahim_Walk_192kbps_TEST"
                  },
                  "54": {
                      "bitrate": "128kbps",
                      "name": "Salah Al Budair",
                      "subfolder": "Salah_Al_Budair_128kbps"
                  }
                  
      
              }
          },
          "error": {
              "msg": "success ## action=show ; query=recitations",
              "code": 0
          }
      }

------
Fields
------

flags:

.. code-block:: python

    {
        "action"="show",
        "query"="fields"
    }

response:

.. code-block:: python
            
      {
          "show": {
              "fields": {
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
          },
          "error": {
              "msg": "success ## action=show ; query=fields",
              "code": 0
          }
      }



