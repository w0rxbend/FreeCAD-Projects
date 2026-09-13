from dataclasses import dataclass

from ._validation import positive
from .evidence import PROVISIONAL, ParameterEvidence


@dataclass(frozen=True)
class ArmProfileParameters:
    """Primary arm dimensions; root asymmetry remains in the canonical profile builder."""

    root_to_motor: float
    root_width: float
    shaft_width: float
    motor_paddle_width: float
    root_hole_spacing: float
    evidence: ParameterEvidence = PROVISIONAL

    def __post_init__(self) -> None:
        for name in (
            "root_to_motor",
            "root_width",
            "shaft_width",
            "motor_paddle_width",
            "root_hole_spacing",
        ):
            positive(name, getattr(self, name))


@dataclass(frozen=True)
class ArmParameters:
    """One canonical arm; contour data and handed placements are separate."""

    thickness: float
    evidence: ParameterEvidence = PROVISIONAL
    thickness_evidence: ParameterEvidence = PROVISIONAL
    profile: ArmProfileParameters | None = None

    def __post_init__(self) -> None:
        positive("thickness", self.thickness)
