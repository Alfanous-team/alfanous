@echo off

cd ..\..\interfaces\desktop
python setup.py py2exe

cd ..\..\
rem makensis nsis_installer...

move alfanousInstaller.exe output\
rmdir /s /q interfaces\desktop\dist 