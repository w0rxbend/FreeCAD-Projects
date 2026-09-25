"""FC/ESC side protection panels between plate_mid and plate_top: dirt guard, crash bumper,
vents, USB window and lead notches, clipped onto the two arm-root standoffs of each side."""

from build123d import (Axis, Circle, Location, Part, Plane, Polygon, Pos, Rectangle, Sketch,
                       extrude, fillet)

from tigerbee.accessories import _blender as BL   # noqa: F401 - checks() reports the decor rows
from tigerbee.accessories import _style as S
from tigerbee.accessories._common import *  # noqa: F401,F403 - constants, builders and checks

NAME = "side_panels"
TITLE = "FC/ESC side panels"
MATERIAL = "PETG"
PRINT = {"side_panel_right": (0, 0, -1), "side_panel_left": (0, 0, -1)}
EXCLUSIVE = ()
MOUNTS = ("standoff_front_arm_right / _left Ø6 shafts (±28.528, 31.831), C-clip bores Z 9-33.8",
          "standoff_rear_arm_right / _left Ø6 shafts (±26.070, -33.373), C-clip bores Z 9-21.5",
          "plate_mid top face Z 9 (the wall's seating face)",
          "plate_top side tabs, underside Z 34 (anti-lift stop, 0.2 mm clearance)")
HARDWARE = ("none - 0.6 mm snap fit onto the two arm-root standoffs, pushed inboard",)

# --- style variants (the reference implementation of the VARIANTS contract in _template.py) -------
# Two genuinely different readings of the same panel, both bolted to the same two arm-root standoffs
# and both passing the same checks() unchanged:
#   shard     the stock faceted look - flat panel, the proven 60 deg louvre bank (45 deg flanks
#             exceed the overhang limit). Pure build123d.
#   carapace  an elytral flank - a row of upright cusped elytra slits in place of the louvre bank,
#             each one a lens whose ends are true tangent-arc points. Also pure build123d.
#
# BOTH ARE PURE build123d, and that is a measured decision, not an oversight. Every Blender recipe was
# tried on this part and every one of them was REFUSED by a gate - which is the bridge working, not
# failing. The findings, because they tell the other accessories where the recipes do belong:
#   elytra_dome  a 1.5 mm wall perforated by the USB window, two notches and the aperture bank has
#                almost no skin more than 1 mm from a rim, so a swell of 0.8 to 2.2 mm either pinched
#                a 0.02-0.03 mm fold at the USB corner or broke the re-boolean (59 solids at rise 1.2).
#   hardshell    reaches a valid, boolean-exact solid (779 faces, bores still coaxial, seat area
#                intact) and then fails the export gate: lib3mf rejects the re-triangulated sewn
#                solid. Welding to 1e-4, collinear decimation, sewing to 2e-2 and
#                ShapeUpgrade_UnifySameDomain were each measured and none of them fixes it.
#   carapace_lattice / chitin  both work cleanly on a PLATE-LIKE part - a voronoi field on a 60 x 24
#                plate measures a 1.7954 mm ligament against a 1.8 target, keeps its bores coaxial and
#                passes the export gate - and both leave non-manifold edges or an unsewable shell on
#                this part's clips, mouths and webs.
# So the Blender families belong on the thick, closed, plate-like parts: the battery_pad cover,
# tail_block, motor_guard, a canopy. Decorate a SIMPLE sub-solid and let CAD reassemble around it.
# Mirrored pair, so neither carries a suture: the pair IS the split (CN-1).
VARIANTS = {
    "shard": {"style": "shard",
              "notes": "the 60 deg louvre bank, slanted because 45 deg flanks exceed the overhang "
                       "limit. Carries no mark - see the MARK note; the wall has no free surface."},
    "carapace": {"style": "carapace", "material": "PETG",
                 "notes": "a row of upright cusped elytra slits instead of the louvre bank - each a "
                          "lens, two tangent arcs meeting at a true point at both ends. Upright so "
                          "the cusp is the only ceiling, which needs no bridge declaration."},
}
ASSEMBLY_VARIANT = "shard"
NOTES = ("Hold the panel ~8 mm outboard of its seat and push it INBOARD: both C-clip mouths face -X, "
         "so the standoffs enter from the inboard side and a side impact loads the closed outboard half "
         "of each ring instead of walking the standoffs out through the mouths. The bottom notches pass "
         "over the inner arm-clamp nyloc nuts during that stroke and double as capacitor/XT60 lead exits. "
         "Each web meets its ring on one side of the mouth only, so the opposite lip is a free 200 deg "
         "arc and takes the 0.6 mm snap over ~15 mm of curved beam (front: upper lip; rear: lower lip). "
         "The wall top (33.8) sits 0.2 under the plate_top side tabs, which are the anti-lift stop; the "
         "rear clip stops at Z 21.5 so xt60_holder can take Z 22-33.8. "
         "Deviations from the spec sheet, all measured in checks(): mouths face -X, not +X (the spec's own "
         "INSTALLATION paragraph, its +X nut sweep and the notches all describe an inboard stroke, which a "
         "+X mouth cannot perform); the spec's front neck probe at (24, 29.5) therefore lands in the mouth "
         "throat and is checked as open, with the real neck probed at (24, 27); the clip lips are squared "
         "off to a uniform 1.6 mm instead of tapering to a knife edge on the bore circle, so no min-wall "
         "allowance is needed; vents are slanted 60 deg (45 deg flanks exceed the overhang limit) in a "
         "Z 22-32 band clear of the USB window; the flat USB lintel is declared a bridge.")

