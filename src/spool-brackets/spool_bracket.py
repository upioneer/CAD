#!/usr/bin/env python3
"""
8ft Maker Station: Parametric 3D Printable Spool Brackets
FreeCAD Automation & Export Script

Generates high-strength, support-free 3D printable brackets to hold
modular 3/4" EMT steel conduit spool rods on the 8ft Maker Station.

Execute within FreeCAD GUI (Macro -> Run) or headless via FreeCADCmd:
    freecadcmd spool_bracket.py
"""

import sys
import os

try:
    import FreeCAD
    import Part
    import MeshPart
    from FreeCAD import Vector, Rotation, Placement
except ImportError:
    print("FreeCAD Python modules not found in current environment.")
    print("Run this script within FreeCAD GUI or via FreeCADCmd.")
    sys.exit(0)

# ==============================================================================
# PARAMETRIC SPECIFICATIONS (Millimeters)
# ==============================================================================

# 3/4" EMT Steel Conduit: OD = 0.922 in = 23.42 mm
CONDUIT_OD_NOMINAL_MM   = 23.42
CONDUIT_CLEARANCE_MM    = 0.78                       # +0.78mm diametral slip-fit clearance
CONDUIT_BORE_RADIUS_MM  = (CONDUIT_OD_NOMINAL_MM + CONDUIT_CLEARANCE_MM) / 2.0  # 12.10 mm

# Cantilever Geometry
# Upright 2x4 post front face is at Y = 27.0 in; Spool centerline is at Y = 21.0 in
# Forward projection delta = 6.0 inches = 152.4 mm
CANTILEVER_ARM_LEN_MM   = 152.4                      # 6.0 inches

# Structural Dimensions
BRACKET_WIDTH_MM        = 36.0                       # 36mm uniform width (prints 100% flat on its side)
FLANGE_THICKNESS_MM     = 10.0                       # Base flange thickness against wood post
MOUNT_Z_TOP_MM          = 30.0                       # Upper mounting flange height
MOUNT_Z_BOT_MM          = -75.0                      # Lower gusset attachment depth (total span 105mm)
CRADLE_WALL_THICK_MM    = 6.0                        # Solid wall thickness surrounding conduit bore
CRADLE_HEAD_TOP_Z_MM    = 20.0                       # Cradle top opening elevation
CRADLE_HEAD_BOT_Z_MM    = -14.0                      # Cradle bottom reinforcement

# Fastener Geometry
SCREW_HOLE_DIA_MM       = 5.2                        # Clearance for #9 / #10 construction screws (M5)
SCREW_CBORE_DIA_MM      = 10.5                       # Counterbore diameter for screw head
SCREW_CBORE_DEPTH_MM    = 5.0                        # Counterbore depth
PIN_HOLE_DIA_MM         = 5.2                        # Transverse retaining linchpin / M5 cross-bolt

# Conduit Stopper Collar
COLLAR_ID_MM            = 23.8                       # Slip fit over conduit
COLLAR_OD_MM            = 36.0                       # Outer collar diameter
COLLAR_WIDTH_MM         = 16.0                       # Collar width along pipe
COLLAR_CLAMP_BOLT_DIA   = 4.3                        # M4 clearance hole


# ==============================================================================
# SOLID GENERATION FUNCTIONS
# ==============================================================================

