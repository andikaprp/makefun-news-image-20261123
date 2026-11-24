#!/usr/bin/env python3
"""Slot 3 V2 renderer, REVISION 2 (councilor pass) - news-image-20261123.
Rebuild of this lane's own V2 renderer:
- card architecture rebuilt to the winners' hierarchy: 3 wide hero leads
  with top pictorial panels (~top half) + 11 compact top-panel cards;
- EVERY scene is rendered into its own panel-sized image and pasted in,
  so art is structurally clipped to its panel bounds and can never cross
  a panel edge (COP31 hill overflow is impossible by construction);
- panels carry census figures as in-graphic data labels;
- footer DATE CHECK box is 52px tall with re-spaced rail lines, so no
  rail glyph can touch the box border;
- slim UTC timeline strip restored under the stat band.
Stdlib + Pillow only. Deterministic: same data.json -> same entry.png.
"""
import json
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W = H = 1024
BG = (247, 241, 227)
CARD_BG = (252, 248, 236)
INK = (26, 24, 20)
MUTED = (96, 88, 74)
RULE = (43, 38, 30)
ACCENT = (154, 32, 24)
BAND = (238, 228, 203)
BAND_LINE = (196, 178, 140)

NOTO = "/usr/share/fonts/truetype/noto"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
COND_B = f"{NOTO}/NotoSans-CondensedBold.ttf"
XCOND_B = f"{NOTO}/NotoSans-ExtraCondensedBold.ttf"
COND = f"{NOTO}/NotoSans-Condensed.ttf"
XCOND = f"{NOTO}/NotoSans-ExtraCondensed.ttf"
COND_SB = f"{NOTO}/NotoSans-SemiCondensedBold.ttf"

_cache = {}
def F(path, size):
    key = (path, size)
    if key not in _cache:
        _cache[key] = ImageFont.truetype(path, size)
    return _cache[key]

def tw(draw, text, font):
    return draw.textlength(text, font=font)

def wrap(draw, text, font, max_w):
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if tw(draw, t, font) <= max_w or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines

def fit_headline(draw, text, max_w, max_lines, start, minimum, max_h=10**9, path=COND_B):
    size = start
    while size > minimum:
        f = F(path, size)
        lines = wrap(draw, text, f, max_w)
        if len(lines) <= max_lines and len(lines) * int(size * 1.10) <= max_h:
            return f, lines, size
        size -= 1
    f = F(path, minimum)
    return f, wrap(draw, text, f, max_w), minimum

def fit_one(draw, text, max_w, start, minimum, path=COND):
    size = start
    while size > minimum and tw(draw, text, F(path, size)) > max_w:
        size -= 1
    return F(path, size), size

def vgrad(img, box, top, bot):
    x0, y0, x1, y1 = box
    d = ImageDraw.Draw(img)
    h = max(1, y1 - y0)
    for i in range(h):
        t = i / h
        c = tuple(int(top[k] + (bot[k] - top[k]) * t) for k in range(3))
        d.line([(x0, y0 + i), (x1, y0 + i)], fill=c)

# ---------------------------------------------------------------- scenes
# Scenes draw into a panel-sized image at box (0,0,pw,ph); the caller
# pastes that image in, so no scene element can ever leave its panel.

def sc_chip(img, b):
    vgrad(img, b, (222, 238, 208), (206, 232, 190))
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = b
    w_, h_ = x1 - x0, y1 - y0
    pts = [(x0 + 6, y1 - 12), (x0 + w_ * .3, y1 - h_ * .34), (x0 + w_ * .55, y1 - h_ * .44),
           (x0 + w_ * .78, y1 - h_ * .72), (x1 - 8, y0 + 10)]
    area = pts + [(x1 - 4, y1 - 4), (x0 + 4, y1 - 4)]
    d.polygon(area, fill=(96, 178, 110))
    d.line(pts, fill=(24, 110, 52), width=4)
    for (px, py) in pts:
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(24, 110, 52))
    ex, ey = pts[-1]
    d.polygon([(ex, ey), (ex - 12, ey + 3), (ex - 3, ey + 12)], fill=(24, 110, 52))
    cx, cy, s = x0 + w_ * .2, y0 + h_ * .26, min(w_, h_) * .3
    d.rounded_rectangle([cx - s/2, cy - s/2, cx + s/2, cy + s/2], 5, fill=(24, 42, 34), outline=(255, 214, 90), width=3)
    d.rounded_rectangle([cx - s/4, cy - s/4, cx + s/4, cy + s/4], 3, fill=(70, 120, 92), outline=(255, 214, 90), width=2)
    for k in range(3):
        px = cx - s/2 + (k + .5) * s / 3
        d.line([(px, cy - s/2 - 6), (px, cy - s/2)], fill=(255, 214, 90), width=3)
        d.line([(px, cy + s/2), (px, cy + s/2 + 6)], fill=(255, 214, 90), width=3)

