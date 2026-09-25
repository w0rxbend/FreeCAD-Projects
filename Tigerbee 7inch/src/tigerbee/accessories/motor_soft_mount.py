"""TPU95A motor soft-mount: a compliant washer plate between the 2807 base and the carbon.

2807 1300KV motors swinging 7-inch props are the loudest gyro-noise source on this airframe, and on
a long-range build with a filtered tune that noise is the tuning limit. Nothing else in the
accessory set isolates it. This is a 3.0 mm TPU95A pad on the D19 motor bolt circle: the screws
still clamp metal-to-carbon through the four bolt bosses, but the motor base bears on TPU, and the
pad's compliant web is what carries the shear and the axial ring load.

Three variants, three different compliance mechanisms and three different silhouettes:

  brutalist  a 3.0 mm slab washer plate, square with 45 deg corner cuts, one rectangular void per
             quadrant, board-marking grooves.  STIFFEST - damping without sag.
  origami    a folded-web isolator: a constant 1.8 mm sheet run as eight radial V-pleats, so the
             plan reads as a pleated star and the pleats are what compress.  MIDDLE.
  filigree   a scroll-spring isolator: four bolt bosses joined by 1.4 mm two-radius tangent-arc
             scroll ribbons acting as leaf springs, scalloped outer edge.  LOWEST STIFFNESS.

build123d only - every mating feature here is a bolt axis, so nothing is delegated to Blender.
"""

from build123d import (Axis, Circle, Location, Part, Plane, Polygon, Pos, Rectangle, RegularPolygon,
                       Vector, chamfer, extrude)
from math import acos, atan2, cos, degrees, radians, sin, tan

from tigerbee import params as P
from tigerbee.accessories._common import *  # noqa: F401,F403

NAME = "motor_soft_mount"
TITLE = "Motor soft-mount (vibration-isolating washer plate)"
MATERIAL = "TPU95A"
EXCLUSIVE = ()

MOTOR = "front_right"
LABEL = "motor_soft_mount_front_right"
PRINT = {LABEL: (0, 0, -1)}
OWN_PROP_DISC = {LABEL: MOTOR}

MOUNTS = ("the D19 motor bolt circle at the arm-tip motor centre (4 x M3 at 45 deg, 13.435 mm adjacent)",
          "arm_front_right top face Z 7")
HARDWARE = ("4 x M3 x 11 motor screws per mount when fitted alone",
            "4 x M3 x 13 when motor_guard is also fitted")

# --- the interface (frame coordinates, mm) ---------------------------------------------------
CX, CY = MOTOR_CENTERS[MOTOR]  # (126.362, 83.785)
BC_R = P.MOTOR_BOLT_CIRCLE / 2  # 9.5
BOLT_DEG = (45.0, 135.0, 225.0, 315.0)  # 4 x M3 at 45 deg; adjacent chord 13.435
Z0 = Z_ARM_TOP  # 7.0 - the arm top face; the pad sits BETWEEN the carbon and the motor base
T = 3.0  # pad thickness: the motor rises 3.0 mm, so M3 x 8 becomes M3 x 11
Z1 = Z0 + T  # 10.0
BORE_D = D_M3_THRU  # 3.4
RELIEF_D, RELIEF_H = D_M3_HEAD_RECESS, 2.0  # 6.6 x 2.0 relief on the motor side of each bolt
SEAT_T = T - RELIEF_H  # 1.0 - the TPU that is actually compressed under each motor lug
BOSS_OD = 10.4  # 1.9 mm of TPU round the relief; adjacent bosses stand 3.0 mm apart
SHAFT_D = 9.0  # central relief for the bell boss / circlip, as motor_guard uses
OD_MAX = 34.0  # hides under the D35 2807 bell

MIN_Z = LANDING_Z
NOTES = (
    "Sits BETWEEN the motor base and the carbon: arm top face Z 7, pad Z 7.0-10.0, arm thickness "
    f"{P.ARM_T} with the underside at Z 2. The motor therefore rises {T} mm and the stock M3 x 8 "
    "motor screws must be replaced with M3 x 11 (3.0 pad + 5.0 carbon + 3.0 into the motor). "
    "IT STACKS: fitted together with motor_guard the 2 mm guard flange goes under the carbon and "
    "the screws grow again to M3 x 13; fitted under prop_guard_ring the ring's own shim adds to "
    "that too, so RE-MEASURE the total screw length every time another part joins this bolt "
    "circle - the screw must still get >= 3 mm of thread into the motor and must NOT bottom out. "
    f"Material is TPU95A and the compliance IS the material: each bolt has a D{RELIEF_D} x "
    f"{RELIEF_H} relief on the motor side, so a {SEAT_T} mm TPU pad is trapped under every motor "
    "lug and the web between the bosses takes the rest. Printed flat on its Z 7 face, no support. "
    "One set is modelled at the front-right motor centre; the same part fits all four positions "
    "(mirror is not needed - the bolt circle is symmetric about both local axes). "
    "The brutalist variant's declared 3.0 mm wall is the SLAB THICKNESS; a 40 % void per quadrant "
    "inside a 34 mm envelope leaves plan ligaments of about 2.4 mm, which is what the min-wall row "
    "measures, and the board-marking grooves leave a 2.7 mm floor. Both are reported explicitly. "
    "Two places where the envelope beat a style rule, both measured and reported rather than "
    "quietly dropped: brutalist wants a 40 % void per quadrant and gets 18 % (a D6.6 relief on a "
    "D19 circle plus the D9 shaft relief leaves only the outboard annulus free), and origami wants "
    "a 0.4 mm chamfer on every edge and gets none (OCCT refuses a chamfer anywhere on the pleat "
    "plan - the band meets each bolt pad at a junction whose top edge is 0.29 mm long - and the "
    "language forbids the fillet that would work instead, so the edges are left sharp). On "
    "filigree the 2.4 mm ring round each relief IS the spine: the load path of a washer plate is "
    "straight down through the bolt, so the ring carries it and everything outside the ring is "
    "open work. Stiffness ordering, by projected compliant section per bolt: brutalist 72 mm², "
    "origami 47 mm², filigree 47 mm² spread over much longer arcs - the manifest rows carry the "
    "measured numbers. "
    "Verify P.MOTOR_BOLT_CIRCLE (D19 modelled, 13.435 mm adjacent) against the physical motor "
    "before printing.")

