"""Three A4-calibrated plate profiles, built from mirrored analytical half contours.

Nominal stations are engineering millimeters in the common body datum. Names
identify design features, not individual ink pixels. Circular arcs replace broad
traced curves; paired openings are reflected from one definition. Structural
bores come exclusively from geometry.layout, shared with arms and standoffs.
"""

from dataclasses import dataclass

from build123d import CenterOf, Edge, Face, Part, Plane, Vector, Wire, extrude

from fpv_frame.geometry.layout import build_layout
from fpv_frame.parameters.frame import FrameParameters
from fpv_frame.parameters.layout import LayoutParameters
from fpv_frame.parameters.plates import OutlineStation, PlateId, PlateProfileParameters

XY = tuple[float, float]


@dataclass(frozen=True)
class _Span:
    name: str
    end: XY
    through: XY | None = None
    controls: tuple[XY, XY] | None = None


@dataclass(frozen=True)
class _Contour:
    start: XY
    spans: tuple[_Span, ...]


# Each half uses a small set of semantic stations; no opposite-side coordinates
# are stored. The body datum is the common lower electronics-square center.
_CONTOURS: dict[PlateId, _Contour] = {
    "scan1_body": _Contour(
        (0, 116),
        (
            _Span("nose_valley", (10, 108.5), controls=((5, 116), (5, 108.5))),
            _Span("nose_lobe_peak", (19, 113.5), controls=((15, 108.5), (13.5, 113.5))),
            _Span("nose_lobe", (23.5, 109), (22.2, 112.2)),
            _Span("nose_neck", (17.2, 96), controls=((23.5, 104), (17.2, 105))),
            _Span("neck_front", (17.2, 84)),
            _Span("forward_mount_lobe", (20, 77), (20, 81)),
            _Span("electronics_neck", (17.2, 67), (18, 73)),
            _Span("electronics_rear", (17.2, 54)),
            _Span("rear_mount_lobe", (20, 46), (20, 50)),
            _Span("shoulder_neck", (20, 39)),
            _Span("front_shoulder_blend", (28, 36), controls=((20, 29), (24, 38))),
            _Span("front_root_lobe", (33.5, 31.5), controls=((31, 36), (33.5, 35))),
            _Span("front_root_side", (33.2, 18)),
            _Span("body_waist", (24.5, 0), (26.5, 9)),
            _Span("rear_root_side", (32.5, -18), (26.5, -10)),
            _Span("rear_root_lobe", (31.5, -33.5)),
            _Span("rear_lobe_base", (25.5, -38.5), (30, -38)),
            _Span("rear_bridge_corner", (13, -29.5)),
            _Span("rear_bridge", (0, -29.5)),
        ),
    ),
    "scan2_broad": _Contour(
        (0, 28.5),
        (
            _Span("front_notch_inner", (6, 28.5)),
            _Span("front_notch_outer", (8, 28.5), (7, 27.5)),
            _Span("front_lobe_ramp", (14, 28.5)),
            _Span("front_root_lobe", (29, 37), (22, 32.5)),
            _Span("front_root_side", (34, 31.5), (33.5, 36)),
            _Span("front_root_lower", (33, 16)),
            _Span("front_waist", (30, 9), (29.5, 12)),
            _Span("center_bore_lobe", (34, 0), (33, 4)),
            _Span("rear_waist", (30, -9), (32, -5)),
            _Span("rear_root_upper", (32.5, -19), (31, -15)),
            _Span("rear_root_side", (31, -33.5)),
            _Span("tail_shoulder", (20.5, -43), (25.5, -38.5)),
            _Span("tail_neck", (20.5, -49)),
            _Span("tail_stem", (17.5, -60), (18, -55)),
            _Span("tail_slot_lobe", (20.2, -80.5), (17.5, -76)),
            _Span("tail_waist", (18.5, -87), (19, -84)),
            _Span("rear_tip_lobe", (21.5, -94), (20.5, -90)),
            _Span("rear_tip_base", (13, -98.5), (18, -100)),
            _Span("rear_fork_inside", (10.5, -92.5)),
            _Span("rear_center_notch", (6, -92.5)),
            _Span("rear_center_lobe", (3.5, -96.5), (5, -95.5)),
            _Span("rear_center", (0, -96.5)),
        ),
    ),
    "scan2_long": _Contour(
        (0, 75),
        (
            _Span("camera_fork_bowl", (17, 86), (11, 78)),
            _Span("camera_fork_inner", (21, 99), (21, 92)),
            _Span("camera_tip_inner", (14.5, 108)),
            _Span("camera_tip_outer", (23.5, 111), (17, 114)),
            _Span("camera_outer_flange", (32.5, 93)),
            _Span("camera_flange_return", (28, 83), (33, 87)),
            _Span("camera_shoulder", (25, 74), (26, 79)),
            _Span("accessory_front", (37, 67), controls=((25, 68), (31, 69))),
            _Span("accessory_rear", (37, 60), (38.5, 63.5)),
            _Span("front_spine", (21, 54), (26, 57.5)),
            _Span("front_spine_end", (21, 38)),
            _Span("front_standoff_front", (32, 35), (28, 38)),
            _Span("front_standoff_rear", (31, 28), (33.5, 31.5)),
            _Span("wide_spine_front", (21, 22), (24, 27)),
            _Span("wide_spine_bump1", (21, 11), (23, 13)),
            _Span("wide_spine_center", (21, -9)),
            _Span("wide_spine_bump2", (21, -17), (23, -14)),
            _Span("wide_spine_rear", (21, -23)),
            _Span("rear_standoff_front", (30, -28), (25, -27)),
            _Span("rear_standoff_rear", (30, -38), (33, -33)),
            _Span("narrow_spine_front", (16.5, -46), (20, -40)),
            _Span("narrow_spine_rear", (16.5, -81)),
            _Span("tail_tip_front", (22, -89), (19, -86)),
            _Span("tail_tip_rear", (22, -96)),
            _Span("tail_fork_inside", (11, -96), (16.5, -100)),
            _Span("tail_fork_bowl", (0, -82), (8, -86)),
        ),
    ),
}


