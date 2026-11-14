"""Tiger Beetle 7": the model follows the owner's tracings, and the parts go together."""

from math import hypot

import numpy as np
import pytest

from tigerbeetle import accessories as A
from tigerbeetle import checks as C
from tigerbeetle import frame as F
from tigerbeetle import model as M
from tigerbeetle import overlay

ACCESSORIES = {a.name: a for a in A.build_all()}


def test_every_frame_check_passes():
    failed = [r for r in C.frame_checks() if not r[1]]
    assert not failed, failed


def test_model_lies_on_the_ink():
    """Every outline, drawn back onto its scan, runs within the pen line of the tracing."""
    from tigerbeetle import trace as T

    plates = M.plates()
    for scan, name in ((1, "camera_plate"), (2, "bottom_plate"), (2, "top_plate")):
        p = plates[name]
        dev = overlay.deviation([p.outline], M.data()["plates"][name]["to_page"], p.shift, T._ink(scan))
        assert dev.mean() < 0.15 and np.percentile(dev, 95) < 0.4, (name, dev.mean())
    arm = M.arms()["front_right"][1]
    for tracing in ("arm_a", "arm_b"):
        dev = overlay.deviation([arm.outline], M.data()["arm"]["to_page"][tracing], arm.shift, T._ink(1))
        assert dev.mean() < 0.25 and np.percentile(dev, 95) < 1.0, (tracing, dev.mean())


def test_plates_are_mirror_symmetric():
    for p in M.plates().values():
        pts = M.resample(p.outline, 2.0)
        mirrored = pts * [-1, 1]
        d = np.min(np.hypot(*(mirrored[:, None, :] - p.outline[None, :, :]).transpose(2, 0, 1)), axis=1)
        assert d.max() < 0.2, p.name


def test_stack_is_the_datum():
    for name in ("camera_plate", "bottom_plate"):
        xy = {(h.x, h.y) for h in M.plates()[name].holes}
        assert {(sx * 15.25, sy * 15.25) for sx in (1, -1) for sy in (1, -1)} <= xy


def test_one_arm_four_places():
    motors = F.motors()
    assert len(motors) == 4
    for q in ("front", "rear"):
        r, l_ = motors[f"{q}_right"], motors[f"{q}_left"]
        assert r[0] == pytest.approx(-l_[0]) and r[1] == pytest.approx(l_[1])
    diag = hypot(motors["front_right"][0] - motors["rear_left"][0], motors["front_right"][1] - motors["rear_left"][1])
    assert 295 < diag < 315  # a 7 inch frame; the old reconstructions said 303-305


def test_standoffs():
    s = F.standoffs()
    assert len(s) == 8
    assert sorted({v[3] for v in s.values()}) == [M.TOP_GAP, M.TOP_GAP + M.T_ARM + M.T_PLATE]


def test_profiles_are_closed_smooth_curves():
    for part in (*M.plates().values(), M.arms()["front_right"][1]):
        f = F.face(part)
        assert f.is_valid and f.area > 0
        assert {e.geom_type.name for e in f.outer_wire().edges()} <= {"BSPLINE", "CIRCLE", "LINE"}


@pytest.mark.parametrize("name", sorted(ACCESSORIES))
def test_accessory_checks(name):
    failed = [r for r in A.check(ACCESSORIES[name]) if not r[1]]
    assert not failed, failed


def test_installed_accessories_do_not_overlap():
    assert A.clashes() == []
