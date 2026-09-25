"""Build, check, export and preview accessories into dist/accessories/.

Per part (print orientation, bed face on Z 0): {step,stl,3mf,freecad}/<label>.*, preview/<label>.png.
Per module: preview/<id>_installed.png (module parts in red over the grey frame).
When nothing is excluded: tigerbee_with_accessories.{step,stl,3mf,FCStd} (frame + every accessory
installed, exclusive sets resolved) plus preview/tigerbee_with_accessories_{iso,top,side}.png.
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
from tigerbee.accessories import (attr, base_label, build_accessory, discover_accessories, hardware,
                                 material_of, mounts, print_normal, printed, run_checks, style_name,
                                 variant_names, variants)

RSVG = "/usr/bin/rsvg-convert"
MONTAGE = "/usr/bin/montage"
MAGICK = "/usr/bin/magick"
FONTS = ("/usr/share/fonts/Adwaita/AdwaitaMono-Regular.ttf",
         "/usr/share/fonts/TTF/DejaVuSansMono.ttf",
         "/usr/share/fonts/dejavu/DejaVuSansMono.ttf",
         "/usr/share/fonts/liberation/LiberationMono-Regular.ttf")
ISO = Vector(1, -1, 0.75)
ASSEMBLY = "tigerbee_with_accessories"
GALLERY = "gallery"


def _bbox(shape) -> list[list[float]]:
    bb = shape.bounding_box()
    return [[round(bb.min.X, 3), round(bb.min.Y, 3), round(bb.min.Z, 3)], [round(bb.max.X, 3), round(bb.max.Y, 3), round(bb.max.Z, 3)]]


_FACE_NAMES = {(0, 0, -1): "-Z (underside)", (0, 0, 1): "+Z (top)", (0, -1, 0): "-Y (rear)",
               (0, 1, 0): "+Y (nose)", (-1, 0, 0): "-X (left)", (1, 0, 0): "+X (right)"}


def _print_orientation(normal: tuple, printed_part: Part) -> str:
    """Plain-language print orientation: which FRAME face of the part lies on the bed, and the
    footprint it occupies there. The exported file is already in that orientation."""
    face = _FACE_NAMES.get(tuple(round(c) for c in normal), f"normal {tuple(normal)}")
    bb = printed_part.bounding_box()
    return (f"frame {face} face on the bed; footprint {bb.size.X:.1f} x {bb.size.Y:.1f} mm, "
            f"height {bb.size.Z:.1f} mm")


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
    eye = {"top": (Vector(0, 0, 1000), (0, 1, 0)), "front": (Vector(0, 1000, 0), (0, 0, 1)),
           "side": (Vector(1000, 0, 0), (0, 0, 1))}.get(view, (ISO * 1000, (0, 0, 1)))
    frame_edges = Compound(children=deepcopy(list(F.frame_parts().values()))).project_to_viewport(c + eye[0], viewport_up=eye[1], look_at=c)[0]
    acc_edges = Compound(children=[deepcopy(p) for p in acc]).project_to_viewport(c + eye[0], viewport_up=eye[1], look_at=c)[0]
    render([(frame_edges, (170, 170, 170), 0.2), (acc_edges, (200, 30, 30), 0.5)], png, width)


def silhouette(part: Part, png: Path, view: str = "auto", width: int = 200) -> None:
    """The thumbnail gate: a small orthographic outline of one part. A style variant is not done
    until its row of thumbnails is visibly several different SHAPES - the brief is variety, so the
    style has to change the plan outline first and the surface treatment second.

    "auto" picks whichever of the three orthographic views shows the most of the part. The plan view
    is the right one for a plate and useless for a side panel, which in plan is a 12 mm sliver."""
    if view == "auto":
        best, edges = -1.0, None
        for v in ("top", "front", "iso"):
            e = _project(part, v)
            if not e:
                continue
            bb = Compound(e).bounding_box()
            area = bb.size.X * bb.size.Y
            if area > best:
                best, edges = area, e
    else:
        edges = _project(part, view)
    if edges:
        render([(edges, (0, 0, 0), 1.2)], png, width)
        fill_silhouette(png)


def fill_silhouette(png: Path) -> bool:
    """Turn a rendered outline into a FILLED black shape on white, in place.

    The gate is about the plan outline, and an outline drawing passes it on interior detail alone -
    two variants with the same silhouette and different vents look different on paper and identical
    in the hand. Filling throws the detail away and leaves the shape.

    Flatten onto white FIRST (the SVG's transparent background has RGB 0, so a flood fill started in
    it spreads through a field of black and the thumbnail comes back blank), flood the exterior with
    a marker colour, call everything that is not the marker black, then the marker white."""
    if not png.is_file() or not Path(MAGICK).is_file():
        return False
    try:
        subprocess.run([MAGICK, str(png), "-background", "white", "-alpha", "remove", "-alpha", "off",
                        "-colorspace", "gray", "-threshold", "62%", "-colorspace", "sRGB",
                        "-type", "TrueColor", "-fill", "red", "-draw", "color 0,0 floodfill",
                        "-fuzz", "12%", "-fill", "black", "+opaque", "red",
                        "-fill", "white", "-opaque", "red", str(png)], check=True, capture_output=True)
    except (subprocess.CalledProcessError, OSError):
        return False   # a missing ImageMagick costs a nicer thumbnail, never an export
    return True


def contact_sheet(pngs: list[Path], out: Path, columns: int = 0, label: bool = True,
                  tile: int = 300) -> bool:
    """Assemble previews into one sheet with ImageMagick `montage`, so the variety can be reviewed at
    a glance. Returns False (and writes nothing) when montage is absent - a missing contact sheet is
    a convenience lost, never a failed export."""
    pngs = [p for p in pngs if p.is_file()]
    if not pngs or not Path(MONTAGE).is_file():
        return False
    columns = columns or min(5, max(1, len(pngs)))
    rows = -(-len(pngs) // columns)
    cmd = [MONTAGE, "-background", "white", "-fill", "#222", "-pointsize", "13",
           "-tile", f"{columns}x{rows}", "-geometry", f"{tile}x{tile}+6+6"]
    # name the font explicitly: this box's fontconfig is broken, so montage reserved the label band
    # and then drew nothing in it - a sheet of anonymous thumbnails is no use to a reviewer
    font = next((f for f in FONTS if Path(f).is_file()), None)
    if font and label:
        cmd += ["-font", font]
    for p in pngs:
        # short, two-line labels: the thumbnail prefix carries no information and a one-line
        # "sil_side_panel_right__carapace" is wider than its own 200 px tile and collides with its
        # neighbour's
        name = p.stem[4:] if p.stem.startswith("sil_") else p.stem
        cmd += (["-label", name.replace("__", "\n")] if label else []) + [str(p)]
    cmd.append(str(out))
    subprocess.run(cmd, check=True, capture_output=True)
    return True


def gallery(dist: Path, families: dict[str, list[str]], width: int = 300) -> dict[str, str]:
    """One contact sheet per accessory (its variants side by side), one silhouette sheet per
    accessory (the thumbnail gate) and one sheet for the whole set. Returns {name: relative path}."""
    out_dir = dist / GALLERY
    out_dir.mkdir(parents=True, exist_ok=True)
    made: dict[str, str] = {}
    hero: list[Path] = []
    for name, labels in sorted(families.items()):
        shots = [dist / "preview" / f"{lab}.png" for lab in labels]
        sheet = out_dir / f"{name}.png"
        if contact_sheet(shots, sheet, tile=width):
            made[name] = str(sheet.relative_to(dist))
            hero.append(shots[0])
        sils = [dist / GALLERY / f"sil_{lab}.png" for lab in labels]
        sil_sheet = out_dir / f"{name}_silhouettes.png"
        if contact_sheet(sils, sil_sheet, tile=200):
            made[f"{name}_silhouettes"] = str(sil_sheet.relative_to(dist))
    whole = out_dir / "tigerbee_accessories.png"
    if contact_sheet(hero, whole, columns=5, tile=width):
        made["all"] = str(whole.relative_to(dist))
    return made


def kits(mods: dict[str, ModuleType]) -> dict[str, list[str]]:
    """What a user actually picks: for every style family, the variants that together make a coherent
    set - `<accessory>:<variant>`, with " (fallback)" wherever the family has no reading on that part
    (`_style.MATRIX`) or the module does not ship it, and the kit borrowed another style.

    The taste is `_style.KITS`; this reconciles it against what the modules ACTUALLY build, because a
    manifest that names a label nobody exports is worse than no manifest. A module whose variant
    declares a style the matrix refuses on that part is still listed - it exists, so a user can pick
    it - just marked as the fallback it is."""
    from tigerbee.accessories import _style as S
    out: dict[str, list[str]] = {}
    for family in S.STYLES:
        picked = []
        for name in sorted(mods):
            vs = variants(mods[name])
            if not vs:
                # a module with no VARIANTS still belongs in the quad - it has exactly one build, and
                # leaving it out of the kit would tell a user their set is missing a part
                picked.append(f"{name} (fallback)")
                continue
            # A variant may be FUNCTIONAL rather than stylistic - motor_guard ships stock/tall/
            # sprung/bellows, camera pods ship tilt angles. Those names are not style families, and
            # feeding one to kit_pick used to raise and take the whole export down with it. Keep
            # them as their own pool: they are still pickable, they just have no family opinion.
            by_style, functional = {}, []
            for v, spec in vs.items():
                key = spec.get("style") or v
                (by_style.setdefault(key, v) if key in S.STYLES else functional.append(v))
            style, fb = S.kit_pick(name, family, tuple(by_style))
            chosen = by_style.get(style) or (functional[0] if functional else next(iter(vs)))
            picked.append(f"{name}:{chosen}"
                          + (" (fallback)" if fb or style not in by_style else ""))
        if picked:
            out[family] = picked
    return out


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


def _stance_check(acc: list[Part]) -> tuple[str, bool, str]:
    """How the assembled quad stands on the ground: which parts reach the lowest plane, and whether
    those contact points make a stable, level stance rather than a tripod.

    This is the only place the WHOLE set is compared at once. It caught (and now guards against) a
    set whose tail bar hung 5.2 mm below the four landing feet, so the quad rested on the bar plus
    the two front feet, ~1.9 deg nose-up, carrying every touchdown on a 2.0 mm TPU groove floor."""
    lows = {}
    for p in acc:
        v = min(p.vertices(), key=lambda q: q.Z)
        lows[p.label] = (round(v.Z, 3), round(v.X, 2), round(v.Y, 2))
    if not lows:
        return ("assembly stands level on its ground contacts", True, "no accessories installed")
    plane = min(z for z, _x, _y in lows.values())
    touch = {l: (x, y) for l, (z, x, y) in lows.items() if abs(z - plane) < 0.05}
    xs = [x for x, _y in touch.values()]
    ys = [y for _x, y in touch.values()]
    ok = len(touch) >= 3 and min(xs) < 0 < max(xs) and min(ys) < 0 < max(ys)
    nearly = {l: z for l, (z, _x, _y) in lows.items() if 0.05 <= z - plane <= 6.0}
    return ("assembly stands level on its ground contacts", ok,
            f"ground plane Z {plane}; {len(touch)} contact point(s) {sorted(touch)} spanning "
            f"x {min(xs, default=0)}..{max(xs, default=0)}, y {min(ys, default=0)}..{max(ys, default=0)}"
            + (f"; within 6 mm of the plane but not touching: {nearly}" if nearly else ""))


def _merge_manifest(path: Path, fresh: dict, rebuilt: set[str]) -> dict:
    """Fold a `--only` run's rows into the manifest already on disk instead of replacing it.

    A `--only` run knows about its own accessories and nothing else, so writing its manifest
    straight out threw away every other accessory's entry - the file then claimed the set was one
    accessory long. The rebuilt ids are replaced, the rest are kept, and the recorded assembly is
    flagged stale (this run did not rebuild it, so it may no longer match the rebuilt parts)."""
    try:
        prev = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return fresh
    if not isinstance(prev, dict) or not prev.get("accessories"):
        return fresh
    out = {**prev, **{k: v for k, v in fresh.items() if k not in ("accessories", "parts", "assembly", "kits")}}
    out["accessories"] = {**prev.get("accessories", {}), **fresh["accessories"]}
    out["parts"] = [p for p in prev.get("parts", []) if p.get("module") not in rebuilt] + fresh["parts"]
    if merged_kits := {**prev.get("kits", {}), **fresh.get("kits", {})}:
        out["kits"] = merged_kits
    if "assembly" in fresh:
        out["assembly"] = fresh["assembly"]
    elif "assembly" in prev:
        # ACCUMULATE: successive `--only` runs each used to overwrite stale_reason with their own id
        # alone, so a tree rebuilt four times claimed only the last one was out of date. The
        # previously recorded ids are kept and this run's are added.
        was = set(prev["assembly"].get("stale_parts") or [])
        touched = sorted((rebuilt | was) & set(prev["assembly"].get("installed", [])))
        out["assembly"] = {**prev["assembly"],
                           "stale": bool(touched),
                           "stale_parts": touched,
                           "stale_reason": (f"{', '.join(touched)} rebuilt since; re-run "
                                            "`python -m tigerbee accessories --assembly`" if touched else "")}
    return out


def export_accessories(dist: Path, only: list[str] | None = None, freecad: bool = True, preview: bool = True,
                       assembly: bool | None = None, variant: str | list[str] | None = None,
                       want_gallery: bool = False) -> tuple[dict, bool]:
    """Returns (manifest, all_checks_passed). Files are written even when checks fail.

    `variant` selects one style variant of every selected module (unknown names raise rather than
    silently building everything); `want_gallery` also writes the contact sheets under gallery/."""
    for sub in ("step", "stl", "3mf", "freecad", "preview"):
        (dist / sub).mkdir(parents=True, exist_ok=True)
    if want_gallery:
        (dist / GALLERY).mkdir(parents=True, exist_ok=True)
    assembly = (not only) if assembly is None else assembly
    mods = discover_accessories(None if assembly else only)  # the assembly needs every module
    selected = {n: m for n, m in mods.items() if not only or n in only}
    if not selected:
        print("no accessories found in tigerbee/accessories (modules not starting with '_')")
        return {"accessories": {}, "parts": []}, True
    manifest = {"name": "tigerbee accessories", "datum": "frame coordinates as installed; exported files are in PRINT "
                "orientation (bed face on Z 0, bbox centred in XY)", "mesh": {"linear_deflection_mm": X.LIN, "angular_deflection_rad": X.ANG},
                "volume_source": "volume_mm3 is measured on the installed build123d solid. A STEP "
                "round trip can read up to ~0.1 % different on a MIRRORED part (OCCT integrates the "
                "mirrored NURBS parametrisation differently; re-tessellating the round-tripped STEP "
                "gives identical mesh volumes for each mirrored pair, so the geometry is symmetric). "
                "STL/3MF volumes are mesh volumes and read slightly high on curved parts.",
                "freecad": {"regenerated_this_run": bool(freecad),
                            "note": "" if freecad else "--skip-freecad: freecad/*.FCStd were NOT "
                            "rebuilt and may be older than the step/stl/3mf beside them"},
                "accessories": {}, "parts": []}
    if not freecad:
        print("WARNING --skip-freecad: freecad/*.FCStd are left as they are and may now be stale; "
              "re-run without --skip-freecad before publishing")
    all_ok = True
    fcstd_pairs, expected = [], {}
    families: dict[str, list[str]] = {}
    for name, mod in selected.items():
        t0 = time.time()
        notes = attr(mod, "NOTES")
        entry = {"title": mod.TITLE, "material": mod.MATERIAL, "labels": [],
                 "exclusive": list(attr(mod, "EXCLUSIVE")), "passed": True, "checks": [],
                 "variants": {}, "mounts_to": [], "hardware": [],
                 "failed_checks": 0, "failed_variants": []}
        manifest["accessories"][name] = entry
        for vname in variant_names(mod, variant):
            parts = build_accessory(mod, vname)
            results = run_checks(mod, parts, vname)
            ok = all(r[1] for r in results)
            all_ok &= ok
            entry["passed"] &= ok
            if not ok:
                entry["failed_checks"] += sum(1 for r in results if not r[1])
                entry["failed_variants"].append(vname or "default")
            entry["labels"] += list(parts)
            entry["checks"] += [{"name": n, "passed": p, "detail": d} for n, p, d in results]
            spec = variants(mod).get(vname) or {}
            if vname:
                entry["variants"][vname] = {
                    "style": style_name(mod, vname), "material": material_of(mod, vname),
                    "labels": list(parts), "passed": ok, "notes": spec.get("notes", ""),
                    "params": {k: str(v) for k, v in (spec.get("params") or {}).items()},
                }
            families.setdefault(name, []).extend(parts)
            for label, part in parts.items():
                p = printed(mod, label, part)
                files = X._write(p, [p], label, dist)
                mts, hw = mounts(mod, label), hardware(mod, label)
                entry["mounts_to"] += [m for m in mts if m not in entry["mounts_to"]]
                entry["hardware"] += [h for h in hw if h not in entry["hardware"]]
                manifest["parts"].append({
                    "label": label, "base_label": base_label(label), "module": name,
                    "title": mod.TITLE, "variant": vname,
                    "style": style_name(mod, vname), "material": material_of(mod, vname),
                    "volume_mm3": round(part.volume, 3),
                    "bbox_installed": _bbox(part), "bbox_printed": _bbox(p),
                    "print_bed_normal": list(print_normal(mod, label)),
                    "print_orientation": _print_orientation(print_normal(mod, label), p),
                    "mounts_to": mts, "hardware": hw,
                    "notes": notes.get(label, notes.get(base_label(label), "")) if isinstance(notes, dict) else notes,
                    "checks": [{"name": n, "passed": pss, "detail": d} for n, pss, d in results if n.startswith(f"{label}:")],
                    "files": files,
                })
                fcstd_pairs.append((dist / files["step"], dist / files["freecad"]))
                expected[str((dist / files["freecad"]).resolve())] = 1
                if preview:
                    preview_part(p, dist / "preview" / f"{label}.png")
                if want_gallery:
                    silhouette(part, dist / GALLERY / f"sil_{label}.png")
            if preview:
                suffix = f"_{vname}" if vname else ""
                preview_installed(list(parts.values()), dist / "preview" / f"{name}{suffix}_installed.png")
            for n, p_, d in results:
                print(f"{'PASS' if p_ else 'FAIL'} {name}{'/' + vname if vname else ''}: {n} - {d}")
            print(f"{name}{'/' + vname if vname else ''}: {len(parts)} part(s) {'OK' if ok else 'FAILED'}")
        # Say what actually failed. Printing the module's whole label count on any failure read as
        # "36 parts are broken" when it was one check on one variant, with the other 18 parts green.
        bad = entry.get("failed_checks", 0)
        verdict = ("OK" if entry["passed"] else
                   f"FAILED ({bad} check(s) in {len(entry.get('failed_variants', ())) or 1} variant(s))")
        print(f"{name}: {len(entry['labels'])} part(s) over {len(entry['variants']) or 1} variant(s) "
              f"{verdict} in {time.time() - t0:.1f} s")
    if assembly:
        installed, excluded = resolve_exclusive(mods)
        acc, alternatives, bom, builds = [], {}, {}, {}
        for name in installed:
            mod = mods[name]
            av = attr(mod, "ASSEMBLY_VARIANT") or (next(iter(variants(mod)), "") or "")
            want = attr(mod, "ASSEMBLY_LABELS")  # () = the module's parts are a set, install all
            over = attr(mod, "ASSEMBLY_BUILD")
            # Record HOW each leaf was built. Without this a reader cross-checking the assembly
            # against the part files saw an unexplained size difference wherever the assembly used a
            # different variant or a build override, with nothing in the manifest to explain it.
            builds[name] = {"variant": av, "overrides": {k: str(v) for k, v in over.items()},
                            "matches_part_file": not over}
            for label, part in build_accessory(mod, av, **over).items():
                if want and base_label(label) not in want:
                    alternatives.setdefault(name, []).append(label)  # an alternative, not a sibling
                    continue
                acc.append(part)
                bom.setdefault(name, [])
                bom[name] += [r for r in hardware(mod, label) if r not in bom[name]]
        clashes = []
        for i, a in enumerate(acc):
            for b in acc[i + 1:]:
                if F.bbox_overlap(a, b):
                    v = F.isect(a, b)
                    if v > F.EPS:
                        clashes.append([a.label, b.label, round(v, 3)])
        stance = _stance_check(acc)
        all_ok &= not clashes and stance[1]
        print(f"{'PASS' if stance[1] else 'FAIL'} assembly: {stance[0]} - {stance[2]}")
        print(f"assembly: {len(acc)} accessory parts, excluded {excluded or 'none'}, "
              f"alternatives left out {alternatives or 'none'}, clashes {clashes or 'none'}")
        frame = Compound(children=deepcopy(list(F.frame_parts().values())), label="tigerbee")
        asm = Compound(children=[frame, Compound(children=acc, label="accessories")], label=ASSEMBLY)
        leaves = [*frame.children, *acc]
        files = X._write(asm, leaves, ASSEMBLY, dist)
        manifest["assembly"] = {
            "installed": installed, "excluded": excluded, "alternatives_left_out": alternatives,
            "builds": builds,
            "parts": [p.label for p in acc],
            "hardware": bom,
            "checks": [{"name": "no accessory-accessory interference", "passed": not clashes,
                        "detail": str(clashes or "none")},
                       {"name": stance[0], "passed": stance[1], "detail": stance[2]}],
            "files": files,
            "file_notes": {
                "3mf": f"{len(leaves)} named objects, each watertight - the printable/importable form",
                "step": "one named assembly tree: tigerbee (frame parts) + accessories",
                "stl": f"REFERENCE ONLY, not printable: STL has no object concept, so the {len(leaves)} "
                       "solids are written into one mesh and touching parts (sleeves on arms, guards "
                       "on arm roots) weld at shared vertices, leaving non-manifold edges. Print from "
                       "the per-part files; every one of those is watertight.",
                "FCStd": f"{len(leaves)} labelled Part::Features"}}
        fcstd_pairs.append((dist / files["step"], dist / files["freecad"]))
        expected[str((dist / files["freecad"]).resolve())] = len(leaves)
        if preview:
            for view in ("iso", "top", "side"):
                preview_installed(acc, dist / "preview" / f"{ASSEMBLY}_{view}.png", view)
    if freecad and fcstd_pairs:
        # X.step_to_fcstd removes each target just before its own chunk converts it, so a FreeCADCmd
        # crash can no longer leave freecad/ empty (it did: every FCStd was unlinked up front, and the
        # one oversized -c script then aborted before writing a single document).
        found = X.step_to_fcstd(fcstd_pairs)
        bad = {k: (found.get(k), v) for k, v in expected.items() if found.get(k) != v}
        assert not bad, f"FCStd Part::Feature counts (got, expected): {bad}"
    ks = kits(selected)
    if ks:
        manifest["kits"] = ks
    # the design intent as well as the reconciliation: `kits` is what this build can actually give
    # you, `kits_design` is the style x accessory matrix's own answer, whether or not a module for
    # that accessory exists yet. A user reading the manifest wants both.
    from tigerbee.accessories import _style as _S
    manifest["kits_design"] = {f: list(labels) for f, labels in _S.KITS.items()}
    if want_gallery:
        manifest["gallery"] = gallery(dist, families)
        print(f"gallery: {len(manifest['gallery'])} sheet(s) -> {dist / GALLERY}")
    written = _merge_manifest(dist / "manifest.json", manifest, set(selected)) if only else manifest
    (dist / "manifest.json").write_text(json.dumps(written, indent=1) + "\n")
    return manifest, all_ok
