This started out as an A-weighting filter and measurement, but I made it into a full waveform analysis tool.

Usage: python wave_analyzer.py "audio file.flac"

It will open anything supported by audiolab, which basically means anything supported by libsndfile (http://www.mega-nerd.com/libsndfile/).

I was previously using the FFT filter in Audition to simulate an A-weighting filter.  This worked for large signal levels, but not for low noise floors, which is what I was stupidly using it for.

Please don't blindly trust this.  If I did anything stupid, let me know.

To do(?):
* Guess the type of waveform?  Noise vs sine vs whatever
* Frequency estimation if appropriate
* Histogram of sample values ("matplotlib not installed... skipping histogram")
* Identify if it is 8-bit samples encoded with 16 bits, for instance
* Frequency response plot if the input is a sweep ;)  
  * Probably should just make a separate script for each function like this, and this one can be a noise analysis script
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
* Ideally: frequency with ±% accuracy - better accuracy for longer wavs
* THD
* THD+N
* Dynamic range
* signal to noise
* should check if channels are identical?  
* Real-time analysis of sound card input?
* Calculate intersample peaks
  * "If you want to see something really bad on the oversampled meter - try a sequence of maximum and minimum values that goes like this: "1010101101010" - notice that the alternating 1's and 0's suddenly change direction in the middle. The results depends on the filter being used in the reconstruction, with the intersample peak easily exceeding 10dB!"
* Message about easygui not installed?
* 2 unique channels vs 2 identical channels vs 1 channel

Done:
* total RMS level
* crest factor  
* DC offset