"""Clearances measured from physical solids and explicitly supplied equipment envelopes."""

from dataclasses import dataclass
from itertools import combinations
from math import isfinite
from typing import TYPE_CHECKING

from build123d import Part

if TYPE_CHECKING:
    from fpv_frame.assembly.frame import FrameAssembly


@dataclass(frozen=True)
class ClearanceEnvelope:
    """Equipment envelope already placed in assembly coordinates (millimeters)."""

    name: str
    shape: Part
    minimum_gap: float

    def __post_init__(self) -> None:
        if not self.name or not isfinite(self.minimum_gap) or self.minimum_gap < 0:
            raise ValueError("Equipment envelope requires a name and nonnegative finite clearance")
        if not self.shape.is_valid or not self.shape.solids():
            raise ValueError("Equipment envelope must contain valid solid geometry")


def _equipment_gap(name: str, a: Part, other_name: str, b: Part, required: float) -> float:
    common = a.intersect(b)
    overlap = 0.0 if common is None else sum(abs(shape.volume) for shape in common)
    distance = a.distance_to(b)
    if overlap > 1e-6 or distance + 1e-6 < required:
        raise ValueError(
            f"{name}: clearance to {other_name} is {distance:.6f} mm; "
            f"required {required:.6f} mm; overlap {overlap:.6f} mm3"
        )
    return distance


def validate_clearances(
    model: "FrameAssembly", envelopes: tuple[ClearanceEnvelope, ...] = ()
) -> dict[str, object]:
    body = model.parts["scan1_body"].bounding_box()
    top = model.parts["scan2_long"].bounding_box()
    gap = top.min.Z - body.max.Z
    if abs(gap - model.params.vertical.top_clearance) > 1e-6:
        raise ValueError("Top plate face clearance differs from the shared vertical stack")
    arm_gaps = {}
    for first, second in combinations(model.layout.arms, 2):
        arm_gaps[f"{first.name}/{second.name}"] = _equipment_gap(
            first.name, model.parts[first.name], second.name, model.parts[second.name],
            model.params.manufacturing.general_clearance,
        )
    measured = {}
    for envelope in envelopes:
        if envelope.name in measured:
            raise ValueError(f"Duplicate equipment envelope: {envelope.name}")
        minimum = float("inf")
        for name, part in model.parts.items():
            distance = _equipment_gap(
                envelope.name, envelope.shape, name, part, envelope.minimum_gap
            )
            minimum = min(minimum, distance)
        measured[envelope.name] = minimum
    equipment_pairs = {}
    for a, b in combinations(envelopes, 2):
        equipment_pairs[f"{a.name}/{b.name}"] = _equipment_gap(
            a.name, a.shape, b.name, b.shape, max(a.minimum_gap, b.minimum_gap)
        )
    return {
        "arm_pair_gaps_mm": arm_gaps,
        "required_arm_gap_mm": model.params.manufacturing.general_clearance,
        "equipment_pair_gaps_mm": equipment_pairs,
        "top_face_clearance_mm": gap,
        "equipment_minimum_gaps_mm": measured,
        "unverified_equipment": sorted({"FC", "ESC", "camera"} - measured.keys()),
        "not_applicable": {
            "side_panels": "No separate side panels identified in the supplied scans and photo."
        },
        "qualification": "Equipment fit is verified only for supplied placed envelopes.",
    }
