"""Three-segment composite side panels: a standoff-mounted ladder carcass plus swappable skins.

The user's own headline concept, and the ARRIS canopy reference read literally: a glossy shell that
stands PROUD of the frame, split along its length into three segments so a crash costs one 6 g skin
instead of a whole panel. The carcass is the only part that touches the frame; the skins slide on
from the rear over a dovetail defined ONCE in this file (`RAIL`) and used to generate both halves,
so they cannot drift apart.

    front   standoff_front_tip  -> standoff_front_arm     (77.76 mm of rail)
    centre  standoff_front_arm  -> standoff_rear_arm      (65.25 mm)
    tail    standoff_rear_arm   -> standoff_rear_tip      (61.38 mm)

Each segment is built in its OWN right-handed local frame - local x = `t` along the rail pointing
REARWARD, local y = `s` outward (away from the centreline), local z = frame Z - and placed with one
Location. Every Z number below is therefore a real frame Z, which is what makes the band arithmetic
(plate_mid top 9, plate_top underside 34) readable. The left side is the exact mirror of the right.

The three things that set every number in here, all measured:

  1. THE Z BAND. Everything lives in Z 9.25-33.75: 0.25 clear of the plate_mid top face and 0.25
     clear of the plate_top underside. Nothing else is in that band except the eight Ø6 standoffs,
     so the only interference this part can have with the frame is with a standoff - and the clips
     own those.
  2. THE REAR PROP DISC. The rear-tip standoff is 7.43 mm outside the rear prop keep-out (centre
     ±115.7212, -98.4367, r 91.9) and the tail axis line's CLOSEST approach to that circle is not at
     the tip but at y -83.0, where only 6.80 mm of outward room is left. That single number sets the
     tail's rail offset (4.75 instead of 6.55), its skin wall and its zero dome rise - see `SEGMENTS`
     and `RISE`.
  3. THE SIBLINGS ON THE SAME STANDOFFS. camera_pod owns front_tip Z 9.2-31.5, tail_block owns
     rear_tip Z 2-22, xt60_holder owns rear_arm Z 22-33.8. Every clip window here is chosen to miss
     them, which is why the six windows are not simply "the middle of the band".
"""

from copy import deepcopy
from math import atan2, cos, degrees, hypot, radians, sin, tan

from build123d import (Align, Axis, Circle, Cone, Location, Part, Plane, Polygon, Pos, Rectangle,
                       RegularPolygon, Sketch, SlotOverall, Sphere, Vector, extrude, fillet, offset)

from tigerbee.accessories import _blender as BL
from tigerbee.accessories._fit import _BARY
from tigerbee.accessories import _style as S
from tigerbee.accessories._common import *  # noqa: F401,F403 - constants, builders and checks

NAME = "side_panel_system"
TITLE = "Side panel system (3-segment carcass + skins)"
MATERIAL = "PETG"
# side_panels is the same volume done as one piece; xt60_holder wants rear_arm Z 22-33.8 AND the
# volume the centre skin occupies. Both are alternatives to this system, not companions.
EXCLUSIVE = ("side_panels", "xt60_holder")

SEGMENT_NAMES = ("front", "centre", "tail")
SKIN_KINDS = ("plain", "vented")


def carcass_label(seg: str, side: str) -> str:
    return f"side_carcass_{seg}_{side}"


def skin_label(seg: str, kind: str, side: str) -> str:
    return f"side_skin_{seg}_{kind}_{side}"


CARCASS_LABELS = tuple(carcass_label(s, h) for s in SEGMENT_NAMES for h in ("l", "r"))
SKIN_LABELS = tuple(skin_label(s, k, h) for s in SEGMENT_NAMES for k in SKIN_KINDS for h in ("l", "r"))
LABELS = (*CARCASS_LABELS, *SKIN_LABELS)

# --- the Z band -----------------------------------------------------------------------------
Z_LO, Z_HI = 9.25, 33.75          # 0.25 clear of plate_mid top (9) and plate_top underside (34)
# RAIL_H 6.0, not 4.6, and min_wall is the reason. The skin's hook fills the rail's flare undercut,
# whose available thickness at the rail's outer face is DT - CLEAR/cos(flare) = DT - 0.20. For the
# hook to have a BLUNT tip (>= 1.25 mm, so it is a hook and not a knife edge that min_wall correctly
# reports as 300 mm³ of thin residual) DT must be ~2.1, and RAIL_H = DT*2 + 1.8 for the 1.8 mm outer
# face the skin rides on.
RAIL_H = 6.0                      # each rail's full height
RAIL_BOT = (Z_LO, Z_LO + RAIL_H)          # 9.25 - 13.85
RAIL_TOP = (Z_HI - RAIL_H, Z_HI)          # 29.15 - 33.75
MID = (RAIL_BOT[1], RAIL_TOP[0])          # the open middle of the ladder, and the skins' crown
_BAND_MID = (MID[0] + MID[1]) / 2
# The aperture lattices are snapped to _BAND_MID, not to the origin: the crown is 12.5 mm tall and an
# AF 5.0 hex plus its 1.8 boundary ligament needs 8.6 of that, so exactly ONE row fits and it has to
# be the centred one. Left on the default origin the rows land at 17.67 and 23.56 and both are
# rejected by the boundary ligament - measured as 4 hexes where 8 fit.

# --- THE RAIL INTERFACE: defined ONCE, both halves generated from it -------------------------
# A dovetail, narrow at the rail's outer face and flaring inboard, so the skin's hook comes in from
# OUTSIDE (where the rail is narrow) and locks under the flare. The opposite taper - wide at the
# outer face - is unbuildable here: at s = rail_out the rail would fill the whole Z band and the
# skin's hook would have to reach over the top rail, which is the 0.25 mm gap under plate_top.
RAIL_T = 3.6                      # rail thickness in s
DT = 2.1                          # dovetail flare per side, in Z
# FLARE_D > DT is a PRINTABILITY constraint, not a taste: the carcass prints on its outer face, so a
# flare face's outward normal has an s component DT / hypot(DT, FLARE_D) pointing at the bed. At
# DT/FLARE_D = 1.0 that is 0.707, just past overhangs()' 0.70 limit, and each of the four flare faces
# is 140-230 mm². At 2.1/3.2 it is 0.549, a 33 deg dovetail that is self-supporting on both flanks.
FLARE_D = 3.2                     # depth of the flare in s (<= RAIL_T)
CLEAR = 0.15                      # skin-on-rail clearance, all round the rail profile
_FLARE_COS = FLARE_D / hypot(DT, FLARE_D)
HOOK_TIP = 1.25                   # the hook's blunt tip thickness (>= the 1.2 TPU floor)
# The hook is the wedge left between the rail's flare and the rail band's Z limit. Its thickness at
# s = rail_out is DT - CLEAR/cos(flare) = 1.90, and it thins going inboard at DT/FLARE_D per mm, so
# the reach at which it is still HOOK_TIP thick is this - 1.0 mm, which is the "~1 mm overlap" the
# brief asks for. Getting this arithmetic backwards (reach 1.66) puts the hook tip at 0.45 mm and
# the 2D section offset refuses the profile outright - which is how the sign error was found.
HOOK_REACH = round((DT - CLEAR / _FLARE_COS - HOOK_TIP) * FLARE_D / DT, 3)
REBATE = 0.30                     # the skin's inner face steps out by this over the middle band
SKIN_W = 1.30                     # skin shell wall (1.2-1.5 band; TPU 95A floor is 1.2)
# SKIN_FRONT = RELIEF_R + 1.5 + CLEAR, and every term of it is a real obstruction: the rails are
# relieved back to RELIEF_R round each axis, the bridge that carries the A ring back to them has to
# land at least 1.5 mm onto rail material, and the skin has to clear that bridge by CLEAR. At 5.6 the
# tail vented skin - whose skirts run the full length, where the plain skin's start later and missed
# it - sat 2.73 mm3 inside its own carcass. The first 6.65 mm of rail was never gripped anyway.
SKIN_FRONT = D_CLIP_BORE / 2 + 1.75 + 1.5 + CLEAR   # RELIEF_R + 1.5 + CLEAR = 6.65
# The rails END at the B-end axis and that end IS the open end (no cantilever): a cantilever past the
# axis would run into the NEXT segment's A-end web, which starts 0.3 mm the other side of the same
# standoff. The B-end web therefore sits INSIDE its own segment (t L-9.2 .. L-0.3).

# Latch: a pocket in the MID RUNG's outer face and a tab on a cantilever tongue cut out of the skin.
# The rung exists because the latch has to be in the middle of the flank: at the front end the plain
# skin's outline is still running out of its cusp and is too narrow to hold a 5.6 mm tongue, and a
# ladder wants a rung anyway.
RUNG_FRAC = 0.42                  # the rung's front edge, as a fraction of the segment length
RUNG_LEN = 8.0
RUNG_DEPTH = RAIL_T               # rung thickness in s: the SAME as the rail, so the union of
#                                 the two leaves no sliver of web standing proud of the rail's inner face
LATCH_Z = (17.8, 20.6)            # the window / tab band in Z (between the tongue's two slits)
# THE LATCH IS A THROUGH WINDOW, not a blind pocket, and that is an overhang fix with a reason. A
# pocket floor 1.0 mm under the rail plane is a 14.0 mm2 flat CEILING once the carcass stands on its
# outer face on the bed (measured: planar 14.0 mm2, normal.Z -1.00), and its forward corner left only
# RUNG_LEN * 0 + 0.5 mm of rung ahead of it (measured: 0.5 mm against a 1.5 mm floor). A window right
# through the 3.6 mm rung has no ceiling at all - every wall of it is parallel to the build axis - and
# it lets you SEE the tab is home. LATCH_DEEP is kept only as the tab's own proud height reference.
LATCH_DEEP = 1.0                  # (legacy) the depth the tab used to sink into a blind pocket
LATCH_WIN = (2.0, 6.0)            # the window along t, measured from the rung's front edge
LATCH_WIN_R = 0.9                 # every window corner is filleted: no sharp corner in the ligament
LATCH_TAB = 0.85                  # tab proud of the rail plane (0.15 slack in the window)
LATCH_LIFT = LATCH_TAB + 0.05     # how far the finger notch lifts the tongue to free the tab
TONGUE_SLIT = 1.0                 # the two slits that make the tongue a cantilever
TONGUE_Z = (17.2, 21.2)           # slit centres; the tongue is the 3.0 mm strip between them
TONGUE_FREE = -1.0                # the slits' forward (free) end, relative to the rung's front edge
TONGUE_ANCHOR = 12.0              # and their rear end, where the tongue is still part of the shell
FINGER = (-6.5, -2.0)             # the finger window, just forward of the tongue's free tip
# M2_BACKUP is OFF, and the B-end web's length is the whole reason. The web is WEB_T - WEB_GAP =
# 8.9 mm long, it already carries a cusped lightening window, and a Ø1.7 bore with 1.5 mm of ligament
# on every side needs 4.7 mm of that 8.9 to itself. Every position that clears the window runs the
# bore out through the web's end face (0.45 mm measured) or, in the skin, out through the rear taper
# (0.254 mm measured on the tail plain skin, 43 thin rays). The dovetail plus the snap latch is the
# retention; a backup screw that has to be squeezed in at 0.45 mm of wall is not a backup.
M2_BACKUP = False                 # the optional Ø1.7 M2 backup screw through skin and web
D_M2 = D_M2_TAP                   # 1.7

# --- clips ----------------------------------------------------------------------------------
RING_R = D_CLIP_BORE / 2 + CLIP_WALL      # 4.85
# How far the squared lip block reaches inboard: exactly to where the ring's OD circle crosses the
# mouth's straight flank, sqrt(RING_R² - (MOUTH/2)²). One millimetre further and the block is proud of
# the ring for no gain; one millimetre less and the ring's own circle leaves a 0.25 mm sliver outside
# the block. It is also what keeps the front segment clear of camera_pod, whose brow post occupies
# x <= 14.0 over y 105-115 at Z 31.5-34: at this reach the nearest material of the front clip is
# x 14.67, and at RING_R it was x 13.66 - measured as 0.02 mm³ of overlap.
LIP_REACH = round((RING_R ** 2 - (STANDOFF_D - MATERIALS[MATERIAL]["snap"]) ** 2 / 4) ** 0.5, 3)
MOUTH = STANDOFF_D - MATERIALS[MATERIAL]["snap"]   # 5.4 PETG throat over a Ø6 standoff
MOUTH_DEG = 270.0                 # the mouth faces local -s, i.e. inboard: push the carcass INBOARD
# THE RAIL RELIEF, and the single worst thing the first build got wrong. The clip bore is a full-
# height Ø6.5 cylinder (it has to be: the standoff runs the whole band), and where it crosses a RAIL
# it shaves the dovetail's 33 deg flare at a glancing angle. Measured on the tail carcass: 0.297 mm of
# PETG left between the bore wall and the flare face, and 147 rays under 1.5 mm, all of them within
# 5 mm of an axis. The fix is not a fillet - it is to STOP THE RAILS SHORT of every axis, at a radius
# where the cut is entirely outside the bore, so the relief face is a clean Ø10 cylinder 1.75 mm clear
# of the bore. The skins never reach into it (they start at SKIN_FRONT 5.6 > RELIEF_R) and at the open
# rear end it doubles as the dovetail's lead-in.
# The cut is a SQUARE END across t, not a cylinder round the axis. A cylinder is the obvious shape
# and it is the wrong one: it crosses the dovetail flare at a glancing angle and leaves exactly the
# feather it was cut to remove, one flare-width further out - 180 rays under 1.5 mm, worst 0.08, all
# of them on the curve where the relief cylinder grazed a flare. A plane normal to t meets the flare
# in a straight edge and leaves a square rail end, which in print orientation (the carcass lies on
# its outer face, t horizontal) is a vertical face that needs no support.
RELIEF_R = D_CLIP_BORE / 2 + 1.75   # 5.0: half the relieved LENGTH along t, 1.75 mm clear of the bore
WEB_T = 9.2                       # end web length along t
WEB_GAP = 0.3                     # gap between the two webs that share a standoff
WEB_DEPTH = RAIL_T                # web thickness in s: aligned with the rail's inner face

# --- the three segments ---------------------------------------------------------------------
# (A, B, rail_out, clip window at A, clip window at B)
# rail_out = the carcass's outer face, as a perpendicular offset from the axis line.
#   front/centre 6.55 = 3.55 mm outside the Ø6 standoff surface, exactly the 3-4 mm the brief asks.
#   tail 4.85 = 1.85 mm outside it, and that is the rear prop disc talking: at y -83 the tail axis
#   line has 6.80 mm of outward room and 4.85 + REBATE + SKIN_W = 6.45 uses 6.45 of it, clearing
#   r 91.9 by 0.35 mm. At 6.55 the tail skin would be 1.9 mm INSIDE the disc. 4.85 is also the floor
#   set by two other numbers: the Ø6.5 bore bites the rail at each axis and must leave >= 1.5 mm of
#   PETG (4.85 - 3.25 = 1.60), and the skin's hook tip at rail_out - FLARE_D = 3.25 must keep 0.2 mm
#   to the Ø6 standoff it slides over (0.25).
# Clip windows, and why each one is where it is:
#   front A  front_tip  31.70-33.75  camera_pod's clip channel is Z 9.2-31.5; this sits 0.2 above it
#   front B  front_arm  15.45-21.00  middle band: the skin's hooks must pass over a B-end ring
#   centre A front_arm  21.60-27.55  0.6 above the front segment's ring on the same standoff
#   centre B rear_arm   15.45-21.00  middle band, and below xt60_holder's 22-33.8 as well
#   tail A   rear_arm    9.45-15.25  bottom rail band: an A-end ring may sit in a rail band because
#                                    the skin starts 5.6 mm aft of it and only ever moves away
#   tail B   rear_tip   22.20-27.75  middle band, 0.2 above tail_block's clip top (Z 22)
SEGMENTS = {
    # t_start / t_end: where the RAILS (and so the skins) begin and end along the segment, and both
    # numbers are a sibling accessory. front t_start 4.4: camera_pod's clip channel (Z 9.2-31.5)
    # reaches x 23.95 between y 105.4 and 112.5, measured as 97 mm³ of overlap with the rails at
    # t 0.3 - the clip ring above Z 31.7 clears it, the rails at 21.9 < x < 25.5 do not. tail t_end
    # L - 5.4: tail_block's own clip owns the rear-tip standoff over Z 2-22 out to r 4.85, measured
    # as 21.5 mm³ against the bottom rail, so the rails stop 5.4 mm short and the B-end ring - which
    # sits at Z 22.2, above tail_block - is carried on a bridge instead.
    "front":  dict(A=(19.0, 109.0), B=(28.5283, 31.8308), rail_out=6.55, t_start=4.4, t_end=0.0,
                   clip_a=(31.70, 33.75), clip_b=(15.45, 21.00)),
    "centre": dict(A=(28.5283, 31.8308), B=(26.0700, -33.3726), rail_out=6.55, t_start=0.3, t_end=0.0,
                   clip_a=(21.60, 27.55), clip_b=(15.45, 21.00)),
    "tail":   dict(A=(26.0700, -33.3726), B=(16.5, -94.0), rail_out=4.90, t_start=0.3, t_end=5.4,
                   clip_a=(9.45, 15.25), clip_b=(22.20, 27.75)),
}
AXIS_OF = {"front": ("standoff_front_tip_right", "standoff_front_arm_right"),
           "centre": ("standoff_front_arm_right", "standoff_rear_arm_right"),
           "tail": ("standoff_rear_arm_right", "standoff_rear_tip_right")}

