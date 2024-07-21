import os
import subprocess
import sys

import pytest


sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))

from scripts.wave_analyzer import wave_analyzer


def test_wave_analyzer_no_args(capsys):
    with pytest.raises(SystemExit) as excinfo:
        wave_analyzer([])
    assert "You must provide at least one file to analyze:" in str(
        excinfo.value)
    assert "python wave_analyzer.py filename.wav" in str(excinfo.value)


def test_wave_analyzer_nonexistent_file(capsys):
    wave_analyzer(["nonexistent.wav"])
    captured = capsys.readouterr()
    assert "Couldn't analyze \"nonexistent.wav\"" in captured.out


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