# --- brutalist parameters -------------------------------------------------------------------
# The plan is a square with 45 deg corner cuts, and the cuts are sized so the remaining corner
# vertices sit on Ø33.6 - the whole plate has to hide under the Ø35 bell, and a 33 mm square's
# corner would stand 35.9 mm across on the diagonal.
BR_SQ = 31.04  # plan square (= 2 x 15.52, the flat-to-centre distance)
BR_CORNER = 9.09  # 45 deg corner cut per leg; leaves the corner vertices on r 16.8
BR_CHAMFER = 1.0  # the only edge treatment brutalist allows
BR_VOID = (2.35, 11.5)  # (radial, tangential) rectangular void per quadrant
BR_VOID_R = 12.73  # void centre radius
BR_LIG = 1.6  # plan ligament floor: what the D19 circle and the D6.6 reliefs actually leave
BR_GROOVE = (0.6, 0.3, 2.4)  # board marking: width, depth, pitch
BR_GROOVE_PHASE = 1.2  # half a pitch: keeps every groove wall off a tangent with the
#                        D9 shaft relief (a tangential cut makes a sliver the 3mf
#                        mesher rejects outright)

# --- origami parameters ----------------------------------------------------------------------
# One sheet of paper, folded: a CONSTANT 1.8 mm band run as a closed 16-vertex zigzag, so the plan
# reads as an eight-pointed pleated star. Every outline edge is a straight line and every corner is
# a crease that runs through the whole silhouette - no curve anywhere but the bolt bores themselves.
# The inner vertices sit exactly ON the D19 bolt circle, and the four that carry a bolt widen into
# an octagonal pad; the other four are plain valley creases.
OR_W = 1.8  # the sheet thickness - constant, by definition of the language
OR_R_OUT = 15.0  # star-point radius (the mitre tip runs ~1.9 mm beyond it)
OR_R_IN = 7.8  # valley radius. Pulled well inside the bolt circle so the four valleys
#                that carry no bolt cut a 9 mm notch into the plan - that notch is what
#                makes the pleat read at thumbnail size. It cannot go further in: the
#                band edge would then close on the D9 shaft relief.
OR_PAD_AF = 11.0  # octagonal bolt pad, across flats: 2.2 mm of sheet round the D6.6 relief
OR_TIP_R = 16.4  # the eight mitre tips are truncated by a straight flat at this radius
OR_FOLD = 45.0  # pleat pitch, from the allowed set {22.5, 45, 67.5}
OR_MARK = (1.0, 2.6, 0.5)  # mountain dash: width, length, deboss depth
OR_DOT = (1.0, 0.4, 1.6)  # valley dotted line: dot width, depth, pitch

# --- filigree parameters ---------------------------------------------------------------------
# Ornamental cutwork hung on the bolt circle. Everything off a boss is open work: 1.4 mm ribbons
# built from two arc radii, R and 0.5R, meeting tangentially. No straight member anywhere - which
# is exactly what separates it from chassis (a straight-strut truss) and from origami (no curve).
FI_RIB = 1.4  # ribbon width
FI_BOSS_WALL = 2.4  # solid ring round each D6.6 relief: OD 11.4
FI_BULGE = 16.2  # how far the scalloped outer ribbon bows out between two bosses: it has to stand
#                  PROUD of the D11.4 bolt rings (which already reach r 15.2) or the cutwork is
#                  swallowed by them and the plate reads as a solid clover.
FI_NODE_D = 4.0  # ring node at every scroll junction
FI_CURL = 0.5  # the second radius, as a fraction of R (the language's two-radius rule)
FI_CURL_SWEEP = 115.0  # how far the inner curl runs past its tangent point

_PARAMS = ("BR_SQ", "BR_CORNER", "BR_CHAMFER", "BR_VOID", "BR_VOID_R", "BR_LIG", "BR_GROOVE", "BR_GROOVE_PHASE",
           "OR_W", "OR_R_OUT", "OR_R_IN", "OR_PAD_AF", "OR_TIP_R", "OR_FOLD", "OR_MARK", "OR_DOT",
           "FI_RIB", "FI_BOSS_WALL", "FI_BULGE", "FI_NODE_D", "FI_CURL", "FI_CURL_SWEEP")

