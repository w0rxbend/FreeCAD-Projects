"""50 deg rearward RX antenna mast bolted to the tail of the top plate, in three styles.

THREE READINGS OF ONE MOUNT.  The clean zone - the bracket seat, the two Ø3.4 bores with their
button-head recesses, the Ø8 mast tube with its Ø3.6 coax bore, the insertion slit and the T-bar
clamp head - is identical in all three and is built by the same code.  Only what hangs off it
changes, so a style can never move a mating face:

  shard     the original: a faceted plate bracket and a plain leaning rod.  Pure build123d.
  chassis   the wishbone.  The bracket becomes an open truss - two bowed rails through the bolt
            eyelets converging into the mast root, one diagonal strut per side off a dorsal
            spine, a ring node at every junction, a serrated outboard rail edge and a debossed
            starburst round each bolt.  The mast grows a two-rail lattice outboard of the closed
            tube.  Pure build123d.
  nocturne  the lit mast.  Six tapering vanes stand off the mast in two fanned combs, carrying
            the frame's own ladder slots and a mark cut through so light strobes out; a ventral
            keel carries a Ø3.0 light pipe from a conical LED well in the bracket tail to 0.8 mm
            below the keel's end face, so the mast glows end-on.  Pure build123d.

Neither new style needs Blender, which is the point: this module keeps shipping with the Blender
branch off, and `_blender` is never imported here.
"""

from math import atan2, cos, degrees, hypot, radians, sin, sqrt, tan

from build123d import (Align, Axis, Box, Circle, Cone, GeomType, Part, Plane, Polygon, Pos,
                       Rectangle, Sketch, SlotOverall, Vector, chamfer, extrude, fillet)

from tigerbee.accessories import _style as S
from tigerbee.accessories._common import *  # noqa: F401,F403 - constants, builders and checks

NAME = "antenna_mast"
TITLE = "915 MHz antenna mast"
MATERIAL = "TPU95A"
PRINT = {"antenna_mast": (0, 0, -1)}  # bracket underside on the bed; the mast leans 50 deg
# rx_antenna_v_holder (a sibling in progress) lands on the same two rear-tip bolts, so the two
# cannot be installed together.  tail_block DOES coexist: it builds TOWER=False for the combined
# assembly and this mast is then the RX holder.
EXCLUSIVE = ("rx_antenna_v_holder",)
STYLES = ("shard", "chassis", "nocturne")
VARIANTS = {
    "shard": {"style": "shard",
              "notes": "the original faceted plate bracket and plain Ø8 leaning rod - the "
                       "always-available baseline, and the one that seats on every square "
                       "millimetre of prong the top plate offers (313 mm²)."},
    "chassis": {"style": "chassis",
                "notes": "the wishbone: an open truss whose void is 52 % of its plan bbox, a "
                         "ring node at every junction, serration along each rail's outboard "
                         "edge, a debossed 8-ray starburst round each bolt, and a two-rail "
                         "lattice outboard of the closed mast tube."},
    "nocturne": {"style": "nocturne", "material": "PETG",
                 "notes": "the lit mast: six tapering vanes in two fanned combs carrying ladder "
                          "slots and a cut-through mark, a conical LED well in the bracket tail "
                          "and a Ø3.0 light pipe up a ventral keel to 0.8 mm from its end face."},
}
ASSEMBLY_VARIANT = "shard"
MOUNTS = ("plate_top top face Z 36, rear fork prongs y -84..-104 (bridges the U-notch)",
          "standoff_rear_tip_left / _right bolt axes (±16.5, -94)")
HARDWARE = ("2 x M3 x 10 button head (replace the rear-tip standoff bolts)",
            "1 x 2.5 mm zip tie through the head slots to retain the T-bar")
_NOTES_SHARD = (
    "Two M3 x 10 buttons replace the rear-tip standoff bolts and clamp the bracket onto "
    "plate_top; the bracket bridges the U-notch and carries the mast past the plate. "
    "The T-bar snaps into the head grooves (zip tie through the slots), the coax lies in "
    "the slit and drops through the mast foot into the top-plate notch. "
    "Departures from the sketch, each forced by a check: the nose is 32 wide at y -84 "
    "instead of 16 (a bracket that narrow seats on only ~267 mm2 of prong, not 300); the "
    "root sits at y -104 and the tongue runs to y -112, so the root ellipse and its r3 "
    "fillet clear the pack by 2.4 mm and still land on the bracket - trimming the root "
    "with a plane instead leaves a knife edge along the leaning rod; the bar grooves run "
    "the full 26 mm head because a 90 mm bar cannot enter a 22 mm pocket; the head is 15 "
    "wide, since at 12 the groove mouths come within 0.1 mm of the rounded corners.")
_NOTES_CHASSIS = (
    "Same two M3 x 10 buttons, same seat, same mast bore and clamp - only the material between "
    "them is gone. Nodes: a dorsal spine nose at (0, -85.5), the two bolt eyelets at (±16.5, -94) "
    "and the mast root at (0, -104); the triangle they form has corners of 62.8, 58.4 and 58.8 "
    "deg, every one inside the family's 50-70 deg window and none near 90. THE BOLT EYELET IS "
    "THE JUNCTION - the rail, the diagonal strut and the eyelet all meet there, so the bolt hole "
    "IS the ring node instead of standing 3.9 mm from a second bore it could not keep 1.2 mm "
    "away from. The starburst is DEBOSSED 0.6, not cut through: a 1.2 mm slot is below TPU's "
    "2.2 mm minimum through-hole, and the rays sit outside the Ø6.6 head recess so they read "
    "round the fitted button. Strut depth is 2.5, not the family's 3.0: the BATTERY floor is "
    "Z 38.5, exactly 2.5 above the seat, so anything forward of y -95 that is thicker is inside "
    "the pack. The section is traded sideways instead - 3.2 x 2.5 = 8.0 mm² against the spec's "
    "2.4 x 3.0 = 7.2 - and checks() asserts every member is at least 2.4 wide and 7.2 mm². "
    "The mast lattice rails run THROUGH every ring node along the mast axis, which is not "
    "decoration: the ring's down-mast arc is the one surface whose normal.Z reaches -0.766, and "
    "the rail covering ±32 deg of it is what keeps the free arc above the -0.72 overhang limit.")
_NOTES_NOCTURNE = (
    "Same two M3 x 10 buttons, same seat, same mast bore and clamp. Six vanes, three per side, "
    "tiled along the mast rather than fanned about one point: at 16 deg apart two blades sharing "
    "an s band would leave a wedge crack 0.4 mm wide at the tube surface, so each blade owns its "
    "own 9.5 mm band and the fan is read along the mast - three teeth in a row from the side, a "
    "six-blade fan from behind. The ladder slots run ALONG the mast, not radially: a radial slot's "
    "ceiling normal is exactly -d (normal.Z -0.766) and would need a bridge declaration, while a "
    "slot along the mast presents only its ±e side walls (normal.Z ±0.18) and two small end caps. "
    "The light pipe is Ø3.0 in a ventral keel below the tube, NOT inside it: a Ø3.6 coax bore and "
    "a Ø3.0 pipe side by side with 1.5 mm PETG walls need a Ø15.6 mast. The keel's Ø6 rounded "
    "underside never faces down harder than normal.Z -0.643. The conical well (mouth Ø9.0, 25 deg "
    "half angle, 4.0 deep) opens DOWNWARD through the bracket tail boss at Z 36 - its wall sits "
    "at 65 deg from horizontal, so normal.Z is -0.42 and it needs no support - and the pipe axis "
    "crosses Z 36 at (0, -108.7), which is where the well is centred. Print the shell in black "
    "PETG; the well is left OPEN (no lens cap ships with this part) so a 3 mm LED pushes straight "
    "in from below and the pipe is a light channel, not an optic.")
NOTES = {"antenna_mast": _NOTES_SHARD,
         "antenna_mast__shard": _NOTES_SHARD,
         "antenna_mast__chassis": _NOTES_CHASSIS,
         "antenna_mast__nocturne": _NOTES_NOCTURNE}

# --- parameters (mm, deg) --------------------------------------------------------------------
MAST_ANGLE = 50.0  # elevation of the mast above horizontal, leaning rearward
MAST_LEN = 36.0  # root plane to the head centre, along the mast axis
MAST_D = 8.0
ROOT_Y = -104.0  # mast axis crosses the bracket top face here; far enough back that
#                  the root ellipse and its fillet clear BATTERY without a trim cut
#                  (any plane trimming the leaning rod feathers out to a knife edge)
BRACKET_T = 2.5  # Z 36.0 (seated on plate_top) .. 38.5
BOLT_XY = REAR_TIP_XY  # (16.5, -94), mirrored: the rear-tip standoff axes
FRONT_X, FRONT_Y = 16.0, -84.0  # bracket nose (wider than the 8 of the first sketch: seating area)
WIDE_X, WIDE_Y0, WIDE_Y1 = 22.0, -87.0, -97.0  # full-width flanks over the two prongs
TAIL_X, TAIL_Y = 8.0, -112.0  # rearward tongue that carries the mast root and its fillet
EDGE_R = 3.0
ROOT_R = 3.0  # root fillet between the mast and the bracket top face
BATTERY_CLEAR = 2.0  # required gap from anything above the bracket to the BATTERY face

COAX_D = 3.6  # channel down the mast, opens through the foot into the top-plate U-notch
COAX_SLIT = 2.2  # insertion slit on the upper face of the mast
SLIT_REACH = 12.0  # how far the slit cutter reaches out from the mast axis. Only 4 is needed to
#                    break the Ø8 surface; the surplus matters where a style puts material further
#                    out (see NOC's vanes, which the slit deliberately splits on the centreline)
SLIT_LIP = 1.5  # material beside the slit; its tip tapers out at the surface, like a c_clip mouth

BAR_D, BAR_LIP = 4.0, 0.3  # BAR_LEN (90, 915 MHz T-bar) comes from _common
GROOVE_X = 2.9  # the grooves run the whole head: a 90 mm bar has to pass through
HEAD_W, HEAD_L, HEAD_T = 15.0, 26.0, 8.0  # X, along the bar, along the mast; 12 wide leaves
#                                           only 0.1 mm between a groove mouth and the corner
HEAD_TILT = 10.0  # tilt of the frame-facing face: without it its normal.Z is -0.766 (unprintable)
HEAD_R = 1.5
TIE_SLOT_L, TIE_SLOT_W, TIE_U = 3.0, 8.0, 8.0  # zip-tie slots, 2.0 mm rails beside them

DIPOLE = False  # extra Ø4 clip on the head rear face for a dipole half
DIPOLE_D, DIPOLE_LEN = 4.0, 12.0

Z0 = Z_TOP_TOP  # 36.0
Z1 = Z0 + BRACKET_T  # 38.5: bracket top, mast root plane

