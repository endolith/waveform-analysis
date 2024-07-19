#!/usr/bin/env python
r"""
Created a SendTo shortcut to

    C:\...\pythonw.exe "C:\...\wave_analyzer_launcher.py"

and multiple files can then be selected and analyzed from the Explorer context
menu, with no command line window, and any errors are displayed in a GUI
window.
"""

import sys

try:
    from thd_analyzer import thd_analyzer
    files = sys.argv[1:]
    thd_analyzer(files)

# TODO: argh this isnt working if easygui isn't installed.  pythonw never opens a command window.  it should get dumped into tkinter instead.

# Catches SystemExit, KeyboardInterrupt and GeneratorExit as well
# but that's ok because it re-raises them.
except BaseException as e:
    try:
        # Tkinter is built-in so it should always Just Work?
        import tkinter.messagebox
        from tkinter import Tk
        root = Tk().withdraw()  # hiding the main window
        var = tkinter.messagebox.showerror('THD analyzer',
                                           f"Exception:\n{str(e)}")
        raise
    except ImportError:
        # This shouldn't ever happen, and if it does it will be hidden by
        # pythonw.exe?
        print('Error:')
        print(e)
        # Otherwise Windows closes the window too quickly to read
        input('(Press <Enter> to close)')
        raise
