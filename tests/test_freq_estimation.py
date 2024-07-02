import numpy as np
import pytest
from numpy import pi, sin
from scipy.signal import sawtooth

# This package must first be installed with `pip install -e .` or similar
from waveform_analysis.freq_estimation import (freq_from_autocorr,
                                               freq_from_crossings,
                                               freq_from_fft, freq_from_hps)


def sine_wave(f, fs):
    """
    Generate 1 second of sine wave at f frequency sampled at fs rate
    """
    t = np.linspace(0, 1, fs, endpoint=False)
    return sin(2*pi * f * t)


def sawtooth_wave(f, fs):
    """
    Generate 1 second of sawtooth wave at f frequency sampled at fs rate
    """
    t = np.linspace(0, 1, fs, endpoint=False)
    return sawtooth(2*pi * f * t)


class TestFreqFromCrossings:
    def test_invalid_params(self):
        with pytest.raises(TypeError):
            freq_from_crossings(None)

        with pytest.raises(TypeError):
            freq_from_crossings(np.array([-2, 2, -1, 1]), fs='eggs')

        with pytest.raises(ValueError):
            freq_from_crossings(np.array([1, 2]), fs=40, interp='cubic')

    def test_array_like(self):
        signal = [-1, 0, +1, 0, -1, 0, +1, 0]
        assert freq_from_crossings(signal, 8) == pytest.approx(2)

    @pytest.mark.parametrize("fs", (48000, 44100))  # Hz
    @pytest.mark.parametrize("f", (1000, 1234.56789, 3000))  # Hz
    def test_sine(self, fs, f):
        signal = sine_wave(f, fs)
        assert freq_from_crossings(signal, fs) == pytest.approx(f)

    @pytest.mark.parametrize("interp", ('none', None, 'linear'))
    def test_interp(self, interp):
        fs = 100000  # Hz
        f = 1234.56789  # Hz
        signal = sine_wave(f, fs)
        correct = pytest.approx(f)
        assert freq_from_crossings(signal, fs, interp=interp) == correct


class TestFreqFromFFT:
    def test_invalid_params(self):
        with pytest.raises(TypeError):
            freq_from_fft(None)

        with pytest.raises(TypeError):
            freq_from_fft(np.array([1, 2]), fs='eggs')

    def test_array_like(self):
        signal = [-1, 0, +1, 0, -1, 0, +1, 0]
        assert freq_from_fft(signal, 8) == pytest.approx(2)

    @pytest.mark.parametrize("fs", (48000, 44100))  # Hz
    @pytest.mark.parametrize("f", (1000, 1234.56789, 3000))  # Hz
    def test_sine(self, fs, f):
        signal = sine_wave(f, fs)
        assert freq_from_fft(signal, fs) == pytest.approx(f)


class TestFreqFromAutocorr:
    def test_invalid_params(self):
        with pytest.raises(TypeError):
            freq_from_autocorr(None)

    @pytest.mark.parametrize("fs", (100000,))  # Hz
    @pytest.mark.parametrize("f", (1000, 1234.56789))  # Hz
    def test_sine(self, fs, f):
        signal = sine_wave(f, fs)
        assert freq_from_autocorr(signal, fs) == pytest.approx(f, rel=1e-4)


class TestFreqFromHPS:
    def test_invalid_params(self):
        with pytest.raises(TypeError):
            freq_from_hps(None)

    @pytest.mark.parametrize("fs", (48000, 100000))  # Hz
    @pytest.mark.parametrize("f", (1000, 1234.56789, 3000))  # Hz
    def test_sawtooth(self, fs, f):
        signal = sawtooth_wave(f, fs)
        assert freq_from_hps(signal, fs) == pytest.approx(f, rel=1e-4)


if __name__ == '__main__':
    pytest.main([__file__, "--capture=sys"])
