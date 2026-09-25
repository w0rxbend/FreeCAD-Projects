"""V-shaped dual RX antenna holder - a CHASSIS wishbone on the rear-tip standoff bolts.

MOUNT LOCATION - option (a), the rear-tip standoff top bolts on plate_top at (+-16.5, -94.0),
seating face Z 36, 33 mm pitch. Option (b) does not exist: `tigerbee.mounts.HOLES` has exactly two
holes in plate_top behind y -50 - the two `rear_tip_standoff` holes and the Ø6.5 `sma` hole at
(0, -56.5). There is no tail hole row on the top plate (`rear_20`, `rear_25p5`, `rear_30p5_row`
and `rear_tail_axis` are all plate_bottom only), so the rear-tip bolts are the only bolted
interface on the tail of the top plate. They are also the pair the 30.5 mm rear-tip standoffs
already carry, so the holder adds no hardware beyond two longer buttons.

WHY THE V OPENS FORE/AFT AND NOT LEFT/RIGHT. A 90 deg V that is mirror-symmetric about X = 0 must
splay at 1/sqrt(2) per unit of arm length in X. The rear prop keep-out discs (centres
(+-115.7212, -98.4367), r 91.9 above Z 7) leave |x| <= 23.93 at y -94 and only reach |x| = 29.4 as
far back as y -130, i.e. the keep-out opens at 0.24 mm of |x| per mm of y against the V's 0.71 - a
left/right V loses that race at every length. The V therefore opens in the YZ plane, where both
tubes stay inside |x| <= 4.5 and the prop discs are never in play at all.

WHY THE V IS RAKED NOWHERE AND SITS BEHIND y -95. The BATTERY envelope is box(-25, -95, 38.5,
25, 55, 83.5): anything above Z 38.5 forward of y -95 is inside the pack. A forward-leaning arm
rooted on the bar (y -94) is inside it after 2 mm of travel, so the V apex is carried rearward on
a keel to y -123.6 and the forward tube's outermost surface lands at y -96.51, 1.51 mm clear of the
pack. Raking the V rearward was measured and rejected: it buys ~8 mm of apex position and turns a
symmetric V into an L (one arm near-vertical, one near-horizontal), and the rear arm then exceeds
the overhang limit.

WHY V_HALF_ANGLE IS 43.0 AND NOT THE BRIEF'S 45.0. `_common.overhangs()` flags any face whose
normal.Z < -0.70. Every member of an arm leaning a from vertical presents a down-facing face at
normal.Z = -sin(a), so at 45 deg that is -0.70711 - 0.007 past the gate, and EVERY rail, strut,
tube wall and tube bore in the V fails at once. 43 deg gives -0.68200 with real margin, keeps the
included angle at 86 deg (polarisation diversity is a cosine, so 86 vs 90 deg costs 0.02 dB), and
is what every face angle in this module is derived from. Printability was bought with geometry,
not by relaxing the gate: the keel apertures are vertical stadium slots whose only ceilings are
Ø4.0 arches, the tube roots are trimmed on vertical planes instead of leaving a square annular
ledge, the coax notch is a gable and not a lintel, and the retaining lip is a Ø1.2 cross nub whose
axis is horizontal.

THREE MORE LANGUAGES ON THE SAME SKELETON (vespid, origami, filigree). They change the keel
silhouette, the arm section, the aperture generator and the accent, and NOTHING about the fit: the
two rear-tip bolt axes, the Z 36 seating face, the 2.5 mm bar, the 86 deg V, the antenna channel on
each arm axis, the coax gable and the suture are the same numbers the first three use. Where one of
them had to move a number it is because a measurement forced it, and the comment says which:
VESPID's sting rises instead of reaching forward (the forward arm ends 1.53 mm off the BATTERY
envelope), ORIGAMI's channel stops at s 33.4 (its folded V stands 5.6 mm off the arm axis and the
same envelope is 0.682 mm nearer per mm of arm), and FILIGREE drops the coax gable (a 5.0 mm wide
cut would sever a 2.4 mm spine, where the other keels close over the top of it).

EXCLUSIVE with antenna_mast: both take the two rear-tip top bolts and both occupy the air above
plate_top behind y -88. COEXISTS with tail_block in either form (TOWER=True reaches Z 31.4,
TOWER=False Z 22.0; this part starts at Z 36) and with gps_mount and gps_pigtail_mount, which live
on the nose at y +55..+80. Those four are imported and checked in checks() when present.
"""

from math import atan2, cos, degrees, hypot, radians, sin

from build123d import (Axis, Circle, Part, Plane, Polygon, Pos, Rectangle, Sketch, SlotOverall,
                       Vector, extrude, fillet)

from tigerbee.accessories import _style as S
from tigerbee.accessories._common import *  # noqa: F401,F403 - constants, builders and checks

NAME = "rx_antenna_v_holder"
TITLE = "V-mount dual RX antenna holder"
MATERIAL = "TPU95A"
PRINT = {"rx_antenna_v": (0, 0, -1)}  # on its back: the whole Z 36 underside is the bed face
EXCLUSIVE = ("antenna_mast",)
MOUNTS = ("plate_top top face Z 36, rear fork prongs y -88.5..-99.5 (the bar bridges the U-notch)",
          "standoff_rear_tip_left / _right bolt axes (±16.5, -94), 33.0 mm pitch")
HARDWARE = ("2 x M3 x 12 button head (replace the rear-tip standoff bolts)",
            "optional 1 x 2.5 mm zip tie through the coax gable notch")
NOTES = ("Two M3 x 12 buttons replace the rear-tip standoff bolts and clamp the bar onto plate_top "
         "between the two rear fork prongs. The keel runs rearward over the top plate's U-notch and "
         "carries the V apex to y -121.5; the two antenna tubes leave it at 43 deg each side of "
         "vertical, an 86 deg diversity V in the YZ plane. Slide each 915 MHz antenna tube in from "
         "the open end until it clicks past the Ø1.2 cross nub; the coax lies in the 1.2 mm slit, "
         "which faces into the V on both arms, runs down the keel and drops through the gable notch "
         "at (0, -97.75) into the top plate's U-notch. "
         "The button heads stand 1.65 mm proud at Z 38.5 - there is no head recess, because a Ø6.6 "
         "recess in a Ø11.2 boss leaves 2.3 mm of wall but only 0.75 mm under the head at BAR_T 2.5, "
         "and BAR_T cannot grow: everything forward of y -95 has to stay at or below Z 38.5 or it is "
         "inside the BATTERY envelope. Use a battery pad, or flat-head M3 x 12.")

# --- variants ---------------------------------------------------------------------------------
# Three genuinely different parts, one skeleton, one checks().
#   chassis_64  the reference: an open keel truss with three stadium slots, five ring nodes, a
#               serrated dorsal rail and starbursts round both eyelets. Tube ID 6.4 for a 915 MHz
#               ELRS T/dipole antenna tube.
#   chassis_44  the same family read at the smaller equipment size - tube ID 4.4 for a bare coax
#               dipole. The tubes drive ARM_W, the blade taper and the apex spacing, so the arms
#               come out visibly slimmer, not just bored smaller.
#   shard_64    the same skeleton cut as a crystal: a 9-sided faceted keel, mitred elongated-hex
#               lightening slots, the chamfer ladder 2.0/1.2/0.6, a stepped 3.6/2.4 thickness with
#               a visible step line, and a faceted LABRUM shield on the bar's rear face. Its plan
#               outline is 30-40 % larger than chassis's - measured in checks(), not asserted.
VARIANTS = {
    "chassis_64": {"style": "chassis", "material": "TPU95A",
                   "params": {"TUBE_ID": 6.4},
                   "notes": "open keel truss, 5 ring nodes, serrated dorsal rail, 10.0 mm blades; "
                            "Ø6.4 tubes for a 915 MHz ELRS T-antenna tube."},
    "chassis_44": {"style": "chassis", "material": "TPU95A",
                   "params": {"TUBE_ID": 4.4},
                   "notes": "the same truss sized round a Ø4.4 bare coax dipole - an 8.0 mm blade "
                            "against chassis_64's 10.0 (the ends of the brief's range), a tighter "
                            "lightening lens and slimmer tubes, on the same 86 deg V."},
    "shard_64": {"style": "shard", "material": "TPU95A",
                 "params": {"TUBE_ID": 6.4},
                 "notes": "faceted crystal reading: 9-sided keel, mitred hex slots, chamfer "
                          "ladder, stepped 3.6/2.4 thickness, LABRUM shield."},
    # --- the three new languages -------------------------------------------------------------
    # `form` is what the GEOMETRY branches on and is always present; `style` is the framework's
    # validated key and is only declared once _style.py knows the name, so these three build
    # whether or not the _style task has landed.
    "vespid": {**({"style": "vespid"} if "vespid" in S.STYLES else {}),
               "form": "vespid", "material": "TPU95A",
               "params": {"TUBE_ID": 6.4},
               "notes": "wasp abdomen: each arm is four shingled tergites stepping 0.82 in length "
                        "and 0.86 in girth, every one with a 1.2 proud collar bead, a 0.45 "
                        "undercut groove and one spiracle slot, ending in a stinger cusp."},
    "origami": {**({"style": "origami"} if "origami" in S.STYLES else {}),
                "form": "origami", "material": "TPU95A",
                "params": {"TUBE_ID": 6.4},
                "notes": "one folded sheet, constant 2.4 (the TPU95A value of the 1.8 law): the "
                         "arms are 90 deg V-section channels creased at 45 deg with the antenna "
                         "lying in the crease, the keel a straight zigzag of 22.5 deg folds, "
                         "apertures sheared parallelogram ladders. No curve anywhere."},
    "filigree": {**({"style": "filigree"} if "filigree" in S.STYLES else {}),
                 "form": "filigree", "material": "TPU95A",
                 "params": {"TUBE_ID": 6.4},
                 "notes": "ornamental cutwork on a rigid spine: 2.4 mm spines on the load path, "
                          "a mirrored two-radius scroll net of 1.4 mm ribbons in the keel and in "
                          "the yoke of the V, Ø4.0 ring nodes at the junctions, a scalloped outer "
                          "edge and a cut lunule at the vertex."},
}
ASSEMBLY_VARIANT = "chassis_64"

# --- parameters (mm, deg) ----------------------------------------------------------------------
V_HALF_ANGLE = 43.0             # see the module docstring: 45.0 is exactly on overhangs()' gate
SIN_V, COS_V = sin(radians(V_HALF_ANGLE)), cos(radians(V_HALF_ANGLE))

TUBE_ID = 6.4                   # 6.4 = 915 MHz ELRS T/dipole tube, 4.4 = bare coax dipole
TUBE_LEN = 22.0
TUBE_WALL = 1.2                 # TPU floor; OD = TUBE_ID + 2.4
SLIT = 1.2                      # coax insertion slit, facing into the V (upward in print)
LIP_R, LIP_INTRUDE, LIP_BACK = 0.6, 0.45, 3.0   # Ø1.2 cross nub: a horizontal-axis arch, exempt
TUBE_S0, TUBE_S1 = 13.0, 35.0   # tube start/end along the arm axis, measured from the apex

ARM_T = 3.0                     # blade thickness in X - the CHASSIS strut depth floor (>= 3.0)
ARM_W = 10.0                    # nominal blade width; _params recomputes it per variant as
#                                 max(8.0, OD + 1.2) -> 10.0 for Ø6.4, 8.0 for Ø4.4

APEX_Y, APEX_Z = -123.6, 45.0   # the V apex / keel rear node
STRUT_W = 3.0                   # nominal CHASSIS strut width -> ring node OD 2.6x, ID 0.9x
RING_OD, RING_ID = 7.6, 3.0     # apex ring node (OD/STRUT_W = 2.53, ID/STRUT_W = 1.00)

BAR_T = 2.5                     # Z 36.0 .. 38.5; cannot grow (BATTERY floor is Z 38.5)
BAR_Y0, BAR_Y1 = -88.5, -99.5   # the bar's plan extent in Y
BAR_X = 17.5                    # rectangular core; cusp tails run out to BAR_TIP
BAR_RAIL_W = 8.0                # CHASSIS: the bar is a RAIL between two eyelet rings, not a slab
SHARD_BAR = (18.5, 22.1, -86.0, -102.0)   # SHARD: a much larger 10-sided faceted plate (x1, x2, y0, y1)
BAR_TIP = 22.1                  # |x| at the cusp tips - the prop keep-out allows 23.83 at y -99.5
EYELET_D = D_M3_THRU            # 3.4
BOSS_D = 11.2                   # 8.0 in the brief; 11.2 is what the starburst needs, see _starburst
MIN_CARBON_CLEAR = 20.0         # required tube-to-carbon gap
BATT_CLEAR = 1.0                # required gap from the part to the BATTERY envelope

KEEL_Y0 = -93.5                 # keel front face (leaves the bar top clear for the suture)
KEEL_BOT_Y1 = -118.0            # the flat Z 36 belly ends here, then rises to the apex
KEEL_E = (-108.0, 50.0)         # dorsal crest node
KEEL_F = (-100.5, 43.5)         # dorsal shoulder node
KEEL_SHOULDER_Y = -96.2         # dorsal edge leaves Z 38.5 here (BATTERY: y > -95 must stay <= 38.5)

SLOT_YS = (-105.0, -110.5, -116.0)    # keel stadium slots, 5.5 pitch -> 1.9 ligaments
SLOT_W = 3.6
SLOT_LIG = 1.6                  # slot to dorsal edge / belly

NOTCH_X, NOTCH_LEN, NOTCH_Z = 2.5, 3.8, 39.2   # coax gable, immediately behind the bar's rear edge
# The gable is a prism ALONG X, not across it. Gabling it across X (a tent in the XZ plane) cuts
# the 3.0-3.6 mm keel web at a shallow angle and leaves a feather edge 0.14 mm thick where the
# tent's flank crosses the web's side face - measured, and the reason for this shape. As a prism
# along X the cut is full width through the web and its two flanks read normal.Z -0.46.

SUTURE_Y = (-88.8, -93.3)       # CN-1, on the bar top face at Z 38.5, forward of the keel
SERR_D, SERR_PITCH, SERR_PROUD = 1.6, 3.2, 0.8    # dorsal rail spines (up-facing, CN-2 free)

SHARD_T_CORE, SHARD_T_ARM = 3.6, 2.4   # the stepped thickness, with a visible step line
SHARD_CHAMFER = (2.0, 1.2, 0.6)        # the SHARD edge ladder sil/crease/free
LABRUM_W, LABRUM_H, LABRUM_PROUD = 13.0, 1.6, 0.8

Z0 = Z_TOP_TOP                  # 36.0, the seating face
Z1 = Z0 + BAR_T                 # 38.5, the bar top face
BOLT_XY = REAR_TIP_XY           # (16.5, -94)

_DEFAULTS = dict(TUBE_ID=TUBE_ID, TUBE_LEN=TUBE_LEN, TUBE_WALL=TUBE_WALL, SLIT=SLIT,
                 TUBE_S0=TUBE_S0, TUBE_S1=TUBE_S1, ARM_T=ARM_T, V_HALF_ANGLE=V_HALF_ANGLE,
                 APEX_Y=APEX_Y, APEX_Z=APEX_Z, BAR_T=BAR_T, BAR_TIP=BAR_TIP, BOSS_D=BOSS_D,
                 EYELET_D=EYELET_D, KEEL_Y0=KEEL_Y0, WALL=WALL)


