"""Engine cover: the tail over the video transmitter, like a supercar's rear deck. Louvres over the
transmitter's heat sink, a slot for the tail light, holes the wing's pylons come up through. Two M2
screws from under the bottom plate hold it; nothing shows from above."""

from build123d import Kind, offset

from bolid import gear as G
from bolid.accessories.base import Accessory, P, box, cyl, prism, prism_y
from bolid.geometry import body_outline, rect, slot

Z0, ROOF = P.Z_ARM + 0.2, 20.0
WALL, T_ROOF = 1.8, 1.6
FRONT = P.TAIL_Y - 0.5
LIGHT = (9.0, 9.0, 12.0)  # half width, z0, z1 of the tail light's slot
PYLON = (12.0, 5.4)


def region():
    return body_outline() & rect(-40, -120, 40, FRONT)


def pylon_xy() -> tuple[float, float]:
    xs = [p[0] for p in P.WING_FEET]
    return sum(xs) / len(xs), P.WING_FEET[0][1]


def outer_y(half: float) -> tuple[float, float]:
    """Across |x| < half: the rear wall's outer face on the centre line, and the most forward point of
    its inner face (the light's flange starts there)."""
    out = (offset(region(), -0.2, kind=Kind.ARC) & rect(-0.05, -120, 0.05, FRONT)).bounding_box().min.Y
    ring = offset(region(), -0.2, kind=Kind.ARC) - offset(region(), -0.2 - WALL, kind=Kind.ARC)
    wall = ring & rect(-half, -120, half, -80.0)
    return out, wall.bounding_box().max.Y


def build() -> list[Accessory]:
    outer = offset(region(), -0.2, kind=Kind.ARC)
    inner = offset(region(), -0.2 - WALL, kind=Kind.ARC)
    part = prism(outer - inner, Z0, ROOF) + prism(outer, ROOF - T_ROOF, ROOF)
    part -= box(-30, FRONT - 3.0, Z0 - 1, 30, FRONT + 1, ROOF - T_ROOF)  # open to the front
    for xy in P.COVER_BOLTS:
        part += cyl(*xy, Z0, ROOF - T_ROOF + 0.01, 4.4)
        part -= cyl(*xy, Z0 - 1, ROOF - T_ROOF - 2.0, 1.8)
    for k in range(5):  # louvres over the heat sink
        y = P.VTX_Y + 10.0 - 5.0 * k
        part -= prism(slot((-9.0, y), (9.0, y), 2.4), ROOF - T_ROOF - 1, ROOF + 1)
    w, d = PYLON
    x, y = pylon_xy()
    part -= box(x - w / 2 - 0.5, y - d / 2 - 0.5, ROOF - T_ROOF - 1, x + w / 2 + 0.5, y + d / 2 + 0.5, ROOF + 1)
    hx, z0, z1 = LIGHT
    part -= prism_y(rect(-hx, z0, hx, z1), -95.0, -80.0)
    vtx = G.build()["vtx"][0].bounding_box()
    return [
        Accessory(
            "engine_cover",
            "Engine cover",
            part,
            bed=(0, 0, 1),
            color="shell",
            bridges=60.0,
            overhang=20.0,
            checks=[
                (
                    "air over the heat sink",
                    ROOF - T_ROOF - vtx.max.Z >= 3.0,
                    f"{ROOF - T_ROOF - vtx.max.Z:.1f} mm under the louvres",
                )
            ],
            hardware="2x M2x8 self-tapping, from under the bottom plate",
            notes="Print it upside down, on its roof.",
        )
    ]
