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
"""

from __future__ import division
from numpy import pi, polymul
from scipy.signal.filter_design import bilinear
from scipy.signal import lfilter

def A_weighting(Fs):
    """Design of an A-weighting filter.
    
    B, A = A_weighting(Fs) designs a digital A-weighting filter for 
    sampling frequency Fs. Usage: y = lfilter(B, A, x).
    Warning: Fs should normally be higher than 20 kHz. For example, 
    Fs = 48000 yields a class 1-compliant filter.

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
    # (Octave, MATLAB, and PyLab disagree about Fs vs 1/Fs)
    return bilinear(NUMs, DENs, Fs)

def A_weight(signal, samplerate):
    """Return the given signal after passing through an A-weighting filter
    
    """
    B, A = A_weighting(samplerate)
    return lfilter(B, A, signal)

# When importing a stereo sound file with scikits.audiolab, it needs axis = 0:
# y = lfilter(B, A, x, axis = 0)