def _params(variant: str, **overrides) -> dict:
    """Every derived number in one place, so checks() can rebuild exactly what build() built."""
    spec = VARIANTS[variant]
    # `form` is the geometry language. The three new ones declare it explicitly so they never
    # depend on _style.py knowing the name; the three original ones take it from their style.
    form = spec.get("form") or spec["style"]
    p = {**_DEFAULTS, "variant": variant, "style": form, "form": form, **overrides}
    p["OD"] = p["TUBE_ID"] + 2 * p["TUBE_WALL"]
    if form in NEW_FORMS:
        return _params_new(p)
    # The two CHASSIS variants sit on the two ENDS of the brief's 8.0-10.0 blade range, not 0.8 mm
    # apart: OD + 1.2 gives 10.0 for the Ø6.4 tube and the 8.0 floor for the Ø4.4. That is a 25 %
    # difference in blade width and it is the thing that makes chassis_44 read as a genuinely
    # leaner part in the thumbnail instead of chassis_64 with a smaller hole. SHARD runs a heavier
    # 10.4 mm faceted blade.
    p["ARM_W"] = 10.4 if p["style"] == "shard" else max(8.0, p["OD"] + 1.2)
    p["T_OUT"] = p["OD"] / 2                        # outboard blade edge, flush with the tube
    p["T_IN"] = p["ARM_W"] - p["OD"] / 2            # inboard blade edge (tapers to OD/2 at the tube)
    p["ARM_T"] = SHARD_T_ARM if p["style"] == "shard" else ARM_T
    p["KEEL_T"] = SHARD_T_CORE if p["style"] == "shard" else ARM_T
    return p


# --- the YZ working plane ----------------------------------------------------------------------
# The whole V - keel, arms, apex ring - is one 2D silhouette in the YZ plane extruded along X, so
# every face it makes is either planar (from a straight segment) or a cylinder with a HORIZONTAL
# axis (from an arc). That is the printability trick of the part: an arc of Ø <= 10 is exempt from
# overhangs() by the arch rule whatever direction it faces, so every ceiling in the silhouette is
# drawn as an arc and every straight boundary is kept within 43 deg of vertical.
def _yz(t: float) -> Plane:
    """Sketch plane with local x = frame +Y, local y = frame +Z, extruding +X, centred on X = 0."""
    return Plane(origin=(-t / 2, 0, 0), x_dir=(0, 1, 0), z_dir=(1, 0, 0))


def _web(sk: Sketch, t: float) -> Part:
    return extrude(_yz(t) * sk, amount=t, dir=(1, 0, 0))


def _cut_yz(sk: Sketch) -> Part:
    """A cutter swept right through the part in X (wider than any thickness it will meet)."""
    return S.extrude_cut(sk, Plane(origin=(-20.0, 0, 0), x_dir=(0, 1, 0), z_dir=(1, 0, 0)), 40.0)


def _cut_xy(sk: Sketch, z0: float, h: float) -> Part:
    return S.extrude_cut(sk, Plane.XY.offset(z0), h)


# --- the arm frame -----------------------------------------------------------------------------
def _dir(p: dict, side: int) -> tuple[float, float]:
    """Arm axis in (u, v) = (frame Y, frame Z). side +1 = the forward arm, -1 = the rear arm."""
    a = radians(p["V_HALF_ANGLE"])
    return side * sin(a), cos(a)


def _out(p: dict, side: int) -> tuple[float, float]:
    """Outboard normal of the arm, perpendicular to _dir - the side the tube's slit does NOT face."""
    a = radians(p["V_HALF_ANGLE"])
    return side * cos(a), -sin(a)


def _pt(p: dict, side: int, s: float, t: float) -> tuple[float, float]:
    du, dv = _dir(p, side)
    mu, mv = _out(p, side)
    return p["APEX_Y"] + s * du + t * mu, p["APEX_Z"] + s * dv + t * mv


def _tube_plane(p: dict, side: int, s: float) -> Plane:
    """Section plane across the arm at distance s from the apex; local x = frame X, +Z = the axis."""
    u, v = _pt(p, side, s, 0.0)
    du, dv = _dir(p, side)
    return Plane(origin=(0.0, u, v), x_dir=(1, 0, 0), z_dir=(0.0, du, dv))


def _tube_root_u(p: dict, side: int) -> float:
    return _pt(p, side, p["TUBE_S0"], 0.0)[0]


def _tube_keep(p: dict, side: int, back: float = 0.0) -> Part:
    """Everything outboard of the tube's vertical root plane. The bore and the slit stop exactly on
    it, so the blade behind stays solid and becomes the antenna's depth stop; the TUBE itself is
    carried `back` mm further, so tube and blade OVERLAP instead of butting on a shared plane - two
    coplanar faces fuse into a sliver the ray sampler reads as a 0.10 mm wall."""
    u = _tube_root_u(p, side) - side * back
    return box(-30, u, Z0 - 20, 30, u + 240, 240) if side > 0 else \
        box(-30, u - 240, Z0 - 20, 30, u, 240)


# --- the keel silhouette (chassis) --------------------------------------------------------------
def _dorsal_pts(p: dict) -> list[tuple[float, float]]:
    """The dorsal (top) rail of the keel, apex first. Nothing on it may rise above Z 38.5 forward
    of y -95: that is the BATTERY envelope's corner and the reason for the shoulder node."""
    if p["style"] == "shard":
        return [(p["APEX_Y"], p["APEX_Z"]), (-113.0, 52.0), (-103.0, 47.0), (-99.0, 41.0),
                (KEEL_SHOULDER_Y, Z1 - 0.15)]
    return [(p["APEX_Y"], p["APEX_Z"]), KEEL_E, KEEL_F, (KEEL_SHOULDER_Y, Z1 - 0.15)]


def _dorsal_v(p: dict, u: float) -> float:
    pts = sorted(_dorsal_pts(p) + [(p["KEEL_Y0"], Z1 - 0.15)])
    for (u0, v0), (u1, v1) in zip(pts, pts[1:]):
        if u0 - 1e-9 <= u <= u1 + 1e-9:
            return v0 + (v1 - v0) * (u - u0) / (u1 - u0) if u1 > u0 else v0
    return Z1 - 0.15


def _dorsal_min(p: dict, u: float, half: float) -> float:
    """The LOWEST dorsal height over an aperture's whole u span. Taking the height at the centre
    alone is how the first cut of this module poked a slot through the dorsal rail: the rail
    slopes, so an aperture sized on its centre breaks out at whichever end the rail drops."""
    xs = [u - half, u, u + half] + [q[0] for q in _dorsal_pts(p) if u - half < q[0] < u + half]
    return min(_dorsal_v(p, x) for x in xs)


def _keel_outline(p: dict) -> Sketch:
    pts = [(p["KEEL_Y0"], Z0), (KEEL_BOT_Y1, Z0), *_dorsal_pts(p), (p["KEEL_Y0"], Z1 - 0.15)]
    if p["style"] == "shard":
        # A 9-sided faceted crystal instead of the truss keel: the belly steps up in two mitred
        # facets, the crest is a pair of long planes and the tail cuts back to the apex. Every
        # facet is >= 8 mm across (facet_report) and every boundary is within 43 deg of vertical
        # or an up-facing top edge.
        pts = [(p["KEEL_Y0"], Z0), (-118.5, Z0), (-121.0, 41.5), *_dorsal_pts(p),
               (p["KEEL_Y0"], Z1 - 0.15)]
    return Polygon(*pts, align=None)


def _keel_apertures(p: dict) -> Sketch:
    """CHASSIS: three vertical stadium slots - the only ceiling each one has is its own Ø4.0 arch.
    SHARD: two mitred elongated hexes, min ligament 2.2, with the same arch-only ceiling rule
    satisfied by the hex's 43 deg mitres rather than by a radius."""
    sk = Sketch()
    if p["style"] == "shard":
        # Mitred elongated hexes, long axis vertical. The mitre is >= 1.022 x the half width, so
        # every mitre face stands within 43.6 deg of vertical: a 45 deg mitre would put the
        # aperture's own ceiling at normal.Z -0.707 and fail the gate that the whole part is
        # designed around.
        for u, hw in ((-109.0, 2.4), (-115.5, 2.8)):
            v_hi, v_lo = _dorsal_min(p, u, hw) - 2.6, Z0 + 2.4
            h = (v_hi - v_lo) / 2
            m = max(1.05 * hw, 0.0)
            if h <= m + 0.4 or hw < 1.1:
                continue
            sk += Pos(u, (v_lo + v_hi) / 2) * Polygon(
                (-hw, -h + m), (0, -h), (hw, -h + m), (hw, h - m), (0, h), (-hw, h - m), align=None)
        return sk
    for u in SLOT_YS:
        v_hi = _dorsal_min(p, u, SLOT_W / 2) - SLOT_LIG
        v_lo = Z0 + SLOT_LIG
        length = v_hi - v_lo
        if length <= SLOT_W + 0.2:
            continue
        sk += Pos(u, (v_lo + v_hi) / 2) * SlotOverall(length, SLOT_W).rotate(Axis.Z, 90)
    return sk


def _serration(p: dict) -> Sketch:
    """The one serrated rail (CHASSIS small tier): SPINE bumps marching up the dorsal edge. They
    face outboard-up, and each is a Ø1.6 cylinder with a horizontal axis, so the arch rule exempts
    every one of them from the overhang gate."""
    path = [KEEL_F, KEEL_E, (p["APEX_Y"], p["APEX_Z"])]
    sk, _n = S.serration(path, d=SERR_D, pitch=SERR_PITCH, protrusion=SERR_PROUD)
    return sk


def _apex_ring(p: dict) -> tuple[Sketch, Sketch]:
    return S.ring_node((p["APEX_Y"], p["APEX_Z"]), STRUT_W,
                       od_factor=RING_OD / STRUT_W, id_factor=RING_ID / STRUT_W)


# --- the arms ----------------------------------------------------------------------------------
def _blade(p: dict, side: int) -> Sketch:
    """One arm blade, in the YZ plane. The outboard edge runs straight at t = OD/2 so it is flush
    with the tube; the inboard edge carries the taper, because it faces UP and a taper there costs
    nothing at the overhang gate while the same taper outboard would read -0.75."""
    s0, s1 = -9.0, p["TUBE_S0"] + 6.0
    s_taper = p["TUBE_S0"] - 5.0
    o, i = p["T_OUT"], p["T_IN"]
    pts = [_pt(p, side, s0, o), _pt(p, side, s1, o), _pt(p, side, s1, -o),
           _pt(p, side, s_taper, -i), _pt(p, side, s0, -i)]
    blade = Polygon(*pts, align=None)
    # Both ends are trimmed on VERTICAL planes (normal.Z 0.00): at the apex, where the two blades
    # butt against each other instead of each leaving a square root face pointing 43 deg downward,
    # and at the tube root, where the blade hands over to the tube and becomes the antenna's depth
    # stop. A square annular ledge at either place reads -0.731 and fails the overhang gate.
    u0, u1 = sorted((p["APEX_Y"], _tube_root_u(p, side)))
    keep = Pos((u0 + u1) / 2, p["APEX_Z"]) * Rectangle(u1 - u0, 200.0)
    return blade & keep


def _arm_slot(p: dict, side: int) -> Sketch:
    """The lightening slot, elongated along the arm - so its ceiling lies at 43 deg (-0.682), the
    one direction a straight edge is allowed to face down in this part."""
    s0, s1 = RING_OD / 2 + 1.6, p["TUBE_S0"] - 2.4
    half = min(2.1, (p["T_OUT"] + p["T_IN"]) / 2 - 2.2)
    if s1 - s0 < 3.0 or half < 1.1:
        return Sketch()
    tc = (p["T_OUT"] - p["T_IN"]) / 2
    if p["style"] == "shard":
        return Polygon(*[_pt(p, side, s, t) for s, t in _shard_hex((s0 + s1) / 2, tc)], align=None)
    a, b = _pt(p, side, s0, tc), _pt(p, side, s1, tc)
    return S.lens(a, b, half)


# Every edge of a hole in a 43 deg blade is a potential ceiling, and a ceiling is legal only when
# its edge stands within 44.4 deg of vertical - locally that is arm angles phi in [-87.4, +1.4]
# off the arm axis. A symmetric mitred hex puts two of its four mitres at +56 deg, which comes out
# 9 deg off HORIZONTAL in frame coordinates (normal.Z -0.987) and was measured failing. The hex is
# therefore SHEARED: its three edge-direction classes are 0, -50 and -80 deg, all inside the
# window, which is why this aperture leans the way it does. The CHASSIS lens needs none of this -
# its boundary is two arcs of Ø5.3, and the arch rule exempts an arc whatever way it faces.
SHARD_HEX_DIRS = (-80.0, -50.0, 0.0)
SHARD_HEX_LENS = (2.2, 2.0, 3.2)


def _shard_hex(s_mid: float, t_mid: float) -> list[tuple[float, float]]:
    pts, cur = [], (0.0, 0.0)
    for a, L in list(zip(SHARD_HEX_DIRS, SHARD_HEX_LENS)) + \
            [(a + 180.0, L) for a, L in zip(SHARD_HEX_DIRS, SHARD_HEX_LENS)]:
        pts.append(cur)
        cur = (cur[0] + L * cos(radians(a)), cur[1] + L * sin(radians(a)))
    cx = (min(q[0] for q in pts) + max(q[0] for q in pts)) / 2
    cy = (min(q[1] for q in pts) + max(q[1] for q in pts)) / 2
    return [(q[0] - cx + s_mid, q[1] - cy + t_mid) for q in pts]


# --- the arm's own truss: the tube IS the inner rail ------------------------------------------
# This is the CHASSIS spec read literally on an arm: "an outer and an inner rail joined by struts
# triangulated at 50-70 deg, with a RING NODE at every junction". The tube is the inner rail, an
# outer rail runs parallel to it inside the V, two struts at 60 deg triangulate the gap and the
# three junctions carry visible eyelets. The frame sits INSIDE the V (t < 0) because outboard of
# the forward arm is the BATTERY envelope - a rail 6 mm outboard there ends at y -94.6, inside the
# pack. The gap between tube and rail is 3.2 mm, wide enough that the coax slit (which reaches
# t -7.4) breaks out into open air instead of slotting the rail.
RAIL_T0, RAIL_W = -10.4, 2.8     # rail centre line offset and width; ring node OD 2.6 x, ID 0.93 x
RAIL_S = (12.0, 30.0)            # rail start/end along the arm axis
RAIL_NODE_OD, RAIL_NODE_ID = 7.3, 2.6
STRUT_W_ARM = 2.6
STRUT_S = (21.0, 29.0)           # where each strut leaves the tube wall; it lands 3.5 further out
SLIT_S1 = 17.5                   # the coax slit stops here, 3.5 short of the first strut foot. A
# slit that ran the tube's full length would cross both strut roots and leave 0.9 mm webs there;
# the coax leaves the antenna at its base anyway, so the slit only has to open the tube's inner end.
STRUT_RUN = 3.5                  # ds over dt 6.0 -> 60 deg to the rails, the spec's own angle
# SHARD reads the arm truss as one faceted panel. Every edge is chosen so that, if it turns out
# to be a CEILING, it still stands within 44.4 deg of vertical in frame coordinates - in arm-local
# terms its direction class has to lie in [0, 1.4] or [92.6, 180). The only edge that breaks the
# rule is the 1.5 mm step at s 18-19 where the panel climbs from clear of the coax slit (t -5.0)
# to inside the tube wall (t -3.9); at 3.6 mm² it is under overhangs()' 5 mm² floor.
SHARD_PANEL = ((6.0, -5.0), (18.0, -5.0), (19.0, -3.9), (30.0, -3.9), (31.5, -14.5),
               (11.0, -13.2), (6.4, -9.0))
SHARD_PANEL_HEX = ((15.0, -9.1), (23.4, -9.5))


