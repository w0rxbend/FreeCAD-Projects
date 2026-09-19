"""Frame interface constants and fit/clearance checks for accessories.

Every number here is derived from tigerbee.params / tigerbee.frame at import time; the frame
itself is built once (cached) on first use. All probes and checks work in FRAME coordinates on
parts in their installed position. Standoffs are checked against Ø STANDOFF_D (6.0, the
physical part), not the modelled Ø5.
"""

from functools import lru_cache
from math import hypot

from build123d import (Align, Axis, Box, Compound, Cylinder, Face, GeomType, Kind, Part, Plane, Pos,
                       Rectangle, Vector)

from tigerbee import params as P
from tigerbee.frame import PLATES, STANDOFFS, build_frame, motor_centers, place_arm  # noqa: F401 (re-exported)
from tigerbee.mounts import HOLES
from tigerbee.profiles import _CONTOURS, _outer_face, column

MIN_Z_ALIGN = (Align.CENTER, Align.CENTER, Align.MIN)
EPS = 1e-3  # mm^3 below which a boolean intersection counts as empty

# --- frame interface constants (frame coordinates, mm) -----------------------------
STANDOFF_D = 6.0  # physical standoff OD; every standoff clearance is designed for this
STANDOFF_FIT = 0.25  # designed radial gap between a clip bore and the Ø6 standoff
PROP_D = 177.8  # 7-inch prop
PROP_MARGIN = 3.0
PROP_KEEPOUT_R = PROP_D / 2 + PROP_MARGIN  # 91.9
PROP_Z0 = P.Z_MID  # arm top face: nothing but arms/motor hardware inside a disc above this
MOTOR_PROP_SEAT = 25.0  # motor-mounted material may sit in its OWN disc up to PROP_Z0 + MOTOR_PROP_SEAT - 10
OWN_DISC_Z_MAX = PROP_Z0 + MOTOR_PROP_SEAT - 10
LANDING_Z = -3.0  # default lowest point of any accessory (motor_guard -10, led_buzzer -12 opt out)

Z_BOTTOM_UNDER = P.Z_BOTTOM  # 0: plate_bottom underside
Z_BOTTOM_TOP = P.Z_BOTTOM + P.PLATE_T  # 2: plate_bottom top face, tail floor, arm underside
Z_ARM_TOP = P.Z_MID  # 7
Z_MID_UNDER = P.Z_MID  # 7
Z_MID_TOP = P.Z_MID + P.PLATE_T  # 9: stack / camera-bay floor
Z_TOP_UNDER = P.Z_TOP  # 34
Z_TOP_TOP = P.Z_TOP + P.PLATE_T  # 36
PLATE_FACES = {"plate_bottom": (Z_BOTTOM_UNDER, Z_BOTTOM_TOP), "plate_mid": (Z_MID_UNDER, Z_MID_TOP),
               "plate_top": (Z_TOP_UNDER, Z_TOP_TOP)}

MOTOR_CENTERS = motor_centers()  # {"front_right": (x, y), ...}
STANDOFF_XY = {name: (x, y) for name, (x, y, _z0, _h) in STANDOFFS.items()}
STANDOFF_Z = {name: (z0, z0 + h) for name, (_x, _y, z0, h) in STANDOFFS.items()}
FRONT_TIP_XY = P.FRONT_TIP  # (19, 109) right side; left = (-x, y)
REAR_TIP_XY = P.REAR_TIP  # (16.5, -94)
FRONT_ARM_XY = STANDOFF_XY["standoff_front_arm_right"]  # (28.528, 31.831)
REAR_ARM_XY = STANDOFF_XY["standoff_rear_arm_right"]  # (26.070, -33.373)
FORK_CROTCH_Y = _CONTOURS["plate_top"][0][1]  # 75: top-plate fork window starts here
NOSE_TIP_Y = _CONTOURS["plate_mid"][0][1]  # 116: mid-plate nose tip
_TOP_BB = _outer_face("plate_top").bounding_box()
PRONG_TIP_Y = _TOP_BB.max.Y  # 114.416: top-plate prong tips
TOP_REAR_Y = _TOP_BB.min.Y  # -100: rear end of the top-plate prongs (U-notch floor is y -82 at x 0)
ARM_NAMES = tuple(P.ARM_PLACEMENTS)
FRAME_SOLID_NAMES = [*PLATES, *ARM_NAMES, *STANDOFFS]


