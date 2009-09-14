#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
import numpy as np
from numpy import log10, pi, convolve, mean
from scipy.signal.filter_design import bilinear
from scipy.signal import lfilter
from scikits.audiolab import Sndfile, Format

def A_weighting(Fs):
    """Design of an A-weighting filter.
    
    [B,A] = A_weighting(Fs) designs a digital A-weighting filter for 
    sampling frequency Fs. Usage: Y = FILTER(B,A,X). 
    Warning: Fs should normally be higher than 20 kHz. For example, 
    Fs = 48000 yields a class 1-compliant filter.
    
    Originally a MATLAB script. Also included ASPEC, CDSGN, CSPEC.
    
    Author: Christophe Couvreur, Faculte Polytechnique de Mons (Belgium)
            couvreur@thor.fpms.ac.be
    Last modification: Aug. 20, 1997, 10:00am.
    
    http://www.mathworks.com/matlabcentral/fileexchange/69
    http://replaygain.hydrogenaudio.org/mfiles/adsgn.m
    Translated from adsgn.m to PyLab 2009-07-14 endolith@gmail.com
    
    References: 
       [1] IEC/CD 1672: Electroacoustics-Sound Level Meters, Nov. 1996.
    
    """
    # Definition of analog A-weighting filter according to IEC/CD 1672.
    f1 = 20.598997
    f2 = 107.65265
    f3 = 737.86223
    f4 = 12194.217
    A1000 = 1.9997
    
    NUMs = [(2 * pi * f4)**2 * (10**(A1000/20)), 0, 0, 0, 0]
    DENs = convolve([1, +4 * pi * f4, (2 * pi * f4)**2], 
                    [1, +4 * pi * f1, (2 * pi * f1)**2], mode='full')
    DENs = convolve(convolve(DENs, [1, 2 * pi * f3], mode='full'), 
                                   [1, 2 * pi * f2], mode='full')
    
    # Use the bilinear transformation to get the digital filter.
    # (Octave, MATLAB, and PyLab disagree about Fs vs 1/Fs)
    return bilinear(NUMs, DENs, Fs)

def A_weight(signal, samplerate):
    """Return the given signal after passing through an A-weighting filter"""
    B, A = A_weighting(samplerate)
    return lfilter(B, A, signal)

# From matplotlib.mlab
def rms_flat(a):
    """
    Return the root mean square of all the elements of *a*, flattened out.
    """
    return np.sqrt(np.mean(np.absolute(a)**2))

def ac_rms(signal):
    """Return the RMS level of the signal after removing any fixed DC offset"""
    return rms_flat(signal - mean(signal))

def dB(level):
     """Return a level in decibels.
     
     Decibels are relative to the RMS level of a full-scale square wave 
     of peak amplitude 1.0 (dBFS).
     
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
    signal_level = ac_rms(signal)
    peak_level = max(max(signal.flat),-min(signal.flat))
    crest_factor = peak_level/signal_level
    
    # Apply the A-weighting filter to the signal
    weighted = A_weight(signal, samplerate)
    weighted_level = ac_rms(weighted)
    
    return [
    'DC offset: %f (%.3f%%)' % (mean(signal), mean(signal)*100),
    'Crest factor: %.3f (%.3f dB)' % (crest_factor, dB(crest_factor)),
    'Peak level: %.3f (%.3f dB)' % (peak_level, dB(peak_level)), # Does not take intersample peaks into account!
    'RMS level: %.3f (%.3f dB)' % (signal_level, dB(signal_level)),
    'A-weighted: %.3f (%.3f dB)' % (weighted_level, dB(weighted_level)),
    'A-difference: %.3f dB' % dB(weighted_level/signal_level),
    '-----------------',
    ]
    
def analyze(filename):
    wave_file = Sndfile(filename, 'r')
    signal = wave_file.read_frames(wave_file.nframes)
    
    header = 'dB values are relative to a full-scale square wave'
    
    results = [
    'Properties for "' + filename + '"',
    str(wave_file.format),
    'Channels: %d' % wave_file.channels,
    'Sampling rate: %d Hz' % wave_file.samplerate,
    'Frames: %d' % wave_file.nframes,
    'Length: ' + str(wave_file.nframes/wave_file.samplerate) + ' seconds',
    '-----------------',
    ]
    
    # Currently only handles mono or stereo files
    # If both channels are identical, it will only show one properties sheet
    
    if wave_file.channels == 1:
        # Monaural
        results += properties(signal, wave_file.samplerate)
    elif wave_file.channels == 2:
        # Stereo
        if np.array_equal(signal[:,0],signal[:,1]):
            results += ['Left and right channels are identical:']
            results += properties(signal[:,0], wave_file.samplerate)
        else:
            results += ['Left channel:']
            results += properties(signal[:,0], wave_file.samplerate)
            results += ['Right channel:']
            results += properties(signal[:,1], wave_file.samplerate)
    else:
        # Multi-channel
        for ch_no, channel in enumerate(signal.transpose()):
            results += ['Channel %d:' % (ch_no + 1)]
            results += properties(channel, wave_file.samplerate)
    
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
        