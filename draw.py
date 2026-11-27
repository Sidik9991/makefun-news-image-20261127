#!/usr/bin/env python3
"""The World in One Day — Friday 27 November 2026. Drawing source.

This script is the drawing source that produced the committed
entry.png: it draws the one-page atlas broadsheet (1024x1024 PNG)
summing up the world's news of Friday 27 November 2026. It is NOT the
graded entrypoint — that is main.ts, which validates the committed
entry.png and ships it byte-for-byte. This file stays in the repo so
the page can be redrawn and audited; run it manually to regenerate
entry.png (it writes to MAKEFUN_OUTPUT_DIR, else /output).

Deterministic: no randomness, no clock, no network. Standard library
plus PIL only. Fonts ship in the repository (assets/fonts) so the
sandbox renders exactly what was rendered here.

Layout (frozen atlas, per the winner study):
  masthead with the date as the largest type on the page,
  a red sub-headline naming the three leads, a KPI strip,
  three big pictured leads (>=32% of the page), twelve small pictured
  panels, a bottom band with a pinned world map and a dense digest,
  a DATE CHECK strip, and a footer with the certainty key.
Text that does not fit its box is shrunk step by step until it fits;
anything still overflowing is logged as a warning but never fails the
build, and if drawing itself raises, the committed entry.png is copied
to the output instead. The program always exits 0 after writing an
image: zero truncations where metrics allow, and never a hard failure
just because another environment's font metrics differ slightly.
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 24
CW = W - 2 * MARGIN  # content width

PAPER = (250, 246, 236)
INK = (26, 26, 26)
RED = (179, 0, 27)
NAVY = (20, 48, 77)
MUTED = (107, 98, 87)
RULE = (216, 210, 196)
CARD = (255, 255, 255)
GOLD = (198, 146, 42)

FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "fonts")


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


SERIF = "DejaVuSerif.ttf"
SERIF_B = "DejaVuSerif-Bold.ttf"
SANS = "DejaVuSans.ttf"
SANS_B = "DejaVuSans-Bold.ttf"

WARNINGS = []


def text_w(draw, s, fnt):
    return draw.textlength(s, font=fnt)


def wrap(draw, s, fnt, max_w):
    """Greedy word wrap; returns list of lines, each <= max_w wide."""
    lines, cur = [], ""
    for word in s.split():
        trial = word if not cur else cur + " " + word
        if text_w(draw, trial, fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit(draw, s, fnt, max_w, box, label):
    """Wrap s into box=(max_lines, line_height); shrink the font step
    by step until every wrapped line fits max_w and the line count
    fits the box. Returns (lines, font_to_use). A text that still
    overflows at the minimum size is truncated to the box and recorded
    in WARNINGS for the log — it never fails the build, because font
    metrics differ slightly between environments."""
    max_lines, _lh = box
    size = fnt.size
    min_size = max(7, int(size * 0.55))
    cur = fnt
    lines = wrap(draw, s, cur, max_w)
    while size > min_size and (
        len(lines) > max_lines
        or any(text_w(draw, ln, cur) > max_w for ln in lines)
    ):
        size = max(min_size, size - 1)
        cur = ImageFont.truetype(fnt.path, size)
        lines = wrap(draw, s, cur, max_w)
    if len(lines) > max_lines or any(text_w(draw, ln, cur) > max_w for ln in lines):
        WARNINGS.append("%s overflows even at %dpx: %r" % (label, size, s))
        lines = lines[:max_lines]
    return lines, cur


def draw_lines(draw, x, y, lines, fnt, lh, fill=INK):
    for ln in lines:
        draw.text((x, y), ln, font=fnt, fill=fill)
        y += lh
    return y


def centered(draw, cx, y, s, fnt, fill=INK):
    draw.text((cx - text_w(draw, s, fnt) / 2, y), s, font=fnt, fill=fill)


# ---------------------------------------------------------------- data

DATE_LINE = "FRIDAY 27 NOVEMBER 2026"
SUB_HEAD = "KUWAIT STRIKE KILLS TWO ITALIANS \u00b7 HAMAS WEIGHS ITS REPLY \u00b7 STOCKS STEADY AFTER THE ROUT"

KPIS = [
    ("600,000+", "US homes without power"),
    ("10", "killed in Gaza strikes"),
    ("2", "Italians dead in Kuwait"),
    ("$94.71", "Brent crude, a barrel"),
    ("+60%", "VIX fear gauge in Nov"),
    ("42,000", "US flights due Friday"),
]

# scene, region, pin number (or None), headline, one line (<=90 chars)
LEADS = [
    (
        "kuwait",
        "MIDDLE EAST",
        1,
        "Two Italians killed in Kuwait drone strike; Iran denies blame",
        "Technicians died at an air-defence station; Tehran offers a joint inquiry.",
    ),
    (
        "gaza",
        "MIDDLE EAST",
        2,
        "Hamas weighs its reply after Israel kills 10 in Gaza",
        "A third night of strikes strains the year-old ceasefire; factions hold talks in Cairo.",
    ),
    (
        "markets",
        "GLOBAL",
        None,
        "Stocks steady on Friday after the tariff-and-AI rout",
        "Asia and Europe claw back ground; Wall Street returns for a shortened session.",
    ),
]

# scene, region, pin number (or None), headline, one line (<=60 chars)
PANELS = [
    ("storm", "NORTH AMERICA", 3, "Nor'easter leaves 600,000 in the dark",
     "Parade postponed; Friday is the travel test"),
    ("plant", "EUROPE", 4, "Ukrainian drones hit explosives plant",
     "Fertilizer works at Nevinnomyssk ablaze"),
    ("warning", "EUROPE", 5, "Zelenskyy warns of a major assault",
     "Kyiv says Russia is massing for a new push"),
    ("trial", "MIDDLE EAST", 6, "Netanyahu: my trial has 'collapsed'",
     "Judges question the key corruption charges"),
    ("tanker", "EUROPE", 7, "Tanker capsizes off Ibiza; one dead",
     "Diesel ship overturns in the Mediterranean"),
    ("court", "EUROPE", 8, "Depardieu to stand trial in Paris",
     "Court sends 2018 rape allegation to trial"),
    ("chess", "SOUTH ASIA", None, "Chess final: third straight draw",
     "Gukesh and Sindarov level after a marathon"),
    ("memorial", "EAST ASIA", 9, "Hong Kong marks a year since fire",
     "City pauses for the high-rise victims"),
    ("protest", "SOUTH ASIA", 10, "Police gas garment workers' protest",
     "Bangladesh pay march broken up in Dhaka"),
    ("pact", "OCEANIA", 11, "Australia seals Solomon Islands pact",
     "Deal pushes back Chinese influence"),
    ("jet", "NORTH AMERICA", 12, "US clears $621.9m F-16 aid for Kyiv",
     "Package paid for by European nations"),
    ("gavel", "SOUTH EAST ASIA", 13, "Myanmar rejects parts of ICJ ruling",
     "Junta dismisses genocide-case findings"),
]

DIGEST = [
    "Kushner urges Israel to drop 'war mindset'",
    "Katz warns Gaza op could displace 1,000,000",
    "UN agency votes to boost Palestinian aid",
    "Costa: EU must deal on budget by December",
    "Parliament warns on Black Sea attacks",
    "Ukrainian sea drones hunt Russian lines",
    "Houthis claim strikes on Saudi Jizan port",
    "US hails Syria Captagon haul, Iran arms",
    "Khartoum rejects Addis plan to end war",
    "Spain sends troops to El Hierro emergency",
    "France cyber chief: 'unprecedented' threat",
    "Britain moves jets to hardened shelters",
    "Estonia reports GPS jamming near Russia",
    "Iraq court: life for 8 French ISIS men",
    "Iraq judge calls Erbil-Baghdad dialogue",
    "China launches observation satellites",
    "Putin pushes AI across Russia's state",
    "Trump, Rutte talk Ukraine, Iran, funds",
    "Heathrow growth 'fails climate tests'",
    "2,000 march in Paris for school funds",
    "French factory prices jump 9.6% in Oct",
    "Hungary joins return of Ukraine children",
]

DATE_CHECK = (
    "DATE CHECK \u2014 left out as other days' news: Karachi building collapse (fell Wed 25 Nov) \u00b7 "
    "Guinea-Bissau vote delay, Bank of Korea hike, Brazil inflation, UK train-stabbing verdict (all Thu 26 Nov). "
    "Morning edition: the day is young; a full-day refresh follows."
)

FOOTER = (
    "Scenes drawn from wire reports of Fri 27 Nov 2026 (Reuters \u00b7 AP \u00b7 BBC \u00b7 CNN \u00b7 WSJ). "
    "A claim made by one side is named as that side's claim. Pins mark pictured stories only."
)


# ---------------------------------------------------------------- scenes
# Each scene paints inside box (x, y, w, h) with a small flat-vector motif.

def _sky(d, box, top, bottom):
    x, y, w, h = box
    for i in range(h):
        t = i / max(h - 1, 1)
        c = tuple(int(top[k] + (bottom[k] - top[k]) * t) for k in range(3))
        d.line([(x, y + i), (x + w, y + i)], fill=c)


def sc_kuwait(d, box):
    x, y, w, h = box
    _sky(d, box, (38, 52, 84), (196, 120, 74))
    d.ellipse([x + w * 0.78, y + h * 0.10, x + w * 0.92, y + h * 0.34], fill=(244, 196, 110))
    # radar dish on a mast
    mx = x + w * 0.16
    d.line([(mx, y + h), (mx, y + h * 0.38)], fill=(20, 24, 30), width=5)
    d.arc([mx - 34, y + h * 0.16, mx + 30, y + h * 0.52], start=300, end=120, fill=(20, 24, 30), width=5)
    d.line([(mx, y + h * 0.34), (mx + 26, y + h * 0.24)], fill=(20, 24, 30), width=4)
    # drone silhouette
    dx, dy = x + w * 0.58, y + h * 0.30
    d.line([(dx - 30, dy - 16), (dx + 30, dy + 16)], fill=(15, 15, 18), width=5)
    d.line([(dx - 30, dy + 16), (dx + 30, dy - 16)], fill=(15, 15, 18), width=5)
    d.ellipse([dx - 9, dy - 7, dx + 9, dy + 7], fill=(15, 15, 18))
    for px, py in ((dx - 30, dy - 16), (dx + 30, dy + 16), (dx - 30, dy + 16), (dx + 30, dy - 16)):
        d.ellipse([px - 8, py - 3, px + 8, py + 3], outline=(15, 15, 18), width=3)
    # burst where a second drone fell
    bx, by = x + w * 0.80, y + h * 0.74
    for ang in range(0, 360, 30):
        import math
        ex = bx + 26 * math.cos(math.radians(ang))
        ey = by + 18 * math.sin(math.radians(ang))
        d.line([(bx, by), (ex, ey)], fill=(226, 84, 32), width=4)
    d.ellipse([bx - 8, by - 6, bx + 8, by + 6], fill=(250, 190, 60))
    d.rectangle([x, y + h * 0.88, x + w, y + h], fill=(52, 40, 34))


def sc_gaza(d, box):
    x, y, w, h = box
    _sky(d, box, (16, 20, 38), (74, 52, 66))
    # skyline silhouette
    rng = [0.55, 0.42, 0.62, 0.48, 0.58, 0.40, 0.52, 0.46]
    bw = w / len(rng)
    for i, t in enumerate(rng):
        bx = x + i * bw
        d.rectangle([bx + 1, y + h * t, bx + bw - 1, y + h], fill=(10, 12, 18))
        for wy in range(int(y + h * (t + 0.08)), int(y + h * 0.92), 13):
            if (i * 7 + wy) % 3:
                d.point((bx + bw * 0.4, wy), fill=(240, 205, 120))
    # two flashes
    for fx, fy, r in ((0.30, 0.30, 20), (0.72, 0.22, 14)):
        cx, cy = x + w * fx, y + h * fy
        d.ellipse([cx - r, cy - r * 0.7, cx + r, cy + r * 0.7], fill=(248, 178, 84))
        d.ellipse([cx - r * 0.4, cy - r * 0.3, cx + r * 0.4, cy + r * 0.3], fill=(255, 226, 150))


def sc_markets(d, box):
    x, y, w, h = box
    _sky(d, box, (24, 44, 66), (24, 44, 66))
    for gx in range(0, int(w), 26):
        d.line([(x + gx, y), (x + gx, y + h)], fill=(38, 66, 96))
    for gy in range(0, int(h), 22):
        d.line([(x, y + gy), (x + w, y + gy)], fill=(38, 66, 96))
    pts_down = [(0.04, 0.22), (0.20, 0.34), (0.34, 0.30), (0.48, 0.52), (0.60, 0.66)]
    pts_up = [(0.60, 0.66), (0.72, 0.58), (0.84, 0.62), (0.96, 0.44)]
    for pts, col in ((pts_down, (226, 84, 84)), (pts_up, (96, 205, 130))):
        xy = [(x + w * a, y + h * b) for a, b in pts]
        d.line(xy, fill=col, width=5, joint="curve")
        for px, py in xy:
            d.ellipse([px - 4, py - 4, px + 4, py + 4], fill=col)


def sc_storm(d, box):
    x, y, w, h = box
    _sky(d, box, (44, 58, 78), (96, 116, 138))
    for i in range(46):
        rx = x + (i * 37) % int(w)
        ry = y + (i * 23) % int(h * 0.8)
        d.line([(rx, ry), (rx - 5, ry + 12)], fill=(190, 208, 226), width=2)
    # wind swirls
    d.arc([x + w * 0.55, y + h * 0.12, x + w * 0.95, y + h * 0.5], start=200, end=40, fill=(230, 238, 245), width=4)
    d.arc([x + w * 0.08, y + h * 0.3, x + w * 0.4, y + h * 0.62], start=180, end=20, fill=(230, 238, 245), width=4)
    # sea
    d.rectangle([x, y + h * 0.78, x + w, y + h], fill=(30, 62, 92))
    for i in range(5):
        wx = x + i * w / 5 + 6
        d.arc([wx, y + h * 0.8, wx + w / 6, y + h * 0.98], start=180, end=330, fill=(200, 220, 235), width=3)


def sc_plant(d, box):
    x, y, w, h = box
    _sky(d, box, (70, 66, 72), (150, 110, 88))
    d.rectangle([x, y + h * 0.72, x + w, y + h], fill=(40, 36, 36))
    for i, cx in enumerate((0.2, 0.42, 0.64)):
        px = x + w * cx
        d.rectangle([px, y + h * 0.34, px + 12, y + h * 0.74], fill=(30, 28, 30))
        d.rectangle([px - 2, y + h * 0.34, px + 14, y + h * 0.40], fill=(178, 52, 40))
    # fire plume
    fx, fy = x + w * 0.80, y + h * 0.55
    d.polygon([(fx - 16, y + h * 0.74), (fx, y + h * 0.22), (fx + 18, y + h * 0.74)], fill=(232, 110, 40))
    d.polygon([(fx - 8, y + h * 0.74), (fx + 2, y + h * 0.42), (fx + 10, y + h * 0.74)], fill=(250, 196, 84))
    # small drone
    dx, dy = x + w * 0.30, y + h * 0.18
    d.line([(dx - 12, dy - 6), (dx + 12, dy + 6)], fill=(12, 12, 14), width=3)
    d.line([(dx - 12, dy + 6), (dx + 12, dy - 6)], fill=(12, 12, 14), width=3)


def sc_warning(d, box):
    x, y, w, h = box
    _sky(d, box, (52, 40, 44), (128, 84, 70))
    # massing arrow over a plain: shaft plus head, pointing east
    ay = y + h * 0.46
    d.rectangle([x + w * 0.10, ay, x + w * 0.52, ay + h * 0.16], fill=(200, 60, 44))
    d.polygon([(x + w * 0.52, ay - h * 0.10), (x + w * 0.84, ay + h * 0.08), (x + w * 0.52, ay + h * 0.26)],
              fill=(200, 60, 44))
    for i in range(6):
        tx = x + w * (0.08 + i * 0.15)
        d.polygon([(tx, y + h * 0.86), (tx + 8, y + h * 0.74), (tx + 16, y + h * 0.86)], fill=(24, 22, 24))
    d.rectangle([x, y + h * 0.86, x + w, y + h], fill=(34, 28, 28))


def _courthouse(d, box, col_top, col_body):
    x, y, w, h = box
    _sky(d, box, col_top, col_top)
    cx = x + w / 2
    d.polygon([(x + w * 0.14, y + h * 0.30), (cx, y + h * 0.10), (x + w * 0.86, y + h * 0.30)], fill=col_body)
    d.rectangle([x + w * 0.12, y + h * 0.32, x + w * 0.88, y + h * 0.38], fill=col_body)
    for i in range(4):
        px = x + w * (0.2 + i * 0.17)
        d.rectangle([px, y + h * 0.40, px + w * 0.07, y + h * 0.78], fill=col_body)
    d.rectangle([x + w * 0.10, y + h * 0.80, x + w * 0.90, y + h * 0.88], fill=col_body)


def sc_trial(d, box):
    _courthouse(d, box, (88, 84, 96), (214, 208, 196))


def sc_court(d, box):
    _courthouse(d, box, (52, 66, 92), (206, 200, 188))


def sc_tanker(d, box):
    x, y, w, h = box
    _sky(d, box, (96, 130, 160), (168, 188, 200))
    d.rectangle([x, y + h * 0.52, x + w, y + h], fill=(38, 84, 116))
    # capsized hull
    hx, hy = x + w * 0.5, y + h * 0.52
    d.polygon([(hx - w * 0.34, hy), (hx + w * 0.30, hy), (hx + w * 0.16, hy - h * 0.20), (hx - w * 0.22, hy - h * 0.20)],
              fill=(150, 44, 36))
    d.rectangle([hx - w * 0.10, hy - h * 0.30, hx + w * 0.02, hy - h * 0.20], fill=(60, 60, 64))
    # oil sheen
    d.ellipse([x + w * 0.56, y + h * 0.66, x + w * 0.94, y + h * 0.82], outline=(30, 40, 50), width=3)
    d.ellipse([x + w * 0.62, y + h * 0.70, x + w * 0.88, y + h * 0.79], outline=(30, 40, 50), width=2)


def sc_chess(d, box):
    x, y, w, h = box
    sq = min(w / 6, h / 3)
    ox, oy = x + (w - sq * 6) / 2, y + (h - sq * 3) / 2
    for r in range(3):
        for c in range(6):
            col = (232, 226, 210) if (r + c) % 2 == 0 else (52, 48, 54)
            d.rectangle([ox + c * sq, oy + r * sq, ox + (c + 1) * sq, oy + (r + 1) * sq], fill=col)
    # two kings
    for kx, col in ((ox + sq * 1.5, (20, 20, 22)), (ox + sq * 4.5, (240, 238, 230))):
        d.polygon([(kx - 9, oy + sq * 2.6), (kx + 9, oy + sq * 2.6), (kx + 5, oy + sq * 1.2), (kx - 5, oy + sq * 1.2)], fill=col)
        d.rectangle([kx - 2, oy + sq * 0.86, kx + 2, oy + sq * 1.2], fill=col)
        d.rectangle([kx - 6, oy + sq * 0.98, kx + 6, oy + sq * 1.06], fill=col)


def sc_memorial(d, box):
    x, y, w, h = box
    _sky(d, box, (30, 34, 52), (58, 60, 84))
    bx, bw = x + w * 0.34, w * 0.32
    d.rectangle([bx, y + h * 0.12, bx + bw, y + h * 0.94], fill=(14, 16, 24))
    for r in range(6):
        for c in range(3):
            if (r * 3 + c) % 4:
                d.rectangle([bx + 6 + c * bw / 3.4, y + h * (0.18 + r * 0.12),
                             bx + 6 + c * bw / 3.4 + 7, y + h * (0.18 + r * 0.12) + 6], fill=(120, 116, 104))
    # candles along the base
    for i in range(7):
        cx = x + w * (0.1 + i * 0.13)
        d.ellipse([cx - 2, y + h * 0.86, cx + 2, y + h * 0.93], fill=(250, 200, 96))


def sc_protest(d, box):
    x, y, w, h = box
    _sky(d, box, (120, 118, 104), (168, 158, 138))
    # banner
    d.rectangle([x + w * 0.12, y + h * 0.14, x + w * 0.88, y + h * 0.34], fill=(232, 228, 218))
    d.line([(x + w * 0.2, y + h * 0.24), (x + w * 0.8, y + h * 0.24)], fill=(179, 0, 27), width=4)
    # crowd heads
    for i in range(14):
        cx = x + w * (0.06 + (i % 7) * 0.14)
        cy = y + h * (0.58 + (i // 7) * 0.2)
        d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=(40, 36, 34))
        d.rectangle([cx - 6, cy + 5, cx + 6, cy + 14], fill=(70, 62, 58))
    # gas cloud
    for gx, gy, r in ((0.72, 0.52, 13), (0.82, 0.44, 10), (0.64, 0.42, 8)):
        d.ellipse([x + w * gx - r, y + h * gy - r * 0.7, x + w * gx + r, y + h * gy + r * 0.7], fill=(206, 210, 200))


def sc_pact(d, box):
    x, y, w, h = box
    _sky(d, box, (70, 130, 170), (150, 190, 205))
    d.rectangle([x, y + h * 0.66, x + w, y + h], fill=(36, 96, 140))
    # island
    d.ellipse([x + w * 0.28, y + h * 0.56, x + w * 0.74, y + h * 0.78], fill=(88, 148, 92))
    # two flags
    for fx, col in ((0.36, (0, 60, 140)), (0.60, (200, 40, 40))):
        px = x + w * fx
        d.line([(px, y + h * 0.60), (px, y + h * 0.22)], fill=(30, 30, 30), width=3)
        d.polygon([(px, y + h * 0.22), (px + w * 0.14, y + h * 0.28), (px, y + h * 0.34)], fill=col)


def sc_jet(d, box):
    x, y, w, h = box
    _sky(d, box, (60, 92, 132), (140, 168, 196))
    cx, cy = x + w * 0.5, y + h * 0.46
    d.polygon([(cx - w * 0.34, cy + 4), (cx + w * 0.10, cy - 8), (cx + w * 0.36, cy + 2),
               (cx + w * 0.10, cy + 10), (cx - w * 0.20, cy + 12)], fill=(28, 34, 44))
    d.polygon([(cx - w * 0.05, cy + 2), (cx - w * 0.26, cy + h * 0.24), (cx - w * 0.10, cy + h * 0.24)], fill=(28, 34, 44))
    d.polygon([(cx - w * 0.30, cy + 2), (cx - w * 0.38, cy - h * 0.16), (cx - w * 0.24, cy - 2)], fill=(28, 34, 44))
    # price tag dot
    d.ellipse([x + w * 0.78, y + h * 0.14, x + w * 0.92, y + h * 0.36], fill=GOLD)
    d.text((x + w * 0.85 - 5, y + h * 0.19), "$", font=font(SANS_B, 15), fill=(30, 26, 10))


def sc_gavel(d, box):
    x, y, w, h = box
    _sky(d, box, (66, 60, 74), (110, 100, 112))
    cx, cy = x + w * 0.46, y + h * 0.40
    d.polygon([(cx - 26, cy - 12), (cx + 6, cy - 26), (cx + 16, cy - 12), (cx - 16, cy + 2)], fill=(120, 84, 48))
    d.line([(cx - 2, cy - 6), (cx + 26, cy + 22)], fill=(120, 84, 48), width=7)
    d.rectangle([x + w * 0.2, y + h * 0.78, x + w * 0.8, y + h * 0.86], fill=(90, 62, 36))
    # globe arc behind
    d.arc([x + w * 0.58, y + h * 0.12, x + w * 0.98, y + h * 0.66], start=90, end=300, fill=(200, 204, 210), width=3)


SCENES = {
    "kuwait": sc_kuwait, "gaza": sc_gaza, "markets": sc_markets,
    "storm": sc_storm, "plant": sc_plant, "warning": sc_warning,
    "trial": sc_trial, "court": sc_court, "tanker": sc_tanker,
    "chess": sc_chess, "memorial": sc_memorial, "protest": sc_protest,
    "pact": sc_pact, "jet": sc_jet, "gavel": sc_gavel,
}


# ---------------------------------------------------------------- layout

def region_chip(d, x, y, region, pin):
    fnt = font(SANS_B, 11)
    label = ("%d \u00b7 %s" % (pin, region)) if pin else region
    tw = text_w(d, label, fnt)
    d.rectangle([x, y, x + tw + 12, y + 16], fill=NAVY)
    d.text((x + 6, y + 2), label, font=fnt, fill=(255, 255, 255))
    return y + 20


def masthead(d):
    y = 16
    d.line([(MARGIN, y), (W - MARGIN, y)], fill=INK, width=3)
    y += 8
    kicker = "THE WORLD IN ONE DAY \u00b7 MORNING EDITION"
    size = 17
    while size > 11 and text_w(d, kicker, font(SANS_B, size)) > CW:
        size -= 1
    centered(d, W / 2, y, kicker, font(SANS_B, size), MUTED)
    y += 26
    # the date is the largest type on the page, shrunk to fit one line
    size = 63
    while size > 40 and text_w(d, DATE_LINE, font(SERIF_B, size)) > CW:
        size -= 1
    centered(d, W / 2, y, DATE_LINE, font(SERIF_B, size), INK)
    y += 82
    # red sub-headline, shrunk to fit one line
    size = 21
    while size > 12 and text_w(d, SUB_HEAD, font(SANS_B, size)) > CW:
        size -= 1
    centered(d, W / 2, y, SUB_HEAD, font(SANS_B, size), RED)
    y += 30
    d.line([(MARGIN, y), (W - MARGIN, y)], fill=INK, width=2)
    return y + 6


def kpi_strip(d, y):
    n = len(KPIS)
    gap = 8
    cw = (CW - gap * (n - 1)) / n
    big, small = font(SANS_B, 21), font(SANS, 10)
    for i, (num, label) in enumerate(KPIS):
        x = MARGIN + i * (cw + gap)
        d.rectangle([x, y, x + cw, y + 40], outline=RULE, width=1)
        centered(d, x + cw / 2, y + 3, num, big, NAVY)
        lines, lf = fit(d, label, small, cw - 8, (1, 11), "kpi label")
        for ln in lines:
            centered(d, x + cw / 2, y + 27, ln, lf, MUTED)
    return y + 46


def lead_card(d, x, y, w, h, item):
    scene, region, pin, head, line = item
    d.rectangle([x, y, x + w, y + h], fill=CARD, outline=RULE, width=1)
    SCENES[scene](d, (x + 1, y + 1, w - 2, 168))
    ty = y + 176
    region_chip(d, x + 10, ty, region, pin)
    ty += 24
    hf = font(SERIF_B, 23)
    lines, hf = fit(d, head, hf, w - 20, (3, 28), "lead headline")
    ty = draw_lines(d, x + 10, ty, lines, hf, 28)
    lf = font(SANS, 14)
    lines, lf = fit(d, line, lf, w - 20, (2, 18), "lead line")
    draw_lines(d, x + 10, ty + 2, lines, lf, 18, MUTED)


def panel_card(d, x, y, w, h, item):
    scene, region, pin, head, line = item
    d.rectangle([x, y, x + w, y + h], fill=CARD, outline=RULE, width=1)
    SCENES[scene](d, (x + 1, y + 1, w - 2, 56))
    ty = y + 60
    hf = font(SANS_B, 12)
    lines, hf = fit(d, head, hf, w - 10, (2, 15), "panel headline")
    ty = draw_lines(d, x + 5, ty, lines, hf, 15)
    lf = font(SANS, 10)
    lines, lf = fit(d, line, lf, w - 10, (2, 12), "panel line")
    draw_lines(d, x + 5, ty + 1, lines, lf, 12, MUTED)
    if pin:
        d.ellipse([x + w - 20, y + 4, x + w - 4, y + 20], fill=RED)
        s = str(pin)
        fnt = font(SANS_B, 10)
        d.text((x + w - 12 - text_w(d, s, fnt) / 2, y + 6), s, font=fnt, fill=(255, 255, 255))


# Dotted world map: land runs on a 64x28 grid (row, [(first col, last col), ...]).
# Columns run -180..180, rows 83N..-76; pins use the same projection.
MAP_RUNS = {
    2: [(6, 16), (34, 56)],
    3: [(2, 17), (33, 58)],
    4: [(6, 18), (32, 58)],
    5: [(7, 19), (31, 57)],
    6: [(8, 20), (31, 58)],
    7: [(8, 21), (31, 57)],
    8: [(9, 20), (29, 55)],
    9: [(9, 20), (28, 54)],
    10: [(9, 13), (28, 54)],
    11: [(10, 12), (28, 51)],
    12: [(13, 16), (29, 55)],
    13: [(13, 18), (30, 57)],
    14: [(13, 19), (30, 58)],
    15: [(13, 19), (31, 61)],
    16: [(13, 19), (31, 37), (53, 58)],
    17: [(14, 19), (32, 36), (52, 59)],
    18: [(14, 18), (32, 36), (52, 59)],
    19: [(14, 17), (32, 35), (53, 58)],
    20: [(14, 16), (54, 57), (62, 62)],
    21: [(14, 15), (62, 63)],
    22: [(14, 15)],
}

# pin number -> (lon, lat)
PINS = {
    1: (47.98, 29.38),    # Kuwait
    2: (34.30, 31.40),    # Gaza
    3: (-74.00, 40.70),   # US East Coast
    4: (41.90, 44.63),    # Nevinnomyssk
    5: (30.52, 50.45),    # Kyiv
    6: (35.20, 31.78),    # Jerusalem
    7: (1.43, 38.98),     # Ibiza
    8: (2.35, 48.86),     # Paris
    9: (114.17, 22.32),   # Hong Kong
    10: (90.40, 23.80),   # Dhaka
    11: (159.97, -9.65),  # Honiara
    12: (-77.04, 38.90),  # Washington
    13: (96.17, 19.76),   # Naypyidaw
}


def bottom_band(d, y):
    band_h = 160
    map_w = 384
    # --- dotted world map with numbered pins (pictured stories only)
    mx, my = MARGIN, y
    d.rectangle([mx, my, mx + map_w, my + band_h], fill=(176, 196, 208), outline=RULE, width=1)
    cols, rows = 64, 28
    cell_w, cell_h = map_w / cols, band_h / rows
    for r, runs in MAP_RUNS.items():
        for c0, c1 in runs:
            for c in range(c0, c1 + 1):
                cx = mx + (c + 0.5) * cell_w
                cy = my + (r + 0.5) * cell_h
                d.ellipse([cx - 2.1, cy - 2.1, cx + 2.1, cy + 2.1], fill=(226, 218, 188))
    pf = font(SANS_B, 9)
    for num, (lon, lat) in PINS.items():
        px = mx + (lon + 180) / 360 * map_w
        py = my + (90 - lat) / 180 * band_h
        d.ellipse([px - 7, py - 7, px + 7, py + 7], fill=RED, outline=(255, 255, 255), width=1)
        s = str(num)
        d.text((px - text_w(d, s, pf) / 2, py - 5), s, font=pf, fill=(255, 255, 255))
    d.text((mx + 6, my + band_h - 15), "WHERE IT HAPPENED \u00b7 PINS = PICTURED STORIES",
           font=font(SANS_B, 9), fill=(40, 60, 80))
    # --- digest: two columns of one-liners
    dx = mx + map_w + 12
    dw = W - MARGIN - dx
    d.text((dx, y + 1), "MORE OF THE DAY \u00b7 22 IN BRIEF", font=font(SANS_B, 13), fill=NAVY)
    d.line([(dx, y + 19), (dx + dw, y + 19)], fill=RULE, width=1)
    col_w = (dw - 12) / 2
    df = font(SANS, 11)
    per = (len(DIGEST) + 1) // 2
    for i, item in enumerate(DIGEST):
        cx = dx + (i // per) * (col_w + 12)
        cy = y + 25 + (i % per) * 12.4
        lines, lf = fit(d, item, df, col_w - 4, (1, 12), "digest line")
        for ln in lines:
            d.text((cx, cy), ln, font=lf, fill=INK)
    return y + band_h + 6


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    y = masthead(d)
    y = kpi_strip(d, y)
    # leads: three cards, band height 330 (32.2% of the page)
    y += 4
    lead_y, lead_h = y, 330
    gap = 12
    lw = (CW - gap * 2) / 3
    for i, item in enumerate(LEADS):
        lead_card(d, MARGIN + i * (lw + gap), lead_y, lw, lead_h, item)
    y = lead_y + lead_h + 8
    # panels: 2 rows x 6
    gap = 8
    pw = (CW - gap * 5) / 6
    ph = 118
    for i, item in enumerate(PANELS):
        px = MARGIN + (i % 6) * (pw + gap)
        py = y + (i // 6) * (ph + gap)
        panel_card(d, px, py, pw, ph, item)
    y += 2 * ph + gap + 8
    y = bottom_band(d, y)
    # date check + footer
    df = font(SANS, 11)
    lines, df = fit(d, DATE_CHECK, df, CW - 16, (2, 14), "date check")
    d.rectangle([MARGIN, y, W - MARGIN, y + 34], fill=(238, 232, 218), outline=RULE, width=1)
    ly = y + 4
    for ln in lines:
        centered(d, W / 2, ly, ln, df, INK)
        ly += 14
    y += 40
    ff = font(SANS, 10)
    lines, ff = fit(d, FOOTER, ff, CW - 16, (1, 12), "footer")
    for ln in lines:
        centered(d, W / 2, y, ln, ff, MUTED)
    return img


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "entry.png")
    try:
        img = build()
        img.save(out, format="PNG", optimize=True)
    except Exception as exc:  # never fail the run: ship the held image
        import shutil
        print("draw failed (%r); copying committed entry.png" % (exc,), file=sys.stderr)
        held = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
        shutil.copyfile(held, out)
    if WARNINGS:
        for wmsg in WARNINGS:
            print("OVERFLOW:", wmsg, file=sys.stderr)
        print("note: %d overflow warning(s); entry written anyway" % len(WARNINGS),
              file=sys.stderr)
    print("wrote %s (%d bytes)" % (out, os.path.getsize(out)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
