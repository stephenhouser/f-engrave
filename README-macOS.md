# macOS Specific Changes and Updates

* `build_macOS.sh` - builds the checked out F-Engrave to a macOS Application
* `update_macOS.sh` - downloads, updates, and builds from new version of F-Engrave

My typical workflow is, on an **OSX 10.10 Yosemite** (to maintain backward compatibility) machine:

    1. Get the latest source link from [http://www.scorchworks.com/Fengrave/fengrave.html][Scorchworks]
    2. `brew update` and `brew upgrade` to make sure my Homebrew is as up-to-date as it can be on an old OS.
    3. `./update-macOS.sh -u "SOURCE-LINK"`. This creates a `.dmg` image file tagged with the version number.
    4. Check everything seems to work, launch from the disk image, check that fonts are loaded, then check `.bmp` loading of the JellyBean file (tests `potrace`).
    5. Check source diffs, and move `macOS-VERSION.patch` to `macOS.patch`
    6. `git commit -a -m"Update to version 1.XX"`
    7. `git tag v1.XX`
    8. `git push & git push --tags`
    9. Create a release from the tag on GitHub and upload the `.dmg` file to it.   


## Using PyInstaller

In general the following `pyinstaller` command line sets up the initial `f-engrave.spec` file.

```bash
pyinstaller f-engrave.py --clean -y --windowed --onefile --add-binary='TTF2CXF_STREAM/ttf2cxf_stream:.' --add-binary='/usr/local/bin/potrace:.' --icon=fengrave.icns --osx-bundle-identifier='com.scorchworks.f-engrave'
``` 

To add entries to the macOS specific `Info.plist` we need to patch in the following in the `BUNDLE` section of the file. NOTE: that I update these in my build and update scripts, in particular the version number to match the version number pulled from `f-engrave.py`.

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

Then we can build using one of the following command lines:

```bash
pyinstaller -y --clean f-engrave.spec
# OR
python -OO -m PyInstaller -y --clean f-engrave.spec
```