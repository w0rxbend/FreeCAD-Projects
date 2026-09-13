import pytest
from build123d import Box, Circle, Compound, Pos, Rectangle, extrude

from tigerbee.validation import FastenerAxis, audit_frame, require_frame_fit


def fixture_frame():
    parts = []
    profile = Rectangle(60, 70)
    for x in (-20, 20):
        profile -= Pos(x, 10) * Circle(1.6)
    for name, z in (("rear-plate", 0), ("camera-plate", 10), ("top-plate", 35)):
        part = Pos(0, 0, z) * extrude(profile, amount=2)
        part.label = name
        parts.append(part)
    motors = {}
    for end, y in (("front", 105), ("rear", -105)):
        for side, x in (("left", -109.5), ("right", 109.5)):
            name = f"{end}-{side}-arm"
            part = Pos(x, y, 5) * extrude(Rectangle(20, 20) - Circle(3.5), amount=5)
            part.label = name
            parts.append(part)
            motors[name] = (x, y)
    joints = [
        FastenerAxis(f"joint-{x}", x, 10, 0, 37, ("rear-plate", "camera-plate", "top-plate"))
        for x in (-20, 20)
    ]
    return parts, joints, motors


def test_actual_solids_pass_symmetry_bores_and_propeller_clearance():
    parts, joints, motors = fixture_frame()
    report = audit_frame(Compound(children=parts), joints, motors)
    assert report["issues"] == []
    require_frame_fit(report)
    assert len(report["joint_checks"]) == 6
    assert all(check["coaxial"] for check in report["joint_checks"])
    assert report["minimum_edge_ligament_mm"] == pytest.approx(8.4)
    assert min(c["tip_gap_mm"] for c in report["propeller_clearances"]) == pytest.approx(32.2)


def test_displaced_plate_is_rejected_from_actual_geometry():
    parts, joints, motors = fixture_frame()
    parts[1] = parts[1].translate((0.2, 0, 0))
    report = audit_frame(Compound(children=parts), joints, motors)
    assert any("asymmetry" in issue for issue in report["issues"])
    assert any("noncoaxial" in issue for issue in report["issues"])
    with pytest.raises(ValueError, match="Frame geometry failed"):
        require_frame_fit(report)


def test_hidden_bore_obstruction_rejected_even_with_both_circular_rims():
    parts, joints, motors = fixture_frame()
    # Fill only the middle of one bore. Its two surface circles remain intact.
    plugged = parts[1].fuse(Pos(20, 10, 10.75) * extrude(Circle(1.7), amount=0.5))
    plugged.label = parts[1].label
    parts[1] = plugged
    report = audit_frame(Compound(children=parts), joints, motors)
    assert any("blocked shaft passage" in issue for issue in report["issues"])
    with pytest.raises(ValueError, match="blocked shaft"):
        require_frame_fit(report)


def test_interference_between_other_components_is_rejected():
    parts, joints, motors = fixture_frame()
    obstruction = Pos(0, 0, 1) * Box(2, 2, 2)
    obstruction.label = "obstruction"
    parts.append(obstruction)
    report = audit_frame(Compound(children=parts), joints, motors)
    assert report["interferences"]
    with pytest.raises(ValueError, match="component interference"):
        require_frame_fit(report)


def test_reported_motor_coordinates_cannot_hide_actual_bore_position():
    parts, joints, motors = fixture_frame()
    motors["front-right-arm"] = (111, 105)
    report = audit_frame(Compound(children=parts), joints, motors)
    with pytest.raises(ValueError, match="motor center differs"):
        require_frame_fit(report)


def test_fastener_span_must_reach_both_faces_of_all_members():
    parts, joints, motors = fixture_frame()
    joints[0] = FastenerAxis("short", -20, 10, 0.5, 37, joints[0].members)
    report = audit_frame(Compound(children=parts), joints, motors)
    with pytest.raises(ValueError, match="incomplete bore"):
        require_frame_fit(report)


def test_symmetric_layout_still_rejects_overlapping_propeller_discs():
    parts, joints, motors = fixture_frame()
    for i, part in enumerate(parts):
        if "arm" not in part.label:
            continue
        delta_y = -25 if "front" in part.label else 25
        parts[i] = part.translate((0, delta_y, 0))
        x, y = motors[part.label]
        motors[part.label] = (x, y + delta_y)
    report = audit_frame(Compound(children=parts), joints, motors)
    assert all(v == pytest.approx(0) for v in report["symmetry_difference_mm3"].values())
    with pytest.raises(ValueError, match="overlapping 7-inch"):
        require_frame_fit(report)


