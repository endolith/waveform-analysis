from scikits.audiolab import wavread, wavwrite
from numpy import mean
from A-weighting import A_weighting

filename = 'noise.wav'
y, Fs, bits = wavread(filename)
p = leq(Y,1000) #???
level = mean(p)
B, A = A_weighting(Fs)
x = filter(B, A, y)
pA = leq(x,1000) #???
levelA = mean(pA)
wavwrite(x, fs, bits, 'weightednoise.wav')
