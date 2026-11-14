"""What Zvir carries besides the usual FPV gear: a companion computer, and a second camera
on a servo under the nose. These envelopes go into the renders and into every clearance check.

The turret's dimensions live here because three things share them: the servo and camera
envelopes, the printed bracket and cradle, and the talons that must stay out of their way.
"""

from math import radians, tan

from build123d import Axis, Cone, Cylinder, Part, Pos, Vector
from zhalo import equipment as E
from zhalo import params as P
from zhalo.accessories.kit import FIT, disc, prism_x

box = E.box

# --- companion computer ---------------------------------------------------------------------------
SBC_BOARD = (56.0, 85.0, 1.4)  # the "credit card" boards: Raspberry Pi 3/4/5, Radxa ROCK 3C/4C+/5C
SBC_HOLES = (49.0, 58.0)  # M2.5; the pattern starts 3.5 mm in from the SD-card edge
ZERO_BOARD = (30.0, 65.0, 1.4)  # Raspberry Pi Zero 2 W, Radxa Zero 3
ZERO_HOLES = (23.0, 58.0)
SBC_FRONT_Y = -32.0  # the SD-card edge, just behind the stack standoffs
SBC_LIFT = 5.0  # board underside above the deck
SBC_Z = P.Z_DECK + SBC_LIFT
SBC_PORTS_H = 16.5  # the USB and Ethernet block: the tallest thing on the board


def sbc_holes(pattern: tuple[float, float] = SBC_HOLES) -> list[tuple[float, float]]:
    y = SBC_FRONT_Y - 3.5
    return [(sx * pattern[0] / 2, yy) for yy in (y, y - pattern[1]) for sx in (1, -1)]


def sbc() -> Part:
    """A Raspberry Pi 4/5 with its plugs to the tail: board, port block, GPIO header, SoC."""
    w, l, t = SBC_BOARD
    y1, y0, z = SBC_FRONT_Y, SBC_FRONT_Y - l, SBC_Z + t
    board = box(-w / 2, y0, SBC_Z, w / 2, y1, z)
    ports = box(-w / 2 + 1.5, y0 - 2.5, z - 0.01, w / 2 - 1.5, y0 + 19.0, z + SBC_PORTS_H)
    header = box(w / 2 - 6.5, y1 - 58.0, z - 0.01, w / 2 - 1.0, y1 - 7.0, z + 8.5)
    soc = box(-12.0, y1 - 38.0, z - 0.01, 6.0, y1 - 20.0, z + 6.0)
    return board + ports + header + soc


SBC_TOP = SBC_Z + SBC_BOARD[2] + SBC_PORTS_H

# --- chin turret ---------------------------------------------------------------------------------
TILT_Y, TILT_Z = 121.0, -21.5  # the tilt axis runs along X through this point, under the nose
TILT_RANGE = (-90.0, 15.0)  # straight down ... a little above the horizon
TILT_SHOWN = -35.0  # how the renders and the assembly show it

# SG90-class 9 g servo; s is measured along the shaft from the bottom of the case
SERVO_BODY = (22.8, 12.4, 22.8)  # along Y, along Z, along the shaft
SERVO_EARS = (32.6, 2.6)  # span, thickness
SERVO_EAR_S = 15.9  # underside of the ears
SERVO_HOLES = 27.8
SERVO_SHAFT_BACK = 6.0  # shaft axis behind the front end of the case
SERVO_BOSS_S, SERVO_TIP_S = 27.2, 30.0
HORN_S = (29.3, 31.0)  # the horn's arm, pressed on the shaft
HORN_HUB_D = 7.0
SERVO_EAR_X = -18.5  # the bracket face the ears bear on; the shaft points to +X

