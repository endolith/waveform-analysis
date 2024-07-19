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


# print('Frequency: %f Hz' % (fs * (true_i / len(windowed))))
#
#    print("THD+N:      %.4f%% or %.1f dB"    % (THDN  * 100, 20 * log10(THDN)))
#    print("A-weighted: %.4f%% or %.1f dB(A)" % (THDNA * 100, 20 * log10(THDNA)))


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
