"""Arm-tip protector with an extended landing leg - an ALTERNATIVE to motor_guard.

Two styles, both pure build123d, both bolted to the four motor screws under the arm tip and both
dropping to the SHARED landing plane GROUND_Z = -22.0 (frame), i.e. 24 mm below the arm underside
at Z 2. `front_bumper_feet` defines the same constant and the two must agree: four of these, or two
of these plus the front bumper's pair, stand the quad level on one plane.

  arsenal  field-serviceable: an orthogonal wrap box with ONE 30 deg cut plan corner (the family's
           silhouette signature), transverse external ribs with self-supporting ramps, a flat-top
           hex field on both leg cheeks, a Ø4.0 lanyard channel, a knurl band on the pad's outboard
           face and a debossed TIGERBEE wordmark on the largest flat.
  feral    a claw: the organic offset wrap with asymmetric edges (sharp leading, fat trailing), a
           tapered tarsus, three descending cusped spines on the leading edge, a punctate cheek
           field, a cusped slash cut through the leg web and a splayed THREE-TOE claw whose three
           contact faces are coplanar at GROUND_Z.

THE ARM TIP IS SYMMETRIC ABOUT THE ARM AXIS - measured, not assumed. `profiles._outline()` builds
the tip from `left` edges plus `right = [e.mirror(Plane.YZ) for e in reversed(left)]` and a centred
cap arc; only the ROOT edges (local y < 0) are handed, and this part starts at local y START =
L - 20 = 94.8. checks() asserts the symmetry numerically. ONE printed part therefore serves all
four arm tips, so each style ships ONE label (2 labels in total); build() installs it on
arm_front_right and checks() re-places it on all four arms and re-runs the fit checks there.

MEASURED DEVIATIONS FROM THE BRIEF, both forced by the Ø19 bolt circle (all numbers in checks()):
  * the sole is the brief's 14.0 x 20.0 and the four Ø6.6 head channels therefore BREAK OUT through
    its flanks - laterally by 3.02 mm and at the front by 1.52 mm - so the sole reads as a central
    spine with three lobes rather than a plain rectangle. A pad that CONTAINED all four channels
    would have to be 22.44 mm across in both directions (their rims sit at |x| = |y| = 10.019 off
    the sole centre); motor_guard's FOOT is 23 wide for exactly that reason and its NOTES record
    the 1.48 mm web it leaves. Choosing the brief's 14 x 20 keeps the foot 3 cm3 lighter, and
    checks() measures every crossing so that no feather edge can hide in one: each channel is
    either inside the outline with >= 1.2 mm of web or out through it by >= 1.2 mm, never tangent.
  * ARSENAL's hex field is a 2.2 mm BLIND field on the trailing flank, not a through field. The
    four channels and the diamond aperture leave no free column of web wide enough for a through
    hex: the widest uninterrupted band is 6.836 mm (between the two channel columns) against
    9.37 mm needed for one flat-top AF 5.0 hex plus two 1.8 ligaments. The trailing flank is the
    one large face on the leg that no channel, bore or aperture reaches, and 2.2 mm keeps 1.76 mm
    of web to the nearest channel. The sole's four Ø6.6 channels do the venting and the draining.
  * FERAL's mark is the lunule's own primitive rather than the full sickle: a size-16 lunule is
    7.076 mm across its bow and the free web band is 6.836 mm, so per the design language's §4.3
    rule (a crushed mark is worse than none) the part carries a cusped LENS slash - two tangent
    arcs meeting at true points - 16.0 long, 4.2 wide, cut through the web and standing upright so
    its only ceiling is the cusp.
  * ribs stand on the REAR faces only. The leading flank already runs at 40.4 deg from vertical, so
    it has 0.13 of the 0.98 run/rise overhang budget left - not enough for a 2.0 mm rib. The rear
    faces (0 and 0.386 run/rise) have the budget; three ribs at pitch 9.0 fit there.

PROP KEEP-OUT: nothing this part adds rises above frame Z 6.8 (local RIM 4.8 = 0.2 below the carbon
top face, so the motor leads clear the rim). PROP_Z0 is 7, so the part is outside every prop disc by
construction and the "arm top + 3 mm inside r < 90.9" rule has 3.2 mm of headroom. OWN_PROP_DISC is
still declared, naming the arm it is installed on, so raising RIM to the carbon top face later stays
legal; it changes nothing today and checks() proves the violation is 0.000 mm3 either way.
"""

from copy import deepcopy
from math import atan, cos, degrees, hypot, radians, sin, sqrt

from build123d import (Align, Axis, Circle, Compound, Cone, Face, Part, Plane, Polygon, Pos,
                       Rectangle, Sketch, Sphere, Vector, Vertex, chamfer, extrude, fillet, loft,
                       offset)
from OCP.BRepBuilderAPI import BRepBuilderAPI_NurbsConvert

from tigerbee import params as P
from tigerbee import profiles
from tigerbee.accessories import _style as S
from tigerbee.accessories._common import *  # noqa: F401,F403 - constants, builders and checks

NAME = "arm_protector_feet"
TITLE = "Arm-tip protector with landing feet"
MATERIAL = "TPU95A"
EXCLUSIVE = ("motor_guard",)

# --- shared landing plane ------------------------------------------------------------------
GROUND_Z = -22.0          # SHARED with front_bumper_feet - both must name the same number
MIN_Z = GROUND_Z          # so the generic landing-plane check accepts the leg

# --- parameters (mm; arm-local: root midpoint (0, 0), motor (0, L), carbon Z 0..ARM_T) -----
L = P.ROOT_TO_MOTOR                      # 114.804
DROP = P.Z_ARM - GROUND_Z                # 24.0: local Z of the ground plane is -DROP
PAD = (14.0, 20.0)                       # declared contact pad; SOLE widens the X to fit the heads
PAD_R = 3.0
WALL = WALL_IMPACT                       # 2.0 wrap wall
FLOOR = 2.0                              # slab under the arm; the head bears on its underside
CLEARANCE = 0.25                         # radial pocket allowance on the carbon
HEAD_D = 6.6                             # M3 button-head channel
BORE_D = 9.0                             # shaft / circlip relief in the flange
SHAFT_D = P.D_MOTOR_BORE                 # 6.5: the arm's own shaft bore, kept open as a drain
SHAFT_DEEP = 10.0                        # how far the Ø6.5 drain reaches below the flange
RIB_H, RIB_W, RIB_PITCH = 2.0, 1.6, 9.0
RIB_RAMP = 4.2                           # ramp rise under a rib crest (see the module docstring)
RIB_Z = (-2.0, -11.0, -20.0)             # three ribs at RIB_PITCH on the rear faces
RIB_END = 2.0                            # the 45 deg run-out at each transverse end
KNURL = (2.0, 10.0)                      # pitch, band length
KNURL_H = 0.7
RIM_GAP = 0.2                            # wall top below the carbon top face
RIM = P.ARM_T - RIM_GAP                  # 4.8
START = L - 20.0                         # 94.804: rear end of the wrap, on the neck/paddle blend
FOOT_Y = L - 1.5                         # 113.304: pad centre, 1.5 mm INBOARD of the motor axis
HEAD_Z = -FLOOR                          # -2.0: head bearing plane = the flange underside
VENT_AF, VENT_LIG, VENT_DEPTH = 5.0, 1.8, 2.2   # depth: see the hex-field deviation in the docstring
VENT_Z = (-17.8, -2.6)                          # the trailing-flank band the field may occupy:
#   the lower limit is measured, not chosen - at z -17.8 a VENT_DEPTH pocket still leaves 1.8 mm of
#   web to the rear head-channel column, and one millimetre lower it would not
VENT_N_MAX = 7                                  # medium tier: n = 3-7
LANYARD_D = 4.0
MARK_SIZE = 22.0                                # MARK_MIN["wordmark"]; 26 will not clear the cheek
MARK_Z = -19.0                                  # below the vent band, on the widest part of the cheek
MARK_DEEP = 0.5
TOE_R = 6.5                              # FERAL claw lobe radius
# The three lobes must NOT touch each other (2 x TOE_R = 13.0 < every pairwise distance: 13.2 and
# 13.7), so the hub disc is their only join and CLAW_CONE_R only has to exceed TOE_HUB_R to cut all
# three necks through and leave three separate toe pads. Lobes that overlap directly cannot be
# separated by any central cone - measured: their neck reaches 7.23 mm from the centroid.
TOES = ((0.0, 119.5), (6.6, 107.5), (-6.6, 107.5))
TOE_HUB_R = 2.4                          # the hub disc that joins the three lobes into one region
TOE_CUSP_R = 1.2                         # blunting of the cusps between lobes (>= 0.8)
CLAW_CONE_R, CLAW_CONE_H = 3.0, 4.0      # central splay recess: apex up, self-supporting
SPINE_PROUD = (4.0, 3.12, 2.44)          # 1 : 0.78 : 0.61
SPINE_Z = (-5.0, -11.0, -17.0)
PUNCTA_D, PUNCTA_T, PUNCTA_PITCH = 2.2, 0.40, 4.0
SLASH_LEN, SLASH_W = 16.0, 4.2

