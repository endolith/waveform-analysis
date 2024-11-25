import os
from glob import glob

import numpy as np
import pytest
from numpy import pi, sin
from scipy.io.wavfile import WavFileWarning, read
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


class TestTHDN:
    def test_invalid_params(self):
        # Invalid signal type
        with pytest.raises(TypeError):
            THDN(None)
            THD(None)

        # Invalid parameter name
        with pytest.raises(TypeError):
            THDN(np.array([1, 2]), sample_rate=50)
            THD(np.array([1, 2]), sample_rate=50)

        # Invalid weighting filter
        with pytest.raises(ValueError):
            signal = sine_wave(100, 1000)
            THDN(signal, 1000, weight='Q')

        # Invalid reference type
        with pytest.raises(ValueError):
            signal = sine_wave(100, 1000)
            THD(signal, 1000, ref='Q')

    def test_array_like(self):
        signal = [-1, 0, +1, +1, +1, 0, -1]*100
        assert THDN(signal, 1234) > 0
        assert THD(signal, 1234) > 0

    def test_sine(self):
        # TODO use non-easy signal lengths and frequencies, padding, etc.
        fs = 100000  # Hz
        f = 1000  # Hz
        signal = sine_wave(f, fs) + 0.75 * sine_wave(2*f, fs)
        # THDF of 75% = THDR of 75%/(sqrt(1+75%**2)) = 60%
        assert THDN(signal, fs) == pytest.approx(0.6)
        assert THD(signal, fs) == pytest.approx(0.75)  # THDF by default

        assert THD(signal, fs, ref='r') == pytest.approx(0.6)
        assert THD(signal, fs, ref='f') == pytest.approx(0.75)

    # TODO: parametrize test cases
    def test_sawtooth(self):
        # These won't be perfect because of aliasing
        # THDR is 62.6% (from conversion of THDF of 80.3% from Wikipedia)
        fs = 100000  # Hz
        f = 1000  # Hz
        signal = sawtooth_wave(f, fs)
        assert THDN(signal, fs) == pytest.approx(62.6/100, rel=0.001)

        # THDF is 80.3%
        fs = 100000  # Hz
        f = 10  # Hz
        signal = sawtooth_wave(f, fs)
        assert THD(signal, fs) == pytest.approx(80.3/100, rel=0.001)
        assert THD(signal, fs, ref='f') == pytest.approx(80.3/100, rel=0.001)
        assert THD(signal, fs, ref='r') == pytest.approx(62.6/100, rel=0.001)


    # Optional sanity tests with third-party wav files.  To avoid any issues
    # with copyright or repo size, these files are not committed.
    # https://web.archive.org/web/20111020022811/http://members.cox.net:80/artludwig
    @pytest.mark.parametrize("filename,thd", [
        ("440Hz.wav", 0.0),
        ("440SE.wav", 5.0),  # "The THD for the single-ended triode is 5%"
        ("440SS.wav", 0.5),  # "for the solid state THD is 0.5%"
    ])
    def test_art_ludwig_wav_files(self, filename, thd):
        full_path = os.path.join(os.path.dirname(__file__), "thd_files",
                                 filename)
        if not os.path.exists(full_path):
            pytest.skip(f"{filename} not found. Skipping test.")

        fs, channels = read(full_path)
        result = THDN(channels[:, 0], fs)  # Stereo files
        assert pytest.approx(result, rel=0.03, abs=0.00003) == thd/100

        result = THD(channels[:, 0], fs, ref='r')  # Stereo files
        assert pytest.approx(result, rel=0.03, abs=0.00003) == thd/100

    # https://www.audiocheck.net/testtones_thdFull.php (54 files)
    thd_files_path = os.path.join(os.path.dirname(__file__), "thd_files")
    audiocheck_files = glob(os.path.join(
        thd_files_path, "audiocheck.net_thd*.wav"))

    audiocheck_files_thd = []
    for filename in audiocheck_files:
        basename = os.path.basename(filename)
        parts = basename.split('_')
        frequency = float(parts[2])
        thd_str = parts[3].split('.')[0]
        thd = float(f"{thd_str[0]}.{thd_str[1:]}")
        audiocheck_files_thd.append((basename, thd))

    @pytest.mark.parametrize("filename, thd", audiocheck_files_thd)
    def test_audiocheck_wav_files(self, filename, thd):
        # If empty, parametrize will raise a warning instead.
        print(filename, thd)
        full_path = os.path.join(os.path.dirname(__file__), "thd_files",
                                 filename)

        with pytest.warns(WavFileWarning):
            fs, sig = read(full_path)
        result = THDN(sig, fs)  # Mono files
        assert pytest.approx(result, abs=0.0002) == thd/100

        result = THD(sig, fs, ref='r')  # Mono files
        assert pytest.approx(result, abs=0.0002) == thd/100

    def test_freq_parameter(self):
        fs = 48000  # Hz
        f = 1000  # Hz
        # Create a signal with known harmonics
        signal = sine_wave(f, fs) + 0.75 * sine_wave(2*f, fs)

        # Test that explicit frequency gives same results as auto-detection
        auto_thdn = THDN(signal, fs)
        explicit_thdn = THDN(signal, fs, freq=f)
        assert explicit_thdn == pytest.approx(auto_thdn)

        auto_thd = THD(signal, fs)
        explicit_thd = THD(signal, fs, freq=f)
        assert explicit_thd == pytest.approx(auto_thd)


if __name__ == '__main__':
    pytest.main([__file__, "--capture=sys"])
