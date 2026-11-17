#!/usr/bin/env python3
"""
10in Rack 2U Dual 3.5in LCD Tray Plate
Parametric FDM-printable faceplate holding 2x cased 3.5in USB LCDs
(85 x 55 x 8mm, Turing/SmartCool class) side by side.

Design intent:
* Drop-in from the rear: modules seat against a front bezel lip (no
  fasteners, no adhesion) and click under printed cantilever hooks.
* Front bezel windows expose the 74 x 49 active area with margin.
* Cable slots on outer sides + top/bottom notches cover every USB-C
  port position across hardware revisions (ports vary by rev).
* 4x rack holes for RackStuds in square-hole front rails (EIA spacing).
* Prints face-down with zero supports: all features are vertical walls,
  slots, or >=45-degree ramps.

Coordinate system: X = width, Y = height, Z = depth (front bezel face
at z=0, tray extends +Z rearward). Print orientation is face-down,
so +Z prints upward.

Execution:
  In FreeCAD GUI : src/live/live_10in_rack_2u_lcd.py (live reload), or Macro -> Run
  Headless CLI   : freecadcmd rack_plate_freecad.py
"""

import sys
import os

try:
    import FreeCAD
    import Part
    import MeshPart
    from FreeCAD import Vector
except ImportError:
    print("FreeCAD Python modules not found in current environment.")
    print("Run within FreeCAD GUI or via FreeCADCmd.")
    sys.exit(0)

try:
    _THIS_DIR = os.path.dirname(os.path.abspath(__file__))
except Exception:
    _THIS_DIR = r"C:\dev\Projects\CAD\src\10in-rack-2u-lcd"
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)

# ==============================================================================
# PARAMETRIC SPECIFICATIONS (Millimeters)
# ==============================================================================

# 10in rack 2U plate (EIA widths; hole centers per NavePoint/Project Mini Rack)
PANEL_W_MM           = 253.0     # front flange width (254 nominal - clearance)
PANEL_H_MM           = 88.1      # 2U 88.9 - 0.8 vertical clearance
FACE_T_MM            = 4.0       # bezel plate thickness
RAIL_CLEAR_MM        = 222.0     # clear width between rails; tray must fit
HOLE_DX_MM           = 236.5     # horizontal hole-center spacing
HOLE_DY_MM           = 44.45     # vertical spacing: middle hole of each U
RACK_HOLE_D_MM       = 8.0       # RackStud shaft clearance + FDM tolerance
RACK_SLOT_EXTRA_MM   = 4.0       # lateral slot length beyond round (±2 wiggle)
CORNER_R_MM          = 3.0       # bezel corner radius (common 10in language)

# LCD module: cased 3.5in USB (Turing/SmartCool class)
MOD_W_MM             = 85.0
MOD_H_MM             = 55.0
MOD_T_MM             = 8.0
MOD_ACTIVE_W_MM      = 74.0      # visible screen area (must clear the window)
MOD_ACTIVE_H_MM      = 49.0

# Bezel offsets, landscape, screen upright as viewed: module edge to lit
# pixels per side. The screens sit off-center; symmetric defaults below
# reproduce centered geometry until real caliper numbers land here.
BEZEL_L_MM           = 2.8       # measured: thin side (calipers)
BEZEL_R_MM           = 8.7       # measured: thick side (calipers)
BEZEL_T_MM           = 3.0       # ASSUMED symmetric; re-measure if off
BEZEL_B_MM           = 3.0       # ASSUMED symmetric; re-measure if off
# How the pair absorbs the offset: "offset" shifts both bays so the two
# active areas land symmetric (no software flip); "rotated" mounts the
# right module at 180 degrees (needs a software flip, and the pair sits
# at different heights unless top/bottom bezels match).
BAY_MODE             = "offset"
LIP_MIN_MM           = 1.0       # minimum bezel lip over the module edge
ACTIVE_MARGIN_MIN_MM = 0.8       # minimum window margin past lit pixels

# Tray fit
POCKET_CLR_MM        = 0.4       # per-side pocket clearance (FDM)
WALL_T_MM            = 2.5       # tray wall thickness
TUB_D_MM             = 14.0      # pocket depth behind bezel (module + air)
WINDOW_W_MM          = 80.0      # bezel window: smaller than module (lip),
WINDOW_H_MM          = 52.0      # larger than active area (view + tolerance)