def hole_xy(name: str, plate: str | None = None) -> list[tuple[float, float]]:
    """Centres of every frame hole called `name` (see dist/manifest.json["holes"])."""
    return [(h.x, h.y) for h in HOLES if h.name == name and (plate is None or plate in h.plates)]


def hole_d(name: str) -> float:
    return next(h.d for h in HOLES if h.name == name)


def arm_to_frame(x: float, y: float, arm: str) -> tuple[float, float]:
    """Arm-local (x, y) -> frame XY for arm 'arm_front_right' etc."""
    return P.place(x, y, P.ARM_PLACEMENTS[arm])


# --- frame cache -----------------------------------------------------------------------
@lru_cache(maxsize=1)
def _frame() -> tuple[Compound, dict[str, Part]]:
    return build_frame()


def frame_parts() -> dict[str, Part]:
    """The 15 frame solids by name (built once per process). Never mutate them."""
    return _frame()[1]


def frame_compound() -> Compound:
    return _frame()[0]


def frame_solid_names() -> list[str]:
    return list(frame_parts())


@lru_cache(maxsize=4)
def standoff_cylinders(d: float = STANDOFF_D) -> dict[str, Part]:
    """Ø d cylinders on the eight standoff axes (default Ø6: physical clearance probes)."""
    return {name: column(x, y, z0, h, d / 2) for name, (x, y, z0, h) in STANDOFFS.items()}


@lru_cache(maxsize=4)
def prop_discs(z0: float = PROP_Z0, z1: float = 80.0, r: float = PROP_KEEPOUT_R) -> dict[str, Part]:
    return {name: column(x, y, z0, z1 - z0, r) for name, (x, y) in MOTOR_CENTERS.items()}


def plate_face(plate: str, z: float | None = None) -> Face:
    """Planar face of a frame part at Z z (default: its top face), holes included."""
    part = frame_parts()[plate]
    z = part.bounding_box().max.Z if z is None else z
    faces = [f for f in part.faces() if f.geom_type == GeomType.PLANE and abs(f.center().Z - z) < 1e-4
             and abs(f.normal_at().Z) > 0.999]
    assert faces, f"{plate} has no horizontal face at Z {z}"
    return max(faces, key=lambda f: f.area)


def outline_spans(plate: str, y: float, material: bool = False) -> list[tuple[float, float]]:
    """X intervals covered by the plate outline at Y y (material=True: holes/cutouts subtracted)."""
    face = plate_face(plate) if material else _outer_face(plate)
    strip = Pos(0, y, face.center().Z) * Rectangle(300, 0.002)
    res = face & strip
    faces = res.faces() if res is not None and hasattr(res, "faces") else []
    return sorted((round(f.bounding_box().min.X, 3), round(f.bounding_box().max.X, 3)) for f in faces if f.area > 1e-6)


def on_plate(plate: str, x: float, y: float) -> bool:
    """True when (x, y) lies on plate material (outline minus holes and cutouts)."""
    face = plate_face(plate)
    return face.is_inside((x, y, face.center().Z))


# --- primitives in frame coordinates ---------------------------------------------------
def box(x0: float, y0: float, z0: float, x1: float, y1: float, z1: float) -> Part:
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(x1 - x0, y1 - y0, z1 - z0)


def cylinder(x: float, y: float, z0: float, z1: float, d: float) -> Part:
    """Vertical Ø d cylinder from z0 to z1."""
    return column(x, y, z0, z1 - z0, d / 2)


def volume(shape) -> float:
    return 0.0 if shape is None else float(shape.volume)


def isect(a, b) -> float:
    """Volume of a & b (0 when disjoint); the boolean returns None for disjoint shapes in 0.11."""
    try:
        return volume(a & b)
    except Exception:  # OCCT can throw on degenerate contacts; treat as disjoint
        return 0.0


def bbox_overlap(a, b, pad: float = 0.0) -> bool:
    A, B = a.bounding_box(), b.bounding_box()
    return not (A.max.X + pad < B.min.X or B.max.X + pad < A.min.X or A.max.Y + pad < B.min.Y
                or B.max.Y + pad < A.min.Y or A.max.Z + pad < B.min.Z or B.max.Z + pad < A.min.Z)


