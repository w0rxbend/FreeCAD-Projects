"""Every dimension of the frame, in millimetres.

Datum: origin = centre of the 30.5 x 30.5 stack, +X right, +Y front (camera), +Z up,
Z = 0 is the underside of the bottom plate. Change a value here and everything
(plates, arms, accessories, checks, exports) follows.

The values below are Zhalo's. A sibling design that needs other numbers calls `configure()`
once, before it imports any other module of this package.
"""

from collections.abc import Callable
from math import atan2, degrees, hypot, sqrt

XY = tuple[float, float]

# ============================ inputs ============================================================
# --- airframe -----------------------------------------------------------------------------
WHEELBASE = 225.0  # motor to diagonally opposite motor
MOTOR_X = 88.0  # wide-X: the motors sit further apart sideways, so the camera sees less prop
PROP_D = 129.54  # 5.1 inch
PROP_MARGIN = 2.5  # nothing of the body or an accessory comes closer to a prop tip than this
PROP_Z = (24.0, 36.0)  # height band the blades can occupy on a 22xx/23xx motor, flex included

# --- sheet stock ----------------------------------------------------------------------------
T_BOTTOM = 2.5
T_ARM = 5.0
T_MID = 2.0
T_TOP = 2.0
T_BRACE = 2.0
STACK_STANDOFF_H = 28.0  # on the mid plate
STANDOFF_OD = 5.0  # round knurled M3 standoff
BAY_ON_DECK = False  # False: the front and rear standoffs stand on the bottom plate and are longer
BRACES = True  # side braces between the front and rear arm of each side

# --- holes ----------------------------------------------------------------------------------
D_M3 = 3.2
D_M2 = 2.2
LOBE_R = 4.8  # carbon round every M3: 3.2 mm of material outside the hole
LEG_R = 5.2

# --- electronics patterns -----------------------------------------------------------------
STACK_PITCH = 30.5  # SpeedyBee F405 V3/V4 + BLS 50/55 A 4-in-1
VTX_BAY_Y = -46.0  # analog VTX: 20 x 20 (TX800 class) and 30.5 x 30.5 (Rush Tank / Unify HV class)
VTX_PITCH_SMALL = 20.0
VTX_PITCH_LARGE = 30.5

# --- body hard points (right-hand side, mirrored in X) -------------------------------------
ARM_BOLT_U = (16.0, 30.0)  # the two arm bolts, measured along the arm from the stack bolt
F: XY = (15.5, 56.0)  # front bay standoff (camera)
R: XY = (14.5, -70.0)  # rear bay standoff (antenna)
A1: XY = (15.5, 38.0)  # accessory hole in both long plates; takes an optional fifth standoff pair
AL: XY = (24.5, 0.0)  # accessory lobe on the top plate
NOSE_HOLE: XY = (0.0, 72.0)  # bumper screw in the bottom plate

# --- arm ------------------------------------------------------------------------------------
ARM_W_ROOT = 15.0
ARM_W_NECK = 11.0
ARM_NECK_BACK = 21.0  # the taper ends this far short of the motor centre; the pad fillet starts there
ARM_WIDTH: Callable[[float], float] | None = None  # full width at station u, replacing the straight taper
ARM_GAP = 0.1  # each root stays this far from the X and Y axes: 0.2 mm between neighbours
STACK_SLOT_W = 3.4  # open slot round the stack bolt: an arm slides out without touching the stack
MOTOR_PAD_R = 16.0
MOTOR_PATTERN = 16.0  # 16 x 16 M3: every 22xx / 23xx five-inch motor
MOTOR_SLOT = 1.0  # the holes are short slots, so a slightly off pattern still bolts on
MOTOR_BORE_D = 6.0
LUG_U = 48.0  # brace lug position along the arm
LUG_OFFSET = 3.4  # lug hole centre outside the arm flank
LUG_R = 4.6
BRACE_ACC_Y = 8.0  # two accessory holes in the middle of each brace

_INPUTS = frozenset(name for name in dir() if name.isupper() and not name.startswith("_"))

# ============================ derived ===========================================================
MOTOR_Y = PROP_KEEPOUT_R = 0.0
Z_BOTTOM = Z_ARM = Z_MID = Z_DECK = Z_TOP = Z_ROOF = Z_BAY = Z_BRACE = BAY_STANDOFF_H = 0.0
S: XY = (0.0, 0.0)  # stack bolt, front right
ARM_LEN = ARM_ANGLE = ARM_NECK_U = 0.0
ARM_DIR: XY = (1.0, 0.0)
B: XY = (0.0, 0.0)  # inner arm bolt, carries a stack standoff
C: XY = (0.0, 0.0)  # outer arm bolt + nyloc
LUG: XY = (0.0, 0.0)  # brace lug hole, front-right arm
MOTORS: dict[str, XY] = {}
STANDOFFS: dict[str, tuple[float, float, float, float]] = {}  # name -> (x, y, z0, height)


