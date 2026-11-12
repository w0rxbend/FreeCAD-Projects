"""Nose bumper: a TPU shoe round the front of the bottom plate.

A floor under the nose, a wall round its edge, one screw through the nose hole. It takes the
first hit in a head-on crash instead of the carbon edge and stands 4 mm above the plate.
It has no upper lip, so it prints flat on its floor without supports.
"""

from zhalo import frame as F
from zhalo.accessories.kit import D_M3_FREE, D_M3_HEAD, FIT, Accessory, P, box, cylinder, hull, prism

WALL_T = 3.2
FLOOR_T = 2.6
HEAD_RECESS = 1.7  # a button head sits flush in the floor
LIP_H = 4.0  # wall height above the plate
Y_FLOOR, Y_WALL = P.NOSE_HOLE[1] - 6.0, P.NOSE_HOLE[1] - 2.0


def _nose(grow: float):
    """Front of the bottom plate outline, grown by `grow` (nose corners and the front standoff lobes)."""
    (nx, ny), nr = F.NOSE, 6.0
    return hull(
        [
            ((P.F[0], P.F[1]), P.LOBE_R + grow),
            ((nx, ny), nr + grow),
            ((-nx, ny), nr + grow),
            ((-P.F[0], P.F[1]), P.LOBE_R + grow),
        ]
    )


def build() -> list[Accessory]:
    outer, pocket = _nose(FIT + WALL_T), _nose(FIT)
    far = 60.0
    floor = prism(outer, -FLOOR_T, 0.0) & box(-far, Y_FLOOR, -FLOOR_T - 1, far, 120, 1)
    wall = (prism(outer, 0.0, P.T_BOTTOM + LIP_H) - prism(pocket, -1, P.T_BOTTOM + LIP_H + 1)) & box(
        -far, Y_WALL, -1, far, 120, 20
    )
    part = floor + wall
    part -= cylinder(*P.NOSE_HOLE, -FLOOR_T - 1, 1, D_M3_FREE)
    part -= cylinder(*P.NOSE_HOLE, -FLOOR_T - 1, -FLOOR_T + HEAD_RECESS, D_M3_HEAD)
    under_head = FLOOR_T - HEAD_RECESS
    own = [
        ("TPU under the screw head", under_head >= 0.8, f"{under_head:.1f} mm"),
        ("lowest point stays above the brace skids", -FLOOR_T > -5.0, f"Z {-FLOOR_T:.1f}"),
    ]
    return [
        Accessory(
            "nose_bumper",
            "Nose bumper",
            part,
            hardware="1x M3x8 button head + M3 nyloc nut",
            ceilings=22.0,
            checks=own,
            notes="Screw from below through the nose hole, nut on top of the plate, under the camera lens.",
        )
    ]
