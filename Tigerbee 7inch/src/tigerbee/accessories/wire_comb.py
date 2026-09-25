"""Wire comb / cable router: four routing styles, two exact mounting interfaces.

A 303 mm seven-inch has four ~120 mm motor runs plus the VTX, camera, GPS and RX tails, and
nothing in the other accessory families routes a single one of them. Unrouted wire chafes on the
carbon edges, and a chafed phase wire on a 6S pack is a fire. This module ships the two combs that
fix it, both mating numerically to the real frame:

  ARM COMB   a U saddle that slides onto the carbon arm shaft (12.0 x 5.0 prism, frame Z 2-7) at
             arm-local y 55-75 - inboard of motor_guard's face at y 84.8 - with a comb flange on
             the trailing flank carrying five wire channels that run ALONG the arm. The saddle
             walls end flush with the arm top face (frame Z 7) exactly as arm_sleeve's do, so
             nothing enters a prop disc; the retention is a pair of 0.4 mm/side detent wedges per
             wall (0.8 mm total squeeze = the TPU95A snap figure), which is a declared press fit.
  STACK COMB a bar on the plate_bottom waist accessory holes (+-28, 0), seating on the plate
             UNDERSIDE at Z 0 with two Ø4.0 registration bosses and an M3 through the Ø3.4 bore at
             (28, 0). It hangs 3.0 mm - no deeper, so it stays above the default landing plane
             Z -3.0 and 12 mm clear of led_buzzer's bar, which stands on GROUND_Z -15.2.

WHY THE CHANNELS OPEN DOWNWARD AND THE CARBON IS THE ROOF. The stack comb has exactly 3.0 mm of
depth to work in. A Ø2.2 bore fully enclosed in 3.0 mm leaves 0.4 mm of wall, so the four motor
channels are open-topped: the pocket runs right up to the seating face and the bottom plate's own
carbon closes it. The wire pushes in past the 1.6 mm throat from below and is then trapped between
the hook shoulders and the plate. The battery/VTX lead is thicker than the whole bar is deep, so it
gets the one feature that does not care about depth: a vertical Ø3.6 eyelet at (0, 0) with a 1.6 mm
throat out through the rear edge - a strain relief you push the lead into sideways, not a channel.

FOUR VARIANTS, four silhouettes, and they differ in LENGTH and mass as well as in form because
each one's declared wall drives its tooth ligament, its floor, its pocket roof and its end walls:

  brutalist  3.0 mm everything, square teeth on a 5.4 mm pitch, 1.0 mm chamfers and no fillet
             above r 0.3, board marking down every large face and a sunk datum plaque. 5.6 cm³.
  origami    a constant 1.8 mm sheet whose plan alternates between full depth and a waist on
             straight 67.5 deg creases. The crease angle is not decoration: a 45 deg leg needs as
             much x as it gains in y and would run into the channel beside it. 3.6 cm³.
  filigree   a 2.4 mm spine along the load path, 1.4 mm scroll ribbons and Ø4.0 ring nodes off
             it; the outline is a run of tangent arcs and 57 % of the plan is void. 2.8 cm³.
  vespid     a tapered abdomen: one tergite per channel, each 0.86 x the girth of the one before
             it, proud collars, undercut grooves and a stinger cusp. 4.5 cm³.

Pure build123d - no Blender anywhere, so all four are always available whatever else is broken.
"""

from functools import lru_cache
from math import atan2, degrees

from build123d import (Axis, Circle, GeomType, Part, Plane, Polygon, Pos, Rectangle, Sketch, chamfer,
                       extrude)

from tigerbee import params as PARAMS
from tigerbee.accessories._common import *  # noqa: F401,F403 - constants, builders and checks

NAME = "wire_comb"
TITLE = "Wire comb / cable router"
MATERIAL = "TPU95A"

_CORNERS = ("front_right", "front_left", "rear_right", "rear_left")
ARM_LABELS = tuple(f"wire_comb_arm_{c}" for c in _CORNERS)
STACK_LABEL = "wire_comb_stack"

# The arm comb clamps the same free shaft span that arm_sleeve's U-sleeve covers (arm-local
# y 40-84), so the two cannot share an arm and the combined assembly installs arm_sleeve (first
# alphabetically) instead. That exclusion is about the ARMS only: wire_comb_stack bolts under the
# bottom plate, touches nothing arm_sleeve touches, and can be printed and fitted alongside it.
EXCLUSIVE = ("arm_sleeve",)

PRINT = {**{lab: (0, 0, -1) for lab in ARM_LABELS}, STACK_LABEL: (0, 0, -1)}
MOUNTS = {
    **{lab: ("arm_" + lab.rsplit("wire_comb_arm_", 1)[1] + " carbon shaft: both 5 mm flanks and the "
             "underside, arm-local y 55-75 (sliding fit 0.25/side)",
             "arm top face Z 7 (the saddle walls end flush with it)") for lab in ARM_LABELS},
    STACK_LABEL: ("plate_bottom underside Z 0 (the whole seating face bears on it)",
                  "Ø4.5 accessory holes (±28, 0) - two Ø4.0 registration bosses",
                  "Ø4.5 accessory hole (28, 0) - the M3 bolt axis"),
}
HARDWARE = {
    **{lab: ("none - the saddle snaps over the arm shaft on four 0.4 mm/side detent wedges "
             "(0.8 mm total squeeze)",) for lab in ARM_LABELS},
    STACK_LABEL: ("1 x M3 x 8 button head + M3 nyloc through the plate_bottom waist hole (28, 0); "
                  "the nut is captured in the 5.9 AF hex pocket in the comb's underside",),
}

# The six new style languages land in _style.py on their own schedule. Until "brutalist" and
# friends exist there, each variant names the closest EXISTING family as its donor law, so the
# module - and the kit tables in _export - work either way and nothing has to wait on anybody.
_DONOR = {"brutalist": "arsenal", "origami": "shard", "filigree": "chassis", "vespid": "feral"}


def style_key(name: str) -> str:
    return name if name in STYLES else _DONOR[name]


VARIANTS = {
    "brutalist": {"style": style_key("brutalist"),
                  "notes": "one poured slab. 3.0 mm walls and a 3.0 mm tooth ligament (twice the "
                           "catalogue), square teeth, 1.0 mm chamfers and no fillet above r 0.3, "
                           "board-marking grooves 0.6 x 0.3 at 2.4 pitch down every large face, "
                           "and a plan of rectangles and 45 deg cuts only. The heaviest comb: it "
                           "does not care that it is 25 mm long."},
    "origami": {"style": style_key("origami"),
                "notes": "one folded sheet. A constant 1.8 mm sheet whose plan is a zigzag - full "
                         "depth at every channel, folded back to a waist between them on straight "
                         "45 deg legs - and whose keyhole pockets are sheared 22.5 deg to the "
                         "fold. 0.4 mm chamfers, no fillet, no curve in the outline anywhere."},
    "filigree": {"style": style_key("filigree"),
                 "notes": "ornamental cutwork on a rigid spine. A 2.4 mm spine runs the load path "
                          "from the saddle wall to the flange tip; everything else is cut away to "
                          "1.4 mm ribbons and Ø4.0 ring nodes, so the outline is a run of tangent "
                          "arcs. Roughly half the mass of the brutalist comb."},
    "vespid": {"style": style_key("vespid"),
               "notes": "a wasp's abdomen lying along the arm. One tergite per channel, each "
                        "0.86 x the girth of the one before it, each opening with a 1.2 mm proud "
                        "collar and a 0.45 mm undercut groove, ending in a stinger cusp of tip "
                        "radius 0.8. The outline steps down visibly from saddle to tip."},
}
ASSEMBLY_VARIANT = "brutalist"


