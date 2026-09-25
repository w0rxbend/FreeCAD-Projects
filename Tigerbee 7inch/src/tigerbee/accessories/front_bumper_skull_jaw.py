"""FERAL skull-jaw front bumper: crossed mandibles, a dorsal spine row and a toothed jaw lip.

The hero of the FERAL family and the part this frame gets photographed with. Hybrid build123d +
Blender: build123d owns every mating and functional feature (the seat on plate_top at Z 36, the
fork-edge step, the two front-tip bolt axes, the jaw lip, the silhouette) and also builds a CRUDE
PARAMETRIC PROXY of every organic feature - tusks, spines, teeth, serrations - so the part is
complete and shippable with no Blender at all. Blender's `sculpt` recipe re-grows those proxies as
faired organic strokes over a voxel remesh, and build123d then CUTS every mating face back into the
result, so the seat, the bores and the silhouette are exact B-rep again:

    final = sculpt(core + proxies) - (Z36 trim + plan trim + bores + counterbores
                                      + rim rebate + lunule + puncta)

THE ASSEMBLY IS SUBTRACTION ONLY, and that is not a style choice. The first version decorated the
two cheeks separately and UNIONED the mesh solids into the CAD core: the result carried three faces
of NEGATIVE area and seventeen under 1e-4 mm², BRepCheck called it valid, UnifySameDomain changed
nothing, and the 3MF exporter refused the part outright. Unioning a mesh solid into a CAD solid is
what makes those slivers, so the union happens in Blender - where mesh booleans are reliable - and
OCCT only ever subtracts simple exact cutters.

STEP and FCStd for this part are TESSELLATED CONVERSIONS: the decorated solid is sewn one planar
facet at a time. The faces the frame touches are exact, because every one of them is a cut.

DESIGN NOTES, all of them forced by measurement rather than taste:

  * NOTHING PROTRUDES BELOW THE SEATING PLANE. A key dropping 1.2 mm into the fork's U-notch was
    modelled, checked and removed: it lifts the whole 1287 mm² seating face 1.2 mm off the bed,
    which is an unsupported overhang that no bridge exemption reaches (the face's shorter extent is
    49 mm against TPU's 22 mm bridge). The fork edge registers IN PLAN instead - the whole plate_top
    silhouette, outer edge and U-notch alike, offset 0.25 mm - and the dorsal rail stands on that
    edge as the visible step. The two M3 bolts locate the part.
  * THE TUSK RISES AT 48.5 deg BECAUSE A ROUND SICKLE HAS TO. The most downward normal of a tube
    with tangent elevation a is -cos a, against overhangs()' -0.70 limit, so anything shallower than
    45.6 deg needs supports. The camera's 60 deg FOV cone reaches back to y 109.84 and up to Z 52.2
    inside |x| <= 10.5 and the tilt sweep fills |x| <= 10.75 up to Z 43, so the sickle may only come
    inboard behind y 109.5 or above Z 52.7. Those three numbers fix the path; the 40 mm length and
    the 126 deg of plan sweep fall out of it.
  * THE SERRATIONS ARE ADDITIVE. A 2.0 mm notch cut into a Ø4.6 tusk leaves a 0.6 mm wall, under the
    1.2 TPU floor, so the inner teeth are grown outward from the tusk's inner flank instead - which
    is what a mandible's teeth actually are.
  * THE JAW TEETH SIT AT A FIXED 1.7 mm PITCH so their bases overlap into one toothed ridge. Two
    teeth spread over the four-tooth span stand 2.3 mm apart, which the voxel remesh webs together
    at 0.52 mm - the single gate the `lite` variant failed.
  * NO BOTTOM FILLETS, NO INNER REBATE. Rounding a lower edge puts a downward quadrant above the bed
    plane; rebating the plate's inner rim leaves the dorsal rail floating over a void.
  * `_fit.min_wall` IS UNUSABLE HERE. OCCT will not offset this plate's spline outline at all
    ("Null TopoDS_Shape"), and _fit's ray fallback has no grazing filter - it reports 0.29 mm on a
    plain 2.5 mm plate. The wall is measured on the mesh by Blender's own sampler, twice: once by
    the bridge on the decorated solid and once by tools/front_bumper_skull_jaw_blender.py on the
    whole part. Both rows must pass, and the designed thicknesses are asserted arithmetically.

TPU 95A only: a rigid tusk is a spear that snaps and takes the mount with it.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import subprocess
import time
from functools import lru_cache
from pathlib import Path

from build123d import (Axis, Circle, Cone, Face, GeomType, Part, Plane, Polygon, Pos, Rectangle,
                       Sketch, Sphere, Vector, export_stl, fillet, loft, offset)

from tigerbee.accessories import _blender as BL
from tigerbee.accessories import _style as S
from tigerbee.accessories._common import *  # noqa: F401,F403 - constants, builders and checks
from tigerbee.profiles import _outer_face

NAME = "front_bumper_skull_jaw"
TITLE = "Skull-jaw front bumper"
MATERIAL = "TPU95A"
PRINT = {NAME: (0, 0, -1)}
EXCLUSIVE = ("front_bumper",)
MOUNTS = ("plate_top top face Z 36 over the front fork (seating plane)",
          "plate_top outer silhouette and fork U-notch, offset 0.25 mm (the registering edge)",
          "standoff_front_tip_left / _right bolt axes (±19.0, 109.0) through plate_top")
HARDWARE = ("2 x M3 x 14 button head (through the bumper and plate_top into the front-tip "
            "standoffs; replaces the 2 x M3 x 8 the frame ships with)",)
NOTES = ("Drop it on the front fork - the edge is the plate_top profile offset 0.25 mm, so it "
         "registers against the fork by eye - and bolt it with two M3 x 14 through the counterbored "
         "bosses at (±19, 109). Alternative to front_bumper; both claim the prong tops. Prints "
         "base-down in TPU 95A with no supports: the whole underside is the seating plane and every "
         "tusk, spine and tooth rises steeper than 45 deg. STEP and FCStd are TESSELLATED "
         "CONVERSIONS of the sculpted solid; every face the frame touches is an exact cut.")

VARIANTS = {
    "full": {"style": "feral",
             "params": {"TUSK_LEN": 40.0, "N_TEETH": 4, "N_SPINES": 5, "N_SERR": 4},
             "notes": "full crossed mandibles: 40 mm tusks crossing at x ∓1.5 above the camera"},
    "lite": {"style": "feral",
             "params": {"TUSK_LEN": 22.0, "N_TEETH": 2, "N_SPINES": 3, "N_SERR": 2},
             "notes": "short 22 mm tusks that curl inward without crossing - for FOV-tight builds"},
}
ASSEMBLY_VARIANT = "full"

# --- parameters (mm) ------------------------------------------------------------------------
STYLE = S.style_of("feral")
WALL_MIN = 1.2                  # TPU 95A structural floor
Z_SEAT = Z_TOP_TOP              # 36.0, plate_top top face
T_PLATE = 2.5                   # base plate
Z_PLATE = Z_SEAT + T_PLATE      # 38.5
T_JAW = 3.0                     # jaw lip / cheek thickness
Z_JAW = Z_SEAT + T_JAW          # 39.0
STEP_FIT = 0.25                 # the plate's edge is the plate_top profile offset by this
STEP_Y = (82.0, 98.0)           # where the U-notch edge is a clean registering step
PLATE_Y0 = 72.0                 # rear edge of the base plate
PLATE_Y1 = PRONG_TIP_Y - 0.4    # 114.02: the plate stops short of the prong tips
OUT_INSET = STEP_FIT            # the whole silhouette, inner notch included, is offset 0.25

BOLT_XY = FRONT_TIP_XY          # (19, 109)
BOSS_D = 10.6
Z_BOSS = Z_SEAT + 4.6           # 40.6
CB_D, CB_H = D_M3_HEAD_RECESS, 2.0   # Ø6.6 x 2.0 counterbore -> 2.6 mm web under the head
THRU_D = D_M3_THRU              # 3.4

RIDGE_OFF, RIDGE_W = STEP_FIT, 4.0   # the dorsal step: flush with the plate's own notch edge
RAIL_Y = (81.0, 108.0)   # 1.1 clear of the lunule slash, which ends at y 79.9
SCAFF_Z = (Z_PLATE - 1.3, Z_JAW + 0.6)     # 37.2 .. 39.6: the rail/lobe, buried 1.3 in the plate
TEETH_Z = Z_JAW - 0.1                      # tooth bases, inside the lobe

TUSK_ROOT = (17.4, 103.2, 39.4)            # right tusk root, buried in the cheek lobe
# The sickle in plan. Every waypoint is where it is because of a keep-out: the path may only come
# inboard of |x| 10.9 once it is behind y 109.5 (the FOV cone's rearmost reach) or above Z 52.7
# (its top), and the root circle must sit wholly inside the cheek lobe.
TUSK_PLAN = ((17.4, 103.2), (18.0, 106.2), (17.3, 108.4), (14.2, 108.0),
             (10.3, 104.9), (5.6, 101.0), (-1.4, 96.9))
TUSK_RISE = 48.5                # deg above horizontal, constant: -cos(48.5) = -0.663 > -0.70
TUSK_R0, TUSK_R1 = 3.0, 0.8     # root Ø6.0 -> tip Ø1.6, never a needle
TUSK_LEN = 40.0                 # 3D arc length (variant parameter)
HEEL, HEEL_R = 2.6, 1.1         # the buried start of the sickle (see _tusk_stations)
TUSK_CROSS_DY = 4.5             # the left tusk's inner half is pulled back this far, so the two
#                                 tusks cross with real clearance instead of meeting on x = 0
SERR_AT = (0.36, 0.52, 0.67, 0.80)   # fractions along the tusk carrying an inner tooth
SERR_LEN = (2.6, 2.2, 1.8, 1.4)      # decreasing toward the tip
N_SERR = 4

SPINE_H0, SPINE_FALL = 9.0, 0.78     # 9.0 : 7.02 : 5.48 : 4.27 : 3.33
SPINE_R0, TIP_R = 2.2, 0.75          # Ø1.5 tips: the 1.2 wall floor survives the voxel remesh
SPINE_Y0, SPINE_PITCH = 106.0, 6.0
SPINE_LEAN = 14.0               # deg, leaning back toward the tail
N_SPINES = 5

TOOTH_H, TOOTH_R0 = 8.0, 1.6    # front-edge teeth, pointing up and 20 deg forward
TOOTH_X0, TOOTH_PITCH = 15.4, 1.7   # a FIXED pitch: see _teeth()
TOOTH_LEAN = 20.0
N_TEETH = 4

PUNCTA_D, PUNCTA_PITCH, PUNCTA_DEPTH = 2.2, 4.0, 0.45   # the cheek plate (see _puncta_tool)
PUNCTA_LIG, PUNCTA_Y1 = 1.0, 104.0
TIP_BALL_R, TUSK_CLEAR = 0.4, 1.5   # a Ø0.8 ball at every tip; 1.5 between the crossed tusks
LUNULE_SIZE, LUNULE_Y, LUNULE_ANGLE = 16.0, 78.6, 8.0   # cut through as a slash (FERAL accent)
EDGE_LEAD, EDGE_TRAIL = 0.3, 1.6    # the asymmetry that makes it read as a creature
REBATE_W, REBATE_T = EDGE_TRAIL, 1.5   # trailing rim: 2.5 -> 1.5 thick over a 1.6 band (CN-5)

VOXEL = 0.4                     # <= WALL_MIN / 3
TRI_BUDGET = 12_000             # the whole part; the measured OCCT knee (hard ceiling 20 000)
BUILD_DIR = Path(__file__).resolve().parents[3] / "build" / "skull_jaw"
TOOL_SCRIPT = Path(__file__).resolve().parents[3] / "tools" / "front_bumper_skull_jaw_blender.py"

# Keep-outs this part is designed around, all measured from the real frame and pod modules:
FOV_HALF_ANGLE = 60.0
FOV_TILTS = (0, 5, 10, 15, 20, 25, 30, 35, 40)
POD_HOOD_X = 13.75 + 0.3        # the pod brow above Z 34 lives inside this, y >= 114.22


# --- parameter set ----------------------------------------------------------------------------
def params(variant: str = "full", **overrides) -> dict:
    """Every number the geometry depends on, in one dict: also what the build cache hashes."""
    p = dict(TUSK_LEN=TUSK_LEN, N_TEETH=N_TEETH, N_SPINES=N_SPINES, N_SERR=N_SERR,
             TUSK_RISE=TUSK_RISE, TUSK_R0=TUSK_R0, TUSK_R1=TUSK_R1, TUSK_CROSS_DY=TUSK_CROSS_DY,
             SPINE_H0=SPINE_H0, SPINE_FALL=SPINE_FALL, SPINE_R0=SPINE_R0, TIP_R=TIP_R,
             SPINE_Y0=SPINE_Y0, SPINE_PITCH=SPINE_PITCH, SPINE_LEAN=SPINE_LEAN,
             TOOTH_H=TOOTH_H, TOOTH_R0=TOOTH_R0, TOOTH_LEAN=TOOTH_LEAN, VOXEL=VOXEL,
             TRI_BUDGET=TRI_BUDGET, variant=variant)
    p.update((v := VARIANTS.get(variant, {})).get("params", {}))
    p.update(overrides)
    p["variant"] = variant
    return p


@lru_cache(maxsize=1)
def _source_digest() -> str:
    """This module's own source, hashed. TUSK_PLAN, the cheek polygon and the rail offsets are
    module constants rather than entries in params(), so without this a geometry edit would be
    served the previous build/skull_jaw/<variant>/base.stl out of the cache."""
    try:
        return hashlib.blake2b(Path(__file__).read_bytes(), digest_size=8).hexdigest()
    except OSError:
        return "nosrc"


def _hash(p: dict) -> str:
    return hashlib.blake2b(json.dumps({**p, "_src": _source_digest()}, sort_keys=True,
                                      default=str).encode(), digest_size=8).hexdigest()


# --- 2D helpers on the real plate_top profile --------------------------------------------------
def _strip(x0: float, x1: float, y0: float, y1: float) -> Sketch:
    return Pos((x0 + x1) / 2, (y0 + y1) / 2) * Rectangle(x1 - x0, y1 - y0)


@lru_cache(maxsize=4)
def _top_outline(amount: float = 0.0) -> Sketch:
    """plate_top's filled silhouette (the fork U is a notch in the outer wire, not a hole)."""
    sk = Sketch() + Face(_outer_face("plate_top").outer_wire())
    return offset(sk, amount=amount) if amount else sk


