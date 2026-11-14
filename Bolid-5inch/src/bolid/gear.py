"""What the frame carries, as envelopes for the clearance checks and the pictures: common published
outer sizes, rounded up, not any one product."""

from functools import lru_cache

from build123d import Align, Axis, Box, Cylinder, Part, Pos

from bolid import params as P

MIN_Z = (Align.CENTER, Align.CENTER, Align.MIN)


def box(x0, y0, z0, x1, y1, z1) -> Part:
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(x1 - x0, y1 - y0, z1 - z0)


def cyl(x, y, z0, z1, d) -> Part:
    return Pos(x, y, z0) * Cylinder(d / 2, z1 - z0, align=MIN_Z)


ESC = (38.0, 38.0, 6.0)  # 4-in-1, 30.5 holes, on gummies
ESC_Z = P.Z_BAY + 2.0
FC = (36.0, 36.0, 6.0)
FC_Z = ESC_Z + ESC[2] + 3.0
RX = (11.0, 16.0, 3.0)  # a small ELRS receiver
RX_Z = P.Z_BAY + 2.0
VTX = (30.0, 30.0, 10.0)  # a digital air unit with its heat sink, 25.5 or 20 holes
VTX_Z = P.Z_ARM + 2.0  # on 2 mm nylon spacers over the bottom plate's tail
BATTERY = (35.0, 70.0, 35.0)  # 6S 1100-1300 mAh
BATTERY_Y = P.STRAP_Y  # the action camera mount takes the plate's nose
PAD_T = 1.6
CAMERA = (19.0, 5.0, 7.0, 14.0, 11.0)  # width, body ahead of / behind the side screws, lens diameter, length
CAM_PIVOT = (0.0, 41.0, P.Z_BAY + 12.4)  # the low corners clear the press plate at every tilt
TILT = (20.0, 50.0)


def camera(tilt: float = 30.0, grow: float = 0.0) -> Part:
    w, ahead, behind, lens_d, lens_l = CAMERA
    h = w / 2 + grow
    body = box(-h, -behind - grow, -h, h, ahead + grow, h)
    lens = Pos(0, ahead, 0) * Cylinder(lens_d / 2 + grow, lens_l + grow, rotation=(-90, 0, 0), align=MIN_Z)
    return (body + lens).rotate(Axis.X, tilt).translate(CAM_PIVOT)


def camera_sweep(grow: float = 0.3) -> Part:
    out = camera(TILT[0], grow)
    for a in range(int(TILT[0]) + 5, int(TILT[1]) + 1, 5):
        out += camera(a, grow)
    return out


def motor(xy) -> Part:
    return cyl(*xy, P.Z_PRESS, P.Z_PRESS + P.MOTOR_H, P.MOTOR_D) + cyl(
        *xy, P.Z_PRESS + P.MOTOR_H, P.Z_PRESS + P.MOTOR_H + 12, 5.0
    )


def prop(xy) -> Part:
    return cyl(*xy, P.PROP_Z[0] + 0.5, P.PROP_Z[1] - 0.5, P.PROP_D)


def keepout(xy) -> Part:
    return cyl(*xy, P.PROP_Z[0], P.PROP_Z[1], 2 * P.PROP_KEEPOUT)


def battery() -> Part:
    w, l, h = BATTERY
    z = P.Z_ROOF + PAD_T
    return box(-w / 2, BATTERY_Y - l / 2, z, w / 2, BATTERY_Y + l / 2, z + h)


@lru_cache(maxsize=1)
def build() -> dict[str, tuple[Part, str, float]]:
    out = {
        "esc": (box(-ESC[0] / 2, -ESC[1] / 2, ESC_Z, ESC[0] / 2, ESC[1] / 2, ESC_Z + ESC[2]), "pcb", 1.0),
        "fc": (box(-FC[0] / 2, -FC[1] / 2, FC_Z, FC[0] / 2, FC[1] / 2, FC_Z + FC[2]), "pcb", 1.0),
        "rx": (box(-RX[0] / 2, P.RX_Y - RX[1] / 2, RX_Z, RX[0] / 2, P.RX_Y + RX[1] / 2, RX_Z + RX[2]), "pcb", 1.0),
        "vtx": (
            box(-VTX[0] / 2, P.VTX_Y - VTX[1] / 2, VTX_Z, VTX[0] / 2, P.VTX_Y + VTX[1] / 2, VTX_Z + VTX[2]),
            "pcb",
            1.0,
        ),
        "camera": (camera(), "camera", 1.0),
        "battery": (battery(), "battery", 1.0),
    }
    for q, xy in P.MOTORS.items():
        out[f"motor_{q}"] = (motor(xy), "motor", 1.0)
        out[f"prop_{q}"] = (prop(xy), "prop", 0.25)
    return out
