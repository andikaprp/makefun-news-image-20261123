#!/usr/bin/env python3
"""Slot-2 candidate renderer - news-image-20261123 (Monday 23 November 2026).

Fresh-authored composing lane. Cream broadsheet, giant date, 13 rich-art
headlined cards, numbered briefs band, DATE CHECK box. Deterministic:
all grain uses fixed numpy RandomState seeds; repeated runs are
byte-identical.
"""
import json
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W = H = 1024
M = 16
CW = W - 2 * M  # 992 content width

NOTO = "/usr/share/fonts/truetype/noto/"
F_DATE = NOTO + "NotoSans-ExtraCondensedBlack.ttf"
F_XCB = NOTO + "NotoSans-ExtraCondensedBlack.ttf"
F_CB = NOTO + "NotoSans-CondensedBold.ttf"
F_C = NOTO + "NotoSans-Condensed.ttf"
F_B = NOTO + "NotoSans-Bold.ttf"

CREAM = (252, 249, 240)
INK = (18, 16, 12)
RED = (178, 24, 20)
NAVY = (16, 28, 52)

_cache = {}


def font(path, size):
    key = (path, size)
    if key not in _cache:
        _cache[key] = ImageFont.truetype(path, size)
    return _cache[key]


def tw(draw, text, fnt):
    return draw.textlength(text, font=fnt)


def wrap(draw, text, fnt, maxw, maxlines):
    words = text.split()
    lines, cur = [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if tw(draw, t, fnt) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    assert len(lines) <= maxlines, f"wrap overflow ({len(lines)}>{maxlines}): {text}"
    return lines


def wrap_balanced(draw, text, fnt, maxw, maxlines=2):
    """Split text into <=maxlines lines minimising the widest line.
    Breaks allowed at spaces and right after , ; : characters."""
    frags = []
    for word in text.split():
        buf = ""
        for i, ch in enumerate(word):
            buf += ch
            if ch in ",;:" and i < len(word) - 1:
                # break point inside a word (e.g. a thousands comma in
                # "1,484"): the fragment carries NO trailing space, so
                # rejoining never prints "1, 484"
                frags.append(buf)
                buf = ""
        if buf:
            frags.append(buf + " ")
    frags = [f_ for f_ in frags]
    n = len(frags)
    best = None
    # try all single split points (2 lines), plus the 1-line case
    for s in range(0, n + 1):
        l1 = "".join(frags[:s]).strip()
        l2 = "".join(frags[s:]).strip()
        lines = [l for l in (l1, l2) if l]
        if not lines:
            continue
        if l1.rstrip().endswith(",") and l2[:1].isdigit():
            continue  # do not split a number at its thousands comma
        widest = max(tw(draw, l, fnt) for l in lines)
        if best is None or widest < best[0]:
            best = (widest, lines)
    assert best and best[0] <= maxw, f"balanced wrap too wide ({best[0]:.0f}>{maxw}): {text}"
    return best[1]


def draw_squeezed(img, x, y, text, fnt, maxw, fill):
    """Draw one line; if it exceeds maxw, squeeze horizontally only
    (glyph height unchanged), capped at 12%."""
    d0 = ImageDraw.Draw(img)
    wdt = tw(d0, text, fnt)
    if wdt <= maxw:
        d0.text((x, y), text, font=fnt, fill=fill)
        return
    factor = maxw / wdt
    assert factor >= 0.88, f"squeeze too deep ({factor:.2f}): {text}"
    layer = Image.new("RGBA", (int(wdt) + 4, fnt.size + 16), (0, 0, 0, 0))
    ImageDraw.Draw(layer).text((2, 2), text, font=fnt, fill=fill + (255,))
    layer = layer.resize((int(maxw), fnt.size + 16), Image.LANCZOS)
    img.paste(layer, (int(x), int(y - 2)), layer)


# ---------------------------------------------------------------- panels
def rich_panel(w, h, c_top, c_bot, seed):
    """Layered multi-frequency gradient + deterministic per-channel grain,
    soft glow and vignette. Returns an RGB PIL image (no strips drawn)."""
    rng = np.random.RandomState(seed)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float64)
    t = yy / max(h - 1, 1)
    base = np.zeros((h, w, 3))
    for ch in range(3):
        base[:, :, ch] = c_top[ch] * (1 - t) + c_bot[ch] * t
    # multi-frequency sinusoidal light field (different phase per channel)
    for ch in range(3):
        f1 = 2.0 + (seed % 5) + ch * 0.7
        f2 = 5.0 + (seed % 3) * 1.3 + ch * 0.9
        ph = rng.uniform(0, 6.28)
        wave = (np.sin(xx / w * f1 * 3.14 + ph) * 0.5
                + np.sin(yy / h * f2 * 3.14 + ph * 1.7) * 0.35
                + np.sin((xx + yy) / (w + h) * 9.0 + ph) * 0.25)
        base[:, :, ch] += wave * 16.0
    # glow: bright radial blob, seeded position
    gx, gy = rng.uniform(0.25, 0.75) * w, rng.uniform(0.2, 0.6) * h
    d2 = ((xx - gx) ** 2 + (yy - gy) ** 2) / (0.55 * w) ** 2
    base += np.exp(-d2)[:, :, None] * np.array([26.0, 22.0, 14.0])
    # vignette
    cx, cy = w / 2.0, h / 2.0
    vd = np.sqrt(((xx - cx) / (0.75 * w)) ** 2 + ((yy - cy) / (0.75 * h)) ** 2)
    base *= (1.0 - 0.20 * np.clip(vd - 0.55, 0, 1))[:, :, None]
    # deterministic per-channel grain, fixed seed
    for ch in range(3):
        base[:, :, ch] += rng.normal(0, 3.6, (h, w))
    return Image.fromarray(np.clip(base, 0, 255).astype(np.uint8), "RGB")


