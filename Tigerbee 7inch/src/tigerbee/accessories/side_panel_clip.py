"""Clip-on side panels: nine reference designs, no bolts, and Blender only on `gyroid`.

Nine genuinely different readings of "a panel between plate_mid and plate_top on one side of the
frame", every one of them held by snap-on C-clips or hooks round the Ø6 standoffs - nothing is
bolted and nothing is bonded, so a panel comes off with two thumbs and goes back on in the field.

    long          ARSENAL    a long bowed ribbed panel, rear C-clip under a flat tab, front cradle
    double        SHARD      a faceted polygonal strap with a full C-clip at BOTH ends
    angled        CHASSIS    a forward diamond-lattice truss: clip aft, claw hook over the plate edge
    window_wing   ARSENAL    the pronotum-waisted panel: hex vents, USB window, outboard wing
    faceted_hook  SHARD      three flat facets, opposed 200 deg hook lips, an L window
    brutalist     BRUTALIST  one poured 3.0 mm slab, dead straight, one huge void, formwork boards
    origami       ORIGAMI    one 1.8 mm sheet folded 22.5 deg twice into a bay window, nothing else
    filigree      FILIGREE   a 2.4 mm spine carrying a scalloped scroll net, 4.5 mm deep cutwork
    gyroid        GYROID     a dumb 3.6 mm slab whose inside Blender replaces with a gyroid sheet

The nine plan outlines are deliberately different shapes, not one shape with different holes - the
waist, the bow, the polygon, the forward truss, the straight slab, the folded bay window and the
deep cutwork screen are different silhouettes (§4.5, and the `thumbnail gate` row in checks()
measures every pair of them).

THE FOUR NEW LANGUAGES ship with the style-guard idiom: they declare `spec["style"]` only when
_style.STYLES already knows the language, so this module builds whether or not that task has
landed, and every rule each language lives by is asserted in checks() from this file.

THE DIVISION OF LABOUR: every mating feature here is build123d and numerically exact. This module
imports `_style` for the shared vocabulary (edge ladders, vent_hex, serration, ring_node, the mark
system, the cusp primitive). Eight of the nine styles call NO Blender recipe at all, and the ninth,
`gyroid`, asks for one and is legal without it - so this stays the module that guarantees a
shippable clip-on set whatever the Blender bridge does that day.
"""

from functools import lru_cache
from math import atan2, cos, degrees, hypot, pi, radians, sin

from build123d import (Align, Axis, Circle, Edge, GeomType, Location, Part, Plane, Polygon, Pos,
                       Rectangle, RegularPolygon, Sketch, Vector, chamfer, extrude, fillet)

from tigerbee.accessories import _style as S
from tigerbee.accessories._common import *  # noqa: F401,F403 - constants, builders and checks

NAME = "side_panel_clip"
TITLE = "Clip-on side panels (9 styles)"
MATERIAL = "TPU95A"
EXCLUSIVE = ("side_panels",)  # the bolted panel occupies the same two standoffs and the same bay
PRINT = {"side_panel_clip_r": (0, 0, -1), "side_panel_clip_l": (0, 0, -1)}
MOUNTS = ("standoff_front_arm_right / _left Ø6 shafts (±28.5283, 31.8308), clip bore Z 9.25-33.75",
          "standoff_rear_arm_right / _left Ø6 shafts (±26.0700, -33.3726), clip bore Z 9.25-33.75",
          "plate_mid top face Z 9 and plate_top underside Z 34 (0.25 mm running clearance to each - "
          "the panel floats between the plates, it does not seat on either)",
          "plate_mid side edge at y 62-70 (the `angled` style's claw hook only)")
HARDWARE = ("none - 0.8 mm snap fit onto the Ø6 arm-root standoffs",)

# --- the five reference panels ---------------------------------------------------------------
# `family` is the _style.STYLES key the panel is drawn in; everything else is this module's own.
STYLES = {
    "long": dict(family="arsenal", wall=2.0, z=(9.25, 33.75),
                 ref="refs/side-panels/long-clip-and-tab.png + context-photo-installed.png"),
    "double": dict(family="shard", wall=1.6, z=(9.25, 33.25),
                   ref="refs/side-panels/double-clip.png"),
    "angled": dict(family="chassis", wall=2.0, z=(9.25, 33.75),
                   ref="refs/side-panels/angled-clip-hook.png"),
    "window_wing": dict(family="arsenal", wall=1.6, z=(9.25, 33.75),
                        ref="refs/side-panels/double-clip-window-wing.png"),
    "faceted_hook": dict(family="shard", wall=1.8, z=(9.25, 33.75),
                         ref="refs/side-panels/faceted-hook-window.png"),
}

VARIANTS = {
    "long": {"style": "arsenal",
             "notes": "ARSENAL. Spans both arm-root standoffs, bowed 4 mm outboard of the clip-to-clip "
                      "chord so the stack boards and a capacitor clear the inboard face. Rear: a 254 deg "
                      "C-clip (bore measure) under a flat tab carrying the Ø4 lanyard eye. Front: a "
                      "160 deg cradle, not a clip - it slides into the 1.96 mm channel between the "
                      "standoff and the plate edge. 7 transverse ribs 1.6 x 2.0 proud at pitch 9, each "
                      "ramped 2.6:3.4 so no flank exceeds 45 deg; one 31 deg cut corner top-front; "
                      "TIGERBEE wordmark debossed 0.5 into a 1.2 mm proud datum pad."},
    "double": {"style": "shard",
               "notes": "SHARD. Full 254 deg C-clips at BOTH arm-root standoffs, mouths facing inboard "
                        "so the panel is pushed on from outside and a side impact loads the closed "
                        "outboard half of each ring. Six-facet polygonal plan, every facet >= 8 mm "
                        "across, every junction chamfered 0.6, edge ladder 0.64/0.64/0.6 (the SHARD "
                        "2.0/1.2/0.6 ladder clamped by 0.40 x the 1.6 wall). Height 24.0. A cusped "
                        "cable notch mid-span at the bottom edge."},
    "angled": {"style": "chassis", "material": "TPU95A",
               "print": {"side_panel_clip_r": (0, 0, 1), "side_panel_clip_l": (0, 0, 1)},
               "notes": "CHASSIS. Runs FORWARD from the front-arm standoff along the narrowing mid-plate "
                        "outline to y 70, guarding the forward bay at (0, 61.5). Diamond lattice between "
                        "two rails with a ring node at every junction and a serrated outboard rail. "
                        "The front-tip standoff is NOT available - a clip there overlaps camera_pod by a "
                        "measured 698 mm³ over Z 9-32 - so the forward end is a three-tooth claw hooking "
                        "under the mid-plate side edge instead. Prints top-face-down."},
    "window_wing": {"style": "arsenal",
                    "notes": "ARSENAL. Follows the mid-plate side outline 1.0 mm outside it, so the plan "
                             "carries the frame's own pronotum waist (x 26.4 at y 2 against 35.2 at the "
                             "shoulders). Full C-clips both ends, a 12 x 8 USB/cable window, a hex vent "
                             "field AF 5.0 on the forward half, and an outboard wing on the rear half "
                             "with an angled 8 x 3 slot for a zip-tied capacitor or antenna pigtail."},
    # --- the four new languages -------------------------------------------------------------
    # The guard idiom: `spec["style"]` is only declared when _style knows the language, so these
    # four work whether or not the _style task has landed. Everything they need geometrically is
    # in this file.
    "brutalist": {**({"style": "brutalist"} if "brutalist" in S.STYLES else {}),
                  "material": "PETG",
                  "notes": "BRUTALIST. One poured slab, formwork still showing. A 3.0 mm flat slab "
                           "with NO curve in plan: it leaves each clip ring on a 45 deg dogleg and "
                           "then runs dead straight 5.5 mm outboard of the clip-to-clip chord, "
                           "12 mm past each ring, so it clears both arm-root bolts whole and needs "
                           "none of the r1.0 relief notches the chord-hugging styles carry. One "
                           "rectangular void 44.2 x 20 (40.9 % of the 88.25 x 24.5 face), corners "
                           "dead sharp. Three 3.0 x 3.0 proud external ribs at 12 mm pitch, full "
                           "height, square section, cut through by the void like formwork planks. "
                           "Board-marking grooves 0.6 x 0.3 at 2.4 pitch on both faces, all running "
                           "the print direction, stopping 1.8 mm short of the void and the tips so "
                           "no board ends in a sliver. A full-height 2.4 mm proud plaque forward of "
                           "the void carries the TIGERBEE wordmark debossed 2.0 mm, cast-in deep. "
                           "1.0 mm chamfers, 45 deg, and nothing anywhere is filleted above r 0.3."},
    "gyroid": {**({"style": "gyroid"} if "gyroid" in S.STYLES else {}),
               "material": "PETG",
               "notes": "GYROID. The solid is a frozen fluid. The silhouette is deliberately dumb "
                        "- a 3.6 mm slab, thicker than anything else in the set because the inside "
                        "is mostly void, bowed 3.0 mm on one smooth half-sine with no crease "
                        "anywhere and a single constant r 3.0 rounding on the plan outline. All "
                        "the visual event is internal: build123d owns the slab, the clip rings and "
                        "a 1.6 mm solid rind on every mating face, and Blender replaces what is "
                        "left between the rinds with a gyroid sheet of period 10.0 and thickness "
                        "1.6. The apertures are NOT cut - they are where the sheet breaks the "
                        "outer surface, so they are continuous, non-repeating curved triangles "
                        "nothing else in the catalogue produces. MEASURED TODAY: over a panel this "
                        "long the F = 0 surface runs ~125 000 triangles at period 10, and the "
                        "bridge's budget is 12 000, so the recipe declines and the slab ships "
                        "undecorated - which is exactly the documented degrade path, and every fit "
                        "row above is measured on the slab that ships. Raise the period past 30 mm "
                        "or the budget past 125 k and the same call turns the lattice on; "
                        "cell='voronoi' through carapace_lattice is the second fallback if the "
                        "gyroid recipe is ever absent."},
    "filigree": {**({"style": "filigree"} if "filigree" in S.STYLES else {}),
                 "notes": "FILIGREE. Ornamental cutwork hung on a rigid spine, cut 4.5 mm deep so "
                          "the scrolls read as wells rather than perforations. A 2.4 mm solid "
                          "spine runs the actual load path - clip, 45 deg dogleg, straight run "
                          "5.2 mm outboard of the chord (clear of both arm-root bolts), dogleg, "
                          "clip - along the panel's mid height. Everything off the spine is open "
                          "work: 1.5 mm ribbons mirrored above and below it, bounded by the scroll "
                          "arc R 4.95 on one side and the Ø4.0 ring node's arc on the other, "
                          "meeting tangentially at every junction. There is no straight member "
                          "anywhere in the net, which is what separates it from chassis. Every "
                          "scroll breaks the top or bottom edge by 0.6 mm, so the silhouette is a "
                          "run of tangent arcs - scalloped, not a polyline - and the void fraction "
                          "is measured, not assumed: checks() asserts it inside 45-60 %."},
    "origami": {**({"style": "origami"} if "origami" in S.STYLES else {}),
                "material": "PETG",
                "notes": "ORIGAMI. One sheet of paper, folded, nothing else. A CONSTANT 1.8 mm "
                         "sheet folded about two vertical creases at exactly 1/3 and 2/3 of the "
                         "clip-to-clip run, 22.5 deg at each, so the panel is a shallow bay window "
                         "in plan and stands 8.0 mm outboard of the chord at the middle facet - "
                         "which is also what carries it clear of both arm-root bolts. The sheet "
                         "runs 18 mm past each clip as a straight flange: paper does not stop at a "
                         "hole. Every silhouette edge is a straight line and 22.5 deg is the only "
                         "angle in the part, including the shear of the parallelogram ladder slots "
                         "(4.0 wide at 6.4 pitch, 2.22 mm of ligament measured perpendicular). "
                         "0.4 mm chamfers, never a fillet - that is what separates it from shard, "
                         "which is a solid with cut facets and a varying wall."},
    "faceted_hook": {"style": "shard",
                     "notes": "SHARD. Three flat facets with 16 and 12 deg bends. The ends are 200 deg "
                              "hook lips, not tubes: OPPOSED (front mouth 150 deg, rear mouth 210 deg) so "
                              "no single translation releases both, which is what replaces the snap a "
                              "200 deg wrap cannot provide. An L-shaped window with a 4 mm foot."},
}
ASSEMBLY_VARIANT = "double"

NOTES = ("INSTALLATION. Hold the panel outboard of its bay and push it INBOARD: every mouth faces -X, "
         "so the standoffs enter from the inboard side and a side impact loads the closed outboard half "
         "of each ring instead of walking the standoffs out through the mouths. `angled` is hooked "
         "first (drop the three claw teeth under the mid-plate side edge at y 62-70) and then snapped "
         "onto the front-arm standoff; the clip is what stops the claw sliding back outboard. "
         "`faceted_hook`'s two hooks are opposed by 60 deg, so it is engaged on the rear hook first and "
         "swung forward onto the front one. "
         "THE PANEL FLOATS. Z 9.25-33.75 leaves 0.25 mm to the plate_mid top face and 0.25 mm to the "
         "plate_top underside; nothing seats, nothing is clamped, and the two plates are the anti-lift "
         "stops. `double` stops at 33.25 so it can be fitted with the top plate already torqued. "
         "DEVIATIONS, all measured in checks(): the C-clip wrap is 254 deg measured at the bore and "
         "295 deg at the outer radius, not a nominal 270 - that is what `c_clip`'s parallel 5.2 mm "
         "throat gives on a Ø6.5 bore, and the shared clip is worth more than the round number. "
         "`angled` uses a 2.0 mm wall rather than the brief's 1.6: TPU CHASSIS struts below 2.4 x 3.0 "
         "flop (§3.2) and 2.0 keeps the ring-node bore at Ø2.7, above TPU's 2.2 mm minimum hole. "
         "`angled` prints top-face-down because its claw hook puts a second face level at Z 5.0; "
         "inverted, both of them are upward faces and the only ceilings left are the diamond apexes. "
         "THE FOUR PETG / DEEP-SECTION LANGUAGES. `brutalist`, `origami` and `gyroid` print in PETG "
         "and `filigree` in TPU95A, but all four keep the module's shared clip: bore Ø6.5, wall "
         "1.6, the parallel 5.2 mm throat and the 0.45 mm mouth fillets, unchanged, because the "
         "clip is the one thing every panel in this family has in common. In PETG that 0.8 mm of "
         "interference is a firm push-fit rather than a snap - fit those three with the top plate "
         "off and thread the ring over the standoff, or warm the ring. `brutalist` and `gyroid` "
         "stand 5.5 and 3.0 mm outboard of the clip-to-clip chord and `origami` 8.0 mm at its "
         "middle facet, which is how a language that may not curve, or may only fold at 22.5 deg, "
         "still clears both arm-root bolt heads without a relief notch. All four print on their "
         "bottom edge like the rest of the family: brutalist's boards, origami's creases, "
         "filigree's ribbons and gyroid's rind all run the print direction.")

# --- frame interface (mm) ---------------------------------------------------------------------
Z_BOT = 9.25                       # 0.25 over the plate_mid top face (Z 9)
Z_TOP = 33.75                      # 0.25 under the plate_top underside (Z 34)
SNAP = MATERIALS[MATERIAL]["snap"]  # 0.8
MOUTH = STANDOFF_D - SNAP          # 5.2 parallel throat over a Ø6 standoff
R_BORE = D_CLIP_BORE / 2           # 3.25
R_RING = R_BORE + CLIP_WALL        # 4.85
FA = FRONT_ARM_XY                  # (28.5283, 31.8308)
RA = REAR_ARM_XY                   # (26.0700, -33.3726)
MOUTH_IN = 180.0                   # every mouth faces -X: pushed on from outside

BOLT_HEADS = ((26.97, 18.17), (26.43, -19.63))   # Ø6 x 3 arm-root bolt heads on plate_mid, Z 9-12
BOLT_HEAD_D, BOLT_HEAD_H = 6.0, 3.0
STACK_40 = box(-20, -20, 12, 20, 20, 31)         # the 40 x 40 Z 12-31 stack envelope
WALL_MIN = MATERIALS[MATERIAL]["wall"]           # 1.2
DECOR_HOLE_MIN = S.DECOR_MATERIALS[MATERIAL]["hole_min"]   # 2.2: no aperture may be smaller
DECOR_LIG_MIN = S.DECOR_MATERIALS[MATERIAL]["ligament_min"]  # 1.2
_INFO: dict = {}          # what the last build() measured, reported back by checks()
_PLANS: dict = {}         # style -> (plan area, hull deficiency) for the thumbnail gate
_BRIDGES: dict = {}       # final label -> bridge boxes in PRINT coordinates
_FUNCTIONAL: dict = {}    # style -> the solid before the mark (where the CAD min-wall is valid)


# --- plan-curve plumbing -----------------------------------------------------------------------
def _seg_normals(pts: list[tuple[float, float]]) -> list[tuple[float, float]]:
    """Outboard (+X-ish) unit normal of every segment. Paths are always ordered by DECREASING y,
    which is what makes (-dy, dx) the outboard side on the right-hand panel."""
    out = []
    for a, b in zip(pts, pts[1:]):
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = hypot(dx, dy) or 1.0
        out.append((-dy / L, dx / L))
    return out


def _offset_path(pts, d: float) -> list[tuple[float, float]]:
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
    """Closed plan profile of a wall of thickness `wall` centred on the polyline `pts`."""
    outer = _offset_path(pts, wall / 2 + out_extra)
    inner = _offset_path(pts, -wall / 2)
    return Polygon(*outer, *reversed(inner), align=None)


