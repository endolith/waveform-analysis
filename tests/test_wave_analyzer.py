import os
import subprocess
import sys

import pytest

# Get the base directory for waveform-analysis project
tests_dir = os.path.dirname(__file__)
script_path = os.path.join(tests_dir, '..', 'scripts', 'wave_analyzer.py')
test_files_dir = os.path.join(tests_dir, 'test_files')


class TestWaveAnalyzer:
    def test_no_arguments(self):
        result = subprocess.run([sys.executable, script_path],
                                capture_output=True, text=True)
        assert result.returncode != os.EX_OK
        assert "the following arguments are required: filenames" in result.stderr

    def test_nonexistent_file(self):
        result = subprocess.run([sys.executable, script_path,
                                 "nonexistent.wav"],
                                capture_output=True, text=True)
        assert 'File not found: "nonexistent.wav"' in result.stdout

    def test_real_file(self):
        test_file_path = os.path.join(test_files_dir,
                                      '1234 Hz -12.3 dB Ocenaudio 16-bit.wav')

        result = subprocess.run([sys.executable, script_path, test_file_path],
                                capture_output=True, text=True)

        assert result.returncode == os.EX_OK


if __name__ == "__main__":
    pytest.main([__file__])
