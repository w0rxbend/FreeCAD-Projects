"""The worked example and smoke test for the Blender decoration bridge.

    uv run python scripts/blender_demo.py [--keep DIR]

It builds a plate-like part with two M3 bores - the same shape class the CARAPACE and CHASSIS recipes
are meant for - decorates it with every recipe that has been measured to survive the full pipeline,
and asserts the things a real accessory asserts: the ligament the lattice promised, the bores still
coaxial, enough seating face to print on, the envelope not grown, one valid solid, and the result
actually exportable. Exits 1 if any of that regresses.

The `round` cell mode is deliberately not exercised: at useful cell sizes its many-sided prisms make a
shell OCCT will not sew into a valid solid (measured), and the gate refuses it. Use `hex` for a
structural field and `voronoi` for a skeletal one.

Read this before writing a decorated accessory; it is the shortest complete statement of the contract.

WHAT IT IS NOT: proof that a recipe works on YOUR part. side_panels is the counter-example - a 1.5 mm
wall carrying clip rings, snap mouths, webs, a USB window and two notches refused every recipe, each
refusal caught by a gate. Decorate thick, closed, plate-like geometry, or decorate a simple sub-solid
and let build123d reassemble the structure around it via `restore`.
"""

import argparse
import sys
import time
from pathlib import Path

from build123d import Axis, Mesher, fillet

from tigerbee import export as X  # noqa: N812 - import first: patches Mesher for absolute deflection
from tigerbee.accessories import _blender as BL
from tigerbee.accessories._fit import Z_TOP_TOP, box, coaxial, cylinder, seats_on, single_solid

WALL_FLOOR = 1.5
BORE_D = 3.4
BORES = ((-22.0, 0.0), (22.0, 0.0))
Z0, Z1 = Z_TOP_TOP, Z_TOP_TOP + 4.0   # a 4 mm plate seated on plate_top

FAILED: list[str] = []


def check(ok: bool, msg: str) -> None:
    print(f"{'PASS' if ok else 'FAIL'} {msg}")
    if not ok:
        FAILED.append(msg)


def build_plate():
    """(part, guard, region_inset_source). The guard is the clean zone: the two bore collars, EXACTLY
    FLUSH with the plate's own faces. A guard proud by even 0.2 mm becomes real material after the
    re-union and breaks the frame interference and overhang checks."""
    plate = fillet(box(-30, -12, Z0, 30, 12, Z1).edges().filter_by(Axis.Z), 3.0)
    cuts = None
    guard = None
    for x, y in BORES:
        b = cylinder(x, y, Z0 - 0.1, Z1 + 0.1, BORE_D)
        g = cylinder(x, y, Z0, Z1, 9.0)          # flush in Z at both ends; padded only radially
        cuts = b if cuts is None else cuts + b
        guard = g if guard is None else guard + g
    return plate - cuts, guard & plate, cuts


