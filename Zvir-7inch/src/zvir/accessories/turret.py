"""Chin turret: a second camera under the nose that a 9 g servo tilts from 15 deg above the
horizon to straight down.

Three rigid prints (PETG, not TPU: a camera on a soft mount cannot be calibrated):

  bracket  bolts under the nose with the two front-standoff bolts and a third one. Its left
           wall carries the servo, its right cheek the pivot.
  cradle   holds a 25 x 24 mm camera board on four M2 posts. Its left wall drops over the
           servo horn, a screw through the cheek is its other bearing.
  spacer   a C-clip on the pivot screw. It takes up the slack the cradle needs to slide
           onto the horn, so it goes in last.

The tilt axis is 21.5 mm under the floor and 4 mm behind the nose edge: looking down, the
lens is ahead of everything on the quad except the talons, and those are outside its view.
"""

from math import cos, radians, sin

from zhalo import checks as C
from zhalo import equipment as E
from zhalo import frame as F
from zhalo.accessories.kit import (
    D_M3_FREE,
    D_M3_HEAD,
    Accessory,
    P,
    box,
    c_ring,
    cylinder,
    disc,
    poly,
    prism,
    prism_x,
    prism_y,
)

from zvir import payload as T
from zvir import profiles, sizing

PETG = "PETG"
FLOOR_T = 5.0
HEAD_RECESS = 2.2  # the three bolt heads sit flush: the cradle swings 2 mm under this floor
WALL_T = 4.0
BRACKET_Y = (100.0, profiles.NOSE_Y - 0.4)
BRACKET_X1 = 21.0  # right edge of the floor behind the pivot cheek's tongue
TONGUE_Y = 115.0  # the tongue starts ahead of the right front talon
WALL_Y = (97.5, 133.5)  # the servo wall: long enough for both ear screws
CHEEK_HALF = 6.0
SIDE = [(-3.0, -13.5), (6.0, -13.5), (15.0, -4.5), (15.0, 4.5), (5.0, 13.5), (-3.0, 13.5)]  # cradle wall, (f, h)
BACK = (-3.0, -1.0)  # the cradle's back plate, behind the tilt axis
BACK_H = (-6.0, 11.5)  # open below: the ribbon socket and the ribbon
POST_D, PILOT_M2 = 4.6, 1.7
PIVOT_PILOT = 2.7  # an M3 screw cuts its own thread in PETG
HORN_ROOT, HORN_TIP = 3.1, 2.3  # half-widths of the horn pocket at the hub and at its open end
SCREW_HEAD_D = 5.5  # clearance for the head of the horn screw
AXIS = (T.TILT_Y, T.TILT_Z)
BOLTS = [*P.pair(P.F), sizing.NOSE_BOLT]


def _bracket():
    wx0, wx1 = T.SERVO_EAR_X - WALL_T, T.SERVO_EAR_X
    cx0, cx1 = T.CHEEK_X
    y0, y1 = BRACKET_Y
    plan = poly([(wx0, y0), (BRACKET_X1, y0), (BRACKET_X1, TONGUE_Y), (cx1, TONGUE_Y), (cx1, y1), (wx0, y1)], 1.5)
    part = prism(plan, -FLOOR_T, 0.0)
    # servo wall: a slab hanging from the floor with a slot, open downwards, that the servo case drops into
    l, w, _h = T.SERVO_BODY
    sy1 = T.TILT_Y + T.SERVO_SHAFT_BACK + 0.2
    sy0 = sy1 - l - 0.4
    bottom = T.TILT_Z - w / 2
    wall = poly([(WALL_Y[0], bottom), (WALL_Y[1], bottom), (WALL_Y[1], 0.0), (WALL_Y[0], 0.0)])
    wall -= poly([(sy0, bottom - 5), (sy1, bottom - 5), (sy1, T.TILT_Z + w / 2 + 0.2), (sy0, T.TILT_Z + w / 2 + 0.2)])
    part += prism_x(wall, wx0, wx1)
    yc = T.TILT_Y + T.SERVO_SHAFT_BACK - l / 2
    for sy in (1, -1):
        part -= prism_x(disc((yc + sy * T.SERVO_HOLES / 2, T.TILT_Z), PILOT_M2), wx0 - 1, wx1 + 1)
    # pivot cheek on the other side
    cheek = poly(
        [
            (T.TILT_Y - CHEEK_HALF, T.TILT_Z),
            (T.TILT_Y + CHEEK_HALF, T.TILT_Z),
            (T.TILT_Y + CHEEK_HALF, 0.0),
            (T.TILT_Y - CHEEK_HALF, 0.0),
        ]
    ) + disc(AXIS, 2 * CHEEK_HALF)
    part += prism_x(cheek, cx0, cx1)
    part -= prism_x(disc(AXIS, D_M3_FREE), cx0 - 1, cx1 + 1)
    for xy in BOLTS:
        part -= cylinder(*xy, -FLOOR_T - 1, 1, D_M3_FREE)
        part -= cylinder(*xy, -FLOOR_T - 1, -FLOOR_T + HEAD_RECESS, D_M3_HEAD)
    return part


