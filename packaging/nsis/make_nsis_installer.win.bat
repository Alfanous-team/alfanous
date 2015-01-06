@echo off


set VERSION="0.7.03"
set PYTHON="C:\Python27\python.exe"
set MAKENSIS="C:\Program Files\NSIS\makensis.exe"
set ALFANOUSDESKTOP="..\..\src\alfanous-desktop"
set OUTPUTFOLDER="..\..\output"

rem building first
rem make build # it's easier to be done in linux
  
rem Compile AlfanousDesktop to a binary executable file
%PYTHON% %ALFANOUSDESKTOP%\setup.py py2exe

rem Build the installer
%MAKENSIS% make_installer.nsi


rem Copy the new generated installer to output folder
mkdir %OUTPUTFOLDER%\%VERSION%
move alfanousInstaller.exe %OUTPUTFOLDER%\%VERSION%\alfanousInstallerV%VERSION%.exe 
rmdir /s /q .\dist

echo "end."
pause