def erode(part: Part, t: float, kind: Kind = Kind.INTERSECTION) -> Part:
    """Inward 3D offset by t (negative offset). Raises when OCCT cannot offset the geometry."""
    off = part.solid().offset_3d(None, -t, kind=kind)
    # OCCT reports failure as a null or empty shape rather than an exception (seen on small
    # fillets, e.g. the c_clip mouth lips); make that an error so callers can fall back.
    # Measure on the Solid: a Part wrapping a bare TopoDS_Solid reports volume 0.
    if off is None or off.wrapped is None or off.wrapped.IsNull() or off.volume <= 0:
        raise RuntimeError(f"offset_3d collapsed the solid at t={t}")
    # Part(<bare TopoDS_Solid>) reports volume 0; go through the compound-building operator.
    return Part() + off


def dilate(part: Part, t: float, kind: Kind = Kind.INTERSECTION) -> Part:
    """Outward 3D offset by t. Raises when OCCT degenerates the result instead of growing it."""
    off = part.solid().offset_3d(None, t, kind=kind)
    out = Part() + off if off is not None and off.wrapped is not None and not off.wrapped.IsNull() else None
    if out is None or out.volume < part.volume:
        raise RuntimeError(f"offset_3d failed to grow the solid at t={t}")
    return out


# --- checks --------------------------------------------------------------------------------
def interference(part: Part, allowance: float = 0.0, against: dict[str, Part] | None = None) -> list[tuple[str, float]]:
    """(frame part, overlap mm^3) for every frame solid the part overlaps by > EPS.
    allowance > 0 erodes the part by that much first (intended press fits)."""
    probe = erode(part, allowance) if allowance > 0 else part
    hits = []
    for name, other in (against if against is not None else frame_parts()).items():
        if bbox_overlap(probe, other):
            v = isect(probe, other)
            if v > EPS:
                hits.append((name, round(v, 3)))
    return hits


def standoff_interference(part: Part, d: float = STANDOFF_D) -> list[tuple[str, float]]:
    """Overlap with the Ø6 standoff probes (stricter than the modelled Ø5 solids)."""
    return interference(part, against=standoff_cylinders(d))


def distance_to_frame(part: Part, near: float = 10.0, standoff_d: float = STANDOFF_D) -> dict[str, float]:
    """Gap to every frame part whose bbox is within `near` mm; standoffs measured to Ø6 cylinders.
    0.0 means touching or overlapping."""
    out = {}
    probes = {**{n: p for n, p in frame_parts().items() if not n.startswith("standoff")}, **standoff_cylinders(standoff_d)}
    for name, other in probes.items():
        if bbox_overlap(part, other, near):
            out[name] = round(part.distance_to(other), 4)
    return dict(sorted(out.items(), key=lambda kv: kv[1]))


def coaxial(part: Part, xy: tuple[float, float], d: float, z0: float | None = None, z1: float | None = None,
            tol: float = 0.05) -> tuple[bool, str]:
    """Is there a Ø d bore on the vertical axis through xy over Z z0..z1 (default: the part's Z range)?
    A Ø(d - tol) probe must be void AND an annulus Ø(d + 2 tol)..Ø(d + 2 tol + 1.2) must hit material,
    so a missing bore and a part that is not there at all both fail. Works for C-clips too."""
    bb = part.bounding_box()
    z0 = bb.min.Z + 0.01 if z0 is None else z0
    z1 = bb.max.Z - 0.01 if z1 is None else z1
    x, y = xy
    probe = column(x, y, z0, z1 - z0, (d - tol) / 2)
    ring = column(x, y, z0, z1 - z0, d / 2 + tol + 0.6) - column(x, y, z0 - 1, z1 - z0 + 2, d / 2 + tol)
    inside, around = isect(part, probe), isect(part, ring)
    ok = inside < EPS and around > EPS
    return ok, f"Ø{d} at ({x:.3f}, {y:.3f}) Z {z0:.2f}-{z1:.2f}: {inside:.3f} mm³ in bore, {around:.1f} mm³ round it"


def assert_coaxial_hole(part: Part, xy: tuple[float, float], z0: float, z1: float, d: float, tol: float = 0.05) -> None:
    ok, detail = coaxial(part, xy, d, z0, z1, tol)
    assert ok, detail


