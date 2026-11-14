"""Print rules and building blocks shared by every TPU accessory.

Everything is modelled in frame coordinates, installed. `Accessory.bed` names the face that
goes on the print bed; the exporter turns the part over, nothing else changes.

Fits assume TPU 95A on a 0.4 mm nozzle. Printed TPU holes come out about 0.2 mm tight,
so the numbers below are the modelled sizes that give the intended fit.
"""

from dataclasses import dataclass, field
from math import asin, cos, pi, radians, sin, sqrt

from build123d import Axis, Face, Part, Plane, Pos, Vector, Wire, extrude

from zhalo import params as P
from zhalo.equipment import box, cylinder
from zhalo.outline import XY, _arc, belt, circle, face, lobe, polygon, rounded_poly, scallop

Row = tuple[str, bool, str]

MATERIAL = "TPU 95A"
WALL = 1.6  # four 0.4 mm perimeters: the thinnest wall used anywhere
FIT = 0.2  # gap per side round a rigid part that must slide in
SLEEVE_BORE = 5.3  # slides over a 5 mm standoff during assembly
SLEEVE_OD = 9.0
CLIP_BORE = 5.1  # snaps onto a 5 mm standoff of the finished frame
CLIP_WALL = 1.8
CLIP_MOUTH = 3.9  # the standoff has to push 1.1 mm of TPU aside to get in
D_M3_FREE = 3.4
D_M3_HEAD = 6.2  # recess for a button or socket head
D_M2_FREE = 2.3
M3_NUT_AF, M3_NUT_H = 5.7, 2.6
M5_NUT_AF, M5_NUT_H = 8.2, 4.2
PANEL_BAND = 8.0  # top of the front and rear standoffs, kept free for the side-panel clips
SLEEVE_TOP = P.Z_TOP - PANEL_BAND - 0.2  # sleeves on those standoffs stop here
SEAT = 0.15  # clearance to the plate above or below a part that sits between two plates
BED = 180.0  # smallest printer bed the parts are checked against


@dataclass
class Accessory:
    name: str  # file stem
    title: str
    part: Part  # installed, frame coordinates
    bed: tuple[float, float, float] = (0, 0, -1)  # outward normal of the face that lies on the bed
    qty: int = 1
    hardware: str = ""
    notes: str = ""
    holds: tuple[str, ...] = ()  # equipment this part is meant to touch
    ceilings: float = 0.0  # mm2 of flat bridge the print is allowed (window tops and the like)
    overhang: float = 0.0  # mm2 of sloped overhang the print is allowed
    in_assembly: bool = True  # False for a variant that shares its place with another part
    instances: tuple = ()  # the other installed copies of the same print (qty > 1), for the assembly
    color: str = "tpu"  # colour key for renders and the FreeCAD document
    material: str = MATERIAL  # a rigid part (a camera turret) names its own
    checks: list[Row] = field(default_factory=list)
    module: str = ""


# --- solids ---------------------------------------------------------------------------------
def prism(profile: Face, z0: float, z1: float) -> Part:
    """XY profile extruded from z0 to z1."""
    return Pos(0, 0, z0) * extrude(profile, amount=z1 - z0, dir=(0, 0, 1))


def prism_x(profile: Face, x0: float, x1: float) -> Part:
    """Profile drawn as (y, z) and extruded along X from x0 to x1."""
    return extrude(Plane(origin=(x0, 0, 0), x_dir=(0, 1, 0), z_dir=(1, 0, 0)) * profile, amount=x1 - x0, dir=(1, 0, 0))


def prism_y(profile: Face, y0: float, y1: float) -> Part:
    """Profile drawn as (x, z) and extruded along Y from y0 to y1."""
    return extrude(
        Plane(origin=(0, y1, 0), x_dir=(1, 0, 0), z_dir=(0, -1, 0)) * profile, amount=y1 - y0, dir=(0, -1, 0)
    )


def poly(points: list[XY], r: float = 0.0) -> Face:
    """Polygon as a face; r > 0 rounds every corner."""
    return face(rounded_poly(points, r) if r > 0 else polygon(points))


def disc(p: XY, d: float) -> Face:
    return face(circle(p, d))


