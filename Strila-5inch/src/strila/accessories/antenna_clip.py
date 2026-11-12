"""Receiver antenna clip: holds the bar of a 2.4 GHz T antenna across a rear arm.

It snaps over the arm like a motor-wire clip (and lets the wires through the same tunnel),
with a snap channel for the antenna bar on top, open towards the body. On an arm the antenna is a hand's width from
the VTX antenna and well under the props.
"""

from zhalo.accessories import wire_clip as base
from zhalo.accessories.kit import FIT, WALL, Accessory, P, box, disc, poly, prism_x, prism_y

U = 52.0  # station along the arm
LENGTH = 9.0
T_D = 4.7  # antenna bar
T_MOUTH = 3.5
ARM = "rear_right"


def _local():
    half = P.arm_half_width(U - LENGTH / 2) + FIT  # the arm tapers: size the slot for its wide end
    out = half + WALL
    top = P.T_ARM + FIT
    tw, th = base.TUNNEL[0] / 2, base.TUNNEL[1]
    zc = top + th + 1.2 + T_D / 2  # antenna bar axis
    roof = zc + T_D / 2 + WALL
    outer = poly(
        [
            (-out, -base.HOOK_T),
            (out, -base.HOOK_T),
            (out, roof - 1.5),
            (out - 1.5, roof),
            (-out + 1.5, roof),
            (-out, roof - 1.5),
        ],
        0.6,
    )
    arm_slot = poly([(-half, -FIT), (half, -FIT), (half, top), (-half, top)])
    tunnel = poly([(-tw, top - 2.5), (tw, top - 2.5), (tw, top + th), (-tw, top + th)], 1.0)
    mouth = poly(
        [
            (-half + base.HOOK, -base.HOOK_T - 1),
            (half - base.HOOK, -base.HOOK_T - 1),
            (half - base.HOOK, 0.0),
            (-half + base.HOOK, 0.0),
        ]
    )
    clip = prism_x(outer - arm_slot - tunnel - mouth, U - LENGTH / 2, U + LENGTH / 2)
    # The bar lies across the arm in a bore near the clip's motor end; the mouth opens towards the
    # body, which is the way the antenna's lead leaves. Printed motor end down, the mouth is open to
    # the top and nothing bridges.
    ub = U + LENGTH / 2 - WALL - T_D / 2
    clip -= prism_y(disc((ub, zc), T_D), -out - 1, out + 1)
    clip -= box(U - LENGTH / 2 - 1, -out - 1, zc - T_MOUTH / 2, ub, out + 1, zc + T_MOUTH / 2)
    return clip, roof


def build() -> list[Accessory]:
    local, roof = _local()
    part = base._place(local, ARM)
    top = P.Z_ARM + roof
    own = [("stays under the props", top < P.PROP_Z[0] - 3.0, f"top at Z {top:.1f}, props from Z {P.PROP_Z[0]:.0f}")]
    bed = (P.ARM_DIR[0], -P.ARM_DIR[1], 0.0)
    return [
        Accessory(
            "antenna_clip",
            "Receiver antenna clip (T antenna)",
            part,
            bed=bed,
            checks=own,
            overhang=20.0,
            ceilings=10.0,
            notes="Snap it over the rear right arm with the motor wires in the tunnel, then press the antenna bar in.",
        )
    ]
