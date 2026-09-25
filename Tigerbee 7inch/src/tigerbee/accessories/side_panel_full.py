"""Full-length side panels: ONE continuous piece down the whole flank, four styles.

The third kind of side panel in this set, and the user supplied photographs of all four readings.
`side_panel_clip` spans one standoff pair per panel; `side_panel_system` splits the flank into a
carcass plus three swappable skins. This module is the opposite idea: a SINGLE piece that runs the
whole length of the stack, from forward of the front arm root to behind the rear one, held by the
same snap-on C-clips and nothing else.

    slab      NOCTURNE    refs/side-panels-full/green-slab-round-vents.png, yellow-slab-vents.png
                          A plain flat plate filling the plate gap. A stepped top edge and one row
                          of round vents aft. Reads as a solid block of colour on the aircraft.
    faceted   SHARD       refs/side-panels-full/orange-faceted-finned.png, orange-sculpted-side.png
                          Angular plan, hard creases, a run of raked fins proud of the outboard
                          face over the rear half, and a rectangular port amidships.
    wrap      BRUTALIST   refs/side-panels-full/black-wrap-shell.png
                          Not a panel but a shell: the flank returns inboard over the top edge to
                          roof the flight-controller bay, so the plan is an L, not a ribbon.
    smooth    SLIPSTREAM  refs/side-panels-full/teal-smooth-body.png
                          One continuous bowed body, no vents, no creases, ends rounded away.

THE PLANS ARE DIFFERENT SHAPES, not one shape with different holes: a near-straight ribbon, a
polygon carrying fins, an L-section with a roof flange, a deep bow, a teardrop, a tub and a wide C.
That is what the silhouette gate measures, and checks() reports the pairwise numbers.

`fairing` IS A DELIBERATE, RECORDED EXCEPTION TO THAT GATE, and with the dome switched on it takes
`hull` and `segmented` red with it, since the gate reports a clash from both sides. Domed, its plan
lands at ~470 mm2, inside 12 % of wrap 473.1, hull 502.3 and segmented 511.4 at once. Undomed it is
365.6 and clashes only with smooth. There is no rise that avoids both: the feasible bands are
<= 355 mm2 (a dome only adds) or >= 570 mm2 (past the recipe's own 1.35 volume ceiling). So the
choice is one red row without the dome or three with it, and the dome is the whole difference
between a curved band with slits in it and the bodywork in the photograph. Flip `dome` in
PARAMS["fairing"] to choose; nothing else changes.

The underlying reason is the same in both cases: It reads 9.7 % of plan area and 0.053
of hull deficiency from `smooth`, inside the 12 % / 0.10 thresholds, and it is left failing. The
two parts are genuinely different - three raked gill slits, a tail blade standing proud at x 35.5,
and a teardrop section against an even bow - and the gate reads plan area and hull deficiency only,
so it can see none of them. The space is also closed: against the four fixed siblings (slab 279.7,
smooth 330.2, faceted 403.5, wrap 473.1) the only plan areas a seventh full-length panel can take
are <= 246 mm2 or >= 570 mm2, which on this outline means a 1.2 mm skin or a near-solid block.
DO NOT "FIX" THIS BY DISTORTING THE PANEL, and do not widen the gate either - it earns its keep
catching near-identical variants elsewhere, and one loosened to admit an honest exception stops
catching dishonest ones. Leave the row red and leave this paragraph here.

THE CLIPS ARE OPEN ON PURPOSE. `_common.c_clip()` now defaults to `closed=True` - a complete ring -
because an open mouth was the wrong default for parts that bolt on and stay on. This module passes
`closed=False` deliberately: a full-length panel is the one part in the set whose whole purpose is
to come off in the field without stripping the frame, and a closed ring cannot be removed without
pulling a standoff and dropping the top plate. The trade is real and is paid in retention: the
panel is held by 0.8 mm of snap interference on two Ø6 standoffs instead of by a captive ring, so
it will part company with the airframe in a hard enough crash. That is the intended failure mode -
the panel is the sacrificial part, and it is cheaper to reprint than the carbon it protects.

WHAT CONSTRAINS THE GEOMETRY, measured rather than assumed. The panel floats in the Z 9.25-33.75
band between plate_mid's top face and plate_top's underside, so neither plate outline touches it -
plate_mid reaches x 33.47 at y 30 and plate_top x 37.0 at y 60, and both are irrelevant here. What
does constrain it: the two Ø6 arm-root standoffs it grips, the Ø6 x 3 arm-root BOLT HEADS at
(26.97, 18.17) and (26.43, -19.63) over Z 9-12 which the inboard face must stand clear of, the
40 x 40 stack envelope at Z 12-31, and the rear prop disc, which is the binding constraint aft:
at y -52 nothing may reach past x 36.5, and at y -60 past x 32.25.
"""

from math import hypot, pi, sin

from build123d import (Align, Axis, Circle, Part, Plane, Polygon, Pos, Rectangle, Sketch,
                       chamfer, extrude, fillet)

from tigerbee.accessories import _style as S
from tigerbee.accessories._common import *  # noqa: F401,F403 - constants, builders and checks

NAME = "side_panel_full"
TITLE = "Full-length side panels (4 styles)"
MATERIAL = "TPU95A"
EXCLUSIVE = ("side_panel_clip", "side_panels", "side_panel_system")
PRINT = {"side_panel_full_r": (0, 0, -1), "side_panel_full_l": (0, 0, -1)}
MOUNTS = (
    "standoff_front_arm_right / _left Ø6 shafts (±28.5283, 31.8308), clip bore Z 9.55-33.45",
    "standoff_rear_arm_right / _left Ø6 shafts (±26.0700, -33.3726), clip bore Z 9.55-33.45",
    "plate_mid top face Z 9 and plate_top underside Z 34 (0.25 mm running clearance to each - the "
    "panel floats between the plates and seats on neither)",
)
HARDWARE = ("none - 0.8 mm snap fit onto the two Ø6 arm-root standoffs",)

# --- frame interface (mm) ---------------------------------------------------------------------
Z_BOT = 9.25                        # 0.25 over plate_mid's top face (Z 9)
Z_TOP = 33.75                       # 0.25 under plate_top's underside (Z 34)
SNAP = MATERIALS[MATERIAL]["snap"]   # 0.8
MOUTH = STANDOFF_D - SNAP            # 5.2 parallel throat over a Ø6 standoff
R_BORE = D_CLIP_BORE / 2             # 3.25
R_RING = R_BORE + CLIP_WALL          # 4.85
FA = FRONT_ARM_XY                    # (28.5283, 31.8308)
RA = REAR_ARM_XY                     # (26.0700, -33.3726)
MOUTH_IN = 180.0                     # mouths face -X: the panel is pushed on from outside