@lru_cache(maxsize=8)
def _window(amount: float = 0.0) -> Sketch:
    """The fork window between the prongs, offset by `amount` (negative shrinks it)."""
    gap = _strip(-40, 40, FORK_CROTCH_Y - 8, PRONG_TIP_Y - 0.02) - _top_outline()
    w = Sketch() + [f for f in gap.faces() if f.is_inside((0, 100, 0))]
    return offset(w, amount=amount) if amount else w


def _notch_x(y: float) -> float:
    """|x| of the fork notch wall at this y (the inner edge of the right prong)."""
    spans = [s for s in outline_spans("plate_top", y) if s[1] > 1.0]
    assert spans, f"no right-hand plate_top span at y {y}"
    return min(a for a, _b in spans)


def _raise(sk: Sketch, z0: float, z1: float) -> Part:
    """Extrude a footprint, FACE BY FACE. A 2D fuse of two overlapping regions does not always
    unify them into one face (measured: body 1224.5 + band 370.1 -> two faces sharing an edge), and
    extruding that sketch in one call returns two overlapping solids whose volume is double counted.
    Part + Part is a real 3D fuse and gives one solid."""
    from build123d import extrude
    out = Part()
    for f in sk.faces():
        out = out + extrude(Plane.XY.offset(z0) * (Sketch() + f), amount=z1 - z0, dir=(0, 0, 1))
    return out


