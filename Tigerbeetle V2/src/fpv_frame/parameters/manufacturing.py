from dataclasses import dataclass

from ._validation import finite, nonnegative, positive
from .evidence import PROVISIONAL, ParameterEvidence


@dataclass(frozen=True)
class ManufacturingParameters:
    """Clearances are total dimensional additions, not per-side offsets (mm)."""

    general_clearance: float = 0.2
    slot_clearance: float = 0.2
    hole_clearance: float = 0.2
    press_fit_clearance: float = -0.05
    printed_part_clearance: float = 0.3
    edge_minimum: float = 1.5
    hardware_wall_minimum: float = 1.0
    fillet_radius: float = 1.0
    linear_tolerance: float = 0.05
    angular_tolerance: float = 0.1
    evidence: ParameterEvidence = PROVISIONAL

    def __post_init__(self) -> None:
        for name in (
            "general_clearance",
            "slot_clearance",
            "hole_clearance",
            "printed_part_clearance",
        ):
            nonnegative(name, getattr(self, name))
        finite("press_fit_clearance", self.press_fit_clearance)
        for name in (
            "edge_minimum", "hardware_wall_minimum", "fillet_radius",
            "linear_tolerance", "angular_tolerance",
        ):
            positive(name, getattr(self, name))
