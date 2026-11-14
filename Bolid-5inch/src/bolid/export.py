"""Every file a builder needs: cut files for the carbon, print files for the TPU, assemblies, a manifest."""

import json
import os
import subprocess
import tempfile
from pathlib import Path

from build123d import Compound, ExportDXF, Mesher, Part, Unit, export_step, export_stl

from bolid import accessories as ACC
from bolid import analysis as AN
from bolid import gear as G
from bolid import geometry as GEO
from bolid import params as P
from bolid.checks import CARBON

OUT = Path(__file__).resolve().parents[2] / "exports"
FREECAD = os.environ.get("FREECAD_APPRUN", "")


def _solid_files(part: Part, stem: Path, three_mf: Path | None = None):
    stem.parent.mkdir(parents=True, exist_ok=True)
    export_step(part, str(stem.with_suffix(".step")))
    export_stl(part, str(stem.with_suffix(".stl")), tolerance=0.02, angular_tolerance=0.2)
    if three_mf is not None:
        three_mf.parent.mkdir(parents=True, exist_ok=True)
        m = Mesher(unit=Unit.MM)
        m.add_shape(part, linear_deflection=0.02, angular_deflection=0.2)
        m.write(str(three_mf))


def cut_files() -> list[dict]:
    rows = []
    for key, make in GEO.PLATES.items():
        plate = make()
        stem = OUT / "cnc" / f"{key}_{plate.thickness:g}mm_x{plate.count}"
        stem.parent.mkdir(parents=True, exist_ok=True)
        dxf = ExportDXF(unit=Unit.MM)
        dxf.add_shape(plate.face)
        dxf.write(str(stem.with_suffix(".dxf")))
        _solid_files(plate.solid(), stem)
        area = plate.face.area
        rows.append(
            {
                "part": key,
                "file": stem.name,
                "thickness": plate.thickness,
                "qty": plate.count,
                "area_mm2": round(area, 1),
                "mass_g": round(area * plate.thickness * CARBON, 1),
            }
        )
    return rows


def print_files() -> list[dict]:
    rows = []
    for acc in ACC.build_all():
        bedded = ACC.base.lay_on_bed(acc.part, acc.bed)
        _solid_files(bedded, OUT / "print" / "step" / acc.name, OUT / "print" / "3mf" / f"{acc.name}.3mf")
        (OUT / "print" / "stl").mkdir(parents=True, exist_ok=True)
        os.replace(OUT / "print" / "step" / f"{acc.name}.stl", OUT / "print" / "stl" / f"{acc.name}.stl")
        bb = bedded.bounding_box()
        rows.append(
            {
                "part": acc.name,
                "title": acc.title,
                "qty": acc.qty,
                "material": acc.material,
                "volume_cm3": round(acc.part.volume / 1000, 2),
                "size_mm": [round(bb.size.X, 1), round(bb.size.Y, 1), round(bb.size.Z, 1)],
                "hardware": acc.hardware,
                "notes": acc.notes,
                "in_assembly": acc.in_assembly,
            }
        )
    return rows


def assemblies() -> dict[str, Path]:
    frame = GEO.parts()
    acc = {}
    for a in ACC.assembly():
        for i, p in enumerate((a.part, *a.instances)):
            acc[a.name if i == 0 else f"{a.name}_{i + 1}"] = p
    gear = {n: p for n, (p, _c, _o) in G.build().items()}
    out = OUT / "assembly"
    out.mkdir(parents=True, exist_ok=True)
    files = {}
    for name, parts in (("bolid_frame", frame), ("bolid_complete", {**frame, **acc})):
        comp = Compound(children=[p.moved(p.location) for p in parts.values()])
        _solid_files(comp, out / name)
        files[name] = out / f"{name}.step"
    # one STEP per part for the FreeCAD document
    tmp = Path(tempfile.mkdtemp(prefix="bolid_parts_"))
    groups = {"frame": frame, "accessories": acc, "gear": gear}
    index = []
    for g, parts in groups.items():
        for n, p in parts.items():
            f = tmp / f"{g}__{n}.step"
            export_step(p, str(f))
            index.append({"group": g, "name": n, "file": str(f), "color": _color(g, n)})
    (tmp / "index.json").write_text(json.dumps(index))
    files["index"] = tmp / "index.json"
    return files


