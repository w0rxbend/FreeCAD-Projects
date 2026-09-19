"""Snap-on TPU edge guard sleeve for the free arm shaft (all four arms, one symmetric part)."""

from copy import deepcopy
from math import radians, tan

from build123d import (Edge, Face, GeomType, Part, Plane, Polygon, Pos, Rectangle, Vertex, Wire, extrude,
                       offset)

from tigerbee import profiles
from tigerbee.accessories._common import *  # noqa: F401,F403 - constants, builders and checks

NAME = "arm_sleeve"
TITLE = "Arm shaft edge guard sleeve"
MATERIAL = "TPU95A"
PRINT = {f"arm_sleeve_{a}": (0, 0, -1) for a in ("front_left", "front_right", "rear_left", "rear_right")}
EXCLUSIVE = ()
NOTES = ("U-sleeve pushed onto the carbon shaft from below over arm-local y 40-84; held by 0.15 mm/side "
         "interference plus three 0.3 mm ribs per wall. Walls end flush with the arm top face (frame Z 7) "
         "so nothing enters a prop disc; 0.8 mm gap to the motor_guard face at arm-local y 84.8.")

# --- parameters (mm, arm-local: root-hole midpoint at (0, 0), motor at (0, L), carbon Z 0..5) ---
Y0, Y1 = 40.0, 84.0  # sleeve extent along the shaft (84.8 = motor_guard face)
INTERFERENCE = 0.15  # pocket = arm outline offset by -INTERFERENCE: the walls squeeze the shaft
WALL = 2.0  # wall thickness outboard of the nominal outline
FLOOR = 1.6  # floor under the carbon (local Z -FLOOR..0)
CARBON_T = 5.0  # arm thickness: the walls end exactly flush with its top face
CHAMFER_DEG = 30.0  # end ramps, measured from vertical (also keeps the print support-free)
RIBS = True
RIB_H = 0.3  # proud of the pocket face
RIB_L = 3.0  # along the shaft
RIB_T = 4.0  # tall
RIB_Y = (47.0, 62.0, 77.0)
RIB_Z0 = (CARBON_T - RIB_T) / 2  # 0.5: rib centred in the carbon thickness
FACET = 2.0  # chord length of the faceted min_wall twin (OCCT cannot offset the curved side faces)

_ARM_NAMES = ("front_left", "front_right", "rear_left", "rear_right")


def _rebuild(wire: Wire, facet: float) -> Wire:
    """Curved edges as BSplines (facet = 0) or as chords `facet` long: OCCT refuses to 3D-offset
    the OFFSET curves that offset() produces, and min_wall() needs a faceted (planar) twin."""
    edges = []
    for e in wire.edges():
        if e.geom_type == GeomType.LINE:
            edges.append(e)
        elif facet:
            pts = [e.position_at(i / max(2, int(e.length / facet))) for i in range(max(2, int(e.length / facet)) + 1)]
            edges += [Edge.make_line(a, b) for a, b in zip(pts, pts[1:])]
        else:
            n = max(8, int(2 * e.length))
            edges.append(Edge.make_spline([e.position_at(i / n) for i in range(n + 1)]))
    return Wire(edges)


def _offset2d(face: Face, amount: float, facet: float = 0.0) -> Face:
    off = offset(face, amount).face()
    return Face(_rebuild(off.outer_wire(), facet), [_rebuild(w, facet) for w in off.inner_wires()])


def _crop(sketch, y0: float, y1: float):
    return sketch & (Pos(0, (y0 + y1) / 2) * Rectangle(120, y1 - y0))


def _slab(sketch, z0: float, z1: float) -> Part:
    """Extrude a Z=0 sketch to Z z0..z1 (offset() can hand back reversed faces, hence the explicit dir)."""
    return Pos(0, 0, z0) * extrude(sketch, amount=z1 - z0, dir=(0, 0, 1))


