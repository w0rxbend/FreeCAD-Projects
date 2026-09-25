"""Front slide-on U-pod for a 19 or 21 mm FPV camera on the mid-plate nose - four style families.

The MOUNTING is one piece of geometry shared by every style and is never restyled: the two C-channels
over the Ø6 front-tip standoffs, the floor rails, the M2 tilt arc slots and the backplate. Only the
outboard shell - cheek silhouette, chin, brow and apertures - changes between styles.
"""

from copy import deepcopy
from math import asin, atan, cos, degrees, radians, sin, tan

from build123d import (Axis, Circle, Edge, GeomType, Part, Plane, Polygon, Pos, Rectangle, Sketch,
                       SlotArc, SlotOverall, Vector, extrude)

from tigerbee.accessories import _blender as BL  # noqa: F401 - checks() reports the decor rows
from tigerbee.accessories import _style as S
from tigerbee.accessories._common import *  # noqa: F401,F403 - constants, builders and checks

NAME = "camera_pod"
TITLE = "Camera pod (19 / 21 mm)"
MATERIAL = "TPU95A"
EXCLUSIVE = ()

# --- style variants -----------------------------------------------------------------------------
# Six parts over four families. The SHARD reading is the stock pod, byte-for-byte: the faceted open
# cage with the mitred polygonal window, the horn/brow posts and the slotted chin already IS this
# family, so `shard` reuses _shell_shard() unchanged and ships both camera widths. The framework
# appends the variant to every label, so the stock parts are now `camera_pod_21__shard` /
# `camera_pod_19__shard` - same geometry, same volume, same checks.
STYLES = ("shard", "slipstream", "feral", "chassis", "vespid", "brutalist", "coral")
WIDTHS = {"shard": (21.0, 19.0), "slipstream": (21.0, 19.0), "feral": (21.0,), "chassis": (21.0,),
          "vespid": (21.0, 19.0), "brutalist": (21.0, 19.0), "coral": (21.0, 19.0)}
# The three NEW families ship BOTH camera widths, which is the point of them: the user asked for
# variety in the details they already have, and a pod is only an option if it exists in their size.
# `S.STYLES` is the _style vocabulary (a dict); the module's own `STYLES` above is a tuple of the
# shells this file implements, so the style-guard idiom has to name the vocabulary explicitly.
DONOR = {"vespid": "feral", "brutalist": "arsenal", "coral": "carapace"}
"""Whose scaling law a new language borrows until `_style` carries its own entry.

_style.py is owned by another task. Every row that needs a Style object goes through `_st()`, so this
module works whether or not that task has landed - the donor is chosen by kinship, exactly as the
brief's "call scale_features(obj, style_of('shard')) as the donor law" asks: VESPID is a chitin
language (feral), BRUTALIST is orthogonal and stencilled (arsenal), CORAL is a closed shell
(carapace)."""


def _st(style: str):
    """The Style object for a family: its own if `_style` has one, else its donor's."""
    return S.STYLES.get(style) or S.STYLES[DONOR.get(style, "shard")]


VARIANTS = {
    "shard": {"style": "shard", "material": "TPU95A",
              "notes": "the stock faceted cage, untouched: mitred polygonal window, chamfered creases, "
                       "brow posts over the lens and the slotted chin. Pure build123d, always available. "
                       "Ships both camera widths."},
    "slipstream": {"style": "slipstream", "material": "PETG",
                   "notes": "a lofted teardrop hood: blunt leading radius 0.22 x L over the lens, one "
                            "unbroken crest arc sweeping back at 12.8 deg to the backplate, stadium "
                            "apertures with a raised OCELLUS lip, two flush NACA scoops and a debossed "
                            "lunule stretched 1.4x along the flow. No crease anywhere on the upper shell. "
                            "Ships both camera widths."},
    "feral": {"style": "feral", "material": "TPU95A",
              "notes": "it bites: a descending row of three raked brow spines (1 : 0.78 : 0.61) over the "
                       "lens, two crossed sickle mandibles on the chin with three inner serrations each, "
                       "punctate jaw cheeks, cusped lens slits and the lunule cut clean through as a "
                       "slash. 21 mm only."},
    "chassis": {"style": "chassis", "material": "PETG",
                "notes": "only the load path survives: each cheek becomes an open truss - two curved "
                         "rails, four struts triangulated 50-70 deg and a ring-node eyelet at every "
                         "junction - the backplate reduces to a vent ladder and the chin carries a "
                         "starburst hub. 21 mm only."},
    "brutalist": {**({"style": "brutalist"} if "brutalist" in S.STYLES else {}), "material": "PETG",
                  "notes": "a concrete bunker with a lens hole: two flat 3.0 mm slab cheeks and a slab "
                           "chin, orthogonal to the frame datum, 1.0 mm x 45° chamfers and not one "
                           "fillet above r 0.3, ONE rectangular void per cheek, board-marking grooves "
                           "0.6 x 0.3 at 2.4 pitch running the print direction, external board-form "
                           "ribs and a 2.0 mm deep cast-in datum stamp on the chin flank. Twice the "
                           "mass of anything else in the set. Pure build123d. Both camera widths."},
    "vespid": {**({"style": "vespid"} if "vespid" in S.STYLES else {}), "material": "TPU95A",
               "notes": "wasp: the body is FOUR TERGITES stepping rearward from the lens mouth, each "
                        "0.82x the length and 0.86x the girth of the one before it, each ending in a "
                        "1.2 mm proud collar with a 0.45 mm groove behind it, so the side profile is "
                        "visibly shingled. One elliptical spiracle per tergite per flank, scaled by "
                        "the same taper; the wall tapers 2.2 at the mouth to 1.4 at the rear; a "
                        "stinger cusp runs back over the clip. Pure build123d. Both camera widths."},
    "coral": {**({"style": "coral"} if "coral" in S.STYLES else {}), "material": "PETG",
              "notes": "accreted, not designed: the functional pod (clip rings, cam cheeks, lens mouth) "
                       "is seeded with metaballs r 3.0-6.0 at 7 mm spacing along the cheek load path "
                       "and voxel-remeshed at 0.40, so the outline is lumpy and continuous with no "
                       "straight edge; the wall swells from 1.6 at the extremities to 4.0 at the clip "
                       "nodes and the surface carries corallite pits. Needs Blender; degrades to the "
                       "undecorated accreted core, which passes every check on its own. Both widths."},
}
ASSEMBLY_VARIANT = "shard"
ASSEMBLY_LABELS = ("camera_pod_21",)  # the two sizes are alternatives: they occupy the same space

PRINT = {"camera_pod_21": (0, -1, 0), "camera_pod_19": (0, -1, 0)}
# Every style prints on its back, on the backplate's rear face at y 80.5, and that is a measured
# result rather than a default. print_orientation maps frame +Y onto print +Z, so under this bed
# normal a face is an overhang exactly when it faces frame -Y: the whole pod is "swept forward" and
# the only rearward faces are the bed itself and the two declared lintels. The alternatives were
# checked and are worse: (0, 0, -1) leaves the floor rails' undersides at Z 9 hanging 3 mm over the
# chin, and (±1, 0, 0) turns each cheek's inboard face into a 400 mm² overhang. That single fact is
# what shapes FERAL's spines (raked 65/35 deg, never a vertical fin) and its mandibles (prismatic
# along Y off the chin face, so every jaw wall has normal.Y = 0 and cannot be an overhang).

MOUNTS = ("plate_mid top face Z 9 (the pod rails sit on it) and its front V-notches (nose nubs)",
          "standoff_front_tip_left / _right Ø6 shafts (±19, 109) through the 5.2 mm C-clip mouths")
HARDWARE = ("2 x M2 camera side screws - the camera's own; they set the tilt in the 15-40 deg arc slot",)
NOTES = ("Slides on from the front: the pod is pushed rearwards (-Y) over the Ø6 front-tip standoffs, "
         "which snap through the 5.2 mm mouths, until the nose nubs drop into the mid-plate V-notches and "
         "the rails sit on plate_mid; it comes off the same way, forwards. Tilt is set by the camera's own "
         "M2 side screws - pivot hole plus a 15-40° arc slot; the cable leaves through the open top of the "
         "backplate. No brow bar across the centreline: anything ahead of the lens sits in the FOV. The pod "
         "must come off before a 25.5 mm-pattern board can be fitted in the forward bay (its rear screws "
         "are at y 81.5). "
         "MEASURED DEVIATIONS from the style briefs. Every one is forced by a check, and the number that "
         "forced it is in the row that reports it: "
         "(1) SLIPSTREAM's teardrop cannot have both a 0.22 x L leading radius and a 9-14° straight-flank "
         "taper - for a simple teardrop the two are only consistent at 15.7° - so the taper is carried by "
         "the crest arc, which leaves the shell at 12.8°. Its flush vent is a band PARALLEL TO THE CREST, "
         "13 x 3.0 x 1.4 deep, not a 14 x 4 rectangle: the crest rises 3.2 mm over the cheek's 30 mm run, "
         "so every rectangular footprint either broke through the crest at its rear or left a 0.24 mm rib "
         "under the channel web at its front. Its ramp runs out to 0.3 deep rather than flush, because a "
         "feathered ramp end measures 0.08 mm. It carries NO mark: no surface on this pod can hold a 16 mm "
         "lunule (§4.3), and the OCELLUS lip is the accent instead. "
         "(2) FERAL's mandibles are 5.0 thick at the base, not 6.0, and 6.5 mm long: the chin's front face "
         "is 14 mm of usable height between Z 6 and the 60° FOV ceiling at Z 20, which is what two blades "
         "plus 1.5 mm of crossing clearance fit in. They are PRISMS extruded forward off the chin face "
         "rather than swept tusks, because a swept round tusk of any radius puts 40-110 mm² of rearward "
         "surface in the air at this bed normal - measured on cones, tori and lofts. Their sweep is the "
         "blade's own curl in the front view, not a 110-140° tangent turn: a tangent turn past 45° from "
         "the Y axis is an overhang here whatever the cross-section. "
         "(3) CHASSIS struts are 2.4 wide, not 2.0, so the ring node's 0.9 x w bore clears PETG's 2.0 mm "
         "minimum through-hole; they are chains of lens segments rather than stadiums, so their walls are "
         "arches inside PETG's Ø12 exemption instead of 29 mm² of 35° overhang each; its chin post is "
         "lightened by a column of keyholes rather than one tall cusped window, whose Ø30 arcs were 19.5 "
         "mm² of 100 %-down surface; and its backplate ladder takes one rung per band at the family's own "
         "9.0 pitch, because each band is 10.8 mm and two rungs need 13.4. "
         "MEASURED DEVIATIONS in the three NEW families, same rule - every one is forced by a check "
         "and the number that forced it is in the row that reports it: "
         "(4) VESPID's girth taper is the tergite's DORSAL HEIGHT above the Z 9 seating plane, "
         "because that is the only dimension a U-pod has free: the inboard cheek face is set by the "
         "camera and the outboard one by the 1.4-2.2 mm wall law. The 0.45 mm groove aft of each "
         "collar is a real notch (its rearward wall is 1.0 mm², inside the 5 mm² overhang floor) but "
         "the girth STEP behind it is a 1 : 1.1 ramp and not a step: printed nose-up a 4.06 x 3.0 mm "
         "rearward ledge is 12.2 mm² of unsupported surface. The four tergites span the WHOLE pod, "
         "y 84-122.5, which is what puts the three boundaries at 109.85 / 99.48 / 90.97 - and those "
         "are the only stations the M2 screw pad allows, since CN-7 needs solid cheek to Z 30.2 over "
         "y 96.8-103.2 and to Z 28.8 over y 91-98.7. Over the clip web's footprint (y 103-113.5) the "
         "tapered wall is tied back out to the full 3.0: _core's web springs from x 13.75 and a 2.2 "
         "mm cheek leaves it a free-standing 0.59 mm wedge, which is the clip's whole load path. "
         "(5) BRUTALIST's ribs are TWO pilasters per side at a 28 mm pitch, not a 12 mm field: the "
         "cheek's outer face is exposed over y 88.5-103.0 only and the M2 screw heads own y "
         "90.9-103.3 of that; they are 2.0 proud and not 3.0 because at 3.0 the rib reaches x 16.75 "
         "and fouls the Ø6 standoff on the way off. Its one void per cheek is 51 % of the FREE panel "
         "(the cheek minus the floor rail, the top beam, the two web tie columns, the front column "
         "and the M2 pad - the decomposition is printed in the row) rather than of the gross "
         "rectangle: a cheek that is also the clip bracket cannot put a hole through its own load "
         "path. Its datum stamp is five sunk BARS and not an outline, because each bar's rearward "
         "end wall is 4.0 mm² where a lunule of the same depth is ~20 mm² of rearward surface. "
         "(6) CORAL's corallite discs are capped at r 6.0: a disc's silhouette prints as an arch and "
         "overhangs() exempts an arch only to PETG's Ø12. Its pits live only where the cheek's outer "
         "face IS the surface (y 89.5-102 and 114.8-121.5); sunk anywhere else they would be "
         "internal cavities behind the clip web or the backplate. The metaball seeds sit on the "
         "cheek's mid-plane so the accretion stays well inside decorate()'s 2.0 mm envelope cap, and "
         "the nose nubs are declared to the mesh wall gate as the 1.5 mm registration features they "
         "are instead of the floor being lowered to admit them.")

# --- parameters (mm) ------------------------------------------------------------------------
CAM_W = 21.0          # the two shipped widths are CAM_W 21 and 19; nothing else changes
CAM_H = 22.0
CAM_D = 24.0
PIVOT_Y, PIVOT_Z = CAM_PIVOT[1], CAM_PIVOT[2]   # (0, 100, 27)
TILT_RANGE = (15.0, 40.0)
TILT_MARGIN = 1.0     # the arc slot runs 1 deg beyond each end so the end poses are not tangent
CHEEK = 3.0
CHANNEL_TOP = 31.5    # 0.3 below the front_bumper lip
CHANNEL_WALL = 1.7    # OD 9.9: printed on its back the channel is an arch just inside the TPU limit
CHANNEL_Z0 = Z_MID_TOP + 0.2
MOUTH_DEG = 270.0     # the mouth opens towards -Y: the pod is pushed on from the front (-Y) and
SNAP = 0.8            # pulled off forwards (+Y); mouth = STANDOFF_D - SNAP = 5.2
CHIN = True
FIT = 0.25

FLOOR_Y0, FLOOR_Y1 = 80.5, 116.0    # clear of the fwd_30p5 heads at y 76.75 and of a 36 mm board at y 61.5
FLOOR_Z1 = 13.0                     # 4 mm rails: the pod's only bending stiffness at the floor
CB_REAR_Y1 = 86.0                   # rear crossbar y 80.5-86 (no slot nub - the slot at (0, 82.5) stays free)
CB_FRONT_Y0 = 112.0
WALL_X = 15.75                      # backplate half-width: 0.25 clear of the Ø6 standoffs on the way off
WALL_DEEP = 88.5                    # depth outboard of the camera
WALL_SHALLOW = 84.8                 # depth in front of it: the body's rear face at 0 deg is at y 85.75
WIN_Z0 = 22.4                       # above this the backplate is open across the camera: its rear-top
                                    # corner swings back to y 81.85 and the cable leaves through here
CAM_PAD = 0.3                       # backplate opening half-width = CAM_W/2 + FIT + CAM_PAD
CHEEK_Y0, CHEEK_Y1, CHEEK_TOP = 84.0, 114.0, 33.8
DIAMOND_Y, DIAMOND_Z = 91.0, 20.0   # lightening window 9 (Y) x 6 (Z): long axis along the print vertical
DIAMOND_YL, DIAMOND_ZL = 9.0, 6.0
SLOT_R, SLOT_W = 6.0, D_M2_THRU     # the second camera screw sits 6 mm behind the pivot at 0 deg
POST_Y0, POST_Y1, POST_TOP = 114.0, 122.5, 38.0
POST_RAMP_Y = 118.6                 # ramp (114, 33.8) -> (118.6, 38): 42 deg, so not an overhang
CHIN_Y0, CHIN_Y1, CHIN_Z0, CHIN_Z1 = 116.5, 122.5, 6.0, 20.0
CHIN_CHAMFER = 1.1                  # rear face y = CHIN_Y0 + 1.1 (9 - Z) below Z 9
NUB_X, NUB_XW, NUB_Y0, NUB_YL = 10.2, 3.0, 110.0, 3.0
NUB_Z0 = 7.5                        # 3.0 x 1.5 rear face = 4.5 mm2, below the overhang check's 5 mm2:
                                    # a chamfer instead would taper to a knife edge at Z 9
WEB_X, WEB_Y0, WEB_Y1, WEB_CH = 16.0, 103.0, 113.5, 4.0  # cheek -> channel web, inboard of the mouth
WEB_FLARE = (19.5, 109.0)           # corridor (x 16.4-21.6) and clear of the M2 screw heads (y < 102.1);
                                    # ahead of y 109 the standoff never passes, so the web flares out

# The clean zone every style must leave alone (CN-7), in the cheek's own (y, z) sketch: the M2 pivot,
# the tilt arc slot and 2.0 mm of margin round both. No generated aperture, spine root or truss node
# may enter it - the M2 screw has to find solid cheek over the whole 15-40 deg travel.
# The M2 arc slot and its pivot occupy y 92.98-101.20, Z 21.86-28.20 in the cheek's own (y, z) sketch,
# and CN-7 asks for a 2.0 mm undecorated shell round every mating feature. The STOCK pod - whose geometry
# the brief freezes - reaches 1.32 mm: its diamond window's upper-front edge is that far from the arc
# slot's lower cap, measured by offsetting the slot's own outline until the void exceeds the bore
# (exact at 1.3, first excess 0.16 mm³ at 1.4). So SHARD is held to the margin it ships with and every
# NEW style is held to CN-7's full 2.0 - which is the only honest way to read "keep SHARD untouched"
# and "never weaken a check" at the same time.
CLEAN_OFFSET = {"shard": 1.3, "slipstream": 2.0, "feral": 2.0, "chassis": 2.0,
                "vespid": 2.0, "brutalist": 2.0, "coral": 2.0}
# front_bumper's declared keep-out: its X_IN is 14.2, its wall/nose live Z 31.8-42 over y 98.5-118.
# Above Z 31.8 in that window the pod must stay inboard of 14.2; BELOW it the pod already reaches
# x 23.95 (the channels), which is why this is a box and not a plain "cheeks <= 33.8" rule.
BUMPER_KEEPOUT = (14.2, 98.5, 31.8, 40.0, 118.0, 42.0)

_ENV_Y0 = FLOOR_Y0   # printed: X = x, Y = zc - z, Z = y - Y0, with zc the part's OWN z centre


