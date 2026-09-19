"""Frame parameters (mm) and the wheelbase -> arm length derivation.

Datum: origin = centre of the central 30.5 stack square, +X right, +Y front,
+Z up, Z = 0 lower face of the bottom plate.
"""

from math import cos, radians, sin, sqrt

WHEELBASE = 303.0  # primary: motor centre to diagonally opposite motor centre

PLATE_T = 2.0
ARM_T = 5.0
TOP_CLEARANCE = 25.0  # mid-plate top face to top-plate underside
Z_BOTTOM = 0.0
Z_ARM = PLATE_T
Z_MID = PLATE_T + ARM_T
Z_TOP = Z_MID + PLATE_T + TOP_CLEARANCE

STANDOFF_OD = 5.0
STANDOFF_BORE = 3.0
STANDOFF_H_SHORT = TOP_CLEARANCE  # sits on the mid plate
STANDOFF_H_REAR = Z_TOP - Z_ARM  # rear tips sit on the bottom plate (no arm there)

D_M3 = 3.2  # ISO 273 fine: stack, standoff, motor and arm bolts
D_M2 = 2.2  # 20x20 and 25.5x25.5 patterns
D_RELIEF_MID = 5.5  # mid-plate bores on the r = 18 diamond
D_ACC_BOTTOM = 4.5
D_ACC_TOP = 4.6
D_MOTOR_BORE = 6.5
D_SMA = 6.5  # SMA / RP-SMA bulkhead
D_STACK_NOTCH = 3.4  # arm-root notch relief (3.2 + 0.2 for the front/rear local offset)

PITCH_30 = 30.5
PITCH_20 = 20.0
PITCH_25 = 25.5
FWD_BAY_Y = 61.5  # forward bay centre (mid plate)
FWD_25_OFFSET = 7.25  # 25.5 square centre = (0, FWD_BAY_Y + FWD_25_OFFSET)
REAR_BAY_Y = -65.5  # rear 20x20 centre (bottom plate)
REAR_25_CENTER_Y = -73.0
SMA_XY = (0.0, -56.5)  # top plate
SMA_HOLE = True

# Motor pattern as traced: 4 x M3 on a Ø19 circle at 45° (13.435 mm adjacent).
# Common 2806.5/2807 motors use 16x16 (circle 22.63) or 19x19 (26.87, does not fit
# the 24 mm paddle); change this value for a different motor.
MOTOR_BOLT_CIRCLE = 19.0

# Arm profile (sibling-calibrated values).
ROOT_WIDTH = 35.0
ROOT_DEPTH = 29.0
SHAFT_WIDTH = 12.0
PADDLE_WIDTH = 24.0
WAIST_WIDTH = 20.5
TIP_EXTENSION = 25.0
NECK_LENGTH = 25.0
ROOT_HOLE_SPACING = 13.75
ROOT_HOLE_ANGLE = 142.7  # degrees from local +X to the outer root bolt
DIAMOND_W, DIAMOND_H, DIAMOND_OFFSET = 7.0, 10.0, 15.5
DIAMOND_FILLET = 0.63
STACK_NOTCH_XY = (1.93, -15.68)  # arm-local axis of the stack bolt in the root notch

# Layout: arm root-hole midpoints and rotations (mirror X -> rotate Z -> translate).
FRONT_ROOT = (27.75, 25.0)
REAR_ROOT = (26.25, -26.5)
FRONT_ANGLE = 90 - 6.5 - ROOT_HOLE_ANGLE  # -59.2
REAR_ANGLE = -90 - 1.5 - (180 - ROOT_HOLE_ANGLE)  # -128.8
FRONT_TIP = (19.0, 109.0)  # standoff pairs
REAR_TIP = (16.5, -94.0)

# name -> (origin_x, origin_y, angle_deg, mirror_x)
ARM_PLACEMENTS: dict[str, tuple[float, float, float, bool]] = {
    "arm_front_right": (FRONT_ROOT[0], FRONT_ROOT[1], FRONT_ANGLE, False),
    "arm_front_left": (-FRONT_ROOT[0], FRONT_ROOT[1], -FRONT_ANGLE, True),
    "arm_rear_right": (REAR_ROOT[0], REAR_ROOT[1], REAR_ANGLE, True),
    "arm_rear_left": (-REAR_ROOT[0], REAR_ROOT[1], -REAR_ANGLE, False),
}


def place(x: float, y: float, placement: tuple[float, float, float, bool]) -> tuple[float, float]:
    """Arm-local (x, y) -> frame XY for one placement."""
    ox, oy, angle, mirror = placement
    a = radians(angle)
    if mirror:
        x = -x
    return ox + x * cos(a) - y * sin(a), oy + x * sin(a) + y * cos(a)


def root_holes() -> tuple[tuple[float, float], tuple[float, float]]:
    """Arm-local root bolt axes: (outer, inner)."""
    r, a = ROOT_HOLE_SPACING / 2, radians(ROOT_HOLE_ANGLE)
    return (r * cos(a), r * sin(a)), (-r * cos(a), -r * sin(a))


def arm_length(wheelbase: float = WHEELBASE) -> float:
    """Root-hole midpoint to motor centre that gives the diagonal wheelbase.

    Only the arm length depends on the wheelbase; roots and plate holes stay put.
    """
    a = sin(radians(-FRONT_ANGLE)) + sin(radians(-REAR_ANGLE))
    b = cos(radians(-FRONT_ANGLE)) - cos(radians(-REAR_ANGLE))
    dx0, dy0 = FRONT_ROOT[0] + REAR_ROOT[0], FRONT_ROOT[1] - REAR_ROOT[1]
    qa, qb, qc = a * a + b * b, 2 * (dx0 * a + dy0 * b), dx0 * dx0 + dy0 * dy0 - wheelbase**2
    return (-qb + sqrt(qb * qb - 4 * qa * qc)) / (2 * qa)


ROOT_TO_MOTOR = arm_length()