# --- parameters (mm) ------------------------------------------------------------------------
WALL_MIN = 1.5                                  # PETG floor; the min-wall threshold
WALL = 1.5 if MATERIAL == "PETG" else 1.6
X_OUT = 23.0                                    # outer face of the wall
X_IN = X_OUT - WALL                             # 21.5, inboard face
Z_BOT = Z_MID_TOP                               # 9.0, seats on the plate_mid top face
Z_TOP_PANEL = 33.8                              # 0.2 under the plate_top tabs
REAR_CLIP_H = 12.5                              # Z 9.0-21.5; Z 22-33.8 belongs to xt60_holder
SNAP = MATERIALS[MATERIAL]["snap"]              # 0.6 PETG / 0.8 TPU
MOUTH = STANDOFF_D - SNAP                       # 5.4 throat over a Ø6 standoff
R_OUT = D_CLIP_BORE / 2 + CLIP_WALL             # 4.85
LIP_Y = MOUTH / 2 + CLIP_WALL                   # 4.3: squared lip flanks, uniform CLIP_WALL thick
MOUTH_REACH = R_OUT + 0.4                       # mouth cut length from the ring centre
WALL_Y = (-29.0, 28.0)                          # the plain wall; the webs carry it further fore/aft
FILLET_2D = 1.0
FILLET_LIP = MOUTH_FILLET                       # 0.45 on every lip tip corner

# Webs: (inboard-side limit, outboard-side limit). Each one runs from the wall to past the ring
# centre and stops flush with the mouth floor/ceiling, so the union leaves no crevice and no web
# material can sit in the throat. The bores and mouths are cut after the union.
FRONT_WEB = (25.0, 30.0)                        # y0, x1  (top edge = front mouth floor)
REAR_WEB = (-26.0, 28.0)                        # y1, x1  (bottom edge = rear mouth ceiling)

NOTCH_H = 8.0                                   # Z 9-17: nut (6.35 across corners x 4) + bolt tip
NOTCHES = ((14.5, 22.0), (-23.5, -16.0))        # y windows over the inner arm-clamp bolts

USB = True
USB_Y, USB_W, USB_H, USB_Z = 0.0, 12.0, 9.0, 17.0   # flat 12 mm lintel: a PETG bridge, not an arch

VENT = True
VENT_W, VENT_L, VENT_ANGLE, VENT_Z = 3.0, 11.0, 60.0, 27.0
VENT_YS = (-22.0, -16.0, -10.0, 10.0, 16.0, 22.0)   # 6 mm pitch -> 2.2 mm ligaments across the slots

# CARAPACE apertures and accent (see _elytra / _carina / _mark)
# The only band of this wall clear of both the USB window (Z 12.5-21.5, plus its 2.4 mm keep-out) and
# the arm-clamp notches (Z 8-17) is Z 22.6-33.4, the same band the shard louvres use. Its 10.8 mm
# carries exactly two slots, and the budget is worth writing down because the ARC'S OWN BULGE counts:
#   (n-1) x pitch + width + 2 x ligament + sagitta  <=  10.8
#   3.8           + 2.0   + 3.2          + 1.8      =   10.8
# At pitch 5.2 / width 2.6 / ligament 1.8 the budget is 0.6 mm over, and vent_elytra drops BOTH slots
# rather than shrinking them - a correct refusal, and how these numbers were found. The ligament is
# PETG's floor of 1.6 rather than scale_features' suggested 0.45 x pitch, because the band is what it
# is; 1.8 mm survives between the two slots.
ELYTRA_Z = (22.6, 33.4)                             # the band, see _elytra
ELYTRA_PITCH, ELYTRA_W = 4.8, 2.4                   # 2.4 mm ligament between slits, above PETG's 1.6
ELYTRA_LIG = 1.6                                    # PETG's minimum ligament (DECOR_MATERIALS)
# NO MARK by default, and the reason is the design language's own rule: "if no surface can hold the
# mark at its minimum size, the part carries no mark - a crushed mark is worse than none". Every
# square millimetre of this wall is taken: the USB window owns Z 12.5-21.5 at y +-6, the two
# arm-clamp notches own Z 8-17, and the aperture bank owns Z 22-33. The widest clear run left is
# 0.5 mm between two louvres. MARK=True is kept as a worked example of the carina-band technique -
# a 0.6 mm deboss into a 1.5 mm wall leaves 0.9 mm and fails `min wall >= 1.5` with worst 0.65 mm,
# so the mark goes into a band MARK_PAD proud (CN-5's thickness gradient), not into the wall itself.
MARK = False
MARK_Z = 13.8                                       # the mark band, clear of the USB window and vents
BAND_H = 12.0                                       # carina band height, the mark plus 1.5 margin
MARK_PAD = 0.9                                      # band proud of the wall, so a 0.6 deboss leaves 1.8
MARK_RAMP = 1.2                                     # >= 1.02 x MARK_PAD or the ramp is an overhang
APERTURE_COLLAR = 1.0                               # skin held back from every aperture rim (see _guard)
DECOR_SKIN = 0.9                                    # outer skin thickness Blender may move (see _guard)

