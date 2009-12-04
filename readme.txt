Crude THD+N calculator in Python

Measures

According to the never-wrong Wikipedia:

* THD is the fundamental alone vs the harmonics alone
* THD+N is the entire signal (not just the fundamental) vs the entire signal with the fundamental notched out.  (For low distortion, the difference between the entire signal and the fundamental is negligible.)

Comparing a test signal on an Audio Precision vs recorded into my 24-bit sound card with this script:

Claimed freq    Script freq    AP THD+N    Script THD+N
440.1    440.1    0.06%    0.06%
10003.9    10003.0    0.05%    0.07%
15000.0    14999.1        0.13%
19987.8    19986.0    0.22%    0.21%
10000.0    9999.1    8.16%    7.85%
997.0    996.9    0.06%    0.08%
100.0    100.0    0.15%    0.14%
