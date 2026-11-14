"""What every printed part of Vektor shares: the print rules, a few solids, and the checks.

Printed in TPU 95A unless a part says otherwise; holes and fits are modelled at the size that
comes out right on a 0.4 mm nozzle.
"""

from dataclasses import dataclass, field
from math import asin, cos, pi, radians, sin

from build123d import Axis, Edge, Face, Part, Plane, Pos, Vector, Wire, extrude

from vektor import gear as G
from vektor import geometry as GEO
from vektor import params as P
from vektor.checks import overlap

FIT = 0.2
WALL = 1.6
BORE = 5.3  # slides over a 5 mm standoff
SNAP = 5.1  # snaps onto one
SNAP_WALL = 1.8
SNAP_MOUTH = 3.9
D_M3 = 3.4
D_HEAD = 6.2
BED = 220.0
THIN = 0.9


@dataclass
class Accessory:
    name: str
    title: str
    part: Part
    bed: tuple = (0, 0, -1)  # outward normal of the face that lies on the bed
    qty: int = 1
    instances: tuple = ()
    material: str = "TPU 95A"
    color: str = "tpu"
    holds: tuple = ()
    bridges: float = 0.0  # mm2 the print may bridge
    overhang: float = 0.0  # mm2 it may overhang
    hardware: str = ""
    notes: str = ""
    in_assembly: bool = True
    checks: list = field(default_factory=list)


def prism(face, z0: float, z1: float) -> Part:
    return Pos(0, 0, z0) * extrude(face, amount=z1 - z0)


def prism_x(face, x0: float, x1: float) -> Part:
    """Profile drawn as (y, z), extruded along X."""
    return extrude(Plane(origin=(x0, 0, 0), x_dir=(0, 1, 0), z_dir=(1, 0, 0)) * face, amount=x1 - x0)


def prism_y(face, y0: float, y1: float) -> Part:
    """Profile drawn as (x, z), extruded along Y."""
    return extrude(Plane(origin=(0, y1, 0), x_dir=(1, 0, 0), z_dir=(0, -1, 0)) * face, amount=y1 - y0)


box, cyl, poly, disc = G.box, G.cyl, GEO.poly, GEO.disc


def snap_ring(c, mouth_deg: float, z0: float, z1: float) -> Part:
    """An open ring that snaps onto a standoff from the side its mouth faces."""
    r_in, r_out = SNAP / 2, SNAP / 2 + SNAP_WALL
    r_mid = (r_in + r_out) / 2
    half = asin((SNAP_MOUTH + SNAP_WALL) / (2 * r_mid))
    m = radians(mouth_deg)

    def arc(center, r, a0, sweep):
        pts = [Vector(center[0] + r * cos(a0 + sweep * k), center[1] + r * sin(a0 + sweep * k), 0) for k in (0, 0.5, 1)]
        return Edge.make_three_point_arc(*pts)

    lip0 = (c[0] + r_mid * cos(m + half), c[1] + r_mid * sin(m + half))
    lip1 = (c[0] + r_mid * cos(m - half), c[1] + r_mid * sin(m - half))
    sweep = 2 * pi - 2 * half
    w = Wire(
        [
            arc(c, r_out, m + half, sweep),
            arc(lip1, SNAP_WALL / 2, m - half, pi),
            arc(c, r_in, m - half, -sweep),
            arc(lip0, SNAP_WALL / 2, m + half + pi, pi),
        ]
    )
    return prism(Face(w), z0, z1)


def mirror_x(part: Part) -> Part:
    return part.mirror(Plane.YZ)


def lay_on_bed(part: Part, bed) -> Part:
    n, down = Vector(*bed).normalized(), Vector(0, 0, -1)
    axis = n.cross(down)
    if axis.length > 1e-9:
        out = part.rotate(Axis((0, 0, 0), axis), n.get_signed_angle(down, axis))
    elif n.Z > 0:
        out = part.rotate(Axis.X, 180)
    else:
        out = part.moved(Pos(0, 0, 0))
    bb = out.bounding_box()
    return out.translate(Vector(-(bb.min.X + bb.max.X) / 2, -(bb.min.Y + bb.max.Y) / 2, -bb.min.Z))


def obstacles() -> dict:
    out = {n: p for n, (p, _c, _o) in G.build().items() if not n.startswith(("prop_", "camera"))}
    out["camera"] = G.camera_sweep()
    for q, xy in P.MOTORS.items():
        out[f"prop_{q}"] = G.keepout(xy)
    return out


_OBST = None


def check(acc: Accessory) -> list:
    from vektor import printcheck as PC

    global _OBST
    if _OBST is None:
        _OBST = obstacles()
    rows = []
    part = acc.part
    n = len(part.solids())
    rows.append(("one valid solid", n == 1 and part.is_valid, f"{n} solid(s), {part.volume / 1000:.2f} cm3"))
    placed = (part, *acc.instances)
    hits = {k: round(v, 2) for p in placed for k, f in GEO.parts().items() if (v := overlap(p, f)) > 1e-3}
    rows.append(("does not cut into the frame", not hits, str(hits or "clear")))
    hits = {
        k: round(v, 2)
        for p in placed
        for k, o in _OBST.items()
        if not k.startswith(acc.holds) and (v := overlap(p, o)) > 1e-3
    }
    rows.append(("clear of electronics, motors and prop discs", not hits, str(hits or "clear")))
    bedded = lay_on_bed(part, acc.bed)
    bb = bedded.bounding_box()
    contact = sum(
        f.area
        for f in bedded.faces()
        if f.geom_type.name == "PLANE" and abs(f.center().Z) < 1e-4 and f.normal_at().Z < -0.999
    )
    rows.append(("lies on a flat face", contact >= 20.0, f"{contact:.0f} mm2 on the bed"))
    rows.append(
        (
            f"fits a {BED:g} mm bed",
            max(bb.size.X, bb.size.Y) <= BED,
            f"{bb.size.X:.0f} x {bb.size.Y:.0f} x {bb.size.Z:.0f} mm",
        )
    )
    br, ov = PC.down_faces(bedded)
    rows.append(
        (
            "prints without support",
            br <= acc.bridges + 3 and ov <= acc.overhang + 3,
            f"{br:.0f} mm2 bridged (allowed {acc.bridges:.0f}), {ov:.0f} mm2 overhanging (allowed {acc.overhang:.0f})",
        )
    )
    share = PC.thinnest(part, THIN)
    rows.append((f"no walls under {THIN} mm", share <= 0.02, f"{share:.1%} of the surface"))
    return rows + list(acc.checks)
