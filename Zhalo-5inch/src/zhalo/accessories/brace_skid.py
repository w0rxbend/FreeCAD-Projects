"""Landing skids: a TPU rail under each side brace.

The two skids are the lowest points of the quad, wide apart and 52 mm long, so it stands
level on them and the bottom-plate screw heads never meet the ground. They bolt to the two
accessory holes in the middle of each brace.
"""

from zhalo.accessories.kit import D_M3_FREE, D_M3_HEAD, Accessory, P, cylinder, mirror_x, poly, prism_x

HEIGHT = 5.5
WIDTH = 8.6
HALF_LEN = 26.0  # stops short of the brace bolts at the lugs
TAPER = 4.5  # ski tip at each end
UNDER_HEAD = 2.0
Z1 = P.Z_BRACE  # underside of the brace


def build() -> list[Accessory]:
    x = P.LUG[0]
    z0 = Z1 - HEIGHT
    side = poly([(-HALF_LEN, Z1), (HALF_LEN, Z1), (HALF_LEN - TAPER, z0), (-HALF_LEN + TAPER, z0)], 1.0)
    right = prism_x(side, x - WIDTH / 2, x + WIDTH / 2)
    for sy in (1, -1):
        y = sy * P.BRACE_ACC_Y
        right -= cylinder(x, y, z0 - 1, Z1 + 1, D_M3_FREE)
        right -= cylinder(x, y, z0 - 1, Z1 - UNDER_HEAD, D_M3_HEAD)
    lowest = {"skids": z0, "nose bumper": -2.6, "plate screw heads": -1.65}
    own = [
        (
            "the skids are the lowest point",
            z0 < min(v for k, v in lowest.items() if k != "skids") - 1.0,
            ", ".join(f"{k} Z {v:.1f}" for k, v in lowest.items()),
        ),
        (
            "clear of the lug bolts",
            HALF_LEN + 3.2 < abs(P.LUG[1]),
            f"skid ends at Y {HALF_LEN:.0f}, lug bolts at Y {abs(P.LUG[1]):.1f}",
        ),
    ]
    note = "Screws from below, heads buried in the skid, nyloc nuts on top of the brace."
    return [
        Accessory(
            "brace_skid",
            "Landing skid",
            right,
            bed=(0, 0, 1),
            qty=2,
            checks=own,
            instances=(mirror_x(right),),
            hardware="2x M3x10 + nyloc per skid",
            notes=note,
        )
    ]
