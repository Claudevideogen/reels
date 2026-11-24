"""Phrase-level TTS. Usage: python3 voice.py spec.json workdir
Writes workdir/voice.wav and workdir/timing.json (exact start/end of every line)."""
import json, sys, os, numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
spec = json.load(open(sys.argv[1])); wd = sys.argv[2]; os.makedirs(wd, exist_ok=True)
k = Kokoro(os.path.expanduser('~/tts/kokoro-v1.0.int8.onnx'), os.path.expanduser('~/tts/voices-v1.0.bin'))
SR = 24000; out = []; t = 0.25; meta = []; prev = None
out.append(np.zeros(int(t * SR)))
for i, L in enumerate(spec['lines']):
    v, sp = spec['voices'][L.get('who', 'A')]
    s, sr = k.create(L['say'], voice=v, speed=sp, lang=spec.get('lang', 'en-us'))
    a = np.abs(s); idx = np.where(a > 0.01)[0]; s = s[max(0, idx[0] - 120): idx[-1] + 300]
    if i:
        g = L.get('gap', 0.12 if L.get('who', 'A') == prev else 0.25)
        out.append(np.zeros(int(g * SR))); t += g
    meta.append({'i': i, 'start': round(t, 3), 'end': round(t + len(s) / SR, 3)}); out.append(s); t += len(s) / SR; prev = L.get('who', 'A')
tail = spec.get('tail', 2.2); out.append(np.zeros(int(tail * SR))); t += tail
sf.write(f'{wd}/voice.wav', np.concatenate(out).astype(np.float32), SR)
json.dump({'lines': meta, 'total': round(t, 3)}, open(f'{wd}/timing.json', 'w'), indent=1)
print('total', round(t, 2), 's'); [print(m) for m in meta]
