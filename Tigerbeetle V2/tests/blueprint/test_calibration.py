"""Calibration must preserve physical dimensions and expose contradictory anchors."""

import math

import pytest

from fpv_frame.blueprint.calibration import Anchor, Calibration, calibrate, calibrate_page


def test_consistent_independent_anchors_recover_scale() -> None:
    result = calibrate(
        (Anchor("stack20", (0, 0), (200, 0), 20), Anchor("stack30", (0, 0), (0, 305), 30.5))
    )
    assert result.pixels_per_mm == pytest.approx(10)
    assert result.maximum_relative_residual == pytest.approx(0)


def test_inconsistent_anchors_are_rejected_instead_of_averaged() -> None:
    with pytest.raises(ValueError, match="disagree"):
        calibrate((Anchor("stack", (0, 0), (200, 0), 20), Anchor("motor", (0, 0), (160, 0), 19)))


def test_one_anchor_cannot_masquerade_as_independent_calibration() -> None:
    with pytest.raises(ValueError, match="two"):
        calibrate((Anchor("stack", (0, 0), (200, 0), 20),))


def test_pixel_coordinates_map_to_right_handed_part_datums() -> None:
    transform = Calibration(10, origin_px=(100, 200), rotation_degrees=0)
    assert transform.to_mm((120, 170)) == pytest.approx((2, 3))
    assert transform.to_pixels((2, 3)) == pytest.approx((120, 170))


def test_rotated_part_mapping_round_trips() -> None:
    transform = Calibration(11.8, origin_px=(1870, 1595), rotation_degrees=180)
    for point in ((0, 0), (20, 30.5), (-19, 7)):
        assert transform.to_mm(transform.to_pixels(point)) == pytest.approx(point)


@pytest.mark.parametrize("invalid", [0, -1, math.inf, math.nan])
def test_invalid_scale_rejected(invalid: float) -> None:
    with pytest.raises(ValueError):
        Calibration(invalid)


def test_zero_length_anchor_rejected() -> None:
    with pytest.raises(ValueError):
        Anchor("coincident", (1, 2), (1, 2), 20)


def test_duplicate_anchor_not_independent() -> None:
    anchor = Anchor("stack", (0, 0), (200, 0), 20)
    with pytest.raises(ValueError, match="distinct"):
        calibrate((anchor, anchor))


def test_user_confirmed_a4_page_agrees_with_independent_stack_pitch() -> None:
    result = calibrate_page((2480, 3508), (210, 297))
    assert result.pixels_per_mm == pytest.approx(11.810486, abs=1e-6)
    assert result.maximum_relative_residual < 0.0001
    assert 360 / result.pixels_per_mm == pytest.approx(30.5, abs=0.03)


def test_cropped_or_distorted_page_does_not_silently_set_scale() -> None:
    with pytest.raises(ValueError, match="disagree"):
        calibrate_page((2000, 3508), (210, 297))
