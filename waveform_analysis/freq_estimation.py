#!/usr/bin/env python

from waveform_analysis._common import parabolic
from numpy.fft import rfft
from numpy import asarray, argmax, mean, diff, log, copy
from matplotlib.mlab import find
from scipy.signal import correlate, kaiser, decimate


def freq_from_crossings(signal, fs):
    """
    Estimate frequency by counting zero crossings

    Works well for long low-noise sines, square, triangle, etc.

    Pros: Fast, accurate (increasing with signal length).

    Cons: Doesn't work if there are multiple zero crossings per cycle,
    low-frequency baseline shift, noise, inharmonicity, etc.
    """
    signal = asarray(signal) + 0.0

    # Find all indices right before a rising-edge zero crossing
    indices = find((signal[1:] >= 0) & (signal[:-1] < 0))

    # Naive (Measures 1000.185 Hz for 1000 Hz, for instance)
    # crossings = indices

    # More accurate, using linear interpolation to find intersample
    # zero-crossings (Measures 1000.000129 Hz for 1000 Hz, for instance)
    crossings = [i - signal[i] / (signal[i+1] - signal[i]) for i in indices]

    # Some other interpolation based on neighboring points might be better.
    # Spline, cubic, whatever

    return fs / mean(diff(crossings))


def freq_from_fft(signal, fs):
    """
    Estimate frequency from peak of FFT

    Pros: Accurate, usually even more so than zero crossing counter
    (1000.000004 Hz for 1000 Hz, for instance).  Due to parabolic
    interpolation being a very good fit for windowed log FFT peaks?
    https://ccrma.stanford.edu/~jos/sasp/Quadratic_Interpolation_Spectral_Peaks.html
    Accuracy also increases with signal length

    Cons: Doesn't find the right value if harmonics are stronger than
    fundamental, which is common.
    """
    signal = asarray(signal)

    N = len(signal)

    # Compute Fourier transform of windowed signal
    windowed = signal * kaiser(N, 100)
    f = rfft(windowed)

    # Find the peak and interpolate to get a more accurate peak
    i_peak = argmax(abs(f))  # Just use this value for less-accurate result
    i_interp = parabolic(log(abs(f)), i_peak)[0]

    # Convert to equivalent frequency
    return fs * i_interp / N  # Hz


def freq_from_autocorr(signal, fs):
    """
    Estimate frequency using autocorrelation

    Pros: Best method for finding the true fundamental of any repeating wave,
    even with strong harmonics or completely missing fundamental

    Cons: Not as accurate, doesn't find fundamental for inharmonic things like
    musical instruments, this implementation has trouble with finding the true
    peak
    """
    signal = asarray(signal) + 0.0

    # Calculate autocorrelation, and throw away the negative lags
    signal -= mean(signal)  # Remove DC offset
    corr = correlate(signal, signal, mode='full')
    corr = corr[len(corr)//2:]

    # Find the first valley in the autocorrelation
    d = diff(corr)
    start = find(d > 0)[0]

    # Find the next peak after the low point (other than 0 lag).  This bit is
    # not reliable for long signals, due to the desired peak occurring between
    # samples, and other peaks appearing higher.
    i_peak = argmax(corr[start:]) + start
    i_interp = parabolic(corr, i_peak)[0]

    return fs / i_interp


def freq_from_hps(signal, fs):
    """
    Estimate frequency using harmonic product spectrum

    Low frequency noise piles up and overwhelms the desired peaks

    Doesn't work well if signal doesn't have harmonics
    """
    signal = asarray(signal) + 0.0

    N = len(signal)
    signal -= mean(signal)  # Remove DC offset

    # Compute Fourier transform of windowed signal
    windowed = signal * kaiser(N, 100)

    # Get spectrum
    X = log(abs(rfft(windowed)))

    # Remove mean of spectrum (so sum is not increasingly offset
    # only in overlap region)
    X -= mean(X)

    # Downsample sum logs of spectra instead of multiplying
    hps = copy(X)
    for h in range(2, 9):  # TODO: choose a smarter upper limit
        dec = decimate(X, h, zero_phase=True)
        hps[:len(dec)] += dec

    # Find the peak and interpolate to get a more accurate peak
    i_peak = argmax(hps[:len(dec)])
    i_interp = parabolic(hps, i_peak)[0]

    # Convert to equivalent frequency
    return fs * i_interp / N  # Hz


if __name__ == '__main__':
    import pytest
    pytest.main(['./tests/test_freq_estimation.py', "--capture=sys"])
