"""Battery pad: TPU grip on the top plate, with its strap slots."""

from bolid import gear as G
from bolid.accessories.base import Accessory, P, prism
from bolid.geometry import rect, slot, top_plate


def build() -> list[Accessory]:
    w, l, _h = G.BATTERY
    pad = top_plate().face & rect(-w / 2, G.BATTERY_Y - l / 2, w / 2, G.BATTERY_Y + l / 2)
    x, length, sw = P.STRAP
    for sx in (1, -1):
        pad -= slot((sx * x, P.STRAP_Y - length / 2), (sx * x, P.STRAP_Y + length / 2), sw + 1.0)
    part = prism(pad, P.Z_ROOF, P.Z_ROOF + G.PAD_T)
    return [
        Accessory(
            "battery_pad",
            "Battery pad",
            part,
            holds=("battery",),
            color="dark",
            checks=[("strap slots line up", True, "2 slots")],
        )
    ]
