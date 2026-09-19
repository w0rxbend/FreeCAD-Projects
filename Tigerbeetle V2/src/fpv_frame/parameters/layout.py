"""Named engineering datums, rounded from A4-calibrated shared scan features.

Coordinates refer to the central electronics square until the geometry factory
recenters the whole frame on the four motor centers. They are not assembly nudges.
"""

from dataclasses import dataclass

from ._validation import finite, positive
from .evidence import ParameterEvidence

LAYOUT_EVIDENCE = ParameterEvidence(
    reason=(
        "Shared scan pairs idealized bilaterally and rounded to engineering dimensions; "
        "see references/measurements/combined.yaml for reconciled observations."
    ),
    sources=("references/measurements/combined.yaml",),
    confidence="medium",
    method="inferred_from_interface",
)


@dataclass(frozen=True)
class LayoutParameters:
    front_root_half_span: float = 27.75
    rear_root_half_span: float = 26.25
    front_root_y: float = 25.0
    rear_root_y: float = -26.5
    front_root_splay_deg: float = 6.5
    rear_root_splay_deg: float = -1.5
    canonical_root_angle_deg: float = 142.7
    front_tip_half_span: float = 19.0
    front_tip_y: float = 109.0
    rear_tip_half_span: float = 16.5
    rear_tip_y: float = -94.0
    forward_stack_y: float = 61.5
    central_axis_half_pitch: float = 18.0
    central_lateral_half_pitch: float = 18.0
    camera_relief_bore_diameter: float = 5.5
    evidence: ParameterEvidence = LAYOUT_EVIDENCE

    def __post_init__(self) -> None:
        for name in (
            "front_root_half_span",
            "rear_root_half_span",
            "front_tip_half_span",
            "rear_tip_half_span",
            "central_axis_half_pitch",
            "central_lateral_half_pitch",
            "camera_relief_bore_diameter",
            "forward_stack_y",
        ):
            positive(name, getattr(self, name))
        for name in (
            "front_root_y",
            "rear_root_y",
            "front_tip_y",
            "rear_tip_y",
            "front_root_splay_deg",
            "rear_root_splay_deg",
            "canonical_root_angle_deg",
        ):
            finite(name, getattr(self, name))
        if not self.rear_tip_y < self.rear_root_y < 0 < self.front_root_y < self.front_tip_y:
            raise ValueError("tip and arm stations must be ordered rear to front around stack")
        if not 0 < self.canonical_root_angle_deg < 180:
            raise ValueError("canonical root first hole must lie in the forward local half-plane")
        if abs(self.front_root_splay_deg) >= 45 or abs(self.rear_root_splay_deg) >= 45:
            raise ValueError("root bolt rows must remain predominantly longitudinal")
