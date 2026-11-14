"""The carbon parts as flat profiles and solids, and the assembled frame.

Each carbon part is a `Plate`: one face (outline, holes, windows) and a thickness. The same face goes
to the DXF and is extruded for the model. Outlines are unions and differences of polygons and circles,
rounded by offsetting in and out, so every inside corner suits a 2 mm cutter.
"""

from dataclasses import dataclass
from functools import lru_cache

from build123d import Align, Circle, Cylinder, Kind, Part, Polygon, Pos, Sketch, extrude, offset

from bolid import params as P

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
    """A polygon facing +Z whatever order its points come in, so that it fuses with circles."""
    pts = list(points)
    area2 = sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1], strict=True))
    return Polygon(*(pts if area2 > 0 else pts[::-1]), align=None)


def disc(xy, d: float) -> Sketch:
    return Pos(xy[0], xy[1]) * Circle(d / 2)


def soften(shape: Sketch, r: float) -> Sketch:
    s = offset(offset(shape, -r, kind=Kind.ARC), r, kind=Kind.ARC)
    return offset(offset(s, r, kind=Kind.ARC), -r, kind=Kind.ARC)


def whole(right_half):
    """A closed outline from its right half, nose to tail, centre-line points listed once."""
    return right_half + [(-x, y) for x, y in reversed(right_half)][1:-1]


def rect(x0, y0, x1, y1) -> Sketch:
    return poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])


def slot(p0, p1, w: float) -> Sketch:
    (x0, y0), (x1, y1) = p0, p1
    dx, dy = x1 - x0, y1 - y0
    n = (dx * dx + dy * dy) ** 0.5
    nx, ny = -dy / n * w / 2, dx / n * w / 2
    return (
        poly([(x0 + nx, y0 + ny), (x1 + nx, y1 + ny), (x1 - nx, y1 - ny), (x0 - nx, y0 - ny)])
        + disc(p0, w)
        + disc(p1, w)
    )


# --- outlines ------------------------------------------------------------------------------------
@lru_cache
def clamp_outline() -> Sketch:
    return soften(poly(whole(P.CLAMP)), P.BODY_ROUND)


@lru_cache
def body_outline() -> Sketch:
    return soften(poly(whole(P.CLAMP[:-1] + P.TAIL)), P.BODY_ROUND)


def strip(quad: str, u0: float, u1: float, step: float = 4.0) -> Sketch:
    """The arm's planform from u0 to u1, following params.arm_width."""
    us = [u0]
    while us[-1] + step < u1:
        us.append(us[-1] + step)
    us.append(u1)
    for knee in (P.U_CLAMP, P.U_TAPER_END):
        if u0 < knee < u1 and knee not in us:
            us.append(knee)
    us.sort()
    left = [P.on_arm(quad, u, P.arm_width(u) / 2) for u in us]
    right = [P.on_arm(quad, u, -P.arm_width(u) / 2) for u in reversed(us)]
    return poly(left + right)


def quadrant(quad: str) -> Sketch:
    sx, sy = P.sign(quad)
    g, big = P.ROOT_GAP, 200.0
    return rect(min(sx * g, sx * big), min(sy * g, sy * big), max(sx * g, sx * big), max(sy * g, sy * big))


# --- holes ---------------------------------------------------------------------------------------
def stack_holes() -> list[tuple[float, float]]:
    return [(sx * s / 2, sy * s / 2) for s in P.STACK for sx in (1, -1) for sy in (1, -1)]


def arm_bolts() -> list[tuple[float, float]]:
    return [P.on_arm(q, P.U_BOLT) for q in P.QUADS]


def clamp_bolts() -> list[tuple[float, float]]:
    """Every bolt through bottom plate, arm and press plate."""
    return stack_holes() + list(P.STANDOFFS) + arm_bolts() + list(P.SPLITTER_HOLES)


def motor_holes(quad: str) -> list[Sketch]:
    mx, my = P.MOTORS[quad]
    h = P.MOTOR_HOLES / 2
    out = [disc((mx, my), P.MOTOR_BORE)]
    for a in (1, -1):
        for b in (1, -1):
            out.append(disc(P.on_arm(quad, P.U_MOTOR + a * h, b * h), P.D_M3))
    return out


def in_quad(quad: str, xy) -> bool:
    sx, sy = P.sign(quad)
    return sx * xy[0] > 0 and sy * xy[1] > 0


