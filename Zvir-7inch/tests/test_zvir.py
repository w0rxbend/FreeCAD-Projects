"""Zvir: the engine's geometric checks on this design, its payload and the sizing it is built on."""

import pytest
from zhalo import accessories as A
from zhalo import checks as C
from zhalo import equipment as E
from zhalo import frame as F
from zhalo import params as P
from zhalo import structure
from zhalo.export import accessory_clashes

from zvir import payload, profiles, sizing

ACCESSORIES = {acc.name: acc for acc in A.build_all()}


def test_the_engine_is_configured_for_this_design():
    assert (P.T_ARM, P.T_BOTTOM, P.T_MID, P.T_BRACE) == (sizing.T_ARM, sizing.T_BOTTOM, sizing.T_DECK, sizing.T_BRACE)
    assert P.BRACES and P.BAY_ON_DECK
    assert len(P.STANDOFFS) == 14
    assert {z0 for (_x, _y, z0, _h) in P.STANDOFFS.values()} == {P.Z_DECK}  # all on the deck
    assert {h for (_x, _y, _z0, h) in P.STANDOFFS.values()} == {sizing.STANDOFF_H}  # and all the same length
    assert set(F.SHEETS) == {"plate_bottom", "plate_mid", "plate_top", "arm", "brace", "core_nose", "core_tail", "puck"}
    assert P.PROP_D == pytest.approx(7 * 25.4)


def test_arm_is_widest_where_the_sandwich_lets_go():
    widths = {u: 2 * P.arm_half_width(u) for u in (0.0, sizing.EDGE_U, 95.0, P.ARM_NECK_U)}
    assert widths[sizing.EDGE_U] == pytest.approx(sizing.EDGE_W) == max(widths.values())
    assert widths[P.ARM_NECK_U] == pytest.approx(sizing.NECK_W)


def test_beam_model_first_mode_is_above_the_cruise_revs():
    edge = P.ARM_BOLT_U[1] + P.LEG_R
    arm = structure.Arm(
        "zvir",
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


def test_top_plate_stays_outside_the_prop_discs_in_plan():
    """The top plate is above the blades, so the engine's check does not look at it; it still keeps out of their way."""
    plate = F.parts()["plate_top"]
    for xy in P.MOTORS.values():
        disc = E.cylinder(*xy, P.Z_TOP - 1, P.Z_ROOF + 1, 2 * P.PROP_KEEPOUT_R)
        assert C.overlap(plate, disc) < C.EPS


def test_payload_is_part_of_the_equipment():
    gear = E.build()
    assert {"sbc", "servo", "cv_camera"} <= set(gear)
    parts = F.parts()
    for name in ("sbc", "servo"):
        hits = {n: v for n, p in parts.items() if (v := C.overlap(gear[name][0], p)) > C.EPS}
        assert not hits, (name, hits)


def test_camera_clears_the_frame_through_its_whole_travel():
    lo, hi = payload.TILT_RANGE
    assert lo == -90.0 and hi > 0.0
    parts = F.parts()
    for k in range(8):
        cam = payload.cv_camera(lo + (hi - lo) * k / 7)
        hits = {n: v for n, p in parts.items() if (v := C.overlap(cam, p)) > C.EPS}
        assert not hits, hits


def test_turret_stays_above_the_feet():
    low = min(payload.cv_camera(t).bounding_box().min.Z for t in (-90.0, -60.0, -30.0, 0.0, 15.0))
    feet = min(
        p.bounding_box().min.Z for a in A.build_all() if a.name.startswith("talon") for p in (a.part, *a.instances)
    )
    assert feet < low - 5.0


def test_companion_computer_bay():
    w, l, _t = payload.SBC_BOARD
    assert 2 * (sizing.MID[0] - P.STANDOFF_OD / 2) > w  # the board passes between the mid standoffs
    assert payload.SBC_FRONT_Y - l > P.R[1] + P.STANDOFF_OD / 2  # and ends ahead of the tail standoffs
    assert P.Z_TOP - payload.SBC_TOP > 8.0
    assert {xy for xy in payload.sbc_holes()} == {(sx * 24.5, y) for y in (-35.5, -93.5) for sx in (1, -1)}
    assert all(abs(x) == 22.0 for x, _y in profiles.TRAY_SCREWS)


def test_rigid_parts_are_not_tpu():
    assert {a.name for a in A.build_all() if a.material == "PETG"} == {
        "turret_bracket",
        "turret_cradle",
        "turret_spacer",
    }


@pytest.mark.parametrize("name", sorted(ACCESSORIES))
def test_accessory_checks(name):
    failed = [row for row in A.check(ACCESSORIES[name]) if not row[1]]
    assert not failed, failed


def test_installed_accessories_do_not_overlap():
    assert accessory_clashes() == []
