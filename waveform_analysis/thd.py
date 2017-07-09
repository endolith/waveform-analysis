from scipy.signal.windows import _cos_win
from scipy.fftpack import next_fast_len
from numpy.fft import rfft, irfft
from numpy import argmax, mean, log, concatenate, zeros
import numpy as np
from waveform_analysis._common import rms_flat, parabolic
from waveform_analysis import A_weight


# This requires accurately measuring frequency component amplitudes, so use a
# flat-top window (https://holometer.fnal.gov/GH_FFT.pdf)
flattops = {
    'dantona3': [0.2811, 0.5209, 0.1980],
    'dantona5': [0.21557895, 0.41663158, 0.277263158, 0.083578947,
                 0.006947368],
    'SFT3F': [0.26526, 0.5, 0.23474],
    'SFT4F': [0.21706, 0.42103, 0.28294, 0.07897],
    'SFT5F': [0.1881, 0.36923, 0.28702, 0.13077, 0.02488],
    'SFT3M': [0.28235, 0.52105, 0.19659],
    'SFT4M': [0.241906, 0.460841, 0.255381, 0.041872],
    'SFT5M': [0.209671, 0.407331, 0.281225, 0.092669, 0.0091036],
    'FTSRS': [1.0, 1.93, 1.29, 0.388, 0.028],
    'FTNI': [0.2810639, 0.5208972, 0.1980399],
    'FTHP': [1.0, 1.912510941, 1.079173272, 0.1832630879],
    'HFT70': [1, 1.90796, 1.07349, 0.18199],
    'HFT95': [1, 1.9383379, 1.3045202, 0.4028270, 0.0350665],
    'HFT90D': [1, 1.942604, 1.340318, 0.440811, 0.043097],
    'HFT116D': [1, 1.9575375, 1.4780705, 0.6367431, 0.1228389, 0.0066288],
    'HFT144D': [1, 1.96760033, 1.57983607, 0.81123644, 0.22583558, 0.02773848,
                0.00090360],
    'HFT169D': [1, 1.97441842, 1.65409888, 0.95788186, 0.33673420, 0.06364621,
                0.00521942, 0.00010599],
    'HFT196D': [1, 1.979280420, 1.710288951, 1.081629853, 0.448734314,
                0.112376628, 0.015122992, 0.000871252, 0.000011896],
    'HFT223D': [1, 1.98298997309, 1.75556083063, 1.19037717712, 0.56155440797,
                0.17296769663, 0.03233247087, 0.00324954578, 0.00013801040,
                0.00000132725],
    'HFT248D': [1, 1.985844164102, 1.791176438506, 1.282075284005,
                0.667777530266, 0.240160796576, 0.056656381764, 0.008134974479,
                0.000624544650, 0.000019808998, 0.000000132974],
    }


def THDN(signal, fs, weight=None):
    """Measure the THD+N for a signal and print the results

    Prints the estimated fundamental frequency and the measured THD+N.  This is
    calculated from the ratio of the entire signal before and after
    notch-filtering.

    This notch-filters by nulling out the frequency coefficients ±10% of the
    fundamental

    TODO: Make R vs F reference a parameter (currently is R)
    TODO: Or report all of the above in a dictionary?

    """
    # Get rid of DC and window the signal
    signal = np.asarray(signal) + 0.0  # Float-like array
    # TODO: Do this in the frequency domain, and take any skirts with it?
    signal -= mean(signal)

    window = _cos_win(len(signal), flattops['HFT248D'])
    windowed = signal * window
    del signal

    # Zero pad to nearest power of two
    new_len = next_fast_len(len(windowed))
    windowed = concatenate((windowed, zeros(new_len - len(windowed))))

    # Measure the total signal before filtering but after windowing
    total_rms = rms_flat(windowed)

    # Find the peak of the frequency spectrum (fundamental frequency)
    f = rfft(windowed)
    i = argmax(abs(f))
    true_i = parabolic(log(abs(f)), i)[0]
    frequency = fs * (true_i / len(windowed))

    # Filter out fundamental by throwing away values ±10%
    lowermin = int(true_i * 0.9)
    uppermin = int(true_i * 1.1)
    f[lowermin: uppermin] = 0
    # TODO: Zeroing FFT bins is bad

    # Transform noise back into the time domain and measure it
    noise = irfft(f)
    # TODO: RMS and A-weighting in frequency domain?  Parseval?

    if weight is None:
        pass
    elif weight == 'A':
        # Apply A-weighting to residual noise (Not normally used for
        # distortion, but used to measure dynamic range with -60 dBFS signal,
        # for instance)
        noise = A_weight(noise, fs)
        # TODO: filtfilt? tail end of filter?
    else:
        raise ValueError('Weighting not understood')

    # TODO: Return a dict or list of frequency, THD+N?
    return rms_flat(noise) / total_rms


def THD(signal, fs):
    """Measure the THD for a signal

    This function is not yet trustworthy.

    Returns the estimated fundamental frequency and the measured THD,
    calculated by finding peaks in the spectrum.

    TODO: Make weighting a parameter
    TODO: Make R vs F reference a parameter (F as default??)

    """
    # Get rid of DC and window the signal
    signal = np.asarray(signal) + 0.0  # Float-like array
    # TODO: Do this in the frequency domain, and take any skirts with it?
    signal -= mean(signal)

    window = _cos_win(len(signal), flattops['HFT248D'])
    windowed = signal * window
    del signal

    # Find the peak of the frequency spectrum (fundamental frequency)
    f = rfft(windowed)
    i = argmax(abs(f))
    true_i = parabolic(log(abs(f)), i)[0]
    print('Frequency: %f Hz' % (fs * (true_i / len(windowed))))

    print('fundamental amplitude: %.3f' % abs(f[i]))

    # Find the values for the first 15 harmonics.  Includes harmonic peaks
    # only, by definition
    # TODO: Should peak-find near each one, not just assume that fundamental
    # was perfectly estimated.
    # Instead of limited to 15, figure out how many fit based on f0 and
    # sampling rate and report this "4 harmonics" and list the strength of each
    for x in range(2, 15):
        print('%.3f' % abs(f[i * x]), end=' ')

    THD = sum([abs(f[i*x]) for x in range(2, 15)]) / abs(f[i])
    print('\nTHD: %f%%' % (THD * 100))
    return
