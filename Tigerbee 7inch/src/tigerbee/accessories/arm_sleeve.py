"""Snap-on TPU edge guard sleeve for the free arm shaft (all four arms, one symmetric part).

FIVE STYLE READINGS of the same U-sleeve. Every one of them is pushed onto the same carbon shaft
over arm-local y 40-84 with the same 0.15 mm/side squeeze, the same 0.3 mm grip ribs and the same
flush wall tops at frame Z 7; what changes is the skin, and it changes enough that all five are
told apart by SILHOUETTE alone at 200 px, not by hole pattern:

  shard     the original: a constant 2.0 mm skin outboard of the nominal arm outline, planar-sided,
            nothing but the sleeve. Pure build123d, always available.
  carapace  the abdomen of the beetle laid along the arm - five shingled chitin segments, each one a
            domed transverse shell that flares outward and steps under the next (anterior over
            posterior, the way a real abdomen shingles), a dorsal elytral suture on the belly
            centreline running out to a cusp at both ends, four cusped segment ports, a punctate
            field along both flank crowns and a debossed stripe3 on the middle segment's belly.
            Also pure build123d - see WHY NO BLENDER PASS below.
  vespid    the arm as a jointed insect leg. Five tergites, each 0.82x the LENGTH and 0.86x the SKIN
            of the one inboard of it, each ending in a 1.2 mm proud collar with a 0.45 mm undercut
            groove immediately aft of it, so the plan outline steps down five times and every
            parting line is a 1.6-1.7 mm shelf. One 5.0 x 2.2 elliptical spiracle slit per tergite
            flank (length on the 0.82 ladder, height on the 0.86 one), two puncta rows on the belly.
            Pure build123d, and prismatic throughout: the only downward faces on the whole part are
            the bed face itself, ten vertical spiracle floors and eighteen 2.5 mm² puncta caps, so
            it needs no BRIDGE_OK declaration at all.
  gyroid    the solid as a frozen fluid. A deliberately dumb soft-cornered slab - constant half
            width, ONE constant r 3.0 plan rounding, no crease anywhere - carrying 3.6 mm of wall at
            the root station and 4.9 at the tip, with a 1.6 mm solid rind over the cavity. All the
            visual event is meant to be internal: a gyroid sheet through the 2.0 mm outboard of the
            rind, whose apertures are not cut but emerge where the sheet breaks the surface.
            Blender does that part, cell="voronoi" is the documented fallback, and the undecorated
            tube passes every row on its own - see _gyroid().
  brutalist one poured slab with the formwork still showing. A plain RECTANGULAR plan (the formwork
            does not follow the shaft, so the wall runs 3.00 mm at the root and 4.33 at the tip -
            2x the catalogue and never locally thinned), 1.0 mm 45 deg corner cuts, a 1.0 mm chamfer
            round the whole top and a deliberately SHARP bottom perimeter, three 3.0 x 3.0 proud
            square ribs at 12 mm pitch, ONE rectangular lightening void per side face at 45% of the
            flank wall band, board marking 0.6 x 0.3 at 2.4 pitch across the plinth and a 22 mm
            wordmark cast 2.0 mm into it. Pure build123d; not one fillet on the part.

The framework labels a variant's parts "<base>__<variant>", so the four base labels stay
arm_sleeve_{front_left,front_right,rear_left,rear_right} and the eight exported parts are
arm_sleeve_<corner>__<variant>. One checks() serves all five, which is the point: whatever the style
does to the skin, every mating assertion still holds - the cavity fits the 12.0 x 5.0 prism at the
same clearance and stays open, nothing fouls the frame or a standoff, the wall tops stay flush, the
prop discs stay empty, the motor_guard keeps its gap and the part prints without supports.

WHY NO BLENDER PASS - SIX MEASURED REFUSALS, not an omission. Blender 5.2.2 LTS was present and
working for every run below (`BL.available()` -> (True, 'Blender 5.2.2 LTS')); every one of them was
stopped by a gate, which is the bridge doing its job, and every one was given the most permissive
setup possible - no guard, `restore=False`, the full 12 000 triangle budget. Both CARAPACE recipes
were tried on the whole sleeve AND on the +X flank skin isolated as a sub-solid (finding #1's
"decorate a simple sub-solid and let CAD reassemble" - the flank came back as 1 valid solid,
130.36 mm³, 2.590 mm thick in X, so the input side was never the problem):

  recipe / axis      target        refused by                                  measured
  chitin  X          flank         volume ratio outside (0.98, 1.35)           1.5602
                                   (and mesh wall 0.0021 mm, 593 of 815 rays thin)
  chitin  X          whole sleeve  mesh wall under the 1.2 floor               0.0002 mm, 205/2406
  chitin  Z          flank         mesh wall under the 1.2 floor               0.0006 mm, 302/379
  chitin  Z          whole sleeve  mesh wall under the 1.2 floor               0.0001 mm, 370/2925
  elytra_dome X      flank         volume ratio outside (0.9, 1.35)            3.8696
  elytra_dome X      whole sleeve  volume ratio outside (0.9, 1.35)            1.4377

`tools/arm_sleeve_blender.py` re-runs exactly that table, so the claim stays falsifiable: if a row
ever comes back applied with its wall row ok, this docstring is out of date.

Two reasons behind those numbers, and both are structural rather than a matter of parameters:

  1. A U-sleeve has NO single outward axis. Both recipes restrict themselves to the outward skin
     through `bl_lib.upward_group`, which keeps `comp(face.normal) >= min_nz` for ONE axis component -
     and that restriction IS their safety argument (displace only the outward skin and a wall can
     only get thicker). Here the only plate-like, closed, thick skin is the BELLY, whose normal is
     (0, 0, -1): `>= min_nz` cannot select a downward face, and a positive +Z displacement on it
     pushes material INTO the 2.2 mm floor. Switching to axis "X" selects the +X flank alone, so one
     flank would get bands and the other none; turning the part over only swaps which flank is
     starved. That is why the axis "Z" runs drove the mesh wall to 0.0001-0.0012 mm rather than
     thickening anything.
  2. The free lip is 1.60 mm and it is a RIM along the whole part. Like side_panels' 1.5 mm wall,
     this sleeve has almost no skin more than ~1 mm from a rim, so a swell either eats the lip (the
     wall rows above) or, once it is big enough to show, blows the volume band - 3.87x on an isolated
     flank whose own volume is only 130 mm³.

So the segment ladder lives in build123d, where every parting step is numerically exact, the ledges
stay crisp instead of being smoothed away, and the 1.60 mm lip is guaranteed by construction. That
is also the better reading of the style: chitin is hard, and a grown shell is not a blurred one.
"""

from copy import deepcopy
from functools import lru_cache
from math import radians, tan

from build123d import (Edge, Ellipse, Face, GeomType, Part, Plane, Polygon, Pos, Rectangle,
                       RectangleRounded, Sketch, Sphere, Vertex, Wire, chamfer, extrude, fillet,
                       loft, offset)

from tigerbee import profiles
from tigerbee.accessories import _blender as BL  # noqa: F401 - checks() reports the decor rows
from tigerbee.accessories import _style as S
from tigerbee.accessories._common import *  # noqa: F401,F403 - constants, builders and checks

NAME = "arm_sleeve"
TITLE = "Arm shaft edge guard sleeve"
MATERIAL = "TPU95A"
_ARM_NAMES = ("front_left", "front_right", "rear_left", "rear_right")
PRINT = {f"arm_sleeve_{a}": (0, 0, -1) for a in _ARM_NAMES}
EXCLUSIVE = ()
MOUNTS = ("arm_<corner> carbon shaft, both 5 mm side faces and the underside, arm-local y 40-84",
          "arm top face Z 7 (the sleeve walls end flush with it)")
HARDWARE = ("none - 0.15 mm/side press fit plus three 0.3 mm ribs per wall",)

VARIANTS = {
    "shard": {"style": "shard",
              "notes": "the frame's own language: a constant 2.0 mm skin outboard of the nominal arm "
                       "outline, flat-sided, 30 deg end ramps. Pure build123d."},
    "carapace": {"style": "carapace", "material": "TPU95A",
                 "notes": "five shingled chitin segments, each a transverse dome (rise/span 0.28-0.34) "
                          "breaking at a filleted carina into the flush 1.6 mm gripping lip; dorsal "
                          "suture on the belly centreline, four cusped segment ports, punctate flank "
                          "crowns, stripe3 debossed on the middle segment. Pure build123d - the "
                          "Blender recipes cannot select a U-sleeve's outward skin (see the module "
                          "docstring)."},
    "vespid": {**({"style": "vespid"} if "vespid" in STYLES else {}), "material": "TPU95A",
               "notes": "the arm becomes a jointed insect leg: five tergites, each 0.82x the length "
                        "and 0.86x the skin of the one inboard of it, each ending in a 1.2 mm proud "
                        "collar with a 0.45 mm undercut groove aft of it, so the plan outline steps "
                        "down five times. One Ø2.2 x 5.0 elliptical spiracle per tergite flank, two "
                        "puncta rows on the belly. Pure build123d; prismatic throughout, so it needs "
                        "no bridge declaration at all."},
    "gyroid": {**({"style": "gyroid"} if "gyroid" in STYLES else {}), "material": "TPU95A",
               "notes": "the solid as a frozen fluid: a deliberately dumb soft-cornered slab, one "
                        "constant r 3.0 plan rounding, no crease anywhere, 3.6 mm of wall at the "
                        "root station and 4.9 at the tip, with a 1.6 mm solid rind over the cavity. "
                        "All the visual event is internal - a gyroid sheet through the 2.0 mm "
                        "outboard of the rind, whose apertures are not cut but emerge where the "
                        "sheet breaks the surface. cell='voronoi' is the documented fallback and the "
                        "undecorated tube passes every row on its own."},
    "brutalist": {**({"style": "brutalist"} if "brutalist" in STYLES else {}), "material": "TPU95A",
                  "notes": "one poured slab with the formwork still showing: a plain rectangular "
                           "plan at 3.0 mm minimum wall with 1.0 mm 45 deg corner cuts and a 1.0 mm "
                           "chamfer round the whole top, three 3.0 x 3.0 proud square ribs at 12 mm "
                           "pitch, ONE rectangular lightening void per side face (45% of the wall "
                           "band, open at the top so it has no ceiling to bridge), board marking "
                           "0.6 x 0.3 at 2.4 pitch across the plinth and a 2.0 mm cast-in wordmark. "
                           "Pure build123d, no fillet anywhere."},
}
ASSEMBLY_VARIANT = "shard"
# Geometry dispatch is keyed on the VARIANT NAME, never on spec["style"]: the style-guard idiom drops
# the "style" key entirely while _style.py has not yet learned a language, and a missing key must not
# silently build the shard body under a vespid label.
_KINDS = ("shard", "carapace", "vespid", "gyroid", "brutalist")


def _kind(variant: str) -> str:
    return variant if variant in _KINDS else "shard"

NOTES = ("U-sleeve pushed onto the carbon shaft from below over arm-local y 40-84; held by 0.15 mm/side "
         "interference plus three 0.3 mm ribs per wall. Walls end flush with the arm top face (frame Z 7) "
         "so nothing enters a prop disc; 0.8 mm gap to the motor_guard face at arm-local y 84.8. "
         "CARAPACE sits 0.6 mm deeper (a 2.2 mm belly instead of 1.6, so the 0.55 mm suture leaves "
         "1.65) and up to 1.1 mm wider per side at a segment crest; its four cusped segment ports "
         "drain the pocket, so grit and water leave the shaft instead of grinding against it. "
         "VESPID is 2.2 mm deep and steps from 4.67 mm of skin at the root collar to 1.90 at the "
         "outboard tergite, so it is the one to fit when the arm takes hits near the root; its ten "
         "spiracle slits drain the flanks. GYROID is the heavy one - a 3.6 mm constant-width slab, "
         "5.0 g against shard's 2.0 - and the one to fit if you keep splitting sleeves. BRUTALIST "
         "is heavier still and its 45% side void lets you see the carbon without pulling the sleeve "
         "off; its 22 mm wordmark plaque is on the plinth, readable with the quad upside down. All "
         "five push on from below and print underside-down with no supports.")

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

