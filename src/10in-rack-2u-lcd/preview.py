#!/usr/bin/env python3
"""
2U tray plate preview: front elevation + bay side-section as SVG.

Pure standard library (no FreeCAD), so it runs anywhere. Layout
constants mirror rack_plate_freecad.py and must be kept in sync.

Usage:
    python preview.py            # writes preview.svg next to this file
"""

import os

HERE = os.path.dirname(os.path.abspath(__file__))

# ---- Layout mirror of rack_plate_freecad.py (keep in sync) ----
PANEL_W, PANEL_H, FACE_T = 253.0, 88.1, 4.0
HOLE_DX, HOLE_DY, HOLE_D = 236.5, 44.45, 8.0
SLOT_EXTRA, CORNER_R = 4.0, 3.0
MOD_W, MOD_H, MOD_T = 85.0, 55.0, 8.0
ACTIVE_W, ACTIVE_H = 74.0, 49.0
POCKET_CLR, WALL_T, TUB_D = 0.4, 2.5, 14.0
WINDOW_W, WINDOW_H = 80.0, 52.0
BEZEL_L, BEZEL_R, BEZEL_T, BEZEL_B = 2.8, 8.7, 3.0, 3.0
BAY_MODE = "offset"
LIP_MIN = 1.0
HOOK_OFF, HOOK_W = 21.0, 6.0
TOOTH_Z0, MOD_REAR_Z = 12.5, 12.0

POCKET_W = MOD_W + 2 * POCKET_CLR
POCKET_H = MOD_H + 2 * POCKET_CLR
TRAY_W = 2 * POCKET_W + 3 * WALL_T
TRAY_H = POCKET_H + 2 * WALL_T
Z1 = FACE_T + TUB_D

# Mirror of bay_layout(): module centers, active centers, solved windows.
# HANDEDNESS: viewer looks from -Z so CAD +X appears viewer-LEFT; the
# viewer-frame bezel offset negates into CAD, and front() negates X.
OX = (BEZEL_R - BEZEL_L) / 2.0
OY = (BEZEL_B - BEZEL_T) / 2.0
_BASE = (POCKET_W + WALL_T) / 2.0
_MODS = [(-_BASE - OX, -OY, +1), (+_BASE - OX, -OY, +1)] \
    if BAY_MODE != "rotated" else [(-_BASE, 0.0, +1), (+_BASE, 0.0, -1)]
_HALF_W, _HALF_H = WINDOW_W / 2.0, WINDOW_H / 2.0
for _mx, _my, _s in _MODS:
    _ax, _ay = _s * OX, _s * OY
    _aw, _ah = MOD_W / 2.0 - LIP_MIN, MOD_H / 2.0 - LIP_MIN
    _HALF_W = min(_HALF_W, ACTIVE_W / 2.0 + min(
        (_ax - ACTIVE_W / 2.0) + _aw,
        _aw - (_ax + ACTIVE_W / 2.0)))
    _HALF_H = min(_HALF_H, ACTIVE_H / 2.0 + min(
        (_ay - ACTIVE_H / 2.0) + _ah,
        _ah - (_ay + ACTIVE_H / 2.0)))
WIN_W, WIN_H = 2 * _HALF_W, 2 * _HALF_H
BAYS = [(mx, my, mx + s * OX, my + s * OY) for mx, my, s in _MODS]


def front(ox, oy, s):
    """Front elevation: panel, RackStud holes, windows, module ghost."""
    # Viewer looks from -Z: CAD +X appears LEFT, so negate X to draw truth.
    def X(x):
        return ox - x * s

    def Y(y):
        return oy - y * s

    def rect(cx, cy, w, h, dash=None, **kw):
        attrs = " ".join(f'{k}="{v}"' for k, v in kw.items())
        if dash:
            attrs += f' stroke-dasharray="{dash}"'
        return (f'<rect x="{X(cx + w / 2):.1f}" y="{Y(cy + h / 2):.1f}" '
                f'width="{w * s:.1f}" height="{h * s:.1f}" {attrs}/>')

    p = [f'<rect x="{X(PANEL_W / 2):.1f}" y="{Y(PANEL_H / 2):.1f}" '
         f'width="{PANEL_W * s:.1f}" height="{PANEL_H * s:.1f}" rx="{CORNER_R * s:.1f}" '
         f'fill="#17171b" stroke="#555" stroke-width="1"/>']
    for sx in (-1, 1):
        for sy in (-1, 1):
            cx, cy = X(sx * HOLE_DX / 2), Y(sy * HOLE_DY / 2)
            a, r = SLOT_EXTRA / 2 * s, HOLE_D * s / 2
            p.append(f'<rect x="{cx - a:.1f}" y="{cy - r:.1f}" '
                     f'width="{2 * a:.1f}" height="{2 * r:.1f}" fill="#000"/>')
            p.append(f'<circle cx="{cx - a:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="#000"/>')
            p.append(f'<circle cx="{cx + a:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="#000"/>')
    for mcx, mcy, ax, ay in BAYS:
        x, y = X(mcx), Y(mcy)
        # module ghost behind the bezel (dashed), active area (dotted)
        p.append(f'<rect x="{x - MOD_W * s / 2:.1f}" y="{y - MOD_H * s / 2:.1f}" '
                 f'width="{MOD_W * s:.1f}" height="{MOD_H * s:.1f}" fill="none" '
                 f'stroke="#4a6fa5" stroke-width="1" stroke-dasharray="5 4"/>')
        xa, ya = X(ax), Y(ay)
        p.append(f'<rect x="{xa - ACTIVE_W * s / 2:.1f}" y="{ya - ACTIVE_H * s / 2:.1f}" '
                 f'width="{ACTIVE_W * s:.1f}" height="{ACTIVE_H * s:.1f}" fill="#0a2038" '
                 f'stroke="#4a6fa5" stroke-width="1" stroke-dasharray="2 3"/>')
        # bezel window cut (dark opening over the active area)
        p.append(f'<rect x="{xa - WIN_W * s / 2:.1f}" y="{ya - WIN_H * s / 2:.1f}" '
                 f'width="{WIN_W * s:.1f}" height="{WIN_H * s:.1f}" '
                 f'fill="#05070c" stroke="#ff2fb3" stroke-width="1.5"/>')
    # dims
    p.append(f'<text x="{ox - PANEL_W * s / 2:.1f}" y="{oy + PANEL_H * s / 2 + 18:.1f}" '
             f'font-family="monospace" font-size="12" fill="#ddd">'
             f'{PANEL_W:.0f} x {PANEL_H:.1f}  holes {HOLE_DX:.1f}/{HOLE_DY:.2f}  '
             f'windows {WIN_W:.1f}x{WIN_H:.1f} off ({OX:+.2f},{OY:+.2f})</text>')
    return "\n    ".join(p)


