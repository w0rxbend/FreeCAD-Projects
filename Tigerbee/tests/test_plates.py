"""Verify the new analytic plate geometry and its shared mounting interfaces."""

from dataclasses import replace

import pytest
from build123d import GeomType, Plane, extrude

from tigerbee.plates import PlateDimensions, build_plate_profile

SUPPORT_ROWS = [
    (19.25, 108.75),
    (28.276473347, 31.571443191),
    (25.607638615, -33.325257818),
    (16.5, -94),
]
REAR_ROWS = [
    (26.814735520, 17.928556809),
    (28.276473347, 31.571443191),
    (26.262374744, -20.174742182),
    (25.607638615, -33.325257818),
    (16.5, -94),
    (15.25, 15.25),
    (15.25, -15.25),
]


def paired(rows):
    return [(side * x, y) for x, y in rows for side in (-1, 1)]


@pytest.mark.parametrize(
    "name,rows,opening_count",
    [
        ("rear-plate", REAR_ROWS, 32),
        ("top-plate", SUPPORT_ROWS, 30),
    ],
)
def test_plate_is_analytic_symmetric_and_all_mounts_are_closed_holes(name, rows, opening_count):
    points = paired(rows)
    profile = build_plate_profile(name, points)
    assert profile.is_valid
    assert len(profile.inner_wires()) == opening_count
    assert {edge.geom_type for edge in profile.edges()} <= {GeomType.LINE, GeomType.CIRCLE}
    assert (profile - profile.mirror(Plane.YZ)).area < 1e-6
    assert (profile.mirror(Plane.YZ) - profile).area < 1e-6
    circles = [
        wire.edges()[0]
        for wire in profile.inner_wires()
        if len(wire.edges()) == 1 and wire.edges()[0].geom_type == GeomType.CIRCLE
    ]
    for x, y in points:
        matching = [
            edge
            for edge in circles
            if abs(edge.arc_center.X - x) < 1e-6 and abs(edge.arc_center.Y - y) < 1e-6
        ]
        assert len(matching) == 1
        assert matching[0].radius == pytest.approx(1.6)
    solid = extrude(profile, amount=2.5, dir=(0, 0, 1))
    assert solid.is_valid and len(solid.solids()) == 1
    assert solid.volume == pytest.approx(profile.area * 2.5, abs=1e-4)


def test_top_has_six_identical_chevrons_on_each_side():
    profile = build_plate_profile("top-plate", paired(SUPPORT_ROWS))
    windows = [
        wire
        for wire in profile.inner_wires()
        if 0 < wire.bounding_box().min.X < 6 and wire.bounding_box().max.Y < 40
    ]
    assert len(windows) == 6
    boxes = sorted([wire.bounding_box() for wire in windows], key=lambda b: b.min.Y)
    for first, second in zip(boxes, boxes[1:], strict=False):
        assert second.min.Y - first.min.Y == pytest.approx(20)
        assert second.size.X == pytest.approx(first.size.X)
        assert second.size.Y == pytest.approx(first.size.Y)


def test_dimensions_change_slot_geometry_without_moving_mounts():
    original = build_plate_profile("rear-plate", paired(REAR_ROWS))
    wider = build_plate_profile(
        "rear-plate", paired(REAR_ROWS), dimensions=replace(PlateDimensions(), rear_slot_width=12)
    )
    assert wider.area == pytest.approx(original.area - 3 * 2 * 7, abs=1e-4)
    assert len(wider.inner_wires()) == len(original.inner_wires())
    assert (wider - wider.mirror(Plane.YZ)).area < 1e-6


def test_asymmetric_mounting_pattern_is_rejected():
    with pytest.raises(ValueError, match="symmetric"):
        build_plate_profile("rear-plate", [(16, -94)])


def test_invalid_window_spacing_is_rejected():
    with pytest.raises(ValueError, match="pitch"):
        build_plate_profile(
            "top-plate",
            paired(SUPPORT_ROWS),
            dimensions=replace(PlateDimensions(), chevron_pitch=10),
        )


@pytest.mark.parametrize("name", ["camera-plate", "rear-plate", "top-plate"])
def test_exported_plate_profile_is_symmetric_and_has_tangent_perimeter(name):
    from tigerbee.models import build_profile

    profile = build_profile(name)
    assert (profile - profile.mirror(Plane.YZ)).area < 1e-6
    assert {edge.geom_type for edge in profile.edges()} <= {GeomType.LINE, GeomType.CIRCLE}
    perimeter = profile.outer_wire()
    for vertex in perimeter.vertices():
        adjacent = [
            edge
            for edge in perimeter.edges()
            if any((v.center() - vertex.center()).length < 1e-6 for v in edge.vertices())
        ]
        assert len(adjacent) == 2
        tangents = [
            edge.tangent_at(0 if (edge.position_at(0) - vertex.center()).length < 1e-6 else 1)
            for edge in adjacent
        ]
        assert abs(tangents[0].dot(tangents[1])) == pytest.approx(1, abs=1e-6)


