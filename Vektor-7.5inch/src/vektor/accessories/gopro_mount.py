"""Action-camera mount on the four nose holes of the battery plate (instead of the GPS tray)."""

from vektor.accessories.base import D_HEAD, D_M3, Accessory, P, cyl, prism, prism_x
from vektor.geometry import GOPRO_HOLES, disc, poly, soften

BASE_T, PRONG_T, PRONG_GAP, PIVOT_H, PRONG_R = 4.0, 3.0, 3.2, 11.0, 7.5


def build() -> list[Accessory]:
    xs = [p[0] for p in GOPRO_HOLES]
    ys = [p[1] for p in GOPRO_HOLES]
    z0 = P.Z_ROOF
    base = soften(
        poly(
            [
                (min(xs) - 6, min(ys) - 6),
                (max(xs) + 6, min(ys) - 6),
                (max(xs) + 6, max(ys) + 6),
                (min(xs) - 6, max(ys) + 6),
            ]
        ),
        4.0,
    )
    part = prism(base, z0, z0 + BASE_T)
    yc = (min(ys) + max(ys)) / 2
    zp = z0 + BASE_T + PIVOT_H
    tab = poly(
        [
            (yc - PRONG_R - 2, z0 + BASE_T - 0.01),
            (yc + PRONG_R + 2, z0 + BASE_T - 0.01),
            (yc + PRONG_R, zp),
            (yc - PRONG_R, zp),
        ]
    ) + disc((yc, zp), 2 * PRONG_R)
    pitch = PRONG_T + PRONG_GAP
    for k in (-1, 0, 1):
        part += prism_x(tab, k * pitch - PRONG_T / 2, k * pitch + PRONG_T / 2)
    part -= prism_x(disc((yc, zp), 5.3), -2 * pitch, 2 * pitch)
    for p in GOPRO_HOLES:
        part -= cyl(*p, z0 - 1, z0 + BASE_T + 1, D_M3)
        part -= cyl(*p, z0 + BASE_T - 1.8, z0 + BASE_T + 1, D_HEAD)
    return [
        Accessory(
            "gopro_mount",
            "Action-camera mount",
            part,
            color="dark",
            in_assembly=False,
            bridges=45.0,
            overhang=30.0,
            hardware="4x M3x10 + nyloc, M5 thumbscrew",
            notes="Takes the GPS tray's four holes: fit one or the other.",
        )
    ]
