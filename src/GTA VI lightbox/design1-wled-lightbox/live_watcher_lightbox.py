#!/usr/bin/env python3
"""
Legacy shim: live scripts now live in ONE consolidated folder:
  src/live/live_gta_vi_lightbox_design1_wled_lightbox.py

This shim keeps old FreeCAD macro paths working by forwarding to it.
Safe to delete once your macros point at src/live/ directly.
"""

import os

_CANDIDATES = [
    # Relative to this shim: <root>/src/GTA VI lightbox/design1-wled-lightbox/ -> <root>/src/live/
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "live", "live_gta_vi_lightbox_design1_wled_lightbox.py")
    if "__file__" in globals()
    else None,
    r"C:\dev\Projects\CAD\src\live\live_gta_vi_lightbox_design1_wled_lightbox.py",
]

_LAUNCHER = next((c for c in _CANDIDATES if c and os.path.isfile(c)), None)
if _LAUNCHER is None:
    raise SystemExit("Launcher not found. Expected src/live/live_gta_vi_lightbox_design1_wled_lightbox.py.")

with open(_LAUNCHER, "r", encoding="utf-8") as _f:
    _code = _f.read()

exec(_code, {"__file__": _LAUNCHER, "__name__": "__main__"})
