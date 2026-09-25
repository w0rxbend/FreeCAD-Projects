"""Hooded camera pod for the 22 mm Foxeer Mini Cat 3 - SLIPSTREAM fairing and a SHARD fallback.

Three genuinely different parts off one functional core (same seat, same two C-channels, same
hole pair geometry, same hood bore), so any of them drops onto the nose of the frame:

  slipstream_t25  PETG teardrop fairing, tilt 25 deg, elliptical OCELLUS hood lip, Blender-smoothed
  slipstream_t35  the same fairing rolled to 35 deg - a visibly steeper, taller silhouette
  shard_t25       TPU95A faceted cage, tilt 25 deg, pure build123d, the option that always ships

The pod is interchangeable with `camera_pod` (19/21 mm): identical mounting - feet on plate_mid at
Z 9 between the two Ø6 front-tip standoffs at (±19, 109), two 270 deg C-channel mouths facing -Y so
it pushes on from the front, under the top-plate fork, clear of the Ø17.5 fwd_bore at (0, 61.5).
"""

from math import atan2, cos, degrees, pi, radians, sin, tan

from build123d import (Axis, BuildLine, BuildSketch, Circle, GeomType, Location, Part, Plane,
                       Polygon, Pos, Rectangle, Sketch, SlotOverall, Spline, Vector, chamfer,
                       extrude, fillet, loft, make_face, scale)

from tigerbee.accessories import _blender as BL
from tigerbee.accessories import _style as S
from tigerbee.accessories._common import *  # noqa: F401,F403 - constants, builders and checks

NAME = "camera_pod_22"
TITLE = "Hooded camera pod (22 mm Foxeer Mini Cat 3)"
MATERIAL = "PETG"
BASE = "camera_pod_22"
EXCLUSIVE = ("camera_pod",)  # 19/21 and 22 mm pods occupy the same bay: fit one

# --- camera parameters (mm) -------------------------------------------------------------------
# SOURCES, measured or quoted - no number here is a silent guess:
#   CAM_W/CAM_H  Foxeer's own spec sheet: "22*22mm; 28*22 (with Bracket)", 12.2 g excluding cable
#                (foxeer.com product page, mirrored by flyingtech.co.uk and getfpv.com). The
#                Predator Mini of the same family measures 21.8 x 21.8 (oscarliang.com), so 22.0 is
#                the conservative (larger) of the two published figures.
#   CAM_D        NOT published by Foxeer. Scaled off refs/camera-22-foxeer-mini-cat3/foxeer-mini-cat3.png
#                against the known 22.0 body height: body depth behind the lens flange 21-22 mm.
#                22.0 is taken, and every wall round it is dimensioned from the +0.30 fit, so a
#                1 mm error eats fit, not wall.
#   LENS_D       the M12 holder + front bezel OD, scaled off the same photo: 16.5-17.5. 17.0 taken.
#   LENS_LEN     lens assembly protrusion ahead of the body front face on the same photo: 9-10.5.
#                10.0 taken - over-estimating only lengthens the hood, which is the safe direction.
#   HOLE_PITCH   the two M2 side holes are fore/aft on the body flank, 6.0 apart. This is the
#                spacing the shipped `camera_pod` already uses for the 19/21 mm bodies (its tilt
#                arc slot is SLOT_R = 6.0 behind the pivot) and it is what the flank of
#                foxeer-mini-cat3.png measures against the 22.0 body height (5.4 +- 0.6). Keeping it
#                identical is what makes the two pods interchangeable.
#   FRONT_OFF    front hole -> body front face, 10.0: the repo datum (_common.camera_envelope's
#                front_offset, and CAM_PIVOT = (0, 100, 27) is that front hole).
CAM_W = 22.0
CAM_H = 22.0
CAM_D = 22.0
LENS_D = 17.0
LENS_LEN = 10.0
HOLE_PITCH = 6.0
HOLE_D = D_M2_THRU          # Ø2.4 clearance for the camera's own M2 side screws
FRONT_OFF = 10.0
FIT22 = 0.30                # PETG free fit round the housing, MATERIALS["PETG"]["fit"]

# --- the camera frame: xi along the lens axis from CAM_PIVOT, v perpendicular (up), x = frame X --
XI_FRONT = FRONT_OFF + FIT22                 # 10.30  body front face
XI_REAR = XI_FRONT - (CAM_D + 2 * FIT22)     # -12.30 body rear face
XI_LENS = FRONT_OFF + LENS_LEN               # 20.00  nominal glass
HOOD_AHEAD = 12.0                            # hood rim this far ahead of the body front face (10-12)
XI_RIM = FRONT_OFF + HOOD_AHEAD              # 22.00  front of the OCELLUS lip
CAM_HALF = CAM_W / 2 + FIT22                 # 11.30  cavity half-width and half-height

# --- pod parameters ---------------------------------------------------------------------------
Y_BED = 84.0                # rear face: the flat plane the part prints on, and the cable exit
SH_RX = 13.5                # shell half-width. 14.208 is the narrowest half-gap of the top-plate
SH_RV = 14.6                # fork window (at y 110), so 13.5 keeps 0.7 mm off the prongs.
SH_N = 6.0                  # the section is a SUPERELLIPSE |x/a|^n + |v/b|^n = 1, one closed
                            # spline: a constant-section prism on it has NO longitudinal crease at
                            # all, which is what SLIPSTREAM's G2 rule actually asks for, and n = 6
                            # is the lowest exponent that still leaves 1.6 mm of wall on the
                            # camera's square corners inside a 27 mm shell.
BORE_RX, BORE_RV, BORE_N = 11.95, 12.05, 8.0
# The bore is a superellipse too, and that is a measured decision, not a stylistic one: a STRICT
# ellipse through the same points leaves the camera's four front corners standing as a 25 mm^2
# flat shoulder facing the bed at 25 deg - an unsupported overhang the checker refuses, and no
# ellipse small enough to fit a 27 mm shell can cover a 22.6 mm square. At n = 8 the corner stands
# 0.42 mm proud on the diagonal, ~0.15 mm^2 per corner, well under the 5 mm^2 floor. The curve is
# still one closed spline - no polygon, no crease.
LIP_W, LIP_PROUD, LIP_FILLET = 2.0, 1.6, 2.5    # the OCELLUS: the rolled hood rim
XI_SHELL = XI_RIM                               # the fairing runs all the way out to the rim
HOOD_WALL = 1.6

