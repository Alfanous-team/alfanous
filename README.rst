  .. image:: https://img.shields.io/pypi/v/alfanous.svg
        :target: https://pypi.python.org/pypi/alfanous

  .. image:: https://travis-ci.org/Alfanous-team/alfanous.png?branch=master
            :target: https://travis-ci.org/Alfanous-team/alfanous

================
Alfanous Project
================
-----------------
What is Alfanous?
-----------------


Alfanous is a functional, dynamic, comprehensive Qur’an search engine that has been effectively designed to carry out simple or advanced Quranic searches.

:Authors: `Authors.rst <https://github.com/Alfanous-team/alfanous/blob/master/AUTHORS.rst>`_
:Mailinglist: `alfanous@googlegroups.com <http://groups.google.com/group/alfanous/>`_
:Website: `Alfanous.org <http://www.alfanous.org/>`_
:Doc: `Readthedocs <http://alfanous.readthedocs.org/en/latest/>`_

-----
Usage
-----
Install it from Pypi:

.. code-block:: sh

    $ sudo pip install alfanous

You can use it from console:

.. code-block:: sh

    $ alfanous-console -a search -q الله 
    $ alfanous-console -a search -q Allh 

or from Python:

.. code-block:: python

    >>> import alfanous
    >>> alfanous.search(u"الله")
    >>> alfanous.do({"action":"search","query":u"الله"})
    >>> alfanous.do({"action":"search","query":u"Allh"}) # Buckwalter transliteration

You can use it also from the web service: 

http://alfanous.org/api/search?query=الله

http://alfanous.org/api/search?query=Allh


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


--------
See also
--------
#. `Application Programming Interface & Console Interface <https://github.com/Alfanous-team/alfanous/tree/master/src/alfanous>`_
