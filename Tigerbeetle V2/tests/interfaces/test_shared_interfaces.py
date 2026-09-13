from math import hypot, inf

import pytest

from fpv_frame.geometry.datums import PlanarTransform, Point2, Point3
from fpv_frame.geometry.interfaces import PlateInterface, TabSlotInterface
from fpv_frame.geometry.patterns import HolePattern


def test_motor_bolt_circle_diameter_is_not_square_side():
    pattern = HolePattern.bolt_circle(diameter=19, count=4, hole_diameter=3, angle_deg=45)
    first, second, third, _ = pattern.centers
    assert hypot(first.x - third.x, first.y - third.y) == pytest.approx(19)
    assert hypot(first.x - second.x, first.y - second.y) == pytest.approx(19 / 2**0.5)


def test_reflection_and_rotation_apply_to_one_canonical_pattern():
    pattern = HolePattern((Point2(2, 3), Point2(-1, 8)), 3)
    placement = PlanarTransform(origin=Point3(10, 20, 5), angle_deg=90, mirror_x=True)
    actual = pattern.placed(placement)
    assert (actual[0].x, actual[0].y, actual[0].z) == pytest.approx((7, 18, 5))
    assert (actual[1].x, actual[1].y, actual[1].z) == pytest.approx((2, 21, 5))
    assert pattern.centers[0] == Point2(2, 3)


def test_plate_mating_holes_share_axes_with_distinct_elevations():
    pattern = HolePattern.rectangle(20, 30.5, 3.2)
    interface = PlateInterface("stack", pattern, (0, 7, 30))
    lower, middle, upper = (interface.holes_at(index) for index in range(3))
    assert [(p.x, p.y) for p in lower] == [(p.x, p.y) for p in upper]
    assert [p.z for p in lower] == [0] * 4
    assert [p.z for p in middle] == [7] * 4
    assert [p.z for p in upper] == [30] * 4
    with pytest.raises(IndexError):
        interface.holes_at(-1)


def test_tab_slot_pair_uses_one_datum_and_total_clearance():
    interface = TabSlotInterface(
        "test_joint",
        Point2(12, -7),
        tab_width=8,
        tab_thickness=2,
        slot_clearance=0.2,
        angle_deg=30,
    )
    tab, slot = interface.tab(), interface.slot_cutout()
    assert tab.center == slot.center == Point2(12, -7)
    assert tab.angle_deg == slot.angle_deg == 30
    assert slot.width - tab.width == pytest.approx(0.2)
    assert slot.height - tab.height == pytest.approx(0.2)


@pytest.mark.parametrize("diameter", [0, -1, inf])
def test_bad_hole_diameter_fails_before_geometry(diameter):
    with pytest.raises(ValueError):
        HolePattern.rectangle(20, 20, diameter)


def test_duplicate_holes_and_nonfinite_datums_are_rejected():
    with pytest.raises(ValueError, match="unique"):
        HolePattern((Point2(0, 0), Point2(0, 0)), 3)
    with pytest.raises(ValueError):
        Point2(inf, 0)
