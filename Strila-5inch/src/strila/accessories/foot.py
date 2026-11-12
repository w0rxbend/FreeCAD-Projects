"""Feet: a TPU pad under the tip of each sandwich leg, on the outer arm bolt.

Four of them, 88 x 74 mm apart, are the lowest points of the quad: it stands level and the
screw heads under the floor never meet the ground.
"""

from build123d import Axis, Plane, revolve
from zhalo.accessories.kit import D_M3_FREE, D_M3_HEAD, Accessory, P, cylinder, poly

RADIUS = 6.5
HEIGHT = 4.5
CHAMFER = 1.2
UNDER_HEAD = 2.0


def _one(xy):
    section = poly(
        [(0.0, 0.0), (RADIUS, 0.0), (RADIUS, -HEIGHT + CHAMFER), (RADIUS - CHAMFER, -HEIGHT), (0.0, -HEIGHT)]
    )
    body = revolve(Plane.XZ * section, Axis.Z, 360).translate((xy[0], xy[1], 0.0))
    body -= cylinder(*xy, -HEIGHT - 1, 1, D_M3_FREE)
    body -= cylinder(*xy, -HEIGHT - 1, -UNDER_HEAD, D_M3_HEAD)
    return body


def build() -> list[Accessory]:
    feet = [_one(p) for p in P.quad(P.C)]
    own = [
        (
            "the feet are the lowest point",
            -HEIGHT < -2.6 - 1.0,
            f"feet Z {-HEIGHT:.1f}, nose shoe Z -2.6, screw heads Z -1.7",
        ),
        ("TPU under the screw head", UNDER_HEAD >= 1.5, f"{UNDER_HEAD:.1f} mm"),
    ]
    return [
        Accessory(
            "foot",
            "Foot",
            feet[0],
            bed=(0, 0, 1),
            qty=4,
            checks=own,
            instances=tuple(feet[1:]),
            color="accent",
            hardware="uses the outer arm bolts (M3x16 instead of M3x14)",
            notes="One under each leg tip; the outer arm bolt goes through it, head buried in the foot.",
        )
    ]
