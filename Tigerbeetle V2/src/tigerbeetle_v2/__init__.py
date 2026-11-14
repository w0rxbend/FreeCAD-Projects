"""Tigerbeetle V2 6": a six-inch for a digital HD video system, in the Tiger Beetle style.

What the digital systems ask of a frame: a tall rear bay for the video transmitter (with its fan
and its 30.5 or 20 mm holes), a front bay for a 20 mm HD camera, two antennas well apart at the
tail, and props out of a 150 deg wide view, which is why the X is wide. From the Tiger Beetle it
keeps the nose, the tail, the forked top deck with its chevrons and the diamond past the motor.
The floor is a sandwich (as on Strila) and the 6 mm arms are sized for a six-inch motor.

Importing this package configures the engine; nothing else of the engine may be imported before it.
"""

from zhalo import params

WHEELBASE = 265.0
MOTOR_X = 105.0  # wide X: the props move out of the HD camera's view
T_ARM = 6.0
STANDOFF_H = 30.0  # a digital VTX with its fan is taller than an analog one
TIP_MASS = 48.0  # g: a 2507 motor, a 6 inch prop, screws

params.configure(
    WHEELBASE=WHEELBASE,
    MOTOR_X=MOTOR_X,
    PROP_D=6 * 25.4,
    PROP_Z=(26.0, 40.0),
    T_BOTTOM=2.0,
    T_ARM=T_ARM,
    T_MID=1.5,
    T_TOP=2.0,
    STACK_STANDOFF_H=STANDOFF_H,
    BAY_ON_DECK=True,
    BRACES=False,
    ARM_BOLT_U=(16.0, 46.0),
    LEG_R=7.0,
    MOTOR_PAD_R=17.0,
    ARM_NECK_BACK=21.0,
    F=(15.5, 62.0),
    R=(15.5, -78.0),
    A1=(15.5, 44.0),
    VTX_BAY_Y=-50.0,
)

from zhalo import accessories, checks, design, frame, tiger  # noqa: E402 - must follow configure()
from zhalo import equipment as E  # noqa: E402
from zhalo.accessories import camera_mount, wire_clip  # noqa: E402

tiger.ARM = tiger.Arm(root_u=-45.0, root_w=13.0, edge_w=20.0, neck_w=12.0, diamond=(11.2, 5.4, 6.8))
params.ARM_WIDTH = tiger.arm_width
tiger.STYLE = tiger.Style(
    body_half=24.0,
    shoulder_y=(-68.0, 52.0),
    ear=(13.0, 72.0),
    ear_r=6.0,
    bump_y=86.0,
    bump_r=7.0,
    foot=(11.0, -90.0),
    foot_r=4.8,
    tail_notch=((0.0, -97.5), 5.5),
    windows_bottom=(
        ((-18.5, -70.0), (18.5, -70.0), (18.5, -32.0), (-18.5, -32.0)),
        ((-16.0, 32.0), (16.0, 32.0), (16.0, 52.0), (-16.0, 52.0)),
    ),
    deck_windows=(
        ((0.0, 30.0), (6.0, 40.0), (0.0, 50.0), (-6.0, 40.0)),
        ((-6.0, -56.0), (6.0, -56.0), (6.0, -44.0), (-6.0, -44.0)),
    ),
    prong=(13.2, 82.0),
    fork=((0.0, 64.0), 9.4),
    top_tail_notch=((0.0, -88.0), 8.0),
    chevron_rows=(-62.0, -48.0, -34.0, -20.0, -6.0, 8.0, 22.0, 36.0, 51.0),
    chevron=(3.5, 8.0, 4.0),
    strap_slots=(
        ((19.0, 14.0), 3.6, 20.0),
        ((-19.0, 14.0), 3.6, 20.0),
        ((19.0, -14.0), 3.6, 20.0),
        ((-19.0, -14.0), 3.6, 20.0),
    ),
)

# what it carries
E.MOTOR_D, E.MOTOR_H = 31.0, 20.0  # 2507 class
E.PROP_T = 7.5
E.VTX_LARGE_SIZE = (36.0, 36.0, 15.0)  # a digital air unit with its fan, on 30.5 mm holes
E.BATTERY_SIZE = (40.0, 95.0, 40.0)  # 6S 1500-2200 mAh
E.BATTERY_Y = -10.0  # behind the action-camera mount
camera_mount.FLOOR_T = 1.2
wire_clip.U = 66.0

design.NAME = "Tigerbeetle V2 6-inch HD"
design.SLUG = "tigerbeetle_v2"
design.DOCUMENT = "Tigerbeetle-V2-6inch"
design.MASS_LIMIT = 175.0
design.TIP_MASS = TIP_MASS
design.BOM = tiger.bill_of_materials
design.EQUIPMENT.update(
    vtx="digital HD air unit up to 36 x 36 x 15 mm, 30.5 or 20 mm holes, rear bay",
    camera="HD camera 20 mm wide on the front mount (19 and 22 mm mounts too)",
)
design.EXTRA_COLORS.update(accent=(0.10, 0.80, 0.85), tpu=(0.12, 0.12, 0.13), aluminium=(0.75, 0.76, 0.80))
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
    "tigerbeetle_v2.accessories.hd_camera",
    "tiger_nose",
    "arm_guard",
    "tigerbeetle_v2.accessories.twin_antenna",
    "tiger_foot",
    "tiger_pad",
    "wire_clip",
    "gopro_mount",
    "xt60_mount",
)
