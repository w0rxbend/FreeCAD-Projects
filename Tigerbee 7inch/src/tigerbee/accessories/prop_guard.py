"""Half-ring prop guard on the arm tip - the CHASSIS family's hero part, in three styles.

`refs/prop-guard/reference.png` executed properly: an arched truss on the outboard half of the
prop disc, an outer rail with a serrated (spined) outer edge, triangulated struts with a RING
NODE at every junction, a hub with a starburst, and a notched anti-rotation tab running back
along the arm shaft. A tiger beetle's spined tibia.

    STYLES = ("chassis", "shard", "feral")

ARM-TIP SYMMETRY - the finding that sets the label count
--------------------------------------------------------
`tigerbee.profiles._outline()` builds the arm's left flank and mirrors it for the right, and only
the ROOT is handed ("handed two-finger root"). Measured on the real wire: for every sampled point
with local y >= L - 50 the mirrored point lies on the outline to **0.0 mm**, while over the whole
outline the worst mirror distance is 2.582 mm (all of it in the root fingers). `motor_bolts()` puts
the four M3 at 45 + 90k on a Ø19 circle and `D_MOTOR_BORE` is on the axis, so the entire mounting
interface is symmetric about the arm axis as well. ONE part therefore fits all four arms and the
module emits **one label per style** - `prop_guard__chassis`, `__shard`, `__feral` - built in the
front-right arm's frame position and checked there, with the other three placements checked too.

MOUNTING - why BETWEEN the arm and the motor, not under the arm
---------------------------------------------------------------
`motor_guard.py` already owns the arm underside: its FLANGE 4.0 slab occupies arm-local Z -4..0
with the M3 heads bearing at HEAD_Z -2.0 in Ø6.6 channels, and its landing foot lofts from that
slab down to local Z -12 over a 23 x 50 pad centred on local y 111.8. There is no room left under
the arm tip that does not either collide with that loft or hang the guard 12 mm below the airframe.

So this guard mounts **between the carbon and the motor**: a 2.0 mm hub floor on the arm top face,
frame Z 7.0-9.0, clamped by the same four motor screws. It raises the motor by exactly 2.0 mm.

  * with `motor_guard` fitted:  M3 x 12 (2 flange + 5 carbon + 2 hub floor + 3 into the motor)
  * prop_guard alone:           M3 x 10 (5 carbon + 2 hub floor + 3 into the motor)

that is **+2 mm of screw length** over whatever the build uses today. The brief's Ø6.6 screw-head
channels belong to the under-arm mount; here the heads bear below the carbon, inside `motor_guard`'s
own Ø6.6 channels (or on the bare carbon when it is not fitted), so the hub floor carries plain
Ø3.4 through holes and every one of its 2.0 mm is clamping material. `motor_guard`'s maximum
envelope tops out at frame Z 6.8, 0.2 mm below this floor; the two parts co-exist and the
interference check below proves it against a locally reconstructed envelope of that part (rebuilt
here rather than imported, so a sibling module's work in progress cannot silently disarm the check).

PROP KEEP-OUT - read this before touching the Z numbers
--------------------------------------------------------
The hub, the spokes and the tab all lie inside the Ø177.8 prop disc, and they sit above the arm
top face, so `_fit.prop_disc_violation` - which counts everything above PROP_Z0 = 7 - rejects them.
That rejection is wrong here and only here: the prop of a 2807 sits at frame Z 32 (arm top face +
`_fit.MOTOR_PROP_SEAT` = 25, the bell height; the 2.0 mm hub floor actually lifts it to 34, so the
number used is 2 mm conservative), and material 22 mm below the blades is not in the prop's way.

`OWN_PROP_DISC` therefore names this part's own motor, and the real rule is enforced LOCALLY:

    nothing above Z = arm top face + 3.0 = 10.0 anywhere inside r = 88.9 + 2.0 = 90.9 of the
    motor centre, and the rim band, which does stand 9 mm tall, lies entirely outside r 90.9.

The hub floor tops out at Z 9.0, every web member at Z 10.0 exactly, and the rail's inside face is
at r 92.9 (= 88.9 + 4), so both halves of that rule hold with the numbers, not with a tolerance.
The neighbouring discs are untouched: the outboard half-arc's closest approach to another motor
centre is 115.28 mm, against a 91.9 mm keep-out radius.

PRINTING
--------
Flat on the hub floor, bed normal (0, 0, -1), frame Z 7 is the bed plane. Every member is a prism
grown straight up from that plane, so there is not one downward face to support and not one bridge
to declare; the FERAL claws are cones with >= 60 deg flanks and their Ø1.7 tip balls are under
`overhangs()`' 5 mm² face floor. Nothing is filleted on the bed face - CN-6, the part looks like it
grew in the print direction.

MATERIAL
--------
TPU 95A throughout. This is the part that leads a crash; a rigid guard is a lever that snaps and
takes the motor mount with it. Struts are held to the family's TPU section (2.4 wide x 3.0 deep)
and the rim to 4.5 (5.0 on FERAL), both above the 2.0 mm impact-path floor.
"""

from functools import lru_cache
from math import atan2, ceil, cos, degrees, hypot, radians, sin, tan

from build123d import (Axis, Circle, Compound, Face, Kind, Part, Plane, Polygon, Pos, Rectangle,
                       Sketch, SlotOverall, Sphere, extrude, loft, offset)

from tigerbee import params as P
from tigerbee import profiles
from tigerbee.accessories._common import *  # noqa: F401,F403
from tigerbee.accessories import _style as S

NAME = "prop_guard"
TITLE = "Half-ring prop guard (arm tip, CHASSIS hero)"
MATERIAL = "TPU95A"
STYLES = ("chassis", "shard", "feral")

VARIANTS = {
    "chassis": {"style": "chassis",
                "notes": "the reference executed properly: two curved rails, 12 triangulated "
                         "struts at 51-66 deg, a ring node at every junction, a serrated outboard "
                         "rail edge and an 8-slot hub starburst"},
    "shard":   {"style": "shard",
                "notes": "faceted polygonal truss: an 8-facet outer rail polyline, a mitred "
                         "central labrum shield pierced with elongated hexes, stepped web "
                         "thickness 3.0/2.4/1.8 with visible step lines"},
    "feral":   {"style": "feral",
                "notes": "five cusped spindle legs and a crescent tarsus, four claw tips in a "
                         "1 : 0.78 : 0.61 : 0.48 run on the outboard rail, punctate rail cheek"},
}
ASSEMBLY_VARIANT = "chassis"