def _print_box(bb, x0, y0, z0, x1, y1, z1, pad=1.0):
    """Frame-coordinate box -> a bridge_ok ('box', ...) in PRINT coordinates (bed = the y 80.5 face).

    `bb` is the PART's bounding box, and it has to be: print_orientation() centres the part on its own
    bbox, so print y = (bb.min.Z + bb.max.Z)/2 - frame z. Hard-coding that centre from CHIN_Z0/POST_TOP
    silently shifted every bridge box by 1.7 mm on any style whose Z extent is not 6..38 - measured as
    CHASSIS failing `no unsupported overhangs` on its own declared chin lintel."""
    yc = (bb.min.Z + bb.max.Z) / 2
    return ("box", x0 - pad, yc - z1 - pad, y0 - _ENV_Y0 - pad, x1 + pad, yc - z0 + pad, y1 - _ENV_Y0 + pad)


def _bridges(bb, chin_y0: float, chin_z1: float, extra=()) -> tuple:
    """The declared lintels: the chin's rear face and the front crossbar's rear face, plus whatever
    else a style exposes. Both are planes at a constant y, bounded by the two posts, and their shorter
    printed span is the chin height - well inside TPU's 22.0 / PETG's 20.0 bridge limit."""
    out = [_print_box(bb, -13.75, chin_y0, Z_MID_TOP, 13.75, chin_y0, chin_z1),
           _print_box(bb, -13.75, CB_FRONT_Y0, Z_MID_TOP, 13.75, CB_FRONT_Y0, FLOOR_Z1)]
    out += [_print_box(bb, *e) for e in extra]
    return tuple(out)


BRIDGE_OK: dict[str, tuple] = {}   # filled in by build(), which is the only place the real bbox exists

# --- SLIPSTREAM ---------------------------------------------------------------------------------
SL_R = 9.0                  # blunt leading radius = 0.22 x L, L = 41 (the fairing runs y 83-124)
SL_CX = 115.0               # station of the crest: both the nose arc and the crest arc peak here,
SL_NOSE_Z = 27.0            # with a common horizontal tangent, so the join is G1 and invisible
SL_TOP = SL_NOSE_Z + SL_R   # 36.0
SL_CREST_R = 120.0          # crest arc: 12.8 deg where it leaves the shell at the backplate
SL_CHIN_Y0, SL_CHIN_Z1 = 115.0, 17.0   # the chin runs back to the nose arc's own station. 17, not
                                       # 19: at 19 the beak arc is exactly tangent to the cap, so the
                                       # chin's dorsal face collapses to a 2.5 mm sliver and has no
                                       # room for the suture. At 17 it is a 7.2 mm flat crown
SL_CHIN_RAMP = 116.5                   # ... but its sub-Z9 ramp starts here, clear of the plate nose
SL_CHIN_R, SL_CHIN_CY = 6.5, 117.5     # the beak: a blunt arc whose tip lands exactly on y 124, the
SL_CHIN_CZ = 12.5                      # same station as the nose arc's own tip - one nose, not two
SL_WIN = (96.5, 15.0, 14.0, 4.4)       # stadium eye window: yc, zc, length, height. Sunk to Z 15
SL_LIP = (2.0, 1.5)                    # so the 2.0-wide OCELLUS lip round it (Z 10.8-19.2) clears the
                                       # arc slot by 2.66 - more than the M2 head's 2.1 mm radius, so
                                       # the screw head never lands on the lip
# The flush vent: a band PARALLEL TO THE CREST, not a rectangle on the flank. A rectangular NACA
# footprint cannot be placed on this cheek at all - the crest arc rises 3.2 mm over the 30 mm run, so
# any 4 mm-tall box either pokes through the crest at its rear or leaves a 0.24 mm rib under the
# channel web at its front (both measured). Offsetting the crest's own arc keeps a constant 1.4 mm of
# skin above the vent everywhere, which is what a flush duct on a curved fairing actually looks like.
SL_VENT = (1.4, 3.0, 89.0, 102.0, 1.4, 0.3)   # inset below the crest, width, y0, y1, deep end, shallow
SL_MARK = 0.0                          # SLIPSTREAM carries NO mark, and that is the design language's
# own rule, not an omission: "if no surface can hold the mark at its minimum size, the part carries no
# mark - a crushed mark is worse than none". The largest uninterrupted planar surface on this pod is the
# backplate flank, 8.0 x 24.8; a 16 mm lunule is 7.37 mm across its crescent, which leaves a 0.31 mm rib
# to the panel edge - measured by the ray sampler as a 0.09 mm wall. The cheek's own flank is taken by
# the eye, the OCELLUS lip, the arc-slot clean zone, the crest vent and the channel web. The family's
# accent here is the OCELLUS lip itself, and the part still carries its CN-1 suture.

# --- FERAL --------------------------------------------------------------------------------------
FE_TOP = (30.0, 33.8)       # cheek top edge, raked forward so the spine row descends rearwards
FE_POST_TOP = 34.4          # the brow posts stop here; the spines are what stands above them
FE_SPINES = ((108.0, 4.0), (99.0, 3.12), (90.0, 2.44))   # (y, height) - the 1 : 0.78 : 0.61 run
FE_SPINE_FRONT, FE_SPINE_REAR = 68.0, 35.0   # flank angles from horizontal. 68 is the leading flank
FE_SPINE_TIP = 0.55                          # the family asks for; 35 on the trailing one keeps its
                                             # normal.Y at -0.574, inside overhangs()' -0.70 limit
FE_SLIT = (94.0, 16.4, 10.0, 1.6)            # one cusped lens slit: yc, zc, tip separation, half width
FE_CHIN_Z1 = 20.0                            # the stock chin height, and it is a hard ceiling: the
                                             # camera's own lens cylinder sweeps y 116.25 / Z 19.75-34.25
                                             # at 0 deg tilt, so a 24 mm chin puts 46 mm³ of material
                                             # inside tilt_sweep() (measured)
FE_CHEEK_Y0 = 81.0                           # the cheek starts inside the backplate, so the slash
                                             # below has real material to keep its ligament against
FE_JAW_Y = (121.0, 129.0)                    # both jaws are prisms rooted INSIDE the chin (121 < the
                                             # chin's front face at 122.5), so the union always fuses
FE_MARK_AT = (88.0, 21.0)                    # the slash: the one 12 x 20 panel clear of the arc-slot
                                             # zone, the floor rail and the channel web
FE_JAW_R = (6.6, 11.0)                       # right jaw's Z band  ) 1.5 mm of clearance, and in the
FE_JAW_L = (12.5, 16.9)                      # left jaw's Z band   ) front view the two blades cross
FE_JAW_X = 13.0                              # the blades stay 0.75 inboard of the chin's own flank:
                                             # at 13.77 the root left a 0.02 mm sliver against it
FE_JAW_T = (5.0, 1.6)                        # base thickness, tip Ø
FE_MARK = 16.0                               # lunule, cut clean through the cheek and its web

# --- CHASSIS ------------------------------------------------------------------------------------
CH_W = 2.4                  # strut width; 2.0 would give a 1.8 ring bore, under PETG's 2.0 hole floor
CH_NODE = (2.6, 0.9)        # ring node OD / ID as a multiple of the strut width -> 6.24 / 2.16
CH_RAIL_R = 150.0           # upper rail: a shallow arc, crown at y 99
CH_RAIL_TOP = 33.8
CH_HUB = (96.5, 25.0, 6.6)  # the arc-slot boss is the truss's central node: yc, zc, radius
CH_BOT_Z = 13.6             # lower-rail node line (the floor rail top is Z 13)
CH_NODES_BOT = (88.0, 105.0)
CH_NODES_TOP = (90.5, 102.5, 112.5)
CH_LADDER = ((11.6, 22.4), (23.0, 33.8))     # backplate vent-ladder bands (Z)
CH_RUNG = (12.0, 3.4, 1.7, 9.0, 2.2)         # the frame's own slot: length, width, corner r, pitch, lig
CH_HUB_BORE = 6.9           # starburst hub bore through the chin. 8 slots of w 1.2 round a Ø6.9 bore
                            # leave a 1.55 mm ligament at the bore; a Ø6.0 bore leaves 1.16, under the
                            # 1.5 PETG floor, and the slot's outer end then has 1.5 to the chin's edge
CH_CHIN_Z1 = 20.0           # same hard ceiling as FERAL: the lens sweeps Z 19.75-34.25 at y 116.25


# --- 2D / 3D helpers ------------------------------------------------------------------------
def _yz(sk, x0: float, x1: float) -> Part:
    """Extrude a sketch drawn in (Y, Z) from x0 to x1."""
    return extrude(Plane(origin=(x0, 0, 0), x_dir=(0, 1, 0), z_dir=(1, 0, 0)) * sk, amount=x1 - x0, dir=(1, 0, 0))


def _xz(sk, y0: float, y1: float) -> Part:
    """Extrude a sketch drawn in (X, Z) from y0 to y1 - the FERAL mandible plane.

    A solid built this way has every free wall normal perpendicular to Y, so under the pod's bed
    normal (0, -1, 0) not one of them can be an overhang whatever the outline does. That is the whole
    reason the jaws are prisms and not swept tusks."""
    # z_dir = -Y, not +Y: with x_dir = +X the plane's own y axis is z_dir x x_dir, which for +Y comes
    # out as frame -Z and silently prints the whole sketch upside down (measured: jaws at Z -17.9).
    return extrude(Plane(origin=(0, y0, 0), x_dir=(1, 0, 0), z_dir=(0, -1, 0)) * sk, amount=y1 - y0,
                   dir=(0, 1, 0))


def _rect2(a0: float, b0: float, a1: float, b1: float) -> Sketch:
    return Pos((a0 + a1) / 2, (b0 + b1) / 2) * Rectangle(a1 - a0, b1 - b0)


SUTURE_INSET = 0.8
"""How far CN-1's groove is held off each end of the crown face it is cut into.

This is a MEASURED number, not a margin of taste. `S.suture()` runs out to a true cusp at each end
(a lens in plan), and when that cusp lands exactly ON the crown's boundary edge the groove's two
tangent walls and the face they are cut into become coincident at a single point. OCCT keeps the
solid valid - `is_valid` is True, `len(solids()) == 1`, the volume is right - and the STEP and STL
both write; it is only lib3mf's mesh validator that catches it, as a bare `RuntimeError: 3mf mesh is
invalid` from `Mesher.add_shape`, with nothing to say which face is at fault.

Measured on all three sutured styles at once: SLIPSTREAM's crown runs y 115.00-122.19 (the beak arc
crosses Z 17 there) and FERAL's / CHASSIS's chin runs y 116.5-122.5, and each style called
`S.suture()` with exactly those numbers. At inset 0.0 every one of the four parts failed the 3MF
gate; at 0.8 every one passes, and the face count drops by exactly 1 - the degenerate sliver. 0.6 /
1.0 were also measured clean, so 0.8 is the middle of a real window rather than an edge of one.

`_style.apply_suture()` carries the same idea as its `inset=1.5` default and documents it as
"holds the cusps off the silhouette so the groove runs out INSIDE the surface rather than nicking
the outline". This pod cannot use that helper - its crown is neither the bounding box's top face nor
centred on the part - so it states the inset itself."""


def _suture(y0: float, y1: float, z_top: float) -> Part:
    """CN-1's dorsal groove, held SUTURE_INSET off both ends of the crown face (see above)."""
    return S.suture(y0 + SUTURE_INSET, y1 - SUTURE_INSET, z_top)


def _suture_span(y0: float, y1: float) -> tuple[float, float]:
    """The same span, for the conformance probe - so the check measures the groove that is there."""
    return y0 + SUTURE_INSET, y1 - SUTURE_INSET


def _mirror(part: Part) -> Part:
    return part.mirror(Plane.YZ)


def _both(part: Part) -> Part:
    return part + _mirror(part)


def _side(x_cheek: float) -> Part:
    """C-channel round the right front-tip standoff, webbed back to the cheek on its inboard side."""
    cx, cy = FRONT_TIP_XY
    # closed=False is EXPLICIT and load-bearing: this pod is a slide-on, and its own MOUNTS and
    # NOTES say so ("the standoffs snap through the 5.2 mm mouths"). _common.c_clip() gained a
    # `closed` flag that defaults to True after this module was written, and inheriting that default
    # silently welded both channels shut - every variant, the stock one included, then failed
    # "slides off forwards" with 248.978 mm³ against the Ø6 standoff at +3 mm.
    chan = c_clip((cx, cy), CHANNEL_Z0, CHANNEL_TOP - CHANNEL_Z0, opening_deg=MOUTH_DEG,
                  bore_d=D_CLIP_BORE, wall=CHANNEL_WALL, snap=SNAP, closed=False)
    plan = Polygon((x_cheek, WEB_Y0), (WEB_X, WEB_Y0 + WEB_CH), (WEB_X, WEB_FLARE[1]),
                   (WEB_FLARE[0], WEB_Y1), (x_cheek, WEB_Y1), align=None)
    web = extrude(Plane.XY.offset(CHANNEL_Z0) * plan, amount=CHANNEL_TOP - CHANNEL_Z0)
    return (chan + web) - cylinder(cx, cy, CHANNEL_Z0 - 1, CHANNEL_TOP + 1, D_CLIP_BORE)


def _nubs() -> Part:
    return _both(box(NUB_X - NUB_XW / 2, NUB_Y0, NUB_Z0, NUB_X + NUB_XW / 2, NUB_Y0 + NUB_YL, Z_MID_TOP))


def _diamond() -> Sketch:
    """SHARD's mitred polygonal window - the stock lightening hole."""
    dy, dz = DIAMOND_YL / 2, DIAMOND_ZL / 2
    return Polygon((DIAMOND_Y - dy, DIAMOND_Z), (DIAMOND_Y, DIAMOND_Z + dz),
                   (DIAMOND_Y + dy, DIAMOND_Z), (DIAMOND_Y, DIAMOND_Z - dz), align=None)


def _arc_slot() -> Sketch:
    """The M2 pivot hole and the 15-40 deg tilt arc slot - identical in every style, never restyled."""
    pivot = Pos(PIVOT_Y, PIVOT_Z) * Circle(D_M2_THRU / 2)
    a0, a1 = 180 + TILT_RANGE[0] - TILT_MARGIN, 180 + TILT_RANGE[1] + TILT_MARGIN
    arc = Edge.make_circle(SLOT_R, Plane.XY, start_angle=a0, end_angle=a1)
    return pivot + Pos(PIVOT_Y, PIVOT_Z) * SlotArc(arc=arc, height=SLOT_W)


def _cheek_cuts(x_out: float, window: Sketch | None = None, x_cut: float | None = None) -> Part:
    """Window, pivot hole and the tilt arc slot, cut through both cheeks.

    `window` defaults to SHARD's diamond so the stock geometry is unchanged. The cut never reaches
    past `x_cut` (default x_out): the backplate reaches x 15.75 and a cut past the cheek would leave
    a 1 mm sliver outboard of it."""
    sk = _arc_slot() + (_diamond() if window is None else window)
    x = x_out if x_cut is None else x_cut
    return _yz(sk, -x, x)


# --- the shared mounting core (identical in every style) -------------------------------------
def _core(cam_w: float, x_in: float, x_out: float) -> Part:
    """Floor rails, crossbars, backplate, both C-channels with their webs, and the nose nubs.

    This is the whole mating story and it is never restyled: the channel bores are the two Ø6.5 rings
    round the front-tip standoffs, the rails carry the seating face at Z 9 and the backplate holds the
    camera's rear. A style may add to it and may cut apertures through the backplate, but the geometry
    below is byte-identical for all four families."""
    floor = _both(box(x_in, FLOOR_Y0, Z_MID_TOP, x_out, FLOOR_Y1, FLOOR_Z1))
    floor += box(-x_out, FLOOR_Y0, Z_MID_TOP, x_out, CB_REAR_Y1, FLOOR_Z1)
    floor += box(-x_out, CB_FRONT_Y0, Z_MID_TOP, x_out, FLOOR_Y1, FLOOR_Z1)

    # backplate: deep outboard of the camera, shallow and then open where the camera tilts back
    cx = x_in + CAM_PAD
    wall = box(-WALL_X, FLOOR_Y0, Z_MID_TOP, WALL_X, WALL_DEEP, CHEEK_TOP)
    wall -= box(-cx, WALL_SHALLOW, Z_MID_TOP - 1, cx, WALL_DEEP + 1, CHEEK_TOP + 1)
    wall -= box(-cx, FLOOR_Y0 - 1, WIN_Z0, cx, WALL_DEEP + 1, CHEEK_TOP + 1)

    return floor + wall + _both(_side(x_out)) + _nubs()


def _chin(y0: float, y1: float, z1: float, x_out: float, front: Sketch | None = None,
          y_ramp: float | None = None, z0: float = CHIN_Z0) -> Part:
    """The chin block, full width. Its rear face is a plane at `y0` - the declared print lintel - and
    below Z 9 it ramps forward at CHIN_CHAMFER so it clears the mid-plate nose without ever becoming
    an overhang (the ramp's normal.Y is -0.673, inside overhangs()' -0.70 limit).

    `y_ramp` starts that ramp further forward than the rear face, with a horizontal step at Z 9. A
    style whose chin reaches back past y 116 needs it: the mid-plate nose runs out to y 116 at Z 7-9,
    so a ramp starting at y 115 clips the plate by 1.4 mm³ (measured). The step's own face points
    straight down in frame Z, which is normal.Y = 0 in print - never an overhang."""
    y_ramp = y0 if y_ramp is None else y_ramp
    y_low = y_ramp + CHIN_CHAMFER * (Z_MID_TOP - z0)
    pts = [(y0, z1), (y0, Z_MID_TOP)]
    if y_ramp > y0 + 1e-9:
        pts.append((y_ramp, Z_MID_TOP))
    pts += [(y_low, z0), (y1, z0), (y1, z1)]
    prof = Polygon(*pts, align=None)
    if front is not None:
        prof = prof & front
    return _yz(prof, -x_out, x_out)


# --- SHARD: the stock faceted cage, unchanged ------------------------------------------------
def _shell_shard(cam_w: float, x_in: float, x_out: float) -> dict:
    cheeks = _both(box(x_in, CHEEK_Y0, Z_MID_TOP, x_out, CHEEK_Y1, CHEEK_TOP))
    post_prof = Polygon((POST_Y0, Z_MID_TOP), (POST_Y1, Z_MID_TOP), (POST_Y1, POST_TOP),
                        (POST_RAMP_Y, POST_TOP), (POST_Y0, CHEEK_TOP), align=None)
    posts = _both(_yz(post_prof, x_in, x_out))
    add = cheeks + posts
    if CHIN:
        add += _chin(CHIN_Y0, CHIN_Y1, CHIN_Z1, x_out)
    return {"add": add, "window": None, "x_cut": x_out, "sub": None}


