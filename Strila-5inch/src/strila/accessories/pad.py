"""Battery pad: a TPU mat with four pegs that drop into the top plate's slots.

The strap passes through four slots that line up with the plate's.
"""

from zhalo import equipment as E
from zhalo import frame as F
from zhalo.accessories.kit import Accessory, P, cylinder, face, poly, prism

from strila import profiles

PAD_T = E.PAD_T
SIZE = (E.BATTERY_SIZE[0], E.BATTERY_SIZE[1])
CENTER_Y = E.BATTERY_Y
PEG_D, PEG_H = 3.3, 1.8  # the plate's slots are 4 mm wide
PEG_ROWS = (-11.0, 11.0)
PILL_X = 6.5
SLOT_GROW = 0.6
Z0 = P.Z_ROOF


def build() -> list[Accessory]:
    w, l = SIZE
    y0, y1 = CENTER_Y - l / 2, CENTER_Y + l / 2
    pad = prism(poly([(-w / 2, y0), (w / 2, y0), (w / 2, y1), (-w / 2, y1)], 5.0), Z0, Z0 + PAD_T)
    rows = [y for y in profiles.PILL_ROWS if y0 + 10.5 <= y <= y1 - 10.5 and y not in PEG_ROWS]
    for y in rows:
        for sx in (1, -1):
            pad -= prism(face(profiles.pill((sx * PILL_X, y), 15.0)), Z0 - 1, Z0 + PAD_T + 1)
    for (x, y), sw, sl in F.STRAP_SLOTS:
        a, b = sw / 2 + SLOT_GROW, sl / 2 + SLOT_GROW
        pad -= prism(
            poly([(x - a, y - b), (x + a, y - b), (x + a, y + b), (x - a, y + b)], a - 0.05), Z0 - 1, Z0 + PAD_T + 1
        )
    pegs = [(sx * PILL_X, y) for y in PEG_ROWS for sx in (1, -1)]
    for xy in pegs:
        pad += cylinder(*xy, Z0 - PEG_H, Z0 + 0.01, PEG_D)
    own = [
        ("covers the battery footprint", w >= E.BATTERY_SIZE[0] and l >= E.BATTERY_SIZE[1], f"{w:.0f} x {l:.0f} mm"),
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
