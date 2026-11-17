#!/usr/bin/env python3
"""
8ft Maker Station: Multi-Tier 3D Printer and Soldering Workbench
Parametric FreeCAD Automation Script
Updated: Short-Ways Orientation for Front & Rear Posts (3.5" in X, 1.5" in Y)
Zero Collisions Across All Joints + Dual-Tier Above-Gantry Spool Pipes

Execute within FreeCAD (Macro -> Macros... -> Execute) or via FreeCADCmd:
    freecadcmd workbench_freecad.py
"""

import sys
import os

try:
    import FreeCAD
    import Part
    from FreeCAD import Vector, Rotation, Placement
except ImportError:
    print("FreeCAD Python modules not found in current environment.")
    print("Run this script within FreeCAD or via FreeCADCmd.")
    sys.exit(0)

# ==========================================
# PARAMETRIC SPECIFICATIONS (Inches)
# ==========================================

INCH_TO_MM = 25.4

TOTAL_WIDTH_IN       = 96.0
TOTAL_DEPTH_IN       = 30.0
DESK_HEIGHT_IN       = 30.0

LUMBER_T_IN          = 1.5   # 2x4 thickness (1-1/2 in) - depth along Y
LUMBER_W_IN          = 3.5   # 2x4 width (3-1/2 in) - width along X
PLYWOOD_T_IN         = 0.75  # 3/4" Baltic birch / sanded plywood

# Upper Shelf Geometry (78.0" frame, 78.75" finished top)
UPPER_SHELF_DEPTH_IN = 18.0
UPPER_SHELF_TOP_Z_IN = 78.75
UPPER_SHELF_FRAME_IN = UPPER_SHELF_TOP_Z_IN - PLYWOOD_T_IN    # 78.0 in (Uprights flush cut here)
UPPER_RAIL_BOT_Z_IN  = UPPER_SHELF_FRAME_IN - LUMBER_W_IN     # 74.5 in

UPRIGHT_HEIGHT_IN    = UPPER_SHELF_FRAME_IN                   # 78.0 in

# Derived Elevations (Inches)
FRAME_TOP_Z_IN       = DESK_HEIGHT_IN - PLYWOOD_T_IN          # 29.25 in
FRAME_RAIL_BOT_Z_IN  = FRAME_TOP_Z_IN - LUMBER_W_IN           # 25.75 in
BOTTOM_RAIL_Z_IN     = 3.5                                    # 3.5 in
BOTTOM_SLAT_Z_IN     = BOTTOM_RAIL_Z_IN + LUMBER_W_IN         # 7.0 in

# Dual-Tier Modular Spool Conduit Configuration (3/4" EMT Steel Conduit)
# Neptune 3 Max Gantry Top is at Z = 59.5 in (Desk 30.0" + Gantry 29.5")
SPOOL_ROD_DIA_IN     = 0.92
SPOOL_ROD_Y_IN       = 21.0                                   # Drops directly into top runout sensor
SPOOL_Z_ROW1_IN      = 63.5                                   # Row 1: 4.0" ABOVE gantry top
SPOOL_Z_ROW2_IN      = 71.0                                   # Row 2: 11.5" ABOVE gantry top
SPOOL_ROD_LEN_IN     = 48.0                                   # 4 ft modular rod
SPOOL_BAY_MODE       = "left_dual"                            # "left_dual", "right_dual", "all_dual"

# Convert to FreeCAD mm
TOTAL_WIDTH          = TOTAL_WIDTH_IN * INCH_TO_MM
TOTAL_DEPTH          = TOTAL_DEPTH_IN * INCH_TO_MM
LUMBER_T             = LUMBER_T_IN * INCH_TO_MM
LUMBER_W             = LUMBER_W_IN * INCH_TO_MM
PLYWOOD_T            = PLYWOOD_T_IN * INCH_TO_MM
UPPER_SHELF_DEPTH    = UPPER_SHELF_DEPTH_IN * INCH_TO_MM
UPRIGHT_HEIGHT       = UPRIGHT_HEIGHT_IN * INCH_TO_MM

FRAME_TOP_Z          = FRAME_TOP_Z_IN * INCH_TO_MM
FRAME_RAIL_BOT_Z     = FRAME_RAIL_BOT_Z_IN * INCH_TO_MM
BOTTOM_RAIL_Z        = BOTTOM_RAIL_Z_IN * INCH_TO_MM
BOTTOM_SLAT_Z        = BOTTOM_SLAT_Z_IN * INCH_TO_MM
UPPER_SHELF_FRAME    = UPPER_SHELF_FRAME_IN * INCH_TO_MM
UPPER_RAIL_BOT_Z     = UPPER_RAIL_BOT_Z_IN * INCH_TO_MM

