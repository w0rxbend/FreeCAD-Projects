"""Zvir 7" ("the beast"): a computer-vision quad.

A wide rounded body with three bays on one deck (FPV camera and VTX, the stack, a Raspberry
Pi or Radxa), a servo turret under the nose that tilts a second camera from the horizon to
straight down, and four talon legs that keep the turret off the ground. It runs on the
Zhalo engine with its own dimensions, so every geometric check of that engine applies; the
arm is sized in `zhalo.structure` (beam model) and `zhalo.fea` (finite elements).

Importing this package configures the engine. Nothing else of the engine may be imported
before it, because the engine's modules read the dimensions when they load.
"""

from zhalo import params

from zvir import sizing


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
    T_BRACE=sizing.T_BRACE,
    STACK_STANDOFF_H=sizing.STANDOFF_H,
    BAY_ON_DECK=True,
    BRACES=True,
    EXTRA_STANDOFFS={
        "nose": sizing.NOSE,
        "mid_front": sizing.MID,
        "mid_rear": (sizing.MID[0], -sizing.MID[1]),
    },
    ARM_BOLT_U=sizing.ARM_BOLT_U,
    LEG_R=sizing.LEG_R,
    MOTOR_PAD_R=sizing.PAD_R,
    MOTOR_PATTERN=sizing.MOTOR_PATTERN,
    MOTOR_BORE_D=sizing.MOTOR_BORE,
    ARM_NECK_BACK=sizing.NECK_BACK,
    ARM_WIDTH=_width,
    LUG_U=sizing.LUG_U,
    LUG_OFFSET=3.6,
    LUG_R=5.0,
    BRACE_ACC_Y=42.0,
    F=sizing.F,
    R=sizing.R,
    A1=sizing.A1,
    NOSE_HOLE=sizing.NOSE_BOLT,
    VTX_BAY_Y=sizing.VTX_Y,
)

from zhalo import accessories, checks, design, frame  # noqa: E402 - must follow configure()
from zhalo import equipment as E  # noqa: E402

from zvir import profiles  # noqa: E402

# what the frame carries: a 7 inch drive and a long pack
E.MOTOR_D, E.MOTOR_H = 34.5, 21.0  # 2806.5 / 2807
E.PROP_T = 8.0
E.BATTERY_SIZE = (46.0, 140.0, 46.0)  # 6S 3000-4000 mAh LiPo, or a 6S2P 21700 pack
E.BATTERY_Y = 0.0

design.NAME = "Zvir 7-inch"
design.SLUG = "zvir"
design.DOCUMENT = "Zvir-7inch"
design.MASS_LIMIT = 320.0
design.TIP_MASS = sizing.TIP_MASS
design.BOM = profiles.bill_of_materials
design.EQUIPMENT.update(
    vtx="analog, 20 x 20 or 30.5 x 30.5 M3, front bay",
    companion_computer="85 x 56 mm board with 58 x 49 mm M2.5 holes (Raspberry Pi 3/4/5, Radxa ROCK 3C/4C+/5C), "
    "or a Zero-size board with 58 x 23 mm holes; rear bay",
    vision_camera="25 x 24 mm board with 21 x 12.5 mm M2 holes (Raspberry Pi Camera Module 2 / 3), on the chin turret",
    tilt_servo="9 g micro servo (SG90 / MG90S class), direct drive",
)
design.EXTRA_COLORS.update(
    accent=(0.55, 0.95, 0.10),  # acid green: the parts that take the hits, and the tag
    tpu=(0.13, 0.13, 0.15),
    petg=(0.92, 0.92, 0.90),  # the turret is rigid and printed light, so the camera stays cool in the sun
    aluminium=(0.20, 0.20, 0.22),  # black standoffs
)

frame.SHEETS.clear()
frame.SHEETS.update(profiles.SHEETS)
_Z = (params.Z_ARM, params.Z_MID)
frame.EXTRA.update({"core_nose": ("core_nose", _Z[0]), "core_tail": ("core_tail", _Z[0])})
for _sx, _side in ((1, "right"), (-1, "left")):
    for _sy, _end in ((1, "front"), (-1, "rear")):
        frame.EXTRA[f"puck_{_end}_{_side}"] = ("puck", _Z[0], (_sx * sizing.MID[0], _sy * sizing.MID[1]))
_BOTTOM = ("plate_bottom", params.Z_BOTTOM, params.Z_ARM)
_DECK = ("plate_mid", params.Z_MID, params.Z_DECK)
_TOP = ("plate_top", params.Z_TOP, params.Z_ROOF)
checks.EXTRA_BOLTS.update(
    {
        "front_core": (params.pair(params.F), 3.0, [("core_nose", *_Z)]),
        "rear_core": (params.pair(params.R), 3.0, [("core_tail", *_Z)]),
        "nose_standoff": (params.pair(sizing.NOSE), 3.0, [_BOTTOM, ("core_nose", *_Z), _DECK, _TOP]),
        "mid_standoff": (params.quad(sizing.MID), 3.0, [_BOTTOM, ("puck_{q}", *_Z), _DECK, _TOP]),
        "nose_bolt": ([sizing.NOSE_BOLT], 3.0, [_BOTTOM, ("core_nose", *_Z), _DECK]),
    }
)
from zhalo.accessories import arm_guard, wire_clip  # noqa: E402

from zvir import payload  # noqa: E402

payload.register()
arm_guard.MOTOR_BASE_D = 34.6  # a 28xx motor
wire_clip.U = 112.0  # between the brace lug and the motor
design.COLOR_OF.update(arm_guard="accent")
design.EXTRA_RENDERS[:] = [
    ("turret", ((0.75, 1.1, -0.42), (0, 0, 1), False), 0.42, ("turret",)),
    ("stance", ((1.0, 0.25, 0.12), (0, 0, 1), False), 1.0, ()),
]
accessories.MODULES = (
    "zvir.accessories.panels",
    "zvir.accessories.turret",
    "zvir.accessories.talon",
    "zvir.accessories.sbc_tray",
    "camera_mount",
    "zvir.accessories.crown",
    "arm_guard",
    "zvir.accessories.pad",
    "wire_clip",
    "gopro_mount",
)
