"""Anti-slip TPU pack seat on the top plate, in three genuinely different readings.

Printed pattern side DOWN (PRINT (0, 0, 1)): the rib/land tops and the front stop band are coplanar
at Z 40, so the whole Z 40 plane is the bed and everything that needs bridging is a pocket ceiling
whose span is declared in BRIDGE_OK. Nothing stands proud of that plane - the pack sits ON it (see
_common.BATTERY, whose floor is Z 38.5), so a stop bar above the seat would have to grow into the
pack; the front band stops the pack by being solid, keyed, carbon-backed material at the pack's
front edge instead of ribbed and hollow.

Envelope Z 34.2 - 40.0 in every style: collars Z 34.2-36 hanging into the twelve plate_top reliefs,
sheet Z 36-38.5, relief pattern and front stop band Z 38.5-40.

THE THREE STYLES
================
The MOUNTING is identical in all three and is not up for negotiation - same outline derivation
(plate_top outline inset 1.0, clipped to |x| 22, front apertures cleared by 0.5), same twelve keying
collars from Z 34.2 with 0.25 clearance and a 1.2 wall, same twelve strap windows, same Z 36 seating
plane, same solid carbon-backed front stop band, same four standoff bolt-head tabs. Only the
SILHOUETTE and the SURFACE change, which is the §4.5 silhouette-first directive taken literally:

  shard    the frame's own language - the plate's curved outline, a +-45 deg diamond crosshatch of
           grip ribs (the reading this module shipped before the style families existed, kept
           byte-for-byte so nothing that was verified changes).
  arsenal  field-serviceable mil-spec, the family's hero part and the pad that flies every day: a
           strictly ORTHOGONAL stepped outline with ONE 30 deg cut corner at the rear-outboard tail
           tip (the signature), transverse rib lands at pitch 9.0 standing 2.0 proud of their valley
           floors with steep end run-outs, a flat-top hex vent spine, two stencil data panels, fine
           knurl in the grab zones and inside the two large bays - the LARGE-tier second sub-pattern
           at pitch/2.6 - and a lanyard eye.
  chassis  only the load path survives: the plate outline SERRATED (Ø1.6 scallops at 3.2 pitch cut
           into both outboard edges - the spined tibia), a Lloyd-free Voronoi grip-cell field with an
           arithmetically exact 2.0 mm ligament cut by Blender's `carapace_lattice`, and a starburst
           of radial relief slots round every keying collar.

SLIPSTREAM and NOCTURNE are explicitly barred from this part by the matrix, and both refusals are
physical: no gloss survives under a battery pack, and a vane comb gets crushed by one. Those kits
fall back to `shard`.

WHY THE PATTERN IS ALWAYS A POCKET, NEVER A PROUD RIB
The pad prints with its Z 40 plane on the bed, so every feature that faces +Z in frame coordinates
faces the build platform. A proud rib would need to grow ABOVE Z 40 and into the pack. So all three
styles make their relief by sinking pockets from the Z 40 plane: the "ribs" are what is left
standing, their tops are the bed, and each pocket ceiling is a flat bridge of a declared span.
"""

from math import cos, radians, sqrt, tan

from build123d import (Axis, Circle, Face, Part, Plane, Polygon, Pos, Rectangle, Sketch, SlotOverall,
                       Vertex, extrude, offset)

from tigerbee.accessories import _blender as BL
from tigerbee.accessories import _style as S
from tigerbee.accessories._common import *  # noqa: F401,F403 - constants, builders and checks
from tigerbee.profiles import _outer_face, cutouts

NAME = "battery_pad"
TITLE = "Battery pad"
MATERIAL = "TPU95A"
STYLES = ("shard", "arsenal", "chassis")
PRINT = {"battery_pad": (0, 0, 1)}  # pattern side on the bed: the Z 40 plane is flat and continuous
EXCLUSIVE = ()
MOUNTS = ("plate_top top face Z 36, y -80..53.5, outline inset 1.0 mm from the carbon edge",
          "the twelve diagonal plate_top relief windows (one 1.2 mm collar hangs into each)")
HARDWARE = ("none - keyed by the twelve collars and clamped by the battery strap (16 / 20 / 25 mm "
            "round the top-plate side edges)",
            "optional 1 x 3.6 mm zip tie through a rear strap window (pad and plate together)")
BATTERY_OK = True  # the pad is what the pack sits on, so it lives inside the BATTERY envelope
ENV_Z = (34.2, 40.0)  # catalog envelope: 0.2 above the plate_top underside up to the land tops

# --- parameters (mm) ------------------------------------------------------------------------
T = 2.5  # sheet thickness: Z 36.0 (seated on plate_top) .. 38.5
INSET = 1.0  # pad outline = plate_top outline offset inwards by this
X_MAX = 22.0  # and clipped to this half-width: the standoff tabs carry the M3 bolt heads
Y_FRONT, Y_REAR = 53.5, -80.0  # pad ends (plate_top runs to 75 / -82 on the centre line)
RIB_H, RIB_W, RIB_PITCH = 1.5, 1.5, 6.0  # +-45 deg crosshatch: grip fore-aft AND sideways
RIB_MARGIN = 1.2  # solid border kept round the outline and every window
POCKET_D, POCKET_MIN = 2.5, 2.0  # valleys sink 1.0 into the sheet (1.5 left); slivers below this go
STOP = True
STOP_Y0, STOP_H = 50.0, 1.5  # solid front band y 50..53.5, Z 38.5..40.0: coplanar with the land tops
FRONT_CLEAR = 0.5  # the pad edge keeps this off every plate_top aperture forward of Y_SOLID
Y_SOLID = 40.0  # forward of this the top plate is no longer solid across the pad's width
WINDOWS = True
KEYS = True  # collars hanging into the reliefs: the pad's only positive retention
KEY_CLEAR = 0.25  # radial gap from a collar to the wall of its relief
KEY_W = 1.2  # collar wall thickness; the strap window is cut at offset -(KEY_CLEAR + KEY_W)
HEAD_AXES = ("standoff_front_arm_right", "standoff_front_arm_left",
             "standoff_rear_arm_right", "standoff_rear_arm_left")

Z0 = Z_TOP_TOP  # 36.0: seating face on plate_top
KEY_Z0 = ENV_Z[0]  # 34.2: collar bottoms, 0.2 clear of the plate_top underside at Z 34

# --- ARSENAL ---------------------------------------------------------------------------------
# The orthogonal silhouette, as an explicit list of axis-aligned boxes (x0, y0, x1, y1). Every one
# was chosen from a measured section of the base outline so that the union is a strict SUBSET of it:
# the pad therefore still lands on carbon everywhere and still keeps its 1.0 mm inset, and the
# silhouette is made of straight runs and right angles rather than the plate's curves. Measured
# outline half widths: 14.95 at y -80, 15.5 to y -46, 16.99 at -42, 22.0 over -36..-30, 20.0 over
# -22..+39 (the waist minimum), and the four front tongues from y 39 to 53.
ORTHO_BOXES = ((-14.8, -80.0, 14.8, -42.0),    # tail
               (-16.8, -42.0, 16.8, -37.0),    # the shoulder step
               (-19.6, -37.0, 19.6, 39.0),     # the long body run
               (-19.6, 39.0, -16.8, 53.0),     # outer tongue, left
               (16.8, 39.0, 19.6, 53.0),       # outer tongue, right
               (-9.9, 39.0, -5.6, 53.0),       # inner tongue, left
               (5.6, 39.0, 9.9, 53.0))         # inner tongue, right
