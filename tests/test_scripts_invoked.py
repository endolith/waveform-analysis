"""
Exercise ``scripts/`` modules by import and ``runpy`` so they are covered under
``--cov=scripts`` without relying on coverage in child processes.
"""

import importlib.util
import os
import runpy
import sys
import tempfile
import types
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from subprocess_helpers import REPO_ROOT


def _load_script(unique_name, relpath):
    path = os.path.join(REPO_ROOT, relpath)
    spec = importlib.util.spec_from_file_location(unique_name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


tests_dir = os.path.dirname(__file__)
test_wav = os.path.join(tests_dir, 'test_files', 'test-44100Hz-le-1ch-4bytes.wav')


class TestMeasureFreqScript:
    def test_freq_wrapper_prints(self, capsys):
        mod = _load_script('measure_freq_script', 'scripts/measure_freq.py')
        fs = 48000
        t = np.linspace(0, 1, num=fs, endpoint=False)
        sig = np.sin(2 * np.pi * 1000 * t)
        mod.freq_wrapper(sig, fs)
        assert 'Hz' in capsys.readouterr().out

    def test_main_no_files_exits(self):
        script = os.path.join(REPO_ROOT, 'scripts', 'measure_freq.py')
        with patch('sys.stdout.isatty', return_value=False):
            with patch('sys.argv', ['measure_freq.py']):
                with pytest.raises(SystemExit):
                    runpy.run_path(script, run_name='__main__')


class TestThdAnalyzerScript:
    def test_thd_wrapper_prints(self, capsys):
        mod = _load_script('thd_analyzer_script', 'scripts/thd_analyzer.py')
        fs = 48000
        t = np.linspace(0, 1, num=fs, endpoint=False)
        sig = np.sin(2 * np.pi * 1000 * t)
        mod.thd_wrapper(sig, fs)
        out = capsys.readouterr().out
        assert 'THD+N' in out and 'THD(F)' in out

    def test_thd_analyzer_empty_exits(self):
        mod = _load_script('thd_analyzer_script2', 'scripts/thd_analyzer.py')
        with pytest.raises(SystemExit):
            mod.thd_analyzer([])

    def test_thd_analyzer_with_wav(self, capsys):
        mod = _load_script('thd_analyzer_script3', 'scripts/thd_analyzer.py')
        mod.thd_analyzer([test_wav])
        assert 'THD+N' in capsys.readouterr().out

    def test_thd_analyzer_ioerror_per_file(self, capsys):
        mod = _load_script('thd_analyzer_io', 'scripts/thd_analyzer.py')
        with patch.object(mod, 'analyze_channels', side_effect=IOError()):
            mod.thd_analyzer([test_wav])
        assert "Couldn't analyze" in capsys.readouterr().out


class TestWaveAnalyzerScript:
    def test_wave_analyzer_nonexistent_file(self):
        with patch('importlib.util.find_spec', return_value=None):
            mod = _load_script('wave_analyzer_nf', 'scripts/wave_analyzer.py')
        with pytest.raises(SystemExit) as exc:
            mod.wave_analyzer(['/nonexistent/path/does-not-exist.wav'],
                              gui=False)
        msg = str(exc.value)
        assert 'File not found' in msg or 'I/O error' in msg

    def test_wave_analyzer_invalid_wav(self):
        bad = os.path.join(
            tests_dir, 'test_files',
            'test-44100Hz-le-1ch-4bytes-incomplete-chunk.wav')
        with patch('importlib.util.find_spec', return_value=None):
            mod = _load_script('wave_analyzer_inv', 'scripts/wave_analyzer.py')
        with pytest.raises(SystemExit) as exc:
            mod.wave_analyzer([bad], gui=False)
        msg = str(exc.value)
        assert 'Invalid audio file' in msg or 'I/O error' in msg

    def test_analyze_stereo_different_channels(self, capsys):
        stereo = os.path.join(
            tests_dir, 'test_files', 'test-8000Hz-le-2ch-1byteu.wav')
        with patch('importlib.util.find_spec', return_value=None):
            mod = _load_script('wave_analyzer_st', 'scripts/wave_analyzer.py')
        mod.analyze(stereo, gui=False)
        out = capsys.readouterr().out
        assert 'Left channel' in out and 'Right channel' in out

    def test_analyze_stereo_identical_channels(self, capsys):
        stereo = os.path.join(
            tests_dir, 'test_files', 'test-44100Hz-2ch-32bit-float-be.wav')
        with patch('importlib.util.find_spec', return_value=None):
            mod = _load_script('wave_analyzer_stid', 'scripts/wave_analyzer.py')
        mod.analyze(stereo, gui=False)
        out = capsys.readouterr().out
        assert 'identical' in out.lower()

    @pytest.mark.filterwarnings('ignore::RuntimeWarning')
    def test_analyze_multichannel(self, capsys):
        quad = os.path.join(
            tests_dir, 'test_files', 'test-8000Hz-le-4ch-9S-12bit.wav')
        with patch('importlib.util.find_spec', return_value=None):
            mod = _load_script('wave_analyzer_4ch', 'scripts/wave_analyzer.py')
        mod.analyze(quad, gui=False)
        out = capsys.readouterr().out
        assert 'Channel 1' in out and 'Channel 4' in out

    def test_wave_analyzer_no_files(self):
        with patch('importlib.util.find_spec', return_value=None):
            mod = _load_script('wave_analyzer_nof', 'scripts/wave_analyzer.py')
        with pytest.raises(SystemExit, match='at least one file'):
            mod.wave_analyzer([], gui=False)

    def test_wave_analyzer_unexpected_error(self):
        with patch('importlib.util.find_spec', return_value=None):
            mod = _load_script('wave_analyzer_unexp', 'scripts/wave_analyzer.py')
        with patch.object(mod, 'analyze', side_effect=RuntimeError('boom')):
            with pytest.raises(SystemExit, match='Unexpected error'):
                mod.wave_analyzer([test_wav], gui=False)

    def test_wave_analyzer_io_error(self):
        with patch('importlib.util.find_spec', return_value=None):
            mod = _load_script('wave_analyzer_io', 'scripts/wave_analyzer.py')
        with patch.object(mod, 'load', side_effect=IOError('read fail')):
            with pytest.raises(SystemExit, match='I/O error'):
                mod.wave_analyzer([test_wav], gui=False)

    def test_analyze_seconds_length_line(self, capsys):
        long_wav = os.path.join(
            tests_dir, 'test_files', 'test-1234Hz-le-1ch-10S-20bit-extra.wav')
        with patch('importlib.util.find_spec', return_value=None):
            mod = _load_script('wave_analyzer_len', 'scripts/wave_analyzer.py')
        mod.analyze(long_wav, gui=False)
        assert 'seconds' in capsys.readouterr().out

    def test_display_with_easygui(self):
        eg = MagicMock()
        eg.codebox = MagicMock()
        with patch.dict(sys.modules, {'easygui': eg}):
            with patch('importlib.util.find_spec', return_value=MagicMock()):
                mod = _load_script('wave_analyzer_eg', 'scripts/wave_analyzer.py')
        mod.display('Hdr', ['r1'], gui=True)
        eg.codebox.assert_called_once()

    def test_wave_analyzer_one_file(self, capsys):
        with patch('importlib.util.find_spec', return_value=None):
            mod = _load_script('wave_analyzer_cli', 'scripts/wave_analyzer.py')
        mod.wave_analyzer([test_wav], gui=False)
        out = capsys.readouterr().out
        assert '44100' in out

    def test_display_gui_without_easygui(self, capsys):
        with patch('importlib.util.find_spec', return_value=None):
            mod = _load_script('wave_analyzer_disp', 'scripts/wave_analyzer.py')
        mod.display('Header', ['line1', 'line2'], gui=True)
        assert 'No EasyGUI' in capsys.readouterr().out

    def test_analyze_subsecond_shows_milliseconds(self, capsys):
        from scipy.io import wavfile

        with patch('importlib.util.find_spec', return_value=None):
            mod = _load_script('wave_analyzer_sub', 'scripts/wave_analyzer.py')
        sr = 44100
        n = 200
        pcm = (0.1 * np.sin(2 * np.pi * 440 * np.linspace(0, n / sr, n,
                                                            endpoint=False)))
        pcm_i16 = (pcm * (2 ** 15 - 1)).astype(np.int16)
        fd, path = tempfile.mkstemp(suffix='.wav')
        os.close(fd)
        try:
            wavfile.write(path, sr, pcm_i16)
            mod.analyze(path, gui=False)
        finally:
            os.unlink(path)
        out = capsys.readouterr().out
        assert 'milliseconds' in out

    def test_histogram_uses_matplotlib_when_available(self):
        pytest.importorskip('matplotlib')
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt

        with patch('importlib.util.find_spec', return_value=None):
            mod = _load_script('wave_analyzer_hist', 'scripts/wave_analyzer.py')
        with patch.object(plt, 'hist'), patch.object(plt, 'show'):
            mod.histogram(np.array([0.0, 1.0, 0.5, -0.25]))


class TestScriptLaunchers:
    scripts_dir = os.path.join(REPO_ROOT, 'scripts')

    @staticmethod
    def _fake_tkinter_modules():
        tk = types.ModuleType('tkinter')
        msg = types.ModuleType('tkinter.messagebox')
        msg.showerror = MagicMock(return_value='ok')
        tk.messagebox = msg
        tk.Tk = lambda *a, **k: MagicMock(withdraw=MagicMock())
        return tk, msg

    def test_thd_analyzer_launcher_empty_argv(self):
        tk, msg = self._fake_tkinter_modules()
        script = os.path.join(REPO_ROOT, 'scripts', 'thd_analyzer_launcher.py')
        with patch.dict(sys.modules, {'tkinter': tk, 'tkinter.messagebox': msg},
                        clear=False):
            with patch('sys.argv', ['thd_analyzer_launcher.py']):
                saved = sys.path[:]
                sys.path.insert(0, self.scripts_dir)
                try:
                    with pytest.raises(SystemExit):
                        runpy.run_path(script, run_name='__main__')
                finally:
                    sys.path[:] = saved
        msg.showerror.assert_called()

    def test_wave_analyzer_launcher_missing_file(self):
        tk, msg = self._fake_tkinter_modules()
        script = os.path.join(REPO_ROOT, 'scripts', 'wave_analyzer_launcher.py')
        with patch.dict(sys.modules, {'tkinter': tk, 'tkinter.messagebox': msg},
                        clear=False):
            with patch('sys.argv', ['wave_analyzer_launcher.py', 'missing.wav']):
                saved = sys.path[:]
                sys.path.insert(0, self.scripts_dir)
                try:
                    with pytest.raises(SystemExit):
                        runpy.run_path(script, run_name='__main__')
                finally:
                    sys.path[:] = saved
        msg.showerror.assert_called()
