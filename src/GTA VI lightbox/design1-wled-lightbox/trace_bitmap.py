"""Trace the official GTA wordmark bitmap into exact vector outlines.

Source: src/GTA VI lightbox/media/gta.svg.webp (white art on black).
Output: text_lockup_vectors.json -- one entry per connected white region
with its counter holes, in source-pixel coords (y DOWN). The FreeCAD build
loads the JSON (no imaging deps needed inside FreeCAD) and scales the whole
lockup uniformly so internal proportions stay pixel-faithful to the art.

Only stdlib + numpy + PIL + scipy (system python, NOT freecadcmd).

Self-test:  python trace_bitmap.py
  Traces the artwork, prints region/hole counts and IoU fidelity vs the
  source mask, and writes a _trace_check.png overlay for visual review.
"""

import json
import math
import os

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
MEDIA = os.path.abspath(os.path.join(HERE, "..", "media"))
SRC_IMAGE = os.path.join(MEDIA, "gta.svg.webp")
OUT_JSON = os.path.join(HERE, "text_lockup_vectors.json")

SUPERSAMPLE = 4          # trace at 4x, then downscale coords
BLUR_SIGMA = 0.75        # px at 4x; kills webp ringing, keeps corners crisp
SPECK_PX2 = 25           # drop white specks / fill black specks below this (src px^2)
RDP_EPS_PX = 0.10        # polygon simplify tolerance, source px (~0.03mm final)


# --------------------------------------------------------------------------
# marching squares iso-contours
# --------------------------------------------------------------------------

def _edge_point(axis, fixed, v0, v1, iso, c0):
    """Interpolated crossing along one cell edge (working-scale coords)."""
    t = (iso - v0) / (v1 - v0) if v1 != v0 else 0.5
    p = c0 + t
    return (p, fixed) if axis == 0 else (fixed, p)


def _marching_segments(field, iso=0.5):
    """All iso-contour segments of a float field as ((x0,y0),(x1,y1)) pairs."""
    h, w = field.shape
    segs = []
    for y in range(h - 1):
        for x in range(w - 1):
            tl = field[y, x]
            tr = field[y, x + 1]
            br = field[y + 1, x + 1]
            bl = field[y + 1, x]
            idx = (8 if tl >= iso else 0) | (4 if tr >= iso else 0) \
                | (2 if br >= iso else 0) | (1 if bl >= iso else 0)
            if idx in (0, 15):
                continue
            t = _edge_point(0, y, tl, tr, iso, x)
            r = _edge_point(1, x + 1, tr, br, iso, y)
            b = _edge_point(0, y + 1, bl, br, iso, x)
            l = _edge_point(1, x, tl, bl, iso, y)  # noqa: E741
            if idx in (1, 14):
                segs.append((l, b))
            elif idx in (2, 13):
                segs.append((b, r))
            elif idx in (3, 12):
                segs.append((l, r))
            elif idx in (4, 11):
                segs.append((t, r))
            elif idx == 5:
                if (tl + tr + br + bl) / 4.0 >= iso:
                    segs += [(t, l), (b, r)]
                else:
                    segs += [(t, r), (l, b)]
            elif idx in (6, 9):
                segs.append((t, b))
            elif idx in (7, 8):
                segs.append((t, l))
            elif idx == 10:
                if (tl + tr + br + bl) / 4.0 >= iso:
                    segs += [(t, r), (l, b)]
                else:
                    segs += [(t, l), (b, r)]
    return segs


def _chain_loops(segs):
    """Chain unordered segments into closed loops. Returns (loops, forced)."""
    key = lambda p: (round(p[0], 4), round(p[1], 4))
    touch = {}
    for i, (a, b) in enumerate(segs):
        touch.setdefault(key(a), []).append(i)
        touch.setdefault(key(b), []).append(i)
    used = bytearray(len(segs))
    loops, forced = [], 0
    for i, (a, b) in enumerate(segs):
        if used[i]:
            continue
        used[i] = 1
        loop = [a, b]
        while True:
            nxt = None
            for j in touch.get(key(loop[-1]), ()):
                if not used[j]:
                    nxt = j
                    break
            if nxt is None:
                break
            used[nxt] = 1
            c, d = segs[nxt]
            loop.append(d if key(c) == key(loop[-1]) else c)
        if key(loop[-1]) != key(loop[0]):
            forced += 1
        else:
            loop.pop()
        if len(loop) >= 3:
            loops.append(loop)
    return loops, forced


