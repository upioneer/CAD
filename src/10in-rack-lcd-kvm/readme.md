# 10in Rack 2U LCD + JetKVM Mini Console Plate

* Parametric FDM-printable 2U faceplate pairing 1x USB LCD with 1x JetKVM Mini (42 x 42 x 23) so one glance ties both to their endpoint.
* Two variants from one model: `RACK_SCREEN=3.5` (default, 85 x 55 x 8 LCD) or `RACK_SCREEN=5.0` (122 x 78 x 10 LCD).
* Drop-in from the rear, no fasteners, no adhesion: LCD seats under a bezel lip + snap hooks; the Mini stands display-forward with glass near-flush in a stepped window, caught by a side hook.

## How It Holds

* **LCD bay (left)**: pocket with 0.4mm/side clearance, bezel window solved from measured bezels (3.5in: L2.8 / R8.7, bays shifted so both lit areas land symmetric), 2 top snap hooks, outer cable slot + top/bottom notches, open rear.
* **Mini bay (right)**: 42.8 pocket on side ledges (open floor-center for cable exit + cooling), front lip ring overlapping the display glass, ports facing up with open-top cable exit into the rack void, single side hook in the center wall.
* **Buttons**: pill slot in the outer wall exposes both Mini buttons + status LED for direct fingertip press. No plungers or linkages.
* **Label**: embossed endpoint text, paint-fillable (bottom strip on 3.5in, rotated side column on 5in). Set per unit at build time via `RACK_LABEL` ("NODE-01", ...); blank default builds with no text.
* **Cables**: USB/HDMI/RJ45 exit up out of the Mini bay and lash to printed tie loops at both tub rears. Right-angle adapters on the Mini ports make the neatest install.

## Mini Dimensions Status

* Body 42 x 42 x 23 is from published specs. Glass (39.1, R4), buttons (D5.8 at +/-8.25, 12.8 behind the glass), and LED are measured off straight-on product renders (+/-0.5mm) and flagged `PHOTO-DERIVED` in the model.
* Orientation map (validated): display faces the aisle, buttons on the rack-right wall, glass 0.9 recessed. Display-forward plus buttons-right admits no other parity: any flip either faces the display into the rack or moves the buttons to the left wall. The 12mm button slot absorbs the +/-0.5mm photo error with margin to spare.
* On arrival, confirm in 30 seconds: caliper glass-edge to near button edge (expect ~9.9mm); note which edge the ports sit on holding display-forward buttons-right (bay already handles up/down/rear, only cable routing changes); check on-screen text reads upright (else look for a firmware display-rotation setting).
* The 34mm glass window keeps 2mm+ lip and shows all content across that error band, but confirm glass size/corner radius plus button spacing with calipers when the units arrive and update `MINI_GLASS_MM`, `MINI_WIN_MM`, `MINI_BTN_PITCH_MM`, `MINI_BTN_D_MM`, `MINI_BTN_DEPTH_MM` if needed.
* Port-face clocking vs the buttons is unconfirmed from photos; the bay is symmetric-safe either way (open top + open floor-center), so no rework is needed, only cable routing changes.

## Print Settings

* **Material**: PETG (recommended for hook flex) or ASA.
* **Orientation**: face-down, bezel front flat on the bed. Pockets, hooks, slots, and ramps print support-free; tie loops bridge 8mm.
* **Profile**: 0.2mm layers, 4+ walls, 25%+ infill. Brim recommended (253 x 88 footprint can warp).
* **Files**: `exports/Rack_2U_LCDKVM_35_Plate.stl` (79.3 cm3) or `exports/Rack_2U_LCDKVM_50_Plate.stl` (69.7 cm3).

## Rack Mounting

* **Holes**: 4x 12 x 8 lateral slots (+/-2mm wiggle) on 236.5 x 44.45 centers for RackStuds; vertical stays hole-tight for U alignment.
* **Fit**: 253.0 x 88.1 flange; tray passes between rails (222 clear).
* **Install**: load LCD then Mini on the bench (rear insertion, listen for the clicks), route USB cables out the back, hang the plate on 4 RackStuds.

## Build & Files

* Run the live watcher [live_10in_rack_lcd_kvm.py](file:///C:/dev/Projects/CAD/src/live/live_10in_rack_lcd_kvm.py) inside FreeCAD, or headless via `freecadcmd kvm_plate_freecad.py` (`RACK_SCREEN=5.0` for the 5in variant). Live saves skip STEP/STL/FCStd writes.
* `kvm_plate_freecad.py`: parametric model. Fit checks assert pocket clearances, window lips and active margins, glass lip, button-slot placement and coverage, tray vs rails, and hook placement on every build.
* Handedness: CAD +X appears on the viewer's LEFT (front view looks from -Z). Mini on CAD -X == viewer-right with buttons facing the outer wall; bezel L/R are viewer-frame and negated into CAD. Previews negate X to match reality.
* `preview.py` → `preview_35.svg` / `preview_50.svg`: front elevation plus 6:1 LCD and Mini bay sections.
* `exports/`: STEP + STL per variant. Every output file carries its variant tag (`_35` / `_50`, never dots, so extensions parse cleanly), plus `_LABEL` when a label is set (e.g. `Rack_2U_LCDKVM_35_NODE-01_Plate.stl`).

## Tweaking

* Screen size: `RACK_SCREEN` env (`3.5` or `5.0`).
* Re-measured Mini or LCD numbers: `MINI_*_MM`, LCD `bez_*` in `LCD_SPECS` (bays, windows, and tray re-solve automatically).
* Endpoint name: `RACK_LABEL` env (blank default builds with no text).