# --- plates --------------------------------------------------------------------------------------
def root_windows(quad: str) -> list[Sketch]:
    """Windows in the clamped root, where the plates carry the bending: everything 2.4 mm clear of a bolt
    hole, 3 mm in from the edges, and off the arm's own centre band, which takes the crash loads in."""
    region = offset(clamp_outline() & quadrant(quad), -3.0, kind=Kind.INTERSECTION)
    for xy in clamp_bolts():
        region -= disc(xy, P.D_M3 + 2 * 2.4)
    region -= strip(quad, 0.0, P.U_CLAMP) & quadrant(quad)  # the arm's own 20 mm band stays solid
    out = []
    for f in region.faces():
        if f.area < 25.0:
            continue
        try:
            w = soften(Sketch() + f, 1.2)
        except Exception:  # noqa: BLE001 - a sliver too thin to round: leave the carbon in
            continue
        if w.area > 15.0:
            out.append(w)
    return out


@lru_cache
def arm(quad: str) -> Plate:
    root = clamp_outline() & quadrant(quad)
    face = root + (strip(quad, 0.0, P.U_MOTOR) & quadrant(quad)) + disc(P.MOTORS[quad], P.PAD_D)
    face = soften(face, 1.5)
    for xy in clamp_bolts():
        if in_quad(quad, xy):
            face -= disc(xy, P.D_M3)
    for h in motor_holes(quad):
        face -= h
    for w in root_windows(quad):
        face -= w
    return Plate(f"arm_{quad}", face, P.T_ARM, P.Z_ARM)


def _with_arm_roots(outline: Sketch) -> Sketch:
    for q in P.QUADS:
        outline += strip(q, 0.0, P.U_CLAMP) + disc(P.on_arm(q, P.U_CLAMP), P.W_CLAMP)
    return soften(outline, 3.0)


@lru_cache
def bottom_plate() -> Plate:
    face = _with_arm_roots(body_outline())
    for xy in clamp_bolts():
        face -= disc(xy, P.D_M3)
    v = P.VTX_HOLES / 2
    for sx in (1, -1):
        for sy in (1, -1):
            face -= disc((sx * v, P.VTX_Y + sy * v), P.D_M2)
    for xy in P.COVER_BOLTS:
        face -= disc(xy, P.D_M2)
    for xy in P.WING_FEET:
        face -= disc(xy, P.D_M3)
    face -= soften(rect(-7.0, P.VTX_Y - 6.0, 7.0, P.VTX_Y + 6.0), 2.5)  # under the VTX: air in
    return Plate("plate_bottom", face, P.T_BOT, P.Z_BOT)


@lru_cache
def press_plate() -> Plate:
    face = _with_arm_roots(clamp_outline())
    for xy in clamp_bolts():
        face -= disc(xy, P.D_M3)
    face -= soften(rect(-6.0, -6.0, 6.0, 6.0), 2.5)
    return Plate("plate_press", face, P.T_PRESS, P.Z_PRESS)


@lru_cache
def top_plate() -> Plate:
    face = poly(whole(P.TOP))
    for xy in P.STANDOFFS:
        face += disc(xy, P.D_M3 + 2 * 2.6)
    face = soften(face, 2.0)
    for xy in P.STANDOFFS:
        face -= disc(xy, P.D_M3)
    x, length, w = P.STRAP
    for sx in (1, -1):
        face -= slot((sx * x, P.STRAP_Y - length / 2), (sx * x, P.STRAP_Y + length / 2), w)
    for xy in P.GOPRO_HOLES:
        face -= disc(xy, P.D_M3)
    face -= slot((0.0, -30.0), (0.0, 10.0), 8.0)
    return Plate("plate_top", face, P.T_TOP, P.Z_TOP)


def standoff() -> Part:
    return Cylinder(P.STANDOFF_D / 2, P.BAY, align=MIN_Z) - Cylinder(1.25, P.BAY, align=MIN_Z)


def build() -> dict[str, tuple[Part, str]]:
    out = {}
    for plate in (bottom_plate(), *(arm(q) for q in P.QUADS), press_plate(), top_plate()):
        out[plate.name] = (plate.placed(), "carbon")
    for i, (x, y) in enumerate(P.STANDOFFS):
        out[f"standoff_{i}"] = (Pos(x, y, P.Z_BAY) * standoff(), "aluminium")
    for name, (part, _m) in out.items():
        part.label = name
    return out


def parts() -> dict[str, Part]:
    return {n: p for n, (p, _m) in build().items()}


def arm_kinds() -> dict[str, Plate]:
    """The arms come in two shapes (front and rear); each is cut twice, one of the pair flipped."""
    return {"arm_front": arm("front_right"), "arm_rear": arm("rear_right")}


PLATES = {
    "plate_bottom": bottom_plate,
    "arm_front": lambda: Plate("arm_front", arm("front_right").face, P.T_ARM, P.Z_ARM, 2),
    "arm_rear": lambda: Plate("arm_rear", arm("rear_right").face, P.T_ARM, P.Z_ARM, 2),
    "plate_press": press_plate,
    "plate_top": top_plate,
}
