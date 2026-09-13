"""Assemble bilateral components on one exact shared set of mounting axes."""

from dataclasses import asdict, dataclass
from itertools import combinations
from math import atan2, cos, degrees, dist, isfinite, radians, sin

from build123d import Axis, Circle, Color, Compound, GeomType, Part, Pos, extrude

from tigerbee.layout import (
    FRONT_SUPPORTS,
    REAR_SUPPORTS,
    frame_arm_layout,
    plate_mounting_holes,
    top_support_holes,
)
from tigerbee.models import PartParameters, build_part, profile_data
from tigerbee.references import (
    MEASURED_WHEELBASE_RANGE_MM,
    MEASUREMENT_REFERENCE,
    WHEELBASE_COMPARISON_ALLOWANCE_MM,
    wheelbase_matches_measurement,
)
from tigerbee.validation import FastenerAxis, audit_frame, require_frame_fit

Point = tuple[float, float]
CLAMP_CENTER_Y = -61.4154192768


@dataclass(frozen=True)
class MountFit:
    angle: float
    translation: Point
    max_error: float

    def apply(self, point: Point) -> Point:
        c, s = cos(radians(self.angle)), sin(radians(self.angle))
        x, y = point
        return (c * x - s * y + self.translation[0], s * x + c * y + self.translation[1])


def fit_mounts(source: list[Point], target: list[Point]) -> MountFit:
    """Least-squares planar rigid fit; never scale or silently move mounting holes."""
    if len(source) != len(target) or len(source) < 2:
        raise ValueError("Provide at least two corresponding mounting points")
    sc = tuple(sum(p[i] for p in source) / len(source) for i in (0, 1))
    tc = tuple(sum(p[i] for p in target) / len(target) for i in (0, 1))
    centered = [
        (a[0] - sc[0], a[1] - sc[1], b[0] - tc[0], b[1] - tc[1])
        for a, b in zip(source, target, strict=True)
    ]
    angle = atan2(
        sum(x * v - y * u for x, y, u, v in centered), sum(x * u + y * v for x, y, u, v in centered)
    )
    c, s = cos(angle), sin(angle)
    translation = (tc[0] - c * sc[0] + s * sc[1], tc[1] - s * sc[0] - c * sc[1])
    fit = MountFit(degrees(angle), translation, 0)
    error = max(dist(fit.apply(a), b) for a, b in zip(source, target, strict=True))
    return MountFit(fit.angle, translation, error)


@dataclass(frozen=True)
class AssemblyParameters:
    """Stack dimensions in mm. Top height remains inferred from product photos."""

    plate_thickness: float = 2.5
    camera_plate_thickness: float = 3.0
    arm_thickness: float = 5.0
    top_z: float = 35.0

    def validate(self) -> None:
        for field in ("plate_thickness", "camera_plate_thickness", "arm_thickness", "top_z"):
            if not isfinite(getattr(self, field)) or getattr(self, field) <= 0:
                raise ValueError(f"{field} must be positive and finite")
        if self.top_z <= self.plate_thickness + self.arm_thickness + self.camera_plate_thickness:
            raise ValueError("top_z must be above the lower plates and arms")


DEFAULT_ASSEMBLY = AssemblyParameters()


def require_final_fit(report: dict, hole_tolerance: float = 1e-6) -> None:
    """Require verified CAD fit; physical qualification is reported separately."""
    if not isfinite(hole_tolerance) or hole_tolerance < 0:
        raise ValueError("Hole tolerance must be finite and nonnegative")
    require_frame_fit(report.get("geometry_audit", {}))
    errors = list(report.get("mounting_errors_mm", {}).values())
    if not errors or any(not isfinite(error) or error > hole_tolerance for error in errors):
        raise ValueError("Assembly is not ready: mounting-hole misalignment")
    if not wheelbase_matches_measurement(report.get("diagonal_wheelbases_mm", [])):
        raise ValueError("Assembly differs from the approximate 303–304 mm physical measurement")


