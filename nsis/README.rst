NSIS installer script
=====================
This script is used to make automatically  the installer of `AlfanousDesktop <https://github.com/Alfanous-team/alfanous/tree/master/src/alfanous-desktop>`_ for windows.

What is NSIS?
    NSIS (Nullsoft Scriptable Install System) is a professional open source system to create Windows installers. It is designed to be as small and flexible as possible and is therefore very suitable for internet distribution. 

How to run the script successfully?
    #. Have a windows OS either XP, Vista or Seven.
    #. Install the python libraries using easy_install: `py2exe <http://www.py2exe.org/>`_ ,  `setuptools <http://pypi.python.org/pypi/setuptools#files>`_ , and all requirments of AlfanousDesktop: 
        PySide, 
		Jinja2,
       `pyparsing <http://pyparsing.wikispaces.com/>`_, 
       `configobj <http://www.voidspace.org.uk/python/configobj.html>`_, 
       `alfanous API <https://github.com/Alfanous-team/alfanous/tree/master/src/alfanous>`_ (build resources then install the API) .
    #. py2exe needs this dll: msvcp90.dll ,so if you havn't installed already Microsoft Visual C++ 2008, get instead the `redisributable package <http://www.microsoft.com/en-us/download/details.aspx?displaylang=en&id=29>`_ then extract it. Move the *nosxs_msvcp90.dll* to Python's DLL folder and rename it to *msvcp90.dll*. 
    #. Compile AlfanousDesktop to a binary executable file:
        
       .. code-block:: bat
            
            cd ..\..\src\alfanous-desktop 
            python setup.py py2exe
       
       

    #. Install `NSIS compiler <http://nsis.sourceforge.net/Download>`_ .
    #. Check if the script `make_installer.nsi <https://github.com/Alfanous-team/alfanous/blob/master/dist/nsis/make_installer.nsi>`_ is up to date and includes the right files.

    #. Run the compiling of the installer using the nsis compiler.
    #. Test the installer building.
    #. For multiple uses, run the batch script  **make_nsis_installer.win.bat**. Update the variables VERSION, PYTHON, MAKENSIS before using it.

       .. code-block:: bat

            set VERSION="0.7"
            set PYTHON="C:\Python27\python.exe"
            set MAKENSIS="C:\Programmes\NSIS\makensis.exe"
