"""Perch: GPS tray and antenna holder on the tail, on the two rear top-plate screws.

The battery covers the top of the body from end to end, so the GPS sits behind it, on a tray
that reaches out past the rim. Two ears hold it and leave the tail notch between them open
for the battery lead. Three spikes: a tab at the back for the VTX antenna's SMA socket and a
tube leaning out on each side for the receiver's antenna ends.
"""

from build123d import Axis, Vector
from zhalo import equipment as E
from zhalo.accessories.kit import D_M3_FREE, FIT, WALL, Accessory, P, box, cylinder, disc, hull, poly, prism, prism_y

GPS = (22.0, 20.0, 6.0)  # module width (X), length (Y), height: BN-220 class
FLOOR_T = 1.2
EAR_T = 3.0
EAR_R = 5.0
LIP, LIP_LEN = 0.8, 8.0
LEAD_W = 9.0  # opening in the pocket's front wall for the lead
TAB = (14.0, 17.0)  # width and height of the SMA tab
SMA_D, SMA_H = 6.5, 12.0
TUBE_LEAN, TUBE_LEN = 30.0, 17.0
TUBE_OD, TUBE_BORE = 6.4, 3.2
Z0 = P.Z_ROOF


def build() -> list[Accessory]:
    rx, ry = P.R
    w, l, h = GPS[0] + 2 * FIT, GPS[1] + 2 * FIT, GPS[2]
    x_out = w / 2 + WALL
    y1 = ry - EAR_R  # front of the tray: level with the back of the ears
    y0 = y1 - (WALL + l + WALL)
    yc, top = (y0 + y1) / 2, Z0 + FLOOR_T + h
    knee = (x_out - 1.4, y1 - 4.0)  # where each ear runs into the tray
    part = box(-x_out, y0, Z0, x_out, y1, top + LIP)
    for sx in (1, -1):
        part += prism(hull([((sx * rx, ry), EAR_R), ((sx * knee[0], knee[1]), 4.0)][::sx]), Z0, Z0 + EAR_T)
    part -= box(-w / 2, y0 + WALL, Z0 + FLOOR_T, w / 2, y1 - WALL, top + LIP + 1)
    for sx in (1, -1):
        x_in, x_w = (w / 2 - LIP, w / 2) if sx > 0 else (-w / 2, -w / 2 + LIP)
        part += box(x_in, yc - LIP_LEN / 2, top, x_w, yc + LIP_LEN / 2, top + LIP)
    part -= box(-LEAD_W / 2, y1 - WALL - 1, Z0 + FLOOR_T, LEAD_W / 2, y1 + 1, top + LIP + 1)
    tw, th = TAB
    tab = poly([(-tw / 2, Z0), (tw / 2, Z0), (tw / 2, Z0 + th - 5), (0.0, Z0 + th), (-tw / 2, Z0 + th - 5)])
    tab -= disc((0.0, Z0 + SMA_H), SMA_D)
    part += prism_y(tab, y0, y0 + WALL + 1.4)
    for sx in (1, -1):
        tube = cylinder(0.0, 0.0, -4.0, TUBE_LEN, TUBE_OD).rotate(Axis.Y, sx * TUBE_LEAN)
        part += tube.translate(Vector(sx * knee[0], knee[1], Z0 + EAR_T - 0.5))
    part &= box(-80.0, y0 - 20.0, Z0, 80.0, ry + 40.0, Z0 + 60.0)
    for sx in (1, -1):
        bore = cylinder(0.0, 0.0, -8.0, TUBE_LEN + 2.0, TUBE_BORE).rotate(Axis.Y, sx * TUBE_LEAN)
        part -= bore.translate(Vector(sx * knee[0], knee[1], Z0 + EAR_T - 0.5))
        part -= cylinder(sx * rx, ry, Z0 - 1, Z0 + EAR_T + 1, D_M3_FREE)
    battery_rear = E.BATTERY_Y - E.BATTERY_SIZE[1] / 2
    own = [
        (
            "sits behind the battery",
            ry + EAR_R <= battery_rear,
            f"ears to Y {ry + EAR_R:.1f}, battery from Y {battery_rear:.1f}",
        ),
        ("GPS pocket", True, f"{w:.1f} x {l:.1f} x {h:.1f} mm for a {GPS[0]:.0f} x {GPS[1]:.0f} mm module"),
        (
            "leaves the tail notch open for the battery lead",
            knee[0] - 4.0 >= 7.0,
            f"{2 * (knee[0] - 4.0):.1f} mm between the ears",
        ),
    ]
    return [
        Accessory(
            "perch",
            "Perch (GPS tray and antenna holder)",
            part,
            checks=own,
            color="accent",
            ceilings=2 * LIP * LIP_LEN + 10.0,
            overhang=30.0,
            hardware="2x M3x12 (replace the two rear top-plate screws); the SMA socket's own nut",
            notes=(
                "The GPS module presses under the two lips, lead to the front and down through the tail notch. "
                "VTX pigtail through the tab, antenna pointing back; the receiver's antenna ends go in the tubes."
            ),
        )
    ]
