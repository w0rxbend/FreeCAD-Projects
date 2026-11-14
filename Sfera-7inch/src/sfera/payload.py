"""What Sfera carries besides the usual FPV gear: a Zero-size companion computer in the rear
bay and a load under the base. These envelopes go into the renders and the clearance checks.
"""

from build123d import Axis, Part, Plane, revolve
from zhalo import equipment as E
from zhalo import params as P

from sfera import sizing

box, cylinder = E.box, E.cylinder

# --- companion computer ---------------------------------------------------------------------------
ZERO_BOARD = (65.0, 30.0, 1.4)  # Raspberry Pi Zero / Zero 2 W, Radxa Zero / Zero 3W / 3E: across the bay
ZERO_HOLES = (58.0, 23.0)  # M2.5
SBC_LIFT = 5.0  # board underside above the deck
SBC_Z = P.Z_DECK + SBC_LIFT
SBC_PARTS_H = 3.5
SBC_TOP = SBC_Z + ZERO_BOARD[2] + SBC_PARTS_H


def sbc_holes() -> list[tuple[float, float]]:
    w, l = ZERO_HOLES
    return [(sx * w / 2, sizing.SBC_Y + sy * l / 2) for sy in (1, -1) for sx in (1, -1)]


def sbc() -> Part:
    w, l, t = ZERO_BOARD
    y = sizing.SBC_Y
    board = box(-w / 2, y - l / 2, SBC_Z, w / 2, y + l / 2, SBC_Z + t)
    parts = box(-w / 2 + 4.0, y - l / 2 + 4.0, SBC_Z + t - 0.01, w / 2 - 4.0, y + l / 2 - 4.0, SBC_TOP)
    return board + parts


# --- cargo -----------------------------------------------------------------------------------------
CARGO_Z = -6.0  # underside of the cargo plate: what a load is bolted or strapped against
CRATE = (90.0, 90.0, 45.0)  # the load the renders show and the legs are checked against
FEET_Z = -60.0
SHADOW_R = sizing.MOTOR_R - sizing.PROP_D / 2  # 88.1: nothing inside this circle is under a propeller


def crate() -> Part:
    w, l, h = CRATE
    return box(-w / 2, -l / 2, CARGO_Z - h, w / 2, l / 2, CARGO_Z)


# --- 9 g servo (SG90 class), for the release ------------------------------------------------------------
SERVO_BODY = (22.8, 12.4, 22.8)  # length, width, height along the shaft
SERVO_EARS = (32.6, 2.6)  # span, thickness
SERVO_EAR_S = 15.9  # underside of the ears above the bottom of the case
SERVO_HOLES = 27.8
SERVO_SHAFT_BACK = 6.0  # shaft axis behind the front end of the case
SERVO_BOSS_S = 27.2
HORN_S = (29.3, 31.0)  # the horn's arm, pressed on the shaft
HORN_R = 11.0  # the hole in the horn the link hooks into


def servo_upright() -> Part:
    """The servo with its shaft along +Z through the origin, Z = 0 at the underside of the ears,
    the case running back along -X."""
    l, w, h = SERVO_BODY
    x1 = SERVO_SHAFT_BACK
    body = box(x1 - l, -w / 2, -SERVO_EAR_S, x1, w / 2, h - SERVO_EAR_S)
    span, t = SERVO_EARS
    xc = x1 - l / 2
    ears = box(xc - span / 2, -w / 2, 0.0, xc + span / 2, w / 2, t)
    boss = cylinder(0.0, 0.0, h - SERVO_EAR_S - 0.01, SERVO_BOSS_S - SERVO_EAR_S, 12.0)
    hub = cylinder(0.0, 0.0, SERVO_BOSS_S - SERVO_EAR_S - 0.01, HORN_S[1] - SERVO_EAR_S, 7.0)
    return body + ears + boss + hub


def spin(profile, a0: float, a1: float) -> Part:
    """A profile drawn as (radius, z), swept about the Z axis from angle a0 to a1 (degrees)."""
    return revolve(Plane.XZ * profile, Axis.Z, a1 - a0).rotate(Axis.Z, a0)


def register() -> None:
    """Put the payload among the frame's equipment."""
    E.EXTRA.update({"sbc": (sbc(), "pcb", 1.0), "cargo": (crate(), "cargo", 0.45)})
