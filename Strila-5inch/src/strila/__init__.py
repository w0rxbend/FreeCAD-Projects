"""Strila 5" ("arrow"): a frame sized by calculation.

Six-millimetre arms that taper where the bending moment falls, clamped in a floor made of
two thin skins, on eight identical standoffs. It runs on the Zhalo engine with its own
dimensions, so every geometric check of that engine applies; the structural sizing is in
`zhalo.structure` (beam model) and `zhalo.fea` (finite elements).

Importing this package configures the engine. Nothing else of the engine may be imported
before it, because the engine's modules read the dimensions when they load.
"""

from zhalo import params

from strila import sizing

_NECK_U = None


def _width(u: float) -> float:
    return sizing.arm_width(u, params.ARM_LEN - sizing.NECK_BACK)


params.configure(
    T_BOTTOM=sizing.T_BOTTOM,
    T_ARM=sizing.T_ARM,
    T_MID=sizing.T_DECK,
    T_TOP=sizing.T_TOP,
    STACK_STANDOFF_H=sizing.STANDOFF_H,
    BAY_ON_DECK=True,
    BRACES=False,
    ARM_BOLT_U=sizing.ARM_BOLT_U,
    LEG_R=sizing.LEG_R,
    MOTOR_PAD_R=sizing.PAD_R,
    ARM_NECK_BACK=sizing.NECK_BACK,
    ARM_WIDTH=_width,
)

from zhalo import accessories, checks, design, frame  # noqa: E402 - must follow configure()
from zhalo.accessories import camera_mount  # noqa: E402

from strila import profiles  # noqa: E402

design.NAME = "Strila 5-inch"
design.SLUG = "strila"
design.DOCUMENT = "Strila-5inch"
design.MASS_LIMIT = 140.0  # 6 mm arms and a double floor: heavier than Zhalo by design
design.BOM = profiles.bill_of_materials
design.EXTRA_COLORS.update(
    accent=(0.10, 0.62, 0.86),  # one cool accent on the parts that take the hits
    tpu=(0.16, 0.17, 0.19),
    aluminium=(0.72, 0.74, 0.78),  # plain silver standoffs
)

frame.SHEETS.clear()
frame.SHEETS.update(profiles.SHEETS)
frame.EXTRA.update({"core_nose": ("core_nose", params.Z_ARM), "core_tail": ("core_tail", params.Z_ARM)})
checks.EXTRA_BOLTS.update(
    {
        "front_core": (params.pair(params.F), 3.0, [("core_nose", params.Z_ARM, params.Z_MID)]),
        "rear_core": (params.pair(params.R), 3.0, [("core_tail", params.Z_ARM, params.Z_MID)]),
    }
)
design.COLOR_OF.update(arm_guard="accent")
camera_mount.FLOOR_T = 1.2  # the bay is 7 mm lower than Zhalo's: a 22 mm camera needs the thinner cradle floor
accessories.MODULES = (
    "strila.accessories.skirt",
    "camera_mount",
    "strila.accessories.nose_shoe",
    "arm_guard",
    "strila.accessories.tail",
    "strila.accessories.foot",
    "strila.accessories.pad",
    "strila.accessories.antenna_clip",
    "wire_clip",
    "gopro_mount",
    "gps_mount",
    "xt60_mount",
)