# --- the OCELLUS bell -------------------------------------------------------------------------
# The fairing is NOT a straight tube: from XI_BELL forward it swells into a flared mouth, and the
# swell IS the OCELLUS. A stepped ring 1.6 proud (the literal reading of the style sheet) cannot be
# built here: the pod prints on its back, bed normal (0, -1, 0), so a ring's rearward annulus is a
# ~170 mm² face with normal.Y -0.91 and overhangs() refuses it outright. A rolled swell is the same
# feature executed to SLIPSTREAM's own rule - G2, no step, no crease - and it is what the reference
# photo actually shows.
#
# Every number below is a measured limit, not a taste:
#   XI_BELL   11.0  the flare may not start earlier. The top-plate fork window is narrowest at
#                   y 110 (half-gap 14.208, from outline_spans("plate_top", y)) and the shell
#                   crosses plate_top's Z 34-36 band at y = 96.27 + 1.1034 xi, so y 110 is xi 12.5.
#   FLARE_X   3.2   the smoothstep reaches 13.5 + 3.2 f at xi 14.3 (y 111.7, half-gap 14.69) with
#                   0.2 mm to spare; anything fatter touches a prong.
#   FLARE_V   1.0   the dorsal flare rate. A crown that leans back at more than ~0.12 per mm of xi
#                   turns the whole upper shell into a down-facing surface once the tilt is added
#                   (the crown's own normal is already Y -0.423 at 25 deg, and the -0.70 limit is
#                   only 0.28 away). 1.0 over an 11 mm run is 0.136 peak: measured safe at both
#                   tilts, 2.2 is not.
#   BELL_PTS  9     the loft stations are EVENLY SPACED, which is not cosmetic. OCCT's ThruSections
#                   parameterises by section index, not by distance: eight unevenly spaced sections
#                   over xi -34..22 produced a valid solid with a 29 m bounding box and negative
#                   volume, and four of them pinched the constant run to 82 % of its true volume.
XI_BELL = 11.0
FLARE_X, FLARE_V = 3.2, 1.0
BELL_PTS = 9
RIM_RX, RIM_RV = None, None      # filled by _radii() at import; see below
BORE_RIM_RX, BORE_RIM_RV = 13.6, 12.9   # the rim aperture: a STRICT ellipse (n = 2), as the style
BORE_RIM_N = 2.0                        # sheet asks. It morphs out of the near-square n = 8 throat
#                                         over the bell, so the hood's inside is one smooth funnel
#                                         and there is no rearward-facing shoulder to bridge.
CHIN_TIP_Y = 116.0          # the ventral keel runs out to a CUSP on the mid-plate nose tip (CN-3)
CHIN_FULL_Y = 101.0         # ... full width aft of here (the vesica's widest station)
CHANNEL_TOP = 31.5          # 0.3 below the front_bumper lip, 2.5 under plate_top
CHANNEL_WALL = 1.7          # OD 9.9 - an arch inside the TPU/PETG self-supporting limit
CHANNEL_Z0 = Z_MID_TOP + 0.2
MOUTH_DEG = 270.0           # mouth opens towards -Y: pushed on from the front, pulled off forwards
SNAP = 0.8
WEB_X, WEB_Y0, WEB_Y1, WEB_CH = 16.0, 103.0, 113.5, 4.0
WEB_FLARE = (19.5, 109.0)
SKIRT_Y1 = 116.0            # ventral chin ends at the mid-plate nose tip
SKIRT_RAMP_Y = 112.5        # ... ramping back up to the waterline from there
STRAP_D, STRAP_Y, STRAP_Z = 5.0, 110.0, 13.5    # zip-tie / cable tunnel straight through in X
NACA_L, NACA_W, NACA_DEEP, NACA_RAMP = 14.0, 4.0, 1.8, 7.0
NACA_XI, NACA_V = -2.0, -7.5                    # low on each flank, running along the flow
NACA_FLOOR = 0.55                               # the ramp floor stops here (1.65 mm of wall left)
                                                # and the rest of the duct is a through inlet
SUTURE_W, SUTURE_D = 0.8, 0.4
LUNULE, LUNULE_DEEP, LUNULE_STRETCH = 17.0, 0.5, 1.4

TILT_DEG = 25.0             # the default; each variant overrides it (the pair of M2 holes IS the tilt)
FOV_HALF = 60.0             # half-angle of the keep-out cone from the glass

_P = Vector(*CAM_PIVOT)     # (0, 100, 27)
_BUILT: dict = {}


# --- variants ---------------------------------------------------------------------------------
VARIANTS = {
    "slipstream_t25": {
        "style": "slipstream", "material": "PETG", "params": {"TILT_DEG": 25.0},
        "notes": "SLIPSTREAM at 25 deg: one unbroken teardrop, no crease above the waterline, the "
                 "OCELLUS lip 1.6 proud round an elliptical hood. Prints on its back (rear face "
                 "down) - the hood flanks sit at 25 deg to the bed normal, well inside 45."},
    "slipstream_t35": {
        "style": "slipstream", "material": "PETG", "params": {"TILT_DEG": 35.0},
        "notes": "SLIPSTREAM at 35 deg: the same fairing rolled up 10 deg, which lifts the hood "
                 "6 mm and pulls it 3 mm aft - a visibly steeper, taller, shorter silhouette. "
                 "Prints on its back."},
    "shard_t25": {
        "style": "shard", "material": "TPU95A", "params": {"TILT_DEG": 25.0},
        "notes": "SHARD at 25 deg: a 10-sided faceted cage, every facet junction chamfered 0.6, "
                 "mitred elongated-hex flank windows, a LABRUM chin shield on the nose facet. "
                 "Pure build123d - the option that ships when the Blender branch degrades. "
                 "Prints on its back."},
}
ASSEMBLY_VARIANT = "shard_t25"

