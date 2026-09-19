"""Concrete shared mechanical layout, independent of CAD kernel and source-file IO."""

from dataclasses import dataclass
from math import cos, hypot, radians, sin

from fpv_frame.blueprint.calibration import Calibration, calibrate_page
from fpv_frame.parameters.frame import FrameParameters
from fpv_frame.parameters.layout import LayoutParameters
from fpv_frame.parameters.plates import PLATE_IDS, PlateId

from .datums import PlanarTransform, Point2, Point3
from .interfaces import ArmInterface
from .patterns import HolePattern

# Registration evidence, not independent manufacturing dimensions.
MASTER_ORIGIN_PX = Point2(1870.5, 1588.75)
MASTER_AXIS_TILT_DEG = 0.35
PIXELS_PER_MM = calibrate_page((2480, 3508), (210, 297)).pixels_per_mm
MASTER_CALIBRATION = Calibration(
    PIXELS_PER_MM,
    (MASTER_ORIGIN_PX.x, MASTER_ORIGIN_PX.y),
    -MASTER_AXIS_TILT_DEG,
)


@dataclass(frozen=True)
class NamedHoleGroup:
    name: str
    pattern: HolePattern
    members: tuple[PlateId, ...]


@dataclass(frozen=True)
class ArmPlacement:
    name: str
    transform: PlanarTransform
    interface: ArmInterface
    motor_center: Point3


@dataclass(frozen=True)
class StandoffDatum:
    name: str
    center: Point2
    lower_z: float
    upper_z: float
    lower_plate: PlateId

    @property
    def height(self) -> float:
        return self.upper_z - self.lower_z


@dataclass(frozen=True)
class FrameLayout:
    dimensions: LayoutParameters
    body_origin: Point2
    root_pattern: HolePattern
    arms: tuple[ArmPlacement, ...]
    hole_groups: tuple[NamedHoleGroup, ...]
    standoffs: tuple[StandoffDatum, ...]

    def body_point(self, x: float, y: float) -> Point2:
        return Point2(x + self.body_origin.x, y + self.body_origin.y)

    def master_to_global(self, u: float, v: float) -> Point2:
        """Scan 1 body observation to global XY; never call this on another loose part."""
        x, y = MASTER_CALIBRATION.to_mm((u, v))
        return self.body_point(x, y)

    def global_to_master(self, point: Point2) -> Point2:
        pixel = MASTER_CALIBRATION.to_pixels(
            (point.x - self.body_origin.x, point.y - self.body_origin.y),
        )
        return Point2(*pixel)

    def plate_hole_groups(self, plate_id: str) -> tuple[NamedHoleGroup, ...]:
        if plate_id not in PLATE_IDS:
            raise ValueError(f"Unknown plate identity: {plate_id}")
        return tuple(group for group in self.hole_groups if plate_id in group.members)

    def arm(self, name: str) -> ArmPlacement:
        for arm in self.arms:
            if arm.name == name:
                return arm
        raise ValueError(f"Unknown arm placement: {name}")

    @property
    def wheelbase(self) -> float:
        """Largest opposite-motor distance, derived rather than independently stored."""
        distances = []
        for side, opposite in (("left", "right"), ("right", "left")):
            a = self.arm(f"arm_front_{side}").motor_center
            b = self.arm(f"arm_rear_{opposite}").motor_center
            distances.append(hypot(a.x - b.x, a.y - b.y))
        return max(distances)


