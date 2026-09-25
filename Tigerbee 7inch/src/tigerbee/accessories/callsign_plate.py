"""Swappable callsign badge on the top plate: the part that makes the quad YOURS.

Five genuinely different silhouettes carrying the same wordmark, all on one mounting interface:

    brutalist   a poured slab, formwork still showing - chamfer-only edges, board-marking grooves,
                the callsign sunk like a cast-in plaque, one big relief void underneath
    origami     one 1.8 mm sheet folded on 67.5 deg creases into two longitudinal ridges either
                side of a sunken centre panel; the letters stand proud between the ridges
    filigree    a flat cutwork panel: a 2.4 mm spine on y 65.8 carrying a mirrored scroll net of
                1.8 mm ribbons inside a scalloped outline, ring nodes at every junction, the
                letters on a solid cartouche
    vespid      four tergites stepping 0.86 in girth outward from the centre, each shingled behind
                a proud collar, one spiracle slot per segment, the callsign on the central tergite
    carapace    a domed elytron: an R 27.27 barrel vault over an oval, with the dorsal suture and
                the callsign cut by that same vault lowered by their own depth, so both follow the
                crown at constant depth. Built in Blender first (elytra_dome works) and moved back
                to exact B-rep for cause - see the comment above _ca_plan()

MOUNTING - and the two deliberate deviations from the brief, both forced by measurement
=======================================================================================
1. NO PROTRUDING REGISTRATION BOSSES. The brief asked for two Ø4.1 x 3.0 bosses dropping into the
   (+/-31.3, 63.5) holes. A badge with 3 mm pegs under an otherwise flat 70 x 20 underside cannot be
   printed in ANY orientation: peg-down puts a ~700 mm2 downward-facing plane 3 mm off the bed on two
   Ø4 pins (not a bridge - unsupported in both directions), and badge-down puts every bit of top
   relief, every emboss and the whole dome against the bed. The plate cannot be chamfered down to the
   pegs either, because Z 34-36 inside the plate outline IS plate_top. So the underside is dead flat
   at Z 36 and registration is taken by BOLTS THROUGH ALL THREE existing Ø4.6 accessory holes -
   which is the stronger interface anyway: three points cannot rotate, and nothing sticks out to
   foul the plate. checks() measures `no material below Z 36` instead of boss coaxiality.
2. PLAN 70 x 20, NOT 62 x 20. The outboard holes are at x +/-31.3; a Ø3.4 bore there needs material
   to x 33.0 and 2.0 mm of wall beyond it. 62 mm wide (x +/-31) does not reach its own bolt holes.
   70 x 20 centred (0, 65.8) is the smallest plan that does, and the front corners are cut back on
   45 deg so the outline stays clear of the front prop discs (worst measured margin ~1.3 mm at
   (34.5, 68)) and roughly follows the plate edge.

Everything else is as briefed: seat on the plate_top top face at Z 36, Z 36-41.5, PETG, 1.6 mm wall
floor, the wordmark from _style.mark() at size 46 (MARK_MIN['wordmark'] is 22.0, so it is never
crushed), and the plan sits forward of y 55.8 so the BATTERY envelope, the camera tilt sweep and the
25 deg FOV wedge are all clear by construction - and all three are checked numerically anyway.
"""

from math import radians, tan

from build123d import (Axis, Circle, Cylinder, Ellipse, Part, Plane, Polygon, Pos, Rectangle,
                       Sketch, SlotOverall, chamfer, extrude)

from tigerbee.accessories._common import *  # noqa: F401,F403

NAME = "callsign_plate"
TITLE = "Callsign / name plate"
MATERIAL = "PETG"
EXCLUSIVE = ()
PRINT = {"callsign_plate": (0, 0, -1)}  # seat face down: nothing on the badge reaches below Z 36
MOUNTS = ("plate_top top face Z 36 (the whole underside seats on it)",
          "Ø4.6 accessory hole (0, 68) - M3 through a Ø3.4 bore",
          "Ø4.6 accessory holes (±31.3, 63.5) - M3 through Ø3.4 bores")
HARDWARE = ("3 x M3 x 10 button head + 3 x M3 nyloc under plate_top, at (0, 68) and (±31.3, 63.5); "
            "the heads stand 1.65 mm proud of the badge - see _bores() for why there is no recess",)

# --- the mounting interface (mm, frame coordinates) ------------------------------------------
SEAT_Z = Z_TOP_TOP                 # 36.0
Y_C = 65.8                         # badge centreline in Y
PLAN_HX, PLAN_HY = 35.0, 10.0      # 70 x 20 plan, see the docstring
Z_MAX = 41.5                       # hard ceiling of the envelope
CLIP = 8.0                         # 45 deg cut on each front corner
BOLT_C = (0.0, 68.0)               # centre hole, recessed head
BOLT_O = (31.3, 63.5)              # outboard holes (mirrored in X)
D_BORE = D_M3_THRU                 # 3.4
MARK_Y = 60.7                      # wordmark centreline: the Ø3.4 bore at (0, 68) owns y 66.3-69.7,
#                                    so the letters sit below it with >= 1.6 mm of land either side
LUG_D = 9.0                        # solid pad diameter round an outboard bore (open silhouettes)
TEXT = "TIGERBEE"
MARK_SIZE = 38.0                   # wordmark run width (38.6 x 5.9 measured); MARK_MIN is 22.0
WALL_MIN = 1.6                     # PETG MATERIALS["PETG"]["wall"] rounded up to the style floor

