"""Sfera 7" ("the sphere"): a cargo quad.

A round barrel of a body on a true-X layout, so the load hangs under the centre of thrust and
in the one place no propeller blows on. A printed cargo deck with a grid of captive nuts, a
servo release, four tall legs, a bumper round the whole rim, and bays for a stack, a camera,
a Zero-size companion computer and two more boards. It runs on the Zhalo engine with its
own dimensions, so every geometric check of that engine applies.

Importing this package configures the engine. Nothing else of the engine may be imported
before it, because the engine's modules read the dimensions when they load.
"""

from zhalo import params

from sfera import sizing


def _width(u: float) -> float:
    return sizing.arm_width(u, params.ARM_LEN - sizing.NECK_BACK)


params.configure(
    WHEELBASE=sizing.WHEELBASE,
    MOTOR_X=sizing.MOTOR_X,
    PROP_D=sizing.PROP_D,
    PROP_Z=sizing.PROP_Z,
    T_BOTTOM=sizing.T_BOTTOM,
    T_ARM=sizing.T_ARM,
    T_MID=sizing.T_DECK,
    T_TOP=sizing.T_TOP,
    STACK_STANDOFF_H=sizing.STANDOFF_H,
    BAY_ON_DECK=True,
    BRACES=False,
    EXTRA_STANDOFFS={
        "nose": sizing.NOSE,
        "side_front": sizing.SIDE,
        "side_rear": (sizing.SIDE[0], -sizing.SIDE[1]),
    },
    ARM_BOLT_U=sizing.ARM_BOLT_U,
    LEG_R=sizing.LEG_R,
    MOTOR_PAD_R=sizing.PAD_R,
    MOTOR_PATTERN=sizing.MOTOR_PATTERN,
    MOTOR_BORE_D=sizing.MOTOR_BORE,
    ARM_NECK_BACK=sizing.NECK_BACK,
    ARM_WIDTH=_width,
    F=sizing.CAM,
    R=(sizing.NOSE[0], -sizing.NOSE[1]),
    A1=sizing.A1,
    VTX_BAY_Y=sizing.VTX_Y,
)

from zhalo import accessories, checks, design, frame  # noqa: E402 - must follow configure()
from zhalo import equipment as E  # noqa: E402

from sfera import profiles  # noqa: E402

# what the frame carries: a 7 inch drive and a 6S pack along the top
E.MOTOR_D, E.MOTOR_H = 34.5, 21.0  # 2806.5 / 2807
E.PROP_T = 8.0
E.BATTERY_SIZE = (46.0, 132.0, 46.0)  # 6S 3000-3300 mAh
E.BATTERY_Y = 0.0
E.VTX_LARGE_AT = (sizing.SIDE_BAY_X, 0.0)  # a 30.5 x 30.5 VTX goes in the right-hand side bay, under the gills

design.NAME = "Sfera 7-inch"
design.SLUG = "sfera"
design.DOCUMENT = "Sfera-7inch"
design.MASS_LIMIT = 330.0
design.TIP_MASS = sizing.TIP_MASS
design.BOM = profiles.bill_of_materials
design.EXTRA_COLORS.update(
    hull=(0.80, 0.81, 0.83),  # pale hull grey
    accent=(0.93, 0.42, 0.10),  # one warm marking colour
    tpu=(0.15, 0.16, 0.18),
    petg=(0.90, 0.90, 0.88),
    aluminium=(0.72, 0.74, 0.78),
)

frame.SHEETS.clear()
frame.SHEETS.update(profiles.SHEETS)
_Z = (params.Z_ARM, params.Z_MID)
for _name, _xy in profiles.PUCKS.items():
    frame.EXTRA[_name] = ("puck", _Z[0], _xy)
_BOTTOM = ("plate_bottom", params.Z_BOTTOM, params.Z_ARM)
_DECK = ("plate_mid", params.Z_MID, params.Z_DECK)
_TOP = ("plate_top", params.Z_TOP, params.Z_ROOF)
_ARM = ("arm_{q}", *_Z)
checks.EXTRA_BOLTS.update(
    {
        "camera_puck": (params.pair(params.F), 3.0, [("puck_camera_{side}", *_Z)]),
        "tail_puck": (params.pair(params.R), 3.0, [("puck_tail_{side}", *_Z)]),
        "nose_standoff": (params.pair(sizing.NOSE), 3.0, [_BOTTOM, ("puck_nose_{side}", *_Z), _DECK, _TOP]),
        "side_standoff": (params.quad(sizing.SIDE), 3.0, [_BOTTOM, ("puck_side_{q}", *_Z), _DECK, _TOP]),
        "arm_leg": (params.quad(profiles.LEG_BOLT), 3.0, [_BOTTOM, _ARM, _DECK]),
    }
)
from zhalo.accessories import arm_guard, wire_clip  # noqa: E402

from sfera import payload  # noqa: E402

payload.register()
design.EXTRA_COLORS.update(cargo=(0.80, 0.62, 0.30))
design.EQUIPMENT.update(
    vtx="20 x 20 behind the camera; 30.5 x 30.5 or 20 x 20 in either side bay, under the gills",
    companion_computer="Zero-size board with 58 x 23 mm M2.5 holes (Raspberry Pi Zero / Zero 2 W, "
    "Radxa Zero / Zero 3W / 3E), across the rear bay",
    cargo="bolted to a 15 mm M3 grid, strapped, or slung from a servo release; legs clear a 90 x 90 x 45 mm load",
)
arm_guard.MOTOR_BASE_D = 34.6  # a 28xx motor
wire_clip.U = 118.0  # on the free part of the arm, towards the motor
design.COLOR_OF.update(arm_guard="accent")
design.EXTRA_RENDERS[:] = [
    ("belly", ((0.8, -1.0, -0.75), (0, 0, 1), False), 1.0, ()),
    ("stance", ((1.0, 0.35, 0.10), (0, 0, 1), False), 1.0, ()),
]
accessories.MODULES = (
    "sfera.accessories.hull",
    "sfera.accessories.bumper",
    "sfera.accessories.leg",
    "sfera.accessories.cargo",
    "sfera.accessories.sbc_tray",
    "camera_mount",
    "sfera.accessories.perch",
    "arm_guard",
    "sfera.accessories.pad",
    "wire_clip",
)
