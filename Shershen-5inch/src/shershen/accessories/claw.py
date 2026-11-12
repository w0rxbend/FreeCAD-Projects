"""Claw: the arm guard for Shershen's pointed arm tip.

Same idea as Zhalo's guard (floor, wall, small lip, motor screws bearing on carbon, not on
TPU), drawn round the teardrop pad and built up to a thick bumper at the point.
"""

from build123d import Axis, Plane, Vector
from zhalo import frame as F
from zhalo.accessories.kit import FIT, Accessory, P, box, cylinder, hull, prism

from shershen import profiles

WALL_T = 2.4
TIP_EXTRA = 2.2  # extra TPU at the point: that is where the arm meets the ground first
FLOOR_T = 2.0
LIP = 0.9
LIP_T = 1.1
REACH = 6.5  # the claw runs from the tip back to this far behind the motor centre
HEAD_HOLE = 6.8
MOTOR_BASE_D = 28.4


def _teardrop(grow_pad: float, grow_tip: float):
    c, tip = (P.ARM_LEN, 0.0), (P.ARM_LEN + profiles.TIP_REACH, 0.0)
    return hull([(c, P.MOTOR_PAD_R + grow_pad), (tip, max(profiles.TIP_R + grow_tip, 0.5))])


def _local():
    """The claw in arm coordinates: arm underside at Z = 0, motor centre at (ARM_LEN, 0)."""
    c = (P.ARM_LEN, 0.0)
    top = P.T_ARM + FIT + LIP_T
    shell = prism(_teardrop(FIT + WALL_T, FIT + WALL_T + TIP_EXTRA), -FLOOR_T, top)
    shell -= prism(_teardrop(FIT, FIT), 0.0, P.T_ARM + FIT)  # the arm itself
    shell -= prism(_teardrop(FIT - LIP, FIT - LIP), P.T_ARM, top + 1)  # opening inside the lip
    reach = P.MOTOR_PAD_R + profiles.TIP_REACH + 10
    part = shell & box(c[0] - REACH, -reach, -FLOOR_T - 1, c[0] + reach, reach, top + 1)
    part -= cylinder(*c, -FLOOR_T - 1, 1, 9.0)
    for xy in F.motor_bolts(c):
        part -= cylinder(*xy, -FLOOR_T - 1, 1, HEAD_HOLE)
    return part


def _place(part, name: str):
    out = part.rotate(Axis.Z, P.ARM_ANGLE).translate(Vector(P.S[0], P.S[1], P.Z_ARM))
    if "left" in name:
        out = out.mirror(Plane.YZ)
    if "rear" in name:
        out = out.mirror(Plane.XZ)
    return out


def build() -> list[Accessory]:
    local = _local()
    placed = {name: _place(local, name) for name in P.MOTORS}
    lip_gap = (P.MOTOR_PAD_R + FIT - LIP) - MOTOR_BASE_D / 2
    own = [
        ("lip clears a 28.4 mm motor base", lip_gap >= 0.5, f"{lip_gap:.2f} mm radial gap"),
        ("TPU at the point", WALL_T + TIP_EXTRA >= 4.0, f"{WALL_T + TIP_EXTRA:.1f} mm"),
    ]
    return [
        Accessory(
            "claw",
            "Claw (arm guard)",
            placed["front_right"],
            qty=4,
            checks=own,
            ceilings=130.0,
            color="accent",
            instances=tuple(v for k, v in placed.items() if k != "front_right"),
            notes=(
                "Stretch it over the arm tip before the motor goes on: the lip snaps over the pad edge and the "
                "floor keys onto the screw heads. Standard M3x8 motor screws."
            ),
        )
    ]
