"""The numbers Strila is built on. They are set before the engine is imported.

Where they come from (see README, "Calculation"):
  - 6 mm arms, 16 mm wide where they leave the sandwich, 9 mm at the motor: against Zhalo's
    5 mm arm this roughly doubles the load an arm takes in both directions and raises its
    first bending frequency by about two thirds, for half a gram of carbon;
  - the outer arm bolt moved out from 30 to 36 mm: the plates hold the arm further out, so
    the free length, and with it every bending stress, drops by a tenth;
  - a floor made of two thin skins with the arms as the core between them, instead of one
    thick plate: the same carbon, an order of magnitude more bending stiffness.
"""

T_ARM = 6.0
T_BOTTOM = 2.0  # lower skin: takes the ground
T_DECK = 1.5  # upper skin: the floor every board stands on
T_TOP = 2.0
STANDOFF_H = 28.0  # all eight standoffs are the same and stand on the deck; 25 is too low for a 22 mm camera
ARM_BOLT_U = (16.0, 36.0)
LEG_R = 6.0  # the sandwich legs are 12 mm wide
PAD_R = 16.0
NECK_BACK = 19.0

ROOT_U = -45.0  # where the root would end if its neighbours did not cut it off at the centre lines
ROOT_W = 13.5  # width there; the arm widens steadily from here to the sandwich edge
EDGE_W = 16.0  # widest: where the sandwich lets go of the arm and the bending moment peaks
NECK_W = 10.5  # just before the motor pad: sized so a side load stresses the neck and the root alike
EDGE_U = ARM_BOLT_U[1] + LEG_R  # 42: station where the plates end


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
