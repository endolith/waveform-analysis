import os
import subprocess
import sys

import pytest

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
    def test_no_arguments(self):
        result = run_wave_analyzer()
        assert result.returncode != os.EX_OK
        assert "the following arguments are required: filenames" in result.stderr

    def test_nonexistent_file(self):
        result = run_wave_analyzer("nonexistent.wav")
        assert any(msg in result.stdout for msg in [
            "File not found",
            "Error opening"
        ])
        assert "nonexistent.wav" in result.stdout

    def test_real_file(self):
        result = run_wave_analyzer('1234 Hz -12.3 dB Ocenaudio 16-bit.wav')
        assert result.returncode == os.EX_OK


if __name__ == "__main__":
    pytest.main([__file__])