INNER_CLAMP_XY = (P.place(*P.root_holes()[1], P.ARM_PLACEMENTS["arm_front_right"]),
                  P.place(*P.root_holes()[1], P.ARM_PLACEMENTS["arm_rear_right"]))
NUT_ACROSS_CORNERS, NUT_H, BOLT_TIP_D, BOLT_TIP_H = 6.35, 4.0, 4.0, 4.0
SLIDE_ON = 6.0                                  # install stroke the nut sweep must stay clear over

_FY_TOP = FRONT_ARM_XY[1] - MOUTH / 2           # 29.131, front mouth floor
_RY_BOT = REAR_ARM_XY[1] + MOUTH / 2            # -30.673, rear mouth ceiling
_NECK_FRONT = (24.0, 27.0)                      # real front neck (the spec point is in the throat)
_NECK_REAR = (23.5, -28.5)

# Downward faces that are bridges between two supported ends, in PRINT coordinates
# (PRINT is (0,0,-1), so print xy = frame xy minus the bbox centre and print z = frame z - 9).
_DX = -(REAR_ARM_XY[0] - R_OUT + FRONT_ARM_XY[0] + R_OUT) / 2
_DY = -(REAR_ARM_XY[1] - R_OUT + FRONT_ARM_XY[1] + R_OUT) / 2
_BRIDGES = (*(("box", -60.0, y0 + _DY - 0.6, NOTCH_H - 0.6, 60.0, y1 + _DY + 0.6, NOTCH_H + 0.6)
              for y0, y1 in NOTCHES),
            ("box", -60.0, USB_Y - USB_W / 2 + _DY - 0.6, USB_Z + USB_H / 2 - Z_BOT - 0.6,
             60.0, USB_Y + USB_W / 2 + _DY + 0.6, USB_Z + USB_H / 2 - Z_BOT + 0.6))
# The carapace slits need NO extra bridge: standing upright, their only ceiling is the cusp, which is
# two steep arcs meeting at a point. That is the whole reason they stand upright (see _elytra).
BRIDGE_OK = {"side_panel_right": _BRIDGES, "side_panel_left": _BRIDGES}


# --- 2D helpers -----------------------------------------------------------------------------
def _rect(x0, y0, x1, y1) -> Sketch:
    return Pos((x0 + x1) / 2, (y0 + y1) / 2) * Rectangle(x1 - x0, y1 - y0)


def _slot(length: float, width: float, angle: float = 0.0) -> Sketch:
    """Stadium of overall `length` x `width`, rotated by `angle` in the sketch plane."""
    straight = length - width
    sk = (Rectangle(straight, width) + Pos(-straight / 2, 0) * Circle(width / 2)
          + Pos(straight / 2, 0) * Circle(width / 2))
    return sk.rotate(Axis.Z, angle) if angle else sk


def _round(sk: Sketch, corners) -> tuple[Sketch, int]:
    """Fillet every listed (x, y, r) that is still a vertex of the profile; corners swallowed by
    a later union are skipped. Returns the count applied so checks() can see one went missing."""
    done = 0
    for cx, cy, r in corners:
        hits = sk.vertices().filter_by(
            lambda v, cx=cx, cy=cy: abs(v.X - cx) < 1e-4 and abs(v.Y - cy) < 1e-4)
        if hits:
            sk = fillet(hits, r)
            done += 1
    return sk, done


def _lip_reach(cx: float) -> float:
    """Inboard end of a clip's squared lips: R_OUT from the axis, but never inboard of the wall."""
    return max(cx - R_OUT, X_IN)