def make_spool_bracket(bracket_type="center", with_truss_pocket=True):
    """
    Constructs a solid B-Rep bracket geometry.
    bracket_type:
      - 'center': Open U-channel pass-through cradle for 2 butting rods or 1 continuous rod.
      - 'end_left': Integrated 4mm solid stop wall on the left side (prevents left sliding).
      - 'end_right': Integrated 4mm solid stop wall on the right side (prevents right sliding).
    """
    conduit_r    = CONDUIT_BORE_RADIUS_MM
    cradle_y     = CANTILEVER_ARM_LEN_MM
    arm_w        = BRACKET_WIDTH_MM
    flange_t     = FLANGE_THICKNESS_MM
    z_top        = MOUNT_Z_TOP_MM
    z_bot        = MOUNT_Z_BOT_MM
    c_bot_z      = CRADLE_HEAD_BOT_Z_MM
    c_top_z      = CRADLE_HEAD_TOP_Z_MM
    c_y_min      = cradle_y - conduit_r - CRADLE_WALL_THICK_MM
    c_y_max      = cradle_y + conduit_r + CRADLE_WALL_THICK_MM

    # 1. Main Structural 2D Profile in the Y-Z plane
    profile_pts = [
        Vector(0, 0, z_bot),
        Vector(0, c_y_min, c_bot_z),
        Vector(0, c_y_max, c_bot_z),
        Vector(0, c_y_max, c_top_z),
        Vector(0, c_y_min, c_top_z),
        Vector(0, flange_t, z_top),
        Vector(0, 0, z_top),
        Vector(0, 0, z_bot)
    ]
    wire = Part.makePolygon(profile_pts)
    face = Part.Face(wire)
    body = face.extrude(Vector(arm_w, 0, 0))

    # Center body at X = 0
    body.translate(Vector(-arm_w / 2.0, 0, 0))

    # 2. Triangular Truss Weight-Saving Pocket (Saves plastic, prints faster, acts like an I-beam)
    if with_truss_pocket:
        pocket_pts = [
            Vector(0, flange_t + 10.0, z_bot + 20.0),
            Vector(0, c_y_min - 8.0, c_bot_z + 8.0),
            Vector(0, flange_t + 10.0, z_top - 18.0),
            Vector(0, flange_t + 10.0, z_bot + 20.0)
        ]
        p_wire = Part.makePolygon(pocket_pts)
        p_face = Part.Face(p_wire)
        p_solid = p_face.extrude(Vector(arm_w + 4.0, 0, 0))
        p_solid.translate(Vector(-arm_w / 2.0 - 2.0, 0, 0))
        body = body.cut(p_solid)

    # 3. Conduit Cradle U-Channel Cut
    cut_x_min = -arm_w / 2.0 - 2.0
    cut_len   = arm_w + 4.0

    if bracket_type == "end_left":
        cut_x_min = -arm_w / 2.0 + 4.0       # 4.0mm solid end stop wall on left
        cut_len   = arm_w + 2.0
    elif bracket_type == "end_right":
        cut_x_min = -arm_w / 2.0 - 2.0
        cut_len   = arm_w - 4.0 + 2.0        # 4.0mm solid end stop wall on right

    cradle_cyl = Part.makeCylinder(conduit_r, cut_len, Vector(cut_x_min, cradle_y, 0), Vector(1, 0, 0))
    cradle_slot = Part.makeBox(cut_len, 2 * conduit_r, c_top_z + 5.0, Vector(cut_x_min, cradle_y - conduit_r, 0))
    cradle_cutter = cradle_cyl.fuse(cradle_slot)
    body = body.cut(cradle_cutter)

    # Flared entry chamfers on cradle top lip (facilitates one-handed pipe insertion)
    chamfer_l = Part.makeBox(cut_len, 3.0, 3.0, Vector(cut_x_min, cradle_y - conduit_r - 1.5, c_top_z - 1.5))
    chamfer_r = Part.makeBox(cut_len, 3.0, 3.0, Vector(cut_x_min, cradle_y + conduit_r - 1.5, c_top_z - 1.5))
    # Rotate chamfer boxes 45 degrees
    chamfer_l.rotate(Vector(cut_x_min, cradle_y - conduit_r, c_top_z), Vector(1, 0, 0), 45)
    chamfer_r.rotate(Vector(cut_x_min, cradle_y + conduit_r, c_top_z), Vector(1, 0, 0), 45)
    body = body.cut(chamfer_l).cut(chamfer_r)

    # 4. Centerline Wood Screw Mounting Holes (3 vertical holes)
    screw_r = SCREW_HOLE_DIA_MM / 2.0
    cbore_r = SCREW_CBORE_DIA_MM / 2.0
    for hz in [16.0, -22.0, -60.0]:
        screw_cyl = Part.makeCylinder(screw_r, flange_t + 4.0, Vector(0, -2.0, hz), Vector(0, 1, 0))
        cbore_cyl = Part.makeCylinder(cbore_r, flange_t, Vector(0, flange_t - SCREW_CBORE_DEPTH_MM, hz), Vector(0, 1, 0))
        body = body.cut(screw_cyl).cut(cbore_cyl)

    # 5. Transverse Linchpin / Retaining Cross-Bolt Hole (5.2mm at Z = 14mm above conduit center)
    pin_r = PIN_HOLE_DIA_MM / 2.0
    pin_hole = Part.makeCylinder(pin_r, arm_w + 4.0, Vector(-arm_w / 2.0 - 2.0, cradle_y, 14.0), Vector(1, 0, 0))
    body = body.cut(pin_hole)

    return body


