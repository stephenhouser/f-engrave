# macOS Distribution

## macOS 10.14 (Mojave)

Yes, there's some gratuitious flashing of windows on macOS.

That's to fix when [buttons are blank or apparently not there](https://stackoverflow.com/questions/52529403/button-text-of-tkinter-not-works-in-mojave)
What's happening is the code is slightly resizing the windows after they open.

## Some of the files...

* `build_macOS.sh` - builds the checked out F-Engrave to a macOS Application
* `update_macOS.sh` - downloads, updates, and builds from new version of F-Engrave

## Code Signing (not done)

https://github.com/pyinstaller/pyinstaller/wiki/Recipe-OSX-Code-Signing