#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from scipy.signal import kaiser
from numpy.fft import rfft, irfft
from numpy import argmax, mean, log10, log, ceil, concatenate, zeros
from common import analyze_channels, rms_flat, parabolic, round2
from A_weighting import A_weight

def THDN(signal, sample_rate):
    """Measure the THD+N for a signal and print the results
    
    Prints the estimated fundamental frequency and the measured THD+N.  This is 
    calculated from the ratio of the entire signal before and after 
    notch-filtering.
    
    This notch-filters by nulling out the frequency coefficients ±10% of the 
    fundamental
    
    """
    # Get rid of DC and window the signal
    signal -= mean(signal) # TODO: Do this in the frequency domain, and take any skirts with it?
    windowed = signal * kaiser(len(signal), 100)
    del signal
   
    # Zero pad to nearest power of two
    new_len = 2**ceil( log(len(windowed)) / log(2) )
    windowed = concatenate((windowed, zeros(new_len - len(windowed))))
    
    # Measure the total signal before filtering but after windowing
    total_rms = rms_flat(windowed)
    
    # Find the peak of the frequency spectrum (fundamental frequency)
    f = rfft(windowed, round2(len(windowed)))
    i = argmax(abs(f))
    true_i = parabolic(log(abs(f)), i)[0]
    print 'Frequency: %f Hz' % (sample_rate * (true_i / len(windowed)))
    
    # Filter out fundamental by throwing away values ±10%
    lowermin = true_i - 0.1 * true_i
    uppermin = true_i + 0.1 * true_i
    f[lowermin: uppermin] = 0
    
    # Transform noise back into the time domain and measure it
    noise = irfft(f)[:len(windowed)]
    THDN = rms_flat(noise) / total_rms
    
    # TODO: RMS and A-weighting in frequency domain?
    
    # Apply A-weighting to residual noise (Not normally used for distortion, 
    # but used to measure dynamic range with -60 dBFS signal, for instance)
    weighted = A_weight(noise, sample_rate)
    THDNA = rms_flat(weighted) / total_rms
    
    print "THD+N:      %.4f%% or %.1f dB"    % (THDN  * 100, 20 * log10(THDN))
    print "A-weighted: %.4f%% or %.1f dB(A)" % (THDNA * 100, 20 * log10(THDNA))

def THD(signal, sample_rate):
    """Measure the THD for a signal
    
    This function is not yet trustworthy.
    
    Returns the estimated fundamental frequency and the measured THD,
    calculated by finding peaks in the spectrum.
    
    There are two definitions for THD, a power ratio or an amplitude ratio
    When finished, this will list both
    
    """
    # Get rid of DC and window the signal
    signal -= mean(signal) # TODO: Do this in the frequency domain, and take any skirts with it?
    windowed = signal * kaiser(len(signal), 100)
    
    # Find the peak of the frequency spectrum (fundamental frequency)
    f = rfft(windowed, round2(len(windowed)))
    i = argmax(abs(f))
    true_i = parabolic(log(abs(f)), i)[0]
    print 'Frequency: %f Hz' % (sample_rate * (true_i / len(windowed)))
    
    print 'fundamental amplitude: %.3f' % abs(f[i])
    
    # Find the values for the first 15 harmonics.  Includes harmonic peaks only, by definition
    # TODO: Should peak-find near each one, not just assume that fundamental was perfectly estimated.
    # Instead of limited to 15, figure out how many fit based on f0 and sampling rate and report this "4 harmonics" and list the strength of each
    for x in range(2, 15):
        print '%.3f' % abs(f[i * x]),
   
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
