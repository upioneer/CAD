#!/usr/bin/env python3
"""
GTA VI WLED Lightbox v4: Negative-VI Backlit Relief Lightbox
Parametric 3D Solid Model, Multi-Layer Laser-Cut Assembly & WLED Cavity

Design intent:
- Front faceplate is 100% clean: full-bleed cap with ONLY the negative "VI"
  aperture. Zero screws, zero holes, zero fasteners on the visible face.
- The "VI" is true negative space: backlit through a deep relief channel
  (faceplate -> neon plate -> tree panel window -> diffuser).
- ONE solid tree panel (4 switchable styles): full sheet with a VI window,
  trees fused across it. Doubles as the glue land for the neon plate.
- Zero spacer frames: diffuser and trees face-glue into one sandwich
  that edge-glues to the walls. Assemble face-down; gravity registers all.
- "grand theft auto" stacks on top as a raised 2-layer badge (white face
  over a one-piece text-shaped backer) glued flush onto the faceplate.

Execution:
  In FreeCAD GUI : src/live/live_gta_vi_lightbox_design1_wled_lightbox.py (live reload), or Macro -> Run
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

# Base joinery: wall bottom tabs drop into backplate edge notches.
BACK_TABS_PER_WALL       = 4
BACK_TAB_W_MM            = 20.0
BACK_JOINT_CLR_MM        = 0.2       # glue gap around base tabs (total)

# Layer stack elevations, back to front. Contiguous sandwich from the
# diffuser up: layers face-glue to neighbors, zero spacer frames.
Z_BACKPLATE              = 0.0       # backplate 0..3.175
Z_DIFFUSER               = 46.525    # diffuser 46.525..49.7 (param size)
Z_TREES                  = 49.7      # tree panel 49.7..52.875 (solid + window)
TREE_STYLE               = "v1"      # visible style: v1 organic (rec.),
                                    # v2 reference, v3 fans, v4 bold
Z_NEON_PLATE             = 52.875    # neon plate 52.875..56.05, glued both sides
FACE_Z_BACK              = 56.05     # faceplate back, flush on neon (no gap)
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
NEON_APERTURE_INSET_MM   = -2.5      # neon window shrunk vs faceplate VI,
                                    # leaving a 2.5mm glowing border in view
NEON_PLATE_CUTBACK_MM    = 12.7      # 0.5in trimmed off W+H vs the faceplate
                                    # (287.3mm plate, 1/8in/side clearance)
TREE_DECIMATE_MM         = 0.3       # RDP tolerance for generated trees (0 = off)
TREE_WINDOW_OVERSIZE_MM  = 2.0       # tree panel window vs exact VI

# Diffuser + slab sizing: None = full drop-in sheet, else explicit size.
# Explicit sizes must still cover the VI aperture (build warns if not).
DIFFUSER_W_MM            = None
DIFFUSER_H_MM            = None
MIN_COVERAGE_W_MM        = 260.0     # VI (238 wide) + margin
MIN_COVERAGE_H_MM        = 210.0     # VI (180 tall) + margin
PANEL_CLR_MM             = 0.5       # drop-in clearance per side

# True during live-watcher iterations (set by src/live/live_core.py);
# production IO (STEP/STL/FCStd writes) is skipped then for fast saves.
LIVE_ITERATION = os.environ.get("FREECAD_LIVE_ITERATION") == "1"

# "grand theft auto" stacked badge: EXACT official wordmark, traced from
# media/gta.svg.webp into text_lockup_vectors.json (see trace_bitmap.py).
# The whole lockup scales uniformly, so letterforms, pitch, and the r/h
# cross-line touch stay pixel-faithful to the reference art. TEXT_LINES /
# TEXT_WIDTHS_MM / TEXT_LINE_PITCH_MM below serve only the legacy font
# fallback path (used when the JSON is missing or USE_TRACED_LOCKUP=False).
TEXT_LINES               = ("grand", "theft", "auto")
TEXT_WIDTHS_MM           = (118.0, 130.0, 108.0)
TEXT_LINE_PITCH_MM       = 54.0
TEXT_LOCKUP_JSON         = "text_lockup_vectors.json"
USE_TRACED_LOCKUP        = True
LOCKUP_WIDTH_MM          = 165.0     # uniform lockup width; area-matched to
                                    # the legacy white faces (same presence)
TEXT_CENTER_X_MM         = 18.0
TEXT_CENTER_Y_MM         = 5.0
TEXT_FACE_T_MM           = 3.175     # 1/8 inch text stock
BACKER_OFFSET_MM         = 7.0       # uniform border hugging the letterforms;
                                    # sized so inter-line bridges stay chunky
SCORE_PLACEMENT          = True      # engrave letter outlines into the backer
                                    # top as laser score guides for gluing
SCORE_WIDTH_MM           = 0.6       # groove width (straddles letter edges)
SCORE_DEPTH_MM           = 0.4       # groove depth into the 3.175 backer top

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


def extrude_face(face, z_lo, z_hi, fudge=True):
    """
    Extrudes a Z=0 planar face into the [z_lo, z_hi] slab. Fudged ends
    (±0.01) help chained fuses overlap; exact ends keep stacked parts
    from micro-interfering across glue planes.
    """
    if fudge:
        solid = face.extrude(Vector(0, 0, (z_hi - z_lo) + 0.02))
        solid.translate(Vector(0, 0, z_lo - 0.01))
    else:
        solid = face.extrude(Vector(0, 0, z_hi - z_lo))
        solid.translate(Vector(0, 0, z_lo))
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


def add_styled_feature(doc, name, shape, color, group=None, trans=0,
                       visible=True):
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
            obj.ViewObject.Visibility = bool(visible)
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


def build_neon_plate(vec_data, z_lo, z_hi):
    """
    Full neon plate behind the aperture (faceplate shrunk 0.5in W+H).
    Its VI window is inset 2.5mm inside the faceplate aperture, so a
    glowing border shows through; the whole back face-glues to the
    tree panel for maximum adhesion.
    """
    w = ENCLOSURE_W_MM - NEON_PLATE_CUTBACK_MM
    h = ENCLOSURE_H_MM - NEON_PLATE_CUTBACK_MM
    plate = Part.makeBox(w, h, z_hi - z_lo, Vector(-w / 2.0, -h / 2.0, z_lo))
    return cut_polys_from_plate(
        plate, vi_polys(vec_data), z_lo, z_hi,
        oversize=NEON_APERTURE_INSET_MM)


def panel_dims():
    """Full-size drop-in panel footprint shared by trees/diffuser/slab."""
    w = ENCLOSURE_W_MM - 2.0 * WALL_THICKNESS_MM - 2.0 * PANEL_CLR_MM
    h = ENCLOSURE_H_MM - 2.0 * WALL_THICKNESS_MM - 2.0 * PANEL_CLR_MM
    return w, h


def build_tree_layer(vec_data, trees, z_lo, z_hi, label):
    """
    Solid tree panel: full sheet with a VI window, trees fused across it.
    Trunk bases and outer fronds overlap the solid border, so the whole
    layer is ONE laser-cut piece with zero floaters. The panel border
    doubles as the glue land for the neon ring sitting directly on top.
    """
    pw, ph = panel_dims()
    plate = Part.makeBox(pw, ph, z_hi - z_lo,
                         Vector(-pw / 2.0, -ph / 2.0, z_lo))
    layer = cut_polys_from_plate(
        plate, vi_polys(vec_data), z_lo, z_hi,
        oversize=TREE_WINDOW_OVERSIZE_MM)

    # 3D union, grouped: each tree's parts fuse small (well-conditioned),
    # then trees join the panel. 2D face fuses fragment instead of
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

    for ti, spec in enumerate(trees):
        parts = [extrude_face(pts_to_face(decimate_closed(p, TREE_DECIMATE_MM)),
                              z_lo, z_hi, fudge=False)
                 for p in palm_trees.tree_polys(spec)]
        tree = _union_3d(parts, f"tree{ti}")
        layer = _union_3d([layer, tree], f"panel+tree{ti}")
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


def _signed_area_xy(pts):
    """Shoelace area of [(x, y)]; positive = CCW in y-up CAD coords."""
    return sum(p[0] * pts[(i + 1) % len(pts)][1]
               - pts[(i + 1) % len(pts)][0] * p[1]
               for i, p in enumerate(pts)) / 2.0


def _lockup_faces(script_dir):
    """
    Loads the traced wordmark JSON into per-region Part.Faces (with counter
    holes), uniformly scaled to LOCKUP_WIDTH_MM, y-flipped (art is y-down),
    and centered on (TEXT_CENTER_X_MM, TEXT_CENTER_Y_MM). Outer wires are
    forced CCW, holes CW, so faces build regardless of trace winding.
    """
    with open(os.path.join(script_dir, TEXT_LOCKUP_JSON), encoding="utf-8") as f:
        data = json.load(f)
    x0, y0, x1, y1 = data["bbox"]
    s = LOCKUP_WIDTH_MM / (x1 - x0)
    cx_px, cy_px = (x0 + x1) / 2.0, (y0 + y1) / 2.0

    def conv(pt):
        return (TEXT_CENTER_X_MM + (pt[0] - cx_px) * s,
                TEXT_CENTER_Y_MM - (pt[1] - cy_px) * s)

    faces = []
    for reg in data["regions"]:
        outer = [conv(p) for p in reg["outer"]]
        if _signed_area_xy(outer) < 0:
            outer = outer[::-1]
        hwires = []
        for h in reg["holes"]:
            hp = [conv(p) for p in h]
            if _signed_area_xy(hp) > 0:
                hp = hp[::-1]
            hv = [Vector(x, y, 0.0) for x, y in hp]
            hv.append(hv[0])
            hwires.append(Part.makePolygon(hv))
        ov = [Vector(x, y, 0.0) for x, y in outer]
        ov.append(ov[0])
        face = Part.Face([Part.makePolygon(ov)] + hwires)
        if face.Area < 1.0:
            raise ValueError("degenerate lockup region")
        faces.append(face)
    if not faces:
        raise ValueError("no regions in lockup JSON")
    return faces


def _loop_is_phantom(solid, pts, z, eps=0.3):
    """
    True when a section loop is an internal fuse seam, not a boundary:
    solid material on BOTH sides at 2+ of 3 sample stations. Real
    boundaries (outer or hole) have void on one side. Untestable loops
    are kept: never drop a path blind.
    """
    n = len(pts)
    both_solid = 0
    for k in (n // 4, n // 2, 3 * n // 4):
        a, b = pts[k % n], pts[(k + 1) % n]
        mx, my = (a.x + b.x) / 2.0, (a.y + b.y) / 2.0
        dx, dy = b.x - a.x, b.y - a.y
        norm = (dx * dx + dy * dy) ** 0.5 or 1.0
        nx, ny = -dy / norm * eps, dx / norm * eps
        try:
            s1 = solid.isInside(Vector(mx + nx, my + ny, z), 0.01, True)
            s2 = solid.isInside(Vector(mx - nx, my - ny, z), 0.01, True)
        except Exception:
            return False
        if s1 and s2:
            both_solid += 1
    return both_solid >= 2


def _chain_section_loops(edges, solid=None, z=None):
    """
    Chains unordered planar section edges into closed loops. Returns a list
    of point lists (FreeCAD Vectors, CAD coords). Straight runs collapse to
    endpoints via deflection-based discretization. When the source solid is
    given, phantom loops from internal fuse seams are classified out.
    """
    def key(p):
        return (round(p.x, 3), round(p.y, 3))

    links = []
    touch = {}
    for e in edges:
        vs = e.Vertexes
        if len(vs) < 2:
            continue
        a, b = key(vs[0].Point), key(vs[-1].Point)
        links.append((a, b, e))
        touch.setdefault(a, []).append(len(links) - 1)
        touch.setdefault(b, []).append(len(links) - 1)
    used = bytearray(len(links))
    loops = []
    for i, (a, b, e) in enumerate(links):
        if used[i]:
            continue
        used[i] = 1
        chain = [(e, True)]
        end = b
        while True:
            nxt = None
            for j in touch.get(end, ()):
                if not used[j]:
                    nxt = j
                    break
            if nxt is None:
                break
            used[nxt] = 1
            na, nb, ne = links[nxt]
            fwd = (na == end)
            chain.append((ne, fwd))
            end = nb if fwd else na
        pts = []
        for ce, fwd in chain:
            dpts = list(ce.discretize(QuasiDeflection=0.05))
            if not fwd:
                dpts.reverse()
            for p in dpts:
                if not pts or (p - pts[-1]).Length > 1e-6:
                    pts.append(p)
        if len(pts) >= 3:
            if solid is not None and z is not None \
                    and _loop_is_phantom(solid, pts, z):
                continue
            loops.append(pts)
    return loops


def write_backer_laser_svg(path, laser2d, backer_shape):
    """
    Laser-ready 2D file for the backer plate: CUT outline (black) plus
    letter placement SCORE paths (red). LightBurn maps stroke colors to
    layers: run black as cut, red as low-power score/engrave.
    Coords are backer-local mm, origin at the lower-left of the plate bbox.
    Returns the path written, or None if a layer is missing.
    """
    if not laser2d["cut"] or not laser2d["score"]:
        print("[!] Warning: laser SVG skipped (missing layer)")
        return None
    bb = backer_shape.BoundBox
    x0, y1 = bb.XMin, bb.YMax

    def path_of_points(pts):
        d = ("M " + " L ".join(f"{p.x - x0:.3f},{y1 - p.y:.3f}" for p in pts)
             + " Z")
        return f'<path d="{d}"/>'

    def path_of_wire(wire, n=600):
        return path_of_points(list(wire.discretize(Number=n)))

    w, h = bb.XLength, bb.YLength
    cut_paths = "\n    ".join(path_of_points(pts) for pts in laser2d["cut"])
    score_paths = "\n    ".join(path_of_wire(w) for w in laser2d["score"])
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w:.3f}mm" height="{h:.3f}mm" viewBox="0 0 {w:.3f} {h:.3f}">
  <title>Text backer plate: CUT (black) + SCORE placement (red)</title>
  <desc>Run black as cut, red as low-power score. Units are mm, origin at lower-left of the plate bbox.</desc>
  <g id="CUT" fill="none" stroke="#000000" stroke-width="0.1">
    {cut_paths}
  </g>
  <g id="SCORE" fill="none" stroke="#FF0000" stroke-width="0.1">
    {score_paths}
  </g>
</svg>
'''
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"[Laser] wrote {path}")
    return path


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
    Primary source is the traced official wordmark (text_lockup_vectors.json);
    falls back to font ShapeStrings, then to block letters.
    The backer glues flush onto the faceplate (no mounting tabs).
    Returns (face_solid, backer_solid, laser2d) where laser2d holds the
    2D outline wires for the laser file: {"cut": [...], "score": [...]}.
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
    traced = False
    if USE_TRACED_LOCKUP:
        try:
            faces = _lockup_faces(_THIS_DIR)
            traced = True
            print(f"[OK] Text badge traced from {TEXT_LOCKUP_JSON} "
                  f"({len(faces)} regions)")
        except Exception as err:
            print(f"[!] Warning: lockup JSON failed ({err}); font path used.")
            faces = []
    if not faces and font_file is not None:
        try:
            for line, target_w, cy in zip(TEXT_LINES, TEXT_WIDTHS_MM, line_cys):
                faces.append(_shapestring_line(
                    doc, line, target_w, TEXT_CENTER_X_MM, cy, font_file
                ))
            print(f"[OK] Text badge lettered with {os.path.basename(font_file)}")
        except Exception as err:
            print(f"[!] Warning: ShapeString failed ({err}); block fallback used.")
            faces = []
    if not faces and font_file is None:
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

    # Inter-line bridge estimate (font/block paths only; the traced lockup
    # is one pre-fitted unit whose merges the pocket-fill pass guarantees).
    if not traced:
        _lines = list(zip(TEXT_LINES, faces, line_cys))
        for (la, fa, ca), (lb, fb, cb) in zip(_lines, _lines[1:]):
            bridge = 2.0 * BACKER_OFFSET_MM + (
                fa.BoundBox.YLength + fb.BoundBox.YLength) / 2.0 - abs(ca - cb)
            print(f"[Text] bridge {la}/{lb}: {bridge:.1f}mm")
            if bridge < 3.0:
                print(f"[!] {la}/{lb} bridge thin ({bridge:.1f}mm); "
                      f"raise BACKER_OFFSET_MM or cut TEXT_LINE_PITCH_MM")

    z_face_lo = Z_TEXT_FACE + explode_lift
    z_face_hi = z_face_lo + TEXT_FACE_T_MM
    face_solid = _fuse_all([extrude_face(f, z_face_lo, z_face_hi, fudge=False)
                            for f in faces])

    # One-piece backer: TRUE outward offset of every glyph outline, fused.
    # Offsets (never scales) give a uniform border hugging the letterforms;
    # inflated neighbors merge into a single text-shaped plaque. Holes are
    # dropped (outer wires only) so counters back solid black.
    inflated = []
    score_outlines = []  # exact letter outlines: groove centerlines + score layer
    n_glyphs = n_offset_ok = 0
    tags = TEXT_LINES if len(faces) == len(TEXT_LINES) else [
        f"art{i}" for i in range(len(faces))]
    for line, f in zip(tags, faces):
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
            score_outlines.append(outline)
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
                fudge=False,
            ))
    print(f"[Text] backer offsets ok: {n_offset_ok}/{n_glyphs}")
    backer_solid = _fuse_all(inflated)
    # Heal trapped fusion pockets: inflated neighbors can enclose small
    # voids (e.g. a ~19mm pocket between grand/theft at 7mm offset) that
    # would laser-cut as stray interior holes. Fill any solid region that
    # is inside the backer bbox but outside the fused backer, so the plaque
    # stays one solid text silhouette (counters still back solid black).
    # Iterates to a fixpoint: fusing a filler can strand a new sliver.
    try:
        for _pass in range(3):
            bb = backer_solid.BoundBox
            z_lo = Z_TEXT_BACKER + explode_lift
            bbox_box = Part.makeBox(
                bb.XLength, bb.YLength, SHEET_THICKNESS_MM,
                Vector(bb.XMin, bb.YMin, z_lo),
            )
            outside = bbox_box.cut(backer_solid)
            pockets = [
                s for s in outside.Solids
                if s.Volume > 0.1
                and s.BoundBox.XMin > bb.XMin + 1.0
                and s.BoundBox.XMax < bb.XMax - 1.0
                and s.BoundBox.YMin > bb.YMin + 1.0
                and s.BoundBox.YMax < bb.YMax - 1.0
            ]
            if not pockets:
                print("[Text] no trapped pockets found"
                      if _pass == 0 else "[Text] pockets healed")
                break
            print(f"[Text] pass {_pass + 1}: filling "
                  f"{len(pockets)} trapped pocket(s): "
                  f"{['%.1fmm3' % s.Volume for s in pockets]}")
            for p in pockets:
                # Dilate the filler so the fuse overlaps the void walls:
                # exact-fit fillers can leave hairline slots behind. Clip
                # back to the plate slab so dilation can't nub above/below.
                try:
                    p = p.makeOffsetShape(0.15, 0.01).common(bbox_box)
                except Exception:
                    pass
                backer_solid = backer_solid.fuse(p)
        else:
            print("[!] Warning: backer voids remain after 3 fill passes; "
                  "inspect before cutting!")
    except Exception as err:
        print(f"[!] Warning: pocket fill skipped ({err})")
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

    # Score grooves: shallow outline channels in the backer top so the
    # laser burns letter placement guides and each white letter gets a
    # visible seat. Grooves straddle the letter edges; the outer 0.3mm
    # reads as a deliberate keyline that proves alignment at a glance.
    if SCORE_PLACEMENT and score_outlines:
        try:
            z_top = Z_TEXT_BACKER + SHEET_THICKNESS_MM + explode_lift
            cutters = []
            n_groove_ok = 0
            for outline in score_outlines:
                try:
                    band = outline.makeOffset2D(SCORE_WIDTH_MM / 2.0)
                    core = outline.makeOffset2D(-SCORE_WIDTH_MM / 2.0)
                except Exception:
                    band = _offset_polygon_fallback(
                        outline, SCORE_WIDTH_MM / 2.0)
                    core = _offset_polygon_fallback(
                        outline, -SCORE_WIDTH_MM / 2.0)
                ring = band.cut(core)
                if ring.Area < 1.0:
                    continue
                cutters.append(extrude_face(
                    ring, z_top - SCORE_DEPTH_MM, z_top, fudge=False))
                n_groove_ok += 1
            if cutters:
                vol_before = backer_solid.Volume
                backer_solid = backer_solid.cut(_fuse_all(cutters))
                print(f"[Text] score grooves cut: {n_groove_ok}/"
                      f"{len(score_outlines)} "
                      f"({(vol_before - backer_solid.Volume):.0f}mm3)")
        except Exception as err:
            print(f"[!] Warning: score grooves skipped ({err})")

    # Laser cut layer: section the finished 3D backer at mid-thickness and
    # chain the edges into loops. The section sees pocket-fill, spine, and
    # grooves exactly as built (grooves are above the section plane), so the
    # cut paths always match the solid. Any loop beyond the first would be a
    # real void that must be cut too, hence every loop is emitted.
    laser2d = {"cut": [], "score": [o.OuterWire for o in score_outlines]}
    try:
        zmid = Z_TEXT_BACKER + SHEET_THICKNESS_MM / 2.0 + explode_lift
        sec = backer_solid.section(
            Part.Plane(Vector(0, 0, zmid), Vector(0, 0, 1)))
        laser2d["cut"] = _chain_section_loops(
            sec.Edges, backer_solid, zmid)
        print(f"[Text] laser layers: cut={len(laser2d['cut'])} "
              f"score={len(laser2d['score'])} loops")
        if len(laser2d["cut"]) != 1:
            print("[!] Warning: backer cut layer is not one loop; inspect!")
    except Exception as err:
        print(f"[!] Warning: laser cut layer failed ({err})")

    return face_solid, backer_solid, laser2d


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
    grp_optics = doc.addObject("App::DocumentObjectGroup", "03_Optics")
    grp_chassis = doc.addObject("App::DocumentObjectGroup", "04_Enclosure_Chassis")
    grp_wled   = doc.addObject("App::DocumentObjectGroup", "05_WLED_Electronics")

    gap = EXPLODE_GAP_MM if EXPLODE_VIEW else 0.0
    lift_diffuser = gap * 1.0
    lift_trees    = gap * 1.7
    lift_ring     = gap * 2.6
    lift_face     = gap * 3.2
    lift_text     = gap * 4.2

    print("==================================================================")
    print("GTA VI WLED Lightbox v4: Solid-Panel Stack, Zero Spacers")
    print(f"Bed Envelope Check: {ENCLOSURE_W_MM}mm x {ENCLOSURE_H_MM}mm (xTool S1 OK)")
    print(f"Display Mode      : {'EXPLODED 3D VIEW' if EXPLODE_VIEW else 'ASSEMBLED PRODUCTION'}")
    print("==================================================================")

    # ------------------------------------------------------------------
    # 1. FRONT RELIEF STACK (faceplate -> ring -> tree panel)
    # ------------------------------------------------------------------
    faceplate = build_front_faceplate(
        vec_data, FACE_Z_BACK + lift_face, FACE_Z_FRONT + lift_face)
    neon_plate = build_neon_plate(
        vec_data, Z_NEON_PLATE + lift_ring,
        Z_NEON_PLATE + SHEET_THICKNESS_MM + lift_ring)
    # One tree layer, three styles. Only TREE_STYLE is visible; flip
    # visibility in the tree view (or change TREE_STYLE) to compare.
    tree_names = {"v1": "Tree_V1_Organic", "v2": "Tree_V2_Reference",
                  "v3": "Tree_V3_Fans", "v4": "Tree_V4_Bold"}
    tree_colors = {"v1": (0.13, 0.15, 0.13), "v2": (0.16, 0.17, 0.22),
                   "v3": (0.13, 0.13, 0.16), "v4": (0.19, 0.16, 0.13)}
    tree_solids = {}
    for key in sorted(palm_trees.STYLES):
        tree_solids[key] = build_tree_layer(
            vec_data, palm_trees.STYLES[key], Z_TREES + lift_trees,
            Z_TREES + SHEET_THICKNESS_MM + lift_trees, key)

    add_styled_feature(doc, "Front_Faceplate", faceplate, (0.10, 0.10, 0.12), grp_relief)
    add_styled_feature(doc, "Neon_Plate", neon_plate, (0.95, 0.05, 0.55), grp_relief)
    for key in sorted(tree_solids):
        add_styled_feature(doc, tree_names[key], tree_solids[key],
                           tree_colors[key], grp_relief,
                           visible=(key == TREE_STYLE))

    # ------------------------------------------------------------------
    # 2. RAISED TEXT BADGE + CLEAR TABS
    # ------------------------------------------------------------------
    text_face, text_backer, text_laser2d = build_text_badge(doc, lift_text)

    add_styled_feature(doc, "Text_Face_White", text_face, (0.96, 0.96, 0.97), grp_text)
    add_styled_feature(doc, "Text_Backer_Plate", text_backer, (0.08, 0.08, 0.10), grp_text)

    # ------------------------------------------------------------------
    # 3. OPTICS (diffuser panel, adhesion-mounted, zero spacers)
    # ------------------------------------------------------------------
    full_w, full_h = panel_dims()
    diff_w = DIFFUSER_W_MM or full_w
    diff_h = DIFFUSER_H_MM or full_h
    if diff_w < MIN_COVERAGE_W_MM or diff_h < MIN_COVERAGE_H_MM:
        print(f"[!] Diffuser {diff_w:g}x{diff_h:g} does NOT cover the VI "
              f"(needs {MIN_COVERAGE_W_MM:g}x{MIN_COVERAGE_H_MM:g}); "
              f"aperture corners will show bare LEDs!")
    diff_trans = 50 if DIFFUSER_TRANSPARENT else 0
    diffuser = Part.makeBox(
        diff_w, diff_h, DIFFUSER_THICK_MM,
        Vector(-diff_w / 2.0, -diff_h / 2.0, Z_DIFFUSER + lift_diffuser),
    )
    add_styled_feature(doc, "Optical_Diffuser_Panel", diffuser,
                       (0.92, 0.95, 0.98), grp_optics, trans=diff_trans)
    # NOTE: zero spacer frames in the v4 stack. The diffuser and tree
    # panel face-glue into one sandwich that edge-glues to the walls;
    # assemble face-down so gravity registers every layer while glue cures.

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

    # Stack-plane interference: neighbors must touch, never overlap.
    _active_trees = tree_solids[TREE_STYLE]
    for an, bn, sa, sb in (
            ("Neon", "Trees", neon_plate, _active_trees),
            ("Trees", "Diffuser", _active_trees, diffuser),
            ("Neon", "Faceplate", neon_plate, faceplate),
            ("Faceplate", "Wall_Top", faceplate, wall_top),
            ("TextBacker", "Faceplate", text_backer, faceplate)):
        overlap = sa.common(sb).Volume
        if overlap > 0.5:
            print(f"[!] {an}-{bn} OVERLAP: {overlap:.1f} mm3")
        else:
            print(f"[OK] {an}-{bn} stack fit ({overlap:.3f} mm3)")

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
    # (03 retired with the reveal plate; numbers stay stable from here on.)
    export_targets = [
        ("01_Front_Faceplate", faceplate),
        ("02_Neon_Plate", neon_plate),
        ("04a_Tree_V1_Organic", tree_solids["v1"]),
        ("04b_Tree_V2_Reference", tree_solids["v2"]),
        ("04c_Tree_V3_Fans", tree_solids["v3"]),
        ("04d_Tree_V4_Bold", tree_solids["v4"]),
        ("05_Text_Face_White", text_face),
        ("06_Text_Backer_Plate", text_backer),
        ("07_Backplate_VESA_Perfs", backplate),
        ("08_Wall_Top", wall_top),
        ("09_Wall_Bottom_Ports", wall_bottom),
        ("10_Wall_Side_x2", wall_side),
        ("11_Diffuser_Plate", diffuser),
    ]
    for name, shape in export_targets:
        # NOTE: Part.export() only accepts document objects and silently writes
        # header-only files for bare shapes; exportStep() is the shape API.
        shape.exportStep(os.path.join(export_dir, f"{name}.step"))
        mesh = MeshPart.meshFromShape(shape, LinearDeflection=0.1, AngularDeflection=0.35)
        mesh.write(os.path.join(export_dir, f"{name}.stl"))

    # Laser-ready backer file: cut outline + score placement in one job.
    try:
        write_backer_laser_svg(
            os.path.join(export_dir, "06_Text_Backer_Plate_laser.svg"),
            text_laser2d, text_backer)
    except Exception as err:
        print(f"[!] Warning: laser SVG failed ({err})")

    print(f"[Exported] Production assets updated in: {export_dir}")
    print("==================================================================")


main()