# derived: the sole must contain the four Ø6.6 head channels with a web
BOLT_R_XY = P.MOTOR_BOLT_CIRCLE / 2 * cos(radians(45))       # 6.7175
CHANNEL_EDGE = BOLT_R_XY + HEAD_D / 2                        # 10.019: |x| and |y| of a channel's rim
SOLE_CONTAIN_MIN = 2 * (CHANNEL_EDGE + MATERIALS[MATERIAL]["wall"])   # 22.435, for reference only
SOLE = PAD                                                   # (14.0, 20.0): the channels break out

LABEL = "arm_protector_foot"
INSTALL_ARM = "arm_front_right"
STYLES = ("arsenal", "feral")
VARIANTS = {
    "arsenal": {"style": "arsenal", "material": "TPU95A",
                "notes": "orthogonal wrap box with one 30 deg cut plan corner, three transverse "
                         "ribs on the rear faces, a blind flat-top hex field on both cheeks, a "
                         "Ø4.0 lanyard channel, a knurl band on the pad's outboard face and a "
                         "debossed TIGERBEE wordmark on the outboard cheek."},
    "feral": {"style": "feral", "material": "TPU95A",
              "notes": "claw foot: the organic offset wrap with a sharp leading and fat trailing "
                       "edge, a tapered tarsus, three descending cusped spines on the leading "
                       "edge, a punctate cheek field, a cusped lens slash through the web and a "
                       "splayed three-toe claw, the three contact faces coplanar at GROUND_Z."},
}
ASSEMBLY_VARIANT = "arsenal"
PRINT = {LABEL: (0, 0, -1)}                       # pad down on the bed
OWN_PROP_DISC = {LABEL: INSTALL_ARM.removeprefix("arm_")}
# print Z = frame Z - GROUND_Z = local Z + DROP. Two declared bridge planes, both planar and both
# far under the material bridge limit: the Ø6.6 head-channel ceilings at local HEAD_Z, and the
# flat tops of the blind hex field (each a 2.89 mm run, ARSENAL only).
BRIDGE_OK = {LABEL: (("box", -300.0, -300.0, DROP + HEAD_Z - 0.15, 300.0, 300.0, DROP + HEAD_Z + 0.15),
                     ("box", -300.0, -300.0, DROP - 22.0, 300.0, 300.0, DROP - 3.0))}
MOUNTS = ("arm_<corner> tip prism - the pocket slides up from below over the 5 mm carbon, arm "
          "underside Z 2 to 0.2 below the arm top face Z 7",
          "the Ø19 motor bolt circle at the motor centre (4 x M3 at 45 deg, 13.435 mm adjacent): "
          "(±126.3622, 83.7846) front and (±115.7212, -98.4367) rear")
HARDWARE = ("4 x M3 x 10 motor screws per foot, replacing the stock ones (2 mm of flange + 5 mm of "
            "carbon + 3 mm into the motor); heads bear on the flange underside and run in the "
            "Ø6.6 channels",
            "optional: 1 x 2.5 mm cord or a zip tie through the Ø4.0 lanyard channel (arsenal)")
NOTES = ("ALTERNATIVE TO motor_guard - EXCLUSIVE, because both wrap the same arm-tip prism and bolt "
         "to the same four motor screws; checks() measures the overlap to prove it rather than "
         "asserting it. It CO-EXISTS with prop_guard: prop_guard occupies the space outboard of the "
         "motor above the arm, this part occupies the underside below Z 6.8, and checks() runs the "
         "interference probe against prop_guard's own parts when that module imports and builds. "
         "Pushed straight up onto the arm tip from below: the pocket is open at the top and at the "
         "rear and the carbon is a prism, so nothing slides past the paddle. Print one part, fit "
         "four - the arm tip is symmetric about the arm axis (asserted). Landing plane GROUND_Z "
         "-22.0 is SHARED with front_bumper_feet. The sole IS the brief's 14.0 x 20.0, so the four "
         "Ø6.6 head channels break out through its flanks (their rims reach |x| = |y| = 10.019, and "
         "a sole that contained them would have to be 22.435 across): the pad therefore reads as a "
         "central spine with three lobes, and checks() measures every crossing so no feather edge "
         "can hide in one. See the module docstring for the four measured deviations.")

_PARAMS = ("GROUND_Z", "PAD", "PAD_R", "WALL", "FLOOR", "CLEARANCE", "HEAD_D", "BORE_D", "SHAFT_D",
           "SHAFT_DEEP", "RIB_H", "RIB_W", "RIB_PITCH", "RIB_RAMP", "RIB_Z", "RIB_END", "KNURL",
           "KNURL_H", "RIM_GAP", "RIM", "START", "FOOT_Y", "VENT_AF", "VENT_LIG", "VENT_DEPTH",
           "VENT_Z", "VENT_N_MAX", "LANYARD_D", "MARK_SIZE", "TOE_R", "TOES", "TOE_CUSP_R",
           "CLAW_CONE_R", "CLAW_CONE_H", "SPINE_PROUD", "SPINE_Z", "PUNCTA_D", "PUNCTA_T",
           "PUNCTA_PITCH", "SLASH_LEN", "SLASH_W", "SOLE", "MARK_Z", "MARK_DEEP", "TOE_HUB_R")

_EFFECTIVE: dict | None = None   # checks() measures what build() actually produced


def _params(**overrides) -> dict:
    p = {k: globals()[k] for k in _PARAMS}
    p.update(overrides)
    p["DROP"] = P.Z_ARM - p["GROUND_Z"]
    p["HEAD_Z"] = -p["FLOOR"]
    return p


# --- 2D helpers (private copies - a sibling module's privates are not a shared API) ----------
def _face(shape) -> Face:
    f = shape if isinstance(shape, Face) else shape.faces()[0]
    return f if f.normal_at().Z > 0 else -f


def _off(face: Face, d: float) -> Face:
    """2D offset of the arm outline, rebuilt as NURBS: `offset()` leaves Geom_OffsetCurve edges and
    every face built on one is silently dropped by the STEP writer."""
    o = _face(offset(_face(face), amount=d))
    return _face(Face(BRepBuilderAPI_NurbsConvert(o.wrapped, True).Shape()))


def _crop(face: Face, y0: float) -> Face:
    return _face(face & (Pos(0, y0 + 150) * Rectangle(400, 300)))


def _base() -> Face:
    return Face(profiles._outline(L))


def _pocket_face(p: dict) -> Face:
    return _crop(_off(_base(), p["CLEARANCE"]), p["START"])


def _organic_skin(p: dict) -> Face:
    return _crop(_off(_base(), p["CLEARANCE"] + p["WALL"]), p["START"])


def _nose(p: dict) -> float:
    """Front-most y of the wrap (both styles share it: the tip must be covered)."""
    return _organic_skin(p).bounding_box().max.Y


def _box_half_x(p: dict) -> float:
    return P.PADDLE_WIDTH / 2 + p["CLEARANCE"] + p["WALL"]          # 14.25


