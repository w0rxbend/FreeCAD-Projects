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
    assert original.area > trimmed.area
    assert sum(face.area for face in trimmed.cut(original).faces()) < 1e-6
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


@pytest.mark.parametrize("name", ["arm-type-1", "arm-type-2"])
def test_entire_clamped_root_stays_inside_both_plate_perimeters(name):
    from build123d import Compound, Face, Rectangle

    from tigerbee.models import build_profile

    placement = next(p for p in frame_arm_layout() if p.part_name == name and not p.mirror)
    # The inner/rootmost bore plus its 1.6 mm radius and 2 mm material ligament
    # defines the clamped base. The outer mounting pad is the natural shaft exit.
    from tigerbee.assembly import mounting_holes

    base_y = min(y for _, y in mounting_holes(name)) + 1.6 + 2.0
    region = (Pos(0, base_y - 100) * Rectangle(400, 200)).face()
    root = placement.place(Compound(children=build_profile(name).intersect(region).faces()))
    for plate_name in ("camera-plate", "rear-plate"):
        envelope = Face(build_profile(plate_name).outer_wire())
        excess = root.cut(envelope)
        assert sum(face.area for face in excess.faces()) < 1e-6, plate_name


@pytest.mark.parametrize("name", ["arm-type-1", "arm-type-2"])
def test_clamp_fit_preserves_every_source_opening_and_full_distal_shaft(name):
    from build123d import Compound, Face, Rectangle

    from tigerbee.assembly import mounting_holes
    from tigerbee.models import PartParameters, build_profile

    source = build_reference_profile(name, PartParameters(mounting_hole_diameter=3.2))
    current = build_profile(name)
    for old in source.inner_wires():
        old_face = Face(old)
        new = min(current.inner_wires(), key=lambda wire: (wire.center() - old.center()).length)
        new_face = Face(new)
        common = old_face.intersect(new_face)
        assert common is not None
        assert old_face.area == pytest.approx(sum(face.area for face in common.faces()), abs=1e-7)
        assert new_face.area == pytest.approx(old_face.area, abs=1e-7)
    # Only the base and a 2 mm transition outside it may change. Retaining the
    # entire source section beyond this plane excludes an artificial thin neck.
    protected_y = min(-114.0, min(y for _, y in mounting_holes(name)) + 1.6 + 2.0 + 2.0)
    region = (Pos(0, protected_y + 100) * Rectangle(400, 200)).face()
    old_shaft = Compound(children=source.intersect(region).faces())
    new_shaft = Compound(children=current.intersect(region).faces())
    assert sum(face.area for face in old_shaft.cut(new_shaft).faces()) < 1e-6
    assert sum(face.area for face in new_shaft.cut(old_shaft).faces()) < 1e-6


def test_new_rear_clamp_relief_joins_are_tangent():
    from tigerbee.models import PartParameters, build_profile

    source = build_reference_profile("arm-type-2", PartParameters(mounting_hole_diameter=3.2))
    old_points = [tuple(v) for v in source.outer_wire().vertices()]
    perimeter = build_profile("arm-type-2").outer_wire()
    for vertex in perimeter.vertices():
        if min(dist(tuple(vertex), point) for point in old_points) < 1e-6:
            continue
        adjacent = [
            edge
            for edge in perimeter.edges()
            if any((v.center() - vertex.center()).length < 1e-6 for v in edge.vertices())
        ]
        tangents = [
            edge.tangent_at(0 if (edge.position_at(0) - vertex.center()).length < 1e-6 else 1)
            for edge in adjacent
        ]
        assert len(tangents) == 2
        assert abs(tangents[0].dot(tangents[1])) == pytest.approx(1, abs=1e-7)


def test_rear_clamp_blend_keeps_at_least_eighteen_mm_continuous_section():
    from build123d import Edge

    from tigerbee.models import build_profile

    profile = build_profile("arm-type-2")
    # Sample the full blend at 0.02 mm intervals and its independently measured
    # narrowest section. A thin neck must not hide within the transition region.
    section_y_values = [-117 + index * 0.02 for index in range(151)] + [-115.29]
    for y in section_y_values:
        section = profile.intersect(Edge.make_line((-100, y), (100, y)))
        assert section is not None
        assert len(section.edges()) == 1
        assert section.edges()[0].length >= 18.0