# Snap hooks: 2 per bay, cantilever from top wall, catch module rear face
HOOK_N_PER_BAY       = 2
HOOK_W_MM            = 6.0       # finger width (X)
HOOK_T_MM            = 1.4       # finger thickness (Y)
HOOK_ROOT_Z_MM       = 4.0       # fused root at bezel back
HOOK_FREE_Z_MM       = 5.5       # flex starts here (relief slot above)
HOOK_TIP_Z_MM        = 14.5      # finger free end
HOOK_CATCH_MM        = 1.0       # tooth overlap below module top face
HOOK_TOOTH_Z0_MM     = 12.5      # tooth front (module rear sits at 12.0)
HOOK_RELIEF_CLR_MM   = 0.2       # per-side relief slot clearance
HOOK_OFF_MM          = 21.0      # hooks at bay center +/- this (X)

# Cable slots: outer side walls + center wall + top/bottom notches
SLOT_H_MM            = 47.8      # side slot height (pocket height - bridges)
SLOT_Z0_MM           = 6.5       # slot front (open at rear for bends)
NOTCH_W_MM           = 14.0      # top/bottom notch width (centered per bay)

# True during live-watcher iterations; production IO is skipped for speed.
LIVE_ITERATION = os.environ.get("FREECAD_LIVE_ITERATION") == "1"


# ==============================================================================
# HELPERS
# ==============================================================================

def _fuse_all(parts):
    solid = parts[0]
    for part in parts[1:]:
        solid = solid.fuse(part)
    return solid


def bay_layout():
    """Solves module + window placement from the bezel offsets.

    Returns per-bay module centers, active-area centers, the uniform
    solved window size, and asymmetric-safe tray bounds. Windows center
    on the active areas and shrink from WINDOW_W/H only as far as the
    offsets demand, never below lip and active-margin minimums.
    """
    # Bezels are viewer-frame; CAD +X appears viewer-LEFT, so negate here.
    ox = (BEZEL_R_MM - BEZEL_L_MM) / 2.0
    oy = (BEZEL_B_MM - BEZEL_T_MM) / 2.0
    pocket_w = MOD_W_MM + 2 * POCKET_CLR_MM
    pocket_h = MOD_H_MM + 2 * POCKET_CLR_MM
    base = (pocket_w + WALL_T_MM) / 2.0
    if BAY_MODE == "rotated":
        mods = [(-base, 0.0, +1), (+base, 0.0, -1)]
    else:
        mods = [(-base - ox, -oy, +1), (+base - ox, -oy, +1)]
    half_w, half_h = WINDOW_W_MM / 2.0, WINDOW_H_MM / 2.0
    for _mx, _my, s in mods:
        ax, ay = s * ox, s * oy  # active center vs module center
        avail_w = MOD_W_MM / 2.0 - LIP_MIN_MM
        avail_h = MOD_H_MM / 2.0 - LIP_MIN_MM
        slow = (ax - MOD_ACTIVE_W_MM / 2.0) + avail_w
        shigh = avail_w - (ax + MOD_ACTIVE_W_MM / 2.0)
        half_w = min(half_w, MOD_ACTIVE_W_MM / 2.0 + min(slow, shigh))
        slow = (ay - MOD_ACTIVE_H_MM / 2.0) + avail_h
        shigh = avail_h - (ay + MOD_ACTIVE_H_MM / 2.0)
        half_h = min(half_h, MOD_ACTIVE_H_MM / 2.0 + min(slow, shigh))
    bays = []
    for mx, my, s in mods:
        bays.append({"mcx": mx, "mcy": my, "sign": s,
                     "ax": mx + s * ox, "ay": my + s * oy})
    p0l = bays[0]["mcx"] - pocket_w / 2.0
    p0r = bays[0]["mcx"] + pocket_w / 2.0
    p1l = bays[1]["mcx"] - pocket_w / 2.0
    p1r = bays[1]["mcx"] + pocket_w / 2.0
    cy = bays[0]["mcy"]
    return {"bays": bays, "win_w": 2 * half_w, "win_h": 2 * half_h,
            "tx0": p0l - WALL_T_MM, "tx1": p1r + WALL_T_MM,
            "ty0": cy - pocket_h / 2.0 - WALL_T_MM,
            "ty1": cy + pocket_h / 2.0 + WALL_T_MM,
            "gap0": p0r, "gap1": p1l, "ox": ox, "oy": oy}


# ==============================================================================
# TRAY BUILDERS
# ==============================================================================