def nominal_plate_profile(component_id: PlateId) -> PlateProfileParameters:
    """Editable semantic width/station defaults; caps stay analytically connected.

    A supplied profile may override a subset of these named stations. This lets
    neck widths or shoulder positions change independently of mounting patterns.
    Arc controls follow the endpoint displacement instead of remaining behind.
    """
    spans = _CONTOURS[component_id].spans
    # Multiple named corners can share a longitudinal row. One station controls
    # that row; additional cap/return points remain part of its analytic detail.
    by_y: dict[float, OutlineStation] = {}
    for span in spans:
        if span.end[0] > 0:
            by_y.setdefault(span.end[1], OutlineStation(span.name, span.end[1], span.end[0]))
    return PlateProfileParameters(tuple(by_y[y] for y in sorted(by_y)))


def _datum_point(params: FrameParameters, point: XY) -> XY:
    """Move semantic geometry with shared stations, retaining nominal feature sizes.

    Smoothstep displacement blends neighboring datum offsets without a kink at
    mounting rows. Outside the end rows the offset is constant so end margins
    remain unchanged. A lateral scale interpolates between the symmetric spans.
    """
    reference, current = LayoutParameters(), params.layout
    rows = (
        (
            reference.rear_tip_y,
            current.rear_tip_y,
            current.rear_tip_half_span / reference.rear_tip_half_span,
        ),
        (
            reference.rear_root_y,
            current.rear_root_y,
            current.rear_root_half_span / reference.rear_root_half_span,
        ),
        (0.0, 0.0, 1.0),
        (
            reference.front_root_y,
            current.front_root_y,
            current.front_root_half_span / reference.front_root_half_span,
        ),
        (reference.forward_stack_y, current.forward_stack_y, 1.0),
        (
            reference.front_tip_y,
            current.front_tip_y,
            current.front_tip_half_span / reference.front_tip_half_span,
        ),
    )
    x, y = point
    delta, scale = rows[0][1] - rows[0][0], rows[0][2]
    for a, b in zip(rows, rows[1:], strict=False):
        if y < a[0]:
            break
        t = min(1.0, (y - a[0]) / (b[0] - a[0]))
        blend = t * t * (3 - 2 * t)
        delta = (a[1] - a[0]) * (1 - blend) + (b[1] - b[0]) * blend
        scale = a[2] * (1 - blend) + b[2] * blend
    return x * scale, y + delta


