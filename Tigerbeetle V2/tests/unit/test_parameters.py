from dataclasses import FrozenInstanceError, replace
from math import inf, nan

import pytest

from fpv_frame.parameters import ArmParameters, FrameParameters, ManufacturingParameters
from fpv_frame.parameters.presets import PRESET_NAMES, get_preset


def test_presets_are_complete_and_explicitly_provisional():
    assert PRESET_NAMES == (
        "reference",
        "default",
        "minimum_supported",
        "maximum_supported",
        "tolerance_test",
    )
    for name in PRESET_NAMES:
        frame = get_preset(name)
        assert isinstance(frame, FrameParameters)
        assert tuple(plate.component_id for plate in frame.plates) == (
            "scan1_body",
            "scan2_broad",
            "scan2_long",
        )
        assert frame.assembly is None
        assert not frame.evidence.verified
        assert frame.evidence.reason
        with pytest.raises(FrozenInstanceError):
            frame.arm.thickness = 99
    assert get_preset("minimum_supported").arm.thickness < get_preset("default").arm.thickness
    assert get_preset("maximum_supported").arm.thickness > get_preset("default").arm.thickness
    assert get_preset("tolerance_test").manufacturing.slot_clearance > 0


@pytest.mark.parametrize("value", [0, -1, inf, -inf, nan, True])
def test_arm_rejects_invalid_dimensions(value):
    with pytest.raises(ValueError, match="thickness"):
        ArmParameters(thickness=value)


@pytest.mark.parametrize("value", [-1, inf, nan, True])
def test_clearance_rejects_invalid_values(value):
    with pytest.raises(ValueError, match="slot_clearance"):
        ManufacturingParameters(slot_clearance=value)


def test_zero_clearance_is_valid_and_unknown_preset_fails():
    assert ManufacturingParameters(slot_clearance=0).slot_clearance == 0
    with pytest.raises(ValueError, match="Unknown preset"):
        get_preset("typo")


def test_frame_rejects_duplicate_component_identity():
    frame = get_preset("reference")
    with pytest.raises(ValueError, match="unique"):
        replace(frame, plates=(frame.plates[0], frame.plates[0], frame.plates[2]))


def test_reference_thicknesses_are_user_measured_but_regression_variants_are_not():
    frame = get_preset("reference")
    assert frame.arm.thickness == 5
    assert frame.arm.thickness_evidence.verified
    assert all(p.thickness == 2 and p.thickness_evidence.verified for p in frame.plates)
    assert not get_preset("minimum_supported").arm.thickness_evidence.verified


def test_vertical_stack_follows_photo_and_recomputes_from_thicknesses():
    frame = get_preset("reference")
    assert frame.plate_elevations == {"scan2_broad": 0, "scan1_body": 7, "scan2_long": 34}
    assert frame.arm_elevation == 2
    assert frame.short_standoff_height == 25
    assert frame.rear_standoff_height == 32
    changed = replace(frame, arm=replace(frame.arm, thickness=6))
    assert changed.plate_elevations["scan1_body"] == 8
    assert changed.plate_elevations["scan2_long"] == 35
    assert changed.rear_standoff_height == 33
    assert changed.short_standoff_height == frame.short_standoff_height


def test_semantic_profile_dimensions_reject_nonfinite_and_invalid_stations():
    from fpv_frame.parameters.arms import ArmProfileParameters
    from fpv_frame.parameters.plates import OutlineStation, PlateProfileParameters

    with pytest.raises(ValueError, match="root_to_motor"):
        ArmProfileParameters(nan, 20, 14, 28, 13)
    with pytest.raises(ValueError, match="ordered"):
        PlateProfileParameters((OutlineStation("rear", 3, 10), OutlineStation("front", 1, 20)))
