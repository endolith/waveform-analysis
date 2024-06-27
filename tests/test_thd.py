import numpy as np
import pytest
from numpy import pi, sin
from scipy.signal import sawtooth

# This package must first be installed with `pip install -e .` or similar
from waveform_analysis.thd import THD, THDN


def sine_wave(f, fs):
    """
    Generate 1 second of sine wave at f frequency sampled at fs rate
    """
    t = np.linspace(0, 1, fs, endpoint=False)
    return sin(2*pi * f * t)


def sawtooth_wave(f, fs):
    """
    Generate 1 second of sine wave at f frequency sampled at fs rate
    """
    t = np.linspace(0, 1, fs, endpoint=False)
    return sawtooth(2*pi * f * t)


class TestTHDN(object):
    def test_invalid_params(self):
        # Invalid signal type
        with pytest.raises(TypeError):
            THDN(None)

        # Invalid parameter name
        with pytest.raises(TypeError):
            THDN(np.array([1, 2]), sample_rate=50)

#    def test_array_like(self):
#        freq_from_crossings([-1, +1, -1, +1], 10)
#
    def test_sine(self):
        # TODO use non-easy signal lengths and frequencies
        # padding, etc.
        fs = 100000  # Hz
        f = 1000  # Hz
        signal = sine_wave(f, fs) + 0.1 * sine_wave(2*f, fs)
        assert THDN(signal, fs) == pytest.approx(0.1, rel=1e-2)
        # TODO: Tighten tolerances

#    def test_interp(self):
#        fs = 100000  # Hz
#        f = 1234.56789  # Hz
#        signal = sine_wave(f, fs)
#        correct = pytest.approx(f)
#        assert freq_from_crossings(signal, fs, interp='none') == correct
#        assert freq_from_crossings(signal, fs, interp=None) == correct


if __name__ == '__main__':
    pytest.main([__file__, "--capture=sys"])