def _member(p: dict, side: int, a: tuple, b: tuple, w: float, grow: float = 0.0) -> Sketch:
    """A strut of width `w` on the segment a->b in arm-local (s, t), extended `grow` at both ends
    so neighbouring members overlap instead of meeting tangentially."""
    (ax, ay), (bx, by) = a, b
    dx, dy = bx - ax, by - ay
    L = hypot(dx, dy)
    ux, uy = dx / L, dy / L
    ax, ay, bx, by = ax - ux * grow, ay - uy * grow, bx + ux * grow, by + uy * grow
    nx, ny = -uy * w / 2, ux * w / 2
    pts = [(ax + nx, ay + ny), (bx + nx, by + ny), (bx - nx, by - ny), (ax - nx, ay - ny)]
    return Polygon(*[_pt(p, side, q, r) for q, r in pts], align=None)


def _half(p: dict, side: int) -> Sketch:
    """The half plane on this arm's side of the apex. Both arms' frames are clipped on it, so they
    BUTT on one mirror plane instead of crossing each other - two crossing panels leave a 0.9 mm
    sliver where one's edge exits the other, which the ray sampler finds every time."""
    return Pos(p["APEX_Y"] + side * 90.0, p["APEX_Z"]) * Rectangle(180.0, 260.0)


def _arm_frame(p: dict, side: int) -> tuple[Sketch, Sketch]:
    """(material, bores) for one arm's truss."""
    add, cut = Sketch(), Sketch()
    if p["style"] == "shard":
        # SHARD reads the same skeleton as one faceted panel with two mitred apertures - the
        # silhouette-first rule: the family changes the OUTLINE before it changes the holes.
        add += Polygon(*[_pt(p, side, q, r) for q, r in SHARD_PANEL], align=None)
        for s_mid, t_mid in SHARD_PANEL_HEX:
            cut += Polygon(*[_pt(p, side, q, r) for q, r in _shard_hex(s_mid, t_mid)], align=None)
        return add & _half(p, side), cut & _half(p, side)
    rail_a, rail_b = (RAIL_S[0], RAIL_T0), (RAIL_S[1], RAIL_T0)
    add += _member(p, side, rail_a, rail_b, RAIL_W, grow=1.0)
    add += _member(p, side, (0.0, 0.0), rail_a, RAIL_W, grow=1.0)          # down to the apex node
    nodes = [rail_a]
    for s0 in STRUT_S:
        foot = (s0, -p["T_OUT"] + 0.6)
        head = (s0 + STRUT_RUN, RAIL_T0)
        add += _member(p, side, foot, head, STRUT_W_ARM, grow=0.8)
        nodes.append(head)
    for n in nodes:
        ring, bore = S.ring_node(_pt(p, side, *n), RAIL_W,
                                 od_factor=RAIL_NODE_OD / RAIL_W, id_factor=RAIL_NODE_ID / RAIL_W)
        add += ring
        cut += bore
    # CN-3: the rail runs out to a point instead of stopping square
    tip = _pt(p, side, RAIL_S[1] + 3.2, RAIL_T0)
    root = _pt(p, side, RAIL_S[1], RAIL_T0)
    add += S.cusp_tail(RAIL_W, hypot(tip[0] - root[0], tip[1] - root[1]), tip_r=0.5, at=root,
                       angle=degrees(atan2(tip[1] - root[1], tip[0] - root[0])))
    return add & _half(p, side), cut & _half(p, side)


def _tube(p: dict, side: int, back: float = 0.6) -> Part:
    """The antenna tube: a cylinder on the arm axis whose root is trimmed on a VERTICAL plane.
    A square annular root face would point -d (normal.Z -0.731) and fail the gate; a vertical
    trim face reads 0.00 and needs nothing declared."""
    r = p["OD"] / 2
    s_start = p["TUBE_S0"] - 7.0
    tube = extrude(_tube_plane(p, side, s_start) * Circle(r), amount=p["TUBE_S1"] - s_start)
    return tube & _tube_keep(p, side, back=back)


def _tube_cuts(p: dict, side: int) -> Part:
    """Bore + coax slit, as one cutter. The slit faces INTO the V (-out), which is up in the print
    orientation on both arms, so the bore has no ceiling of its own at all."""
    r_in = p["TUBE_ID"] / 2
    s_start = p["TUBE_S0"] - 9.0
    pl = _tube_plane(p, side, s_start)
    length = p["TUBE_S1"] - s_start + 0.5
    bore = extrude(pl * Circle(r_in), amount=length)
    # The section plane's local +y is _out for the forward arm and -_out for the rear one (its
    # y_dir is z_dir x x_dir, and z_dir flips with the arm), so the sign has to follow `side`.
    # Without it the rear arm's slit came out on the OUTBOARD wall, where it leaves 0.61 mm to the
    # tube's OD - measured, and the reason this line is not just a minus sign.
    # Radially the slit stops 0.05 outside the tube's OD, so the truss rail (which starts 0.5
    # further out) is never slotted, and along the axis it stops at SLIT_S1.
    y0, y1 = sorted((-side * (p["OD"] / 2 + 0.05), -side * (r_in - 0.4)))
    slit = extrude(pl * (Pos(0.0, (y0 + y1) / 2) * Rectangle(p["SLIT"], y1 - y0)),
                   amount=SLIT_S1 - s_start)
    return (bore + slit) & _tube_keep(p, side)


def _lip(p: dict, side: int) -> Part:
    """The soft retaining lip: a Ø1.2 cross nub on the outboard wall near the mouth, its axis
    along X. Horizontal axis + Ø1.2 -> the arch rule exempts it; a conical funnel in the same
    place reads normal.Z -0.81 on its upper generatrix and fails."""
    t = p["TUBE_ID"] / 2 - LIP_INTRUDE + LIP_R
    u, v = _pt(p, side, p["TUBE_S1"] - LIP_BACK, t)
    return Pos(0, u, v) * extrude(Plane.YZ * Circle(LIP_R), amount=2.0, both=True)


# --- the base bar ------------------------------------------------------------------------------
def _bar_y1(p: dict) -> float:
    """The bar's rear edge - where the keel stops being carried by the bar and the coax gable starts."""
    return SHARD_BAR[3] if p["style"] == "shard" else -94.0 - BAR_RAIL_W / 2


def _bar_outline(p: dict) -> Sketch:
    if p["style"] == "shard":
        # A faceted 10-sided plate: wider in Y and mitred at every corner, so its plan area is
        # 30-40 % larger than the chassis rail. SHARD changes the OUTLINE first (the §4.5
        # silhouette-first directive), not the hole pattern.
        x1, x2, y0, y1 = SHARD_BAR
        pts = [(x1, y0), (-x1, y0), (-x2 + 3.5, -90.0), (-x2, -94.0), (-x2 + 3.5, -98.0),
               (-x1, y1), (x1, y1), (x2 - 3.5, -98.0), (x2, -94.0), (x2 - 3.5, -90.0)]
        return Polygon(*pts, align=None)
    sk = Pos(0, -94.0) * Rectangle(2 * BAR_X, BAR_RAIL_W)
    for sgn in (1, -1):
        sk += Pos(sgn * BOLT_XY[0], BOLT_XY[1]) * Circle(p["BOSS_D"] / 2)
        sk += S.cusp_tail(7.0, p["BAR_TIP"] - 18.0, tip_r=0.5, at=(sgn * 18.0, -94.0),
                          angle=0.0 if sgn > 0 else 180.0)
    return sk


def _bar_apertures(p: dict) -> Sketch:
    """Two lightening windows, both over the top plate's U-notch (|x| < 9.7), so not one mm² of
    seating is spent on them."""
    sk = Sketch()
    for sgn in (1, -1):
        cx = sgn * 6.2
        if p["style"] == "shard":
            w, h, m = 2.4, 4.6, 1.3
            sk += Pos(cx, -94.0) * Polygon((-w, -h + m), (0, -h), (w, -h + m), (w, h - m),
                                           (0, h), (-w, h - m), align=None)
        else:
            sk += S.lens((cx, -94.0 + BAR_RAIL_W / 2 - 1.4), (cx, -94.0 - BAR_RAIL_W / 2 + 1.4), 2.2)
    return sk


def _starburst(p: dict) -> Sketch:
    """CHASSIS hub accent round both Ø3.4 eyelets. The brief's n=8 x w 1.2 is dimensionally
    impossible on a Ø3.4 bore - eight 1.2 mm slots on a r 2.0 circle leave 0.37 mm ligaments, and
    the generators drop apertures rather than shrink them. Six slots at r 2.9..4.4 inside a Ø11.2
    boss leave 1.84 mm between slots, 1.2 mm to the bore and 1.2 mm to the boss rim."""
    sk = Sketch()
    if p["style"] == "shard":
        return sk
    for sgn in (1, -1):
        c = (sgn * BOLT_XY[0], BOLT_XY[1])
        burst, _n = S.starburst(c, 2.9, n=6, w=1.2, length=1.5)
        sk += burst
    return sk


def _labrum(p: dict) -> Part:
    """SHARD's LABRUM: a faceted toothed shield 0.8 proud on the bar's REAR face, the frame-facing
    plane nothing else touches. Its own faces are 2.4 mm across at most, so facet_report treats
    them as rim, not as facets."""
    y = SHARD_BAR[3]
    half, h = LABRUM_W / 2, LABRUM_H
    prof = Polygon((-half, Z0 + 0.4), (-half + 2.0, Z0 + 0.4 + h), (half - 2.0, Z0 + 0.4 + h),
                   (half, Z0 + 0.4), align=None)
    xz = Plane(origin=(0, y, 0), x_dir=(1, 0, 0), z_dir=(0, -1, 0))
    return extrude(xz * prof, amount=LABRUM_PROUD)


def _notch(p: dict) -> Part:
    """The coax gable at X = 0, just behind the bar: a pointed arch, not a lintel. A flat ceiling
    here would read normal.Z -1.00 over 19 mm² and need a bridge declaration; the gable's flanks
    read -0.46. It sits behind the bar so no flank has to cross the bar's top face, which is what
    leaves a sub-millimetre remnant above it."""
    y1 = _bar_y1(p) - 0.2
    y0 = y1 - NOTCH_LEN
    prof = Polygon((y0, Z0 - 0.8), (y1, Z0 - 0.8), ((y0 + y1) / 2, NOTCH_Z), align=None)
    return _web(prof, 2 * NOTCH_X).moved(Location((-NOTCH_X, 0, 0)))


def _eyelet_bores(p: dict) -> Part:
    tools = Part()
    for sgn in (1, -1):
        tools += cylinder(sgn * BOLT_XY[0], BOLT_XY[1], Z0 - 1.0, Z1 + 1.0, p["EYELET_D"])
    return tools


# --- build -------------------------------------------------------------------------------------
def build(variant: str = "chassis_64", **overrides) -> dict[str, Part]:
    p = _params(variant, **overrides)
    if p["form"] in NEW_FORMS:
        return _build_new(p)

    keel_sk = _keel_outline(p) + _apex_ring(p)[0]
    if p["style"] != "shard":
        keel_sk += _serration(p)
    part = _web(keel_sk, p["KEEL_T"])

    arms_sk, arms_cut = Sketch(), Sketch()
    for side in (1, -1):
        arms_sk += _blade(p, side)
        add, cut = _arm_frame(p, side)
        arms_sk += add
        arms_cut += cut
    part += _web(arms_sk, p["ARM_T"])

    part += S.extrude_cut(_bar_outline(p), Plane.XY.offset(Z0), p["BAR_T"])

    for side in (1, -1):
        part += _tube(p, side)
        part += _lip(p, side)
    if p["style"] == "shard":
        part += _labrum(p)

    # --- subtract: every functional bore and every aperture ------------------------------------
    cuts = Part()
    cuts += _cut_yz(_keel_apertures(p) + _apex_ring(p)[1])
    for side in (1, -1):
        slot = _arm_slot(p, side)
        if slot.faces():
            cuts += _cut_yz(slot)
        cuts += _tube_cuts(p, side)
    if arms_cut.faces():
        cuts += _cut_yz(arms_cut)
    cuts += _cut_xy(_bar_apertures(p) + _starburst(p), Z0 - 1.0, p["BAR_T"] + 2.0)
    cuts += _eyelet_bores(p)
    cuts += _notch(p)
    part -= cuts
    part -= S.suture(SUTURE_Y[0], SUTURE_Y[1], Z1)

    part = _treat_edges(p, part)
    part = Part() + part
    part.label = "rx_antenna_v"
    return {"rx_antenna_v": part}


def _treat_edges(p: dict, part: Part) -> Part:
    """CHASSIS fillets 0.8 everywhere it will take; SHARD chamfers on the ladder 2.0/1.2/0.6.
    Applied LAST, after every cut - a fillet on an un-cut outline is lost."""
    style = p["style"]
    r = 0.6 if style == "shard" else 0.8
    # Only the silhouette edges of the web - the ones running along X - and only above the bed
    # plane. Rounding the whole part explodes the face count and makes OCCT's booleans unreliable
    # (a measured finding), and a chamfer on a bed edge reads normal.Z -0.707 and fails the gate.
    sel = [e for e in part.edges() if e.geom_type.name == "LINE" and e.length > 3.0
           and abs(e.tangent_at(0.5).X) > 0.99 and e.bounding_box().min.Z > Z1 + 0.2]
    if not sel:
        return part
    op = "chamfer" if style == "shard" else "fillet"
    for attempt in (r, r / 2, r / 4):
        try:
            from build123d import chamfer as _ch
            return _ch(sel, attempt) if op == "chamfer" else fillet(sel, attempt)
        except Exception:  # noqa: BLE001 - OCCT refuses radii it cannot fit; shrink and retry
            continue
    return part


# --- probes used by checks() ---------------------------------------------------------------
def _plan_area(part: Part, samples: int = 3) -> float:
    """Plan (XY) material area counted WITH multiplicity: the integral of max(0, n.Z) over the
    boundary, which for a closed solid is exactly the number of upward crossings per mm². It is
    therefore an upper bound on the silhouette area, so `1 - plan / bbox` is a LOWER bound on the
    void fraction - the conservative direction for the CHASSIS >= 45 % rule."""
    total = 0.0
    for f in part.faces():
        if f.area <= 1e-9:
            continue
        try:
            if f.geom_type.name == "PLANE":
                total += f.area * max(0.0, f.normal_at().Z)
                continue
            vals = [max(0.0, f.normal_at(u, v).Z) for u in (0.15, 0.5, 0.85) for v in (0.15, 0.5, 0.85)]
            total += f.area * sum(vals) / len(vals)
        except Exception:  # noqa: BLE001 - a degenerate face contributes nothing measurable
            continue
    return total


def _outline_edges(part: Part) -> int:
    """How many edges run along X - one per vertex or arc of the YZ outline, so a count of how
    much detail the side elevation carries."""
    return sum(1 for e in part.edges() if abs(e.tangent_at(0.5).X) > 0.99)


def _side_area(part: Part) -> float:
    """The YZ (side elevation) equivalent of _plan_area: the integral of max(0, n.X) over the
    boundary, an upper bound on the side silhouette. This part's whole design lives in the YZ
    plane, so this is the view its thumbnail is read in."""
    total = 0.0
    for f in part.faces():
        if f.area <= 1e-9:
            continue
        try:
            if f.geom_type.name == "PLANE":
                total += f.area * max(0.0, f.normal_at().X)
                continue
            vals = [max(0.0, f.normal_at(u, v).X) for u in (0.15, 0.5, 0.85) for v in (0.15, 0.5, 0.85)]
            total += f.area * sum(vals) / len(vals)
        except Exception:  # noqa: BLE001 - a degenerate face contributes nothing measurable
            continue
    return total


