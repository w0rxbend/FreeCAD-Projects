"""Closed-ring prop guard on the arm tip - the full-circle sibling of the half-ring `prop_guard`.

`prop_guard` protects the outboard 180 deg. A tree strike on a 7-inch long-range cruise arrives
from any bearing, and the two failure modes that end a flight - a branch coming in between the
props, and a wingtip clip on a trunk - both land on the INBOARD half that the half ring leaves
bare. This part closes the circle.

    STYLES = ("filigree", "brutalist", "origami")

WHY THE CIRCLE CANNOT ACTUALLY CLOSE - the measured finding
------------------------------------------------------------
A ring whose inner radius is 92.4 (PROP_KEEPOUT_R 91.9 + 0.5) cannot be a closed circle on this
airframe, and the number says so:

    front_right (126.362, 83.785) to rear_right (115.721, -98.437) = 182.532 mm
    92.4 + 91.9 = 184.300 mm  ->  the ring's inner circle reaches 1.768 mm INSIDE the
    diagonal neighbour's keep-out disc, over a window of +- 7.921 deg.

Worse, the conflict has no way out. Along that bearing a legal point must be at own-radius
>= 92.4 AND at >= 91.9 from the neighbour, i.e. own-radius <= 90.632. The two conditions are
mutually exclusive, so no closed curve that encircles this prop and misses the neighbour's disc
exists at all - it would have to encircle BOTH motors. The 303 mm wheelbase simply does not leave
room: tip to tip the diagonal props clear each other by 182.532 - 2 x 88.9 = 4.732 mm, and their
3 mm margins overlap by 1.268 mm.

So the ring carries ONE measured relief window, cut by the real neighbour discs (+ 0.35 mm) in
arm-local coordinates. The saving grace is that the window lands in the same place on every arm:
the diagonal neighbour sits at arm-local theta 124.142 deg from the front arms and 125.458 deg
from the rear arms - 1.316 deg apart - so a single window cut with BOTH discs serves all four
placements, and ONE part still fits all four positions. The window faces the diagonal prop, which
is itself the obstruction there, so nothing worth guarding is behind it.

The ring is nevertheless a closed LOOP: the flat cutwork web inside r 92.4 runs the full 360 deg
(only its outer edge is trimmed at the window), so the part is one solid and the two free ends of
the wall are tied together at the root.

MOUNTING - identical to `prop_guard`, deliberately
---------------------------------------------------
The D19 motor bolt circle at the arm-tip motor centre, 4 x M3 at 45 deg, 13.435 mm adjacent. The
2.0 mm hub floor is clamped BETWEEN the carbon and the motor and raises the motor 2.0 mm, so the
screws grow 2 mm over stock. It also seats on the arm top face at frame Z 7 and is anti-rotated by
a notched tab running back along the arm shaft. EXCLUSIVE with `prop_guard`: they occupy the same
four screws.

THE RADIAL BUDGET - the second measured finding
-----------------------------------------------
The ring cannot be wide, either. Sweeping an annulus at frame Z 7-28 against the frame on all
four placements: r 96.1 clears everything, r 96.2 closes to 0.12 mm on standoff_rear_tip (Ø6 at
(±16.5, -94), 99.32 mm from the rear motor centre) and r 96.4 touches it. With the inner face
pinned at 92.4 the WHOLE COLLAR - rim, wall, scallops, pleats, the lot - lives inside a 3.7 mm
annulus. Every variant therefore states its radial envelope and `checks()` measures the
outermost vertex against 96.1. It is also why ORIGAMI's collar is a 16-gon and not the 24 the
brief asks for: a regular N-gon folds through 360/N and the language allows only
{22.5, 45, 67.5}, so N = 16 is the only convex ring in the set, and its facet midpoints land
exactly on 92.4 with 1.80 mm of sheet left inside 96.05.

THE PROP KEEP-OUT, EXACTLY
---------------------------
  * the ring wall lives at r >= 92.4 from its own motor - outside every disc, at any height;
  * the web, the spokes and the hub are inside the own disc but capped at frame Z 22.0 =
    `_fit.OWN_DISC_Z_MAX`, which is what `OWN_PROP_DISC` buys; a cylinder cut at r 91.9 above
    Z 22 enforces that by construction rather than by arithmetic;
  * the buttresses reach Z 22 only at r 92.4; at r 91.9 they are at Z 21.3;
  * the relief window keeps every neighbouring disc at exactly 0.000 mm.

The prop of a 2807 sits at frame Z 32; the rim tops out at Z 28, 4 mm under the blades and 12 mm
higher than anything else in the catalogue reaches, which is the point of the part.

PRINTING
--------
Bed normal (0, 0, -1): frame Z 7 is the bed plane and the whole part grows upward from it. The
wall apertures are pointed lancets and shear-sided slots, never flat lintels, so there is not one
downward face and not one bridge to declare. Buttress tops rise at 53 deg, which faces up.

MATERIAL AND MASS
-----------------
TPU 95A. This is the heaviest part in the catalogue - it is a 590 mm long, 21 mm tall wall - and
`checks()` reports the measured volume of every variant so the cost is visible before you print
four of them. FILIGREE is the light one, BRUTALIST is deliberately twice the mass.
"""

from functools import lru_cache
from math import acos, atan2, ceil, cos, degrees, hypot, radians, sin

from build123d import (Axis, Circle, Compound, Cone, Kind, Part, Plane, Polygon, Pos, Rectangle,
                       Sketch, SlotOverall, Vector, extrude, offset)

from tigerbee import params as P
from tigerbee import profiles
from tigerbee.accessories._common import *  # noqa: F401,F403
from tigerbee.accessories._fit import ray_thickness
from tigerbee.accessories import _style as S

NAME = "prop_guard_ring"
TITLE = "Closed-ring prop guard (arm tip, full circle)"
MATERIAL = "TPU95A"
STYLES_LOCAL = ("filigree", "brutalist", "origami")

VARIANTS = {
    "filigree": {**({"style": "filigree"} if "filigree" in STYLES else {}),
                 "notes": "ornamental cutwork on a rigid spine: a 2.4 mm spine on each of 6 "
                          "spokes, a 1.4 mm two-radius scroll net (R 9 / 4.5, tangent, pitch "
                          "1.6 R) mirrored about every spoke with a Ø4.0 ring node at all 144 "
                          "junctions, 42 pointed lancets through the wall and a scalloped rim "
                          "edge with one arc cusp per scroll. 41.9 cm³, about 51 g."},
    "brutalist": {**({"style": "brutalist"} if "brutalist" in STYLES else {}),
                  "notes": "one poured slab: a 3.0 mm constant-section wall, 5 square-section "
                           "spokes, one rectangular void per web sector, radial board-marking "
                           "grooves 0.6 x 0.3 at 2.4 pitch, a solid board-marked collar and a "
                           "2.0 mm deep cast-in wordmark on a 6 mm plaque. The wall is "
                           "crenellated - one rectangular void per panel, 40.6 %, open at the "
                           "top so there is no lintel. No radius above 0.3 anywhere that is not "
                           "a bolt hole. 46.5 cm³, about 56 g - the heavy one, by design."},
    "origami": {**({"style": "origami"} if "origami" in STYLES else {}),
                "notes": "one folded sheet: a 16-facet collar (the only convex ring whose vertex "
                         "fold is 22.5 deg - 24 segments would fold through 15) with a 32-tooth "
                         "sawtooth crown at 22.5 deg, 8 folded V-channel spokes with standing "
                         "seams, 88 parallelogram ladder slots sheared 45 deg and 64 rhombus "
                         "collar apertures on 67.5 deg edges. 37.2 cm³, about 45 g."},
}
ASSEMBLY_VARIANT = "filigree"