# --- the sickle: one path, used by the CAD proxy and by the Blender strokes ----------------------
def _smooth(pts, passes: int = 2):
    """Chaikin-free 3-point smoothing that keeps the ends: enough to kill the polyline kinks that
    would otherwise show as creases in the lofted proxy and as self-intersections in the sweep."""
    out = [tuple(q) for q in pts]
    for _ in range(passes):
        new = [out[0]]
        for a, b, c in zip(out, out[1:], out[2:]):
            new.append(tuple((x + 2 * y + z) / 4 for x, y, z in zip(a, b, c)))
        new.append(out[-1])
        out = new
    return out


def _densify(pts, step: float = 0.6):
    out = []
    for a, b in zip(pts, pts[1:]):
        d = math.dist(a, b)
        n = max(1, int(d / step))
        for i in range(n):
            t = i / n
            out.append(tuple(u + (v - u) * t for u, v in zip(a, b)))
    out.append(tuple(pts[-1]))
    return out


@lru_cache(maxsize=8)
def _tusk_stations(length: float, rise: float, r0: float, r1: float, n: int = 22):
    """[(x, y, z, r)] along the right tusk, resampled to `n` stations.

    The plan polyline is smoothed and densified, then truncated at the plan distance that makes the
    3D arc length equal `length` (plan = length * cos(rise)). z climbs at a constant `rise` above
    horizontal, which is what keeps a round section self-supporting."""
    plan = _densify(_smooth(_densify(TUSK_PLAN, 1.2), 3), 0.25)
    # THE HEEL. A lofted tube starts with a flat cap square to its own tangent, so a tusk rising at
    # 48.5 deg starts with a Ø6 disc whose normal points DOWN-backward at -0.75 - 12.3 mm² of
    # unsupported overhang, measured, on each side. The path is therefore extended HEEL mm back
    # down the initial tangent at a small radius, which puts the cap inside the cheek and below the
    # seating plane, where the Z 36 trim removes it outright.
    back = Vector(plan[0][0] - plan[3][0], plan[0][1] - plan[3][1], 0)
    back = back.normalized() if back.length > 1e-9 else Vector(0, -1, 0)
    heel = [(plan[0][0] + back.X * HEEL * (1 - i / 4.0), plan[0][1] + back.Y * HEEL * (1 - i / 4.0))
            for i in range(4)]
    plan = heel + plan
    want = length * math.cos(math.radians(rise)) + HEEL
    tan = math.tan(math.radians(rise))
    s, path = 0.0, [(plan[0][0], plan[0][1], 0.0)]
    for a, b in zip(plan, plan[1:]):
        d = math.dist(a, b)
        if s + d >= want:
            t = (want - s) / d if d else 0.0
            path.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, want))
            s = want
            break
        s += d
        path.append((b[0], b[1], s))
    total = path[-1][2] or 1.0
    out = []
    for i in range(n):
        want_s = total * i / (n - 1)
        # INTERPOLATE, never snap to the nearest densified point: on the short `lite` tusk the
        # nearest-point form returned the same point for consecutive stations, which makes a
        # zero-length segment - and a zero tangent reads as a 0 deg elevation and a 0 mm tip.
        j = 0
        while j < len(path) - 2 and path[j + 1][2] < want_s:
            j += 1
        a, b = path[j], path[j + 1]
        span = b[2] - a[2]
        t = 0.0 if span <= 1e-9 else min(1.0, max(0.0, (want_s - a[2]) / span))
        x, y = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
        if want_s < HEEL:                       # the buried heel: swells from Ø2.2 to the root Ø
            r = HEEL_R + (r0 - HEEL_R) * (want_s / HEEL)
        else:
            f = (want_s - HEEL) / max(total - HEEL, 1e-6)
            # radius eases out so the tip is a cusp, not a cone: r = r0 + (r1 - r0) * f^0.78
            r = r0 + (r1 - r0) * f ** 0.78
        out.append((x, y, TUSK_ROOT[2] + (want_s - HEEL) * tan, r))
    return tuple(out)


def _frames(st):
    """(point, tangent, inward-normal) per station, for hanging serrations off the tusk."""
    out = []
    for i, (x, y, z, r) in enumerate(st):
        a = st[max(0, i - 1)]
        b = st[min(len(st) - 1, i + 1)]
        t = Vector(b[0] - a[0], b[1] - a[1], b[2] - a[2])
        t = t.normalized() if t.length > 1e-9 else Vector(0, 0, 1)
        side = Vector(-t.Y, t.X, 0)          # left of travel = the inner (concave) flank
        side = side.normalized() if side.length > 1e-6 else Vector(-1, 0, 0)
        out.append((Vector(x, y, z), t, (side + Vector(0, 0, 0.45)).normalized(), r))
    return out


def _serrations(st, n: int):
    """[(base, tip, r_base, r_tip)] for the inner teeth on the tusk's concave flank."""
    fr = _frames(st)
    out = []
    for i in range(min(n, len(SERR_AT))):
        f = SERR_AT[i]
        k = max(1, min(len(fr) - 2, int(round(f * (len(fr) - 1)))))
        p, _t, nrm, r = fr[k]
        # measured from the tusk's CENTRELINE, so every tooth projects SERR_LEN clear of the flank
        # whatever the local radius. Measuring from the surface swallowed the last two entirely:
        # at f 0.80 the tusk is Ø2.4 and a 1.4 mm spur of tip radius 0.75 never came out.
        out.append((p + nrm * (r * 0.2), p + nrm * (r + SERR_LEN[i]), max(r * 0.55, 0.9), TIP_R))
    return out


def _spines(n: int):
    """[(base, tip, r_base, r_tip)] for the descending dorsal spine row, front-most tallest."""
    out = []
    for i in range(n):
        y = SPINE_Y0 - i * SPINE_PITCH
        x = _notch_x(y) + RIDGE_OFF + RIDGE_W / 2
        h = SPINE_H0 * SPINE_FALL ** i
        lean = math.radians(SPINE_LEAN)
        base = Vector(x, y, SCAFF_Z[1] - 1.0)
        tip = base + Vector(0, -math.sin(lean) * h, math.cos(lean) * h)
        out.append((base, tip, SPINE_R0 * SPINE_FALL ** (i * 0.5), TIP_R))
    return out


