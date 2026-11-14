"""The frame and its printed parts, checked the same way `vektor check` does."""

import pytest

from vektor import accessories as ACC
from vektor import arm_fe as FE
from vektor import geometry as GEO
from vektor import params as P
from vektor.checks import frame_checks

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


def test_box_arm_beats_a_solid_arm():
    box, solid = FE.chosen(), FE.solid_arm(8.0)
    assert box.mass < 0.75 * solid.mass
    assert box.stiffness > 3 * solid.stiffness
    assert box.freq > 1.5 * solid.freq


def test_spacers_alone_do_not_make_a_box():
    assert FE.box_arm(12.0, "rigid").stiffness < FE.solid_arm(8.0).stiffness


def test_tail_has_vtx_and_two_rx_antennas():
    tail = next(a for a in ACC.build_all() if a.name == "tail_trident")
    rows = {r[0]: r[1] for r in tail.checks}
    assert rows["VTX antenna: SMA bulkhead, leaning back"]
    assert rows["two receiver antennas 90 deg apart"]
    assert rows["antennas above the props"]


def test_true_x_and_prop_size():
    xs = {(abs(x), abs(y)) for x, y in P.MOTORS.values()}
    assert len(xs) == 1
    x, y = xs.pop()
    assert abs(x - y) < 1e-6 and abs(2 * (x * x + y * y) ** 0.5 - P.WHEELBASE) < 0.01
    assert 7 * 25.4 <= P.PROP_D <= 8 * 25.4


def test_web_tabs_fit_their_slots():
    assert P.SLOT_W > P.T_WEB
    assert len(GEO.web_tabs(100.0)) == P.TABS