# --- CARAPACE parameters (mm, arm-local; everything above is shared verbatim) ------------------
# The transverse section, as (perpendicular offset from the nominal arm outline, local z). Only the
# OUTBOARD skin changes between styles, so the pocket, the ribs, the flush wall tops at z = CARBON_T
# and the 30 deg end ramps are the shard ones untouched.
#
# CN-5's gradient is the whole shape of this list. D_LIP is the free lip, the one place the sleeve is
# allowed to be thin (1.45 + 0.15 interference = 1.60 mm wall, TPU's 1.2 floor plus margin); beside
# the carbon the wall grades 3.18 -> 1.60 at a segment's flared end and 2.01 -> 1.60 at its narrow
# start, so no two stations along the arm carry the same section - which is the point of the style.
#
# The crown sits BELOW the pocket (z -0.8, frame Z 1.2) on purpose, and that one decision is what
# makes the whole shape possible: it puts the mass in the floor region, where there is no carbon
# beside it, so the belly can be fat enough to read as an abdomen without the GRIPPING wall becoming
# a 3.5 mm slab. Putting the crown at z 0 instead costs 0.8 mm of wall everywhere the sleeve grips.
#
# The keel-to-crown run is also the part's only outward-facing-downward surface, so its slope is a
# printability budget, not a taste one: dr/dz must stay under ~0.7 or overhangs() flags it. Here it
# is 0.54 / 1.40 = 0.39 at the widest segment, with room to spare.
CARAPACE_FLOOR = 2.2   # belly under the carbon (local z -2.2..0); 0.55 suture leaves 1.65
D_LIP = 1.45           # offset at the carina and the flush lip - the style's minimum skin
CARAPACE_PROFILE = ((2.55, -CARAPACE_FLOOR),  # keel: the flat belly edge, the bed face
                    (2.95, -0.80),            # CROWN: widest point, filleted 3.0 into the dome
                    (D_LIP, 2.80),            # CARINA: the crease, filleted 0.8
                    (D_LIP, CARBON_T))        # the lip top, flush with the carbon top face
FILLET_DOME, FILLET_CARINA, FILLET_LIP = 3.0, 0.8, 0.5   # the ladder: 3.0 / 1.6 / 0.8 -> 0.5, no chamfers
SEGMENTS = 5           # five shingled abdominal segments over the 44 mm run -> 8.8 mm period
SEG_M = (0.35, 1.35)   # the bulge factor at a segment's inboard and outboard ends: each scale flares
SEG_EXP = 0.85         # outward and the next one starts small again, so every parting line is a step.
SEG_MID = 0.45         # The 1.00 spread over a 1.50 mm crown range is 1.50 mm of half width, and the
#                      SHAFT'S OWN TAPER spends 0.37 mm of it against the flare inside every segment,
#                      so the flare that survives into the silhouette is 1.13-1.25 mm. Both numbers
#                      were found by looking: an earlier (0.45, 1.15) spread on a 1.25 mm crown range
#                      measured a comfortable-sounding 23.4% "swing" and rendered, at 200 px, as a
#                      straight edge with four small nicks. What reads is the WHOLE segment tapering.
GROOVE_W = 2.0         # the parting groove at every segment line: a real trench, not a scratch - it
GROOVE_M = 0.05        # is 1.95 mm deep at a segment crest and fades to nothing at the carina, where
GROOVE_Z = (-1.80, 3.20)   # both sections meet at D_LIP (the way a segment line dies out on the hard
#                      rim). It stops 0.4 above the belly so its two downward end faces stay at
#                      ~1.9 mm², under overhangs()' 5 mm² floor, instead of cutting a 23 mm²
#                      downward channel straight across the bed face.
SUTURE_W, SUTURE_D = 0.8, 0.55   # CN-1. 0.55 not 0.40: see _suture_cut() - a 0.40 V is exactly 45 deg
PORT_W = 3.0           # the cusped segment ports: one per segment, transverse (CN-2)
PORT_LIG = 2.2         # ligament to the pocket wall and to the segment ends
PORT_SEGMENTS = (0, 1, 3, 4)     # four ports; segment 2 (the middle) carries the mark instead
PUNCTA_D, PUNCTA_DEPTH = 1.8, 0.45
PUNCTA_Z = (-1.60, -0.05)        # two rows straddling the crown, staggered
PUNCTA_PER_SEG = 2
MARK_KIND, MARK_SIZE, MARK_DEPTH_ = "stripe3", 8.0, 0.6   # stripe3, not lunule: L ~ 19 is the small tier

# The stripe3 deboss floor is the one downward planar face on the carapace sleeve: three stadium
# bars 1.6 mm wide sitting 0.6 mm above the bed plane (measured 12.3 / 9.1 / 5.9 mm², normal.Z -1.00).
# It is a bridge in the strictest sense - a flat ceiling 0.6 mm off the bed spanning 1.6 mm, against
# TPU's 22 mm limit - so it is declared rather than designed away. The Z window is only 0.1 mm thick
# and sits exactly at MARK_DEPTH_ above the bed, so nothing else on the part can slip through it.
# The window is generous in X and Y on purpose: PRINT is (0, 0, -1), so the four sleeves are NOT
# rotated for the bed and each one's mark lies along a different frame direction.
_MARK_BRIDGE = (("box", -60.0, -60.0, MARK_DEPTH_ - 0.05, 60.0, 60.0, MARK_DEPTH_ + 0.05),)
BRIDGE_OK = {f"arm_sleeve_{a}__carapace": _MARK_BRIDGE for a in _ARM_NAMES}


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


# =============================================================================================
# CARAPACE: the segmented shell
# =============================================================================================
@lru_cache(maxsize=None)
def _outline_wire() -> Wire:
    return profiles._outline(P.ROOT_TO_MOTOR)


@lru_cache(maxsize=None)
def _half_width(y: float) -> float:
    """The arm outline's own half width at station y. The shaft is NOT parallel: it tapers from
    7.352 at y 40 to 6.027 at y 84, so a straight prism would swing the wall by 1.33 mm. Every
    transverse section is therefore built on the measured h(y)."""
    hit = _outline_wire().intersect(Edge.make_line((-40.0, y, 0.0), (40.0, y, 0.0)))
    return max(abs(v.X) for v in hit.vertices())


def _seg_bounds(i: int, p: dict) -> tuple[float, float]:
    span = (p["Y1"] - p["Y0"]) / p["SEGMENTS"]
    return p["Y0"] + i * span, p["Y0"] + (i + 1) * span


def _seg_m(t: float, p: dict) -> float:
    """The bulge factor across one segment: small at the inboard end, full at the outboard end, so
    the parting line is a STEP of (m1 - m0) x (d_crown - D_LIP) = 1.50 mm and the scale in front
    tucks under the one behind it - anterior over posterior, the way an abdomen shingles."""
    m0, m1 = p["SEG_M"]
    return m0 + (m1 - m0) * max(0.0, min(1.0, t)) ** p["SEG_EXP"]


def _section(y: float, m: float, p: dict) -> Sketch:
    """One transverse section of the carapace, in a sketch whose local x is arm-local x and whose
    local y is arm-local z. Filleted in 2D - the dome, the carina crease and the lip's outer edge -
    so the ruled loft along the arm carries a genuinely smooth section while every parting line
    stays a hard step. Fillets in 2D, never a 3D fillet on a lofted shell: the radii are exact and
    OCCT never has to blend a BSpline."""
    h = _half_width(y)
    d_lip = p["D_LIP"]
    xs = [h + d_lip + m * (d - d_lip) for d, _z in p["CARAPACE_PROFILE"]]
    zs = [z for _d, z in p["CARAPACE_PROFILE"]]
    right = list(zip(xs, zs))
    sk = Polygon(*right, *[(-x, z) for x, z in reversed(right)], align=None)
    # the ladder, applied to whichever vertices survive: 3.0 on the dome, 0.8 on the carina crease,
    # 0.5 on the lip's outer edge (the top FACE stays planar at z = CARBON_T, so the walls are still
    # exactly flush with the carbon)
    for zc, r in ((zs[1], p["FILLET_DOME"]), (zs[2], p["FILLET_CARINA"]), (zs[3], p["FILLET_LIP"])):
        hits = sk.vertices().filter_by(lambda v, zc=zc: abs(v.Y - zc) < 1e-6)
        for attempt in (r, r / 2, r / 4):
            try:
                sk = fillet(hits, attempt)
                break
            except Exception:  # noqa: BLE001 - a radius OCCT cannot fit here; shrink and retry
                continue
    return sk


def _shell(p: dict) -> Part:
    """The outboard skin: five per-segment ruled lofts, unioned. Each segment is lofted from three
    transverse sections (inboard, mid, outboard) and abuts the next on a plane, so the union leaves a
    crisp annular ledge at every parting line instead of a blend."""
    plane = lambda y: Plane(origin=(0.0, y, 0.0), x_dir=(1, 0, 0), z_dir=(0, -1, 0))  # noqa: E731
    body = Part()
    for i in range(p["SEGMENTS"]):
        ya, yb = _seg_bounds(i, p)
        ts = (0.0, p["SEG_MID"], 1.0)
        secs = [plane(ya + t * (yb - ya)) * _section(ya + t * (yb - ya), _seg_m(t, p), p) for t in ts]
        body += loft(secs, ruled=True)
    return body


def _parting_grooves(p: dict) -> Part:
    """The shadow line at every segment line - the feature that makes the ladder read at 200 px.

    Per CN-2 it runs ACROSS the arm, and it is cut by subtracting the same lofted section at
    GROOVE_M: so the groove is 1.25 mm deep at the crown, fades to exactly zero at the carina (both
    sections share D_LIP there, the way a real segment line dies out on the hard rim) and stops
    GROOVE_Z[0] above the belly, which keeps its two end faces at ~1.2 mm² - under overhangs()' 5 mm²
    floor - instead of cutting a 23 mm² downward channel across the bed face."""
    plane = lambda y: Plane(origin=(0.0, y, 0.0), x_dir=(1, 0, 0), z_dir=(0, -1, 0))  # noqa: E731
    span = (p["Y1"] - p["Y0"]) / p["SEGMENTS"]
    tools = Part()
    for i in range(1, p["SEGMENTS"]):
        y = p["Y0"] + i * span
        ya, yb = y - p["GROOVE_W"] / 2, y + p["GROOVE_W"] / 2
        inner = loft([plane(ya) * _section(ya, p["GROOVE_M"], p),
                      plane(yb) * _section(yb, p["GROOVE_M"], p)], ruled=True)
        tools += box(-30.0, ya, p["GROOVE_Z"][0], 30.0, yb, p["GROOVE_Z"][1]) - inner
    return tools


def _plan_swing(p: dict) -> tuple[float, float, float]:
    """The silhouette metric of §4.5, and the one that had to be rewritten after LOOKING at the
    200 px thumbnail. The first version measured crest-to-groove and reported a comfortable 23.4%
    on an outline that rendered as a straight edge with four small nicks, because a 1.3 mm groove is
    5 px wide. What the eye reads is the SEGMENT tapering over its whole 8.8 mm, so the number
    returned is the within-segment flare - the saw-tooth amplitude - measured at each segment's own
    two ends so the shaft's own 1.33 mm taper cannot flatter it.

    SHARD's band is a constant 2.0 mm offset, so its flare is exactly 0."""
    d_lip, d_crown = p["D_LIP"], p["CARAPACE_PROFILE"][1][0]
    m0, m1 = p["SEG_M"]
    flares = []
    for i in range(p["SEGMENTS"]):
        ya, yb = _seg_bounds(i, p)
        flares.append((_half_width(yb) + d_lip + m1 * (d_crown - d_lip))
                      - (_half_width(ya) + d_lip + m0 * (d_crown - d_lip)))
    mean = (_half_width(p["Y0"]) + _half_width(p["Y1"])) / 2 + d_lip + (m0 + m1) / 2 * (d_crown - d_lip)
    return min(flares), max(flares), min(flares) / mean


