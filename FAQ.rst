==========================
Frequently.Asked.Questions 
==========================

-----------------
What is Alfanous? 
-----------------
see `what-is-alfanous <https://github.com/Alfanous-team/alfanous/blob/master/README.rst#what-is-alfanous>`_.

--------------
Why Alfanous? 
--------------
see `why-alfanous <https://github.com/Alfanous-team/alfanous/blob/master/README.rst#why-alfanous>`_.

--------------------------
Why we called it Alfanous?  
--------------------------
Alfanous is an arabic word "الفانوس"  that means the Lantern. The name was inspired from a picture that contains a Mushaf, a chronometer and a lantern. 


------------------
How to contact us?
------------------
see `contacts <https://github.com/Alfanous-team/alfanous#contacts>`_.

-----------------
How you can help?
-----------------
You can help us by:

- Spreading the word 

  - Following and sharing our social network pages : `@Facebook <https://www.facebook.com/alfanous>`_ `@Twitter <https://twitter.com/alfanous>`_ `@GooglePlus <https://plus.google.com/111305625425237630318>`_ 
  - Sharing a link to `our website <www.alfanous.org>`_ via your accounts in Social networks.
  - Pointing  skilled developers and Quranic researchers to the importance of the project.
  - Writing articles about the project in blogs, newspapers.
  - Showing a banner on your Blog/Website.
  - creating an ad for alfanous links using Google adwords or facebook if you're familiar with that (btw,it needs money) 

- Managing and Animating our social network pages with news and daily posts [Arabic, English]: `@Facebook <https://www.facebook.com/alfanous>`_ `@Twitter <https://twitter.com/alfanous>`_ `@GooglePlus <https://plus.google.com/111305625425237630318>`_ 

- Translating project interfaces to your language , we are using Launchpad platform for translation, link `here <https://translations.launchpad.net/alfanous/trunk>`_.

- Testing the modules and releases, Reporting bugs , see `How to report a bug?`_ and `How to help by testing?`_ .
- Fixing `bugs <https://github.com/Alfanous-team/alfanous/issues?labels=bug&milestone=&page=1&state=open>`_ , Coding `new features <https://github.com/Alfanous-team/alfanous/issues/milestones>`_ or Developing `new interfaces <https://github.com/Alfanous-team/alfanous/issues?milestone=8&page=1&state=open>`_ , See: `How to Contribute?`_ .
- Designing  Icons, Logoes , Banners.
- Packaging the project for different systems: Windows, Linux distributions, MacOs.
- Donating/Supporting to the project: *We're stuck looking for possible ways for donations/Funding. Any help is appreciated!*

For more discussion, you can contact us via the mailing list : `alfanous@googlegroups.com <http://groups.google.com/group/alfanous/>`_


--------------------
How to report a bug?
--------------------
If you have a concrete bug report for Alfanous please go to the `Issues Tracker  <https://github.com/Alfanous-team/alfanous/issues>`_, submit your report and tag it "bug".

---------------------------------
How to contribute by translation?
---------------------------------
- Contact us to confirm the translation need into your language and to request the PO file.
- Use Use Poedit or Virtaal to edit it and complete the translation.
- Send us the update po file so we can include it in the website.

------------------------------
How to contribute by donation?
------------------------------
Funding is a critical point for our project. Whereas we're stuck looking for possible ways to get. Donations as far as we tried is so restricted in our home country so Any help in that is appreciated!

Any way you can:

- Pay our web hosting monthly bills directly, we create an account for you in the host to do that.
- Lead an advertising compaign for the project website through `Google adwords <adwords.google.com>`_ or `Facebook <https://www.facebook.com/business/connect>`_.
- Incubate the whole project in another country.

----------------------------
How to contribute by coding? 
----------------------------
If you are a coder, and want to participate in actively developing Alfanous :

#. Learning Git is essential, read about `Set up Git <https://help.github.com/articles/set-up-git>`_ and you can also try it online `here <http://try.github.com/levels/1/challenges/1>`_!
#. Browse a `milestone <https://github.com/Alfanous-team/alfanous/issues/milestones>`_ and choose an open issue (or more) that fits your skills.
#. To get more information about any issue you can contact us on `mailing list:  <http://groups.google.com/group/alfanous/>`_ or leave a comment on the issue.
#. Start with forking the repository and preparing your development environment, see `How to prepare your development environment to contribute?`_.
#. Prepare your changes, test them and then make a pull request to `alfanous-team <https://github.com/Alfanous-team/alfanous>`_ when you think your code is ready.
#. The project is not well documented but you may find helpful information in Readme files:

   - `Application Programming Interface & Console Interface <https://github.com/Alfanous-team/alfanous/tree/master/src/alfanous>`_
   - `JSON output system <https://github.com/Alfanous-team/alfanous/tree/master/src/alfanous-cgi>`_
   - `Desktop Interface <https://github.com/Alfanous-team/alfanous/tree/master/src/alfanous-desktop>`_
   - `Django application <https://github.com/Alfanous-team/alfanous/tree/master/src/alfanous-django>`_
   - `Web user interface <https://github.com/Alfanous-team/alfanous/tree/master/interfaces/web/wui>`_

See also `How you can help?`_


-----------------------
How to help by testing? 
-----------------------
If you want to help us testing  the project modules, just follow these steps and  Sooner as  you encounter a problem, stop testing and  submit it as an issue in  our issue tracker  and then send about it to the mailing list (alfanous@googlegroups.com):

