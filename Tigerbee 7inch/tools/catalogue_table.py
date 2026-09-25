"""Regenerate the README's accessory catalogue table from the modules themselves.

Run: uv run python tools/catalogue_table.py
The table lives between the HTML markers below, so it is replaced wholesale rather than edited
by hand. A table maintained by hand goes stale the day someone adds a module; this one cannot.
"""

import re
from pathlib import Path

from tigerbee.accessories import attr, discover_accessories, variants

ROOT = Path(__file__).resolve().parents[1]
START, END = "<!-- catalogue:start -->", "<!-- catalogue:end -->"


def row(name: str, mod) -> str:
    vs = list(variants(mod)) or []
    parts = len(mod.build()) if not vs else len(mod.build(vs[0])) * len(vs)
    # MOUNTS is a flat tuple of phrases in most modules and a {label: (phrase, ...)} dict in the
    # few that mount their parts in different places; accept both rather than making them agree.
    mounts = attr(mod, "MOUNTS") or ()
    if isinstance(mounts, dict):
        seats = [m[0] if isinstance(m, (list, tuple)) else str(m) for m in mounts.values()]
    else:
        seats = [str(m) for m in mounts]
    where = re.sub(r"\s+", " ", seats[0])[:58] if seats else ""
    excl = ", ".join(attr(mod, "EXCLUSIVE") or ()) or "—"
    return (f"| `{name}` | {mod.TITLE} | {mod.MATERIAL} | {parts} | "
            f"{', '.join(vs) if vs else 'single'} | {where} | {excl} |")


def main() -> None:
    mods = discover_accessories()
    lines = ["| id | what it is | material | parts | variants | mounts to | exclusive with |",
             "|---|---|---|---|---:|---|---|"]
    for name in sorted(mods):
        try:
            lines.append(row(name, mods[name]))
        except Exception as exc:  # noqa: BLE001  a module mid-edit must not block the table
            why = str(exc)[:40]
            lines.append(f"| `{name}` | {mods[name].TITLE} | — | — | — | (not built: {why}) | — |")
    table = "\n".join(lines)
    readme = (ROOT / "README.md").read_text()
    block = f"{START}\n\n{table}\n\n{END}"
    if START in readme:
        readme = re.sub(re.escape(START) + r".*?" + re.escape(END), block, readme, flags=re.S)
    else:
        readme = readme.rstrip() + "\n\n### Catalogue\n\n" + block + "\n"
    (ROOT / "README.md").write_text(readme)
    print(f"{len(mods)} modules written to README.md")


if __name__ == "__main__":
    main()
