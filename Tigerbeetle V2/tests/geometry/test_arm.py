from dataclasses import replace

import pytest
from build123d import Axis, CenterOf, Face, Part, Plane, Vector

from fpv_frame.geometry.layout import build_layout
from fpv_frame.parameters.arms import reference_arm_profile
from fpv_frame.parameters.presets import PRESET_NAMES, get_preset
from fpv_frame.parts.arm import arm_profile, build_arm


def test_reference_arm_has_all_eight_openings_and_a_valid_extrusion():
    params = get_preset("reference")
    profile = arm_profile(params)
    solid = build_arm(params)
    assert isinstance(profile, Face)
    assert isinstance(solid, Part)
    assert profile.is_valid
    assert len(profile.inner_wires()) == 8
    assert len(solid.solids()) == 1
    assert solid.volume == pytest.approx(profile.area * 5)
    assert solid.bounding_box().size.Z == pytest.approx(5)
    assert profile.bounding_box().size.Y == pytest.approx(169, abs=0.5)
    assert profile.bounding_box().size.X == pytest.approx(35, abs=0.5)


def test_every_root_hole_uses_the_accepted_shared_pattern():
    params = get_preset("reference")
    profile = arm_profile(params)
    holes = profile.inner_wires()
    centers = [wire.center(CenterOf.MASS) for wire in holes]
    for expected in build_layout(params).root_pattern.centers:
        assert any(
            (point.X - expected.x) ** 2 + (point.Y - expected.y) ** 2 < 1e-8 for point in centers
        )


def test_motor_paddle_is_symmetric_but_root_is_handed():
    profile = arm_profile(get_preset("reference"))
    mirrored = profile.mirror(Plane.YZ)
    # The motor/paddle halves agree exactly; the root's interlocking notch does not.
    assert abs(profile.area - mirrored.area) < 1e-8
    difference = profile.cut(mirrored)
    assert difference.area > 1
    assert difference.bounding_box().max.Y < 50


def test_arm_dimensions_change_actual_geometry_and_preserve_holes():
    params = get_preset("reference")
    dimensions = reference_arm_profile()
    changed = replace(
        params,
        arm=replace(
            params.arm,
            profile=replace(
                dimensions,
                root_to_motor=dimensions.root_to_motor + 10,
                shaft_width=14,
            ),
        ),
    )
    old, new = arm_profile(params), arm_profile(changed)
    assert new.bounding_box().max.Y - old.bounding_box().max.Y == pytest.approx(10)
    assert len(new.inner_wires()) == len(old.inner_wires()) == 8
    assert new.area > old.area


@pytest.mark.parametrize("name", PRESET_NAMES)
def test_each_regression_preset_produces_one_valid_arm(name):
    part = build_arm(get_preset(name))
    assert part.is_valid
    assert len(part.solids()) == 1
    assert part.volume > 0


def test_one_canonical_arm_clears_all_four_shared_placements():
    from itertools import combinations

    params = get_preset("reference")
    canonical = build_arm(params)
    parts = []
    for placement in build_layout(params).arms:
        transform = placement.transform
        arm = canonical.mirror(Plane.YZ) if transform.mirror_x else canonical
        parts.append(
            arm.rotate(Axis.Z, transform.angle_deg).translate(
                Vector(transform.origin.x, transform.origin.y, transform.origin.z)
            )
        )
    for first, second in combinations(parts, 2):
        assert first.distance_to(second) >= params.manufacturing.general_clearance
        assert sum(shape.volume for shape in (first.intersect(second) or [])) < 1e-7
