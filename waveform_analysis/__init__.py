"""
A collection of functions and scripts for analyzing waveforms, especially audio

https://github.com/endolith/waveform-analysis
"""

from ._common import dB, parabolic, rms_flat
from .freq_estimation import freq_from_autocorr, freq_from_fft, freq_from_hps
from .thd import THD, THDN, thd, thd_n
from .weighting_filters import *
