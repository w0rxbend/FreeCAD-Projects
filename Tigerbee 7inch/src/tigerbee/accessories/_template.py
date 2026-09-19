"""TEMPLATE (not discovered: name starts with "_"). Copy to `<id>.py` and fill in.

Contract for `src/tigerbee/accessories/<id>.py`:

  NAME      = "<id>"            must equal the module file name
  TITLE     = "Human title"
  MATERIAL  = "TPU95A" | "PETG"
  PRINT     = {label: (nx, ny, nz)}   bed face normal in FRAME coords (the face that lies on the bed);
                                      labels left out print on their -Z face
  EXCLUSIVE = ("other_id", ...)       optional: cannot be installed together (first id alphabetically
                                      wins in the combined assembly)
  NOTES     = "mounting notes"        optional: str or {label: str}, copied into the manifest
  build(**overrides) -> dict[str, Part]   labelled parts in FRAME coordinates as installed
  checks(parts, frame) -> list[tuple[str, bool, str | float]]   the REQUIRED CHECKS of the spec;
                                      `parts` is what build() returned, `frame` = frame_parts()

Optional knobs (defaults in accessories/__init__.py OPTIONAL_DEFAULTS): MIN_Z, ALLOWED_INTERFERENCE,
OWN_PROP_DISC, BATTERY_OK, BRIDGE_OK, OVERHANG_SKIP, ASSEMBLY_BUILD, and the hook
orient_for_print(label, part) -> Part when PRINT (a single bed normal) cannot express the orientation.

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
