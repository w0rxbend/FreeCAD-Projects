"""Accessories must fit the existing carbon, not just their own design dimensions."""

import pytest
from build123d import Axis, Face, Plane, extrude

from tigerbee.models import build_part, build_profile
from tigerbee.protectors import ProtectorParameters, build_protector


@pytest.mark.parametrize("arm", ["arm-type-1", "arm-type-2"])
def test_protector_fits_carbon_and_preserves_all_motor_openings(arm):
    protector = build_protector(arm)
    carbon = build_part(arm)
    assert protector.is_valid and len(protector.solids()) == 1
    assert (protector & carbon).volume < 1e-6
    assert protector.bounding_box().min.Z == pytest.approx(-12)
    assert protector.bounding_box().max.Z == pytest.approx(4.8)
    openings = [w for w in build_profile(arm).inner_wires() if w.center().Y > -30]
    assert len(openings) == 6
    for wire in openings:
        tool = extrude(Face(wire), amount=30, dir=(0, 0, 1)).translate((0, 0, -15))
        assert (protector & tool).volume < 1e-6
    # Broad planar ground support, not a rounded unstable point.
    ground = protector.faces().filter_by(Plane.XY).sort_by(Axis.Z)[0]
    assert ground.center().Z == pytest.approx(-12)
    assert ground.area > 200


@pytest.mark.parametrize("arm", ["arm-type-1", "arm-type-2"])
def test_left_protector_is_exact_reflection(arm):
    right = build_protector(arm)
    left = build_protector(arm, mirror=True)
    assert (left - right.mirror(Plane.YZ)).volume < 1e-6


def test_custom_height_changes_stance_without_moving_carbon_seat():
    part = build_protector("arm-type-1", ProtectorParameters(drop=15))
    assert part.bounding_box().min.Z == pytest.approx(-15)
    assert part.bounding_box().max.Z == pytest.approx(4.8)
    assert (part & build_part("arm-type-1")).volume < 1e-6


@pytest.mark.parametrize("kwargs", [{"drop": 1}, {"clearance": -0.1}, {"drop": float("nan")}])
def test_invalid_dimensions_are_rejected(kwargs):
    with pytest.raises(ValueError):
        build_protector("arm-type-1", ProtectorParameters(**kwargs))


def test_separate_print_export_round_trip_and_bolt_access(tmp_path):
    from build123d import import_step, offset

    from tigerbee.protector_export import export_protector

    report = export_protector("arm-type-2", False, tmp_path)
    part = import_step(tmp_path / "arm-type-2-protector-right.step")
    assert part.is_valid and len(part.solids()) == 1
    assert part.bounding_box().min.Z == pytest.approx(0, abs=1e-6)
    assert report["mesh_validation"]["valid"]
    assert report["fit"]["carbon_intersection_mm3"] < 1e-6
    assert report["fit"]["contact_area_mm2"] > 200
    for wire in build_profile("arm-type-2").inner_wires():
        if abs(wire.center().X) > 4 and abs(wire.center().Y) < 10:
            head = offset(Face(wire), amount=1.7).faces()[0]
            tool = extrude(head, amount=9.9, dir=(0, 0, 1))
            assert (part & tool).volume < 1e-6


@pytest.mark.parametrize("defect", ["carbon", "blocked-hole", "height"])
def test_fit_audit_rejects_broken_accessories(defect):
    from build123d import Box, Pos

    from tigerbee.protector_export import audit_protector

    part = build_protector("arm-type-1")
    if defect == "carbon":
        part += Pos(0, -12, 0) * Box(5, 4, 4)
    elif defect == "blocked-hole":
        part += Pos(0, 0, -1) * Box(9, 9, 2)
    else:
        part = part.translate((0, 0, 1))
    with pytest.raises(ValueError, match="Protector fit failed"):
        audit_protector(part, build_part("arm-type-1"), 12, 2)
