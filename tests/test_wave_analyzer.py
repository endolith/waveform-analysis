import os
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
        ("test-44100Hz-le-1ch-4bytes.wav", 44100, 1),
        ("test-44100Hz-2ch-32bit-float-le.wav", 44100, 2),
        ("test-44100Hz-le-1ch-4bytes-early-eof.wav", 44100, 1),
        ("test-8000Hz-le-4ch-9S-12bit.wav", 8000, 4),
        ("test-8000Hz-le-3ch-5S-24bit.wav", 8000, 3),
        ("test-8000Hz-le-2ch-1byteu.wav", 8000, 2),
        ("test-1234Hz-le-1ch-10S-20bit-extra.wav", 1234, 1),
        ("test-8000Hz-le-5ch-9S-5bit.wav", 8000, 5),  # but is level correct?
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
        # could work in scipy though:
        ("test-8000Hz-be-3ch-5S-24bit.wav", 8000, 3),
        ("test-48000Hz-2ch-64bit-float-le-wavex.wav", 48000, 2),
        ("test-44100Hz-be-1ch-4bytes.wav", 44100, 1),
        ("test-44100Hz-2ch-32bit-float-be.wav", 44100, 2),
    ])
    def test_pysoundfile_only_files(self, filename, expected_fs, expected_ch):
        result = run_wave_analyzer(filename)
        assert result.returncode == os.EX_OK
        assert f"Sampling rate:\t{expected_fs} Hz" in result.stdout
        assert f"Channels:\t{expected_ch}" in result.stdout

    @pytest.mark.parametrize("filename", [
        "test-44100Hz-le-1ch-4bytes-incomplete-chunk.wav",
        "test-44100Hz-le-1ch-4bytes-early-eof-no-data.wav",
        # Supported by neither, but could be made to work in scipy:
        "test-8000Hz-le-3ch-5S-64bit.wav",  # 8000, 3),
        "test-8000Hz-le-3ch-5S-53bit.wav",  # 8000, 3),
        "test-8000Hz-le-3ch-5S-45bit.wav",  # 8000, 3),
        "test-8000Hz-le-3ch-5S-36bit.wav",  # 8000, 3),
    ])
    def test_invalid_files(self, filename):
        result = run_wave_analyzer(filename)
        # assert result.returncode != os.EX_OK
        assert "rror" in result.stdout

    def test_no_arguments(self):
        result = run_wave_analyzer()
        assert result.returncode != os.EX_OK
        assert "following arguments are required: filenames" in result.stderr

    def test_nonexistent_file(self):
        result = run_wave_analyzer("nonexistent.wav")
        # assert result.returncode != os.EX_OK
        assert any(msg in result.stdout for msg in [
            "File not found",
            "Error opening"
        ])
        assert "nonexistent.wav" in result.stdout

    def test_help_option(self):
        result = run_wave_analyzer("", extra_args=["--help"])
        assert result.returncode == os.EX_OK
        assert "usage:" in result.stdout
        assert "--gui" in result.stdout


if __name__ == "__main__":
    pytest.main([__file__])
