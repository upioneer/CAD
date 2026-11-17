#!/usr/bin/env python3
"""
Live script: 10in rack 2U dual 3.5in LCD tray plate.

Run this file ONCE inside the FreeCAD GUI (Macro -> Macros... -> Run, or
paste into the Python console). Saving rack_plate_freecad.py then rebuilds
the model live in the 3D viewport. Only this project is watched.
"""

import os
import sys

LABEL = "10in_rack_2u_lcd"
TARGET_RELATIVE = os.path.join("src", "10in-rack-2u-lcd", "rack_plate_freecad.py")
TARGET_FALLBACK = r"C:\dev\Projects\CAD\src\10in-rack-2u-lcd\rack_plate_freecad.py"


def _live_dir():
    try:
        return os.path.dirname(os.path.abspath(__file__))
    except Exception:
        return r"C:\dev\Projects\CAD\src\live"


LIVE_DIR = _live_dir()
if LIVE_DIR not in sys.path:
    sys.path.insert(0, LIVE_DIR)

REPO_ROOT = os.path.dirname(os.path.dirname(LIVE_DIR))

from live_core import watch  # noqa: E402

watch(LABEL, [os.path.join(REPO_ROOT, TARGET_RELATIVE), TARGET_FALLBACK])
