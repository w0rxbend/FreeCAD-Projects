from dataclasses import replace

import pytest

from fpv_frame.assembly import build_assembly
from fpv_frame.parameters.equipment import EquipmentParameters
from fpv_frame.parameters.presets import get_preset
from fpv_frame.validation.clearances import validate_clearances
from fpv_frame.validation.equipment import design_equipment_envelopes


@pytest.fixture(scope="module")
def model():
    return build_assembly(get_preset())


def test_nominal_design_equipment_clears_actual_frame_and_other_equipment(model):
    envelopes = design_equipment_envelopes(model, EquipmentParameters())
    report = validate_clearances(model, envelopes)
    assert {"FC", "ESC", "camera"} <= report["equipment_minimum_gaps_mm"].keys()
    boxes = {item.name: item.shape.bounding_box() for item in envelopes}
    assert (boxes["ESC"].min.Z, boxes["ESC"].max.Z) == pytest.approx((12, 20))
    assert (boxes["FC"].min.Z, boxes["FC"].max.Z) == pytest.approx((23, 31))
    assert not EquipmentParameters().evidence.verified


@pytest.mark.parametrize("changes", [
    {"fc_width": 80, "fc_length": 80}, {"camera_width": 50, "camera_length": 40},
])
def test_oversized_equipment_fails_actual_solid_clearance(model, changes):
    envelopes = design_equipment_envelopes(model, EquipmentParameters(**changes))
    with pytest.raises(ValueError, match="clearance"):
        validate_clearances(model, envelopes)


def test_lowered_top_plate_collides_with_nominal_fc():
    params = get_preset()
    model = build_assembly(replace(params, vertical=replace(params.vertical, top_clearance=20)))
    envelopes = design_equipment_envelopes(model, EquipmentParameters())
    with pytest.raises(ValueError, match="FC.*clearance"):
        validate_clearances(model, envelopes)


def test_stack_hardware_and_board_keepouts_follow_shared_stack_pattern():
    params = get_preset()
    model = build_assembly(replace(params, stack=replace(params.stack, primary_pitch=28)))
    envelopes = design_equipment_envelopes(model, EquipmentParameters())
    group = next(g for g in model.layout.hole_groups if g.name == "central_stack_square")
    hardware = [item for item in envelopes if item.name.startswith("stack_hardware_")]
    assert len(hardware) == 4
    for item, center in zip(hardware, group.pattern.centers, strict=True):
        box = item.shape.bounding_box()
        assert (box.center().X, box.center().Y) == pytest.approx((center.x, center.y))
        for board in (item for item in envelopes if item.name in {"FC", "ESC"}):
            assert board.shape.distance_to(item.shape) == pytest.approx(0.5)


@pytest.mark.parametrize("value", [0, -1, float("inf"), float("nan"), True])
def test_invalid_equipment_dimensions_rejected(value):
    with pytest.raises(ValueError):
        EquipmentParameters(fc_width=value)


def test_stack_keepout_must_clear_hardware():
    with pytest.raises(ValueError, match="keepout"):
        EquipmentParameters(stack_keepout_diameter=5.1)


def test_board_must_contain_its_shared_mounting_keepouts(model):
    with pytest.raises(ValueError, match="contain.*stack"):
        design_equipment_envelopes(model, EquipmentParameters(fc_width=20))
