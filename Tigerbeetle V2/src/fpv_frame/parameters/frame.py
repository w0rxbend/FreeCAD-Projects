from dataclasses import dataclass, field

from fpv_frame.geometry.datums import ComponentPlacement

from ._validation import positive
from .arms import ArmParameters
from .evidence import PROVISIONAL, ParameterEvidence
from .hardware import HardwareParameters
from .manufacturing import ManufacturingParameters
from .mounting import MotorMountParameters, StackParameters
from .plates import PLATE_IDS, PlateParameters


@dataclass(frozen=True)
class AssemblyLayout:
    """Explicit accepted/provisional placements; no inferred vertical stack order."""

    placements: tuple[ComponentPlacement, ...]
    evidence: ParameterEvidence = PROVISIONAL

    def __post_init__(self) -> None:
        if not isinstance(self.placements, tuple) or not self.placements:
            raise ValueError("assembly placements must be a nonempty immutable tuple")
        names = tuple(placement.name for placement in self.placements)
        if len(set(names)) != len(names):
            raise ValueError("assembly placement names must be unique")


@dataclass(frozen=True)
class VerticalStackParameters:
    """Photo-derived sandwich topology; top clearance is an engineering assumption."""

    top_clearance: float = 25.0
    evidence: ParameterEvidence = PROVISIONAL

    def __post_init__(self) -> None:
        positive("top_clearance", self.top_clearance)


@dataclass(frozen=True)
class FrameParameters:
    arm: ArmParameters
    plates: tuple[PlateParameters, ...]
    stack: StackParameters = field(default_factory=StackParameters)
    motor: MotorMountParameters = field(default_factory=MotorMountParameters)
    hardware: HardwareParameters = field(default_factory=HardwareParameters)
    manufacturing: ManufacturingParameters = field(default_factory=ManufacturingParameters)
    vertical: VerticalStackParameters = field(default_factory=VerticalStackParameters)
    assembly: AssemblyLayout | None = None
    evidence: ParameterEvidence = PROVISIONAL

    def __post_init__(self) -> None:
        if not isinstance(self.plates, tuple):
            raise ValueError("plates must be an immutable tuple")
        ids = tuple(plate.component_id for plate in self.plates)
        if len(ids) != len(set(ids)):
            raise ValueError("plate identities must be unique")
        if set(ids) != set(PLATE_IDS):
            raise ValueError("frame requires all three observed body plates")
        if self.assembly is not None:
            allowed = {*PLATE_IDS, "arm"}
            if any(p.component_id not in allowed for p in self.assembly.placements):
                raise ValueError("assembly references an unmodeled component")

    @property
    def clearance_hole_diameter(self) -> float:
        return self.hardware.bolt_diameter + self.manufacturing.hole_clearance

    def plate(self, component_id: str) -> PlateParameters:
        for plate in self.plates:
            if plate.component_id == component_id:
                return plate
        raise ValueError(f"Unknown plate identity: {component_id}")

    @property
    def arm_elevation(self) -> float:
        return self.plate("scan2_broad").thickness

    @property
    def plate_elevations(self) -> dict[str, float]:
        """Lower faces in mm; bottom-plate lower face defines the Z=0 datum."""
        body_bottom = self.arm_elevation + self.arm.thickness
        body_top = body_bottom + self.plate("scan1_body").thickness
        return {
            "scan2_broad": 0.0,
            "scan1_body": body_bottom,
            "scan2_long": body_top + self.vertical.top_clearance,
        }

    @property
    def short_standoff_height(self) -> float:
        return self.vertical.top_clearance

    @property
    def rear_standoff_height(self) -> float:
        return self.vertical.top_clearance + self.arm.thickness + self.plate("scan1_body").thickness