def mounting_holes(name: str) -> list[Point]:
    return [
        tuple(s["center"])
        for loop in profile_data(name)["loops"]
        for s in loop["segments"]
        if s["kind"] == "circle" and abs(s["radius"] - 1.5) < 1e-7
    ]


def ordered(points: list[Point]) -> list[Point]:
    """Pair mounting rows by Y, then order left/right within each row."""
    by_y = sorted(points, key=lambda p: -p[1])
    return [p for i in range(0, len(by_y), 2) for p in sorted(by_y[i : i + 2])]


def locate(part: Part, fit: MountFit, z: float, label: str) -> Part:
    placed = part.rotate(Axis.Z, fit.angle).translate((*fit.translation, z))
    placed.label = label
    placed.color = Color(0.17, 0.20, 0.23)
    return placed


def interference_report(parts: list[Part]) -> list[dict]:
    collisions = []
    for a, b in combinations(parts, 2):
        aa, bb = a.bounding_box(), b.bounding_box()
        if any(
            min(tuple(aa.max)[i], tuple(bb.max)[i]) - max(tuple(aa.min)[i], tuple(bb.min)[i])
            <= 1e-6
            for i in range(3)
        ):
            continue
        common = a.intersect(b)
        volume = sum(s.volume for s in common.solids()) if common is not None else 0
        if volume > 1e-4:
            collisions.append({"parts": [a.label, b.label], "volume_mm3": volume})
    return collisions


def _mount_error(parts: dict[str, Part], joint: FastenerAxis) -> float:
    """Measure axis positions from circular edges in each placed solid."""
    errors = []
    for member in joint.members:
        candidates = [
            dist(tuple(edge.arc_center)[:2], (joint.x, joint.y))
            for edge in parts[member].edges().filter_by(GeomType.CIRCLE)
            if edge.radius >= joint.shaft_diameter / 2 - 1e-6
        ]
        errors.append(min(candidates, default=float("inf")))
    return max(errors)


