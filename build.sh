#!/bin/bash
# ---------------------------------------------------------------------
# This file executes the build command for the OS X Application bundle.
# It is here because I am lazy
# ---------------------------------------------------------------------

# Clean up any previous build work
rm -rf ./build ./dist

# To compile TTF2CXF_STREAM need to have: 
#   - XQuartz (for freetype2)
#   - Xcode command line tools (for g++)
(cd TTF2CXF_STREAM; make osx)

# Use system (OSX) python and py2app. Do use not homebrew or another version. 
# This ensures things will work on other people's computers who might not
# have great tools like homebrew installed.
#
# There's a permission problem since 10.10 with the default system py2app:
# http://stackoverflow.com/questions/33197412/py2app-operation-not-permitted
# https://forums.developer.apple.com/thread/6987
#
# Solution:
#   - Boot in recovery mode
#   - csrutil disable
#   - Reboot
#   - sudo chflags -R norestricted /System/Library/Frameworks/Python.framework
#   - Reboot into recovery mode
#   - csrutil enable
#   - Reboot and build...
# You need to do that before this will work!
/usr/bin/python setup.py py2app

# Py2app does not copy permissions (executable) when bundling resources.
# This may actually not be the right place for the executable, but it works
# for the moment, as long as we tweak the permissions when it's completed.
# http://stackoverflow.com/questions/15815364/embedding-an-executable-within-a-py2app-application
# http://stackoverflow.com/questions/11370012/can-executables-made-with-py2app-include-other-terminal-scripts-and-run-them/11371197#11371197
chmod +x dist/f-engrave.app/Contents/Resources/ttf2cxf_stream

# Clean up the build directory when we are done.
rm -rf build
