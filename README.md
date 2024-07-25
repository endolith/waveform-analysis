[![example workflow](https://github.com/endolith/waveform-analysis/actions/workflows/python-package.yml/badge.svg)](https://github.com/endolith/waveform-analysis/actions/workflows/python-package.yml)
[![codecov](https://codecov.io/github/endolith/waveform-analysis/graph/badge.svg?token=yDrCwmlDYa)](https://codecov.io/github/endolith/waveform-analysis)

This was originally several different scripts for measuring or processing waveforms, which I pasted on gist:

* [Total harmonic distortion measurement](http://gist.github.com/246092)
* [A-weighting](http://gist.github.com/148112)
* [Frequency estimation with zero crossings](http://gist.github.com/129445)
* [Frequency estimation a bunch of ways](http://gist.github.com/255291)
* [Waveform analyzer (RMS level, A-weighted RMS, crest factor)](https://gist.github.com/2c786bf5b53b99ca3879)

Since they have a lot in common, I'm trying to combine them into one repository, so I'm not duplicating effort.  It's a mess so far, though.

Please don't blindly trust this.  If you use this and find a stupid error, please let me know.  Also let me know if you use this and it works perfectly.  :D

Installation
============

This should now be an installable package, using:

    pip install git+https://github.com/endolith/waveform-analysis.git@master

I'm in the process of splitting it into callable functions and scripts that use those functions.

Waveform analyzer
=================

Currently this displays file information and measurements like crest factor and noise (including A-weighted noise, which is not usually included by other tools).

Usage: `python wave_analyzer.py "audio file.flac"`

For Windows' SendTo menu: `pythonw wave_analyzer_launcher.py`

**Requires:**

* Python 3
* NumPy
* SciPy

**Recommended:**

* [PySoundFile](http://pysoundfile.readthedocs.io) for opening any file format supported by [libsndfile](http://www.mega-nerd.com/libsndfile/) (including MP3).  Otherwise, it falls back to SciPy's very limited WAV file support.
  * (Mostly note to self, 2024-07-25: Install using `pip install soundfile`, not `pip install pysoundfile`.  Using `conda install pysoundfile` installs a slightly older version that may or [may not work](https://github.com/conda-forge/pysoundfile-feedstock/issues/13).)

**Optional:**

* [EasyGUI](http://easygui.sourceforge.net/) (output to a window instead of the console)
* Matplotlib (histogram of sample values)

A-weighting
===========

Applies an A-weighting filter to a sound file stored as a NumPy array.

I was previously using the FFT filter in Adobe Audition to simulate an A-weighting filter.  This worked for large signal levels, but not for low noise floors, which is what I was stupidly using it for.

Frequency estimator
===================

A few simple frequency estimation methods in Python

These are the methods that everyone recommends when someone asks about
frequency estimation or pitch detection.  (Such as here: [Music - How do you analyse the fundamental frequency of a PCM or WAV sample](http://stackoverflow.com/questions/65268/music-how-do-you-analyse-the-fundamental-frequency-of-a-pcm-or-wac-sample/))

None of them work well in all situations, these are "offline", not real-time, and I am sure there are much better methods "in the literature", but here is some code for the simple methods at least.

* Count zero-crossings
  * Using interpolation to find a "truer" zero-crossing gives better accuracy
  * Spline is better than linear interpolation?
* Do FFT and find the peak
  * Using quadratic interpolation on a log-scaled spectrum to find a "truer" peak gives better accuracy
* Do autocorrelation and find the peak
* Calculate harmonic product spectrum and find the peak

THD+N calculator
================

Measures the total harmonic distortion plus noise (THD+N) for a given input
signal, by guessing the fundamental frequency (finding the peak in the FFT),
and notching it out in the frequency domain.

Example of usage, with 997 Hz full-scale sine wave generated by Adobe Audition
at 96 kHz, showing the 16-bit quantization distortion:

    > python thd_analyzer.py "../997 Hz from 32-bit to 16-bit no dither.wav"
    Analyzing "../997 Hz from 32-bit to 16-bit no dither.wav"...
    Frequency: 996.999998 Hz
    THD+N:      0.0012% or -98.1 dB
    A-weighted: 0.0006% or -104.1 dB(A)

(Theoretical SNR of a full-scale sine is 1.761+6.02⋅16 = −98.09 dB, so this seems right)

According to the never-wrong Wikipedia:

* THD is the fundamental alone vs the harmonics alone.  The definition is ambiguous
* THD+N is the entire signal (not just the fundamental) vs the entire signal
  with the fundamental notched out.  (For low distortion, the difference between
  the entire signal and the fundamental alone is negligible.)

I'm not sure how much of
the surrounding region of the peak to throw away.  Should the "skirt" around the fundamental
be considered part of the peak or part of the noise (jitter)?  Probably the way to match
other test equipment is to just calculate the width of a certain bandwidth,
but is that really ideal?

Previously was finding the nearest local
minima and throwing away everything between them.  It works for some cases,
but on peaks with wider "skirts", it gets stuck at any notches.  Now using a fixed width ±10% of the fundamental, which works better.

For comparison, Audio Precision manual states:

> Bandreject Amplitude Function
> Bandreject Response
> typically –3 dB at 0.725 fo & 1.38 fo
> –20 dB at fo ±10%
> –40 dB at fo ±2.5%

So this is Q factor 1.53 or 0.93 octaves?  2nd-order?

Adobe Audition with default dither, full-scale 997 Hz sine wave:

     8-bit    -49.8 dB
    16-bit    -93.3 dB
    32-bit   -153.8 dB

[Art Ludwig's Sound Files](http://members.cox.net/artludwig/):

    File                        Claimed  Measured  (dB)
    Reference           (440Hz) 0.0%     0.0022%   -93.3
    Single-ended triode (440SE) 5.0%     5.06%     -25.9
    Solid state         (440SS) 0.5%     0.51%     -45.8

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

(This was done with local minima method.  Redo with 10% method.)

So it's mostly accurate.   Mostly.

To do
=====

* Guess the type of waveform and do different measurements in different situations?  Noise vs sine vs whatever
  * Do FFT, see if there is one continuous peak
  * [Identifying common periodic waveforms (square, sine, sawtooth, …)](http://stackoverflow.com/questions/1141342/identifying-common-periodic-waveforms-square-sine-sawtooth)
  * Report spectral flatness and then do THD+N for sine waves, etc.
  * Frequency analyzer should give "unknown" if SNR below some threshold, etc.
* Frequency estimation
  * Ideally: frequency with ±% accuracy - better accuracy for longer files
* py2exe compilation for Windoze
* Web page describing it
  * Screenshots compared to Audition analysis results
* Histogram of sample values
  * ("matplotlib not installed... skipping histogram")  hist()
* everything that Audition does?
  * ~~histogram of dB values~~
  * number of possibly clipped samples
  * max/min sample values
  * peak amplitude
  * min RMS, max RMS, average RMS for chunks of 100 ms or so
    * ~~This is more a scientific measurement tool for engineering than a musical tool.  Peak and trough RMS and RMS histogram are not as important?~~  Include them anyway!
  * actual bit depth
    * Identify if it is 8-bit samples encoded with 16 bits, for instance, like Audition does. Also like JACK bitmeter does?
* THD
* Real-time analysis of sound card input?
* Calculate intersample peaks
  * "If you want to see something really bad on the oversampled meter - try a sequence of maximum and minimum values that goes like this: "1010101101010" - notice that the alternating 1's and 0's suddenly change direction in the middle. The results depends on the filter being used in the reconstruction, with the intersample peak easily exceeding 10dB!"
* Extract frequency response plot if the input is a sweep ;)
  * Probably should just make a separate script for each function like this, and this one can be a noise analysis script
* Signal to noise and dynamic range from test file
  * Same guts as THD script, just input −60 dBFS waveform and compare to maximum value instead of fundamental peak
* Both normalizations of 468:
  * ITU-R 468: 0 dB at 1 kHz, true quasi-peak meter, for professional equipment
  * ITU-R ARM: 0 dB at 2 kHz, average-response meter, for commercial equipment
* there may be an error in peak calculation?
* test with crazy files like 1 MHz sampling rate, 3-bit, etc.
* Bug: high frequencies of A-weighting roll off too quickly at lower sampling rates
  * make freq-response graphs at different signal levels and different sampling frequencies
* What I've been calling "dBFS" is [probably better referred to](https://en.wikipedia.org/wiki/DBFS#RMS_levels) as "dBov"?
* `THD()` should use a flat-top window for improved accuracy.
* bilinear transform makes weighting filters not accurate at high frequencies.  Use FIR frequency sampling method instead?  Or upsample the signal.

Done
----

* Total RMS level
* Crest factor
* DC offset
* should check if channels are identical
  * 2 unique channels vs 2 identical channels vs 1 channel
* Message about easygui not installed
* THD+N
* Frequency estimation
  * Guess frequency from FFT
  * ~~FFT Filter out noise and get just the fundamental~~
  * ~~Count zero-crossings~~
  * actually, interpolated FFT is the best, without any filtering or crossings counting
* say dBFS instead of dB wherever appropriate (with a note in readme that it is referenced to the RMS value of a full-scale square wave)
* Implement a [468-weighting filter](http://en.wikipedia.org/wiki/ITU-R_468_noise_weighting), too.
  * analog spec: <http://www.beis.de/Elektronik/AudioMeasure/WeightingFilters.html#CCIR>
  * digital approximation: <http://www.mathworks.com/products/dsp-system/demos.html?file=/products/demos/shipping/dsp/audioweightingdemo.html#4>
