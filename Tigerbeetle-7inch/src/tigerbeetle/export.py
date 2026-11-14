"""exports/: what a CNC shop, a printer and FreeCAD need, all from the same model.

cnc/          each carbon part: DXF (cut outline, mm), STEP, STL
print/        each printed part on its bed face: STL, 3MF, STEP
assembly/     the frame and the complete quad: STEP, STL; the FreeCAD document
manifest.json masses, bolts, standoffs, checks, how closely the model follows the tracing
"""

import json
import subprocess
import tempfile
from pathlib import Path

import ezdxf
from build123d import Compound, ExportDXF, Unit, export_brep
from zhalo import design
from zhalo.accessories.kit import lay_on_bed
from zhalo.export import ASSEMBLY_ANG, ASSEMBLY_LIN, DENSITY, TPU_DENSITY, write_3mf, write_step, write_stl
from zhalo.freecad import SCRIPT

from tigerbeetle import accessories as A
from tigerbeetle import checks as C
from tigerbeetle import equipment as E
from tigerbeetle import frame as F
from tigerbeetle import model as M

SHEETS = {
    "plate_bottom": ("bottom_plate", 1),
    "plate_camera": ("camera_plate", 1),
    "plate_top": ("top_plate", 1),
    "arm": ("arm", 4),
}


def sheet(name: str) -> M.Part2D:
    key, _n = SHEETS[name]
    return M.arms()["front_right"][1] if key == "arm" else M.plates()[key]


def file_stem(name: str) -> str:
    part = sheet(name)
    n = SHEETS[name][1]
    return f"{name}_{part.thickness:g}mm" + (f"_x{n}" if n > 1 else "")


def write_dxf(name: str, path: Path) -> None:
    previous = ezdxf.options.write_fixed_meta_data_for_testing
    ezdxf.options.write_fixed_meta_data_for_testing = True
    try:
        dxf = ExportDXF(unit=Unit.MM)
        dxf.add_layer("CUT")
        dxf.add_shape(F.face(sheet(name)), layer="CUT")
        dxf.write(path)
    finally:
        ezdxf.options.write_fixed_meta_data_for_testing = previous


def _bbox(shape) -> list[float]:
    bb = shape.bounding_box()
    return [round(v, 2) for v in (bb.size.X, bb.size.Y, bb.size.Z)]


def freecad_items() -> list[dict]:
    colors = design.colors()
    out = []
    for name, (part, material) in F.build().items():
        out.append(
            {
                "name": name,
                "group": "Standoffs" if material == F.ALUMINIUM else "Carbon",
                "part": part,
                "color": colors[material],
                "transparency": 0,
                "visible": True,
            }
        )
    for acc in A.build_all():
        for i, part in enumerate((acc.part, *acc.instances)):
            out.append(
                {
                    "name": acc.name if i == 0 else f"{acc.name}_{i + 1}",
                    "group": "Printed parts",
                    "part": part,
                    "color": colors[acc.color],
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
                "color": colors[color],
                "transparency": 70 if opacity < 1 else 0,
                "visible": not name.startswith(("prop_", "battery")),
            }
        )
    return out


def write_document(path: Path, cmd: list[str]) -> dict:
    todo = freecad_items()
    with tempfile.TemporaryDirectory() as tmp:
        job = {"out": str(path.resolve()), "items": [], "document": "Tigerbeetle"}
        for item in todo:
            brep = Path(tmp) / f"{item['name']}.brep"
            assert export_brep(item["part"], brep), brep
            job["items"].append({**{k: v for k, v in item.items() if k != "part"}, "brep": str(brep)})
        job["result"] = str(Path(tmp) / "result.json")
        (Path(tmp) / "job.json").write_text(json.dumps(job))
        script = Path(tmp) / "build.py"
        script.write_text(f"JOB = {str(Path(tmp) / 'job.json')!r}\n" + SCRIPT)
        for old in path.parent.glob(f"{path.stem}.FC*"):
            old.unlink()
        res = subprocess.run([*cmd, str(script)], capture_output=True, text=True, timeout=900)
        done = Path(job["result"])
        if not done.exists():
            raise RuntimeError(f"FreeCAD did not report back (exit {res.returncode}): {res.stderr[-1500:]}")
        result = json.loads(done.read_text())
    assert "error" not in result and result["features"] == len(todo) and not result["invalid"], result
    return {"file": f"assembly/{path.name}", **result}


