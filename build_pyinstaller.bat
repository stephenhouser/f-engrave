rem ---------------------------------------------------------------------
rem This file executes the build command for the windows executable file.
rem It is here because I am lazy
rem ---------------------------------------------------------------------

rem set PATH=C:\Python26;%PATH%
rem python py2exe_setup.py py2exe
rem rmdir /S build

rem  --noconsole
rem --onefile
rem --clean
rem --noconsole

C:\Python37\Scripts\pyinstaller --noconsole --icon fengrave.ico  f-engrave.py

rem move dist\f-engrave.exe F-Engrave_Win64\.

rmdir /S /Q build
rmdir /S /Q __pycache__

rem rmdir /S /Q dist

