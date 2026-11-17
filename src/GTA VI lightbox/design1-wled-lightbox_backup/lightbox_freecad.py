#!/usr/bin/env python3
"""
GTA VI WLED Lightbox v3: Negative-VI Backlit Relief Lightbox
Parametric 3D Solid Model, Multi-Layer Laser-Cut Assembly & WLED Cavity

Design intent (v3 reimagine):
- Front faceplate is 100% clean: full-bleed cap with ONLY the negative "VI"
  aperture. Zero screws, zero holes, zero fasteners on the visible face.
- The "VI" is true negative space: backlit through a terraced relief channel
  (faceplate -> neon ring -> reveal step -> palm silhouettes -> diffuser).
- Palm fronds are laser-honest: every floating island is tied to the carrier
  with silhouette bridges, so the layer cuts from one sheet.
- "grand theft auto" stacks on top as a raised 2-layer badge (white face
  over a one-piece text-shaped backer) floating on clear acrylic tabs.
- Two full-palm relief layers: trunks, crowns, and coconuts mounted to
  each layer's own perimeter frame (zero floating pieces, true parallax).

Execution:
  In FreeCAD GUI : src/live/live_lightbox.py (live reload), or Macro -> Run
  Headless CLI   : freecadcmd lightbox_freecad.py
"""

import sys
import os
import json

try:
    import FreeCAD
    import Part
    import MeshPart
    from FreeCAD import Vector, Rotation, Placement
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
    _THIS_DIR = r"C:\dev\Projects\CAD\src\GTA VI lightbox\design1-wled-lightbox"
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)
import importlib
import palm_trees
# Live sessions exec this file repeatedly in ONE process: without reload(),
# Python's module cache would keep serving stale tree geometry forever.
importlib.reload(palm_trees)

# ==============================================================================
# PARAMETRIC SPECIFICATIONS (Millimeters)
# ==============================================================================

# Single-stock build: EVERYTHING cuts from 1/8" sheet (3.175mm).
# Structure + graphic layers: 1/8" basswood. Diffuser: 1/8" frosted acrylic
# (same cut thickness, translucent stock). Text faces: 1/8" white acrylic
# or painted basswood. xTool S1 20W working area: 498mm x 319mm.
SHEET_THICKNESS_MM       = 3.175     # 1/8 inch, all layers + walls + backplate
WALL_THICKNESS_MM        = 3.175     # 1/8 inch basswood walls
DIFFUSER_THICK_MM        = 3.175     # 1/8 inch frosted acrylic
ENCLOSURE_W_MM           = 300.0     # square format, cuts from 12x12" sheet
ENCLOSURE_H_MM           = 300.0     # (11.81", 2.4mm/side sheet margin)

# Box-joint fingers on the 4 vertical wall corners (wood glue assembly).
# Even count so top/bottom walls and side walls alternate symmetrically.
FINGER_COUNT             = 6
FINGER_CLEARANCE_MM      = 0.1       # glue gap between mating tab faces
FRAME_CLEARANCE_MM       = 3.0       # tree-frame fit inside the walls (per side)

# Base joinery: wall bottom tabs drop into backplate edge notches.
BACK_TABS_PER_WALL       = 4
BACK_TAB_W_MM            = 20.0
BACK_JOINT_CLR_MM        = 0.2       # glue gap around base tabs (total)

# Layer stack elevations (assembled state, back to front)
Z_BACKPLATE              = 0.0       # backplate 0..3.175
Z_DIFFUSER               = 34.0      # diffuser 34..37.175
Z_TREES_REAR             = 40.35     # rear trees 40.35..43.525 (up 1 level:
                                    # leaves 37.175..40.35 open for a future
                                    # frosted slab behind the trees)
Z_TREES_FRONT            = 43.525    # front trees 43.525..46.7 (on rear frame)
Z_REVEAL_PLATE           = 46.7      # reveal 46.7..49.875
Z_ACCENT_RING            = 49.875    # ring 49.875..53.05, seated on reveal
FACE_Z_BACK              = 56.05     # faceplate back (3mm shadow gap over ring)
FACE_Z_FRONT             = 59.225    # faceplate front (flush outer face)
Z_TEXT_BACKER            = 59.225    # backer 59.225..62.4, glues to face
Z_TEXT_FACE              = 62.4      # white letters 62.4..65.575

# Backplate joinery: keyholes + VESA + light-leak perforations
KEYHOLE_XS_MM            = (-120.0, 0.0, 120.0)  # triple keyhole options
KEYHOLE_Y_MM             = 60.0
VESA_PATTERNS_MM         = (75.0, 100.0)         # both standard patterns, centered
VESA_HOLE_DIA_MM         = 4.5                   # M4 clearance
BACK_PERF_LEN_MM         = 40.0                  # long perimeter light-leak slots
BACK_PERF_W_MM           = 4.0                   # (fewer pierces, less cleanup)
BACK_PERF_PITCH_MM       = 50.0
BACK_PERF_INSET_MM       = 12.0
BACK_PERF_ENABLED        = True

# Power ports: 12mm options on the bottom wall (both ends) and the two
# lower back corners. Side walls stay fully sealed. Plug unused ports.
POWER_PORT_DIA_MM        = 12.0
POWER_PORT_Z_MM          = 20.0
POWER_PORT_BOTTOM_XS_MM  = (-120.0, 120.0)
POWER_PORT_BACK_MM       = ((-135.0, -108.0), (135.0, -108.0))

# Relief window oversizes (mm, outward positive from exact VI outline)
REVEAL_OVERSIZE_MM       = 1.5       # terraced step visible past ring edge
RING_INNER_MM            = -2.5      # neon edge peeks 2.5mm into aperture
RING_OUTER_MM            = 4.0       # 2.5mm glue foot under faceplate
TREE_DECIMATE_MM         = 0.3       # RDP tolerance for generated trees (0 = off)

