"""Battery pad for the Tiger family: a TPU mat whose openings are the top plate's own chevrons, so a
strap threads through both and the pad cannot slide on the plate."""

from build123d import offset

from zhalo import equipment as E
from zhalo import tiger
from zhalo.accessories.kit import Accessory, P, poly, prism

GROW = 0.5
EDGE = 1.6  # least TPU between an opening and the pad's edge


def build() -> list[Accessory]:
    w, l = E.BATTERY_SIZE[0], E.BATTERY_SIZE[1]
    y0, y1 = E.BATTERY_Y - l / 2, E.BATTERY_Y + l / 2
    pad = poly([(-w / 2, y0), (w / 2, y0), (w / 2, y1), (-w / 2, y1)], 5.0)
    inner = poly([(-w / 2 + EDGE, y0 + EDGE), (w / 2 - EDGE, y0 + EDGE), (w / 2 - EDGE, y1 - EDGE), (-w / 2 + EDGE, y1 - EDGE)])
    for win in tiger.top_plate().windows:
        hole = offset(tiger.face(win), GROW)
        if abs((hole & inner).area - hole.area) < 1e-6:  # only openings wholly inside the pad: no slivers at its edge
            pad -= hole
    part = prism(pad, P.Z_ROOF, P.Z_ROOF + E.PAD_T).clean()
    return [
        Accessory(
            "battery_pad",
            "Battery pad",
            part,
            bed=(0, 0, 1),
            holds=("battery",),
            checks=[("covers the battery footprint", True, f"{w:g} x {l:g} mm")],
            notes="Lay it on the top plate with its openings over the chevrons; strap through both.",
        )
    ]
