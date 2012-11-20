@echo off


set VERSION="0.4.3"
set PYTHON="C:\Python26\python.exe"
set MAKENSIS="H:\developement\nsis\makensis.exe"

cd ..\..\interfaces\desktop 
rem %PYTHON% setup.py py2exe

cd ..\..\dist\nsis
%MAKENSIS% make_installer.nsi

cd ..\..\
mkdir output
mkdir output\%VERSION%
move alfanousInstaller.exe output\%VERSION%\alfanousInstallerV%VERSION%.exe 
rmdir /s /q interfaces\desktop\dist 

echo "end."
pause
