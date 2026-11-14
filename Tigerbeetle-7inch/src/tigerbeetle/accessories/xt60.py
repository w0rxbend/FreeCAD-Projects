"""XT60 holder: the battery plug at the tail, between the two rear standoffs, on the bottom plate.

Two sleeves slide over the rear standoffs before the top plate goes on; between them an open channel
holds the XT60 socket with its mouth to the rear, under a zip tie. The battery lead plugs in behind
the quad, and nothing hangs over the props.
"""

from zhalo.accessories.kit import FIT, SLEEVE_BORE, SLEEVE_OD, WALL, Accessory, box, cylinder

from tigerbeetle import frame as F
from tigerbeetle import model as M

XT60 = (15.8, 16.0, 8.3)  # width, length, height of the socket's body lying flat
FLOOR_T = 1.6
Z0 = M.Z_ARM + 0.15  # stands on the bottom plate
TOP = 22.0


def build() -> list[Accessory]:
    s = F.standoffs()["standoff_rear_right"]
    sx, sy = s[0], s[1]
    w, l, h = XT60[0] + 2 * FIT, XT60[1] + FIT, XT60[2] + 2 * FIT
    y1 = sy + 6.0  # the pocket runs from here back to the tail
    y0 = y1 - l
    x_out = w / 2 + WALL
    z_top = Z0 + FLOOR_T + h - 1.5  # the walls stop below the socket's top: a zip tie goes over it
    part = box(-x_out, y0, Z0, x_out, y1, z_top)
    part += box(-sx, sy - 3.0, Z0, sx, sy + 3.0, Z0 + FLOOR_T + 2.0)  # a beam from sleeve to sleeve
    for x in (sx, -sx):
        part += cylinder(x, sy, Z0, TOP, SLEEVE_OD)
    part -= box(-w / 2, y0 - 1, Z0 + FLOOR_T, w / 2, y1 + 1, z_top + 1)  # an open channel: the socket drops in
    for x in (sx, -sx):
        part -= cylinder(x, sy, Z0 - 1, TOP + 1, SLEEVE_BORE)
    tail = min(p[1] for p in M.plates()["bottom_plate"].outline)
    own = [
        ("pocket fits an XT60", True, f"{w:.1f} x {h:.1f} mm opening, {l:.1f} mm deep"),
        ("the plug's mouth is at the tail", y0 <= tail + 6.0, f"pocket from Y {y0:.1f}, plate ends at Y {tail:.1f}"),
    ]
    return [
        Accessory(
            "xt60_holder",
            "XT60 holder",
            part,
            checks=own,
            color="accent",
            ceilings=12.0,
            overhang=20.0,
            hardware="a zip tie round the socket and the holder",
            notes="Slide it over the two rear standoffs before the top plate goes on; the socket's mouth faces back.",
        )
    ]