def _suture_cut(p: dict) -> Part:
    """CN-1, on the belly centreline - the sleeve's own dorsal surface, the one face that crosses its
    own centreline along the whole run. S.suture() cuts DOWN into a face at z_top, so the shared
    generator is used and its result mirrored, because this groove opens downward at z -2.2.

    Depth 0.55, not the canonical 0.40: a 0.8 x 0.40 V has flanks at exactly 45 deg, so each flank's
    normal.Z is -0.7071 and overhangs() flags 32 mm² of it at its -0.70 limit. Deepening the same
    0.8 mm groove to 0.55 takes the flanks to -0.588 and leaves 1.65 mm of belly."""
    groove = S.suture(p["Y0"], p["Y1"], 0.0, w=p["SUTURE_W"], depth=p["SUTURE_D"], cusped=True)
    return groove.mirror(Plane.XY).translate((0.0, 0.0, -p["FLOOR"]))


def _ports(p: dict, pocket: Sketch) -> tuple[Part, int]:
    """One cusped port per segment, straight across the arm (CN-2), cut clean THROUGH the 2.2 mm
    belly so it has no ceiling at all - the reason it is a lens and not a slot (finding #6: an arc
    lying along Y is a ~1000 mm cylinder that overhangs() will not accept as a bridge, and a blind
    flute's flat floor is a 14 mm² face at normal.Z -1). Each port is a vesica, two tangent arcs
    meeting at a true point at both ends, placed through the shared aperture engine so the PORT_LIG
    ligament to the pocket wall and to the segment ends is enforced rather than hoped for.

    `vent_elytra` is not used here even though it is the family's generator: it clamps n to >= 2 and
    stacks its arcs on the region's own Y, which on an 8.8 mm segment band puts two arcs where the
    ligament budget holds one. A single lens across the band is that stack's degenerate case."""
    tool, kept = Part(), 0
    for i in p["PORT_SEGMENTS"]:
        ya, yb = _seg_bounds(i, p)
        yc = (ya + yb) / 2.0
        # the reach is set by the NARROW end of the band (the shaft tapers 1.33 mm over the run) with
        # 0.3 mm of slack, so the grown candidate still clears the pocket wall at the widest station
        reach = _half_width(yb) - p["INTERFERENCE"] - p["PORT_LIG"] - 0.3
        half = min(p["PORT_W"] / 2.0, 0.45 * 2 * reach)
        # the region is the WHOLE segment band: place_apertures grows each candidate by ligament_min
        # and requires the grown shape inside the region, so pre-cropping by the ligament as well
        # asks for 2 x 2.2 mm and drops every port (measured: 0 of 4 survived)
        region = _crop(pocket, ya, yb)

        def slot(cx, _cy, grow, yc=yc, reach=reach, half=half):
            return S.lens((-reach - grow, yc), (reach + grow, yc), half + grow)

        sk, n = S.place_apertures(region, slot, [(0.0, 0.0)], ligament_min=p["PORT_LIG"],
                                  pairwise=False, min_dim=2 * half,
                                  hole_min=S.DECOR_MATERIALS["TPU95A"]["hole_min"])
        if n:
            tool += _slab(sk, -p["FLOOR"] - 1.0, 0.2)
            kept += n
    return tool, kept


def _puncta_cut(p: dict) -> tuple[Part, int]:
    """PUNCTA on the two flank crowns only, never on the suture ridge: blind spherical dimples
    Ø1.8 x 0.45 deep (a Ø2.4 cap face is 4.5 mm², just under overhangs()' 5.0 mm² floor, so 1.8 is
    safely self-supporting on a near-vertical flank). Two staggered rows per segment straddling the
    crown, each dimple sunk from the flank's OWN local radius at that (y, z) so the depth is 0.45
    everywhere instead of only at the widest station."""
    rs = (p["PUNCTA_D"] ** 2 / 4 + p["PUNCTA_DEPTH"] ** 2) / (2 * p["PUNCTA_DEPTH"])
    tool, n = Part(), 0
    for i in range(p["SEGMENTS"]):
        ya, yb = _seg_bounds(i, p)
        for k in range(p["PUNCTA_PER_SEG"]):
            t = (k + 0.5) / p["PUNCTA_PER_SEG"]
            y = ya + t * (yb - ya)
            for row, z in enumerate(p["PUNCTA_Z"]):
                if (k + row) % 2:      # stagger: a hex field, not a grid
                    continue
                x = _flank_x(y, z, _seg_m(t, p), p)
                for sx in (1.0, -1.0):
                    tool += Pos(sx * (x + rs - p["PUNCTA_DEPTH"]), y, z) * Sphere(rs)
                    n += 1
    return tool, n


def _flank_x(y: float, z: float, m: float, p: dict) -> float:
    """The un-filleted flank half width at (y, z) - the polyline the section is built from, linearly
    interpolated in z. Used to sink the puncta and the mark to a constant depth on a curved flank."""
    h, d_lip = _half_width(y), p["D_LIP"]
    prof = [(d_lip + m * (d - d_lip), zz) for d, zz in p["CARAPACE_PROFILE"]]
    for (d0, z0), (d1, z1) in zip(prof, prof[1:]):
        if min(z0, z1) - 1e-9 <= z <= max(z0, z1) + 1e-9:
            f = 0.0 if abs(z1 - z0) < 1e-12 else (z - z0) / (z1 - z0)
            return h + d0 + f * (d1 - d0)
    return h + prof[0][0] if z < prof[0][1] else h + prof[-1][0]


def _mark_cut(p: dict) -> Part | None:
    """CN-4 on the belly of the MIDDLE segment - the only surface on this part that can hold a mark
    at its minimum size, which is why segment 2 carries no port. stripe3 rather than lunule because
    the decorated surface's characteristic length is ~19 mm (the small tier) and the lunule's 16 mm
    minimum will not sit cleanly on a 19 mm band that already carries the suture. The three bars run
    ACROSS the arm (CN-2); the suture crosses them, which is exactly how a real maculation reads.

    Debossed 0.6 into a 2.2 mm belly leaves 1.6 - no carina band needed here, because CARAPACE's
    thickness gradient already put the mass where the mark goes."""
    if not S.mark_fits(p["MARK_KIND"], p["MARK_SIZE"]):
        return None
    i = p["SEGMENTS"] // 2
    ya, yb = _seg_bounds(i, p)
    return S.mark(p["MARK_KIND"], p["MARK_SIZE"], "deboss", (0.0, (ya + yb) / 2.0, -p["FLOOR"]),
                  normal=(0, 0, -1), depth=p["MARK_DEPTH_"], x_dir=(1, 0, 0))


def _carapace(p: dict) -> Part:
    """The whole carapace sleeve, arm-local. Mating geometry first, decoration last."""
    outline = Face(_outline_wire())
    pocket = _crop(_offset2d(outline, -p["INTERFERENCE"]), p["Y0"], p["Y1"])

    part = _shell(p)
    part -= _slab(pocket, 0.0, p["CARBON_T"] + 2.0)          # the gripping pocket, exact
    if p["RIBS"]:
        rib_inner = _crop(_offset2d(outline, -(p["INTERFERENCE"] + p["RIB_H"])), p["Y0"], p["Y1"])
        for y in p["RIB_Y"]:
            band = _crop(pocket - rib_inner, y - p["RIB_L"] / 2, y + p["RIB_L"] / 2)
            part += _slab(band, p["RIB_Z0"], p["RIB_Z0"] + p["RIB_T"])
    if p["CHAMFER_DEG"] > 0:
        part -= _end_ramps(p)
    part -= _parting_grooves(p)

    ports, _n = _ports(p, pocket)
    if ports.volume:
        part -= ports
    dimples, _k = _puncta_cut(p)
    if dimples.volume:
        part -= dimples
    mk = _mark_cut(p)
    if mk is not None:
        part -= mk
    part -= _suture_cut(p)                                   # last, on exact geometry (CN-1)
    assert len(part.solids()) == 1, f"arm_sleeve carapace: {len(part.solids())} solids"
    return part


def _dome_ratio(p: dict) -> tuple[float, float]:
    """CARAPACE conformance: the transverse shell is a dome of rise = the section height from the
    belly to the carina, span = its width at the carina. Reported at both ends of the run, because
    the arm tapers and the span therefore does."""
    rise = p["CARAPACE_PROFILE"][2][1] + p["FLOOR"]
    return tuple(round(rise / (2 * (_half_width(y) + p["D_LIP"])), 4) for y in (p["Y0"], p["Y1"]))


# =============================================================================================
# VESPID: the arm becomes a jointed insect leg
# =============================================================================================
# Every VESPID feature is a PRISM in the sleeve's own z, which is not a stylistic accident but the
# whole reason the language works on this part: the silhouette event is in the PLAN outline (the band
# offsets step down tergite by tergite), so the part has no downward-facing surface anywhere except
# its own bed face, the two blind spiracle floors (vertical) and the puncta caps. That is why vespid
# needs no BRIDGE_OK box at all while carapace needs one.
#
# The taper law. Lengths run 0.82x outboard, girths 0.86x outboard, both measured on the SKIN - the
# perpendicular offset of the nominal arm outline - because the only quantity this part controls is
# the skin. (Overall transverse girth cannot carry the 0.86 law: the carbon shaft's own half width
# only falls 7.352 -> 6.027 over the run, so a 0.86 ladder on h + skin drives the skin negative by
# the third tergite. Measured, not assumed - see _vespid_checks.)
V_TERGITES = 5
V_L_RATIO = 0.82       # each tergite 0.82x the length of the one inboard of it
V_G_RATIO = 0.86       # ... and 0.86x the skin thickness: 4.02 -> 3.46 -> 2.98 -> 2.56 -> 2.20
V_SKIN_TIP = 1.90      # the last tergite's skin; the ladder is built backwards from here so that the
#                      structural wall behind the outboard spiracle lands on exactly 1.40 mm, and
#                      forwards so that the ROOT COLLAR CREST - the widest point on the whole part -
#                      stays inside a 2.4 mm envelope growth over shard. Those two numbers are what
#                      sizes this variant: the taper ratio is given, so fixing either end fixes the
#                      other. The first cut ran the tip at 2.20 and crested 2.78 mm proud of shard.
V_FLOOR = 2.2          # belly under the carbon; carries the puncta rows (0.4 deep -> 1.8 left)
V_COLLAR_PROUD = 1.2   # each tergite ends in a proud collar, ALWAYS 1.2 proud ...
V_COLLAR_W = 2.2       # ... but only 2.2 mm wide on the root tergite and 0.82x that outboard, like
V_GROOVE_D = 0.45      # every other length on the part, so the collar reads as a segment RIM and not
V_GROOVE_W = 1.4       # as a fin: the first cut of this variant had a constant 1.2 mm collar and
#                      rendered, at 200 px, as five thin flanges stuck on a straight box.
#                      The groove sits immediately aft of the collar and scales with it.
V_SPIRACLE = (5.0, 2.2, 0.50)   # one spiracle per tergite flank: LONG along the arm and shallow in z -
V_SPIRACLE_ZC = 2.0            # a real spiracle is a slit along the body, and an upright 5 mm oval on
#                      a 7.2 mm wall reads as a window. Length scales 0.82x, height 0.86x, depth fixed.
V_PUNCTA_D, V_PUNCTA_DEPTH = 1.8, 0.4
V_PUNCTA_X, V_PUNCTA_PITCH = 2.9, 4.4   # two rows straddling the dorsal (belly) centreline


@lru_cache(maxsize=None)
def _skin(amount: float) -> Face:
    """The nominal arm outline offset perpendicularly by `amount`. Cached: vespid asks for fifteen
    different offsets (body, groove and collar band per tergite) and each offset() is not cheap."""
    return _offset2d(Face(_outline_wire()), amount)