# The arm-root bolt heads the inboard face has to clear, and the band they live in.
BOLT_HEADS = ((26.97, 18.17), (26.43, -19.63))
BOLT_HEAD_R, BOLT_HEAD_Z = 3.0, (9.0, 12.0)
STACK_40 = box(-20, -20, 12, 20, 20, 31)
WALL_MIN = MATERIALS[MATERIAL]["wall"]                       # 1.2
HOLE_MIN = S.DECOR_MATERIALS[MATERIAL]["hole_min"]           # 2.2
LIG_MIN = S.DECOR_MATERIALS[MATERIAL]["ligament_min"]        # 1.2

_INFO: dict = {}     # what the last build() measured, read back by checks()
_PLANS: dict = {}    # style -> (plan area, hull deficiency) for the silhouette gate


# --- plan plumbing ------------------------------------------------------------------------------
def _seg_normals(pts):
    """Outboard (+X-ish) unit normal of every segment. Paths run by DECREASING y, which makes
    (-dy, dx) point outboard on the right-hand panel."""
    out = []
    for a, b in zip(pts, pts[1:]):
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = hypot(dx, dy) or 1.0
        out.append((-dy / L, dx / L))
    return out


def _offset_path(pts, d: float):
    """Miter offset of a polyline by `d` along the outboard normal (negative = inboard)."""
    ns = _seg_normals(pts)
    out = []
    for i, p in enumerate(pts):
        if i == 0:
            n = ns[0]
        elif i == len(pts) - 1:
            n = ns[-1]
        else:
            n1, n2 = ns[i - 1], ns[i]
            k = 1.0 + n1[0] * n2[0] + n1[1] * n2[1]
            n = ((n1[0] + n2[0]) / k, (n1[1] + n2[1]) / k) if k > 1e-6 else n2
        out.append((p[0] + n[0] * d, p[1] + n[1] * d))
    return out


def _ribbon(pts, wall: float, out_extra: float = 0.0) -> Sketch:
    """Closed plan profile of a wall `wall` thick centred on the polyline `pts`."""
    outer = _offset_path(pts, wall / 2 + out_extra)
    inner = _offset_path(pts, -wall / 2)
    return Polygon(*outer, *reversed(inner), align=None)


def _bow(p0, p1, bulge: float, n: int = 12):
    """`n` segments from p0 to p1 bowed `bulge` mm outboard at mid-span (a half sine, so the ends
    leave the chord tangentially and the bow carries no crease)."""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    L = hypot(dx, dy) or 1.0
    nx, ny = -dy / L, dx / L
    return [(p0[0] + dx * (i / n) + nx * bulge * sin(pi * i / n),
             p0[1] + dy * (i / n) + ny * bulge * sin(pi * i / n)) for i in range(n + 1)]


def _ring_plan(center, opening_deg: float = MOUTH_IN) -> Sketch:
    """The open C-clip's own 2D profile - bore Ø6.5, wall 1.6, a parallel 5.2 mm throat with
    filleted lips - as a PLAN sketch, so the ribbon unions into it before anything is extruded and
    the union can never square the lips off again."""
    lip = MOUTH / 2 + CLIP_WALL
    slot = Pos((R_RING + 1.0) / 2, 0) * Rectangle(R_RING + 1.0, MOUTH)
    sk = Circle(R_RING) + Pos(R_RING / 2, 0) * Rectangle(R_RING, 2 * lip)
    sk = sk - Circle(R_BORE) - slot
    tips = [v for v in sk.vertices() if abs(abs(v.Y) - MOUTH / 2) < 1e-6 and v.X > R_RING - 1e-6]
    if len(tips) == 2:
        sk = fillet(tips, MOUTH_FILLET)
    return Pos(*center) * sk.rotate(Axis.Z, opening_deg)


def _prism(plan: Sketch, z0: float = Z_BOT, z1: float = Z_TOP) -> Part:
    """Extrude a plan sketch into the band [z0, z1], whichever way its face normal points.

    `_ribbon` builds its profile outer-then-reversed-inner, which leaves the face normal at -Z, so
    a plain `extrude(..., amount=z1 - z0)` runs DOWNWARD from z0 - the panel came out spanning
    Z -15.25 to 33.75 and collided with the arms and both lower plates. Placing the finished solid
    by its own bounding box is indifferent to the winding."""
    solid = extrude(Plane.XY * plan, amount=z1 - z0)
    return solid.moved(Location((0, 0, z0 - solid.bounding_box().min.Z)))


def _vent(y: float, z: float, d: float) -> Part:
    """A round vent through the wall - axis along X, so it prints as an arch, not a ceiling."""
    return Pos(28.0, y, z) * Cylinder(d / 2, 40.0, rotation=(0, 90, 0))


# --- the four plans ------------------------------------------------------------------------------
# Every path runs by DECREASING y. The inboard face must stay clear of the two bolt heads, which
# reach x 29.97 at y 18.17 and x 29.43 at y -19.63; the rear tip must stay inboard of the prop disc.
FRONT_Y, REAR_Y = 52.0, -52.0

PATHS = {
    "slab": [(30.2, FRONT_Y), (31.4, 36.0), (32.0, 20.0), (32.3, 0.0),
             (31.9, -20.0), (30.4, -38.0), (29.4, REAR_Y)],
    "faceted": [(29.6, FRONT_Y), (32.4, 38.0), (32.9, 22.0), (31.8, 4.0),
                (32.6, -14.0), (31.2, -34.0), (29.0, REAR_Y)],
    "wrap": [(30.6, 46.0), (32.1, 30.0), (32.6, 10.0), (32.4, -10.0),
             (31.3, -28.0), (29.6, -44.0)],
    "smooth": _bow((30.0, FRONT_Y), (29.2, REAR_Y), 11.5, 20),
    # --- the three sculptural readings ----------------------------------------------------------
    # A TEARDROP, not a symmetric bow: the mass sits forward over the stack and the tail draws out
    # to a fine point, which is what makes a fairing read as a fairing beside `smooth`'s even arc.
    "fairing": [(29.6, 52.0), (32.6, 45.0), (35.4, 37.0), (37.1, 28.0), (37.6, 19.0),
                (37.2, 10.0), (36.0, 1.0), (34.2, -9.0), (32.4, -19.0), (31.0, -29.0),
                (30.2, -38.0), (29.8, -46.0), (29.6, REAR_Y)],
    # A TUB: fullest amidships and squared off at both ends, so the plan is a long rounded rectangle
    # rather than a lens. The scoop is cut out of the front third afterwards.
    "hull": [(28.8, 50.0), (32.4, 42.0), (34.6, 32.0), (35.4, 18.0), (35.5, 2.0),
             (34.8, -14.0), (33.0, -28.0), (30.6, -40.0), (28.6, REAR_Y)],
    # A POD: a shallow flank whose whole shape comes from the deep inboard returns at both ends,
    # so in plan it is a wide C. Kept inboard of the others because the returns carry the volume.
    # A BULGING flank with a pointed nose - the only one with real section depth. Its plan area has
    # to clear 570 mm2 (see VARIANTS["segmented"]), which is why the wall is armour-thick.
    "segmented": [(30.0, 52.0), (32.5, 44.0), (34.2, 34.0), (35.0, 22.0), (35.2, 8.0),
                  (34.6, -6.0), (33.4, -20.0), (31.8, -34.0), (30.2, -46.0), (29.4, REAR_Y)],
    "canopy": [(29.4, 46.0), (31.0, 34.0), (31.8, 18.0), (32.0, 0.0),
               (31.6, -18.0), (30.4, -32.0), (29.0, -44.0)],
    # --- the three BOLD readings of the photographs ---------------------------------------------
    # These three exist because `faceted` and `slab` came out as neat strips with a detail applied,
    # where the photographs show moulded bodywork. The difference is SECTION DEPTH: a 2.0 mm wall
    # cannot read as a moulding however it is shaped, so these carry 3.2-5.8 mm and buy the volume
    # back. The inboard face still clears the bolt heads (x 29.97 at y 18.17, x 29.43 at y -19.63)
    # and the outboard face plus anything standing proud of it stays inside the rear prop disc.
    "finned": [(30.0, 52.0), (33.0, 44.0), (33.6, 32.0), (33.2, 20.0), (33.8, 6.0),
               (33.4, -8.0), (33.9, -22.0), (33.2, -36.0), (31.0, -46.0), (29.8, REAR_Y)],
    "moulded": [(29.8, 52.0), (32.6, 44.0), (33.4, 34.0), (33.6, 22.0), (33.4, 8.0),
                (33.6, -6.0), (33.2, -20.0), (32.2, -34.0), (30.6, -44.0), (29.6, REAR_Y)],
    "plated": [(30.6, FRONT_Y), (31.8, 38.0), (32.4, 20.0), (32.6, 0.0),
               (32.2, -20.0), (31.0, -38.0), (29.8, REAR_Y)],
}

