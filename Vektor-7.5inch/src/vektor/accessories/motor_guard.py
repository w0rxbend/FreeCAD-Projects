"""Motor guard: a TPU bumper round the outer half of each motor pad, holding both skins' tips: a lip
over the upper pad, a lip under the lower ring, and a wall round the edge. The arm's tip is what hits
first; this keeps the carbon from splitting and the box from opening."""

from math import atan2, cos, degrees, radians, sin

from build123d import Axis

from vektor.accessories.base import Accessory, P, poly, prism
from vektor.geometry import disc

ARC = 100.0  # degrees either side of straight out
R_WALL = (P.PAD_R + 0.2, P.PAD_R + 2.2)
LIP_IN_TOP = P.MOTOR_D / 2 + 1.0  # clear of the motor's base
LIP_IN_BOTTOM = 13.5
LIP_T = 1.0


def _sector(r_in: float, r_out: float):
    pts = [(0.0, 0.0)] + [(60 * cos(radians(a)), 60 * sin(radians(a))) for a in range(-int(ARC), int(ARC) + 1, 10)]
    return (disc((0, 0), 2 * r_out) - disc((0, 0), 2 * r_in)) & poly(pts)


def _local():
    z_bot, z_top = P.Z_LOWER - LIP_T, P.Z_DECK + LIP_T
    part = prism(_sector(*R_WALL), z_bot, z_top)
    part += prism(_sector(LIP_IN_TOP, R_WALL[1]), P.Z_DECK, z_top)
    part += prism(_sector(LIP_IN_BOTTOM, R_WALL[1]), z_bot, P.Z_LOWER)
    return part


def build() -> list[Accessory]:
    local = _local()
    placed = {}
    for q, (mx, my) in P.MOTORS.items():
        ux, uy = P.arm_dir(q)
        placed[q] = local.rotate(Axis.Z, degrees(atan2(uy, ux))).translate((mx, my, 0))
    first = placed["front_right"]
    return [
        Accessory(
            "motor_guard",
            "Motor guard",
            first,
            qty=4,
            instances=tuple(v for k, v in placed.items() if k != "front_right"),
            color="accent",
            bridges=90.0,
            overhang=40.0,
            checks=[
                (
                    "clears the motor's base",
                    LIP_IN_TOP > P.MOTOR_D / 2,
                    f"top lip from R {LIP_IN_TOP:g}, motor R {P.MOTOR_D / 2:g}",
                )
            ],
            notes="Stretch it over the arm's tip, motor off: one lip over the upper pad, one under the lower ring.",
        )
    ]