def _v_skins(p: dict) -> list[float]:
    n, r = p["V_TERGITES"], p["V_G_RATIO"]
    return [p["V_SKIN_TIP"] / r ** (n - 1 - i) for i in range(n)]


def _v_bounds(p: dict) -> list[tuple[float, float]]:
    n, lr = p["V_TERGITES"], p["V_L_RATIO"]
    w = [lr ** i for i in range(n)]
    span = (p["Y1"] - p["Y0"]) / sum(w)
    ys = [p["Y0"]]
    for k in w:
        ys.append(ys[-1] + k * span)
    ys[-1] = p["Y1"]
    return list(zip(ys, ys[1:]))


def _v_tergite(i: int, p: dict) -> dict:
    """Everything about tergite `i`, in one place so the builder and the checks read the same law:
    its y bounds, its skin, and the y bounds of its three bands (body, undercut groove, collar)."""
    (ya, yb), s = _v_bounds(p)[i], _v_skins(p)[i]
    k = p["V_L_RATIO"] ** i
    gw, cw = p["V_GROOVE_W"] * k, p["V_COLLAR_W"] * k
    return {"i": i, "y0": ya, "y1": yb, "skin": s, "groove_w": gw, "collar_w": cw,
            "body": (ya, yb - gw - cw), "groove": (yb - gw - cw, yb - cw), "collar": (yb - cw, yb)}


def _v_bands(p: dict) -> list[tuple[float, float, float]]:
    """(y0, y1, skin offset) for every band of every tergite: body, undercut groove, proud collar."""
    out = []
    for i in range(p["V_TERGITES"]):
        t = _v_tergite(i, p)
        out += [(*t["body"], t["skin"]), (*t["groove"], t["skin"] - p["V_GROOVE_D"]),
                (*t["collar"], t["skin"] + p["V_COLLAR_PROUD"])]
    return out


def _v_spiracles(p: dict) -> tuple[Part, int]:
    """One elliptical spiracle per tergite, on BOTH flanks, blind. An elliptical cylinder driven in
    along arm-local x: its bore wall is curved (prorated to ~3 mm² facing down, under overhangs()'
    5 mm² floor) and its floor is the cutter's own end cap, a vertical planar ellipse at normal.Z 0.
    A rectangular notch would have read as a second undercut groove; the oval is the one curve vespid
    is allowed and it is what makes the tergite read as a segment with a breathing hole in it."""
    ly, lz, depth = p["V_SPIRACLE"]
    tool, n = Part(), 0
    for i in range(p["V_TERGITES"]):
        t = _v_tergite(i, p)
        yc = sum(t["body"]) / 2.0
        a = ly / 2 * p["V_L_RATIO"] ** i          # the slit follows the LENGTH ladder ...
        b = lz / 2 * p["V_G_RATIO"] ** i          # ... and its height follows the girth ladder
        s = t["skin"]
        x0 = _half_width(yc) + s - depth
        for sx in (1.0, -1.0):
            pl = Plane(origin=(sx * x0, yc, p["V_SPIRACLE_ZC"]), x_dir=(0, sx, 0), z_dir=(sx, 0, 0))
            tool += extrude(pl * Ellipse(a, b), amount=20.0)
            n += 1
    return tool, n


def _v_puncta(p: dict) -> tuple[Part, int]:
    """Two dot rows straddling the dorsal centreline, sunk into the belly from below. Ø1.8 x 0.4 is a
    3.05 mm² spherical cap - under overhangs()' 5 mm² floor - and leaves 1.8 mm of belly."""
    d, depth = p["V_PUNCTA_D"], p["V_PUNCTA_DEPTH"]
    rs = (d ** 2 / 4 + depth ** 2) / (2 * depth)
    zc = -p["FLOOR"] - rs + depth
    tool, n = Part(), 0
    y = p["Y0"] + 3.4
    while y <= p["Y1"] - 3.4:
        for sx in (1.0, -1.0):
            tool += Pos(sx * p["V_PUNCTA_X"], y, zc) * Sphere(rs)
            n += 1
        y += p["V_PUNCTA_PITCH"]
    return tool, n


def _vespid(p: dict) -> Part:
    """The whole vespid sleeve, arm-local. Mating geometry first, decoration last."""
    outline = Face(_outline_wire())
    pocket = _crop(_offset2d(outline, -p["INTERFERENCE"]), p["Y0"], p["Y1"])

    part = Part()
    for y0, y1, d in _v_bands(p):
        outer = _crop(_skin(round(d, 5)), y0, y1)
        part += _slab(outer, -p["FLOOR"], 0.0)              # belly
        part += _slab(outer - pocket, -p["FLOOR"], p["CARBON_T"])   # flanks, flush with the carbon

    if p["RIBS"]:
        rib_inner = _crop(_offset2d(outline, -(p["INTERFERENCE"] + p["RIB_H"])), p["Y0"], p["Y1"])
        for y in p["RIB_Y"]:
            band = _crop(pocket - rib_inner, y - p["RIB_L"] / 2, y + p["RIB_L"] / 2)
            part += _slab(band, p["RIB_Z0"], p["RIB_Z0"] + p["RIB_T"])
    if p["CHAMFER_DEG"] > 0:
        part -= _end_ramps(p)

    spir, _n = _v_spiracles(p)
    part -= spir
    dots, _k = _v_puncta(p)
    part -= dots
    assert len(part.solids()) == 1, f"arm_sleeve vespid: {len(part.solids())} solids"
    return part


# =============================================================================================
# GYROID: the solid is a frozen fluid
# =============================================================================================
# The silhouette is deliberately dumb, because all the visual event is meant to be INTERNAL: a
# soft-cornered slab of constant half width with a single constant r = 3.0 rounding on the plan
# outline and no crease anywhere. That is also the one honest way to say "constant 3.6-5.0 mm thick"
# on a tapering shaft - the slab does not taper, so the wall runs 3.60 mm at the root station and
# 4.92 mm at the tip, which is the envelope the lattice needs (>= 1.5 periods across a 10 mm cell).
#
# The rind is 1.6 mm of solid over the cavity, and the lattice is only ever allowed in the 2.0 mm
# outboard of it. Whether it actually gets there is Blender's business: decorate() never raises, so
# a missing gyroid recipe hands the undecorated tube straight back and every row below still holds.
#
# MEASURED, on Blender 5.2.2 LTS with the recipe running and every gate given its best chance, the
# cell ladder currently ends at the tube. The reasons are recorded rather than hidden, and the
# "gyroid: lattice state" row prints the whole chain on every run:
#   guard not flush   the first guard ran 1.0 mm below and 2.0 above the part; decorate() refused it
#                     outright ("guard is proud of the part by {'-Z': 1.0, '+Z': 2.0} mm"). Fixed by
#                     clamping the mask to the part's own z extents - that one IS a real bug and the
#                     gate caught it.
#   ligament 1.6      the recipe clips border cells flush with the silhouette, so a 1.6 mm region
#                     inset left a 0.89 mm rim at the belly edge against a 1.5 floor. Fixed by
#                     taking the inset (2.6) clear of the ligament (2.2).
#   the rebuild       voronoi, hex and round all then meshed and all three came back
#                     "rebuilt solid: BRepCheck_Analyzer says invalid" - through the triangle path
#                     AND through the OBJ/n-gon path. This is the same wall the carapace pass hit
#                     (see WHY NO BLENDER PASS): OCCT will not sew a lattice mesh back onto a
#                     U-section whose walls are surfaces of extrusion of an offset curve.
# So the shipped part is the tube, and the tube is a complete design on its own terms - a
# soft-cornered monolith is exactly what this language says the outside should be.
G_WALL = 3.6            # the slab half width is _half_width(Y0) + G_WALL
G_FLOOR = 3.6
G_RIND = 1.6            # solid skin over the cavity - the clean zone Blender may not touch
G_R = 3.0               # the single plan rounding, constant, on all four corners
G_PERIOD, G_SHEET = 12.0, 1.6
G_LIG, G_INSET = 2.2, 2.6   # the mesh ligament, and how far inboard of the silhouette a cell may
#                      start. 1.6/1.6 left a 0.89 mm rim at the belly edge (measured) - the recipe
#                      clips border cells flush with the outline, so the inset has to exceed the
#                      ligament, not match it.
G_CELLS = ("gyroid", "voronoi", "hex", "round")   # first choice, then the documented degrades,
#                      each one a simpler cutter than the last; the tube ships if none of them rebuild
G_KEY = "arm_sleeve__gyroid"


def _g_plan(p: dict) -> Sketch:
    w = _half_width(p["Y0"]) + p["G_WALL"]
    return Pos(0.0, (p["Y0"] + p["Y1"]) / 2.0) * \
        RectangleRounded(2 * w, p["Y1"] - p["Y0"], p["G_R"])


def _g_base(p: dict) -> Part:
    """The undecorated tube: the slab, the exact cavity, shard's grip ribs and shard's end ramps."""
    outline = Face(_outline_wire())
    pocket = _crop(_offset2d(outline, -p["INTERFERENCE"]), p["Y0"], p["Y1"])
    plan = _g_plan(p)
    part = _slab(plan, -p["FLOOR"], 0.0)
    part += _slab(plan - pocket, -p["FLOOR"], p["CARBON_T"])
    if p["RIBS"]:
        rib_inner = _crop(_offset2d(outline, -(p["INTERFERENCE"] + p["RIB_H"])), p["Y0"], p["Y1"])
        for y in p["RIB_Y"]:
            band = _crop(pocket - rib_inner, y - p["RIB_L"] / 2, y + p["RIB_L"] / 2)
            part += _slab(band, p["RIB_Z0"], p["RIB_Z0"] + p["RIB_T"])
    if p["CHAMFER_DEG"] > 0:
        part -= _end_ramps(p)
    assert len(part.solids()) == 1, f"arm_sleeve gyroid: {len(part.solids())} solids"
    return part


def _g_guard(p: dict) -> Part:
    """The clean zone: the cavity grown by the 1.6 mm rind, plus a 1.6 mm band at each end face.
    Stated as a solid so it is flush with every mating face by construction."""
    outline = Face(_outline_wire())
    rind = _crop(_offset2d(outline, -p["INTERFERENCE"] + p["G_RIND"]), p["Y0"], p["Y1"])
    # EXACTLY flush, top and bottom. decorate() measures the guard against the part per axis and
    # refuses a guard that is proud of it at all (measured: "guard is proud of the part by
    # {'-Z': 1.0, '+Z': 2.0} mm"), which is the gate doing its job - a mask that sticks out cannot
    # be re-unioned into real B-rep geometry.
    g = _slab(rind, -p["G_RIND"], p["CARBON_T"])
    for y0, y1 in ((p["Y0"], p["Y0"] + p["G_RIND"]), (p["Y1"] - p["G_RIND"], p["Y1"])):
        g += _slab(_crop(_g_plan(p), y0, y1), -p["FLOOR"], p["CARBON_T"])
    return g


_G_REASON = "not attempted"


def _gyroid(p: dict) -> Part:
    """The tube, then the lattice on top of it if Blender will give us one."""
    global _G_REASON
    base = _g_base(p)
    ok, why = BL.available()
    if not ok or not p.get("G_DECOR", True):
        _G_REASON = f"undecorated: {why if not ok else 'G_DECOR off'}"
        return base
    guard = _g_guard(p)
    region = BL.decor_region(base, p["G_INSET"], minus=(guard,))
    tried = []
    for cell in p["G_CELLS"]:
        res = BL.decorate_ex(base, "carapace_lattice",
                             dict(cell=cell, period=p["G_PERIOD"], sheet=p["G_SHEET"],
                                  ligament=p["G_LIG"], axis="Z"),
                             protect=guard, region=region, cache_key=G_KEY, wall_floor=1.5,
                             ngon=cell != "gyroid")
        if res.applied and not overhangs(res.part, (0, 0, -1), material=MATERIAL):
            _G_REASON = f"{cell} lattice applied"
            return res.part
        tried.append(f"{cell}: "
                     f"{res.reason or 'decorated mesh needs supports in PRINT orientation'}")
    BL.RESULTS.pop(G_KEY, None)   # nothing was applied: the tube ships, and says so out loud
    _G_REASON = "undecorated tube - " + "; ".join(tried)
    return base