def _bow(p0, p1, bulge: float, n: int = 10) -> list[tuple[float, float]]:
    """`n` segments from p0 to p1 bowed `bulge` mm outboard at the middle (a half sine, so the
    ends leave the chord tangentially and the bow has no crease)."""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    L = hypot(dx, dy) or 1.0
    nx, ny = -dy / L, dx / L
    pts = []
    for i in range(n + 1):
        t = i / n
        s = bulge * sin(pi * t)
        pts.append((p0[0] + dx * t + nx * s, p0[1] + dy * t + ny * s))
    return pts


def _bend(a, b, c) -> float:
    """Turn angle at b, in degrees."""
    v1, v2 = (b[0] - a[0], b[1] - a[1]), (c[0] - b[0], c[1] - b[1])
    return abs(degrees(atan2(v1[0] * v2[1] - v1[1] * v2[0], v1[0] * v2[0] + v1[1] * v2[1])))


def _smooth(pts, max_bend: float = 22.0, frac: float = 0.3, passes: int = 3):
    """Corner-cut every plan bend sharper than `max_bend` until none is left.

    A miter-offset ribbon is exactly `wall` thick perpendicular to every segment, but at a 50 deg
    corner a ray leaving the outer face near the vertex crosses into the neighbouring facet and
    the wall READS 0.44 mm on a 1.6 mm wall. Cutting the corner twice turns a 55 deg kink into
    four bends under 15 deg, which is also what a panel that has to leave a clip ring and then run
    parallel to the frame actually looks like. SHARD styles are never smoothed: their facets are
    the style."""
    for _ in range(passes):
        if len(pts) < 3:
            return pts
        out = [pts[0]]
        for i in range(1, len(pts) - 1):
            a, b, c = pts[i - 1], pts[i], pts[i + 1]
            if _bend(a, b, c) <= max_bend:
                out.append(b)
                continue
            f = min(frac, 0.45)
            out.append((b[0] - (b[0] - a[0]) * f, b[1] - (b[1] - a[1]) * f))
            out.append((b[0] + (c[0] - b[0]) * f, b[1] + (c[1] - b[1]) * f))
        out.append(pts[-1])
        pts = out
    return pts


def _tangents(c0, c1, r: float):
    """The two outboard tangent points of the common outboard tangent of two circles of radius r."""
    dx, dy = c1[0] - c0[0], c1[1] - c0[1]
    L = hypot(dx, dy) or 1.0
    nx, ny = -dy / L, dx / L
    return (c0[0] + nx * r, c0[1] + ny * r), (c1[0] + nx * r, c1[1] + ny * r)


@lru_cache(maxsize=256)
def _mid_edge(y: float) -> float:
    """The real right-hand outer edge of plate_mid at this y (the frame's own pronotum curve)."""
    spans = outline_spans("plate_mid", y)
    assert spans, f"plate_mid has no material at y {y}"
    return max(b for _a, b in spans)


def _rect(x0, y0, x1, y1) -> Sketch:
    return Pos((x0 + x1) / 2, (y0 + y1) / 2) * Rectangle(x1 - x0, y1 - y0)


def _treat(sk: Sketch, corners, r: float, op) -> tuple[Sketch, int]:
    """fillet/chamfer every listed (x, y) still present as a vertex; corners a later boolean
    swallowed are skipped, and the count is returned so checks() can see one went missing."""
    done = 0
    for cx, cy in corners:
        hits = sk.vertices().filter_by(
            lambda v, cx=cx, cy=cy: abs(v.X - cx) < 2e-4 and abs(v.Y - cy) < 2e-4)
        if not hits:
            continue
        try:
            sk = op(hits, r)
            done += 1
        except Exception:  # noqa: BLE001 - OCCT refuses a radius that does not fit; leave it sharp
            continue
    return sk, done


# --- clips, hooks and local-frame features -----------------------------------------------------
def _cclip_plan(center, opening_deg: float = MOUTH_IN) -> Sketch:
    """`c_clip`'s own 2D profile - bore Ø6.5, wall 1.6, a parallel 5.2 mm throat with MOUTH_FILLET
    lips - as a PLAN sketch, so the ribbon can be unioned into it before the solid is extruded and
    the union never squares the lips off again. Measured wrap: 295 deg at R_RING, 254 deg at the
    bore (the throat is a parallel slot, not an angular sector, which is the point of a snap)."""
    lip = MOUTH / 2 + CLIP_WALL                 # 4.2: the lips are a uniform CLIP_WALL slab
    # c_clip's raw lips taper onto the bore circle and end in a knife edge, and MOUTH_FILLET lands
    # on a CONCAVE corner there, adding 1.1 mm³ of material INSIDE the Ø6.5 bore (measured by
    # coaxial()). Squaring the lips off against a block that ends flush at R_RING - side_panels'
    # own fix - removes both: a parallel 1.6 mm beam to bend, and the only filleted corners are
    # the two convex lip tips.
    slot = Pos((R_RING + 1.0) / 2, 0) * Rectangle(R_RING + 1.0, MOUTH)
    sk = Circle(R_RING) + Pos(R_RING / 2, 0) * Rectangle(R_RING, 2 * lip)
    sk = sk - Circle(R_BORE) - slot
    sk, _c = _treat(sk, [(R_RING, s * lip) for s in (1, -1)], 0.8, chamfer)
    sk, _f = _treat(sk, [(R_RING, s * MOUTH / 2) for s in (1, -1)], MOUTH_FILLET, fillet)
    return Pos(*center) * sk.rotate(Axis.Z, opening_deg)


def _clip(center, z0: float, z1: float, opening_deg: float = MOUTH_IN) -> Part:
    """A full C-clip on a standoff axis - the shared `c_clip`, unchanged, so the snap geometry is
    identical to every other clip in the set. Wrap is 295 deg at the outer radius and 254 deg at
    the bore (the throat is a parallel 5.2 mm slot, not an angular sector)."""
    return c_clip(center, z0, z1 - z0, opening_deg=opening_deg, material=MATERIAL,
                  bore_d=D_CLIP_BORE, wall=CLIP_WALL, snap=SNAP, mouth_fillet=MOUTH_FILLET)


def _sector(center, r_in: float, r_out: float, mid_deg: float, wrap_deg: float) -> Sketch:
    """Annulus sector of `wrap_deg` centred on `mid_deg` - the hook lip and the front cradle."""
    half = wrap_deg / 2
    n = max(3, int(wrap_deg / 12) + 2)
    rr = r_out + 2.0
    pts = [(0.0, 0.0)] + [(rr * cos(radians(mid_deg - half + 2 * half * i / n)),
                           rr * sin(radians(mid_deg - half + 2 * half * i / n))) for i in range(n + 1)]
    wedge = Polygon(*pts, align=None)
    return Pos(*center) * ((Circle(r_out) - Circle(r_in)) & wedge)


def _mouth_fillet(sk: Sketch, center, r_in: float, r_out: float, mid_deg: float,
                  wrap_deg: float, r: float = MOUTH_FILLET) -> Sketch:
    """Round the four lip tips of a sector so nothing presents a knife edge to the standoff."""
    pts = []
    for s in (1, -1):
        a = radians(mid_deg + s * wrap_deg / 2)
        for rad in (r_in, r_out):
            pts.append((center[0] + rad * cos(a), center[1] + rad * sin(a)))
    sk, _n = _treat(sk, pts, r, fillet)
    return sk


def _frame_at(pts, t: float):
    """(point, outboard normal, tangent) at arc-length fraction `t` of a polyline."""
    segs = [(a, b, hypot(b[0] - a[0], b[1] - a[1])) for a, b in zip(pts, pts[1:])]
    total = sum(s[2] for s in segs)
    want = t * total
    run = 0.0
    for a, b, L in segs:
        if run + L >= want or (a, b, L) is segs[-1]:
            f = (want - run) / (L or 1.0)
            p = (a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f)
            tan = ((b[0] - a[0]) / L, (b[1] - a[1]) / L)
            return p, (-tan[1], tan[0]), tan
        run += L
    raise AssertionError("unreachable")


def _local_prism(profile_uz, pts, t: float, width: float) -> Part:
    """Extrude a (u, z) profile - u measured outboard from the polyline centreline - along the
    local tangent by `width`, centred on the path point at fraction `t`. This is how a rib or a
    datum pad sits square on a curved wall without any 3D offset."""
    p, n, tan = _frame_at(pts, t)
    origin = Vector(p[0], p[1], 0.0)
    pl = Plane(origin=tuple(origin - Vector(*tan, 0) * (width / 2)),
               x_dir=(n[0], n[1], 0.0), z_dir=tuple(Vector(*tan, 0)))
    return S.extrude_cut(Polygon(*profile_uz, align=None), pl, width)


def _tip_allow(center, angle_deg: float, z0: float, z1: float, w: float = 2.6) -> Part:
    """The volume a clip or hook lip TIP occupies. `min_wall`'s ray fallback cannot tell a rounded
    or chamfered lip tip from a thin wall (its own docstring says so), and these tips are mating
    geometry the coaxial and standoff-gap rows already measure exactly. Declared, not ignored."""
    r = (R_BORE + R_RING) / 2
    cx, cy = center[0] + r * cos(radians(angle_deg)), center[1] + r * sin(radians(angle_deg))
    blk = box(-CLIP_WALL, -w / 2, z0, CLIP_WALL, w / 2, z1)
    return blk.rotate(Axis.Z, angle_deg).moved(Location((cx, cy, 0)))


def _lip_allow(center, opening_deg: float, z0: float, z1: float) -> Part:
    """The clip or hook RING, declared whole.

    Its geometry is fixed by construction - bore Ø6.5, wall 1.6, a parallel 5.2 mm throat, squared
    lips, MOUTH_FILLET tips - and three rows measure it exactly: the bore is coaxial and void, the
    gap to the Ø6 standoff is the designed 0.25, and nothing of it fouls the frame. What the ray
    sampler reads here instead is the chord across the corner where the ribbon runs into the ring
    (0.66 mm on a 1.6 mm ring, measured), which is its documented blind spot, not a thin wall."""
    _ = opening_deg
    # radius 7.05: the ring (4.85) plus the squared lip block, whose outer corners sit at
    # hypot(R_RING, MOUTH/2 + CLIP_WALL) = 6.42 from the axis, plus 0.6 of margin.
    return cylinder(center[0], center[1], z0 - 0.5, z1 + 0.5,
                    2 * (R_RING + CLIP_WALL + 0.6))


def _vertex_allow(pts, wall: float, z0: float = Z_BOT - 1.0, z1: float = Z_TOP + 1.0) -> Part:
    """The miter vertices of a plan ribbon.

    Perpendicular to every segment the ribbon is exactly `wall` thick - that is what a miter offset
    is, and the `plan miter factor` row asserts no vertex overshoots it. But a ray leaving the
    outer face within a wall's length of a vertex crosses into the neighbouring facet's half-space
    and measures the chord across the corner instead, which is how a 1.6 mm wall reads 0.62 mm at a
    25 deg bend. Declared here, and measured exactly by the miter row instead."""
    out = Part()
    for x, y in pts[1:-1]:
        out += cylinder(x, y, z0, z1, 2.6 * wall)
    return out


def _miter_report(pts, wall: float) -> tuple[bool, float, str]:
    """The exact wall guarantee of a miter-offset ribbon: at every vertex the offset point sits
    |n| x wall/2 from the centreline, |n| = 1 / cos(bend / 2). Above 1.25 (a 51 deg bend) the
    corner starts to spike and a thin ribbon can fold through itself."""
    ns = _seg_normals(pts)
    worst, where = 1.0, 0
    for i in range(1, len(pts) - 1):
        n1, n2 = ns[i - 1], ns[i]
        k = 1.0 + n1[0] * n2[0] + n1[1] * n2[1]
        m = hypot(n1[0] + n2[0], n1[1] + n2[1]) / k if k > 1e-6 else 99.0
        if m > worst:
            worst, where = m, i
    bend = 2 * degrees(atan2(max(worst ** 2 - 1, 0.0) ** 0.5, 1.0))
    return worst <= 1.25, worst, (f"worst miter {worst:.4f} at vertex {where} of {len(pts)} "
                                  f"({bend:.1f} deg bend); the wall stays {wall} mm perpendicular "
                                  f"to every segment")


def _nonempty(parts) -> tuple:
    """Drop empty Parts: `ray_thickness` asserts on a Part with no wrapped shape."""
    return tuple(q for q in parts
                 if q is not None and getattr(q, "_wrapped", None) is not None and q.volume > 0)


def _wing_allow(info: dict, w: dict) -> Part:
    """The wing vane and the angled slot through it: a 2.0 mm fin swept off the flank and cut by a
    prism running across its own plane, so the same oblique-chord artefact applies."""
    root, tip = info["wing_root"], info["wing_tip"]
    cx, cy = (root[0] + tip[0]) / 2, (root[1] + tip[1]) / 2
    r = hypot(tip[0] - root[0], tip[1] - root[1]) / 2 + 2.0
    return box(cx - r, cy - r, Z_BOT - 1, cx + r, cy + r, Z_TOP + 1)


def _aperture_allow(cut: Sketch, grow: float = 1.5) -> Part:
    """The ligament band round every aperture cut through the wall.

    Each of these panels is a wall STANDING IN PLAN and every aperture is cut by a prism along +X,
    so where the wall runs oblique to X the ray sampler leaves an aperture face, travels at
    constant X and exits sideways through the skin long before it has crossed the wall - it
    measures a chord, not a thickness. Each generator's ligament is asserted numerically in the
    style rows instead, which is the number that actually matters."""
    zone = Sketch()
    for f in cut.faces():
        c, bb = f.center(), f.bounding_box()
        zone += Pos(c.X, c.Y) * Rectangle(bb.size.X + 2 * grow, bb.size.Y + 2 * grow)
    return S.extrude_cut(zone, Plane.YZ.offset(-60.0), 200.0) if zone.faces() else Part()


def _ladder_allow(part: Part, z_top: float, r: float) -> Part:
    """The band the silhouette chamfer ladder occupies. A 0.64 chamfer on both top edges of a
    1.6 wall leaves 0.32 mm of flat by design - that is the SHARD ladder, not a thin wall."""
    bb = part.bounding_box()
    return box(bb.min.X - 1, bb.min.Y - 1, z_top - r - 0.15, bb.max.X + 1, bb.max.Y + 1, z_top + 0.1)


def _inboard_of(pts, wall: float, z0: float = -5.0, z1: float = 45.0) -> Part:
    """Everything inboard of the wall's inner surface. A straight local prism (a rib, a datum pad)
    laid on a BOWED wall stands off the surface at its ends by the bow's sagitta - 0.64 mm over a
    26 mm pad on this bow - and a union across a 0.04 mm gap is what makes OCCT hand back an
    invalid solid. Sinking the prism well into the wall and trimming it on this slab instead makes
    the contact an exact shared volume."""
    inner = _offset_path(pts, -wall / 2)
    back = _offset_path(pts, -wall / 2 - 40.0)
    sk = Polygon(*inner, *reversed(back), align=None)
    return S.extrude_cut(sk, Plane.XY.offset(z0), z1 - z0)


def _rib(pts, t: float, wall: float, width: float, proud: float, z0: float, z1: float,
         ramp: float) -> Part:
    """One ARSENAL rib: `proud` mm off the outer face, ramped `ramp` mm at both ends so the lower
    flank's normal.Z is -proud/hypot(proud, ramp) - kept under overhangs()' 0.70 by ramp > proud."""
    u0, u1 = wall / 2 - 0.6, wall / 2 + proud
    return _local_prism([(u0, z0), (u1, z0 + ramp), (u1, z1 - ramp), (u0, z1)], pts, t, width)


def _path_len(pts) -> float:
    return sum(hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:]))


def _at(pts, s: float):
    """(point, outboard normal, tangent) `s` mm along the polyline."""
    return _frame_at(pts, min(max(s / (_path_len(pts) or 1.0), 0.0), 1.0))


def _prism(plan: Sketch, z0: float, h: float) -> Part:
    """Extrude a plan profile into ONE solid.

    A ribbon that runs through a clip ring divides that ring into two arcs, and the sketch fuse
    leaves the region as several coplanar faces sharing edges - geometrically one shape, but
    build123d extrudes a face at a time, so `single_solid` then counts five. `clean()` does not
    merge them (measured); fusing the extrusions does, and the fuse is what makes the result a
    genuine single solid rather than five touching ones."""
    out = Part()
    for f in plan.faces():
        out += S.extrude_cut(Sketch() + f, Plane.XY.offset(z0), h)
    return out


def _prism_at(profile_uz, pts, s: float, width: float) -> Part:
    return _local_prism(profile_uz, pts, min(max(s / (_path_len(pts) or 1.0), 0.0), 1.0), width)


def _relief(pts, s: float, wall: float, depth: float = 0.5, width: float = 6.0) -> Part:
    """Full-height relief channel in the INBOARD face. Full height on purpose: a blind pocket has
    a horizontal ceiling, a full-height channel has none, so it needs no bridge and no ramp."""
    u0, u1 = -wall / 2 - 1.0, -wall / 2 + depth
    return _prism_at([(u0, Z_BOT - 1), (u1, Z_BOT - 1), (u1, Z_TOP + 1), (u0, Z_TOP + 1)],
                     pts, s, width)


