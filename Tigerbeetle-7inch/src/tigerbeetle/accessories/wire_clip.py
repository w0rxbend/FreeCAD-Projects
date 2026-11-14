"""Motor-wire clip: snaps over an arm and holds the three motor wires flat on top of it.

One per arm, on the straight part between the stack and the motor. The arm here is the traced one,
so the slot is sized from its measured width at that station. The profile is constant along the
arm: it prints lying on its side.
"""

import numpy as np
from zhalo.accessories.kit import FIT, WALL, Accessory, poly, prism_x

from tigerbeetle import frame as F
from tigerbeetle import model as M

U = 62.0  # station: mm from the motor centre towards the root
LENGTH = 6.0
TUNNEL = (8.6, 3.2)
HOOK, HOOK_T = 1.4, 1.5


def _width(x: float) -> tuple[float, float]:
    """(lowest y, highest y) of the arm's outline across the station x (arm frame)."""
    outline = M.arms()["front_right"][1].outline
    ys = np.linspace(-20, 20, 4001)
    inside = M.inside(outline, np.c_[np.full_like(ys, x), ys])
    return float(ys[inside].min()), float(ys[inside].max())


def _local():
    spans = [_width(x) for x in np.linspace(U - LENGTH / 2, U + LENGTH / 2, 7)]
    lo, hi = min(s[0] for s in spans), max(s[1] for s in spans)
    mid = (lo + hi) / 2
    half = (hi - lo) / 2 + FIT
    out = half + WALL
    top = M.T_ARM + FIT
    roof = top + TUNNEL[1] + WALL
    tw = TUNNEL[0] / 2
    outer = poly(
        [(-out, -HOOK_T), (out, -HOOK_T), (out, roof - 1.5), (out - 1.5, roof), (-out + 1.5, roof), (-out, roof - 1.5)],
        0.6,
    )
    slot = poly([(-half, -FIT), (half, -FIT), (half, top), (-half, top)])
    tunnel = poly([(-tw, top - 2.5), (tw, top - 2.5), (tw, top + TUNNEL[1]), (-tw, top + TUNNEL[1])], 1.0)
    mouth = poly([(-half + HOOK, -HOOK_T - 1), (half - HOOK, -HOOK_T - 1), (half - HOOK, 0.0), (-half + HOOK, 0.0)])
    profile = outer - slot - tunnel - mouth
    # prism_x reads the profile as (y, z) and extrudes along x: the arm frame's x runs along the arm
    return prism_x(profile, U - LENGTH / 2, U + LENGTH / 2).translate((0, mid, 0)), hi - lo


def build() -> list[Accessory]:
    local, width = _local()
    placed = {q: F.on_arm(local, q) for q in ("front_right", "front_left", "rear_right", "rear_left")}
    _pl, _part = M.arms()["front_right"]
    import math

    a = math.radians(_pl.angle)
    bed = (math.cos(a), math.sin(a), 0.0)
    return [
        Accessory(
            "wire_clip",
            "Motor-wire clip",
            placed["front_right"],
            bed=bed,
            qty=4,
            instances=tuple(v for k, v in placed.items() if k != "front_right"),
            checks=[("sized to the traced arm", width > 8.0, f"arm {width:.1f} mm wide at the clip")],
            notes="Lay the wires on the arm and press the clip down until both hooks snap under it.",
        )
    ]
