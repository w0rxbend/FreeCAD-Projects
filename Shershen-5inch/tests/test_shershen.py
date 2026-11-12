"""Shershen: the Zhalo engine's checks, run on this design."""

import pytest
from zhalo import accessories as A
from zhalo import checks as C
from zhalo import frame as F
from zhalo.export import accessory_clashes

import shershen  # noqa: F401 - registers the design

ACCESSORIES = {acc.name: acc for acc in A.build_all()}


def test_the_design_is_registered():
    assert all(make.__module__ == "shershen.profiles" for make in F.SHEETS.values())
    assert {"head_19", "side_pod_right", "tail_fins", "claw", "stripe_pad"} <= set(ACCESSORIES)


def test_every_frame_check_passes():
    failed = [row for row in C.frame_checks() if not row[1]]
    assert not failed, failed


def test_profiles_are_arcs_and_lines():
    for make in F.SHEETS.values():
        kinds = {e.geom_type.name for e in make().face().edges()}
        assert kinds <= {"LINE", "CIRCLE"}, kinds


@pytest.mark.parametrize("name", sorted(ACCESSORIES))
def test_accessory_checks(name):
    failed = [row for row in A.check(ACCESSORIES[name]) if not row[1]]
    assert not failed, failed


def test_installed_accessories_do_not_overlap():
    assert accessory_clashes() == []
