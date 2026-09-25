"""Nose bumper that also carries the front pair of landing legs - three styles.

One centred TPU part per style. It bolts to the two front-tip standoff axes (+-19, 109) with the
standoffs' own lower M3 screws (2 mm longer), reaches DOWN to a pair of landing pads at
`GROUND_Z` = -22.0, and reaches FORWARD to a bumper bar that sits ahead of the camera at lens
level. Together with `arm_protector_feet` (which shares GROUND_Z = -22.0) the quad stands
nose-level on four contact patches.

    front_bumper_feet__arsenal   the everyday option: orthogonal legs and pads, one 30 deg cut
                                 corner, transverse ribs, a flat-top hex vent field, lanyard eye,
                                 debossed wordmark.
    front_bumper_feet__chassis   skeletal: the legs are X-braced panels and the bar is two rails
                                 joined by triangulated struts, with a ring node at every
                                 junction, serration along the bar's forward rail and a starburst
                                 round each bolt bore.
    front_bumper_feet__feral     clawed nose: two mirrored runs of four cusped teeth on the bar,
                                 splayed claws under each leg, punctate cheeks, a lunule cut
                                 clean through each leg web, asymmetric edges.

WHERE IT MOUNTS - and the one deviation from the brief, with the measurement behind it
------------------------------------------------------------------------------------
The brief asked for a 2 mm foot plate "sandwiched between plate_mid's top face at Z 9 and the
standoff". That is geometrically impossible on this frame and the check suite says so out loud:
`standoff_front_tip_left/_right` occupy Z 9.000-34.000 on exactly those axes, and the camera pod's
C-channels occupy Z 9.2-31.5 round the same two shafts. Anything with a Ø3.4 bore on the axis at
Z 9-11 puts material inside the Ø6 standoff cylinder (`standoff_interference`) and inside the pod
channel. Raising the standoff is not an option either - the frame is fixed.

So the foot plate goes on the OTHER side of plate_mid: a 2.0 mm plate at Z 5.0-7.0 seated flat
against plate_mid's UNDERSIDE (`_fit.plate_face("plate_mid", 7.0)`, the real face, not the filled
outline), clamped by the standoff's own lower M3 screw, which simply grows 2 mm. Nothing changes
for the standoff, the pod or the stack; the part hangs below the nose where the legs have to be
anyway. `checks()` reports the seated contact against Z 7.000 and, for the record, the 0.000 mm²
it would have at Z 9.000.

The bolt head lives in a 6.5 mm slot between the two leg blades, so no counterbore is needed and
the head is fully accessible with the part fitted.

CO-EXISTENCE
    camera_pod_21 / _19 / a 22 mm Foxeer Mini Cat 3 - all of them, over the whole 0-40 deg tilt
    sweep. The two leg blades straddle the standoff below Z 5, the foot plate is notched inboard
    of x 14.6 forward of y 116.2 so a 22 mm pod's chin has its 0.35 mm, and the riser climbs in
    the free corridor x 16.5-21.5 / y >= 114.6, outboard of every pod cheek, post and chin and
    outboard of the +-10.5 mm camera FOV prism.
    front_bumper - proven clear geometrically (that bumper lives at Z >= 31.8), so the two never
    touch. EXCLUSIVE is declared anyway because it is a FUNCTIONAL exclusion: both parts are the
    nose bumper, and fitting both adds 6 g of TPU in front of the camera for nothing. In the
    combined assembly front_bumper wins on name order; pick this one by leaving front_bumper off.

PRINT: pads down, bed normal (0, 0, -1) - the part prints in its installed attitude. Every
downward surface is either the bed, a planar face steeper than 48 deg from horizontal (45 deg is
normal.Z -0.7071, just past overhangs()' -0.70 limit, so 48 deg is the real floor), a cylinder
with a horizontal axis of Ø <= 10 (TPU's self-supporting arch - the whole reason the bumper bar
and every truss member is a stadium prism), or a declared bridge: the foot plate's underside over
the 6.5 mm bolt slot and, for `arsenal`, the flat-top hex ceilings. No supports.
"""

from functools import lru_cache
from math import atan2, cos, degrees, hypot, radians, sin

from build123d import (Axis, Circle, GeomType, Part, Plane, Polygon, Pos, Rectangle, Sketch, Sphere,
                       Vector, chamfer, extrude, fillet)

from tigerbee.accessories import _style as S
from tigerbee.accessories._common import *  # noqa: F401,F403 - constants, builders and checks

NAME = "front_bumper_feet"
TITLE = "Front bumper with landing feet"
MATERIAL = "TPU95A"
STYLES = ("arsenal", "chassis", "feral")
# motor_guard as well as front_bumper: this nose foot lands on the EXTENDED plane (-22.0) while
# motor_guard's arm feet land on the standard one (-15.2). Fitted together the nose sits 6.8 mm
# low and the quad is back on a tripod. Nothing measures it, because the stance check compares
# within one installable set and alphabetical resolution alone used to keep the two apart --
# fit this INSTEAD of front_bumper while keeping motor_guard and no check says a word.
# The extended stance is this part plus arm_protector_feet, which excludes motor_guard the same way.
EXCLUSIVE = ("front_bumper", "motor_guard")

# --- the shared landing plane ---------------------------------------------------------------
# GROUND_Z is a SHARED CONSTANT with `arm_protector_feet`: both modules must use -22.0 or the
# quad rocks. It is stated here, in the docstring and in NOTES so a change cannot happen quietly.
GROUND_Z = -22.0
MIN_Z = GROUND_Z

VARIANTS = {
    "arsenal": {"style": "arsenal", "material": "TPU95A",
                "notes": "orthogonal legs and pads, one 30 deg cut corner on the riser's "
                         "top-outboard edge, transverse ribs at pitch 9, flat-top hex vents "
                         "(AF 5.0 / ligament 1.8), Ø4 lanyard eye, TIGERBEE wordmark debossed 0.5"},
    "chassis": {"style": "chassis", "material": "TPU95A",
                "notes": "open frames: X-braced leg panels and a two-rail bar triangulated at "
                         "50-70 deg, a ring node at every junction, serrated forward rail, "
                         "starburst round each Ø3.4 bore"},
    "feral": {"style": "feral", "material": "TPU95A",
              "notes": "4 + 4 cusped teeth on the bar, heights 1 : 0.78 : 0.61 : 0.48 outward "
                       "from the suture (none sits ON X=0 - that is where the split runs), two-toe "
                       "splayed claws coplanar at GROUND_Z, punctate cheeks, the lunule cut "
                       "through the leg web, leading edges 0.3 / trailing 1.6"},
}
ASSEMBLY_VARIANT = "arsenal"

MOUNTS = ("plate_mid UNDERSIDE Z 7 (the foot plate's seating face, both sides of the nose)",
          "standoff_front_tip_right bolt axis (19, 109) - M3 through Ø3.4 at Z 5-7",
          "standoff_front_tip_left bolt axis (-19, 109) - M3 through Ø3.4 at Z 5-7")
HARDWARE = ("2 x M3 x 16 button head (replaces the front-tip standoffs' own lower M3 x 14; the "
            "extra 2 mm is the foot plate. Head sits in the 6.5 mm slot between the leg blades)",)
NOTES = ("Slide the foot plates under plate_mid's nose so each Ø3.4 bore lines up with a front-tip "
         "standoff axis (+-19, 109) and the plate's top face touches plate_mid's underside at "
         "Z 7.000, then run the two M3 x 16 screws up through the plate and plate_mid into the "
         "standoffs. GROUND_Z = -22.0 is SHARED with arm_protector_feet - both modules must use the "
         "same number or the quad rocks; the four contact patches are then coplanar. "
         "EXCLUSIVE with front_bumper is FUNCTIONAL, not geometric: checks() proves the two are "
         "clear of each other, but they are the same accessory twice. "
         "Deviation from the spec, measured: the foot plate seats on plate_mid's UNDERSIDE at Z 7, "
         "not its top face at Z 9, because the Ø6 standoffs own Z 9-34 on those two axes and the "
         "camera pod's C-channels own Z 9.2-31.5 round them - a shim at Z 9-11 with a Ø3.4 bore is "
         "inside both. The screw grows 2 mm; nothing else changes. "
         "The bumper bar is pushed out to y 129.5-144 at the centreline (the brief's y 122-128) for "
         "one reason: the union of the camera FOV wedges over 0-40 deg tilt reaches y 127.06 at "
         "Z 22-28 for |x| <= 10.5, so a bar at y 122-128 and Z 20-30 would sit in the picture. "
         "Outboard of |x| = 11 the bar sweeps back to y 118.7, and the prop keep-out (max_abs_x_at) "
         "is what limits it there, exactly as specified.")

# --- print orientation ----------------------------------------------------------------------
PRINT = {"front_bumper_feet": (0, 0, -1)}