def _half_outline(params: FrameParameters, component_id: PlateId) -> list[Edge]:
    contour = _CONTOURS[component_id]
    profile = params.plate(component_id).profile
    overrides = {} if profile is None else {s.name: s for s in profile.stations}
    allowed = {s.name for s in nominal_plate_profile(component_id).stations}
    if overrides.keys() - allowed:
        raise ValueError(f"Unknown {component_id} outline stations: {overrides.keys() - allowed}")
    edges = []
    previous = contour.start
    previous_nominal = previous
    for span in contour.spans:
        station = overrides.get(span.name)
        end = span.end if station is None else (station.half_width, station.axial_position)
        start_point, end_point = _datum_point(params, previous), _datum_point(params, end)

        shift_x = ((end[0] - span.end[0]) + (previous[0] - previous_nominal[0])) / 2
        shift_y = ((end[1] - span.end[1]) + (previous[1] - previous_nominal[1])) / 2
        if span.controls is not None:
            edge = Edge.make_bezier(
                start_point,
                *(_datum_point(params, (p[0] + shift_x, p[1] + shift_y)) for p in span.controls),
                end_point,
            )
        elif span.through is not None:
            edge = Edge.make_three_point_arc(
                start_point,
                _datum_point(params, (span.through[0] + shift_x, span.through[1] + shift_y)),
                end_point,
            )
        else:
            edge = Edge.make_line(start_point, end_point)
        edges.append(edge)
        previous, previous_nominal = end, span.end
    return edges


def _outer_face(params: FrameParameters, component_id: PlateId) -> Face:
    half = _half_outline(params, component_id)
    wire = Wire.combine([*half, *(edge.mirror(Plane.YZ) for edge in half)])[0]
    return Face(wire)


def _rounded_polygon(points: tuple[XY, ...], radius: float = 0.6) -> Wire:
    face = Face(Wire.make_polygon([(*p, 0) for p in points]))
    return face.fillet_2d(radius, face.vertices()).outer_wire() if radius else face.outer_wire()


def _slot(center: XY, width: float, height: float, radius: float = 1.2) -> Wire:
    x, y = center
    return _rounded_polygon(
        (
            (x - width / 2, y - height / 2),
            (x + width / 2, y - height / 2),
            (x + width / 2, y + height / 2),
            (x - width / 2, y + height / 2),
        ),
        radius,
    )


def _circle(center: XY, diameter: float) -> Wire:
    return Wire.make_circle(diameter / 2, Plane(origin=(*center, 0)))


def _paired(wire: Wire) -> list[Wire]:
    return [wire, wire.mirror(Plane.YZ)]


