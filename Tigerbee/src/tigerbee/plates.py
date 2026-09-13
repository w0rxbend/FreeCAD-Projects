"""Analytic, symmetric plate designs derived from the frame's reference silhouettes.

Coordinates use the assembly clamp datum. The camera silhouette preserves the
FreeCAD right half, with tangent joins, reflection, and a raised front clamp
shoulder for the 305 mm true-X mounting pattern. Rear/top dimensions are
nominal design choices from the pen tracing; source profiles remain untouched.
Mounting coordinates belong to the caller's shared interface, not to the outline.
"""

import json
from dataclasses import dataclass
from importlib.resources import files
from math import isfinite, sqrt

from build123d import Edge, Face, GeomType, Plane, Pos, RectangleRounded, Shape, ThreePointArc, Wire


@dataclass(frozen=True)
class PlateDimensions:
    """Explicit dimensions shared by the analytic plate sketches, in mm."""

    corner_radius: float = 2.0
    transition_radius: float = 1.0
    top_shoulder_radius: float = 5.0
    camera_datum_y: float = 61.25
    camera_clamp_shoulder_extension: float = 5.0
    rear_front_shoulder_extension: float = 5.0
    camera_round_diameter: float = 18.5
    camera_square_size: float = 15.0
    camera_square_radius: float = 2.0
    camera_slot_width: float = 11.5
    camera_slot_height: float = 8.5
    camera_slot_radius: float = 2.5
    camera_slot_pitch: float = 42.0
    rear_slot_width: float = 10.0
    rear_slot_height: float = 7.0
    rear_slot_radius: float = 2.0
    rear_slot_pitch: float = 18.0
    rear_first_slot_y: float = -47.0
    cross_half_web: float = 2.0
    cross_extent: float = 10.0
    cross_corner_radius: float = 0.6
    chevron_width: float = 8.0
    chevron_height: float = 12.0
    chevron_skew: float = 6.0
    chevron_pitch: float = 20.0
    chevron_first_y: float = -68.0
    chevron_x: float = 9.5
    chevron_corner_radius: float = 1.0

    def validate(self) -> None:
        for name, value in vars(self).items():
            if not isfinite(value):
                raise ValueError(f"{name} must be finite")
            if not name.endswith("_y") and value <= 0:
                raise ValueError(f"{name} must be positive")
        if self.cross_extent <= self.cross_half_web:
            raise ValueError("cross_extent must exceed cross_half_web")
        if self.chevron_skew >= self.chevron_height:
            raise ValueError("chevron_skew must be smaller than chevron_height")
        if self.chevron_pitch <= self.chevron_height:
            raise ValueError("chevron_pitch must exceed chevron_height")
        if self.rear_slot_pitch <= self.rear_slot_height:
            raise ValueError("rear_slot_pitch must exceed rear_slot_height")


DEFAULT_PLATE_DIMENSIONS = PlateDimensions()
MINIMUM_MOUNT_LIGAMENT_MM = 2.0


def _rounded_polygon(points: list[tuple[float, float]], radius: float) -> Face:
    face = Face(Wire.make_polygon(points, close=True))
    if face.normal_at().Z < 0:
        face = Face(Wire.make_polygon(list(reversed(points)), close=True))
    return face.fillet_2d(radius, face.vertices())


def _symmetric_polygon(right: list[tuple[float, float]], radius: float) -> Face:
    points = right + [(-x, y) for x, y in reversed(right) if x != 0]
    return _rounded_polygon(points, radius)


def _circle(x: float, y: float, radius: float) -> Face:
    return Face(Wire([Edge.make_circle(radius, Plane(origin=(x, y, 0)))]))


def _one_face(shape: Shape) -> Face:
    faces = shape.faces()
    if len(faces) != 1 or not faces[0].is_valid:
        raise ValueError("Plate must remain one connected valid face")
    return faces[0]


