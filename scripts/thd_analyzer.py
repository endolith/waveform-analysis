from math import log10
from time import time

from waveform_analysis._common import analyze_channels
from waveform_analysis.thd import THD, THDN


def thd_wrapper(signal, fs):
    """Wrapper function to analyze THD+N and THD, then print results"""
    # Calculate THD+N
    thdn = THDN(signal, fs)
    # Calculate THD
    thd = THD(signal, fs)

    # Print results in both % and dB
    print(f"THD+N(R):\t{thdn * 100:.4f}% or {20 * log10(thdn):.1f} dB")
    print(f"THD(F):  \t{thd * 100:.4f}% or {20 * log10(thd):.1f} dB")


def thd_analyzer(files):
    """Function for the launcher script to call"""
    if files:
        for filename in files:
            try:
                start_time = time()
                analyze_channels(filename, thd_wrapper)
                print(f'\nTime elapsed: {time() - start_time:.3f} s\n')
            except IOError:
                print(f"Couldn't analyze \"{filename}\"\n")
            print('')
    else:
        sys.exit("You must provide at least one file to analyze:\n"
                 "python thd_analyzer.py filename.wav")


if __name__ == '__main__':
    import sys
    try:
        files = sys.argv[1:]
        thd_analyzer(files)
    except BaseException as e:
        print('Error:')
        print(e)
        raise
    finally:
        # Only wait for input when running in an interactive console
        # Otherwise Windows closes the window too quickly to read
        if sys.stdout.isatty():
            input('(Press <Enter> to close)')
