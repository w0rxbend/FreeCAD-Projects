"""The carbon parts as flat profiles and as solids, and the assembled frame.

Every carbon part is a `Plate`: one face (outline with its holes and windows) and a thickness. The
same face goes to the DXF for the CNC shop and is extruded for the 3D model.

Shapes are built as unions and differences of plain polygons and circles, then rounded by offsetting
in and out, so every inside corner can be cut with a 2 mm router bit and every outside corner is soft.
"""

from dataclasses import dataclass
from functools import lru_cache
from math import cos, hypot, radians, sin

from build123d import Align, Circle, Cylinder, Kind, Part, Polygon, Pos, Rot, Sketch, extrude, offset

from vektor import params as P

MIN_Z = (Align.CENTER, Align.CENTER, Align.MIN)


@dataclass
class Plate:
    name: str
    face: Sketch
    thickness: float
    z: float
    count: int = 1

    def solid(self) -> Part:
        return extrude(self.face, amount=self.thickness)

    def placed(self) -> Part:
        return Pos(0, 0, self.z) * self.solid()


def poly(points) -> Sketch:
    """A polygon facing +Z: counter-clockwise whatever order the points come in, so that it fuses with circles."""
    pts = list(points)
    area2 = sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1], strict=True))
    return Polygon(*(pts if area2 > 0 else pts[::-1]), align=None)


def disc(xy, d: float) -> Sketch:
    return Pos(xy[0], xy[1]) * Circle(d / 2)


def soften(shape: Sketch, r: float) -> Sketch:
    """Round every corner: convex ones by shrinking and growing, concave ones by growing and shrinking."""
    s = offset(offset(shape, -r, kind=Kind.ARC), r, kind=Kind.ARC)
    return offset(offset(s, r, kind=Kind.ARC), -r, kind=Kind.ARC)


def mirror_x(points):
    return [(-x, y) for x, y in reversed(points)]


def whole(right_half):
    """A closed outline from its right half listed nose to tail (points on the centre line once)."""
    return right_half + mirror_x(right_half)[1:-1]


# --- arm planform --------------------------------------------------------------------------------
def arm_strip(quad: str, r1: float) -> Sketch:
    """The arm's planform from the centre to r1, tapering as params.half_width."""
    rs = [0.0, P.ROOT_R, P.NECK_R, r1]
    left = [P.on_arm(quad, r, P.half_width(r)) for r in rs]
    right = [P.on_arm(quad, r, -P.half_width(r)) for r in reversed(rs)]
    return poly(left + right)


def truss_windows(quad: str) -> list[Sketch]:
    """Triangular windows between the spacer stations: one diagonal per bay, alternating, a Warren truss."""
    out = []
    stations = P.STATIONS
    for k, (a, b) in enumerate(zip(stations[:-1], stations[1:], strict=True)):
        a, b = a + P.STATION_RIB, b - P.STATION_RIB
        ha, hb = P.half_width(a) - P.CHORD, P.half_width(b) - P.CHORD
        top = [(a, ha), (b, hb)]
        bot = [(a, -ha), (b, -hb)]
        s = 1 if k % 2 == 0 else -1  # the diagonal runs from one chord to the other, alternately
        diag0, diag1 = (bot[0], top[1]) if s > 0 else (top[0], bot[1])
        tri1 = [top[0], top[1], bot[0]] if s > 0 else [bot[0], bot[1], top[0]]
        tri2 = [bot[0], bot[1], top[1]] if s > 0 else [top[0], top[1], bot[1]]
        for tri in (tri1, tri2):
            pts = [P.on_arm(quad, r, v) for r, v in tri]
            win = offset(poly(pts), -(P.DIAG + P.WINDOW_R), kind=Kind.INTERSECTION)
            if win.area > 4.0:
                out.append(offset(win, P.WINDOW_R, kind=Kind.ARC))
        _ = (diag0, diag1)
    return out


def motor_holes(quad: str, lower: bool) -> list[Sketch]:
    c = P.MOTORS[quad]
    if lower:
        return [disc(c, P.RING_HOLE)]
    out = [disc(c, P.MOTOR_BORE)]
    ux, uy = P.arm_dir(quad)
    for k in range(4):
        a = radians(45 + 90 * k) + radians(45)  # the screws sit square to the arm
        r0, r1 = P.MOTOR_PATTERNS[0] / 2 * 2**0.5, P.MOTOR_PATTERNS[1] / 2 * 2**0.5
        d = (cos(a) * ux - sin(a) * uy, cos(a) * uy + sin(a) * ux)
        p0 = (c[0] + r0 * d[0], c[1] + r0 * d[1])
        p1 = (c[0] + r1 * d[0], c[1] + r1 * d[1])
        out.append(slot(p0, p1, P.D_M3))
    return out


