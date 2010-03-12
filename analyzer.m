filename = 'noise.wav'
[Y,FS,BITS] = wavread(filename);
p = leq(Y,1000);
level = mean(p)
[B,A] = adsgn(FS);
x = filter(B,A,Y);
pA = leq(x,1000);
levelA = mean(pA)
wavwrite(x,FS,BITS,'weightednoise.wav')
