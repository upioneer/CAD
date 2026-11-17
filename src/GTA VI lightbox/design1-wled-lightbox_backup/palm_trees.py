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

TREES_REAR = [
    # Left leaner: rises from the bottom bar into the V's left arm.
    dict(base=(-70, -138), crown=(-52, 2), bow=10.0),
    # Right upright: full-height trunk inside the I, like the reference.
    dict(base=(88, -138), crown=(86, 6), bow=-4.0),
    # Top drooper: crown hung from the top bar over the V notch.
    dict(base=(-30, 138), crown=(-30, 100), bow=0.0,
         trunk_w=(9.0, 6.5), fan=DOWN_FAN),
]

TREES_FRONT = [
    # Second leaner: rises beside the rear twin for parallax depth.
    dict(base=(-120, -138), crown=(-78, 32), bow=8.0),
    # Riser: trunk from behind the faceplate into the lower I.
    # Custom fan: right side trimmed (crown sits close to the frame edge).
    dict(base=(135, -138), crown=(108, -40), bow=-10.0, fan=[
        (172, 46, 20, 7.0), (150, 52, 16, 8.0), (128, 59, 11, 8.5),
        (105, 63, 9, 8.5), (90, 65, 8, 8.5), (72, 62, 10, 8.5),
        (50, 48, 14, 8.0), (28, 38, 20, 7.5), (5, 32, 26, 7.0),
    ]),
]


def layer_polys(trees):
    """All tree polygons for one relief layer."""
    polys = []
    for spec in trees:
        polys.extend(palm_tree(**spec))
    return polys


def point_count():
    """Total polygon points per layer (complexity budgeting)."""
    return {name: sum(len(p) for p in layer_polys(trees))
            for name, trees in (("rear", TREES_REAR), ("front", TREES_FRONT))}