ARM = "arm_front_right"  # the placement build() returns; the part fits all four (see the docstring)
LABEL = "prop_guard"
PRINT = {LABEL: (0, 0, -1)}
OWN_PROP_DISC = {LABEL: ARM.removeprefix("arm_")}
MOUNTS = ("the Ø19 motor bolt circle at the arm-tip motor centre (4 x M3 at 45 deg, 13.435 mm "
          "adjacent) - the hub floor is clamped between the carbon and the motor",
          "arm_<corner> top face Z 7 (the hub floor and the anti-rotation tab seat on it)",
          "the arm shaft, local y 68-108, via the tab's two zip-tie notches")
HARDWARE = ("4 x M3 x 12 motor screws per guard when motor_guard is also fitted (2 mm of its "
            "flange + 5 mm of carbon + 2 mm of hub floor + 3 mm into the motor)",
            "4 x M3 x 10 motor screws per guard when it is fitted alone",
            "2 x 2.5 mm zip tie through the tab notches at local y 72 and 81")
NOTES = ("Sits BETWEEN the carbon and the motor and raises the motor 2.0 mm - use screws 2 mm "
         "longer than the build uses today. Co-exists with motor_guard, whose envelope tops out "
         "at frame Z 6.8. The hub, spokes and tab are inside the prop disc but 22 mm below the "
         "blades, which is why OWN_PROP_DISC is set and a local keep-out check (nothing above "
         "Z 10 inside r 90.9) replaces the generic one. One part fits all four arms: the arm tip "
         "is symmetric about the arm axis to 0.0 mm. FERAL is handed by design - its claw row "
         "runs up one side only; mirror it in the slicer for the two arms that spin the other way.")

# --- parameters (mm; arm-local: root midpoint (0, 0), motor at (0, L), carbon frame Z 2..7) ---
L = P.ROOT_TO_MOTOR              # 114.804
Z_BED = Z_ARM_TOP                # 7.0 FRAME: arm top face = hub floor underside = the bed plane
Z_LOCAL = P.ARM_T                # 5.0 ARM-LOCAL: the same plane. place_arm() adds P.Z_ARM = 2,
#                                  so every local Z below is exactly 2 mm under its frame Z.
FLOOR = 2.0                      # hub floor: clamped between the carbon and the motor
WEB_Z = 3.0                      # spoke / strut depth (the family's TPU section is 2.4 x 3.0)
RIM_H = 9.0                      # rim height above the arm top face (spec 8-10)
RIM_W = 4.5                      # rim width (spec 4-5); FERAL uses 5.0 so its puncta fit the cheek
PROP_R = 177.8 / 2               # 88.9
ARC_GAP = 4.0                    # rail inside face = PROP_R + ARC_GAP
ARC_R = PROP_R + ARC_GAP         # 92.9
ARC_HALF = 90.0                  # half angle of the outboard arc -> a 180 deg rail
PROP_Z = Z_ARM_TOP + MOTOR_PROP_SEAT   # 32.0: prop lower face (2807 bell height); see the docstring
PROP_CLEAR = 3.0                 # the rim must stay this far below the prop plane
KEEP_Z = Z_ARM_TOP + 3.0         # 10.0: local keep-out ceiling inside KEEP_R
KEEP_R = PROP_R + 2.0            # 90.9
BELL_R = 18.3                    # Ø35 2807 bell + 0.8: nothing above the floor inside this radius

R_HUB = 20.0                     # hub disc radius
R_SPOKE = 18.5                   # web members start here, just outside BELL_R
HUB_STEP = ((R_SPOKE, FLOOR),)   # inside R_SPOKE the part is the 2.0 hub floor and nothing else,
#                                  so the 2807 bell has its full Ø36.6 above the mounting face
BORE_D = P.D_MOTOR_BORE          # 6.5 shaft bore
BOLT_D = D_M3_THRU               # 3.4
STRUT_W = 2.4                    # TPU strut width
NODE_OD_F, NODE_ID_F = 2.6, 0.9  # ring node OD / ID as multiples of the strut width
NODE_WELD = 0.8                  # how far an outer ring node bites into the rail (a tangent ring
#                                  welds nothing: OCCT returns two solids)
R_INNER = 58.0                   # inner rail radius
INNER_W = 2.4
STAR_N, STAR_W, STAR_LEN = 8, 1.2, 6.4   # hub starburst (length trimmed to keep a 1.2 ligament)
PETAL_N = 8                      # bell-vent petals in the hub floor
PETAL_R0, PETAL_R1, PETAL_HW = 12.5, 17.8, 1.6
SERR_D, SERR_PITCH, SERR_OUT = 1.6, 3.2, 0.8   # outboard rail serration
TAB = (12.0, 68.0, 108.0)        # width, local y0, y1 -> 12 x 40, on the arm shaft top
TAB_NOTCH = (3.0, 1.5)           # zip-tie notch length x depth, both sides
TAB_NOTCH_Y = (72.0, 81.0)       # both behind motor_guard's rear edge (local y 84.804)
WALL_FLOOR = MATERIALS[MATERIAL]["wall"]        # 1.2
WALL_HIT = MATERIALS[MATERIAL]["wall_impact"]   # 2.0

# CHASSIS truss graph, in degrees off the outward arm direction
OUT_NODES = tuple(-90.0 + 30.0 * k for k in range(7))    # 7 nodes on the outer rail
IN_NODES = tuple(-75.0 + 30.0 * k for k in range(6))     # 6 nodes on the inner rail
SPOKE_NODES = (-45.0, -15.0, 15.0, 45.0)                 # 4 hub spokes, raked outboard
SPOKE_RAKE = 22.0

# SHARD: faceted rails, the mitred shield and the stepped web. The rail polylines carry the SAME
# node angles as the CHASSIS truss - "the same load path, executed as a faceted polygonal truss".
SH_OUT_FACETS, SH_IN_FACETS, SH_IN_HALF = 6, 5, 75.0   # struts land on facet MIDPOINTS, where
SH_OUT_NODES = tuple(-75.0 + 30.0 * k for k in range(6))   # equals the circular tangent, so the
SH_IN_NODES = tuple(-60.0 + 30.0 * k for k in range(5))    # 50-70 deg rule means what it says
SH_SHIELD_HALF = 45.0            # the inner labrum shield spans +-45 deg, hub to inner rail
SH_APRON_HALF = 30.0             # the outer apron spans +-30 deg, inner rail to outer rail
SH_SPOKES = (-63.0, 63.0)        # two raked spokes, landing well inside the inner rail's ends
SH_STEPS = ((42.5, 3.0), (77.0, 2.4), (1e3, 1.8))   # (outer radius, web depth) - visible step lines
SH_HEX_RINGS = ((25.5, 4.4), (37.0, 4.4), (48.5, 4.4))   # shield apertures (radius, radial half)
SH_APRON_RINGS = ((70.0, 5.2), (84.0, 5.2))              # apron apertures; no ring crosses a step
SH_LIG = 2.2                     # minimum ligament between shield apertures
SH_CHAMFER = 0.6                 # every junction mitred 0.6 x 45
SH_LABRUM = (16.0, 0.8)          # faceted shield proud of the outboard rail face at theta 0

