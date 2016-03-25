#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Created a SendTo shortcut to

    C:\...\pythonw.exe "C:\...\wave_analyzer_launcher.py"

and multiple files can be selected and analyzed from Explorer context menu,
with no command line window, and any errors are displayed in a GUI window.
"""

from __future__ import division
import sys

try:
    from wave_analyzer import wave_analyzer
    files = sys.argv[1:]
    wave_analyzer(files)

# Catches SystemExit, KeyboardInterrupt and GeneratorExit as well
# but that's ok because it re-raises them.
except BaseException as e:
    try:
        # Tkinter is built-in so it should just work?
        from Tkinter import Tk
        import tkMessageBox
        root = Tk().withdraw()  # hiding the main window
        var = tkMessageBox.showerror('Waveform analyzer',
                                     'Exception:\n' + str(e))
        raise
    except ImportError:
        # This shouldn't ever happen, and if it does it will be hidden by
        # pythonw.exe?
        print('Error:')
        print(e)
        # Otherwise Windows closes the window too quickly to read
        raw_input('(Press <Enter> to close)')
        raise
