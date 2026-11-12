"""Arm guard: a TPU cap round the motor end of an arm.

A floor under the motor pad, a wall round its edge and a small lip over the top edge. The motor
screws do not clamp it: their heads sit in clearance holes in the floor, straight on the carbon,
so the screws keep their full thread in the motor and cannot work loose on creeping TPU.
"""

from math import acos

from build123d import Axis, Plane, Vector

from zhalo import frame as F
from zhalo.accessories.kit import FIT, Accessory, P, box, cylinder

WALL_T = 2.5
FLOOR_T = 2.0
LIP = 0.9  # how far the lip reaches in over the pad
LIP_T = 1.1
REACH = 6.5  # the guard runs from the arm tip back to this far behind the motor centre
HEAD_HOLE = 6.8  # clear of an M3 button or socket head
MOTOR_BASE_D = 28.4  # largest motor base the lip has to clear


def _local():
    """The guard in arm coordinates: arm underside at Z = 0, pad centre at (ARM_LEN, 0)."""
    c = (P.ARM_LEN, 0.0)
    r_pad = P.MOTOR_PAD_R + FIT
    r_out = r_pad + WALL_T
    top = P.T_ARM + FIT + LIP_T
    shell = cylinder(*c, -FLOOR_T, top, 2 * r_out) - cylinder(*c, 0.0, P.T_ARM + FIT, 2 * r_pad)
    shell -= cylinder(*c, P.T_ARM, top + 1, 2 * (r_pad - LIP))
    part = shell & box(c[0] - REACH, -r_out - 1, -FLOOR_T - 1, c[0] + r_out + 1, r_out + 1, top + 1)
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
        ("screw heads bear on carbon, not TPU", HEAD_HOLE >= 6.5, f"{HEAD_HOLE} mm holes round the heads"),
    ]
    wrap = 2 * (3.14159265 - acos(REACH / (P.MOTOR_PAD_R + FIT)))  # radians of pad edge under the lip
    lip_area = wrap * (P.MOTOR_PAD_R + FIT - LIP / 2) * LIP
    return [
        Accessory(
            "arm_guard",
            "Arm guard",
            placed["front_right"],
            qty=4,
            checks=own,
            ceilings=lip_area,
            instances=tuple(v for k, v in placed.items() if k != "front_right"),
            notes=(
                "Stretch it over the arm tip before the motor goes on: the lip snaps over the pad edge "
                "and the floor keys onto the four screw heads. Standard M3x8 motor screws."
            ),
        )
    ]
