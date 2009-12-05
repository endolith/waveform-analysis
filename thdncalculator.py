from __future__ import division
import sys
from scikits.audiolab import flacread
from numpy.fft import rfft, irfft
from numpy import argmax, sqrt, mean, absolute, linspace, log10, logical_and, average, diff, correlate
from matplotlib.mlab import find
from scipy.signal import blackmanharris, fftconvolve


def rms_flat(a):
    """
    Return the root mean square of all the elements of *a*, flattened out.
    
    """
    return sqrt(mean(absolute(a)**2))

def parabolic(f, x):
    """Quadratic interpolation for estimating the true position of an 
    inter-sample maximum when nearby samples are known.
    
    f is a vector and x is an index for that vector.
    
    Returns (vx, vy), the coordinates of the vertex of a parabola that goes
    through point x and its two neighbors.
    
    Example:
    Defining a vector f with a local maximum at index 3 (= 6), find local
    maximum if points 2, 3, and 4 actually defined a parabola.
    
    In [3]: f = [2, 3, 1, 6, 4, 2, 3, 1]
    
    In [4]: parabolic(f, argmax(f))
    Out[4]: (3.2142857142857144, 6.1607142857142856)
    
    """
    # Requires real division.  Insert float() somewhere to force it?
    xv = 1/2 * (f[x-1] - f[x+1]) / (f[x-1] - 2 * f[x] + f[x+1]) + x
    yv = f[x] - 1/4 * (f[x-1] - f[x+1]) * (xv - x)
    return (xv, yv)


filename = sys.argv[1]
signal, fs, enc = flacread(filename)

# Get rid of DC
signal -= mean(signal)

# Window it
windowed = signal * blackmanharris(len(signal))

# Measure the total signal before filtering but after windowing
total_rms = rms_flat(windowed)

# Fourier transform of windowed signal
f = rfft(windowed)

# Find the peak of the frequency spectrum (fundamental frequency) and filter by
# throwing away the region around it
i = argmax(abs(f))  # absolute?
true_i = parabolic(abs(f), i)[0]
print 'Frequency: %f Hz' % (fs * true_i / len(windowed))

# TODO: What's the right number of coefficients to use?  Probably depends on sample length, frequency? windowing etc.
width = 10
f[i-width: i+width+1] = 0

# Transform noise back into the signal domain and measure it
# Could probably calculate the RMS directly in the frequency domain instead
noise = irfft(f)
THDN = rms_flat(noise) / total_rms
print "THD+N:     %.4f%% or %.1f dB" % (THDN * 100, 20 * log10(THDN))