def _cradle_local():
    """The cradle about the tilt axis: lens along +Y ("f"), board upright ("h" = Z), X as on the frame."""
    (x0, x1), xl, xr = T.X_IN, T.X_L, T.X_R
    side = poly(SIDE, 2.0)
    part = prism_x(side, xl, x0) + prism_x(side, x1, xr)
    part += box(x0 - 0.01, BACK[0], BACK_H[0], x1 + 0.01, BACK[1], BACK_H[1])
    bw, bh, bt = T.CAM_BOARD
    rows = (bh / 2 - 2.0, bh / 2 - 2.0 - T.CAM_HOLES[1])
    posts = [(T.CAM_X + sx * T.CAM_HOLES[0] / 2, h) for h in rows for sx in (1, -1)]
    for xz in posts:
        part += prism_y(disc(xz, POST_D), BACK[1] - 0.01, T.BOARD_F - bt)
    for xz in posts:
        part -= prism_y(disc(xz, PILOT_M2), BACK[0] - 1, T.BOARD_F)
    # left wall: a pocket the servo horn drops into, open to the front, and room for the horn screw's head
    reach = SIDE[2][0] + 1.0
    horn = disc((0.0, 0.0), T.HORN_HUB_D + 0.4) + poly(
        [(0.0, -HORN_ROOT), (reach, -HORN_TIP), (reach, HORN_TIP), (0.0, HORN_ROOT)]
    )
    part -= prism_x(horn, xl - 1, xl + T.POCKET)
    part -= prism_x(disc((0.0, 0.0), SCREW_HEAD_D), xl - 1, x0 + 0.01)
    # right wall: the pivot screw
    part -= prism_x(disc((0.0, 0.0), PIVOT_PILOT), x1 - 0.01, xr + 1)
    return part


def _spacer():
    x0 = T.X_R + 0.1
    return prism_x(c_ring(AXIS, -90.0, wall=2.6, bore=D_M3_FREE, mouth=3.1), x0, x0 + T.SPACER_T)


def _tilts(n: int = 15) -> list[float]:
    lo, hi = T.TILT_RANGE
    return [lo + (hi - lo) * k / (n - 1) for k in range(n)]


def _sweep(cradle, bracket) -> tuple[dict, float]:
    """(what the cradle and its camera touch anywhere in their travel, least gap to the bracket)."""
    from zvir.accessories import talon

    others = {**F.parts(), "bracket": bracket, "servo": T.servo()}
    for acc in talon.build():
        for i, p in enumerate((acc.part, *acc.instances)):
            others[f"{acc.name}#{i + 1}"] = p
    moving = (cradle, T.cv_camera_local())
    hits, gap = {}, float("inf")
    for tilt in _tilts():
        for part in moving:
            placed = T.tilted(part, tilt)
            for name, other in others.items():
                v = C.overlap(placed, other)
                if v > C.EPS:
                    hits[name] = max(hits.get(name, 0.0), round(v, 2))
        gap = min(gap, T.tilted(cradle, tilt).distance_to(bracket))
    return hits, gap


