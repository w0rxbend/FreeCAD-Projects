"""The five carbon parts of Shershen. Every bolt sits where Zhalo has it; only the shapes differ.

Style rules, taken from frames that look fast standing still:
  - flowing outlines with a few sharp points (wing tips, mandibles, a barbed stinger);
  - windows that lean back: fishbone triangles along a solid spine instead of full chevrons;
  - arm tips drawn out to a point, with triangular windows aimed along the arm.
"""

from functools import lru_cache
from math import cos, radians, sin

from zhalo import frame as F
from zhalo import params as P
from zhalo.frame import B_F, B_R, C_F, C_R, Sheet, _holes, _link, _square
from zhalo.outline import XY, belt, bite, chevron, circle, face, lobe, mirrored, polygon, rounded_poly, scallop, slot

WING_TIP = (39.0, -6.0)  # swept back: the leading edge is longer than the trailing one
WING_R = 2.4
MANDIBLE = (11.2, 77.5)  # fork tips of the top plate, hooked towards each other
FANG = (10.5, 77.0)  # forked nose of the bottom plate
BARB = (8.0, -80.5)
STING_Y = -93.0
SPINE = 2.6  # half-width of the solid strip down the middle of the fishbone
FISH_Y = (-54.0, -43.0, -32.0, -21.0, -10.0, 1.0, 12.0, 23.0, 34.0)
WINDOW_R = 1.0


def hexagon(center: XY, af: float, r: float = WINDOW_R):
    """Flat-top hexagonal window by its across-flats size."""
    rc = af / 3**0.5
    return rounded_poly(
        [(center[0] + rc * cos(radians(60 * k)), center[1] + rc * sin(radians(60 * k))) for k in range(6)], r
    )


def fishbone(y: float) -> list:
    """A pair of swept triangles either side of the spine: one segment of the hornet's abdomen."""
    right = [(SPINE, y + 4.5), (SPINE + 7.0, y - 3.5), (SPINE, y - 4.5)]
    return [rounded_poly(right, WINDOW_R), rounded_poly([(-x, yy) for x, yy in reversed(right)], WINDOW_R)]


def _both(points: list[XY], r: float = WINDOW_R) -> list:
    return [rounded_poly(points, r), rounded_poly([(-x, y) for x, y in reversed(points)], r)]


@lru_cache(maxsize=1)
def top_plate() -> Sheet:
    r = P.LOBE_R
    n_r, b_r, tip, b_f = lobe(P.R, r), lobe(B_R, r), lobe(WING_TIP, WING_R), lobe(B_F, r)
    a1, f, prong = lobe(P.A1, r), lobe(P.F, r), lobe(MANDIBLE, 2.6)
    right = [
        _link(n_r, scallop(n_r, b_r, 12.0)),  # the wasp waist
        b_r,  # straight trailing edge out to the wing tip
        _link(tip, scallop(tip, b_f, 2.0)),  # leading edge, slightly hollow
        _link(b_f, scallop(b_f, a1, 5.5)),
        _link(a1, scallop(a1, f, 2.2)),
        f,
        prong,
    ]
    outline = face(belt(mirrored(right, top=bite((0.0, 58.5), 9.0), bottom=bite(*F.TAIL_NOTCH))))
    holes = [
        *_holes("front_standoff", "35 mm standoff; action-camera mount front screws", P.pair(P.F)),
        *_holes("stack_standoff", "28 mm standoff", P.quad(P.B)),
        *_holes("rear_standoff", "35 mm standoff; GPS / XT60 mount screws", P.pair(P.R)),
        *_holes("accessory", "action-camera mount rear screws / optional standoff", P.pair(P.A1)),
        *_holes("side_accessory", "accessory hole at the wing root", P.pair(P.AL)),
    ]
    windows = [w for y in FISH_Y for w in fishbone(y)]
    windows += _both([(30.5, 13.0), (37.0, -5.0), (30.5, -14.0)], 1.5)  # wing windows
    windows.append(hexagon((0.0, 44.2), 6.0))  # the one comb cell on the head
    windows += [slot((x, y - l / 2 + w / 2), (x, y + l / 2 - w / 2), w) for (x, y), w, l in F.STRAP_SLOTS]
    return Sheet("plate_top", P.T_TOP, outline, holes, windows)