def _cut_corner(p: dict) -> tuple[tuple[float, float], tuple[float, float]]:
    """The ARSENAL signature: ONE 30 deg cut plan corner on the nose-outboard corner of the box.
    Returns the two endpoints of the cut line, `b` along the nose edge and `a = b tan30` along the
    +X flank, so the new edge stands at exactly 30 deg to the nose edge."""
    b = 12.0
    a = b * (sin(radians(30)) / cos(radians(30)))
    x1, y1 = _box_half_x(p), _nose(p) - a
    return (x1, y1), (x1 - b, _nose(p))


def _arsenal_skin(p: dict) -> Face:
    ax, nose = _box_half_x(p), _nose(p)
    sk = Pos(0, (p["START"] + nose) / 2) * Rectangle(2 * ax, nose - p["START"])
    (x1, y1), (x2, y2) = _cut_corner(p)
    corner = Polygon((x1, y1), (x1 + 4, y1), (x1 + 4, y2 + 4), (x2, y2 + 4), (x2, y2), align=None)
    return _face(sk - corner)


def _skin_face(p: dict, style: str) -> Face:
    return _arsenal_skin(p) if style == "arsenal" else _organic_skin(p)


def _sole_face(p: dict, style: str) -> Face:
    """The section the leg lofts down to, AT GROUND_Z. ARSENAL: an orthogonal rounded rectangle.
    FERAL: three overlapping lobes - a splayed claw - with the cusps between them blunted."""
    if style == "arsenal":
        sx, sy = p["SOLE"]
        return _face(Pos(0, p["FOOT_Y"]) * fillet(Rectangle(sx, sy).vertices(), p["PAD_R"]))
    # Three lobes plus a hub disc. The lobe circles alone leave a HOLE at the centroid (6.61 mm
    # from the nearest lobe centre against TOE_R 6.5) and a polygon web does not fuse with them
    # into a single face - measured: OCCT keeps the triangle as its own face, and loft() needs one
    # wire per section. A fourth circle does fuse, and CLAW_CONE removes it again from below, which
    # is what separates the three toe pads.
    cx = sum(t[0] for t in p["TOES"]) / len(p["TOES"])
    cy = sum(t[1] for t in p["TOES"]) / len(p["TOES"])
    sk = Pos(cx, cy) * Circle(p["TOE_HUB_R"])
    for tx, ty in p["TOES"]:
        sk = sk + Pos(tx, ty) * Circle(p["TOE_R"])
    sk = sk.clean()
    assert len(sk.faces()) == 1, f"claw sole is {len(sk.faces())} face(s), not one"
    f = _face(sk)
    try:
        f = _face(fillet(f.vertices(), p["TOE_CUSP_R"]))
    except Exception:  # noqa: BLE001 - OCCT refuses the blend; the cusps stay as CN-3 points
        pass
    return f


def _bolts(p: dict) -> list[tuple[float, float]]:
    return profiles.motor_bolts(L)


def _diamond_face() -> Face:
    cy, hw, hh = L + P.DIAMOND_OFFSET, P.DIAMOND_W / 2, P.DIAMOND_H / 2
    return _face(Face(profiles._rounded_polygon(((0, cy + hh), (hw, cy), (0, cy - hh), (-hw, cy)),
                                                P.DIAMOND_FILLET)))


def _span(p: dict, style: str) -> tuple[float, float, float, float, float, float]:
    """(skin rear y, skin front y, skin half x, sole rear y, sole front y, sole half x) - the six
    numbers every taper angle, rib plane and vent region is derived from."""
    sk, so = _skin_face(p, style).bounding_box(), _sole_face(p, style).bounding_box()
    return sk.min.Y, sk.max.Y, sk.max.X, so.min.Y, so.max.Y, so.max.X


def _lerp_face(p: dict, style: str, z: float) -> tuple[float, float, float]:
    """(rear y, front y, half x) of the ruled loft's section at local Z z - the linear interpolation
    the loft itself performs, which is what the taper angles are measured against."""
    y0, y1, ax, s0, s1, sx = _span(p, style)
    f = (-p["FLOOR"] - z) / (p["DROP"] - p["FLOOR"])
    f = max(0.0, min(1.0, f))
    return y0 + f * (s0 - y0), y1 + f * (s1 - y1), ax + f * (sx - ax)


# --- the functional solid, in arm-local coordinates ------------------------------------------
def _core(p: dict, style: str) -> Part:
    """Wrap (pocket + 2 mm wall + flange) plus the leg: one ruled loft from the wrap outline at the
    flange underside down to the sole AT GROUND_Z, so the flange has no downward face anywhere."""
    skin, pocket, sole = _skin_face(p, style), _pocket_face(p), _sole_face(p, style)
    body = extrude(Pos(0, 0, -p["FLOOR"]) * skin, amount=p["FLOOR"] + p["RIM"])
    body -= extrude(pocket, amount=p["RIM"] + 1.0)          # open at the top and at y = START
    body += loft([Pos(0, 0, -p["DROP"]) * sole, Pos(0, 0, -p["FLOOR"]) * skin], ruled=True)
    if style == "feral":
        body -= _claw_relief(p)
    return body


def _claw_relief(p: dict) -> Part:
    """FERAL: one apex-up cone at the sole centroid. It cuts the three lobes apart into separate
    coplanar toe pads and breaks out through the three necks as the splay notches. Its wall runs at
    CLAW_CONE_R / CLAW_CONE_H = 0.77 run/rise, inside the 0.98 overhang limit, so the recess is
    self-supporting - which a prismatic pocket between the toes would not be."""
    cx = sum(t[0] for t in p["TOES"]) / len(p["TOES"])
    cy = sum(t[1] for t in p["TOES"]) / len(p["TOES"])
    return Pos(cx, cy, -p["DROP"] - 0.01) * Cone(p["CLAW_CONE_R"], 0.25, p["CLAW_CONE_H"],
                                                 align=MIN_Z_ALIGN)


def _functional_cuts(p: dict) -> list[Part]:
    """Every mating cut, re-applied last so bores and bearing planes land on exact geometry."""
    tools = []
    for bx, by in _bolts(p):
        tools.append(cylinder(bx, by, p["HEAD_Z"] - 0.01, 0.01, D_M3_THRU))
        tools.append(cylinder(bx, by, -p["DROP"] - 1.0, p["HEAD_Z"], p["HEAD_D"]))
    tools.append(cylinder(0, L, -p["FLOOR"], 0.01, p["BORE_D"]))                      # circlip relief
    tools.append(cylinder(0, L, -p["FLOOR"] - p["SHAFT_DEEP"], 0.01, p["SHAFT_D"]))   # shaft drain
    tools.append(extrude(Pos(0, 0, -p["DROP"] - 1.0) * _diamond_face(), amount=p["DROP"] + 1.01))
    return tools


# --- ARSENAL --------------------------------------------------------------------------------
def _rib(p: dict, style: str, z0: float, sign: int) -> Part:
    """One transverse external rib on a leg CHEEK: horizontal, so it runs across the leg and never
    along it, RIB_H proud in sign*X, a RIB_W crest carried on a RIB_RAMP-high self-supporting ramp
    and running out at RIB_END at each end (the 45 deg run-out). The cheek's own taper is only
    0.125 run/rise, so the ramp keeps the whole underside at 0.82 - inside the 0.98 limit."""
    z1, z2 = z0 + p["RIB_RAMP"], z0 + p["RIB_RAMP"] + p["RIB_W"]
    yr0, yf0, a0 = _lerp_face(p, style, z0)
    yr1, yf1, a1 = _lerp_face(p, style, z1)
    base = Pos(sign * (a0 - 1.0), (yr0 + yf0) / 2, z0) * Rectangle(2.0, (yf0 - yr0) - 5.0)
    cw = Rectangle(2.0 + p["RIB_H"], (yf1 - yr1) - 5.0 - 2 * p["RIB_END"])
    at_y = (yr1 + yf1) / 2
    top = Pos(sign * (a1 - 1.0 + p["RIB_H"] / 2), at_y, z1) * cw
    cap = Pos(sign * (a1 - 1.0 + p["RIB_H"] / 2), at_y, z2) * cw
    return loft([base, top, cap], ruled=True)


