import json, math, sys, subprocess, colorsys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, HALF = 1080, 1920, 960
FPS = 30
T = json.load(open('timing.json'))
DUR = round(T['total'], 2)
NF = int(DUR * FPS)
LINES = T['lines']
FD = '/usr/share/fonts/truetype/google-fonts/'
def F(name, size): return ImageFont.truetype(FD + name, size)
DJ = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def FA(size): return ImageFont.truetype(DJ, size)

CREAM = (250, 240, 246); NAVY = (20, 33, 61); YEL = (255, 201, 60)
GREEN = (46, 196, 111); INK = (17, 17, 17); RED = (230, 57, 70); BLUE = (52, 120, 246)

def ease_back(x):
    x = min(max(x, 0), 1); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2
def clamp(x, a=0, b=1): return max(a, min(b, x))

def rrect_sprite(w, h, r, fill, shadow=None, shoff=12, border=None, bw=0):
    S = 2; pad = shoff + 4
    im = Image.new('RGBA', ((w + pad) * S, (h + pad) * S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    if shadow: d.rounded_rectangle([shoff * S, shoff * S, (shoff + w) * S, (shoff + h) * S], r * S, fill=shadow)
    d.rounded_rectangle([0, 0, w * S, h * S], r * S, fill=fill, outline=border, width=bw * S)
    return im.resize((w + pad, h + pad), Image.LANCZOS)

def title_card():
    w, h = 920, 230
    im = rrect_sprite(w, h, 34, (30, 20, 50), shadow=(240, 110, 90), shoff=14); d = ImageDraw.Draw(im)
    d.text((48, 32), "FOR BUSINESS OWNERS RUNNING ADS", font=F('Poppins-Bold.ttf', 30), fill=(255, 190, 120))
    d.text((48, 72), "The ad mistake", font=F('Poppins-Bold.ttf', 64), fill=(255, 255, 255))
    d.text((48, 146), "costing you jobs.", font=F('Poppins-Bold.ttf', 64), fill=(255, 200, 190))
    return im

# ---------- feature cards ----------
def chip(d, x, y, text, bg, fg=(255, 255, 255), size=26, padx=16, h=46):
    f = F('Poppins-Bold.ttf', size); w = f.getlength(text) + padx * 2
    d.rounded_rectangle([x, y, x + w, y + h], h // 2, fill=bg)
    d.text((x + padx, y + (h - size) / 2 - 6), text, font=f, fill=fg)
    return x + w

def card_base(label, accent=(110, 110, 110)):
    w, h = 820, 170
    im = rrect_sprite(w, h, 26, (255, 255, 255), shadow=(0, 0, 0, 40), shoff=8, border=(30, 30, 30), bw=3)
    d = ImageDraw.Draw(im)
    d.text((32, 18), label, font=F('Poppins-Bold.ttf', 24), fill=accent)
    return im, d

def C_stack(p):
    im, d = card_base("YOUR CURRENT STACK", RED)
    x = 32
    apps = ["CRM", "Email", "SMS", "Booking", "Funnels"]
    for i, a in enumerate(apps):
        if p * 5 > i: x = chip(d, x, 62, a, (60, 60, 60), size=26) + 10
    if p >= 1: d.text((32, 118), "5 bills · 5 logins · 0 sync", font=F('Poppins-Bold.ttf', 30), fill=RED)
    return im

def C_allin(p):
    im, d = card_base("THE FIX", GREEN)
    d.text((32, 52), "GoHighLevel", font=F('Poppins-Bold.ttf', 50), fill=INK)
    chip(d, 32 + F('Poppins-Bold.ttf', 50).getlength("GoHighLevel") + 18, 62, "ALL-IN-ONE", GREEN, size=26)
    d.text((32, 118), "One login. One dashboard.", font=F('Poppins-Medium.ttf', 30), fill=(80, 80, 80))
    return im

def C_pipeline(p):
    im, d = card_base("CRM PIPELINE", BLUE)
    stages = ["New lead", "Contacted", "Booked"]
    xs = [32, 300, 568]
    for i, s in enumerate(stages):
        d.rounded_rectangle([xs[i], 64, xs[i] + 220, 150], 16, fill=(240, 243, 250), outline=(200, 205, 220), width=2)
        d.text((xs[i] + 18, 70), s, font=F('Poppins-Bold.ttf', 24), fill=(90, 90, 110))
    # moving lead card
    k = clamp(p * 1.3)
    pos = xs[0] + (xs[2] - xs[0]) * (k * k * (3 - 2 * k))
    d.rounded_rectangle([pos + 14, 104, pos + 206, 142], 10, fill=BLUE)
    d.text((pos + 26, 106), "Sarah K.", font=F('Poppins-Bold.ttf', 22), fill=(255, 255, 255))
    return im

def C_workflow(p):
    im, d = card_base("WORKFLOW · AUTOMATIC", (150, 90, 220))
    d.text((32, 58), "Form filled", font=F('Poppins-Bold.ttf', 36), fill=INK)
    d.text((262, 60), "→", font=FA(36), fill=(150, 90, 220))
    x = 316
    if p > 0.25: x = chip(d, x, 60, "SMS ✓".replace("✓", ""), GREEN, size=26) + 10
    if p > 0.5: x = chip(d, x, 60, "Email", GREEN, size=26) + 10
    if p > 0.75: chip(d, x, 60, "Follow-up", GREEN, size=26)
    d.text((32, 118), "Runs 24/7 while you work.", font=F('Poppins-Medium.ttf', 28), fill=(80, 80, 80))
    return im

def C_inbox(p):
    im, d = card_base("CALENDAR + ONE INBOX", BLUE)
    chip(d, 32, 56, "Booked: Thu 3:00 PM", GREEN, size=26)
    x = 32
    for i, (t, c) in enumerate([("SMS", (60, 60, 60)), ("Email", (60, 60, 60)), ("IG DM", (214, 41, 118)), ("FB", (24, 119, 242))]):
        if p * 4 > i: x = chip(d, x, 112, t, c, size=24, h=42) + 10
    d.text((x + 6, 114), "→ 1 inbox".replace("→", ""), font=F('Poppins-Bold.ttf', 28), fill=INK)
    return im

def C_funnels(p):
    im, d = card_base("FUNNELS + WEBSITES", (255, 140, 0))
    # mini page mockup
    d.rounded_rectangle([32, 56, 250, 154], 10, fill=(245, 245, 245), outline=(200, 200, 200), width=2)
    d.rectangle([44, 70, 238, 84], fill=(255, 140, 0)); d.rectangle([44, 94, 200, 102], fill=(200, 200, 200))
    d.rectangle([44, 110, 180, 118], fill=(200, 200, 200)); d.rounded_rectangle([44, 128, 140, 146], 6, fill=GREEN)
    d.text((280, 60), "Drag & drop builder", font=F('Poppins-Bold.ttf', 36), fill=INK)
    d.text((280, 110), "Landing pages, forms, sites", font=F('Poppins-Medium.ttf', 28), fill=(80, 80, 80))
    return im

def C_reviews(p):
    im, d = card_base("REPUTATION", (230, 160, 0))
    n = int(clamp(p * 1.4) * 5 + 0.001)
    sf = FA(54)
    for i in range(5):
        d.text((32 + i * 62, 50), "★", font=sf, fill=(255, 190, 0) if i < n else (220, 220, 220))
    chip(d, 360, 62, "Review request sent", GREEN, size=26)
    d.text((32, 120), "More 5-star reviews on Google.", font=F('Poppins-Medium.ttf', 28), fill=(80, 80, 80))
    return im

def C_price(p):
    im, d = card_base("PRICING", GREEN)
    d.text((32, 50), "From $97/mo", font=F('Poppins-Bold.ttf', 56), fill=INK)
    chip(d, 440, 62, "1 tool, not 5", NAVY, size=28)
    d.text((32, 122), "Usage fees (SMS, AI) extra. Check current plans.", font=F('Poppins-Medium.ttf', 22), fill=(110, 110, 110))
    return im

def icon(d, x, y, ok):
    S = 1; r = 30
    d.ellipse([x, y, x + 2 * r, y + 2 * r], fill=GREEN if ok else RED)
    if ok: d.line([(x + 16, y + 31), (x + 26, y + 42), (x + 45, y + 19)], fill=(255, 255, 255), width=8, joint='curve')
    else:
        d.line([(x + 19, y + 19), (x + 41, y + 41)], fill=(255, 255, 255), width=8)
        d.line([(x + 41, y + 19), (x + 19, y + 41)], fill=(255, 255, 255), width=8)

def pc(label_ok, main, sub=None):
    ok = label_ok
    def fn(p):
        w, h = 820, 170
        bg = (232, 250, 239) if ok else (255, 235, 236)
        im = rrect_sprite(w, h, 26, bg, shadow=(0, 0, 0, 40), shoff=8, border=GREEN if ok else RED, bw=4)
        d = ImageDraw.Draw(im)
        icon(d, 30, 26, ok)
        d.text((108, 24), "THE FIX" if ok else "THE PROBLEM", font=F('Poppins-Bold.ttf', 26), fill=(20, 140, 70) if ok else RED)
        fb = F('Poppins-Bold.ttf', 46); x = 108
        parts = main.split('→')
        for i, part in enumerate(parts):
            part = part.strip()
            d.text((x, 62), part, font=fb, fill=INK); x += fb.getlength(part + ' ')
            if i < len(parts) - 1:
                d.text((x, 68), "→", font=FA(42), fill=GREEN if ok else RED); x += FA(42).getlength("→ ")
        if sub: d.text((108, 120), sub, font=F('Poppins-Medium.ttf', 28), fill=(80, 80, 80))
        return im
    return fn

def sc(tag, col, main, sub):
    def fn(p):
        w, h = 820, 170
        im = rrect_sprite(w, h, 26, (255, 255, 255), shadow=(0, 0, 0, 40), shoff=8, border=col, bw=4)
        d = ImageDraw.Draw(im)
        tw = F('Poppins-Bold.ttf', 26).getlength(tag) + 32
        d.rounded_rectangle([30, 22, 30 + tw, 62], 20, fill=col)
        d.text((46, 24), tag, font=F('Poppins-Bold.ttf', 26), fill=(255, 255, 255))
        fb = F('Poppins-Bold.ttf', 44); x = 30
        parts = main.split('→')
        for i, part in enumerate(parts):
            part = part.strip()
            d.text((x, 70), part, font=fb, fill=INK); x += fb.getlength(part + ' ')
            if i < len(parts) - 1:
                d.text((x, 76), "→", font=FA(40), fill=col); x += FA(40).getlength("→ ")
        d.text((30, 124), sub, font=F('Poppins-Medium.ttf', 26), fill=(90, 90, 90))
        return im
    return fn

def ls(i): return LINES[i]['start']
def lmid(i, f): return LINES[i]['start'] + (LINES[i]['end'] - LINES[i]['start']) * f
GOLD = (214, 150, 20)
CARDS = [
    (0.0, pc(False, "Ads → leads → missed calls", "The leak most owners never see"), 0.1),
    (ls(3), pc(False, "\"I'll call back later\"", "Later = they already called the next guy"), 0.1),
    (ls(6), pc(True, "Missed call → text in 1 min", "Missed-call text-back"), 0.1),
    (ls(7), pc(True, "They reply → you book", "Even from a job site"), 0.1),
    (ls(9), sc("COMMENT", (240, 110, 90), "How fast do you call back?", "Be honest. Drop your time below."), 0.1),
]
CARD_CACHE = {}
def card_at(t):
    cur = None
    for i, (st, fn, ad) in enumerate(CARDS):
        if t >= st: cur = (i, st, fn, ad)
    if cur is None: return None, 0
    i, st, fn, ad = cur
    p = clamp((t - st) / ad)
    key = (i, round(p * 20))
    if key not in CARD_CACHE: CARD_CACHE[key] = fn(key[1] / 20)
    return CARD_CACHE[key], t - st

# ---------- characters ----------
from people3 import person
JAKE = {(m, b): person('ray', m, b) for m in (0.0, 0.5, 1.0) for b in (False, True)}
MARC = {(m, b): person('kev', m, b) for m in (0.0, 0.5, 1.0) for b in (False, True)}
TITLE = title_card()

# ---------- captions ----------
words = []
for li, L in enumerate(LINES):
    ws = L['text'].split(); tot = sum(len(w) + 2 for w in ws); t = L['start']; dur = L['end'] - L['start']
    for w in ws:
        dw = dur * (len(w) + 2) / tot; words.append((t, t + dw, w, L['who'], li)); t += dw
chunks, cur = [], []
for wd in words:
    if cur and (len(cur) == 3 or cur[-1][4] != wd[4] or cur[-1][2][-1] in '.?…,'):
        chunks.append(cur); cur = []
    cur.append(wd)
chunks.append(cur)
chunks[0][0] = (0.0,) + tuple(chunks[0][0][1:])
CAPF = F('Poppins-Bold.ttf', 52); TAGF = F('Poppins-Bold.ttf', 24)

def speaking(who, t): return any(L['who'] == who and L['start'] <= t <= L['end'] for L in LINES)
def mouth_amt(who, t):
    if not speaking(who, t): return 0.0
    v = abs(math.sin(t * 17.0)) * 0.7 + abs(math.sin(t * 9.3)) * 0.3
    return 1.0 if v > 0.66 else (0.5 if v > 0.33 else 0.0)
def blink(t, seed): return (t + seed) % 3.7 < 0.12

def paste_scaled(im, spr, cx, cy, s):
    if s < 0.01: return
    w, h = spr.size
    sp = spr.resize((max(1, int(w * s)), max(1, int(h * s))), Image.BILINEAR) if abs(s - 1) > 1e-3 else spr
    im.alpha_composite(sp, (int(cx - sp.size[0] / 2), int(cy - sp.size[1] / 2)))


HOOK_END = LINES[1]['end'] - 0.15
def hook_overlay(im, t):
    if t >= HOOK_END: return
    p = clamp(t / 0.18); s = 1.25 - 0.25 * (p * p * (3 - 2 * p))
    shake = (math.sin(t * 90) * 6 * (1 - p), 0)
    ov = Image.new('RGBA', (W, HALF), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    d.rectangle([0, 0, W, 630], fill=(22, 12, 34, 255)); d.rectangle([0, 626, W, 634], fill=(255, 70, 80, 255))
    big = Image.new('RGBA', (1000, 330), (0, 0, 0, 0)); bd = ImageDraw.Draw(big)
    f1 = F('Poppins-Bold.ttf', 132)
    bd.text((500 - f1.getlength('STOP') / 2, 0), 'STOP', font=f1, fill=(255, 70, 80))
    f2 = F('Poppins-Bold.ttf', 104)
    bd.text((500 - f2.getlength('running ads.') / 2, 160), 'running ads.', font=f2, fill=(255, 255, 255))
    big = big.resize((int(1000 * s), int(330 * s)), Image.BILINEAR)
    ov.alpha_composite(big, (int(540 - big.size[0] / 2 + shake[0]), int(270 - big.size[1] / 2)))
    if t > 1.35:
        q = clamp((t - 1.35) / 0.2)
        f3 = F('Poppins-Bold.ttf', 50); txt = '...until you fix this'
        tw = f3.getlength(txt)
        d2 = ImageDraw.Draw(ov)
        d2.rounded_rectangle([540 - tw / 2 - 26, 480, 540 + tw / 2 + 26, 560], 40, fill=(255, 201, 60, int(255 * q)))
        d2.text((540 - tw / 2, 486), txt, font=f3, fill=(20, 20, 30, int(255 * q)))
    im.alpha_composite(ov)

def top_frame(t):
    im = Image.new('RGBA', (W, HALF), CREAM + (255,))
    paste_scaled(im, TITLE, 533, 170, 1.0)
    card, age = card_at(t)
    if card is not None:
        s = (0.85 + 0.15 * ease_back(clamp(age / 0.25))) if (age < 0.25 and t > 0.2) else 1.0
        if 0.35 <= age < 0.6: s = 1 + 0.03 * math.sin((age - 0.35) / 0.25 * math.pi)
        paste_scaled(im, card, 540, 400, s)
    for who, bx, by, spr, seed in (("ray", 245, 822, JAKE, 0.6), ("kev", 835, 822, MARC, 1.3)):
        talk = speaking(who, t)
        sp = spr[(mouth_amt(who, t), blink(t, seed))]
        intro = 1.0
        bob = -abs(math.sin(t * 7.0)) * 10 if talk else math.sin(t * 2.2 + seed) * 4
        sc = intro * (1.0 if talk else 0.94)
        if sc < 0.01: continue
        sh = Image.new('RGBA', (W, HALF), (0, 0, 0, 0))
        ImageDraw.Draw(sh).ellipse([bx - 150 * sc, 945, bx + 150 * sc, 975], fill=(0, 0, 0, 30))
        im.alpha_composite(sh)
        paste_scaled(im, sp, bx, by + bob, sc)
    d = ImageDraw.Draw(im)
    for ci, ch in enumerate(chunks if t >= HOOK_END else []):
        if not (ch[0][0] <= t < ch[-1][1] + 0.35): continue
        if ci + 1 < len(chunks) and t >= chunks[ci + 1][0][0]: continue
        shown = [w for w in ch if w[0] <= t]
        if not shown: continue
        vis = ' '.join(w[2] for w in shown)
        bw = CAPF.getlength(vis) + 48; y = 535; x0 = 540 - bw / 2
        tag = ch[0][3].upper(); tw = TAGF.getlength(tag) + 24
        d.rounded_rectangle([540 - tw / 2, y - 44, 540 + tw / 2, y - 8], 6, fill=INK)
        d.text((540 - tw / 2 + 12, y - 44), tag, font=TAGF, fill=(255, 255, 255))
        d.rectangle([x0, y, x0 + bw, y + 78], fill=(255, 255, 255))
        d.text((x0 + 24, y + 4), vis, font=CAPF, fill=INK)
        break
    if False:
        q = ease_back(clamp((t - (LINES[-1]['start'] + 1.2)) / 0.4))
        cta = rrect_sprite(700, 92, 46, YEL, shadow=NAVY, shoff=8)
        ImageDraw.Draw(cta).text((64, 14), "Comment LEADS · free setup", font=F('Poppins-Bold.ttf', 40), fill=NAVY)
        paste_scaled(im, cta, 540, 575, q)
    hook_overlay(im, t)
    return im.convert('RGB')

# ---------- bottom: tower stacker ----------
import tower
TBG = tower.make_bg()
STATES = [0]
def bottom(f): return tower.draw(f / FPS, TBG)

def frame(f):
    t = f / FPS
    full = Image.new('RGB', (W, H), YEL)
    full.paste(top_frame(t), (0, 0)); full.paste(bottom(f), (0, HALF + 6))
    dd = ImageDraw.Draw(full)
    dd.rectangle([0, HALF - 4, W, HALF + 4], fill=(60, 60, 80))
    dd.rectangle([0, HALF - 4, int(W * min(1, t / DUR)), HALF + 4], fill=YEL)
    return full

if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'still':
        for t in map(float, sys.argv[2:]): frame(int(t * FPS)).save(f'still_{t:05.2f}.png')
    elif mode == 'bounces':
        print(NF, DUR)
    elif mode == 'video':
        a, b, out = int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
        p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                              '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
        for f in range(a, b): p.stdin.write(frame(f).tobytes())
        p.stdin.close(); p.wait(); sys.exit(p.returncode)
