#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Originally a MATLAB script. Also included ASPEC, CDSGN, CSPEC:

Author: Christophe Couvreur, Faculte Polytechnique de Mons (Belgium)
        couvreur@thor.fpms.ac.be
Last modification: Aug. 20, 1997, 10:00am.

http://www.mathworks.com/matlabcentral/fileexchange/69
http://replaygain.hydrogenaudio.org/mfiles/adsgn.m

Translated from adsgn.m to SciPy 2009-07-14 endolith@gmail.com

When importing a stereo sound file with scikits.audiolab or pysoundfile, it
needs axis = 0:
y = lfilter(b, a, x, axis = 0)
"""

from __future__ import division
from numpy import pi, polymul
from scipy.signal import bilinear, lfilter


def A_weighting(fs):
    """
    Design of an A-weighting filter.
    
    Designs a digital A-weighting filter for
    sampling frequency `fs`. Usage: y = lfilter(b, a, x).
    Warning: fs should normally be higher than 20 kHz. For example,
    fs = 48000 yields a class 1-compliant filter.

    Since this uses the bilinear transform, frequency response around fs/2 will
    be inaccurate at lower sampling rates.  A-weighting is undefined above
    20 kHz, though.

    Example:

    from scipy.signal import freqz
    import matplotlib.pyplot as plt
    fs = 200000  # change to 48000 to see truncation
    b, a = A_weighting(fs)
    f = np.logspace(np.log10(10), np.log10(fs/2), 1000)
    w = 2*pi * f / fs
    w, h = freqz(b, a, w)
    plt.semilogx(w*fs/(2*pi), 20*np.log10(abs(h)))
    plt.grid(True, color='0.7', linestyle='-', which='both', axis='both')
    plt.axis([10, 100e3, -50, 20])

    References:
       [1] IEC/CD 1672: Electroacoustics-Sound Level Meters, Nov. 1996.
    """

    # Definition of analog A-weighting filter according to IEC/CD 1672.
    f1 = 20.598997
    f2 = 107.65265
    f3 = 737.86223
    f4 = 12194.217
    A1000 = 1.9997

    NUMs = [(2*pi * f4)**2 * (10**(A1000/20)), 0, 0, 0, 0]

    DENs = polymul([1, 4*pi * f4, (2*pi * f4)**2],
                   [1, 4*pi * f1, (2*pi * f1)**2])
    DENs = polymul(DENs, [1, 2*pi * f3])
    DENs = polymul(DENs, [1, 2*pi * f2])

    # Analog confirmed to match https://en.wikipedia.org/wiki/A-weighting#A_2

    # Use the bilinear transformation to get the digital filter.
    return bilinear(NUMs, DENs, fs)


def A_weight(signal, fs):
    """
    Return the given signal after passing through an A-weighting filter

    signal : array_like
        Input signal
    fs : float
        Sampling frequency
    """

    b, a = A_weighting(fs)
    return lfilter(b, a, signal)