def hull(circles: list[tuple[XY, float]]) -> Face:
    """Belt round circles given counter-clockwise as ((x, y), radius)."""
    return face(belt([lobe(c, r) for c, r in circles]))


def tube(xy: XY, z0: float, z1: float, od: float, bore: float) -> Part:
    return cylinder(*xy, z0, z1, od) - cylinder(*xy, z0 - 1, z1 + 1, bore)


def hexagon(center: XY, af: float, flat_top: bool = True) -> Face:
    """Regular hexagon by its across-flats size; flat_top puts two flats square to the second axis."""
    rc = af / sqrt(3)
    start = 0.0 if flat_top else 30.0
    return poly(
        [
            (center[0] + rc * cos(radians(start + 60 * k)), center[1] + rc * sin(radians(start + 60 * k)))
            for k in range(6)
        ],
        0.35,
    )


def honeycomb(x0: float, x1: float, y0: float, y1: float, af: float, rib: float, origin: XY = (0.0, 0.0)) -> list[XY]:
    """Centres of a staggered flat-top hex grid whose cells lie wholly inside the rectangle."""
    pitch_y = af + rib
    pitch_x = pitch_y * sqrt(3) / 2
    half_w = af / sqrt(3)
    out = []
    kmax = int((x1 - x0) / pitch_x) + 2
    jmax = int((y1 - y0) / pitch_y) + 2
    for k in range(-kmax, kmax + 1):
        cx = origin[0] + k * pitch_x
        for j in range(-jmax, jmax + 1):
            cy = origin[1] + j * pitch_y + (pitch_y / 2 if k % 2 else 0.0)
            if cx - half_w >= x0 and cx + half_w <= x1 and cy - af / 2 >= y0 and cy + af / 2 <= y1:
                out.append((cx, cy))
    return out


def hex_pocket(xy: XY, z0: float, z1: float, af: float, flat_x: bool = True) -> Part:
    """Nut pocket: hexagonal hole between z0 and z1."""
    return prism(hexagon(xy, af, flat_top=flat_x), z0, z1)


def mirror_x(part: Part) -> Part:
    return part.mirror(Plane.YZ)


def c_ring(
    center: XY, mouth_deg: float, wall: float = CLIP_WALL, bore: float = CLIP_BORE, mouth: float = CLIP_MOUTH
) -> Face:
    """Plan view of a snap ring: an open annulus whose two lips are full rounds, mouth facing mouth_deg."""
    r_in, r_out = bore / 2, bore / 2 + wall
    r_mid = (r_in + r_out) / 2
    half = asin((mouth + wall) / (2 * r_mid))  # half the opening, seen from the centre
    m = radians(mouth_deg)
    lip0 = (center[0] + r_mid * cos(m + half), center[1] + r_mid * sin(m + half))
    lip1 = (center[0] + r_mid * cos(m - half), center[1] + r_mid * sin(m - half))
    sweep = 2 * pi - 2 * half
    # outer arc, a half round over the first lip, inner arc back, a half round over the second lip
    edges = [
        _arc(center, r_out, m + half, sweep),
        _arc(lip1, wall / 2, m - half, pi),
        _arc(center, r_in, m - half, -sweep),
        _arc(lip0, wall / 2, m + half + pi, pi),
    ]
    return face(Wire(edges))


def ring_area(d_out: float, d_in: float) -> float:
    return pi * (d_out**2 - d_in**2) / 4


def lay_on_bed(part: Part, bed: tuple[float, float, float]) -> Part:
    """Copy of the part turned so that `bed` points down, resting on Z = 0, centred in XY."""
    n, down = Vector(*bed).normalized(), Vector(0, 0, -1)
    axis = n.cross(down)
    if axis.length > 1e-9:
        out = part.rotate(Axis((0, 0, 0), axis), n.get_signed_angle(down, axis))
    elif n.Z > 0:
        out = part.rotate(Axis.X, 180)
    else:
        out = part.moved(Pos(0, 0, 0))
    bb = out.bounding_box()
    out = out.translate(Vector(-(bb.min.X + bb.max.X) / 2, -(bb.min.Y + bb.max.Y) / 2, -bb.min.Z))
    out.label = part.label
    return out


__all__ = [name for name in dir() if not name.startswith("_")]
_ = (box, cylinder, P, scallop)  # re-exported for the accessory modules
