"""Tail mount: the VTX antenna at the back of the frame.

Two sleeves on the rear standoffs, a back wall between them and a wedge that carries an SMA
bulkhead pointing 40 deg up and back. It stands on the deck, with the sandwich tail under it.
The receiver antenna has its own clip on an arm (antenna_clip), away from the VTX antenna.
"""

from math import cos, radians, sin

from build123d import Axis, Vector
from zhalo import checks as C
from zhalo import frame as F
from zhalo.accessories.kit import (
    SLEEVE_BORE,
    SLEEVE_OD,
    SLEEVE_TOP,
    Accessory,
    P,
    box,
    cylinder,
    disc,
    hexagon,
    poly,
    prism,
    prism_x,
)

Z0 = P.Z_BAY
WALL_T = 2.4
Y0 = P.R[1] - SLEEVE_OD / 2  # rear face of the back wall
SMA_TILT = 40.0
SMA_D = 6.5
SMA_HEX_AF = 8.2
SMA_SEAT = 3.0
WEDGE_OUT = 7.5
WEDGE_Z = Z0 + 1.5
WEDGE_W = 14.0


def _face_mid() -> tuple[float, float]:
    run = WEDGE_OUT / sin(radians(SMA_TILT))
    return (Y0 - WEDGE_OUT + run / 2 * sin(radians(SMA_TILT)), WEDGE_Z + WEDGE_OUT + run / 2 * cos(radians(SMA_TILT)))


def _along_axis(shape, depth0: float, depth1: float):
    """A tool along the antenna axis, between two depths measured inwards from the slanted face."""
    my, mz = _face_mid()
    return prism(shape, -depth1, -depth0).rotate(Axis.X, 90.0 - SMA_TILT).translate(Vector(0, my, mz))


def build() -> list[Accessory]:
    x = P.R[0]
    part = cylinder(x, P.R[1], Z0, SLEEVE_TOP, SLEEVE_OD) + cylinder(-x, P.R[1], Z0, SLEEVE_TOP, SLEEVE_OD)
    part += box(-x, Y0, Z0, x, Y0 + WALL_T, SLEEVE_TOP)
    top_z = WEDGE_Z + WEDGE_OUT + WEDGE_OUT / sin(radians(SMA_TILT)) * cos(radians(SMA_TILT))
    wedge = poly([(Y0 + 0.01, WEDGE_Z), (Y0 - WEDGE_OUT, WEDGE_Z + WEDGE_OUT), (Y0, top_z), (Y0 + 0.01, top_z)])
    part += prism_x(wedge, -WEDGE_W / 2, WEDGE_W / 2)
    part -= _along_axis(disc((0, 0), SMA_D), -1.0, 40.0)
    part -= _along_axis(hexagon((0, 0), SMA_HEX_AF), SMA_SEAT, 40.0)
    for sx in (1, -1):
        part -= cylinder(sx * x, P.R[1], Z0 - 1, SLEEVE_TOP + 1, SLEEVE_BORE)
    antenna = _along_axis(disc((0, 0), 9.5), -60.0, 0.0)
    blocked = [n for n, p in F.parts().items() if C.overlap(antenna, p) > C.EPS]
    own = [
        ("antenna leaves clear of the frame", not blocked, f"60 mm along the axis: {blocked or 'clear'}"),
        (
            "wedge fits under the sleeve tops",
            top_z <= SLEEVE_TOP,
            f"wedge to Z {top_z:.1f}, sleeves to Z {SLEEVE_TOP:.1f}",
        ),
    ]
    return [
        Accessory(
            "tail_mount",
            "Tail mount: VTX antenna (SMA)",
            part,
            checks=own,
            ceilings=55.0,
            overhang=60.0,
            hardware="SMA bulkhead pigtail with its own nut",
            notes=(
                "Slide the sleeves over the rear standoffs before the top plate goes on. Push the SMA bulkhead "
                "through from inside until its hex sits in the pocket, nut on the outside."
            ),
        )
    ]
