"""Feet: TPU pucks under the six body bolts. The quad stands on them, not on the bolt heads or the keel."""

from build123d import Axis, Plane, revolve

from vektor.accessories.base import D_HEAD, D_M3, Accessory, P, cyl, poly
from vektor.geometry import body_posts

R, H, CHAMFER, UNDER_HEAD = 6.0, 6.0, 1.5, 2.0


def _one(xy):
    section = poly([(0, 0), (R, 0), (R, -H + CHAMFER), (R - CHAMFER, -H), (0, -H)])
    body = revolve(Plane.XZ * section, Axis.Z, 360).translate((xy[0], xy[1], P.Z_LOWER))
    body -= cyl(*xy, -H - 1, 1, D_M3)
    body -= cyl(*xy, -H - 1, -UNDER_HEAD, D_HEAD)
    return body


def build() -> list[Accessory]:
    feet = [_one(p) for p in body_posts()]
    return [
        Accessory(
            "foot",
            "Foot",
            feet[0],
            bed=(0, 0, 1),
            qty=len(feet),
            instances=tuple(feet[1:]),
            color="accent",
            checks=[("TPU under each bolt head", UNDER_HEAD >= 1.5, f"{UNDER_HEAD:g} mm")],
            hardware="the six body bolts, 5 mm longer",
        )
    ]
