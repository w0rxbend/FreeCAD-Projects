"""Strila: the engine's geometric checks on this design, and the sizing it is built on."""

import pytest
from zhalo import accessories as A
from zhalo import checks as C
from zhalo import frame as F
from zhalo import params as P
from zhalo import structure
from zhalo.export import accessory_clashes

from strila import sizing

ACCESSORIES = {acc.name: acc for acc in A.build_all()}


def test_the_engine_is_configured_for_this_design():
    assert (P.T_ARM, P.T_BOTTOM, P.T_MID) == (sizing.T_ARM, sizing.T_BOTTOM, sizing.T_DECK)
    assert not P.BRACES and P.BAY_ON_DECK
    assert {z0 for (_x, _y, z0, _h) in P.STANDOFFS.values()} == {P.Z_DECK}  # all eight on the deck
    assert {h for (_x, _y, _z0, h) in P.STANDOFFS.values()} == {sizing.STANDOFF_H}  # and all the same length
    assert set(F.SHEETS) == {"plate_bottom", "plate_mid", "plate_top", "arm", "core_nose", "core_tail"}


def test_arm_is_widest_where_the_sandwich_lets_go():
    widths = {u: 2 * P.arm_half_width(u) for u in (0.0, sizing.EDGE_U, 60.0, P.ARM_NECK_U)}
    assert widths[sizing.EDGE_U] == pytest.approx(sizing.EDGE_W) == max(widths.values())
    assert widths[P.ARM_NECK_U] == pytest.approx(sizing.NECK_W)


def test_beam_model_side_load_stresses_root_and_neck_alike():
    edge = P.ARM_BOLT_U[1] + P.LEG_R
    arm = structure.Arm(
        "strila", P.T_ARM, P.ARM_LEN - edge, lambda x: 2 * P.arm_half_width(x + edge), pad=P.ARM_NECK_BACK
    )
    result = structure.analyse(arm)
    assert result.evenness_h > 0.9  # mean stress within 10 % of the peak along the whole free length
    assert result.freq_v > 350


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
