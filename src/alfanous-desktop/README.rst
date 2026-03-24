=========================
AlfanousDesktop Interface
=========================
A PyQt GUI interface for alfanous Quranic search engine API. 

------------
Requirements
------------
* `Alfanous API <https://github.com/Alfanous-team/alfanous/blob/master/src/alfanous/README.rst>`_
* `pyside <http://qt-project.org/wiki/PySide>`_
* `Qt5 <http://qt-project.org/wiki/Qt_5.0>`_
* `pyparsing <http://pyparsing.wikispaces.com/>`_

------------------
How to contribute?
------------------
* Browse the issues under the milstone: `AlfanousDesktop 0.7 <https://github.com/Alfanous-team/alfanous/issues?milestone=1&state=open>`_
* Read about how to use `Alfanous API <https://github.com/Alfanous-team/alfanous/blob/master/src/alfanous/README.rst>`_, Qt designer, PyQt 
* Fork the source, Do your changes then make a pull request to `Alfanous-team/alfanous <https://github.com/Alfanous-team/alfanous>`_

----------------
Building systems
----------------
* deb package for ubuntu and derivatives: https://code.launchpad.net/~team4alfanous/+recipe/alfanous-daily
* rpm package for redhat, fedore, opensuse,centos: https://build.opensuse.org/package/show/home:Kenzy:tahadz/alfanous

**notes:**  

#. The UI folder contains forms and dialogs , you can open them with Qt designer.
#. Run the command "make qt_all" in project root to compile qt resources to a python module.
#. Gui.py contains the main code, it's unclean and need cleaning or rewriting from the scratch.

