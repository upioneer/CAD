# Modular 3D Printable Spool Brackets & Stopper Collars

High-strength, support-free 3D printable cantilever brackets engineered to support modular 3/4-inch EMT steel conduit filament spool rods on the 8ft Maker Station.

## Workflow Separation

To maintain a clean separation between workshop trades:
* **`src/8ft-maker-station/`**: Workshop carpentry, lumber cutting schedules, framing joints, and table assembly.
* **`src/spool-brackets/`**: Additive manufacturing, 3D printing slicing configurations, STL/STEP assets, and conduit hardware.

---

## Mechanical Specifications & Load Path Analysis

* **Conduit Specification**: 3/4-inch EMT Thinwall Electrical Metallic Tubing (Nominal OD: 0.922 inches / 23.42 mm).
* **Bore Diameter**: 24.20 mm (+0.78 mm diametral clearance), engineered for smooth slip-fit insertion without slop or binding.
* **Cantilever Arm Projection**: 152.4 mm (6.0 inches) forward from the front face of the 2x4 upright posts to the center of the conduit pipe.
* **Overhead Clearance Alignment**:
  * Row 1 (Lower Spool Rod): Elevation Z = 63.5 inches (4.0 inches above printer gantry top).
  * Row 2 (Upper Spool Rod): Elevation Z = 71.0 inches (11.5 inches above printer gantry top).
  * Filament drops directly down at Y = 21.0 inches into the Elegoo Neptune 3 Max runout sensor eyelet.
* **Static Bending Moment**:
  * 4 filament spools (1 kg each) + conduit tare = ~5.0 kg (~49 N).
  * Cantilever Moment: $M = 49\text{ N} \times 0.1524\text{ m} \approx 7.47\text{ N}\cdot\text{m}$ per bracket bay.
  * 105 mm vertical screw baseline ($b = 76\text{ mm}$ between top and bottom screws) reduces top screw pullout tension to $T \approx 98\text{ N}$ (22 lbf), well below the 300+ lbf pullout rating of standard construction screws in SPF lumber.

---

## Component Variants

1. **Center Bracket (`spool_bracket_center`)**:
   * Solid manifold volume: 225.15 cm3.
   * Open through-channel allowing a continuous 8-foot conduit pipe, or serving as the shared central junction where two 4-foot modular conduits meet.
2. **Left End Bracket (`spool_bracket_end_left`)**:
   * Solid manifold volume: 227.94 cm3.
   * Features an integrated 4.0 mm solid left stop wall that prevents the conduit from walking or sliding out to the left.
3. **Right End Bracket (`spool_bracket_end_right`)**:
   * Solid manifold volume: 227.94 cm3.
   * Features an integrated 4.0 mm solid right stop wall that prevents the conduit from sliding out to the right.
4. **Conduit Stopper Collar (`spool_stopper_collar`)**:
   * Solid manifold volume: 10.98 cm3.
   * Clamps onto the 3/4-inch EMT conduit using an M4 bolt and nut trap to partition spools and prevent lateral spool migration.

---

## Design for Additive Manufacturing (DFM) & Slicing Parameters

### 1. Print Orientation (Zero Supports Required)
* **Lay Flat on Side**: The bracket profile is extruded to a uniform width of 36.0 mm. By placing either side face directly against the build plate, the entire bracket prints with **zero support material**.
* **Continuous Tensile Loops**: Printing on its side aligns the extruded plastic filament beads parallel to the cantilever load path:
  * Top horizontal flange carries tensile loads along continuous extruded perimeters.
  * Diagonal lower strut carries compressive loads directly back into the 2x4 wood face.
  * Eliminates the risk of interlayer delamination failure under dynamic spool pulling.

### 2. Recommended Slicer Settings

| Parameter | Recommended Value | Engineering Rationale |
| :--- | :--- | :--- |
| **Material** | PETG, PLA+, or ASA/ABS | High creep resistance and tensile strength under long-term dead loads |
| **Layer Height** | 0.20 mm to 0.28 mm | Optimal balance of print speed and interlayer bonding strength |
| **Perimeter Walls** | 4 to 5 walls (1.6 mm - 2.0 mm) | Major structural load is carried by the perimeter shells |
| **Top / Bottom Layers** | 5 top / 5 bottom | Solid skin across the 36 mm width |
| **Infill Percentage** | 30% to 40% | Sufficient internal shear web resistance |
| **Infill Pattern** | Gyroid or 3D Honeycomb | Isotropic shear resistance without directional stress lines |
| **Supports** | None (Disabled) | Self-supporting geometry when printed on side |
| **Brim** | Optional (3 mm - 5 mm) | Recommended for bed adhesion on textured PEI sheets |

---

## Fastener & Hardware Schedule

* **Wood Mounting Screws**: 3x #9 or #10 x 2-1/2 inch flat head or pan head wood/construction screws per bracket (counterbored for flush head seating).
* **Retaining Linchpin / Cross-Bolt**: 1x M5 x 45 mm hex bolt, socket head cap screw, or 3/16-inch quick-release wire linchpin per bracket (inserted through the transverse hole at Z = 14 mm above the conduit center to prevent pipe dislodgement).
* **Stopper Collar Hardware**: 1x M4 x 20 mm socket head cap screw and 1x M4 hex nut per collar.

---

## Source & Asset Links

* **Parametric FreeCAD Automation Script**: [`spool_bracket.py`](file:///C:/dev/Projects/CAD/src/spool-brackets/spool_bracket.py)
* **Parametric OpenSCAD Script**: [`spool_bracket.scad`](file:///C:/dev/Projects/CAD/src/spool-brackets/spool_bracket.scad)
* **Generated STEP Models (CAD B-Rep)**:
  * [`exports/spool_bracket_center.step`](file:///C:/dev/Projects/CAD/src/spool-brackets/exports/spool_bracket_center.step)
  * [`exports/spool_bracket_end_left.step`](file:///C:/dev/Projects/CAD/src/spool-brackets/exports/spool_bracket_end_left.step)
  * [`exports/spool_bracket_end_right.step`](file:///C:/dev/Projects/CAD/src/spool-brackets/exports/spool_bracket_end_right.step)
  * [`exports/spool_stopper_collar.step`](file:///C:/dev/Projects/CAD/src/spool-brackets/exports/spool_stopper_collar.step)
* **Generated STL Files (Ready for Slicing)**:
  * [`exports/spool_bracket_center.stl`](file:///C:/dev/Projects/CAD/src/spool-brackets/exports/spool_bracket_center.stl)
  * [`exports/spool_bracket_end_left.stl`](file:///C:/dev/Projects/CAD/src/spool-brackets/exports/spool_bracket_end_left.stl)
  * [`exports/spool_bracket_end_right.stl`](file:///C:/dev/Projects/CAD/src/spool-brackets/exports/spool_bracket_end_right.stl)
  * [`exports/spool_stopper_collar.stl`](file:///C:/dev/Projects/CAD/src/spool-brackets/exports/spool_stopper_collar.stl)
