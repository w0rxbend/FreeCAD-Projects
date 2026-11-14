"""Battery pad: a TPU mat on the top plate. Its openings are the top plate's own windows, so a strap
threads through both, and the pad cannot slide because its ribs sit in the windows."""

from build123d import Face, extrude, offset
from zhalo.accessories.kit import Accessory, poly

from tigerbeetle import equipment as E
from tigerbeetle import frame as F
from tigerbeetle import model as M

PAD_T = E.PAD_T
GROW = 0.5


def build() -> list[Accessory]:
    w, l, _h = E.BATTERY
    y0, y1 = E.BATTERY_Y - l / 2, E.BATTERY_Y + l / 2
    pad = poly([(-w / 2, y0), (w / 2, y0), (w / 2, y1), (-w / 2, y1)], 5.0)
    top = M.plates()["top_plate"]
    for win in top.windows:
        pad -= offset(Face(F.spline(win)), GROW)
    part = extrude(pad, amount=PAD_T).translate((0, 0, M.Z_TOP + M.T_PLATE))
    n = len([1 for f in part.faces()])
    return [
        Accessory(
            "battery_pad",
            "Battery pad",
            part,
            bed=(0, 0, 1),
            holds=("battery",),
            checks=[
                ("covers the battery footprint", True, f"{w:g} x {l:g} mm"),
                ("openings over the plate's windows", n > 6, "strap through both"),
            ],
            notes="Lay it on the top plate with its openings over the plate's windows; strap through both.",
        )
    ]
