"""Original music bed + sync hits from timing. Usage: python3 music.py spec.json workdir -> workdir/mix.wav
spec.music: {bpm, root (midi, e.g. 57), mode 'major'|'minor', seed, energy 0..1}"""
import json, sys, numpy as np, soundfile as sf
from scipy.signal import butter, lfilter, resample_poly
spec = json.load(open(sys.argv[1])); wd = sys.argv[2]; T = json.load(open(f'{wd}/timing.json'))
M = spec.get('music', {}); SR = 44100; DUR = T['total']; N = int(SR * DUR); bpm = M.get('bpm', 100); beat = 60 / bpm
rng = np.random.default_rng(M.get('seed', 1)); E = M.get('energy', 0.7)
def env(n, a=0.005, d=0.3): x = np.arange(n) / SR; return np.minimum(x / a, 1) * np.exp(-x / d)
def add(b, s, at, g=1.0):
    i = int(at * SR); j = min(N, i + len(s))
    if 0 <= i < N: b[i:j] += s[:j - i] * g
lp = lambda x, f: lfilter(*butter(2, f / (SR / 2)), x); hp = lambda x, f: lfilter(*butter(2, f / (SR / 2), 'high'), x)
mf = lambda m: 440 * 2 ** ((m - 69) / 12)
def tone(f, dur, d=0.3, h=0.3, a=0.004):
    n = int(dur * SR); x = np.arange(n) / SR
    return (np.sin(2*np.pi*f*x) + h*np.sin(4*np.pi*f*x) + .1*np.sin(6*np.pi*f*x)) * env(n, a, d)
r = M.get('root', 57)
prog = [[0,3,7,10],[-4,0,3,7],[-9,-5,-2,2],[-2,2,5,9]] if M.get('mode','minor')=='minor' else [[0,4,7,11],[-3,0,4,7],[-7,-3,0,4],[-5,-1,2,5]]
mus = np.zeros(N); pump = np.zeros(N)
kn = int(.3*SR); kx = np.arange(kn)/SR; kick = np.sin(2*np.pi*(48+90*np.exp(-kx*35))*kx)*env(kn,.002,.12)
cl = hp(rng.normal(0,1,int(.25*SR)),1000)*env(int(.25*SR),.002,.07); hat = hp(rng.normal(0,1,int(.05*SR)),7000)*env(int(.05*SR),.001,.015)
b = 0; k = 0
while b < DUR - 1.5:
    ch = [r + c for c in prog[(k // 4) % 4]]
    if k % 4 == 0:
        for m in ch: add(mus, tone(mf(m), beat*4, .9, .25, .01), b, .055)
    add(mus, tone(mf(ch[0]-24), beat, .25, .6), b, .2)
    if k >= 2:
        add(mus, kick, b, .75*E); add(pump, env(int(.3*SR), .001, .1), b)
        if k % 2: add(mus, cl, b, .28*E)
        add(mus, hat, b + beat/2, .09*E)
    if k % 2 == 0: add(mus, tone(mf(ch[(k//2) % 3 + 1] + 12), .25, .09, .15), b + beat/2, .07)
    b += beat; k += 1
mus *= 1 - .35*np.clip(pump, 0, 1); mus = lp(mus, 9000)
sfx = np.zeros(N)
def whoosh(d=.25): n = int(d*SR); x = np.linspace(0,1,n); return lp(hp(rng.normal(0,1,n),600),6000)*np.sin(np.pi*x)**2
def boom(): n=int(.7*SR); x=np.arange(n)/SR; return np.sin(2*np.pi*(36+70*np.exp(-x*16))*x)*env(n,.002,.3)
for i, L in enumerate(T['lines'][1:], 1):
    add(sfx, whoosh(), L['start'] - .2, .3)
    if spec['lines'][i].get('hit'): add(sfx, boom(), L['start'] - .03, .9)
v, vsr = sf.read(f'{wd}/voice.wav'); v = resample_poly(v, SR, vsr)[:N]; v = np.pad(v, (0, N - len(v)))
ve = np.convolve(np.abs(v), np.ones(int(.12*SR))/int(.12*SR), 'same'); duck = 1 - .55*np.clip(ve/(ve.max()*.2), 0, 1)
fade = np.ones(N); fo = int(1.2*SR); fade[-fo:] = np.linspace(1, 0, fo)
out = v/np.abs(v).max()*.85 + mus/np.abs(mus).max()*.42*duck*fade + sfx/max(np.abs(sfx).max(),1e-6)*.3
out = out/np.abs(out).max()*.95; sf.write(f'{wd}/mix.wav', np.stack([out,out],1).astype(np.float32), SR); print('mix ok', round(DUR,2))