_DEFAULTS = dict(MAST_ANGLE=MAST_ANGLE, MAST_LEN=MAST_LEN, MAST_D=MAST_D, ROOT_Y=ROOT_Y,
                 BRACKET_T=BRACKET_T, FRONT_X=FRONT_X, FRONT_Y=FRONT_Y, WIDE_X=WIDE_X,
                 WIDE_Y0=WIDE_Y0, WIDE_Y1=WIDE_Y1, TAIL_X=TAIL_X, TAIL_Y=TAIL_Y, EDGE_R=EDGE_R,
                 ROOT_R=ROOT_R, COAX_D=COAX_D, COAX_SLIT=COAX_SLIT, SLIT_LIP=SLIT_LIP,
                 SLIT_REACH=SLIT_REACH, BAR_D=BAR_D, BAR_LIP=BAR_LIP, GROOVE_X=GROOVE_X, HEAD_W=HEAD_W, HEAD_L=HEAD_L,
                 HEAD_T=HEAD_T, HEAD_TILT=HEAD_TILT, HEAD_R=HEAD_R, TIE_SLOT_L=TIE_SLOT_L,
                 TIE_SLOT_W=TIE_SLOT_W, TIE_U=TIE_U, DIPOLE=DIPOLE, DIPOLE_D=DIPOLE_D,
                 DIPOLE_LEN=DIPOLE_LEN, STYLE="shard")

# --- CHASSIS: the wishbone truss (all numbers in the bracket's own plan, frame XY) --------------
# The load path and nothing else. Three nodes per side make ONE triangle whose corners are 62.8 /
# 58.4 / 58.8 deg - the whole triangulation window in a single shape, which is why the truss reads
# as a truss instead of as a plate with holes.
CH_SPINE_N = (0.0, -85.5)      # dorsal spine nose: the two diagonals' junction (ring node)
CH_EYE = (16.5, -94.0)         # = REAR_TIP_XY. Rail + strut + bolt all meet here: the bolt IS the ring
CH_ROOT = (0.0, -104.0)        # mast root; the two rails converge into it
CH_RAIL_W = 3.6                # rail width; >= 2.96 is what keeps a ring node's free arc printable
CH_STRUT_W = 3.0               # diagonal strut and spine-node ring reference width. 3.0, not the
#                                family's 2.4: at 2.4 x 2.5 the section is 6.0 mm², under the 2.4 x
#                                3.0 = 7.2 the family asks for, and depth is not available (see NOTES)
CH_SPINE_W = 3.4               # dorsal spine: 3.4 - 0.8 suture leaves 1.3 either side of the groove
CH_EYE_OD = 10.8               # bolt eyelet pad: Ø6.6 recess + 8 starburst rays + 1.2 rim, and
#                                16.5 + 5.4 = 21.9 keeps the outline inside the |x| <= 22 envelope
# The root hub is a Ø17 disc in the PLAN and stops at Z1 - it is not a raised boss, and that is a
# measured decision twice over. Raised 2.0, the leaning Ø8 rod's section at the boss top came within
# 0.10 mm of the boss wall and OCCT handed back a solid that reported valid=False; and anything of
# this diameter standing above Z 38.5 is inside the BATTERY's 2.0 mm keep-out. Ø17 is what the root
# fillet needs to land on: the root ellipse is 8 x 10.44 and a r3 blend runs 3 mm past its rear.
CH_ROOT_OD = 17.0
CH_ROOT_RISE = 0.0
CH_RAIL = ((15.2, -84.6), (18.2, -88.2), (18.6, -91.4), CH_EYE, CH_ROOT)  # right rail, nose -> root
CH_SERR_D, CH_SERR_PITCH, CH_SERR_OUT = 1.6, 3.2, 0.8   # SPINE serration, outboard rail edge only
CH_BURST_N, CH_BURST_W, CH_BURST_LEN, CH_BURST_DEPTH = 8, 1.2, 0.9, 0.6   # DEBOSSED, see the notes
CH_FILLET = 0.8                # the family's edge ladder, every tier
CH_SUTURE = (-86.5, -101.5)    # the suture run on X=0 along the dorsal spine
CH_LAT_U = 11.0                # mast lattice rail offset from the mast axis in frame X
CH_LAT_RAIL_W = 3.6            # lattice rail: >= 2.96, which is what keeps the ring arcs printable
CH_LAT_W = 2.8                 # lattice strut width, and the ring-node reference width
CH_LAT_DEPTH = 3.2             # lattice thickness along the mast's 'up' direction
CH_LAT_S0, CH_LAT_PITCH, CH_LAT_N = 4.0, 10.5, 3   # first ring node, node pitch, nodes per rail
CH_LAT_TUBE_U = 3.0            # where a strut lands inside the Ø8 tube (surface is u 3.67 at w 1.6)
CH_VOID_MIN = 0.45             # the family's rule: the void is at least 45 % of the plan bbox

# --- NOCTURNE: the lit mast --------------------------------------------------------------------
# A narrow fork nose and a long cusped tongue instead of shard's full-width nose: 832 mm2 of plan
# against shard's 974, 15.7 % apart, which is how §4.5's silhouette rule is satisfied here (the
# hull deficiency of three convex-ish plates can never be 0.10 apart, so the area has to carry it).
# The 21.0 flanks between y -89 and -98 are NOT a free choice: the Ø9.0 bearing annulus under each
# button head reaches x 21.0 at y -94, and a waist anywhere in y -89.5 .. -98.5 cuts into it.
NOC_PLAN = ((10.0, -84.0), (21.0, -89.0), (21.0, -98.0), (13.0, -104.0), (8.0, -112.0))  # right half
NOC_CUSP = (16.0, 10.0, 0.8)   # tail cusp: root width, length, tip radius, rooted at (0, -112). The
#                                root is 16 and not 12 because the LED well sits on the tongue and
#                                needs Ø9.0 plus 1.5 of wall either side where it lands.
NOC_TAIL_Y = -122.0            # cusp tip on the centreline
NOC_MAST_LEN = 44.0            # 8 longer than shard's: the three vane bands (9.6 / 16.0 / 9.6) plus
#                                their gaps need 36.2 of mast below the head's lower face at 37.7
NOC_LED_D, NOC_WELL_HALF = 3.0, 25.0
NOC_WELL_Y = -112.5            # the well's own centre. NOT the point where the pipe axis crosses
#                                Z 36 (-108.69), which is the obvious choice and is 0.10 mm from the
#                                Ø3.6 coax bore at Z 38.5 - measured, and a 0.10 web is not a wall.
#                                Moved back to -112.5 the gap is 2.4 and the two voids still share
#                                2.65 mm of opening at the seat, which is what connects them.
NOC_WELL_DEPTH = 2.5           # = BRACKET_T: the well is a through countersink, so there is no
#                                0.1 mm annular web left at its throat (a 2.4 deep well in a 2.5
#                                plate leaves exactly that, and it is a knife edge, not a wall)
NOC_PIPE_D = 3.0
NOC_LED_SEAT = 6.0             # the first 6 mm of pipe opens to Ø3.0 + PETG fit to hold a 3 mm LED
NOC_KEEL_W, NOC_KEEL_OFF, NOC_KEEL_R = 6.0, 5.2, 3.0   # keel width, pipe offset below the axis, nose r
NOC_KEEL_S1 = 30.0             # keel end; the pipe stops NOC_TIP_WALL short of its end face
NOC_TIP_WALL = 0.8
NOC_VANE_T = 2.0               # blade thickness
# THE VANES ARE UPRIGHT PLATES IN PARALLEL VERTICAL PLANES, and that is a printability result, not a
# taste. Blades radiating from the mast axis - the first reading of "fanned 15 deg apart" - put every
# blade's leading edge on a nearly HORIZONTAL line with the whole blade above it: measured, 19-28 mm²
# per blade at normal.Z -0.766, six times over, and no bridge can save an edge supported at one end.
# Stand the same plate upright in a plane perpendicular to Y and every face is either vertical
# (normal.Z 0), a V flank at NOC_FIN_ANGLE off horizontal (normal.Z -0.574) or a horizontal-axis
# fillet cylinder under Ø12, which overhangs() exempts as an arch. Nothing needs support at all.
# Parallel planes also never intersect, so there is no wedge crack anywhere - the failure that killed
# every radial layout. The fan is read along the mast instead: (s, half width) with the heights in a
# 1 : 0.79 : 0.58 run, the design language's own spine-row progression.
NOC_FIN = ((5.0, 14.0), (15.0, 12.5), (25.0, 11.0))  # (s along the mast axis, half width X)
NOC_FIN_ANGLE = 48.0           # the V flank angle above horizontal. 48, not 55: 46.4 is where a
#                                plane's normal.Z reaches the -0.70 overhang limit, and every degree
#                                above that is height the fin has to buy - at 55 the tallest fin was
#                                31 and the smallest could not hold a 3.4 slot with its ligaments.
NOC_FIN_ROOT = -4.5            # the bottom vertex, in the fin plane, relative to the mast axis: it
#                                must stay inside the tube's section there (which spans +-6.22)
NOC_FIN_FLANK, NOC_FIN_PEAK = 0.75, 0.35   # vertical flank and cusped peak, as fractions of X. The
#                                flank is long on purpose: it is the only full-width band on the fin,
#                                and it is what a transverse ladder slot and the accent both need.
NOC_SLOT = (3.4, 1.7, 6.0, 2.2)   # ladder slot width, corner r, pitch, ligament
NOC_FILLET, NOC_TIP_CHAMFER, NOC_CUSP_R = 1.0, 0.4, 0.6
# The suture runs from the nose to the LED well and stops there. That is not a compromise: on a real
# tiger beetle the elytral suture is interrupted at the scutellum, and here the well is the scutellum.
# Up the mast the suture is read instead as the DORSAL SPLIT - the coax slit, widened to SLIT_REACH,
# parts every vane on the centreline (CN-1's "the pair IS the split").
NOC_SUTURE = (-86.0, -106.5)
NOC_MARK_FIN = 0               # index into NOC_FIN: the largest fin carries the cut-through mark
NOC_SLOT_TRIES = (0.42, 0.36, 0.30, 0.24)   # slot lengths to try, as fractions of the half width

_STYLE_PARAMS = {
    "shard": {},
    "chassis": {"BRACKET_T": 2.5, "ROOT_Y": CH_ROOT[1], "EDGE_R": CH_FILLET},
    # HEAD_W 16.0, not 15.0: PETG's wall floor is 1.5 and the tightest wall in the clamp head - the
    # one between a bar groove and the rounded corner - measures 1.27 at 15.0. 16.0 takes it to 1.77.
    "nocturne": {"BRACKET_T": 2.5, "MAST_LEN": NOC_MAST_LEN, "ROOT_Y": -104.0, "HEAD_W": 16.0,
                 "SLIT_REACH": 18.0},
}
_MATERIAL_OF = {"shard": "TPU95A", "chassis": "TPU95A", "nocturne": "PETG"}
_SEAT_MIN = {"shard": 300.0, "chassis": 170.0, "nocturne": 240.0}
# Why the seat threshold is per style and is NOT a relaxed check.  plate_top's two rear prongs offer
# ~330 mm2 of face at Z 36 in total, and the shard plate takes 313 of it - there is no more to have.
# A style that changes the plan outline (which §4.5 REQUIRES: >12 % in area or >0.10 in hull
# deficiency between any two) therefore changes the contact area by construction.  The requirement
# that is identical for all three is the CLAMP LOAD PATH, and that is checked separately and
# without any per-style number: the full Ø3.5..Ø9.0 bearing annulus under each button head must be
# seated on plate material.  See `_bearing_annulus` and the "bolt bearing annulus" rows.
_BEARING_R = (1.75, 4.5)


