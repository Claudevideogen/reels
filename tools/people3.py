from PIL import Image, ImageDraw
def person(kind, mouth=0.0, blink=False):
    S = 2; w, h = 380, 440
    im = Image.new('RGBA', (w * S, h * S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    def E(b, **k): d.ellipse([v * S for v in b], **k)
    def P(pts, **k): d.polygon([(x * S, y * S) for x, y in pts], **k)
    def R(b, r, **k): d.rounded_rectangle([v * S for v in b], r * S, **k)
    def Lw(pts, wd, col): d.line([(x * S, y * S) for x, y in pts], fill=col, width=int(wd * S), joint='curve')
    ray = kind == 'ray'
    skin = (232, 186, 150) if ray else (122, 80, 52)
    shade = tuple(int(c * 0.86) for c in skin); line = (60, 35, 28)
    if ray:
        R((40, 300, 340, 470), 70, fill=(140, 96, 60))                 # brown cardigan
        R((150, 300, 230, 470), 18, fill=(70, 90, 120))                # navy shirt
        for y in (340, 380, 420): E((172, y, 182, y + 10), fill=(230, 210, 170))
        Lw([(150, 302), (150, 470)], 5, (115, 78, 48)); Lw([(230, 302), (230, 470)], 5, (115, 78, 48))
    else:
        R((40, 300, 340, 470), 70, fill=(210, 40, 50))                 # red tee
        d.arc([110 * S, 270 * S, 270 * S, 350 * S], 20, 160, fill=(30, 30, 30), width=14 * S)  # headphones band
        E((96, 300, 146, 350), fill=(30, 30, 30)); E((234, 300, 284, 350), fill=(30, 30, 30))
    R((162, 250, 218, 312), 20, fill=shade)
    E((80, 140, 114, 196), fill=skin); E((266, 140, 300, 196), fill=skin)
    E((97, 45, 283, 268), fill=skin)
    if ray:
        grey = (200, 200, 205)
        d.chord([93 * S, 36 * S, 287 * S, 190 * S], 180, 360, fill=grey)
        P([(110, 110), (150, 70), (240, 68), (275, 100), (190, 90)], fill=(225, 225, 230))
        R((92, 100, 108, 170), 6, fill=grey); R((272, 100, 288, 170), 6, fill=grey)
        d.chord([104 * S, 118 * S, 276 * S, 284 * S], 0, 180, fill=grey)     # grey beard
        E((140, 150, 240, 232), fill=skin)
    else:
        E((150, 66, 196, 84), fill=(140, 96, 66))  # head shine
        d.chord([160 * S, 205 * S, 220 * S, 262 * S], 0, 180, fill=(25, 20, 18))           # goatee
        E((166, 205, 214, 236), fill=skin)
    for cx in (152, 228):
        E((cx - 21, 140, cx + 21, 172), fill=(255, 255, 255))
        if blink: Lw([(cx - 17, 157), (cx + 17, 157)], 5, line)
        else:
            E((cx - 10, 145, cx + 10, 168), fill=(45, 35, 30)); E((cx - 4, 148, cx + 2, 154), fill=(255, 255, 255))
    if ray:
        Lw([(124, 124), (174, 126)], 10, (170, 170, 175)); Lw([(256, 124), (206, 126)], 10, (170, 170, 175))
    else:
        Lw([(126, 126), (172, 118)], 9, (25, 20, 18)); Lw([(254, 126), (208, 118)], 9, (25, 20, 18))
    d.arc([176 * S, 162 * S, 204 * S, 200 * S], 20, 160, fill=shade, width=5 * S)
    if mouth < 0.05:
        d.arc([160 * S, 198 * S, 220 * S, 230 * S], 20, 160, fill=line, width=6 * S)
    else:
        oh = 10 + 22 * mouth
        E((166, 210, 214, 210 + oh), fill=(110, 30, 40)); E((176, 210 + oh * 0.55, 204, 210 + oh), fill=(230, 110, 120))
    return im.resize((w, h), Image.LANCZOS)
