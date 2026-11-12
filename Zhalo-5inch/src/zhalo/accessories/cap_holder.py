"""Capacitor saddle: keeps the low-ESR capacitor off the carbon and under one zip tie.

Sized for the 10 mm can that ships with the stack (1000 uF 35 V); CAP_D is the only number
to change for a 12.5 or 13 mm can. Shown in the front bay, where a tie passed through the
two chevron windows goes round the plate, the saddle and the can.
"""

from zhalo.accessories.kit import FIT, Accessory, P, box, disc, poly, prism_x

CAP_D = 10.0
FLOOR_T = 1.6
LENGTH = 14.0  # along the can
TIE_W = 3.2  # groove for a 2.5-3 mm zip tie
CHEEK_Z = 0.42  # the cheeks rise to this share of the can diameter
CHEVRONS = (27.5, 38.5)  # the two chevron windows of the bottom plate's front bay
Y_C = sum(CHEVRONS) / 2 + 2.5  # midway between their points
TIE_DEPTH = 0.8
Z0 = P.Z_ARM


def build() -> list[Accessory]:
    r = CAP_D / 2 + FIT
    half = r + 1.2
    axis_z = Z0 + FLOOR_T + r
    top = Z0 + FLOOR_T + CAP_D * CHEEK_Z
    block = poly([(Y_C - half, Z0), (Y_C + half, Z0), (Y_C + half, top), (Y_C - half, top)], 0.8)
    part = prism_x(block, -LENGTH / 2, LENGTH / 2) - prism_x(disc((Y_C, axis_z), 2 * r), -LENGTH, LENGTH)
    for y0, y1 in ((Y_C - half - 1, Y_C - half + TIE_DEPTH), (Y_C + half - TIE_DEPTH, Y_C + half + 1)):
        part -= box(-TIE_W / 2, y0, Z0 - 1, TIE_W / 2, y1, top + 1)  # tie groove down each side
    # the tie comes up through the chevron windows either side: both flanks must stand over a window
    windows = [(y + 2.5 - 2.2, y + 2.5 + 2.2) for y in CHEVRONS]
    flanks = (Y_C - half + TIE_DEPTH, Y_C + half - TIE_DEPTH)
    over = all(any(lo <= f <= hi for lo, hi in windows) for f in flanks)
    own = [
        ("a full wall under the can", FLOOR_T >= 1.6, f"{FLOOR_T} mm"),
        (
            "zip tie runs straight up through the chevron windows",
            over,
            f"tie at Y {flanks[0]:.1f} and {flanks[1]:.1f}; windows at Y {windows[0][0]:.1f}-{windows[0][1]:.1f} "
            f"and {windows[1][0]:.1f}-{windows[1][1]:.1f}",
        ),
    ]
    return [
        Accessory(
            "cap_holder",
            f"Capacitor saddle ({CAP_D:.0f} mm can)",
            part,
            checks=own,
            hardware="1x 2.5 mm zip tie",
            notes="Lay the can in the saddle and tie it down through the two chevron windows under it.",
        )
    ]
