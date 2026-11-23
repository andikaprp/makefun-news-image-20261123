"""Monday 23 November 2026 - one-page broadsheet renderer.
Authored fresh for news-image-20261123. Reads data.json beside it,
draws a 1024x1024 cream broadsheet with PIL, writes entry.png beside it.
Deterministic: fixed palette, fixed layout, no clocks, no randomness.
"""
import json
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W = 1024
M = 26
IW = W - 2 * M

CREAM = (247, 241, 227)
PAPER = (252, 248, 238)
INK = (24, 24, 24)
MUTED = (92, 84, 70)
RED = (178, 32, 26)
NAVY = (26, 48, 84)
TEAL = (18, 102, 96)
GOLD = (196, 148, 32)
WHITE = (255, 255, 255)

COND = "/usr/share/fonts/truetype/noto/NotoSansDisplay-CondensedBold.ttf"
COND_R = "/usr/share/fonts/truetype/noto/NotoSansDisplay-Condensed.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def F(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, font, maxw):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=font) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def centered(draw, cx, y, text, font, fill):
    draw.text((cx - draw.textlength(text, font=font) / 2, y), text, font=font, fill=fill)


# ---------- flat art: each draws inside (x, y, w, h) ----------
def art_chart(d, x, y, w, h, c):
    d.rectangle([x, y, x + w, y + h], fill=(250, 226, 214))
    pts = [(x + 8, y + 8), (x + w * 0.3, y + h * 0.34), (x + w * 0.52, y + h * 0.3),
           (x + w * 0.74, y + h * 0.62), (x + w - 26, y + h - 8)]
    d.line(pts, fill=RED, width=4)
    d.polygon([(x + w - 26, y + h - 8), (x + w - 40, y + h - 16), (x + w - 14, y + h - 22)],
              fill=RED)
    for i in range(4):
        gx = x + 10 + i * (w - 20) // 3
        d.line([gx, y + 4, gx, y + h - 4], fill=(226, 196, 180), width=1)


def art_cricket(d, x, y, w, h, c):
    d.rectangle([x, y, x + w, y + h], fill=(203, 230, 198))
    d.rectangle([x + w * 0.42, y + 4, x + w * 0.58, y + h - 4], fill=(233, 214, 160))
    for sx in (0.46, 0.52):
        d.rectangle([x + w * sx, y + h * 0.3, x + w * sx + 3, y + h * 0.62], fill=(120, 84, 40))
    d.ellipse([x + w * 0.66, y + h * 0.52, x + w * 0.66 + 9, y + h * 0.52 + 9], fill=RED)
    d.arc([x + w * 0.6, y + 4, x + w * 0.94, y + h * 0.8], 200, 320, fill=TEAL, width=3)


def art_rescue(d, x, y, w, h, c):
    d.rectangle([x, y, x + w, y + h], fill=(216, 222, 232))
    d.polygon([(x + 6, y + h - 6), (x + w * 0.4, y + h * 0.4), (x + w * 0.72, y + h - 6)],
              fill=(140, 138, 132))
    d.polygon([(x + w * 0.3, y + h - 6), (x + w * 0.62, y + h * 0.52), (x + w - 8, y + h - 6)],
              fill=(112, 110, 104))
    d.line([x + w * 0.2, y + h - 10, x + w * 0.52, y + 8], fill=GOLD, width=4)
    d.ellipse([x + w * 0.5, y + 6, x + w * 0.5 + 10, y + 16], fill=GOLD)


def art_factory(d, x, y, w, h, c):
    d.rectangle([x, y, x + w, y + h], fill=(224, 232, 240))
    d.rectangle([x + 12, y + h * 0.42, x + w * 0.55, y + h - 6], fill=NAVY)
    d.rectangle([x + w * 0.6, y + h * 0.2, x + w * 0.68, y + h - 6], fill=(70, 90, 120))
    for i in range(3):
        d.rectangle([x + 20 + i * 22, y + h * 0.55, x + 32 + i * 22, y + h * 0.72],
                    fill=(250, 220, 120))
    d.line([x + w * 0.74, y + h - 8, x + w - 12, y + 10], fill=RED, width=4)
    d.polygon([(x + w - 12, y + 10), (x + w - 26, y + 12), (x + w - 16, y + 24)], fill=RED)


