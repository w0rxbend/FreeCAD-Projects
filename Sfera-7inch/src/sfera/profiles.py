"""The carbon parts of Sfera.

  plate_bottom  lower skin, 2 mm      } the base: two round skins with the arms and ten pucks
  plate_mid     deck (upper skin), 1.5 }  between them, bolted into one sandwich
  puck          8 mm fillers under the rim standoffs (cut from the arm sheet)
  arm           8 mm, four of them
  plate_top     2 mm

Everything is a circle or a piece of one. The base is a 160 mm disc with four short fingers
that reach out along the arms; the top plate is the same disc with a notch for the camera
between two prongs, a notch for the battery lead at the tail, four round ports and a bank of
gills over each side bay.
"""

from functools import lru_cache
from math import cos, hypot, radians, sin, sqrt

from zhalo import frame as F
from zhalo import params as P
from zhalo.frame import Sheet, _holes, _square
from zhalo.outline import XY, belt, bite, circle, face, lobe, mirrored, polygon, rounded_poly, rounded_rect, slot

from sfera import sizing

RB = sizing.BODY_R
FINGER_FILLET = 6.0  # where a finger meets the disc
NOSE, SIDE, CAM = sizing.NOSE, sizing.SIDE, sizing.CAM
TAIL_PAIR = (NOSE[0], -NOSE[1])
SIDE_REAR = (SIDE[0], -SIDE[1])
LEG_BOLT = P.on_arm(sizing.LEG_BOLT_U)
RIM_STANDOFFS = [*P.pair(NOSE), *P.pair(TAIL_PAIR), *P.pair(SIDE), *P.pair(SIDE_REAR)]
PRONG = ((13.2, 88.0), 3.4)  # the top plate's two prongs guard the lens: they end at Y 91.4
PRONG_FILLET = 4.0
FORK = ((0.0, 60.0), 9.4)
TAIL_NOTCH = ((0.0, -70.0), 7.0)  # the battery lead comes up here
TAIL_CORNER = 2.5
TRAY_SCREWS = [(12.0, sizing.SBC_Y), (-12.0, sizing.SBC_Y)]
STRAP_SLOTS = [((sx * 19.5, sy * 32.0), 3.6, 26.0) for sx in (1, -1) for sy in (1, -1)]  # centre, w, l
PILLS = [(sx * 8.5, y) for y in (-33.0, -11.0, 11.0, 33.0) for sx in (1, -1)]
MID_PILLS = [(0.0, y) for y in (-22.0, 0.0, 22.0)]
PILL = (18.0, 6.0)  # length, width
GILLS = ((40.0, 20.0), (48.0, 18.0), (56.0, 14.0), (64.0, 8.0))  # station X, half-length: over each side bay
GILL_W = 4.0
PORTS = (43.0, 16.0)  # the four round ports: distance out along each axis, diameter


def pill(center: XY, length: float = PILL[0], width: float = PILL[1]):
    """A slot lying along Y."""
    x, y = center
    return slot((x, y - (length - width) / 2), (x, y + (length - width) / 2), width)


def quarter(points: list[XY], k: int) -> list[XY]:
    """The points turned k quarter turns counter-clockwise."""
    for _ in range(k % 4):
        points = [(-y, x) for x, y in points]
    return points


def _base(inset: float = 0.0):
    """Outline of the base (both skins share it): the disc and its four fingers."""
    f, lam = FINGER_FILLET, P.LEG_R + FINGER_FILLET
    rho = sqrt((RB + f + 0.01) ** 2 - lam**2)  # 0.01 mm short of touching the disc: the belt needs a tangent
    rc = hypot(*P.C)
    nodes = []
    for k in range(4):
        a = radians(45 + 90 * k)
        ux, uy = cos(a), sin(a)

        def at(r: float, side: float, ux=ux, uy=uy) -> XY:
            return r * ux - side * uy, r * uy + side * ux

        nodes += [
            bite(at(rho, -lam), f + inset),
            lobe(at(rc, 0.0), P.LEG_R - inset),
            bite(at(rho, lam), f + inset),
            lobe((0.0, 0.0), RB - inset),
        ]
    return face(belt(nodes))


