"""Fit shared planar datums without hiding mismatched features or reflections."""

from dataclasses import dataclass
from math import atan2, degrees, dist, hypot, isfinite

from fpv_frame.blueprint.calibration import Calibration, Point, _finite_point


@dataclass(frozen=True)
class Correspondence:
    name: str
    pixel: Point
    datum_mm: Point

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("Correspondence requires a feature name")
        _finite_point(self.pixel)
        _finite_point(self.datum_mm)


@dataclass(frozen=True)
class Registration:
    calibration: Calibration
    residuals_mm: tuple[tuple[str, float], ...]

    @property
    def maximum_error_mm(self) -> float:
        return max(error for _, error in self.residuals_mm)

    @property
    def mean_error_mm(self) -> float:
        return sum(error for _, error in self.residuals_mm) / len(self.residuals_mm)


def _center(points: tuple[Point, ...]) -> Point:
    return (sum(x for x, _ in points) / len(points), sum(y for _, y in points) / len(points))


def _check_spread(points: tuple[Point, ...]) -> None:
    cx, cy = _center(points)
    xx = sum((x - cx) ** 2 for x, _ in points)
    yy = sum((y - cy) ** 2 for _, y in points)
    xy = sum((x - cx) * (y - cy) for x, y in points)
    if xx * yy - xy * xy <= 1e-12 * (xx + yy) ** 2:
        raise ValueError("Registration features must not be coincident or collinear")


def register(features: tuple[Correspondence, ...], *, maximum_error_mm: float) -> Registration:
    """Least-squares similarity fit of pixels to shared engineering datums.

    Targets must be independently justified. This fit measures agreement and
    cannot establish physical scale merely because a familiar pattern fits.
    Raster Y inversion is explicit; reflections of physical parts are separate.
    """
    if not isfinite(maximum_error_mm) or maximum_error_mm <= 0:
        raise ValueError("Maximum registration error must be positive and finite")
    if len(features) < 3 or len({f.name for f in features}) != len(features):
        raise ValueError("Registration requires at least three uniquely named features")
    source = tuple((f.pixel[0], -f.pixel[1]) for f in features)
    target = tuple(f.datum_mm for f in features)
    if len(set(source)) != len(source) or len(set(target)) != len(target):
        raise ValueError("Registration features must have distinct positions")
    _check_spread(source)
    _check_spread(target)
    sx, sy = _center(source)
    tx, ty = _center(target)
    denominator = sum((x - sx) ** 2 + (y - sy) ** 2 for x, y in source)
    a = (
        sum(
            (x - sx) * (u - tx) + (y - sy) * (v - ty)
            for (x, y), (u, v) in zip(source, target, strict=True)
        )
        / denominator
    )
    b = (
        sum(
            (x - sx) * (v - ty) - (y - sy) * (u - tx)
            for (x, y), (u, v) in zip(source, target, strict=True)
        )
        / denominator
    )
    scale = hypot(a, b)
    if scale <= 1e-12:
        raise ValueError("Registration has no nondegenerate similarity transform")
    ox = sx - (a * tx + b * ty) / scale**2
    oy = sy - (-b * tx + a * ty) / scale**2
    calibration = Calibration(1 / scale, (ox, -oy), degrees(atan2(b, a)))
    residuals = tuple((f.name, dist(calibration.to_mm(f.pixel), f.datum_mm)) for f in features)
    result = Registration(calibration, residuals)
    if result.maximum_error_mm > maximum_error_mm:
        raise ValueError(
            f"Shared-feature residual {result.maximum_error_mm:.3f} mm exceeds "
            f"{maximum_error_mm:.3f} mm: {dict(residuals)}"
        )
    return result
