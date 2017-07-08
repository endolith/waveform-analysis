import pytest
from scipy import signal
from scipy.interpolate import interp1d
import numpy as np
from numpy import pi

# This package must first be installed with `pip install -e .` or similar
from waveform_analysis import ABC_weighting, A_weighting, A_weight

# It will plot things for sanity-checking if MPL is installed
try:
    import matplotlib.pyplot as plt
    mpl = True
except ImportError:
    mpl = False


# ANSI S1.4-1983 Table AI "Exact frequency"
frequencies = np.array((10.00, 12.59, 15.85, 19.95, 25.12, 31.62, 39.81,
                        50.12, 65.10, 79.43, 100.00, 125.90, 158.50, 199.50,
                        251.20, 316.20, 398.10, 501.20, 631.00, 794.30,
                        1000.00, 1259.00, 1585.00, 1995.00, 2512.00, 3162.00,
                        3981.00, 5012.00, 6310.00, 7943.00, 10000.00,
                        12590.00, 15850.00, 19950.00, 25120.00, 31620.00,
                        39810.00, 50120.00, 63100.00, 79430.00, 100000.00,
                        ))

responses = {}

# ANSI S1.4-1983 Table AI "A weighting"
responses['A'] = np.array((-70.4, -63.4, -56.7, -50.5, -44.7, -39.4, -34.6,
                           -30.2, -26.2, -22.5, -19.1, -16.1, -13.4, -10.9,
                           -8.6, -6.6, -4.8, -3.2, -1.9, -0.8, 0.0, +0.6,
                           +1.0, +1.2, +1.3, +1.2, +1.0, +0.5, -0.1, -1.1,
                           -2.5, -4.3, -6.6, -9.3, -12.4, -15.8, -19.3, -23.1,
                           -26.9, -30.8, -34.7,
                           ))

# ANSI S1.4-1983 Table IV "B Weighting"
responses['B'] = np.array((-38.2, -33.2, -28.5, -24.2, -20.4, -17.1, -14.2,
                           -11.6, -9.3, -7.4, -5.6, -4.2, -3.0, -2.0, -1.3,
                           -0.8, -0.5, -0.3, -0.1, 0.0, 0.0, 0.0, 0.0, -0.1,
                           -0.2, -0.4, -0.7, -1.2, -1.9, -2.9, -4.3, -6.1,
                           -8.4, -11.1,
                           ))

# ANSI S1.4-1983 Table IV "C Weighting"
responses['C'] = np.array((-14.3, -11.2, -8.5, -6.2, -4.4, -3.0, -2.0, -1.3,
                           -0.8, -0.5, -0.3, -0.2, -0.1, 0.0, 0.0, 0.0, 0.0,
                           0.0, 0.0, 0.0, 0.0, 0.0, -0.1, -0.2, -0.3, -0.5,
                           -0.8, -1.3, -2.0, -3.0, -4.4, -6.2, -8.5, -11.2,
                           ))

# ANSI S1.4-1983 Table AII "Type 0"
# Stricter than IEC 61672-1 (2002) Table 2 Class 1 (±1.1 dB at 1 kHz)
upper_limits = np.array((+2.0, +2.0, +2.0, +2.0, +1.5, +1.0, +1.0, +1.0, +1.0,
                         +1.0, +0.7, +0.7, +0.7, +0.7, +0.7, +0.7, +0.7, +0.7,
                         +0.7, +0.7, +0.7, +0.7, +0.7, +0.7, +0.7, +0.7, +0.7,
                         +1.0, +1.0, +1.0, +2.0, +2.0, +2.0, +2.0, +2.4, +2.8,
                         +3.3, +4.1, +4.9, +5.1, +5.6,
                         ))

lower_limits = np.array((-5.0, -4.0, -3.0, -2.0, -1.5, -1.0, -1.0, -1.0, -1.0,
                         -1.0, -0.7, -0.7, -0.7, -0.7, -0.7, -0.7, -0.7, -0.7,
                         -0.7, -0.7, -0.7, -0.7, -0.7, -0.7, -0.7, -0.7, -0.7,
                         -1.0, -1.5, -2.0, -3.0, -3.0, -3.0, -3.0, -4.5, -6.2,
                         -7.9, -9.3, -10.9, -12.2, -14.3,
                         ))