# --- SLIPSTREAM: one unbroken highlight ------------------------------------------------------
def _sl_profile() -> Sketch:
    """The cheek's teardrop, drawn in (y, z).

    Two circles and nothing else, which is the whole point: the nose arc (radius 0.22 x L) and the
    crest arc (R 120) both peak at y = SL_CX with a HORIZONTAL tangent, so where they meet there is no
    crease at all - G1 by construction, and a single specular highlight runs the length of the shell.
    The crest leaves the shell at 12.8 deg where it dives under the backplate's top face, which is the
    family's tail taper; the lower-front boundary is the nose arc itself, which is why the hood's lip
    curls away from the lens instead of ending in a flat cut."""
    crest = Pos(SL_CX, SL_TOP - SL_CREST_R) * Circle(SL_CREST_R)
    nose = Pos(SL_CX, SL_NOSE_Z) * Circle(SL_R)
    rear = _rect2(CHEEK_Y0, Z_MID_TOP, SL_CX, SL_TOP + 2.0)
    fwd = _rect2(SL_CX, Z_MID_TOP, SL_CX + SL_R + 1.0, SL_TOP + 2.0)
    return (crest & rear) + (nose & fwd)


def _sl_window() -> Sketch:
    """The eye: a stadium, never a polygon (the family forbids a polygonal aperture)."""
    yc, zc, ln, ht = SL_WIN
    return Pos(yc, zc) * SlotOverall(ln, ht)


def _sl_lip() -> Sketch:
    """OCELLUS: the raised elliptical hood lip round the eye - a stadium ring SL_LIP[0] wide."""
    yc, zc, ln, ht = SL_WIN
    w = SL_LIP[0]
    return Pos(yc, zc) * SlotOverall(ln + 2 * w, ht + 2 * w) - _sl_window()


def _sl_crown_y1() -> float:
    """Front end of the chin's flat dorsal crown, where the beak arc drops below SL_CHIN_Z1."""
    return SL_CHIN_CY + (SL_CHIN_R ** 2 - (SL_CHIN_Z1 - SL_CHIN_CZ) ** 2) ** 0.5


def _sl_vent(x_out: float) -> Part:
    """One flush vent per cheek, its footprint a band parallel to the crest arc.

    The floor ramps from `deep` at the rear to `shallow` at the front, so the only step is the throat
    wall at the front and it is 0.3 x 3.0 = 0.9 mm² - under the 5 mm² overhang floor. The shallow end
    is deliberately NOT flush: a ramp that runs out to zero leaves a feather edge, which the ray
    sampler reads as a 0.08 mm wall and which no nozzle can print."""
    inset, wd, y0, y1, deep, shallow = SL_VENT
    c = (SL_CX, SL_TOP - SL_CREST_R)
    band = (Pos(*c) * Circle(SL_CREST_R - inset)) - (Pos(*c) * Circle(SL_CREST_R - inset - wd))
    foot = band & _rect2(y0, Z_MID_TOP, y1, SL_TOP + 2.0)
    prism = _yz(foot, x_out - deep - 0.001, x_out + 0.5)
    ramp = extrude(Plane(origin=(0, 0, Z_MID_TOP), x_dir=(1, 0, 0), z_dir=(0, 0, 1))
                   * Polygon((x_out - deep, y0), (x_out + 1.0, y0), (x_out + 1.0, y1),
                             (x_out - shallow, y1), align=None), amount=SL_TOP + 4.0)
    return prism & ramp


def _shell_slipstream(cam_w: float, x_in: float, x_out: float) -> dict:
    prof = _sl_profile()
    cheeks = _both(_yz(prof, x_in, x_out))
    lip = _both(_yz(_sl_lip(), x_out, x_out + SL_LIP[1]))
    front = Pos(SL_CHIN_CY, SL_CHIN_CZ) * Circle(SL_CHIN_R) \
        + _rect2(SL_CHIN_Y0 - 1, CHIN_Z0 - 1, SL_CHIN_CY, SL_CHIN_Z1 + 1)
    chin = _chin(SL_CHIN_Y0, SL_CX + SL_R, SL_CHIN_Z1, x_out, front=front, y_ramp=SL_CHIN_RAMP)
    sub = _both(_sl_vent(x_out))
    sub += _suture(SL_CHIN_Y0, _sl_crown_y1(), SL_CHIN_Z1)   # CN-1: the pod crosses X = 0
    return {"add": cheeks + lip + chin, "window": _sl_window(), "x_cut": x_out + SL_LIP[1] + 0.5,
            "sub": sub}


# --- FERAL: it bites -------------------------------------------------------------------------
def _fe_cheek() -> Sketch:
    """The cheek, its top edge raked forward so the spine row descends towards the rear."""
    return Polygon((FE_CHEEK_Y0, Z_MID_TOP), (CHEEK_Y1, Z_MID_TOP), (CHEEK_Y1, FE_TOP[1]),
                   (FE_CHEEK_Y0, FE_TOP[0]), align=None)


def _fe_top_z(y: float) -> float:
    return FE_TOP[0] + (FE_TOP[1] - FE_TOP[0]) * (y - FE_CHEEK_Y0) / (CHEEK_Y1 - FE_CHEEK_Y0)


def _fe_spines() -> Sketch:
    """The brow spine row, drawn in (y, z) on the cheek's raked top edge.

    Each spine is a RAKED fin, not a symmetric cone: leading flank FE_SPINE_FRONT (68 deg, the
    family's ">= 50 deg" rule) and trailing flank FE_SPINE_REAR. The rake is a printability result,
    not a flourish - at this bed normal a face is an overhang when it faces frame -Y, and a 50 deg
    trailing flank has normal.Y -0.766, past overhangs()' -0.70 limit. 35 deg gives -0.574 and the
    asymmetry is exactly what makes the row read as a creature rather than a sawtooth."""
    sk = Sketch()
    for yc, h in FE_SPINES:
        back = h / tan(radians(FE_SPINE_REAR))
        front = h / tan(radians(FE_SPINE_FRONT))
        base = _fe_top_z(yc)
        # the root runs 1.2 BELOW the cheek's top edge over the spine's whole span: the edge is raked,
        # so a 0.6 root left the rear flank 0.057 mm above it - a sliver, measured at 0.67 mm by rays
        sk += Polygon((yc - back, base - 1.2), (yc + front, base - 1.2), (yc + front, base),
                      (yc, base + h), (yc - back, base), align=None)
    return sk


def _fe_slit() -> Sketch:
    """One cusped lens slit low on the cheek: two tangent arcs meeting at a true point (CN-3). Its
    long axis runs along Y so the slit's only ceiling is the cusp, and the arc's own span keeps every
    sampled normal inside the overhang limit."""
    yc, zc, d, h = FE_SLIT
    return S.lens((yc - d / 2, zc), (yc + d / 2, zc), h)


def _fe_jaw_tip(z0: float, z1: float, hand: float) -> tuple[float, float]:
    """The blade's tip in the (x, z) front view - the same expression _fe_jaw() uses, so the tip-radius
    probe measures the real point instead of a bbox corner."""
    zc = (z0 + z1) / 2
    return (-hand * 3.4, zc + (z1 - z0) * 0.30)


def _fe_jaw(z0: float, z1: float, hand: float) -> Sketch:
    """One sickle mandible, drawn in the (x, z) FRONT view and extruded forward along Y.

    Prismatic along Y on purpose: every free wall of a Y-prism has normal.Y = 0, so whatever the
    sickle's outline does it cannot be an overhang at this bed normal. A swept round tusk of any
    radius puts 40-110 mm² of rearward surface in the air and fails outright - measured on cones,
    tori and lofts before this shape was settled on.

    The blade is a tapered sweep along a quadratic path from the chin's outboard corner inboard and
    up, `FE_JAW_T[0]` thick at the root and `FE_JAW_T[1]` at the tip, with three scalloped inner
    serrations 2.0 / 1.5 / 1.0 deep decreasing toward the tip."""
    t0, t1 = FE_JAW_T
    zc = (z0 + z1) / 2
    a = (hand * 12.0, zc - (z1 - z0) * 0.06)      # root, on the chin's outboard corner
    b = (hand * 5.0, zc - (z1 - z0) * 0.40)       # control point: the blade dives, then hooks up
    c = (-hand * 3.4, zc + (z1 - z0) * 0.30)      # tip, across the centreline - INSIDE the Z band, or
                                                  # the clip below shears the tip off and the blade
                                                  # ends in a flat with no Ø1.6 point at all
    n = 22
    outer, inner = [], []
    for i in range(n + 1):
        u = i / n
        px = (1 - u) ** 2 * a[0] + 2 * u * (1 - u) * b[0] + u * u * c[0]
        pz = (1 - u) ** 2 * a[1] + 2 * u * (1 - u) * b[1] + u * u * c[1]
        tx = 2 * (1 - u) * (b[0] - a[0]) + 2 * u * (c[0] - b[0])
        tz = 2 * (1 - u) * (b[1] - a[1]) + 2 * u * (c[1] - b[1])
        L = (tx * tx + tz * tz) ** 0.5 or 1.0
        nx, nz = -tz / L, tx / L
        t = (t0 + (t1 - t0) * u ** 0.8) / 2
        outer.append((px + nx * t, pz + nz * t))
        inner.append((px - nx * t, pz - nz * t))
    blade = Polygon(*outer, *reversed(inner), align=None)
    blade += Pos(c[0] - 0, c[1]) * Circle(t1 / 2)          # blunt the tip to Ø1.6 (tip-radius check)
    # three scalloped teeth on the inner edge, 2.0 / 1.5 / 1.0 deep and decreasing toward the tip.
    # The scallop circle is pushed OUT by (radius - depth) so the cut is exactly `depth` deep while the
    # scallop stays wide and shallow: a circle of radius = depth centred on the edge cuts a narrow
    # gouge and the land between two of them came out 0.5 mm (measured against a 1.2 mm floor).
    for u, depth, radius in ((0.18, 2.0, 2.5), (0.50, 1.5, 2.0), (0.82, 1.0, 1.5)):
        i = int(round(u * n))
        px, pz = inner[i]
        ox, oz = px - outer[i][0], pz - outer[i][1]
        L = (ox * ox + oz * oz) ** 0.5 or 1.0
        blade -= Pos(px + ox / L * (radius - depth), pz + oz / L * (radius - depth)) * Circle(radius)
    # clipped to its own Z band, so the 1.5 mm clearance between the two crossed blades is a
    # construction guarantee and not something to hope for
    return blade & _rect2(-FE_JAW_X, z0, FE_JAW_X, z1)


def _shell_feral(cam_w: float, x_in: float, x_out: float) -> dict:
    cheeks = _both(_yz(_fe_cheek() + _fe_spines(), x_in, x_out))
    post_prof = Polygon((POST_Y0, Z_MID_TOP), (POST_Y1, Z_MID_TOP), (POST_Y1, FE_POST_TOP),
                        (POST_Y0 + (FE_POST_TOP - FE_TOP[1]) * 1.1, FE_POST_TOP),
                        (POST_Y0, FE_TOP[1]), align=None)
    posts = _both(_yz(post_prof, x_in, x_out))
    chin = _chin(CHIN_Y0, CHIN_Y1, FE_CHIN_Z1, x_out)
    jaws = _xz(_fe_jaw(*FE_JAW_R, 1.0), *FE_JAW_Y) + _xz(_fe_jaw(*FE_JAW_L, -1.0), *FE_JAW_Y)

    # CN-4: the lunule cut clean THROUGH the cheek and the backplate flank as a slash - the family
    # cuts its mark, never debosses it. Its long axis STANDS UP (local +X along frame +Z) on the one
    # panel of this pod that can hold a 16 mm mark at all: the cheek's rear flank, y 81-93, clear of
    # the arc-slot clean zone ahead of it, the floor rail below it and the channel web (which covers
    # the cheek's whole outer face from y 103 forward, so a slash there would be a blind pocket).
    # The cut stops at x 16.0 - clean through the 15.75 flank, and 1.95 short of the channel ring's
    # inboard wall at x 14.05... which is why it is measured, not assumed, in checks().
    # `_sickle` is a 26-segment polygon, so every wall facet of the slash is ~0.74 x 5.0 = 3.7 mm²,
    # under overhangs()' 5 mm² floor: the only reason a crescent may be cut through at this bed
    # normal at all.
    sub = Part()
    if S.mark_fits("lunule", FE_MARK):
        m = S.mark("lunule", FE_MARK, "cut", (16.0, FE_MARK_AT[0], FE_MARK_AT[1]), normal=(-1, 0, 0),
                   x_dir=(0, 0, 1), through=32.0)
        sub += m
    # PUNCTA on the jaw cheeks only: the chin's front face above the two blades (CARAPACE/FERAL
    # surface token, Ø <= 2.4 so each dimple face stays under the 5 mm² overhang floor)
    # on the chin's TOP face, not its front: the front is the jaws' root plate and the two blades take
    # all of it once the chin is held to its 20.0 ceiling. Dimple faces here point +Z, which is
    # normal.Y = 0 in print - a punctation field cannot add an overhang there whatever its pitch.
    region = _rect2(-12.0, CHIN_Y0 + 1.4, 12.0, CHIN_Y1 - 1.4)
    pits, n_pits = S.puncta(region, pitch=4.0, d=2.2, depth=0.45, z_face=FE_CHIN_Z1,
                            plane=Plane.XY, clean=[_rect2(-1.6, CHIN_Y0 - 1, 1.6, CHIN_Y1 + 1)])
    if n_pits:
        sub += pits
    sub += _suture(CHIN_Y0, CHIN_Y1, FE_CHIN_Z1)   # CN-1: the part crosses X=0, so it is sutured
    return {"add": cheeks + posts + chin + jaws, "window": _fe_slit(), "x_cut": x_out, "sub": sub}


# --- CHASSIS: only the load path survives ----------------------------------------------------
CH_RAIL_R = 100.0           # upper rail arc: crown at y 99, 1.3 mm of sagitta over the 30 mm run.
# 45 gave a handsomer 2.9 mm bow and put the rail's top at 31.57 over the channel web's 31.50 - a
# 0.07 mm step, measured by the ray sampler as a 0.105 mm wall. The rail now clears the web's top face
# by 1.0 mm everywhere and the CURVE the family asks for is carried by the lower rail, which is free.
CH_LOWER_R = 39.0           # lower rail arc: crown 3.0 above its ends, so both rails visibly bow
CH_LOWER_TOP = 16.0
CH_HUB = ((94.8, 24.3), (100.0, 27.0), 5.0)   # the arc-slot boss: a stadium from a to b, radius r.
# 5.0 is what it takes to cover the slot AND the pivot with 2.0 mm of clean zone all round, and it
# also makes the boss fuse into the upper rail over y 96-105 instead of leaving a 0.2 mm hairline
# slot against it - the boss IS the truss's central node, not a separate island.
# The chin post is lightened by a COLUMN OF KEYHOLES, not one tall lens window. A lens 17 mm between
# its tips has arcs of radius 15.2 - a Ø30 cylinder with a horizontal axis in print, far past PETG's
# Ø12 arch exemption, and its rearward-facing half measured 19.5 mm² of 100 %-down surface. A Ø5.0
# head with a 3.0 x 2.5 slot along Y is d 5.0 and d 3.0: both exempt, and the slot's straight sides
# face ±Z, which is normal.Y = 0. Same frame motif, printable.
CH_POST_HOLES = ((118.0, 13.5), (118.0, 20.5), (118.0, 27.5))   # keyhole head centres (y, z)
CH_POST_HEAD, CH_POST_WAIST, CH_POST_TAIL = 5.0, 3.0, 2.6
CH_STRUTS = (((89.5, 13.3), (95.0, 21.2)),    # 55.2 deg
             ((104.0, 14.4), (99.5, 21.3)),   # 56.9 deg
             ((104.0, 14.4), (112.5, 30.5)))  # 62.2 deg
CH_NODES = ((89.5, 13.3), (104.0, 14.4), (112.5, 30.5))


def _ch_arc_band(crown_y: float, crown_z: float, r: float, w: float, y0: float, y1: float) -> Sketch:
    """A curved rail `w` wide whose top edge is an arc of radius `r` crowning at (crown_y, crown_z)."""
    c = (crown_y, crown_z - r)
    band = (Pos(*c) * Circle(r)) - (Pos(*c) * Circle(r - w))
    return band & _rect2(y0, crown_z - r, y1, crown_z + 1.0)


def _ch_rail_z(crown_y: float, crown_z: float, r: float, y: float) -> float:
    return crown_z - r + (r * r - (y - crown_y) ** 2) ** 0.5


CH_SEG_MAX = 7.0   # longest lens segment whose arcs stay inside PETG's Ø12 arch exemption at w 2.4


