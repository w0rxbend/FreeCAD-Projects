"""Write everything a build needs into exports/.

cnc/       flat carbon parts: DXF (true arcs and lines, mm) and STEP, one file per part
print/     TPU parts in print orientation: STL, 3MF and STEP
assembly/  the frame alone and the complete quad as STEP, plus a FreeCAD document
manifest.json  dimensions, masses, hole tables, bill of materials and every check result
"""

import json
import struct
from copy import deepcopy
from pathlib import Path

import numpy as np
from build123d import Compound, ExportDXF, Mesher, Part, Unit, export_step
from OCP.BRepMesh import BRepMesh_IncrementalMesh

from zhalo import accessories as A
from zhalo import checks as C
from zhalo import design
from zhalo import equipment as E
from zhalo import frame as F
from zhalo import params as P
from zhalo.accessories.kit import MATERIAL, lay_on_bed

STEP_TIME = "2000-01-01T00:00:00"  # fixed stamp: regenerating gives the same file
MESH_LIN, MESH_ANG = 0.02, 0.1
TPU_DENSITY = 1.21e-3  # g / mm3


def write_stl(part: Part, path: Path) -> int:
    """Binary STL from a fixed-deflection tessellation; returns the triangle count."""
    verts, tris = part.tessellate(MESH_LIN, MESH_ANG)
    v = np.array([(p.X, p.Y, p.Z) for p in verts], dtype="<f4")
    t = np.array(tris, dtype=int)
    a, b, c = v[t[:, 0]], v[t[:, 1]], v[t[:, 2]]
    n = np.cross(b - a, c - a)
    length = np.linalg.norm(n, axis=1)
    n[length > 0] /= length[length > 0][:, None]
    rec = np.zeros(len(t), dtype=[("n", "<f4", 3), ("a", "<f4", 3), ("b", "<f4", 3), ("c", "<f4", 3), ("attr", "<u2")])
    rec["n"], rec["a"], rec["b"], rec["c"] = n, a, b, c
    with path.open("wb") as fh:
        fh.write(f"{design.SLUG} {path.stem}".encode().ljust(80, b" "))
        fh.write(struct.pack("<I", len(t)))
        fh.write(rec.tobytes())
    return len(t)


def write_3mf(part: Part, path: Path) -> None:
    # build123d meshes with a deflection relative to edge length; triangulate first with an
    # absolute one (OCCT keeps the finer mesh) so large-radius arcs are not left coarse
    BRepMesh_IncrementalMesh(part.wrapped, MESH_LIN, False, MESH_ANG, True)
    mesher = Mesher(unit=Unit.MM)
    mesher.add_shape(part, linear_deflection=MESH_LIN, angular_deflection=MESH_ANG, part_number=part.label)
    mesher.write(path)


def write_step(shape, path: Path) -> None:
    assert export_step(shape, path, unit=Unit.MM, timestamp=STEP_TIME), path


def write_dxf(sheet: F.Sheet, path: Path) -> None:
    dxf = ExportDXF(unit=Unit.MM)
    dxf.add_layer("CUT")
    dxf.add_shape(sheet.face(), layer="CUT")
    dxf.write(path)


def _bbox(shape) -> list[float]:
    bb = shape.bounding_box()
    return [round(v, 2) for v in (bb.size.X, bb.size.Y, bb.size.Z)]


def sheet_file(name: str) -> str:
    sheet = F.SHEETS[name]()
    count = f"_x{sheet.count}" if sheet.count > 1 else ""
    return f"{name}_{sheet.thickness:g}mm{count}"


def bill_of_materials() -> dict:
    if design.BOM is not None:
        return design.BOM()
    thick = P.T_BOTTOM + P.T_ARM + P.T_MID  # the sandwich
    return {
        "carbon": [
            {
                "part": n,
                "qty": F.SHEETS[n]().count,
                "thickness_mm": F.SHEETS[n]().thickness,
                "file": f"cnc/{sheet_file(n)}.dxf",
            }
            for n in F.SHEETS
        ],
        "standoffs": [
            {
                "item": f"M3 x {P.STACK_STANDOFF_H:g} mm round standoff, OD {P.STANDOFF_OD:g}",
                "qty": 4,
                "where": "stack corners, on the mid plate",
            },
            {
                "item": f"M3 x {P.BAY_STANDOFF_H:g} mm round standoff, OD {P.STANDOFF_OD:g}",
                "qty": 4,
                "where": "front and rear bay, on the bottom plate",
            },
        ],
        "screws": [
            {
                "item": "M3 x 30 (with the stack) + M3 nut",
                "qty": 4,
                "where": f"stack bolts: through the {thick:g} mm sandwich, nut on the deck, then the stack",
            },
            {"item": "M3 x 16 button head", "qty": 4, "where": "inner arm bolts, from below into the 28 mm standoffs"},
            {"item": "M3 x 14 button head + nyloc", "qty": 4, "where": "outer arm bolts, nut on the mid plate"},
            {
                "item": "M3 x 8 button head",
                "qty": 12,
                "where": "bay standoffs from below (4) and all standoffs from above (8)",
            },
            {"item": "M3 x 12 button head + nyloc", "qty": 4, "where": "braces to the arm lugs"},
            {"item": "M3 x 8", "qty": 16, "where": "motors (16 x 16 mm pattern)"},
        ],
    }