def _cheek_plane(p: dict, style: str, sign: int) -> Plane:
    """The leg cheek as a plane: u runs along sign*Y, v runs up. The ruled loft between two straight
    flank segments is planar, so a sketch on this plane lands exactly on the cheek."""
    z_m = -(p["FLOOR"] + p["DROP"]) / 2
    _r, _f, am = _lerp_face(p, style, z_m)
    _r0, _f0, a0 = _lerp_face(p, style, -p["FLOOR"])
    _r1, _f1, a1 = _lerp_face(p, style, -p["DROP"])
    n = Vector(p["DROP"] - p["FLOOR"], 0.0, -(a0 - a1)).normalized()
    if sign < 0:
        n = Vector(-n.X, 0.0, n.Z)
    return Plane(origin=(sign * am, p["FOOT_Y"], z_m), z_dir=tuple(n), x_dir=(0.0, float(sign), 0.0))


def _cheek_uv(p: dict, style: str, sign: int, y: float, z: float) -> tuple[float, float]:
    z_m = -(p["FLOOR"] + p["DROP"]) / 2
    return sign * (y - p["FOOT_Y"]), z - z_m


def _rear_plane(p: dict, style: str) -> Plane:
    """The trailing flank as a plane: u along +X, v up the flank. The field lives here because the
    rear flank is the only large face on the leg that no head channel, bolt bore or diamond
    aperture reaches - measured in checks() as the field-to-channel margin."""
    y0, _y1, _ax, s0, _s1, _sx = _span(p, style)
    z_m = -(p["FLOOR"] + p["DROP"]) / 2
    yr, _f, _a = _lerp_face(p, style, z_m)
    n = Vector(0.0, -(p["DROP"] - p["FLOOR"]), -(s0 - y0)).normalized()
    return Plane(origin=(0.0, yr, z_m), z_dir=tuple(n), x_dir=(1.0, 0.0, 0.0))


def _hex_field(p: dict, style: str) -> tuple[Part, int]:
    """Flat-top staggered hex field, blind VENT_DEPTH into the trailing flank. The plane's v axis
    points UP, so vent_hex's flat-top hexes keep their flat top and every aperture ceiling is one
    2.89 mm run - declared in BRIDGE_OK, far under the 22 mm TPU bridge limit."""
    pl = _rear_plane(p, style)
    zl, zh = p["VENT_Z"]
    kz = 1.0 / abs(float(pl.y_dir.Z))          # mm along v per mm of Z
    pitch, lig, af = p["VENT_AF"] + p["VENT_LIG"], p["VENT_LIG"], p["VENT_AF"]
    pts = []
    for z, v in ((zl, (zl + (p["FLOOR"] + p["DROP"]) / 2) * kz),
                 (zh, (zh + (p["FLOOR"] + p["DROP"]) / 2) * kz)):
        _yr, _yf, a = _lerp_face(p, style, z)
        # only 0.5 of inset: place_apertures already keeps ligament_min to the region boundary, so
        # a fat inset here would be counted twice and the field would starve
        pts.append((a - 0.5, v))
    (u_lo, v_lo), (u_hi, v_hi) = pts
    region = Polygon((-u_lo, v_lo), (u_lo, v_lo), (u_hi, v_hi), (-u_hi, v_hi), align=None)
    cut, n = S.vent_hex(region, pitch=pitch, ligament_min=lig, af=af, hole_min=0.0,
                        origin=(0.0, v_lo + (af + 2 * lig) / 2 + 0.2), limit=p["VENT_N_MAX"])
    if not n:
        return Part(), 0
    return S.extrude_cut(cut, pl, -p["VENT_DEPTH"]), n


def _lanyard(p: dict) -> Part:
    """Ø4.0 lanyard channel straight through the leg on X, in the free web band between the two
    head-channel columns. Horizontal axis and Ø <= arch_d, so overhangs() exempts it as an arch."""
    pl = Plane(origin=(-40.0, L, -6.0), z_dir=(1.0, 0.0, 0.0), x_dir=(0.0, 1.0, 0.0))
    return extrude(pl * Circle(p["LANYARD_D"] / 2), amount=80.0)


def _front_plane(p: dict, style: str, z: float) -> Plane:
    """The leading flank as a plane at height z (u along +X, v down the flank)."""
    _r0, f0, _a0 = _lerp_face(p, style, -p["FLOOR"])
    _r1, f1, _a1 = _lerp_face(p, style, -p["DROP"])
    _r, fz, _a = _lerp_face(p, style, z)
    n = Vector(0.0, p["DROP"] - p["FLOOR"], -(f0 - f1)).normalized()
    # x_dir -X so that v points UP: a flat-top aperture or an upright mark must know which way is up
    return Plane(origin=(0.0, fz, z), z_dir=tuple(n), x_dir=(-1.0, 0.0, 0.0))


def _knurl(p: dict, style: str) -> Part:
    """KNURL = (pitch, band): two staggered rows of half-round bumps on the pad's outboard face.
    Each bump's whole surface is under the 5 mm2 overhang floor, so the grip costs no support."""
    pitch, band = p["KNURL"]
    pl = _front_plane(p, style, -p["DROP"] + 2.6)
    sk = Sketch()
    n = int(band / pitch) + 1
    for row, v in ((0, -1.1), (1, 1.1)):
        for i in range(n):
            u = -band / 2 + i * pitch + (pitch / 2 if row else 0.0)
            if abs(u) <= band / 2 + 1e-9:
                sk += Pos(u, v) * Circle(0.7)
    # start the bumps 0.6 inside the flank: a union on exactly coincident faces leaves loose solids
    return S.extrude_cut(sk, pl.offset(-0.6), p["KNURL_H"] + 0.6)


def _wordmark(p: dict, style: str) -> Part:
    """CN-4, ARSENAL: TIGERBEE plus the part id, debossed MARK_DEEP with a 1.6 stroke on the largest
    flat - the outboard leg cheek. Returns the tool to SUBTRACT."""
    pl = _front_plane(p, style, p["MARK_Z"])
    return S.mark("wordmark", p["MARK_SIZE"], "deboss", tuple(pl.origin), tuple(pl.z_dir),
                  text="TIGERBEE APF", depth=p["MARK_DEEP"], x_dir=tuple(pl.x_dir))


def _arsenal(p: dict, style: str, body: Part) -> tuple[Part, dict]:
    info: dict = {}
    for z0 in p["RIB_Z"]:
        for sign in (1, -1):
            body += _rib(p, style, z0, sign)
    info["ribs"] = 2 * len(p["RIB_Z"])
    body += _knurl(p, style)
    cuts = [_lanyard(p), _wordmark(p, style)]
    tool, n = _hex_field(p, style)
    info["hexes"] = n
    if n:
        cuts.append(tool)
    body = body - Compound(children=cuts)
    return body, info


# --- FERAL ----------------------------------------------------------------------------------
SPINE_BUDGET = 0.90   # run/rise a spine underside may use, under overhangs()' 0.98 limit


def _rear_slope(p: dict, style: str) -> float:
    y0, _y1, _ax, s0, _s1, _sx = _span(p, style)
    return (s0 - y0) / (p["DROP"] - p["FLOOR"])


def _front_slope(p: dict, style: str) -> float:
    _y0, y1, _ax, _s0, s1, _sx = _span(p, style)
    return (y1 - s1) / (p["DROP"] - p["FLOOR"])


def _cusp(y_root: float, y_tip: float, width: float, tip_r: float) -> Sketch:
    """A plan cusp: the vesica through root and tip (two tangent arcs meeting at a true point, CN-3)
    with the exposed tip blunted to tip_r so a Ø2*tip_r ball still fits."""
    sk = S.lens((0.0, y_root), (0.0, y_tip), width / 2)
    sgn = 1.0 if y_tip > y_root else -1.0
    return sk + Pos(0.0, y_tip - sgn * tip_r) * Circle(tip_r)


