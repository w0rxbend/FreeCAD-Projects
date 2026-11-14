"""Tigerbee 7" LR: a long-range seven-inch in the Tiger Beetle style.

A long-range quad cruises for twenty minutes at part throttle, so what matters is that the arms do
not ring at cruise revs, that the GPS hears the sky and not the video transmitter, and that both
radio links have their antennas clear. Hence: a true X (on a seven-inch the motors are far enough
out for it, and it flies the same in every direction), 8 mm arms held 70 mm out by the sandwich
floor, a GPS on a mast above the noise, the receiver's antenna on a rear arm and the VTX antenna at
the tail. From the Tiger Beetle it keeps the nose, the tail, the forked top deck with its chevrons
and the diamond past the motor.

Importing this package configures the engine; nothing else of the engine may be imported before it.
"""

from math import sqrt

from zhalo import params

WHEELBASE = 315.0
T_ARM = 8.0
STANDOFF_H = 30.0
TIP_MASS = 55.0  # g: a 2806.5 motor, a 7 inch prop, screws

params.configure(
    WHEELBASE=WHEELBASE,
    MOTOR_X=WHEELBASE / 2 / sqrt(2),  # true X
    PROP_D=7 * 25.4,
    PROP_Z=(28.0, 44.0),
    T_BOTTOM=2.0,
    T_ARM=T_ARM,
    T_MID=1.5,
    T_TOP=2.0,
    STACK_STANDOFF_H=STANDOFF_H,
    BAY_ON_DECK=True,
    BRACES=False,
    ARM_BOLT_U=(16.0, 62.0),
    LEG_R=8.0,
    MOTOR_PAD_R=18.5,
    MOTOR_PATTERN=19.0,
    MOTOR_BORE_D=8.0,
    ARM_NECK_BACK=24.0,
    F=(15.5, 70.0),
    R=(15.5, -88.0),
    A1=(15.5, 52.0),
    VTX_BAY_Y=-56.0,
)

from zhalo import accessories, checks, design, frame, tiger  # noqa: E402 - must follow configure()
from zhalo import equipment as E  # noqa: E402
from zhalo.accessories import arm_guard, camera_mount, tiger_antenna, wire_clip  # noqa: E402

tiger.ARM = tiger.Arm(root_u=-45.0, root_w=12.0, edge_w=20.0, neck_w=12.0, diamond=(12.6, 6.0, 8.0), relief_d=6.4)
params.ARM_WIDTH = tiger.arm_width
tiger.STYLE = tiger.Style(
    body_half=24.0,
    shoulder_y=(-78.0, 58.0),
    ear=(13.0, 80.0),
    ear_r=6.5,
    bump_y=95.0,
    bump_r=7.5,
    foot=(11.0, -100.0),
    foot_r=5.0,
    tail_notch=((0.0, -107.5), 6.0),
    windows_bottom=(
        ((-18.5, -82.0), (18.5, -82.0), (18.5, -40.0), (-18.5, -40.0)),
        ((-16.0, 42.0), (16.0, 42.0), (16.0, 58.0), (-16.0, 58.0)),
    ),
    deck_windows=(
        ((0.0, 36.0), (6.5, 47.0), (0.0, 58.0), (-6.5, 47.0)),
        ((-6.0, -62.0), (6.0, -62.0), (6.0, -50.0), (-6.0, -50.0)),
    ),
    prong=(13.2, 90.0),
    fork=((0.0, 72.0), 9.4),
    top_tail_notch=((0.0, -98.0), 8.0),
    chevron_rows=(-72.0, -58.0, -44.0, -30.0, -16.0, -2.0, 12.0, 26.0, 40.0),
    chevron=(3.5, 9.0, 4.2),
    strap_slots=(
        ((19.0, 16.0), 3.6, 24.0),
        ((-19.0, 16.0), 3.6, 24.0),
        ((19.0, -16.0), 3.6, 24.0),
        ((-19.0, -16.0), 3.6, 24.0),
    ),
)

# a seven-inch long-range drive and pack
E.MOTOR_D, E.MOTOR_H = 34.5, 21.0
E.PROP_T = 8.0
E.BATTERY_SIZE = (46.0, 110.0, 46.0)  # 6S 3000-4000 mAh LiPo, or 6S1P 21700 Li-ion
E.BATTERY_Y = -12.0
camera_mount.FLOOR_T = 1.2
arm_guard.MOTOR_BASE_D = 34.6
wire_clip.U = 112.0
tiger_antenna.U = 88.0  # past the sandwich's edge (70 mm out)

design.NAME = "Tigerbee 7-inch LR"
design.SLUG = "tigerbee_lr"
design.DOCUMENT = "Tigerbee-7inch-LR"
design.MASS_LIMIT = 270.0
design.TIP_MASS = TIP_MASS
design.BOM = tiger.bill_of_materials
design.EQUIPMENT.update(gps="on a mast above the top plate's tail", receiver="T antenna on the rear right arm")
design.EXTRA_COLORS.update(accent=(0.98, 0.78, 0.10), tpu=(0.12, 0.12, 0.13), aluminium=(0.15, 0.15, 0.16))
frame.SHEETS.clear()
frame.SHEETS.update(tiger.sheets())
frame.EXTRA.update({"core_nose": ("core_nose", params.Z_ARM), "core_tail": ("core_tail", params.Z_ARM)})
checks.EXTRA_BOLTS.update(
    {
        "front_core": (params.pair(params.F), 3.0, [("core_nose", params.Z_ARM, params.Z_MID)]),
        "rear_core": (params.pair(params.R), 3.0, [("core_tail", params.Z_ARM, params.Z_MID)]),
    }
)
design.COLOR_OF.update(arm_guard="accent")
accessories.MODULES = (
    "tiger_skirt",
    "tiger_panels",
    "camera_mount",
    "tiger_nose",
    "arm_guard",
    "tiger_tail",
    "tiger_foot",
    "tiger_pad",
    "tiger_antenna",
    "wire_clip",
    "gopro_mount",
    "tigerbee_lr.accessories.gps_mast",
)
