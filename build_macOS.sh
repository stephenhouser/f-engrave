#!/bin/bash
# ---------------------------------------------------------------------
# This file executes the build command for the OS X Application bundle.
# It is here because I am lazy
# ---------------------------------------------------------------------

# Call getopt to validate the provided input. 
VERBOSE=false
MAKE_DISK=false
KEEP_VENV=false
SETUP_ENVIRONMENT=false
while getopts "hvdes" OPTION; do
	case "$OPTION" in
		h)  echo "Options:"
			echo "\t-h Print help (this)"
			echo "\t-v Verbose output"
			echo "\t-e Keep Python virtual environment (don't delete)"
			echo "\t-s Setup dev environment"
			echo "\t-d Make disk image (.dmg)"
			exit 0
			;;
		v) 	VERBOSE=true
			;;
		d) 	MAKE_DISK=true
			;;
		e)  KEEP_VENV=true
			;;
		s)  SETUP_ENVIRONMENT=true
			;;
		*)  echo "Incorrect option provided"
			exit 1
			;;
    esac
done

# *** Not Tested! ***
if [ "$SETUP_ENVIRONMENT" = true ]
then
	# Install HomeBrew (only if you don't have it)
	/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

	# Install python environments...
	# brew install pyenv
	# eval "$(pyenv init -)"

	# # Install Python 3.7.2 with pyenv and set it as the default Python
	# PYTHON_CONFIGURE_OPTS="--enable-framework" pyenv install 3.7.2
	# pyenv global 3.7.2
	# pyenv rehash

	# Installs Python3 (which includes pip3)
	brew install python
	pip3 install pyinstaller
fi

echo "Validate environment..."

# Get version from main source file.
VERSION=$(grep "^version " f-engrave.py | grep -Eo "[\.0-9]+")

# Determine Python to use... prefer Python3
PYTHON=$(command -v python3)
if [ -z "${PYTHON}" ]
then
	PYTHON=$(command -v python)
fi

PIP=$(command -v pip3)
if [ -z "${PIP}" ]
then
	PIP=$(command -v pip)
fi

# Clean up any previous build work
echo "Remove old builds..."
rm -rf ./build ./dist *.pyc ./__pycache__

# Set up and activate virtual environment for dependencies
echo "Setup Python Virtual Environment..."
PY_VER=$(${PYTHON} --version 2>&1)
if [[ $PY_VER == *"2.7"* ]]
then
	${PIP} install virtualenv py2app==0.16
	virtualenv python_venv
else
	${PYTHON} -m venv python_venv
fi

source ./python_venv/bin/activate

# Install requirements
echo "Install Dependencies..."
${PIP} install -r requirements.txt

echo "Build macOS Application Bundle..."
# To compile TTF2CXF_STREAM need to have: 
#   - XQuartz (for freetype2)
#   - Xcode command line tools (for g++)
(cd TTF2CXF_STREAM; make osx)

# Make the bundle with PyInstaller
${PYTHON} -OO -m PyInstaller --log-level=INFO -y --clean f-engrave.spec

# Remove temporary binary
#rm dist/f-engrave

echo "Copy support files to dist..."
# Copy in the ttf2cxf_stream binary. I can't seem to get PyInstaller to do this
#cp TTF2CXF_STREAM/ttf2cxf_stream dist/f-engrave.app/Contents/Resources/ttf2cxf_stream
#chmod +x dist/f-engrave.app/Contents/Resources/ttf2cxf_stream

# Other support files for disk image
cp README.md gpl-3.0.txt INSTALL.txt dist

# Clean up the build directory when we are done.
echo "Clean up build artifacts..."
#rm -rf build

# Remove virtual environment
if [ "$KEEP_VENV" = false ]
then
	echo "Remove Python virtual environment..."
	deactivate
	rm -rf python_venv
fi

# Buid a new disk image
if [ "$MAKE_DISK" = true ]
then
	echo "Build macOS Disk Image..."
	rm ./F-Engrave-${VERSION}.dmg
	hdiutil create -fs HFS+ -volname F-Engrave-${VERSION} -srcfolder ./dist ./F-Engrave-${VERSION}.dmg
fi

echo "Done."
