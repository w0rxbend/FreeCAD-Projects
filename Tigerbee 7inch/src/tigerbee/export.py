"""STEP / STL / 3MF / FCStd export of the assembly and every part, plus manifest."""

import json
import os
import subprocess
from copy import deepcopy
from pathlib import Path

from OCP.BRepMesh import BRepMesh_IncrementalMesh
from build123d import Compound, Mesher, Part, Unit, export_step, export_stl

from tigerbee import params as P
from tigerbee.frame import PLATES, motor_centers
from tigerbee.mounts import PATTERNS, hole_rows

STEP_TIMESTAMP = "2000-01-01T00:00:00"  # reproducible files
LIN, ANG = 0.02, 0.1  # mesh chord (mm) and angular (rad) deflection
FCSTD_TAG = "FCSTD "
FREECAD_CMD = os.environ.get("FREECAD_CMD", "flatpak run --command=FreeCADCmd org.freecad.FreeCAD").split()


def _mesh(shape) -> None:
    """Triangulate with an absolute deflection. build123d 0.11 meshes with isRelative=True,
    which scales LIN by edge length (2 mm on the 100 mm arm beziers: +0.5 % mesh volume).
    OCCT keeps an existing finer triangulation, so meshing first fixes both STL and 3MF."""
    BRepMesh_IncrementalMesh(shape.wrapped, LIN, False, ANG, True)


_relative_mesh_shape = Mesher._mesh_shape


def _absolute_mesh_shape(shape, linear_deflection, angular_deflection):
    _mesh(shape)  # Mesher.add_shape deep-copies its input (dropping any mesh), then calls this
    return _relative_mesh_shape(shape, linear_deflection, angular_deflection)


Mesher._mesh_shape = staticmethod(_absolute_mesh_shape)


def _write(shape, members: list[Part], name: str, dist: Path) -> dict[str, str]:
    files = {"step": f"step/{name}.step", "stl": f"stl/{name}.stl", "3mf": f"3mf/{name}.3mf",
             "freecad": f"freecad/{name}.FCStd"}
    assert export_step(shape, dist / files["step"], unit=Unit.MM, timestamp=STEP_TIMESTAMP), name
    _mesh(shape)
    assert export_stl(shape, dist / files["stl"], tolerance=LIN, angular_tolerance=ANG, ascii_format=False), name
    mesher = Mesher(unit=Unit.MM)
    for part in members:
        mesher.add_shape(part, linear_deflection=LIN, angular_deflection=ANG, part_number=part.label)
    mesher.add_meta_data("tigerbee", "wheelbase_mm", str(P.WHEELBASE), "float", True)
    mesher.write(dist / files["3mf"])
    return files


# Loop body (for `... out ...:`) that reopens one FCStd, counts its Part::Features and
# closes it again. A reopened document is named after the file stem; closing it keeps the
# next newDocument('tigerbee') from being auto-renamed tigerbee001. Two FreeCADCmd 1.1.3
# quirks shape this: a `-c` script containing a `def` block aborts ("Application
# unexpectedly terminated"), and Python's stdout buffer is not reliably flushed at exit,
# so the result line is flushed explicitly.
_REOPEN = (
    "    re = App.openDocument(out); nm = re.Name\n"
    "    n = len([o for o in re.Objects if o.TypeId == 'Part::Feature']); App.closeDocument(nm)\n"
    f"    print('\\n' + {FCSTD_TAG!r} + json.dumps({{'out': out, 'features': n, 'doc': nm}}), flush=True)\n"
)


def step_to_fcstd(pairs: list[tuple[Path, Path]]) -> dict[str, int]:
    """Convert STEP -> FCStd in one FreeCADCmd run; return {fcstd_path: Part::Feature count}."""
    jobs = json.dumps([[str(s.resolve()), str(f.resolve())] for s, f in pairs])
    code = (
        f"for step, out in json.loads({jobs!r}):\n"
        "    doc = App.newDocument('tigerbee'); Import.insert(step, doc.Name); doc.recompute()\n"
        "    doc.saveAs(out); App.closeDocument(doc.Name)\n" + _REOPEN
    )
    return {row["out"]: row["features"] for row in run_freecad(code, [f for _, f in pairs])}