def sc_grainship(img, b):
    vgrad(img, b, (219, 231, 241), (208, 226, 238))
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = b
    w_, h_ = x1 - x0, y1 - y0
    d.polygon([(x0, y0 + h_ * .3), (x0 + w_ * .16, y0 + h_ * .52), (x0, y1)], fill=(110, 96, 78))
    d.polygon([(x1, y0 + h_ * .24), (x1 - w_ * .14, y0 + h_ * .5), (x1, y1)], fill=(96, 84, 68))
    sea = y0 + h_ * .66
    d.rectangle([x0, sea, x1, y1], fill=(216, 228, 238))
    for k in range(2):
        yy = sea + 7 + k * 9
        d.arc([x0 + 6 + (k % 2) * 16, yy, x1 - 6, yy + 9], 0, 180, fill=(90, 140, 190), width=2)
    hx0, hx1 = x0 + w_ * .2, x0 + w_ * .82
    d.polygon([(hx0, sea - 2), (hx1, sea - 2), (hx1 - 8, sea - 14), (hx0 + 6, sea - 14)], fill=(30, 34, 40))
    d.polygon([(hx0 + 12, sea - 14), (hx0 + w_ * .3 + 12, sea - 26), (hx1 - 16, sea - 14)], fill=(238, 186, 84))
    d.rectangle([hx1 - 22, sea - 32, hx1 - 8, sea - 14], fill=(30, 34, 40))
    d.rectangle([hx0 + 8, sea - 28, hx0 + 18, sea - 14], fill=(30, 34, 40))
    ax = hx0 + 16
    d.line([(ax, sea - 12), (ax, sea + 8)], fill=(240, 240, 230), width=2)
    d.arc([ax - 7, sea + 2, ax + 7, sea + 14], 20, 160, fill=(240, 240, 230), width=2)
    for k, fx in enumerate((0.86, 0.92, 0.97)):
        bx, by = x0 + w_ * fx, y1 - 2
        top = by - h_ * (0.34 + 0.05 * (k % 2))
        d.line([(bx, by), (bx - 2, top)], fill=(214, 164, 60), width=2)
        for j in range(4):
            gy = top + 3 + j * 5
            d.ellipse([bx - 6, gy, bx - 1, gy + 5], fill=(246, 205, 105))
            d.ellipse([bx + 1, gy, bx + 6, gy + 5], fill=(246, 205, 105))

def sc_rubble(img, b):
    vgrad(img, b, (233, 224, 207), (224, 213, 194))
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = b
    w_, h_ = x1 - x0, y1 - y0
    d.rectangle([x0 + 6, y0 + h_ * .2, x0 + w_ * .44, y1 - 14], fill=(168, 156, 140), outline=(80, 70, 58), width=2)
    for r in range(3):
        for c in range(2):
            wx, wy = x0 + 13 + c * w_ * .16, y0 + h_ * .28 + r * h_ * .19
            col = (70, 64, 56) if (r + c) % 2 else (240, 218, 160)
            d.rectangle([wx, wy, wx + w_ * .11, wy + h_ * .12], fill=col)
    d.polygon([(x0 + w_ * .44, y0 + h_ * .2), (x0 + w_ * .62, y0 + h_ * .46), (x0 + w_ * .44, y1 - 14)], fill=(120, 108, 94))
    d.polygon([(x0 + w_ * .52, y1 - 30), (x0 + w_ * .86, y1 - 44), (x0 + w_ * .9, y1 - 30), (x0 + w_ * .56, y1 - 16)], fill=(140, 128, 112), outline=(80, 70, 58))
    d.polygon([(x1 - 8, y0 + 6), (x0 + w_ * .58, y1 - 26), (x0 + w_ * .78, y1 - 20)], fill=(252, 240, 190))
    d.ellipse([x1 - 15, y0 + 2, x1 - 3, y0 + 13], fill=(255, 250, 220), outline=(120, 100, 60))
    d.polygon([(x0 + 3, y1 - 3), (x0 + w_ * .4, y1 - 18), (x0 + w_ * .74, y1 - 10), (x1 - 3, y1 - 3)], fill=(100, 88, 74))
    for (mx, my) in [(0.3, 0.86), (0.55, 0.8), (0.68, 0.9)]:
        d.ellipse([x0 + w_ * mx - 3, y0 + h_ * my - 3, x0 + w_ * mx + 3, y0 + h_ * my + 3], fill=(240, 110, 30))

