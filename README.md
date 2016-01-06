# f-engrave
Modifications and Packaging of Scorchworks F-Engrave to work on OSX.

Original F-Engrave and instructions are at Scorchworks:

>    http://www.scorchworks.com/Fengrave/fengrave.html

In the OSX directory, run `make`. This will create a clickable OSX Application
named `F-Engrave.app` that can then be distributed or moved to your Applications
folder.

Includes `ttf2cxf` modified makefile for OS X with X11 in `/usr/X11` to
allow engraving of TrueType (`ttf`) fonts.

Does not include `potrace`. If `potrace` is installed in the system path or 
in `/usr/local/bin` (e.g. Homebrew) then bitmap (`PBM`) files can be read and
utilized.