# --- frame interface (exact, shared by every variant) -----------------------------------------
ARM_W = PARAMS.SHAFT_WIDTH        # 12.0 carbon shaft width
ARM_TH = PARAMS.ARM_T             # 5.0 carbon thickness; arm-local z 0..5 == frame Z 2..7
CLEARANCE = 0.25                  # sliding fit per side on the shaft flanks
Y0, Y1 = 55.0, 75.0               # arm-local span (motor_guard's face is at y 84.8)


@lru_cache(maxsize=1)
def shaft_half() -> tuple[float, float]:
    """Half width of the REAL carbon outline at (Y0, Y1). The 12.0 mm shaft is nominal: the arm
    tapers, and over y 55-75 it runs 13.46 -> 12.32 mm wide. A saddle cut to the nominal 12.0
    would bite 0.5 mm into the carbon at the inboard end, so the pocket follows the taper - which
    also means the comb wedges home as it is pushed inboard instead of sliding about."""
    from tigerbee.profiles import build_arm
    face = max((f for f in build_arm().faces()
                if f.geom_type == GeomType.PLANE and abs(f.normal_at().Z) > 0.99),
               key=lambda f: f.area)
    out = []
    for y in (Y0, Y1):
        res = face & (Pos(0, y, face.center().Z) * Rectangle(400, 0.002))
        faces = res.faces() if res is not None and hasattr(res, "faces") else []
        out.append(round(max(q.bounding_box().max.X for q in faces if q.area > 1e-9), 3))
    return tuple(out)


def pocket_half(y: float) -> float:
    """Straight-line pocket wall: it lies OUTSIDE the arm's slightly convex taper everywhere
    between Y0 and Y1, so the fit is 0.25 mm at both ends and never less anywhere between."""
    h0, h1 = shaft_half()
    return h0 + CLEARANCE + (h1 - h0) * (y - Y0) / (Y1 - Y0)


# Constant outer face, so the flange geometry stays simple: the wall is CLIP_WALL exactly where
# the shaft is widest (y 55, half width 6.734) and thickens to 2.17 by y 75 as the carbon tapers
# away. checks() re-measures it against the real profile rather than trusting this number.
OUT_HALF = 8.60
TOP_Z = ARM_TH                    # saddle walls flush with the arm top face (frame Z 7)
SNAP = 0.8                        # total squeeze: two 0.4 mm/side detent wedges per wall
LIP_Y = ((Y0 + 3.0, Y0 + 7.0), (Y1 - 7.0, Y1 - 3.0))

STACK_HOLES = ((-28.0, 0.0), (28.0, 0.0))
BOLT_XY = (28.0, 0.0)
BOSS_H = 1.8                      # 0.2 shy of the plate top face
BOLT_D = D_M3_THRU                # 3.4
HEX_AF, HEX_DEPTH, HEX_ROT = 5.9, 1.6, 30.0   # M3 nyloc capture in the underside, flats facing X
STACK_Z0, STACK_Z1 = -3.0, 0.0    # the whole hang: the default landing plane is Z -3.0
STACK_HALF_Y = 7.0
# The bar's plan follows the real plate_bottom edge at the waist (34.0 half width at y 0, 31.0 at
# y +-7, measured with outline_spans), so nothing overhangs the carbon and the nyloc pocket at
# (28, 0) keeps 3 mm of material outboard of it.
STACK_HALF_X, STACK_WAIST_X = 34.0, 31.0

# --- wire slots -------------------------------------------------------------------------------
D_PHASE = 2.2                     # 16 AWG motor phase
D_MAIN = 3.4                      # battery / VTX lead
THROAT = 1.6                      # keyhole throat: the wire pushes past it and stays
SLOT_CLEAR = 0.2                  # pocket = d + SLOT_CLEAR
HOOK_H = 0.6                      # height of the narrowed throat band (the retaining shoulders)
N_PHASE = 4
STACK_SLOT_X = (-20.0, -12.0, 12.0, 20.0)
EYELET_XY = (0.0, 0.0)
EYELET_D = D_MAIN + SLOT_CLEAR    # 3.6 vertical strain-relief eyelet through the bar
# The four stack channels are open-topped (the plate's carbon is their roof), so each one would
# saw the bar into strips. A 2.2 mm hook bridge across the middle of each mouth puts it back
# together; the ~5 mm of open mouth either side of it is where the wire goes in.
STACK_BRIDGE_Y = ((-1.1, 1.1),)   # on the centreline, the one band every variant's plan carries

# --- style -------------------------------------------------------------------------------------
GROOVE_W, GROOVE_D, GROOVE_PITCH = 0.6, 0.3, 2.4
CHAMFER = 1.0
FOLD_DEG, PLAN_FOLD_DEG = 22.5, 45.0   # origami uses nothing but {22.5, 45, 67.5}
FOLD_TAN = 0.41421               # tan 22.5: how far the sheared pocket walls lean
FOLD_STEEP_TAN = 2.41421         # tan 67.5: the plan creases, steep enough to fit a ligament
TERGITE_GIRTH = 0.86              # vespid: each segment is 0.86 x the girth of the one before it
COLLAR, UNDERCUT = 1.2, 0.45      # vespid: proud collar and the groove immediately aft of it
STINGER_R = 0.8                   # vespid tip radius
RIBBON, SPINE = 1.4, 2.4          # filigree: ribbon and spine widths
RING_OD = 4.0                     # filigree: ring node diameter over a channel
WALL_FLOOR = 1.2                  # TPU95A material minimum, enforced on every variant
PLAQUE, PLAQUE_DEPTH = 22.0, 0.8  # brutalist's cast-in datum stamp (2.0 would halve the roof)

# Per variant: `wall` is the declared body law and drives the tooth ligament, the saddle floor,
# the pocket roof and the end walls - so the four combs differ in LENGTH and mass as well as in
# form. The saddle's own 1.6 mm clip wall is fixed by the mating spec and is never restyled.
_V = {
    "brutalist": dict(wall=3.0, floor=3.0, top_wall=3.0, grooves=True, chamfer=CHAMFER, shear=0.0,
                      end_pad=0.0),
    # NO pocket shear: a 22.5 deg lean over a 3.2 mm pocket walks 1.33 mm sideways, which is most
    # of the 1.8 mm tooth the crease beside it has to stand in. The folds live in the plan.
    # pitch is set explicitly, not derived: a 67.5 deg crease needs 1.24 mm of run and must keep
    # 1.32 mm off the channel wall beside it, so the fold only fits on a 6.6 mm tooth pitch. On the
    # derived 4.4 pitch the crease face ends up 0.3 mm from the pocket - measured, not guessed.
    "origami": dict(wall=1.8, floor=1.8, top_wall=1.8, grooves=False, chamfer=0.4, shear=0.0,
                    end_pad=0.8, clear=0.4, pitch=6.6),
    "filigree": dict(wall=1.4, floor=2.4, top_wall=1.4, grooves=False, chamfer=0.0, shear=0.0,
                     end_pad=1.0),
    "vespid": dict(wall=2.2, floor=2.2, top_wall=1.8, grooves=False, chamfer=0.0, shear=0.0,
                   end_pad=0.6),
}


