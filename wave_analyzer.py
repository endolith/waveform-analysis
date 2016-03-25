#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from numpy import mean, absolute, array_equal
from A_weighting import A_weight
from ITU_R_468_weighting import ITU_R_468_weight
from common import rms_flat, dB

try:
    from soundfile import SoundFile
    wav_loader = 'pysoundfile'
except:
    try:
        from scikits.audiolab import Sndfile
        wav_loader = 'audiolab'
    except:
        try:
            from scipy.io.wavfile import read
            wav_loader = 'scipy'
        except:
            raise ImportError('No sound file loading package installed '
                              '(pysoundfile, scikits.audiolab, or scipy')

try:
    import easygui
    displayer = 'easygui'
except:
    displayer = 'stdout'


def display(header, results):
    """
    Display header string and list of result lines
    """
    if displayer == 'easygui':
        title = 'Waveform properties'
        easygui.codebox(header, title, '\n'.join(results))
    else:
        print 'No EasyGUI; printing output to console\n'
        print header
        print '-----------------'
        print '\n'.join(results)


def histogram(signal):
    """
    Plot a histogram of the sample values
    """
    try:
        from matplotlib.pyplot import hist, show
    except ImportError:
        print 'Matplotlib not installed - skipping histogram'
    else:
        print 'Plotting histogram'
        hist(signal) #TODO: parameters, abs(signal)?
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
        'DC offset:\t%f (%.3f%%)' % (DC_offset, DC_offset * 100),
        'Crest factor:\t%.3f (%.3f dB)' % (crest_factor, dB(crest_factor)),
        'Peak level:\t%.3f (%.3f dBFS)' %
        (peak_level, dB(peak_level)),  # Doesn't account for intersample peaks!
        'RMS level:\t%.3f (%.3f dBFS)' % (signal_level, dB(signal_level)),
        'RMS A-weighted:\t%.3f (%.3f dBFS(A), %.3f dB)' %
        (Aweighted_level, dB(Aweighted_level),
         dB(Aweighted_level/signal_level)),
        'RMS 468-weighted:\t%.3f (%.3f dBFS(A), %.3f dB)' %
        (ITUweighted_level, dB(ITUweighted_level),
         dB(ITUweighted_level/signal_level)),
        '-----------------',
    ]


def analyze(filename):
    if wav_loader == 'pysoundfile':
        sf = SoundFile(filename)
        signal = sf.read()
        channels = sf.channels
        sample_rate = sf.samplerate
        samples = len(sf)
        file_format = sf.format_info + ' ' + sf.subtype_info
        sf.close()
    elif wav_loader == 'audiolab':
        sf = Sndfile(filename, 'r')
        signal = sf.read_frames(sf.nframes)
        channels = sf.channels
        sample_rate = sf.samplerate
        samples = sf.nframes
        file_format = sf.format
        sf.close()
    elif wav_loader == 'scipy':
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
            raise Exception("Don't know how to handle file "
                            "format {}".format(file_format))

    else:
        raise Exception("wav_loader has failed")

    header = 'dBFS values are relative to a full-scale square wave'

    if samples/sample_rate >= 1:
        length = str(samples/sample_rate) + ' seconds'
    else:
        length = str(samples/sample_rate*1000) + ' milliseconds'

    results = [
        'Properties for "' + filename + '"',
        str(file_format),
        'Channels:\t%d' % channels,
        'Sampling rate:\t%d Hz' % sample_rate,
        'Samples:\t%d' % samples,
        'Length: \t' + length,
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
            results += ['Channel %d:' % (ch_no + 1)]
            results += properties(channel, sample_rate)

    display(header, results)

    plot_histogram = False
    if plot_histogram:
        histogram(signal)

if __name__ == '__main__':
    try:
        import sys
        files = sys.argv[1:]
        if files:
            for filename in files:
                try:
                    analyze(filename)
                except IOError:
                    print 'Couldn\'t analyze "' + filename + '"\n'             
                print ''
        else:
            # TODO: realtime analyzer goes here
            sys.exit("You must provide at least one file to analyze:\npython wave_analyzer.py filename.wav")
    except BaseException as e:
        print('Error:')
        print(e)
        raise
    finally:
        raw_input('(Press <Enter> to close)') # Otherwise Windows closes the window too quickly to read
