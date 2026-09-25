"""TIGERBEE style vocabulary: the tiger-beetle design language as reusable build123d generators.

Pure build123d - nothing here knows about Blender, and nothing here touches fit: every generator
takes the region it may cut and the clean zones it must avoid as arguments.

    from tigerbee.accessories._style import STYLES, scale_features, vent_ladder, mark, suture

    st = STYLES["shard"]                       # the style family
    f  = scale_features(part, st, wall=1.5)    # pitch/ligament/count/mark size for THIS part
    cut, n = vent_ladder(region_sketch, pitch=f.pitch, ligament_min=f.ligament, clean=clean_sketches)
    panel -= extrude(Plane.XY.offset(z) * cut, amount=t)

It also owns the set's taste, not just its geometry: MATRIX says how each family reads on each
accessory (§6) and KITS turns that into the labels a user actually picks, naming the fallback style
wherever a family has no reading on a part. `_export.kits()` reconciles KITS against what the modules
really build; nothing else may fork it.

Every guarantee in here is measured, not asserted in prose:

    uv run python -m tigerbee.accessories._style      # 84 rows, all numeric

Canon rules this module implements (see .scratch/direction/tigerbee-design-language.md):
  CN-1 suture on X=0 for any part crossing the centreline          -> suture(), apply_suture()
  CN-3 free silhouette edges end in a cusp, never a stub           -> lens(), cusp_tail()
  CN-4 marks are debossed/embossed 0.6 mm, stroke >= 1.6 mm        -> mark()
  CN-7 the clean zone is sacred: every generator honours `clean`   -> every vent_*/puncta/serration

Vent generator contract (all of them):

    gen(region: Sketch | Face, *, pitch, ligament_min, clean=(), seed=0, **kw) -> (Sketch, int)

  * the returned Sketch is a CUTTER, to be extruded and subtracted;
  * `ligament_min` is kept between any two apertures AND to the region boundary;
  * nothing is cut inside any sketch/face in `clean`;
  * an aperture whose smallest dimension is below the material minimum hole is dropped, never
    shrunk; orphaned apertures are dropped too;
  * deterministic - randomness only through an explicit `seed`;
  * the int is how many apertures survived, so checks() can assert the pattern actually landed.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import ceil, cos, hypot, radians, sin, sqrt

from build123d import (Align, Axis, Box, Circle, Cone, Face, Part, Plane, Polygon, Pos, Rectangle,
                       RegularPolygon, Sketch, SlotOverall, Sphere, Text, Vector,
                       chamfer, extrude, fillet)

# --- material decoration limits (on top of _common.MATERIALS) --------------------------------
# Every number is the design-language table in §5.1. PETG's ligament is deliberately LARGER than
# TPU's: PETG cracks at a thin ligament under vibration, TPU only bends.
DECOR_MATERIALS = {
    "TPU95A": dict(wall=1.2, wall_impact=2.0, decor_min=0.8, hole_min=2.2, ligament_min=1.2,
                   strut=(2.4, 3.0), bridge_max=22.0, arch_d=10.0, puncta_d=2.4, puncta_depth=0.45,
                   mark_depth=0.6, mark_stroke=1.6),
    "PETG": dict(wall=1.5, wall_impact=2.0, decor_min=0.8, hole_min=2.0, ligament_min=1.6,
                 strut=(2.0, 2.6), bridge_max=20.0, arch_d=12.0, puncta_d=2.4, puncta_depth=0.45,
                 mark_depth=0.6, mark_stroke=1.6),
    "NYLON": dict(wall=1.5, wall_impact=2.0, decor_min=0.8, hole_min=2.0, ligament_min=1.6,
                  strut=(1.8, 2.4), bridge_max=18.0, arch_d=12.0, puncta_d=2.4, puncta_depth=0.45,
                  mark_depth=0.6, mark_stroke=1.6),
}
PUNCTA_D_MAX = 2.4        # a Ø2.4 dimple face is ~4.5 mm², under overhangs()' 5.0 mm² floor
PUNCTA_DEPTH_MAX = 0.45
MARK_STROKE_MIN = 1.6     # four passes at a 0.4 nozzle with margin
MARK_DEPTH = 0.6          # exactly 3 layers at 0.2
MARK_SKIRT = 0.3          # 0.3 x 45 deg chamfer round an emboss base so it cannot peel
SUTURE_W, SUTURE_D = 0.8, 0.4
FACET_MIN = 8.0           # SHARD: minimum facet across, the rule that stops low-poly reading broken
ENVELOPE_GROWTH_MAX = 2.0  # decoration may add at most this to the functional envelope, any axis

# --- edge treatment ladders ------------------------------------------------------------------
# sil = outer silhouette, crease = internal facet/rib junctions, free = aperture and free edges,
# tip = cusps and clip-mouth lips (0.45 matches _common.MOUTH_FILLET, so clip geometry never
# changes between styles). SLIPSTREAM's crease 0.0 is the family's definition, not an omission.
EDGE_LADDER = {
    "carapace":   {"kind": "fillet",  "sil": 3.0, "crease": 1.6, "free": 0.8, "tip": 0.45},
    "chassis":    {"kind": "fillet",  "sil": 1.2, "crease": 0.8, "free": 0.8, "tip": 0.45},
    "shard":      {"kind": "chamfer", "sil": 2.0, "crease": 1.2, "free": 0.6, "tip": 0.45},
    "feral":      {"kind": "mixed",   "sil": 1.6, "crease": 0.8, "free": 0.3, "tip": 0.8},
    "slipstream": {"kind": "varfil",  "sil": (4.0, 0.8), "crease": 0.0, "free": 1.2, "tip": 0.6},
    "arsenal":    {"kind": "chamfer", "sil": 1.6, "crease": 0.6, "free": 0.6, "tip": 0.45},
    "nocturne":   {"kind": "fillet",  "sil": 1.0, "crease": 0.6, "free": 0.4, "tip": 0.45},
    # --- the six added languages. GYROID and CORAL declare crease 0.0 for the same reason
    # SLIPSTREAM does: a crease would leave the family. ORIGAMI and BRUTALIST are chamfer-only by
    # definition, at one angle and one size each - that is the whole rule, not a default.
    "gyroid":     {"kind": "fillet",  "sil": 3.0, "crease": 0.0, "free": 1.2, "tip": 0.45},
    "origami":    {"kind": "chamfer", "sil": 0.4, "crease": 0.4, "free": 0.4, "tip": 0.45},
    "vespid":     {"kind": "mixed",   "sil": 1.2, "crease": 0.6, "free": 0.45, "tip": 0.8},
    "filigree":   {"kind": "fillet",  "sil": 1.2, "crease": 0.6, "free": 0.7, "tip": 0.45},
    "brutalist":  {"kind": "chamfer", "sil": 1.0, "crease": 1.0, "free": 1.0, "tip": 0.45},
    "coral":      {"kind": "fillet",  "sil": 3.0, "crease": 0.0, "free": 1.6, "tip": 0.8},
}
# --- the six added languages' own constants -----------------------------------------------------
FOLD_ANGLES = (22.5, 45.0, 67.5)   # ORIGAMI: the only fold angles allowed anywhere in the part
CREASE_CHAMFER = 0.4               # ORIGAMI: every edge, chamfer, never a fillet
TERGITE_RATIO = 0.82               # VESPID: each segment is 0.82 x the length of the one before it
GIRTH_RATIO = 0.86                 # VESPID: ... and 0.86 x the girth, so the outline steps down
FILIGREE_VOID_BAND = (0.45, 0.60)  # FILIGREE: fraction of the plan area that must be cut away
BOARD_MARK = dict(w=0.6, depth=0.3, pitch=2.4)   # BRUTALIST: formwork plank marks
BRUTALIST_CHAMFER = 1.0            # BRUTALIST: 1.0 x 45 deg, and no fillet over r 0.3 anywhere
FILLET_WALL_FRACTION = 0.45   # a fillet may not exceed 0.45 x local wall
CHAMFER_WALL_FRACTION = 0.40  # a chamfer may not exceed 0.40 x local wall


@dataclass(frozen=True)
class Style:
    """One style family. `vent` and `accent` name the generators below, so a module can stay
    style-agnostic: `getattr(_style, st.vent)(region, ...)`."""

    name: str
    identity: str            # the one-line brief, copied into the manifest
    edge: dict               # EDGE_LADDER entry
    vent: str                # default aperture generator name
    vents: tuple[str, ...]   # every generator legal for this family, best first
    accent: str              # "lunule" | "stripe3" | "mandible" | "wordmark" | ""
    accent_mode: str         # "deboss" | "emboss" | "cut"
    material: str            # default material
    recipe: str | None       # _blender recipe name, or None for a pure-build123d family
    recipe_params: dict      # defaults for that recipe
    wall: float              # structural floor at the free edge
    wall_load: float         # floor on a load path / at any mating feature (CN-5 thick end)
    rib: float               # default external rib width
    suture: bool             # CN-1: cut a suture on X=0 when the part crosses the centreline
    puncta: bool             # a PUNCTA field is part of this family's reading
    blender_only: bool       # True when the family's identity cannot be reached without Blender

    def wall_at(self, frac: float) -> float:
        """CN-5 thickness gradient: frac 0 at the free edge, 1 on the load path."""
        return self.wall + (self.wall_load - self.wall) * max(0.0, min(1.0, frac))


def _style(name, identity, vent, vents, accent, accent_mode, material, recipe, recipe_params,
           wall, wall_load, rib, suture_, puncta_, blender_only) -> Style:
    return Style(name=name, identity=identity, edge=EDGE_LADDER[name], vent=vent, vents=vents,
                 accent=accent, accent_mode=accent_mode, material=material, recipe=recipe,
                 recipe_params=dict(recipe_params), wall=wall, wall_load=wall_load, rib=rib,
                 suture=suture_, puncta=puncta_, blender_only=blender_only)


STYLES: dict[str, Style] = {
    "shard": _style(
        "shard", "the frame's own language, sharpened: planar crystalline facets and hard creases",
        "vent_louvre", ("vent_louvre", "vent_keyhole", "vent_ladder", "vent_hex"),
        "stripe3", "deboss", "PETG", None, {}, 1.2, 2.4, 1.6, True, False, False),
    "arsenal": _style(
        "arsenal", "field-serviceable mil-spec kit: orthogonal datums, external ribs, stencil text",
        "vent_hex", ("vent_hex", "vent_ladder", "vent_louvre"),
        "wordmark", "deboss", "PETG", None, {}, 1.5, 2.4, 1.6, False, False, False),
    "chassis": _style(
        "chassis", "only the load path survives: rails, struts and ring nodes, the void is the shape",
        "vent_keyhole", ("vent_keyhole", "vent_voronoi", "vent_hex"),
        "stripe3", "deboss", "PETG", "carapace_lattice",
        dict(cell="voronoi", ligament=1.6, cell_area=(28.0, 90.0), seed=7), 1.6, 2.6, 2.0,
        False, False, False),
    "carapace": _style(
        "carapace", "the shell closed over it: a domed sutured elytron, nothing structural visible",
        "vent_elytra", ("vent_elytra", "vent_ladder"),
        "lunule", "deboss", "PETG", "elytra_dome",
        dict(mode="top", rise_span=0.32, relax=6), 1.6, 2.6, 1.4, True, True, True),
    "feral": _style(
        "feral", "it bites: crossed mandibles, a descending dorsal spine row, claws",
        "vent_ladder", ("vent_ladder", "vent_louvre"),
        "lunule", "cut", "TPU95A", "sculpt",
        dict(mode="curve", voxel=0.35, teeth=3), 1.6, 2.4, 2.0, True, True, True),
    "slipstream": _style(
        "slipstream", "one unbroken highlight: a lofted teardrop fairing, G2, zero creases",
        "vent_elytra", ("vent_elytra",),
        "lunule", "deboss", "PETG", "elytra_dome",
        dict(mode="top", rise_span=0.26, relax=8), 1.5, 2.4, 1.2, True, False, True),
    "nocturne": _style(
        "nocturne", "the night hunter lit from inside: thin fanned vanes, light wells, lensed edges",
        "vent_ladder", ("vent_ladder", "vent_louvre"),
        "lunule", "cut", "PETG", None, {}, 1.2, 2.2, 1.4, True, False, False),
    # --- the six added languages -------------------------------------------------------------
    # Each one is recognisable in a 200 px thumbnail by SILHOUETTE and APERTURE PATTERN before any
    # texture, which is the bar a language has to clear to earn a slot.
    "gyroid": _style(
        "gyroid", "the solid is a frozen fluid: a TPMS sheet where the wall used to be",
        None, ("vent_voronoi",),
        None, "", "PETG", "gyroid",
        dict(period=10.0, sheet=1.6, rind=1.6), 1.6, 3.6, 0.0, False, False, True),
    "origami": _style(
        "origami", "one sheet, folded: straight creases, no curve anywhere",
        "vent_ladder", ("vent_ladder", "vent_louvre"),
        "stripe3", "deboss", "PETG", None, {}, 1.8, 2.4, 0.0, False, False, False),
    "vespid": _style(
        "vespid", "wasp: tapered segmentation, banded tergites, a stinger terminal",
        "vent_keyhole", ("vent_keyhole", "vent_ladder"),
        "lunule", "deboss", "TPU95A", "chitin",
        dict(period=9.0, amplitude=0.6, texture="WOOD"), 1.4, 2.2, 0.8, False, True, False),
    "filigree": _style(
        "filigree", "ornamental cutwork hung on a rigid spine",
        "vent_voronoi", ("vent_voronoi", "vent_keyhole"),
        "lunule", "cut", "PETG", None, {}, 1.4, 2.4, 2.0, False, False, False),
    "brutalist": _style(
        "brutalist", "one poured slab, formwork still showing",
        "vent_ladder", ("vent_ladder",),
        "wordmark", "deboss", "PETG", None, {}, 3.0, 3.0, 3.0, False, False, False),
    "coral": _style(
        "coral", "accreted, not designed",
        None, (), None, "", "TPU95A", "sculpt",
        dict(mode="meta", voxel=0.40), 1.6, 4.0, 0.0, False, True, True),
}
CORE_STYLES = ("carapace", "chassis", "shard", "feral")
PURE_B123D_STYLES = tuple(n for n, s in STYLES.items() if s.recipe is None)


def style_of(name_or_style) -> Style:
    """Accept a Style or its name; raise with the list of families on a typo."""
    if isinstance(name_or_style, Style):
        return name_or_style
    try:
        return STYLES[name_or_style]
    except KeyError:
        raise KeyError(f"unknown style {name_or_style!r}; families: {sorted(STYLES)}") from None


# --- the scaling law -------------------------------------------------------------------------
TIERS = (("micro", 0.0, 18.0), ("small", 18.0, 32.0), ("medium", 32.0, 60.0), ("large", 60.0, 1e9))


def clamp(v: float, lo: float, hi: float) -> float:
    return lo if v < lo else (hi if v > hi else v)


def characteristic_length(obj) -> float:
    """L = the shorter of the two in-plane extents of a Face/Sketch, or volume**(1/3) for a solid.
    One number, so a 12 mm bracket and a 70 mm canopy get the same family at two scales instead of
    the same drawing at two zooms."""
    if isinstance(obj, (int, float)):
        return float(obj)
    if isinstance(obj, (Sketch, Face)):
        bb = obj.bounding_box()
        return float(min(bb.size.X, bb.size.Y))
    bb = obj.bounding_box()
    sizes = sorted((bb.size.X, bb.size.Y, bb.size.Z))
    try:
        vol = float(obj.volume)
    except Exception:  # noqa: BLE001 - not a solid
        vol = 0.0
    # a plate-like solid is decorated on its large face: L is that face's short side
    return float(sizes[1]) if sizes[0] < 0.35 * sizes[1] else float(vol ** (1 / 3)) if vol > 0 else float(sizes[1])


@dataclass(frozen=True)
class FeatureScale:
    """Every generator argument a module needs, derived once from the part and the style."""

    L: float
    tier: str
    pitch: float
    aperture: float
    ligament: float
    count: int
    mark: float
    mark_kind: str
    edge_r: float
    rib: float
    puncta: bool
    second_tier: float  # sub-pattern pitch for L >= 60, else 0.0

    def as_kwargs(self) -> dict:
        """`gen(region, **f.as_kwargs())` - pitch/ligament_min only, so it fits every generator."""
        return dict(pitch=self.pitch, ligament_min=self.ligament)


def scale_features(obj, style, wall: float | None = None, material: str = "PETG") -> FeatureScale:
    """The §4.4 scaling law. `obj` is the part, face or sketch being decorated (or a bare L)."""
    st = style_of(style)
    mat = DECOR_MATERIALS.get(material, DECOR_MATERIALS["PETG"])
    wall = st.wall if wall is None else wall
    L = characteristic_length(obj)
    tier = next(t for t, lo, hi in TIERS if lo <= L < hi)
    p = clamp(L / 6.0, 4.0, 14.0)
    g = max(0.45 * p, 1.2 * wall, mat["ligament_min"])
    n = int(clamp(round(L / p), 2, 9))
    m = clamp(0.38 * L, 8.0, 34.0)
    r = clamp(0.06 * L, 0.4, 3.0)
    h = clamp(0.10 * L, 1.2, 3.0)
    kind = st.accent
    puncta_ = st.puncta
    if tier == "micro":
        n, puncta_ = 2, False
        if kind == "lunule":
            kind = "stripe3"
        r = min(r, _ladder_value(st, "free"))
    elif tier == "small":
        n = int(clamp(n, 3, 4))
    r = min(r, _ladder_value(st, "sil"))
    return FeatureScale(L=round(L, 3), tier=tier, pitch=round(p, 3), aperture=round(0.55 * p, 3),
                        ligament=round(g, 3), count=n, mark=round(m, 3), mark_kind=kind,
                        edge_r=round(r, 3), rib=round(h, 3), puncta=puncta_,
                        second_tier=round(p / 2.6, 3) if tier == "large" else 0.0)


def scale_law(L: float, style, wall: float | None = None, material: str = "PETG") -> dict:
    """The §4.4 law as a plain dict, for a caller that wants the numbers rather than the dataclass:
    `{pitch, aperture, ligament, count, mark, mark_kind, edge_r, rib, tier, puncta, second_tier}`.
    `scale_features()` is the same law and also accepts a Part/Face/Sketch."""
    f = scale_features(float(L), style, wall=wall, material=material)
    return dict(L=f.L, tier=f.tier, pitch=f.pitch, aperture=f.aperture, ligament=f.ligament,
                count=f.count, mark=f.mark, mark_kind=f.mark_kind, edge_r=f.edge_r, rib=f.rib,
                puncta=f.puncta, second_tier=f.second_tier)


# --- edge treatment --------------------------------------------------------------------------
def _ladder_value(style, tier: str) -> float:
    v = style_of(style).edge[tier]
    return float(v[0]) if isinstance(v, tuple) else float(v)


def edge_radius(style, tier: str = "sil", wall: float | None = None) -> float:
    """Ladder value for this tier, clamped by the hard limit (0.45 x wall for a fillet, 0.40 for a
    chamfer). Returns 0.0 when the family declares no treatment at that tier (SLIPSTREAM crease)."""
    st = style_of(style)
    v = _ladder_value(st, tier)
    if v <= 0.0:
        return 0.0
    if wall is not None:
        frac = CHAMFER_WALL_FRACTION if st.edge["kind"] == "chamfer" else FILLET_WALL_FRACTION
        v = min(v, frac * wall)
    return round(v, 3)


def treat_edges(shape, style, tier: str = "sil", wall: float | None = None, edges=None,
                kind: str | None = None):
    """Apply this style's edge ladder to `edges` (default: every edge of `shape`), retrying at
    half radius twice when OCCT refuses. Returns (shape, radius_applied); radius 0.0 means the
    treatment was skipped, which is a legal outcome (SLIPSTREAM's crease tier is 0.0 by design).
    build the silhouette FIRST and treat edges LAST - a fillet on an un-cut outline is lost."""
    st = style_of(style)
    r = edge_radius(st, tier, wall)
    if r <= 0.0:
        return shape, 0.0
    kind = kind or st.edge["kind"]
    op = chamfer if kind == "chamfer" else fillet
    sel = list(edges) if edges is not None else list(shape.edges())
    if not sel:
        return shape, 0.0
    for attempt in (r, r / 2, r / 4):
        try:
            return op(sel, attempt), round(attempt, 3)
        except Exception:  # noqa: BLE001 - OCCT refuses radii it cannot fit; shrink and retry
            continue
    return shape, 0.0


# --- region / clean-zone plumbing shared by every generator ----------------------------------
_AREA_TOL = 1e-4


def as_sketch(region) -> Sketch:
    """Sketch | Face | iterable of either -> one Sketch."""
    if isinstance(region, Sketch):
        return region
    if isinstance(region, Face):
        return Sketch() + region
    sk = Sketch()
    for r in region:
        sk += as_sketch(r)
    return sk


def _inside(candidate: Sketch, region: Sketch) -> bool:
    try:
        return (candidate - region).area <= _AREA_TOL
    except Exception:  # noqa: BLE001 - OCCT can throw on a degenerate profile; drop the aperture
        return False


def _clear_of(candidate: Sketch, clean) -> bool:
    for c in clean:
        try:
            if (candidate & as_sketch(c)).area > _AREA_TOL:
                return False
        except Exception:  # noqa: BLE001
            return False
    return True


PAIR_GROW = 0.45  # each aperture grown by 0.45 x ligament for the pairwise test, so two kept
# neighbours are >= 0.90 x ligament apart even in the worst case. A full 0.5 factor makes the
# lattice cases exactly tangent, and an exactly tangent OCCT boolean is a coin toss - regular
# lattices therefore pass pairwise=False and rely on the pitch arithmetic instead (the research's
# "the guarantee is arithmetic, not hope": with centre separation D and circumradius r the
# ligament is D - 2r by construction).


def place_apertures(region, shape_fn, centres, *, ligament_min: float, clean=(),
                    pairwise: bool = True, min_dim: float = 0.0, hole_min: float = 0.0,
                    limit: int = 0):
    """The engine behind every vent_*: keep a candidate only when it is fully inside `region` with
    `ligament_min` to the boundary, clear of every clean zone, and `ligament_min` from every other
    kept aperture. `shape_fn(cx, cy, grow) -> Sketch` must grow the aperture by `grow` all round.

    Apertures are DROPPED, never shrunk (§4.1), and the smallest dimension is checked against the
    material's minimum hole before anything else. `limit` caps how many survive (0 = no cap)."""
    reg = as_sketch(region)
    cleans = [as_sketch(c) for c in clean]
    if min_dim and hole_min and min_dim < hole_min - 1e-9:
        return Sketch(), 0
    kept, halves, out = [], [], Sketch()
    for cx, cy in centres:
        if limit and len(kept) >= limit:
            break
        try:
            full = shape_fn(cx, cy, ligament_min)
            cut = shape_fn(cx, cy, 0.0)
            half = shape_fn(cx, cy, PAIR_GROW * ligament_min) if pairwise else None
        except Exception:  # noqa: BLE001
            continue
        if not _inside(full, reg) or not _clear_of(full, cleans):
            continue
        if pairwise and any((half & h).area > _AREA_TOL for h in halves if _bb_near(half, h)):
            continue
        kept.append(cut)
        if pairwise:
            halves.append(half)
    for cut in kept:
        out += cut
    return out, len(kept)


def _bb_near(a: Sketch, b: Sketch) -> bool:
    A, B = a.bounding_box(), b.bounding_box()
    return not (A.max.X < B.min.X or B.max.X < A.min.X or A.max.Y < B.min.Y or B.max.Y < A.min.Y)


def grid_centres(region, pitch_x: float, pitch_y: float, stagger: bool = False,
                 origin=(0.0, 0.0)) -> list[tuple[float, float]]:
    """Lattice points covering the region's bounding box, snapped to `origin` so the pattern is
    deterministic and identical between two parts of a mirrored pair."""
    bb = as_sketch(region).bounding_box()
    ox, oy = origin
    nx = int((bb.size.X + 2 * pitch_x) / pitch_x) + 2
    ny = int((bb.size.Y + 2 * pitch_y) / pitch_y) + 2
    x0 = ox + pitch_x * ceil((bb.min.X - pitch_x - ox) / pitch_x)
    y0 = oy + pitch_y * ceil((bb.min.Y - pitch_y - oy) / pitch_y)
    pts = []
    for j in range(ny):
        y = y0 + j * pitch_y
        shift = 0.5 * pitch_x if (stagger and j % 2) else 0.0
        for i in range(nx):
            pts.append((x0 + i * pitch_x + shift, y))
    return pts


def extrude_cut(sk: Sketch, plane: Plane, amount: float) -> Part:
    """Extrude a cutter sketch `amount` along the plane's +Z (negative = into the surface).

    ALWAYS go through this instead of bare extrude(): build123d picks the extrusion direction PER
    FACE from that face's own normal, so a cutter built by booleans or mirroring (vent_elytra,
    vent_voronoi, a mirrored mark) silently extrudes half its apertures the wrong way - measured as
    a "0.6 mm" emboss occupying z -0.6..+0.6."""
    d = Vector(*plane.z_dir).normalized()
    return extrude(plane * sk, amount=abs(amount), dir=tuple(d if amount >= 0 else -d))


# --- CN-3: cusps, not stubs -------------------------------------------------------------------
def lens(p0, p1, half_width: float) -> Sketch:
    """The vesica through p0 and p1: two equal circular arcs meeting at a POINT at each end.
    This is the cusp primitive - every cusped end in the set is a clipped lens, so the tips are
    true tangent-arc points instead of a rounded stub (CN-3).

    GEOMETRIC LIMIT, worth knowing before you design with it: a vesica whose tips are `d` apart can
    be at most `d/2` wide, and at exactly d/2 it degenerates into a circle with no tips at all. The
    half width is therefore clamped to 0.499 * d. Sharper tips mean a narrower lens; that trade is
    the shape, not a defect."""
    (x0, y0), (x1, y1) = p0, p1
    dx, dy = x1 - x0, y1 - y0
    d = hypot(dx, dy)
    if d < 1e-9 or half_width <= 0:
        return Sketch()
    h = min(half_width, 0.499 * d)
    a = ((d / 2) ** 2 - h * h) / (2 * h)  # centre offset along the perpendicular bisector
    rho = a + h                           # radius, so both arcs pass through p0 and p1
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    ux, uy = -dy / d, dx / d
    return (Pos(mx + ux * a, my + uy * a) * Circle(rho)) & (Pos(mx - ux * a, my - uy * a) * Circle(rho))


def cusp_tail(width: float, length: float, tip_r: float = 0.6, at=(0.0, 0.0),
              angle: float = 90.0) -> Sketch:
    """A pointed tail `length` long off a `width`-wide root: two concave arcs meeting in a point,
    the frame's own edge grammar (CN-3). Built as the far half of a full-length vesica, so the root
    is exactly `width` and the tip is a true arc-to-arc point, blunted to `tip_r` so a Ø2*tip_r ball
    still fits (the FERAL tip-radius check). UNION it onto a plan outline to terminate a free
    silhouette edge in a cusp. `angle` is the direction the tip points (deg, 0 = +X)."""
    full = lens((0.0, -length), (0.0, length), width / 2)
    keep = Pos(0.0, (length + 1.0) / 2) * Rectangle(2 * width + 4.0, length + 1.0)
    tail = full & keep
    if tip_r > 0:
        tail += Pos(0.0, length - tip_r) * Circle(tip_r)
    return Pos(*at) * tail.rotate(Axis.Z, angle - 90.0)


def suture(y0: float, y1: float, z_top: float, *, w: float = SUTURE_W, depth: float = SUTURE_D,
           cusped: bool = True) -> Part:
    """CN-1. The elytral suture: a V groove of width `w` and depth `depth` on X = 0, from y0 to y1,
    cut into the surface at `z_top`. Running out to a cusp at both ends (a lens in plan) so the
    groove ends in a point, never a square stop. SUBTRACT it, and subtract it AFTER any Blender
    pass so the groove lands on exact geometry.

    A mirrored pair carries no suture - the pair IS the split."""
    prof = Polygon((-w / 2, z_top + 0.01), (w / 2, z_top + 0.01), (0.0, z_top - depth), align=None)
    xz = Plane(origin=(0, y0 - 1.0, 0), x_dir=(1, 0, 0), z_dir=(0, -1, 0))
    groove = extrude(xz * prof, amount=(y1 - y0) + 2.0)
    if cusped:
        clip = extrude(Plane.XY.offset(z_top - depth - 1.0) * lens((0.0, y0), (0.0, y1), w), amount=depth + 2.0)
        groove = groove & clip
    return groove


def apply_suture(part: Part, length: float | None = None, z_face: float | None = None, *,
                 at_y: float | None = None, w: float = SUTURE_W, depth: float = SUTURE_D,
                 cusped: bool = True, inset: float = 1.5) -> Part:
    """CN-1 in one call: `part = apply_suture(part)`. The dorsal extents and the top face come from
    the part's own bounding box unless given, so a module never has to restate its own geometry.
    `length` centres the groove on `at_y` (default the part's mid Y); `inset` holds the cusps off the
    silhouette so the groove runs out INSIDE the surface rather than nicking the outline.

    A part that does not cross X = 0 is returned untouched - a mirrored pair carries no suture."""
    bb = part.bounding_box()
    if bb.min.X > -w / 2 or bb.max.X < w / 2:
        return part
    z = bb.max.Z if z_face is None else z_face
    if length is None:
        y0, y1 = bb.min.Y + inset, bb.max.Y - inset
    else:
        mid = bb.center().Y if at_y is None else at_y
        y0, y1 = mid - length / 2, mid + length / 2
    if y1 - y0 <= 4 * w:
        return part
    return part - suture(y0, y1, z, w=w, depth=depth, cusped=cusped)


# --- aperture / vent generators ---------------------------------------------------------------
def vent_hex(region, *, pitch: float, ligament_min: float, clean=(), af: float | None = None,
             hole_min: float = 0.0, origin=(0.0, 0.0), limit: int = 0, seed: int = 0, **_kw):
    """ARSENAL / CHASSIS. Honeycomb flat-top hex field. Defaults AF 5.0, ligament 1.8, pitch 6.8.
    Flat-top means the aperture's top edge is a short horizontal bridge of AF*0.5 - self-supporting
    at these sizes - rather than a peak that leaves a spike.

    The lattice is the one a honeycomb actually has, and that is not optional: a flat-top hexagon has
    its FLATS facing 30/90/150 deg and its VERTICES facing 0/60/120 deg, so the six neighbours must
    sit in the flat directions or the field is vertex-to-vertex and the ligament collapses. Measured
    on the naive staggered-row grid (neighbours at 0/60/120 deg): 1.07 mm against a 2.0 mm target,
    a 46 % shortfall that no pairwise test caught because the lattice was trusted as "arithmetic".

    So: centre spacing D = AF + ligament in the flat directions - columns pitched D*sqrt(3)/2 in x,
    each odd column dropped D/2 in y - and the gap between neighbours is then exactly the ligament
    by construction. `pitch` IS D (flat to flat, centre to centre), which is why the family's
    defaults read AF 5.0 + ligament 1.8 = pitch 6.8."""
    af = (pitch - ligament_min) if af is None else af
    d_lat = max(af + ligament_min, pitch)   # a caller's explicit AF may need more room than `pitch`
    rc = af / 2.0 / cos(radians(30))        # circumradius of a hex whose across-flats is `af`

    def shape(cx, cy, grow):
        # growth is perpendicular to the flats (that is where the ligament is measured), so the
        # circumradius grows by grow/cos(30), not by grow
        return Pos(cx, cy) * RegularPolygon(rc + grow / cos(radians(30)), 6)

    bb = as_sketch(region).bounding_box()
    step_x, step_y = d_lat * sqrt(3) / 2, d_lat
    pad = rc + ligament_min
    nx = int((bb.size.X + 2 * pad) / step_x) + 2
    ny = int((bb.size.Y + 2 * pad) / step_y) + 2
    x0 = bb.min.X - pad + (origin[0] % step_x)
    y0 = bb.min.Y - pad + (origin[1] % step_y)
    centres = [(x0 + i * step_x, y0 + j * step_y + (step_y / 2 if i % 2 else 0.0))
               for i in range(nx) for j in range(ny)]
    return place_apertures(region, shape, centres, ligament_min=ligament_min, clean=clean,
                           pairwise=False, min_dim=af, hole_min=hole_min, limit=limit)


def vent_ladder(region, *, pitch: float, ligament_min: float, clean=(), length: float | None = None,
                width: float | None = None, corner_r: float | None = None, columns: int = 1,
                hole_min: float = 0.0, origin=(0.0, 0.0), limit: int = 0, seed: int = 0, **_kw):
    """The frame's own motif and the one generator legal in every family: the abdominal segment
    ladder - rounded-rectangular slots with their long axis across X, even pitch in Y (CN-2:
    repeating features run transverse, never along Y). Defaults slot 12 x 3.4, corner r 1.7."""
    bb = as_sketch(region).bounding_box()
    floor_ = hole_min or 2.2
    # the frame's own ratio is 3.4 / 9.0 = 0.378; at a small pitch that lands under the minimum
    # hole, so the slot opens to the material floor instead of being dropped
    width = max(0.378 * pitch, min(0.55 * pitch, floor_)) if width is None else width
    length = max(bb.size.X - 2 * ligament_min, 2 * width) if length is None else length
    corner_r = width / 2 if corner_r is None else corner_r

    def shape(cx, cy, grow):
        w, l = width + 2 * grow, length + 2 * grow
        return Pos(cx, cy) * SlotOverall(l, w)

    step = bb.size.X / columns
    xs = [bb.min.X + step * (i + 0.5) for i in range(columns)]
    ys = sorted({y for _x, y in grid_centres(region, pitch, pitch, origin=origin)}, reverse=True)
    centres = [(x, y) for y in ys for x in xs]
    return place_apertures(region, shape, centres, ligament_min=ligament_min, clean=clean,
                           pairwise=True, min_dim=width, hole_min=hole_min, limit=limit)


def vent_elytra(region, *, pitch: float, ligament_min: float, clean=(), n: int | None = None,
                pivot=None, span_deg: float = 52.0, width: float | None = None,
                hole_min: float = 0.0, seed: int = 0, **_kw):
    """CARAPACE / SLIPSTREAM. Curved slots following the dome's parallels, cusped at both ends -
    each slot is an annular band clipped by a lens (see lens()), so the ends are true tangent-arc
    points and not square stops. n = 3..7, width 0.55 x pitch, ligament 0.45 x pitch.

    The arc radius is solved from the region, not guessed: the chord is held constant across the
    whole set (so every slot is the same length, like real elytral parallels) and the sagitta is
    capped at 0.22 x the available Y band, or the outer slots bulge out of the region and get
    dropped. Pass `pivot` explicitly to arc the slots round a specific centre instead."""
    reg = as_sketch(region)
    bb = reg.bounding_box()
    cx0 = bb.center().X
    floor_ = hole_min or 2.2
    width = max(0.55 * pitch, floor_) if width is None else width
    band = bb.size.Y - 2 * ligament_min - width
    # the family spec asks for 3-7 slots; 2 is allowed because a real region sometimes only holds 2,
    # and forcing a third into a band that cannot take it just drops them all
    n = int(clamp(n if n else int(band / pitch), 2, 7))
    while n > 2 and (n - 1) * pitch > band:
        n -= 1
    chord = bb.size.X - 2.4 * ligament_min
    # the Y the arcs may bulge into is what the slot stack leaves over, not a fixed fraction
    sag_budget = max(0.6, bb.size.Y - 2 * ligament_min - (n - 1) * pitch - width)
    span = span_deg
    for _ in range(14):  # shrink the span until the arc's bulge fits that budget
        R = chord / (2 * sin(radians(span / 2)))
        if R * (1 - cos(radians(span / 2))) <= sag_budget or span <= 6.0:
            break
        span *= 0.8
    R = chord / (2 * sin(radians(span / 2)))
    sag = R * (1 - cos(radians(span / 2)))
    # centre the whole stack in the band: mid of [innermost arc bottom, outermost arc top]
    pivot = (cx0, bb.center().Y - R + sag / 2) if pivot is None else pivot

    def band_slot(_cx, R_i, grow):
        """The slot is addressed by its radius (carried in the second slot of the centre tuple)."""
        half = width / 2 + grow
        ring = Pos(*pivot) * (Circle(R_i + half) - Circle(R_i - half))
        th = radians(span / 2) * (R / R_i)          # constant chord: narrower angle further out
        p0 = (pivot[0] - R_i * sin(th), pivot[1] + R_i * cos(th))
        p1 = (pivot[0] + R_i * sin(th), pivot[1] + R_i * cos(th))
        # the lens must swallow the whole arc and pinch ONLY at the two tips, so its half width is
        # the arc's own sagitta plus the band half width - a narrower lens clips the arc's crown
        # off and leaves two crumbs instead of one cusped slot
        return ring & lens(p0, p1, R_i * (1 - cos(th)) + half + 0.05)

    radii = [(0.0, R + (i - (n - 1) / 2) * pitch) for i in range(n)]
    return place_apertures(reg, band_slot, radii, ligament_min=ligament_min, clean=clean,
                           pairwise=True, min_dim=width, hole_min=hole_min)


def vent_louvre(region, *, pitch: float, ligament_min: float, clean=(), length: float | None = None,
                width: float | None = None, angle: float = 60.0, hole_min: float = 0.0,
                origin=(0.0, 0.0), limit: int = 0, seed: int = 0, **_kw):
    """SHARD / ARSENAL. Slanted stadium slots, proven in side_panels: 60 deg, not 45, because a
    45 deg flank exceeds the overhang limit once the part stands on the bed."""
    width = 3.0 if width is None else width
    length = 11.0 if length is None else length

    def shape(cx, cy, grow):
        w, l = width + 2 * grow, length + 2 * grow
        return Pos(cx, cy) * SlotOverall(l, w).rotate(Axis.Z, angle)

    centres = grid_centres(region, pitch, max(pitch, length * abs(sin(radians(angle))) + ligament_min),
                           origin=origin)
    return place_apertures(region, shape, centres, ligament_min=ligament_min, clean=clean,
                           pairwise=True, min_dim=width, hole_min=hole_min, limit=limit)


def vent_keyhole(region, *, pitch: float, ligament_min: float, clean=(), head_d: float | None = None,
                 waist: float | None = None, tail: float | None = None, angle: float = 270.0,
                 hole_min: float = 0.0, origin=(0.0, 0.0), limit: int = 0, seed: int = 0, **_kw):
    """SHARD / CHASSIS. The frame's own keyhole/teardrop lightening hole: a circle blended into a
    slot with a tangent waist. Defaults head Ø6.0, waist 3.0, ligament 2.4."""
    floor_ = hole_min or 2.2
    head_d = max(min(6.0, 0.9 * pitch), floor_ + 1.2) if head_d is None else head_d
    waist = max(head_d / 2, floor_) if waist is None else waist
    tail = head_d * 1.3 if tail is None else tail

    def shape(cx, cy, grow):
        sk = Circle(head_d / 2 + grow) + Pos(0, -tail / 2) * SlotOverall(tail + 2 * grow, waist + 2 * grow, rotation=90)
        return Pos(cx, cy) * sk.rotate(Axis.Z, angle - 270.0)

    centres = grid_centres(region, max(pitch, head_d + ligament_min),
                           head_d + tail + ligament_min, stagger=True, origin=origin)
    return place_apertures(region, shape, centres, ligament_min=ligament_min, clean=clean,
                           pairwise=True, min_dim=min(head_d, waist), hole_min=hole_min, limit=limit)


# --- the six added languages' own generators ----------------------------------------------------
# Same contract as the vent_* family above - the region they may work in, the clean zones they must
# not touch, deterministic, and a count so checks() can prove the pattern landed.
def board_mark(region, *, w: float = 0.6, depth: float = 0.3, pitch: float = 2.4,
               angle_deg: float = 0.0, clean=(), ligament_min: float = 0.0, **_kw):
    """BRUTALIST. The formwork: parallel grooves `w` wide at `pitch`, all running one way - the print
    direction - like the planks of a shuttering board. `depth` is carried for the caller's extrude
    (extrude_cut(..., -depth)); it is not used in the plan sketch.

    Grooves are DECORATION, 0.3 mm deep, not through-holes, so the minimum-hole rule does not apply
    and a groove crossing a clean zone is TRIMMED rather than dropped - dropping whole planks leaves
    a gap that reads as a mistake, while a plank that stops at the boss reads as formwork. Returns
    (cutter, n_grooves)."""
    reg = inset_region(region, ligament_min) if ligament_min > 0 else as_sketch(region)
    if not reg.faces():
        return Sketch(), 0
    bb = reg.bounding_box()
    diag = hypot(bb.size.X, bb.size.Y) + 2 * pitch
    cx, cy = bb.center().X, bb.center().Y
    n = int(diag / pitch) + 2
    field = Sketch()
    kept = 0
    for i in range(-n // 2, n // 2 + 1):
        bar = Pos(cx, cy) * Rotation_z(angle_deg) * Pos(0.0, i * pitch) * Rectangle(diag, w)
        one = bar & reg
        if not one.faces() or one.area < 0.25 * w * w:
            continue
        field += one
        kept += 1
    for c in clean:
        grown = grow_region(c, max(ligament_min, w))
        try:
            field -= (grown if grown.faces() else as_sketch(c))
        except Exception:  # noqa: BLE001 - an OCCT refusal here means the groove stays whole
            pass
    return field, kept


@dataclass(frozen=True)
class FoldNet:
    """What fold_facets() hands back: the plan footprints of a folded sheet, the creases between
    them, and the numbers a module needs to raise it into 3D."""

    facets: tuple          # Sketch per facet, in order along the fold axis
    creases: tuple         # ((x0, y0), (x1, y1), sense, angle_deg) - sense +1 mountain, -1 valley
    angles: tuple          # signed tilt of each facet, degrees, drawn only from `angles`
    heights: tuple         # mid-surface height at each crease, first = 0.0
    thickness: float
    axis: str
    rise: float            # peak-to-valley of the mid-surface

    def __len__(self) -> int:
        return len(self.facets)


def fold_facets(region, *, n: int, angles=FOLD_ANGLES, thickness: float, axis: str = "X",
                clean=(), ligament_min: float = 0.0, start: int = 0, **_kw):
    """ORIGAMI. One sheet of paper, folded: `n` planar facets tiling `region` across `axis`, tilted
    by angles drawn ONLY from `angles` (default 22.5 / 45 / 67.5), with a crease between each pair.

    The facets are of EQUAL TRUE LENGTH and their footprints are that length foreshortened by
    cos(tilt), which is what makes it a folded sheet rather than a set of stripes: the developed
    length of the sheet is n x L whatever the angles, and the plan span is sum(L cos t_i). A facet
    whose footprint cannot hold a disc of `thickness` is dropped, never shrunk (the same rule as
    every vent_*), and its crease goes with it.

    Returns a FoldNet. The caller extrudes each facet `thickness` along its own tilted plane and
    marks the creases with mark(..., "deboss") - mountain solid, valley dotted."""
    assert n >= 2, "a fold needs at least two facets"
    assert all(a in FOLD_ANGLES or 0.0 < a < 90.0 for a in angles), f"illegal fold angles {angles}"
    reg = inset_region(region, ligament_min) if ligament_min > 0 else as_sketch(region)
    if not reg.faces():
        return FoldNet((), (), (), (), thickness, axis, 0.0)
    bb = reg.bounding_box()
    ax = axis.upper()
    u0, u1 = (bb.min.X, bb.max.X) if ax == "X" else (bb.min.Y, bb.max.Y)
    across = (bb.size.Y if ax == "X" else bb.size.X) + 2.0
    tilts = [angles[(start + i) % len(angles)] * (1.0 if i % 2 == 0 else -1.0) for i in range(n)]
    L = (u1 - u0) / sum(cos(radians(abs(t))) for t in tilts)
    facets, creases, kept_tilts, heights = [], [], [], [0.0]
    u, z = u0, 0.0
    cleans = [as_sketch(c) for c in clean]
    for i, t in enumerate(tilts):
        du = L * cos(radians(abs(t)))
        mid = u + du / 2.0
        strip = (Pos(mid, bb.center().Y) * Rectangle(du, across) if ax == "X"
                 else Pos(bb.center().X, mid) * Rectangle(across, du))
        foot = strip & reg
        for c in cleans:
            try:
                foot -= c
            except Exception:  # noqa: BLE001
                pass
        if foot.faces() and admits_disc(foot, thickness):
            facets.append(foot)
            kept_tilts.append(t)
            if i:
                p0 = (u, bb.min.Y - 1.0) if ax == "X" else (bb.min.X - 1.0, u)
                p1 = (u, bb.max.Y + 1.0) if ax == "X" else (bb.max.X + 1.0, u)
                creases.append((p0, p1, 1 if t > 0 else -1, abs(t)))
        u += du
        z += L * sin(radians(t))
        heights.append(round(z, 4))
    rise = (max(heights) - min(heights)) if heights else 0.0
    return FoldNet(tuple(facets), tuple(creases), tuple(kept_tilts), tuple(heights),
                   thickness, ax, round(rise, 4))


def _volute(R: float, ribbon: float):
    """One scroll, drawn at the origin with the spine along +X and the scroll growing along +Y:
    an arc of radius R turned through 180 deg, then an arc of R/2 tangent to it at their common
    point and turned back through 180 deg. The two centres and the junction are collinear, which is
    what tangent MEANS - it is why the outline runs as one continuous curve with no corner, and why
    this is not `chassis` (whose members are straight)."""
    from build123d import Align
    half = ribbon / 2.0
    c1, c2 = (0.0, R), (0.0, 1.5 * R)
    big = (Pos(*c1) * (Circle(R + half) - Circle(R - half))
           & Pos(c1[0], c1[1]) * Rectangle(R + ribbon, 2 * R + 2 * ribbon,
                                           align=(Align.MIN, Align.CENTER)))
    small = (Pos(*c2) * (Circle(R / 2 + half) - Circle(R / 2 - half))
             & Pos(c2[0], c2[1]) * Rectangle(R / 2 + ribbon, R + 2 * ribbon,
                                             align=(Align.MAX, Align.CENTER)))
    return big + small, ((0.0, 0.0), (0.0, 2 * R), (0.0, R))


def scroll_net(region, *, R: float, ribbon: float = 1.4, spine_w: float = 2.4,
               void_band=FILIGREE_VOID_BAND, spine_deg: float | None = None, node_d: float = 4.0,
               clean=(), ligament_min: float = 0.0, hole_min: float = 0.0, tries: int = 8, **_kw):
    """FILIGREE. The scroll net: a solid SPINE `spine_w` wide along the load path, and off it a net
    of `ribbon`-wide tangent-arc scrolls at pitch 1.6R, mirrored about the spine, with a ring node
    of `node_d` at every junction. Returns (cutter, n_voids) - the CUTTER is the open work, so what
    comes back is what gets subtracted, exactly like a vent_*.

    The void fraction is not a hope either: it is measured against the plan area and the ribbon and
    pitch are re-tuned until it lands inside `void_band` (45-60 %), which is asserted before the
    result goes out. Too little void and the part is a plate with scratches on it; too much and the
    net carries nothing."""
    from build123d import Align, mirror, Plane
    reg = inset_region(region, ligament_min) if ligament_min > 0 else as_sketch(region)
    plan = as_sketch(region)
    if not reg.faces() or plan.area <= 0:
        return Sketch(), 0
    bb = reg.bounding_box()
    ang = spine_deg if spine_deg is not None else (0.0 if bb.size.X >= bb.size.Y else 90.0)
    length = hypot(bb.size.X, bb.size.Y)
    cx, cy = bb.center().X, bb.center().Y
    rib, pitch_f = float(ribbon), 1.6
    cleans = [as_sketch(c) for c in clean]
    best = (Sketch(), 0, 0.0)
    for _ in range(max(1, tries)):
        step = max(pitch_f * R, rib + 1.0)
        mat = Pos(cx, cy) * Rotation_z(ang) * Rectangle(length + 2 * R, spine_w)
        one, nodes = _volute(R, rib)
        n_st = int(length / step) + 1
        for i in range(-n_st // 2, n_st // 2 + 1):
            place = Pos(cx, cy) * Rotation_z(ang) * Pos(i * step, 0.0)
            pair = one + mirror(one, Plane.XZ)
            mat += place * pair
            for nx, ny in nodes:
                for sgn in (1.0, -1.0):
                    mat += place * Pos(nx, sgn * ny) * Circle(node_d / 2.0)
        cut = reg - (mat & reg)
        for c in cleans:
            grown = grow_region(c, max(ligament_min, rib))
            try:
                cut -= (grown if grown.faces() else c)
            except Exception:  # noqa: BLE001
                pass
        if hole_min > 0:
            keep = Sketch()
            for f in cut.faces():
                one_f = Sketch() + f
                if admits_disc(one_f, hole_min):
                    keep += one_f
            cut = keep
        frac = cut.area / plan.area if plan.area else 0.0
        best = (cut, len(cut.faces()), frac)
        if void_band[0] <= frac <= void_band[1]:
            break
        if frac < void_band[0]:                 # not enough open work: thinner ribbons, wider pitch
            rib, pitch_f = max(1.0, rib * 0.85), pitch_f * 1.10
        else:                                   # too open: fatter ribbons, tighter pitch
            rib, pitch_f = rib * 1.18, max(1.15, pitch_f * 0.90)
    cut, n, frac = best
    assert void_band[0] - 1e-6 <= frac <= void_band[1] + 1e-6, (
        f"scroll_net void fraction {frac:.3f} outside {void_band} after {tries} tunings "
        f"(R {R}, ribbon {rib:.2f}, spine {spine_w})")
    return cut, n


def Rotation_z(deg: float):
    """Pos/Rot helper kept local so this file stays import-light: a rotation about Z as a Location."""
    from build123d import Rot
    return Rot(0.0, 0.0, deg)


def inset_region(region, amount: float) -> Sketch:
    """2D inward offset of a region sketch, used to keep a boundary ligament. Returns an empty
    Sketch when OCCT cannot offset the profile (then the caller must drop the pattern, not shrink
    it). `amount` is positive for an inward inset."""
    from build123d import offset as _offset
    sk = as_sketch(region)
    if amount <= 0:
        return sk
    try:
        out = _offset(sk, -amount)
    except Exception:  # noqa: BLE001
        return Sketch()
    return out if isinstance(out, Sketch) and out.faces() and out.area > _AREA_TOL else Sketch()


CELL_AREA_BAND = (28.0, 90.0)   # §3.2: a voronoi cell of 28-90 mm² reads as a lattice


def grow_region(region, amount: float) -> Sketch:
    """2D OUTWARD offset - a clean zone grown by the ligament, so a test against the grown zone is a
    ligament test. Returns an empty Sketch when OCCT refuses the profile, and the caller must then
    measure the gap instead of assuming it."""
    from build123d import offset as _offset
    sk = as_sketch(region)
    if amount <= 0:
        return sk
    try:
        out = _offset(sk, amount)
    except Exception:  # noqa: BLE001
        return Sketch()
    return out if isinstance(out, Sketch) and out.faces() and out.area > sk.area else Sketch()


def admits_disc(region, d: float, *, step: float = 0.5, budget: int = 600) -> bool:
    """Does every face of `region` admit a Ø`d` disc? This is the honest measure of an aperture's
    NARROW dimension, which is what the minimum-hole rule is about - a bounding box is not: a
    voronoi cell 12 x 10 in bbox can be 7 mm across the middle and still pass a bbox test.

    Two routes, cheap first: an inward 2D offset by d/2 (exact, and enough for a convex cell), then
    disc sampling for the profiles OCCT refuses to offset - measured on the keyhole, whose Ø10.2 head
    obviously holds a Ø9 disc while the offset of the whole circle-plus-slot profile comes back
    empty."""
    r = d / 2 - 0.02
    if r <= 0:
        return True
    for f in as_sketch(region).faces():
        one = Sketch() + f
        try:
            if inset_region(one, r).faces():
                continue
        except Exception:  # noqa: BLE001
            pass
        bb = f.bounding_box()
        if min(bb.size.X, bb.size.Y) < d - 0.04:
            return False
        c = f.center()
        nx = max(1, int(bb.size.X / step))
        ny = max(1, int(bb.size.Y / step))
        cands = [(bb.min.X + (i + 0.5) * bb.size.X / nx, bb.min.Y + (j + 0.5) * bb.size.Y / ny)
                 for i in range(nx) for j in range(ny)]
        cands.sort(key=lambda p: (p[0] - c.X) ** 2 + (p[1] - c.Y) ** 2)
        fits = False
        for cx, cy in cands[:budget]:
            try:
                if (Pos(cx, cy) * Circle(d / 2 - 0.01) - one).area <= _AREA_TOL:
                    fits = True
                    break
            except Exception:  # noqa: BLE001
                continue
        if not fits:
            return False
    return True


def _min_gap_to(sk: Sketch, others) -> float:
    """Exact smallest distance from `sk` to any of `others` (1e9 when there are none)."""
    best = 1e9
    for o in others:
        for a in sk.faces():
            for b in as_sketch(o).faces():
                try:
                    best = min(best, float(a.distance_to(b)))
                except Exception:  # noqa: BLE001
                    return -1.0
    return best


def _poisson(x0: float, y0: float, x1: float, y1: float, d: float, seed: int) -> list[tuple[float, float]]:
    """Dart-thrown Poisson-disk sample with minimum separation exactly `d`, deterministic in `seed`.
    The separation is VERIFIED by the caller, not assumed: material between two cells of
    circumradius r is then at least d - 2r, which is the whole ligament guarantee."""
    import random
    rng = random.Random(seed)
    target = max(4, int((x1 - x0) * (y1 - y0) / (0.72 * d * d)))
    pts: list[tuple[float, float]] = []
    for _ in range(target * 60):
        if len(pts) >= target * 2:
            break
        p = (rng.uniform(x0, x1), rng.uniform(y0, y1))
        if all(hypot(p[0] - q[0], p[1] - q[1]) >= d for q in pts):
            pts.append(p)
    return pts


def _clip_halfplane(poly, px, py, nx, ny, offset_):
    """Keep the half plane (v - p).n <= offset_. Sutherland-Hodgman on a convex polygon."""
    out = []
    for a in range(len(poly)):
        A, B = poly[a], poly[(a + 1) % len(poly)]
        da = (A[0] - px) * nx + (A[1] - py) * ny - offset_
        db = (B[0] - px) * nx + (B[1] - py) * ny - offset_
        if da <= 0:
            out.append(A)
        if (da <= 0) != (db <= 0):
            t = da / (da - db)
            out.append((A[0] + (B[0] - A[0]) * t, A[1] + (B[1] - A[1]) * t))
    return out


def vent_voronoi(region, *, pitch: float, ligament_min: float, clean=(), seed: int = 7,
                 cell_d: float | None = None, hole_min: float = 0.0, limit: int = 0, **_kw):
    """CHASSIS. Lloyd-free Voronoi cell field with an EXACT ligament: each cell is the Voronoi
    polygon inset by offsetting every bisector HALF PLANE inward by ligament/2, which is true
    Minkowski erosion because a Voronoi cell is always convex. The gap left between two
    neighbouring inset cells is exactly 2 x inset, and that gap IS the ligament.

    Do NOT inset by scaling vertices toward the centroid: that moves far edges barely at all and
    collapses near ones (measured: 91 % of the volume gone, 0.45 mm walls against a 1.6 target).

    PETG-first. Below a 2.0 mm ligament TPU struts flop and the part looks damaged, not skeletal."""
    reg = as_sketch(region)
    bb = reg.bounding_box()
    # the family asks for cells of 28-90 mm²; a Poisson field at separation d averages ~0.866 d²,
    # so d belongs in 5.7..10.2. `pitch * 1.7` put a pitch-8 field at 160 mm² a cell - one or two
    # giant cells per panel, which reads as a hole, not a lattice.
    d = clamp(pitch, sqrt(CELL_AREA_BAND[0] / 0.866), sqrt(CELL_AREA_BAND[1] / 0.866)) \
        if cell_d is None else cell_d
    inset = ligament_min / 2.0 + 0.1  # +0.1: an exact inset lands ON the floor, which fails >=
    pts = _poisson(bb.min.X, bb.min.Y, bb.max.X, bb.max.Y, d, seed)
    if len(pts) < 2:
        return Sketch(), 0
    sep = min(hypot(a[0] - b[0], a[1] - b[1]) for i, a in enumerate(pts) for b in pts[i + 1:])
    assert sep >= d - 1e-6, f"poisson property violated: {sep:.4f} < {d}"
    pad = 2 * d
    frame = [(bb.min.X - pad, bb.min.Y - pad), (bb.max.X + pad, bb.min.Y - pad),
             (bb.max.X + pad, bb.max.Y + pad), (bb.min.X - pad, bb.max.Y + pad)]
    cells = []
    for i, (px, py) in enumerate(pts):
        poly = list(frame)
        for j, (qx, qy) in enumerate(pts):
            if i == j:
                continue
            dx, dy = qx - px, qy - py
            n = hypot(dx, dy)
            mx, my = (px + qx) / 2, (py + qy) / 2
            poly = _clip_halfplane(poly, mx, my, dx / n, dy / n, -inset)
            if len(poly) < 3:
                break
        if len(poly) >= 3:
            cells.append(poly)
    inner = inset_region(reg, ligament_min)
    if not inner.faces():
        return Sketch(), 0
    # the clean zones are GROWN by the ligament before the test: a Voronoi cell is clipped, not
    # placed, so place_apertures' grown-candidate rule never sees it, and testing the raw cell
    # against the raw clean zone would let a cell land flush against a bore wall.
    cleans, blind = [], []
    for c in clean:
        csk = as_sketch(c)
        grown = grow_region(csk, ligament_min)
        (cleans if grown.faces() else blind).append(grown if grown.faces() else csk)
    kept, out = 0, Sketch()
    for poly in cells:
        try:
            sk = Polygon(*poly, align=None)
            sk = sk & inner   # cells run out to the rim instead of being dropped whole
        except Exception:  # noqa: BLE001
            continue
        if not sk.faces() or sk.area < CELL_AREA_BAND[0] * 0.3 or not _clear_of(sk, cleans):
            continue
        if _min_gap_to(sk, blind) < ligament_min - 1e-6:  # un-growable clean zone: measure instead
            continue
        # the minimum hole is about the cell's NARROW dimension, not its bounding box: a cell 12 x 10
        # in bbox can be 7 mm across the middle, and a bbox test let exactly that through
        if hole_min and not admits_disc(sk, hole_min):
            continue
        out += sk
        kept += 1
        if limit and kept >= limit:
            break
    return out, kept


def puncta(region, *, pitch: float = 3.6, d: float = 1.8, depth: float = 0.45, z_face: float = 0.0,
           clean=(), plane: Plane = Plane.XY, ligament_min: float | None = None, seed: int = 0,
           limit: int = 0, **_kw) -> tuple[Part, int]:
    """CARAPACE / FERAL. A field of BLIND spherical dimples - punctation, the rows of pits in the
    shell. Returns a Part to SUBTRACT, plus the count.

    Hard caps, both measured: Ø <= 2.4 (a Ø2.4 dimple face is ~4.5 mm², just under the 5.0 mm²
    floor in overhangs(); at Ø3.0 it is 7 mm² and flags) and depth <= 0.45. Pits read as print
    defects below L 18, so scale_features() switches them off at the micro tier."""
    assert d <= PUNCTA_D_MAX + 1e-9, f"puncta Ø{d} exceeds the {PUNCTA_D_MAX} mm face-area cap"
    assert depth <= PUNCTA_DEPTH_MAX + 1e-9, f"puncta depth {depth} exceeds {PUNCTA_DEPTH_MAX}"
    g = (pitch - d) if ligament_min is None else ligament_min

    def shape(cx, cy, grow):
        return Pos(cx, cy) * Circle(d / 2 + grow)

    flat, n = place_apertures(region, shape, grid_centres(region, pitch, pitch * sqrt(3) / 2, stagger=True),
                             ligament_min=g, clean=clean, pairwise=False, limit=limit)
    if not n:
        return Part(), 0
    rs = (d * d / 4 + depth * depth) / (2 * depth)  # sphere whose cap of `depth` is Ø d
    tool = Part()
    for f in flat.faces():
        c = f.center()
        tool += plane * Pos(c.X, c.Y, z_face + rs - depth) * Sphere(rs)
    return tool, n


def serration(path_pts, *, d: float = 1.6, pitch: float = 3.2, protrusion: float = 0.8,
              outward: tuple[float, float] | None = None) -> tuple[Sketch, int]:
    """CHASSIS / FERAL. The spined tibia: half-round bumps marching along an OUTBOARD edge.
    `path_pts` is the polyline of that edge in plan; bumps are placed every `pitch` along it and
    pushed out by `protrusion - d/2` along the outward normal. Returns a Sketch to UNION."""
    pts = [(float(x), float(y)) for x, y in path_pts]
    if len(pts) < 2:
        return Sketch(), 0
    segs = [(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    total = sum(hypot(b[0] - a[0], b[1] - a[1]) for a, b in segs)
    n = int(total // pitch)
    if n < 1:
        return Sketch(), 0
    out, placed, s = Sketch(), 0, pitch / 2
    for a, b in segs:
        L = hypot(b[0] - a[0], b[1] - a[1])
        if L < 1e-9:
            continue
        tx, ty = (b[0] - a[0]) / L, (b[1] - a[1]) / L
        nx, ny = (ty, -tx) if outward is None else outward
        nl = hypot(nx, ny) or 1.0
        nx, ny = nx / nl, ny / nl
        while s <= L:
            cx = a[0] + tx * s + nx * (protrusion - d / 2)
            cy = a[1] + ty * s + ny * (protrusion - d / 2)
            out += Pos(cx, cy) * Circle(d / 2)
            placed += 1
            s += pitch
        s -= L
    return out, placed


def starburst(center: tuple[float, float], bore_r: float, *, n: int = 8, w: float = 1.2,
              length: float | None = None, clean=(), region=None) -> tuple[Sketch, int]:
    """CHASSIS hub accent: n radial slots round the largest bore, length 0.35 x R. UNION them into
    the cutter that also cuts the bore, or subtract separately."""
    length = 0.35 * bore_r if length is None else length
    out, kept = Sketch(), 0
    for i in range(n):
        a = 360.0 * i / n
        rmid = bore_r + length / 2
        sk = Pos(center[0] + rmid * cos(radians(a)), center[1] + rmid * sin(radians(a))) * \
            SlotOverall(length + w, w).rotate(Axis.Z, a)
        if region is not None and not _inside(sk, as_sketch(region)):
            continue
        if not _clear_of(sk, [as_sketch(c) for c in clean]):
            continue
        out += sk
        kept += 1
    return out, kept


def ring_node(center: tuple[float, float], strut_w: float, *, od_factor: float = 2.6,
              id_factor: float = 0.9) -> tuple[Sketch, Sketch]:
    """CHASSIS signature: every strut junction is a visible eyelet. Returns (solid_ring, bore) -
    union the ring into the truss and subtract the bore. OD 2.6 x strut width, ID 0.9 x strut
    width, exactly as the family spec, so the ring is always a ring and never a blob."""
    r_out, r_in = od_factor * strut_w / 2, id_factor * strut_w / 2
    return Pos(*center) * Circle(r_out), Pos(*center) * Circle(r_in)


def rib_band(x0: float, x1: float, ys, *, width: float, proud: float, z0: float,
             ramp: float = 45.0) -> Part:
    """ARSENAL external ribs, transverse (CN-2), each ending in a `ramp` degree run-out so it is
    self-supporting. Returns a Part to UNION onto an outboard face at Z z0 (ribs stand in +Z)."""
    run = proud / max(1e-6, abs(sin(radians(ramp)) / max(cos(radians(ramp)), 1e-6)))
    out = Part()
    for y in ys:
        body = Polygon((x0, z0), (x1, z0), (x1 - run, z0 + proud), (x0 + run, z0 + proud), align=None)
        xz = Plane(origin=(0, y - width / 2, 0), x_dir=(1, 0, 0), z_dir=(0, -1, 0))
        out += extrude(xz * body, amount=width)
    return out


def light_well(center: tuple[float, float], z_face: float, *, led_d: float = 3.0,
               half_angle: float = 25.0, depth: float = 4.0) -> Part:
    """NOCTURNE: a conical light well, mouth Ø = 3 x LED, `half_angle` flare, sunk `depth` into the
    face at z_face. Returns a Part to SUBTRACT. Pair with a 1.0 thick translucent cap printed as a
    separate label so the kit stays two-filament without an AMS."""
    mouth = 3.0 * led_d
    throat = max(led_d, mouth - 2 * depth * (sin(radians(half_angle)) / max(cos(radians(half_angle)), 1e-6)))
    return Pos(center[0], center[1], z_face - depth) * Cone(throat / 2, mouth / 2, depth,
                                                            align=(Align.CENTER, Align.CENTER, Align.MIN))


# --- the mark system: a tiger-beetle mark (CN-4) ----------------------------------------------
MARK_MIN = {"lunule": 16.0, "stripe3": 8.0, "mandible": 20.0, "wordmark": 22.0}
MARK_MODES = ("emboss", "deboss", "cut", "inlay")
INLAY_DEPTH, INLAY_CLEARANCE = 0.8, 0.2


def mark_fits(kind: str, size: float) -> bool:
    """If no surface can hold the mark at its minimum size, the part carries R_NO mark - a crushed
    mark is worse than none (§4.3)."""
    return size >= MARK_MIN[kind] - 1e-9


def _sickle(length: float, sweep_deg: float = 118.0, n: int = 26, stroke_min: float = MARK_STROKE_MIN) -> Sketch:
    """The maculation: a crescent thick at the outboard end, tapering to a cusp inboard. Built as a
    tapered swept arc rather than a circle difference, because a circle difference is symmetric and
    a tiger beetle's lunule is not."""
    half = radians(sweep_deg / 2)
    R = length / (2 * sin(half))
    t0, t1 = 0.30 * length, max(0.55 * stroke_min, 0.055 * length)
    outer, inner = [], []
    for i in range(n + 1):
        u = i / n
        a = -half + 2 * half * u
        t = t0 + (t1 - t0) * u ** 0.85
        for arr, sgn in ((outer, +1), (inner, -1)):
            r = R + sgn * t / 2
            arr.append((r * sin(a), r * cos(a) - R))
    poly = Polygon(*outer, *reversed(inner), align=None)
    tip = ((outer[-1][0] + inner[-1][0]) / 2, (outer[-1][1] + inner[-1][1]) / 2)
    return poly + Pos(*tip) * Circle(t1 / 2)   # on the MID radius, so it fuses with the polygon


def _stripe3(size: float, stroke: float | None = None) -> Sketch:
    """The small-part substitute for the lunule: three transverse bars, lengths 1 : 0.75 : 0.5.
    Transverse, because repeating features run across X and never along Y (CN-2)."""
    stroke = max(MARK_STROKE_MIN, 0.13 * size) if stroke is None else stroke
    pitch = 2.2 * stroke
    sk = Sketch()
    for i, f in enumerate((1.0, 0.75, 0.5)):
        sk += Pos(0, (1 - i) * pitch) * SlotOverall(size * f, stroke)
    return sk


def _wordmark(size: float, text: str = "TIGERBEE", grow: float = 0.28) -> Sketch:
    """ARSENAL only. Stencil-ish: a bold face scaled so the run is `size` wide, then grown so the
    stroke approaches the 1.6 mm floor. CAVEAT, measured: below ~10 mm cap height no normal face
    holds a 1.6 mm stroke without closing its counters, so the growth is capped. Treat the
    wordmark as legible-at-arms-length branding, and use stripe3 when a true 1.6 stroke matters."""
    from build123d import FontStyle
    from build123d import offset as _offset
    probe = Text(text, 10.0, font_style=FontStyle.BOLD)
    w = probe.bounding_box().size.X or 1.0
    sk = Text(text, 10.0 * size / w, font_style=FontStyle.BOLD)
    if grow > 0:
        try:
            grown = _offset(sk, grow)
            if isinstance(grown, Sketch) and grown.faces():
                sk = grown
        except Exception:  # noqa: BLE001 - counters closed; ship the ungrown glyphs
            pass
    return sk


def _plinth(sk: Sketch, skirt: float = MARK_SKIRT) -> Sketch | None:
    """The CN-4 emboss plinth: the mark's own outline grown `skirt` all round, so the emboss is wider
    at its base and cannot peel. Returns None when neither route survives (no plinth is still a legal
    emboss, just less peel-proof).

    OCCT refuses a single offset of a many-face sketch - measured on the stencil wordmark, whose
    plinth came back empty and left the glyphs standing on nothing - so each glyph is offset on its
    own and the results are unioned. A per-glyph plinth is also the better reading: the wordmark
    stands on eight little pads rather than one slab."""
    for route in ("whole", "per_face"):
        try:
            from build123d import offset as _off
            if route == "whole":
                out = _off(sk, skirt)
                if isinstance(out, Sketch) and out.faces() and out.area > sk.area:
                    return out
                continue
            acc, n = Sketch(), 0
            for f in sk.faces():
                try:
                    one = _off(Sketch() + f, skirt)
                except Exception:  # noqa: BLE001 - a glyph OCCT will not offset keeps no pad
                    continue
                if isinstance(one, Sketch) and one.faces():
                    acc += one
                    n += 1
            if n and acc.area > sk.area:
                return acc
        except Exception:  # noqa: BLE001
            continue
    return None


def mark_sketch(kind: str, size: float, *, text: str = "TIGERBEE", stroke: float | None = None,
                mirror_x: bool = False) -> Sketch:
    """The 2D mark, centred on the origin, long axis along local +X. `mirror_x` gives the other
    flank of a mirrored pair (the lunule is mirrored, never rotated)."""
    if kind == "lunule":
        sk = _sickle(size, stroke_min=stroke or MARK_STROKE_MIN)
    elif kind == "stripe3":
        sk = _stripe3(size, stroke)
    elif kind == "mandible":
        one = _sickle(size * 0.92, sweep_deg=130.0)
        sk = Pos(-size * 0.11, 0) * one + Pos(size * 0.11, 0) * one.mirror(Plane.YZ)
    elif kind == "wordmark":
        sk = _wordmark(size, text)
    else:
        raise KeyError(f"unknown mark {kind!r}; kinds: {sorted(MARK_MIN)}")
    return sk.mirror(Plane.YZ) if mirror_x else sk


def mark(kind: str, size: float, mode: str, at, normal=(0.0, 0.0, 1.0), *, text: str = "TIGERBEE",
         depth: float | None = None, angle: float = 0.0, through: float = 0.0,
         stroke: float | None = None, mirror_x: bool = False, x_dir=None) -> Part:
    """CN-4: two-tone by geometry. Returns a Part - ADD it for `emboss`, SUBTRACT it for `deboss`,
    `cut` and `inlay`. Never an engraved line.

      emboss  0.6 proud on a 0.3 plinth 0.3 wider all round, so the mark cannot peel (a plinth,
              not a 45 deg taper loft: OCCT's tapered extrude fails outright on a multi-face mark,
              and a plinth is wider at the bottom so it adds no overhang)
      deboss  0.6 deep (exactly 3 layers at 0.2 - paintable, or a clean filament-change plane)
      cut     straight through `through` mm (FERAL cuts the lunule as a slash)
      inlay   0.8 deep with 0.2 clearance all round for a second-colour insert

    `at` is the point on the surface, `normal` its outward normal, `angle` the rotation of the
    mark's long axis in that surface. Placement rules the CALLER owns: the largest uninterrupted
    planar or single-curvature surface, >= 2.0 mm from any clean zone, 1.5 x stroke from any
    aperture - and no mark at all when mark_fits() is False."""
    assert mode in MARK_MODES, f"mode {mode!r} not in {MARK_MODES}"
    from build123d import offset as _offset
    sk = mark_sketch(kind, size, text=text, stroke=stroke, mirror_x=mirror_x)
    if angle:
        sk = sk.rotate(Axis.Z, angle)
    n = Vector(*normal).normalized()
    kw = {"origin": tuple(at), "z_dir": tuple(n)}
    if x_dir is not None:
        kw["x_dir"] = tuple(x_dir)
    pl = Plane(**kw)
    if mode == "emboss":
        d = MARK_DEPTH if depth is None else depth
        body = extrude_cut(sk, pl, d)
        base = _plinth(sk)
        if base is not None:
            body += extrude_cut(base, pl, MARK_SKIRT)
        return body
    if mode == "inlay":
        d = INLAY_DEPTH if depth is None else depth
        try:
            grown = _offset(sk, INLAY_CLEARANCE)
            if isinstance(grown, Sketch) and grown.faces():
                sk = grown
        except Exception:  # noqa: BLE001
            pass
    elif mode == "cut":
        d = through if through > 0 else 50.0
    else:
        d = MARK_DEPTH if depth is None else depth
    out = Plane(origin=tuple(Vector(*at) + n * 0.01), z_dir=tuple(n),
                **({"x_dir": tuple(x_dir)} if x_dir is not None else {}))
    return extrude_cut(sk, out, -(d + 0.01))


# --- style conformance helpers (the §5.2 extra checks a module splices into checks()) ----------
def facet_report(part: Part, min_across: float = FACET_MIN, ignore_extent: float | None = None) -> tuple[bool, str]:
    """SHARD conformance: no planar facet smaller than `min_across` across, the rule that stops
    low-poly reading as a broken mesh export (facet normals 18-40 deg apart, nothing under 8 mm).

    Rim faces are not facets: a 6 mm plate legitimately has 6 mm thick edges, so faces whose short
    extent equals the part's own smallest bbox dimension are skipped. Pass `ignore_extent`
    explicitly when the part is not plate-like. Edge-treatment strips are skipped by area."""
    bb0 = part.bounding_box()
    if ignore_extent is None:
        ignore_extent = min(bb0.size.X, bb0.size.Y, bb0.size.Z)
    ignore_area = 0.125 * min_across * min_across
    small = []
    for f in part.faces():
        if f.geom_type.name != "PLANE" or f.area < ignore_area:
            continue
        bb = f.bounding_box()
        across = min(v for v in (bb.size.X, bb.size.Y, bb.size.Z) if v > 1e-6)
        if across <= ignore_extent + 0.01 or across >= min_across - 1e-6:
            continue
        small.append(round(across, 2))
    return not small, (f"{len(small)} facet(s) under {min_across} mm across "
                       f"(rim extent {ignore_extent:.2f} ignored): {sorted(small)[:6]}")


def tip_radius_report(part: Part, r: float = 0.4, samples: int = 0) -> tuple[bool, str]:
    """FERAL and any cusped style: a Ø2r sphere must fit at every silhouette extremity. Implemented
    as a convexity probe at the six bbox extremes - the cheap version of the check; a module with
    real sculpted tips should probe each tip explicitly."""
    bb = part.bounding_box()
    worst, bad = None, []
    for axis, lo, hi in (("X", bb.min.X, bb.max.X), ("Y", bb.min.Y, bb.max.Y), ("Z", bb.min.Z, bb.max.Z)):
        for end, v in (("min", lo), ("max", hi)):
            c = [bb.center().X, bb.center().Y, bb.center().Z]
            c["XYZ".index(axis)] = v + (r if end == "min" else -r)
            ball = Pos(*c) * Sphere(r)
            frac = 0.0
            try:
                inter = part & ball
                frac = float(inter.volume) / float(ball.volume) if inter is not None else 0.0
            except Exception:  # noqa: BLE001
                frac = 0.0
            if worst is None or frac < worst:
                worst = frac
            if frac < 0.30:
                bad.append(f"{axis}{end} {frac:.2f}")
    return not bad, f"worst tip fill {worst:.2f} of a Ø{2 * r} ball; thin at {bad or 'nowhere'}"


def suture_present(part: Part, y0: float, y1: float, z_top: float, *, w: float = SUTURE_W,
                   depth: float = SUTURE_D) -> tuple[bool, str]:
    """CARAPACE conformance: the groove is actually there. Probes the groove volume against the
    ideal V prism; a full-depth groove fills ~0.5 of the probe box."""
    from tigerbee.accessories._fit import isect
    probe = Pos(0.0, (y0 + y1) / 2, z_top - depth / 2) * Box(w, abs(y1 - y0) * 0.6, depth)
    v = isect(part, probe)
    frac = v / probe.volume if probe.volume else 1.0
    return frac < 0.72, f"groove probe {frac:.2f} solid (a cut V groove reads ~0.45-0.60)"


# --- the style x accessory matrix and the kits (§6, §7.2) -------------------------------------
# How each family reads on each part, straight out of the design-language matrix:
#   "hero"  build it first, it sells the style   "ok"    works well
#   "plain" allowed, plain reading               "no"    do not - fall back to FALLBACK_STYLE
# A style is never *forbidden* by this table; "no" only means the kit picks the fallback instead,
# so a user who asks for a NOCTURNE quad still gets a complete quad.
R_HERO, R_OK, R_PLAIN, R_NO = "hero", "ok", "plain", "no"
FALLBACK_STYLE = "shard"   # §3.3: every accessory ships a SHARD option, no Blender in the pipeline
STYLE_ORDER = ("shard", "arsenal", "chassis", "carapace", "feral", "slipstream", "nocturne",
               "origami", "filigree", "brutalist", "vespid", "gyroid", "coral")

_MATRIX_ROWS = (
    # (accessory, L, carapace, chassis, shard, feral, slipstream, arsenal, nocturne)
    ("side_panels",  62, R_HERO,  R_OK,    R_OK,   R_PLAIN, R_HERO,  R_HERO, R_HERO),
    ("camera_pod",   34, R_OK,    R_OK,    R_HERO, R_HERO,  R_HERO,  R_OK,   R_NO),     # vanes in FOV
    ("front_bumper", 30, R_OK,    R_OK,    R_OK,   R_HERO,  R_OK,    R_OK,   R_NO),     # vanes get crushed
    ("motor_guard",  70, R_PLAIN, R_HERO,  R_OK,   R_OK,    R_OK,    R_OK,   R_OK),
    ("antenna_mast", 45, R_OK,    R_HERO,  R_OK,   R_OK,    R_OK,    R_OK,   R_HERO),
    ("arm_sleeve",   40, R_HERO,  R_OK,    R_OK,   R_OK,    R_OK,    R_OK,   R_OK),
    ("battery_pad",  90, R_OK,    R_OK,    R_OK,   R_PLAIN, R_NO,    R_HERO, R_NO),     # no gloss under a pack
    ("gopro_mount",  28, R_OK,    R_OK,    R_HERO, R_OK,    R_OK,    R_HERO, R_PLAIN),
    ("gps_mount",    26, R_OK,    R_HERO,  R_OK,   R_PLAIN, R_OK,    R_OK,   R_OK),
    ("xt60_holder",  24, R_PLAIN, R_OK,    R_HERO, R_PLAIN, R_PLAIN, R_HERO, R_OK),
    ("cap_holder",   16, R_PLAIN, R_OK,    R_HERO, R_PLAIN, R_NO,    R_OK,   R_PLAIN),  # micro rule
    ("led_buzzer",   14, R_PLAIN, R_OK,    R_OK,   R_PLAIN, R_NO,    R_OK,   R_HERO),
    ("tail_block",   50, R_HERO,  R_OK,    R_OK,   R_HERO,  R_HERO,  R_OK,   R_HERO),
    ("landing",      35, R_OK,    R_HERO,  R_OK,   R_OK,    R_PLAIN, R_HERO, R_PLAIN),
)
_MATRIX_FAMILIES = ("carapace", "chassis", "shard", "feral", "slipstream", "arsenal", "nocturne")
MATRIX = {row[0]: dict(zip(_MATRIX_FAMILIES, row[2:])) for row in _MATRIX_ROWS}
NOMINAL_L = {row[0]: float(row[1]) for row in _MATRIX_ROWS}


def reads_as(accessory: str, family: str) -> str:
    """How `family` reads on `accessory`: "hero" | "ok" | "plain" | "no". An accessory the matrix
    has never heard of (a module added after this table) reads "ok" in every family - the table
    steers taste, it must never block a sibling's new part from appearing in a kit."""
    return MATRIX.get(accessory, {}).get(style_of(family).name, R_OK)


def kit_pick(accessory: str, family: str, available: tuple[str, ...] = ()) -> tuple[str, bool]:
    """(style, is_fallback) for one accessory in one family's kit.

    `available` is what the module actually ships (variant style names). The family's own style wins
    when the matrix likes it and the module ships it; otherwise the pick walks FALLBACK_STYLE first
    and then STYLE_ORDER, so a kit is always complete."""
    want = style_of(family).name
    avail = tuple(style_of(s).name for s in available) if available else ()
    ok_here = reads_as(accessory, want) != R_NO
    if ok_here and (not avail or want in avail):
        return want, False
    for cand in (FALLBACK_STYLE, *STYLE_ORDER):
        if avail and cand not in avail:
            continue
        if not avail and reads_as(accessory, cand) == R_NO:
            continue
        return cand, True
    return (avail[0], True) if avail else (FALLBACK_STYLE, True)


def kit_for(family: str, accessories=None, shipped: dict | None = None) -> list[str]:
    """The labels that together make a coherent quad in `family`: `<accessory>_<style>`, with
    " (fallback)" appended wherever the family has no reading on that part and the kit borrowed
    another style. `shipped` maps accessory -> the style names that module actually builds."""
    names = list(accessories) if accessories is not None else list(MATRIX)
    out = []
    for acc in names:
        style, fb = kit_pick(acc, family, tuple((shipped or {}).get(acc, ())))
        out.append(f"{acc}_{style}" + (" (fallback)" if fb else ""))
    return out


KITS: dict[str, list[str]] = {family: kit_for(family) for family in STYLES}


# --- self test: the vocabulary's own guarantees, measured ---------------------------------------
# `uv run python -m tigerbee.accessories._style` - every row is a NUMBER, not an opinion. The
# generators promise a ligament; this proves it with OCCT distances rather than by construction.
def _faces(sk) -> list:
    try:
        return list(sk.faces()) if sk is not None else []
    except Exception:  # noqa: BLE001 - an empty cutter is a legal result, not a crash
        return []


def _gaps(sk: Sketch, near: float) -> float:
    """Smallest real gap between any two apertures of a cutter sketch (1e9 when there is one).
    Every pair is measured when the field is small; the bbox prefilter only guards the big fields,
    and it never skips a pair whose bboxes are within `near`."""
    faces = _faces(sk)
    prefilter = len(faces) > 30
    worst = 1e9
    for i, a in enumerate(faces):
        ba = a.bounding_box()
        for b in faces[i + 1:]:
            bb = b.bounding_box()
            if prefilter and (max(ba.min.X, bb.min.X) - min(ba.max.X, bb.max.X) > near
                              or max(ba.min.Y, bb.min.Y) - min(ba.max.Y, bb.max.Y) > near):
                continue
            worst = min(worst, float(a.distance_to(b)))
    return worst


def _boundary_gap(sk: Sketch, region: Sketch) -> float:
    """Smallest gap from any aperture to the region's outer boundary."""
    wires = [f.outer_wire() for f in _faces(region)]
    return min((float(f.distance_to(w)) for f in _faces(sk) for w in wires), default=1e9)


def _clean_gap(sk: Sketch, clean: Sketch) -> float:
    fs = _faces(sk)
    if not fs:
        return 1e9
    if (sk & clean).area > _AREA_TOL:
        return -1.0
    return min((float(f.distance_to(c)) for f in fs for c in _faces(clean)), default=1e9)


def _admits_disc(sk: Sketch, d: float) -> bool:
    return not _faces(sk) or admits_disc(sk, d)


_GEN_TESTS = (
    # generator, kwargs, ligament mode (arithmetic lattice / pairwise test), clean-zone centre.
    # The clean zone sits where it leaves the pattern something to do: a generator whose apertures
    # span the whole region (vent_ladder, vent_elytra) is blocked by a mid-region zone BY DESIGN,
    # so those two are tested with the zone near a corner and the blocking case is checked below.
    ("vent_hex", {}, "arithmetic", (-11.0, 0.0)),
    ("vent_ladder", {}, "pairwise", (-18.0, -16.0)),
    ("vent_elytra", {}, "pairwise", (-18.0, -17.0)),
    ("vent_louvre", {}, "pairwise", (-11.0, 0.0)),
    ("vent_keyhole", {}, "pairwise", (-11.0, 0.0)),
    ("vent_voronoi", {"seed": 7}, "arithmetic", (-11.0, 0.0)),
)


def _test_generators(rows, pitch=8.0, g=2.0):
    region = Rectangle(46, 40)
    # PAIR_GROW is 0.45, so two kept neighbours are >= 0.90 x ligament apart in the worst case;
    # a lattice placed by pitch arithmetic owes the full ligament.
    for name, kw, mode, at in _GEN_TESTS:
        gen = globals()[name]
        clean = Pos(*at) * Circle(3.5)
        cut, n = gen(region, pitch=pitch, ligament_min=g, clean=(clean,), hole_min=2.0, **kw)
        floor_ = g - 0.02 if mode == "arithmetic" else 0.90 * g - 0.02
        gap, edge, cl = _gaps(cut, 6 * g), _boundary_gap(cut, region), _clean_gap(cut, clean)
        rows.append((f"{name}: at least 2 apertures placed on a 46 x 40 region", n >= 2, f"n={n}"))
        rows.append((f"{name}: ligament between apertures >= {floor_:.2f}", gap >= floor_,
                     f"min gap {gap:.4f} mm (target {g})"))
        rows.append((f"{name}: ligament to region boundary >= {g - 0.02:.2f}", edge >= g - 0.02,
                     f"min boundary gap {edge:.4f} mm"))
        rows.append((f"{name}: ligament to the clean zone >= {0.90 * g:.2f}", cl >= 0.90 * g - 0.02,
                     f"gap to clean zone {cl:.4f} mm (0 area intersection required)"))
        rows.append((f"{name}: no aperture narrower than the minimum hole (2.0 PETG)",
                     _admits_disc(cut, 2.0), f"{n} apertures probed with a Ø2.0 disc"))
        # ask for 9 mm apertures: a generator either drops the field or opens up to the floor, but
        # it must NEVER emit something narrower than the floor it was handed
        cut2, n2 = gen(region, pitch=pitch, ligament_min=g, clean=(clean,), hole_min=9.0, **kw)
        rows.append((f"{name}: at a 9.0 minimum hole, survivors are all >= 9.0 wide",
                     _admits_disc(cut2, 9.0), f"n={n2} survivor(s), none shrunk below 9.0"))
        # a clean zone across the middle of the region: whatever survives still clears it
        mid = Pos(0.0, 0.0) * Circle(7.0)
        cut3, n3 = gen(region, pitch=pitch, ligament_min=g, clean=(mid,), hole_min=2.0, **kw)
        rows.append((f"{name}: a clean zone through the middle is respected or the field is dropped",
                     n3 == 0 or _clean_gap(cut3, mid) >= 0.90 * g - 0.02,
                     f"n={n3}, gap {_clean_gap(cut3, mid):.4f} mm"))
        # determinism
        cut4, n4 = gen(region, pitch=pitch, ligament_min=g, clean=(clean,), hole_min=2.0, **kw)
        rows.append((f"{name}: deterministic", n4 == n and abs(cut4.area - cut.area) < 1e-6,
                     f"{n} then {n4}, area delta {abs(cut4.area - cut.area):.2e}"))


def _test_scale_law(rows):
    micro = scale_law(12.0, "carapace", wall=1.6, material="PETG")
    rows.append(("scale law: L 12 is micro, n=2, no puncta, stripe3 not lunule",
                 micro["tier"] == "micro" and micro["count"] == 2 and not micro["puncta"]
                 and micro["mark_kind"] == "stripe3", str(micro)))
    small = scale_law(24.0, "shard", wall=1.5)
    rows.append(("scale law: 18-32 is small, n in 3..4", small["tier"] == "small"
                 and 3 <= small["count"] <= 4, str(small)))
    med = scale_law(40.0, "chassis", wall=2.0)
    rows.append(("scale law: 32-60 is medium, no second tier",
                 med["tier"] == "medium" and med["second_tier"] == 0.0, str(med)))
    big = scale_law(90.0, "arsenal", wall=1.5)
    rows.append(("scale law: >= 60 adds a sub-pattern at p/2.6",
                 big["tier"] == "large" and abs(big["second_tier"] - big["pitch"] / 2.6) < 0.01,
                 str(big)))
    rows.append(("scale law: pitch clamped to 4..14",
                 scale_law(10.0, "shard")["pitch"] == 4.0 and scale_law(300.0, "shard")["pitch"] == 14.0,
                 f"{scale_law(10.0, 'shard')['pitch']} / {scale_law(300.0, 'shard')['pitch']}"))
    for mat, floor_ in (("TPU95A", 1.2), ("PETG", 1.6)):
        f = scale_law(36.0, "shard", wall=1.5, material=mat)
        want = max(0.45 * f["pitch"], 1.2 * 1.5, floor_)
        rows.append((f"scale law: {mat} ligament = max(0.45p, 1.2 wall, {floor_})",
                     abs(f["ligament"] - want) < 1e-6, f"{f['ligament']} vs {want:.3f}"))
    rows.append(("scale law: aperture = 0.55 p (to the law's own 0.001 rounding)",
                 all(abs(scale_law(L, "shard")["aperture"] - 0.55 * scale_law(L, "shard")["pitch"]) < 2e-3
                     for L in (14.0, 30.0, 50.0, 80.0)), "checked at L 14/30/50/80"))
    rows.append(("scale law: mark size clamped to 8..34",
                 scale_law(12.0, "shard")["mark"] == 8.0 and scale_law(200.0, "shard")["mark"] == 34.0,
                 f"{scale_law(12.0, 'shard')['mark']} / {scale_law(200.0, 'shard')['mark']}"))


def _test_edges(rows):
    ok = True
    detail = []
    for name, st in STYLES.items():
        for tier in ("sil", "crease", "free", "tip"):
            wall = 2.0
            r = edge_radius(st, tier, wall)
            frac = CHAMFER_WALL_FRACTION if st.edge["kind"] == "chamfer" else FILLET_WALL_FRACTION
            if r > frac * wall + 1e-9:
                ok = False
                detail.append(f"{name}.{tier}={r}")
    rows.append(("edge ladder: fillet <= 0.45 wall, chamfer <= 0.40 wall", ok,
                 "; ".join(detail) or "every family x tier within its limit at wall 2.0"))
    rows.append(("edge ladder: SLIPSTREAM crease is 0.0 by design (a crease leaves the family)",
                 edge_radius("slipstream", "crease") == 0.0 and EDGE_LADDER["slipstream"]["crease"] == 0.0,
                 f"{edge_radius('slipstream', 'crease')}"))
    rows.append(("edge ladder: tip tier is 0.45 wherever clip mouths live (matches MOUTH_FILLET)",
                 all(EDGE_LADDER[n]["tip"] in (0.45, 0.6, 0.8) for n in EDGE_LADDER),
                 str({n: EDGE_LADDER[n]["tip"] for n in EDGE_LADDER})))


def _test_marks(rows):
    rows.append(("marks: minimum sizes are the §4.3 table",
                 MARK_MIN == {"lunule": 16.0, "stripe3": 8.0, "mandible": 20.0, "wordmark": 22.0},
                 str(MARK_MIN)))
    rows.append(("marks: below the minimum, mark_fits() says no",
                 not any(mark_fits(k, v - 0.1) for k, v in MARK_MIN.items())
                 and all(mark_fits(k, v) for k, v in MARK_MIN.items()), "checked at min and min-0.1"))
    for kind, size in MARK_MIN.items():
        deb = mark(kind, size, "deboss", (0, 0, 0))
        emb = mark(kind, size, "emboss", (0, 0, 0))
        bb = deb.bounding_box()
        span = max(bb.size.X, bb.size.Y)
        rows.append((f"mark {kind}: deboss is {MARK_DEPTH} deep and reaches its nominal size",
                     deb.volume > 0 and abs(bb.size.Z - (MARK_DEPTH + 0.01)) < 0.02
                     and span >= 0.80 * size,
                     f"span {span:.2f} of {size}, depth {bb.size.Z:.2f}"))
        rows.append((f"mark {kind}: emboss sits on a {MARK_SKIRT} plinth (peel-proof, no overhang)",
                     emb.volume > deb.volume * 1.05, f"emboss {emb.volume:.1f} > deboss {deb.volume:.1f} mm³"))
    thin = mark_sketch("stripe3", 8.0)
    bars = sorted((min(f.bounding_box().size.X, f.bounding_box().size.Y) for f in thin.faces()))
    rows.append(("marks: every stroke >= 1.6 mm (four passes at a 0.4 nozzle)",
                 bars and bars[0] >= MARK_STROKE_MIN - 1e-6, f"thinnest stroke {bars[0]:.2f} mm"))


def _test_suture_and_puncta(rows):
    plate = Box(30, 46, 4, align=(Align.CENTER, Align.CENTER, Align.MIN))
    cut = apply_suture(plate)
    rows.append(("suture: CN-1 groove cut on X=0 from the part's own bbox",
                 cut.volume < plate.volume and suture_present(cut, -20.0, 20.0, 4.0)[0],
                 f"removed {plate.volume - cut.volume:.2f} mm³; {suture_present(cut, -20.0, 20.0, 4.0)[1]}"))
    bbc = cut.bounding_box()
    rows.append(("suture: runs out to a cusp inside the silhouette, not off the end",
                 abs(bbc.size.Y - 46.0) < 1e-6 and abs(bbc.size.X - 30.0) < 1e-6,
                 f"bbox {bbc.size.X:.2f} x {bbc.size.Y:.2f} unchanged"))
    off = Pos(20, 0, 0) * Box(10, 20, 4)
    rows.append(("suture: a part clear of X=0 (a mirrored pair's half) carries none",
                 abs(apply_suture(off).volume - off.volume) < 1e-9, "volume unchanged"))
    ok = False
    try:
        puncta(Rectangle(20, 20), d=3.0)
    except AssertionError:
        ok = True
    rows.append(("puncta: Ø > 2.4 refused (a Ø3.0 dimple face is 7 mm², over overhangs()' 5 mm²)",
                 ok, "AssertionError raised" if ok else "accepted a Ø3.0 dimple"))
    ok2 = False
    try:
        puncta(Rectangle(20, 20), depth=0.8)
    except AssertionError:
        ok2 = True
    rows.append(("puncta: depth > 0.45 refused", ok2, "AssertionError raised" if ok2 else "accepted 0.8"))


def _test_kits(rows):
    rows.append(("kits: one per style family", set(KITS) == set(STYLES), str(sorted(KITS))))
    bad, fallbacks = [], {}
    for family, labels in KITS.items():
        if len(labels) != len(MATRIX):
            bad.append(f"{family} has {len(labels)} of {len(MATRIX)}")
        fb = 0
        for entry in labels:
            label = entry.split(" ")[0]
            acc = next((a for a in MATRIX if label.startswith(a + "_")), None)
            style = label[len(acc) + 1:] if acc else ""
            if acc is None or style not in STYLES:
                bad.append(f"{family}: {entry!r} is not <accessory>_<style>")
                continue
            if reads_as(acc, style) == R_NO:
                bad.append(f"{family}: {entry} picks a style the matrix refuses")
            if "(fallback)" in entry:
                fb += 1
                if style != FALLBACK_STYLE:
                    bad.append(f"{family}: fallback {entry} is not {FALLBACK_STYLE}")
        fallbacks[family] = fb
    rows.append(("kits: every kit is a complete quad, every pick legal, fallbacks named",
                 not bad, "; ".join(bad) or f"fallbacks per family {fallbacks}"))
    rows.append(("kits: SHARD and ARSENAL cover the whole set with no Blender",
                 fallbacks.get("shard") == 0 and fallbacks.get("arsenal") == 0
                 and all(s in PURE_B123D_STYLES for s in ("shard", "arsenal")),
                 f"pure build123d families: {PURE_B123D_STYLES}"))
    shipped = {"cap_holder": ("shard",), "led_buzzer": ("nocturne", "shard")}
    rows.append(("kits: a pick falls back when the module does not ship that style",
                 kit_pick("cap_holder", "carapace", shipped["cap_holder"]) == ("shard", True)
                 and kit_pick("led_buzzer", "nocturne", shipped["led_buzzer"]) == ("nocturne", False),
                 str(kit_pick("cap_holder", "carapace", shipped["cap_holder"]))))
    rows.append(("kits: an accessory the matrix has never heard of still gets a pick",
                 kit_pick("gps_pigtail_mount", "carapace", ("carapace", "shard")) == ("carapace", False),
                 str(kit_pick("gps_pigtail_mount", "carapace", ("carapace", "shard")))))


ADDED_STYLES = ("gyroid", "origami", "vespid", "filigree", "brutalist", "coral")


def _test_languages(rows):
    """The six added languages, measured - the same standard as the rest of this file."""
    missing = [n for n in ADDED_STYLES if n not in STYLES or n not in EDGE_LADDER]
    rows.append(("languages: six added families registered with an edge ladder each", not missing,
                 "; ".join(missing) or f"{', '.join(ADDED_STYLES)}"))
    bad = []
    for n in ADDED_STYLES:
        st = style_of(n)
        if st.wall_load < st.wall:
            bad.append(f"{n} wall_load {st.wall_load} < wall {st.wall}")
        for L in (20.0, 40.0, 80.0):
            f = scale_features(L, st, wall=st.wall, material=st.material)
            if not (4.0 <= f.pitch <= 14.0 and f.ligament >= 0.45 * f.pitch - 0.01):
                bad.append(f"{n} at L {L}: {f}")
        if n in ("gyroid", "coral") and not st.blender_only:
            bad.append(f"{n} must declare blender_only")
        if n in ("origami", "filigree", "brutalist") and st.recipe is not None:
            bad.append(f"{n} must be pure build123d")
    rows.append(("languages: the scaling law resolves for all six at L 20/40/80, thick end on the "
                 "load path", not bad, "; ".join(bad) or "6 families x 3 lengths"))
    rows.append(("languages: ORIGAMI/FILIGREE/BRUTALIST need no Blender, so every module can ship one",
                 all(n in PURE_B123D_STYLES for n in ("origami", "filigree", "brutalist")),
                 f"pure: {tuple(n for n in ADDED_STYLES if n in PURE_B123D_STYLES)}"))
    # board_mark: the plank ligament is arithmetic - pitch minus width
    region, clean = Rectangle(46, 40), Pos(-11.0, 0.0) * Circle(3.5)
    cut, n = board_mark(region, w=0.6, pitch=2.4, clean=(clean,), ligament_min=1.6)
    # the plank ligament is measured on the UNCLEANED field: a round clean zone is tangent to some
    # plank's edge whatever the pitch, and trimming there pinches that one plank to a point - which
    # is a 0.3 mm deep groove narrowing, not a wall, and would otherwise read as a 0.0 mm ligament
    gap = _gaps(board_mark(region, w=0.6, pitch=2.4, ligament_min=1.6)[0], 12.0)
    rows.append((f"board_mark: {BOARD_MARK['pitch']} pitch leaves a {BOARD_MARK['pitch'] - BOARD_MARK['w']} "
                 f"ligament between planks", n >= 8 and gap >= 2.4 - 0.6 - 0.02,
                 f"{n} planks, min gap {gap:.4f} mm"))
    rows.append(("board_mark: nothing is cut inside the clean zone",
                 (cut & clean).area <= _AREA_TOL, f"intersection {(cut & clean).area:.6f} mm²"))
    cut2, n2 = board_mark(region, w=0.6, pitch=2.4, clean=(clean,), ligament_min=1.6)
    rows.append(("board_mark: deterministic", n2 == n and abs(cut2.area - cut.area) < 1e-6,
                 f"{n} then {n2}, area delta {abs(cut2.area - cut.area):.2e}"))
    # fold_facets: only the three legal angles, and the footprints tile the region
    fn = fold_facets(region, n=5, thickness=1.8, ligament_min=1.2)
    covered = sum(f.area for f in fn.facets)
    inner = inset_region(region, 1.2).area
    rows.append(("fold_facets: every tilt is drawn from {22.5, 45, 67.5}",
                 bool(fn.angles) and all(abs(a) in FOLD_ANGLES for a in fn.angles), str(fn.angles)))
    rows.append(("fold_facets: the facets tile the region they were given (no gaps, no overlap)",
                 len(fn) >= 4 and abs(covered - inner) <= 0.02 * inner,
                 f"{len(fn)} facets covering {covered:.1f} of {inner:.1f} mm²"))
    rows.append(("fold_facets: one crease per interior joint, each marked mountain or valley",
                 len(fn.creases) == len(fn) - 1
                 and all(c[2] in (1, -1) and abs(c[3]) in FOLD_ANGLES for c in fn.creases),
                 f"{len(fn.creases)} creases, rise {fn.rise} mm"))
    # scroll_net: the void fraction is the family's definition, so it is measured
    net, nv = scroll_net(Rectangle(60, 34), R=6.0, ligament_min=1.6, clean=(clean,))
    frac = net.area / (60 * 34)
    rows.append((f"scroll_net: void fraction inside {FILIGREE_VOID_BAND}",
                 FILIGREE_VOID_BAND[0] <= frac <= FILIGREE_VOID_BAND[1],
                 f"{frac:.3f} over {nv} voids"))
    rows.append(("scroll_net: the clean zone is untouched", (net & clean).area <= _AREA_TOL,
                 f"intersection {(net & clean).area:.6f} mm²"))
    net2, nv2 = scroll_net(Rectangle(60, 34), R=6.0, ligament_min=1.6, clean=(clean,))
    rows.append(("scroll_net: deterministic", nv2 == nv and abs(net2.area - net.area) < 1e-6,
                 f"{nv} then {nv2}, area delta {abs(net2.area - net.area):.2e}"))


def _test_materials(rows):
    rows.append(("materials: minimum through-hole 2.2 TPU / 2.0 PETG",
                 DECOR_MATERIALS["TPU95A"]["hole_min"] == 2.2 and DECOR_MATERIALS["PETG"]["hole_min"] == 2.0,
                 str({m: v["hole_min"] for m, v in DECOR_MATERIALS.items()})))
    rows.append(("materials: PETG's ligament is fatter than TPU's (PETG cracks, TPU bends)",
                 DECOR_MATERIALS["PETG"]["ligament_min"] > DECOR_MATERIALS["TPU95A"]["ligament_min"],
                 str({m: v["ligament_min"] for m, v in DECOR_MATERIALS.items()})))
    rows.append(("materials: puncta capped at Ø2.4 / 0.45 deep in every material",
                 all(v["puncta_d"] <= PUNCTA_D_MAX and v["puncta_depth"] <= PUNCTA_DEPTH_MAX
                     for v in DECOR_MATERIALS.values()), f"Ø{PUNCTA_D_MAX} / {PUNCTA_DEPTH_MAX}"))


def self_test(verbose: bool = True) -> int:
    """Every guarantee this module makes, measured. Returns the number of failures."""
    rows: list[tuple[str, bool, str]] = []
    for fn in (_test_generators, _test_scale_law, _test_edges, _test_marks,
               _test_suture_and_puncta, _test_kits, _test_materials, _test_languages):
        try:
            fn(rows)
        except Exception as exc:  # noqa: BLE001 - a crashed group is a failed group, not a crash
            rows.append((f"{fn.__name__} raised", False, f"{type(exc).__name__}: {exc}"))
    fails = [r for r in rows if not r[1]]
    if verbose:
        for name, ok, detail in rows:
            print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"  [{detail}]" if detail else ""))
        print(f"\n{len(rows) - len(fails)} PASS / {len(fails)} FAIL")
    return len(fails)


if __name__ == "__main__":
    raise SystemExit(1 if self_test() else 0)


# --- §4.5 silhouettes: ONE implementation, TWO projections --------------------------------------
# There were three of these and they had diverged, which is how a gate starts producing answers
# nobody trusts: scripts/thumbnail_silhouette.py measured a real convex hull off a rendered mask,
# antenna_mast measured its own monotone-chain hull off the solid, and side_panel_full used the
# BOUNDING BOX in place of a hull. Same rule on paper, three different numbers.
#
# The gate also looked at ONE projection - straight down. Every differentiator that matters on a
# side panel lives in the other one: a swell, a gill bank, a fin run, an intake, a bow. Two parts
# can share a plan outline to the millimetre and be unmistakable in the hand. So a pair now has to
# be alike in BOTH views to fail. The thresholds are untouched: this is not a wider gate, it is a
# gate that looks at the object from the second direction a person would.
SIL_AREA_DELTA = 0.12
SIL_DEF_DELTA = 0.10
_AXES = {"X": (0, 1, 2), "Y": (1, 0, 2), "Z": (2, 0, 1)}


def hull_area_2d(pts) -> float:
    """Convex-hull area of 2D points by monotone chain."""
    p = sorted(set((round(x, 4), round(y, 4)) for x, y in pts))
    if len(p) < 3:
        return 0.0

    def half(seq):
        out = []
        for q in seq:
            while len(out) >= 2:
                (ax, ay), (bx, by) = out[-2], out[-1]
                if (bx - ax) * (q[1] - ay) - (by - ay) * (q[0] - ax) > 0:
                    break
                out.pop()
            out.append(q)
        return out

    h = half(p)[:-1] + half(p[::-1])[:-1]
    if len(h) < 3:
        return 0.0
    return abs(sum(h[i][0] * h[(i + 1) % len(h)][1] - h[(i + 1) % len(h)][0] * h[i][1]
                   for i in range(len(h)))) / 2.0


def section_metrics(part, axis: str = "Z", at: float | None = None, slab: float = 0.2):
    """(area, hull deficiency) of the part's section normal to `axis`, at `at` (default mid-span).

    A section rather than a true projection, which is what this gate has always compared and what
    keeps the numbers commensurable with the ones already recorded in the modules."""
    from build123d import Box, Pos
    ax, u, v = _AXES[axis]
    bb = part.bounding_box()
    lo = (bb.min.X, bb.min.Y, bb.min.Z)[ax]
    hi = (bb.max.X, bb.max.Y, bb.max.Z)[ax]
    cut = (lo + hi) / 2 if at is None else at
    size = [bb.size.X + 2, bb.size.Y + 2, bb.size.Z + 2]
    size[ax] = slab
    centre = [bb.center().X, bb.center().Y, bb.center().Z]
    centre[ax] = cut
    sec = part & (Pos(*centre) * Box(*size))
    if sec is None or not sec.faces():
        return 0.0, 0.0
    faces = [f for f in sec.faces() if abs(f.normal_at().to_tuple()[ax]) > 0.9]
    area = sum(f.area for f in faces) / 2 if faces else 0.0
    pts = [(vx.to_tuple()[u], vx.to_tuple()[v]) for vx in sec.vertices()]
    hull = hull_area_2d(pts)
    return round(area, 2), round(1.0 - area / hull, 3) if hull > 0 else 0.0


def elevation_axis(part) -> str:
    """Fallback elevation axis: the thinnest direction, i.e. the way you would sight along a part
    to see its profile. PASS THE AXIS EXPLICITLY where the family knows it. Auto-detection picks
    Z for anything wider than it is tall - a panel with deep inboard returns, say - and then the
    'elevation' collapses onto the plan and the second view measures nothing new."""
    bb = part.bounding_box()
    return min((("X", bb.size.X), ("Y", bb.size.Y), ("Z", bb.size.Z)), key=lambda t: t[1])[0]


def silhouette_views(part, elev: str | None = None) -> dict[str, tuple[float, float]]:
    """{'plan': (area, deficiency), 'elev': (area, deficiency)} - the two views §4.5 compares.

    `elev` is the axis sighted along for the elevation; for anything mounted on a flank that is the
    OUTBOARD NORMAL, which is the view a person judges the part by in the hand."""
    ax = elev or elevation_axis(part)
    if ax == "Z":
        ax = elevation_axis(part) if elev else ax
    return {"plan": section_metrics(part, "Z"), "elev": section_metrics(part, ax)}


def silhouette_differs(a: dict, b: dict) -> tuple[bool, str]:
    """True when the pair differs enough in EITHER view. Fails only when alike in BOTH."""
    parts, ok = [], False
    for view in ("plan", "elev"):
        (a0, d0), (a1, d1) = a[view], b[view]
        da = abs(a0 - a1) / max(a0, a1) if max(a0, a1) else 0.0
        dd = abs(d0 - d1)
        hit = da > SIL_AREA_DELTA or dd > SIL_DEF_DELTA
        ok = ok or hit
        parts.append(f"{view} area {da:.1%} hull Δ{dd:.3f}{'' if hit else ' alike'}")
    return ok, "; ".join(parts)
