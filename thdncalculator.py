from __future__ import division
import sys
from scikits.audiolab import flacread
from scipy.signal import blackmanharris
from numpy.fft import rfft, irfft
from numpy import argmax, sqrt, mean, absolute, arange, log10

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

filename = sys.argv[1]
signal, fs, enc = flacread(filename)

# Get rid of DC and window the signal
signal -= mean(signal)
windowed = signal * blackmanharris(len(signal))

# Measure the total signal before filtering but after windowing
total_rms = rms_flat(windowed)

# Find the peak of the frequency spectrum (fundamental frequency), and filter 
# the signal by throwing away values between the nearest local minima
f = rfft(windowed)
i = argmax(abs(f))
print 'Frequency: %f Hz' % (fs * (i / len(windowed)))
lowermin, uppermin = find_range(abs(f), i)
f[lowermin: uppermin] = 0

# Transform noise back into the signal domain and measure it
# Could probably calculate the RMS directly in the frequency domain instead
noise = irfft(f)
THDN = rms_flat(noise) / total_rms
print "THD+N:     %.4f%% or %.1f dB" % (THDN * 100, 20 * log10(THDN))
