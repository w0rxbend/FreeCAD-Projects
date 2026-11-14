"""Battery pad: a TPU mat with four pegs that drop into the top plate's slots.

The strap passes through four slots that line up with the plate's.
"""

from zhalo import equipment as E
from zhalo.accessories.kit import Accessory, P, cylinder, face, poly, prism

from zvir import profiles

PAD_T = E.PAD_T
PEG_D, PEG_H = 4.6, 1.8  # the plate's slots are 6 mm wide
PEG_ROWS = (-11.0, 11.0)
SLOT_GROW = 0.6
Z0 = P.Z_ROOF


def build() -> list[Accessory]:
    w, l = E.BATTERY_SIZE[0], E.BATTERY_SIZE[1]
    y0, y1 = E.BATTERY_Y - l / 2, E.BATTERY_Y + l / 2
    pad = prism(poly([(-w / 2, y0), (w / 2, y0), (w / 2, y1), (-w / 2, y1)], 6.0), Z0, Z0 + PAD_T)
    rows = [y for y in profiles.PILL_ROWS if y0 + 13.0 <= y <= y1 - 13.0 and y not in PEG_ROWS]
    for y in rows:
        for sx in (1, -1):
            pad -= prism(face(profiles.pill((sx * profiles.PILL_X, y))), Z0 - 1, Z0 + PAD_T + 1)
    for (x, y), sw, sl in profiles.STRAP_SLOTS:
        a, b = sw / 2 + SLOT_GROW, sl / 2 + SLOT_GROW
        pad -= prism(
            poly([(x - a, y - b), (x + a, y - b), (x + a, y + b), (x - a, y + b)], a - 0.05), Z0 - 1, Z0 + PAD_T + 1
        )
    pegs = [(sx * profiles.PILL_X, y) for y in PEG_ROWS for sx in (1, -1)]
    for xy in pegs:
        pad += cylinder(*xy, Z0 - PEG_H, Z0 + 0.01, PEG_D)
    own = [
        ("covers the battery footprint", True, f"{w:.0f} x {l:.0f} mm"),
        ("pegs sit in the plate's slots", all(y in profiles.PILL_ROWS for y in PEG_ROWS), f"{len(pegs)} pegs"),
    ]
    return [
        Accessory(
            "battery_pad",
            "Battery pad",
            pad,
            bed=(0, 0, 1),
            holds=("battery",),
            checks=own,
            notes="Print it top side down; the four pegs drop into the plate's slots. Strap through the four slots.",
        )
    ]