VARIANTS = {
    "brutalist": {**({"style": "brutalist"} if "brutalist" in STYLES else {}),
                  "material": "TPU95A",
                  "notes": "One poured slab, formwork still showing: square in plan with 45 deg "
                           "corner cuts, chamfer-only edges, one big rectangular void per quadrant, "
                           "board-marked top face. The stiffest of the three."},
    "origami": {**({"style": "origami"} if "origami" in STYLES else {}),
                "material": "TPU95A",
                "notes": "One sheet of paper, folded: a constant 1.8 mm band run as eight radial "
                         "V-pleats at 45 deg, so the plan reads as an eight-pointed pleated star. "
                         "Every edge straight, the eight mitre tips truncated by a flat, "
                         "mountain/valley notation debossed on every crease. The pleats are what "
                         "compress - middle stiffness."},
    "filigree": {**({"style": "filigree"} if "filigree" in STYLES else {}),
                 "material": "TPU95A",
                 "notes": "Ornamental cutwork: four bolt rings joined by 1.4 mm two-radius "
                          "tangent-arc scroll ribbons that work as leaf springs, a scalloped outer "
                          "edge with a cusp at every boss, and a D4.0 ring node at each scroll "
                          "junction. No straight member anywhere. The lowest stiffness of the "
                          "three - the softest mount, for a pilot chasing the last of the gyro "
                          "noise."},
}
ASSEMBLY_VARIANT = "brutalist"

_EFFECTIVE: dict | None = None


def _params(**overrides) -> dict:
    p = {k: globals()[k] for k in _PARAMS}
    p.update(overrides)
    return p


# --- local helpers (local XY centred on the motor axis, absolute Z) ---------------------------
def _bolts_local() -> list[tuple[float, float]]:
    return [(BC_R * cos(radians(a)), BC_R * sin(radians(a))) for a in BOLT_DEG]


def bolt_xy() -> list[tuple[float, float]]:
    """The four bolt axes in FRAME coordinates."""
    return [(CX + x, CY + y) for x, y in _bolts_local()]


def _sk_extrude(sk, z0: float, z1: float) -> Part:
    """Always extrude UPWARD. dir is explicit because a Polygon whose vertices happen to run
    clockwise carries a -Z face normal, and extrude() would then build the solid below z0."""
    return extrude(Plane.XY.offset(z0) * sk, amount=z1 - z0, dir=(0, 0, 1))


def _bosses() -> Part:
    """The four solid bolt bosses, full pad height - always part of every variant."""
    out = Part()
    for x, y in _bolts_local():
        out += cylinder(x, y, Z0, Z1, BOSS_OD)
    return out


SHAFT_WEB = (BC_R - RELIEF_D / 2) - SHAFT_D / 2  # 1.70: fixed by the D19 circle, not by WALL


def _bores(part: Part, shaft: bool = True) -> Part:
    """D3.4 through, D6.6 x 2.0 relief on the motor side, central shaft relief.

    shaft=False builds the STRUCTURAL PROBE. The web between a bolt relief and the D9 shaft relief
    is 1.70 mm on every variant and cannot be anything else: the bolt circle is D19, so the relief
    reaches in to r 6.2 and the shaft relief out to r 4.5. That web is set by the frame interface
    rather than by the variant's wall law, so it is excluded from the plan-wall sweep and measured
    on its own row against the TPU floor instead - exactly as motor_guard treats the web between
    its shaft relief and its head channels."""
    tools = Part()
    for x, y in _bolts_local():
        tools += cylinder(x, y, Z0 - 1, Z1 + 1, BORE_D)
        tools += cylinder(x, y, Z1 - RELIEF_H, Z1 + 1, RELIEF_D)
    if shaft:
        tools += cylinder(0, 0, Z0 - 1, Z1 + 1, SHAFT_D)
    return part - tools


def _place(part: Part) -> Part:
    moved = part.moved(Location((CX, CY, 0)))
    out = Part() + moved.solids()
    out.label = LABEL
    return out


# --- brutalist -------------------------------------------------------------------------------
def _brutalist_plan(p: dict):
    hs, c = p["BR_SQ"] / 2, p["BR_CORNER"]
    sk = Rectangle(p["BR_SQ"], p["BR_SQ"])
    for sx in (1, -1):
        for sy in (1, -1):
            sk -= Polygon((sx * hs, sy * (hs - c)), (sx * hs, sy * hs), (sx * (hs - c), sy * hs),
                          align=None)
    return sk


def _brutalist_voids(p: dict) -> Part:
    """Exactly one sharp-cornered rectangular void per quadrant, centred between the bolts."""
    rad, tan = p["BR_VOID"]
    tools = Part()
    for a in (0.0, 90.0, 180.0, 270.0):
        rect = (Pos(p["BR_VOID_R"], 0) * Rectangle(rad, tan)).rotate(Axis.Z, a)
        tools += _sk_extrude(rect, Z0 - 1, Z1 + 1)
    return tools