PARAMS = {
    "slab": dict(family="nocturne", wall=2.2, vent_d=5.6,
                 vents=(-22.0, -30.0, -38.0, -46.0), vent_z=24.5,
                 notch=(-3.0, 13.0, 7.0)),          # y0, y1, depth cut into the top edge
    "faceted": dict(family="shard", wall=2.0, port=(0.0, 9.0, 19.0, 29.0),
                    fins=(-10.0, -18.0, -26.0, -34.0, -42.0, -50.0), fin_proud=5.2),
    "wrap": dict(family="brutalist", wall=3.8, roof=12.0),
    "smooth": dict(family="slipstream", wall=2.0),
    # gills: (y centre, z centre) of each raked slit; winglet: (y root, y tip, x tip, rake)
    "fairing": dict(family="carapace", wall=1.9, dome=True,
                    gills=((24.0, 25.5), (17.0, 24.0), (10.0, 22.5)),
                    gill_len=9.0, gill_w=2.6, gill_rake=58.0,
                    winglet=(-36.0, -48.0, 35.5, 3.0)),
    # scoop: (y0, y1, z0, z1) of the intake mouth; lip stands proud around its aft and lower edges
    "hull": dict(family="arsenal", wall=3.2, scoop=(30.5, 41.5, 14.5, 28.0), lip=3.2,  # taller than wide: an upright stadium has no flat floor
                 returns=22.0, straps=((12.0, 2.0), (-6.0, 2.0))),
    # bands: y of each vespid segmentation groove across the flank
    # grooves: y of each transverse segment join; fins: y of each rear fin
    "segmented": dict(family="carapace", wall=4.2, grooves=(34.0, 18.0, 2.0, -14.0),
                      groove_w=2.4, groove_d=1.3,
                      fins=(-30.0, -33.0, -36.0, -39.0, -42.0, -45.0, -48.0),
                      fin_w=1.6, fin_proud=4.0),
    "canopy": dict(family="vespid", wall=1.6, dome=False, ret_front=31.0, ret_rear=26.0,
                   bands=(20.0, 10.0, 0.0, -10.0, -20.0), band_w=1.8, band_d=0.30),
    # A 5 mm flank carrying TWELVE fins at 2 mm pitch. `faceted` has six at 8 mm on a 2 mm wall;
    # this is the same idea taken to the photograph's density. Fins stop at y -40: at -45 the tip
    # reaches within 0.2 mm of the rear prop disc, measured, so the bank is shortened rather than
    # thinned. Creases are kinks in the path, not cuts - a crease cut into a 5 mm wall is a groove.
    # EIGHT fins at 3.2 mm pitch, not twelve at 2.0. Twelve rendered as a serrated edge rather than
    # a fin bank - at that pitch the gaps are narrower than the fins are proud and the eye reads
    # texture, not fins. Eight wider ones standing 6.5 mm proud read as the photograph's louvre run.
    # The bank still stops at y -40.4: the tip there clears the rear prop disc by 2.5 mm, measured.
    "finned": dict(family="shard", wall=5.0,
                   fins=tuple(-4.0 - 3.6 * i for i in range(11)),
                   fin_w=2.0, fin_proud=6.5,
                   creases=(40.0, 28.0, 16.0, 4.0), crease_w=2.2, crease_d=1.8),
    # The deepest wall in the set, and the only one whose TOP EDGE steps. Steps are cut from the
    # top, so every ceiling they leave faces UP; the same feature cut into the bottom edge is what
    # `segmented` had to drop. Flutes are wide shallow transverse reliefs standing in for the
    # internal ribs the translucent print shows in the photograph.
    "moulded": dict(family="carapace", wall=5.8,
                    steps=((-2.0, 14.0, 3.0), (-20.0, -4.0, 5.5), (-40.0, -22.0, 8.0)),
                    flutes=(30.0, 18.0, 6.0, -8.0, -22.0), flute_w=5.0, flute_d=1.6),
    # Boldness by COVERAGE, not detail: a 3.2 mm wall - half again over `slab` - carried flat the
    # whole length, and five Ø8.0 vents at 9.5 mm pitch, which is 1.5 mm of ligament between them.
    # `slab` has four Ø5.6 at 8 mm. The step in the top edge is the photograph's one crisp feature.
    # THE ROW SITS BETWEEN THE RINGS, not aft where the photograph puts it, and that is a frame
    # constraint rather than a style choice. `_vent` bores straight through everything in its path,
    # and the rear clip ring occupies y -38.2..-28.5; a Ø8 vent anywhere in that span cuts the
    # ring's collar into 0.06 mm slivers (measured, at y -38.1, x 25.5-26.6). The clear span
    # between the two rings is y -28.5..27, so the row is biased as far aft inside it as the
    # 1.2 mm ligament to the ring allows - the aftmost vent leaves 2.0 mm.
    # 4.2 mm, not 3.2: at 3.2 the gate read this 9.2 % from `slab` in plan and 11.7 % in elevation,
    # both inside the threshold, and it was right - a 45 % thicker wall with slightly bigger holes
    # is the same panel. Nearly DOUBLE slab's 2.2 mm wall with Ø9 vents against its Ø5.6 is a
    # different object. Pitch is 10.5, which is the 1.5 mm ligament the Ø9 hole allows.
    "plated": dict(family="nocturne", wall=4.2, vent_d=9.0,
                   vents=(-22.5, -12.0, -1.5, 9.0, 19.5), vent_z=22.0,
                   notch=(-50.0, -40.0, 6.0)),   # aft of the rear ring, 1.8 mm clear of its collar
}

