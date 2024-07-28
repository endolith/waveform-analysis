#!/usr/bin/env python

import numpy as np

try:
    from soundfile import SoundFile
    wav_loader = 'pysoundfile'
except:
    try:
        from scipy.io.wavfile import read
        wav_loader = 'scipy.io.wavfile'
    except:
        raise ImportError('No sound file loading package installed '
                          '(PySoundFile or SciPy)')


def load(filename):
    soundfile = {}
    if wav_loader == 'pysoundfile':
        sf = SoundFile(filename)
        soundfile['signal'] = sf.read()
        soundfile['channels'] = sf.channels
        soundfile['fs'] = sf.samplerate
        soundfile['samples'] = len(sf)
        soundfile['format'] = f"{sf.format_info} {sf.subtype_info}"
        sf.close()
    elif wav_loader == 'scipy.io.wavfile':
        soundfile['fs'], soundfile['signal'] = read(filename)
        try:
            soundfile['channels'] = soundfile['signal'].shape[1]
        except IndexError:
            soundfile['channels'] = 1
        soundfile['samples'] = soundfile['signal'].shape[0]
        soundfile['format'] = str(soundfile['signal'].dtype)

        # Scale common formats
        signal = soundfile['signal']
        # PCM:
        if signal.dtype.kind == 'u' and signal.dtype.itemsize == 1:
            # 8-bit and under are unsigned
            signal = (signal.astype(float) - 128) / (2**7)
        elif signal.dtype.kind == 'i':  # int16, int32, int64
            if signal.dtype.itemsize == 2:
                # 9-bit and higher will be stored in 16-bit and are signed
                signal = signal.astype(float) / (2**15)
            elif signal.dtype.itemsize == 4:
                # 32-bit is signed
                # 24-bit are loaded as LJ 32-bit, so this gets scaled
                # correctly, assuming the fixed point convention described in
                # https://github.com/scipy/scipy/pull/12507#issue-652818718
                signal = signal.astype(float) / (2**31)
            elif signal.dtype.itemsize == 8:
                # 64-bit is rare but theoretically possible
                signal = signal.astype(float) / (2**63)
        # Float:
        elif signal.dtype.kind == 'f':  # float32, float64
            pass
        else:
            raise Exception("Don't know how to handle file format "
                            f"{soundfile['format']}")
        soundfile['signal'] = signal
    else:
        raise Exception("wav_loader has failed")

    return soundfile


def analyze_channels(filename, function):
    """
    Given a filename, run the given analyzer function on each channel of the
    file
    """
    signal, sample_rate, channels = load(filename)
    print(f"Analyzing \"{filename}\"...")

    if channels == 1:
        # Monaural
        function(signal, sample_rate)
    elif channels == 2:
        # Stereo
        if np.array_equal(signal[:, 0], signal[:, 1]):
            print('-- Left and Right channels are identical --')
            function(signal[:, 0], sample_rate)
        else:
            print('-- Left channel --')
            function(signal[:, 0], sample_rate)
            print('-- Right channel --')
            function(signal[:, 1], sample_rate)
    else:
        # Multi-channel
        for ch_no, channel in enumerate(signal.transpose()):
            print(f'-- Channel {ch_no + 1} --')
            function(channel, sample_rate)


# Copied from matplotlib.mlab:

def rms_flat(a):
    """
    Return the root mean square of all the elements of *a*, flattened out.
    """
    return np.sqrt(np.mean(np.absolute(a)**2))


def find(condition):
    "Return the indices where ravel(condition) is true"
    res, = np.nonzero(np.ravel(condition))
    return res


def dB(q):
    """
    Return the level of a field quantity in decibels.
    """
    return 20 * np.log10(q)


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
    if int(x) != x:
        raise ValueError('x must be an integer sample index')
    else:
        x = int(x)
    xv = 1/2. * (f[x-1] - f[x+1]) / (f[x-1] - 2 * f[x] + f[x+1]) + x
    yv = f[x] - 1/4. * (f[x-1] - f[x+1]) * (xv - x)
    return (xv, yv)


def parabolic_polyfit(f, x, n):
    """
    Use the built-in polyfit() function to find the peak of a parabola

    f is a vector and x is an index for that vector.

    n is the number of samples of the curve used to fit the parabola.
    """
    a, b, c = np.polyfit(np.arange(x-n//2, x+n//2+1), f[x-n//2:x+n//2+1], 2)
    xv = -0.5 * b/a
    yv = a * xv**2 + b * xv + c
    return (xv, yv)
