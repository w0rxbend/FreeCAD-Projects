"""The carbon parts of Strila.

  plate_bottom  lower skin, 2 mm      } the floor: two skins with the arms and the two core
  plate_mid     deck (upper skin), 1.5 }  rims between them, bolted through into one sandwich
  core_nose / core_tail   6 mm rims that close the sandwich at both ends (cut from the arm sheet)
  arm           6 mm, four of them
  plate_top     2 mm

Shapes are deliberately plain: straight edges, one fillet radius, and every window the same
"pill" lying along the frame's length. The arms are solid between the sandwich and the motor.
"""

from functools import lru_cache

from build123d import Face, fillet
from zhalo import frame as F
from zhalo import params as P
from zhalo.frame import Sheet, _holes, _square
from zhalo.outline import XY, belt, bite, circle, face, lobe, mirrored, polygon, rounded_poly, slot

BODY_HALF = 24.0  # the floor is a straight 48 mm strip: 1.2 mm outside the ESC each side
FILLET = 6.0  # inside corners where a leg meets the body
CORNER = 5.0  # outside corners of the body
SHOULDER_Y = (-62.0, 50.0)  # where the strip starts to narrow towards the tail and the nose
NOSE = (9.5, 75.0)  # nose corner (the nose ends at Y 80)
TAIL = (11.0, -78.0)  # tail corner (the tail ends at Y -83)
TAIL_NOTCH = ((0.0, -85.5), 6.0)
RIM = 4.0  # width of the two core rims
PILL_W = 4.0


def pill(center: XY, length: float, width: float = PILL_W):
    """The one window shape: a slot lying along Y."""
    x, y = center
    return slot((x, y - (length - width) / 2), (x, y + (length - width) / 2), width)


def _leg_fillet(sy: int, front_edge: bool) -> XY:
    """Centre of the fillet between the body's straight side and one edge of a right-hand leg.
    sy: +1 front leg, -1 rear leg. front_edge: the leg's edge that faces away from the stack."""
    dx, dy = P.ARM_DIR[0], sy * P.ARM_DIR[1]
    nx, ny = (-dy, dx) if sy > 0 else (dy, -dx)  # normal pointing away from the stack (towards the bay)
    if not front_edge:
        nx, ny = -nx, -ny  # the other edge: normal pointing towards the waist
    cx_leg, cy_leg = P.C[0], sy * P.C[1]
    px, py = cx_leg + P.LEG_R * nx, cy_leg + P.LEG_R * ny  # a point on that edge
    cx = BODY_HALF + FILLET
    cy = py + (FILLET - (cx - px) * nx) / ny
    return cx, cy


def _body(inset: float = 0.0):
    """Outline of the floor (both skins share it). `inset` moves it inwards by that much."""
    r, f = CORNER - inset, FILLET + inset
    leg = P.LEG_R - inset
    right = [
        lobe(TAIL, r),
        lobe((BODY_HALF - CORNER, SHOULDER_Y[0]), r),
        bite(_leg_fillet(-1, True), f),
        lobe((P.C[0], -P.C[1]), leg),
        bite(_leg_fillet(-1, False), f),
        bite(_leg_fillet(1, False), f),
        lobe(P.C, leg),
        bite(_leg_fillet(1, True), f),
        lobe((BODY_HALF - CORNER, SHOULDER_Y[1]), r),
        lobe(NOSE, r),
    ]
    return face(belt(mirrored(right, bottom=bite(TAIL_NOTCH[0], TAIL_NOTCH[1] + inset))))


def _through_holes() -> list:
    return [
        *_holes("stack", "30.5 stack bolt, clamps the arm roots", P.quad(P.S)),
        *_holes("arm_inner", "arm bolt + standoff", P.quad(P.B)),
        *_holes("arm_outer", "arm bolt + nyloc", P.quad(P.C)),
        *_holes("front_standoff", "through the nose core into the standoff", P.pair(P.F)),
        *_holes("rear_standoff", "through the tail core into the standoff", P.pair(P.R)),
    ]


@lru_cache(maxsize=1)
def bottom_skin() -> Sheet:
    windows = [  # the lower skin is open under both bays: less weight, and the deck's screws can be reached
        rounded_poly([(-18.5, -64.5), (18.5, -64.5), (18.5, -27.5), (-18.5, -27.5)], 4.0),
        rounded_poly([(-16.0, 27.5), (16.0, 27.5), (16.0, 48.5), (-16.0, 48.5)], 4.0),
    ]
    return Sheet("plate_bottom", P.T_BOTTOM, _body(), _through_holes(), windows)


@lru_cache(maxsize=1)
def deck() -> Sheet:
    holes = [
        *_through_holes(),
        *_holes("accessory", "optional fifth standoff pair / accessory", P.pair(P.A1)),
        *_holes("vtx_30p5", "analog VTX 30.5 x 30.5", _square((0, P.VTX_BAY_Y), P.VTX_PITCH_LARGE)),
        *_holes("vtx_20", "analog VTX 20 x 20", _square((0, P.VTX_BAY_Y), P.VTX_PITCH_SMALL)),
    ]
    windows = [pill((-8.0, 37.0), 16.0), pill((8.0, 37.0), 16.0), pill((0.0, P.VTX_BAY_Y), 12.0)]
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


