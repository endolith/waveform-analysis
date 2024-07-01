from waveform_analysis._common import analyze_channels
from waveform_analysis.thd import THDN

# if __name__ == '__main__':
#
#
#    try:
#
#        if files:
#            for filename in files:
#                try:
#                    analyze_channels(filename, THDN)
#                except IOError:
#                    print('Couldn\'t analyze "' + filename + '"\n')
#                print('')
#        else:
#            sys.exit("You must provide at least one file to analyze")
#    except BaseException as e:
#        print('Error:')
#        print(e)
#        raise
#    finally:
#        # Otherwise Windows closes the window too quickly to read
#        input('(Press <Enter> to close)')
#


# print(f'Frequency: {fs * (true_i / len(windowed)):f} Hz')

# print(f"THD+N:      {THDN * 100:.4f}% or {20 * log10(THDN):.1f} dB")
# print(f"A-weighted: {THDNA * 100:.4f}% or {20 * log10(THDNA):.1f} dB(A)")


def thd_analyzer(files):
    import sys

    if files:
        for filename in files:
            try:
                analyze_channels(filename, THDN)
            except IOError:
                print(f"Couldn't analyze \"{filename}\"\n")
            print('')
    else:
        sys.exit("You must provide at least one file to analyze:\n"
                 "python wave_analyzer.py filename.wav")
