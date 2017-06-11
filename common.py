#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from numpy import array_equal, polyfit, sqrt, mean, absolute, log10, arange
from scipy.stats import gmean

try:
    from soundfile import SoundFile
    wav_loader = 'pysoundfile'
except:
    try:
        from scikits.audiolab import Sndfile
        wav_loader = 'scikits.audiolab'
    except:
        try:
            from scipy.io.wavfile import read
            wav_loader = 'scipy.io.wavfile'
        except:
            raise ImportError('No sound file loading package installed '
                              '(PySoundFile, scikits.audiolab, or SciPy)')


def load(filename):
    """
    Load a wave file and return the signal, sample rate and number of channels.

    Can be any format supported by the underlying library (libsndfile or SciPy)
    """
    if wav_loader == 'pysoundfile':
        sf = SoundFile(filename)
        signal = sf.read()
        channels = sf.channels
        sample_rate = sf.samplerate
        samples = len(sf)
        file_format = sf.format_info + ' ' + sf.subtype_info
        sf.close()
    elif wav_loader == 'scikits.audiolab':
        sf = Sndfile(filename, 'r')
        signal = sf.read_frames(sf.nframes)
        channels = sf.channels
        sample_rate = sf.samplerate
        samples = sf.nframes
        file_format = sf.format
        sf.close()
    elif wav_loader == 'scipy.io.wavfile':
        sample_rate, signal = read(filename)
        try:
            channels = signal.shape[1]
        except IndexError:
            channels = 1
        samples = signal.shape[0]
        file_format = str(signal.dtype)

    return signal, sample_rate, channels


def analyze_channels(filename, function):
    """
    Given a filename, run the given analyzer function on each channel of the
    file
    """
    signal, sample_rate, channels = load(filename)
    print 'Analyzing "' + filename + '"...'

    if channels == 1:
        # Monaural
        function(signal, sample_rate)
    elif channels == 2:
        # Stereo
        if array_equal(signal[:, 0], signal[:, 1]):
            print '-- Left and Right channels are identical --'
            function(signal[:, 0], sample_rate)
        else:
            print '-- Left channel --'
            function(signal[:, 0], sample_rate)
            print '-- Right channel --'
            function(signal[:, 1], sample_rate)
    else:
        # Multi-channel
        for ch_no, channel in enumerate(signal.transpose()):
            print '-- Channel %d --' % (ch_no + 1)
            function(channel, sample_rate)


def rms_flat(a):
    """
    Return the root mean square of all the elements of *a*, flattened out.
    """
    return sqrt(mean(absolute(a)**2))


def dB(level):
    """
    Return a level in decibels.
    """
    return 20 * log10(level)


def spectral_flatness(spectrum):
    """
    The spectral flatness is calculated by dividing the geometric mean of
    the power spectrum by the arithmetic mean of the power spectrum

    I'm not sure if the spectrum should be squared first...
    """
    return gmean(spectrum)/mean(spectrum)


def parabolic(f, x):
    """
    Quadratic interpolation for estimating the true position of an
    inter-sample maximum when nearby samples are known.

    f is a vector and x is an index for that vector.

    Returns (vx, vy), the coordinates of the vertex of a parabola that goes
    through point x and its two neighbors.

    Example:
    Defining a vector f with a local maximum at index 3 (= 6), find local
    maximum if points 2, 3, and 4 actually defined a parabola.

    In [3]: f = [2, 3, 1, 6, 4, 2, 3, 1]

    In [4]: parabolic(f, argmax(f))
    Out[4]: (3.2142857142857144, 6.1607142857142856)
    """
    xv = 1/2. * (f[x-1] - f[x+1]) / (f[x-1] - 2 * f[x] + f[x+1]) + x
    yv = f[x] - 1/4. * (f[x-1] - f[x+1]) * (xv - x)
    return (xv, yv)


def parabolic_polyfit(f, x, n):
    """
    Use the built-in polyfit() function to find the peak of a parabola

    f is a vector and x is an index for that vector.

    n is the number of samples of the curve used to fit the parabola.
    """
    a, b, c = polyfit(arange(x-n//2, x+n//2+1), f[x-n//2:x+n//2+1], 2)
    xv = -0.5 * b/a
    yv = a * xv**2 + b * xv + c
    return (xv, yv)
