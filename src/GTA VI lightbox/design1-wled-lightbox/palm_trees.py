#!/usr/bin/env python3
"""
Parametric full palm trees as 2D polygons (pure standard library).

Shared by lightbox_freecad.py (extrudes + fuses into relief layers) and
preview.py (draws the front elevation), so the model and the preview can
never disagree. Units: millimeters, Y up, origin at enclosure center.

Each tree layer is a skeleton: a perimeter frame plus full trees whose
trunks start ON the frame bars. Nothing floats, so every layer laser-cuts
from a single sheet with zero loose pieces and zero bridges.
"""

import math

# Layer frame: 12mm perimeter bars inside a 408 x 248 inner area.
FRAME_OUTER_W = 408.0
FRAME_OUTER_H = 248.0
FRAME_BAR = 12.0

# (angle_deg, length, droop, width): 90 = straight up, 270 = straight down.
# Droop pulls the frond tip downward for the classic arching read.


def _bez(p0, p1, p2, t):
    u = 1.0 - t
    return (u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0],
            u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1])


def _strip(p0, p1, p2, w0, w1, segs):
    """Tapered ribbon along a quadratic bezier spine. Returns a polygon."""
    spine = [_bez(p0, p1, p2, i / segs) for i in range(segs + 1)]
    left, right = [], []
    for i, (x, y) in enumerate(spine):
        t = i / segs
        xa, ya = spine[max(i - 1, 0)]
        xb, yb = spine[min(i + 1, segs)]
        dx, dy = xb - xa, yb - ya
        leng = (dx * dx + dy * dy) ** 0.5 or 1.0
        nx, ny = -dy / leng, dx / leng
        hw = (w0 + (w1 - w0) * t) / 2.0
        left.append((x + nx * hw, y + ny * hw))
        right.append((x - nx * hw, y - ny * hw))
    return [[round(px, 3), round(py, 3)] for px, py in left + right[::-1]]


def trunk_poly(base, crown, bow, w0, w1, segs=6):
    """Curved tapered trunk from base point to crown point."""
    mx, my = (base[0] + crown[0]) / 2.0, (base[1] + crown[1]) / 2.0
    dx, dy = crown[0] - base[0], crown[1] - base[1]
    leng = (dx * dx + dy * dy) ** 0.5 or 1.0
    ctrl = (mx - dy / leng * bow, my + dx / leng * bow)
    return _strip(base, ctrl, crown, w0, w1, segs)


def frond_poly(crown, angle_deg, length, droop, width, segs=8):
    """Single arching frond spraying from the crown."""
    a = math.radians(angle_deg)
    dx, dy = math.cos(a), math.sin(a)
    tip = (crown[0] + dx * length, crown[1] + dy * length - droop)
    ctrl = (crown[0] + dx * length * 0.55,
            crown[1] + dy * length * 0.55 - droop * 0.12)
    return _strip(crown, ctrl, tip, width, 0.9, segs)


def nut_poly(cx, cy, r=3.0, segs=10):
    """Coconut circle. Place overlapping the crown so it fuses."""
    return [[round(cx + r * math.cos(2 * math.pi * i / segs), 3),
             round(cy + r * math.sin(2 * math.pi * i / segs), 3)]
            for i in range(segs)]


def _cubic(p0, p1, p2, p3, t):
    u = 1.0 - t
    return (u * u * u * p0[0] + 3 * u * u * t * p1[0]
            + 3 * u * t * t * p2[0] + t * t * t * p3[0],
            u * u * u * p0[1] + 3 * u * u * t * p1[1]
            + 3 * u * t * t * p2[1] + t * t * t * p3[1])


def _ribbon(spine, width_at):
    """Variable-width ribbon polygon around a spine polyline."""
    left, right = [], []
    n = len(spine) - 1
    for i, (x, y) in enumerate(spine):
        t = i / n if n else 0.0
        xa, ya = spine[max(i - 1, 0)]
        xb, yb = spine[min(i + 1, n)]
        dx, dy = xb - xa, yb - ya
        leng = (dx * dx + dy * dy) ** 0.5 or 1.0
        hw = width_at(t) / 2.0
        left.append((x - dy / leng * hw, y + dx / leng * hw))
        right.append((x + dy / leng * hw, y - dx / leng * hw))
    return [[round(px, 3), round(py, 3)] for px, py in left + right[::-1]]


