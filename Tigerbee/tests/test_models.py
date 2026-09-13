"""Compare reconstructed geometry with independent saved FreeCAD STEP solids."""

from pathlib import Path

import pytest
from build123d import import_step

from tigerbee.models import PARTS, PartParameters, build_part

BASELINE = Path(__file__).resolve().parents[1] / "refs/baseline"


@pytest.mark.parametrize("name", ["arm-type-1", "arm-type-2", "camera-plate"])
def test_original_matches_freecad_solid(name):
    actual = build_part(name)
    reference = import_step(BASELINE / f"{name}.step")
    assert actual.is_valid
    assert len(actual.solids()) == 1
    assert actual.volume == pytest.approx(reference.volume, abs=1e-4)
    assert (actual - reference).volume < 1e-4
    assert (reference - actual).volume < 1e-4
    assert actual.bounding_box().min.Z == pytest.approx(0, abs=1e-7)


@pytest.mark.parametrize("name", ["arm-type-1", "arm-type-2", "camera-plate"])
def test_thickness_changes_without_altering_profile(name):
    original = build_part(name)
    changed = build_part(name, PartParameters(thickness=2.5))
    assert changed.is_valid
    assert changed.bounding_box().size.Z == pytest.approx(2.5)
    assert changed.volume / 2.5 == pytest.approx(
        original.volume / original.bounding_box().size.Z, abs=1e-5
    )


@pytest.mark.parametrize("thickness", [0, -1, float("nan"), float("inf")])
def test_invalid_thickness_fails(thickness):
    with pytest.raises(ValueError, match="thickness"):
        build_part("arm-type-1", PartParameters(thickness=thickness))


def test_unknown_part_fails():
    with pytest.raises(ValueError, match="Unknown part"):
        build_part("missing")


def test_part_catalog_includes_original_components():
    assert {"arm-type-1", "arm-type-2", "camera-plate"} <= set(PARTS)


@pytest.mark.parametrize("name,openings", [("rear-plate", 31), ("top-plate", 30)])
def test_scan_plate_has_valid_outline_and_all_openings(name, openings):
    from tigerbee.models import build_profile

    profile = build_profile(name)
    assert len(profile.inner_wires()) == openings
    part = build_part(name)
    assert part.is_valid
    assert len(part.solids()) == 1
    assert part.bounding_box().size.Z == pytest.approx(2.5)


@pytest.mark.parametrize("name", ["arm-type-1", "arm-type-2"])
def test_arm_extension_preserves_motor_and_root_holes(name):
    from tigerbee.models import profile_data

    original = build_part(name)
    longer = build_part(name, PartParameters(length_extension=20))
    assert longer.is_valid
    assert len(longer.solids()) == 1
    assert longer.bounding_box().size.Y == pytest.approx(original.bounding_box().size.Y + 20)
    assert longer.bounding_box().max.Y == pytest.approx(original.bounding_box().max.Y)
    assert not longer.is_inside((0, 0, 2.5))
    assert longer.is_inside((5, 0, 2.5))
    for loop in profile_data(name)["loops"]:
        for segment in loop["segments"]:
            if segment["kind"] == "circle" and segment["radius"] == 1.5:
                x, y = segment["center"]
                assert not longer.is_inside((x, y - 20, 2.5))
                assert longer.is_inside((x + 1.6, y - 20, 2.5))


def test_plate_rejects_arm_only_parameter():
    with pytest.raises(ValueError, match="only supported for arms"):
        build_part("camera-plate", PartParameters(length_extension=10))