def slot(p0, p1, w: float) -> Sketch:
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    length = hypot(dx, dy)
    from math import atan2, degrees

    body = (
        Pos((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2)
        * Rot(0, 0, degrees(atan2(dy, dx)))
        * Polygon((-length / 2, -w / 2), (length / 2, -w / 2), (length / 2, w / 2), (-length / 2, w / 2), align=None)
    )
    return body + disc(p0, w) + disc(p1, w)


def station_points() -> list[tuple[float, float]]:
    return [P.on_arm(q, r) for q in P.QUADS for r in P.STATIONS]


def body_posts() -> list[tuple[float, float]]:
    return [(sx * x, y) for x, y in P.BODY_POSTS for sx in (1, -1)]


def stack_holes() -> list[tuple[float, float]]:
    h = P.STACK / 2
    return [(sx * h, sy * h) for sx in (1, -1) for sy in (1, -1)]


def square(c, pitch: float):
    h = pitch / 2
    return [(c[0] + sx * h, c[1] + sy * h) for sx in (1, -1) for sy in (1, -1)]


def _skin_outline(lower: bool) -> Sketch:
    shape = poly(whole(P.BODY))
    for q in P.QUADS:
        shape += arm_strip(q, P.ARM_R)
        shape += disc(P.MOTORS[q], 2 * (P.RING_R if lower else P.PAD_R))
    return soften(shape, P.BODY_ROUND)


def _bolt_holes() -> list[Sketch]:
    return [disc(p, P.D_M3) for p in body_posts() + stack_holes()]


# --- the webs ------------------------------------------------------------------------------------
def web_line(quad: str, side: int):
    """(start, end) of a web's middle plane in plan: straight, about WEB_INSET inside the arm's edge."""
    v = lambda r: side * (P.half_width(r) - P.WEB_INSET)  # noqa: E731
    k = (v(P.NECK_R) - v(P.ROOT_R)) / (P.NECK_R - P.ROOT_R)
    r0, r1 = P.WEB_R
    return P.on_arm(quad, r0, v(P.ROOT_R) + k * (r0 - P.ROOT_R)), P.on_arm(quad, r1, v(P.ROOT_R) + k * (r1 - P.ROOT_R))


def web_tabs(length: float) -> list[float]:
    """Middle of each tab along a web."""
    return [length * (k + 0.5) / P.TABS for k in range(P.TABS)]


def web_slots(quad: str) -> list[Sketch]:
    out = []
    for side in (1, -1):
        p0, p1 = web_line(quad, side)
        length = hypot(p1[0] - p0[0], p1[1] - p0[1])
        ux, uy = (p1[0] - p0[0]) / length, (p1[1] - p0[1]) / length
        # the cutter leaves round slot ends; the tab is square: lengthen the slot until its corners fit the round
        r = P.SLOT_W / 2
        h = P.TAB_L / 2 - (r * r - (P.T_WEB / 2) ** 2) ** 0.5 + 0.05
        for s_mid in web_tabs(length):
            c = (p0[0] + ux * s_mid, p0[1] + uy * s_mid)
            out.append(slot((c[0] - ux * h, c[1] - uy * h), (c[0] + ux * h, c[1] + uy * h), P.SLOT_W))
    return out


@lru_cache(maxsize=1)
def web() -> Plate:
    """One web, flat, as cut: x along it, y up (y = 0 the lower skin's top face). Eight of them."""
    p0, p1 = web_line("front_right", 1)
    length = hypot(p1[0] - p0[0], p1[1] - p0[1])
    body = soften(poly([(0, 0), (length, 0), (length, P.CAVITY), (0, P.CAVITY)]), 1.0)
    r = P.SLOT_W / 2  # the tabs are rounded like the slots the cutter leaves
    for s_mid in web_tabs(length):
        for y0, y1 in ((-P.T_SKIN, 0.5), (P.CAVITY - 0.5, P.CAVITY + P.T_SKIN)):
            tab = poly(
                [
                    (s_mid - P.TAB_L / 2, y0),
                    (s_mid + P.TAB_L / 2, y0),
                    (s_mid + P.TAB_L / 2, y1),
                    (s_mid - P.TAB_L / 2, y1),
                ]
            )
            body += offset(offset(tab, -r * 0.9, kind=Kind.ARC), r * 0.9, kind=Kind.ARC)
    return Plate("web", body, P.T_WEB, 0.0, count=8)


def placed_web(quad: str, side: int) -> Part:
    from math import atan2, degrees

    from build123d import Axis

    p0, p1 = web_line(quad, side)
    ang = degrees(atan2(p1[1] - p0[1], p1[0] - p0[0]))
    solid = web().solid().translate((0, 0, -P.T_WEB / 2))  # thickness centred on the middle plane
    stood = solid.rotate(Axis.X, 90)  # the web's y becomes z
    return Pos(p0[0], p0[1], P.Z_LOWER + P.T_SKIN) * stood.rotate(Axis.Z, ang)


@lru_cache(maxsize=2)
def skin(lower: bool) -> Plate:
    shape = _skin_outline(lower)
    for q in P.QUADS:
        for w in truss_windows(q):
            shape -= w
        for w in web_slots(q):
            shape -= w
        for h in motor_holes(q, lower):
            shape -= h
        if not lower:  # the motor wires come up out of the cavity next to the motor
            r, length, w = P.WIRE_SLOT
            shape -= slot(P.on_arm(q, r - length / 2), P.on_arm(q, r + length / 2), w)
    for h in _bolt_holes():
        shape -= h
    if lower:
        # the keel: hexagonal windows round the ESC, and under the VTX and receiver bays
        shape -= soften(poly([(-9, -9), (9, -9), (9, 9), (-9, 9)]), 3.0)
        for y in (-52.0, 52.0):
            shape -= hexagon((0.0, y), 18.0)
        for y in (-84.0, 84.0):
            shape -= hexagon((0.0, y), 10.0)
    else:
        shape -= soften(poly([(-11, -6), (11, -6), (11, 6), (-11, 6)]), 3.0)  # FC to ESC wiring
        for p in square((0.0, P.VTX_Y), 20.0) + square((0.0, P.VTX_Y), 30.5):
            shape -= disc(p, P.D_M3)
        for p in square((0.0, P.RX_Y), 20.0):
            shape -= disc(p, 2.2)
        for y in (30.0, 56.0):
            shape -= hexagon((0.0, y), 12.0)
    name = "skin_lower" if lower else "skin_upper"
    return Plate(name, shape, P.T_SKIN, P.Z_LOWER if lower else P.Z_UPPER)


def hexagon(c, across_flats: float) -> Sketch:
    r = across_flats / 3**0.5
    pts = [(c[0] + r * cos(radians(60 * k)), c[1] + r * sin(radians(60 * k))) for k in range(6)]
    return soften(poly(pts), 1.2)


@lru_cache(maxsize=1)
def top_plate() -> Plate:
    shape = soften(poly(whole(P.TOP)), 4.0)
    for x, y in body_posts():
        shape += disc((x, y), 11.0)
    shape = soften(shape, 2.0)
    for p in body_posts():
        shape -= disc(p, P.D_M3)
    # strap slots and a spine of hex windows, the battery's footprint stays mostly solid
    for sx in (1, -1):
        for sy in (1, -1):
            shape -= slot((sx * 15.0, sy * 14.0), (sx * 15.0, sy * 34.0), 3.6)
    for y in (-60.0, -45.0, 45.0, 60.0):
        shape -= hexagon((0.0, y), 10.0)
    for x, y in GOPRO_HOLES:
        shape -= disc((x, y), P.D_M3)
    return Plate("plate_top", shape, P.T_TOP, P.Z_TOP)


GOPRO_HOLES = [(sx * 9.0, y) for y in (62.0, 76.0) for sx in (1, -1)]


def spacer(height: float, d: float) -> Part:
    return Cylinder(d / 2, height, align=MIN_Z) - Pos(0, 0, -1) * Cylinder(1.25, height + 2, align=MIN_Z)


@lru_cache(maxsize=1)
def build() -> dict[str, tuple[Part, str]]:
    """Every solid of the frame in place: name -> (part, material)."""
    out = {}
    for plate in (skin(True), skin(False), top_plate()):
        out[plate.name] = (plate.placed(), "carbon")
    for q in P.QUADS:
        for side, tag in ((1, "left"), (-1, "right")):
            out[f"web_{q}_{tag}"] = (placed_web(q, side), "carbon")
    for i, (x, y) in enumerate(body_posts()):
        out[f"spacer_{i}"] = (Pos(x, y, P.Z_LOWER + P.T_SKIN) * spacer(P.CAVITY, P.SPACER_D), "aluminium")
    for i, (x, y) in enumerate(body_posts()):
        out[f"standoff_{i}"] = (Pos(x, y, P.Z_DECK) * spacer(P.BAY, P.STANDOFF_D), "aluminium")
    for name, (part, _m) in out.items():
        part.label = name
    return out


def parts() -> dict[str, Part]:
    return {n: p for n, (p, _m) in build().items()}


PLATES = {"skin_lower": lambda: skin(True), "skin_upper": lambda: skin(False), "plate_top": top_plate, "web": web}
