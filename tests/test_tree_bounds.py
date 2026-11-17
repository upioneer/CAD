#!/usr/bin/env python3
"""
Regression test: tree relief layers stay inside their frames and walls.

Guards the defect where a frond tip escaped past the frame, through the
wall, and outside the enclosure (front tree1 reached x=152.3 in a 300mm
box). Pure standard library; run from the repository root:

    python tests/test_tree_bounds.py

Exit code is nonzero on failure, with one line per violation.
"""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DESIGN = os.path.join(ROOT, "src", "GTA VI lightbox", "design1-wled-lightbox")
sys.path.insert(0, DESIGN)

import palm_trees as pt

# Mirror of lightbox_freecad.py enclosure params (keep in sync).
ENCLOSURE = 300.0
WALL = 3.175
PANEL_CLR = 0.5
PANEL_W = ENCLOSURE - 2.0 * WALL - 2.0 * PANEL_CLR
PANEL_H = ENCLOSURE - 2.0 * WALL - 2.0 * PANEL_CLR
WALL_IN_X = ENCLOSURE / 2.0 - WALL
WALL_IN_Y = ENCLOSURE / 2.0 - WALL
# VI window bbox (conservative: window fits inside this rect).
WIN_X = 121.2
WIN_Y = 92.0

failures = []


def check(cond, message):
    if not cond:
        failures.append(message)
        print("FAIL:", message)


def test_polys_inside_panel():
    """Every tree point of every style stays within the panel bounds."""
    for name, trees in sorted(pt.STYLES.items()):
        for ti, spec in enumerate(trees):
            for x, y in [p for poly in pt.layer_polys([spec]) for p in poly]:
                check(abs(x) <= PANEL_W / 2.0 and abs(y) <= PANEL_H / 2.0,
                      "%s tree%d escapes panel at (%.1f, %.1f)"
                      % (name, ti, x, y))


def test_trunk_bases_on_solid():
    """Every trunk base lands on solid panel outside the VI window.

    Sound but conservative: the window fits inside the bbox, so a base
    outside the bbox is certainly on solid. (A base inside the bbox but
    outside the chevron would need a polygon test; none exist today.)
    """
    for name, trees in sorted(pt.STYLES.items()):
        for ti, spec in enumerate(trees):
            bx, by = spec["base"]
            check(abs(bx) > WIN_X or abs(by) > WIN_Y,
                  "%s tree%d trunk base (%.1f, %.1f) inside window void"
                  % (name, ti, bx, by))


def test_panel_inside_walls():
    """The tree panel itself clears the wall inner faces."""
    check(PANEL_W / 2.0 < WALL_IN_X and PANEL_H / 2.0 < WALL_IN_Y,
          "panel %gx%g exceeds wall inner %gx%g"
          % (PANEL_W, PANEL_H, WALL_IN_X * 2, WALL_IN_Y * 2))


if __name__ == "__main__":
    test_polys_inside_panel()
    test_trunk_bases_on_solid()
    test_panel_inside_walls()
    if failures:
        print("%d violation(s)" % len(failures))
        sys.exit(1)
    print("tree bounds OK: %s inside %gx%g panel"
          % (", ".join("%s(%d trees)" % (k, len(v))
                       for k, v in sorted(pt.STYLES.items())),
             PANEL_W, PANEL_H))
