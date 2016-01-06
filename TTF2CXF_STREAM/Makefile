#
# Makefile for TTF2CXF_STREAM
# Date: 6/28/2013

WIN_BASEDIR = freetype-2.3.5-1-lib

all: linux

linux:
	g++ -o ttf2cxf_stream ttf2cxf_stream.cpp -lm -I/usr/include/freetype2 -lfreetype

install: linux
	@echo "Installing... ttf2cxf_stream"
	/usr/bin/install -m 755 -t /usr/local/bin ttf2cxf_stream
	@echo "Done Installing..."

win:
	g++ -o ttf2cxf_stream         \
		ttf2cxf_stream.cpp    \
		-static-libgcc        \
		-static-libstdc++     \
		-lm                   \
		-lfreetype.dll        \
		-lfreetype            \
		-I$(WIN_BASEDIR)/include             \
		-I$(WIN_BASEDIR)/include/freetype2   \
		-L$(WIN_BASEDIR)/lib                 \
		$(WIN_BASEDIR)/lib/freetype.lib