SPOOL_ROD_Y          = SPOOL_ROD_Y_IN * INCH_TO_MM
SPOOL_Z_ROW1         = SPOOL_Z_ROW1_IN * INCH_TO_MM
SPOOL_Z_ROW2         = SPOOL_Z_ROW2_IN * INCH_TO_MM
SPOOL_ROD_R          = (SPOOL_ROD_DIA_IN * INCH_TO_MM) / 2.0
SPOOL_ROD_LEN        = SPOOL_ROD_LEN_IN * INCH_TO_MM


def create_box(doc, name, dx, dy, dz, pos, group=None):
    """Creates a parametric Part::Box with exact placement and non-colliding boundaries."""
    box_obj = doc.addObject("Part::Box", name)
    box_obj.Length = dx
    box_obj.Width = dy
    box_obj.Height = dz
    box_obj.Placement = Placement(Vector(pos[0], pos[1], pos[2]), Rotation(0, 0, 0, 1))
    if group:
        group.addObject(box_obj)
    return box_obj


def build_maker_station():
    doc_name = "MakerStation_8ft"
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

    # Document groups
    group_bents    = doc.addObject("App::DocumentObjectGroup", "Bents_2x4")
    group_rails    = doc.addObject("App::DocumentObjectGroup", "Longitudinal_Rails_96in")
    group_slats    = doc.addObject("App::DocumentObjectGroup", "Bottom_Slats_ApproachB")
    group_surfaces = doc.addObject("App::DocumentObjectGroup", "Plywood_Surfaces")
    group_hardware = doc.addObject("App::DocumentObjectGroup", "Hardware_Accessories")

    # ----------------------------------------------------
    # 1. THREE LADDER BENTS (Short-Ways: 3.5" in X, 1.5" in Y)
    # X-Coordinates:
    #   Bent 1 (Left):   [0.0, 3.5 in]
    #   Bent 2 (Center): [46.25, 49.75 in]
    #   Bent 3 (Right):  [92.5, 96.0 in]
    # Y-Partitions:
    #   [0.0, 1.5]   : Front 96" Rail
    #   [1.5, 3.0]   : Front Leg (Z: 0 to 25.75)
    #   [1.5, 27.0]  : Main Deck Depth Stringer (Z: 25.75 to 29.25, Length: 25.5")
    #   [3.0, 27.0]  : Bottom Depth Stringer (Z: 3.5 to 7.0, Length: 24.0")
    #   [27.0, 28.5] : Rear Upright Post (Z: 0 to 78.0)
    #   [28.5, 30.0] : Rear 96" Rail
    # ----------------------------------------------------
    bent_x_starts = [
        0.0,
        (TOTAL_WIDTH - LUMBER_W) / 2.0,
        TOTAL_WIDTH - LUMBER_W
    ]

    for idx, bx in enumerate(bent_x_starts):
        tag = f"Bent_{idx+1}"

        # Rear Upright Post (Short-ways: 3.5" in X, 1.5" in Y, 78.0" tall)
        create_box(
            doc, f"{tag}_RearUpright_78in",
            LUMBER_W, LUMBER_T, UPRIGHT_HEIGHT,
            (bx, 27.0 * INCH_TO_MM, 0.0),
            group_bents
        )

        # Front Leg (Short-ways: 3.5" in X, 1.5" in Y, 25.75" tall)
        create_box(
            doc, f"{tag}_FrontLeg_25_75in",
            LUMBER_W, LUMBER_T, FRAME_RAIL_BOT_Z,
            (bx, LUMBER_T, 0.0),
            group_bents
        )

        # Main Deck Depth Stringer (Z: 25.75 to 29.25", Length: 25.5")
        # Centered on the 3.5" leg, sits on top of front leg (Y: 1.5 to 3.0) and spans to rear post (Y=27.0)
        create_box(
            doc, f"{tag}_MainDeckStringer",
            LUMBER_T, (27.0 - LUMBER_T_IN) * INCH_TO_MM, LUMBER_W,
            (bx + (1.0 * INCH_TO_MM), LUMBER_T, FRAME_RAIL_BOT_Z),
            group_bents
        )

        # Bottom Full-Depth Stringer (Z: 3.5 to 7.0", Length: 24.0")
        # Fits squarely between front leg (Y=3.0) and rear post (Y=27.0)
        create_box(
            doc, f"{tag}_BottomDepthStringer",
            LUMBER_T, (27.0 - 3.0) * INCH_TO_MM, LUMBER_W,
            (bx + (1.0 * INCH_TO_MM), 3.0 * INCH_TO_MM, BOTTOM_RAIL_Z),
            group_bents
        )

        # Upper Cantilever Stringer (Z: 74.5 to 78.0", Length: 13.5")
        # Spans between Upper Front Rail (Y=13.5) and Rear Post (Y=27.0)
        create_box(
            doc, f"{tag}_UpperCantilever_2x4",
            LUMBER_T, (27.0 - 13.5) * INCH_TO_MM, LUMBER_W,
            (bx + (1.0 * INCH_TO_MM), 13.5 * INCH_TO_MM, UPPER_RAIL_BOT_Z),
            group_bents
        )

        # Dual Spool Pipe Cradle Brackets on Upright Posts (Row 1 and Row 2)
        for r_idx, cz in enumerate([SPOOL_Z_ROW1, SPOOL_Z_ROW2]):
            create_box(
                doc, f"{tag}_SpoolCradle_Row{r_idx+1}",
                (2.5 * INCH_TO_MM), (27.0 * INCH_TO_MM) - (SPOOL_ROD_Y - (0.75 * INCH_TO_MM)), (2.5 * INCH_TO_MM),
                (bx + (0.5 * INCH_TO_MM), SPOOL_ROD_Y - (0.75 * INCH_TO_MM), cz - (1.25 * INCH_TO_MM)),
                group_hardware
            )

    # Intermediate Reinforcement Ribs under Main Benchtop (X=24" and X=72")
    for rib_in, name in [(24.0, "Rib_X24"), (72.0, "Rib_X72")]:
        rx = (rib_in * INCH_TO_MM) - (LUMBER_T / 2.0)
        create_box(
            doc, f"MainDeck_{name}",
            LUMBER_T, (27.0 - LUMBER_T_IN) * INCH_TO_MM, LUMBER_W,
            (rx, LUMBER_T, FRAME_RAIL_BOT_Z),
            group_bents
        )

    # ----------------------------------------------------
    # 2. LONGITUDINAL 96" RAILS (Zero Collisions)
    # ----------------------------------------------------
    # Main Deck Front Rail (Y: 0.0 to 1.5)
    create_box(
        doc, "MainDeck_FrontRail_96in",
        TOTAL_WIDTH, LUMBER_T, LUMBER_W,
        (0.0, 0.0, FRAME_RAIL_BOT_Z),
        group_rails
    )

    # Main Deck Rear Rail (Y: 28.5 to 30.0)
    create_box(
        doc, "MainDeck_RearRail_96in",
        TOTAL_WIDTH, LUMBER_T, LUMBER_W,
        (0.0, 28.5 * INCH_TO_MM, FRAME_RAIL_BOT_Z),
        group_rails
    )

    # Lower Front Stretcher & Elevated Footrest (Y: 0.0 to 1.5)
    create_box(
        doc, "Lower_FrontFootrest_96in",
        TOTAL_WIDTH, LUMBER_T, LUMBER_W,
        (0.0, 0.0, BOTTOM_RAIL_Z),
        group_rails
    )

    # Lower Rear Stretcher (Y: 28.5 to 30.0)
    create_box(
        doc, "Lower_RearStretcher_96in",
        TOTAL_WIDTH, LUMBER_T, LUMBER_W,
        (0.0, 28.5 * INCH_TO_MM, BOTTOM_RAIL_Z),
        group_rails
    )

    # Upper Shelf Front Rail (Y: 12.0 to 13.5, Z: 74.5 to 78.0)
    create_box(
        doc, "UpperShelf_FrontRail_96in",
        TOTAL_WIDTH, LUMBER_T, LUMBER_W,
        (0.0, (TOTAL_DEPTH_IN - UPPER_SHELF_DEPTH_IN) * INCH_TO_MM, UPPER_RAIL_BOT_Z),
        group_rails
    )

    # Upper Shelf Rear Rail (Y: 28.5 to 30.0, Z: 74.5 to 78.0)
    create_box(
        doc, "UpperShelf_RearRail_96in",
        TOTAL_WIDTH, LUMBER_T, LUMBER_W,
        (0.0, 28.5 * INCH_TO_MM, UPPER_RAIL_BOT_Z),
        group_rails
    )

    # ----------------------------------------------------
    # 3. BOTTOM SLAT DECK (APPROACH B)
    # 4 Uncut 96" 2x4s laid flat in the rear half
    # ----------------------------------------------------
    slat_y_inches = [23.5, 19.5, 15.5, 11.5]

    for idx, sy_in in enumerate(slat_y_inches):
        create_box(
            doc, f"BottomSlat_96in_{idx+1}",
            TOTAL_WIDTH, LUMBER_W, LUMBER_T,
            (0.0, sy_in * INCH_TO_MM, BOTTOM_SLAT_Z),
            group_slats
        )

    # ----------------------------------------------------
    # 4. PLYWOOD SHEETING SURFACES (Flush Capped Design)
    # ----------------------------------------------------
    # Primary Benchtop Surface (30.0" x 96.0" x 0.75", Z: 29.25 to 30.0)
    create_box(
        doc, "Primary_Benchtop_Plywood",
        TOTAL_WIDTH, TOTAL_DEPTH, PLYWOOD_T,
        (0.0, 0.0, FRAME_TOP_Z),
        group_surfaces
    )

    # Upper Tier Storage Shelf (18.0" x 96.0" x 0.75", Z: 78.0 to 78.75)
    create_box(
        doc, "Upper_Tier_Plywood",
        TOTAL_WIDTH, UPPER_SHELF_DEPTH, PLYWOOD_T,
        (0.0, (TOTAL_DEPTH_IN - UPPER_SHELF_DEPTH_IN) * INCH_TO_MM, UPPER_SHELF_FRAME),
        group_surfaces
    )

    # ----------------------------------------------------
    # 5. DUAL-TIER MODULAR 4FT SPOOL PIPES (Above Gantry)
    # ----------------------------------------------------
    def add_spool_pipe(doc, name, start_x, rod_z):
        rod = doc.addObject("Part::Cylinder", name)
        rod.Radius = SPOOL_ROD_R
        rod.Height = SPOOL_ROD_LEN
        rod.Placement = Placement(
            Vector(start_x, SPOOL_ROD_Y, rod_z),
            Rotation(Vector(0, 1, 0), 90)
        )
        group_hardware.addObject(rod)
        return rod

    if SPOOL_BAY_MODE in ("left_dual", "all_dual"):
        add_spool_pipe(doc, "SpoolRod_Left_Lower_Row1", 0.0, SPOOL_Z_ROW1)
        add_spool_pipe(doc, "SpoolRod_Left_Upper_Row2", 0.0, SPOOL_Z_ROW2)

    if SPOOL_BAY_MODE in ("right_dual", "all_dual"):
        bay_w = TOTAL_WIDTH / 2.0
        add_spool_pipe(doc, "SpoolRod_Right_Lower_Row1", bay_w, SPOOL_Z_ROW1)
        add_spool_pipe(doc, "SpoolRod_Right_Upper_Row2", bay_w, SPOOL_Z_ROW2)

    doc.recompute()

    try:
        import FreeCADGui
        if FreeCADGui.activeDocument():
            FreeCADGui.activeDocument().activeView().redraw()
    except Exception:
        pass

    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "exports")
    os.makedirs(out_dir, exist_ok=True)
    doc.saveAs(os.path.join(os.path.dirname(os.path.abspath(__file__)), "MakerStation.FCStd"))

    part_objs = [o for o in doc.Objects if o.TypeId.startswith("Part::")
                 and o.TypeId not in ("Part::Feature",)]
    lumber = [o for o in part_objs if o.Name.startswith(("Bent_", "MainDeck_", "Lower_", "UpperShelf_", "BottomSlat_"))
              and "SpoolCradle" not in o.Name]
    plywood = [o for o in part_objs if o.Name.startswith(("Primary_Benchtop", "Upper_Tier"))]
    rods = [o for o in part_objs if o.Name.startswith("SpoolRod_")]
    cradles = [o for o in part_objs if "SpoolCradle" in o.Name]

    import Mesh
    Part.export(part_objs, os.path.join(out_dir, "MakerStation.step"))
    Mesh.export(lumber + cradles, os.path.join(out_dir, "MakerStation_Lumber.stl"))
    Mesh.export(plywood, os.path.join(out_dir, "MakerStation_Plywood.stl"))
    Mesh.export(rods, os.path.join(out_dir, "MakerStation_Rods.stl"))
    print("MakerStation 8ft solid assembly built successfully in FreeCAD.")
    print("Exported STEP + 3 STLs "
          f"(lumber={len(lumber) + len(cradles)}, plywood={len(plywood)}, rods={len(rods)})")
    return doc


if __name__ == "__main__" or "FreeCAD" in sys.modules:
    build_maker_station()
