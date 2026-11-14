"""The carbon parts of Zvir.

  plate_bottom  lower skin, 2 mm      } the floor: two skins with the arms, the two core rims
  plate_mid     deck (upper skin), 1.5 }  and four pucks between them, bolted into one sandwich
  core_nose / core_tail / puck   8 mm fillers of that sandwich (cut from the arm sheet)
  arm           8 mm, four of them
  brace         3 mm, two of them: front arm to rear arm on each side
  plate_top     2 mm

The body is a 74 mm wide rounded slab, 283 mm long: three bays in a row on one deck (camera
and VTX, stack, companion computer). Corners are R12 and the tail runs out into a blunt
arrow. The decoration is cut where it weakens nothing: fangs in the motor pads, claw marks
in the braces, a crown and two chevrons in the top plate.
"""

from dataclasses import replace
from functools import lru_cache
from math import cos, radians, sin

from build123d import Face, fillet
from zhalo import frame as F
from zhalo import params as P
from zhalo.frame import Sheet, _holes, _square
from zhalo.outline import (
    XY,
    belt,
    bite,
    chevron,
    circle,
    face,
    lobe,
    mirrored,
    polygon,
    rounded_poly,
    rounded_rect,
    scallop,
    slot,
)

from zvir import sizing

BODY_HALF = 37.0  # the floor is a straight 74 mm strip
FILLET = 8.0  # inside corners where a leg meets the body
CORNER = 12.0  # outside corners of the body
NOSE_Y = 125.0  # the nose is cut square: the turret hangs under it and looks past its edge
TAIL_CORNER_Y = -132.0  # the sides run straight down to here
TAIL_TIP = ((0.0, -152.0), 6.0)  # blunt arrow: it lies under the companion computer's plugs
RIM = 4.0  # width of the two core rims
MID_F, MID_R = sizing.MID, (sizing.MID[0], -sizing.MID[1])
B_F, B_R = P.B, (P.B[0], -P.B[1])
PRONG = (13.2, 131.5)  # tip of the top plate's camera fork: it ends at Y 134.9
FORK = ((0.0, 114.0), 9.4)
TAIL_NOTCH = ((0.0, -137.5), 9.0)
TRAY_SCREWS = [(22.0, -62.5), (-22.0, -62.5)]  # the companion computer's tray
STRAP_SLOTS = [((sx * 19.5, sy * 32.0), 3.6, 26.0) for sx in (1, -1) for sy in (1, -1)]  # centre, w, l
PILL_ROWS = (-55.0, -33.0, -11.0, 11.0, 33.0, 55.0)
PILL_X = 8.5
MID_PILLS = (-44.0, -22.0, 0.0, 22.0, 44.0)  # a third, narrower column between the two
PILL = (18.0, 6.0)  # length, width


def pill(center: XY, length: float = PILL[0], width: float = PILL[1]):
    """A slot lying along Y."""
    x, y = center
    return slot((x, y - (length - width) / 2), (x, y + (length - width) / 2), width)


def _leg_fillet(sy: int, front_edge: bool) -> XY:
    """Centre of the fillet between the body's straight side and one edge of a right-hand leg.
    sy: +1 front leg, -1 rear leg. front_edge: the leg's edge that faces away from the stack."""
    dx, dy = P.ARM_DIR[0], sy * P.ARM_DIR[1]
    nx, ny = (-dy, dx) if sy > 0 else (dy, -dx)  # normal pointing away from the stack (towards the bay)
    if not front_edge:
        nx, ny = -nx, -ny  # the other edge: normal pointing towards the waist
    px, py = P.C[0] + P.LEG_R * nx, sy * P.C[1] + P.LEG_R * ny  # a point on that edge
    cx = BODY_HALF + FILLET
    return cx, py + (FILLET - (cx - px) * nx) / ny


def _body(inset: float = 0.0):
    """Outline of the floor (both skins share it). `inset` moves it inwards by that much; negative grows it."""
    c, f, leg = CORNER - inset, FILLET + inset, P.LEG_R - inset
    right = [
        lobe((BODY_HALF - CORNER, TAIL_CORNER_Y), c),
        bite(_leg_fillet(-1, True), f),
        lobe((P.C[0], -P.C[1]), leg),
        bite(_leg_fillet(-1, False), f),
        bite(_leg_fillet(1, False), f),
        lobe(P.C, leg),
        bite(_leg_fillet(1, True), f),
        lobe((BODY_HALF - CORNER, NOSE_Y - CORNER), c),
    ]
    return face(belt(mirrored(right, bottom=lobe(TAIL_TIP[0], TAIL_TIP[1] - inset))))