# --------------------------------------------------------------------------
# polygon utils (pure python)
# --------------------------------------------------------------------------

def _signed_area(poly):
    return sum(
        p[0] * poly[(i + 1) % len(poly)][1]
        - poly[(i + 1) % len(poly)][0] * p[1]
        for i, p in enumerate(poly)) / 2.0


def _point_in_poly(pt, poly):
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if (yi > pt[1]) != (yj > pt[1]) and \
                pt[0] < (xj - xi) * (pt[1] - yi) / (yj - yi) + xi:
            inside = not inside
        j = i
    return inside


def _rdp(points, eps):
    """Iterative Ramer-Douglas-Peucker. Keeps first/last, drops strays."""
    if len(points) < 3:
        return list(points)
    keep = bytearray(len(points))
    keep[0] = keep[-1] = 1
    stack = [(0, len(points) - 1)]
    while stack:
        s, e = stack.pop()
        ax, ay = points[s]
        bx, by = points[e]
        dx, dy = bx - ax, by - ay
        norm = math.hypot(dx, dy) or 1.0
        dmax, imax = 0.0, -1
        for i in range(s + 1, e):
            px, py = points[i]
            d = abs(dy * px - dx * py + bx * ay - by * ax) / norm
            if d > dmax:
                dmax, imax = d, i
        if dmax > eps:
            keep[imax] = 1
            stack.append((s, imax))
            stack.append((imax, e))
    return [p for p, k in zip(points, keep) if k]


def _rdp_closed(loop, eps):
    """RDP for a closed loop (no duplicated seam point in/out)."""
    if len(loop) < 4:
        return list(loop)
    x0, y0 = loop[0]
    # split at the point farthest from loop[0] so neither chain is degenerate
    f = max(range(len(loop)),
            key=lambda i: (loop[i][0] - x0) ** 2 + (loop[i][1] - y0) ** 2)
    if f == 0:
        return list(loop)
    first = _rdp(loop[:f + 1], eps)
    second = _rdp(loop[f:] + [loop[0]], eps)
    return first + second[1:-1]


# --------------------------------------------------------------------------
# main trace
# --------------------------------------------------------------------------