def _core(front: bool) -> Sheet:
    """Rim that fills the gap between the skins round the nose (or the tail), with a boss at each bolt."""
    far = 200.0
    rim = _body() - _body(RIM)
    y0 = SHOULDER_Y[1] - 0.5 if front else SHOULDER_Y[0] + 0.5
    half = (
        [(-far, y0), (far, y0), (far, far), (-far, far)]
        if front
        else [(-far, -far), (far, -far), (far, y0), (-far, y0)]
    )
    shape = rim & face(polygon(half))
    points = P.pair(P.F) if front else P.pair(P.R)
    for p in points:
        shape = shape + (face(circle(p, 2 * P.LOBE_R)) & _body())
    profile = _rounded(max(shape.faces(), key=lambda f: f.area))
    name = "core_nose" if front else "core_tail"
    purpose = "bolt through both skins into the standoff"
    return Sheet(name, P.T_ARM, Face(profile.outer_wire()), _holes("standoff", purpose, points), [])


@lru_cache(maxsize=1)
def core_nose() -> Sheet:
    return _core(True)


@lru_cache(maxsize=1)
def core_tail() -> Sheet:
    return _core(False)


TOP_FILLET = 8.0
TOP_KINK_Y = 44.0  # where the top plate's sides turn in, front and rear
TOP_WAIST_R = 6.0
TOP_WAIST_Y = 12.0


@lru_cache(maxsize=1)
def top_plate() -> Sheet:
    r = P.LOBE_R
    b_f, b_r = P.B, (P.B[0], -P.B[1])
    right = [
        lobe(P.R, r),
        bite((P.R[0] + r + TOP_FILLET, -TOP_KINK_Y), TOP_FILLET),
        lobe(b_r, r),
        bite((BODY_HALF + TOP_WAIST_R, -TOP_WAIST_Y), TOP_WAIST_R),  # between the stack standoffs the plate
        bite((BODY_HALF + TOP_WAIST_R, TOP_WAIST_Y), TOP_WAIST_R),  # is as wide as the floor under it
        lobe(b_f, r),
        bite((P.F[0] + r + TOP_FILLET, TOP_KINK_Y), TOP_FILLET),
        lobe(P.F, r),
        lobe((13.2, 75.5), 3.4),
    ]
    outline = face(belt(mirrored(right, top=bite((0.0, 58.0), 9.4), bottom=bite((0.0, -80.0), 8.0))))
    holes = [
        *_holes("front_standoff", "standoff; action-camera mount front screws", P.pair(P.F)),
        *_holes("stack_standoff", "standoff", P.quad(P.B)),
        *_holes("rear_standoff", "standoff; GPS / XT60 mount screws", P.pair(P.R)),
        *_holes("accessory", "action-camera mount rear screws / optional standoff", P.pair(P.A1)),
    ]
    windows = [pill((sx * 6.5, y), 15.0) for y in PILL_ROWS for sx in (1, -1)]
    windows += [slot((x, y - l / 2 + w / 2), (x, y + l / 2 - w / 2), w) for (x, y), w, l in F.STRAP_SLOTS]
    return Sheet("plate_top", P.T_TOP, outline, holes, windows)


PILL_ROWS = (-55.0, -33.0, -11.0, 11.0, 33.0)
ARM_GUIDE_R = 2.0
PAD_RELIEF_D = 5.5
PAD_FILLET = 8.0


def _pad_fillet() -> XY:
    """Centre (u, +v) of the fillet that is tangent both to the tapering flank and to the motor pad."""
    from strila import sizing

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


@lru_cache(maxsize=1)
def arm() -> Sheet:
    """The arm in its own coordinates: stack bolt at the origin, motor at (ARM_LEN, 0).
    Its width follows `sizing.arm_width`: it swells to the sandwich edge and tapers to the motor."""
    from strila import sizing

    length, hw, g = P.ARM_LEN, P.arm_half_width, ARM_GUIDE_R
    belly = hw(sizing.EDGE_U)  # the widest station is one round of this radius, centred on the axis

    def guide(u: float, side: int, link: float = 0.0):
        return lobe((u, side * (hw(u) - g)), g, link)

    fx, fy = _pad_fillet()
    nodes = [
        guide(sizing.ROOT_U, -1),
        lobe((sizing.EDGE_U, 0.0), belly),
        bite((fx, -fy), PAD_FILLET),  # the taper runs straight into this fillet, and the fillet into the pad
        lobe((length, 0), P.MOTOR_PAD_R),
        bite((fx, fy), PAD_FILLET),
        lobe((sizing.EDGE_U, 0.0), belly),
        guide(sizing.ROOT_U, 1),
    ]
    blank = face(belt(nodes))
    far = 400.0
    corners = ((P.ARM_GAP, P.ARM_GAP), (far, P.ARM_GAP), (far, far), (P.ARM_GAP, far))
    quadrant = face(polygon([F.frame_to_arm(*p) for p in corners]))
    stack_slot = face(slot((-45, 0), (0, 0), P.STACK_SLOT_W))
    outline = F._round_root(((blank & quadrant) - stack_slot).faces()[0])
    holes = [
        *_holes("arm_inner", "arm bolt + standoff", [(P.ARM_BOLT_U[0], 0)]),
        *_holes("arm_outer", "arm bolt + nyloc", [(P.ARM_BOLT_U[1], 0)]),
    ]
    c = (length, 0)
    # four round holes under the motor base: a gram off each arm where the carbon carries next to nothing
    relief = [circle((length + dx, dy), PAD_RELIEF_D) for dx, dy in ((10.2, 0), (-10.2, 0), (0, 10.2), (0, -10.2))]
    windows = [*F.motor_slots(c), circle(c, P.MOTOR_BORE_D), *relief]
    return Sheet("arm", P.T_ARM, outline, holes, windows, count=4)


SHEETS = {
    "plate_bottom": bottom_skin,
    "plate_mid": deck,
    "plate_top": top_plate,
    "arm": arm,
    "core_nose": core_nose,
    "core_tail": core_tail,
}
