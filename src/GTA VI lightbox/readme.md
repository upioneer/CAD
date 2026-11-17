# GTA VI Lightbox: Multi-Layer Laser Cut WLED Enclosure

An addressable multi-layer illuminated lightbox engineered for the xTool S1 20W enclosed diode laser cutter, featuring integrated WLED ambient and perimeter lighting.

---

## Machine Validation: xTool S1 20W Working Envelope

The stated dimensions have been verified against official manufacturer hardware specifications:

* **Total Machine Bed / Base Size**:
  * Metric: **608 mm (L) x 385 mm (W)**
  * Imperial: **23.93 inches (L) x 15.16 inches (W)**
  * *Context*: This is the total interior structural floor and honeycomb footprint inside the enclosed chassis.
* **Effective Working Area (Cutting & Engraving Travel)**:
  * Metric: **498 mm (X) x 319 mm (Y)** (up to 330 mm Y on the 20W diode module depending on focus pin and air assist nozzle clearance)
  * Imperial: **19.61 inches (X) x 12.56 inches (Y)**
  * *Context*: This is the strict mechanical boundary of the X/Y gantry travel where the laser beam can fire.
* **Recommended Maximum Part Bounding Box**:
  * Metric: **480 mm x 300 mm**
  * Imperial: **18.90 inches x 11.81 inches**
  * *Engineering Rationale*: Leaves a 9 mm to 10 mm perimeter margin for material hold-down pins, magnetic honeycomb clamps, and exhaust air draft without risk of gantry limit-switch collision.

---

## Material & Diode Laser Physics Constraints (20W 455nm Blue Diode)

* **Organic & Wood Materials (Ideal)**:
  * 3 mm / 5 mm Baltic birch plywood, basswood, and draftwood / MDF cut crisply with high edge squareness and minimal charring at 20W.
* **Plastics & Acrylics**:
  * **Opaque & Dark Cast Acrylic (Black, Dark Gray, Magenta, Teal, Sunset Orange)**: Absorbs 455 nm blue diode wavelengths readily and cuts cleanly.
  * **Clear & White Acrylic Consideration**: Standard 455 nm blue diode lasers transmit directly through transparent clear and pure white acrylic without absorption. For edge-lit clear light guides or white diffusers, options include:
    * Laser marking spray / laser mask coating for surface engraving.
    * Frosted or tinted cast acrylics compatible with 455 nm absorption.
    * Laser cut translucent polypropylene / diffusion film sheets layered over cut wood/dark acrylic ribs.
    * CNC or pre-cut stock blanks paired with laser-cut perimeter alignment bezels.

---

## Enclosure & Lighting Architecture (WLED Integration)

* **Enclosure Type**: Multi-tier shadowbox frame with interlocking mortise-and-tenon or box-jointed walls.
* **Layer Depth Spacing**:
  * Internal slotted side rails or 3 mm / 5 mm laser-cut spacer frames create 3D parallax depth between silhouette layers (e.g. background sunset, skyline, foreground character / palm silhouettes, front bezel).
* **WLED Microcontroller & Power**:
  * **Controller**: ESP32 (D1 Mini ESP32 or ESP32-WROOM) running WLED firmware with Wi-Fi AP/station control, Home Assistant integration, and customizable animation segments.
  * **Addressable LED Channels**:
    * WS2812B / SK6812 (5V) or WS2811 / WS2815 (12V) high-density strips (or COB addressable strip for continuous, zero-hotspot diffuse glow).
    * Segmented lighting: Independent control over the top horizon / sky, neon signage / logo elements, and lower street / foreground silhouette ambient wash.
  * **Power Supply & Input**:
    * Rear panel cutout for a 5.5 x 2.1 mm DC barrel jack or a USB-C PD trigger board (5V 3A to 5A depending on LED count).
  * **Serviceability**:
    * Removable rear access hatch held by countersunk screws or magnetic catches for easy access to the microcontroller and wiring harness.

---

## Next Steps

* Receive the inspirational media / fan artwork.
* Deconstruct artwork into multi-plane vector silhouettes and lighting tiers.
* Generate parametric cutting vectors (SVG / DXF) and 3D assembly models.
