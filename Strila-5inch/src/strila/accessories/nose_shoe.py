"""Nose shoe: a TPU bumper round the front of the sandwich floor.

A floor under the nose and a wall round its edge, held by the two front standoff bolts.
The nose it covers is already the toughest edge of the frame (two skins and a 6 mm core
bolted into one 9.5 mm slab); the shoe is there so that slab does not chip and does not
cut whatever it hits.
"""

from zhalo.accessories.kit import D_M3_FREE, D_M3_HEAD, FIT, Accessory, P, box, cylinder, prism

from strila import profiles

WALL_T = 3.0
FLOOR_T = 2.6
HEAD_RECESS = 1.6
LIP = 2.5  # the wall stands this much above the deck
FLOOR_RIM = 5.0
BOSS_R = 5.5
Y_FLOOR = P.F[1] - 6.0
Y_WALL = P.F[1] - 2.0


def build() -> list[Accessory]:
    outer, pocket = profiles._body(-(FIT + WALL_T)), profiles._body(-FIT)
    far, top = 80.0, P.Z_DECK + LIP
    floor = prism(outer, -FLOOR_T, 0.0) & box(-far, Y_FLOOR, -FLOOR_T - 1, far, 120, 1)
    wall = (prism(outer, 0.0, top) - prism(pocket, -1, top + 1)) & box(-far, Y_WALL, -1, far, 120, top + 1)
    part = floor + wall
    # open the middle of the floor: what is left is a rim under the edge and a boss round each bolt
    window = prism(profiles._body(FLOOR_RIM), -FLOOR_T - 1, 1) & box(
        -far, Y_FLOOR + FLOOR_RIM, -FLOOR_T - 1, far, 120, 1
    )
    for x, y in P.pair(P.F):
        window -= cylinder(x, y, -FLOOR_T - 2, 2, 2 * BOSS_R)
    part -= window
    for x, y in P.pair(P.F):
        part -= cylinder(x, y, -FLOOR_T - 1, 1, D_M3_FREE)
        part -= cylinder(x, y, -FLOOR_T - 1, -FLOOR_T + HEAD_RECESS, D_M3_HEAD)
    under_head = FLOOR_T - HEAD_RECESS
    own = [
        ("TPU under the screw heads", under_head >= 0.8, f"{under_head:.1f} mm"),
        (
            "covers the whole edge of the floor",
            top >= P.Z_DECK + 2.0,
            f"wall Z 0 to {top:.1f}, floor edge Z 0 to {P.Z_DECK:.1f}",
        ),
    ]
    return [
        Accessory(
            "nose_shoe",
            "Nose shoe (bumper)",
            part,
            checks=own,
            ceilings=45.0,
            color="accent",
            hardware="uses the two front standoff bolts (M3x16)",
            notes="Goes on from below; the two front standoff bolts pass through its floor.",
        )
    ]