def _teeth(n: int):
    """[(base, tip, r_base, r_tip)] along the jaw lip's front edge, pointing up and forward.

    They sit BEHIND y 114.0 and outboard of x 15: the camera pod's brow occupies |x| <= 13.75
    forward of y 114.22 up to Z 38, and the FOV prism owns |x| <= 10.5 forward of y 109.84."""
    out = []
    lean = math.radians(TOOTH_LEAN)
    for i in range(n):
        # FIXED PITCH, not "n teeth spread over the same span". At 1.7 the Ø3.2 bases overlap and
        # the row remeshes as one toothed ridge; spreading two teeth over the four-tooth span puts
        # them 2.3 apart, which is close enough for the voxel remesh to web them together and far
        # enough for that web to be 0.52 mm - measured, and the one gate the `lite` variant failed.
        x = TOOTH_X0 + i * TOOTH_PITCH
        y = 113.8 - 0.06 * (x - 18.0) ** 2      # a shallow arc round the camera's brow
        h = TOOTH_H * (1.0 - 0.16 * i)
        base = Vector(x, y, TEETH_Z)
        tip = base + Vector(0, math.sin(lean) * h, math.cos(lean) * h)
        out.append((base, tip, TOOTH_R0 * (1.0 - 0.1 * i), TIP_R))
    return out


# --- solids: the functional core (pure build123d, 100 % of the mating geometry) -----------------
def _rear_cut(inset: float = 0.0) -> Sketch:
    """Everything behind the cusped neck line, subtracted from the plate: the rear edge dips to
    y 68 on the centreline and rises to y 74.5 at the flanks (CN-3, and it keeps the centre bridge
    - the only material joining the two prongs - at full depth). `inset` walks the line forward."""
    d = inset * 1.03   # the neck line runs at ~13 deg, so a normal inset is this much in y
    edge = ((-45, 76.9 + d), (-13, 69.6 + d), (0, 68.0 + d), (13, 69.6 + d), (45, 76.9 + d))
    return Polygon(*edge, (45, 50), (-45, 50), align=None)


@lru_cache(maxsize=2)
def _cheek_fp() -> Sketch:
    """The right jaw cheek in plan: a rounded lobe that flares 2.3 mm proud of the carbon at the
    front corner and reaches 2.8 mm ahead of the prong tip as the jaw lip."""
    poly = Polygon((13.9, 100.0), (13.9, 111.0), (14.95, 112.8), (14.95, 114.2), (15.7, 116.2),
                   (18.6, 117.2), (22.6, 116.7), (25.6, 114.0), (26.3, 110.0), (24.6, 105.2),
                   (21.4, 99.6), align=None)
    for xy, r in (((14.95, 114.2), 1.0), ((26.3, 110.0), 3.0), ((24.6, 105.2), 2.5),
                  ((21.4, 99.6), 2.5), ((13.9, 100.0), 2.0)):
        poly = _fillet_at(poly, xy, r)
    return poly


def _fillet_at(sk: Sketch, xy: tuple[float, float], r: float) -> Sketch:
    v = sk.vertices().filter_by(lambda q: abs(q.X - xy[0]) < 1e-6 and abs(q.Y - xy[1]) < 1e-6)
    if len(v) != 1:
        return sk
    for radius in (r, r * 0.6, r * 0.35):
        try:
            return fillet(v, radius)
        except Exception:  # noqa: BLE001 - a shallow corner cannot take the nominal radius
            continue
    return sk


def _plate_fp(inset: float = 0.0) -> Sketch:
    """Base plate footprint: the whole plate_top silhouette - outer edge AND fork U-notch - offset
    0.25 mm, plus the two jaw cheeks, minus the cusped neck line.

    That single 0.25 offset is the registering edge: drop the bumper on and its inner edge stands
    0.25 mm off the fork's notch wall the whole way round, which is what `outline_spans` is read for.

    `inset` pulls every FREE edge in by that much (and no other edge), which is what the rim rebate
    is built from. It is applied to the source profile, never to the union: OCCT will not offset the
    assembled outline ("Unexpected result type") and will not taper-extrude it either."""
    body = _top_outline(-(OUT_INSET + inset)) & _strip(-40, 40, PLATE_Y0 - 6, PLATE_Y1 - inset)
    fp = body + _cheek_fp() + _cheek_fp().mirror(Plane.YZ)
    return fp - _rear_cut(inset)





def _rail_fp(side: int) -> Sketch:
    """The dorsal ridge rail one prong carries, parallel to the notch."""
    band = _window(RIDGE_OFF + RIDGE_W) - _window(RIDGE_OFF)
    half = _strip(1.0, 40, *RAIL_Y) if side > 0 else _strip(-40, -1.0, *RAIL_Y)
    return band & half


def _lobe_fp(side: int) -> Sketch:
    """The cheek lobe the tusk, the teeth and the rail all grow out of - the blank's floor."""
    lo = Polygon((14.4, 100.4), (14.4, 115.0), (16.6, 115.9), (19.4, 115.4), (20.9, 111.0),
                 (20.9, 101.0), align=None)
    lo = _fillet_at(lo, (20.9, 111.0), 2.0)
    lo = _fillet_at(lo, (20.9, 101.0), 2.0)
    lo = _fillet_at(lo, (14.4, 100.4), 2.0)
    return lo if side > 0 else lo.mirror(Plane.YZ)


def _spike(base: Vector, tip: Vector, r0: float, r1: float) -> Part:
    """A tapered cone from `base` to `tip` - one spine, tooth or serration."""
    d = tip - base
    h = d.length
    if h < 1e-6:
        return Part()
    pl = Plane(origin=base.to_tuple(), z_dir=d.normalized().to_tuple())
    return pl * Cone(bottom_radius=r0, top_radius=max(r1, 0.05), height=h, align=MIN_Z_ALIGN)


def _tube(st) -> Part:
    """The lofted proxy sickle. A ruled loft through circles on the path's own normal planes; if
    OCCT refuses the loft, a chain of frustums, which Blender fairs into the same shape anyway."""
    secs = []
    for i, (x, y, z, r) in enumerate(st):
        a, b = st[max(0, i - 1)], st[min(len(st) - 1, i + 1)]
        t = Vector(b[0] - a[0], b[1] - a[1], b[2] - a[2])
        t = t.normalized() if t.length > 1e-9 else Vector(0, 0, 1)
        secs.append(Plane(origin=(x, y, z), z_dir=t.to_tuple()) * Circle(r))
    try:
        part = loft(secs, ruled=True)
        if part is not None and part.volume > 1.0:
            return Part() + part
    except Exception:  # noqa: BLE001
        pass
    part = Part()
    for a, b in zip(st, st[1:]):
        part += _spike(Vector(*a[:3]), Vector(*b[:3]), a[3], b[3])
    return part


def _tusk_side(p: dict, side: int, n: int = 14):
    """The tusk stations for one side. The LEFT tusk is not a mirror: its inner half is pulled back
    by TUSK_CROSS_DY so the two tusks cross with real clearance instead of meeting on x = 0."""
    st = _tusk_stations(p["TUSK_LEN"], p["TUSK_RISE"], p["TUSK_R0"], p["TUSK_R1"], n)
    if side > 0:
        return st
    m = len(st) - 1
    return tuple((-x, y - p["TUSK_CROSS_DY"] * (i / m) ** 1.5, z, r)
                 for i, (x, y, z, r) in enumerate(st))


def _organ_strokes(p: dict, side: int) -> list[dict]:
    """Every organic feature of one side as a Blender stroke: the tusk, its inner serrations, the
    dorsal spine row and the jaw teeth. The same list drives the build123d proxy."""
    st = _tusk_side(p, side, 24)
    out = [{"points": [[x, y, z] for x, y, z, _r in st], "radii": [r for *_q, r in st]}]
    for b, t, r0, r1 in _side_rows(p, side):
        mid = b + (t - b) * 0.55
        out.append({"points": [list(b.to_tuple()), list(mid.to_tuple()), list(t.to_tuple())],
                    "radii": [r0, r0 * 0.55 + r1 * 0.45, r1]})
    return out


