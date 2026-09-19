"""python -m tigerbee accessories [--only ID ...] [--dist DIR] [--skip-freecad] [--no-preview] [--assembly]

Builds the selected accessories, runs their checks, exports every part in print orientation,
writes dist/accessories/manifest.json and previews. Exit 1 when any check fails (files are
still written so the failure can be inspected). `python -m tigerbee.accessories` is the same.
"""

import argparse
import sys
from pathlib import Path

from tigerbee.accessories._export import export_accessories


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="tigerbee accessories")
    ap.add_argument("--only", nargs="+", metavar="ID", help="accessory ids (module names) to build")
    ap.add_argument("--dist", type=Path, default=Path(__file__).resolve().parents[3] / "dist" / "accessories")
    ap.add_argument("--skip-freecad", action="store_true")
    ap.add_argument("--no-preview", action="store_true")
    ap.add_argument("--assembly", action="store_true", help="also export the combined assembly with --only")
    args = ap.parse_args(argv)
    manifest, ok = export_accessories(args.dist, only=args.only, freecad=not args.skip_freecad,
                                      preview=not args.no_preview, assembly=True if args.assembly else None)
    n = len(manifest["parts"])
    print(f"{'OK' if ok else 'CHECKS FAILED'}: {len(manifest['accessories'])} accessories, {n} parts -> {args.dist}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
