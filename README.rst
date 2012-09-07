=================
What is Alfanous?
=================
Alfanous is a Quranic search engine API that offers simple and advanced search services in the whole information that Holy Qur’an contains. it is based on the modern approach of information retrieval to get a good-stability and a high-speed search. We want implement some additional features like Highlight, Suggestions, Scoring …etc.by the way, a Quranic search engine is an Arabic search engine so we have to offer Arabic language processing like the stemming and eliminating of ambiguities. The API is aimed to be the base that the developers can use it to build different types of interfaces in different systems, ex: Desktop GUI 



:Authors: `Authors.rst <https://github.com/Alfanous-team/alfanous/blob/master/AUTHORS.rst>`_
:Version: 0.7.##
:License: `AGPL <https://github.com/Alfanous-team/alfanous/blob/master/LICENSE>`_
:Tracker: `Alfanous-team/alfanous/Issues <https://github.com/Alfanous-team/alfanous/issues>`_
:Mailinglist: `alfanous@googlegroups.com <http://groups.google.com/group/alfanous/>`_
:Website: `Alfanous.org <http://www.alfanous.org/>`_
:Accounts: `@Facebook <https://www.facebook.com/alfanous>`_ `@Twitter <https://twitter.com/alfanous>`_ `@GooglePlus <https://plus.google.com/111305625425237630318>`_ 
        | `@Sourceforge <http://sourceforge.net/projects/alfanous/>`_ `@Launchpad <http://www.launchpad.net/alfanous/>`_



--------
Contacts
--------
- If you have a concrete bug report for Alfanous please go to the `Issues Tracker  <https://github.com/Alfanous-team/alfanous/issues>`_, submit your report and tag it "bug".

- If you want to participate in actively developing Alfanous,  read this `How to contribute?  <https://github.com/Alfanous-team/alfanous/blob/master/FAQ.rst#how-to-contribute>`_. 

- If you want to help in Alfanous somehow,  read this `How you can help?  <https://github.com/Alfanous-team/alfanous/blob/master/FAQ.rst#how-you-can-help>`_. 

- If you have a feature request, a proposition or a question for the project, you may use the mailing list.

- If you want to criticize the project, we'll be thankful if you resume your criticism and send it to the mailing list.

For anything else, you can contact us via the mailing list:  `alfanous@googlegroups.com <http://groups.google.com/group/alfanous>`_ .
Here also the emails of `Maintainers <https://github.com/Alfanous-team/alfanous/blob/master/AUTHORS.rst#maintainers>`_, use them wisely.


--------------
 Why Alfanous? 
--------------

* Alfanous is FREE LIBRE OPEN SOURCE: Any one can use it and any one can contribute in coding, translating, design...etc. Alfanous will die only if his community dies!

* Alfanous is a Python API: that allows anyone to create independently a web interface, desktop interface , Android/Iphone/Windows phone interfaces , facebook/twitter/G+ applications ...and so on. The search process is too fast and too stable

* Alfanous is a research project : so we figure out features not only do what other websites/applications do.

* Alfanous has lot of features: see `Search Features`_.

* Alfanous has many interfaces for many platforms: see `Interfaces`_.

* Alfanous is FREE GRATIS: no payment, no ads. 

see `FAQ <https://github.com/Alfanous-team/alfanous/blob/master/FAQ.rst>`_

----------
Interfaces
----------
#. Alfanous Python API, `source <https://github.com/Alfanous-team/alfanous/tree/master/src/alfanous>`_.
#. JSON web interface, `link <http://www.alfanous.org/json>`_, actually we're moving to JSON web interface II, `source <https://github.com/Alfanous-team/alfanous/tree/master/src/alfanous-cgi>`_.
#. Web User interface [Arabic], `link <http://wui.alfanous.org/>`_, `source <https://github.com/Alfanous-team/alfanous/tree/master/interfaces/web/wui>`_.
#. Web User interface for mobiles [Multi-language], `link <http://m.alfanous.org/>`_, `source <https://github.com/Alfanous-team/alfanous/tree/master/interfaces/web/mobile_wui>`_.
#. Alfanous Desktop application (Windows: `[Arabic] <http://sourceforge.net/projects/alfanous/files/Interfaces/AlfanousDesktop/0.3/alfanousDesktop-windows-0.3ar.exe/download>`_ `[English] <http://sourceforge.net/projects/alfanous/files/Interfaces/AlfanousDesktop/0.4.3/alfanousInstallerV0.4.3.exe/download>`_; Ubuntu/Sabily), `source <https://github.com/Alfanous-team/alfanous/tree/master/src/alfanous-desktop>`_. 
#. Alfanous Firefox toolbar, `link <https://addons.mozilla.org/en-us/firefox/addon/alfanous-toolbar/>`_, `source <https://github.com/Alfanous-team/alfanous/tree/master/interfaces/toolbars/firefox>`_.
#. Alfanous Firefox search bar addon, `link <https://addons.mozilla.org/en-us/firefox/addon/alfanous/>`_.
#. Django app (alpha), `source <https://github.com/Alfanous-team/alfanous/tree/master/src/alfanous-django>`_.
#. Chrome extension (alpha), `source <https://github.com/Alfanous-team/alfanous/tree/master/interfaces/toolbars/chrome>`_.
#. App for Nokia S60 (prototype), `source <https://github.com/Alfanous-team/alfanous/tree/master/interfaces/smart_phones/alfanousS60>`_.
#. Facebook app (prototype), `source <https://github.com/Alfanous-team/alfanous/tree/master/interfaces/web/facebook_app>`_.
#. Third party:
  * `Alfanous4WP7 <http://www.windowsphone.com/en-US/apps/f9e1504d-ce31-4802-a2d1-24ff9f41a06e>`_ by  Abdelmoumen BOUABDALLAH ,  source: unavailable.
  * `Alfanous4Iphone <http://itunes.apple.com/us/app/alfanws-mhrk-bhth-qrany-mtqdm/id543646326?mt=8>`_ by i4islam, source: closed.

