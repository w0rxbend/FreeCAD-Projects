"""The numbers Sfera is built on. They are set before the engine is imported.

A cargo quad is sized from the load outwards:

  - the load hangs under the centre of thrust, so the body is round and the layout a true X:
    the same from every side, with the load in the one place no propeller blows on;
  - the body's widest point (the bulge of its barrel sides, 84.3 mm out) and the 7 inch
    propellers fix the motor circle at 177 mm: 2.5 mm between a blade tip and the hull;
  - the arm is the one already sized for Zvir (8 mm, 20 mm wide at the sandwich, 12 mm at the
    motor, 72 mm of free length), so the floor reaches out along each arm in a finger to hold
    the first 83 mm of it. See the README, "Calculation", for the finite-element figures.
"""

from math import asin, cos, degrees, radians, sin, sqrt

# --- airframe ---------------------------------------------------------------------------------
MOTOR_R = 177.0  # motor circle
WHEELBASE = 2 * MOTOR_R
MOTOR_X = MOTOR_R / sqrt(2)  # true X
PROP_D = 177.8  # 7 inch
PROP_Z = (28.0, 44.0)  # blade band on a 28xx motor, flex included

# --- sheet stock ------------------------------------------------------------------------------
T_ARM = 8.0
T_BOTTOM = 2.0  # lower skin: the cargo hangs from it
T_DECK = 1.5  # upper skin: the floor every board stands on
T_TOP = 2.0
STANDOFF_H = 35.0  # all fourteen standoffs are the same

# --- arm ----------------------------------------------------------------------------------------
ARM_BOLT_U = (16.0, 75.0)
LEG_BOLT_U = 63.0  # a third bolt through every arm: with the outer one it carries a landing leg
LEG_R = 8.0  # the fingers of the floor are 16 mm wide
PAD_R = 18.5
MOTOR_PATTERN = 19.0  # 19 x 19 M3: 28xx motors
MOTOR_BORE = 8.0
NECK_BACK = 24.0
ROOT_U = -45.0
ROOT_W = 11.0  # inside the sandwich the arm is only a core
EDGE_W = 20.0  # widest: where the sandwich lets go of the arm
NECK_W = 12.0
EDGE_U = ARM_BOLT_U[1] + LEG_R  # 83: station where the fingers end
TIP_MASS = 62.0  # g: a 2806.5 / 2807 motor, a 7 inch prop, screws

# --- body ----------------------------------------------------------------------------------------
BODY_R = 80.0  # the carbon discs
RING_R = 74.0  # the eight rim standoffs stand on this circle, in four pairs
PAIR_X = 19.5  # half the distance between the two standoffs of a pair
PAIR_DEG = degrees(asin(PAIR_X / RING_R))  # 15.3: each pair sits this far either side of a main axis
PAIR_Y = RING_R * cos(radians(PAIR_DEG))
NOSE = (PAIR_X, PAIR_Y)  # nose pair; the tail pair mirrors it, the side pairs are it turned 90 deg
SIDE = (PAIR_Y, PAIR_X)
CAM = (15.5, 62.0)  # the camera's own pair, inside the nose pair
A1 = (15.5, 50.0)  # accessory holes in the top plate
VTX_Y = 43.0  # 20 x 20 VTX behind the camera
SIDE_BAY_X = 48.0  # middle of each side bay: 30.5 x 30.5 and 20 x 20 patterns
SBC_Y = -46.0  # middle of the companion computer, across the rear bay


def arm_width(u: float, neck_u: float) -> float:
    """Full width of the arm at station u (mm from the stack bolt): it swells to the sandwich
    edge, then tapers straight to the neck. `neck_u` is where the neck starts."""
    if u <= ROOT_U:
        return ROOT_W
    if u <= EDGE_U:
        return ROOT_W + (EDGE_W - ROOT_W) * (u - ROOT_U) / (EDGE_U - ROOT_U)
    if u >= neck_u:
        return NECK_W
    return EDGE_W + (NECK_W - EDGE_W) * (u - EDGE_U) / (neck_u - EDGE_U)


def polar(r: float, deg: float) -> tuple[float, float]:
    return r * cos(radians(deg)), r * sin(radians(deg))
