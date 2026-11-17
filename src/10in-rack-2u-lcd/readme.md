# 10in Rack 2U Dual 3.5in LCD Tray Plate

* Parametric FDM-printable 2U faceplate for 10in mini racks. Holds 2x cased 3.5in USB LCDs (85 x 55 x 8mm, Turing/SmartCool class) side by side.
* Drop-in from the rear: modules seat against the front bezel lip and click under printed snap hooks. No fasteners, no adhesion, no assembly.
* 4x rack holes on EIA spacing for RackStuds in square-hole front rails.

## How It Holds

* **Front**: bezel windows (77.1 x 52, solved) are smaller than the module (85 x 55), leaving a retaining lip all around, and larger than the 74 x 49 active area, so the full screen shows with margin.
* **Bezel offset**: the screens sit 2.95mm left of module center (measured landscape bezels L2.8 / R8.7; top/bottom assumed symmetric 3.0). Both bays shift 2.95mm toward the thick side so the two lit areas land symmetric about the plate center with even view margins. Windows auto-shrink only as far as offsets demand, never below 1.0mm lip or 0.8mm active margin.
* **Sides**: pockets sized 85.8 x 55.8 (0.4mm/side FDM clearance).
* **Rear**: 2 cantilever snap hooks per bay with 45-degree insertion ramps and 1.0mm catch overlap behind the module. Release by lifting a tooth through its relief slot with a pick while sliding the module back.
* **Cables**: USB-C port positions vary by hardware revision (some units carry 2 ports on different sides), so every bay gets side slots plus top and bottom notches, all open at the rear. Right-angle USB-C cables route cleanest toward the back of the rack.

## Print Settings

* **Material**: PETG (recommended for hook flex) or ASA. PLA works but hooks fatigue faster.
* **Orientation**: face-down, bezel front flat on the bed. Tray, hooks, slots, and ramps all print support-free in this orientation.
* **Profile**: 0.2mm layers, 4+ walls, 25%+ infill. Brim recommended (253 x 88 footprint can warp).
* **File**: `exports/Rack_2U_DualLCD_Plate.stl` (single part, 67.4 cm3).

## Rack Mounting

* **Holes**: 4x 12 x 8 lateral slots (D8 + 4 extra, so +/-2mm wiggle) on 236.5 x 44.45 centers (EIA mid-hole of each U). D8 clears RackStud shafts with FDM tolerance; vertical stays hole-tight for U alignment.
* **Corners**: R3 bezel radius, matching common 10in plate language.
* **Fit**: 253.0 x 88.1 flange; tray body 179.1 wide passes between rails (222 clear).
* **Install**: load both modules on the bench (rear insertion, listen for the clicks), route USB cables out the back, then hang the plate on 4 RackStuds.

## Build & Files

* Run the live watcher [live_10in_rack_2u_lcd.py](file:///C:/dev/Projects/CAD/src/live/live_10in_rack_2u_lcd.py) inside FreeCAD, or headless via `freecadcmd rack_plate_freecad.py`. Live saves skip STEP/STL/FCStd writes; a Macro or `freecadcmd` run performs the full export.
* `rack_plate_freecad.py`: parametric model. Fit checks assert pocket clearance, window vs active area vs module, tray vs rails, and hole placement on every build; the build fails loudly if a param edit breaks retention.
* `preview.py` → `preview.svg`: front elevation plus a 6:1 bay section through the hook.
* Handedness: CAD +X appears on the viewer's LEFT (front view looks from -Z). Bezel L/R are viewer-frame and negated into CAD; the preview negates X to match reality.
* `exports/`: `Rack_2U_DualLCD_Plate.step` + `.stl`.

## Tweaking

* Different module thickness: `MOD_T_MM` (hook tooth and tub depth derive from it).
* Re-measured bezels: `BEZEL_L_MM` / `BEZEL_R_MM` / `BEZEL_T_MM` / `BEZEL_B_MM` (bays, windows, and tray re-solve automatically). `BAY_MODE = "rotated"` instead mounts the right module at 180 degrees, at the cost of a software flip.
* Tighter/looser drop-in: `POCKET_CLR_MM` (0.4 default; keep >= 0.25 for FDM).
* Different rails: `RACK_HOLE_D_MM`, `HOLE_DX_MM`, `HOLE_DY_MM`. Slot length via `RACK_SLOT_EXTRA_MM` (0 restores round holes); corners via `CORNER_R_MM`.
* Weaker/stronger catch: `HOOK_CATCH_MM` (1.0 default).
