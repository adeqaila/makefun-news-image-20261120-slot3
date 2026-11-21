#!/usr/bin/env python3
"""D3 — "The World in One Day" — news-image-20261120, slot 3.

Renders entry.png (1024x1024 broadsheet) from verified 20 Nov 2026 news.
Stdlib + PIL only, no network, fully deterministic: same input bytes out
on every run. Run:  python3 compose.py [out.png]

Layout (after the leader broadsheet pattern, redrawn from scratch):
  top line | masthead | subhead | 6-stat strip | 7-region bar |
  3 big stories with procedural visuals | 10 small stories in 5x2 |
  map + 22-more list | by-the-clock | date-check box | footer.
All 35 stories happened, or were first reported, on Friday 20 Nov 2026.
See AUDIT.md for the per-story verification.
"""

import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 243, 232)
INK = (17, 17, 17)
RED = (176, 30, 36)
DARKRED = (138, 20, 25)
NAVY = (26, 42, 74)
GRAY = (96, 94, 88)
FAINT = (168, 164, 152)
RULE = (60, 58, 52)
GREEN = (28, 110, 58)
SEA = (206, 224, 234)
LAND = (232, 217, 172)
LAND_LINE = (176, 154, 106)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

WARNINGS = []


def font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


# ---------------------------------------------------------------- data
TOP_LEFT = "THE WORLD IN ONE DAY"
TOP_RIGHT = "35 STORIES \u00b7 7 REGIONS \u00b7 EVERY ONE DATED FRIDAY 20 NOVEMBER 2026"
MASTHEAD = "Friday 20 November 2026"
SUBHEAD = ("Russian missiles hit Kyiv\u2019s bridges \u00b7 Cyclone Akvan strikes India "
           "\u00b7 An AI sell-off sinks Asia\u2019s markets \u00b7 UK and EU seal a deal")

STATS = [
    ("3", "bridges over the Dnipro\ndamaged in Kyiv"),
    ("372,000", "people moved to shelters\nbefore Akvan"),
    ("\u22126.2%", "Taiwan\u2019s share index,\nFriday\u2019s close"),
    ("100,000", "youth visas a year in the\nUK\u2013EU deal"),
    ("2.3%", "Japan\u2019s consumer inflation\nin October"),
    ("118", "runs by Glenn Phillips\nagainst India"),
]

REGIONS = [
    ("EUROPE", 9, (47, 90, 168)),
    ("MIDDLE EAST", 4, (138, 109, 59)),
    ("ASIA", 11, (176, 30, 36)),
    ("AFRICA", 5, (46, 125, 79)),
    ("AMERICAS", 3, (122, 31, 43)),
    ("OCEANIA", 2, (46, 127, 134)),
    ("WORLD", 1, (107, 107, 107)),
]

# Big stories: number, kicker, headline, body, visual kind, label, chip.
BIG = [
    dict(num=1, kicker="KYIV, UKRAINE \u00b7 WAR",
         headline="Russian missiles hit three Kyiv bridges",
         body=("An overnight barrage of about 110 missiles and 400 drones killed "
               "at least nine people across Ukraine and cut power and water in "
               "the capital. (Kyiv Independent, BBC)"),
         visual="kyiv", label="KYIV", chip="3 bridges hit"),
    dict(num=2, kicker="ODISHA, INDIA \u00b7 CYCLONE",
         headline="Cyclone Akvan comes ashore in eastern India",
         body=("The storm crossed the coast near Gopalpur at 02:00 UTC after "
               "372,000 people were moved to shelters. No deaths were reported. "
               "(IMD, The Hindu)"),
         visual="akvan", label="CYCLONE AKVAN", chip="Landfall \u00b7 02:00 UTC"),
    dict(num=3, kicker="TAIPEI \u00b7 SEOUL \u00b7 TOKYO \u00b7 MARKETS",
         headline="AI sell-off sinks Asia\u2019s stock markets",
         body=("Taiwan\u2019s index fell 6.2% to end its worst week since 1991. "
               "Seoul lost 5.2% and Tokyo 5.1% as chipmakers led the slide. "
               "(Al Jazeera, Anadolu)"),
         visual="selloff", label="AI SELL-OFF", chip="Closing prices"),
]

