#!/usr/bin/env python3
"""Rich-art renderer for news-image-20261123 slot-1 page.
Fresh PIL renderer: cream broadsheet, giant date, 11 cards each with a
layered-gradient, grain-textured illustrated panel and a drawn scene.
Deterministic: all texture comes from fixed-seed numpy RandomState or
pure maths, so repeated runs are byte-identical.
"""
import json, math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1024, 1024
CREAM_TOP = (248, 243, 233)
CREAM_BOT = (242, 233, 208)
INK = (24, 22, 18)
RED = (178, 28, 32)
NAVY = (18, 42, 84)
CARD_BG = (252, 249, 240)
CARD_LINE = (146, 132, 104)

FDIR = "/usr/share/fonts/truetype/noto/"
SERIF_CB = FDIR + "NotoSerif-CondensedBold.ttf"
COND_B = FDIR + "NotoSans-CondensedBold.ttf"
COND = FDIR + "NotoSans-Condensed.ttf"
EXTRA_B = FDIR + "NotoSans-ExtraCondensedBold.ttf"

def font(path, size):
    return ImageFont.truetype(path, size)

def wrap(text, fnt, maxw):
    words, lines, cur = text.split(), [], ""
    for wd in words:
        t = (cur + " " + wd).strip()
        if fnt.getlength(t) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur); cur = wd
    if cur:
        lines.append(cur)
    return lines

def fit_lines(text, maxw, size, max_lines=2):
    """Try condensed bold, then extra-condensed bold, at the given size."""
    for path in (COND_B, EXTRA_B):
        f = font(path, size)
        ls = wrap(text, f, maxw)
        if len(ls) <= max_lines:
            return f, ls
    f = font(EXTRA_B, size)
    return f, wrap(text, f, maxw)

# ---------- rich gradient panel base ----------
def gradient_panel(w, h, c_top, c_mid, c_bot, seed, grain=13):
    rng = np.random.RandomState(seed)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float64)
    t = 0.72 * (yy / max(h - 1, 1)) + 0.28 * (xx / max(w - 1, 1))
    t += 0.07 * np.sin(xx * 0.11 + seed * 1.7) * np.cos(yy * 0.13 + seed)
    # radial glow upper-left
    d = np.sqrt(((xx - w * 0.28) / max(w, 1)) ** 2 + ((yy - h * 0.18) / max(h, 1)) ** 2)
    glow = np.clip(1.0 - d, 0, 1) * 26.0
    arr = np.zeros((h, w, 3), np.float64)
    ct, cm, cb = (np.array(c, np.float64) for c in (c_top, c_mid, c_bot))
    lo = t < 0.5
    for ch in range(3):
        a = np.where(lo, ct[ch] + (cm[ch] - ct[ch]) * (t * 2),
                     cm[ch] + (cb[ch] - cm[ch]) * ((t - 0.5) * 2))
        # multi-frequency colour field, phase/frequency differ per channel
        field = (9.0 * np.sin(xx * (0.16 + 0.03 * ch) + seed * 2.1 + ch * 1.7)
                 * np.cos(yy * (0.19 - 0.02 * ch) + seed + ch * 0.9)
                 + 6.0 * np.sin((xx + yy) * (0.07 + 0.013 * ch) + ch * 2.3 + seed))
        arr[:, :, ch] = a + glow + field
    noise = rng.randint(-grain, grain + 1, size=(h, w, 3))
    arr += noise
    # soft vignette
    vx = 1.0 - 0.10 * ((xx / max(w - 1, 1) - 0.5) ** 2 + (yy / max(h - 1, 1) - 0.5) ** 2) * 2
    arr *= vx[:, :, None]
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")

