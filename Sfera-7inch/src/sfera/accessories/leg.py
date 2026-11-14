"""Legs: four TPU struts, one under each finger of the base.

They lift the base 60 mm off the ground, so a 45 mm load bolted under it lands on the legs
and not on itself. Each hangs on the two outer bolts of an arm; the bolts come down from the
deck into nylocs that slide into the leg from the side. A leg stands entirely under its arm,
so it adds nothing to what the propeller above it has to blow past.
"""

from build123d import Axis
from zhalo.accessories.kit import D_M3_FREE, Accessory, P, box, cylinder, poly, prism_y

from sfera import payload, sizing

WIDTH = 2 * sizing.LEG_R  # as wide as the finger above it
HEIGHT = -payload.FEET_Z
NUT = (5.7, 4.3)  # nyloc: across flats, height of its slot
ROOF = 1.4  # TPU between a nut and the base
BOLTS = (sizing.LEG_BOLT_U, sizing.ARM_BOLT_U[1])
S_R = (P.S[0] ** 2 + P.S[1] ** 2) ** 0.5  # the stack bolt is this far out along the diagonal
# side view along the diagonal, as (distance from the centre, z)
OUTLINE = [
    (78.0, 0.0),
    (78.0, -9.0),
    (86.0, -11.0),
    (93.0, -30.0),
    (101.0, -HEIGHT),
    (110.0, -HEIGHT),
    (110.0, -HEIGHT + 6.0),
    (107.5, -30.0),
    (105.4, -9.0),
    (104.6, 0.0),
]


def _leg():
    """The leg under the +X axis; `build` turns it onto a diagonal."""
    part = prism_y(poly(OUTLINE, 1.0), -WIDTH / 2, WIDTH / 2)
    af, h = NUT
    for u in BOLTS:
        r = S_R + u
        part -= cylinder(r, 0.0, -ROOF - h - 3.0, 1.0, D_M3_FREE)
        part -= box(r - af / 2, -af / 2, -ROOF - h, r + af / 2, WIDTH / 2 + 1, -ROOF)
    return part


def build() -> list[Accessory]:
    legs = [_leg().rotate(Axis.Z, 45.0 + 90.0 * k) for k in range(4)]
    load = payload.CARGO_Z - payload.CRATE[2]
    foot = (OUTLINE[4][0] + OUTLINE[5][0]) / 2
    own = [
        (
            "a 45 mm load lands on the legs, not on itself",
            payload.FEET_Z <= load - 5.0,
            f"feet Z {payload.FEET_Z:g}, load to Z {load:g}",
        ),
        (
            "stands under its arm",
            WIDTH <= 2 * P.arm_half_width(BOLTS[0]),
            f"{WIDTH:g} mm wide under a {2 * P.arm_half_width(BOLTS[0]):.1f} mm arm",
        ),
        ("stance", foot > sizing.BODY_R, f"feet on a {2 * foot:.0f} mm circle, {foot * 2**0.5:.0f} mm apart"),
    ]
    return [
        Accessory(
            "leg",
            "Landing leg",
            legs[0],
            bed=(2**-0.5, -(2**-0.5), 0.0),
            qty=4,
            checks=own,
            instances=tuple(legs[1:]),
            ceilings=10.0,
            overhang=24.0,
            hardware="2x M3x20 + nyloc: the two outer arm bolts, head on the deck, nut in the leg",
            notes=(
                "Print it lying on the side without the nut slots, 4 perimeters, 40 % infill or more. Slide the two "
                "nylocs in from the side, then run the arm bolts down into them from the deck."
            ),
        )
    ]