def _p(variant: str, **overrides) -> dict:
    p = dict(_V.get(variant, _V["brutalist"]))
    p["variant"] = variant
    p.update(overrides)
    p.setdefault("clear", SLOT_CLEAR)
    p["pitch"] = p.get("pitch", (D_PHASE + p["clear"]) + p["wall"])
    p["x0"] = OUT_HALF + (D_PHASE + p["clear"]) / 2 + p["wall"] + p["end_pad"]
    p["phase_x"] = tuple(p["x0"] + i * p["pitch"] for i in range(N_PHASE))
    p["flange_x1"] = p["phase_x"][-1] + (D_PHASE + p["clear"]) / 2 + p["wall"] + p["end_pad"]
    p["main_x"] = -(OUT_HALF + (D_MAIN + p["clear"]) / 2 + p["wall"] + p["end_pad"])
    p["flange_x0"] = p["main_x"] - (D_MAIN + p["clear"]) / 2 - p["wall"] - p["end_pad"]
    p["z_mouth"] = -p["floor"]
    p["z_top"] = TOP_Z - p["top_wall"]
    return p


def slots_of(p: dict) -> tuple[tuple[float, float], ...]:
    """((centre x, wire Ø), ...) for one arm comb: four phases on the trailing flank, the fat
    battery/VTX lead on the leading flank."""
    return (*((x, D_PHASE) for x in p["phase_x"]), (p["main_x"], D_MAIN))


# --- primitives ---------------------------------------------------------------------------------
def prism_xz(pts, y0: float, y1: float) -> Part:
    """Polygon given as (x, z) pairs, extruded along +Y from y0 to y1."""
    return extrude(Plane.XZ.offset(-y1) * Polygon(*pts, align=None), amount=y1 - y0)


def slot_sketch(xc: float, d: float, z_mouth: float, z_top: float, shear: float = 0.0,
                arch: bool = True, clear: float = SLOT_CLEAR) -> Sketch:
    """Keyhole in the XZ plane: a (d + SLOT_CLEAR) wide pocket closed by a Ø(d + SLOT_CLEAR) arch
    at z_top, and a THROAT wide mouth below it. The step IS the retention - the wire snaps past
    the shoulders and cannot fall back out, and the arch keeps the roof printable without support
    (`overhangs()` exempts a horizontal-axis cylinder under Ø10). `shear` leans the pocket walls,
    which is how origami folds them. arch=False leaves the pocket open-topped: the stack comb's
    roof is the bottom plate's own carbon, so there is nothing there to bridge.

    This one function is both the cutting profile and the region handed to admits_disc(), so the
    check can never drift from the geometry."""
    half = (d + clear) / 2
    z_step = z_mouth + HOOK_H
    zc = z_top - half if arch else z_top
    lean = shear * (zc - z_step)
    poly = Polygon((xc - THROAT / 2, z_mouth), (xc + THROAT / 2, z_mouth),
                   (xc + THROAT / 2, z_step), (xc + half, z_step), (xc + half + lean, zc),
                   (xc - half + lean, zc), (xc - half, z_step), (xc - THROAT / 2, z_step),
                   align=None)
    sk = Sketch() + poly
    return sk + Pos(xc + lean, zc) * Circle(half) if arch else sk


def prism_sk(sk: Sketch, y0: float, y1: float) -> Part:
    """Sketch drawn in (x, z), extruded along +Y from y0 to y1."""
    return extrude(Plane.XZ.offset(-y1) * sk, amount=y1 - y0)


def groove_field(x0: float, x1: float, z0: float, z1: float, y_face: float, into: float,
                 avoid=(), clear: float = 2.2) -> Part:
    """Board marking: GROOVE_W x GROOVE_D grooves at GROOVE_PITCH running in Z (the print
    direction) across the face at y = y_face; `into` is +1 to cut toward +Y, -1 toward -Y."""
    tool = Part()
    n = int((x1 - x0) // GROOVE_PITCH)
    for i in range(max(0, n - 1)):
        xc = x0 + GROOVE_PITCH * (i + 1)
        if any(abs(xc - a) < clear for a in avoid):
            continue  # a groove over an aperture would leave a 0.3 mm sliver beside it
        ya, yb = sorted((y_face, y_face + into * GROOVE_D))
        tool += box(xc - GROOVE_W / 2, ya, z0 - 0.01, xc + GROOVE_W / 2, yb, z1 + 0.01)
    return tool


# --- the arm comb (arm-local coordinates: shaft x +-6, z 0..5, +y toward the motor) -------------
def _detent_wedges() -> Part:
    """Four 0.4 mm/side wedges, two per wall, apex at local z 4.2. The under-surface rises at
    72 deg, so the part still prints without support with the saddle mouth up. This is the only
    deliberate interference with the frame in the module (ALLOWED_INTERFERENCE covers it)."""
    tool = Part()
    for y0, y1 in LIP_Y:
        ph = pocket_half((y0 + y1) / 2)
        tool += prism_xz([(ph, 3.0), (ph, TOP_Z), (ph - SNAP / 2, 4.2)], y0, y1)
        tool += prism_xz([(-ph, 3.0), (-ph + SNAP / 2, 4.2), (-ph, TOP_Z)], y0, y1)
    return tool


def _pocket(grow: float = 0.0, z0: float = 0.0, z1: float = TOP_Z + 1.0) -> Part:
    """The tapered cavity the carbon shaft occupies, optionally grown `grow` per flank."""
    pts = []
    for y, sgn in ((Y0 - 1.0, 1), (Y1 + 1.0, 1), (Y1 + 1.0, -1), (Y0 - 1.0, -1)):
        pts.append((sgn * (pocket_half(y) + grow), y))
    return extrude(Plane.XY.offset(z0) * (Sketch() + Polygon(*pts, align=None)), amount=z1 - z0)


def _arm_slot_tool(p: dict) -> Part:
    tool = Part()
    for xc, d in slots_of(p):
        lean = p["shear"] * (1.0 if xc > 0 else -1.0)
        tool += prism_sk(slot_sketch(xc, d, p["z_mouth"] - 0.02, p["z_top"], lean, clear=p["clear"]),
                         Y0 - 1.0, Y1 + 1.0)
    return tool


def _arm_thin_features(p: dict) -> tuple[Part, ...]:
    """Declared sub-wall features: the keyhole hook shoulders and the four detent wedges."""
    out = [_detent_wedges()]
    if p["variant"] == "brutalist":  # the sunk plaque: its letter gaps are a mark, not a wall
        out.append(box(OUT_HALF - 0.5, Y0 - 0.1, TOP_Z - PLAQUE_DEPTH - 0.1, p["flange_x1"] + 0.5,
                       Y1 + 0.1, TOP_Z + 0.1))
    if p["variant"] == "vespid":
        out += _collar_lips(OUT_HALF, p["flange_x1"], p["phase_x"], Y0, Y1, +1.0, p["z_mouth"], TOP_Z)
        out += _collar_lips(-OUT_HALF, p["flange_x0"], [p["main_x"]], Y0, Y1, -1.0, p["z_mouth"], TOP_Z)
    if p["grooves"]:  # board marking is 0.3 deep surface texture, not a wall
        out += [box(p["flange_x0"] - 1, Y0 - 0.1, p["z_mouth"] - 0.1, p["flange_x1"] + 1,
                    Y0 + GROOVE_D + 0.2, TOP_Z + 0.1),
                box(p["flange_x0"] - 1, Y1 - GROOVE_D - 0.2, p["z_mouth"] - 0.1,
                    p["flange_x1"] + 1, Y1 + 0.1, TOP_Z + 0.1)]
    for xc, d in slots_of(p):
        half = (d + p["clear"]) / 2 + p["shear"] * (TOP_Z - p["z_mouth"]) + 0.06
        out.append(box(xc - half, Y0 - 0.1, p["z_mouth"] - 0.1, xc + half, Y1 + 0.1,
                       p["z_mouth"] + HOOK_H + 0.1))
    return tuple(out)


def _saddle(p: dict) -> Part:
    """The exact mating half: floor, two clip walls flush with the arm top face, four detents."""
    body = box(-OUT_HALF, Y0, -p["floor"], OUT_HALF, Y1, TOP_Z) - _pocket()
    return body + _detent_wedges()


def _arm_comb(variant: str, **overrides) -> Part:
    p = _p(variant, **overrides)
    body = _saddle(p)
    body += _arm_body(p)
    body -= _arm_slot_tool(p)
    return body


def _rect(x0: float, y0: float, x1: float, y1: float) -> Sketch:
    return Pos((x0 + x1) / 2, (y0 + y1) / 2) * Rectangle(abs(x1 - x0), abs(y1 - y0))


def _poly(pts) -> Sketch:
    """Polygon with its winding normalised. A clockwise point list extrudes DOWNWARD, which is how
    a mirrored flange quietly ends up 6.8 mm below the landing plane; sort it out here, once."""
    area = sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(pts, [*pts[1:], pts[0]]))
    return Sketch() + Polygon(*(pts if area >= 0 else list(reversed(pts))), align=None)


