from __future__ import division
from scikits.audiolab import Sndfile
from numpy import array_equal, polyfit

def load(filename):
    """Load a wave file and return the signal, sample rate and number of channels.
    
    Can be any format that libsndfile supports, like .wav, .flac, etc.
    
    """
    wave_file = Sndfile(filename, 'r')
    signal = wave_file.read_frames(wave_file.nframes)
    channels = wave_file.channels
    sample_rate = wave_file.samplerate
    return signal, sample_rate, channels

def analyze_channels(filename, function):
    """Given a filename, run the given analyzer function on each channel of the file
	
	"""
    signal, sample_rate, channels = load(filename)
    print 'Analyzing "' + filename + '"...'

    if channels == 1:
        # Monaural
        function(signal, sample_rate)
    elif channels == 2:
        # Stereo
        if array_equal(signal[:,0],signal[:,1]):
            print '-- Left and Right channels are identical --'
            function(signal[:,0], sample_rate)
        else:
            print '-- Left channel --'
            function(signal[:,0], sample_rate)
            print '-- Right channel --'
            function(signal[:,1], sample_rate)
    else:
        # Multi-channel
        for ch_no, channel in enumerate(signal.transpose()):
            print '-- Channel %d --' % (ch_no + 1)
            function(channel, sample_rate)

def parabolic(f, x):
    """Quadratic interpolation for estimating the true position of an
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
    # Requires real division.  Insert float() somewhere to force it?
    xv = 1/2 * (f[x-1] - f[x+1]) / (f[x-1] - 2 * f[x] + f[x+1]) + x
    yv = f[x] - 1/4 * (f[x-1] - f[x+1]) * (xv - x)
    return (xv, yv)

def parabolic_polyfit(f, x):
    """Use the built-in polyfit() function to find the peak of a parabola"""
    a, b, c = polyfit([x-3,x-2,x-1,x,x+1,x+2,x+3],f[x-3:x+4],2)
    xv = -0.5*b/a
    yv = a*xv**2 + b*xv + c
    return (xv, yv)