# Small stories: number, red label, kicker, headline, body, visual kind, chip.
SMALL = [
    dict(num=4, label="UK\u2013EU DEAL", kicker="BRUSSELS \u00b7 DIPLOMACY",
         headline="UK and EU seal a \u201creset\u201d deal",
         body="Food trade, youth visas, carbon link. (Reuters)",
         visual="ukeu", chip="Agreed \u00b7 Reuters"),
    dict(num=5, label="COP31: NO DEAL", kicker="ANTALYA \u00b7 CLIMATE",
         headline="COP31 runs past its deadline with no deal",
         body="Talks suspended to Saturday; the draft drops fossil fuels. (Reuters, AP)",
         visual="cop", chip="Ongoing \u00b7 UN News"),
    dict(num=6, label="POLAND: MISSILE", kicker="EASTERN POLAND \u00b7 SECURITY",
         headline="Russian cruise missile lands in Poland",
         body="It fell in a field; jets scrambled in response. (Reuters, AP)",
         visual="poland", chip="Minister says \u00b7 Reuters"),
    dict(num=7, label="IRAQ: ARMY IN", kicker="CENTRAL IRAQ \u00b7 SECURITY",
         headline="Iraqi army enters a militia stronghold",
         body="Troops deploy to Jurf al-Sakhar. (Reuters)",
         visual="iraq", chip="Witnessed \u00b7 Reuters"),
    dict(num=8, label="ITALY: STRIKE", kicker="ITALY \u00b7 LABOUR",
         headline="General strike over Italy\u2019s budget",
         body="Workers and students march in 100 cities. (Reuters, AP)",
         visual="italy", chip="Reported \u00b7 Reuters"),
    dict(num=9, label="JAPAN: +2.3%", kicker="TOKYO \u00b7 ECONOMY",
         headline="Japan\u2019s inflation picks up to 2.3%",
         body="A December rate rise stays in view. (Reuters)",
         visual="japan", chip="Official data \u00b7 Reuters"),
    dict(num=10, label="SEOUL: IMPEACH", kicker="SEOUL \u00b7 POLITICS",
         headline="Seoul moves to impeach top judge",
         body="The ruling party adopts impeachment of Chief Justice Cho. (KJD)",
         visual="seoul", chip="Party decision \u00b7 KJD"),
    dict(num=11, label="KENYA: OIL", kicker="TURKANA, KENYA \u00b7 ENERGY",
         headline="Kenya starts drilling its first oil well",
         body="First crude is due on 1 December. (Reuters)",
         visual="kenya", chip="Ceremony held \u00b7 allAfrica"),
    dict(num=12, label="PHILLIPS: 118", kicker="WELLINGTON \u00b7 CRICKET",
         headline="Phillips hits 118 against India",
         body="Unbeaten 118 as New Zealand reach 368 on day two. (AP)",
         visual="cricket", chip="Scorecard \u00b7 ICC"),
    dict(num=13, label="TAIZ: VOICES", kicker="TAIZ \u00b7 BESIEGED CITY",
         headline="Voices from besieged Taiz",
         body="Families inside Taiz tell the BBC their story. (BBC)",
         visual="taiz", chip="BBC \u00b7 Taiz"),
]

# 22 more stories: (number, one line <= 55 chars, source already inside).
ALSO = [
    (14, "Lviv A strike on a railway station kills two (BBC)"),
    (15, "APEC leaders meet on day two in Shenzhen (AP)"),
    (16, "Trump holds noon conference in Washington (AP)"),
    (17, "Europe ready for Russia talks in Berlin (BBC)"),
    (18, "Estonia approves Russia border closure (Reuters)"),
    (19, "Berlin pupils strike over military service (Reuters)"),
    (20, "General says UK runs cyber attacks abroad (Sky)"),
    (21, "Israeli strikes hit Lebanon\u2019s south and east (AFP)"),
    (22, "Gunmen fire at cargo ship off Yemen (UKMTO)"),
    (23, "Modi opens SCO forum in Delhi (Reuters)"),
    (24, "India launches its own H5N1 vaccine (Reuters)"),
    (25, "Sudan\u2019s army pushes towards Al Nahud (Reuters)"),
    (26, "Sheinbaum leads Revolution Day parade (AP)"),
    (27, "China leaves its loan rates unchanged (Xinhua)"),
    (28, "Haiti approves a Salvadoran troop deal (AP)"),
    (29, "World Children\u2019s Day marked worldwide (UN)"),
    (30, "Abuja court rejects Atiku evidence bid (Channels)"),
    (31, "Malawi fuel crisis forces long queues (Al Jazeera)"),
    (32, "AfDB: 22 countries near debt distress (This Day)"),
    (33, "Sydney shares slide 1.6% in AI sell-off (Reuters)"),
    (34, "SoftBank shares fall 14.5% in a day (Al Jazeera)"),
    (35, "Kospi ends the week 7.9% lower (Anadolu)"),
]

CLOCK = [
    ("00:13", "Taiz voices reach the BBC"),
    ("00:50", "Europe ready for talks"),
    ("02:00", "Akvan landfall"),
    ("17:00", "Trump presser, Washington"),
]

DATE_CHECK = (
    "Left out as Thursday 19 November\u2019s news: the World Court\u2019s ruling on "
    "Myanmar, the three-leader declaration in Shenzhen, Bukele\u2019s filing for a "
    "third term, Tonga\u2019s drought emergency and the migrant boat lost off "
    "Senegal. Not yet happened, so not shown: BepiColombo\u2019s entry into orbit "
    "round Mercury and any final COP31 text."
)

FOOTER_L = ("Every story here happened, or was first reported, on Friday "
            "20 November 2026. Officials\u2019 counts are attributed.")
FOOTER_R = "Sources named beside each story \u00b7 original drawings"

# Map pins: story number -> (lon, lat, dx, dy) offset of the number badge.
# Badges spread so no two overlap: East Asia (3/9/10) fanned apart,
# Antalya/Baghdad (5/7) and Kenya/Taiz (11/13) separated the same way.
PINS = {
    1: (30.5, 50.4, 6, -16), 2: (84.9, 19.3, 0, 12), 3: (121.5, 25.0, 12, 14),
    4: (4.4, 50.8, -22, -10), 5: (30.7, 36.9, 20, 18),
    6: (23.0, 50.4, -24, 4), 7: (44.4, 33.3, 26, -12), 8: (12.5, 41.9, -16, 16),
    9: (139.7, 35.7, 18, -12), 10: (127.0, 37.5, -22, -16),
    11: (36.5, 3.5, -22, 18), 12: (174.8, -41.3, -14, 0),
    13: (44.0, 13.6, 10, 16),
}