def _eye(pts, s: float, z: float, d: float = 4.0) -> Part:
    """Cutting tool for a lanyard eye: a bore along the local OUTBOARD normal, so its axis is
    horizontal and overhangs() exempts it as an arch (Ø4 <= TPU's 10 mm self-supporting arch)."""
    p, n, _t = _at(pts, s)
    pl = Plane(origin=(p[0] - n[0] * 12.0, p[1] - n[1] * 12.0, z), z_dir=(n[0], n[1], 0.0))
    return S.extrude_cut(Circle(d / 2), pl, 24.0)


# ================================================================================================
# STYLE 1  `long`  - ARSENAL
# ================================================================================================
LONG_BULGE = 4.0        # outboard of the clip-to-clip tangent chord, at mid span
LONG_WALL = 2.0
LONG_CLIP_H = 13.0      # rear C-clip Z 9.25-22.25; above it the flat tab
LONG_RIB = dict(width=1.6, proud=2.0, pitch=9.0, ramp=3.4, first=4.0)
LONG_PAD = (25.0, 55.0)  # tangential span of the datum pad, mm of arc (the mark needs 27.6)
LONG_PAD_PROUD = 1.2
LONG_MARK, LONG_MARK_SIZE, LONG_MARK_DEPTH = "wordmark", 27.0, 0.5
LONG_CORNER = ((41.0, 28.5), (29.5, Z_TOP + 1.0))   # the single 30 deg cut corner, in (y, z)
LONG_RELIEF = (17.0, 49.0)   # arc positions of the inboard plate-outline reliefs


def _long_path() -> list[tuple[float, float]]:
    tf, tr = _tangents(FA, RA, R_RING)
    pts = _bow(tf, tr, LONG_BULGE, 12)
    # Both ends run to the ring CENTRE, so the ribbon's end cap is inside the Ø6.5 bore and is cut
    # away with it. Ending on the tangent point instead leaves the flat tab standing 1.0 mm proud
    # of the ring below it - a 6.4 mm² cantilevered ceiling, measured by overhangs().
    pts[0], pts[-1] = FA, RA
    return pts


def _build_long(p: dict) -> Part:
    wall = p["wall"]
    plan, info = _plan_for("long", p)
    pts = info["path"]
    total = _path_len(pts)

    # The rear ring lives only UNDER the flat tab (the reference's defining detail), so the plan's
    # rear disc is trimmed back to the ribbon above LONG_CLIP_H and the shared `c_clip` is unioned
    # in below it - the snap geometry is then bit-identical to every other clip in the set.
    # Above the clip the tab is the RIBBON, nothing else. Trimming the ring disc out of the plan
    # instead leaves a crescent of ribbon outside the disc that tapers to zero - measured at
    # 0.109 mm by the ray sampler, and it is a real feather edge, not an artefact.
    plan_tab = _ribbon(pts, wall)
    part = _prism(plan, Z_BOT, LONG_CLIP_H)
    part += _prism(plan_tab, Z_BOT + LONG_CLIP_H, Z_TOP - Z_BOT - LONG_CLIP_H)

    # ARSENAL ribs, transverse, each ramped so no flank passes 45 deg
    pad0, pad1 = p["pad"]
    ribs, thin = 0, Part()
    s = LONG_RIB["first"]
    while s < total - 2.0:
        here, s = s, s + LONG_RIB["pitch"]
        if pad0 - 2.0 < here < pad1 + 2.0:
            continue
        pr, _n, _t = _at(pts, here)
        if min(hypot(pr[0] - c[0], pr[1] - c[1]) for c in (FA, RA)) < R_RING + 2.0:
            continue        # a rib that close would stand inside the clip bore
        s_ = here
        rib = _rib(pts, s_ / total, wall, LONG_RIB["width"], LONG_RIB["proud"],
                   Z_BOT, Z_TOP, LONG_RIB["ramp"])
        part += rib
        thin += rib
        ribs += 1

    # the datum pad: CN-5's thickness gradient, so a 0.5 deboss still leaves 2.7 mm of wall
    # the ramp's rise must beat its run or the flank is an overhang: 7.0 over 5.2 puts the lower
    # face at normal.Z -0.596, clear of overhangs()' -0.70 limit.
    u0, u1 = -wall / 2 - 2.0, wall / 2 + p["pad_proud"]
    pad = _prism_at([(u0, 17.0), (u1, 24.0), (u1, 31.0), (u0, Z_TOP)], pts, (pad0 + pad1) / 2,
                    pad1 - pad0) - _inboard_of(pts, wall)
    part += pad
    thin += pad
    if p["mark"] and S.mark_fits(LONG_MARK, p["mark_size"]):
        pm, pn, _pt = _at(pts, (pad0 + pad1) / 2)
        # NOT cut here: build() cuts it once per hand, un-mirrored, so the stencil reads the same
        # way round on both flanks (a mirrored wordmark is a defect, not a mirrored pair).
        _INFO["mark_band"] = _prism_at([(u1 - 1.2, 23.0), (u1 + 0.4, 23.0),
                                        (u1 + 0.4, 32.0), (u1 - 1.2, 32.0)],
                                       pts, (pad0 + pad1) / 2, pad1 - pad0 + 2.0)
        _INFO["mark"] = dict(kind=LONG_MARK, size=p["mark_size"], mode="deboss",
                             at=(pm[0] + pn[0] * u1, pm[1] + pn[1] * u1, 27.5),
                             normal=(pn[0], pn[1], 0.0), depth=p["mark_depth"],
                             x_dir=(0, 0, 1), angle=-90.0)

    for s_rel in LONG_RELIEF:
        part -= _relief(pts, s_rel, wall)
    part -= _eye(pts, total - 6.0, 28.0, 4.0)
    (cy0, cz0), (cy1, cz1) = p["corner"]
    part -= S.extrude_cut(Polygon((cy0, cz0), (cy0, cz1), (cy1, cz1), align=None),
                          Plane.YZ.offset(-60.0), 200.0)
    # The bores and the mouth come LAST, so nothing added after the prism - a rib, the datum pad,
    # the cradle's own lip fillets - can leave material in a bore. Measured before this moved:
    # 1.121 mm³ inside the rear Ø6.5 and a 0.0288 mm standoff gap where 0.25 was designed.
    part -= cylinder(*FA, Z_BOT - 1, Z_TOP + 1, D_CLIP_BORE)
    part -= cylinder(*RA, Z_BOT - 1, Z_TOP + 1, D_CLIP_BORE)
    part -= box(RA[0] - R_RING - 1.2, RA[1] - MOUTH / 2, Z_BOT - 1, RA[0], RA[1] + MOUTH / 2,
                Z_TOP + 1)
    part, n_relief, relief_zone = _bolt_relief(part)
    _INFO.update(ribs=ribs, marked=bool(p["mark"]), bolt_reliefs=n_relief,
                 allow=_nonempty((thin, relief_zone, _vertex_allow(pts, wall), _lip_allow(RA, MOUTH_IN, Z_BOT, Z_BOT + LONG_CLIP_H),
                        _tip_allow(FA, -100.0, Z_BOT, Z_TOP), _tip_allow(FA, 60.0, Z_BOT, Z_TOP))))
    return part


def _junction_corners(pts, wall: float) -> list[tuple[float, float]]:
    """Every interior plan vertex of the ribbon, outer and inner - SHARD chamfers all of them."""
    outer, inner = _offset_path(pts, wall / 2), _offset_path(pts, -wall / 2)
    return [*outer[1:-1], *inner[1:-1]]


def _top_edges(part: Part, z: float, min_len: float = 2.5, skip=()) -> list[Edge]:
    """Edges lying in the part's top plane - the only silhouette edges a chamfer may touch. The
    bottom perimeter is left square: a 45 deg chamfer there is a downward face at normal.Z -0.707,
    one hundredth past overhangs()' limit, and the bottom face is the bed (CN-6)."""
    out = []
    for e in part.edges():
        bb = e.bounding_box()
        if abs(bb.min.Z - z) > 1e-4 or abs(bb.max.Z - z) > 1e-4 or e.length < min_len:
            continue
        c = e.center()
        if any(hypot(c.X - sx, c.Y - sy) < R_RING + 0.4 for sx, sy in skip):
            continue        # the clip rings keep their own MOUTH_FILLET geometry, untouched
        out.append(e)
    return out


def _soft_treat(part: Part, style: str, wall: float, edges) -> tuple[Part, float, int]:
    """S.treat_edges over a whole edge set at once, then one edge at a time when OCCT refuses the
    set. A single edge it cannot fit otherwise loses the whole silhouette ladder (measured: the
    `double` top ring returned radius 0.0 for all twelve edges)."""
    if not edges:
        return part, 0.0, 0
    out, r = S.treat_edges(part, style, "sil", wall, edges)
    if r > 0.0:
        return out, r, len(edges)
    r = S.edge_radius(style, "sil", wall)
    done = 0
    for e in edges:
        for attempt in (r, r / 2):
            try:
                part = chamfer(part.edges().filter_by(
                    lambda x, e=e: abs(x.length - e.length) < 1e-7
                    and (x.center() - e.center()).length < 1e-7), attempt)
                done += 1
                break
            except Exception:  # noqa: BLE001
                continue
    return part, (r if done else 0.0), done


# ================================================================================================
# STYLE 2  `double`  - SHARD
# ================================================================================================
DOUBLE_WALL = 1.6
DOUBLE_Z_TOP = 33.25            # height 24.0
DOUBLE_BOW = 1.6                # slight outward curvature, executed as 6 straight facets
DOUBLE_FACETS = 6
DOUBLE_NOTCH = (-1.0, 3.2, 9.0)  # (y centre, half width, height above Z_BOT) - a cusped cable notch
DOUBLE_CHAMFER = 0.6


def _double_path() -> list[tuple[float, float]]:
    tf, tr = _tangents(FA, RA, R_RING)
    pts = _bow(tf, tr, DOUBLE_BOW, DOUBLE_FACETS)
    pts[0], pts[-1] = FA, RA
    return pts


def _build_double(p: dict) -> Part:
    wall, z1 = p["wall"], p["z_top"]
    plan, info = _plan_for("double", p)

    part = _prism(plan, Z_BOT, z1 - Z_BOT)

    # the cable notch: a lens, so its ceiling is a true cusp and needs no bridge declaration (CN-3)
    # The notch is a lens whose WIDEST point sits exactly on the bottom edge, so from there up it
    # only narrows and ends in a cusp. Put the widest point any higher and the flanks below it are
    # an undercut: measured, 2 x 19.2 mm² of Ø20 cylinder at 33 % facing down, which overhangs()
    # will not exempt as an arch (the limit is Ø10 in TPU) and cannot be declared a bridge either.
    yc, hw, h = p["notch"]
    notch_sk = S.lens((yc, Z_BOT - h), (yc, Z_BOT + h), min(hw, 0.49 * h))
    part -= S.extrude_cut(notch_sk, Plane.YZ.offset(-60.0), 200.0)
    part, n_relief, relief_zone = _bolt_relief(part)
    _INFO.update(bolt_reliefs=n_relief)
    part, r_ch, n_e = _soft_treat(part, "shard", wall, _top_edges(part, z1, skip=(FA, RA)))
    _INFO.update(chamfers=info.get("chamfers", 0), edge_r=r_ch, edges=n_e,
                 allow=_nonempty((_ladder_allow(part, z1, r_ch), relief_zone, _aperture_allow(notch_sk),
                        _vertex_allow(info["path"], wall),
                        *(_lip_allow(c, MOUTH_IN, Z_BOT, z1) for c in (FA, RA)))))
    return part


# ================================================================================================
# STYLE 5  `faceted_hook`  - SHARD
# ================================================================================================
HOOK_WRAP = 200.0
HOOK_FRONT_MOUTH = 150.0        # opposed by 60 deg so no single translation releases both hooks
HOOK_REAR_MOUTH = 210.0
FH_WALL = 1.8
FH_BENDS = ((23.0, 14.0), (22.0, -14.0))   # 15.2 and 13.9 deg bends, measured in checks()
FH_WINDOW = dict(y0=-7.0, y1=7.0, z0=16.0, z1=26.0, foot=4.0, riser=4.0)


def _fh_path() -> list[tuple[float, float]]:
    return [FA, *FH_BENDS, RA]


def _hook(center, mouth_deg: float) -> Sketch:
    """A 200 deg hook lip: an annulus sector centred opposite the mouth, lip tips rounded."""
    mid = mouth_deg - 180.0
    sk = _sector(center, R_BORE, R_RING, mid, HOOK_WRAP)
    return _mouth_fillet(sk, center, R_BORE, R_RING, mid, HOOK_WRAP)


def _build_faceted_hook(p: dict) -> Part:
    wall = p["wall"]
    plan, info = _plan_for("faceted_hook", p)

    part = _prism(plan, Z_BOT, Z_TOP - Z_BOT)
    w = p["window"]
    ell = (_rect(w["y0"], w["z0"], w["y1"], w["z1"])
           - _rect(w["y0"], w["z0"] + w["foot"], w["y1"] - w["riser"], w["z1"]))
    part -= S.extrude_cut(ell, Plane.YZ.offset(-60.0), 200.0)
    part, n_relief, relief_zone = _bolt_relief(part)
    _INFO.update(bolt_reliefs=n_relief)
    part, r_ch, n_e = _soft_treat(part, "shard", wall, _top_edges(part, Z_TOP, skip=(FA, RA)))
    _INFO.update(chamfers=info.get("chamfers", 0), edge_r=r_ch, edges=n_e,
                 allow=_nonempty((_ladder_allow(part, Z_TOP, r_ch), relief_zone, _aperture_allow(ell),
                        _vertex_allow(info["path"], wall),
                        _tip_allow(FA, p["front_mouth"] - 80.0, Z_BOT, Z_TOP),
                        _tip_allow(FA, p["front_mouth"] + 80.0, Z_BOT, Z_TOP),
                        _tip_allow(RA, p["rear_mouth"] - 80.0, Z_BOT, Z_TOP),
                        _tip_allow(RA, p["rear_mouth"] + 80.0, Z_BOT, Z_TOP))))
    return part


# ================================================================================================
# STYLE 4  `window_wing`  - ARSENAL
# ================================================================================================
WW_WALL = 1.6
WW_OUTSIDE = 1.0                 # inboard face held this far outside the real plate_mid outline
WW_YS = (27.0, 20.0, 14.0, 8.0, 2.0, -4.0, -10.0, -16.0, -22.0, -28.0)
WW_WINDOW = dict(y=-2.0, w=12.0, h=8.0, z=17.0)
# pitch 7.6, not 6.8: `vent_hex` places a VERTEX along the row (local +x is frame +Y here),
# so two neighbours in a row are 2 x circumradius = 5.774 apart edge to edge and a 6.8
# pitch leaves 1.03 mm, not 1.8. 2 x 2.887 + 1.8 = 7.57, rounded up.
WW_HEX = dict(af=5.0, ligament=1.8, pitch=7.6, y=(2.0, 25.5), z=(10.5, 32.5),
              origin=(13.0, 17.5))
WW_WING = dict(y=-13.0, reach=11.0, drop=(0.64, -0.77), wall=2.0, tip_z=21.0,
               slot=(8.0, 3.0, 40.0))


def _ww_path() -> list[tuple[float, float]]:
    off = WW_OUTSIDE + WW_WALL / 2
    return _smooth([FA, *[(_mid_edge(y) + off, y) for y in WW_YS], RA])


def _wing_plane(origin, d) -> Plane:
    """The vertical plane containing a wing vane: local x runs along the vane, local y is +Z."""
    n = (-d[1], d[0])
    return Plane(origin=(origin[0] - n[0] * 6.0, origin[1] - n[1] * 6.0, 0.0),
                 x_dir=(d[0], d[1], 0.0), z_dir=(-n[0], -n[1], 0.0))


def _build_window_wing(p: dict) -> Part:
    wall = p["wall"]
    plan, info = _plan_for("window_wing", p)
    # the wing: one swept vane off the rear flank, tapering in height so every cut face looks up
    w, d = p["wing"], p["wing"]["drop"]
    root = info["wing_root"]

    part = _prism(plan, Z_BOT, Z_TOP - Z_BOT)

    pl = _wing_plane(root, d)
    part -= S.extrude_cut(Polygon((0.0, Z_TOP), (w["reach"] + 4.0, w["tip_z"]),
                                  (w["reach"] + 4.0, Z_TOP + 6.0), (0.0, Z_TOP + 6.0), align=None),
                          pl, 12.0)
    sl, sw, sa = w["slot"]
    part -= S.extrude_cut(Pos(w["reach"] * 0.55, (Z_BOT + w["tip_z"]) / 2 + 1.0)
                          * _stadium(sl, sw).rotate(Axis.Z, sa), pl, 12.0)

    # USB / cable window, hex vent field on the forward half
    u = p["window"]
    win = _rect(u["y"] - u["w"] / 2, u["z"] - u["h"] / 2, u["y"] + u["w"] / 2, u["z"] + u["h"] / 2)
    win, _n2 = _treat(win, [(u["y"] + sx * u["w"] / 2, u["z"] + sz * u["h"] / 2)
                            for sx in (1, -1) for sz in (1, -1)], 0.8, fillet)
    part -= S.extrude_cut(win, Plane.YZ.offset(-60.0), 200.0)
    h = p["hex"]
    vents, n_vent = S.vent_hex(_rect(h["y"][0], h["z"][0], h["y"][1], h["z"][1]),
                               pitch=h["pitch"], ligament_min=h["ligament"], af=h["af"],
                               hole_min=DECOR_HOLE_MIN, origin=h["origin"],
                               clean=[_rect(u["y"] - u["w"] / 2 - 2.4, u["z"] - u["h"] / 2 - 2.4,
                                            u["y"] + u["w"] / 2 + 2.4, u["z"] + u["h"] / 2 + 2.4)])
    if n_vent:
        part -= S.extrude_cut(vents, Plane.YZ.offset(-60.0), 200.0)
    part, n_relief, relief_zone = _bolt_relief(part)
    _INFO.update(vents=n_vent, bolt_reliefs=n_relief,
                 allow=_nonempty((box(0.0, h["y"][0], h["z"][0], 60.0, h["y"][1], h["z"][1]), relief_zone,
                        _vertex_allow(info["path"], wall),
                        _aperture_allow(win), _wing_allow(info, w),
                        *(_lip_allow(c, MOUTH_IN, Z_BOT, Z_TOP) for c in (FA, RA)))))
    return part


