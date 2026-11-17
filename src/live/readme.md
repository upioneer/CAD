# Live Launchers

* One consolidated folder for every project's FreeCAD GUI live-reload launcher. Run a launcher once inside FreeCAD (Macro -> Run); saving its target script rebuilds that project live in the viewport.
* Never run `live_core.py` directly. It is the shared reload engine.

## Naming Rule

* File: `live_<src-relative-dir>.py`, lowercased, with `/`, spaces, and `-` all mapped to `_`.
* `LABEL` inside the file equals the filename slug (no `live_` prefix, no `.py`).
* The filename therefore always identifies its project with no guessing.

## Registry

* `live_10in_rack_2u_lcd.py` -> `src/10in-rack-2u-lcd/rack_plate_freecad.py`
* `live_10in_rack_lcd_kvm.py` -> `src/10in-rack-lcd-kvm/kvm_plate_freecad.py`
* `live_8ft_maker_station_cad.py` -> `src/8ft-maker-station/cad/workbench_freecad.py`
* `live_gta_vi_lightbox_design1_wled_lightbox.py` -> `src/GTA VI lightbox/design1-wled-lightbox/lightbox_freecad.py`
* `live_spool_brackets.py` -> `src/spool-brackets/spool_bracket.py`

## Adding a Project

* Copy any launcher, rename it per the rule, set its `LABEL` and target paths, and add one registry line above.
