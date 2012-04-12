#!/usr/bin/env python
# -*- coding: utf-8 -*-

# TODO: Add A-weighting

from __future__ import division
from scipy.signal import kaiser
from numpy.fft import rfft, irfft
from numpy import argmax, mean, arange, log10, log
from common import analyze_channels, rms_flat, parabolic

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
    windowed = signal * kaiser(len(signal), 100)

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

def THD(signal, sample_rate):
    """Measure the THD for a signal
    
    Returns the estimated fundamental frequency and the measured THD,
    calculated by finding peaks in the spectrum.
        
    """
    # Get rid of DC and window the signal
    signal -= mean(signal) # TODO: Do this in the frequency domain, and take any skirts with it?
    windowed = signal * kaiser(len(signal), 100)
    
    # Find the peak of the frequency spectrum (fundamental frequency)
    f = rfft(windowed)
    i = argmax(abs(f))
    i = parabolic(log(abs(f)), i)[0]
    
    print 'Frequency: %f Hz' % (sample_rate * (i / len(windowed))) # Not exact
    
    print 'fundamental amplitude: %.3f' % abs(f[i])
    
    for x in range(2, 15):
        print '%.3f' % abs(f[i*x]),
   
    THD = sum([abs(f[i*x]) for x in range(2,15)]) / abs(f[i])
    print '\nTHD: %f%%' % (THD * 100)
    return

if __name__ == '__main__':
    try:
        import sys
        files = sys.argv[1:]
        if files:
            for filename in files:
                try:
                    analyze_channels(filename, THDN)
                except IOError:
                    print 'Couldn\'t analyze "' + filename + '"\n'
                print ''
        else:
            sys.exit("You must provide at least one file to analyze")
    except BaseException as e:
        print('Error:')
        print(e)
        raise
    finally:
        raw_input('(Press <Enter> to close)') # Otherwise Windows closes the window too quickly to read
