"""Sfera: the engine's geometric checks on this design, its cargo and the figures it is built on."""

from math import hypot

import pytest
from zhalo import accessories as A
from zhalo import checks as C
from zhalo import equipment as E
from zhalo import frame as F
from zhalo import params as P
from zhalo import structure
from zhalo.export import accessory_clashes

from sfera import aero, payload, profiles, sizing
from sfera.accessories import cargo

ACCESSORIES = {acc.name: acc for acc in A.build_all()}


def test_the_engine_is_configured_for_this_design():
    assert (P.T_ARM, P.T_BOTTOM, P.T_MID) == (sizing.T_ARM, sizing.T_BOTTOM, sizing.T_DECK)
    assert not P.BRACES and P.BAY_ON_DECK
    assert len(P.STANDOFFS) == 14
    assert {z0 for (_x, _y, z0, _h) in P.STANDOFFS.values()} == {P.Z_DECK}
    assert {h for (_x, _y, _z0, h) in P.STANDOFFS.values()} == {sizing.STANDOFF_H}
    assert set(F.SHEETS) == {"plate_bottom", "plate_mid", "plate_top", "arm", "puck"}


def test_layout_is_a_true_x_about_the_load():
    assert P.MOTOR_X == pytest.approx(P.MOTOR_Y)
    assert P.ARM_ANGLE == pytest.approx(45.0)
    assert {round(hypot(*xy), 6) for xy in P.MOTORS.values()} == {sizing.MOTOR_R}
    rim = [
        (x, y, z, h)
        for n, (x, y, z, h) in P.STANDOFFS.items()
        if not n.startswith(("standoff_stack", "standoff_front"))
    ]
    assert len(rim) == 8 and {round(hypot(x, y), 6) for x, y, _z, _h in rim} == {sizing.RING_R}


def test_arm_is_the_one_that_was_sized():
    edge = P.ARM_BOLT_U[1] + P.LEG_R
    assert P.ARM_LEN - edge == pytest.approx(72.4, abs=0.1)  # the free length the arm was analysed at
    arm = structure.Arm(
        "sfera",
        P.T_ARM,
        P.ARM_LEN - edge,
        lambda x: 2 * P.arm_half_width(x + edge),
        pad=P.ARM_NECK_BACK,
        tip_mass=sizing.TIP_MASS,
    )
    result = structure.analyse(arm)
    assert result.freq_v > 330  # the beam model reads about 15 % high: see the README for the finite-element figure
    assert result.load_v > 1500 and result.load_h > 3500


def test_every_frame_check_passes():
    failed = [row for row in C.frame_checks() if not row[1]]
    assert not failed, failed


def test_profiles_are_arcs_and_lines():
    for make in F.SHEETS.values():
        kinds = {e.geom_type.name for e in make().face().edges()}
        assert kinds <= {"LINE", "CIRCLE"}, kinds


def test_no_propeller_is_over_the_body_or_the_load():
    for xy in P.MOTORS.values():
        disc = E.cylinder(*xy, -80.0, 80.0, P.PROP_D)
        for name in ("plate_top", "plate_mid"):
            assert C.overlap(F.parts()[name], E.cylinder(0, 0, -80, 80, 2 * sizing.BODY_R) & disc) < C.EPS, name
        assert C.overlap(payload.crate(), disc) < C.EPS
    assert hypot(payload.CRATE[0], payload.CRATE[1]) / 2 < payload.SHADOW_R


def test_aerodynamic_figures():
    report = aero.report()
    assert report["blockage_percent"] < 6.0  # arms and fingers under a propeller
    assert report["hull_clearance_mm"] >= P.PROP_MARGIN
    ideal, real = aero.hover_power(2.5)
    assert 150 < ideal < real < 800


def test_cargo_plate_grid():
    nuts = cargo.grid()
    assert len(nuts) == len(set(nuts)) >= 20
    assert {(sx * 15.25, sy * 15.25) for sx in (1, -1) for sy in (1, -1)} <= set(nuts)  # a 30.5 mm square
    assert all(m in nuts for m in cargo.MOUNTS)
    assert payload.FEET_Z < payload.CARGO_Z - payload.CRATE[2] - 5.0


def test_companion_computer_bay():
    gear = E.build()
    assert {"sbc", "cargo"} <= set(gear)
    hits = {n: v for n, p in F.parts().items() if (v := C.overlap(gear["sbc"][0], p)) > C.EPS}
    assert not hits, hits
    assert set(payload.sbc_holes()) == {(sx * 29.0, sizing.SBC_Y + sy * 11.5) for sx in (1, -1) for sy in (1, -1)}


def test_deck_has_the_common_hole_patterns():
    names = {h.name for h in profiles.deck().holes}
    assert {"vtx_20", "bay_30p5", "bay_20", "tray"} <= names
    assert sum(1 for h in profiles.deck().holes if h.name == "bay_30p5") == 8  # one square in each side bay


def test_rigid_parts_are_not_tpu():
    assert {a.name for a in A.build_all() if a.material == "PETG"} == {"cargo_plate", "cargo_hook"}


@pytest.mark.parametrize("name", sorted(ACCESSORIES))
def test_accessory_checks(name):
    failed = [row for row in A.check(ACCESSORIES[name]) if not row[1]]
    assert not failed, failed


def test_installed_accessories_do_not_overlap():
    assert accessory_clashes() == []