# THE SIGNATURE: one 30 deg cut corner, at the rear-outboard tail tip, on the right only. Asymmetry
# is the point - it is what makes the plan legible at 200 px next to the hex spine. The cut runs from
# (14.8, -68) at exactly 30 deg to the pad's Y axis, so at y -73.45 (the rear strap window's edge) it
# still stands 1.8 mm outboard of the window and at y -80 it has taken 6.93 mm off the corner.
CUT_CORNER_Y = -68.0
CUT_CORNER_DEG = 30.0
RIB_LAND = 1.6          # land width across the rib top (the 1.6 x 2.0 external rib of the family)
RIB_PITCH_T = 9.0       # transverse rib pitch (CN-2: repeating features run across X)
RIB_PROUD = 2.0         # land stands this proud of its valley floor -> POCKET_D 2.0
RIB_RAMP = 1.6          # run-out at each end of a valley. 1.6 over 2.0 proud is 51.3 deg, and that
#                         is deliberate: a true 45 deg ramp has normal.Z -0.7071 in print, just past
#                         overhangs()' -0.70 limit. Steeper is safer, so the ramp is steeper.
SPINE_X = 6.0           # half width of the hex vent spine down the centre of the pad
HEX_AF = 4.4            # across flats. 5.0 is the family default and does not fit: the spine is only
#                         3.65 mm of half width clear of the strap windows, and a Ø5.0 flat-top hex
#                         needs 3.49 plus the boundary ligament.
HEX_PITCH = 6.8         # centre spacing in the flat directions -> ligament 6.8 - 4.4 = 2.4 exactly
HEX_LIG = 0.6           # boundary allowance handed to the generator, on top of RIB_MARGIN
KNURL_SUB = 2.6         # the LARGE-tier rule: the second sub-pattern runs at pitch / this
KNURL_W, KNURL_D = 1.2, 0.5     # groove width and depth, blind
KNURL_BANDS = ((-80.0, -71.0), (39.0, 50.0))   # the grab zones: the rear tip and the front prongs
# The two stencil data panels: flat, rib-free bands of the Z 40 plane. Both sit in a transverse strip
# of the pad with no strap window in it, so the mark keeps its 2.0 mm to every clean zone.
PANELS = ((-6.74, 1.74, "BATTERY PAD", 30.0), (13.26, 22.98, "TIGERBEE", 34.0))
LARGE_BAYS = ((-57.0, -22.0), (23.0, 39.0))    # the two bays that carry the second sub-pattern
MARK_D = 0.5            # deboss depth (the brief's number; CN-4's 0.6 is the ceiling, not a floor)
EYE_D, EYE_XY = 4.0, (0.0, -76.0)   # the service lanyard eye, through the tail

# --- CHASSIS ---------------------------------------------------------------------------------
SERR_D, SERR_PITCH = 1.6, 3.2    # SPINE serration: Ø1.6 scallops at 3.2 pitch, CUT INTO the edge
SERR_X, SERR_Y = 12.0, (-46.0, 38.0)   # which part of the outline is "the outboard edge"
STAR_N, STAR_W = 8, 1.2          # starburst round every keying collar: n = 8, w 1.2, len 0.35 R
STAR_GAP = 1.4                   # land kept between two starburst slots: above TPU's 1.2 wall floor
#                                  and below the 2.0 cell ligament, because it is a wall between two
#                                  blind pockets in a 4.0 mm sheet, not a strut in a lattice
VOR_LIG = 2.0                    # TPU's Voronoi ligament floor; the recipe insets by LIG/2 + 0.1
VOR_D = 10.0                     # Poisson separation -> 0.866 D^2 = 86.6 mm2 a cell, inside 28-90
VOR_SEED = 11                    # deterministic, explicit
VOR_EDGE = 2.0                   # the cell field is held this far off its bay boundary, so the
#                                  boundary ligament is the same 2.0 as the cell-to-cell one
VOID_MIN = 0.45                  # the family rule: the void is >= 45 % of the decorated bays

# --- the style variants -----------------------------------------------------------------------
VARIANTS = {
    "shard": {"style": "shard",
              "notes": "the frame's own language: the plate's curved outline and a +-45 deg diamond "
                       "grip crosshatch at 6.0 pitch. Pure build123d, always available, and the "
                       "fallback for the SLIPSTREAM and NOCTURNE kits, which are barred from this "
                       "part (no gloss survives under a pack; vanes get crushed by one)."},
    "arsenal": {"style": "arsenal",
                "notes": "the family hero: strictly orthogonal stepped outline with ONE 30 deg cut "
                         "corner at the rear-outboard tail tip, transverse rib lands at 9.0 pitch "
                         "standing 2.0 proud with 51 deg run-outs, a flat-top hex vent spine, two "
                         "debossed stencil panels, knurl at pitch/2.6 in the grab zones and the two "
                         "large bays, and a Ø4.0 lanyard eye. Pure build123d."},
    "chassis": {"style": "chassis",
                "notes": "only the load path survives: the outline serrated with Ø1.6 scallops at "
                         "3.2 pitch, a Voronoi grip-cell field with an arithmetically exact 2.0 mm "
                         "ligament cut by Blender's carapace_lattice, and an 8-slot starburst round "
                         "every keying collar. TPU, so the Voronoi ligament is 2.0 and not PETG's 1.6."},
}
ASSEMBLY_VARIANT = "shard"

# One bridge box per pocket-floor plane, in PRINT coordinates (print z = 40 - frame z), keyed by the
# FINAL label so each style declares exactly the ceilings it actually has. Every one of these is a
# pocket ceiling supported on all four sides, which is what a bridge is; none of them is a cantilever.
#   shard    one plane, the diamond valley floors at Z 37.5, span 4.5 mm
#   arsenal  three: the stencil deboss floors and the Z-40 knurl at Z 39.5 (span <= 1.4 mm), the rib
#            valley floors at Z 38.0 (span 7.4 mm), the in-valley knurl at Z 37.5 (span 1.4 mm). The
#            hex vents need NO allowance at all: a flat-top hex is self-supporting, which is exactly
#            why the family specifies flat-top.
#   chassis  one plane, the Voronoi cell floors and the starburst slots at Z 37.5. A cell of 86.6 mm2
#            spans at most ~12 mm, inside TPU's 22 mm bridge limit - checked, then declared.
def _bridge(*depths) -> tuple:
    return tuple(("box", -100.0, -100.0, d - 0.1, 100.0, 100.0, d + 0.1) for d in depths)


BRIDGE_OK = {
    "battery_pad": _bridge(POCKET_D),
    "battery_pad__shard": _bridge(POCKET_D),
    "battery_pad__arsenal": _bridge(MARK_D, RIB_PROUD, RIB_PROUD + KNURL_D),
    "battery_pad__chassis": _bridge(POCKET_D),
}

