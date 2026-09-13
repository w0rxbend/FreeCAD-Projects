"""Independent checks of placed CAD solids; these do not certify physical strength."""

from dataclasses import asdict, dataclass
from itertools import combinations
from math import dist, isfinite, pi

from build123d import Circle, Compound, Edge, GeomType, Part, Plane, Pos, Shape, ShapeList, extrude

Point = tuple[float, float]
AXIS_TOLERANCE_MM = 1e-6
VOLUME_TOLERANCE_MM3 = 1e-6
PROPELLER_DIAMETER_MM = 177.8
MINIMUM_PROPELLER_GAP_MM = 3.0
MINIMUM_MOUNTING_LIGAMENT_MM = 2.0
MINIMUM_STANDOFF_WALL_MM = 1.0
WHEELBASE_RANGE_MM = (303.0, 304.0)


@dataclass(frozen=True)
class FastenerAxis:
    name: str
    x: float
    y: float
    z_min: float
    z_max: float
    members: tuple[str, ...]
    shaft_diameter: float = 3.0


def _volume(shape: Shape | ShapeList | None) -> float:
    return sum(s.volume for s in shape.solids()) if shape is not None else 0.0


def _circles(part: Part) -> list[Edge]:
    return [
        e
        for e in part.edges().filter_by(GeomType.CIRCLE)
        if abs(e.length - 2 * pi * e.radius) < AXIS_TOLERANCE_MM
        and e.bounding_box().size.Z < AXIS_TOLERANCE_MM
    ]


def _symmetry_error(a: Part, b: Part) -> float:
    reflected = b.mirror(Plane.YZ)
    return _volume(a.cut(reflected)) + _volume(reflected.cut(a))


def _ligament(part: Part, x: float, y: float, radius: float) -> float | None:
    """Minimum planar material gap from the structural bore to any other boundary."""
    ligaments = []
    for face in part.faces():
        if face.bounding_box().size.Z > AXIS_TOLERANCE_MM:
            continue
        inner = list(face.inner_wires())
        for hole in inner:
            if any(
                edge.geom_type == GeomType.CIRCLE
                and dist(tuple(edge.arc_center)[:2], (x, y)) < AXIS_TOLERANCE_MM
                and abs(edge.radius - radius) < AXIS_TOLERANCE_MM
                for edge in hole.edges()
            ):
                boundaries = [face.outer_wire()] + [
                    wire for wire in inner if not wire.is_same(hole)
                ]
                ligaments.append(min(hole.distance_to(boundary) for boundary in boundaries))
    return min(ligaments, default=None)


