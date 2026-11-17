#!/usr/bin/env python3
"""
10in Rack 2U LCD + JetKVM Mini Console Plate
Parametric FDM-printable faceplate pairing 1x USB LCD (3.5in default,
5in via RACK_SCREEN=5.0) with 1x JetKVM Mini (42 x 42 x 23) so one
glance ties both to their endpoint.

Design intent:
* LCD bay (left): drop-in from the rear, bezel-lip retention, snap
  hooks, cable slots. Same proven geometry as the dual-LCD plate.
* Mini bay (right): unit stands display-forward, glass near-flush in a
  stepped bezel window; side-button pill slots + status LED in BOTH
  side walls; tapered pocket (no hook); symmetric support ledges.
* FLIP-MOUNTABLE: rotate the plate 180 degrees in-plane to swap the
  Mini left/right. Bilateral slots, centered windows/pocket, tapered
  (hook-free) Mini retention, and symmetric ledges make both parities
  identical: modules insert normally, content reads upright natively,
  no software rotation needed anywhere. Keep the label blank if you
  flip (text would read upside-down).
* Embossed endpoint label strip (3.5in) or side column (5in).
* Prints face-down with zero supports.

Coordinate system: X = width, Y = height, Z = depth (front bezel face
at z=0, tray extends +Z rearward, viewer/aisle at -Z).

Execution:
  In FreeCAD GUI : src/live/live_10in_rack_lcd_kvm.py (live reload), or Macro -> Run
  Headless CLI   : freecadcmd kvm_plate_freecad.py
                   RACK_SCREEN=5.0 freecadcmd kvm_plate_freecad.py
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
    import Draft
    HAVE_DRAFT = True
except ImportError:
    HAVE_DRAFT = False

try:
    _THIS_DIR = os.path.dirname(os.path.abspath(__file__))
except Exception:
    _THIS_DIR = r"C:\dev\Projects\CAD\src\10in-rack-lcd-kvm"
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)

# ==============================================================================
# PARAMETRIC SPECIFICATIONS (Millimeters)
# ==============================================================================

SCREEN = os.environ.get("RACK_SCREEN", "3.5")
if SCREEN not in ("3.5", "5.0"):
    print(f"[!] Unknown RACK_SCREEN={SCREEN!r}; falling back to 3.5")
    SCREEN = "3.5"

# LCD specs per screen size. 3.5in bezels are user-measured (landscape);
# 5in bezels are assumed symmetric until calipers say otherwise.
LCD_SPECS = {
    "3.5": {"mod_w": 85.0, "mod_h": 55.0, "mod_t": 8.0,
            "act_w": 74.0, "act_h": 49.0,
            "bez_l": 2.8, "bez_r": 8.7, "bez_t": 3.0, "bez_b": 3.0,
            "win_max_w": 80.0, "win_max_h": 52.0},
    "5.0": {"mod_w": 122.0, "mod_h": 78.0, "mod_t": 10.0,
            "act_w": 110.0, "act_h": 66.0,
            "bez_l": 6.0, "bez_r": 6.0, "bez_t": 6.0, "bez_b": 6.0,
            "win_max_w": 116.0, "win_max_h": 72.0},
}
LCD = LCD_SPECS[SCREEN]

# 10in rack 2U plate (EIA widths; hole centers per NavePoint/Project Mini Rack)
PANEL_W_MM           = 253.0
PANEL_H_MM           = 88.1
FACE_T_MM            = 4.0
RAIL_CLEAR_MM        = 222.0
HOLE_DX_MM           = 236.5
HOLE_DY_MM           = 44.45
RACK_HOLE_D_MM       = 8.0
RACK_SLOT_EXTRA_MM   = 4.0
CORNER_R_MM          = 3.0

# JetKVM Mini, standing display-forward. Body 42 x 42 x 23 per spec
# sheets; glass/buttons from straight-on product renders (PHOTO-DERIVED,
# +/-0.5mm: confirm with calipers on arrival, starting with MINI_GLASS).
MINI_W_MM            = 42.0      # X footprint (standing)
MINI_H_MM            = 42.0      # Y footprint (standing)
MINI_D_MM            = 22.9      # Z depth (0.9in)
MINI_GLASS_MM        = 39.1      # display glass edge-to-edge, centered
MINI_GLASS_R_MM      = 4.0       # glass corner radius (estimate)
MINI_WIN_MM          = 34.0      # bezel window (lip-safe at glass corners)
MINI_WIN_R_MM        = 3.0
MINI_LIP_T_MM        = 1.0       # front lip ring; glass sits ~flush
MINI_BTN_PITCH_MM    = 16.5      # button pair spacing, symmetric
MINI_BTN_D_MM        = 5.8
MINI_BTN_DEPTH_MM    = 12.8      # button plane behind the FRONT (glass)
                                # face: photo read 12.75 from the display
                                # edge (glass lip visible at photo top).
                                # Display-forward + buttons-right admits
                                # no other parity; flipping about any axis
                                # either faces the display into the rack
                                # or moves the buttons to the left wall.
MINI_LED_D_MM        = 3.0       # status dot opening
BTN_SLOT_W_MM        = 12.0      # pill slot width (Z, fingertip room)
BTN_SLOT_EXTRA_MM    = 3.75      # pill extension past button edges

# Tray fit (shared)
POCKET_CLR_MM        = 0.4
WALL_T_MM            = 2.5
LIP_MIN_MM           = 1.0
ACTIVE_MARGIN_MIN_MM = 0.8
MINI_TAPER_MM        = 0.3       # mini pocket widen per side at the rear
                                # mouth (wedge fit replaces the hook so
                                # both parities stay symmetric)

# Snap hooks (LCD top pair + single Mini side hook, same mechanics)
HOOK_W_MM            = 6.0
HOOK_T_MM            = 1.4
HOOK_CATCH_MM        = 1.0
HOOK_FLEX_MM         = 10.5      # free flex length
HOOK_ROOT_MM         = 2.5       # fused root length
HOOK_RELIEF_CLR_MM   = 0.2       # (LCD hook spread derives from pocket width)
TOOTH_RUN_MM         = 2.3       # ramp run (~48 degrees)

# LCD cable slots/notches
SLOT_H_MM            = 47.8
SLOT_Z0_MM           = 6.5
NOTCH_W_MM           = 14.0

# Endpoint label (embossed, paint-fillable). Set per unit at build time:
#   $env:RACK_LABEL = 'NODE-01'
# Blank default: the plate builds with no text.
LABEL_TEXT           = os.environ.get("RACK_LABEL", "")
LABEL_H_MM           = 7.0
LABEL_PROUD_MM       = 0.5

# True during live-watcher iterations; production IO is skipped for speed.
LIVE_ITERATION = os.environ.get("FREECAD_LIVE_ITERATION") == "1"

FONT_CANDIDATES = [
    os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts", "arialbd.ttf"),
    os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts", "arial.ttf"),
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]


# ==============================================================================
# HELPERS
# ==============================================================================

def _fuse_all(parts):
    solid = parts[0]
    for part in parts[1:]:
        solid = solid.fuse(part)
    return solid


def find_display_font():
    for cand in FONT_CANDIDATES:
        if os.path.isfile(cand):
            return cand
    return None


def filename_tag():
    """Variant tag for every output file: screen size + label if set."""
    tag = SCREEN.replace(".", "")
    label = "".join(c if (c.isalnum() or c in "-_") else "-"
                    for c in LABEL_TEXT.strip().replace(" ", "-"))
    if label:
        tag += "_" + label
    return tag


def rounded_rect_prism(w, h, r, z0, z1, cx, cy):
    """Rounded-rectangle cutter prism (box + 4 corner cylinders)."""
    straight_x = w - 2 * r
    straight_y = h - 2 * r
    parts = [Part.makeBox(w, straight_y, z1 - z0,
                          Vector(cx - w / 2.0, cy - straight_y / 2.0, z0)),
             Part.makeBox(straight_x, h, z1 - z0,
                          Vector(cx - straight_x / 2.0, cy - h / 2.0, z0))]
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            parts.append(Part.makeCylinder(
                r, z1 - z0,
                Vector(cx + sx * straight_x / 2.0,
                       cy + sy * straight_y / 2.0, z0),
                Vector(0, 0, 1)))
    return _fuse_all(parts)


# ==============================================================================
# LAYOUT
# ==============================================================================

def _centered_window(mod_d, act_d, off):
    """Centered window size: balanced ideal, else max-view at min lip."""
    ideal = (mod_d + act_d) / 2.0
    floor = act_d + 2 * (ACTIVE_MARGIN_MIN_MM + abs(off))
    ceil = mod_d - 2 * LIP_MIN_MM
    if floor > ceil + 1e-9:
        raise ValueError(
            f"window infeasible (need {floor:.1f}, max {ceil:.1f})")
    return ceil if ideal < floor else min(ideal, ceil)


def combo_layout():
    """Solves the LCD bay + Mini bay + label placement.

    Viewer frame, left to right: outer wall, LCD pocket, center wall,
    Mini pocket, outer wall, centered as a group. NOTE the handedness:
    the viewer looks from -Z, so CAD +X appears on the viewer's LEFT.
    LCD on CAD +X == viewer-left; Mini on CAD -X == viewer-right,
    where its buttons face the outer wall. Windows center on pockets
    on active areas) so a 180-degree flip maps every opening onto
    itself; modules insert normally in both parities with content
    upright and zero software rotation. Window size prefers the
    balanced ideal and falls back to max-view at minimum lip when
    offsets demand it.
    """
    pocket_w = LCD["mod_w"] + 2 * POCKET_CLR_MM
    pocket_h = LCD["mod_h"] + 2 * POCKET_CLR_MM
    mini_pw = MINI_W_MM + 2 * POCKET_CLR_MM
    total = WALL_T_MM + mini_pw + WALL_T_MM + pocket_w + WALL_T_MM
    tx0 = -total / 2.0
    tx1 = total / 2.0
    mini_p0 = tx0 + WALL_T_MM
    mini_p1 = mini_p0 + mini_pw
    gap0 = mini_p1
    gap1 = gap0 + WALL_T_MM
    lcd_p0 = gap1
    lcd_p1 = lcd_p0 + pocket_w
    lcd_mcx = (lcd_p0 + lcd_p1) / 2.0
    mini_mcx = (mini_p0 + mini_p1) / 2.0
    # LCD bay vertical: centered (measured T/B symmetric).
    # HANDEDNESS: bezels are measured in viewer frame (screen as viewed).
    # CAD +X appears on the viewer's LEFT (front view looks from -Z), so
    # the viewer-frame offset must be negated into CAD:
    # thin bezel viewer-left => active shifts CAD +X => ox positive.
    oy = (LCD["bez_b"] - LCD["bez_t"]) / 2.0
    lcd_mcy = -oy
    ty0 = lcd_mcy - pocket_h / 2.0 - WALL_T_MM
    ty1 = lcd_mcy + pocket_h / 2.0 + WALL_T_MM
    # LCD window centers on the pocket (flip-invariant); size prefers the
    # balanced ideal, falls back to max-view at minimum lip. The active
    # area sits off-center inside it on asymmetric bezels (visible but
    # fully shown); centering is what makes flip-mounting work with zero
    # software rotation, since modules insert normally in both parities.
    ox = (LCD["bez_r"] - LCD["bez_l"]) / 2.0
    win_w = _centered_window(LCD["mod_w"], LCD["act_w"], ox)
    win_h = _centered_window(LCD["mod_h"], LCD["act_h"], oy)
    # Mini bay vertical: centered (flip maps the pocket onto itself).
    mini_mcy = 0.0
    mini_front_z = MINI_LIP_T_MM - 0.1
    mini_rear_z = mini_front_z + MINI_D_MM
    return {
        "tx0": tx0, "tx1": tx1, "ty0": ty0, "ty1": ty1,
        "lcd_p0": lcd_p0, "lcd_p1": lcd_p1, "gap0": gap0, "gap1": gap1,
        "mini_p0": mini_p0, "mini_p1": mini_p1,
        "lcd_mcx": lcd_mcx, "lcd_mcy": lcd_mcy,
        "lcd_ax": lcd_mcx + ox, "lcd_ay": lcd_mcy + oy,
        "win_w": win_w, "win_h": win_h,
        "ox": ox, "oy": oy,
        "mini_mcx": mini_mcx, "mini_mcy": mini_mcy,
        "mini_front_z": mini_front_z, "mini_rear_z": mini_rear_z,
    }


def lcd_tub_rear():
    """LCD tub rear Z from module depth + hook + access."""
    rear = FACE_T_MM + LCD["mod_t"]
    return rear + 0.5 + TOOTH_RUN_MM + 3.5


def mini_tub_rear():
    """Mini tub rear Z from seated depth + finger access (hook-free)."""
    lay = combo_layout()
    return lay["mini_rear_z"] + 4.0


# ==============================================================================
# TRAY BUILDERS
# ==============================================================================

def build_bezel():
    """Front flange: corner rounds, rack slots, LCD + Mini windows."""
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
        print(f"[!] Warning: corner fillet failed ({err}); sharp kept")
    lay = combo_layout()
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
            bar = Part.makeBox(
                2 * a, 2 * r, FACE_T_MM + 2.0, Vector(cx - a, cy - r, -1.0))
            c1 = Part.makeCylinder(
                r, FACE_T_MM + 2.0, Vector(cx - a, cy, -1.0), Vector(0, 0, 1))
            c2 = Part.makeCylinder(
                r, FACE_T_MM + 2.0, Vector(cx + a, cy, -1.0), Vector(0, 0, 1))
            tools.append(bar.fuse(c1).fuse(c2))
    # LCD window (sharp rect centered on the pocket: flip-invariant;
    # the active area sits off-center inside it on asymmetric bezels).
    tools.append(Part.makeBox(
        lay["win_w"], lay["win_h"], FACE_T_MM + 2.0,
        Vector(lay["lcd_mcx"] - lay["win_w"] / 2.0,
               lay["lcd_mcy"] - lay["win_h"] / 2.0, -1.0)))
    # Mini stepped window: small outer (lip ring) + face clearance behind.
    tools.append(rounded_rect_prism(
        MINI_WIN_MM, MINI_WIN_MM, MINI_WIN_R_MM,
        -1.0, MINI_LIP_T_MM, lay["mini_mcx"], lay["mini_mcy"]))
    clr = MINI_W_MM + 2 * POCKET_CLR_MM
    tools.append(Part.makeBox(
        clr, clr, FACE_T_MM,  # z 0.9..: overlaps lip back for clean booleans
        Vector(lay["mini_mcx"] - clr / 2.0, lay["mini_mcy"] - clr / 2.0,
               MINI_LIP_T_MM - 0.1)))
    return bezel.cut(_fuse_all(tools))


def build_tub():
    """Pocket walls, floors, ledges, slots, reliefs, tie loops."""
    lay = combo_layout()
    pocket_h = LCD["mod_h"] + 2 * POCKET_CLR_MM
    x0, x1 = lay["tx0"], lay["tx1"]
    y0 = lay["ty0"]
    # z0 embeds 0.5 into the bezel: every joint overlaps volumetrically,
    # never just kisses coplanar (OCC fuse is flaky on kiss joints).
    z0 = FACE_T_MM - 0.5
    lcd_z1 = lcd_tub_rear()
    mini_z1 = mini_tub_rear()
    cy = lay["lcd_mcy"]
    pocket_top = cy + pocket_h / 2.0
    mini_cy = lay["mini_mcy"]
    mini_plo = mini_cy - (MINI_W_MM / 2.0 + POCKET_CLR_MM)
    mini_phi = mini_cy + (MINI_W_MM / 2.0 + POCKET_CLR_MM)

    def _tapered_wall(x_lo_front, x_hi_front, x_lo_rear, x_hi_rear):
        """X-normal wall quad (one face tapered), extruded full height."""
        pts = [(x_lo_front, z0), (x_hi_front, z0),
               (x_hi_rear, mini_z1), (x_lo_rear, mini_z1)]
        vs = [Vector(x, y0, z) for x, z in pts]
        vs.append(vs[0])
        return Part.Face(Part.makePolygon(vs)).extrude(
            Vector(0, lay["ty1"] - y0, 0))

    walls = [
        # outer left (Mini bay): mini face tapers outward rearward
        # (pocket snug at front, loose at the rear mouth: wedge fit)
        _tapered_wall(x0, x0 + WALL_T_MM,
                      x0, x0 + WALL_T_MM - MINI_TAPER_MM),
        # center wall: LCD face vertical, mini face tapers outward rearward
        _tapered_wall(lay["gap0"], lay["gap1"],
                      lay["gap0"] + MINI_TAPER_MM, lay["gap1"]),
        # outer right (LCD bay, plain, LCD depth)
        Part.makeBox(WALL_T_MM, lay["ty1"] - y0, lcd_z1 - z0,
                     Vector(x1 - WALL_T_MM, y0, z0)),
        # LCD top wall (mini bay stays open-top for cables)
        Part.makeBox(x1 - lay["gap0"], WALL_T_MM, lcd_z1 - z0,
                     Vector(lay["gap0"], lay["ty1"] - WALL_T_MM, z0)),
        # LCD floor
        Part.makeBox(x1 - lay["gap0"], WALL_T_MM, lcd_z1 - z0,
                     Vector(lay["gap0"], y0, z0)),
        # mini support ledges, top + bottom mirrored (flip-symmetric)
        Part.makeBox(5.5, WALL_T_MM, mini_z1 - z0,
                     Vector(lay["mini_p0"] - 0.5, mini_plo - WALL_T_MM, z0)),
        Part.makeBox(5.5, WALL_T_MM, mini_z1 - z0,
                     Vector(lay["mini_p1"] - 5.0, mini_plo - WALL_T_MM, z0)),
        Part.makeBox(5.5, WALL_T_MM, mini_z1 - z0,
                     Vector(lay["mini_p0"] - 0.5, mini_phi, z0)),
        Part.makeBox(5.5, WALL_T_MM, mini_z1 - z0,
                     Vector(lay["mini_p1"] - 5.0, mini_phi, z0)),
    ]
    # tie loops: rear outer corners (LCD viewer-left bay, mini viewer-right)
    for lx, lz1, ly in ((x1 - WALL_T_MM, lcd_z1, cy),
                        (x0, mini_z1, mini_cy)):
        walls.append(Part.makeBox(WALL_T_MM, 10.0, 8.5,
                                  Vector(lx, ly - 5.0, lz1 - 0.5)))
    tub = _fuse_all(walls)

    tools = []
    # LCD outer cable slots, BOTH outer walls (flip needs the pair).
    # Blind at the rear (cable bends happen outside the tray): an open
    # slot would saw through the tie-tab root. Height spans the module
    # edge minus bridges so any side port position is covered.
    slot_h = LCD["mod_h"] + 2 * POCKET_CLR_MM - 8.0
    for wx0 in (x0, x1 - WALL_T_MM):
        tools.append(Part.makeBox(
            WALL_T_MM + 2.0, slot_h, (lcd_z1 - 2.5) - (SLOT_Z0_MM - 1.0),
            Vector(wx0 - 1.0, cy - slot_h / 2.0, SLOT_Z0_MM - 1.0)))
    # LCD top + bottom notches.
    mcx = lay["lcd_mcx"]
    tools.append(Part.makeBox(
        NOTCH_W_MM, WALL_T_MM + 2.0, lcd_z1 - SLOT_Z0_MM + 1.0,
        Vector(mcx - NOTCH_W_MM / 2.0, lay["ty1"] - WALL_T_MM - 1.0,
               SLOT_Z0_MM)))
    tools.append(Part.makeBox(
        NOTCH_W_MM, WALL_T_MM + 2.0, lcd_z1 - SLOT_Z0_MM + 1.0,
        Vector(mcx - NOTCH_W_MM / 2.0, y0 - 1.0, SLOT_Z0_MM)))
    # LCD hook reliefs through the top wall.
    hoff = (LCD["mod_w"] + 2 * POCKET_CLR_MM) / 4.0
    for s in (-1.0, 1.0):
        hx = mcx + s * hoff
        tools.append(Part.makeBox(
            HOOK_W_MM + 2 * HOOK_RELIEF_CLR_MM,
            WALL_T_MM + 2.0, HOOK_FLEX_MM + 1.0,
            Vector(hx - HOOK_W_MM / 2.0 - HOOK_RELIEF_CLR_MM,
                   pocket_top - 1.0,
                   FACE_T_MM + HOOK_ROOT_MM)))
    # Mini button pill slots + LED dots in BOTH side walls: outer-left
    # serves the buttons now (they face CAD -X == viewer-right); center
    # serves them after a 180-degree flip. No hook competes anymore.
    btn_z = lay["mini_front_z"] + MINI_BTN_DEPTH_MM
    slot_half = MINI_BTN_PITCH_MM / 2.0 + MINI_BTN_D_MM / 2.0 + BTN_SLOT_EXTRA_MM
    for wx0 in (x0, lay["gap0"]):
        tools.append(Part.makeBox(
            WALL_T_MM + 2.0, 2 * slot_half - BTN_SLOT_W_MM, BTN_SLOT_W_MM,
            Vector(wx0 - 1.0,
                   mini_cy - (slot_half - BTN_SLOT_W_MM / 2.0),
                   btn_z - BTN_SLOT_W_MM / 2.0)))
        for s in (-1.0, 1.0):
            tools.append(Part.makeCylinder(
                BTN_SLOT_W_MM / 2.0, WALL_T_MM + 2.0,
                Vector(wx0 - 1.0,
                       mini_cy + s * (slot_half - BTN_SLOT_W_MM / 2.0), btn_z),
                Vector(1, 0, 0)))
        tools.append(Part.makeCylinder(
            MINI_LED_D_MM / 2.0, WALL_T_MM + 2.0,
            Vector(wx0 - 1.0, mini_cy, btn_z), Vector(1, 0, 0)))
    # Tie-loop eyes (axis X).
    for lx, lz1, ly in ((x1 - WALL_T_MM, lcd_z1, cy),
                        (x0, mini_z1, mini_cy)):
        tools.append(Part.makeCylinder(
            2.0, WALL_T_MM + 2.0, Vector(lx - 1.0, ly, lz1 + 4.0),
            Vector(1, 0, 0)))
    return tub.cut(_fuse_all(tools))


def build_lcd_hooks():
    """Top cantilever pair + ramped teeth (module-depth derived)."""
    lay = combo_layout()
    cy = lay["lcd_mcy"]
    mod_top = cy + LCD["mod_h"] / 2.0
    finger_y0 = mod_top + 0.1
    finger_y1 = finger_y0 + HOOK_T_MM
    tooth_ylo = mod_top - HOOK_CATCH_MM
    tooth_z0 = FACE_T_MM + LCD["mod_t"] + 0.5
    tip_z = tooth_z0 + TOOTH_RUN_MM
    tooth_top = finger_y1 - 0.5
    hoff = (LCD["mod_w"] + 2 * POCKET_CLR_MM) / 4.0
    parts = []
    for s in (-1.0, 1.0):
        hx = lay["lcd_mcx"] + s * hoff
        parts.append(Part.makeBox(
            HOOK_W_MM, finger_y1 - finger_y0, tip_z - FACE_T_MM,
            Vector(hx - HOOK_W_MM / 2.0, finger_y0, FACE_T_MM)))
        ty = [(tooth_top, tooth_z0),
              (tooth_ylo, tooth_z0),
              (tooth_top, tooth_z0 + TOOTH_RUN_MM)]
        tri = [Vector(hx - HOOK_W_MM / 2.0, y, z) for y, z in ty]
        tri.append(tri[0])
        parts.append(Part.Face(Part.makePolygon(tri)).extrude(
            Vector(HOOK_W_MM, 0, 0)))
    return _fuse_all(parts)


def build_label(doc):
    """Embossed endpoint text, or None (missing font/empty text safe)."""
    if not LABEL_TEXT or not HAVE_DRAFT:
        return None
    font_file = find_display_font()
    if font_file is None:
        print("[!] Warning: no font for label; skipped")
        return None
    lay = combo_layout()
    try:
        tmp = Draft.makeShapeString(
            String=LABEL_TEXT, FontFile=font_file, Size=10.0, Tracking=0)
        doc.recompute()
        bb = tmp.Shape.BoundBox
        if bb.XLength < 1e-6 or bb.YLength < 1e-6:
            raise ValueError("empty label geometry")
        # Fit box: bottom strip (3.5in) below both windows, or right
        # column, rotated (5in), between tray edge and rack slots. Label
        # shares the bezel face with windows/holes (tray sits behind).
        if SCREEN == "3.5":
            top_lim = min(lay["lcd_ay"] - lay["win_h"] / 2.0,
                          lay["mini_mcy"] - MINI_WIN_MM / 2.0) - 2.0
            box_w, box_h = 150.0, 10.0
            box_cx, box_cy = 0.0, top_lim - box_h / 2.0
            rot = 0.0
        else:
            box_w, box_h = 80.0, 12.0  # pre-rotation footprint
            box_cx = lay["tx1"] + (112.0 - lay["tx1"]) / 2.0
            box_cy = 0.0
            rot = 90.0
        s = min(box_w / bb.XLength, box_h / bb.YLength, 3.0)
        tmp.Size = 10.0 * s
        doc.recompute()
        shape = tmp.Shape.copy()
        doc.removeObject(tmp.Name)
        bb = shape.BoundBox
        shape.translate(Vector(
            box_cx - (bb.XMin + bb.XMax) / 2.0,
            box_cy - (bb.YMin + bb.YMax) / 2.0, -LABEL_PROUD_MM))
        if rot:
            shape.rotate(Vector(box_cx, box_cy, 0.0), Vector(0, 0, 1), rot)
        return shape.extrude(Vector(0, 0, LABEL_PROUD_MM + 0.1))
    except Exception as err:
        print(f"[!] Warning: label failed ({err}); skipped")
        return None


# ==============================================================================
# FIT CHECKS
# ==============================================================================

def check_fits():
    """Asserts bays hold modules, Mini glass/buttons land, tray fits."""
    lay = combo_layout()
    pocket_w = LCD["mod_w"] + 2 * POCKET_CLR_MM
    pocket_h = LCD["mod_h"] + 2 * POCKET_CLR_MM
    dh = LCD["bez_l"] + LCD["bez_r"] + LCD["act_w"] - LCD["mod_w"]
    dv = LCD["bez_t"] + LCD["bez_b"] + LCD["act_h"] - LCD["mod_h"]
    if abs(dh) > 0.3 or abs(dv) > 0.3:
        print(f"[!] Note: LCD bezel sums off by ({dh:+.1f}, {dv:+.1f})mm")
    print(f"[Fit] screen {SCREEN}in, LCD offset ({lay['ox']:+.2f}, "
          f"{lay['oy']:+.2f})mm, LCD window {lay['win_w']:.1f}x{lay['win_h']:.1f}")
    mcx, mcy = lay["lcd_mcx"], lay["lcd_mcy"]
    hw, hh = lay["win_w"] / 2.0, lay["win_h"] / 2.0
    # Window centers on the pocket (flip-invariant); lips symmetric, the
    # thin view margin absorbs the bezel offset.
    lip_x = LCD["mod_w"] / 2.0 - hw
    lip_y = LCD["mod_h"] / 2.0 - hh
    margin_x = hw - LCD["act_w"] / 2.0 - abs(lay["ox"])
    margin_y = hh - LCD["act_h"] / 2.0 - abs(lay["oy"])
    glass_lip = (MINI_GLASS_MM - MINI_WIN_MM) / 2.0
    btn_z = lay["mini_front_z"] + MINI_BTN_DEPTH_MM
    slot_half = MINI_BTN_PITCH_MM / 2.0 + MINI_BTN_D_MM / 2.0 + BTN_SLOT_EXTRA_MM
    checks = [
        ("LCD pocket clears module",
         pocket_w > LCD["mod_w"] and pocket_h > LCD["mod_h"]),
        ("LCD window lip all around",
         min(lip_x, lip_y) >= LIP_MIN_MM - 1e-6),
        ("LCD window clears active area",
         min(margin_x, margin_y) >= ACTIVE_MARGIN_MIN_MM - 1e-6),
        ("Mini glass lip all around", glass_lip >= LIP_MIN_MM - 1e-6),
        ("Mini pocket clears unit",
         MINI_W_MM + 2 * POCKET_CLR_MM > MINI_W_MM),
        ("button slot inside wall",
         btn_z - BTN_SLOT_W_MM / 2.0 > FACE_T_MM
         and btn_z + BTN_SLOT_W_MM / 2.0 < mini_tub_rear()
         and lay["mini_mcy"] - slot_half > lay["ty0"] + WALL_T_MM
         and lay["mini_mcy"] + slot_half < lay["ty1"] - WALL_T_MM),
        ("button slot covers buttons",
         slot_half > MINI_BTN_PITCH_MM / 2.0 + MINI_BTN_D_MM / 2.0),
        ("tray fits between rails",
         lay["tx0"] > -RAIL_CLEAR_MM / 2.0
         and lay["tx1"] < RAIL_CLEAR_MM / 2.0),
        ("tray fits 2U height",
         lay["ty0"] > -PANEL_H_MM / 2.0
         and lay["ty1"] < PANEL_H_MM / 2.0),
        ("rack slots inside panel",
         HOLE_DX_MM / 2.0 + RACK_HOLE_D_MM / 2.0
         + RACK_SLOT_EXTRA_MM / 2.0 < PANEL_W_MM / 2.0
         and HOLE_DY_MM / 2.0 + RACK_HOLE_D_MM / 2.0 < PANEL_H_MM / 2.0),
        ("LCD hooks clear bay walls",
         pocket_w / 4.0 + HOOK_W_MM / 2.0 < pocket_w / 2.0),
    ]
    ok = True
    for label, passed in checks:
        print(f"[{'OK' if passed else 'FAIL'}] Fit: {label}")
        ok = ok and passed
    if not ok:
        raise ValueError("fit checks failed; review params")
    tray_w = lay["tx1"] - lay["tx0"]
    print(f"[Fit] tray outer {tray_w:.1f}mm (rails clear {RAIL_CLEAR_MM:.0f}mm)")


# ==============================================================================
# MAIN
# ==============================================================================

def main():
    print("==================================================================")
    print(f"10in Rack 2U LCD + JetKVM Mini Console Plate (screen {SCREEN}in)")
    print("==================================================================")
    check_fits()

    doc_name = f"Rack_2U_LCDKVM_{filename_tag()}"
    try:
        doc = FreeCAD.getDocument(doc_name)
        for obj in list(doc.Objects):
            try:
                doc.removeObject(obj.Name)
            except Exception:
                pass
    except Exception:
        doc = FreeCAD.newDocument(doc_name)

    tray = build_bezel().fuse(build_tub()).fuse(build_lcd_hooks())
    label = build_label(doc)
    if label is not None:
        tray = tray.fuse(label)

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
    fcstd_path = os.path.join(script_dir, f"{doc_name}.FCStd")
    doc.saveAs(fcstd_path)
    print(f"\n[Saved] Native FreeCAD Document: {fcstd_path}")

    tray.exportStep(os.path.join(export_dir, f"{doc_name}_Plate.step"))
    mesh = MeshPart.meshFromShape(
        tray, LinearDeflection=0.1, AngularDeflection=0.35)
    mesh.write(os.path.join(export_dir, f"{doc_name}_Plate.stl"))
    print(f"[Exported] Production assets updated in: {export_dir}")
    print("==================================================================")


main()