def body(grow: float = 0.0):
    """The floor's outline grown outwards by `grow`: what a part that hugs the body's edge is cut against."""
    return _body(-grow)


def _through_holes() -> list:
    return [
        *_holes("stack", "30.5 stack bolt, clamps the arm roots", P.quad(P.S)),
        *_holes("arm_inner", "arm bolt + standoff", P.quad(P.B)),
        *_holes("arm_outer", "arm bolt + nyloc", P.quad(P.C)),
        *_holes("front_standoff", "through the nose core into the standoff; turret bracket", P.pair(P.F)),
        *_holes("nose_standoff", "through the nose core into the standoff; front talons", P.pair(sizing.NOSE)),
        *_holes("mid_standoff", "through a puck into the standoff", P.quad(sizing.MID)),
        *_holes("rear_standoff", "through the tail core into the standoff; rear talons", P.pair(P.R)),
        *_holes("nose_bolt", "third turret-bracket bolt + nyloc", [sizing.NOSE_BOLT]),
    ]


# The lower skin is open under both bays: every nut under the deck can be reached, and the turret's
# leads come up through the front opening. Each opening ends in a V that follows the arm roots.
WINDOW_REAR = [(-27.0, -118.0), (27.0, -118.0), (27.0, -40.5), (0.0, -20.0), (-27.0, -40.5)]
WINDOW_FRONT = [(-27.0, 40.5), (0.0, 20.0), (27.0, 40.5), (27.0, 96.0), (-27.0, 96.0)]


TAIL_ARROW = [(-15.0, -126.0), (15.0, -126.0), (0.0, -141.0)]  # an arrowhead window in the tail of both skins


@lru_cache(maxsize=1)
def bottom_skin() -> Sheet:
    windows = [rounded_poly(WINDOW_REAR, 5.0), rounded_poly(WINDOW_FRONT, 5.0), rounded_poly(TAIL_ARROW, 3.0)]
    return Sheet("plate_bottom", P.T_BOTTOM, _body(), _through_holes(), windows)


@lru_cache(maxsize=1)
def deck() -> Sheet:
    holes = [
        *_through_holes(),
        *_holes("accessory", "action-camera mount rear screws / accessory", P.pair(P.A1)),
        *_holes("vtx_30p5", "analog VTX 30.5 x 30.5", _square((0, P.VTX_BAY_Y), P.VTX_PITCH_LARGE)),
        *_holes("vtx_20", "analog VTX 20 x 20", _square((0, P.VTX_BAY_Y), P.VTX_PITCH_SMALL)),
        *_holes("tray", "companion-computer tray, M3 + nut", TRAY_SCREWS),
    ]
    windows = [
        rounded_rect((0.0, -74.0), 34.0, 66.0, 6.0),  # air under the companion computer
        rounded_rect((0.0, 0.0), 20.0, 20.0, 4.0),
        pill((0.0, P.VTX_BAY_Y), 12.0),
        rounded_rect((0.0, 84.0), 22.0, 14.0, 3.0),  # camera ribbon and servo lead come up here
        rounded_poly(TAIL_ARROW, 3.0),
    ]
    return Sheet("plate_mid", P.T_MID, _body(), holes, windows)


def _rounded(f: Face, r: float = 1.2) -> Face:
    """Round every sharp corner of a profile (the ends of a cut rim, the foot of a boss)."""
    sharp = [v for v in f.vertices() if F._is_corner(f, v)]
    if not sharp:
        return f
    try:
        out = fillet(sharp, r)
        done = out.faces()[0] if hasattr(out, "faces") else out
        if done.is_valid and done.area > 0.8 * f.area:
            return done
    except Exception:  # noqa: BLE001 - OCCT refuses some corner sets; the sharp profile is still valid
        pass
    return f


CORE_Y = (-122.0, 100.0)  # the tail rim starts behind this station, the nose rim ahead of it


def _core(front: bool) -> Sheet:
    """Rim that fills the gap between the skins round the nose (or the tail), with a boss at each bolt."""
    far = 300.0
    rim = _body() - _body(RIM)
    y0 = CORE_Y[1] if front else CORE_Y[0]
    half = (
        [(-far, y0), (far, y0), (far, far), (-far, far)]
        if front
        else [(-far, -far), (far, -far), (far, y0), (-far, y0)]
    )
    shape = rim & face(polygon(half))
    if front:
        bolts = [*P.pair(P.F), *P.pair(sizing.NOSE), sizing.NOSE_BOLT]
        webs = [*P.pair(P.F), sizing.NOSE_BOLT]  # these sit too far in to touch the rim: a web joins them to it
    else:
        bolts, webs = P.pair(P.R), []
    for p in bolts:
        shape = shape + (face(circle(p, 2 * P.LOBE_R)) & _body())
    for p in webs:
        shape = shape + (face(slot(p, (p[0], NOSE_Y - RIM / 2), 2 * P.LOBE_R)) & _body())
    profile = _rounded(max(shape.faces(), key=lambda f: f.area))
    name = "core_nose" if front else "core_tail"
    return Sheet(name, P.T_ARM, Face(profile.outer_wire()), _holes("bolt", "bolt through both skins", bolts), [])