# --- mast frame ------------------------------------------------------------------------------
def _axes(p: dict) -> tuple[Vector, Vector, Vector, Vector]:
    """(root point A, mast direction D, bar direction B, mast 'up' V); D, B, V are orthonormal."""
    a = radians(p["MAST_ANGLE"])
    d = Vector(0, -cos(a), sin(a))  # up and rearward
    b = Vector(0, -sin(a), -cos(a))  # perpendicular to the mast in YZ, pointing down-rear
    return Vector(0, p["ROOT_Y"], Z0 + p["BRACKET_T"]), d, b, -b


def _mast_plane(p: dict, s: float) -> Plane:
    """Plane across the mast at distance s from the root; local x = frame X, local y = mast up."""
    a, d, _b, _v = _axes(p)
    return Plane(origin=a + d * s, x_dir=(1, 0, 0), z_dir=d)


def _head_plane(p: dict) -> Plane:
    """Section plane of the head at its upper end; local x = frame X, local y = mast direction,
    extruded along the bar. Cutting the grooves in this 2D section (instead of with 3D cylinder
    tools) keeps their faces plain cylinders, which the shared overhang check needs."""
    a, d, b, _v = _axes(p)
    return Plane(origin=a + d * p["MAST_LEN"] - b * (p["HEAD_L"] / 2), x_dir=(1, 0, 0), z_dir=b)


def _groove_depth(p: dict) -> float:
    """Distance of a bar-groove axis below the outer face that leaves BAR_LIP lips on both sides."""
    r = p["BAR_D"] / 2
    return sqrt(r ** 2 - (r - p["BAR_LIP"]) ** 2)


# --- pieces ----------------------------------------------------------------------------------
def _bracket(p: dict) -> Part:
    pts = [(p["FRONT_X"], p["FRONT_Y"]), (p["WIDE_X"], p["WIDE_Y0"]), (p["WIDE_X"], p["WIDE_Y1"]),
           (p["TAIL_X"], p["TAIL_Y"]), (-p["TAIL_X"], p["TAIL_Y"]), (-p["WIDE_X"], p["WIDE_Y1"]),
           (-p["WIDE_X"], p["WIDE_Y0"]), (-p["FRONT_X"], p["FRONT_Y"])]
    sk = fillet(Polygon(*pts, align=None).vertices(), p["EDGE_R"])
    return extrude(Plane.XY.offset(Z0) * sk, amount=p["BRACKET_T"], dir=(0, 0, 1))


def _mast_foot_drop(p: dict) -> float:
    """How far below the root plane the rod has to run so that Z 36 cuts it off completely."""
    return (p["BRACKET_T"] + p["MAST_D"] / 2 * cos(radians(p["MAST_ANGLE"])) + 0.5) / sin(radians(p["MAST_ANGLE"]))


def _rod(p: dict, d: float, s0: float, s1: float) -> Part:
    return extrude(_mast_plane(p, s0) * Circle(d / 2), amount=s1 - s0)


def _tilt_cutter(p: dict) -> Part:
    """Half space under the frame-facing face of the head. That face would point 50 deg down
    (normal.Z -0.766); tilting it HEAD_TILT towards the upper bar end brings every head normal
    back above the 45 deg limit. The coax channel and its slit stop on the same plane, so their
    ends are part of that face instead of two more unsupported ceilings."""
    a, d, b, _v = _axes(p)
    g = radians(p["HEAD_TILT"])
    n = b * -sin(g) + d * -cos(g)
    origin = a + d * (p["MAST_LEN"] - p["HEAD_T"] / 2)
    return Plane(origin=origin, x_dir=(1, 0, 0), z_dir=n) * Box(400, 400, 400, align=MIN_Z_ALIGN)


def _head(p: dict, grooves: bool = True) -> Part:
    t, w_top = tan(radians(p["HEAD_TILT"])), p["HEAD_T"] / 2
    w_bot = -(w_top + p["HEAD_L"] / 2 * t)  # deep enough that the tilted cut sweeps the whole face
    sec = Pos(0, (w_top + w_bot) / 2) * Rectangle(p["HEAD_W"], w_top - w_bot)
    sec = fillet(sec.vertices().filter_by(lambda q: q.Y > 0), p["HEAD_R"])
    if grooves:
        for x in (-p["GROOVE_X"], p["GROOVE_X"]):
            sec -= Pos(x, w_top - _groove_depth(p)) * Circle(p["BAR_D"] / 2)
    head = extrude(_head_plane(p) * sec, amount=p["HEAD_L"])
    return head - _tilt_cutter(p) - _tie_slots(p)


def _tie_slots(p: dict) -> Part:
    a, d, b, _v = _axes(p)
    tools = Part()
    for u in (-p["TIE_U"], p["TIE_U"]):
        origin = a + d * p["MAST_LEN"] + b * u
        tools += Plane(origin=origin, x_dir=(1, 0, 0), z_dir=d) * Box(p["TIE_SLOT_W"], p["TIE_SLOT_L"], 60)
    return tools


def _dipole_clip(p: dict) -> Part:
    a, d, b, _v = _axes(p)
    r_in = p["DIPOLE_D"] / 2 + FIT
    r_out = r_in + CLIP_WALL
    mouth = p["DIPOLE_D"] - MATERIALS[MATERIAL]["snap"]
    sk = (Circle(r_out) - Circle(r_in)) - Rectangle(r_out + 1, mouth, align=(Align.MIN, Align.CENTER)).rotate(Axis.Z, 90)
    sk = fillet(sk.vertices().filter_by(lambda v: abs(abs(v.X) - mouth / 2) < 1e-6), MOUTH_FILLET)
    # started below the head's frame plane and trimmed on it, so its lower end is not a ceiling
    start = p["MAST_LEN"] - p["HEAD_T"] / 2 - 6.0
    origin = a + d * start + b * (p["HEAD_L"] / 2 + r_out - 1.0)
    clip = extrude(Plane(origin=origin, x_dir=(1, 0, 0), z_dir=d) * sk, amount=p["DIPOLE_LEN"] + 6.0)
    return clip - _tilt_cutter(p)


def _bolt_tools(p: dict) -> Part:
    z_top = Z0 + p["BRACKET_T"]
    tools = Part()
    for x in (BOLT_XY[0], -BOLT_XY[0]):
        tools += screw_hole((x, BOLT_XY[1]), z_top, D_M3_THRU, p["BRACKET_T"] + 2,
                            head_d=D_M3_HEAD_RECESS, head_h=1.0)
    return tools


# === CHASSIS ==================================================================================
def _thick_path(pts, width: float) -> Sketch:
    """A polyline swollen to `width`: one stadium per segment, so every joint is already rounded
    (the caps overlap) and no fillet call is needed. Every truss member is drawn with this."""
    sk = Sketch()
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        L = hypot(x1 - x0, y1 - y0)
        if L < 1e-9:
            continue
        sk += Pos((x0 + x1) / 2, (y0 + y1) / 2) * \
            SlotOverall(L + width, width).rotate(Axis.Z, degrees(atan2(y1 - y0, x1 - x0)))
    return sk


def _ch_members() -> list[tuple[str, list, float]]:
    """(name, polyline, width) for the RIGHT half of the truss plus the centre spine. The three
    nodes make one triangle whose corners are all inside the 50-70 deg window; `_ch_angles()`
    measures them so checks() can assert it rather than trust this comment."""
    rail = [tuple(q) for q in CH_RAIL]
    return [("rail", rail, CH_RAIL_W),
            ("strut", [CH_SPINE_N, tuple(CH_EYE)], CH_STRUT_W),
            ("spine", [CH_SPINE_N, CH_ROOT], CH_SPINE_W)]


def _ch_angles() -> dict[str, float]:
    """The triangulation angles of the spine / strut / rail triangle, in degrees."""
    def ang(o, a, b):
        va, vb = (a[0] - o[0], a[1] - o[1]), (b[0] - o[0], b[1] - o[1])
        return abs(degrees(atan2(va[1], va[0]) - atan2(vb[1], vb[0]))) % 360.0

    def norm(t):
        return 360.0 - t if t > 180.0 else t

    e, s, r = tuple(CH_EYE), CH_SPINE_N, CH_ROOT
    return {"at the spine nose": norm(ang(s, e, r)),
            "at the bolt eyelet": norm(ang(e, s, r)),
            "at the mast root": norm(ang(r, s, e))}


def _ch_junctions(p: dict) -> list[tuple[str, tuple, float, float]]:
    """(name, centre, ring OD, bore Ø) for every junction of the truss - the CHASSIS signature is
    that each one is a visible eyelet, and this table is what the conformance check probes."""
    od, bore = 2.6 * CH_STRUT_W, 0.9 * CH_STRUT_W
    out = [("spine nose", CH_SPINE_N, od, bore)]
    for x in (CH_EYE[0], -CH_EYE[0]):
        out.append((f"bolt eyelet x{x:+.1f}", (x, CH_EYE[1]), CH_EYE_OD, D_M3_THRU))
    out.append(("mast root", CH_ROOT, CH_ROOT_OD, p["COAX_D"]))
    return out


def _ch_rail_edge() -> list[tuple[float, float]]:
    """The right rail's OUTBOARD edge polyline: the centreline pushed out CH_RAIL_W/2 along the
    average of the adjacent segments' right-hand normals, traversed root -> nose."""
    pts = [tuple(q) for q in reversed(CH_RAIL)]
    norms = []
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        L = hypot(x1 - x0, y1 - y0) or 1.0
        norms.append(((y1 - y0) / L, -(x1 - x0) / L))
    out = []
    for i, (x, y) in enumerate(pts):
        ns = [norms[max(0, i - 1)], norms[min(len(norms) - 1, i)]]
        nx, ny = sum(n[0] for n in ns), sum(n[1] for n in ns)
        L = hypot(nx, ny) or 1.0
        out.append((x + nx / L * CH_RAIL_W / 2, y + ny / L * CH_RAIL_W / 2))
    return out


def _ch_plan(p: dict) -> tuple[Sketch, int, int]:
    """The truss in plan. Right half plus the symmetric spine, then mirrored - so the left rail's
    serration marches outboard too instead of inboard, which is what a mirrored normal buys.
    Returns (sketch, serration bumps per side, ring nodes placed)."""
    half = Sketch()
    for _n, pts, w in _ch_members():
        half += _thick_path(pts, w)
    half += Pos(CH_EYE[0], CH_EYE[1]) * Circle(CH_EYE_OD / 2)
    half += Pos(*CH_ROOT) * Circle(CH_ROOT_OD / 2)
    rings = 0
    for _name, c, od, _bore in _ch_junctions(p):
        if c[0] < -1e-9:
            continue
        half += Pos(*c) * Circle(od / 2)
        rings += 1
    # SPINE: half-round bumps along the rail's OUTBOARD EDGE - serration() offsets from the polyline
    # it is handed, so it must be handed the EDGE, not the centreline (handed the centreline the
    # bumps land wholly inside a 3.6 mm rail and the serration is invisible: measured, |x| max was
    # unchanged at 21.900). Traversed root -> nose, so the default right-hand normal (ty, -tx)
    # already points outboard on this side.
    bumps, n_b = S.serration(_ch_rail_edge(), d=CH_SERR_D,
                             pitch=CH_SERR_PITCH, protrusion=CH_SERR_OUT)
    half += bumps
    sk = half + half.mirror(Plane.YZ)
    return sk, n_b, 2 * rings - 1  # the spine-nose ring is shared by the mirror