def art_shop(d, x, y, w, h, c):
    d.rectangle([x, y, x + w, y + h], fill=(250, 236, 200))
    d.polygon([(x + 14, y + h * 0.34), (x + w - 14, y + h * 0.34), (x + w - 26, y + h * 0.18),
               (x + 26, y + h * 0.18)], fill=TEAL)
    d.rectangle([x + 22, y + h * 0.34, x + w - 22, y + h - 6], fill=(255, 250, 238))
    d.rectangle([x + w * 0.44, y + h * 0.58, x + w * 0.56, y + h - 6], fill=NAVY)
    d.line([x + w * 0.66, y + h - 10, x + w - 16, y + 10], fill=(30, 140, 70), width=4)
    d.polygon([(x + w - 16, y + 10), (x + w - 30, y + 12), (x + w - 20, y + 24)],
              fill=(30, 140, 70))


def art_poll(d, x, y, w, h, c):
    d.rectangle([x, y, x + w, y + h], fill=(232, 228, 244))
    base = y + h - 8
    d.rectangle([x + 16, base - h * 0.62, x + 40, base], fill=NAVY)
    d.rectangle([x + 52, base - h * 0.82, x + 76, base], fill=RED)
    d.rectangle([x + 88, base - h * 0.4, x + 112, base], fill=(150, 148, 160))
    d.line([x + 10, base, x + w - 10, base], fill=INK, width=2)


def art_coin(d, x, y, w, h, c):
    d.rectangle([x, y, x + w, y + h], fill=(38, 40, 52))
    cx, cy, r = x + w * 0.24, y + h / 2, h * 0.34
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=GOLD, outline=(150, 108, 20), width=2)
    bf = F(SANS_B, int(r * 1.1))
    d.text((cx - d.textlength("B", font=bf) / 2, cy - r * 0.58), "B", font=bf, fill=(90, 62, 8))
    pts = [(x + w * 0.48, y + h * 0.6), (x + w * 0.66, y + h * 0.44), (x + w * 0.82, y + h * 0.5),
           (x + w - 10, y + h * 0.3)]
    d.line(pts, fill=(90, 220, 160), width=3)


def art_music(d, x, y, w, h, c):
    d.rectangle([x, y, x + w, y + h], fill=(244, 224, 236))
    for i, nx in enumerate((0.2, 0.42, 0.64)):
        bx = x + w * nx
        d.line([bx + 12, y + 8, bx + 12, y + h - 16], fill=NAVY, width=3)
        d.ellipse([bx, y + h - 22, bx + 13, y + h - 10], fill=NAVY)
        if i < 2:
            d.line([bx + 12, y + 8, bx + w * 0.22 + 12, y + 8], fill=NAVY, width=4)
    d.ellipse([x + w * 0.84, y + h * 0.24, x + w * 0.84 + 11, y + h * 0.24 + 11], fill=RED)


ART = {"chart_down": art_chart, "cricket": art_cricket, "rescue": art_rescue,
       "factory": art_factory, "shop": art_shop, "poll": art_poll,
       "coin": art_coin, "music": art_music}


