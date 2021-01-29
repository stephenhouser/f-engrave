#!/bin/bash
# ---------------------------------------------------------------------
# This file executes the build command for the OS X Application bundle.
# It is here because I am lazy
# ---------------------------------------------------------------------

# Make sure we're in the same folder as this file
cd -P -- $(dirname -- "$0")/

# Set this to the version of python we want to use (via pyenv)
PYTHON_VERSION=3.9.1

# Call getopt to validate the provided input. 
VENV_DIR=build_env.$$
VERBOSE=false
MAKE_DISK=false
KEEP_VENV=false
SETUP_ENVIRONMENT=false
while getopts "hvdesp" OPTION; do
	case "$OPTION" in
		h)  echo "Options:"
			echo -e "\t-h Print help (this)"
			echo -e "\t-v Verbose output"
			echo -e "\t-e Keep Python virtual environment (don't delete)"
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

	# Installs Python3 (which includes pip3) and freetype libraries (for ttf2cxf)
	brew install --build-from-source freetype potrace tcl-tk
	check_failure "Failed to install freetype and potrace"

	# Install python environments...
	brew install --build-from-source pyenv
	check_failure "Failed to install pyenv"
	eval "$(pyenv init -)"

	# Install Python with pyenv and set it as the default Python
	PATH="/usr/local/opt/tcl-tk/bin:$PATH" \
		LDFLAGS="-L/usr/local/opt/tcl-tk/lib" \
		CPPFLAGS="-I/usr/local/opt/tcl-tk/include" \
		PKG_CONFIG_PATH="/usr/local/opt/tcl-tk/lib/pkgconfig" \
		PYTHON_CONFIGURE_OPTS="--with-tcltk-includes='-I$(brew --prefix tcl-tk)/include' --with-tcltk-libs='-L$(brew --prefix tcl-tk)/lib -ltcl8.6 -ltk8.6'" \
		pyenv install ${PYENV_PYTHON_VERSION}
	check_failure "Failed to install Python ${PYTHON_VERSION}"

	# Select Python to use
	pyenv local ${PYTHON_VERSION} && pyenv rehash
	check_failure "Failed to setup Python ${PYTHON_VERSION}"
fi

echo "Validate environment..."
OS=$(uname)
if [ "${OS}" != "Darwin" ]; then
	fail "Um... this build script is for OSX/macOS."
fi

# Ensure that the user installed external dependencies
command -v freetype-config > /dev/null || fail 1 "Please rerun with -s to setup build environment"
command -v potrace         > /dev/null || fail 1 "Please rerun with -s to setup build environment"

# Use the specific python version from pyenv so we don't get hung up on the
# system python or a user's own custom environment.
PYTHON=$(command -v python3)
PY_VER=$($PYTHON --version 2>&1 | awk '{ print $2 }')
[[ ${PY_VER} == "${PYTHON_VERSION}" ]] || fail 1 "Packaging REQUIRES Python ${PYTHON_VERSION}. Please rerun with -s to setup build environment"

# Clean up any previous build work
echo "Remove old builds..."
rm -rf ./build ./dist *.pyc ./__pycache__

# Set up and activate virtual environment for dependencies
echo "Setup Python Virtual Environment..."
python3 -m venv "${VENV_DIR}"
check_failure "Failed to initialize python venv"

source "./${VENV_DIR}/bin/activate"
check_failure "Failed to activate python venv"

# Unset our python variable now that we are running inside of the virtualenv
# and can just use `python` directly
PYTHON=

# Install requirements
echo "Install Dependencies..."
pip3 install -r requirements.txt
check_failure "Failed to install python requirements"

echo "Build macOS Application Bundle..."

# Get version from main source file.
VERSION=$(grep "^version " f-engrave.py | grep -Eo "[\.0-9]+")
[[ -z $VERSION ]] && fail 1 "Could not determine f-engrave version"

# To compile TTF2CXF_STREAM need to have: 
#   - XQuartz (for freetype2)
#   - Xcode command line tools (for g++)
(cd TTF2CXF_STREAM; make osx)
check_failure "Failed to build TTF2CXF_STREAM"

echo "Packaging f-engrave bundle for MacOS"
# Make the bundle with PyInstaller
python3 -OO -m PyInstaller -y --clean f-engrave.spec
check_failure "Failed to package f-engrave bundle"

# Remove temporary binary
rm -rf dist/f-engrave

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
	rm -rf "${VENV_DIR}"
fi

# Buid a new disk image
if [[ "$MAKE_DISK" = true ]]
then
	echo "Build macOS Disk Image..."
	VOLNAME=F-Engrave-${VERSION}
	rm ${VOLNAME}.dmg
	hdiutil create -fs HFS+ -volname ${VOLNAME} -srcfolder ./dist ./${VOLNAME}.dmg
	check_failure "Failed to build f-engrave dmg"
fi

echo "Done."
