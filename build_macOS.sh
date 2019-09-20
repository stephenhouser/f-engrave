#!/bin/bash
# ---------------------------------------------------------------------
# This file executes the build command for the OS X Application bundle.
# It is here because I am lazy
# ---------------------------------------------------------------------

# Call getopt to validate the provided input. 
VERBOSE=false
MAKE_DISK=false
KEEP_VENV=false
INSTALL_TOOLS=false
PYINSTALLER=true
while getopts "hvdesp" OPTION; do
	case "$OPTION" in
		h)  echo "Options:"
			echo "\t-h Print help (this)"
			echo "\t-v Verbose output"
			echo "\t-e Keep Python virtual environment (don't delete)"
			echo "\t-s Install development tools"
			echo "\t-p Use pyinstaller to build application bundle (default)"
			echo "\t-P Use py2app to build application bundle"
			echo "\t-d Make disk image (.dmg)"
			exit 0
			;;
		v) 	VERBOSE=true
			;;
		d) 	MAKE_DISK=true
			;;
		e)  KEEP_VENV=true
			;;
		s)  INSTALL_TOOLS=true
			;;
		p)  PYINSTALLER=true
			;;
		P)  PYINSTALLER=false
			;;
		*)  echo "Incorrect option provided"
			exit 1
			;;
    esac
done

# *** Not Tested! ***
if [ "$INSTALL_TOOLS" = true ]
then
	# Install HomeBrew (only if you don't have it)
	/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

	
	if [ "$PYINSTALLER" = true ]
	then
		# Installs Python3 (which includes pip3) and freetype libraries (for ttf2cxf)
		brew install python freetype potrace
	else
		# Install newer python environments...
		# brew install pyenv
		# eval "$(pyenv init -)"
		
		# # Install Python 3.7.4 with pyenv and set it as the default Python
		# # Need to enable framework when installing for bundled app to work properly.
		# PYTHON_CONFIGURE_OPTS="--enable-framework" pyenv install 3.7.4
		# pyenv global 3.7.4
		# pyenv rehash

		brew install freetype potrace
		easy_install pip
	fi
fi

echo "Setup build environment..."
if [ "$PYINSTALLER" = true ]
then
	echo "Using pyinstaller to build application bundle."

	echo "Your system is: "
	sw_vers
	echo -e "\033[1;31m"
	echo "  This build _may not work_ on older versions of macOS/OS X."
	echo -e "\033[0m"

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
else
	# Use System Installed Python and py2app
	echo "Using py2app to build application bundle."

	# Precheck for 'restricted' permissions on system Python when using py2app.
	# Build will fail if this is set
	if ls -dlO /System/Library/Frameworks/Python.framework | grep 'restricted'> /dev/null
	then
		echo -e "\033[1;31m"
		echo "  *** *** *** *** *** *** *** *** *** *** *** *** ***"
		echo ""
		echo "  Your system Python has the 'restricted' flag set."
		echo ""
		echo "  This causes application packaging to fail."
		echo "  Please read README.md and/or this build.sh script"
		echo "  for details on how to resolve this problem."
		echo ""
		echo "  *** *** *** *** *** *** *** *** *** *** *** *** ***"
		echo -e "\033[0m"
		exit 1
	fi

	PYTHON=/usr/bin/python
fi

# Clean up any previous build work
echo "Remove old builds..."
rm -rf ./build ./dist *.pyc ./__pycache__

echo "Build macOS Application Bundle..."
# To compile TTF2CXF_STREAM need to have: 
#   - XQuartz (for freetype2)
#   - Xcode command line tools (for g++)
(cd TTF2CXF_STREAM; make osx)

if [ "$PYINSTALLER" = true ]
then
	# Make the bundle with PyInstaller
	${PYTHON} -OO -m PyInstaller --log-level=ERROR -y --clean f-engrave.spec
else 
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
	${PYTHON} setup.py py2app

	# Py2app does not copy permissions (executable) when bundling resources.
	# This may actually not be the right place for the executable, but it works
	# for the moment, as long as we tweak the permissions when it's completed.
	# http://stackoverflow.com/questions/15815364/embedding-an-executable-within-a-py2app-application
	# http://stackoverflow.com/questions/11370012/can-executables-made-with-py2app-include-other-terminal-scripts-and-run-them/11371197#11371197
	chmod +x dist/f-engrave.app/Contents/Resources/ttf2cxf_stream
fi

echo "Copy support files to dist..."
cp -rv README.md gpl-3.0.txt INSTALL.txt samples dist

# Clean up the build directory when we are done.
echo "Clean up build artifacts..."
# Remove temporary binary
if [ -d dist/f-engrave ]
then
	rm -rf dist/f-engrave
fi

# Clean up any previous build work
echo "Remove build intermediates..."
rm -rf ./build *.pyc ./__pycache__

if [ "$PYINSTALLER" = true ]
then
	# Remove virtual environment
	if [ "$KEEP_VENV" = false ]
	then
		echo "Remove Python virtual environment..."
		deactivate
		rm -rf python_venv
	fi
fi

# Buid a new disk image
if [ "$MAKE_DISK" = true ]
then
	echo "Build macOS Disk Image..."
	# Get version from main source file.
	VERSION=$(grep "^version " f-engrave.py | grep -Eo "[\.0-9]+")
	if [ "$PYINSTALLER" = true ]
	then
		VERSION=$VERSION-pyinstaller
	fi

	rm ./F-Engrave-${VERSION}.dmg
	hdiutil create -fs HFS+ -volname F-Engrave-${VERSION} -srcfolder ./dist ./F-Engrave-${VERSION}.dmg
fi

echo "Done."