# Rough continent outlines, (lon, lat) vertices, drawn by hand.
CONTINENTS = [
    [(-168, 66), (-140, 70), (-125, 71), (-110, 68), (-95, 69), (-85, 66),
     (-80, 73), (-70, 62), (-65, 60), (-55, 52), (-60, 46), (-70, 44),
     (-75, 38), (-80, 32), (-81, 26), (-90, 21), (-95, 19), (-97, 16),
     (-92, 15), (-86, 13), (-83, 9), (-80, 8), (-85, 11), (-90, 14),
     (-97, 16), (-105, 20), (-110, 23), (-114, 29), (-120, 34), (-125, 40),
     (-124, 48), (-130, 55), (-145, 60), (-158, 58), (-165, 60)],
    [(-80, 8), (-77, 4), (-80, -3), (-81, -6), (-77, -12), (-70, -18),
     (-70, -23), (-65, -28), (-60, -35), (-57, -38), (-62, -41), (-65, -45),
     (-68, -52), (-70, -48), (-73, -44),
     (-73, -37), (-71, -30), (-70, -23), (-70, -18), (-77, -12), (-81, -6)],
    [(-17, 15), (-17, 21), (-10, 31), (-5, 35), (0, 36), (10, 37), (11, 34),
     (20, 32), (30, 31), (32, 31), (35, 28), (37, 22), (40, 15), (43, 12),
     (48, 11), (51, 12), (44, 5), (41, 0), (40, -5), (36, -10), (35, -18),
     (32, -26), (28, -33), (20, -35), (17, -32), (15, -27), (12, -18),
     (12, -10), (9, -1), (9, 4), (-8, 5), (-13, 8), (-17, 12)],
    [(-10, 36), (-9, 43), (-2, 48), (-4, 50), (0, 51), (3, 53), (8, 57),
     (10, 59), (5, 60), (10, 62), (18, 69), (25, 71), (30, 70), (40, 68),
     (50, 69), (60, 69), (70, 72), (80, 73), (90, 75), (100, 77), (110, 74),
     (120, 73), (130, 72), (140, 72), (150, 70), (160, 70), (170, 67),
     (178, 65), (178, 64), (170, 60), (162, 56), (158, 52), (150, 59),
     (142, 55), (140, 50), (135, 44), (130, 42), (127, 40), (122, 38),
     (120, 32), (122, 28), (118, 25), (110, 20), (108, 18), (105, 10),
     (103, 8), (100, 6), (98, 10), (95, 16), (92, 21), (89, 22), (86, 20),
     (82, 17), (80, 13), (77, 8), (75, 12), (72, 20), (68, 23), (66, 25),
     (61, 25), (58, 26), (56, 27), (52, 28), (50, 29), (48, 30), (44, 29),
     (40, 31), (36, 36), (33, 36), (30, 36), (27, 37), (23, 36), (22, 37),
     (19, 40), (15, 44), (12, 44), (8, 44), (3, 43), (0, 40), (-2, 37),
     (-6, 36), (-9, 37)],
    [(114, -22), (113, -26), (115, -32), (118, -35), (124, -33), (129, -32),
     (132, -32), (135, -35), (138, -35), (140, -38), (145, -38), (150, -37),
     (153, -32), (153, -27), (150, -23), (146, -19), (142, -15), (142, -11),
     (137, -12), (135, -15), (132, -12), (130, -13), (126, -14), (122, -17),
     (118, -20)],
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (1, 51),
     (-2, 50)],
    [(130, 31), (132, 33), (135, 34), (138, 35), (140, 37), (141, 39),
     (141, 41), (142, 44), (144, 44), (141, 42), (140, 38), (138, 35),
     (135, 34), (132, 33)],
    [(167, -45), (170, -43), (173, -41), (175, -38), (177, -38), (175, -40),
     (173, -42), (170, -44), (167, -46)],
]


