"""Build, check, export and preview accessories into dist/accessories/.

Per part (print orientation, bed face on Z 0): {step,stl,3mf,freecad}/<label>.*, preview/<label>.png.
Per module: preview/<id>_installed.png (module parts in red over the grey frame).
When nothing is excluded: tigerbee_with_accessories.{step,stl,3mf,FCStd} (frame + every accessory
installed, exclusive sets resolved) plus preview/tigerbee_with_accessories_{iso,top}.png.
"""

import json
import subprocess
import time
from copy import deepcopy
from pathlib import Path
from types import ModuleType

from build123d import Compound, ExportSVG, Part, Vector

from tigerbee import export as X  # noqa: N812 - import first: patches Mesher for absolute deflection
from tigerbee.accessories import _fit as F
from tigerbee.accessories import attr, build_accessory, discover_accessories, printed, run_checks

RSVG = "/usr/bin/rsvg-convert"
ISO = Vector(1, -1, 0.75)
ASSEMBLY = "tigerbee_with_accessories"


def _bbox(shape) -> list[list[float]]:
    bb = shape.bounding_box()
    return [[round(bb.min.X, 3), round(bb.min.Y, 3), round(bb.min.Z, 3)], [round(bb.max.X, 3), round(bb.max.Y, 3), round(bb.max.Z, 3)]]


def _project(shape, view: str):
    c = shape.center()
    if view == "top":
        return shape.project_to_viewport(c + Vector(0, 0, 1000), viewport_up=(0, 1, 0), look_at=c)[0]
    if view == "front":
        return shape.project_to_viewport(c + Vector(0, 1000, 0), viewport_up=(0, 0, 1), look_at=c)[0]
    return shape.project_to_viewport(c + ISO * 1000, viewport_up=(0, 0, 1), look_at=c)[0]


def render(layers: list[tuple[list, tuple[int, int, int], float]], png: Path, width: int = 1200) -> None:
    """layers: [(edges, rgb, line_weight)] already projected into one common viewport."""
    edges = [e for lay in layers for e in lay[0]]
    if not edges:
        return
    bb = Compound(edges).bounding_box()
    scale = 240 / max(bb.size.X, bb.size.Y, 1e-3)  # drawing ~240 units wide so line weights read the same
    svg = ExportSVG(scale=scale, margin=4, line_weight=0.4)
    for i, (lay, rgb, lw) in enumerate(layers):
        if lay:
            svg.add_layer(f"l{i}", line_color=rgb, line_weight=lw)
            svg.add_shape(lay, f"l{i}")
    svg_path = png.with_suffix(".svg")
    svg.write(svg_path)
    subprocess.run([RSVG, "-w", str(width), "-o", str(png), str(svg_path)], check=True, capture_output=True)
    svg_path.unlink()


def preview_part(part: Part, png: Path) -> None:
    render([(_project(part, "iso"), (30, 30, 30), 0.4)], png)


def preview_installed(acc: list[Part], png: Path, view: str = "iso", width: int = 1800) -> None:
    """Accessories in red over the frame in grey: both projected in the frame's viewport (no
    occlusion between the two layers)."""
    scene = Compound(children=[*deepcopy(list(F.frame_parts().values())), *[deepcopy(p) for p in acc]])
    c = scene.center()
    eye = {"top": (Vector(0, 0, 1000), (0, 1, 0)), "front": (Vector(0, 1000, 0), (0, 0, 1))}.get(view, (ISO * 1000, (0, 0, 1)))
    frame_edges = Compound(children=deepcopy(list(F.frame_parts().values()))).project_to_viewport(c + eye[0], viewport_up=eye[1], look_at=c)[0]
    acc_edges = Compound(children=[deepcopy(p) for p in acc]).project_to_viewport(c + eye[0], viewport_up=eye[1], look_at=c)[0]
    render([(frame_edges, (170, 170, 170), 0.2), (acc_edges, (200, 30, 30), 0.5)], png, width)


def resolve_exclusive(mods: dict[str, ModuleType]) -> tuple[list[str], dict[str, str]]:
    """Alphabetically first id of each exclusive set is installed; returns (installed, {excluded: by})."""
    installed, excluded = [], {}
    for name in sorted(mods):
        blocker = next((i for i in installed if name in attr(mods[i], "EXCLUSIVE") or i in attr(mods[name], "EXCLUSIVE")), None)
        if blocker:
            excluded[name] = blocker
        else:
            installed.append(name)
    return installed, excluded


