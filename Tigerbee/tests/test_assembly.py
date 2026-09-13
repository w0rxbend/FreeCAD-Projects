import math

import pytest

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
    assert max(report["diagonal_wheelbases_mm"]) < 330
    assert report["advertised_wheelbase_mm"] == 330
    assert report["wheelbase_errors_mm"] == pytest.approx(
        [value - 330 for value in report["diagonal_wheelbases_mm"]]
    )
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


def test_final_fit_gate_rejects_hole_error_even_without_collision():
    report = {
        "interference_volume_mm3": 0,
        "mounting_errors_mm": {"arm": 0.2},
        "diagonal_wheelbases_mm": [330, 330],
        "advertised_wheelbase_mm": 330,
        "status": "verified",
    }
    with pytest.raises(ValueError, match="misalignment"):
        require_final_fit(report)


def test_final_fit_gate_uses_confirmed_330_mm_wheelbase():
    report = {
        "interference_volume_mm3": 0,
        "mounting_errors_mm": {"arm": 0},
        "diagonal_wheelbases_mm": [330, 330],
        "advertised_wheelbase_mm": 330,
        "status": "verified",
    }
    require_final_fit(report)
    report["diagonal_wheelbases_mm"] = [303, 304]
    with pytest.raises(ValueError, match="330 mm"):
        require_final_fit(report)


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