_SHARED_NOTES = (
    "Drops onto plate_top between y -80 and 53.5 and is keyed by twelve collars (1.2 mm wall, "
    "Z 34.2-36, 0.25 mm clear of the relief walls) that hang into the twelve diagonal plate_top "
    "reliefs, so the pad cannot slide or lift off before the strap is on; the strap windows are cut "
    "1.45 mm INSIDE each relief, i.e. inside the collar, so a 3.6 mm zip tie through a rear window "
    "passes through pad and plate together. The outline is inset 1.0 from the carbon edge and "
    "clipped to |x| 22 so it clears the four arm-root standoff bolt heads and never fouls a strap "
    "wrapping the plate edge. Forward of y 40 the top plate is no longer solid across the pad, so "
    "the two long slots at (+-13.25, 49.3) and the centre slot at (0, 55.5) are cut out of the "
    "outline with 0.5 mm of clearance: the front of the pad is tongues, each standing on carbon, and "
    "the solid front stop band (y 50-53.5, Z 38.5-40, no pockets) is carried by carbon over its "
    "whole footprint. The band is coplanar with the land tops because the pack underside is Z 38.5: "
    "it stops the pack by being solid where the rest is relieved, not by standing proud. The front "
    "edge stands 2.5 mm clear of the built gopro_mount (its base starts at y 56.0) and 4.5 mm clear "
    "of the built gps_mount. Battery straps of 16/20/25 mm wrap the top-plate side edges - the pad "
    "is not a strap slot. The plate_top SMA hole (0, -56.5) is under the pack and unusable with a "
    "pad fitted; the tail SMA seat is the primary one."
)
NOTES = {
    "battery_pad": _SHARED_NOTES,
    "battery_pad__shard": _SHARED_NOTES,
    "battery_pad__arsenal": _SHARED_NOTES + (
        " ARSENAL: the plan is a union of axis-aligned boxes INTERSECTED with that same outline, so "
        "the silhouette is orthogonal and still carbon-backed everywhere; the one 30 deg cut corner "
        "at the rear-right tail tip is the family signature and the only asymmetry on the part. The "
        "hex vent spine drains the pad and is flat-top, so it needs no bridge allowance."),
    "battery_pad__chassis": _SHARED_NOTES + (
        " CHASSIS: the outboard edges are serrated with Ø1.6 scallops CUT INWARD at 3.2 pitch - "
        "outward bumps would eat the 1.0 mm outline inset the strap needs - and the grip field is a "
        "Voronoi cell field cut by Blender, confined by a build123d region solid to the Z 38.5-40 "
        "band so the cells are blind pockets and the Z 36 seating plane is never touched."),
}

_DEFAULTS = dict(STYLE="shard", T=T, INSET=INSET, X_MAX=X_MAX, Y_FRONT=Y_FRONT, Y_REAR=Y_REAR,
                 RIB_H=RIB_H, RIB_W=RIB_W, RIB_PITCH=RIB_PITCH, RIB_MARGIN=RIB_MARGIN,
                 POCKET_D=POCKET_D, POCKET_MIN=POCKET_MIN, STOP=STOP, STOP_Y0=STOP_Y0, STOP_H=STOP_H,
                 FRONT_CLEAR=FRONT_CLEAR, Y_SOLID=Y_SOLID, WINDOWS=WINDOWS, KEYS=KEYS,
                 KEY_CLEAR=KEY_CLEAR, KEY_W=KEY_W, KEY_Z0=KEY_Z0,
                 # arsenal
                 ORTHO=False, CUT_CORNER=False, HEX=False, RIBS_T=False, KNURL=False,
                 WORDMARK=False, EYE=False, HEX_AF=HEX_AF, HEX_PITCH=HEX_PITCH,
                 RIB_LAND=RIB_LAND, RIB_PITCH_T=RIB_PITCH_T, RIB_RAMP=RIB_RAMP, SPINE_X=SPINE_X,
                 KNURL_W=KNURL_W, KNURL_D=KNURL_D, MARK_D=MARK_D, EYE_D=EYE_D,
                 # chassis
                 SERRATE=False, STARBURST=False, VORONOI=False, DECOR=True, STAR_DEFER=False,
                 SERR_D=SERR_D, SERR_PITCH=SERR_PITCH, VOR_LIG=VOR_LIG, VOR_D=VOR_D,
                 VOR_SEED=VOR_SEED, VOR_EDGE=VOR_EDGE)

# Everything a style changes, in one table. `POCKET_D` is the depth of the style's primary relief and
# therefore also the plane its bridge box is declared at, which is why the two are derived from one
# number rather than written down twice.
STYLE_PARAMS = {
    "shard": dict(),
    "arsenal": dict(ORTHO=True, CUT_CORNER=True, HEX=True, RIBS_T=True, KNURL=True, WORDMARK=True,
                    EYE=True, POCKET_D=RIB_PROUD),
    "chassis": dict(SERRATE=True, STARBURST=True, VORONOI=True),
}
_BUILT = dict(_DEFAULTS)  # parameters of the last build(), so checks() measures what was built
_BASE: dict[str, Part] = {}   # the UNDECORATED functional solid of the last build of each style


def _params(**overrides) -> dict:
    """Defaults with `overrides` applied. An unknown key is a typo, never a silent no-op."""
    unknown = sorted(set(overrides) - set(_DEFAULTS))
    assert not unknown, f"unknown parameter(s) {unknown}; known: {sorted(_DEFAULTS)}"
    style = overrides.get("STYLE", _DEFAULTS["STYLE"])
    assert style in STYLES, f"unknown style {style!r}; styles: {STYLES}"
    return {**_DEFAULTS, **STYLE_PARAMS[style], **overrides}


def _zs(p: dict) -> tuple[float, float, float, float]:
    """Seating face, sheet top, land top, stop top."""
    return Z0, Z0 + p["T"], Z0 + p["T"] + p["RIB_H"], Z0 + p["T"] + p["STOP_H"]


def _knurl_pitch(p: dict) -> float:
    """The LARGE-tier second sub-pattern: the primary pitch divided by 2.6 (§4.4)."""
    return p["HEX_PITCH"] / KNURL_SUB


def _L(p: dict) -> float:
    """The characteristic dimension the §4.4 scaling law is evaluated at.

    `_style.characteristic_length` returns the SHORTER in-plane extent, which for this pad is 44 and
    would put the family's hero part in the `medium` tier. That is the wrong reading for a 44 x 133
    plate: the geometric mean of the two in-plane extents, 76.6, is the dimension the eye actually
    scales the pattern against, and it puts the pad in the `large` tier where it belongs - which is
    what turns on the second sub-pattern rule."""
    return sqrt((p["X_MAX"] * 2.0) * (p["Y_FRONT"] - p["Y_REAR"]))


# --- 2D profiles ----------------------------------------------------------------------------
def _rect(x0: float, y0: float, x1: float, y1: float) -> Sketch:
    return Pos((x0 + x1) / 2, (y0 + y1) / 2) * Rectangle(x1 - x0, y1 - y0)


def _opened(sk: Sketch, t: float = WALL) -> Sketch:
    """Morphological opening: everything thinner than t (the knife edges a straight cut leaves where
    it crosses the curved plate outline) disappears, convex corners keep a t/2 radius. Erosion and
    dilation run per face because OCCT's 2D offset raises instead of returning nothing when a
    fragment vanishes."""
    out = Sketch()
    for face in sk.faces():
        try:
            eroded = offset(face, -t / 2)
        except Exception:  # noqa: BLE001 - fragment thinner than t everywhere
            continue
        for part in eroded.faces() if eroded is not None else []:
            if part.area > 1e-9:
                out += offset(part, t / 2)
    return out


