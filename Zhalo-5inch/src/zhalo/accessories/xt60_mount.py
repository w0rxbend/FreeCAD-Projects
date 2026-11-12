"""XT60 holder at the tail: keeps the quad-side connector upright behind the top plate.

The battery lead plugs in from above with one hand, and the pigtail cannot be pulled into
the rear props. The two power wires drop straight down behind the plate and run forward to
the ESC through the gap above the tail mount.
"""

from zhalo.accessories.kit import D_M3_FREE, FIT, Accessory, P, box, cylinder, hull, prism

XT60 = (15.8, 8.2)  # body cross-section
GRIP_H = 11.0
WALL_T = 1.8
FLOOR_T = 1.4
WIRES = (12.5, 5.2)  # floor opening for the two solder cups and wires
EAR_T = 3.0
EAR_R = 5.0
Z0 = P.Z_ROOF
Y_C = -72.0 - 0.6 - WIRES[1] / 2  # wires pass just behind the top plate's tail notch


def build() -> list[Accessory]:
    w, t = XT60[0] + 2 * FIT, XT60[1] + 2 * FIT
    x_out, y_half = w / 2 + WALL_T, t / 2 + WALL_T
    part = box(-x_out, Y_C - y_half, Z0, x_out, Y_C + y_half, Z0 + FLOOR_T + GRIP_H)
    ears = hull([((-P.R[0], P.R[1]), EAR_R), ((P.R[0], P.R[1]), EAR_R)])
    part += prism(ears, Z0, Z0 + EAR_T)
    part -= box(-w / 2, Y_C - t / 2, Z0 + FLOOR_T, w / 2, Y_C + t / 2, Z0 + FLOOR_T + GRIP_H + 1)
    part -= box(-WIRES[0] / 2, Y_C - WIRES[1] / 2, Z0 - 1, WIRES[0] / 2, Y_C + WIRES[1] / 2, Z0 + FLOOR_T + 1)
    for sx in (1, -1):
        part -= cylinder(sx * P.R[0], P.R[1], Z0 - 1, Z0 + EAR_T + 1, D_M3_FREE)
    own = [
        (
            "wires drop behind the top plate",
            Y_C + WIRES[1] / 2 <= -72.0,
            f"opening Y {Y_C - WIRES[1] / 2:.1f} to {Y_C + WIRES[1] / 2:.1f}, plate notch at Y -72.0",
        )
    ]
    return [
        Accessory(
            "xt60_mount",
            "XT60 holder",
            part,
            checks=own,
            in_assembly=False,
            hardware="2x M3x12 (replace the rear top-plate screws)",
            notes=(
                "Shares the rear top-plate screws with the GPS tray: fit one or the other. Push the "
                "soldered XT60 in from above; a drop of CA on the TPU holds it for good."
            ),
        )
    ]
