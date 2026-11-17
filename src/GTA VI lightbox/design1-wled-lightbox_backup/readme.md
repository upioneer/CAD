# Design 1: GTA VI WLED Negative Cutout Lightbox (v3)

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
| 3.175 to 30.825 | WLED cavity + ESP32 sled | Matte white liner |
| 30.825 to 34 | Spacer frame | 1/8 in basswood |
| 34 to 37.175 | Optical diffuser panel | 1/8 in frosted acrylic |
| 37.175 to 40.35 | Slab-slot spacer (omit if frosted slab fitted) | 1/8 in basswood |
| 40.35 to 43.525 | Tree relief REAR (frame + 3 full palms) | 1/8 in basswood, stained black |
| 43.525 to 46.7 | Tree relief FRONT (frame + 2 full palms) | 1/8 in basswood, stained black |
| 46.7 to 49.875 | Relief reveal plate (VI + 1.5 mm window) | 1/8 in basswood, dark stain |
| 49.875 to 53.05 | Neon accent ring (VI -2.5 to +4.0 mm band) | 1/8 in magenta acrylic |
| 53.05 to 56.05 | Shadow gap (floating reveal) | Air |
| 56.05 to 59.225 | **Faceplate: clean, VI aperture ONLY** | 1/8 in basswood, matte black |
| 59.225 to 62.4 | Text backer plaque, one piece | 1/8 in black acrylic / stained basswood |
| 62.4 to 65.575 | White `grand theft auto` letters | 1/8 in white acrylic |

---

## Front Faceplate: Zero-Fastener Negative Space

* **Material**: 1/8 inch basswood, matte black finish, full-bleed 300 x 300 mm cap over the wall frame.
* **Geometry**: The ONLY cut is the exact negative `VI` through-aperture from `vi_palm_vectors.json`. No screws, no holes, no fasteners anywhere on the visible face. All joinery lives on the walls and rear chassis.
* **Relief channel**: Looking into the aperture, the eye drops through a terraced 21 mm channel: neon ring edge (2.5 mm visible), reveal step, palm silhouettes, then the glowing diffuser. True parallax as the viewer walks past.

## Relief Cuts for Depth

* **Neon ring**: Fused V + I band peeking 2.5 mm into the aperture with a glue foot hidden under the faceplate.
* **Reveal plate**: Oversized VI window forming a shadow step behind the ring.
* **Tree relief layers (x2)**: Full parametric palms (trunks, 9-frond crowns, coconuts from `palm_trees.py`) mounted to each layer's own 12 mm perimeter frame. Nothing floats: trunk bases start on the frame bars and the open centers flood with backlight. Rear layer holds 3 trees, front layer 2, offset for true parallax. Retune any tree's base, crown, lean, or frond fan in `palm_trees.py`; model and preview follow together.
* **Future slab slot**: Trees sit one level up so 37.175 to 40.35 stays open behind them. A spacer frame holds the rear layer there today; to fit an extra full-size frosted slab (411.65 x 251.65 mm), build it in that slot and omit the spacer.

## Raised `grand theft auto` Badge (2 Layers)

* **Layout**: Official stacked order (`grand` / `theft` / `auto`), 54 mm pitch, centered at X +18 mm over the V notch, lettered in a condensed heavy display face (Impact, with Arial Black / Arial Bold fallback).
* **Construction**: Exactly two layers. White 1/8 inch letters over ONE single-piece backer that follows the text shape: every glyph outline is inflated outward 5 mm (true offset, never scaled, so the border is uniform) and fused into one plaque. Alignment is automatic since offsets share the letters' exact position. Counters back solid black. The backer glues flush onto the faceplate; no mounting tabs, nothing to interfere with cutting or slicing.
* **Re-lettering**: Change `TEXT_LINES` / `TEXT_WIDTHS_MM` in `lightbox_freecad.py`; the backer re-offsets and re-fuses automatically (`BACKER_OFFSET_MM` sets the border).
* **Laser note**: Letter counters (the inner islands of `a`, `d`, `e`, `o`) cut as tiny separate pieces; glue them into the white letters during assembly.

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
* **Build order**: Dry-fit the 4 walls into the backplate notches, then glue the tube. Drop in the diffuser frame, diffuser, slab-slot spacer, both tree layers, and the reveal plate. Wire the WLED perimeter. Glue the backplate. Cap with the faceplate, then glue the text backer + letters onto the face.
* **12x12 sheet estimate**: About 9 sheets with simple nesting. Nest the small parts (ring, text, spacers) inside each other's offcuts; the spacer rings swallow the text plates whole.

## Build & Export

Run the live watcher [live_lightbox.py](file:///C:/dev/Projects/CAD/src/live/live_lightbox.py) inside FreeCAD, or headless via `freecadcmd lightbox_freecad.py`. Live-watcher saves skip STEP/STL/FCStd writes for speed; a manual Macro run or `freecadcmd` run performs the full production export:

1. `01_Front_Faceplate` (300 x 300, x1)
2. `02_Neon_Accent_Ring` (~246 x 188, x1)
3. `03_Relief_Reveal_Plate` (292.8 x 292.8, x1)
4. `04_Tree_Relief_Rear` (287.7 x 287.7, x1)
5. `05_Tree_Relief_Front` (287.7 x 287.7, x1)
6. `06_Text_Face_White` (~140 x 162, x1)
7. `07_Text_Backer_Plate` (~150 x 172, x1)
8. `08_Backplate_VESA_Perfs` (300 x 300, x1)
9. `09_Wall_Top` (300 x 52.9 fingered, x1)
10. `10_Wall_Bottom_Ports` (300 x 52.9 fingered + ports, x1)
11. `11_Wall_Side_x2` (300 x 52.9 fingered, x2)
12. `12_Diffuser_Plate` (291.7 x 291.7 frosted, x1)
13. `13_Spacer_Frame_x2` (292.8 ring, x2)

The `exports/` folder holds exactly these thirteen pairs; no stale files remain.
