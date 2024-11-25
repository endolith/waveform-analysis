import numpy as np
from numpy import argmax, concatenate, log, mean, zeros
from scipy.fft import irfft, next_fast_len, rfft
from scipy.signal.windows import general_cosine

from waveform_analysis._common import parabolic, rms_flat
from waveform_analysis.weighting_filters.ABC_weighting import A_weight

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
    """
    Calculate the Total Harmonic Distortion + Noise (THD+N) of a signal.

    Parameters
    ----------
    signal : array_like
        Input signal to analyze.
    fs : float
        Sampling frequency of the signal in Hz, used for A-weighting.
    weight : {'A', None}, optional
        Weighting type for the noise measurement:

        - 'A' : Apply A-weighting to the residual noise.
        - None : No weighting applied (default).

    Returns
    -------
    thdn : float
        The THD+N of the input signal as a dimensionless ratio.

    Notes
    -----
    This function calculates the total harmonic distortion and noise ratio
    of the signal by nulling out the frequency coefficients ±10% of the
    fundamental frequency, to isolate harmonic components and noise.

    The fundamental is estimated from the peak of the frequency spectrum, so
    it must be the strongest frequency in the signal.

    The signal is windowed using a flattop window to reduce spectral leakage,
    while still allowing accurate amplitude measurements. It is then
    zero-padded to the nearest size that provides efficient FFT computation.

    This calculates the ratio vs the RMS value of the original signal, so this
    is THD(R), not THD(F).

    Examples
    --------
    Calculate THD+N for a 1 kHz sine wave sampled at 48 kHz, with a
    2nd harmonic at 10% amplitude:

    >>> import numpy as np
    >>> fs = 48000  # Hz
    >>> t = np.linspace(0, 1, fs, endpoint=False)
    >>> signal = np.sin(2*np.pi*1000*t) + 0.1*np.sin(2*np.pi*2000*t)
    >>> THDN_ratio = THDN(signal, fs)
    >>> print(f"THD+N ratio: {THDN_ratio*100:.1f}%")
    THD+N ratio: 10.0%
    """
    # Get rid of DC and window the signal
    signal = np.asarray(signal) + 0.0  # Float-like array
    # TODO: Do this in the frequency domain, and take any skirts with it?
    signal -= mean(signal)

    window = general_cosine(len(signal), flattops['HFT248D'])
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
    # frequency = fs * (true_i / len(windowed))

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


thd_n = THDN


def THD(signal, fs, *, ref='f', verbose=True):
    """
    Calculate the Total Harmonic Distortion (THD) of a signal.

    Parameters
    ----------
    signal : array_like
        Input signal to analyze.
    fs : float
        Sampling frequency of the signal in Hz.
    ref : {'r', 'f'}, optional
        Reference type for the THD calculation:

        - 'r' : Use the RMS value of the original signal as reference.
        - 'f' : Use the fundamental amplitude as reference (default).
    verbose : bool, optional
        If True, print detailed measurements (default).

    Returns
    -------
    results : dict
        A dictionary containing:
            - 'thd': The THD ratio (float)
            - 'frequency': Fundamental frequency in Hz (float)
            - 'fundamental_amplitude': Amplitude of fundamental (float)
            - 'harmonics': List of tuples (freq, amplitude) for each harmonic

    Notes
    -----
    This function calculates the total harmonic distortion ratio of the
    signal by identifying the fundamental frequency and its harmonics in the
    frequency spectrum.

    The fundamental is estimated from the peak of the frequency spectrum, so
    it must be the strongest frequency in the signal.

    The signal is windowed using a flattop window to reduce spectral leakage,
    while still allowing accurate amplitude measurements.

    Examples
    --------
    Calculate THD for a 10 kHz sine wave sampled at 48 kHz, with a
    2nd harmonic at 10% amplitude:

    >>> import numpy as np
    >>> fs = 48000  # Hz
    >>> t = np.linspace(0, 1, fs, endpoint=False)
    >>> signal = np.sin(2*np.pi*10000*t) + 0.1*np.sin(2*np.pi*20000*t)
    >>> results = THD(signal, fs)
    Frequency: 10000.000000 Hz
    fundamental amplitude: 23999.500
    Harmonic 2 at 20000.000 Hz: 2399.950

    THD: 10.000000%
    >>> results['thd']
    0.1
    """
    # Get rid of DC and window the signal
    signal = np.asarray(signal) + 0.0  # Float-like array
    # TODO: Do this in the frequency domain, and take any skirts with it?
    signal -= mean(signal)

    window = general_cosine(len(signal), flattops['HFT248D'])
    windowed = signal * window
    del signal

    # Find the peak of the frequency spectrum (fundamental frequency)
    f = rfft(windowed)
    i = argmax(abs(f))
    true_i = parabolic(log(abs(f)), i)[0]
    frequency = fs * (true_i / len(windowed))
    if verbose:
        print(f'Frequency: {frequency:f} Hz')

    fundamental_amplitude = abs(f[i])
    if verbose:
        print(f'fundamental amplitude: {fundamental_amplitude:.3f}')

    # Find the values for the harmonics.  Includes harmonic peaks
    # only, by definition
    # TODO: Should peak-find near each one, not just assume that fundamental
    # was perfectly estimated.
    num_harmonics = int((fs/2)/frequency)
    harmonic_amplitudes = []
    harmonics = []
    for h in range(2, num_harmonics + 1):
        freq = frequency * h
        ampl = abs(f[i * h])
        harmonic_amplitudes.append(ampl)
        harmonics.append((freq, ampl))
        if verbose:
            print(f'Harmonic {h} at {freq:.3f} Hz: {ampl:.3f}')

    THD = np.sqrt(sum(h**2 for h in harmonic_amplitudes))
    if ref.lower() == 'f':
        THD /= fundamental_amplitude
    elif ref.lower() == 'r':
        THD /= np.sqrt(fundamental_amplitude**2 + THD**2)
    else:
        raise ValueError('Reference argument not understood.')

    if verbose:
        print(f'\nTHD: {THD * 100:f}%')

    return {
        'thd': THD,
        'frequency': frequency,
        'fundamental_amplitude': fundamental_amplitude,
        'harmonics': harmonics,
    }


thd = THD