def _smooth_outline(face: Face, radius: float) -> Face:
    """Round only discontinuous joins; existing tangent arcs remain untouched."""
    corners = []
    perimeter = face.outer_wire()
    for vertex in perimeter.vertices():
        edges = [
            edge
            for edge in perimeter.edges()
            if any((v.center() - vertex.center()).length < 1e-6 for v in edge.vertices())
        ]
        tangents = [
            edge.tangent_at(0 if (edge.position_at(0) - vertex.center()).length < 1e-6 else 1)
            for edge in edges
        ]
        if len(tangents) == 2 and abs(abs(tangents[0].dot(tangents[1])) - 1) > 1e-8:
            corners.append(vertex)
    return face.fillet_2d(radius, corners) if corners else face


def _camera_outline(dimensions: PlateDimensions) -> Face:
    """Retain the authoritative FreeCAD right silhouette and reflect it exactly.

    Original source points define circular radii and straight constraints. The
    left half's small drafting offsets are discarded. A 1 mm tangent blend
    removes inherited non-tangent joins. The front clamp shoulder arc pair moves
    forward by 5 mm for the true-X interface; overall width and length are retained.
    """
    data = json.loads(files("tigerbee").joinpath("profiles", "camera-plate.json").read_text())
    segments = next(loop["segments"] for loop in data["loops"] if loop["outer"])
    edges = []
    for segment in segments:
        # Raise the inherited front clamp shoulder as a rigid arc pair. This
        # makes room for the 305 mm true-X interface without widening the CAD
        # silhouette or altering the camera neck, rear clamp, or openings.
        points = [
            (x, y + dimensions.camera_clamp_shoulder_extension if -31 < y < -23 else y)
            for x, y in segment["points"]
        ]
        if all(x >= -1e-8 for x, _ in points):
            edge = (
                Edge.make_line(*points)
                if segment["kind"] == "line"
                else ThreePointArc(*points).edge()
            )
            edges.extend([edge, edge.mirror(Plane.YZ)])
        elif min(x for x, _ in points) < 0 < max(x for x, _ in points):
            edges.append(
                Edge.make_line(*points)
                if segment["kind"] == "line"
                else ThreePointArc(*points).edge()
            )
    outline = Face(Wire(edges))
    if outline.normal_at().Z < 0:
        outline = -outline
    outline = _smooth_outline(outline, dimensions.transition_radius)
    return outline.translate((0, dimensions.camera_datum_y, 0))


def _camera_openings(dimensions: PlateDimensions, center_diameter: float | None) -> list[Face]:
    datum = dimensions.camera_datum_y
    openings = [
        _circle(0, datum, (center_diameter or dimensions.camera_round_diameter) / 2),
        RectangleRounded(
            dimensions.camera_square_size,
            dimensions.camera_square_size,
            dimensions.camera_square_radius,
        ).face(),
        _rounded_polygon(
            [
                (0, datum + 49),
                (4.5, datum + 41.25),
                (2.5, datum + 35),
                (-2.5, datum + 35),
                (-4.5, datum + 41.25),
            ],
            1,
        ),
    ]
    for side in (-1, 1):
        openings.append(
            (
                Pos(0, datum + side * dimensions.camera_slot_pitch / 2)
                * RectangleRounded(
                    dimensions.camera_slot_width,
                    dimensions.camera_slot_height,
                    dimensions.camera_slot_radius,
                )
            ).face()
        )
        openings.extend([_circle(side * 18, 0, 3), _circle(0, side * 18, 3)])
    return openings


