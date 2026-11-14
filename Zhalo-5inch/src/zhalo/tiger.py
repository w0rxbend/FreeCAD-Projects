"""Carbon parts in the Tiger Beetle style, for the three frames that grew out of the owner's Tiger
Beetle (Tigerbee 5", Tigerbeetle V2 6" HD, Tigerbee 7" LR).

What the scanned frame gave them: a nose with two ears and a rounded bump between them, a tail that
ends in two small feet with a notch, a long top deck with a U-shaped camera fork at the front and
pairs of slanted windows down its length like chevrons, and arms with a diamond window past the motor.

What they do differently from it: a sandwich floor (two skins with the arms and two core rims between
them, the construction sized in Strila), a true X, eight equal standoffs on one deck, and arms sized
by calculation for each frame.

A design sets `STYLE` (and `ARM`) before it calls `sheets()`. Everything else comes from `zhalo.params`.
"""

from dataclasses import dataclass, replace
from functools import lru_cache
from math import cos, radians, sin

from build123d import Face, fillet

from zhalo import frame as F
from zhalo import params as P
from zhalo.frame import Sheet, _holes, _square
from zhalo.outline import XY, belt, bite, circle, face, lobe, mirrored, polygon, rounded_poly, scallop, slot


@dataclass
class Style:
    body_half: float  # the floor is a straight strip this wide either side between the legs
    shoulder_y: tuple[float, float]  # where it starts to narrow towards the tail and the nose
    ear: XY  # the nose's two ears (right-hand one)
    ear_r: float
    bump_y: float  # the rounded bump between the ears ends here
    bump_r: float
    foot: XY  # the tail's two feet
    foot_r: float
    tail_notch: tuple[XY, float]
    fillet: float = 6.0  # inside corners where a leg meets the body
    corner: float = 5.0
    rim: float = 4.0  # width of the two core rims between the skins
    nose_sag: float = 2.2  # how deep the dip between an ear and the bump is
    windows_bottom: tuple = ()  # rounded polygons cut from the lower skin (under the bays)
    deck_windows: tuple = ()  # and from the deck
    prong: XY = (13.2, 75.5)  # tip of the top plate's camera fork
    fork: tuple[XY, float] = ((0.0, 58.0), 9.4)
    top_tail_notch: tuple[XY, float] = ((0.0, -80.0), 8.0)
    chevron_rows: tuple[float, ...] = ()  # Y of each pair of slanted windows in the top plate
    chevron: tuple[float, float, float] = (5.0, 13.0, 4.5)  # x of the inner edge, length, width
    strap_slots: tuple = ()  # ((x, y), width, length) through the top plate


@dataclass
class Arm:
    root_u: float
    root_w: float
    edge_w: float  # widest: where the sandwich lets go of the arm
    neck_w: float
    diamond: tuple[float, float, float] = (10.6, 5.0, 6.4)  # distance past the motor centre, width, length
    pad_fillet: float = 8.0
    relief_d: float = 5.5


STYLE: Style | None = None
ARM: Arm | None = None


def edge_u() -> float:
    return P.ARM_BOLT_U[1] + P.LEG_R


def arm_width(u: float) -> float:
    """Full width of the arm at station u: it swells to the sandwich edge, then tapers to the neck."""
    a, e, n = ARM, edge_u(), P.ARM_LEN - P.ARM_NECK_BACK
    if u <= a.root_u:
        return a.root_w
    if u <= e:
        return a.root_w + (a.edge_w - a.root_w) * (u - a.root_u) / (e - a.root_u)
    if u >= n:
        return a.neck_w
    return a.edge_w + (a.neck_w - a.edge_w) * (u - e) / (n - e)


# --- floor -------------------------------------------------------------------------------------------
def _leg_fillet(sy: int, front_edge: bool, f: float) -> XY:
    dx, dy = P.ARM_DIR[0], sy * P.ARM_DIR[1]
    nx, ny = (-dy, dx) if sy > 0 else (dy, -dx)
    if not front_edge:
        nx, ny = -nx, -ny
    px, py = P.C[0] + P.LEG_R * nx, sy * P.C[1] + P.LEG_R * ny
    cx = STYLE.body_half + STYLE.fillet
    return cx, py + (STYLE.fillet - (cx - px) * nx) / ny


