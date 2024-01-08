#run this from the command line: python py2exe_setup.py py2exe

from distutils.core import setup
import os
import shutil
import py2exe

script_name = "f-engrave.py"
icon_name   = "fengrave.ico"

fileName, fileExtension = os.path.splitext(script_name)
console_name = fileName+"_c"+fileExtension
shutil.copyfile(script_name,console_name)

setup(
    options = {
		"py2exe": 
		{
            "dll_excludes": ["crypt32.dll","MSVCP90.dll"],
			#%"excludes":  ["numpy"],
            "compressed": 0, "optimize": 0,
			"includes": ["numbers"],
            #"includes": ["lxml.etree", "lxml._elementpath", "gzip"],
		} 
	},
    zipfile = None,
    windows=[
		{
			"script": script_name,
			"icon_resources":[(0,icon_name),(1,icon_name)]
		}
	],
)
 
 
setup(
    options = {
		"py2exe": 
		{
            "dll_excludes": ["crypt32.dll","MSVCP90.dll"],
			#%"excludes":  ["numpy"],
            "compressed": 0, "optimize": 0,
			"includes": ["numbers"],
            #"includes": ["lxml.etree", "lxml._elementpath", "gzip"],
		} 
	},
    zipfile = None,
    console=[
		{
			"script": console_name,
			"icon_resources":[(0,icon_name),(1,icon_name)]
		}
	],
)

os.remove(console_name)

