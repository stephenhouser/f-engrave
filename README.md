# F-Engrave
Packaging of Scorchworks F-Engrave as an OSX Application

F-Engrave generates 'GCODE' for Computer Numerical Control (CNC) systems from
text and bitmaps. It "Suppoprts Engraving and V-Carving, Uses CXF and TTF fonts,
Imports DXF and Bitmap images".

The official F-Engrave and instructions are at Scorchworks:

>    http://www.scorchworks.com/Fengrave/fengrave.html

This fork is merely to add packaging for OSX systems, creating a clickable
'Applicaion' that can be installed on any OSX system. This eliminates having
to run F-Engrave from a Terminal prompt.

## Compiling

In the OSX directory, run `make`. This will create a clickable OSX Application
named `F-Engrave.app` that can then be distributed or moved to your Applications
folder.

## Additional Programs

Includes `ttf2cxf` modified makefile for OS X with X11 in `/usr/X11` to
allow engraving of TrueType (`ttf`) fonts.

Does not include `potrace`. If `potrace` is installed in the system path or 
in `/usr/local/bin` (e.g. Homebrew) then bitmap (`PBM`) files can be read and
utilized.
