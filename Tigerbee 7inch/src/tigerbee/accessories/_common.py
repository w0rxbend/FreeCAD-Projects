"""Print/material constants, equipment envelopes and geometry helpers shared by every accessory.

`from tigerbee.accessories._common import *` also brings in everything from `_fit` (frame
constants, frame_parts(), interference(), coaxial(), seated(), prop_disc_violation(), ...).
All builders return Parts in FRAME coordinates unless the docstring says otherwise.
"""

from copy import deepcopy
from math import atan2, cos, degrees, radians, sin

from build123d import (Align, Axis, Box, Circle, Cylinder, GeomType, Location, Part, Plane, Polygon, Pos,
                       Rectangle, RegularPolygon, Sketch, Vector, extrude, fillet)

from tigerbee.accessories._fit import *  # noqa: F401,F403
from tigerbee.accessories._fit import (EPS, MIN_Z_ALIGN, STANDOFF_D, STANDOFF_FIT, box, cylinder, isect,
                                       prop_discs)
# The style vocabulary (STYLES, scale_features, the vent_* generators, mark(), suture(), the kits)
# rides in on the same `import *` every accessory already does, so a module never has to remember
# where the design language lives. It has ONE owner - import it, never fork a generator. The only
# names it shares with _fit/_common are the build123d and math re-exports, which are the same
# objects, so nothing here is shadowed.
from tigerbee.accessories._style import *  # noqa: F401,F403,E402

# --- materials and print rules ------------------------------------------------------------
MATERIALS = {
    "TPU95A": dict(wall=1.2, wall_impact=2.0, fit=0.25, m3_tap=2.7, m2_tap=1.7, snap=0.8, bridge_max=22.0, arch_d=10.0),
    "PETG": dict(wall=1.5, wall_impact=2.0, fit=0.30, m3_tap=2.5, m2_tap=1.7, snap=0.6, bridge_max=20.0, arch_d=12.0),
}
FIT = 0.25  # TPU radial fit; PETG free fit is MATERIALS["PETG"]["fit"]
WALL = 1.2
WALL_IMPACT = 2.0
D_M3_TAP, D_M2_TAP = 2.7, 1.7  # self-tapping (>= 5 mm engagement for M3)
D_M3_THRU, D_M2_THRU = 3.4, 2.4
D_M3_HEAD, H_M3_HEAD = 5.7, 1.65  # ISO 7380 button head
D_M3_HEAD_RECESS, H_M3_HEAD_RECESS = 6.6, 2.0
D_M2_HEAD = 4.2
HEX_M3_AF, HEX_M3_H = 5.7, 2.6
HEX_M5_AF, HEX_M5_H = 8.4, 4.2
SMA_AF, SMA_H = 8.4, 3.5
D_SMA, SMA_FLAT = 6.5, 6.0  # D-hole for an SMA bulkhead
SMA_SEAT_WALL_MAX = 2.2
D_CLIP_BORE = 6.5  # C-clip bore round a Ø6 standoff
CLIP_WALL = 1.6
MOUTH_FILLET = 0.45
BOSS_D = {"TPU95A": 4.0, "PETG": 4.1}  # registration boss into a Ø4.5/Ø4.6 plate hole
BRIDGE_MAX = {m: v["bridge_max"] for m, v in MATERIALS.items()}
BAR_LEN = 90.0  # 915 MHz T-antenna bar
MOTOR_PROP_SEAT = 25.0  # see _fit.OWN_DISC_Z_MAX
CAM_PIVOT = (0.0, 100.0, 27.0)  # camera tilt axis: Axis(CAM_PIVOT, (1, 0, 0)); +angle tilts the lens up
CAM_TILT_RANGE = (0.0, 40.0)

# --- equipment envelopes (frame coordinates) ---------------------------------------------
BATTERY = box(-25, -95, 38.5, 25, 55, 83.5)  # 50 x 150 x 45 pack on the top plate
VTX = box(-16, -87.5, 5, 16, -50.5, 17)  # 32 x 37 x 12 VTX on 3 mm M2 standoffs, centred (0, -69)
FC_STACK = box(-18.5, -18.5, 9, 18.5, 18.5, 34)  # 37 x 37 boards between the mid and top plates


