"""What the frame carries, as envelopes: for the clearance checks and the pictures. Common published
outer sizes, rounded up; not any one product."""

from functools import lru_cache

from build123d import Axis, Box, Cylinder, Part, Pos

from vektor import params as P

MIN_Z = (__import__("build123d").Align.CENTER,) * 2 + (__import__("build123d").Align.MIN,)


def box(x0, y0, z0, x1, y1, z1) -> Part:
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(x1 - x0, y1 - y0, z1 - z0)


def cyl(x, y, z0, z1, d) -> Part:
    return Pos(x, y, z0) * Cylinder(d / 2, z1 - z0, align=MIN_Z)


ESC = (46.0, 46.0, 7.0)  # 4-in-1, in the cavity on grommets
ESC_Z = P.Z_LOWER + P.T_SKIN + 2.5
FC = (38.0, 38.0, 8.0)
FC_Z = P.Z_DECK + 6.0
VTX = (36.0, 36.0, 9.0)  # analog, 30.5 or 20 holes, with its heat sink
VTX_Z = P.Z_DECK + 4.0
RX = (18.0, 24.0, 7.0)  # a diversity receiver (ELRS / Crossfire class), lying flat
BATTERY = (46.0, 110.0, 46.0)  # 6S 3000-4500 mAh LiPo or 6S1P/6S2P 21700 Li-ion
BATTERY_Y = -2.0
PAD_T = 1.6
CAMERA = (19.0, 5.0, 7.0, 14.0, 11.0)  # width, body ahead of / behind the side screws, lens diameter, lens length
CAM_PIVOT = (0.0, 86.0, P.Z_DECK + P.BAY / 2 + 1.0)
TILT = (10.0, 40.0)
GPS = (25.0, 25.0, 8.0)


def camera(tilt: float = 25.0, grow: float = 0.0) -> Part:
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
    return cyl(*xy, P.Z_DECK, P.Z_DECK + P.MOTOR_H, P.MOTOR_D) + cyl(
        *xy, P.Z_DECK + P.MOTOR_H, P.Z_DECK + P.MOTOR_H + 14, 5.0
    )


def prop(xy) -> Part:
    z = P.Z_DECK + P.MOTOR_H + 1.5
    return cyl(*xy, z, z + 8.0, P.PROP_D)


def keepout(xy) -> Part:
    return cyl(*xy, P.PROP_Z[0], P.PROP_Z[1], 2 * P.PROP_KEEPOUT)


def battery() -> Part:
    w, l, h = BATTERY
    z = P.Z_ROOF + PAD_T
    return box(-w / 2, BATTERY_Y - l / 2, z, w / 2, BATTERY_Y + l / 2, z + h)


@lru_cache(maxsize=1)
def build() -> dict[str, tuple[Part, str, float]]:
    w, l, h = ESC
    out = {
        "esc": (box(-w / 2, -l / 2, ESC_Z, w / 2, l / 2, ESC_Z + h), "pcb", 1.0),
        "fc": (box(-FC[0] / 2, -FC[1] / 2, FC_Z, FC[0] / 2, FC[1] / 2, FC_Z + FC[2]), "pcb", 1.0),
        "vtx": (
            box(-VTX[0] / 2, P.VTX_Y - VTX[1] / 2, VTX_Z, VTX[0] / 2, P.VTX_Y + VTX[1] / 2, VTX_Z + VTX[2]),
            "pcb",
            1.0,
        ),
        "rx": (
            box(-RX[0] / 2, P.RX_Y - RX[1] / 2, P.Z_DECK + 2, RX[0] / 2, P.RX_Y + RX[1] / 2, P.Z_DECK + 2 + RX[2]),
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