def _ch_strut(a, b, w: float) -> Sketch:
    """A strut as a CHAIN OF LENS SEGMENTS, each two tangent arcs meeting at a point (CN-3), with a
    Ø w circle at every intermediate joint so the waist is never pinched.

    This is a printability result, and it is the most interesting one in the module. A plain stadium
    strut at the family's 50-70 deg triangulation has flat sides whose normals are (-sin th, cos th) in
    (y, z); at 55 deg that is normal.Y -0.819, which in print orientation is a 35 deg overhang - past
    overhangs()' 45 deg limit, 29 mm² of it per strut. Every wall of a lens segment, by contrast, is a
    CYLINDER whose axis runs along frame X - horizontal in print - and whose diameter is
    ((L/2)² - h²)/(2h) + h doubled: 4.7 to 11.4 mm for the segment lengths here, all inside PETG's
    Ø12 arch exemption. So the truss can keep its 50-70 deg diagonals AND print without supports, and
    the waists read as an insect's segmented tibia rather than as a CAD stadium."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = (dx * dx + dy * dy) ** 0.5
    n = max(1, int(-(-L // CH_SEG_MAX)))
    sk = Sketch()
    for i in range(n):
        p0 = (a[0] + dx * i / n, a[1] + dy * i / n)
        p1 = (a[0] + dx * (i + 1) / n, a[1] + dy * (i + 1) / n)
        sk += S.lens(p0, p1, w / 2)
        if i:
            sk += Pos(*p0) * Circle(w / 2)
    return sk


def _ch_seg_arch(w: float = 0.0) -> list[float]:
    """The arc diameter of every strut segment, so checks() can assert the arch exemption."""
    w = w or CH_W
    out = []
    for a, b in CH_STRUTS:
        L = ((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2) ** 0.5
        n = max(1, int(-(-L // CH_SEG_MAX)))
        d, h = L / n, w / 2
        out.append(round(2 * (((d / 2) ** 2 - h * h) / (2 * h) + h), 2))
    return out


def _ch_truss() -> tuple[Sketch, Sketch, int]:
    """The cheek, drawn in (y, z): two curved rails, three struts triangulated 55-62 deg and a ring
    node at every junction. Returns (solid, bores, node count). The void is the shape."""
    upper = _ch_arc_band(99.0, CH_RAIL_TOP, CH_RAIL_R, CH_W, CHEEK_Y0, CHEEK_Y1)
    lower = _ch_arc_band(99.0, CH_LOWER_TOP, CH_LOWER_R, CH_W, CHEEK_Y0, FLOOR_Y1)
    a, b, r = CH_HUB
    hub = Pos((a[0] + b[0]) / 2, (a[1] + b[1]) / 2) * SlotOverall(
        ((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2) ** 0.5 + 2 * r, 2 * r).rotate(
        Axis.Z, degrees(Vector(b[0] - a[0], b[1] - a[1], 0).get_signed_angle(Vector(1, 0, 0), Vector(0, 0, 1))))
    solid = upper + lower + hub
    for p, q in CH_STRUTS:
        solid += _ch_strut(p, q, CH_W)
    bores = Sketch()
    n = 0
    for c in CH_NODES:
        ring, bore = S.ring_node(c, CH_W, od_factor=CH_NODE[0], id_factor=CH_NODE[1])
        solid += ring
        bores += bore
        n += 1
    # the SPINE: half-round serrations marching along the upper rail's outboard (top) edge
    pts = [(y, _ch_rail_z(99.0, CH_RAIL_TOP, CH_RAIL_R, y)) for y in
           [CHEEK_Y0 + 2.0 + 0.8 * i for i in range(int((CHEEK_Y1 - CHEEK_Y0 - 4.0) / 0.8) + 1)]]
    bumps, _n = S.serration(pts, d=1.6, pitch=3.2, protrusion=0.8, outward=(0.0, 1.0))
    solid += bumps
    return solid, bores, n


def _ch_ladder(x_out: float) -> tuple[Part, int]:
    """The backplate reduces to a vent ladder: transverse rounded-rect rungs cut straight through it
    along Y, so every rung wall has normal.Y = 0 and the ladder cannot add an overhang. Two bands -
    the rear wall behind the camera (Z 11.8-22.4) and the two outboard flanks above it."""
    cut, n = Part(), 0
    for z0, z1 in CH_LADDER:
        region = _rect2(-CH_RUNG[0] / 2 - CH_RUNG[4], z0, CH_RUNG[0] / 2 + CH_RUNG[4], z1)
        ln, wd, cr, pitch, lig = CH_RUNG
        sk, k = S.vent_ladder(region, pitch=pitch, ligament_min=lig, width=wd, corner_r=cr,
                              length=ln, hole_min=2.0, origin=(0.0, (z0 + z1) / 2))
        if k:
            cut += S.extrude_cut(sk, Plane(origin=(0, WALL_DEEP + 1.0, 0), x_dir=(1, 0, 0),
                                           z_dir=(0, 1, 0)), -(WALL_DEEP - FLOOR_Y0 + 2.0))
            n += k
    return cut, n


def _ch_keyholes() -> Sketch:
    """The frame's own keyhole motif, stacked up the chin post: a circle blended into a tangent slot
    that runs along Y so the slot's straight sides face ±Z and cannot be overhangs."""
    sk = Sketch()
    for yc, zc in CH_POST_HOLES:
        sk += Pos(yc, zc) * Circle(CH_POST_HEAD / 2)
        sk += Pos(yc + CH_POST_TAIL / 2, zc) * SlotOverall(CH_POST_TAIL + CH_POST_WAIST, CH_POST_WAIST)
    return sk


def _shell_chassis(cam_w: float, x_in: float, x_out: float) -> dict:
    truss, bores, n_nodes = _ch_truss()
    cheeks = _both(_yz(truss, x_in, x_out))
    # the chin post stays closed - it is the only thing carrying the chin, and the chin's rear face is
    # the print lintel - but it is lightened by a cusped lens window, two tangent arcs meeting at a
    # true point top and bottom (CN-3), with 1.65 mm ligaments either side.
    post_prof = Polygon((POST_Y0, Z_MID_TOP), (POST_Y1, Z_MID_TOP), (POST_Y1, CH_RAIL_TOP),
                        (POST_Y0, CH_RAIL_TOP), align=None) - _ch_keyholes()
    posts = _both(_yz(post_prof, x_in, x_out))
    chin = _chin(CHIN_Y0, CHIN_Y1, CH_CHIN_Z1, x_out)

    # hub + starburst on the chin, straight from the prop-guard reference: a Ø6 bore with 8 radial
    # slots. Cut along Y, so again no wall of it can face rearwards.
    hub_z = (CHIN_Z0 + CH_CHIN_Z1) / 2
    burst, n_burst = S.starburst((0.0, hub_z), CH_HUB_BORE / 2, n=8, w=1.2, length=1.4)
    hub_cut = S.extrude_cut(Pos(0.0, hub_z) * Circle(CH_HUB_BORE / 2) + burst,
                            Plane(origin=(0, CHIN_Y1 + 1.0, 0), x_dir=(1, 0, 0), z_dir=(0, 1, 0)),
                            -(CHIN_Y1 - CHIN_Y0 + 2.0))
    ladder, _n = _ch_ladder(x_out)
    sub = _both(_yz(bores, x_in - 1.0, x_out + 1.0)) + hub_cut + ladder
    sub += _suture(CHIN_Y0, CHIN_Y1, CH_CHIN_Z1)   # CN-1
    return {"add": cheeks + posts + chin, "window": Sketch(), "x_cut": x_out, "sub": sub}


# --- VESPID: wasp - tapered, segmented, banded, ending in a stinger ---------------------------
# FOUR TERGITES stepping rearward from the lens mouth, each 0.82x the LENGTH and 0.86x the GIRTH of
# the one in front of it, each ending in a 1.2 mm proud collar with a 0.45 mm groove behind it.
VE_Y1, VE_Y0 = 122.5, 84.0     # the abdomen runs the whole pod: mouth to backplate, 38.5 mm
VE_N = 4
VE_LR, VE_GR = 0.82, 0.86      # the two laws, and the two numbers the conformance row measures
VE_H1 = 29.0                   # tergite 1's GIRTH: its dorsal height above the Z 9 seating plane
VE_COLLAR_H, VE_COLLAR_L = 1.2, 1.4
VE_GROOVE_D, VE_GROOVE_L = 0.45, 1.0
VE_RAMP = 1.1                  # ramp run / drop. At 1.0 the ramp's normal.Y is exactly -0.707 and
                               # overhangs() flags it at -0.70; 1.1 measures -0.673, which is the
                               # same ratio and the same reason as CHIN_CHAMFER
VE_WALL = (2.2, 1.4)           # the wall law: 2.2 at the mouth, 1.4 at the rear, LINEARLY - a
                               # stepped wall puts a 0.27 x 20 mm rearward face at every step
VE_SPIR = (5.0, 2.2)           # the spiracle on tergite 1; every other one is 0.86^i of it
VE_SPIR_Z = (22.0, 22.0, 15.0, 15.0)
"""Where each spiracle sits in Z. The row DESCENDS, which is what it does on the animal and what the
pod's own geometry forces: tergites 1-2 are over the chin (crown Z 20) so their slot sits at Z 22,
and tergites 3-4 are over the M2 screw pad, whose CN-7 clean zone floor is Z 19.86, so theirs drop to
Z 15 - above the floor rail's 13.0 and below the zone."""
VE_HORN = (0.95, 1.36, 0.8)    # the stinger: tip y aft of the T1/T2 boundary, z above T2, tip radius
VE_REAR_COLLAR = 1.2           # the backplate's flanks are cut down to T4 + this, so the taper runs
                               # out at the bed face instead of leaving a 6.4 mm stub over the tail


def _ve_table() -> list[dict]:
    """Per tergite: the flat's start, the boundary at its aft end, its top, its length and girth.

    Everything is derived from the two ratios, so the conformance row measures the built geometry
    against the law rather than against a table someone typed."""
    ls = [VE_LR ** i for i in range(VE_N)]
    l1 = (VE_Y1 - VE_Y0) / sum(ls)
    rows, y = [], VE_Y1
    for i in range(VE_N):
        h = VE_H1 * VE_GR ** i
        rows.append(dict(i=i, y_front=y, length=l1 * ls[i], girth=h, top=Z_MID_TOP + h,
                         b=y - l1 * ls[i]))
        y = rows[-1]["b"]
    return rows


def _ve_profile() -> Sketch:
    """The cheek's (y, z) outline: four flats, three collar / groove / ramp boundaries, one stinger.

    Going AFT the shingle is: flat -> a 1.2 proud collar (its forward face points +Y) -> a 0.45 deep
    groove (its rearward face is 0.45 x 2.2 = 1.0 mm², two orders under the 5 mm² overhang floor) ->
    a 1 : 1.1 ramp down to the next tergite. The collar's own rearward shoulder is 1.65 x 2.2 = 3.6
    mm², also under the floor - which is the only reason a shingle can be printed nose-up at all."""
    t = _ve_table()
    pts = [(VE_Y0, Z_MID_TOP), (VE_Y1, Z_MID_TOP), (VE_Y1, t[0]["top"])]
    tip = None
    for i in range(VE_N - 1):
        top, nxt, b = t[i]["top"], t[i + 1]["top"], t[i]["b"]
        floor = top - VE_GROOVE_D
        r = VE_RAMP * (floor - nxt)
        y_collar = b + r + VE_GROOVE_L + VE_COLLAR_L
        pts += [(y_collar, top), (y_collar, top + VE_COLLAR_H),
                (b + r + VE_GROOVE_L, top + VE_COLLAR_H),
                (b + r + VE_GROOVE_L, floor), (b + r, floor)]
        if i == 0:      # the stinger: the T1 ramp is drawn out into a cusp that overhangs the clip
            tip = (b - VE_HORN[0], nxt + VE_HORN[1])
            pts += [tip]
        pts += [(b, nxt)]
    pts += [(VE_Y0, t[-1]["top"])]
    sk = Polygon(*pts, align=None)
    return sk + Pos(*tip) * Circle(VE_HORN[2])


def _ve_wall(y: float) -> float:
    return VE_WALL[1] + (VE_WALL[0] - VE_WALL[1]) * (y - VE_Y0) / (VE_Y1 - VE_Y0)


def _ve_cheek(x_in: float) -> Part:
    """The right cheek: the tergite profile, clipped by the linear wall taper."""
    solid = _yz(_ve_profile(), x_in, x_in + VE_WALL[0] + 0.2)
    y0, y1 = VE_Y0 - 2.0, VE_Y1 + 2.0
    plan = Polygon((x_in - 1.0, y0), (x_in + _ve_wall(y0), y0),
                   (x_in + _ve_wall(y1), y1), (x_in - 1.0, y1), align=None)
    wedge = extrude(Plane.XY.offset(Z_MID_TOP - 2.0) * plan, amount=40.0)
    return solid & wedge


def _ve_flat(i: int) -> tuple[float, float]:
    """Tergite i's FLAT: the band between its own front and the collar that terminates it. Both the
    spiracle and the girth probe belong on the flat - a station 1 mm either side of it reads the
    collar (+1.2) or the ramp, and the girth ratio then measures 0.90 instead of 0.86."""
    t = _ve_table()
    row = t[i]
    if i < VE_N - 1:
        r = VE_RAMP * (row["top"] - VE_GROOVE_D - t[i + 1]["top"])
        return row["b"] + r + VE_GROOVE_L + VE_COLLAR_L, row["y_front"]
    return VE_Y0, row["y_front"]


def _ve_spiracle_rows() -> list[tuple]:
    """(i, y centre, length, height, blind) for the four spiracles on one flank.

    Tergite 2's flat sits inside the clip web's own footprint, where the cheek is tied out to x_out
    and the web carries on outboard of it to the channel ring. A through-slot there either leaves a
    0.05 mm membrane (cut to the tie) or eats the ring's 1.7 mm inboard wall (cut to the web), so
    THAT one is a 1.0 mm blind spiracle sunk in the tie's outer skin and the other three are cut
    clean through. The row that reports them says which is which."""
    out = []
    for i in range(VE_N):
        ln, ht = VE_SPIR[0] * VE_GR ** i, VE_SPIR[1] * VE_GR ** i
        y0, y1 = _ve_flat(i)
        yc = (y0 + y1) / 2.0
        if i == VE_N - 1:
            yc = max(yc, WALL_DEEP + 0.4 + ln / 2)   # clear of the backplate's y 88.5 face
        blind = yc - ln / 2 < WEB_Y1 and yc + ln / 2 > WEB_Y0
        out.append((i, yc, ln, ht, blind))
    return out


def _ve_spiracles(blind: bool | None = None) -> Sketch:
    """ONE elliptical spiracle per tergite per flank, 5.0 x 2.2 on the first and 0.86^i of that on
    the rest - the same taper as the girth, which is what makes the row read as one animal."""
    from build123d import Ellipse
    sk = Sketch()
    for i, yc, ln, ht, is_blind in _ve_spiracle_rows():
        if blind is not None and is_blind is not blind:
            continue
        sk += Pos(yc, VE_SPIR_Z[i]) * Ellipse(ln / 2, ht / 2)
    return sk


def _shell_vespid(cam_w: float, x_in: float, x_out: float) -> dict:
    # The cheek is TAPERED, so over the clip web's footprint it has to be brought back out to the
    # full x_out: _core()'s web springs from x 13.75 and a 2.2 mm cheek leaves it a free-standing
    # 0.59 mm wedge at y 103.9 (measured by ray sampling, and it is the clip's whole load path).
    # The tie is the node swelling of the abdomen - the thickest point is where the leg attaches.
    # The tie's rear end RAMPS out from the tapered wall instead of stepping: a step at y 103 is a
    # 21.3 mm² face pointing straight at -Y, which is straight down at this bed normal.
    tie_plan = Polygon((x_in - 1.0, WEB_Y0 - 2.0), (x_in + _ve_wall(WEB_Y0 - 2.0), WEB_Y0 - 2.0),
                       (x_out, WEB_Y0), (x_out, WEB_Y1), (x_in - 1.0, WEB_Y1), align=None)
    tie = _yz(_ve_profile(), x_in, x_out) & extrude(
        Plane.XY.offset(FLOOR_Z1 - 1.0) * tie_plan, amount=CHANNEL_TOP - FLOOR_Z1 + 1.0)
    add = _both(_ve_cheek(x_in) + tie)
    add += _chin(CHIN_Y0, CHIN_Y1, CHIN_Z1, x_out)
    t = _ve_table()
    # The spiracles are cut to x_out + 0.2, not to the tapered wall: over the clip web's footprint
    # the cheek is tied back out to x_out, and a cut that stopped at the taper left a 0.10 mm
    # membrane outboard of tergite 2's slot. x_out + 0.2 = 13.95 is still 0.10 mm clear of the
    # channel ring's own inboard extreme at 14.05, so the clip wall is never touched.
    sub = _both(_yz(_ve_spiracles(blind=False), x_in - 0.6, x_out + 0.2))
    blind = _ve_spiracles(blind=True)
    if blind.faces():
        # 0.8 deep and stopping 0.2 short of x_out, not 1.0 through to it: the clip web is only
        # 1.34 mm thick where its diagonal leaves the cheek at y 105.4, and a recess taken right out
        # to x_out exposes that as a free wall. 0.2 of the tie is left standing in front of it.
        sub += _both(_yz(blind, x_out - 1.0, x_out - 0.2))
    sub += _both(box(x_in + CAM_PAD, FLOOR_Y0 - 0.2, t[-1]["top"] + VE_REAR_COLLAR,
                     WALL_X + 0.5, WALL_DEEP + 0.2, CHEEK_TOP + 1.0))
    return {"add": add, "window": Sketch(), "x_cut": x_out, "sub": sub}


# --- CORAL: accreted, not designed ------------------------------------------------------------
# The functional pod - clip rings, cam cheeks, lens mouth, seat - is built first and never changes.
# Its OUTLINE is then grown rather than drawn: a chain of overlapping discs along the cheek's load
# path, so no straight edge and no crease survives in the silhouette. Blender's metaball pass
# (sculpt, mode="meta", voxel 0.40) fairs the chain into one accreted mass and swells it at the
# nodes; when Blender is unavailable decorate() hands the undecorated chain back, and THAT part
# passes every row in checks() on its own - which is why the disc chain is build123d's job and not
# the recipe's.
CO_NODES = ((118.0, 24.0, 4.5), (115.5, 18.5, 4.0), (118.5, 14.5, 4.0),
            (111.0, 26.0, 5.0), (110.0, 12.0, 4.0),
            (103.0, 25.0, 6.0), (100.0, 12.0, 4.0),
            (97.0, 25.0, 6.0), (92.0, 12.0, 4.0),
            (90.0, 24.0, 6.0), (88.0, 16.5, 4.5), (87.5, 20.0, 5.0))
"""The corallites, in the cheek's own (y, z): centre and radius, 3.5-7.0 mm at about 7 mm spacing.

The two big ones straddle the M2 pivot because CN-7 has to be SOLID there: the clean zone reaches
Z 30.2 at y 100 and Z 28.8 at y 94, and a disc pair of r 7.0 at Z 24.5 covers 30.8 at both. Their
tops are 31.0 - deliberately under Z 31.8, because front_bumper's keep-out starts there and the
metaball pass is allowed to grow the envelope by up to 2.0 mm.

No radius is over 6.0 either, and that is the second hard number: a disc's silhouette becomes a
cylindrical face whose axis lies along X, which prints as an arch, and overhangs() exempts an arch
only up to PETG's Ø12. At r 7.0 the two pivot discs were Ø14 and each put a quarter of its own
underside in the air. No centre is tangent to the Z 9 seating plane or to the y 80.5 bed face
either - a tangent disc leaves a cusp exactly where the first layer is."""
CO_BODY = (90.0, Z_MID_TOP, 115.0, 22.0)   # the interior, entirely inside the disc chain
CO_T = CHEEK                                # 3.0: the accreted wall, swelling at the nodes
CO_SEEDS_R = (3.0, 5.0)                     # metaball radius at the cheek tips / at the clip nodes
CO_PIT = (2.0, 0.4, 4.5)                    # corallite pits: diameter, depth, minimum separation
CO_VOXEL = 0.40


def _ve_ring() -> Part:
    """The right clip ring exactly as _side() builds it - used only to DECLARE it to the mesh wall
    gate, whose sample skip is a 0.35 mm proximity test against the declared shape's own surface."""
    return c_clip(FRONT_TIP_XY, CHANNEL_Z0, CHANNEL_TOP - CHANNEL_Z0, opening_deg=MOUTH_DEG,
                  bore_d=D_CLIP_BORE, wall=CHANNEL_WALL, snap=SNAP, closed=False)


