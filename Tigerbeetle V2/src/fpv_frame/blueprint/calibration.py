"""Explicit similarity transforms; never assume JPEG pixels are millimeters."""

from dataclasses import dataclass
from math import cos, dist, isfinite, radians, sin
from statistics import median

type Point = tuple[float, float]


def _finite_point(point: Point) -> None:
    if len(point) != 2 or not all(isfinite(value) for value in point):
        raise ValueError("Coordinates must contain two finite values")


@dataclass(frozen=True)
class Anchor:
    """An identified physical distance between two raster observations."""

    name: str
    start_px: Point
    end_px: Point
    distance_mm: float

    def __post_init__(self) -> None:
        _finite_point(self.start_px)
        _finite_point(self.end_px)
        if not self.name or not isfinite(self.distance_mm) or self.distance_mm <= 0:
            raise ValueError("Anchor requires a name and positive finite physical distance")
        if self.start_px == self.end_px:
            raise ValueError("Anchor endpoints must be distinct")

    @property
    def pixels_per_mm(self) -> float:
        return dist(self.start_px, self.end_px) / self.distance_mm


@dataclass(frozen=True)
class Calibration:
    """Map scan pixels to a part's engineering plane (+X right, +Y up).

    Rotation is counterclockwise after removing the raster Y inversion.
    Assembly placement is a separate transform; this does not infer front/rear.
    """

    pixels_per_mm: float
    origin_px: Point = (0, 0)
    rotation_degrees: float = 0
    maximum_relative_residual: float = 0

    def __post_init__(self) -> None:
        _finite_point(self.origin_px)
        if not isfinite(self.pixels_per_mm) or self.pixels_per_mm <= 0:
            raise ValueError("Scale must be positive and finite")
        if not isfinite(self.rotation_degrees):
            raise ValueError("Rotation must be finite")
        if not isfinite(self.maximum_relative_residual) or self.maximum_relative_residual < 0:
            raise ValueError("Residual must be finite and nonnegative")

    def to_mm(self, point: Point) -> Point:
        _finite_point(point)
        x = (point[0] - self.origin_px[0]) / self.pixels_per_mm
        y = (self.origin_px[1] - point[1]) / self.pixels_per_mm
        angle = radians(self.rotation_degrees)
        return x * cos(angle) - y * sin(angle), x * sin(angle) + y * cos(angle)

    def to_pixels(self, point: Point) -> Point:
        _finite_point(point)
        angle = radians(-self.rotation_degrees)
        x = point[0] * cos(angle) - point[1] * sin(angle)
        y = point[0] * sin(angle) + point[1] * cos(angle)
        return (self.origin_px[0] + x * self.pixels_per_mm,
                self.origin_px[1] - y * self.pixels_per_mm)


def calibrate(
    anchors: tuple[Anchor, ...],
    *,
    origin_px: Point = (0, 0),
    rotation_degrees: float = 0,
    relative_tolerance: float = 0.02,
) -> Calibration:
    """Reconcile independent anchors only if their scales agree within tolerance.

    Two anchors guard against transcription errors; callers must still document
    the physical evidence that identifies them. Agreement alone is not proof of
    an assumed mounting standard.
    """
    if len(anchors) < 2:
        raise ValueError("Calibration requires at least two independent anchors")
    segments = {frozenset((anchor.start_px, anchor.end_px)) for anchor in anchors}
    if len(segments) != len(anchors) or len({a.name for a in anchors}) != len(anchors):
        raise ValueError("Calibration anchors must have distinct names and segments")
    if not isfinite(relative_tolerance) or not 0 < relative_tolerance < 1:
        raise ValueError("Relative tolerance must lie between zero and one")
    scales = [anchor.pixels_per_mm for anchor in anchors]
    scale = median(scales)
    residual = max(abs(value - scale) / scale for value in scales)
    if residual > relative_tolerance:
        details = ", ".join(f"{a.name}={a.pixels_per_mm:.4g} px/mm" for a in anchors)
        raise ValueError(f"Calibration anchors disagree: {details}; residual={residual:.2%}")
    return Calibration(scale, origin_px, rotation_degrees, residual)
