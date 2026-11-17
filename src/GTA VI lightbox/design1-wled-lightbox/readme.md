# Design 1: GTA VI WLED Negative Cutout Lightbox (v4)

A multi-plane architectural lightbox engineered for the xTool S1 20W diode laser cutter, producing the Vice City sunset glow via addressable WLED control.

Open [preview.svg](file:///C:/dev/Projects/CAD/src/GTA%20VI%20lightbox/design1-wled-lightbox/preview.svg) for the front elevation and side-section stack diagram (regenerate anytime with `python preview.py`).

---

## Dimensional Envelope & Machine Compatibility

* **Outer Enclosure**: 300.0 x 300.0 mm square (11.81 inches)
* **Total Box Depth**: 59.2 mm face, 65.6 mm including raised text badge
* **Single-stock build**: Every layer cuts from 1/8 inch (3.175 mm) sheet. Structure and graphic layers are 1/8 inch basswood; the diffuser is 1/8 inch frosted acrylic (same cut thickness); text faces are white acrylic or painted basswood.
* **12x12 Sheet Fit**: All parts fit 12 x 12 inch stock (largest part 300 mm, 2.4 mm/side margin). xTool S1 bed has room to spare.

---

## Layer Stack (Back to Front)

| Z (mm)    | Layer | Material |
| --------- | ----- | -------- |
| 0 to 3.175 | Backplate: keyholes, VESA, light-leak perfs | 1/8 in basswood |
| 3.175 to 46.525 | WLED cavity + ESP32 sled | Matte white liner |
| 46.525 to 49.7 | Optical diffuser panel (param size) | 1/8 in frosted acrylic |
| 49.7 to 52.875 | Tree panel: solid sheet, VI window, fused palms | 1/8 in basswood, stained black |
| 52.875 to 56.05 | Neon plate, full sheet, VI-2.5 window | 1/8 in magenta acrylic |
| 56.05 to 59.225 | **Faceplate: clean, VI aperture ONLY** | 1/8 in basswood, matte black |
| 59.225 to 62.4 | Text backer plaque, one piece | 1/8 in black acrylic / stained basswood |
| 62.4 to 65.575 | White `grand theft auto` letters | 1/8 in white acrylic |

---

## Front Faceplate: Zero-Fastener Negative Space

* **Material**: 1/8 inch basswood, matte black finish, full-bleed 300 x 300 mm cap over the wall frame.
* **Geometry**: The ONLY cut is the exact negative `VI` through-aperture from `vi_palm_vectors.json`. No screws, no holes, no fasteners anywhere on the visible face. All joinery lives on the walls and rear chassis.
* **Relief stack**: Fully sandwiched, zero air gaps. Looking into the aperture: the neon plate border (2.5 mm visible) sits flush behind the face, with palm silhouettes and the glowing diffuser directly behind it. Every layer face-glues to its neighbors; the LED cavity below provides the only air in the box.

## Relief Cuts for Depth

* **Neon plate**: Full 287.3 mm sheet (faceplate trimmed 0.5 in W+H) with a VI window inset 2.5 mm inside the faceplate aperture, leaving a glowing border in view. Its entire back face-glues to the tree panel for maximum adhesion.
* **Tree panel (ONE layer, 4 styles)**: Full drop-in sheet with a VI+2 window; parametric palms (trunks, crowns, coconuts from `palm_trees.py`) fuse across the window into one laser-cut piece. Nothing floats: every trunk base lands on solid panel. Styles ranked: `v1` organic (arching fronds, lanceolate taper, S-trunks; recommended), `v2` reference, `v3` original fans, `v4` bold graphic (fastest cut). All four live in the model; only `TREE_STYLE` is visible. Compare by flipping visibility on the `Tree_V*` objects in the tree view, or change `TREE_STYLE` and rebuild. Cut exactly ONE of `04a` / `04b` / `04c` / `04d`.

## Raised `grand theft auto` Badge (2 Layers)

* **Layout**: EXACT official wordmark traced from `media/gta.svg.webp` (no font approximation): `grand` / `theft` / `auto` with the authentic cross-line `r`/`h` touch, 165 x 131 mm lockup centered at X +18 mm over the V notch. 13 white regions, 7 counter cutouts.
* **Construction**: Exactly two layers. White 1/8 inch letters (36.13 cm3) over ONE single-piece backer (62.67 cm3) that follows the text shape: every region outline is inflated outward 7 mm (true offset, never scaled, so the border is uniform) and fused into one plaque. Alignment is automatic since offsets share the letters' exact position. Counters back solid black. The backer glues flush onto the faceplate; no mounting tabs, nothing to interfere with cutting or slicing.
* **One-piece guarantee**: The build auto-fills any trapped fusion voids to a fixpoint (max 3 passes), so the laser path is always a single outer loop with zero interior holes. Verified by raster union test: 1 connected component, 0 holes. To re-trace new art, run `python trace_bitmap.py` (self-checks IoU vs source) and rebuild.
* **Re-lettering**: The traced lockup is fixed art; `TEXT_LINES` / `TEXT_WIDTHS_MM` now serve only the legacy font fallback (`USE_TRACED_LOCKUP = False`). `LOCKUP_WIDTH_MM` rescales the whole lockup uniformly.
* **Laser note**: The 7 counters cut as interior cutouts (slugs are waste); they read black from the solid backer behind. No tiny glue-ups needed.
* **Score placement**: The backer top carries the 13 letter outlines as shallow 0.6 x 0.4 mm grooves, and `exports/06_Text_Backer_Plate_laser.svg` holds the same job in 2D: black layer cuts the plate outline, red layer scores the letter seats at low power. The grooves straddle the letter edges, so a thin scored keyline remains visible around each glued letter and proves alignment at a glance. Disable with `SCORE_PLACEMENT = False`.

## WLED Segments

* **Top strip**: Twilight violet. **Bottom strip**: Sunset amber. **Left / right strips**: Neon magenta. Live gradient blending reproduces the official sunset palette with pulsing, breathing, and audio-reactive animations.
* **Perimeter runs**: LED strips mount to the inner wall faces all around. The bottom run splits into 3 with 20 mm gaps where the power ports land.
* **Power**: Four 12 mm port options for a 5.5 x 2.1 mm DC barrel jack or USB-C PD trigger: two on the bottom wall (x +/-120) plus two on the lower back corners (+/-135, -108). Plug the unused ones. ESP32 sled inside the rear cavity.

## Rear Chassis: Mounts + Light Leak

* **Walls**: Top, left, and right walls are fully sealed, zero cuts. Only the bottom wall (ports) and backplate break the enclosure.
* **Keyholes**: Triple keyhole slots (left, center, right) for flush wall hanging.
* **VESA**: Standard 75 x 75 mm and 100 x 100 mm patterns (M4 clearance), centered, for monitor arms and wall mounts.
* **Light-leak slots**: 18 long slots (40 x 4 mm, 50 mm pitch) around the backplate perimeter bleed a deliberate halo onto the wall behind the unit. Long slots mean fewer pierces, faster cutting, and less char cleanup than dots. Disable with `BACK_PERF_ENABLED = False`.

## Finger Joints + Cut List (v1 Physical)

* **Joints**: All four vertical wall corners are 6-finger box joints (8.8 mm pitch, 0.1 mm glue gap). All four walls also drop 4 base tabs each into edge notches in the backplate, which registers the walls square during glue-up and carries the full hanging load (verified zero-interference fit). Faceplate butt-glues onto the wall top edges as a clean lid.
* **Adhesion system (zero spacers)**: Diffuser and tree panel face-glue into one sandwich that edge-glues to the walls. No spacer frames anywhere. Use wood glue wood-to-wood; use silicone adhesive or VHB tape for anything touching acrylic (wood glue bonds acrylic poorly).
* **Diffuser sizing**: Defaults to a full 292.65 mm drop-in sheet. Set `DIFFUSER_W_MM` / `DIFFUSER_H_MM` to use offcuts: anything at or above 260 x 210 still covers the VI aperture, and the build warns loudly below that. Note an 8x8 inch sheet (203 mm) does NOT span the 238 mm VI: overlap two for full coverage.
* **Build order (face-down)**: Lay the faceplate face-down. Stack neon plate, tree panel, diffuser with glue between (gravity registers everything). Slide the pre-glued wall tube over the stack, lower the backplate onto the wall base tabs, wire the WLED perimeter first if you prefer access. Flip upright after curing. Glue the text backer + letters onto the face last.
* **12x12 sheet estimate**: About 8 sheets with simple nesting. Nest the small parts (text) inside each other's offcuts.

## Build & Export

Run the live watcher [live_gta_vi_lightbox_design1_wled_lightbox.py](file:///C:/dev/Projects/CAD/src/live/live_gta_vi_lightbox_design1_wled_lightbox.py) inside FreeCAD, or headless via `freecadcmd lightbox_freecad.py`. Live-watcher saves skip STEP/STL/FCStd writes for speed; a manual Macro run or `freecadcmd` run performs the full production export:

1. `01_Front_Faceplate` (300 x 300, x1)
2. `02_Neon_Plate` (287.3 x 287.3 with VI window, x1)
3. (retired with the reveal plate; numbers stay stable from here on)
4. `04a_Tree_V1_Organic`, `04b_Tree_V2_Reference`, `04c_Tree_V3_Fans`, `04d_Tree_V4_Bold` (292.7 x 292.7 solid panel, cut ONE)
5. `05_Text_Face_White` (165 x 131 traced lockup, x1)
6. `06_Text_Backer_Plate` (179 x 145, x1) plus `06_Text_Backer_Plate_laser.svg` (black cut + red score in one job)
7. `07_Backplate_VESA_Perfs` (300 x 300, x1)
8. `08_Wall_Top` (300 x 52.9 fingered, x1)
9. `09_Wall_Bottom_Ports` (300 x 52.9 fingered + ports, x1)
10. `10_Wall_Side_x2` (300 x 52.9 fingered, x2)
11. `11_Diffuser_Plate` (292.7 x 292.7 frosted default, x1)

The `exports/` folder holds exactly these thirteen pairs (cut one tree style) plus the backer laser SVG; no stale files remain.