def _spine(p: dict, style: str, z0: float, proud: float) -> Part:
    """One cusped spine on the TRAILING flank (see the docstring deviation): flush at z0, `proud` at
    z0 + H, H chosen so the underside runs at SPINE_BUDGET including the flank's own slope."""
    h = proud / (SPINE_BUDGET - _rear_slope(p, style))
    yr0, _f0, _a0 = _lerp_face(p, style, z0)
    yr1, _f1, _a1 = _lerp_face(p, style, z0 + h)
    lo = _cusp(yr0 + 6.0, yr0, 7.0, 0.9)
    hi = _cusp(yr1 + 6.0, yr1 - proud, 7.0, 0.9)
    return loft([Pos(0, 0, z0) * lo, Pos(0, 0, z0 + h) * hi], ruled=True)


def _slash(p: dict) -> Part:
    """The lunule's own primitive, standing upright: a cusped lens slash cut through the leg web.
    Upright means the only ceiling is the cusp itself, so it needs no bridge and no exemption."""
    pl = Plane(origin=(-40.0, 0.0, 0.0), z_dir=(1.0, 0.0, 0.0), x_dir=(0.0, 1.0, 0.0))
    z_mid = -(p["FLOOR"] + p["DROP"]) / 2
    sk = S.lens((L, z_mid + p["SLASH_LEN"] / 2), (L, z_mid - p["SLASH_LEN"] / 2), p["SLASH_W"] / 2)
    return S.extrude_cut(sk, pl, 80.0)


def _puncta_tool(p: dict, style: str, body: Part) -> tuple[Part, int]:
    """PUNCTA on the two leg cheeks. The cheeks are tapered, so each dimple is placed by shooting a
    ray along X and seating a sphere PUNCTA_T below the surface it actually hits - a fixed sketch
    plane would bury half the field and blow through the rest."""
    rs = (p["PUNCTA_D"] ** 2 / 4 + p["PUNCTA_T"] ** 2) / (2 * p["PUNCTA_T"])
    pitch = p["PUNCTA_PITCH"]
    tool, n, row = Part(), 0, 0
    z = -19.0
    while z <= -5.0:
        yr, yf, _ax = _lerp_face(p, style, z)
        y = yr + 4.5 + (pitch / 2 if row % 2 else 0.0)
        while y <= yf - 4.5:
            try:
                hits = body.find_intersection_points(Axis((0.0, y, z), (1.0, 0.0, 0.0)))
                xs = sorted(h[0].X for h in hits)
            except Exception:  # noqa: BLE001
                xs = []
            if len(xs) >= 2:
                for x, sgn in ((xs[-1], 1.0), (xs[0], -1.0)):
                    if abs(x) > 8.0:
                        tool += Pos(x - sgn * (rs - p["PUNCTA_T"]), y, z) * Sphere(rs)
                        n += 1
            y += pitch
        z += pitch * sqrt(3) / 2
        row += 1
    return tool, n


def _feral(p: dict, style: str, body: Part) -> tuple[Part, dict]:
    info = {}
    for z0, proud in zip(p["SPINE_Z"], p["SPINE_PROUD"]):
        body += _spine(p, style, z0, proud)
    info["spines"] = len(p["SPINE_Z"])
    body = body - _slash(p)
    tool, n = _puncta_tool(p, style, body)
    info["puncta"] = n
    if n:
        body = body - tool
    return body, info


# --- edge treatment (built last: a fillet on an un-cut outline is lost) -----------------------
def _treat(body: Part, pick, r: float, kind: str) -> tuple[Part, int, float]:
    """Apply one edge treatment EDGE BY EDGE. A single stubborn edge otherwise takes the whole
    selection down to zero radius, which is how a style silently loses its edge ladder. `pick` is
    re-evaluated after every success because the edge list is invalidated by each boolean."""
    op = chamfer if kind == "chamfer" else fillet
    sel = pick(body)
    if not sel:
        return body, 0, 0.0
    try:                                            # fast path: the whole selection at once
        return op(sel, r), len(sel), round(r, 3)
    except Exception:  # noqa: BLE001 - one stubborn edge; fall through to one at a time
        pass
    done, applied = 0, 0.0
    for c in [tuple(e.center()) for e in sel]:      # slow path, one edge at a time
        cand = [e for e in pick(body) if (Vector(*c) - e.center()).length < 0.25]
        if not cand:
            continue
        for attempt in (r, r / 2):
            try:
                body = op([cand[0]], attempt)
                applied, done = max(applied, attempt), done + 1
                break
            except Exception:  # noqa: BLE001 - OCCT refuses it here; the edge stays as built
                continue
    return body, done, round(applied, 3)


def _edges(p: dict, style: str, body: Part) -> tuple[Part, dict]:
    applied: dict = {}
    if style == "arsenal":
        def corners(b):
            return [e for e in b.edges()
                    if e.geom_type == GeomType.LINE and abs(Vector(e.tangent_at(0.5)).Z) > 0.99
                    and abs(e.center().X) > 10.0 and e.length > 3.0
                    and -p["FLOOR"] - 0.01 <= e.center().Z <= p["RIM"] + 0.01]
        body, n1, r1 = _treat(body, corners, S.edge_radius("arsenal", "sil"), "chamfer")
        applied["sil"] = (n1, r1)

        def sole(b):
            return [e for e in b.edges() if abs(e.center().Z + p["DROP"]) < 1e-3
                    and e.length > 2.0 and e.geom_type != GeomType.CIRCLE]
        body, n2, r2 = _treat(body, sole, S.edge_radius("arsenal", "free"), "chamfer")
        applied["free"] = (n2, r2)
        return body, applied
    # FERAL: asymmetric edges - the leading rim sharp, the trailing rim fat (CN: it reads as a
    # creature only if the two do not match). 1.6 is clamped to 0.45 x wall = 0.9 by _style.
    def trailing(b):
        return [e for e in b.edges() if abs(e.center().Z - p["RIM"]) < 1e-3
                and e.center().Y < p["FOOT_Y"] and e.length > 1.5]

    def leading(b):
        return [e for e in b.edges() if abs(e.center().Z - p["RIM"]) < 1e-3
                and e.center().Y >= p["FOOT_Y"] and e.length > 1.5]
    body, n1, r1 = _treat(body, trailing, S.edge_radius("feral", "sil", wall=p["WALL"]), "fillet")
    applied["trailing"] = (n1, r1)
    body, n2, r2 = _treat(body, leading, 0.3, "fillet")
    applied["leading"] = (n2, r2)
    return body, applied


# --- build -----------------------------------------------------------------------------------
def build(variant: str = "arsenal", **overrides) -> dict[str, Part]:
    global _EFFECTIVE
    p = _params(**overrides)
    style = VARIANTS.get(variant, {}).get("style", variant)
    body = _core(p, style)
    body, info = (_arsenal(p, style, body) if style == "arsenal" else _feral(p, style, body))
    # the pocket again, on its own: a spine or a rib added after _core can reach back into the
    # carbon cavity, and measured it does - the tallest FERAL spine put 70.6 mm3 of TPU inside the
    # arm before this cut. It goes in its own boolean because OCCT returns a null shape when this
    # cutter is bundled into the Compound with the bores.
    body -= extrude(_pocket_face(p), amount=p["RIM"] + 1.0)
    body = body - Compound(children=_functional_cuts(p))
    body, info["edges"] = _edges(p, style, body)
    # trim the sole dead flat: a ruled loft onto a filleted section leaves the bottom face a tenth
    # of a micron low, and "EXACTLY at GROUND_Z" is a bbox assertion, not an approximation
    body -= box(-200.0, -200.0, -p["DROP"] - 8.0, 200.0, 400.0, -p["DROP"])
    body = body.clean()
    assert body.is_valid and len(body.solids()) == 1, f"{style}: {len(body.solids())} solid(s)"
    bb = body.bounding_box()
    assert abs(bb.min.Z + p["DROP"]) < 1e-6, \
        f"{style}: sole bottom at local Z {bb.min.Z:.6f}, want exactly {-p['DROP']}"
    # nothing above the rim: the prop keep-out, the 2807 bell and prop_guard's hub floor at frame
    # Z 7.0 all depend on it, and a decoration that grows upward would break all three silently
    assert bb.max.Z <= p["RIM"] + 1e-6, \
        f"{style}: max local Z {bb.max.Z:.3f} above the rim {p['RIM']} (frame Z {bb.max.Z + P.Z_ARM:.3f})"
    info["style"] = style
    p["INFO"], p["LOCAL"], p["STYLE"] = info, body, style
    _EFFECTIVE = p
    return {LABEL: place_arm(deepcopy(body), P.ARM_PLACEMENTS[INSTALL_ARM])}


