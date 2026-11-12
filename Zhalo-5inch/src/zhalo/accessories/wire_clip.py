"""Motor-wire clip: snaps over an arm and holds the three motor wires flat on top of it.

One clip per arm, between the brace lug and the motor. Its profile is constant along the arm,
so it prints lying on its side with no overhang at all.
"""

from build123d import Axis, Plane, Vector

from zhalo.accessories.kit import FIT, WALL, Accessory, P, poly, prism_x

U = 62.0  # station along the arm
LENGTH = 6.0
TUNNEL = (8.6, 3.2)  # three 18 AWG silicone wires side by side
HOOK = 1.4  # how far each hook reaches under the arm
HOOK_T = 1.5


def _local():
    """Clip in arm coordinates, arm underside at Z = 0: profile in (v, z), extruded along the arm."""
    half = P.arm_half_width(U) + FIT
    out = half + WALL
    top = P.T_ARM + FIT
    roof = top + TUNNEL[1] + WALL
    tw = TUNNEL[0] / 2
    outer = poly(
        [(-out, -HOOK_T), (out, -HOOK_T), (out, roof - 1.5), (out - 1.5, roof), (-out + 1.5, roof), (-out, roof - 1.5)],
        0.6,
    )
    arm_slot = poly([(-half, -FIT), (half, -FIT), (half, top), (-half, top)])
    # the tunnel starts inside the arm slot, so only its two top corners end up rounded
    tunnel = poly([(-tw, top - 2.5), (tw, top - 2.5), (tw, top + TUNNEL[1]), (-tw, top + TUNNEL[1])], 1.0)
    mouth = poly([(-half + HOOK, -HOOK_T - 1), (half - HOOK, -HOOK_T - 1), (half - HOOK, 0.0), (-half + HOOK, 0.0)])
    # prism_x reads the profile as (y, z): v plays the part of y here
    return prism_x(outer - arm_slot - tunnel - mouth, U - LENGTH / 2, U + LENGTH / 2)


def _place(part, name: str):
    out = part.rotate(Axis.Z, P.ARM_ANGLE).translate(Vector(P.S[0], P.S[1], P.Z_ARM))
    if "left" in name:
        out = out.mirror(Plane.YZ)
    if "rear" in name:
        out = out.mirror(Plane.XZ)
    return out


def build() -> list[Accessory]:
    local = _local()
    placed = {name: _place(local, name) for name in P.MOTORS}
    top = P.Z_ARM + P.T_ARM + FIT + TUNNEL[1] + WALL
    own = [
        ("stays under the props", top < P.PROP_Z[0] - 5, f"top at Z {top:.1f}, props from Z {P.PROP_Z[0]:.0f}"),
        (
            "hooks leave a mouth the arm can pass",
            2 * HOOK < 2 * P.arm_half_width(U) * 0.3,
            f"{HOOK} mm hooks on a {2 * P.arm_half_width(U):.1f} mm arm",
        ),
    ]
    bed = (P.ARM_DIR[0], P.ARM_DIR[1], 0.0)  # the face square to the arm lies on the bed
    return [
        Accessory(
            "wire_clip",
            "Motor-wire clip",
            placed["front_right"],
            bed=bed,
            qty=4,
            checks=own,
            instances=tuple(v for k, v in placed.items() if k != "front_right"),
            notes="Lay the wires on the arm and press the clip down over them until both hooks snap under the arm.",
        )
    ]
