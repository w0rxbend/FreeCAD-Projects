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
