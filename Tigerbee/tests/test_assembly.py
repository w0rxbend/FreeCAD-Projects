import math

import pytest
from build123d import GeomType

from tigerbee.assembly import AssemblyParameters, build_assembly, fit_mounts, require_final_fit


def test_mount_fit_recovers_rigid_transform():
    fit = fit_mounts([(0, 0), (10, 0)], [(5, 7), (5, 17)])
    assert fit.angle == pytest.approx(90)
    assert fit.translation == pytest.approx((5, 7))
    assert fit.max_error == pytest.approx(0)


def test_mount_fit_reports_incompatible_pitch():
    fit = fit_mounts([(0, 0), (10, 0)], [(0, 0), (12, 0)])
    assert fit.max_error == pytest.approx(1)


def test_frame_contains_four_arms_three_plates_and_eight_standoffs():
    assembly, report = build_assembly()
    labels = [child.label for child in assembly.children]
    assert len(labels) == 15
    assert len(set(labels)) == 15
    assert sum("arm" in name for name in labels) == 4
    assert sum("plate" in name for name in labels) == 3
    assert sum("standoff" in name for name in labels) == 8
    assert all(child.is_valid and len(child.solids()) == 1 for child in assembly.children)
    assert report["status"] == "provisional-assembly"
    assert len(report["motor_centers_mm"]) == 4
    assert all(math.isfinite(value) for value in report["diagonal_wheelbases_mm"])
    assert report["diagonal_wheelbases_mm"] == pytest.approx([302.592190141, 303.985621985])
    assert report["measured_wheelbase_range_mm"] == [303, 304]
    assert report["wheelbase_matches_measurement"]
    assert report["mounting_errors_mm"]
    # Preserving the supplied geometry exposes root collisions; the final-fit
    # gate must reject them rather than treating valid individual solids as fit.
    assert report["interference_volume_mm3"] > 0
    assert {tuple(item["parts"]) for item in report["interferences"]} == {
        ("front-right-arm", "front-left-arm"),
        ("rear-left-arm", "rear-right-arm"),
    }
    with pytest.raises(ValueError, match="interference"):
        require_final_fit(report)


def test_actual_solid_motor_holes_match_the_physical_wheelbase_reading():
    from tigerbee.references import wheelbase_matches_measurement

    assembly, report = build_assembly()
    centers = {}
    for part in assembly.children:
        if "arm" not in part.label:
            continue
        radius = 3.5 if part.label in ("front-right-arm", "rear-left-arm") else 3.62
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
    assert wheelbase_matches_measurement(diagonals)
    assert diagonals == pytest.approx(report["diagonal_wheelbases_mm"], abs=1e-7)


def test_default_assembly_preserves_authoritative_freecad_solids_and_thickness():
    from tigerbee.models import build_part

    assembly, report = build_assembly()
    parts = {part.label: part for part in assembly.children}
    for label, name in (
        ("camera-plate", "camera-plate"),
        ("front-right-arm", "arm-type-1"),
        ("front-left-arm", "arm-type-2"),
        ("rear-left-arm", "arm-type-1"),
        ("rear-right-arm", "arm-type-2"),
    ):
        source = build_part(name)
        assert parts[label].volume == pytest.approx(source.volume, abs=1e-6)
        assert parts[label].bounding_box().size.Z == pytest.approx(source.bounding_box().size.Z)
    assert report["parameters"]["camera_plate_thickness"] == 3
    assert report["standoff_lengths_mm"] == pytest.approx([24.5] * 6 + [32.5] * 2)


def test_final_fit_gate_rejects_hole_error_even_without_collision():
    report = {
        "interference_volume_mm3": 0,
        "mounting_errors_mm": {"arm": 0.2},
        "diagonal_wheelbases_mm": [303, 304],
        "status": "verified",
    }
    with pytest.raises(ValueError, match="misalignment"):
        require_final_fit(report)


def test_final_fit_gate_uses_physical_measurement_instead_of_product_photo():
    report = {
        "interference_volume_mm3": 0,
        "mounting_errors_mm": {"arm": 0},
        "diagonal_wheelbases_mm": [302.592190141, 303.985621985],
        "status": "verified",
    }
    require_final_fit(report)
    report["diagonal_wheelbases_mm"] = [330, 330]
    with pytest.raises(ValueError, match="physical measurement"):
        require_final_fit(report)


@pytest.mark.parametrize("diagonals", [[295, 295], [330, 330], [float("nan"), 304], [303]])
def test_wheelbase_check_rejects_wrong_or_incomplete_measurements(diagonals):
    from tigerbee.references import wheelbase_matches_measurement

    assert not wheelbase_matches_measurement(diagonals)


def test_top_height_changes_standoff_lengths():
    _, low = build_assembly(AssemblyParameters(top_z=35))
    _, high = build_assembly(AssemblyParameters(top_z=40))
    assert high["standoff_lengths_mm"] == pytest.approx(
        [length + 5 for length in low["standoff_lengths_mm"]]
    )


@pytest.mark.parametrize("height", [0, 8, float("nan"), float("inf")])
def test_invalid_stack_height_rejected(height):
    with pytest.raises(ValueError, match="top_z"):
        build_assembly(AssemblyParameters(top_z=height))
