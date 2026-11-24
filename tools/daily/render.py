"""Render a 1080x1920 reel: one shot per line, cut 0.03s before each line, punch-in on cuts,
word-by-word captions (active word yellow), optional big 'label' per line, header, CTA end card, progress bar.
Usage: python3 render.py spec.json workdir out.mp4"""
import json, sys, os, subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
spec = json.load(open(sys.argv[1])); wd = sys.argv[2]; OUT = sys.argv[3]; T = json.load(open(f'{wd}/timing.json'))
FPS = 30; W, H = 1080, 1920; BW, BH = 1188, 2112; DUR = T['total']; CL = spec['clips'].rstrip('/') + '/'
FB = '/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf'; font = lambda s: ImageFont.truetype(FB, s)
YEL = (255, 212, 0); ease = lambda x: 1 - (1 - min(max(x, 0), 1)) ** 3
lines = spec['lines']; tl = T['lines']
seg = []
for i, L in enumerate(lines):
    a = 0.0 if i == 0 else tl[i]['start'] - 0.03; b = DUR if i == len(lines) - 1 else tl[i + 1]['start'] - 0.03
    seg.append((a, b, L))
def decode(L, dur):
    cx = L.get('cx', .5); cy = L.get('cy', .5)
    vf = (f"scale={BW}:{BH}:force_original_aspect_ratio=increase,crop={BW}:{BH}:(iw-{BW})*{cx}:(ih-{BH})*{cy},fps={FPS},"
          "eq=contrast=1.07:saturation=1.1,colorbalance=rs=0.04:gs=0.01:bs=-0.04")
    raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-ss', str(L.get('off', 0.5)), '-stream_loop', '-1', '-i', CL + L['clip'] + '.mp4',
                          '-t', str(dur + .3), '-vf', vf, '-frames:v', str(int(dur * FPS) + 3), '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, BH, BW, 3)
vig = Image.new('L', (W, H), 0); dv = ImageDraw.Draw(vig)
for k in range(40): dv.rectangle([k*6, k*9, W-k*6, H-k*9], fill=int(160*(1-k/40)))
vig = vig.filter(ImageFilter.GaussianBlur(60)); VIG = Image.merge('RGBA', [Image.new('L', (W, H), 0)]*3 + [vig])
# bottom gradient behind captions
gr = np.zeros((H, W), np.uint8); gr[1000:] = (np.linspace(0, 150, H-1000)[:, None]).astype(np.uint8); GRAD = Image.merge('RGBA', [Image.new('L', (W, H), 0)]*3 + [Image.fromarray(gr)])
F_CAP = font(78); F_TOP = font(44); F_LAB = font(spec.get('label_size', 150)); F_CTA = font(64)
def chunks(words, n=4):
    return [words[i:i+n] for i in range(0, len(words), n)]
def word_times(i):
    words = lines[i].get('cap', lines[i]['say']).split(); s, e = tl[i]['start'], tl[i]['end']
    L = sum(len(w) + 1 for w in words); t = s; out = []
    for w in words: out.append((w, t)); t += (e - s) * (len(w) + 1) / L
    return out
def draw_caption(ov, i, t):
    wt = word_times(i); words = [w for w, _ in wt]
    act = max([j for j, (_, ts) in enumerate(wt) if t >= ts] or [0])
    ch = chunks(list(range(len(words))), lines[i].get('chunk', 4)); cur = next(c for c in ch if act in c)
    d = ImageDraw.Draw(ov); txt = [words[j] for j in cur]; sp = F_CAP.getlength(' ')
    widths = [F_CAP.getlength(w) for w in txt]; rows = [[]]; rw = 0
    for j, w in zip(cur, widths):
        if rw + w > 900 and rows[-1]: rows.append([]); rw = 0
        rows[-1].append(j); rw += w + sp
    y0 = spec.get('cap_y', 1380) - (len(rows) - 1) * 50
    for r, row in enumerate(rows):
        tw = sum(F_CAP.getlength(words[j]) for j in row) + sp * (len(row) - 1); x = W / 2 - tw / 2
        for j in row:
            col = YEL if j == act or words[j].strip('.,!?').upper() in [h.upper() for h in lines[i].get('hl', [])] else (255, 255, 255)
            d.text((x, y0 + r * 100), words[j], font=F_CAP, fill=col, stroke_width=7, stroke_fill=(0, 0, 0), anchor='lm'); x += F_CAP.getlength(words[j]) + sp