def camera_envelope(width: float = 21.0, height: float = 22.0, depth: float = 24.0, lens_d: float = 14.0,
                    lens_len: float = 6.0, pivot=CAM_PIVOT, tilt_deg: float = 0.0, fit: float = FIT,
                    front_offset: float = 10.0) -> Part:
    """Camera body (width x height x depth, +fit per side, height centred on the pivot, front face
    `front_offset` ahead of it) plus the lens cylinder, tilted about Axis(pivot, +X). At 0 deg the
    21 mm lens tip is at y 116.25, Z 27; at 40 deg the body's rear-bottom corner is at Z 9.2."""
    w, h, d = width + 2 * fit, height + 2 * fit, depth + 2 * fit
    y_front = front_offset + fit
    body = Pos(0, y_front - d / 2, 0) * Box(w, d, h)
    lens = Pos(0, y_front, 0) * Cylinder(lens_d / 2 + fit, lens_len, rotation=(-90, 0, 0), align=MIN_Z_ALIGN)
    cam = (body + lens).moved(Location(Vector(*pivot)))
    return cam.rotate(Axis(Vector(*pivot), (1, 0, 0)), tilt_deg) if tilt_deg else cam


def _cam_silhouette(height, depth, lens_d, lens_len, fit, front_offset) -> Sketch:
    """YZ silhouette with the pivot at the origin: local x = frame +Y, local y = frame +Z."""
    d, h, yf = depth + 2 * fit, height + 2 * fit, front_offset + fit
    return Pos(yf - d / 2, 0) * Rectangle(d, h) + Pos(yf + lens_len / 2, 0) * Rectangle(lens_len, lens_d + 2 * fit)


def tilt_sweep(width: float = 21.0, a0: float = CAM_TILT_RANGE[0], a1: float = CAM_TILT_RANGE[1],
               height: float = 22.0, depth: float = 24.0, lens_d: float = 14.0, lens_len: float = 6.0,
               pivot=CAM_PIVOT, fit: float = FIT, front_offset: float = 10.0) -> Part:
    """Exact volume swept by camera_envelope() tilted from a0 to a1 (analytic 2D union: both end
    poses, one pie sector per silhouette vertex, the inscribed disc; then extruded in X).
    ~60 ms versus seconds for a stack of rotated copies. Anything the camera may hit must
    satisfy (part & tilt_sweep(...)).volume == 0."""
    prof = _cam_silhouette(height, depth, lens_d, lens_len, fit, front_offset)
    verts = [Vector(v.X, v.Y) for v in prof.vertices()]
    rmax = max(v.length for v in verts)
    sectors = []
    for v in verts:
        th = degrees(atan2(v.Y, v.X))
        wedge = Polygon((0, 0), *(Vector(2 * rmax, 0).rotate(Axis.Z, th + a) for a in (a0, (a0 + a1) / 2, a1)), align=None)
        sectors.append(Circle(v.length) & wedge)
    inner = Circle(min(height / 2 + fit, front_offset + fit, depth - front_offset + fit))
    sk = Sketch() + [prof.rotate(Axis.Z, a0), prof.rotate(Axis.Z, a1), *sectors, inner]
    yz = Plane(Vector(*pivot), x_dir=(0, 1, 0), z_dir=(1, 0, 0))
    return extrude(yz * sk, amount=(width + 2 * fit) / 2, both=True)