def body(inset: float = 0.0):
    """The floor's outline (both skins share it). `inset` moves it inwards; negative grows it."""
    s = STYLE

    def rr(r: float) -> float:  # an inset outline keeps every round cuttable with a 2 mm router bit
        return max(r - inset, 1.2)

    c, f, leg = rr(s.corner), s.fillet + inset, P.LEG_R - inset
    ear = lobe(s.ear, rr(s.ear_r))
    bump = lobe((0.0, s.bump_y - s.bump_r), rr(s.bump_r))
    ear = replace(
        ear, link=scallop(lobe(s.ear, s.ear_r), lobe((0.0, s.bump_y - s.bump_r), s.bump_r), s.nose_sag) + inset
    )
    foot = lobe(s.foot, rr(s.foot_r))
    right = [
        foot,
        lobe((s.body_half - s.corner, s.shoulder_y[0]), c),
        bite(_leg_fillet(-1, True, f), f),
        lobe((P.C[0], -P.C[1]), leg),
        bite(_leg_fillet(-1, False, f), f),
        bite(_leg_fillet(1, False, f), f),
        lobe(P.C, leg),
        bite(_leg_fillet(1, True, f), f),
        lobe((s.body_half - s.corner, s.shoulder_y[1]), c),
        ear,
    ]
    notch_c, notch_r = s.tail_notch
    return face(belt(mirrored(right, top=bump, bottom=bite(notch_c, notch_r + inset))))


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
    windows = [rounded_poly(list(w), 4.0) for w in STYLE.windows_bottom]
    return Sheet("plate_bottom", P.T_BOTTOM, body(), _through_holes(), windows)


@lru_cache(maxsize=1)
def deck() -> Sheet:
    holes = [
        *_through_holes(),
        *_holes("accessory", "optional fifth standoff pair / accessory", P.pair(P.A1)),
        *_holes("vtx_30p5", "VTX 30.5 x 30.5", _square((0, P.VTX_BAY_Y), P.VTX_PITCH_LARGE)),
        *_holes("vtx_20", "VTX 20 x 20", _square((0, P.VTX_BAY_Y), P.VTX_PITCH_SMALL)),
    ]
    windows = [rounded_poly(list(w), 3.0) for w in STYLE.deck_windows]
    return Sheet("plate_mid", P.T_MID, body(), holes, windows)


def _rounded(f: Face, r: float = 1.2) -> Face:
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
    """Rim that closes the sandwich round the nose (or the tail), with a boss at each standoff bolt."""
    far = 400.0
    rim = body() - body(STYLE.rim)
    y0 = STYLE.shoulder_y[1] - 0.5 if front else STYLE.shoulder_y[0] + 0.5
    half = (
        [(-far, y0), (far, y0), (far, far), (-far, far)]
        if front
        else [(-far, -far), (far, -far), (far, y0), (-far, y0)]
    )
    shape = rim & face(polygon(half))
    points = P.pair(P.F) if front else P.pair(P.R)
    for p in points:
        boss = face(circle(p, 2 * P.LOBE_R)) & body()
        if (boss & rim).area < 1e-3:  # the bolt sits further in than the rim reaches: join it with a web
            boss = boss + (face(slot(p, (p[0] + (1 if p[0] > 0 else -1) * 30.0, p[1]), 2 * P.LOBE_R)) & body())
        shape = shape + boss
    profile = _rounded(max(shape.faces(), key=lambda f: f.area))
    name = "core_nose" if front else "core_tail"
    return Sheet(name, P.T_ARM, Face(profile.outer_wire()), _holes("standoff", "bolt through both skins", points), [])


@lru_cache(maxsize=1)
def core_nose() -> Sheet:
    return _core(True)


@lru_cache(maxsize=1)
def core_tail() -> Sheet:
    return _core(False)


# --- top plate -----------------------------------------------------------------------------------------
def chevron_pair(y: float) -> list:
    """Two slanted windows, mirror images, leaning back from the centre line like a tiger's stripes."""
    x0, length, w = STYLE.chevron
    lean = 0.75  # how far back the outer end sits, per mm out
    pts = [
        (x0, y + w / 2),
        (x0 + length, y + w / 2 - length * lean),
        (x0 + length, y - w / 2 - length * lean),
        (x0, y - w / 2),
    ]
    right = rounded_poly(pts[::-1] if False else [pts[3], pts[2], pts[1], pts[0]], 1.5)
    left = rounded_poly([(-p[0], p[1]) for p in pts], 1.5)
    return [right, left]


@lru_cache(maxsize=1)
def top_plate() -> Sheet:
    s, r = STYLE, P.LOBE_R
    b_f, b_r = P.B, (P.B[0], -P.B[1])
    waist = scallop(lobe(b_r, r), lobe(b_f, r), 1.6)
    right = [
        replace(lobe(P.R, r), link=scallop(lobe(P.R, r), lobe(b_r, r), 2.5)),
        replace(lobe(b_r, r), link=waist),
        replace(lobe(b_f, r), link=scallop(lobe(b_f, r), lobe(P.F, r), 2.5)),
        lobe(P.F, r),
        lobe(s.prong, 3.4),
    ]
    outline = face(belt(mirrored(right, top=bite(*s.fork), bottom=bite(*s.top_tail_notch))))
    holes = [
        *_holes("front_standoff", "standoff; action-camera mount front screws", P.pair(P.F)),
        *_holes("stack_standoff", "standoff", P.quad(P.B)),
        *_holes("rear_standoff", "standoff; GPS / antenna mount screws", P.pair(P.R)),
        *_holes("accessory", "action-camera mount rear screws", P.pair(P.A1)),
    ]
    windows = [w for y in s.chevron_rows for w in chevron_pair(y)]
    windows += [slot((x, y - l / 2 + w / 2), (x, y + l / 2 - w / 2), w) for (x, y), w, l in s.strap_slots]
    return Sheet("plate_top", P.T_TOP, outline, holes, windows)


