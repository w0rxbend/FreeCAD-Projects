"""Bumper: four TPU segments that close the rim of the base.

The base is two skins with an 8 mm gap between them, open all round. A segment covers that
gap between two fingers, takes the knocks a disc gets on its edge, and gives the rim a
chamfered nose instead of two sharp plates. It is an L in section: a flange under the base,
held by the two rim-standoff bolts it passes, and a wall up the outside.
"""

from build123d import Axis
from zhalo.accessories.kit import D_M3_FREE, FIT, Accessory, P, cylinder, poly

from sfera import profiles, sizing
from sfera.payload import spin

SPAN = 69.0  # degrees: from one finger's fillet to the next
FLANGE_T = 2.0
FLANGE_IN = 68.0  # the flange reaches in to this radius
NOSE_OUT = 84.75
TOP = P.Z_DECK - 0.1


def _segment():
    """The front segment, centred on the nose."""
    r0 = sizing.BODY_R + FIT + 0.05
    section = poly(
        [
            (FLANGE_IN, -FLANGE_T),
            (NOSE_OUT - 1.75, -FLANGE_T),
            (NOSE_OUT, 1.0),
            (NOSE_OUT, TOP - 3.0),
            (NOSE_OUT - 2.25, TOP),
            (r0, TOP),
            (r0, 0.0),
            (FLANGE_IN, 0.0),
        ]
    )
    part = spin(section, 90.0 - SPAN / 2, 90.0 + SPAN / 2)
    for xy in P.pair(profiles.NOSE):
        part -= cylinder(*xy, -FLANGE_T - 1, 1, D_M3_FREE)
    return part


def build() -> list[Accessory]:
    front = _segment()
    gap = (P.Z_ARM, P.Z_MID)
    own = [
        (
            "covers the open edge between the skins",
            TOP >= gap[1] and -FLANGE_T <= gap[0],
            f"wall Z {-FLANGE_T:g} to {TOP:g}",
        ),
        ("stays below the propellers", TOP < P.PROP_Z[0], f"top at Z {TOP:g}, blades from Z {P.PROP_Z[0]:g}"),
    ]
    return [
        Accessory(
            "bumper",
            "Rim bumper",
            front,
            qty=4,
            checks=own,
            instances=tuple(front.rotate(Axis.Z, 90.0 * k) for k in (1, 2, 3)),
            color="accent",
            hardware="uses the two rim-standoff bolts it covers (M3x18)",
            notes="Print it flange down. The four segments are the same; each goes between two fingers of the base.",
        )
    ]
