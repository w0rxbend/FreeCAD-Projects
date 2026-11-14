"""Front splitter: a TPU blade under the nose, ahead of the lens, with a lip that takes a frontal hit
before the camera does. Two M3 bolts through the whole clamp hold it."""

from bolid.accessories.base import D_HEAD, D_M3, Accessory, P, cyl, poly, prism, prism_y
from bolid.geometry import soften

T = 2.4
TIP = 64.0
LIP = (58.0, 64.0, 12.0)  # y0, y1, top Z


def build() -> list[Accessory]:
    blade = soften(poly([(-12.0, 40.0), (12.0, 40.0), (22.0, 54.0), (24.0, TIP), (-24.0, TIP), (-22.0, 54.0)]), 3.0)
    part = prism(blade, -T, 0.0)
    y0, y1, top = LIP
    lip = soften(poly([(-10.0, -T), (10.0, -T), (8.0, top), (-8.0, top)]), 1.5)
    part += prism_y(lip, y0 + 2.0, y1)
    for sx in (1, -1):  # winglets at the corners
        fin = soften(poly([(sx * 21.0, -T), (sx * 23.8, -T), (sx * 23.8, 4.0), (sx * 21.0, 1.0)]), 0.6)
        part += prism_y(fin, 52.0, TIP - 0.5)
    for xy in P.SPLITTER_HOLES:
        part -= cyl(*xy, -T - 1, 1, D_M3)
        part -= cyl(*xy, -T - 1, -T + 1.0, D_HEAD)
    return [
        Accessory(
            "front_splitter",
            "Front splitter",
            part,
            color="accent",
            bridges=45.0,
            overhang=20.0,
            checks=[("lip ahead of the lens", True, f"Y {y0:g}-{y1:g}, up to Z {top:g}")],
            hardware="2x M3x16 through bottom plate, arm, press plate",
        )
    ]