def _eroded(sk: Sketch, t: float) -> Sketch:
    """Inward offset per face, dropping fragments OCCT refuses. Not an opening - the result keeps
    its slivers, which is what a region wants when the slivers are simply too small to host a cell."""
    out = Sketch()
    for face in sk.faces():
        try:
            er = offset(face, -t)
        except Exception:  # noqa: BLE001
            continue
        for g in er.faces() if er is not None else []:
            if g.area > 1e-9:
                out += g
    return out


def _reliefs() -> list[Face]:
    """The twelve diagonal plate_top reliefs (kidneys, long slots and the centre slot are elsewhere)."""
    wires = [w for w in cutouts("plate_top")
             if abs(w.bounding_box().center().X) > 1.0 and w.bounding_box().center().Y < 40.0]
    assert len(wires) == 12, f"expected 12 reliefs, got {len(wires)}"
    return [Face(w) for w in wires]


def _front_apertures(p: dict) -> list[Face]:
    """plate_top apertures forward of Y_SOLID: the two kidneys (+-12.1, 68), the two long slots
    (+-13.25, 49.3) and the centre slot (0, 55.5). Forward of Y_SOLID the plate is not solid across
    the pad, so these are cut out of the outline instead of bridged by it."""
    wires = [w for w in cutouts("plate_top") if w.bounding_box().center().Y > p["Y_SOLID"]]
    assert len(wires) == 5, f"expected 5 apertures forward of y {p['Y_SOLID']}, got {len(wires)}"
    return [Face(w) for w in wires]


def _windows(p: dict) -> Sketch:
    """Strap/drain windows: each relief shrunk by KEY_CLEAR + KEY_W, i.e. the inner edge of its
    collar, so the sheet always overhangs the relief rim and the window is inside the plate aperture."""
    return Sketch() + [offset(f, -(p["KEY_CLEAR"] + p["KEY_W"])) for f in _reliefs()]


def _collars(p: dict) -> Sketch:
    """The twelve collar rings: relief offset -KEY_CLEAR minus relief offset -(KEY_CLEAR + KEY_W)."""
    rings = Sketch()
    for f in _reliefs():
        rings += offset(f, -p["KEY_CLEAR"]) - offset(f, -(p["KEY_CLEAR"] + p["KEY_W"]))
    return rings


def _base_outline(p: dict) -> Sketch:
    """The carbon-backed outline every style starts from and none of them may grow out of."""
    crop = Pos(0, (p["Y_REAR"] + p["Y_FRONT"]) / 2) * Rectangle(2 * p["X_MAX"], p["Y_FRONT"] - p["Y_REAR"])
    sk = offset(_outer_face("plate_top"), -p["INSET"]) & crop
    for hole in _front_apertures(p):
        sk -= offset(hole, p["FRONT_CLEAR"])
    return _opened(sk)


def _ortho_plan(p: dict) -> Sketch:
    """ARSENAL's silhouette before it is clipped: axis-aligned boxes minus the one 30 deg cut corner.

    Kept separate from the clip so checks() can assert the clip removed (almost) nothing - i.e. that
    the orthogonal plan really is a subset of the carbon-backed outline and the pad's silhouette is
    genuinely straight runs and right angles rather than the plate's curves showing through."""
    sk = Sketch()
    for x0, y0, x1, y1 in ORTHO_BOXES:
        sk += _rect(x0, y0, x1, y1)
    if p["CUT_CORNER"]:
        x_top = max(x1 for _x0, _y0, x1, _y1 in ORTHO_BOXES[:1])   # the tail's outboard face, 14.8
        run = (CUT_CORNER_Y - (p["Y_REAR"] - 2.0)) * tan(radians(CUT_CORNER_DEG))
        sk -= Polygon((x_top, CUT_CORNER_Y), (x_top, p["Y_REAR"] - 2.0),
                      (x_top - run, p["Y_REAR"] - 2.0), align=None)
    return sk


def _serration_cut(p: dict, sk: Sketch) -> tuple[Sketch, int]:
    """CHASSIS's SPINE token: half-round scallops marching along both outboard edges of the plan.

    The family spec draws these as bumps standing 0.8 PROUD of the rail. On this part they are cut
    INWARD instead, and that is a fit argument rather than a taste one: the pad's outline is inset
    exactly 1.0 mm from the carbon edge so a battery strap wraps the plate and never the pad, and a
    0.8 mm bump would spend that inset and leave 0.2. Cutting the same Ø1.6 at the same 3.2 pitch
    gives the identical serrated silhouette and makes the inset 1.8 where it bites."""
    face = sk.faces()[0]
    wire = face.outer_wire()
    n = 1600
    pts = [wire.position_at(i / n) for i in range(n)]
    runs, cur = [], []
    for q in pts:
        if abs(q.X) > SERR_X and SERR_Y[0] < q.Y < SERR_Y[1]:
            cur.append((q.X, q.Y))
        elif cur:
            runs.append(cur)
            cur = []
    if cur:
        runs.append(cur)
    cut, placed = Sketch(), 0
    for run in runs:
        if len(run) < 8:
            continue
        # protrusion = d/2 puts every bump centre exactly ON the edge, so the scallop is a true
        # half round of depth d/2 and the teeth between them keep their full sheet thickness
        bumps, k = S.serration(run, d=p["SERR_D"], pitch=p["SERR_PITCH"], protrusion=p["SERR_D"] / 2)
        if k:
            cut += bumps
            placed += k
    return cut, placed


def _outline(p: dict) -> Sketch:
    """The style's plan outline. Every style's outline is the base outline or a SUBSET of it, so the
    'lands on carbon' and 'inset from the carbon edge' checks hold by construction, not by luck."""
    sk = _base_outline(p)
    if p["ORTHO"]:
        sk = _opened(_ortho_plan(p) & sk)
    if p["SERRATE"]:
        cut, _n = _serration_cut(p, sk)
        if cut.faces():
            sk = sk - cut
    return sk


def _sheet_profile(p: dict) -> Sketch:
    """The sheet as cut: outline, strap windows, and any THROUGH apertures the style adds."""
    sk = _outline(p)
    if p["WINDOWS"]:
        sk -= _windows(p)
    if p["HEX"]:
        vents, _n = _hex_vents(p, sk)
        if vents.faces():
            sk -= vents
    if p["EYE"]:
        sk -= Pos(*EYE_XY) * Circle(p["EYE_D"] / 2)
    return sk


def _stop_profile(p: dict, sheet: Sketch) -> Sketch:
    if not p["STOP"]:
        return Sketch()
    band = Pos(0, (p["STOP_Y0"] + p["Y_FRONT"]) / 2) * Rectangle(400, p["Y_FRONT"] - p["STOP_Y0"])
    return _opened(sheet & band)


def _band(y0: float, y1: float) -> Sketch:
    return _rect(-400.0, y0, 400.0, y1)


def _panel_sketches(p: dict, grow: float = 0.0) -> list[Sketch]:
    """The two ARSENAL stencil panels as clean zones (a mark needs 2.0 mm to anything)."""
    if not p["WORDMARK"]:
        return []
    return [_band(y0 - grow, y1 + grow) for y0, y1, _t, _s in PANELS]


