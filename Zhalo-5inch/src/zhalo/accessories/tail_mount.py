"""Tail mount: VTX antenna and receiver antenna at the back of the frame.

Two sleeves on the rear standoffs joined by a back wall. A wedge on the wall carries an SMA
bulkhead pointing 40 deg up and back; a snap channel under it holds the bar of a 2.4 GHz
T antenna, low enough to pass under the rear props. The bottom plate's stinger sits below
both and takes the ground hits.
"""

from math import cos, radians, sin

from build123d import Axis, Vector

from zhalo import checks as C
from zhalo import frame as F
from zhalo.accessories.kit import (
    SLEEVE_BORE,
    SLEEVE_OD,
    SLEEVE_TOP,
    WALL,
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

Z0 = P.Z_ARM
WALL_T = 2.4
WALL_Y = (P.R[1] - SLEEVE_OD / 2, P.R[1] - SLEEVE_OD / 2 + WALL_T)  # rear face, front face
SMA_TILT = 40.0  # antenna axis above horizontal
SMA_D = 6.5  # 1/4"-36 bulkhead thread
SMA_HEX_AF = 8.2  # the bulkhead's hex body sits in a pocket so the nut can be tightened
SMA_SEAT = 3.0  # TPU between the hex body and the nut
WEDGE_OUT = 7.5  # how far the wedge stands behind the wall
WEDGE_Z = 8.5  # where its 45 deg underside leaves the wall
WEDGE_W = 14.0
T_D = 4.7  # bar of an ELRS T antenna
T_MOUTH = 3.5
T_AXIS = (WALL_Y[0] - 2.9, Z0 + T_D / 2 + WALL)  # (y, z) of the bar: a full wall of TPU under it
T_LEN = 20.0


def _sma_axis():
    """(point on the slanted face, unit vector pointing out along the antenna), both as (y, z)."""
    y0, z0 = WALL_Y[0] - WEDGE_OUT, WEDGE_Z + WEDGE_OUT
    run = WEDGE_OUT / sin(radians(SMA_TILT))  # length of the slanted face
    mid = (y0 + run / 2 * sin(radians(SMA_TILT)), z0 + run / 2 * cos(radians(SMA_TILT)))
    return mid, (-cos(radians(SMA_TILT)), sin(radians(SMA_TILT)))


def _along_axis(d: float, depth0: float, depth1: float):
    """Round or hex tool along the SMA axis between two depths measured inwards from the slanted face."""
    (my, mz), (uy, uz) = _sma_axis()
    tool = prism(hexagon((0, 0), d) if d == SMA_HEX_AF else disc((0, 0), d), -depth1, -depth0)
    # the tool is built along +Z; lean it back so +Z becomes the antenna axis, then move it to the face
    return tool.rotate(Axis.X, 90.0 - SMA_TILT).translate(Vector(0, my, mz))


def build() -> list[Accessory]:
    x = P.R[0]
    part = cylinder(x, P.R[1], Z0, SLEEVE_TOP, SLEEVE_OD) + cylinder(-x, P.R[1], Z0, SLEEVE_TOP, SLEEVE_OD)
    part += box(-x, WALL_Y[0], Z0, x, WALL_Y[1], SLEEVE_TOP)
    (my, mz), _u = _sma_axis()
    top = (WALL_Y[0], WEDGE_Z + WEDGE_OUT + WEDGE_OUT / sin(radians(SMA_TILT)) * cos(radians(SMA_TILT)))
    wedge = poly(
        [(WALL_Y[0] + 0.01, WEDGE_Z), (WALL_Y[0] - WEDGE_OUT, WEDGE_Z + WEDGE_OUT), top, (WALL_Y[0] + 0.01, top[1])]
    )
    part += prism_x(wedge, -WEDGE_W / 2, WEDGE_W / 2)
    # T-antenna channel: a block behind the wall with a bore along X and a mouth to the rear
    ty, tz = T_AXIS
    r_out = T_D / 2 + WALL
    channel = (
        disc((ty, tz), 2 * r_out)  # the snap ring round the bar ...
        + poly(
            [(WALL_Y[0] + 0.01, Z0), (ty - r_out, Z0), (ty - r_out, tz), (WALL_Y[0] + 0.01, tz)]
        )  # ... a square foot
        + poly([(WALL_Y[0] + 0.01, tz - 0.01), (ty, tz - 0.01), (ty, tz + r_out), (WALL_Y[0] + 0.01, tz + r_out + 2.9)])
    )
    part += prism_x(channel, -T_LEN / 2, T_LEN / 2)
    part -= prism_x(disc((ty, tz), T_D), -T_LEN, T_LEN)
    part -= prism_x(
        poly(
            [
                (ty, tz - T_MOUTH / 2),
                (ty - r_out - 1, tz - T_MOUTH / 2),
                (ty - r_out - 1, tz + T_MOUTH / 2),
                (ty, tz + T_MOUTH / 2),
            ]
        ),
        -T_LEN,
        T_LEN,
    )
    depth = 40.0
    part -= _along_axis(SMA_D, -1.0, depth)
    part -= _along_axis(SMA_HEX_AF, SMA_SEAT, depth)
    for sx in (1, -1):
        part -= cylinder(sx * x, P.R[1], Z0 - 1, SLEEVE_TOP + 1, SLEEVE_BORE)
    antenna = _along_axis(9.5, -60.0, 0.0)  # the antenna itself: nut, stem and head
    tips = 2 * 30.0  # a T antenna is up to 60 mm across
    blocked = [n for n, p in F.parts().items() if C.overlap(antenna, p) > C.EPS]
    own = [
        ("antenna leaves clear of the frame", not blocked, f"60 mm along the axis: {blocked or 'clear'}"),
        (
            "T antenna passes under the rear props",
            T_AXIS[1] + T_D / 2 < P.PROP_Z[0] - 5,
            f"bar at Z {T_AXIS[1]:.1f}, props from Z {P.PROP_Z[0]:.0f}; up to {tips:.0f} mm tip to tip",
        ),
        ("TPU between the SMA hex and its nut", 2.5 <= SMA_SEAT <= 4.0, f"{SMA_SEAT} mm"),
    ]
    return [
        Accessory(
            "tail_mount",
            "Tail mount: VTX antenna (SMA) and T antenna",
            part,
            checks=own,
            ceilings=55.0,
            overhang=70.0,
            hardware="SMA bulkhead pigtail with its own nut",
            notes=(
                "Slide the sleeves over the rear standoffs before the top plate goes on. Push the SMA "
                "bulkhead through from inside until its hex sits in the pocket, nut on the outside. "
                "Snap the T antenna bar into the channel under the wedge."
            ),
        )
    ]
