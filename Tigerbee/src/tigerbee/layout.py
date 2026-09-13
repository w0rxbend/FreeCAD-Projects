"""Symmetric arm placements and the small root relief required by those placements.

The saved FreeCAD motor pads, shafts and mounting axes define the arm geometry.
Two copies of type 1 form the front pair and two copies of type 2 the rear pair;
the left copies are reflected. Filleted root clearances provide a deliberate
centerline gap and unobstructed equipment fastener passages.
"""

import json
from dataclasses import dataclass
from importlib.resources import files
from math import cos, dist, isfinite, radians, sin, sqrt

from build123d import Axis, Circle, Face, Keep, Plane, Pos, Shape, split

from tigerbee.references import NOMINAL_WHEELBASE_MM

Point = tuple[float, float]
ROOT_GAP_MM = 0.6
ELECTRONICS_ROOT_CLEARANCE_RADIUS_MM = 2.0
ROOT_RELIEF_FILLET_MM = 0.6
ROOT_CENTERLINE_FILLET_MM = 0.2
REAR_TRANSVERSE_ROOT_DATUM_MM = -1.0


@dataclass(frozen=True)
class ArmPlacement:
    """Mirror local X first, rotate around Z, then translate to the motor centre."""

    part_name: str
    label: str
    mirror: bool
    angle: float
    motor_center: Point

    def apply(self, point: Point) -> Point:
        x, y = point
        if self.mirror:
            x = -x
        c, s = cos(radians(self.angle)), sin(radians(self.angle))
        return (
            c * x - s * y + self.motor_center[0],
            s * x + c * y + self.motor_center[1],
        )

    def place(self, shape: Shape, z: float = 0.0) -> Shape:
        placed = shape.mirror(Plane.YZ) if self.mirror else shape
        placed = placed.rotate(Axis.Z, self.angle).translate((*self.motor_center, z))
        placed.label = self.label
        return placed

    def root_holes(self) -> list[Point]:
        """Exact mount centres transformed from the saved FreeCAD profile data."""
        data = json.loads(
            files("tigerbee").joinpath("profiles", f"{self.part_name}.json").read_text()
        )
        return [
            self.apply(tuple(segment["center"]))
            for loop in data["loops"]
            for segment in loop["segments"]
            if segment["kind"] == "circle" and abs(segment["radius"] - 1.5) < 1e-7
        ]


# Nominal assembly dimensions. Motor positions and plate interfaces use this
# single datum; none is independently fitted to an imperfect tracing.
WHEELBASE_MM = NOMINAL_WHEELBASE_MM
MOTOR_OFFSET_MM = WHEELBASE_MM / (2 * sqrt(2))
FRONT_ARM_ANGLE_DEG = -45.0
REAR_ARM_ANGLE_DEG = -135.0
FRONT_SUPPORTS: tuple[Point, ...] = ((-19.25, 108.75), (19.25, 108.75))
REAR_SUPPORTS: tuple[Point, ...] = ((-16.5, -94.0), (16.5, -94.0))


def frame_arm_layout() -> tuple[ArmPlacement, ...]:
    """Place all motor bores on a 305 mm true-X square centered at the datum.

    Diagonals have equal lengths and midpoint, and intersect at 90 degrees.
    Matched source arm types are mirrored left/right, with 45°/135° rotations.
    """
    front = (MOTOR_OFFSET_MM, MOTOR_OFFSET_MM)
    rear = (MOTOR_OFFSET_MM, -MOTOR_OFFSET_MM)
    return (
        ArmPlacement("arm-type-1", "front-right-arm", False, FRONT_ARM_ANGLE_DEG, front),
        ArmPlacement(
            "arm-type-1", "front-left-arm", True, -FRONT_ARM_ANGLE_DEG, (-front[0], front[1])
        ),
        ArmPlacement("arm-type-2", "rear-right-arm", False, REAR_ARM_ANGLE_DEG, rear),
        ArmPlacement("arm-type-2", "rear-left-arm", True, -REAR_ARM_ANGLE_DEG, (-rear[0], rear[1])),
    )


def arm_root_holes() -> list[Point]:
    """Eight shared arm clamp axes, derived directly from the arm CAD holes."""
    return [point for placement in frame_arm_layout() for point in placement.root_holes()]


def top_support_holes() -> list[Point]:
    """Eight standoffs: front tips, outer clamp rows and rear tips, front first."""
    outer = [max(p.root_holes(), key=lambda point: abs(point[1])) for p in frame_arm_layout()]
    return sorted(
        [*FRONT_SUPPORTS, *outer, *REAR_SUPPORTS], key=lambda point: (-point[1], point[0])
    )


