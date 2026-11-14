"""tigerbeetle trace | check | export | render | all

trace   scans -> src/tigerbeetle/data/reconstruction.json (about 5 minutes)
check   every check of the frame and the printed parts
export  exports/: DXF + STEP + STL for the carbon, STL + 3MF + STEP for the prints, assemblies, manifest
render  exports/renders/*.png, the overlays on the scans, exports/GALLERY.md (needs a display or xvfb-run)
all     export, then render
"""

import argparse
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _check() -> bool:
    from tigerbeetle import accessories as A
    from tigerbeetle import checks as C

    ok = C.report(C.frame_checks())
    for acc in A.build_all():
        ok &= C.report([(f"{acc.name}: {n}", p, d) for n, p, d in A.check(acc)])
    clashes = A.clashes()
    ok &= C.report([("no two installed printed parts overlap", not clashes, str(clashes or "none"))])
    print("ALL CHECKS PASSED" if ok else "SOME CHECKS FAILED")
    return ok


def main() -> None:
    ap = argparse.ArgumentParser(
        prog="tigerbeetle", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("command", choices=("trace", "check", "export", "render", "all"))
    ap.add_argument("--out", type=Path, default=ROOT / "exports")
    ap.add_argument("--no-freecad", action="store_true")
    args = ap.parse_args()
    ok = True
    if args.command == "trace":
        from tigerbeetle import trace

        trace.run()
    if args.command == "check":
        ok = _check()
    if args.command in ("export", "all"):
        from zhalo.freecad import find_freecad

        from tigerbeetle.export import export_all

        m = export_all(args.out, None if args.no_freecad else find_freecad())
        print(
            f"exports -> {args.out}: {len(m['carbon'])} carbon parts, {len(m['accessories'])} printed parts, "
            f"{m['mass_g']['carbon']} g of carbon, checks {'passed' if m['all_checks_passed'] else 'FAILED'}"
        )
        ok = m["all_checks_passed"]
    if args.command in ("render", "all"):
        if not os.environ.get("DISPLAY") and shutil.which("xvfb-run") and not os.environ.get("TB_XVFB"):
            os.environ["TB_XVFB"] = "1"
            argv = [a for a in sys.argv[1:] if a != "all"] + ([] if args.command == "render" else [])
            cmd = [
                "xvfb-run",
                "-a",
                "-s",
                "-screen 0 1600x1200x24",
                sys.executable,
                "-m",
                "tigerbeetle",
                "render",
                *[a for a in argv if a != "render"],
            ]
            os.execvp("xvfb-run", cmd)
        from tigerbeetle.previews import render_all

        fit = render_all(args.out / "renders")
        print(f"renders -> {args.out / 'renders'}; fit to the tracing: {fit}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