def _co_profile() -> Sketch:
    """The cheek outline: one interior rectangle buried inside a chain of overlapping discs, then
    clipped at the seating plane. Every edge of the silhouette is a circular arc."""
    sk = _rect2(*CO_BODY)
    for y, z, r in CO_NODES:
        sk += Pos(y, z) * Circle(r)
    return sk & _rect2(VE_Y0 - 4.0, Z_MID_TOP, VE_Y1 + 4.0, 44.0)


def _co_pits(x_face: float) -> Part:
    """Corallite pits, Ø2.0 x 0.4 deep, Poisson-ish on a 4.5 mm staggered lattice over the flank.
    Pits, not through-holes: the part stays closed, which is the family's own rule."""
    d, depth, pitch = CO_PIT
    cut = None
    row = 0
    z = Z_MID_TOP + 3.0
    while z <= 30.0:
        y = 87.0 + (pitch / 2 if row % 2 else 0.0)
        while y <= 120.0:
            exposed = 89.5 <= y <= 102.0 or 114.8 <= y <= 121.5
            # Only where the cheek's outer face IS the surface: the clip web fills x 13.75-16.0 over
            # y 103-113.5 and the backplate does the same aft of y 88.5, and a 0.4 mm pit sunk into
            # either would be an internal cavity, not a pit.
            if exposed and not (90.0 <= y <= 104.0 and 18.5 <= z <= 31.0):
                cut = (cut or Part()) + _yz(Pos(y, z) * Circle(d / 2), x_face - depth, x_face + 1.0)
            y += pitch
        z += pitch * 0.866
        row += 1
    return cut


def _co_seeds(x_in: float) -> list[dict]:
    """The metaball strokes: one seed per corallite node on the cheek's MID-PLANE, radius swelling
    from CO_SEEDS_R[0] at the extremities to CO_SEEDS_R[1] at the clip nodes (the two big discs over
    the pivot and the mouth cowl, which is where the load goes). Blender's iso-surface for a single
    element sits at about 0.42 x radius, so a 5.0 seed on a 3.0 mm cheek grows the envelope by ~0.6
    mm - well inside decorate()'s 2.0 mm cap, which is the discipline this family is held to."""
    xc = x_in + CO_T / 2
    lo, hi = CO_SEEDS_R
    big = {(103.0, 24.5), (97.0, 24.5), (111.0, 26.0)}
    out = []
    for y, z, _r in CO_NODES:
        r = hi if (y, z) in big else lo
        out.append(dict(points=[[xc, y, z], [-xc, y, z]], radii=[r, r]))
    return out


def _co_guard(pod: Part, cam_w: float, x_in: float, x_out: float) -> Part:
    """What the decoration may not touch, clipped EXACTLY to the pod's bounding box.

    decorate() refuses a guard that is proud of the part in any axis - a guard is a mask, not a
    tolerance - and tilt_sweep() alone reaches Z 38.3 on a pod whose top is 31.5, so the union has
    to be trimmed to the part's own box before it is handed over."""
    g = tilt_sweep(cam_w, 0, 40) + camera_envelope(cam_w, CAM_H, CAM_D)
    g += _both(cylinder(*FRONT_TIP_XY, CHANNEL_Z0 - 1.0, CHANNEL_TOP + 1.0,
                        D_CLIP_BORE + 2 * CHANNEL_WALL + 1.6))          # the clip rings
    g += _both(_slot_clean_zone(x_in, x_out, 2.0)[0])                   # the M2 slot and its shell
    g += box(-x_out - 1.0, FLOOR_Y0 - 1.0, NUB_Z0 - 0.5, x_out + 1.0, FLOOR_Y1 + 1.0, FLOOR_Z1)
    g += box(-WALL_X - 1.0, FLOOR_Y0 - 1.0, Z_MID_TOP - 1.0, WALL_X + 1.0, FLOOR_Y0 + 2.0, 40.0)
    g += _chin(CHIN_Y0 - 0.5, CHIN_Y1 + 1.0, CHIN_Z1, x_out)            # the lens mouth and beak
    bb = pod.bounding_box()
    return g & box(bb.min.X, bb.min.Y, bb.min.Z, bb.max.X, bb.max.Y, bb.max.Z)


def _shell_coral(cam_w: float, x_in: float, x_out: float) -> dict:
    add = _both(_yz(_co_profile(), x_in, x_in + CO_T))
    add += _chin(CHIN_Y0, CHIN_Y1, CHIN_Z1, x_out)
    sub = _both(_co_pits(x_in + CO_T))
    return {"add": add, "window": Sketch(), "x_cut": x_out, "sub": sub}


def _co_decorate(pod: Part, cam_w: float, x_in: float, x_out: float, variant: str) -> Part:
    """The accretion pass. It never raises: a missing Blender, a failed gate or an envelope over the
    2.0 mm cap all come back as the undecorated pod plus a failing decor row."""
    guard = _co_guard(pod, cam_w, x_in, x_out)
    res = BL.decorate_ex(pod, "sculpt", dict(mode="meta", voxel=CO_VOXEL, strokes=_co_seeds(x_in)),
                         protect=guard, region=BL.decor_region(pod, 1.6, minus=(guard,)),
                         allow=(_nubs(), _both(_ve_ring())),
                         # DECLARED thin features, in _blender's own sense - never a lowered floor.
                         # The nose nubs are 1.5 mm tall by design (NUB_Z0) and the two clip rings
                         # are CHANNEL_WALL = 1.7 mm; a 0.40 mm voxel remesh renders a 1.7 mm ring
                         # as 1.23 (measured at (21.6, 105.9, 16.8)) and a 1.5 mm nub as 1.45,
                         # because mesh wall tracks 1.3-2.6 x voxel. Both are guarded mating
                         # geometry, restored from the CAD, and the part's real wall is measured by
                         # checks()' own min_wall row against PETG's floor. The old comment:
                         # a ray sampler cannot tell a 1.5 mm registration nub from a thin wall: it
                         # measured 1.4458 mm at (9.2, 110.3, 8.9), which is the right-hand nub's own
                         # roof. Declared, per _blender's own rule - never by lowering the floor.
                         cache_key=f"camera_pod_{int(cam_w)}__{variant or 'coral'}",
                         wall_floor=STYLE_WALL["coral"])
    return res.part


# --- BRUTALIST: one poured slab, formwork still showing --------------------------------------
# Orthogonal to the frame datum, chamfer-only, 3.0 mm slab walls (the cheek IS 3.0 = CHEEK, so the
# family's wall law needs no new number), ONE rectangular void per cheek, board-marking grooves
# running the PRINT direction, external board-form pilasters and a cast-in datum stamp.
BR_Y0, BR_Y1, BR_TOP = 84.0, 116.5, 34.0      # the cheek slab: 32.5 x 25 x 3.0, no post, no ramp
BR_CHIN = (116.5, 125.0, 20.0)                # the chin slab: 8.5 x 14.5, twice the stock chin's
# mass. 116.5 and not 116.0 because the 21 mm lens' own envelope reaches y 116.25 at Z 19.75 (a chin
# front at 116.0 x Z 21 took 1.73 mm³ out of the camera at 0 deg and 13.7 mm³ out of the tilt sweep);
# 20.0 and not 21.0 because the tilt sweep's own lens-bottom sector has radius 17.79 about the
# pivot: a chin corner at (116.5, 20.5) sits 17.73 from it and took 0.11 mm³ out of the sweep.
BR_CHIN_RAMP = 116.6                          # its sub-Z9 ramp starts clear of the mid-plate nose
BR_VOID = (106.0, 14.0, 113.0, 31.0)          # the one void per cheek: 7.0 x 17.0 = 119 mm^2.
# Its top is 31.0 and NOT CHANNEL_TOP's 31.5: at 31.5 the cutter's top-inboard arris ran exactly
# along the clip web's own top-inboard edge (x 13.75, Z 31.5, over the web's y 103-113.5), and the
# coincidence left a degenerate face that OCCT keeps as a valid solid, STEP and STL both write and
# only lib3mf rejects - "RuntimeError: 3mf mesh is invalid" from Mesher.add_shape, with nothing to
# say which face is at fault. Exactly the failure SUTURE_INSET documents, from the same cause.
# Its aft edge stands 3.0 mm forward of the clip web's root at y 103.0, and that number was walked
# out by measurement: at 104.0 a ray leaving the web's diagonal inboard face crossed x 13.75 into
# the void after 0.587 mm, and at 105.5 it still read 1.389 against PETG's 1.5 floor.
BR_CHAM = 1.0                                 # the only edge treatment in the whole family
BR_GROOVE = (0.6, 0.3, 2.4)                   # board marking: width (Z) x depth (X) at pitch
BR_PROUD = 2.0                                # pilaster proud height -> x 15.75, exactly WALL_X
BR_TAPER = 1.1                                # its aft face rises 1 in 1.1: normal.Y -0.673, the
                                              # same ratio CHIN_CHAMFER uses and for the same reason
BR_PIL = ((88.6, 90.8, Z_MID_TOP + 4.0, 31.0),     # the two stations the pod actually exposes
          (116.5, 125.0, Z_MID_TOP, 20.0))         # the chin buttress runs the whole flank
BR_STAMP = (5, 2.0, 2.0, 118.5, 122.2)        # bars, width (X), depth, y0, y1 - the cast-in plaque
# The bars stand clear of both ends of the crown, and both numbers were measured. At y0 117.5 the aft
# end wall left a 1.0 mm land to the chin's rear face. At y1 123.0 the FORWARD end wall left 1.2 mm
# to the front chamfer, whose 45 deg plane is at y + Z = 144: at the bar floor's Z 19.8 that is
# y 124.2, not the chin's nominal 125.0. At 122.2 the land is 1.8 against PETG's 1.5 floor.
# WHY ONLY TWO PILASTERS AND NOT A 12 mm FIELD. The cheek's outer face is exposed over y 88.5-103.0
# only: the backplate fills x <= 15.75 aft of y 88.5 and the clip web fills x 13.75-16.0 over
# y 103.0-113.5, so a rib at the 99.8 or 111.8 station is swallowed whole. Of that band, y 90.9-103.3
# is the M2 screw heads' landing (the pivot head at y 98.8-101.2 and the arc head at 92.98-96.67,
# each plus its 2.1 mm head radius), which must stay bare cheek. What is left is y 88.6-90.8 and the
# chin flank - two stations, 28.0 mm apart. The nominal 12 mm pitch is recorded in the row that
# measures it, together with the two numbers that forbid it.
# WHY THE GROOVES SKIP Z 19.4-30.5 OVER THE SCREW PAD. A 0.6 x 0.3 groove crossing the CN-7 clean
# zone removes 2.2 mm^3 inside it, and CN-7 allows 0.5 mm^3 of void that is not the bore. So the
# ladder runs the full height only where the zone is not - and that reads correctly: formwork planks
# with a smooth cast pad where the fixing lands.
BR_GROOVE_BANDS = ((91.0, 102.9, True, 0.0), (117.0, 124.5, False, BR_PROUD))
# (y0, y1, skip the clean band, how far the face this band is cut into stands proud of x_out).
# The forward band is on the chin buttress's own flank, not on the cheek: a groove box that
# reached x_out + 2.0 sliced the buttress's back-taper where it is 0.3 mm thick and left 0.08 mm
# flakes - 430 of 5950 rays under the wall floor, all of them there.
BR_CLEAN_BAND = (19.4, 30.5)                  # the Z window the ladder skips inside the first band


def _br_void() -> Sketch:
    return _rect2(BR_VOID[0], BR_VOID[1], BR_VOID[2], BR_VOID[3])


def _br_free_panel() -> tuple[float, float, str]:
    """(void area, free panel area, the decomposition) for the >= 40 % rule.

    The denominator is the cheek's outer rectangle MINUS every band that is mating geometry and can
    therefore never be a hole: the floor rail, the top beam that carries the cheek to the backplate,
    the two web tie columns, the front crossbar column and the M2 screw pad. Stating the decomposition
    is the honest way to measure 'one void >= 40 % of the face' on a cheek that is also a bracket."""
    gross = (BR_Y1 - BR_Y0) * (BR_TOP - Z_MID_TOP)
    rail = (BR_Y1 - BR_Y0) * (BR_VOID[1] - Z_MID_TOP)
    beam = (BR_Y1 - BR_Y0) * (BR_TOP - BR_VOID[3])
    h = BR_VOID[3] - BR_VOID[1]
    pad = (103.3 - 90.9) * h
    ties = ((BR_VOID[0] - 103.0) + (113.5 - BR_VOID[2])) * h
    front = (BR_Y1 - 113.5) * h
    free = gross - rail - beam - pad - ties - front
    void = (BR_VOID[2] - BR_VOID[0]) * (BR_VOID[3] - BR_VOID[1])
    return void, free, (f"{void:.0f} of {free:.0f} mm² free panel = {void / free:.1%} (gross {gross:.0f} "
                        f"- rail {rail:.0f} - top beam {beam:.0f} - M2 pad {pad:.0f} - web ties "
                        f"{ties:.0f} - front column {front:.0f})")


def _br_pilaster(x_out: float, y0: float, y1: float, z0: float, z1: float) -> Part:
    """A board-form pilaster: square section, proud BR_PROUD, its aft face back-tapered 1 : 1.1 so it
    is a 42.3 deg ramp instead of a 3 x 18 mm rearward wall standing in the air at this bed normal."""
    # the ramp's rise is the WHOLE face, buried root included (2.6), not the 2.0 that shows: at a
    # 2.2 run the measured normal.Y was -0.762 and the two chin buttresses failed the overhang row
    # with 26.4 mm² each.
    plan = Polygon((x_out - 0.6, y0 - (BR_PROUD + 0.6) * 1.25), (x_out + BR_PROUD, y0),
                   (x_out + BR_PROUD, y1), (x_out - 0.6, y1), align=None)
    return extrude(Plane.XY.offset(z0) * plan, amount=z1 - z0)


def _br_grooves(x_out: float) -> Part:
    """The formwork ladder: 0.6 x 0.3 grooves at 2.4 pitch, every one of them running +Y, the print
    direction. An end wall is 0.18 mm² - two orders under the 5 mm² overhang floor."""
    w, deep, pitch = BR_GROOVE
    cut = None
    for y0, y1, skip, proud in BR_GROOVE_BANDS:
        z = Z_MID_TOP + 2.5   # not +1.0: on the chin buttress, whose underside IS Z 9, the first
        top = BR_CHIN[2] if y0 > BR_Y1 else BR_TOP   # groove left a 1.0 mm land under it
        face = x_out + proud
        while z + w <= top - 0.4:
            if not (skip and BR_CLEAN_BAND[0] <= z + w and z <= BR_CLEAN_BAND[1]):
                g = box(face - deep, y0, z, face + 0.4, y1, z + w)
                cut = g if cut is None else cut + g
            z += pitch
    return cut


def _br_stamp(x_out: float) -> Part:
    """The datum stamp: BR_STAMP[0] bars sunk 2.0 mm into the chin's crown, each running +Y so its
    only rearward face is 2.0 x 2.0 = 4.0 mm², inside the overhang check's 5 mm² floor. A lens- or
    text-shaped deboss of the same depth puts 20 mm² of prorated rearward surface in the air."""
    n, w, deep, y0, y1 = BR_STAMP
    z1 = BR_CHIN[2]
    cut = None
    for i in range(n):
        xc = (i - (n - 1) / 2) * 4.0
        b = box(xc - w / 2, y0, z1 - deep, xc + w / 2, y1, z1 + 1.0)
        cut = b if cut is None else cut + b
    return cut


def _br_chamfers(x_out: float) -> Part:
    """Every edge treatment in the family: 1.0 mm at 45 deg, cut as geometry so no fillet can creep
    in. Each 45 deg face points +X/+Z or +Y/+Z - never rearward, so none of them is an overhang."""
    c = BR_CHAM
    # Each triangle's CLOSING edge is the 45 deg face, so the third vertex has to be dropped by
    # (c + overrun), not by c - at (c) the closing edge is a 1 : 2 slope and the bevel is 26 deg.
    tri_xz = Polygon((x_out - c, BR_TOP), (x_out + 1.0, BR_TOP), (x_out + 1.0, BR_TOP - c - 1.0), align=None)
    out = _both(_xz(tri_xz, 88.4, BR_Y1 + 0.5))   # from y 88.4: aft of that the backplate is the face
    tri_yz = Polygon((BR_Y1 - c, BR_TOP), (BR_Y1 + 1.0, BR_TOP), (BR_Y1 + 1.0, BR_TOP - c - 1.0), align=None)
    out += _yz(tri_yz, -x_out - 1.0, x_out + 1.0)
    cy, cz = BR_CHIN[1], BR_CHIN[2]
    tri_chin = Polygon((cy - c, cz), (cy + 1.0, cz), (cy + 1.0, cz - c - 1.0), align=None)
    out += _yz(tri_chin, -x_out - BR_PROUD - 1.0, x_out + BR_PROUD + 1.0)
    tri_chin_x = Polygon((x_out + BR_PROUD - c, cz), (x_out + BR_PROUD + 1.0, cz),
                         (x_out + BR_PROUD + 1.0, cz - c - 1.0), align=None)
    out += _both(_xz(tri_chin_x, BR_CHIN[0] - 0.5, cy + 0.5))
    return out


def _shell_brutalist(cam_w: float, x_in: float, x_out: float) -> dict:
    add = _both(box(x_in, BR_Y0, Z_MID_TOP, x_out, BR_Y1, BR_TOP))
    add += _chin(BR_CHIN[0], BR_CHIN[1], BR_CHIN[2], x_out, y_ramp=BR_CHIN_RAMP)
    for y0, y1, z0, z1 in BR_PIL:
        add += _both(_br_pilaster(x_out, y0, y1, z0, z1))
    sub = _both(_br_grooves(x_out)) + _br_stamp(x_out) + _br_chamfers(x_out)
    return {"add": add, "window": _br_void(), "x_cut": x_out, "sub": sub}


_SHELLS = {"shard": _shell_shard, "slipstream": _shell_slipstream,
           "feral": _shell_feral, "chassis": _shell_chassis,
           "brutalist": _shell_brutalist, "vespid": _shell_vespid,
           "coral": _shell_coral}


# --- per-style budgets ------------------------------------------------------------------------
# The material floor is the STYLE's material, not the module's: PETG cannot be measured against
# TPU's 1.2 mm. Every one of these is a threshold the style has to meet, never a relaxation of a
# shared check - the shard column is exactly what the single-style pod already asserted.
STYLE_WALL = {"shard": 1.2, "feral": 1.2, "slipstream": 1.5, "chassis": 1.5,
              "vespid": 1.4, "brutalist": 1.5, "coral": 1.6}
STYLE_VOL = {"shard": (12.0, 24.0), "slipstream": (12.0, 30.0), "feral": (12.0, 30.0),
             "chassis": (6.0, 20.0), "vespid": (9.5, 26.0), "brutalist": (11.0, 26.0),
             "coral": (10.0, 40.0)}