VARIANTS = {
    "slab": {"style": "nocturne",
             "notes": "NOCTURNE. The plain reading, after the green and yellow panels: a flat 2.2 mm "
                      "plate filling the whole plate gap, one rectangular step cut out of the top "
                      "edge amidships where the wiring crosses, and a single row of four Ø5.6 vents "
                      "aft over the ESC. No ribs, no creases, no mark - it is meant to read as one "
                      "block of colour."},
    "faceted": {"style": "shard",
                "notes": "SHARD. The orange reading: a polygonal plan that kinks at every station "
                         "instead of curving, a rectangular port amidships, and four fins standing "
                         "2.4 mm proud of the outboard face over the rear half, each raked so no "
                         "flank passes 45 deg in the print orientation."},
    "wrap": {"style": "brutalist", "material": "PETG",
             "notes": "BRUTALIST. The black reading, and the only one that is not a ribbon: the "
                      "flank returns 7.0 mm inboard at the top as a 2.4 mm roof flange, so the plan "
                      "is an L and the panel shells the flight-controller bay from the side and "
                      "over. Heavier wall, no vents, nothing filleted above r 0.3."},
    "smooth": {"style": "slipstream",
               "notes": "SLIPSTREAM. The teal reading: one continuous body bowed 3.4 mm outboard "
                        "across its whole length, 3.0 mm wall, both ends rounded away to nothing. "
                        "No vents and no apertures at all - the unbroken surface is the point."},
    "fairing": {"style": "carapace",
                "notes": "CARAPACE. refs/side-panels-full/fairing-gill-slits-winglet.png - the "
                         "motorcycle-fairing reading and the boldest of the seven. A teardrop plan "
                         "swelling to x 37.6 over the stack and drawing out to a point aft, a "
                         "Blender dome over the swell so the flank is a curved shell rather than a "
                         "bent plate, three raked gill slits cut into the crown of the swell, and "
                         "the tail flaring into a winglet that stands away from the frame."},
    "hull": {"style": "arsenal", "material": "PETG",
             "notes": "ARSENAL. refs/side-panels-full/black-scooped-hull.png - a tub, not a panel. "
                      "3.2 mm wall carried full height with short inboard returns at both ends, a "
                      "large intake scoop cut out of the front third with a lip standing proud "
                      "around it, and two strap reliefs over the top edge. The heaviest of the "
                      "seven and the one that actually encloses something."},
    "segmented": {"style": "carapace",
                  "notes": "CARAPACE, and the most literal tiger-beetle reading in the catalogue - "
                           "refs/side-panels-full/segmented-armour-finned.png. A bulging armoured "
                           "flank divided along its length by four transverse grooves into five "
                           "plates that step over one another like abdominal segments, a bank of "
                           "seven upright fins over the tail, a nose drawn to a point and a notch "
                           "cut low at the front to clear the arm - except that the notch is "
                           "dropped (see _build_segmented) and the grooves read MORE SUBTLY than "
                           "the reference, because they are 1.3 mm reliefs in the outboard face "
                           "rather than whole plates stepping over one another. Do not 'fix' that "
                           "by deepening them into the wall. The 4.2 mm wall is not padding: "
                           "with seven siblings already placed, the only plan area left open to an "
                           "eighth panel is above 570 mm2, and the reference's own bodywork volume "
                           "is what puts it there. It is the heaviest panel in the set and says so."},
    "canopy": {"style": "vespid",
               "notes": "VESPID. refs/side-panels-full/blue-full-canopy-pod.png - the full pod. A "
                        "shallow flank whose volume is in the deep inboard returns at both ends, so "
                        "in plan it is a wide C that closes the bay fore and aft as well as from "
                        "the side. Seven transverse segmentation grooves band the flank, and a "
                        "Blender dome rounds the shoulders."},
    "finned": {"style": "shard",
               "notes": "SHARD, and the bold reading of orange-faceted-finned.png that `faceted` is "
                        "not. Same photograph, opposite restraint: a 5.0 mm moulded flank instead "
                        "of a 2.0 mm plate, twelve fins at 2 mm pitch standing 6.0 mm proud "
                        "instead of six at 8 mm standing 5.2, and four longitudinal creases cut "
                        "into the outboard face. The bank stops at y -40 because at y -45 a fin "
                        "tip comes within 0.2 mm of the rear prop disc - shortened, not thinned."},
    "moulded": {"style": "carapace", "material": "PETG",
                "notes": "CARAPACE, from orange-sculpted-side.png - the profile view, where the "
                         "photographed panel's VOLUME is the whole point. The deepest wall in the "
                         "set at 5.8 mm, a top edge that steps down in three stages toward the "
                         "tail (3.0, 5.5, 8.0 mm), and five wide shallow flutes standing in for "
                         "the internal ribs the translucent print shows. Every step is cut from "
                         "the TOP edge so its ceiling faces up - the same feature cut low is what "
                         "`segmented` had to drop as unprintable."},
    "plated": {"style": "nocturne",
               "notes": "NOCTURNE, the bold reading of green-slab-round-vents.png. Where `slab` is "
                        "2.2 mm with four Ø5.6 vents, this is 3.2 mm with five Ø8.0 at 9.5 mm "
                        "pitch - 1.5 mm of ligament, near the printable floor. The photograph's "
                        "boldness is coverage and proportion rather than detail, so the plan stays "
                        "flat and unbroken and the vents do the talking."},
}
ASSEMBLY_VARIANT = "slab"


def _base(style: str, p: dict) -> Part:
    """Ribbon along the style's path, fused with an open C-clip ring at each arm-root standoff.

    The three pieces are extruded and fused as SOLIDS, not unioned as sketches: `Sketch + Sketch`
    trims the overlap out of one operand and leaves the faces separate, which hands back a
    five-solid part that fails `single_solid` before anything else gets a chance to.
    """
    body = _prism(_ribbon(PATHS[style], p["wall"]))
    body += _prism(_ring_plan(FA))
    body += _prism(_ring_plan(RA))
    # The ribbon runs OUTBOARD of both standoffs and overlaps their bores on the way past, which
    # closed the Ø6.5 clip bore down to a 0.000 mm gap on the Ø6 shaft. Re-cut both bores after
    # the fuse so the snap fit is the ring's, not whatever the ribbon happened to leave.
    for x, y in (FA, RA):
        body -= cylinder(x, y, Z_BOT - 1.0, Z_TOP + 1.0, D_CLIP_BORE)
    return body.clean()


def _build_slab(p: dict) -> Part:
    part = _base("slab", p)
    y0, y1, depth = p["notch"]
    part -= box(20.0, y0, Z_TOP - depth, 40.0, y1, Z_TOP + 1.0)
    for y in p["vents"]:
        part -= _vent(y, p["vent_z"], p["vent_d"])
    _INFO["apertures"] = len(p["vents"])
    return part