def prop_disc_violation(part: Part, z0: float = PROP_Z0, z1: float = 80.0, exclude: tuple[str, ...] = ()) -> float:
    """Volume of the part inside the four prop keep-out cylinders (r 91.9) between z0 and z1.
    exclude: motor names ('front_right', ...) whose disc is skipped (own-disc collar rule)."""
    total = 0.0
    for name, disc in prop_discs(z0, z1).items():
        if name not in exclude and bbox_overlap(part, disc):
            total += isect(part, disc)
    return total


def seats_on(part: Part, frame_part: str, z_face: float, tol: float = 0.02) -> float:
    """Contact area (mm^2) between the part's horizontal faces at z_face and that frame part's
    face at z_face. Seating faces are meant to touch exactly (0.0 gap)."""
    try:
        target = plate_face(frame_part, z_face)
    except AssertionError:
        return 0.0
    area = 0.0
    for f in part.faces():
        if f.geom_type != GeomType.PLANE or abs(f.normal_at().Z) < 0.999 or abs(f.center().Z - z_face) > tol:
            continue
        try:
            res = f & target
        except Exception:
            continue
        if res is None:
            continue
        area += sum(x.area for x in res.faces()) if hasattr(res, "faces") else getattr(res, "area", 0.0)
    return round(area, 3)


def seated(part: Part, z_face: float, tol: float = 0.02) -> float:
    """seats_on() against whichever plate has a face at z_face (0, 2, 7, 9, 34, 36)."""
    for plate, faces in PLATE_FACES.items():
        if any(abs(z - z_face) < 1e-6 for z in faces):
            return seats_on(part, plate, z_face, tol)
    raise ValueError(f"no plate face at Z {z_face}; use seats_on(part, name, z)")


WALL_TOL = 0.02  # a wall built exactly at the threshold must pass its own min-wall check


_BARY = ((1 / 3, 1 / 3, 1 / 3), (0.6, 0.2, 0.2), (0.2, 0.6, 0.2), (0.2, 0.2, 0.6),
         (0.45, 0.45, 0.1), (0.45, 0.1, 0.45), (0.1, 0.45, 0.45), (0.8, 0.1, 0.1),
         (0.1, 0.8, 0.1), (0.1, 0.1, 0.8))


