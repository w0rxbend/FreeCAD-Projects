"""Battery pad: a TPU mat with four pegs that drop into the top plate's slots."""

from zhalo import equipment as E
from zhalo.accessories.kit import Accessory, P, cylinder, face, poly, prism

from sfera import profiles

PAD_T = E.PAD_T
PEG_D, PEG_H = 4.6, 1.8  # the plate's slots are 6 mm wide
PEGS = [c for c in profiles.PILLS if abs(c[1]) < 20.0]
SLOT_GROW = 0.6
Z0 = P.Z_ROOF


def build() -> list[Accessory]:
    w, l = E.BATTERY_SIZE[0], E.BATTERY_SIZE[1]
    y0, y1 = E.BATTERY_Y - l / 2, E.BATTERY_Y + l / 2
    pad = prism(poly([(-w / 2, y0), (w / 2, y0), (w / 2, y1), (-w / 2, y1)], 6.0), Z0, Z0 + PAD_T)
    for c in profiles.PILLS:
        if c not in PEGS:
            pad -= prism(face(profiles.pill(c)), Z0 - 1, Z0 + PAD_T + 1)
    for (x, y), sw, sl in profiles.STRAP_SLOTS:
        a, b = sw / 2 + SLOT_GROW, sl / 2 + SLOT_GROW
        pad -= prism(
            poly([(x - a, y - b), (x + a, y - b), (x + a, y + b), (x - a, y + b)], a - 0.05), Z0 - 1, Z0 + PAD_T + 1
        )
    for xy in PEGS:
        pad += cylinder(*xy, Z0 - PEG_H, Z0 + 0.01, PEG_D)
    own = [
        ("covers the battery footprint", True, f"{w:.0f} x {l:.0f} mm"),
        ("pegs sit in the plate's slots", len(PEGS) == 4, f"{len(PEGS)} pegs"),
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