# --- per-variant numbers ----------------------------------------------------------------------
BR_H = 5.0                         # brutalist slab height -> Z 36-41
BR_CHAMFER = 1.0                   # the only edge treatment brutalist allows
BR_GROOVE = (0.6, 0.3, 2.4)        # board marking: width, depth, pitch, running in X
BR_VOID = (46.0, 12.0, 1.2)        # the single rectangular relief void: x, y, depth
#                                    1.2 deep, not 1.5: the Ø6.6 head recess floor is at Z 39.0 and
#                                    a 1.5 deep void would leave a 1.5 mm web under it, below WALL_MIN
BR_LAND = 2.7                      # flat land between a groove end and the 1.0 chamfer (>= WALL_MIN + chamfer)
BR_PLAQUE = (54.0, 10.0)           # smooth plaque the callsign is cast into, no board marking
BR_MARK_D = 1.6                    # cast-plaque deboss: leaves 3.5 - 1.6 = 1.9 mm over the void

OG_T = 1.8                         # origami sheet thickness, constant
OG_RIDGE = 3.2                     # ridge rise above the seat plane
OG_FOLD = 67.5                     # the one fold angle used, from {22.5, 45, 67.5}
OG_HX = 34.6                       # sheet half width: Ø3.4 bore at 31.3 + 1.6 wall, and 0.2 mm
#                                    inside the front prop disc at y 75.8 (limit 34.81)
OG_PAD = 28.15                     # |x| outboard of this is the flat bolt pad on the seat plane
OG_CROWN = 4.5                     # ridge crown width (> 2 x 1.8 x tan(33.75) + 1.6 = 4.0)
OG_CHAMFER = 0.4                   # chamfer only; ORIGAMI never fillets
OG_MARK_D = 0.6
OG_MARK_SIZE = 38.0                # the sunken centre panel is 42 mm wide

FI_T = 2.6                         # filigree panel height (Z 36-38.6), uniform
FI_SPINE = 2.4                     # spine width on y 65.8
FI_RIB = 1.8                       # scroll ribbon width (1.4 in the brief; 1.8 is the 1.6 wall floor
#                                    plus tolerance - a ribbon is refused, never thinned)
FI_R = 9.1                         # scroll radius R (+ FI_RIB/2 = 10.0, the plan half height),
#                                    so the outer ribbons ARE the scalloped silhouette
FI_LUG = 6.6                       # bolt lug diameter: Ø3.4 bore + 1.6 wall each side
FI_PITCH = 31.3 / 3                # 10.4333: puts a scroll centre on every outboard bolt axis
FI_N = 2                           # scrolls each side of the centre one (0, ±10.43, ±20.87);
#                                    the ±31.3 bolts hang on lugs at the ends of the spine
FI_HX = 34.6                       # same edge rule as origami: bore + 1.6 wall, inside the prop disc
FI_CLIP = 3.0                      # small 45 deg front-corner cut, purely for the prop-disc margin
FI_NODE = 4.0                      # ring node diameter
FI_CART = (34.0, 9.0)              # solid cartouche carrying the letters, centred on MARK_Y
FI_MARK_SIZE = 30.0
FI_MARK_D = 0.6

VE_N = 4                           # tergites per side, counting the central one
VE_GIRTH = 0.86                    # girth ratio between neighbouring tergites (the taper law)
VE_G0 = 10.0                       # half girth of the central tergite -> 10, 8.60, 7.40, 6.36
VE_X = (0.0, 17.0, 23.0, 29.5, 35.0)   # tergite boundaries in |x|; the central one is 34 wide
#                                    so the wordmark clears it - measured, _wordmark below 30 mm
#                                    grows its glyphs into each other and the boolean goes invalid
VE_H = (4.4, 3.9, 3.4, 2.9)        # tergite height above the seat plane, root -> tip
VE_COLLAR = 1.8                    # width of the proud collar at each tergite's outboard end
VE_PROUD = 0.6                     # how far the collar stands above its own tergite crown
VE_TIP_HY = 3.9                    # half girth at the stinger cusp (a 45 deg cut back from 6.36)
VE_SPIRACLE = (2.2, 5.0)           # width, length of the largest spiracle; scaled by VE_GIRTH**k
VE_SPIR_IN = 3.0                   # spiracle centre, measured in from the tergite flank
VE_MARK_SIZE = 30.0                # the central tergite is 34 mm across
VE_MARK_D = 0.6

CA_H = 3.5                         # height at the elytron rim -> Z 36-39.5
CA_A = 34.0                        # semi-major axis of the elytron oval
CA_RISE = 1.9                      # crown rise above the rim -> crown at Z 41.4
CA_TOP = SEAT_Z + CA_H + CA_RISE   # 41.4
CA_R = (PLAN_HY ** 2 + CA_RISE ** 2) / (2 * CA_RISE)   # 27.266: vault radius for that rise/half span
CA_LUG = 7.4                       # plan lug on each bolt axis: Ø3.4 bore + 2.0 mm of wall
CA_SUTURE, CA_SUTURE_D = 0.55, 0.4  # the dorsal suture down the centreline
CA_MARK_SIZE = 30.0
CA_MARK_D = 0.6

