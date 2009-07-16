from scipy.signal.filter_design import bilinear
from scipy.signal import lfilter
from numpy import pi, convolve

def A_weighting(Fs):
    """Design of an A-weighting filter.
    
    B, A = A_weighting(Fs) designs a digital A-weighting filter for 
    sampling frequency Fs. Usage: y = lfilter(B, A, x).
    Warning: Fs should normally be higher than 20 kHz. For example, 
    Fs = 48000 yields a class 1-compliant filter.
    
    Original also included ASPEC, CDSGN, CSPEC.
    
    Author: Christophe Couvreur, Faculte Polytechnique de Mons (Belgium)
            couvreur@thor.fpms.ac.be
    Last modification: Aug. 20, 1997, 10:00am.
    
    Translated from adsgn.m to PyLab 2009-07-14 endolith@gmail.com
    
    References: 
       [1] IEC/CD 1672: Electroacoustics-Sound Level Meters, Nov. 1996.
    
    """
    
    # Definition of analog A-weighting filter according to IEC/CD 1672.
    f1 = 20.598997
    f2 = 107.65265
    f3 = 737.86223
    f4 = 12194.217
    A1000 = 1.9997
    
    NUMs = [(2*pi*f4)**2*(10**(A1000/20)), 0, 0, 0, 0]
    DENs = convolve([1, +4*pi*f4, (2*pi*f4)**2], [1, +4*pi*f1, (2*pi*f1)**2], mode='full')
    DENs = convolve(convolve(DENs, [1, 2*pi*f3], mode='full'), [1, 2*pi*f2], mode='full')
    
    # Use the bilinear transformation to get the digital filter.
    # (Octave, MATLAB, and PyLab disagree about Fs vs 1/Fs)
    return bilinear(NUMs, DENs, Fs)

# You probably need to specify the axis. Importing a stereo sound file with scikits.audiolab needs axis = 0, for instance:
y = lfilter(B, A, x, axis = 0)