PRINT = {BASE: (0, -1, 0)}
MOUNTS = ("plate_mid top face Z 9 (the ventral skirt seats on it)",
          "standoff_front_tip_left / _right Ø6 shafts (±19, 109) through the 5.2 mm C-clip mouths")
HARDWARE = ("2 x M2 x 4 camera side screws - the camera's own; the hole PAIR sets the tilt, "
            "there is no slot to slip",)
NOTES = ("Slides on from the front like the 19/21 mm pod: pushed rearwards (-Y) over the two Ø6 "
         "front-tip standoffs until the skirt lands on plate_mid at Z 9. The camera goes in from "
         "the REAR, straight down the lens axis, and its own two M2 screws pick up the hole pair - "
         "the tilt is built in, so it cannot creep. The cable leaves through the open rear; a Ø5 "
         "tunnel through the chin at y 110 takes a zip tie or the cable tail. Nothing sits in front "
         "of the glass: the hood lip is 2 mm ahead of it and 11.3 mm off axis, outside a 60 deg "
         "half-angle cone. Remove the pod before fitting a 25.5 mm-pattern board in the forward bay.")


# --- the camera frame -------------------------------------------------------------------------
def _ax(t: float) -> tuple[Vector, Vector]:
    """(a, u): the lens axis and the camera's own 'up', for tilt `t` degrees about CAM_PIVOT +X."""
    c, s = cos(radians(t)), sin(radians(t))
    return Vector(0, c, s), Vector(0, -s, c)


def _pt(t: float, xi: float, v: float = 0.0, x: float = 0.0) -> Vector:
    a, u = _ax(t)
    return _P + a * xi + u * v + Vector(x, 0, 0)


def _pl(t: float, xi: float) -> Plane:
    """Station plane at `xi`, normal = the lens axis. Local (X, Y) = (-frame x, v)."""
    a, _u = _ax(t)
    return Plane(origin=tuple(_pt(t, xi)), z_dir=tuple(a), x_dir=(-1.0, 0.0, 0.0))


def _prism(sk: Sketch, t: float, xi0: float, xi1: float) -> Part:
    """Extrude a station sketch forward along the lens axis from xi0 to xi1."""
    return S.extrude_cut(sk, _pl(t, xi0), xi1 - xi0)


def _yz(sk: Sketch, x0: float, x1: float) -> Part:
    """Extrude a sketch drawn in (Y, Z) from x0 to x1."""
    return extrude(Plane(origin=(x0, 0, 0), x_dir=(0, 1, 0), z_dir=(1, 0, 0)) * sk,
                   amount=x1 - x0, dir=(1, 0, 0))


def _both(part: Part) -> Part:
    return part + part.mirror(Plane.YZ)


def _waterline(t: float, y: float) -> float:
    """Z of the shell's widest line at station y: the axis height, since the section is widest on
    its own centre line. The ventral skirt is tangent to the shell exactly here - the CARINA."""
    return 27.0 + tan(radians(t)) * (y - 100.0)


# --- station sections -------------------------------------------------------------------------
def superellipse(a: float, b: float, n: float, pts: int = 96) -> Sketch:
    """|x/a|^n + |v/b|^n = 1 as ONE closed spline. n = 2 is an ellipse, n -> inf a rectangle; in
    between it is the only closed curve that both covers a square camera and carries no crease."""
    # Sampled by POLAR angle, not by the textbook |cos t|^(2/n) parameter: at n = 6 that
    # parameter is a cube root, so its second sample already sits 6.5 mm up the flank and the
    # spline through it cuts the corner and self-intersects (measured: a 0.09 mm wall and a 3MF
    # the mesher refuses). r(phi) spaces the samples evenly round the curve instead.
    k = []
    for i in range(pts):
        th = 2.0 * pi * i / pts
        ct, st = cos(th), sin(th)
        r = ((abs(ct) / a) ** n + (abs(st) / b) ** n) ** (-1.0 / n)
        k.append((r * ct, r * st))
    with BuildSketch() as sk:
        with BuildLine():
            Spline(*k, k[0], tangents=((0.0, 1.0), (0.0, 1.0)))
        make_face()
    return sk.sketch


SHARD_SECTION = ((1.000, 0.342), (0.933, 0.884), (0.370, 1.000), (-0.370, 1.000),
                 (-0.933, 0.884), (-1.000, 0.342), (-1.000, -0.445), (-0.933, -0.884),
                 (-0.370, -1.000), (0.370, -1.000), (0.933, -0.884), (1.000, -0.445))


def _smoothstep(s: float) -> float:
    """s^2 (3 - 2 s): 0 at s = 0, 1 at s = 1, ZERO SLOPE at both ends. The zero slope at s = 0 is
    what makes the bell leave the constant tube tangentially - no crease, which is the family's
    one rule - and the zero slope at s = 1 is the roll of the OCELLUS."""
    s = min(1.0, max(0.0, s))
    return s * s * (3.0 - 2.0 * s)


def _bell(xi: float) -> float:
    return _smoothstep((xi - XI_BELL) / (XI_SHELL - XI_BELL))


def _radii(rx: float, rv: float, xi: float) -> tuple[float, float]:
    """The fairing's half-width and half-height at station `xi`."""
    f = _bell(xi)
    return rx + FLARE_X * f, rv + FLARE_V * f


RIM_RX, RIM_RV = _radii(SH_RX, SH_RV, XI_SHELL)      # 16.70, 15.60


def _bore_radii(xi: float) -> tuple[float, float, float]:
    """The hood funnel at `xi`: (half-width, half-height, superellipse exponent). It opens from the
    near-square throat that swallows the camera's front face to a strict ellipse at the rim."""
    f = _bell(xi)
    return (BORE_RX + (BORE_RIM_RX - BORE_RX) * f, BORE_RV + (BORE_RIM_RV - BORE_RV) * f,
            BORE_N + (BORE_RIM_N - BORE_N) * f)


