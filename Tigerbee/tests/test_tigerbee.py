"""Tigerbee 5": the engine's checks on this design, its Tiger Beetle style and its sizing."""

import pytest
from zhalo import accessories as A
from zhalo import checks as C
from zhalo import frame as F
from zhalo import params as P
from zhalo import structure, tiger
from zhalo.export import accessory_clashes

import tigerbee

ACCESSORIES = {acc.name: acc for acc in A.build_all()}


def test_the_engine_is_configured_for_this_design():
    assert P.T_ARM == tigerbee.T_ARM and P.BAY_ON_DECK and not P.BRACES
    assert len(P.STANDOFFS) == 8 and {h for (*_xy, _z, h) in P.STANDOFFS.values()} == {tigerbee.STANDOFF_H}
    assert set(F.SHEETS) == {"plate_bottom", "plate_mid", "plate_top", "arm", "core_nose", "core_tail"}


def test_front_and_rear_arms_at_the_same_angle():
    fr, rr = P.MOTORS["front_right"], P.MOTORS["rear_right"]
    assert fr[0] == pytest.approx(rr[0]) and fr[1] == pytest.approx(-rr[1])


def test_tiger_beetle_style():
    top = tiger.top_plate()
    assert len(top.windows) >= 2 * len(tiger.STYLE.chevron_rows)  # a pair of chevrons per row
    assert any("Wire" in type(w).__name__ for w in tiger.arm().windows)  # the diamond past the motor


def test_arm_sizing():
    edge = P.ARM_BOLT_U[1] + P.LEG_R
    arm = structure.Arm(
        "tigerbee",
        P.T_ARM,
        P.ARM_LEN - edge,
        lambda x: 2 * P.arm_half_width(x + edge),
        pad=P.ARM_NECK_BACK,
        tip_mass=tigerbee.TIP_MASS,
    )
    r = structure.analyse(arm)
    assert r.load_v > 1300 and r.load_h > 3000 and r.freq_v > 550


def test_every_frame_check_passes():
    failed = [r for r in C.frame_checks() if not r[1]]
    assert not failed, failed


def test_profiles_are_arcs_and_lines():
    for make in F.SHEETS.values():
        assert {e.geom_type.name for e in make().face().edges()} <= {"LINE", "CIRCLE"}


@pytest.mark.parametrize("name", sorted(ACCESSORIES))
def test_accessory_checks(name):
    failed = [r for r in A.check(ACCESSORIES[name]) if not r[1]]
    assert not failed, failed


def test_installed_accessories_do_not_overlap():
    assert accessory_clashes() == []
