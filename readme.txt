A few simple frequency estimation methods in Python

These are the methods that everyone recommends when someone asks about 
frequency estimation or pitch detection.  (Such as here: 
http://stackoverflow.com/questions/65268/music-how-do-you-analyse-the-fundamental-frequency-of-a-pcm-or-wac-sample/)

None of them work well in all situations, and I am sure there are much better 
methods "in the literature", but here is some code for the simple methods.

* Count zero-crossings
 * Using interpolation to find a "truer" zero-crossing gives better accuracy
* Do FFT and find the peak 
 * Using interpolation to find a "truer" peak gives better accuracy
* Do autocorrelation and find the peak
* Calculate harmonic product spectrum and find the peak
