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

UPDATE_DIR=$1
if [ ! -f ${UPDATE_DIR}/f-engrave-???.py ] ; then
	echo "F-Engrave does not exist at \$1 = ${UPDATE_DIR}!"
	exit
fi

NEW_APP=$(ls -1 ${UPDATE_DIR}/f-engrave-???.py)
FILE_VERSION=$(basename ${UPDATE_DIR}/f-engrave-???.py .py |cut -d- -f3)
VERSION=$(echo ${FILE_VERSION}|cut -c1).$(echo ${FILE_VERSION}|cut -c2-)

echo "Updating to version $VERSION"

# Copy f-engrave Python script
echo "Copy new version of f-engrave..."
echo "    `basename ${NEW_APP}`"
cp "${NEW_APP}" "f-engrave.py"

# Copy over changed supporting files
echo "Copy supporting files..."
for i in $files
do
	curd5=`${MD5} "${i}"`
	newd5=`${MD5} "${UPDATE_DIR}/${i}"`
	if [ "$curd5" != "$newd5" ]; then
		echo "    $i"
		cp "${UPDATE_DIR}/${i}" "$i"
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
./build.sh

# Make macOS Disk Image (.dmg) for distribution
echo "Build macOS Disk Image..."
hdiutil create -fs HFS+ -volname F-Engrave-${VERSION} -srcfolder ./dist ./F-Engrave-${VERSION}.dmg