# the cradle, left to right
POCKET = 1.9  # depth of the horn pocket in the cradle's left wall
WALL_L, WALL_R = 4.0, 5.0
CAM_BOARD = (25.0, 24.0, 1.0)  # Raspberry Pi Camera Module 2 / 3 and the many boards that copy its outline
CAM_HOLES = (21.0, 12.5)  # M2; the upper row is 2 mm below the top edge
CAM_LENS_H = -2.4  # lens centre below the middle of the board
CAM_LENS_TIP = 11.5  # Module 3 Wide: the longest of them
LENS_D = 12.4
X_L = SERVO_EAR_X + (HORN_S[0] - SERVO_EAR_S) - 0.1  # outer face of the left wall
X_IN = (X_L + WALL_L, X_L + WALL_L + CAM_BOARD[0] + 2 * FIT)  # between the walls
X_R = X_IN[1] + WALL_R
CAM_X = (X_IN[0] + X_IN[1]) / 2
BOARD_F = 3.0  # front face of the camera board ahead of the tilt axis
SPACER_T, PLAY = 2.0, 0.2
CHEEK_X = (X_R + SPACER_T + PLAY, X_R + SPACER_T + PLAY + 3.5)  # the bracket's pivot cheek


def tilted(part: Part, tilt: float) -> Part:
    """A part drawn about the tilt axis (lens along +Y, axis through the origin) -> its place on the frame."""
    return part.rotate(Axis.X, tilt).translate(Vector(0.0, TILT_Y, TILT_Z))


def servo() -> Part:
    l, w, h = SERVO_BODY
    x0 = SERVO_EAR_X - SERVO_EAR_S
    y1 = TILT_Y + SERVO_SHAFT_BACK
    y0, yc = y1 - l, y1 - l / 2
    body = box(x0, y0, TILT_Z - w / 2, x0 + h, y1, TILT_Z + w / 2)
    span, t = SERVO_EARS
    ears = box(SERVO_EAR_X, yc - span / 2, TILT_Z - w / 2, SERVO_EAR_X + t, yc + span / 2, TILT_Z + w / 2)
    axis = (TILT_Y, TILT_Z)
    boss = prism_x(disc(axis, 12.0), x0 + h - 0.01, x0 + SERVO_BOSS_S)
    hub = prism_x(disc(axis, HORN_HUB_D), x0 + SERVO_BOSS_S - 0.01, x0 + HORN_S[1])
    return body + ears + boss + hub


def cv_camera_local(grow: float = 0.0) -> Part:
    """Camera board, sensor block, lens and ribbon socket, drawn about the tilt axis."""
    w, h, t = CAM_BOARD
    board = box(
        CAM_X - w / 2 - grow, BOARD_F - t - grow, -h / 2 - grow, CAM_X + w / 2 + grow, BOARD_F + grow, h / 2 + grow
    )
    block = box(CAM_X - 4.5, BOARD_F - 0.01, CAM_LENS_H - 4.5, CAM_X + 4.5, BOARD_F + 5.5, CAM_LENS_H + 4.5)
    lens = Pos(CAM_X, BOARD_F + 5.49, CAM_LENS_H) * Cylinder(
        LENS_D / 2, CAM_LENS_TIP - 5.49, rotation=(-90, 0, 0), align=E.MIN_Z
    )
    socket = box(CAM_X - 10.5, BOARD_F - t - 2.9, -h / 2, CAM_X + 10.5, BOARD_F - t + 0.01, -h / 2 + 5.5)
    return board + block + lens + socket


def cv_camera(tilt: float = TILT_SHOWN, grow: float = 0.0) -> Part:
    return tilted(cv_camera_local(grow), tilt)


def view_cone(tilt: float, half_angle: float = 38.0, reach: float = 120.0) -> Part:
    """What the lens sees: a cone from the lens face (38 deg half-angle covers a 76 deg diagonal field)."""
    r0 = LENS_D / 2
    cone = Cone(r0, r0 + reach * tan(radians(half_angle)), reach, rotation=(-90, 0, 0), align=E.MIN_Z)
    return tilted(Pos(CAM_X, BOARD_F + CAM_LENS_TIP + 0.1, CAM_LENS_H) * cone, tilt)


def register() -> None:
    """Put the payload among the frame's equipment."""
    E.EXTRA.update(
        {
            "sbc": (sbc(), "pcb", 1.0),
            "servo": (servo(), "motor", 1.0),
            "cv_camera": (cv_camera(), "camera", 1.0),
        }
    )
