"""
Helpers for subprocess-based script tests.

Scripts import ``waveform_analysis`` as a top-level package. Running them with
``sys.executable script.py`` only finds that package if it is installed
(``pip install -e .``) or if ``PYTHONPATH`` includes the repository root. CI
installs the package; setting ``PYTHONPATH`` here keeps local ``pytest`` runs
working the same way without an editable install.
"""

import os

_TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(_TESTS_DIR, '..'))


def env_with_repo_on_pythonpath():
    env = os.environ.copy()
    key = 'PYTHONPATH'
    prefix = REPO_ROOT
    if env.get(key):
        env[key] = prefix + os.pathsep + env[key]
    else:
        env[key] = prefix
    return env
