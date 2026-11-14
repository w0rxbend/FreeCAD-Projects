"""Feet: TPU pucks under the bolt heads on the underside of the bottom plate.

Six of them: under the inner root bolt of each arm and under the two tail standoffs. They are the
lowest points of the quad, so it stands on TPU and the bolt heads never meet the ground.
"""

from build123d import Axis, Plane, revolve
from zhalo.accessories.kit import D_M3_FREE, D_M3_HEAD, Accessory, cylinder, poly

from tigerbeetle import frame as F
from tigerbeetle import model as M

RADIUS, HEIGHT, CHAMFER, UNDER_HEAD = 6.0, 5.0, 1.5, 2.0


def _one(xy):
    section = poly(
        [(0.0, 0.0), (RADIUS, 0.0), (RADIUS, -HEIGHT + CHAMFER), (RADIUS - CHAMFER, -HEIGHT), (0.0, -HEIGHT)]
    )
    body = revolve(Plane.XZ * section, Axis.Z, 360).translate((xy[0], xy[1], M.Z_BOTTOM))
    body -= cylinder(*xy, -HEIGHT - 1, 1, D_M3_FREE)
    body -= cylinder(*xy, -HEIGHT - 1, -UNDER_HEAD, D_M3_HEAD)
    return body


def spots() -> list[tuple[float, float]]:
    """The inner root bolt of each arm (the one nearer the stack) and the tail standoffs."""
    out = []
    for pl, part in M.arms().values():
        roots = [h for h in part.holes if h.group.startswith("root:")]
        inner = min(roots, key=lambda h: abs(pl.apply([[h.x, h.y]])[0][1]))
        x, y = pl.apply([[inner.x, inner.y]])[0]
        out += [(float(x), float(y)), (-float(x), float(y))]
    s = F.standoffs()["standoff_rear_right"]
    out += [(s[0], s[1]), (-s[0], s[1])]
    return out


def build() -> list[Accessory]:
    feet = [_one(p) for p in spots()]
    own = [
        ("TPU under each bolt head", UNDER_HEAD >= 1.5, f"{UNDER_HEAD} mm"),
        ("feet", len(feet) == 6, f"{len(feet)}"),
    ]
    return [
        Accessory(
            "foot",
            "Foot",
            feet[0],
            bed=(0, 0, 1),
            qty=len(feet),
            instances=tuple(feet[1:]),
            checks=own,
            color="accent",
            hardware="the bolts it covers, 3 mm longer",
            notes="Under the inner root bolt of each arm and the two tail standoff bolts: the bolt head sinks into it.",
        )
    ]