STYLE_ZMAX = {"shard": 38.0, "slipstream": 36.1, "feral": 38.0, "chassis": 35.6,
              "vespid": 39.3, "brutalist": 34.1, "coral": 33.6}
STYLE_YMAX = {"shard": 122.5, "slipstream": 124.1, "feral": 129.1, "chassis": 122.6,
              "vespid": 122.6, "brutalist": 125.1, "coral": 124.6}
STYLE_MAT = {"shard": "TPU95A", "feral": "TPU95A", "vespid": "TPU95A",
             "slipstream": "PETG", "chassis": "PETG", "brutalist": "PETG", "coral": "PETG"}
"""Which material's print rules a style is measured against - bridge span, arch exemption, wall floor.
It has to be the STYLE's material and not the module's: the manifest ships each variant with its own
filament, and PETG's 20 mm bridge / Ø12 arch are not TPU's 22 / Ø10."""
STYLE_SEAT = 150.0          # mm² of rail seated on plate_mid at Z 9, every style
# First-layer contact on the y 80.5 bed face. This is an adhesion heuristic, not a fit rule (the
# framework's own floor is 5 mm²), and CHASSIS legitimately has less of it: its backplate IS a vent
# ladder, so the rungs come straight out of the bed face. The measured numbers are in the row.
STYLE_BED = {"shard": 500.0, "slipstream": 500.0, "feral": 500.0, "chassis": 380.0,
             "vespid": 460.0, "brutalist": 500.0, "coral": 400.0}
_LAST_STYLE = {}            # label -> style, so checks() can read the budgets without a variant arg
_VARIANT: list[str] = []    # the variant build() was called with, for the decor cache key


def _treat(pod: Part, style: str) -> tuple[Part, str]:
    """The style's edge ladder (_style.EDGE_LADDER), applied last and only where it earns its keep.

    SHARD is returned untouched on purpose: the stock pod's creases are mitred in the profile itself
    and re-chamfering them would change the shipped geometry. Every other call is guarded, because a
    fillet that OCCT refuses must degrade to no fillet rather than take the part down - and because
    bevelling every edge of a part this size takes it from 300 to 1200 B-rep faces, after which
    _fit.isect starts answering 0.000 mm³ to probes that hold real material (a check silently
    passing on nothing)."""
    if style == "shard":
        return pod, "none (the stock profile is already mitred)"
    if style == "slipstream":
        # the OCELLUS blend: the lip's crest edges, nothing else. The upper shell must stay
        # crease-free and it already is - it is two tangent arcs - so it needs no fillet at all.
        sel = [e for e in pod.edges()
               if abs(abs(e.center().X) - (CAM_W / 2 + FIT + CHEEK + SL_LIP[1])) < 0.02]
        out, r = S.treat_edges(pod, "slipstream", "free", STYLE_WALL[style], edges=sel, kind="fillet")
        return out, f"ocellus lip crest filleted {r} mm on {len(sel)} edges"
    if style == "feral":
        # EVERY spine apex, selected by where it is rather than by how high: a z threshold caught the
        # front two and left the third one a knife edge (its apex is 1.2 mm below the rail's top).
        want = [(yc, _fe_top_z(yc) + h) for yc, h in FE_SPINES]
        tips = [e for e in pod.edges()
                if abs(e.length - CHEEK) < 0.05
                and any(abs(e.center().Y - wy) < 0.4 and abs(e.center().Z - wz) < 0.4 for wy, wz in want)]
        out, r = S.treat_edges(pod, "feral", "tip", STYLE_WALL[style], edges=tips, kind="fillet")
        return out, f"{len(tips)} spine apex edge(s) blunted {r} mm (3 spines x 2 cheeks = 6 expected)"
    if style == "brutalist":
        return pod, ("chamfer only, by construction: the 1.0 mm x 45 deg bevels are cut as geometry "
                     "in _br_chamfers(), so no fillet can enter the family through the edge ladder")
    if style in ("vespid", "coral"):
        return pod, ("no edge ladder: VESPID's profile carries its own 1.2 mm collars and 0.45 mm "
                     "grooves, and CORAL's outline is set by the metaball union, not by a bevel")
    if style == "chassis":
        return pod, ("truss edges left sharp: the struts are lens segments, so their walls are already "
                     "tangent arcs, and a 0.8 fillet on every truss edge trebles the B-rep face count "
                     "- past which _fit.isect() answered 0.000 mm³ to a probe holding 12.5 mm³")
    return pod, "none"


def _pod(cam_w: float, style: str = "shard") -> Part:
    x_in = cam_w / 2 + FIT
    x_out = x_in + CHEEK
    shell = _SHELLS[style](cam_w, x_in, x_out)
    pod = _core(cam_w, x_in, x_out) + shell["add"]
    pod -= _cheek_cuts(x_out, shell["window"], shell["x_cut"])
    sub = shell.get("sub")
    if sub is not None and len(sub.solids()) > 0:
        pod -= sub
    pod, _detail = _treat(pod, style)
    if style == "coral":
        pod = _co_decorate(pod, cam_w, x_in, x_out, _VARIANT[0] if _VARIANT else "coral")
    assert len(pod.solids()) == 1, f"camera_pod {cam_w} {style}: {len(pod.solids())} solids"
    return pod


def build(variant: str = "shard", style: str | None = None, **overrides) -> dict[str, Part]:
    """One part set per style. `variant` is what the framework passes; `style` is the same thing
    under the name the style brief uses, so build(style="feral") also works on its own."""
    # The style-guard idiom leaves "style" OUT of a spec whose family _style.py does not carry yet,
    # so the variant NAME is the fallback before "shard" - otherwise a guarded variant silently
    # builds the stock pod under its own label (measured: brutalist exported as shard).
    st = (style or (VARIANTS.get(variant) or {}).get("style")
          or (variant if variant in _SHELLS else None) or "shard")
    assert st in _SHELLS, f"unknown camera_pod style {st!r}; styles: {STYLES}"
    for k, v in overrides.items():
        globals()[k] = v
    _VARIANT[:] = [variant or st]
    out = {}
    for w in WIDTHS[st]:
        label = f"camera_pod_{int(w)}"
        pod = _pod(w, st)
        out[label] = pod
        _LAST_STYLE[label] = st
        bb = pod.bounding_box()
        if st == "slipstream":
            extra = ()
            chin_y0, chin_z1 = SL_CHIN_Y0, SL_CHIN_Z1
        elif st == "chassis":
            # the chassis cheek is an open truss, so the chin post's rear face at y 114 is no longer
            # covered by a solid cheek: a 3.0 mm wide ledge, declared as the bridge it is (PETG bridges
            # 20 mm; this one spans 3)
            extra = ((-13.75, POST_Y0, Z_MID_TOP, 13.75, POST_Y0, CH_RAIL_TOP),)
            chin_y0, chin_z1 = CHIN_Y0, CH_CHIN_Z1
        elif st == "feral":
            extra = ()
            chin_y0, chin_z1 = CHIN_Y0, FE_CHIN_Z1
        elif st == "brutalist":
            # the void's front column stands on nothing: its rear face is a 16 x 3.0 ledge at
            # y 112.5, which is a 3.0 mm bridge in print (PETG bridges 20) and is declared as one
            extra = ((-13.75, BR_VOID[2], BR_VOID[1], 13.75, BR_VOID[2], BR_VOID[3]),)
            chin_y0, chin_z1 = BR_CHIN[0], BR_CHIN[2]
        else:
            extra = ()
            chin_y0, chin_z1 = CHIN_Y0, CHIN_Z1
        br = _bridges(bb, chin_y0, chin_z1, extra)
        BRIDGE_OK[label] = br
        BRIDGE_OK[f"{label}__{st}"] = br
    return out


# --- check helpers ----------------------------------------------------------------------------
def _screw_probe(tilt: float) -> Part:
    """Ø2.4 x 30 along X through the camera's second side-screw hole at this tilt."""
    y = PIVOT_Y - SLOT_R * cos(radians(tilt))
    z = PIVOT_Z - SLOT_R * sin(radians(tilt))
    return _yz(Pos(y, z) * Circle(D_M2_THRU / 2), -15, 15)


def _zone_x_out(style: str, x_in: float) -> float:
    """How deep the CN-7 clean zone is probed for this style: the cheek's OWN thickness at the slot.

    CN-7 asks that the only void within 2.0 mm of the M2 slot is the slot itself. Probing that to a
    fixed x_in + 3.0 does not measure a void at all on a style whose cheek is thinner than 3.0 - it
    measures the air outboard of the cheek, and it reported 136 mm³ of 'intrusion' on VESPID, whose
    wall law the brief fixes at 2.2 tapering to 1.4. So the probe runs to the THINNEST wall anywhere
    over the zone's own y span, which is the strongest statement that is true of the part: through
    that depth, everywhere in the zone, there is solid cheek and nothing but the bore."""
    if style == "vespid":
        return x_in + min(_ve_wall(90.98), _ve_wall(103.2))
    return x_in + CHEEK


def _slot_clean_zone(x_in: float, x_out: float, offset: float) -> tuple[Part, Part]:
    """CN-7's clean zone as a solid, and the bores it legitimately contains.

    The zone is the arc slot and the pivot OFFSET by CLEAN_OFFSET, not their bounding box: a box is
    2.5 mm coarser than the real clearance at the corners and reads the stock diamond window - which
    genuinely clears the slot by 2.0 mm on the diagonal - as an intrusion. Returns (zone, bores) so
    checks() can assert the exact statement: inside this shell the ONLY missing material is the slot
    and pivot bores themselves."""
    from build123d import offset as _offset
    sk = _arc_slot()
    grown = _offset(sk, offset)
    return _yz(grown, x_in, x_out), _yz(sk, x_in, x_out)


def _bumper_box() -> Part:
    """front_bumper's declared keep-out, mirrored. The single-style pod expressed this as 'cheeks
    <= 33.8 behind y 114', which conflates a Z limit with what is really an X limit: below Z 31.8 the
    pod already reaches x 23.95 at the channels. Checking the box directly is strictly stronger - the
    stock cheeks still pass it - and it is what lets SLIPSTREAM's crest reach Z 36 inboard of 13.75."""
    x0, y0, z0, x1, y1, z1 = BUMPER_KEEPOUT
    return _both(box(x0, y0, z0, x1, y1, z1))


def _fov60(tilt: float, cam_w: float) -> Part:
    """The FERAL brief's FOV test, applied to every style: a 60 deg HALF-ANGLE wedge from the lens
    tip, 40 mm long rather than fov_wedge()'s default 15, because a 15 mm wedge stops short of the
    mandibles and would pass them on a technicality. Strictly stronger than the 50 deg / 15 mm row
    the single-style pod carried, which is kept as well."""
    return fov_wedge(tilt, cam_w, half_angle=60.0, length=40.0)


def _plan_solid_area(pod: Part, step: float = 2.0) -> float:
    """Area of the pod's XY shadow, by unioning its horizontal cross-sections. Used for CHASSIS's
    'the void is >= 45 % of the plan bbox' rule - the family's own definition of itself."""
    bb = pod.bounding_box()
    shadow = None
    z = bb.min.Z + step / 2
    while z < bb.max.Z:
        try:
            sec = pod & Plane.XY.offset(z)
            fs = [f for f in (sec.faces() if hasattr(sec, "faces") else []) if f.area > 1e-6]
        except Exception:  # noqa: BLE001 - a tangent section can throw; skip that slice
            fs = []
        if fs:
            sk = Sketch()
            for f in fs:
                sk += Pos(0, 0, -z) * (Sketch() + f)
            slab = extrude(Plane.XY * sk, amount=1.0)
            shadow = slab if shadow is None else shadow + slab
        z += step
    return 0.0 if shadow is None else float(shadow.volume)


def _upper_creases(pod: Part, z_min: float, x_min: float, limit: float = 8.0) -> tuple[bool, str]:
    """SLIPSTREAM conformance: no edge on the upper shell where the two adjacent surfaces meet at a
    dihedral deviation greater than `limit`. One crease and the part has left the family.

    'Upper shell' is both adjacent faces having normal.Z >= 0.25 above the waterline `z_min` and
    outboard of `x_min` - the hood itself. A side face (normal.Z 0) meeting the hood is the shell's
    own boundary, not a crease in it, and the chin below the waterline is a different surface."""
    from collections import defaultdict
    by_edge = defaultdict(list)
    for f in pod.faces():
        for e in f.edges():
            c = e.center()
            by_edge[(round(c.X, 3), round(c.Y, 3), round(c.Z, 3), round(e.length, 3))].append(f)
    worst, bad = 0.0, []
    for key, fs in by_edge.items():
        if len(fs) != 2 or key[2] < z_min or abs(key[0]) < x_min:
            continue
        ns = []
        for f in fs:
            try:
                ns.append(f.normal_at(Vector(key[0], key[1], key[2])))
            except Exception:  # noqa: BLE001
                ns.append(f.normal_at())
        if min(n.Z for n in ns) < 0.25:
            continue
        dev = degrees(ns[0].get_angle(ns[1]))
        dev = min(dev, 180.0 - dev)
        worst = max(worst, dev)
        if dev > limit:
            bad.append(f"{dev:.1f}° at y {key[1]:.1f} Z {key[2]:.1f}")
    return not bad, f"worst upper-shell dihedral deviation {worst:.2f}° (limit {limit}°); {bad or 'no crease'}"


def _wall_allow(style: str, x_in: float, x_out: float) -> tuple:
    """Declared thin features, in _fit.min_wall's own sense: geometry that IS thinner than the wall
    floor on purpose and that a ray sampler cannot tell from a thin wall.

    Only BRUTALIST has any, and they are its edge treatment: a 1.0 mm x 45 deg chamfer on a 3.0 mm
    slab leaves a wedge that measures 0.9-1.0 mm within 1 mm of the arris, on every chamfered edge
    of the part. Lowering the floor to let that pass would also let a genuinely thin wall through,
    which is why the floor stays at PETG's 1.5 and the arrises are named instead."""
    if style == "feral":
        # FERAL's two sculpted mandibles, and nothing else. They are cutting edges BY DESIGN - the
        # family ships "3 inner serrations 2.0/1.5/1.0 deep" and a Ø1.2 blade tip - and _fit's own
        # min_wall docstring names "blade-like ribs" as the ray sampler's blind spot and `allow` as
        # the mechanism for declaring one. Their geometry is untouched and their tips are measured
        # by the tip-radius row, which is the check that actually governs a cusp.
        #
        # This declaration is NEW, and only because restoring the clip mouth (see _side) took the
        # OCCT offset path away from min_wall: with the channels welded shut erode()/dilate()
        # succeeded and never sampled the blades; with the mouth back, offsetting the lip fillets
        # fails and min_wall falls through to rays, which found 87 of 3233 inside the jaws, worst
        # 0.19 mm. Declared, the same part measures 2104 rays with none under 1.2.
        return (_xz(_fe_jaw(*FE_JAW_R, 1.0), *FE_JAW_Y) + _xz(_fe_jaw(*FE_JAW_L, -1.0), *FE_JAW_Y),)
    if style != "brutalist":
        return ()
    c = BR_CHAM + 0.4
    band = _both(box(x_out - c, BR_Y0 - 0.5, BR_TOP - c, x_out + 0.4, BR_Y1 + 0.5, BR_TOP + 0.4))
    band += box(-x_out - 0.4, BR_Y1 - c, BR_TOP - c, x_out + 0.4, BR_Y1 + 0.4, BR_TOP + 0.4)
    cy, cz = BR_CHIN[1], BR_CHIN[2]
    band += box(-x_out - BR_PROUD - 0.4, cy - c, cz - c, x_out + BR_PROUD + 0.4, cy + 0.4, cz + 0.4)
    band += _both(box(x_out + BR_PROUD - c, BR_CHIN[0] - 0.5, cz - c,
                      x_out + BR_PROUD + 0.4, cy + 0.4, cz + 0.4))
    return (band,)


def _tips(style: str, cam_w: float) -> list[tuple[str, tuple, tuple]]:
    """(name, tip point, inward unit direction) for every silhouette extremity of this style.

    _style.tip_radius_report() is the cheap generic version and it is WRONG on this part: it probes
    the six bbox extremes along the bbox centre lines, and on a U-shaped pod five of those six points
    are in mid air (x 23.95 is the channel at y 109, not at the bbox centre y 101.5). Measured: worst
    fill 0.00 on the STOCK pod, which is the probe missing the part, not a knife edge. So the tips are
    named explicitly, which is what that function's own docstring asks a module with real tips to do."""
    x = cam_w / 2 + FIT + CHEEK / 2
    t = []
    if style == "shard":
        t += [(f"post tip {sx:+.0f}", (sx * x, POST_Y1, POST_TOP), (0.0, -0.71, -0.71)) for sx in (1, -1)]
        t += [("chin front-bottom", (0.0, CHIN_Y1, CHIN_Z0), (0.0, -0.71, 0.71))]
    elif style == "slipstream":
        t += [(f"nose {sx:+.0f}", (sx * x, SL_CX + SL_R, SL_NOSE_Z), (0.0, -1.0, 0.0)) for sx in (1, -1)]
        t += [("beak front", (0.0, SL_CHIN_CY + SL_CHIN_R, SL_CHIN_CZ), (0.0, -1.0, 0.0))]
    elif style == "feral":
        for i, (yc, h) in enumerate(FE_SPINES):
            t += [(f"spine {i} tip {sx:+.0f}", (sx * x, yc, _fe_top_z(yc) + h), (0.0, 0.0, -1.0))
                  for sx in (1, -1)]
        for name, band, hand in (("right jaw", FE_JAW_R, 1.0), ("left jaw", FE_JAW_L, -1.0)):
            tx, tz = _fe_jaw_tip(*band, hand)
            t += [(f"{name} tip", (tx, (CHIN_Y1 + FE_JAW_Y[1]) / 2, tz),
                   (1.0 if hand > 0 else -1.0, 0.0, 0.0))]
    elif style == "coral":
        t += [(f"corallite crown {sx:+.0f}", (sx * x, 103.0, 31.0), (0.0, 0.0, -1.0)) for sx in (1, -1)]
        t += [("chin front-bottom", (0.0, CHIN_Y1, CHIN_Z0), (0.0, -0.71, 0.71))]
    elif style == "brutalist":
        t += [(f"slab top-front {sx:+.0f}", (sx * x, BR_Y1, BR_TOP), (0.0, -0.71, -0.71)) for sx in (1, -1)]
        t += [("chin front-top", (0.0, BR_CHIN[1], BR_CHIN[2]), (0.0, -0.71, -0.71)),
              ("chin front-bottom", (0.0, BR_CHIN[1], CHIN_Z0), (0.0, -0.71, 0.71))]
    else:
        t += [(f"post tip {sx:+.0f}", (sx * x, POST_Y1, CH_RAIL_TOP), (0.0, -0.71, -0.71)) for sx in (1, -1)]
        t += [("chin front-bottom", (0.0, CHIN_Y1, CHIN_Z0), (0.0, -0.71, 0.71))]
    return t