def ray_thickness(part: Part, t: float, allow: tuple[Part, ...] = (), per_face: int = 40,
                  max_rays: int = 20000) -> tuple[bool, float, str]:
    """Local wall thickness by shooting a ray inward from sampled surface points and measuring
    the distance to the far surface. Needs no offset, so it works where erode() collapses.
    Returns (any wall thinner than t, worst thickness found, detail). Points inside an `allow`
    solid (declared thin features) are skipped. Heuristic: grazing rays on curved faces can
    read short, so a single thin sample is reported with its count, not treated as exact.
    Sample points come from each face's triangulation, never from the surface's parametric
    rectangle: on a trimmed face (any taper, loft or non-rectangular profile) uv points near
    the narrow end fall outside the trim and would read a neighbouring wall as paper thin.

    KNOWN BLIND SPOT: a ray leaving a knife edge or a rounded tip (clip mouth lips, blade-like
    ribs, fillet crowns) travels ALONG the material and measures a long chord, so tapering tips
    read as thick. erode()/min_wall's offset path does catch them; this fallback does not. A
    pass from here means 'no thin wall found by rays', not 'no thin wall'. For a prismatic part
    whose tips matter, section the plan profile and do a 2D opening instead."""
    faces = [f for f in part.faces() if f.area > 0.2]
    if not faces:
        return False, 0.0, "no sampleable faces"
    budget = max(1, max_rays // len(faces))
    worst, thin, total = float("inf"), 0, 0
    for f in faces:
        try:
            verts, tris = f.tessellate(0.3)
        except Exception:  # noqa: BLE001
            continue
        if not tris:
            continue
        want = min(per_face, budget)
        step = max(1, len(tris) // want)
        used = tris[::step]
        # Planar faces tessellate into 2 triangles, so centroids alone would sample a large
        # wall at 2 points; spread several barycentric points inside each triangle instead.
        k = max(1, min(len(_BARY), -(-want // len(used))))
        for tri, (b0, b1, b2) in ((tri, bary) for tri in used for bary in _BARY[:k]):
            p = verts[tri[0]] * b0 + verts[tri[1]] * b1 + verts[tri[2]] * b2
            try:
                if not f.is_inside(p):
                    continue
                normal = f.normal_at(p)
            except Exception:  # noqa: BLE001  degenerate triangle
                continue
            if any(a.wrapped is not None and not a.wrapped.IsNull() and a.is_inside(p)
                   for a in allow):
                continue
            d = -normal
            origin = p + d * 1e-4
            try:
                hits = part.find_intersection_points(Axis(origin, d))
            except Exception:  # noqa: BLE001
                continue
            # Discard hits right at the origin: where two faces of the same solid meet at a
            # shallow seam the neighbour sits a few hundredths of a mm ahead and is not a wall.
            floor = min(0.1, t / 20)
            ahead = [x for x in ((h[0] - origin).dot(d) for h in hits) if x > floor]
            if not ahead:
                continue
            total += 1
            thickness = min(ahead)
            if thickness < t - WALL_TOL:
                thin += 1
                worst = min(worst, thickness)
    if not total:
        return False, 0.0, "no usable rays"
    if thin == 0:
        return False, t, f"{total} rays, none thinner than {t} mm (rays cannot see knife-edge tips)"
    return True, worst, f"{thin}/{total} rays thinner than {t} mm, worst {worst:.2f} mm"


def min_wall(part: Part, t: float, allow: tuple[Part, ...] = ()) -> tuple[bool, float, str]:
    """Heuristic: erode by t/2, dilate by t/2, residual = part - result; regions thinner than t
    vanish in the erosion and show up as residual. Volumes of `allow` (intentional thin features:
    lips, ribs, mouth fillets) are subtracted. Pass = residual <= 2 mm^3 and no residual lump with
    a bbox larger than 3 x 3 mm. Limits: OCCT offsets can fail on complex/filleted geometry (then
    (False, -1, error)); sharp internal corners and fillets < t leave slivers of a few mm^3;
    it cannot see walls that are thin only in the print direction after slicing.
    When OCCT cannot offset the geometry at all (small fillets collapse the erosion, e.g. any
    c_clip mouth lip) it falls back to ray_thickness(), which needs no offset."""
    # Erode by slightly less than t/2 so a wall built exactly at the threshold (WALL == t)
    # is not collapsed by its own check.
    half = max(t / 2 - WALL_TOL, 1e-3)
    try:
        residual = part - dilate(erode(part, half), half)
    except Exception:  # noqa: BLE001  OCCT offset failure -> ray sampling instead
        thin, worst, detail = ray_thickness(part, t, allow)
        return not thin, round(worst, 3), f"ray sampling (offset unavailable): {detail}"
    for feature in allow:
        if bbox_overlap(residual, feature):
            residual = residual - feature
    lumps = [s for s in residual.solids() if s.volume > 0.05]
    big = [s for s in lumps if sorted((s.bounding_box().size.X, s.bounding_box().size.Y, s.bounding_box().size.Z))[1] > 3.0]
    vol = sum(s.volume for s in lumps)
    ok = vol <= 2.0 and not big
    return ok, round(vol, 3), f"thin residual {vol:.2f} mm³ in {len(lumps)} lump(s), {len(big)} larger than 3x3"


def min_wall_ok(part: Part, t: float, allow: tuple[Part, ...] = ()) -> bool:
    return min_wall(part, t, allow)[0]


def single_solid(part: Part) -> tuple[bool, str]:
    n = len(part.solids())
    ok = n == 1 and part.volume > 0 and part.is_valid
    return ok, f"{n} solid(s), {part.volume:.1f} mm³, valid={part.is_valid}"


def in_prop_disc(x: float, y: float, r: float = PROP_KEEPOUT_R) -> bool:
    return any(hypot(x - mx, y - my) < r for mx, my in MOTOR_CENTERS.values())


def max_abs_x_at(y: float, r: float = PROP_KEEPOUT_R) -> float:
    """Largest |x| allowed above Z 7 at this y by the nearest prop keep-out (see interface map §1.3)."""
    best = float("inf")
    for mx, my in MOTOR_CENTERS.values():
        if abs(y - my) < r:
            best = min(best, abs(mx) - (r * r - (y - my) ** 2) ** 0.5)
    return best
