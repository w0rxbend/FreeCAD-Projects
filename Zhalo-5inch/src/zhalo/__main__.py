"""zhalo check | export | render | all | analyse

check   run every geometry check (frame, accessories, accessory against accessory)
export  write exports/: DXF + STEP for the carbon, STL + 3MF + STEP for the prints, assemblies, manifest
render  write exports/renders/*.png (needs the `render` extra and a display; xvfb-run is used if there is none)
all     export, then render
analyse structural sizing of the arm: beam model, plus a finite-element check if the `fea` extra is installed
"""

import argparse
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = "zhalo"  # what `python -m` must start to rebuild this design; a sibling design passes its own


def _check() -> bool:
    from zhalo import accessories as A
    from zhalo import checks as C
    from zhalo.export import accessory_clashes

    ok = C.report(C.frame_checks())
    for acc in A.build_all():
        rows = [(f"{acc.name}: {n}", passed, d) for n, passed, d in A.check(acc)]
        ok &= C.report(rows)
    clashes = accessory_clashes()
    ok &= C.report([("no two installed accessories overlap", not clashes, str(clashes or "none"))])
    print("ALL CHECKS PASSED" if ok else "SOME CHECKS FAILED")
    return ok


def _export(out: Path, freecad: bool) -> bool:
    from zhalo.export import export_all
    from zhalo.freecad import find_freecad

    cmd = find_freecad() if freecad else None
    if freecad and cmd is None:
        print("FreeCAD not found (set FREECAD_CMD): skipping the .FCStd document")
    manifest = export_all(out, cmd)
    n_print = len(manifest["accessories"])
    print(
        f"exports -> {out}: {len(manifest['carbon'])} carbon parts, {n_print} printed parts, "
        f"{manifest['mass_g']['carbon']} g of carbon, checks {'passed' if manifest['all_checks_passed'] else 'FAILED'}"
    )
    return manifest["all_checks_passed"]


def _render(out: Path) -> bool:
    if not os.environ.get("DISPLAY") and shutil.which("xvfb-run") and not os.environ.get("ZHALO_XVFB"):
        os.environ["ZHALO_XVFB"] = "1"  # re-run once under a virtual display
        xvfb = ["xvfb-run", "-a", "-s", "-screen 0 1600x1200x24"]
        os.execvp("xvfb-run", [*xvfb, sys.executable, "-m", PACKAGE, *sys.argv[1:]])
    from zhalo.previews import render_all

    files = render_all(out / "renders")
    print(f"renders -> {out / 'renders'}: {len(files)} images")
    return True


def _analyse(out: Path, prog: str) -> bool:
    import json

    from zhalo import design, structure
    from zhalo import params as P

    edge = P.ARM_BOLT_U[1] + P.LEG_R
    arm = structure.Arm(
        prog,
        P.T_ARM,
        P.ARM_LEN - edge,
        lambda x: 2 * P.arm_half_width(x + edge),
        pad=P.ARM_NECK_BACK,
        tip_mass=design.TIP_MASS,
    )
    beam = structure.analyse(arm)
    print(structure.table([beam]))
    result = {"design": prog, "material": structure.MATERIAL.__dict__, "beam": beam.__dict__}
    folder = out / "analysis"
    folder.mkdir(parents=True, exist_ok=True)
    try:
        import gmsh  # noqa: F401 - needs the system library libGLU
        import skfem  # noqa: F401

        from zhalo import fea
    except (ImportError, OSError) as exc:
        print(f"finite-element check skipped: {exc}")
    else:
        if not os.environ.get("DISPLAY") and shutil.which("xvfb-run") and not os.environ.get("ZHALO_XVFB"):
            os.environ["ZHALO_XVFB"] = "1"  # the stress pictures need a display
            xvfb = ["xvfb-run", "-a", "-s", "-screen 0 1600x1200x24"]
            os.execvp("xvfb-run", [*xvfb, sys.executable, "-m", PACKAGE, *sys.argv[1:]])
        report, data = fea.analyse(prog)
        result["fea"] = report.as_dict()
        for case in ("vertical", "side"):
            fea.plot(data, folder / f"stress_{case}.png", case)
        v, h = report.vertical, report.side
        print(
            f"FEA: vertical {v.load:.0f} N at the allowable ({v.stiffness:.0f} N/mm), side {h.load:.0f} N "
            f"({h.stiffness:.0f} N/mm), frequencies {', '.join(f'{f:.0f}' for f in report.frequencies[:3])} Hz"
        )
    (folder / "analysis.json").write_text(json.dumps(result, indent=1, default=str) + "\n")
    print(f"analysis -> {folder}")
    return True


def main(root: Path = ROOT, prog: str = "zhalo") -> None:
    global PACKAGE
    PACKAGE = prog
    ap = argparse.ArgumentParser(prog=prog, description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=("check", "export", "render", "all", "analyse"))
    ap.add_argument("--out", type=Path, default=root / "exports")
    ap.add_argument("--no-freecad", action="store_true", help="do not write the FreeCAD document")
    args = ap.parse_args()
    ok = True
    if args.command == "check":
        ok = _check()
    if args.command in ("export", "all"):
        ok = _export(args.out, not args.no_freecad)
    if args.command in ("render", "all"):
        ok &= _render(args.out)
    if args.command == "analyse":
        ok = _analyse(args.out, prog)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