def card_fill(w, h, tint, seed):
    """Pastel gradient wash + fine grain for a card background."""
    rng = np.random.RandomState(seed + 5000)
    yy = np.linspace(0, 1, h)[:, None]
    top = np.array(tint, float)
    bot = top * 0.90 + np.array([6.0, 4.0, 0.0])
    arr = top[None, None, :] * (1 - yy[:, :, None]) + bot[None, None, :] * yy[:, :, None]
    arr = np.repeat(arr, w, axis=1)
    for ch in range(3):
        arr[:, :, ch] += rng.normal(0, 1.4, (h, w))
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")


# ---------------------------------------------------------------- scenes
def scene(draw, key, x, y, w, h):
    """Simple drawn scene in the panel's middle zone only."""
    cx, cy = x + w / 2, y + h / 2
    L = (240, 236, 220)   # light line
    D = (12, 12, 14)      # dark shape
    A = (255, 196, 64)    # accent
    R = (255, 92, 72)
    if key == "nvidia":  # chip + rising arrow
        s = min(w, h) * 0.30
        draw.rectangle([cx - s, cy - s, cx + s, cy + s], outline=L, width=3)
        for i in range(-1, 2):
            draw.line([cx + i * s * 0.5, cy - s, cx + i * s * 0.5, cy - s - 7], fill=L, width=2)
            draw.line([cx + i * s * 0.5, cy + s, cx + i * s * 0.5, cy + s + 7], fill=L, width=2)
        draw.line([x + 6, y + h - 8, x + w - 14, y + 8], fill=A, width=3)
        draw.polygon([(x + w - 14, y + 8), (x + w - 24, y + 10), (x + w - 16, y + 18)], fill=A)
    elif key in ("kospi", "sensex", "taiex"):  # chart line
        col = R if key != "taiex" else (96, 255, 150)
        pts = []
        n = 7
        for i in range(n):
            px = x + 6 + (w - 12) * i / (n - 1)
            frac = i / (n - 1)
            py = y + h * (0.25 + 0.55 * frac) if key != "taiex" else y + h * (0.80 - 0.55 * frac)
            if key == "taiex":
                py = y + h * (0.80 - 0.55 * frac)
            pts.append((px, py + (4 if i % 2 else -3)))
        draw.line(pts, fill=col, width=3)
        for i in range(0, int(w), 14):
            draw.line([x + i, y + h - 4, x + i, y + h - 1], fill=L, width=1)
    elif key == "dymer":  # building + rescue beam
        draw.rectangle([x + 8, y + 4, x + 34, y + h - 4], outline=L, width=2)
        for r in range(3):
            for c in range(2):
                draw.rectangle([x + 13 + c * 10, y + 9 + r * 10, x + 19 + c * 10, y + 15 + r * 10], fill=A)
        draw.polygon([(x + w - 8, y + h - 6), (x + 30, y + 12), (x + 44, y + 10)], fill=(255, 240, 180))
        draw.ellipse([x + w - 16, y + h - 12, x + w - 4, y + h - 2], fill=A)
    elif key == "cikande":  # flames
        for i, fx in enumerate(np.linspace(x + 10, x + w - 10, 4)):
            fh = h * (0.55 + 0.25 * math.sin(i * 1.7))
            draw.polygon([(fx - 7, y + h - 4), (fx, y + h - fh), (fx + 7, y + h - 4)], fill=R if i % 2 else A)
        draw.rectangle([x + 4, y + h - 5, x + w - 4, y + h - 2], fill=D)
    elif key == "wellington":  # stadium + ball
        draw.arc([x + 6, y + 6, x + w - 6, y + h + 16], 180, 360, fill=L, width=3)
        for i in range(5):
            lx = x + 12 + i * (w - 24) / 4
            draw.line([lx, y + 12, lx, y + 5], fill=A, width=2)
            draw.ellipse([lx - 2, y + 2, lx + 2, y + 6], fill=A)
        draw.ellipse([cx - 4, cy + 2, cx + 4, cy + 10], fill=(250, 250, 250))
    elif key == "benghazi":  # ship + drone arcs
        draw.polygon([(x + 8, y + h - 12), (x + w - 14, y + h - 12), (x + w - 24, y + h - 4), (x + 16, y + h - 4)], fill=D)
        draw.rectangle([x + 24, y + h - 22, x + 44, y + h - 12], fill=D)
        draw.line([x + 34, y + h - 22, x + 34, y + h - 30], fill=L, width=2)
        for i in range(3):
            draw.arc([x + w - 34 + i * 3, y + 4 + i * 5, x + w - 6 + i * 3, y + 18 + i * 5], 200, 320, fill=A, width=2)
        draw.line([x + 4, y + h - 2, x + w - 4, y + h - 2], fill=(120, 190, 255), width=2)
    elif key == "nepal":  # peaks + sun
        draw.polygon([(x + 4, y + h - 4), (x + w * 0.38, y + 8), (x + w * 0.62, y + h - 4)], outline=L, width=3)
        draw.polygon([(x + w * 0.42, y + h - 4), (x + w * 0.72, y + 16), (x + w - 4, y + h - 4)], outline=L, width=3)
        draw.ellipse([x + w - 22, y + 4, x + w - 10, y + 16], fill=A)
    elif key == "pmi":  # gauge
        draw.arc([x + 8, y + 4, x + w - 8, y + h + 10], 180, 360, fill=L, width=3)
        ang = math.radians(200)
        draw.line([cx, cy + 8, cx + 16 * math.cos(ang), cy + 8 + 16 * math.sin(ang)], fill=R, width=3)
        draw.ellipse([cx - 3, cy + 5, cx + 3, cy + 11], fill=A)
        for i in range(5):
            a = math.radians(180 + i * 45)
            draw.line([cx + 20 * math.cos(a), cy + 8 + 20 * math.sin(a), cx + 24 * math.cos(a), cy + 8 + 24 * math.sin(a)], fill=L, width=2)
    elif key == "cop":  # globe + thermometer
        r = min(w, h) * 0.32
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(140, 220, 255), width=3)
        draw.arc([cx - r, cy - r, cx + r, cy + r], 20, 160, fill=(140, 220, 255), width=2)
        draw.line([cx - r, cy, cx + r, cy], fill=(140, 220, 255), width=2)
        draw.rectangle([x + w - 14, y + 8, x + w - 8, y + h - 14], outline=R, width=2)
        draw.rectangle([x + w - 13, y + h - 22, x + w - 9, y + h - 15], fill=R)
    elif key == "burnham":  # parliament columns
        for i in range(4):
            bx = x + 8 + i * (w - 16) / 3
            draw.rectangle([bx - 3, y + 12, bx + 3, y + h - 10], fill=L)
        draw.polygon([(x + 4, y + 12), (cx, y + 3), (x + w - 4, y + 12)], fill=A)
        draw.rectangle([x + 4, y + h - 9, x + w - 4, y + h - 5], fill=L)
    elif key == "drones":  # drone silhouettes
        for (dx, dy, s) in [(0.3, 0.35, 9), (0.62, 0.55, 12), (0.45, 0.75, 7)]:
            px, py = x + w * dx, y + h * dy
            draw.ellipse([px - 3, py - 3, px + 3, py + 3], fill=D)
            for (ox, oy) in [(-s, -s), (s, -s), (-s, s), (s, s)]:
                draw.line([px, py, px + ox, py + oy], fill=D, width=2)
                draw.ellipse([px + ox - 2, py + oy - 2, px + ox + 2, py + oy + 2], outline=L, width=1)
    else:  # generic bars
        for i in range(4):
            bh = h * (0.25 + 0.15 * i)
            draw.rectangle([x + 8 + i * 14, y + h - 6 - bh, x + 18 + i * 14, y + h - 6], fill=A if i % 2 else L)