def _plan(p: dict) -> tuple[Sketch, int]:
    """Plan view: wall + both webs + both full clip rings (circle plus a squared lip block on the
    inboard side), then the Ø6.5 bores and the -X mouths. Cutting the rings only after the union
    keeps every bore free of web material; the squared block keeps both lips CLIP_WALL thick
    instead of letting them taper into the bore circle."""
    mouth, lip = p["MOUTH"] / 2, p["MOUTH"] / 2 + CLIP_WALL
    fy_top, ry_bot = FRONT_ARM_XY[1] - mouth, REAR_ARM_XY[1] + mouth
    fx1, ry1, rx1 = FRONT_WEB[1], REAR_WEB[0], REAR_WEB[1]

    sk = (_rect(X_IN, WALL_Y[0], p["X_OUT"], WALL_Y[1])
          + _rect(X_IN, FRONT_WEB[0], fx1, fy_top)
          + _rect(X_IN, ry_bot, rx1, ry1))
    for cx, cy in (FRONT_ARM_XY, REAR_ARM_XY):
        sk += Pos(cx, cy) * Circle(R_OUT) + _rect(_lip_reach(cx), cy - lip, cx, cy + lip)

    # where each web's outboard edge runs into the ring circle
    fy_cross = FRONT_ARM_XY[1] - (R_OUT ** 2 - (fx1 - FRONT_ARM_XY[0]) ** 2) ** 0.5
    ry_cross = REAR_ARM_XY[1] + (R_OUT ** 2 - (rx1 - REAR_ARM_XY[0]) ** 2) ** 0.5
    sk, n = _round(sk, [(p["X_OUT"], FRONT_WEB[0], FILLET_2D), (fx1, FRONT_WEB[0], FILLET_2D),
                        (fx1, fy_cross, FILLET_2D), (X_IN, fy_top, FILLET_2D),
                        (p["X_OUT"], ry1, FILLET_2D), (rx1, ry1, FILLET_2D),
                        (rx1, ry_cross, FILLET_2D),
                        (_lip_reach(FRONT_ARM_XY[0]), FRONT_ARM_XY[1] + lip, FILLET_LIP),
                        (_lip_reach(REAR_ARM_XY[0]), REAR_ARM_XY[1] - lip, FILLET_LIP)])

    for cx, cy in (FRONT_ARM_XY, REAR_ARM_XY):
        sk -= Pos(cx, cy) * Circle(D_CLIP_BORE / 2)
        sk -= _rect(cx - MOUTH_REACH, cy - mouth, cx, cy + mouth)
    sk, n2 = _round(sk, [(_lip_reach(cx), cy + s * mouth, FILLET_LIP)
                         for cx, cy in (FRONT_ARM_XY, REAR_ARM_XY) for s in (1, -1)])
    return sk, n + n2


# The undecorated functional solid of the last build of each variant. `min_wall` erodes and dilates,
# and OCCT's offset_3d returns an EMPTY shape on a solid made of ~1000 planar triangle faces: on a
# mesh-derived part erode() collapses to 0 mm3, min_wall silently drops to its ray fallback and costs
# tens of seconds, and what it then reports is not a wall measurement. So the CAD min-wall check runs
# on the functional solid, where it is valid, and the decorated mesh is measured by rays inside
# Blender instead (the "decor: mesh wall" row). Two checks, both of which must pass - not one relaxed.
_BASE: dict[str, Part] = {}


def _keepouts(p: dict) -> list[Sketch]:
    """The clean zones no generated aperture may touch, in the wall's own (Y, Z) sketch: the USB
    window and both arm-clamp notches, each with 2.4 mm of ligament round it."""
    return [_rect(p["USB_Y"] - p["USB_W"] / 2 - 2.4, p["USB_Z"] - p["USB_H"] / 2 - 2.4,
                  p["USB_Y"] + p["USB_W"] / 2 + 2.4, p["USB_Z"] + p["USB_H"] / 2 + 2.4)] + \
           [_rect(y0 - 2.4, Z_BOT - 1, y1 + 2.4, Z_BOT + p["NOTCH_H"] + 2.4) for y0, y1 in NOTCHES]