def _fold_strip(x0: float, x1: float, stations, amp: float, y0: float = Y0, y1: float = Y1) -> Sketch:
    """ORIGAMI: one folded sheet. The strip alternates between full depth and a waist, and every
    crease is a straight 67.5 deg leg (one of the three allowed fold angles) placed at the midpoint
    BETWEEN two channels - so the whole fold, legs included, fits inside the tooth ligament and the
    outline meets every channel wall square. A 45 deg leg would need as much x as it gains in y,
    walk into the channel beside it and leave an acute 45 deg wedge of material there; 67.5 deg
    buys the same 3 mm of fold for 1.24 mm of run."""
    lo, hi = min(x0, x1), max(x0, x1)
    st = sorted(stations)
    run = amp / FOLD_STEEP_TAN                       # x consumed by one 67.5 deg leg
    gaps = [b - a for a, b in zip(st, st[1:])] or [4.0]
    if run > min(gaps) / 2 - 0.2:                    # never let a crease reach a channel wall
        run = max(min(gaps) / 2 - 0.2, 0.2)
        amp = run * FOLD_STEEP_TAN
    off = [0.0 if k % 2 else amp for k in range(len(st))]
    edge = [(lo, off[0])]
    for k in range(len(st) - 1):
        m = (st[k] + st[k + 1]) / 2
        edge += [(m - run / 2, off[k]), (m + run / 2, off[k + 1])]
    edge.append((hi, off[-1]))
    pts = [(x, y0 + o) for x, o in edge] + [(x, y1 - o) for x, o in reversed(edge)]
    return _poly(pts)


def _gaps(x0: float, x1: float, stations, half: float) -> list[tuple[float, float]]:
    """((centre, width), ...) of the solid gaps BETWEEN the channels and at both flange ends.

    A scroll node belongs in a gap and must FIT it. Both failure modes were measured on this
    part: a node centred over a channel is cut away by it and leaves its ribbon standing 0.32 mm
    from the pocket wall, and a node that overhangs a channel by a whisker leaves a 0.06 mm
    crescent on the far side. Sizing every node to its own gap removes both by construction."""
    lo, hi = min(x0, x1), max(x0, x1)
    out, prev = [], lo
    for sx in sorted(stations):
        out.append(((prev + sx - half) / 2, sx - half - prev))
        prev = sx + half
    out.append(((prev + hi) / 2, hi - prev))
    return [(c, w) for c, w in out if w > 0.3]


def _scrollwork(x0: float, x1: float, stations, half: float, y0: float = Y0, y1: float = Y1,
                reach: float = 0.62, spine: float = SPINE, max_w: float = 5.0) -> Sketch:
    """FILIGREE: a SPINE traced along the load path (saddle wall to flange tip) with everything
    else cut away - a scroll ribbon in every gap between the channels, alternating above and
    below the spine, each capped by a ring node whose arc closes the outline. Every ribbon is
    exactly as wide as the gap it stands in, so the outline meets each channel wall square and
    the scrollwork can never leave a sliver against one."""
    yc = (y0 + y1) / 2
    sk = _rect(x0, yc - spine / 2, x1, yc + spine / 2)
    for x, w in _gaps(x0, x1, stations, half):
        if w > max_w + 2 * 1.2:      # a wide gap keeps a scroll of its own width, not a wall
            w = max_w
        for sgn in (1.0, -1.0):      # mirrored about the spine, as scrollwork is
            y = yc + sgn * (y1 - y0) / 2 * reach
            sk += _rect(x - w / 2, min(yc, y), x + w / 2, max(yc, y))
            sk += Pos(x, y) * Circle(w / 2)
    return sk


def _tergites(x0: float, x1: float, stations, y0: float, y1: float):
    """((a, b, girth), ...) - one segment per channel, each 0.86 x the girth of the one before it,
    running outward from the saddle. `a` is the segment's inboard end, where its collar sits."""
    half = (y1 - y0) / 2
    st = sorted(stations, key=lambda x: abs(x - x0))
    bounds = [x0, *[(a + b) / 2 for a, b in zip(st, st[1:])], x1]
    return tuple((bounds[k], bounds[k + 1], half * TERGITE_GIRTH ** k) for k in range(len(bounds) - 1))


def _collar_lips(x0: float, x1: float, stations, y0: float, y1: float, outward: float,
                 z0: float, z1: float) -> tuple[Part, ...]:
    """The 1.2 mm proud collar edges as min-wall allowances: a shingle lip standing 0.6 mm outside
    its own tergite is a deliberate sub-wall feature, exactly like the keyhole hook shoulders."""
    yc = (y0 + y1) / 2
    out, prev = [], None
    for a, _b, g in _tergites(x0, x1, stations, y0, y1):
        lo, hi = min(g, prev if prev is not None else g), max(g, prev if prev is not None else g)
        xa, xb = sorted((a, a + outward * (COLLAR + UNDERCUT)))
        xa, xb = xa - 0.35, xb + 0.35
        out.append(box(xa, yc + lo - 0.25, z0 - 0.1, xb, yc + hi + 0.85, z1 + 0.1))
        out.append(box(xa, yc - hi - 0.85, z0 - 0.1, xb, yc - lo + 0.25, z1 + 0.1))
        prev = g
    return tuple(out)


