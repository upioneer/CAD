#!/usr/bin/env python3
"""
KVM console plate preview: front + both bay sections as SVG.

Pure standard library (no FreeCAD). Mirrors kvm_plate_freecad.py;
RACK_SCREEN=5.0 previews the 5in variant (default 3.5).

Usage:
    python preview.py            # writes preview_<tag>.svg next to this file
                                 # (tag matches the model: screen + label)
"""

import os

HERE = os.path.dirname(os.path.abspath(__file__))
SCREEN = os.environ.get("RACK_SCREEN", "3.5")
if SCREEN not in ("3.5", "5.0"):
    SCREEN = "3.5"

LCD_SPECS = {
    "3.5": {"mod_w": 85.0, "mod_h": 55.0, "mod_t": 8.0,
            "act_w": 74.0, "act_h": 49.0, "ox": 2.95, "oy": 0.0},
    "5.0": {"mod_w": 122.0, "mod_h": 78.0, "mod_t": 10.0,
            "act_w": 110.0, "act_h": 66.0, "ox": 0.0, "oy": 0.0},
}
LCD = LCD_SPECS[SCREEN]
# HANDEDNESS: viewer looks from -Z so CAD +X appears on the viewer's
# LEFT. front() negates X to draw what the viewer sees. ox below is the
# CAD offset (active toward CAD +X, the viewer-left thin-bezel side).

# ---- Layout mirror of kvm_plate_freecad.py (keep in sync) ----
PANEL_W, PANEL_H, FACE_T = 253.0, 88.1, 4.0
HOLE_DX, HOLE_DY, HOLE_D = 236.5, 44.45, 8.0
SLOT_EXTRA, CORNER_R = 4.0, 3.0
MINI_W, MINI_H, MINI_D = 42.0, 42.0, 22.9
MINI_GLASS, MINI_WIN = 39.1, 34.0
MINI_LIP_T = 1.0
BTN_PITCH, BTN_D, BTN_DEPTH = 16.5, 5.8, 12.8
BTN_SLOT_W, BTN_EXTRA = 12.0, 3.75
POCKET_CLR, WALL_T, LIP_MIN = 0.4, 2.5, 1.0
LABEL_TEXT = os.environ.get("RACK_LABEL", "")


def filename_tag():
    tag = SCREEN.replace(".", "")
    label = "".join(c if (c.isalnum() or c in "-_") else "-"
                    for c in LABEL_TEXT.strip().replace(" ", "-"))
    if label:
        tag += "_" + label
    return tag

POCKET_W = LCD["mod_w"] + 2 * POCKET_CLR
POCKET_H = LCD["mod_h"] + 2 * POCKET_CLR
MINI_PW = MINI_W + 2 * POCKET_CLR
TOTAL = WALL_T + MINI_PW + WALL_T + POCKET_W + WALL_T
TX0, TX1 = -TOTAL / 2.0, TOTAL / 2.0
MINI_MCX = TX0 + WALL_T + MINI_PW / 2.0
LCD_MCX = TX1 - WALL_T - POCKET_W / 2.0
LCD_MCY = 0.0
TY0 = LCD_MCY - POCKET_H / 2.0 - WALL_T
TY1 = LCD_MCY + POCKET_H / 2.0 + WALL_T
MINI_MCY = 0.0
LCD_AX = LCD_MCX + LCD["ox"]
LCD_AY = LCD_MCY + LCD["oy"]


def _centered_window(mod_d, act_d, off):
    ideal = (mod_d + act_d) / 2.0
    floor = act_d + 2 * (0.8 + abs(off))
    ceil = mod_d - 2 * LIP_MIN
    return ceil if ideal < floor else min(ideal, ceil)


WIN_W = _centered_window(LCD["mod_w"], LCD["act_w"], LCD["ox"])
WIN_H = _centered_window(LCD["mod_h"], LCD["act_h"], LCD["oy"])
MINI_FRONT_Z = MINI_LIP_T - 0.1
MINI_REAR_Z = MINI_FRONT_Z + MINI_D
BTN_Z = MINI_FRONT_Z + BTN_DEPTH
SLOT_HALF = BTN_PITCH / 2.0 + BTN_D / 2.0 + BTN_EXTRA


