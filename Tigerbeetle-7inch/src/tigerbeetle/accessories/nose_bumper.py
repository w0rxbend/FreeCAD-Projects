"""Nose bumper: a TPU rim round the front edge of the camera plate, the part that lands first.

A wall round the nose, flush with the plate's top face (the camera swings down just above it), and
a floor under the nose that the two front-standoff bolts clamp to the plate.
"""

from build123d import Face, extrude, offset
from zhalo.accessories.kit import D_M3_FREE, D_M3_HEAD, FIT, Accessory, cylinder, poly

from tigerbeetle import frame as F
from tigerbeetle import model as M

WALL_T = 2.2
FLOOR_T = 1.6
HEAD_RECESS = 0.0
Y_CUT = 100.0


def build() -> list[Accessory]:
    plate = Face(F.spline(M.plates()["camera_plate"].outline))
    keep = poly([(-60.0, Y_CUT), (60.0, Y_CUT), (60.0, 160.0), (-60.0, 160.0)])
    nose = plate & keep
    outer = offset(nose, FIT + WALL_T) & keep
    inner = offset(nose, FIT) & keep
    z, t = M.Z_CAMERA, M.T_PLATE
    part = extrude(outer - inner, amount=t + FLOOR_T).translate((0, 0, z - FLOOR_T))  # top flush with the plate
    part += extrude(inner, amount=FLOOR_T).translate((0, 0, z - FLOOR_T))
    s = F.standoffs()["standoff_front_right"]
    for x in (s[0], -s[0]):
        part -= cylinder(x, s[1], z - FLOOR_T - 1, z + 1, D_M3_FREE)
    return [
        Accessory(
            "nose_bumper",
            "Nose bumper",
            part,
            bed=(0, 0, -1),
            ceilings=4.0,
            overhang=4.0,
            color="accent",
            checks=[("wall flush with the plate's top face", True, "the camera swings down just above it")],
            hardware="the two front-standoff bolts, 2 mm longer",
            notes="It goes under the nose of the camera plate; the front standoff bolts hold it.",
        )
    ]


_ = (D_M3_HEAD, HEAD_RECESS)