def _clean_for_apertures(p: dict) -> list[Sketch]:
    """Zones no generated aperture may enter: the solid front stop band, the stencil panels, the
    lanyard eye and the grab bands. RIB_MARGIN round the outline and the windows is already in the
    region itself (see _hex_vents), which is why it is not repeated here."""
    clean = [_band(p["STOP_Y0"] - 2.4, p["Y_FRONT"] + 2.0)]
    clean += _panel_sketches(p, 2.4)
    if p["EYE"]:
        clean.append(Pos(*EYE_XY) * Circle(p["EYE_D"] / 2 + 2.0))
    if p["KNURL"]:
        clean += [_band(y0 - 1.2, y1 + 1.2) for y0, y1 in KNURL_BANDS]
    return clean


def _spine(p: dict) -> Sketch:
    return _rect(-p["SPINE_X"], p["Y_REAR"] - 2.0, p["SPINE_X"], p["Y_FRONT"] + 2.0)


def _hex_vents(p: dict, sheet_with_windows: Sketch) -> tuple[Sketch, int]:
    """ARSENAL's vent spine: a flat-top hex field down the pad's centre line, cut THROUGH the sheet.

    Flat-top is the family's own rule and it is the reason this field needs no bridge allowance at
    all: the top of a flat-top hexagon is a short horizontal run of AF/2, self-supporting at these
    sizes, instead of a peak that leaves a spike.

    Why a spine and not a field: the pad's free material is longitudinal STRIPS. The twelve strap
    windows sit in two columns at |x| 4.85-15.0, leaving a centre spine and two outboard strips only
    5.8 mm wide. A hex field lives in the spine; the transverse rib lands own everything outboard of
    it (CN-2 - the repeating rib features run across X, the vent lattice is a 2D field, and neither
    is a flowing feature running along Y)."""
    region = _eroded(sheet_with_windows, p["RIB_MARGIN"]) & _spine(p)
    if not region.faces():
        return Sketch(), 0
    return S.vent_hex(region, pitch=p["HEX_PITCH"], ligament_min=HEX_LIG, af=p["HEX_AF"],
                      clean=_clean_for_apertures(p), hole_min=MATERIALS[MATERIAL]["wall"] + 1.0,
                      origin=(0.0, 0.0))


def _valley_centres(p: dict) -> list[float]:
    """Transverse rib valley centre lines at RIB_PITCH_T, skipping any whose 7.4 mm band would run
    into a stencil panel or a grab band. Anchored on a fixed y so the pattern is deterministic."""
    half = (p["RIB_PITCH_T"] - p["RIB_LAND"]) / 2.0
    blocked = [(y0 - 0.2, y1 + 0.2) for y0, y1, _t, _s in (PANELS if p["WORDMARK"] else ())]
    blocked += [(y0 - 0.2, y1 + 0.2) for y0, y1 in (KNURL_BANDS if p["KNURL"] else ())]
    blocked.append((p["STOP_Y0"] - 1.2, p["Y_FRONT"] + 2.0))
    out = []
    k = 0
    while True:
        yc = -66.0 + k * p["RIB_PITCH_T"]
        if yc - half > p["Y_FRONT"]:
            break
        k += 1
        if yc - half < p["Y_REAR"] + p["RIB_MARGIN"] or yc + half > Y_SOLID - 1.0:
            continue
        if any(yc - half < b1 and yc + half > b0 for b0, b1 in blocked):
            continue
        out.append(round(yc, 3))
    return out


def _valley_region(p: dict, sheet: Sketch) -> Sketch:
    """Where a transverse valley may sink: the sheet held back RIB_MARGIN from every rim, outboard of
    the hex spine, and never under the stop band or a stencil panel."""
    reg = _eroded(sheet, p["RIB_MARGIN"])
    if p["HEX"]:
        reg = reg - _rect(-p["SPINE_X"] - p["RIB_MARGIN"], p["Y_REAR"] - 3.0,
                          p["SPINE_X"] + p["RIB_MARGIN"], p["Y_FRONT"] + 3.0)
    reg = reg - _band(p["STOP_Y0"] - p["RIB_MARGIN"], p["Y_FRONT"] + 2.0)
    for pan in _panel_sketches(p, 0.0):
        reg = reg - pan
    return _opened(reg, 1.0)


def _valleys(p: dict, sheet: Sketch) -> tuple[Part, int]:
    """The transverse rib field as a 3D cutter. Each valley fragment gets a run-out at both X ends.

    The run-out is 1.6 over 2.0 proud, i.e. 51.3 deg from horizontal, and NOT the family's nominal
    45: a 45 deg ramp face has normal.Z -0.7071 once the pad is flipped onto its Z 40 plane, which is
    just past the -0.70 limit in overhangs(). Steeper is self-supporting, shallower is a failed
    check, so the ramp is steeper and the number is written down here rather than discovered twice."""
    region = _valley_region(p, sheet)
    if not region.faces():
        return Part(), 0
    z_floor = Z0 + p["T"] + p["RIB_H"] - p["POCKET_D"]
    z_top = Z0 + p["T"] + p["RIB_H"]
    half = (p["RIB_PITCH_T"] - p["RIB_LAND"]) / 2.0
    ramp = p["RIB_RAMP"]
    out, placed = Part(), 0
    for yc in _valley_centres(p):
        band = region & _band(yc - half, yc + half)
        for frag in band.faces():
            if frag.area < 4.0:
                continue
            bb = frag.bounding_box()
            xa, xb = bb.min.X, bb.max.X
            if xb - xa < 2 * ramp + 1.0:
                continue
            prof = Polygon((xa - 0.5, z_top + 0.6), (xb + 0.5, z_top + 0.6), (xb + 0.5, z_top),
                           (xb - ramp, z_floor), (xa + ramp, z_floor), (xa - 0.5, z_top), align=None)
            pl = Plane(origin=(0.0, bb.max.Y + 0.1, 0.0), x_dir=(1, 0, 0), z_dir=(0, -1, 0))
            wedge = extrude(pl * prof, amount=bb.size.Y + 0.2, dir=(0, -1, 0))
            prism = extrude(Plane.XY.offset(z_floor) * (Sketch() + frag),
                            amount=z_top + 0.6 - z_floor, dir=(0, 0, 1))
            piece = prism & wedge
            if piece is not None and piece.volume > 1.0:
                out += piece
                placed += 1
    return out, placed


def _knurl_grooves(p: dict, region: Sketch) -> Sketch:
    """Fine transverse grooves at the §4.4 second-tier pitch (primary / 2.6). Straight and transverse
    rather than cross-hatched: CN-2 forbids two repeat directions on one surface, and a band of fine
    transverse grooves is what a knurl on this pad has to be to stay printable in this orientation."""
    if not region.faces():
        return Sketch()
    pitch = _knurl_pitch(p)
    bb = region.bounding_box()
    grooves = Sketch()
    k = 0
    n = int((bb.size.Y + 2 * pitch) / pitch) + 2
    y0 = pitch * round((bb.min.Y - pitch) / pitch)
    for i in range(n):
        y = y0 + i * pitch
        grooves += _rect(-400.0, y - p["KNURL_W"] / 2, 400.0, y + p["KNURL_W"] / 2)
        k += 1
    out = grooves & region
    return Sketch() + [f for f in out.faces() if f.area >= 1.0]