def trace_artwork(path=SRC_IMAGE, scale=SUPERSAMPLE, sigma=BLUR_SIGMA,
                  speck=SPECK_PX2, eps=RDP_EPS_PX):
    """Trace white-on-black art. Returns dict with regions + fidelity stats."""
    gray = np.asarray(Image.open(path).convert("L"), dtype=np.float64) / 255.0
    mask = gray > 0.5
    # drop specks far below real-feature size (smallest real hole is 84px^2)
    lab, n = ndimage.label(mask, structure=np.ones((3, 3)))
    sizes = np.bincount(lab.ravel())
    mask = mask & (sizes[lab] >= speck)
    holes = ndimage.binary_fill_holes(mask) ^ mask
    hlab, hn = ndimage.label(holes, structure=np.ones((3, 3)))
    hsizes = np.bincount(hlab.ravel())
    mask = mask | (holes & (hsizes[hlab] < speck))

    h0, w0 = mask.shape
    work = np.asarray(Image.fromarray((gray * 255).astype(np.uint8)).resize(
        (w0 * scale, h0 * scale), Image.LANCZOS), dtype=np.float64) / 255.0
    work = ndimage.gaussian_filter(work, sigma)
    loops, forced = _chain_loops(_marching_segments(work))
    loops = [[(x / scale, y / scale) for x, y in lp] for lp in loops]
    loops = [lp for lp in loops if abs(_signed_area(lp)) > 1e-6]

    # nesting: even depth = outer, odd = hole of smallest containing outer
    areas = [abs(_signed_area(lp)) for lp in loops]
    contains = [[_point_in_poly(loops[i][0], loops[j]) for j in range(len(loops))]
                for i in range(len(loops))]
    regions, hole_of = [], {}
    for i, lp in enumerate(loops):
        holders = [j for j in range(len(loops))
                   if i != j and contains[i][j]]
        if len(holders) % 2 == 0:
            regions.append({"outer": lp, "holes": [], "_idx": i})
        else:
            parent = min(holders, key=lambda j: areas[j])
            hole_of.setdefault(parent, []).append(lp)
    by_idx = {r["_idx"]: r for r in regions}
    for p, hs in hole_of.items():
        by_idx[p]["holes"].extend(hs)

    # simplify + strip degenerate points
    for r in regions:
        del r["_idx"]
        r["outer"] = _clean(_rdp_closed(r["outer"], eps))
        r["holes"] = [_clean(_rdp_closed(h, eps)) for h in r["holes"]]
        r["holes"] = [h for h in r["holes"] if len(h) >= 3]
    regions = [r for r in regions if len(r["outer"]) >= 3]

    # fidelity: re-rasterize at source resolution, IoU vs source mask
    check = Image.new("1", (w0, h0), 0)
    cd = ImageDraw.Draw(check)
    for r in regions:
        cd.polygon([(x, y) for x, y in r["outer"]], fill=1)
        for h in r["holes"]:
            cd.polygon([(x, y) for x, y in h], fill=0)
    back = np.asarray(check, dtype=bool)
    inter = int((back & mask).sum())
    union = int((back | mask).sum())
    allx = [x for r in regions for x, y in r["outer"]]
    ally = [y for r in regions for x, y in r["outer"]]
    return {
        "size": [w0, h0],
        "bbox": [min(allx), min(ally), max(allx), max(ally)],
        "regions": regions,
        "forced_closures": forced,
        "iou": inter / union if union else 0.0,
        "mismatch_px": int((back != mask).sum()),
    }


def _clean(poly):
    out = []
    for p in poly:
        if not out or math.hypot(p[0] - out[-1][0], p[1] - out[-1][1]) > 1e-9:
            out.append((round(p[0], 3), round(p[1], 3)))
    return out


def write_lockup_json(path=OUT_JSON, art=SRC_IMAGE):
    res = trace_artwork(art)
    data = {
        "source": os.path.basename(art),
        "size": res["size"],
        "bbox": [round(v, 3) for v in res["bbox"]],
        "y_down": True,
        "regions": [
            {"outer": r["outer"], "holes": r["holes"]} for r in res["regions"]
        ],
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f)
    return res


if __name__ == "__main__":
    res = trace_artwork()
    print("regions: %d  holes: %d  forced: %d" % (
        len(res["regions"]), sum(len(r["holes"]) for r in res["regions"]),
        res["forced_closures"]))
    print("bbox: %s" % ([round(v, 1) for v in res["bbox"]],))
    print("IoU vs source: %.5f  mismatch px: %d" % (
        res["iou"], res["mismatch_px"]))
    npts = sum(len(r["outer"]) + sum(len(h) for h in r["holes"])
               for r in res["regions"])
    print("total polygon points: %d" % npts)
    # overlay check: source edges (gray) vs traced loops (magenta/green)
    w0, h0 = res["size"]
    gray = np.asarray(Image.open(SRC_IMAGE).convert("L"))
    edge = np.zeros((h0, w0), bool)
    edge[:-1, :] |= (gray[:-1, :] > 128) != (gray[1:, :] > 128)
    edge[:, :-1] |= (gray[:, :-1] > 128) != (gray[:, 1:] > 128)
    ov = Image.new("RGB", (w0, h0), (0, 0, 0))
    opx = ov.load()
    for y in range(h0):
        for x in range(w0):
            if edge[y, x]:
                opx[x, y] = (120, 120, 120)
    od = ImageDraw.Draw(ov)
    for r in res["regions"]:
        o = r["outer"]
        od.line(o + [o[0]], fill=(255, 47, 179))
        for h in r["holes"]:
            od.line(h + [h[0]], fill=(80, 255, 120))
    out = os.path.join(HERE, "_trace_check.png")
    ov.resize((w0 * 2, h0 * 2), Image.NEAREST).save(out)
    print("wrote", out)
