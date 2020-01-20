#!/bin/bash
#
# Script to copy changed files from Scorch's updated F-Engrave
# to staging directory for creating macOS package.
#
# 1. Copy over new files from directory specified on command line
# 2. Apply macOS patches from `macOS.patch` and update version numbers
# 3. Run the build script
# 4. Create a disk image (.dmg) for release
#
MD5="md5 -q"
files="INSTALL.txt build.bat fengrave.ico gpl-3.0.txt py2exe_setup.py \
		TTF2CXF_STREAM/INSTALL.txt TTF2CXF_STREAM/Makefile \
		TTF2CXF_STREAM/gpl-2.0.txt TTF2CXF_STREAM/ttf2cxf_stream.cpp"

CLEAN_SOURCE=false
while getopts "hvf:u:d:" OPTION; do
	case "$OPTION" in
		h)  echo "Update F-Engrave and build macOS Application"
			echo "update_macOS.sh [-hv]  [-d <dir>] | [-f <zipfile>] | [-u <url>] | [<url>]"
			echo "	-h Print help (this)"
			echo "	-v Verbose output"
			echo "  -c Clean up (delete) new sources (ON when downloading from URL)"
			echo "	-d <dir> Use existing source directory"
			echo "	-f <file> Use existing .zip file"
			echo "	-u <url> Download archive from URL"
			exit 1
			;;
		v) 	VERBOSE=true
			;;
		c)  CLEAN_SOURCE=true
			;;
		d) 	UPDATE_DIR=${OPTARG}
			unset SOURCE_ZIP
			unset URL
			;;
		f) 	SOURCE_ZIP=${OPTARG}
			unset UPDATE_DIR
			unset URL
			;;
		u) 	URL=${OPTARG}
			unset SOURCE_ZIP
			unset UPDATE_DIR
			;;
		*)  echo "Incorrect option provided $1"
			exit 1
			;;
    esac
done

if [ -z ${URL+x} ] && [ -z ${SOURCE_ZIP+x} ] && [ -z ${UPDATE_DIR+x} ]
then
	URL=$1
fi

# http://www.scorchworks.com/K40whisperer/K40_Whisperer-0.29_src.zip
if [ ! -z ${URL+x} ]
then
	echo "Download F-Engrave source archive..."
	CLEAN_SOURCE=true
	SOURCE_ZIP=$(echo $URL | rev | cut -f1 -d/ | rev)
	curl -o $SOURCE_ZIP $URL
	if [ ! -f $SOURCE_ZIP ]
	then
		echo "Download failed."
		exit 1
	fi
fi

if [ -f "$SOURCE_ZIP" ]
then
	echo "Extract F-Engrave  source files..."
	unzip -oq $SOURCE_ZIP
	UPDATE_DIR=$(basename $SOURCE_ZIP .zip)
	if [ ! -d $UPDATE_DIR ]
	then
		echo "Extraction failed."
		exit 1
	fi
fi

# Check that the update directory has K40 in it.
if [ ! -f ${UPDATE_DIR}/f-engrave.py ] ; then
	echo "F-Engrave  does not exist at \$1 = ${UPDATE_DIR}!"
	exit
fi

NEW_APP=$(ls -1 ${UPDATE_DIR}/f-engrave.py)
VERSION=$(grep "^version " ${UPDATE_DIR}/f-engrave.py | grep -Eo "[\.0-9]+")

echo "Updating to version $VERSION"

# Copy over changed supporting files
echo "Copy updated files from ${UPDATE_DIR}..."
for i in ${UPDATE_DIR}/*
do
	fn=`basename ${i}`
	if [ -f "$fn" ]
	then
		curd5=`${MD5} "${fn}"`
		newd5=`${MD5} "${UPDATE_DIR}/${fn}"`
		if [ "$curd5" != "$newd5" ]; then
			echo "*   $fn"
			cp "${UPDATE_DIR}/${fn}" "$fn"
		fi
	else
		echo "+   $fn"
		cp "${UPDATE_DIR}/${fn}" "$fn"
	fi
done

# Apply macOS patches to f-engrave.py
echo "Patch f-engrave for macOS..."
patch -p0 -i macOS.patch

# Update version in setup script
echo "Update version number in setup script..."
sed -i.orig "s/version = .*/version = \"${VERSION}\"/" setup.py

# Build macOS application
echo "Build macOS Application..."
./build-macOS.sh -d || exit

# Make new patch file
echo "Update macOS.patch file..."
rm macOS-${VERSION}.patch
for i in $(grep +++ macOS.patch | cut  -f1|cut -d\  -f2)
do
    diff -Naur $UPDATE_DIR/$i $i >> macOS-${VERSION}.patch
done

if [ ! -z ${CLEAN_SOURCE+x} ]
then
	echo "🧹 Cleaning up downloaded source files..."
	rm -rf $SOURCE_ZIP $UPDATE_DIR
fi