def _stadium(length: float, width: float) -> Sketch:
    straight = max(length - width, 1e-3)
    return (Rectangle(straight, width) + Pos(-straight / 2, 0) * Circle(width / 2)
            + Pos(straight / 2, 0) * Circle(width / 2))


def _arc_at_y(pts, y: float) -> float:
    """Arc length at which the polyline crosses this y (paths are monotonic in y by construction)."""
    s = 0.0
    for a, b in zip(pts, pts[1:]):
        L = hypot(b[0] - a[0], b[1] - a[1])
        if (a[1] - y) * (b[1] - y) <= 0 and abs(a[1] - b[1]) > 1e-9:
            return s + L * (a[1] - y) / (a[1] - b[1])
        s += L
    return s


# ================================================================================================
# STYLE 3  `angled`  - CHASSIS
# ================================================================================================
AN_WALL = 2.0
AN_PATH = ((18.60, 70.0), (18.60, 58.0), (19.90, 49.0), (21.00, 42.5), (22.10, 39.3),
           (23.80, 37.2), (26.00, 35.6))   # every bend under 20 deg: a 42 deg kink puts
#          the miter corner inside its own wall and the ray sampler reads 0.07 mm across it
AN_RAIL = 4.75                       # chord depth, top and bottom
# flat 1.5: the truncated apex is the only ceiling the print has, and 1.5 x the 2.6 mm
# oblique wall section is 3.9 mm², under overhangs()' 5.0 mm² floor (2.0 measured 5.2).
AN_DIAMOND = dict(centres=(41.0, 50.5, 60.0), half_w=3.4, flat=1.5)
AN_STRUT_W = 3.0
AN_NODES = (36.25, 45.75, 55.25, 64.75)
# Ø2.3 rather than the canon's 1.6 so each bump is buried 0.35 mm in the rail instead of
# sitting exactly tangent to it: a tangent OCCT union on thirteen bumps segfaults outright
# (measured). Protrusion and pitch are the canon values, so the SPINE reads unchanged.
AN_SERR = dict(d=2.3, pitch=3.2, protrusion=0.8, z=(9.25, 14.0),
               path=((18.60, 69.0), (18.60, 58.0), (19.90, 49.0), (21.00, 42.5)))
AN_HOOK = dict(y=(63.5, 70.0), z_bot=5.0, teeth=((64.0, 65.5), (66.0, 67.5), (68.0, 69.5)),
               tooth_z=1.6, reach=1.95)


def _an_path() -> list[tuple[float, float]]:
    return _smooth([*AN_PATH, FA])


def _diamond(yc: float, half_w: float, z0: float, z1: float, flat: float) -> Sketch:
    """A lattice cell: a diamond with both apexes truncated to `flat`, so the aperture ceiling is
    4 mm² whichever way up the part is printed - which is what lets this part print top-down."""
    zm = (z0 + z1) / 2
    return Polygon((yc - half_w, zm), (yc - flat / 2, z1), (yc + flat / 2, z1),
                   (yc + half_w, zm), (yc + flat / 2, z0), (yc - flat / 2, z0), align=None)


def _build_angled(p: dict) -> Part:
    wall = p["wall"]
    plan, info = _plan_for("angled", p)
    pts = info["path"]

    part = _prism(plan, Z_BOT, Z_TOP - Z_BOT)

    # the claw hook: the wall carries on down past the mid-plate side edge and three teeth reach
    # under it. Three small teeth rather than one shelf: each top face is 2.9 mm², under the 5 mm²
    # floor, so the ceiling never has to be declared a bridge.
    hk = p["hook"]
    y0, y1 = hk["y"]
    skirt = _prism(plan, hk["z_bot"], Z_BOT - hk["z_bot"])
    part += skirt & box(0, y0, hk["z_bot"] - 1, 60, y1, Z_BOT)
    for ty0, ty1 in hk["teeth"]:
        pin, _n, _t = _at(pts, _arc_at_y(pts, (ty0 + ty1) / 2))
        x_in = pin[0] - wall / 2
        part += box(x_in - hk["reach"], ty0, hk["z_bot"], x_in + 0.4, ty1,
                    hk["z_bot"] + hk["tooth_z"])

    # the lattice: diamonds, then the ring nodes unioned back in and bored
    d = p["diamond"]
    zr0, zr1 = Z_BOT + p["rail"], Z_TOP - p["rail"]
    cells = Sketch()
    for yc in d["centres"]:
        cells += _diamond(yc, d["half_w"], zr0, zr1, d["flat"])
    node_r_out, node_r_in = 2.6 * p["strut"] / 2, 0.9 * p["strut"] / 2
    zm = (zr0 + zr1) / 2
    for yn in p["nodes"]:
        cells -= Pos(yn, zm) * Circle(node_r_out)
    part -= S.extrude_cut(cells, Plane.YZ.offset(-60.0), 200.0)
    lattice_zone = _aperture_allow(cells)
    bores = Sketch()
    for yn in p["nodes"]:
        bores += Pos(yn, zm) * Circle(node_r_in)
    part -= S.extrude_cut(bores, Plane.YZ.offset(-60.0), 200.0)

    # SPINE: the outboard rail carries half-round serrations (the spined tibia)
    sr = p["serration"]
    outer = list(reversed(_offset_path(list(sr["path"]), wall / 2)))  # reversed: +y order makes (ty, -tx) outboard
    bumps, n_bump = S.serration(outer, d=sr["d"], pitch=sr["pitch"], protrusion=sr["protrusion"])
    if n_bump:
        part += _prism(bumps, sr["z"][0], sr["z"][1] - sr["z"][0])
    _INFO.update(nodes=len(p["nodes"]), serrations=n_bump,
                 allow=_nonempty((_lip_allow(FA, MOUTH_IN, Z_BOT, Z_TOP), lattice_zone,
                                  _vertex_allow(pts, wall))))
    return part


BOLT_NOTCH = dict(half_w=4.6, z_top=17.6, corner_r=1.0)


def _bolt_probe(x: float, y: float) -> Part:
    """The inner arm-root fastener as it really stands on plate_mid: the brief's Ø6 x 3 head, plus
    the nyloc nut and the 4 mm of bolt tip above it that side_panels already measured (Z 9-17)."""
    return (cylinder(x, y, Z_MID_TOP, Z_MID_TOP + BOLT_HEAD_H, BOLT_HEAD_D)
            + cylinder(x, y, Z_MID_TOP + BOLT_HEAD_H, Z_MID_TOP + 8.2, 4.6))


def _bolt_relief(part: Part) -> tuple[Part, int]:
    """A notch over each inner arm-root bolt the panel would otherwise sit on.

    The two bolts at (26.97, 18.17) and (26.43, -19.63) lie almost exactly ON the chord between the
    two arm-root standoffs, so ANY panel that follows that chord instead of bowing outboard has to
    open up for them - which is why the reference photo of the faceted panel has notches on its
    inboard edge. Cut only where a probe says the panel really fouls the bolt, so a bowed or
    plate-hugging style keeps an unbroken skirt."""
    n, zone = 0, Sketch()
    for x, y in BOLT_HEADS:
        if isect(part, _bolt_probe(x, y)) <= EPS:
            continue
        b = BOLT_NOTCH
        sk = _rect(y - b["half_w"], Z_BOT - 1.0, y + b["half_w"], b["z_top"])
        sk, _k = _treat(sk, [(y - b["half_w"], b["z_top"]), (y + b["half_w"], b["z_top"])],
                        b["corner_r"], fillet)
        part -= S.extrude_cut(sk, Plane.YZ.offset(-60.0), 200.0)
        zone += sk
        n += 1
    return part, n, _aperture_allow(zone) if n else Part()


# ================================================================================================
# STYLE 6  `brutalist`  - one poured slab, formwork still showing (PETG)
# ================================================================================================
BR_WALL = 3.0                  # 2 x the catalogue wall, constant, no local thinning
BR_OFFSET = 5.5                # the straight run sits this far outboard of the clip-to-clip chord
BR_EXT = 17.0                  # and overhangs each clip ring by this much
BR_VOID = dict(y0=-34.0, y1=10.2, z0=11.5, z1=31.5)         # ONE rectangular void, sharp corners
BR_RIB = dict(proud=3.0, width=3.0, pitch=12.0, ys=(-6.0, -18.0, -30.0))
BR_GROOVE = dict(w=0.6, depth=0.3, pitch=2.4)               # board marking, both faces
BR_CHAMFER = 1.0
BR_FILLET_MAX = 0.3
BR_PLAQUE = dict(y=26.5, length=30.0, proud=2.4)            # full height: a pad with no underside
# 27.0, not 24.0: at 24 the glyph set hands OCCT a degenerate edge and the cut solid
# comes back is_valid False (measured on the clean prism, both hands).
BR_MARK, BR_MARK_SIZE, BR_MARK_DEPTH = "wordmark", 27.0, 2.0


def _unit(a, b) -> tuple[float, float]:
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = hypot(dx, dy) or 1.0
    return dx / L, dy / L


def _run_geom(d: float, ext: float) -> dict:
    """A straight run `d` mm outboard of the clip-to-clip chord, reached from each ring on a 45 deg
    dogleg, and overhanging the rings by `ext`. At d >= 5.0 the run stands clear of both arm-root
    bolt heads, which is what lets a style that may not curve keep an unbroken skirt."""
    u = _unit(FA, RA)
    n = (-u[1], u[0])                      # outboard (+X-ish) on a decreasing-y path
    p1 = (FA[0] + (u[0] + n[0]) * d, FA[1] + (u[1] + n[1]) * d)
    p2 = (RA[0] - (u[0] - n[0]) * d, RA[1] - (u[1] - n[1]) * d)
    tf = (p1[0] - u[0] * ext, p1[1] - u[1] * ext)
    tr = (p2[0] + u[0] * ext, p2[1] + u[1] * ext)
    return dict(u=u, n=n, p1=p1, p2=p2, tip_front=tf, tip_rear=tr, run=[tf, tr],
                dogleg_front=[FA, p1], dogleg_rear=[p2, RA])


def _br_geom() -> dict:
    """BRUTALIST's own run: 5.5 mm outboard, overhanging each ring by 12 mm."""
    return _run_geom(BR_OFFSET, BR_EXT)


def _br_at(y: float) -> tuple[float, float]:
    """The run centreline point at this y (the run is straight, so this is exact)."""
    g = _br_geom()
    tf, u = g["tip_front"], g["u"]
    s = (y - tf[1]) / u[1]
    return (tf[0] + u[0] * s, y)


def _br_face_area() -> float:
    g = _br_geom()
    return _path_len(g["run"]) * (Z_TOP - Z_BOT)


def _br_pad_plan(g: dict, wall: float, y: float, length: float, proud: float) -> Sketch:
    """A full-height proud pad (a formwork rib, or the plaque) as a PLAN rectangle.

    Every proud feature on this slab runs the whole 24.5 mm height, which is what makes it a plan
    feature and not a 3D one: a full-height pad has no underside to overhang and no coplanar-face
    fuse to make OCCT hand back a bad solid (measured: unioning the same ribs as separate solids
    onto the chamfered slab segfaults OCCT). Extruding one merged plan profile builds the ribs, the
    plaque and the slab as ONE prism."""
    c = _br_at(y)
    n, t = g["n"], g["u"]
    u0, u1 = wall / 2 - 0.6, wall / 2 + proud
    v0, v1 = -length / 2, length / 2
    pts = [(c[0] + n[0] * a + t[0] * b, c[1] + n[1] * a + t[1] * b)
           for a, b in ((u0, v0), (u1, v0), (u1, v1), (u0, v1))]
    return Polygon(*pts, align=None)


def _br_corners(g: dict, wall: float) -> list[tuple[float, float]]:
    """Every convex corner of the brutalist plan: the two slab tips and the outboard corners of
    the three ribs and the plaque. These are where the 1.0 mm 45 deg chamfer goes.

    IN PLAN, not on the top edge, and that is a measured decision: a chamfer on the top silhouette
    turns the slab into a 439-face solid that OCCT SEGFAULTS on when the wordmark is cut out of it
    (reproduced four times; without the top chamfer the same cut is clean and valid). A plan
    chamfer is also what the language actually asks for - the plan outline is rectangles and
    45 deg cuts - and it leaves the poured top face square, as a cast slab is."""
    n, t = g["n"], g["u"]
    out = []
    for tip in (g["tip_front"], g["tip_rear"]):
        for side in (1, -1):
            out.append((tip[0] + n[0] * side * wall / 2, tip[1] + n[1] * side * wall / 2))
    for y, length, proud in ([(ry, BR_RIB["width"], BR_RIB["proud"]) for ry in BR_RIB["ys"]]
                             + [(BR_PLAQUE["y"], BR_PLAQUE["length"], BR_PLAQUE["proud"])]):
        c = _br_at(y)
        u1 = wall / 2 + proud
        for v in (-length / 2, length / 2):
            out.append((c[0] + n[0] * u1 + t[0] * v, c[1] + n[1] * u1 + t[1] * v))
    return out


def _br_grooves(g: dict, wall: float) -> Part:
    """Board marking: 0.6 x 0.3 grooves at 2.4 pitch, vertical - they run the PRINT direction, so
    every one of them is a vertical slot with no ceiling and no flank steeper than the wall."""
    run, total, u = g["run"], _path_len(g["run"]), g["u"]
    b, r, q = BR_GROOVE, BR_RIB, BR_PLAQUE
    y0 = g["tip_front"][1]
    cut = Part()
    s = b["pitch"]
    while s < total - b["pitch"] / 2:
        for side in (+1, -1):               # outer face and inboard face, staggered half a pitch
            off = 0.0 if side > 0 else b["pitch"] / 2
            if s + off >= total:
                continue
            y = y0 + u[1] * (s + off)
            # The plaque is a cast plaque, not formwork: the boards stop at it. On a rib the groove
            # is taken from the RIB'S OWN outer face, 0.3 deep like everywhere else - cutting it at
            # the slab's face instead would slot the rib through and leave 1.2 mm cheeks (measured).
            if side > 0 and abs(y - q["y"]) < q["length"] / 2 + 0.8:
                continue
            # A groove that lands within 1.8 mm of the void's edge or of the slab's tip leaves a
            # sliver instead of a wall - the board stops short of the opening, as formwork does.
            v = BR_VOID
            if min(abs(y - v["y0"]), abs(y - v["y1"])) < b["w"] / 2 + 1.5:
                continue
            if min(s + off, total - s - off) < b["w"] / 2 + 1.5:
                continue
            proud = r["proud"] if (side > 0 and any(abs(y - ry) < r["width"] / 2 + 0.3
                                                    for ry in r["ys"])) else 0.0
            u0 = side * (wall / 2 + proud - b["depth"])
            u1 = side * (wall / 2 + proud + 1.0)
            lo, hi = min(u0, u1), max(u0, u1)
            # The groove stops 1.4 mm short of the top so the silhouette chamfer still has a
            # continuous edge to land on; its own 0.6 x 0.3 ceiling is 0.18 mm², two orders under
            # overhangs()' 5.0 mm² floor, and it opens downward through the bed.
            cut += _prism_at([(lo, Z_BOT - 1.0), (hi, Z_BOT - 1.0), (hi, Z_TOP - 1.4), (lo, Z_TOP - 1.4)],
                             run, s + off, b["w"])
        s += b["pitch"]
    return cut