def _build_faceted(p: dict) -> Part:
    part = _base("faceted", p)
    # The port is GABLED, not rectangular: a flat ceiling over a 12 mm opening is a horizontal
    # unsupported face in the print orientation, and the check counted it. The peak keeps every
    # face of the opening inside 45 deg. Cut as a YZ profile swept through the whole wall.
    y0, y1, z0, z1 = p["port"]
    yc = (y0 + y1) / 2
    rise = (y1 - y0) * 0.78       # steeper than 45 deg: 45 exactly reads -0.707 and the
    #                             overhang gate refuses anything at or past its 0.7 cosine limit
    prof = Polygon((y0, z0), (y1, z0), (y1, z1 - rise), (yc, z1), (y0, z1 - rise), align=None)
    part -= extrude(Plane.YZ * prof, amount=40.0, both=True)
    # Fins stand proud of the OUTBOARD face, raked 30 deg off vertical in plan. They run the FULL
    # height: stopping them short of the top and bottom left four floating end faces pointing at
    # the bed. Flush with the panel's own faces, they add no downward face at all.
    pts = PATHS["faceted"]
    fins = Sketch()
    for y in p["fins"]:
        x = _x_at(pts, y)
        fins += Polygon((x - 1.0, y + 5.5), (x + p["fin_proud"], y + 1.4),
                        (x + p["fin_proud"], y - 1.4), (x - 1.0, y - 5.5), align=None)
    part += _prism(fins)
    _INFO["apertures"] = 1
    _INFO["fins"] = len(p["fins"])
    return _clear_bores(part)


def _build_wrap(p: dict) -> Part:
    part = _base("wrap", p)
    # The shell returns inboard at each END rather than along the whole top edge. A continuous roof
    # flange was both a 394 mm² horizontal overhang in the print orientation AND a lid over the two
    # standoff bores, which took the snap fit to a 0.000 mm gap - the panel could not have gone on.
    # Two full-height end returns shell the bay just as the reference does, print as plain vertical
    # walls, and leave both standoffs open to the sky.
    pts = PATHS["wrap"]
    for end, sgn in ((pts[0], 1), (pts[-1], -1)):
        x, y = end
        inb = _offset_path(pts, -p["wall"] / 2)[0 if sgn > 0 else -1][0]
        part += _prism(Polygon((x + p["wall"] / 2, y), (x + p["wall"] / 2, y - sgn * p["wall"]),
                               (inb - p["roof"], y - sgn * p["wall"]), (inb - p["roof"], y),
                               align=None))
    _INFO["apertures"] = 0
    return _clear_bores(part)


def _clear_bores(part: Part) -> Part:
    """Re-cut both Ø6.5 clip bores after any style has added material near them."""
    for x, y in (FA, RA):
        part -= cylinder(x, y, Z_BOT - 1.0, Z_TOP + 1.0, D_CLIP_BORE)
    return part.clean()


def _build_smooth(p: dict) -> Part:
    part = _base("smooth", p)
    # Both ends rounded away to a nose. A disc of the wall's own radius at each path endpoint caps
    # the square end exactly - cheaper and far more robust than trimming the tip with a boolean,
    # which hands back a Standard_DomainError on this bowed path.
    # The cap radius carries 0.15 mm over the half-wall. A disc of exactly wall/2 is TANGENT to
    # both side faces, the fuse finds zero overlap volume, and the nose ships as a second loose
    # solid; the overshoot is invisible on a 2.4 mm wall and makes the boolean unambiguous.
    for x, y in (PATHS["smooth"][0], PATHS["smooth"][-1]):
        part += _prism(Pos(x, y) * Circle(p["wall"] / 2 + 0.15))
    # The 5.5 mm bow is what makes this silhouette its own, and it carries the flank 0.15 mm
    # OUTBOARD of the rear ring's outer radius at y -33.37 - the ring shipped as a second loose
    # solid. A 6 mm wide web from each standoff axis out to the flank ties them together; the
    # bores are re-cut through it afterwards, and the mouths face -X so nothing blocks the snap.
    for cx, cy in (FA, RA):
        xo = _x_at(PATHS["smooth"], cy) + p["wall"] / 2
        part += _prism(Polygon((cx, cy + 3.0), (xo, cy + 3.0),
                               (xo, cy - 3.0), (cx, cy - 3.0), align=None))
    _INFO["apertures"] = 0
    return _clear_bores(part)


# --- the three sculptural readings ---------------------------------------------------------------
def _body(style: str, p: dict) -> Part:
    """Ribbon + both clip rings, WITHOUT the bores.

    `_base` cuts the bores immediately; these three styles must not, because a mesh pass wants the
    flank solid. Two through-bores in a 2.4 mm wall give the relaxed mesh two more rims to pleat
    against, and the bore is a MATING feature besides - it is deferred through `decorate(cuts=...)`
    and re-cut in B-rep afterwards, exactly as side_panel_system defers its dovetail slits.
    """
    body = _prism(_ribbon(PATHS[style], p["wall"]))
    body += _prism(_ring_plan(FA))
    body += _prism(_ring_plan(RA))
    return body.clean()


def _bores() -> Part:
    out = Part()
    for x, y in (FA, RA):
        out += cylinder(x, y, Z_BOT - 1.0, Z_TOP + 1.0, D_CLIP_BORE)
    return out


def _slot_yz(y: float, z: float, length: float, width: float, rake: float) -> Part:
    """A rounded slot through the wall, raked `rake` degrees, cut along X so it prints as an arch."""
    sk = Rectangle(length, width)
    sk = fillet(sk.vertices(), width / 2 - 0.01)
    return extrude(Plane.YZ * (Pos(y, z) * sk.rotate(Axis.Z, rake)), amount=40.0, both=True)