def frond_organic(crown, angle_deg, length, rise, droop, width, segs=12):
    """
    Arching palm frond: rises off the crown, arcs over, and falls to a
    fine tip. Lanceolate width (swells past the base, pinches at the tip)
    instead of a straight triangle taper.
    """
    a = math.radians(angle_deg)
    dx, dy = math.cos(a), math.sin(a)
    p0 = tuple(crown)
    p3 = (crown[0] + dx * length, crown[1] + dy * length - droop)
    p1 = (crown[0] + dx * length * 0.35,
          crown[1] + dy * length * 0.35 + rise)
    p2 = (p3[0] - dx * length * 0.30, p3[1] + rise * 0.25)
    spine = [_cubic(p0, p1, p2, p3, i / segs) for i in range(segs + 1)]

    def profile(t):
        return max(width * math.sin(math.pi * (0.12 + 0.88 * t)) ** 0.7, 0.5)

    return _ribbon(spine, profile)


def trunk_organic(base, crown, bow1, bow2, w0, w1, segs=8):
    """S-curving tapered trunk from base point to crown point."""
    dx, dy = crown[0] - base[0], crown[1] - base[1]
    leng = (dx * dx + dy * dy) ** 0.5 or 1.0
    nx, ny = -dy / leng, dx / leng
    p0 = tuple(base)
    p3 = tuple(crown)
    p1 = (base[0] + dx * 0.33 + nx * bow1,
          base[1] + dy * 0.33 + ny * bow1)
    p2 = (base[0] + dx * 0.66 + nx * bow2,
          base[1] + dy * 0.66 + ny * bow2)
    spine = [_cubic(p0, p1, p2, p3, i / segs) for i in range(segs + 1)]
    return _ribbon(spine, lambda t: w0 + (w1 - w0) * t)


def palm_organic(base, crown, bow1=8.0, bow2=-4.0, trunk_w=(11.0, 6.0),
                 fan=None, nuts=True):
    """Full organic palm: S-curved trunk plus arching frond crown."""
    polys = [trunk_organic(tuple(base), tuple(crown), bow1, bow2,
                           trunk_w[0], trunk_w[1])]
    for angle, length, rise, droop, width in (fan or []):
        polys.append(frond_organic(tuple(crown), angle, length,
                                   rise, droop, width))
    if nuts:
        polys.append(nut_poly(crown[0] - 4.5, crown[1] - 3.5, r=3.5))
        polys.append(nut_poly(crown[0] + 5.0, crown[1] - 2.5, r=3.5))
    return polys


def palm_tree(base, crown, bow=8.0, trunk_w=(10.0, 6.0), fan=None, nuts=True):
    """
    Full palm tree: trunk + frond crown + coconuts.
    Returns a list of polygons; all overlap at the crown for fusing.
    """
    polys = [trunk_poly(tuple(base), tuple(crown), bow, trunk_w[0], trunk_w[1])]
    fan = fan if fan is not None else [
        (172, 46, 20, 7.0), (150, 52, 16, 8.0), (128, 59, 11, 8.5),
        (105, 63, 9, 8.5), (90, 65, 8, 8.5), (72, 62, 10, 8.5),
        (50, 57, 14, 8.0), (28, 50, 20, 7.5), (5, 44, 26, 7.0),
    ]
    for angle, length, droop, width in fan:
        polys.append(frond_poly(tuple(crown), angle, length, droop, width))
    if nuts:
        polys.append(nut_poly(crown[0] - 4.0, crown[1] - 3.0))
        polys.append(nut_poly(crown[0] + 4.5, crown[1] - 2.0))
    return polys


def frame_bars(w=408.0, h=248.0):
    """Four (x0, y0, x1, y1) perimeter bars for an outer w x h frame."""
    hw, hh, b = w / 2.0, h / 2.0, FRAME_BAR
    return [
        (-hw, hh - b, hw, hh),      # top
        (-hw, -hh, hw, -hh + b),    # bottom
        (-hw, -hh + b, -hw + b, hh - b),  # left
        (hw - b, -hh + b, hw, hh - b),    # right
    ]


# ----------------------------------------------------------------------------
# LAYER COMPOSITION (tuned against the VI window: x -119..119, y -90..90)
# Trunk bases sit ON frame bars; crowns + fronds reach into the aperture.
# ----------------------------------------------------------------------------

DOWN_FAN = [
    (255, 54, 32, 8.0), (270, 62, 36, 8.5), (285, 54, 32, 8.0),
    (238, 48, 28, 7.5), (302, 48, 28, 7.5), (222, 42, 26, 7.0),
    (318, 42, 26, 7.0), (205, 36, 24, 6.5), (335, 36, 24, 6.5),
]

