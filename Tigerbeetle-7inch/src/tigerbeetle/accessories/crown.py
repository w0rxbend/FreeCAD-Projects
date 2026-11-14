"""Crown: GPS tray and antenna holder on the tail of the top plate, on the two rear standoff screws.

A tray for the GPS module ahead of the screws, a tab for the VTX antenna's SMA socket between them
and two tubes leaning out for the receiver's antenna ends.
"""

from build123d import Axis, Vector
from zhalo.accessories.kit import D_M3_FREE, FIT, WALL, Accessory, box, cylinder, disc, hull, poly, prism, prism_y

from tigerbeetle import equipment as E
from tigerbeetle import frame as F
from tigerbeetle import model as M

GPS = (22.0, 20.0, 6.0)
FLOOR_T, EAR_T, EAR_R = 1.2, 3.0, 5.0
LIP, LIP_LEN = 0.8, 8.0
TAB = (14.0, 17.0)
SMA_D, SMA_H = 6.5, 11.0
TUBE_LEAN, TUBE_LEN, TUBE_OD, TUBE_BORE = 30.0, 17.0, 6.4, 3.2


def build() -> list[Accessory]:
    s = F.standoffs()["standoff_rear_right"]
    rx, ry = s[0], s[1]
    z0 = M.Z_TOP + M.T_PLATE
    part = prism(hull([((-rx, ry), EAR_R), ((rx, ry), EAR_R)]), z0, z0 + EAR_T)
    w, l, h = GPS[0] + 2 * FIT, GPS[1] + 2 * FIT, GPS[2]
    y0 = ry + EAR_R - 1.0
    y1 = y0 + WALL + l + WALL
    yc, x_out, top = (y0 + y1) / 2, w / 2 + WALL, z0 + FLOOR_T + h
    part += box(-x_out, y0, z0, x_out, y1, top + LIP)
    part -= box(-w / 2, y0 + WALL, z0 + FLOOR_T, w / 2, y1 - WALL, top + LIP + 1)
    for sx in (1, -1):
        x_in, x_w = (w / 2 - LIP, w / 2) if sx > 0 else (-w / 2, -w / 2 + LIP)
        part += box(x_in, yc - LIP_LEN / 2, top, x_w, yc + LIP_LEN / 2, top + LIP)
    tw, th = TAB
    tab = poly(
        [
            (-tw / 2, z0 + EAR_T - 0.01),
            (tw / 2, z0 + EAR_T - 0.01),
            (tw / 2, z0 + th - 5),
            (0.0, z0 + th),
            (-tw / 2, z0 + th - 5),
        ]
    )
    tab -= disc((0.0, z0 + SMA_H), SMA_D)
    part += prism_y(tab, ry - 1.5, ry + 1.5)
    for sx in (1, -1):
        tube = cylinder(0, 0, -4.0, TUBE_LEN, TUBE_OD).rotate(Axis.Y, sx * TUBE_LEAN)
        part += tube.translate(Vector(sx * (rx - 7.5), ry, z0 + EAR_T - 0.5))
    part &= box(-80, ry - 40, z0, 80, ry + 80, z0 + 60)
    for sx in (1, -1):
        bore = cylinder(0, 0, -8.0, TUBE_LEN + 2, TUBE_BORE).rotate(Axis.Y, sx * TUBE_LEAN)
        part -= bore.translate(Vector(sx * (rx - 7.5), ry, z0 + EAR_T - 0.5))
        part -= cylinder(sx * rx, ry, z0 - 1, z0 + EAR_T + 1, D_M3_FREE)
    rear = E.BATTERY_Y - E.BATTERY[1] / 2
    own = [("sits behind the battery", y1 <= rear, f"tray to Y {y1:.1f}, battery from Y {rear:.1f}")]
    return [
        Accessory(
            "crown",
            "Crown (GPS tray and antenna holder)",
            part,
            checks=own,
            color="accent",
            ceilings=2 * LIP * LIP_LEN + 12.0,
            overhang=40.0,
            hardware="2x M3x12 (replace the two rear top-plate screws); the SMA socket's own nut",
            notes="GPS under the two lips; VTX pigtail through the tab; receiver antenna ends in the two tubes.",
        )
    ]