@pytest.mark.parametrize(
    "name,centers,radius",
    [
        ("top-plate", [(-28, 58), (28, 58), (-27, 91), (27, 91)], 2.5),
        ("rear-plate", [(-28, 0), (28, 0)], 2.5),
        (
            "rear-plate",
            [
                (0, -18),
                (0, 18),
                (-18, 0),
                (18, 0),
                (-15, -81),
                (15, -81),
                (-10, -75),
                (10, -75),
                (0, -91),
            ],
            1.5,
        ),
    ],
)
def test_scan_service_openings_are_preserved_as_nominal_symmetric_circles(name, centers, radius):
    from tigerbee.models import build_profile

    profile = build_profile(name)
    circles = [
        w.edges()[0]
        for w in profile.inner_wires()
        if len(w.edges()) == 1 and w.edges()[0].geom_type == GeomType.CIRCLE
    ]
    for x, y in centers:
        assert any(
            abs(edge.arc_center.X - x) < 1e-6
            and abs(edge.arc_center.Y - y) < 1e-6
            and abs(edge.radius - radius) < 1e-6
            for edge in circles
        )


def test_camera_retains_source_square_round_and_slot_metrics():
    from build123d import Face

    from tigerbee.models import build_profile

    profile = build_profile("camera-plate")
    square = next(
        w
        for w in profile.inner_wires()
        if abs(w.bounding_box().center().X) < 1e-6 and abs(w.bounding_box().center().Y) < 1e-6
    )
    assert square.bounding_box().size.X == pytest.approx(15)
    assert square.bounding_box().size.Y == pytest.approx(15)
    assert sorted(e.radius for e in square.edges() if e.geom_type == GeomType.CIRCLE) == [2] * 4
    rounds = [
        e
        for w in profile.inner_wires()
        for e in w.edges()
        if e.geom_type == GeomType.CIRCLE and e.radius > 9
    ]
    assert len(rounds) == 1 and rounds[0].radius == pytest.approx(9.25)
    assert rounds[0].arc_center.Y == pytest.approx(61.25)
    slots = [w for w in profile.inner_wires() if 11 < w.bounding_box().size.X < 12]
    assert len(slots) == 2
    assert Face(slots[0]).area == pytest.approx(Face(slots[1]).area)
    for slot in slots:
        assert slot.bounding_box().size.X == pytest.approx(11.5)
        assert slot.bounding_box().size.Y == pytest.approx(8.5)


def test_camera_outer_silhouette_stays_within_cad_design_envelope():
    from build123d import Face

    from tigerbee.models import build_profile, build_reference_profile

    reference = Face(build_reference_profile("camera-plate").outer_wire()).translate((0, 61.25, 0))
    actual = Face(build_profile("camera-plate").outer_wire())
    # Symmetry correction preserves the design: under 0.2% outline change,
    # unchanged front/rear extent and less than 0.1 mm total width correction.
    assert (actual - reference).area + (reference - actual).area < reference.area * 0.002
    assert actual.bounding_box().size.Y == pytest.approx(reference.bounding_box().size.Y, abs=1e-6)
    assert abs(actual.bounding_box().size.X - reference.bounding_box().size.X) < 0.1


def test_oversize_mounting_bore_cannot_silently_open_plate_edge():
    from tigerbee.layout import plate_mounting_holes

    with pytest.raises(ValueError, match="opening|perimeter|connected"):
        build_plate_profile("top-plate", plate_mounting_holes("top-plate"), hole_diameter=18)


def test_clearance_bores_must_keep_two_millimeter_material_ligament():
    from tigerbee.layout import plate_mounting_holes

    with pytest.raises(ValueError, match="ligament"):
        build_plate_profile("rear-plate", plate_mounting_holes("rear-plate"), hole_diameter=3.5)


@pytest.mark.parametrize("diameter", [-1, 0, float("nan"), float("inf")])
def test_direct_camera_builder_rejects_invalid_center_diameter(diameter):
    with pytest.raises(ValueError, match="center_hole_diameter"):
        build_plate_profile("camera-plate", [], center_hole_diameter=diameter)
