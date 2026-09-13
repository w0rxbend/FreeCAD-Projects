"""Quantitative source-fit diagnostics with explicit measurement limitations."""

import json
from bisect import bisect_left
from math import dist, isfinite, sqrt
from pathlib import Path
from statistics import mean
from typing import Any

from build123d import Face
from PIL import Image

from fpv_frame.blueprint.calibration import Point
from fpv_frame.blueprint.overlay import ProfileOverlay, profile_polylines


class InkIndex:
    """Sorted source-ink pixels by row; exact nearest-pixel Euclidean distance."""

    def __init__(self, rows: dict[int, tuple[int, ...]]) -> None:
        self.rows = {y: tuple(sorted(xs)) for y, xs in rows.items() if xs}
        if not self.rows:
            raise ValueError("No red source ink detected")
        self.ys = sorted(self.rows)

    @classmethod
    def from_scan(cls, path: Path) -> "InkIndex":
        rows: dict[int, list[int]] = {}
        with Image.open(path) as source:
            rgb = source.convert("RGB")
            width = rgb.width
            for index, pixel in enumerate(rgb.getdata()):
                r, g, b = pixel
                if r > g + 25 and r > b + 12 and g < 200:
                    rows.setdefault(index // width, []).append(index % width)
        return cls({y: tuple(xs) for y, xs in rows.items()})

    def distance(self, point: Point) -> float:
        x, y = point
        if not isfinite(x) or not isfinite(y):
            raise ValueError("Query coordinates must be finite")
        pivot = bisect_left(self.ys, y)
        left, right, best = pivot - 1, pivot, float("inf")
        while left >= 0 or right < len(self.ys):
            if left >= 0 and (right == len(self.ys) or y - self.ys[left] <= self.ys[right] - y):
                row = self.ys[left]
                left -= 1
            else:
                row = self.ys[right]
                right += 1
            dy2 = (row - y) ** 2
            if dy2 >= best:
                break
            xs = self.rows[row]
            position = bisect_left(xs, x)
            for candidate in xs[max(0, position - 1) : position + 1]:
                best = min(best, (candidate - x) ** 2 + dy2)
        return sqrt(best)


def nearest_feature_errors(
    measured: dict[str, Point],
    generated_px: tuple[Point, ...],
    *,
    pixels_per_mm: float,
) -> dict[str, float]:
    if not generated_px:
        raise ValueError("No generated circular holes available for comparison")
    if not isfinite(pixels_per_mm) or pixels_per_mm <= 0:
        raise ValueError("Scale must be positive and finite")
    return {
        name: min(dist(point, candidate) for candidate in generated_px) / pixels_per_mm
        for name, point in measured.items()
    }


def _measured_holes(root: Path, scan: str, component: str) -> dict[str, Point]:
    data = json.loads((root / f"references/measurements/{scan}.yaml").read_text())
    if scan == "Scan_1":
        prefix = "plate_" if component == "scan1_body" else component + "_"
        return {
            name: tuple(value["value"])
            for name, value in data["feature_centers"].items()
            if name.startswith(prefix)
        }
    key = "broad_plate" if component == "scan2_broad" else "long_plate"
    return {
        name: tuple(value["value"]["center"])
        for name, value in data["components"][key]["holes"].items()
    }


def fit_report(
    root: Path,
    overlays: dict[str, tuple[ProfileOverlay, ...]],
) -> dict[str, Any]:
    """Measure CAD exterior→red ink and observed circular centers→CAD centers.

    Exterior samples use the nearest source red pixel; this directed metric is
    optimistic by ink half-width and may match another nearby stroke. It cannot
    prove missing-feature absence or replace independent full-overlay review.
    Nearest-center matching is diagnostic; actual mating axes have BREP tests.
    """
    result: dict[str, Any] = {
        "schema_version": 1,
        "method": "CAD exterior to nearest red source pixel; observed circular centers to CAD",
        "limitations": (
            "Directed ink distance is optimistic by stroke half-width; visual review required"
        ),
        "sampling_step_mm": 0.25,
        "scans": {},
    }
    for scan, components in overlays.items():
        ink = InkIndex.from_scan(root / f"references/source/{scan}.jpeg")
        reports = {}
        for item in components:
            distances = [
                ink.distance(item.calibration.to_pixels(point)) / item.calibration.pixels_per_mm
                for line in profile_polylines(Face(item.profile.faces()[0].outer_wire()))
                for point in line
            ]
            holes = nearest_feature_errors(
                _measured_holes(root, scan, item.name),
                tuple(item.calibration.to_pixels(point) for point in item.hole_centers),
                pixels_per_mm=item.calibration.pixels_per_mm,
            )
            reports[item.name] = {
                "max_outline_deviation_mm": max(distances),
                "mean_outline_deviation_mm": mean(distances),
                "critical_hole_max_deviation_mm": max(holes.values(), default=0),
                "hole_residuals_mm": holes,
                "outline_sample_count": len(distances),
            }
        result["scans"][scan + ".jpeg"] = reports
    return result
