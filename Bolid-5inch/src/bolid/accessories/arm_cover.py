"""Arm cover: a TPU channel under each arm, from the plates' edge to the motor pad. The motor wires run
inside it; from below the quad shows only clean white strips. Lips over the arm's edges hold it on."""

from build123d import Kind, offset

from bolid.accessories.base import Accessory, P, prism
from bolid.geometry import strip

U0, U1 = 60.0, P.U_MOTOR - P.PAD_D / 2 - 2.2  # the ends grow by the wall: stops short of the skid
WALL, FLOOR, CHANNEL, LIP = 1.4, 1.4, 2.6, 0.9


def _one(q: str):
    arm = strip(q, U0, U1)
    outer = offset(arm, WALL + 0.25, kind=Kind.INTERSECTION)
    part = prism(outer, P.Z_ARM - CHANNEL - FLOOR, P.Z_PRESS + 1.0)
    part -= prism(
        offset(arm, 0.25, kind=Kind.INTERSECTION) & offset(strip(q, U0 - 5, U1 + 5), 0.25, kind=Kind.INTERSECTION),
        P.Z_ARM - 0.01,
        P.Z_PRESS + 0.01,
    )
    part -= prism(offset(strip(q, U0 - 5, U1 + 5), -1.0, kind=Kind.INTERSECTION), P.Z_ARM - CHANNEL, P.Z_ARM + 0.01)
    part -= prism(offset(strip(q, U0 - 5, U1 + 5), -LIP, kind=Kind.INTERSECTION), P.Z_PRESS - 0.01, P.Z_PRESS + 1.1)
    # open the arm's slot at both ends, so it slides on along the arm
    part -= prism(offset(strip(q, U0 - 5, U1 + 5), 0.25, kind=Kind.INTERSECTION), P.Z_ARM - 0.01, P.Z_PRESS + 0.01)
    return part


def build() -> list[Accessory]:
    parts = [_one(q) for q in P.QUADS]
    return [
        Accessory(
            "arm_cover",
            "Arm cover (wire channel)",
            parts[0],
            qty=4,
            instances=tuple(parts[1:]),
            color="shell",
            bridges=80.0,
            overhang=120.0,
            checks=[("wire channel", CHANNEL >= 2.5, f"{CHANNEL:g} mm deep, as wide as the arm less 2 mm")],
            notes=(
                "Its 0.9 mm lips print as short bridges. Spread it over the arm from below "
                "before the motor goes on; the wires run inside."
            ),
        )
    ]
