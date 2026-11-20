import json, numpy as np, soundfile as sf
import json as _j; SR = 44100; DUR = round(_j.load(open('timing.json'))['total'], 2); N = int(SR * DUR)
rng = np.random.default_rng(3)
t = np.arange(N) / SR
mix = np.zeros(N)
bpm = 82; beat = 60 / bpm
def add(sig, at, gain=1.0):
    i = int(at * SR); j = min(N, i + len(sig))
    if i < N: mix[i:j] += sig[: j - i] * gain
def env(n, a=0.005, d=0.3):
    x = np.arange(n) / SR
    return np.minimum(x / a, 1) * np.exp(-x / d)
# kick
kn = int(0.35 * SR); kx = np.arange(kn) / SR
kick = np.sin(2 * np.pi * (50 + 90 * np.exp(-kx * 30)) * kx) * env(kn, 0.002, 0.12)
# snare (soft brushed)
sn = int(0.25 * SR); snare = rng.normal(0, 1, sn) * env(sn, 0.002, 0.07)
snare = np.convolve(snare, np.ones(6) / 6, 'same')
# hat
hn = int(0.06 * SR); hat = np.diff(rng.normal(0, 1, hn + 1)) * env(hn, 0.001, 0.015)
# chords: Fmaj7 - Em7 - Dm7 - Cmaj7 (warm electric-piano-ish)
chords = [[53, 57, 60, 64], [52, 55, 59, 62], [50, 53, 57, 60], [48, 52, 55, 59]]
def note(m, dur):
    n = int(dur * SR); x = np.arange(n) / SR; f = 440 * 2 ** ((m - 69) / 12)
    s = np.sin(2 * np.pi * f * x) + 0.3 * np.sin(4 * np.pi * f * x) * np.exp(-x * 3)
    return s * env(n, 0.02, 1.4) * (1 + 0.15 * np.sin(2 * np.pi * 4.5 * x))
bar = beat * 4
b = 0; k = 0
while b < DUR:
    for m in chords[k % 4]:
        add(note(m, bar + 0.5), b, 0.05)
    add(note(chords[k % 4][0] - 12, bar), b, 0.09)
    for i in range(4):
        tb = b + i * beat
        swing = 0.0
        add(kick, tb, 0.55 if i in (0, 2) else 0.0)
        if i in (1, 3): add(snare, tb, 0.18)
        add(hat, tb + beat / 2 + 0.03, 0.08); add(hat, tb, 0.05)
    b += bar; k += 1
# vinyl crackle
cr = np.zeros(N); idx = rng.integers(0, N, 900); cr[idx] = rng.normal(0, 0.25, 900)
mix += np.convolve(cr, np.ones(3) / 3, 'same') * 0.4 + rng.normal(0, 0.003, N)
# lowpass the beat (lofi)
from scipy.signal import butter, lfilter
bb, aa = butter(2, 3500 / (SR / 2)); mix = lfilter(bb, aa, mix)
# fade in/out
fade = np.ones(N); fi = int(0.6 * SR); fo = int(1.5 * SR)
fade[:fi] = np.linspace(0, 1, fi); fade[-fo:] = np.linspace(1, 0, fo)
mix *= fade
# bounce plucks (pentatonic), deduped
bounces = []
keep = []
for x in bounces:
    if not keep or x - keep[-1] > 0.09: keep.append(x)
pent = [72, 74, 76, 79, 81, 84, 86, 88]
pl = np.zeros(N)
for i, x in enumerate(keep):
    m = pent[i % len(pent)]; n = int(0.4 * SR); xx = np.arange(n) / SR
    f = 440 * 2 ** ((m - 69) / 12)
    s = (np.sin(2 * np.pi * f * xx) + 0.4 * np.sin(2 * np.pi * 2 * f * xx)) * env(n, 0.001, 0.09)
    i0 = int(x * SR); j0 = min(N, i0 + n); pl[i0:j0] += s[: j0 - i0]
# voice
v, vsr = sf.read('voice.wav')
from scipy.signal import resample_poly
v = resample_poly(v, SR, vsr)[:N]; v = np.pad(v, (0, N - len(v)))
# duck music under voice
venv = np.convolve(np.abs(v), np.ones(int(0.15 * SR)) / int(0.15 * SR), 'same')
duck = 1 - 0.45 * np.clip(venv / (venv.max() * 0.25), 0, 1)
out = v * 1.0 / np.abs(v).max() * 0.9 + mix / np.abs(mix).max() * 0.22 * duck
out = out / np.abs(out).max() * 0.95
sf.write('mix.wav', np.stack([out, out], 1).astype(np.float32), SR)
print('plucks', len(keep))