def _abdomen(x0: float, x1: float, stations, outward: float, y0: float = Y0,
             y1: float = Y1) -> Sketch:
    """VESPID: a tapered segmented abdomen. One tergite per channel, each 0.86 x the girth of the
    one before it, each opening with a 1.2 mm proud collar and a 0.45 mm undercut groove aft of
    it, so the profile reads as scalloped shingles; a stinger cusp closes the outboard end."""
    yc = (y0 + y1) / 2
    sk = Sketch()
    segs = _tergites(x0, x1, stations, y0, y1)
    for a, b, g in segs:
        sk += _rect(a, yc - g, b, yc + g)
        c0 = a + outward * COLLAR
        sk += _rect(a, yc - g - 0.6, c0, yc + g + 0.6)
        u = a + outward * (COLLAR + UNDERCUT)
        sk -= _rect(c0, yc + g - 0.2, u, yc + g + 2.0)
        sk -= _rect(c0, yc - g - 2.0, u, yc - g + 0.2)
    g = segs[-1][2]
    tip = x1 + outward * min(g - STINGER_R, 4.0)
    sk += _poly([(x1, yc - g), (x1, yc + g), (tip, yc + STINGER_R), (tip, yc - STINGER_R)])
    return sk + Pos(tip, yc) * Circle(STINGER_R)


def _arm_plan(p: dict) -> Sketch:
    """Plan (XY) outline of the two comb flanges - this is where the four variants part company.
    The saddle underneath, and every mating dimension in it, is identical in all four."""
    v = p["variant"]
    trail = (OUT_HALF, p["flange_x1"])          # four phase channels
    lead = (p["flange_x0"], -OUT_HALF)          # the fat battery / VTX channel
    phase, main = list(p["phase_x"]), [p["main_x"]]
    if v == "origami":
        sk = _fold_strip(*trail, phase, 3.0) + _fold_strip(lead[1], lead[0], main, 3.0)
        return chamfer(sk.vertices().group_by(Axis.X)[0] + sk.vertices().group_by(Axis.X)[-1], 0.4)
    if v == "filigree":
        return (_scrollwork(*trail, phase, (D_PHASE + p["clear"]) / 2, reach=0.70)
                + _scrollwork(lead[1], lead[0], main, (D_MAIN + p["clear"]) / 2, reach=0.70))
    if v == "vespid":
        return _abdomen(trail[0], trail[1], phase, +1.0) + _abdomen(lead[1], lead[0], main, -1.0)
    sk = _rect(trail[0], Y0, trail[1], Y1) + _rect(lead[0], Y0, lead[1], Y1)
    return chamfer(sk.vertices().group_by(Axis.X)[0] + sk.vertices().group_by(Axis.X)[-1], CHAMFER)


def _arm_body(p: dict) -> Part:
    body = extrude(Plane.XY.offset(p["z_mouth"]) * _arm_plan(p), amount=TOP_Z - p["z_mouth"])
    if p["variant"] == "brutalist" and mark_fits("wordmark", PLAQUE):
        # the datum stamp goes on the flange roof - the one large uninterrupted face on the part,
        # 3.0 mm thick here, so a 0.8 deep plaque still leaves 2.2 over the channel arches
        body -= mark("wordmark", PLAQUE, "deboss",
                     ((OUT_HALF + p["flange_x1"]) / 2, (Y0 + Y1) / 2, TOP_Z), (0, 0, 1),
                     depth=PLAQUE_DEPTH, x_dir=(1, 0, 0))
    if p["grooves"]:
        body -= groove_field(OUT_HALF, p["flange_x1"], p["z_mouth"], TOP_Z, Y0, +1)
        body -= groove_field(OUT_HALF, p["flange_x1"], p["z_mouth"], TOP_Z, Y1, -1)
        body -= groove_field(p["flange_x0"], -OUT_HALF, p["z_mouth"], TOP_Z, Y0, +1)
        body -= groove_field(p["flange_x0"], -OUT_HALF, p["z_mouth"], TOP_Z, Y1, -1)
    return body


# --- the stack comb (frame coordinates) ---------------------------------------------------------
def _stack_plan(p: dict) -> Sketch:
    """The bar's plan, styled like the arm comb's flange - but the two bolt pads and the collar
    round the eyelet are unioned in afterwards, so no style can ever thin a mating feature."""
    v, st = p["variant"], list(STACK_SLOT_X)
    a, b, hy = -STACK_WAIST_X, STACK_WAIST_X, STACK_HALF_Y
    if v == "origami":
        base = _fold_strip(a, b, st, 4.0, -hy, hy)
    elif v == "filigree":
        # the stack channels are open-topped, so a node ON a channel would be cut away with it;
        # the scroll net hangs between them instead, and the centre node rings the eyelet
        # a 5.0 mm spine here, not 2.4: the hook bridge lives on the centreline, and the keyhole
        # shoulders beside it need somewhere to be
        base = _scrollwork(a, b, st, (D_PHASE + p["clear"]) / 2, -hy, hy, 0.45, spine=5.0)
    elif v == "vespid":
        base = (_abdomen(0.0, b, [x for x in st if x > 0], +1.0, -hy, hy)
                + _abdomen(0.0, a, [x for x in st if x < 0], -1.0, -hy, hy))
    else:
        base = _poly([(STACK_HALF_X, 0.0), (b, hy), (a, hy), (-STACK_HALF_X, 0.0), (a, -hy), (b, -hy)])
        base = chamfer(base.vertices().group_by(Axis.X)[0] + base.vertices().group_by(Axis.X)[-1],
                       CHAMFER)
    pads = Sketch()
    for sgn in (1, -1):
        pads += _rect(sgn * 22.0, -5.6, sgn * STACK_HALF_X, 5.6)
    # the eyelet throat must leave through a STRAIGHT edge: cut a 1.6 slot out of a circle and it
    # ends in two tangent cusps that no amount of wall thickness can save
    pads += _rect(-2.1, -STACK_HALF_Y, 2.1, 0.0) + Pos(*EYELET_XY) * Circle(EYELET_D / 2 + 2.0)
    return base + pads


def _stack_slot_tool(p: dict) -> Part:
    tool = Part()
    for xc in STACK_SLOT_X:
        tool += prism_sk(slot_sketch(xc, D_PHASE, STACK_Z0 - 0.02, STACK_Z1 + 0.02,
                                     p["shear"] * (1.0 if xc > 0 else -1.0), arch=False,
                                     clear=p["clear"]), -STACK_HALF_Y - 1.0, STACK_HALF_Y + 1.0)
    ex, ey = EYELET_XY
    tool += cylinder(ex, ey, STACK_Z0 - 0.1, STACK_Z1 + 0.1, EYELET_D)
    tool += box(ex - THROAT / 2, -STACK_HALF_Y - 1.0, STACK_Z0 - 0.1, ex + THROAT / 2, ey,
                STACK_Z1 + 0.1)
    return tool


def _stack_thin_features(p: dict) -> tuple[Part, ...]:
    out = [hex_pocket(HEX_AF + 0.4, HEX_DEPTH + 0.3, (*BOLT_XY, STACK_Z0 - 0.15), HEX_ROT)]
    if p["variant"] == "vespid":
        for sgn, end in ((1.0, STACK_WAIST_X), (-1.0, -STACK_WAIST_X)):
            out += _collar_lips(0.0, end, [x for x in STACK_SLOT_X if x * sgn > 0], -STACK_HALF_Y,
                                STACK_HALF_Y, sgn, STACK_Z0, STACK_Z1)
    if p["grooves"]:
        out += [box(-STACK_HALF_X - 1, -STACK_HALF_Y - 0.1, STACK_Z0 - 0.1, STACK_HALF_X + 1,
                    -STACK_HALF_Y + GROOVE_D + 0.25, STACK_Z1 + 0.1),
                box(-STACK_HALF_X - 1, STACK_HALF_Y - GROOVE_D - 0.25, STACK_Z0 - 0.1,
                    STACK_HALF_X + 1, STACK_HALF_Y + 0.1, STACK_Z1 + 0.1)]
    for xc in STACK_SLOT_X:
        half = (D_PHASE + p["clear"]) / 2 + p["shear"] * (STACK_Z1 - STACK_Z0) + 0.06
        out.append(box(xc - half, -STACK_HALF_Y - 0.1, STACK_Z0 - 0.1, xc + half,
                       STACK_HALF_Y + 0.1, STACK_Z0 + HOOK_H + 0.1))
    return tuple(out)