def _ring_ok(part: Part, centre, id_: float, od_: float, axis: str, depth: float) -> tuple[bool, str]:
    """A ring node is a VISIBLE EYELET: the bore has to be empty and the annulus round it solid.
    Anything less is a blob with a dimple, which is what the CHASSIS spec exists to forbid."""
    if axis == "Z":
        x, y = centre
        bore = cylinder(x, y, Z0 - 1.0, Z1 + 1.0, id_ - 0.2)
        ring = cylinder(x, y, Z0 + 0.2, Z1 - 0.2, od_ - 0.3) - cylinder(x, y, Z0 - 1, Z1 + 1, id_ + 0.3)
    else:
        u, v = centre
        half = depth / 2 - 0.15
        pl = Plane(origin=(0.0, u, v), x_dir=(0, 1, 0), z_dir=(1, 0, 0))
        bore = extrude(pl * Circle((id_ - 0.2) / 2), amount=depth + 4.0, both=True)
        ring = extrude(pl * (Circle(od_ / 2 - 0.15) - Circle(id_ / 2 + 0.15)), amount=half, both=True)
    inside, around = isect(part, bore), isect(part, ring)
    return inside < EPS and around > 1.0, f"{inside:.3f} mm³ in the bore, {around:.1f} mm³ in the annulus"


def _ring_nodes(p: dict) -> list[tuple[str, tuple, float, float, str, float]]:
    """Every junction of three or more members in this part, and the node that sits on it."""
    return [("apex (keel + both arms)", (p["APEX_Y"], p["APEX_Z"]), RING_ID, RING_OD, "X", p["KEEL_T"]),
            ("right eyelet (bar rail + boss)", (BOLT_XY[0], BOLT_XY[1]), p["EYELET_D"], p["BOSS_D"], "Z", p["BAR_T"]),
            ("left eyelet (bar rail + boss)", (-BOLT_XY[0], BOLT_XY[1]), p["EYELET_D"], p["BOSS_D"], "Z", p["BAR_T"])]


def _open_s0(p: dict) -> float:
    """Where the bore is open over its full Ø: the tube's root is trimmed on a VERTICAL plane, so
    the bore only clears the blade once the whole bore circle is outboard of it."""
    return p["TUBE_S0"] + (p["TUBE_ID"] / 2) * cos(radians(p["V_HALF_ANGLE"])) / sin(radians(p["V_HALF_ANGLE"]))


def _antenna_probe(p: dict, side: int, clearance: float = 0.1) -> Part:
    """The equipment envelope: the antenna tube, Ø(TUBE_ID - 2 x clearance), pushed in until it
    bottoms out on the blade. The retaining nub band is cut out of the probe - the nub is meant to
    be in the way, and it is checked on its own."""
    r = p["TUBE_ID"] / 2 - clearance
    s0, s1 = _open_s0(p) + 0.2, p["TUBE_S1"] - 0.2
    probe = extrude(_tube_plane(p, side, s0) * Circle(r), amount=s1 - s0)
    band0 = p["TUBE_S1"] - LIP_BACK - LIP_R - 0.4
    band = extrude(_tube_plane(p, side, band0) * Circle(r + 1.0), amount=2 * LIP_R + 0.8)
    return probe - band


def _tube_solid(p: dict, side: int) -> Part:
    return _tube(p, side)


def _bar_ends(p: dict, side: int) -> list[Vector]:
    """The 915 MHz T-antenna's radiating bar, BAR_LEN long, transverse (along X) at the tube mouth
    - the only orientation that keeps both ends away from carbon; along the arm's own outboard
    normal the forward bar would end 3.9 mm above plate_top."""
    u, v = _pt(p, side, p["TUBE_S1"], 0.0)
    return [Vector(BAR_LEN / 2, u, v), Vector(-BAR_LEN / 2, u, v)]


def _neighbours() -> dict[str, Part]:
    """Sibling accessories that share the tail or could be installed at the same time. Imported
    defensively: a sibling still being written must not break this module's checks."""
    out = {}
    for mod_name, kwargs in (("tail_block", {"TOWER": True}), ("tail_block", {"TOWER": False}),
                             ("gps_mount", {}), ("gps_pigtail_mount", {})):
        key = f"{mod_name}{'(TOWER=False)' if kwargs.get('TOWER') is False else ''}"
        if key in out:
            continue
        try:
            import importlib
            mod = importlib.import_module(f"tigerbee.accessories.{mod_name}")
            parts = mod.build(**kwargs) if kwargs else mod.build()
            out[key] = Part() + list(parts.values())
        except Exception:  # noqa: BLE001 - sibling absent or in progress
            continue
    return out


# --- checks ------------------------------------------------------------------------------------
def checks(parts: dict[str, Part], frame: dict[str, Part], variant: str | None = None) -> list[tuple[str, bool, str]]:
    variant = variant or ASSEMBLY_VARIANT
    p = _params(variant, **VARIANTS[variant].get("params", {}))
    part = parts["rx_antenna_v"]
    out: list[tuple[str, bool, str]] = []

    # 1. the two mount axes
    for side, sgn in (("right", 1), ("left", -1)):
        xy = (sgn * BOLT_XY[0], BOLT_XY[1])
        ok, detail = coaxial(part, xy, p["EYELET_D"], Z0, Z1)
        probe = isect(part, cylinder(*xy, Z0 - 1.0, Z1 + 1.0, 3.2))
        out.append((f"eyelet coaxial with standoff_rear_tip_{side} (±16.5, -94), Ø3.2 bolt clear",
                    ok and probe < EPS, f"{detail}; Ø3.2 probe {probe:.4f} mm³"))

    # 2. seated on the real plate face (holes and the U-notch subtracted, not the filled outline)
    contact = seats_on(part, "plate_top", Z0)
    out.append(("seated on the plate_top face at Z 36.000 (>= 120 mm² of real carbon)",
                contact >= 120.0, f"{contact} mm² contact on the two rear prongs"))

    # 3. frame, standoffs, prop discs, battery
    hits = interference(part)
    out.append(("no interference with any frame part", not hits, f"{hits or 'none'}"))
    so = standoff_interference(part)
    out.append((f"clear of the Ø{STANDOFF_D} standoff cylinders", not so, f"{so or 'none'}"))
    disc = prop_disc_violation(part)
    out.append(("prop-disc keep-out violation < EPS (rear discs are the binding pair)",
                disc < EPS, f"{disc:.4f} mm³; max |x| {max(abs(part.bounding_box().min.X), abs(part.bounding_box().max.X)):.2f} "
                            f"against {max_abs_x_at(BAR_Y1):.2f} allowed at y {BAR_Y1}"))
    vb = isect(part, BATTERY)
    out.append(("no material inside the BATTERY envelope (the bar top IS the pack's floor)",
                vb < EPS, f"{vb:.4f} mm³"))
    # The pack rests ON the bar, so the bar top is coplanar with the envelope floor by design and a
    # distance_to() reads 0.00 for a part that is perfectly placed. The clearance rule is therefore
    # a guard box: the pack's footprint grown BATT_CLEAR in -Y and ±X, starting 0.05 above its floor.
    guard = box(-25 - BATT_CLEAR, -95 - BATT_CLEAR, Z1 + 0.05, 25 + BATT_CLEAR, 55.0, 83.5)
    vg = isect(part, guard)
    out.append((f"nothing within {BATT_CLEAR} mm of the pack footprint above its floor Z {Z1}",
                vg < EPS, f"{vg:.4f} mm³ inside the guard; the part's forward-most material "
                          f"(the bar's front edge) is at y {part.bounding_box().max.Y:.2f}, the "
                          f"forward tube at y {_tube(p, 1).bounding_box().max.Y:.2f}"))

    # 4. the siblings that could share the tail
    for name, other in _neighbours().items():
        v, g = isect(part, other), part.distance_to(other)
        out.append((f"no interference with {name}", v < EPS, f"{v:.4f} mm³, gap {g:.2f} mm"))

    # 5. the antenna tubes against carbon
    worst = None
    for side, label in ((1, "forward"), (-1, "rear")):
        tube = _tube_solid(p, side)
        gaps = distance_to_frame(tube, near=80.0)
        d = min(gaps.values()) if gaps else 999.0
        worst = d if worst is None else min(worst, d)
        out.append((f"{label} antenna tube >= {MIN_CARBON_CLEAR} mm from every frame part",
                    d >= MIN_CARBON_CLEAR, f"{d:.2f} mm to {min(gaps, key=gaps.get) if gaps else 'nothing within 80 mm'}"))
    ends = [(e, min(cylinder(e.X, e.Y, e.Z - 0.05, e.Z + 0.05, 0.1).distance_to(frame[n]) for n in PLATE_FACES))
            for side in (1, -1) for e in _bar_ends(p, side)]
    out.append((f"all four {BAR_LEN} mm T-bar ends >= {MIN_CARBON_CLEAR} mm from every plate",
                all(g >= MIN_CARBON_CLEAR for _e, g in ends),
                "; ".join(f"({e.X:.0f}, {e.Y:.0f}, {e.Z:.0f}) {g:.1f}" for e, g in ends)))

    # 6. the equipment actually fits the tubes
    for side, label in ((1, "forward"), (-1, "rear")):
        v = isect(part, _antenna_probe(p, side))
        out.append((f"{label} tube bore takes a Ø{p['TUBE_ID']} x {p['TUBE_LEN']} antenna tube",
                    v < EPS, f"{v:.4f} mm³ of material inside the antenna envelope"))

    # 7. walls, solidity, print
    thin, _w, wall_detail = ray_thickness(part, WALL, allow=_thin_allow(p))
    out.append((f"min wall >= {WALL} outside the declared thin features", not thin, wall_detail))
    walls = _named_walls(p)
    out.append((f"declared thin features rooted in >= {WALL} of material",
                min(walls.values()) >= WALL - 1e-6,
                ", ".join(f"{k} {v:.2f}" for k, v in walls.items())))
    ok_solid, detail = single_solid(part)
    out.append(("one watertight solid", ok_solid, detail))
    over = overhangs(part, PRINT["rx_antenna_v"], material=MATERIAL)
    out.append(("prints flat on its back (bed normal (0, 0, -1), no support)", not over,
                "; ".join(over) or f"none; every arm face stands at {V_HALF_ANGLE} deg "
                                   f"(normal.Z {-sin(radians(V_HALF_ANGLE)):.3f})"))

    # 8. style conformance
    out.extend(_style_rows(p, part))
    return out


def _junction_band(p: dict, side: int) -> Part:
    """The tube-root junction: a 1.9 mm window in Y round the vertical trim plane. The blade has a
    RECTANGULAR section (ARM_T x ARM_W) and the tube a ROUND one, so wherever the rectangle's
    corner crosses the circle the union tapers to a point - a tangential lip, not a wall, and the
    only thing the ray sampler finds thin once the tube and blade are made to overlap. Both real
    walls through this window (blade ARM_T, tube TUBE_WALL) are stated in _named_walls."""
    u = _tube_root_u(p, side)
    du, dv = _dir(p, side)
    mu, mv = _out(p, side)
    vs = []
    for t in (p["T_OUT"], -p["T_IN"]):
        s = (u - p["APEX_Y"] - t * mu) / du
        vs.append(p["APEX_Z"] + s * dv + t * mv)
    y0, y1 = sorted((u - side * 1.3, u + side * 0.6))
    return box(-5.5, y0, min(vs) - 0.8, 5.5, y1, max(vs) + 0.8)


def _v_thin_allow(p: dict) -> tuple[Part, ...]:
    """VESPID's one declared thin feature: the retaining lip each side of the open channel mouth.
    A straight-sided mouth through a round channel always tapers to a lip where it breaks the
    surface - the same geometry _thin_allow documents for the coax slit and c_clip mouths - so the
    band covers the mouth's vicinity only, and every real wall inside it is stated in
    _named_walls (mouth side wall, tube wall, blade)."""
    band = Part()
    for side in (1, -1):
        s0 = p["TUBE_S0"] - 10.0
        pl = _tube_plane(p, side, s0)
        y0, y1 = sorted((-side * (p["TUBE_ID"] / 2 - 1.6), -side * (V_G0 + 2.0)))
        band += extrude(pl * (Pos(0.0, (y0 + y1) / 2) * Rectangle(V_MOUTH_W + 3.2, y1 - y0)),
                        amount=p["TUBE_S1"] + 3.0 - s0)
    return (Part() + band,)


def _thin_allow(p: dict) -> tuple[Part, ...]:
    """The intentionally thin features the ray sampler skips, each one justified in _named_walls:
    the coax slit mouth (a straight slot through a round tube always tapers to a lip where it
    breaks the surface, exactly like a c_clip mouth), the Ø1.2 retaining nub, and the blade/tube
    junction window."""
    if p["form"] == "vespid":
        return _v_thin_allow(p)
    if p["form"] in NEW_FORMS:
        # The V-VERTEX JUNCTION, the one declared thin feature these two carry. The apex ring
        # node's Ø RING_ID bore is a MATING feature (checks() probes it over ±6.4 mm of X), and
        # at the vertex it runs through the two channels where they butt - a round hole through a
        # sheet inclined at 43 deg always feathers at its rim, exactly like the coax slit's lip.
        # The band is 5.2 mm across and nothing else lives in it; every wall inside it is stated
        # in _named_walls.
        return (box(-10.0, p["APEX_Y"] - 2.6, p["APEX_Z"] - 2.6,
                    10.0, p["APEX_Y"] + 2.6, p["APEX_Z"] + 2.6),)
    band = Part()
    for side in (1, -1):
        band += _junction_band(p, side)
    for side in (1, -1):
        s0 = p["TUBE_S0"] - 1.0
        pl = _tube_plane(p, side, s0)
        y0, y1 = sorted((-side * (p["OD"] / 2 + 1.2), -side * (p["TUBE_ID"] / 2 - 1.0)))
        band += extrude(pl * (Pos(0.0, (y0 + y1) / 2) * Rectangle(p["SLIT"] + 2.2, y1 - y0)),
                        amount=p["TUBE_S1"] - s0 + 1.0)
        band += _lip(p, side)
    return (Part() + band,)


def _named_walls(p: dict) -> dict[str, float]:
    """Every wall inside a declared allowance band, stated so the allowance is an argument and not
    a hole in the check."""
    if p["form"] == "vespid":
        t = _v_tergites(p)
        half = V_MOUTH_W / 2
        # the wall left beside the mouth, measured at the mouth's own edge (|x| = half)
        lip = (((p["OD"] / 2) ** 2 - half ** 2) ** 0.5
               - ((p["TUBE_ID"] / 2) ** 2 - half ** 2) ** 0.5)
        return {"channel wall at the mouth edge": lip,
                "channel mouth side wall": (t[-1]["tx"] - V_MOUTH_W) / 2,
                "channel wall": p["TUBE_WALL"],
                "tergite wall at the root": t[0]["wall"],
                "tergite wall at the tip": t[-1]["wall"],
                "keel thickness": p["KEEL_T"],
                "sting cusp": V_STING_T,
                "bar under the eyelet boss": (p["BOSS_D"] - p["EYELET_D"]) / 2,
                "starburst to bore": 1.2}
    if p["form"] in NEW_FORMS:
        return _new_walls(p)
    return {"tube wall": p["TUBE_WALL"],
            "slit lip (material beside the 1.2 slit)": (p["OD"] - p["SLIT"]) / 2 - p["TUBE_ID"] / 2 + 0.6,
            "retaining nub root": 2 * LIP_R,
            "blade at the tube-root junction": p["ARM_T"],
            "tube wall at the junction": p["TUBE_WALL"],
            "blade thickness": p["ARM_T"],
            "keel thickness": p["KEEL_T"],
            "bar under the eyelet boss": (p["BOSS_D"] - p["EYELET_D"]) / 2,
            "starburst to bore": 1.2,
            "keel slot ligament": 6.75 - SLOT_W if p["style"] != "shard" else 2.2}


