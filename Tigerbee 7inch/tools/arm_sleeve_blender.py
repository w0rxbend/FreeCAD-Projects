"""Re-measure the six Blender refusals recorded in `arm_sleeve`'s module docstring.

    cd '<repo>' && uv run python tools/arm_sleeve_blender.py

This is evidence, not part of the build: `arm_sleeve` ships both styles as pure build123d, and the
module docstring explains why. The claim it makes is falsifiable, so the measurement that produced it
lives here and can be re-run whenever `_blender.py`, `_bl/recipe.py` or the sleeve's own section
changes. If any row below ever comes back `applied=True` with its wall row ok, the docstring is out of
date and the carapace sleeve should take the decoration.

It is NOT a Blender script - it never runs inside Blender. It drives the bridge from CAD, exactly as
the module would, so every gate that would reject a real decoration rejects it here too.

What is tried, and why each combination is the fair one:
  chitin       axis "X"  the +X flank skin as an isolated sub-solid (finding #1: decorate a simple
                         sub-solid and let CAD reassemble). The flank is the only surface on a
                         U-sleeve with a single outward direction.
  chitin       axis "X"  the whole sleeve, to show that isolating the flank was not the problem.
  chitin       axis "Z"  both, because "Z" is what the design language prescribes for a part lying on
                         the bed - and on this part the outward skin along +Z does not exist.
  elytra_dome  axis "X"  both, the family's own dome recipe at its default rise/span.

Every run is given the full budget the module would give it: wall_floor 1.2 (TPU), tri_budget 12 000,
`restore=False` so the re-boolean is not asked to reassemble anything, and no guard - i.e. the most
permissive setup possible. A refusal here is therefore a property of the geometry, not of the mask.
"""

from __future__ import annotations

from tigerbee.accessories import _blender as BL
from tigerbee.accessories import arm_sleeve as A
from tigerbee.accessories._fit import box

RUNS = (
    ("chitin", {"period": 9.0, "amplitude": 0.75, "axis": "X", "min_nz": 0.5}),
    ("chitin", {"period": 9.0, "amplitude": 0.45, "axis": "Z", "min_nz": 0.5}),
    ("elytra_dome", {"mode": "top", "rise_span": 0.32, "axis": "X", "min_nz": 0.5}),
)


def flank_subsolid(p: dict):
    """The +X flank skin: everything outboard of the D_LIP surface on the right-hand side. Built by
    subtracting the same lofted shell at m = 0, so the cut lands exactly on the style's own minimum
    skin rather than on a guessed plane."""
    lip_shell = A._shell({**p, "SEG_M": (0.0, 0.0), "GROOVE_M": 0.0})
    right = box(0.0, p["Y0"] - 1.0, -p["FLOOR"] - 1.0, 40.0, p["Y1"] + 1.0, p["CARBON_T"] + 1.0)
    return (A._carapace(p) - lip_shell) & right


def main() -> int:
    ok, why = BL.available()
    print(f"blender available: {ok}  ({why})")
    if not ok:
        print("nothing measured - TIGERBEE_BLENDER is empty or blender is missing")
        return 1

    p = A._params({}, "carapace")
    whole = A._carapace(p)
    flank = flank_subsolid(p)
    bb = flank.bounding_box()
    print(f"whole sleeve: {len(whole.solids())} solid(s), {whole.volume:.2f} mm³")
    print(f"flank sub-solid: {len(flank.solids())} solid(s), {flank.volume:.2f} mm³, "
          f"{bb.size.X:.3f} mm thick in X")

    applied = 0
    for recipe, params in RUNS:
        for target, name in ((flank, "flank sub-solid"), (whole, "whole sleeve")):
            if len(target.solids()) != 1:
                print(f"  {recipe:11s} axis={params['axis']} {name:15s} SKIP "
                      f"({len(target.solids())} solids)")
                continue
            r = BL.decorate_ex(target, recipe, params, restore=False, wall_floor=1.2,
                               tri_budget=12_000,
                               cache_key=f"arm_sleeve_probe_{recipe}_{params['axis']}_{name}")
            wall = r.stats.get("wall") or {}
            print(f"  {recipe:11s} axis={params['axis']} {name:15s} applied={r.applied}")
            print(f"      reason      {r.reason}")
            print(f"      volume ratio {r.stats.get('volume_ratio')}  "
                  f"mesh wall {wall.get('min_thickness')} mm at {wall.get('at')} "
                  f"({wall.get('thin_rays')} thin of {wall.get('rays')} rays)")
            applied += int(r.applied)

    print(f"\n{applied} of {2 * len(RUNS)} runs were APPLIED.")
    if applied:
        print("The module docstring says none of them are. Re-read it and re-decide.")
    else:
        print("Matches the docstring: every recipe is refused by a gate, so both styles ship as "
              "pure build123d and every mating check is exact.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