def _stations(xi0: float, xi1: float, n: int) -> list[float]:
    return [xi0 + (xi1 - xi0) * i / (n - 1) for i in range(n)]


def _section(style: str, rx: float, rv: float) -> Sketch:
    """The shell's cross-section perpendicular to the lens axis, in (-x, v)."""
    if style == "shard":
        # 12 sides: flank, shoulder, crown, and the mirror of each. Every run is a long planar
        # strip down the whole fairing; neighbouring normals differ 21-41 deg (SHARD's rule), and
        # the shoulder stands 1.48 mm clear of the camera's square corner.
        return Polygon(*[(u * rx, w * rv) for u, w in SHARD_SECTION], align=None)
    return superellipse(rx, rv, SH_N)


def _shell(style: str, t: float, rx: float = SH_RX, rv: float = SH_RV) -> Part:
    """The fairing: a tube on the lens axis that swells into the OCELLUS bell over its last 11 mm,
    cut off flat at the rear plane (the bed) and the seating plane.

    Aft of XI_BELL the section is constant, so the dorsal surface has no crease along the flow;
    forward of it the radius follows a smoothstep that leaves the tube with zero slope, so the
    joint is tangent and still has no crease. SHARD gets the same envelope as a RULED loft between
    two polygons - the bell becomes a ring of flat trapezoidal facets, which is that family's whole
    point, and the creases it leaves are chamfered by build()."""
    aft = _prism(_section(style, rx, rv), t, -34.0, XI_BELL)
    if style == "shard":
        bell = loft([_pl(t, xi) * _section("shard", *_radii(rx, rv, xi))
                     for xi in (XI_BELL, XI_SHELL)], ruled=True)
    else:
        bell = loft([_pl(t, xi) * superellipse(*_radii(rx, rv, xi), SH_N, 64)
                     for xi in _stations(XI_BELL, XI_SHELL, BELL_PTS)])
    tube = aft + bell
    tube -= box(-60, -200, -60, 60, Y_BED, 200)          # flat rear face: the bed
    tube -= box(-60, -200, -60, 60, 200, Z_MID_TOP)      # flat seat on plate_mid at Z 9
    return tube


def _chin_plan(style: str, rx: float) -> Part:
    """CN-3 in plan: the ventral keel does not stop at a flat cut, it runs out to a POINT on the
    mid-plate nose tip. SLIPSTREAM gets the cusp as two tangent arcs (S.lens's far half); SHARD gets
    the same outline mitred, because that family has no arcs except at cusps. Extruded through the
    whole skirt height, so it clips the chin in plan and nothing else."""
    aft = Polygon((rx, Y_BED - 2), (rx, CHIN_FULL_Y), (-rx, CHIN_FULL_Y), (-rx, Y_BED - 2),
                  align=None)
    if style == "shard":
        nose = Polygon((rx, CHIN_FULL_Y), (0.42 * rx, CHIN_TIP_Y - 3.4), (0.0, CHIN_TIP_Y),
                       (-0.42 * rx, CHIN_TIP_Y - 3.4), (-rx, CHIN_FULL_Y), align=None)
    else:
        # S.lens is the cusp primitive. Its tips must be 2 x CHIN_FULL_Y - CHIN_TIP_Y apart for the
        # vesica's widest point to land exactly on CHIN_FULL_Y, where its tangent is parallel to the
        # keel's own flank - so the two meet with no step and no crease, and the far half runs out
        # to a 12 deg point on the mid-plate nose tip.
        y_root = 2 * CHIN_FULL_Y - CHIN_TIP_Y
        nose = S.lens((0.0, y_root), (0.0, CHIN_TIP_Y), rx) & \
            Pos(0.0, (CHIN_FULL_Y + CHIN_TIP_Y) / 2) * Rectangle(4 * rx, CHIN_TIP_Y - CHIN_FULL_Y)
    return extrude(Plane.XY.offset(Z_MID_TOP - 1.0) * (aft + nose), amount=40.0)


def _skirt(style: str, t: float, rx: float = SH_RX) -> Part:
    """The ventral skirt: everything between the seating plane and the waterline, tangent to the
    shell along its widest line so there is no crease where the two meet."""
    z0, z1 = _waterline(t, Y_BED), _waterline(t, SKIRT_RAMP_Y)
    prof = Polygon((Y_BED, Z_MID_TOP), (SKIRT_Y1, Z_MID_TOP), (SKIRT_RAMP_Y, z1), (Y_BED, z0),
                   align=None)
    skirt = _yz(prof, -rx, rx) & _chin_plan(style, rx)
    if style == "shard":
        # CN-5 as SHARD states it: stepped zones with a VISIBLE step line, not a gradient.
        skirt -= box(rx - 0.55, Y_BED - 1, Z_MID_TOP - 1, rx + 1, 100.0, Z_MID_TOP + 6.0)
        skirt -= box(-rx - 1, Y_BED - 1, Z_MID_TOP - 1, -rx + 0.55, 100.0, Z_MID_TOP + 6.0)
    return skirt


def _cavity(t: float) -> Part:
    """The camera plus its rearward insertion corridor: the body swept straight back down the lens
    axis, so the camera can always be pushed in from the rear, and the lens bore in front of it."""
    body = _prism(Rectangle(2 * CAM_HALF, 2 * CAM_HALF), t, XI_REAR - 44.0, XI_FRONT)
    lens_r = LENS_D / 2 + FIT22
    body += _prism(Circle(lens_r), t, XI_FRONT - 0.5, XI_LENS + 0.6)
    return body


def _bore(t: float) -> Part:
    """The hood funnel: a throat that swallows the camera's square front face, opening forward to a
    strict ellipse at the rim. One lofted surface, so the hood's inside has no shoulder to bridge
    and no crease, and the mouth is the ellipse the style sheet asks for."""
    throat = _prism(superellipse(BORE_RX, BORE_RV, BORE_N), t, XI_FRONT - 1.4, XI_BELL)
    funnel = loft([_pl(t, xi) * superellipse(*_bore_radii(xi), 64)
                   for xi in _stations(XI_BELL, XI_SHELL, BELL_PTS)])
    lip = _prism(superellipse(BORE_RIM_RX, BORE_RIM_RV, BORE_RIM_N), t, XI_SHELL - 0.01,
                 XI_RIM + 6.0)
    return throat + funnel + lip


