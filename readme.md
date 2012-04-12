This was originally several different scripts for measuring or processing waveforms, which I pasted on gist:

http://gist.github.com/246092 total harmonic distortion measurement
http://gist.github.com/148112 A-weighting
http://gist.github.com/129445 frequency estimation with zero crossings
http://gist.github.com/255291 frequency estimation a bunch of ways
https://gist.github.com/2c786bf5b53b99ca3879 waveform analyzer (RMS level, A-weighted RMS, crest factor)

Since they have a lot in common, I'm combining them into one repository so I'm not duplicating effort.

Please don't blindly trust this.  If you use this and find a stupid error, please let me know.  Also let me know if you use this and it works perfectly.  :D

== Waveform analyzer ==
Usage: python wave_analyzer.py "audio file.flac"

Requires: Python, NumPy, SciPy, Audiolab
Optional: EasyGUI (output to a window instead of the console), Matplotlib (histogram of sample values)

http://pypi.python.org/pypi/scikits.audiolab
http://www.ar.media.kyoto-u.ac.jp/members/david/softwares/audiolab/sphinx/index.html

http://easygui.sourceforge.net/

It will open any file supported by audiolab, which basically means anything supported by libsndfile (http://www.mega-nerd.com/libsndfile/).

Currently this displays wave file information and measurements like crest factor and noise.

== To do or maybe to do ==
* Guess the type of waveform and do different measurements in different situations?  Noise vs sine vs whatever
   * Do FFT, see if there is one continuous peak
   * http://stackoverflow.com/questions/1141342/identifying-common-periodic-waveforms-square-sine-sawtooth
* Frequency estimation
   * Ideally: frequency with ±% accuracy - better accuracy for longer files
* py2exe compilation for Windoze
* Web page describing it
  * Screenshots compared to Audition analysis results
* Histogram of sample values
   * ("matplotlib not installed... skipping histogram")  hist()
* everything that Audition does?
   * --histogram of dB values--
   * number of possibly clipped samples
   * max/min sample values
   * peak amplitude
   * min RMS, max RMS, average RMS for chunks of 100 ms or so
   * actual bit depth
     * Identify if it is 8-bit samples encoded with 16 bits, for instance, like Audition does. Also like JACK bitmeter does?
* THD
* Real-time analysis of sound card input?
* Calculate intersample peaks
  * "If you want to see something really bad on the oversampled meter - try a sequence of maximum and minimum values that goes like this: "1010101101010" - notice that the alternating 1's and 0's suddenly change direction in the middle. The results depends on the filter being used in the reconstruction, with the intersample peak easily exceeding 10dB!"
* say dBFS instead of dB (with a note in readme that it is referenced to the RMS value of a full-scale square wave)
* Frequency response plot if the input is a sweep ;)
   * Probably should just make a separate script for each function like this, and this one can be a noise analysis script
* Dynamic range from test wave
* signal to noise from test wave
    * Same guts as THD script, just input -60 dBFS waveform and compare to maximum value instead of fundamental peak
* Implement a 468-weighting filter, too.
    * http://en.wikipedia.org/wiki/ITU-R_468_noise_weighting
    * http://www.mathworks.com/products/filterdesign/demos.html?file=/products/demos/shipping/filterdesign/audioweightingdemo.html#4
* Frequency analyzer should give "unknown" if SNR below some threshold, etc.

Done:
* total RMS level
* crest factor  
* DC offset
* should check if channels are identical
  * 2 unique channels vs 2 identical channels vs 1 channel
* Message about easygui not installed
* THD+N
* Frequency estimation
   * Guess frequency from FFT
   * <s>FFT Filter out noise and get just the fundamental</s>
   * <s>Count zero-crossings</s>
   * actually, interpolated FFT is the best, without any filtering or crossings counting


1. Get it into publishable form
2. Post it on github
3. Start using revision control for real
4. Use dBFS instead of dB

there may be an error in peak calculation?

test with crazy files like 1 MHz sampling rate, 3-bit, etc.

high frequencies of A-weighting roll off too quickly at lower sampling rates
make freq-response graphs at different signal levels and different sampling frequencies

<s>This is more a scientific measurement tool for engineering than a musical tool.  Peak and trough RMS and RMS histogram are not as important?</s>  Include them anyway!