def export_accessories(dist: Path, only: list[str] | None = None, freecad: bool = True, preview: bool = True,
                       assembly: bool | None = None) -> tuple[dict, bool]:
    """Returns (manifest, all_checks_passed). Files are written even when checks fail."""
    for sub in ("step", "stl", "3mf", "freecad", "preview"):
        (dist / sub).mkdir(parents=True, exist_ok=True)
    assembly = (not only) if assembly is None else assembly
    mods = discover_accessories(None if assembly else only)  # the assembly needs every module
    selected = {n: m for n, m in mods.items() if not only or n in only}
    if not selected:
        print("no accessories found in tigerbee/accessories (modules not starting with '_')")
        return {"accessories": {}, "parts": []}, True
    manifest = {"name": "tigerbee accessories", "datum": "frame coordinates as installed; exported files are in PRINT "
                "orientation (bed face on Z 0, bbox centred in XY)", "mesh": {"linear_deflection_mm": X.LIN, "angular_deflection_rad": X.ANG},
                "accessories": {}, "parts": []}
    all_ok = True
    fcstd_pairs, expected = [], {}
    for name, mod in selected.items():
        t0 = time.time()
        parts = build_accessory(mod)
        results = run_checks(mod, parts)
        ok = all(r[1] for r in results)
        all_ok &= ok
        notes = attr(mod, "NOTES")
        manifest["accessories"][name] = {"title": mod.TITLE, "material": mod.MATERIAL, "labels": list(parts),
                                         "exclusive": list(attr(mod, "EXCLUSIVE")), "passed": ok,
                                         "checks": [{"name": n, "passed": p, "detail": d} for n, p, d in results]}
        for label, part in parts.items():
            p = printed(mod, label, part)
            files = X._write(p, [p], label, dist)
            manifest["parts"].append({
                "label": label, "module": name, "material": mod.MATERIAL, "volume_mm3": round(part.volume, 3),
                "bbox_installed": _bbox(part), "bbox_printed": _bbox(p),
                "print_bed_normal": list(attr(mod, "PRINT").get(label, (0, 0, -1))),
                "notes": notes.get(label, "") if isinstance(notes, dict) else notes,
                "checks": [{"name": n, "passed": pss, "detail": d} for n, pss, d in results if n.startswith(f"{label}:")],
                "files": files,
            })
            fcstd_pairs.append((dist / files["step"], dist / files["freecad"]))
            expected[str((dist / files["freecad"]).resolve())] = 1
            if preview:
                preview_part(p, dist / "preview" / f"{label}.png")
        if preview:
            preview_installed(list(parts.values()), dist / "preview" / f"{name}_installed.png")
        for n, p_, d in results:
            print(f"{'PASS' if p_ else 'FAIL'} {name}: {n} - {d}")
        print(f"{name}: {len(parts)} part(s) {'OK' if ok else 'FAILED'} in {time.time() - t0:.1f} s")
    if assembly:
        installed, excluded = resolve_exclusive(mods)
        acc = []
        for name in installed:
            for label, part in build_accessory(mods[name], **attr(mods[name], "ASSEMBLY_BUILD")).items():
                acc.append(part)
        clashes = []
        for i, a in enumerate(acc):
            for b in acc[i + 1:]:
                if F.bbox_overlap(a, b):
                    v = F.isect(a, b)
                    if v > F.EPS:
                        clashes.append([a.label, b.label, round(v, 3)])
        all_ok &= not clashes
        print(f"assembly: {len(acc)} accessory parts, excluded {excluded or 'none'}, clashes {clashes or 'none'}")
        frame = Compound(children=deepcopy(list(F.frame_parts().values())), label="tigerbee")
        asm = Compound(children=[frame, Compound(children=acc, label="accessories")], label=ASSEMBLY)
        leaves = [*frame.children, *acc]
        files = X._write(asm, leaves, ASSEMBLY, dist)
        manifest["assembly"] = {"installed": installed, "excluded": excluded, "parts": [p.label for p in acc],
                                "checks": [{"name": "no accessory-accessory interference", "passed": not clashes, "detail": str(clashes or "none")}],
                                "files": files}
        fcstd_pairs.append((dist / files["step"], dist / files["freecad"]))
        expected[str((dist / files["freecad"]).resolve())] = len(leaves)
        if preview:
            for view in ("iso", "top"):
                preview_installed(acc, dist / "preview" / f"{ASSEMBLY}_{view}.png", view)
    if freecad and fcstd_pairs:
        for _s, f in fcstd_pairs:
            for old in f.parent.glob(f"{f.stem}.FC*"):
                old.unlink()
        found = X.step_to_fcstd(fcstd_pairs)
        bad = {k: (found.get(k), v) for k, v in expected.items() if found.get(k) != v}
        assert not bad, f"FCStd Part::Feature counts (got, expected): {bad}"
    (dist / "manifest.json").write_text(json.dumps(manifest, indent=1) + "\n")
    return manifest, all_ok
