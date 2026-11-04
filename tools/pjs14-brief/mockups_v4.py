"""PJS #14 mockups, round 4: fix the compass and the flags (user feedback).

Feedback on round 3:
  - The compass meant nothing, and it pointed the wrong way: the kit's
    kompas_01 reads T (Timur, east) at the top, U (Utara, north) on the left.
  - The flags floated: a cropped flag cluster hung in the top-right corner
    with nothing holding it.

Fixes, on the option-3 base (karaoke squirrels):
  A "Tiang bendera"  compass removed. Each flag cluster flies from a real
                     pole standing on the ground (the cloud floor) in the
                     strip beside the cover and beside the lyrics, so the
                     flags hang from something. The meaningless vertical
                     pills those strips held are gone; the poles take their
                     place.
  B "Tiang + kompas" A, plus the compass rebuilt to point correctly
                     (U up, T right, S down, B left, letters kept upright)
                     and used as a faint compass rose behind the lyrics,
                     the place Halloween's moon takes, as an "explore"
                     motif instead of a sticker in the corner.

Flags are never mirrored (a mirrored flag is a wrong flag), so each cluster
keeps its hoist side on the pole: both clusters have the hoist on the left.

Same checks as rounds 2-3: no decoration in the cover/title/lyrics zones,
white text >= 4.5:1, busy share >= the Halloween mockup.
"""

import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
_src = open(os.path.join(HERE, "mockups_v2.py"), encoding="utf-8").read()
exec(_src[: _src.index("h_edge, h_busy, h_empty = measure(HALLOWEEN)")])  # helpers only

FLAGS = r"hiasan\ilustrasi_globe_bendera\ilustrasi_globe_bendera_03_12f749e5d8.png"
POLE = (226, 232, 240, 255)
POLE_DARK = (150, 162, 180, 255)


def flag_cluster(side):
    """'L' = Australia over Korea (hoist cut at x 0 of the source),
    'R' = EU over Singapore (hoist sleeve at x 933)."""
    im = Image.open(os.path.join(A, FLAGS)).convert("RGBA")
    box = (0, 313, 604, 1019) if side == "L" else (933, 412, 1512, 982)
    c = im.crop(box)
    return c.crop(c.getchannel("A").getbbox())


def flagpole(s, x, top, bottom, flag, label):
    """A pole from the ground (bottom) to a gold ball at the top, the flag's
    hoist edge against the pole. Drawn on the foreground so the overlap
    check sees it."""
    w = 8
    lay = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(lay)
    d.rounded_rectangle((x - w / 2, top, x + w / 2, bottom), radius=3, fill=POLE)
    d.rectangle((x + 1, top + 6, x + w / 2, bottom), fill=POLE_DARK)  # shade
    d.ellipse((x - 9, top - 16, x + 9, top + 2), fill=YELLOW + (255,))
    d.ellipse((x - 5, top - 13, x - 1, top - 9), fill=(255, 245, 190, 255))
    s.fg.alpha_composite(lay)
    s.placed.append((f"{label} pole", (x - 9, top - 16, x + 9, bottom)))
    s.put(f"{label} flags", flag, x + w / 2 - 2, top + 2)


def compass_true(h):
    """kompas_01 rebuilt to point north: star kept, letters moved so
    U (Utara) is up, T (Timur) right, S (Selatan) down, B (Barat) left."""
    im = Image.open(os.path.join(A, r"hiasan\kompas\kompas_01_722c99867b.png")).convert("RGBA")
    parts = {  # source boxes found by connected components (round 4 probe)
        "T": (180, 11, 214, 57), "S": (374, 189, 402, 237),
        "U": (6, 191, 40, 238), "B": (186, 374, 216, 420),
    }
    star = (60, 71, 348, 360)
    out = Image.new("RGBA", im.size)
    out.alpha_composite(im.crop(star), star[:2])
    cx, cy = (star[0] + star[2]) / 2, (star[1] + star[3]) / 2
    r = 182
    where = {"U": (0, -1), "T": (1, 0), "S": (0, 1), "B": (-1, 0)}
    for k, (dx, dy) in where.items():
        g = im.crop(parts[k])
        out.alpha_composite(g, (round(cx + dx * r - g.width / 2), round(cy + dy * r - g.height / 2)))
    out = out.crop(out.getchannel("A").getbbox())
    return by_h(out, h)


def base(name, title):
    """Option 3's background and squirrels, without the compass, the
    floating flags or the strip pills."""
    s = Scene(name, title)
    s.back(Image.new("RGBA", (W, H), (8, 52, 140, 255)), 0, 0)
    s.back(alpha(cover(load(r"background\gradasi_biru\gradasi_biru_08_d36bf44d39.png"), W, H), 0.7), 0, 0)
    g1 = by_h(load(r"hiasan\ilustrasi_globe_bendera\ilustrasi_globe_bendera_01_3e88716fb7.png"), 460)
    s.back(grade(g1, 0.55), W - g1.width + 90, H - g1.height + 120)
    sw = by_h(load(r"hiasan\swoosh_dan_kurva\swoosh_dan_kurva_02_e873711616.png"), 520)
    s.back(alpha(sw, 0.55), -120, H - sw.height + 40)
    c = ZONES["ALBUM COVER"]
    blu = by_w(load(r"hiasan\panel_kartu\panel_kartu_01_3fbb8d92dd.png"), 540)
    s.back(alpha(blu.rotate(5, expand=True, resample=Image.BICUBIC), 0.9), c[0] - 100, c[1] + 70)
    yel = by_w(load(r"hiasan\panel_kartu\panel_kartu_06_d4798c11c9.png"), 200)
    s.back(yel.rotate(-8, expand=True, resample=Image.BICUBIC), c[0] - 100, c[1] - 50)
    s.back(skyline_strip(190, src=r"background\langit_skyline\langit_skyline_01_d939808c08.png", y0=0.42, y1=0.72), 0, H - 190)
    return s


