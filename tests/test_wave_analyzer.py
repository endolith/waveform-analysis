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
        assert "You must provide at least one file to analyze:" in result.stderr

    def test_nonexistent_file(self):
        result = subprocess.run(
            [sys.executable, self.script_path, "nonexistent.wav"],
            capture_output=True, text=True)
        assert "Couldn't analyze \"nonexistent.wav\"" in result.stdout


if __name__ == "__main__":
    pytest.main([__file__])
