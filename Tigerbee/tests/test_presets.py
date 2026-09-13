import pytest

from tigerbee.models import PartParameters, build_part
from tigerbee.presets import part_parameters


def test_original_preserves_native_thickness():
    parameters = part_parameters("camera-plate", "original")
    assert build_part("camera-plate", parameters).bounding_box().size.Z == pytest.approx(3)


def test_product_preset_uses_photographed_plate_thickness():
    parameters = part_parameters("camera-plate", "product-7inch")
    assert parameters.thickness == 2.5
    assert part_parameters("arm-type-1", "product-7inch").thickness == 5


def test_explicit_dimension_overrides_preset():
    assert part_parameters("camera-plate", "product-7inch", thickness=4).thickness == 4


def test_center_hole_override_cannot_silently_do_nothing():
    with pytest.raises(ValueError, match="no center hole"):
        build_part("top-plate", PartParameters(center_hole_diameter=8))