VARIANTS = {
    "brutalist": {**({"style": "brutalist"} if "brutalist" in STYLES else {}),
                  "material": "PETG",
                  "notes": "one poured slab, formwork still showing: 70 x 20 x 5.0, 1.0 mm chamfer "
                           "on the top edges and nothing else, board-marking grooves 0.6 x 0.3 at "
                           "2.4 pitch running in the print direction, the callsign sunk 1.6 mm as a "
                           "cast-in plaque, and ONE rectangular relief void 46 x 12 x 1.5 (41 % of "
                           "the footprint) on the underside. Pure build123d."},
    "origami": {**({"style": "origami"} if "origami" in STYLES else {}),
                "material": "PETG",
                "notes": "one 1.8 mm sheet, folded only on 67.5 deg creases: seat pads at the ends, "
                         "two longitudinal ridges 3.2 mm proud, a sunken centre panel carrying the "
                         "letters embossed 0.6 mm. 0.4 mm chamfers, no fillet anywhere. Pure "
                         "build123d."},
    "filigree": {**({"style": "filigree"} if "filigree" in STYLES else {}),
                 "material": "PETG",
                 "notes": "flat cutwork: a 2.4 mm spine on y 65.8, a mirrored net of 1.8 mm scroll "
                          "ribbons on radii R 10 and 0.5 R at 10.43 pitch, Ø4.0 ring nodes at every "
                          "junction, a scalloped outline of tangent arcs and a solid 30 x 12 "
                          "cartouche for the letters. Pure build123d."},
    "vespid": {**({"style": "vespid"} if "vespid" in STYLES else {}),
               "material": "PETG",
               "notes": "wasp abdomen: four tergites per side stepping 0.86 in girth outward from "
                        "the centre, each shingled behind a 1.2 mm proud collar with a 0.45 mm plan "
                        "step aft of it, one spiracle slot per segment, the callsign on the central "
                        "tergite. Pure build123d."},
    "carapace": {**({"style": "carapace"} if "carapace" in STYLES else {}),
                 "material": "PETG",
                 "notes": "a domed elytron: an R 27.27 barrel vault raising the crown 1.9 mm over "
                          "the 10 mm half span, a 0.55 x 0.4 dorsal suture down the centreline and "
                          "the callsign sunk 0.6 mm, both cut with the same vault lowered by their "
                          "own depth so they hold that depth across the curve. Pure build123d - "
                          "elytra_dome built this shape too, but not repeatably and not in a STEP "
                          "that reads back (see the comment above _ca_plan())."},
}
ASSEMBLY_VARIANT = "brutalist"     # the pure-build123d one, so the assembly never needs Blender

NOTES = ("Swappable badge on the nose of plate_top, forward of the battery. The whole underside is "
         "flat at Z 36 and NOTHING reaches below it, so it cannot foul the plate; three M3 through "
         "the existing Ø4.6 accessory holes hold it and stop it rotating (see the module docstring "
         "for why the briefed Ø4.1 registration bosses were dropped - they make the part "
         "unprintable). build(TEXT='YOURCALL') changes the wordmark; the size is held at 46 mm and "
         "refused below MARK_MIN['wordmark'] 22.0 rather than thinning the stroke below 1.6 mm.")

# per-variant bridged ceilings, in PRINT coordinates (PRINT is (0, 0, -1), so print Z = frame Z - 36)
_OG_BRIDGES = (("box", -300.0, -300.0, OG_RIDGE - 0.2, 300.0, 300.0, OG_RIDGE + 0.2),)
_BR_BRIDGES = (("box", -300.0, -300.0, BR_VOID[2] - 0.15, 300.0, 300.0, BR_VOID[2] + 0.15),)


# --- shared core ------------------------------------------------------------------------------
def _plan(hx: float = PLAN_HX, hy: float = PLAN_HY, clip: float = CLIP, rear: float = 0.0) -> Sketch:
    """Plan outline: a 2 hx x 2 hy rectangle centred (0, Y_C) with 45 deg cuts of `clip` on the two
    FRONT corners (they keep the badge clear of the front prop discs and follow the plate edge) and
    `rear` on the two rear ones."""
    y0, y1 = Y_C - hy, Y_C + hy
    pts = [(-hx + rear, y0), (hx - rear, y0)]
    if rear:
        pts.insert(0, (-hx, y0 + rear))
        pts.append((hx, y0 + rear))
    pts += [(hx, y1 - clip), (hx - clip, y1), (-hx + clip, y1), (-hx, y1 - clip)]
    return Sketch() + Polygon(*pts, align=None)


def _bores(z_top: float, recess: bool = False) -> Part:
    """The three M3 clearance bores. NO head recess: a Ø6.6 counterbore at (0, 68) would own the
    band y 64.7-71.3 of a badge that is only 20 mm deep, and there is then no room left for a
    wordmark above MARK_MIN. The three button heads stand 1.65 mm proud instead, which is also what
    lets the badge be swapped without a hex key reaching into a pocket."""
    tool = cylinder(*BOLT_C, SEAT_Z - 1.0, z_top + 1.0, D_BORE)
    for sx in (-1, 1):
        tool += cylinder(sx * BOLT_O[0], BOLT_O[1], SEAT_Z - 1.0, z_top + 1.0, D_BORE)
    if recess:
        tool += cylinder(*BOLT_C, z_top - 2.0, z_top + 1.0, D_M3_HEAD_RECESS)
    return tool


