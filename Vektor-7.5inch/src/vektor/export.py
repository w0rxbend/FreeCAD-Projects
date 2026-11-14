"""Every file a builder needs: cut files for the carbon, print files for the TPU, assemblies, a manifest."""

import json
import os
import subprocess
import tempfile
from pathlib import Path

from build123d import Compound, ExportDXF, Mesher, Part, Unit, export_step, export_stl

from vektor import accessories as ACC
from vektor import arm_fe as FE
from vektor import gear as G
from vektor import geometry as GEO
from vektor import params as P
from vektor.checks import CARBON

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
    for name, parts in (("vektor_frame", frame), ("vektor_complete", {**frame, **acc})):
        comp = Compound(children=[p.moved(p.location) for p in parts.values()])
        _solid_files(comp, out / name)
        files[name] = out / f"{name}.step"
    # one STEP per part for the FreeCAD document
    tmp = Path(tempfile.mkdtemp(prefix="vektor_parts_"))
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
    from vektor.render import PALETTE

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
doc = App.newDocument("Vektor")
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
    """Build Vektor-7.5inch.FCStd with FreeCAD itself, if FREECAD_APPRUN points at a FreeCAD AppRun."""
    if not FREECAD or not Path(FREECAD).exists():
        return {"skipped": "set FREECAD_APPRUN to a FreeCAD AppRun to build the .FCStd"}
    script = index.parent / "make_fcstd.py"
    script.write_text(SCRIPT)
    target = OUT / "assembly" / "Vektor-7.5inch.FCStd"
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
    arm = FE.chosen()
    return {
        "name": "Vektor 7.5-inch",
        "units": "mm",
        "datum": "origin = centre of the stack; +X right, +Y front, +Z up; Z = 0 underside of the lower skin",
        "wheelbase": P.WHEELBASE,
        "prop": {"diameter": P.PROP_D, "margin": P.PROP_MARGIN},
        "motors": {q: [round(v, 3) for v in xy] for q, xy in P.MOTORS.items()},
        "stack_up_z": {
            "skin_lower": [P.Z_LOWER, P.Z_LOWER + P.T_SKIN],
            "cavity_webs": [P.Z_LOWER + P.T_SKIN, P.Z_UPPER],
            "skin_upper": [P.Z_UPPER, P.Z_DECK],
            "bay": [P.Z_DECK, P.Z_TOP],
            "plate_top": [P.Z_TOP, P.Z_ROOF],
        },
        "arm": {
            "stiffness_N_per_mm": round(arm.stiffness, 1),
            "allowable_load_N": round(arm.load),
            "first_mode_Hz": round(arm.freq),
            "carbon_g": round(arm.mass, 1),
        },
        "carbon": cut,
        "carbon_mass_g": round(sum(r["mass_g"] * r["qty"] for r in cut), 1),
        "printed": prints,
        "accessory_clashes": ACC.clashes(),
    }


def analysis() -> dict:
    rows = FE.study()
    data = {
        "model": "beam: bending + shear of the webs; the tip pad as a cantilever past the webs",
        "E_MPa": FE.E_CARBON,
        "G_MPa": FE.G_CARBON,
        "strength_MPa": FE.STRENGTH,
        "tip_mass_g": FE.TIP_MASS,
        "rows": [r.__dict__ for r in rows],
        "chosen": FE.chosen().__dict__,
    }
    (OUT / "analysis").mkdir(parents=True, exist_ok=True)
    (OUT / "analysis" / "arm_study.json").write_text(json.dumps(data, indent=1))
    (OUT / "analysis" / "arm_study.txt").write_text(FE.table(rows) + "\n")
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
