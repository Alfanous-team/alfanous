NSIS installer script
=====================
This script is used to make automatically  the installer of `AlfanousDesktop <https://github.com/Alfanous-team/alfanous/tree/master/src/alfanous-desktop>`_ for windows.

What is NSIS?
    NSIS (Nullsoft Scriptable Install System) is a professional open source system to create Windows installers. It is designed to be as small and flexible as possible and is therefore very suitable for internet distribution. 

How to run the script successfully?
    #. Have a windows OS either XP, Vista or Seven.
    #. Install the python library `py2exe <http://www.py2exe.org/>`_ and all requirments of AlfanousDesktop: 
       `PyQt4 <http://www.riverbankcomputing.co.uk/software/pyqt/download>`_, 
       `pyparsing <http://pyparsing.wikispaces.com/>`_, 
       `configobj <http://www.voidspace.org.uk/python/configobj.html>`_, 
       `alfanous API <https://github.com/Alfanous-team/alfanous/tree/master/src/alfanous>`_ .
    #. Compile AlfanousDesktop to a binary executable file:
        
       .. code-block:: bat
            
            cd ..\..\src\alfanous-desktop 
            python setup.py py2exe

    #. Install `NSIS compiler <http://nsis.sourceforge.net/Download>`_ .
    #. Check if the script `make_installer.nsi <https://github.com/Alfanous-team/alfanous/blob/master/dist/nsis/make_installer.nsi>`_ is up to date and includes the right files.

    #. Run the compilation of the installer using the nsis compiler.
    #. Test the installer built.
    #. For multiple uses, you can configure the bat script  `make_nsis_installer.win.bat <https://github.com/Alfanous-team/alfanous/blob/master/dist/nsis/make_nsis_installer.win.bat>`_ the command line. Update the variables VERSION, PYTHON, MAKENSIS before using it.

       .. code-block:: bat

            set VERSION="0.4.3"
            set PYTHON="C:\Python26\python.exe"
            set MAKENSIS="H:\developement\nsis\makensis.exe"