#. Get the code source:

   - clone the git repo  from github:  $ git clone https://github.com/Alfanous-team/alfanous.git
   - or download it as a `zipfile <https://github.com/Alfanous-team/alfanous/zipball/master>`_ 

#. Run the build: 

   - Install all building dependencies: `pyparsing <http://pyparsing.wikispaces.com/>`_, `pyside <http://qt-project.org/wiki/Get-PySide>`_, `epydoc <http://epydoc.sourceforge.net/>`_,
     `sphinx <http://sphinx.pocoo.org/>`_.

   - Go to the root path of the code source and execute this command    
   
     .. code-block:: sh
      
          $ make build
  
     **Possible Problems:**

     #. **/bin/sh: python2: not found** : if you dont have the command "python2", create one using a symbolic link
  
        .. code-block:: sh
    
               $ python --version
               Python 2.7.4
               $ sudo ln -s /usr/bin/python2.7 /usr/bin/python2 
               
     
     #. **ImportError: No module named pyparsing** : you need to install pyparsing python library
  
        .. code-block:: sh
    
              $ sudo pip pyparsing

               
        
     

#. Install the API: 

   - Also in the root path of the code source, execute the command
     
     .. code-block:: sh

          $ make install_api_no_arguments
#. Test the console interface, it provides results in Json format:

   .. code-block:: sh

       $ alfanous-console -h
       $ alfanous-console -a search -q qawol
       $ alfanous-console -a search -q الصلاة+الزكاة
       $ ...

#. Test the basic script:

   .. code-block:: sh
        
        $ cd src/alfanous-tests
        $ python sample.py

#. Test the desktop interface:

   .. code-block:: sh
      
        $ cd src/alfanous-desktop
        $ python Gui.py

#. Test the installation of alfanous-desktop as a library

   .. code-block:: sh
          
        $ sudo python setup.py install
        $ alfanous-desktop
    

#. Test the json output system II  

   - install it in apache as a cgi script
     
     .. code-block:: sh
        
         # Install apache2 first
         $ sudo make install_jos2
        
   - test it in browser by checking those links
      
     - http://alfanous.local/cgi-bin/alfanous_json2.py
     - http://alfanous.local/cgi-bin/alfanous_json2.py?action=search&query=qawol
     - http://alfanous.local/cgi-bin/alfanous_json2.py?action=suggest&query=مءصدة
     - http://alfanous.local/cgi-bin/alfanous_json2.py?action=search&query=%D8%A7%D9%84%D9%83%D9%88%D8%AB%D8%B1&sortedby=mushaf&page=1&word_info=true&highlight=css&script=standard&prev_aya=true&next_aya=true&sura_info=true&aya_position_info=true&aya_theme_info=true&aya_stat_info=true&aya_sajda_info=true&annotation_word=true&annotation_aya=true&recitation=1
     - ...


#. Test Django app (don't forget to install `django <https://www.djangoproject.com/>`_)

   - run the server
     
     .. code-block:: sh
        
         $ cd src/alfanous-django
         $ python manage.py runserver
        
   - test it in browser by checking this link
      
     - http://127.0.0.1:8000/wui/

#. Test Firefox toolbar 

   - package it 
     
     .. code-block:: sh
        
         $ make dist_xpi

   - use it,  you'll find the package in output folder with the extension .xpi


#. Test Ubuntu/Sabily package 
   
   - run the command of packaging
     
     .. code-block:: sh
    
         $ make dist_deb

   - Add sabily repository and test the package

#. Test Windows Installer script (later)
#. Test MacOs package (later)
#. Test PyCorpus (later)





See also `How you can help?`_

----------------------------------------------------------
How to prepare your development environment to contribute?
----------------------------------------------------------
Best OS for that is Ubuntu (>11.10).

#. First at all, create an account in `Github <https://github.com>`_ and make your own fork of `alfanous-team/alfanous <https://github.com/Alfanous-team/alfanous>`_ (Fork button is top-right).
#. Secondly, install `git-scm <http://git-scm.com/downloads>`_ and then clone locally your fork : 
      
   .. code-block:: sh
   
       git clone LINK_OF_GITHUB_FORK.

#. Third, install building dependencies :  `pyparsing <http://pyparsing.wikispaces.com/>`_, `pyside <http://qt-project.org/wiki/Get-PySide>`_, `epydoc <http://epydoc.sourceforge.net/>`_,
     `sphinx <http://sphinx.pocoo.org/>`_. 
   - then run in the root of your local repo: 
     
     .. code-block:: sh
    
         $ make build 
   - then run also in the same path: 
     
     .. code-block:: sh

         $ sudo make install_api_no_arguments
   - test the installation with this command: 
     
     .. code-block:: sh

         $ alfanous-console -h

#. Forth, prepare your dev tool :

   - if you want work on web tasks, install `aptana <http://www.aptana.com/>`_ with `pydev <http://pydev.org/>`_ plugin (install apache2 also for local tests).
   - else install `eclipse <http://www.eclipse.org/downloads/>`_ with `pydev <http://pydev.org/>`_ plugin.
   - or you can just use a simple text editor.

   You can also use git with eclipse, by installing `EGit <http://www.eclipse.org/egit/>`_.

--------------
How API works?
--------------
TODO