def on_arm(u: float, v: float = 0.0) -> XY:
    """Front-right arm coordinates (u along the arm from the stack bolt, v to its left) -> frame XY."""
    return S[0] + u * ARM_DIR[0] - v * ARM_DIR[1], S[1] + u * ARM_DIR[1] + v * ARM_DIR[0]


def arm_half_width(u: float) -> float:
    """Half the arm's width at station u: a straight taper from the stack bolt to the neck,
    unless the design supplies its own width law."""
    if ARM_WIDTH is not None:
        return ARM_WIDTH(u) / 2
    if u <= 0:
        return ARM_W_ROOT / 2
    if u >= ARM_NECK_U:
        return ARM_W_NECK / 2
    return ARM_W_ROOT / 2 + (ARM_W_NECK - ARM_W_ROOT) / 2 * u / ARM_NECK_U


def quad(p: XY) -> list[XY]:
    """A front-right point mirrored into all four quadrants (FR, FL, RR, RL)."""
    return [(p[0], p[1]), (-p[0], p[1]), (p[0], -p[1]), (-p[0], -p[1])]


def pair(p: XY) -> list[XY]:
    return [(p[0], p[1]), (-p[0], p[1])]


def _derive() -> None:
    g = globals()
    g["MOTOR_Y"] = sqrt((WHEELBASE / 2) ** 2 - MOTOR_X**2)  # 70.09
    g["PROP_KEEPOUT_R"] = PROP_D / 2 + PROP_MARGIN

    g["Z_BOTTOM"] = 0.0
    g["Z_ARM"] = T_BOTTOM  # 2.5  arm underside
    g["Z_MID"] = Z_ARM + T_ARM  # 7.5  arm top, mid-plate underside
    g["Z_DECK"] = Z_MID + T_MID  # 9.5  stack floor
    g["Z_TOP"] = Z_DECK + STACK_STANDOFF_H  # 37.5 top-plate underside
    g["Z_ROOF"] = Z_TOP + T_TOP  # 39.5 battery deck
    g["Z_BAY"] = Z_DECK if BAY_ON_DECK else Z_ARM  # floor of the front and rear bays
    g["BAY_STANDOFF_H"] = Z_TOP - Z_BAY  # 35.0
    g["Z_BRACE"] = Z_ARM - T_BRACE  # 0.5  braces bolt under the arm lugs

    g["S"] = (STACK_PITCH / 2, STACK_PITCH / 2)
    length = hypot(MOTOR_X - S[0], MOTOR_Y - S[1])  # stack bolt to motor centre, 91.1
    g["ARM_LEN"] = length
    g["ARM_DIR"] = ((MOTOR_X - S[0]) / length, (MOTOR_Y - S[1]) / length)
    g["ARM_ANGLE"] = degrees(atan2(ARM_DIR[1], ARM_DIR[0]))  # 37.0 deg from +X
    g["ARM_NECK_U"] = ARM_LEN - ARM_NECK_BACK
    g["B"] = on_arm(ARM_BOLT_U[0])  # (28.03, 24.88)
    g["C"] = on_arm(ARM_BOLT_U[1])  # (39.21, 33.31)
    g["LUG"] = on_arm(LUG_U, -(arm_half_width(LUG_U) + LUG_OFFSET))

    g["MOTORS"] = {
        "front_right": (MOTOR_X, MOTOR_Y),
        "front_left": (-MOTOR_X, MOTOR_Y),
        "rear_right": (MOTOR_X, -MOTOR_Y),
        "rear_left": (-MOTOR_X, -MOTOR_Y),
    }
    standoffs = {}
    for tag, p, z0, h in (
        ("front", F, Z_BAY, BAY_STANDOFF_H),
        ("stack_front", B, Z_DECK, STACK_STANDOFF_H),
        ("stack_rear", (B[0], -B[1]), Z_DECK, STACK_STANDOFF_H),
        ("rear", R, Z_BAY, BAY_STANDOFF_H),
    ):
        standoffs[f"standoff_{tag}_right"] = (p[0], p[1], z0, h)
        standoffs[f"standoff_{tag}_left"] = (-p[0], p[1], z0, h)
    g["STANDOFFS"] = standoffs


def configure(**inputs) -> None:
    """Replace input dimensions for a sibling design and recompute everything derived from them.
    Call it before importing any other module of this package: they read these values on import."""
    unknown = sorted(set(inputs) - _INPUTS)
    assert not unknown, f"not input dimensions: {unknown}"
    globals().update(inputs)
    _derive()


_derive()
