"""The frame and its printed parts, checked the same way `bolid check` does, plus the design claims."""

from math import sqrt

import pytest

from bolid import accessories as ACC
from bolid import analysis as AN
from bolid import geometry as GEO
from bolid import params as P
from bolid.checks import frame_checks

FRAME = frame_checks()


@pytest.mark.parametrize("row", FRAME, ids=[r[0] for r in FRAME])
def test_frame(row):
    assert row[1], row[2]


@pytest.mark.parametrize("acc", ACC.build_all(), ids=lambda a: a.name)
def test_accessory(acc):
    failed = [r for r in ACC.check(acc) if not r[1]]
    assert not failed, failed


def test_no_accessory_clashes():
    assert ACC.clashes() == []


def test_true_x_five_inch():
    for x, y in P.MOTORS.values():
        assert abs(abs(x) - abs(y)) < 1e-9
        assert abs(2 * sqrt(x * x + y * y) - P.WHEELBASE) < 1e-6
    assert 5 * 25.4 <= P.PROP_D <= 5.2 * 25.4


def test_wheelbase_is_near_the_smallest_safe_one():
    assert AN.smallest_wheelbase() <= P.WHEELBASE <= AN.smallest_wheelbase() + 5.0


def test_taper_beats_a_uniform_arm_of_the_same_mass():
    taper = AN.chosen()
    uniform = AN.beam("uniform 14", lambda u: 14.0)
    assert taper.mass <= uniform.mass
    assert taper.f_vertical > 1.3 * uniform.f_vertical
    assert taper.f_side > uniform.f_side
    assert taper.k_vertical > uniform.k_vertical


def test_taper_is_as_strong_as_the_full_width_arm():
    full = AN.beam("uniform 20", lambda u: P.W_CLAMP)
    taper = AN.chosen()
    assert taper.f_vertical >= 0.99 * full.f_vertical
    assert taper.mass < 0.75 * full.mass


def test_arms_are_two_shapes_mirrored():
    fr, fl = GEO.arm("front_right").face, GEO.arm("front_left").face
    rr, rl = GEO.arm("rear_right").face, GEO.arm("rear_left").face
    assert abs(fr.area - fl.area) < 1e-6 and abs(rr.area - rl.area) < 1e-6