def _end_ramps(p: dict) -> Part:
    """Cutting wedges at both ends: material tapers inward going up at CHAMFER_DEG from vertical."""
    t = tan(radians(p["CHAMFER_DEG"]))
    z0, z1 = -p["FLOOR"] - 1.0, p["CARBON_T"] + 1.0
    tools = []
    for end, out in ((p["Y0"], -1.0), (p["Y1"], 1.0)):  # `out` points away from the sleeve
        def edge_y(z, end=end, out=out):  # the ramp passes through (end, -FLOOR) and leans inboard
            return end - out * t * (z + p["FLOOR"])
        far = end + out * 60.0
        tri = Polygon((edge_y(z0), z0), (edge_y(z1), z1), (far, z1), (far, z0), align=None)
        tools.append(extrude(Plane(origin=(0, 0, 0), x_dir=(0, 1, 0), z_dir=(1, 0, 0)) * tri, amount=60, both=True))
    return tools[0] + tools[1]


def _sleeve(p: dict, facet: float = 0.0) -> Part:
    outline = Face(profiles._outline(P.ROOT_TO_MOTOR))
    y0, y1 = p["Y0"], p["Y1"]
    outer = _crop(_offset2d(outline, p["WALL"], facet), y0, y1)
    pocket = _crop(_offset2d(outline, -p["INTERFERENCE"], facet), y0, y1)
    walls = outer - pocket

    part = _slab(outer, -p["FLOOR"], 0.0)  # floor under the carbon
    part += _slab(walls, -p["FLOOR"], p["CARBON_T"])  # walls, flush with the arm top face

    if p["RIBS"]:
        rib_inner = _crop(_offset2d(outline, -(p["INTERFERENCE"] + p["RIB_H"]), facet), y0, y1)
        for y in p["RIB_Y"]:
            band = _crop(pocket - rib_inner, y - p["RIB_L"] / 2, y + p["RIB_L"] / 2)
            part += _slab(band, p["RIB_Z0"], p["RIB_Z0"] + p["RIB_T"])

    if p["CHAMFER_DEG"] > 0:
        part -= _end_ramps(p)
    assert len(part.solids()) == 1, f"arm_sleeve: {len(part.solids())} solids"
    return part


def _wall_gauge(p: dict) -> float:
    """Measured wall band thickness: min distance from the pocket boundary to the outer boundary
    over the gripping length (the walls are two parallel offsets of the same curve, nominally
    WALL + INTERFERENCE apart)."""
    outline = Face(profiles._outline(P.ROOT_TO_MOTOR))
    inner = _offset2d(outline, -p["INTERFERENCE"]).outer_wire()
    outer = _offset2d(outline, p["WALL"]).outer_wire()
    n = 800
    pts = [inner.position_at(i / n) for i in range(n)]
    return min(Vertex(q.X, q.Y, q.Z).distance_to(outer) for q in pts if p["Y0"] + 0.5 <= q.Y <= p["Y1"] - 0.5)


def _guard_probe(p: dict) -> Part:
    """Stand-in for the motor_guard outer skin (outline + 2.25, arm-local y >= L - 30, Z -2..4.8)."""
    outline = Face(profiles._outline(P.ROOT_TO_MOTOR))
    skin = _crop(_offset2d(outline, 2.25), P.ROOT_TO_MOTOR - 30.0, P.ROOT_TO_MOTOR + 30.0)
    return _slab(skin, -2.0, 4.8)


def _params(overrides: dict) -> dict:
    p = dict(Y0=Y0, Y1=Y1, INTERFERENCE=INTERFERENCE, WALL=WALL, FLOOR=FLOOR, CARBON_T=CARBON_T,
             CHAMFER_DEG=CHAMFER_DEG, RIBS=RIBS, RIB_H=RIB_H, RIB_L=RIB_L, RIB_T=RIB_T, RIB_Y=RIB_Y,
             RIB_Z0=RIB_Z0)
    p.update(overrides)
    return p