DOWN_FAN_V2 = [
    (255, 54, 32, 8.0), (262, 60, 36, 8.5), (270, 64, 38, 8.5),
    (278, 60, 36, 8.5), (285, 54, 32, 8.0), (240, 48, 30, 7.5),
    (300, 48, 30, 7.5), (225, 42, 28, 7.0), (315, 42, 28, 7.0),
]

# ----------------------------------------------------------------------------
# STYLE LAYOUTS (tuned against the VI window: x -119..119, y -90..90)
# Trunk bases sit ON frame bars; crowns + fronds reach into the aperture.
# ----------------------------------------------------------------------------

# v3: original 9-frond fans (kept for comparison).
_TREES_FANS = [
    dict(base=(-70, -138), crown=(-52, 2), bow=10.0),
    dict(base=(88, -138), crown=(86, 6), bow=-4.0),
    dict(base=(-30, 138), crown=(-30, 100), bow=0.0,
         trunk_w=(9.0, 6.5), fan=DOWN_FAN),
    dict(base=(-120, -138), crown=(-78, 32), bow=8.0),
    dict(base=(135, -138), crown=(108, -40), bow=-10.0, fan=[
        (172, 46, 20, 7.0), (150, 52, 16, 8.0), (128, 59, 11, 8.5),
        (105, 63, 9, 8.5), (90, 65, 8, 8.5), (72, 62, 10, 8.5),
        (50, 48, 14, 8.0), (28, 38, 20, 7.5), (5, 32, 26, 7.0),
    ]),
]

# v2: reference-inspired. Big dominant crowns, long arching fronds with
# layered skirts, like the example artwork.
_TREES_REF = [
    dict(base=(-100, -138), crown=(-72, 8), bow=12.0,
         trunk_w=(11.0, 6.5), fan=[
             (185, 55, 26, 8.5), (165, 62, 20, 9.0), (145, 72, 14, 9.5),
             (125, 80, 10, 9.5), (105, 86, 8, 10.0), (90, 88, 8, 10.0),
             (72, 86, 10, 9.5), (52, 80, 14, 9.5), (32, 72, 20, 9.0),
             (12, 62, 26, 8.5), (-5, 52, 30, 8.0),
             (-25, 40, 34, 7.5), (-40, 32, 34, 7.0),
         ]),
    dict(base=(88, -138), crown=(86, 12), bow=-4.0,
         trunk_w=(11.0, 6.5), fan=[
             (200, 48, 24, 7.5), (175, 58, 22, 8.5), (155, 66, 16, 9.0),
             (135, 74, 12, 9.5), (115, 80, 9, 9.5), (95, 82, 8, 10.0),
             (75, 80, 10, 9.5), (55, 74, 14, 9.5), (35, 66, 20, 9.0),
             (15, 58, 26, 8.5), (0, 50, 30, 8.0), (-20, 40, 32, 7.5),
         ]),
    dict(base=(-30, 138), crown=(-30, 98), bow=0.0,
         trunk_w=(9.0, 6.5), fan=DOWN_FAN_V2),
    dict(base=(135, -138), crown=(104, -56), bow=-8.0,
         trunk_w=(10.0, 6.0), fan=[
             (160, 40, 14, 7.5), (135, 48, 10, 8.0), (110, 52, 8, 8.5),
             (90, 54, 8, 8.5), (68, 52, 10, 8.0), (45, 44, 14, 7.5),
             (20, 34, 20, 7.0), (0, 28, 24, 6.5),
         ]),
]

# v4: bold graphic. Few wide fronds, high contrast, fastest laser cut.
_TREES_BOLD = [
    dict(base=(-100, -138), crown=(-72, 8), bow=12.0,
         trunk_w=(12.0, 7.0), fan=[
             (165, 58, 18, 11.0), (130, 72, 12, 12.0), (95, 78, 10, 12.0),
             (60, 72, 14, 12.0), (25, 60, 22, 11.0), (-10, 48, 28, 10.0),
         ]),
    dict(base=(88, -138), crown=(86, 12), bow=-4.0,
         trunk_w=(12.0, 7.0), fan=[
             (195, 52, 22, 11.0), (160, 62, 16, 11.5), (125, 72, 12, 12.0),
             (90, 76, 10, 12.0), (55, 68, 14, 12.0), (20, 56, 22, 11.0),
         ]),
    dict(base=(-30, 138), crown=(-30, 98), bow=0.0,
         trunk_w=(10.0, 7.0), fan=[
             (245, 50, 32, 10.0), (265, 58, 36, 11.0), (280, 58, 36, 11.0),
             (300, 50, 32, 10.5), (225, 42, 28, 10.0), (315, 42, 28, 10.0),
         ]),
    dict(base=(135, -138), crown=(104, -56), bow=-8.0,
         trunk_w=(11.0, 6.5), fan=[
             (150, 44, 14, 10.0), (115, 50, 10, 11.0), (90, 52, 9, 11.5),
             (65, 50, 11, 11.0), (35, 44, 16, 10.5), (5, 36, 22, 10.0),
         ]),
]

