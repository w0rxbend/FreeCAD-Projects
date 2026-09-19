"""Reusable nominal mounting patterns; no CAD kernel or export dependency."""

from dataclasses import dataclass
from math import cos, radians, sin

from fpv_frame.parameters._validation import finite, positive

from .datums import PlanarTransform, Point2, Point3


@dataclass(frozen=True)
class HolePattern:
    centers: tuple[Point2, ...]
    hole_diameter: float

    def __post_init__(self) -> None:
        positive("hole_diameter", self.hole_diameter)
        if not isinstance(self.centers, tuple) or not self.centers:
            raise ValueError("hole centers must be a nonempty immutable tuple")
        if not all(isinstance(point, Point2) for point in self.centers):
            raise ValueError("hole centers must be Point2 values")
        if len(set(self.centers)) != len(self.centers):
            raise ValueError("hole centers must be unique")

    @classmethod
    def rectangle(cls, pitch_x: float, pitch_y: float, hole_diameter: float) -> "HolePattern":
        positive("pitch_x", pitch_x)
        positive("pitch_y", pitch_y)
        return cls(
            tuple(
                Point2(x * pitch_x / 2, y * pitch_y / 2)
                for x, y in ((-1, -1), (1, -1), (1, 1), (-1, 1))
            ),
            hole_diameter,
        )

    @classmethod
    def bolt_circle(
        cls,
        diameter: float,
        count: int,
        hole_diameter: float,
        angle_deg: float = 0,
    ) -> "HolePattern":
        positive("bolt_circle_diameter", diameter)
        finite("angle_deg", angle_deg)
        if isinstance(count, bool) or not isinstance(count, int) or count < 2:
            raise ValueError("bolt circle requires an integer count of at least two")
        return cls(
            tuple(
                Point2(
                    diameter / 2 * cos(radians(angle_deg + index * 360 / count)),
                    diameter / 2 * sin(radians(angle_deg + index * 360 / count)),
                )
                for index in range(count)
            ),
            hole_diameter,
        )

    def placed(self, transform: PlanarTransform) -> tuple[Point3, ...]:
        return tuple(transform.apply(center) for center in self.centers)


@dataclass(frozen=True)
class RectangleFeature:
    center: Point2
    width: float
    height: float
    angle_deg: float = 0

    def __post_init__(self) -> None:
        positive("width", self.width)
        positive("height", self.height)
        finite("angle_deg", self.angle_deg)
