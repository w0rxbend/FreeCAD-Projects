"""Kernel-independent coordinates: +X right, +Y front, +Z up; lengths in mm."""

from dataclasses import dataclass
from math import cos, isfinite, radians, sin


def _finite(name: str, value: float) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value):
        raise ValueError(f"{name} must be a finite number")


@dataclass(frozen=True)
class Point2:
    x: float
    y: float

    def __post_init__(self) -> None:
        _finite("x", self.x)
        _finite("y", self.y)


@dataclass(frozen=True)
class Point3:
    x: float
    y: float
    z: float

    def __post_init__(self) -> None:
        _finite("x", self.x)
        _finite("y", self.y)
        _finite("z", self.z)


ORIGIN = Point3(0, 0, 0)


@dataclass(frozen=True)
class PlanarTransform:
    """Reflect local X, rotate about +Z, then translate. Reflection preserves handed roots.

    Apply the same transform to a part profile and every one of its interfaces.
    Mirror is an actual reflection; a Z rotation cannot replace it for asymmetric arms.
    """

    origin: Point3 = ORIGIN
    angle_deg: float = 0.0
    mirror_x: bool = False

    def __post_init__(self) -> None:
        _finite("angle_deg", self.angle_deg)
        if not isinstance(self.origin, Point3) or not isinstance(self.mirror_x, bool):
            raise ValueError("transform requires a Point3 origin and boolean mirror_x")

    def apply(self, point: Point2) -> Point3:
        angle = radians(self.angle_deg)
        x = -point.x if self.mirror_x else point.x
        return Point3(
            self.origin.x + x * cos(angle) - point.y * sin(angle),
            self.origin.y + x * sin(angle) + point.y * cos(angle),
            self.origin.z,
        )


@dataclass(frozen=True)
class ComponentPlacement:
    name: str
    component_id: str
    transform: PlanarTransform

    def __post_init__(self) -> None:
        if not self.name.strip() or not self.component_id.strip():
            raise ValueError("component placement requires nonempty names")
