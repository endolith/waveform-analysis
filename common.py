from scikits.audiolab import Sndfile
from numpy import array_equal

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