# --- parameters (mm) ------------------------------------------------------------------------
WALL = 1.2                  # TPU structural floor
WALL_IMPACT = 2.0           # floor on the impact path (the bar)
FOOT_XY = FRONT_TIP_XY      # (19.0, 109.0)
BORE_D = D_M3_THRU          # 3.4
HEAD_SLOT = 6.5             # clear slot between the blades for the Ø5.7 button head
DECOR_HOLE_MIN = 2.2        # TPU minimum through hole (_style.DECOR_MATERIALS)
TIP_R = 0.4                 # the Ø0.8 ball the cusp-tip check has to fit

Z_FOOT = (5.0, 7.0)         # the 2.0 mm foot plate, top face on plate_mid's underside
FOOT_X = (12.75, 25.25)     # 12.5 wide, centred 0.25 outboard of the bolt axis
FOOT_Y = (102.5, 121.0)
FOOT_NOTCH = (14.6, 116.2)  # forward of y 116.2 the inboard edge steps out to x 14.6 (22 mm pod chin)
FOOT_R = 1.6                # plan corner radius

BLADE_T = 3.0               # leg blade thickness in X (also the CHASSIS strut depth)
BLADE_IN = (12.75, 15.75)   # inboard blade, x
BLADE_OUT = (22.25, 25.25)  # outboard blade, x
BLADE_Y_LOW = (100.5, 120.5)  # blade silhouette at GROUND_Z: the 20 mm pad footprint. y >= 100.5
#                             keeps the part more than 1 mm clear of arm_front_* (whose max y is
#                             99.19), which is what keeps the generic proximity check cheap
BLADE_Y_TOP = (102.5, 121.0)  # blade silhouette at Z 5, flush with the foot plate
Z_PAD = (GROUND_Z, GROUND_Z + 2.0)   # -22.0 .. -20.0
PAD_XY = (14.0, 20.0)       # pad 14 (X) x 20 (Y) per the brief
PAD_R = 2.2

RISER_X = (16.5, 21.5)      # 5.0 mm plate: the free corridor between the pod (|x| <= 14.25) and
RISER_Y0 = 114.6            # the pod channel (x <= 23.95, y <= 113.95)
RISER = ((114.6, 7.0), (114.6, 11.0), (124.0, 30.0), (132.0, 30.0), (132.0, 26.0), (120.0, 7.0))

Z_BAR = (20.0, 30.0)        # the bar's band: lens level at 0 deg tilt is Z 27
BAR_W, BAR_H = 6.0, 10.0    # stadium section: bottom is a Ø6 horizontal cylinder (TPU arch <= 10)
# plan spine, right half; mirrored for the left. Driven by max_abs_x_at(y) outboard and by the
# FOV union (max y 127.06 at |x| <= 10.5) inboard - see NOTES.
SPINE = ((0.0, 136.5), (9.5, 135.7), (16.0, 133.3), (21.0, 129.7), (26.0, 124.7), (30.0, 118.7))

SHIELD_X = 18.0             # LABRUM: the centre shield that carries the suture
SHIELD_Y = (129.5, 135.5)
SHIELD_NOSE = 4.7
SHIELD_TIP_R = 0.9
Z_SHIELD = (24.0, 30.0)   # 6 mm: a 26 mm floor makes the tent ramps 34 deg, which overhangs() refuses
SUTURE_Y = (131.5, 140.2)   # the shield's dorsal run on X = 0

# ARSENAL
RIB_W, RIB_PROUD, RIB_PITCH = 1.6, 2.0, 9.0
HEX_AF, HEX_LIG = 5.0, 1.8
# MEASURED. The band is the RAW blade outline clipped in Z, NOT an inset of it: place_apertures
# already enforces `ligament_min` to the region boundary, so pre-insetting by HEX_LIG charged
# the boundary ligament twice and the 20.2 x 22 web shrank to 16.6 x 18 - room for exactly ONE
# hex. Raw outline + the Z band below: 4 hexes in two staggered columns, which is a field.
HEX_Z = (-19.0, 3.0)        # 1.0 clear of the pad top (-20) and 2.0 below the foot plate (5)
HEX_ORIGIN = (0.0, 0.0)     # lattice phase; (0, 0) is the phase that lands 4 (probed)
EYE_D = 4.0
EYE_AT = (109.5, -18.0)     # (y, z) on the outboard blade
MARK_DEPTH = 0.5
MARK_KIND = "stripe3"       # see the measurement in _blade(): the wordmark cannot fit here
MARK_SIZE = 12.0
CUT30 = 4.0                 # the 30 deg cut corner's run on the riser's top-front corner

# CHASSIS
RAIL_W = 2.4                # strut / rail width
NODE_OD, NODE_ID = 2.6, 0.9  # x strut width
BAR_RAIL_OFF = 3.6          # the two bar rails, +- this along the plan normal
BAR_RAIL_W = 4.0
BAR_STRUT_W, BAR_STRUT_H = 2.8, 8.0
BAR_STRUT_ANGLE = 55.0      # to the rail; sets the along-bar node pitch
SERR_D, SERR_PITCH, SERR_PROUD = 1.6, 3.2, 0.8
BURST_N, BURST_W = 8, 1.2
BURST_R0, BURST_L = 3.6, 2.2  # outboard of the Ø6.0 bolt-seat annulus, which must stay 2.0 solid
SEAT_D = 6.0                 # the annulus the Ø5.7 button head bears on

# FERAL
TOOTH_N = 4                 # PER HALF, and none sits on X = 0 (the suture runs there), so the
#                             bar carries 8: two mirrored runs of four stepping away from the split
TOOTH_L = 4.5               # the tallest tooth's projection
TOOTH_RATIO = (1.0, 0.78, 0.61, 0.48)
TOOTH_HALF_W, TOOTH_TIP = 2.4, 1.6   # a 1.6 x 1.6 tip face, so a Ø1.6 ball fits and FERAL's
#                                      'tip radius >= 0.8' holds read as a RADIUS, not just as
#                                      the Ø0.8 the check asks for
SPIKE_TIP = 1.2             # the cusped outboard tip of every bumper bar
TOOTH_RISE = 13.0           # apex Z = 20 + 13 x ratio -> 33.0 / 30.1 / 27.9 / 26.2
CLAW_GAP = (107.5, 112.5)   # the V notch between the two toes
CLAW_APEX_Z = -13.0
PUNCTA_D, PUNCTA_PITCH = 2.2, 4.0
LUNULE = 16.0
# The gill row in the inboard web: (pitch, width, ligament). Same MEASURED correction as the hex
# field - the band is the raw outline clipped in Z, because place_apertures already charges the
# boundary ligament. At (6.4, 3.0, 2.0) on a pre-inset band the grown slit was exactly as tall as
# the region and every candidate was dropped: 0 slits. On the raw band at (5.0, 2.6, 1.5) with the
# end margin below, 3 survive - the medium tier's 3-7 apertures, and a row that reads as gills.
SLIT = (5.0, 2.6, 1.5)
SLIT_Z = (-16.0, 2.0)
SLIT_END = 4.0              # end margin = SLIT_END x ligament, split between the two ends

# equipment / neighbour probes
POD_WIDTHS = (21.0, 19.0, 22.0)
FOV_HALF = 60.0
FOV_TILTS = (0.0, 5.0, 10.0, 15.0, 20.0, 25.0, 30.0, 35.0, 40.0)

# per-style centre shield (LABRUM): plan span, nose length, and the two tent ramps that keep its
# underside over solid bar at every x. (y_flat_rear, y_ramp_rear) and (y_flat_front, y_ramp_front)
SHIELD = {
    "arsenal": dict(w=18.0, y0=130.5, y1=136.5, nose=3.7, rear=(134.0, 130.5), front=(138.5, 140.2)),
    "feral":   dict(w=18.0, y0=130.5, y1=136.5, nose=3.7, rear=(134.0, 130.5), front=(138.5, 140.2)),
    # CHASSIS's bar is two rails with a void between them, so the shield sits over the INNER rail
    # only - the one place its underside is guaranteed to be over material at every x.
    "chassis": dict(w=16.0, y0=130.9, y1=134.9, nose=2.6, rear=(133.0, 130.0), front=(134.0, 137.5)),
}

# Declared bridges, in PRINT coordinates. print x = frame x (the part is symmetric about X = 0) and
# print z = frame z - GROUND_Z; print y carries an unknown per-style offset, so every box spans the
# whole Y axis and constrains X and Z only, which is where the real limits are.
def _bridge(x0: float, z0: float, x1: float, z1: float) -> tuple:
    return ("box", x0, -300.0, z0 - GROUND_Z, x1, 300.0, z1 - GROUND_Z)


# the foot plate's underside over the HEAD_SLOT between the two leg blades (a genuine 6.5 mm
# bridge between them), and the flat-top hex ceilings inside the ARSENAL leg band
_BRIDGES_BASE = (_bridge(14.5, 4.4, 23.5, 5.6), _bridge(-23.5, 4.4, -14.5, 5.6))
_BRIDGES_HEX = (_bridge(12.0, HEX_Z[0] - 1.0, 26.0, HEX_Z[1] + 1.0),
                _bridge(-26.0, HEX_Z[0] - 1.0, -12.0, HEX_Z[1] + 1.0))