# True during live-watcher iterations (set by src/live/live_core.py);
# production IO (STEP/STL/FCStd writes) is skipped then for fast saves.
LIVE_ITERATION = os.environ.get("FREECAD_LIVE_ITERATION") == "1"

# "grand theft auto" stacked badge (official logo order, Pricedown style)
# NOTE: spelled "grand" per the official GTA wordmark; change TEXT_LINES to
# re-letter the badge without touching geometry code.
TEXT_LINES               = ("grand", "theft", "auto")
TEXT_WIDTHS_MM           = (118.0, 130.0, 108.0)
TEXT_LINE_PITCH_MM       = 54.0
TEXT_CENTER_X_MM         = 18.0
TEXT_CENTER_Y_MM         = 5.0
TEXT_FACE_T_MM           = 3.175     # 1/8 inch text stock
BACKER_OFFSET_MM         = 5.0       # uniform border hugging the letterforms

# Viewport & Display Options
EXPLODE_VIEW             = False     # True: pull layers apart along Z
EXPLODE_GAP_MM           = 25.0
DIFFUSER_TRANSPARENT     = False     # True for X-ray; False for 60 FPS orbit

# Display font chain for the badge (condensed heavy first; Pricedown stand-in)
FONT_CANDIDATES = [
    os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts", "impact.ttf"),
    os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts", "arialblk.ttf"),
    os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts", "arialbd.ttf"),
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]


# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def load_vector_data(script_dir):
    """Loads 1:1 VI and Palm Tree vector contours from vi_palm_vectors.json."""
    json_path = os.path.join(script_dir, "vi_palm_vectors.json")
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def pts_to_face(pts_2d):
    """Converts a list of [x, y] coordinates into a closed planar Part.Face."""
    vec_pts = [Vector(x, y, 0.0) for x, y in pts_2d]
    if vec_pts[0] != vec_pts[-1]:
        vec_pts.append(vec_pts[0])
    return Part.Face(Part.makePolygon(vec_pts))


def safe_offset2d(face, dist):
    """
    Offsets a planar face by dist mm (positive = outward).
    Falls back to centroid scaling if the OCC offset kernel fails, so the
    build never dies on one fragile contour operation.
    """
    try:
        result = face.makeOffset2D(dist)
        if result is not None and result.Area > 1.0:
            return result
    except Exception:
        pass
    try:
        c = face.CenterOfMass
        bb = face.BoundBox
        span = max(bb.XLength, bb.YLength)
        s = 1.0 + (dist / (span / 2.0)) if span > 0 else 1.0
        m = FreeCAD.Matrix(
            s, 0, 0, c.x * (1.0 - s),
            0, s, 0, c.y * (1.0 - s),
            0, 0, 1, 0,
        )
        return face.transformGeometry(m)
    except Exception:
        return face


def extrude_face(face, z_lo, z_hi):
    """Extrudes a Z=0 planar face into the [z_lo, z_hi] slab."""
    solid = face.extrude(Vector(0, 0, (z_hi - z_lo) + 0.02))
    solid.translate(Vector(0, 0, z_lo - 0.01))
    return solid


def cut_polys_from_plate(plate, polys, z_lo, z_hi, oversize=0.0):
    """Cuts VI/polygon windows (optionally oversized) through a plate slab."""
    result = plate
    for poly in polys:
        face = pts_to_face(poly)
        if abs(oversize) > 1e-6:
            face = safe_offset2d(face, oversize)
        tool = face.extrude(Vector(0, 0, (z_hi - z_lo) + 4.0))
        tool.translate(Vector(0, 0, z_lo - 2.0))
        result = result.cut(tool)
    return result


def add_fast_box(doc, name, dx, dy, dz, pos, color, group=None, trans=0):
    """Creates a fast native Part::Box primitive (zero boolean overhead)."""
    box = doc.addObject("Part::Box", name)
    box.Length = dx
    box.Width = dy
    box.Height = dz
    box.Placement = Placement(Vector(pos[0], pos[1], pos[2]), Rotation(0, 0, 0, 1))
    if group:
        group.addObject(box)
    try:
        if hasattr(box, "ViewObject") and box.ViewObject:
            box.ViewObject.ShapeColor = color
            box.ViewObject.Transparency = int(trans)
    except Exception:
        pass
    return box


def add_styled_feature(doc, name, shape, color, group=None, trans=0):
    """Adds a B-Rep Part::Feature with Coin3D tessellation tuned for orbit FPS."""
    try:
        if not shape.isValid():
            print(f"[!] Warning: {name} has geometric validity issues.")
        else:
            vol = round(shape.Volume / 1000.0, 2)
            print(f"[OK] {name:<30}: Solid Manifold | Volume: {vol:>7.2f} cm3")
    except Exception as err:
        print(f"[!] Warning: {name} validity check skipped ({err}).")

    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shape
    if group:
        group.addObject(obj)
    try:
        if hasattr(obj, "ViewObject") and obj.ViewObject:
            obj.ViewObject.ShapeColor = color
            obj.ViewObject.Transparency = int(trans)
            obj.ViewObject.Deviation = 0.5
            obj.ViewObject.AngularDeflection = 28.5
    except Exception:
        pass
    return obj


def find_display_font():
    """Returns the first usable condensed/heavy display font, or None."""
    for candidate in FONT_CANDIDATES:
        if candidate and os.path.isfile(candidate):
            return candidate
    return None


