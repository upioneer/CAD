#!/usr/bin/env python3
"""
Live script: spool brackets and stopper collars.

Run this file ONCE inside the FreeCAD GUI (Macro -> Macros... -> Run, or
paste into the Python console). Saving spool_bracket.py then rebuilds
the models live in the 3D viewport. Only this project is watched.
"""

import os
import sys

LABEL = "spool_brackets"
TARGET_RELATIVE = os.path.join("src", "spool-brackets", "spool_bracket.py")
TARGET_FALLBACK = r"C:\dev\Projects\CAD\src\spool-brackets\spool_bracket.py"


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