def _stack_comb(variant: str, **overrides) -> Part:
    p = _p(variant, **overrides)
    body = extrude(Plane.XY.offset(STACK_Z0) * _stack_plan(p), amount=STACK_Z1 - STACK_Z0)
    for xy in STACK_HOLES:
        body += boss(xy, STACK_Z1, BOSS_H, BOSS_D[MATERIAL])
    body -= _stack_slot_tool(p)
    for xc in STACK_SLOT_X:
        for by0, by1 in STACK_BRIDGE_Y:
            body += box(xc - THROAT / 2, by0, STACK_Z0, xc + THROAT / 2, by1, STACK_Z0 + HOOK_H)
    body -= cylinder(*BOLT_XY, STACK_Z0 - 0.1, STACK_Z1 + BOSS_H + 0.1, BOLT_D)
    body -= hex_pocket(HEX_AF, HEX_DEPTH, (*BOLT_XY, STACK_Z0 - 0.01), HEX_ROT)
    if p["grooves"]:
        avoid = (*STACK_SLOT_X, EYELET_XY[0])
        body -= groove_field(-STACK_WAIST_X, STACK_WAIST_X, STACK_Z0, STACK_Z1, -STACK_HALF_Y, +1, avoid)
        body -= groove_field(-STACK_WAIST_X, STACK_WAIST_X, STACK_Z0, STACK_Z1, STACK_HALF_Y, -1, avoid)
    return body


def build(variant: str = ASSEMBLY_VARIANT, **overrides) -> dict[str, Part]:
    local = _arm_comb(variant, **overrides)
    parts = {f"wire_comb_arm_{c}": place_arm(local, PARAMS.ARM_PLACEMENTS[f"arm_{c}"])
             for c in _CORNERS}
    parts[STACK_LABEL] = _stack_comb(variant, **overrides)
    return parts


ALLOWED_INTERFERENCE = {lab: {f"arm_{c}": 1.5} for lab, c in zip(ARM_LABELS, _CORNERS)}
# The M3 nyloc pocket is a 5.9 mm bridged ceiling in the printed underside - well inside the
# 22 mm TPU bridge limit. Print coords: the part is not turned over, so x_p = x, y_p = y,
# z_p = z + 3.0.
BRIDGE_OK = {STACK_LABEL: (("box", BOLT_XY[0] - 4.5, -4.5, 0.9, BOLT_XY[0] + 4.5, 4.5, 2.6),)}


MIN_Z = LANDING_Z
NOTES = {
    **{lab: "Slides onto the carbon shaft from below over arm-local y 55-75 and snaps home on four "
            "0.4 mm/side detent wedges; the 1.6 mm clip walls end flush with the arm top face "
            "(frame Z 7), so no part of it enters a prop disc. Four Ø2.2 phase channels run along "
            "the trailing flank and the fat Ø3.4 battery/VTX channel along the leading one, every "
            "one of them a keyhole with a 1.6 mm throat. Prints saddle-mouth up, floor on the bed: "
            "every widening step faces upward, so it needs no support." for lab in ARM_LABELS},
    STACK_LABEL: "Bolts under the bottom plate on the (±28, 0) waist holes: two Ø4.0 bosses key it, "
                 "one M3 x 8 through the Ø3.4 bore at (28, 0) holds it, and the nyloc sits in the "
                 "5.9 AF hex pocket in the underside. It hangs exactly 3.0 mm, so it stays above "
                 "the landing plane and 62 mm clear of led_buzzer's bar. The four Ø2.2 channels "
                 "are roofed by the plate's own carbon and bridged across the middle; the Ø3.6 eyelet at "
                 "(0, 0) is the battery-lead strain relief.",
}


# --- checks -------------------------------------------------------------------------------------
def _place(part: Part) -> Part:
    return place_arm(part, PARAMS.ARM_PLACEMENTS["arm_front_right"])


def _arm_prism(half_w: float, z0: float = 0.0, z1: float = ARM_TH) -> Part:
    """The carbon shaft itself as a probe, in the installed position of arm_front_right."""
    return _place(box(-half_w, Y0 - 0.5, z0, half_w, Y1 + 0.5, z1))


def _face_area_at(part: Part, z: float, up: bool = True, tol: float = 1e-4) -> float:
    return round(sum(f.area for f in part.faces()
                     if f.geom_type.name == "PLANE" and abs(f.center().Z - z) < tol
                     and (f.normal_at().Z > 0.999 if up else f.normal_at().Z < -0.999)), 3)


def _throat_rows(part: Part, xs, z_mouth: float, y0: float, y1: float, place: bool,
                 tag: str) -> list[tuple[str, bool, str]]:
    """Brackets every throat at THROAT +- 0.05: a (THROAT - 0.1) wide slab must be void and a
    (THROAT + 0.1) wide slab must hit material."""
    void = mat = 0.0
    for xc in xs:
        for w, acc in ((THROAT - 0.1, "void"), (THROAT + 0.1, "mat")):
            probe = box(xc - w / 2, y0, z_mouth + 0.06, xc + w / 2, y1, z_mouth + HOOK_H - 0.06)
            v = isect(part, _place(probe) if place else probe)
            if acc == "void":
                void += v
            else:
                mat += v
    return [(f"{tag}: every throat is {THROAT} +- 0.05 wide", void < EPS and mat > 0.01 * len(xs),
             f"{void:.4f} mm³ inside Ø{THROAT - 0.1}, {mat:.3f} mm³ caught by Ø{THROAT + 0.1}")]


def _bore_coaxial_rows(part: Part) -> list[tuple[str, bool, str]]:
    out = []
    d_hole = {round(h.d, 2) for h in HOLES if abs(abs(h.x) - 28.0) < 1e-6 and abs(h.y) < 1e-6}
    out.append(("frame really has Ø4.5 accessory holes at (±28, 0)", d_hole == {4.5},
                f"plate_bottom hole Ø {sorted(d_hole) or 'MISSING'}"))
    for xy in STACK_HOLES:
        probe = cylinder(*xy, STACK_Z1 + 0.02, STACK_Z1 + BOSS_H - 0.02, BOSS_D[MATERIAL] + 0.06)
        ring = (cylinder(*xy, STACK_Z1 + 0.02, STACK_Z1 + BOSS_H - 0.02, BOSS_D[MATERIAL] + 1.6)
                - cylinder(*xy, STACK_Z1 - 0.1, STACK_Z1 + BOSS_H + 0.1, BOSS_D[MATERIAL] + 0.06))
        inside, around = isect(part, probe), isect(part, ring)
        out.append((f"Ø{BOSS_D[MATERIAL]} boss coaxial with the {xy} hole", inside > 5.0 and around < EPS,
                    f"{inside:.2f} mm³ of boss inside Ø{BOSS_D[MATERIAL] + 0.06}, {around:.3f} mm³ outside it"))
    ok, detail = coaxial(part, BOLT_XY, BOLT_D, STACK_Z0 + 0.02, STACK_Z1 + BOSS_H - 0.02)
    out.append((f"M3 bore Ø{BOLT_D} coaxial with the (28, 0) hole axis", ok, detail))
    return out