def _rdp_open(points, tol):
    """Ramer-Douglas-Peucker decimation of an open polyline (list of (x, y))."""
    if len(points) < 3 or tol <= 0:
        return list(points)
    ax, ay = points[0]
    bx, by = points[-1]
    dx, dy = bx - ax, by - ay
    denom = (dx * dx + dy * dy) ** 0.5
    dmax, idx = 0.0, 0
    for i in range(1, len(points) - 1):
        px, py = points[i]
        dist = abs(dy * px - dx * py + bx * ay - by * ax) / denom if denom else 0.0
        if dist > dmax:
            dmax, idx = dist, i
    if dmax > tol:
        left = _rdp_open(points[:idx + 1], tol)
        right = _rdp_open(points[idx:], tol)
        return left[:-1] + right
    return [points[0], points[-1]]


def decimate_closed(poly, tol):
    """Decimates a closed polygon ring, keeping max deviation under tol."""
    pts = [tuple(p) for p in poly]
    if len(pts) > 1 and pts[0] == pts[-1]:
        pts = pts[:-1]
    if len(pts) < 4 or tol <= 0:
        return [list(p) for p in pts]
    x0, y0 = pts[0]
    j = max(range(len(pts)), key=lambda i: (pts[i][0] - x0) ** 2 + (pts[i][1] - y0) ** 2)
    first = _rdp_open(pts[:j + 1], tol)
    second = _rdp_open(pts[j:] + pts[:1], tol)
    return [list(p) for p in (first[:-1] + second[:-1])]


# ==============================================================================
# GRAPHIC LAYER BUILDERS (1:1 VECTOR GEOMETRY)
# ==============================================================================

def vi_polys(vec_data):
    """The exact 'VI' outlines driving every aperture, ring, and window."""
    return [vec_data["v_outer_mm"], vec_data["i_outer_mm"]]


def build_front_faceplate(vec_data, z_lo, z_hi):
    """
    Layer 1: Full-bleed faceplate cap. The ONLY geometry cut is the exact
    negative 'VI' aperture. No screws, no holes, no fasteners on the face.
    """
    w, h = ENCLOSURE_W_MM, ENCLOSURE_H_MM
    plate = Part.makeBox(w, h, z_hi - z_lo, Vector(-w / 2.0, -h / 2.0, z_lo))
    return cut_polys_from_plate(plate, vi_polys(vec_data), z_lo, z_hi)


def build_accent_ring(vec_data, z_lo, z_hi):
    """
    Layer 2: Neon accent band terraced behind the aperture. The inner edge
    peeks into the negative space; the outer foot hides under the faceplate
    for glue area. V and I bands are fused into one manifold solid.
    """
    bands = []
    for poly in vi_polys(vec_data):
        outer = safe_offset2d(pts_to_face(poly), RING_OUTER_MM)
        inner = safe_offset2d(pts_to_face(poly), RING_INNER_MM)
        band = extrude_face(outer, z_lo, z_hi).cut(
            extrude_face(inner, z_lo - 1.0, z_hi + 1.0)
        )
        bands.append(band)
    ring = bands[0]
    for band in bands[1:]:
        ring = ring.fuse(band)
    return ring


def build_reveal_plate(vec_data, z_lo, z_hi):
    """
    Layer 3: Relief reveal plate. Its slightly oversized VI window forms the
    terraced step visible past the neon ring inside the aperture channel.
    """
    w = ENCLOSURE_W_MM - (2.0 * WALL_THICKNESS_MM) - 1.0
    h = ENCLOSURE_H_MM - (2.0 * WALL_THICKNESS_MM) - 1.0
    plate = Part.makeBox(w, h, z_hi - z_lo, Vector(-w / 2.0, -h / 2.0, z_lo))
    return cut_polys_from_plate(
        plate, vi_polys(vec_data), z_lo, z_hi, oversize=REVEAL_OVERSIZE_MM
    )


def build_tree_layer(trees, z_lo, z_hi, label):
    """
    Full-palm relief layer: a perimeter frame plus complete trees (trunks,
    crowns, coconuts) whose bases start ON the frame bars. The open centers
    flood with backlight while the trees read as mounted silhouettes.
    Everything fuses to ONE solid: single-sheet laser cut, zero floaters.
    """
    fw = ENCLOSURE_W_MM - 2.0 * WALL_THICKNESS_MM - 2.0 * FRAME_CLEARANCE_MM
    fh = ENCLOSURE_H_MM - 2.0 * WALL_THICKNESS_MM - 2.0 * FRAME_CLEARANCE_MM
    # 3D union, grouped: each tree's parts fuse small (well-conditioned),
    # then trees join the frame ring. 2D face fuses fragment instead of
    # merging in this OCC build, so the union stays in 3D with asserts.
    def _union_3d(parts, what):
        merged = parts[0]
        for member in parts[1:]:
            merged = merged.fuse(member)
        try:
            n = len(merged.Solids)
        except Exception:
            n = 1
        if n != 1:
            print(f"[!] {label}: {what} split into {n} solids, retrying")
            merged = parts[-1]
            for member in reversed(parts[:-1]):
                merged = merged.fuse(member)
            try:
                n = len(merged.Solids)
            except Exception:
                n = 1
            if n != 1:
                print(f"[!] {label}: {what} STILL split ({n}); inspect!")
        return merged

    bars = [Part.makeBox(x1 - x0, y1 - y0, z_hi - z_lo,
                         Vector(x0, y0, z_lo))
            for x0, y0, x1, y1 in palm_trees.frame_bars(fw, fh)]
    layer = _union_3d(bars, "frame")
    for ti, spec in enumerate(trees):
        parts = [extrude_face(pts_to_face(decimate_closed(p, TREE_DECIMATE_MM)),
                              z_lo, z_hi)
                 for p in palm_trees.palm_tree(**spec)]
        tree = _union_3d(parts, f"tree{ti}")
        layer = _union_3d([layer, tree], f"frame+tree{ti}")
    print(f"[Trees] {label}: {len(trees)} trees, one solid")
    return layer