def fov_wedge(tilt: float, cam_w: float = 21.0, half_angle: float = 50.0, length: float = 15.0,
              pivot=CAM_PIVOT, lens_reach: float = 16.25) -> Part:
    """Field-of-view prism from the lens tip at this tilt: rays at tilt +- half_angle in the YZ
    plane, `length` long, extruded x +-cam_w/2. Must not intersect anything in front of the camera."""
    tip = Vector(0, lens_reach * cos(radians(tilt)), lens_reach * sin(radians(tilt)))
    rays = [tip + Vector(0, length * cos(radians(tilt + s * half_angle)), length * sin(radians(tilt + s * half_angle)))
            for s in (1, -1)]
    tri = Polygon(*((p.Y, p.Z) for p in (tip, *rays)), align=None)
    yz = Plane(Vector(*pivot), x_dir=(0, 1, 0), z_dir=(1, 0, 0))
    return extrude(yz * tri, amount=cam_w / 2, both=True)


# --- builders -----------------------------------------------------------------------------
def c_clip(center: tuple[float, float], z0: float, h: float, opening_deg: float = 0.0, material: str = "TPU95A",
           bore_d: float = D_CLIP_BORE, wall: float = CLIP_WALL, snap: float | None = None,
           mouth_fillet: float = MOUTH_FILLET, closed: bool = True) -> Part:
    """Collar round a standoff axis: bore Ø bore_d, OD bore_d + 2 wall, Z z0..z0+h.

    closed=True (the default) is a COMPLETE ring that encircles the standoff. That is the correct
    interface: it cannot be levered off, it carries load all the way round, and it keeps the part
    concentric instead of letting it splay at the mouth. The part is threaded on while the standoff
    is out, or over the standoff before its plate goes back on.

    closed=False cuts a mouth of width STANDOFF_D - snap facing `opening_deg` (0 = +X, 90 = +Y,
    180 = -X) with filleted lips, so the part snaps on sideways with the frame assembled. Only use
    it where fitting without disassembly is the whole point of the part, and say so where you call
    it -- an open mouth is a deliberate trade of retention for serviceability, not a default."""
    r_in, r_out = bore_d / 2, bore_d / 2 + wall
    sk = Circle(r_out) - Circle(r_in)
    if not closed:
        snap = MATERIALS[material]["snap"] if snap is None else snap
        mouth = STANDOFF_D - snap
        sk -= Rectangle(r_out + 1, mouth, align=(Align.MIN, Align.CENTER))  # from the centre outward
        lips = sk.vertices().filter_by(lambda v: abs(abs(v.Y) - mouth / 2) < 1e-6)
        if mouth_fillet > 0:
            sk = fillet(lips, mouth_fillet)
    return extrude(Plane.XY.offset(z0) * sk.rotate(Axis.Z, opening_deg), amount=h).moved(Location((*center, 0)))


def hex_pocket(af: float, depth: float, at: tuple[float, float, float] = (0, 0, 0), rotation_deg: float = 0.0) -> Part:
    """Hexagonal prism tool (across-flats `af`) from Z at[2] up to at[2] + depth; subtract it."""
    x, y, z = at
    return Pos(x, y, z) * extrude(RegularPolygon(af / 2 / cos(radians(30)), 6).rotate(Axis.Z, rotation_deg), amount=depth)


def boss(center: tuple[float, float], z0: float, h: float, d: float) -> Part:
    """Registration peg: Ø d cylinder Z z0..z0+h (e.g. BOSS_D['TPU95A'] into a Ø4.5 plate hole)."""
    return cylinder(*center, z0, z0 + h, d)


def screw_hole(center: tuple[float, float], z_top: float, d: float, depth: float, head_d: float = 0.0,
               head_h: float = 0.0) -> Part:
    """Cutting tool: Ø d bore from z_top down by `depth`, optional Ø head_d x head_h recess at the top."""
    x, y = center
    tool = cylinder(x, y, z_top - depth, z_top + 0.01, d)
    if head_d and head_h:
        tool = tool + cylinder(x, y, z_top - head_h, z_top + 0.01, head_d)
    return tool


def pair(part: Part, name: str) -> dict[str, Part]:
    """{name_right: fresh copy, name_left: mirror(Plane.YZ)} - build the right side, mirror for the left."""
    right = deepcopy(part)
    right.label = f"{name}_right"
    left = part.mirror(Plane.YZ)
    left.label = f"{name}_left"
    return {right.label: right, left.label: left}


