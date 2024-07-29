#!/usr/bin/env python

import argparse
import sys

from numpy import absolute, array_equal, mean

from waveform_analysis import A_weight, ITU_R_468_weight
from waveform_analysis._common import dB, load, rms_flat, wav_loader

try:
    import easygui
    has_easygui = True
except:
    has_easygui = False
SEPARATOR = '-----------------'


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
        print(SEPARATOR)
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
        SEPARATOR,
    ]


def analyze(filename, gui):
    soundfile = load(filename)
    signal = soundfile['signal']
    channels = soundfile['channels']
    sample_rate = soundfile['fs']
    samples = soundfile['samples']
    file_format = soundfile['format']

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
        SEPARATOR,
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
    """
    Analyze one or more audio files and display their properties.

    Parameters
    ----------
    files : list
        List of file paths to analyze.
    gui : bool
        If True, attempt to use GUI for output display.

    Returns
    -------
    None
    """
    if files:
        for filename in files:
            try:
                analyze(filename, gui)
            except FileNotFoundError:
                raise SystemExit(f'File not found: "{filename}"')
            except IOError as e:
                raise SystemExit('I/O error occurred while reading '
                                 f'"{filename}": {str(e)}')
            except ValueError as e:
                raise SystemExit('Invalid audio file: '
                                 f'"{filename}": {str(e)}')
            except Exception as e:
                raise SystemExit('Unexpected error analyzing '
                                 f'"{filename}": {str(e)}')
            print('')
    else:
        # TODO: realtime analyzer goes here
        raise SystemExit("You must provide at least one file to analyze:\n"
                         "python wave_analyzer.py filename.wav [filename2.wav ...]")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze waveform properties")
    parser.add_argument("filenames", nargs='+',
                        help="Path(s) to the wave file(s) to analyze")
    parser.add_argument("--gui", action="store_true",
                        help="Use GUI for output if available")
    args = parser.parse_args()

    wave_analyzer(args.filenames, gui=args.gui)