@lru_cache(maxsize=1)
def core_nose() -> Sheet:
    return _core(True)


@lru_cache(maxsize=1)
def core_tail() -> Sheet:
    return _core(False)


PUCK = (8.0, 16.0)  # width, length


@lru_cache(maxsize=1)
def puck() -> Sheet:
    """Filler between the skins under a mid standoff, drawn round its own bolt."""
    w, l = PUCK
    outline = face(slot((0.0, -(l - w) / 2), (0.0, (l - w) / 2), w))
    return Sheet("puck", P.T_ARM, outline, _holes("bolt", "bolt through both skins into the standoff", [(0, 0)]), [], 4)


CROWN = [(-14.0, -97.0), (14.0, -97.0), (14.0, -81.0), (7.0, -89.0), (0.0, -79.0), (-7.0, -89.0), (-14.0, -81.0)]
CHEVRON_Y = (80.0, 91.0)


@lru_cache(maxsize=1)
def top_plate() -> Sheet:
    r = P.LOBE_R
    n_r, m_r, b_r = lobe(P.R, r), lobe(MID_R, r), lobe(B_R, r)
    b_f, m_f, ns = lobe(B_F, r), lobe(MID_F, r), lobe(sizing.NOSE, r)
    waist = scallop(m_r, b_r, 3.0)
    right = [
        replace(n_r, link=scallop(n_r, m_r, 3.0)),  # bowed in: the rear prop passes 2.5 mm outside this edge
        replace(m_r, link=waist),
        replace(b_r, link=scallop(b_r, b_f, 2.0)),
        replace(b_f, link=waist),
        replace(m_f, link=scallop(m_f, ns, 1.2)),  # and the front prop outside this one
        ns,
        lobe(PRONG, 3.4),
    ]
    outline = face(belt(mirrored(right, top=bite(*FORK), bottom=bite(*TAIL_NOTCH))))
    holes = [
        *_holes("front_standoff", "standoff; action-camera mount front screws", P.pair(P.F)),
        *_holes("nose_standoff", "standoff", P.pair(sizing.NOSE)),
        *_holes("mid_standoff", "standoff", P.quad(sizing.MID)),
        *_holes("stack_standoff", "standoff", P.quad(P.B)),
        *_holes("rear_standoff", "standoff; GPS and antenna crown screws", P.pair(P.R)),
        *_holes("accessory", "action-camera mount rear screws", P.pair(P.A1)),
    ]
    windows = [pill((sx * PILL_X, y)) for y in PILL_ROWS for sx in (1, -1)]
    windows += [pill((0.0, y), PILL[0], 5.0) for y in MID_PILLS]
    windows += [slot((x, y - l / 2 + w / 2), (x, y + l / 2 - w / 2), w) for (x, y), w, l in STRAP_SLOTS]
    windows += [chevron((0.0, y), 9.0, 5.0, 4.4) for y in CHEVRON_Y]
    windows.append(rounded_poly(CROWN, 1.2))
    return Sheet("plate_top", P.T_TOP, outline, holes, windows)


ARM_GUIDE_R = 2.0
LUG_FILLET = 5.0
LUG_REACH = 10.5  # the lug's fillets start this far either side of it
PAD_FILLET = 9.0
ROOT_SLOT = (27.0, 51.0, 8.0)  # from, to, width
FANG = (8.6, 15.4, 4.0)  # base radius, tip radius, half-width of the windows in the motor pad


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
        # 0.01 mm short of touching: the two arcs are then joined by a common tangent the belt can find
        gap = ((cx - P.ARM_LEN) ** 2 + cy**2) ** 0.5 - (P.MOTOR_PAD_R + PAD_FILLET + 0.01)
        lo, hi = (mid, hi) if gap > 0 else (lo, mid)
    return centre((lo + hi) / 2)


