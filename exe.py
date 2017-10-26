from cx_Freeze import setup, Executable
import os

os.environ['TCL_LIBRARY'] = "C:\\Users\\Daniel\\Anaconda2\\tcl\\tcl8.5"
os.environ['TK_LIBRARY'] = "C:\\Users\\Daniel\\Anaconda2\\tcl\\tk8.5"

packages = ['pandas', 'numpy']
setup(
    name="output",
    version='1.0',
    description='A farming guide generator for Hogtown Knights',
    options={'build_exe': {'packages': packages}},
    executables=[Executable('main.py', base='Win32GUI')]
)