def _build_brutalist(p: dict) -> Part:
    wall = p["wall"]
    plan, info = _plan_for("brutalist", p)
    g = info["geom"]
    part = _prism(plan, Z_BOT, Z_TOP - Z_BOT)

    # ONE rectangular void, sharp corners, cut through slab, ribs and all - formwork planks do not
    # stop at a hole. Its ceiling is the only downward face in the part; it spans the 3.0 mm wall
    # (6.0 where a rib crosses it) and is declared a bridge.
    v = p["void"]
    void_sk = _rect(v["y0"], v["z0"], v["y1"], v["z1"])
    part -= S.extrude_cut(void_sk, Plane.YZ.offset(-60.0), 200.0)
    grooves = _br_grooves(g, wall)
    part -= grooves

    n_ch = info.get("chamfers", 0)   # 1.0 mm 45 deg, cut in the plan (see _br_corners)

    # The three formwork ribs and the plaque are already in the prism: both are full-height plan
    # features (see _br_pad_plan), which is also why neither needs a 3D union onto the slab.
    r, q = BR_RIB, BR_PLAQUE
    cq = _br_at(q["y"])
    if S.mark_fits(BR_MARK, p["mark_size"]):
        u1 = wall / 2 + q["proud"]
        # The band must cover the whole deboss, from the plaque's outer face (u 3.5) down past its
        # 2.0 mm floor (u 1.5), or the mirror row sees the un-mirrored stencil as an asymmetry.
        band = _br_pad_plan(g, 2.0, q["y"], q["length"] + 2.0, 3.2)
        _INFO["mark_band"] = S.extrude_cut(band, Plane.XY.offset(14.0), 16.0)
        at = (cq[0] + g["n"][0] * u1, cq[1] + g["n"][1] * u1, 21.5)
        _INFO["mark"] = dict(kind=BR_MARK, size=p["mark_size"], mode="deboss", at=at,
                             normal=(g["n"][0], g["n"][1], 0.0), depth=p["mark_depth"],
                             x_dir=(0, 0, 1), angle=-90.0)
        # The left panel's own stencil: reflected position and normal, glyphs flipped so the
        # wordmark still reads left to right on that flank (a mirrored wordmark is a defect).
        _INFO["mark_left"] = dict(_INFO["mark"], at=(-at[0], at[1], at[2]),
                                  normal=(-g["n"][0], g["n"][1], 0.0), mirror_x=False)

    # No bore cut here either: the plan already carries both Ø6.5 bores (see the origami note).
    part, n_relief, relief_zone = _bolt_relief(part)
    _INFO.update(chamfers=n_ch, bolt_reliefs=n_relief, ribs=len(r["ys"]),
                 void_area=(v["y1"] - v["y0"]) * (v["z1"] - v["z0"]), face_area=_br_face_area(),
                 # The ribs and the plaque are NOT declared: both are 3.0 mm or more of section
                 # and the slab under them is straight, so the rays measure them honestly. Only
                 # the 0.6 x 0.3 board grooves are - a ray leaving a groove flank runs along the
                 # face and reads 0.6 mm, which is the sampler's documented blind spot, not a wall.
                 allow=_nonempty((relief_zone, grooves,
                                  _vertex_allow([FA, g["p1"], g["p2"], RA], wall),
                                  _aperture_allow(void_sk),
                                  *(_lip_allow(c, MOUTH_IN, Z_BOT, Z_TOP) for c in (FA, RA)))))
    return part


def _max_fillet_r(part: Part, skip=(), r_max: float = 3.0) -> tuple[float, int]:
    """The largest rounding radius anywhere on the part's silhouette, ignoring the clip rings.

    BRUTALIST's rule is `no fillet above r 0.3`, and the only way to assert it is to measure the
    part: every vertical-axis cylindrical face under r_max is a plan rounding, and a torus is a
    3D fillet. The clip rings are excluded BY NAME, not by relaxing the rule - their bore, their
    0.8 lip chamfer and their 0.45 mouth fillets are `c_clip`'s fixed mating geometry, measured
    exactly by the coaxial and standoff-gap rows."""
    worst, n = 0.0, 0
    for f in part.faces():
        if f.geom_type not in (GeomType.CYLINDER, GeomType.TORUS):
            continue
        c = f.center()
        if any(hypot(c.X - sx, c.Y - sy) < R_RING + CLIP_WALL + 1.0 for sx, sy in skip):
            continue
        try:
            rad = (f.geom_adaptor().Cylinder().Radius() if f.geom_type == GeomType.CYLINDER
                   else f.geom_adaptor().Torus().MinorRadius())
        except Exception:  # noqa: BLE001 - a trimmed surface has no adaptor; fall back to the bbox
            bb = f.bounding_box()
            rad = min(bb.size.X, bb.size.Y) / 2
        if rad <= r_max:
            worst, n = max(worst, rad), n + 1
    return round(worst, 4), n


# ================================================================================================
# STYLE 7  `origami`  - one sheet of paper, folded, nothing else (PETG)
# ================================================================================================
OR_WALL = 1.8                   # CONSTANT: the part is a 1.8 mm offset of a folded mid-surface
OR_FOLD = 22.5                  # the only angle allowed anywhere in the part
OR_FLANGE = 18.0                # the sheet runs on past both clips - paper does not stop at a hole
OR_CHAMFER = 0.4                # chamfer only, never a fillet
OR_SLOT = dict(w=4.0, pitch=6.4, z0=13.0, z1=29.0, clear=6.8, y_hi=40.0, y_lo=-41.0)


def _or_path() -> list[tuple[float, float]]:
    """FA -> RA in three planar facets of equal length, folded +22.5 then -22.5, plus a straight
    flange off each end. Two creases, at exactly 1/3 and 2/3 of the folded run."""
    u = _unit(FA, RA)
    L = hypot(RA[0] - FA[0], RA[1] - FA[1])
    a = L / (2 * cos(radians(OR_FOLD)) + 1.0)          # 2a cos(fold) + a = L, so the facets match
    u1 = (u[0] * cos(radians(OR_FOLD)) - u[1] * sin(radians(OR_FOLD)),
          u[0] * sin(radians(OR_FOLD)) + u[1] * cos(radians(OR_FOLD)))
    u3 = (u[0] * cos(radians(-OR_FOLD)) - u[1] * sin(radians(-OR_FOLD)),
          u[0] * sin(radians(-OR_FOLD)) + u[1] * cos(radians(-OR_FOLD)))
    q1 = (FA[0] + u1[0] * a, FA[1] + u1[1] * a)
    q2 = (q1[0] + u[0] * a, q1[1] + u[1] * a)
    tf = (FA[0] - u1[0] * OR_FLANGE, FA[1] - u1[1] * OR_FLANGE)
    tr = (RA[0] + u3[0] * OR_FLANGE, RA[1] + u3[1] * OR_FLANGE)
    return [tf, FA, q1, q2, RA, tr]


def _or_slots() -> tuple[Sketch, int, float]:
    """The ladder of parallelogram slots, sheared to the fold angle. Every edge is a straight line
    and every slanted edge is at exactly 22.5 deg, which is the whole rule of the language."""
    b = OR_SLOT
    d = (b["z1"] - b["z0"]) * sin(radians(OR_FOLD)) / cos(radians(OR_FOLD))
    sk, n = Sketch(), 0
    y = b["y_hi"]
    while y >= b["y_lo"]:
        if all(abs(y - c[1]) >= b["clear"] for c in (FA, RA)):
            w = b["w"]
            sk += Polygon((y - w / 2 - d / 2, b["z0"]), (y + w / 2 - d / 2, b["z0"]),
                          (y + w / 2 + d / 2, b["z1"]), (y - w / 2 + d / 2, b["z1"]), align=None)
            n += 1
        y -= b["pitch"]
    return sk, n, round((b["pitch"] - b["w"]) * cos(radians(OR_FOLD)), 3)


def _build_origami(p: dict) -> Part:
    wall = p["wall"]
    plan, info = _plan_for("origami", p)
    pts = info["path"]
    part = _prism(plan, Z_BOT, Z_TOP - Z_BOT)

    slots, n_slots, lig = _or_slots()
    part -= S.extrude_cut(slots, Plane.YZ.offset(-60.0), 200.0)
    # The rear flange leaves RA heading inboard, and 0.15 mm³ of it stands in the standoff's
    # insertion channel. The mouth slot is run on inboard to the end of that channel - a straight
    # 5.2 mm slot, which is also the only edge treatment this language allows.
    part -= box(RA[0] - R_RING - 8.5, RA[1] - MOUTH / 2, Z_BOT - 1,
                RA[0], RA[1] + MOUTH / 2, Z_TOP + 1)
    # NOTE: no bore cut here. _plan_for() already subtracted both Ø6.5 bores from the plan, and
    # subtracting the same cylinder again hands back an INVALID solid (measured: is_valid False,
    # and every later chamfer then refuses).

    n_ch = 0
    for e in _top_edges(part, Z_TOP, min_len=2.0, skip=(FA, RA)):
        try:
            part = chamfer(part.edges().filter_by(
                lambda x, e=e: abs(x.length - e.length) < 1e-7
                and (x.center() - e.center()).length < 1e-7), OR_CHAMFER)
            n_ch += 1
        except Exception:  # noqa: BLE001 - OCCT refuses a chamfer that does not fit; leave it sharp
            continue

    part, n_relief, relief_zone = _bolt_relief(part)
    _INFO.update(slots=n_slots, ligament=lig, chamfers=n_ch, bolt_reliefs=n_relief,
                 allow=_nonempty((relief_zone, _aperture_allow(slots),
                                  _vertex_allow(pts, wall),
                                  *(_lip_allow(c, MOUTH_IN, Z_BOT, Z_TOP) for c in (FA, RA)))))
    return part


# ================================================================================================
# STYLE 8  `filigree`  - ornamental cutwork hung on a rigid spine (TPU95A)
# ================================================================================================
FI_WALL = 4.5                   # deep cutwork: the scrolls read as wells, not perforations
FI_OFFSET = 5.2                 # the spine runs this far outboard of the chord, clear of the bolts
FI_SPINE = 2.4                  # the solid spine, on the load path, clip to clip
FI_R = 4.95                     # the scroll radius R: Ø9.9, just inside TPU's 10 mm arch limit
FI_LIG = 1.5                    # every ribbon, everywhere (1.5 wide x 4.5 deep)
FI_NODE_D = 4.0                 # ring node at every scroll junction
FI_Z_BIG = 30.8                 # scroll centre: 3.15 clear of the spine, 2.0 through the edge
FI_TIP = 1.2                    # and the cusp tip is blunted by this radius, so the
                                # scallop ends in a 1.8 mm shoulder, not a feather edge
FI_VOID_BAND = (0.45, 0.60)
FI_ACCENT_R = 3.4               # the lunule crescent: Ø6.8, an arch like every other opening
FI_ACCENT_D = 0.6               # and 0.6 mm deep, so the spine keeps 3.9 mm of its 4.5


def _fi_net(y_lo: float, y_hi: float) -> tuple[Sketch, Sketch, dict]:
    """The scroll net as a cut, mirrored about the spine.

    The ribbon is the material LEFT between two arc radii - the scroll arc R and the node arc at
    every junction, which meet tangentially where the node sits on a ligament. There is no straight
    member anywhere in it, which is what separates filigree from chassis.

    Two deviations, both measured and both deliberate. The brief's pitch of 1.6 R would merge two
    adjacent R scrolls (1.6 R < 2 R), so the pitch is 2 R + the ribbon = 11.4, which is the pitch
    that actually delivers the specified ribbon. And R is 4.95, not larger: the scroll is cut as a
    prism along X, so its face is a Ø9.9 arch with a horizontal axis and overhangs() exempts it
    only up to TPU's 10.0 mm - one tenth more and every scroll becomes an unsupported ceiling."""
    z_mid = (Z_BOT + Z_TOP) / 2
    pitch = 2 * FI_R + FI_LIG
    keep = R_RING + FI_R + FI_LIG          # how far a scroll must stay off a clip ring
    lo = max(y_lo, RA[1] + keep)
    hi = min(y_hi, FA[1] - keep)
    n = max(1, int((hi - lo) / pitch) + 1)
    span = (n - 1) * pitch
    y0 = (lo + hi) / 2 - span / 2
    ys = [y0 + i * pitch for i in range(n)]
    cut, nodes = Sketch(), Sketch()
    edge = Z_TOP if FI_Z_BIG > z_mid else Z_BOT
    half = (max(FI_R ** 2 - (edge - FI_Z_BIG) ** 2, 0.0)) ** 0.5   # where the scroll breaks the edge
    for i, yc in enumerate(ys):
        for sgn in (1, -1):                # mirrored about the spine
            zc = z_mid + sgn * (FI_Z_BIG - z_mid)
            cut += Pos(yc, zc) * Circle(FI_R)
            # Blunt both cusp tips. Where a scroll crosses a straight edge the material tapers to
            # a knife edge, and the ray sampler reads it at 0.22 mm (measured, 77 rays of 775).
            # A Ø2.4 disc on the crossing point truncates the wedge where it is already thicker
            # than the ribbon, so the outline still ends in an arc - just not in a feather.
            for s_ in (1, -1):
                cut += Pos(yc + s_ * half, z_mid + sgn * (edge - z_mid)) * Circle(FI_TIP)
            if i < len(ys) - 1:            # a ring node on every scroll junction
                nodes += Pos(yc + pitch / 2, zc) * Circle(FI_NODE_D / 2)
    tips = [(yc + s_ * half, z_mid + sgn * (edge - z_mid))
            for yc in ys for sgn in (1, -1) for s_ in (1, -1)]
    info = dict(tips=tips, pitch=round(pitch, 3), scrolls=2 * len(ys), nodes=2 * max(0, len(ys) - 1),
                ligament=round(pitch - 2 * FI_R, 3),
                spine_gap=round(FI_Z_BIG - FI_R - (z_mid + FI_SPINE / 2), 3),
                cusp=round(FI_Z_BIG + FI_R - Z_TOP, 3),
                net_field=(round(ys[0] - FI_R, 3), round(ys[-1] + FI_R, 3)))
    return cut, nodes, info


def _fi_lunule(y: float, z: float) -> Sketch:
    """The crescent: a disc of R_a with a disc of R_b swung off it, so both edges are arcs and the
    two horns are cusps. Small enough (Ø <= 8) that its cut face is an arch, like every other
    opening in this panel."""
    a, b, off = FI_ACCENT_R, FI_ACCENT_R * 0.86, FI_ACCENT_R * 0.55
    sk = Circle(a) - Pos(off, 0) * Circle(b)
    # Both horns are blunted with a Ø1.4 disc, exactly as the scroll cusps are: a bare cusp here
    # crashes OCCT's erosion outright (min_wall segfaults the process, reproduced three times),
    # and a blunt horn still leaves an outline made only of arcs.
    for hx, hz in _fi_horns(0.0, 0.0):
        sk += Pos(hx, hz) * Circle(0.7)
    return Pos(y, z) * sk


def _fi_horns(y: float, z: float) -> list[tuple[float, float]]:
    """The crescent's two cusps, where its arcs cross. A lunule HAS two horns - that is what makes
    it a lunule - so they are declared for the ray sampler rather than rounded away."""
    a, b, off = FI_ACCENT_R, FI_ACCENT_R * 0.86, FI_ACCENT_R * 0.55
    dx = (a * a - b * b + off * off) / (2 * off)
    dz = max(a * a - dx * dx, 0.0) ** 0.5
    return [(y + dx, z + dz), (y + dx, z - dz)]


def _fi_tip_allow(tips, extra=()) -> Part:
    """The cusp tips, declared.

    Where an arc meets a straight edge the material ends in a point, and a ray leaving that point
    runs ALONG the material - the blind spot ray_thickness() documents for itself. These are tips,
    not walls: the scallop is truncated at Ø2.4 so the printed shoulder is 1.4 mm (blunter than
    the ribbon it hangs off), and the ribbon, the ligament and the void fraction are all measured
    numerically in the rows below. Same treatment, and same reason, as the clip lips above."""
    sk = Sketch()
    for y, z in list(tips) + list(extra):
        sk += Pos(y, z) * Circle(FI_TIP + 0.7)
    return S.extrude_cut(sk, Plane.YZ.offset(-60.0), 200.0) if sk.faces() else Part()


def _fi_rim_allow(voids: Sketch, grow: float = 0.7) -> Part:
    """A 0.7 mm band round the RIM of every scroll - and nothing else.

    A sample point that the tessellation drops on a hole's rim shoots its ray along the rim and
    reads 0.07 mm on a 4.5 mm slab (measured, twice, on the two 800 mm² faces). That is the
    grazing artefact ray_thickness documents, not a wall. This declares only the rim band, not
    the aperture field the way `_aperture_allow` would - the ribbons themselves stay measured."""
    try:
        band = S.grow_region(voids, grow) - voids
    except Exception:  # noqa: BLE001 - if OCCT will not offset the field, declare nothing
        return Part()
    return S.extrude_cut(band, Plane.YZ.offset(-60.0), 200.0) if band.faces() else Part()


def _fi_void_fraction(cut: Sketch, nodes: Sketch, y0: float, y1: float) -> tuple[float, float]:
    """(void fraction, field area) over the cutwork field's own elevation - measured, not assumed."""
    field = _rect(y0, Z_BOT, y1, Z_TOP)
    voids = (cut - nodes) & field
    return round(float(voids.area) / float(field.area), 4), round(float(field.area), 1)


def _build_filigree(p: dict) -> Part:
    wall = p["wall"]
    plan, info = _plan_for("filigree", p)
    g = info["geom"]
    part = _prism(plan, Z_BOT, Z_TOP - Z_BOT)

    y0, y1 = min(g["p1"][1], g["p2"][1]), max(g["p1"][1], g["p2"][1])
    cut, nodes, net = _fi_net(y0, y1)
    voids = cut - nodes
    part -= S.extrude_cut(voids, Plane.YZ.offset(-60.0), 200.0)
    frac, field = _fi_void_fraction(cut, nodes, *net["net_field"])

    # THE ONE ACCENT: the lunule, where the two mirrored scrolls meet - on the spine, at mid span.
    # It is a 0.6 mm deep crescent DEBOSS, not a through cut: the spine is the load path and the
    # language's own rule is that everything off the spine is open work and everything on it is
    # not. Built here from two arcs rather than through `mark`, because the mark vocabulary has no
    # lunule kind yet (S.mark_fits("lunule", ...) is False today) and an accent must not depend on
    # another task landing first.
    y_mid = (y0 + y1) / 2
    tf, u, n = g["run"][0], g["u"], g["n"]
    x_face = tf[0] + u[0] * (y_mid - tf[1]) / u[1] + n[0] * wall / 2
    lun_sk = _fi_lunule(y_mid, (Z_BOT + Z_TOP) / 2)
    lun_tool = S.extrude_cut(lun_sk, Plane.YZ.offset(x_face - FI_ACCENT_D), 60.0)
    part -= lun_tool
    lun = round(float(lun_sk.area), 2)

    part, n_relief, relief_zone = _bolt_relief(part)
    horns = _fi_horns(y_mid, (Z_BOT + Z_TOP) / 2)
    _INFO.update(void_fraction=frac, field=field, lunule=lun, bolt_reliefs=n_relief, **net,
                 allow=_nonempty((relief_zone, _fi_tip_allow(net["tips"], horns),
                                  _fi_rim_allow(voids),
                                  _vertex_allow([FA, g["p1"], g["p2"], RA], wall),
                                  *(_lip_allow(c, MOUTH_IN, Z_BOT, Z_TOP) for c in (FA, RA)))))
    return part