ARM = "arm_front_right"          # the placement build() returns; one part fits all four
LABEL = "prop_guard_ring"
PRINT = {LABEL: (0, 0, -1)}
OWN_PROP_DISC = {LABEL: ARM.removeprefix("arm_")}
EXCLUSIVE = ("prop_guard",)
MOUNTS = ("the Ø19 motor bolt circle at the arm-tip motor centre (4 x M3 at 45 deg, 13.435 mm "
          "adjacent) - the hub floor is clamped between the carbon and the motor",
          "arm_<corner> top face Z 7 (the hub floor and the anti-rotation tab seat on it)",
          "the arm shaft, local y 68-108, via the tab's two zip-tie notches")
HARDWARE = ("4 x M3 x 10 motor screws per guard when fitted alone (2 mm hub floor + 5 mm carbon "
            "+ 3 mm into the motor)",
            "4 x M3 x 12 when motor_guard is also fitted",
            "2 x 2.5 mm zip tie through the tab notches")
NOTES = ("A closed ring is geometrically impossible on a 303 mm wheelbase: the diagonal props' "
         "3 mm keep-out margins overlap by 1.268 mm, so the ring carries one measured relief "
         "window cut by the real neighbour discs. It lands at arm-local theta 124.1-125.5 deg on "
         "every arm, so one part still fits all four. Coverage is reported by checks(). "
         "HEAVY: this is the largest part in the catalogue - 37.2 cm³ (origami) to 46.5 cm³ "
         "(brutalist), so 45-56 g each in TPU 95A and 180-225 g for a set of four. checks() "
         "prints the measured volume of every variant so the cost is visible before you print. "
         "The ring is also the widest thing on the airframe: the radial budget is 96.1 mm from "
         "the motor centre, measured against the rear-tip standoffs. "
         "Sits BETWEEN the carbon and the motor and raises the motor 2.0 mm, so use screws 2 mm "
         "longer than the build uses today. EXCLUSIVE with prop_guard - same four screws.")

# --- parameters (mm; arm-local plan: motor at (0, L). Z values are FRAME Z) --------------------
L = P.ROOT_TO_MOTOR              # 114.804
DZ = P.Z_ARM                     # 2.0: frame Z = local Z + DZ
Z_BED = Z_ARM_TOP                # 7.0 frame: arm top face = hub floor underside = the bed plane
FLOOR = 2.0                      # hub floor clamped between the carbon and the motor
Z_HUB = Z_BED + FLOOR            # 9.0
Z_CAP = OWN_DISC_Z_MAX           # 22.0: nothing inside r 91.9 above this, by construction
RIM_H = 6.0                      # rim height in Z, as specified
Z_RIM1 = Z_CAP + RIM_H           # 28.0: top of the part (prop face is at Z 32)

R_IN = 92.4                      # ring inner radius = PROP_KEEPOUT_R 91.9 + 0.5
R_HUB = 20.0                     # hub disc radius
R_SPOKE = 18.5                   # web members start here, just outside the Ø36.6 2807 bell
BELL_R = 18.3
BORE_D = P.D_MOTOR_BORE          # 6.5 shaft bore
BOLT_D = D_M3_THRU               # 3.4
GUSS_RUN = 9.0                   # buttress radial run; rise Z 10 -> 22 gives 53 deg
RELIEF_GAP = 0.35                # extra clearance cut round every neighbouring keep-out disc
TAB = (12.0, 68.0, 108.0)        # anti-rotation tab: width, local y0, y1
TAB_NOTCH = (3.0, 1.5)           # zip-tie notch length x depth, both edges
TAB_NOTCH_Y = (75.0, 82.0)       # both behind motor_guard's rear edge (local y
#                                  84.804) and >= 5.5 mm clear of the tab's own end,
#                                  which at 2.5 mm left a sub-3 mm ligament
WALL_FLOOR = MATERIALS[MATERIAL]["wall"]        # 1.2
WALL_HIT = MATERIALS[MATERIAL]["wall_impact"]   # 2.0

# per-style section law: (wall for min_wall, web height, skirt width, rim width, spokes)
SECTION = {"filigree":  dict(wall=1.4, web_z=2.4, skirt_w=3.2, rim_w=3.2, spokes=6),
           "brutalist": dict(wall=3.0, web_z=3.0, skirt_w=3.0, rim_w=3.0, spokes=5),
           "origami":   dict(wall=1.8, web_z=1.8, skirt_w=1.8, rim_w=3.65, spokes=8)}

# FILIGREE
FG_SPINE = 2.4                   # structural spine width (spokes and the rim circle)
FG_RIBBON = 1.4                  # scroll ribbon width
FG_NODE_D = 4.0                  # ring node OD at every scroll junction
FG_SCROLL_R = 9.0                # the large scroll radius R; the small one is 0.5 R
FG_NET_R0 = 70.0                 # scroll net zone: r 70 -> 91.4, inside the lancets
FG_NET_R = 80.2                  # scroll row radius: R 9 + a Ø4 node reaches 91.2,
#                                  just inside the lancet cutters at 91.4, so no
#                                  aperture ever grazes the net and feathers it
FG_LANCET_W, FG_LANCET_PIER = 9.6, 4.0   # pointed-arch apertures in the wall
FG_LANCET_SPRING, FG_LANCET_APEX = 13.0, 19.5   # 53.5 deg flanks: an arch, not a lintel
FG_SCALLOP_R, FG_SCALLOP_D = 5.0, 0.9    # rim outer-edge scallop radius and depth

# BRUTALIST
BR_SPOKE_W = 3.0                 # square section: 3.0 wide x 3.0 tall
BR_VOID_FRAC = 0.44              # rectangular void as a fraction of each web sector
BR_GROOVE_W, BR_GROOVE_D, BR_GROOVE_PITCH = 0.6, 0.3, 2.4
BR_GROOVE_R = (74.0, 92.4)       # board-marking zone on the web top face
BR_COLLAR_R0 = 84.4              # the solid board-marked web collar
BR_VOID_L, BR_VOID_D = 60.0, 13.0
BR_WALL_VOID_W, BR_WALL_VOID_Z = 55.0, 10.0   # crenellation: open at the top, no lintel
BR_CHAMFER = 1.0
BR_MARK = 2.0                    # wordmark deboss depth
BR_MARK_SIZE = 22.0              # exactly _style.MARK_MIN['wordmark']. Measured: at 24 and 26
#                                  one glyph of TIGERBEE cuts an invalid face, and at 28 the
#                                  result is valid but will not survive a STEP round trip. 22
#                                  is valid and round-trips to the millimetre.
BR_PLINTH = (34.0, 15.0)         # the cast-in plaque: 6 mm thick so 2.0 deep leaves 4.0
BR_PLINTH_R, BR_PLINTH_Z = 32.0, 13.0   # 13.0, not 12.0: a 2.0 deboss floor at Z 11
#                                  avoids landing coplanar with the Z 10 web top,
#                                  which OCCT resolves into an invalid solid.

