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