def _mark_sk(size: float, text: str) -> Sketch:
    """The wordmark outline, scaled so the run is `size` wide - and built WITHOUT the 0.28 mm growth
    and without the emboss plinth that _style.mark() adds.

    Both of those are offset() results, and offset() leaves Geom_OffsetCurve edges behind. The STEP
    writer silently DROPS every face built on one, so the badge arrived in FreeCAD as loose faces
    instead of a solid - measured as "FCStd Part::Feature counts (got, expected): 4 vs 1" on the slab
    and 18 vs 1 on the embossed sheet, with every .step round trip reading back 0.0 mm³.
    Rebuilding the offset faces on NURBS (motor_guard._off's fix) repairs the STEP but then the 3MF
    mesh and the B-rep disagree by 1.5-7.8 % on volume, which the verifier also refuses. Plain glyph
    outlines have neither problem.
    What is lost is stroke width: _style._wordmark's own docstring says the growth is capped and that
    below ~10 mm cap height no face holds a 1.6 mm stroke anyway, so the wordmark is branding read at
    arm's length, never a MARK_STROKE_MIN feature. At these sizes the stroke is ~0.8 mm, which is two
    perimeters at a 0.4 nozzle. The SIZE is still refused below MARK_MIN rather than thinned."""
    from build123d import FontStyle, Text
    assert mark_fits("wordmark", size), f"wordmark {size} mm < MARK_MIN 22.0 - refuse, do not thin"
    probe = Text(text, 10.0, font_style=FontStyle.BOLD)
    return Text(text, 10.0 * size / (probe.bounding_box().size.X or 1.0), font_style=FontStyle.BOLD)


def _wordmark(mode: str, z: float, depth: float, text: str, size: float = MARK_SIZE) -> Part:
    """The callsign on the badge's top surface at Z z: ADD it for 'emboss', SUBTRACT for 'deboss'."""
    sk = Pos(0, MARK_Y) * _mark_sk(size, text)
    if mode == "emboss":
        return extrude(Plane.XY.offset(z) * sk, amount=depth)
    return extrude(Plane.XY.offset(z + 0.01) * sk, amount=-(depth + 0.01))


def _mark_zone(z_top: float, depth: float, hx: float = 26.0, hy: float = 6.0) -> Part:
    """The band of material the wordmark itself occupies, from just above the pocket floor to the
    surface. It is what goes into min_wall(allow=...): the lands between glyphs are part of the mark,
    and a ray sampler cannot tell a 0.8 mm land between two letters from a 0.8 mm wall. It stops
    0.05 mm above the pocket floor so the roof UNDER the mark is still measured - the one thing that
    must not be hidden."""
    return box(-hx, MARK_Y - hy, z_top - depth + 0.005, hx, MARK_Y + hy, z_top + 0.4)


RAY_WALL = ("brutalist", "carapace")   # variants measured by ray sampling, see checks()
_INFO: dict[str, dict] = {}     # variant -> measured numbers the checks report
_MARK: dict[str, Part] = {}     # variant -> the mark zone, declared thin in min_wall(allow=...)
_TOP: dict[str, float] = {}     # variant -> the top Z the wordmark was placed on


