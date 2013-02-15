==============
Code Structure
==============

This is a quick view of the source code structure of Alfanous project explaining the different packages and modules.

--------
Packages
-------- 

:alfanous: the main API of the project, offers the search features. 
:alfanous-import: a library responsible of all management tasks of Quranic & Linguistic resources. 
:alfanous-cgi: a small script to execute the API in a web CGI environment. 
:alfanous-desktop: a desktop interface made by QT & PyQt.
:alfanous-django: a django app replaces the old web user interface and also the cgi script.
:alfanous-labs:  all related libraries that still in alpha phase.
:alfanous-tests: scripts used to test the different modules of the API.
:PyCorpus: a library used to parse & understand Arabic Quranic Corpus.
:PyZekrModels: a library used to parse Zekr Translations Models.


-----------------------------
API Modules, Files (alfanous)
-----------------------------

:main.py: the main module that relay all the modules.
:console.py: a console interface for the API.
:Outputs.py: the programming interface, responsible of the output of all results.
:Data.py: the manager of paths and Data reading and loading.
:TextProcessing.py: the module responsible of searched/indexed text processing.
:QueryProcessing.py: the module responsible of search query processing.
:ResultsProcessing.py: the module responsible of results processing.
:Indexing.py: the manager of the indexes reading.
:Searching.py: the module responsible of the basic search operation.
:Suggestions.py: the module responsible of suggestions.
:Romanization.py: the module responsible of romanization systems.
:Threading.py: the module responsible of multi-processing during the search.
:Constants.py: a module that contains some constants used in the API.
:Exceptions.py: a module that contains some exceptions used in the API.
:Misc.py: a pre-implementing test module.
:Support.*: Some third-party libraries.
:configs.*: Configuration files in a Json format.
:resources.*: Quranic & Lingustic data in a Json format to replace the binary sqlite database.
:dynamic_resources.*: Compiled linguistic data to python modules to gain speed.
:indexes.*:  All needed indexes on Whoosh indexes format.
:setup.py: the script of installation & packaging (setuptools)
:ez_setup.py: an alternatif for setuptools library.





----------------------------------
Importer Modules (alfanous-import)
----------------------------------
:main.py: the main module that relays all the modules and offers a console interface.
:Downloader.py: download online resources.
:Parser.py: parse the resources.
:Standardizer.py: convert the resources to a standard format (not implemented).
:Importer.py: import the resources into the main database.
:Transformer.py: transfer&convert the resources from the main database into Whoosh indexes.
:Updater.py: update the data in API based on actual resources.
:initial_importing.py: a script used the first-time to load many resources (deprecated).
:setup.py: the script of installation & packaging (setuptools).
