"""TPU accessories: each one passes its checks, and the installed set does not collide."""

import pytest

from zhalo import accessories as A
from zhalo.export import accessory_clashes

ACCESSORIES = {acc.name: acc for acc in A.build_all()}


@pytest.mark.parametrize("name", sorted(ACCESSORIES))
def test_accessory_checks(name):
    failed = [row for row in A.check(ACCESSORIES[name]) if not row[1]]
    assert not failed, failed


def test_installed_accessories_do_not_overlap():
    assert accessory_clashes() == []


def test_mirrored_panels_are_mirror_images():
    right, left = ACCESSORIES["side_panel_right"].part, ACCESSORIES["side_panel_left"].part
    assert left.volume == pytest.approx(right.volume)
    assert left.bounding_box().min.X == pytest.approx(-right.bounding_box().max.X)