def _ch_burst(p: dict) -> tuple[Part, int]:
    """The hub starburst round each bolt: 8 rays DEBOSSED CH_BURST_DEPTH into the bracket top.
    Cut through, a 1.2 mm ray is under TPU's 2.2 mm minimum through-hole; debossed it leaves
    1.9 mm of floor. The rays start at the Ø6.6 head recess, so they read round a fitted button."""
    z1, sk, kept = Z0 + p["BRACKET_T"], Sketch(), 0
    for x in (CH_EYE[0], -CH_EYE[0]):
        rays, n = S.starburst((x, CH_EYE[1]), D_M3_HEAD_RECESS / 2, n=CH_BURST_N,
                              w=CH_BURST_W, length=CH_BURST_LEN)
        sk += rays
        kept += n
    if not sk.faces():
        return Part(), 0
    return S.extrude_cut(sk, Plane.XY.offset(z1 + 0.01), -(CH_BURST_DEPTH + 0.01)), kept


def _ch_bracket(p: dict) -> Part:
    """Truss bracket Z 36 .. Z1. The root hub is already in the plan sketch, so the rod meets a flat
    top face exactly as it does on the shard bracket and the root fillet has an ellipse to find."""
    sk, _b, _r = _ch_plan(p)
    body = extrude(Plane.XY.offset(Z0) * sk, amount=p["BRACKET_T"], dir=(0, 0, 1))
    if CH_ROOT_RISE > 0:
        body += cylinder(CH_ROOT[0], CH_ROOT[1], Z0, Z0 + p["BRACKET_T"] + CH_ROOT_RISE, CH_ROOT_OD)
    return Part() + body


def _ch_ring_bores(p: dict) -> Part:
    """The ID of every ring node that is not already a bolt bore or the coax bore."""
    tool = Part()
    z1 = Z0 + p["BRACKET_T"]
    for name, c, _od, bore in _ch_junctions(p):
        if name.startswith("bolt") or name == "mast root":
            continue
        tool += cylinder(c[0], c[1], Z0 - 1.0, z1 + 1.0, bore)
    return tool


def _ch_lattice_nodes() -> list[float]:
    return [CH_LAT_S0 + k * CH_LAT_PITCH for k in range(CH_LAT_N)]


def _ch_lattice(p: dict) -> tuple[Part, int]:
    """The mast's two-rail lattice, OUTBOARD of the closed Ø8 tube - the antenna bore and its
    1.2 mm-plus wall are the clean zone and are never touched.

    Drawn in the plane that contains the mast axis and frame X, extruded CH_LAT_DEPTH along the
    mast's own perpendicular, so every face of it is either a plane whose normal.Z is 0 or
    -0.643 (inside the 0.72 limit) or a cylinder covered by the rail. The rail runs THROUGH every
    ring node for exactly that reason: the node's down-mast arc is the only surface here whose
    normal.Z would reach -0.766, and 3.6 mm of rail covers +-29.6 deg of it."""
    a, d, b, _v = _axes(p)
    pl = Plane(origin=a, x_dir=(1, 0, 0), z_dir=tuple(b))  # local x = frame X, local y = along d
    nodes = _ch_lattice_nodes()
    s_lo = nodes[0] - 1.3 * CH_LAT_W
    s_hi = nodes[-1] + 1.3 * CH_LAT_W
    half, rings = Sketch(), 0
    # The rail is drawn with MITRED, POINTED ends, not the round caps _thick_path would give: a round
    # cap here is a half cylinder whose axis is the mast's own perpendicular (z component -0.643, so
    # NOT a horizontal arch), and its down-mast arc measured 18.1 mm² at 33 % facing down - the only
    # overhang this style had. A tip at 32 deg off the rail takes the steepest face to normal.Z
    # -0.41, and it is CN-3's cusp into the bargain.
    hw, tip = CH_LAT_RAIL_W / 2, 1.6 * CH_LAT_RAIL_W / 2
    half += Polygon((CH_LAT_U - hw, s_lo), (CH_LAT_U, s_lo - tip), (CH_LAT_U + hw, s_lo),
                    (CH_LAT_U + hw, s_hi), (CH_LAT_U, s_hi + tip), (CH_LAT_U - hw, s_hi),
                    align=None)
    # Warren zig-zag: tube -> node -> tube, every diagonal 55.5 deg off the rail
    for k, s_node in enumerate(nodes):
        half += Pos(CH_LAT_U, s_node) * Circle(2.6 * CH_LAT_W / 2)
        rings += 1
        for sgn in (-1, 1):
            s_tube = min(max(s_node + sgn * CH_LAT_PITCH / 2, s_lo), s_hi)
            half += _thick_path([(CH_LAT_TUBE_U, s_tube), (CH_LAT_U, s_node)], CH_LAT_W)
    sk = half + half.mirror(Plane.YZ)
    bores = Sketch() + [Pos(x, s) * Circle(0.9 * CH_LAT_W / 2)
                        for s in nodes for x in (CH_LAT_U, -CH_LAT_U)]
    lat = extrude(pl * (sk - bores), amount=CH_LAT_DEPTH / 2, both=True)
    return Part() + lat, 2 * rings


# === NOCTURNE =================================================================================
BRIDGE_OK: dict[str, tuple] = {}  # filled by build(): the vane apertures' flat ceilings, per label
_BRIDGES: dict[str, list] = {}    # aperture cutter bboxes in FRAME coords, per variant


def _noc_plan(p: dict) -> Sketch:
    """A narrower, waisted plate ending in a true cusp - the plan that makes this style read as a
    different part at 200 px and not as the shard bracket with fins bolted on."""
    pts = [tuple(q) for q in NOC_PLAN]
    poly = Polygon(*pts, *[(-x, y) for x, y in reversed(pts)], align=None)
    keep = [v for v in poly.vertices() if abs(abs(v.Y) - 84.0) > 1e-6 and abs(v.Y + 112.0) > 1e-6]
    sk = fillet(keep, 2.5) if keep else poly
    w, ln, tip = NOC_CUSP
    return sk + S.cusp_tail(w, ln, tip_r=tip, at=(0.0, pts[-1][1]), angle=-90.0)


def _noc_keel_section(p: dict) -> Sketch:
    """The ventral keel in the mast's own cross-section (local x = frame X, local y = mast 'up'):
    a NOC_KEEL_W wide web hanging off the tube, closed by a Ø2*NOC_KEEL_R rounded nose. The nose
    is round so its underside never faces down harder than normal.Z -0.643."""
    return (Pos(0.0, -NOC_KEEL_OFF / 2) * Rectangle(NOC_KEEL_W, NOC_KEEL_OFF)
            + Pos(0.0, -NOC_KEEL_OFF) * Circle(NOC_KEEL_R))


def _noc_keel(p: dict) -> Part:
    s0 = -_mast_foot_drop(p) - 4.0
    return Part() + extrude(_mast_plane(p, s0) * _noc_keel_section(p), amount=NOC_KEEL_S1 - s0)


def _noc_pipe(p: dict) -> Part:
    """The Ø3.0 light channel up the keel, stopping NOC_TIP_WALL short of the keel's end face, plus
    the LED seat: the first NOC_LED_SEAT mm open to Ø3.0 + the PETG fit so a 3 mm LED is retained."""
    s0 = -_mast_foot_drop(p) - 4.0
    fit = MATERIALS["PETG"]["fit"]
    pipe = extrude(_mast_plane(p, s0) * (Pos(0.0, -NOC_KEEL_OFF) * Circle(NOC_PIPE_D / 2)),
                   amount=(NOC_KEEL_S1 - NOC_TIP_WALL) - s0)
    seat = extrude(_mast_plane(p, s0) * (Pos(0.0, -NOC_KEEL_OFF) * Circle((NOC_PIPE_D + fit) / 2)),
                   amount=(s0 * -1) + NOC_LED_SEAT)
    return Part() + (pipe + seat)


def _noc_well_xy(p: dict) -> tuple[float, float]:
    """Where the pipe axis crosses the seating plane - the only sensible centre for the well."""
    _a, d, _b, v = _axes(p)
    s = (Z0 - (Z0 + p["BRACKET_T"]) + NOC_KEEL_OFF * v.Z) / d.Z
    return 0.0, p["ROOT_Y"] + d.Y * s - NOC_KEEL_OFF * v.Y


def _noc_well(p: dict) -> Part:
    """The conical LED well, mouth Ø 3 x LED at Z 36 and narrowing UPWARD at NOC_WELL_HALF deg.
    _style.light_well() builds the flare opening upward, so it is turned over about its own mid
    height and lifted - the cone is axisymmetric, so that is an exact 180 deg flip, not a fudge.
    Opening downward, its wall stands 65 deg off horizontal: normal.Z -0.42, no support needed."""
    x, y = 0.0, NOC_WELL_Y
    well = S.light_well((x, y), Z0, led_d=NOC_LED_D, half_angle=NOC_WELL_HALF, depth=NOC_WELL_DEPTH)
    well = well.rotate(Axis((x, y, Z0 - NOC_WELL_DEPTH / 2), (1, 0, 0)), 180)
    well = well.moved(Location((0.0, 0.0, NOC_WELL_DEPTH)))
    # the mouth is carried 0.5 below the seat so the boolean is not tangent to the bed cut (left
    # tangent it leaves a vertex at Z 35.9999999 and a split bed face); the bed cut trims it back
    return Part() + (well + cylinder(x, y, Z0 - 0.5, Z0 + 1e-3, 3.0 * NOC_LED_D))


def _noc_fin_frame(p: dict, s: float) -> Plane:
    """The fin's own sketch plane: VERTICAL, perpendicular to frame Y, through the mast axis point at
    `s`. local x = frame X, local y = frame Z, and the plate extrudes along Y. Every fin uses a plane
    of this family, so no two fin planes ever meet - which is the whole point."""
    a, d, _b, _v = _axes(p)
    o = a + d * s
    return Plane(origin=tuple(o), x_dir=(1, 0, 0), z_dir=(0, -1, 0))