def front(ox, oy, s):
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
    # LCD bay: module ghost, active area (offset inside it), solved window.
    p.append(rect(LCD_MCX, LCD_MCY, LCD["mod_w"], LCD["mod_h"], "5 4",
                  fill="none", stroke="#4a6fa5", **{"stroke-width": "1"}))
    p.append(rect(LCD_AX, LCD_AY, LCD["act_w"], LCD["act_h"], "2 3",
                  fill="#0a2038", stroke="#4a6fa5", **{"stroke-width": "1"}))
    p.append(rect(LCD_MCX, LCD_MCY, WIN_W, WIN_H,
                  fill="#05070c", stroke="#ff2fb3", **{"stroke-width": "1.5"}))
    # Mini bay: glass ghost + stepped window.
    p.append(rect(MINI_MCX, MINI_MCY, MINI_GLASS, MINI_GLASS, "5 4",
                  fill="none", stroke="#4a6fa5", **{"stroke-width": "1"}))
    p.append(rect(MINI_MCX, MINI_MCY, MINI_WIN, MINI_WIN,
                  fill="#05070c", stroke="#ff2fb3", **{"stroke-width": "1.5"}))
    # Label zone (embossed text in the model); hidden when blank.
    if not LABEL_TEXT:
        p.append(f'<text x="{X(PANEL_W / 2):.1f}" y="{Y(-PANEL_H / 2) + 18:.1f}" '
                 f'font-family="monospace" font-size="12" fill="#ddd">'
                 f'{SCREEN}in LCD + Mini off ({LCD["ox"]:+.2f},{LCD["oy"]:+.2f})  '
                 f'LCD win {WIN_W:.1f}x{WIN_H:.1f}  Mini win {MINI_WIN:.0f}</text>')
        return "\n    ".join(p)
    if SCREEN == "3.5":
        top_lim = Y(min(LCD_MCY - WIN_H / 2, MINI_MCY - MINI_WIN / 2) - 2.0)
        p.append(f'<rect x="{X(75.0):.1f}" y="{top_lim:.1f}" '
                 f'width="{150 * s:.1f}" height="{10 * s:.1f}" fill="none" '
                 f'stroke="#c7a15c" stroke-width="1" stroke-dasharray="3 3"/>')
        p.append(f'<text x="{X(0.0):.1f}" y="{top_lim + 8 * s:.1f}" '
                 f'font-family="monospace" font-size="{7 * s:.0f}" fill="#c7a15c" '
                 f'text-anchor="middle">{LABEL_TEXT}</text>')
    else:
        lx = (TX1 + 112.0) / 2
        p.append(f'<rect x="{X(lx + 6.0):.1f}" y="{Y(40.0):.1f}" '
                 f'width="{12 * s:.1f}" height="{80 * s:.1f}" fill="none" '
                 f'stroke="#c7a15c" stroke-width="1" stroke-dasharray="3 3"/>')
        p.append(f'<text x="{X(lx):.1f}" y="{Y(0.0):.1f}" '
                 f'font-family="monospace" font-size="{9 * s:.0f}" fill="#c7a15c" '
                 f'text-anchor="middle" transform="rotate(-90 {X(lx):.1f} {Y(0.0):.1f})">'
                 f'{LABEL_TEXT}</text>')
    p.append(f'<text x="{X(PANEL_W / 2):.1f}" y="{Y(-PANEL_H / 2) + 18:.1f}" '
             f'font-family="monospace" font-size="12" fill="#ddd">'
             f'{SCREEN}in LCD + Mini  off ({LCD["ox"]:+.2f},{LCD["oy"]:+.2f})  '
             f'LCD win {WIN_W:.1f}x{WIN_H:.1f}  Mini win {MINI_WIN:.0f}</text>')
    return "\n    ".join(p)