def _carina(p: dict) -> Part:
    """The band the mark is debossed into - the lateral carina, and the reason the mark is legal.

    A 0.6 mm deboss (CN-4: exactly 3 layers at 0.2) into a 1.5 mm PETG wall leaves 0.9 mm, under the
    material floor - measured as `min wall >= 1.5` failing with worst 0.65 mm. The answer is CN-5's
    thickness gradient, not a shallower mark: a band MARK_PAD proud raises the local wall to
    1.5 + 0.9 = 2.4, so the debossed residual is 1.8.

    Both edges ramp outward over MARK_RAMP. The ramp must be LONGER than the band is proud: a 45 deg
    ramp has normal.Z -0.7071, just past overhangs()' -0.70 limit, so run > 1.02 x proud is the real
    constraint and MARK_RAMP is 1.33 x it."""
    z0, z1 = p["MARK_Z"] - p["BAND_H"] / 2, p["MARK_Z"] + p["BAND_H"] / 2
    x0, x1 = p["X_OUT"], p["X_OUT"] + MARK_PAD
    prof = Polygon((x0, z0 - MARK_RAMP), (x1, z0), (x1, z1), (x0, z1 + MARK_RAMP), align=None)
    xz = Plane(origin=(0, WALL_Y[0], 0), x_dir=(1, 0, 0), z_dir=(0, -1, 0))
    return extrude(xz * prof, amount=WALL_Y[1] - WALL_Y[0])


def _wall_region(p: dict, z: tuple | None = None) -> Sketch:
    """The decoratable area of the wall, sketched in (frame Y, frame Z) exactly as _windows() is.
    It is the plain wall only - the webs and clip rings are structure and are never decorated."""
    z0, z1 = z or (Z_BOT, p["Z_TOP_PANEL"])
    return _rect(WALL_Y[0], z0, WALL_Y[1], z1)


def _elytra(p: dict, clean: list[Sketch] | tuple = ()) -> tuple[Sketch, int]:
    """CARAPACE apertures: a row of VERTICAL cusped slits up the flank - punctation drawn out into
    slits, which is what an elytron actually looks like close up.

    Each slit is a lens (_style.lens): two tangent arcs meeting at a true point at each end, CN-3
    executed literally. Vertical is the whole trick, and it is a printability argument, not a taste
    one. Printed with frame Z up, a slit running along Y has a horizontal ceiling - an overhang - and
    worse, `vent_elytra`'s arc makes that ceiling a CYLINDER of ~1000 mm diameter, which overhangs()
    will not accept as a bridge at all (bridge_ok only exempts planar faces, and the arch exemption
    stops at Ø12 for PETG). Measured: 39.1 mm2 of cylinder, 100 % facing down, three times over.
    Turn the same slit upright and its only ceiling is the cusp itself - two steep arcs meeting at a
    point - so it needs no bridge declaration and no exemption.

    The band is the one strip of this wall clear of the USB window and the notches (ELYTRA_Z)."""
    z0, z1 = p["ELYTRA_Z"]
    length = (z1 - z0) - 2 * ELYTRA_LIG
    half = min(p["ELYTRA_W"] / 2, 0.45 * length)     # a lens cannot be wider than half its length
    zc = (z0 + z1) / 2

    def slit(cy, _unused, grow):
        return S.lens((cy, zc - length / 2 - grow), (cy, zc + length / 2 + grow), half + grow)

    region = _wall_region(p, p["ELYTRA_Z"])
    pitch = p["ELYTRA_PITCH"]
    n = int((WALL_Y[1] - WALL_Y[0]) / pitch) + 2
    centres = [(WALL_Y[0] + (WALL_Y[1] - WALL_Y[0]) / 2 + (i - n / 2) * pitch, 0.0) for i in range(n + 1)]
    return S.place_apertures(region, slit, centres, ligament_min=ELYTRA_LIG, clean=clean,
                             pairwise=True, min_dim=2 * half, hole_min=2.0)


def _mark(p: dict, kind: str, mode: str = "deboss") -> Part | None:
    """The style's accent on the wall's outer face (+X), the largest uninterrupted planar surface on
    the part. Returns None when the face cannot hold the mark at its minimum size - a crushed mark is
    worse than none (§4.3). Mirrored for the left panel by pair(), never rotated."""
    size = S.clamp(0.38 * (WALL_Y[1] - WALL_Y[0]), 8.0, 34.0)
    if not S.mark_fits(kind, size):
        return None
    # local +X of the mark's plane runs along frame -Y so the sickle's thick end is outboard-forward
    return S.mark(kind, size, mode, (p["X_OUT"] + MARK_PAD, (WALL_Y[0] + WALL_Y[1]) / 2, p["MARK_Z"]),
                  normal=(1, 0, 0), x_dir=(0, 1, 0))