def test_nonfinite_motor_coordinates_do_not_bypass_comparison():
    parts, joints, motors = fixture_frame()
    motors["front-right-arm"] = (float("nan"), 105)
    with pytest.raises(ValueError, match="invalid nominal motor"):
        require_frame_fit(audit_frame(Compound(children=parts), joints, motors))


def test_thin_mounting_ligament_is_rejected_even_when_bore_is_clear():
    parts, joints, motors = fixture_frame()
    for x in (-25, 25):
        parts[1] = parts[1].cut(Pos(x, 10, 10) * extrude(Rectangle(4, 4), amount=2))
    parts[1].label = "camera-plate"
    report = audit_frame(Compound(children=parts), joints, motors)
    assert all(c["coaxial"] for c in report["joint_checks"])
    assert report["minimum_edge_ligament_mm"] == pytest.approx(1.4)
    with pytest.raises(ValueError, match="insufficient mounting material"):
        require_frame_fit(report)


def test_equal_diagonals_outside_measured_range_are_rejected():
    parts, joints, motors = fixture_frame()
    for index, part in enumerate(parts):
        if "arm" not in part.label:
            continue
        delta_x = -5 if "left" in part.label else 5
        parts[index] = part.translate((delta_x, 0, 0))
        x, y = motors[part.label]
        motors[part.label] = (x + delta_x, y)
    report = audit_frame(Compound(children=parts), joints, motors)
    assert report["diagonal_wheelbases_mm"][0] == pytest.approx(report["diagonal_wheelbases_mm"][1])
    with pytest.raises(ValueError, match="303–304"):
        require_frame_fit(report)


def test_extra_opening_cannot_pass_declared_topology_contract():
    parts, joints, motors = fixture_frame()
    expected = {part.label: (1 if "arm" in part.label else 2) for part in parts}
    report = audit_frame(Compound(children=parts), joints, motors, expected_openings=expected)
    require_frame_fit(report)
    extra = parts[1].cut(Pos(0, 0, 10) * extrude(Circle(2), amount=2))
    extra.label = parts[1].label
    parts[1] = extra
    report = audit_frame(Compound(children=parts), joints, motors, expected_openings=expected)
    with pytest.raises(ValueError, match="unexpected openings"):
        require_frame_fit(report)


def test_shaft_cannot_pass_through_an_undeclared_component():
    parts, joints, motors = fixture_frame()
    # This solid does not touch the listed plates, but obstructs their shared screw.
    obstruction = Pos(20, 10, 20) * Box(4, 4, 2)
    obstruction.label = "forgotten-spacer"
    parts.append(obstruction)
    report = audit_frame(Compound(children=parts), joints, motors)
    assert report["interferences"] == []
    with pytest.raises(ValueError, match="blocked shaft passage"):
        require_frame_fit(report)


def test_positive_but_insufficient_propeller_gap_is_rejected():
    parts, joints, motors = fixture_frame()
    for index, part in enumerate(parts):
        if "arm" not in part.label:
            continue
        x, y = motors[part.label]
        new_y = 89.9 if y > 0 else -89.9
        parts[index] = part.translate((0, new_y - y, 0))
        motors[part.label] = (x, new_y)
    report = audit_frame(Compound(children=parts), joints, motors)
    assert min(c["tip_gap_mm"] for c in report["propeller_clearances"]) == pytest.approx(2)
    with pytest.raises(ValueError, match="insufficient tip gap"):
        require_frame_fit(report)


def test_opening_contract_cannot_silently_skip_a_component():
    parts, joints, motors = fixture_frame()
    report = audit_frame(
        Compound(children=parts), joints, motors, expected_openings={"top-plate": 2}
    )
    with pytest.raises(ValueError, match="cover every component"):
        require_frame_fit(report)


def test_standoff_exteriors_must_also_be_mirror_symmetric():
    parts, joints, motors = fixture_frame()
    for index, x in enumerate((-20, 20), start=1):
        outside_x = x + (0.2 if x > 0 else 0)
        profile = Pos(outside_x, 10) * Circle(3) - Pos(x, 10) * Circle(1.6)
        tube = Pos(0, 0, 20) * extrude(profile, amount=5)
        tube.label = f"standoff-{index:02}"
        parts.append(tube)
    report = audit_frame(Compound(children=parts), joints, motors)
    assert report["interferences"] == []
    with pytest.raises(ValueError, match="asymmetry: standoff"):
        require_frame_fit(report)