def sc_factory(img, b):
    vgrad(img, b, (244, 227, 206), (238, 216, 192))
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = b
    w_, h_ = x1 - x0, y1 - y0
    d.rectangle([x0 + 6, y1 - h_ * .42, x1 - 6, y1 - 8], fill=(110, 92, 78), outline=(60, 48, 40), width=2)
    d.polygon([(x0 + 6, y1 - h_ * .42), (x0 + w_ * .3, y1 - h_ * .56), (x0 + w_ * .55, y1 - h_ * .42)], fill=(84, 68, 58))
    d.rectangle([x0 + w_ * .72, y0 + h_ * .3, x0 + w_ * .82, y1 - 8], fill=(94, 76, 64))
    for (sx, sy, sr, col) in [(0.76, 0.24, 0.13, (140, 128, 120)), (0.68, 0.15, 0.1, (168, 156, 146)), (0.8, 0.1, 0.08, (192, 182, 172))]:
        d.ellipse([x0 + w_ * (sx - sr), y0 + h_ * (sy - sr), x0 + w_ * (sx + sr), y0 + h_ * (sy + sr)], fill=col)
    for k, fx in enumerate((0.24, 0.38, 0.5)):
        fh = h_ * (0.3 - 0.05 * (k % 2))
        d.polygon([(x0 + w_ * fx - 9, y1 - h_ * .42), (x0 + w_ * fx, y1 - h_ * .42 - fh), (x0 + w_ * fx + 9, y1 - h_ * .42)], fill=(238, 120, 36))
        d.polygon([(x0 + w_ * fx - 5, y1 - h_ * .42), (x0 + w_ * fx, y1 - h_ * .42 - fh * .6), (x0 + w_ * fx + 5, y1 - h_ * .42)], fill=(252, 200, 70))

def sc_shield(img, b):
    vgrad(img, b, (52, 92, 140), (110, 165, 205))
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = b
    w_, h_ = x1 - x0, y1 - y0
    nodes = [(0.14, 0.2), (0.3, 0.78), (0.86, 0.16), (0.9, 0.78), (0.66, 0.9)]
    for (ax, ay) in nodes:
        for (bx, by) in nodes:
            d.line([(x0 + w_ * ax, y0 + h_ * ay), (x0 + w_ * bx, y0 + h_ * by)], fill=(150, 195, 235), width=1)
    for (ax, ay) in nodes:
        d.ellipse([x0 + w_ * ax - 4, y0 + h_ * ay - 4, x0 + w_ * ax + 4, y0 + h_ * ay + 4], fill=(205, 232, 255))
    def shield(cx, cy, s, fill):
        d.polygon([(cx - s, cy - s * .8), (cx + s, cy - s * .8), (cx + s, cy + s * .2), (cx, cy + s * 1.05), (cx - s, cy + s * .2)],
                  fill=fill, outline=(255, 224, 110), width=3)
    shield(x0 + w_ * .38, y0 + h_ * .44, min(w_, h_) * .24, (28, 110, 150))
    shield(x0 + w_ * .62, y0 + h_ * .54, min(w_, h_) * .3, (20, 105, 66))
    cx, cy, s = x0 + w_ * .62, y0 + h_ * .54, min(w_, h_) * .3
    d.line([(cx - s * .45, cy), (cx - s * .1, cy + s * .38), (cx + s * .5, cy - s * .42)], fill=(255, 255, 255), width=5)

def sc_ship(img, b):
    vgrad(img, b, (219, 231, 241), (196, 218, 234))
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = b
    w_, h_ = x1 - x0, y1 - y0
    d.ellipse([x0 + w_ * .06, y0 + 8, x0 + w_ * .3, y0 + 8 + w_ * .24], fill=(252, 232, 160))
    sea = y0 + h_ * .62
    for k in range(3):
        yy = sea + 8 + k * 9
        d.arc([x0 + 4 + (k % 2) * 14, yy, x1 - 4, yy + 10], 0, 180, fill=(175, 215, 240), width=2)
    d.polygon([(x0 + w_ * .18, sea), (x0 + w_ * .82, sea), (x0 + w_ * .72, sea - 12), (x0 + w_ * .26, sea - 12)], fill=(26, 36, 48))
    d.rectangle([x0 + w_ * .4, sea - 30, x0 + w_ * .62, sea - 12], fill=(26, 36, 48))
    d.rectangle([x0 + w_ * .55, sea - 44, x0 + w_ * .6, sea - 30], fill=(26, 36, 48))
    d.line([(x0 + w_ * .34, sea - 12), (x0 + w_ * .3, sea - 34)], fill=(26, 36, 48), width=3)
    for (dx, dy) in [(0.2, 0.2), (0.78, 0.16), (0.6, 0.3)]:
        px, py = x0 + w_ * dx, y0 + h_ * dy
        d.line([(px - 8, py), (px + 8, py)], fill=(255, 244, 205), width=3)
        d.line([(px, py - 5), (px, py + 5)], fill=(255, 244, 205), width=2)
        d.arc([px - 16, py + 4, px + 16, py + 30], 20, 160, fill=(255, 200, 100), width=2)