def section(ox, oy, s):
    """Side section through one bay (Y vertical, Z depth to the right)."""
    y0, y1 = -TRAY_H / 2, TRAY_H / 2
    mod_y0, mod_y1 = -MOD_H / 2, MOD_H / 2

    def X(z):
        return ox + z * s

    def Y(y):
        return oy - y * s

    p = []
    # tray top/bottom walls (z 4..18)
    for wy0, wy1 in ((y1 - WALL_T, y1), (y0, y0 + WALL_T)):
        p.append(f'<rect x="{X(FACE_T):.1f}" y="{Y(wy1):.1f}" '
                 f'width="{TUB_D * s:.1f}" height="{(wy1 - wy0) * s:.1f}" fill="#2a2a30"/>')
    # bezel with window gap (face at left)
    for wy0, wy1 in ((WINDOW_H / 2, y1), (y0, -WINDOW_H / 2)):
        p.append(f'<rect x="{X(0):.1f}" y="{Y(wy1):.1f}" '
                 f'width="{FACE_T * s:.1f}" height="{(wy1 - wy0) * s:.1f}" fill="#17171b" '
                 f'stroke="#555" stroke-width="0.5"/>')
    # module block seated against bezel
    p.append(f'<rect x="{X(FACE_T):.1f}" y="{Y(mod_y1):.1f}" '
             f'width="{MOD_T * s:.1f}" height="{MOD_H * s:.1f}" '
             f'fill="#12325a" stroke="#4a6fa5" stroke-width="1"/>')
    # hook finger + catch tooth above module rear
    fy1 = mod_y1 + 0.1 + 1.4
    p.append(f'<rect x="{X(FACE_T):.1f}" y="{Y(fy1):.1f}" '
             f'width="{(14.5 - FACE_T) * s:.1f}" height="{1.4 * s:.1f}" fill="#c7a15c"/>')
    tx = [(fy1 - 0.5, TOOTH_Z0), (mod_y1 - 1.0, TOOTH_Z0), (fy1 - 0.5, 14.5)]
    pts = " ".join(f"{X(z):.1f},{Y(y):.1f}" for y, z in tx)
    p.append(f'<polygon points="{pts}" fill="#c7a15c" stroke="#7a5f2a" stroke-width="0.5"/>')
    # labels
    p.append(f'<text x="{X(FACE_T + MOD_T / 2):.1f}" y="{Y(0) + 4:.1f}" '
             f'font-family="monospace" font-size="10" fill="#cfe3ff" text-anchor="middle">LCD 8</text>')
    p.append(f'<text x="{X(16.5):.1f}" y="{Y(mod_y1 + 3.5):.1f}" '
             f'font-family="monospace" font-size="10" fill="#c7a15c">snap hook</text>')
    p.append(f'<text x="{X(0):.1f}" y="{Y(y1 + 6):.1f}" '
             f'font-family="monospace" font-size="10" fill="#ddd">FRONT</text>')
    p.append(f'<text x="{X(Z1):.1f}" y="{Y(y1 + 6):.1f}" '
             f'font-family="monospace" font-size="10" fill="#ddd" text-anchor="end">REAR (open)</text>')
    return "\n    ".join(p)


def write_svg(path):
    s_front, s_sec = 2.4, 6.0
    fx, fy = 30 + PANEL_W * s_front / 2, 50 + PANEL_H * s_front / 2
    front_bottom = 50 + PANEL_H * s_front + 40
    sx = 60
    sy = front_bottom + 110 + TRAY_H * s_sec / 2
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="700" height="810" viewBox="0 0 700 810">
  <rect width="700" height="810" fill="#0a0a0c"/>
  <text x="20" y="30" font-family="monospace" font-size="15" fill="#fff">FRONT (rack face, windows + module ghosts)</text>
    {front(fx, fy, s_front)}
  <text x="20" y="{front_bottom + 30:.1f}" font-family="monospace" font-size="15" fill="#fff">BAY SECTION 6:1 (bezel, seated LCD, snap hook)</text>
    {section(sx, sy, s_sec)}
</svg>
'''
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"[preview] wrote {path}")


if __name__ == "__main__":
    write_svg(os.path.join(HERE, "preview.svg"))
