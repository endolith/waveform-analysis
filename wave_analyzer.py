#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from numpy import mean, absolute, array_equal
from scikits.audiolab import Sndfile
from A_weighting import A_weight
from common import rms_flat, dB

def display(header, results):
    """Display header string and list of result lines
    
    """
    try:
        import easygui
    except ImportError:
        #Print to console
        print 'EasyGUI not installed - printing output to console\n'
        print header
        print '-----------------'
        print '\n'.join(results)
    else:
        # Pop the stuff up in a text box
        title = 'Waveform properties'
        easygui.textbox(header, title, '\n'.join(results))

def histogram(signal):
    """Plot a histogram of the sample values
    
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
    """Return a list of some wave properties for a given 1-D signal
    
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
    weighted = A_weight(signal, sample_rate)
    weighted_level = rms_flat(weighted)
    
    # TODO: rjust instead of tabs
    
    return [
    'DC offset:\t%f (%.3f%%)' % (DC_offset, DC_offset * 100),
    'Crest factor:\t%.3f (%.3f dB)' % (crest_factor, dB(crest_factor)),
    'Peak level:\t%.3f (%.3f dBFS)' % (peak_level, dB(peak_level)), # Doesn't account for intersample peaks!
    'RMS level:\t%.3f (%.3f dBFS)' % (signal_level, dB(signal_level)),
    'RMS A-weighted:\t%.3f (%.3f dBFS(A), %.3f dB)' % (weighted_level, dB(weighted_level), dB(weighted_level/signal_level)),
    '-----------------',
    ]
    
def analyze(filename):
    wave_file = Sndfile(filename, 'r')
    signal = wave_file.read_frames(wave_file.nframes)
    channels = wave_file.channels
    sample_rate = wave_file.samplerate
    header = 'dBFS values are relative to a full-scale square wave'
    
    results = [
    'Properties for "' + filename + '"',
    str(wave_file.format),
    'Channels:\t%d' % channels,
    'Sampling rate:\t%d Hz' % sample_rate,
    'Frames/samples:\t%d' % wave_file.nframes,
    'Length: \t' + str(wave_file.nframes/sample_rate) + ' seconds',
    '-----------------',
    ]
    
    wave_file.close()
    
    if channels == 1:
        # Monaural
        results += properties(signal, sample_rate)
    elif channels == 2:
        # Stereo
        if array_equal(signal[:,0],signal[:,1]):
            results += ['Left and Right channels are identical:']
            results += properties(signal[:,0], sample_rate)
        else:
            results += ['Left channel:']
            results += properties(signal[:,0], sample_rate)
            results += ['Right channel:']
            results += properties(signal[:,1], sample_rate)
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
            sys.exit("You must provide at least one file to analyze:\npython wave_analyzer.py filename.wav")
    except BaseException as e:
        print('Error:')
        print(e)
        raise
    finally:
        raw_input('(Press <Enter> to close)') # Otherwise Windows closes the window too quickly to read