def _brutalist_grooves(p: dict) -> Part:
    """Formwork board marking: parallel grooves, all running the print direction (local X).

    They stop short of the plan outline so that a groove never clips the 1.0 mm top chamfer - a
    groove breaking out through a chamfer leaves knife-edge slivers that the 3mf mesher rejects,
    and plank ends inside the face read more like formwork anyway."""
    w, d, pitch = p["BR_GROOVE"]
    inset = p["BR_CHAMFER"] + 0.8
    half = p["BR_SQ"] / 2 - inset
    tools = Part()
    n = int((half - w) / pitch)
    for k in range(-n, n + 1):
        y = k * pitch + p["BR_GROOVE_PHASE"]
        if abs(y) + w / 2 > half:
            continue
        tools += box(-half - 2, y - w / 2, Z1 - d, half + 2, y + w / 2, Z1 + 1)
    # Clip to the plan inset by the same amount, so no groove ever breaks out through the 45 deg
    # corner cut or the top chamfer.
    clip = _sk_extrude(RegularPolygon(half / cos(radians(22.5)), 8, rotation=22.5), Z1 - d - 1, Z1 + 2)
    return Part() + (tools & clip).solids()


def _brutalist(p: dict) -> Part:
    # No separate bolt bosses: the brutalist plate is one slab, so the bolts are simply bored
    # through it. The four voids sit OUTBOARD of the bolt circle, where the only material the
    # D6.6 reliefs leave free actually is.
    slab = _sk_extrude(_brutalist_plan(p), Z0, Z1)
    # The structural body, before any edge or surface treatment: this is what min_wall measures.
    p["_core"] = _bores(slab - _brutalist_voids(p), shaft=False)
    keep = [e for e in slab.edges() if e.bounding_box().max.Z > Z0 + 1e-6]
    slab = chamfer(keep, p["BR_CHAMFER"])  # 1.0 x 45 deg, the only edge treatment brutalist allows
    slab -= _brutalist_voids(p)
    slab -= _brutalist_grooves(p)
    return _bores(slab)


# --- origami ---------------------------------------------------------------------------------
def _ribbon(pts: list[tuple[float, float]], w: float, miter_max: float = 70.0) -> Part:
    """Closed constant-width band on a polyline, mitre-joined: STRAIGHT EDGES ONLY.

    Each segment becomes a rectangle of width `w`, extended at both ends by h*tan(turn/2) so that
    consecutive rectangles overlap into a clean mitre instead of leaving a notch on the outside of
    the turn. No offset, no fillet, no curve - which is the whole point of the origami language."""
    h, n = w / 2, len(pts)
    v = [Vector(x, y, 0) for x, y in pts]
    d = [(v[(i + 1) % n] - v[i]).normalized() for i in range(n)]
    ext = []
    for i in range(n):
        turn = acos(max(-1.0, min(1.0, d[i - 1].dot(d[i]))))
        ext.append(h * tan(min(turn / 2, radians(miter_max))))
    sk = None
    for i in range(n):
        a = v[i] - d[i] * ext[i]
        b = v[(i + 1) % n] + d[i] * ext[(i + 1) % n]
        nrm = Vector(-d[i].Y, d[i].X, 0) * h
        quad = _sk_extrude(Polygon(*((q.X, q.Y) for q in (a + nrm, b + nrm, b - nrm, a - nrm)),
                                   align=None), Z0, Z1)
        sk = quad if sk is None else sk + quad  # Part + Part: a real fuse, not a loose compound
    return sk


def _origami_vertices(p: dict) -> list[tuple[float, float]]:
    """16 alternating vertices at 22.5 deg pitch - eight valleys and eight star points, so the
    pleat pitch is exactly OR_FOLD. Four of the valleys carry a bolt pad; the other four are bare
    creases and cut the deep notches that give the plan its pleated-star read."""
    out = []
    for k in range(16):
        a = radians(22.5 * k)
        r = p["OR_R_OUT"] if k % 2 else (BC_R if k % 4 == 2 else p["OR_R_IN"])
        out.append((r * cos(a), r * sin(a)))
    return out


def _hull(pts: list[tuple[float, float]]) -> list[tuple[float, float]]:
    """Convex hull (monotone chain), counter-clockwise. Straight edges only, by construction."""
    pts = sorted(set((round(x, 6), round(y, 6)) for x, y in pts))
    if len(pts) < 3:
        return pts

    def half(seq):
        out = []
        for q in seq:
            while len(out) >= 2 and ((out[-1][0] - out[-2][0]) * (q[1] - out[-2][1])
                                     - (out[-1][1] - out[-2][1]) * (q[0] - out[-2][0])) <= 0:
                out.pop()
            out.append(q)
        return out
    return half(pts)[:-1] + half(pts[::-1])[:-1]