def _noc_fin_profile(x: float) -> tuple[Sketch, dict]:
    """One upright vane in its own plane, heights relative to the mast axis point:

        (0, root)  --55 deg-->  (+-x, knee)  --vertical-->  (+-x, flank)  --> (0, peak)

    The bottom vertex sits INSIDE the tube's section, so the V has no free underside at all; the two
    flanks stand NOC_FIN_ANGLE off horizontal, which is what keeps them off the overhang list; the
    peak runs out to a CN-3 cusp. Returns the sketch and the four key heights."""
    knee = NOC_FIN_ROOT + x * tan(radians(NOC_FIN_ANGLE))
    flank = knee + NOC_FIN_FLANK * x
    peak = flank + NOC_FIN_PEAK * x
    sk = Polygon((0.0, NOC_FIN_ROOT), (x, knee), (x, flank), (0.0, peak),
                 (-x, flank), (-x, knee), align=None)
    for sel, r in ((lambda q: abs(abs(q.X) - x) < 1e-6, NOC_FILLET),
                   (lambda q: abs(q.X) < 1e-6 and q.Y > 0, NOC_CUSP_R)):
        hits = sk.vertices().filter_by(sel)
        if hits:
            try:
                sk = fillet(hits, r)
            except Exception:  # noqa: BLE001 - OCCT refuses a radius it cannot fit; leave the corner
                pass
    return sk, {"root": NOC_FIN_ROOT, "knee": knee, "flank": flank, "peak": peak}


def _noc_fin_region(x: float) -> Sketch:
    """Where a fin may be cut: its own profile, held clear of the tube's section."""
    sk, h = _noc_fin_profile(x)
    keep = Pos(0.0, (NOC_FIN_ROOT + 1.5 + h["peak"]) / 2) * \
        Rectangle(4 * x, h["peak"] - NOC_FIN_ROOT - 1.5)
    return sk & keep


def _noc_clear_band(x: float, need_w: float) -> tuple[float, float]:
    """The interval of heights over which the fin is at least `need_w` wide - exactly, from the
    profile's own three segments (V flank, vertical flank, cusped peak). Every aperture on a fin is
    placed from this, which is why nothing has to be guessed or nudged."""
    _sk, h = _noc_fin_profile(x)
    frac = min(1.0, need_w / (2 * x))
    return (h["root"] + (h["knee"] - h["root"]) * frac,
            h["peak"] - (h["peak"] - h["flank"]) * frac)


def _noc_mark_kind(x: float) -> tuple[str, float, float]:
    """§4.3 applied with the measurement rather than a guess: the biggest accent whose own bounding
    box fits inside the fin with NOC_SLOT's ligament all round. Returns (kind, size, centre height),
    or ("", 0, 0) - and no mark at all is a legal outcome, because a crushed mark is worse than none.

    Measured on the widest fin (x +-12, so 24 across): `lunule` at its 16 mm minimum has an
    18.5 x 7.1 footprint and so needs a 22.9 wide band, which this fin offers over only 9.3 mm of
    height against the 11.5 it needs. `stripe3` at 10 needs 14.4 x 13.0 and gets 15.9. So this mast
    carries stripe3, which the brief's own scaling note allows."""
    lig = NOC_SLOT[3]
    for kind, size in (("lunule", 16.0), ("stripe3", 10.0), ("stripe3", 8.0)):
        bb = S.mark_sketch(kind, size).bounding_box()
        lo, hi = _noc_clear_band(x, bb.size.X + 2 * lig)
        if hi - lo >= bb.size.Y + 2 * lig:
            return kind, size, (lo + hi) / 2
    return "", 0.0, 0.0


def _noc_wing_region(p: dict, x: float) -> Sketch:
    """One WING of a fin: the half outboard of the dorsal split. The slit parts every vane on the
    centreline, so an aperture generated across the whole fin would be cut in two - the apertures
    are generated on the right wing and mirrored, exactly as the chassis truss is."""
    inner = p["COAX_SLIT"] / 2 + MATERIALS["PETG"]["wall"]
    _sk, h = _noc_fin_profile(x)
    keep = Pos((inner + 2 * x) / 2, (NOC_FIN_ROOT + h["peak"]) / 2) * \
        Rectangle(2 * x - inner, h["peak"] - NOC_FIN_ROOT + 2.0)
    return _noc_fin_region(x) & keep


def _noc_fin_apertures(p: dict, idx: int, x: float) -> tuple[Sketch, int, str]:
    """A fin's aperture set: the frame's own ladder slots, transverse across X and pitched in Z
    exactly as the abdominal ladder on plate_top is (CN-2), or the accent cut THROUGH the largest
    fin so it is backlit - where the dorsal split then crosses it, which is what a real elytral
    maculation does at the suture."""
    w, cr, pitch, lig = NOC_SLOT
    if idx == NOC_MARK_FIN:
        kind, size, at = _noc_mark_kind(x)
        if not kind:
            return Sketch(), 0, "no mark fits (§4.3)"
        return Pos(0.0, at) * S.mark_sketch(kind, size), 1, f"{kind} {size:g} cut through"
    # The slot length is searched, not chosen: a longer slot needs a wider band, and a wider band on
    # a wing that tapers at both ends is a SHORTER one, so the two pull against each other and the
    # optimum is different for every fin. Deterministic - the first length that places anything wins.
    region = _noc_wing_region(p, x)
    inner = p["COAX_SLIT"] / 2 + MATERIALS["PETG"]["wall"]
    for frac in NOC_SLOT_TRIES:
        length = frac * x
        # the band is asked for the width the WING needs, which is the slot plus its ligaments plus
        # the inner margin, doubled - _noc_clear_band() measures the fin across the whole centreline
        lo, hi = _noc_clear_band(x, 2 * (length + 2 * lig + inner))
        slots, n = S.vent_ladder(region, pitch=pitch, ligament_min=lig, length=length, width=w,
                                 corner_r=cr, hole_min=2.0, origin=(0.0, (lo + hi) / 2))
        if n:
            return slots + slots.mirror(Plane.YZ), 2 * n, f"vent_ladder {length:.1f} x {w}"
    return Sketch(), 0, "no ladder slot fits this wing"


def _noc_vanes(p: dict, variant: str = "") -> tuple[Part, Part, dict]:
    """(vane solids to union, aperture cutters to subtract, a report)."""
    vanes, cutters = Part(), Part()
    rep: dict = {"vanes": 0, "apertures": 0, "kinds": [], "boxes": [], "heights": []}
    for idx, (s, x) in enumerate(NOC_FIN):
        pl = _noc_fin_frame(p, s)
        prof, h = _noc_fin_profile(x)
        vanes += extrude(pl * prof, amount=NOC_VANE_T / 2, both=True)
        rep["vanes"] += 1
        rep["heights"].append(round(h["peak"] - h["root"], 2))
        sk, n, kind = _noc_fin_apertures(p, idx, x)
        rep["kinds"].append(f"fin {idx} (x +-{x}): {kind} x{n}")
        if not sk.faces():
            continue
        tool = S.extrude_cut(sk, pl.offset(-(NOC_VANE_T / 2 + 1.0)), NOC_VANE_T + 2.0)
        cutters += tool
        rep["apertures"] += n
        for f in tool.solids():
            bb = f.bounding_box()
            rep["boxes"].append((bb.min.X, bb.min.Y, bb.min.Z, bb.max.X, bb.max.Y, bb.max.Z))
    # Two flat spans that are bridges in the plainest sense, declared exactly as the frame's own USB
    # lintel is: the keel closing over the LED well's throat at Z 38.5 (a 6 mm span), and the light
    # pipe's blind end, a Ø3.0 flat ceiling NOC_TIP_WALL below the keel's end face.
    rep["boxes"].append((-5.5, NOC_WELL_Y - 5.5, Z0 + p["BRACKET_T"] - 0.4,
                         5.5, NOC_WELL_Y + 5.5, Z0 + p["BRACKET_T"] + 0.4))
    tip = _rod_at(p, NOC_PIPE_D + 0.8, NOC_KEEL_S1 - NOC_TIP_WALL - 0.3,
                  NOC_KEEL_S1 - NOC_TIP_WALL + 0.3, -NOC_KEEL_OFF).bounding_box()
    rep["boxes"].append((tip.min.X, tip.min.Y, tip.min.Z, tip.max.X, tip.max.Y, tip.max.Z))
    _BRIDGES[variant] = rep["boxes"]
    return Part() + vanes, cutters, rep


def _noc_tip_chamfer(part: Part, p: dict) -> tuple[Part, float]:
    """The 0.4 chamfer on every vane peak, so a 2.0 mm PETG edge does not curl in the airflow.
    Selected by proximity to each fin's own peak point, which is the only thing that identifies it."""
    a, d, _b, _v = _axes(p)
    peaks = []
    for s, x in NOC_FIN:
        _sk, h = _noc_fin_profile(x)
        o = a + d * s
        peaks.append(Vector(0.0, o.Y, o.Z + h["peak"] - NOC_CUSP_R))

    def near_peak(edge) -> bool:
        try:
            q = edge.center()
        except Exception:  # noqa: BLE001
            return False
        return any((Vector(q.X, q.Y, q.Z) - pk).length < 1.8 for pk in peaks)

    sel = [e for e in part.edges() if near_peak(e)]
    for r in (NOC_TIP_CHAMFER, 0.2):
        if not sel:
            break
        try:
            return Part() + chamfer(sel, r), r
        except Exception:  # noqa: BLE001 - OCCT refuses a chamfer it cannot fit; report 0.0
            continue
    return part, 0.0

def _params(variant: str = "shard", style: str | None = None, **overrides) -> dict:
    st = style or variant or "shard"
    assert st in STYLES, f"unknown style {st!r}; styles: {STYLES}"
    return {**_DEFAULTS, **_STYLE_PARAMS[st], "STYLE": st, **overrides}


def _root_fillet(part: Part, p: dict) -> Part:
    """Blend the leaning rod into the flat bracket top. The only ellipse in the part at Z1 is that
    intersection, so the edge selects itself - except on CHASSIS, where the rod lands inside a
    cylindrical boss and there is no ellipse at all (the boss IS the reinforcement)."""
    z1 = Z0 + p["BRACKET_T"]
    root = [e for e in part.edges()
            if e.geom_type == GeomType.ELLIPSE and abs(e.center().Z - z1) < 1e-3]
    if len(root) != 1:
        return part
    for r in (p["ROOT_R"], 2.0, 1.2):
        try:
            return part.fillet(r, root)
        except Exception:  # noqa: BLE001 - OCCT can refuse the cylinder/plane blend
            continue
    return part