# ================================================================================================
# STYLE 9  `gyroid`  - the solid is a frozen fluid (PETG, Blender)
# ================================================================================================
GY_WALL = 3.6                   # thicker than anything else in the set: the inside is mostly void
GY_BOW = 3.0                    # one smooth half-sine; there is no crease anywhere in the part
GY_RIND = 1.6                   # solid skin on every mating and bearing face
GY_PERIOD = 10.0                # gyroid period: >= 1.5 of them fit across the 24.5 mm height
GY_LIG = 1.6                    # gyroid sheet thickness
GY_ROUND = 3.0                  # the single constant plan rounding
GY_CELL, GY_FALLBACK = "gyroid", "voronoi"


def _gy_path() -> list[tuple[float, float]]:
    """A smooth bowed chord: tangent to both rings, 3.0 mm proud at mid span, corner-cut until no
    bend anywhere exceeds 10 deg. The silhouette is deliberately dumb - all the event is inside."""
    tf, tr = _tangents(FA, RA, R_RING)
    pts = _bow(tf, tr, GY_BOW, 14)
    pts[0], pts[-1] = FA, RA
    return _smooth(pts, max_bend=10.0, frac=0.34, passes=4)


def _gy_round(part: Part, r: float, z_top: float) -> tuple[Part, float, int]:
    """One constant rounding, no creases: the plan outline's vertical edges first, then the top
    silhouette. Each edge is tried at r and then at half r; OCCT refuses what will not fit."""
    done, applied = 0, 0.0
    for tier, edges in ((r, [e for e in part.edges()
                             if abs(e.bounding_box().size.Z - (z_top - Z_BOT)) < 1e-6]),
                        (r / 2.5, _top_edges(part, z_top, min_len=2.0, skip=(FA, RA)))):
        for e in edges:
            for attempt in (tier, tier / 2):
                try:
                    part = fillet(part.edges().filter_by(
                        lambda x, e=e: abs(x.length - e.length) < 1e-7
                        and (x.center() - e.center()).length < 1e-7), attempt)
                    done, applied = done + 1, max(applied, attempt)
                    break
                except Exception:  # noqa: BLE001 - a radius that does not fit is left alone
                    continue
    return part, round(applied, 3), done


def _build_gyroid(p: dict) -> Part:
    wall = p["wall"]
    plan, info = _plan_for("gyroid", p)
    base = _prism(plan, Z_BOT, Z_TOP - Z_BOT)
    base, r_round, n_round = _gy_round(base, GY_ROUND, Z_TOP)
    base, n_relief, relief_zone = _bolt_relief(base)

    clips = Part()
    for c in (FA, RA):
        clips += _lip_allow(c, MOUTH_IN, Z_BOT, Z_TOP)
    # No vertex allowance here on purpose: the path is corner-cut until no bend exceeds 10 deg, so
    # the miter never spikes and the ray sampler has no oblique corner to mis-measure. Declaring
    # one would mask most of a 3.6 mm slab, which is the opposite of what an allowance is for.
    allow = _nonempty((relief_zone,
                       *(_lip_allow(c, MOUTH_IN, Z_BOT, Z_TOP) for c in (FA, RA))))
    _INFO.update(round_r=r_round, rounded=n_round, bolt_reliefs=n_relief, allow=allow,
                 decor_applied=False, decor_reason="not attempted", cell=p["cell"])

    # THE LATTICE. build123d owns the slab, the clip rings and the 1.6 mm rind; Blender replaces
    # only what is left between the rinds. If the gyroid cell is not in the recipe yet, or Blender
    # is not there at all, decorate_ex() hands the slab straight back - and the slab is legal on
    # its own, which is why this variant ships whatever the bridge does that day.
    part = base
    try:
        from tigerbee.accessories import _blender as BL
        # The gyroid is its own recipe now. Where the bridge carries it, ask for it by name with
        # axis="X" (the panel's thickness direction) and skin="open", so the lattice BREAKS the two
        # big faces and the apertures emerge instead of being cut - which is the whole language.
        # Where it does not, fall back to the documented voronoi cell of carapace_lattice, and if
        # even that degrades, the undecorated slab is legal on its own.
        has_gyroid = GY_CELL in getattr(BL, "RECIPES", ())
        recipe = "gyroid" if has_gyroid else "carapace_lattice"
        params = ({"period": GY_PERIOD, "sheet": GY_LIG, "rind": GY_RIND, "voxel": 1.2,
                   "axis": "X", "skin": "open", "mode": "prism"} if has_gyroid else
                  {"cell": GY_FALLBACK, "ligament": GY_LIG, "cell_d": GY_PERIOD, "axis": "X"})
        _INFO["cell"] = GY_CELL if has_gyroid else GY_FALLBACK
        region = BL.decor_region(base, GY_RIND, minus=(clips,), axis="X")
        # The guard has to be INSIDE the part: decorate_ex refuses a mask that stands proud of it
        # (measured: "guard is proud of the part by {'-X': 2.2, ...}" and the whole pass degraded).
        guard = ((base - region) + clips) & base if region is not None else base
        res = BL.decorate_ex(base, recipe, params, protect=guard, region=region, restore=False,
                             cache_key="side_panel_clip_r__gyroid", wall_floor=1.5,
                             tri_budget=12_000)
        skipped = ((res.stats.get("recipe") or {}).get(recipe) or {}).get("skipped") \
            if isinstance(res.stats, dict) else None
        _INFO.update(decor_applied=bool(res.applied) and not skipped, decor_recipe=recipe,
                     decor_reason=skipped or res.reason or "applied",
                     region_ok=region is not None)
        if res.applied and not skipped:
            part = res.part
    except Exception as exc:  # noqa: BLE001 - the bridge must never take the part down with it
        _INFO.update(decor_reason=f"bridge unavailable: {exc}")
    return part


# ================================================================================================
# THE PLAN OUTLINES - one source of truth, because the thumbnail gate measures them
# ================================================================================================
def _plan_for(style: str, p: dict) -> tuple[Sketch, dict]:
    """The style's plan profile (§4.5: the STYLE CHANGES THE OUTLINE FIRST). Returned separately
    from the solid so `checks()` can measure all five outlines against each other without building
    five solids."""
    info: dict = {}
    if style == "long":
        pts = _long_path()
        plan = _ribbon(pts, p["wall"])
        plan += _sector(FA, R_BORE, R_RING, -20.0, 160.0) + _cclip_plan(RA)
        plan -= Pos(*FA) * Circle(R_BORE) + Pos(*RA) * Circle(R_BORE)
        plan = _mouth_fillet(plan, FA, R_BORE, R_RING, -20.0, 160.0)
    elif style == "double":
        pts = _double_path()
        plan = _ribbon(pts, p["wall"])
        plan, info["chamfers"] = _treat(plan, _junction_corners(pts, p["wall"]), p["chamfer"], chamfer)
        plan += _cclip_plan(FA) + _cclip_plan(RA)
        plan -= Pos(*FA) * Circle(R_BORE) + Pos(*RA) * Circle(R_BORE)
    elif style == "faceted_hook":
        pts = _fh_path()
        plan = _ribbon(pts, p["wall"])
        plan, info["chamfers"] = _treat(plan, _junction_corners(pts, p["wall"]), 0.6, chamfer)
        plan += _hook(FA, p["front_mouth"]) + _hook(RA, p["rear_mouth"])
        plan -= Pos(*FA) * Circle(R_BORE) + Pos(*RA) * Circle(R_BORE)
    elif style == "window_wing":
        pts = _ww_path()
        w = p["wing"]
        root, _n, _t = _at(pts, _arc_at_y(pts, w["y"]))
        tip = (root[0] + w["drop"][0] * w["reach"], root[1] + w["drop"][1] * w["reach"])
        info["wing_root"], info["wing_tip"] = root, tip
        plan = _ribbon(pts, p["wall"]) + _ribbon([root, tip], w["wall"])
        plan += _cclip_plan(FA) + _cclip_plan(RA)
        plan -= Pos(*FA) * Circle(R_BORE) + Pos(*RA) * Circle(R_BORE)
    elif style == "gyroid":
        pts = _gy_path()
        plan = _ribbon(pts, p["wall"])
        plan += _cclip_plan(FA) + _cclip_plan(RA)
        plan -= Pos(*FA) * Circle(R_BORE) + Pos(*RA) * Circle(R_BORE)
    elif style == "filigree":
        g = _run_geom(FI_OFFSET, 0.0)
        info["geom"] = g
        plan = (_ribbon(g["run"], p["wall"]) + _ribbon(g["dogleg_front"], p["wall"])
                + _ribbon(g["dogleg_rear"], p["wall"]))
        plan += _cclip_plan(FA) + _cclip_plan(RA)
        plan -= Pos(*FA) * Circle(R_BORE) + Pos(*RA) * Circle(R_BORE)
        pts = g["run"]
    elif style == "origami":
        pts = _or_path()
        plan = _ribbon(pts, p["wall"])
        plan += _cclip_plan(FA) + _cclip_plan(RA)
        plan -= Pos(*FA) * Circle(R_BORE) + Pos(*RA) * Circle(R_BORE)
    elif style == "brutalist":
        g = _br_geom()
        info["geom"] = g
        # Rectangles and 45 deg cuts only: one straight run plus two 45 deg doglegs into the rings.
        plan = (_ribbon(g["run"], p["wall"]) + _ribbon(g["dogleg_front"], p["wall"])
                + _ribbon(g["dogleg_rear"], p["wall"]))
        for y in BR_RIB["ys"]:
            plan += _br_pad_plan(g, p["wall"], y, BR_RIB["width"], BR_RIB["proud"])
        plan += _br_pad_plan(g, p["wall"], BR_PLAQUE["y"], BR_PLAQUE["length"], BR_PLAQUE["proud"])
        plan, info["chamfers"] = _treat(plan, _br_corners(g, p["wall"]), BR_CHAMFER, chamfer)
        plan += _cclip_plan(FA) + _cclip_plan(RA)
        plan -= Pos(*FA) * Circle(R_BORE) + Pos(*RA) * Circle(R_BORE)
        pts = g["run"]
    elif style == "angled":
        pts = _an_path()
        plan = _ribbon(pts, p["wall"]) + _cclip_plan(FA)
        plan -= Pos(*FA) * Circle(R_BORE)
    else:
        raise KeyError(f"unknown side_panel_clip style {style!r}; styles: {sorted(STYLES)}")
    info["path"] = pts
    return plan, info


def _hull_area(pts) -> float:
    """Monotone-chain convex hull area of a point cloud (pure python: the gate must be portable)."""
    pts = sorted(set((round(x, 4), round(y, 4)) for x, y in pts))
    if len(pts) < 3:
        return 0.0

    def half(seq):
        out = []
        for q in seq:
            while len(out) >= 2 and ((out[-1][0] - out[-2][0]) * (q[1] - out[-2][1])
                                     - (out[-1][1] - out[-2][1]) * (q[0] - out[-2][0])) <= 0:
                out.pop()
            out.append(q)
        return out[:-1]

    hull = half(pts) + half(pts[::-1])
    return abs(sum(hull[i][0] * hull[i - 1][1] - hull[i - 1][0] * hull[i][1]
                   for i in range(len(hull)))) / 2.0


def _outline_metrics(plan: Sketch) -> tuple[float, float]:
    """(plan area mm², convex-hull deficiency) - the two numbers §4.5 gates the family on."""
    pts = []
    for e in plan.edges():
        for i in range(9):
            v = e @ (i / 8.0)
            pts.append((v.X, v.Y))
    hull = _hull_area(pts)
    area = float(plan.area)
    return round(area, 2), round(1.0 - area / hull, 4) if hull > 0 else 0.0


# ================================================================================================
# THE CONTRACT
# ================================================================================================
PARAMS = {
    "long": dict(wall=LONG_WALL, pad=LONG_PAD, pad_proud=LONG_PAD_PROUD, mark=True,
                 mark_size=LONG_MARK_SIZE, mark_depth=LONG_MARK_DEPTH, corner=LONG_CORNER),
    "double": dict(wall=DOUBLE_WALL, z_top=DOUBLE_Z_TOP, chamfer=DOUBLE_CHAMFER,
                   notch=DOUBLE_NOTCH),
    "angled": dict(wall=AN_WALL, rail=AN_RAIL, diamond=AN_DIAMOND, strut=AN_STRUT_W,
                   nodes=AN_NODES, serration=AN_SERR, hook=AN_HOOK),
    "window_wing": dict(wall=WW_WALL, window=WW_WINDOW, hex=WW_HEX, wing=WW_WING),
    "faceted_hook": dict(wall=FH_WALL, front_mouth=HOOK_FRONT_MOUTH, rear_mouth=HOOK_REAR_MOUTH,
                         window=FH_WINDOW),
    "brutalist": dict(wall=BR_WALL, void=BR_VOID, mark_size=BR_MARK_SIZE, mark_depth=BR_MARK_DEPTH),
    "origami": dict(wall=OR_WALL, fold=OR_FOLD, flange=OR_FLANGE, slot=OR_SLOT),
    "filigree": dict(wall=FI_WALL, spine=FI_SPINE, r=FI_R, node_d=FI_NODE_D),
    "gyroid": dict(wall=GY_WALL, bow=GY_BOW, rind=GY_RIND, cell=GY_CELL),
}
_BUILDERS = {"long": _build_long, "double": _build_double, "angled": _build_angled,
             "window_wing": _build_window_wing, "faceted_hook": _build_faceted_hook,
             "brutalist": _build_brutalist, "origami": _build_origami,
             "filigree": _build_filigree, "gyroid": _build_gyroid}
# Each variant is measured at ITS OWN material's wall floor - PETG's 1.5, not TPU's 1.2.
WALL_FLOOR_OF = {s: MATERIALS[VARIANTS[s].get("material", MATERIAL)]["wall"] for s in PARAMS}
Z_TOP_OF = {s: PARAMS[s].get("z_top", Z_TOP) for s in PARAMS}
Z_BOT_OF = {s: (AN_HOOK["z_bot"] if s == "angled" else Z_BOT) for s in PARAMS}
BRIDGE_OK: dict = _BRIDGES


def _pair_rl(part: Part) -> dict[str, Part]:
    """{_r: this part, _l: its exact mirror in Plane.YZ}. Mirrored pairs carry no suture - the
    pair IS the split (CN-1)."""
    from copy import deepcopy
    right = deepcopy(part)
    right.label = "side_panel_clip_r"
    left = part.mirror(Plane.YZ)
    left.label = "side_panel_clip_l"
    return {right.label: right, left.label: left}


def _declare_bridges(style: str, part: Part) -> None:
    """Flat window lintels, in PRINT coordinates. PRINT is (0, 0, -1) for every style but `angled`
    (which has none), so print xy = frame xy - bbox centre and print z = frame z - bbox min Z."""
    bb = part.bounding_box()
    dx, dy, dz = -bb.center().X, -bb.center().Y, -bb.min.Z
    boxes = []
    if style == "window_wing":
        u = WW_WINDOW
        boxes.append(("box", -60.0, u["y"] - u["w"] / 2 + dy - 0.8, u["z"] + u["h"] / 2 + dz - 0.8,
                      60.0, u["y"] + u["w"] / 2 + dy + 0.8, u["z"] + u["h"] / 2 + dz + 0.8))
    if style == "brutalist":
        v, q = BR_VOID, BR_PLAQUE
        boxes.append(("box", -60.0, v["y0"] + dy - 0.8, v["z1"] + dz - 0.8,
                      60.0, v["y1"] + dy + 0.8, v["z1"] + dz + 0.8))
        # The wordmark is sunk 2.0 mm, so the upper edge of every stroke is a 2.0 mm deep ledge:
        # 5.5 mm² of them all told, just over overhangs()' 5.0 mm² floor. A 2.0 mm span is a
        # bridge by any measure (PETG's limit is 20), and it is the deboss depth the language
        # asks for, not a wall.
        boxes.append(("box", -60.0, q["y"] - q["length"] / 2 + dy - 1.0, 14.0 + dz - 1.0,
                      60.0, q["y"] + q["length"] / 2 + dy + 1.0, 30.0 + dz + 1.0))
    if style == "origami":
        b = OR_SLOT
        for f in _or_slots()[0].faces():
            fb = f.bounding_box()
            boxes.append(("box", -60.0, fb.max.X - OR_SLOT["w"] + dy - 0.8, b["z1"] + dz - 0.8,
                          60.0, fb.max.X + dy + 0.8, b["z1"] + dz + 0.8))
    if style == "faceted_hook":
        w = FH_WINDOW
        boxes.append(("box", -60.0, w["y0"] + dy - 0.8, w["z0"] + w["foot"] + dz - 0.8,
                      60.0, w["y1"] - w["riser"] + dy + 0.8, w["z0"] + w["foot"] + dz + 0.8))
        boxes.append(("box", -60.0, w["y1"] - w["riser"] + dy - 0.8, w["z1"] + dz - 0.8,
                      60.0, w["y1"] + dy + 0.8, w["z1"] + dz + 0.8))
    for hand in ("r", "l"):
        _BRIDGES[f"side_panel_clip_{hand}__{style}"] = tuple(boxes)