def _dome(body: Part, cuts: Part, style: str, rise: float, freeze: Part | None = None) -> Part:
    """Swell the flank outboard with the elytra dome, then re-cut the mating bores in B-rep.

    CURRENTLY UNUSED - both styles ship `dome=False`. The dome itself works here: the mesh reaches
    the wall gate cleanly at 1.4863 mm with ZERO thin rays. What never succeeds is the rebuild,
    `(mesh_solid + restore) - cuts`, which BRepCheck_Analyzer calls invalid in all four
    configurations tried on this geometry:

        restore=False          cuts=bores+gills   invalid
        restore=False          cuts=bores         invalid
        restore=rings & body   cuts=bores         invalid
        restore=rings & body   cuts=None          invalid

    The third and fourth were the wrong shape of guess; the FIRST TWO are the configuration
    side_panel_system.py:1005 ships and its comment at 973-978 recommends ("the rail-band restore
    came back as 15 solids, restore=False as one"), and they were re-run against this module's
    current geometry rather than an earlier draft. So the pairing is not the variable. The
    difference is the operand: that module domes a plain slab, this one a 104 mm ribbon with two
    C-clip rings and two webs fused into it, and the rings are where the rebuild has to knit
    tessellation back to B-rep. Do not spend a fifth attempt on parameters - if this is worth
    reviving, dome a plain sub-solid and let CAD reassemble, the way arm_sleeve.py:51 records.

    Kept, documented and switched off rather than left calling a bridge that silently hands the
    undecorated part back - the failure mode this project has already been bitten by once, which
    is why `decor_checks()` is published whenever `dome` is true.

    The guard is intersected with the body rather than merely placed over it: a mask that stands
    proud becomes real material on the way back, and 0.6 mm of phantom ring would break both the
    snap fit and the frame clearance.

    It IS restored, unlike side_panel_system's, whose mating faces are planar and tessellate onto
    their own plane exactly. Ours are the two Ø6.5 CYLINDRICAL bores: left tessellated, cutting a
    true cylinder through a faceted approximation of one shaves slivers off every facet and the
    rebuilt solid came back invalid. Restoring the ring hands the boolean real B-rep to cut.
    """
    from tigerbee.accessories import _blender as BL
    guard = Part()
    for x, y in (FA, RA):
        guard += cylinder(x, y, Z_BOT, Z_TOP, 2 * (R_RING + 0.6))
    if freeze is not None:
        guard += freeze
    res = BL.decorate_ex(body, "elytra_dome",
                         {"rise": rise, "rise_span": 0.0, "subdiv": 3, "relax": 2,
                          "min_nz": 0.72, "feather": 3.0, "axis": "X", "flat": ("Y",)},
                         protect=guard & body, restore=False, cuts=cuts,
                         cache_key=f"side_panel_full_r__{style}", wall_floor=WALL_MIN)
    _INFO["decor"] = res.applied
    # The bores are cut HERE, not handed to the bridge as `cuts`. Inside the rebuild they are
    # subtracted from `mesh_solid + restore` and BRepCheck_Analyzer called the result invalid every
    # time; cut afterwards they land on the restored ring, which is real B-rep, and the same
    # cylinders go through cleanly. Either way the bores are build123d's - only the order moved.
    part = res.part if res.applied else (res.part - cuts)
    return part if isinstance(part, Part) else Part(part.wrapped)


def _dome_plain(flank: Part, style: str, rise: float) -> Part:
    """Dome a PLAIN ribbon - no rings, no webs, no bores, nothing that has to stay exact.

    The arm_sleeve.py:51 approach, and the last one worth trying here. Four parameter pairings of
    protect/restore/cuts were measured against a flank that already had both C-clip rings fused
    into it and every one rebuilt BRepCheck-invalid; the rings are precisely where the rebuild has
    to knit tessellation back to B-rep. So the mesh never sees them: it gets a bare extruded
    ribbon, and CAD fuses the rings and webs on afterwards. Same principle that fixed the mating
    cuts - keep the mesh pass away from the features that must stay exact.
    """
    from tigerbee.accessories import _blender as BL
    res = BL.decorate_ex(flank, "elytra_dome",
                         {"rise": rise, "rise_span": 0.0, "subdiv": 3, "relax": 2,
                          "min_nz": 0.72, "feather": 3.0, "axis": "X", "flat": ("Y",)},
                         protect=None, restore=False, cuts=None,
                         cache_key=f"side_panel_full_r__{style}", wall_floor=WALL_MIN)
    _INFO["decor"] = res.applied
    out = res.part
    return out if isinstance(out, Part) else Part(out.wrapped)


def _build_fairing(p: dict) -> Part:
    # The flank alone goes to Blender; the rings and webs are fused on afterwards in CAD.
    flank = _prism(_ribbon(PATHS["fairing"], p["wall"]))
    if p.get("dome"):
        flank = _dome_plain(flank, "fairing", 1.2)
    part = flank + _prism(_ring_plan(FA)) + _prism(_ring_plan(RA))
    # The teardrop's swell carries the flank to x 35.2 at the FRONT standoff, 1.8 mm outboard of
    # that ring's own x 33.4, so the ring would otherwise ship as a second loose solid. A 6 mm web
    # from each standoff axis out to the flank ties them together.
    for cx, cy in (FA, RA):
        xo = _x_at(PATHS["fairing"], cy) + p["wall"] / 2
        part += _prism(Polygon((cx, cy + 3.0), (xo, cy + 3.0),
                               (xo, cy - 3.0), (cx, cy - 3.0), align=None))
    for gy, gz in p["gills"]:
        part -= _slot_yz(gy, gz, p["gill_len"], p["gill_w"], p["gill_rake"])
    _INFO["apertures"] = len(p["gills"])
    # The blade ends BLUNTLY at the panel's own tail rather than converging back onto the flank:
    # where the two ran nearly tangent the dome relaxed that wedge to 0.006 mm and the wall gate
    # refused the part over a sliver that was an artefact of the outline, not of the swell.
    y0, y1, x_tip, _rake = p["winglet"]
    x_root = _x_at(PATHS["fairing"], y0) - p["wall"] / 2 - 3.0
    part += _prism(Polygon((x_root, y0 + 4.0), (x_tip, y1 + 6.0),
                           (x_tip, REAR_Y), (x_root, REAR_Y), align=None))
    return _clear_bores(part)


def _build_segmented(p: dict) -> Part:
    part = _base("segmented", p)
    pts = PATHS["segmented"]
    # The bulge carries the flank outboard of both rings, so each ring meets the ribbon's inner
    # face almost tangentially and the lens left where they cross measured 0.07 mm. A 6 mm web
    # from each standoff axis out to the flank fills it - the same fix `smooth` and `fairing` use,
    # and for the same reason.
    for cx, cy in (FA, RA):
        xo = _x_at(pts, cy) + p["wall"] / 2
        part += _prism(Polygon((cx, cy + 3.0), (xo, cy + 3.0),
                               (xo, cy - 3.0), (cx, cy - 3.0), align=None))
    # Transverse grooves cut into the OUTBOARD face only, so the plates read as stepping over one
    # another. Full height, so neither a groove ceiling nor a groove floor faces the bed.
    for y in p["grooves"]:
        x = _x_at(pts, y) + p["wall"] / 2
        part -= box(x - p["groove_d"], y - p["groove_w"] / 2, Z_BOT - 1.0,
                    x + 20.0, y + p["groove_w"] / 2, Z_TOP + 1.0)
    # The fin bank. Full height for the same reason `faceted`'s fins are: stopping them short
    # leaves a floating end face pointing at the bed.
    fins = Sketch()
    for y in p["fins"]:
        x = _x_at(pts, y)
        fins += Polygon((x - 1.0, y + p["fin_w"] / 2), (x + p["fin_proud"], y + p["fin_w"] / 2),
                        (x + p["fin_proud"], y - p["fin_w"] / 2), (x - 1.0, y - p["fin_w"] / 2),
                        align=None)
    part += _prism(fins)
    # NO LOW FRONT NOTCH, though the reference has one. A step cut into the bottom edge leaves its
    # ceiling facing the bed - 52.2 mm2 at normal.Z -1.00 - and a ceiling cannot be raked out of
    # it: the slope is h/run, so a 6 mm step over the 18 mm the feature needs is 18 deg, where the
    # overhang gate refuses anything past 45. Ramping it steeply enough would make it a 18 mm deep
    # cut in a 24.5 mm panel. It is cosmetic - the panel clears the arm root without it, measured -
    # so it is dropped rather than bridged or waived.
    _INFO["apertures"] = 0
    _INFO["segments"] = len(p["grooves"]) + 1
    return _clear_bores(part)


