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
    root_depth: float = 31.0
    motor_tip_extension: float = 25.0
    motor_neck_length: float = 25.0
    motor_waist_width: float = 20.5
    diamond_width: float = 7.0
    diamond_height: float = 10.0
    diamond_offset: float = 15.5

    def __post_init__(self) -> None:
        for name in (
            "root_to_motor",
            "root_width",
            "shaft_width",
            "motor_paddle_width",
            "root_hole_spacing",
            "root_depth",
            "motor_tip_extension",
            "motor_neck_length",
            "motor_waist_width",
            "diamond_width",
            "diamond_height",
            "diamond_offset",
        ):
            positive(name, getattr(self, name))
        if self.shaft_width >= self.motor_waist_width:
            raise ValueError("shaft width must be smaller than the motor waist")
        if self.motor_waist_width >= self.motor_paddle_width:
            raise ValueError("motor waist must be smaller than the paddle width")
        if self.root_to_motor <= self.motor_neck_length:
            raise ValueError("root_to_motor must exceed motor_neck_length")
        if self.diamond_offset + self.diamond_height / 2 >= self.motor_tip_extension:
            raise ValueError("diamond opening must remain inside the motor tip")


@dataclass(frozen=True)
class ArmParameters:
    """One canonical arm; contour data and handed placements are separate."""

    thickness: float
    evidence: ParameterEvidence = PROVISIONAL
    thickness_evidence: ParameterEvidence = PROVISIONAL
    profile: ArmProfileParameters | None = None

    def __post_init__(self) -> None:
        positive("thickness", self.thickness)


def reference_arm_profile() -> ArmProfileParameters:
    """Nominal engineering dimensions from A4-calibrated sparse Scan 1 observations."""
    return ArmProfileParameters(
        root_to_motor=115.0,
        root_width=35.0,
        root_depth=29.0,
        shaft_width=12.0,
        motor_paddle_width=24.0,
        root_hole_spacing=13.75,
        evidence=ParameterEvidence(
            reason=(
                "A4-calibrated arm A/B reconstruction: motor distance 114.66/115.59 mm, "
                "shaft about 12 mm, paddle about 24 mm, traced root envelope about 38 x 31 mm. "
                "Root envelope reconstructed at 35 x 29 mm to clear all four mirrored "
                "placements by at least 0.29 mm without moving shared bolt axes; this "
                "local engineering departure from the tracing needs physical confirmation. "
                "13.75 mm root pitch reconciles plate/root holes within pen uncertainty. "
                "Sparse analytical contour and root notch need overlay/assembly review."
            ),
            sources=(
                "references/measurements/combined.yaml",
                "Scan_1.jpeg sparse row observations",
            ),
            confidence="medium",
            method="cross_scan_measurement",
        ),
    )