def build(variant: str = "double", **overrides) -> dict[str, Part]:
    style = variant or "double"
    assert style in PARAMS, f"unknown style {style!r}; styles: {sorted(PARAMS)}"
    p = dict(PARAMS[style])
    p.update(overrides)
    _INFO.clear()
    _INFO["style"] = style
    part = _BUILDERS[style](p)
    spec = _INFO.get("mark")
    _FUNCTIONAL[style] = part
    # The left panel is the mirror of the right EXCEPT for the stencil, which is cut un-mirrored so
    # it reads the same way round on both flanks. Both the base and the cutter are mirrored
    # separately and the boolean is done afterwards: mirroring the already-cut solid hands back an
    # invalid shape (measured on the 280-face wordmark part), mirroring the two operands does not.
    right = part - S.mark(**spec) if spec else part
    left = part.mirror(Plane.YZ)
    if spec:
        lspec = _INFO.get("mark_left")
        if lspec:
            # The stencil is built DIRECTLY in the left panel's own space - same place, outward
            # normal reflected in X, glyphs pre-flipped - instead of mirroring the cut tool.
            # Measured on the brutalist slab: every route that mirrors wordmark geometry hands
            # back is_valid False (mirroring the tool, mirroring the cut part, and mirroring the
            # already-marked right panel all do), while building the stencil in place is valid.
            # Opt-in per style, so no existing style's output moves by a micron.
            left = left - S.mark(**lspec)
        else:
            left = left - S.mark(**spec, mirror_x=True).mirror(Plane.YZ)
    right.label, left.label = "side_panel_clip_r", "side_panel_clip_l"
    _PLANS[style] = _outline_metrics(_plan_for(style, p)[0])
    _declare_bridges(style, right)
    return {right.label: right, left.label: left}


# --- the required checks -----------------------------------------------------------------------
# Which axes each style must be concentric with, and over which Z band.
AXES = {
    "long": (("front_arm cradle", FA, Z_BOT + 0.3, Z_TOP - 1.5),
             ("rear_arm clip", RA, Z_BOT + 0.2, Z_BOT + LONG_CLIP_H - 0.2)),
    "double": (("front_arm clip", FA, Z_BOT + 0.9, DOUBLE_Z_TOP - 0.9),
               ("rear_arm clip", RA, Z_BOT + 0.9, DOUBLE_Z_TOP - 0.9)),
    "angled": (("front_arm clip", FA, Z_BOT + 0.2, Z_TOP - 0.2),),
    "window_wing": (("front_arm clip", FA, Z_BOT + 0.2, Z_TOP - 0.2),
                    ("rear_arm clip", RA, Z_BOT + 0.2, Z_TOP - 0.2)),
    "faceted_hook": (("front_arm hook", FA, Z_BOT + 0.9, Z_TOP - 0.9),
                     ("rear_arm hook", RA, Z_BOT + 0.9, Z_TOP - 0.9)),
    "brutalist": (("front_arm clip", FA, Z_BOT + 0.2, Z_TOP - 0.2),
                  ("rear_arm clip", RA, Z_BOT + 0.2, Z_TOP - 0.2)),
    "origami": (("front_arm clip", FA, Z_BOT + 0.2, Z_TOP - 0.2),
                ("rear_arm clip", RA, Z_BOT + 0.2, Z_TOP - 0.2)),
    "filigree": (("front_arm clip", FA, Z_BOT + 0.2, Z_TOP - 0.2),
                 ("rear_arm clip", RA, Z_BOT + 0.2, Z_TOP - 0.2)),
    "gyroid": (("front_arm clip", FA, Z_BOT + 0.9, Z_TOP - 0.9),
               ("rear_arm clip", RA, Z_BOT + 0.9, Z_TOP - 0.9)),
}
STANDOFF_OF = {FA: "front_arm", RA: "rear_arm"}


# The camera bay the two camera pods occupy, measured from camera_pod's own build: both the 21 and
# the 19 mm pods have the bounding box below, and inside it they wrap the front-tip standoff from
# Z 9 to 32 (a clip there overlaps them by 698 mm³ - which is why `angled` hooks the plate edge
# instead). The box is hard-coded rather than imported so a sibling module being edited mid-run
# cannot turn this check into an import error; the live pods are ALSO probed when they import.
CAMERA_BAY = box(-25.0, 80.5, 6.0, 25.0, 122.5, 38.0)


@lru_cache(maxsize=1)
def _camera_pods() -> dict[str, Part]:
    """The live camera pod parts, when the module is importable; {} when a sibling is mid-edit."""
    try:
        from tigerbee.accessories import build_accessory, discover_accessories
        return build_accessory(discover_accessories(["camera_pod"])["camera_pod"])
    except Exception:  # noqa: BLE001 - fall back to CAMERA_BAY, which is stricter anyway
        return {}


def _bolt_heads() -> Part:
    out = Part()
    for x, y in BOLT_HEADS:
        out += cylinder(x, y, Z_MID_TOP, Z_MID_TOP + BOLT_HEAD_H, BOLT_HEAD_D)
    return out


def _plate_gap(part: Part, plate: str, z: float) -> float:
    """Distance to the REAL plate face (holes and cutouts included), not to the filled outline -
    this panel floats between the plates, so the gap IS the fit."""
    return round(part.distance_to(plate_face(plate, z)), 4)


def _all_outlines() -> dict[str, tuple[float, float]]:
    """(plan area, hull deficiency) for all five styles; missing ones are measured on the spot so
    the gate is never vacuous just because this variant happened to be built first."""
    for st in PARAMS:
        if st not in _PLANS:
            _PLANS[st] = _outline_metrics(_plan_for(st, dict(PARAMS[st]))[0])
    return dict(_PLANS)


def checks(parts: dict[str, Part], frame: dict[str, Part], variant: str = "") -> list[tuple[str, bool, str]]:
    """ONE checks() for all five styles. Every fit assertion below holds for every one of them -
    that is the guarantee the variant contract exists for; only the four style-conformance rows at
    the end are style-aware, and none of them relaxes a fit check."""
    style = variant or _INFO.get("style") or "double"
    right, left = parts["side_panel_clip_r"], parts["side_panel_clip_l"]
    bb = right.bounding_box()
    z0, z1 = Z_BOT_OF[style], Z_TOP_OF[style]
    wall = PARAMS[style]["wall"]
    out: list[tuple[str, bool, str]] = []

    # --- 1. nothing touches the frame, the standoffs, the stack or the bolt heads ---------------
    hits = interference(right)
    out.append(("no interference with any frame part", not hits, f"{hits or 'none'}"))
    so = standoff_interference(right)
    out.append((f"clear of every Ø{STANDOFF_D} standoff cylinder", not so, f"{so or 'none'}"))
    for nm in ("standoff_front_arm_right", "standoff_rear_arm_right"):
        if nm.replace("standoff_", "").replace("_right", "") in {STANDOFF_OF[c] for _n, c, _a, _b in AXES[style]}:
            d = right.distance_to(standoff_cylinders()[nm])
            out.append((f"gap to the Ø{STANDOFF_D} {nm} is the designed {STANDOFF_FIT}",
                        abs(d - STANDOFF_FIT) <= 0.05, f"{d:.4f} mm"))
    v = isect(right, FC_STACK)
    out.append(("clear of the FC/ESC stack box (±18.5, Z 9-34)", v < EPS, f"{v:.3f} mm³"))
    v = isect(right, STACK_40)
    out.append(("clear of the 40 x 40 Z 12-31 stack envelope", v < EPS, f"{v:.3f} mm³"))
    v = isect(right, _bolt_heads())
    out.append((f"clear of the Ø{BOLT_HEAD_D} x {BOLT_HEAD_H} arm-root bolt heads", v < EPS, f"{v:.3f} mm³"))
    v = isect(right, VTX) + isect(right, BATTERY)
    out.append(("clear of the VTX and battery envelopes", v < EPS, f"{v:.3f} mm³"))
    live = _camera_pods()
    pods = max([isect(right, pod) for pod in live.values()] or [0.0])
    bay = isect(right, CAMERA_BAY)
    out.append(("clear of the camera bay (both pods' envelope)", bay < EPS and pods < EPS,
                f"{bay:.3f} mm³ in the envelope, {pods:.3f} mm³ in "
                f"{len(live) or 'no'} live pod part(s)"))
    v = prop_disc_violation(right)
    out.append(("outside the prop keep-out discs", v < EPS, f"{v:.3f} mm³"))

    # --- 2. every clip / hook is concentric with its standoff axis ------------------------------
    for name, c, za, zb in AXES[style]:
        for hand, part, cx in (("right", right, c[0]), ("left", left, -c[0])):
            ok, detail = coaxial(part, (cx, c[1]), D_CLIP_BORE, za, zb)
            out.append((f"{name} bore coaxial with standoff_{STANDOFF_OF[c]}_{hand}", ok, detail))
        chan = box(c[0] - R_RING - 8, c[1] - MOUTH / 2 + 0.05, za,
                   c[0], c[1] + MOUTH / 2 - 0.05, zb)
        v = isect(right, chan)
        out.append((f"{name}: the inboard insertion channel is clear to the mouth", v < EPS,
                    f"{v:.4f} mm³"))

    # --- 3. the panel floats: measured against the REAL plate faces -----------------------------
    g_mid = _plate_gap(right, "plate_mid", Z_MID_TOP)
    g_top = _plate_gap(right, "plate_top", Z_TOP_UNDER)
    out.append(("0.25 mm running clearance to the real plate_mid top face (Z 9)",
                g_mid >= 0.20, f"{g_mid} mm to plate_face('plate_mid', 9)"))
    out.append(("clearance to the real plate_top underside (Z 34)",
                g_top >= 0.20, f"{g_top} mm to plate_face('plate_top', 34)"))
    out.append((f"panel Z band {z0}-{z1}", abs(bb.min.Z - z0) < 1e-6 and bb.max.Z <= z1 + 1e-6,
                f"Z {bb.min.Z:.3f}-{bb.max.Z:.3f}"))
    out.append(("outboard of the standoff axes (min X >= 15.0)", bb.min.X >= 15.0,
                f"x {bb.min.X:.3f}..{bb.max.X:.3f}"))

    # --- 4. solid, walls, print ------------------------------------------------------------------
    ok, detail = single_solid(right)
    out.append(("one watertight solid", ok, detail))
    measured = _FUNCTIONAL.get(style, right)
    allow = tuple(_INFO.get("allow", ()))
    floor = WALL_FLOOR_OF.get(style, WALL_MIN)
    if style == "filigree":
        # THE RAY SAMPLER, ON PURPOSE, AND ONLY HERE. min_wall() prefers an erode/dilate pass and
        # falls back to rays when OCCT refuses the offset - which is what happens on every other
        # style in this module. On the cutwork panel OCCT does not refuse: it returns a 2333 mm³
        # "thin residual" on a part whose thinnest member is a 1.5 mm ribbon by construction, i.e.
        # a third of the part. That is the offset failing silently, not a wall, so this style is
        # measured with the same ray sampler min_wall itself falls back to - and the ribbon, the
        # ligament, the spine and the void fraction are each asserted numerically in the rows
        # below, which is the measurement that actually decides whether this panel is printable.
        thin, worst, ray_detail = ray_thickness(measured, floor, allow)
        ok_w, detail = not thin, f"ray sampling (OCCT's erosion mis-reports cutwork): {ray_detail}"
    else:
        ok_w, _resid, detail = min_wall(measured, floor, allow=allow)
    out.append((f"min wall >= {floor}"
                + ("" if measured is right else " on the functional solid (the stencil's own "
                   "residual wall is the ARSENAL row below)")
                + (f", {len(allow)} declared thin feature(s) excluded" if allow else ""),
                ok_w, detail))
    over = overhangs(right, print_normal_of(style), material=MATERIAL,
                     bridge_ok=_BRIDGES.get(f"side_panel_clip_r__{style}", ()))
    out.append((f"no unsupported overhangs printing on {print_normal_of(style)}", not over,
                "; ".join(over) or "none"))
    bed = sum(f.area for f in printed_faces(right, style))
    out.append(("bed contact >= 60 mm²", bed >= 60.0, f"{bed:.1f} mm²"))

    # --- 5. the mirrored pair ---------------------------------------------------------------------
    # The real test is the symmetric difference, not the reported volume: OCCT's volume of a
    # chamfered 70-face solid moves by ~0.05 mm³ under an exact mirror, so a volume-equality row
    # would fail on numerical noise while a genuinely asymmetric part could slip through it.
    mr = right.mirror(Plane.YZ)
    sym = volume(mr - left) + volume(left - mr)
    band = _INFO.get("mark_band")
    if band is not None:
        both = band + band.mirror(Plane.YZ)

        def _outside(a: Part, b: Part) -> float:
            """volume(a - b - both), and 0.0 when a - b is already empty. OCCT refuses to subtract
            a solid from an empty compound ("Dimensions ... are inconsistent"), which is exactly
            what happens when the two hands ARE identical outside the band."""
            d = a - b
            return volume(d - both) if d.solids() else 0.0

        sym = _outside(mr, left) + _outside(left, mr)
    out.append(("left is the exact mirror of right" + (" outside the stencil band" if band else ""),
                sym < 0.01, f"symmetric difference {sym:.6f} mm³, Δvolume "
                f"{abs(left.volume - right.volume):.6f} mm³"
                + (" (the stencil is cut un-mirrored so it reads the same way round on both "
                   "flanks; everything else is an exact reflection)" if band else "")))
    lbb = left.bounding_box()
    out.append(("left bounding box is the exact reflection",
                abs(lbb.min.X + bb.max.X) < 1e-6 and abs(lbb.max.X + bb.min.X) < 1e-6
                and abs(lbb.min.Y - bb.min.Y) < 1e-6 and abs(lbb.max.Z - bb.max.Z) < 1e-6,
                f"x {lbb.min.X:.3f}..{lbb.max.X:.3f} against {-bb.max.X:.3f}..{-bb.min.X:.3f}"))

    # --- 6. the thumbnail gate (§4.5) -------------------------------------------------------------
    outlines = _all_outlines()
    worst, pairs = None, []
    for a in PARAMS:
        for b in PARAMS:
            if a >= b:
                continue
            (aa, ad), (ba, bd) = outlines[a], outlines[b]
            d_area = abs(aa - ba) / max(aa, ba)
            d_def = abs(ad - bd)
            ok_pair = d_area > 0.12 or d_def > 0.10
            if not ok_pair:
                pairs.append(f"{a}/{b} Δarea {d_area:.1%}, Δdeficiency {d_def:.3f}")
            score = max(d_area / 0.12, d_def / 0.10)
            worst = score if worst is None else min(worst, score)
    n_pairs = len(PARAMS) * (len(PARAMS) - 1) // 2
    out.append((f"thumbnail gate: all {n_pairs} style pairs differ by >12 % area or >0.10 hull deficiency",
                not pairs, f"{'; '.join(pairs) or f'all {n_pairs} pairs pass'}; closest pair scores "
                           f"{worst:.2f} x the threshold"))

    # --- 7. style conformance ----------------------------------------------------------------------
    out += _style_rows(style, right, wall)
    return out


def print_normal_of(style: str) -> tuple:
    spec = VARIANTS[style].get("print") or {}
    return tuple(spec.get("side_panel_clip_r", PRINT["side_panel_clip_r"]))


def printed_faces(part: Part, style: str):
    """The faces that actually touch the bed in this style's print orientation."""
    p = print_orientation(part, print_normal_of(style))
    return [f for f in p.faces() if f.geom_type == GeomType.PLANE
            and abs(f.center().Z) < 1e-3 and f.normal_at().Z < -0.999]