def sc_trophy(img, b):
    vgrad(img, b, (220, 238, 205), (206, 232, 192))
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = b
    w_, h_ = x1 - x0, y1 - y0
    cols = [(214, 48, 49), (250, 200, 60), (52, 110, 200), (240, 240, 240), (30, 130, 76), (52, 110, 200)]
    for k, col in enumerate(cols):
        fx = x0 + 6 + k * (w_ - 12) / 5
        d.line([(fx, y0 + 3), (fx, y0 + 13)], fill=(50, 50, 50), width=1)
        d.polygon([(fx, y0 + 13), (fx + 9, y0 + 16), (fx, y0 + 20)], fill=col)
    d.pieslice([x0 + 4, y0 + h_ * .42, x1 - 4, y1 + h_ * .34], 0, 180, fill=(232, 230, 220), outline=(100, 100, 94), width=2)
    d.ellipse([x0 + w_ * .24, y0 + h_ * .6, x1 - w_ * .24, y0 + h_ * .9], fill=(52, 150, 78), outline=(255, 255, 255), width=2)
    cx = x0 + w_ * .5
    top, bot = y0 + h_ * .2, y0 + h_ * .66
    gold, gold_d = (246, 196, 64), (196, 144, 36)
    d.polygon([(cx - w_ * .13, top), (cx + w_ * .13, top), (cx + w_ * .07, top + (bot - top) * .45), (cx - w_ * .07, top + (bot - top) * .45)], fill=gold, outline=gold_d, width=2)
    d.arc([cx - w_ * .22, top + 2, cx - w_ * .1, top + (bot - top) * .42], 90, 270, fill=gold_d, width=4)
    d.arc([cx + w_ * .1, top + 2, cx + w_ * .22, top + (bot - top) * .42], 270, 90, fill=gold_d, width=4)
    d.rectangle([cx - 4, top + (bot - top) * .45, cx + 4, bot - 8], fill=gold_d)
    d.rectangle([cx - w_ * .11, bot - 8, cx + w_ * .11, bot], fill=gold_d)
    d.ellipse([cx - 7, top + 5, cx + 7, top + 19], fill=(255, 240, 180))

def _chart(img, b, up, col_top, col_bot, line_col):
    vgrad(img, b, col_top, col_bot)
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = b
    w_, h_ = x1 - x0, y1 - y0
    for k in range(3):
        yy = y0 + h_ * (.25 + .22 * k)
        d.line([(x0 + 5, yy), (x1 - 5, yy)], fill=(255, 255, 255), width=1)
    for k, bh in enumerate((0.2, 0.34, 0.26, 0.42, 0.3)):
        bx = x0 + 6 + k * (w_ - 12) / 5
        d.rectangle([bx, y1 - 6 - h_ * bh, bx + (w_ - 12) / 5 - 4, y1 - 6], fill=(52, 58, 68))
    if up:
        pts = [(x0 + 7, y1 - h_ * .3), (x0 + w_ * .32, y1 - h_ * .42), (x0 + w_ * .55, y1 - h_ * .38), (x0 + w_ * .78, y1 - h_ * .68), (x1 - 7, y1 - h_ * .82)]
    else:
        pts = [(x0 + 7, y0 + h_ * .18), (x0 + w_ * .3, y0 + h_ * .3), (x0 + w_ * .52, y0 + h_ * .28), (x0 + w_ * .76, y1 - h_ * .3), (x1 - 7, y1 - h_ * .18)]
    d.line(pts, fill=line_col, width=4)
    for (px, py) in pts:
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=line_col)
    ex, ey = pts[-1]
    d.polygon([(ex, ey), (ex - 10, ey + (2 if up else -8)), (ex - 2, ey + (10 if up else 2))], fill=line_col)

def sc_chartdown(img, b):
    _chart(img, b, False, (240, 223, 206), (236, 214, 196), (168, 44, 34))

def sc_chartdown2(img, b):
    _chart(img, b, False, (242, 229, 203), (238, 219, 190), (150, 88, 18))

def sc_mountains(img, b):
    vgrad(img, b, (249, 230, 198), (216, 226, 236))
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = b
    w_, h_ = x1 - x0, y1 - y0
    d.ellipse([x0 + w_ * .62, y0 + 8, x0 + w_ * .9, y0 + 8 + w_ * .28], fill=(255, 244, 196))
    d.polygon([(x0 + 2, y1 - 10), (x0 + w_ * .34, y0 + h_ * .3), (x0 + w_ * .62, y1 - 10)], fill=(110, 126, 142))
    d.polygon([(x0 + w_ * .3, y1 - 10), (x0 + w_ * .62, y0 + h_ * .18), (x0 + w_ * .96, y1 - 10)], fill=(88, 106, 126))
    for (mx, my) in [(0.34, 0.3), (0.62, 0.18)]:
        px, py = x0 + w_ * mx, y0 + h_ * my
        d.polygon([(px - 10, py + 10), (px, py), (px + 10, py + 10), (px + 3, py + 6), (px, py + 10), (px - 4, py + 5)], fill=(250, 250, 252))
    d.polygon([(x0 + w_ * .42, y1 - 10), (x0 + w_ * .55, y1 - 34), (x0 + w_ * .62, y1 - 10)], fill=(100, 180, 225))
    for k in range(2):
        bx, by = x0 + w_ * (.12 + .16 * k), y1 - 24
        d.rectangle([bx, by, bx + 16, by + 13], fill=(205, 135, 60), outline=(100, 62, 24), width=2)
        d.line([(bx, by + 6), (bx + 16, by + 6)], fill=(100, 62, 24), width=1)

