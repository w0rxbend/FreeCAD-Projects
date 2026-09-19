"""Part builders: plate outlines and cutouts, the handed arm, the standoff.

Plate half-contours and the arm outline are the sibling project's scan-calibrated
geometry (Tigerbeetle V2, parts/plates.py and parts/arm.py) with values inlined.
"""

from math import cos, radians, sin

from build123d import Align, Cylinder, Edge, Face, Part, Plane, Pos, Wire, extrude

from tigerbee import params as P
from tigerbee.mounts import Hole

XY = tuple[float, float]
MIN_Z = (Align.CENTER, Align.CENTER, Align.MIN)


def column(x: float, y: float, z0: float, h: float, r: float) -> Cylinder:
    """Cylinder of radius r whose lower face is at z0 (Cylinder is Z-centred by default)."""
    return Pos(x, y, z0) * Cylinder(r, h, align=MIN_Z)


# --- plate outlines: half contours, mirrored in X -------------------------------
# span = (end,) line | (end, through) 3-point arc | (end, None, (c1, c2)) cubic bezier
def L(end: XY):
    return (end,)


def A(end: XY, through: XY):
    return (end, through)


def B(end: XY, c1: XY, c2: XY):
    return (end, None, (c1, c2))


_CONTOURS: dict[str, tuple[XY, list]] = {
    "plate_mid": ((0, 116), [
        B((10, 108.5), (5, 116), (5, 108.5)), B((19, 113.5), (15, 108.5), (13.5, 113.5)),
        A((23.5, 109), (22.2, 112.2)), B((17.2, 96), (23.5, 104), (17.2, 105)),
        L((17.2, 84)), A((20, 77), (20, 81)), A((17.2, 67), (18, 73)), L((17.2, 54)),
        A((20, 46), (20, 50)), L((20, 39)), B((28, 36), (20, 29), (24, 38)),
        B((33.5, 31.5), (31, 36), (33.5, 35)), L((33.2, 18)), A((24.5, 0), (26.5, 9)),
        A((32.5, -18), (26.5, -10)), L((31.5, -33.5)), A((25.5, -38.5), (30, -38)),
        L((13, -29.5)), L((0, -29.5)),
    ]),
    "plate_bottom": ((0, 28.5), [
        L((6, 28.5)), A((8, 28.5), (7, 27.5)), L((14, 28.5)), A((29, 37), (22, 32.5)),
        A((34, 31.5), (33.5, 36)), L((33, 16)), A((30, 9), (29.5, 12)), A((34, 0), (33, 4)),
        A((30, -9), (32, -5)), A((32.5, -19), (31, -15)), L((31, -33.5)),
        A((20.5, -43), (25.5, -38.5)), L((20.5, -49)), A((17.5, -60), (18, -55)),
        A((20.2, -80.5), (17.5, -76)), A((18.5, -87), (19, -84)), A((21.5, -94), (20.5, -90)),
        A((13, -98.5), (18, -100)), L((10.5, -92.5)), L((6, -92.5)), A((3.5, -96.5), (5, -95.5)),
        L((0, -96.5)),
    ]),
    "plate_top": ((0, 75), [
        A((17, 86), (11, 78)), A((21, 99), (21, 92)), L((14.5, 108)), A((23.5, 111), (17, 114)),
        L((32.5, 93)), A((28, 83), (33, 87)), A((25, 74), (26, 79)),
        B((37, 67), (25, 68), (31, 69)), A((37, 60), (38.5, 63.5)), A((21, 54), (26, 57.5)),
        L((21, 38)), A((32, 35), (28, 38)), A((31, 28), (33.5, 31.5)), A((21, 22), (24, 27)),
        A((21, 11), (23, 13)), L((21, -9)), A((21, -17), (23, -14)), L((21, -23)),
        A((30, -28), (25, -27)), A((30, -38), (33, -33)), A((16.5, -46), (20, -40)),
        L((16.5, -81)), A((22, -89), (19, -86)), L((22, -96)), A((11, -96), (16.5, -100)),
        A((0, -82), (8, -86)),
    ]),
}


