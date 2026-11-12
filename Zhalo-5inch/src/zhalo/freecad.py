"""Build exports/assembly/Zhalo-5inch.FCStd with FreeCAD itself.

Each solid is handed over as an exact BREP file and becomes a Part::Feature in its installed
position, grouped as Carbon / Standoffs / TPU accessories / Equipment. The document is a
model to look at and measure; the Python code stays the source of truth.

Colours live in FreeCAD's view providers, which only exist when its GUI is up. Run the GUI
binary on a virtual display to get them (FREECAD_CMD="xvfb-run -a freecad"); the console
binary (freecadcmd) writes the same solids without colours.
"""

import json
import os
import shlex
import shutil
import subprocess
import tempfile
from pathlib import Path

from build123d import export_brep

from zhalo import accessories as A
from zhalo import equipment as E
from zhalo import frame as F
from zhalo.render import COLORS

SCRIPT = r"""
import json, os, sys
import FreeCAD as App, Part
job = json.load(open(JOB))
result = {"gui": bool(App.GuiUp)}
try:
    doc = App.newDocument("Zhalo5")
    groups = {}
    for item in job["items"]:
        grp = groups.get(item["group"])
        if grp is None:
            grp = doc.addObject("App::DocumentObjectGroup", "Group%d" % len(groups))
            grp.Label = item["group"]
            groups[item["group"]] = grp
        obj = doc.addObject("Part::Feature", item["name"])
        obj.Label = item["name"]
        obj.Shape = Part.read(item["brep"])
        grp.addObject(obj)
        view = getattr(obj, "ViewObject", None)
        if view is not None:
            view.ShapeColor = tuple(item["color"])
            view.Transparency = int(item["transparency"])
            view.Visibility = bool(item["visible"])
    doc.recompute()
    doc.saveAs(job["out"])
    App.closeDocument(doc.Name)
    check = App.openDocument(job["out"])
    solids = [o for o in check.Objects if o.TypeId == "Part::Feature"]
    result["features"] = len(solids)
    result["invalid"] = [o.Name for o in solids if o.Shape.isNull() or not o.Shape.isValid()]
    App.closeDocument(check.Name)
except Exception as exc:  # the caller reads this file, not our stdout (the GUI swallows it)
    result["error"] = repr(exc)
json.dump(result, open(job["result"], "w"))
os._exit(0)  # the GUI would otherwise stay open waiting for a user
"""


def find_freecad() -> list[str] | None:
    """Command that starts FreeCAD, from $FREECAD_CMD or the usual binary names."""
    env = os.environ.get("FREECAD_CMD")
    if env:
        return shlex.split(env)
    for name in ("freecad", "FreeCAD", "freecadcmd", "FreeCADCmd"):
        if shutil.which(name):
            return [name]
    return None


def items() -> list[dict]:
    out = []
    for name, (part, material) in F.build().items():
        group = "Standoffs" if material == F.ALUMINIUM else "Carbon"
        out.append(
            {"name": name, "group": group, "part": part, "color": COLORS[material], "transparency": 0, "visible": True}
        )
    for acc in A.build_all():
        for i, part in enumerate([acc.part, *acc.instances]):
            out.append(
                {
                    "name": acc.name if i == 0 else f"{acc.name}_{i + 1}",
                    "group": "TPU accessories",
                    "part": part,
                    "color": COLORS["tpu"],
                    "transparency": 0,
                    "visible": acc.in_assembly,
                }
            )
    for name, (part, color, opacity) in E.build().items():
        out.append(
            {
                "name": name,
                "group": "Equipment (reference only)",
                "part": part,
                "color": COLORS[color],
                "transparency": 70 if opacity < 1 else 0,
                "visible": not name.startswith(("prop_", "battery")),
            }
        )
    return out


def write_document(path: Path, freecad_cmd: list[str]) -> dict:
    todo = items()
    with tempfile.TemporaryDirectory() as tmp:
        job = {"out": str(path.resolve()), "items": []}
        for item in todo:
            brep = Path(tmp) / f"{item['name']}.brep"
            assert export_brep(item["part"], brep), brep
            job["items"].append({**{k: v for k, v in item.items() if k != "part"}, "brep": str(brep)})
        job["result"] = str(Path(tmp) / "result.json")
        job_path = Path(tmp) / "job.json"
        job_path.write_text(json.dumps(job))
        script = Path(tmp) / "build_document.py"
        script.write_text(f"JOB = {str(job_path)!r}\n" + SCRIPT)
        for old in path.parent.glob(f"{path.stem}.FC*"):
            old.unlink()
        res = subprocess.run([*freecad_cmd, str(script)], capture_output=True, text=True, timeout=900)
        done = Path(job["result"])
        if not done.exists():
            raise RuntimeError(
                f"FreeCAD did not report back (exit {res.returncode}):\n{res.stdout[-1500:]}\n{res.stderr[-1500:]}"
            )
        result = json.loads(done.read_text())
    assert "error" not in result and result["features"] == len(todo) and not result["invalid"], result
    return {"file": f"assembly/{path.name}", **result}
