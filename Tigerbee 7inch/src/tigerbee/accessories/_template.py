"""TEMPLATE (not discovered: name starts with "_"). Copy to `<id>.py` and fill in.

Contract for `src/tigerbee/accessories/<id>.py`:

  NAME      = "<id>"            must equal the module file name
  TITLE     = "Human title"
  MATERIAL  = "TPU95A" | "PETG"
  PRINT     = {label: (nx, ny, nz)}   bed face normal in FRAME coords (the face that lies on the bed);
                                      labels left out print on their -Z face
  EXCLUSIVE = ("other_id", ...)       optional: cannot be installed together (first id alphabetically
                                      wins in the combined assembly)
  MOUNTS    = ("frame face/axis", ...)  REQUIRED: the frame faces and axes this part mounts to, one
                                      short string each, named as _fit names them ("plate_top top
                                      face Z 36", "standoff_rear_tip_left / _right Ø6 shafts",
                                      "Ø4.6 accessory holes (±31.3, 63.5)"). A tuple for the whole
                                      accessory, or {label: tuple} when the parts differ.
  HARDWARE  = ("2 x M3 x 10 ...", ...)  REQUIRED: every fastener the installation needs, each row
                                      "<count> x <size> <type> (<where>)". An accessory that needs
                                      none still says so: ("none - 0.6 mm snap fit",). Tuple or
                                      {label: tuple}. Both land in dist/accessories/manifest.json.
  NOTES     = "mounting notes"        optional: str or {label: str}, copied into the manifest
  build(**overrides) -> dict[str, Part]   labelled parts in FRAME coordinates as installed
  checks(parts, frame) -> list[tuple[str, bool, str | float]]   the REQUIRED CHECKS of the spec;
                                      `parts` is what build() returned, `frame` = frame_parts()

Optional knobs (defaults in accessories/__init__.py OPTIONAL_DEFAULTS): MIN_Z, ALLOWED_INTERFERENCE,
OWN_PROP_DISC, BATTERY_OK, BRIDGE_OK, OVERHANG_SKIP, ASSEMBLY_BUILD, ASSEMBLY_VARIANT, and the hook
orient_for_print(label, part) -> Part when PRINT (a single bed normal) cannot express the orientation.

STYLE VARIANTS - how an accessory ships several genuinely different-looking options
==================================================================================
Declare VARIANTS and the exporter builds one part set per variant, labelling every part
"<base label>__<variant>". build() keeps returning its own BASE labels; the suffix is added for it,
so PRINT / BRIDGE_OK / NOTES / ALLOWED_INTERFERENCE / OWN_PROP_DISC / OVERHANG_SKIP stay keyed by the
base label, and checks() is handed the parts dict keyed by the base labels too:

    VARIANTS = {
      "shard":    {"style": "shard"},                       # pure build123d, always available
      "carapace": {"style": "carapace", "material": "PETG", # a Blender-decorated family
                   "params": {"DOME": True},                # extra kwargs handed to build()
                   "print":  {"side_panel_right": (0, 0, -1)},   # a style may pick its own bed normal
                   "notes":  "one line for the manifest"},
    }
    ASSEMBLY_VARIANT = "shard"        # which one goes into tigerbee_with_accessories

    def build(variant="shard", **overrides) -> dict[str, Part]: ...

ONE checks() SERVES EVERY VARIANT and must pass for all of them - that is the guarantee: whatever the
style does to the look, the same fit assertions still hold. Add variant-specific rows by declaring
checks(parts, frame, variant=None); the framework passes `variant` when the signature accepts it.

The style vocabulary lives in `_style.py` (one owner - import it, never fork a generator):

    from tigerbee.accessories._style import (STYLES, scale_features, edge_radius, treat_edges,
                                             extrude_cut, vent_ladder, vent_hex, vent_louvre,
                                             vent_keyhole, vent_elytra, vent_voronoi, puncta,
                                             serration, starburst, ring_node, rib_band, light_well,
                                             lens, cusp_tail, suture, mark, mark_fits,
                                             facet_report, tip_radius_report, suture_present)

and the Blender bridge in `_blender.py` (decoration only - build123d keeps every mating feature):

    from tigerbee.accessories import _blender as BL
    part = BL.decorate(base, "elytra_dome", {"rise_span": 0.30},
                       protect=guard, cuts=bores, region=BL.decor_region(base, lig, minus=(guard,)),
                       cache_key=f"side_panel_right__{variant}", wall_floor=1.5)
    # then in checks():  return [*BL.decor_checks(f"side_panel_right__{variant}"), ...]

CLI, per module and per variant:
    uv run python -m tigerbee accessories --only <id> [--variant <name>] [--gallery] [--skip-blender]
    uv run python scripts/verify_accessories.py --only <id> [--variant <name>]

Generic checks run automatically for every label (see accessories.generic_checks): one valid solid,
no frame interference, clear of the Ø6 standoffs (>= 0.2 mm), outside the prop discs above Z 7,
above the landing plane, outside the BATTERY envelope, flat bed face at Z 0, no overhangs > 45 deg
in print orientation.
"""

from build123d import Part

from tigerbee.accessories._common import *  # noqa: F401,F403 - constants, builders and checks

NAME = "_template"
TITLE = "Template accessory"
MATERIAL = "TPU95A"
PRINT = {"template_block": (0, 0, -1)}
EXCLUSIVE = ()
MOUNTS = ("plate_top top face Z 36", "standoff_front_tip_right bolt axis (19, 109)")
HARDWARE = ("1 x M3 x 10 button head (replaces the front-tip standoff bolt)",)
NOTES = "Seats on plate_top over the right front-tip standoff; M3 x 10 replaces the standoff bolt."

# --- parameters (mm) ------------------------------------------------------------------------
T = 6.0
HOLE_D = D_M3_THRU


def build(**overrides) -> dict[str, Part]:
    p = {"T": T, "HOLE_D": HOLE_D, **overrides}
    x, y = STANDOFF_XY["standoff_front_tip_right"]
    block = box(x - 5, y - 5, Z_TOP_TOP, x + 5, y + 5, Z_TOP_TOP + p["T"])
    block -= cylinder(x, y, Z_TOP_TOP - 1, Z_TOP_TOP + p["T"] + 1, p["HOLE_D"])
    return {"template_block": block}


def checks(parts: dict[str, Part], frame: dict[str, Part]) -> list[tuple[str, bool, str]]:
    blk = parts["template_block"]
    xy = STANDOFF_XY["standoff_front_tip_right"]
    ok, detail = coaxial(blk, xy, HOLE_D, Z_TOP_TOP, Z_TOP_TOP + T)
    contact = seats_on(blk, "plate_top", Z_TOP_TOP)
    ok_wall, _v, wall_detail = min_wall(blk, WALL)
    return [
        ("hole coaxial with standoff_front_tip_right", ok, detail),
        ("seated on plate_top at Z 36", contact >= 40, f"{contact} mm² contact"),
        (f"min wall >= {WALL}", ok_wall, wall_detail),
    ]
