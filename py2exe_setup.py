#run this from the command line: python py2exe_setup.py py2exe

from distutils.core import setup
import py2exe


setup(
    options = {"py2exe": {"compressed": 0, "optimize": 0, } },
    zipfile = None,
    console=[{"script":"f-engrave-158.py","icon_resources":[(0,"fengrave.ico"),(0,"fengrave.ico")]}]
)
