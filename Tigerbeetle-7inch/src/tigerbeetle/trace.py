"""From the two traced A4 sheets to the numbers the CAD model is built from.

The owner laid each carbon part on an A4 sheet and ran a red pen round it. The sheets were
scanned at 300 dpi, so one pixel is 25.4 / 300 = 0.0847 mm. This module:

  1. separates the red ink and finds the five parts (one camera plate and two tracings of the
     arm on sheet 1, the bottom plate and the top plate on sheet 2);
  2. turns each tracing into a material mask: inside the outline, outside every cut-out. The pen
     is held against the part, so the part's edge is the inner edge of the outline's ink and the
     outer edge of each cut-out's ink;
  3. finds each plate's mirror axis by making the mask agree with its own reflection, and stands
     the plate on it; the two arm tracings (one of each face) are laid onto each other;
  4. averages: a plate with its reflection, the arm with its second tracing, then smooths the edge
     by 0.3 mm (the hand's wobble) and keeps the 50 % line;
  5. measures every round hole (centre, traced diameter) for `model.py` to snap to real sizes.

Nothing here is idealised beyond that averaging. `model.py` takes the decisions (hole sizes,
which holes mate, the assembly); they are written down there, not hidden in a fit.

Run `tigerbeetle trace` to regenerate data/reconstruction.json from the scans.
"""

import json
from functools import lru_cache
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
PX = 25.4 / 300  # mm per pixel
GRID = 0.1  # mm: the raster the averaging is done on
SMOOTH = 0.3  # mm: Gaussian blur of the averaged edge
OUT = Path(__file__).with_name("data") / "reconstruction.json"
PARTS = {(1, 0): "camera_plate", (1, 1): "arm_b", (1, 2): "arm_a", (2, 0): "top_plate", (2, 1): "bottom_plate"}


def _ink(scan: int) -> np.ndarray:
    from PIL import Image
    from scipy import ndimage as ndi

    im = np.asarray(Image.open(ROOT / "references" / f"Scan_{scan}.jpeg").convert("RGB")).astype(int)
    ink = (im[..., 0] - (im[..., 1] + im[..., 2]) / 2 > 40) & (im[..., 0] > 120)
    return ndi.binary_closing(ink, iterations=2)


@lru_cache(maxsize=1)
def tracings() -> dict:
    """name -> (material mask, list of (hole mask) in page pixels)."""
    from scipy import ndimage as ndi

    out = {}
    for scan in (1, 2):
        ink = _ink(scan)
        lab, n = ndi.label(ink)
        sizes = ndi.sum(ink, lab, range(1, n + 1))
        outlines = sorted([i + 1 for i, s in enumerate(sizes) if s > 20000], key=lambda i: -sizes[i - 1])
        for k, oid in enumerate(outlines):
            ring = lab == oid
            filled = ndi.binary_fill_holes(ring)
            # The plate is the one big piece of paper inside the outline that no ink crosses. Everything
            # else inside (a cut-out, a cut-out traced twice, the sliver between two passes of the pen)
            # is a hole. The ink is closed a little first, so a gap of up to 1.4 mm where the pen lifted does not
            # join a cut-out to the plate.
            closed = ndi.binary_closing(ink, iterations=8) | ring
            pieces, m = ndi.label(filled & ~closed)
            sizes_p = ndi.sum(np.ones_like(pieces), pieces, range(1, m + 1))
            material = pieces == (int(np.argmax(sizes_p)) + 1)
            # give back the thin band the closing took off the plate's own edges
            material = ndi.binary_dilation(material, iterations=1) & filled & ~ink
            voids, m = ndi.label(filled & ~material & ~ndi.binary_dilation(ring, iterations=2))
            holes = []
            for j in range(1, m + 1):
                hole = voids == j
                if hole.sum() >= 30:  # a speck of ink is not a cut-out
                    holes.append(hole)
            material = ndi.binary_fill_holes(material) & ~np.any(holes, axis=0) if holes else material
            out[PARTS[(scan, k)]] = (ndi.binary_opening(material, iterations=1), holes)
    return out


