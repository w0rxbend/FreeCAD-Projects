"""Native FreeCAD documents generated from the build123d STEP outputs.

The worker uses FreeCAD's own Python interpreter. It intentionally imports no
build123d modules, so the two CAD kernels never share a process.
"""

import importlib
import json
import shutil
import subprocess
from importlib.resources import files
from pathlib import Path


def write_documents(directory: str) -> None:
    """Execute inside FreeCADCmd; reopen every saved file before reporting success."""
    app = importlib.import_module("FreeCAD")
    part = importlib.import_module("Part")
    importer = importlib.import_module("Import")
    root = Path(directory)
    results = []
    sources = sorted((root / "parts").glob("*.step"))
    sources += sorted((root / "assembly").glob("*.step"))
    sources += sorted((root / "accessories").glob("*.step"))
    if not sources:
        raise ValueError(f"No STEP builds found in {root}")
    for source in sources:
        is_assembly = source.parent.name == "assembly"
        metadata = source.parent / (
            "assembly-report.json" if is_assembly else f"{source.stem}.json"
        )
        data = json.loads(metadata.read_text())
        is_assembly = is_assembly or data.get("solid_count", 1) > 1
        document = app.newDocument("TigerbeeExport")
        document.Label = source.stem
        if is_assembly:
            importer.insert(str(source), document.Name)
        else:
            obj = document.addObject("PartDesign::Feature", "Component")
            obj.Label = source.stem
            obj.Shape = part.read(str(source))
        info = document.addObject("App::FeaturePython", "BuildInformation")
        info.addProperty("App::PropertyString", "Source", "Build123d")
        info.Source = "Generated from build123d; edit Python parameters and rebuild."
        info.addProperty("App::PropertyString", "Parameters", "Build123d")
        info.Parameters = json.dumps(data["parameters"], sort_keys=True)
        if "design_dimensions_mm" in data:
            info.addProperty("App::PropertyString", "DesignDimensions", "Build123d")
            info.DesignDimensions = json.dumps(data["design_dimensions_mm"], sort_keys=True)
            info.addProperty("App::PropertyString", "MountingCoordinates", "Build123d")
            info.MountingCoordinates = json.dumps(data["mounting_hole_centers_mm"])
        info.addProperty("App::PropertyString", "FitStatus", "Build123d")
        info.FitStatus = data.get("status", data.get("reference_status", "unspecified"))
        document.recompute()
        destination = source.with_suffix(".FCStd")
        document.saveAs(str(destination))
        app.closeDocument(document.Name)
        reopened = app.openDocument(str(destination))
        shapes = [
            obj.Shape
            for obj in reopened.Objects
            if obj.isDerivedFrom("Part::Feature") and not obj.Shape.isNull()
        ]
        valid = bool(shapes) and all(shape.isValid() for shape in shapes)
        solids = sum(len(shape.Solids) for shape in shapes)
        expected = data.get("solid_count", 15 if is_assembly else 1)
        if not valid or solids != expected:
            raise ValueError(f"FreeCAD verification failed: {destination}, solids={solids}")
        results.append(
            {
                "file": str(destination.relative_to(root)),
                "valid": valid,
                "solids": solids,
                "volume_mm3": sum(shape.Volume for shape in shapes),
            }
        )
        app.closeDocument(reopened.Name)
        print("Verified native document:", destination)
    (root / "native-report.json").write_text(json.dumps(results, indent=2) + "\n")


def export_native(directory: Path) -> list[dict]:
    """Find the native or Flatpak CLI, convert, and require a fresh verification report."""
    command = next(
        (
            [path]
            for name in ("FreeCADCmd", "freecadcmd", "/usr/lib/freecad/bin/freecadcmd-python3")
            if (path := shutil.which(name))
        ),
        None,
    )
    if command is None and shutil.which("flatpak"):
        probe = subprocess.run(["flatpak", "info", "org.freecad.FreeCAD"], capture_output=True)
        if probe.returncode == 0:
            command = ["flatpak", "run", "--command=FreeCADCmd", "org.freecad.FreeCAD"]
    if command is None:
        raise RuntimeError(
            "Install FreeCADCmd or the org.freecad.FreeCAD Flatpak for native export"
        )
    root = directory.resolve()
    report_path = root / "native-report.json"
    report_path.unlink(missing_ok=True)
    worker = str(files("tigerbee").joinpath("native.py"))
    script = (
        f"import runpy\nworker = runpy.run_path({worker!r})\n"
        f"worker['write_documents']({str(root)!r})\nexit()\n"
    )
    result = subprocess.run(command, input=script, text=True, capture_output=True, timeout=180)
    if result.returncode != 0 or not report_path.is_file():
        raise RuntimeError(
            "Native export failed:\n" + result.stdout[-4000:] + result.stderr[-4000:]
        )
    from tigerbee.inventory import write_inventory

    write_inventory(root)
    return json.loads(report_path.read_text())