def _rear_outline(dimensions: PlateDimensions) -> Face:
    # Broad clamp plate transitions to a 36 mm strap stem with two end lugs.
    right: list[tuple[float, float]] = [
        (0, 29 + dimensions.rear_front_shoulder_extension),
        (13, 29 + dimensions.rear_front_shoulder_extension),
        (28, 37 + dimensions.rear_front_shoulder_extension),
        (34, 34 + dimensions.rear_front_shoulder_extension),
        (34, 17),
        (29, 10),
        (34, 0),
        (29, -11),
        (33, -20),
        (32, -35),
        (20, -39),
        (20, -52),
        (18, -56),
        (18, -76),
        (20, -81),
        (18, -87),
        (21.5, -94),
        (18, -99),
        (13, -99),
        (9, -91),
        (5, -96),
        (0, -96),
    ]
    return _symmetric_polygon(right, dimensions.corner_radius)


def _cross_openings(dimensions: PlateDimensions) -> list[Face]:
    # Four equal lobes with a concave quarter-circle instead of convex hulls.
    inner, outer = dimensions.cross_half_web, dimensions.cross_extent
    radius = outer - inner
    midpoint = outer - radius / sqrt(2)
    lobe = Face(
        Wire(
            [
                Edge.make_line((inner, inner), (outer, inner)),
                ThreePointArc((outer, inner), (midpoint, midpoint), (inner, outer)).edge(),
                Edge.make_line((inner, outer), (inner, inner)),
            ]
        )
    )
    lobe = lobe.fillet_2d(dimensions.cross_corner_radius, lobe.vertices())
    left = lobe.mirror(Plane.YZ)
    return [lobe, left, lobe.mirror(Plane.XZ), left.mirror(Plane.XZ)]


def _rear_openings(dimensions: PlateDimensions) -> list[Face]:
    openings = _cross_openings(dimensions)
    openings.extend([_circle(x, 0, 2.5) for x in (-28, 28)])
    accessory_points = [
        (0, -18),
        (0, 18),
        (-18, 0),
        (18, 0),
        (-15, -81),
        (15, -81),
        (-10, -75),
        (10, -75),
        (0, -91),
    ]
    openings.extend([_circle(x, y, 1.5) for x, y in accessory_points])
    for index in range(3):
        slot = Pos(0, dimensions.rear_first_slot_y - index * dimensions.rear_slot_pitch) * (
            RectangleRounded(
                dimensions.rear_slot_width,
                dimensions.rear_slot_height,
                dimensions.rear_slot_radius,
            )
        )
        openings.append(slot.face())
    return openings


def _top_outline(dimensions: PlateDimensions) -> Face:
    # Nominal shoulders envelop the four support rows without fused bosses.
    right = [
        (0, -100),
        (22, -100),
        (22, -88),
        (18, -82),
        (18, -48),
        (22, -42),
        (31, -39),
        (31, -28),
        (22, -23),
        (22, 20),
        (34, 26),
        (34, 37),
        (22, 43),
        (22, 48),
        (33, 53),
        (33, 63),
        (24, 70),
        (24, 79),
        (33, 89),
        (33, 96),
        (24.5, 114.5),
        (0, 114.5),
    ]
    points = right + [(-x, y) for x, y in reversed(right) if x != 0]
    outline = Face(Wire.make_polygon(points, close=True))
    if outline.normal_at().Z < 0:
        outline = Face(Wire.make_polygon(list(reversed(points)), close=True))
    shoulders = [v for v in outline.vertices() if abs(v.X) > 30 and -42 < v.Y < 100]
    outline = outline.fillet_2d(dimensions.top_shoulder_radius, shoulders)
    outline = _smooth_outline(outline, dimensions.corner_radius)
    front = _circle(0, 92, 14).fuse(
        Face(Wire.make_polygon([(-14, 92), (14, 92), (14, 125), (-14, 125)], close=True))
    )
    outline = _one_face(outline.cut(front, _circle(0, -100, 11)))
    return _smooth_outline(outline, dimensions.transition_radius)