@lru_cache(maxsize=1)
def bottom_plate() -> Sheet:
    r, leg = P.LOBE_R, P.LEG_R
    sting, barb = lobe((0.0, STING_Y), 1.4), lobe(BARB, 1.6)
    n_r, v_r = lobe(P.R, r), lobe(F.VTX_REAR, r)
    c_r, c_f, f, fang = lobe(C_R, leg), lobe(C_F, leg), lobe(P.F, r), lobe(FANG, 2.6)
    right = [
        barb,
        n_r,
        _link(v_r, scallop(v_r, c_r, 8.5)),
        _link(c_r, scallop(c_r, c_f, C_R[0] + leg - F.WAIST_X)),
        _link(c_f, scallop(c_f, f, 5.0)),
        f,
        fang,
    ]
    sting = _link(sting, scallop(sting, barb, 2.0))
    outline = face(belt(mirrored(right, top=bite((0.0, 82.0), 7.0), bottom=sting)))
    holes = [
        *_holes("stack", "30.5 stack bolt, also clamps the arm roots", P.quad(P.S)),
        *_holes("arm_inner", "arm bolt + 28 mm standoff", P.quad(P.B)),
        *_holes("arm_outer", "arm bolt + nyloc", P.quad(P.C)),
        *_holes("front_standoff", "35 mm standoff, head", P.pair(P.F)),
        *_holes("rear_standoff", "35 mm standoff, tail fins", P.pair(P.R)),
        *_holes("accessory", "optional 35 mm standoff / accessory", P.pair(P.A1)),
        *_holes("vtx_30p5", "analog VTX 30.5 x 30.5", _square((0, P.VTX_BAY_Y), P.VTX_PITCH_LARGE)),
        *_holes("vtx_20", "analog VTX 20 x 20", _square((0, P.VTX_BAY_Y), P.VTX_PITCH_SMALL)),
    ]
    windows = [
        hexagon((0.0, 0.0), 13.0, 2.0),
        hexagon((0.0, P.VTX_BAY_Y), 10.0, 1.5),
        chevron((0, 27.5), 8.5, 5.0, 4.4),  # the capacitor saddle ties down through these two
        chevron((0, 38.5), 8.5, 5.0, 4.4),
        rounded_poly([(-8.5, 51.5), (8.5, 51.5), (8.5, 61.5), (-8.5, 61.5)], 2.5),
        rounded_poly([(-4.0, -73.0), (4.0, -73.0), (0.0, -84.5)], WINDOW_R),  # arrow in the stinger
    ]
    return Sheet("plate_bottom", P.T_BOTTOM, outline, holes, windows)


@lru_cache(maxsize=1)
def mid_plate() -> Sheet:
    leg = P.LEG_R
    rr, fr, fl, rl = (lobe((sx * P.C[0], sy * P.C[1]), leg) for sx, sy in ((1, -1), (1, 1), (-1, 1), (-1, -1)))
    side = scallop(rr, fr, P.C[0] + leg - F.WAIST_X)
    end = scallop(fr, fl, P.C[1] + leg - F.WAIST_Y)
    outline = face(belt([_link(rr, side), _link(fr, end), _link(fl, side), _link(rl, end)]))
    holes = [
        *_holes("stack", "30.5 stack bolt", P.quad(P.S)),
        *_holes("arm_inner", "arm bolt + 28 mm standoff", P.quad(P.B)),
        *_holes("arm_outer", "arm bolt + nyloc", P.quad(P.C)),
    ]
    return Sheet("plate_mid", P.T_MID, outline, holes, [hexagon((0.0, 0.0), 16.0, 2.0)])


TIP_REACH = 21.0  # the pointed tip stands this far beyond the motor centre
TIP_R = 2.6


@lru_cache(maxsize=1)
def arm() -> Sheet:
    """Zhalo's arm with a pointed tip: stack bolt at the origin, motor at (ARM_LEN, 0)."""
    length, hw, g = P.ARM_LEN, P.arm_half_width, F.ARM_GUIDE_R

    def guide(u: float, side: int, link: float = 0.0):
        return lobe((u, side * (hw(u) - g)), g, link)

    lug_v = -(hw(P.LUG_U) + P.LUG_OFFSET)
    pad = lobe((length, 0), P.MOTOR_PAD_R)
    nodes = [
        guide(-45, -1),
        guide(0, -1),
        guide(P.LUG_U - 9.5, -1, F.LUG_FILLET),
        lobe((P.LUG_U, lug_v), P.LUG_R, F.LUG_FILLET),
        guide(P.LUG_U + 9.5, -1),
        guide(P.ARM_NECK_U, -1, F.PAD_FILLET),
        pad,  # round the motor on one side ...
        lobe((length + TIP_REACH, 0), TIP_R),  # ... out to the point ...
        _link(pad, F.PAD_FILLET),  # ... and back round the other side
        guide(P.ARM_NECK_U, 1),
        guide(0, 1),
        guide(-45, 1),
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
        *_holes("brace", "brace bolt", [(P.LUG_U, lug_v)]),
    ]
    c = (length, 0)
    windows = [
        *F.motor_slots(c),
        circle(c, P.MOTOR_BORE_D),
        rounded_poly([(length + 9.8, -3.4), (length + 17.8, 0.0), (length + 9.8, 3.4)], WINDOW_R),  # aimed at the tip
        rounded_poly([(length - 9.8, 3.2), (length - 17.0, 0.0), (length - 9.8, -3.2)], WINDOW_R),  # aimed at the root
        F._rotated_diamond((length, 10.2), 5.4, 6.6, 90),
        F._rotated_diamond((length, -10.2), 5.4, 6.6, 270),
    ]
    return Sheet("arm", P.T_ARM, outline, holes, windows, count=4)


FIN_TIP = (8.5, -5.0)  # the brace's winglet, swept like the wings above it


@lru_cache(maxsize=1)
def brace() -> Sheet:
    """Side brace with a winglet on its outboard edge; the bolt holes are Zhalo's."""
    y_end, y_acc = P.LUG[1], P.BRACE_ACC_Y
    lo, tip, hi = lobe((0, -y_end), P.LUG_R), lobe(FIN_TIP, 1.8), lobe((0, y_end), P.LUG_R)
    holes = [
        *_holes("lug", "bolt into the arm lug", [(0, -y_end), (0, y_end)]),
        *_holes("accessory", "skid / accessory", [(0, -y_acc), (0, y_acc)]),
    ]
    return Sheet("brace", P.T_BRACE, face(belt([lo, tip, hi])), holes, [], count=2)


SHEETS = {"plate_bottom": bottom_plate, "plate_mid": mid_plate, "plate_top": top_plate, "arm": arm, "brace": brace}