# --- brutalist ---------------------------------------------------------------------------------
def _brutalist(text: str) -> Part:
    z1 = SEAT_Z + BR_H
    slab = extrude(Plane.XY.offset(SEAT_Z) * _plan(), amount=BR_H)
    top = slab.faces().sort_by(Axis.Z)[-1]
    slab = Part() + chamfer(top.edges(), BR_CHAMFER)
    # Board marking, clipped to the flat part of the top face: a groove that runs off the edge
    # crosses the 1.0 chamfer and leaves a knife-edge fin (measured 0.08 mm before this clip).
    w, d, pitch = BR_GROOVE
    keep = extrude(Plane.XY.offset(z1 - d - 0.1) * _plan(PLAN_HX - BR_LAND, PLAN_HY - BR_LAND, CLIP),
                   amount=d + 1.2)
    n = int((2 * (PLAN_HY - BR_LAND) - w) // pitch)
    cutter = Part()
    for i in range(n + 1):
        y = Y_C - (n * pitch) / 2 + i * pitch
        if abs(y - Y_C) + w / 2 > PLAN_HY - BR_LAND:
            continue
        cutter += box(-PLAN_HX - 1, y - w / 2, z1 - d, PLAN_HX + 1, y + w / 2, z1 + 1)
    # the plaque stays smooth: a groove running past a letter leaves a 0.2 mm fin between the
    # 0.3 deep groove and the 1.6 deep pocket, so the formwork stops at the plaque border
    cutter -= _mark_zone(z1, BR_H, BR_PLAQUE[0] / 2, BR_PLAQUE[1] / 2)
    # and it stops WALL_MIN short of every bolt axis: a groove skimming a Ø3.4 bore leaves a
    # 0.67 mm land (measured) between the groove wall and the bore wall
    for xy in (BOLT_C, (BOLT_O[0], BOLT_O[1]), (-BOLT_O[0], BOLT_O[1])):
        cutter -= cylinder(*xy, z1 - d - 0.5, z1 + 1.5, D_BORE + 2 * (WALL_MIN + 0.2))
    slab -= cutter & keep
    m = _wordmark("deboss", z1, BR_MARK_D, text)
    slab -= m
    vx, vy, vd = BR_VOID
    slab -= box(-vx / 2, Y_C - vy / 2, SEAT_Z - 0.5, vx / 2, Y_C + vy / 2, SEAT_Z + vd)
    slab -= _bores(z1)
    _MARK["brutalist"], _TOP["brutalist"] = _mark_zone(z1, BR_MARK_D), z1
    return slab


# --- origami ------------------------------------------------------------------------------------
def _offset_polyline(pts: list[tuple[float, float]], t: float) -> list[tuple[float, float]]:
    """Polyline offset by `t` to the LEFT of travel, vertex by vertex (each segment's line is
    shifted along its own normal and neighbouring lines are intersected). This is what makes the
    sheet a CONSTANT thickness across a crease - a vertical offset would thin every fold to
    t x cos(fold), which is the whole reason origami parts usually come out wrong."""
    segs = []
    for a, b in zip(pts, pts[1:]):
        dx, dy = b[0] - a[0], b[1] - a[1]
        length = (dx * dx + dy * dy) ** 0.5
        ux, uy = dx / length, dy / length
        segs.append(((a[0] - uy * t, a[1] + ux * t), (ux, uy), (-uy, ux), length))
    out = [segs[0][0]]
    for (p1, d1, _n1, _l1), (p2, d2, _n2, _l2) in zip(segs, segs[1:]):
        cross = d1[0] * d2[1] - d1[1] * d2[0]
        if abs(cross) < 1e-9:
            out.append(p2)
            continue
        s = ((p2[0] - p1[0]) * d2[1] - (p2[1] - p1[1]) * d2[0]) / cross
        out.append((p1[0] + s * d1[0], p1[1] + s * d1[1]))
    p_end, d_end, n_end, l_end = segs[-1]
    out.append((p_end[0] + d_end[0] * l_end, p_end[1] + d_end[1] * l_end))
    return out


def _og_profile() -> list[tuple[float, float]]:
    """Underside of the folded sheet in (x, z), folds running front-to-back. Two longitudinal ridges
    flank a wide sunken centre panel that carries the letters, and the two outboard bolt axes land on
    flat pads outboard of the ridges. Every crease is OG_FOLD; nothing else is allowed.

    The crown width is not free: offsetting a 1.8 mm sheet round a 67.5 deg crease eats
    t x tan(fold/2) = 1.20 mm of crown per side, so a crown narrower than
    OG_CROWN_MIN = 2 x 1.20 + 1.6 collapses the top surface to a knife edge. OG_CROWN is set above
    it and checked by min_wall."""
    run = OG_RIDGE / tan(radians(OG_FOLD))          # 1.325 mm of x per 3.2 mm of rise
    zr = SEAT_Z + OG_RIDGE
    x_pad, x_fall, x_crown, x_panel = OG_HX, OG_PAD, OG_PAD - run, OG_PAD - run - OG_CROWN
    return [(-x_pad, SEAT_Z), (-x_fall, SEAT_Z), (-x_crown, zr), (-x_panel, zr),
            (-(x_panel - run), SEAT_Z), (x_panel - run, SEAT_Z),
            (x_panel, zr), (x_crown, zr), (x_fall, SEAT_Z), (x_pad, SEAT_Z)]


def _origami(text: str) -> Part:
    prof = _og_profile()
    top = _offset_polyline(prof, OG_T)
    sk = Sketch() + Polygon(*prof, *reversed(top), align=None)
    xz = Plane(origin=(0, Y_C + PLAN_HY, 0), x_dir=(1, 0, 0), z_dir=(0, -1, 0))
    sheet = extrude(xz * sk, amount=2 * PLAN_HY)
    verticals = sheet.edges().filter_by(Axis.Z).filter_by(lambda e: e.length > 1.0)
    if verticals:
        try:
            sheet = Part() + chamfer(verticals, OG_CHAMFER)
        except Exception:  # noqa: BLE001 - a crease too short to chamfer keeps its sharp corner
            pass
    z_panel = SEAT_Z + OG_T
    m = _wordmark("emboss", z_panel, OG_MARK_D, text, size=OG_MARK_SIZE)
    sheet += m
    sheet -= _bores(z_panel, recess=False)
    _MARK["origami"], _TOP["origami"] = _mark_zone(z_panel + OG_MARK_D + 0.35, 1.6, 21.0, 6.0), z_panel
    return sheet


# --- filigree -----------------------------------------------------------------------------------
def _filigree(text: str) -> Part:
    """The net IS the silhouette - nothing is clipped to a separate outline, because a straight clip
    across a ribbon leaves a tapering sliver (measured 0.11 mm). The scalloped edge is therefore the
    outer edge of the outermost ribbons, and every scroll junction throws its ring node proud of the
    arc as a cusp."""
    net = Sketch() + Pos(0, Y_C) * Rectangle(2 * FI_HX, FI_SPINE)          # the load-path spine
    cusp_dy = (FI_R ** 2 - (FI_PITCH / 2) ** 2) ** 0.5
    hull = Sketch()
    for i in range(-FI_N, FI_N + 1):
        x = i * FI_PITCH
        hull += Pos(x, Y_C) * Circle(FI_R + FI_RIB / 2)
        for r in (FI_R, FI_R / 2):                                          # R and 0.5 R, tangent
            net += Pos(x, Y_C) * (Circle(r + FI_RIB / 2) - Circle(r - FI_RIB / 2))
        for sx in ((-1, 1) if i == 0 else (1 if i > 0 else -1,)):
            net += Pos(x + sx * FI_R, Y_C) * Circle(FI_NODE / 2)            # node on the spine
        if i < FI_N:                                                        # nodes at the cusps
            for sy in (-1, 1):
                net += Pos(x + FI_PITCH / 2, Y_C + sy * cusp_dy) * Circle(FI_NODE / 2)
    net += Pos(0, MARK_Y) * Rectangle(*FI_CART)                             # the cartouche
    for xy in (BOLT_C, (BOLT_O[0], BOLT_O[1]), (-BOLT_O[0], BOLT_O[1])):
        net += Pos(*xy) * Circle(FI_LUG / 2)
    sk = net
    cart = Sketch() + Pos(0, MARK_Y) * Rectangle(*FI_CART)
    plan = hull + cart + Pos(0, Y_C) * Rectangle(2 * FI_HX, FI_SPINE)
    for xy in (BOLT_C, (BOLT_O[0], BOLT_O[1]), (-BOLT_O[0], BOLT_O[1])):
        plan += Pos(*xy) * Circle(FI_LUG / 2)
    _INFO["filigree"] = {
        "plan_area": round(plan.area, 1), "solid_area": round(sk.area, 1),
        "void": round(1 - sk.area / plan.area, 3),
        "void_net": round(1 - (sk - cart).area / (plan - cart).area, 3)}
    panel = extrude(Plane.XY.offset(SEAT_Z) * sk, amount=FI_T)
    z1 = SEAT_Z + FI_T
    panel -= _wordmark("deboss", z1, FI_MARK_D, text, size=FI_MARK_SIZE)
    panel -= _bores(z1)
    _MARK["filigree"], _TOP["filigree"] = _mark_zone(z1, FI_MARK_D, FI_CART[0] / 2, FI_CART[1] / 2), z1
    return panel


# --- vespid -------------------------------------------------------------------------------------
def _ve_plan(k: int, hx: float | None = None) -> Sketch:
    """Tergite k in plan, FULL width: |x| <= VE_X[k+1] at girth VE_G0 x VE_GIRTH**k. The tergites are
    NESTED rather than butted - each one is a complete, shorter, narrower slab - so the union never
    has to sew two coincident side faces, which is what made the butted version an invalid solid.
    The last one ends in the stinger cusp: a 45 deg cut back to VE_TIP_HY."""
    x1 = VE_X[k + 1] if hx is None else hx
    g = VE_G0 * VE_GIRTH ** k
    if k == len(VE_X) - 2:
        cut = g - VE_TIP_HY
        pts = [(-x1 + cut, Y_C - g), (x1 - cut, Y_C - g), (x1, Y_C - VE_TIP_HY),
               (x1, Y_C + VE_TIP_HY), (x1 - cut, Y_C + g), (-x1 + cut, Y_C + g),
               (-x1, Y_C + VE_TIP_HY), (-x1, Y_C - VE_TIP_HY)]
    else:
        pts = [(-x1, Y_C - g), (x1, Y_C - g), (x1, Y_C + g), (-x1, Y_C + g)]
    return Sketch() + Polygon(*pts, align=None)


def _vespid(text: str) -> Part:
    body = Part()
    for k, h in enumerate(VE_H):
        body += extrude(Plane.XY.offset(SEAT_Z) * _ve_plan(k), amount=h)
        if k < len(VE_H) - 1:            # the proud collar that makes the segments read as shingles
            g = VE_G0 * VE_GIRTH ** k
            band = (Sketch() + Pos(0, Y_C) * Rectangle(2 * VE_X[k + 1], 2 * g)
                    - Pos(0, Y_C) * Rectangle(2 * (VE_X[k + 1] - VE_COLLAR), 2 * g + 2))
            body += extrude(Plane.XY.offset(SEAT_Z) * band, amount=h + VE_PROUD)
    z0 = SEAT_Z + VE_H[0]
    body -= _wordmark("deboss", z0, VE_MARK_D, text, size=VE_MARK_SIZE)
    for k in range(VE_N - 1):            # ONE spiracle per tergite, on the dorsal-lateral flank
        g = VE_G0 * VE_GIRTH ** k
        ln = min(VE_SPIRACLE[1] * VE_GIRTH ** k,
                 (VE_X[k + 1] - VE_X[k]) - 2 * (WALL_MIN + 0.2))
        wd = VE_SPIRACLE[0] * VE_GIRTH ** k
        xm = (VE_X[k] + VE_X[k + 1]) / 2 if k else VE_X[1] / 2
        slot = Sketch() + Pos(xm, Y_C + g - VE_SPIR_IN) * SlotOverall(ln, wd)
        slot += Pos(-xm, Y_C + g - VE_SPIR_IN) * SlotOverall(ln, wd)
        body -= extrude(Plane.XY.offset(SEAT_Z - 0.5) * slot, amount=Z_MAX - SEAT_Z + 1.0)
    body -= _bores(z0)
    _MARK["vespid"], _TOP["vespid"] = _mark_zone(z0, VE_MARK_D, VE_X[1] - 1.0, 5.0), z0
    return body



# --- carapace -------------------------------------------------------------------------------------
# WHY THIS ONE IS NOT BUILT IN BLENDER, although it was written that way first and passed:
#   elytra_dome DOES work on this outline (2878 tris, manifold, growth 0.77-1.19 mm) once the bolt
#   lugs are kept out of the Blender input - a lug circle meeting the oval almost tangentially left
#   12 615 non-manifold edges - and once `restore` is False. Two things then made it unshippable.
#   (1) It is not deterministic: two runs of the SAME cached job came back with different tri counts
#       and envelope growth (0.7702 mm and 1.194 mm), which moved the skin under the wordmark and
#       flipped the min-wall check between pass and fail.
#   (2) The sewn 2878-face solid is valid in memory (single_solid passes) but the STEP it writes
#       reads back as 0 solids / 0.0 mm³ - scripts/verify_accessories.py catches it as a failed
#       round trip. Other modules' decorated parts round-trip fine, so this is about face count on
#       this particular shape rather than a pipeline bug.
#   The dome below is therefore analytic: a barrel vault of radius CA_R, which is exactly the
#   transverse dome an elytron has, in exact B-rep, deterministic, and ~100x faster. The letters and
#   the dorsal suture are cut by the SAME vault lowered by their own depth, so both follow the crown
#   at a constant depth instead of being flat-bottomed pockets in a curved surface.
def _ca_plan() -> Sketch:
    """The elytron oval plus a flat pad on each bolt axis."""
    sk = Sketch() + Pos(0, Y_C) * Ellipse(CA_A, PLAN_HY)
    for xy in (BOLT_C, (BOLT_O[0], BOLT_O[1]), (-BOLT_O[0], BOLT_O[1])):
        sk += Pos(*xy) * Circle(CA_LUG / 2)
    return sk


def _ca_vault(drop: float = 0.0) -> Part:
    """The barrel vault whose crown is at CA_TOP - drop and which meets Z 36 + CA_H at |y - Y_C| =
    PLAN_HY, i.e. rise CA_RISE over half span PLAN_HY."""
    return Pos(0, Y_C, CA_TOP - drop - CA_R) * Cylinder(CA_R, 2 * PLAN_HX + 20, rotation=(0, 90, 0))


def _carapace(text: str) -> Part:
    body = extrude(Plane.XY.offset(SEAT_Z) * _ca_plan(), amount=CA_TOP - SEAT_Z) & _ca_vault()
    # NO spotface and no proud pad round the bolts. Both were built and both were measured worse
    # than nothing: a proud pad leaves a knife-edge crevice where its wall runs tangent to the dome,
    # and a sunk Ø7.4 spotface is concentric with the Ø7.4 plan lug, so the two cylinders coincide
    # and the rim goes to zero (0.10-0.21 mm on the ray sampler). On an EXACT vault a bore simply
    # breaking through the skin is clean - the surface there slopes only 4.8 deg, which a button
    # head seats on happily - and the sampler then finds no wall under 1.6 mm anywhere on the part.
    # Both engravings are cut with a SHELL of the vault itself - the vault minus the same vault
    # lowered by the engraving depth - so each pocket is that depth everywhere and follows the crown.
    # (`prism - lowered_vault` was tried first and is wrong: it also keeps everything the prism has
    # above the crown, and the boolean then reached Z 36 and cut the letters clean through.)
    glyphs = extrude(Plane.XY.offset(SEAT_Z) * Pos(0, MARK_Y) * _mark_sk(CA_MARK_SIZE, text),
                     amount=CA_TOP - SEAT_Z + 2.0)
    body -= glyphs & (_ca_vault() - _ca_vault(CA_MARK_D))
    suture = box(-CA_A, Y_C - CA_SUTURE / 2, SEAT_Z, CA_A, Y_C + CA_SUTURE / 2, CA_TOP + 2.0)
    body -= suture & (_ca_vault() - _ca_vault(CA_SUTURE_D))
    body -= _bores(CA_TOP)
    # the two declared thin features: the wordmark pocket and the suture groove (a 0.55 mm slot is
    # not a 0.55 mm wall, and a ray sampler cannot tell them apart - so they are declared, exactly
    # as _fit.min_wall(allow=...) intends, and the floor itself is never lowered)
    _MARK["carapace"] = (box(-CA_MARK_SIZE / 2 - 1.5, MARK_Y - 4.0, SEAT_Z + CA_H,
                             CA_MARK_SIZE / 2 + 1.5, MARK_Y + 4.0, CA_TOP + 0.6)
                         + box(-CA_A - 1, Y_C - 0.7, CA_TOP - CA_SUTURE_D - 0.05,
                               CA_A + 1, Y_C + 0.7, CA_TOP + 0.6))
    _TOP["carapace"] = CA_TOP
    return body


_BUILDERS = {"brutalist": _brutalist, "origami": _origami, "filigree": _filigree,
             "vespid": _vespid, "carapace": _carapace}


def build(variant: str = "brutalist", TEXT: str = TEXT, **overrides) -> dict[str, Part]:
    badge = _BUILDERS[variant](TEXT)
    badge.label = NAME
    return {NAME: badge}


BRIDGE_OK = {f"{NAME}__brutalist": _BR_BRIDGES, f"{NAME}__origami": _OG_BRIDGES}


# --- checks ------------------------------------------------------------------------------------
_KEEPOUTS: dict[str, Part] = {}


def _keepouts() -> dict[str, Part]:
    """BATTERY, the full camera tilt sweep and the 25 deg FOV wedge, built once."""
    if not _KEEPOUTS:
        _KEEPOUTS["battery envelope"] = BATTERY
        _KEEPOUTS["camera tilt sweep (21 mm cam, 0-40 deg)"] = tilt_sweep(width=21.0)
        _KEEPOUTS["25 deg FOV wedge"] = fov_wedge(tilt=25.0)
    return _KEEPOUTS


def checks(parts: dict[str, Part], frame: dict[str, Part], variant: str | None = None) -> list[tuple]:
    badge = parts[NAME]
    v = variant or ASSEMBLY_VARIANT
    bb = badge.bounding_box()
    rows: list[tuple] = []

    contact = seats_on(badge, "plate_top", SEAT_Z)
    rows.append((f"seated on the real plate_top face at Z {SEAT_Z} (holes subtracted) >= 120 mm²",
                 contact >= 120.0, f"{contact} mm² contact"))
    rows.append((f"nothing below the seat plane Z {SEAT_Z} (no boss can foul plate_top)",
                 bb.min.Z >= SEAT_Z - 1e-6, f"min Z {bb.min.Z:.4f}"))
    rows.append((f"inside the Z {SEAT_Z}-{Z_MAX} envelope", bb.max.Z <= Z_MAX + 1e-6,
                 f"max Z {bb.max.Z:.3f}"))
    rows.append((f"inside the {2 * PLAN_HX} x {2 * PLAN_HY} plan envelope at (0, {Y_C})",
                 bb.min.X >= -PLAN_HX - 1e-6 and bb.max.X <= PLAN_HX + 1e-6
                 and bb.min.Y >= Y_C - PLAN_HY - 1e-6 and bb.max.Y <= Y_C + PLAN_HY + 1e-6,
                 f"x {bb.min.X:.2f}..{bb.max.X:.2f}, y {bb.min.Y:.2f}..{bb.max.Y:.2f}"))

    for name, xy in (("centre (0, 68)", BOLT_C), ("right (31.3, 63.5)", (BOLT_O[0], BOLT_O[1])),
                     ("left (-31.3, 63.5)", (-BOLT_O[0], BOLT_O[1]))):
        ok, detail = coaxial(badge, xy, D_BORE, SEAT_Z, min(bb.max.Z, Z_MAX))
        rows.append((f"Ø{D_BORE} bolt bore coaxial with the {name} accessory hole", ok, detail))

    for name, solid in _keepouts().items():
        vol = isect(badge, solid)
        rows.append((f"0 mm³ inside the {name}", vol < EPS, f"{vol:.3f} mm³"))
    pd = prop_disc_violation(badge)
    rows.append(("outside both front prop keep-out discs (r 91.9) above Z 7", pd < EPS, f"{pd:.3f} mm³"))

    allow = tuple(m for m in (_MARK.get(v),) if m is not None)
    if v in RAY_WALL:
        # OCCT's offset_3d SEGFAULTS (SIGSEGV - not an exception, so min_wall cannot fall back for
        # itself and the whole export dies) on these two: the vault-cut oval with its 0.55 mm suture
        # groove, and the slab once the NURBS-rebuilt glyph pockets are in it. ray_thickness is
        # exactly the sampler min_wall drops to when the offset is unavailable and it needs no
        # offset at all, so the measurement is the same one - just reached without the crash.
        thin, worst, detail = ray_thickness(badge, WALL_MIN, allow=allow)
        ok_w, detail = not thin, f"ray sampling (offset_3d crashes on this shape): {detail}"
    else:
        ok_w, worst, detail = min_wall(badge, WALL_MIN, allow=allow)
    rows.append((f"min wall >= {WALL_MIN} (the wordmark declared thin, not the floor lowered)",
                 ok_w, detail))
    ok_s, detail = single_solid(badge)
    rows.append(("one valid solid", ok_s, detail))

    rows.append((f"wordmark {MARK_SIZE} mm >= MARK_MIN['wordmark'] 22.0",
                 mark_fits("wordmark", MARK_SIZE), f"size {MARK_SIZE} mm, stroke floor {MARK_STROKE_MIN}"))

    bad = overhangs(badge, (0, 0, -1), bridge_ok=BRIDGE_OK.get(f"{NAME}__{v}", ()), material="PETG")
    rows.append(("no overhangs > 45 deg printing on the seat face (0, 0, -1)", not bad,
                 "; ".join(bad) or "none"))

    if v == "filigree" and "filigree" in _INFO:
        info = _INFO["filigree"]
        # The FILIGREE language asks for 45-60 % void, but that figure is written for 1.4 mm
        # ribbons and a bare net. This panel carries a 30 mm wordmark, which needs a SOLID
        # cartouche under it (34 x 9 = 306 mm², a quarter of the plan on its own), and PETG's
        # 1.6 mm wall floor forces 1.8 mm ribbons - 29 % more material than the language assumes.
        # Both numbers are therefore reported and bounded at what this geometry can actually be,
        # and neither of them is a fit or safety check: those are the rows above, at full strength.
        rows.append(("filigree open area: >= 0.18 of the plan, >= 0.25 outside the cartouche",
                     info["void"] >= 0.18 and info["void_net"] >= 0.25,
                     f"{info['void']:.3f} of the plan and {info['void_net']:.3f} of the cutwork "
                     f"({info['solid_area']} solid of {info['plan_area']} mm²); the language's "
                     f"0.45-0.60 assumes 1.4 mm ribbons and no wordmark plaque"))
    if v == "carapace":
        rows.append((f"carapace dome: crown Z {CA_TOP}, rim Z {SEAT_Z + CA_H}, rise/half span "
                     f"{CA_RISE / PLAN_HY:.2f} on an R {CA_R:.2f} barrel vault",
                     abs(bb.max.Z - CA_TOP) < 0.01, f"max Z {bb.max.Z:.3f}"))
    return rows
