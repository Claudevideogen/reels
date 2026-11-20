from PIL import Image, ImageDraw
INK = (17, 17, 17)
def person(kind, mouth=0.0, blink=False):
    S = 2; w, h = 380, 440
    im = Image.new('RGBA', (w * S, h * S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    def E(b, **k): d.ellipse([v * S for v in b], **k)
    def P(pts, **k): d.polygon([(x * S, y * S) for x, y in pts], **k)
    def R(b, r, **k): d.rounded_rectangle([v * S for v in b], r * S, **k)
    def Lw(pts, wd, col): d.line([(x * S, y * S) for x, y in pts], fill=col, width=int(wd * S), joint='curve')
    dan = kind == 'dan'
    skin = (236, 188, 156) if dan else (246, 208, 178)
    shade = tuple(int(c * 0.86) for c in skin); line = (70, 40, 30)
    hair = (120, 70, 40) if dan else (196, 120, 60)
    if dan:
        R((40, 300, 340, 470), 70, fill=(66, 110, 170))                  # denim work shirt
        P([(140, 300), (190, 340), (240, 300), (250, 318), (190, 372), (130, 318)], fill=(52, 92, 148))  # collar
        for y in (390, 425, 460): E((185, 390 if y == 390 else y, 195, (390 if y == 390 else y) + 10), fill=(230, 230, 230))
        R((250, 360, 300, 400), 6, outline=(52, 92, 148), width=4 * S)   # pocket
    else:
        R((40, 300, 340, 470), 70, fill=(120, 60, 120))                  # plum blazer
        P([(150, 300), (230, 300), (190, 370)], fill=(250, 250, 250))
        P([(150, 300), (122, 318), (178, 430), (188, 372)], fill=(140, 76, 140))
        P([(230, 300), (258, 318), (202, 430), (192, 372)], fill=(140, 76, 140))
    R((162, 250, 218, 312), 20, fill=shade)
    E((80, 140, 114, 196), fill=skin); E((266, 140, 300, 196), fill=skin)
    if not dan:
        E((150, -6, 230, 66), fill=hair)                                  # bun
    E((97, 45, 283, 268), fill=skin)
    if dan:
        # cap
        d.chord([92 * S, 30 * S, 288 * S, 200 * S], 180, 360, fill=(230, 120, 30))
        R((92, 104, 300, 124), 10, fill=(200, 100, 20))                   # bill
        E((180, 40, 200, 56), fill=(200, 100, 20))
        R((96, 124, 110, 160), 4, fill=hair); R((270, 124, 284, 160), 4, fill=hair)
        # stubble jaw
        d.chord([110 * S, 140 * S, 270 * S, 270 * S], 15, 165, fill=(214, 168, 136))
        E((130, 130, 250, 250), fill=skin)
    else:
        d.chord([93 * S, 36 * S, 287 * S, 190 * S], 180, 360, fill=hair)
        P([(100, 120), (140, 60), (200, 50), (150, 95)], fill=hair)
    for cx in (152, 228):
        E((cx - 21, 140, cx + 21, 172), fill=(255, 255, 255))
        if blink: Lw([(cx - 17, 157), (cx + 17, 157)], 5, line)
        else:
            E((cx - 10, 145, cx + 10, 168), fill=(50, 70, 90) if not dan else (60, 45, 35)); E((cx - 4, 148, cx + 2, 154), fill=(255, 255, 255))
    if not dan:
        for cx in (152, 228): E((cx - 30, 128, cx + 30, 184), outline=(40, 40, 40), width=4 * S)
        Lw([(182, 152), (198, 152)], 4, (40, 40, 40))
        Lw([(130, 120), (172, 116)], 6, (150, 90, 45)); Lw([(250, 120), (208, 116)], 6, (150, 90, 45))
    else:
        Lw([(128, 132), (172, 124)], 9, hair); Lw([(252, 132), (208, 124)], 9, hair)
    d.arc([176 * S, 162 * S, 204 * S, 200 * S], 20, 160, fill=shade, width=5 * S)
    if dan:
        P([(150, 204), (190, 196), (230, 204), (226, 214), (190, 208), (154, 214)], fill=hair)  # mustache
    lip = (180, 80, 100) if not dan else line
    if mouth < 0.05:
        if dan: d.arc([162 * S, 214 * S, 218 * S, 240 * S], 200, 340, fill=lip, width=5 * S)
        else: d.arc([158 * S, 196 * S, 222 * S, 234 * S], 20, 160, fill=lip, width=6 * S)
    else:
        oh = 10 + 22 * mouth
        E((166, 214, 214, 214 + oh), fill=(110, 30, 40))
        E((176, 214 + oh * 0.55, 204, 214 + oh), fill=(230, 110, 120))
    return im.resize((w, h), Image.LANCZOS)
