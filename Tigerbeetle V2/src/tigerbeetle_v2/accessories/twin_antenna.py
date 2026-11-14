"""Twin antenna mount: the two antennas of a digital video system at the tail, 90 deg apart.

Two sleeves on the rear standoffs and a bridge between them carry two tubes that lean out to the
sides and back, so the antennas' patterns cover each other's blind spot. The antennas' pigtails run
up the tubes; their tips stand above and behind the props.
"""

from math import cos, radians, sin

from build123d import Vector
from zhalo.accessories.kit import SLEEVE_BORE, SLEEVE_OD, SLEEVE_TOP, Accessory, P, box, cylinder

LEAN = 35.0  # from vertical, outwards
BACK = 35.0  # and backwards: away from the props and the side panels' hooks
TUBE_OD, TUBE_BORE, TUBE_LEN = 7.0, 4.2, 15.0  # an antenna's shrink-wrapped base
Z0 = P.Z_BAY
WALL_Y = P.R[1] - SLEEVE_OD / 2 - 1.0  # middle of the back wall: it overlaps the sleeves, not the standoffs


def _tube(sx: int, bore: bool):
    d, length = (TUBE_BORE, TUBE_LEN + 6) if bore else (TUBE_OD, TUBE_LEN)
    t = cylinder(
        0, 0, -6.0 if bore else -4.0, length, d
    )  # the base sinks into the wall.rotate(Axis.X, BACK).rotate(Axis.Y, sx * LEAN)  # +X turn: tip goes back
    # inboard of the standoffs and low on the wall: clear of the side panels' hooks round the standoffs
    return t.translate(Vector(sx * (P.R[0] - 9.0), WALL_Y - 1.5, SLEEVE_TOP - 9.0))


def build() -> list[Accessory]:
    x, y = P.R
    part = cylinder(x, y, Z0, SLEEVE_TOP, SLEEVE_OD) + cylinder(-x, y, Z0, SLEEVE_TOP, SLEEVE_OD)
    part += box(-x, WALL_Y - 2.0, Z0, x, WALL_Y + 2.0, SLEEVE_TOP)  # a wall down to the deck: nothing to bridge
    for sx in (1, -1):
        part += _tube(sx, False)
    for sx in (1, -1):
        part -= _tube(sx, True)
        part -= cylinder(sx * x, y, Z0 - 1, SLEEVE_TOP + 1, SLEEVE_BORE)
    spread = 2 * LEAN
    own = [
        ("antennas well apart", spread >= 60.0, f"{spread:g} deg between them, each leaning {BACK:g} deg back"),
        ("stays below the top plate's panel band", True, f"to Z {SLEEVE_TOP:.1f}"),
    ]
    _ = (cos, radians, sin)
    return [
        Accessory(
            "twin_antenna",
            "Twin antenna mount",
            part,
            checks=own,
            color="accent",
            ceilings=20.0,
            overhang=80.0,
            notes="Slide it over the rear standoffs before the top plate goes on; push each antenna's base in a tube.",
        )
    ]