**note:** you can find the perspective interfaces under the milestone: `Extra Interfaces <https://github.com/Alfanous-team/alfanous/issues?milestone=8&page=1&sort=updated&state=open>`_.

---------------
Search Features
---------------
This is the list of search features already implemented, preview links use Alfanous web user interface: www.alfanous.org. 

#. Exact Word: that is the simple search, eg: `فأسقيناكموه <http://alfanous.org/?search=%D9%81%D8%A3%D8%B3%D9%82%D9%8A%D9%86%D8%A7%D9%83%D9%85%D9%88%D9%87>`_
#. Phrase: for searching a whole phrase rather then independent words, eg:`"رسول الله" <http://alfanous.org/%22%D8%B1%D8%B3%D9%88%D9%84%20%D8%A7%D9%84%D9%84%D9%87%22>`_
#. Logical relations

   * Conjuction: for searching only the ayahs that contains two terms or more, eg: `الصلاة + الزكاة <http://alfanous.org/?search=%D8%A7%D9%84%D8%B5%D9%84%D8%A7%D8%A9%20%2B%20%D8%A7%D9%84%D8%B2%D9%83%D8%A7%D8%A9>`_.
   * Disjunction (default): for searching all the ayahs that contains one of two terms or more, eg:`الصلاة | الزكاة <http://alfanous.org/?search=%D8%A7%D9%84%D8%B5%D9%84%D8%A7%D8%A9%20%7C%20%20%D8%A7%D9%84%D8%B2%D9%83%D8%A7%D8%A9>`_.
   * Exception: for eleminating a term from search results, eg:`الصلاة - الزكاة <http://alfanous.org/?search=%D8%A7%D9%84%D8%B5%D9%84%D8%A7%D8%A9%20-%20%20%D8%A7%D9%84%D8%B2%D9%83%D8%A7%D8%A9>`_. You can understand it as "Ayahs that contains الصلاة but doesn't contain الزكاة". 

#. Wildcards or Jokers: for search all words that share many letters, we have:
 
   * Asterisk: replace zero or many undefined letters, eg: `*نبي* <http://alfanous.org/?search=*%D9%86%D8%A8%D9%8A*>`_
   * Interogation mark: replace one undefined letter, eg: `نعم؟ <http://alfanous.org/?search=%D9%86%D8%B9%D9%85%D8%9F>`_

#. Fielded  search: to search in more information of Quran , not only ayahs'text, we cite here the most significant fields for users:

   * aya_id or رقم_الآية (Aya local ID): that's the number of ayah inside its sura, use it for example to search all first ayahs (`رقم_الآية:1 <http://alfanous.org/?search=%D8%B1%D9%82%D9%85_%D8%A7%D9%84%D8%A2%D9%8A%D8%A9%3A1>`_).
   * sura_id or رقم_السورة (Sura ID): use it with  aya_id to specify an exact ayah,for example the first ayah of surate an-nass will be :  `aya_id:1 + sura_id:114 <http://alfanous.org/?search=aya_id%3A1%20%2Bsura_id%3A114>`_.       
   * subject or موضوع (Topics): thats field contains all topics information, it will be helpful to search for a topic,eg:  `موضوع:الشيطان <http://alfanous.org/?search=%D9%85%D9%88%D8%B6%D9%88%D8%B9%3A%D8%A7%D9%84%D8%B4%D9%8A%D8%B7%D8%A7%D9%86%20>`_
   for more fields, see: `Fields <https://github.com/Alfanous-team/alfanous/tree/master/src/alfanous#fields>`_

#. Intervals: this will be helpful in statistics or positions, for example search the divine name only in the first surahs: `رقم_السورة :[1 الى 5 ] + الله <http://alfanous.org/?search=%D8%B1%D9%82%D9%85_%D8%A7%D9%84%D8%B3%D9%88%D8%B1%D8%A9%20%3A%5B1%20%D8%A7%D9%84%D9%89%205%20%5D%20%2B%20%D8%A7%D9%84%D9%84%D9%87>`_
#. Partial vocalization: to consider given diacritics and ignore the others, eg: `آية_ :'مَن' <http://alfanous.org/?search=%D8%A2%D9%8A%D8%A9_%20%3A'%D9%85%D9%8E%D9%86'>`_.
#. Word Properties: to search using root and type of words, type could be اسم, فعل or أداة,eg: `{قول،اسم} <http://alfanous.org/?search=%7B%D9%82%D9%88%D9%84%D8%8C%D8%A7%D8%B3%D9%85%7D%20>`_.
#. Derivations

   * light (using lemma): to search all the words having the same lemma of the given word,eg: `>ملك <http://alfanous.org/?search=%3E%D9%85%D9%84%D9%83>`_.
   * heavy (using root): to search all the words having the same root of the given word,eg: `>>ملك <http://alfanous.org/?search=%3E%3E%D9%85%D9%84%D9%83>`_. 


