rem ---------------------------------------------------------------------
rem This file executes the build command for the windows executable file.
rem It is here because I am lazy
rem ---------------------------------------------------------------------

set PATH=C:\Python25;%PATH%
python py2exe_setup.py py2exe
rmdir /S build

