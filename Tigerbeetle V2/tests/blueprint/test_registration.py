"""Shared scan features must resolve to one datum within explicit residual bounds."""

import pytest

from fpv_frame.blueprint.calibration import Calibration
from fpv_frame.blueprint.registration import Correspondence, register


def test_independent_features_recover_scan_transform() -> None:
    expected = Calibration(11.8, (1500, 1200), 17)
    targets = ((-15.25, 15.25), (15.25, 15.25), (-15.25, -15.25), (15.25, -15.25))
    fit = register(tuple(Correspondence(str(i), expected.to_pixels(p), p)
                         for i, p in enumerate(targets)), maximum_error_mm=0.01)
    assert fit.calibration.pixels_per_mm == pytest.approx(11.8)
    assert fit.calibration.origin_px == pytest.approx((1500, 1200))
    assert fit.calibration.rotation_degrees == pytest.approx(17)
    assert fit.maximum_error_mm < 1e-10


def test_wrong_shared_hole_is_rejected() -> None:
    pairs = (Correspondence("a", (0, 0), (0, 0)),
             Correspondence("b", (100, 0), (10, 0)),
             Correspondence("c", (0, 100), (0, -10)),
             Correspondence("wrong", (100, 100), (15, -10)))
    with pytest.raises(ValueError, match="residual"):
        register(pairs, maximum_error_mm=0.5)


def test_reflection_cannot_be_hidden_as_rotation() -> None:
    pairs = (Correspondence("a", (0, 0), (0, 0)),
             Correspondence("b", (100, 0), (-10, 0)),
             Correspondence("c", (0, 100), (0, -10)))
    with pytest.raises(ValueError):
        register(pairs, maximum_error_mm=0.1)


def test_repeated_or_insufficient_points_do_not_prove_registration() -> None:
    pair = Correspondence("a", (0, 0), (0, 0))
    for pairs in ((pair,), (pair, pair, pair)):
        with pytest.raises(ValueError):
            register(pairs, maximum_error_mm=1)


def test_collinear_features_cannot_establish_plane_registration() -> None:
    pairs = tuple(Correspondence(str(i), (i * 10, 0), (i, 0)) for i in range(3))
    with pytest.raises(ValueError, match="collinear"):
        register(pairs, maximum_error_mm=1)
