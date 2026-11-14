"""Hull: four TPU panels that close the body between the deck and the top plate.

The body is a drum; these make it a barrel. Seen from the side a panel is three facets: it
leaves the deck leaning 40 deg outwards, runs upright for 20 mm, and leans back in under the
top plate. That does three things: nothing square meets the air from any side, the panel is
a folded shell (stiff at 1.8 mm) rather than a flat sheet, and it still prints standing up
without support, because 40 deg is as far as it ever leans.

A panel runs from the middle of a side to the camera opening at the nose (or the lead opening
at the tail) and snaps onto its two rim standoffs from outside. Two mirrored prints, two of
each. In each: three gills over the side bay, a gate at the foot where the motor wires come
in over the arm, a groove round the equator and the outline of a hatch.
"""

from math import cos, radians, tan

from build123d import Axis
from zhalo.accessories.kit import CLIP_BORE, CLIP_WALL, SEAT, Accessory, P, c_ring, mirror_x, poly, prism

from sfera import sizing
from sfera.payload import spin

SKIN = 1.8
R0 = 79.0  # outer radius of the shell where it meets the deck and the top plate
LEAN = 40.0  # how far from upright the lower and the upper facet lean
BULGE = 6.0
Z0 = P.Z_DECK + SEAT
Z1 = P.Z_TOP - SEAT
ZM = (Z0 + Z1) / 2
RISE = BULGE / tan(radians(LEAN))  # height of a leaning facet
R_MAX = R0 + BULGE  # 85: the widest point of the body
SEAM = 0.25  # the panel starts this far (degrees) from the middle of the side
END = 90.0 - sizing.PAIR_DEG  # and ends on the nose standoff
STANDOFFS = (sizing.PAIR_DEG, END)  # where its two rim standoffs are, degrees from the side axis
PUSH = 225.0  # the rings open this way: the panel goes on along its own diagonal
WEB = 1.6  # degrees: a rib from each ring out to the shell
GILLS = (22.0, 26.5, 31.0)  # degrees
GILL_DEG = 2.2
GILL_Z = (Z0 + 9.0, Z1 - 9.0)
GATE = (10.0, 5.0)  # the motor-wire gate at the foot, on the diagonal: degrees wide, mm high
GROOVE = 0.7
HATCH = (53.0, 68.0, 6.5)  # a panel line: from, to (degrees), half-height


def _outer(inset: float = 0.0) -> list[tuple[float, float]]:
    """The three facets from the deck up, moved inwards by `inset`."""
    k = tan(radians(LEAN / 2))
    foot = R0 - inset / cos(radians(LEAN))
    return [
        (foot, Z0),
        (R_MAX - inset, Z0 + RISE + inset * k),
        (R_MAX - inset, Z1 - RISE - inset * k),
        (foot, Z1),
    ]


def _between(a: float, b: float, z0: float | None = None, z1: float | None = None):
    """Side view of the layer of the hull between `a` and `b` mm under its outer surface (b = None: all of it
    out from the standoff circle), optionally only between two heights."""
    inner = _outer(b)[::-1] if b is not None else [(77.0, Z1), (77.0, Z0)]
    shape = poly(_outer(a) + inner)
    if z0 is not None:
        shape &= poly([(60.0, z0), (100.0, z0), (100.0, z1), (60.0, z1)])
    return shape


def _slab(z0: float, z1: float):
    return poly([(60.0, z0), (100.0, z0), (100.0, z1), (60.0, z1)])


def _panel():
    """The front-right panel. Every cutter is itself turned about the body's axis, like the shell."""
    cuts = [spin(_slab(*GILL_Z), a - GILL_DEG / 2, a + GILL_DEG / 2) for a in GILLS]
    cuts.append(spin(_slab(Z0 - 2.0, Z0 + GATE[1]), 45.0 - GATE[0] / 2, 45.0 + GATE[0] / 2))
    groove = poly([(R_MAX + 0.3, ZM - GROOVE - 0.3), (R_MAX + 0.3, ZM + GROOVE + 0.3), (R_MAX - GROOVE, ZM)])
    cuts.append(spin(groove, SEAM - 1.0, END + 1.0))
    a0, a1, half = HATCH
    line = _between(-0.5, GROOVE - 0.1, ZM - half, ZM + half)
    cuts += [spin(line, a, a + 0.9) for a in (a0, a1 - 0.9)]
    for z in (ZM - half, ZM + half):
        v = poly([(R_MAX + 0.3, z - GROOVE - 0.3), (R_MAX + 0.3, z + GROOVE + 0.3), (R_MAX - GROOVE, z)])
        cuts.append(spin(v, a0, a1))
    part = spin(_between(0.0, SKIN), SEAM, END) - cuts
    centres = [sizing.polar(sizing.RING_R, a) for a in STANDOFFS]
    rib = _between(0.3, None)
    adds = [spin(rib, SEAM, SEAM + WEB)]
    adds += [spin(rib, a - WEB / 2, a + WEB / 2) for a in STANDOFFS]
    adds += [prism(c_ring(c, PUSH), Z0, Z1) for c in centres]
    part = part + adds
    assert len(part.solids()) == 1 and part.is_valid, "hull panel did not come out as one valid solid"
    return part


def build() -> list[Accessory]:
    right = _panel()
    left = mirror_x(right)
    clear = sizing.MOTOR_R - sizing.PROP_D / 2 - R_MAX
    inside = R0 - SKIN / cos(radians(LEAN)) - (sizing.RING_R + CLIP_BORE / 2)
    arc = radians(GILL_DEG) * R_MAX
    own = [
        ("never leans further than it can print", LEAN <= 45.0, f"{LEAN:g} deg from upright, top and bottom"),
        ("blade tips pass the widest point of the hull", clear >= P.PROP_MARGIN, f"{clear:.1f} mm at R {R_MAX:.1f}"),
        ("shell passes outside the standoffs", inside >= 0.05, f"{inside:.2f} mm"),
        ("gills", len(GILLS) == 3, f"{len(GILLS)} slots {arc:.1f} x {GILL_Z[1] - GILL_Z[0]:.0f} mm over the side bay"),
    ]
    notes = (
        "Push it on along the arm: both rings open towards the middle of the quad. Print it standing on its "
        "lower edge, as it sits on the deck. The gate at the foot is where the motor wires come in over the arm."
    )
    common = {
        "color": "hull",
        "qty": 2,
        "notes": notes,
        # flat tops: the three gills, the gate's lintel, the upper line of the hatch
        "ceilings": 3 * arc * SKIN + radians(GATE[0]) * R0 * SKIN * 1.4 + 12.0,
        "overhang": 14.0,
    }
    return [
        Accessory(
            "hull_a",
            "Hull panel A (front right, rear left)",
            right,
            instances=(right.rotate(Axis.Z, 180.0),),
            checks=list(own),
            **common,
        ),
        Accessory(
            "hull_b",
            "Hull panel B (front left, rear right)",
            left,
            instances=(left.rotate(Axis.Z, 180.0),),
            checks=list(own),
            **common,
        ),
    ]


_ = CLIP_WALL
