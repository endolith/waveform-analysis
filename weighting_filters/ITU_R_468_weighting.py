# -*- coding: utf-8 -*-
"""
Created on Sun Mar 20 2016

@author: endolith@gmail.com

Poles and zeros were calculated in Maxima from circuit component values which
are listed in:
https://www.itu.int/dms_pubrec/itu-r/rec/bs/R-REC-BS.468-4-198607-I!!PDF-E.pdf
http://www.beis.de/Elektronik/AudioMeasure/WeightingFilters.html#CCIR
https://en.wikipedia.org/wiki/ITU-R_468_noise_weighting
"""

from numpy import pi, inf
from scipy.signal import zpk2tf, freqs, bilinear, lfilter


def ITU_R_468_weighting_analog():
    """
    Return ITU-R 468 analog weighting filter zeros, poles, and gain
    """

    z = [0]
    p = [-25903.70104781628,
         +36379.90893732929j-23615.53521363528,
         -36379.90893732929j-23615.53521363528,
         +62460.15645250649j-18743.74669072136,
         -62460.15645250649j-18743.74669072136,
         -62675.1700584679]

    # Normalize to +12.2 dB at 6.3 kHz, numerically
    b, a = zpk2tf(z, p, 1)
    w, h = freqs(b, a, 2*pi*6300)
    k = 10**(+12.2/20) / abs(h[0])

    return z, p, k


def ITU_R_468_weighting(fs):
    """
    Return ITU-R 468 digital weighting filter transfer function

    fs : float
        Sampling frequency

    Example:

    >>> from scipy.signal import freqz
    >>> import matplotlib.pyplot as plt
    >>> fs = 200000
    >>> b, a = ITU_R_468_weighting(fs)
    >>> f = np.logspace(np.log10(10), np.log10(fs/2), 1000)
    >>> w = 2*pi * f / fs
    >>> w, h = freqz(b, a, w)
    >>> plt.semilogx(w*fs/(2*pi), 20*np.log10(abs(h)))
    >>> plt.grid(True, color='0.7', linestyle='-', which='both', axis='both')
    >>> plt.axis([10, 100e3, -50, 20])

    """

    z, p, k = ITU_R_468_weighting_analog()

    # Use the bilinear transformation to get the digital filter.
    try:
        # Currently private but more accurate
        from scipy.signal.filter_design import _zpkbilinear
        zz, pz, kz = _zpkbilinear(z, p, k, fs)
        return zpk2tf(zz, pz, kz)
    except ImportError:
        b, a = zpk2tf(z, p, k)
        return bilinear(b, a, fs)


def ITU_R_468_weight(signal, fs):
    """
    Return the given signal after passing through an 468-weighting filter

    signal : array_like
        Input signal
    fs : float
        Sampling frequency
    """

    b, a = ITU_R_468_weighting(fs)
    return lfilter(b, a, signal)


def test_ITU_R_468_weight(fs=None):
    """
    Test that frequency response meets tolerance from Rec. ITU-R BS.468-4
    """
    import numpy as np
    import matplotlib.pyplot as plt
    from scipy.signal import freqz

    frequencies = np.array((
        31.5, 63, 100, 200, 400, 800, 1000, 2000, 3150, 4000, 5000,
        6300,
        7100, 8000, 9000, 10000, 12500, 14000, 16000, 20000, 31500
        ))

    responses = np.array((
        -29.9, -23.9, -19.8, -13.8, -7.8, -1.9, 0, +5.6, +9.0, +10.5, +11.7,
        +12.2,
        +12.0, +11.4, +10.1, +8.1, 0, -5.3, -11.7, -22.2, -42.7
        ))

    upper_limits = np.array((
        +2.0, +1.4, +1.0, +0.85, +0.7, +0.55, +0.5, +0.5, +0.5, +0.5, +0.5,
        +0.01,   # Actually 0 tolerance, but specified as "+12.2" dB
        +0.2, +0.4, +0.6, +0.8, +1.2, +1.4, +1.6, +2.0, +2.8
        ))

    lower_limits = np.array((
        -2.0, -1.4, -1.0, -0.85, -0.7, -0.55, -0.5, -0.5, -0.5, -0.5, -0.5,
        -0.01,   # Actually 0 tolerance, but specified as "+12.2" dB
        -0.2, -0.4, -0.6, -0.8, -1.2, -1.4, -1.6, -2.0, -inf
        ))

    if fs is None:
        z, p, k = ITU_R_468_weighting_analog()
        b, a = zpk2tf(z, p, k)
        w, h = freqs(b, a, 2*pi*frequencies)
    else:
        # Passes if fs >= 180000 Hz but not at typical audio sample rates
        b, a = ITU_R_468_weighting(fs)
        w = 2*pi * frequencies / fs
        w, h = freqz(b, a, w)

    levels = 20 * np.log10(abs(h))

    plt.semilogx(frequencies, levels)
    plt.semilogx(frequencies, responses + upper_limits, 'r:')
    plt.semilogx(frequencies, responses + lower_limits, 'r:')
    plt.grid(True, color='0.7', linestyle='-', which='major')
    plt.grid(True, color='0.9', linestyle='-', which='minor')

    assert all(np.less_equal(levels, responses + upper_limits))
    assert all(np.greater_equal(levels, responses + lower_limits))

if __name__ == '__main__':
    test_ITU_R_468_weight()
