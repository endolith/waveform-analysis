import sys
from time import time

from waveform_analysis._common import analyze_channels
from waveform_analysis.freq_estimation import freq_from_fft

if __name__ == '__main__':
    try:
        def freq_wrapper(signal, fs):
            freq = freq_from_fft(signal, fs)
            print(f'{freq:f} Hz')

        files = sys.argv[1:]
        if files:
            for filename in files:
                try:
                    start_time = time()
                    analyze_channels(filename, freq_wrapper)
                    print(f'\nTime elapsed: {time() - start_time:.3f} s\n')

                except IOError:
                    print(f"Couldn't analyze \"{filename}\"\n")
                print('')
        else:
            sys.exit("You must provide at least one file to analyze")
    except BaseException as e:
        print('Error:')
        print(e)
        raise
    finally:
        # Only wait for input when running in an interactive console
        # Otherwise Windows closes the window too quickly to read
        if sys.stdout.isatty():
            input('(Press <Enter> to close)')