def _windows(p: dict) -> Sketch | None:
    """Openings cut through the wall, sketched in (frame Y, frame Z) on Plane.YZ."""
    sk = Sketch()
    if p["USB"]:
        y0, y1 = p["USB_Y"] - p["USB_W"] / 2, p["USB_Y"] + p["USB_W"] / 2
        z0, z1 = p["USB_Z"] - p["USB_H"] / 2, p["USB_Z"] + p["USB_H"] / 2
        win = _rect(y0, z0, y1, z1)
        win, _ = _round(win, [(y, z, FILLET_2D) for y in (y0, y1) for z in (z0, z1)])
        sk += win
    for y0, y1 in NOTCHES:
        notch = _rect(y0, Z_BOT - 1.0, y1, Z_BOT + p["NOTCH_H"])
        notch, _ = _round(notch, [(y, Z_BOT + p["NOTCH_H"], FILLET_2D) for y in (y0, y1)])
        sk += notch
    if p["VENT"]:
        sk += [Pos(yc, VENT_Z) * _slot(VENT_L, VENT_W, VENT_ANGLE) for yc in VENT_YS]
    return sk if sk.faces() else None


def _lip_probe(cx: float, cy: float, side: int, z0: float, z1: float) -> Part:
    """Slab occupying one snap lip's full CLIP_WALL cross-section, clear of the bore. Solid
    everywhere = the lip is a parallel 1.6 mm slab, not a wedge tapering onto the bore circle."""
    y0 = cy + side * MOUTH / 2
    return box(_lip_reach(cx) + 0.5, min(y0, y0 + side * CLIP_WALL), z0,
               cx - 2.6, max(y0, y0 + side * CLIP_WALL), z1)


def build(variant: str = "shard", **overrides) -> dict[str, Part]:
    p = dict(WALL=WALL, X_OUT=X_OUT, MOUTH=MOUTH, Z_TOP_PANEL=Z_TOP_PANEL, REAR_CLIP_H=REAR_CLIP_H,
             NOTCH_H=NOTCH_H, USB=USB, USB_Y=USB_Y, USB_W=USB_W, USB_H=USB_H, USB_Z=USB_Z,
             VENT=VENT, MARK=MARK, ELYTRA_PITCH=ELYTRA_PITCH,
             ELYTRA_W=ELYTRA_W, ELYTRA_Z=ELYTRA_Z, MARK_Z=MARK_Z, BAND_H=BAND_H,
)
    if variant == "carapace":
        p.update(VENT=False)
    p.update(overrides)
    z_rear = Z_BOT + p["REAR_CLIP_H"]

    plan, _ = _plan(p)
    panel = extrude(Plane.XY.offset(Z_BOT) * plan, amount=p["Z_TOP_PANEL"] - Z_BOT)
    # The rear clip ends at Z 21.5; above it only the plain wall may reach back to y -29.
    # The second cut clears REAR_WEB's root fillet as well, or its tapering wedge would survive
    # above the clip as a knife edge along y -26.
    panel -= box(X_IN - 5, -60, z_rear, 45, WALL_Y[0], p["Z_TOP_PANEL"] + 1)
    panel -= box(p["X_OUT"], -60, z_rear, 45, REAR_WEB[0] + FILLET_2D, p["Z_TOP_PANEL"] + 1)

    apertures = _windows(p) or Sketch()
    if variant == "carapace":
        slots, n = _elytra(p, _keepouts(p))
        if n:
            apertures += slots
    if apertures.faces():
        panel -= S.extrude_cut(apertures, Plane.YZ.offset(X_IN - 1), p["WALL"] + MARK_PAD + 8.0)

    # The mark is cut BEFORE the dome on purpose: its groove floor faces +X, so it belongs to the
    # displaced skin and rises WITH the surface, keeping its 0.6 mm depth on the swell. Cutting it
    # afterwards with a straight prism would give a groove 0.6 deep at the crest and cut clean through
    # at the flanks, because the swell varies 2.2 mm across the mark's own footprint.
    m = None
    if p["MARK"]:
        panel += _carina(p) & box(X_IN, WALL_Y[0], Z_BOT, 60, WALL_Y[1], p["Z_TOP_PANEL"])
        m = _mark(p, "lunule" if variant == "carapace" else "stripe3")
        if m is not None:
            panel -= m

    _BASE[variant] = panel
    return pair(panel, "side_panel")


