#!/bin/bash
#
# Script to copy changed files from Scorch's updated F-Engrave
# to staging directory for creating macOS package.
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
VERSION=$(basename ${UPDATE_DIR}/f-engrave-???.py .py |cut -d- -f3)

# Copy f-engrave Python script
echo "Copy new version of f-engrave"
echo "    `basename ${NEW_APP}`"
cp "${NEW_APP}" "f-engrave.py"

# Copy over changed supporting files
echo "Copy supporting files"
for i in $files
do
	curd5=`${MD5} "${i}"`
	newd5=`${MD5} "${UPDATE_DIR}/${i}"`
	if [ "$curd5" != "$newd5" ]; then
		echo "    $i"
		cp "${UPDATE_DIR}/${i}" "$i"
	fi
done

# Update version in setup script
#osx:
#-       g++ -o ttf2cxf_stream ttf2cxf_stream.cpp -lm -I/usr/X11/include/freetype2 -L/usr/X11/lib #-lfreetype

# Apply macOS patches to f-engrave.py
echo "Patch f-engrave for macOS..."
patch -p0 -i macOS.patch

# Build macOS application
echo "Build macOS Application"
#./build.sh


