"""Battery pad: a TPU honeycomb mat between the top plate and the pack.

Two pegs on its underside drop into chevron windows of the top plate, so it cannot creep
under the strap; the strap itself passes through four slots that line up with the plate's.
"""

from zhalo import equipment as E
from zhalo import frame as F
from zhalo.accessories.kit import Accessory, P, cylinder, hexagon, honeycomb, poly, prism

PAD_T = E.PAD_T
SIZE = (E.BATTERY_SIZE[0], E.BATTERY_SIZE[1])  # width, length: the footprint of the pack
CENTER_Y = E.BATTERY_Y
BORDER = 3.0
HEX_AF, HEX_RIB = 5.0, 2.0
PEG_D, PEG_H = 3.3, 1.8  # the chevron slot is 3.8 mm wide square across
PEG_CHEVRONS = (-21.0, 12.0)  # which chevrons (by their Y) take a peg
SLOT_GROW = 0.6  # strap slots are this much larger all round than the plate's
Z0 = P.Z_ROOF


def _peg_xy(chevron_y: float) -> tuple[float, float]:
    return 0.0, chevron_y + 2.5  # the middle of the V's point (sweep 5: the apex sits 2.5 ahead)


def build() -> list[Accessory]:
    w, l = SIZE
    y0, y1 = CENTER_Y - l / 2, CENTER_Y + l / 2
    pad = prism(poly([(-w / 2, y0), (w / 2, y0), (w / 2, y1), (-w / 2, y1)], 5.0), Z0, Z0 + PAD_T)
    slots = [((x, y), sw + 2 * SLOT_GROW, sl + 2 * SLOT_GROW) for (x, y), sw, sl in F.STRAP_SLOTS]
    pegs = [_peg_xy(y) for y in PEG_CHEVRONS]
    half_w = HEX_AF / 3**0.5
    cells = []
    for x, y in honeycomb(
        -w / 2 + BORDER, w / 2 - BORDER, y0 + BORDER, y1 - BORDER, HEX_AF, HEX_RIB, origin=(0.0, CENTER_Y)
    ):
        near_slot = any(
            abs(x - sx) < sw / 2 + half_w + 1.4 and abs(y - sy) < sl / 2 + HEX_AF / 2 + 1.4
            for (sx, sy), sw, sl in slots
        )
        near_peg = any((x - px) ** 2 + (y - py) ** 2 < (half_w + PEG_D / 2 + 1.6) ** 2 for px, py in pegs)
        if not near_slot and not near_peg:
            cells.append((x, y))
    for c in cells:
        pad -= prism(hexagon(c, HEX_AF), Z0 - 1, Z0 + PAD_T + 1)
    for (x, y), sw, sl in slots:
        pad -= prism(
            poly(
                [
                    (x - sw / 2, y - sl / 2),
                    (x + sw / 2, y - sl / 2),
                    (x + sw / 2, y + sl / 2),
                    (x - sw / 2, y + sl / 2),
                ],
                sw / 2 - 0.05,
            ),
            Z0 - 1,
            Z0 + PAD_T + 1,
        )
    for xy in pegs:
        pad += cylinder(*xy, Z0 - PEG_H, Z0 + 0.01, PEG_D)
    own = [
        (
            "covers the battery footprint",
            w >= E.BATTERY_SIZE[0] and l >= E.BATTERY_SIZE[1],
            f"{w:.0f} x {l:.0f} mm pad, {E.BATTERY_SIZE[0]:.0f} x {E.BATTERY_SIZE[1]:.0f} mm pack",
        ),
        ("honeycomb cells", len(cells) >= 20, f"{len(cells)} cells of {HEX_AF} mm"),
    ]
    return [
        Accessory(
            "battery_pad",
            "Battery pad",
            pad,
            bed=(0, 0, 1),
            holds=("battery",),
            checks=own,
            notes="Print it top side down; the two pegs drop into the chevron windows. Strap through the four slots.",
        )
    ]