def _plan_depth(sk: Sketch, x: float) -> float:
    """Y extent of a plan sketch at abscissa x (vespid's girth probe)."""
    res = sk & (Pos(x, (Y0 + Y1) / 2) * Rectangle(0.02, 400))
    faces = res.faces() if res is not None and hasattr(res, "faces") else []
    return round(max((f.bounding_box().size.Y for f in faces if f.area > 1e-9), default=0.0), 3)


def _style_rows(p: dict, arm: Part, stack: Part) -> list[tuple[str, bool, str]]:
    v = p["variant"]
    out = []
    # the tooth between two neighbouring phase channels, measured: a probe exactly as wide as the
    # designed ligament must be solid through, and one 0.16 mm wider must not be
    lig = p["pitch"] - (D_PHASE + p["clear"])
    x1, x2 = p["phase_x"][1], p["phase_x"][2]
    mid, w, yc = (x1 + x2) / 2, p["wall"], (Y0 + Y1) / 2
    z0 = p["z_mouth"] + HOOK_H + 0.15   # inside the pocket band, above the hook step
    z1 = z0 + 1.5
    mid += p["shear"] * ((z0 + z1) / 2 - (p["z_mouth"] + HOOK_H))   # the sheared teeth lean too
    # measured on the centreline band, which every variant's plan carries (brutalist slab, origami
    # waist, filigree spine, vespid tergite) - so one probe serves all four
    full = box(mid - lig / 2 + 0.02, yc - 0.3, z0, mid + lig / 2 - 0.02, yc + 0.3, z1)
    over = box(mid - lig / 2 - 0.08, yc - 0.3, z0, mid + lig / 2 + 0.08, yc + 0.3, z1)
    got, wide = isect(arm, _place(full)), isect(arm, _place(over))
    out.append((f"[{v}] tooth is {lig:.2f} mm, at or above the declared wall {w}",
                lig >= w - 1e-6 and abs(got - full.volume) < 0.05 * full.volume
                and wide < over.volume - 0.10,
                f"ligament {lig:.2f} vs wall {w}; {got:.2f}/{full.volume:.2f} mm³ solid at "
                f"{lig:.2f} mm, {wide:.2f}/{over.volume:.2f} at {lig + 0.16:.2f}"))
    if v == "origami":
        angs, curved = set(), 0
        for e in _arm_plan(p).edges():
            if e.geom_type.name != "LINE":
                curved += 1
                continue
            d0 = e.end_point() - e.start_point()
            angs.add(round(degrees(atan2(d0.Y, d0.X)) % 90.0, 1))
        allowed = {0.0, 22.5, 45.0, 67.5}
        bad = sorted(a for a in angs if min(abs(a - q) for q in allowed) > 0.2)
        out.append(("[origami] plan is straight-edged and every fold is 22.5/45/67.5 deg",
                    not curved and not bad,
                    f"plan angles {sorted(angs)}; {curved} curved plan edge(s); creases at "
                    f"{degrees(atan2(FOLD_STEEP_TAN, 1)):.1f} deg, sheet {p['wall']} mm"))
    if v == "filigree":
        # measured over the trailing flange's own rectangle - the span between the two flanges is
        # the saddle, and counting that as cutwork would flatter the number
        sk = _arm_plan(p)
        rect = _rect(OUT_HALF, Y0, p["flange_x1"], Y1)
        solid = (sk & rect).area
        void = 1.0 - solid / rect.area
        out.append(("[filigree] void fraction of the flange plan is 45-60 %", 0.45 <= void <= 0.60,
                    f"{void:.1%} void over the {p['flange_x1'] - OUT_HALF:.1f} x {Y1 - Y0:.0f} mm "
                    f"flange, spine {SPINE}, scroll ribbons in every tooth gap"))
    if v == "vespid":
        sk = _arm_plan(p)
        depths = [_plan_depth(sk, x) for x in p["phase_x"]]
        ratios = [round(b / a, 3) for a, b in zip(depths, depths[1:]) if a > 0]
        out.append((f"[vespid] each tergite is {TERGITE_GIRTH} x the girth of the one before it",
                    all(abs(r - TERGITE_GIRTH) <= 0.02 for r in ratios) and len(ratios) == 3,
                    f"girths {[round(d, 2) for d in depths]} mm, ratios {ratios}"))
    if v == "brutalist":
        radii = sorted({round(f.geom_adaptor().Cylinder().Radius(), 2) for part in (arm, stack)
                        for f in part.faces() if f.geom_type.name == "CYLINDER"
                        and hasattr(f.geom_adaptor(), "Cylinder")})
        tori = sum(1 for part in (arm, stack) for f in part.faces() if f.geom_type.name == "TORUS")
        bores = {round((D_PHASE + p["clear"]) / 2, 2), round((D_MAIN + p["clear"]) / 2, 2),
                 round(BOLT_D / 2, 2), round(BOSS_D[MATERIAL] / 2, 2), round(EYELET_D / 2, 2)}
        rounds = [r for r in radii if 0.3 < r < 1.5 and r not in bores]
        out.append(("[brutalist] no fillet above r 0.3 - chamfer only", not tori and not rounds,
                    f"{tori} torus face(s), cylinder radii {radii}"))
        # probe the groove AND the plank between it and the next one, so the row proves the
        # field is really cut and really at the declared pitch - not that it missed the part
        gx = -STACK_WAIST_X + GROOVE_PITCH
        cut = box(gx - GROOVE_W / 4, STACK_HALF_Y - GROOVE_D + 0.05, STACK_Z0 + 0.5,
                  gx + GROOVE_W / 4, STACK_HALF_Y, STACK_Z1 - 0.5)
        plank = box(gx + GROOVE_W, STACK_HALF_Y - GROOVE_D + 0.05, STACK_Z0 + 0.5,
                    gx + GROOVE_PITCH - GROOVE_W, STACK_HALF_Y, STACK_Z1 - 0.5)
        n = int((2 * STACK_WAIST_X) // GROOVE_PITCH) - 1
        v_cut, v_plank = isect(stack, cut), isect(stack, plank)
        out.append((f"[brutalist] board marking {GROOVE_W} x {GROOVE_D} at {GROOVE_PITCH} pitch",
                    v_cut < EPS and v_plank > 0.5 * plank.volume,
                    f"up to {n} grooves per face; groove 1 holds {v_cut:.4f} mm³ of material, the "
                    f"plank beside it {v_plank:.2f}/{plank.volume:.2f} mm³"))
    return out


def checks(parts: dict[str, Part], frame: dict[str, Part], variant: str | None = None):
    v = variant or ASSEMBLY_VARIANT
    p = _p(v)
    arm = parts["wire_comb_arm_front_right"]
    stack = parts[STACK_LABEL]
    arms = [parts[lab] for lab in ARM_LABELS]
    out: list[tuple[str, bool, str]] = []

    # --- the arm interface -------------------------------------------------------------------
    wedge = isect(arm, frame["arm_front_right"])
    over = isect(arm, _place(_pocket(grow=CLEARANCE + 0.1, z0=0.02, z1=ARM_TH - 0.02)))
    h0, h1 = shaft_half()
    out.append(("saddle cavity clears the REAL tapered shaft (only the detents touch it)",
                wedge < 1.5 and over > 10.0,
                f"carbon {2 * h0:.2f} -> {2 * h1:.2f} mm wide over y {Y0}-{Y1}; {wedge:.2f} mm³ of "
                f"detent squeeze against the real arm, {over:.1f} mm³ caught once the cavity is "
                f"opened by a further {CLEARANCE + 0.1} per flank (zero fit)"))
    hits = [h for part in arms for h in interference(part)]
    bad = [(n, q) for n, q in hits if q > 1.5]
    out.append(("no frame interference beyond the declared 0.8 mm snap squeeze", not bad,
                f"overlaps {hits or 'none'}"))
    wall_at_y0 = OUT_HALF - pocket_half(Y0)
    out.append((f"saddle clip wall >= {CLIP_WALL} at the widest point of the taper",
                wall_at_y0 >= CLIP_WALL - 1e-6,
                f"{wall_at_y0:.3f} mm at y {Y0} (outer face {OUT_HALF}, pocket "
                f"{pocket_half(Y0):.3f}), {OUT_HALF - pocket_half(Y1):.3f} mm at y {Y1}"))
    floor = _face_area_at(arm, Z_BOTTOM_TOP)
    out.append((f"saddle floor bears on the arm underside Z {Z_BOTTOM_TOP}", floor >= 200.0,
                f"{floor} mm² of up-facing face at Z {Z_BOTTOM_TOP}"))
    tops = [round(part.bounding_box().max.Z, 4) for part in arms]
    out.append((f"arm combs end flush with the arm top face Z {Z_ARM_TOP}",
                all(abs(t - Z_ARM_TOP) <= 0.05 for t in tops), f"max Z {tops}"))

    # --- the stack interface -----------------------------------------------------------------
    out += _bore_coaxial_rows(stack)
    seat = seats_on(stack, "plate_bottom", Z_BOTTOM_UNDER)
    out.append((f"stack comb seated on the plate_bottom underside Z {Z_BOTTOM_UNDER}", seat >= 90.0,
                f"{seat} mm² of contact"))
    out.append(("stack comb hangs no deeper than the landing plane",
                stack.bounding_box().min.Z >= LANDING_Z - 1e-6,
                f"min Z {stack.bounding_box().min.Z:.3f} vs {LANDING_Z}"))
    try:
        from tigerbee.accessories.led_buzzer import Y_FRONT as LED_Y
    except Exception:  # noqa: BLE001 - sibling module may be mid-edit
        LED_Y = -69.0
    out.append(("clear of led_buzzer's bar (which stands on GROUND_Z -15.2)",
                stack.bounding_box().min.Y - LED_Y > 0.3,
                f"{stack.bounding_box().min.Y - LED_Y:.1f} mm between the bar front y {LED_Y} and "
                f"the comb rear y {stack.bounding_box().min.Y:.1f}"))

    # --- the wire slots ----------------------------------------------------------------------
    admits = []
    for xc, d in slots_of(p):
        admits.append((round(xc, 2), d,
                       admits_disc(slot_sketch(xc, d, p["z_mouth"], p["z_top"],
                                               p["shear"] * (1.0 if xc > 0 else -1.0),
                                               clear=p["clear"]), d)))
    ok_arm = all(a[2] for a in admits)
    out.append(("every arm channel admits its design wire", ok_arm,
                "; ".join(f"x {a[0]} Ø{a[1]}: {'yes' if a[2] else 'NO'}" for a in admits)))
    stack_ok = all(admits_disc(slot_sketch(xc, D_PHASE, STACK_Z0, STACK_Z1,
                                           p["shear"] * (1.0 if xc > 0 else -1.0), arch=False,
                                           clear=p["clear"]), D_PHASE) for xc in STACK_SLOT_X)
    eye = Sketch() + (Circle(EYELET_D / 2) + Pos(0, -STACK_HALF_Y / 2) * Rectangle(THROAT, STACK_HALF_Y))
    out.append((f"every stack channel admits Ø{D_PHASE} and the eyelet admits Ø{D_MAIN}",
                stack_ok and admits_disc(eye, D_MAIN),
                f"4 phase channels {'ok' if stack_ok else 'FAIL'}, Ø{EYELET_D} eyelet "
                f"{'ok' if admits_disc(eye, D_MAIN) else 'FAIL'}"))
    out += _throat_rows(arm, [x for x, _d in slots_of(p)], p["z_mouth"], Y0 + 0.5, Y1 - 0.5, True, "arm comb")
    # clear of the centreline hook bridge, which is material in the mouth ON PURPOSE
    out += _throat_rows(stack, STACK_SLOT_X, STACK_Z0, STACK_BRIDGE_Y[0][1] + 0.2, 2.3, False,
                        "stack comb")

    # --- keep-outs, wall, solidity, printability ----------------------------------------------
    disc = sum(prop_disc_violation(part) for part in (*arms, stack))
    out.append(("outside every prop keep-out disc above Z 7", disc < EPS, f"{disc:.4f} mm³"))
    gaps = {}
    for part in (*arms, stack):
        gaps.update({n: d for n, d in distance_to_frame(part, near=3.0).items() if n.startswith("standoff")})
    worst = min(gaps.values()) if gaps else 99.0
    out.append((f"≥ {STANDOFF_FIT - 0.05} mm to every Ø{STANDOFF_D} standoff", worst >= STANDOFF_FIT - 0.05,
                f"nearest {gaps or 'none within 3 mm'}"))
    zmin = min(part.bounding_box().min.Z for part in (*arms, stack))
    out.append((f"every part above the landing plane Z {LANDING_Z}", zmin >= LANDING_Z - 1e-6, f"min Z {zmin:.3f}"))
    ok_w, _v, detail = min_wall(arm, WALL_FLOOR, allow=tuple(_place(a) for a in _arm_thin_features(p)))
    out.append((f"arm comb: min wall ≥ {WALL_FLOOR} (hook shoulders, detents and the 0.3 mm "
                f"surface texture excepted)", ok_w, detail))
    # OCCT's 3D offset collapses the stack bar - a 3.0 mm slab erodes to 11 mm³ at t 0.58 - so the
    # bar is measured by ray sampling instead, which needs no offset (see _fit.ray_thickness).
    thin, worst, detail = ray_thickness(stack, WALL_FLOOR, allow=_stack_thin_features(p))
    out.append((f"stack comb: min wall ≥ {WALL_FLOOR} by ray sampling (offset unavailable)",
                not thin, f"thinnest {worst:.2f} mm - {detail}"))
    solids = {lab: len(part.solids()) for lab, part in parts.items()}
    out.append(("one valid solid per part", all(n == 1 for n in solids.values()), f"{solids}"))
    for lab, part in parts.items():
        over_f = overhangs(part, PRINT[lab], bridge_ok=BRIDGE_OK.get(lab, ()), material=MATERIAL)
        out.append((f"{lab}: no overhang > 45 deg printed on {PRINT[lab]}", not over_f,
                    "; ".join(over_f) or "none"))
    out += _style_rows(p, arm, stack)
    return out