def _offset_polygon_fallback(outline, dist):
    """
    Robust offset via a discretized polygon. Bspline offsets occasionally
    fail in OCC at specific glyph sizes; polygon offsets do not.
    """
    pts = outline.OuterWire.discretize(Number=220)
    poly = Part.Face(Part.makePolygon(pts + [pts[0]]))
    grown = poly.makeOffset2D(dist)
    if grown is None or grown.Area < 1.0:
        raise ValueError("empty offset")
    return grown


def scaled_about_xy(shape, cx, cy, s):
    """Last-resort uniform border: scale a glyph copy about its own center."""
    m = FreeCAD.Matrix(
        s, 0, 0, cx * (1.0 - s),
        0, s, 0, cy * (1.0 - s),
        0, 0, 1, 0,
    )
    return shape.transformGeometry(m)


def _shapestring_line(doc, line, target_w, cx, cy, font_file):
    """
    Builds one line of display type at an exact width, centered on (cx, cy).
    Returns a Z=0 planar shape (faces with letter counters preserved).
    """
    tmp = Draft.makeShapeString(
        String=line, FontFile=font_file, Size=100.0, Tracking=0
    )
    doc.recompute()
    bb = tmp.Shape.BoundBox
    if bb.XLength < 1e-6:
        raise ValueError(f"Empty ShapeString geometry for '{line}'")
    tmp.Size = 100.0 * target_w / bb.XLength
    doc.recompute()
    shape = tmp.Shape.copy()
    doc.removeObject(tmp.Name)
    bb = shape.BoundBox
    shape.translate(Vector(
        cx - (bb.XMin + bb.XMax) / 2.0,
        cy - (bb.YMin + bb.YMax) / 2.0,
        0.0,
    ))
    return shape


def build_text_badge(doc, explode_lift):
    """
    Raised 'grand theft auto' badge, exactly 2 layers: white letters over a
    SINGLE one-piece backer following the text shape (inflated glyph
    outlines fused). Offsets share the letters' position exactly, so
    alignment is automatic.
    Falls back to block letters if no display font is available.
    The backer glues flush onto the faceplate (no mounting tabs).
    Returns (face_solid, backer_solid).
    """
    n = len(TEXT_LINES)
    line_cys = [
        TEXT_CENTER_Y_MM + (n - 1 - i) * TEXT_LINE_PITCH_MM - (n - 1) * TEXT_LINE_PITCH_MM / 2.0
        for i in range(n)
    ]
    # line order top->bottom: grand, theft, auto
    line_cys = sorted(line_cys, reverse=True)

    font_file = find_display_font() if HAVE_DRAFT else None
    faces = []
    if font_file is not None:
        try:
            for line, target_w, cy in zip(TEXT_LINES, TEXT_WIDTHS_MM, line_cys):
                faces.append(_shapestring_line(
                    doc, line, target_w, TEXT_CENTER_X_MM, cy, font_file
                ))
            print(f"[OK] Text badge lettered with {os.path.basename(font_file)}")
        except Exception as err:
            print(f"[!] Warning: ShapeString failed ({err}); block fallback used.")
            faces = []
    else:
        print("[!] Warning: no display font found; block fallback used for text.")

    if not faces:
        for target_w, cy in zip(TEXT_WIDTHS_MM, line_cys):
            block_face = Part.makePlane(
                target_w, TEXT_LINE_PITCH_MM * 0.72,
                Vector(TEXT_CENTER_X_MM - target_w / 2.0,
                       cy - TEXT_LINE_PITCH_MM * 0.36, 0.0),
            )
            faces.append(block_face)

    def _fuse_all(parts):
        solid = parts[0]
        for part in parts[1:]:
            solid = solid.fuse(part)
        return solid

    z_face_lo = Z_TEXT_FACE + explode_lift
    z_face_hi = z_face_lo + TEXT_FACE_T_MM
    face_solid = _fuse_all([extrude_face(f, z_face_lo, z_face_hi) for f in faces])

    # One-piece backer: TRUE outward offset of every glyph outline, fused.
    # Offsets (never scales) give a uniform border hugging the letterforms;
    # inflated neighbors merge into a single text-shaped plaque. Holes are
    # dropped (outer wires only) so counters back solid black.
    inflated = []
    n_glyphs = n_offset_ok = 0
    for line, f in zip(TEXT_LINES, faces):
        try:
            glyphs = list(f.Faces)
        except Exception:
            glyphs = [f]
        for gi, g in enumerate(glyphs):
            n_glyphs += 1
            try:
                outline = Part.Face(g.OuterWire)
            except Exception:
                print(f"[Text] {line}[{gi}]: outer wire failed, glyph skipped")
                continue
            try:
                grown = outline.makeOffset2D(BACKER_OFFSET_MM)
                if grown is None or grown.Area < 1.0:
                    raise ValueError("empty offset")
                n_offset_ok += 1
            except Exception:
                try:
                    grown = _offset_polygon_fallback(outline, BACKER_OFFSET_MM)
                    print(f"[Text] {line}[{gi}]: bspline offset failed, "
                          f"polygon fallback used")
                    n_offset_ok += 1
                except Exception:
                    bb = outline.BoundBox
                    grown = scaled_about_xy(
                        outline, (bb.XMin + bb.XMax) / 2.0,
                        (bb.YMin + bb.YMax) / 2.0, 1.06)
                    print(f"[Text] {line}[{gi}]: offsets failed, scaled fallback")
            inflated.append(extrude_face(
                grown, Z_TEXT_BACKER + explode_lift,
                Z_TEXT_BACKER + SHEET_THICKNESS_MM + explode_lift,
            ))
    print(f"[Text] backer offsets ok: {n_offset_ok}/{n_glyphs}")
    backer_solid = _fuse_all(inflated)
    try:
        n_solids = len(backer_solid.Solids)
    except Exception:
        n_solids = 1
    if n_solids > 1:
        # Rare: lines did not quite merge. Stitch with one hidden spine bar.
        print(f"[Text] Backer split in {n_solids}; stitching with spine bar.")
        bb = backer_solid.BoundBox
        spine = Part.makeBox(
            12.0, bb.YLength, SHEET_THICKNESS_MM,
            Vector(TEXT_CENTER_X_MM - 6.0, bb.YMin,
                   Z_TEXT_BACKER + explode_lift),
        )
        backer_solid = backer_solid.fuse(spine)

    return face_solid, backer_solid