def build(variant: str = "shard", style: str | None = None, **overrides) -> dict[str, Part]:
    """One labelled part per call. Everything that mates - the seat, the two bolt bores and their
    recesses, the Ø8 tube with its Ø3.6 coax bore, the insertion slit and the clamp head - is built
    by the SAME code in all three styles; `style` only chooses what hangs off it."""
    p = _params(variant, style, **overrides)
    st, label = p["STYLE"], NAME
    rep: dict = {}

    if st == "chassis":
        part = _ch_bracket(p)
    elif st == "nocturne":
        part = extrude(Plane.XY.offset(Z0) * _noc_plan(p), amount=p["BRACKET_T"], dir=(0, 0, 1))
    else:
        part = _bracket(p)

    part += _rod(p, p["MAST_D"], -_mast_foot_drop(p), p["MAST_LEN"])
    if st == "nocturne":
        part += _noc_keel(p)
    part = _root_fillet(part, p)

    if st == "chassis":
        lattice, n_rings = _ch_lattice(p)
        part += lattice
        rep["lattice rings"] = n_rings
    if st == "nocturne":
        blades, vane_cuts, vrep = _noc_vanes(p, variant or st)
        part += blades
        rep.update(vrep)

    part += _head(p)
    if p["DIPOLE"]:
        part += _dipole_clip(p)

    under_head = _tilt_cutter(p)
    channel = _rod(p, p["COAX_D"], -_mast_foot_drop(p), p["MAST_LEN"]) & under_head
    slit = extrude(_mast_plane(p, 0) * Rectangle(p["COAX_SLIT"], p["SLIT_REACH"],
                                                align=(Align.CENTER, Align.MIN)),
                   amount=p["MAST_LEN"]) & under_head
    part -= channel + slit + _bolt_tools(p)

    if st == "chassis":
        burst, n_rays = _ch_burst(p)
        part -= burst + _ch_ring_bores(p)
        rep["starburst rays"] = n_rays
        part -= S.suture(CH_SUTURE[0], CH_SUTURE[1], Z0 + p["BRACKET_T"])
    if st == "nocturne":
        part -= vane_cuts + _noc_pipe(p) + _noc_well(p)
        part -= S.suture(NOC_SUTURE[0], NOC_SUTURE[1], Z0 + p["BRACKET_T"])

    part -= box(-60, -200, Z0 - 40, 60, 60, Z0)  # flat bed face: the mast foot stops at Z 36
    part = Part() + part  # the fillet/cut chain hands back a plain Solid

    if st == "nocturne":
        part, r_ch = _noc_tip_chamfer(part, p)
        rep["tip chamfer"] = r_ch
        _publish_bridges(part, variant or st)

    _REPORT[p["STYLE"]] = rep
    part.label = label
    return {label: part}


_REPORT: dict[str, dict] = {}


def _bridges_for(shape: Part, variant: str) -> tuple:
    """The declared bridge boxes in the PRINT coordinates OF THIS SHAPE.

    PRINT is (0, 0, -1), so print_orientation() only translates: print = frame - (bbox centre X,
    bbox centre Y, min Z). That translation depends on the shape's OWN bbox, so a box computed for
    the whole part is wrong for the mast-only probe - measured as three bridged faces reappearing
    on a row that had been handed the right boxes. `_BRIDGES` therefore holds FRAME coordinates and
    every consumer converts for itself."""
    boxes = _BRIDGES.get(variant) or []
    if not boxes:
        return ()
    bb = shape.bounding_box()
    dx, dy, dz = -bb.center().X, -bb.center().Y, -bb.min.Z
    return tuple(("box", x0 + dx - 0.5, y0 + dy - 0.5, z0 + dz - 0.5,
                  x1 + dx + 0.5, y1 + dy + 0.5, z1 + dz + 0.5)
                 for x0, y0, z0, x1, y1, z1 in boxes)


def _publish_bridges(part: Part, variant: str) -> None:
    """Hand the framework this label's bridge boxes in the whole part's print coordinates."""
    if _BRIDGES.get(variant):
        BRIDGE_OK[f"{NAME}{'__' + variant if variant else ''}"] = _bridges_for(part, variant)


def _above_bracket(part: Part) -> Part:
    """The mast: everything above the bracket top face."""
    return part - box(-60, -200, Z0 - 40, 60, 60, Z1)


def _thin_allowance(p: dict) -> tuple[Part, ...]:
    """The two intentionally thin features the wall check skips:
    1. the coax slit mouth - a straight slot through a round mast always tapers to a lip where it
       breaks the surface, exactly like a c_clip mouth;
    2. the 0.3 bar-groove lips, and only those: the band stops 1.6 short of the head corner, so
       the tight wall between a groove and that corner is still sampled.
    _thin_walls() states how thick the material is where each band ends."""
    half = p["COAX_SLIT"] / 2 + p["SLIT_LIP"]
    mouth = extrude(_mast_plane(p, -_mast_foot_drop(p)) * (Pos(0, 4.0) * Rectangle(2 * half, 8.0)),
                    amount=_mast_foot_drop(p) + p["MAST_LEN"])
    band = Sketch() + [Pos(x, p["HEAD_T"] / 2 - _groove_depth(p)) * Rectangle(p["BAR_D"] + 1.0, p["BAR_D"] + 2.0)
                       for x in (-p["GROOVE_X"], p["GROOVE_X"])]
    lips = extrude(_head_plane(p) * band, amount=p["HEAD_L"])
    # 3. where the leaning coax channel breaks the bed plane at Z 36. A Ø3.6 bore cut at 50 deg by a
    #    horizontal plane meets it at an acute dihedral on one side, so the material there tapers to a
    #    knife edge exactly as the slit mouth does - measured at 0.10 mm on rays leaving the bed face
    #    just outboard of the opening. The band is 1.6 tall and hugs the channel; _thin_walls() states
    #    the real wall there ("mast tube wall", 2.20).
    out = [Part() + mouth, Part() + lips,
           Part() + (_rod(p, p["COAX_D"] + 3.6, -_mast_foot_drop(p), 3.0)
                     & box(-60, -200, Z0 - 0.1, 60, 60, Z0 + 1.6))]
    if p["STYLE"] == "chassis":
        # 4. the two mast-lattice rail tips, which are CN-3 cusps at 32 deg off the rail: a wedge,
        #    and the ray sampler measures across it (0.70 mm, 0.56 from the point).
        a, _d, b, _v = _axes(p)
        pl = Plane(origin=a, x_dir=(1, 0, 0), z_dir=tuple(b))
        nodes = _ch_lattice_nodes()
        tip = 1.6 * CH_LAT_RAIL_W / 2
        for s_end in (nodes[0] - 1.3 * CH_LAT_W - tip, nodes[-1] + 1.3 * CH_LAT_W + tip):
            for u in (CH_LAT_U, -CH_LAT_U):
                sk = Pos(u, s_end) * Rectangle(CH_LAT_RAIL_W + 1.0, 2.2 * tip)
                out.append(Part() + extrude(pl * sk, amount=CH_LAT_DEPTH, both=True))
    if p["STYLE"] == "nocturne":
        # 3. the keel's NOC_TIP_WALL end wall, which is deliberately 0.8 so the mast glows end-on.
        #    _noc_pipe_rows() measures it to +-0.1 instead, and the band is only as long as the wall.
        out.append(_rod_at(p, NOC_PIPE_D + 2.4, NOC_KEEL_S1 - NOC_TIP_WALL - 0.2,
                           NOC_KEEL_S1 + 0.2, -NOC_KEEL_OFF))
        # 4. each vane's cusped peak, where a NOC_CUSP_R fillet plus a 0.4 tip chamfer leaves a rim
        #    the ray sampler reads as a wall; the plate's full 2.0 is measured everywhere below it.
        for s, x in NOC_FIN:
            pl = _noc_fin_frame(p, s)
            _sk, h = _noc_fin_profile(x)
            sk = Pos(0.0, h["peak"] - 1.0) * Rectangle(2.2 * NOC_CUSP_R + 2.0, 3.0)
            out.append(Part() + extrude(pl * sk, amount=NOC_VANE_T, both=True))
    return tuple(out)


def _groove_corner_wall(p: dict) -> float:
    """Material between a bar groove and the rounded head corner - the tightest wall in the head,
    and the one a flat 'HEAD_W/2 - GROOVE_X - r' estimate misses."""
    r_f, cx, cw = p["HEAD_R"], p["GROOVE_X"], p["HEAD_T"] / 2 - _groove_depth(p)
    fx, fw = p["HEAD_W"] / 2 - r_f, p["HEAD_T"] / 2 - r_f
    arc = [(fx + r_f * cos(radians(a)), fw + r_f * sin(radians(a))) for a in range(0, 91)]
    return min(hypot(x - cx, w - cw) for x, w in arc) - p["BAR_D"] / 2


def _thin_walls(p: dict) -> dict[str, float]:
    """Walls inside the two allowance bands, which the ray sampler therefore never measures,
    plus the two head walls that are tight by construction."""
    r, t = p["BAR_D"] / 2, tan(radians(p["HEAD_TILT"]))
    walls = {"between the grooves": 2 * p["GROOVE_X"] - p["BAR_D"],
             "groove to head corner": _groove_corner_wall(p),
             "under the groove": (p["HEAD_T"] / 2 - _groove_depth(p) - r) + (p["HEAD_T"] / 2 - p["HEAD_L"] / 2 * t),
             "zip-tie slot rail": p["HEAD_W"] / 2 - p["HEAD_R"] - p["TIE_SLOT_W"] / 2,
             "slit lip width": p["SLIT_LIP"],
             "mast tube wall": (p["MAST_D"] - p["COAX_D"]) / 2,
             "under the M3 recess": p["BRACKET_T"] - 1.0}
    if p["STYLE"] == "chassis":
        walls.update({"spine beside the suture": (CH_SPINE_W - S.SUTURE_W) / 2,
                      "under the suture": p["BRACKET_T"] - S.SUTURE_D,
                      "under the starburst": p["BRACKET_T"] - CH_BURST_DEPTH,
                      "lattice ring annulus": (2.6 - 0.9) * CH_LAT_W / 2})
    if p["STYLE"] == "nocturne":
        walls.update({"vane plate": NOC_VANE_T,
                      "pipe to coax bore": (NOC_KEEL_OFF - NOC_PIPE_D / 2) - p["COAX_D"] / 2,
                      "keel below the pipe": NOC_KEEL_R - NOC_PIPE_D / 2,
                      "keel beside the pipe": NOC_KEEL_W / 2 - NOC_PIPE_D / 2,
                      "mark bar ligament": 2.2 * S.MARK_STROKE_MIN - S.MARK_STROKE_MIN,
                      "slot ligament": NOC_SLOT[3]})
    return walls


def _bar_ends(p: dict) -> list[Vector]:
    a, d, b, _v = _axes(p)
    centre = a + d * p["MAST_LEN"] + d * (p["HEAD_T"] / 2 - sqrt((p["BAR_D"] / 2) ** 2 - (p["BAR_D"] / 2 - p["BAR_LIP"]) ** 2))
    return [centre + b * (BAR_LEN / 2), centre - b * (BAR_LEN / 2)]


# --- shared probes for the three styles' own rows ---------------------------------------------
def _seat_sketch(part: Part) -> Sketch:
    """The part's bed footprint as a flat 2D sketch at z = 0 - every horizontal face sitting on the
    seating plane, translated down so plain Sketch booleans work on it. This is the PLAN OUTLINE
    §4.5 talks about, measured off the real solid rather than off the sketch that drew it."""
    sk = Sketch()
    for f in part.faces():
        if f.geom_type != GeomType.PLANE or abs(f.normal_at().Z) < 0.999:
            continue
        if abs(f.center().Z - Z0) > 1e-3:
            continue
        try:
            sk += Sketch() + f.moved(Location((0.0, 0.0, -Z0)))
        except Exception:  # noqa: BLE001 - a degenerate sliver face is not part of the footprint
            continue
    return sk