def audit_frame(
    assembly: Compound,
    joints: list[FastenerAxis],
    motor_centers: dict[str, Point],
    *,
    expected_openings: dict[str, int] | None = None,
) -> dict:
    """Inspect actual geometry, using declared interfaces only to locate expected holes."""
    issues: list[str] = []
    parts = {part.label: part for part in assembly.children}
    if len(parts) != len(assembly.children) or not parts:
        issues.append("missing or duplicate component labels")
    for name, part in parts.items():
        if not part.is_valid or len(part.solids()) != 1:
            issues.append(f"invalid component: {name}")
    opening_checks = {}
    if expected_openings is not None:
        if set(expected_openings) != set(parts):
            issues.append("opening contract must cover every component")
        for name, expected in expected_openings.items():
            if name not in parts:
                continue
            part = parts[name]
            bounds = part.bounding_box()
            counts = []
            for z in (bounds.min.Z, bounds.max.Z):
                faces = [
                    face
                    for face in part.faces()
                    if face.bounding_box().size.Z <= AXIS_TOLERANCE_MM
                    and abs(face.bounding_box().min.Z - z) <= AXIS_TOLERANCE_MM
                ]
                counts.append(sum(len(face.inner_wires()) for face in faces))
            opening_checks[name] = {"expected": expected, "actual_by_face": counts}
            if any(count != expected for count in counts):
                issues.append(f"unexpected openings: {name}")
    collisions = []
    for (an, a), (bn, b) in combinations(parts.items(), 2):
        aa, bb = a.bounding_box(), b.bounding_box()
        if any(
            min(tuple(aa.max)[i], tuple(bb.max)[i]) - max(tuple(aa.min)[i], tuple(bb.min)[i])
            <= AXIS_TOLERANCE_MM
            for i in range(3)
        ):
            continue
        volume = _volume(a.intersect(b))
        if volume > VOLUME_TOLERANCE_MM3:
            collisions.append({"parts": [an, bn], "volume_mm3": volume})
    if collisions:
        issues.append("component interference")

    symmetry = {}
    pairs = [(name, name) for name in ("camera-plate", "rear-plate", "top-plate")]
    pairs += [(f"{end}-left-arm", f"{end}-right-arm") for end in ("front", "rear")]
    # Assembly support labels enumerate paired left/right positions in each row.
    standoffs = sorted(name for name in parts if name.startswith("standoff-"))
    if len(standoffs) % 2:
        issues.append("missing mirrored standoff member")
    pairs += list(zip(standoffs[::2], standoffs[1::2], strict=False))
    for left, right in pairs:
        if left not in parts or right not in parts:
            issues.append(f"missing symmetry member: {left}, {right}")
            continue
        error = _symmetry_error(parts[left], parts[right])
        symmetry[f"{left}/{right}"] = error
        if not isfinite(error) or error > VOLUME_TOLERANCE_MM3:
            issues.append(f"left/right asymmetry: {left}, {right}")

    joint_checks: list[dict] = []
    if not joints or len({joint.name for joint in joints}) != len(joints):
        issues.append("missing or duplicate fastener axes")
    for joint in joints:
        dimensions = (joint.x, joint.y, joint.z_min, joint.z_max, joint.shaft_diameter)
        if (
            not all(isfinite(v) for v in dimensions)
            or joint.z_max <= joint.z_min
            or joint.shaft_diameter <= 0
        ):
            issues.append(f"invalid fastener dimensions: {joint.name}")
            continue
        if not joint.members or len(set(joint.members)) != len(joint.members):
            issues.append(f"missing or duplicate fastener members: {joint.name}")
        shaft = Pos(joint.x, joint.y, joint.z_min) * extrude(
            Circle(joint.shaft_diameter / 2), amount=joint.z_max - joint.z_min
        )
        # A shaft must clear every solid it encounters, including accidentally
        # omitted members; nominal interface metadata cannot hide an obstruction.
        for name, part in parts.items():
            obstruction = _volume(shaft.intersect(part))
            if not isfinite(obstruction) or obstruction > VOLUME_TOLERANCE_MM3:
                issues.append(f"blocked shaft passage: {joint.name}/{name}")
        for name in joint.members:
            if name not in parts:
                issues.append(f"missing fastener member: {joint.name}/{name}")
                continue
            part = parts[name]
            bounds = part.bounding_box()
            circles = [
                e
                for e in _circles(part)
                if e.radius >= joint.shaft_diameter / 2 - AXIS_TOLERANCE_MM
                and dist(tuple(e.arc_center)[:2], (joint.x, joint.y)) <= AXIS_TOLERANCE_MM
            ]
            coaxial = (
                all(
                    any(abs(e.arc_center.Z - z) <= AXIS_TOLERANCE_MM for e in circles)
                    for z in (bounds.min.Z, bounds.max.Z)
                )
                and joint.z_min <= bounds.min.Z + AXIS_TOLERANCE_MM
                and joint.z_max >= bounds.max.Z - AXIS_TOLERANCE_MM
            )
            obstruction = _volume(shaft.intersect(part))
            radius = min((e.radius for e in circles), default=0)
            ligament = _ligament(part, joint.x, joint.y, radius) if coaxial else None
            minimum_ligament = (
                MINIMUM_STANDOFF_WALL_MM
                if name.startswith("standoff-")
                else MINIMUM_MOUNTING_LIGAMENT_MM
            )
            if (
                ligament is None
                or not isfinite(ligament)
                or (ligament < minimum_ligament - AXIS_TOLERANCE_MM)
            ):
                issues.append(f"insufficient mounting material: {joint.name}/{name}")
            joint_checks.append(
                {
                    "joint": joint.name,
                    "member": name,
                    "coaxial": coaxial,
                    "shaft_interference_mm3": obstruction,
                    "hole_diameter_mm": 2 * radius if circles else None,
                    "minimum_edge_ligament_mm": ligament,
                    "required_edge_ligament_mm": minimum_ligament,
                }
            )
            if not coaxial:
                issues.append(f"noncoaxial or incomplete bore: {joint.name}/{name}")

    measured = {}
    for name in (f"{end}-{side}-arm" for end in ("front", "rear") for side in ("left", "right")):
        if name not in parts or name not in motor_centers:
            issues.append(f"missing motor interface: {name}")
            continue
        if len(motor_centers[name]) != 2 or not all(isfinite(v) for v in motor_centers[name]):
            issues.append(f"invalid nominal motor center: {name}")
            continue
        circles = [
            e
            for e in _circles(parts[name])
            if min(abs(e.radius - r) for r in (3.5, 3.62)) < AXIS_TOLERANCE_MM
        ]
        if len(circles) != 2:
            issues.append(f"missing motor bore: {name}")
            continue
        actual = tuple(circles[0].arc_center)[:2]
        measured[name] = actual
        if (
            dist(actual, tuple(circles[1].arc_center)[:2]) > AXIS_TOLERANCE_MM
            or dist(actual, motor_centers[name]) > AXIS_TOLERANCE_MM
        ):
            issues.append(f"motor center differs from solid: {name}")
    clearances: list[dict] = [
        {"motors": [a, b], "tip_gap_mm": dist(p, q) - PROPELLER_DIAMETER_MM}
        for (a, p), (b, q) in combinations(measured.items(), 2)
    ]
    if len(clearances) != 6 or any(
        c["tip_gap_mm"] < MINIMUM_PROPELLER_GAP_MM - AXIS_TOLERANCE_MM for c in clearances
    ):
        issues.append("missing or overlapping 7-inch propeller discs, or insufficient tip gap")
    diagonals = [
        dist(measured[a], measured[b])
        for a, b in (("front-left-arm", "rear-right-arm"), ("front-right-arm", "rear-left-arm"))
        if a in measured and b in measured
    ]
    if len(diagonals) != 2 or abs(diagonals[0] - diagonals[1]) > AXIS_TOLERANCE_MM:
        issues.append("unequal or missing wheelbase diagonals")
    if len(diagonals) != 2 or any(
        not WHEELBASE_RANGE_MM[0] <= diagonal <= WHEELBASE_RANGE_MM[1] for diagonal in diagonals
    ):
        issues.append("wheelbase outside 303–304 mm measured range")
    ligaments = [
        c["minimum_edge_ligament_mm"]
        for c in joint_checks
        if c["minimum_edge_ligament_mm"] is not None
    ]
    return {
        "passed": not issues,
        "issues": issues,
        "thresholds": {
            "axis_tolerance_mm": AXIS_TOLERANCE_MM,
            "volume_tolerance_mm3": VOLUME_TOLERANCE_MM3,
            "propeller_diameter_mm": PROPELLER_DIAMETER_MM,
            "minimum_propeller_tip_gap_mm": MINIMUM_PROPELLER_GAP_MM,
            "minimum_mounting_ligament_mm": MINIMUM_MOUNTING_LIGAMENT_MM,
            "minimum_standoff_wall_mm": MINIMUM_STANDOFF_WALL_MM,
            "wheelbase_range_mm": list(WHEELBASE_RANGE_MM),
            "equal_diagonal_tolerance_mm": AXIS_TOLERANCE_MM,
        },
        "symmetry_difference_mm3": symmetry,
        "opening_checks": opening_checks,
        "interferences": collisions,
        "fastener_axes": [asdict(joint) for joint in joints],
        "joint_checks": joint_checks,
        "actual_motor_centers_mm": measured,
        "diagonal_wheelbases_mm": diagonals,
        "propeller_clearances": clearances,
        "minimum_edge_ligament_mm": min(ligaments, default=None),
        "minimum_structural_edge_ligament_mm": min(
            (
                c["minimum_edge_ligament_mm"]
                for c in joint_checks
                if c["minimum_edge_ligament_mm"] is not None
                and not c["member"].startswith("standoff-")
            ),
            default=None,
        ),
        "minimum_standoff_wall_mm": min(
            (
                c["minimum_edge_ligament_mm"]
                for c in joint_checks
                if c["minimum_edge_ligament_mm"] is not None and c["member"].startswith("standoff-")
            ),
            default=None,
        ),
        "scope": (
            "CAD fit only; propeller discs assume a shared unobstructed plane. "
            "Edge ligaments and propeller gaps meet explicit design minima only. "
            "No material strength, manufacturing process, or flight qualification."
        ),
    }


def require_frame_fit(report: dict) -> None:
    if report.get("passed") is not True or report.get("issues"):
        raise ValueError(
            "Frame geometry failed: " + "; ".join(report.get("issues", ["missing audit"]))
        )