def _outer_face(plate: str) -> Face:
    start, spans = _CONTOURS[plate]
    half, prev = [], start
    for span in spans:
        end = span[0]
        if len(span) == 1:
            half.append(Edge.make_line(prev, end))
        elif span[1] is not None:
            half.append(Edge.make_three_point_arc(prev, span[1], end))
        else:
            half.append(Edge.make_bezier(prev, *span[2], end))
        prev = end
    return Face(Wire.combine([*half, *(e.mirror(Plane.YZ) for e in half)])[0])


def _rounded_polygon(points: tuple[XY, ...], radius: float) -> Wire:
    face = Face(Wire.make_polygon([(*p, 0) for p in points]))
    return face.fillet_2d(radius, face.vertices()).outer_wire()


def _slot(center: XY, width: float, height: float, radius: float = 1.2) -> Wire:
    x, y, w, h = *center, width / 2, height / 2
    return _rounded_polygon(((x - w, y - h), (x + w, y - h), (x + w, y + h), (x - w, y + h)), radius)


def _circle(center: XY, diameter: float) -> Wire:
    return Wire.make_circle(diameter / 2, Plane(origin=(*center, 0)))


def _paired(wire: Wire) -> list[Wire]:
    return [wire, wire.mirror(Plane.YZ)]


def cutouts(plate: str) -> list[Wire]:
    """Non-round scanned openings (round holes come from mounts.HOLES)."""
    if plate == "plate_mid":
        return [_slot((0, 82.5), 10.5, 7.6), _slot((0, 40.5), 10.5, 7.6),
                _rounded_polygon(((0, 111.5), (4.8, 103), (0, 97), (-4.8, 103)), 1.5)]
    if plate == "plate_bottom":
        result = [_slot((0, y), 10.8, 7.6) for y in (-47.5, -65.5, -83.5)]
        quadrant = Wire([  # four of these leave a 3.6 mm cross under the stack
            Edge.make_line((1.8, 1.8, 0), (10, 1.8, 0)),
            Edge.make_three_point_arc((10, 1.8, 0), (4.6, 4.6, 0), (1.8, 10, 0)),
            Edge.make_line((1.8, 10, 0), (1.8, 1.8, 0)),
        ])
        return result + _paired(quadrant) + _paired(quadrant.mirror(Plane.XZ))
    result = []
    for y in (27.5, 7.5, -12.5, -30, -49.5, -69):  # diagonal weight-saving reliefs
        inner, outer, h = (5, 15, 16.5) if y > -20 else (3.4, 11.3, 14.0)
        result += _paired(_rounded_polygon(((inner, y + h / 2), (outer, y), (outer, y - h / 2), (inner, y)), 0.9))
    result += _paired(_rounded_polygon(((8, 72.5), (17.5, 70.5), (12, 63.5), (7.5, 66)), 1.1))
    result += _paired(_rounded_polygon(((10.5, 58.5), (16, 56), (16, 40), (10.5, 43)), 0.7))
    result.append(_slot((0, 55.5), 9.4, 10, 0.9))
    return result


def build_plate(name: str, holes: list[Hole]) -> Part:
    face = Face(_outer_face(name).outer_wire(), [*cutouts(name), *(_circle((h.x, h.y), h.d) for h in holes)])
    assert face.is_valid and face.area > 0, name
    part = extrude(face, amount=P.PLATE_T, dir=(0, 0, 1))
    part.label = name
    return part


