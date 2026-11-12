"""The frame: outlines, layout numbers and every geometry check."""

from math import hypot

import pytest

from zhalo import checks as C
from zhalo import frame as F
from zhalo import params as P
from zhalo.outline import belt, lobe, scallop


def test_wheelbase_and_layout():
    assert hypot(2 * P.MOTOR_X, 2 * P.MOTOR_Y) == pytest.approx(P.WHEELBASE)
    assert P.BAY_STANDOFF_H == pytest.approx(P.STACK_STANDOFF_H + P.T_ARM + P.T_MID)
    # the arm axis runs through the stack bolt, both arm bolts and the motor
    assert P.on_arm(P.ARM_LEN) == pytest.approx((P.MOTOR_X, P.MOTOR_Y))


def test_belt_is_closed_and_tangent():
    a, b = lobe((0, 0), 5), lobe((30, 0), 5)
    stadium = belt([a, b])
    assert stadium.is_closed
    assert stadium.length == pytest.approx(2 * 30 + 2 * 3.141592653589793 * 5)


def test_scallop_reaches_the_asked_depth():
    from dataclasses import replace

    from build123d import Face

    a, b = lobe((0, 0), 5), lobe((40, 0), 5)
    shape = Face(belt([replace(a, link=scallop(a, b, 4.0)), replace(b, link=scallop(a, b, 4.0))]))
    # two scallops of 4 mm on a 10 mm wide stadium leave a 2 mm waist
    assert shape.is_inside((20, 0.9, 0)) and not shape.is_inside((20, 1.1, 0))


def test_sheets_are_single_faces_of_arcs_and_lines():
    for make in F.SHEETS.values():
        face = make().face()
        assert face.is_valid
        kinds = {e.geom_type.name for e in face.edges()}
        assert kinds <= {"LINE", "CIRCLE"}, kinds


def test_arm_root_stays_in_its_quadrant():
    # every arm root keeps ARM_GAP from both axes, so four of them meet without touching
    arm = F.parts()["arm_front_right"].bounding_box()
    assert arm.min.X == pytest.approx(P.ARM_GAP, abs=1e-6)
    assert arm.min.Y == pytest.approx(P.ARM_GAP, abs=1e-6)


def test_every_frame_check_passes():
    failed = [row for row in C.frame_checks() if not row[1]]
    assert not failed, failed
