from dataclasses import dataclass
from typing import Literal

from ._validation import finite, positive
from .evidence import PROVISIONAL, ParameterEvidence

PlateId = Literal["scan1_body", "scan2_broad", "scan2_long"]
PLATE_IDS: tuple[PlateId, ...] = ("scan1_body", "scan2_broad", "scan2_long")


@dataclass(frozen=True)
class OutlineStation:
    """Named longitudinal design station, shared by mathematically mirrored plate edges."""

    name: str
    axial_position: float
    half_width: float

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("outline station requires a semantic name")
        finite("axial_position", self.axial_position)
        positive("half_width", self.half_width)


@dataclass(frozen=True)
class PlateProfileParameters:
    stations: tuple[OutlineStation, ...]
    evidence: ParameterEvidence = PROVISIONAL

    def __post_init__(self) -> None:
        if not isinstance(self.stations, tuple) or len(self.stations) < 2:
            raise ValueError("plate profile requires at least two immutable outline stations")
        if len({station.name for station in self.stations}) != len(self.stations):
            raise ValueError("outline station names must be unique")
        positions = [station.axial_position for station in self.stations]
        if any(a >= b for a, b in zip(positions, positions[1:], strict=False)):
            raise ValueError("outline stations must be ordered rear to front")


@dataclass(frozen=True)
class PlateParameters:
    """Source identity is stable while physical top/bottom roles remain unresolved."""

    component_id: PlateId
    thickness: float
    evidence: ParameterEvidence = PROVISIONAL
    thickness_evidence: ParameterEvidence = PROVISIONAL
    profile: PlateProfileParameters | None = None

    def __post_init__(self) -> None:
        if self.component_id not in PLATE_IDS:
            raise ValueError(f"Unknown plate identity: {self.component_id}")
        positive("thickness", self.thickness)
