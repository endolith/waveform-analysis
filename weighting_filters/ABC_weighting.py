# -*- coding: utf-8 -*-
"""
Created on Fri May 23 2014

Definitions from
 - ANSI S1.4-1983 Specification for Sound Level Meters, Section
   5.2 Weighting Networks, pg 5.
 - IEC 61672-1 (2002) Electroacoustics - Sound level meters,
   Part 1: Specification

"Above 20000 Hz, the relative response level shall decrease by at least 12 dB
per octave for any frequency-weighting characteristic"

Appendix C:

"it has been shown that the uncertainty allowed in the A-weighted frequency
response in the region above 16 kHz leads to an error which may exceed the
intended tolerances for the measurement of A-weighted sound level by a
precision (type 1) sound level meter."
"""

from __future__ import division
from scipy import signal
from numpy import pi, log10
import matplotlib.pyplot as plt


def ABC_weighting(curve='A'):
    """
    Return zeros, poles, gain of analog weighting filter with A, B, or C curve.

    Example:

    Plot all 3 curves:

    >>> from scipy import signal
    >>> import matplotlib.pyplot as plt
    >>> for curve in ['A', 'B', 'C']:
    ...     z, p, k = ABC_weighting(curve)
    ...     w = 2*pi*logspace(log10(10), log10(100000), 1000)
    ...     w, h = signal.freqs_zpk(z, p, k, w)
    ...     plt.semilogx(w/(2*pi), 20*np.log10(h), label=curve)
    >>> plt.title('Frequency response')
    >>> plt.xlabel('Frequency [Hz]')
    >>> plt.ylabel('Amplitude [dB]')
    >>> plt.ylim(-50, 20)
    >>> plt.grid(True, color='0.7', linestyle='-', which='major', axis='both')
    >>> plt.grid(True, color='0.9', linestyle='-', which='minor', axis='both')
    >>> plt.legend()
    >>> plt.show()

    """
    if curve not in 'ABC':
        raise ValueError('Curve type not understood')

    # ANSI S1.4-1983 C weighting
    #    2 poles on the real axis at "20.6 Hz" HPF
    #    2 poles on the real axis at "12.2 kHz" LPF
    #    -3 dB down points at "10^1.5 (or 31.62) Hz"
    #                         "10^3.9 (or 7943) Hz"
    #
    # IEC 61672 specifies "10^1.5 Hz" and "10^3.9 Hz" points and formulas for
    # derivation.  See _derive_coefficients()

    z = [0, 0]
    p = [-2*pi*20.598997057568145,
         -2*pi*20.598997057568145,
         -2*pi*12194.21714799801,
         -2*pi*12194.21714799801]
    k = 1

    if curve == 'A':
        # ANSI S1.4-1983 A weighting =
        #    Same as C weighting +
        #    2 poles on real axis at "107.7 and 737.9 Hz"
        #
        # IEC 61672 specifies cutoff of "10^2.45 Hz" and formulas for
        # derivation.  See _derive_coefficients()

        p.append(-2*pi*107.65264864304628)
        p.append(-2*pi*737.8622307362899)
        z.append(0)
        z.append(0)

    elif curve == 'B':
        # ANSI S1.4-1983 B weighting
        #    Same as C weighting +
        #    1 pole on real axis at "10^2.2 (or 158.5) Hz"
        p.append(-2*pi*10**2.2)  # exact
        z.append(0)

    # TODO: Calculate actual constants for this
    # Normalize to 0 dB at 1 kHz for all curves
    b, a = signal.zpk2tf(z, p, k)
    k /= abs(signal.freqs(b, a, [2*pi*1000])[1][0])

    return z, p, k


# TODO: Rename?
def A_weighting(fs):
    """
    Design of an A-weighting filter.

    Designs a digital A-weighting filter for
    sampling frequency `fs`. Usage: y = lfilter(b, a, x).
    Warning: fs should normally be higher than 20 kHz. For example,
    fs = 48000 yields a class 1-compliant filter.

    fs : float
        Sampling frequency

    Example:

    >>> from scipy.signal import freqz
    >>> import matplotlib.pyplot as plt
    >>> fs = 200000
    >>> b, a = A_weighting(fs)
    >>> f = np.logspace(np.log10(10), np.log10(fs/2), 1000)
    >>> w = 2*pi * f / fs
    >>> w, h = freqz(b, a, w)
    >>> plt.semilogx(w*fs/(2*pi), 20*np.log10(abs(h)))
    >>> plt.grid(True, color='0.7', linestyle='-', which='both', axis='both')
    >>> plt.axis([10, 100e3, -50, 20])

    Since this uses the bilinear transform, frequency response around fs/2 will
    be inaccurate at lower sampling rates.
    """
    z, p, k = ABC_weighting('A')

    # Use the bilinear transformation to get the digital filter.