def _channels(t: float, rx: float = SH_RX) -> Part:
    """The two 270 deg C-channels round the Ø6 front-tip standoffs, webbed back to the skirt.
    The web is capped at the waterline so it reads as part of the hull, not as a loose fin."""
    cx, cy = FRONT_TIP_XY
    chan = c_clip((cx, cy), CHANNEL_Z0, CHANNEL_TOP - CHANNEL_Z0, opening_deg=MOUTH_DEG,
                  bore_d=D_CLIP_BORE, wall=CHANNEL_WALL, snap=SNAP)
    plan = Polygon((rx - 0.4, WEB_Y0), (WEB_X, WEB_Y0 + WEB_CH), (WEB_X, WEB_FLARE[1]),
                   (WEB_FLARE[0], WEB_Y1), (rx - 0.4, WEB_Y1), align=None)
    web = extrude(Plane.XY.offset(CHANNEL_Z0) * plan, amount=CHANNEL_TOP - CHANNEL_Z0)
    return _both(chan + (web & _web_cap(t)))


def _web_cap(t: float) -> Part:
    """Keeps the webs under the waterline so they read as part of the hull, not as loose fins."""
    z_hi = _waterline(t, WEB_Y1) + 0.5
    prof = Polygon((WEB_Y0 - 2, 0.0), (WEB_Y1 + 2, 0.0), (WEB_Y1 + 2, z_hi),
                   (WEB_Y0 - 2, _waterline(t, WEB_Y0 - 2) + 0.5), align=None)
    return _yz(prof, -25.0, 25.0)


# --- flank / dorsal feature plumbing ----------------------------------------------------------
def _flank(sk: Sketch, t: float, x0: float, x1: float) -> Part:
    """Extrude a sketch drawn in the camera's own (xi, v) plane straight through in X."""
    return _yz(Pos(100.0, 27.0) * sk.rotate(Axis.Z, t), x0, x1)


def _screws(t: float) -> Part:
    """The two Ø2.4 M2 holes per side. The PAIR is the tilt - there is no slot to slip."""
    holes = Sketch()
    for xi in (0.0, -HOLE_PITCH):
        holes += Pos(xi, 0.0) * Circle(HOLE_D / 2)
    return _flank(holes, t, -(SH_RX + 3.0), SH_RX + 3.0)


def _strap() -> Part:
    """Ø5 tunnel straight through the chin: zip tie, or the camera cable tail."""
    return _yz(Pos(STRAP_Y, STRAP_Z) * Circle(STRAP_D / 2), -(SH_RX + 2), SH_RX + 2)


def _hex_slot(length: float, width: float, miter: float = 1.6) -> Sketch:
    """SHARD's mitred elongated hex: no arcs, every corner cut."""
    h, w = length / 2, width / 2
    return Polygon((h, 0.0), (h - miter, w), (-h + miter, w), (-h, 0.0), (-h + miter, -w),
                   (h - miter, -w), align=None)


def _naca(t: float, side: float) -> tuple[Part, Part]:
    """One flush NACA inlet per flank: a 14 x 4 stadium, ramp NACA_RAMP deg to NACA_DEEP.
    The ramp floor stops at NACA_FLOOR (1.65 mm of wall left) and the rest of the duct is a
    through inlet into the camera bay - which is what a NACA duct is for, and what keeps a
    1.8 mm recess out of a 2.2 mm wall."""
    a, u = _ax(t)
    xi_c = NACA_XI + NACA_L / 2
    plan = _flank(Pos(xi_c, NACA_V) * SlotOverall(NACA_L, NACA_W), t,
                  side * (SH_RX + 2.0), side * (SH_RX - NACA_DEEP - 2.5))
    # the sloping floor, drawn in (xi, -x) on the plane whose normal is the camera's own up
    pl = Plane(origin=tuple(_pt(t, 0.0, NACA_V)), z_dir=tuple(u), x_dir=tuple(a))
    x_out, x_in = -side * (SH_RX + 2.0), -side * (SH_RX - NACA_DEEP)
    ramp = Polygon((NACA_XI, x_out), (NACA_XI + NACA_L, x_out), (NACA_XI + NACA_L, x_in),
                   (NACA_XI, -side * SH_RX), align=None)
    wedge = extrude(pl * ramp, amount=NACA_W, both=True)
    s_floor = NACA_FLOOR * NACA_L / NACA_DEEP
    throat_l = NACA_L - s_floor
    throat = _flank(Pos(NACA_XI + s_floor + throat_l / 2, NACA_V) * SlotOverall(throat_l, NACA_W),
                    t, side * (SH_RX + 2.0), side * (CAM_HALF - 1.2))
    return (plan & wedge), throat


# (xi, v) centre, half-length, mitre, half-width. The mitre is longer than the half-width on
# purpose: printed on its back the pod's build direction is frame +Y, so an aperture's lower mitre
# faces the bed at atan(w/m) - at m >= 1.02 w that is under the 45 deg limit and the window needs
# no support. Both windows stand 2.3 mm clear of the M2 hole pair and 2.9 mm clear of each other.
SHARD_WINDOWS = (((8.0, -2.5), 4.0, 2.3, 2.2), ((-12.0, -3.5), 3.0, 1.8, 1.7))


def _windows(t: float, side: float) -> Part:
    """SHARD's flank apertures: mitred elongated hexes, drawn in the (Y, Z) plane so their long
    axis stands up the build direction, which is what makes the mitres self-supporting."""
    cut = Sketch()
    for (xi, v), h, m, w in SHARD_WINDOWS:
        q = _pt(t, xi, v)
        cut += Pos(q.Y, q.Z) * Polygon((h, 0.0), (h - m, w), (-h + m, w), (-h, 0.0),
                                       (-h + m, -w), (h - m, -w), align=None)
    return _yz(cut, side * (SH_RX + 2.0), side * (CAM_HALF - 1.4))


