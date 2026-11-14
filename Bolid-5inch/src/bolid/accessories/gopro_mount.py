"""Action-camera mount on the top plate's nose, ahead of the battery."""

from bolid.accessories.base import D_HEAD, D_M3, Accessory, P, cyl, prism, prism_x
from bolid.geometry import disc, poly, soften

BASE_T, PRONG_T, PRONG_GAP, PIVOT_H, PRONG_R = 4.0, 3.0, 3.2, 10.0, 7.0


def build() -> list[Accessory]:
    holes = P.GOPRO_HOLES
    xs = [p[0] for p in holes]
    ys = [p[1] for p in holes]
    z0 = P.Z_ROOF
    base = soften(
        poly(
            [
                (min(xs) - 5, min(ys) - 4.5),
                (max(xs) + 5, min(ys) - 4.5),
                (max(xs) + 5, max(ys) + 4),
                (min(xs) - 5, max(ys) + 4),
            ]
        ),
        3.0,
    )
    part = prism(base, z0, z0 + BASE_T)
    yc = (min(ys) + max(ys)) / 2
    zp = z0 + BASE_T + PIVOT_H
    tab = poly(
        [
            (yc - PRONG_R - 1, z0 + BASE_T - 0.01),
            (yc + PRONG_R + 1, z0 + BASE_T - 0.01),
            (yc + PRONG_R, zp),
            (yc - PRONG_R, zp),
        ]
    ) + disc((yc, zp), 2 * PRONG_R)
    pitch = PRONG_T + PRONG_GAP
    for k in (-1, 0, 1):
        part += prism_x(tab, k * pitch - PRONG_T / 2, k * pitch + PRONG_T / 2)
    part -= prism_x(disc((yc, zp), 5.3), -2 * pitch, 2 * pitch)
    for p in holes:
        part -= cyl(*p, z0 - 1, z0 + BASE_T + 1, D_M3)
        part -= cyl(*p, z0 + BASE_T - 1.8, z0 + BASE_T + 1, D_HEAD)
    return [
        Accessory(
            "gopro_mount",
            "Action-camera mount",
            part,
            color="dark",
            bridges=110.0,
            overhang=30.0,
            hardware="4x M3x10 + nyloc, M5 thumbscrew",
        )
    ]
