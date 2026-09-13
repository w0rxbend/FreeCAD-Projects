"""Verify physical solids, including reflection, gaps and seven-inch propeller discs."""

from itertools import combinations
from math import dist

import pytest
from build123d import Circle, Plane, Pos

from tigerbee.layout import (
    WHEELBASE_MM,
    frame_arm_layout,
    plate_mounting_holes,
    top_support_holes,
    trim_arm_profile,
)
from tigerbee.models import build_part, build_reference_profile


@pytest.fixture(scope="module")
def arms():
    return {p.label: p.place(build_part(p.part_name)) for p in frame_arm_layout()}


def common_volume(a, b):
    common = a.intersect(b)
    return 0 if common is None else sum(s.volume for s in common.solids())


def test_arm_solids_are_mirrored_and_do_not_intersect(arms):
    for end in ("front", "rear"):
        left, right = arms[f"{end}-left-arm"], arms[f"{end}-right-arm"]
        reflection = right.mirror(Plane.YZ)
        assert abs(left.volume - common_volume(left, reflection)) < 1e-5
        assert left.is_valid and right.is_valid
        assert len(left.solids()) == len(right.solids()) == 1
        assert right.bounding_box().min.X == pytest.approx(0.3, abs=1e-5)
        assert left.bounding_box().max.X == pytest.approx(-0.3, abs=1e-5)
        assert left.distance_to(right) == pytest.approx(0.6, abs=1e-5)
    for a, b in combinations(arms.values(), 2):
        assert common_volume(a, b) < 1e-5
        assert a.distance_to(b) >= 0.6 - 1e-5


def test_motor_diagonals_equal_and_seven_inch_discs_clear():
    placements = {p.label: p for p in frame_arm_layout()}
    diagonals = [
        dist(
            placements[f"front-{side}-arm"].motor_center,
            placements[f"rear-{other}-arm"].motor_center,
        )
        for side, other in (("right", "left"), ("left", "right"))
    ]
    assert diagonals == pytest.approx([WHEELBASE_MM] * 2, abs=1e-8)
    centers = {name: placement.motor_center for name, placement in placements.items()}
    offset = 305 / (2 * 2**0.5)
    for end, y in (("front", offset), ("rear", -offset)):
        for side, x in (("right", offset), ("left", -offset)):
            assert centers[f"{end}-{side}-arm"] == pytest.approx((x, y), abs=1e-8)
    first = centers["front-left-arm"]
    second = centers["front-right-arm"]
    assert sum(a * b for a, b in zip(first, second, strict=True)) == pytest.approx(0, abs=1e-8)
    discs = [Pos(*p.motor_center) * Circle(7 * 25.4 / 2) for p in placements.values()]
    assert min(a.distance_to(b) for a, b in combinations(discs, 2)) > 3.0


@pytest.mark.parametrize("name", ["arm-type-1", "arm-type-2"])
def test_root_relief_preserves_holes_and_removes_only_small_tips(name):
    original = build_reference_profile(name)
    trimmed = trim_arm_profile(original, name)
    assert 0 < original.area - trimmed.area < original.area * 0.012
    assert sorted(w.length for w in trimmed.inner_wires()) == pytest.approx(
        sorted(w.length for w in original.inner_wires()), abs=1e-8
    )
    right = next(p for p in frame_arm_layout() if p.part_name == name and not p.mirror)
    for x, _ in right.root_holes():
        assert x - 1.5 - 0.3 > 20.0
    # Hole topology and placement agree across the entire reflected pair.
    left = next(p for p in frame_arm_layout() if p.part_name == name and p.mirror)
    assert left.root_holes() == pytest.approx([(-x, y) for x, y in right.root_holes()])


@pytest.mark.parametrize("gap", [-1, float("nan"), float("inf")])
def test_invalid_root_gap_rejected(gap):
    with pytest.raises(ValueError, match="finite and nonnegative"):
        trim_arm_profile(build_reference_profile("arm-type-1"), "arm-type-1", gap)


def test_shared_plate_axes_are_symmetric_and_cover_every_arm_and_support():
    rear = plate_mounting_holes("rear-plate")
    camera = plate_mounting_holes("camera-plate")
    top = plate_mounting_holes("top-plate")
    for placement in frame_arm_layout():
        for point in placement.root_holes():
            assert point in camera and point in rear
    assert top == top_support_holes()
    for x, y in top:
        assert (x, y) in rear or (x, y) in camera
        assert (-x, y) in top
    for points in (rear, camera, top):
        assert len(points) == len(set(points))
        assert all((-x, y) in points for x, y in points)
