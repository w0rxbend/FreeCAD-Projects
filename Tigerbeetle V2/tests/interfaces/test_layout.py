from dataclasses import replace
from math import hypot

import pytest

from fpv_frame.geometry.datums import Point2
from fpv_frame.geometry.layout import build_layout
from fpv_frame.parameters.arms import ArmProfileParameters
from fpv_frame.parameters.layout import LayoutParameters
from fpv_frame.parameters.presets import get_preset


def frame_parameters():
    frame = get_preset("reference")
    profile = ArmProfileParameters(115, 37, 12, 24, 13.75)
    return replace(frame, arm=replace(frame.arm, profile=profile))


def test_four_arms_share_root_pitch_and_all_receiving_holes():
    frame = frame_parameters()
    layout = build_layout(frame)
    assert len(layout.arms) == 4
    assert len(layout.root_pattern.centers) == 2
    assert len(layout.standoffs) == 8
    for arm in layout.arms:
        assert arm.interface.root_pattern is layout.root_pattern
        first, second = arm.interface.hole_axes
        assert hypot(first.x - second.x, first.y - second.y) == pytest.approx(13.75)
        for plate_id in ("scan1_body", "scan2_broad"):
            centers = tuple(
                point
                for group in layout.plate_hole_groups(plate_id)
                for point in group.pattern.centers
            )
            for point in (first, second):
                assert min(hypot(point.x - other.x, point.y - other.y) for other in centers) < 1e-9


def test_motor_centroid_is_origin_and_each_pair_is_exactly_mirrored():
    layout = build_layout(frame_parameters())
    assert sum(arm.motor_center.x for arm in layout.arms) == pytest.approx(0)
    assert sum(arm.motor_center.y for arm in layout.arms) == pytest.approx(0)
    for end in ("front", "rear"):
        left, right = (layout.arm(f"arm_{end}_{side}") for side in ("left", "right"))
        assert left.motor_center.x == pytest.approx(-right.motor_center.x)
        assert left.motor_center.y == pytest.approx(right.motor_center.y)
        for a, b in zip(left.interface.hole_axes, right.interface.hole_axes, strict=True):
            assert a.x == pytest.approx(-b.x)
            assert a.y == pytest.approx(b.y)


def test_standoff_faces_and_member_holes_are_shared():
    frame = frame_parameters()
    layout = build_layout(frame)
    assert sorted(standoff.height for standoff in layout.standoffs) == [25] * 6 + [32] * 2
    for support in layout.standoffs:
        assert support.upper_z == frame.plate_elevations["scan2_long"]
        assert support.lower_z == (
            frame.plate_elevations[support.lower_plate] + frame.plate(support.lower_plate).thickness
        )
        for plate_id in (support.lower_plate, "scan2_long"):
            assert any(
                support.center in group.pattern.centers
                for group in layout.plate_hole_groups(plate_id)
            )


def test_length_pitch_and_stock_changes_preserve_shared_interfaces():
    frame = frame_parameters()
    assert frame.arm.profile is not None
    changed = replace(
        frame,
        arm=replace(
            frame.arm,
            thickness=6,
            profile=replace(frame.arm.profile, root_to_motor=130, root_hole_spacing=14),
        ),
    )
    layout = build_layout(changed)
    assert sum(arm.motor_center.y for arm in layout.arms) == pytest.approx(0)
    assert sorted(s.height for s in layout.standoffs) == [25] * 6 + [33] * 2
    first, second = layout.root_pattern.centers
    assert hypot(first.x - second.x, first.y - second.y) == pytest.approx(14)
    assert build_layout(frame).body_origin != layout.body_origin
    assert layout.body_point(0, 0) == layout.body_origin


def test_rejects_missing_profiles_and_invalid_layout_parameters():
    frame = frame_parameters()
    with pytest.raises(ValueError, match="profile"):
        build_layout(replace(frame, arm=replace(frame.arm, profile=None)))
    with pytest.raises(ValueError):
        LayoutParameters(front_root_half_span=-1)
    with pytest.raises(ValueError):
        LayoutParameters(front_root_y=-25)
    with pytest.raises(ValueError):
        build_layout(frame).plate_hole_groups("missing")
    assert build_layout(frame).root_pattern.centers[0] != Point2(0, 0)


def test_all_plate_hole_groups_preserve_bilateral_intent_and_source_mapping_roundtrip():
    layout = build_layout(frame_parameters())
    for group in layout.hole_groups:
        for point in group.pattern.centers:
            assert (
                min(hypot(point.x + other.x, point.y - other.y) for other in group.pattern.centers)
                < 1e-9
            )
    for pixel in (Point2(1638, 303), Point2(2182, 1982), Point2(1870.5, 1588.75)):
        restored = layout.global_to_master(layout.master_to_global(pixel.x, pixel.y))
        assert (restored.x, restored.y) == pytest.approx((pixel.x, pixel.y))


def test_frame_owns_layout_dimensions_for_serialization_and_geometry():
    frame = frame_parameters()
    changed = replace(frame, layout=replace(frame.layout, front_tip_y=115))
    layout = build_layout(changed)
    group = next(g for g in layout.hole_groups if g.name == "front_tip_standoff_pair")
    assert all(p.y == pytest.approx(layout.body_origin.y + 115) for p in group.pattern.centers)
    assert layout.dimensions is changed.layout