def finish(s, compass=False):
    if compass:
        rose = compass_true(380)
        lz = ZONES["LYRICS"]
        s.back(alpha(grade(rose, 0.9), 0.55), lz[2] - rose.width + 40, lz[1] + 40)
    cloud_band(s.bg, 772)
    scrim(s.bg, 205)

    # Top band without the corner pieces: logo, zooming pills, notes.
    logo = by_h(load(r"logo\pjs_perayaan_jelajah_studi\pjs_perayaan_jelajah_studi_07_0e16274837.png"), 80)
    s.put("PJS logo", logo, (W - logo.width) / 2, 5)
    for i, (n, w, x, y) in enumerate([(1, 120, 240, 20), (36, 84, 370, 58), (5, 110, 870, 16), (33, 78, 1010, 56)]):
        s.put(f"zoom pill {i + 1}", pill(n, w), x, y)
    for i, (shape, col, h, x, y) in enumerate([("a", "yellow", 40, 500, 26), ("b", "white", 30, 575, 58),
                                               ("b", "yellow", 36, 1150, 30)]):
        s.put(f"top note {i + 1}", by_h(note(shape, col), h, px=True), x, y)

    # Flagpoles stand on the cloud floor (y 800 is under it) in the two
    # side strips; the flags fly in the free band above the cover / beside
    # the lyrics. Right flag runs off the window edge, like a flag in wind.
    lf = by_h(flag_cluster("L"), 112)
    flagpole(s, 22, 12, 800, lf, "left")
    rf = by_h(flag_cluster("R"), 104)
    flagpole(s, ZONES["LYRICS"][2] + MARGIN + 10, 22, 800, rf, "right")

    kar = by_w(sprite(1), GAP_R - GAP_L - 2, px=True)
    s.put("karaoke squirrels", kar, GAP_L + 1, H - kar.height - 4)
    girl = by_w(sprite(10), LEFT_R - 6, px=True)
    s.put("squirrel waving", girl, 3, H - girl.height - 4)
    s.rising_pins(H - kar.height - 4, n=6)
    # Clouds hide the pole feet, so the poles read as planted.
    lay = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(lay)
    for cx, r in [(22, 30), (ZONES["LYRICS"][2] + MARGIN + 10, 30)]:
        d.ellipse((cx - r * 2.2, 776, cx + r * 2.2, 776 + r * 2), fill=(232, 244, 255, 235))
    s.fg.alpha_composite(lay.filter(ImageFilter.GaussianBlur(6)))
    return s


def opt_a():
    return finish(base("4a_tiang", "4A Tiang bendera (no compass)"))


def opt_b():
    return finish(base("4b_tiang_kompas", "4B Tiang + true compass rose"), compass=True)


if __name__ == "__main__":
    h_edge, h_busy, h_empty = measure(HALLOWEEN)
    print(f"Halloween reference: busy {h_busy:.1f}%")
    results, bad = [], False
    for build in (opt_a, opt_b):
        s = build()
        fails, rep = check(s)
        img = render(s)
        path = os.path.join(OUT, f"mockup4_{s.name}.png")
        img.convert("RGB").save(path)
        _, busy, empty = measure(path)
        if busy < h_busy:
            fails.append(f"fullness: busy {busy:.1f}% < Halloween {h_busy:.1f}%")
        results.append((s, img))
        bad |= bool(fails)
        print(f"{s.name:16} {len(s.placed):2} decorations | busy {busy:4.1f}% | {' | '.join(rep)}{' | OK' if not fails else ''}")
        for f in fails:
            print("   FAIL", f)
    # Before / after sheet: round-3 option 3 next to 4A and 4B.
    before = Image.open(os.path.join(OUT, "mockup2_3_karaoke.png")).convert("RGB")
    tiles = [("Round 3 (before)", before)] + [(s.title, i.convert("RGB")) for s, i in results]
    sheet = Image.new("RGB", (720 * 3 + 40, 405 + 50), (24, 28, 40))
    sd = ImageDraw.Draw(sheet)
    for i, (t, im) in enumerate(tiles):
        sheet.paste(im.resize((720, 405), Image.LANCZOS), (10 + i * 730, 44))
        sd.text((14 + i * 730, 8), t, font=TAG, fill="white")
    sheet.save(os.path.join(OUT, "mockups4_compare.png"))
    # Compass proof: the kit's compass vs the rebuilt one.
    k = by_h(Image.open(os.path.join(A, r"hiasan\kompas\kompas_01_722c99867b.png")).convert("RGBA"), 200)
    t = compass_true(200)
    pr = Image.new("RGBA", (max(k.width, 300) + max(t.width, 300) + 60, 250), (14, 97, 207, 255))
    pr.alpha_composite(k, (20, 40))
    pr.alpha_composite(t, (max(k.width, 300) + 40, 40))
    pd = ImageDraw.Draw(pr)
    pd.text((20, 8), "kit: T (east) up, wrong", font=BOLD, fill="white")
    pd.text((max(k.width, 300) + 40, 8), "rebuilt: U (north) up", font=BOLD, fill="white")
    pr.convert("RGB").save(os.path.join(OUT, "compass_fix.png"))
    sys.exit(1 if bad else 0)
