"""Tigerbee 5": a freestyle five-inch that keeps the Tiger Beetle's face and fixes what it got wrong.

Kept from the owner's Tiger Beetle: the ears and bump of its nose, the two feet of its tail, the
long top deck with a camera fork in front and chevron windows down its length, the diamond past
the motor. Changed: a wide X with the front and rear arms at the same angle (the Tiger Beetle's
differ by seven degrees), so the props stay out of the camera's view; a sandwich floor instead of
two overlapping plates; eight equal standoffs on one deck; and 6 mm arms whose width follows the
bending moment (see the README for the calculation).

Importing this package configures the engine; nothing else of the engine may be imported before it.
"""

from zhalo import params

WHEELBASE = 225.0
T_ARM = 6.0
STANDOFF_H = 28.0
TIP_MASS = 40.0  # g: a 2207 motor, a 5.1 inch prop, screws

params.configure(
    WHEELBASE=WHEELBASE,
    MOTOR_X=88.0,  # wide X: the props move out to the sides, away from the camera and the body
    T_BOTTOM=2.0,
    T_ARM=T_ARM,
    T_MID=1.5,
    T_TOP=2.0,
    STACK_STANDOFF_H=STANDOFF_H,
    BAY_ON_DECK=True,
    BRACES=False,
    ARM_BOLT_U=(16.0, 40.0),
    LEG_R=6.0,
    MOTOR_PAD_R=16.0,
    ARM_NECK_BACK=19.0,
    F=(15.5, 56.0),
    R=(14.5, -70.0),
    A1=(15.5, 38.0),
)

from zhalo import accessories, checks, design, frame, tiger  # noqa: E402 - must follow configure()
from zhalo.accessories import camera_mount  # noqa: E402

tiger.ARM = tiger.Arm(root_u=-45.0, root_w=13.5, edge_w=18.0, neck_w=11.0)
params.ARM_WIDTH = tiger.arm_width  # the width law needs the arm's own numbers, so it is set after them
tiger.STYLE = tiger.Style(
    body_half=24.0,
    shoulder_y=(-60.0, 46.0),
    ear=(13.0, 66.0),
    ear_r=6.0,
    bump_y=79.0,
    bump_r=6.5,
    foot=(10.5, -82.0),
    foot_r=4.5,
    tail_notch=((0.0, -89.5), 5.0),
    windows_bottom=(
        ((-18.5, -62.5), (18.5, -62.5), (18.5, -30.0), (-18.5, -30.0)),
        ((-16.0, 30.0), (16.0, 30.0), (16.0, 46.0), (-16.0, 46.0)),
    ),
    deck_windows=(
        ((0.0, 26.0), (6.0, 36.0), (0.0, 46.0), (-6.0, 36.0)),  # the Tiger Beetle's diamond, in the camera bay
        ((-6.0, -52.0), (6.0, -52.0), (6.0, -40.0), (-6.0, -40.0)),
    ),
    chevron_rows=(-54.0, -40.0, -26.0, -12.0, 2.0, 16.0, 31.0, 46.0),
    chevron=(3.5, 8.0, 4.0),
    strap_slots=(
        ((19.0, 14.0), 3.6, 20.0),
        ((-19.0, 14.0), 3.6, 20.0),
        ((19.0, -14.0), 3.6, 20.0),
        ((-19.0, -14.0), 3.6, 20.0),
    ),
)

design.NAME = "Tigerbee 5-inch"
design.SLUG = "tigerbee"
design.DOCUMENT = "Tigerbee-5inch"
design.MASS_LIMIT = 150.0
design.TIP_MASS = TIP_MASS
design.BOM = tiger.bill_of_materials
design.EXTRA_COLORS.update(accent=(0.98, 0.55, 0.05), tpu=(0.12, 0.12, 0.13), aluminium=(0.80, 0.55, 0.10))
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
camera_mount.FLOOR_T = 1.2  # a 28 mm bay: the 22 mm camera needs the thinner cradle floor (as on Strila)
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
    "gps_mount",
    "xt60_mount",
)
