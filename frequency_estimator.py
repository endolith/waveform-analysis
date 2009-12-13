from __future__ import division
from scikits.audiolab import flacread
from numpy.fft import rfft, irfft
from numpy import argmax, sqrt, mean, absolute, linspace, log10, logical_and, average, diff, correlate
from matplotlib.mlab import find
from scipy.signal import blackmanharris, fftconvolve
import time
import sys

# Faster version from http://projects.scipy.org/scipy/browser/trunk/scipy/signal/signaltools.py
# from signaltoolsmod import fftconvolve
from parabolic import parabolic

def freq_from_crossings(sig, fs):
    """Estimate frequency by counting zero crossings
    
    Pros: Fast, accurate (increasing with data length).  Works well for long low-noise sines, square, triangle, etc.
    
    Cons: Doesn't work if there are multiple zero crossings per cycle, low-frequency baseline shift, noise, etc.
    
    """
    # Find all indices right before a rising-edge zero crossing
    indices = find((sig[1:] >= 0) & (sig[:-1] < 0))
    
    # Naive (Measures 1000.185 Hz for 1000 Hz, for instance)
    #crossings = indices
    
    # More accurate, using linear interpolation to find intersample 
    # zero-crossings (Measures 1000.000129 Hz for 1000 Hz, for instance)
    crossings = [i - sig[i] / (sig[i+1] - sig[i]) for i in indices]
    
    # Some other interpolation based on neighboring points might be better. Spline, cubic, whatever
    
    return fs / average(diff(crossings))

def freq_from_fft(sig, fs):
    """Estimate frequency from peak of FFT
    
    Pros: Accurate, usually even more so than zero crossing counter 
    (1000.000003 Hz for 1000 Hz, for instance).  Due to parabolic interpolation 
    being a very good fit for windowed log FFT peaks?
    https://ccrma.stanford.edu/~jos/sasp/Quadratic_Interpolation_Spectral_Peaks.html
    Accuracy also increases with data length
    
    Cons: Doesn't find the right value if harmonics are stronger than 
    fundamental, which is common.  Better method would try to identify the fundamental
    
    """
    # Compute Fourier transform of windowed signal
    windowed = signal * blackmanharris(len(signal))
    f = rfft(windowed)
    
    # Find the peak and interpolate to get a more accurate peak
    i = argmax(abs(f)) # Just use this for less-accurate, naive version
    true_i = parabolic(abs(f), i)[0]
    
    # Convert to equivalent frequency
    return fs * true_i / len(windowed)

filename = sys.argv[1]

print 'Reading file "%s"\n' % filename
signal, fs, enc = flacread(filename)

print 'Calculating frequency from FFT:',
start_time = time.time()
print '%f Hz'   % freq_from_fft(signal, fs)
print 'Time elapsed: %.3f s\n' % (time.time() - start_time)

print 'Calculating frequency from zero crossings:',
start_time = time.time()
print '%f Hz' % freq_from_crossings(signal, fs)
print 'Time elapsed: %.3f s\n' % (time.time() - start_time)