PALETTES = {
    "nvidia": ((24, 60, 30), (10, 22, 40)),
    "kospi": ((52, 26, 60), (16, 14, 44)),
    "dymer": ((58, 44, 30), (24, 20, 34)),
    "cikande": ((70, 30, 16), (30, 12, 20)),
    "wellington": ((16, 52, 66), (8, 24, 44)),
    "benghazi": ((14, 44, 74), (8, 18, 40)),
    "nepal": ((30, 52, 84), (16, 26, 52)),
    "pmi": ((54, 48, 22), (26, 24, 16)),
    "cop": ((18, 56, 62), (10, 30, 44)),
    "burnham": ((44, 36, 64), (20, 16, 40)),
    "sensex": ((62, 30, 34), (26, 14, 30)),
    "drones": ((40, 40, 48), (16, 16, 26)),
    "taiex": ((18, 58, 44), (10, 28, 34)),
}
TINTS = [(238, 233, 214), (232, 236, 218), (236, 230, 222), (230, 234, 226),
         (238, 236, 208), (226, 234, 232), (234, 232, 216), (238, 230, 210),
         (228, 236, 224), (234, 230, 226), (236, 226, 216), (230, 232, 230),
         (226, 236, 220)]


def draw_panel(img, card, x, y, w, h, seed):
    top, bot = PALETTES[card["key"]]
    panel = rich_panel(w, h, top, bot, seed)
    img.paste(panel, (x, y))
    d = ImageDraw.Draw(img)
    strip = 14
    d.rectangle([x, y, x + w, y + strip], fill=(10, 10, 12))
    d.rectangle([x, y + h - strip, x + w, y + h], fill=(10, 10, 12))
    # Strip text fit-to-width: shrink the tag font (13px down to 11px)
    # until it fits inside the strip's inner width (panel width minus
    # 4px padding each side); if it still overflows, squeeze it
    # horizontally into the available width. No tag may spill outside
    # its strip (ESPNCRICINFO / BUSINESSLINE / UA AIR FORCE did).
    def strip_text(text, tx, ty, align, fill):
        avail = w - 8
        size = 13
        while size > 11:
            f_try = font(F_CB, size)
            if tw(d, text, f_try) <= avail:
                break
            size -= 1
        f_use = font(F_CB, size)
        wdt = tw(d, text, f_use)
        y_off = ty + (13 - size)
        if wdt <= avail:
            sx = tx if align == "left" else tx + avail - wdt
            d.text((sx, y_off), text, font=f_use, fill=fill)
        else:
            # squeezed to exactly the available width, starting at the
            # strip's left padding edge
            draw_squeezed(img, tx, y_off, text, f_use, avail, fill)

    strip_text(card["place"], x + 4, y + 1, "left", (255, 244, 200))
    d = ImageDraw.Draw(img)
    strip_text(card["source"], x + 4, y + h - strip + 1, "right", (210, 214, 220))
    d = ImageDraw.Draw(img)
    scene(d, card["key"], x, y + strip, w, h - 2 * strip)