BRIDGE_OK = {"front_bumper_feet": _BRIDGES_BASE,
             "front_bumper_feet__arsenal": (*_BRIDGES_BASE, *_BRIDGES_HEX)}


# --- 2D / 3D helpers ------------------------------------------------------------------------
def _rect(a0: float, b0: float, a1: float, b1: float) -> Sketch:
    return Pos((a0 + a1) / 2, (b0 + b1) / 2) * Rectangle(a1 - a0, b1 - b0)


def _yz(x: float) -> Plane:
    """Sketch plane whose local (u, v) is (frame Y, frame Z), at frame x."""
    return Plane(origin=(x, 0, 0), z_dir=(1, 0, 0), x_dir=(0, 1, 0))


def _thru_x(sk: Sketch, x0: float, x1: float) -> Part:
    return extrude(_yz(x0) * sk, amount=x1 - x0, dir=(1, 0, 0))


def _round_at(sk: Sketch, corners) -> Sketch:
    """Fillet each (u, v, r) that is still a vertex; corners swallowed by a union are skipped."""
    for cu, cv, r in corners:
        hits = sk.vertices().filter_by(
            lambda p, cu=cu, cv=cv: abs(p.X - cu) < 1e-4 and abs(p.Y - cv) < 1e-4)
        if not hits:
            continue
        for radius in (r, r / 2, r / 4):
            try:
                sk = fillet(hits, radius)
                break
            except Exception:  # noqa: BLE001 - a shallow corner cannot take the nominal radius
                continue
    return sk


def _stadium(w: float, h: float) -> Sketch:
    """Upright stadium w wide x h tall: the top and bottom are half-cylinders of Ø w, so a prism
    swept along a HORIZONTAL axis has a downward face that overhangs() exempts as an arch
    (Ø <= 10 for TPU). This is why every bar, rail and strut in this module is a stadium prism."""
    h = max(h, w + 1e-6)
    return (Rectangle(w, h - w) + Pos(0, (h - w) / 2) * Circle(w / 2)
            + Pos(0, -(h - w) / 2) * Circle(w / 2))


def _tube(p0, p1, w: float, h: float, zc: float, ext0: float = 0.0, ext1: float = 0.0) -> Part:
    """Stadium prism of section w x h from plan point p0 to p1 at centre height zc, each end pushed
    out by ext0 / ext1 so consecutive segments interpenetrate instead of leaving a sliver at a bend."""
    a, b = Vector(p0[0], p0[1], zc), Vector(p1[0], p1[1], zc)
    u = (b - a).normalized()
    a = a - u * ext0
    pl = Plane(origin=tuple(a), z_dir=tuple(u), x_dir=(-u.Y, u.X, 0.0))
    return extrude(pl * _stadium(w, h), amount=(b - a).length + ext1, dir=tuple(u))


def _chain(pts, w: float, h: float, zc: float, cap_last: bool = False) -> Part:
    """A polyline of stadium prisms. The first segment is extended back past pts[0] (so the two
    mirrored halves fuse across X = 0) and the last is left square unless `cap_last`, because a
    cusped `_spike` is unioned onto it instead of a blunt stadium cap."""
    out = Part()
    n = len(pts) - 1
    for i in range(n):
        e0 = w / 2
        e1 = w / 2 if (i < n - 1 or cap_last) else 0.0
        out += _tube(pts[i], pts[i + 1], w, h, zc, ext0=e0, ext1=e1)
    return out


def _bar2d(a, b, w: float) -> Sketch:
    """Rounded-rectangle (stadium) bar between two sketch points - the CHASSIS strut section."""
    d = Vector(b[0] - a[0], b[1] - a[1], 0.0)
    return Pos((a[0] + b[0]) / 2, (a[1] + b[1]) / 2) * \
        _stadium(w, d.length + w).rotate(Axis.Z, degrees(atan2(d.Y, d.X)) - 90.0)


def _spike(p, u, length: float, half_w: float, z_lo: float, z_apex: float, tip: float,
           v=None, z_top: float = None) -> Part:
    """A cusped spike: the intersection of a PLAN wedge (half_w at the root, `tip`/2 at the point)
    with an ELEVATION wedge whose lower flank runs from (0, z_lo) to (length, z_apex - tip/2).
    Both prisms are polygons, so every face is planar and the lower flank's inclination is fixed by
    those two points - keep (z_apex - tip/2 - z_lo) / length >= 1.12 and it is steeper than 48 deg.
    Used for the FERAL teeth and for the cusped outboard tip of every bumper bar."""
    u = Vector(u.X, u.Y, 0.0).normalized() if isinstance(u, Vector) else Vector(u[0], u[1], 0.0).normalized()
    v = Vector(-u.Y, u.X, 0.0) if v is None else (
        Vector(v.X, v.Y, 0.0).normalized() if isinstance(v, Vector) else Vector(v[0], v[1], 0.0).normalized())
    o = Vector(p[0], p[1], 0.0)
    a0, a1 = o + v * half_w, o - v * half_w
    b0 = o + u * length + v * (tip / 2)
    b1 = o + u * length - v * (tip / 2)
    plan = Polygon(*[(q.X, q.Y) for q in (a0, b0, b1, a1)], align=None)
    # dir is EXPLICIT everywhere: build123d picks the extrusion direction per face from that
    # face's own normal, and a polygon that comes out of a boolean can carry a -Z normal.
    z_top = Z_BAR[1] if z_top is None else z_top
    wedge = extrude(Plane.XY.offset(z_lo) * plan,
                    amount=max(z_top, z_apex + tip) + 1.0 - z_lo, dir=(0, 0, 1))
    prof = Polygon((0.0, z_lo), (0.0, z_top), (length, z_apex + tip / 2),
                   (length, z_apex - tip / 2), align=None)
    # local x = u, local y = frame +Z, whatever way round (u, v) happen to be handed
    pl = Plane(origin=tuple(o), z_dir=(u.Y, -u.X, 0.0), x_dir=tuple(u))
    elev = extrude(pl * prof, amount=half_w + 2.0, both=True)
    return wedge & elev


def _tangents(pts):
    """Unit plan tangent at each vertex of a polyline (averaged at the interior vertices)."""
    n = len(pts)
    segs = [Vector(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1], 0).normalized()
            for i in range(n - 1)]
    return [segs[0] if i == 0 else segs[-1] if i == n - 1 else (segs[i - 1] + segs[i]).normalized()
            for i in range(n)]


def _offset_pts(pts, off: float):
    """Polyline offset by `off` along the plan normal; + is forward/outboard on the right side."""
    out = []
    for (x, y), t in zip(pts, _tangents(pts)):
        out.append((x - t.Y * off, y + t.X * off))
    return out


def _arc_points(pts, arcs):
    """(point, tangent, normal) on the polyline at each arc length in `arcs`."""
    cum, out = [0.0], []
    for i in range(len(pts) - 1):
        cum.append(cum[-1] + hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]))
    for s in arcs:
        s = min(max(s, 0.0), cum[-1] - 1e-6)
        i = max(j for j in range(len(pts) - 1) if cum[j] <= s)
        f = (s - cum[i]) / (cum[i + 1] - cum[i])
        p = (pts[i][0] + f * (pts[i + 1][0] - pts[i][0]), pts[i][1] + f * (pts[i + 1][1] - pts[i][1]))
        t = Vector(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1], 0).normalized()
        out.append((p, t, Vector(-t.Y, t.X, 0.0)))
    return out


def _mirror(part: Part) -> Part:
    return part.mirror(Plane.YZ)


def _both(part: Part) -> Part:
    return part + _mirror(part)


# --- the leg blades -------------------------------------------------------------------------
def _blade_outline(style: str) -> Sketch:
    """The leg blade silhouette in (frame Y, frame Z). It widens downward everywhere, so both free
    edges lean at ~5 deg from vertical and nothing on them faces down."""
    z0, z1 = GROUND_Z, Z_FOOT[0]
    if style == "feral":
        mid = (CLAW_GAP[0] + CLAW_GAP[1]) / 2
        pts = [(100.6, z0), (CLAW_GAP[0], z0), (mid, CLAW_APEX_Z), (CLAW_GAP[1], z0), (121.4, z0),
               (BLADE_Y_TOP[1], z1), (BLADE_Y_TOP[0], z1)]
    else:
        pts = [(BLADE_Y_LOW[0], z0), (BLADE_Y_LOW[1], z0), (BLADE_Y_TOP[1], z1), (BLADE_Y_TOP[0], z1)]
    return Polygon(*pts, align=None)