# ---------------------------------------------------------------- helpers
def wrap(d, text, fnt, max_w):
    """Greedy word wrap; returns list of lines that fit max_w."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if d.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(d, x, y, text, fnt, max_w, fill, leading, max_lines, tag):
    lines = wrap(d, text, fnt, max_w)
    if len(lines) > max_lines:
        WARNINGS.append("%s: %d lines, kept %d: %r"
                        % (tag, len(lines), max_lines, text[:60]))
        lines = lines[:max_lines]
    for i, line in enumerate(lines):
        d.text((x, y + i * leading), line, font=fnt, fill=fill)
    return y + len(lines) * leading


def label_box(d, x, y, text, fnt, fg=(255, 255, 255), bg=RED, pad=4):
    w = int(d.textlength(text, font=fnt)) + 2 * pad
    h = fnt.size + 2 * pad - 2
    d.rectangle([x, y, x + w, y + h], fill=bg)
    d.text((x + pad, y + pad - 1), text, font=fnt, fill=fg)
    return w, h


def chip_box(d, x, y, text, fnt, fg=(255, 255, 255), bg=(20, 20, 20), pad=3):
    return label_box(d, x, y, text, fnt, fg=fg, bg=bg, pad=pad)


def rule(d, x0, x1, y, fill=RULE, width=1):
    d.line([(x0, y), (x1, y)], fill=fill, width=width)


# ---------------------------------------------------------------- big visuals
def draw_kyiv(d, x, y, w, h):
    """Night over the Dnipro: skyline, bridge, missile streaks, fires."""
    x, y, w, h = int(x), int(y), int(w), int(h)
    d.rectangle([x, y, x + w, y + h], fill=(16, 28, 58))
    # stars (fixed positions, deterministic)
    for sx, sy, r in [(18, 12, 1), (60, 26, 1), (120, 10, 2), (180, 22, 1),
                      (240, 14, 1), (290, 30, 2), (40, 44, 1), (150, 38, 1),
                      (210, 48, 1), (270, 8, 1), (95, 18, 1), (320, 40, 1),
                      (135, 6, 1), (205, 8, 1), (75, 34, 1), (305, 52, 1)]:
        d.ellipse([x + sx - r, y + sy - r, x + sx + r, y + sy + r],
                  fill=(220, 225, 240))
    # moon with halo + crater
    d.ellipse([x + w - 58, y + 4, x + w - 20, y + 42], fill=(110, 118, 148))
    d.ellipse([x + w - 52, y + 10, x + w - 26, y + 36], fill=(235, 228, 200))
    d.ellipse([x + w - 46, y + 16, x + w - 36, y + 26], fill=(208, 198, 162))
    # skyline silhouettes (varied roofs, two antennas, one dome)
    for bx, bw, bh in [(0, 34, 46), (38, 26, 62), (68, 30, 40), (102, 22, 58),
                       (128, 36, 48), (168, 24, 66), (196, 30, 44), (230, 28, 60),
                       (262, 34, 42), (300, 26, 56)]:
        d.rectangle([x + bx, y + h - 58 - bh, x + bx + bw, y + h - 58],
                    fill=(10, 16, 34))
        for wy in range(y + h - 58 - bh + 6, y + h - 60, 12):
            for wx in range(x + bx + 5, x + bx + bw - 4, 10):
                if (wx * 7 + wy * 3) % 11 < 4:
                    d.rectangle([wx, wy, wx + 3, wy + 4], fill=(255, 214, 120))
    # church dome on the 128-wide block, antennas on two towers
    d.arc([x + 134, y + h - 58 - 48 - 12, x + 158, y + h - 58 - 48 + 4],
          180, 360, fill=(10, 16, 34), width=2)
    d.pieslice([x + 134, y + h - 58 - 48 - 12, x + 158, y + h - 58 - 48 + 4],
               180, 360, fill=(10, 16, 34))
    for ax in (51, 243):
        d.line([(x + ax, y + h - 58 - 62), (x + ax, y + h - 58 - 74)],
               fill=(10, 16, 34), width=2)
        d.ellipse([x + ax - 2, y + h - 58 - 76, x + ax + 2, y + h - 58 - 72],
                  fill=(255, 90, 70))
    # searchlight beams fanning up from two rooftops
    d.line([(x + 60, y + h - 58 - 60), (x + 22, y + 12)],
           fill=(190, 200, 228), width=2)
    d.line([(x + 282, y + h - 58 - 40), (x + 318, y + 8)],
           fill=(190, 200, 228), width=2)
    # river
    d.rectangle([x, y + h - 58, x + w, y + h], fill=(24, 52, 96))
    for rx in range(6, w, 26):
        d.line([(x + rx, y + h - 30), (x + rx + 14, y + h - 30)],
               fill=(70, 110, 170), width=2)
    # bridge deck + arches + suspension cables
    by = y + h - 66
    d.rectangle([x, by, x + w, by + 7], fill=(8, 12, 26))
    for cx in (60, 165, 270):
        d.arc([x + cx - 42, by - 26, x + cx + 42, by + 8], 180, 360,
              fill=(200, 205, 220), width=3)
        d.line([(x + cx - 42, by), (x + cx - 42, by + 7)], fill=(200, 205, 220),
               width=3)
        d.line([(x + cx + 42, by), (x + cx + 42, by + 7)], fill=(200, 205, 220),
               width=3)
        for vx in (-28, -14, 0, 14, 28):
            d.line([(x + cx + vx, by - 14), (x + cx + vx, by)],
                   fill=(150, 158, 175), width=1)
    # missile streaks (dashed) + smoke puff at one trail end
    for (mx0, my0, mx1, my1) in [(300, 6, 168, 62), (250, 2, 62, 66),
                                 (330, 30, 272, 60), (110, 4, 52, 40)]:
        steps = 9
        for i in range(steps):
            if i % 2:
                continue
            t0 = i / steps
            t1 = (i + 0.7) / steps
            d.line([(x + mx0 + (mx1 - mx0) * t0, y + my0 + (my1 - my0) * t0),
                    (x + mx0 + (mx1 - mx0) * t1, y + my0 + (my1 - my0) * t1)],
                   fill=(255, 230, 150), width=2)
    d.ellipse([x + 296, y + 2, x + 306, y + 12], fill=(120, 125, 140))
    # fireballs with layered glow on the bridge
    for fx, fy in [(62, 62), (168, 58), (272, 56)]:
        d.ellipse([x + fx - 13, y + fy - 13, x + fx + 13, y + fy + 13],
                  fill=(200, 90, 20))
        d.ellipse([x + fx - 9, y + fy - 9, x + fx + 9, y + fy + 9],
                  fill=(255, 140, 30))
        d.ellipse([x + fx - 5, y + fy - 5, x + fx + 5, y + fy + 5],
                  fill=(255, 200, 80))
        d.ellipse([x + fx - 2, y + fy - 2, x + fx + 2, y + fy + 2],
                  fill=(255, 235, 150))
        # reflection dashes in the river below each fire
        for k, rw in enumerate((16, 11, 7)):
            d.line([(x + fx - rw // 2, y + h - 22 + k * 6),
                    (x + fx + rw // 2, y + h - 22 + k * 6)],
                   fill=(255, 160, 60), width=2)


def draw_akvan(d, x, y, w, h):
    """Cyclone spiral over the Odisha coast."""
    x, y, w, h = int(x), int(y), int(w), int(h)
    d.rectangle([x, y, x + w, y + h], fill=(58, 122, 168))
    # faint cloud texture over the sea (fixed soft ellipses)
    for ex, ey, ew, eh in [(200, 18, 70, 14), (250, 118, 60, 12),
                           (180, 130, 80, 14), (290, 60, 44, 10)]:
        d.ellipse([x + ex, y + ey, x + ex + ew, y + ey + eh],
                  fill=(90, 145, 185))
    # land (left) and coast, with a small bay and a river inland
    d.polygon([(x, y), (x + 92, y), (x + 78, y + 50), (x + 96, y + 95),
               (x + 70, y + h), (x, y + h)], fill=(196, 178, 120))
    d.polygon([(x + 92, y), (x + 78, y + 50), (x + 96, y + 95),
               (x + 70, y + h), (x + 70, y + h), (x + 92, y + h),
               (x + 104, y + 60), (x + 96, y)], fill=(140, 168, 110))
    d.arc([x + 70, y + 42, x + 96, y + 74], 270, 90, fill=(120, 148, 96),
          width=2)
    d.line([(x + 30, y + 30), (x + 55, y + 55), (x + 82, y + 52)],
           fill=(110, 140, 170), width=2)
    # rain streaks over land
    for rx, ry in [(20, 20), (40, 55), (15, 90), (55, 110), (30, 130),
                   (65, 30), (45, 75), (10, 60), (58, 128), (25, 108)]:
        d.line([(x + rx, y + ry), (x + rx - 5, y + ry + 14)],
               fill=(220, 235, 245), width=2)
    # spiral: concentric arcs, tighter toward the eye, plus outer rain arms
    cx, cy = x + w - 105, y + 78
    for r, a0, a1 in [(82, 30, 110), (70, 200, 280)]:
        d.arc([cx - r, cy - r, cx + r, cy + r], a0, a1, fill=(210, 225, 238),
              width=3)
    for r, a0, a1 in [(58, 20, 300), (46, 120, 40), (35, 200, 120),
                      (24, 280, 200), (14, 40, 320)]:
        d.arc([cx - r, cy - r, cx + r, cy + r], a0, a1, fill=(240, 246, 250),
              width=4)
    # eye wall: double ring around the calm eye
    d.ellipse([cx - 12, cy - 12, cx + 12, cy + 12], outline=(240, 246, 250),
              width=2)
    d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=(240, 246, 250))
    # landfall marker with white ring
    d.ellipse([x + 92 - 8, y + 62 - 8, x + 92 + 8, y + 62 + 8],
              outline=(255, 255, 255), width=2)
    d.ellipse([x + 92 - 6, y + 62 - 6, x + 92 + 6, y + 62 + 6], fill=RED)
    d.ellipse([x + 92 - 2, y + 62 - 2, x + 92 + 2, y + 62 + 2],
              fill=(255, 255, 255))
    # wind barbs (short ticks with a flag tick) around the spiral
    for bx, by, ang in [(cx - 70, cy - 30, 30), (cx + 60, cy - 45, -20),
                        (cx + 70, cy + 40, 15), (cx - 60, cy + 45, -35),
                        (cx - 88, cy + 8, 10), (cx + 84, cy - 8, -10)]:
        d.line([(bx, by), (bx + 12, by + 4)], fill=(230, 240, 248), width=2)
        d.line([(bx + 12, by + 4), (bx + 9, by + 9)], fill=(230, 240, 248),
               width=2)


def draw_selloff(d, x, y, w, h):
    """Falling market: candlesticks, red trend arrow, 4-market table."""
    x, y, w, h = int(x), int(y), int(w), int(h)
    d.rectangle([x, y, x + w, y + h], fill=(18, 24, 44))
    # grid + left axis labels (-2% per grid step)
    f_ax = font(SANS, 8)
    for i, gy in enumerate(range(y + 16, y + h - 8, 26)):
        d.line([(x + 10, gy), (x + w - 118, gy)], fill=(48, 58, 88), width=1)
        if i:
            d.text((x + 12, gy - 9), "-%d%%" % (2 * i), font=f_ax,
                   fill=(120, 130, 160))
    # candlesticks, falling left to right with one brief bounce
    candles = [(14, 24, 32), (34, 30, 42), (54, 40, 50), (74, 52, 60),
               (94, 48, 58), (114, 62, 72), (134, 78, 88), (154, 96, 106)]
    for i, (cx, top, bot) in enumerate(candles):
        col = (210, 60, 60) if i % 2 == 0 else (200, 80, 80)
        d.line([(x + cx + 6, y + top - 6), (x + cx + 6, y + bot + 6)],
               fill=col, width=2)
        d.rectangle([x + cx, y + top, x + cx + 12, y + bot], fill=col)
    # second index (Kospi, amber dashed) falling less steeply
    pts = [(18, 34), (48, 48), (78, 56), (108, 70), (138, 82), (166, 94)]
    for (px0, py0), (px1, py1) in zip(pts, pts[1:]):
        steps = 4
        for i in range(steps):
            if i % 2:
                continue
            t0 = i / steps
            t1 = (i + 0.6) / steps
            d.line([(x + px0 + (px1 - px0) * t0, y + py0 + (py1 - py0) * t0),
                    (x + px0 + (px1 - px0) * t1, y + py0 + (py1 - py0) * t1)],
                   fill=(255, 180, 80), width=2)
    for px, py in pts:
        d.ellipse([x + px - 2, y + py - 2, x + px + 2, y + py + 2],
                  fill=(255, 180, 80))
    # red trend arrow
    d.line([(x + 12, y + 26), (x + 172, y + 118)], fill=(255, 70, 70), width=4)
    d.polygon([(x + 172, y + 118), (x + 156, y + 112), (x + 168, y + 100)],
              fill=(255, 70, 70))
    # market table, right side
    tx = x + w - 112
    d.rectangle([tx, y + 8, x + w - 8, y + h - 8], fill=(255, 255, 255))
    rows = [("Taipei", "\u22126.2%"), ("Seoul", "\u22125.2%"),
            ("Tokyo", "\u22125.1%"), ("Hong Kong", "\u22121.9%")]
    f_city = font(SANS_B, 11)
    f_pct = font(SANS_B, 11)
    for i, (city, pct) in enumerate(rows):
        ry = y + 16 + i * 30
        d.text((tx + 6, ry), city, font=f_city, fill=INK)
        d.text((tx + 6, ry + 13), pct, font=f_pct, fill=RED)
        if i < 3:
            d.line([(tx + 4, ry + 27), (x + w - 12, ry + 27)], fill=FAINT,
                   width=1)


# ---------------------------------------------------------------- small visuals
def _stars(d, x, y, cx, cy, r, n=12, col=(255, 215, 0)):
    import math
    for i in range(n):
        a = 2 * math.pi * i / n - math.pi / 2
        sx, sy = cx + r * math.cos(a), cy + r * math.sin(a)
        d.ellipse([x + sx - 1, y + sy - 1, x + sx + 1, y + sy + 1], fill=col)


def draw_icon(d, kind, x, y, w, h):
    """One thin illustrative strip for a small story."""
    x, y, w, h = int(x), int(y), int(w), int(h)
    if kind == "ukeu":
        d.rectangle([x, y, x + w // 2, y + h], fill=(0, 51, 153))
        _stars(d, x, y, w // 4, h // 2, 9)
        d.rectangle([x + w // 2, y, x + w, y + h], fill=(0, 36, 125))
        d.rectangle([x + w // 2, y + h // 2 - 3, x + w, y + h // 2 + 3],
                    fill=(255, 255, 255))
        d.rectangle([x + 3 * w // 4 - 3, y, x + 3 * w // 4 + 3, y + h],
                    fill=(255, 255, 255))
        d.rectangle([x + w // 2, y + h // 2 - 1, x + w, y + h // 2 + 1],
                    fill=(200, 16, 46))
        d.rectangle([x + 3 * w // 4 - 1, y, x + 3 * w // 4 + 1, y + h],
                    fill=(200, 16, 46))
    elif kind == "cop":
        d.rectangle([x, y, x + w, y + h], fill=(178, 216, 232))
        d.ellipse([x + 8, y + 3, x + 34, y + h - 3], fill=(38, 110, 190))
        d.ellipse([x + 13, y + 7, x + 21, y + 13], fill=(90, 180, 110))
        d.ellipse([x + 22, y + 15, x + 30, y + 22], fill=(90, 180, 110))
        d.rectangle([x + w - 22, y + 4, x + w - 16, y + h - 6], fill=(220, 225, 230))
        d.ellipse([x + w - 24, y + h - 11, x + w - 14, y + h - 1], fill=RED)
        d.rectangle([x + w - 20, y + 6, x + w - 18, y + h - 6], fill=RED)
    elif kind == "poland":
        d.rectangle([x, y, x + w, y + h], fill=(198, 220, 190))
        d.rectangle([x, y + h - 8, x + w, y + h], fill=(120, 150, 110))
        for i in range(5):
            d.line([(x + 8 + i * 10, y + h - 12), (x + 14 + i * 10, y + h - 18)],
                   fill=(255, 255, 255), width=1)
        d.polygon([(x + 60, y + 6), (x + 150, y + 16), (x + 60, y + 20)],
                  fill=(90, 95, 105))
        d.polygon([(x + 150, y + 16), (x + 162, y + 12), (x + 162, y + 20)],
                  fill=(60, 62, 70))
        d.line([(x + 20, y + 10), (x + 58, y + 14)], fill=(255, 220, 120),
               width=2)
    elif kind == "iraq":
        d.rectangle([x, y, x + w, y + h], fill=(222, 200, 150))
        d.rectangle([x + 20, y + 12, x + 120, y + h - 6], fill=(96, 104, 60))
        d.rectangle([x + 120, y + 8, x + 148, y + h - 6], fill=(80, 88, 52))
        for wx in (38, 70, 102, 132):
            d.ellipse([x + wx, y + h - 8, x + wx + 10, y + h + 2], fill=(20, 20, 20))
        d.rectangle([x + 158, y + 4, x + 162, y + h - 12], fill=(120, 84, 50))
        for fx, fy in [(150, 6), (162, 2), (172, 8), (166, 12)]:
            d.ellipse([x + fx - 6, y + fy - 2, x + fx + 6, y + fy + 2],
                      fill=(60, 130, 70))
    elif kind == "italy":
        d.rectangle([x, y, x + w // 3, y + h], fill=(0, 146, 70))
        d.rectangle([x + w // 3, y, x + 2 * w // 3, y + h], fill=(255, 255, 255))
        d.rectangle([x + 2 * w // 3, y, x + w, y + h], fill=(206, 43, 55))
        f = font(SANS_B, 10)
        d.text((x + w // 3 + 4, y + h // 2 - 6), "SCIOPERO", font=f,
               fill=(20, 20, 20))
    elif kind == "japan":
        d.rectangle([x, y, x + w, y + h], fill=(245, 242, 235))
        d.ellipse([x + 10, y + 4, x + 34, y + h - 4], fill=(188, 0, 45))
        bars = [8, 12, 10, 16, 20]
        for i, bh in enumerate(bars):
            bx = x + 48 + i * 26
            d.rectangle([bx, y + h - 4 - bh, bx + 16, y + h - 4],
                        fill=(90, 95, 105))
    elif kind == "seoul":
        d.rectangle([x, y, x + w, y + h], fill=(214, 222, 230))
        d.rectangle([x + 30, y + 5, x + 110, y + 10], fill=(70, 78, 90))
        for i in range(4):
            cx = x + 40 + i * 20
            d.rectangle([cx, y + 10, cx + 6, y + h - 4], fill=(120, 128, 140))
        d.rectangle([x + 30, y + h - 6, x + 110, y + h - 2], fill=(70, 78, 90))
        d.rectangle([x + 130, y + 8, x + 170, y + 12], fill=(120, 84, 50))
        d.rectangle([x + 148, y + 12, x + 152, y + h - 6], fill=(120, 84, 50))
    elif kind == "kenya":
        d.rectangle([x, y, x + w, y + h // 2], fill=(232, 140, 60))
        d.rectangle([x, y + h // 2, x + w, y + h], fill=(120, 70, 40))
        d.ellipse([x + w - 44, y + 2, x + w - 20, y + h - 10],
                  fill=(255, 214, 120))
        d.polygon([(x + 30, y + h), (x + 60, y + 4), (x + 90, y + h)],
                  fill=(30, 28, 26))
        d.line([(x + 48, y + 10), (x + 72, y + 10)], fill=(30, 28, 26), width=2)
        d.line([(x + 42, y + 16), (x + 78, y + 16)], fill=(30, 28, 26), width=2)
    elif kind == "cricket":
        d.rectangle([x, y, x + w, y + h], fill=(64, 140, 80))
        d.rectangle([x, y + h - 8, x + w, y + h], fill=(190, 170, 120))
        d.polygon([(x + 60, y + 4), (x + 74, y + 8), (x + 130, y + h - 6),
                   (x + 116, y + h - 2)], fill=(190, 150, 100))
        d.ellipse([x + 140, y + 4, x + 152, y + 16], fill=(200, 40, 40))
        d.line([(x + 20, y + 6), (x + 40, y + 6)], fill=(255, 255, 255), width=2)
    elif kind == "taiz":
        d.rectangle([x, y, x + w, y + h], fill=(14, 20, 44))
        d.ellipse([x + w - 34, y + 3, x + w - 20, y + 17], fill=(235, 228, 200))
        for bx, bw, bh in [(8, 26, 16), (38, 20, 22), (62, 30, 14),
                           (96, 24, 20), (124, 28, 12)]:
            d.rectangle([x + bx, y + h - bh, x + bx + bw, y + h],
                        fill=(8, 12, 30))
            for wy in range(y + h - bh + 4, y + h - 2, 7):
                for wx in range(x + bx + 4, x + bx + bw - 3, 8):
                    if (wx + wy) % 3 == 0:
                        d.rectangle([wx, wy, wx + 2, wy + 3],
                                    fill=(255, 214, 120))


# ---------------------------------------------------------------- map
def draw_map(d, x, y, w, h):
    """Simplified world map with numbered pins for stories 1-13."""
    d.rectangle([x, y, x + w, y + h], fill=SEA)
    lat_top, lat_bot = 85.0, -60.0

    def proj(lon, lat):
        px = x + (lon + 180.0) / 360.0 * w
        py = y + (lat_top - lat) / (lat_top - lat_bot) * h
        return px, py

    for poly in CONTINENTS:
        pts = [proj(lon, lat) for lon, lat in poly]
        d.polygon(pts, fill=LAND, outline=LAND_LINE)
    f_num = font(SANS_B, 9)
    for num in sorted(PINS):
        lon, lat, dx, dy = PINS[num]
        px, py = proj(lon, lat)
        bx, by = px + dx, py + dy
        d.line([(px, py), (bx, by)], fill=RED, width=1)
        d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=RED)
        d.ellipse([bx - 8, by - 8, bx + 8, by + 8], fill=RED,
                  outline=(255, 255, 255))
        tw = d.textlength(str(num), font=f_num)
        d.text((bx - tw / 2, by - 6), str(num), font=f_num,
               fill=(255, 255, 255))


# ---------------------------------------------------------------- layout
def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    mx, cw = 10, W - 20  # content x, content width

    # top line
    f_top = font(SANS_B, 13)
    d.text((mx, 8), TOP_LEFT, font=f_top, fill=RED)
    f_topr = font(SANS_B, 11)
    d.text((mx + cw - d.textlength(TOP_RIGHT, font=f_topr), 9), TOP_RIGHT,
           font=f_topr, fill=INK)
    rule(d, mx, mx + cw, 26, width=2)

    # masthead + subhead
    f_mast = font(SERIF_B, 54)
    tw = d.textlength(MASTHEAD, font=f_mast)
    d.text((mx + (cw - tw) / 2, 30), MASTHEAD, font=f_mast, fill=INK)
    f_sub = font(SERIF, 15)
    tw = d.textlength(SUBHEAD, font=f_sub)
    d.text((mx + (cw - tw) / 2, 92), SUBHEAD, font=f_sub, fill=INK)
    rule(d, mx, mx + cw, 112, width=2)

    # stat strip: 6 cells
    cell_w = cw / 6
    f_num = font(SERIF_B, 22)
    f_lab = font(SANS, 10)
    d.rectangle([mx, 116, mx + 4, 156], fill=RED)
    for i, (big, lab) in enumerate(STATS):
        cx = mx + i * cell_w + (8 if i == 0 else 12)
        d.text((cx, 116), big, font=f_num, fill=INK)
        for j, line in enumerate(lab.split("\n")):
            d.text((cx, 141 + j * 11), line, font=f_lab, fill=GRAY)
        if i:
            rule(d, mx + i * cell_w, mx + i * cell_w, 118, fill=FAINT)
            d.line([(mx + i * cell_w, 118), (mx + i * cell_w, 156)],
                   fill=FAINT, width=1)

    # region bar: 7 equal segments
    seg_w = cw / 7
    f_reg = font(SANS_B, 11)
    for i, (name, count, col) in enumerate(REGIONS):
        sx = mx + i * seg_w
        d.rectangle([sx, 164, sx + seg_w - 1, 184], fill=col)
        txt = "%s %d" % (name, count)
        tw = d.textlength(txt, font=f_reg)
        d.text((sx + (seg_w - tw) / 2, 167), txt, font=f_reg,
               fill=(255, 255, 255))

    # big 3
    f_kick = font(SANS_B, 11)
    f_head = font(SERIF_B, 19)
    f_body = font(SANS, 11)
    col_w = (cw - 16) // 3
    for i, st in enumerate(BIG):
        x = int(mx + i * (col_w + 8))
        y0 = 188
        vh = 148
        if st["visual"] == "kyiv":
            draw_kyiv(d, x, y0, col_w, vh)
        elif st["visual"] == "akvan":
            draw_akvan(d, x, y0, col_w, vh)
        else:
            draw_selloff(d, x, y0, col_w, vh)
        label_box(d, x, y0, st["label"], font(SANS_B, 12))
        f_chip = font(SANS_B, 10)
        cw_chip = int(d.textlength(st["chip"], font=f_chip)) + 8
        chip_box(d, x, y0 + vh - 19, st["chip"], f_chip)
        d.text((x, y0 + 154), "%d %s" % (st["num"], st["kicker"]),
               font=f_kick, fill=RED)
        draw_wrapped(d, x, y0 + 170, st["headline"], f_head, col_w, INK, 22,
                     2, "BIG %d headline" % st["num"])
        draw_wrapped(d, x, y0 + 216, st["body"], f_body, col_w, INK, 14, 3,
                     "BIG %d body" % st["num"])
    rule(d, mx, mx + cw, 448, width=1)

    # small 10: 5 x 2
    f_slab = font(SANS_B, 10)
    f_skick = font(SANS_B, 10)
    f_shead = font(SERIF_B, 13)
    f_sbody = font(SANS, 10)
    scol_w = (cw - 32) // 5
    for i, st in enumerate(SMALL):
        col, row = i % 5, i // 5
        x = int(mx + col * (scol_w + 8))
        y0 = 452 + row * 92
        draw_icon(d, st["visual"], x, y0, scol_w, 26)
        label_box(d, x, y0, st["label"], f_slab, pad=3)
        f_chip = font(SANS_B, 9)
        cw_chip = int(d.textlength(st["chip"], font=f_chip)) + 6
        chip_box(d, x + scol_w - cw_chip, y0 + 26 - 15, st["chip"], f_chip,
                 pad=3)
        d.text((x, y0 + 28), "%d %s" % (st["num"], st["kicker"]),
               font=f_skick, fill=RED)
        draw_wrapped(d, x, y0 + 41, st["headline"], f_shead, scol_w, INK, 14,
                     2, "SMALL %d headline" % st["num"])
        draw_wrapped(d, x, y0 + 70, st["body"], f_sbody, scol_w, INK, 11, 2,
                     "SMALL %d body" % st["num"])
    rule(d, mx, mx + cw, 640, width=1)

    # bottom: map + ALSO list
    f_sec = font(SANS_B, 13)
    d.text((mx, 644), "WHERE IT HAPPENED", font=f_sec, fill=INK)
    d.text((mx + 402, 644), "ALSO ON FRIDAY 20 NOVEMBER \u2014 22 MORE STORIES",
           font=f_sec, fill=INK)
    draw_map(d, mx, 666, 392, 220)
    f_cap = font(SANS, 10)
    d.text((mx, 890), "Each number is that story on this page.",
           font=f_cap, fill=GRAY)
    # ALSO in two columns of 11 (uniform 10px text so nothing wraps)
    f_anum = font(SANS_B, 11)
    f_at = font(SANS, 10)
    for idx, (num, text) in enumerate(ALSO):
        col = idx // 11
        row = idx % 11
        ax = mx + 402 + col * 306
        ay = 666 + row * 21
        ntxt = "%d " % num
        nw = d.textlength(ntxt, font=f_anum)
        if d.textlength(text, font=f_at) > 296 - nw:
            WARNINGS.append("ALSO %d wrapped: %r" % (num, text))
        d.text((ax, ay), ntxt, font=f_anum, fill=GREEN)
        d.text((ax + nw, ay), text, font=f_at, fill=INK)

    # by the clock
    f_clock = font(SANS, 11)
    f_clockb = font(SANS_B, 11)
    cx = mx
    d.text((cx, 906), "BY THE CLOCK \u00b7 UTC", font=f_clockb, fill=INK)
    cx += d.textlength("BY THE CLOCK \u00b7 UTC  ", font=f_clockb)
    for t, what in CLOCK:
        d.text((cx, 906), t, font=f_clockb, fill=RED)
        cx += d.textlength(t + " ", font=f_clockb)
        d.text((cx, 906), what, font=f_clock, fill=INK)
        cx += d.textlength(what + "   \u00b7   ", font=f_clock)

    # date check box: red title, text flowing after it on the same line
    d.rectangle([mx, 928, mx + cw, 998], outline=RED, width=2)
    f_dc = font(SANS_B, 11)
    d.text((mx + 8, 933), "DATE CHECK", font=f_dc, fill=RED)
    tw = d.textlength("DATE CHECK  ", font=f_dc)
    draw_wrapped(d, mx + 8 + tw, 933, DATE_CHECK, font(SANS, 11),
                 cw - 16 - tw, INK, 14, 3, "DATE CHECK")

    # footer
    f_foot = font(SANS, 10)
    d.text((mx, 1003), FOOTER_L, font=f_foot, fill=GRAY)
    d.text((mx + cw - d.textlength(FOOTER_R, font=f_foot), 1003), FOOTER_R,
           font=f_foot, fill=GRAY)
    return img


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "entry.png"
    img = build()
    img.save(out, format="PNG")
    import os
    print("wrote %s %dx%d %d bytes" % (out, img.width, img.height,
                                      os.path.getsize(out)))
    for w in WARNINGS:
        print("WARNING:", w)
    print("warnings:", len(WARNINGS))


if __name__ == "__main__":
    main()