# FERAL: spindle legs, crescent tarsus, claw run
FR_LEGS = (-80.0, -48.0, 0.0, 48.0, 80.0)
FR_LEG_HW = 8.0                  # spindle half width at mid span (a vesica, cusped at both ends)
FR_LEG_R0, FR_LEG_R1 = 6.0, 104.0   # both cusps are BURIED, in the hub and in the rim
FR_RIM_W = 5.0                   # wider cheek so a Ø2.2 punctum keeps its ligament
FR_ARC_R, FR_ARC_W, FR_ARC_HALF = 55.0, 5.0, 80.0
FR_CLAWS = ((0.0, 1.00), (27.0, 0.78), (54.0, 0.61), (81.0, 0.48))
FR_CLAW_H = 9.0                  # the tallest claw; the run scales off it
FR_CLAW_RB, FR_CLAW_WAIST, FR_CLAW_TIP = 2.2, 0.62, 0.85
FR_CLAW_RAKE = 0.30              # the tip leans this fraction of its height toward the prow
FR_PUNCTA_D, FR_PUNCTA_DEPTH, FR_PUNCTA_PITCH = 2.2, 0.45, 4.0

_EFFECTIVE: dict = {}


# --- polar helpers about the motor centre, in arm-local XY ------------------------------------
def _pt(r: float, th: float) -> tuple[float, float]:
    """Arm-local point at radius r, angle th (deg) off the outward arm direction (+Y)."""
    a = radians(th)
    return (r * sin(a), L + r * cos(a))


def _sector(r: float, a0: float, a1: float, step: float = 5.0) -> Sketch:
    """Pie sector about the motor centre, big enough to clip an annulus of radius < r."""
    n = max(2, int(ceil((a1 - a0) / step)))
    pts = [(0.0, L)] + [_pt(r, a0 + (a1 - a0) * i / n) for i in range(n + 1)]
    return Polygon(*pts, align=None)


def _band(r0: float, r1: float, a0: float, a1: float) -> Sketch:
    """Annular band r0..r1 clipped to the angular sector a0..a1."""
    return (Pos(0, L) * (Circle(r1) - Circle(r0))) & _sector(r1 * 1.2 + 6.0, a0, a1)


