"""The numbers Zvir is built on. They are set before the engine is imported.

A seven-inch quad that carries a companion computer is half as heavy again as a racing
five-inch, its arms are half as long again, and its motors turn slower. That last point
sizes the arm. With a 62 g motor and prop on its end, a 6 mm arm of this length rings at
about 200 Hz: 12 000 RPM, the middle of the throttle, exactly where a camera platform
cruises. So (see `zhalo.structure`, `zhalo.fea` and the README, "Calculation"):

  - 8 mm arms, 20 mm wide where the sandwich lets go of them and 12 mm at the motor: the
    first bending frequency moves up to about 310 Hz, where the motors only get near full throttle;
  - the outer arm bolt 62 mm out: the plates hold the first 70 mm of every arm, which
    shortens the free length, and with it every bending stress, by a tenth;
  - side braces between the front and the rear arm of each side: they take the fore-and-aft
    load a long arm is weakest against.
"""

# --- airframe ---------------------------------------------------------------------------------
WHEELBASE = 328.0
MOTOR_X = 126.0  # wide: the body between the props is 74 mm across, and the camera sees no blade
PROP_D = 177.8  # 7 inch
PROP_Z = (28.0, 44.0)  # blade band on a 28xx motor, flex included

# --- sheet stock ------------------------------------------------------------------------------
T_ARM = 8.0
T_BOTTOM = 2.0  # lower skin
T_DECK = 1.5  # upper skin: the floor every board stands on
T_TOP = 2.0
T_BRACE = 3.0
STANDOFF_H = 35.0  # all fourteen standoffs are the same

# --- arm ----------------------------------------------------------------------------------------
ARM_BOLT_U = (16.0, 62.0)
LEG_R = 8.0  # the sandwich legs are 16 mm wide
PAD_R = 18.5
MOTOR_PATTERN = 19.0  # 19 x 19 M3: 28xx motors
MOTOR_BORE = 8.0
NECK_BACK = 24.0
ROOT_U = -45.0  # where the root would end if its neighbours did not cut it off at the centre lines
ROOT_W = 11.0  # inside the sandwich the arm is only a core: it need not be wide there
EDGE_W = 20.0  # widest: where the sandwich lets go of the arm and the bending moment peaks
NECK_W = 12.0
EDGE_U = ARM_BOLT_U[1] + LEG_R  # 70: station where the plates end
LUG_U = 96.0  # brace lug
TIP_MASS = 62.0  # g: a 2806.5 / 2807 motor, a 7 inch prop, screws

# --- body hard points (right-hand side) -----------------------------------------------------------
F = (15.5, 112.0)  # front standoffs: the FPV camera hangs between them
NOSE = (29.5, 108.0)  # nose-corner standoffs: front talons, front of the side panels
MID = (33.0, 62.0)  # one pair ahead of the stack and one behind it (mirrored in Y)
R = (32.0, -128.0)  # tail standoffs: rear talons, rear of the side panels
A1 = (15.5, 94.0)  # accessory holes (action-camera mount)
NOSE_BOLT = (0.0, 116.0)  # third bolt of the turret bracket
VTX_Y = 52.0


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