def _through_holes() -> list:
    return [
        *_holes("stack", "30.5 stack bolt, clamps the arm roots", P.quad(P.S)),
        *_holes("arm_inner", "arm bolt + standoff; cargo plate", P.quad(P.B)),
        *_holes("arm_leg", "arm bolt + nyloc; landing leg", P.quad(LEG_BOLT)),
        *_holes("arm_outer", "arm bolt + nyloc; landing leg", P.quad(P.C)),
        *_holes("camera_standoff", "through a puck into the standoff", P.pair(P.F)),
        *_holes("rim_standoff", "through a puck into the standoff; bumper", RIM_STANDOFFS),
    ]


# The lower skin is open under all four bays: every nut under the deck can be reached from below.
# Each opening ends in a V that follows the arm roots.
WINDOW_FRONT = [(-30.0, 46.0), (0.0, 16.0), (30.0, 46.0), (30.0, 57.0), (-30.0, 57.0)]
WINDOW_SIDE = [(46.0, 30.0), (16.0, 0.0), (46.0, -30.0), (62.0, -30.0), (62.0, 30.0)]


def _mirror_y(points: list[XY]) -> list[XY]:
    return [(x, -y) for x, y in reversed(points)]


def _mirror_x(points: list[XY]) -> list[XY]:
    return [(-x, y) for x, y in reversed(points)]


@lru_cache(maxsize=1)
def bottom_skin() -> Sheet:
    shapes = [WINDOW_FRONT, _mirror_y(WINDOW_FRONT), WINDOW_SIDE, _mirror_x(WINDOW_SIDE)]
    return Sheet("plate_bottom", P.T_BOTTOM, _base(), _through_holes(), [rounded_poly(s, 4.0) for s in shapes])


@lru_cache(maxsize=1)
def deck() -> Sheet:
    side = [(sx * sizing.SIDE_BAY_X, 0.0) for sx in (1, -1)]
    holes = [
        *_through_holes(),
        *_holes("vtx_20", "VTX 20 x 20, behind the camera", _square((0, P.VTX_BAY_Y), P.VTX_PITCH_SMALL)),
        *(h for c in side for h in _holes("bay_30p5", "side bay, 30.5 x 30.5: VTX, receiver", _square(c, 30.5))),
        *(h for c in side for h in _holes("bay_20", "side bay, 20 x 20", _square(c, 20.0))),
        *_holes("tray", "companion-computer tray, M3 + nut", TRAY_SCREWS),
    ]
    windows = [
        rounded_rect((0.0, 0.0), 20.0, 20.0, 4.0),
        rounded_rect((0.0, sizing.SBC_Y), 14.0, 14.0, 3.0),  # air under the companion computer
        pill((0.0, P.VTX_BAY_Y), 12.0),
        *(pill(c, 12.0) for c in side),
    ]
    return Sheet("plate_mid", P.T_MID, _base(), holes, windows)


PUCK_D = 9.6


@lru_cache(maxsize=1)
def puck() -> Sheet:
    """Filler between the skins under a rim or camera standoff. An 8 mm M3 spacer does the same job."""
    holes = _holes("bolt", "bolt through both skins into the standoff", [(0, 0)])
    return Sheet("puck", P.T_ARM, face(circle((0.0, 0.0), PUCK_D)), holes, [], count=10)


