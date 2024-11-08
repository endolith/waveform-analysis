import os

import numpy as np
import pytest

from waveform_analysis._common import (analyze_channels, dB, find, load,
                                       parabolic, parabolic_polyfit, rms_flat)

# Get the test files directory
tests_dir = os.path.dirname(__file__)
test_files_dir = os.path.join(tests_dir, 'test_files')


class TestLoad:
    @pytest.mark.parametrize("filename, expected_sr, expected_channels", [
        ("1234 Hz -12.3 dB Ocenaudio 16-bit.wav", 48000, 1),
        ("test-44100Hz-2ch-32bit-float-be.wav", 44100, 2),
        ("test-8000Hz-le-2ch-1byteu.wav", 8000, 2),
    ])
    def test_load_returns_correct_format(self, filename, expected_sr,
                                         expected_channels):
        """
        Test that load() returns data in the expected format regardless of
        backend
        """
        filepath = os.path.join(test_files_dir, filename)
        soundfile = load(filepath)

        # Test dictionary contains required keys with correct values
        assert soundfile['fs'] == expected_sr
        assert soundfile['channels'] == expected_channels
        assert soundfile['samples'] > 0
        assert isinstance(soundfile['format'], str)

        # Test array shape contract: 1D for mono, 2D for multi-channel
        # This is a core part of load()'s specification, used by
        # analyze_channels and other functions
        assert soundfile['signal'].shape[0] == soundfile['samples']
        if expected_channels == 1:
            assert soundfile['signal'].ndim == 1
        else:
            assert soundfile['signal'].shape[1] == expected_channels

    def test_load_handles_invalid_files(self):
        """
        Test that load() raises appropriate errors for invalid files
        """
        try:
            from soundfile import LibsndfileError
            expected_error = LibsndfileError
        except ModuleNotFoundError:
            expected_error = IOError

        with pytest.raises(expected_error):
            load("nonexistent_file.wav")


class TestAnalyzeChannels:
    def test_analyze_channels_processes_all_channels(self):
        """
        Test that analyze_channels correctly processes mono and stereo files
        """
        results = []

        def dummy_analyzer(signal, fs):
            results.append((len(signal), fs))

        mono_file = os.path.join(
            test_files_dir, "1234 Hz -12.3 dB Ocenaudio 16-bit.wav")
        stereo_file = os.path.join(
            test_files_dir, "test-44100Hz-2ch-32bit-float-be.wav")

        # Test mono file
        results.clear()
        analyze_channels(mono_file, dummy_analyzer)
        assert len(results) == 1  # One channel processed

        # Test stereo file
        results.clear()
        analyze_channels(stereo_file, dummy_analyzer)
        assert len(results) >= 1  # At least one channel processed


class TestHelperFunctions:
    def test_rms_flat(self):
        """Test RMS calculation"""
        test_signal = np.array([1.0, -1.0, 1.0, -1.0])
        assert rms_flat(test_signal) == 1.0

        test_signal = np.array([1.0, 1.0, 1.0, 1.0])
        assert rms_flat(test_signal) == 1.0

    def test_find(self):
        """Test find() function"""
        condition = np.array([False, True, False, True])
        result = find(condition)
        assert np.array_equal(result, np.array([1, 3]))

    def test_dB(self):
        """Test dB conversion"""
        assert dB(1.0) == 0.0
        assert dB(0.5) == pytest.approx(-6.02, abs=0.01)
        assert np.isneginf(dB(0.0))

    def test_parabolic(self):
        """Test parabolic interpolation"""
        f = np.array([2, 3, 1, 6, 4, 2, 3, 1])
        x = 3  # Index of maximum
        xv, yv = parabolic(f, x)
        assert isinstance(xv, float)
        assert isinstance(yv, float)
        assert xv >= x-1 and xv <= x+1  # Interpolated x should be near peak

    def test_parabolic_polyfit(self):
        """Test parabolic fitting using polyfit"""
        f = np.array([2, 3, 1, 6, 4, 2, 3, 1])
        x = 3  # Index of maximum
        xv, yv = parabolic_polyfit(f, x, n=3)
        assert isinstance(xv, float)
        assert isinstance(yv, float)
        assert xv >= x-1 and xv <= x+1  # Fitted x should be near peak


if __name__ == '__main__':
    pytest.main([__file__, "-v"])