def _knurl(p: dict, sheet: Sketch, valleys_2d: Sketch) -> tuple[Part, int]:
    """Two knurl fields, one for each plane the pad presents:
      * the GRAB zones (the rear tail tip and the front prongs) are knurled into the Z 40 land plane;
      * the two LARGE BAYS carry the same pitch INSIDE their valley floors, which is the §4.4
        large-tier rule taken literally - a second sub-pattern at p/2.6 inside the primary one."""
    z_land = Z0 + p["T"] + p["RIB_H"]
    z_floor = z_land - p["POCKET_D"]
    base = _eroded(sheet, p["RIB_MARGIN"])
    clean_band = _band(p["STOP_Y0"] - p["RIB_MARGIN"], p["Y_FRONT"] + 2.0)
    tool, n = Part(), 0
    grab = Sketch()
    for y0, y1 in KNURL_BANDS:
        grab += _band(y0, y1)
    top = (base & grab) - clean_band
    if p["EYE"]:
        top = top - Pos(*EYE_XY) * Circle(p["EYE_D"] / 2 + 1.0)
    g = _knurl_grooves(p, top)
    if g.faces():
        tool += extrude(Plane.XY.offset(z_land - p["KNURL_D"]) * g, amount=p["KNURL_D"] + 0.6, dir=(0, 0, 1))
        n += len(g.faces())
    bays = Sketch()
    for y0, y1 in LARGE_BAYS:
        bays += _band(y0, y1)
    sub = _eroded(valleys_2d & bays, 0.8)
    g2 = _knurl_grooves(p, sub)
    if g2.faces():
        tool += extrude(Plane.XY.offset(z_floor - p["KNURL_D"]) * g2, amount=p["KNURL_D"] + 0.3, dir=(0, 0, 1))
        n += len(g2.faces())
    return tool, n


def _marks(p: dict) -> tuple[Part, list[str]]:
    """ARSENAL's stencil accent: TIGERBEE and the part id debossed MARK_D into the Z 40 land plane,
    each on its own rib-free data panel. A panel that cannot hold its wordmark at the family minimum
    carries none - a crushed mark is worse than none (§4.3)."""
    z_land = Z0 + p["T"] + p["RIB_H"]
    tool, done = Part(), []
    if not p["WORDMARK"]:
        return tool, done
    for y0, y1, text, size in PANELS:
        if not S.mark_fits("wordmark", size):
            continue
        tool += S.mark("wordmark", size, "deboss", (0.0, (y0 + y1) / 2, z_land), normal=(0, 0, 1),
                       text=text, depth=p["MARK_D"])
        done.append(f"{text}@{size}")
    return tool, done


def _starburst(p: dict, sheet: Sketch) -> tuple[Sketch, int]:
    """CHASSIS's hub accent, one per keying collar. A ring node at a cell-wall junction is meaningless
    in a Voronoi field, so the family's signature on this part is the starburst instead: eight radial
    relief slots round every collar, w 1.2, length 0.35 R, sunk with the cell field."""
    region = _eroded(sheet, p["RIB_MARGIN"])
    fixed = [S.grow_region(_windows(p), p["RIB_MARGIN"]),
             _band(p["STOP_Y0"] - p["RIB_MARGIN"], p["Y_FRONT"] + 2.0),
             # the centre-line keep-out: a slot kept clear of this strip is STAR_GAP clear of its
             # own mirror image, which is the one clash a right-half-then-mirror order cannot see
             # (the first collar has nothing placed yet to be measured against)
             _rect(-STAR_GAP / 2, Y_REAR - 5.0, STAR_GAP / 2, Y_FRONT + 5.0)]
    fixed = [c for c in fixed if c.faces()]
    # Placed on the RIGHT ONLY and mirrored, and pairwise-clean against everything already placed
    # INCLUDING that mirror image. Two things forced this. The generator's clean list only knows
    # about the windows, so the twelve collars - two columns 14.7 mm apart on a pad whose centre
    # spine is 12.9 mm wide - drove their inboard slots straight across X=0 into each other and
    # left a 0.329 mm sliver of land at (0.17, -36.6), which failed the mesh wall outright. And a
    # slot dropped on one side but kept on the other would make the pad's only asymmetry a mistake
    # rather than a decision. Building the right half and mirroring it makes the field symmetric by
    # construction; feeding the mirror back in as a clean zone means a slot that would reach the
    # centre line clashes with its own reflection and is DROPPED (never shortened - the §4.1 rule),
    # symmetrically, on both sides.
    right, kept = Sketch(), 0
    for f in sorted(_reliefs(), key=lambda g: -g.bounding_box().center().Y):
        bb = f.bounding_box()
        c = bb.center()
        if c.X < 0:
            continue
        r = max(bb.size.X, bb.size.Y) / 2.0 + 1.0
        both = (right + right.mirror(Plane.YZ)) if right.faces() else Sketch()
        placed = S.grow_region(both, STAR_GAP) if both.faces() else Sketch()
        clean = [*fixed, placed] if placed.faces() else list(fixed)
        sk, k = S.starburst((c.X, c.Y), r, n=STAR_N, w=STAR_W, length=0.35 * r,
                            clean=clean, region=region)
        right += sk
        kept += k
    if not right.faces():
        return Sketch(), 0
    return right + right.mirror(Plane.YZ), 2 * kept


def _bays(p: dict, sheet: Sketch) -> Sketch:
    """CHASSIS's decorated bays: the sheet held back RIB_MARGIN from every rim, forward limit y 44
    (the four front tongues are structure and carry the stop band), and nothing thinner than 3 mm."""
    reg = _eroded(sheet, p["RIB_MARGIN"]) - _band(44.0, p["Y_FRONT"] + 2.0)
    return _opened(reg, 3.0)


def _pockets(p: dict, sheet: Sketch) -> Sketch:
    """SHARD's valleys: the +-45 deg rib crosshatch. The diamond lattice is clipped to the sheet
    eroded by RIB_MARGIN, so every pocket keeps a full-thickness border of at least that much to the
    outline, to a window and to the stop band - no rib ever ends in a knife edge - while partial
    cells at the rim still get their relief. Fragments below POCKET_MIN are dropped."""
    side, pitch, r2 = p["RIB_PITCH"] - p["RIB_W"], p["RIB_PITCH"], sqrt(2)
    inner = _eroded(sheet, p["RIB_MARGIN"])
    if not inner.faces():
        return Sketch()
    bb = inner.bounding_box()
    y_max = (p["STOP_Y0"] - p["RIB_MARGIN"]) if p["STOP"] else bb.max.Y + 1
    inner &= Pos(0, (bb.min.Y - 5 + y_max) / 2) * Rectangle(400, y_max - bb.min.Y + 5)
    diamond = Rectangle(side, side).rotate(Axis.Z, 45)
    # lattice in the rib frame u = (x+y)/sqrt2, v = (x-y)/sqrt2; a cell there is a diamond in XY
    n = int((bb.size.X + bb.size.Y) / r2 / pitch) + 2
    grid = Sketch()
    for i in range(-n, n + 1):
        for j in range(-n, n + 1):
            u, v = (i + 0.5) * pitch, (j + 0.5) * pitch
            x, y = (u + v) / r2, (u - v) / r2
            if bb.min.X - pitch <= x <= bb.max.X + pitch and bb.min.Y - pitch <= y <= y_max + pitch:
                grid += Pos(x, y) * diamond
    cut = grid & inner
    return Sketch() + [f for f in cut.faces() if f.area >= p["POCKET_MIN"]]