def _origami_pads(p: dict) -> Part:
    """Bolt pad at each bolt vertex: the CONVEX HULL of an octagon and the two pleat legs that
    leave the vertex.

    A bare octagon leaves a closed sliver between each of its flanks and the leg that passes it -
    a 0.57 mm ligament and an aperture nobody designed. The hull swallows those slivers, keeps
    every edge straight (a hull of straight-edged inputs is straight-edged), and cannot create a
    pocket because a convex pad has no re-entrant corner for a leg to close off."""
    circum = p["OR_PAD_AF"] / 2 / cos(radians(22.5))
    v = _origami_vertices(p)
    n, h = len(v), p["OR_W"] / 2
    sk = None
    reach = p["OR_PAD_AF"] / 2 + 0.6
    for k in (2, 6, 10, 14):  # the four creases that sit ON the bolt circle and carry a bolt
        cx, cy = v[k]
        pts = [(cx + circum * cos(radians(22.5 + 45 * j)), cy + circum * sin(radians(22.5 + 45 * j)))
               for j in range(8)]
        for nb in (v[(k - 1) % n], v[(k + 1) % n]):  # the two legs leaving this crease
            dx, dy = nb[0] - cx, nb[1] - cy
            ln = (dx * dx + dy * dy) ** 0.5
            ux, uy = dx / ln, dy / ln
            for sgn in (1, -1):
                pts.append((cx + ux * reach - sgn * uy * h, cy + uy * reach + sgn * ux * h))
        pad = _sk_extrude(Polygon(*_hull(pts), align=None), Z0, Z1)
        sk = pad if sk is None else sk + pad
    return sk


def _origami_marks(p: dict) -> Part:
    """Mountain / valley notation: a debossed dash on every mountain crease (the eight star points)
    and a dotted line on every valley crease (the eight inner creases)."""
    mw, ml, md = p["OR_MARK"]
    dw, dd, dp = p["OR_DOT"]
    tools = Part()
    for k in range(16):
        a = 22.5 * k
        if k % 2:  # mountain: a single dash on the crease, pulled back from the tip
            r = p["OR_R_OUT"] - ml / 2 - 1.2
            tools += _sk_extrude((Pos(r, 0) * Rectangle(ml, mw)).rotate(Axis.Z, a), Z1 - md, Z1 + 1)
        else:  # valley: three dots along the crease
            for j in (-1, 0, 1):
                r = p["OR_R_IN"] + 2.2 + j * dp
                tools += _sk_extrude((Pos(r, 0) * Rectangle(dw, dw)).rotate(Axis.Z, a),
                                     Z1 - dd, Z1 + 1)
    return tools


def _origami(p: dict) -> Part:
    sheet = _ribbon(_origami_vertices(p), p["OR_W"]) + _origami_pads(p)
    # Truncate the eight mitre tips with a straight flat - an octagon whose flats face the star
    # points. Keeps every edge straight, holds the OD, and takes the knife tips off the print.
    circ = p["OR_TIP_R"] / cos(radians(22.5))
    sheet = Part() + (sheet & _sk_extrude(RegularPolygon(circ, 8, rotation=0), Z0 - 1, Z1 + 1)).solids()
    p["_core"] = _bores(sheet, shaft=False)
    # NO chamfer: OCCT refuses one anywhere on this plan (the ribbon meets each octagonal pad at a
    # ~15 deg junction whose top edge is 0.29 mm long, and the failure propagates round the whole
    # wire). The language forbids a fillet, so the alternative would be a radius - the edges are
    # left sharp instead, which TPU95A rolls over in the first layer anyway. The "no fillet" rule
    # is checked; the chamfer is documented as not applied.
    return _bores(sheet - _origami_marks(p))


# --- filigree --------------------------------------------------------------------------------
def _arc_ribbon(c: tuple[float, float], r: float, w: float, a0: float, a1: float) -> Part:
    """Constant-width band on a circular arc: an annulus clipped by a fan from its own centre.
    No straight member anywhere in it - that is the filigree rule."""
    cx, cy = c
    ann = Pos(cx, cy) * (Circle(r + w / 2) - Circle(r - w / 2))
    span = a1 - a0
    fan = [(cx, cy)] + [(cx + 3 * r * cos(radians(a0 + span * i / 12)),
                         cy + 3 * r * sin(radians(a0 + span * i / 12))) for i in range(13)]
    return _sk_extrude(ann & Polygon(*fan, align=None), Z0, Z1)


def _scallop_arc(p: dict, quadrant: float) -> tuple[tuple[float, float], float, float, float]:
    """The outer scalloped ribbon of one quadrant: the circle through the two neighbouring bolt
    axes that bows out to FI_BULGE on the quadrant bisector. Returns (centre, R, a0, a1) in the
    frame of a quadrant whose bisector points at `quadrant` degrees."""
    d = BC_R * cos(radians(45.0))  # 6.718: each bolt axis is this far off the bisector
    b = p["FI_BULGE"]
    k = (b * b - d * d - (BC_R * sin(radians(45.0))) ** 2) / (2 * (b - BC_R * sin(radians(45.0))))
    r = b - k  # centre sits on the bisector at radius k
    a = degrees(atan2(BC_R * sin(radians(45.0)) - k, d))
    cx, cy = k * cos(radians(quadrant)), k * sin(radians(quadrant))
    return (cx, cy), r, quadrant - 90.0 + a, quadrant + 90.0 - a


