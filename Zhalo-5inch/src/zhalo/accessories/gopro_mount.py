"""Action-camera mount: a base on the front of the top plate with a three-prong GoPro pivot.

The front screws go through the base and the top plate into the front standoffs; the rear
ones use the accessory holes (nyloc nuts under the plate, or the optional fifth standoff pair).
"""

from zhalo import equipment as E
from zhalo.accessories.kit import (
    D_M3_FREE,
    D_M3_HEAD,
    M5_NUT_AF,
    Accessory,
    P,
    cylinder,
    disc,
    hexagon,
    hull,
    poly,
    prism,
    prism_x,
)

BASE_T = 4.0
HEAD_RECESS = 2.0
EAR_R = 5.5
PRONG_T, PRONG_GAP = 3.0, 3.2  # the camera's two fingers are 3 mm thick
PIVOT_D = 5.3  # M5 thumbscrew
PIVOT_H = 11.5  # pivot above the base
PIVOT_Y = (P.F[1] + P.A1[1]) / 2
PRONG_R = 7.5
NUT_BOSS = 3.2  # extra thickness on one outer prong to bury the M5 nut
Z0 = P.Z_ROOF


def build() -> list[Accessory]:
    corners = [(P.A1[0], P.A1[1]), (P.F[0], P.F[1]), (-P.F[0], P.F[1]), (-P.A1[0], P.A1[1])]
    base = prism(hull([(c, EAR_R) for c in corners]), Z0, Z0 + BASE_T)
    zp = Z0 + BASE_T + PIVOT_H
    tab = poly(
        [
            (PIVOT_Y - PRONG_R - 2.0, Z0 + BASE_T - 0.01),
            (PIVOT_Y + PRONG_R + 2.0, Z0 + BASE_T - 0.01),
            (PIVOT_Y + PRONG_R, zp),
            (PIVOT_Y - PRONG_R, zp),
        ]
    ) + disc((PIVOT_Y, zp), 2 * PRONG_R)
    pitch = PRONG_T + PRONG_GAP
    part = base
    for k in (-1, 0, 1):
        part += prism_x(tab, k * pitch - PRONG_T / 2, k * pitch + PRONG_T / 2)
    x_boss = pitch + PRONG_T / 2
    part += prism_x(tab, x_boss - 0.01, x_boss + NUT_BOSS)
    part -= prism_x(disc((PIVOT_Y, zp), PIVOT_D), -pitch - PRONG_T, x_boss + NUT_BOSS + 1)
    part -= prism_x(hexagon((PIVOT_Y, zp), M5_NUT_AF), x_boss, x_boss + NUT_BOSS + 1)
    for c in corners:
        part -= cylinder(*c, Z0 - 1, Z0 + BASE_T + 1, D_M3_FREE)
        part -= cylinder(*c, Z0 + BASE_T - HEAD_RECESS, Z0 + BASE_T + 1, D_M3_HEAD)
    battery_front = E.BATTERY_Y + E.BATTERY_SIZE[1] / 2
    own = [
        (
            "room left for the battery behind the base",
            P.A1[1] - EAR_R >= battery_front,
            f"base from Y {P.A1[1] - EAR_R:.1f}, battery to Y {battery_front:.1f}",
        ),
        (
            "prongs fit a GoPro's two 3 mm fingers",
            abs(PRONG_GAP - 3.2) < 0.25 and abs(PRONG_T - 3.0) < 0.2,
            f"{PRONG_T} mm prongs, {PRONG_GAP} mm gaps",
        ),
    ]
    return [
        Accessory(
            "gopro_mount",
            "Action-camera mount (GoPro prongs)",
            part,
            checks=own,
            ceilings=35.0,
            overhang=25.0,
            hardware="2x M3x12 (front, into the standoffs), 2x M3x10 + nyloc (rear), M5 nut + thumbscrew",
            notes="Replaces the two front top-plate screws. The M5 nut presses into the hex pocket on the right prong.",
        )
    ]
