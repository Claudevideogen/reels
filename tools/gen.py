import json, numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
k = Kokoro('/home/claude/reel/tts/kokoro-v1.0.int8.onnx', '/home/claude/reel/tts/voices-v1.0.bin')
L = [
 ("ray", "Stop running ads.", "Stop running ads."),
 ("kev", "What? Ads are how I get clients!", "What? Ads are how I get clients!"),
 ("ray", "Ads get you leads. Then you miss their call.", "Ads get you leads. Then you miss their call."),
 ("kev", "I'm busy. I call back later.", "I'm busy. I call back later."),
 ("ray", "By then, they've already called the next guy.", "By then, they've already called the next guy."),
 ("kev", "So I hire someone to answer?", "So I hire someone to answer?"),
 ("ray", "No. Turn on missed-call text back. You miss a call, they get a text in a minute.", "No. Turn on missed-call text-back. You miss a call, they get a text in a minute."),
 ("ray", "They reply, you book them. Even from a job site.", "They reply, you book them. Even from a job site."),
 ("kev", "That's it?", "That's it?"),
 ("ray", "That's it. Be honest. How fast do you call back right now? Comment it.", "That's it. Be honest… how fast do you call back right now? Comment it."),
 ("ray", "And fix this, before you run another ad.", "And fix this before you run another ad."),
]
voice = {"ray": ("am_onyx", 1.06), "kev": ("am_liam", 1.12)}
SR = 24000; lead = 0.12; t = lead
out = [np.zeros(int(lead * SR), np.float32)]; meta = []
for i, (who, say, cap) in enumerate(L):
    v, sp = voice[who]
    s, sr = k.create(say, voice=v, speed=sp, lang="en-us")
    a = np.abs(s); idx = np.where(a > 0.01)[0]; s = s[max(0, idx[0]-120): idx[-1]+500]
    d = len(s) / SR
    meta.append({"who": who, "text": cap, "start": t, "end": t + d})
    out.append(s.astype(np.float32)); t += d
    g = 0.0 if i == len(L)-1 else (0.14 if L[i+1][0] == who else 0.2)
    out.append(np.zeros(int(g * SR), np.float32)); t += g
tail = 2.6; out.append(np.zeros(int(tail * SR), np.float32)); t += tail
sf.write('voice.wav', np.concatenate(out), SR)
json.dump({"lines": meta, "total": t}, open('timing.json', 'w'), indent=1)
for i, m in enumerate(meta): print(i, round(m['start'],2), round(m['end'],2), m['who'], m['text'])
print('TOTAL', t)