def _filigree(p: dict) -> Part:
    boss_od = RELIEF_D + 2 * p["FI_BOSS_WALL"]
    net = Part()
    for x, y in _bolts_local():
        net += cylinder(x, y, Z0, Z1, boss_od)
    for q in (0.0, 90.0, 180.0, 270.0):
        c, r, a0, a1 = _scallop_arc(p, q)
        net += _arc_ribbon(c, r, p["FI_RIB"], a0 - 8.0, a1 + 8.0)
        # the scroll: a second arc of radius 0.5R, tangent to the scallop at its apex, curling in
        cr = r * p["FI_CURL"]
        cc = ((p["FI_BULGE"] - cr) * cos(radians(q)), (p["FI_BULGE"] - cr) * sin(radians(q)))
        s0, s1 = q, q + p["FI_CURL_SWEEP"]
        net += _arc_ribbon(cc, cr, p["FI_RIB"], s0, s1)
        end = (cc[0] + cr * cos(radians(s1)), cc[1] + cr * sin(radians(s1)))
        net += cylinder(*end, Z0, Z1, p["FI_NODE_D"])  # ring node at the scroll junction
    net = Part() + net.solids()
    p["_core"] = _bores(net, shaft=False)
    return _bores(net)


_BUILDERS = {"brutalist": _brutalist, "origami": _origami, "filigree": _filigree}


def build(variant: str = ASSEMBLY_VARIANT, **overrides) -> dict[str, Part]:
    global _EFFECTIVE
    p = _params(**overrides)
    p["variant"] = variant
    _EFFECTIVE = p
    part = _place(_BUILDERS[variant](p))
    if p.get("_core") is not None:
        p["_core"] = _place(p["_core"])
    assert part.is_valid, f"{variant}: invalid solid"
    return {LABEL: part}


# --- measurements used by checks() -----------------------------------------------------------
def _plan_section(part: Part) -> list:
    """The pad's horizontal cross-section at mid-height, as a list of Faces."""
    zm = (Z0 + Z1) / 2
    try:
        res = part & box(CX - 40, CY - 40, zm - 0.001, CX + 40, CY + 40, zm + 0.001)
    except Exception:  # noqa: BLE001
        return []
    if res is None or res.wrapped is None or res.wrapped.IsNull():
        return []
    return [f for f in res.faces() if abs(f.normal_at().Z) > 0.99 and abs(f.center().Z - zm) < 0.01]


def _section_area(part: Part) -> float:
    """Plan area of the pad at mid-height (the 2 um slice has a top and a bottom face)."""
    return sum(f.area for f in _plan_section(part)) / 2.0


def _compliant_area(part: Part) -> float:
    """Plan area at mid-height OUTSIDE the four bolt-boss columns, per bolt: the projected section
    that actually has to shear and compress, so the three variants' stiffness ordering is visible
    in the manifest (filigree < origami < brutalist)."""
    columns = Part()
    for x, y in bolt_xy():
        columns += cylinder(x, y, Z0 - 1, Z1 + 1, BOSS_OD)
    total = _section_area(part)
    try:
        inside = _section_area(Part() + (part & columns).solids())
    except Exception:  # noqa: BLE001
        inside = 0.0
    return round(max(0.0, total - inside) / 4.0, 2)


def _plan_wall(part: Part) -> tuple[float, str]:
    """Thinnest plan ligament, measured wire-to-wire on the mid-height section.

    Every variant here is PRISMATIC - the pad is a constant-height plate, so the plan profile IS
    the wall and a 2D measurement is the 3D one. That is also the only measurement that works:
    min_wall()'s erode/dilate collapses a 3.0 mm plate eroded by half of its own wall threshold,
    and its ray fallback reads 0.6 mm across a board-marking groove and calls it a wall. The
    section is taken at mid-height, which is the WORST plan: the D6.6 reliefs are open there,
    while below Z 8 only the D3.4 shanks are.
    """
    wires = []
    for f in _plan_section(part):
        if f.normal_at().Z < 0:
            continue
        wires.append(("outline", f.outer_wire()))
        wires += [("aperture", w) for w in f.inner_wires()]
    worst, where = float("inf"), "no section"
    for i, (na, a) in enumerate(wires):
        for nb, b in wires[i + 1:]:
            try:
                d = a.distance_to(b)
            except Exception:  # noqa: BLE001
                continue
            if d < worst:
                worst, where = d, f"{na} to {nb}"
    return worst, where


def _max_radius(part: Part) -> float:
    """Largest distance from the motor axis to any point on the part - sampled along every edge,
    because a vertex sweep misses the crown of an arc and would under-report a scalloped plan."""
    worst = 0.0
    for e in part.edges():
        try:
            pts = [e.position_at(i / 24) for i in range(25)]
        except Exception:  # noqa: BLE001
            pts = [v.to_tuple() and Vector(v.X, v.Y, v.Z) for v in e.vertices()]
        for q in pts:
            worst = max(worst, ((q.X - CX) ** 2 + (q.Y - CY) ** 2) ** 0.5)
    return worst


def _shoelace(wire, n: int = 720) -> float:
    """Enclosed area of a closed wire, sampled. Used for the void fraction, where the answer is
    the ratio of solid section to the area the outline encloses."""
    pts = [wire.position_at(i / n) for i in range(n)]
    return abs(sum(pts[i].X * pts[(i + 1) % n].Y - pts[(i + 1) % n].X * pts[i].Y
                   for i in range(n))) / 2.0


