"""Every number that shapes Bolid. Millimetres; origin at the centre of the stack, +X right, +Y forward,
+Z up, Z = 0 the underside of the bottom plate.

Stack-up:  bottom plate 2 | arms 6 | press plate 2 | bay 22 (standoffs) | top plate 2.
The four arms are separate parts, clamped between the bottom plate and the press plate. Their roots
fill the four quarters of the body and bear on each other along the centre lines.
"""

from math import sqrt

# --- props and motors ----------------------------------------------------------------------------
PROP_D = 129.5  # 5.1 inch
PROP_MARGIN = 2.5
TIP_GAP_MIN = 20.0  # prop tip to prop tip: less and the props start eating each other's wash
WHEELBASE = 214.0  # motor to motor across the diagonal; analysis.wheelbase_study() picks it
MOTOR_D = 28.0  # 2207 / 2306 bell
MOTOR_H = 17.0  # base to top of the bell
MOTOR_HOLES = 16.0  # 16x16 M3
MOTOR_BORE = 7.0

# --- stack-up ------------------------------------------------------------------------------------
T_BOT, T_ARM, T_PRESS, BAY, T_TOP = 2.0, 6.0, 2.0, 22.0, 2.0
Z_BOT = 0.0
Z_ARM = Z_BOT + T_BOT  # 2
Z_PRESS = Z_ARM + T_ARM  # 8
Z_BAY = Z_PRESS + T_PRESS  # 10
Z_TOP = Z_BAY + BAY  # 32
Z_ROOF = Z_TOP + T_TOP  # 34
PROP_Z = (Z_PRESS + MOTOR_H + 0.5, Z_PRESS + MOTOR_H + 8.5)  # the band the blades sweep

# --- arms ----------------------------------------------------------------------------------------
U_MOTOR = WHEELBASE / 2
U_CLAMP = 48.0  # where the plates let go of the arm: the highest bending moment
W_CLAMP = 20.0  # arm width there
W_MIN = 12.0  # the narrowest the arm gets: torsion, a crash from the side, the motor wires' cover
PAD_D = 31.0  # the motor pad: the motor's own footprint and 2 mm of carbon round its bolts
U_BOLT = 40.0  # the arm's own bolt, besides the stack and standoff bolts
ROOT_GAP = 0.5  # half the gap between neighbouring roots


def arm_width(u: float) -> float:
    """The fully stressed taper: width falls with the bending moment F*(U_MOTOR - u) until W_MIN."""
    if u <= U_CLAMP:
        return W_CLAMP
    return max(W_MIN, W_CLAMP * (U_MOTOR - u) / (U_MOTOR - U_CLAMP))


U_TAPER_END = U_MOTOR - W_MIN / W_CLAMP * (U_MOTOR - U_CLAMP)

QUADS = ("front_right", "front_left", "rear_right", "rear_left")
_SIGN = {"front_right": (1, 1), "front_left": (-1, 1), "rear_right": (1, -1), "rear_left": (-1, -1)}


def arm_dir(quad: str) -> tuple[float, float]:
    sx, sy = _SIGN[quad]
    return sx / sqrt(2), sy / sqrt(2)


def sign(quad: str) -> tuple[int, int]:
    return _SIGN[quad]


def on_arm(quad: str, u: float, v: float = 0.0) -> tuple[float, float]:
    """A point u along the arm from the centre and v to its left."""
    dx, dy = arm_dir(quad)
    return (u * dx - v * dy, u * dy + v * dx)


MOTORS = {q: on_arm(q, U_MOTOR) for q in QUADS}
PROP_KEEPOUT = PROP_D / 2 + PROP_MARGIN

# --- body ----------------------------------------------------------------------------------------
# right half, nose to tail. CLAMP is what the arms, the press plate and the bottom plate share;
# the bottom plate alone runs on to TAIL, under the video transmitter.
CLAMP = [
    (0.0, 50.0),
    (10.0, 49.5),
    (17.0, 44.0),
    (21.0, 30.0),
    (23.5, 12.0),
    (24.0, 0.0),
    (23.5, -14.0),
    (21.0, -32.0),
    (19.5, -42.0),
    (0.0, -42.0),
]
TAIL = [(19.5, -42.0), (19.5, -78.0), (12.0, -86.0), (0.0, -87.0)]
BODY_ROUND = 4.0
TAIL_Y = -42.0

STACK = (30.5, 20.0)  # both stack patterns, M3
STANDOFFS = [(14.5, 30.0), (-14.5, 30.0), (14.0, -34.0), (-14.0, -34.0)]
STANDOFF_D = 5.0
D_M3 = 3.2
D_M2 = 2.2

TOP = [(0.0, 35.0), (11.0, 35.0), (19.0, 29.0), (18.5, 0.0), (18.0, -36.0), (12.0, -43.0), (0.0, -44.0)]
STRAP = (13.0, 20.0, 3.2)  # slots at x = +-13, as long as a 20 mm strap is wide, this wide
STRAP_Y = -16.0
GOPRO_HOLES = [(sx * 6.5, y) for y in (24.0, 31.0) for sx in (1, -1)]

VTX_Y = -62.7
VTX_HOLES = 25.5  # M2 on the bottom plate's tail
RX_Y = -30.0
COVER_BOLTS = [(0.0, -45.2)]  # engine cover, M2 from below; the wing's pylon holds its tail
WING_FEET = [(3.0, -80.7), (-3.0, -80.7)]  # the wing's pylon, 2x M3 from below
SPLITTER_HOLES = [(6.0, 46.0), (-6.0, 46.0)]
