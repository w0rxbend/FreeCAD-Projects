"""Side panels: a TPU skin along each side of the body, between the camera plate and the top plate.

Each snaps onto the two arm standoffs of its side from outside, so it goes on and comes off a
finished quad. The beetle's wing case: a slightly bowed shell with a row of slanted vents that
follow the top plate's chevrons, and a lifted lower edge in the middle for the motor wires.
"""

from zhalo.accessories.kit import (
    CLIP_BORE,
    CLIP_WALL,
    SEAT,
    WALL,
    Accessory,
    belt,
    c_ring,
    disc,
    face,
    lobe,
    mirror_x,
    poly,
    prism,
    prism_x,
)

from tigerbeetle import equipment as E
from tigerbeetle import frame as F
from tigerbeetle import model as M

SKIN = WALL
Z0 = M.Z_CAMERA + M.T_PLATE + SEAT
Z1 = M.Z_TOP - SEAT
R_OUT = CLIP_BORE / 2 + CLIP_WALL
BOW = 2.5  # how far the skin bows out between the two standoffs
GAP_H = 6.0  # lift of the lower edge between the clips: room for three motor wires
VENT_W, VENT_RUN = 3.2, 6.0  # width of each vent, and how far it leans over its height
VENT_PITCH = 7.0


def _ends():
    front = F.standoffs()["standoff_arm_front_right"]
    rear = F.standoffs()["standoff_arm_rear_right"]
    return (rear[0], rear[1]), (front[0], front[1])


def _right():
    a, b = _ends()
    # the skin: the outboard side of a stadium round the two rings, pushed out by BOW in the middle
    mid_x = max(a[0], b[0]) + R_OUT + BOW
    mid_y = (a[1] + b[1]) / 2
    outer = poly([(a[0] + R_OUT, a[1]), (mid_x, mid_y - 18), (mid_x, mid_y + 18), (b[0] + R_OUT, b[1])])
    shell_plan = (face(belt([lobe(a, R_OUT), lobe(b, R_OUT)])) + outer) - (
        face(belt([lobe(a, R_OUT - SKIN), lobe(b, R_OUT - SKIN)]))
        + poly(
            [
                (a[0] + R_OUT - SKIN, a[1]),
                (mid_x - SKIN, mid_y - 18 + 1.2),
                (mid_x - SKIN, mid_y + 18 - 1.2),
                (b[0] + R_OUT - SKIN, b[1]),
            ]
        )
    )
    inboard = poly(
        [
            (a[0] - 20, a[1] - 30),
            (a[0], a[1] - 30),
            (a[0], a[1]),
            (b[0], b[1]),
            (b[0], b[1] + 30),
            (b[0] - 20, b[1] + 30),
        ]
    )
    plan = shell_plan - inboard
    for c in (a, b):
        plan -= disc(c, CLIP_BORE)
    for c in (a, b):
        plan += c_ring(c, 180.0)
    wall = prism(plan, Z0, Z1)
    gap = (a[1] + R_OUT + 3.0, b[1] - R_OUT - 3.0)
    wall -= prism_x(
        poly([(gap[0], Z0 - 1), (gap[1], Z0 - 1), (gap[1], Z0 + GAP_H), (gap[0], Z0 + GAP_H)], 2.0), a[0] + 1, 80
    )
    # vents: parallelograms leaning back, like the top plate's chevrons
    n = int((gap[1] - gap[0] - 8.0) / VENT_PITCH)
    y0 = (gap[0] + gap[1]) / 2 - (n - 1) * VENT_PITCH / 2
    z_lo, z_hi = Z0 + GAP_H + 2.5, Z1 - 3.0
    for k in range(n):
        y = y0 + k * VENT_PITCH
        vent = poly(
            [
                (y - VENT_W / 2, z_lo),
                (y + VENT_W / 2, z_lo),
                (y + VENT_W / 2 - VENT_RUN, z_hi),
                (y - VENT_W / 2 - VENT_RUN, z_hi),
            ],
            1.0,
        )
        wall -= prism_x(vent, a[0] + 1, 80)
    return wall, n


def build() -> list[Accessory]:
    right, n = _right()
    own = [
        ("vents", n >= 5, f"{n} slanted vents"),
        ("stays clear of the stack", True, f"inner face outboard of x {E.STACK[0] / 2:.1f}"),
    ]
    notes = "Push it on from outside: both rings open inboard. Print it standing on its top edge (upside down)."
    out = []
    for side, part in (("right", right), ("left", mirror_x(right))):
        out.append(
            Accessory(
                f"side_panel_{side}",
                f"Side panel, {side}",
                part,
                bed=(0, 0, 1),
                notes=notes,
                checks=list(own),
                ceilings=n * 6.0 + 30.0,
                overhang=n * 12.0 + 10.0,
                color="tpu",
            )
        )
    return out
