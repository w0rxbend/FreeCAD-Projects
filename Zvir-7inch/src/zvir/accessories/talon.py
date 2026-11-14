"""Talons: four landing legs, one under each corner of the body.

The quad stands 45 mm off the ground, so the turret (which reaches 36.5 mm down when it looks
straight down) never touches it. Each leg hangs on one bolt, the one that already holds a
corner standoff, and a lip up the side of the floor stops it turning. The profile is the
same through the whole 12 mm: it prints lying on its side with nothing overhanging.
"""

from zhalo.accessories.kit import D_M3_FREE, D_M3_HEAD, FIT, Accessory, P, cylinder, mirror_x, poly, prism_y

from zvir import payload, profiles, sizing

HEIGHT = 45.0
THICK = 12.0
FLANGE_T = 4.0
UNDER_HEAD = 2.0
LIP_T, LIP_H = 2.4, 6.0
INNER_X = profiles.BODY_HALF - 0.8  # the leg starts here: outside the servo, under the edge of the floor
# the claw below the flange, as (distance outboard of INNER_X, z): outer edge top to bottom, then inner edge back up
OUTER = [(9.3, -12.0), (13.3, -28.0), (15.3, -40.0), (15.3, -HEIGHT)]
INNER = [(9.3, -HEIGHT), (6.3, -38.0), (2.3, -28.0), (0.0, -14.0), (0.0, -FLANGE_T)]


def _leg(bolt):
    xb, yb = bolt
    xe = profiles.BODY_HALF + FIT
    points = [
        (xb - 6.5, 0.0),
        (xb - 6.5, -FLANGE_T),
        *[(INNER_X + dx, z) for dx, z in reversed(INNER)],
        *[(INNER_X + dx, z) for dx, z in reversed(OUTER)],
        (xe + LIP_T, -2.0),
        (xe + LIP_T, LIP_H),
        (xe, LIP_H),
        (xe, 0.0),
    ]
    profile = poly(points, 1.0)
    # the corner the floor's edge sits in stays sharp
    profile -= poly([(xe - 2.0, 0.0), (xe, 0.0), (xe, 2.0), (xe - 2.0, 2.0)])
    part = prism_y(profile, yb - THICK / 2, yb + THICK / 2)
    part -= cylinder(xb, yb, -FLANGE_T - 1, 1, D_M3_FREE)
    part -= cylinder(xb, yb, -FLANGE_T - 1, -UNDER_HEAD, D_M3_HEAD)
    return part


def build() -> list[Accessory]:
    reach = payload.TILT_Z - 15.0  # the turret's lowest point: the cradle's nose, looking straight down
    out = []
    for tag, bolt in (("front", sizing.NOSE), ("rear", P.R)):
        right = _leg(bolt)
        foot = profiles.BODY_HALF - 0.8 + (OUTER[-1][0] + INNER[0][0]) / 2
        own = [
            (
                "keeps the turret off the ground",
                -HEIGHT <= reach - 5.0,
                f"feet Z {-HEIGHT:.0f}, turret to Z {reach:.1f}",
            ),
            ("TPU under the screw head", UNDER_HEAD >= 1.5, f"{UNDER_HEAD:.1f} mm"),
            (
                "stance",
                foot > profiles.BODY_HALF,
                f"feet {2 * foot:.0f} mm apart across, {sizing.NOSE[1] - P.R[1]:.0f} mm along",
            ),
        ]
        out.append(
            Accessory(
                f"talon_{tag}",
                f"Talon ({tag} leg)",
                right,
                bed=(0, 1, 0),
                qty=2,
                checks=own,
                instances=(mirror_x(right),),
                color="accent",
                ceilings=6.0,
                overhang=12.0,
                hardware="uses the corner standoff's bolt (M3x18)",
                notes=(
                    "Print it lying on its side, 4 perimeters, 40 % infill or more: it is a spring. The left and the "
                    "right leg are the same print. The lip goes up the outside of the floor; the bolt's head sinks "
                    "into the flange."
                ),
            )
        )
    return out
