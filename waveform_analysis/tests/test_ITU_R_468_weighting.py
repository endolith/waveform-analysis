import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import freqz

from context import waveform_analysis
from waveform_analysis.weighting_filters import ITU


def check_ITU_R_468_weight(fs=None):
    """
    Test that frequency response meets tolerance from Rec. ITU-R BS.468-4
    """


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
        -0.2, -0.4, -0.6, -0.8, -1.2, -1.4, -1.6, -2.0, -float('inf')
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
    plt.semilogx(frequencies, responses + upper_limits, 'r--')
    plt.semilogx(frequencies, responses + lower_limits, 'r--')
    plt.grid(True, color='0.7', linestyle='-', which='major')
    plt.grid(True, color='0.9', linestyle='-', which='minor')

    assert all(np.less_equal(levels, responses + upper_limits))
    assert all(np.greater_equal(levels, responses + lower_limits))


# Class 468 analog
def test_freq_resp():
    pass


# Class 468 digital
def test_freq_resp():
    pass


def test_468_analog():
    check_ITU_R_468_weight()

def test_468_digital():
    check_ITU_R_468_weight(fs=180000)
