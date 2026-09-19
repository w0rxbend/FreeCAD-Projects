"""Configurable design envelopes; these are not measurements of the user's hardware."""

from dataclasses import dataclass, fields

from ._validation import positive
from .evidence import ParameterEvidence

EQUIPMENT_EVIDENCE = ParameterEvidence(
    reason=(
        "Nominal supported design envelopes selected for clearance assessment; "
        "no FC, ESC, camera, or stack hardware dimensions supplied by the user."
    ),
    sources=("docs/equipment.md",),
    method="engineering_assumption",
)


@dataclass(frozen=True)
class EquipmentParameters:
    """All dimensions in mm; boards align with the shared central stack axes."""

    fc_width: float = 40.0
    fc_length: float = 40.0
    fc_height: float = 8.0
    esc_width: float = 40.0
    esc_length: float = 40.0
    esc_height: float = 8.0
    camera_width: float = 20.0
    camera_length: float = 20.0
    camera_height: float = 20.0
    stack_bottom_gap: float = 3.0
    board_gap: float = 3.0
    camera_bottom_gap: float = 2.0
    camera_front_inset: float = 14.0
    stack_hardware_diameter: float = 5.0
    stack_keepout_diameter: float = 6.0
    minimum_gap: float = 0.2
    evidence: ParameterEvidence = EQUIPMENT_EVIDENCE

    def __post_init__(self) -> None:
        for item in fields(self):
            if item.name != "evidence":
                positive(item.name, getattr(self, item.name))
        if self.stack_keepout_diameter < self.stack_hardware_diameter + 2 * self.minimum_gap:
            raise ValueError("PCB keepout diameter must provide the required hardware clearance")