# --- arm ------------------------------------------------------------------------
def _outline(length: float) -> Wire:
    """Root-hole midpoint at (0, 0), motor at (0, length). Handed two-finger root."""
    neck = length - P.NECK_LENGTH
    shaft, paddle, waist = P.SHAFT_WIDTH / 2, P.PADDLE_WIDTH / 2, P.WAIST_WIDTH / 2
    tip = length + P.TIP_EXTENSION
    lobe = P.TIP_EXTENSION * 0.28
    tip_half = P.PADDLE_WIDTH * 0.20
    cap = P.TIP_EXTENSION * 0.12

    def root(x, y):  # sibling ratios of a 38 x 31 traced root envelope
        return x / 38 * P.ROOT_WIDTH, y / 31 * P.ROOT_DEPTH

    left_root, right_root = root(-11, -10), root(11, -10)
    left = [
        Edge.make_bezier(left_root, root(-9, 20), (-shaft, neck - 30), (-shaft, neck)),
        Edge.make_bezier((-shaft, neck), (-shaft, length - 14), (-paddle, length - 11), (-paddle, length - lobe)),
        Edge.make_three_point_arc((-paddle, length - lobe), (-waist, length), (-paddle, length + lobe)),
        Edge.make_line((-paddle, length + lobe), (-tip_half, tip - cap)),
    ]
    right = [e.mirror(Plane.YZ) for e in reversed(left)]
    cap_arc = Edge.make_three_point_arc((-tip_half, tip - cap), (0, tip), (tip_half, tip - cap))
    root_edges = [
        Edge.make_bezier(right_root, root(12, -15), root(16, -18), root(19, -20)),
        Edge.make_three_point_arc(root(19, -20), root(19, -21.5), root(17, -22.5)),
        Edge.make_bezier(root(17, -22.5), root(15, -23.5), root(14, -21.5), root(12, -23.5)),
        Edge.make_three_point_arc(root(12, -23.5), root(11, -25), root(12, -27)),
        Edge.make_bezier(root(12, -27), root(11, -29), root(9, -31), root(7.5, -30)),
        Edge.make_bezier(root(7.5, -30), root(6, -29), root(4, -23), root(2.5, -21)),
        Edge.make_line(root(2.5, -21), root(1.7, -16.5)),
        Edge.make_three_point_arc(root(1.7, -16.5), root(1, -15.8), root(0.3, -16.5)),
        Edge.make_bezier(root(0.3, -16.5), root(1, -20), root(-1.5, -24), root(-3.5, -29)),
        Edge.make_bezier(root(-3.5, -29), root(-5, -33), root(-7, -30), root(-9.5, -28)),
        Edge.make_three_point_arc(root(-9.5, -28), root(-10.5, -26.5), root(-10, -25)),
        Edge.make_bezier(root(-10, -25), root(-9, -22.5), root(-12, -22), root(-14, -23.5)),
        Edge.make_bezier(root(-14, -23.5), root(-16, -23), root(-18, -21), root(-19, -20)),
        Edge.make_bezier(root(-19, -20), root(-19.5, -19), root(-12, -16), left_root),
    ]
    return Wire([*left, cap_arc, *right, *root_edges])


def motor_bolts(length: float) -> list[XY]:
    r = P.MOTOR_BOLT_CIRCLE / 2
    return [(r * cos(radians(45 + 90 * i)), length + r * sin(radians(45 + 90 * i))) for i in range(4)]


def arm_holes(length: float) -> list[Wire]:
    holes = [_circle(c, P.D_M3) for c in P.root_holes()]
    holes += [_circle(c, P.D_M3) for c in motor_bolts(length)]
    holes.append(_circle((0, length), P.D_MOTOR_BORE))
    cy, hw, hh = length + P.DIAMOND_OFFSET, P.DIAMOND_W / 2, P.DIAMOND_H / 2
    holes.append(_rounded_polygon(((0, cy + hh), (hw, cy), (0, cy - hh), (-hw, cy)), P.DIAMOND_FILLET))
    return holes


def build_arm(length: float = P.ROOT_TO_MOTOR, relief: bool = True) -> Part:
    """Arm-local, Z 0..ARM_T. The stack bolt relief is cut after extrusion because
    it overlaps the root notch of the outer wire (keyhole)."""
    face = Face(_outline(length), arm_holes(length))
    assert face.is_valid
    arm = extrude(face, amount=P.ARM_T, dir=(0, 0, 1))
    if relief:
        arm = arm - column(*P.STACK_NOTCH_XY, -1, P.ARM_T + 2, P.D_STACK_NOTCH / 2)
    arm.label = "arm"
    return arm


def build_standoff(height: float) -> Part:
    face = Face(Wire.make_circle(P.STANDOFF_OD / 2), [Wire.make_circle(P.STANDOFF_BORE / 2)])
    return extrude(face, amount=height, dir=(0, 0, 1))
