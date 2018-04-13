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

In the main directory run `build.sh`.  This will create a clickable OSX Application
named `f-engrave.app` that can then be distributed or moved to your Applications folder.

There are a few complications with compilation that are addressed in the `build.sh` script. 
I've been able to compile everything on a freshly installed macOS 10.11.6 system after 
installing the dependencies listed below.

Specifically:

* There are dependencies (see below)
* `py2app` needs to be run with system restrictions changed (see `build.sh`)
* `py2app` does not copy file permissions for resources (see `build.sh`)

## Dependencies

* `Xcode Command Line Tools` (for `g++`)
* `XQuartz` (for `libfreetype2`)

Includes `ttf2cxf` modified makefile for OS X with X11 in `/usr/X11` to
allow engraving of TrueType (`ttf`) fonts. This adds the requirement for
`XQuartz` and it's provided library `libfreetype2` installed to compile.

Does not include `potrace`. If `potrace` is installed in the system path or 
in `/usr/local/bin` (e.g. Homebrew) then bitmap (`PBM`) files can be read and
utilized.

## Updating to New Versions

To make `f-engrave` work well on macOS there are a few minor changes to the
Python source code. The `macOS-update.sh` script is an attempt to automate
the process of appying macOS specific patches. It uses a `.patch` file to do
most of the hard work of merging the macOS specific things (below) with the
base code.

It does the following (or at least tries to):

* Add `/usr/local/bin` to the environment path. I was uanble to do this
properly with the application package creation process (`setup.py`), so this is
a little bit of a hack. Add the followling line:

```
+  os.environ["PATH"] += os.pathsep + "." + os.pathsep + "/usr/local/bin"
```

* To get the font files from subdirectories loaded on macOS, I added a little
hack to walk the font directory looking for likely font files:

```
-            font_files=os.listdir(self.fontdir.get())
-            font_files.sort()
+            font_files = []
+            import fnmatch
+            for r, dirnames, filenames in os.walk(self.fontdir.get()):
+                for filename in fnmatch.filter(filenames, '*.[Cc][Xx][Ff]'):
+                    font_files.append(os.path.join(r.replace(self.fontdir.get(), ""), filename))
+                for filename in fnmatch.filter(filenames, '*.[Tt][Tt][Ff]'):
+                    font_files.append(os.path.join(r.replace(self.fontdir.get(), ""), filename))
+                font_files.sort()
```

* I also made several small adjustments to user interface elements. These are
to align them better on macOS systems. These are sprinkled throughout the user
interface creation code. Check the `.patch` file if you want the gory details.

* `TTF2CXF_STREAM/Makefile` has a target added to compile it on macOS. It's
at the end.

## macOS Package Development Notes

To create a new patch file, when needed, which should be rarely:

```
diff -Naur f-engrave.py f-engrave-163.py > macOS.patch
diff -Naur TTF2CXF_STREAM/Makefile TTF2CXF_STREAM-163/Makefile >> macOS.patch
```

There's something funny with line feeds in that `.patch` file so be careful
if you edit it.

- - -
The following is from [Scorchworks F-Engrave Site][fengrave]:

## Background
F-Engrave is a text to g-code program that is written in python and is based on the text engraving software ([engrave-11](http://wiki.linuxcnc.org/cgi-bin/wiki.pl?Simple_LinuxCNC_G-Code_Generators#Text_Engraving_Software)) available in the [LinuxCNCKnowledgeBase](http://wiki.linuxcnc.org/cgi-bin/wiki.pl?LinuxCNCKnowledgeBase). The name F-Engrave is simply the predecessor programs name "engrave" with an "F" slapped on to indicate that the program can perform more formating functions like justification (left, right and center) and text on a circle. When I first released the program I had no idea I was going to add v-carving or DXF features so the name does not reflect any of those features. F-Engrave is a free open source program released under the [GNU General Public License (GPL) Version 3](http://www.gnu.org/licenses/). There is not much left of the original engrave-11 script but I needed a jumping off point. One of the things that remained intact for the most part is the CXF font reading. (although I tweaked it to accept a second variation of the CXF font format.)

## F-Engrave Features

- V-carve for outline fonts and images (images and fonts should be composed of closed section loops when v-carving) 
- Imports DXF files 
- Imports PBM images (with potrace helper program) 
- Uses TTF font files (with the help of ttf2cxf_stream, not all formats are supported) 
- Capable of exporting Scalable Vector Graphics (SVG) file 
- Opens previously saved G-Code file and retrieve the settings and text 
- Supports multiple lines of text with justification (Left, Right and Centered) 
- Mirroring text (vertical) and flipping text (horizontal) 
- Create text that follows an arc 
- Origin selection allows user to select the location of g-code zero position 
- Display line thickness to be used during engraving allows visualization of end result 
- Use inches or mm as export units 
- Customizable G-Code preamble and postamble 
- Usable as an LinuxCNC Axis filter program (open the f-engrave.py file from within LinuxCNC Axis File-Open-f-engrave.py. when you are finished with your text select File-Write To Axis and Exit, This option only existed when executed from within Axis)

Please see the official [Scorchworks F-Engrave website][fengrave] for the full details.

  [fengrave]: http://www.scorchworks.com/Fengrave/fengrave.html
