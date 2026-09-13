from dataclasses import replace

import pytest
from build123d import Box, Face, Plane, Wire

from fpv_frame.assembly import build_assembly
from fpv_frame.parameters.presets import get_preset
from fpv_frame.validation.clearances import ClearanceEnvelope, validate_clearances
from fpv_frame.validation.manufacturing import validate_manufacturing


def test_manufacturing_rejects_a_thin_edge_ligament():
    model = build_assembly(get_preset())
    face = Face(Wire.make_rect(20, 20), [Wire.make_circle(2, Plane(origin=(7, 0, 0)))])
    model = replace(model, profiles={"test_coupon": face})
    with pytest.raises(ValueError, match="ligament"):
        validate_manufacturing(model)


def test_equipment_clearance_detects_material_collision():
    model = build_assembly(get_preset())
    envelope = ClearanceEnvelope("FC", Box(20, 20, 100), 0.2)
    with pytest.raises(ValueError, match="FC.*clearance"):
        validate_clearances(model, (envelope,))


def test_equipment_clearance_reports_missing_equipment_dimensions():
    model = build_assembly(get_preset())
    report = validate_clearances(model)
    assert set(report["unverified_equipment"]) == {"FC", "ESC", "camera"}
    assert "side_panels" in report["not_applicable"]
    assert report["top_face_clearance_mm"] == pytest.approx(25)


def test_bore_gate_rejects_an_internal_plug_even_with_both_open_rims():
    from build123d import Solid

    from fpv_frame.validation.interfaces import _check_bore

    ring = Face(Wire.make_circle(6), [Wire.make_circle(2)])
    from build123d import extrude

    part = extrude(ring, amount=5)
    plug = Solid.make_cylinder(2.2, 0.5, Plane(origin=(0, 0, 2)))
    blocked = part.fuse(plug)
    with pytest.raises(ValueError, match="bore.*blocked"):
        _check_bore(blocked, 0, 0, 0, 5, 4, "coupon")


def test_equipment_envelopes_must_clear_each_other():
    model = build_assembly(get_preset())
    first = ClearanceEnvelope("FC", Box(10, 10, 10).translate((0, 0, 100)), 0.2)
    second = ClearanceEnvelope("ESC", Box(10, 10, 10).translate((0, 0, 105)), 0.2)
    with pytest.raises(ValueError, match="clearance"):
        validate_clearances(model, (first, second))


def test_configured_arm_clearance_is_enforced_on_actual_solids():
    params = get_preset()
    model = build_assembly(replace(params, manufacturing=replace(
        params.manufacturing, general_clearance=2.0)))
    with pytest.raises(ValueError, match='arm.*clearance'):
        validate_clearances(model)


def test_purchased_standoff_uses_hardware_wall_requirement():
    model = build_assembly(get_preset())
    name = model.layout.standoffs[0].name
    profile = model.profiles[name]
    report = validate_manufacturing(replace(model, profiles={name: profile}))
    assert report['minimum_ligament_mm'][name] == pytest.approx(1.0)