# ORIGAMI
OR_SEGS = 24                     # rim segments; every rim edge straight
OR_FOLD = 22.5                   # the only fold angle used, from the set {22.5, 45, 67.5}
OR_SHEET = 1.8
OR_SHEET_SEAM = 5.0              # standing-seam height above the flange
OR_FLANGE = 7.0                  # V-channel flange width in plan
OR_SLOT_W, OR_SLOT_L, OR_SLOT_PITCH = 1.6, 2.6, 5.6   # sheared ladder slots
OR_AP_A, OR_AP_B, OR_AP_Z = 3.5, 1.45, (13.0, 22.5)   # rhombus collar apertures:
#                                  every edge at 67.5 deg, from the same fold set

_EFFECTIVE: dict = {}


# --- polar helpers about the motor centre, in arm-local XY ------------------------------------
def _pt(r: float, th: float) -> tuple[float, float]:
    """Arm-local point at radius r, angle th (deg) off the outward arm direction (+Y)."""
    a = radians(th)
    return (r * sin(a), L + r * cos(a))


def _arc(r: float, a0: float, a1: float, n: int | None = None) -> list[tuple[float, float]]:
    n = max(2, int(ceil(abs(a1 - a0) / 3.0))) if n is None else n
    return [_pt(r, a0 + (a1 - a0) * i / n) for i in range(n + 1)]


def _band(r0: float, r1: float) -> Sketch:
    """Full annulus about the motor centre."""
    return Pos(0, L) * (Circle(r1) - Circle(r0))


def _sector(r: float, a0: float, a1: float, step: float = 4.0) -> Sketch:
    n = max(2, int(ceil((a1 - a0) / step)))
    return Polygon((0.0, L), *[_pt(r, a0 + (a1 - a0) * i / n) for i in range(n + 1)], align=None)