# ==============================================================================
# CHASSIS BUILDERS
# ==============================================================================

def build_backplate():
    """
    Rear 1/8" chassis plate: triple keyholes, 75 + 100mm VESA patterns,
    lower-corner power ports, and long perimeter light-leak slots.
    All cutters are fused into one tool: a single boolean cut.
    """
    w, h, t = ENCLOSURE_W_MM, ENCLOSURE_H_MM, WALL_THICKNESS_MM
    back = Part.makeBox(w, h, t, Vector(-w / 2.0, -h / 2.0, Z_BACKPLATE))

    tools = []
    for px, py in POWER_PORT_BACK_MM:
        tools.append(Part.makeCylinder(
            POWER_PORT_DIA_MM / 2.0, t + 2.0,
            Vector(px, py, -1.0), Vector(0, 0, 1),
        ))
    for kx in KEYHOLE_XS_MM:
        ky = KEYHOLE_Y_MM
        tools.append(Part.makeCylinder(4.0, t + 2.0, Vector(kx, ky, -1.0), Vector(0, 0, 1)))
        tools.append(Part.makeCylinder(2.1, t + 2.0, Vector(kx, ky + 10.0, -1.0), Vector(0, 0, 1)))
        tools.append(Part.makeBox(4.2, 10.0, t + 2.0, Vector(kx - 2.1, ky, -1.0)))

    for pattern in VESA_PATTERNS_MM:
        half = pattern / 2.0
        for vx in (-half, half):
            for vy in (-half, half):
                tools.append(Part.makeCylinder(
                    VESA_HOLE_DIA_MM / 2.0, t + 2.0,
                    Vector(vx, vy, -1.0), Vector(0, 0, 1),
                ))

    # Edge notches receiving the wall base tabs (all 4 sides). Walls sit
    # flush with the exterior, so these break the plate edge (U-notches).
    nw = BACK_TAB_W_MM + BACK_JOINT_CLR_MM
    nd = t + BACK_JOINT_CLR_MM
    for c in back_tab_centers():
        for e in (-1.0, 1.0):
            tools.append(Part.makeBox(
                nw, nd + 1.0, t + 2.0,
                Vector(c - nw / 2.0,
                       e * h / 2.0 - (nd if e > 0 else 1.0), -1.0)))
            tools.append(Part.makeBox(
                nd + 1.0, nw, t + 2.0,
                Vector(e * w / 2.0 - (nd if e > 0 else 1.0),
                       c - nw / 2.0, -1.0)))

    if BACK_PERF_ENABLED:
        sl, sw = BACK_PERF_LEN_MM, BACK_PERF_W_MM
        xe = w / 2.0 - BACK_PERF_INSET_MM
        ye = h / 2.0 - BACK_PERF_INSET_MM

        def _centers(half_span, half_len, pitch):
            span = 2.0 * (half_span - half_len)
            n = max(int(span // pitch), 0)
            start = -n * pitch / 2.0
            return [round(start + i * pitch, 3) for i in range(n + 1)]

        # Horizontal slots along top/bottom; vertical slots left/right.
        # Column span stops short so slot ends clear the corner rows.
        xs = _centers(xe, sl / 2.0, BACK_PERF_PITCH_MM)
        ys = _centers(ye - sl / 2.0, sl / 2.0, BACK_PERF_PITCH_MM)
        for px in xs:
            for py in (-ye, ye):
                tools.append(Part.makeBox(
                    sl, sw, t + 2.0, Vector(px - sl / 2.0, py - sw / 2.0, -1.0)))
        for py in ys:
            for px in (-xe, xe):
                tools.append(Part.makeBox(
                    sw, sl, t + 2.0, Vector(px - sw / 2.0, py - sl / 2.0, -1.0)))
        print(f"[Backplate] {len(tools)} cutters "
              f"({len(xs) * 2 + len(ys) * 2} light-leak slots)")

    tool = tools[0]
    for cutter in tools[1:]:
        tool = tool.fuse(cutter)
    return back.cut(tool)


def comb_outline(s0, s1, tab, z0, z1, fingers, tab_even, clr,
                 teeth=None, tooth_depth=0.0):
    """
    2D box-joint comb polygon: wall running s0..s1 with finger tabs
    protruding one thickness past each end on alternating z bands.
    tab_even picks even (True) or odd (False) bands; mating walls use
    opposite parity so tabs interleave with a glue gap. Optional bottom
    teeth (list of (xa, xb) ranges) extend below z0 in the SAME profile,
    so base tabs never need a fused box (no seam edges).
    """
    th = (z1 - z0) / fingers
    pts = [(s0, z0)]
    for i in range(fingers):
        zlo, zhi = z0 + i * th, z0 + (i + 1) * th
        if (i % 2 == 0) == tab_even:
            c = clr / 2.0
            pts += [(s0, zlo + c), (s0 - tab, zlo + c),
                    (s0 - tab, zhi - c), (s0, zhi - c)]
        else:
            pts.append((s0, zhi))
    if pts[-1] != (s0, z1):
        pts.append((s0, z1))
    pts.append((s1, z1))
    for i in range(fingers - 1, -1, -1):
        zlo, zhi = z0 + i * th, z0 + (i + 1) * th
        if (i % 2 == 0) == tab_even:
            c = clr / 2.0
            pts += [(s1, zhi - c), (s1 + tab, zhi - c),
                    (s1 + tab, zlo + c), (s1, zlo + c)]
        else:
            pts.append((s1, zlo))
    if pts[-1] != (s1, z0):
        pts.append((s1, z0))
    for xa, xb in sorted(teeth or [], reverse=True):
        pts += [(xb, z0), (xb, z0 - tooth_depth),
                (xa, z0 - tooth_depth), (xa, z0)]
    return pts


def _wall_from_comb(outline_2d, plane, fixed, z_lo_unused, thick, inward):
    """Extrudes a comb outline (built flat) into a positioned wall solid."""
    pts3 = [Vector(fixed, s, z) if plane == "x" else Vector(s, fixed, z)
            for s, z in outline_2d]
    pts3.append(pts3[0])
    return Part.Face(Part.makePolygon(pts3)).extrude(inward * thick)


def back_tab_centers():
    """Tab centers along a wall span; shared by walls and backplate."""
    s = ENCLOSURE_W_MM / 2.0 - WALL_THICKNESS_MM
    n = BACK_TABS_PER_WALL
    return [-s + 2.0 * s * (i + 0.5) / n for i in range(n)]


def base_teeth():
    """Bottom-edge tooth ranges shared by all walls (match backplate notches)."""
    hw = BACK_TAB_W_MM / 2.0
    return [(c - hw, c + hw) for c in back_tab_centers()]


def build_h_wall(sign, z_lo, z_hi, tab_even):
    """Top (+1) / bottom (-1) wall: comb panel spanning X, tabs at both ends."""
    w, t = ENCLOSURE_W_MM, WALL_THICKNESS_MM
    s = w / 2.0 - t
    outline = comb_outline(-s, s, t, z_lo, z_hi,
                           FINGER_COUNT, tab_even, FINGER_CLEARANCE_MM,
                           teeth=base_teeth(), tooth_depth=t)
    return _wall_from_comb(outline, "y", sign * ENCLOSURE_H_MM / 2.0,
                           z_lo, t, Vector(0, -sign, 0))


def build_v_wall(sign, z_lo, z_hi, tab_even):
    """Left (-1) / right (+1) wall: comb panel spanning Y, tabs at both ends."""
    h, t = ENCLOSURE_H_MM, WALL_THICKNESS_MM
    s = h / 2.0 - t
    outline = comb_outline(-s, s, t, z_lo, z_hi,
                           FINGER_COUNT, tab_even, FINGER_CLEARANCE_MM,
                           teeth=base_teeth(), tooth_depth=t)
    return _wall_from_comb(outline, "x", sign * ENCLOSURE_W_MM / 2.0,
                           z_lo, t, Vector(-sign, 0, 0))


def build_bottom_wall_with_power_ports(wall_top_z):
    """Bottom wall: finger-jointed comb plus a 12mm port near EACH end."""
    wall = build_h_wall(-1, WALL_THICKNESS_MM, wall_top_z, tab_even=False)
    h, t = ENCLOSURE_H_MM, WALL_THICKNESS_MM
    for px in POWER_PORT_BOTTOM_XS_MM:
        pwr_hole = Part.makeCylinder(
            POWER_PORT_DIA_MM / 2.0, t + 4.0,
            Vector(px, -h / 2.0 - 2.0, POWER_PORT_Z_MM),
            Vector(0, 1, 0),
        )
        wall = wall.cut(pwr_hole)
    return wall


def build_spacer_frame_shape(z_lo, height):
    """One fused 4-strip ring; plates rest on these at their level."""
    w = ENCLOSURE_W_MM - (2.0 * WALL_THICKNESS_MM) - 1.0
    h = ENCLOSURE_H_MM - (2.0 * WALL_THICKNESS_MM) - 1.0
    bar = 12.0
    strips = [
        Part.makeBox(w, bar, height, Vector(-w / 2.0, h / 2.0 - bar, z_lo)),
        Part.makeBox(w, bar, height, Vector(-w / 2.0, -h / 2.0, z_lo)),
        Part.makeBox(bar, h, height, Vector(-w / 2.0, -h / 2.0, z_lo)),
        Part.makeBox(bar, h, height, Vector(w / 2.0 - bar, -h / 2.0, z_lo)),
    ]
    ring = strips[0]
    for strip in strips[1:]:
        ring = ring.fuse(strip)
    return ring


def add_spacer_frame(doc, name, z_lo, height, group, color):
    """Adds one fused spacer ring feature; returns its shape for export."""
    shape = build_spacer_frame_shape(z_lo, height)
    add_styled_feature(doc, name, shape, color, group)
    return shape


# ==============================================================================
# MAIN ASSEMBLY COMPILATION
# ==============================================================================

def main():
    script_dir = (
        os.path.dirname(os.path.abspath(__file__))
        if "__file__" in globals()
        else r"C:\dev\Projects\CAD\src\GTA VI lightbox\design1-wled-lightbox"
    )
    export_dir = os.path.join(script_dir, "exports")
    os.makedirs(export_dir, exist_ok=True)

    vec_data = load_vector_data(script_dir)

    doc_name = "GTA_VI_Lightbox"
    try:
        doc = FreeCAD.getDocument(doc_name)
    except Exception:
        doc = None

    if doc is None:
        doc = FreeCAD.newDocument(doc_name)
    else:
        for obj in list(doc.Objects):
            try:
                doc.removeObject(obj.Name)
            except Exception:
                pass

    grp_relief = doc.addObject("App::DocumentObjectGroup", "01_Front_Relief_Stack")
    grp_text   = doc.addObject("App::DocumentObjectGroup", "02_Text_Badge")
    grp_optics = doc.addObject("App::DocumentObjectGroup", "03_Optics_And_Spacers")
    grp_chassis = doc.addObject("App::DocumentObjectGroup", "04_Enclosure_Chassis")
    grp_wled   = doc.addObject("App::DocumentObjectGroup", "05_WLED_Electronics")

    gap = EXPLODE_GAP_MM if EXPLODE_VIEW else 0.0
    lift_diffuser = gap * 1.0
    lift_rear     = gap * 1.5
    lift_front    = gap * 1.9
    lift_reveal   = gap * 2.3
    lift_ring     = gap * 2.6
    lift_face     = gap * 3.2
    lift_text     = gap * 4.2

    print("==================================================================")
    print("GTA VI WLED Lightbox v3: Negative-VI Backlit Relief Assembly")
    print(f"Bed Envelope Check: {ENCLOSURE_W_MM}mm x {ENCLOSURE_H_MM}mm (xTool S1 OK)")
    print(f"Display Mode      : {'EXPLODED 3D VIEW' if EXPLODE_VIEW else 'ASSEMBLED PRODUCTION'}")
    print("==================================================================")

    # ------------------------------------------------------------------
    # 1. FRONT RELIEF STACK (faceplate -> ring -> reveal -> palms)
    # ------------------------------------------------------------------
    faceplate = build_front_faceplate(
        vec_data, FACE_Z_BACK + lift_face, FACE_Z_FRONT + lift_face)
    accent_ring = build_accent_ring(
        vec_data, Z_ACCENT_RING + lift_ring,
        Z_ACCENT_RING + SHEET_THICKNESS_MM + lift_ring)
    reveal = build_reveal_plate(
        vec_data, Z_REVEAL_PLATE + lift_reveal,
        Z_REVEAL_PLATE + SHEET_THICKNESS_MM + lift_reveal)
    trees_rear = build_tree_layer(
        palm_trees.TREES_REAR, Z_TREES_REAR + lift_rear,
        Z_TREES_REAR + SHEET_THICKNESS_MM + lift_rear, "rear")
    trees_front = build_tree_layer(
        palm_trees.TREES_FRONT, Z_TREES_FRONT + lift_front,
        Z_TREES_FRONT + SHEET_THICKNESS_MM + lift_front, "front")

    add_styled_feature(doc, "Front_Faceplate", faceplate, (0.10, 0.10, 0.12), grp_relief)
    add_styled_feature(doc, "Neon_Accent_Ring", accent_ring, (0.95, 0.05, 0.55), grp_relief)
    add_styled_feature(doc, "Relief_Reveal_Plate", reveal, (0.20, 0.18, 0.22), grp_relief)
    add_styled_feature(doc, "Tree_Relief_Rear", trees_rear, (0.13, 0.13, 0.16), grp_relief)
    add_styled_feature(doc, "Tree_Relief_Front", trees_front, (0.16, 0.16, 0.19), grp_relief)

    # ------------------------------------------------------------------
    # 2. RAISED TEXT BADGE + CLEAR TABS
    # ------------------------------------------------------------------
    text_face, text_backer = build_text_badge(doc, lift_text)

    add_styled_feature(doc, "Text_Face_White", text_face, (0.96, 0.96, 0.97), grp_text)
    add_styled_feature(doc, "Text_Backer_Plate", text_backer, (0.08, 0.08, 0.10), grp_text)

    # ------------------------------------------------------------------
    # 3. OPTICS (diffuser + support frames)
    # ------------------------------------------------------------------
    diff_w = ENCLOSURE_W_MM - (2.0 * WALL_THICKNESS_MM) - 2.0
    diff_h = ENCLOSURE_H_MM - (2.0 * WALL_THICKNESS_MM) - 2.0
    diff_trans = 50 if DIFFUSER_TRANSPARENT else 0
    diffuser = Part.makeBox(
        diff_w, diff_h, DIFFUSER_THICK_MM,
        Vector(-diff_w / 2.0, -diff_h / 2.0, Z_DIFFUSER + lift_diffuser),
    )
    add_styled_feature(doc, "Optical_Diffuser_Panel", diffuser,
                       (0.92, 0.95, 0.98), grp_optics, trans=diff_trans)
    birch = (0.45, 0.32, 0.22)
    st = SHEET_THICKNESS_MM
    add_spacer_frame(doc, "Spacer_Diffuser", Z_DIFFUSER - st + lift_diffuser, st, grp_optics, birch)
    # Reserved slot for a future frosted slab behind the trees: spacer holds
    # the rear frame until the slab exists (omit the spacer when fitting it).
    spacer_shape = add_spacer_frame(
        doc, "Spacer_SlabSlot", Z_DIFFUSER + DIFFUSER_THICK_MM + lift_rear, st, grp_optics, birch)

    # ------------------------------------------------------------------
    # 4. ENCLOSURE CHASSIS (walls cap UNDER the faceplate; face stays clean)
    # ------------------------------------------------------------------
    w, h, t = ENCLOSURE_W_MM, ENCLOSURE_H_MM, WALL_THICKNESS_MM
    basswood = (0.82, 0.68, 0.47)

    # Finger-jointed walls (odd parity top/bottom, even parity sides).
    # Top/left/right fully sealed; bottom wall + backplate carry ports.
    wall_top = build_h_wall(+1, t, FACE_Z_BACK, tab_even=False)
    wall_bottom = build_bottom_wall_with_power_ports(FACE_Z_BACK)
    wall_side = build_v_wall(-1, t, FACE_Z_BACK, tab_even=True)
    wall_side_r = build_v_wall(+1, t, FACE_Z_BACK, tab_even=True)
    add_styled_feature(doc, "Wall_Top", wall_top, basswood, grp_chassis)
    add_styled_feature(doc, "Wall_Bottom_Ports", wall_bottom, basswood, grp_chassis)
    add_styled_feature(doc, "Wall_Left", wall_side, basswood, grp_chassis)
    add_styled_feature(doc, "Wall_Right", wall_side_r, basswood, grp_chassis)

    for an, bn, sa, sb in (("Top", "Left", wall_top, wall_side),
                           ("Top", "Right", wall_top, wall_side_r),
                           ("Bottom", "Left", wall_bottom, wall_side),
                           ("Bottom", "Right", wall_bottom, wall_side_r)):
        overlap = sa.common(sb).Volume / 1000.0
        if overlap > 0.05:
            print(f"[!] Joint {an}-{bn} fingers COLLIDE: {overlap:.2f} cm3")
        else:
            print(f"[OK] Joint {an}-{bn} interleaves clean ({overlap:.3f} cm3)")

    backplate = build_backplate()
    add_styled_feature(doc, "Backplate_VESA_Perfs", backplate,
                       (0.78, 0.62, 0.42), grp_chassis)

    # ------------------------------------------------------------------
    # 5. WLED ELECTRONICS (sunset segments: violet / magenta / amber)
    # ------------------------------------------------------------------
    w_in = w - 2 * t
    h_in = h - 2 * t
    add_fast_box(doc, "ESP32_Mounting_Sled", 36.0, 58.0, 3.0,
                 (-18.0, -80.0, t), (0.10, 0.50, 0.80), grp_wled)
    # LED runs float off the wall inner faces: exact touches render as
    # coplanar flicker (false overlap look) in the viewport.
    led_gap = 0.5
    add_fast_box(doc, "WLED_Top_Violet", w_in, 3.0, 10.0,
                 (-w_in / 2.0, h_in / 2.0 - 3.0 - led_gap, 10.0), (0.35, 0.20, 0.95), grp_wled)
    # Bottom run splits into 3 with 20mm gaps where the ports land
    g0, g1 = POWER_PORT_BOTTOM_XS_MM[0] - 10.0, POWER_PORT_BOTTOM_XS_MM[0] + 10.0
    g2, g3 = POWER_PORT_BOTTOM_XS_MM[1] - 10.0, POWER_PORT_BOTTOM_XS_MM[1] + 10.0
    add_fast_box(doc, "WLED_Bot_Amber_L", g0 + w_in / 2.0, 3.0, 10.0,
                 (-w_in / 2.0, -h_in / 2.0 + led_gap, 10.0), (1.00, 0.60, 0.05), grp_wled)
    add_fast_box(doc, "WLED_Bot_Amber_M", g2 - g1, 3.0, 10.0,
                 (g1, -h_in / 2.0 + led_gap, 10.0), (1.00, 0.60, 0.05), grp_wled)
    add_fast_box(doc, "WLED_Bot_Amber_R", w_in / 2.0 - g3, 3.0, 10.0,
                 (g3, -h_in / 2.0 + led_gap, 10.0), (1.00, 0.60, 0.05), grp_wled)
    add_fast_box(doc, "WLED_Left_Magenta", 3.0, h_in - 6.0, 10.0,
                 (-w_in / 2.0 + led_gap, -h_in / 2.0 + 3.0, 10.0), (0.95, 0.10, 0.60), grp_wled)
    add_fast_box(doc, "WLED_Right_Magenta", 3.0, h_in - 6.0, 10.0,
                 (w_in / 2.0 - 3.0 - led_gap, -h_in / 2.0 + 3.0, 10.0), (0.95, 0.10, 0.60), grp_wled)

    doc.recompute()

    if LIVE_ITERATION:
        print("[Live] Skipping STEP/STL/FCStd writes for fast iteration.")
        print("[Live] Run manually (Macro) or via freecadcmd for production export.")
        print("==================================================================")
        return

    fcstd_path = os.path.join(script_dir, "GTA_VI_Lightbox.FCStd")
    doc.saveAs(fcstd_path)
    print(f"\n[Saved] Native FreeCAD Document: {fcstd_path}")

    # Export laser-cut layers + text stack to STEP & STL
    export_targets = [
        ("01_Front_Faceplate", faceplate),
        ("02_Neon_Accent_Ring", accent_ring),
        ("03_Relief_Reveal_Plate", reveal),
        ("04_Tree_Relief_Rear", trees_rear),
        ("05_Tree_Relief_Front", trees_front),
        ("06_Text_Face_White", text_face),
        ("07_Text_Backer_Plate", text_backer),
        ("08_Backplate_VESA_Perfs", backplate),
        ("09_Wall_Top", wall_top),
        ("10_Wall_Bottom_Ports", wall_bottom),
        ("11_Wall_Side_x2", wall_side),
        ("12_Diffuser_Plate", diffuser),
        ("13_Spacer_Frame_x2", spacer_shape),
    ]
    for name, shape in export_targets:
        # NOTE: Part.export() only accepts document objects and silently writes
        # header-only files for bare shapes; exportStep() is the shape API.
        shape.exportStep(os.path.join(export_dir, f"{name}.step"))
        mesh = MeshPart.meshFromShape(shape, LinearDeflection=0.1, AngularDeflection=0.35)
        mesh.write(os.path.join(export_dir, f"{name}.stl"))

    print(f"[Exported] Production assets updated in: {export_dir}")
    print("==================================================================")


main()
