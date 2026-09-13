"""Locate the reference parts from mounting interfaces and report unresolved fit."""

from dataclasses import asdict, dataclass
from itertools import combinations
from math import atan2, cos, degrees, dist, isfinite, radians, sin

from build123d import Axis, Circle, Color, Compound, Part, Pos, extrude

from tigerbee.models import PartParameters, build_part, profile_data

Point = tuple[float, float]
CLAMP_CENTER_Y = -61.4154192768
TARGET_WHEELBASE_MM = 330.0


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
    arm_thickness: float = 5.0
    top_z: float = 35.0

    def validate(self) -> None:
        for field in ("plate_thickness", "arm_thickness", "top_z"):
            if not isfinite(getattr(self, field)) or getattr(self, field) <= 0:
                raise ValueError(f"{field} must be positive and finite")
        if self.top_z <= 2 * self.plate_thickness + self.arm_thickness:
            raise ValueError("top_z must be above the lower plates and arms")


DEFAULT_ASSEMBLY = AssemblyParameters()


def require_final_fit(report: dict, hole_tolerance: float = 0.1) -> None:
    """Reject a provisional assembly until its geometry and dimensions are resolved."""
    issues = []
    if report["interference_volume_mm3"] > 1e-4:
        issues.append("arm or plate interference")
    if max(report["mounting_errors_mm"].values()) > hole_tolerance:
        issues.append("mounting-hole misalignment")
    if any(
        abs(w - report["advertised_wheelbase_mm"]) > 0.5 for w in report["diagonal_wheelbases_mm"]
    ):
        issues.append(f"wheelbase differs from {report['advertised_wheelbase_mm']:g} mm reference")
    if report["status"] == "provisional-assembly":
        issues.append("unconfirmed scan dimensions, stack height, and hardware")
    if issues:
        raise ValueError("Assembly is not ready: " + "; ".join(issues))


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


def build_assembly(parameters: AssemblyParameters = DEFAULT_ASSEMBLY) -> tuple[Compound, dict]:
    parameters.validate()
    plate_params = PartParameters(thickness=parameters.plate_thickness)
    camera_fit = MountFit(0, (0, -CLAMP_CENTER_Y), 0)
    camera_holes = [camera_fit.apply(p) for p in mounting_holes("camera-plate")]
    clamp_holes = ordered([p for p in camera_holes if abs(p[0]) > 25])
    rear_holes = mounting_holes("rear-plate")
    rear_clamp = ordered([p for p in rear_holes if abs(p[0]) > 25 and abs(p[1]) < 40])
    rear_fit = fit_mounts(rear_clamp, clamp_holes)
    camera_z = parameters.plate_thickness + parameters.arm_thickness
    parts = [
        locate(build_part("rear-plate", plate_params), rear_fit, 0, "rear-plate"),
        locate(build_part("camera-plate", plate_params), camera_fit, camera_z, "camera-plate"),
    ]
    errors = {"rear-plate-to-camera-plate": rear_fit.max_error}
    motors = {}
    for label, name, side, front in (
        ("front-right-arm", "arm-type-1", 1, True),
        ("front-left-arm", "arm-type-2", -1, True),
        ("rear-left-arm", "arm-type-1", -1, False),
        ("rear-right-arm", "arm-type-2", 1, False),
    ):
        target = [p for p in clamp_holes if p[0] * side > 0 and (p[1] > 0) == front]
        source = mounting_holes(name)
        fits = [fit_mounts(source, target), fit_mounts(source, target[::-1])]
        fit = next(
            f for f in fits if f.translation[0] * side > 0 and (f.translation[1] > 0) == front
        )
        parts.append(
            locate(
                build_part(name, PartParameters(thickness=parameters.arm_thickness)),
                fit,
                parameters.plate_thickness,
                label,
            )
        )
        motors[label] = fit.translation
        errors[label] = fit.max_error
    front_tips = [p for p in camera_holes if p[1] > 100]
    rear_tips = [rear_fit.apply(p) for p in rear_holes if p[1] < -93]
    # The top plate's two central mounting rows land at the outer clamp rows.
    supports = ordered(front_tips + clamp_holes[:2] + clamp_holes[-2:] + rear_tips)
    top_fit = fit_mounts(ordered(mounting_holes("top-plate")), supports)
    parts.append(
        locate(build_part("top-plate", plate_params), top_fit, parameters.top_z, "top-plate")
    )
    errors["top-plate-to-standoffs"] = top_fit.max_error
    lengths = []
    for i, (x, y) in enumerate(supports):
        bottom = parameters.plate_thickness if y < -80 else camera_z + parameters.plate_thickness
        length = parameters.top_z - bottom
        spacer = Pos(x, y, bottom) * extrude(Circle(3) - Circle(1.5), amount=length)
        spacer.label = f"standoff-{i + 1:02}"
        spacer.color = Color(0.65, 0.68, 0.72)
        parts.append(spacer)
        lengths.append(length)
    collisions = interference_report(parts)
    report = {
        "status": "provisional-assembly",
        "units": "mm",
        "parameters": asdict(parameters),
        "motor_centers_mm": motors,
        "diagonal_wheelbases_mm": [
            dist(motors["front-right-arm"], motors["rear-left-arm"]),
            dist(motors["front-left-arm"], motors["rear-right-arm"]),
        ],
        "advertised_wheelbase_mm": TARGET_WHEELBASE_MM,
        "wheelbase_reference": "refs/product/tiger-beetle-7inch-330mm.png",
        "authoritative_blueprints": ["refs/Scan_1.jpeg", "refs/Scan_2.jpeg"],
        "wheelbase_errors_mm": [
            dist(motors["front-right-arm"], motors["rear-left-arm"]) - TARGET_WHEELBASE_MM,
            dist(motors["front-left-arm"], motors["rear-right-arm"]) - TARGET_WHEELBASE_MM,
        ],
        "mounting_errors_mm": errors,
        "standoff_lengths_mm": lengths,
        "interferences": collisions,
        "interference_volume_mm3": sum(c["volume_mm3"] for c in collisions),
        "assumptions": [
            "Top plate Z=35 mm is provisional",
            "Standoffs represented as 6/3 mm tubes",
            "Both scans are authoritative outlines; metric calibration requires confirmation",
            "Saved FreeCAD solids are prior reconstructions, subordinate to the scans",
            "330 mm diagonal wheelbase confirmed by user; earlier 295 mm photo superseded",
            "Original hole positions preserved; fit errors are not corrected",
            "Fasteners and end brackets are not yet modeled",
        ],
    }
    return Compound(label="Tigerbee frame", children=parts), report
