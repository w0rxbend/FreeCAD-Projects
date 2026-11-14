"""Every dimension of Vektor 7.5", in millimetres.

Datum: origin on the frame's centre line at the middle of the stack, +X right, +Y front (camera),
+Z up, Z = 0 the underside of the lower skin.

The frame is two carbon skins, each one piece from motor to motor, held 12 mm apart: the lower skin
(the keel) and the upper skin (the deck). Between them, along every arm, aluminium spacers; the arm
is therefore a box beam with two flanges instead of a solid bar. Above the deck, a 26 mm bay for the
flight controller, the VTX and the receiver; on top, the battery plate.
"""

from math import cos, radians, sin, sqrt

# --- airframe -------------------------------------------------------------------------------------
WHEELBASE = 320.0  # true X
ARM_R = WHEELBASE / 2  # centre to motor
PROP_D = 7.5 * 25.4  # 190.5
PROP_MARGIN = 2.5
MOTOR_D, MOTOR_H = 34.0, 21.0  # 2807 class

# --- stack-up ---------------------------------------------------------------------------------------
T_SKIN = 2.0  # both skins
CAVITY = 14.0  # between the skins: the height of the arms' webs, and room for a 4-in-1 ESC
BAY = 26.0  # above the deck: flight controller, VTX, receiver, camera
T_TOP = 2.0
Z_LOWER = 0.0
Z_UPPER = Z_LOWER + T_SKIN + CAVITY  # 16: underside of the upper skin
Z_DECK = Z_UPPER + T_SKIN  # 18: top of the deck, the motors stand here
Z_TOP = Z_DECK + BAY  # 44: underside of the battery plate
Z_ROOF = Z_TOP + T_TOP  # 46
PROP_Z = (Z_DECK + MOTOR_H - 1.0, Z_DECK + MOTOR_H + 11.0)  # 38..50: the band the blades sweep, flex included

# --- arm (a beam along the 45 deg diagonal; r = distance from the centre) ------------------------------
ARM_W_ROOT = 28.0  # width where the arm leaves the body
ARM_W_NECK = 18.0
ROOT_R = 44.0
NECK_R = 140.0
PAD_R = 19.0  # motor pad, upper skin
RING_R = 16.0  # the lower skin under the motor: a ring
RING_HOLE = 24.0  # through which all four motor screws go in
STATIONS = (52.0, 84.0, 112.0, 138.0)  # the truss bays lie between these
STATION_RIB = 6.0  # solid carbon either side of a spacer
CHORD = 4.8  # the truss windows stay this far inside the arm's edge (plus DIAG): 2 mm clear of the web slots
DIAG = 1.6  # half the width of a diagonal (plus the window rounding)
WINDOW_R = 1.2  # window corners
MOTOR_PATTERNS = (16.0, 19.0)  # 16x16 and 19x19 M3: slots cover both
MOTOR_BORE = 8.0
WIRE_SLOT = (132.0, 11.0, 5.0)  # where the motor wires come up out of the cavity: r, length, width

# --- the webs: what makes each arm a box ------------------------------------------------------------
T_WEB = 2.0  # carbon, two per arm, standing between the skins along the arm's edges (a 2 mm cutter cuts its slot)
WEB_INSET = 3.2  # the web's middle plane sits this far inside the arm's edge: 2.1 mm of carbon outside its slot
WEB_R = (40.0, 146.0)  # from where the body holds the arm to under the motor ring
TABS = 3  # tabs on each long edge of a web, into slots through the skin
TAB_L = 10.0
SLOT_W = T_WEB + 0.15  # the slots through the skins: a glue fit

# --- body ----------------------------------------------------------------------------------------------
BODY = [
    (0.0, 98.0),
    (20.0, 88.0),
    (34.0, 36.0),
    (34.0, -36.0),
    (20.0, -96.0),
    (0.0, -106.0),
]  # right half, nose to tail
BODY_ROUND = 5.0
STACK = 30.5
SPACER_D = 6.0  # round aluminium spacer between the skins
D_M3 = 3.2
STANDOFF_D = 5.0
BODY_POSTS = [
    (15.0, 76.0),
    (28.0, 0.0),
    (14.0, -80.0),
]  # right-hand side: a spacer between the skins + a standoff above
VTX_Y = -46.0  # analog VTX, 20 x 20 and 30.5 x 30.5, on the deck
RX_Y = -76.0  # receiver, on the deck behind the VTX

# --- battery plate --------------------------------------------------------------------------------------
TOP = [
    (0.0, 84.0),
    (12.0, 86.0),
    (22.0, 70.0),
    (24.0, 30.0),
    (36.0, 6.0),
    (36.0, -6.0),
    (24.0, -30.0),
    (22.0, -74.0),
    (14.0, -94.0),
    (0.0, -96.0),
]


def arm_dir(quad: str) -> tuple[float, float]:
    sx = 1.0 if "right" in quad else -1.0
    sy = 1.0 if "front" in quad else -1.0
    return sx * cos(radians(45)), sy * sin(radians(45))


def on_arm(quad: str, r: float, v: float = 0.0) -> tuple[float, float]:
    """A point r along the arm from the centre, v to its left (as seen looking out along it)."""
    ux, uy = arm_dir(quad)
    return r * ux - v * uy, r * uy + v * ux


def half_width(r: float) -> float:
    if r <= ROOT_R:
        return ARM_W_ROOT / 2
    if r >= NECK_R:
        return ARM_W_NECK / 2
    return ARM_W_ROOT / 2 + (ARM_W_NECK - ARM_W_ROOT) / 2 * (r - ROOT_R) / (NECK_R - ROOT_R)


QUADS = ("front_right", "front_left", "rear_right", "rear_left")
MOTORS = {q: on_arm(q, ARM_R) for q in QUADS}
PROP_KEEPOUT = PROP_D / 2 + PROP_MARGIN
_ = sqrt