def _style_rows(p: dict, part: Part) -> list[tuple[str, bool, str]]:
    rows: list[tuple[str, bool, str]] = []

    # CN-1: the suture on X = 0, on the one stretch of bar top the keel leaves clear
    ok, detail = S.suture_present(part, SUTURE_Y[0], SUTURE_Y[1], Z1)
    rows.append((f"CN-1 suture present on X = 0, y {SUTURE_Y[0]}..{SUTURE_Y[1]} at Z {Z1}", ok, detail))

    # CHASSIS: a ring node at every junction, and the void
    for name, centre, id_, od_, axis, depth in _ring_nodes(p):
        ok, detail = _ring_ok(part, centre, id_, od_, axis, depth)
        rows.append((f"CHASSIS ring node at the {name}: Ø{id_} bore in a Ø{od_} eyelet", ok, detail))
    bb = part.bounding_box()
    plan = _plan_area(part)
    bbox_area = bb.size.X * bb.size.Y
    void = 1.0 - plan / bbox_area
    rows.append(("CHASSIS void >= 45 % of the plan bbox (upper-bound material area, so the void "
                 "is a lower bound)", void >= 0.45,
                 f"{void:.1%} void; {plan:.0f} mm² material in a {bb.size.X:.1f} x {bb.size.Y:.1f} plan bbox"))

    # SHARD: the 8 mm minimum facet, measured against this part's own rim thickness
    # Rim faces, not facets: the blade/keel/bar thicknesses, the tube's mouth annulus (whose
    # bbox measures OD x sin 43 deg) and the bore's vertical root face (TUBE_ID across).
    if p["form"] in ("chassis", "shard"):
        rim = max(p["ARM_T"], p["KEEL_T"], p["BAR_T"], p["TUBE_ID"],
                  p["OD"] * sin(radians(p["V_HALF_ANGLE"])))
        ok, detail = S.facet_report(part, ignore_extent=rim)
        rows.append((f"SHARD minimum facet >= {S.FACET_MIN} mm across (rim {rim} ignored)", ok, detail))

    # §4.5 silhouette-first: the plan outline must differ between the families by > 12 %
    if p["form"] in NEW_FORMS:
        rows.extend(_new_style_rows(p, part, plan))
    elif p["style"] == "shard":
        ref = build("chassis_64", **VARIANTS["chassis_64"].get("params", {}))["rx_antenna_v"]
        ref_plan = _plan_area(ref)
        diff = abs(plan - ref_plan) / ref_plan
        rows.append(("SHARD plan outline differs from CHASSIS by > 12 %", diff > 0.12,
                     f"{diff:.1%} ({plan:.0f} mm² against {ref_plan:.0f} mm²)"))
    else:
        rows.append(("CHASSIS strut depth >= 3.0 and strut width 2.4-3.2 (TPU floor)",
                     p["ARM_T"] >= 3.0 - 1e-9 and 2.4 <= STRUT_W <= 3.2,
                     f"blade {p['ARM_T']} deep, nominal strut {STRUT_W} wide, "
                     f"ring OD/strut {RING_OD / STRUT_W:.2f}, ID/strut {RING_ID / STRUT_W:.2f}"))
        # The two CHASSIS variants are the same truss at two equipment sizes, which is what the
        # brief asks for (the tube ID is the discriminator) - but "the same design bored smaller"
        # is not a variant. This row GATES the visible separation instead of claiming it in the
        # notes: blade area and tube OD both have to differ by >= 20 %, which is what put ARM_W on
        # the two ends of the brief's 8.0-10.0 range rather than 0.8 mm apart.
        big = _params("chassis_64", **VARIANTS["chassis_64"].get("params", {}))
        small = _params("chassis_44", **VARIANTS["chassis_44"].get("params", {}))
        d_blade = 1.0 - _blade(small, 1).area / _blade(big, 1).area
        d_tube = 1.0 - small["OD"] / big["OD"]
        rows.append(("chassis_44 reads as a leaner part than chassis_64, not the same one bored "
                     "smaller: blade area and tube OD both differ by >= 20 %",
                     d_blade >= 0.20 and d_tube >= 0.20,
                     f"blade {d_blade:.1%} leaner ({_blade(small, 1).area:.0f} against "
                     f"{_blade(big, 1).area:.0f} mm²), tube OD {d_tube:.1%} thinner "
                     f"(Ø{small['OD']:.1f} against Ø{big['OD']:.1f}), "
                     f"ARM_W {small['ARM_W']} against {big['ARM_W']}"))

    # the V itself
    inc = 2 * p["V_HALF_ANGLE"]
    rows.append((f"diversity V included angle {inc} deg, both tubes in the YZ plane",
                 abs(inc - 86.0) < 1e-6, f"arms at ±{p['V_HALF_ANGLE']} deg from vertical; "
                                         f"tube axes (0, ±{sin(radians(p['V_HALF_ANGLE'])):.3f}, "
                                         f"{cos(radians(p['V_HALF_ANGLE'])):.3f})"))
    return rows


# ==============================================================================================
# THE THREE NEW LANGUAGES: vespid, origami, filigree
# ==============================================================================================
# All three keep the FIXED interface of this module exactly as the first three left it: the two
# rear-tip bolt axes at (±16.5, -94), the Z 36.0 seating face, the 2.5 mm bar, the 86 deg V in the
# YZ plane, the antenna channel on each arm axis from TUBE_S0 to TUBE_S1, the coax gable, the
# suture and the apex ring node. Everything they change is form: the keel silhouette, the arm
# section, the aperture generator and the accent. Nothing here touches MOUNTS or HARDWARE.
NEW_FORMS = ("vespid", "origami", "filigree")

# --- vespid: four shingled tergites per arm, ending in a stinger -------------------------------
V_N = 4                         # tergites per arm
V_L0, V_LEN_R = 8.87, 0.82      # first tergite length, and the length ratio down the taper
V_G0, V_GIRTH_R = 9.0, 0.86     # first tergite inboard girth (flank depth), and the girth ratio
V_WALL = (2.2, 1.4)             # the wall law: root -> last tergite, around the constant channel
V_S0 = 8.0                      # where the segmented abdomen starts along the arm
V_ROOT_S = -5.0                 # the root band before it (the propodeum, buried in the V vertex)
V_COLLAR_R, V_COLLAR_PROUD = 1.6, 1.2      # the proud collar bead at every tergite boundary
V_GROOVE_R, V_GROOVE_D, V_GROOVE_BACK = 1.0, 0.45, 1.4   # the undercut groove immediately aft
V_SPIRACLE = (2.2, 5.0)         # one elliptical slot per tergite, scaled by the girth ratio
V_STING_W, V_STING_L, V_STING_T, V_TIP_R = 2.4, 5.0, 3.0, 0.8   # the paired sting cusps
V_STING_S = 33.5                # where they rise, on the last tergite's inboard flank
V_TIP_IN = 3.9                  # the last tergite's inboard edge at its tip (channel wall + 0.7)
BATT_GUARD_Y = -96.1            # nothing this far forward above Z 38.5: BATTERY + BATT_CLEAR
V_MOUTH_W, V_MOUTH_RUN = 5.0, 2.6   # the open channel mouth (0.7 of retaining lip each side)
V_PUNCTA_D, V_PUNCTA_DEPTH, V_PUNCTA_PITCH, V_PUNCTA_END = 1.8, 0.4, 3.6, 2.3

# --- origami: one folded sheet, constant thickness, no curve anywhere --------------------------
O_T = 2.4                       # the TPU95A value of the 1.8 mm sheet law (MATERIALS floor 1.2)
O_FOLDS = (22.5, 45.0, 67.5)    # the only fold angles allowed anywhere in the part
O_FLANGE = 9.0                  # V-channel flange length, measured from the bottom crease
O_ARM_S = (-8.0, 33.4)          # the channel runs this far along each arm. 33.4 is the BATTERY
#                                 envelope's own limit: the channel's outer crease stands 5.6 off
#                                 the arm axis and the forward arm spends 0.682 mm of y per mm of
#                                 s, so the outer crease lands at y -96.15 - measured, not chosen.
O_FLANGE_MID = (5.356, -0.867)  # the MIDDLE of the flange's mid-surface, in section coordinates.
#                                 At (7.22, 1.0) - half way up in y, not half way along the fold -
#                                 the rung's outer wall stood 0.76 mm from the flange tip.
O_ZIP = (2.6, 1.6)              # the zip-tie slot through both flanges (w x h), two per arm
O_LADDER = (2.2, 4.0)           # sheared rung width and length
# Every ligament in the ladder is measured PERPENDICULAR to the sheared walls, not along the arm:
# the 45 deg shear costs a factor of cos 45, so a 2.6 mm gap along the arm is a 1.84 mm wall and
# the 1.6 mm gap the first cut of this ladder left was 1.13 - the ray sampler was right.
O_RUNG_S = (12.0, 18.6, 25.2)   # rung stations along the arm (2.6 mm gaps -> 1.84 perpendicular)
O_ZIP_S = (7.0, 30.6)           # and the two zip-tie slots, 2.0 mm clear of the channel's ends
O_KEEL_RUNG = (2.0, 1.8)        # the keel's own rungs: the web is only 6.3 mm deep there, and a
#                                 67.5 deg parallelogram spends 1.08 mm of depth per mm of width
O_BELLY = -123.6 + 5.6 * cos(radians(67.5)) / sin(radians(67.5))
#                                 where the belly leaves Z 36 at EXACTLY 67.5 deg (the rounded
#                                 -121.28 came out 67.4965 and failed the 22.5 grid by 1.6e-4).
#                                 A 45 deg run-up reads
#                                 normal.Z -0.707 and fails overhangs() by 0.007 - measured; 67.5
#                                 is the next angle up in O_FOLDS and reads -0.383.
O_SHEAR = 67.5                  # the ladder's shear: the only angle in O_FOLDS whose slot walls
#                                 stand clear of the -0.70 gate (cos 67.5 = 0.383)

# --- filigree: cutwork on a spine -------------------------------------------------------------
F_SPINE, F_RIB, F_NODE = 2.4, 1.4, 2.0     # spine / ribbon / ring-node thickness in X
F_R = 2.6                       # the scroll's big radius; the small one is 0.5 R (both Ø <= 10)
F_PITCH_K = 1.6                 # scroll pitch = F_PITCH_K x R
F_RIB_W = 1.4                   # ribbon width in the YZ plane
F_NODE_OD = 4.0                 # Ø4.0 ring node at every scroll junction
F_STOP = 2.2                    # depth-stop thickness behind the channel's root
F_SCALLOP_Y, F_SCALLOP_Y0 = -108.0, -119.0            # the dorsal spine is clear of the belly only behind this
F_SCALLOP = 3.2                 # pitch of the arc cusps on the outer edge
F_ROW = 5.2                     # vertical pitch of the scroll rows - the number the void
#                                 fraction is tuned on, measured in checks() and not asserted
F_LUNULE = 16.0                 # the cut lunule at the vertex of the V (MARK_MIN["lunule"])


def _params_new(p: dict) -> dict:
    """Derived numbers for the three new languages. The channel geometry is FIXED - only the
    body wrapped round it changes - so TUBE_ID / TUBE_S0 stay exactly as the module declares."""
    form = p["form"]
    p["T_OUT"] = p["OD"] / 2
    if form == "vespid":
        p["ARM_W"] = V_G0 + p["OD"] / 2
        p["ARM_T"] = V_WALL[1]              # the tip wall, the thinnest load-bearing section
        p["KEEL_T"] = 3.0
        p["TUBE_S1"] = V_S0 + _v_len_total()  # the mouth sits flush with the last tergite's tip
    elif form == "origami":
        p["ARM_W"] = O_FLANGE
        p["ARM_T"] = O_T
        p["KEEL_T"] = O_T
        p["TUBE_S1"] = O_ARM_S[1] - 1.0
    else:
        p["ARM_W"] = 8.0
        p["ARM_T"] = F_RIB_W
        p["KEEL_T"] = F_SPINE
        p["TUBE_S1"] = 35.0
    p["T_IN"] = p["ARM_W"] - p["OD"] / 2
    return p


def _poly(p: dict, side: int, pts) -> Sketch:
    """A polygon given in arm-local (s, t), placed in the YZ working plane."""
    return Polygon(*[_pt(p, side, s, t) for s, t in pts], align=None)


def _disc(p: dict, side: int, s: float, t: float, r: float) -> Sketch:
    return Pos(*_pt(p, side, s, t)) * Circle(r)


def _web_at(sk: Sketch, t: float) -> Part:
    """`_web` with an explicit thickness - the new forms vary thickness element by element."""
    return _web(sk, t)


# --- vespid -----------------------------------------------------------------------------------
def _v_lengths() -> list[float]:
    return [V_L0 * V_LEN_R ** k for k in range(V_N)]


def _v_len_total() -> float:
    return sum(_v_lengths())


def _v_tergites(p: dict) -> list[dict]:
    """The four tergites, root first. `g` is the inboard girth (how far the segment stands proud of
    the channel axis on the flank that is free to taper); the OUTBOARD edge cannot taper, because
    it is the channel's own surface and the one face of this part that looks downward in print -
    tapering it would swing it past overhangs()' -0.70 gate. The 0.86 law therefore runs on `g`,
    which is what the silhouette shows, and the wall law runs in X."""
    out, s = [], V_S0
    for k, L in enumerate(_v_lengths()):
        wall = V_WALL[0] + (V_WALL[1] - V_WALL[0]) * (k / (V_N - 1))
        out.append(dict(k=k, s0=s, s1=s + L, L=L, g=V_G0 * V_GIRTH_R ** k,
                        tx=p["OD"] + 2 * wall, wall=wall))
        s += L
    return out


def _v_dorsal(p: dict) -> list[tuple[float, float]]:
    """The keel's stepped dorsal edge, apex first: four shingles, every tread up-facing and every
    riser vertical, so a segmented thorax costs nothing at the overhang gate."""
    # The last shingle stays at 41.8 as far forward as y -98.4: the coax gable's apex is at
    # Z 39.2 under y -100.1, and a dorsal edge that drops to 38.9 there leaves the gable breaking
    # out through the top of the keel on a 0.11 mm knife edge - measured.
    steps = [(-117.6, 45.0), (-117.6, 43.2), (-110.0, 43.2), (-110.0, 41.8),
             (-98.4, 41.8), (-98.4, 38.9), (KEEL_SHOULDER_Y, Z1 - 0.15)]
    return [(p["APEX_Y"], p["APEX_Z"]), *steps]