def draw_card(d, card, x, y, w, h, lead):
    d.rectangle([x, y, x + w, y + h], fill=PAPER, outline=INK, width=2)
    art_h = 46 if lead else 38
    ART[card["art"]](d, x + 2, y + 2, w - 4, art_h, None)
    # banner label chip on the art (left) + source tag on the art (right)
    bf = F(COND, 17)
    label = card["banner"]
    lw = d.textlength(label, font=bf) + 14
    d.rectangle([x + 8, y + 8, x + 8 + lw, y + 30], fill=INK)
    d.text((x + 15, y + 10), label, font=bf, fill=WHITE)
    sf = F(SANS_B, 12)
    stag = card["source"]
    sw = d.textlength(stag, font=sf) + 12
    d.rectangle([x + w - 8 - sw, y + art_h - 16, x + w - 8, y + art_h + 2], fill=WHITE)
    d.text((x + w - 8 - sw + 6, y + art_h - 15), stag, font=sf, fill=INK)
    # number chip
    cx, cy, r = x + 20, y + art_h + 22, 15
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED)
    nf = F(SANS_B, 19)
    num = str(card["n"])
    d.text((cx - d.textlength(num, font=nf) / 2, cy - 12), num, font=nf, fill=WHITE)
    # headline, 36px floor, one line by design
    hf = F(COND, 36)
    hl = card["headline"]
    assert d.textlength(hl, font=hf) <= w - 52, "headline too wide: " + hl
    d.text((x + 44, y + art_h + 6), hl, font=hf, fill=INK)
    # body
    body_f = F(SANS, 15)
    lines = wrap(d, card["body"], body_f, w - 20)
    max_lines = 3 if lead else 2
    by = y + art_h + (48 if lead else 50)
    for ln in lines[:max_lines]:
        d.text((x + 10, by), ln, font=body_f, fill=(46, 42, 36))
        by += 18 if lead else 19


def main():
    with open(os.path.join(HERE, "data.json"), encoding="utf-8") as fh:
        data = json.load(fh)
    img = Image.new("RGB", (W, W), CREAM)
    d = ImageDraw.Draw(img)

    # masthead
    centered(d, W / 2, 12, data["strap"], F(COND, 22), MUTED)
    d.line([M, 42, W - M, 42], fill=INK, width=3)
    centered(d, W / 2, 48, data["date_line"], F(COND, 78), INK)
    d.line([M, 136, W - M, 136], fill=INK, width=3)

    # stat band
    d.rectangle([M, 144, W - M, 190], fill=INK)
    colw = IW / 4
    for i, s in enumerate(data["stats"]):
        cx = M + colw * i + colw / 2
        centered(d, cx, 147, s["value"], F(COND, 27), (255, 214, 90))
        centered(d, cx, 176, s["label"], F(SANS_B, 11), WHITE)

    # region strip
    centered(d, W / 2, 196, data["regions"], F(COND, 18), NAVY)

    # cards: lead row taller
    cards = data["cards"]
    gx, gy = 22, 8
    cw = (IW - gx) // 2
    rows = [(0, 152), (2, 132), (4, 132), (6, 132)]
    y = 222
    for start, rh in rows:
        for k in range(2):
            draw_card(d, cards[start + k], M + k * (cw + gx), y, cw, rh, start == 0)
        y += rh + gy

    # briefs band
    d.rectangle([M, y, W - M, y + 58], fill=(238, 230, 208), outline=MUTED, width=1)
    d.text((M + 10, y + 4), "BRIEFS", font=F(COND, 20), fill=RED)
    bf = F(SANS, 15)
    by = y + 5
    for i, b in enumerate(data["briefs"]):
        line = "%d. %s - %s (%s)" % (i + 1, b["place"], b["text"], b["source"])
        d.text((M + 92, by), line, font=bf, fill=INK)
        by += 19
    y += 62

    # date check box
    d.rectangle([M, y, W - M, y + 34], fill=RED)
    d.text((M + 10, y + 4), "DATE CHECK - NOT MONDAY (do not mistake these for today's news)",
           font=F(COND, 26), fill=WHITE)
    d.rectangle([M, y + 34, W - M, y + 130], outline=RED, width=2)
    df = F(COND, 24)
    for i, item in enumerate(data["date_check"]):
        ix = M + 12 + (i % 2) * (IW // 2)
        iy = y + 40 + (i // 2) * 30
        d.text((ix, iy), "x " + item, font=df, fill=INK)
    y += 134

    # not yet line
    centered(d, W / 2, y, data["not_yet"], F(COND, 20), RED)

    out = os.path.join(HERE, "entry.png")
    img.save(out, format="PNG", optimize=True)
    print(out)


if __name__ == "__main__":
    main()
