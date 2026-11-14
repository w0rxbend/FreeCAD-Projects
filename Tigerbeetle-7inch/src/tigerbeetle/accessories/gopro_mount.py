"""Action-camera mount: a base on the four accessory holes at the front of the top plate, with the
three GoPro prongs. The plate's holes are 5.3 mm: use M3 bolts with washers, or M5."""

from zhalo.accessories.kit import (
    D_M3_FREE,
    D_M3_HEAD,
    M5_NUT_AF,
    Accessory,
    cylinder,
    disc,
    hexagon,
    hull,
    poly,
    prism,
    prism_x,
)

from tigerbeetle import equipment as E
from tigerbeetle import model as M

BASE_T = 4.0
HEAD_RECESS = 2.0
EAR_R = 5.5
PRONG_T, PRONG_GAP = 3.0, 3.2
PIVOT_D, PIVOT_H, PRONG_R, NUT_BOSS = 5.3, 11.5, 7.5, 3.2


def corners():
    top = M.plates()["top_plate"]
    own = [h for h in top.holes if h.d > 4.0 and abs(h.x) > 20.0]
    return sorted(((h.x, h.y) for h in own), key=lambda p: (p[1], p[0]))


def build() -> list[Accessory]:
    c = corners()
    z0 = M.Z_TOP + M.T_PLATE
    ring = [p for p in c if p[0] > 0] + [p for p in c if p[0] < 0][::-1]
    ring = sorted(c, key=lambda p: __import__("math").atan2(p[1] - 77, p[0]))
    base = prism(hull([(p, EAR_R) for p in ring]), z0, z0 + BASE_T)
    y = sum(p[1] for p in c) / len(c)
    zp = z0 + BASE_T + PIVOT_H
    tab = poly(
        [
            (y - PRONG_R - 2, z0 + BASE_T - 0.01),
            (y + PRONG_R + 2, z0 + BASE_T - 0.01),
            (y + PRONG_R, zp),
            (y - PRONG_R, zp),
        ]
    ) + disc((y, zp), 2 * PRONG_R)
    pitch = PRONG_T + PRONG_GAP
    part = base
    for k in (-1, 0, 1):
        part += prism_x(tab, k * pitch - PRONG_T / 2, k * pitch + PRONG_T / 2)
    xb = pitch + PRONG_T / 2
    part += prism_x(tab, xb - 0.01, xb + NUT_BOSS)
    part -= prism_x(disc((y, zp), PIVOT_D), -pitch - PRONG_T, xb + NUT_BOSS + 1)
    part -= prism_x(hexagon((y, zp), M5_NUT_AF), xb, xb + NUT_BOSS + 1)
    for p in c:
        part -= cylinder(*p, z0 - 1, z0 + BASE_T + 1, D_M3_FREE)
        part -= cylinder(*p, z0 + BASE_T - HEAD_RECESS, z0 + BASE_T + 1, D_M3_HEAD)
    front = E.BATTERY_Y + E.BATTERY[1] / 2
    own = [
        (
            "room for the battery behind it",
            min(p[1] for p in c) - EAR_R >= front,
            f"base from Y {min(p[1] for p in c) - EAR_R:.1f}, battery to Y {front:.1f}",
        )
    ]
    return [
        Accessory(
            "gopro_mount",
            "Action-camera mount (GoPro prongs)",
            part,
            checks=own,
            ceilings=40.0,
            overhang=30.0,
            hardware="4x M3x12 + washer + nyloc (the plate's holes are 5.3 mm), M5 nut + thumbscrew",
        )
    ]
