"""Verify accessories: every module's checks(), the generic checks and the exported files.

Run after `python -m tigerbee accessories`:
    uv run python scripts/verify_accessories.py [--only ID ...] [--variant NAME ...] [--dist DIR]
                                               [--skip-freecad]
Prints PASS/FAIL per check and exits 1 if anything failed. Modules that declare VARIANTS are checked
once per variant, against the labels "<base>__<variant>" the exporter writes.
"""

import argparse
import sys
from pathlib import Path

from build123d import Mesher, import_step, import_stl

from tigerbee import export as X  # noqa: F401,N812 - absolute-deflection mesh patch
from tigerbee.accessories import build_accessory, discover_accessories, printed, run_checks, variant_names
from tigerbee.export import reopen_counts

FAILED = []


def check(ok: bool, msg: str) -> None:
    print(f"{'PASS' if ok else 'FAIL'} {msg}")
    if not ok:
        FAILED.append(msg)


def bbox_close(a, b, tol: float) -> bool:
    return all(abs(getattr(a.min, k) - getattr(b.min, k)) <= tol and abs(getattr(a.max, k) - getattr(b.max, k)) <= tol for k in "XYZ")


def check_variant(args, mod, name: str, vname: str, fcstd: list) -> None:
    """One module, one variant: its checks() plus a round trip of every exported file."""
    tag = f"{name}/{vname}" if vname else name
    parts = build_accessory(mod, vname)
    for n, ok, detail in run_checks(mod, parts, vname):
        check(ok, f"{tag}: {n} - {detail}")
    for label, part in parts.items():
        p = printed(mod, label, part)
        pb = p.bounding_box()
        step, stl, mf = args.dist / "step" / f"{label}.step", args.dist / "stl" / f"{label}.stl", args.dist / "3mf" / f"{label}.3mf"
        if not (step.exists() and stl.exists() and mf.exists()):
            check(False, f"{label}: exported files present (run python -m tigerbee accessories --only {name}"
                         + (f" --variant {vname}" if vname else "") + ")")
            continue
        s = import_step(step)
        check(abs(s.volume - part.volume) <= 0.005 * part.volume and bbox_close(s.bounding_box(), pb, 0.05),
              f"{label}.step round trip in print orientation ({s.volume:.1f} / {part.volume:.1f} mm³)")
        meshes = Mesher().read(mf)
        mb = meshes[0].bounding_box()
        for m in meshes[1:]:
            mb = mb.add(m.bounding_box())
        stl_bb = import_stl(stl).bounding_box()
        check(abs(mb.min.Z) <= 0.05 and bbox_close(mb, stl_bb, 0.05) and bbox_close(mb, pb, 0.05),
              f"{label}.3mf bed on Z 0 and same bbox as the STL (3mf min Z {mb.min.Z:.3f})")
        check(abs(sum(m.volume for m in meshes) - part.volume) <= 0.01 * part.volume, f"{label}.3mf volume within 1 %")
        fcstd.append(args.dist / "freecad" / f"{label}.FCStd")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="+", metavar="ID")
    ap.add_argument("--dist", type=Path, default=Path(__file__).resolve().parents[1] / "dist" / "accessories")
    ap.add_argument("--skip-freecad", action="store_true")
    ap.add_argument("--variant", nargs="+", metavar="NAME",
                    help="style variant(s) to check, for modules that declare VARIANTS")
    args = ap.parse_args()
    mods = discover_accessories(args.only)
    check(bool(mods), f"accessories found: {sorted(mods)}")
    fcstd = []
    for name, mod in mods.items():
        for vname in variant_names(mod, args.variant):
            check_variant(args, mod, name, vname, fcstd)
    if not args.skip_freecad and fcstd:
        present = [f for f in fcstd if f.exists()]
        check(len(present) == len(fcstd), f"{len(present)}/{len(fcstd)} FCStd files present")
        if present:
            rows = {Path(r["out"]).stem: r for r in reopen_counts(present)}
            for f in present:
                check(rows[f.stem]["features"] == 1, f"{f.name}: reopens with {rows[f.stem]['features']} Part::Feature")
    print(f"{'OK' if not FAILED else f'{len(FAILED)} FAILED'}: {sum(1 for _ in mods)} accessories checked, dist = {args.dist}")
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(main())
