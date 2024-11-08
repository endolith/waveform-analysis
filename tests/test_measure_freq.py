import os
import re
import subprocess
import sys

import pytest

# Get the base directory for waveform-analysis project
tests_dir = os.path.dirname(__file__)
script_path = os.path.join(tests_dir, '..', 'scripts', 'measure_freq.py')
test_files_dir = os.path.join(tests_dir, 'test_files')


def run_measure_freq(filename="", extra_args=None):
    """Helper function to run measure_freq.py with given arguments"""
    if extra_args is None:
        extra_args = []

    args = [sys.executable, script_path]

    if filename:
        filepath = os.path.join(test_files_dir, filename)
        args.append(filepath)

    # Convert extra_args to full paths if they're filenames
    full_path_args = [
        os.path.join(test_files_dir, arg) if arg.endswith('.wav') else arg
        for arg in extra_args
    ]
    args.extend(full_path_args)

    result = subprocess.run(
        args,
        capture_output=True,
        text=True
    )
    return result


class TestMeasureFreq:
    @pytest.mark.parametrize("filename, expected_freq", [
        ("1234 Hz -12.3 dB Ocenaudio 16-bit.wav", 1234),
        ("test-44100Hz-le-1ch-4bytes.wav", 1000),  # 1kHz reference
    ])
    def test_frequency_measurement(self, filename, expected_freq):
        """Test that frequency measurement is accurate"""
        result = run_measure_freq(filename)
        assert result.returncode == 0

        # Extract frequency from output
        freq_match = re.search(r'(\d+\.?\d*) Hz', result.stdout)
        assert freq_match is not None
        measured_freq = float(freq_match.group(1))
        assert measured_freq == pytest.approx(expected_freq, rel=0.01)

    def test_no_arguments(self):
        """Test error message when no files provided"""
        result = run_measure_freq()
        assert result.returncode != 0
        assert "You must provide at least one file to analyze" in result.stderr

    def test_nonexistent_file(self):
        """Test error handling for nonexistent file"""
        result = run_measure_freq("nonexistent.wav")
        # Check for either error message depending on backend
        assert any(msg in result.stdout for msg in [
            "Error opening",
            "Couldn't analyze"
        ])

    def test_multiple_files(self):
        """Test analyzing multiple files"""
        files = [
            "1234 Hz -12.3 dB Ocenaudio 16-bit.wav",
            "test-44100Hz-le-1ch-4bytes.wav"
        ]
        # Pass files as separate arguments
        result = run_measure_freq(extra_args=files)
        assert result.returncode == 0

        # Count only frequency measurement lines (ends with Hz)
        freq_lines = [line for line in result.stdout.splitlines()
                     if line.strip().endswith('Hz')]
        assert len(freq_lines) == 2  # Two frequency measurements

        assert result.stdout.count("Time elapsed:") == 2  # Two timing reports
