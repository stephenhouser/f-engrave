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
PYINSTALLER=true
while getopts "hvdesp" OPTION; do
	case "$OPTION" in
		h)  echo "Options:"
			echo -e "\t-h Print help (this)"
			echo -e "\t-v Verbose output"
			echo -e "\t-e Keep Python virtual environment (don't delete)"
			echo -e "\t-p Use py2app to build instead of pyinstaller"
			echo -e "\t-s Setup dev environment"
			echo -e "\t-d Make disk image (.dmg)"
			exit 0
			;;
		v) 	VERBOSE=true
			;;
		d) 	MAKE_DISK=true
			;;
		e)  KEEP_VENV=true
			;;
		p)	PYINSTALLER=false
			;;
		s)  SETUP_ENVIRONMENT=true
			;;
		*)  echo "Incorrect option provided"
			exit 1
			;;
    esac
done

# Prints the provided error message and then exits with an error code
function fail {
    CODE="${1:-1}"
    MESSAGE="${2:-Unknown error}"
    echo ""
    echo -e "\033[31;1;4m*** ERROR: $MESSAGE ***\033[0m"
    echo ""
    exit $CODE
}


# Exits with error code/message if the previous command failed
function check_failure {
    CODE="$?"
    MESSAGE="$1"
    [[ $CODE == 0 ]] || fail "$CODE" "$MESSAGE" 
}

# *** Not Tested! ***
if [[ "$SETUP_ENVIRONMENT" == true ]]
then
	# Install HomeBrew (only if you don't have it)
	/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
	check_failure "Failed to install homebrew"

	# Install python environments...
	brew install pyenv
	check_failure "Failed to install pyenv"
	eval "$(pyenv init -)"
	check_failure "Failed to initialize pyenv"

	#PYTHON_CONFIGURE_OPTS="--enable-framework" pyenv install 3.7.2
	PYTHON_CONFIGURE_OPTS="--enable-shared" pyenv install 3.8.2
	check_failure "Failed to install pyenv"
	pyenv local 3.8.2
	pyenv rehash
	check_failure "Failed to set up pyenv"
	pip install --upgrade pip

	# Installs Python3 (which includes pip3) and freetype libraries (for ttf2cxf)
	brew install freetype
	check_failure "Failed to install freetype"
fi

echo "Validate environment..."

# Ensure that the user installed potrace
command -v potrace > /dev/null || fail 1 "Please install potrace via: brew install potrace"

# Get version from main source file.
VERSION=$(grep "^version " f-engrave.py | grep -Eo "[\.0-9]+")
[[ -z $VERSION ]] && fail 1 "Could not determine f-engrave version"

# Determine Python to use... prefer Python3
PYTHON=$(command -v python3)
if [[ -z $PYTHON ]]
then
	PYTHON=$(command -v python)
fi

PY_VER=$(${PYTHON} --version 2>&1)
[[ $PY_VER == *"3."* ]] || fail 1 "Packaging REQUIRES Python3"

PIP=$(command -v pip3)
if [[ -z $PIP ]]
then
	PIP=$(command -v pip)
fi

# Clean up any previous build work
echo "Remove old builds..."
rm -rf ./build ./dist *.pyc ./__pycache__

# Set up and activate virtual environment for dependencies
echo "Setup Python Virtual Environment..."
${PYTHON} -m venv python_venv
check_failure "Failed to initialize python venv"
source ./python_venv/bin/activate

# Install requirements
echo "Install Dependencies..."
${PIP} install -r requirements.txt
check_failure "Failed to install python requirements"

echo "Build macOS Application Bundle..."
# To compile TTF2CXF_STREAM need to have: 
#   - XQuartz (for freetype2)
#   - Xcode command line tools (for g++)
(cd TTF2CXF_STREAM; make osx)
check_failure "Failed to build TTF2CXF_STREAM"

if [[ "$PYINSTALLER" = true ]]
then
	# Make the bundle with PyInstaller
	${PYTHON} -OO -m PyInstaller -y --clean f-engrave.spec
	check_failure "Failed to package f-engrave bundle"

	# Remove temporary binary
	rm -rf dist/f-engrave
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
	/usr/bin/python setup.py py2app
	check_failure "Failed to setup py2app"

	# Py2app does not copy permissions (executable) when bundling resources.
	# This may actually not be the right place for the executable, but it works
	# for the moment, as long as we tweak the permissions when it's completed.
	# http://stackoverflow.com/questions/15815364/embedding-an-executable-within-a-py2app-application
	# http://stackoverflow.com/questions/11370012/can-executables-made-with-py2app-include-other-terminal-scripts-and-run-them/11371197#11371197
	chmod +x dist/f-engrave.app/Contents/Resources/ttf2cxf_stream
fi

echo "Copy support files to dist..."
cp -Rv README.md gpl-3.0.txt INSTALL.txt samples dist

# Clean up the build directory when we are done.
echo "Clean up build artifacts..."
rm -rf build

# Remove virtual environment
if [[ "$KEEP_VENV" == false ]]
then
	echo "Remove Python virtual environment..."
	deactivate
	rm -rf python_venv
fi

# Buid a new disk image
if [[ "$MAKE_DISK" = true ]]
then
	echo "Build macOS Disk Image..."
	if [[ "$PYINSTALLER" = true ]]
	then
		VOLNAME=F-Engrave-${VERSION}
	else 
		VOLNAME=F-Engrave-${VERSION}-py2app
	fi

	rm ${VOLNAME}.dmg
	hdiutil create -fs HFS+ -volname ${VOLNAME} -srcfolder ./dist ./${VOLNAME}.dmg
	check_failure "Failed to build f-engrave dmg"
fi

echo "Done."
