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

from numpy import pi
from scipy.signal import zpk2tf, zpk2sos, freqs, sosfilt
from waveform_analysis.weighting_filters._filter_design import _zpkbilinear

__all__ = ['ITU_R_468_weighting_analog', 'ITU_R_468_weighting',
           'ITU_R_468_weight']


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
    # TODO: Derive exact value with sympy
    b, a = zpk2tf(z, p, 1)
    w, h = freqs(b, a, 2*pi*6300)
    k = 10**(+12.2/20) / abs(h[0])

    return z, p, k


def ITU_R_468_weighting(fs, output='ba'):
    """
    Return ITU-R 468 digital weighting filter transfer function

    Parameters
    ----------
    fs : float
        Sampling frequency

    Examples
    --------

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
    zz, pz, kz = _zpkbilinear(z, p, k, fs)

    if output == 'zpk':
        return zz, pz, kz
    elif output in {'ba', 'tf'}:
        return zpk2tf(zz, pz, kz)
    elif output == 'sos':
        return zpk2sos(zz, pz, kz)
    else:
        raise ValueError("'%s' is not a valid output form." % output)


def ITU_R_468_weight(signal, fs):
    """
    Return the given signal after passing through an 468-weighting filter

    signal : array_like
        Input signal
    fs : float
        Sampling frequency
    """

    sos = ITU_R_468_weighting(fs, output='sos')
    return sosfilt(sos, signal)


if __name__ == '__main__':
    import pytest
    pytest.main(['../tests/test_ITU_R_468_weighting.py', "--capture=sys"])