def export_all(out: Path, freecad_cmd: list[str] | None = None) -> dict:
    for sub in ("cnc", "print/stl", "print/3mf", "print/step", "assembly"):
        (out / sub).mkdir(parents=True, exist_ok=True)
    manifest: dict = {
        "name": design.NAME,
        "units": "mm",
        "datum": "origin = centre of the 30.5 stack; +X right, +Y front, +Z up; Z = 0 underside of the bottom plate",
        "wheelbase": P.WHEELBASE,
        "motors": {k: [round(v[0], 3), round(v[1], 3)] for k, v in P.MOTORS.items()},
        "prop": {"diameter": P.PROP_D, "margin": P.PROP_MARGIN},
        "stack_up_z": {
            "plate_bottom": [P.Z_BOTTOM, P.Z_ARM],
            "arms": [P.Z_ARM, P.Z_MID],
            "plate_mid": [P.Z_MID, P.Z_DECK],
            "standoffs_stack": [P.Z_DECK, P.Z_TOP],
            "standoffs_bay": [P.Z_ARM, P.Z_TOP],
            "plate_top": [P.Z_TOP, P.Z_ROOF],
            "braces": [P.Z_BRACE, P.Z_ARM],
        },
        "equipment": {
            "stack": "SpeedyBee F405 V3/V4 + BLS 4-in-1, 30.5 x 30.5 M3",
            "vtx": "analog, 20 x 20 or 30.5 x 30.5 M3, rear bay",
            "camera": "19 mm micro (22 mm mini variant)",
            "battery": list(E.BATTERY_SIZE),
        },
        "carbon": [],
        "accessories": [],
        "bom": bill_of_materials(),
    }

    masses = C.mass()
    for name, make in F.SHEETS.items():
        sheet = make()
        stem = sheet_file(name)
        write_dxf(sheet, out / "cnc" / f"{stem}.dxf")
        write_step(sheet.solid(), out / "cnc" / f"{stem}.step")
        each = sheet.solid().volume * C.CARBON_DENSITY
        manifest["carbon"].append(
            {
                "part": name,
                "qty": sheet.count,
                "thickness": sheet.thickness,
                "size": _bbox(sheet.face())[:2],
                "mass_g_each": round(each, 1),
                "files": [f"cnc/{stem}.dxf", f"cnc/{stem}.step"],
                "holes": [
                    {"name": h.name, "purpose": h.purpose, "x": round(h.x, 3), "y": round(h.y, 3), "d": h.d}
                    for h in sheet.holes
                ],
            }
        )
    manifest["mass_g"] = {
        "carbon": round(sum(v for k, v in masses.items() if not k.startswith("standoff")), 1),
        "standoffs": round(sum(v for k, v in masses.items() if k.startswith("standoff")), 1),
    }

    frame_rows = C.frame_checks()
    manifest["frame_checks"] = [{"name": n, "passed": ok, "detail": d} for n, ok, d in frame_rows]
    all_ok = all(r[1] for r in frame_rows)

    installed: list[Part] = []
    for acc in A.build_all():
        rows = A.check(acc)
        all_ok &= all(r[1] for r in rows)
        printed = lay_on_bed(acc.part, acc.bed)
        printed.label = acc.name
        tris = write_stl(printed, out / "print/stl" / f"{acc.name}.stl")
        write_3mf(printed, out / "print/3mf" / f"{acc.name}.3mf")
        write_step(printed, out / "print/step" / f"{acc.name}.step")
        manifest["accessories"].append(
            {
                "name": acc.name,
                "title": acc.title,
                "module": acc.module,
                "material": MATERIAL,
                "qty": acc.qty,
                "mass_g_each": round(acc.part.volume * TPU_DENSITY, 1),
                "print_size": _bbox(printed),
                "triangles": tris,
                "hardware": acc.hardware,
                "notes": acc.notes,
                "in_assembly": acc.in_assembly,
                "files": [f"print/stl/{acc.name}.stl", f"print/3mf/{acc.name}.3mf", f"print/step/{acc.name}.step"],
                "checks": [{"name": n, "passed": ok, "detail": d} for n, ok, d in rows],
            }
        )
        if acc.in_assembly:
            installed += [acc.part, *acc.instances]

    clashes = accessory_clashes()
    manifest["accessory_clashes"] = clashes
    all_ok &= not clashes
    manifest["all_checks_passed"] = bool(all_ok)

    frame_parts = [deepcopy(p) for p in F.parts().values()]
    write_step(
        Compound(children=frame_parts, label=f"{design.SLUG}_frame"), out / "assembly" / f"{design.SLUG}_frame.step"
    )
    acc_parts = []
    for i, p in enumerate(installed):
        q = deepcopy(p)
        q.label = p.label if p.label else f"accessory_{i}"
        acc_parts.append(q)
    complete = Compound(
        children=[
            Compound(children=[deepcopy(p) for p in F.parts().values()], label="frame"),
            Compound(children=acc_parts, label="accessories"),
        ],
        label=f"{design.SLUG}_complete",
    )
    write_step(complete, out / "assembly" / f"{design.SLUG}_complete.step")

    if freecad_cmd:
        from zhalo.freecad import write_document

        manifest["freecad"] = write_document(out / "assembly" / f"{design.DOCUMENT}.FCStd", freecad_cmd)
    (out / "manifest.json").write_text(json.dumps(manifest, indent=1) + "\n")
    return manifest


def accessory_clashes() -> list[list]:
    """Pairs of installed accessories that share volume (there must be none)."""
    placed = []
    for acc in A.assembly():
        placed.append((acc.name, acc.part))
        placed += [(f"{acc.name}#{i + 2}", p) for i, p in enumerate(acc.instances)]
    out = []
    for i, (na, pa) in enumerate(placed):
        for nb, pb in placed[i + 1 :]:
            v = C.overlap(pa, pb)
            if v > C.EPS:
                out.append([na, nb, round(v, 3)])
    return out
