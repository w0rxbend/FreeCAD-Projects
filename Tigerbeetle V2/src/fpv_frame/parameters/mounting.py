from dataclasses import dataclass

from ._validation import positive
from .evidence import PROVISIONAL, ParameterEvidence


@dataclass(frozen=True)
class StackParameters:
    """Pitch hypotheses; these do not prescribe a board clearance envelope."""

    primary_pitch: float = 30.5
    secondary_pitch: float = 20.0
    evidence: ParameterEvidence = PROVISIONAL

    def __post_init__(self) -> None:
        positive("primary_pitch", self.primary_pitch)
        positive("secondary_pitch", self.secondary_pitch)


@dataclass(frozen=True)
class MotorMountParameters:
    """Four holes on a bolt circle: diameter means opposite-hole distance."""

    bolt_circle_diameter: float = 19.0
    center_bore_diameter: float = 6.5
    evidence: ParameterEvidence = PROVISIONAL

    def __post_init__(self) -> None:
        positive("bolt_circle_diameter", self.bolt_circle_diameter)
        positive("center_bore_diameter", self.center_bore_diameter)
        if self.center_bore_diameter >= self.bolt_circle_diameter:
            raise ValueError("center bore diameter must be smaller than motor bolt circle")