# v1: organic. Cubic-arching fronds with lanceolate width profiles,
# asymmetric clustered crowns, S-curved trunks. Closest to the artwork.
_TREES_ORGANIC = [
    dict(base=(-100, -138), crown=(-72, 8), bow1=14.0, bow2=-6.0,
         trunk_w=(11.5, 6.5), organic=True, fan=[
             (172, 50, 10, 20, 8.5), (152, 64, 14, 14, 9.5),
             (132, 76, 18, 10, 10.0), (112, 84, 20, 8, 10.5),
             (94, 88, 22, 8, 10.5), (76, 86, 20, 10, 10.0),
             (56, 80, 14, 14, 9.5), (38, 72, 8, 20, 9.0),
             (20, 62, 4, 26, 8.5), (4, 52, 0, 30, 8.0),
             (-14, 42, -4, 32, 7.5), (-30, 34, -6, 32, 7.0),
         ]),
    dict(base=(88, -138), crown=(86, 12), bow1=-5.0, bow2=3.0,
         trunk_w=(11.5, 6.5), organic=True, fan=[
             (195, 50, 8, 22, 8.5), (173, 60, 14, 16, 9.0),
             (153, 70, 18, 12, 9.5), (133, 78, 20, 10, 10.0),
             (113, 84, 22, 8, 10.5), (93, 86, 22, 8, 10.5),
             (73, 84, 20, 10, 10.0), (53, 78, 14, 14, 9.5),
             (33, 68, 8, 20, 9.0), (13, 58, 2, 26, 8.5),
             (-5, 48, -4, 30, 8.0), (-22, 38, -8, 32, 7.5),
         ]),
    dict(base=(-30, 138), crown=(-30, 98), bow1=0.0, bow2=0.0,
         trunk_w=(9.5, 6.5), organic=True, fan=[
             (248, 56, 4, 36, 8.5), (262, 60, 2, 40, 9.0),
             (270, 64, 0, 42, 9.5), (278, 60, 2, 40, 9.0),
             (292, 56, 4, 36, 8.5), (236, 48, 0, 32, 8.0),
             (304, 48, 0, 32, 8.0), (222, 40, -2, 30, 7.5),
             (318, 40, -2, 30, 7.5),
         ]),
    dict(base=(135, -138), crown=(104, -56), bow1=-8.0, bow2=4.0,
         trunk_w=(10.5, 6.0), organic=True, fan=[
             (165, 38, 10, 14, 8.0), (140, 46, 12, 10, 8.5),
             (115, 50, 12, 8, 9.0), (90, 52, 12, 8, 9.0),
             (65, 50, 10, 12, 8.5), (42, 44, 6, 16, 8.0),
             (20, 36, 0, 22, 7.5), (0, 28, -4, 26, 7.0),
         ]),
]

STYLES = {"v1": _TREES_ORGANIC, "v2": _TREES_REF, "v3": _TREES_FANS,
          "v4": _TREES_BOLD}
STYLE_LABELS = {
    "v1": "Organic (recommended)",
    "v2": "Reference",
    "v3": "Fans (original)",
    "v4": "Bold graphic",
}


def tree_polys(spec):
    """Polygons for one tree spec (dispatches organic vs classic)."""
    spec = dict(spec)
    if spec.pop("organic", False):
        return palm_organic(**spec)
    return palm_tree(**spec)


def layer_polys(trees):
    """All tree polygons for one relief layer."""
    polys = []
    for spec in trees:
        polys.extend(tree_polys(spec))
    return polys


def point_count():
    """Total polygon points per style (complexity budgeting)."""
    return {name: sum(len(p) for p in layer_polys(trees))
            for name, trees in STYLES.items()}