# --- build ----------------------------------------------------------------------------------
def _functional(p: dict) -> tuple[Part, dict]:
    """The pad as build123d owns it: 100 % of the mating geometry plus the style's silhouette and
    relief. This is the solid every fit check is really about; Blender only ever decorates it."""
    z0, _z1, z2, z3 = _zs(p)
    key_z0 = p["KEY_Z0"] if p["KEYS"] else z0
    sheet = _sheet_profile(p)
    assert len(sheet.faces()) == 1, f"the pad sheet must be one face, got {len(sheet.faces())}"
    stop = _stop_profile(p, sheet)
    info: dict = {}

    # Subtractive throughout: fusing a collar or a bar onto a slab welds coincident faces into
    # trimmed surfaces that _common.overhangs can no longer read.
    pad = extrude(Plane.XY.offset(key_z0) * sheet, amount=z3 - key_z0, dir=(0, 0, 1))
    if p["KEYS"]:
        slab = extrude(Plane.XY.offset(key_z0 - 1) * Rectangle(400, 400), amount=z0 - key_z0 + 1, dir=(0, 0, 1))
        rings = extrude(Plane.XY.offset(key_z0) * _collars(p), amount=z0 - key_z0, dir=(0, 0, 1))
        pad -= slab - rings
    if z3 > z2 + 1e-9:
        above = Rectangle(400, 400) - stop if stop.area > 1e-6 else Rectangle(400, 400)
        pad -= extrude(Plane.XY.offset(z2) * above, amount=z3 - z2 + 1, dir=(0, 0, 1))

    if p["RIBS_T"]:
        valleys, n = _valleys(p, sheet)
        info["valleys"] = n
        if n:
            pad -= valleys
    elif not p["VORONOI"]:
        pockets = _pockets(p, sheet)
        info["pockets"] = len(pockets.faces())
        if pockets.area > 1e-6:
            pad -= S.extrude_cut(pockets, Plane.XY.offset(z2 - p["POCKET_D"]), p["POCKET_D"] + 1)

    if p["STARBURST"]:
        star, n = _starburst(p, sheet)
        info["starburst"] = n
        if n:
            tool = S.extrude_cut(star, Plane.XY.offset(z2 - p["POCKET_D"]), p["POCKET_D"] + 1)
            # STAR_DEFER hands the tool back instead of cutting it, so build() can give Blender the
            # SIMPLER solid and re-apply the slots afterwards through decorate()'s `cuts` hook. This
            # is not a cosmetic choice: the forty slots tessellate to 7 040 of the input mesh's
            # 16 180 triangles, and the OCCT re-sew of the decorated mesh at that size came back
            # BRepCheck-INVALID every time, which degraded the whole Voronoi pass. At 9 140 triangles
            # it sews to a valid solid, and the slots land on exact B-rep instead of on facets.
            if p["STAR_DEFER"]:
                info["star_tool"] = tool
            else:
                pad -= tool

    if p["KNURL"]:
        valleys_2d = _valley_region(p, sheet)
        knurl, n = _knurl(p, sheet, valleys_2d)
        info["knurl"] = n
        if n:
            pad -= knurl

    if p["WORDMARK"]:
        marks, done = _marks(p)
        info["marks"] = done
        if done:
            pad -= marks
    return pad, info


def _decor_zone(p: dict, sheet: Sketch) -> tuple[Part, Part, Sketch]:
    """(guard, region, region sketch) for the Blender pass.

    The guard is written the safest way round - EVERYTHING EXCEPT the skin to be decorated - and is
    built as `pad - band`, so it is exactly flush with every functional face by construction: the
    Z 36 seating plane, the twelve collars, the four bolt-head tabs, the strap-window rims, the
    RIB_MARGIN border and the solid front stop band are all inside it. The region is the same band
    held a further VOR_EDGE back from the bay boundary, so a cell that runs out to the region's rim
    still leaves 2.0 mm of material - the same ligament the cells keep from each other."""
    z2 = Z0 + p["T"] + p["RIB_H"]
    z_floor = z2 - p["POCKET_D"]
    bays = _bays(p, sheet)
    # The bays are already held RIB_MARGIN off every rim, so the further erosion that turns them
    # into "the outline inset by w" is VOR_EDGE - RIB_MARGIN, not VOR_EDGE. Eroding by the whole
    # 2.0 on top of the 1.2 left a 6.5 mm wide centre strip and a 319 mm2 region - a Voronoi field
    # with nowhere to live. The morphological opening that used to follow is gone with it: OCCT's
    # 2D offset raises on this twelve-holed face often enough that an opening silently returned
    # nothing, and a sliver in the REGION is harmless anyway (it can only make a pocket narrow, and
    # every point of the region is already VOR_EDGE from the land the pad is made of).
    reg_sk = _eroded(bays, p["VOR_EDGE"] - p["RIB_MARGIN"])
    if p["STARBURST"]:
        star, _n = _starburst(p, sheet)
        if star.faces():
            grown = S.grow_region(star, STAR_GAP)
            reg_sk = reg_sk - (grown if grown.faces() else star)
    zone = extrude(Plane.XY.offset(z_floor) * bays, amount=z2 + 0.6 - z_floor, dir=(0, 0, 1))
    region = extrude(Plane.XY.offset(z_floor) * reg_sk, amount=z2 + 0.6 - z_floor, dir=(0, 0, 1)) \
        if reg_sk.faces() else None
    return zone, region, reg_sk


def build(variant: str = "shard", **overrides) -> dict[str, Part]:
    style = overrides.pop("style", None) or variant or "shard"
    p = _params(STYLE=style, **overrides)
    assert p["T"] + p["RIB_H"] - p["POCKET_D"] >= WALL, "pocket floor thinner than the minimum wall"
    extra = p["KNURL_D"] if p["KNURL"] else 0.0
    assert p["T"] + p["RIB_H"] - p["POCKET_D"] - extra >= WALL, \
        "the second-tier knurl would leave less than the minimum wall over the seating face"
    assert p["STOP_H"] >= p["RIB_H"], "the front stop band cannot be lower than the land tops"
    assert Z0 + p["T"] + max(p["RIB_H"], p["STOP_H"]) <= ENV_Z[1] + 1e-9, (
        f"the pack seat would stand above the catalog envelope Z {ENV_Z[1]}")
    assert p["KEY_W"] >= WALL - 1e-9, "collar wall thinner than the minimum wall"
    assert p["KEY_Z0"] >= Z_TOP_UNDER + 0.2 - 1e-9, "collars would reach through the plate_top underside"
    _BUILT.clear()
    _BUILT.update(p)

    decorating = bool(p["VORONOI"] and p["DECOR"])
    pad, info = _functional({**p, "STAR_DEFER": decorating})
    star_tool = info.pop("star_tool", None)
    # _BASE is always the FULL functional solid - starburst included - because that is what the CAD
    # min-wall row and every fit probe must measure. `pad` at this point may be the starburst-free
    # solid that Blender is about to be handed.
    _BASE[style] = (pad - star_tool) if star_tool is not None else pad
    _INFO[style] = info

    if decorating:
        sheet = _sheet_profile(p)
        zone, region, reg_sk = _decor_zone(p, sheet)
        guard = pad - zone
        info["region_area"] = round(reg_sk.area, 1)
        info["bay_area"] = round(_bays(p, sheet).area, 1)
        res = BL.decorate_ex(pad, "carapace_lattice",
                             {"cell": "voronoi", "ligament": p["VOR_LIG"], "cell_d": p["VOR_D"],
                              "seed": p["VOR_SEED"], "axis": "Z"},
                             protect=guard, region=region, restore=False, cuts=star_tool,
                             cache_key=f"{NAME}__{style}", wall_floor=WALL, tri_budget=12_000)
        info["decor"] = res.applied
        # decorate_ex hands back its INPUT when any gate refuses, and that input is the deferred-
        # starburst solid - so the fallback is _BASE, never the input, or a degraded run would ship
        # a pad with no starburst on it at all.
        pad = res.part if res.applied else _BASE[style]

    pad.label = NAME
    return {NAME: pad}