# --- the skins' form ------------------------------------------------------------------------
# RISE = the plain skin's single-curvature outward bulge, on top of REBATE, at the middle of the
# middle band. The design language asks rise/span 0.28-0.36 of the section span; the middle band
# spans 15.3, so that would be 4.3-5.5 mm. front and centre take 3.0 (0.20 of the span, itself capped
# by the plate_top prop-arch tab - see PLATE_TAB_NOTE); the TAIL takes 0.0, and that is measured:
# at y -83 the tail has 6.80 mm of room and the flat skin already uses 6.45, so every 0.1 of rise is
# 0.1 mm into the rear prop disc. The tail's CARAPACE reading is carried by its outline instead -
# which is the silhouette-first directive (§4.5), not a consolation prize.
# STEP 1 measured every one of these to zero. A `rise` sagitta makes the crown a CYLINDER, and
# every graphic placed on it - the lunule deboss cut from the apex tangent plane, the dimple spheres
# seeded at one constant s - then runs out to a feather where the arc falls away from the tool:
# 707 rays under 1.2 mm on the front plain skin, 790 on the centre, all of them on the crown's outer
# face between s 10.37 and 10.75, i.e. exactly the band the arc sweeps. The elytral swell is now the
# Blender pass's job on a FLAT CAD crown (see `_decorate_centre`), which is where a swell belongs:
# there it is a relaxed mesh with a feathered boundary instead of a tool cutting a tangent surface.
RISE = {"front": 0.0, "centre": 0.0, "tail": 0.0}
CUSP_LEN = {"front": 15.0, "centre": 14.0, "tail": 17.0}   # the plain skin's forward cusp run-out
CUSP_TIP = 4.0                     # the cusp is blunted to this height: a knife edge is thin wall
TAPER = {"front": 2.4, "centre": 2.4, "tail": 2.6}         # plain: crown drawn in at the rear
# Fraction of the length the rear taper runs over. Per segment, and the tail is the one that
# differs: it is the SHORTEST skin, so the same fraction starts its taper further forward relative
# to the latch, and the taper's rising edge ran under the aft cap of the lower tongue slit. That
# left 1.03 mm of ligament between the two against a 1.2 mm floor - a real wall, caught only once
# `_fit.ray_thickness` stopped counting buried faces and grazing chords. At 0.36 the tail's taper
# starts at t 38.2, aft of the slit's last cap at 37.98, so the ligament is the full 1.45 mm.
# The taper keeps its full 2.6 mm depth; it is the run that shortens, which is a smaller change to
# the silhouette than flattening it would be (the alternative needed TAPER 2.6 -> 0.8).
# The centre skin escapes the same trap only by being longer: its slit ends 0.5 mm into its taper
# and the ligament is 1.40 mm.
REAR_RUN = {"front": 0.45, "centre": 0.45, "tail": 0.36}
# ALL silhouette shaping happens in the CROWN (the middle band). The two skirts are plain rectangles
# that end flush with the rails, and that is a printability rule with teeth: an oblique outline edge
# crossing a rail band slices the hook's wedge at a shallow angle and leaves a feather edge - measured
# as 714 of 2483 rays under 1.2 mm, worst 0.07 - while a skirt that STARTS later than the crown leaves
# a step whose face points forward, i.e. upward once the skin stands on its rear face on the bed.
SKIRT_IN = {"bottom": 0.62, "top": 0.98}   # where each skirt starts, as a fraction of CUSP_LEN
# CN-5's thickness gradient, and the reason the plain skin can carry a deboss at all: the middle band
# (the dome crown) is SKIN_W + PAD thick, the rail bands (the skirt) stay at SKIN_W. A 0.6 deboss
# into 1.30 leaves 0.70 and fails the 1.2 floor; into 2.10 it leaves 1.50. The tail's PAD is 0.0
# because its 0.30 mm of prop-disc margin has no room for it - its lunule is CUT THROUGH instead.
# centre 1.0, not 0.8: the Blender dome relaxes the crown mesh and one ray in 191 came back 0.035 mm
# under the 1.2 floor on a 2.1 mm crown. 2.3 mm of CAD wall under the same pass has the margin.
PAD = {"front": 0.8, "centre": 0.8, "tail": 0.0}
# The chamfer's own face normal is (cz, cx) normalised, and the skins print with t as the build axis,
# so its t component IS the overhang cosine: at (3.4, 5.9) that is 0.87 and the face was reported as
# 8.9 mm2 at normal.Z -0.87. cx >= cz brings it under the 0.70 limit; (7.0, 5.9) gives 0.64.
VENT_CUT = (7.0, 5.9)              # vented: the cut corner at the crown's rear top edge

# apertures (the vented skin)
# The brief's louvre is w 3.0, len 11.0, pitch 6.0, ligament 2.2 at 60 deg - measured from the OTHER
# axis, because side_panels sketches in (Y, Z) and prints Z-up while these skins print standing on
# their rear end face, so t is the build axis. Rotated to 30 deg from t (which is the same 60 deg
# between slot and flank Z) two numbers have to follow it: the perpendicular spacing of parallel
# slanted slots is pitch x sin(angle), so pitch 6.0 gives a 0.0 mm ligament at 30 deg and has to
# become 10.4 to keep the same 2.2; and the length comes down to 9.0 because the slot plus its 2.2
# boundary ligament has to fit the 12.5 mm middle band (11.0 needs 12.5 exactly and is dropped).
# length 7.0 and pitch 10.4 are both forced, and both by arithmetic worth writing down.
# HEIGHT: place_apertures grows the slot by the ligament in BOTH directions before testing it against
# the crown, so the grown height is (L + 2g)sin30 + (W + 2g)cos30 = 0.5L + 2.6 + 6.01. At L 11.0 that
# is 14.6 against a 12.5 crown and every slot is dropped; 7.0 gives 12.1.
# PITCH: parallel slanted slots sit pitch*sin(angle) apart perpendicular to themselves, so the 6.0
# that gives side_panels its 2.2 mm ligament at 60 deg gives 0.0 at 30 deg. 10.4 restores the 2.2.
# Measured, not chosen: on the front crown (868 mm2 of region once the tongue's 2 mm clean zone is
# taken out) the old 3.0 x 7.0 at pitch 10.4 placed exactly ONE slot. Shorter, closer and flatter is
# what the crown can actually hold - 3.0 x 5.0 at pitch 6.5 and 20 deg places four. 20 deg is still
# well inside the 45 deg the build axis allows, and the ligament stays at 1.8.
LOUVRE = dict(w=3.0, length=5.0, pitch=6.5, ligament=1.8, angle=20.0)
# AF 3.2, not the family default 5.0, and the crown's height is the whole reason. _style's vent_hex
# lays a TRUE honeycomb: columns pitched (AF+ligament)*sqrt(3)/2 in x with every odd column dropped
# half a row in y, so a field needs 2*(circumradius + ligament) + (AF+ligament)/2 of height before
# BOTH column parities can place. At AF 5.0 that is 15.9 mm against a 12.5 mm crown, and the measured
# result is one row of every other column - 4 lonely portholes, not a honeycomb. At AF 3.2 it is
# 12.3 mm, both parities land (rows at 21.5 and 24.0) and the field is a field. AF 3.2 is still well
# over TPU's 2.2 mm minimum through-hole.
# AF 3.0 / ligament 1.6 rather than 3.2 / 1.8, and it is the BOUNDARY ligament that pays: a hex is
# kept only when its circumradius plus the ligament clears the crown edge, so the usable centre band
# is 12.5 - 2 x (AF/sqrt(3) + ligament) tall. At 3.2/1.8 that is 5.2 mm and the honeycomb places 5 / 3
# / 1 cells on the three segments; at 3.0/1.6 it is 5.8 mm with a tighter column pitch and it places
# 11 / 6 / 2. AF 3.0 is still well over TPU's 2.2 mm minimum through-hole and 1.6 over PETG's wall.
HEX = dict(af=3.0, ligament=1.6)
# 30 deg from t, not 60: the skins print standing on their rear end face, so t is the BUILD axis and
# a slot must lie within 45 deg of it. side_panels' proven 60 deg is measured from the other axis of
# its own sketch; this is the same slot with the same 60 deg between it and the flank's Z.
# tail -> hex, and the crown's length is the reason: `vent_louvre` grows every slot by its ligament
# before testing it, and on the tail's 50 mm crown the 30 deg slot bank placed ZERO apertures. The
# honeycomb at AF 3.2 places a full field in the same 12.5 mm height.
VENT_KIND = {"front": "louvre", "centre": "hex", "tail": "hex"}
# PUNCTA_ON / MARK_ON: both graphics are off on the CAD skins of the base reading and the rows say
# why. A spherical dimple meets the surface TANGENTIALLY - its rim is a zero-angle edge - and a
# crescent cut clean through the 1.30 mm tail crown ends in two knife cusps; between them they were
# 1858 of the 2074 thin rays this module reported. The styled skins in STEP 2 carry their graphics as
# through-cut apertures and chamfered debosses instead, which have no tangent rim.
PUNCTA_ON = False
MARK_ON = False
PUNCTA = dict(pitch=3.6, d=1.8, depth=0.45)
EQUIP = dict(front_fork=(6.0, 9.0), tail_slot=(9.0, 4.2))  # front fork notch; tail pigtail/XT60 slot

# --- THE SKIN LANGUAGES -----------------------------------------------------------------------
# The carcass is one part and never changes; the SKIN is what the user swaps, so it is the skin that
# carries the design language. Each language redraws the CROWN's two long edges and replaces the
# aperture generator, which between them are what a 200 px thumbnail actually shows. Nothing here
# touches a mating face: `skin_profile` (the dovetail, the rebate, the hooks) and `latch_tab` are
# generated from the rail exactly as before, in every language.
#
#   carapace   the domed elytron: a cusped run-out forward, a drawn-in rear taper, louvre/hex banks
#   origami    ONE FOLDED SHEET. The crown is waisted by two 45 deg creases at t 0.33 and 0.66, and
#              every edge in the silhouette is straight - no arc anywhere. Parallelogram ladder slots
#              lie parallel to the nearest crease. Constant wall, 0.4 chamfers, no fillet.
#   brutalist  ONE POURED SLAB. Rectangular plan, 1.0 mm 45 deg chamfers and nothing rounder than
#              that, and ONE big rectangular void per face instead of a field of small holes. Board
#              marking - 0.6 x 0.3 grooves at 2.4 pitch, all running the print direction - wherever
#              the crown carries PAD to sink them into.
#   filigree   ORNAMENTAL CUTWORK ON A SPINE. A 2.4 mm solid spine runs the crown's centreline; above
#              and below it the sheet is cut away to a 1.4 mm net of tangent arcs, and the crown's own
#              edges are scalloped, so the outline is a run of arcs rather than a polyline.
SKIN_STYLES = ("carapace", "origami", "brutalist", "filigree")
ORIGAMI_ANGLE = 45.0      # from the fixed fold set {22.5, 45, 67.5}
ORIGAMI_STEP = 2.4        # how far each crease steps the crown edge in z (both edges, so a waist)
ORIGAMI_SLOT = dict(w=2.4, length=7.0, pitch=9.0, ligament=1.8, angle=ORIGAMI_ANGLE / 2)
BRUT_CHAMFER = 1.0        # the ONLY edge treatment brutalist allows
BRUT_VOID_Z = 7.6         # the big void's height: 2.45 mm of crown left above and below it
BRUT_GROOVE = (0.6, 0.3, 2.4)   # board marking: width, depth, pitch - along t, the print direction
FILIGREE_SPINE = 2.4      # the solid spine on the crown centreline
FILIGREE_R = 2.6          # the scroll radius R; the net's ribbons are 1.4 and the pitch is 1.6 R
FILIGREE_SCALLOP = 2.0    # the arc bite taken out of each crown edge


def style_of_skin(p: dict) -> str:
    """The language this skin is being drawn in. Defaults to `carapace` so every existing call site
    - checks(), sections_of(), the area comparison - keeps working when handed a bare dict."""
    st = p.get("SKIN_STYLE", "carapace")
    return st if st in SKIN_STYLES else "carapace"


# --- the local frame of a segment ------------------------------------------------------------
class Seg:
    """One segment's local frame. local x = t (along the rail, REARWARD), local y = s (outward),
    local z = frame Z. `loc` maps local -> frame, and it is a pure rotation about Z plus a
    translation, so every frame Z in this module survives the mapping untouched."""

    def __init__(self, name: str):
        d = SEGMENTS[name]
        self.name = name
        self.A, self.B = Vector(*d["A"], 0), Vector(*d["B"], 0)
        v = self.B - self.A
        self.L = v.length
        self.t = v / self.L
        self.u = Vector(-self.t.Y, self.t.X, 0)      # outward: +x for the right-hand side
        assert self.u.X > 0, f"{name}: local +s must point outboard"
        self.angle = degrees(atan2(self.t.Y, self.t.X))
        self.loc = Location(self.A) * Location((0, 0, 0), (0, 0, self.angle))
        self.rail_out = d["rail_out"]
        self.t_start = d["t_start"]
        self.t_end = self.L - d["t_end"]
        self.clip_a, self.clip_b = d["clip_a"], d["clip_b"]
        self.axis_a, self.axis_b = AXIS_OF[name]

    # local -> frame, for a point given as (t, s, z)
    def xy(self, t: float, s: float) -> tuple[float, float]:
        p = self.A + self.t * t + self.u * s
        return (p.X, p.Y)

    @property
    def fl(self) -> float:
        """The s at which the dovetail flare starts: the hook's inner tip."""
        return self.rail_out - FLARE_D

    @property
    def web_in(self) -> float:
        return self.rail_out - WEB_DEPTH

    def bands(self) -> tuple[tuple[float, float], tuple[float, float]]:
        return (RAIL_BOT, RAIL_TOP)

    def clips(self) -> tuple[tuple[float, float, float, str], ...]:
        """(t, z0, z1, axis name) for the two clips."""
        return ((0.0, *self.clip_a, self.axis_a), (self.L, *self.clip_b, self.axis_b))

    def webs(self) -> tuple[tuple[float, float], ...]:
        """(t0, t1) of the two end webs, each on its OWN side of its axis and inside the rails."""
        return ((self.t_start, self.t_start + WEB_T),
                (self.t_end - WEB_T, self.t_end - min(WEB_GAP, self.L - self.t_end)))

    def bridges(self) -> tuple[tuple[float, float, float, float], ...]:
        """(t0, t1, z0, z1) of the two plates that carry each clip ring back to its web. They live in
        the clip's OWN Z window, which is how the tail's B ring can sit over a standoff whose lower
        20 mm belongs to tail_block."""
        # The A bridge stops at SKIN_FRONT - 0.2: no skin ever reaches inboard of that, so it may
        # be a full-depth rectangle and fill the dovetail undercut freely. The B bridge is under the
        # skin, but every B window is in the MIDDLE band where there is no undercut to fill - it is
        # clipped against the hook wedges anyway, so a future window cannot quietly break the fit.
        return ((0.0, SKIN_FRONT - 0.2, *self.clip_a),
                (min(self.t_end - 1.2, self.L - RELIEF_R - 1.5), self.L, *self.clip_b))

    def rail_t(self) -> tuple[float, float]:
        return (self.t_start, self.t_end)

    def skin_t(self) -> tuple[float, float]:
        return (max(SKIN_FRONT, self.t_start + 1.2), self.t_end)


SEGS = {n: Seg(n) for n in SEGMENT_NAMES}


# --- 2D helpers, all in one of the two local sketch planes ------------------------------------
def _rect(a0: float, b0: float, a1: float, b1: float) -> Sketch:
    return Pos((a0 + a1) / 2, (b0 + b1) / 2) * Rectangle(a1 - a0, b1 - b0)


def _sz(sk: Sketch, t0: float, t1: float) -> Part:
    """Extrude a cross-section drawn in (s, z) along local +X from t0 to t1."""
    return extrude(Plane.YZ.offset(t0) * sk, amount=t1 - t0)