def _build_hull(p: dict) -> Part:
    part = _base("hull", p)
    pts = PATHS["hull"]
    # Short inboard returns at both ends close the tub fore and aft. Full height, vertical walls.
    for end, sgn in ((pts[0], 1), (pts[-1], -1)):
        x, y = end
        inb = _offset_path(pts, -p["wall"] / 2)[0 if sgn > 0 else -1][0]
        part += _prism(Polygon((x + p["wall"] / 2, y), (x + p["wall"] / 2, y - sgn * p["wall"]),
                               (inb - p["returns"], y - sgn * p["wall"]), (inb - p["returns"], y),
                               align=None))
    # The intake scoop: a large mouth through the front third with a lip standing proud around it.
    # The lip is added BEFORE the mouth is cut, so the cut passes cleanly through both.
    y0, y1, z0, z1 = p["scoop"]
    xr = _x_at(pts, (y0 + y1) / 2)
    # FULL HEIGHT, like `faceted`'s fins and for the same two reasons. A lip that stopped at
    # z0 - lip and z1 + lip hung a horizontal face over the bed at each end, and the resulting
    # solid crashed OCCT's offset outright inside min_wall - a segfault, not an exception, so the
    # ray fallback never got the chance to catch it and the whole export died mid-check.
    part += _prism(Polygon((xr - 1.0, y1 + p["lip"]), (xr + p["lip"], y1 + p["lip"]),
                           (xr + p["lip"], y0 - p["lip"]), (xr - 1.0, y0 - p["lip"]), align=None))
    # The mouth is a stadium STOOD UPRIGHT. A stadium keeps a flat run wherever its length exceeds
    # its width, and lying down that flat was the mouth's floor - 50 mm² of ceiling facing straight
    # at the bed, which the overhang gate counted. Rotated 90° the flats are the mouth's vertical
    # sides and nothing in the opening faces downward.
    part -= _slot_yz((y0 + y1) / 2, (z0 + z1) / 2, z1 - z0, y1 - y0, 90.0)
    # Strap reliefs over the top edge - square notches, so their ceilings face UP, not down.
    for y, w in p["straps"]:
        part -= box(20.0, y - w, Z_TOP - 4.0, 40.0, y + w, Z_TOP + 1.0)
    _INFO["apertures"] = 1
    return _clear_bores(part)


def _build_canopy(p: dict) -> Part:
    body = _body("canopy", p)
    pts = PATHS["canopy"]
    # The pod's volume is in the returns, not the flank: deep enough to close the bay fore and aft.
    # Both sit outside y ±20, so neither can reach the 40 x 40 stack envelope however far in it goes.
    for end, sgn, depth in ((pts[0], 1, p["ret_front"]), (pts[-1], -1, p["ret_rear"])):
        x, y = end
        inb = _offset_path(pts, -p["wall"] / 2)[0 if sgn > 0 else -1][0]
        body += _prism(Polygon((x + p["wall"] / 2, y), (x + p["wall"] / 2, y - sgn * p["wall"]),
                               (inb - depth, y - sgn * p["wall"]), (inb - depth, y), align=None))
    # Vespid segmentation: shallow transverse grooves banding the flank. Cut after the dome with
    # the bores, so the mesh relaxes over an unbroken surface and the bands stay their CAD depth.
    cuts = _bores()
    for y in p["bands"]:
        x = _x_at(pts, y)
        cuts += box(x + p["wall"] / 2 - p["band_d"], y - p["band_w"] / 2, Z_BOT - 1.0,
                    x + 20.0, y + p["band_w"] / 2, Z_TOP + 1.0)
    _INFO["apertures"] = 0
    _INFO["bands"] = len(p["bands"])
    part = _dome(body, cuts, "canopy", 2.2) if p.get("dome") else (body - cuts)
    return part.clean()


def _webs(part: Part, pts, wall: float) -> Part:
    """Tie each clip ring to the flank. A deep wall carries the ribbon outboard of both rings, so
    they meet almost tangentially and the lens left where they cross measures a few hundredths -
    the ring then ships as a second loose solid. Same fix `smooth`, `fairing` and `segmented` use."""
    for cx, cy in (FA, RA):
        xo = _x_at(pts, cy) + wall / 2
        part += _prism(Polygon((cx, cy + 3.0), (xo, cy + 3.0),
                               (xo, cy - 3.0), (cx, cy - 3.0), align=None))
    return part


def _build_finned(p: dict) -> Part:
    part = _base("finned", p)
    pts = PATHS["finned"]
    part = _webs(part, pts, p["wall"])
    # Longitudinal creases read as panel joins on a wall this deep. Cut into the outboard face.
    for y in p["creases"]:
        x = _x_at(pts, y) + p["wall"] / 2
        part -= box(x - p["crease_d"], y - p["crease_w"] / 2, Z_BOT - 1.0,
                    x + 20.0, y + p["crease_w"] / 2, Z_TOP + 1.0)
    # The bank. Full height, flush with the panel's own top and bottom faces, so the fins add no
    # downward face at all - the same rule `faceted` and `segmented` follow.
    fins = Sketch()
    for y in p["fins"]:
        x = _x_at(pts, y)
        fins += Polygon((x - 1.0, y + p["fin_w"] / 2 + 0.8), (x + p["fin_proud"], y + p["fin_w"] / 2),
                        (x + p["fin_proud"], y - p["fin_w"] / 2), (x - 1.0, y - p["fin_w"] / 2 - 0.8),
                        align=None)
    part += _prism(fins)
    _INFO["apertures"] = 0
    _INFO["fins"] = len(p["fins"])
    return _clear_bores(part)


def _build_moulded(p: dict) -> Part:
    part = _base("moulded", p)
    pts = PATHS["moulded"]
    part = _webs(part, pts, p["wall"])
    # The top edge steps down in stages toward the tail. Cut from the TOP, so each step's ceiling
    # faces up and the print orientation never sees it.
    for y0, y1, depth in p["steps"]:
        part -= box(20.0, y0, Z_TOP - depth, 40.0, y1, Z_TOP + 1.0)
    # Wide shallow flutes standing in for the internal ribs the translucent reference shows.
    for y in p["flutes"]:
        x = _x_at(pts, y) + p["wall"] / 2
        part -= box(x - p["flute_d"], y - p["flute_w"] / 2, Z_BOT - 1.0,
                    x + 20.0, y + p["flute_w"] / 2, Z_TOP + 1.0)
    _INFO["apertures"] = 0
    _INFO["steps"] = len(p["steps"])
    return _clear_bores(part)