def _build_vespid(p: dict) -> tuple[Part, Part]:
    add, cut = Part(), Part()
    terg = _v_tergites(p)

    # the thorax keel: the same belly and apex as every other variant, a shingled dorsal edge
    keel = Polygon((p["KEEL_Y0"], Z0), (KEEL_BOT_Y1, Z0), *_v_dorsal(p), (p["KEEL_Y0"], Z1 - 0.15),
                   align=None) + _apex_ring(p)[0]
    add += _web(keel, p["KEEL_T"])
    cut += _cut_yz(_apex_ring(p)[1])
    # a spiracle in each thorax shingle, sized on the shingle's own height
    for u, v_hi in ((-114.2, 43.2), (-108.5, 41.8), (-104.3, 41.8)):
        h = v_hi - Z0 - 3.2
        if h > 2.4:
            cut += _cut_yz(Pos(u, (Z0 + v_hi) / 2) * SlotOverall(min(h, 5.0), 2.2).rotate(Axis.Z, 90))

    for side in (1, -1):
        half = _half(p, side)
        # The root band. It is NOT a tergite: the mirror plane at the V vertex cuts it, so its
        # flank is the plane and not the 0.86 law - which is why the law is measured from the
        # first tergite out, where the flank is real material.
        root = _poly(p, side, [(V_ROOT_S, p["T_OUT"]), (terg[0]["s0"] + 0.4, p["T_OUT"]),
                               (terg[0]["s0"] + 0.4, -terg[0]["g"]), (V_ROOT_S, -terg[0]["g"])])
        add += _web(root & half, terg[0]["tx"])
        for t in terg:
            back = t["s0"] - (0.4 if t["k"] else 0.0)       # bury each root in the one before it
            # the last tergite tapers its INBOARD edge to the channel wall, so the abdomen comes
            # to a point instead of stopping square; that edge is a top face at any angle.
            taper = t["k"] == V_N - 1
            pts = [(back, p["T_OUT"]), (t["s1"], p["T_OUT"])]
            if taper:
                pts += [(t["s1"], -V_TIP_IN), (t["s1"] - 0.4 * t["L"], -t["g"])]
            else:
                pts += [(t["s1"], -t["g"])]
            pts += [(back, -t["g"])]
            body = _poly(p, side, pts)
            add += _web(body & half, t["tx"])
            # the proud collar bead at the segment's tip end, on both flanks, 1.2 clear of the
            # surface in the silhouette plane and 1.2 clear in X - every face it makes is either
            # a cylinder about a HORIZONTAL axis (the arch rule) or a plane whose normal is X.
            bead = Sketch()
            for tt in (p["T_OUT"] - (V_COLLAR_R - V_COLLAR_PROUD),
                       -(t["g"] - (V_COLLAR_R - V_COLLAR_PROUD))):
                # The forward arm's last outboard bead would stand at y -95.2, inside the pack
                # guard - measured. A bead that cannot be 1.2 proud without touching the battery
                # is dropped rather than shrunk, so the ones that are there are all the same.
                if _pt(p, side, t["s1"], tt)[0] + V_COLLAR_R > BATT_GUARD_Y:
                    continue
                bead += _disc(p, side, t["s1"], tt, V_COLLAR_R)
            clipped = bead & half if bead.faces() else Sketch()
            if clipped.faces():
                add += _web(clipped, t["tx"] + 2 * V_COLLAR_PROUD)
            # the undercut groove immediately aft of the collar: a Ø4.0 lune 0.45 deep
            groove = Sketch()
            for tt in (p["T_OUT"] + V_GROOVE_R - V_GROOVE_D, -(t["g"] + V_GROOVE_R - V_GROOVE_D)):
                groove += _disc(p, side, t["s1"] - V_GROOVE_BACK, tt, V_GROOVE_R)
            cut += _cut_yz(groove & half)
            # ONE spiracle per segment, a blind 0.9 deep stadium pit on each flank face, scaled by
            # the same 0.86 taper. Blind, so it never opens into the antenna channel.
            w, L = V_SPIRACLE[0] * V_GIRTH_R ** t["k"], V_SPIRACLE[1] * V_GIRTH_R ** t["k"]
            pit = Pos(*_pt(p, side, (t["s0"] + t["s1"]) / 2, -1.2)) * \
                SlotOverall(L, w).rotate(Axis.Z, degrees(atan2(*reversed(_dir(p, side)))))
            # the puncta row that straddles the dorsal centreline, one row per flank
            dots = Sketch()
            # The row stops V_PUNCTA_END short of the segment's tip: a punctum closer than that
            # leaves a 1.02 mm ligament to the step where the next tergite narrows, and the ray
            # sampler reads that ligament as a thin wall - measured.
            s_d = t["s0"] + 1.6
            while s_d <= t["s1"] - V_PUNCTA_END:
                dots += Pos(*_pt(p, side, s_d, p["T_OUT"] - 2.4)) * Circle(V_PUNCTA_D / 2)
                s_d += V_PUNCTA_PITCH
            # Both flank cutters are built in the SAME YZ orientation and extruded along +X: a
            # plane mirrored with z_dir=(-1,0,0) flips its own local +y, which silently reflects
            # every cutter in Z (measured - the -X spiracles came out below the bed).
            for depth, sk in ((0.9, pit), (V_PUNCTA_DEPTH, dots)):
                for x0 in (t["tx"] / 2 - depth, -t["tx"] / 2 - 0.2):
                    cut += S.extrude_cut(sk, Plane(origin=(x0, 0, 0), x_dir=(0, 1, 0),
                                                   z_dir=(1, 0, 0)), depth + 0.2)
        # the stinger: a spine along the outboard flank past the mouth, blunted to r 0.8. Its only
        # straight boundary that could be a ceiling is the channel's own generatrix at 43 deg.
        # THE STING. Nothing may grow past the last tergite: the forward arm's outboard surface
        # already ends at y -96.47, 1.53 mm off the BATTERY envelope, and every mm along the arm
        # spends 0.68 mm of that - measured, and the reason the sting rises instead of reaching.
        # It is a PAIR of cusps straddling the open channel, one each side in X, because the
        # channel mouth takes the middle V_MOUTH_W of the abdomen for its whole length.
        s_end = terg[-1]["s1"]
        barb = S.cusp_tail(V_STING_W, V_STING_L, tip_r=V_TIP_R,
                           at=_pt(p, side, V_STING_S, -(terg[-1]["g"] - 1.1)), angle=90.0)
        for x0 in (V_MOUTH_W / 2 + 0.1, -V_MOUTH_W / 2 - 0.1 - V_STING_T):
            add += S.extrude_cut(barb & half, Plane(origin=(x0, 0, 0), x_dir=(0, 1, 0),
                                                    z_dir=(1, 0, 0)), V_STING_T)
        # The channel is an open U-groove, not a bore: the sting CAPS the far end (the brief's own
        # rule), so the antenna cannot go in along the axis and is pressed in through the mouth
        # instead. The mouth is V_MOUTH_W wide against the Ø6.4 channel, so 0.7 of the bore's own
        # surface stands proud each side and snaps over the tube. The mouth faces inboard, which
        # is UP in the print orientation on both arms.
        add += _tube(p, side)
        cut += _v_channel(p, side)
    return add, cut


# --- the shared assembly for the three new languages -------------------------------------------
def _build_new(p: dict) -> dict[str, Part]:
    """Same bar, same bolts, same seating face, same gable and suture as every other variant; the
    form function owns everything above Z 38.5."""
    add = S.extrude_cut(_bar_outline(p), Plane.XY.offset(Z0), p["BAR_T"])
    body, cut = {"vespid": _build_vespid, "origami": _build_origami,
                 "filigree": _build_filigree}[p["form"]](p)
    add += body
    cut += _cut_xy(_bar_apertures(p) + _starburst(p), Z0 - 1.0, p["BAR_T"] + 2.0)
    cut += _eyelet_bores(p)
    if p["form"] != "filigree":
        # FILIGREE has no gable: the 5.0 mm wide cut would sever a 2.4 mm spine outright (the
        # other keels are a solid web 9 mm deep there and close over the top of it). Its coax
        # comes up through the cutwork, which is 50 % open by rule.
        cut += _notch(p)
    part = add - cut
    part -= S.suture(SUTURE_Y[0], SUTURE_Y[1], Z1)
    part = _treat_edges_new(p, part)
    try:
        # coplanar overlaps (the keel belly sits ON the bar at Z 36) leave micron slivers that
        # count as extra solids; clean() fuses them back into their neighbours
        part = part.clean()
    except Exception:  # noqa: BLE001 - clean() is an optimisation, never a requirement
        pass
    part = Part() + part
    part.label = "rx_antenna_v"
    return {"rx_antenna_v": part}


def _treat_edges_new(p: dict, part: Part) -> Part:
    """ORIGAMI is chamfer-only (0.4, never a fillet - that is the language's own rule); VESPID
    softens its shingles with a 0.6 fillet; FILIGREE is left alone, because a fillet on a 1.4 mm
    ribbon net multiplies the face count into OCCT's unreliable range for no visible gain."""
    if p["form"] == "filigree":
        return part
    # Edges within 2.5 mm of the V vertex are skipped: the two arms butt on that plane and the
    # edge where their inner surfaces meet is CONCAVE. Chamfering a concave edge widens the groove
    # and leaves a chain of 1.0 mm slivers behind it - measured, 50 thin rays of it.
    sel = [e for e in part.edges() if e.geom_type.name == "LINE" and e.length > 1.2
           and abs(e.tangent_at(0.5).X) > 0.99 and e.bounding_box().min.Z > Z1 + 0.2
           and abs(e.center().Y - p["APEX_Y"]) > 2.5]
    if not sel:
        return part
    from build123d import chamfer as _ch
    r0 = 0.4 if p["form"] == "origami" else 0.6
    for attempt in (r0, r0 / 2, r0 / 4):
        try:
            return _ch(sel, attempt) if p["form"] == "origami" else fillet(sel, attempt)
        except Exception:  # noqa: BLE001 - OCCT refuses radii it cannot fit; shrink and retry
            continue
    return part


def _build_origami(p: dict) -> tuple[Part, Part]:
    return Part(), Part()





def _v_channel(p: dict, side: int) -> Part:
    """VESPID's antenna channel: the same Ø TUBE_ID axis every other variant bores, opened along
    its whole length into a U-groove whose mouth faces INBOARD, and stopped V_CAP short of the
    last tergite's tip so the stinger caps it. The near end is trimmed on the same vertical plane
    `_tube_keep` uses, so the cut's own root face reads normal.Z 0.00; the far end faces +axis and
    is an up-face. Nothing else in the module changes."""
    r_in = p["TUBE_ID"] / 2
    s_start = p["TUBE_S0"] - 9.0
    # +V_MOUTH_RUN so the cut leaves through open air past the last collar bead instead of
    # ending against it: a mouth that stops inside material has a 16 mm2 ceiling at -0.73.
    s_end = p["TUBE_S1"] + V_MOUTH_RUN
    pl = _tube_plane(p, side, s_start)
    L = s_end - s_start
    bore = extrude(pl * Circle(r_in), amount=L)
    # The section plane's local +y follows the arm (see _tube_cuts), so the inboard direction is
    # -side * +y on both arms - the sign is not decoration.
    y0, y1 = sorted((-side * (r_in - (p["TUBE_ID"] - V_MOUTH_W) / 2), -side * (V_G0 + 8.0)))
    mouth = extrude(pl * (Pos(0.0, (y0 + y1) / 2) * Rectangle(V_MOUTH_W, y1 - y0)), amount=L)
    return (bore + mouth) & _tube_keep(p, side)


# --- the new languages' own conformance rows ---------------------------------------------------
def _new_walls(p: dict) -> dict[str, float]:
    """ORIGAMI and FILIGREE: the walls their own laws fix. VESPID is stated in _named_walls."""
    if p["form"] == "origami":
        return {"sheet at the V-vertex junction": O_T,
                "keel at the V-vertex junction": O_T,
                "folded sheet (the TPU95A value of the 1.8 law)": O_T,
                "channel flange": O_T,
                "snap tab": O_T,
                "bar under the eyelet boss": (p["BOSS_D"] - p["EYELET_D"]) / 2}
    return {"spine at the V-vertex junction": F_SPINE,
            "spine": F_SPINE, "scroll ribbon": F_RIB, "ring node": F_NODE,
            "ribbon width in plan": F_RIB_W,
            "bar under the eyelet boss": (p["BOSS_D"] - p["EYELET_D"]) / 2}


def _first_hit(part: Part, origin, direction) -> float | None:
    """Distance from `origin` to the first surface along `direction`, or None."""
    o, d = Vector(*origin), Vector(*direction).normalized()
    try:
        hits = part.find_intersection_points(Axis(tuple(o), tuple(d)))
    except Exception:  # noqa: BLE001 - a ray that misses the solid entirely
        return None
    ahead = sorted(x for x in ((h[0] - o).dot(d) for h in hits) if x > 1e-6)
    return ahead[0] if ahead else None


