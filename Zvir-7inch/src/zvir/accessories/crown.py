"""Crown: GPS tray and antenna holder on the tail of the top plate.

Three spikes over the two tail screws: an upright tab in the middle for the VTX antenna's SMA
socket, and a tube leaning out on each side for the receiver's two antenna ends. Ahead of
them, a pocket for the GPS module.
"""

from build123d import Axis, Vector
from zhalo import equipment as E
from zhalo.accessories.kit import D_M3_FREE, FIT, WALL, Accessory, P, box, cylinder, disc, hull, poly, prism, prism_y

GPS = (22.0, 20.0, 6.0)  # module width (X), length (Y), height: BN-220 class
FLOOR_T = 1.2
BAR_T = 3.0
EAR_R = 5.0
LIP, LIP_LEN = 0.8, 8.0
LEAD_W = 9.0  # opening in the pocket's front wall for the lead
TAB = (14.0, 3.0, 17.0)  # width, thickness, height of the SMA tab
SMA_D, SMA_H = 6.5, 9.0
TUBE_X, TUBE_LEAN, TUBE_LEN = 15.0, 30.0, 17.0
TUBE_OD, TUBE_BORE = 6.4, 3.2
Z0 = P.Z_ROOF


def build() -> list[Accessory]:
    rx, ry = P.R
    part = prism(hull([((-rx, ry), EAR_R), ((rx, ry), EAR_R)]), Z0, Z0 + BAR_T)
    # GPS pocket ahead of the bar
    w, l, h = GPS[0] + 2 * FIT, GPS[1] + 2 * FIT, GPS[2]
    y0 = ry + EAR_R - WALL
    y1 = y0 + WALL + l + WALL
    yc, x_out, top = (y0 + y1) / 2, w / 2 + WALL, Z0 + FLOOR_T + h
    part += box(-x_out, y0, Z0, x_out, y1, top + LIP)
    part -= box(-w / 2, y0 + WALL, Z0 + FLOOR_T, w / 2, y1 - WALL, top + LIP + 1)
    for sx in (1, -1):
        x_in, x_w = (w / 2 - LIP, w / 2) if sx > 0 else (-w / 2, -w / 2 + LIP)
        part += box(x_in, yc - LIP_LEN / 2, top, x_w, yc + LIP_LEN / 2, top + LIP)
    part -= box(-LEAD_W / 2, y1 - WALL - 1, Z0 + FLOOR_T, LEAD_W / 2, y1 + 1, top + LIP + 1)
    # the middle spike: SMA tab with a pointed top
    tw, tt, th = TAB
    y_tab = ry - EAR_R + 0.5
    tab = poly(
        [
            (-tw / 2, Z0 + BAR_T - 0.01),
            (tw / 2, Z0 + BAR_T - 0.01),
            (tw / 2, Z0 + th - 5),
            (0.0, Z0 + th),
            (-tw / 2, Z0 + th - 5),
        ]
    )
    tab -= disc((0.0, Z0 + SMA_H), SMA_D)
    part += prism_y(tab, y_tab, y_tab + tt)
    # the side spikes: tubes for the receiver antenna, leaning outwards
    for sx in (1, -1):
        tube = cylinder(0.0, 0.0, -4.0, TUBE_LEN, TUBE_OD).rotate(Axis.Y, sx * TUBE_LEAN)
        part += tube.translate(Vector(sx * TUBE_X, ry, Z0 + BAR_T - 0.5))
    part &= box(-80.0, ry - 40.0, Z0, 80.0, ry + 60.0, Z0 + 60.0)
    for sx in (1, -1):
        bore = cylinder(0.0, 0.0, -8.0, TUBE_LEN + 2.0, TUBE_BORE).rotate(Axis.Y, sx * TUBE_LEAN)
        part -= bore.translate(Vector(sx * TUBE_X, ry, Z0 + BAR_T - 0.5))
        part -= cylinder(sx * rx, ry, Z0 - 1, Z0 + BAR_T + 1, D_M3_FREE)
    battery_rear = E.BATTERY_Y - E.BATTERY_SIZE[1] / 2
    head = rx - 2.9 - (TUBE_X + (TUBE_LEN - 4) * 0.5 + TUBE_OD / 2)
    own = [
        ("sits behind the battery", y1 <= battery_rear, f"pocket to Y {y1:.1f}, battery from Y {battery_rear:.1f}"),
        ("GPS pocket", True, f"{w:.1f} x {l:.1f} x {h:.1f} mm for a {GPS[0]:.0f} x {GPS[1]:.0f} mm module"),
        ("a driver reaches both screws past the tubes", head >= 0.5, f"{head:.1f} mm between a tube and a screw head"),
    ]
    return [
        Accessory(
            "crown",
            "Crown (GPS tray and antenna holder)",
            part,
            checks=own,
            color="accent",
            ceilings=2 * LIP * LIP_LEN + 10.0,
            overhang=30.0,
            hardware="2x M3x12 (replace the tail top-plate screws); the SMA socket's own nut",
            notes=(
                "VTX pigtail through the tab, antenna pointing back; the receiver's antenna ends push into the two "
                "tubes. The GPS module presses under the two lips, lead to the front."
            ),
        )
    ]
