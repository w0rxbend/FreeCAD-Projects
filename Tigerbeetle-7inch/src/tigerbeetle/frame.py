"""The carbon parts and standoffs as solids, in their installed positions.

plate_bottom   2 mm   under the arms; carries the tail (receiver, VTX antenna, rear standoffs)
arm            5 mm   one part, four times: two placed as traced, two turned over
plate_camera   2 mm   on the arms; carries the front bay and the camera standoffs
plate_top      2 mm   on eight standoffs; the battery deck
"""

from functools import lru_cache

import numpy as np
from build123d import Align, Axis, Cylinder, Edge, Face, Part, Plane, Pos, Vector, Wire, extrude

from tigerbeetle import model as M

CARBON, ALUMINIUM = "carbon", "aluminium"
MIN_Z = (Align.CENTER, Align.CENTER, Align.MIN)


def spline(pts: np.ndarray) -> Wire:
    """A closed smooth curve through the contour, resampled every RESAMPLE mm."""
    p = M.resample(np.asarray(pts))
    return Wire([Edge.make_spline([Vector(float(x), float(y), 0.0) for x, y in p], periodic=True)])


def circle(x: float, y: float, d: float) -> Wire:
    return Wire([Edge.make_circle(d / 2).translate(Vector(x, y, 0))])


def face(part: M.Part2D) -> Face:
    inner = [spline(w) for w in part.windows] + [circle(h.x, h.y, h.d) for h in part.holes]
    f = Face(spline(part.outline), inner)
    for x, y, d in part.reliefs:
        f = (f - Face(circle(x, y, d))).faces()[0]
    for c in part.cuts:
        poly = Wire.make_polygon([Vector(float(px), float(py), 0) for px, py in c], close=True)
        f = max((f - Face(poly)).faces(), key=lambda g: g.area)
    assert f.is_valid, part.name
    return f


def solid(part: M.Part2D) -> Part:
    out = extrude(face(part), amount=part.thickness)
    out.label = part.name
    return out


PLATES = {
    "plate_bottom": ("bottom_plate", M.Z_BOTTOM),
    "plate_camera": ("camera_plate", M.Z_CAMERA),
    "plate_top": ("top_plate", M.Z_TOP),
}


@lru_cache(maxsize=1)
def arm_solid() -> Part:
    """The arm in its own frame (motor at the origin, root along +X), as cut."""
    pl, part = M.arms()["front_right"]
    return solid(part)


def _place_arm(quad: str) -> Part:
    pl, part = M.arms()[quad.replace("left", "right")]
    return on_arm(solid(part), quad)


def on_arm(s: Part, quad: str) -> Part:
    """A solid drawn in the arm's own frame (arm underside at Z = 0) -> its place on the given arm."""
    pl, _part = M.arms()[quad.replace("left", "right")]
    if pl.mirror:
        s = s.mirror(Plane.XZ)
    s = s.rotate(Axis.Z, pl.angle).translate(Vector(pl.x, pl.y, M.Z_ARM))
    if "left" in quad:
        s = s.mirror(Plane.YZ)
    return s


def standoffs() -> dict[str, tuple[float, float, float, float]]:
    """name -> (x, y, z0, height): one under every hole of the top plate, standing on the highest
    plate below that has the same bolt."""
    out = {}
    for members in M.bolts().values():
        names = [n for n, _h in members]
        if "top_plate" not in names or len(names) < 2:  # a hole in the top plate alone is for an accessory
            continue
        h = members[0][1]
        z0 = M.Z_CAMERA + M.T_PLATE if "camera_plate" in names else M.Z_ARM
        side = "right" if h.x > 0 else "left"
        where = "front" if h.y > 60 else "rear" if h.y < -60 else "arm_front" if h.y > 0 else "arm_rear"
        name = f"standoff_{where}_{side}"
        assert name not in out, name
        out[name] = (h.x, h.y, z0, M.Z_TOP - z0)
    return out


def standoff(height: float) -> Part:
    return Cylinder(M.STANDOFF_OD / 2, height, align=MIN_Z) - Pos(0, 0, -1) * Cylinder(1.25, height + 2, align=MIN_Z)


@lru_cache(maxsize=1)
def build() -> dict[str, tuple[Part, str]]:
    out = {}
    for name, (plate, z) in PLATES.items():
        part = solid(M.plates()[plate]).translate(Vector(0, 0, z))
        out[name] = (part, CARBON)
    for quad in ("front_right", "front_left", "rear_right", "rear_left"):
        out[f"arm_{quad}"] = (_place_arm(quad), CARBON)
    for name, (x, y, z0, h) in standoffs().items():
        out[name] = (standoff(h).translate(Vector(x, y, z0)), ALUMINIUM)
    for name, (part, _m) in out.items():
        part.label = name
    return out


def parts() -> dict[str, Part]:
    return {n: p for n, (p, _m) in build().items()}


def motors() -> dict[str, tuple[float, float]]:
    out = {}
    for quad, (pl, _part) in M.arms().items():
        x, y = pl.apply(np.zeros((1, 2)))[0]
        out[quad] = (float(x), float(y))
        out[quad.replace("right", "left")] = (-float(x), float(y))
    return out
