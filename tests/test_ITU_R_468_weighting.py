import numpy as np
import pytest
from numpy import pi
from scipy import signal
from scipy.interpolate import interp1d

# This package must first be installed with `pip install -e .` or similar
from waveform_analysis import (ITU_R_468_weight, ITU_R_468_weighting,
                               ITU_R_468_weighting_analog)

# It will plot things for sanity-checking if MPL is installed
try:
    import matplotlib.pyplot as plt
    mpl = True
except ImportError:
    mpl = False

# Rec. ITU-R BS.468-4 Measurement of audio-frequency noise voltage
# level in sound broadcasting Table 1
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
    +0.01,  # Actually 0 tolerance, but specified with 1 significant figure
    +0.2, +0.4, +0.6, +0.8, +1.2, +1.4, +1.6, +2.0, +2.8
))

lower_limits = np.array((
    -2.0, -1.4, -1.0, -0.85, -0.7, -0.55, -0.5, -0.5, -0.5, -0.5, -0.5,
    -0.01,  # Actually 0 tolerance, but specified with 1 significant figure
    -0.2, -0.4, -0.6, -0.8, -1.2, -1.4, -1.6, -2.0, -float('inf')
))


class TestITU468WeightingAnalog:
    def test_invalid_params(self):
        with pytest.raises(TypeError):
            ITU_R_468_weighting_analog('eels')

    def test_freq_resp(self):
        # Test that frequency response meets tolerance from ITU-R BS.468-4
        upper = responses + upper_limits
        lower = responses + lower_limits

        z, p, k = ITU_R_468_weighting_analog()
        w, h = signal.freqs_zpk(z, p, k, 2*pi*frequencies)
        levels = 20 * np.log10(abs(h))

        if mpl:
            plt.figure('468')
            plt.title('ITU 468 weighting limits')
            plt.semilogx(frequencies, levels, alpha=0.7, label='analog')
            plt.semilogx(frequencies, upper, 'r:', alpha=0.7)
            plt.semilogx(frequencies, lower, 'r:', alpha=0.7)
            plt.grid(True, color='0.7', linestyle='-', which='major')
            plt.grid(True, color='0.9', linestyle='-', which='minor')
            plt.legend()

        assert all(np.less_equal(levels, upper))
        assert all(np.greater_equal(levels, lower))


class TestITU468Weighting:
    def test_invalid_params(self):
        with pytest.raises(ValueError):
            ITU_R_468_weighting(fs='spam')

        with pytest.raises(ValueError):
            ITU_R_468_weighting(fs=10000, output='eggs')

    def test_freq_resp_ba(self):
        # Test that frequency response meets tolerance from ITU-R BS.468-4
        fs = 300000
        b, a = ITU_R_468_weighting(fs)
        w, h = signal.freqz(b, a, 2*pi*frequencies/fs)
        levels = 20 * np.log10(abs(h))

        if mpl:
            plt.figure('468')
            plt.semilogx(frequencies, levels, alpha=0.7, label='ba')
            plt.legend()

        assert all(np.less_equal(levels, responses + upper_limits))
        assert all(np.greater_equal(levels, responses + lower_limits))

    def test_freq_resp_zpk(self):
        # Test that frequency response meets tolerance from ITU-R BS.468-4
        fs = 270000
        z, p, k = ITU_R_468_weighting(fs, 'zpk')
        w, h = signal.freqz_zpk(z, p, k, 2*pi*frequencies/fs)
        levels = 20 * np.log10(abs(h))

        if mpl:
            plt.figure('468')
            plt.semilogx(frequencies, levels, alpha=0.7, label='zpk')
            plt.legend()

        assert all(np.less_equal(levels, responses + upper_limits))
        assert all(np.greater_equal(levels, responses + lower_limits))

    def test_freq_resp_sos(self):
        # Test that frequency response meets tolerance from ITU-R BS.468-4
        fs = 400000
        sos = ITU_R_468_weighting(fs, output='sos')
        w, h = signal.sosfreqz(sos, 2*pi*frequencies/fs)
        levels = 20 * np.log10(abs(h))

        if mpl:
            plt.figure('468')
            plt.semilogx(frequencies, levels, alpha=0.7, label='sos')
            plt.legend()

        assert all(np.less_equal(levels, responses + upper_limits))
        assert all(np.greater_equal(levels, responses + lower_limits))


class TestITU468Weight:
    def test_invalid_params(self):
        with pytest.raises(TypeError):
            ITU_R_468_weight('change this')

    def test_freq_resp(self):
        # Test that frequency response meets tolerance from ITU-R BS.468-4
        N = 12000
        fs = 300000
        impulse = signal.unit_impulse(N)
        out = ITU_R_468_weight(impulse, fs)
        freq = np.fft.rfftfreq(N, 1/fs)
        levels = 20 * np.log10(abs(np.fft.rfft(out)))

        if mpl:
            plt.figure('468')
            plt.semilogx(freq, levels, alpha=0.7, label='fft')
            plt.legend()
            plt.axis([20, 45000, -50, +15])

        # Interpolate FFT points to measure response at spec's frequencies
        func = interp1d(freq, levels)
        levels = func(frequencies)
        assert all(np.less_equal(levels, responses + upper_limits))
        assert all(np.greater_equal(levels, responses + lower_limits))


if __name__ == '__main__':
    # Without capture sys it doesn't work sometimes, I'm not sure why.
    pytest.main([__file__, "--capture=sys"])
