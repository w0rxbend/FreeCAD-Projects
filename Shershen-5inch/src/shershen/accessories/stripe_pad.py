"""Battery pad cut with the same fishbone as the top plate under it.

Four pegs on its underside drop into four of the plate's fishbone windows, so it cannot
creep under the strap; the strap passes through four slots that line up with the plate's.
"""

from zhalo import equipment as E
from zhalo import frame as F
from zhalo.accessories.kit import Accessory, P, cylinder, poly, prism

from shershen import profiles

PAD_T = E.PAD_T
SIZE = (E.BATTERY_SIZE[0], E.BATTERY_SIZE[1])
CENTER_Y = E.BATTERY_Y
PEG_D, PEG_H = 3.3, 1.8
PEG_ROWS = (-21.0, 12.0)  # the fishbone rows that take pegs
PEG_AT = (4.96, -1.78)  # centre of the circle that fits inside a fishbone triangle, from the row's station
SLOT_GROW = 0.6
EDGE = 3.0
Z0 = P.Z_ROOF


def _triangle(y: float, sx: int) -> list[tuple[float, float]]:
    s = profiles.SPINE
    pts = [(s, y + 4.5), (s + 7.0, y - 3.5), (s, y - 4.5)]
    return pts if sx > 0 else [(-x, yy) for x, yy in reversed(pts)]


def build() -> list[Accessory]:
    w, l = SIZE
    y0, y1 = CENTER_Y - l / 2, CENTER_Y + l / 2
    pad = prism(poly([(-w / 2, y0), (w / 2, y0), (w / 2, y1), (-w / 2, y1)], 5.0), Z0, Z0 + PAD_T)
    rows = [y for y in profiles.FISH_Y if y0 + EDGE + 4.5 <= y <= y1 - EDGE - 4.5 and y not in PEG_ROWS]
    for y in rows:
        for sx in (1, -1):
            pad -= prism(poly(_triangle(y, sx), 1.0), Z0 - 1, Z0 + PAD_T + 1)
    for (x, y), sw, sl in F.STRAP_SLOTS:
        a, b = sw / 2 + SLOT_GROW, sl / 2 + SLOT_GROW
        pad -= prism(
            poly([(x - a, y - b), (x + a, y - b), (x + a, y + b), (x - a, y + b)], a - 0.05), Z0 - 1, Z0 + PAD_T + 1
        )
    pegs = [(sx * PEG_AT[0], y + PEG_AT[1]) for y in PEG_ROWS for sx in (1, -1)]
    for xy in pegs:
        pad += cylinder(*xy, Z0 - PEG_H, Z0 + 0.01, PEG_D)
    own = [
        ("covers the battery footprint", w >= E.BATTERY_SIZE[0] and l >= E.BATTERY_SIZE[1], f"{w:.0f} x {l:.0f} mm"),
        ("fishbone rows", len(rows) >= 4, f"{len(rows)} rows cut, {len(pegs)} pegs"),
    ]
    return [
        Accessory(
            "stripe_pad",
            "Battery pad",
            pad,
            bed=(0, 0, 1),
            holds=("battery",),
            checks=own,
            notes="Print it top side down; the four pegs drop into the fishbone windows. Strap through the four slots.",
        )
    ]