class TestABCWeighting(object):
    def test_invalid_params(self):
        with pytest.raises(ValueError):
            ABC_weighting('D')

    def test_freq_resp(self):
        # Test that frequency response meets tolerance from ANSI S1.4-1983
        for curve in {'A', 'B', 'C'}:
            N = len(responses[curve])  # Number of frequencies in spec
            f_test = frequencies[:N]
            upper = responses[curve] + upper_limits[:N]
            lower = responses[curve] + lower_limits[:N]

            z, p, k = ABC_weighting(curve)
            w, h = signal.freqs_zpk(z, p, k, 2*pi*f_test)
            levels = 20 * np.log10(abs(h))

            if mpl:
                plt.figure(curve)
                plt.title('{}-weighting limits (Type 0)'.format(curve))
                plt.semilogx(f_test, levels, alpha=0.7, label='analog')
                plt.semilogx(f_test, upper, 'r:', alpha=0.7)
                plt.semilogx(f_test, lower, 'r:', alpha=0.7)
                plt.grid(True, color='0.7', linestyle='-', which='major')
                plt.grid(True, color='0.9', linestyle='-', which='minor')
                plt.legend()

            assert all(np.less_equal(levels, upper))
            assert all(np.greater_equal(levels, lower))


class TestAWeighting(object):
    def test_invalid_params(self):
        with pytest.raises(TypeError):
            A_weighting(fs='spam')

        with pytest.raises(ValueError):
            A_weighting(fs=10000, output='eggs')

    def test_zpkbilinear_bug(self):
        # https://github.com/scipy/scipy/pull/7504
        # Copied a local version and fixed it, but just to make sure:
        z, p, k = A_weighting(fs=48000, output='zpk')
        assert k != 0

    def test_freq_resp_ba(self):
        # Test that frequency response meets tolerance from ANSI S1.4-1983
        fs = 300000
        b, a = A_weighting(fs)
        w, h = signal.freqz(b, a, 2*pi*frequencies/fs)
        levels = 20 * np.log10(abs(h))

        if mpl:
            plt.figure('A')
            plt.semilogx(frequencies, levels, alpha=0.7, label='ba')
            plt.legend()

        assert all(np.less_equal(levels, responses['A'] + upper_limits))
        assert all(np.greater_equal(levels, responses['A'] + lower_limits))

    def test_freq_resp_zpk(self):
        # Test that frequency response meets tolerance from ANSI S1.4-1983
        fs = 270000
        z, p, k = A_weighting(fs, 'zpk')
        w, h = signal.freqz_zpk(z, p, k, 2*pi*frequencies/fs)
        levels = 20 * np.log10(abs(h))

        if mpl:
            plt.figure('A')
            plt.semilogx(frequencies, levels, alpha=0.7, label='zpk')
            plt.legend()

        assert all(np.less_equal(levels, responses['A'] + upper_limits))
        assert all(np.greater_equal(levels, responses['A'] + lower_limits))

    def test_freq_resp_sos(self):
        # Test that frequency response meets tolerance from ANSI S1.4-1983
        fs = 400000
        sos = A_weighting(fs, output='sos')
        w, h = signal.sosfreqz(sos, 2*pi*frequencies/fs)
        levels = 20 * np.log10(abs(h))

        if mpl:
            plt.figure('A')
            plt.semilogx(frequencies, levels, alpha=0.7, label='sos')
            plt.legend()

        assert all(np.less_equal(levels, responses['A'] + upper_limits))
        assert all(np.greater_equal(levels, responses['A'] + lower_limits))


class TestAWeight(object):
    def test_freq_resp(self):
        # Test that frequency response meets tolerance from ANSI S1.4-1983
        N = 40000
        fs = 300000
        impulse = signal.unit_impulse(N)
        out = A_weight(impulse, fs)
        freq = np.fft.rfftfreq(N, 1/fs)
        levels = 20 * np.log10(abs(np.fft.rfft(out)))

        if mpl:
            plt.figure('A')
            plt.semilogx(freq, levels, alpha=0.7, label='fft')
            plt.legend()
            plt.ylim(-80, +5)

        # Interpolate FFT points to measure response at spec's frequencies
        func = interp1d(freq, levels)
        levels = func(frequencies)
        assert all(np.less_equal(levels, responses['A'] + upper_limits))
        assert all(np.greater_equal(levels, responses['A'] + lower_limits))


if __name__ == '__main__':
    pytest.main([__file__])