def _side_rows(p: dict, side: int):
    """[(base, tip, r0, r1)] of every spike on one side, in FRAME coordinates.

    The serrations are computed from THAT SIDE'S OWN tusk stations and are therefore already on the
    right side of x = 0; mirroring them again (as the spines and teeth must be) put four spurs on
    the opposite flank, floating in mid air - the "input is 6 solids, not one" the bridge refused."""
    rows = [*_serrations(_tusk_side(p, side, 24), int(p["N_SERR"]))]
    for base, tip, r0, r1 in [*_spines(int(p["N_SPINES"])), *_teeth(int(p["N_TEETH"]))]:
        if side > 0:
            rows.append((base, tip, r0, r1))
        else:
            rows.append((Vector(-base.X, base.Y, base.Z), Vector(-tip.X, tip.Y, tip.Z), r0, r1))
    return rows


def _organs(p: dict, side: int) -> Part:
    """The build123d proxy of everything in _organ_strokes(): crude, faceted, and complete, so the
    part still has its tusks when Blender is missing."""
    part = _tube(_tusk_side(p, side, 14))
    for b, t, r0, r1 in _side_rows(p, side):
        part += _spike(b, t, r0, r1)
    return part


def _scaffold(p: dict, side: int) -> Part:
    """The blank's floor: the cheek lobe and the dorsal rail, both buried 1.3 mm in the plate and
    inset from every exact silhouette, so the voxel remesh never reaches a mating face."""
    return _raise(_lobe_fp(side), *SCAFF_Z) + _raise(_rail_fp(side), *SCAFF_Z)


def _cuts(p: dict) -> Part:
    """Functional cuts, re-applied after decoration so they land on exact B-rep: the two bolt
    bores, their counterbores, and the trim plane at the seating face."""
    # NOTHING BELOW THE SEATING PLANE, and that is a printability rule, not tidiness: a key
    # dropping 1.2 mm into the U-notch lifts the whole 1287 mm² seating face 1.2 mm off the bed,
    # where it is an unsupported overhang no bridge exemption reaches (the face's shorter extent is
    # 49 mm against a 22 mm TPU bridge). Measured, modelled, removed - the fork edge registers in
    # plan at +0.25 instead and the two M3 bolts locate the part.
    cut = box(-60, 55, -20, 60, 140, Z_SEAT)
    for sx in (1, -1):
        x, y = sx * BOLT_XY[0], BOLT_XY[1]
        cut += cylinder(x, y, Z_SEAT - 2, Z_BOSS + 30, THRU_D)
        cut += cylinder(x, y, Z_BOSS - CB_H, Z_BOSS + 30, CB_D)
    # THE PLAN TRIM, below the cheek top only: everything outside the exact footprint is removed, so
    # the decorated mesh cannot wander past the silhouette the fit checks were written against. The
    # organs above Z_JAW are free-form and are left alone.
    hull = _plate_fp() + _cheek_fp() + _cheek_fp().mirror(Plane.YZ)
    cut += _raise(_strip(-60, 60, 55, 140) - hull, Z_SEAT - 1.0, Z_JAW)
    cut += _rim_rebate()
    cut += _lunule()
    pun, n_pun, free = _puncta_tool()
    if pun is not None and pun.volume > 0:
        cut += pun
    _PUNCTA_COUNT.update({"n": n_pun, "free": free})
    return cut


_PUNCTA_COUNT: dict = {"n": 0, "free": 0.0}


def _lunule() -> Part:
    """CN-4 for FERAL: the elytral sickle CUT THROUGH as a slash, mirrored on the two flanks."""
    tool = Part()
    for mx in (False, True):
        tool += S.mark("lunule", LUNULE_SIZE, "cut", at=((-14.0 if mx else 14.0), LUNULE_Y, Z_SEAT - 1.0),
                       through=T_PLATE + 2.0, angle=(-LUNULE_ANGLE if mx else LUNULE_ANGLE), mirror_x=mx)
    return tool


def _lunule_sketch() -> Sketch:
    """The two lunule slashes in plan - used as a clean zone for the punctation field."""
    out = Sketch()
    for mx in (False, True):
        out += Pos(-14.0 if mx else 14.0, LUNULE_Y) * \
            S.mark_sketch("lunule", LUNULE_SIZE, mirror_x=mx).rotate(Axis.Z, -LUNULE_ANGLE if mx else LUNULE_ANGLE)
    return out


def _puncta_tool() -> tuple[Part, int, float]:
    """Punctation: blind Ø2.2 dimples 0.45 deep on the flat cheek plate, built on the RIGHT half
    and mirrored so the field is symmetric whatever the grid does.

    NOT on the jaw cheek lobes, and that is a measurement rather than a preference: after the Ø10.6
    bolt boss and the lobe the tusk grows from, the largest free island on a cheek is 11.2 mm², and
    one Ø2.2 dimple with the TPU 1.2 ligament needs ~19. The surface that does hold a field is the
    cheek plate behind the jaw, which is where a tiger beetle's punctation rows actually run."""
    region = _plate_fp(REBATE_W) & _strip(0.5, 40, 60.0, PUNCTA_Y1)
    clean = [_lunule_sketch(), _rail_fp(1), _cheek_fp()]
    tool, n = S.puncta(region, pitch=PUNCTA_PITCH, d=PUNCTA_D, depth=PUNCTA_DEPTH, z_face=Z_PLATE,
                       clean=clean, ligament_min=PUNCTA_LIG, seed=3)
    free = float(region.area)
    if n and tool.volume > 0:
        return tool + tool.mirror(Plane.YZ), 2 * n, free
    return Part(), 0, free


def _rim_rebate() -> Part:
    """FERAL's asymmetric edge and CN-5's thickness gradient in one cutter: the trailing plate rim
    steps down to REBATE_T over a REBATE_W band (2.5 -> 1.5 mm, the material floor); the leading
    jaw cheeks are excluded and stay sharp. A TOP-face rebate only - shaving a lower edge would put
    a downward-facing band above the bed plane and flag overhangs().

    Built in 2D from the footprint and its own inset, never with fillet()/chamfer() on the edge
    set: filleting the 38 top edges of this core in one OCCT call takes the process down (no
    exception, no traceback - the interpreter is simply gone), taper-extruding the assembled
    outline raises "Null TopoDS_Shape", and offsetting the assembled outline raises "Unexpected
    result type". Only the source profiles can be offset, which is what _plate_fp(inset) does.
    A lofted 0.3 chamfer on the cheeks was tried and refused: it left five 0.06 mm downward
    slivers of 5-12 mm² round the rim, each one an overhang the checker rightly flags."""
    cheeks = _cheek_fp() + _cheek_fp().mirror(Plane.YZ)
    # The OUTER silhouette only. The plate's inner (fork) edge is a free edge too, but it carries
    # the dorsal rail: rebating under it leaves the rail's top 1.0 mm floating over a void - two
    # 36.3 mm² faces pointing straight down, measured, and rightly flagged.
    rim = (_plate_fp() - _plate_fp(REBATE_W)) - cheeks - _window(RIDGE_OFF + RIDGE_W + 0.6)
    if rim is None or not rim.faces():
        return Part()
    return _raise(rim, Z_SEAT + REBATE_T, Z_PLATE + 0.1)


def _meshable(shape) -> tuple[bool, str]:
    """Can build123d's Mesher take this solid? A sewn mesh solid can be BRepCheck-valid and still
    carry a face with null triangulation, which STL export silently drops and 3MF export refuses."""
    try:
        from build123d import Mesher
        probe = Mesher()
        probe.add_shape(shape, linear_deflection=BL.EXPORT_TOL, angular_deflection=BL.EXPORT_ANG,
                        part_number="skull-jaw-probe")
        return True, "ok"
    except Exception as exc:  # noqa: BLE001
        return False, f"DEGRADED to the parametric base: {type(exc).__name__}: {exc}"


