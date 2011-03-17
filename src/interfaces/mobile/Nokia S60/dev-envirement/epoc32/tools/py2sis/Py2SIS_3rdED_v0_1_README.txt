=====================================================
Py2SIS v0.2 for Python for S60 3rd Edition, 24.9.2007
=====================================================

This is a pre-release of Py2SIS for Python for S60, 3rd Edition. This tool has 
not been tested extensively, and it might cause problems in your device or SDK.

The tool can be used to package Python scripts to standalone applications on the 
desktop side. The packaged Python applications are no different from native 
applications to a handset user.

For an overview of how the Symbian platform security enhancements affect PyS60 
and Py2SIS (e.g. what are the options for signing), please see 
'PyS60_3rdEd_README.txt'.

For more information about tool usage, please take a look at "Programming with 
Python for Series 60 Platform", Section 14: "Making Stand-Alone Applications 
from Python Scripts".

Prerequisites
-------------

 * A working version of S60 3rdEd C++ SDK installed. The installed SDK should 
 compile e.g. "helloworldbasic" example program.

 * Py2SIS also currently requires that the SDK configuration is subst'ed, this 
 means that e.g:

    C:\>subst
    S:\: => C:\Symbian\7.0s\Series60_v20
    T:\: => C:\Symbian\8.1a\S60_2nd_FP3
    U:\: => C:\Symbian\8.0a\S60_2nd_FP2
    V:\: => C:\Symbian\9.1\S60_3rd

 Py2SIS has to exist on the same subst'ed drive as your 3rdEd SDK, in the above 
 case the correct drive is 'V:'.
 
 * A working version of Python is also needed (tested with Python 2.4.2).

 * PyS60 installed on a phone.

Usage
-----

Invoke e.g. with ("snake.py" is the script we are packaging):

    V:\cc\python\vob001\src\py2sis>python py2sis.py snake.py --uid=0x01234567 
    --sdk30 --caps="NetworkServices LocalServices ReadUserData WriteUserData 
    Location" --leavetemp
    
Following is outputted:
    
    Creating SIS for SDK3.0 and later
    Processing template V:\cc\python\vob001\src\py2sis\build\app.mmp.in
    Processing template V:\cc\python\vob001\src\py2sis\build\Icons_aif.mk.in
    Processing template V:\cc\python\vob001\src\py2sis\build\PyTest.cpp.in
    Processing template V:\cc\python\vob001\src\py2sis\build\PyTest.rss.in
    Processing template V:\cc\python\vob001\src\py2sis\build\PyTest_reg.rss.in
    Compiling...
    Done.
    makesis V:\cc\python\vob001\src\py2sis\temp\snake.pkg V:\cc\python\vob001\src\py
    2sis\snake.sis
    Processing V:\cc\python\vob001\src\py2sis\temp\snake.pkg...
    Unique vendor name not found.

    Created V:\cc\python\vob001\src\py2sis\snake.sis
    
    Note: Sign the created SIS file prior installation (tool "SignSIS")

Here is the output without arguments:

  Y:\src\py2sis>python py2sis.py
  
  Python to SIS
  usage: py2sis.py <src> [sisfile] [--uid=0x01234567] [--appname=myapp] [--caps="c
  ap_1 cap_2 ..."] [--presdk20] [--sdk30] [--armv5] [--leavetemp] [--autostart]
  
         src       - Source script or directory
         sisfile   - Path of the created SIS file
         uid       - Symbian UID for the application
         appname   - Name of the application
         caps      - A list of capabilities ("NONE", if caps is not given)
         presdk20  - Use a format suitable for pre-SDK2.0 phones
         sdk30     - Use a format suitable for SDK3.0 phones
         leavetemp - Leave temporary files in place
         armv5     - Generate armv5 binaries, by default gcce binaries are created. Only in SDK3.0
         autostart - Start the application during the device bootstrap (SDK3.0 only)
  
  By default, py2sis outputs SIS packages suitable for S60 2.X handsets.
  
  Packages for SDK3.0 phones are unsigned (use "SignSIS" for signing).

  Y:\src\py2sis>
    
For signing the created packages use "SignSIS", example invocation:

    V:\cc\python\vob001\src\py2sis>signsis snake.sis snake.sis v:\keys\rd.cer v:\key
    s\rd-key.pem


Other information
-----------------

 * The tool is not very verbose at the moment, if you run into problems, please 
 verify first that your SDK is working correctly (a proper test is to compile 
 "helloworldbasic") and to use the "--leavetemp"-switch with Py2SIS invocation. 
 After this you can investigate the contents of "temp" folder (especially ".pkg" 
 file and relations to the whole file tree under "temp")

 * The above is also useful if you want to investigate the internals of Py2SIS, 
 e.g. UID is added as postfix to file names due to flat file structure in 
 certain locations in S60 devices.

 * You can change the contents of the "\templates_eka2\python_star.svg"-file if 
 you want to use some other logo than the default one (currently the star and 
 the snake)

  * Invoke py2sis with argument --autostart to enable the start-up of your 
  script during device boot. Please note that self-signing is not enough for a 
  start on boot package - In this case the package created with py2sis requires 
  e.g. developer certificate signing.


Questions, feedback and defects
-------------------------------

For all questions and feedback, related to py2sis or PyS60, please use the Forum 
Nokia discussion board:

http://discussion.forum.nokia.com/forum/forumdisplay.php?f=102

For defect reports, please use the defect tracking at:

http://sourceforge.net/tracker/?atid=790646&group_id=154155&func=browse


Copyright (c) 2006 Nokia Corporation. All rights reserved. Nokia and Nokia 
Connecting People are registered trademarks of Nokia Corporation.
