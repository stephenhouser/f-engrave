
APP=F-Engrave.app
VER=154

all: ttf2cxf app

ttf2cxf:
	@(cd ../TTF2CXF_STREAM; make osx)
    
app:
	@mkdir $(APP) $(APP)/Contents $(APP)/Contents/MacOS $(APP)/Contents/Resources

	@cp ../f-engrave-$(VER).py $(APP)/Contents/MacOS
	@cp ../TTF2CXF_STREAM/ttf2cxf_stream $(APP)/Contents/MacOS

	@cp Info.plist $(APP)/Contents

	@cp f-engrave.sh $(APP)/Contents/MacOS
	@chmod +x $(APP)/Contents/MacOS/f-engrave.sh

	@cp f-engrave.icns $(APP)/Contents/Resources