def _sample(mask: np.ndarray, T: np.ndarray, extent: tuple[float, float, float, float]) -> np.ndarray:
    """Resample a page mask onto a GRID raster in part coordinates. T maps part mm (x, y, 1) to page px."""
    from scipy import ndimage as ndi

    x0, x1, y0, y1 = extent
    xs = np.linspace(x0, x1, round((x1 - x0) / GRID) + 1)  # extents are whole multiples of GRID
    ys = np.linspace(y0, y1, round((y1 - y0) / GRID) + 1)
    X, Y = np.meshgrid(xs, ys)
    P = T @ np.vstack([X.ravel(), Y.ravel(), np.ones(X.size)])
    vals = ndi.map_coordinates(mask.astype(float), [P[1], P[0]], order=1, cval=0.0)
    return vals.reshape(X.shape)


def _frame(theta: float, cx: float, cy: float, mirror: bool = False) -> np.ndarray:
    """Part mm -> page px: part +Y is page up, rotated by theta about the page point (cx, cy)."""
    c, s = np.cos(theta), np.sin(theta)
    sx = -1.0 if mirror else 1.0
    # page u = cx + (c*x*sx - s*y)/PX ... with page v pointing down
    return np.array([[c * sx / PX, s / PX, cx], [s * sx / PX, -c / PX, cy], [0, 0, 1]])


def _centroid(mask: np.ndarray) -> np.ndarray:
    ys, xs = np.nonzero(mask)
    return np.array([xs.mean(), ys.mean()])


def _mirror_fit(mask: np.ndarray) -> tuple[float, float, float]:
    """(theta, cx, cy): the page line about which the mask best matches its own reflection."""
    from scipy import optimize

    cx, cy = _centroid(mask)
    ys, xs = np.nonzero(mask)
    half = max(xs.max() - xs.min(), ys.max() - ys.min()) * PX / 2 + 5
    ext = (-half, half, -half, half)
    small = mask[::2, ::2]

    def cost(p):
        T = _frame(p[0], p[1], cy)
        Ts = T.copy()
        Ts[:, 0] = T[:, 0] * -1
        Ts[2, 0] = 0
        g = _sample(small, np.diag([0.5, 0.5, 1]) @ T, ext)
        h = _sample(small, np.diag([0.5, 0.5, 1]) @ Ts, ext)
        return -((g * h).sum() / ((g + h).sum() / 2 + 1e-9))

    best = optimize.minimize(cost, [0.0, cx], method="Nelder-Mead", options={"xatol": 1e-4, "fatol": 1e-6})
    return float(best.x[0]), float(best.x[1]), float(cy)


def _blur_threshold(field: np.ndarray) -> np.ndarray:
    from scipy import ndimage as ndi

    return ndi.gaussian_filter(field, SMOOTH / GRID)


def _contours(field: np.ndarray, extent) -> list[np.ndarray]:
    """Closed 50 % iso-lines of a smoothed field, in part mm, counter-clockwise for the outer one."""
    from skimage import measure

    x0, _x1, y0, _y1 = extent
    padded = np.pad(field, 2)
    out = []
    for c in measure.find_contours(padded, 0.5):
        pts = np.c_[(c[:, 1] - 2) * GRID + x0, (c[:, 0] - 2) * GRID + y0]
        if len(pts) > 20:
            out.append(pts)
    return out


def _round_holes(holes, T_inv) -> list[dict]:
    """Every cut-out that is a circle: its centre in part mm and its traced diameter."""
    out = []
    for h in holes:
        ys, xs = np.nonzero(h)
        area = h.sum() * PX * PX
        ext = (max(xs.max() - xs.min(), ys.max() - ys.min()) + 1) * PX
        roundness = area / (np.pi * ext * ext / 4)
        c = T_inv @ np.array([xs.mean(), ys.mean(), 1.0])
        out.append(
            {"x": float(c[0]), "y": float(c[1]), "d": float(2 * np.sqrt(area / np.pi)), "round": float(roundness)}
        )
    return out


