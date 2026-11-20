import numpy as np, colorsys, json
from PIL import Image, ImageDraw, ImageFilter, ImageFont
W, HALF, FPS = 1080, 960, 30
BR = 18; PR = 10
rows = 9; pegs = []
for r in range(rows):
    y = 150 + r * 68
    xs = [40 + i * 100 for i in range(11)] if r % 2 == 0 else [90 + i * 100 for i in range(10)]
    pegs += [(x, y) for x in xs]
PEGS = np.array(pegs, float)
BIN_TOP = 770; NB = 9; BW = W / NB
DIV = [i * BW for i in range(1, NB)]
def simulate(NF, seed=7):
    rng = np.random.default_rng(seed)
    P = np.zeros((0, 2)); V = np.zeros((0, 2)); C = []; alive = []
    counts = [0] * NB; flashes = []; states = []
    sub = 6; dt = 1 / FPS / sub; g = 1900.0
    landed_ids = set(); bid = 0; ids = []; born = []
    for f in range(NF):
        t = f / FPS
        if f % 5 == 0:
            P = np.vstack([P, [540 + rng.uniform(-70, 70), 60]]); V = np.vstack([V, [rng.uniform(-40, 40), 0]])
            C.append((bid * 0.083) % 1); ids.append(bid); born.append(t); bid += 1
        for s in range(sub):
            if len(P) == 0: break
            V[:, 1] += g * dt; P += V * dt
            # pegs
            d = P[:, None, :] - PEGS[None, :, :]; dist = np.linalg.norm(d, axis=2)
            hit = dist < (BR + PR)
            for i, j in zip(*np.nonzero(hit)):
                n = d[i, j] / max(dist[i, j], 1e-6)
                vn = np.dot(V[i], n)
                if vn < 0: V[i] -= 1.55 * vn * n; V[i, 0] += rng.uniform(-25, 25)
                P[i] = PEGS[j] + n * (BR + PR + 0.1)
            # ball-ball
            if len(P) > 1:
                d = P[:, None, :] - P[None, :, :]; dist = np.linalg.norm(d, axis=2) + np.eye(len(P)) * 1e6
                for i, j in zip(*np.nonzero(dist < 2 * BR)):
                    if i < j:
                        n = d[i, j] / max(dist[i, j], 1e-6); ov = 2 * BR - dist[i, j]
                        P[i] += n * ov / 2; P[j] -= n * ov / 2
                        rv = np.dot(V[i] - V[j], n)
                        if rv < 0: V[i] -= 0.8 * rv * n; V[j] += 0.8 * rv * n
            # walls
            m = P[:, 0] < BR; P[m, 0] = BR; V[m, 0] = np.abs(V[m, 0]) * 0.6
            m = P[:, 0] > W - BR; P[m, 0] = W - BR; V[m, 0] = -np.abs(V[m, 0]) * 0.6
            # bin dividers
            for x in DIV:
                m = (P[:, 1] > BIN_TOP) & (np.abs(P[:, 0] - x) < BR + 4)
                side = np.sign(P[m, 0] - x); side[side == 0] = 1
                P[m, 0] = x + side * (BR + 4); V[m, 0] *= -0.4
        # landing
        keep = []
        for i in range(len(P)):
            if P[i, 1] > 900:
                b = int(min(NB - 1, max(0, P[i, 0] // BW))); counts[b] += 1; flashes.append((t, b))
            else: keep.append(i)
        P, V = P[keep], V[keep]; C = [C[i] for i in keep]
        states.append((P.copy(), list(C), list(counts)))
    return states, flashes

FB = ImageFont.truetype('/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf', 34)
def make_static():
    yy, xx = np.mgrid[0:HALF, 0:W]
    rad = np.sqrt((xx - 540) ** 2 + (yy - 420) ** 2) / 760
    bg = Image.fromarray(np.clip(np.stack([16 + 22 * (1 - rad), 12 + 14 * (1 - rad), 40 + 40 * (1 - rad)], -1), 0, 255).astype(np.uint8)).convert('RGBA')
    S = 2; lay = Image.new('RGBA', (W * S, HALF * S), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for x, y in PEGS: d.ellipse([(x - PR) * S, (y - PR) * S, (x + PR) * S, (y + PR) * S], fill=(235, 235, 255, 255))
    for i in range(NB):
        h = i / NB
        col = tuple(int(255 * c) for c in colorsys.hsv_to_rgb(h, 0.7, 0.9))
        d.rounded_rectangle([(i * BW + 6) * S, 905 * S, ((i + 1) * BW - 6) * S, 950 * S], 10 * S, fill=col + (255,))
    for x in DIV: d.rounded_rectangle([(x - 4) * S, BIN_TOP * S, (x + 4) * S, 950 * S], 4 * S, fill=(200, 200, 230, 255))
    lay = lay.resize((W, HALF), Image.LANCZOS)
    glow = lay.filter(ImageFilter.GaussianBlur(8))
    bg.alpha_composite(glow); bg.alpha_composite(lay)
    return bg