# --- arm -----------------------------------------------------------------------------------------------
def _pad_fillet() -> XY:
    a = ARM
    u0, w0, u1, w1 = edge_u(), a.edge_w / 2, P.ARM_NECK_U, a.neck_w / 2
    k = (w1 - w0) / (u1 - u0)
    norm = (1 + k * k) ** 0.5

    def centre(u: float) -> XY:
        return u + a.pad_fillet * (-k) / norm, w0 + k * (u - u0) + a.pad_fillet / norm

    lo, hi = u0, P.ARM_LEN
    for _ in range(60):
        mid = (lo + hi) / 2
        cx, cy = centre(mid)
        gap = ((cx - P.ARM_LEN) ** 2 + cy**2) ** 0.5 - (P.MOTOR_PAD_R + a.pad_fillet + 0.01)
        lo, hi = (mid, hi) if gap > 0 else (lo, mid)
    return centre((lo + hi) / 2)


def _diamond(center: XY, w: float, l: float):
    x, y = center
    return rounded_poly([(x + l / 2, y), (x, y + w / 2), (x - l / 2, y), (x, y - w / 2)], 1.2)


@lru_cache(maxsize=1)
def arm() -> Sheet:
    """The arm: stack bolt at the origin, motor at (ARM_LEN, 0). Past the motor, the Tiger Beetle's diamond."""
    a, length, hw, g = ARM, P.ARM_LEN, P.arm_half_width, 2.0
    belly = hw(edge_u())

    def guide(u: float, side: int):
        return lobe((u, side * (hw(u) - g)), g)

    fx, fy = _pad_fillet()
    nodes = [
        guide(a.root_u, -1),
        lobe((edge_u(), 0.0), belly),
        bite((fx, -fy), a.pad_fillet),
        lobe((length, 0), P.MOTOR_PAD_R),
        bite((fx, fy), a.pad_fillet),
        lobe((edge_u(), 0.0), belly),
        guide(a.root_u, 1),
    ]
    blank = face(belt(nodes))
    far = 600.0
    corners = ((P.ARM_GAP, P.ARM_GAP), (far, P.ARM_GAP), (far, far), (P.ARM_GAP, far))
    quadrant = face(polygon([F.frame_to_arm(*p) for p in corners]))
    stack_slot = face(slot((-45, 0), (0, 0), P.STACK_SLOT_W))
    outline = F._round_root(((blank & quadrant) - stack_slot).faces()[0])
    holes = [
        *_holes("arm_inner", "arm bolt + standoff", [(P.ARM_BOLT_U[0], 0)]),
        *_holes("arm_outer", "arm bolt + nyloc", [(P.ARM_BOLT_U[1], 0)]),
    ]
    c = (length, 0)
    off, w, l = a.diamond
    relief = [circle((length + dx * 10.2, dy * 10.2), a.relief_d) for dx, dy in ((-1, 0), (0, 1), (0, -1))]
    windows = [*F.motor_slots(c), circle(c, P.MOTOR_BORE_D), _diamond((length + off, 0.0), w, l), *relief]
    return Sheet("arm", P.T_ARM, outline, holes, windows, count=4)


def sheets() -> dict:
    return {
        "plate_bottom": bottom_skin,
        "plate_mid": deck,
        "plate_top": top_plate,
        "arm": arm,
        "core_nose": core_nose,
        "core_tail": core_tail,
    }


def bill_of_materials() -> dict:
    floor = P.T_BOTTOM + P.T_ARM + P.T_MID
    return {
        "carbon": [{"part": n, "qty": m().count, "thickness_mm": m().thickness} for n, m in sheets().items()],
        "standoffs": [
            {
                "item": f"M3 x {P.STACK_STANDOFF_H:g} mm round standoff, OD {P.STANDOFF_OD:g}",
                "qty": 8,
                "where": "all eight on the deck",
            }
        ],
        "screws": [
            {
                "item": "M3 x 30 (with the stack) + M3 nut",
                "qty": 4,
                "where": f"stack bolts through the {floor:g} mm floor",
            },
            {
                "item": "M3 x 18 button head",
                "qty": 8,
                "where": "inner arm bolts and nose/tail bolts, from below into the standoffs",
            },
            {"item": f"M3 x {floor + 5:.0f} button head + nyloc", "qty": 4, "where": "outer arm bolts"},
            {"item": "M3 x 8 button head", "qty": 8, "where": "top plate into the standoffs"},
            {"item": f"M3 x {P.T_ARM + 4:.0f}", "qty": 16, "where": "motors: check your motor's thread depth"},
        ],
    }


_ = (cos, radians, sin)
