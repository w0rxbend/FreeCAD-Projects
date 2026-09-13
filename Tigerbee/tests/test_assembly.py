import copy
import math

import pytest
from build123d import GeomType, Plane

from tigerbee.assembly import AssemblyParameters, build_assembly, fit_mounts, require_final_fit
from tigerbee.layout import WHEELBASE_MM, frame_arm_layout


@pytest.fixture(scope="module")
def frame():
    return build_assembly()


def test_mount_fit_recovers_rigid_transform():
    fit = fit_mounts([(0, 0), (10, 0)], [(5, 7), (5, 17)])
    assert fit.angle == pytest.approx(90)
    assert fit.translation == pytest.approx((5, 7))
    assert fit.max_error == pytest.approx(0)


def test_mount_fit_reports_incompatible_pitch():
    fit = fit_mounts([(0, 0), (10, 0)], [(0, 0), (12, 0)])
    assert fit.max_error == pytest.approx(1)


def test_frame_has_valid_components_exact_interfaces_and_equal_diagonals(frame):
    assembly, report = frame
    labels = [child.label for child in assembly.children]
    assert len(labels) == len(set(labels)) == 15
    assert sum("arm" in name for name in labels) == 4
    assert sum("plate" in name for name in labels) == 3
    assert sum("standoff" in name for name in labels) == 8
    assert all(child.is_valid and len(child.solids()) == 1 for child in assembly.children)
    assert report["status"] == "cad-fit-verified"
    assert report["physical_validation_status"] == "unconfirmed-stack-hardware-and-material"
    assert report["diagonal_wheelbases_mm"] == pytest.approx([WHEELBASE_MM] * 2, abs=1e-8)
    assert report["measured_wheelbase_range_mm"] == [303, 304]
    assert report["wheelbase_matches_measurement"]
    assert max(report["mounting_errors_mm"].values()) < 1e-8
    assert report["interference_volume_mm3"] == 0
    assert report["interferences"] == []
    assert report["geometry_audit"]["passed"]
    assert report["geometry_audit"]["minimum_edge_ligament_mm"] >= 1.0
    assert all(item["coaxial"] for item in report["geometry_audit"]["joint_checks"])
    assert min(item["tip_gap_mm"] for item in report["geometry_audit"]["propeller_clearances"]) > 3
    require_final_fit(report)


def test_actual_solid_motor_holes_match_report(frame):
    assembly, report = frame
    centers = {}
    for part in assembly.children:
        if "arm" not in part.label:
            continue
        radius = 3.5 if part.label.startswith("front") else 3.62
        holes = [
            edge
            for edge in part.edges().filter_by(GeomType.CIRCLE)
            if abs(edge.radius - radius) < 1e-7 and abs(edge.length - 2 * math.pi * radius) < 1e-6
        ]
        assert len(holes) == 2
        centers[part.label] = tuple(holes[0].arc_center)[:2]
    diagonals = [
        math.dist(centers[a], centers[b])
        for a, b in (("front-right-arm", "rear-left-arm"), ("front-left-arm", "rear-right-arm"))
    ]
    assert diagonals == pytest.approx([303.5, 303.5], abs=1e-7)
    assert diagonals == pytest.approx(report["diagonal_wheelbases_mm"], abs=1e-7)


def test_actual_assembly_matches_exported_parts_and_reflects_exactly(frame):
    from tigerbee.models import build_part

    assembly, report = frame
    parts = {part.label: part for part in assembly.children}
    for placement in frame_arm_layout():
        source = build_part(placement.part_name)
        assert parts[placement.label].volume == pytest.approx(source.volume, abs=1e-6)
        assert parts[placement.label].bounding_box().size.Z == pytest.approx(5)
    for end in ("front", "rear"):
        right = parts[f"{end}-right-arm"]
        left = parts[f"{end}-left-arm"]
        common = left.intersect(right.mirror(Plane.YZ))
        assert sum(s.volume for s in common.solids()) == pytest.approx(left.volume, abs=1e-6)
    assert report["parameters"]["camera_plate_thickness"] == 3
    assert report["standoff_lengths_mm"] == pytest.approx([24.5] * 6 + [32.5] * 2)


def test_final_fit_gate_rejects_hole_error_even_without_collision(frame):
    report = copy.deepcopy(frame[1])
    report["mounting_errors_mm"]["arm"] = 0.2
    with pytest.raises(ValueError, match="misalignment"):
        require_final_fit(report)


def test_final_fit_gate_requires_real_geometry_audit(frame):
    report = copy.deepcopy(frame[1])
    report.pop("geometry_audit")
    with pytest.raises(ValueError, match="Frame geometry failed"):
        require_final_fit(report)


def test_final_fit_gate_uses_physical_measurement_instead_of_product_photo(frame):
    report = copy.deepcopy(frame[1])
    report["diagonal_wheelbases_mm"] = [330, 330]
    with pytest.raises(ValueError, match="physical measurement"):
        require_final_fit(report)


@pytest.mark.parametrize("diagonals", [[295, 295], [330, 330], [float("nan"), 304], [303]])
def test_wheelbase_check_rejects_wrong_or_incomplete_measurements(diagonals):
    from tigerbee.references import wheelbase_matches_measurement

    assert not wheelbase_matches_measurement(diagonals)


def test_top_height_changes_standoff_lengths(frame):
    _, low = frame
    _, high = build_assembly(AssemblyParameters(top_z=40))
    assert high["standoff_lengths_mm"] == pytest.approx(
        [length + 5 for length in low["standoff_lengths_mm"]]
    )
    require_final_fit(high)


@pytest.mark.parametrize("height", [0, 8, float("nan"), float("inf")])
def test_invalid_stack_height_rejected(height):
    with pytest.raises(ValueError, match="top_z"):
        build_assembly(AssemblyParameters(top_z=height))
