#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
import sys
from scikits.audiolab import Sndfile
from scipy.signal import blackmanharris
from numpy.fft import rfft, irfft
from numpy import argmax, sqrt, mean, absolute, arange, log10
import numpy as np

def rms_flat(a):
    """Return the root mean square of all the elements of *a*, flattened out.
    
    """
    return sqrt(mean(absolute(a)**2))

def find_range(f, x):
    """Find range between nearest local minima from peak at index x
    
    """
    for i in arange(x+1, len(f)):
        if f[i+1] >= f[i]:
            uppermin = i
            break
    for i in arange(x-1, 0, -1):
        if f[i] <= f[i-1]:
            lowermin = i + 1
            break
    return (lowermin, uppermin)

def THDN(signal, sample_rate):
    """Measure the THD+N for a signal and print the results
    
    Prints the estimated fundamental frequency and the measured THD+N.  This is 
    calculated from the ratio of the entire signal before and after 
    notch-filtering.
    
    Currently this tries to find the "skirt" around the fundamental and notch 
    out the entire thing.  A fixed-width filter would probably be just as good, 
    if not better.
    
    """
    # Get rid of DC and window the signal
    signal -= mean(signal) # TODO: Do this in the frequency domain, and take any skirts with it?
    windowed = signal * blackmanharris(len(signal))  # TODO Kaiser?

    # Measure the total signal before filtering but after windowing
    total_rms = rms_flat(windowed)

    # Find the peak of the frequency spectrum (fundamental frequency), and filter 
    # the signal by throwing away values between the nearest local minima
    f = rfft(windowed)
    i = argmax(abs(f))
    print 'Frequency: %f Hz' % (sample_rate * (i / len(windowed))) # Not exact
    lowermin, uppermin = find_range(abs(f), i)
    f[lowermin: uppermin] = 0

    # Transform noise back into the signal domain and measure it
    # TODO: Could probably calculate the RMS directly in the frequency domain instead
    noise = irfft(f)
    THDN = rms_flat(noise) / total_rms
    print "THD+N:     %.4f%% or %.1f dB" % (THDN * 100, 20 * log10(THDN))

def load(filename):
    """Load a wave file and return the signal, sample rate and number of channels.
    
    Can be any format that libsndfile supports, like .wav, .flac, etc.
    
    """
    wave_file = Sndfile(filename, 'r')
    signal = wave_file.read_frames(wave_file.nframes)
    channels = wave_file.channels
    sample_rate = wave_file.samplerate
    return signal, sample_rate, channels
    
def analyze_channels(filename, function):
    """Given a filename, run the given analyzer function on each channel of the file
	
	"""
    signal, sample_rate, channels = load(filename)
    print 'Analyzing "' + filename + '"...'

    if channels == 1:
        # Monaural
        function(signal, sample_rate)
    elif channels == 2:
        # Stereo
        if np.array_equal(signal[:,0],signal[:,1]):
            print '-- Left and Right channels are identical --'
            function(signal[:,0], sample_rate)
        else:
            print '-- Left channel --'
            function(signal[:,0], sample_rate)
            print '-- Right channel --'
            function(signal[:,1], sample_rate)
    else:
        # Multi-channel
        for ch_no, channel in enumerate(signal.transpose()):
            print '-- Channel %d --' % (ch_no + 1)
            function(channel, sample_rate)

files = sys.argv[1:]
if files:
    for filename in files:
        try:
            analyze_channels(filename, THDN)
        except:
            print 'Couldn\'t analyze "' + filename + '"'
        print ''
else:
    sys.exit("You must provide at least one file to analyze")
