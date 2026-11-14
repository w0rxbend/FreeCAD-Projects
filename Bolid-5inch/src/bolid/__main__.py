"""bolid check | analyse | export | render | all"""

import sys


def check() -> bool:
    from bolid import accessories as ACC
    from bolid.checks import frame_checks, report

    ok = report(frame_checks())
    bad = 0
    for acc in ACC.build_all():
        rows = ACC.check(acc)
        failed = [r for r in rows if not r[1]]
        bad += len(failed)
        print(f"{acc.name:22s} {len(rows) - len(failed)}/{len(rows)}")
        for r in failed:
            print(f"    FAIL {r[0]}: {r[2]}")
    clashes = ACC.clashes()
    print("accessory clashes:", clashes or "none")
    return ok and not bad and not clashes


def main() -> int:
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    if cmd in ("check", "all") and not check():
        return 1
    if cmd in ("analyse", "all"):
        from bolid import analysis

        print(analysis.tables())
    if cmd in ("export", "all"):
        from bolid.export import export_all

        m = export_all()
        print(f"exported; carbon {m['carbon_mass_g']} g; FreeCAD: {m['freecad']}")
    if cmd in ("render", "all"):
        from bolid.gallery import render_all

        print(f"{len(render_all())} pictures")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