def build_layout(
    frame: FrameParameters,
    dimensions: LayoutParameters | None = None,
) -> FrameLayout:
    dimensions = frame.layout if dimensions is None else dimensions
    profile = frame.arm.profile
    if profile is None:
        raise ValueError("concrete layout requires semantic arm profile dimensions")
    if frame.assembly is not None:
        raise ValueError("concrete shared layout derives placements; custom assembly conflicts")
    radius = profile.root_hole_spacing / 2
    angle = radians(dimensions.canonical_root_angle_deg)
    first = Point2(radius * cos(angle), radius * sin(angle))
    root_pattern = HolePattern((first, Point2(-first.x, -first.y)), frame.clearance_hole_diameter)
    front_angle = 90 - dimensions.front_root_splay_deg - dimensions.canonical_root_angle_deg
    rear_angle = -90 + dimensions.rear_root_splay_deg - (180 - dimensions.canonical_root_angle_deg)
    # Each local first root hole is the outer arm bolt. The second is the inner bolt.
    placements: list[tuple[str, PlanarTransform]] = []
    for end, half_span, y, right_angle, right_mirror in (
        ("front", dimensions.front_root_half_span, dimensions.front_root_y, front_angle, False),
        ("rear", dimensions.rear_root_half_span, dimensions.rear_root_y, rear_angle, True),
    ):
        for side, sign in (("left", -1), ("right", 1)):
            placements.append(
                (
                    f"arm_{end}_{side}",
                    PlanarTransform(
                        Point3(sign * half_span, y, frame.arm_elevation),
                        sign * right_angle,
                        right_mirror if sign == 1 else not right_mirror,
                    ),
                )
            )
    local_motor = Point2(0, profile.root_to_motor)
    motors = tuple(transform.apply(local_motor) for _, transform in placements)
    body_origin = Point2(-sum(p.x for p in motors) / 4, -sum(p.y for p in motors) / 4)
    arms = []
    for name, old in placements:
        transform = PlanarTransform(
            Point3(old.origin.x + body_origin.x, old.origin.y + body_origin.y, old.origin.z),
            old.angle_deg,
            old.mirror_x,
        )
        arms.append(
            ArmPlacement(
                name, transform, ArmInterface(root_pattern, transform), transform.apply(local_motor)
            )
        )

    def body_point(x: float, y: float) -> Point2:
        return Point2(x + body_origin.x, y + body_origin.y)

    groups: list[NamedHoleGroup] = []

    def add_group(
        name: str,
        centers: tuple[Point2, ...],
        members: tuple[PlateId, ...],
        diameter: float | None = None,
    ) -> None:
        groups.append(
            NamedHoleGroup(
                name,
                HolePattern(
                    centers, frame.clearance_hole_diameter if diameter is None else diameter
                ),
                members,
            )
        )

    for end in ("front", "rear"):
        pair = tuple(arm for arm in arms if arm.name.startswith(f"arm_{end}_"))
        add_group(
            f"{end}_arm_outer_pair",
            tuple(a.interface.hole_axes[0] for a in pair),
            ("scan1_body", "scan2_broad", "scan2_long"),
        )
        add_group(
            f"{end}_arm_inner_pair",
            tuple(a.interface.hole_axes[1] for a in pair),
            ("scan1_body", "scan2_broad"),
        )
    for end, span, y, lower in (
        ("front", dimensions.front_tip_half_span, dimensions.front_tip_y, "scan1_body"),
        ("rear", dimensions.rear_tip_half_span, dimensions.rear_tip_y, "scan2_broad"),
    ):
        members: tuple[PlateId, ...] = (
            ("scan1_body", "scan2_long") if lower == "scan1_body" else ("scan2_broad", "scan2_long")
        )
        add_group(
            f"{end}_tip_standoff_pair", tuple(body_point(x, y) for x in (-span, span)), members
        )
    for name, pitch, y, members in (
        ("central_stack_square", frame.stack.primary_pitch, 0.0, ("scan1_body", "scan2_broad")),
        (
            "forward_primary_stack",
            frame.stack.primary_pitch,
            dimensions.forward_stack_y,
            ("scan1_body",),
        ),
        (
            "forward_secondary_stack",
            frame.stack.secondary_pitch,
            dimensions.forward_stack_y,
            ("scan1_body",),
        ),
    ):
        square = HolePattern.rectangle(pitch, pitch, frame.clearance_hole_diameter)
        plate_members: tuple[PlateId, ...] = tuple(
            member for member in PLATE_IDS if member in members
        )
        add_group(name, tuple(body_point(p.x, p.y + y) for p in square.centers), plate_members)
    axial = tuple(
        body_point(0, y)
        for y in (dimensions.central_axis_half_pitch, -dimensions.central_axis_half_pitch)
    )
    lateral = tuple(
        body_point(x, 0)
        for x in (-dimensions.central_lateral_half_pitch, dimensions.central_lateral_half_pitch)
    )
    # Shared axes with different bore roles must not silently become equal bores.
    add_group(
        "central_axis_camera_relief", axial, ("scan1_body",), dimensions.camera_relief_bore_diameter
    )
    add_group("central_axis_bottom_fasteners", axial, ("scan2_broad",))
    add_group(
        "central_lateral_camera_relief",
        lateral,
        ("scan1_body",),
        dimensions.camera_relief_bore_diameter,
    )
    # The source omits the right mark; bilateral interface intent restores its mate.
    add_group("central_lateral_bottom_fasteners", lateral, ("scan2_broad",))
    supports = []
    for group in groups:
        if "scan2_long" not in group.members:
            continue
        lower_plate: PlateId = (
            "scan2_broad" if group.name == "rear_tip_standoff_pair" else "scan1_body"
        )
        lower_z = frame.plate_elevations[lower_plate] + frame.plate(lower_plate).thickness
        for side, center in zip(("left", "right"), group.pattern.centers, strict=True):
            supports.append(
                StandoffDatum(
                    f"standoff_{group.name}_{side}",
                    center,
                    lower_z,
                    frame.plate_elevations["scan2_long"],
                    lower_plate,
                )
            )
    return FrameLayout(
        dimensions, body_origin, root_pattern, tuple(arms), tuple(groups), tuple(supports)
    )