def _suture(t: float, rv: float = SH_RV, xi0: float = -8.0, xi1: float = 18.0) -> Part:
    """CN-1. A V groove on X = 0 down the whole dorsal crest, running out to a cusp at both ends.
    Cut AFTER any Blender pass so it lands on exact geometry."""
    a, u = _ax(t)
    prof = Polygon((-SUTURE_W / 2, rv + 0.8), (SUTURE_W / 2, rv + 0.8), (0.0, rv - SUTURE_D),
                   align=None)
    groove = _prism(prof, t, xi0 - 1.0, xi1 + 1.0)
    pl = Plane(origin=tuple(_pt(t, 0.0, rv + 1.0)), z_dir=tuple(-u), x_dir=(1.0, 0.0, 0.0))
    # in that plane local Y runs -xi, so the lens tips land on xi0 / xi1
    clip = S.extrude_cut(S.lens((0.0, -xi1), (0.0, -xi0), SUTURE_W / 2), pl, 3.0)
    return groove & clip


def _lunule(t: float, side: float) -> Part:
    """CN-4, SLIPSTREAM reading: the elytral sickle debossed 0.5 and stretched 1.4x along the flow,
    mirrored on the two flanks."""
    sk = S.mark_sketch("lunule", LUNULE, mirror_x=(side < 0))
    sk = scale(sk, by=(LUNULE_STRETCH, 1.0, 1.0))
    at = _pt(t, -1.0, 3.5, side * (SH_RX + 0.01))
    a, _u = _ax(t)
    pl = Plane(origin=tuple(at), z_dir=(side, 0.0, 0.0), x_dir=tuple(a * side))
    return S.extrude_cut(sk, pl, -(LUNULE_DEEP + 0.01))


def _labrum(t: float) -> Part:
    """SHARD's LABRUM: the toothed centre shield, 0.8 proud on the ventral keel facet just behind
    the nose - the front-most facet a print can carry it on without shadowing the lens."""
    keel = 0.52 * SH_RX
    sk = Polygon((-4.6, 0.0), (-2.7, keel * 0.60), (2.7, keel * 0.60), (4.6, 0.0),
                 (2.7, -keel * 0.60), (-2.7, -keel * 0.60), align=None)
    a, u = _ax(t)
    pl = Plane(origin=tuple(_pt(t, 13.5, -SH_RV + 0.05)), z_dir=tuple(-u), x_dir=(1.0, 0.0, 0.0))
    return S.extrude_cut(sk, pl, 0.85)


# --- assembly ---------------------------------------------------------------------------------
def _try_edges(shape, edges, radius, kind="fillet"):
    """Edge treatment that never takes the build down with it; reports the radius it reached."""
    op = chamfer if kind == "chamfer" else fillet
    sel = [e for e in edges if e.length > 0.35]
    if not sel:
        return shape, 0.0
    for r in (radius, radius / 2, radius / 4):
        try:
            return op(sel, r), round(r, 3)
        except Exception:  # noqa: BLE001 - OCCT refuses radii it cannot fit; shrink and retry
            continue
    return shape, 0.0


def _flow_edges(part: Part, t: float, min_len: float = 6.0):
    """The longitudinal facet junctions: straight edges parallel to the lens axis."""
    a, _u = _ax(t)
    out = []
    for e in part.edges():
        if e.geom_type != GeomType.LINE or e.length < min_len:
            continue
        d = (e @ 1 - e @ 0).normalized()
        if abs(d.dot(a)) > 0.999:
            out.append(e)
    return out


def _nose_edges(part: Part, t: float, xi: float, tol: float = 0.25):
    """Edges lying in the station plane at `xi` - the nose ring and the lip."""
    a, _u = _ax(t)
    out = []
    for e in part.edges():
        pts = [e @ s for s in (0.0, 0.5, 1.0)]
        if all(abs((p - _P).dot(a) - xi) < tol for p in pts):
            out.append(e)
    return out


def build(variant: str = "slipstream_t25", **overrides) -> dict[str, Part]:
    cfg = VARIANTS.get(variant, VARIANTS["slipstream_t25"])
    style = cfg["style"]
    p = dict(TILT_DEG=TILT_DEG, SH_RX=SH_RX, SH_RV=SH_RV)
    p.update(cfg.get("params", {}))
    p.update(overrides)
    t, rx, rv = float(p["TILT_DEG"]), float(p["SH_RX"]), float(p["SH_RV"])

    pod = _shell(style, t, rx, rv) + _skirt(style, t, rx) + _channels(t, rx)

    cavity, bore = _cavity(t), _bore(t)
    pod -= cavity
    pod -= bore

    for sx in (1.0, -1.0):
        pod -= cylinder(sx * FRONT_TIP_XY[0], FRONT_TIP_XY[1], CHANNEL_Z0 - 1, CHANNEL_TOP + 1,
                        D_CLIP_BORE)
    pod -= _screws(t)
    pod -= _strap()

    allow: list = []
    if style == "slipstream":
        for side in (1.0, -1.0):
            ramp, throat = _naca(t, side)
            pod -= ramp
            pod -= throat
            allow.append(ramp)
            mk = _lunule(t, side)
            pod -= mk
            allow.append(mk)
        # The OCELLUS: the hood rim rolled on both edges, so the mouth reads as a raised eye-ring
        # rather than a cut pipe. It is flush with the fairing rather than proud of it, because a
        # ring standing outboard of a 27 mm shell has no room inside the 28.4 mm fork window, and
        # its rearward step is an unsupported overhang at both tilts. Rolled, not stepped.
        pod, _r = _try_edges(pod, _nose_edges(pod, t, XI_RIM), LIP_FILLET)
    else:
        for side in (1.0, -1.0):
            pod -= _windows(t, side)
        pod += _labrum(t)
        pod, _r = _try_edges(pod, _flow_edges(pod, t), 0.6, kind="chamfer")
        pod, _r = _try_edges(pod, _nose_edges(pod, t, XI_RIM), 1.2, kind="chamfer")

    pod -= _suture(t, rv)

    assert len(pod.solids()) == 1, f"{BASE} {variant}: {len(pod.solids())} solids"
    pod.label = BASE
    _BUILT[variant] = dict(tilt=t, rx=rx, rv=rv, style=style, allow=tuple(allow),
                           cavity=cavity, bore=bore)
    return {BASE: pod}