def _tz(sk: Sketch, s0: float, s1: float) -> Part:
    """Extrude an elevation drawn in (t, z) along local +Y (outward) from s0 to s1.
    Goes through S.extrude_cut because build123d picks the direction PER FACE otherwise."""
    return S.extrude_cut(sk, Plane.XZ.offset(-s0), -(s1 - s0))


def _round(sk: Sketch, corners) -> tuple[Sketch, int]:
    """Fillet every listed (a, b, r) still present as a vertex; corners swallowed by a later union
    are skipped, and the count comes back so checks() can see one went missing."""
    done = 0
    for ca, cb, r in corners:
        hits = sk.vertices().filter_by(lambda v, ca=ca, cb=cb: abs(v.X - ca) < 1e-4 and abs(v.Y - cb) < 1e-4)
        if hits:
            sk = fillet(hits, r)
            done += 1
    return sk, done


# --- THE RAIL INTERFACE, generated once for both halves --------------------------------------
def rail_profile(z0: float, z1: float, rail_out: float) -> Sketch:
    """The dovetail rail's cross-section in (s, z): full RAIL_H inboard, narrowing to RAIL_H - 2*DT
    at the outer face. THE one definition - the carcass unions it and the skin subtracts it grown by
    CLEAR, so the two halves cannot drift apart."""
    ri, fl = rail_out - RAIL_T, rail_out - FLARE_D
    return Polygon((ri, z0), (fl, z0), (rail_out, z0 + DT), (rail_out, z1 - DT),
                   (fl, z1), (ri, z1), align=None)


def rail_pair(rail_out: float) -> Sketch:
    return rail_profile(*RAIL_BOT, rail_out) + rail_profile(*RAIL_TOP, rail_out)


def carcass_envelope(ro: float) -> Sketch:
    """The (s, z) outline the carcass may occupy: the two dovetail rails plus the full-depth middle
    band. Everything unioned on is clipped to it, so no block stands proud of a rail's flare and
    nothing leaves a strip of material where no rail backs it up."""
    return rail_pair(ro) + _rect(ro - RAIL_T, MID[0], ro, MID[1])


def bulge(ro: float, rise: float, pad: float = 0.0) -> Sketch:
    """The plain skin's outer form over the middle band: ONE circular arc, sagitta `rise` over the
    12.5 mm band, so the outer face is a true single-curvature cylinder - the elytral swell, and the
    surface an iridescent highlight needs (SHEEN). Returns the (s, z) region it bounds.

    The tangent break where the arc meets the flat rail band IS the lateral carina (the hard ridge
    where a beetle's dome turns down into its skirt), and it is exactly where the Blender pass puts
    its 0.8 fillet."""
    s_in, s_out = ro + REBATE, ro + REBATE + SKIN_W + pad
    band = _rect(s_in, MID[0], s_out + rise + 1.0, MID[1])
    if rise <= 1e-9:
        return _rect(s_in, MID[0], s_out, MID[1])
    h = (MID[1] - MID[0]) / 2
    r = (h * h + rise * rise) / (2 * rise)
    disc = Pos(s_out + rise - r, (MID[0] + MID[1]) / 2) * Circle(r)
    return band & disc


def skin_profile(seg: Seg, rise: float, pad: float = 0.0, ro: float | None = None,
                 screwed_skin: bool = False) -> Sketch:
    """The skin's cross-section in (s, z), generated FROM `rail_profile` so the fit is one number.

    Over the two rail bands the shell rides the rail's 1.8 mm outer face and grows a HOOK_REACH hook
    into each of the four flare undercuts; over the middle band it steps out by REBATE - which is
    what gives the clip rings their 0.30 mm of clearance, draws the segment's waist line, and leaves
    room for the bulge. The rail is subtracted GROWN BY CLEAR, so 0.15 mm of slack exists on every
    face of the interface by construction rather than by arithmetic done twice."""
    ro = seg.rail_out if ro is None else ro
    flat = ro + CLEAR + SKIN_W
    if screwed_skin:
        # FLAT-BACKED. No hook reaches into the flare: the shell starts outboard of the rail plane
        # and simply lands on the two 1.8 mm rail faces, and the screws hold it there. That is what
        # makes the lift-off radial - straight out along the screw axis, with the carcass still on
        # the standoffs - instead of a rearward slide.
        return (_rect(ro + CLEAR, RAIL_BOT[0], flat, RAIL_BOT[1])
                + _rect(ro + CLEAR, RAIL_TOP[0], flat, RAIL_TOP[1])
                + bulge(ro, rise, pad))
    band = (_rect(ro - HOOK_REACH, RAIL_BOT[0], flat, RAIL_BOT[1])
            + _rect(ro - HOOK_REACH, RAIL_TOP[0], flat, RAIL_TOP[1])
            + bulge(ro, rise, pad))
    return band - offset(rail_pair(ro), CLEAR)


def rung_t0(seg: Seg) -> float:
    return round(RUNG_FRAC * seg.L, 3)


def _web_xs(seg: Seg) -> Sketch:
    """The end web's cross-section in (s, z). The MIDDLE BAND ONLY, plus 0.8 mm of solid overlap into
    each rail band inboard of the flare. Running it the full height instead - the obvious drawing -
    leaves a WEB_DEPTH - FLARE_D strip standing where no rail backs it up, and that strip is the one
    thing in this module that the 2D section test caught as a real thin wall."""
    # NOT "full depth in the middle band plus a strip inboard of the flare in the rail bands", and
    # NOT a 0.8 mm overlap either. Both were measured and both are thin:
    #   * the strip inboard of the flare is RAIL_T - FLARE_D = 0.40 mm wide, dead on
    #     s = rail_out - FLARE_D at z 15.25 and 27.75;
    #   * a 0.8 mm overlap clipped to the rail profile ends its top edge PART WAY UP a 33 deg flare,
    #     and the wedge between the two tapers to nothing: 0.082 mm at (s 2.80, z 28.55) on the tail.
    # The overlap is therefore exactly DT deep, because DT is where a flare runs out: the band
    # MID[0] - DT .. MID[1] + DT clipped to `carcass_envelope` has both of its own edges lying on
    # FULL-DEPTH rail (z 13.15 and 29.85 are where the flares finish), so the overlap is a trapezoid
    # from 3.6 mm down to the rail's own 0.4 mm tip and introduces no edge of its own.
    ro = seg.rail_out
    return _rect(ro - WEB_DEPTH, MID[0] - DT, ro, MID[1] + DT) & carcass_envelope(ro)


def _rung_xs(seg: Seg) -> Sketch:
    """The mid rung's (s, z) section - the same shape as the end web's, and for the same reason."""
    ro = seg.rail_out
    return _rect(ro - RUNG_DEPTH, MID[0] - DT, ro, MID[1] + DT) & carcass_envelope(ro)


def mid_rung(seg: Seg) -> Part:
    """The ladder's middle rung: the block that carries the latch pocket, and the third rung that
    keeps the two rails from working against each other in a side impact.

    Two rectangles, not one: the inboard part runs 0.8 mm INTO both rail bands so the union is a
    solid overlap instead of a tangency (a face-to-face union at exactly Z 15.25 is the kind of
    contact that leaves OCCT a zero-area edge), and it stops at the flare so it never fills the
    undercut the skin's hooks need."""
    r0 = rung_t0(seg)
    return _sz(_rung_xs(seg), r0, r0 + RUNG_LEN)


def _bridge_xs(seg: Seg, z0: float, z1: float, under_skin: bool) -> Sketch:
    """A clip bridge's (s, z) section.

    It is a plain full-depth rectangle, and BOTH of the things that could have made it something
    cleverer were tried and measured:

    1. IT MUST NOT FILL THE DOVETAIL UNDERCUT WHERE A SKIN RUNS. Clipping it against `hook_wedges`
       looks like the answer until a clip window lands wholly inside a rail band - the front's A
       window is Z 31.70-33.75, inside RAIL_TOP - and then the clip deletes the whole bridge and the
       ring becomes its own solid ('2 solid(s), 3379.5 mm3'). The A bridge instead stops 0.2 mm short
       of SKIN_FRONT: no skin reaches inboard of that, so it may be solid, and it still overlaps the
       relieved rail (which resumes at RELIEF_R 5.0) by 0.4 mm of t, which is what keeps it one
       solid. The B bridge does run under a skin, so it keeps the `hook_wedges` clip - a guard, since
       every B window is in the middle band today where there is no undercut to fill.
    2. IT MUST NOT REACH DOWN INTO THE MIDDLE BAND to tie through the web. That was the first fix
       and it cost 24.042 mm3 against camera_pod: the pod's clip channel is Z 9.2-31.5 and reaches
       x 23.95 over y 105.4-112.5, which is exactly where a front A bridge extended below Z 31.70
       lands. Above Z 31.7 the pod is clear - that is why the window is where it is.

    A full-depth rectangle is also what keeps the Ø6.5 bore from cutting a feather here: the bore
    meets a face parallel to itself and leaves rail_out - 3.25 mm of material (3.30 front and centre,
    1.65 tail), not the glancing wedge a rail flare would give it."""
    ro = seg.rail_out
    sk = _rect(ro - RUNG_DEPTH, z0, ro, z1)
    return (sk - hook_wedges(seg)) if under_skin else sk


def clip_ring(seg: Seg, tc: float, z0: float, z1: float) -> Part:
    """A CLOSED collar that encircles the standoff: bore Ø D_CLIP_BORE, wall CLIP_WALL, no mouth.

    It used to be a 270 deg C-clip snapped on sideways, with a squared lip block bolted across the
    throat because the two mouth lips otherwise tapered onto the bore circle and ended in knife
    edges (rays measured them at 0.10 mm against a 1.5 mm floor). A closed ring has no throat and
    no lips, so the block is gone with them: the section is a plain annulus everywhere.

    The trade this makes is deliberate. The carcass is now threaded over the standoff during
    assembly instead of clipped on afterwards - which is exactly right for this system, because the
    carcass is the part that STAYS: the skin still slides off it without the frame being touched.
    A closed ring cannot be levered off, carries load all the way round, and holds the ladder
    concentric instead of letting it splay at a mouth."""
    return c_clip((tc, 0.0), z0, z1 - z0, material=MATERIAL, bore_d=D_CLIP_BORE, wall=CLIP_WALL)


def latch_window_sk(seg: Seg) -> Sketch:
    """The latch window drawn in the flank plane (t, z), corners filleted LATCH_WIN_R."""
    t0 = rung_t0(seg)
    sk = _rect(t0 + LATCH_WIN[0], LATCH_Z[0], t0 + LATCH_WIN[1], LATCH_Z[1])
    sk, _n = _round(sk, [(t0 + a, b, LATCH_WIN_R) for a in LATCH_WIN for b in LATCH_Z])
    return sk


def latch_pocket(seg: Seg) -> Part:
    """The snap-latch WINDOW: right through the 3.6 mm mid rung, so it has no ceiling in print
    orientation and no sharp corner anywhere in its ligaments. Kept under the old name because the
    tab-in-pocket engagement row measures against it."""
    return _tz(latch_window_sk(seg), seg.rail_out - RUNG_DEPTH - 1.0, seg.rail_out + 1.0)


def latch_tab(seg: Seg) -> Part:
    """The skin's latch tab: LATCH_TAB proud of the rail plane, on the cantilever tongue the two
    slits cut out of the shell, and 0.15 mm smaller than the window on every side."""
    t0 = rung_t0(seg)
    sk = _rect(t0 + LATCH_WIN[0] + 0.15, LATCH_Z[0] + 0.15, t0 + LATCH_WIN[1] - 0.15, LATCH_Z[1] - 0.15)
    sk, _n = _round(sk, [(t0 + LATCH_WIN[0] + 0.15, LATCH_Z[0] + 0.15, LATCH_WIN_R - 0.15),
                         (t0 + LATCH_WIN[0] + 0.15, LATCH_Z[1] - 0.15, LATCH_WIN_R - 0.15),
                         (t0 + LATCH_WIN[1] - 0.15, LATCH_Z[0] + 0.15, LATCH_WIN_R - 0.15),
                         (t0 + LATCH_WIN[1] - 0.15, LATCH_Z[1] - 0.15, LATCH_WIN_R - 0.15)])
    return _tz(sk, seg.rail_out - LATCH_TAB, seg.rail_out + REBATE + 0.01)


def tongue_slits(seg: Seg) -> Part:
    """The two slits that turn the latch strip into a cantilever tongue, free at its forward tip.
    Printed standing on the rear end face they run along the BUILD axis, so a 1.0 mm slit is four
    clean perimeters rather than an unsupported hole."""
    r0 = rung_t0(seg)
    out = Part()
    # STADIUM ends, not square ones. A square slit end is a 5.3 mm2 flat ceiling once the skin stands
    # on its rear face (measured at print Z 38.8 on the centre plain skin); a semicircular end of
    # Ø TONGUE_SLIT is a cylinder whose axis lies along s - horizontal on the bed - so overhangs()
    # reads it as an arch and it bridges itself in one perimeter.
    for zc in TONGUE_Z:
        length = TONGUE_ANCHOR - TONGUE_FREE
        out += _tz(Pos(r0 + (TONGUE_FREE + TONGUE_ANCHOR) / 2, zc) * SlotOverall(length, TONGUE_SLIT),
                   seg.rail_out - 1.0, seg.rail_out + REBATE + SKIN_W + 12.0)
    return out


def finger_window(seg: Seg) -> Part:
    """The finger notch: a window through the shell just forward of the tongue's free tip, so a nail
    can go under the tip and lever the tab out of its pocket. It is also the one place a hex or
    louvre bank is interrupted, which is how you find it by feel."""
    r0 = rung_t0(seg)
    sk = _rect(r0 + FINGER[0], TONGUE_Z[0] + 0.5, r0 + FINGER[1], TONGUE_Z[1] - 0.5)
    sk, _ = _round(sk, [(r0 + a, b, 1.4) for a in FINGER for b in (TONGUE_Z[0] + 0.5, TONGUE_Z[1] - 0.5)])
    return _tz(sk, seg.rail_out - 1.0, seg.rail_out + REBATE + SKIN_W + 12.0)


def tongue_lift(seg: Seg) -> Part:
    """What the finger notch does, as a solid: everything of the skin deeper than the pocket's mouth
    plane inside the tongue's own band. Subtracting it models the tongue FLEXED CLEAR, which is the
    state the skin is actually in while it is being pulled off - see the removal sweep in checks()."""
    r0 = rung_t0(seg)
    return _sz(_rect(seg.rail_out - LATCH_TAB - 1.0, LATCH_Z[0], seg.rail_out - LATCH_TAB + LATCH_LIFT,
                     LATCH_Z[1]), r0 + TONGUE_FREE, r0 + TONGUE_ANCHOR)


def m2_backup(seg: Seg) -> Part:
    """The optional Ø1.7 M2 backup screw: radial, through the skin and into the B-end web, in the
    middle band where the web is a full WEB_DEPTH thick. 2.35 mm clear of the B-end clip ring."""
    t = seg.L - WEB_T + 2.2
    z = MID[1] - 2.8
    return _tz(Pos(t, z) * Circle(D_M2 / 2), seg.rail_out - WEB_DEPTH - 1.0,
               seg.rail_out + REBATE + SKIN_W + 12.0)


def mating_cuts(seg: Seg, p: dict) -> Part:
    """The skin's MATING cuts, in one place because they are one thing: the features that have to
    measure exactly what CAD says for a skin to slide onto the carcass and latch. The tongue slits
    are the cantilever that carries the latch tab; the M2 bore lands in the B-end web.

    They are separated from the form cuts because the Blender pass must never see them, and each
    one breaks it differently:
      the SLITS SEVER. A relaxed mesh made from a skin already open along them comes back
        FRAGMENTED - measured, 15-21 solids out of the re-boolean, wandering with every unrelated
        parameter - and `side_panels.py:33-35` records the same failure on the sibling module.
    The architectural reason is the stronger one: build123d owns every mating feature so it stays
    numerically exact, and Blender only adds form on top. So `_decorate_centre` domes a skin that is
    still SOLID here and hands these to `decorate(cuts=...)`, which subtracts them in B-rep after the
    re-boolean - exact geometry, and a mesh with no slit to sever.

    The finger window is NOT in here, and that was measured both ways. Deferring it too gave a
    cleaner dome, but it also took the only interior vertices out of a 404-triangle coarse mesh: the
    whole protect mask came back frozen and the sewn solid was refused ("BRepCheck_Analyzer says
    invalid") at every rise. Its rim is handled where it belongs instead - `_decorate_centre` takes
    a collar around it OUT of the decoration region, so the dome never displaces the rim."""
    out = tongue_slits(seg)
    if p.get("M2", M2_BACKUP):
        out += m2_backup(seg)
    return out