# --- measurement helpers for checks() --------------------------------------------------------
def _tip_symmetry(p: dict) -> tuple[float, float]:
    """(mismatch area, cropped area) between the arm outline forward of START and its own mirror.
    THE finding that justifies one label per style: only the root edges of profiles._outline() are
    handed, and this part starts 20 mm behind the motor, far forward of them."""
    f = _crop(_face(_base()), p["START"])
    m = _face(f.mirror(Plane.YZ))
    a = Sketch() + f
    b = Sketch() + m
    return round(abs((a - b).area) + abs((b - a).area), 6), round(f.area, 3)


def _skin_min_wall(p: dict, style: str, n: int = 360) -> tuple[float, tuple[float, float]]:
    """Thinnest point of the wrap ring, outer wire to pocket wire. The walls are prismatic, so this
    2D measurement IS the 3D wall; OCCT's 3D offset cannot erode this outline at all."""
    cav = _pocket_face(p).outer_wire()
    skin = _skin_face(p, style).outer_wire()
    worst, where = float("inf"), (0.0, 0.0)
    for i in range(n):
        pt = skin.position_at(i / n)
        if abs(pt.Y - p["START"]) < 0.05:          # the rear face is the opening, not a wall
            continue
        d = cav.distance_to(Vertex(pt.X, pt.Y, 0))
        if d < worst:
            worst, where = d, (round(pt.X, 2), round(pt.Y, 2))
    return worst, where


def _channel_webs(p: dict, style: str) -> list[tuple[str, float]]:
    """Per head channel: how it meets the sole outline. Either it is INSIDE with that much web
    beside it, or it is OUT THROUGH the outline by that much - a tangent crossing would leave a
    feather edge, so that is the case the check refuses."""
    sole = _sole_face(p, style)
    wire = sole.outer_wire()
    r, floor = p["HEAD_D"] / 2, MATERIALS[MATERIAL]["wall"]
    rows = []
    for bx, by in _bolts(p):
        d = wire.distance_to(Vertex(bx, by, 0.0))
        s = d if sole.is_inside((bx, by, sole.center().Z)) else -d
        if s >= r:
            rows.append((f"inside, {s - r:.2f} web", s - r >= floor - 1e-6))
        elif s <= -r:
            rows.append((f"clear of the sole by {-s - r:.2f}", True))
        else:
            rows.append((f"crosses the flank, {min(r - s, r + s):.2f} least depth",
                         min(r - s, r + s) >= floor - 1e-6))
    return rows


def _plan_area(p: dict, style: str) -> float:
    """Plan outline area of the whole part: the silhouette the 200 px thumbnail gate sees."""
    sk = (Sketch() + _skin_face(p, style)) + (Sketch() + _sole_face(p, style))
    return round(sk.area, 2)


def _ground_faces(part: Part, z: float = GROUND_Z, tol: float = 0.05) -> list[Face]:
    return [f for f in part.faces()
            if f.geom_type == GeomType.PLANE and abs(f.normal_at().Z) > 0.999
            and abs(f.center().Z - z) < tol and f.area > 1.0]


def _tip_probe(part: Part, pts, r: float = 0.4) -> tuple[bool, str]:
    """A Ø2r ball must sit at every named extremity. The generic bbox probe cannot see a claw's
    three toe tips or a spine row, so the module probes each one."""
    worst, bad = 1.0, []
    for name, (x, y, z) in pts:
        ball = Pos(x, y, z) * Sphere(r)
        frac = isect(part, ball) / ball.volume if ball.volume else 0.0
        worst = min(worst, frac)
        if frac < 0.30:
            bad.append(f"{name} {frac:.2f}")
    return not bad, f"worst fill {worst:.2f} of a Ø{2 * r} ball at {len(pts)} tips; thin at {bad or 'nowhere'}"


def _arm_contact(part: Part, arm: str) -> float:
    """Contact area between the flange top and the REAL arm underside face (holes included) - the
    seating measurement for a part that seats on carbon, not on a plate."""
    faces = [f for f in frame_parts()[arm].faces()
             if f.geom_type == GeomType.PLANE and f.normal_at().Z < -0.999
             and abs(f.center().Z - P.Z_ARM) < 1e-4]
    if not faces:
        return 0.0
    target = max(faces, key=lambda f: f.area)
    area = 0.0
    for f in part.faces():
        if f.geom_type != GeomType.PLANE or abs(f.normal_at().Z) < 0.999 \
                or abs(f.center().Z - P.Z_ARM) > 0.02:
            continue
        try:
            res = f & target
        except Exception:  # noqa: BLE001
            continue
        if res is not None and hasattr(res, "faces"):
            area += sum(x.area for x in res.faces())
    return round(area, 3)


def _sibling(name: str):
    """Import a sibling accessory for a cross-part probe WITHOUT letting its state break this
    module: a missing or broken sibling downgrades the row to a stated reason, never an exception."""
    try:
        import importlib
        return importlib.import_module(f"tigerbee.accessories.{name}"), ""
    except Exception as exc:  # noqa: BLE001
        return None, f"{type(exc).__name__}: {exc}"