def _core_solid(p: dict) -> Part:
    """Everything whose dimensions must match the frame: the seated plate, the registration step,
    the two counterbored bolt bosses and the jaw cheeks."""
    core = _raise(_plate_fp(), Z_SEAT, Z_PLATE)
    core += _raise(_cheek_fp() + _cheek_fp().mirror(Plane.YZ), Z_SEAT, Z_JAW)
    for sx in (1, -1):
        core += cylinder(sx * BOLT_XY[0], BOLT_XY[1], Z_SEAT, Z_BOSS, BOSS_D)
    return core


# --- the build cache: build/skull_jaw/<variant>/ ------------------------------------------------
def _slot(variant: str) -> Path:
    d = BUILD_DIR / variant
    d.mkdir(parents=True, exist_ok=True)
    return d


def _write_base(base: Part, p: dict, variant: str) -> Path:
    """The parametric base as STL at the brief's tolerances, regenerated only when the parameter
    hash moves or the file is gone. build/ is a build artifact and is git-ignored."""
    slot = _slot(variant)
    stl, meta = slot / "base.stl", slot / "params.json"
    digest = _hash(p)
    fresh = stl.is_file() and meta.is_file() and json.loads(meta.read_text()).get("hash") == digest
    if not fresh:
        assert export_stl(base, str(stl), tolerance=BL.EXPORT_TOL,
                          angular_tolerance=BL.EXPORT_ANG, ascii_format=False), "base.stl"
        meta.write_text(json.dumps({"hash": digest, "params": p}, indent=1, default=str))
    return stl


def _tool_report(p: dict, variant: str, base_stl: Path, force: bool = False) -> dict:
    """Run the standalone sculpt script and parse its one-line JSON result.

    This is the second, independent Blender pass: `_blender.decorate()` builds the geometry that
    ships, this one rebuilds the same strokes on the same base through tools/ and reports what came
    out (vertices, triangles, manifold, components, bbox). checks() uses it for the regeneration
    row - delete the cached STL, rebuild, get the same triangle count - which is the only real
    proof that the sculpt is deterministic."""
    slot = _slot(variant)
    job = {"base": str(base_stl), "voxel": float(p["VOXEL"]), "tri_budget": int(p["TRI_BUDGET"]) * 2,
           "wall_floor": WALL_MIN,
           "strokes": _organ_strokes(p, 1) + _organ_strokes(p, -1),
           "out": str((slot / "tmp" if force else slot) / "skull.stl")}
    digest = _hash({**p, "job": "tool"})
    cached = slot / f"report_{digest}.json"
    if cached.is_file() and not force:
        return json.loads(cached.read_text())
    exe = BL.BLENDER
    if not exe or not TOOL_SCRIPT.is_file():
        return {"ok": False, "reason": f"blender {exe!r} / script {TOOL_SCRIPT.name} unavailable"}
    jf = slot / ("job_force.json" if force else "job.json")
    Path(job["out"]).parent.mkdir(parents=True, exist_ok=True)
    jf.write_text(json.dumps(job, indent=1))
    t0 = time.time()
    try:
        proc = subprocess.run([exe, "--background", "--factory-startup", "--python", str(TOOL_SCRIPT),
                               "--", str(jf)], capture_output=True, text=True, timeout=BL.TIMEOUT,
                              env={**os.environ, "BLENDER_USER_SCRIPTS": "/nonexistent"})
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "reason": f"{type(exc).__name__}: {exc}"}
    rep = {"ok": False, "reason": f"rc={proc.returncode}, no [SKULLJAW] line"}
    for line in proc.stdout.splitlines():
        if line.startswith("[SKULLJAW] "):
            try:
                rep = json.loads(line[len("[SKULLJAW] "):])
                rep["ok"] = bool(rep.get("is_manifold")) and rep.get("components") == 1
            except json.JSONDecodeError as exc:
                rep = {"ok": False, "reason": f"unparsable report: {exc}"}
    rep["seconds"] = round(time.time() - t0, 2)
    if not force:
        cached.write_text(json.dumps(rep, indent=1))
    return rep


# --- build --------------------------------------------------------------------------------------
_LAST: dict[str, dict] = {}   # variant -> {"base": Part, "p": dict, "stl": Path, "decor": {...}}


def build(variant: str = "full", **overrides) -> dict[str, Part]:
    """The part in frame coordinates, under its BASE label.

    ONE Blender pass over the WHOLE part, and then nothing but CUTS. The first version unioned two
    decorated cheeks into the CAD core with OCCT and the result carried three faces of NEGATIVE
    area and seventeen under 1e-4 mm²: BRepCheck called it valid, ShapeUpgrade_UnifySameDomain
    changed nothing, and the 3MF exporter refused the whole part ("3mf mesh is invalid"). Unioning
    a 6000-facet mesh solid into a CAD solid is what produces those slivers, so the union is done
    where mesh booleans are reliable - in Blender, before the remesh - and OCCT is left with only
    SUBTRACTIONS of simple exact cutters. Every mating face is therefore re-established by a cut:
    the seat by the Z 36 trim, the silhouette by the plan trim, the bores and counterbores by their
    own cylinders, the rim rebate, the lunule and the punctation by theirs."""
    p = params(variant, **overrides)
    blank = _core_solid(p)
    for s in (1, -1):
        blank = blank + _scaffold(p, s) + _organs(p, s)
    assert len(blank.solids()) == 1, f"{NAME}: the blank is {len(blank.solids())} solids"
    cuts = _cuts(p)
    base = blank - cuts                       # the part as it ships with no Blender at all
    stl = _write_base(base, p, variant)

    strokes = _organ_strokes(p, 1) + _organ_strokes(p, -1)
    res = BL.decorate_ex(blank, "sculpt",
                         {"mode": "curve", "voxel": float(p["VOXEL"]), "strokes": strokes},
                         cache_key=f"{NAME}__{variant}", wall_floor=WALL_MIN,
                         tri_budget=int(p["TRI_BUDGET"]))
    # res.part is the decorated mesh solid when the bridge applied, and `blank` unchanged when it
    # degraded - so the same subtraction produces the right part either way.
    part = res.part - cuts
    assert len(part.solids()) == 1, f"{NAME}: {len(part.solids())} solids after the cuts"
    # The exporter meshes what it is given and dies if it cannot; probe here and fall back to the
    # undecorated base rather than taking the whole run down. The row in checks() says so.
    meshes, why = _meshable(part)
    if not meshes:
        part = base
    part.label = NAME
    _LAST[variant] = {"base": base, "blank": blank, "p": p, "stl": stl, "decor": res,
                      "meshable": (meshes, why),
                      "lunule": _lunule().volume, "puncta": _PUNCTA_COUNT["n"],
                      "puncta_free": _PUNCTA_COUNT["free"], "strokes": len(strokes)}
    return {NAME: part}


# --- checks --------------------------------------------------------------------------------------
@lru_cache(maxsize=2)
def _fov_cone(half_angle: float = FOV_HALF_ANGLE) -> Part:
    """The camera's whole field of view over its whole tilt range: one wedge per 5 deg of tilt,
    unioned. Nothing this part owns may be inside it at any tilt."""
    cone = None
    for t in FOV_TILTS:
        w = fov_wedge(t, half_angle=half_angle)
        cone = w if cone is None else cone + w
    return cone