def build_bezel():
    """Front flange with rack holes and two bezel windows."""
    bezel = Part.makeBox(
        PANEL_W_MM, PANEL_H_MM, FACE_T_MM,
        Vector(-PANEL_W_MM / 2.0, -PANEL_H_MM / 2.0, 0.0),
    )
    try:
        vert = [e for e in bezel.Edges
                if abs(e.BoundBox.XLength) < 1e-6
                and abs(e.BoundBox.YLength) < 1e-6]
        bezel = bezel.makeFillet(CORNER_R_MM, vert)
    except Exception as err:
        print(f"[!] Warning: corner fillet failed ({err}); sharp corners kept")
    tools = []
    r = RACK_HOLE_D_MM / 2.0
    a = RACK_SLOT_EXTRA_MM / 2.0
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            cx = sx * HOLE_DX_MM / 2.0
            cy = sy * HOLE_DY_MM / 2.0
            if a < 0.05:
                tools.append(Part.makeCylinder(
                    r, FACE_T_MM + 2.0, Vector(cx, cy, -1.0), Vector(0, 0, 1)))
                continue
            # Lateral slot: bar + end cylinders (vertical stays hole-tight).
            bar = Part.makeBox(
                2 * a, 2 * r, FACE_T_MM + 2.0, Vector(cx - a, cy - r, -1.0))
            c1 = Part.makeCylinder(
                r, FACE_T_MM + 2.0, Vector(cx - a, cy, -1.0), Vector(0, 0, 1))
            c2 = Part.makeCylinder(
                r, FACE_T_MM + 2.0, Vector(cx + a, cy, -1.0), Vector(0, 0, 1))
            tools.append(bar.fuse(c1).fuse(c2))
    lay = bay_layout()
    for b in lay["bays"]:
        tools.append(Part.makeBox(
            lay["win_w"], lay["win_h"], FACE_T_MM + 2.0,
            Vector(b["ax"] - lay["win_w"] / 2.0,
                   b["ay"] - lay["win_h"] / 2.0, -1.0),
        ))
    return bezel.cut(_fuse_all(tools))


def build_tub():
    """Pocket walls (open rear) with cable slots and hook reliefs."""
    lay = bay_layout()
    pocket_h = MOD_H_MM + 2 * POCKET_CLR_MM
    x0, x1, y0, y1 = lay["tx0"], lay["tx1"], lay["ty0"], lay["ty1"]
    tray_w, tray_h = x1 - x0, y1 - y0
    z0, z1 = FACE_T_MM, FACE_T_MM + TUB_D_MM
    bays = lay["bays"]
    cy = bays[0]["mcy"]

    walls = [
        # outer left / center / outer right (full height + depth)
        Part.makeBox(WALL_T_MM, tray_h, TUB_D_MM, Vector(x0, y0, z0)),
        Part.makeBox(lay["gap1"] - lay["gap0"], tray_h, TUB_D_MM,
                     Vector(lay["gap0"], y0, z0)),
        Part.makeBox(WALL_T_MM, tray_h, TUB_D_MM,
                     Vector(x1 - WALL_T_MM, y0, z0)),
        # top / bottom (full width, overlap the side walls)
        Part.makeBox(tray_w, WALL_T_MM, TUB_D_MM, Vector(x0, y1 - WALL_T_MM, z0)),
        Part.makeBox(tray_w, WALL_T_MM, TUB_D_MM, Vector(x0, y0, z0)),
    ]
    tub = _fuse_all(walls)

    pocket_top = cy + pocket_h / 2.0
    tools = []
    # Side cable slots: all three X-normal walls, open at rear.
    for wx0 in (x0, lay["gap0"], x1 - WALL_T_MM):
        tools.append(Part.makeBox(
            WALL_T_MM + 2.0, SLOT_H_MM, z1 - SLOT_Z0_MM + 1.0,
            Vector(wx0 - 1.0, cy - SLOT_H_MM / 2.0, SLOT_Z0_MM),
        ))
    # Top + bottom cable notches per bay, open at rear.
    for b in bays:
        cx = b["mcx"]
        tools.append(Part.makeBox(
            NOTCH_W_MM, WALL_T_MM + 2.0, z1 - SLOT_Z0_MM + 1.0,
            Vector(cx - NOTCH_W_MM / 2.0, y1 - WALL_T_MM - 1.0, SLOT_Z0_MM),
        ))
        tools.append(Part.makeBox(
            NOTCH_W_MM, WALL_T_MM + 2.0, z1 - SLOT_Z0_MM + 1.0,
            Vector(cx - NOTCH_W_MM / 2.0, y0 - 1.0, SLOT_Z0_MM),
        ))
    # Hook relief slots through the top wall (also the release access).
    for b in bays:
        for s in (-1.0, 1.0):
            hx = b["mcx"] + s * HOOK_OFF_MM
            tools.append(Part.makeBox(
                HOOK_W_MM + 2 * HOOK_RELIEF_CLR_MM,
                WALL_T_MM + 2.0,
                HOOK_TIP_Z_MM - HOOK_FREE_Z_MM + 1.0,
                Vector(hx - HOOK_W_MM / 2.0 - HOOK_RELIEF_CLR_MM,
                       pocket_top - 1.0, HOOK_FREE_Z_MM),
            ))
    return tub.cut(_fuse_all(tools))


