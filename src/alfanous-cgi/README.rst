===================
JSON Web Service II
===================
This is the JSON output system version 2 of Alfanous project. This feature is in Alpha test and the JSON schema may be it's not stable. We are waiting for real feadbacks and suggestions to improve its efficacy, quality and stability. To contact us, please send an email to the mailing list <alfanous@googlegroups.com>. If you don't know what is JSON, See: Wikipedia_ or the Official_Website_of_JSON_. It contains many JSON parsing libraries for most programming languages. 

.. _Wikipedia: http://en.wikipedia.org/wiki/JSON
.. _Official_Website_of_JSON: http://www.json.org/

------------
Terms of use
------------
*  This service is free to use.
*  Don't name your application "Alfanous" before we are okey about that.
*  We highly recommend to refer Alfanous engine somewhere in your pages using icons or texts like "Alfanous engine", "Powered by Alfanous.org", or "Based on Alfanous.org" linked to "http://www.alfanous.org" or "http://www.alfanous.org/jos2". 
*  We highly recommend to describe clearly somewhere in your application the relation to the whole Alfanous project, such as an about button.
*  Art works you may need are available here_, the Art is licenced with AGPL license.

.. _here: http://www.alfanous.org/art/

-----------
Limitations
-----------
1. 100 keywords at most
2. Ayah word annotations are enabled for only one ayah

--------------
Quering Syntax
--------------
To get JSON information , use this syntax : http://www.alfanous.org/jos2?ARGUMENT such as ARGUMENT is compound of those flags: `API flags <https://github.com/Alfanous-team/alfanous/blob/master/src/alfanous/README.rst#flags>`_.

--------
Examples
--------
*  `http://www.alfanous.org/jos2?action=search&unit=aya&query=الحمد&highlight=bbcode&sortedby=tanzil&page=2&traduction=1&fuzzy=True`
*  http://www.alfanous.org/jos2?action=show&query=recitations
*  http://www.alfanous.org/jos2?action=show&queryfields
*  http://www.alfanous.org/jos2?action=show&query=All
*  http://www.alfanous.org/jos2?action=show&query=translations 
*  http://www.alfanous.org/jos2?action=show&query=errors
*  `http://www.alfanous.org/jos2?action=suggest&unit=aya&query=مءصدة`

----------------
Response Samples
----------------
See `API Schema Samples <https://github.com/Alfanous-team/alfanous/tree/master/src/alfanous#schema-samples>`_.

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

.. _Fields: https://github.com/Alfanous-team/alfanous/blob/master/src/alfanous/README.rst#fields



------
Demoes
------
(No demoes yet! if you have a demo, we'll be happy to refer it here)



-------------
Who use this?
-------------
If you are using this service, We want to make Alfanous more helpful. We will be happy to know about your applications.
   * Official web interface by AlfanousTeam - `alfanous.org <www.alfanous.org>`_
   * Application for Android by FenyLab - `link <https://play.google.com/store/apps/details?id=com.fenylab.alfanous>`_
   * Application for iPhone/iPad by iPhoneIslam - `link <https://itunes.apple.com/us/app/alfanws-mhrk-bhth-qrany-mtqdm/id543646326?mt=8&ign-mpt=uo%3D4>`_ 
   * Qoogle - Application for Android by Amr Ebada - `link <https://play.google.com/store/apps/details?id=com.roic.amr_ebada.qoogle>`_