@lru_cache(maxsize=2)
def _pods() -> dict[str, Part]:
    """The real camera pods when the sibling module is importable, else a conservative envelope of
    the one thing that matters up here: the brow above Z 34, |x| <= 13.75, y >= 114.22."""
    try:
        from tigerbee.accessories import camera_pod
        out = {}
        for variant in ("", ):
            for lbl, part in camera_pod.build().items():
                out[lbl] = part
        if out:
            return out
    except Exception:  # noqa: BLE001 - a sibling module need not be importable
        pass
    return {"camera_pod envelope": box(-13.75, 114.22, 34.0, 13.75, 122.5, 38.0)
            + box(-15.75, 80.5, 6.0, 15.75, 122.5, 33.8)}


def _tip_probe(part: Part, tip: Vector, back: Vector, r: float = 0.4) -> float:
    """Fraction of a Ø2r ball filled at a designed extremity - the FERAL tip-radius rule, probed at
    the tips this module actually placed rather than at the bounding box corners."""
    c = tip - back.normalized() * r
    ball = Pos(*c.to_tuple()) * Sphere(r)
    try:
        inter = part & ball
        return float(inter.volume) / float(ball.volume) if inter is not None else 0.0
    except Exception:  # noqa: BLE001
        return 0.0


def _tusk_gap(p: dict) -> tuple[float, str]:
    """Smallest surface gap between the two tusks (centreline distance minus both radii)."""
    a = _tusk_stations(p["TUSK_LEN"], p["TUSK_RISE"], p["TUSK_R0"], p["TUSK_R1"], 60)
    m = len(a) - 1
    b = [(-x, y - p["TUSK_CROSS_DY"] * (i / m) ** 1.5, z, r) for i, (x, y, z, r) in enumerate(a)]
    best, at = float("inf"), ""
    for qa in a:
        for qb in b:
            d = math.dist(qa[:3], qb[:3]) - qa[3] - qb[3]
            if d < best:
                best, at = d, f"({qa[0]:.1f}, {qa[1]:.1f}, {qa[2]:.1f})"
    return best, at


def _min_elevation(p: dict) -> float:
    """The shallowest tangent elevation anywhere on the tusk: a round section is self-supporting
    only above 45.6 deg, so this is the printability of the sickle stated as one number."""
    st = _tusk_stations(p["TUSK_LEN"], p["TUSK_RISE"], p["TUSK_R0"], p["TUSK_R1"], 60)
    return min(math.degrees(math.atan2(b[2] - a[2], math.hypot(b[0] - a[0], b[1] - a[1])))
               for a, b in zip(st, st[1:]))


def checks(parts: dict[str, Part], frame: dict[str, Part], variant: str | None = None) -> list:
    part = parts[NAME]
    v = variant or ASSEMBLY_VARIANT
    last = _LAST.get(v) or {}
    p = last.get("p") or params(v)
    out = []

    # --- seating and registration ---------------------------------------------------------------
    contact = seats_on(part, "plate_top", Z_SEAT)
    out.append((f"seated on plate_top at Z {Z_SEAT}", contact >= 300.0, f"{contact} mm² contact"))
    bb = part.bounding_box()
    out.append((f"nothing below the seating plane Z {Z_SEAT} (so the seat is the bed face)",
                abs(bb.min.Z - Z_SEAT) < 1e-6, f"min Z {bb.min.Z:.3f}"))
    ring = _raise((_window(STEP_FIT - 0.10) & _strip(-40, 40, *STEP_Y)), Z_SEAT - 1, Z_BOSS + 1)
    band = _raise(((_window(STEP_FIT + 0.35) - _window(STEP_FIT - 0.10)) & _strip(-40, 40, *STEP_Y)),
                  Z_SEAT, Z_PLATE)
    a, b = isect(part, ring), isect(part, band)
    out.append((f"U-notch step: clears the fork wall by >= {STEP_FIT - 0.1}", a < EPS,
                f"{a:.3f} mm³ inside the notch +{STEP_FIT - 0.10}"))
    out.append((f"U-notch step: the plate edge registers within {STEP_FIT + 0.35} of the wall", b > EPS,
                f"{b:.3f} mm³ in the register band over y {STEP_Y[0]}-{STEP_Y[1]}"))

    # --- the two bolt axes ----------------------------------------------------------------------
    for sx, side in ((1, "right"), (-1, "left")):
        xy = (sx * BOLT_XY[0], BOLT_XY[1])
        ok, detail = coaxial(part, xy, THRU_D, Z_SEAT + 0.05, Z_BOSS - CB_H - 0.05)
        out.append((f"{side} bolt bore Ø{THRU_D} coaxial with standoff_front_tip_{side}", ok, detail))
        cb = cylinder(*xy, Z_BOSS - CB_H + 0.05, Z_BOSS + 5, CB_D - 0.1)
        web = cylinder(*xy, Z_SEAT, Z_BOSS - CB_H - 0.05, CB_D) - cylinder(*xy, Z_SEAT - 1, Z_BOSS, THRU_D + 0.1)
        vcb, vweb = isect(part, cb), isect(part, web)
        out.append((f"{side} Ø{CB_D} x {CB_H} counterbore open to the sky", vcb < EPS, f"{vcb:.3f} mm³ in the recess"))
        out.append((f"{side} head web >= 2.0 under the counterbore", vweb > 0.8 * web.volume,
                    f"{vweb:.1f} of {web.volume:.1f} mm³, web {Z_BOSS - CB_H - Z_SEAT:.1f} mm"))

    # --- clearances -----------------------------------------------------------------------------
    hits = interference(part)
    out.append(("no interference with any frame part", not hits, f"{hits or 'none'}"))
    so = standoff_interference(part)
    out.append((f"clear of the Ø{STANDOFF_D} standoff cylinders", not so, f"{so or 'none'}"))
    for lbl, pod in _pods().items():
        vv = isect(part, pod)
        gap = round(part.distance_to(pod), 3)
        out.append((f"clear of {lbl}", vv < EPS and gap >= 0.2, f"{vv:.3f} mm³, gap {gap} mm"))
    vf = isect(part, _fov_cone())
    out.append((f"outside the {FOV_HALF_ANGLE * 2:.0f}° camera FOV cone over tilt 0-40°", vf < EPS, f"{vf:.3f} mm³"))
    vs = isect(part, tilt_sweep(21, *CAM_TILT_RANGE))
    out.append(("outside the camera tilt sweep 0-40°", vs < EPS, f"{vs:.3f} mm³"))
    vp = prop_disc_violation(part)
    out.append(("outside the front prop keep-out discs", vp < EPS, f"{vp:.3f} mm³"))
    vb = isect(part, BATTERY)
    out.append(("outside the battery envelope", vb < EPS, f"{vb:.3f} mm³"))
    out += _creature_checks(part, p, v, last)
    return out