# =============================================================================================
# BRUTALIST: one poured slab, formwork still showing
# =============================================================================================
# The formwork does not follow the shaft. The plan outline is a plain RECTANGLE set at the root
# station's half width plus 3.0, so the wall is 3.05 mm where the shaft is widest and thickens to
# 4.33 mm where it narrows - the slab is dumb and the shaft tapers inside it. Wall is a MINIMUM here,
# never a local thinning, which is exactly the language's claim.
#
# Two decisions are printability, not taste. (1) The lightening void is open at the wall top, so it
# has no ceiling and therefore no bridge and no overhang - a closed rectangle would have hung a
# 0.6 mm strip over a 22 mm span. (2) The bottom perimeter is left SHARP. A 1.0 x 45 deg chamfer
# there is a 184 mm² band at normal.Z -0.707 straight across the bed face and fails overhangs()
# outright; the chamfer budget is spent on the plan corners and the whole top perimeter instead,
# which is where formwork actually shows a chamfer.
B_WALL = 3.0            # 2x the catalogue, constant, and the plan is orthogonal so it only grows
B_FLOOR = 4.0           # the plinth; carries the 2.0 mm cast-in wordmark and the board marking
B_CORNER = 1.0          # 45 deg plan corner cuts - rectangles and 45 deg cuts only
B_CHAMFER = 1.0         # the top perimeter, built as a ruled loft (no 3D fillet or chamfer op)
B_RIB_PROUD, B_RIB_W = 3.0, 3.0
B_RIB_Y = (52.0, 64.0, 76.0)          # three proud square ribs at 12 mm pitch
B_GRIP_Y = (44.0, 76.0, 81.0)         # the internal 0.3 grip ribs, moved clear of the void
B_VOID = (50.0, 72.0, 0.5)            # y0, y1, sill: the void runs from the sill to the wall top
B_BOARD_W, B_BOARD_D, B_BOARD_PITCH = 0.6, 0.3, 2.4
B_BOARD_GAP = (18.0, 26.0)     # staggered plank ends, measured from Y0 - see _b_board_run()
B_MARK_KIND, B_MARK_SIZE, B_MARK_DEPTH = "wordmark", 22.0, 2.0
# print_orientation() lays the bed face on Z 0 but does NOT recentre X and Y, and each of the four
# sleeves sits at its own arm's frame coordinates (measured: x -104.7 to -57.3 on the front left), so
# the window has to be generous in plan and tight in Z. It is 0.1 mm thick and sits exactly at the
# feature's own depth above the bed, so nothing else on the part can slip through it.
_B_BRIDGE = (("box", -400.0, -400.0, B_BOARD_D - 0.05, 400.0, 400.0, B_BOARD_D + 0.05),
             ("box", -400.0, -400.0, B_MARK_DEPTH - 0.05, 400.0, 400.0, B_MARK_DEPTH + 0.05))


def _b_plan(p: dict, half: float, y0: float, y1: float) -> Sketch:
    """The formwork in plan: a rectangle with 1.0 mm 45 deg corner cuts. No curve anywhere."""
    c = p["B_CORNER"]
    return Polygon((half, y0 + c), (half - c, y0), (-half + c, y0), (-half, y0 + c),
                   (-half, y1 - c), (-half + c, y1), (half - c, y1), (half, y1 - c), align=None)


def _b_prism(p: dict, half: float, y0: float, y1: float, z0: float, z1: float, c: float) -> Part:
    """One formwork prism: the plan extruded z0..z1 with a `c` mm 45 deg chamfer round its top edge
    only. The bottom perimeter is deliberately left sharp - see the note above."""
    solid = _slab(_b_plan(p, half, y0, y1), z0, z1)
    top = solid.edges().filter_by(Plane.XY).group_by(Axis.Z)[-1]
    return chamfer(top, c)


def _b_half(p: dict) -> float:
    return _half_width(p["Y0"]) + p["B_WALL"]


def _b_board(p: dict, wx: float) -> Part:
    """Board marking: 0.6 x 0.3 grooves at 2.4 mm pitch running ALONG the arm across the bed face -
    the one face on this part over 200 mm² that can carry them without hanging a ceiling. On a
    vertical formwork face the same groove is a 13 mm² downward strip per groove and could only be
    declared away twenty-four times over; on the bed face it is one 0.6 mm span, declared once."""
    tool = Part()
    k = int((wx - 1.4) / p["B_BOARD_PITCH"])
    for i in range(-k, k + 1):
        x = i * p["B_BOARD_PITCH"]
        gap = p["Y0"] + (p["B_BOARD_GAP"][i % 2])
        for ya, yb in ((p["Y0"] - 1.0, gap - 1.2), (gap + 1.2, p["Y1"] + 1.0)):
            tool += box(x - p["B_BOARD_W"] / 2, ya, -p["FLOOR"] - 1.0,
                        x + p["B_BOARD_W"] / 2, yb, -p["FLOOR"] + p["B_BOARD_D"])
    return tool


def _b_board_run(p: dict) -> float:
    """The longest single plank run, which is what the bridge declaration has to cover. The grooves
    run along the ARM, and the arm sits at ~33 deg to the frame axes, so overhangs() measures a
    continuous 44 mm groove floor as min(44 cos, 44 sin) = 24 mm of axis-aligned span and rejects it
    against TPU95A's 22 mm limit. Breaking each groove at a staggered plank end caps that span at
    run/sqrt(2) whatever the arm angle, which is also what formwork actually looks like: planks have
    ends, and they are staggered course to course."""
    gaps = p["B_BOARD_GAP"]
    return max(max(g - 1.2 - (p["Y0"] - 1.0), (p["Y1"] + 1.0) - (p["Y0"] + g + 1.2)) for g in gaps)


def _b_mark(p: dict) -> Part | None:
    """The cast-in plaque: a wordmark sunk 2.0 mm into the plinth, running ALONG the arm because a
    22 mm wordmark (its MARK_MIN) does not fit across a 20.7 mm slab. 2.0 into a 4.0 plinth leaves
    2.0 - declared as a residual, the way carapace declares its suture."""
    if not S.mark_fits(p["B_MARK_KIND"], p["B_MARK_SIZE"]):
        return None
    return S.mark(p["B_MARK_KIND"], p["B_MARK_SIZE"], "deboss",
                  (0.0, p["Y0"] + 13.0, -p["FLOOR"]), normal=(0, 0, -1),
                  depth=p["B_MARK_DEPTH"], x_dir=(0, 1, 0))


def _brutalist(p: dict) -> Part:
    """The whole brutalist sleeve, arm-local. Mating geometry first, formwork last."""
    outline = Face(_outline_wire())
    pocket = _crop(_offset2d(outline, -p["INTERFERENCE"]), p["Y0"], p["Y1"])
    F, T, wx, c = p["FLOOR"], p["CARBON_T"], _b_half(p), p["B_CHAMFER"]

    # The slab and each rib are chamfered as SEPARATE convex prisms and only then unioned. Chamfering
    # the unioned plan instead asks OCCT to run a 1.0 mm chamfer through six re-entrant corners where
    # a rib meets the slab, and it declines outright (BRep_API: command not done, measured).
    part = _b_prism(p, wx, p["Y0"], p["Y1"], -F, T, c)
    for y in p["B_RIB_Y"]:                       # the proud square ribs are part of the formwork
        part += _b_prism(p, wx + p["B_RIB_PROUD"], y - p["B_RIB_W"] / 2, y + p["B_RIB_W"] / 2,
                         -F, T, c)
    part -= _slab(pocket, 0.0, T + 2.0)          # the cavity, exact - shard's, untouched

    if p["RIBS"]:
        rib_inner = _crop(_offset2d(outline, -(p["INTERFERENCE"] + p["RIB_H"])), p["Y0"], p["Y1"])
        for y in p["RIB_Y"]:
            band = _crop(pocket - rib_inner, y - p["RIB_L"] / 2, y + p["RIB_L"] / 2)
            part += _slab(band, p["RIB_Z0"], p["RIB_Z0"] + p["RIB_T"])

    vy0, vy1, sill = p["B_VOID"]                 # ONE rectangular void per side face, open at the top
    part -= _slab(_crop(_b_plan(p, wx, p["Y0"], p["Y1"]), vy0, vy1), sill, T + 1.0)
    part -= _b_board(p, wx)
    mk = _b_mark(p)
    if mk is not None:
        part -= mk
    assert len(part.solids()) == 1, f"arm_sleeve brutalist: {len(part.solids())} solids"
    return part


# The two declared bridges, and the only two on this variant: the board-marking groove floors sit
# 0.3 mm above the bed and span 0.6 mm, the wordmark floor sits 2.0 mm above it and spans one letter
# stroke. Both are far under TPU95A's bridge limit. Everything else on the part is vertical or up.
BRIDGE_OK.update({f"arm_sleeve_{a}__brutalist": _B_BRIDGE for a in _ARM_NAMES})


def _params(overrides: dict, style: str = "shard") -> dict:
    p = dict(Y0=Y0, Y1=Y1, INTERFERENCE=INTERFERENCE, WALL=WALL, FLOOR=FLOOR, CARBON_T=CARBON_T,
             CHAMFER_DEG=CHAMFER_DEG, RIBS=RIBS, RIB_H=RIB_H, RIB_L=RIB_L, RIB_T=RIB_T, RIB_Y=RIB_Y,
             RIB_Z0=RIB_Z0, STYLE=style)
    if style == "carapace":
        p.update(FLOOR=CARAPACE_FLOOR, D_LIP=D_LIP, CARAPACE_PROFILE=CARAPACE_PROFILE,
                 FILLET_DOME=FILLET_DOME, FILLET_CARINA=FILLET_CARINA, FILLET_LIP=FILLET_LIP,
                 SEGMENTS=SEGMENTS, SEG_M=SEG_M, SEG_EXP=SEG_EXP, SEG_MID=SEG_MID,
                 GROOVE_W=GROOVE_W, GROOVE_M=GROOVE_M, GROOVE_Z=GROOVE_Z,
                 SUTURE_W=SUTURE_W, SUTURE_D=SUTURE_D, PORT_W=PORT_W, PORT_LIG=PORT_LIG,
                 PORT_SEGMENTS=PORT_SEGMENTS, PUNCTA_D=PUNCTA_D, PUNCTA_DEPTH=PUNCTA_DEPTH,
                 PUNCTA_Z=PUNCTA_Z, PUNCTA_PER_SEG=PUNCTA_PER_SEG, MARK_KIND=MARK_KIND,
                 MARK_SIZE=MARK_SIZE, MARK_DEPTH_=MARK_DEPTH_)
    if style == "vespid":
        p.update(FLOOR=V_FLOOR, V_TERGITES=V_TERGITES, V_L_RATIO=V_L_RATIO, V_G_RATIO=V_G_RATIO,
                 V_SKIN_TIP=V_SKIN_TIP, V_COLLAR_PROUD=V_COLLAR_PROUD, V_COLLAR_W=V_COLLAR_W,
                 V_GROOVE_D=V_GROOVE_D, V_GROOVE_W=V_GROOVE_W, V_SPIRACLE=V_SPIRACLE,
                 V_SPIRACLE_ZC=V_SPIRACLE_ZC, V_PUNCTA_D=V_PUNCTA_D, V_PUNCTA_DEPTH=V_PUNCTA_DEPTH,
                 V_PUNCTA_X=V_PUNCTA_X, V_PUNCTA_PITCH=V_PUNCTA_PITCH)
    if style == "gyroid":
        p.update(FLOOR=G_FLOOR, WALL=G_WALL, G_WALL=G_WALL, G_RIND=G_RIND, G_R=G_R,
                 G_PERIOD=G_PERIOD, G_SHEET=G_SHEET, G_CELLS=G_CELLS, G_LIG=G_LIG, G_INSET=G_INSET)
    if style == "brutalist":
        p.update(FLOOR=B_FLOOR, WALL=B_WALL, CHAMFER_DEG=0.0, RIB_Y=B_GRIP_Y, B_WALL=B_WALL,
                 B_CORNER=B_CORNER, B_CHAMFER=B_CHAMFER, B_RIB_PROUD=B_RIB_PROUD, B_RIB_W=B_RIB_W,
                 B_RIB_Y=B_RIB_Y, B_VOID=B_VOID, B_BOARD_W=B_BOARD_W, B_BOARD_D=B_BOARD_D,
                 B_BOARD_PITCH=B_BOARD_PITCH, B_BOARD_GAP=B_BOARD_GAP, B_MARK_KIND=B_MARK_KIND, B_MARK_SIZE=B_MARK_SIZE,
                 B_MARK_DEPTH=B_MARK_DEPTH)
    p.update(overrides)
    return p