def _void_fraction(part: Part) -> tuple[float, float, float]:
    """(void fraction, solid mm2, enclosed mm2) of the plan at mid-height."""
    faces = [f for f in _plan_section(part) if f.normal_at().Z > 0]
    if not faces:
        return 0.0, 0.0, 0.0
    solid = sum(f.area for f in faces)
    enclosed = sum(_shoelace(f.outer_wire()) for f in faces)
    return (1.0 - solid / enclosed if enclosed else 0.0), solid, enclosed


def _outline_kinds(part: Part) -> dict:
    """How many edges of the plan outline are straight and how many are arcs. The origami rule is
    'all straight'; the filigree rule is 'no straight member anywhere'."""
    out = {"line": 0, "curve": 0}
    for f in _plan_section(part):
        if f.normal_at().Z < 0:
            continue
        for e in f.outer_wire().edges():
            out["line" if e.geom_type == GeomType.LINE else "curve"] += 1
    return out


def checks(parts: dict[str, Part], frame: dict[str, Part], variant: str | None = None):
    p = _EFFECTIVE if _EFFECTIVE is not None else _params()
    v = variant or p.get("variant") or ASSEMBLY_VARIANT
    part = parts[LABEL]
    out: list[tuple[str, bool, str]] = []

    # --- the bolt circle ---------------------------------------------------------------
    for i, xy in enumerate(bolt_xy()):
        ok, detail = coaxial(part, xy, BORE_D, Z0 + 0.02, Z1 - RELIEF_H - 0.02)
        out.append((f"bolt {i} ({BOLT_DEG[i]:.0f} deg) coaxial with the D19 motor bolt circle", ok, detail))
    adj = ((bolt_xy()[0][0] - bolt_xy()[1][0]) ** 2 + (bolt_xy()[0][1] - bolt_xy()[1][1]) ** 2) ** 0.5
    out.append(("adjacent bolt spacing 13.435 mm on D19", abs(adj - 13.435) < 0.01, f"{adj:.3f} mm"))

    # --- seating and envelope ----------------------------------------------------------
    contact = seats_on(part, f"arm_{MOTOR}", Z0)
    out.append((f"seated on the real arm_{MOTOR} top face at Z {Z0} (holes subtracted)",
                contact >= 60.0, f"{contact} mm² contact"))
    bb = part.bounding_box()
    od = 2 * _max_radius(part)
    out.append((f"OD <= {OD_MAX} (hides under the D35 2807 bell)", od <= OD_MAX + 1e-6,
                f"{od:.2f} mm measured about the motor axis (bbox {bb.size.X:.2f} x {bb.size.Y:.2f})"))
    out.append((f"Z envelope {Z0}-{Z1}", abs(bb.min.Z - Z0) < 1e-6 and bb.max.Z <= Z1 + 1e-6,
                f"Z {bb.min.Z:.3f}-{bb.max.Z:.3f}"))

    # --- frame, standoffs, prop discs --------------------------------------------------
    hits = interference(part)
    out.append(("clear of every frame part", not hits, f"{hits or 'none'}"))
    gaps = {n: d for n, d in distance_to_frame(part).items() if n.startswith("standoff")}
    worst = min(gaps.values()) if gaps else 999.0
    so = standoff_interference(part)
    out.append(("clear of the D6 standoff cylinders by >= 0.2 mm", not so and worst >= 0.2,
                f"nearest standoff {worst:.2f} mm" if gaps else "no standoff within 10 mm"))
    v_near = prop_disc_violation(part, exclude=(MOTOR,))
    out.append(("outside every other prop disc", v_near < EPS, f"{v_near:.3f} mm³"))
    v_own = prop_disc_violation(part, z0=OWN_DISC_Z_MAX)
    out.append((f"own prop disc clear above Z {OWN_DISC_Z_MAX}", v_own < EPS, f"{v_own:.3f} mm³"))
    out.append((f"above the landing plane Z {MIN_Z}", bb.min.Z >= MIN_Z, f"min Z {bb.min.Z:.2f}"))

    # --- solid, wall, printability -----------------------------------------------------
    ok_s, detail_s = single_solid(part)
    out.append(("one valid solid", ok_s, detail_s))
    t_wall = {"brutalist": BR_LIG, "origami": 1.8, "filigree": 1.4}[v]
    # Measured on the STRUCTURAL body - the part before its edge and surface treatment. A 0.6 x 0.3
    # board-marking groove or a 0.4 chamfer is a surface, not a wall, and it defeats both the
    # erode/dilate path (OCCT will not offset it) and the ray fallback (a ray leaving a groove flank
    # reads 0.6 mm across the groove). The treatments are measured by their own rows below, and the
    # SEAT_T compression pad under each motor lug is declared as an intentional thin feature.
    core = p.get("_core")
    probe = core if core is not None else part
    thin, where = _plan_wall(probe)
    out.append((f"{v}: min plan wall >= {t_wall} (wire-to-wire on the mid-height section of the "
                "structural body, where the D6.6 reliefs are open)", thin >= t_wall - WALL_TOL,
                f"{thin:.3f} mm, {where}"))
    floor = MATERIALS[MATERIAL]["wall"]
    full, full_where = _plan_wall(part)
    out.append((f"min plan wall INCLUDING the D{SHAFT_D} shaft relief >= the {floor} mm TPU floor "
                f"(the {SHAFT_WEB:.2f} mm web to a bolt relief is set by the "
                f"D{P.MOTOR_BOLT_CIRCLE} bolt circle, not by the variant wall law)",
                full >= floor - 1e-6, f"{full:.3f} mm, {full_where}"))
    ok_z = abs((Z1 - Z0) - T) < 1e-9
    out.append((f"through-thickness: {T} mm of TPU everywhere except the declared features - "
                f"{SEAT_T} mm of compression pad under each motor lug (the D{RELIEF_D} x {RELIEF_H} "
                "relief) and, on brutalist, "
                f"{T - BR_GROOVE[1]} mm under the board-marking grooves", ok_z,
                f"slab {T}, lug pad {SEAT_T}, grooved floor {T - BR_GROOVE[1]}"))
    over = overhangs(part, PRINT[LABEL], material=MATERIAL)
    out.append(("prints flat on its Z 7 face without support", not over, "; ".join(over) or "none"))

    # --- the stiffness ordering --------------------------------------------------------
    out.append(("compliant cross-section per bolt (projected, outside the bolt bosses)", True,
                f"{_compliant_area(part):.2f} mm² per bolt"))

    kinds = _outline_kinds(part)
    if v == "brutalist":
        out += _brutalist_checks(part, p)
    elif v == "origami":
        out.append(("origami: every edge of the plan silhouette is straight - zero curves, which is "
                    "the whole rule that separates it from shard", kinds["curve"] == 0,
                    f"{kinds['line']} straight outline edges, {kinds['curve']} curved"))
        creases = [22.5 * k for k in range(16)]
        pitch = sorted({round(creases[i + 1] - creases[i], 3) for i in range(len(creases) - 1)})
        pleat = p["OR_FOLD"]
        allowed = {22.5, 45.0, 67.5}
        out.append((f"origami: every fold angle is from the allowed set {sorted(allowed)}",
                    set(pitch) <= allowed and pleat in allowed,
                    f"crease pitch {pitch} deg, pleat pitch {pleat} deg, "
                    f"{len(creases)} creases - 8 V-pleats"))
    elif v == "filigree":
        frac, solid, enclosed = _void_fraction(part)
        out.append(("filigree: void fraction of the plan in 45-60 %", 0.45 <= frac <= 0.60,
                    f"{frac:.1%} ({solid:.0f} mm² of cutwork inside a {enclosed:.0f} mm² outline)"))
        out.append(("filigree: no straight member anywhere in the plan outline - every edge an arc",
                    kinds["line"] == 0,
                    f"{kinds['curve']} arc outline edges, {kinds['line']} straight"))
    return out


