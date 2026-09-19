"""Mating relationships generate both components' features from shared definitions.

TabSlotInterface is available for future evidenced joints; observed plate apertures
are not automatically classified as tab slots and no side panels are implied.
"""

from dataclasses import dataclass

from fpv_frame.parameters._validation import finite, nonnegative, positive

from .datums import PlanarTransform, Point2, Point3
from .patterns import HolePattern, RectangleFeature


@dataclass(frozen=True)
class PlateInterface:
    """One XY bolt pattern shared by horizontal plates at explicit Z datums."""

    name: str
    pattern: HolePattern
    elevations: tuple[float, ...]

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("plate interface requires a name")
        if not isinstance(self.elevations, tuple) or len(self.elevations) < 2:
            raise ValueError("plate interface requires at least two immutable elevations")
        for elevation in self.elevations:
            finite("elevation", elevation)

    def holes_at(self, plane_index: int) -> tuple[Point3, ...]:
        if plane_index < 0 or plane_index >= len(self.elevations):
            raise IndexError("plate interface plane index out of range")
        transform = PlanarTransform(origin=Point3(0, 0, self.elevations[plane_index]))
        return self.pattern.placed(transform)


@dataclass(frozen=True)
class ArmInterface:
    """Canonical root holes transformed once for both arm and receiving plate."""

    root_pattern: HolePattern
    placement: PlanarTransform

    @property
    def hole_axes(self) -> tuple[Point2, ...]:
        return tuple(Point2(point.x, point.y) for point in self.root_pattern.placed(self.placement))

    def holes_at(self, elevation: float) -> tuple[Point3, ...]:
        return tuple(Point3(point.x, point.y, elevation) for point in self.hole_axes)


@dataclass(frozen=True)
class TabSlotInterface:
    name: str
    center: Point2
    tab_width: float
    tab_thickness: float
    slot_clearance: float
    angle_deg: float = 0

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("tab-slot interface requires a name")
        positive("tab_width", self.tab_width)
        positive("tab_thickness", self.tab_thickness)
        nonnegative("slot_clearance", self.slot_clearance)
        finite("angle_deg", self.angle_deg)

    def tab(self) -> RectangleFeature:
        return RectangleFeature(self.center, self.tab_width, self.tab_thickness, self.angle_deg)

    def slot_cutout(self) -> RectangleFeature:
        return RectangleFeature(
            self.center,
            self.tab_width + self.slot_clearance,
            self.tab_thickness + self.slot_clearance,
            self.angle_deg,
        )