def sc_bars(img, b):
    vgrad(img, b, (232, 237, 242), (185, 198, 212))
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = b
    w_, h_ = x1 - x0, y1 - y0
    fy = y0 + h_ * .34
    d.rectangle([x0 + w_ * .55, fy, x1 - 8, y1 - 14], fill=(168, 180, 194))
    d.polygon([(x0 + w_ * .55, fy), (x0 + w_ * .68, fy - h_ * .1), (x0 + w_ * .8, fy), (x0 + w_ * .92, fy - h_ * .1), (x1 - 8, fy)], fill=(168, 180, 194))
    d.rectangle([x0 + w_ * .86, fy - h_ * .24, x0 + w_ * .92, fy], fill=(150, 164, 180))
    base = y1 - 14
    d.line([(x0 + 6, base), (x1 - 6, base)], fill=(60, 66, 76), width=3)
    heights = [0.34, 0.52, 0.78, 0.24, 0.16]
    cols = [(100, 122, 152), (100, 122, 152), (36, 140, 84), (64, 104, 180), (64, 104, 180)]
    bw = (w_ - 16) / 5
    for k, (hh, col) in enumerate(zip(heights, cols)):
        bx = x0 + 8 + k * bw
        d.rectangle([bx, base - h_ * hh, bx + bw - 5, base], fill=col, outline=(44, 48, 56), width=1)
    d.line([(x0 + 8, y0 + h_ * .18), (x1 - 8, y0 + h_ * .1)], fill=(36, 140, 84), width=3)

def sc_parliament(img, b):
    vgrad(img, b, (219, 231, 241), (212, 228, 238))
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = b
    w_, h_ = x1 - x0, y1 - y0
    d.pieslice([x0 - w_ * .2, y0 + h_ * .48, x1 + w_ * .2, y1 + h_ * .5], 180, 360, fill=(96, 168, 92))
    d.rectangle([x0, y1 - h_ * .26, x1, y1], fill=(96, 168, 92))
    bx0, bx1, by = x0 + w_ * .14, x0 + w_ * .86, y0 + h_ * .58
    d.rectangle([bx0, by, bx1, by + h_ * .2], fill=(238, 238, 234), outline=(110, 110, 104), width=1)
    for k in range(5):
        vx = bx0 + 6 + k * (bx1 - bx0 - 12) / 4
        d.rectangle([vx, by + 4, vx + 5, by + h_ * .2 - 4], fill=(120, 150, 180))
    d.polygon([(bx0 - 4, by), (x0 + w_ * .5, by - h_ * .22), (bx1 + 4, by)], fill=(245, 245, 242), outline=(110, 110, 104))
    mx = x0 + w_ * .5
    d.line([(mx, by - h_ * .22), (mx, by - h_ * .52)], fill=(60, 60, 60), width=3)
    d.polygon([(mx, by - h_ * .52), (mx + w_ * .17, by - h_ * .46), (mx, by - h_ * .4)], fill=(40, 70, 150))
    for (sx, sy) in [(0.53, 0.06), (0.56, 0.1), (0.545, 0.14)]:
        d.ellipse([x0 + w_ * sx - 2, y0 + h_ * sy - 2, x0 + w_ * sx + 2, y0 + h_ * sy + 2], fill=(250, 250, 250))
    px, py = x0 + w_ * .16, y1 - h_ * .3
    d.polygon([(px - 12, y1 - 4), (px - 8, py), (px + 14, py), (px + 10, y1 - 4)], fill=(90, 60, 40))
    d.line([(px, py), (px - 8, py - 12)], fill=(30, 30, 30), width=2)
    d.line([(px + 4, py), (px + 10, py - 13)], fill=(30, 30, 30), width=2)
    d.ellipse([px - 11, py - 15, px - 5, py - 9], fill=(30, 30, 30))
    d.ellipse([px + 7, py - 16, px + 13, py - 10], fill=(30, 30, 30))

