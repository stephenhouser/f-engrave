#!/bin/bash
# ---------------------------------------------------------------------
# This file executes the build command for the OS X Application bundle.
# It is here because I am lazy
# ---------------------------------------------------------------------
(cd TTF2CXF_STREAM; make osx)
python setup.py py2app
rm -rf build
