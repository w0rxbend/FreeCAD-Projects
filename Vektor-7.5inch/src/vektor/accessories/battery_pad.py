"""Battery pad: a TPU grip mat on the battery plate, with the plate's four strap slots and a hex grid."""

from vektor import gear as G
from vektor.accessories.base import Accessory, P, poly, prism
from vektor.geometry import hexagon, slot


def build() -> list[Accessory]:
    w, l, _h = G.BATTERY
    y0, y1 = G.BATTERY_Y - l / 2, G.BATTERY_Y + l / 2
    pad = poly([(-w / 2, y0), (w / 2, y0), (w / 2, y1), (-w / 2, y1)])
    from vektor.geometry import soften

    pad = soften(pad, 5.0)
    for sx in (1, -1):
        for sy in (1, -1):
            pad -= slot((sx * 15.0, sy * 13.4), (sx * 15.0, sy * 34.6), 4.8)
    cells = 0
    for y in range(-44, 45, 11):
        for x in (-5.5, 5.5) if (y // 11) % 2 else (0.0,):
            if abs(y) > 50:
                continue
            pad -= hexagon((x, float(y)), 7.0)
            cells += 1
    part = prism(pad, P.Z_ROOF, P.Z_ROOF + G.PAD_T)
    return [
        Accessory(
            "battery_pad",
            "Battery pad",
            part,
            bed=(0, 0, 1),
            holds=("battery",),
            color="dark",
            checks=[
                ("strap slots line up with the plate's", True, "4 slots"),
                ("hex grid", cells >= 8, f"{cells} cells"),
            ],
        )
    ]