def make_spool_collar():
    """
    Constructs a clamp-on conduit collar with an M4 clamping bolt and hex nut pocket.
    Clamps onto 3/4" EMT conduit anywhere along the span to prevent spools from drifting.
    """
    r_in    = COLLAR_ID_MM / 2.0
    r_out   = COLLAR_OD_MM / 2.0
    h       = COLLAR_WIDTH_MM
    ear_w   = 14.0
    ear_len = 16.0

    # Base ring body with clamping ear boss
    cyl_out = Part.makeCylinder(r_out, h, Vector(0, 0, 0), Vector(0, 0, 1))
    ear_box = Part.makeBox(ear_w, ear_len, h, Vector(-ear_w / 2.0, r_out - 4.0, 0))
    collar_body = cyl_out.fuse(ear_box)

    # Center conduit bore
    bore = Part.makeCylinder(r_in, h + 4.0, Vector(0, 0, -2.0), Vector(0, 0, 1))
    collar_body = collar_body.cut(bore)

    # Clamping expansion slit (2.0mm wide)
    slit = Part.makeBox(2.0, ear_len + 12.0, h + 4.0, Vector(-1.0, 0, -2.0))
    collar_body = collar_body.cut(slit)

    # Clamping bolt hole (M4 through ear)
    bolt_z = h / 2.0
    bolt_y = r_out + 6.0
    bolt_hole = Part.makeCylinder(COLLAR_CLAMP_BOLT_DIA / 2.0, ear_w + 4.0, Vector(-ear_w / 2.0 - 2.0, bolt_y, bolt_z), Vector(1, 0, 0))
    cbore = Part.makeCylinder(4.2, 5.0, Vector(-ear_w / 2.0 - 2.0, bolt_y, bolt_z), Vector(1, 0, 0))
    nut_pocket = Part.makeCylinder(4.5, 5.0, Vector(ear_w / 2.0 - 3.5, bolt_y, bolt_z), Vector(1, 0, 0))

    collar_body = collar_body.cut(bolt_hole).cut(cbore).cut(nut_pocket)
    return collar_body


# ==============================================================================
# MAIN EXECUTION & MULTI-FORMAT EXPORT
# ==============================================================================

def main():
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        script_dir = r"C:\dev\Projects\CAD\src\spool-brackets"

    export_dir = os.path.join(script_dir, "exports")
    os.makedirs(export_dir, exist_ok=True)

    doc_name = "MakerStation_SpoolBrackets"
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

    parts_dict = {
        "spool_bracket_center": make_spool_bracket("center"),
        "spool_bracket_end_left": make_spool_bracket("end_left"),
        "spool_bracket_end_right": make_spool_bracket("end_right"),
        "spool_stopper_collar": make_spool_collar()
    }

    print("==================================================================")
    print("8ft Maker Station: Spool Bracket Solid Generation & DFM Verification")
    print("==================================================================")

    for name, shape in parts_dict.items():
        if not shape.isValid():
            print(f"WARNING: Shape {name} has geometric faults!")
        else:
            vol_cm3 = round(shape.Volume / 1000.0, 2)
            print(f"[OK] {name:<25}: Solid Manifold | Volume: {vol_cm3:>6.2f} cm3")

        # Add to FreeCAD document
        obj = doc.addObject("Part::Feature", name)
        obj.Shape = shape

        # Export STEP (High precision B-Rep)
        # NOTE: Part.export() only accepts document objects and silently writes
        # header-only files for bare shapes; exportStep() is the shape API.
        step_path = os.path.join(export_dir, f"{name}.step")
        shape.exportStep(step_path)

        # Export STL (High resolution mesh for 3D slicing)
        stl_path = os.path.join(export_dir, f"{name}.stl")
        mesh = MeshPart.meshFromShape(
            Shape=shape,
            LinearDeflection=0.05,
            AngularDeflection=0.261799  # ~15 degrees
        )
        mesh.write(stl_path)

    doc.recompute()
    print(f"\nAll STEP and STL assets successfully written to:\n{export_dir}")
    print("==================================================================")


main()

