============
Alfanous API
============


-------
Install
-------
.. code-block:: sh

    $ sudo python setup.py install



-------
Console
-------
.. code-block:: sh

    $ alfanous-console -h

-----------
Quick Start
-----------

.. code-block:: python

    # import Output object 
    from alfanous.Outputs import Raw
    
    # import default Paths
    from alfanous.Data import Paths
    
    # Initialize search engines 
    RAWoutput = Raw( 
                        QSE_index = Paths.QSE_INDEX	, # Quranic Main index path
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
                 "query": u"الحمد لله",
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