# (recipe, params, ngon, target ligament or None, cuts_through)
# `cuts_through` is the difference between "the seating face must be untouched" and "the seating face
# must still be enough to print on": a cell field goes clean through the plate and is SUPPOSED to take
# bed area with it, where a displacement recipe must leave every mating face exactly where it was.
CASES = (
    ("carapace_lattice", {"cell": "voronoi", "ligament": 1.8, "cell_d": 11.0, "seed": 7}, True, 1.8, True),
    ("carapace_lattice", {"cell": "hex", "ligament": 2.0, "cell_d": 9.0, "seed": 5}, True, 2.0, True),
    ("chitin", {"period": 12.0, "amplitude": 0.8}, False, None, False),
)
SEAT_MIN_FRACTION = 0.35   # a through-cut field may take up to 65 % of the bed contact


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--keep", type=Path, help="also write each decorated part as STEP into this dir")
    args = ap.parse_args()

    ok, why = BL.available()
    print(f"blender: {why}")
    if not ok:
        print("Blender unavailable - the bridge's degraded path is what this proves instead.")

    part, guard, cuts = build_plate()
    check(single_solid(part)[0], f"functional plate is one valid solid ({part.volume:.1f} mm³)")
    base_seat = seats_on(part, "plate_top", Z0)
    for x, y in BORES:
        check(coaxial(part, (x, y), BORE_D, Z0 + 0.05, Z1 - 0.05)[0], f"functional bore at ({x}, {y}) coaxial")

    for recipe, params, ngon, ligament, cuts_through in CASES:
        tag = f"{recipe}/{params.get('cell', '-')}"
        t = time.time()
        # PASS THE REGION, not the raw outline: without the inset the recipe clips border cells flush
        # with the silhouette and leaves a knife edge - measured 0.0121 mm against a 1.5 mm floor.
        region = BL.decor_region(part, params.get("ligament", 1.8), minus=(guard,))
        res = BL.decorate_ex(part, recipe, params, protect=guard, cuts=cuts, region=region,
                             cache_key=f"demo_{tag}", wall_floor=WALL_FLOOR, ngon=ngon)
        dt = time.time() - t
        if not ok:
            check(not res.applied and res.part is part,
                  f"{tag}: degraded to the undecorated part - {res.reason[:70]}")
            continue
        check(res.applied, f"{tag}: applied in {dt:.1f} s - {res.reason or 'fresh run'}")
        if not res.applied:
            continue
        st, dec = res.stats, res.part
        check(single_solid(dec)[0], f"{tag}: one valid solid, {st.get('b_rep_faces')} B-rep faces "
                                   f"from {st.get('tris')} triangles")
        for x, y in BORES:
            check(coaxial(dec, (x, y), BORE_D, Z0 + 0.05, Z1 - 0.05)[0],
                  f"{tag}: bore at ({x}, {y}) still coaxial after decoration")
        seat = seats_on(dec, "plate_top", Z0)
        if cuts_through:
            check(seat >= SEAT_MIN_FRACTION * base_seat and seat >= 100.0,
                  f"{tag}: seating face still {seat / base_seat:.0%} of {base_seat:.1f} mm² "
                  f"({seat:.1f} mm², floor {SEAT_MIN_FRACTION:.0%} and 100 mm²)")
        else:
            check(abs(seat - base_seat) <= 0.02 * base_seat,
                  f"{tag}: seating face untouched ({seat:.1f} of {base_seat:.1f} mm²)")
        check(st.get("envelope_growth_mm", 9.0) <= 2.0 + 1e-6,
              f"{tag}: envelope growth {st.get('envelope_growth_mm')} mm <= 2.0")
        measured = (st.get("wall") or {}).get("min_thickness")
        check((st.get("wall") or {}).get("ok") is True,
              f"{tag}: mesh wall {measured} mm >= {WALL_FLOOR} (Blender rays, guard skipped)")
        if ligament is not None and measured is not None:
            # the ligament guarantee is ARITHMETIC: cells of circumradius (D - w)/2 at Poisson
            # separation D leave D - 2r = w, and a Voronoi cell inset by w/2 on every bisector half
            # plane leaves exactly 2 x inset. Measured 1.8 -> 1.7954 and 2.0 -> 1.9949.
            check(measured >= ligament - 0.05,
                  f"{tag}: ligament {measured} mm against the {ligament} mm target (within 0.05)")
        try:
            probe = Mesher()
            probe.add_shape(dec, linear_deflection=X.LIN, angular_deflection=X.ANG, part_number="demo")
            check(True, f"{tag}: exports as a valid 3MF mesh")
        except Exception as exc:  # noqa: BLE001
            check(False, f"{tag}: 3MF export - {exc}")
        if args.keep:
            from build123d import export_step
            args.keep.mkdir(parents=True, exist_ok=True)
            export_step(dec, str(args.keep / f"demo_{recipe}_{params.get('cell', 'x')}.step"))

    print(f"{'OK' if not FAILED else f'{len(FAILED)} FAILED'}: {len(CASES)} recipe case(s), "
          f"cache {BL.CACHE}")
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(main())