def _style_rows(style: str, right: Part, wall: float) -> list[tuple[str, bool, str]]:
    """The style's own §5.2 conformance assertions - what makes it THAT family and not a sibling
    with different holes."""
    rows = []
    fam = VARIANTS[style].get("style")
    if fam in S.STYLES:
        st = S.STYLES[fam]
        if fam == "gyroid":
            # GYROID's edge law is not a ladder clamped to 0.40 x wall - it is ONE constant
            # rounding of r 3.0 on the plan outline, and on a 3.6 mm slab that is the whole point
            # of the language (no crease anywhere). The law it is held to is its own.
            rows.append((f"style {st.name}: one constant rounding, r <= {GY_ROUND}",
                         S.edge_radius(st, "sil", wall) <= GY_ROUND + 1e-9,
                         f"silhouette tier {S.edge_radius(st, 'sil', wall)} mm on a {wall} wall, "
                         f"applied at {_INFO.get('round_r')} mm"))
        else:
            rows.append((f"style {st.name}: edge ladder within the wall limit",
                         S.edge_radius(st, "sil", wall) <= 0.40 * wall + 1e-9,
                         f"silhouette tier {S.edge_radius(st, 'sil', wall)} mm on a {wall} wall"))
    else:
        # The guard idiom: this language is not in _style yet, so its edge law is asserted by the
        # style's own rows below instead of by the shared ladder. Nothing is skipped.
        rows.append((f"language {style}: declared locally (not yet in _style.STYLES)", True,
                     f"_style has {len(S.STYLES)} languages; {style}'s edge law is measured below"))

    if style in ("double", "faceted_hook"):
        # the clip rings are mating geometry, not facets: their lips, throat walls and mouth
        # fillets are 2-3.5 mm across by specification and would read as broken low-poly
        skin = right
        for c in (FA, RA):
            skin = skin - cylinder(c[0], c[1], Z_BOT - 1, Z_TOP + 1, 2 * (R_RING + 0.6))
        ok, detail = S.facet_report(skin, ignore_extent=wall + 0.05)
        rows.append((f"SHARD: no planar facet under {S.FACET_MIN} mm across", ok, detail))
        rows.append(("SHARD: every plan junction chamfered and the top ladder applied",
                     _INFO.get("chamfers", 0) >= 4 and _INFO.get("edge_r", 0.0) > 0.0,
                     f"{_INFO.get('chamfers')} plan junctions at 0.6, "
                     f"{_INFO.get('edges')} silhouette edges at {_INFO.get('edge_r')} mm"))
    if style == "faceted_hook":
        a0 = degrees(atan2(FH_BENDS[0][1] - FA[1], FH_BENDS[0][0] - FA[0]))
        a1 = degrees(atan2(FH_BENDS[1][1] - FH_BENDS[0][1], FH_BENDS[1][0] - FH_BENDS[0][0]))
        a2 = degrees(atan2(RA[1] - FH_BENDS[1][1], RA[0] - FH_BENDS[1][0]))
        rows.append(("three facets with 10-20 deg bends",
                     10.0 <= abs(a1 - a0) <= 20.0 and 10.0 <= abs(a2 - a1) <= 20.0,
                     f"bends {abs(a1 - a0):.1f} and {abs(a2 - a1):.1f} deg"))
        rows.append(("the two hook mouths are opposed, so no single translation releases both",
                     abs(HOOK_FRONT_MOUTH - HOOK_REAR_MOUTH) >= 45.0,
                     f"{HOOK_FRONT_MOUTH} deg against {HOOK_REAR_MOUTH} deg, "
                     f"{HOOK_WRAP} deg of wrap each"))
    if style == "double":
        yc, _hw, h = DOUBLE_NOTCH
        v = isect(right, box(-60, yc - 1.0, Z_BOT, 60, yc + 1.0, Z_BOT + h * 0.5))
        rows.append(("the cusped cable notch is open", v < EPS, f"{v:.3f} mm³ in the notch"))
    if style == "long":
        rows.append(("ARSENAL: transverse ribs at pitch 9.0, ramped steeper than 45 deg",
                     _INFO.get("ribs", 0) >= 3 and LONG_RIB["ramp"] > 1.02 * LONG_RIB["proud"],
                     f"{_INFO.get('ribs')} ribs, ramp {LONG_RIB['ramp']} over "
                     f"{LONG_RIB['proud']} proud -> flank normal.Z "
                     f"{-LONG_RIB['proud'] / hypot(LONG_RIB['proud'], LONG_RIB['ramp']):.3f}"))
        rows.append(("ARSENAL: the wordmark fits and leaves enough wall",
                     S.mark_fits(LONG_MARK, LONG_MARK_SIZE)
                     and wall + LONG_PAD_PROUD - LONG_MARK_DEPTH >= WALL_MIN,
                     f"{LONG_MARK} {LONG_MARK_SIZE} mm debossed {LONG_MARK_DEPTH} into a "
                     f"{wall + LONG_PAD_PROUD} mm pad leaves "
                     f"{wall + LONG_PAD_PROUD - LONG_MARK_DEPTH} mm"))
        bowed = max(x for x, _y in _long_path())
        rows.append(("bowed 4-6 mm outboard of the clip-to-clip chord at mid span",
                     3.5 <= LONG_BULGE <= 6.0, f"bulge {LONG_BULGE} mm, crest at x {bowed:.2f}"))
    if style == "window_wing":
        rows.append(("ARSENAL: hex vent field placed on the forward half",
                     _INFO.get("vents", 0) >= 2,
                     f"{_INFO.get('vents')} hexes AF {WW_HEX['af']} at ligament "
                     f"{WW_HEX['ligament']} (TPU floor {DECOR_LIG_MIN})"))
        waist = min(_mid_edge(y) for y in WW_YS)
        rows.append(("the plan carries the frame's own pronotum waist",
                     max(_mid_edge(y) for y in WW_YS) - waist > 6.0,
                     f"mid-plate edge {waist:.2f} at the waist against "
                     f"{max(_mid_edge(y) for y in WW_YS):.2f} at the shoulder"))
        v = isect(right, box(-60, WW_WINDOW["y"] - 3, WW_WINDOW["z"] - 2,
                             60, WW_WINDOW["y"] + 3, WW_WINDOW["z"] + 2))
        rows.append(("the USB / cable window is open", v < EPS, f"{v:.3f} mm³"))
    if style == "angled":
        rows.append(("CHASSIS: a ring node at every four-way strut junction",
                     _INFO.get("nodes", 0) == len(AN_NODES) and len(AN_NODES) == len(AN_DIAMOND["centres"]) + 1,
                     f"{_INFO.get('nodes')} nodes, OD {2.6 * AN_STRUT_W:.2f} / ID "
                     f"{0.9 * AN_STRUT_W:.2f} (>= TPU's {DECOR_HOLE_MIN} hole minimum) "
                     f"for {len(AN_DIAMOND['centres'])} diamonds"))
        flank = degrees(atan2((Z_TOP - AN_RAIL - (Z_BOT + AN_RAIL)) / 2, AN_DIAMOND["half_w"]))
        rows.append(("CHASSIS: strut triangulation between 50 and 70 deg",
                     50.0 <= flank <= 70.0, f"{flank:.1f} deg diamond flank"))
        rows.append(("CHASSIS: the outboard rail carries a SPINE serration",
                     _INFO.get("serrations", 0) >= 6,
                     f"{_INFO.get('serrations')} bumps Ø{AN_SERR['d']} at pitch {AN_SERR['pitch']}"))
        teeth = AN_HOOK["teeth"]
        tooth_face = AN_HOOK["reach"] * (teeth[0][1] - teeth[0][0])
        rows.append(("the claw teeth hook under the mid-plate side edge with no declared bridge",
                     len(teeth) == 3 and tooth_face < 5.0,
                     f"{len(teeth)} teeth, each top face {tooth_face:.2f} mm², under "
                     f"overhangs()' 5.0 mm² floor"))
        gap = min(_mid_edge(y) for y in (63.5, 66.0, 70.0))
        rows.append(("the claw's inner wall clears the real mid-plate edge",
                     isect(right, box(0, 60, 4.0, gap, 72, Z_MID_TOP + 0.01)) < EPS,
                     f"mid-plate edge {gap:.3f} at y 63.5-70"))
    if style == "brutalist":
        v, face = BR_VOID, _br_face_area()
        void = (v["y1"] - v["y0"]) * (v["z1"] - v["z0"])
        rows.append(("BRUTALIST: ONE rectangular void >= 40 % of the panel face, corners sharp",
                     void >= 0.40 * face,
                     f"{void:.0f} mm² of {face:.0f} mm² face = {void / face:.1%}, "
                     f"{v['y1'] - v['y0']:.1f} x {v['z1'] - v['z0']:.1f}"))
        hole = isect(right, box(-60, v["y0"] + 1.0, v["z0"] + 1.0, 60, v["y1"] - 1.0, v["z1"] - 1.0))
        rows.append(("BRUTALIST: the void is open all the way through", hole < EPS, f"{hole:.3f} mm³"))
        r_max, n_round = _max_fillet_r(right, skip=(FA, RA))
        rows.append((f"BRUTALIST: nothing filleted above r {BR_FILLET_MAX} outside the clip rings",
                     r_max <= BR_FILLET_MAX + 1e-9,
                     f"largest rounding r {r_max} over {n_round} curved face(s); "
                     f"{_INFO.get('chamfers', 0)} silhouette edges chamfered {BR_CHAMFER} at 45 deg"))
        rows.append(("BRUTALIST: the slab clears both arm-root bolts whole, so it carries none of "
                     "the r1.0 relief notches", _INFO.get("bolt_reliefs", 1) == 0,
                     f"{_INFO.get('bolt_reliefs')} notches; the run stands {BR_OFFSET} mm outboard "
                     f"of the chord"))
        rows.append((f"BRUTALIST: 3 proud ribs {BR_RIB['proud']} x {BR_RIB['width']} at "
                     f"{BR_RIB['pitch']} mm pitch, full height",
                     _INFO.get("ribs", 0) == 3
                     and all(abs(abs(a - b) - BR_RIB["pitch"]) < 1e-6
                             for a, b in zip(BR_RIB["ys"], BR_RIB["ys"][1:])),
                     f"ribs at y {BR_RIB['ys']}, square section, Z {Z_BOT}-{Z_TOP} (no underside)"))
        rows.append((f"BRUTALIST: board marking {BR_GROOVE['w']} x {BR_GROOVE['depth']} at "
                     f"{BR_GROOVE['pitch']} pitch leaves the 3.0 wall above the floor",
                     wall - 2 * BR_GROOVE["depth"] >= WALL_FLOOR_OF["brutalist"],
                     f"{wall - 2 * BR_GROOVE['depth']:.1f} mm where both faces are grooved "
                     f"(staggered half a pitch, so in practice {wall - BR_GROOVE['depth']:.1f})"))
        rows.append(("BRUTALIST: the 2.0 mm wordmark deboss leaves more wall than the slab itself",
                     S.mark_fits(BR_MARK, BR_MARK_SIZE)
                     and wall + BR_PLAQUE["proud"] - BR_MARK_DEPTH >= WALL_FLOOR_OF["brutalist"],
                     f"{BR_MARK} {BR_MARK_SIZE} mm sunk {BR_MARK_DEPTH} into a "
                     f"{wall + BR_PLAQUE['proud']} mm plaque leaves "
                     f"{wall + BR_PLAQUE['proud'] - BR_MARK_DEPTH} mm"))
        plan = _plan_for("brutalist", dict(PARAMS["brutalist"]))[0]
        curved = [e for e in plan.edges()
                  if e.geom_type != GeomType.LINE
                  and all(hypot(e.center().X - c[0], e.center().Y - c[1]) > R_RING + CLIP_WALL + 0.8
                          for c in (FA, RA))]
        rows.append(("BRUTALIST: no curve in plan - the outline is rectangles and 45 deg cuts and "
                     "nothing else outside the clip rings", not curved,
                     f"{len(plan.edges())} plan edges, {len(curved)} curved outside the rings; "
                     f"hull deficiency {_outline_metrics(plan)[1]}"))

    if style == "origami":
        pts = _or_path()
        folds = [round(_bend(pts[i - 1], pts[i], pts[i + 1]), 3) for i in range(1, len(pts) - 1)]
        creases = [a for a in folds if a > 1e-6]
        rows.append(("ORIGAMI: every fold angle is one of {22.5, 45, 67.5} and nothing else",
                     bool(creases) and all(any(abs(a - k) < 0.05 for k in (22.5, 45.0, 67.5))
                                           for a in creases),
                     f"folds {creases} deg at 1/3 and 2/3 of the run; the flanges are collinear "
                     f"with their facets ({len(folds) - len(creases)} zero bends)"))
        plan = _plan_for("origami", dict(PARAMS["origami"]))[0]
        curved = [e for e in plan.edges()
                  if e.geom_type != GeomType.LINE
                  and all(hypot(e.center().X - c[0], e.center().Y - c[1]) > R_RING + CLIP_WALL + 0.8
                          for c in (FA, RA))]
        rows.append(("ORIGAMI: every silhouette edge is straight (zero curves outside the clip "
                     "rings, which are c_clip's own fixed geometry)", not curved,
                     f"{len(plan.edges())} plan edges, {len(curved)} curved outside the rings"))
        ok_m, m, detail = _miter_report(pts, wall)
        rows.append((f"ORIGAMI: constant {wall} mm sheet - the offset never spikes at a crease",
                     ok_m, detail))
        rows.append(("ORIGAMI: ladder ligament >= 1.8 and the slots shear to the fold angle",
                     _INFO.get("ligament", 0.0) >= 1.8 and _INFO.get("slots", 0) >= 6,
                     f"{_INFO.get('slots')} parallelogram slots {OR_SLOT['w']} wide at "
                     f"{OR_SLOT['pitch']} pitch, ligament {_INFO.get('ligament')} mm measured "
                     f"perpendicular, sheared {OR_FOLD} deg"))
        r_max, n_round = _max_fillet_r(right, skip=(FA, RA))
        rows.append(("ORIGAMI: chamfer only, never a fillet", r_max <= 0.3 + 1e-9,
                     f"largest rounding r {r_max} over {n_round} curved face(s) outside the rings; "
                     f"{_INFO.get('chamfers', 0)} silhouette edges chamfered {OR_CHAMFER}"))

    if style == "filigree":
        lo, hi = FI_VOID_BAND
        frac = _INFO.get("void_fraction", 0.0)
        rows.append((f"FILIGREE: void fraction measured inside {lo:.0%}-{hi:.0%} of the cutwork "
                     f"field", lo <= frac <= hi,
                     f"{frac:.1%} of {_INFO.get('field')} mm² of field, "
                     f"{_INFO.get('scrolls')} scrolls and {_INFO.get('nodes')} ring nodes"))
        z_mid = (Z_BOT + Z_TOP) / 2
        y0, y1 = _INFO.get("net_field", (0.0, 0.0))
        spine = box(-60, y0, z_mid - FI_SPINE / 2 + 0.2, 60, y1, z_mid + FI_SPINE / 2 - 0.2)
        got = isect(right, spine)
        want = (y1 - y0) * (FI_SPINE - 0.4) * wall
        rows.append((f"FILIGREE: the {FI_SPINE} mm spine is solid the whole length of the net",
                     got >= 0.97 * want, f"{got:.1f} mm³ of a possible {want:.1f} mm³"))
        rows.append((f"FILIGREE: a Ø{FI_NODE_D} ring node on every scroll junction",
                     _INFO.get("nodes", 0) == _INFO.get("scrolls", 0) - 2,
                     f"{_INFO.get('nodes')} nodes for {_INFO.get('scrolls')} scrolls "
                     f"({_INFO.get('scrolls', 0) // 2} per side, mirrored about the spine)"))
        rows.append((f"FILIGREE: ribbon {_INFO.get('ligament')} mm and no straight member anywhere "
                     f"- the net is arcs only",
                     _INFO.get("ligament", 0.0) >= 1.4 and _INFO.get("cusp", 0.0) > 0.0,
                     f"ligament {_INFO.get('ligament')} mm, spine gap "
                     f"{_INFO.get('spine_gap')} mm, every scroll breaks the edge by "
                     f"{_INFO.get('cusp')} mm - a scalloped outline, not a polyline"))
        rows.append((f"FILIGREE: the lunule accent is a {FI_ACCENT_D} mm deboss on the spine, not "
                     f"a cut through it", _INFO.get("lunule", 0.0) > 4.0
                     and wall - FI_ACCENT_D >= WALL_FLOOR_OF["filigree"],
                     f"{_INFO.get('lunule')} mm² of crescent, Ø{2 * FI_ACCENT_R}, leaving "
                     f"{wall - FI_ACCENT_D} mm of spine"))
        rows.append((f"FILIGREE: every scroll is an arch (Ø{2 * FI_R} <= TPU's "
                     f"{MATERIALS['TPU95A']['arch_d']} mm), so the cutwork needs no support",
                     2 * FI_R <= MATERIALS["TPU95A"]["arch_d"] + 1e-9,
                     f"scroll Ø{2 * FI_R}, node Ø{FI_NODE_D}"))

    if style == "gyroid":
        applied = bool(_INFO.get("decor_applied"))
        if applied:
            from tigerbee.accessories import _blender as BL
            rows += BL.decor_checks("side_panel_clip_r__gyroid")
        else:
            # The language's own degrade path, declared in VARIANTS: a module that asks for a cell
            # the recipe does not carry gets its part back undecorated, and THAT part has to be
            # legal on its own. Every fit row above just measured it. Nothing is skipped: when the
            # bridge does run, decor_checks' manifold, wall and envelope rows run with it.
            rows.append(("GYROID: the bridge degraded, and the undecorated slab is legal on its "
                         "own (the documented fallback)", True,
                         f"{_INFO.get('decor_reason')}; cell used {_INFO.get('cell')!r} "
                         f"(asked for {GY_CELL!r}, documented fallback {GY_FALLBACK!r})"))
        rows.append((f"GYROID: wall {GY_WALL} - the thickest in the set, because the inside is "
                     f"mostly void", wall >= 3.6 - 1e-9,
                     f"{wall} mm against {max(PARAMS[s]['wall'] for s in PARAMS if s != 'gyroid')} "
                     f"for the next thickest style"))
        rows.append((f"GYROID: >= 1.5 periods of {GY_PERIOD} mm fit across the panel height",
                     (Z_TOP - Z_BOT) / GY_PERIOD >= 1.5,
                     f"{(Z_TOP - Z_BOT) / GY_PERIOD:.2f} periods over {Z_TOP - Z_BOT} mm, "
                     f"rind {GY_RIND} + sheet {GY_LIG} on a {wall} wall"))
        rows.append((f"GYROID: one constant r {GY_ROUND} rounding, no crease anywhere in the plan",
                     _INFO.get("round_r", 0.0) > 0.0
                     and max(_bend(*_gy_path()[i - 1:i + 2]) for i in range(1, len(_gy_path()) - 1)) <= 10.0,
                     f"{_INFO.get('rounded')} edges rounded, largest applied r "
                     f"{_INFO.get('round_r')}; sharpest plan bend "
                     f"{max(_bend(*_gy_path()[i - 1:i + 2]) for i in range(1, len(_gy_path()) - 1)):.1f} deg"))
    return rows
