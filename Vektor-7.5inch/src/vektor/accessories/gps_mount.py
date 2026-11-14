"""GPS tray on the nose of the battery plate, as far from the VTX antenna at the tail as the frame allows.
It uses the four accessory holes there (the action-camera mount takes the same holes)."""

from vektor import gear as G
from vektor.accessories.base import D_HEAD, D_M3, FIT, WALL, Accessory, P, box, cyl
from vektor.geometry import GOPRO_HOLES

FLOOR = 3.2
RECESS = 1.8


def build() -> list[Accessory]:
    w, l, h = G.GPS[0] + 2 * FIT, G.GPS[1] + 2 * FIT, G.GPS[2]
    yc = sum(p[1] for p in GOPRO_HOLES) / len(GOPRO_HOLES)
    z0 = P.Z_ROOF
    part = box(-w / 2 - WALL, yc - l / 2 - WALL, z0, w / 2 + WALL, yc + l / 2 + WALL, z0 + FLOOR + h)
    part -= box(-w / 2, yc - l / 2, z0 + FLOOR, w / 2, yc + l / 2, z0 + FLOOR + h + 1)
    part -= box(-4.5, yc + l / 2 - 1, z0 + FLOOR, 4.5, yc + l / 2 + WALL + 1, z0 + FLOOR + h + 1)  # lead
    for p in GOPRO_HOLES:
        part -= cyl(*p, z0 - 1, z0 + FLOOR + 1, D_M3)
        part -= cyl(*p, z0 + FLOOR - RECESS, z0 + FLOOR + 1, D_HEAD)
    front = G.BATTERY_Y + G.BATTERY[1] / 2
    return [
        Accessory(
            "gps_mount",
            "GPS tray",
            part,
            color="dark",
            checks=[
                (
                    "ahead of the battery",
                    yc - l / 2 - WALL >= front,
                    f"from Y {yc - l / 2 - WALL:.1f}, battery to Y {front:.1f}",
                ),
                ("far from the VTX antenna", True, "nose of the plate; the antenna is on the tail"),
            ],
            hardware="4x M3x8 into nylocs under the plate; foam tape under the module",
        )
    ]
