"""Assembly: plates at their Z, four placed arms, eight standoffs."""

from copy import deepcopy

from build123d import Axis, Compound, Part, Plane, Vector

from tigerbee import params as P
from tigerbee.mounts import holes_for
from tigerbee.profiles import build_arm, build_plate, build_standoff

PLATES = {"plate_bottom": P.Z_BOTTOM, "plate_mid": P.Z_MID, "plate_top": P.Z_TOP}

# name -> (x, y, z0, height)
STANDOFFS: dict[str, tuple[float, float, float, float]] = {}
for _name, (_x, _y), _z0, _h in (
    ("front_tip", P.FRONT_TIP, P.Z_MID + P.PLATE_T, P.STANDOFF_H_SHORT),
    ("front_arm", P.place(*P.root_holes()[0], P.ARM_PLACEMENTS["arm_front_right"]), P.Z_MID + P.PLATE_T, P.STANDOFF_H_SHORT),
    ("rear_arm", P.place(*P.root_holes()[0], P.ARM_PLACEMENTS["arm_rear_right"]), P.Z_MID + P.PLATE_T, P.STANDOFF_H_SHORT),
    ("rear_tip", P.REAR_TIP, P.Z_ARM, P.STANDOFF_H_REAR),
):
    STANDOFFS[f"standoff_{_name}_left"] = (-_x, _y, _z0, _h)
    STANDOFFS[f"standoff_{_name}_right"] = (_x, _y, _z0, _h)


def motor_centers(length: float = P.ROOT_TO_MOTOR) -> dict[str, tuple[float, float]]:
    return {name.removeprefix("arm_"): P.place(0, length, pl) for name, pl in P.ARM_PLACEMENTS.items()}


def wheelbase(length: float = P.ROOT_TO_MOTOR) -> float:
    m = motor_centers(length)
    return (Vector(*m["front_right"]) - Vector(*m["rear_left"])).length


def place_arm(arm: Part, placement: tuple[float, float, float, bool]) -> Part:
    x, y, angle, mirror = placement
    # Each placement gets its own copy: rotate/translate only relocate the shared shape,
    # and the STEP writer would merge instances that share it under one label.
    part = arm.mirror(Plane.YZ) if mirror else deepcopy(arm)
    return part.rotate(Axis.Z, angle).translate(Vector(x, y, P.Z_ARM))


def build_frame() -> tuple[Compound, dict[str, Part]]:
    parts: dict[str, Part] = {}
    for name, z in PLATES.items():
        parts[name] = build_plate(name, holes_for(name)).translate(Vector(0, 0, z))
    arm = build_arm()
    for name in ("arm_front_left", "arm_front_right", "arm_rear_left", "arm_rear_right"):
        parts[name] = place_arm(arm, P.ARM_PLACEMENTS[name])
    for name, (x, y, z0, h) in STANDOFFS.items():
        parts[name] = build_standoff(h).translate(Vector(x, y, z0))
    for name, part in parts.items():
        part.label = name
    return Compound(children=list(parts.values()), label="tigerbee"), parts
