"""Provenance distinguishes design assumptions from physically verified dimensions."""

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class ParameterEvidence:
    reason: str
    sources: tuple[str, ...] = ()
    verified: bool = False
    confidence: Literal["known", "high", "medium", "low", "estimated"] = "estimated"
    method: str = "estimated"

    def __post_init__(self) -> None:
        if not self.reason.strip():
            raise ValueError("evidence requires a reason")
        if not isinstance(self.sources, tuple):
            raise ValueError("evidence sources must be an immutable tuple")
        if self.verified and not self.sources:
            raise ValueError("verified evidence requires a physical source")


PROVISIONAL = ParameterEvidence(
    reason="Engineering assumptions for reconstruction development; physical dimensions unverified."
)

USER_THICKNESS = ParameterEvidence(
    reason="User confirmed arm thickness 5 mm and all three plate thicknesses 2 mm.",
    sources=("user instruction: arm 5 mm, plate 2 mm",),
    verified=True,
    confidence="known",
    method="direct_measurement",
)
