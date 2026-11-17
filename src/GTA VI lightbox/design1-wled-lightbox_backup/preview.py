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
TEXT_LINES = ("grand", "theft", "auto")
TEXT_WIDTHS_MM = (118.0, 130.0, 108.0)
TEXT_PITCH_MM = 54.0
TEXT_CX_MM, TEXT_CY_MM = 18.0, 5.0
BACKER_OFFSET_MM = 5.0

STACK = [  # (label, z_lo, z_hi, color)
    ("backplate VESA+perfs", 0.0, 3.175, "#c7a15c"),
    ("WLED cavity", 3.175, 30.825, "#1c2f57"),
    ("spacer frame", 30.825, 34.0, "#a8844c"),
    ("diffuser 1/8 acrylic", 34.0, 37.175, "#dfe9f2"),
    ("slab slot spacer*", 37.175, 40.35, "#a8844c"),
    ("tree relief REAR", 40.35, 43.525, "#232327"),
    ("tree relief FRONT", 43.525, 46.7, "#2e2e36"),
    ("reveal plate VI+1.5", 46.7, 49.875, "#3a3f4a"),
    ("neon ring VI-2.5/+4", 49.875, 53.05, "#ff2fb3"),
    ("SHADOW GAP 3mm", 53.05, 56.05, "#000000"),
    ("FACEPLATE clean, VI only", 56.05, 59.225, "#101014"),
    ("backer plaque 1pc", 59.225, 62.4, "#0a0a0c"),
    ("text face white", 62.4, 65.575, "#f4f4f6"),
]


def load_vectors():
    with open(os.path.join(HERE, "vi_palm_vectors.json"), encoding="utf-8") as f:
        return json.load(f)


def text_line_cys():
    n = len(TEXT_LINES)
    cys = [TEXT_CY_MM + (n - 1 - i) * TEXT_PITCH_MM - (n - 1) * TEXT_PITCH_MM / 2.0
           for i in range(n)]
    return sorted(cys, reverse=True)


def poly_points(poly, s, ox, oy):
    return " ".join(f"{x * s + ox:.1f},{-y * s + oy:.1f}" for x, y in poly)


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
    # Full palm trees, rear layer then front layer, over the glow
    for trees, fill in ((palm_trees.TREES_REAR, "#17171c"),
                        (palm_trees.TREES_FRONT, "#0b0b0e")):
        for poly in palm_trees.layer_polys(trees):
            parts.append(
                f'<polygon points="{poly_points(poly, s, ox, oy)}" fill="{fill}"/>')
    # Neon ring hugging the aperture edge
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
    # Stacked badge: halo -> backer -> face
    for line, tw, cy in zip(TEXT_LINES, TEXT_WIDTHS_MM, text_line_cys()):
        fs = tw * s / (0.52 * len(line))
        x, y = ox + TEXT_CX_MM * s, oy - cy * s
        # Opaque core: the model backer is solid under counters (SVG text
        # counters are transparent, so this rect restores the true look).
        parts.append(
            f'<rect x="{x - tw * s / 2:.1f}" y="{y - 12 * s:.1f}" '
            f'width="{tw * s:.1f}" height="{24 * s:.1f}" fill="#0a0a0c"/>')
        # Text-shaped backer: same glyphs inflated (thick stroke merges).
        parts.append(
            f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="middle" '
            f'dominant-baseline="central" font-family="Impact,\'Arial Black\',sans-serif" '
            f'font-size="{fs:.1f}" textLength="{tw * s:.1f}" lengthAdjust="spacingAndGlyphs" '
            f'fill="#0a0a0c" stroke="#0a0a0c" stroke-width="{2 * BACKER_OFFSET_MM * s:.1f}" '
            f'paint-order="stroke" stroke-linejoin="round" '
            f'font-weight="900">{line}</text>')
        parts.append(
            f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="middle" '
            f'dominant-baseline="central" font-family="Impact,\'Arial Black\',sans-serif" '
            f'font-size="{fs:.1f}" textLength="{tw * s:.1f}" lengthAdjust="spacingAndGlyphs" '
            f'fill="#f6f6f8" font-weight="900">{line}</text>')
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