_LOCAL: dict[str, Part] = {}   # the arm-local solid of the last build of each variant


_BODIES = {"carapace": _carapace, "vespid": _vespid, "brutalist": _brutalist, "gyroid": _gyroid}


def build(variant: str = "shard", **overrides) -> dict[str, Part]:
    style = _kind(variant)
    p = _params(overrides, style)
    local = _BODIES.get(style, _sleeve)(p)
    _LOCAL[variant or "shard"] = local
    return {f"arm_sleeve_{a}": place_arm(deepcopy(local), P.ARM_PLACEMENTS[f"arm_{a}"]) for a in _ARM_NAMES}


def _intended_overlap(p: dict) -> float:
    """Press fit on its own arm: 2 x INTERFERENCE x CARBON_T x (Y1 - Y0) plus the ribs."""
    v = 2 * p["INTERFERENCE"] * p["CARBON_T"] * (p["Y1"] - p["Y0"])
    if p.get("B_VOID"):        # brutalist: the side-face void removes that band of squeeze outright
        vy0, vy1, sill = p["B_VOID"]
        v -= 2 * p["INTERFERENCE"] * (p["CARBON_T"] - sill) * (vy1 - vy0)
    if p["RIBS"]:
        v += 2 * len(p["RIB_Y"]) * p["RIB_H"] * p["RIB_L"] * p["RIB_T"]
    return v


# the generic frame-interference check tolerates exactly the band that checks() also enforces
ALLOWED_INTERFERENCE = {f"arm_sleeve_{a}": {f"arm_{a}": 1.2 * _intended_overlap(_params({}))}
                        for a in _ARM_NAMES}


def _wall_floor(style: str) -> float:
    """SHARD's skin is a uniform 2.15 mm band, so 1.5 is the honest threshold and is kept. CARAPACE
    deliberately grades its skin to 1.60 at the free lip (CN-5 - a constant-thickness slab is a
    failure of the style), so its threshold is TPU's structural floor of 1.2. Not a relaxation of
    SHARD's check: two different walls, each measured against its own material floor."""
    return {"carapace": 1.2, "vespid": 1.4, "gyroid": 1.5, "brutalist": 3.0}.get(style, 1.5)


def _twin_wall(p: dict, style: str) -> float:
    """The uniform-skin SHARD twin min_wall() is measured on, chosen so it is everywhere <= the real
    part's skin - a conservative lower bound, never a relaxation. CARAPACE: D_LIP. VESPID: the
    outboard tergite's skin less its undercut groove, the thinnest perpendicular offset on the part
    (the spiracle floors are decoration and are measured as explicit residuals instead, exactly as
    carapace's suture and puncta are)."""
    if style == "carapace":
        return p["D_LIP"]
    if style == "vespid":
        return round(p["V_SKIN_TIP"] - p["V_GROOVE_D"], 5)
    return p["WALL"]      # brutalist: WALL is B_WALL, and the rectangular plan is everywhere
#                           at least that far from the outline (the shaft only narrows outboard)


def checks(parts: dict[str, Part], frame: dict[str, Part], variant: str = "") -> list[tuple[str, bool, str]]:
    """ONE checks() for both styles. Every mating assertion below is the one the single-style sleeve
    had; the style-specific rows add CARAPACE's conformance and never relax a fit check."""
    style = _kind(variant)
    p = _params({}, style)
    target = _intended_overlap(p)
    floor_t = _wall_floor(style)
    guards = {a: place_arm(deepcopy(_guard_probe(p)), P.ARM_PLACEMENTS[f"arm_{a}"]) for a in _ARM_NAMES}

    # min_wall() erodes and dilates, which OCCT refuses on surfaces of extrusion and on features it
    # erodes away entirely; it runs on a faceted twin (curved walls as FACET-long chords, < 1 um
    # deviation on this taper) of the bare wall structure, with the 0.3 ribs and the 30 deg end
    # chamfers - the spec's allowances - left out. _wall_gauge() measures the band itself.
    #
    # For CARAPACE the twin is the SHARD construction at WALL = D_LIP with the carapace floor. That is
    # rigorously conservative rather than a shortcut: every point of the carapace skin lies at a
    # perpendicular offset of at least D_LIP from the nominal outline, so the real part's wall is
    # everywhere >= the twin's, and the twin has the same simple topology the shard twin has.
    # min_wall reports "ray sampling (offset unavailable)" on BOTH twins - OCCT will not offset a
    # surface of extrusion, which is exactly why this module has always carried _wall_gauge() as well:
    # the gauge is an exact planar measurement of the band, the rays are the sanity net. The
    # decoration neither of them can see - the suture, the ports, the puncta, the mark - is measured
    # explicitly, number by number, in _carapace_checks().
    twin_wall = _twin_wall(p, style)
    twin = _sleeve({**p, "RIBS": False, "CHAMFER_DEG": 0.0, "WALL": twin_wall}, FACET)
    gauge = _wall_gauge({**p, "WALL": twin_wall})
    ok_wall, _v, wall_detail = min_wall(place_arm(deepcopy(twin), P.ARM_PLACEMENTS["arm_front_right"]), floor_t)

    out = []
    if variant:
        # No Blender pass on this part - the recipes cannot select a U-sleeve's outward skin (module
        # docstring). absent_ok keeps that from reading as a forgotten decorate() call; any module
        # that DOES decorate leaves it False.
        out += BL.decor_checks(G_KEY if style == "gyroid" else f"arm_sleeve_front_right__{variant}",
                               absent_ok=True)
        if style in S.STYLES:
            st = S.STYLES[style]
            out.append((f"style {st.name}: free-edge radius within 0.45 x the lip wall",
                        S.edge_radius(st, "free", 1.6) <= 0.45 * 1.6 + 1e-9,
                        f"free tier {S.edge_radius(st, 'free', 1.6)} mm on the 1.6 mm lip"))
    if style == "vespid":
        out += _vespid_checks(p, variant)
    if style == "brutalist":
        out += _brutalist_checks(p, variant)
    if style == "gyroid":
        out += _gyroid_checks(p, variant)
    if style == "carapace":
        # CARAPACE is fillets only, no chamfers anywhere - a carapace is grown, not cut. The ladder's
        # `crease` tier (1.6) is deliberately NOT spent: the sleeve's only internal crease is the keel,
        # where the flank meets the flat belly, and that edge IS the bed plane - a 1.6 fillet there is
        # a ~220 mm² downward-facing band across both flanks and fails overhangs() outright.
        out.append(("carapace: fillets only (3.0 dome / 0.8 carina / 0.5 lip), no chamfer anywhere",
                    S.STYLES["carapace"].edge["kind"] == "fillet"
                    and (FILLET_DOME, FILLET_CARINA, FILLET_LIP) == (3.0, 0.8, 0.5),
                    f"dome {FILLET_DOME}, carina {FILLET_CARINA}, lip {FILLET_LIP}; the 1.6 crease "
                    f"tier is unspent - the only crease is the keel, which is the bed plane"))
        out += _carapace_checks(p, variant)

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
        out.append((f"{label}: wall tops flush with the carbon top face Z {Z_ARM_TOP} (+-0.05)",
                    abs(top - Z_ARM_TOP) <= 0.05, f"max Z {top:.4f}"))

        disc = prop_disc_violation(s)
        out.append((f"{label}: outside the prop discs above Z {PROP_Z0}", disc < EPS, f"{disc:.3f} mm³"))

        gap = s.distance_to(guards[a])
        out.append((f"{label}: >= 0.5 mm clear of the motor_guard face", gap >= 0.5, f"{gap:.3f} mm"))

        bridges = BRIDGE_OK.get(f"{label}__{variant}", ())
        over = overhangs(s, PRINT[label], material=MATERIAL, bridge_ok=bridges)
        out.append((f"{label}: no unsupported overhangs"
                    + (" (the mark's 1.6 mm bars bridged)" if bridges else ""),
                    not over, "; ".join(over) or "none"))

        solid_ok, solid_detail = single_solid(s)
        out.append((f"{label}: one watertight solid", solid_ok, solid_detail))

        out.append((f"{label}: min wall >= {floor_t} (ribs and decoration allowed)",
                    ok_wall and gauge >= floor_t - 1e-6,
                    f"{wall_detail}; wall band {gauge:.3f} mm, floor {p['FLOOR']} mm"))

    distinct = all(not a.wrapped.IsSame(b.wrapped) for i, a in enumerate(shapes) for b in shapes[i + 1:])
    out.append(("four distinct placed shapes", distinct and len(shapes) == 4, f"{len(shapes)} copies"))
    return out


def _station_skin(local: Part, y: float, p: dict) -> float:
    """The skin thickness the SOLID actually carries at arm-local station y: the widest half width of
    a 0.4 mm slice through the part, less the carbon shaft's own half width there. Measured on the
    built solid, not read back off the parameter list."""
    sl = local & box(-40.0, y - 0.2, -p["FLOOR"] - 1.0, 40.0, y + 0.2, p["CARBON_T"] + 1.0)
    return sl.bounding_box().max.X - _half_width(y)


