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
        thd = float(thd_str[0] + '.' + thd_str[1:])
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


if __name__ == '__main__':
    pytest.main([__file__, "--capture=sys"])
