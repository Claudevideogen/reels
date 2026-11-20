from PIL import Image, ImageDraw
INK = (17, 17, 17)
def person(kind, mouth=0.0, blink=False):
    S = 2; w, h = 380, 440
    im = Image.new('RGBA', (w * S, h * S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    def E(b, **k): d.ellipse([v * S for v in b], **k)
    def P(pts, **k): d.polygon([(x * S, y * S) for x, y in pts], **k)
    def R(b, r, **k): d.rounded_rectangle([v * S for v in b], r * S, **k)
    def Lw(pts, wd, col): d.line([(x * S, y * S) for x, y in pts], fill=col, width=int(wd * S), joint='curve')
    sana = kind == 'sana'
    skin = (198, 140, 105) if sana else (226, 178, 138)
    shade = tuple(int(c * 0.86) for c in skin); line = (60, 35, 30)
    hair = (28, 20, 18) if sana else (35, 28, 24)
    if sana:  # long hair behind
        R((78, 70, 302, 360), 90, fill=hair)
    # torso
    if sana:
        R((50, 305, 330, 470), 70, fill=(22, 160, 150))
        P([(160, 305), (220, 305), (190, 350)], fill=shade)
        Lw([(160, 306), (190, 350), (220, 306)], 4, (15, 120, 112))
    else:
        R((40, 300, 340, 470), 70, fill=(72, 130, 80))          # green overshirt
        R((150, 300, 230, 470), 20, fill=(245, 245, 245))       # white tee
        Lw([(150, 300), (150, 470)], 5, (55, 105, 62)); Lw([(230, 300), (230, 470)], 5, (55, 105, 62))
    R((162, 250, 218, 312), 20, fill=shade)  # neck
    E((80, 140, 114, 196), fill=skin); E((266, 140, 300, 196), fill=skin)  # ears
    if sana:
        E((88, 186, 100, 200), fill=(240, 190, 40)); E((280, 186, 292, 200), fill=(240, 190, 40))
    E((97, 45, 283, 268), fill=skin)  # head
    if sana:
        d.chord([92 * S, 38 * S, 288 * S, 210 * S], 180, 360, fill=hair)
        P([(110, 125), (150, 60), (240, 70), (200, 100), (140, 120)], fill=hair)  # side-swept bangs
        R((86, 110, 112, 300), 14, fill=hair); R((268, 110, 294, 300), 14, fill=hair)
    else:
        for cx, cy, r in [(120, 92, 28), (150, 70, 30), (190, 62, 32), (230, 70, 30), (260, 92, 28), (108, 122, 20), (272, 122, 20), (170, 88, 26), (212, 88, 26)]:
            E((cx - r, cy - r, cx + r, cy + r), fill=hair)
        # beard
        d.chord([104 * S, 120 * S, 276 * S, 282 * S], 0, 180, fill=hair)
        E((140, 150, 240, 236), fill=skin)
    for cx in (152, 228):
        E((cx - 21, 140, cx + 21, 172), fill=(255, 255, 255))
        if blink: Lw([(cx - 17, 157), (cx + 17, 157)], 5, line)
        else:
            E((cx - 10, 145, cx + 10, 168), fill=(45, 30, 25)); E((cx - 4, 148, cx + 2, 154), fill=(255, 255, 255))
        if sana and not blink:
            Lw([(cx - 22, 146), (cx - 27, 140)], 4, INK); Lw([(cx + 22, 146), (cx + 27, 140)], 4, INK)
    # brows
    if sana: Lw([(128, 124), (172, 120)], 7, hair); Lw([(252, 124), (208, 120)], 7, hair)
    else: Lw([(124, 122), (174, 118)], 10, hair); Lw([(256, 122), (206, 118)], 10, hair)
    d.arc([176 * S, 162 * S, 204 * S, 200 * S], 20, 160, fill=shade, width=5 * S)
    lip = (190, 70, 90) if sana else line
    if mouth < 0.05:
        d.arc([158 * S, 196 * S, 222 * S, 234 * S], 20, 160, fill=lip, width=6 * S)
    else:
        oh = 10 + 22 * mouth
        E((166, 212, 214, 212 + oh), fill=(110, 30, 40), outline=lip if sana else None, width=3 * S)
        E((176, 212 + oh * 0.55, 204, 212 + oh), fill=(230, 110, 120))
    return im.resize((w, h), Image.LANCZOS)