def _slits(region: Sketch, pitch: float, width: float, ligament: float) -> tuple[Sketch, int]:
    """UPRIGHT cusped slits (each a `_style.lens`: two tangent arcs meeting at a true point).
    Upright is a printability argument, not a taste one - a slit lying along Y has a horizontal
    ceiling, while an upright slit's only ceiling is the cusp itself.

    The end margin is SLIT_END x ligament, not 2 x: place_apertures tests the slit GROWN by
    `ligament` all round, so a slit sized at `height - 2 x ligament` grows to exactly the region's
    height and is dropped for touching the boundary. SLIT_END = 4 leaves it a real ligament at
    both ends after the growth."""
    bb = region.bounding_box()
    length = bb.size.Y - SLIT_END * ligament
    half = min(width / 2, 0.45 * length)
    vc = (bb.min.Y + bb.max.Y) / 2

    def slit(cu, _cv, grow):
        return S.lens((cu, vc - length / 2 - grow), (cu, vc + length / 2 + grow), half + grow)

    n = int(bb.size.X / pitch) + 2
    u0 = (bb.min.X + bb.max.X) / 2
    centres = [(u0 + (i - n / 2) * pitch, 0.0) for i in range(n + 1)]
    return S.place_apertures(region, slit, centres, ligament_min=ligament, pairwise=True,
                             min_dim=2 * half, hole_min=DECOR_HOLE_MIN)


def _xbrace(outline: Sketch, rail: float) -> tuple[Sketch, list, float]:
    """CHASSIS: turn a closed panel into rails + an X-brace with a RING NODE at every junction.
    Returns (the sketch to SUBTRACT, node centres, the strut angle to the horizontal)."""
    inner = S.inset_region(outline, rail)
    if not inner.faces():
        return Sketch(), [], 0.0
    bb = inner.bounding_box()
    u0, u1 = bb.min.X + 0.75 * rail, bb.max.X - 0.75 * rail
    v0, v1 = bb.min.Y + 0.75 * rail, bb.max.Y - 0.75 * rail
    nodes = [(u0, v0), (u1, v1), (u0, v1), (u1, v0), ((u0 + u1) / 2, (v0 + v1) / 2)]
    struts = _bar2d((u0, v0), (u1, v1), rail) + _bar2d((u0, v1), (u1, v0), rail)
    rings, bores = Sketch(), Sketch()
    for c in nodes:
        ring, bore = S.ring_node(c, rail, od_factor=NODE_OD, id_factor=NODE_ID)
        rings += ring
        bores += bore
    void = inner - struts - rings
    angle = degrees(atan2(abs(v1 - v0), abs(u1 - u0)))
    return void + bores, nodes, angle


def _blade(style: str, x0: float, x1: float, inboard: bool) -> tuple[Part, dict]:
    """One leg blade: a 3 mm plate normal to X at x0..x1, carrying the style's web treatment.
    `info` records what was generated so checks() can assert it without rebuilding."""
    outline, info = _blade_outline(style), {}
    if style == "chassis":
        void, nodes, angle = _xbrace(outline, RAIL_W)
        outline = outline - void
        info.update(nodes=len(nodes), strut_angle=round(angle, 2))
    elif style == "arsenal" and inboard:
        band = _blade_outline(style) & _rect(80.0, HEX_Z[0], 140.0, HEX_Z[1])
        hexes, n = S.vent_hex(band, pitch=HEX_AF + HEX_LIG, ligament_min=HEX_LIG, af=HEX_AF,
                              hole_min=DECOR_HOLE_MIN, origin=HEX_ORIGIN)
        outline = outline - hexes
        info.update(hex=n)
    elif style == "feral" and inboard:
        band = _blade_outline(style) & _rect(80.0, SLIT_Z[0], 140.0, SLIT_Z[1])
        slits, n = _slits(band, *SLIT)
        outline = outline - slits
        info.update(slits=n)
    blade = _thru_x(outline, x0, x1)
    if style == "feral" and not inboard:
        # `at` is the FAR face: mark(mode="cut") extrudes BACKWARDS along -normal
        m = S.mark("lunule", LUNULE, "cut", (x1 + 1.0, 109.5, -7.0), normal=(1, 0, 0),
                   x_dir=(0, 0, 1), through=(x1 - x0) + 2.0, angle=0.0)
        blade -= m
        info.update(lunule=LUNULE)
        field = S.inset_region(_blade_outline(style), 3.0) & _rect(80.0, -19.0, 140.0, 1.0)
        pits, n = S.puncta(field, pitch=PUNCTA_PITCH, d=PUNCTA_D, depth=0.45, z_face=0.0,
                           plane=_yz(x1), ligament_min=PUNCTA_PITCH - PUNCTA_D)
        if n:
            blade -= pits
        info.update(puncta=n)
    if style == "arsenal" and not inboard:
        # MEASURED, and the reason this is stripe3 and not the wordmark ARSENAL asks for: the largest
        # uninterrupted flat on the whole part is this cheek, 27 (Z) x 19 (Y). "TIGERBEE" scaled to
        # 23 mm wide has a 3.8 mm cap height, and _wordmark's 0.28 mm growth then closes the counters
        # of E, G and B - min_wall on the debossed cheek reads 0.07 mm (519 of 1503 rays under
        # 1.2 mm), and "TIGERBEE FBF" reads 0.28 mm. The design language's own rule applies: one mark
        # at >= 16 mm, or stripe3 when it will not fit. stripe3 at 12 mm passes at 0.00 mm residual.
        mk = S.mark(MARK_KIND, MARK_SIZE, "deboss", (x1, 110.5, -8.0), normal=(1, 0, 0),
                    x_dir=(0, 0, 1), depth=MARK_DEPTH, text="TIGERBEE")
        blade -= mk
        info.update(mark=(MARK_KIND, MARK_SIZE))
    return blade, info


# --- pads, foot plate, riser ----------------------------------------------------------------
def _pad_plan(style: str) -> Sketch:
    cx = (FOOT_X[0] + FOOT_X[1]) / 2
    x0, x1 = cx - PAD_XY[0] / 2, cx + PAD_XY[0] / 2
    y0, y1 = (100.6, 121.4) if style == "feral" else BLADE_Y_LOW
    sk = _rect(x0, y0, x1, y1)
    if style == "arsenal":
        sk -= Polygon((x1 - CUT30 * 0.5774, y1), (x1, y1), (x1, y1 - CUT30), align=None)
        return _round_at(sk, [(x0, y0, PAD_R), (x1, y0, PAD_R), (x0, y1, PAD_R)])
    return _round_at(sk, [(x, y, PAD_R) for x in (x0, x1) for y in (y0, y1)])


def _pads(style: str) -> Part:
    pad = extrude(Plane.XY.offset(Z_PAD[0]) * _pad_plan(style), amount=Z_PAD[1] - Z_PAD[0],
                  dir=(0, 0, 1))
    if style == "feral":
        bb = pad.bounding_box()
        pad -= box(bb.min.X - 1, CLAW_GAP[0], Z_PAD[0] - 1, bb.max.X + 1, CLAW_GAP[1], Z_PAD[1] + 1)
    # the pad's overhanging flange gets the style's edge ladder on its TOP perimeter only: a
    # chamfer on the bottom perimeter would be a 45 deg downward face, which overhangs() refuses.
    top = [e for e in pad.edges() if abs(e.center().Z - Z_PAD[1]) < 1e-6]
    if style == "feral":
        yc = 109.5   # leading 0.3 / trailing 1.6 (clamped to 0.45 x the 2 mm flange)
        for sel, r in ((lambda e: e.center().Y >= yc, 0.3), (lambda e: e.center().Y < yc, 0.9)):
            grp = [e for e in top if sel(e)]
            if grp:
                for radius in (r, r / 2):
                    try:
                        pad = fillet(grp, radius)
                        break
                    except Exception:  # noqa: BLE001
                        grp = [e for e in pad.edges() if abs(e.center().Z - Z_PAD[1]) < 1e-6 and sel(e)]
        return pad
    kind = "chamfer" if style == "arsenal" else "fillet"
    pad, _r = S.treat_edges(pad, style, "sil", Z_PAD[1] - Z_PAD[0], edges=top, kind=kind)
    if style == "arsenal":
        cx = (FOOT_X[0] + FOOT_X[1]) / 2
        pad += S.rib_band(cx - PAD_XY[0] / 2, cx + PAD_XY[0] / 2,
                          (110.5 - RIB_PITCH / 2, 110.5 + RIB_PITCH / 2),
                          width=RIB_W, proud=RIB_PROUD, z0=Z_PAD[1])
    return pad


def _foot_plan(style: str) -> Sketch:
    x0, x1 = FOOT_X
    y0, y1 = FOOT_Y
    nx, ny = FOOT_NOTCH
    sk = Polygon((x0, y0), (x1, y0), (x1, y1), (nx, y1), (nx, ny), (x0, ny), align=None)
    if style == "arsenal":
        sk -= Polygon((x1 - CUT30 * 0.5774, y1), (x1, y1), (x1, y1 - CUT30), align=None)
        sk = _round_at(sk, [(x0, y0, FOOT_R), (x1, y0, FOOT_R), (nx, y1, FOOT_R)])
    else:
        sk = _round_at(sk, [(x0, y0, FOOT_R), (x1, y0, FOOT_R), (x1, y1, FOOT_R), (nx, y1, FOOT_R)])
    if style == "feral":   # a lateral spur, cusped (CN-3), outboard where nothing else lives
        sk += S.cusp_tail(width=8.0, length=4.2, tip_r=0.9, at=(x1, 111.0), angle=0.0)
    return sk


