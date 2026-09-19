from dataclasses import dataclass

from ._validation import positive
from .evidence import PROVISIONAL, ParameterEvidence


@dataclass(frozen=True)
class HardwareParameters:
    """Nominal dimensions; manufacturing hole allowance is applied separately."""

    bolt_diameter: float = 3.0
    standoff_outer_diameter: float = 5.0
    evidence: ParameterEvidence = PROVISIONAL

    def __post_init__(self) -> None:
        positive("bolt_diameter", self.bolt_diameter)
        positive("standoff_outer_diameter", self.standoff_outer_diameter)
        if self.standoff_outer_diameter <= self.bolt_diameter:
            raise ValueError("standoff outer diameter must exceed bolt diameter")