def build_assembly(parameters: AssemblyParameters = DEFAULT_ASSEMBLY) -> tuple[Compound, dict]:
    parameters.validate()
    plate_params = PartParameters(thickness=parameters.plate_thickness)
    camera_z = parameters.plate_thickness + parameters.arm_thickness
    identity = MountFit(0, (0, 0), 0)
    parts = [
        locate(build_part("rear-plate", plate_params), identity, 0, "rear-plate"),
        locate(
            build_part("camera-plate", PartParameters(thickness=parameters.camera_plate_thickness)),
            identity,
            camera_z,
            "camera-plate",
        ),
    ]
    motors = {}
    for placement in frame_arm_layout():
        part = placement.place(
            build_part(placement.part_name, PartParameters(thickness=parameters.arm_thickness)),
            parameters.plate_thickness,
        )
        part.color = Color(0.17, 0.20, 0.23)
        parts.append(part)
        motors[placement.label] = placement.motor_center
    parts.append(
        locate(build_part("top-plate", plate_params), identity, parameters.top_z, "top-plate")
    )
    supports = top_support_holes()
    standoffs = {}
    lengths = []
    for i, (x, y) in enumerate(supports):
        bottom = (
            parameters.plate_thickness
            if (x, y) in REAR_SUPPORTS
            else camera_z + parameters.camera_plate_thickness
        )
        length = parameters.top_z - bottom
        spacer = Pos(x, y, bottom) * extrude(Circle(3) - Circle(1.6), amount=length)
        spacer.label = f"standoff-{i + 1:02}"
        spacer.color = Color(0.65, 0.68, 0.72)
        parts.append(spacer)
        lengths.append(length)
        standoffs[(x, y)] = spacer.label
    top = parameters.top_z + parameters.plate_thickness
    camera_top = camera_z + parameters.camera_plate_thickness
    joints = []
    for placement in frame_arm_layout():
        for index, (x, y) in enumerate(placement.root_holes()):
            members = ["rear-plate", placement.label, "camera-plate"]
            if (x, y) in standoffs:
                members.extend([standoffs[(x, y)], "top-plate"])
            joints.append(
                FastenerAxis(
                    f"{placement.label}-root-{index + 1}",
                    x,
                    y,
                    0,
                    top if (x, y) in standoffs else camera_top,
                    tuple(members),
                )
            )
    for end, points, member, bottom in (
        ("front", FRONT_SUPPORTS, "camera-plate", camera_z),
        ("rear", REAR_SUPPORTS, "rear-plate", 0),
    ):
        for i, (x, y) in enumerate(points):
            joints.append(
                FastenerAxis(
                    f"{end}-support-{i + 1}",
                    x,
                    y,
                    bottom,
                    top,
                    (member, standoffs[(x, y)], "top-plate"),
                )
            )
    for i, (x, y) in enumerate(
        point for point in plate_mounting_holes("rear-plate") if abs(point[0]) == 15.25
    ):
        joints.append(
            FastenerAxis(
                f"electronics-{i + 1}", x, y, 0, camera_top, ("rear-plate", "camera-plate")
            )
        )
    assembly = Compound(label="Tigerbee frame", children=parts)
    expected_openings = {part.label: 1 for part in parts}
    expected_openings.update({"camera-plate": 31, "rear-plate": 32, "top-plate": 30})
    expected_openings.update({placement.label: 8 for placement in frame_arm_layout()})
    audit = audit_frame(assembly, joints, motors, expected_openings=expected_openings)
    errors = {joint.name: _mount_error({p.label: p for p in parts}, joint) for joint in joints}
    diagonals = [
        dist(motors["front-right-arm"], motors["rear-left-arm"]),
        dist(motors["front-left-arm"], motors["rear-right-arm"]),
    ]
    report = {
        "status": "cad-fit-verified" if audit["passed"] else "cad-fit-failed",
        "physical_validation_status": "unconfirmed-stack-hardware-and-material",
        "units": "mm",
        "parameters": asdict(parameters),
        "motor_centers_mm": motors,
        "diagonal_wheelbases_mm": diagonals,
        "measured_wheelbase_range_mm": list(MEASURED_WHEELBASE_RANGE_MM),
        "wheelbase_comparison_allowance_mm": WHEELBASE_COMPARISON_ALLOWANCE_MM,
        "wheelbase_reference": MEASUREMENT_REFERENCE,
        "authoritative_geometry_sources": {
            "arm-type-1": "Tigerbee.FCStd#Body001; mirrored pairs with filleted root clearances",
            "arm-type-2": "Tigerbee.FCStd#Body002; mirrored pairs with filleted root clearances",
            "camera-plate": "Tigerbee.FCStd#Body; symmetric analytic profile and shared axes",
            "rear-plate": "refs/Scan_2.jpeg; nominal symmetric analytic design",
            "top-plate": "refs/Scan_2.jpeg; nominal symmetric analytic design",
        },
        "wheelbase_matches_measurement": wheelbase_matches_measurement(diagonals),
        "mounting_errors_mm": errors,
        "standoff_lengths_mm": lengths,
        "interferences": audit["interferences"],
        "interference_volume_mm3": sum(c["volume_mm3"] for c in audit["interferences"]),
        "geometry_audit": audit,
        "assumptions": [
            f"Top plate Z={parameters.top_z:g} mm is a nominal stack choice",
            "Standoffs represented as 6/3.2 mm tubes; hardware is not yet selected",
            "Saved FreeCAD parts and root 3MFs define arm and camera design intent",
            "Scan_2 supplies design intent for rear and top plates",
            "Original tracings remain reference evidence, not manufacturing outlines",
            "User measured approximately 303–304 mm between opposite motor-hole centers",
            "Both nominal diagonals are constrained to 303.5 mm",
            "Left arms are mirrored matched copies of the right arms",
            "Shared mounting axes replace independent imperfect hole fits",
            "CAD fit does not establish carbon laminate strength or flight qualification",
        ],
    }
    return assembly, report