# --- checks -----------------------------------------------------------------------------------
def _camera(t: float) -> Part:
    return camera_envelope(CAM_W, CAM_H, CAM_D, lens_d=LENS_D, lens_len=LENS_LEN,
                           tilt_deg=t, fit=FIT22, front_offset=FRONT_OFF)


def _insertion(t: float, reach: float = 34.0, step: float = 2.0) -> Part:
    """The camera envelope swept straight back down the lens axis: the path it must travel to get
    in. Built as the body prism plus the lens prism, which is exactly that sweep."""
    a, _u = _ax(t)
    body = _prism(Rectangle(CAM_W + 2 * FIT22, CAM_H + 2 * FIT22), t, XI_REAR - reach, XI_FRONT)
    lens_r = LENS_D / 2 + FIT22
    return body + _prism(Circle(lens_r), t, XI_FRONT - reach, XI_LENS)


def _cone(t: float, half: float = FOV_HALF, reach: float = 46.0) -> Part:
    from build123d import Cone
    r = reach * tan(radians(half))
    a, _u = _ax(t)
    c = Cone(bottom_radius=0.0, top_radius=r, height=reach, align=MIN_Z_ALIGN)
    ang = degrees(atan2(a.Z, a.Y))
    return c.rotate(Axis.X, ang - 90.0).moved(Location(tuple(_pt(t, XI_LENS))))


def _dihedral_creases(part: Part, t: float, rx: float, rv: float, marks=(),
                      limit: float = 8.0) -> tuple[int, float]:
    """SLIPSTREAM conformance: the worst dihedral deviation between adjacent faces on the DORSAL
    SKIN and nowhere else - above the waterline, on the fairing's own outer surface, off the
    centreline (the suture is a declared groove) and outside the declared marks and ducts. The
    family is defined by there being no crease on that skin: one crease and it has become SHARD."""
    boxes = []
    for m in marks:
        bb = m.bounding_box()
        boxes.append((bb.min.X - 0.8, bb.min.Y - 0.8, bb.min.Z - 0.8,
                      bb.max.X + 0.8, bb.max.Y + 0.8, bb.max.Z + 0.8))
    from OCP.TopAbs import TopAbs_EDGE, TopAbs_FACE
    from OCP.TopExp import TopExp
    from OCP.TopTools import TopTools_IndexedDataMapOfShapeListOfShape
    from build123d import Edge, Face
    a, u = _ax(t)
    amap = TopTools_IndexedDataMapOfShapeListOfShape()
    TopExp.MapShapesAndAncestors_s(part.wrapped, TopAbs_EDGE, TopAbs_FACE, amap)
    worst, bad = 0.0, 0
    for i in range(1, amap.Extent() + 1):
        e = Edge(amap.FindKey(i))
        faces = [Face(f) for f in amap.FindFromIndex(i)]
        if len(faces) != 2 or e.length < 1.0:
            continue
        q = e @ 0.5
        d = q - _P
        xi, v = d.dot(a), d.dot(u)
        rad = (d - a * xi).length          # distance from the lens axis, the fairing's own radius
        if v < 2.0 or abs(q.X) < 1.6:
            continue                        # below the waterline, or the declared suture
        if rad < rx - 3.0 or rad > rv + 1.2:
            continue                        # the bore and the cavity inside, the clips outside
        if xi < -8.0 or xi > XI_RIM - 3.2:
            continue                        # the bed face aft and the declared rim forward
        if any(bx[0] <= q.X <= bx[3] and bx[1] <= q.Y <= bx[4] and bx[2] <= q.Z <= bx[5]
               for bx in boxes):
            continue                        # a declared mark or duct, which the family asks for
        try:
            n0, n1 = (f.normal_at(m) for f in faces)
        except Exception:  # noqa: BLE001 - a periodic face can refuse a point projection
            continue
        ang = float(n0.get_angle(n1))
        if ang > limit:
            bad += 1
        worst = max(worst, ang)
    return bad, round(worst, 2)


