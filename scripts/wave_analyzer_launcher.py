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
    from wave_analyzer import wave_analyzer
    files = sys.argv[1:]
    wave_analyzer(files, gui=True)

# Catches SystemExit, KeyboardInterrupt and GeneratorExit as well
# but that's ok because it re-raises them.
except BaseException as e:
    try:
        # Tkinter is built-in, so it should always Just Work?
        import tkinter.messagebox
        from tkinter import Tk
        root = Tk().withdraw()  # hiding the main window
        var = tkinter.messagebox.showerror('Waveform analyzer',
                                           f"Exception:\n{str(e)}")
        raise
    except:  # ImportError:
        # This shouldn't ever happen, and if it does it will be hidden by
        # pythonw.exe?
        print('Error:')
        print(e)
        # Only wait for input when running in an interactive console
        # Otherwise Windows closes the window too quickly to read
        if sys.stdout.isatty():
            input('(Press <Enter> to close)')
        raise
