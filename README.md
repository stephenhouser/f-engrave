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

This version has been built with:

* Python v3.7.6
* potrace v1.16
* PyInstaller v3.4

## What's Different With this macOS version from Scorch's Code?

To make `f-engrave` look and work well on macOS there are a few minor changes 
to Scorch's code that I've done here. 

* Adds two new functions `ttf2cxf_stream()` and `potrace()` that locate their related executable files either in the *application bundle* or the local file system depending on the application bundle type. This allows these two binary files to be bundled within the macOS .app bundle.

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

* To align some of the user interface elements better on macOS systems. There are 
some small *number adjustments* sprinkled throughout the user interface creation
code. Check the `.patch` file if you want the gory details.

* `TTF2CXF_STREAM/Makefile` has a target added to compile it on macOS/darwin.

## Compiling and Updating Versions

There are two macOS build related scripts:

* `update_macOS.sh` - downloads, updates, and builds from new version of F-Engrave
* `build_macOS.sh` - builds the checked out F-Engrave to a macOS Application

To simply **build** the checked out version of `f-engrave`, in the repository 
directory run `build-macOS.sh`.  This will create a clickable OS X/macOS 
Application in the ./dist directory named `f-engrave.app` that can then be 
run or moved to your Applications folder.

To **update** the code to a new version of `f-engrave` from [http://www.scorchworks.com/Fengrave/fengrave.html][fengrave], which is my typical workflow. **NOTE** I do this on **OSX 10.10 Yosemite** machine to make sure the compiled application can run on versions >= 10.10. 

1. Get the latest source link from [http://www.scorchworks.com/Fengrave/fengrave.html][fengrave]
2. `brew update` and `brew upgrade` to make sure my Homebrew is as up-to-date as it can be on an old OS.
3. `./update-macOS.sh -u "SOURCE-LINK"`. This creates a `.dmg` image file tagged with the version number.
4. Check everything seems to work, launch from the disk image, check that fonts are loaded, then check `.bmp` loading of the JellyBean file (tests `potrace`).
5. Check source diffs, and move `macOS-VERSION.patch` to `macOS.patch`
6. `git commit -a -m"Update to version 1.XX"`
7. `git tag v1.XX`
8. `git push & git push --tags`
9. Create a release from the tag on GitHub and upload the `.dmg` file to it.   

The following process [Make mac binaries with pyinstaller that are backwards-compatible on Mac OS X](https://gist.github.com/phfaist/a5b8a895b003822df5397731f4673042) looks appealing to resolving having to have a 10.10 box kicking around.

## Compilation Dependencies

* `Xcode Command Line Tools` (for `g++`)
* `XQuartz` for `libfreetype2` install via homebrew)
* `potrace` for bitmap engraving, install via homebrew)
* `pillow` installed as part of build script in virtual Python environment
* `pyinstaller` installed as part of build script in virtual Python environment

The application builds and includes `ttf2cxf` (modified makefile for a macOS system with X11 in `/usr/X11`) to allow engraving of TrueType (`ttf`) fonts. This adds the requirement for `XQuartz` and it's provided library `libfreetype2` installed to compile.

This will bundle the currently installed `potrace` with the application if `potrace` is installed in the system path or in `/usr/local/bin` (e.g. Homebrew) then bitmap (`PBM`, `BMP`) files can be read and
utilized.

## macOS Package Development Notes

To create a new patch file, when needed, which should be rarely as this code 
is contained in the `update-macOS.sh` script and done automatically when we
run it in the normal update process.

```
diff -Naur f-engrave.py f-engrave-163.py > macOS.patch
diff -Naur TTF2CXF_STREAM/Makefile TTF2CXF_STREAM-163/Makefile >> macOS.patch
```

There's something funny with line feeds in that `.patch` file so be careful
if you edit it.

## PyInstaller Packaging Notes and the `.spec` file

In general the following `pyinstaller` command line sets up a good initial
`f-engrave.spec` file that `pyinstaller` can use to build the app bundle.

```bash
pyinstaller f-engrave.py --clean -y --windowed --onefile --add-binary='TTF2CXF_STREAM/ttf2cxf_stream:.' --add-binary='/usr/local/bin/potrace:.' --add-binary='/usr/local/lib/libpotrace*.dylib':.' --icon=fengrave.icns --osx-bundle-identifier='com.scorchworks.f-engrave'
``` 

This does not make a very nice looking application for macOS though! To do that 
we need to add entries to the macOS specific `Info.plist` file. These are added
to the `BUNDLE` section of the `.spec` file. 

NOTE: The **absolute paths to `potrace` and it's `.dylib`** might change over 
time! These are the installed locations on my development machine, which were 
installed with Homebrew. (This is a warning to my future self)

NOTE: that I update these in my build and update scripts, in particular the 
version number to match the version number pulled from `f-engrave.py`, so you
should be careful when updating things here.

```Python
info_plist={
    'NSPrincipleClass': 'NSApplication',
	'NSAppleScriptEnabled': False,
    'NSHighResolutionCapable': 'True',
	'CFBundleIdentifier': 'com.scorchworks.f-engrave',
	'CFBundleName': 'F-Engrave',
	'CFBundleDisplayName': 'F-Engrave',
	'CFBundleShortVersionString': '1.71'
}
```

Then we can build using one of the following command lines to build the app 
bundle.

```bash
pyinstaller -y --clean f-engrave.spec
# OR
python -OO -m PyInstaller -y --clean f-engrave.spec
```

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