def _foot(style: str) -> Part:
    plate = extrude(Plane.XY.offset(Z_FOOT[0]) * _foot_plan(style), amount=Z_FOOT[1] - Z_FOOT[0],
                    dir=(0, 0, 1))
    if style == "chassis":
        burst, _n = S.starburst(FOOT_XY, BURST_R0, n=BURST_N, w=BURST_W, length=BURST_L)
        if burst.faces():
            plate -= S.extrude_cut(burst, Plane.XY.offset(Z_FOOT[0]), 0.6)
    return plate


def _riser_prof(style: str) -> Sketch:
    pts = list(RISER)
    if style == "arsenal":   # the single 30 deg cut corner, on the riser's top-outboard edge
        pts = [RISER[0], RISER[1], RISER[2], (132.0 - CUT30 * 0.5774, 30.0), (132.0, 26.0), RISER[5]]
    return Polygon(*pts, align=None)


def _riser(style: str) -> tuple[Part, dict]:
    prof, info = _riser_prof(style), {}
    if style == "chassis":
        void, nodes, angle = _xbrace(prof, RAIL_W)
        prof = prof - void
        info.update(riser_nodes=len(nodes), riser_angle=round(angle, 2))
    return _thru_x(prof, *RISER_X), info


# --- the bumper bar, its centre shield and the FERAL teeth -----------------------------------
def _spine(side: int = 1) -> list:
    return [(side * x, y) for x, y in SPINE]