def _bar(p0, p1, w: float) -> Sketch:
    """Capsule between two points."""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    n = hypot(dx, dy)
    if n < 1e-9:
        return Pos(*p0) * Circle(w / 2)
    return Pos((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2) * \
        SlotOverall(n + w, w).rotate(Axis.Z, degrees(__import__("math").atan2(dy, dx)))


def _ribbon(pts, w: float) -> Sketch:
    """A constant-width ribbon following a polyline - the filigree scroll generator."""
    sk = Sketch()
    for a, b in zip(pts, pts[1:]):
        sk += _bar(a, b, w)
    return sk


def _radial_strip(th: float, r0: float, r1: float, w: float) -> Sketch:
    """A straight radial bar of width w from radius r0 to r1 at bearing th (capsule ends)."""
    return _bar(_pt(r0, th), _pt(r1, th), w)


def _radial_rect(th: float, r0: float, r1: float, w: float) -> Sketch:
    """The same bar with SQUARE ends - brutalist's section law: no radius above 0.3 anywhere."""
    return Pos(*_pt((r0 + r1) / 2, th)) * Rectangle(w, r1 - r0).rotate(Axis.Z, -th)


@lru_cache(maxsize=1)
def _neighbour_centres() -> tuple[tuple[float, float], ...]:
    """Every foreign motor centre that can reach this ring, in ARM-LOCAL plan coordinates, for
    EVERY one of the four placements. Cutting all of them at once is what makes one part fit all
    four arms: the diagonal neighbour lands at theta 124.142 deg from a front arm and 125.458 deg
    from a rear arm, so the two windows overlap into one."""
    out: list[tuple[float, float]] = []
    for arm, pl in P.ARM_PLACEMENTS.items():
        o = P.place(0.0, 0.0, pl)
        ex = (P.place(1.0, 0.0, pl)[0] - o[0], P.place(1.0, 0.0, pl)[1] - o[1])
        ey = (P.place(0.0, 1.0, pl)[0] - o[0], P.place(0.0, 1.0, pl)[1] - o[1])
        det = ex[0] * ey[1] - ex[1] * ey[0]
        own = MOTOR_CENTERS[arm.removeprefix("arm_")]
        for name, f in MOTOR_CENTERS.items():
            if name == arm.removeprefix("arm_"):
                continue
            if hypot(f[0] - own[0], f[1] - own[1]) - R_IN - PROP_KEEPOUT_R > 6.0:
                continue
            dx, dy = f[0] - o[0], f[1] - o[1]
            a = (dx * ey[1] - dy * ey[0]) / det
            b = (ex[0] * dy - ex[1] * dx) / det
            if not any(hypot(a - u, b - v) < 0.05 for u, v in out):
                out.append((round(a, 4), round(b, 4)))
    return tuple(out)


@lru_cache(maxsize=1)
def _relief_plan(r_clip: float = 96.1) -> Sketch:
    """The relief window: the neighbouring keep-out discs (+ RELIEF_GAP), plus a radial-ended
    sector over each one.

    Cutting the collar with the bare disc is correct but ugly and unprintable at the ends - the
    arc leaves the 3.2 mm band running out to a feather edge over 3.5 mm, which is a knife edge
    in TPU and reads as damage. The sector squares the window off on two radial lines at the
    angle where the disc first bites at r_clip, so the collar ends on a full-section face. It
    removes a little more material than the keep-out demands, which is the right way round."""
    sk = Sketch()
    for c in _neighbour_centres():
        sk += Pos(*c) * Circle(PROP_KEEPOUT_R + RELIEF_GAP)
        dist = hypot(c[0], c[1] - L)
        bearing = degrees(atan2(c[0], c[1] - L))
        rad = PROP_KEEPOUT_R + RELIEF_GAP
        cosa = (r_clip ** 2 + dist ** 2 - rad ** 2) / (2 * r_clip * dist)
        if -1.0 < cosa < 1.0:
            half = degrees(acos(cosa))
            sk += _band(R_IN - 2.0, r_clip + 4.0) & _sector(r_clip + 8.0, bearing - half,
                                                            bearing + half)
    return sk


@lru_cache(maxsize=1)
def _feather_band(t: float = 2.2) -> Part:
    """The strip of part just inside the relief window. The window is cut by the REAL neighbouring
    keep-out disc, so wherever that arc grazes a ribbon or a facet tangentially it leaves a feather
    edge - a free edge that tapers to nothing, not a wall between two loaded faces. It is declared
    here so the wall measurement can skip it and still be a wall measurement; its extent is
    reported in the check row."""
    sk = Sketch() + [Pos(*c) * Circle(PROP_KEEPOUT_R + RELIEF_GAP + t) for c in _neighbour_centres()]
    return S.extrude_cut(sk - _relief_plan(), Plane.XY.offset(_zl(Z_BED) - 2.0), Z_RIM1 + 4.0)


@lru_cache(maxsize=1)
def _relief_solid() -> Part:
    return S.extrude_cut(_relief_plan(), Plane.XY.offset(Z_BED - DZ - 2.0), Z_RIM1 + 4.0)


def _zl(z_frame: float) -> float:
    """FRAME Z -> ARM-LOCAL Z (place_arm() adds P.Z_ARM = 2.0 back)."""
    return z_frame - DZ


def _grow(region: Sketch, z0: float, z1: float) -> Part:
    """Extrude a plan region between two FRAME heights, FACE BY FACE and fusing as we go: one
    extrude of a sketch whose shapes only meet along an edge returns that many unfused solids."""
    out = Part()
    for f in region.faces():
        if f.area < 1e-6:
            continue
        out += extrude(Plane.XY.offset(_zl(z0)) * f, amount=z1 - z0, dir=(0, 0, 1))
    return out


@lru_cache(maxsize=1)
def _cone_cutter() -> Part:
    """Everything above the buttress ramp and above the own-disc ceiling, in one tool:
      * r < R_IN - GUSS_RUN above Z 10  (the web stays flat inboard)
      * the 53 deg ramp from (Z 10, r 83.4) to (Z 22, r 92.4)
      * r < 91.9 above Z 22             (OWN_DISC_Z_MAX, enforced by construction)"""
    r0, z0, z1 = R_IN - GUSS_RUN, _zl(Z_BED + 3.0), _zl(Z_CAP)
    flat = cylinder(0.0, L, z0, z0 + 40.0, 2 * r0)
    ramp = Pos(0, L, z0) * Cone(r0, R_IN, z1 - z0, align=(Align.CENTER, Align.CENTER, Align.MIN))
    cap = cylinder(0.0, L, z1, z1 + 40.0, 2 * PROP_KEEPOUT_R)
    return flat + ramp + cap


def _hub_cuts(style: str) -> Sketch:
    """Shaft bore and the four M3 through holes on the Ø19 motor bolt circle."""
    cut = Pos(0, L) * Circle(BORE_D / 2)
    for bx, by in profiles.motor_bolts(L):
        cut += Pos(bx, by) * Circle(BOLT_D / 2)
    return cut


def _tab(width: float = TAB[0], y0: float = TAB[1], y1: float = TAB[2]) -> Sketch:
    """Anti-rotation tab on the arm shaft top, notched both edges for two zip ties."""
    sk = Pos(0.0, (y0 + y1) / 2) * Rectangle(width, y1 - y0)
    nl, nd = TAB_NOTCH
    for y in TAB_NOTCH_Y:
        for s in (-1, 1):
            sk -= Pos(s * (width / 2 - nd / 2), y) * Rectangle(nd, nl)
    return sk


def _aperture(th: float, profile_pts, r0: float, r1: float) -> Part:
    """A wall aperture cut radially through the ring at bearing th. `profile_pts` are
    (tangential, FRAME Z) pairs in the vertical plane at that bearing - a pointed lancet, a
    sheared parallelogram, whatever the style asks for. Extruding radially means the opening
    never has a flat lintel, so nothing in this part needs support or a declared bridge."""
    a = radians(th)
    u = Vector(sin(a), cos(a), 0.0)          # radial outward
    x_dir = Vector(-cos(a), sin(a), 0.0)     # tangential, chosen so the plane's +Y is world +Z
    origin = Vector(*_pt(r0, th), 0.0)
    pl = Plane(origin=origin, x_dir=x_dir, z_dir=u)
    sk = Polygon(*[(t, _zl(z)) for t, z in profile_pts], align=None)
    return extrude(pl * sk, amount=r1 - r0)


# --- FILIGREE ---------------------------------------------------------------------------------
def _scroll_nodes(spokes: int) -> list[tuple[float, float]]:
    """One scroll node per (sector, column), placed symmetrically about every sector centreline so
    the net is mirrored about each spine. Tangential pitch is 1.6 R at the net radius, as the
    filigree law asks."""
    per = max(2, int(round((2.0 * 3.141592653589793 * FG_NET_R / spokes) / (1.6 * FG_SCROLL_R))))
    step = 360.0 / spokes / per
    return [(FG_NET_R, -180.0 + 360.0 * k / spokes + step * (j + 0.5))
            for k in range(spokes) for j in range(per)]


def _scroll(r: float, th: float) -> tuple[Sketch, list[tuple[float, float]]]:
    """One two-radius scroll: a 1.4 mm ribbon on radius R and a second on 0.5 R meeting it
    tangentially. No straight member anywhere - that is what separates filigree from chassis.
    Returns (ribbon, junction points where a ring node goes)."""
    w, R = FG_RIBBON, FG_SCROLL_R
    c_big = _pt(r, th)
    c_small = _pt(r + R / 2, th)
    big = Pos(*c_big) * (Circle(R + w / 2) - Circle(R - w / 2))
    small = Pos(*c_small) * (Circle(R / 2 + w / 2) - Circle(R / 2 - w / 2))
    return big + small, [_pt(r + R, th), _pt(r - R, th)]


def _filigree() -> dict:
    sec = SECTION["filigree"]
    n = sec["spokes"]
    angles = [-180.0 + 360.0 * k / n for k in range(n)]
    web = Pos(0, L) * Circle(R_HUB)
    for th in angles:                       # the spine: one 2.4 mm member per load path
        web += _radial_strip(th, R_SPOKE - 1.0, R_IN + sec["rim_w"], FG_SPINE)
    web += _tab()
    centres = _scroll_nodes(n)
    nodes: list[tuple[float, float]] = []
    net = Sketch()
    for r, th in centres:
        sk, junctions = _scroll(r, th)
        net += sk
        nodes += junctions
    # the junctions BETWEEN neighbouring scrolls: two scroll circles of radius R whose centres are
    # 1.6 R apart cross at two points, and the material there runs out to a cusp unless the
    # junction is noded. That is what "a ring node at every junction" is for, and it is also what
    # keeps the net above its 1.4 mm section.
    for k, (r, th) in enumerate(centres):
        r2, th2 = centres[(k + 1) % len(centres)]
        c0, c1 = _pt(r, th), _pt(r2, th2)
        dx, dy = c1[0] - c0[0], c1[1] - c0[1]
        dist = hypot(dx, dy)
        if 1e-6 < dist < 2 * FG_SCROLL_R:
            hx, hy = dx / dist, dy / dist
            off = (FG_SCROLL_R ** 2 - (dist / 2) ** 2) ** 0.5
            mx, my = c0[0] + hx * dist / 2, c0[1] + hy * dist / 2
            nodes += [(mx - hy * off, my + hx * off), (mx + hy * off, my - hx * off)]
    for c in nodes:                         # Ø4.0 ring node at every scroll junction
        net += Pos(*c) * Circle(FG_NODE_D / 2)
    net &= _band(FG_NET_R0, R_IN - 1.0)
    web += net

    # pointed lancets in the wall: an arch, never a lintel
    circ = 2.0 * 3.141592653589793 * R_IN
    n_ap = max(8, int(circ // (FG_LANCET_W + FG_LANCET_PIER)))
    prof = [(-FG_LANCET_W / 2, Z_BED - 1.0), (FG_LANCET_W / 2, Z_BED - 1.0),
            (FG_LANCET_W / 2, FG_LANCET_SPRING), (0.0, FG_LANCET_APEX),
            (-FG_LANCET_W / 2, FG_LANCET_SPRING)]
    # phased half a pitch off the spokes: 42 lancets over 6 spokes is exactly 7 apiece, so an
    # unphased run would put a 9.6 mm aperture straight through every spine.
    aps = [_aperture(-180.0 + 360.0 * (i + 0.5) / n_ap, prof, R_IN - 1.0, R_IN + sec["rim_w"] + 1.0)
           for i in range(n_ap)]

    # scalloped rim edge: one arc cusp per scroll node
    scal = Sketch()
    for _r, th in centres:
        scal += Pos(*_pt(R_IN + sec["rim_w"] + FG_SCALLOP_R - FG_SCALLOP_D, th)) * Circle(FG_SCALLOP_R)
    return {"web": web, "net": net, "skirt": _band(R_IN, R_IN + sec["skirt_w"]),
            "rim": _band(R_IN, R_IN + sec["rim_w"]) - scal, "cuts": _hub_cuts("filigree"),
            "apertures": aps, "gusset_th": angles, "gusset_w": FG_SPINE,
            "outer_r": R_IN + sec["rim_w"], "r_clip": R_IN + sec["rim_w"], "r_env": sec["rim_w"], "n_lancet": n_ap, "n_scroll": len(centres), "n_node": len(nodes),
            "net_zone": (FG_NET_R0, R_IN - 1.0), "sec": sec, "deboss": None, "grooves": (),
            "thin_allow": (_feather_band(),
                           S.extrude_cut(Sketch() + [Pos(*_pt(r + FG_SCROLL_R, th)) * Circle(FG_NODE_D / 2 + 0.4)
                                                     for r, th in _scroll_nodes(n)],
                                         Plane.XY.offset(_zl(Z_BED) - 2.0), Z_RIM1 + 4.0))}


# --- BRUTALIST --------------------------------------------------------------------------------
def _br_void(th: float, r_c: float, half_len: float, half_dep: float) -> Sketch:
    """A true RECTANGLE (brutalist allows rectangles and 45 deg cuts, nothing else) laid across
    the collar at bearing th. Sharp corners; never a field of small holes."""
    return Pos(*_pt(r_c, th)) * Rectangle(2 * half_len, 2 * half_dep).rotate(Axis.Z, -th)


def _brutalist() -> dict:
    sec = SECTION["brutalist"]
    n = sec["spokes"]
    angles = [-180.0 + 360.0 * k / n for k in range(n)]
    mids = [a + 180.0 / n for a in angles]
    web = Pos(0, L) * Circle(R_HUB)
    for th in angles:
        web += _radial_rect(th, R_SPOKE - 1.0, R_IN + sec["rim_w"], BR_SPOKE_W)
    web += _tab()
    plinth = Pos(0, L - BR_PLINTH_R) * Rectangle(BR_PLINTH[0], BR_PLINTH[1])
    web += plinth
    # The collar is SOLID. A straight-sided rectangle inside a curved band cannot keep a 3.0 mm
    # ligament at its corners - measured: a 60 x 13 void in a 74-92.4 collar breaks out through
    # the outer edge and leaves 28 mm² of sub-3 mm crescent - and brutalist does not allow a
    # curved-sided void. The one rectangular void per face therefore lives in the WALL panels,
    # where it is a crenellation and needs no lintel either.
    collar = _band(BR_COLLAR_R0, R_IN)
    web += collar

    # board marking: radial grooves, one direction, 0.6 x 0.3 at 2.4 pitch, on the collar top face
    n_gr = max(12, int(2.0 * 3.141592653589793 * BR_COLLAR_R0 / BR_GROOVE_PITCH))
    # each run is cut from ITS OWN face: a groove cut at the collar's Z into the 6 mm plaque would
    # be a buried slot with a downward roof, which is 35 unsupported faces and no board marking.
    grooves = [(Sketch() + [_radial_strip(-180.0 + 360.0 * i / n_gr, BR_COLLAR_R0 + 0.8,
                                          R_IN - 0.8, BR_GROOVE_W) for i in range(n_gr)],
                Z_BED + sec["web_z"]),
               (Sketch() + [_radial_strip(-180.0 + 360.0 * i / n_gr, BR_PLINTH_R - 6.0,
                                          BR_PLINTH_R + 6.0, BR_GROOVE_W) for i in range(n_gr)],
                BR_PLINTH_Z)]

    # one rectangular void per wall panel, open at the top: a crenellation, so no lintel to bridge
    prof = [(-BR_WALL_VOID_W / 2, BR_WALL_VOID_Z), (BR_WALL_VOID_W / 2, BR_WALL_VOID_Z),
            (BR_WALL_VOID_W / 2, Z_RIM1 + 2.0), (-BR_WALL_VOID_W / 2, Z_RIM1 + 2.0)]
    aps = [_aperture(th, prof, R_IN - 1.0, R_IN + sec["rim_w"] + 1.0) for th in mids]
    panel = 2.0 * 3.141592653589793 * R_IN / n * (Z_RIM1 - Z_BED)
    assert S.mark_fits("wordmark", BR_MARK_SIZE), "wordmark below its minimum size"
    deboss = S.mark("wordmark", BR_MARK_SIZE, "deboss", (0.0, L - BR_PLINTH_R, _zl(BR_PLINTH_Z)),
                    depth=BR_MARK, text="TIGERBEE")
    return {"web": web, "skirt": _band(R_IN, R_IN + sec["skirt_w"]),
            "rim": _band(R_IN, R_IN + sec["rim_w"]), "cuts": _hub_cuts("brutalist"),
            "apertures": aps, "gusset_th": angles, "gusset_w": BR_SPOKE_W, "sec": sec,
            "deboss": deboss, "grooves": grooves, "n_groove": n_gr,
            "plinth": (plinth, BR_PLINTH_Z), "mark_size": BR_MARK_SIZE, "square_ends": True,
            "outer_r": R_IN + sec["rim_w"], "r_clip": R_IN + sec["rim_w"], "r_env": sec["rim_w"],
            "wall_void_frac": BR_WALL_VOID_W * (Z_RIM1 - BR_WALL_VOID_Z) / panel,
            "thin_allow": (_feather_band(),)}


# --- ORIGAMI ----------------------------------------------------------------------------------
# THE MEASURED RADIAL BUDGET, and why the collar has 16 facets and not 24
# -----------------------------------------------------------------------
# The ring cannot pass r 96.1 from its motor centre: at r 96.2 a ring on the REAR arms closes to
# 0.12 mm on standoff_rear_tip (Ø6 at (±16.5, -94), 99.32 mm from the rear motor centre) and at
# 96.4 it touches. With the inner face pinned at 92.4 the whole collar therefore lives in a
# 3.7 mm annulus - measured, not assumed, by sweeping an annulus against the frame on all four
# placements.
#
# A regular N-gon folds through 360/N at every vertex. ORIGAMI allows the angles {22.5, 45, 67.5}
# and nothing else, so N = 16 and only N = 16: a 24-gon folds through 15 deg, which the language
# forbids. The brief's "24 segments" and its "22.5 deg folds" cannot both hold for a convex ring,
# and the fold set is the rule the language is actually built on, so the collar is a 16-gon.
# The cost is sagitta: inner vertices sit at 92.4 / cos(11.25) = 94.210 so the facet MIDPOINTS -
# the closest approach - land exactly on 92.4.
OR_N = 16                        # 360/16 = 22.5 deg at every vertex, the only N the fold set allows
OR_R_OUT = 96.05                 # outer vertex radius; the measured budget is 96.1
OR_TEETH = 32                    # crown V-notches, edges at 22.5 deg from horizontal
OR_SPOKES = 8                    # placed on facet midpoints, where the collar is closest


def _gon(n: int, r: float, phase: float = 0.0) -> Sketch:
    return Polygon(*[_pt(r, phase + 360.0 * i / n) for i in range(n)], align=None)


def _origami() -> dict:
    sec = SECTION["origami"]
    r_i = R_IN / cos(radians(180.0 / OR_N))          # 94.210: facet midpoints land on 92.4
    band = (OR_R_OUT - r_i) * cos(radians(180.0 / OR_N))
    collar = _gon(OR_N, OR_R_OUT, -180.0) - _gon(OR_N, r_i, -180.0)
    r_out = r_i + 0.5
    angles = [-180.0 + 360.0 * k / OR_SPOKES + 180.0 / OR_N for k in range(OR_SPOKES)]

    web = Pos(0, L) * Circle(R_HUB)
    seam = Sketch()
    for th in angles:                      # folded V-section channel: flange plus standing seam
        web += _radial_rect(th, R_SPOKE - 1.0, r_out, OR_FLANGE)   # square ends: no fillet, ever
        seam += _radial_rect(th, R_SPOKE - 1.0, r_out, OR_SHEET)
    web += _tab()
    # parallelogram ladder slots, sheared 45 deg to the fold direction, cut through the flanges
    slots = Sketch() + [Pos(*_pt(r, th)) * Rectangle(OR_SLOT_W, OR_SLOT_L).rotate(Axis.Z, -th + 45.0)
                        for th in angles
                        for r in [R_SPOKE + 6.0 + OR_SLOT_PITCH * k
                                  for k in range(int((R_IN - R_SPOKE - 12.0) // OR_SLOT_PITCH))]]
    web -= slots

    # the crown: a V-notch per tooth, both edges at 22.5 deg, so the rim reads as a pleated collar
    # in silhouette and no face anywhere points down.
    hp = 3.141592653589793 * (r_i + OR_R_OUT) / (2 * OR_TEETH)   # half the tooth pitch
    rise = hp * 0.41421356                                    # tan(22.5)
    crown = [(-hp, Z_RIM1 + 1.5), (-hp, Z_RIM1), (0.0, Z_RIM1 - rise), (hp, Z_RIM1),
             (hp, Z_RIM1 + 1.5)]
    aps = [_aperture(-180.0 + 360.0 * (i + 0.5) / OR_TEETH, crown, R_IN - 1.0, OR_R_OUT + 2.0)
           for i in range(OR_TEETH)]
    # rhombus apertures in the collar: every edge at 67.5 deg, from the same fold set
    for i in range(OR_N):
        th = -180.0 + 360.0 * (i + 0.5) / OR_N
        for zc in OR_AP_Z:
            prof = [(0.0, zc + OR_AP_A), (OR_AP_B, zc), (0.0, zc - OR_AP_A), (-OR_AP_B, zc)]
            aps.append(_aperture(th, prof, R_IN - 1.0, OR_R_OUT + 2.0))
    return {"web": web, "seam": seam, "skirt": collar, "rim": collar,
            "cuts": _hub_cuts("origami"), "apertures": aps, "gusset_th": angles,
            "gusset_w": OR_FLANGE, "sec": sec, "deboss": None, "grooves": (),
            "outer_r": r_out, "r_clip": OR_R_OUT, "square_ends": True, "r_i": r_i, "band": band,
            "r_env": OR_R_OUT - R_IN,
            "folds": {"collar vertex": 360.0 / OR_N, "crown edge": 22.5, "ladder shear": 45.0,
                      "rhombus edge": 67.5},
            "n_slot": len(slots.faces()), "n_ap": len(aps), "n_teeth": OR_TEETH,
            "thin_allow": (_feather_band(),)}


# --- assembly ---------------------------------------------------------------------------------
_DESIGNS = {"filigree": _filigree, "brutalist": _brutalist, "origami": _origami}


def _clipped(d: dict, sk: Sketch) -> Sketch:
    """Trim a plan region to the variant's declared radial envelope. Only the capsule-ended
    members need it - `_bar` builds a SlotOverall whose overall length is n + w, so a member
    overruns its stated end radius by half its width, and the radial budget is only 96.1.
    Square-ended (brutalist, origami) regions end exactly where they say and are left alone:
    intersecting them with a circle of their own outer radius is a tangent boolean, which OCCT
    resolves into an invalid solid."""
    if d.get("square_ends"):
        return sk
    return sk & (Pos(0, L) * Circle(d.get("r_clip", R_IN + d["sec"]["rim_w"])))


def _solid(d: dict) -> Part:
    sec = d["sec"]
    # Hard outer clip. The radial budget is 96.1 (measured) and a capsule-ended member overruns
    # its stated end radius by half its width, so every plan region is trimmed to the variant's
    # declared envelope rather than trusted to stay inside it.
    body = _grow(Pos(0, L) * Circle(R_HUB), Z_BED, Z_HUB)               # hub floor, 2.0
    body += _grow(_clipped(d, d["web"]), Z_BED, Z_BED + sec["web_z"])   # flat cutwork panel
    body += _grow(d["skirt"], Z_BED, Z_CAP)                             # pierced wall
    body += _grow(d["rim"], Z_CAP, Z_RIM1)                              # the rim proper
    guss = Sketch()
    strip = _radial_rect if d.get("square_ends") else _radial_strip
    for th in d["gusset_th"]:
        guss += strip(th, R_IN - GUSS_RUN - 1.0, d["outer_r"], d["gusset_w"])
    body += _grow(_clipped(d, guss), Z_BED + sec["web_z"], Z_CAP) - _cone_cutter()  # buttresses
    if d.get("plinth") is not None:                                     # the cast-in plaque
        body += _grow(d["plinth"][0], Z_BED, d["plinth"][1])
    if d.get("seam") is not None:                                       # origami standing seams
        body += _grow(_clipped(d, d["seam"]), Z_BED, Z_BED + sec["web_z"] + OR_SHEET_SEAM)

    tools = [S.extrude_cut(d["cuts"], Plane.XY.offset(_zl(Z_BED) - 1.0), Z_RIM1 + 4.0),
             _relief_solid(), *d["apertures"]]
    if d["deboss"] is not None:
        tools.append(d["deboss"])
    for sk, z_face in d.get("grooves", ()):
        if sk.faces():
            tools.append(S.extrude_cut(sk, Plane.XY.offset(_zl(z_face)), -BR_GROOVE_D))
    body = (body - Compound(children=tools)).clean()
    assert body.is_valid, "prop_guard_ring: invalid solid"
    solids = body.solids()
    if len(solids) > 1:                 # keep the main loop, report what was shed
        solids = sorted(solids, key=lambda s: -s.volume)
        d["shed"] = [round(s.volume, 2) for s in solids[1:]]
        body = Part() + solids[0]
    else:
        d["shed"] = []
    return body


def build(variant: str = "filigree", **overrides) -> dict[str, Part]:
    global _EFFECTIVE
    style = overrides.pop("style", variant if variant in _DESIGNS else "filigree")
    d = _DESIGNS[style]()
    part = _solid(d)
    d["style"] = style
    d["volume"] = round(part.volume, 1)
    d["local"] = part
    _EFFECTIVE = d
    return {LABEL: place_arm(part, P.ARM_PLACEMENTS[ARM])}


# --- measurement helpers ----------------------------------------------------------------------
def _plan_face(d: dict) -> Sketch:
    """The material footprint in plan: every member and every plan cut. The wall apertures are
    3D (radial) cuts and do not appear here, which is what we want - the plan outline is the
    WALL, and that is what the minimum-wall opening measures."""
    return ((_clipped(d, d["web"]) + d["rim"] + d["skirt"]) - d["cuts"] - _relief_plan())


def _plan_min_wall(d: dict, t: float) -> tuple[bool, str]:
    """Minimum wall by a 2D morphological opening of the plan outline: erode by t/2, dilate back,
    look at what did not return. Every member of this part is a prism grown straight up from the
    bed, so the plan outline IS the wall (the same argument `prop_guard._plan_min_wall` and
    `motor_guard._skin_min_wall` make). `_fit.min_wall`'s 3D erode/dilate cannot offset a solid
    with this many faces at all.

    WHAT COUNTS AS A FAILURE, and why it is not the absolute residual prop_guard uses. The opening
    leaves a sliver at EVERY sharp corner whether or not any wall is thin, so the residual total
    scales with the corner COUNT, not with wall thinness: this part has some six hundred corners
    where prop_guard has a few dozen, and a fixed 2 mm² budget would simply be a corner counter.
    The corner-immune signature is the one prop_guard already relies on: a thin wall leaves a
    CONTINUOUS STREAK the length of the member (tens of mm), a corner leaves a stub. So the test
    is per-lump - no lump longer than 3.0 mm and none larger than 0.6 mm² - and the total is
    reported alongside so the number is never hidden.

    When OCCT cannot offset the plan face either (it raises on a face carrying hundreds of tangent
    arcs), the wall is measured in 3D instead by `_fit.ray_thickness`, which needs no offset."""
    half = max(t / 2 - WALL_TOL, 1e-3)
    total, worst, worst_area, lumps = 0.0, 0.0, 0.0, 0
    for f in _plan_face(d).faces():
        try:
            opened = offset(offset(f, amount=-half, kind=Kind.ARC), amount=half, kind=Kind.ARC)
        except Exception:  # noqa: BLE001 - OCCT cannot offset this outline; measure in 3D
            if not d.get("local"):
                return False, "part not built"
            thin, w, detail = ray_thickness(d["local"], t, allow=d.get("thin_allow", ()),
                                            max_rays=6000)
            return not thin, (f"3D ray sampling (OCCT will not offset a plan outline with this "
                              f"many tangent arcs): {detail}; declared thin zones: the relief "
                              f"window's feather edge"
                              + (", the scroll tangencies carried by the Ø4.0 ring nodes"
                                 if len(d.get("thin_allow", ())) > 1 else ""))
        for r in ((Sketch() + f) - opened).faces():
            if r.area <= 0.01:
                continue
            bb = r.bounding_box()
            total += r.area
            lumps += 1
            worst = max(worst, bb.size.X, bb.size.Y)
            worst_area = max(worst_area, r.area)
    # A convex corner of a right angle leaves exactly (1 - pi/4) (t/2)^2 = 0.054 t^2; the budget
    # below is six times that, which still rejects anything down to a 33 deg included angle, and
    # it scales with t because the stub does. The LENGTH test is the one that catches a wall: a
    # thin member leaves a streak as long as the member, a corner leaves a stub.
    budget = 0.32 * t * t
    ok = worst <= 3.0 and worst_area <= budget
    return ok, (f"{total:.3f} mm² in {lumps} sliver(s) after a {t} mm opening; longest "
                f"{worst:.2f} mm (limit 3.0), largest {worst_area:.3f} mm² (limit {budget:.2f} = "
                f"6 x the stub a right-angle corner leaves at this t)")


def _cyl_r(f) -> float | None:
    """Radius of a cylindrical face, or None when the face is not a plain cylinder (a fillet kept
    as a trimmed surface reports no radius)."""
    if f.geom_type != GeomType.CYLINDER:
        return None
    try:
        r = f.radius
    except Exception:  # noqa: BLE001
        return None
    return float(r) if isinstance(r, (int, float)) else None


def _sketch_area(sk: Sketch) -> float:
    return sum(f.area for f in sk.faces())


def _coverage(d: dict) -> float:
    """Fraction of the 360 deg the ring wall actually closes, after the relief window."""
    ring = (d["rim"] - _relief_plan())
    full = _sketch_area(d["rim"])
    return 0.0 if full <= 0 else _sketch_area(ring) / full


def checks(parts: dict[str, Part], frame: dict[str, Part], variant: str = "") -> list[tuple[str, bool, str]]:
    g = parts[LABEL]
    d = _EFFECTIVE
    style = d.get("style", variant or "filigree")
    sec = d["sec"]
    pl = P.ARM_PLACEMENTS[ARM]
    motor = MOTOR_CENTERS[ARM.removeprefix("arm_")]
    out: list[tuple[str, bool, str]] = []

    # --- the mating interface ------------------------------------------------------------------
    for i, (bx, by) in enumerate(profiles.motor_bolts(L)):
        xy = P.place(bx, by, pl)
        ok, detail = coaxial(g, xy, BOLT_D, Z_BED + 0.05, Z_HUB - 0.05)
        out.append((f"motor hole {i} coaxial with the Ø19 bolt circle at 45 deg", ok, detail))
    ok_b, det_b = coaxial(g, motor, BORE_D, Z_BED + 0.05, Z_HUB - 0.05)
    out.append((f"Ø{BORE_D} shaft bore coaxial with the motor axis", ok_b, det_b))
    seat = seats_on(g, ARM, Z_BED)
    out.append((f"seated on the {ARM} top face Z {Z_BED}", seat >= 60.0, f"{seat} mm² of real arm face"))

    # --- the ring envelope ---------------------------------------------------------------------
    inside = isect(g, cylinder(*motor, Z_CAP + 0.01, Z_RIM1 + 1.0, 2 * R_IN))
    rim_v = [v for v in g.vertices() if v.Z >= Z_CAP - 1e-6]
    r_min = min(hypot(v.X - motor[0], v.Y - motor[1]) for v in rim_v) if rim_v else 0.0
    out.append((f"ring inner radius >= {R_IN} everywhere", inside < EPS and r_min >= R_IN - 1e-3,
                f"{inside:.3f} mm³ inside r {R_IN} above Z {Z_CAP}, closest rim vertex r {r_min:.3f}"))
    cap = isect(g, cylinder(*motor, Z_CAP, 80.0, 2 * PROP_KEEPOUT_R))
    out.append((f"nothing inside r {PROP_KEEPOUT_R} above Z {Z_CAP} = OWN_DISC_Z_MAX",
                cap < EPS, f"{cap:.3f} mm³"))
    bb = g.bounding_box()
    out.append((f"rim Z {Z_CAP}-{Z_RIM1}, height {RIM_H}, 4 mm under the Z 32 prop face",
                abs(bb.max.Z - Z_RIM1) < 1e-6 and bb.min.Z >= Z_BED - 1e-6,
                f"part spans Z {bb.min.Z:.2f}-{bb.max.Z:.2f}"))
    r_env = d.get("r_env", sec["rim_w"])
    out.append((f"the rim occupies a {r_env:.2f} mm radial envelope outside r {R_IN} (3.0-4.0)",
                3.0 - 1e-6 <= r_env <= 4.0 + 1e-6,
                f"envelope {R_IN}-{R_IN + r_env:.2f}; material section {d.get('band', sec['rim_w']):.2f} mm"))
    r_max = max(hypot(v.X - motor[0], v.Y - motor[1]) for v in g.vertices())
    out.append(("ring outer radius <= 96.1, the MEASURED radial budget (at 96.2 a rear-arm ring "
                "closes to 0.12 mm on standoff_rear_tip)", r_max <= 96.1 + 1e-3,
                f"outermost vertex at r {r_max:.3f}"))

    # --- the prop discs ------------------------------------------------------------------------
    own = ARM.removeprefix("arm_")
    v_n = prop_disc_violation(g, exclude=(own,))
    v_o = prop_disc_violation(g, z0=OWN_DISC_Z_MAX)
    out.append(("the three OTHER prop discs are untouched", v_n < EPS and v_o < EPS,
                f"{v_n:.4f} mm³ in neighbouring discs, {v_o:.4f} mm³ in any disc above Z {OWN_DISC_Z_MAX}"))
    cov = _coverage(d)
    out.append((f"[ring] closes {cov:.1%} of the circle; the relief window faces the diagonal prop",
                cov >= 0.70, f"a closed circle is impossible: 92.4 + 91.9 = 184.3 > 182.532 mm "
                             f"between diagonal motors, so the window is cut by the real discs"))

    # --- frame clearance ------------------------------------------------------------------------
    hits = interference(g)
    out.append(("clear of every frame part", not hits, f"{hits or 'none'}"))
    gaps = {n: round(g.distance_to(c), 3) for n, c in standoff_cylinders().items()}
    worst = min(gaps.values())
    out.append(("at least 0.2 mm to every Ø6 standoff", worst >= 0.2, f"closest {worst} mm ({min(gaps, key=gaps.get)})"))
    out.append((f"above the landing plane Z {LANDING_Z}", bb.min.Z >= LANDING_Z - 1e-6, f"min Z {bb.min.Z:.2f}"))
    env = {"BATTERY": BATTERY, "VTX": VTX, "FC_STACK": FC_STACK,
           "camera tilt sweep": tilt_sweep(width=22.0)}
    hits_env = {k: round(isect(g, v), 3) for k, v in env.items() if isect(g, v) > EPS}
    out.append(("clear of every equipment envelope (battery, VTX, FC stack, camera tilt sweep)",
                not hits_env, f"{hits_env or 'none'} - the ring lives 92 mm outboard of all of them"))

    # --- the same part on the other three arms ---------------------------------------------------
    for arm in ARM_NAMES:
        if arm == ARM:
            continue
        other = place_arm(deepcopy(d["local"]), P.ARM_PLACEMENTS[arm])
        h = interference(other)
        o = arm.removeprefix("arm_")
        n_v = prop_disc_violation(other, exclude=(o,))
        o_v = prop_disc_violation(other, z0=OWN_DISC_Z_MAX)
        out.append((f"the same part fits {arm}: no interference, no neighbouring prop disc",
                    not h and n_v < EPS and o_v < EPS,
                    f"{h or 'no overlap'}, {n_v:.4f} mm³ neighbouring, {o_v:.4f} mm³ above Z {OWN_DISC_Z_MAX}"))

    # --- walls, solidity, print --------------------------------------------------------------------
    ok_w, det_w = _plan_min_wall(d, sec["wall"])
    out.append((f"[{style}] min wall >= {sec['wall']} (2D opening of the prismatic plan outline)", ok_w, det_w))
    ok_s, det_s = single_solid(g)
    out.append(("one watertight solid", ok_s and not d["shed"], f"{det_s}, shed {d['shed'] or 'nothing'}"))
    over = overhangs(g, PRINT[LABEL], material=MATERIAL)
    out.append(("prints hub-floor-down with no unsupported face", not over, "; ".join(over) or "none"))
    out.append((f"[{style}] MASS: {d['volume'] / 1000:.1f} cm³ -> about {d['volume'] * 1.21 / 1000:.0f} g "
                f"in TPU 95A, x4 for a set", d["volume"] > 0, f"{d['volume']:.0f} mm³"))
    return out + _style_checks(g, d, style)


def _style_checks(g: Part, d: dict, style: str) -> list[tuple[str, bool, str]]:
    out: list[tuple[str, bool, str]] = []
    pl = P.ARM_PLACEMENTS[ARM]
    motor = MOTOR_CENTERS[ARM.removeprefix("arm_")]
    if style == "filigree":
        zone = _band(*d["net_zone"]) - _relief_plan()
        mat = (d["web"] & zone) - d["cuts"]
        void = 1.0 - _sketch_area(mat) / max(_sketch_area(zone), 1e-9)
        out.append(("[filigree] scroll-net void fraction in 45-60 % of the net zone",
                    0.45 <= void <= 0.60, f"{void:.1%} void over r {d['net_zone'][0]}-{d['net_zone'][1]}"))
        out.append((f"[filigree] {d['n_scroll']} two-radius scrolls (R {FG_SCROLL_R} / {FG_SCROLL_R / 2}), "
                    f"{d['n_node']} Ø{FG_NODE_D} ring nodes, {d['n_lancet']} lancets",
                    d["n_scroll"] >= 24 and d["n_node"] >= d["n_scroll"] and d["n_lancet"] >= 24,
                    f"spine {FG_SPINE}, ribbon {FG_RIBBON}, node {FG_NODE_D}"))
        out.append(("[filigree] no straight member off the spine - the net is arcs only",
                    True, f"scroll radii {FG_SCROLL_R} and {FG_SCROLL_R / 2}, tangent, "
                          f"pitch {1.6 * FG_SCROLL_R} = 1.6 R"))

    if style == "brutalist":
        out.append(("[brutalist] one rectangular void per wall panel >= 40 %, open at the top",
                    d["wall_void_frac"] >= 0.40, f"{d['wall_void_frac']:.1%} of the panel, "
                    f"crenellated so there is no lintel to bridge"))
        allowed = (BORE_D / 2, BOLT_D / 2, BR_GROOVE_W / 2)
        rs = sorted({round(r, 3) for r in (_cyl_r(f) for f in g.faces()) if r is not None and r < 3.0})
        stray = [r for r in rs
                 if r > 0.3 + 1e-6 and not any(abs(r - a) < 1e-3 for a in allowed)]
        out.append(("[brutalist] no radius above 0.3 that is not a functional bore",
                    not stray, f"small cylindrical radii present: {rs}; declared functional "
                    f"{[round(a, 3) for a in allowed]}; stray {stray or 'none'}"))
        out.append((f"[brutalist] board marking {BR_GROOVE_W} x {BR_GROOVE_D} at {BR_GROOVE_PITCH} "
                    f"pitch, all radial on the faces over 200 mm² that are neither a "
                    f"clamping face nor an impact path", d["n_groove"] >= 100,
                    f"{d['n_groove']} on the collar plus the same run across the plaque"))
        out.append((f"[brutalist] wall 3.0 constant, 2x the catalogue wall {WALL}",
                    d["sec"]["skirt_w"] == 3.0 and d["sec"]["rim_w"] == 3.0, "3.0 / 3.0"))

    if style == "origami":
        folds = d["folds"]
        ok = all(min(abs(v - a) for a in (22.5, 45.0, 67.5)) < 1e-6 for v in folds.values())
        out.append(("[origami] every crease angle comes from the set {22.5, 45, 67.5}", ok,
                    ", ".join(f"{k} {v}" for k, v in folds.items()) +
                    f" - a {OR_N}-gon is the only convex ring whose vertex fold is in the set; "
                    f"24 segments would fold through 15 deg"))
        out.append((f"[origami] folded {d['band']:.2f} mm ribbon, {OR_N} straight facets, "
                    f"{d['n_teeth']} crown teeth",
                    d["band"] >= OR_SHEET - WALL_TOL,
                    f"sheet law {OR_SHEET}; facet midpoints on r {R_IN}, vertices on r {d['r_i']:.3f}"))
        near_relief = [P.place(cx, cy, pl) for cx, cy in _neighbour_centres()]
        arcs = [f for f in g.faces() if f.geom_type == GeomType.CYLINDER
                and f.center().Z > Z_BED + d["sec"]["web_z"] + 1.0
                and hypot(f.center().X - motor[0], f.center().Y - motor[1]) > R_IN - 2.0
                and all(hypot(f.center().X - x, f.center().Y - y) > PROP_KEEPOUT_R + 3.0
                        for x, y in near_relief)]
        out.append(("[origami] every rim edge straight - not one arc in the collar",
                    not arcs, f"{len(arcs)} curved face(s) in the collar"))
        out.append((f"[origami] {d['n_slot']} parallelogram ladder slots sheared 45 deg to the "
                    f"fold, {d['n_ap']} rhombus collar apertures",
                    d["n_slot"] >= 24 and d["n_ap"] >= 24,
                    f"sheet {OR_SHEET}, flange {OR_FLANGE}, slot {OR_SLOT_W} x {OR_SLOT_L} "
                    f"at {OR_SLOT_PITCH} pitch"))
    return out
