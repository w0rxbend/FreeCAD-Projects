from copy import deepcopy
from dataclasses import replace

import pytest
from build123d import Compound, Face, Vector, extrude

from fpv_frame.assembly import build_assembly, validate_assembly
from fpv_frame.parameters.presets import PRESET_NAMES, get_preset


@pytest.fixture(scope="module")
def reference():
    return build_assembly(get_preset("reference"))


def test_named_components_and_photo_stack(reference):
    assert len(reference.parts) == 15
    assert len(reference.compound.solids()) == 15
    assert set(reference.profiles) == set(reference.parts)
    for name, profile in reference.profiles.items():
        assert profile.center().Z == pytest.approx(0, abs=1e-10)
        assert abs(profile.normal_at().Z) == pytest.approx(1)
        thickness = reference.parts[name].bounding_box().size.Z
        assert profile.area * thickness == pytest.approx(reference.parts[name].volume)
    expected_z = {"scan2_broad": (0, 2), "scan1_body": (7, 9), "scan2_long": (34, 36)}
    for name, (lower, upper) in expected_z.items():
        bounds = reference.parts[name].bounding_box()
        assert bounds.min.Z == pytest.approx(lower)
        assert bounds.max.Z == pytest.approx(upper)
    assert sum(name.startswith("arm_") for name in reference.parts) == 4
    assert sum(name.startswith("standoff_") for name in reference.parts) == 8
    assert all(part.label == name for name, part in reference.parts.items())
    for datum in reference.layout.standoffs:
        part = reference.parts[datum.name]
        bounds = part.bounding_box()
        assert bounds.min.Z == pytest.approx(datum.lower_z)
        assert bounds.max.Z == pytest.approx(datum.upper_z)
        assert not part.is_inside(
            (datum.center.x, datum.center.y, (datum.lower_z + datum.upper_z) / 2)
        )


def test_reference_validates_real_interfaces_and_symmetric_material(reference):
    report = validate_assembly(reference)
    assert report["valid"] is True
    assert report["interference"]["maximum_overlap_mm3"] <= 1e-6
    assert report["interfaces"]["checked_bores"] >= 50
    assert report["symmetry"]["maximum_difference_mm3"] <= 1e-5
    assert report["clearances"]["unverified_equipment"] == []
    assert {"FC", "ESC", "camera"} <= set(report["clearances"]["equipment_minimum_gaps_mm"])


@pytest.mark.parametrize("preset", PRESET_NAMES)
def test_all_presets_validate(preset):
    model = build_assembly(get_preset(preset))
    assert validate_assembly(model)["valid"]


def test_material_intersection_is_rejected(reference):
    parts = deepcopy(reference.parts)
    parts["scan2_long"] = parts["scan2_long"].translate(Vector(0, 0, -27))
    broken = replace(reference, parts=parts, compound=Compound(children=list(parts.values())))
    with pytest.raises(ValueError, match="overlap|interference"):
        validate_assembly(broken)


def test_shifted_plate_bores_are_rejected(reference):
    parts = deepcopy(reference.parts)
    parts["scan2_long"] = parts["scan2_long"].translate(Vector(0.25, 0, 0))
    broken = replace(reference, parts=parts, compound=Compound(children=list(parts.values())))
    with pytest.raises(ValueError, match="bore|interface"):
        validate_assembly(broken)


def test_missing_manufacturing_profile_is_rejected(reference):
    profiles = dict(reference.profiles)
    profiles.pop("scan2_long")
    with pytest.raises(ValueError, match="inventory"):
        validate_assembly(replace(reference, profiles=profiles))


def test_missing_cosmetic_opening_is_rejected(reference):
    profiles = dict(reference.profiles)
    face = profiles["scan2_long"]
    profiles["scan2_long"] = Face(face.outer_wire(), face.inner_wires()[1:])
    with pytest.raises(ValueError, match="hole count"):
        validate_assembly(replace(reference, profiles=profiles))


def test_solid_must_match_its_manufacturing_profile(reference):
    parts = deepcopy(reference.parts)
    face = reference.profiles["scan2_long"]
    wires = list(face.inner_wires())
    index = next(i for i, w in enumerate(wires)
                 if len(w.edges()) > 1 and abs(Face(w).center().X) < 1e-6)
    wires.pop(index)
    filled = Face(face.outer_wire(), wires)
    parts["scan2_long"] = extrude(filled, amount=2).translate((0, 0, 34))
    broken = replace(reference, parts=parts, compound=Compound(children=list(parts.values())))
    with pytest.raises(ValueError, match="extrusion"):
        validate_assembly(broken)


def test_parameter_changes_recompute_the_whole_stack_and_motor_span(reference):
    params = reference.params
    changed = replace(
        params,
        arm=replace(
            params.arm,
            thickness=6,
            profile=replace(
                params.arm.profile, root_to_motor=params.arm.profile.root_to_motor + 10
            ),
        ),
        vertical=replace(params.vertical, top_clearance=30),
    )
    model = build_assembly(changed)
    assert model.parts["scan1_body"].bounding_box().min.Z == pytest.approx(8)
    assert model.parts["scan2_long"].bounding_box().min.Z == pytest.approx(40)
    assert model.layout.wheelbase > reference.layout.wheelbase
    assert validate_assembly(model)["valid"]
