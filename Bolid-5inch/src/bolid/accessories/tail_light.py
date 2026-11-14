"""Tail light: a clear bar in the engine cover's slot, lit from inside by a strip of LEDs. A flange
inside the wall holds it; the wing's pylon stands in a notch in it."""

from bolid.accessories.base import Accessory, box
from bolid.accessories.engine_cover import LIGHT, PYLON, outer_y, pylon_xy

FLANGE = 1.4


def build() -> list[Accessory]:
    hx, z0, z1 = LIGHT
    y_out, y_in = outer_y(hx + FLANGE)
    part = box(-hx + 0.15, y_out - 0.6, z0 + 0.15, hx - 0.15, y_in, z1 - 0.15)
    part += box(-hx - FLANGE, y_in, z0 - FLANGE, hx + FLANGE, y_in + 1.0, z1 + FLANGE)
    (px, py), (w, d) = pylon_xy(), PYLON
    assert py - d / 2 - 0.3 > y_in, "the pylon would cut into the light's bar"
    part -= box(px - w / 2 - 0.3, y_in + 0.01, z0 - 5, px + w / 2 + 0.3, py + d / 2 + 0.3, z1 + 5)  # the pylon's notch
    return [
        Accessory(
            "tail_light",
            "Tail light",
            part,
            bed=(0, 1, 0),
            material="clear PETG or clear TPU",
            color="light",
            bridges=80.0,
            notes=(
                "Print it on the flange's face (the notch bridges 13 mm). Push it into the slot from inside "
                "before the cover goes on; a 5 V LED strip behind it, red."
            ),
        )
    ]
