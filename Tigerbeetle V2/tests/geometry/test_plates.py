"""BREP checks against the observed three plate topologies and symmetry intent."""

from dataclasses import replace

import pytest
from build123d import Face, Plane

from fpv_frame.parameters.plates import PLATE_IDS
from fpv_frame.parameters.presets import get_preset
from fpv_frame.parts.plates import build_plate, plate_profile


@pytest.mark.parametrize("identity", PLATE_IDS)
def test_plate_is_one_closed_planar_profile_and_one_solid(identity):
    params = get_preset("reference")
    face = plate_profile(params, identity)
    part = build_plate(params, identity)
    assert face.is_valid
    assert face.area > 1000
    assert all(wire.is_closed for wire in face.wires())
    assert len(part.solids()) == 1
    assert part.is_valid
    assert part.volume == pytest.approx(face.area * 2, rel=1e-8)
    assert part.bounding_box().size.Z == pytest.approx(2)


@pytest.mark.parametrize("identity", PLATE_IDS)
def test_plate_profile_is_exactly_bilateral(identity):
    face = plate_profile(get_preset(), identity)
    # Missing broad-plate marks were explicitly restored by interface review.
    exterior = Face(face.outer_wire())
    mirrored = exterior.mirror(Plane.YZ)
    assert (exterior - mirrored).area < 1e-7
    assert (mirrored - exterior).area < 1e-7
    assert (face - face.mirror(Plane.YZ)).area < 1e-7


@pytest.mark.parametrize(
    "identity,length", [("scan1_body", 155), ("scan2_broad", 137), ("scan2_long", 214)]
)
def test_plate_envelope_matches_calibrated_reference(identity, length):
    box = plate_profile(get_preset(), identity).bounding_box()
    assert box.size.Y == pytest.approx(length, abs=3)
    assert 60 < box.size.X < 80


@pytest.mark.parametrize("identity", PLATE_IDS)
def test_plate_thickness_change_preserves_cut_profile(identity):
    params = get_preset()
    changed = replace(params, plates=tuple(replace(p, thickness=3) for p in params.plates))
    reference = build_plate(params, identity)
    thicker = build_plate(changed, identity)
    assert thicker.volume == pytest.approx(reference.volume * 1.5)


@pytest.mark.parametrize(
    "identity,count", [("scan1_body", 30), ("scan2_broad", 32), ("scan2_long", 30)]
)
def test_plate_opening_topology_matches_observed_features(identity, count):
    face = plate_profile(get_preset(), identity)
    assert len(face.inner_wires()) == count


@pytest.mark.parametrize(
    "field,value",
    [
        ("front_tip_y", 115),
        ("rear_tip_y", -100),
        ("front_tip_half_span", 22),
        ("rear_tip_half_span", 19.5),
        ("front_root_y", 30),
        ("rear_root_y", -31.5),
        ("front_root_half_span", 31),
        ("rear_root_half_span", 29.5),
        ("forward_stack_y", 67.5),
    ],
)
@pytest.mark.parametrize("identity", PLATE_IDS)
def test_plate_contours_follow_changed_interface_datums(identity, field, value):
    params = get_preset()
    changed = replace(params, layout=replace(params.layout, **{field: value}))
    original = plate_profile(params, identity)
    updated = plate_profile(changed, identity)
    assert updated.is_valid
    assert len(updated.inner_wires()) == len(original.inner_wires())
    assert len(build_plate(changed, identity).solids()) == 1


def test_forward_stack_access_bore_follows_stack_datum():
    from build123d import CenterOf

    from fpv_frame.geometry.layout import build_layout

    params = get_preset()
    changed = replace(params, layout=replace(params.layout, forward_stack_y=67.5))
    face = plate_profile(changed, "scan1_body")
    expected = build_layout(changed).body_point(0, changed.layout.forward_stack_y)
    access = max(face.inner_wires(), key=lambda wire: Face(wire).area)
    center = access.center(CenterOf.MASS)
    assert center.X == pytest.approx(expected.x)
    assert center.Y == pytest.approx(expected.y)


def test_forward_accessory_bores_keep_manufacturing_ligament():
    params = get_preset()
    face = plate_profile(params, "scan2_long")
    for wire in face.inner_wires():
        assert face.outer_wire().distance_to(wire) >= params.manufacturing.edge_minimum