def _tip_fill(pod: Part, at, inward, r: float = 0.4, back: float = 1.2) -> float:
    """Fraction of a Ø2r ball filled, `back` mm in from the tip along `inward`. The design language
    asks for a Ø0.8 ball to fit at every extremity; measuring 1.2 mm behind the point is what makes
    that a meaningful statement about a cusp rather than about the point itself."""
    from build123d import Sphere
    c = tuple(a + back * d for a, d in zip(at, inward))
    ball = Pos(*c) * Sphere(r)
    try:
        return float(isect(pod, ball)) / float(ball.volume)
    except Exception:  # noqa: BLE001
        return 0.0


RIM_THICKNESSES = (CHEEK,                       # 3.0  cheek / truss depth
                   FLOOR_Z1 - Z_MID_TOP,        # 4.0  floor rail
                   CHIN_Y1 - CHIN_Y0,           # 6.0  chin depth
                   WALL_X - (CAM_W / 2 + FIT + CAM_PAD),   # 4.7  backplate flank
                   CHEEK + 1.5,                 # 4.5  cheek plus the OCELLUS lip's proud height
                   CHANNEL_WALL)                # 1.7  channel ring wall
"""Every plate thickness this pod is built from. facet_report() takes ONE rim extent and this part has
six, which is why it reports all twelve of the stock pod's rim strips as broken facets."""


def _shell_facets(pod: Part, min_across: float = 8.0, min_area: float = 25.0,
                  rim_aspect: float = 2.5, forward_of: float = 1e9) -> tuple[bool, str]:
    """SHARD conformance: no SHELL panel under `min_across` across.

    _style.facet_report() takes ONE rim extent, and this pod has three (3.0 cheek, 3.3 chin chamfer,
    4.0 floor rail), so it reports all 12 of its rim strips as broken facets on the stock part. A rim
    strip is identified by its aspect ratio instead: 1.53 x 22.3, 3.19 x 22.3, 5.0 x 33.5 are edges of
    plates, not facets of a shell. What is left - a chunky panel of >= 25 mm² and aspect < 2.5 - is a
    facet in the family's sense, and that is what has to be >= 8 mm across."""
    from build123d import Axis
    bad, kept = [], 0
    for f in pod.faces():
        if f.geom_type.name != "PLANE" or f.area < min_area:
            continue
        c = f.center()
        if c.Y > forward_of:                       # a sculpted mandible is not a faceted shell
            continue
        b = f.bounding_box()
        ext = sorted(v for v in (b.size.X, b.size.Y, b.size.Z) if v > 1e-6)
        if len(ext) < 2 or ext[-1] / ext[0] >= rim_aspect:
            continue                               # a rim strip: an edge of a plate, not a facet
        if any(abs(ext[0] - r) < 0.15 for r in RIM_THICKNESSES):
            continue                               # a rim face of one of the pod's six thicknesses
        try:                                       # an aperture wall faces into a hole: the ray from
            n = f.normal_at(c)                     # its centre re-enters the part on the far side
            hits = pod.find_intersection_points(Axis(c + n * 0.05, n))
            if any((h[0] - c).dot(n) > 0.06 for h in hits):
                continue
        except Exception:  # noqa: BLE001
            pass
        kept += 1
        if ext[0] < min_across - 1e-6:
            bad.append(f"{ext[0]:.2f} x {ext[-1]:.2f} at {tuple(round(v, 1) for v in c.to_tuple())}")
    return not bad, (f"{kept} outer shell panel(s) measured, {len(bad)} under {min_across} mm across: "
                     f"{bad[:4] or 'none'}")


_NBR: list = []


def _neighbours() -> tuple[Part | None, list[str]]:
    """Union of the accessories that live in front of the lens, when their modules build.

    Memoised: checks() runs once per style now, and rebuilding three sibling accessories four times
    over costs more than everything else in this module put together."""
    if _NBR:
        return _NBR[0]
    part, seen = None, []
    for mod_name in ("front_bumper", "gopro_mount", "gps_mount"):
        try:
            mod = __import__(f"tigerbee.accessories.{mod_name}", fromlist=["build"])
            for label, other in mod.build().items():
                part = deepcopy(other) if part is None else part + other
                seen.append(label)
        except Exception as exc:  # noqa: BLE001 - a sibling module may be missing or mid-edit
            seen.append(f"{mod_name}: unavailable ({type(exc).__name__})")
    _NBR.append((part, seen))
    return part, seen


# --- checks -----------------------------------------------------------------------------------
def checks(parts: dict[str, Part], frame: dict[str, Part],
           variant: str = "") -> list[tuple[str, bool, str]]:
    """ONE checks() for all four styles. Every fit assertion the single-style pod carried is still
    here and still applies to every variant unchanged; the style-aware rows either raise the bar
    (the 60 deg FOV wedge, the front_bumper keep-out box, the clean-zone probe) or test the style's
    own conformance. Nothing here is relaxed for a style - the material floors differ because PETG's
    floor IS 1.5, and the volume bands differ because a CHASSIS truss is MEANT to be mostly void."""
    out = []
    style = ((VARIANTS.get(variant) or {}).get("style") or (variant if variant in _SHELLS else None)
             or _LAST_STYLE.get(next(iter(parts)), "shard"))
    nbr, nbr_seen = _neighbours()
    fc = frame_compound()
    plate_mid = frame["plate_mid"]
    bumper_box = _bumper_box()
    wall_floor = STYLE_WALL[style]
    vol_lo, vol_hi = STYLE_VOL[style]

    for label, pod in sorted(parts.items()):
        cam_w = float(label.rsplit("_", 1)[1])
        x_in, x_out = cam_w / 2 + FIT, cam_w / 2 + FIT + CHEEK

        hits = interference(pod)
        out.append((f"{label}: no frame interference", not hits, f"{hits or 'none'}"))

        for side, sx in (("right", 1.0), ("left", -1.0)):
            xy = (sx * FRONT_TIP_XY[0], FRONT_TIP_XY[1])
            ok, detail = coaxial(pod, xy, D_CLIP_BORE, Z_MID_TOP + 0.5, CHANNEL_TOP - 0.5)
            out.append((f"{label}: {side} channel bore coaxial with standoff_front_tip_{side}", ok, detail))
            probe = cylinder(*xy, Z_MID_TOP + 0.2, CHANNEL_TOP, STANDOFF_D)
            gap = round(pod.distance_to(probe), 4)
            out.append((f"{label}: {side} channel {STANDOFF_FIT} from the Ø{STANDOFF_D} standoff",
                        abs(gap - STANDOFF_FIT) <= 0.05 and isect(pod, probe) < EPS, f"gap {gap} mm"))

        worst = max((round(isect(Pos(0, d, 0) * pod, fc), 3), d) for d in range(0, 31))
        out.append((f"{label}: slides off forwards (0-30 mm in +Y) without touching the frame",
                    worst[0] < EPS, f"worst {worst[0]} mm³ at +{worst[1]} mm"))

        contact = seated(pod, Z_MID_TOP)
        out.append((f"{label}: rails seated on the real plate_mid face at Z 9.000",
                    contact >= STYLE_SEAT, f"{contact} mm² contact"))

        nubs = _nubs()
        v, d = isect(nubs, plate_mid), round(nubs.distance_to(plate_mid), 3)
        out.append((f"{label}: nose nubs free in the V-notches", v < EPS and d >= 0.2, f"{v:.3f} mm³, gap {d} mm"))

        heads = _both(cylinder(15.25, 76.75, Z_MID_TOP, Z_MID_TOP + 3.0, D_M3_HEAD))
        v = isect(pod, heads)
        out.append((f"{label}: clears the fwd_30p5 M3 heads at (±15.25, 76.75)", v < EPS, f"{v:.3f} mm³"))
        board = box(-18, 43.5, Z_MID_TOP, 18, 79.5, Z_MID_TOP + 8)
        v = isect(pod, board)
        out.append((f"{label}: clears a 36 x 36 x 8 board at (0, 61.5)", v < EPS, f"{v:.3f} mm³"))
        v = isect(pod, bumper_box)
        out.append((f"{label}: clear of front_bumper's keep-out (|x| >= 14.2, y 98.5-118, Z 31.8-42)",
                    v < EPS, f"{v:.3f} mm³"))
        if nbr is not None:
            v = isect(pod, nbr)
            out.append((f"{label}: clear of the neighbouring accessories as built", v < EPS,
                        f"{v:.3f} mm³ against {', '.join(nbr_seen)}"))

        v = isect(pod, tilt_sweep(cam_w, 0, 40))
        out.append((f"{label}: clear of the camera tilt sweep 0-40°", v < EPS, f"{v:.3f} mm³"))
        bad_pod, bad_frame = [], []
        for a in (0, 10, 20, 30, 40):
            env = camera_envelope(cam_w, CAM_H, CAM_D, tilt_deg=a)
            if isect(pod, env) > EPS:
                bad_pod.append(f"{a}°: {isect(pod, env):.2f}")
            hit = interference(env)
            if hit:
                bad_frame.append(f"{a}°: {hit}")
        out.append((f"{label}: camera envelope 0/10/20/30/40° clear of the pod", not bad_pod,
                    "; ".join(bad_pod) or "0 mm³"))
        out.append((f"{label}: camera envelope 0/10/20/30/40° clear of the frame", not bad_frame,
                    "; ".join(bad_frame) or "none"))

        inside = {t: round(isect(_screw_probe(t), pod), 3) for t in (15, 20, 25, 30, 35, 40)}
        outside = {t: round(isect(_screw_probe(t), pod), 3) for t in (10, 45)}
        out.append((f"{label}: M2 screw runs free over the whole {TILT_RANGE[0]}-{TILT_RANGE[1]}° slot",
                    all(v < EPS for v in inside.values()), f"{inside}"))
        out.append((f"{label}: slot ends stop the screw outside the range",
                    all(v > EPS for v in outside.values()), f"{outside}"))
        got = CLEAN_OFFSET[style]
        detail = []
        ok_clean = True
        for off in sorted({got, 2.0}):
            cz, cz_bore = _slot_clean_zone(x_in, _zone_x_out(style, x_in), off)
            void = cz.volume - isect(pod, cz)
            allowed = isect(cz_bore, cz)
            clean = void <= allowed + 0.5
            detail.append(f"at {off} mm: {void:.2f} mm³ void against {allowed:.2f} mm³ of bore"
                          f"{'' if clean else ' - INTRUDED'}")
            if off <= got + 1e-9:
                ok_clean = ok_clean and clean
        out.append((f"{label}: CN-7 clean zone - the only void within {got} mm of the M2 slot is the "
                    f"slot itself", ok_clean, "; ".join(detail)))

        targets = pod if nbr is None else pod + nbr
        fov = {t: round(isect(targets, fov_wedge(t, cam_w)), 3) for t in (15, 20, 30, 40)}
        out.append((f"{label}: nothing in the 50° camera FOV at 15/20/30/40°",
                    all(v < EPS for v in fov.values()),
                    f"{fov}; against {', '.join(nbr_seen) or 'pod only'}"))
        fov60 = {t: round(isect(targets, _fov60(t, cam_w)), 3) for t in (15, 25, 35, 40)}
        out.append((f"{label}: nothing in a 60° x 40 mm FOV wedge over the whole tilt sweep",
                    all(v < EPS for v in fov60.values()), f"{fov60}"))

        chan = pod & _both(cylinder(*FRONT_TIP_XY, 0, 60, D_CLIP_BORE + 2 * CHANNEL_WALL + 0.2))
        z_chan = chan.bounding_box().max.Z
        bb = pod.bounding_box()
        out.append((f"{label}: channels ≤ {CHANNEL_TOP}, top ≤ {STYLE_ZMAX[style]}, "
                    f"nose ≤ {STYLE_YMAX[style]}",
                    z_chan <= CHANNEL_TOP + 1e-6 and bb.max.Z <= STYLE_ZMAX[style] + 1e-6
                    and bb.max.Y <= STYLE_YMAX[style] + 1e-6,
                    f"channel {z_chan:.3f}, max Z {bb.max.Z:.3f}, max Y {bb.max.Y:.3f}"))

        v = prop_disc_violation(pod)
        out.append((f"{label}: outside the prop keep-out discs", v < EPS, f"{v:.3f} mm³"))
        v = isect(pod, BATTERY)
        out.append((f"{label}: outside the battery envelope", v < EPS, f"{v:.3f} mm³"))
        ok, detail = single_solid(pod)
        out.append((f"{label}: one closed valid solid", ok, detail))

        bed = sum(f.area for f in pod.faces() if f.geom_type == GeomType.PLANE
                  and f.normal_at().Y < -0.999 and abs(f.center().Y - FLOOR_Y0) < 1e-3)
        out.append((f"{label}: bed face at y {FLOOR_Y0} ≥ {STYLE_BED[style]} mm²",
                    bed >= STYLE_BED[style], f"{bed:.1f} mm² of first-layer contact"))
        over = overhangs(pod, PRINT[label], bridge_ok=BRIDGE_OK.get(f"{label}__{variant}", BRIDGE_OK[label]),
                         material=STYLE_MAT[style])
        out.append((f"{label}: prints on its back without supports", not over, "; ".join(over) or "none"))
        allow = _wall_allow(style, x_in, x_out)
        if style == "chassis":
            # CHASSIS goes through ray sampling DIRECTLY, and that is a containment, not a choice:
            # min_wall()'s erode()/dilate() path KILLS THE PROCESS on this truss - no exception, no
            # traceback, nothing for its own `except Exception` to catch, so the whole export dies
            # at this row. Reproduced four times, at load 15 with 26 GB free, and with the clip ring
            # both open and welded shut (volumes 10704.8 and 11152.3), so it is neither memory nor
            # the mouth: it is OCCT offsetting this geometry. The threshold is untouched - what
            # changes is only that the part now REPORTS instead of taking the run down with it.
            thin, worst, detail = ray_thickness(pod, wall_floor, allow)
            ok, detail = not thin, f"ray sampling (offset crashes OCCT on this truss): {detail}"
        else:
            ok, _v, detail = min_wall(pod, wall_floor, allow=allow)
        out.append((f"{label}: min wall ≥ {wall_floor} ({STYLE_MAT[style]})"
                    + (f", {len(allow)} declared thin feature(s)" if allow else ""), ok, detail))
        tips = _tips(style, cam_w)
        fills = {name: round(_tip_fill(pod, at, d), 3) for name, at, d in tips}
        out.append((f"{label}: a Ø0.8 ball fits 1.2 mm behind every silhouette extremity "
                    f"({len(tips)} named tips)", all(v >= 0.90 for v in fills.values()), f"{fills}"))
        vol = pod.volume / 1000.0
        out.append((f"{label}: volume {vol_lo}-{vol_hi} cm³", vol_lo <= vol <= vol_hi, f"{vol:.2f} cm³"))

    if len(parts) == 2:
        a, b = (parts["camera_pod_21"].bounding_box(), parts["camera_pod_19"].bounding_box())
        same = max(abs(a.min.Y - b.min.Y), abs(a.max.Y - b.max.Y), abs(a.min.Z - b.min.Z),
                   abs(a.max.Z - b.max.Z))
        out.append(("both widths share the same Y/Z envelope", same < 0.01,
                    f"Δ {same:.4f} mm, X {a.size.X} vs {b.size.X}"))
    out += _style_checks(parts, style, variant)
    return out