@lru_cache(maxsize=1)
def top_plate() -> Sheet:
    (px, py), pr = PRONG
    flank = px + pr  # the prong's outer edge runs straight back to the disc
    root = (flank + PRONG_FILLET, sqrt((RB + PRONG_FILLET + 0.01) ** 2 - (flank + PRONG_FILLET) ** 2))
    cx = TAIL_NOTCH[1] + TAIL_CORNER
    corner = (cx, -sqrt((RB - TAIL_CORNER + 0.01) ** 2 - cx**2))  # a round on each side of the tail notch's mouth
    right = [
        lobe(corner, TAIL_CORNER),
        lobe((0.0, 0.0), RB),
        bite(root, PRONG_FILLET),
        lobe((px, py), pr),
    ]
    outline = face(belt(mirrored(right, top=bite(*FORK), bottom=bite(*TAIL_NOTCH))))
    holes = [
        *_holes("camera_standoff", "standoff", P.pair(P.F)),
        *_holes("rim_standoff", "standoff; rear pair also takes the GPS and antenna perch", RIM_STANDOFFS),
        *_holes("stack_standoff", "standoff", P.quad(P.B)),
        *_holes("accessory", "accessory", P.pair(P.A1)),
    ]
    windows = [pill(c) for c in PILLS]
    windows += [pill(c, PILL[0], 5.0) for c in MID_PILLS]
    windows += [slot((x, y - l / 2 + w / 2), (x, y + l / 2 - w / 2), w) for (x, y), w, l in STRAP_SLOTS]
    windows += [slot((sx * x, -h), (sx * x, h), GILL_W) for x, h in GILLS for sx in (1, -1)]
    windows += [circle((sx * PORTS[0], sy * PORTS[0]), PORTS[1]) for sx in (1, -1) for sy in (1, -1)]
    return Sheet("plate_top", P.T_TOP, outline, holes, windows)


ARM_GUIDE_R = 2.0
PAD_FILLET = 9.0
ROOT_SLOT = (27.0, 52.0, 8.0)  # from, to, width
PAD_PORTS = (10.8, 6.4)  # four round reliefs under the motor: radius out, diameter


def _pad_fillet() -> XY:
    """Centre (u, +v) of the fillet that is tangent both to the tapering flank and to the motor pad."""
    u0, w0, u1, w1 = sizing.EDGE_U, sizing.EDGE_W / 2, P.ARM_NECK_U, sizing.NECK_W / 2
    k = (w1 - w0) / (u1 - u0)  # slope of the flank
    norm = (1 + k * k) ** 0.5

    def centre(u: float) -> XY:  # fillet centre when it touches the flank at station u
        return u + PAD_FILLET * (-k) / norm, w0 + k * (u - u0) + PAD_FILLET / norm

    lo, hi = u0, P.ARM_LEN  # slide along the flank until the fillet just touches the pad circle
    for _ in range(60):
        mid = (lo + hi) / 2
        cx, cy = centre(mid)
        gap = ((cx - P.ARM_LEN) ** 2 + cy**2) ** 0.5 - (P.MOTOR_PAD_R + PAD_FILLET + 0.01)
        lo, hi = (mid, hi) if gap > 0 else (lo, mid)
    return centre((lo + hi) / 2)