def _bar(p0, p1, w: float) -> Sketch:
    """Capsule between two points: a rounded rectangle, never square (CHASSIS strut section)."""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    n = hypot(dx, dy)
    return Pos((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2) * \
        SlotOverall(n + w, w).rotate(Axis.Z, degrees(atan2(dy, dx)))


def _poly_rail(r_in: float, w: float, facets: int, half: float = ARC_HALF) -> tuple[Sketch, list]:
    """SHARD rail: a straight-facet polyline band whose facet MIDPOINTS sit at radius r_in, so the
    inside face never comes closer to the motor axis than r_in. Returns (band, vertex radii)."""
    rv = r_in / cos(radians(half / facets))
    inner = [_pt(rv, -half + 2 * half * i / facets) for i in range(facets + 1)]
    outer = [_pt(rv + w, -half + 2 * half * i / facets) for i in range(facets + 1)]
    return Polygon(*inner, *reversed(outer), align=None), inner


def _tab(width: float, y0: float, y1: float, cusp: float = 0.0) -> Sketch:
    """Anti-rotation tab on the arm shaft top, with two zip-tie notches in both edges."""
    sk = Pos(0.0, (y0 + y1) / 2) * Rectangle(width, y1 - y0)
    if cusp > 0:  # FERAL: the tail runs out to a point instead of stopping square
        sk += S.cusp_tail(width, cusp, tip_r=0.8, at=(0.0, y0), angle=-90.0)
    nl, nd = TAB_NOTCH
    for y in TAB_NOTCH_Y:
        for s in (-1, 1):
            sk -= Pos(s * (width / 2 - nd / 2), y) * Rectangle(nd, nl)
    return sk


# --- the truss graph shared by CHASSIS and SHARD ----------------------------------------------
def _node_r_out() -> float:
    """Outer-rail node centres sit one ring radius inboard of the rail, so the eyelet is tangent to
    the rail's inside face instead of being a hole drilled through a 4.5 mm impact rim."""
    return ARC_R + NODE_WELD - NODE_OD_F * STRUT_W / 2


def _struts() -> list[tuple[tuple[float, float], tuple[float, float]]]:
    """The W truss: every inner node braced to the two outer nodes that bracket it (delta 15 deg)."""
    ro = _node_r_out()
    out = []
    for a in IN_NODES:
        for b in (a - 15.0, a + 15.0):
            out.append((_pt(R_INNER, a), _pt(ro, b)))
    return out


def _spokes(angles, rake: float, r_end: float = R_INNER
            ) -> list[tuple[tuple[float, float], tuple[float, float]]]:
    """Hub spokes, raked outboard so none of them meets the inner rail square on."""
    return [(_pt(R_SPOKE, a + (rake if a >= 0 else -rake)), _pt(r_end, a)) for a in angles]


def _hub_cuts() -> Sketch:
    """Shaft bore, the four motor holes, the starburst and the 8 bell-vent petals."""
    cut = Pos(0, L) * Circle(BORE_D / 2)
    for bx, by in profiles.motor_bolts(L):
        cut += Pos(bx, by) * Circle(BOLT_D / 2)
    star, n = S.starburst((0.0, L), BORE_D / 2 + 1.6, n=STAR_N, w=STAR_W, length=STAR_LEN)
    assert n == STAR_N, f"starburst lost {STAR_N - n} slots"
    cut += star
    for i in range(PETAL_N):
        th = 22.5 + 360.0 * i / PETAL_N
        cut += S.lens(_pt(PETAL_R0, th), _pt(PETAL_R1, th), PETAL_HW)
    return cut


# --- CHASSIS ----------------------------------------------------------------------------------
def _chassis() -> dict:
    ro = _node_r_out()
    web = Pos(0, L) * Circle(R_HUB)
    web += _band(R_INNER - INNER_W / 2, R_INNER + INNER_W / 2, IN_NODES[0], IN_NODES[-1])
    members = _spokes(SPOKE_NODES, SPOKE_RAKE) + _struts()
    for p0, p1 in members:
        web += _bar(p0, p1, STRUT_W)
    nodes = [_pt(R_INNER, a) for a in IN_NODES] + [_pt(ro, a) for a in OUT_NODES]
    bores = Sketch()
    for c in nodes:
        ring, bore = S.ring_node(c, STRUT_W, od_factor=NODE_OD_F, id_factor=NODE_ID_F)
        web += ring
        bores += bore
    web += _tab(*TAB)

    rim = _band(ARC_R, ARC_R + RIM_W, -ARC_HALF, ARC_HALF)
    edge = [_pt(ARC_R + RIM_W, ARC_HALF - 180.0 * i / 90) for i in range(91)]
    spines, n_spine = S.serration(edge, d=SERR_D, pitch=SERR_PITCH, protrusion=SERR_OUT)
    rim += spines
    return {"web": web, "rim": rim, "cuts": _hub_cuts() + bores, "nodes": nodes,
            "members": members, "struts": _struts(), "spokes": _spokes(SPOKE_NODES, SPOKE_RAKE),
            "steps": HUB_STEP + ((1e3, WEB_Z),), "serrations": n_spine,
            "rim_w": RIM_W, "claws": ()}


# --- SHARD ------------------------------------------------------------------------------------
def _elongated_hex(r: float, th: float, a: float, b: float, mitre: float) -> Sketch:
    """A mitred elongated hexagon, long axis tangential, centred at polar (r, th)."""
    pts = [(-a, 0.0), (-a + mitre, b), (a - mitre, b), (a, 0.0), (a - mitre, -b), (-a + mitre, -b)]
    return Pos(*_pt(r, th)) * Polygon(*pts, align=None).rotate(Axis.Z, -th)


def _hex_ring(r: float, b: float, half: float) -> tuple[Sketch, int, float]:
    """One tangential ring of mitred elongated hexes inside an angular sector, sized so the
    ligament between neighbours is exactly SH_LIG and the ligament to the sector edge is 1.5 x it."""
    usable = r * radians(2 * half) - 2 * SH_LIG
    n = max(2, int(usable // 13.0))
    pitch = usable / n
    a = (pitch - SH_LIG) / 2
    sk = Sketch()
    for i in range(n):
        off = -usable / 2 + pitch * (i + 0.5)
        sk += _elongated_hex(r, degrees(off / r), a, b, 0.3 * a)
    return sk, n, SH_LIG


def _faceted_panel(r0: float, r1: float, half: float, n0: int, n1: int) -> Sketch:
    """A mitred polygon web between two radii - every edge straight, every corner a mitre."""
    inner = [_pt(r0, -half + 2 * half * i / n0) for i in range(n0 + 1)]
    outer = [_pt(r1, -half + 2 * half * i / n1) for i in range(n1 + 1)]
    return Polygon(*inner, *reversed(outer), align=None)


def _shard_webs() -> tuple[Sketch, int, float]:
    """The two faceted webs - the inner labrum shield (hub to inner rail) and the outer apron
    (inner rail to outer rail) - pierced by rings of mitred elongated hexes. Returns
    (sketch, aperture count, worst ligament anywhere in the pattern)."""
    r_in_out = R_INNER + INNER_W / 2
    sk = _faceted_panel(R_SPOKE, r_in_out, SH_SHIELD_HALF, 4, 6)
    sk += _faceted_panel(r_in_out - 0.6, ARC_R + 0.6, SH_APRON_HALF, 2, 2)
    holes, count, worst = Sketch(), 0, SH_LIG
    for rings, half, lo, hi in ((SH_HEX_RINGS, SH_SHIELD_HALF, R_SPOKE, R_INNER - INNER_W / 2),
                                (SH_APRON_RINGS, SH_APRON_HALF, r_in_out, ARC_R)):
        for r, b in rings:
            ring, n, _lig = _hex_ring(r, b, half)
            holes += ring
            count += n
        worst = min(worst, rings[0][0] - rings[0][1] - lo, hi - (rings[-1][0] + rings[-1][1]))
        for (r0, b0), (r1r, b1) in zip(rings, rings[1:]):
            worst = min(worst, (r1r - b1) - (r0 + b0))
    for r_step, _dz in SH_STEPS[:-1]:                 # a step line may not run through an aperture
        for rings in (SH_HEX_RINGS, SH_APRON_RINGS):
            for r, b in rings:
                worst = min(worst, abs(abs(r_step - r) - b)) if abs(r_step - r) < b else worst
    return sk - holes, count, worst


def _shard_struts() -> list[tuple[tuple[float, float], tuple[float, float]]]:
    out = [(_pt(R_INNER, a), _pt(ARC_R + 1.0, b)) for a in SH_IN_NODES for b in (a - 15.0, a + 15.0)]
    # the last two brace the inner rail's own ends against the outer rail's ends, so nothing on
    # this part is a free stub hanging in mid air
    out += [(_pt(R_INNER, s * SH_IN_HALF), _pt(ARC_R + 1.0, s * ARC_HALF)) for s in (-1.0, 1.0)]
    return out


def _labrum() -> Sketch:
    """LABRUM - the toothed centre shield between the jaws. A mitred chevron standing exactly
    SH_LABRUM[1] proud of the two rail facets that meet at the outboard prow (with
    SH_OUT_FACETS = 6 theta 0 is a rail VERTEX, the sharpest point on the part)."""
    mid = radians(180.0 / SH_OUT_FACETS / 2)
    rv = ARC_R / cos(mid) + RIM_W                 # radius of the outer polyline's vertices
    lw, lp = SH_LABRUM
    t, rise = tan(mid), lp / cos(mid)             # a line offset lp normal to it rises lp/cos here
    h, m = lw / 2, 2.2                            # half width, mitre
    pts = [(-h, rv - h * t - 3.2), (-h + m, rv - (h - m) * t + rise), (0.0, rv + rise),
           (h - m, rv - (h - m) * t + rise), (h, rv - h * t - 3.2)]
    return Pos(0.0, L) * Polygon(*pts, align=None)


def _shard() -> dict:
    web = Pos(0, L) * Circle(R_HUB)
    out_rail, out_v = _poly_rail(ARC_R, RIM_W, SH_OUT_FACETS)
    in_rail, _iv = _poly_rail(R_INNER - INNER_W / 2, INNER_W, SH_IN_FACETS, half=SH_IN_HALF)
    web += in_rail
    shield, n_hex, lig = _shard_webs()
    web += shield
    members = _spokes(SH_SPOKES, SPOKE_RAKE, R_INNER + 1.5) + _shard_struts()
    for p0, p1 in members:
        web += _bar(p0, p1, STRUT_W)
    web += _tab(*TAB)

    rim = out_rail + _labrum()
    return {"web": web, "rim": rim, "rim_wall": out_rail, "cuts": _hub_cuts(), "nodes": [],
            "members": members, "struts": _shard_struts(),
            "spokes": _spokes(SH_SPOKES, SPOKE_RAKE, R_INNER + 1.5),
            "steps": HUB_STEP + SH_STEPS, "hexes": n_hex, "ligament": lig, "facets": out_v,
            "strut_r": (R_INNER, ARC_R), "rim_w": RIM_W, "claws": ()}


# --- FERAL ------------------------------------------------------------------------------------
def _claw_axis(th: float, h: float) -> list[tuple[float, float, float]]:
    """Base, waist and tip of one claw. The claw is RAKED tangentially toward the outboard prow by
    FR_CLAW_RAKE x its height, so the row reads as a set of hooks rather than a row of cones; the
    steepest lean is 18 deg off vertical, well inside the 45 deg overhang limit."""
    x, y = _pt(ARC_R + FR_RIM_W / 2, th)
    tx, ty = -cos(radians(th)), sin(radians(th))     # tangent, toward decreasing theta
    z0 = Z_LOCAL + RIM_H
    lean = FR_CLAW_RAKE * h * (1.0 if th >= 0 else -1.0)
    return [(x, y, z0),
            (x + tx * lean * 0.40, y + ty * lean * 0.40, z0 + 0.45 * h),
            (x + tx * lean, y + ty * lean, z0 + h - FR_CLAW_TIP)]


def _claw(th: float, h: float) -> Part:
    """A cusped, raked claw standing on the rail top: lofted through three circles so the flank is
    CONCAVE - a tarsal claw, not a traffic cone - with a Ø1.7 tip ball, so a crash lands on a
    blunt point rather than on a needle that snaps and takes the rail with it."""
    (bx, by, bz), (wx, wy, wz), (tx_, ty_, tz) = _claw_axis(th, h)
    body = loft([Pos(bx, by, bz) * Circle(FR_CLAW_RB),
                 Pos(wx, wy, wz) * Circle(FR_CLAW_WAIST * FR_CLAW_RB),
                 Pos(tx_, ty_, tz) * Circle(0.8 * FR_CLAW_TIP)], ruled=True)
    # the ball is WIDER than the loft's top circle on purpose: a ball whose equator coincides with
    # it is a tangent union, and OCCT hands back a solid that meshes into an invalid 3MF
    return body + Pos(tx_, ty_, tz) * Sphere(FR_CLAW_TIP)


def _arc_puncta(r: float, half: float, z_face: float) -> tuple[Part, int, float]:
    """PUNCTA marching along the rail's top cheek. `_style.puncta` places on a planar grid, which a
    cylindrical band is not, so the centres are laid out along the arc here and the dimple itself is
    _style's own spherical cap, under _style's own Ø and depth caps."""
    d, depth = FR_PUNCTA_D, FR_PUNCTA_DEPTH
    assert d <= S.PUNCTA_D_MAX + 1e-9 and depth <= S.PUNCTA_DEPTH_MAX + 1e-9
    rs = (d * d / 4 + depth * depth) / (2 * depth)   # sphere whose cap of `depth` is Ø d
    span = r * radians(2 * half) - 2 * FR_PUNCTA_PITCH
    n = int(span // FR_PUNCTA_PITCH)
    tool, placed = Part(), 0
    for i in range(n):
        th = degrees((-span / 2 + FR_PUNCTA_PITCH * (i + 0.5)) / r)
        if any(abs(th - c) < 5.0 for c, _h in FR_CLAWS):   # clean zone: the claw footprints
            continue
        x, y = _pt(r, th)
        tool += Pos(x, y, z_face + rs - depth) * Sphere(rs)
        placed += 1
    return tool, placed, (FR_RIM_W - d) / 2


def _feral() -> dict:
    web = Pos(0, L) * Circle(R_HUB)
    web += _band(FR_ARC_R - FR_ARC_W / 2, FR_ARC_R + FR_ARC_W / 2, -FR_ARC_HALF, FR_ARC_HALF)
    clip = Pos(0, L) * Circle(ARC_R + FR_RIM_W)
    legs = Sketch()
    for th in FR_LEGS:
        legs += S.lens(_pt(FR_LEG_R0, th), _pt(FR_LEG_R1, th), FR_LEG_HW)
    web += legs & clip
    web += _tab(TAB[0], TAB[1] - 8.0, TAB[2], cusp=14.0)

    rim = _band(ARC_R, ARC_R + FR_RIM_W, -ARC_HALF, ARC_HALF)
    claws = tuple(_claw(th, FR_CLAW_H * f) for th, f in FR_CLAWS)
    pits, n_pit, pit_lig = _arc_puncta(ARC_R + FR_RIM_W / 2, ARC_HALF - 3.0, Z_LOCAL + RIM_H)
    return {"web": web, "rim": rim, "cuts": _hub_cuts(), "nodes": [],
            "members": [], "struts": [], "spokes": [],
            "steps": HUB_STEP + ((1e3, WEB_Z),), "claws": claws, "puncta": pits, "n_puncta": n_pit,
            "puncta_ligament": pit_lig, "rim_w": FR_RIM_W, "legs": len(FR_LEGS)}


# --- assembly ---------------------------------------------------------------------------------
_DESIGNS = {"chassis": _chassis, "shard": _shard, "feral": _feral}


def _design(style: str) -> dict:
    assert style in _DESIGNS, f"unknown style {style!r}; STYLES = {STYLES}"
    return _DESIGNS[style]()


def _zone(r0: float, r1: float) -> Sketch:
    ring = Pos(0, L) * Circle(r1)
    return ring if r0 <= 0 else ring - Pos(0, L) * Circle(r0)


def _grow(region: Sketch, dz: float) -> Part:
    """Extrude a plan region up from the bed plane, FACE BY FACE and fusing as we go: a sketch
    union of shapes that only meet along an edge keeps them as separate coplanar faces, and one
    `extrude` of that sketch returns as many unfused solids, which fails `single_solid`."""
    out = Part()
    for f in region.faces():
        out += extrude(Plane.XY.offset(Z_LOCAL) * f, amount=dz, dir=(0, 0, 1))
    return out


def _solid(d: dict) -> Part:
    """Grow every plan member straight up from the bed plane, then cut once."""
    body = Part()
    r0 = 0.0
    for r1, dz in d["steps"]:
        piece = d["web"] & _zone(r0, min(r1, 400.0))
        if piece.faces():
            body += _grow(piece, dz)
        r0 = r1
    body += _grow(d["rim"], RIM_H)
    for claw in d["claws"]:
        body += claw
    tools = [S.extrude_cut(d["cuts"], Plane.XY.offset(Z_LOCAL - 1.0), RIM_H + 3.0)]
    if d.get("puncta") is not None:
        tools.append(d["puncta"])
    body = body - Compound(children=tools)
    body = body.clean()
    assert body.is_valid, "prop_guard: invalid solid"
    assert len(body.solids()) == 1, f"prop_guard: {len(body.solids())} solid(s)"
    return body


def build(variant: str = "chassis", **overrides) -> dict[str, Part]:
    global _EFFECTIVE
    style = overrides.pop("style", variant if variant in _DESIGNS else "chassis")
    d = _design(style)
    local = _solid(d)
    d["style"] = style
    d["plan_area"] = sum(f.area for f in _plan_face(d).faces())
    _EFFECTIVE = d
    return {LABEL: place_arm(local, P.ARM_PLACEMENTS[ARM])}


def _plan_face(d: dict, structural: bool = False) -> Sketch:
    """The material footprint in plan: every member, every through cut. The styles are compared
    on this, not on the filled outline - the void IS the shape in this family.

    `structural=True` leaves out the style's applied DECORATION (SHARD's 0.8 mm proud LABRUM),
    which is held to the 0.8 mm decorative-feature floor rather than to the 1.2 mm wall floor, and
    whose outline splits the rail into coplanar sub-faces that a 2D opening cannot read."""
    rim = d.get("rim_wall", d["rim"]) if structural else d["rim"]
    return (d["web"] + rim) - d["cuts"]


# --- style metrics (silhouette-first directive, §4.5) -----------------------------------------
def _hull_area(pts) -> float:
    pts = sorted(set((round(x, 4), round(y, 4)) for x, y in pts))
    if len(pts) < 3:
        return 0.0

    def half(seq):
        out = []
        for q in seq:
            while len(out) >= 2 and (out[-1][0] - out[-2][0]) * (q[1] - out[-2][1]) - \
                    (out[-1][1] - out[-2][1]) * (q[0] - out[-2][0]) <= 0:
                out.pop()
            out.append(q)
        return out[:-1]

    hull = half(pts) + half(reversed(pts))
    return abs(sum(hull[i][0] * hull[i - 1][1] - hull[i - 1][0] * hull[i][1]
                   for i in range(len(hull)))) / 2


@lru_cache(maxsize=8)
def _plan_metrics(style: str) -> tuple[float, float, float]:
    """(material footprint area, bbox area, convex-hull deficiency) of one style's plan outline.
    The material footprint, not the filled outline: in CHASSIS the void IS the shape, so comparing
    filled silhouettes would call three very different parts the same half disc."""
    d = _design(style)
    plan = _plan_face(d)
    area = sum(f.area for f in plan.faces())
    bb = plan.bounding_box()
    pts = []
    for f in plan.faces():
        w = f.outer_wire()
        pts += [(p.X, p.Y) for p in (w.position_at(i / 96) for i in range(96))]
    hull = _hull_area(pts)
    return area, bb.size.X * bb.size.Y, (1.0 - area / hull) if hull else 0.0


def _member_angles(members, r_rail: float) -> list[float]:
    """Angle (deg) at which each member meets the rail circle of radius r_rail, measured against
    that circle's tangent. 90 deg is a member coming in dead radial, which the family forbids."""
    out = []
    for p0, p1 in members:
        near, far = sorted((p0, p1), key=lambda q: hypot(q[0], q[1] - L))
        for q in (near, far):
            r = hypot(q[0], q[1] - L)
            if abs(r - r_rail) > 3.0:
                continue
            chord = (p1[0] - p0[0], p1[1] - p0[1])
            n = hypot(*chord) or 1.0
            ur = (q[0] / r, (q[1] - L) / r)
            radial = abs(chord[0] * ur[0] + chord[1] * ur[1]) / n
            out.append(degrees(atan2(radial, max(1e-9, (1 - radial ** 2) ** 0.5))))
    return out


# --- checks -----------------------------------------------------------------------------------
def _plan_min_wall(d: dict, t: float) -> tuple[bool, str]:
    """Minimum wall by a 2D morphological opening of the plan outline - erode by t/2, dilate back,
    look at what did not come back.

    Every member of this part is a prism grown straight up from the bed, so the plan outline IS the
    wall, exactly as `motor_guard._skin_min_wall` argues for the arm skin. `_fit.min_wall`'s 3D
    erode/dilate cannot offset a truss with this many faces and falls back to `ray_thickness`,
    whose documented blind spot is precisely a corner: a ray leaving a face within a fraction of a
    millimetre of a sub-90 deg corner measures the corner, not a wall, and reported 0.90 mm across
    a 2.4 mm rail. The tolerance here mirrors `min_wall`'s own - a few sliver mm at sharp corners
    pass, anything elongated does not.

    Non-prismatic features (the FERAL claws) are checked separately, by their section."""
    half = max(t / 2 - WALL_TOL, 1e-3)
    total, worst, lumps = 0.0, 0.0, 0
    for f in _plan_face(d, structural=True).faces():
        try:
            opened = offset(offset(f, amount=-half, kind=Kind.ARC), amount=half, kind=Kind.ARC)
        except Exception:  # noqa: BLE001 - a face that erodes to nothing is thinner than t
            return False, f"a plan face of {f.area:.1f} mm² does not survive a {half:.2f} mm erosion"
        residual = (Sketch() + f) - opened
        for r in residual.faces():
            if r.area <= 0.01:
                continue
            bb = r.bounding_box()
            total += r.area
            lumps += 1
            worst = max(worst, bb.size.X, bb.size.Y)
    ok = total <= 2.0 and worst <= 3.0
    return ok, (f"{total:.3f} mm² left in {lumps} sliver(s) after a {t} mm opening, "
                f"longest {worst:.2f} mm (sharp corners leave slivers; a thin wall leaves a streak)")


def _motor_guard_envelope() -> Part:
    """A conservative reconstruction of motor_guard's maximum envelope, in arm-local coordinates:
    the arm outline offset by its CLEARANCE + WALL (2.25), unioned with its 23 x 50 landing pad,
    swept from the pad underside (local Z -12) to its rim top (local Z 4.8). Rebuilt here rather
    than imported so a sibling module's work in progress cannot silently disarm this check."""
    from build123d import Rectangle as _Rect
    from build123d import fillet as _fillet
    from build123d import offset as _offset
    base = Face(profiles._outline(L))
    skin = _offset(base, amount=2.25).faces()[0]
    skin = skin & (Pos(0, 84.804 + 150) * _Rect(400, 300))
    pad = Pos(0, L - 3.0) * _fillet(_Rect(23.0, 50.0).vertices(), 6.0)
    return extrude(Plane.XY.offset(-12.0) * (skin + pad), amount=16.8, dir=(0, 0, 1))


def _col(xy, z0: float, z1: float, d: float) -> Part:
    return cylinder(xy[0], xy[1], z0, z1, d)


def checks(parts: dict[str, Part], frame: dict[str, Part], variant: str = "") -> list[tuple[str, bool, str]]:
    g = parts[LABEL]
    d = _EFFECTIVE
    style = d.get("style", variant or "chassis")
    pl = P.ARM_PLACEMENTS[ARM]
    motor = MOTOR_CENTERS[ARM.removeprefix("arm_")]
    rim_w = d["rim_w"]
    out: list[tuple[str, bool, str]] = []

    # --- mating -------------------------------------------------------------------------------
    for i, (bx, by) in enumerate(profiles.motor_bolts(L)):
        xy = P.place(bx, by, pl)
        try:
            assert_coaxial_hole(g, xy, Z_BED + 0.05, Z_BED + FLOOR - 0.05, BOLT_D)
            ok, detail = True, coaxial(g, xy, BOLT_D, Z_BED + 0.05, Z_BED + FLOOR - 0.05)[1]
        except AssertionError as exc:
            ok, detail = False, str(exc)
        out.append((f"motor hole {i} coaxial with the Ø19 bolt circle", ok, detail))
    ok_b, det_b = coaxial(g, motor, BORE_D, Z_BED + 0.05, Z_BED + FLOOR - 0.05)
    out.append((f"Ø{BORE_D} shaft bore coaxial with the motor axis", ok_b, det_b))

    seat = seats_on(g, ARM, Z_BED)
    out.append((f"seated on the {ARM} top face Z {Z_BED}", seat >= 150.0, f"{seat} mm² of real arm face"))

    # --- co-existence and frame clearance ------------------------------------------------------
    hits = interference(g)
    out.append(("clear of every frame part", not hits, f"{hits or 'none'}"))
    v_mg = isect(g, place_arm(_motor_guard_envelope(), pl))
    out.append(("clear of motor_guard's maximum envelope (frame Z -10..6.8)", v_mg < EPS, f"{v_mg:.3f} mm³"))

    # --- the LOCAL prop keep-out (see the module docstring) -------------------------------------
    above = _col(motor, KEEP_Z, PROP_Z + 10.0, 2 * KEEP_R)
    v_keep = isect(g, above)
    out.append((f"nothing above Z {KEEP_Z} inside r {KEEP_R} of the motor centre", v_keep < EPS,
                f"{v_keep:.3f} mm³"))
    band = g - _col(motor, Z_BED - 1.0, KEEP_Z, 2 * KEEP_R)
    up = [v for v in band.vertices() if v.Z >= KEEP_Z + 0.01]
    r_min = min(hypot(v.X - motor[0], v.Y - motor[1]) for v in up) if up else 1e9
    out.append((f"the rim band stands entirely outside r {KEEP_R}", r_min >= KEEP_R - 1e-6,
                f"closest vertex above Z {KEEP_Z} at r {r_min:.3f}"))
    z_top = g.bounding_box().max.Z
    out.append((f"top of the part >= {PROP_CLEAR} mm below the prop plane Z {PROP_Z}",
                z_top <= PROP_Z - PROP_CLEAR + 1e-6, f"max Z {z_top:.2f} vs {PROP_Z - PROP_CLEAR}"))
    rim_top = Z_BED + RIM_H
    out.append((f"rim height {RIM_H} above the arm top face, 8-10 as specified",
                8.0 - 1e-6 <= RIM_H <= 10.0 + 1e-6, f"rim top Z {rim_top}"))
    v_bell = isect(g, _col(motor, Z_BED + FLOOR, PROP_Z, 2 * BELL_R))
    out.append((f"clear of the Ø{2 * BELL_R} 2807 bell envelope above the hub floor", v_bell < EPS,
                f"{v_bell:.3f} mm³"))

    # --- the same part on the other three arms --------------------------------------------------
    for arm in ARM_NAMES:
        if arm == ARM:
            continue
        other = place_arm(deepcopy(_solid(d)), P.ARM_PLACEMENTS[arm])
        h = interference(other)
        own = arm.removeprefix("arm_")
        v_n = prop_disc_violation(other, exclude=(own,))
        v_o = prop_disc_violation(other, z0=OWN_DISC_Z_MAX)
        out.append((f"the same part fits {arm}: no interference, no neighbouring prop disc",
                    not h and v_n < EPS and v_o < EPS,
                    f"{h or 'no overlap'}, {v_n:.3f} mm³ neighbouring, {v_o:.3f} mm³ above Z {OWN_DISC_Z_MAX}"))

    # --- walls, solidity, print ------------------------------------------------------------------
    ok_w, det_w = _plan_min_wall(d, WALL_FLOOR)
    out.append((f"min wall >= {WALL_FLOOR} (2D opening of the prismatic plan outline)", ok_w, det_w))
    claw_min = 2 * FR_CLAW_TIP if d["claws"] else float("inf")
    out.append((f"non-prismatic features >= {WALL_FLOOR} in section",
                claw_min >= WALL_FLOOR - WALL_TOL,
                f"claw tip Ø{2 * FR_CLAW_TIP}, base Ø{2 * FR_CLAW_RB}" if d["claws"] else "none"))
    out.append((f"impact path (rim {rim_w} x {RIM_H}, rails and struts {STRUT_W}) >= {WALL_HIT}",
                min(rim_w, STRUT_W, INNER_W) >= WALL_HIT - 1e-6,
                f"rim {rim_w}, inner rail {INNER_W}, strut {STRUT_W}"))
    ok_s, det_s = single_solid(g)
    out.append(("one watertight solid", ok_s, det_s))
    over = overhangs(g, PRINT[LABEL], material=MATERIAL)
    out.append(("prints hub-floor-down with no unsupported face", not over, "; ".join(over) or "none"))
    return out + _style_checks(g, d, style)


def _style_checks(g: Part, d: dict, style: str) -> list[tuple[str, bool, str]]:
    out: list[tuple[str, bool, str]] = []
    pl = P.ARM_PLACEMENTS[ARM]
    area, bbox_area, deficiency = _plan_metrics(style)
    out.append((f"[{style}] plan footprint {area:.0f} mm² in a {bbox_area:.0f} mm² bbox",
                area > 0, f"hull deficiency {deficiency:.3f}"))

    if style in ("chassis", "shard"):
        ang = _member_angles(d["struts"], ARC_R if style == "shard" else _node_r_out()) + \
            _member_angles(d["struts"], R_INNER)
        ok = bool(ang) and all(50.0 - 0.5 <= a <= 70.0 + 0.5 for a in ang)
        out.append((f"[{style}] every triangulating strut meets a rail at 50-70 deg", ok,
                    f"{len(ang)} joints, {min(ang):.1f}-{max(ang):.1f} deg"))
        sp = _member_angles(d["spokes"], R_INNER)
        out.append((f"[{style}] no hub spoke comes in dead radial (< 86 deg to the rail)",
                    bool(sp) and max(sp) <= 86.0, f"{min(sp):.1f}-{max(sp):.1f} deg"))

    if style == "chassis":
        bad = []
        for cx, cy in d["nodes"]:
            xy = P.place(cx, cy, pl)
            ok_n, _det = coaxial(g, xy, NODE_ID_F * STRUT_W, Z_BED + 0.2, Z_BED + WEB_Z - 0.2)
            if not ok_n:
                bad.append((round(cx, 1), round(cy, 1)))
        out.append((f"[chassis] a ring node eyelet at every one of the {len(d['nodes'])} junctions",
                    not bad, f"missing at {bad or 'nowhere'}"))
        void = 1.0 - area / bbox_area
        out.append(("[chassis] void >= 45 % of the plan bbox - the void IS the shape",
                    void >= 0.45, f"{void:.1%} void"))
        out.append((f"[chassis] serration on the outboard rail edge (Ø{SERR_D} @ {SERR_PITCH})",
                    d["serrations"] >= 80, f"{d['serrations']} bumps"))

    if style == "shard":
        mid = 180.0 / SH_OUT_FACETS
        chord = 2 * (ARC_R / cos(radians(mid / 2))) * sin(radians(mid / 2))
        out.append((f"[shard] rail facets >= {S.FACET_MIN} mm across, normals {mid:.0f} deg apart",
                    chord >= S.FACET_MIN and 18.0 <= mid <= 40.0,
                    f"{SH_OUT_FACETS} facets, chord {chord:.1f} mm"))
        out.append((f"[shard] shield apertures keep a >= {SH_LIG} mm ligament",
                    d["ligament"] >= SH_LIG - 1e-6, f"{d['hexes']} mitred hexes, worst {d['ligament']:.2f} mm"))
        steps = [dz for _r, dz in SH_STEPS]
        out.append(("[shard] stepped web thickness with visible step lines",
                    len(set(steps)) == 3 and min(steps) >= WALL_FLOOR,
                    f"{'/'.join(f'{x:.1f}' for x in steps)} at r {SH_STEPS[0][0]}, {SH_STEPS[1][0]}"))
        lab = _col(P.place(0.0, L + ARC_R + RIM_W + 0.4, pl), Z_BED + 1.0, Z_BED + RIM_H - 1.0, 2.0)
        decor_min = S.DECOR_MATERIALS[MATERIAL]["decor_min"]
        out.append((f"[shard] LABRUM shield {SH_LABRUM[1]} proud of the outboard rail prow, at or "
                    f"above the {decor_min} decorative-feature floor",
                    isect(g, lab) > EPS and SH_LABRUM[1] >= decor_min - 1e-9,
                    f"{isect(g, lab):.2f} mm³ of a probe 0.4 mm outboard of the rail"))

    if style == "feral":
        bad, flanks = [], []
        for (th, f), claw in zip(FR_CLAWS, d["claws"]):
            h = FR_CLAW_H * f
            tx_, ty_, tz = _claw_axis(th, h)[2]
            xy = P.place(tx_, ty_, pl)
            tip = Pos(xy[0], xy[1], tz + P.Z_ARM) * Sphere(0.4)
            frac = isect(g, tip) / tip.volume
            if frac < 0.9:
                bad.append((th, round(frac, 2)))
            rise = 0.45 * h
            run = hypot(FR_CLAW_RB * (1 - FR_CLAW_WAIST), FR_CLAW_RAKE * h * 0.40)
            flanks.append(degrees(atan2(rise, run)))
        out.append((f"[feral] a Ø0.8 ball fits at every claw tip", not bad,
                    f"worst fill {min(1.0, 1.0 if not bad else bad[0][1]):.2f}; thin at {bad or 'nowhere'}"))
        out.append(("[feral] shallowest claw flank >= 50 deg from horizontal (self-supporting)",
                    min(flanks) >= 50.0, f"{min(flanks):.1f}-{max(flanks):.1f} deg"))
        run = [f for _t, f in FR_CLAWS]
        out.append(("[feral] claw heights in a 1 : 0.78 : 0.61 : 0.48 run, tallest outboard",
                    run == sorted(run, reverse=True) and abs(run[0] - 1.0) < 1e-9,
                    f"{[round(FR_CLAW_H * f, 2) for f in run]} mm at theta {[t for t, _f in FR_CLAWS]}"))
        out.append((f"[feral] puncta Ø{FR_PUNCTA_D} <= {S.PUNCTA_D_MAX}, depth {FR_PUNCTA_DEPTH} "
                    f"<= {S.PUNCTA_DEPTH_MAX}, ligament to the cheek edge",
                    d["n_puncta"] > 20 and d["puncta_ligament"] >= 1.2,
                    f"{d['n_puncta']} pits, {d['puncta_ligament']:.2f} mm to the cheek edge"))

    metrics = {s: _plan_metrics(s) for s in STYLES}
    worst_pair, worst_sep = None, 1e9
    for i, a in enumerate(STYLES):
        for b in STYLES[i + 1:]:
            da = abs(metrics[a][0] - metrics[b][0]) / max(metrics[a][0], metrics[b][0])
            dh = abs(metrics[a][2] - metrics[b][2])
            sep = max(da / 0.12, dh / 0.10)
            if sep < worst_sep:
                worst_sep, worst_pair = sep, (a, b, da, dh)
    a, b, da, dh = worst_pair
    out.append(("the three plan outlines differ pairwise by > 12 % area or > 0.10 hull deficiency",
                worst_sep >= 1.0, f"worst pair {a}/{b}: {da:.1%} area, {dh:.3f} deficiency; "
                                  f"areas {[round(metrics[s][0]) for s in STYLES]}"))
    return out