== A-weighting ==
I was previously using the FFT filter in Adobe Audition to simulate an A-weighting filter.  This worked for large signal levels, but not for low noise floors, which is what I was stupidly using it for.

Apply an A-weighting filter to a sound stored as a NumPy array.

Use Audiolab or other module to import .wav or .flac files, for instance.
http://www.ar.media.kyoto-u.ac.jp/members/david/softwares/audiolab/

Translated from MATLAB script at 
http://www.mathworks.com/matlabcentral/fileexchange/69

== Frequency estimator ==
A few simple frequency estimation methods in Python

These are the methods that everyone recommends when someone asks about 
frequency estimation or pitch detection.  (Such as here: 
http://stackoverflow.com/questions/65268/music-how-do-you-analyse-the-fundamental-frequency-of-a-pcm-or-wac-sample/)

None of them work well in all situations, and I am sure there are much better 
methods "in the literature", but here is some code for the simple methods.

* Count zero-crossings
 * Using interpolation to find a "truer" zero-crossing gives better accuracy
 * Spline is better than linear interpolation?
* Do FFT and find the peak 
 * Using quadratic interpolation on a log-scaled spectrum to find a "truer" peak gives better accuracy
* Do autocorrelation and find the peak
* Calculate harmonic product spectrum and find the peak
== Somewhat crude THD+N calculator in Python ==

Measures the total harmonic distortion plus noise (THD+N) for a given input 
signal, by guessing the fundamental frequency (finding the peak in the FFT), 
and notching it out in the frequency domain.

Depends on Audiolab and SciPy
* http://www.ar.media.kyoto-u.ac.jp/members/david/softwares/audiolab/
* http://www.scipy.org/

Example of usage, with 997 Hz full-scale sine wave generated by Adobe Audition 
at 96 kHz, showing the 16-bit quantization distortion:

> python thdcalculator.py "perfect 997 Hz no dither.flac"
Frequency:	997.000000 Hz
THD+N:  	0.0016% or -96.1 dB

(Is this right?  Theoretical SNR of a FS sine is 1.761+6.02*16 = -98.09 dB.  
Close, at least.)

According to the never-wrong Wikipedia:
* THD is the fundamental alone vs the harmonics alone
* THD+N is the entire signal (not just the fundamental) vs the entire signal 
with the fundamental notched out.  (For low distortion, the difference between 
the entire signal and the fundamental is negligible.)

The primary problem with the current script is that I don't know how much of 
the surrounding region of the peak to throw away.  Probably the way to match 
other test equipment is to just calculate the width of a certain bandwidth, 
but is that really ideal?

width = 50
f[i-width: i+width+1] = 0

Instead of a fixed width, it currently just tries to find the nearest local 
minima and throw away everything between them.  It works for almost all cases, 
but on peaks with wider "skirts", it gets stuck at any notches.  Should this 
be considered part of the peak or part of the noise (jitter)?

By comparison, Audio Precision manual states "Bandreject Response typically 
–3 dB at 0.725 f0 & 1.38 f0", which is about 0.93 octaves.

Also it computes the FFT for the entire sample, which is a waste of time.  Use 
short samples.

Adobe Audition with dither:
997 Hz 8-bit    -49.8
997 Hz 16-bit   -93.4
997 Hz 32-bit   -143.9

Art Ludwig's Sound Files (http://members.cox.net/artludwig/):
File                Claimed  Measured  (dB)
Reference           0.0%     0.0022%   -93.3
Single-ended triode 5.0%     5.06%     -25.9
Solid state         0.5%     0.51%     -45.8

Comparing a test device on an Audio Precision System One 22 kHz filtered vs 
recorded into my 96 kHz 24-bit sound card and measured with this script:

Frequency   AP THD+N    Script THD+N
40          1.00%       1.04%
100         0.15%       0.19%
100         0.15%       0.14%
140         0.15%       0.17%
440         0.056%      0.057%
961         0.062%      0.067%
1021        0.080%      0.082%
1440        0.042%      0.041%
1483        0.15%       0.15%
4440        0.048%      0.046%
9974        7.1%        7.8%
10036       0.051%      0.068%
10723       8.2%        9.3%
13640       12.2%       16.8%
19998       20.2%       56.3%  (nasty intermodulation distortion)
20044       0.22%       0.30%

So it's mostly accurate.   Mostly.