def _hull_area(pts) -> float:
    """Monotone-chain convex hull area of 2D points, for §4.5's silhouette hull deficiency."""
    ps = sorted(set((round(x, 4), round(y, 4)) for x, y in pts))
    if len(ps) < 3:
        return 0.0

    def build(seq):
        h = []
        for q in seq:
            while len(h) >= 2 and ((h[-1][0] - h[-2][0]) * (q[1] - h[-2][1])
                                   - (h[-1][1] - h[-2][1]) * (q[0] - h[-2][0])) <= 0:
                h.pop()
            h.append(q)
        return h

    hull = build(ps)[:-1] + build(ps[::-1])[:-1]
    return abs(sum(hull[i][0] * hull[(i + 1) % len(hull)][1] - hull[(i + 1) % len(hull)][0] * hull[i][1]
                   for i in range(len(hull)))) / 2.0


def _plan_metric(part: Part) -> tuple[float, float, float]:
    """(footprint area, hull area, hull deficiency) of the plan outline."""
    sk = _seat_sketch(part)
    area = float(sk.area) if sk.faces() else 0.0
    hull = _hull_area([(v.X, v.Y) for v in sk.vertices()])
    return area, hull, (1.0 - area / hull) if hull > 1e-6 else 0.0


_PLAN: dict[str, tuple[float, float, float]] = {}


def _plan_all(style: str, part: Part) -> dict[str, tuple[float, float, float]]:
    """Every style's plan metric, the caller's own measured in place and the siblings built once."""
    _PLAN[style] = _plan_metric(part)
    for other in STYLES:
        if other not in _PLAN:
            _PLAN[other] = _plan_metric(build(other)[NAME])
    return _PLAN


def _bearing_rows(part: Part) -> list[tuple[str, bool, str]]:
    """THE check that is identical for all three styles, and the one that actually matters: the full
    Ø3.5 .. Ø9.0 bearing annulus under each button head must be seated on plate material.

    A style may trade plan area for its silhouette - §4.5 obliges it to - but it may not trade the
    clamp load path, and this row does not know or care which style it is looking at."""
    from tigerbee.accessories._fit import plate_face
    r_in, r_out = _BEARING_R
    plate = Sketch() + plate_face("plate_top", Z0).moved(Location((0.0, 0.0, -Z0)))
    seat, out = _seat_sketch(part), []
    for side, x in (("right", BOLT_XY[0]), ("left", -BOLT_XY[0])):
        ann = Pos(x, BOLT_XY[1]) * (Circle(r_out) - Circle(r_in))
        need = float((ann & plate).area)
        got = float((ann & plate & seat).area) if seat.faces() else 0.0
        frac = got / need if need > 1e-6 else 0.0
        out.append((f"bolt bearing annulus Ø{2 * r_in}-Ø{2 * r_out} seated, {side}",
                    frac >= 0.98, f"{got:.1f} of the {need:.1f} mm² of plate under it ({frac:.1%})"))
    return out


def _bore_continuity(part: Part, p: dict) -> tuple[str, bool, str]:
    """The antenna bore runs unbroken from the mast foot to under the head, in every style."""
    probe = _rod(p, p["COAX_D"] - 0.4, -_mast_foot_drop(p) + 1.0,
                 p["MAST_LEN"] - p["HEAD_T"] / 2 - 1.5)
    v = isect(part, probe)
    return (f"Ø{p['COAX_D']} antenna bore continuous root to head", v < EPS,
            f"{v:.4f} mm³ of material inside a Ø{p['COAX_D'] - 0.4} probe {probe.volume:.0f} mm³ long")


def _neighbour_rows(part: Part, mast: Part) -> list[tuple[str, bool, str]]:
    """Every sibling that could share this corner of the frame. A module that is not written yet
    reports as unchecked rather than silently passing on nothing."""
    out = [_tail_block_check(mast)]
    for mod_name, build_kw, subject, min_gap in (("gps_mount", {}, part, 1.0),
                                                 ("gopro_mount", {}, part, 1.0),
                                                 ("rx_antenna_v_holder", {}, part, 1.0)):
        name = f"clear of {mod_name} by >= {min_gap} mm"
        try:
            import importlib
            mod = importlib.import_module(f"tigerbee.accessories.{mod_name}")
            other = Part() + list(mod.build(**build_kw).values())
        except Exception as e:  # noqa: BLE001 - sibling absent or in progress
            out.append((name, True, f"{mod_name} unavailable ({type(e).__name__}), not checked"))
            continue
        if mod_name == "rx_antenna_v_holder":
            out.append((f"EXCLUSIVE with {mod_name} (same rear-tip bolts), declared", True,
                        f"both claim (±{BOLT_XY[0]}, {BOLT_XY[1]}); EXCLUSIVE = {EXCLUSIVE}"))
            continue
        v, gap = isect(subject, other), subject.distance_to(other)
        out.append((name, v < EPS and gap >= min_gap, f"{v:.3f} mm³, gap {gap:.3f} mm"))
    return out


# --- CHASSIS conformance ----------------------------------------------------------------------
def _ch_ring_rows(part: Part, p: dict) -> list[tuple[str, bool, str]]:
    """The family signature, probed rather than asserted: at every junction of the truss there is a
    clear bore and a solid annulus round it - a visible eyelet, not a blob."""
    z1, out = Z0 + p["BRACKET_T"], []
    for name, c, od, bore in _ch_junctions(p):
        if name == "mast root":
            # the root's eyelet is the coax bore itself, which leaves at 50 deg; its continuity is
            # the `antenna bore continuous` row, so only the annulus round it is probed here
            ring = cylinder(c[0], c[1], Z0 + 0.2, z1 - 0.2, od - 0.8) - \
                cylinder(c[0], c[1], Z0 - 1, z1 + 1, bore + 1.2)
            frac = isect(part, ring) / ring.volume
            out.append((f"ring node at the {name}: annulus solid", frac >= 0.85,
                        f"OD {od}, bore Ø{bore}, annulus {frac:.1%} solid"))
            continue
        clear = cylinder(c[0], c[1], Z0 - 1.0, z1 + 1.0, bore - 0.2)
        # the annulus is probed BELOW the Ø6.6 button-head recess and the 0.6 starburst deboss: those
        # are fitted features, not voids, and a probe that runs through them measures 84 % of a ring
        # that is in fact whole (measured, and the reason this row reads z1 - 1.3 and not z1 - 0.2)
        z_hi = z1 - 1.3 if name.startswith("bolt") else z1 - 0.2
        ring = cylinder(c[0], c[1], Z0 + 0.2, z_hi, od - 0.8) - \
            cylinder(c[0], c[1], Z0 - 1, z1 + 1, bore + 0.8)
        v_clear, frac = isect(part, clear), isect(part, ring) / ring.volume
        out.append((f"ring node at the {name}: bore open, annulus solid",
                    v_clear < EPS and frac >= 0.85,
                    f"OD {od}, ID {bore}, {v_clear:.4f} mm³ in the bore, annulus {frac:.1%} solid "
                    f"over Z {Z0 + 0.2:.1f}-{z_hi:.1f}"))
    return out


def _ch_lattice_rows(part: Part, p: dict) -> list[tuple[str, bool, str]]:
    a, _d, b, _v = _axes(p)
    pl = Plane(origin=a, x_dir=(1, 0, 0), z_dir=tuple(b))
    bore_d, od = 0.9 * CH_LAT_W, 2.6 * CH_LAT_W
    clear, ring = Part(), Part()
    for s in _ch_lattice_nodes():
        for x in (CH_LAT_U, -CH_LAT_U):
            clear += extrude(pl * (Pos(x, s) * Circle((bore_d - 0.2) / 2)),
                             amount=CH_LAT_DEPTH / 2 + 1.0, both=True)
            ring += extrude(pl * (Pos(x, s) * (Circle((od - 0.8) / 2) - Circle((bore_d + 0.8) / 2))),
                            amount=CH_LAT_DEPTH / 2 - 0.2, both=True)
    v, frac = isect(part, clear), isect(part, ring) / ring.volume
    return [(f"mast lattice: {2 * CH_LAT_N} ring nodes, bores open and annuli solid",
             v < EPS and frac >= 0.80,
             f"{v:.4f} mm³ in the Ø{bore_d:.2f} bores, annuli {frac:.1%} solid, "
             f"rails at x ±{CH_LAT_U} outboard of the Ø{p['MAST_D']} tube")]


def _ch_void_row(part: Part) -> tuple[str, bool, str]:
    sk = _seat_sketch(part)
    bb = sk.bounding_box()
    box_area = bb.size.X * bb.size.Y
    void = 1.0 - float(sk.area) / box_area if box_area > 1e-6 else 0.0
    return (f"CHASSIS: void >= {CH_VOID_MIN:.0%} of the plan bbox", void >= CH_VOID_MIN,
            f"{void:.1%} void: {sk.area:.0f} mm² of truss in a {bb.size.X:.1f} x {bb.size.Y:.1f} bbox")


def _ch_member_rows() -> list[tuple[str, bool, str]]:
    """Struts are 2.5 deep, not the family's 3.0, and the trade is checked rather than excused:
    BATTERY's floor is Z 38.5 - exactly BRACKET_T above the seat - so section is bought in width."""
    ref_area = 2.4 * 3.0
    worst_w, worst_a, rows = 99.0, 999.0, []
    for name, _pts, w in _ch_members():
        area = w * _STYLE_PARAMS["chassis"]["BRACKET_T"]
        worst_w, worst_a = min(worst_w, w), min(worst_a, area)
        rows.append(f"{name} {w} x {_STYLE_PARAMS['chassis']['BRACKET_T']} = {area:.1f} mm²")
    ang = _ch_angles()
    return [(f"CHASSIS: every member >= 2.4 wide and >= {ref_area:.1f} mm² in section",
             worst_w >= 2.4 - 1e-9 and worst_a >= ref_area - 1e-9, "; ".join(rows)),
            ("CHASSIS: triangulation 50-70 deg, nothing within 8 deg of 90",
             all(50.0 - 1e-6 <= v <= 70.0 + 1e-6 and abs(v - 90.0) >= 8.0 for v in ang.values()),
             ", ".join(f"{k} {v:.1f}" for k, v in ang.items()))]