def _top_openings(dimensions: PlateDimensions) -> list[Face]:
    openings = [_circle(x, y, 2.5) for x, y in [(-28, 58), (28, 58), (-27, 91), (27, 91)]]
    half_width = dimensions.chevron_width / 2
    half_height = dimensions.chevron_height / 2
    for index in range(6):
        x = dimensions.chevron_x
        y = dimensions.chevron_first_y + index * dimensions.chevron_pitch
        right = _rounded_polygon(
            [
                (x - half_width, y + half_height),
                (x + half_width, y + half_height - dimensions.chevron_skew),
                (x + half_width, y - half_height),
                (x - half_width, y - half_height + dimensions.chevron_skew),
            ],
            dimensions.chevron_corner_radius,
        )
        openings.extend([right, right.mirror(Plane.YZ)])
    for x in (-13.0, 13.0):
        openings.append((Pos(x, 58) * RectangleRounded(5, 17, 1.5)).face())
    openings.append((Pos(0, 57) * RectangleRounded(8, 10, 1.5)).face())
    # Equal front shoulder windows, with a 5 mm central service opening.
    right = _rounded_polygon([(8, 68), (17, 71), (15, 77), (8, 74)], 1)
    openings.extend([right, right.mirror(Plane.YZ), _circle(0, 69, 2.5)])
    return openings


def build_plate_profile(
    name: str,
    mounting_holes: list[tuple[float, float]],
    hole_diameter: float = 3.2,
    dimensions: PlateDimensions = DEFAULT_PLATE_DIMENSIONS,
    center_hole_diameter: float | None = None,
) -> Face:
    """Build an analytic plate around the supplied shared mounting-hole pattern.

    The caller must supply a left-right symmetric pattern in the assembly datum.
    Nominal shoulders provide mounting material without union seams or slivers.
    Consumers must additionally verify all interface clearances on the final solid.
    """
    dimensions.validate()
    if not isfinite(hole_diameter) or hole_diameter <= 0:
        raise ValueError("hole_diameter must be positive and finite")
    if center_hole_diameter is not None and (
        not isfinite(center_hole_diameter) or center_hole_diameter <= 0
    ):
        raise ValueError("center_hole_diameter must be positive and finite")
    if any(not isfinite(value) for point in mounting_holes for value in point):
        raise ValueError("Mounting hole coordinates must be finite")
    point_set = {(round(x, 7), round(y, 7)) for x, y in mounting_holes}
    if any((round(-x, 7), round(y, 7)) not in point_set for x, y in mounting_holes):
        raise ValueError("Mounting pattern must be left-right symmetric")
    if name == "camera-plate":
        outline = _camera_outline(dimensions)
        openings = _camera_openings(dimensions, center_hole_diameter)
    elif name == "rear-plate":
        outline = _rear_outline(dimensions)
        openings = _rear_openings(dimensions)
    elif name == "top-plate":
        outline = _top_outline(dimensions)
        openings = _top_openings(dimensions)
    else:
        raise ValueError("Unknown analytic plate name")
    holes = [_circle(x, y, hole_diameter / 2) for x, y in mounting_holes]
    profile = _one_face(outline.cut(*openings, *holes).clean())
    if len(profile.inner_wires()) != len(openings) + len(holes):
        raise ValueError("Parameters merge an opening or break through the plate perimeter")
    wires = list(profile.inner_wires())
    for x, y in mounting_holes:
        bore = next(
            wire
            for wire in wires
            if len(wire.edges()) == 1
            and wire.edges()[0].geom_type == GeomType.CIRCLE
            and abs(wire.edges()[0].arc_center.X - x) < 1e-6
            and abs(wire.edges()[0].arc_center.Y - y) < 1e-6
        )
        boundaries = [profile.outer_wire()] + [wire for wire in wires if not wire.is_same(bore)]
        ligament = min(bore.distance_to(boundary) for boundary in boundaries)
        if ligament < MINIMUM_MOUNT_LIGAMENT_MM - 1e-6:
            raise ValueError(
                f"Mounting bore at ({x:.3f}, {y:.3f}) leaves {ligament:.3f} mm ligament; "
                f"at least {MINIMUM_MOUNT_LIGAMENT_MM} mm is required"
            )
    return profile