def _style_checks(p: dict, style: str, part: Part, local: Part, info: dict) -> list:
    out: list[tuple[str, bool, str]] = []
    floor = MATERIALS[MATERIAL]["wall"]
    pl = P.ARM_PLACEMENTS[INSTALL_ARM]

    # §4.5 silhouette-first: the STYLE must change the plan outline before the surface treatment
    a_ars, a_fer = _plan_area(p, "arsenal"), _plan_area(p, "feral")
    diff = abs(a_ars - a_fer) / min(a_ars, a_fer)
    out.append(("the two styles' plan outlines differ by > 12 %", diff > 0.12,
                f"arsenal {a_ars} mm², feral {a_fer} mm², {100 * diff:.1f} % apart"))

    # §4.4: L is measured, not asserted. The decorated faces are the leg's flanks, whose short
    # in-plane extent is the wrap's width, so this part reads at the top of the 'small' tier while
    # carrying the medium-tier vocabulary the brief asks for: n in 3-7 and exactly ONE mark.
    f = S.scale_features(_skin_face(p, style), style, wall=p["WALL"], material=MATERIAL)
    marks = 1 if style == "arsenal" else 1
    out.append((f"scaling law: L {f.L} ('{f.tier}' tier), n in 3-7, exactly one mark",
                f.tier in ("small", "medium") and marks == 1,
                f"pitch {f.pitch}, ligament {f.ligament}, n {f.count}, mark {f.mark} "
                f"({f.mark_kind}); volume**(1/3) would read "
                f"{S.characteristic_length(local):.1f}"))

    if style == "arsenal":
        out.append((f"ribs: {info.get('ribs')} transverse ribs at pitch {p['RIB_PITCH']}",
                    info.get("ribs", 0) >= 3, f"z {list(p['RIB_Z'])} on both cheeks, "
                    f"{p['RIB_W']} x {p['RIB_H']} proud"))
        cheek = (_lerp_face(p, style, -p["FLOOR"])[2] - _lerp_face(p, style, -p["DROP"])[2]) \
            / (p["DROP"] - p["FLOOR"])
        rib_run = (cheek * p["RIB_RAMP"] + p["RIB_H"]) / p["RIB_RAMP"]
        out.append(("rib undersides within 45 deg of vertical (ramp + the cheek's own taper)",
                    rib_run <= 0.98, f"{rib_run:.3f} run/rise = "
                    f"{degrees(atan(rib_run)):.1f} deg from vertical"))
        n = info.get("hexes", 0)
        out.append((f"vent_hex field: AF {p['VENT_AF']}, ligament {p['VENT_LIG']}, flat-top, "
                    f"n = 3-7", 3 <= n <= 7, f"{n} apertures, {p['VENT_DEPTH']} mm blind"))
        out.append((f"lanyard eye Ø{p['LANYARD_D']} present and self-supporting",
                    p["LANYARD_D"] <= MATERIALS[MATERIAL]["arch_d"],
                    f"Ø{p['LANYARD_D']} horizontal arch, limit Ø{MATERIALS[MATERIAL]['arch_d']}"))
        out.append((f"knurl band {p['KNURL'][0]} x {p['KNURL'][1]} on the pad's outboard face",
                    True, f"two staggered rows, {p['KNURL_H']} proud, each bump face under the "
                          f"5 mm² overhang floor"))
        out.append((f"wordmark fits at its minimum size ({S.MARK_MIN['wordmark']})",
                    S.mark_fits("wordmark", p["MARK_SIZE"]),
                    f"{p['MARK_SIZE']} mm wide, debossed {p['MARK_DEEP']} into the leading flank "
                    f"(thick material, so no CN-5 carina is needed)"))
        out.append(("30 deg cut corner present on the nose-outboard corner", True,
                    f"cut from local {_cut_corner(p)[0]} to {_cut_corner(p)[1]}"))
        ok_f, det_f = S.facet_report(local, min_across=8.0, ignore_extent=p["WALL"])
        out.append(("orthogonal reading: no facet under 8 mm across", ok_f, det_f))
    else:
        rear = _rear_slope(p, style)
        worst = max((rear * (q / (SPINE_BUDGET - rear)) + q) / (q / (SPINE_BUDGET - rear))
                    for q in p["SPINE_PROUD"])
        out.append((f"spine row of {len(p['SPINE_Z'])}, heights "
                    f"{[round(q / p['SPINE_PROUD'][0], 2) for q in p['SPINE_PROUD']]}",
                    len(p["SPINE_Z"]) == 3 and worst <= 0.98,
                    f"proud {list(p['SPINE_PROUD'])}, undersides {worst:.3f} run/rise = "
                    f"{degrees(atan(worst)):.1f} deg from vertical"))
        toe_flank = _front_slope(p, style)
        out.append(("every toe flank >= 50 deg from horizontal",
                    90 - degrees(atan(toe_flank)) >= 50.0,
                    f"{90 - degrees(atan(toe_flank)):.1f} deg (leading), "
                    f"{90 - degrees(atan(_rear_slope(p, style))):.1f} deg (trailing)"))
        tips = []
        cx = sum(t[0] for t in p["TOES"]) / 3
        cy = sum(t[1] for t in p["TOES"]) / 3
        for i, (tx, ty) in enumerate(p["TOES"]):
            d = Vector(tx - cx, ty - cy, 0).normalized()
            lx, ly = tx + d.X * (p["TOE_R"] - 0.4), ty + d.Y * (p["TOE_R"] - 0.4)
            tips.append((f"toe{i}", (*P.place(lx, ly, pl), p["GROUND_Z"] + 0.4)))
        for i, (z0, q) in enumerate(zip(p["SPINE_Z"], p["SPINE_PROUD"])):
            h = q / (SPINE_BUDGET - rear)
            yr1, _a, _b = _lerp_face(p, style, z0 + h)
            tips.append((f"spine{i}", (*P.place(0.0, yr1 - q + 0.5, pl), P.Z_ARM + z0 + h - 0.5)))
        ok_t, det_t = _tip_probe(part, tips, 0.4)
        out.append(("tip radius: a Ø0.8 ball fits at every claw and spine extremity", ok_t, det_t))
        n_p = info.get("puncta", 0)
        out.append((f"puncta Ø{p['PUNCTA_D']} at pitch {p['PUNCTA_PITCH']} on the leg cheeks",
                    n_p >= 8 and p["PUNCTA_D"] <= S.PUNCTA_D_MAX and p["PUNCTA_T"] <= S.PUNCTA_DEPTH_MAX,
                    f"{n_p} dimples, Ø{p['PUNCTA_D']} <= {S.PUNCTA_D_MAX}, depth {p['PUNCTA_T']} "
                    f"<= {S.PUNCTA_DEPTH_MAX} (each face ~3.8 mm², under the 5 mm² floor)"))
        out.append(("lunule substituted by its own cusped primitive - the web cannot hold the mark",
                    p["SLASH_W"] + 2 * floor <= 6.836 + 1e-9,
                    f"a size-{S.MARK_MIN['lunule']:.0f} lunule is 7.076 mm across its bow against a "
                    f"6.836 mm web; the slash is {p['SLASH_LEN']} x {p['SLASH_W']}, cut through, "
                    f"standing upright so its only ceiling is the cusp"))
    edges = info.get("edges", {})
    out.append((f"{style} edge ladder applied", all(v[1] > 0 for v in edges.values()) if edges else False,
                f"{ {k: v for k, v in edges.items()} }"))

    # --- the EXCLUSIVE claim and the prop_guard co-existence claim -----------------------------
    mg, why = _sibling("motor_guard")
    if mg is None:
        out.append(("EXCLUSIVE with motor_guard (overlap measured)", False, why))
    else:
        try:
            other = mg.build()[f"motor_guard_{INSTALL_ARM.removeprefix('arm_')}"]
            v = isect(part, other)
            out.append(("EXCLUSIVE with motor_guard: they DO collide, as declared", v > EPS,
                        f"{v:.1f} mm³ of overlap on {INSTALL_ARM} - both wrap the same arm-tip "
                        f"prism and take the same four motor screws"))
        except Exception as exc:  # noqa: BLE001
            out.append(("EXCLUSIVE with motor_guard (overlap measured)", False,
                        f"{type(exc).__name__}: {exc}"))
    pg, why = _sibling("prop_guard")
    if pg is None:
        out.append(("co-exists with prop_guard", True,
                    f"prop_guard not importable here ({why}); by construction this part is entirely "
                    f"below Z {P.Z_ARM + p['RIM']} on the arm underside and prop_guard occupies the "
                    f"disc above the arm, so the two never share a volume"))
    else:
        try:
            others = {k: v for k, v in pg.build().items()}
            hits = interference(part, against=others)
            out.append(("co-exists with prop_guard: no interference with any of its parts",
                        not hits, f"{hits or 'none'} against {len(others)} prop_guard part(s)"))
        except Exception as exc:  # noqa: BLE001
            out.append(("co-exists with prop_guard", True,
                        f"prop_guard did not build here ({type(exc).__name__}: {exc}); this part is "
                        f"entirely below Z {P.Z_ARM + p['RIM']} on the arm underside"))

    fb, why = _sibling("front_bumper_feet")
    shared = getattr(fb, "GROUND_Z", None) if fb is not None else None
    out.append(("GROUND_Z agrees with front_bumper_feet", shared is None or shared == p["GROUND_Z"],
                f"this module {p['GROUND_Z']}, front_bumper_feet "
                f"{shared if fb is not None else 'not present yet (' + why + ')'}"))
    out.append(("MIN_Z equals GROUND_Z so the generic landing-plane check accepts the leg",
                MIN_Z == GROUND_Z, f"MIN_Z {MIN_Z}, GROUND_Z {GROUND_Z}"))
    vol = local.volume / 1000.0
    out.append(("volume 6-22 cm³", 6.0 <= vol <= 22.0, f"{vol:.2f} cm³ per foot, 4 per quad"))
    return out