#    try:
#        # Currently private but more accurate
#        zz, pz, kz = signal.filter_design._zpkbilinear(z, p, k, fs)
#        return signal.zpk2tf(zz, pz, kz)
    # TODO: THIS DOESN'T WORK< WHY?
#    except AttributeError:
    if True:
        b, a = signal.zpk2tf(z, p, k)
        return signal.bilinear(b, a, fs)


def A_weight(signal, fs):
    """
    Return the given signal after passing through an A-weighting filter

    signal : array_like
        Input signal
    fs : float
        Sampling frequency
    """

    b, a = A_weighting(fs)
    return signal.lfilter(b, a, signal)

"""
When importing a stereo sound file with scikits.audiolab or pysoundfile, it
needs axis = 0:
y = lfilter(b, a, x, axis = 0)
"""


def _derive_coefficients():
    """
    Calculate A- and C-weighting coefficients with equations from IEC 61672-1

    This is for reference only. The coefficients were generated with this and
    then placed in ABC_weighting().
    """
    import sympy as sp

    # Section 5.4.6
    f_r = 1000
    f_L = sp.Pow(10, sp.Rational('1.5'))  # 10^1.5 Hz
    f_H = sp.Pow(10, sp.Rational('3.9'))  # 10^3.9 Hz
    D = sp.sympify('1/sqrt(2)')  # D^2 = 1/2

    f_A = sp.Pow(10, sp.Rational('2.45'))  # 10^2.45 Hz

    # Section 5.4.9
    c = f_L**2 * f_H**2
    b = (1/(1-D))*(f_r**2+(f_L**2*f_H**2)/f_r**2-D*(f_L**2+f_H**2))

    f_1 = sp.sqrt((-b - sp.sqrt(b**2 - 4*c))/2)
    f_4 = sp.sqrt((-b + sp.sqrt(b**2 - 4*c))/2)

    # Section 5.4.10
    f_2 = (3 - sp.sqrt(5))/2 * f_A
    f_3 = (3 + sp.sqrt(5))/2 * f_A

    # Section 5.4.11
    assert abs(float(f_1) - 20.60) < 0.005
    assert abs(float(f_2) - 107.7) < 0.05
    assert abs(float(f_3) - 737.9) < 0.05
    assert abs(float(f_4) - 12194) < 0.5

    for f in ('f_1', 'f_2', 'f_3', 'f_4'):
        print(f'{f} = {float(eval(f))}')

    # Section 5.4.8  Normalizations
    f = 1000
    C1000 = (f_4**2 * f**2)/((f**2 + f_1**2) * (f**2 + f_4**2))
    A1000 = (f_4**2 * f**4)/((f**2 + f_1**2) * sp.sqrt(f**2 + f_2**2) *
                             sp.sqrt(f**2 + f_3**2) * (f**2 + f_4**2))

    # Section 5.4.11
    assert abs(20*log10(float(C1000)) + 0.062) < 0.0005
    assert abs(20*log10(float(A1000)) + 2.000) < 0.0005

    for norm in ('C1000', 'A1000'):
        print(f'{norm} = {float(eval(norm))}')


###########################################
################### TESTS


