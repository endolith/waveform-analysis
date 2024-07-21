import os
import subprocess
import sys

import pytest


def test_wave_analyzer_command_line():
    script_path = os.path.join(os.path.dirname(
        __file__), '..', 'scripts', 'wave_analyzer.py')
    result = subprocess.run([sys.executable, script_path],
                            capture_output=True, text=True)
    assert result.returncode != 0
    assert "You must provide at least one file to analyze:" in result.stderr


def test_wave_analyzer_command_line_nonexistent_file():
    script_path = os.path.join(os.path.dirname(
        __file__), '..', 'scripts', 'wave_analyzer.py')
    result = subprocess.run(
        [sys.executable, script_path, "nonexistent.wav"], capture_output=True,
        text=True)
    assert "Couldn't analyze \"nonexistent.wav\"" in result.stdout


if __name__ == "__main__":
    pytest.main([__file__])