PALETTES = {
    "kospi":    ((38, 62, 120), (24, 38, 84), (10, 16, 40)),
    "cricket":  ((34, 110, 62), (22, 84, 48), (10, 48, 28)),
    "rescue":   ((112, 96, 84), (76, 64, 56), (38, 32, 28)),
    "pmi":      ((84, 96, 116), (54, 66, 88), (26, 34, 50)),
    "retail":   ((196, 92, 60), (164, 62, 48), (110, 36, 32)),
    "poll":     ((70, 92, 140), (46, 64, 104), (22, 34, 62)),
    "bitcoin":  ((96, 74, 20), (66, 52, 14), (34, 27, 8)),
    "nhs":      ((196, 120, 156), (158, 82, 122), (104, 48, 84)),
    "hangseng": ((28, 104, 116), (18, 74, 92), (8, 40, 58)),
    "robot":    ((88, 84, 96), (56, 54, 68), (28, 27, 38)),
    "music":    ((74, 40, 110), (48, 26, 78), (22, 12, 40)),
}

# ---------- scenes (drawn only inside the scene rect) ----------
def scene_layer(w, h, kind, seed):
    lay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    rng = np.random.RandomState(seed + 77)
    if kind == "kospi":
        base = h - 4
        for i, bw in enumerate([10, 14, 8, 16, 11, 13, 9, 15]):
            x = 4 + i * (w // 8)
            bh = int(h * (0.34 + 0.3 * ((i * 37) % 10) / 10.0))
            d.rectangle([x, base - bh, x + bw - 2, base], fill=(8, 12, 30, 235))
            for wy in range(base - bh + 3, base - 3, 5):
                for wx in range(x + 2, x + bw - 3, 4):
                    if (wx * 7 + wy * 13) % 5 < 2:
                        d.point((wx, wy), fill=(255, 214, 120, 255))
        pts = [(2, int(h * 0.22)), (int(w * 0.3), int(h * 0.34)),
               (int(w * 0.55), int(h * 0.30)), (int(w * 0.8), int(h * 0.62)),
               (w - 3, int(h * 0.78))]
        d.line(pts, fill=(255, 70, 60, 255), width=3)
        d.polygon([(w - 12, int(h * 0.78)), (w - 3, int(h * 0.78)),
                   (w - 4, int(h * 0.66))], fill=(255, 70, 60, 255))
    elif kind == "cricket":
        d.arc([-w * 0.2, h * 0.35, w * 1.2, h * 1.5], 180, 360, fill=(230, 240, 220, 220), width=2)
        for fx in (0.12, 0.88):
            x = int(w * fx)
            d.line([x, 4, x, int(h * 0.4)], fill=(240, 240, 230, 255), width=2)
            for k in range(3):
                d.ellipse([x - 5 + k * 4, 2, x - 2 + k * 4, 5], fill=(255, 255, 210, 255))
        d.rectangle([int(w * 0.42), int(h * 0.45), int(w * 0.58), h - 3], fill=(214, 188, 130, 255))
        d.line([int(w * 0.3), h - 4, int(w * 0.7), h - 4], fill=(255, 255, 255, 200), width=2)
        d.ellipse([int(w * 0.62), int(h * 0.55), int(w * 0.62) + 5, int(h * 0.55) + 5], fill=(200, 30, 30, 255))
    elif kind == "rescue":
        d.polygon([(0, h), (int(w * 0.3), int(h * 0.4)), (int(w * 0.55), h)], fill=(52, 46, 42, 255))
        d.polygon([(int(w * 0.4), h), (int(w * 0.68), int(h * 0.3)), (w, h)], fill=(64, 56, 50, 255))
        d.polygon([(int(w * 0.52), 0), (int(w * 0.66), 0), (int(w * 0.6), int(h * 0.55))], fill=(255, 226, 140, 90))
        cx, cy = int(w * 0.58), int(h * 0.62)
        d.arc([cx - 9, cy - 8, cx + 9, cy + 10], 180, 360, fill=(255, 140, 30, 255), width=4)
        d.ellipse([cx - 3, cy + 2, cx + 3, cy + 8], fill=(246, 200, 150, 255))
        d.line([2, int(h * 0.3), w - 2, int(h * 0.22)], fill=(30, 26, 24, 255), width=3)
    elif kind == "pmi":
        base = h - 3
        d.rectangle([4, int(h * 0.45), int(w * 0.4), base], fill=(16, 22, 36, 240))
        d.polygon([(4, int(h * 0.45)), (int(w * 0.22), int(h * 0.28)), (int(w * 0.4), int(h * 0.45))], fill=(16, 22, 36, 240))
        d.rectangle([int(w * 0.1), int(h * 0.12), int(w * 0.16), int(h * 0.3)], fill=(16, 22, 36, 240))
        cx, cy, r = int(w * 0.68), int(h * 0.62), int(h * 0.42)
        d.pieslice([cx - r, cy - r, cx + r, cy + r], 180, 360, fill=(238, 232, 210, 255))
        d.pieslice([cx - r, cy - r, cx + r, cy + r], 180, 235, fill=(214, 60, 50, 255))
        ang = math.radians(205)
        d.line([cx, cy, cx + int(r * 0.8 * math.cos(ang)), cy + int(r * 0.8 * math.sin(ang))], fill=(20, 20, 20, 255), width=2)
    elif kind == "retail":
        for i in range(8):
            x = 4 + i * (w // 8)
            col = (255, 240, 220, 255) if i % 2 == 0 else (150, 30, 30, 255)
            d.polygon([(x, int(h * 0.3)), (x + w // 8, int(h * 0.3)), (x + w // 16, int(h * 0.46))], fill=col)
        d.rectangle([int(w * 0.34), int(h * 0.48), int(w * 0.66), h - 4], fill=(250, 246, 238, 255))
        d.arc([int(w * 0.44), int(h * 0.34), int(w * 0.56), int(h * 0.56)], 180, 360, fill=(60, 40, 30, 255), width=2)
        d.text((int(w * 0.5), int(h * 0.62)), "%", font=font(COND_B, 16), anchor="mm", fill=(178, 28, 32, 255))
        for i, cx in enumerate((int(w * 0.16), int(w * 0.84))):
            d.ellipse([cx - 6, int(h * 0.6), cx + 6, int(h * 0.6) + 12], fill=(240, 190, 60, 255), outline=(150, 110, 20, 255))
    elif kind == "poll":
        base = h - 3
        d.polygon([(int(w * 0.08), int(h * 0.34)), (int(w * 0.5), int(h * 0.1)), (int(w * 0.92), int(h * 0.34))], fill=(228, 222, 204, 255))
        for i in range(5):
            x = int(w * (0.14 + i * 0.17))
            d.rectangle([x, int(h * 0.36), x + 5, base], fill=(232, 226, 210, 255))
        d.rectangle([int(w * 0.06), base - 3, int(w * 0.94), base], fill=(200, 192, 168, 255))
        d.arc([int(w * 0.42), int(h * 0.02), int(w * 0.58), int(h * 0.3)], 180, 360, fill=(240, 236, 220, 255), width=3)
    elif kind == "bitcoin":
        pts = [(2, int(h * 0.6)), (int(w * 0.3), int(h * 0.48)), (int(w * 0.55), int(h * 0.56)), (w - 2, int(h * 0.2))]
        d.line(pts, fill=(90, 220, 130, 200), width=2)
        cx, cy, r = int(w * 0.5), int(h * 0.52), int(min(w, h) * 0.34)
        for rr, col in [(r, (250, 200, 70, 255)), (int(r * 0.78), (238, 178, 44, 255)), (int(r * 0.6), (250, 200, 70, 255))]:
            d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=col)
        d.text((cx, cy), "B", font=font(COND_B, int(r * 1.05)), anchor="mm", fill=(120, 82, 10, 255))
    elif kind == "nhs":
        cx, cy = int(w * 0.34), int(h * 0.52)
        for rr, col in [(16, (255, 220, 236, 255)), (11, (244, 160, 196, 255)), (6, (214, 80, 140, 255))]:
            d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=col)
        gx = int(w * 0.68)
        d.rectangle([gx - 10, int(h * 0.18), gx + 10, h - 4], outline=(240, 240, 246, 255), width=2)
        for i in range(4):
            y = int(h * (0.28 + i * 0.16))
            d.line([gx - 7, y, gx + 7, y], fill=(200, 235, 255, 220), width=2)
        d.line([int(w * 0.52), cy, gx - 12, cy], fill=(255, 255, 255, 180), width=1)
    elif kind == "hangseng":
        base = h - 3
        for i, bw in enumerate([9, 15, 7, 18, 10, 12]):
            x = 3 + i * (w // 6)
            bh = int(h * (0.4 + 0.32 * ((i * 53) % 9) / 9.0))
            d.rectangle([x, base - bh, x + bw - 2, base], fill=(6, 30, 40, 235))
            for wy in range(base - bh + 3, base - 3, 5):
                for wx in range(x + 1, x + bw - 3, 4):
                    if (wx * 3 + wy * 7) % 4 < 2:
                        d.point((wx, wy), fill=(160, 240, 255, 255))
        pts = [(2, int(h * 0.18)), (int(w * 0.35), int(h * 0.3)), (int(w * 0.62), int(h * 0.26)), (w - 3, int(h * 0.5))]
        d.line(pts, fill=(255, 96, 80, 255), width=3)
    elif kind == "robot":
        base = h - 3
        d.rectangle([int(w * 0.08), int(h * 0.55), int(w * 0.2), base], fill=(30, 30, 40, 255))
        d.line([int(w * 0.14), int(h * 0.55), int(w * 0.4), int(h * 0.22)], fill=(255, 150, 40, 255), width=5)
        d.line([int(w * 0.4), int(h * 0.22), int(w * 0.66), int(h * 0.44)], fill=(255, 150, 40, 255), width=5)
        d.line([int(w * 0.66), int(h * 0.44), int(w * 0.66), int(h * 0.62)], fill=(200, 200, 210, 255), width=3)
        d.ellipse([int(w * 0.1), int(h * 0.5), int(w * 0.18), int(h * 0.5) + 8], fill=(90, 90, 105, 255))
        d.ellipse([int(w * 0.36), int(h * 0.17), int(w * 0.44), int(h * 0.17) + 8], fill=(90, 90, 105, 255))
        d.rectangle([int(w * 0.56), int(h * 0.66), int(w * 0.78), base], outline=(220, 220, 230, 255), width=2)
        for sx in (int(w * 0.84), int(w * 0.9)):
            d.point((sx, int(h * 0.3)), fill=(120, 255, 160, 255))
    elif kind == "music":
        for fx in (0.22, 0.78):
            d.polygon([(int(w * fx), 0), (int(w * fx) - 12, h - 2), (int(w * fx) + 12, h - 2)], fill=(255, 240, 180, 46))
        mx, my = int(w * 0.5), int(h * 0.34)
        d.line([mx, my, mx, h - 4], fill=(210, 210, 220, 255), width=2)
        d.ellipse([mx - 5, my - 9, mx + 5, my + 3], fill=(30, 30, 36, 255), outline=(200, 200, 210, 255))
        d.text((int(w * 0.3), int(h * 0.6)), "♪", font=font(COND_B, 18), anchor="mm", fill=(255, 210, 240, 255))
        d.text((int(w * 0.7), int(h * 0.5)), "♪", font=font(COND_B, 14), anchor="mm", fill=(190, 220, 255, 255))
    return lay

def make_panel(w, h, card, seed):
    pal = PALETTES[card["kind"]]
    img = gradient_panel(w, h, pal[0], pal[1], pal[2], seed)
    d = ImageDraw.Draw(img)
    ban_h, src_h = 16, 14
    # scene, clipped to the middle zone so it can never touch the tags
    scene = scene_layer(w, h - ban_h - src_h, card["kind"], seed)
    img.paste(scene, (0, ban_h), scene)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, w, ban_h], fill=(12, 12, 14))
    bf = font(COND_B, 12)
    if bf.getlength(card["banner"]) > w - 4:
        bf = font(EXTRA_B, 11)
    if bf.getlength(card["banner"]) > w - 4:
        bf = font(EXTRA_B, 10)
    d.text((w // 2, ban_h // 2), card["banner"], font=bf, anchor="mm", fill=(255, 246, 220))
    d.rectangle([0, h - src_h, w, h], fill=(246, 240, 222))
    d.text((w // 2, h - src_h // 2), card["source"], font=font(COND, 11), anchor="mm", fill=(52, 44, 32))
    d.rectangle([0, 0, w - 1, h - 1], outline=(30, 26, 20), width=1)
    return img


# ---------- page ----------
def build():
    data = json.load(open(os.path.join(HERE, "data.json")))
    # cream background: smooth vertical gradient + gentle sinusoidal shading
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float64)
    t = yy / (H - 1)
    arr = np.zeros((H, W, 3), np.float64)
    for ch in range(3):
        shade = (1.6 * np.sin(xx * (0.011 + 0.0016 * ch) + yy * 0.004 + ch * 1.4)
                 + 1.1 * np.cos(yy * (0.016 - 0.001 * ch) + xx * 0.002 + ch * 0.7))
        arr[:, :, ch] = CREAM_TOP[ch] + (CREAM_BOT[ch] - CREAM_TOP[ch]) * t + shade
    img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")
    d = ImageDraw.Draw(img)
    M = 16
    CW = W - 2 * M

    # strap
    d.text((W // 2, 6), data["strap"], font=font(COND_B, 20), anchor="ma", fill=RED)
    d.line([M, 32, W - M, 32], fill=INK, width=2)

    # giant date: serif condensed bold at 106px, rendered then squeezed
    # horizontally (only) so the full line fits the measure at that size.
    DATE_SIZE = 106
    fdate = font(SERIF_CB, DATE_SIZE)
    tw = int(fdate.getlength(data["date_line"]))
    layer = Image.new("RGBA", (tw + 8, DATE_SIZE + 8), (0, 0, 0, 0))
    ImageDraw.Draw(layer).text((4, 0), data["date_line"], font=fdate, fill=INK + (255,))
    layer = layer.resize((CW, DATE_SIZE + 8), Image.LANCZOS)
    img.paste(layer, (M, 36), layer)
    d = ImageDraw.Draw(img)
    date_bottom = 36 + DATE_SIZE + 8
    d.line([M, date_bottom, W - M, date_bottom], fill=INK, width=2)

    # stat band: navy horizontal gradient
    sy = date_bottom + 4
    band = gradient_panel(CW, 42, (26, 58, 110), (18, 42, 84), (12, 30, 62), 999, grain=4)
    img.paste(band, (M, sy))
    d = ImageDraw.Draw(img)
    colw = CW // 4
    for i, s in enumerate(data["stats"]):
        x = M + i * colw + 8
        d.text((x, sy + 4), s["k"], font=font(COND_B, 14), anchor="la", fill=(170, 200, 245))
        d.text((x, sy + 17), s["v"], font=font(COND_B, 24), anchor="la", fill=(255, 255, 255))
        sx = x + int(font(COND_B, 24).getlength(s["v"])) + 8
        d.text((sx, sy + 23), s["s"], font=font(COND, 13), anchor="la", fill=(214, 226, 246))
        if i:
            d.line([M + i * colw, sy + 4, M + i * colw, sy + 40], fill=(140, 170, 220), width=1)
    ry = sy + 46
    d.text((W // 2, ry), data["region"], font=font(COND_B, 17), anchor="ma", fill=NAVY)

    # cards
    cards = data["cards"]
    y = ry + 22
    gap = 6
    def draw_card(card, x, y, w, h, lead):
        d.rounded_rectangle([x, y, x + w, y + h], 6, fill=CARD_BG, outline=CARD_LINE, width=1)
        aw = 168 if lead else 88
        ah = 88 if lead else 68
        panel = make_panel(aw, ah, card, seed=1000 + card["n"] * 131)
        img.paste(panel, (x + 6, y + 6))
        tx = x + 12 + aw
        twd = x + w - 8 - tx
        hsize = 40 if lead else 36
        hf, hl = fit_lines(card["headline"], int(twd / 0.90), hsize, 2)
        lead_h = 42 if lead else 37
        maxw_line = max(hf.getlength(ln) for ln in hl) if hl else 0
        if maxw_line <= twd:
            for j, ln in enumerate(hl):
                d.text((tx, y + 5 + j * lead_h), ln, font=hf, anchor="la", fill=INK)
        else:
            lay = Image.new("RGBA", (int(maxw_line) + 6, lead_h * len(hl) + 8), (0, 0, 0, 0))
            ld = ImageDraw.Draw(lay)
            for j, ln in enumerate(hl):
                ld.text((3, j * lead_h), ln, font=hf, anchor="la", fill=INK + (255,))
            lay = lay.resize((twd, lay.height), Image.LANCZOS)
            img.paste(lay, (tx, y + 5), lay)
        # number chip on the bottom-right corner, clear of headline and body
        d.ellipse([x + w - 22, y + h - 22, x + w - 2, y + h - 2], fill=RED)
        d.text((x + w - 12, y + h - 12), str(card["n"]), font=font(COND_B, 13), anchor="mm", fill=(255, 255, 255))
        bf = font(COND, 17 if lead else 16)
        bl = wrap(card["body"], bf, w - 16)
        by = y + 96 if lead else y + 78
        for j, ln in enumerate(bl[:2]):
            d.text((x + 8, by + j * 19), ln, font=bf, anchor="la", fill=(52, 48, 40))
    # leads row
    lw = (CW - gap) // 2
    draw_card(cards[0], M, y, lw, 134, True)
    draw_card(cards[1], M + lw + gap, y, lw, 134, True)
    y += 134 + gap
    sw = (CW - 2 * gap) // 3
    for r in range(3):
        for c in range(3):
            draw_card(cards[2 + r * 3 + c], M + c * (sw + gap), y, sw, 116, False)
        y += 116 + gap
    cards_bottom = y - gap

    # briefs band
    by0 = cards_bottom + 4
    d.rectangle([M, by0, W - M, by0 + 62], fill=(238, 230, 208), outline=CARD_LINE)
    d.text((M + 8, by0 + 3), "BRIEFS - MONDAY, PLACE-LED, SOURCED", font=font(COND_B, 13), anchor="la", fill=RED)
    bf = font(COND, 14)
    for i, b in enumerate(data["briefs"]):
        d.text((M + 8, by0 + 18 + i * 15), b, font=bf, anchor="la", fill=(52, 48, 40))

    # DATE CHECK box
    dy = by0 + 66
    d.rectangle([M, dy, W - M, dy + 28], fill=RED)
    d.text((W // 2, dy + 14), data["datecheck_heading"], font=font(COND_B, 24), anchor="mm", fill=(255, 255, 255))
    iy = dy + 32
    d.rectangle([M, iy, W - M, iy + 150], fill=(250, 246, 234), outline=RED, width=2)
    df = font(COND, 24)
    dfl = font(COND_B, 24)
    col_w = (CW - 24) // 2
    for i, item in enumerate(data["datecheck"]):
        cx = M + 10 + (i % 2) * (col_w + 8)
        cy = iy + 4 + (i // 2) * 49
        day = item["day"] + "  "
        dw = dfl.getlength(day)
        d.text((cx, cy), day, font=dfl, anchor="la", fill=RED)
        ls = wrap(item["text"], df, col_w - dw)
        # if the remainder needs a second line it continues full-width below
        first = ls[0] if ls else ""
        d.text((cx + dw, cy), first, font=df, anchor="la", fill=INK)
        rest = " ".join(ls[1:])
        if rest:
            ls2 = wrap(rest, df, col_w)
            d.text((cx, cy + 24), ls2[0], font=df, anchor="la", fill=INK)

    # not-yet line
    ny = iy + 154
    d.rectangle([M, ny, W - M, ny + 24], fill=INK)
    d.text((W // 2, ny + 12), data["notyet"], font=font(COND_B, 16), anchor="mm", fill=(255, 250, 235))
    # footer
    d.text((W // 2, ny + 28), data["footer"], font=font(COND, 13), anchor="ma", fill=(90, 82, 66))

    out = os.path.join(HERE, "entry.png")
    img.save(out, optimize=False)
    print(out)

if __name__ == "__main__":
    build()