def build_hooks():
    """Cantilever fingers + ramped catch teeth (2 per bay)."""
    lay = bay_layout()
    cy = lay["bays"][0]["mcy"]
    mod_top = cy + MOD_H_MM / 2.0
    finger_y0 = mod_top + 0.1  # kissing fit: no drag along the finger
    finger_y1 = finger_y0 + HOOK_T_MM
    tooth_ylo = mod_top - HOOK_CATCH_MM
    parts = []
    for b in lay["bays"]:
        for s in (-1.0, 1.0):
            hx = b["mcx"] + s * HOOK_OFF_MM
            parts.append(Part.makeBox(
                HOOK_W_MM, finger_y1 - finger_y0,
                HOOK_TIP_Z_MM - HOOK_ROOT_Z_MM,
                Vector(hx - HOOK_W_MM / 2.0, finger_y0, HOOK_ROOT_Z_MM),
            ))
            # Catch tooth: vertical front (catch) face behind the seated
            # module, 45-degree insertion ramp on the rear approach side.
            # Triangle in YZ, extruded across the finger width.
            tooth_top = finger_y1 - 0.5  # fused into the finger
            ty = [(tooth_top, HOOK_TOOTH_Z0_MM),
                  (tooth_ylo, HOOK_TOOTH_Z0_MM),
                  (tooth_top, HOOK_TIP_Z_MM)]
            tri = [Vector(hx - HOOK_W_MM / 2.0, y, z) for y, z in ty]
            tri.append(tri[0])
            tooth = Part.Face(Part.makePolygon(tri)).extrude(
                Vector(HOOK_W_MM, 0, 0))
            parts.append(tooth)
    return _fuse_all(parts)


# ==============================================================================
# FIT CHECKS
# ==============================================================================

def check_fits():
    """Asserts the tray actually holds the modules and fits the rack."""
    lay = bay_layout()
    pocket_w = MOD_W_MM + 2 * POCKET_CLR_MM
    pocket_h = MOD_H_MM + 2 * POCKET_CLR_MM
    tray_w, tray_h = lay["tx1"] - lay["tx0"], lay["ty1"] - lay["ty0"]
    # Measurement sanity: only the offset (difference) drives geometry.
    dh = BEZEL_L_MM + BEZEL_R_MM + MOD_ACTIVE_W_MM - MOD_W_MM
    dv = BEZEL_T_MM + BEZEL_B_MM + MOD_ACTIVE_H_MM - MOD_H_MM
    if abs(dh) > 0.3 or abs(dv) > 0.3:
        print(f"[!] Note: bezel sums off by ({dh:+.1f}, {dv:+.1f})mm; "
              f"using offset (L-R)/2={(BEZEL_L_MM - BEZEL_R_MM) / 2.0:+.2f}")
    print(f"[Fit] active offset ({lay['ox']:+.2f}, {lay['oy']:+.2f})mm, "
          f"windows {lay['win_w']:.1f}x{lay['win_h']:.1f} at "
          f"{[(round(b['ax'], 1), round(b['ay'], 1)) for b in lay['bays']]}")
    lips_ok = margins_ok = True
    for b in lay["bays"]:
        for c, a, half_mod, half_act, half_win in (
                (b["mcx"], b["ax"], MOD_W_MM / 2.0,
                 MOD_ACTIVE_W_MM / 2.0, lay["win_w"] / 2.0),
                (b["mcy"], b["ay"], MOD_H_MM / 2.0,
                 MOD_ACTIVE_H_MM / 2.0, lay["win_h"] / 2.0)):
            lip_lo = (a - half_win) - (c - half_mod)
            lip_hi = (c + half_mod) - (a + half_win)
            lips_ok = lips_ok and lip_lo >= LIP_MIN_MM - 1e-6 \
                and lip_hi >= LIP_MIN_MM - 1e-6
            margins_ok = margins_ok and \
                half_win - half_act >= ACTIVE_MARGIN_MIN_MM - 1e-6
    checks = [
        ("pocket clears module",
         pocket_w > MOD_W_MM and pocket_h > MOD_H_MM),
        ("clearance >= 0.25/side", POCKET_CLR_MM >= 0.25),
        ("window lip all around", lips_ok),
        ("window clears active area", margins_ok),
        ("tray fits between rails",
         lay["tx0"] > -RAIL_CLEAR_MM / 2.0
         and lay["tx1"] < RAIL_CLEAR_MM / 2.0),
        ("tray fits 2U height",
         lay["ty0"] > -PANEL_H_MM / 2.0
         and lay["ty1"] < PANEL_H_MM / 2.0),
        ("rack holes inside panel",
         HOLE_DX_MM / 2.0 + RACK_HOLE_D_MM / 2.0
         + RACK_SLOT_EXTRA_MM / 2.0 < PANEL_W_MM / 2.0
         and HOLE_DY_MM / 2.0 + RACK_HOLE_D_MM / 2.0 < PANEL_H_MM / 2.0),
        ("slot edge web >= 1.5mm",
         PANEL_W_MM / 2.0 - (HOLE_DX_MM / 2.0 + RACK_HOLE_D_MM / 2.0
                             + RACK_SLOT_EXTRA_MM / 2.0) >= 1.5),
        ("hooks clear bay walls",
         HOOK_OFF_MM + HOOK_W_MM / 2.0 < pocket_w / 2.0),
        ("catch behind module rear",
         HOOK_TOOTH_Z0_MM > FACE_T_MM + MOD_T_MM),
        ("module rear inside tub",
         FACE_T_MM + MOD_T_MM < FACE_T_MM + TUB_D_MM),
    ]
    ok = True
    for label, passed in checks:
        print(f"[{'OK' if passed else 'FAIL'}] Fit: {label}")
        ok = ok and passed
    if not ok:
        raise ValueError("fit checks failed; review params")
    print(f"[Fit] tray outer {tray_w:.1f} x {tray_h:.1f}mm "
          f"(rails clear {RAIL_CLEAR_MM:.0f}mm)")