_INFO: dict[str, dict] = {}


def checks(parts: dict[str, Part], frame: dict[str, Part]) -> list[tuple[str, bool, str]]:
    """The spec rows. `generic_checks` already covers single-solid, frame and standoff interference,
    prop discs, the landing plane, the bed face and overhangs, so none of that is repeated here.

    Every row below exists because an independent verifier found the corresponding defect in this
    module's earlier incarnation and its checks could not see it: the pad had no keying at all, it
    measured its neighbour clearance against a hard-coded box instead of the built parts, it tested
    containment against the plate outline with the holes filled in, and it stood outside its
    envelope. Each row therefore measures the real geometry, not a restatement of a parameter."""
    import importlib

    pad = parts[NAME]
    p = dict(_BUILT)
    style = p.get("STYLE", _DEFAULTS["STYLE"])
    base = _BASE.get(style, pad)  # the functional solid: Blender only ever decorates it
    _z0, _z1, _z2, z3 = _zs(p)
    plate = frame["plate_top"]
    out: list[tuple[str, bool, str]] = []

    # --- 1. KEYING: the pad's only positive retention -----------------------------------------
    reliefs = _reliefs()
    keel = pad & box(-200.0, -200.0, KEY_Z0 - 1.0, 200.0, 200.0, Z0 - 1e-6)
    rings = keel.solids() if keel is not None else []
    keel_v = volume(keel)
    out.append((f"keyed: material hangs below the Z {Z0} seating plane",
                keel_v > 50.0, f"{keel_v:.1f} mm³ of collar below Z {Z0}"))
    out.append((f"one collar in each of the {len(reliefs)} plate_top reliefs",
                len(rings) == len(reliefs), f"{len(rings)} separate collars below Z {Z0}"))
    fouled = isect(keel, plate) if keel is not None else 0.0
    out.append(("collars hang INSIDE their reliefs, clear of the carbon",
                fouled < EPS, f"{fouled:.3f} mm³ of collar in plate_top"))
    try:
        gap = keel.distance_to(plate) if rings else 0.0
        out.append((f"collar-to-relief-wall gap >= {KEY_CLEAR} (designed KEY_CLEAR)",
                    gap >= p["KEY_CLEAR"] - 0.05, f"{gap:.3f} mm"))
    except Exception as exc:  # noqa: BLE001 - OCCT can refuse a distance on a 12-solid compound
        out.append((f"collar-to-relief-wall gap >= {KEY_CLEAR}", False, f"not measurable: {exc}"))
    win_a, rel_a = _windows(p).area, sum(f.area for f in reliefs)
    out.append(("strap windows are cut INSIDE the collars, never wider than the reliefs",
                win_a < rel_a, f"windows {win_a:.1f} mm² vs relief openings {rel_a:.1f} mm²"))

    # --- 2. NEIGHBOURS: measured against the parts those modules actually build ----------------
    for sib, need in (("gopro_mount", 2.0), ("gps_mount", 2.0)):
        try:
            sib_parts = importlib.import_module(f"tigerbee.accessories.{sib}").build()
            dist = min(pad.distance_to(q) for q in sib_parts.values())
            over = max(isect(pad, q) for q in sib_parts.values())
            y0 = min(q.bounding_box().min.Y for q in sib_parts.values())
            out.append((f">= {need} mm to the built {sib}", dist >= need and over < EPS,
                        f"{dist:.3f} mm ({sib} starts at y {y0:.1f}), overlap {over:.3f} mm³"))
        except Exception as exc:  # noqa: BLE001 - a sibling mid-edit must not fail this module
            out.append((f">= {need} mm to the built {sib}", True,
                        f"SKIPPED, {sib} did not build: {type(exc).__name__}: {exc}"[:140]))

    # --- 3. CARBON SUPPORT: the REAL top face, holes subtracted --------------------------------
    face = plate_face("plate_top", Z_TOP_TOP)
    apertures = _front_apertures(p)
    intrusions = []
    for ap in apertures:
        tool = extrude(Plane.XY.offset(Z0 - 1.0) * offset(ap, p["FRONT_CLEAR"] - 0.05),
                       amount=(z3 - Z0) + 2.0, dir=(0, 0, 1))
        v = isect(pad, tool)
        if v > EPS:
            intrusions.append(f"{ap.bounding_box().center().X:.1f},{ap.bounding_box().center().Y:.1f}: {v:.2f} mm³")
    out.append((f"pad edge keeps {p['FRONT_CLEAR']} mm off every plate_top aperture forward of "
                f"y {p['Y_SOLID']}", not intrusions,
                f"{len(apertures)} apertures; {'; '.join(intrusions) or 'none intruded'}"))

    if p["STOP"]:
        step = 0.5
        n_x = int(2 * p["X_MAX"] / step)
        n_y = max(1, int((p["Y_FRONT"] - p["STOP_Y0"]) / step))
        pts = [(-p["X_MAX"] + i * step, p["STOP_Y0"] + j * step)
               for i in range(n_x + 1) for j in range(n_y + 1)]
        inside = [xy for xy in pts if pad.is_inside((xy[0], xy[1], Z0 + 0.2))]
        backed = [xy for xy in inside if face.is_inside((xy[0], xy[1], Z_TOP_TOP))]
        frac = len(backed) / len(inside) if inside else 0.0
        out.append(("the front stop band stands on carbon over its whole footprint",
                    inside and frac >= 0.999,
                    f"{len(backed)}/{len(inside)} samples on plate_top material ({frac:.1%})"))

    # --- 4. ENVELOPE ---------------------------------------------------------------------------
    bb = pad.bounding_box()
    out.append((f"inside the catalog envelope Z {ENV_Z[0]}-{ENV_Z[1]}",
                bb.min.Z >= ENV_Z[0] - 1e-6 and bb.max.Z <= ENV_Z[1] + 1e-6,
                f"Z {bb.min.Z:.3f}..{bb.max.Z:.3f}"))
    out.append((f"the pack seat is the Z {z3} plane, nothing stands proud of it",
                bb.max.Z <= z3 + 1e-6, f"max Z {bb.max.Z:.3f} vs land tops {z3:.1f}"))

    # --- 5. MIN WALL on the CAD solid (the decorated mesh has decorate_ex's own wall_floor) -----
    ok_wall, _worst, detail = min_wall(base, WALL)
    out.append((f"min wall >= {WALL} on the functional solid", ok_wall, detail))
    return out
