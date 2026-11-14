"""Wire grommet: a TPU eyelet in each arm's wire slot, where the motor wires leave the box. The carbon
edge would cut their insulation; the grommet snaps in from above and its lip holds under the skin."""

from vektor.accessories.base import Accessory, P, prism
from vektor.geometry import slot

FLANGE, LIP, WALL = 1.6, 0.6, 1.2


def _one(q: str):
    r, length, w = P.WIRE_SLOT
    a, b = P.on_arm(q, r - length / 2), P.on_arm(q, r + length / 2)
    outer_neck = slot(a, b, w - 0.15)
    inner = slot(a, b, w - 0.15 - 2 * WALL)
    flange = slot(a, b, w + 2 * FLANGE)
    lip = slot(a, b, w + 2 * LIP)
    part = prism(flange - inner, P.Z_DECK, P.Z_DECK + 1.2)
    part += prism(outer_neck - inner, P.Z_UPPER - 0.01, P.Z_DECK + 0.01)
    part += prism(lip - inner, P.Z_UPPER - 1.0, P.Z_UPPER)
    return part


def build() -> list[Accessory]:
    parts = [_one(q) for q in P.QUADS]
    return [
        Accessory(
            "wire_grommet",
            "Wire grommet",
            parts[0],
            bed=(0, 0, 1),
            qty=4,
            instances=tuple(parts[1:]),
            color="accent",
            bridges=30.0,
            overhang=20.0,
            notes=(
                "Squeeze it into the slot from above until the lip clicks under the skin; then feed the wires through."
            ),
        )
    ]
