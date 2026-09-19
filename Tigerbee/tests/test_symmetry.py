"""Check exact reflection, preserved cutouts, and stable spline mass properties."""

import pytest
from build123d import Face, Plane, Wire, extrude

from tigerbee.models import PartParameters, build_reference_profile
from tigerbee.symmetry import stabilize_profile, symmetrize_profile


def test_camera_preserves_intentional_openings_and_is_exactly_symmetric():
    source = build_reference_profile("camera-plate", PartParameters(mounting_hole_diameter=3.0))
    result = symmetrize_profile(source)
    assert result.is_valid
    assert len(result.inner_wires()) == len(source.inner_wires()) == 31
    assert (result - result.mirror(Plane.YZ)).area < 1e-7
    assert (result.mirror(Plane.YZ) - result).area < 1e-7
    assert result.area == pytest.approx(5685.1459779268, abs=1e-7)
    assert source.area == pytest.approx(5688.1779146673, abs=1e-7)


@pytest.mark.parametrize("name", ["rear-plate", "top-plate"])
def test_exact_spline_span_subdivision_restores_area_volume_consistency(name):
    source = build_reference_profile(name, PartParameters(mounting_hole_diameter=3.0))
    result = stabilize_profile(source)
    assert result.is_valid
    assert len(result.inner_wires()) == len(source.inner_wires())
    part = extrude(result, amount=2.5, dir=(0, 0, 1))
    assert part.is_valid
    assert part.volume == pytest.approx(result.area * 2.5, abs=1e-6)
    assert (source - result).area < 1e-6
    assert (result - source).area < 1e-6


def test_shifted_axis_and_right_half_are_supported():
    source = Face(Wire.make_polygon([(1, -2), (6, -2), (5, 2), (1, 2)], close=True))
    result = symmetrize_profile(source, axis_x=3, side="right")
    plane = Plane(origin=(3, 0, 0), x_dir=(0, 1, 0), z_dir=(1, 0, 0))
    assert (result - result.mirror(plane)).area < 1e-7
    assert result.bounding_box().min.X == pytest.approx(0)
    assert result.bounding_box().max.X == pytest.approx(6)


def test_disconnected_mirrored_half_is_rejected():
    source = Face(
        Wire.make_polygon(
            [(-4, -4), (4, -4), (4, 4), (-4, 4), (-4, 2), (2, 2), (2, -2), (-4, -2)],
            close=True,
        )
    )
    with pytest.raises(ValueError, match="connected"):
        symmetrize_profile(source)


@pytest.mark.parametrize("axis", [float("nan"), float("inf"), 100])
def test_invalid_axis_is_rejected(axis):
    with pytest.raises(ValueError, match="axis"):
        symmetrize_profile(
            build_reference_profile("camera-plate", PartParameters(mounting_hole_diameter=3.0)),
            axis_x=axis,
        )