def _creature_checks(part: Part, p: dict, v: str, last: dict) -> list:
    """The rows that are about the sculpted half of the part: walls, tips, printability, the
    decoration bridge and the regeneration of the cached mesh."""
    out = []
    base = last.get("base")

    # --- walls. erode() collapses a mesh-derived solid, so the CAD floor is measured on the
    # functional base and the decorated part's wall comes from Blender's ray sampler (below).
    thin = [f"rim {REBATE_T}", f"head web {Z_BOSS - CB_H - Z_SEAT:.1f}", f"boss wall {(BOSS_D - CB_D) / 2:.1f}",
            f"tusk tip Ø{2 * p['TUSK_R1']}", f"spine/tooth tip Ø{2 * TIP_R}", f"rail {RIDGE_W}"]
    worst_designed = min(REBATE_T, Z_BOSS - CB_H - Z_SEAT, (BOSS_D - CB_D) / 2, 2 * p["TUSK_R1"], 2 * TIP_R)
    out.append((f"every designed thickness >= {WALL_MIN} (CN-5 gradient {T_PLATE} -> {REBATE_T})",
                worst_designed >= WALL_MIN - 1e-9, f"worst {worst_designed:.2f} mm: " + ", ".join(thin)))

    # --- one solid, valid, exportable -----------------------------------------------------------
    ok, detail = single_solid(part)
    out.append(("watertight single solid, OCCT IsValid", ok, detail))
    meshes, why = last.get("meshable", _meshable(part))
    out.append(("the part as built meshes for STL/3MF export", meshes,
                why if not meshes else f"{len(part.faces())} B-rep faces accepted by the 3MF mesher"))

    # --- tips: a Ø0.8 ball must fit at every designed extremity ---------------------------------
    worst, where = 1.0, "nowhere"
    for side in (1, -1):
        st = _tusk_side(p, side, 24)
        tips = [(Vector(*st[-1][:3]), Vector(*st[-1][:3]) - Vector(*st[-2][:3]))]
        rows = [*_serrations(_tusk_side(p, side, 24), int(p["N_SERR"])),
                *_spines(int(p["N_SPINES"])), *_teeth(int(p["N_TEETH"]))]
        for b_, t_, _r0, _r1 in rows:
            b2, t2 = ((b_, t_) if side > 0 else (Vector(-b_.X, b_.Y, b_.Z), Vector(-t_.X, t_.Y, t_.Z)))
            tips.append((t2, t2 - b2))
        for tip, direction in tips:
            f = _tip_probe(part, tip, direction, TIP_BALL_R)
            if f < worst:
                worst, where = f, f"({tip.X:.1f}, {tip.Y:.1f}, {tip.Z:.1f})"
    out.append((f"tip radius: a Ø{2 * TIP_BALL_R} ball fits at every tip", worst >= 0.30,
                f"worst fill {worst:.2f} at {where}"))
    # --- printability ---------------------------------------------------------------------------
    elev = _min_elevation(p)
    out.append(("tusk tangent >= 45.6° above horizontal everywhere (a round section is then "
                "self-supporting)", elev >= 45.6, f"min {elev:.1f}°, most downward normal -{math.cos(math.radians(elev)):.3f}"))
    if base is not None:
        over = overhangs(base, PRINT[NAME], material=MATERIAL)
        out.append(("parametric base prints base-down with no overhang steeper than 45°", not over,
                    "; ".join(over) or "none (B-rep faces, the honest test: the decorated mesh's "
                                       "facets are each under the 5 mm² floor)"))

    # --- the sickle -----------------------------------------------------------------------------
    gap, at = _tusk_gap(p)
    crossing = min(x for x, *_ in _tusk_side(p, 1, 40)) < 0.0
    out.append((f"tusks clear each other by >= {TUSK_CLEAR}", gap >= TUSK_CLEAR,
                f"{gap:.2f} mm at {at}, {'crossed' if crossing else 'converging, not crossed'}"))
    st = _tusk_side(p, 1, 40)
    shown = [q for q in st if q[2] >= Z_JAW]          # the heel is buried; measure what you can see
    L3 = sum(math.dist(a[:3], b[:3]) for a, b in zip(shown, shown[1:]))
    sweep = _plan_sweep(st)
    out.append((f"tusk {p['TUSK_LEN']:.0f} mm: sweep 110-140°, root Ø{2 * p['TUSK_R0']}, tip Ø{2 * p['TUSK_R1']}",
                110.0 <= sweep <= 140.0 and 2 * p["TUSK_R1"] >= 1.2
                and abs(L3 - p["TUSK_LEN"]) <= 0.12 * p["TUSK_LEN"],
                f"{L3:.1f} mm clear of the cheek, {sweep:.0f}° of plan sweep, tip at Z {st[-1][2]:.1f}"))
    out.append((f"{int(p['N_SERR'])} inner serrations, {int(p['N_SPINES'])} dorsal spines, "
                f"{int(p['N_TEETH'])} jaw teeth per side",
                int(p["N_SPINES"]) == max(3, min(7, round(_char_len() / 9))) or v == "lite",
                f"spine row n = clamp(L/9, 3, 7) with L = {_char_len():.0f}, heights "
                f"{[round(SPINE_H0 * SPINE_FALL ** i, 1) for i in range(int(p['N_SPINES']))]}"))

    # --- accents ---------------------------------------------------------------------------------
    out.append(("lunule cut through both flanks (CN-4, FERAL cuts it as a slash)",
                last.get("lunule", 0.0) > 100.0, f"{last.get('lunule', 0.0):.0f} mm³ of cutter, "
                f"{LUNULE_SIZE} mm, through {T_PLATE} mm of plate"))
    n_pun, free = int(last.get("puncta", 0)), last.get("puncta_free", 0.0)
    out.append((f"puncta Ø{PUNCTA_D} @ {PUNCTA_PITCH} within the Ø2.4 / 0.45 caps",
                PUNCTA_D <= 2.4 and PUNCTA_DEPTH <= 0.45 and n_pun >= 4,
                f"{n_pun} dimples on {free:.0f} mm² of cheek plate; the jaw cheeks themselves hold "
                f"11.2 mm² after the Ø{BOSS_D} boss and the tusk lobe - too little for one dimple"))

    # --- the Blender bridge -----------------------------------------------------------------------
    for name, ok, detail in BL.decor_checks(f"{NAME}__{v}"):
        out.append((name, ok, detail))

    # --- the standalone script, and regeneration ---------------------------------------------------
    stl = last.get("stl")
    out.append(("parametric base cached at build/skull_jaw/<variant>/base.stl",
                bool(stl) and Path(stl).is_file(), str(stl)))
    rep = _tool_report(p, v, Path(stl)) if stl else {"ok": False, "reason": "no base.stl"}
    out.append((f"{TOOL_SCRIPT.name}: one manifold component", bool(rep.get("ok")),
                f"{rep.get('verts', '?')} verts, {rep.get('tris', '?')} tris, manifold="
                f"{rep.get('is_manifold')}, components={rep.get('components')}, "
                f"{rep.get('reason', '')} {rep.get('seconds', '')}s"))
    wall = rep.get("wall") or {}
    out.append((f"mesh wall >= {WALL_MIN} on the WHOLE part (Blender rays, grazing filtered)",
                bool(wall.get("ok")),
                f"min {wall.get('min_thickness')} mm at {wall.get('at')}, {wall.get('rays')} rays, "
                f"{wall.get('thin_rays')} thin, {wall.get('grazing_rejected')} grazing rejected"
                f"{'' if wall else ' - ' + str(rep.get('reason'))}"))
    if rep.get("ok"):
        again = _tool_report(p, v, Path(stl), force=True)
        out.append(("regeneration is deterministic: same triangle count after deleting the cache",
                    again.get("tris") == rep.get("tris") and again.get("ok"),
                    f"{rep.get('tris')} -> {again.get('tris')} triangles"))
    return out


def _plan_sweep(st) -> float:
    """Total heading change of the tusk in plan, in degrees - the 110-140° of the FERAL spec."""
    head = [math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])) for a, b in zip(st, st[1:])]
    total = 0.0
    for a, b in zip(head, head[1:]):
        d = (b - a + 180.0) % 360.0 - 180.0
        total += d
    return abs(total)


def _char_len() -> float:
    """The part's characteristic length for the scaling law: its longer in-plane extent."""
    # the scaling law's L is the SHORTER in-plane extent of the surface being decorated
    bb = _plate_fp().bounding_box()
    return min(bb.size.X, bb.size.Y)