@lru_cache(maxsize=1)
def arm() -> Sheet:
    """The arm in its own coordinates: stack bolt at the origin, motor at (ARM_LEN, 0)."""
    length, hw, g = P.ARM_LEN, P.arm_half_width, ARM_GUIDE_R
    belly = hw(sizing.EDGE_U)  # the widest station is one round of this radius, centred on the axis

    def guide(u: float, side: int):
        return lobe((u, side * (hw(u) - g)), g)

    fx, fy = _pad_fillet()
    nodes = [
        guide(sizing.ROOT_U, -1),
        lobe((sizing.EDGE_U, 0.0), belly),
        bite((fx, -fy), PAD_FILLET),
        lobe((length, 0), P.MOTOR_PAD_R),
        bite((fx, fy), PAD_FILLET),
        lobe((sizing.EDGE_U, 0.0), belly),
        guide(sizing.ROOT_U, 1),
    ]
    blank = face(belt(nodes))
    far = 500.0
    corners = ((P.ARM_GAP, P.ARM_GAP), (far, P.ARM_GAP), (far, far), (P.ARM_GAP, far))
    quadrant = face(polygon([F.frame_to_arm(*p) for p in corners]))
    stack_slot = face(slot((-45, 0), (0, 0), P.STACK_SLOT_W))
    outline = F._round_root(((blank & quadrant) - stack_slot).faces()[0])
    holes = [
        *_holes("arm_inner", "arm bolt + standoff", [(P.ARM_BOLT_U[0], 0)]),
        *_holes("arm_leg", "arm bolt + nyloc", [(sizing.LEG_BOLT_U, 0)]),
        *_holes("arm_outer", "arm bolt + nyloc", [(P.ARM_BOLT_U[1], 0)]),
    ]
    c = (length, 0)
    r, d = PAD_PORTS
    ports = [circle((length + dx, dy), d) for dx, dy in ((r, 0), (-r, 0), (0, r), (0, -r))]
    root = slot((ROOT_SLOT[0], 0.0), (ROOT_SLOT[1], 0.0), ROOT_SLOT[2])  # between the arm bolts, inside the sandwich
    windows = [*F.motor_slots(c), circle(c, P.MOTOR_BORE_D), *ports, root]
    return Sheet("arm", P.T_ARM, outline, holes, windows, count=4)


SHEETS = {"plate_bottom": bottom_skin, "plate_mid": deck, "plate_top": top_plate, "arm": arm, "puck": puck}

# name of each puck -> where it goes
PUCKS = {
    "puck_camera_right": P.F,
    "puck_camera_left": (-P.F[0], P.F[1]),
    "puck_nose_right": NOSE,
    "puck_nose_left": (-NOSE[0], NOSE[1]),
    "puck_tail_right": TAIL_PAIR,
    "puck_tail_left": (-TAIL_PAIR[0], TAIL_PAIR[1]),
    "puck_side_front_right": SIDE,
    "puck_side_front_left": (-SIDE[0], SIDE[1]),
    "puck_side_rear_right": SIDE_REAR,
    "puck_side_rear_left": (-SIDE_REAR[0], SIDE_REAR[1]),
}


def bill_of_materials() -> dict:
    floor = P.T_BOTTOM + P.T_ARM + P.T_MID
    return {
        "carbon": [
            {"part": name, "qty": make().count, "thickness_mm": make().thickness} for name, make in SHEETS.items()
        ],
        "standoffs": [
            {
                "item": f"M3 x {P.STACK_STANDOFF_H:g} mm round standoff, OD {P.STANDOFF_OD:g}",
                "qty": len(P.STANDOFFS),
                "where": "all fourteen stand on the deck",
            },
        ],
        "screws": [
            {
                "item": "M3 x 35 (with the stack) + M3 nut",
                "qty": 4,
                "where": f"stack bolts: through the {floor:g} mm base, nut on the deck, then the stack",
            },
            {
                "item": "M3 x 22 button head",
                "qty": 4,
                "where": "inner arm bolts: through the cargo plate and the base into the stack standoffs "
                "(M3 x 16 without the cargo plate)",
            },
            {
                "item": "M3 x 18 button head",
                "qty": 8,
                "where": "rim standoffs: through the bumper and the base",
            },
            {"item": "M3 x 16 button head", "qty": 2, "where": "camera standoffs, through the base"},
            {
                "item": "M3 x 20 button head + nyloc",
                "qty": 8,
                "where": "the two outer bolts of each arm: head on the deck, nut in the leg "
                "(M3 x 16 and a nut under the base without the legs)",
            },
            {"item": "M3 x 8 button head", "qty": 14, "where": "top plate into the standoffs"},
            {
                "item": "M3 x 12",
                "qty": 16,
                "where": "motors: the arm is 8 mm, so M3 x 12 puts 4 mm of thread in the motor; "
                "check your motor's thread depth",
            },
        ],
    }