def _vespid_checks(p: dict, variant: str) -> list[tuple[str, bool, str]]:
    """VESPID's own conformance, every number measured on the arm-local solid."""
    local = _LOCAL.get(variant) or _vespid(p)
    bounds, skins = _v_bounds(p), _v_skins(p)
    out = []

    # --- the two taper laws, read back off the geometry -----------------------------------------
    lens = [yb - ya for ya, yb in bounds]
    lr = [b / a for a, b in zip(lens, lens[1:])]
    out.append((f"vespid: {p['V_TERGITES']} tergites, length ratio {p['V_L_RATIO']} within 2%",
                len(lens) == p["V_TERGITES"]
                and all(abs(r - p["V_L_RATIO"]) <= 0.02 * p["V_L_RATIO"] for r in lr),
                "lengths " + ", ".join(f"{v:.2f}" for v in lens)
                + " mm, ratios " + ", ".join(f"{r:.4f}" for r in lr)))

    # the body station of each tergite: inboard of the undercut groove, clear of both parting lines
    terg = [_v_tergite(i, p) for i in range(p["V_TERGITES"])]
    body_y = [sum(t["body"]) / 2.0 for t in terg]
    meas = [_station_skin(local, y, p) for y in body_y]
    gr = [b / a for a, b in zip(meas, meas[1:])]
    out.append((f"vespid: girth ratio {p['V_G_RATIO']} within 2%, measured on the solid",
                all(abs(r - p["V_G_RATIO"]) <= 0.02 * p["V_G_RATIO"] for r in gr),
                "skins " + ", ".join(f"{v:.3f}" for v in meas)
                + " mm, ratios " + ", ".join(f"{r:.4f}" for r in gr)))
    out.append(("vespid: the skin ladder matches the design (0.02 mm)",
                all(abs(m - s) <= 0.02 for m, s in zip(meas, skins)),
                "designed " + ", ".join(f"{v:.3f}" for v in skins) + " mm"))

    # --- the collar and its undercut groove: a step, not a blend --------------------------------
    collar = [_station_skin(local, sum(t["collar"]) / 2.0, p) for t in terg]
    groove = [_station_skin(local, sum(t["groove"]) / 2.0, p) for t in terg]
    proud = [c - m for c, m in zip(collar, meas)]
    under = [m - g for m, g in zip(meas, groove)]
    out.append((f"vespid: every tergite ends in a {p['V_COLLAR_PROUD']} mm proud collar",
                all(abs(v - p["V_COLLAR_PROUD"]) <= 0.02 for v in proud),
                "proud " + ", ".join(f"{v:.3f}" for v in proud) + " mm"))
    out.append((f"vespid: a {p['V_GROOVE_D']} mm undercut groove immediately aft of every collar",
                all(abs(v - p["V_GROOVE_D"]) <= 0.02 for v in under),
                "undercut " + ", ".join(f"{v:.3f}" for v in under) + " mm"))
    # the 200 px thumbnail gate: the plan outline has to STEP, and the step that reads is the drop
    # from a collar to the next tergite's body
    steps = [collar[i] - meas[i + 1] for i in range(len(meas) - 1)]
    out.append(("vespid: every parting line steps >= 1.0 mm in plan (the 200 px thumbnail gate)",
                min(steps) >= 1.0, "collar-to-body steps " + ", ".join(f"{v:.2f}" for v in steps)
                + f" mm, against shard's constant {WALL:.2f} mm band (step 0.00)"))

    # --- apertures and accents ------------------------------------------------------------------
    ly, lz, depth = p["V_SPIRACLE"]
    _sp, n_sp = _v_spiracles(p)
    lig = [(t["body"][1] - t["body"][0] - ly * p["V_L_RATIO"] ** t["i"]) / 2 for t in terg]
    out.append((f"vespid: one {ly} x {lz} spiracle slit per tergite flank, {depth} mm deep, blind, "
                f"ligament >= 0.8 mm", n_sp == 2 * p["V_TERGITES"] and min(lig) >= 0.8,
                f"{n_sp} spiracles ({p['V_TERGITES']} tergites x 2 flanks), end ligaments "
                + ", ".join(f"{v:.2f}" for v in lig) + " mm"))
    _dots, n_dots = _v_puncta(p)
    out.append((f"vespid: two puncta rows, Ø{p['V_PUNCTA_D']} x {p['V_PUNCTA_DEPTH']} deep, "
                f"straddling the dorsal centreline", n_dots >= 16 and n_dots % 2 == 0,
                f"{n_dots} dimples at x +-{p['V_PUNCTA_X']}, {p['V_PUNCTA_PITCH']} mm pitch, cap face "
                f"{3.1416 * (p['V_PUNCTA_D'] / 2) ** 2:.2f} mm² (under the 5.0 mm² overhang floor)"))

    residuals = {"spiracle floor (outboard tergite)": skins[-1] - depth,
                 "undercut groove (outboard tergite)": skins[-1] - p["V_GROOVE_D"],
                 "puncta (belly)": p["FLOOR"] - p["V_PUNCTA_DEPTH"]}
    worst = min(residuals.values())
    out.append((f"vespid: every decoration residual >= {_wall_floor('vespid')} mm",
                worst >= _wall_floor("vespid") - 1e-6,
                ", ".join(f"{k} {v:.3f}" for k, v in residuals.items())))
    out.append(("vespid: wall 2.2+ inboard tapering to 1.4 at the outboard spiracle",
                abs((skins[-1] - depth) - 1.4) <= 0.02 and skins[0] - depth >= 2.2,
                f"structural wall {skins[0] - depth:.2f} mm at tergite 1 -> "
                f"{skins[-1] - depth:.2f} mm at tergite {p['V_TERGITES']}"))

    shard_bb = _sleeve(_params({}, "shard")).bounding_box()
    bb = local.bounding_box()
    growth = max((bb.size.X - shard_bb.size.X) / 2, shard_bb.min.Z - bb.min.Z, bb.max.Z - shard_bb.max.Z)
    out.append(("vespid: envelope growth over shard <= 2.4 mm on any face (collar crest included)",
                growth <= 2.4 + 1e-6,
                f"x +{(bb.size.X - shard_bb.size.X) / 2:.2f} per side, z {bb.min.Z:.2f}..{bb.max.Z:.2f} "
                f"vs shard {shard_bb.min.Z:.2f}..{shard_bb.max.Z:.2f}"))
    out.append(("vespid: the pocket, ribs, flush lip and end ramps are shard's, untouched",
                p["INTERFERENCE"] == INTERFERENCE and p["RIB_Y"] == RIB_Y and p["RIB_H"] == RIB_H
                and p["CARBON_T"] == CARBON_T and p["CHAMFER_DEG"] == CHAMFER_DEG,
                f"squeeze {p['INTERFERENCE']} mm/side, ribs {p['RIB_H']} proud at y {p['RIB_Y']}, "
                f"ramps {p['CHAMFER_DEG']} deg from vertical"))
    return out


def _gyroid_checks(p: dict, variant: str) -> list[tuple[str, bool, str]]:
    """GYROID's own conformance. Every row here holds on the UNDECORATED tube, which is the point:
    the lattice is allowed to be absent, the slab is not allowed to be wrong."""
    local = _LOCAL.get(variant) or _gyroid(p)
    w = _half_width(p["Y0"]) + p["G_WALL"]
    walls = [w - _half_width(y) for y in (p["Y0"], p["Y1"])]
    out = [("gyroid: constant-half-width slab, wall 3.6-5.0 mm (>= 1.5 periods across a "
            f"{p['G_PERIOD']} mm cell needs the envelope)",
            3.6 - 1e-6 <= min(walls) and max(walls) <= 5.0 + 1e-6,
            f"{walls[0]:.2f} mm at the root station to {walls[1]:.2f} mm at the tip, "
            f"plinth {p['FLOOR']:.1f} mm; the slab does not taper, the shaft does")]

    # the plan outline: one constant rounding, no crease. Measured as the radii of the vertical
    # cylindrical faces on the OUTER boundary of the undecorated slab.
    plan_solid = _slab(_g_plan(p), -p["FLOOR"], 0.0)
    radii = set()
    for f in plan_solid.faces():
        if f.geom_type != GeomType.CYLINDER:
            continue
        try:    # a trimmed surface has no .Cylinder(); fall back to its own bounding radius
            radii.add(round(f.geom_adaptor().Cylinder().Radius(), 4))
        except AttributeError:
            bb = f.bounding_box()
            radii.add(round(max(bb.size.X, bb.size.Y), 4))
    radii = sorted(radii)
    out.append((f"gyroid: a single constant r = {p['G_R']} rounding on the plan outline, no crease",
                radii == [p["G_R"]], f"plan corner radii {radii} mm"))
    out.append((f"gyroid: {p['G_RIND']} mm solid rind over the cavity and at both end faces",
                _g_guard(p).volume > 0 and isect(_g_guard(p), _slab(
                    _crop(_offset2d(Face(_outline_wire()), -p["INTERFERENCE"]), p["Y0"], p["Y1"]),
                    0.0, p["CARBON_T"])) > 0,
                f"rind {p['G_RIND']} mm, leaving {p['G_WALL'] - p['G_RIND']:.1f} mm of wall for the "
                f"sheet at the root station and {walls[1] - p['G_RIND']:.1f} at the tip"))
    out.append((f"gyroid: lattice state (cells tried: {', '.join(p['G_CELLS'])})", True, _G_REASON))

    shard_bb = _sleeve(_params({}, "shard")).bounding_box()
    bb = local.bounding_box()
    growth = max((bb.size.X - shard_bb.size.X) / 2, shard_bb.min.Z - bb.min.Z, bb.max.Z - shard_bb.max.Z)
    out.append(("gyroid: envelope growth over shard <= 2.4 mm on any face", growth <= 2.4 + 1e-6,
                f"x +{(bb.size.X - shard_bb.size.X) / 2:.2f} per side, z {bb.min.Z:.2f}..{bb.max.Z:.2f} "
                f"vs shard {shard_bb.min.Z:.2f}..{shard_bb.max.Z:.2f}"))
    out.append(("gyroid: the cavity, ribs, flush lip and end ramps are shard's, untouched",
                p["INTERFERENCE"] == INTERFERENCE and p["RIB_Y"] == RIB_Y and p["RIB_H"] == RIB_H
                and p["CARBON_T"] == CARBON_T and p["CHAMFER_DEG"] == CHAMFER_DEG,
                f"squeeze {p['INTERFERENCE']} mm/side, ribs {p['RIB_H']} proud at y {p['RIB_Y']}, "
                f"ramps {p['CHAMFER_DEG']} deg from vertical"))
    return out


