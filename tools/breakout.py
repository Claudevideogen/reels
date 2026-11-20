import numpy as np, colorsys
from PIL import Image, ImageDraw, ImageFilter, ImageFont
W, HALF, FPS = 1080, 960, 30
COLS, ROWS = 9, 7; BX0, BY0, BWID, BH, GAP = 30, 70, 113, 40, 6
PY = 880; PW = 220; PH = 24; BR = 18
FB = ImageFont.truetype('/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf', 34)
def brick_rect(c, r): return (BX0 + c * BWID + GAP / 2, BY0 + r * (BH + GAP), BX0 + (c + 1) * BWID - GAP / 2, BY0 + r * (BH + GAP) + BH)
def simulate(NF, seed=3):
    rng = np.random.default_rng(seed)
    alive = np.ones((ROWS, COLS), bool)
    balls = [[540.0, 700.0, 430.0, -700.0], [300.0, 760.0, -470.0, -680.0], [780.0, 600.0, 400.0, 690.0]]
    px = 540.0; score = 0; parts = []; states = []
    sub = 4; dt = 1 / FPS / sub
    for f in range(NF):
        for s in range(sub):
            # paddle AI: follow lowest descending ball
            tgt = max(balls, key=lambda b: (b[3] > 0, b[1]))
            px += np.clip(tgt[0] + 30 * np.sin(f * 0.07) - px, -26, 26)
            px = float(np.clip(px, PW / 2, W - PW / 2))
            for b in balls:
                b[0] += b[2] * dt; b[1] += b[3] * dt
                if b[0] < BR: b[0] = BR; b[2] = abs(b[2])
                if b[0] > W - BR: b[0] = W - BR; b[2] = -abs(b[2])
                if b[1] < BR: b[1] = BR; b[3] = abs(b[3])
                if b[3] > 0 and PY - BR <= b[1] <= PY + PH and abs(b[0] - px) < PW / 2 + BR:
                    off = (b[0] - px) / (PW / 2)
                    sp = np.hypot(b[2], b[3]); ang = np.radians(-90 + 55 * off)
                    b[2], b[3] = sp * np.cos(ang), sp * np.sin(ang); b[1] = PY - BR
                if b[1] > HALF + 30:  # missed: respawn
                    b[0], b[1], b[2], b[3] = px, PY - 40, rng.choice([-1, 1]) * 400.0, -620.0
                c = int((b[0] - BX0) // BWID); r = int((b[1] - BY0) // (BH + GAP))
                if 0 <= c < COLS and 0 <= r < ROWS and alive[r, c]:
                    x0, y0, x1, y1 = brick_rect(c, r)
                    if x0 - BR < b[0] < x1 + BR and y0 - BR < b[1] < y1 + BR:
                        alive[r, c] = False; score += 10
                        b[3] = -b[3]
                        hue = r / ROWS
                        for k in range(8):
                            parts.append([b[0], b[1], rng.uniform(-260, 260), rng.uniform(-260, 120), f / FPS, hue])
        if not alive.any(): alive[:] = True
        t = f / FPS
        parts = [p for p in parts if t - p[4] < 0.6]
        states.append((alive.copy(), [list(b) for b in balls], px, score, [list(p) for p in parts]))
    return states

def make_bg():
    yy, xx = np.mgrid[0:HALF, 0:W]
    rad = np.sqrt((xx - 540) ** 2 + (yy - 480) ** 2) / 760
    return Image.fromarray(np.clip(np.stack([8 + 18 * (1 - rad), 20 + 26 * (1 - rad), 30 + 26 * (1 - rad)], -1), 0, 255).astype(np.uint8)).convert('RGBA')

def draw(state, t, BG):
    alive, balls, px, score, parts = state
    S = 2; lay = Image.new('RGBA', (W * S, HALF * S), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for r in range(ROWS):
        col = tuple(int(255 * c) for c in colorsys.hsv_to_rgb(r / ROWS, 0.75, 1.0))
        for c in range(COLS):
            if alive[r, c]:
                x0, y0, x1, y1 = brick_rect(c, r)
                d.rounded_rectangle([x0 * S, y0 * S, x1 * S, y1 * S], 8 * S, fill=col + (255,))
                d.rounded_rectangle([x0 * S, y0 * S, x1 * S, (y0 + 10) * S], 6 * S, fill=(255, 255, 255, 70))
    for p in parts:
        age = t - p[4]; a = max(0, 1 - age / 0.6)
        x = p[0] + p[2] * age; y = p[1] + p[3] * age + 400 * age * age
        col = tuple(int(255 * c) for c in colorsys.hsv_to_rgb(p[5], 0.7, 1.0))
        d.rectangle([(x - 5) * S, (y - 5) * S, (x + 5) * S, (y + 5) * S], fill=col + (int(255 * a),))
    d.rounded_rectangle([(px - PW / 2) * S, PY * S, (px + PW / 2) * S, (PY + PH) * S], 11 * S, fill=(240, 240, 255, 255))
    for b in balls:
        d.ellipse([(b[0] - BR) * S, (b[1] - BR) * S, (b[0] + BR) * S, (b[1] + BR) * S], fill=(255, 230, 90, 255))
    lay = lay.resize((W, HALF), Image.BILINEAR)
    out = BG.copy(); out.alpha_composite(lay.filter(ImageFilter.GaussianBlur(7))); out.alpha_composite(lay)
    dd = ImageDraw.Draw(out)
    dd.text((30, 14), f"SCORE {score}", font=FB, fill=(255, 255, 255))
    return out.convert('RGB')