def _ts(sk: Sketch, z0: float, z1: float) -> Part:
    """Extrude a plan sketch drawn in (t, s) along local +Z."""
    return extrude(Plane.XY.offset(z0) * sk, amount=z1 - z0)


def cylinder_s(seg: Seg, tc: float, zc: float, s0: float, s1: float, d: float) -> Part:
    """A cylinder whose axis runs along local +s (radially outboard) at (tc, zc), from s0 to s1.
    This is the screw axis: the one direction in which a screwed skin lifts off its carcass."""
    return _tz(Pos(tc, zc) * Circle(d / 2), s0, s1)


def cone_s(seg: Seg, tc: float, zc: float, s0: float, s1: float, d0: float, d1: float) -> Part:
    """A truncated cone on the same radial axis: the 90 deg countersink under a flat head. Cone is
    built along +Z and turned onto +s by Rx(-90), which maps +Z to +Y."""
    c = Cone(d0 / 2, d1 / 2, s1 - s0, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return c.rotate(Axis.X, -90.0).moved(Location((tc, s0, zc)))


def _lens_window(t0: float, t1: float, zc: float, half: float) -> Sketch:
    """A cusped lightening window: a true vesica, two tangent arcs meeting at a point (CN-3)."""
    return S.lens((t0, zc), (t1, zc), half)


# --- the carcass ------------------------------------------------------------------------------
def build_carcass(seg: Seg, p: dict) -> Part:
    """The ladder: two dovetail rails, two end webs, two 270 deg C-clips. The only part of this
    system that touches the frame, and it touches it ONLY through the two clip bores."""
    ro = seg.rail_out
    body = _sz(rail_pair(ro), *seg.rail_t())
    # THE RELIEF (see RELIEF_R): the rails stop clear of both clip axes so the bore never gets to
    # shave a flare. Cut it here, on the bare rail prism, before anything is unioned on.
    for tc, _cz0, _cz1, _axis in seg.clips():
        body -= box(tc - RELIEF_R, ro - RAIL_T - 1.0, Z_LO - 1.0, tc + RELIEF_R, ro + 1.0, Z_HI + 1.0)

    for wt0, wt1 in seg.webs():
        body += _sz(_web_xs(seg), wt0, wt1)
    for i, (bt0, bt1, bz0, bz1) in enumerate(seg.bridges()):
        body += _sz(_bridge_xs(seg, bz0, bz1, under_skin=(i == 1)), bt0, bt1)

    for tc, cz0, cz1, _axis in seg.clips():
        body += clip_ring(seg, tc, cz0, cz1)

    # lightening windows: one cusped vesica per web, forward of the latch pocket on the A web
    (a0, a1), (b0, b1) = seg.webs()
    zc = (MID[0] + MID[1]) / 2
    win = _lens_window(a0 + 1.8, a1 - 1.8, zc, 2.6) + _lens_window(b0 + 1.8, b1 - 1.8, zc, 2.6)
    # KEEP THE LIGHTENING WINDOW OFF THE CLIP RINGS. A web reaches to within 2.1 mm of its own
    # standoff axis, so the vesica's rear cusp was landing inside the RING_R 4.85 collar and cutting
    # a 0.083 mm crescent of PETG between the window and the Ø6.5 bore (measured at t 62.6, s 1.95,
    # z 20.4 on the centre carcass). The tool is trimmed by a collar guard instead of the window
    # being shortened, so the window keeps its full span wherever the ring is not.
    guard = Part()
    for tc, _cz0, _cz1, _axis in seg.clips():
        guard += cylinder(tc, 0.0, Z_LO - 1.0, Z_HI + 1.0, 2 * (RING_R + 1.0))
    body -= (_tz(win, seg.web_in - 1.0, ro + 1.0) - guard)

    body += mid_rung(seg)
    if p.get("SCREWED"):
        # The screwed skins do not latch, so the rung keeps no pocket; instead every station that
        # has no web or rung under it gets one, and each carries a boss for its tapped hole.
        carried = [*seg.webs(), (rung_t0(seg), rung_t0(seg) + RUNG_LEN)]
        for tc in screw_stations(seg, p):
            if not any(t0 <= tc <= t1 for t0, t1 in carried):
                body += _boss_rung(seg, tc, p)
        body += screw_bosses(seg, p)
        if p.get("CABLE"):
            body -= cable_channel(seg, p)
    else:
        body -= latch_pocket(seg)
    if p.get("M2", M2_BACKUP):
        body -= m2_backup(seg)

    if p.get("SCREWED"):
        body -= screw_sockets(seg, p)  # the spigot's socket, sunk below the rails' outer plane
        body -= screw_taps(seg, p)     # blind, so BLIND mm is left under every thread
    # Bores LAST, so no web or rail material survives inside a bore. No throat is cut: the collars
    # are CLOSED rings that encircle the standoff (see clip_ring). The carcass is threaded over the
    # standoffs at assembly instead of snapped on afterwards - it is the part that stays, and the
    # skin is what comes off without the frame being touched.
    for tc, _cz0, _cz1, _axis in seg.clips():
        body -= cylinder(tc, 0.0, Z_LO - 1.0, Z_HI + 1.0, D_CLIP_BORE)

    # UNIFY. A union leaves each operand's own face inside the result, and ray sampling then reads
    # an internal face as a wall: before this line the clip ring's outer cylinder was being reported
    # as 0.305 mm of material on every clip of every segment. clean() removes the internal faces and
    # leaves the solid itself untouched.
    body = body.clean()

    # No lead-in bevel at the rails' open end. The obvious one - a 45 deg plan cut across the flare -
    # leaves a 0.2 mm sliver at the rail's inner face wherever it stops short of the full thickness,
    # and cutting the full thickness just shortens the rail. With 0.15 mm of clearance on every face
    # of the dovetail the hooks find the flare without help.
    return body


# --- the skins --------------------------------------------------------------------------------
def elevation(seg: Seg, kind: str, p: dict) -> Sketch:
    """The skin's outline in the flank plane (t, z) - the silhouette that makes the two readings
    different shapes rather than the same shape with two hole patterns (§4.5). Areas are compared
    in checks(); the gate is 12 %."""
    t0, t1 = seg.skin_t()
    z0, z1 = MID
    # Two outline levers the screwed variants use, both defaulting to the shape the dovetail
    # variants have always had, so `plain` and `carapace` are untouched:
    #   SKIRT_FULL - the skirts run the whole length instead of starting part way along the cusp,
    #     which is what lets `clamped` land on rail material at all four screw stations;
    #   CUSP_SCALE - scales the forward cusp run-out. A LONGER run-out rakes the nose and takes
    #     area OUT of the plain skin, which also widens its margin against the vented one; a
    #     shorter one fills the nose in and narrows that margin, which is why the first attempt at
    #     0.55 failed the 12 % outline gate. Both levers change the silhouette, which is the point:
    #     variants have to differ in outline, not just in fastener count.
    skirt_full = bool(p.get("SKIRT_FULL"))
    cusp_scale = float(p.get("CUSP_SCALE", 1.0))
    if kind == "plain":
        run = CUSP_LEN[seg.name] * cusp_scale
        rr = t1 - REAR_RUN[seg.name] * (t1 - t0)
        tp = TAPER[seg.name]
        zm = (z0 + z1) / 2
        crown = Polygon((t0, zm - CUSP_TIP / 2), (t0 + run, z0), (rr, z0), (t1, z0 + tp),
                        (t1, z1 - tp), (rr, z1), (t0 + run, z1), (t0, zm + CUSP_TIP / 2), align=None)
        bot = t0 if skirt_full else t0 + SKIRT_IN["bottom"] * run
        top = t0 if skirt_full else t0 + SKIRT_IN["top"] * run
        return (crown
                + _rect(bot, RAIL_BOT[0], t1, RAIL_BOT[1])
                + _rect(top, RAIL_TOP[0], t1, RAIL_TOP[1]))
    cx, cz = VENT_CUT
    crown = Polygon((t0, z0), (t1, z0), (t1, z1 - cz), (t1 - cx, z1), (t0, z1), align=None)
    crown, _n = _round(crown, [(t0, z0, 1.0), (t0, z1, 1.0)])
    return (crown + _rect(t0, RAIL_BOT[0], t1, RAIL_BOT[1])
            + _rect(t0, RAIL_TOP[0], t1, RAIL_TOP[1]))


def _vent_region(seg: Seg, kind: str, p: dict) -> Sketch:
    """Where an aperture may go: the middle band only. The rail bands carry the four hooks and are
    structure - an aperture there is an aperture through the interface."""
    t0, t1 = seg.skin_t()
    return elevation(seg, kind, p) & _rect(t0, MID[0], t1, MID[1])


def _vent_clean(seg: Seg) -> list[Sketch]:
    """Clean zones inside the flank: the latch tongue and its slits, the M2 boss, the tail's
    equipment slot. 2.0 mm of ligament round each, as CN-7 asks."""
    r0 = rung_t0(seg)
    out = [_rect(r0 + FINGER[0] - 2.0, TONGUE_Z[0] - 2.2, r0 + TONGUE_ANCHOR + 2.2, TONGUE_Z[1] + 2.2),
           _rect(seg.L - WEB_T - 0.4, MID[1] - 6.4, seg.L - WEB_T + 4.8, MID[1])]
    if seg.name == "tail":
        w, h = EQUIP["tail_slot"]
        tc = seg.L - 16.0
        out.append(_rect(tc - w / 2 - 2.2, MID[0] + 2.0, tc + w / 2 + 2.2, MID[0] + 6.4 + h))
    return out


def apertures(seg: Seg, kind: str, p: dict) -> tuple[Sketch, int, str]:
    """The vented skin's aperture bank. Two readings, both from _style's own generators:
    `vent_louvre` at 30 deg from the print axis (the same 60 deg slot side_panels proved, measured
    from the flank's Z instead) and `vent_hex` AF 5.0 / ligament 1.8, flat-top so every vent bridges
    itself. The plain skin has none: that is what makes it plain."""
    if kind != "vented":
        return Sketch(), 0, "plain: no apertures"
    region = _vent_region(seg, kind, p)
    clean = _vent_clean(seg)
    if VENT_KIND[seg.name] == "hex":
        sk, n = S.vent_hex(region, pitch=HEX["af"] + HEX["ligament"], ligament_min=HEX["ligament"],
                           af=HEX["af"], clean=clean, hole_min=2.0, origin=(0.0, _BAND_MID))
        return sk, n, f"vent_hex AF {HEX['af']} ligament {HEX['ligament']}"
    sk, n = S.vent_louvre(region, pitch=LOUVRE["pitch"], ligament_min=LOUVRE["ligament"],
                          width=LOUVRE["w"], length=LOUVRE["length"], angle=LOUVRE["angle"],
                          clean=clean, hole_min=2.0, origin=(0.0, _BAND_MID))
    return sk, n, (f"vent_louvre {LOUVRE['w']} x {LOUVRE['length']} at {LOUVRE['angle']} deg from the "
                   f"print axis (60 deg from the flank's Z)")


def equipment(seg: Seg, kind: str) -> Sketch:
    """The cutouts the installed equipment needs: the front segment's fork notch, which follows the
    top-plate prong and the camera pod's tilt arc, and the tail's pigtail / XT60 exit slot."""
    t0, _t1 = seg.skin_t()
    sk = Sketch()
    if seg.name == "front":
        # OPEN AT THE FRONT EDGE. Closed 1.6 mm aft of it the notch's forward wall is a 13.5 mm2
        # flat ceiling in print orientation (measured at print Z 70.6); carried right out through
        # the skin's leading edge it has no forward wall at all, and it reads as a scallop.
        w, h = EQUIP["front_fork"]
        notch = _rect(t0 - 2.0, Z_HI - h, t0 + w, Z_HI + 1.0)
        notch, _ = _round(notch, [(t0 + w, Z_HI - h, 1.6)])
        sk += notch
    if seg.name == "tail":
        w, h = EQUIP["tail_slot"]
        tc = seg.L - 16.0
        # Z MID[0] + 4.2, not + 2.2. The tail's crown is a TAPERED silhouette: its lower edge
        # climbs from Z 15.25 at t 0.6 L to Z 15.25 + TAPER at the rear end, and at the slot's rear
        # the ligament between the slot floor and that edge measured 0.47 mm. Two millimetres higher
        # the slot sits between the two taper edges with 2.5 mm to each.
        sk += Pos(tc, MID[0] + 4.2 + h / 2) * SlotOverall(w, h, rotation=0)
    return sk


def mark_of(seg: Seg, kind: str, p: dict) -> tuple[Part | None, str]:
    """CN-4, the maculation. A DEBOSSED lunule where the crown is PAD thicker than the skirt, and a
    lunule CUT THROUGH on the tail, whose crown carries no PAD (see PAD). Mirrored for the left
    flank by `pair()`, never rotated, so the pair carries no suture (CN-1: the pair IS the split)."""
    if kind != "plain":
        return None, "vented: the aperture bank is the graphic"
    if not MARK_ON:
        return None, ("no CAD mark on the base reading: a deboss cut from the crown's tangent plane "
                      "feathers out where the crown falls away, and a lunule cut clean through the "
                      "1.30 mm tail crown ends in two knife cusps - see MARK_ON")
    t0, t1 = seg.skin_t()
    size = S.clamp(0.30 * (t1 - t0), 16.0, 28.0)
    if not S.mark_fits("lunule", size):
        return None, f"lunule needs {S.MARK_MIN['lunule']}, only {size:.1f} available"
    ro, rise = seg.rail_out, RISE[seg.name]
    s_out = ro + REBATE + SKIN_W + PAD[seg.name] + rise
    tc = (t0 + t1) / 2 + 2.0
    zc = (MID[0] + MID[1]) / 2
    mode = "deboss" if PAD[seg.name] > 0 else "cut"
    m = S.mark("lunule", size, mode, (tc, s_out - 0.02, zc), normal=(0, 1, 0), x_dir=(-1, 0, 0),
               through=SKIN_W + 2.0 if mode == "cut" else 0.0)
    return m, f"lunule {size:.1f} mm {mode} on the crown"


def puncta_of(seg: Seg, kind: str, p: dict) -> tuple[Part | None, int, str]:
    """The punctation field - rows of pits, the second thing you notice on a tiger beetle's shell.
    Ø1.8 x 0.45 deep on a hex pitch of 3.6, and ONLY on a crown that carries PAD: 0.45 into the
    1.30 skirt would leave 0.85, under the floor. The centre plain skin keeps its crown clear for
    the Blender pass, which owns that surface."""
    if not PUNCTA_ON or kind != "plain" or PAD[seg.name] <= 0 or seg.name == "centre":
        return None, 0, ("no punctation: a spherical dimple meets the crown tangentially, and its "
                         "zero-angle rim is what 707 of the front skin's thin rays were reading")
    ro, rise = seg.rail_out, RISE[seg.name]
    s_out = ro + REBATE + SKIN_W + PAD[seg.name] + rise
    d, depth, pitch = PUNCTA["d"], PUNCTA["depth"], PUNCTA["pitch"]
    rs = (d * d / 4 + depth * depth) / (2 * depth)
    t0, t1 = seg.skin_t()
    region = _vent_region(seg, kind, p) - _rect(t0, MID[0], t0 + CUSP_LEN[seg.name] * 0.7, MID[1])
    centres = S.grid_centres(region, pitch, pitch * 0.866, stagger=True)
    flat, n = S.place_apertures(region, lambda cx, cy, g: Pos(cx, cy) * Circle(d / 2 + g), centres,
                               ligament_min=pitch - d, clean=_vent_clean(seg), pairwise=False)
    if not n:
        return None, 0, "no dimple survived the clean zones"
    tool = Part()
    for f in flat.faces():
        c = f.center()
        tool += Pos(c.X, s_out + rs - depth, c.Y) * Sphere(rs)
    return tool, n, f"{n} dimples Ø{d} x {depth} deep, hex pitch {pitch}, on the {SKIN_W + PAD[seg.name]} crown"


def _skin_s_range(seg: Seg, rise: float, pad: float) -> tuple[float, float]:
    return (seg.rail_out - HOOK_REACH - 1.0, seg.rail_out + REBATE + SKIN_W + pad + rise + 2.0)


def build_skin(seg: Seg, kind: str, p: dict, *,
               defer_mating: bool = False) -> tuple[Part, dict]:
    """One skin. Everything about how it meets the carcass comes out of `skin_profile`, so `kind`
    only ever changes the FORM: the outline, the outer surface and the apertures."""
    sc = bool(p.get("SCREWED"))
    rise = RISE[seg.name] if kind == "plain" else 0.0
    # The screwed skins carry SCREW_PAD of extra shell over the middle band so the countersink has
    # material behind it; that pad is the whole reason a flat head can finish below the surface.
    pad = (PAD[seg.name] if kind == "plain" else 0.0) + (SCREW_PAD if sc else 0.0)
    s0, s1 = _skin_s_range(seg, rise, pad)
    info: dict = {}

    body = _sz(skin_profile(seg, rise, pad, screwed_skin=sc), *seg.skin_t())
    body = body & _tz(elevation(seg, kind, p), s0, s1)
    if not sc:
        body += latch_tab(seg)

    ap, n, how = apertures(seg, kind, p)
    if sc and ap.faces():
        # No vent may be cut within a head radius plus a wall of a screw. Left to chance one was:
        # the clamped centre vented skin came back with rays at 0.87 mm where a hex cell met a
        # countersink. The keepout is subtracted from the aperture TOOL, so the vent field simply
        # opens around each station instead of the station being moved to dodge the pattern.
        keep = Sketch()
        r = screw_of(p)["d_head"] / 2 + MATERIALS[MATERIAL]["wall"]
        for tc in screw_stations(seg, p):
            keep += Pos(tc, _BAND_MID) * Circle(r)
        ap = ap - keep
        n = len(ap.faces())
    info["apertures"], info["aperture_note"] = n, how
    cut = ap + equipment(seg, kind)
    if cut.faces():
        body -= _tz(cut, s0, s1)
    if sc:
        # No finger window and no tongue: there is nothing to lift. The screws are the retention
        # and the release. The spigots go on BEFORE the holes so the bore passes through them.
        # clean() for the same reason build_carcass does it: unioning the spigots onto the shell
        # leaves the shell's own inner face buried INSIDE the solid, and a ray crossing it stops
        # there and reports the spigot's 0.95 mm protrusion as the wall. Measured: 61 thin rays
        # from the spigots alone, none once the internal faces are gone.
        body = (body + skin_spigots(seg, p)).clean()
        body -= screw_holes_skin(seg, p, pad)
        info["screws"] = len(screw_stations(seg, p))
    else:
        body -= finger_window(seg)
        # `defer_mating` leaves the tongue slits and the M2 bore UNCUT, for the one caller that
        # follows with a Blender pass: see `mating_cuts`. The caller must subtract them itself.
        if not defer_mating:
            body -= mating_cuts(seg, p)

    m, why = mark_of(seg, kind, p)
    info["mark"] = why
    if m is not None:
        body -= m
    pun, npun, pwhy = puncta_of(seg, kind, p)
    info["puncta"], info["puncta_note"] = npun, pwhy
    if pun is not None:
        body -= pun
    return body, info


# --- the Blender pass: the centre plain skin only ---------------------------------------------
def _decorate_centre(skin: Part, seg: Seg, variant: str, mating: Part) -> Part:
    """`elytra_dome` on the one part in the set that is a big, closed, plate-like shell: the centre
    plain skin's 59 x 12.5 mm crown, 2.10 mm thick, with no clip, bore or seat anywhere in it.

    The mask is written as "everything except the crown I want swelled", which is the safe form. The
    rise is passed EXPLICITLY: left to rise_span the recipe would take the span from the part's
    longest non-axis extent (59 mm) and ask for 9.4 mm, which the envelope-growth gate refuses at
    once and which would also put the flank inside the front prop disc. 0.9 mm on top of the 3.2 mm
    the CAD arc already carries is the elytral swell finished, not started.

    `flat=("Y",)` is the printability half of it: the segment runs roughly along -Y, the skin prints
    standing on its rear end face, and a swell that varied along Y would put a down-facing slope on
    the build axis. Held flat along Y it is a RIDGE - constant along the segment, curved across the
    flank - which is both what an elytron looks like and what prints without a support.

    `skin` arrives with its MATING cuts still uncut (`build_skin(defer_mating=True)`) and `mating`
    carries them, placed. That is not a tidiness choice: the dovetail slits are the skin-to-carcass
    interface, build123d owns every mating feature so it stays numerically exact, and a mesh made
    from a skin already open along them relaxes into 15-21 disconnected solids. Domed solid and cut
    afterwards through `cuts=`, the mesh stays one body and the slits keep their CAD numbers."""
    # feather 3.0, and the CROWN'S HEIGHT sets it. The blend runs `feather` in from each edge of the
    # region, so a dome only reaches its full `rise` where 2 x feather fits inside the region: the
    # crown is 8.1 mm tall in Z, so feather 4.5 asks for 9.0 mm of blend across 8.1 mm and the rise
    # multiplier never reaches 1.0 ANYWHERE. Measured at rise 0.9: the swell arrived as 0.056 mm,
    # +9.5 mm3 on a 737 mm2 crown - a dome only a volume probe could find. At 3.0 the blend is 6.0 mm
    # inside 8.1 and a 2.1 mm band reaches full rise.
    # It cannot go lower. The dome swells the crown OUTWARD and so cannot thin the middle of it, but
    # the relaxed mesh UNDERSHOOTS where it rejoins the protected region, and that boundary dip is
    # what the wall floor catches: at rise 0.9 feather 2.0 came back 0.0171 mm under the 1.2 mm floor
    # (0.0164 at relax 1), while 3.0 measured 2.3 mm with 0 thin rays. 3.0 is the smallest blend -
    # the strongest dome - that the wall floor allows, not a number chosen for looks.
    rise = RISE["centre"]
    pad = PAD["centre"]
    s0, s1 = _skin_s_range(seg, rise, pad)
    crown_in = seg.rail_out + REBATE + SKIN_W + pad + rise - 0.62
    t0, t1 = seg.skin_t()
    crown = _tz(_rect(t0 + 9.0, MID[0] + 2.2, t1 - 6.0, MID[1] - 2.2), crown_in, s1 + 2.0)
    crown = crown.moved(seg.loc)
    guard = skin - crown                      # the mask: everything except the crown
    # restore=False, which is what every other module here does and what decorate()'s own docstring
    # asks for - "mask big, restore small; they are different jobs". The mask already guarantees
    # Blender moved no vertex in the mating zone, so re-unioning an exact B-rep copy of the two rail
    # bands on top of the tessellation of the SAME geometry is a geometric no-op that hands OCCT a
    # pile of coincident faces. Measured on this part, with the mating cuts already deferred: the
    # rail-band restore came back as 15 solids, restore=False as one. The mating faces that matter
    # here are the hook wedge and the rebate, and they are PLANAR - a planar face tessellates onto
    # its own plane exactly, so there is nothing for a restore to put back.
    restore = False
    # rise 4.5, subdiv 3, relax 2 - and `rise` is a REQUEST the weight field spends, not a height.
    # 4.5 buys 1.764 mm of actual swell (39 %), which is the ridge you can see; the rest is spent by
    # the lateral feather running the dome out to nothing at the crown's border and at the finger
    # window's rim, and by the relax pass. The three knobs were measured together, all green:
    #   3.0 / relax 4 / subdiv 2 -> 0.929    4.5 / relax 2 / subdiv 3 -> 1.764
    #   3.0 / relax 2 / subdiv 2 -> 1.038    5.5 / relax 2 / subdiv 3 -> refused (1 thin ray)
    #   3.0 / relax 4 / subdiv 3 -> 1.095    4.5 / relax 1 / subdiv 3 -> refused (1 thin ray)
    # so 4.5 is at the edge: the wall gate takes the next step up, and relax below 2 stops smoothing
    # the ridge's own facets. subdiv 3 is what makes 4.5 reachable at all - a coarser crown cannot
    # carry the curvature and folds instead.
    # HISTORY, because two separate bugs hid this and both are worth not re-deriving. Until the
    # protect ramp was made lateral every crown vertex was capped at 0.62/feather = 0.21, so `rise`
    # was a lever wired to nothing: 0.9 delivered 0.087 mm and 1.15 delivered 0.11. And until the
    # ramp also feathered towards the part's OWN rims, the finger window's edge pleated at anything
    # over rise 0.6 - adjacent facets 0.02 mm apart with opposing normals, a wall reading of 0.0241
    # on a 2.105 mm wall, the same "pinched a 0.02-0.03 mm fold at the USB corner" `side_panels.py`
    # recorded. Masking that rim instead was tried three ways and every one left a solid OCCT would
    # not sew at any rise down to 0.3 (a collar out of the region, the same collar into the guard,
    # and moving the crown's t-start past the window). Feathering towards the rim needs no mask.
    key = f"side_skin_centre_plain_r__{variant}"
    out = BL.decorate(skin, "elytra_dome",
                      {"rise": 4.5, "subdiv": 3, "relax": 2, "min_nz": 0.72, "feather": 3.0,
                       "axis": "X", "flat": ("Y",), "dome_spread": 1.0},
                      protect=guard, restore=restore, cuts=mating, region=crown,
                      cache_key=key, wall_floor=1.2,
                      tri_budget=11000, allow=(), guard_margin=0.6)
    # decorate() hands back the INPUT unchanged when a gate refuses, and the input is the skin with
    # its mating cuts still deferred - so on that path the slits have to be cut here or the skin
    # would ship with no tongue at all. Only the decorated path gets them from `cuts=`.
    res = BL.RESULTS.get(key)
    return out if (res is not None and res.applied) else out - mating


# --- the screwed alternative ------------------------------------------------------------------
# A SECOND ATTACHMENT SCHEME, alongside the dovetail, not replacing it. The dovetail's argument is
# tool-less service: the skin slides off rearward and the latch releases under a fingernail. A
# screwed skin trades that for retention and precision - it cannot rattle loose or pop off in a
# crash, it is pulled FLAT against the carcass so a 1.3 mm shell stops drumming, and the joint
# carries load the hook cannot. The property the user actually asked to keep survives either way:
# the skin still comes off without the carcass leaving the standoffs. It just needs a driver.
#
# THE SCREW IS COUNTERSUNK, and the shell thickness is the reason. An M2 socket head is ~1.6 mm
# tall and the shell is SKIN_W 1.30, so a counterbore deep enough to bury one leaves nothing behind
# it. A 90 deg countersink sinks (3.8 - 2.4)/2 = 0.70 mm, and the screwed skins carry SCREW_PAD of
# extra wall over the middle band, so 1.60 mm of material remains under the head and it finishes
# below the outer surface - which matters, because a proud head on the widest part of the airframe
# is the first thing a gate post finds.
#
# M2 IS THE DEFAULT AND M1.5 IS OFFERED, NOT RECOMMENDED. M1.5 self-tapped into PETG has a 0.225 mm
# thread and strips on the second or third assembly; it is here because the user asked for it, and
# `SCREW_SIZES["M1.5"]` selects it. Either way the engagement is the honest number below.
SCREW_SIZES = {
    # d_tap: self-tapping pilot. d_thru: clearance in the skin. d_head/csk: 90 deg countersink.
    "M2":   dict(d_tap=D_M2_TAP, d_thru=D_M2_THRU, d_head=3.8, boss_d=8.2, spigot_d=4.8, min_eng=6.0),
    "M1.5": dict(d_tap=1.25,     d_thru=1.70,      d_head=3.0, boss_d=7.5, spigot_d=4.2, min_eng=4.5),
}
SCREW_SIZE = "M2"
# THE JOINT IS A SOCKET AND SPIGOT, and three separate failures drove it there. A boss standing
# REBATE proud of the rails to meet the skin lifted the whole carcass off the print bed - every
# face that used to lie on it became a 0.3 mm overhang, 6 of them per part. Thickening the skin
# outward instead to give the countersink material put the TAIL skin 1.0 mm into the rear prop
# disc, which it has no room for (6.80 mm available, 6.45 already used). So the depth is taken
# INBOARD: the carcass's web is counterbored to SOCKET_DEEP, the skin grows a matching spigot into
# it, and the head sinks through SKIN_W + REBATE + SOCKET_DEEP of material without the outer
# surface moving at all. The spigot locates the skin laterally as a bonus - the screw no longer
# has to be the only thing stopping it sliding.
SCREW_PAD = 0.00       # no outward pad: the tail has no room for one (see above)
SOCKET_DEEP = 0.80     # how far the socket is sunk below the rails' outer plane
SPIGOT_CLEAR = 0.15    # radial slack between spigot and socket - the same CLEAR the dovetail uses
BOSS_IN = 4.00         # how far the boss stands INBOARD of the web's inner face
BOSS_CLEAR_T = 2.60    # a boss centre keeps this much of its own radius clear of a web's end
BORE_KEEPOUT = 6.40    # a boss centre stays this far along t from either clip axis (bore r 3.25)
# The bay is not empty everywhere. A boss reaches WEB_DEPTH + BOSS_IN inboard of the rails, and at
# the tail's B end that lands inside tail_block, which owns the rear-tip standoff and the volume
# around it (measured: 37.7 mm³ of overlap with a station at t 49.4). So that one end carries its
# own keepout instead of the generic one, and the station moves forward onto a rung of its own.
END_KEEPOUT = {("tail", "b"): 28.0}
CABLE_D = 2.8          # the channel `captive` sinks into its mid rung to trap a lead
CABLE_CUT = 1.20       # how deep that channel goes, of the rung's WEB_DEPTH
CSK_ANGLE = 90.0
# THE TAP IS A THROUGH HOLE, not blind. A blind one left BLIND mm of floor under it, and that
# floor is a wall: rays read it at 0.60 mm against a 1.5 mm carcass floor, 150-200 of them per
# part. Opening it costs nothing - inboard of the boss is empty bay, so a screw that runs long
# simply stands proud into it - and it removes both the thin floor and the risk of splitting the
# boss by bottoming the screw.
BLIND = 0.00           # through-tapped: no floor left under the thread


def screw_of(p: dict) -> dict:
    return SCREW_SIZES[p.get("SCREW_SIZE", SCREW_SIZE)]


def boss_depth() -> float:
    """Socket floor to the boss's inboard face: the web's WEB_DEPTH less the socket sunk into it,
    plus BOSS_IN of boss standing inboard behind it."""
    return WEB_DEPTH - SOCKET_DEEP + BOSS_IN


def screw_engagement(p: dict) -> float:
    """Tapped thread actually available. The hole is blind: BLIND of material is left at the bottom
    so the boss cannot be split by bottoming the screw."""
    return boss_depth() - BLIND


def head_stack(p: dict) -> float:
    """Material the countersink has to sink into: the shell, the rebate it steps out by, and the
    socket. This is what makes a flat head finish flush without thickening the panel outward."""
    return SKIN_W + SCREW_PAD + REBATE + SOCKET_DEEP


def screw_stations(seg: Seg, p: dict) -> list[float]:
    """The t of every screw. The ALLOWED INTERVAL is worked out first and the stations are then
    placed inside it, rather than raw positions being clamped onto its ends - clamping put two of
    `clamped`'s four on the tail at the same t (33.378 twice), which is a duplicate boss and a
    variant that quietly ships three screws while its notes claim four.

    The interval respects, in order: the rails' own extent; the SKIN's extent plus a head radius
    and a wall, because a station on the skin's leading edge puts half the countersink over air;
    the clip bores at both ends; and any END_KEEPOUT, which exists because the bay is not empty -
    at the tail's B end a boss lands inside tail_block."""
    st0, st1 = seg.skin_t()
    edge = screw_of(p)["d_head"] / 2 + MATERIALS[MATERIAL]["wall"]
    lo = max(seg.t_start + BOSS_CLEAR_T, st0 + edge,
             END_KEEPOUT.get((seg.name, "a"), BORE_KEEPOUT))
    hi = min(seg.t_end - BOSS_CLEAR_T, st1 - edge,
             seg.L - END_KEEPOUT.get((seg.name, "b"), BORE_KEEPOUT))
    if hi < lo:
        lo = hi = (lo + hi) / 2
    plan = p.get("SCREW_PLAN", "ends")
    n = {"ends": 2, "spine": 3}.get(plan, 4)
    if n == 1 or hi - lo < 1e-9:
        raw = [(lo + hi) / 2]
    else:
        raw = [lo + (hi - lo) * i / (n - 1) for i in range(n)]
    return [round(t, 3) for t in raw]


def _boss_rung(seg: Seg, tc: float, p: dict) -> Part:
    """A short length of rung under a screw station that has no web or rung of its own, so every
    boss is backed by material tied to both rails rather than hanging off the shell."""
    half = screw_of(p)["boss_d"] / 2 + 1.4
    return _sz(_rung_xs(seg), tc - half, tc + half)


def screw_bosses(seg: Seg, p: dict) -> Part:
    """One cylindrical boss per station, standing INBOARD of the web. Its outer end is flush with
    the rails' outer plane, so nothing on the carcass stands proud of the face that prints on the
    bed - that flushness is the whole reason the boss is not simply extended out to the skin."""
    ro, sc = seg.rail_out, screw_of(p)
    out = Part()
    for tc in screw_stations(seg, p):
        out += cylinder_s(seg, tc, _BAND_MID, ro - WEB_DEPTH - BOSS_IN, ro, sc["boss_d"])
    return out


def screw_sockets(seg: Seg, p: dict) -> Part:
    """The counterbore the skin's spigot drops into, sunk SOCKET_DEEP below the rails' outer plane."""
    ro, sc = seg.rail_out, screw_of(p)
    out = Part()
    for tc in screw_stations(seg, p):
        out += cylinder_s(seg, tc, _BAND_MID, ro - SOCKET_DEEP, ro + 0.5,
                          sc["spigot_d"] + 2 * SPIGOT_CLEAR)
    return out


def screw_taps(seg: Seg, p: dict) -> Part:
    """The blind tapped holes, drilled from the socket floor inboard through the boss."""
    ro, sc = seg.rail_out, screw_of(p)
    floor = ro - SOCKET_DEEP
    out = Part()
    for tc in screw_stations(seg, p):
        out += cylinder_s(seg, tc, _BAND_MID, floor - screw_engagement(p) - 1.0, floor + 0.5,
                          sc["d_tap"])
    return out


def cable_channel(seg: Seg, p: dict) -> Part:
    """`captive` only: a half-round channel ALONG the segment, sunk into the carcass rung's outer
    face so the screw that retains the panel also traps a lead under it.

    It is cut into the CARCASS, not the skin, and the shell thickness is why: the skin is SKIN_W
    1.30 over the middle band and a Ø2.8 groove in it is a hole, which is exactly what the first
    attempt produced - 10 to 13 rays at 0.45 mm on every plain skin. The rung has WEB_DEPTH 3.6 to
    give, so a half-round sunk in it leaves 2.2 mm of rung and the skin simply caps the wire."""
    ro, sc = seg.rail_out, screw_of(p)
    stations = screw_stations(seg, p)
    tc = stations[len(stations) // 2]
    z = _BAND_MID - sc["spigot_d"] / 2 - CABLE_D / 2 - 0.8
    # A SQUARE trough, and every rounder shape was tried first and measured worse. A circle
    # centred on the rung's outer face is tangent to it and feathers the material either side to
    # nothing (23 rays at 0.26 mm); sinking that circle and squaring the mouth put the bottom
    # CABLE_D below the face instead of CABLE_D/2 and left 66 rays at 0.25. A rectangle CABLE_CUT
    # deep has no tangency anywhere, leaves WEB_DEPTH - CABLE_CUT of rung under the wire, and a
    # 2.8 mm square channel holds a 24 AWG lead just as well as a round one.
    half = RUNG_LEN / 2 - 0.5
    prof = _rect(ro - CABLE_CUT, z - CABLE_D / 2, ro + 1.0, z + CABLE_D / 2)
    return _sz(prof, tc - half, tc + half)


def skin_spigots(seg: Seg, p: dict) -> Part:
    """The skin's side of the joint: a plug that fills the socket, so the head has REBATE +
    SOCKET_DEEP of extra material behind it and the skin is located without relying on the screw."""
    ro, sc = seg.rail_out, screw_of(p)
    out = Part()
    for tc in screw_stations(seg, p):
        # The spigot runs PAST the shell's inner face rather than stopping on it. Two solids that
        # merely touch leave that face buried in the union and clean() will not lift a coincident
        # seam, so rays stopped there and read the spigot's 0.95 mm stand-off as the wall. An
        # overlap makes it one body with no internal face to stop on.
        out += cylinder_s(seg, tc, _BAND_MID, ro - SOCKET_DEEP + SPIGOT_CLEAR, ro + REBATE + 0.6,
                          sc["spigot_d"])
    return out


def screw_holes_skin(seg: Seg, p: dict, pad: float = 0.0) -> Part:
    """Clearance bore plus the 90 deg countersink, cut through the skin's middle band and spigot.

    `pad` is the shell's OWN extra thickness over the middle band (PAD, which the plain skins
    carry), and it has to be passed in: sinking the cone to a fixed depth left it 0.8 mm below the
    real outer face on a padded skin, and the ring of shell over it measured 1.01 mm."""
    ro, sc = seg.rail_out, screw_of(p)
    s_out = ro + REBATE + SKIN_W + SCREW_PAD + pad
    csk = (sc["d_head"] - sc["d_thru"]) / 2 / tan(radians(CSK_ANGLE / 2))
    out = Part()
    for tc in screw_stations(seg, p):
        out += cylinder_s(seg, tc, _BAND_MID, ro - SOCKET_DEEP - 1.0, s_out + 2.0, sc["d_thru"])
        out += cone_s(seg, tc, _BAND_MID, s_out - csk, s_out, sc["d_thru"], sc["d_head"])
        out += cylinder_s(seg, tc, _BAND_MID, s_out, s_out + 2.0, sc["d_head"])
    return out


def screwed(variant: str) -> bool:
    return bool(VARIANTS.get(variant or ASSEMBLY_VARIANT, {}).get("params", {}).get("SCREWED"))


# --- module tables ----------------------------------------------------------------------------
VARIANTS = {
    "plain": {"style": "carapace", "material": "PETG", "params": {"DECOR": False},
              "notes": "the system as build123d alone cuts it: the same carcass and the same six "
                       "skins, with the centre plain skin left at its CAD arc instead of being "
                       "swelled in Blender. Prints and fits identically; the flank is flatter."},
    "carapace": {"style": "carapace", "material": "PETG",
                 "notes": "the ARRIS reading: a ladder carcass that only the clips touch, plus six "
                          "swappable skins - three domed `plain` elytra and three `vented` flanks."},
    # --- the screwed family. Same carcass, same three segments, same swappable skins; the skin is
    # bolted flat instead of hooked and latched. Each of the three answers a different complaint.
    "bolted": {"style": "carapace", "material": "PETG",
               "params": {"SCREWED": True, "DECOR": False, "SCREW_PLAN": "ends"},
               "notes": "TWO SCREWS, one at each end web - the fewest fasteners that still hold a "
                        "skin flat, and the quickest of the three to service. It answers the "
                        "dovetail's one real weakness, which is that a hook and a snap latch can "
                        "both let go under impact, while keeping the panel count and the print "
                        "time unchanged. The middle of a long skin is unsupported between the two "
                        "screws, so this is the one to choose for the short front and tail "
                        "segments rather than for a drumming centre flank. You need a driver: "
                        "that is the trade against the latch, which released under a fingernail."},
    "clamped": {"style": "carapace", "material": "PETG",
                "params": {"SCREWED": True, "DECOR": False, "SCREW_PLAN": "spread",
                           "CUSP_SCALE": 1.30},
                "notes": "FOUR SCREWS spread along the skin, each on its own rung, plus skirts run "
                         "the full length so the shell lands on rail material everywhere instead "
                         "of only at its ends. This is the stiff, quiet one: a 1.3 mm PETG shell "
                         "pulled flat at four stations cannot drum against the carcass the way a "
                         "two-point skin can, and the continuous skirt stops the free edges "
                         "buzzing. It costs two more screws, two more rungs of carcass, and the "
                         "longest service time of the three. Its nose is raked 1.30 x the standard "
                         "cusp run-out, which is what tells it from `bolted` at a glance."},
    "captive": {"style": "carapace", "material": "PETG",
                "params": {"SCREWED": True, "DECOR": False, "SCREW_PLAN": "spine",
                           "CUSP_SCALE": 1.40},
                "notes": "THREE SCREWS on the spine - both end webs and the mid rung - and the "
                         "middle screw earns its place twice: it lands on the rung, which is the "
                         "one place a cable can be pinched between skin and carcass without "
                         "crossing a rail, so the same fastener that retains the panel also "
                         "carries the wiring run: the rung is the one place a lead can cross from "
                         "the bay to the flank without passing a rail, so the panel is fastened "
                         "where the cable already wants to go rather than pinning it at the ends. "
                         "Its nose carries the longest cusp of the three at 1.40, which is what "
                         "tells it from the other two in silhouette. Between `bolted` and "
                         "`clamped` in both stiffness and service time.\n"
                         "A moulded cable trough on that rung was designed, measured and DROPPED: "
                         "the Ø8.2 boss is wider than the 8.0 mm rung, so a trough crossing it "
                         "leaves a 0.25 mm web between trough and socket, and there is no room in "
                         "Z to move it - below the boss the rail band starts at 13.85. Cutting it "
                         "into the skin instead is worse: a Ø2.8 groove in a 1.30 mm shell is a "
                         "hole (10-13 rays at 0.45 mm). Route the lead along the rung and let the "
                         "skin cap it; do not re-cut the trough."},
}
ASSEMBLY_VARIANT = "carapace"


def decorates(variant: str) -> bool:
    """Whether this variant runs the Blender pass. The `plain` variant exists so the system still
    ships when Blender is unavailable or its gates refuse the dome."""
    return VARIANTS.get(variant or ASSEMBLY_VARIANT, {}).get("params", {}).get("DECOR", True)
# The assembly wears one skin per segment; the other three are the alternative, not a second layer.
ASSEMBLY_LABELS = (*CARCASS_LABELS,
                   *(skin_label(s, "plain" if s != "centre" else "vented", h)
                     for s in SEGMENT_NAMES for h in ("l", "r")))

PRINT = {}
for _s in SEGMENT_NAMES:
    _u = SEGS[_s].u
    _t = SEGS[_s].t
    for _h in ("l", "r"):
        _sgn = 1.0 if _h == "r" else -1.0
        PRINT[carcass_label(_s, _h)] = (round(_sgn * _u.X, 6), round(_u.Y, 6), 0.0)
        for _k in SKIN_KINDS:
            PRINT[skin_label(_s, _k, _h)] = (round(_sgn * _t.X, 6), round(_t.Y, 6), 0.0)

# Bridgeable downward faces, measured in PRINT coordinates (see overhangs()). Every one of these
# is a ledge a couple of millimetres across - far under PETG's 20 mm bridge limit - and each is
# declared with the face it covers, not as a blanket exemption:
#   carcass, 14.0 mm², span 3.0-3.6 mm, flat at print-Z 1.0: the clip-ring underside, one
#     millimetre off the bed, which the first layers bridge without ever drooping onto anything.
#   skin `plain`, 5.3 mm², span 1.2 mm at Z 38.8: the latch tongue's underside.
#   skin `vented`, 8.9 mm², normal.Z -0.87 rising off the bed over 3.4 mm: the run-out of the
#     lowest vent louvre, whose base is ON the bed; and 13.5 mm², span 3.2 mm at Z 70.6 on the
#     front skin: the top vent's lintel.
_BR_CARCASS = ("box", -6.0, -2.0, 0.5, 6.0, 6.0, 1.5)
# The screwed carcass adds one more, and only one: the SOCKET FLOOR. Each is a Ø5.1 disc of roof
# SOCKET_DEEP above the bed - an 18.2 mm² face spanning 5.1 mm, against PETG's 20 mm bridge limit -
# and there are two to four of them spread along the part, so the window is the part's whole length
# in plan but only the socket's own depth in Z. Nothing else on this carcass lies in that band.
_BR_SOCKET = ("box", -60.0, -60.0, SOCKET_DEEP - 0.3, 60.0, 60.0, SOCKET_DEEP + 0.3)
# and `captive` adds its cable trough's floor: one 19.6 mm² face spanning CABLE_D at CABLE_CUT
# above the bed, which is the same kind of short bridge as the socket and the clip-ring underside.
_BR_CABLE = ("box", -60.0, -60.0, CABLE_CUT - 0.3, 60.0, 60.0, CABLE_CUT + 0.3)
_BR_TONGUE = ("box", -5.0, -2.0, 38.0, 5.0, 2.0, 40.0)
_BR_LOUVRE = ("box", -4.0, -8.0, -0.1, 4.0, 1.0, 4.0)
_BR_LINTEL = ("box", -4.0, -14.0, 69.5, 4.0, -3.0, 71.5)
BRIDGE_OK = {
    **{carcass_label(s, h): (_BR_CARCASS, _BR_SOCKET, _BR_CABLE) for s in SEGMENT_NAMES for h in ("l", "r")},
    **{skin_label(s, "plain", h): (_BR_TONGUE, _BR_LOUVRE, _BR_LINTEL)
       for s in SEGMENT_NAMES for h in ("l", "r")},
    **{skin_label(s, "vented", h): (_BR_TONGUE, _BR_LOUVRE, _BR_LINTEL)
       for s in SEGMENT_NAMES for h in ("l", "r")},
}

MOUNTS = {
    **{carcass_label(s, h): (
        f"standoff_{AXIS_OF[s][0][9:-6]}_{'right' if h == 'r' else 'left'} Ø6 shaft, "
        f"270 deg C-clip bore Ø{D_CLIP_BORE} over Z {SEGMENTS[s]['clip_a'][0]}-{SEGMENTS[s]['clip_a'][1]}",
        f"standoff_{AXIS_OF[s][1][9:-6]}_{'right' if h == 'r' else 'left'} Ø6 shaft, "
        f"270 deg C-clip bore Ø{D_CLIP_BORE} over Z {SEGMENTS[s]['clip_b'][0]}-{SEGMENTS[s]['clip_b'][1]}",
        "no plate contact at all: the whole ladder lives in Z 9.25-33.75, 0.25 mm clear of the "
        "plate_mid top face and 0.25 mm clear of the plate_top underside")
       for s in SEGMENT_NAMES for h in ("l", "r")},
    **{skin_label(s, k, h): (
        f"side_carcass_{s}_{h}: the two dovetail rails (hook engagement {HOOK_REACH} mm in s, "
        f"{HOOK_TIP} mm thick at the tip, {CLEAR} mm clearance)",
        f"side_carcass_{s}_{h}: the mid-rung latch pocket ({LATCH_DEEP} mm deep)",
        "no frame contact")
       for s in SEGMENT_NAMES for k in SKIN_KINDS for h in ("l", "r")},
}
HARDWARE = {
    **{carcass_label(s, h): ("none - two 270 deg C-clips snapped onto the Ø6 standoffs, pushed INBOARD",)
       for s in SEGMENT_NAMES for h in ("l", "r")},
    **{skin_label(s, k, h): (f"none - dovetail slide plus the {LATCH_TAB} mm snap latch",)
       for s in SEGMENT_NAMES for k in SKIN_KINDS for h in ("l", "r")},
}
NOTES = {
    **{carcass_label(s, h): (
        "Snap-on: hold the ladder about 8 mm OUTBOARD of its seat and push it INBOARD. Both mouths "
        "face inboard, so the standoffs enter from the inboard side and a side impact loads the "
        "closed outboard half of each ring rather than walking the standoffs out through the mouths. "
        "Nothing here touches a plate: the whole ladder lives in Z 9.25-33.75.")
       for s in SEGMENT_NAMES for h in ("l", "r")},
    **{skin_label(s, k, h): (
        "Slides on from the REAR, forwards along the rails, until the latch tab drops into the mid "
        "rung's pocket. To take it off, hook a nail through the finger window, lift the tongue "
        f"{LATCH_LIFT} mm to free the tab and pull the skin rearward. Service order is tail first, "
        "then centre, then front - consecutive skins overlap the segment behind them.")
       for s in SEGMENT_NAMES for k in SKIN_KINDS for h in ("l", "r")},
}

_P: dict = {}                  # the params the last build() actually used, so checks() sees them
_BASE: dict[str, Part] = {}    # the undecorated functional solids: min_wall is only valid on these
_INFO: dict[tuple[str, str], dict] = {}
_CARC: dict[str, Part] = {}    # the right-hand carcass per segment, for the skins' own checks


def _pair_lr(part: Part, rlab: str, llab: str) -> dict[str, Part]:
    """The right-hand part and its exact mirror. A mirrored pair carries no suture: the pair IS the
    split (CN-1), which is why nothing in this module cuts one."""
    right = deepcopy(part)
    right.label = rlab
    left = part.mirror(Plane.YZ)
    left.label = llab
    return {rlab: right, llab: left}


def build(variant: str = "carapace", **overrides) -> dict[str, Part]:
    p = dict(M2=M2_BACKUP, DECOR=decorates(variant))
    p.update(VARIANTS.get(variant or ASSEMBLY_VARIANT, {}).get("params", {}))
    p.update(overrides)
    _P.clear()
    _P.update(p)
    out: dict[str, Part] = {}
    for name in SEGMENT_NAMES:
        seg = SEGS[name]
        carc = build_carcass(seg, p).moved(seg.loc)
        _CARC[name] = carc
        _BASE[carcass_label(name, "r")] = carc
        out.update(_pair_lr(carc, carcass_label(name, "r"), carcass_label(name, "l")))
        for kind in SKIN_KINDS:
            decor = name == "centre" and kind == "plain" and p["DECOR"]
            skin, info = build_skin(seg, kind, p, defer_mating=decor)
            skin = skin.moved(seg.loc)
            _INFO[(name, kind)] = info
            if decor:
                # The mating cuts are held back so the Blender pass meshes a connected body, then
                # applied in B-rep on the way out (`mating_cuts`). `_BASE` is the functional solid
                # the wall checks measure, so it gets them cut the ordinary way.
                mating = mating_cuts(seg, p).moved(seg.loc)
                _BASE[skin_label(name, kind, "r")] = skin - mating
                skin = _decorate_centre(skin, seg, variant, mating)
            else:
                _BASE[skin_label(name, kind, "r")] = skin
            out.update(_pair_lr(skin, skin_label(name, kind, "r"), skin_label(name, kind, "l")))
    return out


# --- measuring the wall without offset_3d -----------------------------------------------------
# `_fit.min_wall` erodes with OCCT's offset_3d, and on these solids offset_3d does not fail - it
# SEGFAULTS the interpreter (measured on the front plain skin: exit 139, no Python traceback, so it
# cannot even be caught). The carcass is no better: there the offset collapses and min_wall silently
# drops to its ray fallback, which then reports the c_clip lips as 0.10 mm.
#
# So the wall is measured twice, by two methods that need no 3D offset, and BOTH have to pass:
#   1. a 2D opening on the part's own cross-sections. Every part here is a prism along one local
#      axis, so a 2D erode/dilate of the section IS the exact wall measurement for it - including
#      the knife-edge tips that _fit's own docstring says ray sampling cannot see.
#   2. `_fit.ray_thickness` on the finished 3D solid, which catches anything the sections miss
#      (the tab, the cusp run-out, the bore bites).
# OCCT WILL NOT OFFSET THESE SECTIONS. Every union of two overlapping rectangles in here - the web,
# the rung, the shell and its hooks - made `offset(sk, -t/2)` raise RuntimeError outright (10 of the
# 18 parts, measured; rebuilding each face from its outer wire and cleaning it first does not help,
# checked strategy by strategy). So the 2D measurement is done the way `_fit.ray_thickness` does the
# 3D one, with no offset anywhere in it: chop every boundary wire into ~WALL_2D_STEP chords, and from
# each chord's midpoint shoot a ray straight into the material and measure the distance to the far
# side of the section. The threshold is untouched - 1.5 on the carcass, 1.2 on the skins.
#
# A perpendicular ray reads a 90 deg corner correctly (the neighbouring edge is parallel to the ray,
# so it is never hit) and reads an ACUTE corner as the knife edge it is, which is exactly the class of
# defect the old offset test existed to catch.
WALL_2D_STEP = 1.1        # mm between ray origins along a section boundary
WALL_2D_TOL = 1e-3
WALL_2D_OPPOSED = 0.7071   # cos 45 deg: a hit face steeper than this to the ray bounds a corner, not a wall


def _chords(sk: Sketch, step: float = WALL_2D_STEP) -> list:
    """Every boundary of `sk` chopped into ~`step` mm chords, each carrying the unit normal that
    points INTO the material: (mx, my, nx, ny, a, b). The material side is settled once per wire by
    a majority of point-in-section tests, never per chord, so one degenerate chord cannot flip it."""
    raw = []
    for f in sk.faces():
        for w in (f.outer_wire(), *f.inner_wires()):
            grp = []
            for e in w.edges():
                n = max(2, int(e.length / step) + 1)
                pts = [e @ (i / n) for i in range(n + 1)]
                grp += [((u.X, u.Y), (v.X, v.Y)) for u, v in zip(pts, pts[1:])
                        if hypot(v.X - u.X, v.Y - u.Y) > 1e-9]
            if grp:
                raw.append(grp)
    flat = [c for grp in raw for c in grp]
    out = []
    for grp in raw:
        votes = 0
        for i in range(0, len(grp), max(1, len(grp) // 5)):
            (ax, ay), (bx, by) = grp[i]
            L = hypot(bx - ax, by - ay)
            nx, ny = -(by - ay) / L, (bx - ax) / L
            mx, my = (ax + bx) / 2, (ay + by) / 2
            votes += 1 if _pip(flat, mx + nx * 1e-3, my + ny * 1e-3) else -1
        side = 1.0 if votes > 0 else -1.0
        for (ax, ay), (bx, by) in grp:
            L = hypot(bx - ax, by - ay)
            nx, ny = -(by - ay) / L * side, (bx - ax) / L * side
            out.append(((ax + bx) / 2, (ay + by) / 2, nx, ny, (ax, ay), (bx, by)))
    return out


def _pip(chords, x: float, y: float) -> bool:
    """Even-odd point-in-section test on a list of ((x0, y0), (x1, y1)) chords."""
    c = False
    for (x0, y0), (x1, y1) in chords:
        if (y0 > y) != (y1 > y) and x0 + (y - y0) * (x1 - x0) / (y1 - y0) > x:
            c = not c
    return c


def _shoot(chords, px: float, py: float, dx: float, dy: float, skip: float) -> float | None:
    """Distance from (px, py) along (dx, dy) to the nearest OPPOSED boundary - a chord whose own
    inward normal faces back down the ray within WALL_2D_OPPOSED. That qualifier is the whole
    difference between a wall and a chamfer: the rail is a 3.6 x 6.0 mm solid bar with a 33 deg
    dovetail flare on each corner, and a bare perpendicular ray from its inner face reads the flare
    as 1.16 mm of 'wall'. It is not a wall - it is a corner, and nothing is thin there. Only faces
    roughly parallel to the one the ray leaves bound a wall."""
    best = None
    for _mx, _my, nx, ny, (x0, y0), (x1, y1) in chords:
        if nx * dx + ny * dy > -WALL_2D_OPPOSED:
            continue
        ex, ey = x1 - x0, y1 - y0
        det = dx * ey - dy * ex
        if -1e-12 < det < 1e-12:
            continue
        qx, qy = x0 - px, y0 - py
        t = (qx * ey - qy * ex) / det
        if t <= skip or (best is not None and t >= best):
            continue
        u = (qx * dy - qy * dx) / det
        if -1e-9 <= u <= 1 + 1e-9:
            best = t
    return best


def wall_2d(sk: Sketch, t: float, name: str = "", allow: tuple = ()) -> tuple[bool, str]:
    """Minimum-wall test on a 2D section by opposed-face ray sampling. `allow` is a tuple of
    Sketches naming DECLARED thin features (the dovetail hook wedges); a sample whose ray starts
    inside one is skipped and the count is reported, exactly as `_fit.ray_thickness(allow=...)`
    does in 3D. The threshold itself is never relaxed."""
    chords = _chords(sk)
    if not chords:
        return False, f"{name}: empty section"
    skips = [[(c[4], c[5]) for c in _chords(a)] for a in allow]
    worst, thin, total, where = 1e9, 0, 0, None
    skip = min(0.05, t / 20)
    for mx, my, dx, dy, _a, _b in chords:
        if any(_pip(g, mx + dx * 0.02, my + dy * 0.02) for g in skips):
            continue
        h = _shoot(chords, mx + dx * 1e-5, my + dy * 1e-5, dx, dy, skip)
        if h is None:
            continue
        total += 1
        if h < t - WALL_2D_TOL:
            thin += 1
            if h < worst:
                worst, where = h, (round(mx, 2), round(my, 2))
    if not total:
        return False, f"{name}: no usable section rays"
    if thin:
        return False, (f"{name}: {thin}/{total} section rays thinner than {t} mm, "
                       f"worst {worst:.3f} mm at {where}")
    return True, (f"{name}: {total} opposed-face section rays, none thinner than {t} mm"
                  + (f"; {len(skips)} declared thin region(s) skipped" if skips else ""))


def ray_solid(part: Part, t: float, what: str = "", allow: tuple = ()) -> tuple[bool, str]:
    """The 3D half of the wall measurement: `_fit.ray_thickness` on the finished solid, which
    catches whatever a cross-section cannot see (the latch tab, the cusp run-out, the bore bites).
    It needs no offset - offset_3d SEGFAULTS on these shells, which is why min_wall() is not used.

    `allow` names the SAME declared thin features the 2D row names (see `hook_wedges`), so the two
    halves of the measurement agree about what a dovetail is. Without it the 2D row passes the four
    flare wedges as declared and the 3D row reports the identical 0.4 mm rail tip as a defect - 108
    of the front carcass's 1345 rays, every one of them on a flare face or a band edge at z 9.25,
    15.25, 27.75 or 33.75. Everything outside the wedges is still measured against the full floor."""
    thin, worst, detail = ray_thickness(part, t, allow=allow)
    return (not thin), f"{what}: {detail}" if what else detail


def hook_wedges(seg: Seg) -> Sketch:
    """The four dovetail wedges - BOTH halves of them - as an (s, z) region, DECLARED thin.

    A dovetail is a wedge on each side of its own flare: the rail's land narrows from RAIL_T to
    RAIL_T - FLARE_D over the DT it takes the flare to run out, and the skin's hook is the negative
    of it, HOOK_TIP thick at its tip. Both are thick in the direction they are LOADED and the
    direction they are PRINTED (across the rail band, 1.25 mm and up, several perimeters at a 0.4
    nozzle), and both are thin measured PERPENDICULAR to the 33 deg flare face, where the tip reads
    HOOK_TIP * cos(33.3 deg) = 1.04 mm and the rail's bottom land reads 0.4 mm at the band edge.
    That is what a dovetail is. Naming the four wedges is the honest way to say so; lowering the
    1.2 / 1.5 floors to hide them would not be, and everything outside these four bands is still
    measured against the full threshold."""
    ro = seg.rail_out
    ri = ro - RAIL_T
    out = Sketch()
    # No padding on the MIDDLE-band side of either band: a 0.05 mm overhang there slices a 0.05 mm
    # sliver off any bridge whose clip window ends flush with a band edge, and the tail's B window
    # ends at Z 27.75, which is RAIL_TOP[0] to the micron.
    for z0, z1 in (RAIL_BOT, RAIL_TOP):
        out += _rect(ri - 0.05, z0 - 0.05, ro + CLEAR + 0.05, z0 + DT)
        out += _rect(ri - 0.05, z1 - DT, ro + CLEAR + 0.05, z1 + 0.05)
    return out


def dovetail_allow(seg: Seg) -> tuple[Part, ...]:
    """`hook_wedges` as a solid in FRAME coordinates, for `ray_solid(allow=...)`: the four dovetail
    wedges swept the whole length of the segment. One definition, two measurements."""
    return (_sz(hook_wedges(seg), -RELIEF_R - 2.0, seg.L + 2.0).moved(seg.loc),)


def sections_of(seg: Seg, kind: str | None, p: dict) -> list[tuple[str, Sketch]]:
    """The cross-sections that carry this part's walls. `kind` None = the carcass."""
    ro = seg.rail_out
    if kind is None:
        r0, lip = rung_t0(seg), MOUTH / 2 + CLIP_WALL
        (a0, a1), (b0, b1) = seg.webs()
        rails = rail_pair(ro)
        web = rails + _web_xs(seg)
        rung = rails + _rung_xs(seg)
        # the clip band in plan (t, s): a closed annulus, no mouth and no lips to square off
        ring = Pos(0.0, 0.0) * Circle(RING_R) - Pos(0.0, 0.0) * Circle(D_CLIP_BORE / 2)
        # The latch window is a hole in the rung's FLANK, so it is measured in (t, z), where its
        # ligaments actually live: LATCH_WIN[0] of rung ahead of it, RUNG_LEN - LATCH_WIN[1] behind
        # it, and MID[0] - 0.8 .. LATCH_Z[0] of rung under it.
        rung_tz = (_rect(seg.t_start, RAIL_BOT[0], seg.t_end, RAIL_BOT[1])
                   + _rect(seg.t_start, RAIL_TOP[0], seg.t_end, RAIL_TOP[1])
                   + _rect(r0, MID[0] - DT, r0 + RUNG_LEN, MID[1] + DT)) - latch_window_sk(seg)
        return [("rails (s, z)", rails, ()), ("end web (s, z)", web, ()),
                ("mid rung (s, z)", rung, ()),
                ("closed clip ring (t, s)", ring, ()),
                ("mid rung + latch window (t, z)", rung_tz, ())]
    sc = bool(p.get("SCREWED"))
    rise = RISE[seg.name] if kind == "plain" else 0.0
    pad = (PAD[seg.name] if kind == "plain" else 0.0) + (SCREW_PAD if sc else 0.0)
    xs = skin_profile(seg, rise, pad, screwed_skin=sc)
    elev = elevation(seg, kind, p)
    ap, n, _how = apertures(seg, kind, p)
    holed = (elev - ap - equipment(seg, kind)) if n or kind == "vented" else elev
    # A screwed shell has no hook, so there is no wedge to declare as an intentional thin tip.
    return [("shell + hooks (s, z)" if not sc else "flat-backed shell (s, z)", xs,
             () if sc else (hook_wedges(seg),)),
            ("flank outline and its apertures (t, z)", holed, ())]


# --- checks ------------------------------------------------------------------------------------
STACK_40 = box(-20.0, -20.0, 12.0, 20.0, 20.0, 31.0)   # the 40 x 40 stack envelope, Z 12-31
ARM_BOLT_HEADS = ((26.97, 18.17), (26.43, -19.63))     # Ø6 x 3 heads on plate_mid, right side
SIBLINGS = ("camera_pod", "tail_block", "gps_mount", "rx_antenna_v_holder")
_SIB: dict | None = None


def _siblings() -> tuple[dict[str, Part], list[str]]:
    """The installed neighbours this system has to share the frame with, built once. A sibling that
    cannot be built right now is NAMED in the row rather than silently dropped."""
    global _SIB
    if _SIB is None:
        import importlib
        got, missed = {}, []
        for mod_name in SIBLINGS:
            try:
                mod = importlib.import_module(f"tigerbee.accessories.{mod_name}")
                from tigerbee.accessories import build_accessory, variant_names
                for v in variant_names(mod)[:1]:
                    for lab, part in build_accessory(mod, v).items():
                        got[lab] = part
            except Exception as exc:  # noqa: BLE001 - a sibling in flux must not fail this module
                missed.append(f"{mod_name} ({type(exc).__name__})")
        _SIB = (got, missed)
    return _SIB


def _prop_margin(part: Part) -> tuple[float, str]:
    """How much room is left to the nearest prop keep-out cylinder. `prop_disc_violation` answers
    yes/no; this answers 'by how much', which is the number that sets the tail's whole geometry."""
    best, who = 1e9, ""
    for name, disc in prop_discs().items():
        d = part.distance_to(disc)
        if d < best:
            best, who = d, name
    return round(best, 3), who


def _outline_exceptions(seg: Seg, pad: float) -> tuple[list[str], list[str]]:
    """Samples along this segment's outer line that are NOT outside a plate outline in plan, split
    into (plate_mid, plate_top). plate_mid has to be clean: it is the plate this system stands over,
    and anything of ours inside its outline would be in the way of a bolt or a lead. plate_top's
    lobes are a different matter - they are 0.25 mm above the top rail and are passed UNDER, which is
    the only thing the prop discs leave room for (see PLATE_TAB_NOTE)."""
    mid, top = [], []
    for i in range(7):
        t = SKIN_FRONT + (seg.L - SKIN_FRONT) * i / 6.0
        for s_off, what in ((seg.rail_out, "rail"), (seg.rail_out + REBATE + SKIN_W + pad, "skin")):
            x, y = seg.xy(t, s_off)
            for plate, into in (("plate_mid", mid), ("plate_top", top)):
                spans = outline_spans(plate, y)
                if any(lo - 0.3 <= abs(x) <= hi + 0.3 for lo, hi in spans):
                    into.append(f"{what} y {y:.1f} x {x:.2f} in {spans}")
    return mid, top


def _hook_probe(seg: Seg) -> Part:
    """The volume inboard of the rail plane inside the two rail bands: whatever skin material is in
    here IS the four dovetail hooks, so its volume is the engagement."""
    inner = seg.rail_out - HOOK_REACH - 0.25
    sk = (_rect(inner, RAIL_BOT[0], seg.rail_out, RAIL_BOT[1])
          + _rect(inner, RAIL_TOP[0], seg.rail_out, RAIL_TOP[1]))
    t0, t1 = seg.skin_t()
    return _sz(sk, t0, t1 + 0.5).moved(seg.loc)


def checks(parts: dict[str, Part], frame: dict[str, Part], variant: str = "") -> list[tuple[str, bool, str]]:
    """ONE checks() for the whole system. Every row is run per segment, and the skins' rows are run
    on the right-hand part with a mirror-equality row standing in for the left, so a failure on one
    flank cannot hide behind the other."""
    out: list[tuple[str, bool, str]] = []
    cyls = standoff_cylinders()
    rigid = {n: pt for n, pt in frame.items() if not n.startswith("standoff")}
    sib, missed = _siblings()

    if decorates(variant):
        out += BL.decor_checks(f"side_skin_centre_plain_r__{variant}" if variant else
                               "side_skin_centre_plain_r__carapace")
    else:
        out.append(("decor: none by design (the `plain` variant is build123d only)", True,
                    "the centre plain skin keeps its CAD arc; no Blender pass to gate"))
    st = S.STYLES["carapace"]
    out.append((f"style {st.name}: free-edge fillet within 0.45 x wall",
                S.edge_radius(st, "free", SKIN_W) <= 0.45 * SKIN_W + 1e-9,
                f"{S.edge_radius(st, 'free', SKIN_W)} mm on a {SKIN_W} mm shell"))
    out.append(("mirrored pair, so no suture is cut anywhere (CN-1)",
                all(S.suture_present(parts[lab], -95.0, 110.0, Z_HI)[0] for lab in
                    (carcass_label("centre", "r"), skin_label("centre", "plain", "r"))),
                "the pair IS the split; a suture on X=0 would be a second one"))
    out.append(("every sibling accessory built into the interference check", not missed,
                f"{len(sib)} neighbour part(s) checked" + (f"; could not build {missed}" if missed else "")))

    for name in SEGMENT_NAMES:
        seg = SEGS[name]
        carc_r, carc_l = parts[carcass_label(name, "r")], parts[carcass_label(name, "l")]
        pre = f"{name} carcass"

        for tc, cz0, cz1, axis in seg.clips():
            for hand, part in (("right", carc_r), ("left", carc_l)):
                xy = STANDOFF_XY[axis if hand == "right" else axis.replace("_right", "_left")]
                ok, detail = coaxial(part, xy, D_CLIP_BORE, cz0 + 0.25, cz1 - 0.25)
                out.append((f"{pre} {hand}: clip bore coaxial with {axis.replace('_right', '')}"
                            f"_{hand}", ok, detail))
            d = carc_r.distance_to(cyls[axis])
            out.append((f"{pre}: Ø{STANDOFF_D} gap at {axis}", abs(d - STANDOFF_FIT) <= 0.06,
                        f"{d:.4f} mm (designed {STANDOFF_FIT})"))
            out.append((f"{pre}: clip window Z {cz0}-{cz1} inside the band {Z_LO}-{Z_HI}",
                        Z_LO - 1e-9 <= cz0 and cz1 <= Z_HI + 1e-9, f"{cz0}-{cz1}"))

        bb = carc_r.bounding_box()
        out.append((f"{pre}: every rail inside Z {Z_LO}-{Z_HI}",
                    bb.min.Z >= Z_LO - 1e-6 and bb.max.Z <= Z_HI + 1e-6,
                    f"Z {bb.min.Z:.3f}-{bb.max.Z:.3f}"))
        out.append((f"{pre}: outer face {seg.rail_out - STANDOFF_D / 2:.2f} mm outside the "
                    f"Ø{STANDOFF_D} standoff surface",
                    seg.rail_out - STANDOFF_D / 2 >= 1.7,
                    f"rail_out {seg.rail_out}" + (" - the rear prop disc caps the tail at 4.90"
                                                  if name == "tail" else " (spec band 3-4 mm)")))
        v = isect(carc_r, FC_STACK) + isect(carc_r, STACK_40)
        out.append((f"{pre}: clear of the FC stack envelopes", v < EPS, f"{v:.3f} mm³"))
        heads = Part()
        for hx, hy in ARM_BOLT_HEADS:
            heads += cylinder(hx, hy, Z_MID_TOP, Z_MID_TOP + 3.0, 6.0)
        v = isect(carc_r, heads)
        out.append((f"{pre}: clear of the arm-root bolt heads Ø6 x 3", v < EPS, f"{v:.3f} mm³"))
        hits = [(n, round(isect(carc_r, pt), 3)) for n, pt in sib.items()
                if bbox_overlap(carc_r, pt) and isect(carc_r, pt) > EPS]
        out.append((f"{pre}: clear of every sibling accessory", not hits, f"{hits or 'none'}"))
        margin, who = _prop_margin(carc_r)
        out.append((f"{pre}: outside the prop keep-out discs",
                    prop_disc_violation(carc_r) < EPS, f"{margin} mm to {who}"))
        wall = MATERIALS[MATERIAL]["wall"]
        for what, sk, allow in sections_of(seg, None, _P):
            ok_w, detail = wall_2d(sk, wall, what, allow)
            out.append((f"{pre}: min wall >= {wall} on the {what} section", ok_w, detail))
        ok_r, detail = ray_solid(carc_r, wall, "carcass", allow=dovetail_allow(seg))
        out.append((f"{pre}: min wall >= {wall} by per-face rays on the solid", ok_r, detail))
        ok_s, detail = single_solid(carc_r)
        out.append((f"{pre}: one solid", ok_s, detail))
        out.append((f"{pre}: left is the exact mirror", abs(carc_l.volume - carc_r.volume) < 0.01,
                    f"Δ {abs(carc_l.volume - carc_r.volume):.6f} mm³"))
        mid_bad, top_bad = _outline_exceptions(seg, PAD[name] + RISE[name])
        out.append((f"{pre}: outside the plate_mid outline in plan", not mid_bad,
                    f"{mid_bad or 'every sample outboard of the mid plate'}"))
        out.append((f"{pre}: {len(top_bad)} sample(s) pass under a plate_top lobe, with zero overlap",
                    isect(carc_r, frame["plate_top"]) < EPS,
                    f"{top_bad or 'none'}; {PLATE_TAB_NOTE}" if top_bad else "outside it in plan too"))
    return out + _skin_checks(parts, rigid, cyls, sib)


SWEEP, SWEEP_STEP = 15.0, 1.0
LIFT, LIFT_STEP = 12.0, 1.0       # the screwed skin's release: straight out along the screw axis


def _screw_checks(seg: Seg, pre: str, skin: Part, carc: Part, probe: dict) -> list[tuple[str, bool, str]]:
    """The screwed joint, measured rather than asserted: the thread is really there, the head
    really finishes below the surface, the boss really has wall around it, and the skin really
    comes off along the screw axis with the carcass still on its standoffs."""
    out: list[tuple[str, bool, str]] = []
    p, sc = _P, screw_of(_P)
    ro, zc = seg.rail_out, _BAND_MID
    stations = screw_stations(seg, p)
    eng = screw_engagement(p)
    s_out = ro + REBATE + SKIN_W + SCREW_PAD
    csk = (sc["d_head"] - sc["d_thru"]) / 2 / tan(radians(CSK_ANGLE / 2))

    floor = ro - SOCKET_DEEP
    bad_tap, bad_thru, bad_spig, wall_min = [], [], [], 1e9
    for tc in stations:
        tap = cylinder_s(seg, tc, zc, floor - eng + 0.05, floor - 0.05,
                         sc["d_tap"] - 0.05).moved(seg.loc)
        if isect(carc, tap) > EPS:
            bad_tap.append(round(tc, 2))
        thru = cylinder_s(seg, tc, zc, floor + 0.05, s_out - csk - 0.05,
                          sc["d_thru"] - 0.05).moved(seg.loc)
        if isect(skin, thru) > EPS:
            bad_thru.append(round(tc, 2))
        # the spigot really occupies its socket: material in the annulus between bore and spigot OD
        spig = (cylinder_s(seg, tc, zc, floor + 0.2, ro - 0.1, sc["spigot_d"] - 0.1)
                - cylinder_s(seg, tc, zc, floor, ro, sc["d_thru"] + 0.1)).moved(seg.loc)
        if isect(skin, spig) < 2.0:
            bad_spig.append(round(tc, 2))
        ring = (cylinder_s(seg, tc, zc, floor - 2.0, floor - 0.2, sc["boss_d"] - 0.2)
                - cylinder_s(seg, tc, zc, floor - 2.0, floor, sc["d_tap"] + 0.1)).moved(seg.loc)
        wall_min = min(wall_min, isect(carc, ring))

    out.append((f"{pre}: {len(stations)} tapped hole(s) clear through {eng:.1f} mm of boss",
                not bad_tap, f"stations {[round(t, 1) for t in stations]}; "
                             f"{'blocked at ' + str(bad_tap) if bad_tap else 'every thread open'}"))
    out.append((f"{pre}: every clearance bore open through the skin", not bad_thru,
                f"Ø{sc['d_thru']} thru; {bad_thru or 'all clear'}"))
    out.append((f"{pre}: every spigot seated in its socket", not bad_spig,
                f"Ø{sc['spigot_d']} spigot in a Ø{sc['spigot_d'] + 2 * SPIGOT_CLEAR} socket "
                f"{SOCKET_DEEP} deep; {bad_spig or 'all seated'}"))
    out.append((f"{pre}: boss carries material round every thread",
                wall_min > 8.0, f"{wall_min:.1f} mm³ in the Ø{sc['boss_d']} collar, "
                                f"wall {(sc['boss_d'] - sc['d_tap']) / 2:.2f} mm"))
    out.append((f"{pre}: thread engagement >= {sc['min_eng']} mm ({p.get('SCREW_SIZE', SCREW_SIZE)})",
                eng >= sc["min_eng"] - 1e-9,
                f"{eng:.2f} mm = web {WEB_DEPTH} - socket {SOCKET_DEEP} + boss {BOSS_IN} "
                f"- blind {BLIND}"))
    under = head_stack(p) - csk
    out.append((f"{pre}: countersunk head finishes flush or below the outer face",
                under >= MATERIALS[MATERIAL]["wall"] - 1e-9,
                f"{csk:.2f} mm of {CSK_ANGLE:.0f} deg countersink in a {head_stack(p):.2f} mm "
                f"stack (shell {SKIN_W} + rebate {REBATE} + socket {SOCKET_DEEP}) leaves "
                f"{under:.2f} mm under the head"))

    blocked, worst = [], 0.0
    for step in range(1, int(LIFT / LIFT_STEP) + 1):
        moved = skin.moved(Location(seg.u * (step * LIFT_STEP)))
        for n, pt in probe.items():
            if bbox_overlap(moved, pt):
                v = isect(moved, pt)
                if v > EPS:
                    blocked.append((step, n, round(v, 3)))
                worst = max(worst, v)
    out.append((f"{pre}: lifts straight off along the screw axis, {LIFT:.0f} x {LIFT_STEP:.0f} mm "
                f"outboard, carcass still on its standoffs", not blocked,
                f"{blocked[:4] or 'clear of frame, carcass and standoffs'}; worst {worst:.4f} mm³"))
    return out


def _skin_checks(parts, rigid, cyls, sib) -> list[tuple[str, bool, str]]:
    out: list[tuple[str, bool, str]] = []
    for name in SEGMENT_NAMES:
        seg = SEGS[name]
        carc = _CARC[name]
        probe = {"own carcass": carc, f"{seg.axis_a}": cyls[seg.axis_a],
                 f"{seg.axis_b}": cyls[seg.axis_b],
                 "plate_mid": rigid["plate_mid"], "plate_top": rigid["plate_top"]}
        areas = {}
        for kind in SKIN_KINDS:
            skin = parts[skin_label(name, kind, "r")]
            left = parts[skin_label(name, kind, "l")]
            base = _BASE[skin_label(name, kind, "r")]
            info = _INFO[(name, kind)]
            pre = f"{name} {kind} skin"
            areas[kind] = elevation(seg, kind, _P).area

            v = isect(skin, carc)
            out.append((f"{pre}: seated on its carcass with no interference", v < EPS,
                        f"{v:.4f} mm³ at {CLEAR} mm designed clearance"))

            if _P.get("SCREWED"):
                out += _screw_checks(seg, pre, skin, carc, probe)
            else:
                eng = isect(skin, _hook_probe(seg))
                out.append((f"{pre}: dovetail hooks engaged (volume inboard of the rail plane)",
                            eng > 40.0, f"{eng:.1f} mm³ of hook in the undercut, reach {HOOK_REACH} mm, "
                                        f"tip {HOOK_TIP} mm"))
                tab, pocket = latch_tab(seg).moved(seg.loc), latch_pocket(seg).moved(seg.loc)
                inside = isect(tab, pocket) / max(tab.volume, 1e-9)
                bite = isect(skin.moved(Location(seg.t * 1.0)), carc)
                out.append((f"{pre}: latch engaged and it bites",
                            inside > 0.92 and bite > EPS,
                            f"{inside:.3f} of the tab inside the pocket; {bite:.2f} mm³ of the tab fouls "
                            f"the rung after 1.0 mm of rearward travel, which is the snap"))

                released = skin - tongue_lift(seg).moved(seg.loc)
                blocked, worst = [], 0.0
                for step in range(1, int(SWEEP / SWEEP_STEP) + 1):
                    moved = released.moved(Location(seg.t * (step * SWEEP_STEP)))
                    for n, pt in probe.items():
                        if bbox_overlap(moved, pt):
                            v = isect(moved, pt)
                            if v > EPS:
                                blocked.append((step, n, round(v, 3)))
                            worst = max(worst, v)
                out.append((f"{pre}: removal sweep {SWEEP:.0f} x {SWEEP_STEP:.0f} mm rearward, latch "
                            f"released (tongue lifted {LATCH_LIFT} mm)", not blocked,
                            f"{blocked[:4] or 'clear of frame, carcass and standoffs'}; worst {worst:.4f} mm³"))

            gaps = {n: round(skin.distance_to(c), 4) for n, c in cyls.items() if bbox_overlap(skin, c, 2.0)}
            close = {n: d for n, d in gaps.items() if d < STANDOFF_FIT - 0.05}
            out.append((f"{pre}: >= {STANDOFF_FIT - 0.05} mm to every Ø{STANDOFF_D} standoff",
                        not close, f"{gaps or 'none within 2 mm'}"))
            hits = [(n, round(isect(skin, pt), 3)) for n, pt in sib.items()
                    if bbox_overlap(skin, pt) and isect(skin, pt) > EPS]
            out.append((f"{pre}: clear of every sibling accessory", not hits, f"{hits or 'none'}"))
            v = isect(skin, FC_STACK) + isect(skin, STACK_40)
            out.append((f"{pre}: clear of the FC stack envelopes", v < EPS, f"{v:.3f} mm³"))
            margin, who = _prop_margin(skin)
            out.append((f"{pre}: outside the prop keep-out discs", prop_disc_violation(skin) < EPS,
                        f"{margin} mm to {who}"))

            if name == "front":
                cone = Part()
                for a in (CAM_TILT_RANGE[0], 20.0, CAM_TILT_RANGE[1]):
                    cone += fov_wedge(a, half_angle=60.0, length=40.0)
                v = isect(skin, cone) + isect(skin, tilt_sweep())
                out.append((f"{pre}: outside the camera's 60 deg FOV cone and its tilt sweep",
                            v < EPS, f"{v:.3f} mm³ over tilt {CAM_TILT_RANGE}"))

            for what, sk, allow in sections_of(seg, kind, _P):
                ok_w, detail = wall_2d(sk, 1.2, what, allow)
                out.append((f"{pre}: min wall >= 1.2 on the {what} section", ok_w, detail))
            ok_r, detail = ray_solid(base, 1.2, "skin")
            out.append((f"{pre}: min wall >= 1.2 by per-face rays on the functional solid"
                        + (" (the decorated mesh is measured by the decor mesh-wall row)"
                           if (name, kind) == ("centre", "plain") else ""), ok_r, detail))
            ok_s, detail = single_solid(skin)
            out.append((f"{pre}: one solid", ok_s, detail))
            out.append((f"{pre}: left is the exact mirror", abs(left.volume - skin.volume) < 0.01,
                        f"Δ {abs(left.volume - skin.volume):.6f} mm³"))
            out.append((f"{pre}: print orientation stated", skin_label(name, kind, "r") in PRINT,
                        f"bed normal {PRINT[skin_label(name, kind, 'r')]} - standing on the rear end "
                        f"face, so the dovetail, the tongue slits and every aperture run along the "
                        f"build axis"))
            out.append((f"{pre}: {info['aperture_note']}",
                        (info["apertures"] > 0) == (kind == "vented"),
                        f"{info['apertures']} aperture(s); mark: {info['mark']}; "
                        f"puncta: {info['puncta_note']}"))

        diff = abs(areas["plain"] - areas["vented"]) / max(areas.values())
        out.append((f"{name}: plain and vented outlines differ by > 12 % in plan area", diff > 0.12,
                    f"{areas['plain']:.0f} vs {areas['vented']:.0f} mm², {diff:.1%} - a different "
                    f"shape, not the same shape with holes in it"))
    return out



PLATE_TAB_NOTE = (
    "The front segment passes UNDER the plate_top prop-arch tab rather than outside it, and the "
    "corridor is why: the tab reaches x 37.0 at y 60, and at that y the front prop keep-out caps "
    "|x| at 37.59 - a 0.59 mm corridor, against the 1.9 mm the skin wall alone needs. Interference "
    "is nonetheless zero: the tab is plate_top material at Z 34-36 and this whole system stops at "
    "Z 33.75, 0.25 mm below it. Everywhere else both plate outlines are cleared in plan.")