def main():
    data = json.load(open(os.path.join(HERE, "data.json")))
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)

    # ---- masthead
    fm = font(F_B, 24)
    d.text((M, 10), data["masthead_left"], font=fm, fill=INK)
    r = data["masthead_right"]
    d.text((W - M - tw(d, r, fm), 10), r, font=fm, fill=INK)
    d.rectangle([M, 40, W - M, 43], fill=INK)

    # ---- giant date: 106px nominal, squeezed horizontally only to fit
    # the measure (glyph ink height unchanged by an x-only squeeze)
    date_size = 106
    fd = font(F_DATE, date_size)
    txt = data["date_line"]
    wdt = tw(d, txt, fd)
    layer = Image.new("RGBA", (int(wdt) + 8, 136), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    ld.text((4, 9), txt, font=fd, fill=INK + (255,))
    if wdt > CW:
        layer = layer.resize((CW, 136), Image.LANCZOS)
    img.paste(layer, (M, 2), layer)
    d = ImageDraw.Draw(img)
    DATE_NOMINAL = date_size

    # ---- strap
    fs = font(F_CB, 24)
    st = data["strap"]
    d.text(((W - tw(d, st, fs)) / 2, 148), st, font=fs, fill=(90, 30, 20))

    # ---- stat band
    d.rectangle([M, 176, W - M, 214], fill=NAVY)
    fst = font(F_CB, 24)
    for i, s in enumerate(data["stats"]):
        assert tw(d, s, fst) <= CW / 4 - 10, f"stat too wide: {s}"
        cx0 = M + i * CW / 4
        d.text((cx0 + (CW / 4 - tw(d, s, fst)) / 2, 183), s, font=fst, fill=(255, 246, 214))
        if i:
            d.line([cx0, 182, cx0, 208], fill=(120, 140, 180), width=2)

    # ---- region strip
    d.rectangle([M, 218, W - M, 244], fill=(238, 230, 204))
    fr = font(F_C, 24)
    rg = data["region_strip"]
    assert tw(d, rg, fr) <= CW, "region strip too wide"
    d.text(((W - tw(d, rg, fr)) / 2, 219), rg, font=fr, fill=INK)

    # ---- cards
    cards = data["cards"]
    y = 252
    # lead row: 2 cards
    lead_h, gap = 106, 5
    lw = (CW - 8) / 2
    for i in range(2):
        cx0 = M + i * (lw + 8)
        img.paste(card_fill(int(lw), lead_h, TINTS[i], 100 + i), (int(cx0), y))
        pw = 120
        draw_panel(img, cards[i], int(cx0), y, pw, lead_h, 200 + i * 7)
        fh = font(F_XCB, 40)
        lines = wrap_balanced(d, cards[i]["headline"], fh, (lw - pw - 14) * 1.13, 2)
        ty = y + 4
        for ln in lines:
            draw_squeezed(img, cx0 + pw + 8, ty, ln, fh, lw - pw - 14, INK)
            ty += 38
        d = ImageDraw.Draw(img)
        ff = font(F_C, 24)
        flines = wrap(d, cards[i]["fact"], ff, lw - pw - 14, 1)
        for ln in flines:
            d.text((cx0 + pw + 8, ty + 1), ln, font=ff, fill=(60, 40, 20))
            ty += 25
        assert ty <= y + lead_h + 2, f"lead overflow card {i}"
    y += lead_h + gap
    # rows of 3,3,3,2
    row_h = 66
    cw3 = (CW - 12) / 3
    idx = 2
    fh36 = font(F_XCB, 36)
    for row in range(4):
        n_in = 3 if row < 3 else 2
        for c in range(n_in):
            card = cards[idx]
            cx0 = M + c * (cw3 + 6)
            img.paste(card_fill(int(cw3), row_h, TINTS[idx], 100 + idx), (int(cx0), y))
            pw = 76
            draw_panel(img, card, int(cx0), y, pw, row_h, 200 + idx * 7)
            lines = wrap_balanced(d, card["headline"], fh36, (cw3 - pw - 12) * 1.13, 2)
            ty = y + (row_h - len(lines) * 33) / 2 - 1
            for ln in lines:
                draw_squeezed(img, cx0 + pw + 7, ty, ln, fh36, cw3 - pw - 12, INK)
                ty += 33
            d = ImageDraw.Draw(img)
            idx += 1
        y += row_h + gap
    cards_bottom = y - gap

    # ---- briefs band
    y = cards_bottom + 8
    fb_h = font(F_B, 24)
    d.text((M, y), data["briefs_heading"], font=fb_h, fill=INK)
    d.rectangle([M, y + 28, W - M, y + 30], fill=INK)
    y += 36
    fb = font(F_C, 24)
    colw = (CW - 16) / 2
    briefs = data["briefs"]
    per = (len(briefs) + 1) // 2
    for col in range(2):
        cx0 = M + col * (colw + 16)
        for j in range(per):
            k = col * per + j
            if k >= len(briefs):
                break
            line = f"{k + 1}. {briefs[k]}"
            assert tw(d, line, fb) <= colw, f"brief too wide: {line}"
            d.text((cx0, y + j * 24), line, font=fb, fill=INK)
    y += per * 24 + 6

    # ---- DATE CHECK box
    d.rectangle([M, y, W - M, H - 8], outline=RED, width=3)
    fdc = font(F_B, 24)
    d.rectangle([M, y, W - M, y + 28], fill=RED)
    hd = data["date_check_heading"]
    d.text(((W - tw(d, hd, fdc)) / 2, y + 2), hd, font=fdc, fill=(255, 255, 255))
    y += 30
    fitem = font(F_C, 24)
    fday = font(F_CB, 24)
    colw3 = (CW - 24) / 3
    items = data["date_check"]
    for r_ in range(2):
        for c in range(3):
            it = items[r_ * 3 + c]
            cx0 = M + 8 + c * (colw3 + 4)
            day, rest = it.split(" - ", 1)
            dayw = tw(d, day + " - ", fday)
            iy = y + r_ * 44
            d.text((cx0, iy), day + " -", font=fday, fill=RED)
            # greedy wrap with per-line widths: line 1 sits beside the
            # red day label, line 2 uses the full column width
            widths = [colw3 - 6 - dayw, colw3 - 6]
            lines, cur, li = [], "", 0
            for w_ in rest.split():
                t = (cur + " " + w_).strip()
                if tw(d, t, fitem) <= widths[min(li, 1)] or not cur:
                    cur = t
                else:
                    lines.append(cur)
                    li += 1
                    cur = w_
            if cur:
                lines.append(cur)
            assert len(lines) <= 2, f"date-check overflow: {it}"
            d.text((cx0 + dayw, iy), lines[0], font=fitem, fill=INK)
            if len(lines) > 1:
                d.text((cx0, iy + 22), lines[1], font=fitem, fill=INK)
    out = os.path.join(HERE, "entry.png")
    img.save(out, optimize=True)
    print("date nominal:", DATE_NOMINAL)
    print("saved", out)


if __name__ == "__main__":
    main()
