#!/usr/bin/env python

import argparse
import sys

from numpy import absolute, array_equal, mean

from waveform_analysis import A_weight, ITU_R_468_weight
from waveform_analysis._common import dB, rms_flat

try:
    from soundfile import SoundFile
    wav_loader = 'pysoundfile'
except:
    try:
        from scipy.io.wavfile import read
        wav_loader = 'scipy.io.wavfile'
    except:
        raise ImportError('No sound file loading package installed '
                          '(PySoundFile or SciPy)')

try:
    import easygui
    has_easygui = True
except:
    has_easygui = False


def display(header, results, gui):
    """
    Display header string and list of result lines
    """
    if gui and not has_easygui:
        print('No EasyGUI; printing output to console\n')
    elif gui and has_easygui:
        title = 'Waveform properties'
        easygui.codebox(header, title, '\n'.join(results))
    else:
        print(header)
        print('-----------------')
        print('\n'.join(results))


def histogram(signal):
    """
    Plot a histogram of the sample values
    """
    try:
        from matplotlib.pyplot import hist, show
    except ImportError:
        print('Matplotlib not installed - skipping histogram')
    else:
        print('Plotting histogram')
        hist(signal)  # TODO: parameters, abs(signal)?
        show()


def properties(signal, sample_rate):
    """
    Return a list of some wave properties for a given 1-D signal
    """
    # Measurements that include DC component
    DC_offset = mean(signal)
    # Maximum/minimum sample value
    # Estimate of true bit rate

    # Remove DC component
    signal -= mean(signal)

    # Measurements that don't include DC
    signal_level = rms_flat(signal)
    peak_level = max(absolute(signal))
    crest_factor = peak_level/signal_level

    # Apply the A-weighting filter to the signal
    Aweighted = A_weight(signal, sample_rate)
    Aweighted_level = rms_flat(Aweighted)

    # Apply the ITU-R 468 weighting filter to the signal
    ITUweighted = ITU_R_468_weight(signal, sample_rate)
    ITUweighted_level = rms_flat(ITUweighted)

    # TODO: rjust instead of tabs

    return [
        f'DC offset:\t{DC_offset:f} ({DC_offset * 100:.3f}%)',
        f'Crest factor:\t{crest_factor:.3f} ({dB(crest_factor):.3f} dB)',
        # Peak level doesn't account for intersample peaks!
        f'Peak level:\t{peak_level:.3f} ({dB(peak_level):.3f} dBFS)',
        f'RMS level:\t{signal_level:.3f} ({dB(signal_level):.3f} dBFS)',
        (f'RMS A-weighted:\t{Aweighted_level:.3f} ({dB(Aweighted_level):.3f} '
         f'dBFS(A), {dB(Aweighted_level / signal_level):.3f} dB)'),
        (f'RMS 468-weighted:\t{ITUweighted_level:.3f} '
         f'({dB(ITUweighted_level):.3f} dBFS(468), '
         f'{dB(ITUweighted_level / signal_level):.3f} dB)'),
        '-----------------',
    ]


def analyze(filename, gui):
    if wav_loader == 'pysoundfile':
        sf = SoundFile(filename)
        signal = sf.read()
        channels = sf.channels
        sample_rate = sf.samplerate
        samples = len(sf)
        file_format = f"{sf.format_info} {sf.subtype_info}"
        sf.close()
    elif wav_loader == 'scipy.io.wavfile':
        sample_rate, signal = read(filename)
        try:
            channels = signal.shape[1]
        except IndexError:
            channels = 1
        samples = signal.shape[0]
        file_format = str(signal.dtype)

        # Scale common formats
        # Other bit depths (24, 20) are not handled by SciPy correctly.
        if file_format == 'int16':
            signal = signal.astype(float) / (2**15)
        elif file_format == 'uint8':
            signal = (signal.astype(float) - 128) / (2**7)
        elif file_format == 'int32':
            signal = signal.astype(float) / (2**31)
        elif file_format == 'float32':
            pass
        else:
            raise Exception("Don't know how to handle file format "
                            f"{file_format}")

    else:
        raise Exception("wav_loader has failed")

    header = 'dBFS values are relative to a full-scale square wave'

    if samples/sample_rate >= 1:
        length = f"{str(samples / sample_rate)} seconds"
    else:
        length = f"{str(samples / sample_rate * 1000)} milliseconds"

    results = [
        f"Using sound file backend '{wav_loader}'",
        f"Properties for \"{filename}\"",
        str(file_format),
        f'Channels:\t{channels}',
        f'Sampling rate:\t{sample_rate} Hz',
        f'Samples:\t{samples}',
        f"Length: \t{length}",
        '-----------------',
    ]

    if channels == 1:
        # Monaural
        results += properties(signal, sample_rate)
    elif channels == 2:
        # Stereo
        if array_equal(signal[:, 0], signal[:, 1]):
            results += ['Left and Right channels are identical:']
            results += properties(signal[:, 0], sample_rate)
        else:
            results += ['Left channel:']
            results += properties(signal[:, 0], sample_rate)
            results += ['Right channel:']
            results += properties(signal[:, 1], sample_rate)
    else:
        # Multi-channel
        for ch_no, channel in enumerate(signal.transpose()):
            results += [f'Channel {ch_no + 1}:']
            results += properties(channel, sample_rate)

    display(header, results, gui)

    plot_histogram = False
    if plot_histogram:
        histogram(signal)


def wave_analyzer(files, gui):
    if files:
        for filename in files:
            try:
                analyze(filename, gui)
            except IOError:
                print(f"Couldn't analyze \"{filename}\"\n")
            print('')
    else:
        # TODO: realtime analyzer goes here
        sys.exit("You must provide at least one file to analyze:\n"
                 "python wave_analyzer.py filename.wav")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze waveform properties")
    parser.add_argument("filename", help="Path to the wave file to analyze")
    parser.add_argument("--gui", action="store_true",
                        help="Use GUI for output if available")
    args = parser.parse_args()

    wave_analyzer([args.filename], gui=args.gui)