def check_weighting(curve='A', fs=None):
    """
    Test that frequency response meets tolerance from ANSI S1.4-1983
    """

    import numpy as np
    import matplotlib.pyplot as plt
    from scipy.signal import freqz
    from scipy.signal import zpk2tf, freqs

    # ANSI S1.4-1983 Table AI "Exact frequency"
    frequencies = np.array((10.00, 12.59, 15.85, 19.95, 25.12, 31.62, 39.81,
                            50.12, 65.10, 79.43, 100.00, 125.90, 158.50,
                            199.50, 251.20, 316.20, 398.10, 501.20, 631.00,
                            794.30, 1000.00, 1259.00, 1585.00, 1995.00,
                            2512.00, 3162.00, 3981.00, 5012.00, 6310.00,
                            7943.00, 10000.00, 12590.00, 15850.00, 19950.00,
                            25120.00, 31620.00, 39810.00, 50120.00, 63100.00,
                            79430.00, 100000.00,
                            ))

    responses = {}

    # ANSI S1.4-1983 Table AI "A weighting"
    responses['A'] = np.array((-70.4, -63.4, -56.7, -50.5, -44.7, -39.4, -34.6,
                               -30.2, -26.2, -22.5, -19.1, -16.1, -13.4, -10.9,
                               -8.6, -6.6, -4.8, -3.2, -1.9, -0.8, 0.0, +0.6,
                               +1.0, +1.2, +1.3, +1.2, +1.0, +0.5, -0.1, -1.1,
                               -2.5, -4.3, -6.6, -9.3, -12.4, -15.8, -19.3,
                               -23.1, -26.9, -30.8, -34.7,
                               ))

    # ANSI S1.4-1983 Table IV "B Weighting"
    responses['B'] = np.array((-38.2, -33.2, -28.5, -24.2, -20.4, -17.1, -14.2,
                               -11.6, -9.3, -7.4, -5.6, -4.2, -3.0, -2.0, -1.3,
                               -0.8, -0.5, -0.3, -0.1, 0.0, 0.0, 0.0, 0.0,
                               -0.1, -0.2, -0.4, -0.7, -1.2, -1.9, -2.9, -4.3,
                               -6.1, -8.4, -11.1,
                               ))

    # ANSI S1.4-1983 Table IV "C Weighting"
    responses['C'] = np.array((-14.3, -11.2, -8.5, -6.2, -4.4, -3.0, -2.0,
                               -1.3, -0.8, -0.5, -0.3, -0.2, -0.1, 0.0, 0.0,
                               0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.1, -0.2,
                               -0.3, -0.5, -0.8, -1.3, -2.0, -3.0, -4.4, -6.2,
                               -8.5, -11.2,
                               ))

    # ANSI S1.4-1983 Table AII "Type 0"
    # Stricter than IEC 61672-1 (2002) Table 2 Class 1 (±1.1 dB at 1 kHz)
    upper_limits = np.array((+2.0, +2.0, +2.0, +2.0, +1.5, +1.0, +1.0, +1.0,
                             +1.0, +1.0, +0.7, +0.7, +0.7, +0.7, +0.7, +0.7,
                             +0.7, +0.7, +0.7, +0.7, +0.7, +0.7, +0.7, +0.7,
                             +0.7, +0.7, +0.7, +1.0, +1.0, +1.0, +2.0, +2.0,
                             +2.0, +2.0, +2.4, +2.8, +3.3, +4.1, +4.9, +5.1,
                             +5.6,
                             ))

    lower_limits = np.array((-5.0, -4.0, -3.0, -2.0, -1.5, -1.0, -1.0, -1.0,
                             -1.0, -1.0, -0.7, -0.7, -0.7, -0.7, -0.7, -0.7,
                             -0.7, -0.7, -0.7, -0.7, -0.7, -0.7, -0.7, -0.7,
                             -0.7, -0.7, -0.7, -1.0, -1.5, -2.0, -3.0, -3.0,
                             -3.0, -3.0, -4.5, -6.2, -7.9, -9.3, -10.9, -12.2,
                             -14.3,
                             ))

    if fs is None:
        z, p, k = ABC_weighting(curve)
        b, a = zpk2tf(z, p, k)
        w, h = freqs(b, a, 2*pi*frequencies)
    else:
        # A passes if fs >= 260 kHz, but not at typical audio sample rates
        # So upsample 48 kHz by 6 times to get an accurate measurement?
        b, a = A_weighting(fs)
        w = 2*pi * frequencies / fs
        w, h = freqz(b, a, w)

    levels = 20 * np.log10(abs(h))

    levels = levels[:len(responses[curve])]
    frequencies = frequencies[:len(responses[curve])]
    upper_limits = upper_limits[:len(responses[curve])]
    lower_limits = lower_limits[:len(responses[curve])]

    plt.semilogx(frequencies, levels)
    plt.semilogx(frequencies, responses[curve] + upper_limits, 'r:')
    plt.semilogx(frequencies, responses[curve] + lower_limits, 'r:')
    plt.grid(True, color='0.7', linestyle='-', which='major')
    plt.grid(True, color='0.9', linestyle='-', which='minor')

    assert all(np.less_equal(levels, responses[curve] + upper_limits))
    assert all(np.greater_equal(levels, responses[curve] + lower_limits))


if __name__ == '__main__':
    plt.figure('A')
    check_weighting('A')
    check_weighting('A', 260000)

    plt.figure('B')
    check_weighting('B')
    # check_weighting('B', 260000)

    plt.figure('C')
    check_weighting('C')
    # check_weighting('C', 260000)