def build(**overrides) -> dict[str, Part]:
    p = _params(overrides)
    local = _sleeve(p)
    return {f"arm_sleeve_{a}": place_arm(deepcopy(local), P.ARM_PLACEMENTS[f"arm_{a}"]) for a in _ARM_NAMES}


def _intended_overlap(p: dict) -> float:
    """Press fit on its own arm: 2 x INTERFERENCE x CARBON_T x (Y1 - Y0) plus the ribs."""
    v = 2 * p["INTERFERENCE"] * p["CARBON_T"] * (p["Y1"] - p["Y0"])
    if p["RIBS"]:
        v += 2 * len(p["RIB_Y"]) * p["RIB_H"] * p["RIB_L"] * p["RIB_T"]
    return v


# the generic frame-interference check tolerates exactly the band that checks() also enforces
ALLOWED_INTERFERENCE = {f"arm_sleeve_{a}": {f"arm_{a}": 1.2 * _intended_overlap(_params({}))}
                        for a in _ARM_NAMES}


def checks(parts: dict[str, Part], frame: dict[str, Part]) -> list[tuple[str, bool, str]]:
    p = _params({})
    target = _intended_overlap(p)
    guards = {a: place_arm(deepcopy(_guard_probe(p)), P.ARM_PLACEMENTS[f"arm_{a}"]) for a in _ARM_NAMES}
    # min_wall() erodes and dilates, which OCCT refuses on surfaces of extrusion and on features it
    # erodes away entirely; it runs on a faceted twin (curved walls as FACET-long chords, < 1 um
    # deviation on this taper) of the bare wall structure, with the 0.3 ribs and the 30 deg end
    # chamfers - the spec's allowances - left out. _wall_gauge() measures the band itself.
    twin = _sleeve({**p, "RIBS": False, "CHAMFER_DEG": 0.0}, FACET)
    gauge = _wall_gauge(p)
    out = []
    shapes = []
    for a in _ARM_NAMES:
        label, arm_name = f"arm_sleeve_{a}", f"arm_{a}"
        s, arm = parts[label], frame[arm_name]
        shapes.append(s)

        grip = isect(s, arm)
        out.append((f"{label}: press fit on {arm_name} within 20% of {target:.1f} mm³",
                    0.8 * target <= grip <= 1.2 * target, f"{grip:.1f} mm³ intended overlap"))
        out.append((f"{label}: seated on the shaft (touching {arm_name})", s.distance_to(arm) == 0.0,
                    f"distance {s.distance_to(arm):.3f}"))

        others = {n: q for n, q in frame.items() if n != arm_name}
        hits = interference(s, against=others)
        out.append((f"{label}: clear of every other frame part", not hits, f"overlaps {hits or 'none'}"))

        top = s.bounding_box().max.Z
        out.append((f"{label}: at or below the arm top face Z {Z_ARM_TOP}", top <= Z_ARM_TOP + 1e-6, f"max Z {top:.3f}"))

        disc = prop_disc_violation(s)
        out.append((f"{label}: outside the prop discs above Z {PROP_Z0}", disc < EPS, f"{disc:.3f} mm³"))

        gap = s.distance_to(guards[a])
        out.append((f"{label}: >= 0.5 mm clear of the motor_guard face", gap >= 0.5, f"{gap:.3f} mm"))

        over = overhangs(s, PRINT[label], material=MATERIAL)
        out.append((f"{label}: no unsupported overhangs", not over, "; ".join(over) or "none"))

        ok, _v, detail = min_wall(place_arm(deepcopy(twin), P.ARM_PLACEMENTS[arm_name]), 1.5)
        out.append((f"{label}: min wall >= 1.5 (ribs allowed)", ok and gauge >= 1.5 - 1e-6,
                    f"{detail}; wall band {gauge:.3f} mm, floor {p['FLOOR']} mm"))

    distinct = all(not a.wrapped.IsSame(b.wrapped) for i, a in enumerate(shapes) for b in shapes[i + 1:])
    out.append(("four distinct placed shapes", distinct and len(shapes) == 4, f"{len(shapes)} copies"))
    return out
