This started out as an A-weighting filter and measurement, but I made it into a full waveform analysis tool.

I was previously using the FFT filter in Adobe Audition to simulate an A-weighting filter.  This worked for large signal levels, but not for low noise floors, which is what I was stupidly using it for.

Please don't blindly trust this.  If you use this and find a stupid error, please let me know.  If you use this and don't find any errors, please let me know.


Usage: python wave_analyzer.py "audio file.flac"

Requires: Python, NumPy, SciPy, Audiolab
Optional: EasyGUI (output to a window instead of the console), Matplotlib (histogram of sample values)

http://pypi.python.org/pypi/scikits.audiolab
http://www.ar.media.kyoto-u.ac.jp/members/david/softwares/audiolab/sphinx/index.html

http://easygui.sourceforge.net/

It will open any file supported by audiolab, which basically means anything supported by libsndfile (http://www.mega-nerd.com/libsndfile/).


To do:
* Guess the type of waveform?  Noise vs sine vs whatever
   * Do FFT, see if there is one continuous peak
   * http://stackoverflow.com/questions/1141342/identifying-common-periodic-waveforms-square-sine-sawtooth
* Frequency estimation if appropriate
   * Guess frequency from FFT
   * FFT Filter out noise and get just the fundamental
   * Count zero-crossings
   * Ideally: frequency with ±% accuracy - better accuracy for longer wavs
* Histogram of sample values
   * ("matplotlib not installed... skipping histogram")  hist()
* Identify if it is 8-bit samples encoded with 16 bits, for instance
* py2exe compilation for Windoze
* Web page describing it
  * Screenshots compared to Audition analysis results
* everything that Audition does?
   * --histogram of dB values--
   * number of possibly clipped samples
   * max/min sample values
   * peak amplitude
   * min RMS, max RMS, average RMS
   * actual bit depth
* THD
* THD+N
* Real-time analysis of sound card input?
* Calculate intersample peaks
  * "If you want to see something really bad on the oversampled meter - try a sequence of maximum and minimum values that goes like this: "1010101101010" - notice that the alternating 1's and 0's suddenly change direction in the middle. The results depends on the filter being used in the reconstruction, with the intersample peak easily exceeding 10dB!"

Maybe:
* Frequency response plot if the input is a sweep ;)
  * Probably should just make a separate script for each function like this, and this one can be a noise analysis script
* Dynamic range from test wave
* signal to noise from test wave

Done:
* total RMS level
* crest factor  
* DC offset
* should check if channels are identical
  * 2 unique channels vs 2 identical channels vs 1 channel
* Message about easygui not installed


1. Get it into publishable form
2. Post it on gist public
3. Start using revision control for real

right and left and multichannel are good

may be an error in peak calculation

high frequencies of A-weighting roll off too quickly at lower sampling rates
make freq-response graphs at different signal levels and different sampling frequencies

This is more a scientific measurement tool for engineering than a musical tool.  Peak and trough RMS and RMS histogram are not as important?