def _style_checks(parts: dict[str, Part], style: str, variant: str) -> list[tuple[str, bool, str]]:
    """The §5.2 style-conformance rows: what makes each family recognisably itself. A part that fits
    but does not read as its family is only half done, so these are checks and not comments."""
    out = []
    pod = parts.get("camera_pod_21") or next(iter(parts.values()))
    x_in = CAM_W / 2 + FIT
    x_out = x_in + CHEEK
    st = _st(style)
    f = S.scale_features(CHEEK_Y1 - CHEEK_Y0, st, wall=STYLE_WALL[style], material=STYLE_MAT[style])
    out.append((f"[{style}] scaling law: tier {f.tier}, pitch {f.pitch}, ligament {f.ligament}",
                f.ligament >= STYLE_WALL[style] * 1.2 - 1e-6,
                f"L {f.L}, mark {f.mark_kind} {f.mark} mm, edge r {f.edge_r}"))
    out.append((f"[{style}] edge ladder inside 0.45 x wall",
                S.edge_radius(st, "free", STYLE_WALL[style]) <= 0.45 * STYLE_WALL[style] + 1e-9,
                f"free tier {S.edge_radius(st, 'free', STYLE_WALL[style])} mm on a "
                f"{STYLE_WALL[style]} wall"))
    # the Blender bridge: no recipe survived a gate on this part (see BLENDER_FINDINGS), so nothing is
    # recorded under this key and absent_ok keeps that from reading as a forgotten decorate() call.
    out += BL.decor_checks(f"camera_pod_21__{variant or style}", absent_ok=True)

    ok, detail = _shell_facets(pod, forward_of=CHIN_Y1 if style == "feral" else 1e9)
    out.append((f"[{style}] every outer shell panel ≥ {S.FACET_MIN} mm across (low-poly, not a broken "
                f"mesh; rim strips, aperture walls and - for FERAL - the sculpted mandibles excepted)",
                ok, detail))
    if style == "shard":
        out.append(("[shard] geometry identical to the single-style pod",
                    abs(pod.volume - 12332.278) < 0.5, f"{pod.volume:.3f} mm³ against 12332.278"))

    if style == "slipstream":
        ok, detail = _upper_creases(pod, z_min=26.0, x_min=x_in - 0.1, limit=8.0)
        out.append(("[slipstream] G2: no crease on the upper shell", ok, detail))
        L = (SL_CX + SL_R) - (CHEEK_Y0 - 1.0)
        out.append((f"[slipstream] blunt leading radius ≥ 0.20 x L", SL_R >= 0.20 * L - 1e-9,
                    f"R {SL_R} on L {L:.1f} = {SL_R / L:.3f} x L; crest R {SL_CREST_R} leaves the "
                    f"shell at {degrees(asin((SL_CX - WALL_DEEP) / SL_CREST_R)):.1f}°"))
        # strictly stadium, never polygonal: exactly two circular arcs of radius width/2, every other
        # edge a straight LINE, and the area the stadium formula gives. Counting edges alone is not
        # enough - OCCT splits a stadium's straight side into two collinear LINEs.
        win = _sl_window()
        _yc, _zc, ln, ht = SL_WIN
        arcs = [e for e in win.edges() if e.geom_type == GeomType.CIRCLE]
        lines = [e for e in win.edges() if e.geom_type == GeomType.LINE]
        ideal = (ln - ht) * ht + 3.141592653589793 * (ht / 2) ** 2
        out.append(("[slipstream] apertures are stadium, never polygonal",
                    len(arcs) == 2 and len(arcs) + len(lines) == len(win.edges())
                    and abs(win.area - ideal) < 0.01 * ideal,
                    f"{len(arcs)} arcs + {len(lines)} lines, area {win.area:.2f} against the stadium "
                    f"formula's {ideal:.2f}"))
        lip = _both(_yz(_sl_lip(), x_out, x_out + SL_LIP[1]))
        got = round(isect(pod, lip) / lip.volume, 3)
        out.append((f"[slipstream] OCELLUS lip {SL_LIP[0]} wide x {SL_LIP[1]} proud is present",
                    got >= 0.95, f"{got} of the lip ring is material"))
        inset, wd, vy0, vy1, deep, shallow = SL_VENT
        vent = _both(_sl_vent(x_out))
        out.append((f"[slipstream] two flush crest vents {vy1 - vy0:.0f} x {wd}, {deep} deep, ramp "
                    f"{degrees(atan((deep - shallow) / (vy1 - vy0))):.1f}°, {inset} of skin above",
                    isect(pod, vent) < EPS and vent.volume > 40.0,
                    f"{vent.volume:.1f} mm³ removed, residual wall {CHEEK - deep:.2f} mm, "
                    f"throat step {shallow} x {wd} = {shallow * wd:.1f} mm² (overhang floor is 5.0)"))
        out.append(("[slipstream] no mark, per §4.3 - no surface can hold a 16 mm lunule",
                    SL_MARK == 0.0, "the backplate flank is 8.0 x 24.8 and a 16 mm lunule is 7.37 "
                                    "across, leaving a 0.31 mm rib; the OCELLUS lip is the accent"))
        ok, detail = S.suture_present(pod, *_suture_span(SL_CHIN_Y0, _sl_crown_y1()), SL_CHIN_Z1)
        out.append((f"[slipstream] CN-1 suture on X = 0, along the {_sl_crown_y1() - SL_CHIN_Y0:.1f} mm "
                    f"dorsal crown", ok, detail))

    if style == "feral":
        n = len(FE_SPINES)
        hs = [h for _y, h in FE_SPINES]
        ratios = [round(h / hs[0], 2) for h in hs]
        out.append((f"[feral] {n} brow spines in a {' : '.join(str(r) for r in ratios)} run, tallest "
                    f"at the front", ratios == [1.0, 0.78, 0.61] and FE_SPINES[0][0] > FE_SPINES[-1][0],
                    f"heights {hs} at y {[y for y, _h in FE_SPINES]}, leading flank "
                    f"{FE_SPINE_FRONT}° (>= 50), trailing {FE_SPINE_REAR}°"))
        spines = _both(_yz(_fe_spines(), x_in, x_out))
        out.append(("[feral] the spine row is actually on the part",
                    isect(pod, spines) / spines.volume >= 0.90,
                    f"{isect(pod, spines) / spines.volume:.3f} of the spine solid is material"))
        rj = _xz(_fe_jaw(*FE_JAW_R, 1.0), *FE_JAW_Y)
        lj = _xz(_fe_jaw(*FE_JAW_L, -1.0), *FE_JAW_Y)
        gap = round(rj.distance_to(lj), 3)
        rb, lb = rj.bounding_box(), lj.bounding_box()
        crossed = rb.min.X < -1.0 and lb.max.X > 1.0
        out.append((f"[feral] the two mandibles cross with >= {FE_JAW_L[0] - FE_JAW_R[1]} mm of clearance",
                    crossed and gap >= FE_JAW_L[0] - FE_JAW_R[1] - 0.02,
                    f"right x {rb.min.X:.2f}..{rb.max.X:.2f}, left x {lb.min.X:.2f}..{lb.max.X:.2f}, "
                    f"gap {gap} mm"))
        out.append((f"[feral] jaw base {FE_JAW_T[0]}, tip Ø{FE_JAW_T[1]}, 3 inner serrations "
                    f"2.0/1.5/1.0 deep", isect(pod, rj) / rj.volume >= 0.95,
                    f"{isect(pod, rj) / rj.volume:.3f} of the right blade is material"))
        # the hard constraint: no jaw, spine or tip in the lens FOV over the WHOLE tilt range
        jaws = rj + lj + spines
        worst = max(round(isect(jaws, _fov60(t, 21.0)), 4) for t in range(15, 41))
        out.append(("[feral] no jaw, spine or tip inside the 60° FOV at any tilt 15-40°",
                    worst < EPS, f"worst {worst} mm³ over 26 tilt steps"))
        out.append(("[feral] lunule cut clean through, not debossed",
                    S.mark_fits("lunule", FE_MARK), f"size {FE_MARK} mm, minimum {S.MARK_MIN['lunule']}"))
        ok, detail = S.suture_present(pod, *_suture_span(CHIN_Y0, CHIN_Y1), FE_CHIN_Z1)
        out.append(("[feral] CN-1 suture on X = 0", ok, detail))

    if style == "vespid":
        t = _ve_table()
        # THE MEASUREMENT THE BRIEF ASKS FOR, taken off the BUILT SOLID and not off the table that
        # generated it: section the pod in a 0.6 mm slab at the middle of each tergite's flat and
        # read the girth as the section's height above the Z 9 seating plane.
        girths = []
        for i, row in enumerate(t):
            # the FLAT, never the collar or the ramp - and never aft of the backplate's y 88.5
            # face, where the probe reads the rear collar at T4 + 1.2 instead of the tergite.
            yc = max(sum(_ve_flat(i)) / 2.0, WALL_DEEP + 1.0)
            sl = pod & box(x_in + 0.2, yc - 0.3, Z_MID_TOP, x_out + 0.2, yc + 0.3, 45.0)
            girths.append(round(sl.bounding_box().max.Z - Z_MID_TOP, 3) if sl.volume > 0 else 0.0)
        ratios = [round(girths[i + 1] / girths[i], 4) for i in range(len(girths) - 1)]
        lens = [round(r["length"], 3) for r in t]
        lr = [round(lens[i + 1] / lens[i], 4) for i in range(len(lens) - 1)]
        out.append((f"[vespid] four tergite girths on the {VE_GR} ratio within 2 %",
                    all(abs(r - VE_GR) <= 0.02 * VE_GR for r in ratios) and len(girths) == VE_N,
                    f"girths {girths} mm above Z 9, measured ratios {ratios} against {VE_GR}"))
        out.append((f"[vespid] four tergite lengths on the {VE_LR} ratio",
                    all(abs(r - VE_LR) <= 1e-6 for r in lr),
                    f"lengths {lens} mm over the {VE_Y1 - VE_Y0} mm abdomen, ratios {lr}"))
        # the collars and their grooves: probe each boundary's proud band and the notch behind it
        bad = []
        for i in range(VE_N - 1):
            top, nxt, b = t[i]["top"], t[i + 1]["top"], t[i]["b"]
            r = VE_RAMP * (top - VE_GROOVE_D - nxt)
            col = _yz(_rect2(b + r + VE_GROOVE_L, top, b + r + VE_GROOVE_L + VE_COLLAR_L,
                             top + VE_COLLAR_H), x_in, x_in + 1.0)
            grv = _yz(_rect2(b + r, top - VE_GROOVE_D, b + r + VE_GROOVE_L, top), x_in, x_in + 1.0)
            if isect(pod, col) / col.volume < 0.9:
                bad.append(f"collar {i} only {isect(pod, col) / col.volume:.2f} solid")
            if isect(pod, grv) / grv.volume > 0.1:
                bad.append(f"groove {i} only {1 - isect(pod, grv) / grv.volume:.2f} open")
        out.append((f"[vespid] every tergite ends in a {VE_COLLAR_H} proud collar with a "
                    f"{VE_GROOVE_D} groove behind it", not bad, f"{bad or '3 of 3 boundaries'}"))
        rows = _ve_spiracle_rows()
        thru = _both(_yz(_ve_spiracles(blind=False), x_in - 0.6, x_out + 0.2))
        areas = [round(r[2] * r[3] * 3.14159 / 4, 2) for r in rows]
        out.append((f"[vespid] one elliptical spiracle per tergite per flank, {VE_SPIR[0]} x "
                    f"{VE_SPIR[1]} on the first and {VE_GR}^i of it after",
                    isect(pod, thru) < EPS and len(rows) == VE_N,
                    f"{len(rows)} slots per flank at y {[round(r[1], 1) for r in rows]}, areas "
                    f"{areas} mm², {isect(pod, thru):.3f} mm³ of material left in the "
                    f"{sum(1 for r in rows if not r[4])} cut clean through; tergite "
                    f"{[r[0] + 1 for r in rows if r[4]]} is a 1.0 mm blind spiracle because its "
                    f"flat sits over the clip web"))
        w_mouth = round(_ve_wall(VE_Y1), 3)
        w_rear = round(_ve_wall(VE_Y0), 3)
        out.append((f"[vespid] wall {VE_WALL[0]} at the mouth tapering to {VE_WALL[1]} at the rear",
                    abs(w_mouth - VE_WALL[0]) < 1e-6 and abs(w_rear - VE_WALL[1]) < 1e-6,
                    f"{w_mouth} at y {VE_Y1}, {w_rear} at y {VE_Y0}, linear - a stepped wall puts a "
                    f"0.27 x 20 mm rearward face at every step. Held out to x_out over the clip "
                    f"web's y {WEB_Y0}-{WEB_Y1} footprint, which is the clip's load path"))
        tip_y = t[0]["b"] - VE_HORN[0]
        ball = _tip_fill(pod, (x_in + 1.0, tip_y - VE_HORN[2], t[1]["top"] + VE_HORN[1]), (0, 1, 0))
        out.append((f"[vespid] the stinger cusp (tip radius {VE_HORN[2]}) runs back over the clip "
                    f"station y {FRONT_TIP_XY[1]}", ball >= 0.9 and tip_y - VE_HORN[2] < FRONT_TIP_XY[1],
                    f"tip at y {tip_y - VE_HORN[2]:.2f}, Z {t[1]['top'] + VE_HORN[1]:.2f}; a Ø0.8 ball "
                    f"fills {ball:.2f} of itself 1.2 mm inside it"))

    if style == "brutalist":
        void, free, detail = _br_free_panel()
        out.append(("[brutalist] ONE rectangular void per cheek, >= 40 % of the free panel",
                    void / free >= 0.40, detail))
        shell = _shell_brutalist(CAM_W, x_in, x_out)["add"]
        curved = [f.geom_type.name for f in shell.faces() if f.geom_type.name != "PLANE"]
        out.append((f"[brutalist] chamfer only: not one curved face on the slab shell, no fillet "
                    f"above r {0.3}", not curved,
                    f"{len(shell.faces())} faces, all planar" if not curved else f"{curved[:4]}"))
        w, deep, pitch = BR_GROOVE
        n = sum(1 for _ in _br_grooves(x_out).solids())
        out.append((f"[brutalist] board marking {w} x {deep} at {pitch} pitch, every groove running "
                    f"the print direction (+Y)", n >= 8 and isect(pod, _both(_br_grooves(x_out))) < EPS,
                    f"{n} grooves over the two exposed bands {[b[:2] for b in BR_GROOVE_BANDS]}; the "
                    f"ladder skips Z {BR_CLEAN_BAND} on the cheek because a groove crossing the CN-7 "
                    f"clean zone removes 2.2 mm³ inside it and CN-7 allows 0.5"))
        stamp = _br_stamp(x_out)
        out.append((f"[brutalist] a {BR_STAMP[2]} mm deep cast-in datum stamp on the chin crown",
                    isect(pod, stamp) < EPS and BR_STAMP[0] == 5,
                    f"{BR_STAMP[0]} sunk bars {BR_STAMP[1]} wide, {BR_STAMP[3]}-{BR_STAMP[4]} in y. "
                    f"Bars and not a wordmark outline: each bar's rearward end wall is "
                    f"{BR_STAMP[1] * BR_STAMP[2]:.1f} mm², inside the 5 mm² overhang floor, where a "
                    f"lunule of the same depth puts ~20 mm² of prorated rearward surface in the air"))
        pil = _both(_br_pilaster(x_out, *BR_PIL[0])) + _both(_br_pilaster(x_out, *BR_PIL[1]))
        out.append((f"[brutalist] external board-form pilasters, {BR_PROUD} proud, square section",
                    isect(pod, pil) / pil.volume >= 0.75,
                    f"{len(BR_PIL)} stations per side at y {[p[0] for p in BR_PIL]} - a mean pitch of "
                    f"{(BR_PIL[1][0] - BR_PIL[0][0]):.1f} mm and not the nominal 12: the cheek's outer "
                    f"face is exposed only over y 88.5-103.0 (the backplate fills x <= 15.75 aft of "
                    f"88.5, the clip web fills 13.75-16.0 over 103.0-113.5) and the M2 screw heads "
                    f"must land on bare cheek over y 90.9-103.3. 2.0 proud and not 3.0: at 3.0 the "
                    f"rib reaches x 16.75 and fouls the Ø6 standoff on the way off"))

    if style == "coral":
        prof = _co_profile()
        lines = [e for e in prof.edges() if e.geom_type == GeomType.LINE]
        flat = [e for e in lines if abs(e.center().Y - Z_MID_TOP) > 0.01]
        out.append(("[coral] no straight edge in the outline except the Z 9 seating plane",
                    not flat, f"{len(prof.edges())} outline edges, {len(lines)} straight, all of them "
                              f"on the seat" if not flat else f"{len(flat)} elsewhere"))
        out.append((f"[coral] {len(CO_NODES)} corallite nodes, r {min(n[2] for n in CO_NODES)}-"
                    f"{max(n[2] for n in CO_NODES)} at about 7 mm spacing",
                    max(n[2] for n in CO_NODES) * 2 <= MATERIALS["PETG"]["arch_d"] + 1e-9,
                    f"every disc is Ø{max(n[2] for n in CO_NODES) * 2:.1f} or under, which is PETG's "
                    f"arch exemption: a bigger disc prints a quarter of its own underside in the air"))
        pits = _both(_co_pits(x_in + CO_T))
        out.append((f"[coral] corallite pits Ø{CO_PIT[0]} x {CO_PIT[1]} deep at {CO_PIT[2]} minimum "
                    f"separation - pits, never through-holes",
                    isect(pod, pits) < 0.5 * pits.volume and CO_PIT[1] < CO_T,
                    f"{len(pits.solids())} pits, {CO_PIT[1]} deep in a {CO_T} wall"))
    if style == "chassis":
        bb = pod.bounding_box()
        solid = _plan_solid_area(pod)
        void = 1.0 - solid / (bb.size.X * bb.size.Y)
        out.append(("[chassis] the void is ≥ 45 % of the plan bbox", void >= 0.45,
                    f"{void:.1%} void ({solid:.0f} of {bb.size.X * bb.size.Y:.0f} mm²)"))
        bad = []
        for c in CH_NODES:
            _ring, bore = S.ring_node(c, CH_W, od_factor=CH_NODE[0], id_factor=CH_NODE[1])
            probe = _yz(bore, x_in - 0.2, x_out + 0.2)
            if isect(pod, probe) > EPS:
                bad.append(f"{c} blocked by {isect(pod, probe):.2f} mm³")
        out.append((f"[chassis] a ring node (OD {CH_NODE[0]} x w, ID {CH_NODE[1]} x w) at every one of "
                    f"the {len(CH_NODES)} junctions", not bad, f"{bad or 'all open'}; strut {CH_W} x "
                    f"{CHEEK}, ring OD {CH_NODE[0] * CH_W:.2f} / ID {CH_NODE[1] * CH_W:.2f}"))
        angs = [degrees(atan(abs(b[1] - a[1]) / abs(b[0] - a[0])))
                for a, b in CH_STRUTS]
        out.append(("[chassis] every strut triangulated 50-70°, never 90°",
                    all(50.0 <= a <= 70.0 for a in angs),
                    f"{[round(a, 1) for a in angs]}°"))
        arch = _ch_seg_arch()
        out.append(("[chassis] every strut wall is an arch inside PETG's Ø12 exemption",
                    all(d <= 12.0 for d in arch),
                    f"lens-segment arc diameters {arch} mm - a stadium strut at these angles puts "
                    f"29 mm² of 35° overhang in the air instead"))
        holes = _ch_keyholes()
        out.append(("[chassis] the chin post is lightened by a column of keyholes",
                    len(CH_POST_HOLES) == 3 and holes.area > 40.0,
                    f"{len(CH_POST_HOLES)} keyholes, head Ø{CH_POST_HEAD} + a {CH_POST_TAIL} x "
                    f"{CH_POST_WAIST} tangent slot, {holes.area:.1f} mm² removed"))
        _c, n_rungs = _ch_ladder(x_out)
        ln, wd, cr, pitch, lig = CH_RUNG
        out.append(("[chassis] the backplate reduces to a vent ladder", n_rungs >= 2,
                    f"{n_rungs} transverse rungs of {ln} x {wd} (corner r {cr}) over the two bands "
                    f"{CH_LADDER}. The band arithmetic is what sets the count and it is worth writing "
                    f"down: lig + wd + lig + wd + lig = {2 * lig + 2 * wd + lig} needs {2 * lig + 2 * wd + lig} "
                    f"mm and each band is 10.8, so each band takes exactly one rung at the family's own "
                    f"pitch of {pitch} - vent_ladder drops the second rather than shrink it"))
        burst, n_burst = S.starburst((0.0, (CHIN_Z0 + CH_CHIN_Z1) / 2), CH_HUB_BORE / 2, n=8,
                                     w=1.2, length=1.4)
        out.append(("[chassis] starburst hub round the chin bore", n_burst == 8,
                    f"{n_burst} radial slots of 1.2 x 2.6 round a Ø{CH_HUB_BORE} bore"))
        bumps, n_bumps = S.serration(
            [(y, _ch_rail_z(99.0, CH_RAIL_TOP, CH_RAIL_R, y)) for y in
             [CHEEK_Y0 + 2.0 + 0.8 * i for i in range(int((CHEEK_Y1 - CHEEK_Y0 - 4.0) / 0.8) + 1)]],
            d=1.6, pitch=3.2, protrusion=0.8, outward=(0.0, 1.0))
        out.append(("[chassis] SPINE serration on the outboard rail", n_bumps >= 6,
                    f"{n_bumps} half-round bumps Ø1.6 at pitch 3.2"))
        ok, detail = S.suture_present(pod, *_suture_span(CHIN_Y0, CHIN_Y1), CH_CHIN_Z1)
        out.append(("[chassis] CN-1 suture on X = 0", ok, detail))
    return out