def section_lcd(ox, oy, s):
    """Side section through the LCD bay."""
    y0, y1 = -POCKET_H / 2 - WALL_T, POCKET_H / 2 + WALL_T
    mod_y0, mod_y1 = -LCD["mod_h"] / 2, LCD["mod_h"] / 2
    tub_z1 = FACE_T + LCD["mod_t"] + 0.5 + 2.3 + 3.5

    def X(z):
        return ox + z * s

    def Y(y):
        return oy - y * s

    p = []
    for wy0, wy1 in ((y1 - WALL_T, y1), (y0, y0 + WALL_T)):
        p.append(f'<rect x="{X(FACE_T - 0.5):.1f}" y="{Y(wy1):.1f}" '
                 f'width="{(tub_z1 - FACE_T + 0.5) * s:.1f}" height="{WALL_T * s:.1f}" '
                 f'fill="#2a2a30"/>')
    for wy0, wy1 in ((WIN_H / 2, y1), (y0, -WIN_H / 2)):
        p.append(f'<rect x="{X(0):.1f}" y="{Y(wy1):.1f}" '
                 f'width="{FACE_T * s:.1f}" height="{(wy1 - wy0) * s:.1f}" '
                 f'fill="#17171b" stroke="#555" stroke-width="0.5"/>')
    p.append(f'<rect x="{X(FACE_T):.1f}" y="{Y(mod_y1):.1f}" '
             f'width="{LCD["mod_t"] * s:.1f}" height="{LCD["mod_h"] * s:.1f}" '
             f'fill="#12325a" stroke="#4a6fa5" stroke-width="1"/>')
    fy1 = mod_y1 + 0.1 + 1.4
    tz0 = FACE_T + LCD["mod_t"] + 0.5
    p.append(f'<rect x="{X(FACE_T):.1f}" y="{Y(fy1):.1f}" '
             f'width="{(tz0 + 2.3 - FACE_T) * s:.1f}" height="{1.4 * s:.1f}" fill="#c7a15c"/>')
    tx = [(fy1 - 0.5, tz0), (mod_y1 - 1.0, tz0), (fy1 - 0.5, tz0 + 2.3)]
    pts = " ".join(f"{X(z):.1f},{Y(y):.1f}" for y, z in tx)
    p.append(f'<polygon points="{pts}" fill="#c7a15c" stroke="#7a5f2a" stroke-width="0.5"/>')
    p.append(f'<text x="{X(tub_z1 / 2):.1f}" y="{Y(y0) + 14:.1f}" '
             f'font-family="monospace" font-size="10" fill="#ddd" text-anchor="middle">LCD</text>')
    return "\n    ".join(p)