# ==============================================================================
# MAIN
# ==============================================================================

def main():
    print("==================================================================")
    print("10in Rack 2U Dual 3.5in LCD Tray Plate")
    print("==================================================================")
    check_fits()

    doc_name = "Rack_2U_DualLCD"
    try:
        doc = FreeCAD.getDocument(doc_name)
        for obj in list(doc.Objects):
            try:
                doc.removeObject(obj.Name)
            except Exception:
                pass
    except Exception:
        doc = FreeCAD.newDocument(doc_name)

    bezel = build_bezel()
    tub = build_tub()
    hooks = build_hooks()
    tray = bezel.fuse(tub).fuse(hooks)

    try:
        n_solids = len(tray.Solids)
    except Exception:
        n_solids = 1
    is_manifold = n_solids == 1
    print(f"[{'OK' if is_manifold else 'FAIL'}] Tray_Plate : "
          f"{'Solid Manifold' if is_manifold else f'{n_solids} solids'} | "
          f"Volume: {tray.Volume / 1000.0:7.2f} cm3")
    if not is_manifold:
        raise ValueError("tray is not one solid; inspect!")

    bb = tray.BoundBox
    print(f"[OK] BBox: {bb.XLength:.1f} x {bb.YLength:.1f} x {bb.ZLength:.1f}mm")
    feat = doc.addObject("Part::Feature", "Tray_Plate")
    feat.Shape = tray
    try:
        if feat.ViewObject is not None:
            feat.ViewObject.ShapeColor = (0.16, 0.16, 0.18)
    except Exception:
        pass  # headless freecadcmd has no ViewObject
    doc.recompute()

    if LIVE_ITERATION:
        print("[Live] Skipping STEP/STL/FCStd writes for fast iteration.")
        print("==================================================================")
        return

    script_dir = _THIS_DIR
    export_dir = os.path.join(script_dir, "exports")
    os.makedirs(export_dir, exist_ok=True)
    fcstd_path = os.path.join(script_dir, "Rack_2U_DualLCD.FCStd")
    doc.saveAs(fcstd_path)
    print(f"\n[Saved] Native FreeCAD Document: {fcstd_path}")

    tray.exportStep(os.path.join(export_dir, "Rack_2U_DualLCD_Plate.step"))
    mesh = MeshPart.meshFromShape(
        tray, LinearDeflection=0.1, AngularDeflection=0.35)
    mesh.write(os.path.join(export_dir, "Rack_2U_DualLCD_Plate.stl"))
    print(f"[Exported] Production assets updated in: {export_dir}")
    print("==================================================================")


main()
