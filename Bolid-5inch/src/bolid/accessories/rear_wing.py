"""Rear wing: the antenna mast, shaped as a supercar's wing. A pylon stands on the bottom plate's tail,
comes up through the engine cover and carry an inverted aerofoil above the props' band. Its tips hold the
video transmitter's two antennas, leaning out 45 deg each (90 deg apart); the middle holds the receiver's.
The pylon is bolted from below, and presses the cover down."""

from build123d import Axis

from bolid.accessories.base import Accessory, P, box, cyl, poly, prism_x
from bolid.accessories.engine_cover import PYLON, ROOF, pylon_xy
from bolid.geometry import soften

TOP = 47.0  # the wing's flat upper face
CHORD = (-94.0, -72.0)
SPAN = 25.0  # half
SHAPE = [(0.00, 0.0), (0.10, -3.2), (0.30, -4.6), (0.60, -4.0), (0.85, -2.6), (1.00, -1.6)]  # under the flat top
TUBE = (7.0, 4.2, 12.0)
LEAN = 45.0
RX = (0.0, -76.0)


def aerofoil():
    y0, y1 = CHORD
    c = y1 - y0
    under = [(y1 - f * c, TOP + dz) for f, dz in SHAPE]  # nose at the front (y1), dropping under the top
    return soften(poly([(y0, TOP)] + under), 0.6)


def _tube(sx: int, bore: bool):
    od, d, length = TUBE
    t = cyl(0, 0, -length if not bore else -length - 2, 3.0 if bore else 0.0, d if bore else od)
    t = t.rotate(Axis.Y, sx * LEAN)
    return t.translate((sx * (SPAN - 7.0), (CHORD[0] + CHORD[1]) / 2, TOP))


def build() -> list[Accessory]:
    part = prism_x(aerofoil(), -SPAN, SPAN)
    for sx in (1, -1):  # end plates, under the top face
        plate = soften(
            poly(
                [(CHORD[0] - 1.0, TOP), (CHORD[1] + 0.5, TOP), (CHORD[1] - 3.0, TOP - 9.0), (CHORD[0] + 3.0, TOP - 9.0)]
            ),
            1.0,
        )
        part += prism_x(plate, sx * SPAN - (1.6 if sx > 0 else 0), sx * SPAN + (0 if sx > 0 else 1.6))
        part += _tube(sx, False)
    w, d = PYLON
    px, py = pylon_xy()
    part += box(px - w / 2, py - d / 2, P.Z_ARM + 0.1, px + w / 2, py + d / 2, TOP - 1.0)
    for x, y in P.WING_FEET:
        part -= cyl(x, y, P.Z_ARM, P.Z_ARM + 12.0, 2.6)  # M3, self-tapping into the pylon
    part += cyl(*RX, TOP - 10.0, TOP, 7.0)
    for sx in (1, -1):
        part -= _tube(sx, True)
    part -= cyl(*RX, TOP - 12.0, TOP + 1, 4.2)
    part &= box(-60, -120, -10, 60, 0, TOP)  # the flat top: what it prints on
    return [
        Accessory(
            "rear_wing",
            "Rear wing (VTX antennas x2, RX antenna)",
            part,
            bed=(0, 0, 1),
            color="accent",
            bridges=30.0,
            overhang=60.0,
            checks=[
                ("two VTX antennas 90 deg apart", abs(2 * LEAN - 90) < 1e-9, f"each {LEAN:g} deg out"),
                ("receiver antenna in the middle", True, f"vertical at Y {RX[1]:g}"),
                (
                    "wing above the props' band",
                    TOP - 9.0 > P.PROP_Z[1],
                    f"lowest Z {TOP - 9.0:g}, blades to {P.PROP_Z[1]:g}",
                ),
                ("pylon through the cover's roof", TOP - 1.0 > ROOF, "it also presses the cover down"),
            ],
            hardware="2x M3x10 from under the bottom plate",
            notes="Print it upside down, on the wing's flat top. Feed the antennas' leads up beside the pylon.",
        )
    ]
