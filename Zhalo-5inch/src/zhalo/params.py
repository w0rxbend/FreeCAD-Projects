"""Every dimension of the frame, in millimetres.

Datum: origin = centre of the 30.5 x 30.5 stack, +X right, +Y front (camera), +Z up,
Z = 0 is the underside of the bottom plate. Change a value here and everything
(plates, arms, accessories, checks, exports) follows.
"""

from math import atan2, degrees, hypot, sqrt

XY = tuple[float, float]

# --- airframe -----------------------------------------------------------------------------
WHEELBASE = 225.0  # motor to diagonally opposite motor
MOTOR_X = 88.0  # wide-X: the motors sit further apart sideways, so the camera sees less prop
MOTOR_Y = sqrt((WHEELBASE / 2) ** 2 - MOTOR_X**2)  # 70.09
PROP_D = 129.54  # 5.1 inch
PROP_MARGIN = 2.5  # nothing of the body or an accessory comes closer to a prop tip than this
PROP_KEEPOUT_R = PROP_D / 2 + PROP_MARGIN
PROP_Z = (24.0, 36.0)  # height band the blades can occupy on a 22xx/23xx motor, flex included

# --- sheet stock ----------------------------------------------------------------------------
T_BOTTOM = 2.5
T_ARM = 5.0
T_MID = 2.0
T_TOP = 2.0
T_BRACE = 2.0
STACK_STANDOFF_H = 28.0  # on the mid plate; the bay standoffs are this + T_ARM + T_MID = 35
STANDOFF_OD = 5.0  # round knurled M3 standoff

Z_BOTTOM = 0.0
Z_ARM = Z_BOTTOM + T_BOTTOM  # 2.5  bay floor, arm underside
Z_MID = Z_ARM + T_ARM  # 7.5  arm top, mid-plate underside
Z_DECK = Z_MID + T_MID  # 9.5  stack floor
Z_TOP = Z_DECK + STACK_STANDOFF_H  # 37.5 top-plate underside
Z_ROOF = Z_TOP + T_TOP  # 39.5 battery deck
BAY_STANDOFF_H = Z_TOP - Z_ARM  # 35.0
Z_BRACE = Z_ARM - T_BRACE  # 0.5  braces bolt under the arm lugs

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
S: XY = (STACK_PITCH / 2, STACK_PITCH / 2)  # stack bolt, front right
_ARM_LEN = hypot(MOTOR_X - S[0], MOTOR_Y - S[1])  # stack bolt to motor centre, 91.1
ARM_DIR: XY = ((MOTOR_X - S[0]) / _ARM_LEN, (MOTOR_Y - S[1]) / _ARM_LEN)
ARM_ANGLE = degrees(atan2(ARM_DIR[1], ARM_DIR[0]))  # 37.0 deg from +X
ARM_LEN = _ARM_LEN


def on_arm(u: float, v: float = 0.0) -> XY:
    """Front-right arm coordinates (u along the arm from the stack bolt, v to its left) -> frame XY."""
    return S[0] + u * ARM_DIR[0] - v * ARM_DIR[1], S[1] + u * ARM_DIR[1] + v * ARM_DIR[0]


ARM_BOLT_U = (16.0, 30.0)  # the two arm bolts, measured from the stack bolt
B: XY = on_arm(ARM_BOLT_U[0])  # (28.03, 24.88) inner arm bolt, carries the 28 mm standoff
C: XY = on_arm(ARM_BOLT_U[1])  # (39.21, 33.31) outer arm bolt + nyloc
F: XY = (15.5, 56.0)  # front bay standoff (camera)
R: XY = (14.5, -70.0)  # rear bay standoff (antenna)
A1: XY = (15.5, 38.0)  # accessory hole in both long plates; takes an optional fifth standoff pair
AL: XY = (24.5, 0.0)  # accessory lobe on the top plate
NOSE_HOLE: XY = (0.0, 72.0)  # bumper screw in the bottom plate

# --- arm ------------------------------------------------------------------------------------
ARM_W_ROOT = 15.0
ARM_W_NECK = 11.0
ARM_NECK_U = ARM_LEN - 21.0  # where the taper ends and the motor pad fillet starts
ARM_GAP = 0.1  # each root stays this far from the X and Y axes: 0.2 mm between neighbours
STACK_SLOT_W = 3.4  # open slot round the stack bolt: an arm slides out without touching the stack
MOTOR_PAD_R = 16.0
MOTOR_PATTERN = 16.0  # 16 x 16 M3: every 22xx / 23xx five-inch motor
MOTOR_SLOT = 1.0  # the holes are short slots, so a slightly off pattern still bolts on
MOTOR_BORE_D = 6.0
LUG_U = 48.0  # brace lug position along the arm
LUG_OFFSET = 3.4  # lug hole centre outside the arm flank
LUG_R = 4.6


def arm_half_width(u: float) -> float:
    """Linear taper from the stack bolt (root width) to the neck."""
    if u <= 0:
        return ARM_W_ROOT / 2
    if u >= ARM_NECK_U:
        return ARM_W_NECK / 2
    return ARM_W_ROOT / 2 + (ARM_W_NECK - ARM_W_ROOT) / 2 * u / ARM_NECK_U


LUG: XY = on_arm(LUG_U, -(arm_half_width(LUG_U) + LUG_OFFSET))  # lug hole, front-right arm
BRACE_ACC_Y = 8.0  # two accessory holes in the middle of each brace

# --- derived tables -------------------------------------------------------------------------
MOTORS: dict[str, XY] = {
    "front_right": (MOTOR_X, MOTOR_Y),
    "front_left": (-MOTOR_X, MOTOR_Y),
    "rear_right": (MOTOR_X, -MOTOR_Y),
    "rear_left": (-MOTOR_X, -MOTOR_Y),
}


def quad(p: XY) -> list[XY]:
    """A front-right point mirrored into all four quadrants (FR, FL, RR, RL)."""
    return [(p[0], p[1]), (-p[0], p[1]), (p[0], -p[1]), (-p[0], -p[1])]


def pair(p: XY) -> list[XY]:
    return [(p[0], p[1]), (-p[0], p[1])]


# name -> (x, y, z0, height)
STANDOFFS: dict[str, tuple[float, float, float, float]] = {}
for _tag, _p, _z0, _h in (
    ("front", F, Z_ARM, BAY_STANDOFF_H),
    ("stack_front", B, Z_DECK, STACK_STANDOFF_H),
    ("stack_rear", (B[0], -B[1]), Z_DECK, STACK_STANDOFF_H),
    ("rear", R, Z_ARM, BAY_STANDOFF_H),
):
    STANDOFFS[f"standoff_{_tag}_right"] = (_p[0], _p[1], _z0, _h)
    STANDOFFS[f"standoff_{_tag}_left"] = (-_p[0], _p[1], _z0, _h)