def pop(ov, txt, f, y, t0, t, col=YEL, box=False):
    sc = 1 + .35 * (1 - ease((t - t0) / .16)); tw = int(f.getlength(txt)) + 80; th = int(f.size * 1.5)
    tmp = Image.new('RGBA', (tw, th), (0, 0, 0, 0)); td = ImageDraw.Draw(tmp)
    if box: td.rounded_rectangle([0, 0, tw-1, th-1], 30, fill=(255, 255, 255, 245)); td.text((tw/2, th/2), txt, font=f, fill=(15, 15, 15), anchor='mm')
    else: td.text((tw/2, th/2), txt, font=f, fill=col, stroke_width=10, stroke_fill=(0, 0, 0), anchor='mm')
    tmp = tmp.resize((max(1, int(tw*sc)), max(1, int(th*sc))), Image.BILINEAR); ov.alpha_composite(tmp, (int(W/2-tmp.width/2), int(y-tmp.height/2)))
def cta_card(ov, t, t0):
    rows = spec['cta']; d = ImageDraw.Draw(ov); a = ease((t - t0) / .25); lh = 86
    bw = max(F_CTA.getlength(r) for r in rows) + 90; bh = lh * len(rows) + 60; y = 1000 + 40 * (1 - a)
    d.rounded_rectangle([W/2-bw/2, y-bh/2, W/2+bw/2, y+bh/2], 34, fill=(255, 255, 255, int(245*a)))
    for k, r in enumerate(rows): d.text((W/2, y-bh/2+30+lh*k+lh/2), r, font=F_CTA, fill=(15, 15, 15, int(255*a)), anchor='mm')
tmpout = OUT[:-4] + '.part.mp4'
p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                      '-i', f'{wd}/mix.wav', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k',
                      '-shortest', '-movflags', '+faststart', tmpout], stdin=subprocess.PIPE)
NF = int(DUR * FPS); fi = 0; cta_t = tl[-1]['end'] + 0.2 if spec.get('cta') else None
for si, (a, b, L) in enumerate(seg):
    fr = decode(L, b - a); n_end = min(NF, int(round(b * FPS)))
    while fi < n_end:
        t = fi / FPS; lt = t - a; k = min(int(lt * FPS), len(fr) - 1)
        punch = 0 if si == 0 else 1 - ease(lt / .35); Z = min(1.1, 1 + .07 * punch + .03 * lt / max(b - a, .1))
        cw, chh = BW / Z, BH / Z; x0, y0 = (BW - cw) / 2, (BH - chh) / 2
        im = Image.fromarray(fr[k]).resize((W, H), Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + chh)).convert('RGBA')
        im.alpha_composite(VIG); im.alpha_composite(GRAD)
        if cta_t and t >= cta_t: im.alpha_composite(Image.new('RGBA', (W, H), (0, 0, 0, int(90 * ease((t - cta_t) / .3)))))
        ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
        if spec.get('top'): d.text((W/2, 250), spec['top'], font=F_TOP, fill=(255, 255, 255), stroke_width=5, stroke_fill=(0, 0, 0), anchor='mm')
        if L.get('label'): pop(ov, L['label'], F_LAB, spec.get('label_y', 560), max(a, 0) + (0.05 if si else 0.0), t, box=L.get('label_box', False))
        if cta_t and t >= cta_t: cta_card(ov, t, cta_t)
        elif t >= tl[si]['start'] - .05: draw_caption(ov, si, t)
        if si and lt < .07 and L.get('hit'): im.alpha_composite(Image.new('RGBA', (W, H), (255, 255, 255, int(170 * (1 - lt / .07)))))
        im.alpha_composite(ov)
        pb = Image.new('RGBA', (W, 10), (255, 255, 255, 60)); ImageDraw.Draw(pb).rectangle([0, 0, int(W * t / DUR), 10], fill=YEL + (255,)); im.alpha_composite(pb, (0, H - 10))
        p.stdin.write(im.convert('RGB').tobytes()); fi += 1
p.stdin.close(); rc = p.wait(); print('ffmpeg rc', rc, fi, '/', NF)
if rc == 0: os.replace(tmpout, OUT); print('wrote', OUT)
else: sys.exit(1)
