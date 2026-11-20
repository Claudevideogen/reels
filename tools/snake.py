import numpy as np, colorsys
from collections import deque
from PIL import Image, ImageDraw, ImageFilter, ImageFont
W, HALF, FPS = 1080, 960, 30
C = 40; GW, GH = 27, 22; OY = 80
FB = ImageFont.truetype('/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf', 34)
def bfs(start, goal, blocked):
    q = deque([start]); prev = {start: None}
    while q:
        cur = q.popleft()
        if cur == goal: break
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (cur[0] + dx, cur[1] + dy)
            if 0 <= n[0] < GW and 0 <= n[1] < GH and n not in blocked and n not in prev:
                prev[n] = cur; q.append(n)
    if goal not in prev: return None
    p = goal
    while prev[p] != start: p = prev[p]
    return p
def reach(start, blocked):
    q = deque([start]); seen = {start}
    while q:
        c = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (c[0] + dx, c[1] + dy)
            if 0 <= n[0] < GW and 0 <= n[1] < GH and n not in blocked and n not in seen: seen.add(n); q.append(n)
    return len(seen)
def simulate(NF, seed=11, steps_per_sec=12):
    rng = np.random.default_rng(seed)
    body = deque([(5, 11), (4, 11), (3, 11)]); grow = 0; score = 0
    def newfood():
        while True:
            f = (int(rng.integers(0, GW)), int(rng.integers(0, GH)))
            if f not in body: return f
    food = newfood(); eaten = []; states = []; acc = 0.0
    for fr in range(NF):
        acc += steps_per_sec / FPS
        while acc >= 1:
            acc -= 1
            head = body[0]; blocked = set(list(body)[:-1])
            nxt = bfs(head, food, blocked)
            if nxt is not None:
                bl2 = set(list(body)[:-1]) | {nxt}
                if reach(nxt, set(list(body)[:-2])) < len(body) + 2: nxt = None
            if nxt is None:
                best = None; bv = -1
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    n = (head[0] + dx, head[1] + dy)
                    if 0 <= n[0] < GW and 0 <= n[1] < GH and n not in blocked:
                        v = reach(n, blocked)
                        if v > bv: bv = v; best = n
                nxt = best
            if nxt is None:  # dead -> restart
                body = deque([(5, 11), (4, 11), (3, 11)]); food = newfood(); continue
            body.appendleft(nxt)
            if nxt == food:
                grow += 3; score += 10; eaten.append((fr / FPS, food)); food = newfood()
            if grow > 0: grow -= 1
            else: body.pop()
            if len(body) > 120: body = deque(list(body)[:60])
        states.append((list(body), food, score, [e for e in eaten if fr / FPS - e[0] < 0.5]))
    return states
def make_bg():
    bg = Image.new('RGBA', (W, HALF), (14, 22, 18, 255)); d = ImageDraw.Draw(bg)
    for gx in range(GW):
        for gy in range(GH):
            if (gx + gy) % 2 == 0: d.rectangle([gx * C, OY + gy * C, gx * C + C - 1, OY + gy * C + C - 1], fill=(20, 32, 26, 255))
    return bg
def draw(state, t, BG):
    body, food, score, eaten = state
    S = 2; lay = Image.new('RGBA', (W * S, HALF * S), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    pulse = 1 + 0.12 * np.sin(t * 8)
    fx, fy = food[0] * C + C / 2, OY + food[1] * C + C / 2; r = 14 * pulse
    d.ellipse([(fx - r) * S, (fy - r) * S, (fx + r) * S, (fy + r) * S], fill=(255, 70, 90, 255))
    n = len(body)
    for i, (x, y) in enumerate(reversed(body)):
        k = i / max(1, n - 1)
        col = tuple(int(255 * c) for c in colorsys.hsv_to_rgb(0.33 + 0.25 * k, 0.8, 0.75 + 0.25 * k))
        pad = 4 if i < n - 1 else 2
        d.rounded_rectangle([(x * C + pad) * S, (OY + y * C + pad) * S, (x * C + C - pad) * S, (OY + y * C + C - pad) * S], 10 * S, fill=col + (255,))
    hx, hy = body[0]
    for ex, ey in ((12, 12), (26, 12)):
        d.ellipse([(hx * C + ex - 4) * S, (OY + hy * C + ey - 4) * S, (hx * C + ex + 4) * S, (OY + hy * C + ey + 4) * S], fill=(20, 20, 20, 255))
    for (et, (gx, gy)) in eaten:
        a = 1 - (t - et) / 0.5; rr = 20 + 60 * (1 - a)
        cx, cy = gx * C + C / 2, OY + gy * C + C / 2
        d.ellipse([(cx - rr) * S, (cy - rr) * S, (cx + rr) * S, (cy + rr) * S], outline=(255, 220, 120, int(255 * a)), width=4 * S)
    lay = lay.resize((W, HALF), Image.BILINEAR)
    out = BG.copy(); out.alpha_composite(lay.filter(ImageFilter.GaussianBlur(8))); out.alpha_composite(lay)
    dd = ImageDraw.Draw(out)
    dd.text((30, 18), f"SCORE {score}", font=FB, fill=(255, 255, 255))
    dd.text((W - 30 - FB.getlength(f"LENGTH {len(body)}"), 18), f"LENGTH {len(body)}", font=FB, fill=(160, 230, 170))
    return out.convert('RGB')
