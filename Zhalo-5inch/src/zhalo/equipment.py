"""Envelopes of the parts the frame is built round. They are not exported for manufacture:
they exist so the clearance checks and the renders show a dressed quad, not bare carbon.

Sizes are the manufacturers' published outer dimensions rounded up; where a part has no
single standard (camera, battery) the envelope is the common worst case and is a parameter.
"""

from dataclasses import dataclass
from functools import lru_cache

from build123d import Align, Axis, Box, Cylinder, Part, Pos, Vector

from zhalo import params as P

MIN_Z = (Align.CENTER, Align.CENTER, Align.MIN)

# --- SpeedyBee F405 V3/V4 stack (30.5 x 30.5, M3) ------------------------------------------
ESC_SIZE = (45.6, 44.0, 8.0)  # BLS 55A 4-in-1
FC_SIZE = (41.6, 39.4, 7.8)
STACK_H = 18.3  # deck to the top of the FC, standoffs and grommets included
ESC_Z = P.Z_DECK + 2.5
FC_Z = P.Z_DECK + STACK_H - FC_SIZE[2]

# --- analog VTX ------------------------------------------------------------------------------
VTX_SIZE = (28.0, 28.0, 7.0)  # SpeedyBee TX800 with its heat sink; 20 x 20 holes
VTX_LARGE_SIZE = (36.0, 36.0, 8.0)  # 30.5 x 30.5 class (Rush Tank Ultimate, Unify Pro32 HV)
VTX_Z = P.Z_BAY + 5.0  # on 5 mm spacers above the bay floor

# --- camera ----------------------------------------------------------------------------------
# the camera's side screws; the tilt axis runs along X through this point, 1 mm above mid-height of the bay
CAM_PIVOT = (0.0, P.F[1] + 7.0, (P.Z_BAY + P.Z_TOP) / 2 + 1.0)
CAM_TILT = 30.0  # nominal up-tilt, degrees
CAM_TILT_RANGE = (15.0, 45.0)


@dataclass(frozen=True)
class Camera:
    name: str
    width: float  # also the height: these cameras are square from the front
    body_front: float  # body front face ahead of the side screws
    body_rear: float  # body rear face behind the side screws
    lens_d: float
    lens_len: float  # lens tip ahead of the body front face
    screw: float  # side screw thread


CAM_MICRO = Camera("micro 19 mm", 19.0, 5.0, 7.0, 14.0, 11.0, 2.0)  # Ratel 2 / Razer Micro / Phoenix 2
CAM_MINI = Camera("mini 22 mm", 22.0, 6.0, 8.0, 17.0, 12.0, 2.0)  # Razer Mini / Phoenix 2 Mini (21-22)

# --- drive -----------------------------------------------------------------------------------
MOTOR_D, MOTOR_H = 28.0, 19.5  # 2207 / 2306 can
SHAFT_D, SHAFT_H = 5.0, 13.0
PROP_T = 7.0  # swept thickness of a 5.1 x 3.6 blade

# --- battery ---------------------------------------------------------------------------------
BATTERY_SIZE = (38.0, 78.0, 40.0)  # 6S 1100-1300 mAh; a 4S 1500 is smaller in every direction
BATTERY_Y = -8.0  # slid back: leaves the front of the deck to the action-camera mount
PAD_T = 1.6  # battery pad between the deck and the pack


def box(x0: float, y0: float, z0: float, x1: float, y1: float, z1: float) -> Part:
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(x1 - x0, y1 - y0, z1 - z0)


def cylinder(x: float, y: float, z0: float, z1: float, d: float) -> Part:
    return Pos(x, y, z0) * Cylinder(d / 2, z1 - z0, align=MIN_Z)


def _slab(size, z0: float, center=(0.0, 0.0)) -> Part:
    return box(
        center[0] - size[0] / 2,
        center[1] - size[1] / 2,
        z0,
        center[0] + size[0] / 2,
        center[1] + size[1] / 2,
        z0 + size[2],
    )


def camera(cam: Camera = CAM_MICRO, tilt: float = CAM_TILT, grow: float = 0.0) -> Part:
    """Camera body + lens at the given up-tilt. `grow` pads every face (used for pockets)."""
    w = cam.width / 2 + grow
    body = box(-w, -cam.body_rear - grow, -w, w, cam.body_front + grow, w)
    lens = Pos(0, cam.body_front, 0) * Cylinder(
        cam.lens_d / 2 + grow, cam.lens_len + grow, rotation=(-90, 0, 0), align=MIN_Z
    )
    return (body + lens).rotate(Axis.X, tilt).translate(Vector(*CAM_PIVOT))


def camera_sweep(cam: Camera = CAM_MICRO, grow: float = 0.3, step: float = 5.0) -> Part:
    """Everything the camera touches over the whole tilt range."""
    lo, hi = CAM_TILT_RANGE
    out, a = camera(cam, lo, grow), lo + step
    while a <= hi + 1e-6:
        out = out + camera(cam, a, grow)
        a += step
    return out


def motor(xy) -> Part:
    return cylinder(*xy, P.Z_MID, P.Z_MID + MOTOR_H, MOTOR_D) + cylinder(
        *xy, P.Z_MID + MOTOR_H, P.Z_MID + MOTOR_H + SHAFT_H, SHAFT_D
    )


def prop(xy) -> Part:
    z = P.Z_MID + MOTOR_H + 1.0
    return cylinder(*xy, z, z + PROP_T, P.PROP_D)


def prop_keepout(xy) -> Part:
    """Where no body or accessory material may be: the prop disc plus margin over the blade band."""
    return cylinder(*xy, P.PROP_Z[0], P.PROP_Z[1], 2 * P.PROP_KEEPOUT_R)


def battery() -> Part:
    return _slab(BATTERY_SIZE, P.Z_ROOF + PAD_T, (0.0, BATTERY_Y))


@lru_cache(maxsize=1)
def build() -> dict[str, tuple[Part, str, float]]:
    """name -> (part, colour key, opacity) for the renders."""
    out: dict[str, tuple[Part, str, float]] = {
        "esc": (_slab(ESC_SIZE, ESC_Z), "pcb", 1.0),
        "fc": (_slab(FC_SIZE, FC_Z), "pcb", 1.0),
        "vtx": (_slab(VTX_SIZE, VTX_Z, (0.0, P.VTX_BAY_Y)), "pcb", 1.0),
        "camera": (camera(), "camera", 1.0),
        "battery": (battery(), "battery", 1.0),
    }
    for name, xy in P.MOTORS.items():
        out[f"motor_{name}"] = (motor(xy), "motor", 1.0)
        out[f"prop_{name}"] = (prop(xy), "prop", 0.28)
    out.update(EXTRA)
    for name, (part, _c, _o) in out.items():
        part.label = name
    return out


EXTRA: dict[str, tuple[Part, str, float]] = {}  # gear a sibling design adds: name -> (part, colour key, opacity)
