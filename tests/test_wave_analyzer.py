import os
import subprocess
import sys

import pytest


class TestWaveAnalyzer:
    def setup_method(self):
        self.script_path = os.path.join(os.path.dirname(
            __file__), '..', 'scripts', 'wave_analyzer.py')

    def test_no_arguments(self):
        result = subprocess.run([sys.executable, self.script_path],
                                capture_output=True, text=True)
        assert result.returncode != 0
        assert "the following arguments are required: filenames" in result.stderr

    def test_nonexistent_file(self):
        result = subprocess.run([sys.executable, self.script_path,
                                 "nonexistent.wav"],
                                capture_output=True, text=True)
        assert 'File not found: "nonexistent.wav"' in result.stdout

    def test_real_file(self):
        test_file_path = os.path.join(os.path.dirname(__file__), 'test_files',
                                      '1234 Hz -12.3 dB Ocenaudio 16-bit.wav')

        result = subprocess.run([sys.executable, self.script_path,
                                 test_file_path],
                                capture_output=True, text=True)

        assert result.returncode == 0


if __name__ == "__main__":
    pytest.main([__file__])