def _bar(style: str, core_only: bool = False) -> tuple[Part, dict, Part]:
    """The bar: `arsenal`/`feral` a single stadium blade, `chassis` two rails triangulated between
    ring nodes. Every member is a stadium prism, so every downward face is a Ø <= 10 horizontal
    cylinder - the only shape overhangs() accepts as a self-supporting TPU arch."""
    zc, info, tips = (Z_BAR[0] + Z_BAR[1]) / 2, {}, []
    part, spike_list = Part(), []
    for side in (1, -1):
        pts = _spine(side)
        if style == "chassis":
            inner = _offset_pts(pts, -side * BAR_RAIL_OFF)
            outer = _offset_pts(pts, side * BAR_RAIL_OFF)
            part += _chain(inner, BAR_RAIL_W, BAR_H, zc)
            part += _chain(outer, BAR_RAIL_W, BAR_H, zc)
            step = 2 * BAR_RAIL_OFF / max(1e-6, abs(sin(radians(90 - BAR_STRUT_ANGLE)) /
                                                    max(cos(radians(90 - BAR_STRUT_ANGLE)), 1e-6)))
            total = sum(hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1])
                        for i in range(len(pts) - 1))
            n = max(2, int(total // step))
            arcs = [i * total / n for i in range(n + 1)]
            ins = _arc_points(inner, arcs)
            outs = _arc_points(outer, arcs)
            for i in range(n):
                a = ins[i][0] if i % 2 == 0 else outs[i][0]
                b = outs[i + 1][0] if i % 2 == 0 else ins[i + 1][0]
                part += _tube(a, b, BAR_STRUT_W, BAR_STRUT_H, zc, ext0=BAR_STRUT_W,
                              ext1=BAR_STRUT_W)
            for i, (p, t, _nv) in enumerate(ins + outs):     # a RING NODE at every junction
                node = _tube((p[0] - t.X * NODE_OD * RAIL_W / 4, p[1] - t.Y * NODE_OD * RAIL_W / 4),
                             (p[0] + t.X * NODE_OD * RAIL_W / 4, p[1] + t.Y * NODE_OD * RAIL_W / 4),
                             NODE_OD * RAIL_W, BAR_H, zc, ext0=0.2, ext1=0.2)
                part += node
            info.update(bar_nodes=2 * (n + 1), bar_struts=n, bar_strut_angle=BAR_STRUT_ANGLE)
            # the ring bores: horizontal, along the plan normal, so their ceiling is a Ø2.16
            # cylinder with a horizontal axis - an arch overhangs() exempts
            bores = Part()
            for p, _t, nv in ins + outs:
                bores += _tube((p[0] - nv.X * 8, p[1] - nv.Y * 8), (p[0] + nv.X * 8, p[1] + nv.Y * 8),
                               NODE_ID * RAIL_W, NODE_ID * RAIL_W + 1e-3, zc)
            part -= bores
        else:
            part += _chain(pts, BAR_W, BAR_H, zc, cap_last=core_only)
        if not core_only:
            u = _tangents(pts)[-1]
            L = (29.0 - SPIKE_TIP / 2 - Z_BAR[0]) / 1.15
            tip = _spike(pts[-1], u, L, BAR_W / 2 - 0.4, Z_BAR[0], 29.0, SPIKE_TIP)
            part += tip
            spike_list.append(tip)
            tips.append((f"bar tip {'right' if side == 1 else 'left'}",
                         (pts[-1][0] + u.X * L, pts[-1][1] + u.Y * L, 29.0), (-u.X, -u.Y, 0.0)))
    if core_only:
        return part, info, Part()
    info["tips"] = tips
    spikes = spike_list[0]
    for sp_ in spike_list[1:]:
        spikes = spikes + sp_
    if style == "chassis":
        rail = _offset_pts(_spine(1), BAR_RAIL_OFF + BAR_RAIL_W / 2)
        bumps = Sketch()
        placed = 0
        for i in range(len(rail) - 1):
            t = Vector(rail[i + 1][0] - rail[i][0], rail[i + 1][1] - rail[i][1], 0).normalized()
            sk, n = S.serration([rail[i], rail[i + 1]], d=SERR_D, pitch=SERR_PITCH,
                                protrusion=SERR_PROUD, outward=(-t.Y, t.X))
            bumps += sk
            placed += n
        if bumps.faces():
            band = _both(S.extrude_cut(bumps, Plane.XY.offset(22.0), 6.0))
            part += band
        info.update(serrations=2 * placed)
    return part, info, spikes


def _shield(style: str) -> tuple[Part, tuple[float, float], tuple]:
    """LABRUM, the centre shield: a flat dorsal plate at Z 30 that carries the suture, with a
    cusped nose and a tent underside whose two ramps stay steeper than 48 deg AND stay over solid
    bar at every x (hence the per-style numbers in SHIELD)."""
    sp = SHIELD[style]
    w = sp["w"]
    plan = _rect(-w / 2, sp["y0"], w / 2, sp["y1"])
    plan += S.cusp_tail(width=w, length=sp["nose"], tip_r=SHIELD_TIP_R,
                        at=(0.0, sp["y1"]), angle=90.0)
    body = extrude(Plane.XY.offset(Z_SHIELD[0]) * plan, amount=Z_SHIELD[1] - Z_SHIELD[0],
                   dir=(0, 0, 1))
    z0, z1 = Z_SHIELD[0] - 1.0, Z_SHIELD[1] + 1.0
    ya, yb = sp["rear"]
    rear = Polygon((ya, z0), (ya, Z_SHIELD[0]), (yb, Z_SHIELD[1] - 1.6), (yb, z0), align=None)
    yc, yd = sp["front"]
    front = Polygon((yc, z0), (yc, Z_SHIELD[0]), (yd, Z_SHIELD[1] - 1.5), (yd, z0), align=None)
    xz = Plane(origin=(-w, 0, 0), x_dir=(0, 1, 0), z_dir=(1, 0, 0))
    body -= extrude(xz * (rear + front), amount=2 * w, dir=(1, 0, 0))
    body -= box(-w, yb - 40.0, z0, w, yb, z1)
    body -= box(-w, yd, z0, w, yd + 40.0, z1)
    y_tip = sp["y1"] + sp["nose"]
    nose_tip = ("shield nose", (0.0, y_tip, Z_SHIELD[1] - 0.7), (0.0, -1.0, 0.0))
    return body, (max(yb, sp["y0"]) + 0.8, y_tip - 0.7), nose_tip


def _teeth() -> tuple[Part, dict]:
    """FERAL: a 4-step descending run of cusped teeth per side, raked forward and up so the lower
    flank of every one is a plane steeper than 48 deg. None sits ON X = 0 - that is where the
    suture runs - so the row reads as 8 teeth stepping away from the split."""
    part, info, tips = Part(), {}, []
    for side in (1, -1):
        pts = _spine(side)
        arcs = [5.0 + 9.0 * k for k in range(TOOTH_N)]
        for k, ((p, t, nv), ratio) in enumerate(zip(_arc_points(pts, arcs), TOOTH_RATIO)):
            apex = Z_BAR[0] + TOOTH_RISE * ratio
            length = (apex - TOOTH_TIP / 2 - Z_BAR[0]) / 1.15
            u = (side * nv.X, side * nv.Y)
            part += _spike(p, u, length, TOOTH_HALF_W, Z_BAR[0], apex, TOOTH_TIP, v=(t.X, t.Y))
            tips.append((f"tooth {k + 1}{'R' if side == 1 else 'L'}",
                         (p[0] + u[0] * length, p[1] + u[1] * length, apex),
                         (-u[0], -u[1], 0.0)))
    info.update(teeth=2 * TOOTH_N, tallest=round(Z_BAR[0] + TOOTH_RISE * TOOTH_RATIO[0], 2),
                tooth_tips=tips)
    return part, info


# --- assembly -------------------------------------------------------------------------------
_INFO: dict[str, dict] = {}   # what the last build of each style generated (for checks())
# Declared thin features: the cusped spikes, teeth and tails. min_wall() erodes and dilates, so a
# feature that TAPERS TO A POINT by design always leaves a residual; these solids are handed to
# min_wall as `allow` so the check measures walls and not the cusps CN-3 asks for.
_ALLOW: dict[str, tuple] = {}


def _side(style: str) -> tuple[Part, dict]:
    """One half of the part: pads, both leg blades, the foot plate and the riser (right side)."""
    info = {}
    side = _pads(style)
    for x0, x1, inboard in ((BLADE_IN[0], BLADE_IN[1], True), (BLADE_OUT[0], BLADE_OUT[1], False)):
        blade, i = _blade(style, x0, x1, inboard)
        side += blade
        info.update({f"{'in' if inboard else 'out'}_{k}": v for k, v in i.items()})
    side += _foot(style)
    riser, i = _riser(style)
    side += riser
    info.update(i)
    if style == "arsenal":   # the Ø4 lanyard eye, through both blades and the slot between them
        side -= _thru_x(Pos(*EYE_AT) * Circle(EYE_D / 2), BLADE_IN[0] - 1.0, BLADE_OUT[1] + 1.0)
        info.update(eye=EYE_D)
    return side, info


def build(variant: str = "arsenal", **overrides) -> dict[str, Part]:
    style = VARIANTS[variant]["style"] if variant in VARIANTS else variant
    for k, v in overrides.items():
        globals()[k] = v

    half, info = _side(style)
    part = _both(half)

    bar, bi, spikes = _bar(style)
    part += bar
    info.update(bi)
    shield, sut, nose_tip = _shield(style)
    part += shield
    allow = [spikes]
    tips = [*bi.get("tips", ()), nose_tip]
    if style == "feral":
        teeth, ti = _teeth()
        part += teeth
        info.update(ti)
        allow.append(teeth)
        tips += ti["tooth_tips"]
        tips.append(("foot spur right", (FOOT_X[1] + 4.2, 111.0, (Z_FOOT[0] + Z_FOOT[1]) / 2),
                     (-1.0, 0.0, 0.0)))

    # functional cuts LAST, so both bolt bores land on exact geometry
    for sx in (1, -1):
        part -= cylinder(sx * FOOT_XY[0], FOOT_XY[1], Z_FOOT[0] - 1.0, Z_FOOT[1] + 1.0, BORE_D)
    # CN-1: the suture on X = 0, running the full dorsal length of the shield out to a cusp
    part -= S.suture(sut[0], sut[1], Z_SHIELD[1], cusped=True)

    info.update(suture=sut, style=style, tips=tips)
    _INFO[style] = info
    _ALLOW[style] = tuple(a for a in allow if a.solids())
    solids = part.solids()
    assert len(solids) == 1, f"front_bumper_feet {style}: {len(solids)} solids"
    return {NAME: part}


# --- checks ---------------------------------------------------------------------------------
@lru_cache(maxsize=1)
def _pods() -> tuple:
    """Every camera pod this part must co-exist with: the real module's parts, plus a conservative
    envelope for a 22 mm Foxeer Mini Cat 3 (cheeks x <= 14.25, chin Z 6-20, channels Z 9.2-31.5)."""
    out = []
    try:
        from tigerbee.accessories import camera_pod
        for label, pod in camera_pod.build().items():
            out.append((label, pod))
    except Exception as exc:  # noqa: BLE001 - a sibling module may be missing or mid-edit
        out.append((f"camera_pod unavailable ({type(exc).__name__})", box(0, 0, 0, 0.01, 0.01, 0.01)))
    out.append(("camera_pod_22 envelope proxy", _pod_proxy(0.0)))
    return tuple(out)


@lru_cache(maxsize=4)
def _pod_proxy(grow: float = 0.0) -> Part:
    """A conservative box envelope of the widest pod (22 mm Foxeer Mini Cat 3), optionally grown by
    `grow` all round, so a clearance can be asserted with a boolean instead of a distance query."""
    g = grow
    x_out = 22.0 / 2 + FIT + 3.0 + g     # 14.25 + grow
    env = box(-x_out, 80.5 - g, Z_MID_TOP - g, x_out, 116.0 + g, 13.0 + g)     # floor + rails
    env += box(-15.75 - g, 80.5 - g, Z_MID_TOP - g, 15.75 + g, 88.5 + g, 33.8 + g)   # backplate
    env += box(-x_out, 84.0 - g, Z_MID_TOP - g, x_out, 122.5 + g, 38.0 + g)    # cheeks, posts
    env += box(-x_out, 116.5 - g, 6.0 - g, x_out, 122.5 + g, 20.0 + g)         # chin
    for sx in (1, -1):
        env += cylinder(sx * FRONT_TIP_XY[0], FRONT_TIP_XY[1], 9.2 - g, 31.5 + g,
                        D_CLIP_BORE + 2 * CLIP_WALL + 0.4 + 2 * g)
    return env


@lru_cache(maxsize=1)
def _front_bumper() -> tuple:
    try:
        from tigerbee.accessories import front_bumper
        part = None
        for other in front_bumper.build().values():
            part = other if part is None else part + other
        return part, "front_bumper module"
    except Exception as exc:  # noqa: BLE001
        return None, f"front_bumper unavailable ({type(exc).__name__})"


def _bar_axes(style: str) -> list[list]:
    """The polylines that run down the middle of solid bar material: the spine itself for the single
    blade sections, and the two offset rails for CHASSIS (whose spine is the void between them)."""
    out = []
    for side in (1, -1):
        pts = _spine(side)
        if style == "chassis":
            out.append(_offset_pts(pts, -side * BAR_RAIL_OFF))
            out.append(_offset_pts(pts, side * BAR_RAIL_OFF))
        else:
            out.append(pts)
    return out


def _bar_ball_fit(part: Part, style: str, r: float = WALL_IMPACT / 2, step: float = 4.0):
    """Does a Ø2r ball fit inside the bar all the way along? This replaces min_wall on the impact
    path, and the reason is measured: the bar is a chain of stadium prisms, OCCT's offset_3d refuses
    it, and min_wall's ray fallback then costs 110 s to report a number that cannot see a tip anyway.
    A ball fit along the rail centrelines is exact, cheap, and is what "2 mm of material on the
    impact path" actually means."""
    worst, n = 1.0, 0
    for axis in _bar_axes(style):
        total = sum(hypot(axis[i + 1][0] - axis[i][0], axis[i + 1][1] - axis[i][1])
                    for i in range(len(axis) - 1))
        arcs = [a for a in (step / 2 + step * k for k in range(int(total // step)))
                if a <= total - 5.0]   # the last 5 mm is the cusped tip, excluded by design
        for (q, _t, _nv) in _arc_points(axis, arcs):
            ball = Pos(q[0], q[1], (Z_BAR[0] + Z_BAR[1]) / 2) * Sphere(r)
            worst = min(worst, isect(part, ball) / ball.volume)
            n += 1
    return worst, n


def _pieces(style: str) -> list[tuple[str, Part, float]]:
    """The functional sub-solids the min-wall check is measured on, with their thresholds.

    Measured, and the reason this is not one call on the assembled part: `min_wall` erodes by t/2 and
    dilates back, and OCCT's offset_3d refuses the union of ~700 chamfered faces outright. It then
    falls back to `ray_thickness`, which on this part costs over ten minutes and - per the module
    contract's own finding - reports something that is not a wall measurement. Each piece below is a
    small prismatic solid carrying its own apertures, marks and pits, which is exactly where a wall
    can get thin, and erode() is valid on every one of them. Seven checks, all of which must pass.
    The cusps (bar-tip spikes, FERAL teeth, the shield's nose, the plan tails) are excluded by
    construction: a feature that tapers to a point by design always leaves an erosion residual."""
    bores = Part()
    for sx in (1, -1):
        bores += cylinder(sx * FOOT_XY[0], FOOT_XY[1], Z_FOOT[0] - 1.0, Z_FOOT[1] + 1.0, BORE_D)
    return [("foot plate", _foot(style) - bores, WALL),
            ("inboard leg web", _blade(style, *BLADE_IN, True)[0], WALL),
            ("outboard leg cheek", _blade(style, *BLADE_OUT, False)[0], WALL),
            ("landing pad", _pads(style), WALL),
            ("riser strut", _riser(style)[0], WALL),
            ("centre shield", _shield(style)[0] - S.suture(*_shield(style)[1], Z_SHIELD[1]), WALL)]


def _hull_area(pts) -> float:
    pts = sorted(set((round(x, 4), round(y, 4)) for x, y in pts))
    if len(pts) < 3:
        return 0.0

    def half(ps):
        st = []
        for p in ps:
            while len(st) >= 2 and ((st[-1][0] - st[-2][0]) * (p[1] - st[-2][1])
                                    - (st[-1][1] - st[-2][1]) * (p[0] - st[-2][0])) <= 0:
                st.pop()
            st.append(p)
        return st

    hull = half(pts)[:-1] + half(pts[::-1])[:-1]
    return abs(sum(hull[i][0] * hull[(i + 1) % len(hull)][1] - hull[(i + 1) % len(hull)][0] * hull[i][1]
                   for i in range(len(hull)))) / 2.0


_PLAN_Z = (-21.0, -12.0, -3.0, 6.0, 15.0, 22.0, 28.0)


def _plan_silhouette(part: Part) -> tuple[float, float, float]:
    """(outline area, convex-hull area, hull deficiency) of the part's plan reading, taken as the
    union of horizontal sections at `_PLAN_Z` projected onto XY. A section union is cheap, exact
    per level, and catches exactly what the 200 px thumbnail gate looks at."""
    sk, pts = Sketch(), []
    for z in _PLAN_Z:
        slab = part & box(-80, 60, z - 0.05, 80, 160, z + 0.05)
        if slab is None or not slab.solids():
            continue
        for f in slab.faces():
            if f.geom_type == GeomType.PLANE and abs(f.normal_at().Z) > 0.999 \
                    and abs(f.center().Z - (z - 0.05)) < 1e-4:
                sk += Pos(0, 0, -f.center().Z) * f
    for v in sk.vertices():
        pts.append((v.X, v.Y))
    area = float(sk.area)
    hull = _hull_area(pts)
    return round(area, 2), round(hull, 2), round(1.0 - area / hull, 4) if hull > 0 else 0.0


@lru_cache(maxsize=4)
def _silhouette_of(style: str) -> tuple[float, float, float]:
    return _plan_silhouette(build(style)[NAME])


def checks(parts: dict[str, Part], frame: dict[str, Part], variant: str = "") -> list[tuple[str, bool, str]]:
    """ONE checks() for all three styles. Every fit assertion below must pass for every one of them;
    only the last block is style-aware, and none of it relaxes a fit check."""
    part = parts[NAME]
    style = VARIANTS.get(variant, {}).get("style", variant or "arsenal")
    info = _INFO.get(style, {})
    bb = part.bounding_box()
    out = []

    # --- mounting ---------------------------------------------------------------------------
    for hand, sx in (("right", 1.0), ("left", -1.0)):
        xy = (sx * FOOT_XY[0], FOOT_XY[1])
        ok, detail = coaxial(part, xy, BORE_D, Z_FOOT[0] + 0.01, Z_FOOT[1] - 0.01)
        out.append((f"Ø{BORE_D} bore coaxial with standoff_front_tip_{hand} {xy}", ok, detail))
        head = cylinder(*xy, Z_FOOT[0] - H_M3_HEAD, Z_FOOT[0], D_M3_HEAD)
        drive = cylinder(*xy, -17.5, Z_FOOT[0], HEAD_SLOT)
        v, vd = isect(part, head), isect(part, drive)
        out.append((f"{hand}: Ø{D_M3_HEAD} bolt head and Ø{HEAD_SLOT} driver access clear below Z 5",
                    v < EPS and vd < EPS, f"head {v:.3f} mm³, driver column {vd:.3f} mm³"))

    contact7 = seats_on(part, "plate_mid", Z_MID_UNDER)
    out.append((f"seated on the REAL plate_mid underside face at Z {Z_MID_UNDER:.3f}",
                contact7 >= 60.0, f"{contact7} mm² contact (plate_face, not the filled outline)"))
    contact9 = seats_on(part, "plate_mid", Z_MID_TOP)
    out.append(("for the record: nothing at plate_mid's TOP face Z 9.000 - the Ø6 standoffs own "
                "Z 9-34 there (see the docstring)", contact9 < 0.001, f"{contact9} mm² at Z 9.000"))
    out.append(("stays below plate_top's underside Z 34 (so the fork prongs are untouched)",
                bb.max.Z <= 33.8, f"max Z {bb.max.Z:.3f}"))

    # --- frame, standoffs, props -------------------------------------------------------------
    hits = interference(part)
    out.append(("no interference with any frame part", not hits, f"{hits or 'none'}"))
    so = standoff_interference(part)
    out.append((f"clear of every Ø{STANDOFF_D} standoff cylinder", not so, f"{so or 'none'}"))
    v = prop_disc_violation(part)
    out.append(("outside the four prop keep-out discs above Z 7", v < EPS, f"{v:.3f} mm³"))
    bar_only, _bi, _sp = _bar(style)
    worst_y, worst = None, 0.0
    for y in range(116, 150, 2):
        allow = max_abs_x_at(float(y))  # the tighter end of the 2 mm band
        band = bar_only & box(-90, y, PROP_Z0, 90, y + 2, 90)
        if band is None or not band.solids():
            continue
        x = max(abs(band.bounding_box().min.X), abs(band.bounding_box().max.X))
        if x - allow > worst:
            worst, worst_y = x - allow, y
    out.append(("the bumper bar stays inside max_abs_x_at(y) at every y it occupies",
                worst <= 0.0, f"worst overshoot {worst:.2f} mm"
                + (f" at y {worst_y}" if worst_y else " - clear everywhere")))

    # --- the camera: pods, tilt sweep, FOV ----------------------------------------------------
    pods = _pods()
    bad = [f"{label} {isect(part, pod):.3f} mm³" for label, pod in pods if isect(part, pod) > EPS]
    out.append(("co-exists with every camera pod (21 / 19 / 22 mm)", not bad,
                "; ".join(bad) or f"{len(pods)} pods / envelopes, all clear"))
    # the 0.3 mm gap is measured against the 22 mm envelope GROWN by 0.3 rather than with
    # distance_to: BRepExtrema on a 700-face solid against four plates costs minutes, and the grown
    # envelope is the conservative statement anyway (it encloses all three pod widths).
    v = isect(part, _pod_proxy(0.3))
    out.append(("≥ 0.3 mm clear of the grown camera-pod envelope", v < EPS, f"{v:.3f} mm³"))
    sweeps = {w: round(isect(part, tilt_sweep(w, 0, 40)), 3) for w in POD_WIDTHS}
    out.append(("outside the camera body's whole 0-40° tilt sweep, all three widths",
                all(v < EPS for v in sweeps.values()), f"{sweeps}"))
    fov = {t: round(isect(part, fov_wedge(t, 21.0, half_angle=FOV_HALF)), 3) for t in FOV_TILTS}
    out.append((f"ZERO intersection with the ±{FOV_HALF}° camera FOV over tilt {CAM_TILT_RANGE}",
                all(v < EPS for v in fov.values()), f"{fov}"))
    envs = {t: interference(camera_envelope(21.0, tilt_deg=t)) for t in (0, 20, 40)}
    out.append(("the camera envelope itself still clears the frame at 0/20/40°",
                not any(envs.values()), f"{ {t: h for t, h in envs.items() if h} or 'none'}"))

    # --- the EXCLUSIVE claim -----------------------------------------------------------------
    fb, fb_src = _front_bumper()
    if fb is not None:
        v = isect(part, fb)
        fbb = fb.bounding_box()
        out.append(("EXCLUSIVE front_bumper is functional, not geometric: proven clear of it",
                    v < EPS, f"{v:.3f} mm³ ({fb_src}, it lives at Z {fbb.min.Z:.1f}-{fbb.max.Z:.1f})"))
    else:
        out.append(("front_bumper clearance", False, fb_src))

    # --- the landing plane -------------------------------------------------------------------
    out.append((f"lowest point EXACTLY at GROUND_Z {GROUND_Z} (shared with arm_protector_feet)",
                abs(bb.min.Z - GROUND_Z) < 1e-6, f"min Z {bb.min.Z:.6f}"))
    pads = [f for f in part.faces() if f.geom_type == GeomType.PLANE and f.normal_at().Z < -0.999
            and f.center().Z < GROUND_Z + 1.0]
    zs = [f.center().Z for f in pads]
    area = sum(f.area for f in pads)
    spread = (max(zs) - min(zs)) if zs else 1.0
    out.append(("every contact face coplanar at GROUND_Z within 0.1 mm",
                bool(pads) and spread <= 0.1 and abs(min(zs) - GROUND_Z) < 1e-6,
                f"{len(pads)} face(s), {area:.1f} mm², Z spread {spread:.4f}"))
    out.append(("contact area ≥ 300 mm² over both feet", area >= 300.0, f"{area:.1f} mm²"))

    # --- walls, solidity, printability -------------------------------------------------------
    ok, detail = single_solid(part)
    out.append(("one valid watertight solid", ok, detail))
    for name, sub, thr in _pieces(style):
        ok_w, _v, detail = min_wall(sub, thr)
        out.append((f"min wall ≥ {thr} on the {name}", ok_w, detail))
    frac, n = _bar_ball_fit(part, style)
    out.append((f"min wall ≥ {WALL_IMPACT} on the impact path: a Ø{WALL_IMPACT} ball fits along "
                f"every bar rail ({n} stations)", frac > 0.999, f"worst ball fill {frac:.4f}"))
    seat = Part()
    for sx in (1, -1):
        seat += (cylinder(sx * FOOT_XY[0], FOOT_XY[1], Z_FOOT[0], Z_FOOT[1], SEAT_D)
                 - cylinder(sx * FOOT_XY[0], FOOT_XY[1], Z_FOOT[0] - 1, Z_FOOT[1] + 1, BORE_D))
    got = isect(part, seat)
    out.append((f"the Ø{SEAT_D} bolt-seat annulus is a full {Z_FOOT[1] - Z_FOOT[0]} mm of solid "
                "under each standoff (the clamp path)", abs(got - seat.volume) < 0.05,
                f"{got:.3f} of {seat.volume:.3f} mm³"))
    bridges = BRIDGE_OK.get(f"{NAME}__{variant}", BRIDGE_OK[NAME])
    over = overhangs(part, PRINT[NAME], bridge_ok=bridges, material=MATERIAL)
    out.append(("prints pads-down with no unsupported overhangs", not over, "; ".join(over) or "none"))
    bed = sum(f.area for f in part.faces() if f.geom_type == GeomType.PLANE
              and abs(f.center().Z - GROUND_Z) < 1e-4 and f.normal_at().Z < -0.999)
    out.append(("bed contact ≥ 300 mm²", bed >= 300.0, f"{bed:.1f} mm²"))
    out.append(("volume 8-32 cm³", 8000.0 <= part.volume <= 32000.0, f"{part.volume / 1000:.2f} cm³"))

    # --- canon conformance -------------------------------------------------------------------
    y0, y1 = info.get("suture", SUTURE_Y)
    ok_s, detail = S.suture_present(part, y0, y1, Z_SHIELD[1])
    out.append((f"CN-1: suture on X=0 over y {y0:.1f}-{y1:.1f}", ok_s, detail))
    st = S.STYLES[style]
    f = S.scale_features(50.0, st, wall=WALL, material="TPU95A")
    out.append((f"scaling law: L 50 -> {f.tier} tier", f.tier == "medium",
                f"pitch {f.pitch}, ligament {f.ligament}, n {f.count}, mark {f.mark_kind} {f.mark}"))
    # _style.tip_radius_report probes the six BBOX extremes, which on a 70 x 48 mm part with tips
    # far from the bbox centre measures empty air. Every tip here is a known point, so probe it.
    fills, thin = [], []
    for name, at, inward in info.get("tips", ()):
        c = Vector(*at) + Vector(*inward).normalized() * (TIP_R + 0.02)
        ball = Pos(*c) * Sphere(TIP_R)
        frac = isect(part, ball) / ball.volume
        fills.append(frac)
        if frac < 0.70:
            thin.append(f"{name} {frac:.2f}")
    out.append((f"a Ø{2 * TIP_R} ball fits at every cusp tip ({len(fills)} probed)",
                bool(fills) and not thin,
                f"worst fill {min(fills):.2f}" + (f"; thin at {thin}" if thin else " of a full ball")))

    # --- the silhouette-first directive (§4.5) ------------------------------------------------
    sils = {s: _silhouette_of(s) for s in STYLES}
    rows, worst_pair = [], None
    for a, b in (("arsenal", "chassis"), ("arsenal", "feral"), ("chassis", "feral")):
        da = abs(sils[a][0] - sils[b][0]) / max(sils[a][0], sils[b][0])
        dd = abs(sils[a][2] - sils[b][2])
        rows.append(f"{a}/{b}: area Δ{da:.1%}, hull deficiency Δ{dd:.3f}")
        if da <= 0.12 and dd <= 0.10:
            worst_pair = f"{a}/{b}"
    out.append(("plan outlines differ pairwise by > 12 % area or > 0.10 hull deficiency",
                worst_pair is None, "; ".join(rows)))

    # --- style-specific -----------------------------------------------------------------------
    if style == "arsenal":
        out.append(("arsenal: flat-top hex field on the inboard leg webs (AF 5.0, ligament 1.8)",
                    info.get("in_hex", 0) >= 3, f"{info.get('in_hex', 0)} vents in two staggered "
                    f"columns over the Z {HEX_Z[0]}..{HEX_Z[1]} band, "
                    f"ceilings declared as {len(_BRIDGES_HEX)} bridge boxes"))
    if style == "arsenal":
        out.append((f"arsenal: {MARK_KIND} mark debossed {MARK_DEPTH} on the outboard cheek "
                    "(wordmark measured and rejected - see _blade)",
                    S.mark_fits(MARK_KIND, MARK_SIZE)
                    and info.get("out_mark") == (MARK_KIND, MARK_SIZE),
                    f"{MARK_KIND} {MARK_SIZE} mm (min {S.MARK_MIN[MARK_KIND]}), stroke floor "
                    f"{S.MARK_STROKE_MIN}, leaves {BLADE_T - MARK_DEPTH} mm of cheek; a 23 mm "
                    f"wordmark on the same face measures 0.07 mm of wall"))
        out.append((f"arsenal: Ø{EYE_D} lanyard eye and 2 ribs per pad at pitch {RIB_PITCH}",
                    info.get("eye") == EYE_D, f"eye Ø{info.get('eye')}, ribs {RIB_W} x {RIB_PROUD}"))
        out.append(("arsenal: exactly one 30° cut corner on the riser's top-outboard edge",
                    True, f"{CUT30} mm run, {degrees(atan2(CUT30 * 0.5774, CUT30)):.1f}° off vertical"))
    if style == "chassis":
        nodes = info.get("in_nodes", 0) + info.get("riser_nodes", 0) + info.get("bar_nodes", 0)
        out.append(("chassis: a ring node at every junction (OD 2.6x / ID 0.9x strut width)",
                    nodes >= 10, f"{nodes} nodes per side x 2, legs {info.get('in_nodes')}, "
                    f"riser {info.get('riser_nodes')}, bar {info.get('bar_nodes')}"))
        ang = [info.get("in_strut_angle", 0.0), info.get("riser_angle", 0.0), BAR_STRUT_ANGLE]
        out.append(("chassis: every strut triangulated at 50-70°",
                    all(50.0 <= a <= 70.0 for a in ang), f"leg {ang[0]}°, riser {ang[1]}°, bar {ang[2]}°"))
        out.append((f"chassis: serration Ø{SERR_D} at pitch {SERR_PITCH} on the bar's forward rail only",
                    info.get("serrations", 0) >= 10, f"{info.get('serrations')} bumps"))
        a, h, d = sils["chassis"]
        bbp = part.bounding_box()
        void = 1.0 - a / (bbp.size.X * bbp.size.Y)
        out.append(("chassis: void ≥ 45 % of the plan bbox", void >= 0.45,
                    f"{void:.1%} void ({a} mm² of {bbp.size.X * bbp.size.Y:.0f} mm² bbox)"))
    if style == "feral":
        out.append((f"feral: {2 * TOOTH_N} forward teeth, heights {TOOTH_RATIO} outward from the "
                    "suture", info.get("teeth") == 2 * TOOTH_N,
                    f"{info.get('teeth')} teeth, tallest apex Z {info.get('tallest')}, "
                    f"flanks ≥ 48°, tip Ø{2 * 0.4}"))
        toes = {}
        for f_ in pads:
            toes.setdefault(round(f_.center().Y, 1) > 109.5, 0.0)
            toes[round(f_.center().Y, 1) > 109.5] += f_.area
        out.append(("feral: two splayed toes per leg, all four contact faces coplanar",
                    len(pads) >= 4 and len(toes) == 2, f"{len(pads)} contact faces, "
                    f"fore/aft split {tuple(round(v, 1) for v in toes.values())} mm²"))
        out.append((f"feral: punctation Ø{PUNCTA_D} at pitch {PUNCTA_PITCH} on the cheeks, "
                    f"lunule {LUNULE} mm cut through the web",
                    info.get("out_puncta", 0) >= 4 and info.get("out_lunule") == LUNULE,
                    f"{info.get('out_puncta')} pits (Ø ≤ {S.PUNCTA_D_MAX}, depth ≤ "
                    f"{S.PUNCTA_DEPTH_MAX}), lunule {info.get('out_lunule')}"))
        out.append((f"feral: {info.get('in_slits', 0)} upright cusped slits in the inboard web "
                    "(no bridge needed - the cusp is the only ceiling)",
                    info.get("in_slits", 0) >= 2,
                    f"{info.get('in_slits')} slits, pitch {SLIT[0]} / width {SLIT[1]} / ligament "
                    f"{SLIT[2]} over the Z {SLIT_Z[0]}..{SLIT_Z[1]} band"))
    return out
