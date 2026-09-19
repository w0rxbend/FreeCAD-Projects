import pytest

from fpv_frame.blueprint.deviation import InkIndex, nearest_feature_errors


def test_nearest_ink_distance_is_euclidean_and_searches_distant_rows():
    index = InkIndex({0: (0, 20), 30: (10,)})
    assert index.distance((3, 4)) == pytest.approx(5)
    assert index.distance((10, 29)) == pytest.approx(1)
    assert index.distance((10, 15)) == pytest.approx(15)


def test_absent_source_strokes_are_rejected():
    with pytest.raises(ValueError, match="ink"):
        InkIndex({})


def test_displaced_holes_are_reported_in_real_units():
    errors = nearest_feature_errors({"bolt": (0, 0)}, ((3, 4),), pixels_per_mm=10)
    assert errors == {"bolt": 0.5}
    with pytest.raises(ValueError, match="holes"):
        nearest_feature_errors({"bolt": (0, 0)}, (), pixels_per_mm=10)
