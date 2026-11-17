#!/usr/bin/env python3
"""
Design 1 v3 preview: renders front elevation + layer stack section as SVG.

Pure standard library (no FreeCAD), so it runs anywhere. Geometry comes from
the real vi_palm_vectors.json contours; layout constants mirror
lightbox_freecad.py and must be kept in sync with it.

Usage:
    python preview.py            # writes preview.svg next to this file
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import palm_trees

HERE = os.path.dirname(os.path.abspath(__file__))

# ---- Layout mirror of lightbox_freecad.py (keep in sync) ----
W_MM, H_MM = 300.0, 300.0
LOCKUP_JSON = "text_lockup_vectors.json"
LOCKUP_WIDTH_MM = 165.0
TEXT_CX_MM, TEXT_CY_MM = 18.0, 5.0
BACKER_OFFSET_MM = 7.0
TREE_STYLE = "v1"  # mirror of lightbox_freecad.py; preview draws this style

STACK = [  # (label, z_lo, z_hi, color)
    ("backplate VESA+perfs", 0.0, 3.175, "#c7a15c"),
    ("WLED cavity", 3.175, 46.525, "#1c2f57"),
    ("diffuser (param size)", 46.525, 49.7, "#dfe9f2"),
    ("tree panel solid+window", 49.7, 52.875, "#232327"),
    ("neon plate 287 full, VI-2.5", 52.875, 56.05, "#ff2fb3"),
    ("FACEPLATE clean, VI only", 56.05, 59.225, "#101014"),
    ("backer, text-shaped 1pc", 59.225, 62.4, "#0a0a0c"),
    ("text face white", 62.4, 65.575, "#f4f4f6"),
]


def load_vectors():
    with open(os.path.join(HERE, "vi_palm_vectors.json"), encoding="utf-8") as f:
        return json.load(f)


def poly_points(poly, s, ox, oy):
    return " ".join(f"{x * s + ox:.1f},{-y * s + oy:.1f}" for x, y in poly)


def load_lockup():
    """Traced wordmark regions in mm, y-up, centered like the model."""
    with open(os.path.join(HERE, LOCKUP_JSON), encoding="utf-8") as f:
        data = json.load(f)
    x0, y0, x1, y1 = data["bbox"]
    s = LOCKUP_WIDTH_MM / (x1 - x0)
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0

    def conv(pt):
        return (TEXT_CX_MM + (pt[0] - cx) * s,
                TEXT_CY_MM - (pt[1] - cy) * s)

    return [([conv(p) for p in r["outer"]],
             [[conv(p) for p in h] for h in r["holes"]])
            for r in data["regions"]]


def front_panel(vec, s, ox, oy):
    """Front elevation: backlit VI + palms + ring + face + text."""
    w, h = W_MM * s, H_MM * s
    v_pts = poly_points(vec["v_outer_mm"], s, ox, oy)
    i_pts = poly_points(vec["i_outer_mm"], s, ox, oy)
    parts = [f'<rect x="{ox - W_MM * s / 2:.1f}" y="{oy - H_MM * s / 2:.1f}" '
             f'width="{w:.1f}" height="{h:.1f}" fill="#050507"/>']
    # Sunset glow inside the aperture
    parts.append(f'<polygon points="{v_pts}" fill="url(#sunset)"/>')
    parts.append(f'<polygon points="{i_pts}" fill="url(#sunset)"/>')
    # Full palm trees (active style) over the glow
    for poly in palm_trees.layer_polys(palm_trees.STYLES[TREE_STYLE]):
        parts.append(
            f'<polygon points="{poly_points(poly, s, ox, oy)}" fill="#0e0e12"/>')
    # Neon plate border visible inside the aperture edge
    parts.append(f'<polygon points="{v_pts}" fill="none" stroke="#ff2fb3" '
                 f'stroke-width="{2.5 * s:.1f}" stroke-linejoin="round"/>')
    parts.append(f'<polygon points="{i_pts}" fill="none" stroke="#ff2fb3" '
                 f'stroke-width="{2.5 * s:.1f}" stroke-linejoin="round"/>')
    # Clean faceplate with ONLY the VI cut (evenodd punch)
    parts.append(
        f'<path fill="#131316" fill-rule="evenodd" d="'
        f'M {ox - w / 2:.1f} {oy - h / 2:.1f} h {w:.1f} v {h:.1f} h {-w:.1f} Z '
        f'M {v_pts.split(" ")[0]} L {" L ".join(v_pts.split(" "))} Z '
        f'M {i_pts.split(" ")[0]} L {" L ".join(i_pts.split(" "))} Z"/>')
    # Stacked badge: real traced lockup (backer halo -> white -> counters).
    # Backer reads as the same glyphs inflated (thick round stroke merges).
    lockup = load_lockup()
    for outer, _holes in lockup:
        pts = poly_points(outer, s, ox, oy)
        parts.append(
            f'<polygon points="{pts}" fill="#0a0a0c" stroke="#0a0a0c" '
            f'stroke-width="{2 * BACKER_OFFSET_MM * s:.1f}" '
            f'stroke-linejoin="round"/>')
    for outer, holes in lockup:
        parts.append(
            f'<polygon points="{poly_points(outer, s, ox, oy)}" fill="#f6f6f8"/>')
        for h in holes:  # counters stay solid black like the model backer
            parts.append(
                f'<polygon points="{poly_points(h, s, ox, oy)}" fill="#0a0a0c"/>')
    return "\n    ".join(parts)


def stack_panel(ox, oy, bar_w, z_s):
    """Side section: layer cake with z elevations."""
    parts = []
    for label, z_lo, z_hi, color in STACK:
        y = oy - z_hi * z_s
        hh = max((z_hi - z_lo) * z_s, 2.0)
        dash = ' stroke-dasharray="4 3" stroke="#666" ' if "GAP" in label else ""
        parts.append(
            f'<rect x="{ox:.1f}" y="{y:.1f}" width="{bar_w:.1f}" height="{hh:.1f}" '
            f'fill="{color}"{dash}/>'
            f'<text x="{ox + bar_w + 8:.1f}" y="{y + hh / 2 + 4:.1f}" '
            f'font-family="monospace" font-size="11" fill="#ddd">'
            f'{label}  z {z_lo:g}..{z_hi:g}</text>')
    # LED + ESP32 markers in cavity
    led_y = oy - 15.0 * z_s
    parts.append(f'<circle cx="{ox + 6:.1f}" cy="{led_y:.1f}" r="4" fill="#ff2fb3"/>'
                 f'<circle cx="{ox + bar_w - 6:.1f}" cy="{led_y:.1f}" r="4" fill="#ff2fb3"/>'
                 f'<text x="{ox + bar_w + 8:.1f}" y="{led_y + 4:.1f}" '
                 f'font-family="monospace" font-size="11" fill="#ddd">WLED strips z 10..20</text>')
    return "\n    ".join(parts)


def write_svg(path):
    vec = load_vectors()
    s = 2.0
    fx, fy = 20 + W_MM * s / 2, 40 + H_MM * s / 2
    front_bottom = 40 + H_MM * s + 30
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="1080" viewBox="0 0 900 1080">
  <defs>
    <linearGradient id="sunset" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#3b2bd6"/>
      <stop offset="0.45" stop-color="#e0219b"/>
      <stop offset="0.75" stop-color="#ff7a2f"/>
      <stop offset="1" stop-color="#ffc93c"/>
    </linearGradient>
  </defs>
  <rect width="900" height="1080" fill="#0a0a0c"/>
  <text x="20" y="26" font-family="monospace" font-size="15" fill="#fff">FRONT ELEVATION (420 x 260, faceplate clean, VI negative backlit)</text>
    {front_panel(vec, s, fx, fy)}
  <text x="20" y="{front_bottom:.1f}" font-family="monospace" font-size="15" fill="#fff">SIDE SECTION (z stack, back to front)</text>
    {stack_panel(60, front_bottom + 30 + 67 * 5, 420, 5)}
</svg>
'''
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"[preview] wrote {path}")


if __name__ == "__main__":
    write_svg(os.path.join(HERE, "preview.svg"))