def export_all(out: Path, freecad_cmd: list[str] | None = None) -> dict:
    for sub in ("cnc", "print/stl", "print/3mf", "print/step", "assembly"):
        (out / sub).mkdir(parents=True, exist_ok=True)
    rows = C.frame_checks()
    acc_rows = {a.name: A.check(a) for a in A.build_all()}
    clashes = A.clashes()
    passed = all(r[1] for r in rows) and all(r[1] for rs in acc_rows.values() for r in rs) and not clashes
    manifest: dict = {
        "name": design.NAME,
        "units": "mm",
        "source": "references/Scan_1.jpeg and Scan_2.jpeg: the owner's parts traced on A4 at 300 dpi",
        "datum": "origin = centre of the 30.5 stack; +X right, +Y front (camera), +Z up; "
        "Z = 0 underside of the bottom plate",
        "stack_up_z": {
            "plate_bottom": [M.Z_BOTTOM, M.Z_ARM],
            "arms": [M.Z_ARM, M.Z_CAMERA],
            "plate_camera": [M.Z_CAMERA, M.Z_CAMERA + M.T_PLATE],
            "plate_top": [M.Z_TOP, M.Z_TOP + M.T_PLATE],
        },
        "motors": {k: [round(v[0], 2), round(v[1], 2)] for k, v in F.motors().items()},
        "standoffs": {
            k: {"xy": [round(v[0], 2), round(v[1], 2)], "z0": v[2], "height": v[3]} for k, v in F.standoffs().items()
        },
        "bolts": {
            g: {"xy": [round(m[0][1].x, 2), round(m[0][1].y, 2)], "plates": {n: h.d for n, h in m}}
            for g, m in M.bolts().items()
        },
        "carbon": [],
        "accessories": [],
        "checks": {"frame": [list(r) for r in rows], "clashes": clashes},
        "all_checks_passed": passed,
    }
    for name in SHEETS:
        stem = file_stem(name)
        write_dxf(name, out / "cnc" / f"{stem}.dxf")
        solid = F.solid(sheet(name))
        write_step(solid, out / "cnc" / f"{stem}.step")
        write_stl(solid, out / "cnc" / f"{stem}.stl")
        manifest["carbon"].append(
            {
                "part": name,
                "qty": SHEETS[name][1],
                "thickness_mm": sheet(name).thickness,
                "mass_g_each": round(solid.volume * C.CARBON_DENSITY, 1),
                "size": _bbox(solid),
                "file": f"cnc/{stem}.dxf",
            }
        )
    for acc in A.build_all():
        printed = lay_on_bed(acc.part, acc.bed)
        write_stl(printed, out / "print" / "stl" / f"{acc.name}.stl")
        write_3mf(printed, out / "print" / "3mf" / f"{acc.name}.3mf")
        write_step(printed, out / "print" / "step" / f"{acc.name}.step")
        manifest["accessories"].append(
            {
                "name": acc.name,
                "title": acc.title,
                "material": acc.material,
                "qty": acc.qty,
                "mass_g_each": round(acc.part.volume * DENSITY.get(acc.material, TPU_DENSITY), 1),
                "print_size": _bbox(printed),
                "in_assembly": acc.in_assembly,
                "hardware": acc.hardware,
                "notes": acc.notes,
                "checks": [list(r) for r in acc_rows[acc.name]],
            }
        )
    frame = Compound(children=list(F.parts().values()), label="tigerbeetle_frame")
    prints = [p for a in A.assembly() for p in (a.part, *a.instances)]
    complete = Compound(children=[*F.parts().values(), *prints], label="tigerbeetle_complete")
    for stem, shape in (("tigerbeetle_frame", frame), ("tigerbeetle_complete", complete)):
        write_step(shape, out / "assembly" / f"{stem}.step")
        write_stl(shape, out / "assembly" / f"{stem}.stl", ASSEMBLY_LIN, ASSEMBLY_ANG)
    mass = {
        "carbon": round(sum(c["mass_g_each"] * c["qty"] for c in manifest["carbon"]), 1),
        "standoffs": round(
            sum(p.volume for n, (p, m) in F.build().items() if m == F.ALUMINIUM) * C.ALUMINIUM_DENSITY, 1
        ),
    }
    manifest["mass_g"] = mass
    if freecad_cmd:
        manifest["freecad"] = write_document(out / "assembly" / "Tigerbeetle-7inch.FCStd", freecad_cmd)
    (out / "manifest.json").write_text(json.dumps(manifest, indent=1) + "\n")
    return manifest