def section_mini(ox, oy, s):
    """Side section through the Mini bay (step, unit, hook, buttons hidden)."""
    y0, y1 = TY0_ABS, TY1_ABS
    tub_z1 = MINI_REAR_Z_ABS + 4.0

    def X(z):
        return ox + z * s

    def Y(y):
        return oy - y * s

    p = []
    # support ledges top + bottom (out of plane): dashed + labeled.
    for ly0 in (MINI_PLO_ABS - WALL_T, MINI_PHI_ABS):
        p.append(f'<rect x="{X(FACE_T - 0.5):.1f}" y="{Y(ly0 + WALL_T):.1f}" '
                 f'width="{(tub_z1 - FACE_T + 0.5) * s:.1f}" height="{WALL_T * s:.1f}" '
                 f'fill="none" stroke="#2a2a30" stroke-width="2" stroke-dasharray="4 3"/>')
    p.append(f'<text x="{X(tub_z1 - 1):.1f}" y="{Y(MINI_PLO_ABS - WALL_T) - 4:.1f}" '
             f'font-family="monospace" font-size="9" fill="#777" text-anchor="end">'
             f'symmetric ledges</text>')
    clr = MINI_W + 2 * POCKET_CLR
    for wy0, wy1 in ((MINI_MCY_ABS + clr / 2, TY1_ABS),
                     (TY0_ABS, MINI_MCY_ABS - clr / 2)):
        p.append(f'<rect x="{X(0):.1f}" y="{Y(wy1):.1f}" '
                 f'width="{FACE_T * s:.1f}" height="{(wy1 - wy0) * s:.1f}" '
                 f'fill="#17171b" stroke="#555" stroke-width="0.5"/>')
    for wy0, wy1 in ((MINI_MCY_ABS + MINI_WIN / 2, MINI_MCY_ABS + clr / 2),
                     (MINI_MCY_ABS - clr / 2, MINI_MCY_ABS - MINI_WIN / 2)):
        p.append(f'<rect x="{X(0):.1f}" y="{Y(wy1):.1f}" '
                 f'width="{MINI_LIP_T * s:.1f}" height="{(wy1 - wy0) * s:.1f}" '
                 f'fill="#2e2e36" stroke="#555" stroke-width="0.5"/>')
    # mini body (glass at front step)
    p.append(f'<rect x="{X(MINI_FRONT_Z_ABS):.1f}" y="{Y(MINI_MCY_ABS + MINI_H / 2):.1f}" '
             f'width="{MINI_D * s:.1f}" height="{MINI_H * s:.1f}" '
             f'fill="#12325a" stroke="#4a6fa5" stroke-width="1"/>')
    # button plane (hidden in this view, dashed) + LED dot
    p.append(f'<line x1="{X(BTN_Z_ABS):.1f}" y1="{Y(MINI_MCY_ABS - 14.9):.1f}" '
             f'x2="{X(BTN_Z_ABS):.1f}" y2="{Y(MINI_MCY_ABS + 14.9):.1f}" '
             f'stroke="#4a6fa5" stroke-width="1" stroke-dasharray="3 3"/>')
    p.append(f'<circle cx="{X(BTN_Z_ABS):.1f}" cy="{Y(MINI_MCY_ABS):.1f}" r="2" fill="#4a6fa5"/>')
    p.append(f'<text x="{X(tub_z1 / 2):.1f}" y="{Y(y0) + 14:.1f}" '
             f'font-family="monospace" font-size="10" fill="#ddd" text-anchor="middle">MINI</text>')
    return "\n    ".join(p)


LCD_MCY = -LCD["oy"]
TY0_ABS = LCD_MCY - POCKET_H / 2.0 - WALL_T
TY1_ABS = LCD_MCY + POCKET_H / 2.0 + WALL_T
MINI_MCY_ABS = 0.0
MINI_PLO_ABS = MINI_MCY_ABS - (MINI_W / 2.0 + POCKET_CLR)
MINI_PHI_ABS = MINI_MCY_ABS + (MINI_W / 2.0 + POCKET_CLR)
MINI_FRONT_Z_ABS = MINI_LIP_T - 0.1
MINI_REAR_Z_ABS = MINI_FRONT_Z_ABS + MINI_D
BTN_Z_ABS = MINI_FRONT_Z_ABS + BTN_DEPTH


def write_svg(path):
    s_front, s_sec = 2.4, 6.0
    fx, fy = 30 + PANEL_W * s_front / 2, 50 + PANEL_H * s_front / 2
    front_bottom = 50 + PANEL_H * s_front + 40
    sy = front_bottom + 110 + (TY1_ABS - TY0_ABS) * s_sec / 2
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="700" height="810" viewBox="0 0 700 810">
  <rect width="700" height="810" fill="#0a0a0c"/>
  <text x="20" y="30" font-family="monospace" font-size="15" fill="#fff">FRONT ({SCREEN}in LCD + Mini, windows + ghosts)</text>
    {front(fx, fy, s_front)}
  <text x="20" y="{front_bottom + 30:.1f}" font-family="monospace" font-size="15" fill="#fff">BAY SECTIONS 6:1 (LCD left, Mini right)</text>
    {section_lcd(60, sy, s_sec)}
    {section_mini(360, sy, s_sec)}
</svg>
'''
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"[preview] wrote {path}")


if __name__ == "__main__":
    write_svg(os.path.join(HERE, f"preview_{filename_tag()}.svg"))
