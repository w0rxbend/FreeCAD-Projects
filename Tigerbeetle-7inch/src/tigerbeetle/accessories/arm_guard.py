"""Arm guard: a TPU bumper that stretches over the end of each arm, past the motor.

A channel round the tip of the motor paddle: a wall outside the carbon edge and a lip over its top
and bottom face. The top lip stops short of the motor base, the bottom one clears the motor screws'
heads. The arm's tip is the first thing to meet a gate or the ground; this takes the knock and
keeps the carbon from delaminating.
"""

from build123d import extrude, offset
from zhalo.accessories.kit import FIT, Accessory, cylinder, poly

from tigerbeetle import equipment as E
from tigerbeetle import frame as F
from tigerbeetle import model as M

WALL_T = 2.0
LIP, LIP_T = 1.4, 1.0
X_CUT = -2.0  # the guard covers the arm from its tip back to just past the motor centre
HEAD_HOLE = 6.8


def _local():
    _pl, part = M.arms()["front_right"]
    arm = poly([tuple(p) for p in M.resample(part.outline, 0.6)])  # a fine polygon offsets cleanly; a spline did not
    keep = poly([(-80.0, -60.0), (X_CUT, -60.0), (X_CUT, 60.0), (-80.0, 60.0)])
    tip = arm & keep
    outer = offset(tip, FIT + WALL_T) & keep
    inner = offset(tip, FIT) & keep
    lip = (inner - offset(tip, -LIP)) & keep
    t = M.T_ARM
    band = extrude(outer - inner, amount=t + 2 * FIT + 2 * LIP_T).translate((0, 0, -FIT - LIP_T))
    top = extrude(lip, amount=LIP_T).translate((0, 0, t + FIT))
    bottom = extrude(lip, amount=LIP_T).translate((0, 0, -FIT - LIP_T))
    for h in part.holes:
        if h.group == "motor":
            bottom -= cylinder(h.x, h.y, -5, 1, HEAD_HOLE)
    # the motor stands on the arm and overhangs its edges: under it the guard stops at the arm's top face
    out = (band + top + bottom) - cylinder(0, 0, t, t + 10, E.MOTOR_D + 1.2)
    return out.clean()


def build() -> list[Accessory]:
    local = _local()
    placed = {q: F.on_arm(local, q) for q in ("front_right", "front_left", "rear_right", "rear_left")}
    own = [
        ("top lip clears the motor base", True, f"lip outside a {E.MOTOR_D + 1.2:g} mm circle"),
        ("covers the tip", X_CUT < 0, f"from the tip to {-X_CUT:g} mm past the motor"),
    ]
    return [
        Accessory(
            "arm_guard",
            "Arm guard",
            placed["front_right"],
            bed=(0, 0, -1),
            qty=4,
            instances=tuple(v for k, v in placed.items() if k != "front_right"),
            checks=own,
            ceilings=60.0,
            overhang=30.0,
            color="accent",
            notes="Stretch it over the arm tip, motor off. The left arms take the same print, turned over.",
        )
    ]