def sc_drones(img, b):
    vgrad(img, b, (52, 62, 102), (120, 130, 168))
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = b
    w_, h_ = x1 - x0, y1 - y0
    d.ellipse([x0 + w_ * .72, y0 + 8, x0 + w_ * .92, y0 + 8 + w_ * .2], fill=(240, 242, 224))
    d.ellipse([x0 + w_ * .68, y0 + 6, x0 + w_ * .86, y0 + 6 + w_ * .18], fill=(52, 62, 102))
    d.polygon([(x0 + w_ * .2, y1 - 8), (x0 + w_ * .44, y0 + h_ * .3), (x0 + w_ * .56, y0 + h_ * .34)], fill=(244, 234, 178))
    d.polygon([(x0 + w_ * .85, y1 - 8), (x0 + w_ * .6, y0 + h_ * .42), (x0 + w_ * .7, y0 + h_ * .46)], fill=(228, 222, 170))
    for (dx, dy, s) in [(0.3, 0.24, 1.0), (0.55, 0.16, 0.8), (0.72, 0.34, 0.9), (0.16, 0.44, 0.7)]:
        px, py = x0 + w_ * dx, y0 + h_ * dy
        d.line([(px - 11 * s, py), (px + 11 * s, py)], fill=(245, 248, 252), width=3)
        d.line([(px, py - 4 * s), (px, py + 6 * s)], fill=(245, 248, 252), width=2)
        d.ellipse([px - 3, py - 2, px + 3, py + 3], fill=(255, 130, 95))
    d.rectangle([x0 + 3, y1 - 16, x0 + w_ * .3, y1 - 3], fill=(30, 34, 52))
    d.rectangle([x0 + w_ * .62, y1 - 12, x1 - 3, y1 - 3], fill=(30, 34, 52))

def sc_volcano(img, b):
    vgrad(img, b, (226, 211, 199), (218, 198, 184))
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = b
    w_, h_ = x1 - x0, y1 - y0
    cx = x0 + w_ * .5
    crater_y = y0 + h_ * .52
    for k, (dx, hh, wd) in enumerate([(-0.1, 0.42, 5), (0.0, 0.5, 7), (0.1, 0.4, 5), (-0.05, 0.34, 4), (0.06, 0.3, 4)]):
        fx = cx + w_ * dx
        top = crater_y - h_ * hh
        d.arc([fx - wd * 2.2, top, fx + wd * 2.2, crater_y + 4], 300, 60, fill=(255, 170, 60), width=wd)
        d.arc([fx - wd * 1.4, top + 6, fx + wd * 1.4, crater_y + 4], 300, 60, fill=(255, 220, 130), width=max(2, wd - 2))
    d.ellipse([cx - 12, crater_y - 8, cx + 12, crater_y + 3], fill=(255, 190, 80))
    d.polygon([(x0 + 4, y1 - 4), (cx - w_ * .13, crater_y), (cx + w_ * .13, crater_y), (x1 - 4, y1 - 4)], fill=(58, 44, 44))
    d.polygon([(cx - w_ * .13, crater_y), (cx + w_ * .13, crater_y), (cx + w_ * .3, y1 - 4), (cx + w_ * .08, y1 - 4)], fill=(76, 56, 50))
    pts = [(cx + w_ * .04, crater_y + 2), (cx + w_ * .16, y0 + h_ * .72), (cx + w_ * .24, y1 - 6)]
    d.line(pts, fill=(255, 140, 40), width=6)
    d.line(pts, fill=(255, 205, 110), width=2)
    for (sx, sy) in [(0.38, 0.2), (0.6, 0.14), (0.68, 0.3), (0.3, 0.34)]:
        d.ellipse([x0 + w_ * sx - 2, y0 + h_ * sy - 2, x0 + w_ * sx + 2, y0 + h_ * sy + 2], fill=(255, 190, 90))

SCENES = {"chip": sc_chip, "grainship": sc_grainship, "rubble": sc_rubble, "factory": sc_factory,
          "shield": sc_shield, "ship": sc_ship, "trophy": sc_trophy,
          "chartdown": sc_chartdown, "chartdown2": sc_chartdown2,
          "mountains": sc_mountains, "bars": sc_bars, "parliament": sc_parliament,
          "drones": sc_drones, "volcano": sc_volcano}

# ---------------------------------------------------------------- layout
MX = 16
CW = W - 2 * MX

def draw_panel(img, draw, card, x, y, w_, ph):
    """Render the scene into its own image and paste it: art is clipped
    to the panel by construction. Then the census data label chip."""
    pw = w_ - 12
    tmp = Image.new("RGB", (pw, ph), BG)
    SCENES[card["scene"]](tmp, (0, 0, pw, ph))
    img.paste(tmp, (x + 6, y + 5))
    draw.rectangle([x + 6, y + 5, x + 6 + pw, y + 5 + ph], outline=(30, 28, 24), width=2)
    lab = card.get("label")
    if lab:
        lf = F(COND_B, 15)
        lw = tw(draw, lab, lf)
        cx0, cy0 = x + 12, y + 5 + ph - 25
        draw.rectangle([cx0 - 4, cy0 - 2, cx0 + lw + 4, cy0 + 19], fill=(24, 22, 18))
        draw.text((cx0, cy0), lab, font=lf, fill=(250, 246, 235))
    return ph

