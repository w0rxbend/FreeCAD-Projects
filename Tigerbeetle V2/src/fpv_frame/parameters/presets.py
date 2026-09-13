"""Development presets, not validated manufacturing ranges or measured dimensions."""

from dataclasses import replace

from .arms import ArmParameters, ArmProfileParameters
from .evidence import PROVISIONAL, USER_THICKNESS, ParameterEvidence
from .frame import FrameParameters
from .plates import PLATE_IDS, PlateParameters

PRESET_NAMES = (
    "reference",
    "default",
    "minimum_supported",
    "maximum_supported",
    "tolerance_test",
)


def get_preset(name: str = "default") -> FrameParameters:
    if name not in PRESET_NAMES:
        raise ValueError(f"Unknown preset {name!r}; choose one of {', '.join(PRESET_NAMES)}")
    evidence = ParameterEvidence(
        reason=(
            f"{name}: provisional reconstruction assumptions. "
            "Reference thicknesses user-confirmed; "
            "fits, heights and motor dimensions unverified. Minimum/maximum are regression cases."
        ),
        sources=("references/measurements/Scan_1.yaml", "references/measurements/Scan_2.yaml"),
    )
    frame = FrameParameters(
        arm=ArmParameters(
            thickness=5.0,
            thickness_evidence=USER_THICKNESS,
            profile=ArmProfileParameters(
                root_to_motor=115.0,
                root_width=37.0,
                shaft_width=15.0,
                motor_paddle_width=24.0,
                root_hole_spacing=13.75,
                evidence=ParameterEvidence(
                    reason="A4 calibrated nominal arm dimensions; contour overlay review pending",
                    sources=("references/measurements/combined.yaml",),
                ),
            ),
        ),
        plates=tuple(
            PlateParameters(identity, thickness=2.0, thickness_evidence=USER_THICKNESS)
            for identity in PLATE_IDS
        ),
        evidence=evidence,
    )
    if name == "minimum_supported":
        return replace(
            frame,
            arm=replace(frame.arm, thickness=3.0, thickness_evidence=PROVISIONAL),
            plates=tuple(
                replace(plate, thickness=1.5, thickness_evidence=PROVISIONAL)
                for plate in frame.plates
            ),
        )
    if name == "maximum_supported":
        return replace(
            frame,
            arm=replace(frame.arm, thickness=7.0, thickness_evidence=PROVISIONAL),
            plates=tuple(
                replace(plate, thickness=3.0, thickness_evidence=PROVISIONAL)
                for plate in frame.plates
            ),
        )
    if name == "tolerance_test":
        return replace(
            frame,
            manufacturing=replace(
                frame.manufacturing,
                slot_clearance=0.35,
                hole_clearance=0.3,
            ),
        )
    return frame
