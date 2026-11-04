"""PJS #14 option 4A, animated preview (MP4 + GIF) before building it into
the theme.

Motion, one 14.4 s loop (every period divides 14.4 so the loop is seamless):
  flags            wave from the pole outward, 1.8 s (hoist edge stays put)
  karaoke squirrels bounce + squash like singing, 0.9 s     (Halloween strum)
  waving squirrel  sway about her feet, 4.8 s               (Halloween sway)
  music notes      rise from the karaoke pair and fade, 7.2 s, 6 staggered
                   (Halloween Hlw__Rise keyframes, same timing)
  top capsules     drift sideways like clouds, 14.4 / 7.2 s (Halloween bats)
  top notes        bob, 3.6 s
  paper plane      the "big moment": crosses the top band right to left
                   once per loop, behind the logo, dotted trail
                   (Halloween zombie walk; the kit has no plane, so it is
                   drawn here as pixel art in the notes' style)
  lyrics           active line steps every 2.88 s, only to make the
                   preview read like a playing song

Checks on every frame: no animated item enters the cover / title / lyrics
zones; white-text contrast >= 4.5:1 on sampled frames; the loop is seamless
(frame 0 == frame at 14.4 s).

Outputs (tools/pjs14-brief/): preview_4a.mp4 (1440x810, 25 fps),
preview_4a.gif (720x405, 12.5 fps), preview_4a_frames.png (contact strip).
"""

import math
import os
import runpy
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
g = runpy.run_path(os.path.join(HERE, "mockups_v4.py"), run_name="v4")
W, H, ZONES, MARGIN = g["W"], g["H"], g["ZONES"], g["MARGIN"]
GAP_L, GAP_R, LEFT_R = g["GAP_L"], g["GAP_R"], g["LEFT_R"]
by_h, by_w, sprite, note, pill, load = g["by_h"], g["by_w"], g["sprite"], g["note"], g["pill"], g["load"]
YELLOW, DEEP = g["YELLOW"], g["DEEP"]
BOLD, BIG, LYR = g["BOLD"], g["BIG"], g["LYR"]

LOOP, FPS = 14.4, 25
N = round(LOOP * FPS)
TAU = 2 * math.pi

# ─────────────────────────────────────────────── static layers
s = g["base"]("4a_anim", "4A animated")
g["cloud_band"](s.bg, 772)
g["scrim"](s.bg, 205)
bottom = s.bg.copy()

POLES = [(22, 12), (ZONES["LYRICS"][2] + MARGIN + 10, 22)]
pd = ImageDraw.Draw(bottom)
for x, top in POLES:
    pd.rounded_rectangle((x - 4, top, x + 4, 800), radius=3, fill=g["POLE"])
    pd.rectangle((x + 1, top + 6, x + 4, 800), fill=g["POLE_DARK"])
    pd.ellipse((x - 9, top - 16, x + 9, top + 2), fill=YELLOW + (255,))
    pd.ellipse((x - 5, top - 13, x - 1, top - 9), fill=(255, 245, 190, 255))