def draw_card(img, draw, card, x, y, w_, h_, hero):
    draw.rounded_rectangle([x, y, x + w_, y + h_], 6, fill=CARD_BG, outline=RULE, width=2)
    ph = 92 if hero else 90
    draw_panel(img, draw, card, x, y, w_, ph)
    tx = x + 8
    tw_max = w_ - 16
    ky = y + 5 + ph + 3
    kfont, ksize = fit_one(draw, card["place"], tw_max, 15 if hero else 13, 11, COND_SB)
    draw.text((tx, ky), card["place"], font=kfont, fill=ACCENT)
    hy = ky + (17 if hero else 15)
    sub_h = 17 if hero else 15
    n_sub = 1
    sy = y + h_ - 4 - n_sub * (sub_h + 1)
    hf, lines, hsize = fit_headline(draw, card["headline"], tw_max, 2, 30 if hero else 26, 19 if hero else 18, sy - hy, COND_B if hero else XCOND_B)
    assert len(lines) <= 2, f"headline wraps >2 lines: {card['headline']}"
    lh = int(hsize * 1.10)
    for ln in lines:
        draw.text((tx, hy), ln, font=hf, fill=INK)
        hy += lh
    assert hy <= sy + 2, f"headline/sub collision: {card['headline']} hy={hy} sy={sy}"
    subs = [card["sub"]]
    ssize_min = 99
    for i, stxt in enumerate(subs):
        sfont, ssize = fit_one(draw, stxt, tw_max, sub_h, 13, COND)
        ssize_min = min(ssize_min, ssize)
        slines = wrap(draw, stxt, sfont, tw_max)
        assert len(slines) == 1, f"sub wraps: {stxt}"
        draw.text((tx, sy + i * (sub_h + 1)), slines[0], font=sfont, fill=MUTED)
    return {"panel_h": ph, "panel_w": w_ - 12, "headline_px": hsize, "sub_px": ssize_min, "lines": len(lines)}

def tracked(draw, x, y, text, font, tracking, fill):
    cx = x
    for ch in text:
        draw.text((cx, y), ch, font=font, fill=fill)
        cx += tw(draw, ch, font) + tracking
    return cx - tracking