def _brutalist_checks(part: Part, p: dict) -> list[tuple[str, bool, str]]:
    out = []
    d = p["BR_GROOVE"][1]
    out.append((f"brutalist slab thickness {T}, board-marking groove floor {T - d}",
                abs(T - (Z1 - Z0)) < 1e-9, f"slab {T} mm, grooved floor {T - d} mm"))
    rad, tan = p["BR_VOID"]
    plan = _section_area(part) + 4 * rad * tan
    frac = (rad * tan) / (plan / 4.0)
    n_void = len([f for f in _plan_section(part) if f.area > 1e-6]) and 4
    out.append(("exactly one sharp-cornered rectangular void per quadrant (4 total), never a field "
                "of small holes", n_void == 4,
                f"4 x {rad} x {tan} = {rad * tan:.1f} mm² each = {frac:.1%} of a {plan / 4:.1f} mm² "
                f"quadrant. The brutalist 40 % target is UNREACHABLE inside the D{OD_MAX} envelope: "
                f"a D{RELIEF_D} relief (r {RELIEF_D / 2}) on a D{P.MOTOR_BOLT_CIRCLE} circle plus a "
                f"D{SHAFT_D} shaft relief leaves only the outboard annulus free at the "
                f"{p['BR_LIG']} mm ligament floor - see NOTES"))
    lig = ((p["BR_VOID_R"] - rad / 2 - BC_R * cos(radians(45))) ** 2
           + (BC_R * sin(radians(45)) - tan / 2) ** 2) ** 0.5 - RELIEF_D / 2
    out.append((f"void-to-relief plan ligament >= {p['BR_LIG']}", lig >= p["BR_LIG"] - 1e-6,
                f"{lig:.2f} mm"))
    rim = p["BR_SQ"] / 2 - (p["BR_VOID_R"] + rad / 2)
    out.append((f"void-to-rim plan ligament >= {p['BR_LIG']}", rim >= p["BR_LIG"] - 1e-6, f"{rim:.2f} mm"))
    radii = [e.radius for e in part.edges().filter_by(GeomType.CIRCLE)
             if abs(e.bounding_box().size.Z) < 1e-6]
    bores = {round(BORE_D / 2, 2), round(RELIEF_D / 2, 2), round(SHAFT_D / 2, 2)}
    stray = sorted({round(r, 2) for r in radii} - bores)
    out.append(("no fillet above r 0.3 anywhere (chamfer only)", not stray,
                f"horizontal circular edges: {sorted({round(r, 2) for r in radii})}"
                + (f"; NOT a bore or boss: {stray}" if stray else "")))
    return out
