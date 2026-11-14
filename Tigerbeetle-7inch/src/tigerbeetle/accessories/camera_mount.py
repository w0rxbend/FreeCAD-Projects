"""FPV camera mount: two sleeves on the front standoffs, each carrying a cheek beside the camera.

The camera hangs on its own two M2 side screws, so the up-tilt is set by hand (15-45 deg) and held
by the screws clamping TPU against the camera body. For 19 mm ("micro") cameras: a 22 mm camera
has no room to tilt in a 25 mm bay.
"""

from zhalo.accessories.kit import (
    D_M2_FREE,
    FIT,
    SLEEVE_BORE,
    SLEEVE_OD,
    Accessory,
    box,
    cylinder,
    disc,
    mirror_x,
    poly,
    prism_x,
)
from zhalo.checks import overlap

from tigerbeetle import equipment as E
from tigerbeetle import frame as F
from tigerbeetle import model as M

CHEEK_T = 2.6
FLOOR_T = 1.6
Z0 = M.Z_CAMERA + M.T_PLATE
TOP = M.Z_TOP - 0.2
FLOOR_BACK = 6.5  # the bridge between the sleeves runs from this far behind the standoffs to 2.5 mm behind them
NOSE_CLEAR = 110.0


def build() -> list[Accessory]:
    cam = E.CAM_MICRO
    s = F.standoffs()["standoff_front_right"]
    sx, sy = s[0], s[1]
    px, py, pz = E.cam_pivot()
    x_in = cam.width / 2 + FIT
    x_out = x_in + CHEEK_T
    y_rear, y_front = sy - SLEEVE_OD / 2, py + 8.0
    nose = NOSE_CLEAR  # the cheeks and the floor stay this far behind the plate's nose (the bumper is there)
    profile = poly(
        [(y_rear, Z0), (nose, Z0), (y_front, Z0 + 9.0), (y_front, pz + 5.0), (py + 2.0, TOP), (y_rear, TOP)], 2.0
    )
    right = prism_x(profile, x_in, x_out)
    right += box(x_out - 0.01, y_rear, Z0, sx, sy + SLEEVE_OD / 2 - 1.0, Z0 + 6.0)  # a web from the cheek to the sleeve
    right += cylinder(sx, sy, Z0, TOP, SLEEVE_OD)
    right -= prism_x(disc((py, pz), D_M2_FREE), x_in - 1, x_out + 1)
    # a bridge between the two sleeves, behind the camera: its underside never swings back that far
    floor = box(-x_out, sy - FLOOR_BACK, Z0, x_out, sy - 2.5, Z0 + FLOOR_T)
    part = right + mirror_x(right) + floor
    for x in (sx, -sx):
        part -= cylinder(x, sy, Z0 - 1, TOP + 1, SLEEVE_BORE)
    swept = overlap(part, E.camera_sweep(cam, grow=0.0))
    gap = sx - SLEEVE_BORE / 2 - x_in
    own = [
        ("camera swings 15-45 deg without touching the mount", swept < 1e-3, f"{swept:.3f} mm3"),
        ("TPU between the camera and each standoff", gap >= 2.0, f"{gap:.2f} mm"),
    ]
    return [
        Accessory(
            "camera_mount",
            "FPV camera mount, 19 mm",
            part,
            holds=("camera",),
            checks=own,
            ceilings=8.0,
            overhang=14.0,
            color="accent",
            hardware="2x M2x5 (the camera's own side screws)",
            notes="Sleeves over the front standoffs before the top plate goes on; set the tilt, tighten the screws.",
        )
    ]