def plate_mounting_holes(name: str) -> list[Point]:
    """Shared structural and equipment axes in the assembly XY datum, in mm."""
    if name == "top-plate":
        return top_support_holes()
    electronics = [(x, y) for y in (-15.25, 15.25) for x in (-15.25, 15.25)]
    if name == "rear-plate":
        return [*arm_root_holes(), *electronics, *REAR_SUPPORTS]
    if name == "camera-plate":
        electronics += [(x, y) for y in (45.75, 76.75) for x in (-15.25, 15.25)]
        electronics += [(x, y) for y in (51.25, 71.25) for x in (-10.0, 10.0)]
        return [*arm_root_holes(), *electronics, *FRONT_SUPPORTS]
    raise ValueError(f"No shared plate mounting pattern for {name!r}")


def trim_arm_profile(face: Face, name: str, gap: float = ROOT_GAP_MM) -> Face:
    """Add filleted centerline and equipment-shaft clearances to a right arm.

    The opposite part is reflected at assembly time, giving the full requested
    gap. Root edits preserve every original closed opening; final solid audits
    verify passage and ligament dimensions. Gap does not imply strength approval.
    """
    if not isfinite(gap) or gap < 0:
        raise ValueError("Root gap must be finite and nonnegative")
    placement = next((p for p in frame_arm_layout() if p.part_name == name and not p.mirror), None)
    if placement is None:
        raise ValueError(f"No arm root relief is defined for {name!r}")
    c, s = cos(radians(placement.angle)), sin(radians(placement.angle))
    mx, my = placement.motor_center
    # Inverse-transform the global cutting plane; +normal keeps the right arm.
    cutting_plane = Plane(
        origin=(c * (gap / 2 - mx) - s * my, -s * (gap / 2 - mx) - c * my, 0),
        z_dir=(c, -s, 0),
    )
    cut = split(face, cutting_plane, keep=Keep.TOP)
    faces = cut.faces()
    if len(faces) != 1 or not faces[0].is_valid:
        raise ValueError("Root relief must leave one valid continuous arm profile")
    trimmed = faces[0]
    cut_corners = [
        vertex
        for vertex in trimmed.vertices()
        if abs(placement.apply(tuple(vertex)[:2])[0] - gap / 2) < 1e-6
    ]
    if len(cut_corners) not in (2, 4):
        raise ValueError("Centerline relief must create one or two pairs of edge junctions")
    trimmed = trimmed.fillet_2d(ROOT_CENTERLINE_FILLET_MM, cut_corners)
    # Keep rear roots below the transverse datum as well: the original tips
    # otherwise approach the front pair within 0.134 mm in the true-X layout.
    if placement.label.startswith("rear"):
        boundary_y = min(-gap / 2, REAR_TRANSVERSE_ROOT_DATUM_MM)
        dx, dy = -mx, boundary_y - my
        transverse_plane = Plane(origin=(c * dx + s * dy, -s * dx + c * dy, 0), z_dir=(-s, -c, 0))
        transverse = split(trimmed, transverse_plane, keep=Keep.TOP)
        faces = transverse.faces()
        if len(faces) != 1 or not faces[0].is_valid:
            raise ValueError("Transverse root relief must leave one continuous arm")
        trimmed = faces[0]
        corners = [
            vertex
            for vertex in trimmed.vertices()
            if abs(placement.apply(tuple(vertex)[:2])[1] - boundary_y) < 1e-6
        ]
        if len(corners) != 2:
            raise ValueError("Transverse root relief must create one edge junction pair")
        trimmed = trimmed.fillet_2d(ROOT_CENTERLINE_FILLET_MM, corners)
    # The 30.5 mm equipment fasteners pass through both lower plates. Their
    # axes clip the very edge of each original arm root, so create an open
    # clearance scallop instead of leaving the shaft obstructed by carbon.
    equipment = (15.25, 15.25 if placement.label.startswith("front") else -15.25)
    dx, dy = equipment[0] - mx, equipment[1] - my
    local_axis = (c * dx + s * dy, -s * dx + c * dy)
    clearance = Pos(*local_axis) * Circle(ELECTRONICS_ROOT_CLEARANCE_RADIUS_MM)
    relieved = trimmed.cut(clearance)
    faces = relieved.faces()
    if len(faces) != 1 or not faces[0].is_valid:
        raise ValueError("Electronics root relief must leave one valid continuous arm profile")
    trimmed = faces[0]
    junctions = [
        vertex
        for vertex in trimmed.vertices()
        if abs(dist(tuple(vertex)[:2], local_axis) - ELECTRONICS_ROOT_CLEARANCE_RADIUS_MM) < 1e-6
    ]
    if len(junctions) != 2:
        raise ValueError("Equipment clearance must form one open root notch")
    trimmed = trimmed.fillet_2d(ROOT_RELIEF_FILLET_MM, junctions)
    if len(trimmed.inner_wires()) != len(face.inner_wires()):
        raise ValueError("Root relief must preserve every arm opening")
    return trimmed