def main():
    with open(os.path.join(HERE, "data.json"), encoding="utf-8") as fh:
        data = json.load(fh)
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    metrics = {}
    presented = len(data["cards"]) + len(data["briefs"])
    metrics["presented"] = presented

    # masthead strap
    draw.rectangle([0, 0, W, 24], fill=BAND)
    draw.line([(0, 24), (W, 24)], fill=BAND_LINE, width=1)
    draw.text((MX, 2), data["strap_left"], font=F(SERIF_B, 17), fill=INK)
    rtxt = f"{presented} MONDAY STORIES VERIFIED - 7 REGIONS - WIRES AND OFFICIAL SOURCES ONLY"
    rf = F(COND_SB, 16)
    draw.text((W - MX - tw(draw, rtxt, rf), 4), rtxt, font=rf, fill=MUTED)

    # two-line date: MONDAY (tracked) over 23 NOVEMBER 2026 at 106px
    day_f = F(XCOND_B, 34)
    tracked(draw, MX + 2, 26, data["date_day"], day_f, 12, ACCENT)
    date_f = F(XCOND_B, 106)
    assert tw(draw, data["date_rest"], date_f) <= CW, "date line too wide"
    draw.text((MX, 54), data["date_rest"], font=date_f, fill=INK)
    metrics["date_px"] = 106
    date_bottom = 54 + 100
    draw.rectangle([MX, date_bottom + 3, W - MX, date_bottom + 7], fill=ACCENT)

    # slim stat band (figures match the cards exactly)
    sb_y = date_bottom + 10
    draw.rectangle([MX, sb_y, W - MX, sb_y + 28], fill=BAND, outline=BAND_LINE, width=1)
    n = len(data["stats"])
    colw = CW / n
    for i, (num, lab) in enumerate(data["stats"]):
        cx = MX + i * colw + 12
        draw.text((cx, sb_y + 1), num, font=F(COND_B, 19), fill=INK)
        draw.text((cx, sb_y + 19), lab, font=F(COND_SB, 10), fill=MUTED)

    # slim UTC timeline strip (timed Monday markers, all from the census)
    tl_y = sb_y + 32
    draw.line([(MX, tl_y + 7), (W - MX, tl_y + 7)], fill=BAND_LINE, width=2)
    tf = F(COND_SB, 14)
    tl = data["timeline"]
    seg = CW / len(tl)
    for i, (hh, lab) in enumerate(tl):
        cx = MX + i * seg + seg / 2
        draw.ellipse([cx - 3, tl_y + 4, cx + 3, tl_y + 10], fill=ACCENT)
        txt = f"{hh} {lab}"
        assert tw(draw, txt, tf) <= seg - 8, f"timeline label too wide: {txt}"
        draw.text((cx - tw(draw, txt, tf) / 2, tl_y + 11), txt, font=tf, fill=MUTED)
    metrics["furniture_bottom"] = tl_y + 27
    metrics["timeline_y"] = tl_y

    # ---- geometry (solved, then asserted) ----
    FOOTER_H = 50
    BRIEF_HEAD = 20
    BRIEF_PITCH = 18
    briefs = data["briefs"]
    per = (len(briefs) + 2) // 3
    briefs_block = BRIEF_HEAD + per * BRIEF_PITCH + 8
    cards_y = tl_y + 30
    footer_y = H - 6 - FOOTER_H
    briefs_y = footer_y - 2 - briefs_block
    cards_avail = briefs_y - 2 - cards_y
    hero_h = 196
    grid_h = (cards_avail - hero_h - 4 * 2) // 2
    assert grid_h >= 170, f"grid cards too short: {grid_h}"
    metrics["lead_h"], metrics["grid_h"] = hero_h, grid_h
    metrics["footer_y"], metrics["cards_y"] = footer_y, cards_y

    # cards: 3 heroes across the top, then 5 + 6 compact top-panel cards
    cards = data["cards"]
    results = []
    y = cards_y
    hw = (CW - 20) // 3
    for i in range(3):
        results.append(draw_card(img, draw, cards[i], MX + i * (hw + 10), y, hw, hero_h, True))
    y += hero_h + 4
    for r, cnt in enumerate((5, 6)):
        gw = (CW - (cnt - 1) * 8) // cnt
        for c in range(cnt):
            idx = 3 + (5 if r == 1 else 0) + c
            results.append(draw_card(img, draw, cards[idx], MX + c * (gw + 8), y, gw, grid_h, False))
        y += grid_h + 4
    metrics["cards"] = results
    metrics["cards_bottom"] = y - 4
    assert metrics["cards_bottom"] <= briefs_y - 2, "cards overrun briefs"

    # briefs heading + 3 columns
    draw.line([(MX, briefs_y + 2), (W - MX, briefs_y + 2)], fill=RULE, width=2)
    draw.text((MX, briefs_y + 4), "MORE OF MONDAY - THE BRIEFS", font=F(COND_B, 19), fill=INK)
    by = briefs_y + BRIEF_HEAD
    bf = F(XCOND, 22)
    GUT = 14
    colw_b = (CW - 2 * GUT) // 3
    for i, btxt in enumerate(briefs):
        col, row = divmod(i, per)
        bx = MX + col * (colw_b + GUT)
        byy = by + row * BRIEF_PITCH
        draw.text((bx, byy), f"{i + 1:02d}", font=F(COND_B, 22), fill=ACCENT)
        assert tw(draw, btxt, bf) <= colw_b - 38, f"brief too wide: {btxt}"
        draw.text((bx + 34, byy), btxt, font=bf, fill=INK)
    metrics["briefs_bottom"] = by + per * BRIEF_PITCH
    assert metrics["briefs_bottom"] + 8 <= footer_y - 2, "briefs overrun footer"

    # DATE CHECK footnote: 52px box, rail lines re-spaced with clear
    # padding above and below every glyph (the revision-1 clip is fixed
    # by geometry: line tops at dy+3 / dy+21 / dy+36, 12-15px type, so
    # the lowest glyph bottom sits ~7px above the box's bottom border).
    dy = footer_y
    draw.rectangle([MX, dy, W - MX, dy + FOOTER_H], fill=(238, 229, 205), outline=MUTED, width=1)
    RAIL = 132
    draw.text((MX + 10, dy + 3), "DATE CHECK", font=F(COND_SB, 15), fill=INK)
    draw.text((MX + 10, dy + 20), "NOT MONDAY", font=F(COND, 12), fill=MUTED)
    draw.text((MX + 10, dy + 34), "HELD BACK", font=F(COND, 12), fill=MUTED)
    draw.line([(MX + RAIL, dy + 4), (MX + RAIL, dy + FOOTER_H - 4)], fill=MUTED, width=1)
    items = data["date_check"]
    df = F(COND, 14)
    lf = F(COND_SB, 14)
    colw_d = (CW - RAIL - 12) // 3
    for i, (lab, txt) in enumerate(items):
        col, row = divmod(i, 2)
        ix = MX + RAIL + 12 + col * colw_d
        iy = dy + 5 + row * 22
        draw.text((ix, iy), lab, font=lf, fill=(140, 60, 40))
        tx2 = ix + tw(draw, lab, lf) + 5
        assert tx2 + tw(draw, "- " + txt, df) <= ix + colw_d - 4, f"date-check item too wide: {txt}"
        draw.text((tx2, iy), "- " + txt, font=df, fill=MUTED)
    metrics["datecheck_h"] = FOOTER_H

    out = os.path.join(HERE, "entry.png")
    img.save(out, format="PNG", optimize=True)
    img.resize((512, 512), Image.LANCZOS).save(os.path.join(HERE, "entry-512.png"), format="PNG", optimize=True)
    img.resize((300, 300), Image.LANCZOS).save(os.path.join(HERE, "entry-300.png"), format="PNG", optimize=True)
    with open(os.path.join(HERE, "metrics.json"), "w", encoding="utf-8") as fh:
        json.dump(metrics, fh, indent=1, sort_keys=True)
    print(json.dumps(metrics, indent=1))

if __name__ == "__main__":
    main()
