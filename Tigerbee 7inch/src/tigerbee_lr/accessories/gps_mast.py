"""GPS mast: the GPS module 40 mm above the top plate, at the tail.

A GPS hears the satellites badly next to a video transmitter, an ESC or carbon. Raised on a mast
behind the battery it sees open sky and sits as far from the noise as the frame allows. The mast
flares at 40 deg up to the tray, so the whole part prints standing, without support.
"""

from build123d import extrude
from zhalo import equipment as E
from zhalo.accessories.kit import D_M3_FREE, FIT, WALL, Accessory, P, box, cylinder, hull, poly, prism

GPS = (25.0, 25.0, 8.0)  # covers the common 18-25 mm modules (M8N/M10 class)
HEIGHT = 40.0  # top of the tray above the top plate
BASE_T, EAR_R = 3.0, 5.0
COLUMN = (12.0, 12.0)  # at the foot
FLARE = 40.0  # degrees from vertical
FLOOR_T, LIP = 1.6, 0.8


def build() -> list[Accessory]:
    x, y = P.R
    z0 = P.Z_ROOF
    w, l, h = GPS[0] + 2 * FIT, GPS[1] + 2 * FIT, GPS[2]
    tray = (w + 2 * WALL, l + 2 * WALL)
    yc = y + 6.0  # the tray's middle: over the screws, behind the battery
    part = prism(hull([((-x, y), EAR_R), ((x, y), EAR_R)]), z0, z0 + BASE_T)
    part += box(-COLUMN[0] / 2 - 2, y, z0, COLUMN[0] / 2 + 2, yc + COLUMN[1] / 2 + 2, z0 + BASE_T)  # under the column
    z_tray = z0 + HEIGHT - FLOOR_T - h
    from math import radians, tan

    rise = (tray[0] - COLUMN[0]) / 2 / tan(radians(FLARE))
    column_top = z_tray - rise
    part += box(
        -COLUMN[0] / 2, yc - COLUMN[1] / 2, z0 + BASE_T - 0.01, COLUMN[0] / 2, yc + COLUMN[1] / 2, column_top + 0.01
    )
    flare = extrude(
        poly(
            [
                (-COLUMN[0] / 2, yc - COLUMN[1] / 2),
                (COLUMN[0] / 2, yc - COLUMN[1] / 2),
                (COLUMN[0] / 2, yc + COLUMN[1] / 2),
                (-COLUMN[0] / 2, yc + COLUMN[1] / 2),
            ]
        ),
        amount=rise,
        taper=-FLARE,
    ).translate((0, 0, column_top))
    part += flare
    part += box(-tray[0] / 2, yc - tray[1] / 2, z_tray - 0.01, tray[0] / 2, yc + tray[1] / 2, z_tray + FLOOR_T + h)
    part -= box(-w / 2, yc - l / 2, z_tray + FLOOR_T, w / 2, yc + l / 2, z_tray + FLOOR_T + h + 1)
    part -= box(-4.5, yc + l / 2 - 1, z_tray + FLOOR_T, 4.5, yc + tray[1] / 2 + 1, z_tray + FLOOR_T + h + 1)  # lead
    for sx in (1, -1):
        part -= cylinder(sx * x, y, z0 - 1, z0 + BASE_T + 1, D_M3_FREE)
    rear = E.BATTERY_Y - E.BATTERY_SIZE[1] / 2
    own = [
        ("GPS high above the electronics", HEIGHT >= 35.0, f"tray top {HEIGHT:g} mm above the top plate"),
        (
            "behind the battery",
            yc + tray[1] / 2 <= rear + 60.0 and yc - tray[1] / 2 > y - 30,
            f"tray Y {yc - tray[1] / 2:.0f}..{yc + tray[1] / 2:.0f}, battery from Y {rear:.0f}",
        ),
        ("prints standing", FLARE <= 45.0, f"flare {FLARE:g} deg from vertical"),
    ]
    _ = LIP
    return [
        Accessory(
            "gps_mast",
            "GPS mast",
            part,
            checks=own,
            color="accent",
            ceilings=12.0,
            overhang=40.0,
            hardware="2x M3x12 (replace the two rear top-plate screws); foam tape under the module",
            notes="Print it standing. The GPS module sits in the tray on foam tape, lead down the front slot.",
        )
    ]