def _fang(center: XY, deg: float):
    """Tooth-shaped window pointing away from the motor centre."""
    base, tip, half = FANG
    ux, uy = cos(radians(deg)), sin(radians(deg))
    bx, by = center[0] + base * ux, center[1] + base * uy
    pts = [
        (center[0] + tip * ux, center[1] + tip * uy),
        (bx - half * uy, by + half * ux),
        (bx + half * uy, by - half * ux),
    ]
    return rounded_poly(pts, 1.0)


@lru_cache(maxsize=1)
def arm() -> Sheet:
    """The arm in its own coordinates: stack bolt at the origin, motor at (ARM_LEN, 0).
    Its width follows `sizing.arm_width`; the brace lug stands on the flank that faces the other arm."""
    length, hw, g = P.ARM_LEN, P.arm_half_width, ARM_GUIDE_R
    belly = hw(sizing.EDGE_U)  # the widest station is one round of this radius, centred on the axis

    def guide(u: float, side: int, link: float = 0.0):
        return lobe((u, side * (hw(u) - g)), g, link)

    lug_v = -(hw(P.LUG_U) + P.LUG_OFFSET)
    fx, fy = _pad_fillet()
    nodes = [
        guide(sizing.ROOT_U, -1),
        lobe((sizing.EDGE_U, 0.0), belly),
        guide(P.LUG_U - LUG_REACH, -1, LUG_FILLET),
        lobe((P.LUG_U, lug_v), P.LUG_R, LUG_FILLET),
        guide(P.LUG_U + LUG_REACH, -1),
        bite((fx, -fy), PAD_FILLET),  # the taper runs straight into this fillet, and the fillet into the pad
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
        *_holes("arm_outer", "arm bolt + nyloc", [(P.ARM_BOLT_U[1], 0)]),
        *_holes("brace", "brace bolt + nyloc", [(P.LUG_U, lug_v)]),
    ]
    c = (length, 0)
    root = slot(
        (ROOT_SLOT[0], 0.0), (ROOT_SLOT[1], 0.0), ROOT_SLOT[2]
    )  # between the two arm bolts, inside the sandwich
    windows = [*F.motor_slots(c), circle(c, P.MOTOR_BORE_D), *(_fang(c, 90 * k) for k in range(4)), root]
    return Sheet("arm", P.T_ARM, outline, holes, windows, count=4)


BRACE_BELLY = (28.0, 6.0)  # the brace is 12 mm wide between these stations, 10 mm at the lugs
CLAW = (2.2, 3.4, 2.6, 9.0)  # half-run in X, half-run in Y, width, pitch of the three slashes


@lru_cache(maxsize=1)
def brace() -> Sheet:
    """Side brace between the lugs of the front and rear arm, flat along +Y, centred on the origin."""
    y_end, (y_b, r_b) = P.LUG[1], BRACE_BELLY
    lo, b_lo, b_hi, hi = (
        lobe((0, -y_end), P.LUG_R),
        lobe((0, -y_b), r_b),
        lobe((0, y_b), r_b),
        lobe((0, y_end), P.LUG_R),
    )
    outline = face(belt([lo, b_lo, b_hi, hi, b_hi, b_lo]))
    holes = [
        *_holes("lug", "bolt into the arm lug", [(0, -y_end), (0, y_end)]),
        *_holes("accessory", "skid, LED strip or antenna tube", [(0, -P.BRACE_ACC_Y), (0, P.BRACE_ACC_Y)]),
    ]
    dx, dy, w, pitch = CLAW
    windows = [slot((-dx, k * pitch - dy), (dx, k * pitch + dy), w) for k in (-1, 0, 1)]
    return Sheet("brace", P.T_BRACE, outline, holes, windows, count=2)


SHEETS = {
    "plate_bottom": bottom_skin,
    "plate_mid": deck,
    "plate_top": top_plate,
    "arm": arm,
    "brace": brace,
    "core_nose": core_nose,
    "core_tail": core_tail,
    "puck": puck,
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
                "where": f"stack bolts: through the {floor:g} mm floor, nut on the deck, then the stack",
            },
            {
                "item": "M3 x 16 button head",
                "qty": 8,
                "where": "inner arm bolts (4) and mid standoffs (4): from below through the floor into the standoffs",
            },
            {
                "item": "M3 x 18 button head",
                "qty": 4,
                "where": "nose and tail standoffs: through a talon, then the floor",
            },
            {
                "item": "M3 x 20 button head",
                "qty": 3,
                "where": "turret bracket: two into the front standoffs, the third takes a nyloc on the deck",
            },
            {
                "item": "M3 x 16 button head + nyloc",
                "qty": 8,
                "where": "outer arm bolts (4), braces to the arm lugs (4)",
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
