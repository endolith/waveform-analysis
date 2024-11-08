import os
import re
import subprocess
import sys

import pytest

from waveform_analysis._common import wav_loader

# Get the base directory for waveform-analysis project
tests_dir = os.path.dirname(__file__)
script_path = os.path.join(tests_dir, '..', 'scripts', 'wave_analyzer.py')
test_files_dir = os.path.join(tests_dir, 'test_files')


def run_wave_analyzer(filename=None, extra_args=[]):
    cmd = [sys.executable, script_path]
    if filename:
        cmd.append(os.path.join(test_files_dir, filename))
    cmd.extend(extra_args)
    return subprocess.run(cmd, capture_output=True, text=True)


class TestWaveAnalyzer:
    @pytest.mark.parametrize("filename, expected_fs, expected_ch", [
        ("1234 Hz -12.3 dB Ocenaudio 16-bit.wav", 48000, 1),
        ("1234 Hz -12.3 dB Ocenaudio 24-bit.wav", 44100, 1),
        ("test-44100Hz-le-1ch-4bytes.wav", 44100, 1),
        ("test-44100Hz-2ch-32bit-float-le.wav", 44100, 2),
        ("test-44100Hz-le-1ch-4bytes-early-eof.wav", 44100, 1),
        ("test-8000Hz-le-4ch-9S-12bit.wav", 8000, 4),
        ("test-8000Hz-le-3ch-5S-24bit.wav", 8000, 3),
        ("test-8000Hz-le-2ch-1byteu.wav", 8000, 2),
        ("test-1234Hz-le-1ch-10S-20bit-extra.wav", 1234, 1),
        ("test-8000Hz-le-5ch-9S-5bit.wav", 8000, 5),  # but is level correct?
        ("test-48000Hz-2ch-64bit-float-le-wavex.wav", 48000, 2),  # float64
        ("test-8000Hz-be-3ch-5S-24bit.wav", 8000, 3),  # >i4
        ("test-44100Hz-be-1ch-4bytes.wav", 44100, 1),  # >i4
        ("test-44100Hz-2ch-32bit-float-be.wav", 44100, 2),  # >f4
    ])
    def test_common_files(self, filename, expected_fs, expected_ch):
        result = run_wave_analyzer(filename)
        assert result.returncode == os.EX_OK
        assert f"Sampling rate:\t{expected_fs} Hz" in result.stdout
        assert f"Channels:\t{expected_ch}" in result.stdout

    @pytest.mark.skipif(wav_loader != 'pysoundfile',
                        reason="Requires pysoundfile backend")
    @pytest.mark.parametrize("filename, expected_fs, expected_ch", [
        ("short_sine.mp3", 44100, 2),  # Only in v0.11.0 or later
        ("short_sine.flac", 44100, 2),
        ("test-8000Hz-le-3ch-5S-24bit-inconsistent.wav", 8000, 3),
        ("test-8000Hz-le-1ch-1byte-ulaw.wav", 8000, 1),
    ])
    def test_pysoundfile_only_files(self, filename, expected_fs, expected_ch):
        result = run_wave_analyzer(filename)
        assert result.returncode == os.EX_OK
        assert f"Sampling rate:\t{expected_fs} Hz" in result.stdout
        assert f"Channels:\t{expected_ch}" in result.stdout

    @pytest.mark.skipif(wav_loader != 'scipy.io.wavfile',
                        reason="Requires scipy backend")
    @pytest.mark.parametrize("filename, expected_fs, expected_ch", [
        ("test-8000Hz-le-3ch-5S-64bit.wav", 8000, 3),
        ("test-8000Hz-le-3ch-5S-53bit.wav", 8000, 3),
        ("test-8000Hz-le-3ch-5S-45bit.wav", 8000, 3),
        ("test-8000Hz-le-3ch-5S-36bit.wav", 8000, 3),
    ])
    def test_scipy_only_files(self, filename, expected_fs, expected_ch):
        result = run_wave_analyzer(filename)
        assert result.returncode == os.EX_OK
        assert f"Sampling rate:\t{expected_fs} Hz" in result.stdout
        assert f"Channels:\t{expected_ch}" in result.stdout

    @pytest.mark.parametrize("filename, expected_peak", [
        ("1234 Hz -12.3 dB Ocenaudio 16-bit.wav", -12.3456),
        ("1234 Hz -12.3 dB Ocenaudio 24-bit.wav", -12.3456),
        ("test-44100Hz-le-1ch-4bytes.wav", -3.01),
        ("test-44100Hz-2ch-32bit-float-le.wav", -1.94),
        ("test-44100Hz-le-1ch-4bytes-early-eof.wav", -3.01),
        ("test-8000Hz-le-2ch-1byteu.wav", -3.01),
        ("test-48000Hz-2ch-64bit-float-le-wavex.wav", -1.94),
    ])
    def test_correctness(self, filename, expected_peak):
        # Test some sine wave files for correct peak levels
        # Short length of sine waves ruins accuracy because of DC offset
        result = run_wave_analyzer(filename)
        assert result.returncode == os.EX_OK

        peak_pattern = r"Peak level:.*\(([-\d.]+) dBFS\)"
        rms_pattern = r"RMS level:.*\(([-\d.]+) dBFS\)"
        crest_pattern = r"Crest factor:.*\(([-\d.]+) dB\)"

        peak_match = re.search(peak_pattern, result.stdout)
        rms_match = re.search(rms_pattern, result.stdout)
        crest_match = re.search(crest_pattern, result.stdout)

        peak_db = float(peak_match.group(1))
        rms_db = float(rms_match.group(1))
        crest_factor_db = float(crest_match.group(1))

        """
        AES17-1998:

        3.3
        full-scale amplitude
        amplitude of a 997-Hz sine wave whose positive peak value reaches the
        positive digital full scale, leaving the negative maximum code unused.

        3.3.1
        decibels, full scale
        dB FS
        amplitude expressed as a level in decibels relative to full-scale
        amplitude (20 times the common logarithm of the amplitude over the
        full-scale amplitude)

        So the dBFS level should be 0 for a full-scale sine wave, whether
        peak or RMS.
        """
        assert peak_db == pytest.approx(expected_peak, abs=0.6)
        assert rms_db == pytest.approx(expected_peak, abs=0.6)

        # These are all sine waves, which always have crest factor of 3 dB.
        assert crest_factor_db == pytest.approx(3.01029995663, abs=0.6)

    @pytest.mark.parametrize("filename, expected_level", [
        ("test-44100Hz-le-1ch-4bytes.wav", -3.01),
        ("test-8000Hz-le-2ch-1byteu.wav", -3.01),
        ("test-44100Hz-le-1ch-4bytes-early-eof.wav", -3.01),
    ])
    def test_a_weighting_1khz(self, filename, expected_level):
        """Test that A-weighted RMS matches unweighted RMS for 1 kHz sine waves"""
        result = run_wave_analyzer(filename)
        assert result.returncode == os.EX_OK

        rms_pattern = r"RMS level:.*\(([-\d.]+) dBFS\)"
        a_weighted_pattern = r"RMS A-weighted:.*\(([-\d.]+) dBFS\(A\)"

        rms_match = re.search(rms_pattern, result.stdout)
        a_weighted_match = re.search(a_weighted_pattern, result.stdout)

        rms_db = float(rms_match.group(1))
        a_weighted_db = float(a_weighted_match.group(1))

        # At 1 kHz, A-weighting should match unweighted, no 3 dB offset
        # (Wider tolerance due to short file length)
        assert a_weighted_db == pytest.approx(rms_db, abs=0.3)

    @pytest.mark.parametrize("filename, expected_level, freq", [
        ("test-44100Hz-be-1ch-4bytes.wav", -3.01, 1000),  # 1 kHz reference
        ("test-44100Hz-le-1ch-4bytes.wav", -3.01, 1000),  # 1 kHz reference
        ("test-8000Hz-le-2ch-1byteu.wav", -3.01, 1000),   # 1 kHz reference
        ("1234 Hz -12.3 dB Ocenaudio 16-bit.wav", -12.3456, 1234),
        ("1234 Hz -12.3 dB Ocenaudio 24-bit.wav", -12.3456, 1234),
    ])
    def test_itu_r_468_weighting(self, filename, expected_level, freq):
        """Test ITU-R 468-weighted RMS matches expected values"""
        result = run_wave_analyzer(filename)
        assert result.returncode == os.EX_OK

        rms_pattern = r"RMS level:.*\(([-\d.]+) dBFS\)"
        itu_weighted_pattern = r"RMS 468-weighted:.*\(([-\d.]+) dBFS\(468\)"

        rms_match = re.search(rms_pattern, result.stdout)
        itu_weighted_match = re.search(itu_weighted_pattern, result.stdout)

        rms_db = float(rms_match.group(1))
        itu_weighted_db = float(itu_weighted_match.group(1))

        if freq == 1000:
            # At 1 kHz, ITU-R 468 weighting should match unweighted
            assert itu_weighted_db == pytest.approx(rms_db, abs=0.6)
        else:
            # At 1234 Hz, ITU-R 468 weighting is +1.31 dB (interpolated from
            # Wikipedia table)
            weighting = 5.6 * (freq - 1000) / 1000  # Linear interpolation
            assert itu_weighted_db == pytest.approx(rms_db + weighting,
                                                    abs=0.6)

    @pytest.mark.parametrize("filename", [
        "test-44100Hz-le-1ch-4bytes-incomplete-chunk.wav",
        "test-44100Hz-le-1ch-4bytes-early-eof-no-data.wav",
    ])
    def test_invalid_audio_file(self, filename):
        result = run_wave_analyzer(filename)
        assert result.returncode != os.EX_OK
        assert any(msg in result.stderr for msg in [
                   "Invalid audio file", "Error in WAV file"])

    @pytest.mark.parametrize("filename", [
    ])
    def test_unsupported(self, filename):
        result = run_wave_analyzer(filename)
        assert result.returncode != os.EX_OK
        assert "Unexpected error analyzing" in result.stderr

    def test_no_arguments(self):
        result = run_wave_analyzer()
        assert result.returncode != os.EX_OK
        assert "following arguments are required: filenames" in result.stderr

    def test_nonexistent_file(self):
        result = run_wave_analyzer("nonexistent.wav")
        assert result.returncode != os.EX_OK
        assert any(msg in result.stderr for msg in [
            "File not found",
            "Error opening"
        ])
        assert "nonexistent.wav" in result.stderr

    def test_help_option(self):
        result = run_wave_analyzer("", extra_args=["--help"])
        assert result.returncode == os.EX_OK
        assert "usage:" in result.stdout
        assert "--gui" in result.stdout


if __name__ == "__main__":
    pytest.main([__file__, "-x"])  # Stop after first failure
