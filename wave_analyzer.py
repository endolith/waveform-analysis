#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from numpy import log10, pi, convolve, mean, sqrt, absolute, array_equal
from scipy.signal.filter_design import bilinear
from scipy.signal import lfilter
from scikits.audiolab import Sndfile, Format
from A_weighting import A_weight

def rms_flat(a):
    """
    Return the root mean square of all the elements of *a*, flattened out.
    """
    return sqrt(mean(absolute(a)**2))

def dB(level):
    """Return a level in decibels.
    
    Decibels (dBFS) are relative to the RMS level of a full-scale square wave 
    of peak amplitude 1.0.
    
    A full-scale square wave is 0 dB
    A full-scale sine wave is -3.01 dB
    
    """
    return 20 * log10(level)

def display(header, results):
    """Display header string and list of result lines"""
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
    """Plot a histogram of the sample values"""
    try:
        from matplotlib.pyplot import hist, show
    except ImportError:
        print 'Matplotlib not installed - skipping histogram'
    else:
        print 'Plotting histogram'
        hist(signal) #parameters
        show()

def properties(signal, samplerate):
    """Return a list of some wave properties for a given 1-D signal"""
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
    weighted = A_weight(signal, samplerate)
    weighted_level = rms_flat(weighted)
        
    return [
    'DC offset:\t%f (%.3f%%)' % (DC_offset, DC_offset * 100),
    'Crest factor:\t%.3f (%.3f dB)' % (crest_factor, dB(crest_factor)),
    'Peak level:\t%.3f (%.3f dBFS)' % (peak_level, dB(peak_level)), # Doesn't account for intersample peaks!
    'RMS level:\t%.3f (%.3f dBFS)' % (signal_level, dB(signal_level)),
    'A-weighted:\t%.3f (%.3f dBFS(A), %.3f dB)' % (weighted_level, dB(weighted_level), dB(weighted_level/signal_level)),
    '-----------------',
    ]
    
def analyze(filename):
    wave_file = Sndfile(filename, 'r')
    signal = wave_file.read_frames(wave_file.nframes)
    channels = wave_file.channels
    samplerate = wave_file.samplerate
    header = 'dBFS values are relative to a full-scale square wave'
    
    results = [
    'Properties for "' + filename + '"',
    str(wave_file.format),
    'Channels:\t%d' % channels,
    'Sampling rate:\t%d Hz' % samplerate,
    'Frames:\t%d' % wave_file.nframes,
    'Length:\t' + str(wave_file.nframes/samplerate) + ' seconds',
    '-----------------',
    ]
    
    wave_file.close()
    
    if channels == 1:
        # Monaural
        results += properties(signal, samplerate)
    elif channels == 2:
        # Stereo
        if array_equal(signal[:,0],signal[:,1]):
            results += ['Left and Right channels are identical:']
            results += properties(signal[:,0], samplerate)
        else:
            results += ['Left channel:']
            results += properties(signal[:,0], samplerate)
            results += ['Right channel:']
            results += properties(signal[:,1], samplerate)
    else:
        # Multi-channel
        for ch_no, channel in enumerate(signal.transpose()):
            results += ['Channel %d:' % (ch_no + 1)]
            results += properties(channel, samplerate)
    
    display(header, results)
    
    plot_histogram = False
    if plot_histogram:
        histogram(signal)

if __name__ == '__main__':
    import sys
    if len(sys.argv) == 2:
        filename = sys.argv[1]
        analyze(filename)
    else:
        print 'You need to provide a filename:\n'
        print 'python wave_analyzer.py filename.wav'
        