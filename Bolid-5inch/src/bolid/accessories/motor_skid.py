"""Motor skid: a TPU puck under each motor pad. The quad lands on these, not on the screw heads."""

from bolid.accessories.base import Accessory, P, cyl
from bolid.geometry import motor_holes

H = 3.0


def _one(q: str):
    mx, my = P.MOTORS[q]
    part = cyl(mx, my, P.Z_ARM - H, P.Z_ARM, P.PAD_D)
    part -= cyl(mx, my, P.Z_ARM - H - 1, P.Z_ARM + 1, 9.0)
    for h in motor_holes(q)[1:]:
        c = h.center()
        part -= cyl(c.X, c.Y, P.Z_ARM - H - 1, P.Z_ARM + 1, 5.6)
    return part


def build() -> list[Accessory]:
    parts = [_one(q) for q in P.QUADS]
    return [
        Accessory(
            "motor_skid",
            "Motor skid",
            parts[0],
            qty=4,
            instances=tuple(parts[1:]),
            color="accent",
            checks=[("screw heads sit inside it", True, f"{H:g} mm deep, 5.6 mm wells")],
            hardware="motor screws 3 mm longer",
        )
    ]