def _plate(name: str) -> dict:
    mask, holes = tracings()[name]
    theta, cx, cy = _mirror_fit(mask)
    T = _frame(theta, cx, cy)
    ys, xs = np.nonzero(mask)
    corners = np.linalg.inv(T) @ np.array(
        [[xs.min(), xs.max(), xs.min(), xs.max()], [ys.min(), ys.min(), ys.max(), ys.max()], [1, 1, 1, 1]]
    )
    snap = lambda v: round(v / GRID) * GRID  # noqa: E731
    hx = snap(np.abs(corners[0]).max() + 5)  # x runs from -hx to hx: flipping the raster reflects the plate
    ext = (-hx, hx, snap(corners[1].min() - 5), snap(corners[1].max() + 5))
    g = _sample(mask, T, ext)
    gf = g[:, ::-1]  # the grid is symmetric about x = 0, so this is the plate's reflection
    # The outline: the plate and its reflection averaged. Inside it: a cut-out traced on either side is a
    # cut-out on both, so a hole marked on one side only, or a cut-out whose tracing went wrong on one
    # side (a double loop with a gap), comes out whole.
    from scipy import ndimage as ndi

    avg = (g + gf) / 2
    inside = ndi.binary_erosion(ndi.binary_fill_holes(avg > 0.5), iterations=int(1.5 / GRID))
    field = _blur_threshold(np.where(inside, np.minimum(g, gf), avg))
    agree = np.minimum(g, gf).sum() / np.maximum(g, gf).sum()
    return {
        "page_axis": {"theta_deg": float(np.degrees(theta)), "u": cx, "v": cy},
        "to_page": T.tolist(),  # part mm (x, y, 1) -> page px, before model.py moves the plate onto the datum
        "mirror_agreement": float(agree),
        "contours": [c.tolist() for c in _contours(field, ext)],
        "holes": _round_holes(holes, np.linalg.inv(T)),
    }


def _arm() -> dict:
    """Both tracings of the arm, laid onto each other and averaged. Arm frame: motor centre at the origin,
    +X along the arm towards its root."""
    from scipy import optimize

    data = {}
    for name in ("arm_a", "arm_b"):
        mask, holes = tracings()[name]
        # the biggest round hole is the motor bore
        cs = [(_centroid(h), h.sum()) for h in holes]
        motor = max(cs, key=lambda t: t[1])[0]
        far = _centroid(mask)  # the root end carries most of the length: the centroid sits towards it
        theta = np.arctan2(far[1] - motor[1], far[0] - motor[0])  # part +X runs from the motor to the root
        data[name] = (mask, holes, motor, theta)
    ext = (-30.0, 160.0, -30.0, 30.0)

    def placed(name, p, mirror):
        mask, _h, motor, theta = data[name]
        T = _frame(theta + p[0], motor[0] + p[1] / PX, motor[1] + p[2] / PX, mirror)
        return T, _sample(mask, T, ext)

    Ta, a = placed("arm_a", (0, 0, 0), False)
    best = None
    for mirror in (False, True):

        def cost(p, mirror=mirror):
            return -(np.minimum(a, placed("arm_b", p, mirror)[1]).sum())

        for t0 in (0.0, np.pi):
            r = optimize.minimize(cost, [t0, 0, 0], method="Nelder-Mead", options={"xatol": 1e-4, "fatol": 1e-3})
            if best is None or r.fun < best[0]:
                best = (r.fun, r.x, mirror)
    Tb, b = placed("arm_b", best[1], best[2])
    agree = np.minimum(a, b).sum() / np.maximum(a, b).sum()
    from scipy import ndimage as ndi

    avg = (a + b) / 2  # as for the plates: the outline averaged, a cut-out on either tracing is a cut-out
    inside = ndi.binary_erosion(ndi.binary_fill_holes(avg > 0.5), iterations=int(1.5 / GRID))
    field = _blur_threshold(np.where(inside, np.minimum(a, b), avg))
    holes = []
    for name, T in (("arm_a", Ta), ("arm_b", Tb)):
        for h in _round_holes(data[name][1], np.linalg.inv(T)):
            h["tracing"] = name
            holes.append(h)
    return {
        "to_page": {"arm_a": Ta.tolist(), "arm_b": Tb.tolist()},  # arm mm -> page px of each tracing
        "second_tracing_mirrored": bool(best[2]),
        "tracing_agreement": float(agree),
        "contours": [c.tolist() for c in _contours(field, ext)],
        "holes": holes,
    }


def run() -> dict:
    result = {
        "mm_per_px": PX,
        "smoothing_mm": SMOOTH,
        "plates": {name: _plate(name) for name in ("camera_plate", "bottom_plate", "top_plate")},
        "arm": _arm(),
    }
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(result, separators=(",", ":")))
    return result


if __name__ == "__main__":
    r = run()
    for n, p in r["plates"].items():
        print(
            n,
            "mirror agreement",
            round(p["mirror_agreement"], 4),
            "contours",
            len(p["contours"]),
            "holes",
            len(p["holes"]),
        )
    a = r["arm"]
    print(
        "arm: tracings agree",
        round(a["tracing_agreement"], 4),
        "mirrored",
        a["second_tracing_mirrored"],
        "contours",
        len(a["contours"]),
    )
