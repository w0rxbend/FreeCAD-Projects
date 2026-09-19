"""python -m tigerbee [--dist DIR] [--skip-freecad]: build, export, write manifest.
python -m tigerbee accessories [...]: see tigerbee.accessories.__main__."""

import argparse
import sys
from pathlib import Path

from tigerbee import params as P
from tigerbee.export import export_all
from tigerbee.frame import build_frame, wheelbase


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "accessories":
        from tigerbee.accessories.__main__ import main as accessories_main
        sys.exit(accessories_main(sys.argv[2:]))
    ap = argparse.ArgumentParser(prog="tigerbee")
    ap.add_argument("--dist", type=Path, default=Path(__file__).resolve().parents[2] / "dist")
    ap.add_argument("--skip-freecad", action="store_true")
    args = ap.parse_args()
    compound, parts = build_frame()
    manifest = export_all(compound, parts, args.dist, freecad=not args.skip_freecad)
    n = len(manifest["parts"]) + 1
    print(f"tigerbee: wheelbase {wheelbase():.4f} mm (target {P.WHEELBASE}), arm L = {P.ROOT_TO_MOTOR:.4f} mm")
    print(f"exported {n} STEP, {n} STL, {n} 3MF" + ("" if args.skip_freecad else f", {n} FCStd") + f" -> {args.dist}")


if __name__ == "__main__":
    main()
