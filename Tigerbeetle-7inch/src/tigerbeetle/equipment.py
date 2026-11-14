"""Envelopes of what the frame carries, for the clearance checks and the renders. Nothing here is
traced; sizes are the common published outer dimensions, rounded up.
"""

from functools import lru_cache

from build123d import Axis, Box, Cylinder, Part, Pos, Vector
from zhalo.equipment import Camera

from tigerbeetle import frame as F
from tigerbeetle import model as M

MIN_Z = F.MIN_Z
PROP_D = 7 * 25.4
PROP_MARGIN = 2.5
MOTOR_D, MOTOR_H = 34.0, 21.0  # 2806.5 / 2807 class
PROP_T = 8.0
PROP_Z = (M.Z_CAMERA + 18.0, M.Z_CAMERA + 34.0)  # the band the blades can sweep, flex included

STACK = (45.6, 44.0, 22.0)  # 30.5 mm FC + 4-in-1 ESC on grommets: what a 25 mm bay takes
STACK_Z = M.Z_CAMERA + M.T_PLATE + 0.5
VTX = (36.0, 36.0, 9.0)  # 30.5 mm class analog VTX with its fan or heat sink
VTX_Z = M.Z_CAMERA + M.T_PLATE + 4.0
BATTERY = (40.0, 110.0, 42.0)  # 6S 1800-2200 mAh, or 6S1P 21700 Li-ion in a soft pack
BATTERY_Y = -5.0
PAD_T = 1.6
CAM_MICRO = Camera("micro 19 mm", 19.0, 5.0, 7.0, 14.0, 11.0, 2.0)
CAM_TILT_RANGE = (15.0, 45.0)


def box(x0, y0, z0, x1, y1, z1) -> Part:
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(x1 - x0, y1 - y0, z1 - z0)


def cylinder(x, y, z0, z1, d) -> Part:
    return Pos(x, y, z0) * Cylinder(d / 2, z1 - z0, align=MIN_Z)


def front_bay() -> tuple[float, float]:
    """Centre of the camera plate's front board pattern (20 and 30.5 mm squares)."""
    ys = sorted({round(h.y, 2) for h in M.plates()["camera_plate"].holes if abs(abs(h.x) - 15.25) < 1e-6 and h.y > 30})
    return 0.0, (ys[0] + ys[-1]) / 2


def cam_pivot() -> tuple[float, float, float]:
    """The FPV camera's side screws: between the two front standoffs, just ahead of them, mid-height."""
    s = F.standoffs()["standoff_front_right"]
    return 0.0, s[1] + 3.0, M.Z_CAMERA + M.T_PLATE + (M.Z_TOP - M.Z_CAMERA - M.T_PLATE) / 2


def camera(cam: Camera = CAM_MICRO, tilt: float = 30.0, grow: float = 0.0) -> Part:
    w = cam.width / 2 + grow
    body = box(-w, -cam.body_rear - grow, -w, w, cam.body_front + grow, w)
    lens = Pos(0, cam.body_front, 0) * Cylinder(
        cam.lens_d / 2 + grow, cam.lens_len + grow, rotation=(-90, 0, 0), align=MIN_Z
    )
    return (body + lens).rotate(Axis.X, tilt).translate(Vector(*cam_pivot()))


def camera_sweep(cam: Camera = CAM_MICRO, grow: float = 0.3) -> Part:
    lo, hi = CAM_TILT_RANGE
    out, a = camera(cam, lo, grow), lo + 5
    while a <= hi + 1e-6:
        out = out + camera(cam, a, grow)
        a += 5
    return out


def motor(xy) -> Part:
    z = M.Z_CAMERA
    return cylinder(*xy, z, z + MOTOR_H, MOTOR_D) + cylinder(*xy, z + MOTOR_H, z + MOTOR_H + 13, 5.0)


def prop(xy) -> Part:
    z = M.Z_CAMERA + MOTOR_H + 1.0
    return cylinder(*xy, z, z + PROP_T, PROP_D)


def prop_keepout(xy) -> Part:
    return cylinder(*xy, PROP_Z[0], PROP_Z[1], PROP_D + 2 * PROP_MARGIN)


def stack() -> Part:
    w, l, h = STACK
    return box(-w / 2, -l / 2, STACK_Z, w / 2, l / 2, STACK_Z + h)


def vtx() -> Part:
    x, y = front_bay()
    w, l, h = VTX
    return box(x - w / 2, y - l / 2, VTX_Z, x + w / 2, y + l / 2, VTX_Z + h)


def battery() -> Part:
    w, l, h = BATTERY
    z = M.Z_TOP + M.T_PLATE + PAD_T
    return box(-w / 2, BATTERY_Y - l / 2, z, w / 2, BATTERY_Y + l / 2, z + h)


@lru_cache(maxsize=1)
def build() -> dict[str, tuple[Part, str, float]]:
    out = {
        "stack": (stack(), "pcb", 1.0),
        "vtx": (vtx(), "pcb", 1.0),
        "camera": (camera(), "camera", 1.0),
        "battery": (battery(), "battery", 1.0),
    }
    for name, xy in F.motors().items():
        out[f"motor_{name}"] = (motor(xy), "motor", 1.0)
        out[f"prop_{name}"] = (prop(xy), "prop", 0.28)
    for n, (p, _c, _o) in out.items():
        p.label = n
    return out