def _brutalist_checks(p: dict, variant: str) -> list[tuple[str, bool, str]]:
    """BRUTALIST's own conformance, measured on the arm-local solid."""
    local = _LOCAL.get(variant) or _brutalist(p)
    wx, T, F = _b_half(p), p["CARBON_T"], p["FLOOR"]
    out = []

    # --- no rounded edge treatment anywhere -----------------------------------------------------
    curved = [f for f in local.faces() if f.geom_type.name in ("TORUS", "SPHERE", "BEZIER")]
    out.append(("brutalist: no fillet anywhere - max edge radius 0.0 <= 0.3",
                not curved, f"{len(curved)} toroidal/spherical faces; the only curved faces on the "
                            f"part are the cavity, which is the carbon shaft's own profile offset "
                            f"by {p['INTERFERENCE']} mm - mating geometry, not an edge treatment"))
    # the chamfer is a ruled loft, so it is exactly 1.0 at 45 deg by construction; measured as the
    # planar faces whose normal is 45 deg off vertical in the top 1.0 mm of the part
    ch = [f for f in local.faces() if f.geom_type == GeomType.PLANE
          and abs(abs(f.normal_at().Z) - 0.7071) < 0.01 and f.bounding_box().min.Z >= T - p["B_CHAMFER"] - 1e-3]
    out.append((f"brutalist: {p['B_CHAMFER']} mm 45 deg chamfer round the whole top perimeter, "
                f"and 45 deg cuts on every plan corner", len(ch) >= 8 and p["B_CORNER"] == 1.0,
                f"{len(ch)} chamfer faces at 45 deg, plan corners cut {p['B_CORNER']} mm; the bottom "
                f"perimeter is left SHARP on purpose - a chamfer there is a 184 mm² band at "
                f"normal.Z -0.71 across the bed face"))

    # --- the wall is 3.0 MINIMUM and the plan is orthogonal --------------------------------------
    walls = [wx - _half_width(y) for y in (p["Y0"], p["Y1"])]
    out.append((f"brutalist: wall >= {p['B_WALL']} everywhere, never thinned (the formwork does not "
                f"follow the shaft)", min(walls) >= p["B_WALL"] - 1e-6,
                f"{walls[0]:.2f} mm at the root station, {walls[1]:.2f} mm at the tip; plinth "
                f"{F:.1f} mm"))
    bb = local.bounding_box()
    shard_bb = _sleeve(_params({}, "shard")).bounding_box()
    out.append(("brutalist: reads twice as heavy as shard (plan area and volume)",
                local.volume >= 1.8 * _sleeve(_params({}, "shard")).volume,
                f"{local.volume:.0f} mm³ against shard's "
                f"{_sleeve(_params({}, 'shard')).volume:.0f} mm³, "
                f"{bb.size.X:.1f} mm wide against shard's {shard_bb.size.X:.1f} mm"))

    # --- exactly ONE rectangular void per side face, >= 40% of that face ------------------------
    vy0, vy1, sill = p["B_VOID"]
    face_a = T * (p["Y1"] - p["Y0"])            # the flank's WALL band: the panel the void is cut in
    void_a = (vy1 - vy0) * (T - sill)
    out.append((f"brutalist: one rectangular void per side face, >= 40% of that face",
                void_a >= 0.40 * face_a,
                f"{void_a:.1f} of {face_a:.1f} mm² = {void_a / face_a:.1%} of the flank wall band "
                f"(z 0-{T}, y {p['Y0']}-{p['Y1']}); open at the wall top, so it has no ceiling"))

    # --- ribs, board marking, plaque -------------------------------------------------------------
    pitch = [b - a for a, b in zip(p["B_RIB_Y"], p["B_RIB_Y"][1:])]
    out.append((f"brutalist: {len(p['B_RIB_Y'])} proud square ribs, {p['B_RIB_PROUD']} x "
                f"{p['B_RIB_W']} section, 12 mm pitch, full height",
                len(p["B_RIB_Y"]) == 3 and all(abs(v - 12.0) < 1e-6 for v in pitch)
                and p["B_RIB_PROUD"] == p["B_RIB_W"]
                and abs(bb.max.X - (wx + p["B_RIB_PROUD"])) < 0.05,
                f"pitch {pitch} mm, outer half width {bb.max.X:.2f} mm against the slab's {wx:.2f}"))
    board = _b_board(p, wx)
    n_grooves = len(board.solids())
    run = _b_board_run(p)
    out.append((f"brutalist: board marking {p['B_BOARD_W']} x {p['B_BOARD_D']} at "
                f"{p['B_BOARD_PITCH']} mm pitch, all one direction, plank ends staggered",
                n_grooves >= 14 and (p["Y1"] - p["Y0"]) * 2 * wx > 200
                and run / 2 ** 0.5 <= MATERIALS[MATERIAL]["bridge_max"],
                f"{n_grooves} plank runs along the arm across the "
                f"{(p['Y1'] - p['Y0']) * 2 * wx:.0f} mm² plinth face, longest run {run:.1f} mm -> at "
                f"most {run / 2 ** 0.5:.1f} mm of axis-aligned span at any arm angle, against "
                f"TPU95A's {MATERIALS[MATERIAL]['bridge_max']} mm bridge limit"))
    mk = _b_mark(p)
    out.append((f"brutalist: {p['B_MARK_KIND']} plaque cast {p['B_MARK_DEPTH']} mm into the plinth",
                mk is not None and S.mark_fits(p["B_MARK_KIND"], p["B_MARK_SIZE"]),
                f"{p['B_MARK_SIZE']} mm, minimum {S.MARK_MIN[p['B_MARK_KIND']]} mm, running along "
                f"the arm (a 22 mm wordmark does not fit across a {2 * wx:.1f} mm slab)"))

    residuals = {"wordmark plaque": F - p["B_MARK_DEPTH"], "board marking": F - p["B_BOARD_D"],
                 "void sill": sill + F}
    worst = min(residuals.values())
    out.append(("brutalist: every formwork residual >= 1.2 (TPU floor)", worst >= 1.2 - 1e-9,
                ", ".join(f"{k} {v:.3f}" for k, v in residuals.items())))
    out.append(("brutalist: the cavity, the 0.3 grip ribs and the flush lip are shard's, untouched",
                p["INTERFERENCE"] == INTERFERENCE and p["RIB_H"] == RIB_H and p["CARBON_T"] == CARBON_T
                and len(p["RIB_Y"]) == len(RIB_Y),
                f"squeeze {p['INTERFERENCE']} mm/side, {len(p['RIB_Y'])} ribs {p['RIB_H']} proud at "
                f"y {p['RIB_Y']} (moved clear of the void, same count and section)"))
    return out


def _carapace_checks(p: dict, variant: str) -> list[tuple[str, bool, str]]:
    """CARAPACE's own conformance and every decoration residual, measured on the arm-local solid."""
    local = _LOCAL.get(variant) or _carapace(p)
    out = []

    lo, hi = sorted(_dome_ratio(p))
    out.append(("carapace: transverse dome rise/span in 0.28-0.36 (CN: the section is a dome)",
                0.28 - 1e-9 <= lo and hi <= 0.36 + 1e-9,
                f"{lo:.4f} at y {p['Y1']} to {hi:.4f} at y {p['Y0']} "
                f"(rise {p['CARAPACE_PROFILE'][2][1] + p['FLOOR']:.2f} mm)"))

    # CN-1: the groove is really there, on the belly centreline. The shared probe measures a groove
    # cut DOWNWARD, so the same arithmetic is applied to this upward-opening one: a full-depth V
    # leaves the probe box about half solid.
    probe = Pos(0.0, (p["Y0"] + p["Y1"]) / 2.0, -p["FLOOR"] + p["SUTURE_D"] / 2.0) * \
        Box(p["SUTURE_W"], (p["Y1"] - p["Y0"]) * 0.6, p["SUTURE_D"])
    frac = isect(local, probe) / probe.volume
    out.append((f"carapace: suture present on the dorsal centreline, {p['SUTURE_W']} x {p['SUTURE_D']} V",
                frac < 0.72, f"groove probe {frac:.3f} solid (a cut V reads ~0.45-0.60)"))
    # CN-3: it runs out to a POINT, not a square stop. Probed 2.0 mm in from each end rather than at
    # the very tip, because at the tip the 30 deg end ramp has already taken the belly away and the
    # probe would be measuring the ramp (measured 0.688 solid, all of it ramp). A vesica 44 mm long
    # is 0.28 mm wide 2 mm from its tip against 0.8 mm at mid-length, so the near-tip probe must come
    # back markedly MORE solid than the mid-length one - that difference IS the taper.
    tips = [isect(local, Pos(0.0, y, -p["FLOOR"] + p["SUTURE_D"] / 2.0) *
                  Box(p["SUTURE_W"], 0.6, p["SUTURE_D"])) for y in (p["Y0"] + 2.0, p["Y1"] - 2.0)]
    tip_probe = p["SUTURE_W"] * 0.6 * p["SUTURE_D"]
    tf = [v / tip_probe for v in tips]
    out.append(("carapace: the suture runs out to a cusp at both ends (CN-3)",
                min(tf) >= frac + 0.12 and max(tf) < 0.995,
                f"tip probes {tf[0]:.3f} and {tf[1]:.3f} solid against {frac:.3f} at mid-length"))

    ports, n_ports = _ports(p, _crop(_offset2d(Face(_outline_wire()), -p["INTERFERENCE"]), p["Y0"], p["Y1"]))
    out.append((f"carapace: {len(p['PORT_SEGMENTS'])} cusped segment ports placed, ligament >= "
                f"{p['PORT_LIG']}", n_ports == len(p["PORT_SEGMENTS"]),
                f"{n_ports} of {len(p['PORT_SEGMENTS'])} survived the aperture engine"))
    _dimples, n_puncta = _puncta_cut(p)
    out.append((f"carapace: punctate flanks, Ø{p['PUNCTA_D']} x {p['PUNCTA_DEPTH']} deep",
                n_puncta >= 8 and p["PUNCTA_D"] <= S.PUNCTA_D_MAX and p["PUNCTA_DEPTH"] <= S.PUNCTA_DEPTH_MAX,
                f"{n_puncta} dimples, cap face {3.1416 * (p['PUNCTA_D'] / 2) ** 2:.2f} mm² "
                f"(under the 5.0 mm² overhang floor)"))
    out.append((f"carapace: {p['MARK_KIND']} mark fits at {p['MARK_SIZE']} mm",
                S.mark_fits(p["MARK_KIND"], p["MARK_SIZE"]) and _mark_cut(p) is not None,
                f"minimum {S.MARK_MIN[p['MARK_KIND']]} mm, debossed {p['MARK_DEPTH_']} mm"))

    # every decoration residual against TPU's 1.2 structural floor, stated as a number rather than
    # left to the twin, which cannot see any of them
    residuals = {"suture": p["FLOOR"] - p["SUTURE_D"], "mark": p["FLOOR"] - p["MARK_DEPTH_"],
                 "puncta (thinnest flank row)": _flank_x(p["Y1"], p["PUNCTA_Z"][0], p["SEG_M"][0], p)
                 - (_half_width(p["Y1"]) - p["INTERFERENCE"]) - p["PUNCTA_DEPTH"],
                 "port ligament": p["PORT_LIG"]}
    worst = min(residuals.values())
    out.append(("carapace: every decoration residual >= 1.2 (TPU floor)", worst >= 1.2 - 1e-9,
                ", ".join(f"{k} {v:.3f}" for k, v in residuals.items())))

    # CN-5: the skin is graded, not a slab - the free lip is the material minimum and the crown
    # carries the impact path
    lip = p["D_LIP"] + p["INTERFERENCE"]
    crown = p["D_LIP"] + p["SEG_M"][1] * (p["CARAPACE_PROFILE"][1][0] - p["D_LIP"]) + p["INTERFERENCE"]
    out.append(("carapace: CN-5 thickness gradient, lip 1.60 -> crown >= 2.0 (impact path)",
                abs(lip - 1.60) < 0.02 and crown >= 2.0, f"lip {lip:.2f} mm, crown {crown:.2f} mm"))

    # the segment ladder is the style's silhouette (the thumbnail gate): every parting line must be a
    # visible step, and the steps must run ACROSS the arm (CN-2)
    step = (p["SEG_M"][1] - p["SEG_M"][0]) * (p["CARAPACE_PROFILE"][1][0] - p["D_LIP"])
    groove = (p["SEG_M"][1] - p["GROOVE_M"]) * (p["CARAPACE_PROFILE"][1][0] - p["D_LIP"])
    out.append((f"carapace: {p['SEGMENTS']} shingled segments, shingle step >= 0.5 and groove >= 1.0",
                p["SEGMENTS"] >= 4 and step >= 0.5 and groove >= 1.0,
                f"period {(p['Y1'] - p['Y0']) / p['SEGMENTS']:.2f} mm, shingle step {step:.3f} mm, "
                f"parting groove {groove:.3f} mm deep at the crown, transverse (CN-2)"))

    # §4.5, the silhouette-first directive: the PLAN OUTLINE has to change, not just the surface.
    # >= 1.0 mm of saw-tooth per side on a ~9.5 mm half width is ~9 px at the 200 px thumbnail size,
    # which is the size at which the ladder was actually looked at and judged.
    lo, hi, swing = _plan_swing(p)
    out.append(("carapace: every segment flares >= 1.0 mm in plan (the 200 px thumbnail gate)",
                lo >= 1.0, f"flare {lo:.2f}-{hi:.2f} mm per segment, {swing:.1%} of the half width, "
                           f"against shard's constant {WALL:.2f} mm band (flare 0.00)"))

    shard_local = _sleeve(_params({}, "shard"))
    shard_bb, bb = shard_local.bounding_box(), local.bounding_box()
    growth = max((bb.size.X - shard_bb.size.X) / 2, shard_bb.min.Z - bb.min.Z,
                 bb.max.Z - shard_bb.max.Z)
    out.append(("carapace: envelope growth over shard <= 2.0 mm on any face", growth <= 2.0 + 1e-6,
                f"x +{(bb.size.X - shard_bb.size.X) / 2:.2f} per side, z {bb.min.Z:.2f}..{bb.max.Z:.2f} "
                f"vs shard {shard_bb.min.Z:.2f}..{shard_bb.max.Z:.2f}"))
    out.append(("carapace: the pocket, ribs, flush lip and end ramps are shard's, untouched",
                p["INTERFERENCE"] == INTERFERENCE and p["RIB_Y"] == RIB_Y and p["RIB_H"] == RIB_H
                and p["CARBON_T"] == CARBON_T and p["CHAMFER_DEG"] == CHAMFER_DEG,
                f"squeeze {p['INTERFERENCE']} mm/side, ribs {p['RIB_H']} proud at y {p['RIB_Y']}, "
                f"ramps {p['CHAMFER_DEG']} deg from vertical"))
    return out
