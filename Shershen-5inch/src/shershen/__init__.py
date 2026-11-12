"""Shershen 5" ("hornet"): the stylish sibling of Zhalo.

Same hard points, same stack-up, same electronics, so every clearance and bolt check of
the Zhalo engine applies unchanged. What is new is everything you see: swept wings on the
top plate, fishbone windows, a barbed stinger, pointed arm tips, and a TPU set in two colours.

Importing this package registers the design with the engine; nothing is built until asked.
"""

from zhalo import accessories, design, frame

from shershen import profiles

design.NAME = "Shershen 5-inch"
design.SLUG = "shershen"
design.DOCUMENT = "Shershen-5inch"
design.EXTRA_COLORS.update(
    accent=(1.0, 0.42, 0.04),  # hornet orange: the parts that carry the look
    tpu=(0.15, 0.15, 0.17),  # black TPU: the quiet, functional parts
    aluminium=(0.78, 0.16, 0.10),  # red anodised standoffs
)

frame.SHEETS.update(profiles.SHEETS)
accessories.MODULES = (
    "shershen.accessories.head",
    "shershen.accessories.side_pod",
    "shershen.accessories.tail_fins",
    "shershen.accessories.claw",
    "shershen.accessories.stripe_pad",
    "gopro_mount",
    "gps_mount",
    "xt60_mount",
    "cap_holder",
    "wire_clip",
    "brace_skid",
)