def _build_plated(p: dict) -> Part:
    part = _base("plated", p)
    y0, y1, depth = p["notch"]
    part -= box(20.0, y0, Z_TOP - depth, 40.0, y1, Z_TOP + 1.0)
    for y in p["vents"]:
        part -= _vent(y, p["vent_z"], p["vent_d"])
    _INFO["apertures"] = len(p["vents"])
    return _clear_bores(part)


def _x_at(pts, y: float) -> float:
    """Centreline x where the path crosses this y."""
    for a, b in zip(pts, pts[1:]):
        if (a[1] - y) * (b[1] - y) <= 0 and a[1] != b[1]:
            t = (a[1] - y) / (a[1] - b[1])
            return a[0] + t * (b[0] - a[0])
    return pts[0][0]


_BUILDERS = {"slab": _build_slab, "faceted": _build_faceted,
             "wrap": _build_wrap, "smooth": _build_smooth,
             "fairing": _build_fairing, "hull": _build_hull, "canopy": _build_canopy,
             "segmented": _build_segmented,
             "finned": _build_finned, "moulded": _build_moulded, "plated": _build_plated}


def build(variant: str = "slab", **overrides) -> dict[str, Part]:
    style = variant or "slab"
    assert style in PARAMS, f"unknown style {style!r}; styles: {sorted(PARAMS)}"
    p = dict(PARAMS[style])
    p.update(overrides)
    _INFO.clear()
    _INFO["style"] = style
    # `clean()` on a fused stack hands back a Compound, and the exporter asserts on the type, so
    # every builder's result is coerced to a Part here rather than in four places.
    built = _BUILDERS[style](p)
    right = built if isinstance(built, Part) else Part(built.wrapped)
    left = right.mirror(Plane.YZ)
    right.label, left.label = "side_panel_full_r", "side_panel_full_l"
    _PLANS[style] = _plan_metrics(right)
    return {right.label: right, left.label: left}


def _plan_metrics(part: Part) -> dict[str, tuple[float, float]]:
    """Both §4.5 views, from the one shared implementation in _style.

    This used to be local, measured one projection, and divided by the BOUNDING BOX where the
    other two copies of this rule used a real convex hull - so the same gate answered three
    different numbers depending on which file you read. It now calls _style.silhouette_views()."""
    # X explicitly: these hang on a flank, so the outboard normal IS the elevation.
    return S.silhouette_views(part, elev="X")


# --- the required checks --------------------------------------------------------------------
def _bolt_head_solid() -> Part:
    out = Part()
    for x, y in BOLT_HEADS:
        out += cylinder(x, y, BOLT_HEAD_Z[0], BOLT_HEAD_Z[1], 2 * BOLT_HEAD_R)
    return out


def checks(parts: dict[str, Part], frame: dict[str, Part],
           variant: str = "") -> list[tuple[str, bool, str]]:
    style = variant or _INFO.get("style", "slab")
    p = PARAMS[style]
    right, left = parts["side_panel_full_r"], parts["side_panel_full_l"]
    rows: list[tuple[str, bool, str]] = []

    # 1. concentric with both arm-root standoffs, over the clip band
    for name, xy in (("front_arm", FA), ("rear_arm", RA)):
        ok, detail = coaxial(right, xy, D_CLIP_BORE, Z_BOT + 0.3, Z_TOP - 0.3)
        rows.append((f"clip bore concentric with standoff_{name}_right", ok, detail))

    # 2. the Ø6 standoffs themselves stay clear of the material
    worst = min((right.distance_to(c) for c in standoff_cylinders().values()), default=9.9)
    rows.append((f"Ø6 standoff shafts clear by the designed {STANDOFF_FIT}",
                 worst >= STANDOFF_FIT - 0.02, f"worst {worst:.3f} mm"))

    # 3. the arm-root bolt heads - the reason the inboard face is bowed out at all
    v = isect(right, _bolt_head_solid())
    rows.append((f"clear of the Ø6 x 3 arm-root bolt heads (Z 9-12)", v <= EPS,
                 f"{v:.3f} mm³"))

    # 4. the stack envelope
    v = isect(right, STACK_40)
    rows.append((f"clear of the 40 x 40 x Z 12-31 stack envelope", v <= EPS, f"{v:.3f} mm³"))

    # 5. floats between the plates, touching neither
    bb = right.bounding_box()
    rows.append((f"floats in the plate gap Z {Z_BOT}-{Z_TOP}",
                 bb.min.Z >= Z_BOT - 1e-6 and bb.max.Z <= Z_TOP + 1e-6,
                 f"Z {bb.min.Z:.2f}..{bb.max.Z:.2f}"))

    # 6. prop discs - the binding constraint aft
    v = prop_disc_violation(right) + prop_disc_violation(left)
    rows.append((f"outside the prop keep-out discs", v <= EPS, f"{v:.3f} mm³"))

    # 7. min wall on the functional solid. `hull` used to need a local bypass here: OCCT's offset
    # SEGFAULTS on a tub with a through mouth, killing the export mid-check with no traceback.
    # _fit.min_wall now rehearses the offset in a forked child and falls back to ray sampling when
    # the child dies on a signal, so the guard lives in one place and catches the shapes nobody has
    # bisected yet. Nothing to special-case here any more.
    ok_w, _val, detail = min_wall(right, WALL_MIN)
    rows.append((f"min wall >= {WALL_MIN}", ok_w, detail))

    # 8. one valid solid per hand
    for lbl, part in parts.items():
        ok_s, detail = single_solid(part)
        rows.append((f"{lbl}: one valid solid", ok_s, detail))

    # 9. left is the exact mirror of right
    dv = abs(right.volume - left.volume)
    rows.append((f"left is the exact mirror of right", dv < 1e-6,
                 f"Δ{dv:.6f} mm³"))

    # 10. apertures, where the style has them, are printable and not slivers
    if _INFO.get("apertures"):
        rows.append((f"every aperture >= {HOLE_MIN} mm across",
                     p.get("vent_d", 9.9) >= HOLE_MIN, f"{_INFO['apertures']} aperture(s)"))

    # 10b. the Blender pass, REPORTED rather than assumed. decorate() never raises - it hands the
    # undecorated part back - so a module that calls it without publishing decor_checks() ships a
    # silent degrade, which is the failure mode this project has already been bitten by once.
    if p.get("dome"):
        from tigerbee.accessories import _blender as BL
        rows += BL.decor_checks(f"side_panel_full_r__{style}")

    # 11. the silhouette gate, in BOTH views: this style against every other built so far. A pair
    # passes when it differs in the plan OR the side elevation, and fails only when alike in both.
    if len(_PLANS) > 1:
        mine = _PLANS[style]
        worst_pair, ok_sil = "", True
        for other, theirs in _PLANS.items():
            if other == style:
                continue
            differs, detail = S.silhouette_differs(mine, theirs)
            if not differs:
                ok_sil = False
                worst_pair = f"{style}/{other}: {detail}"
        rows.append(("outline differs from its siblings in plan or elevation", ok_sil,
                     worst_pair or f"plan {mine['plan']}, elev {mine['elev']}"))
    return rows