def _color(group: str, name: str):
    from bolid.render import PALETTE

    if group == "frame":
        return PALETTE["aluminium" if name.startswith(("spacer", "standoff")) else "carbon"]
    if group == "accessories":
        a = next((x for x in ACC.build_all() if name.startswith(x.name)), None)
        return PALETTE[a.color] if a else PALETTE["tpu"]
    for key in ("motor", "prop", "battery", "camera"):
        if name.startswith(key):
            return PALETTE[key]
    return PALETTE["pcb"]


SCRIPT = r"""
import json, os, sys
import FreeCAD as App, Part
idx, target, result = sys.argv[-3:]
doc = App.newDocument("Bolid")
groups = {}
for row in json.load(open(idx)):
    g = groups.get(row["group"]) or doc.addObject("App::DocumentObjectGroup", row["group"].capitalize())
    groups[row["group"]] = g
    shape = Part.read(row["file"])
    obj = doc.addObject("Part::Feature", row["name"])
    obj.Shape = shape
    g.addObject(obj)
    if App.GuiUp:
        obj.ViewObject.ShapeColor = tuple(row["color"])
        if row["name"].startswith("prop"):
            obj.ViewObject.Transparency = 70
doc.recompute()
doc.saveAs(target)
json.dump({"objects": len(doc.Objects), "gui": App.GuiUp}, open(result, "w"))
os._exit(0)
"""


def freecad_document(index: Path) -> dict:
    """Build Bolid-5inch.FCStd with FreeCAD itself, if FREECAD_APPRUN points at a FreeCAD AppRun."""
    if not FREECAD or not Path(FREECAD).exists():
        return {"skipped": "set FREECAD_APPRUN to a FreeCAD AppRun to build the .FCStd"}
    script = index.parent / "make_fcstd.py"
    script.write_text(SCRIPT)
    target = OUT / "assembly" / "Bolid-5inch.FCStd"
    result = index.parent / "result.json"
    # FreeCAD's GUI takes its script arguments from sys.argv; the last three are ours
    cmd = [
        "xvfb-run",
        "-a",
        "-s",
        "-screen 0 1280x1024x24",
        FREECAD,
        "freecad",
        str(script),
        str(index),
        str(target),
        str(result),
    ]
    subprocess.run(cmd, timeout=900, capture_output=True)
    return json.loads(result.read_text()) if result.exists() else {"error": "FreeCAD wrote no result"}


def manifest(cut: list, prints: list) -> dict:
    arm = AN.chosen()
    return {
        "name": "Bolid 5-inch",
        "units": "mm",
        "datum": "origin = centre of the stack; +X right, +Y front, +Z up; Z = 0 underside of the bottom plate",
        "wheelbase": P.WHEELBASE,
        "prop": {"diameter": P.PROP_D, "margin": P.PROP_MARGIN, "tip_gap": round(P.WHEELBASE / 2**0.5 - P.PROP_D, 1)},
        "motors": {q: [round(v, 3) for v in xy] for q, xy in P.MOTORS.items()},
        "stack_up_z": {
            "plate_bottom": [P.Z_BOT, P.Z_ARM],
            "arms": [P.Z_ARM, P.Z_PRESS],
            "plate_press": [P.Z_PRESS, P.Z_BAY],
            "bay": [P.Z_BAY, P.Z_TOP],
            "plate_top": [P.Z_TOP, P.Z_ROOF],
        },
        "arm": {k: round(v, 1) if isinstance(v, float) else v for k, v in arm.__dict__.items()},
        "carbon": cut,
        "carbon_mass_g": round(sum(r["mass_g"] * r["qty"] for r in cut), 1),
        "printed": prints,
        "accessory_clashes": ACC.clashes(),
    }


def analysis() -> dict:
    data = {
        "model": "Euler-Bernoulli cantilever from the plates' edge to the motor; rigid-body inertia for the wheelbase",
        "E_MPa": AN.E,
        "strength_MPa": AN.STRENGTH,
        "tip_mass_g": AN.TIP_MASS,
        "arms": [r.__dict__ for r in AN.arm_study()],
        "wheelbase": [r.__dict__ for r in AN.wheelbase_study()],
        "chosen_arm": AN.chosen().__dict__,
    }
    (OUT / "analysis").mkdir(parents=True, exist_ok=True)
    (OUT / "analysis" / "studies.json").write_text(json.dumps(data, indent=1))
    (OUT / "analysis" / "studies.txt").write_text(AN.tables() + "\n")
    return data


def export_all() -> dict:
    cut = cut_files()
    prints = print_files()
    files = assemblies()
    analysis()
    m = manifest(cut, prints)
    m["freecad"] = freecad_document(files["index"])
    (OUT / "manifest.json").write_text(json.dumps(m, indent=1))
    return m