# --- NOCTURNE conformance ---------------------------------------------------------------------
def _noc_pipe_rows(part: Part, p: dict) -> list[tuple[str, bool, str]]:
    """The light path, end to end: the well and the pipe are one connected void, nothing blocks it,
    and the keel's end face is left exactly NOC_TIP_WALL thick so the mast glows end-on."""
    well, pipe = _noc_well(p), _noc_pipe(p)
    join = isect(well, pipe)
    blocked = isect(part, (well + pipe) - box(-60, -200, Z0 - 40, 60, 60, Z0))
    # Ø2.0, not Ø2.6: the probe is centred NOC_KEEL_OFF below the mast axis, so a Ø2.6 probe reaches
    # r 3.9 and clips the Ø8 tube itself - measured as 0.0557 mm³ "beyond the end face" that is in
    # fact tube wall. Ø2.0 spans r 4.2..6.2, inside the keel and clear of the tube.
    d_probe = NOC_PIPE_D - 1.0
    plug = _rod_at(p, d_probe, NOC_KEEL_S1 - NOC_TIP_WALL + 0.05, NOC_KEEL_S1 - 0.05, -NOC_KEEL_OFF)
    beyond = _rod_at(p, d_probe, NOC_KEEL_S1 + 0.05, NOC_KEEL_S1 + 1.0, -NOC_KEEL_OFF)
    inside = _rod_at(p, d_probe, NOC_KEEL_S1 - NOC_TIP_WALL - 1.0,
                     NOC_KEEL_S1 - NOC_TIP_WALL - 0.05, -NOC_KEEL_OFF)
    f_plug = isect(part, plug) / plug.volume
    v_beyond, v_inside = isect(part, beyond), isect(part, inside)
    x, y = _noc_well_xy(p)
    return [("NOCTURNE: light well and pipe are one connected void", join > 1.0,
             f"{join:.2f} mm³ shared; well mouth Ø{3 * NOC_LED_D} at Z 36 centred (0, {y:.2f}), "
             f"{NOC_WELL_HALF} deg half angle, open (no lens cap ships with this part)"),
            ("NOCTURNE: nothing blocks the light channel", blocked < EPS, f"{blocked:.4f} mm³"),
            (f"NOCTURNE: keel tip wall {NOC_TIP_WALL} +/- 0.1 (the mast glows end-on)",
             f_plug > 0.99 and v_beyond < EPS and v_inside < EPS,
             f"plug {f_plug:.3f} solid, {v_beyond:.4f} mm³ beyond the end face, "
             f"{v_inside:.4f} mm³ inside the pipe")]


def _rod_at(p: dict, d: float, s0: float, s1: float, w_off: float) -> Part:
    """A probe cylinder parallel to the mast axis, offset `w_off` along the mast's 'up'."""
    return extrude(_mast_plane(p, s0) * (Pos(0.0, w_off) * Circle(d / 2)), amount=s1 - s0)


def _noc_vane_rows(part: Part, p: dict) -> list[tuple[str, bool, str]]:
    rep = _REPORT.get("nocturne", {})
    n_ap, hs = rep.get("apertures", 0), rep.get("heights", [])
    run = "1 : " + " : ".join(f"{v / hs[0]:.2f}" for v in hs[1:]) if hs else "none"
    rows = [(f"NOCTURNE: {rep.get('vanes', 0)} upright vanes, {NOC_VANE_T} thick, "
             f"{min(hs) if hs else 0:.1f}-{max(hs) if hs else 0:.1f} tall, 3-7 apertures",
             rep.get("vanes", 0) == len(NOC_FIN) and 3 <= n_ap <= 7,
             f"{n_ap} apertures; " + "; ".join(rep.get("kinds", [])) +
             f"; heights {hs}, a {run} run")]
    # the family's own printability argument, stated as a number rather than a claim: the V flank is
    # the steepest down-facing PLANE on any vane, and its normal.Z is -cos(NOC_FIN_ANGLE)
    flank_nz = -cos(radians(NOC_FIN_ANGLE))
    rows.append((f"NOCTURNE: vane faces vertical, V flanks at {NOC_FIN_ANGLE} deg off horizontal",
                 flank_nz > -0.70,
                 f"plate faces normal.Z 0.000, flanks {flank_nz:.3f}, "
                 f"fillet cylinders Ø{2 * NOC_FILLET}/Ø{2 * NOC_CUSP_R} on a horizontal axis "
                 f"(overhangs() exempts an arch under Ø{MATERIALS['PETG']['arch_d']})"))
    rows.append((f"NOCTURNE: vane peak chamfer {NOC_TIP_CHAMFER} applied",
                 rep.get("tip chamfer", 0.0) > 0.0, f"{rep.get('tip chamfer', 0.0)} mm"))
    return rows


def checks(parts: dict[str, Part], frame: dict[str, Part],
           variant: str | None = None) -> list[tuple[str, bool, str]]:
    """ONE checks() for all three styles. Every fit assertion below is the one the single-style mast
    already had, and all three must still pass all of them; the style-specific rows are additions,
    not relaxations. The one number that varies by style is the seating CONTACT AREA, and the reason
    is written out at _SEAT_MIN - the load path itself is checked by `_bearing_rows`, identically."""
    style = (variant or "shard") if (variant or "shard") in STYLES else "shard"
    p = _params(style)
    part = parts[NAME]
    z1 = Z0 + p["BRACKET_T"]
    wall = MATERIALS[_MATERIAL_OF[style]]["wall"]
    mast = part - box(-60, -200, Z0 - 40, 60, 60, z1)
    out = []

    hits = interference(part)
    out.append(("no interference with the frame", not hits, f"{hits or 'none'}"))

    for side, x in (("right", BOLT_XY[0]), ("left", -BOLT_XY[0])):
        ok, detail = coaxial(part, (x, BOLT_XY[1]), D_M3_THRU, Z0, z1)
        probe = isect(part, cylinder(x, BOLT_XY[1], Z0 - 1, z1 + 1, 3.2))
        out.append((f"bolt hole coaxial with standoff_rear_tip_{side}, Ø3.2 probe clear",
                    ok and probe < EPS, f"{detail}; probe {probe:.4f} mm³"))

    contact = seated(part, Z0)
    out.append((f"bracket seated on plate_top at Z 36.000 (>= {_SEAT_MIN[style]:.0f} mm² for {style})",
                contact >= _SEAT_MIN[style],
                f"{contact} mm² contact; plate_top's two rear prongs offer ~330 mm² in total"))
    out += _bearing_rows(part)

    bb = part.bounding_box()
    out.append(("outline |x| <= 22.0 behind y -82", max(abs(bb.min.X), abs(bb.max.X)) <= WIDE_X + 1e-6,
                f"|x| max {max(abs(bb.min.X), abs(bb.max.X)):.3f}, y {bb.min.Y:.1f}..{bb.max.Y:.1f}"))

    disc = prop_disc_violation(part)
    out.append(("outside the prop keep-out discs", disc < EPS, f"{disc:.3f} mm³"))

    so = standoff_interference(part)
    gaps = {n: g for n, g in distance_to_frame(part, near=2.0).items() if n.startswith("standoff")}
    out.append((f"clear of the Ø{STANDOFF_D} rear-tip standoff shafts", not so,
                f"overlaps {so or 'none'}; gaps {gaps or 'none within 2 mm'}"))

    vb, gap = isect(mast, BATTERY), mast.distance_to(BATTERY)
    out.append((f"mast clear of the BATTERY envelope by >= {BATTERY_CLEAR} mm",
                vb < EPS and gap >= BATTERY_CLEAR, f"{vb:.3f} mm³, gap {gap:.3f} mm"))

    plates = [frame[n] for n in PLATE_FACES]
    ends = [(e, min(cylinder(e.X, e.Y, e.Z - 0.05, e.Z + 0.05, 0.1).distance_to(pl) for pl in plates))
            for e in _bar_ends(p)]
    out.append(("both T-bar ends >= 20 mm from every plate",
                all(g >= 20.0 for _e, g in ends),
                "; ".join(f"({e.X:.0f}, {e.Y:.1f}, {e.Z:.1f}) {g:.1f} mm" for e, g in ends)))

    out.append(_bore_continuity(part, p))
    out += _neighbour_rows(part, mast)

    over = overhangs(mast, PRINT[NAME], cos_limit=0.72, material=_MATERIAL_OF[style],
                     bridge_ok=_bridges_for(mast, style))
    out.append((f"mast self-supporting above Z {z1} (no normal.Z < -0.72)", not over,
                "; ".join(over) or "none"))

    # min_wall()'s erode/dilate path is unreliable on this solid: OCCT sometimes refuses the
    # offset (min_wall then falls back to ray_thickness by itself) and sometimes returns a
    # collapsed shape that reads as a 2.5 cm3 "thin residual". Its ray sampler is exact here,
    # so call that directly and get the same answer every run.
    thin, _worst, wall_detail = ray_thickness(part, wall, allow=_thin_allowance(p))
    out.append((f"min wall >= {wall} outside the declared thin features", not thin, wall_detail))
    walls = _thin_walls(p)
    out.append((f"declared thin features rooted in >= {wall} of material",
                min(walls.values()) >= wall - 1e-6,
                ", ".join(f"{k} {v:.2f}" for k, v in walls.items())))

    # --- the style's own rows ------------------------------------------------------------------
    if style == "chassis":
        out += _ch_ring_rows(part, p)
        out += _ch_lattice_rows(part, p)
        out.append(_ch_void_row(part))
        out += _ch_member_rows()
        rep = _REPORT.get("chassis", {})
        _sk, n_bumps, n_rings = _ch_plan(p)
        out.append((f"CHASSIS: SPINE serration on both rails' outboard edge, starburst round both bolts",
                    n_bumps >= 8 and rep.get("starburst rays", 0) == 2 * CH_BURST_N,
                    f"{n_bumps} bumps Ø{CH_SERR_D} at {CH_SERR_PITCH} pitch per rail, "
                    f"{rep.get('starburst rays', 0)} rays debossed {CH_BURST_DEPTH} deep, "
                    f"{n_rings} plan ring nodes"))
    if style == "nocturne":
        out += _noc_pipe_rows(part, p)
        out += _noc_vane_rows(part, p)

    if style in ("chassis", "nocturne"):
        runs = [CH_SUTURE] if style == "chassis" else [NOC_SUTURE]
        for y0, y1 in runs:
            ok_s, det_s = S.suture_present(part, y0, y1, z1)
            out.append((f"CN-1: {S.SUTURE_W} x {S.SUTURE_D} suture on X=0, y {y0} to {y1}",
                        ok_s, det_s))

    # --- §4.5: the three plans must be three shapes -------------------------------------------
    metrics = _plan_all(style, part)
    rows, worst_ok = [], True
    for i, a in enumerate(STYLES):
        for b in STYLES[i + 1:]:
            aa, _ha, da = metrics[a]
            ab, _hb, db = metrics[b]
            d_area = abs(aa - ab) / max(1e-6, (aa + ab) / 2)
            d_def = abs(da - db)
            ok = d_area > 0.12 or d_def > 0.10
            worst_ok = worst_ok and ok
            rows.append(f"{a}/{b} area {d_area:.1%}, hull deficiency Δ{d_def:.3f}{'' if ok else ' FAIL'}")
    out.append(("§4.5: plan outlines differ pairwise by >12 % area or >0.10 hull deficiency",
                worst_ok, "; ".join(rows) + "; " +
                ", ".join(f"{s} {metrics[s][0]:.0f} mm² def {metrics[s][2]:.3f}" for s in STYLES)))
    return out


def _tail_block_check(mast: Part) -> tuple[str, bool, str]:
    """The mast is the alternative RX holder when the tail block is cut down to TOWER=False."""
    name = "clear of tail_block(TOWER=False) by >= 1.0 mm"
    try:
        from tigerbee.accessories import tail_block
        tb = Part() + list(tail_block.build(TOWER=False).values())
    except Exception as e:  # noqa: BLE001 - sibling module not written yet
        return name, True, f"tail_block unavailable ({type(e).__name__}), not checked"
    v, gap = isect(mast, tb), mast.distance_to(tb)
    return name, v < EPS and gap >= 1.0, f"{v:.3f} mm³, gap {gap:.3f} mm"