def checks(parts: dict[str, Part], frame: dict[str, Part], variant: str = "") -> list[tuple[str, bool, str]]:
    """ONE checks() for every variant: the fit assertions below are exactly the ones the single-style
    panel had, and both styles must still pass all of them. Only three rows are variant-aware - the
    decoration report, the aperture count and the style conformance - and none of them relaxes a
    fit check."""
    right, left = parts["side_panel_right"], parts["side_panel_left"]
    z_rear = Z_BOT + REAR_CLIP_H
    bb = right.bounding_box()
    out = []
    if variant:
        # A degraded Blender pass reports FALSE here, never "skipped": the manifest then records that
        # the part shipped undecorated, and every fit check below still passes because the undecorated
        # part IS the verified functional solid.
        # No Blender pass on this part (see the VARIANTS note), so nothing is expected under this
        # key; absent_ok keeps that from reading as a missing call. Any module that DOES decorate
        # leaves absent_ok False, so a forgotten decorate() shows up as a failing row.
        out += BL.decor_checks(f"side_panel_right__{variant}", absent_ok=True)
        st = S.STYLES[VARIANTS[variant]["style"]]
        out.append((f"style {st.name}: edge ladder within 0.45 x wall",
                    S.edge_radius(st, "free", WALL_MIN) <= 0.45 * WALL_MIN + 1e-9,
                    f"free tier {S.edge_radius(st, 'free', WALL_MIN)} mm on a {WALL_MIN} wall"))
        if variant == "carapace":
            p = dict(WALL=WALL, X_OUT=X_OUT, Z_TOP_PANEL=Z_TOP_PANEL, NOTCH_H=NOTCH_H, USB=USB,
                     USB_Y=USB_Y, USB_W=USB_W, USB_H=USB_H, USB_Z=USB_Z, ELYTRA_Z=ELYTRA_Z,
                     ELYTRA_PITCH=ELYTRA_PITCH, ELYTRA_W=ELYTRA_W)
            _sk, n = _elytra(p, _keepouts(p))
            out.append(("carapace: cusped elytra slits placed", n >= 6,
                        f"{n} slits, {ELYTRA_PITCH - ELYTRA_W:.1f} mm ligament, "
                        f"band Z {ELYTRA_Z[0]}-{ELYTRA_Z[1]}, upright so the cusp is the only ceiling"))
        else:
            out.append(("shard: louvre bank present", VENT and len(VENT_YS) >= 4,
                        f"{len(VENT_YS)} slots at {VENT_ANGLE} deg"))

    hits = interference(right)
    out.append(("no interference with any frame part", not hits, f"{hits or 'none'}"))
    out.append(("one solid", len(right.solids()) == 1, f"{len(right.solids())} solid(s)"))

    for name, (px, py), h in (("front", _NECK_FRONT, 24.0), ("rear", _NECK_REAR, 12.5)):
        probe = box(px - 0.5, py - 0.5, Z_BOT, px + 0.5, py + 0.5, Z_BOT + h)
        v = isect(right, probe)
        out.append((f"{name} neck fully solid at ({px}, {py})", abs(v - h) < 1e-3, f"{v:.4f} of {h} mm³"))
    # The spec's front neck probe sits at (24, 29.5) - with -X mouths that point is the insertion
    # channel, so it is checked open rather than solid, over the whole channel and clip height.
    for side, (cx, cy), z1 in (("front", FRONT_ARM_XY, Z_TOP_PANEL), ("rear", REAR_ARM_XY, z_rear)):
        chan = box(X_IN - 8, cy - MOUTH / 2 + 0.05, Z_BOT, cx, cy + MOUTH / 2 - 0.05, z1)
        v = isect(right, chan)
        out.append((f"{side} standoff insertion channel clear to the mouth", v < EPS, f"{v:.4f} mm³"))

    for side, xy, span in (("front", FRONT_ARM_XY, (Z_BOT + 0.2, Z_TOP_PANEL - 0.2)),
                           ("rear", REAR_ARM_XY, (Z_BOT + 0.2, z_rear - 0.2))):
        for hand, part, cx in (("right", right, xy[0]), ("left", left, -xy[0])):
            ok, detail = coaxial(part, (cx, xy[1]), D_CLIP_BORE, *span)
            out.append((f"{side} bore coaxial with standoff_{side}_arm_{hand}", ok, detail))

    cyls = standoff_cylinders()
    for nm in ("standoff_front_arm_right", "standoff_rear_arm_right"):
        d = right.distance_to(cyls[nm])
        out.append((f"gap to the Ø{STANDOFF_D} {nm}", abs(d - STANDOFF_FIT) <= 0.05, f"{d:.4f} mm"))

    probes = None
    for cx, cy in INNER_CLAMP_XY:
        nut = hex_pocket(NUT_ACROSS_CORNERS * cos(radians(30)), NUT_H, (cx, cy, Z_BOT))
        tip = cylinder(cx, cy, Z_BOT + NUT_H, Z_BOT + NUT_H + BOLT_TIP_H, BOLT_TIP_D)
        probes = nut + tip if probes is None else probes + nut + tip
    worst, worst_dx = 0.0, 0.0
    for step in range(int(SLIDE_ON / 0.5) + 1):
        dx = step * 0.5
        v = isect(right if dx == 0 else right.moved(Location((dx, 0, 0))), probes)
        if v > worst:
            worst, worst_dx = v, dx
    out.append((f"inner arm-clamp nuts clear over the {SLIDE_ON} mm slide-on", worst < EPS,
                f"max {worst:.4f} mm³ at +{worst_dx:.1f} mm"))

    # Nothing but the two standoffs may be in the way while the panel is pushed inboard; the
    # standoff overlap that does appear is the snap itself and must come back to zero when seated.
    rigid = {n: pt for n, pt in frame.items() if not n.startswith("standoff")}
    blocked, snap_peak = [], 0.0
    for step in range(int(SLIDE_ON / 0.5) + 1):
        moved = right if step == 0 else right.moved(Location((step * 0.5, 0, 0)))
        blocked += [(step * 0.5, *h) for h in interference(moved, against=rigid)]
        snap_peak = max(snap_peak, sum(v for _n, v in standoff_interference(moved)))
    out.append((f"slide-on path clear of the plates and arms over {SLIDE_ON} mm", not blocked,
                f"{blocked or 'none'}; snap interference peaks at {snap_peak:.1f} mm³ and is 0 when seated"))

    contact = seated(right, Z_BOT)
    out.append(("wall bottom seated at Z 9.000", abs(bb.min.Z - Z_BOT) < 1e-6,
                f"min Z {bb.min.Z:.4f}, {contact} mm² on plate_mid"))
    bed = sum(f.area for f in right.faces() if f.geom_type == GeomType.PLANE
              and abs(f.center().Z - Z_BOT) < 1e-4 and abs(f.normal_at().Z) > 0.999)
    out.append(("bed-plane faces >= 90 mm²", bed >= 90.0, f"{bed:.1f} mm²"))
    out.append((f"max Z <= {Z_TOP_PANEL}", bb.max.Z <= Z_TOP_PANEL + 1e-6, f"max Z {bb.max.Z:.3f}"))
    out.append(("inboard faces >= 21.2", bb.min.X >= 21.2 - 1e-6, f"min X {bb.min.X:.3f}"))
    out.append(("envelope x <= 33.4, y -38.2..36.7", bb.max.X <= 33.4 and bb.min.Y >= -38.25
                and bb.max.Y <= 36.7, f"x {bb.min.X:.3f}..{bb.max.X:.3f}, y {bb.min.Y:.3f}..{bb.max.Y:.3f}"))

    v = isect(right, box(-20, -20, Z_BOT, 20, 20, Z_BOT + 25))
    out.append(("clear of the 40 x 40 x 25 FC/ESC envelope", v < EPS, f"{v:.3f} mm³"))
    v = prop_disc_violation(right)
    out.append(("outside the prop keep-out discs", v < EPS, f"{v:.3f} mm³"))

    # the variant's own bridge list, not the base one: carapace adds the elytra slot ceilings, which
    # are bridges of ELYTRA_W across exactly as the flat USB lintel is
    over = overhangs(right, PRINT["side_panel_right"], material=MATERIAL,
                     bridge_ok=BRIDGE_OK.get(f"side_panel_right__{variant}", BRIDGE_OK["side_panel_right"]))
    out.append(("no unsupported overhangs (notch and USB lintels bridged)", not over,
                "; ".join(over) or "none"))

    measured = _BASE.get(variant, right)
    ok, _residual, detail = min_wall(measured, WALL_MIN)
    out.append((f"min wall >= {WALL_MIN}" + ("" if measured is right else
                " on the functional solid (the decorated mesh is measured by the decor mesh-wall row)"),
                ok, detail))
    # min_wall's ray fallback cannot see a tapering tip, so measure the four lips directly.
    worst_lip, lips = 1.0, []
    for (cx, cy), z1 in ((FRONT_ARM_XY, Z_TOP_PANEL), (REAR_ARM_XY, z_rear)):
        for side in (1, -1):
            probe = _lip_probe(cx, cy, side, Z_BOT + 0.05, z1 - 0.05)
            frac = isect(right, probe) / probe.volume
            worst_lip = min(worst_lip, frac)
            lips.append(f"{frac:.4f}")
    out.append((f"snap lips a full {CLIP_WALL} mm slab (no tapering tip)", worst_lip > 1 - 1e-4,
                f"solid fractions {', '.join(lips)}"))

    # 9 structural corners + 3 lip tips; the front lower lip has no tip (the web's top face is the
    # mouth floor there), so 12 is the full set.
    _, filleted = _plan(dict(WALL=WALL, X_OUT=X_OUT, MOUTH=MOUTH))
    out.append(("every plan corner filleted", filleted == 12, f"{filleted} of 12 corners"))

    out.append(("volume 2.5-5.5 cm³", 2500.0 <= right.volume <= 5500.0, f"{right.volume / 1000:.3f} cm³"))
    out.append(("left mirror has the same volume", abs(left.volume - right.volume) < 0.01,
                f"Δ {abs(left.volume - right.volume):.6f} mm³"))
    return out