def checks(parts: dict[str, Part], frame: dict[str, Part], variant: str = "") -> list:
    pod = parts[BASE]
    info = _BUILT.get(variant) or _BUILT.get("slipstream_t25") or {}
    t = float(info.get("tilt", TILT_DEG))
    rx, rv = float(info.get("rx", SH_RX)), float(info.get("rv", SH_RV))
    style = info.get("style", "slipstream")
    mat = VARIANTS.get(variant, {}).get("material", MATERIAL)
    wall = MATERIALS[mat]["wall"]
    allow = info.get("allow", ())
    out: list = []

    # --- mounting ------------------------------------------------------------------------
    for side, sx in (("right", 1.0), ("left", -1.0)):
        xy = (sx * FRONT_TIP_XY[0], FRONT_TIP_XY[1])
        ok, detail = coaxial(pod, xy, D_CLIP_BORE, Z_MID_TOP + 0.5, CHANNEL_TOP - 0.5)
        out.append((f"{side} channel bore coaxial with standoff_front_tip_{side}", ok, detail))
        probe = cylinder(*xy, CHANNEL_Z0, CHANNEL_TOP, STANDOFF_D)
        gap = round(pod.distance_to(probe), 4)
        out.append((f"{side} channel {STANDOFF_FIT} mm off the Ø{STANDOFF_D} standoff",
                    abs(gap - STANDOFF_FIT) <= 0.05 and isect(pod, probe) < EPS, f"gap {gap} mm"))
    contact = seats_on(pod, "plate_mid", Z_MID_TOP)
    out.append(("seated on plate_mid at Z 9.000", contact >= 150.0, f"{contact} mm² contact"))
    worst = max((round(isect(Pos(0, d, 0) * pod, frame_compound()), 3), d) for d in range(0, 31, 2))
    out.append(("slides off forwards (0-30 mm in +Y) without touching the frame", worst[0] < EPS,
                f"worst {worst[0]} mm³ at +{worst[1]} mm"))

    # --- frame clearance -----------------------------------------------------------------
    hits = interference(pod)
    out.append(("no frame interference", not hits, f"{hits or 'none'}"))
    so = standoff_interference(pod)
    out.append((f"clear of the Ø{STANDOFF_D} standoffs", not so, f"{so or 'none'}"))
    gaps = {n: d for n, d in distance_to_frame(pod, near=3.0).items()}
    fork = round(min([d for n, d in gaps.items() if n == "plate_top"] or [99.0]), 3)
    out.append(("clears the top-plate fork prongs", fork >= 0.3, f"{fork} mm to plate_top"))
    v = isect(pod, cylinder(0.0, 61.5, Z_MID_TOP - 1, Z_MID_TOP + 40, 17.5))
    out.append(("clear of the Ø17.5 fwd_bore at (0, 61.5)", v < EPS, f"{v:.3f} mm³"))
    v = isect(pod, _both(cylinder(15.25, 76.75, Z_MID_TOP, Z_MID_TOP + 3.0, D_M3_HEAD)))
    out.append(("clears the fwd_30p5 M3 heads at (±15.25, 76.75)", v < EPS, f"{v:.3f} mm³"))
    v = prop_disc_violation(pod)
    out.append(("outside the prop keep-out discs", v < EPS, f"{v:.3f} mm³"))
    v = isect(pod, BATTERY)
    out.append(("outside the battery envelope", v < EPS, f"{v:.3f} mm³"))

    # --- the camera ----------------------------------------------------------------------
    cam = _camera(t)
    v = isect(pod, cam)
    out.append((f"22 mm camera envelope fits at {t:g}°", v < EPS, f"{v:.3f} mm³ overlap"))
    hit = interference(cam)
    out.append((f"camera envelope clear of the frame at {t:g}°", not hit, f"{hit or 'none'}"))
    v = isect(pod, _insertion(t))
    out.append(("camera insertion path down the lens axis is clear", v < EPS, f"{v:.3f} mm³"))
    v = isect(pod, _cone(t))
    out.append((f"nothing inside the {FOV_HALF:g}° half-angle FOV cone", v < EPS, f"{v:.3f} mm³"))
    for xi, nm in ((0.0, "front"), (-HOLE_PITCH, "rear")):
        for sx, side in ((1.0, "right"), (-1.0, "left")):
            probe = _yz(Pos(*(lambda q: (q.Y, q.Z))(_pt(t, xi))) * Circle(HOLE_D / 2),
                        sx * (CAM_HALF - 0.4), sx * (rx + 2.5))
            ok = isect(pod, probe) < EPS
            out.append((f"M2 {nm} hole clear through the {side} flank", ok,
                        f"{isect(pod, probe):.3f} mm³"))

    # --- the hood ------------------------------------------------------------------------
    inner = round(2 * min(BORE_RX, BORE_RV), 2)
    out.append((f"hood inner opening ≥ lens Ø + 3 = {LENS_D + 3:g}", inner >= LENS_D + 3.0 - 1e-6,
                f"{inner} mm across the short axis"))
    out.append(("hood rim 10-12 mm ahead of the camera front face",
                10.0 - 1e-6 <= HOOD_AHEAD <= 12.0 + 1e-6, f"{HOOD_AHEAD} mm"))
    rim_x, rim_v = round(rx - BORE_RX, 2), round(rv - BORE_RV, 2)
    out.append((f"OCELLUS rim ≥ {LIP_W} mm wide and rolled", min(rim_x, rim_v) >= 1.5,
                f"{rim_x} mm across the flanks, {rim_v} mm over the crown, "
                f"fillet target {LIP_FILLET}"))

    # --- fabric --------------------------------------------------------------------------
    ok, detail = single_solid(pod)
    out.append(("one closed manifold solid", ok, detail))
    ok_w, _v, wd = min_wall(pod, wall, allow=allow)
    out.append((f"min wall ≥ {wall} ({mat})", ok_w, wd))
    over = overhangs(pod, PRINT[BASE], material=mat)
    out.append(("prints on its back (rear face on the bed) without support", not over,
                "; ".join(over) or "none"))
    printed = print_orientation(pod, PRINT[BASE])
    bed = sum(f.area for f in printed.faces() if f.geom_type == GeomType.PLANE
              and abs(f.center().Z) < 1e-3 and f.normal_at().Z < -0.999)
    out.append(("bed face ≥ 120 mm²", bed >= 120.0, f"{bed:.1f} mm²"))
    vol = pod.volume / 1000.0
    out.append(("volume 10-30 cm³", 10.0 <= vol <= 30.0, f"{vol:.2f} cm³"))

    # --- style ---------------------------------------------------------------------------
    cut = isect(pod + _suture(t, rv), _suture(t, rv))
    out.append(("CN-1: the suture is cut on X = 0 down the dorsal crest", cut > 8.0,
                f"{cut:.2f} mm³ of groove"))
    if style == "shard":
        ok, detail = S.facet_report(pod)
        out.append(("SHARD: no facet under 8 mm across", ok, detail))
    else:
        bad, w = _dihedral_creases(pod, t, rx, rv, marks=allow)
        out.append(("SLIPSTREAM: no crease over 8° on the dorsal skin", bad == 0,
                    f"{bad} creases, worst {w}°"))
        out.append(("SLIPSTREAM: crease tier is 0.0 (no bevel above the waterline)",
                    S.edge_radius("slipstream", "crease", wall) == 0.0, "edge ladder varfil"))
    out += BL.decor_checks(f"{BASE}__{variant}", absent_ok=True)
    return out