def _apertures(params: FrameParameters, component_id: PlateId) -> list[Wire]:
    """Nonstructural openings only; bores shared by parts are defined in layout."""
    if component_id == "scan1_body":
        return [
            _circle((0, 61.5), 17.5),
            _slot((0, 82.5), 10.5, 7.6),
            _slot((0, 40.5), 10.5, 7.6),
            _rounded_polygon(((0, 111.5), (4.8, 103), (0, 97), (-4.8, 103)), 1.5),
        ]
    if component_id == "scan2_broad":
        result = [_slot((0, y), 10.8, 7.6) for y in (-47.5, -65.5, -83.5)]
        quadrant = Wire(
            [
                Edge.make_line((1.8, 1.8, 0), (10, 1.8, 0)),
                Edge.make_three_point_arc((10, 1.8, 0), (4.6, 4.6, 0), (1.8, 10, 0)),
                Edge.make_line((1.8, 10, 0), (1.8, 1.8, 0)),
            ]
        )
        result.extend(_paired(quadrant))
        result.extend(_paired(quadrant.mirror(Plane.XZ)))
        result.extend(_paired(_circle((28, 0), 4.5)))
        # Two partial electronics rows at the rear, not complete square patterns.
        for half_pitch, y in (
            (params.stack.secondary_pitch / 2, -75.5),
            (params.stack.primary_pitch / 2, -81),
        ):
            result.extend(_paired(_circle((half_pitch, y), params.clearance_hole_diameter)))
        result.append(_circle((0, -91), params.clearance_hole_diameter))
        return result
    result = [_circle((0, 68), 4.6)]
    for half_pitch, y in ((27.3, 91), (31.3, 63.5)):
        result.extend(_paired(_circle((half_pitch, y), 4.6)))
    # Six paired relief rows share one wide and one narrow diagonal primitive.
    for y in (27.5, 7.5, -12.5, -30, -49.5, -69):
        wide = y > -20
        inner, outer = (5, 15) if wide else (3.4, 11.3)
        height = 16.5 if wide else 14.0
        relief = _rounded_polygon(
            ((inner, y + height / 2), (outer, y), (outer, y - height / 2), (inner, y)), 0.9
        )
        result.extend(_paired(relief))
    result.extend(_paired(_rounded_polygon(((8, 72.5), (17.5, 70.5), (12, 63.5), (7.5, 66)), 1.1)))
    result.extend(_paired(_rounded_polygon(((10.5, 58.5), (16, 56), (16, 40), (10.5, 43)), 0.7)))
    # Crossing strokes obscure the lower edge: clean rounded-rectangle hypothesis.
    result.append(_slot((0, 55.5), 9.4, 10, 0.9))
    return result


def plate_profile(params: FrameParameters, component_id: PlateId) -> Face:
    """A planar face at global Z=0, used unchanged by extrusion and drawings."""
    layout = build_layout(params)
    body_origin = layout.body_origin
    move = Vector(body_origin.x, body_origin.y, 0)
    outer = _outer_face(params, component_id).outer_wire().translate(move)
    holes = []
    for wire in _apertures(params, component_id):
        center = wire.center(CenterOf.MASS)
        x, y = _datum_point(params, (center.X, center.Y))
        holes.append(wire.translate(Vector(x - center.X, y - center.Y, 0) + move))
    for group in layout.plate_hole_groups(component_id):
        holes.extend(
            _circle((point.x, point.y), group.pattern.hole_diameter)
            for point in group.pattern.centers
        )
    face = Face(outer, holes)
    if not face.is_valid or face.area <= 0:
        raise ValueError(f"{component_id}: invalid or empty plate profile")
    return face


def build_plate(params: FrameParameters, component_id: PlateId) -> Part:
    """Extrude the validated manufacturing face; assembly supplies its Z placement."""
    face = plate_profile(params, component_id)
    part = extrude(face, amount=params.plate(component_id).thickness, dir=(0, 0, 1))
    part.label = component_id
    if not part.is_valid or len(part.solids()) != 1 or part.volume <= 0:
        raise ValueError(f"{component_id}: expected one valid solid")
    return part


def build_camera_plate(params: FrameParameters) -> Part:
    return build_plate(params, "scan1_body")


def build_rear_plate(params: FrameParameters) -> Part:
    return build_plate(params, "scan2_broad")


def build_top_plate(params: FrameParameters) -> Part:
    return build_plate(params, "scan2_long")
