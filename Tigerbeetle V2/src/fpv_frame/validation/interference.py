"""Check every material pair; coplanar surface contacts have zero overlap volume."""

from itertools import combinations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fpv_frame.assembly.frame import FrameAssembly

VOLUME_TOLERANCE = 1e-6


def validate_interference(model: "FrameAssembly") -> dict[str, object]:
    maximum = 0.0
    checked = 0
    for (name_a, a), (name_b, b) in combinations(model.parts.items(), 2):
        checked += 1
        bounds_a, bounds_b = a.bounding_box(), b.bounding_box()
        # Broad phase preserves exact checks for any positive 3D overlap.
        if any(
            min(getattr(bounds_a.max, axis), getattr(bounds_b.max, axis))
            - max(getattr(bounds_a.min, axis), getattr(bounds_b.min, axis))
            <= 1e-7
            for axis in ("X", "Y", "Z")
        ):
            continue
        common = a.intersect(b)
        volume = 0.0 if common is None else sum(abs(shape.volume) for shape in common)
        maximum = max(maximum, volume)
        if volume > VOLUME_TOLERANCE:
            raise ValueError(
                f"material interference: {name_a} / {name_b}: {volume:.8f} mm3 overlap"
            )
    return {
        "checked_pairs": checked,
        "maximum_overlap_mm3": maximum,
        "allowed_material_overlaps": [],
    }
