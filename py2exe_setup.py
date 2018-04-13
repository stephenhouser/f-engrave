#run this from the command line: python py2exe_setup.py py2exe

from distutils.core import setup
import os
import shutil
import py2exe

script_name = "f-engrave-165.py"

fileName, fileExtension = os.path.splitext(script_name)
console_name = fileName+"_c"+fileExtension
shutil.copyfile(script_name,console_name)

setup(
    options = {"py2exe": {"compressed": 0, "optimize": 0, } },
    zipfile = None,
    windows = [
    {
        "script": script_name,
        "icon_resources":[(0,"fengrave.ico"),(0,"fengrave.ico")]
    }
  ],
 )
 
setup(
    options = {"py2exe": {"compressed": 0, "optimize": 0, } },
    zipfile = None,
    console=[
        {
            "script":console_name,
            "icon_resources":[(0,"fengrave.ico"),(0,"fengrave.ico")]
            }
    ]
)
os.remove(console_name)