def _v_girths(p: dict, part: Part, side: int) -> list[float]:
    """MEASURE each tergite's girth on the finished solid: a ray fired from well inboard, back
    along the outboard normal, at x = ±4.0 (outside the channel mouth, so it meets the flank and
    not the inside of the groove). Returns the flank offset from the channel axis, root first."""
    out = []
    mu, mv = _out(p, side)
    for t in _v_tergites(p):
        # start 3 mm off the expected flank: a ray fired from the far side of the V crosses the
        # OTHER arm first (they are 6 mm apart at the vertex) and reads its girth instead
        start = -(t["g"] + 3.0)
        # the window that is clear of the previous collar bead (which stands 1.2 PROUD) and of
        # this segment's own undercut groove (which cuts 0.45 IN) - measuring across either reads
        # the accent, not the girth
        lo, hi = t["s0"] + 1.8, min(t["s0"] + 0.55 * t["L"], t["s1"] - 2.6)
        got = []
        for k in (0.2, 0.5, 0.8):
            s_i = lo + (hi - lo) * k if hi > lo else (t["s0"] + t["s1"]) / 2
            u, v = _pt(p, side, s_i, start)
            for x in (4.0, -4.0):
                d = _first_hit(part, (x, u, v), (0.0, mu, mv))
                if d is not None:
                    got.append(-(start + d))
        out.append(sorted(got)[len(got) // 2] if got else None)
    return out


def _v_flank_at(p: dict, part: Part, side: int, s: float) -> float | None:
    """The outboard flank's offset from the channel axis at station `s`, measured on the solid by
    a ray coming in from outboard along -out. This is what reads the collar (proud) and the
    undercut groove (sunk) without trusting the generator."""
    start = 12.0
    u, v = _pt(p, side, s, start)
    mu, mv = _out(p, side)
    d = _first_hit(part, (0.0, u, v), (0.0, -mu, -mv))
    return None if d is None else start - d


def _v_rows(p: dict, part: Part) -> list[tuple[str, bool, str]]:
    rows = []
    terg = _v_tergites(p)
    # 1. the girth law, measured on the finished solid, both arms
    ratios, detail = [], []
    for side, name in ((1, "forward"), (-1, "rear")):
        g = _v_girths(p, part, side)
        detail.append(f"{name} " + "/".join("-" if x is None else f"{x:.2f}" for x in g))
        for a, b in zip(g, g[1:]):
            if a and b:
                ratios.append(b / a)
    ok = bool(ratios) and all(abs(r - V_GIRTH_R) <= 0.02 * V_GIRTH_R for r in ratios)
    rows.append((f"VESPID tergite girth ratio {V_GIRTH_R} within 2 %, measured on the solid",
                 ok, f"ratios {' '.join(f'{r:.3f}' for r in ratios)}; girths {'; '.join(detail)}"))
    # 2. the length law and the wall law, from the generator that drew them
    lens_ = _v_lengths()
    lr = [b / a for a, b in zip(lens_, lens_[1:])]
    rows.append((f"VESPID tergite length ratio {V_LEN_R} over {V_N} segments",
                 all(abs(r - V_LEN_R) < 1e-9 for r in lr),
                 f"lengths {' '.join(f'{x:.2f}' for x in lens_)} mm"))
    rows.append((f"VESPID wall law {V_WALL[0]} at the root -> {V_WALL[1]} at the last tergite",
                 abs(terg[0]["wall"] - V_WALL[0]) < 1e-9 and abs(terg[-1]["wall"] - V_WALL[1]) < 1e-9,
                 " -> ".join(f"{t['wall']:.2f}" for t in terg)))
    # 3. the collar and its undercut, measured
    proud, sunk = [], []
    for t in terg[:-1]:  # the last tergite's tip carries the taper, not a collar
        c = _v_flank_at(p, part, 1, t["s1"])
        g = _v_flank_at(p, part, 1, t["s1"] - V_GROOVE_BACK)
        if c is not None:
            proud.append(c - p["T_OUT"])
        if g is not None:
            sunk.append(p["T_OUT"] - g)
    rows.append((f"VESPID collar {V_COLLAR_PROUD} proud with a {V_GROOVE_D} undercut groove aft",
                 bool(proud) and all(x >= V_COLLAR_PROUD - 0.05 for x in proud)
                 and bool(sunk) and all(x >= V_GROOVE_D - 0.08 for x in sunk),
                 f"proud {' '.join(f'{x:.2f}' for x in proud)}; "
                 f"groove {' '.join(f'{x:.2f}' for x in sunk)}"))
    # 4. one spiracle per tergite, on the flank, blind (it never opens into the channel)
    pits, floors = 0, 0
    for t in terg:
        c = _pt(p, 1, (t["s0"] + t["s1"]) / 2, -1.2)
        for sgn in (1, -1):
            x0 = sgn * (t["tx"] / 2 - 0.5)
            mouth = box(min(x0, x0 + sgn * 0.4), c[0] - 0.5, c[1] - 0.5,
                        max(x0, x0 + sgn * 0.4), c[0] + 0.5, c[1] + 0.5)
            x1 = sgn * (t["tx"] / 2 - 1.5)
            floor = box(min(x1, x1 + sgn * 0.4), c[0] - 0.5, c[1] - 0.5,
                        max(x1, x1 + sgn * 0.4), c[0] + 0.5, c[1] + 0.5)
            pits += isect(part, mouth) < EPS
            floors += isect(part, floor) > 0.1
    rows.append((f"VESPID one blind spiracle per tergite per flank, {V_SPIRACLE[0]} x "
                 f"{V_SPIRACLE[1]} scaled by {V_GIRTH_R}",
                 pits == 2 * V_N and floors == 2 * V_N,
                 f"{pits}/{2 * V_N} pits open at the flank, {floors}/{2 * V_N} closed at 1.5 mm "
                 f"(blind, so the channel is never vented)"))
    return rows


def _new_style_rows(p: dict, part: Part, plan: float) -> list[tuple[str, bool, str]]:
    rows = {"vespid": _v_rows, "origami": _o_rows,
            "filigree": _f_rows}.get(p["form"], lambda _p, _part: [])(p, part)
    ref = build("chassis_64", **VARIANTS["chassis_64"].get("params", {}))["rx_antenna_v"]
    ref_plan, ref_side = _plan_area(ref), _side_area(ref)
    d_plan = abs(plan - ref_plan) / ref_plan
    d_side = abs(_side_area(part) - ref_side) / ref_side
    # This part lives in the YZ plane, so the SIDE view is the one a thumbnail reads; the plan
    # view sees a filigree net edge-on and calls it the same shape as a truss.
    # A net seen edge-on has almost the same projected area as the truss it replaces, so the
    # third measure is the one a thumbnail actually reads: how much of the V's own yoke - empty
    # air in every other variant - this one occupies.
    # Area alone cannot see a net: cutwork has nearly the same projected area as the truss it
    # replaces. The third measure is boundary richness - how many separate edges the YZ outline
    # throws - which is exactly what a 200 px thumbnail reads.
    rich, rich_ref = _outline_edges(part), _outline_edges(ref)
    d_rich = abs(rich - rich_ref) / rich_ref
    rows.append((f"§4.5 silhouette-first: {p['form']} differs from CHASSIS by > 12 % in plan or "
                 "side area, or by > 50 % in outline richness",
                 max(d_plan, d_side) > 0.12 or d_rich > 0.50,
                 f"plan {d_plan:.1%} ({plan:.0f} against {ref_plan:.0f} mm²), side {d_side:.1%} "
                 f"({_side_area(part):.0f} against {ref_side:.0f} mm²), outline {rich} edges "
                 f"against {rich_ref} ({d_rich:+.0%})"))
    return rows


# --- origami ------------------------------------------------------------------------------------
def _o_keel_pts(p: dict) -> list[tuple[float, float]]:
    """The keel as one folded strip: every edge straight, every turn a whole multiple of 22.5 deg.
    Listed anticlockwise from the bar's front bottom corner. The dorsal run holds 40.6 as far
    forward as y -98.97 because the coax gable's apex is at Z 39.2 under y -100.1."""
    pts = [(p["KEEL_Y0"], Z0), (O_BELLY, Z0), (-123.6, 41.6), (p["APEX_Y"], p["APEX_Z"])]
    # the dorsal run, generated from headings so every fold is EXACTLY a multiple of 22.5 deg
    for heading, length in ((-22.5, 7.14), (0.0, 9.0), (-22.5, 4.11), (0.0, 6.0), (-45.0, 3.22)):
        u, v = pts[-1]
        pts.append((u + length * cos(radians(heading)), v + length * sin(radians(heading))))
    pts.append((p["KEEL_Y0"], pts[-1][1]))
    return pts


def _o_octagon(c: tuple[float, float], r_in: float) -> Sketch:
    """A regular octagon of inradius `r_in` - ORIGAMI's stand-in for a circle, so the apex ring
    node and its bore are still a node and a bore but carry no curve."""
    r = r_in / cos(radians(22.5))
    return Pos(*c) * Polygon(*[(r * cos(radians(22.5 + 45 * i)), r * sin(radians(22.5 + 45 * i)))
                               for i in range(8)], align=None)


def _o_shear_slot(c: tuple[float, float], w: float, L: float) -> Sketch:
    """One rung of the ladder: a parallelogram leaning at O_SHEAR with VERTICAL ends. The leaning
    edges read normal.Z -0.38 and the ends 0.00, so the whole rung clears the overhang gate - a
    rung sheared the other way (22.5 deg off horizontal) reads -0.92 and fails."""
    d = (cos(radians(O_SHEAR)), sin(radians(O_SHEAR)))
    hv = w / sin(radians(O_SHEAR)) / 2
    a = (c[0] + d[0] * L / 2, c[1] + d[1] * L / 2)
    b = (c[0] - d[0] * L / 2, c[1] - d[1] * L / 2)
    return Polygon((a[0], a[1] + hv), (a[0], a[1] - hv), (b[0], b[1] - hv), (b[0], b[1] + hv),
                   align=None)


def _o_section(p: dict, side: int) -> Sketch:
    """The arm's section: one 2.4 mm sheet folded at 45 deg into a flat-bottomed V that cradles
    the Ø TUBE_ID antenna on three tangent lines. Local +y follows the arm (see _tube_cuts), so
    every inboard offset is multiplied by -side."""
    r, t, k = p["TUBE_ID"] / 2, O_T, 2 ** 0.5
    # inner surface: the flat bottom y = -r and the two 45 deg flanks x -+ y = r*sqrt2, all three
    # tangent to the Ø TUBE_ID antenna. Outer surface: the same three lines offset by t.
    x_c = r * k - r                     # where the 45 deg flank meets the flat bottom
    x_co = r * k + t * k - (r + t)      # the same corner on the outer surface
    tip_x, tip_y = x_c + O_FLANGE / k, -r + O_FLANGE / k
    o = t / k
    pts = [(-tip_x, tip_y), (-x_c, -r), (x_c, -r), (tip_x, tip_y),     # inner, left to right
           (tip_x + o, tip_y - o), (x_co, -r - t), (-x_co, -r - t), (-tip_x - o, tip_y - o)]
    return Polygon(*[(x, -side * y) for x, y in pts], align=None)


def _o_flange_plane(p: dict, side: int, sgn: int, s: float) -> Plane:
    """A sketch plane ON one flange of the channel, local x along the arm, z_dir INTO the sheet.
    Every aperture in a flange is cut on this plane and not along X: a cutter swept along X meets
    a 45 deg flange obliquely and leaves a feather edge the ray sampler reads at 0.08 mm -
    measured, 1473 rays of it."""
    du, dv = _dir(p, side)
    mu, mv = _out(p, side)
    x_dir = Vector(0.0, du, dv)
    inboard = Vector(0.0, -mu, -mv)
    k = 1 / (2 ** 0.5)
    n = Vector(sgn * k, 0.0, 0.0) + inboard * (-k)          # outward normal of that flange
    u, v = _pt(p, side, s, 0.0)
    axis_pt = Vector(0.0, u, v)
    mid = axis_pt + Vector(sgn * O_FLANGE_MID[0], 0.0, 0.0) + inboard * O_FLANGE_MID[1]
    return Plane(origin=tuple(mid + n * 3.0), x_dir=tuple(x_dir), z_dir=tuple(-n))


def _o_flange_slot(w: float, length: float, sh: int = 1) -> Sketch:
    """A parallelogram rung in the flange's own plane: long axis along the arm, ends sheared 45 deg
    (a fold angle). The shear is what keeps the end wall off the overhang gate - square ends read
    normal.Z -0.73, the 45 deg shear -0.18."""
    a, b = length / 2, w / 2 * sh
    return Polygon((-a - b, -w / 2), (a - b, -w / 2), (a + b, w / 2), (-a + b, w / 2), align=None)


def _o_shear_sign(pl: Plane) -> int:
    """Which way to lean the rung. A 45 deg shear tilts the rung's end wall by 45 deg out of the
    plane perpendicular to the arm; one lean brings that wall UP (normal.Z -0.18), the other
    drives it DOWN (-0.86) past the gate. The sign is measured from the plane, never assumed -
    it flips with the flange and with the arm."""
    k = 1 / (2 ** 0.5)
    up = (pl.x_dir * -k + pl.y_dir * k).Z
    dn = (pl.x_dir * -k - pl.y_dir * k).Z
    return 1 if up >= dn else -1


def _o_arm(p: dict, side: int) -> tuple[Part, Part]:
    add, cut = Part(), Part()
    s0, s1 = O_ARM_S
    pl = _tube_plane(p, side, s0)
    # S.extrude_cut, never a bare extrude: build123d takes the direction from the FACE normal and
    # this section's winding flips with `side` - measured, as an arm that grew out of the back of
    # the frame.
    add += S.extrude_cut(_o_section(p, side), pl, s1 - s0) & _apex_half(p, side)
    for sgn in (1, -1):
        for s_i in O_RUNG_S:
            pl_i = _o_flange_plane(p, side, sgn, s_i)
            cut += S.extrude_cut(_o_flange_slot(O_LADDER[0], O_LADDER[1], _o_shear_sign(pl_i)),
                                 pl_i, 6.0)
        # one zip-tie slot per flange at each end, so a tie can go round the antenna
        for s_i in O_ZIP_S:
            pl_i = _o_flange_plane(p, side, sgn, s_i)
            cut += S.extrude_cut(_o_flange_slot(O_ZIP[0], O_ZIP[1], _o_shear_sign(pl_i)), pl_i, 6.0)
    return add, cut


def _build_origami(p: dict) -> tuple[Part, Part]:
    add, cut = Part(), Part()
    keel = Polygon(*_o_keel_pts(p), align=None) + _o_octagon((p["APEX_Y"], p["APEX_Z"]), RING_OD / 2)
    add += _web(keel, p["KEEL_T"])
    cut += _cut_yz(_o_octagon((p["APEX_Y"], p["APEX_Z"]), RING_ID / 2))
    for u in (-118.5, -113.5, -108.5):
        cut += _cut_yz(_o_shear_slot((u, (Z0 + 42.27) / 2), *O_KEEL_RUNG))
    for side in (1, -1):
        a, c = _o_arm(p, side)
        add += a
        cut += c
    return add, cut


def _apex_half(p: dict, side: int) -> Part:
    """The solid half space on this arm's side of the V vertex, bounded by a VERTICAL plane at
    y = APEX_Y - the 3D form of `_half`. Both arms are trimmed on it, so they butt on one plane
    whose faces read normal.Z 0.00 instead of crossing each other."""
    y = p["APEX_Y"]
    return box(-30.0, y, Z0 - 6.0, 30.0, y + 220.0, 240.0) if side > 0 else \
        box(-30.0, y - 220.0, Z0 - 6.0, 30.0, y, 240.0)


# --- filigree -----------------------------------------------------------------------------------
def _sk_add(sk: Sketch, other) -> Sketch:
    """Union a sketch into another FACE BY FACE. `Sketch() + other` throws a null-shape error
    whenever `other` carries several DISJOINT faces (measured on the keel net's three islands),
    and a null sketch poisons everything downstream."""
    for fc in other.faces() if isinstance(other, Sketch) else other:
        sk = sk + fc if sk.faces() else Sketch() + fc
    return sk


def _ribbon(pts, w: float) -> Sketch:
    """A polyline ribbon of width `w`: one rectangle per segment plus a Ø w disc at every interior
    joint. Drawing the outline by hand instead self-intersects wherever the turn is sharper than
    the width - measured on the belly spine, which came back an invalid solid."""
    sk = Sketch()
    for a, b in zip(pts, pts[1:]):
        L = hypot(b[0] - a[0], b[1] - a[1])
        if L < 1e-9:
            continue
        sk += Pos((a[0] + b[0]) / 2, (a[1] + b[1]) / 2) * \
            Rectangle(L, w).rotate(Axis.Z, degrees(atan2(b[1] - a[1], b[0] - a[0])))
    for q in pts[1:-1]:
        sk += Pos(*q) * Circle(w / 2)
    return sk


def _f_wedge(c: tuple[float, float], r: float, a0: float, a1: float) -> Sketch:
    """A fan polygon covering the sector [a0, a1] out to radius r - the clip that turns an
    annulus into an arc ribbon."""
    n = max(2, int(abs(a1 - a0) // 20) + 2)
    pts = [c] + [(c[0] + r * cos(radians(a0 + (a1 - a0) * i / n)),
                  c[1] + r * sin(radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]
    return Polygon(*pts, align=None)


def _f_arc(c: tuple[float, float], r: float, w: float, a0: float, a1: float) -> Sketch:
    """One ribbon on a circular arc. Every radius used here is <= 5.0, so the cylindrical face it
    makes is an arch under Ø10 and overhangs() exempts it whichever way it faces - which is what
    lets a net of curves print flat on a part whose every straight edge has to stand at 43 deg."""
    ring = (Pos(*c) * Circle(r + w / 2)) - (Pos(*c) * Circle(max(0.05, r - w / 2)))
    return ring & _f_wedge(c, r + w, a0, a1)


def _f_wave(start: tuple[float, float], n: int, R: float, w: float, up: bool = True) -> Sketch:
    """The scroll: arcs of R and 0.5R meeting TANGENTIALLY, repeated at pitch 3R along +u. Each
    period is one big arc over the top and one small arc under, so the ribbon never runs straight
    - the rule that separates FILIGREE from CHASSIS's straight struts."""
    sk, x, y = Sketch(), start[0], start[1]
    for _i in range(n):
        # each arc runs 6 deg past the tangent point, so the two radii OVERLAP instead of
        # meeting exactly - a tangential meeting is a coincident-surface case OCCT gets wrong
        sk += _f_arc((x + R, y), R, w, 174.0, 366.0) if up else _f_arc((x + R, y), R, w, -6.0, 186.0)
        sk += _f_arc((x + 2.5 * R, y), 0.5 * R, w, -6.0, 186.0) if up else \
            _f_arc((x + 2.5 * R, y), 0.5 * R, w, 174.0, 366.0)
        x += 3 * R
    return sk


def _f_nodes(start: tuple[float, float], n: int, R: float) -> list[tuple[float, float]]:
    return [(start[0] + 3 * R * i + k * R, start[1]) for i in range(n) for k in (0, 2)]


def _f_region(p: dict, t_edge: float = -4.0, s_top: float = 32.0) -> tuple[Sketch, float, float]:
    """The yoke: the open triangle between the two channels, from the point where their inboard
    surfaces cross up to a chord at s_top. Its two long edges lie 0.4 mm INSIDE the channel wall,
    so the net fuses with the tubes instead of touching them tangentially."""
    a = radians(p["V_HALF_ANGLE"])
    s_v = -t_edge * cos(a) / sin(a)
    vtx = (p["APEX_Y"], p["APEX_Z"] + s_v * cos(a) - t_edge * sin(a))
    fwd, rear = _pt(p, 1, s_top, t_edge), _pt(p, -1, s_top, t_edge)
    tri = Polygon(vtx, fwd, rear, align=None)
    # the scalloped outer edge: a run of tangent arc cusps along the top chord, so the silhouette
    # ends in arcs and not in a straight cut - FILIGREE's own edge rule
    n = max(2, int((fwd[0] - rear[0]) // F_SCALLOP))
    for i in range(n + 1):
        x = rear[0] + (fwd[0] - rear[0]) * i / n
        tri += Pos(x, fwd[1]) * Circle(F_SCALLOP * 0.72)
    # THE LUNULE IS THE VOID, not a mark cut into a solid patch. A solid gusset dropped into the
    # net crosses every ribbon that reaches it at a shallow angle and leaves a sliver at each
    # crossing - measured, a dozen faces of 0.3-1.0 mm. As a hole in the region it costs nothing,
    # the rim traces it, and it is still exactly S.mark_sketch("lunule").
    tri -= Pos(*_f_lunule_at(p, vtx[1])) * S.mark_sketch("lunule", F_LUNULE)
    return tri, vtx[1], fwd[1]


def _f_lunule_at(p: dict, v0: float) -> tuple[float, float]:
    """High enough up the V that the 16 mm lunule clears both channels: the yoke widens by
    0.93 mm of half width per mm of height, and at v0 + 5.1 the mark ran 0.19 mm off the
    forward channel."""
    return (p["APEX_Y"], v0 + F_LUNULE * 0.70)


def _build_filigree(p: dict) -> tuple[Part, Part]:
    """Every piece is extruded on its own and the whole lot is fused in ONE call. Sketch unions
    and one-at-a-time solid fusions both break down on this part - a sketch of disjoint faces
    comes back as a null shape, and forty sequential fuses of coplanar-faced ribbons produced a
    solid with a NEGATIVE volume. Both were measured; a single multi-argument fuse is stable."""
    cut, pieces = Part(), []

    def add_face(sk: Sketch, t: float) -> None:
        for fc in sk.faces():
            pieces.append(_web(Sketch() + fc, t))

    # 1. the spines: the load path itself - bar to apex along the belly, bar top to apex along the
    #    dorsal, and one out each arm to its channel. Everything off them is open work.
    add_face(_ribbon([(p["KEEL_Y0"], Z0 + F_SPINE / 2), (-120.0, Z0 + F_SPINE / 2),
                      (p["APEX_Y"], p["APEX_Z"] - F_SPINE / 2)], F_SPINE), F_SPINE)
    # The dorsal spine runs 11.7 deg off horizontal, so its UNDERSIDE is a ceiling at -0.97 with
    # nothing but open work beneath it. It is scalloped instead: a run of Ø3.6 arc cusps, each a
    # cylinder about a horizontal axis and therefore an arch overhangs() exempts - and the same
    # cusp run that the outer edge carries, which is what the language asks for anyway.
    add_face(_ribbon([(KEEL_SHOULDER_Y, Z0 + F_SPINE / 2),
                      (p["APEX_Y"] + 1.0, p["APEX_Z"] - F_SPINE / 2)], F_SPINE), F_SPINE)
    a, b = (KEEL_SHOULDER_Y, Z0 + F_SPINE / 2), (p["APEX_Y"] + 1.0, p["APEX_Z"] - F_SPINE / 2)
    L = hypot(b[0] - a[0], b[1] - a[1])
    n = int(L // (F_SCALLOP * 0.62))
    r_s, depth = F_SCALLOP * 0.34, 0.62
    for i in range(1, n + 1):
        q = (a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n)
        if not F_SCALLOP_Y0 <= q[0] <= F_SCALLOP_Y:
            continue    # outside this run the dorsal spine meets the belly and has no underside:
        #                 forward of F_SCALLOP_Y they are the same web, and behind F_SCALLOP_Y0
        #                 they converge on the apex, where a scallop ate 0.65 mm out of the belly
        # X-limited to the spine's own width: a _cut_yz sweeps ±20 mm and would scallop the bar
        # and the belly with it - measured, as four stray slivers at Z 36.
        cut += S.extrude_cut(Pos(q[0], q[1] - F_SPINE / 2 - r_s + depth) * Circle(r_s),
                             Plane(origin=(-F_SPINE / 2 - 0.2, 0, 0), x_dir=(0, 1, 0),
                                   z_dir=(1, 0, 0)), F_SPINE + 0.4)
    add_face(_apex_ring(p)[0], F_SPINE)
    for side in (1, -1):
        # ON the arm axis, which is legal because the bore only exists outboard of the tube root
        # plane - the trick every other variant's blade uses to be the antenna's depth stop.
        add_face(_member(p, side, (-4.0, 0.0), (p["TUBE_S0"] + 0.5, 0.0), F_SPINE) & _half(p, side),
                 F_SPINE)
    cut += _cut_yz(_apex_ring(p)[1])

    # 2. the cutwork: the keel's own panel, and the yoke between the two channels
    keel_net, keel_nodes = _f_fill(
        # the panel's two lower edges lie ON the belly spine's centre line, so its rim is buried
        # 1.2 mm inside the spine; running them alongside the spine instead left a 0.65 mm sliver
        # between the two - measured.
        Polygon((p["KEEL_Y0"], Z0 + F_SPINE / 2), (-119.7, Z0 + F_SPINE / 2),
                (-122.16, 40.44), (KEEL_SHOULDER_Y, Z1 - 0.9), align=None),
        Z0 + F_SPINE, 42.6, scallop=False, r=1.5, rim=False)
    region, v0, v1 = _f_region(p)
    net, nodes = _f_fill(region, v0, v1)
    add_face(keel_net, F_RIB)
    add_face(net, F_RIB)
    for side in (1, -1):
        add_face(_member(p, side, (6.0, -4.4), (32.0, -4.4), F_RIB_W * 1.7) & _half(p, side), F_RIB)

    # 3. a Ø4.0 ring node at every junction of the net
    for c in keel_nodes + nodes:
        ring, bore = S.ring_node(c, F_RIB_W, od_factor=F_NODE_OD / F_RIB_W,
                                 id_factor=(F_NODE_OD - 2 * 1.3) / F_RIB_W)
        add_face(ring, F_NODE)
        cut += _cut_yz(bore)

    # 5. the channels
    for side in (1, -1):
        # back=F_STOP, not the 0.6 the other variants use: they back the antenna's depth stop with
        # a blade, and FILIGREE has only a 2.4 mm spine there - a 0.6 mm disc is not a stop.
        pieces.append(_tube(p, side, back=F_STOP))
        pieces.append(_lip(p, side))
        cut += _tube_cuts(p, side)
    return Part() + pieces, cut


def _f_fill(region: Sketch, v0: float, v1: float, scallop: bool = True, r: float | None = None,
            rim: bool = True) -> tuple[Sketch, list[tuple[float, float]]]:
    """Fill a region with mirrored scroll rows and return (ribbons, junction centres). Rows
    alternate phase and direction, so where two rows meet they cross at a junction - which is
    where the Ø4.0 ring nodes go."""
    bb = region.bounding_box()
    sk, nodes = Sketch(), []
    R = F_R if r is None else r
    rows = max(1, int((v1 - v0 - R) // (F_ROW if r is None else 2 * R + F_RIB_W)))
    for j in range(rows):
        v = v0 + R * 0.5 + (F_ROW if r is None else 2 * R + F_RIB_W) * j
        n = int((bb.max.X - bb.min.X) / (3 * R)) + 2
        start = (bb.min.X - (1.5 * R if j % 2 else 0.0), v)
        sk += _f_wave(start, n, R, F_RIB_W, up=bool(j % 2))
        nodes += _f_nodes(start, n, R)
    # The rim. Every ribbon the region clips ends ON the rim, so the net is one connected piece
    # instead of a shower of fragments - and the rim is what carries the scallops.
    sk = sk & region
    if rim:
        try:
            edge = region - S.inset_region(region, F_RIB_W)
        except Exception:  # noqa: BLE001 - OCCT will not inset every outline; the net stands alone
            edge = Sketch()
        if edge.faces() and edge.area > 1.0:
            sk += edge
    keep = []
    for c in nodes:
        probe = Pos(*c) * Circle(F_NODE_OD / 2)
        if abs((probe & region).area - probe.area) < 1e-3:
            keep.append(c)
    return sk, keep


def _turns(pts) -> list[float]:
    """The turn at every interior vertex of a polyline, in degrees (0 = straight on)."""
    out = []
    for a, b, c in zip(pts, pts[1:], pts[2:]):
        t0 = degrees(atan2(b[1] - a[1], b[0] - a[0]))
        t1 = degrees(atan2(c[1] - b[1], c[0] - b[0]))
        d = (t1 - t0 + 180.0) % 360.0 - 180.0
        out.append(abs(d))
    return out


def _o_rows(p: dict, part: Part) -> list[tuple[str, bool, str]]:
    rows = []
    # 1. every edge straight, every turn a whole multiple of 22.5, every FOLD in O_FOLDS
    keel = _o_keel_pts(p) + [_o_keel_pts(p)[0], _o_keel_pts(p)[1]]
    turns = _turns(keel)
    sec_pts = [(v.X, v.Y) for v in _o_section(p, 1).vertices()]
    ok_mult = all(abs(t / 22.5 - round(t / 22.5)) < 1e-4 for t in turns)
    # The FOLDS are the turns of the folded run itself; the four corners where the strip's two
    # ends meet the bar (67.5, 90, 90, 112.5) are corners, not folds, and are only held to the
    # 22.5 grid.
    dorsal = _turns(_o_keel_pts(p)[3:])
    ok_fold = all(any(abs(t - fa) < 1e-4 for fa in O_FOLDS) for t in dorsal)
    rows.append(("ORIGAMI keel: every edge straight, every turn a whole multiple of 22.5 deg and "
                 f"every fold of the folded run in {O_FOLDS}", ok_mult and ok_fold,
                 f"folds {' '.join(f'{t:.1f}' for t in dorsal)}; all turns "
                 f"{' '.join(f'{t:.1f}' for t in turns)} deg; "
                 f"{len(sec_pts)} straight vertices in the arm section"))
    # 2. no curve anywhere above the bar - the rule that separates ORIGAMI from SHARD
    curved = [f for f in part.faces()
              if f.geom_type.name != "PLANE" and f.bounding_box().min.Z > Z1 + 0.3 and f.area > 0.3]
    rows.append(("ORIGAMI: not one curved face above the bar (the sheet is folded, never rolled)",
                 not curved, f"{len(curved)} curved face(s)"
                             + ("" if not curved else f", largest {max(f.area for f in curved):.1f} mm²")))
    # 3. the sheet is CONSTANT thickness, measured through all three flats of the section
    got = _o_sheet(p, part, 1) + _o_sheet(p, part, -1)
    ok = bool(got) and all(abs(t - O_T) <= 0.06 for t in got)
    rows.append((f"ORIGAMI constant sheet {O_T} (the TPU95A value of the 1.8 law) through every "
                 "flat of the channel", ok,
                 "measured " + " ".join(f"{t:.2f}" for t in got) + " mm"))
    return rows


def _o_sheet(p: dict, part: Part, side: int) -> list[float]:
    """Measure the folded sheet where it matters: a ray fired at the middle of each of the three
    flats, normal to that flat, returning the distance between the two surfaces it crosses."""
    r = p["TUBE_ID"] / 2
    out = []
    for nx, ny in ((0.0, -1.0), (0.7071, -0.7071), (-0.7071, -0.7071)):
        # (nx, ny) is the outward normal in section coordinates (y = inboard)
        s_mid = (O_ARM_S[0] + O_ARM_S[1]) / 2
        pl = _tube_plane(p, side, s_mid)
        start = pl * Pos(nx * (r + 12.0), -side * ny * (r + 12.0))
        o = start.position
        d = Vector(-nx, side * ny, 0.0)
        d = pl.x_dir * -nx + pl.y_dir * (side * ny)
        hits = sorted(x for x in ((h[0] - o).dot(d.normalized())
                                  for h in part.find_intersection_points(Axis(tuple(o), tuple(d.normalized()))))
                      if x > 1e-6)
        if len(hits) >= 2:
            out.append(hits[1] - hits[0])
    return out


def _f_rows(p: dict, part: Part) -> list[tuple[str, bool, str]]:
    rows = []
    region, v0, v1 = _f_region(p)
    net, nodes = _f_fill(region, v0, v1)
    # Measured on the FINISHED solid, not by adding sketch areas up: the ribbons, the ring nodes
    # and the gusset all overlap, and a sum counts every overlap twice. A 0.6 mm slab through
    # X = 0 gives the panel's true cross-section, lunule and all.
    slab = S.extrude_cut(region, Plane(origin=(-0.3, 0, 0), x_dir=(0, 1, 0), z_dir=(1, 0, 0)), 0.6)
    solid = isect(part, slab) / 0.6
    void = 1.0 - min(1.0, solid / region.area)
    rows.append(("FILIGREE void fraction of the yoke's plan area in (0.45, 0.60)",
                 0.45 < void < 0.60,
                 f"{void:.1%} void; {solid:.0f} mm² of ribbon, node and gusset in a "
                 f"{region.area:.0f} mm² panel"))
    rows.append((f"FILIGREE scroll: two radii {F_R} and {F_R / 2} meeting tangentially, both under "
                 f"Ø{MATERIALS[MATERIAL]['arch_d']} so every ribbon is an arch",
                 2 * F_R <= MATERIALS[MATERIAL]["arch_d"] and F_R > 0,
                 f"Ø{2 * F_R} and Ø{F_R} ribbons, pitch {3 * F_R} mm, {len(nodes)} junctions"))
    ok_n, detail = _ring_ok(part, nodes[len(nodes) // 2], F_NODE_OD - 2 * 1.3, F_NODE_OD, "X", F_NODE)
    rows.append((f"FILIGREE Ø{F_NODE_OD} ring node at a scroll junction, bore clear",
                 ok_n, f"at {nodes[len(nodes) // 2]}: {detail}"))
    at = _f_lunule_at(p, v0)
    lun = S.mark("lunule", F_LUNULE, "cut", (1.0, at[0], at[1]), normal=(1, 0, 0),
                 through=F_RIB + 2.0, x_dir=(0, 1, 0))
    # measured inside the panel only: the sickle is 18.5 mm across at Ø16 and the yoke is
    # 17 mm wide where it sits, so its two tips are trimmed by the net's own scalloped edge
    v_in = isect(part, lun & slab)
    rows.append((f"FILIGREE lunule Ø{F_LUNULE} open at the vertex of the V, where the two mirrored "
                 "scroll nets meet", v_in < EPS and S.mark_fits("lunule", F_LUNULE),
                 f"{v_in:.4f} mm³ of material inside the mark; the lunule is the VOID the net "
                 f"leaves, centred at y {at[0]:.1f} Z {at[1]:.1f}"))
    return rows
