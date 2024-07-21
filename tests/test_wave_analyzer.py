import pytest

from scripts.wave_analyzer import wave_analyzer


def test_wave_analyzer_no_args(capsys):
    with pytest.raises(SystemExit) as excinfo:
        wave_analyzer([])
    assert "You must provide at least one file to analyze:" in str(
        excinfo.value)
    assert "python wave_analyzer.py filename.wav" in str(excinfo.value)


if __name__ == "__main__":
    pytest.main([__file__])