top_layer = Image.new("RGBA", (W, H))  # above the animation, below the UI
logo = by_h(load(r"logo\pjs_perayaan_jelajah_studi\pjs_perayaan_jelajah_studi_07_0e16274837.png"), 80)
LOGO_BOX = ((W - logo.width) // 2, 5)
top_layer.alpha_composite(logo, LOGO_BOX)
feet = Image.new("RGBA", (W, H))
fd = ImageDraw.Draw(feet)
for cx, _ in POLES:
    fd.ellipse((cx - 66, 776, cx + 66, 836), fill=(232, 244, 255, 235))
top_layer.alpha_composite(feet.filter(ImageFilter.GaussianBlur(6)))


def ui_layer(active):
    """The player UI from mockups_v2.render, on a transparent layer, with
    the given lyric line highlighted."""
    lay = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(lay, "RGBA")
    c = ZONES["ALBUM COVER"]
    d.rounded_rectangle(c, radius=16, fill=(6, 30, 80, 255), outline=(255, 255, 255, 70), width=2)
    d.text(((c[0] + c[2]) / 2, (c[1] + c[3]) / 2), "ALBUM COVER", font=BOLD, fill="white", anchor="mm")
    t = ZONES["TITLE / ARTIST / CONTROLS"]
    cx = (t[0] + t[2]) / 2
    d.text((cx, t[1] + 28), "Song Title", font=BIG, fill="white", anchor="mm")
    d.text((cx, t[1] + 64), "Artist Name", font=BOLD, fill=(255, 255, 255, 175), anchor="mm")
    d.rounded_rectangle((t[0] + 50, t[1] + 92, t[2] - 50, t[1] + 98), radius=3, fill=(255, 255, 255, 70))
    d.rounded_rectangle((t[0] + 50, t[1] + 92, t[0] + 120 + active * 50, t[1] + 98), radius=3, fill=YELLOW + (255,))
    by = t[1] + 124
    for sx, sg in ((cx - 70, -1), (cx + 70, 1)):
        d.polygon([(sx - 9 * sg, by - 10), (sx - 9 * sg, by + 10), (sx + 7 * sg, by)], fill="white")
        d.rectangle((sx + 8 * sg - 2, by - 10, sx + 8 * sg + 2, by + 10), fill="white")
    d.ellipse((cx - 22, by - 22, cx + 22, by + 22), fill="white")
    d.rectangle((cx - 8, by - 9, cx - 3, by + 9), fill=DEEP + (255,))
    d.rectangle((cx + 3, by - 9, cx + 8, by + 9), fill=DEEP + (255,))
    lz = ZONES["LYRICS"]
    lines = ["Young vision, global mission", "every road leads somewhere new", "from Jogja to the world",
             "pack your dreams and go", "the map is yours to draw"]
    for i, txt in enumerate(lines):
        a = 255 if i == active else (130 if i < active else 85)
        d.text((lz[0] + 16, lz[1] + 70 + i * 118), txt, font=LYR, fill=(255, 255, 255, a))
    return lay


UI = [ui_layer(i) for i in range(5)]

# ─────────────────────────────────────────────── animated items
FLAGS = [(by_h(g["flag_cluster"]("L"), 112), POLES[0]), (by_h(g["flag_cluster"]("R"), 104), POLES[1])]
KAR = by_w(sprite(1), GAP_R - GAP_L - 2, px=True)
GIRL = by_w(sprite(10), LEFT_R - 6, px=True)
PILLS = [(pill(n, w), x, y, amp, per, ph) for n, w, x, y, amp, per, ph in
         [(1, 120, 240, 20, 18, 14.4, 0.0), (36, 84, 370, 58, 14, 7.2, 1.3),
          (5, 110, 870, 16, 18, 14.4, 2.1), (33, 78, 1010, 56, 14, 7.2, 0.4)]]
TOPNOTES = [(by_h(note(sh, col), h, px=True), x, y, ph) for sh, col, h, x, y, ph in
            [("a", "yellow", 40, 500, 26, 0.0), ("b", "white", 30, 575, 58, 1.7), ("b", "yellow", 36, 1150, 30, 0.9)]]
SEQ = [("a", "white"), ("b", "yellow"), ("a", "sky"), ("b", "white"), ("a", "yellow"), ("b", "sky")]
RISE = [by_h(note(sh, col), 46, px=True) for sh, col in SEQ]

PLANE_ART = [
    "...............###",
    "............###WW#",
    ".........###WWWW#.",
    "......###WWWWWW#..",
    "...###WWWWWWWW#...",
    "###WWWWWWWWWW#....",
    "...###SSSSSWW#....",
    "......###SSSSW#...",
    ".........###SSS#..",
    "............###S#.",
    "...............###",
]
PAL = {"#": DEEP + (255,), "W": (255, 255, 255, 255), "S": (178, 214, 245, 255)}
_p = Image.new("RGBA", (len(PLANE_ART[0]), len(PLANE_ART)))
for y, row in enumerate(PLANE_ART):
    for x, ch in enumerate(row):
        if ch in PAL:
            _p.putpixel((x, y), PAL[ch])
PLANE = _p.resize((_p.width * 4, _p.height * 4), Image.NEAREST)
PLANE_T0, PLANE_DUR = 5.0, 6.5


def wave(img, t):
    """Flag wave travelling away from the hoist (x = 0); the hoist column
    never moves, amplitude grows toward the fly end."""
    a = np.asarray(img)
    h, w = a.shape[:2]
    amp, lam = 4.0, 62.0
    pad = int(amp) + 2
    src = np.zeros((h + 2 * pad, w, 4), np.uint8)
    src[pad:pad + h] = a
    xs = np.arange(w, dtype=np.float32)
    k = xs / w
    arg = TAU * xs / lam - TAU * t / 1.8
    dy = (amp * k * np.sin(arg)).astype(np.float32)
    map_x = np.tile(xs, (h + 2 * pad, 1))
    map_y = (np.arange(h + 2 * pad, dtype=np.float32)[:, None] - dy[None, :])
    out = cv2.remap(src, map_x, map_y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    shade = (1 + 0.14 * k * np.cos(arg))[None, :, None]
    out[..., :3] = np.clip(out[..., :3] * shade, 0, 255).astype(np.uint8)
    return Image.fromarray(out, "RGBA"), pad


def lerp_keys(p, keys):
    for (p0, v0), (p1, v1) in zip(keys, keys[1:]):
        if p0 <= p <= p1:
            f = (p - p0) / (p1 - p0) if p1 > p0 else 0
            return v0 + (v1 - v0) * f
    return keys[-1][1]


def frame(t):
    """Returns (scene without UI, list of (label, bbox) of animated items)."""
    im = bottom.copy()
    boxes = []

    def put(label, sp, x, y):
        x, y = round(x), round(y)
        boxes.append((label, (x, y, x + sp.width, y + sp.height)))
        if x >= W or y >= H or x + sp.width <= 0 or y + sp.height <= 0:
            return  # fully off screen
        im.alpha_composite(sp, (max(0, x), max(0, y)), (max(0, -x), max(0, -y)))

    for i, (sp, x, y, amp, per, ph) in enumerate(PILLS):
        put(f"pill {i + 1}", sp, x + amp * math.sin(TAU * t / per + ph), y)
    for i, (sp, x, y, ph) in enumerate(TOPNOTES):
        put(f"top note {i + 1}", sp, x, y + 4 * math.sin(TAU * t / 3.6 + ph))
    for i, (fl, (px, top)) in enumerate(FLAGS):
        wv, pad = wave(fl, t + i * 0.45)
        put(f"flag {i + 1}", wv, px + 2, top + 2 - pad)

    # Waving girl: sway about her feet (rotate a padded copy, pivot bottom-centre).
    ang = -1.4 * (0.5 - 0.5 * math.cos(TAU * t / 4.8))
    pad = 8
    gp = Image.new("RGBA", (GIRL.width + 2 * pad, GIRL.height + 2 * pad))
    gp.alpha_composite(GIRL, (pad, pad))
    gr = gp.rotate(ang, resample=Image.NEAREST, center=(gp.width / 2, pad + GIRL.height))
    gr = gr.crop(gr.getchannel("A").getbbox())
    put("squirrel waving", gr, 3 + (GIRL.width - gr.width) / 2, H - 4 - gr.height)

    # Karaoke pair: bounce + squash, feet stay on the floor.
    b = abs(math.sin(TAU * t / 1.8))  # two bounces per 1.8 s = 0.9 s each
    kh = round(KAR.height * (1 + 0.035 * b))
    kw = round(KAR.width * (1 - 0.012 * b))
    kar = KAR.resize((kw, kh), Image.NEAREST)
    put("karaoke squirrels", kar, GAP_L + 1 + (KAR.width - kw) / 2, H - 4 - kh - round(3 * b))

    # Rising notes: Halloween's Hlw__Rise keyframes and timing.
    gap = GAP_R - GAP_L
    start_y = H - 4 - KAR.height - 30
    for i, sp in enumerate(RISE):
        p = ((t + i * 1.2) % 7.2) / 7.2
        dx = lerp_keys(p, [(0, -0.18), (0.5, 0.18), (1, -0.12)]) * gap
        dy = lerp_keys(p, [(0, 0), (0.5, -0.26), (1, -0.52)]) * H * 0.82
        rot = lerp_keys(p, [(0, -8), (0.5, 8), (1, -6)])
        sc = lerp_keys(p, [(0, 1), (0.5, 0.85), (1, 0.7)])
        op = lerp_keys(p, [(0, 0), (0.12, 1), (0.85, 0.5), (1, 0)])
        n = sp.resize((max(1, round(sp.width * sc)), max(1, round(sp.height * sc))), Image.NEAREST)
        n = n.rotate(-rot, expand=True, resample=Image.NEAREST)
        n.putalpha(n.getchannel("A").point(lambda v, o=op: round(v * o)))
        put(f"rising note {i + 1}", n, (GAP_L + GAP_R) / 2 + dx - n.width / 2, start_y + dy - n.height / 2)

    # Paper plane, right to left across the top band, with a dotted trail.
    def plane_at(tt):
        q = (tt - PLANE_T0) / PLANE_DUR
        return W + 40 - q * (W + 40 + PLANE.width + 40), 30 + 10 * math.sin(TAU * q * 1.5)

    if PLANE_T0 <= t <= PLANE_T0 + PLANE_DUR:
        trail = Image.new("RGBA", (W, H))
        td = ImageDraw.Draw(trail)
        for k in range(1, 16):
            tt = t - k * 0.06
            if tt < PLANE_T0:
                break
            x, y = plane_at(tt)
            if k % 2 == 0:
                a = round(200 * (1 - k / 16))
                td.rectangle((x + PLANE.width - 4, y + PLANE.height / 2 - 2, x + PLANE.width, y + PLANE.height / 2 + 2),
                             fill=(255, 255, 255, a))
        im.alpha_composite(trail)
        x, y = plane_at(t)
        put("paper plane", PLANE, x, y)

    im.alpha_composite(top_layer)
    return im, boxes


# ─────────────────────────────────────────────── render + checks
def zone_hits(boxes):
    out = []
    for label, b in boxes:
        for zn, z in ZONES.items():
            gz = (z[0] - MARGIN, z[1] - MARGIN, z[2] + MARGIN, z[3] + MARGIN)
            if b[0] < gz[2] and gz[0] < b[2] and b[1] < gz[3] and gz[1] < b[3]:
                out.append(f"{label} touches {zn} {b}")
    return out


def worst_contrast(arr):
    res = {}
    for zn in ("LYRICS", "TITLE / ARTIST / CONTROLS"):
        x0, y0, x1, y1 = ZONES[zn]
        worst = 99.0
        for ty in range(y0, y1, 48):
            for tx in range(x0, x1, 48):
                lum = g["rel_lum"](arr[ty:min(ty + 48, y1), tx:min(tx + 48, x1)])
                worst = min(worst, 1.05 / (float(np.percentile(lum, 98)) + 0.05))
        res[zn.split()[0].lower()] = worst
    return res


mp4 = os.path.join(HERE, "preview_4a.mp4")
vw = None
for cc in ("mp4v", "avc1"):  # mp4v first: this OpenCV has no OpenH264 dll
    vw = cv2.VideoWriter(mp4, cv2.VideoWriter_fourcc(*cc), FPS, (W, H))
    if vw.isOpened():
        codec = cc
        break
gif_frames, strip, fails, min_c = [], [], [], {"lyrics": 99.0, "title": 99.0}
first = None
for f in range(N + 1):  # frame N is t = LOOP, used only for the seam check
    t = f / FPS
    scene, boxes = frame(t)
    if f == N:
        seam = np.abs(np.asarray(scene, np.int16) - first).max()
        break
    if f == 0:
        first = np.asarray(scene, np.int16)
    for h in zone_hits(boxes):
        fails.append(f"t={t:.2f}s {h}")
    if f % 5 == 0:
        c = worst_contrast(np.asarray(scene.convert("RGB")).astype(np.float64))
        for k in c:
            min_c[k] = min(min_c[k], c[k])
    full = Image.alpha_composite(scene, UI[int(t / 2.88) % 5]).convert("RGB")
    vw.write(cv2.cvtColor(np.asarray(full), cv2.COLOR_RGB2BGR))
    if f % 2 == 0:
        gif_frames.append(full.resize((720, 405), Image.LANCZOS))
    if f in (0, 50, 140, 175, 210, 300):
        strip.append((t, full))
vw.release()

pal = gif_frames[len(gif_frames) // 2].quantize(255, method=Image.MEDIANCUT)
q = [fr.quantize(palette=pal) for fr in gif_frames]
gif = os.path.join(HERE, "preview_4a.gif")
q[0].save(gif, save_all=True, append_images=q[1:], duration=80, loop=0, optimize=True)

sheet = Image.new("RGB", (3 * 730 + 10, 2 * 440 + 10), (24, 28, 40))
sd = ImageDraw.Draw(sheet)
for i, (t, im) in enumerate(strip):
    x, y = 10 + (i % 3) * 730, 10 + (i // 3) * 440
    sheet.paste(im.resize((720, 405), Image.LANCZOS), (x, y + 30))
    sd.text((x, y), f"t = {t:.1f} s", font=BOLD, fill="white")
sheet.save(os.path.join(HERE, "preview_4a_frames.png"))

cap = cv2.VideoCapture(mp4)
n_read = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
ok_read, _ = cap.read()
cap.release()

print(f"frames {N} @ {FPS} fps = {LOOP} s loop | codec {codec} | mp4 readable {ok_read} ({n_read} frames) "
      f"{os.path.getsize(mp4) / 1e6:.1f} MB | gif {len(q)} frames {os.path.getsize(gif) / 1e6:.1f} MB")
print(f"zone overlaps: {len(fails)} | worst contrast lyrics {min_c['lyrics']:.1f}:1 title {min_c['title']:.1f}:1 "
      f"| loop seam max diff {seam}")
for x in fails[:10]:
    print("  FAIL", x)
bad = fails or min(min_c.values()) < 4.5 or seam > 2 or not ok_read or n_read != N
print("ALL PASS" if not bad else "SOME CHECKS FAILED")
sys.exit(1 if bad else 0)