**note:** you can find the perspective search features under the milestones: `Quranic Search Features Pack 1 <https://github.com/Alfanous-team/alfanous/issues?milestone=7&state=open>`_,  `Quranic Search Features Pack 2 <https://github.com/Alfanous-team/alfanous/issues?milestone=10&state=open>`_.

-------
History
-------
- **02 January 2012**: Launching new web interface for mobiles, uses: json_web_service_, link: http://m.alfanous.org/, wiki: mobile_web_interface_

- **19 September 2011**: Launching a new web interface with a new design based on the json_web_service_, the link is:  http://wui.alfanous.org

- **26 July 2011**: Launching json_web_service_ of Alfanous ,this service is available in the link: http://www.alfanous.org/json 

- **06 March 2011**:A Symposium  in Riyadh - Saudi Arabia called NITS2011 or Third National Information Technology Symposium "Arabic an d Islamic Contents on the Internet",the search paper published in Arabic with the name “Indexation/Search API in Holy Qur'an”

- **17 January 2010**: Launching the arabic web-interface and reserving the domain alfanous.org_ 

- **29 November 2010**: Uploading the english_interface_ of alfanous-Desktop version 0.4 beta for Windows and Linux

- **19 October 2010**: A workshop in Damascus called “.......”,the search paper published in Arabic with the name “Indexation/Search API in Holy Qur'an”

- **21 July 2010**: Uploading the arabic_interface_ of alfanous-Desktop version 0.3 beta for Windows

- **30 September 2010 - 6 July 2011**: Graduation project for obtaining State-Engineer degree in National higher school of computer science (ESI ,ex.INI) - Algiers. The project was entitled *“Developpement  d'un moteur d'indexation et de recherche dans les documents coranique”*. 
  
--------------
Featured Posts
--------------
- *Alfanous, mesin pencari ayat Al-Quran masa depan*, ahmadbinhanbalblog_
- *الفانوس مشروع محرك بحث متقدم للقرآن الكريم*,  arabcrunch_
- *جزائري يطلق محرك بحث شامل للقرآن الكريم*, onislam_
- *Alfanous – Quran Search Engine*, muslihzarthblog_ 
**Note:**  If you wrote -yourself- a good post about Alfanous in any language, please just tell us to refer it here!

--------
See also
--------
#. `Application Programming Interface & Console Interface <https://github.com/Alfanous-team/alfanous/tree/master/src/alfanous>`_

#. `JSON output system <https://github.com/Alfanous-team/alfanous/tree/master/src/alfanous-cgi>`_

#. `Desktop Interface <https://github.com/Alfanous-team/alfanous/tree/master/src/alfanous-desktop>`_

#. `Django application <https://github.com/Alfanous-team/alfanous/tree/master/src/alfanous-django>`_

#. `Web user interface <https://github.com/Alfanous-team/alfanous/tree/master/interfaces/web/wui>`_

.. _json_web_service: https://github.com/assem-ch/alfanous/blob/master/src/alfanous-cgi/README.rst
.. _mobile_web_interface: https://github.com/assem-ch/alfanous/tree/master/interfaces/web
.. _alfanous.org: http://old.alfanous.org
.. _english_interface: http://sourceforge.net/projects/alfanous/files/Interfaces/AlfanousDesktop/0.4.20
.. _arabic_interface: http://sourceforge.net/projects/alfanous/files/Interfaces/AlfanousDesktop/0.3/alfanousDesktop-windows-0.3ar.exe/download
.. _ahmadbinhanbalblog: http://ahmadbinhanbal.wordpress.com/2011/10/24/alfanous-mesin-pencari-ayat-al-quran-masa-depan/
.. _onislam: http://www.onislam.net/arabic/health-a-science/technology/128137-2011-01-24-13-55-24.html
.. _muslihzarthblog: http://muslihzarth.wordpress.com/2010/12/13/alfanous-quran-search-engine/
.. _saidmaroc: http://www.saidmaroc.com/2010/07/blog-post_23.html
.. _arabcrunch: http://arabcrunch.com/ar/2011/09/%D8%A7%D9%84%D9%81%D8%A7%D9%86%D9%88%D8%B3-%D9%85%D8%B4%D8%B1%D9%88%D8%B9-%D9%85%D8%AD%D8%B1%D9%83-%D8%A8%D8%AD%D8%AB-%D9%85%D8%AA%D9%82%D8%AF%D9%85-%D9%84%D9%84%D9%82%D8%B1%D8%A2%D9%86-%D8%A7%D9%84/