"""GPS tray on the tail of the top plate, behind the battery.

A shallow pocket with two snap lips, held by the two rear top-plate screws. The pocket is a
parameter: the default takes a 22 x 20 mm module (BN-220 class); 18 and 20 mm modules sit
in it on a piece of foam tape.
"""

from zhalo import equipment as E
from zhalo.accessories.kit import D_M3_FREE, FIT, WALL, Accessory, P, box, cylinder, hull, prism

GPS = (22.0, 20.0, 6.0)  # module width (X), length (Y), height
FLOOR_T = 1.2
EAR_T = 3.0
EAR_R = 5.0
LIP = 0.8
LIP_LEN = 8.0
CABLE = (9.0, 5.0)  # opening in the floor for the lead; it drops through a chevron window
Z0 = P.Z_ROOF
REAR_Y = P.R[1] - 1.5  # rear edge of the tray


def build() -> list[Accessory]:
    w, l, h = GPS[0] + 2 * FIT, GPS[1] + 2 * FIT, GPS[2]
    y1 = REAR_Y + WALL + l + WALL  # front edge
    yc = (REAR_Y + y1) / 2
    x_out = w / 2 + WALL
    top = Z0 + FLOOR_T + h
    part = box(-x_out, REAR_Y, Z0, x_out, y1, top + LIP)
    ears = hull([((-P.R[0], P.R[1]), EAR_R), ((P.R[0], P.R[1]), EAR_R)])
    part += prism(ears, Z0, Z0 + EAR_T)
    part -= box(-w / 2, REAR_Y + WALL, Z0 + FLOOR_T, w / 2, y1 - WALL, top + LIP + 1)  # pocket
    for sx in (1, -1):  # two lips over the long sides, mid-length
        part += box(
            sx * (w / 2 - LIP) if sx > 0 else -w / 2,
            yc - LIP_LEN / 2,
            top,
            sx * w / 2 if sx > 0 else -w / 2 + LIP,
            yc + LIP_LEN / 2,
            top + LIP,
        )
    part -= box(-CABLE[0] / 2, yc - CABLE[1] / 2, Z0 - 1, CABLE[0] / 2, yc + CABLE[1] / 2, Z0 + FLOOR_T + 1)
    for sx in (1, -1):
        part -= cylinder(sx * P.R[0], P.R[1], Z0 - 1, Z0 + EAR_T + 1, D_M3_FREE)
    battery_rear = E.BATTERY_Y - E.BATTERY_SIZE[1] / 2
    own = [
        ("tray sits behind the battery", y1 <= battery_rear, f"tray to Y {y1:.1f}, battery from Y {battery_rear:.1f}"),
        ("pocket", True, f"{w:.1f} x {l:.1f} x {h:.1f} mm for a {GPS[0]:.0f} x {GPS[1]:.0f} mm module"),
    ]
    return [
        Accessory(
            "gps_mount",
            "GPS tray",
            part,
            checks=own,
            ceilings=2 * LIP * LIP_LEN + 2.0,
            hardware="2x M3x12 (replace the rear top-plate screws)",
            notes=(
                "Shares the rear top-plate screws with the XT60 mount: fit one or the other. "
                "Press the module under the two lips; the lead drops through the floor opening."
            ),
        )
    ]