def reopen_counts(paths: list[Path]) -> list[dict]:
    """Reopen FCStd files in one FreeCADCmd run: [{out, features, doc}]."""
    code = f"for out in json.loads({json.dumps([str(p.resolve()) for p in paths])!r}):\n" + _REOPEN
    return run_freecad(code, paths)


def run_freecad(code: str, expected: list[Path]) -> list[dict]:
    # Paths contain spaces, so results are JSON lines tagged FCSTD; everything else on
    # stdout (recompute progress) and stderr (Fontconfig) is noise.
    res = subprocess.run([*FREECAD_CMD, "-c", "import json, FreeCAD as App, Import\n" + code],
                         check=True, capture_output=True, text=True, timeout=600)
    # FreeCAD's progress output shares the fd and can land on either side of the tag on the
    # same line, so find the tag anywhere and let raw_decode ignore whatever follows the JSON.
    rows = [json.JSONDecoder().raw_decode(line[i + len(FCSTD_TAG):])[0]
            for line in res.stdout.splitlines() if (i := line.find(FCSTD_TAG)) >= 0]
    found = {row["out"] for row in rows}
    missing = [str(p.resolve()) for p in expected if str(p.resolve()) not in found]
    if missing:
        raise RuntimeError(f"FreeCAD did not report: {missing}\n{res.stderr[-2000:]}")
    return rows


def export_all(compound: Compound, parts: dict[str, Part], dist: Path, freecad: bool = True) -> dict:
    for sub in ("step", "stl", "3mf", "freecad"):
        (dist / sub).mkdir(parents=True, exist_ok=True)
    manifest = {
        "name": "tigerbee", "wheelbase_mm": P.WHEELBASE, "root_to_motor_mm": round(P.ROOT_TO_MOTOR, 7),
        "datum": "origin = centre of the central 30.5 stack square; +X right, +Y front, +Z up; "
                 "Z=0 lower face of plate_bottom",
        "motor_centers": {k: [round(v[0], 4), round(v[1], 4)] for k, v in motor_centers().items()},
        "stackup_z": {"plate_bottom": [0, P.PLATE_T], "arms": [P.Z_ARM, P.Z_MID], "plate_mid": [P.Z_MID, P.Z_MID + P.PLATE_T],
                      "plate_top": [P.Z_TOP, P.Z_TOP + P.PLATE_T]},
        "mesh": {"linear_deflection_mm": LIN, "angular_deflection_rad": ANG},
        "assembly": {"files": _write(compound, list(parts.values()), "tigerbee", dist)},
        "parts": [], "holes": hole_rows(), "patterns": PATTERNS,
    }
    for name, part in parts.items():
        solo = deepcopy(part)  # detach from the compound so the assembly is untouched
        solo.parent = None
        solo.label = name
        bb = part.bounding_box()
        manifest["parts"].append({
            "name": name, "volume_mm3": round(part.volume, 3),
            "bbox": [[round(bb.min.X, 3), round(bb.min.Y, 3), round(bb.min.Z, 3)],
                     [round(bb.max.X, 3), round(bb.max.Y, 3), round(bb.max.Z, 3)]],
            "files": _write(solo, [solo], name, dist),
        })
    if freecad:
        for old in (dist / "freecad").glob("*.FC*"):
            old.unlink()  # FreeCAD leaves .FCBak backups when it overwrites a file
        pairs = [(dist / "step" / f"{n}.step", dist / "freecad" / f"{n}.FCStd") for n in ("tigerbee", *parts)]
        found = step_to_fcstd(pairs)
        expected = {str(pairs[0][1].resolve()): len(parts), **{str(f.resolve()): 1 for _, f in pairs[1:]}}
        bad = {k: (found[k], v) for k, v in expected.items() if found[k] != v}
        assert not bad, f"FCStd Part::Feature counts (got, expected): {bad}"
    (dist / "manifest.json").write_text(json.dumps(manifest, indent=1) + "\n")
    return manifest


__all__ = ["export_all", "step_to_fcstd", "reopen_counts", "PLATES"]