def _view(cradle, bracket, spacer) -> dict:
    """What gets into the lens's field anywhere between straight down and the horizon."""
    from zvir.accessories import talon

    others = {**F.parts(), "bracket": bracket, "spacer": spacer, "servo": T.servo()}
    for name, xy in P.MOTORS.items():
        others[f"motor_{name}"] = E.motor(xy)
    for acc in talon.build():
        for i, p in enumerate((acc.part, *acc.instances)):
            others[f"{acc.name}#{i + 1}"] = p
    seen = {}
    for tilt in (-90.0, -45.0, 0.0):
        cone = T.view_cone(tilt)
        scene = {**others, "cradle": T.tilted(cradle, tilt)}
        for name, other in scene.items():
            v = C.overlap(cone, other)
            if v > C.EPS:
                seen[f"{name} at {tilt:.0f}"] = round(v, 1)
    return seen


def build() -> list[Accessory]:
    bracket, cradle, spacer = _bracket(), _cradle_local(), _spacer()
    hits, gap = _sweep(cradle, bracket)
    seen = _view(cradle, bracket, spacer)
    lo, hi = T.TILT_RANGE
    board = C.overlap(cradle, T.cv_camera_local())
    slack = T.CHEEK_X[0] - T.X_R - T.PLAY
    t = radians(T.TILT_SHOWN)
    cradle_checks = [
        (
            f"tilts {hi:.0f} to {lo:.0f} deg without touching anything",
            not hits,
            str(hits or f"{gap:.2f} mm to the bracket"),
        ),
        ("looks straight down", lo <= -90.0, f"travel {hi - lo:.0f} deg, a 9 g servo gives 180"),
        ("nothing of the quad in a 76 deg field of view", not seen, str(seen or "clear at 0, -45 and -90 deg")),
        ("camera board drops between the walls onto its posts", board < C.EPS, f"{board:.3f} mm3"),
        (
            "slides onto the servo horn",
            slack >= T.POCKET,
            f"{slack:.1f} mm of slack before the spacer, pocket {T.POCKET} mm",
        ),
    ]
    bracket_checks = [
        (
            "bolt heads are flush under the floor",
            HEAD_RECESS >= 1.7 and FLOOR_T - HEAD_RECESS >= 2.5,
            f"{HEAD_RECESS} mm recess, {FLOOR_T - HEAD_RECESS:.1f} mm of PETG under each head",
        ),
        (
            "servo case drops into its slot",
            C.overlap(bracket, T.servo()) < C.EPS,
            f"{C.overlap(bracket, T.servo()):.3f} mm3 shared with the servo",
        ),
    ]
    common = {"material": PETG, "color": "petg"}
    return [
        Accessory(
            "turret_bracket",
            "Turret bracket",
            bracket,
            bed=(0, 0, 1),
            holds=("servo",),
            checks=bracket_checks,
            ceilings=6.0,
            overhang=14.0,
            hardware="3x M3x20 (two replace the front-standoff bolts, the third takes a nyloc on the deck), "
            "the servo's own two screws, M3x10 pivot screw",
            notes=(
                "PETG or ASA, 4 perimeters. Print it upside down, the face that meets the carbon on the bed. "
                "Bolt it on before the servo goes in: the servo covers the left bolt. The servo case drops into "
                "the slot from below, shaft to the right."
            ),
            **common,
        ),
        Accessory(
            "turret_cradle",
            "Turret camera cradle",
            T.tilted(cradle, T.TILT_SHOWN),
            bed=(0.0, -cos(t), -sin(t)),
            holds=("cv_camera", "servo"),
            checks=cradle_checks,
            ceilings=8.0,
            overhang=24.0,
            hardware="4x M2x5 self-tapping (camera board), the servo's horn and horn screw",
            notes=(
                f"PETG or ASA, back plate on the bed. For a {T.CAM_BOARD[0]:g} x {T.CAM_BOARD[1]:g} mm camera board "
                "(Raspberry Pi Camera Module 2 / 3 outline). Screw the single-arm horn to the servo at mid travel, "
                "slide the cradle sideways onto it, then fit the pivot screw through the cheek and clip the spacer on."
            ),
            **common,
        ),
        Accessory(
            "turret_spacer",
            "Turret pivot spacer",
            spacer,
            bed=(1, 0, 0),
            notes="PETG. Clips onto the pivot screw between the cheek and the cradle once the cradle is on the horn.",
            **common,
        ),
    ]
