import numpy as np, colorsys
from PIL import Image, ImageDraw, ImageFilter, ImageFont
W, HALF, FPS = 1080, 960, 30
BH = 46; T = 0.8; MOVE = 0.5; FALL = 0.12; V = 760
FB = ImageFont.truetype('/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf', 34)
FP = ImageFont.truetype('/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf', 56)
def plan(n_levels, seed=5):
    rng = np.random.default_rng(seed)
    levels = [(540.0, 460.0)]; events = []
    for i in range(1, n_levels):
        pc, pw = levels[-1]
        if pw < 150: pw = 460.0; pc = 540.0; levels[-1] = (pc, pw)  # reset width (bonus)
        e = rng.normal(0, 22)
        perfect = abs(e) < 7 or rng.random() < 0.3
        if perfect: e = 0.0
        a0, a1 = pc - pw / 2, pc + pw / 2; b0, b1 = pc + e - pw / 2, pc + e + pw / 2
        o0, o1 = max(a0, b0), min(a1, b1)
        nc, nw = (o0 + o1) / 2, o1 - o0
        cut = None
        if not perfect:
            cut = (b1 if e > 0 else b0, abs(e))  # edge and width of overhang
            cut = ((o1 + b1) / 2 if e > 0 else (b0 + o0) / 2, abs(e))
        events.append(dict(i=i, land_c=pc + e, w=pw, nc=nc, nw=nw, perfect=perfect, cut=cut, dir=1 if i % 2 else -1))
        levels.append((nc, nw))
    return levels, events
def make_bg():
    yy = np.linspace(0, 1, HALF)[:, None]
    top = np.array([40, 24, 70]); bot = np.array([240, 110, 90])
    g = (top * (1 - yy) + bot * yy)[:, None, :].repeat(W, 1).astype(np.uint8)
    return Image.fromarray(g[:, :, 0, :] if g.ndim == 4 else g).convert('RGBA')
LEVELS, EVENTS = plan(80)
T0 = -8 * T  # pre-built levels at t=0
def state_at(t):
    k = (t - T0) / T  # how many cycles elapsed
    idx = int(np.floor(k)); ph = (k - idx) * T
    placed = min(max(idx, 0), len(EVENTS))  # events fully landed before current cycle
    return idx, ph
def draw(t, BG):
    idx, ph = state_at(t)
    landed = idx + (1 if ph >= MOVE + FALL else 0)
    landed = min(landed, len(EVENTS))
    top_level = landed
    cam_target = max(0, top_level * BH - 520)
    cam_prev = max(0, (top_level - 1) * BH - 520)
    cam = cam_prev + (cam_target - cam_prev) * min(1, ph / 0.3) if ph < 0.3 else cam_target
    base_y = HALF - 60
    S = 2; lay = Image.new('RGBA', (W * S, HALF * S), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    def ly(level): return base_y - level * BH + cam
    for lvl in range(0, top_level + 1):
        y = ly(lvl)
        if y > HALF + BH or y < -BH: continue
        c, w = LEVELS[lvl]
        col = tuple(int(255 * v) for v in colorsys.hsv_to_rgb((lvl * 0.037) % 1, 0.65, 1.0))
        d.rounded_rectangle([(c - w / 2) * S, (y - BH) * S, (c + w / 2) * S, (y - 2) * S], 8 * S, fill=col + (255,))
        d.rectangle([(c - w / 2 + 6) * S, (y - BH + 4) * S, (c + w / 2 - 6) * S, (y - BH + 12) * S], fill=(255, 255, 255, 70))
    # current moving / falling block
    if 0 <= idx < len(EVENTS):
        ev = EVENTS[idx]; lvl = ev['i']
        col = tuple(int(255 * v) for v in colorsys.hsv_to_rgb((lvl * 0.037) % 1, 0.65, 1.0))
        if ph < MOVE + FALL:
            if ph < MOVE: x = ev['land_c'] + ev['dir'] * V * (MOVE - ph); y = ly(lvl) - 150
            else: x = ev['land_c']; y = ly(lvl) - 150 * (1 - (ph - MOVE) / FALL)
            w = ev['w']
            d.rounded_rectangle([(x - w / 2) * S, (y - BH) * S, (x + w / 2) * S, (y - 2) * S], 8 * S, fill=col + (255,))
        else:
            age = ph - MOVE - FALL
            if ev['cut']:
                cx, cw = ev['cut']; fy = ly(lvl) + 900 * age * age + 60 * age; a = max(0, 1 - age / 0.5)
                d.rounded_rectangle([(cx - cw / 2) * S, (fy - BH) * S, (cx + cw / 2) * S, (fy - 2) * S], 8 * S, fill=col + (int(255 * a),))
            elif age < 0.45:
                a = 1 - age / 0.45
                d.text((ev['nc'] * S - FP.getlength('PERFECT!') * S / 2, (ly(lvl) - BH - 80) * S), 'PERFECT!', font=FP.font_variant(size=56 * S), fill=(255, 255, 255, int(255 * a)))
    lay = lay.resize((W, HALF), Image.BILINEAR)
    out = BG.copy(); out.alpha_composite(lay.filter(ImageFilter.GaussianBlur(6))); out.alpha_composite(lay)
    dd = ImageDraw.Draw(out)
    dd.text((30, 18), f"HEIGHT {top_level}", font=FB, fill=(255, 255, 255))
    return out.convert('RGB')