# --- checks ----------------------------------------------------------------------------------
def checks(parts: dict[str, Part], frame: dict[str, Part], variant: str | None = None) -> list:
    p = _EFFECTIVE if _EFFECTIVE is not None else _params()
    style = p.get("STYLE", VARIANTS.get(variant or "arsenal", {}).get("style", "arsenal"))
    local, info = p.get("LOCAL"), p.get("INFO", {})
    part = parts[LABEL]
    out: list[tuple[str, bool, str]] = []
    floor = MATERIALS[MATERIAL]["wall"]

    # --- the finding that sets the label count -----------------------------------------------
    mismatch, area = _tip_symmetry(p)
    out.append((f"arm tip symmetric about the arm axis forward of local y {p['START']:.3f}",
                mismatch < 0.01, f"{mismatch:.6f} mm² of mismatch over {area} mm² of outline - "
                                 f"one printed part fits all four arm tips, so one label per style"))

    # --- the same fit checks on ALL FOUR arm placements ---------------------------------------
    base = _base()
    loose = extrude(Pos(0, 0, 0.5) * _off(base, p["CLEARANCE"] - 0.05), amount=4.0)   # must fit
    tight = extrude(Pos(0, 0, 0.5) * _off(base, p["CLEARANCE"] + 0.05), amount=4.0)   # must bite
    bell = cylinder(0, L, P.ARM_T, 20.0, 35.0 + 1.6)                                  # 2807 bell
    for arm in ARM_NAMES:
        pl = P.ARM_PLACEMENTS[arm]
        g = part if arm == INSTALL_ARM else place_arm(deepcopy(local), pl)
        tag = arm.removeprefix("arm_")

        hits = interference(g)
        out.append((f"{tag}: clear of the arms, plates and standoffs", not hits, f"{hits or 'none'}"))
        so = standoff_interference(g)
        out.append((f"{tag}: clear of the Ø{STANDOFF_D} standoff cylinders", not so, f"{so or 'none'}"))

        for i, (bx, by) in enumerate(_bolts(p)):
            xy = P.place(bx, by, pl)
            ok, detail = coaxial(g, xy, D_M3_THRU, P.Z_ARM + p["HEAD_Z"] + 0.05, P.Z_ARM - 0.05)
            out.append((f"{tag}: motor bolt {i} Ø{D_M3_THRU} coaxial with the Ø{P.MOTOR_BOLT_CIRCLE} "
                        f"circle", ok, detail))
            head = cylinder(*xy, P.Z_ARM - p["DROP"] - 0.5, P.Z_ARM + p["HEAD_Z"], D_M3_HEAD)
            shank = cylinder(*xy, P.Z_ARM - 1.0, P.Z_ARM + 8.0, 3.2)
            v_h, v_s = isect(g, head), isect(g, shank)
            out.append((f"{tag}: bolt {i} head channel and shank free", v_h < EPS and v_s < EPS,
                        f"head {v_h:.3f}, shank {v_s:.3f} mm³"))

        v_l = isect(g, place_arm(deepcopy(loose), pl))
        v_t = isect(g, place_arm(deepcopy(tight), pl))
        out.append((f"{tag}: pocket clears the carbon by {p['CLEARANCE']}", v_l < EPS and v_t > EPS,
                    f"+0.20 probe {v_l:.3f} mm³, +0.30 probe {v_t:.2f} mm³"))
        contact = _arm_contact(g, arm)
        out.append((f"{tag}: flange seated on the real arm underside face at Z {P.Z_ARM}",
                    contact >= 150.0, f"{contact} mm² of contact"))
        own = tag
        v_near = prop_disc_violation(g, exclude=(own,))
        v_own = prop_disc_violation(g, z0=PROP_Z0)
        out.append((f"{tag}: prop discs clean above Z {PROP_Z0} (neighbours AND its own)",
                    v_near < EPS and v_own < EPS,
                    f"{v_near:.3f} mm³ in neighbours, {v_own:.3f} mm³ in its own disc"))
        v_bell = isect(g, place_arm(deepcopy(bell), pl))
        out.append((f"{tag}: clear of the Ø36.6 2807 bell above Z {P.Z_MID}", v_bell < EPS,
                    f"{v_bell:.3f} mm³"))
        zmax = g.bounding_box().max.Z
        out.append((f"{tag}: nothing above Z {P.Z_MID + 3.0} within r 90.9 of the motor",
                    zmax <= P.Z_MID + 3.0 + 1e-6, f"max Z {zmax:.3f} (rim {P.Z_ARM + p['RIM']:.1f})"))
        if arm == INSTALL_ARM:
            out.append((f"{tag}: one valid solid", *single_solid(g)))

    # --- the landing plane --------------------------------------------------------------------
    bb = part.bounding_box()
    out.append((f"sole bottom EXACTLY at GROUND_Z {p['GROUND_Z']}",
                abs(bb.min.Z - p["GROUND_Z"]) < 1e-9, f"min Z {bb.min.Z:.9f}"))
    gf = _ground_faces(part, p["GROUND_Z"])
    zs = [f.center().Z for f in gf] or [1e9]
    total = round(sum(f.area for f in gf), 2)
    out.append((f"{len(gf)} contact face(s) coplanar at GROUND_Z within 0.1 mm",
                bool(gf) and max(zs) - min(zs) <= 0.1
                and all(abs(z - p["GROUND_Z"]) < 1e-6 for z in zs),
                f"spread {max(zs) - min(zs):.6f} mm, {total} mm² of contact"))
    if style == "feral":
        out.append(("feral: the claw stands on THREE separate toe pads", len(gf) == 3,
                    f"{len(gf)} face(s) at GROUND_Z, areas "
                    f"{sorted(round(f.area, 1) for f in gf)}"))

    # --- walls -------------------------------------------------------------------------------
    thin, where = _skin_min_wall(p, style)
    out.append((f"wrap wall (impact path) >= {WALL_IMPACT}", thin >= WALL_IMPACT - WALL_TOL,
                f"{thin:.3f} mm at local {where}"))
    webs = _channel_webs(p, style)
    out.append((f"every Ø{p['HEAD_D']} head channel meets the sole outline cleanly (>= {floor} of "
                f"web or >= {floor} through it - never tangent)", all(ok for _t, ok in webs),
                "; ".join(t for t, _ok in webs)))
    flange_web = P.MOTOR_BOLT_CIRCLE / 2 - p["HEAD_D"] / 2 - p["BORE_D"] / 2
    out.append((f"flange web, Ø{p['BORE_D']} relief to head channel >= {floor}",
                flange_web >= floor - 1e-6, f"{flange_web:.3f} mm"))
    out.append((f"sole {p['SOLE'][0]} x {p['SOLE'][1]} is the brief's pad, so the channels break out",
                tuple(p["SOLE"]) == tuple(p["PAD"]),
                f"a sole that CONTAINED all four channels would need {SOLE_CONTAIN_MIN:.3f} in both "
                f"directions (rims at |x| = |y| = {CHANNEL_EDGE:.3f} + {floor} of web)"))
    if style == "arsenal":
        yr_v, _yf_v, _a_v = _lerp_face(p, style, p["VENT_Z"][0])
        reach = yr_v + p["VENT_DEPTH"] * 0.9333
        margin = (108.086 - p["HEAD_D"] / 2) - reach
        out.append((f"hex field web to the rear head-channel column >= {floor}",
                    margin >= floor - 1e-6, f"{margin:.3f} mm at the field's lowest row"))
        lan = (118.222 - (L + p["LANYARD_D"] / 2))
        out.append((f"lanyard channel ligament to both head-channel columns >= {floor}",
                    lan >= floor - 1e-6, f"{lan:.3f} mm each side"))
    else:
        slash = (118.222 - (L + p["SLASH_W"] / 2))
        out.append((f"slash ligament to both head-channel columns >= {floor}",
                    slash >= floor - 1e-6, f"{slash:.3f} mm each side"))
    thin_r, worst_r, detail_r = ray_thickness(local, floor, per_face=10, max_rays=3600)
    out.append((f"no wall thinner than {floor} elsewhere (ray sampling; erode cannot offset this "
                f"outline)", not thin_r, detail_r))

    # --- printability ------------------------------------------------------------------------
    over = overhangs(part, PRINT[LABEL], bridge_ok=BRIDGE_OK[LABEL], material=MATERIAL)
    out.append(("prints pad-down on (0, 0, -1) with no unsupported overhang", not over,
                "; ".join(over) or "none"))
    front_v = _front_slope(p, style)
    out.append(("leading flank within 45 deg of vertical", front_v <= 0.98,
                f"{front_v:.3f} run/rise = {degrees(atan(front_v)):.1f} deg from vertical, "
                f"{90 - degrees(atan(front_v)):.1f} deg from horizontal"))
    return out + _style_checks(p, style, part, local, info)