def print_orientation(part: Part, bed_normal=(0, 0, -1)) -> Part:
    """Copy of the part rotated so the face whose outward normal is `bed_normal` (frame coords)
    points down, then moved to bbox centre XY = 0 and min Z = 0. The installed part is untouched."""
    n = Vector(*bed_normal).normalized()
    down = Vector(0, 0, -1)
    axis_dir = n.cross(down)
    if axis_dir.length > 1e-9:
        p = part.rotate(Axis((0, 0, 0), axis_dir), n.get_signed_angle(down, axis_dir))
    elif n.Z > 0:
        p = part.rotate(Axis.X, 180)
    else:
        p = part.moved(Location())
    bb = p.bounding_box()
    p = p.moved(Location((-bb.center().X, -bb.center().Y, -bb.min.Z)))
    p.label = part.label
    return p


def overhangs(part: Part, bed_normal=(0, 0, -1), min_area: float = 5.0, cos_limit: float = 0.7,
              bridge_ok: tuple = (), material: str = "TPU95A") -> list[str]:
    """Downward faces (normal.Z < -cos_limit) larger than min_area in PRINT orientation, excluding
    the bed plane, arches (cylindrical faces with a horizontal axis and d <= arch_d) and planar
    faces inside a bridge_ok box ('box', xmin, ymin, zmin, xmax, ymax, zmax in print coords) whose
    shorter horizontal extent <= BRIDGE_MAX. Curved faces are sampled on a 3x3 (u, v) grid and
    the flagged area is prorated. Empty list = printable without supports."""
    printed = print_orientation(part, bed_normal)
    limit = MATERIALS[material]["bridge_max"]
    arch_d = MATERIALS[material]["arch_d"]
    bad = []
    for f in printed.faces():
        if f.area <= min_area:
            continue
        bb = f.bounding_box()
        if f.geom_type == GeomType.PLANE:
            nz = f.normal_at().Z
            if nz >= -cos_limit or bb.max.Z < 1e-3:
                continue
            span = min(bb.size.X, bb.size.Y)
            if any(bb.min.X >= b[1] - 1e-6 and bb.min.Y >= b[2] - 1e-6 and bb.min.Z >= b[3] - 1e-6
                   and bb.max.X <= b[4] + 1e-6 and bb.max.Y <= b[5] + 1e-6 and bb.max.Z <= b[6] + 1e-6
                   for b in bridge_ok if b[0] == "box") and span <= limit:
                continue
            bad.append(f"planar {f.area:.1f} mm² at Z {bb.min.Z:.1f}-{bb.max.Z:.1f}, normal.Z {nz:.2f}")
            continue
        if f.geom_type == GeomType.CYLINDER:
            # A trimmed cylinder (a bore split by a boolean, a filleted run-out) arrives as a
            # Geom_RectangularTrimmedSurface, which has no .Cylinder() of its own - its
            # BasisSurface() does. Unwrap it, or a plain Ø6.5 bore printed on its side loses the
            # arch exemption and is reported as an unsupported overhang.
            surf = f.geom_adaptor()
            while not hasattr(surf, "Cylinder") and hasattr(surf, "BasisSurface"):
                surf = surf.BasisSurface()
            cyl = surf.Cylinder() if hasattr(surf, "Cylinder") else None
            if cyl is not None and abs(cyl.Axis().Direction().Z()) < 0.01 and 2 * cyl.Radius() <= arch_d:
                continue
        samples = [f.normal_at(u, v).Z for u in (0.15, 0.5, 0.85) for v in (0.15, 0.5, 0.85)]
        frac = sum(1 for z in samples if z < -cos_limit) / len(samples)
        if frac * f.area > min_area:
            bad.append(f"{f.geom_type.name.lower()} {f.area:.1f} mm² ({frac:.0%} facing down) at Z {bb.min.Z:.1f}-{bb.max.Z:.1f}")
    return bad
