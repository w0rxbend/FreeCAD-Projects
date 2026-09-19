"""Executed inside FreeCADCmd, whose Python runtime supplies FreeCAD and Import.

This file deliberately has no dependency on the fpv_frame package or build123d.
"""

import importlib
import json
import math
import os
from pathlib import Path
from typing import Any


def run() -> None:
    FreeCAD = importlib.import_module("FreeCAD")
    Import = importlib.import_module("Import")

    job = json.loads(Path(os.environ["FPV_FREECAD_JOB"]).read_text(encoding="utf-8"))
    output = Path(job["output"])
    document = FreeCAD.newDocument("Tigerbeetle")
    Import.insert(job["step"], document.Name)
    document.recompute()

    def inspect(doc: Any) -> list[dict[str, Any]]:
        components = []
        for obj in doc.Objects:
            if not hasattr(obj, "Shape") or obj.Shape.isNull():
                continue
            shape = obj.Shape
            if not shape.isValid():
                raise RuntimeError(f"Invalid FreeCAD shape: {obj.Label}")
            if not shape.Solids:
                continue
            # Imported STEP assembly compounds reference their physical children.
            # Count leaves once, while still checking every aggregate shape above.
            if any(hasattr(child, "Shape") and not child.Shape.isNull()
                   for child in obj.OutList):
                continue
            components.append(
                {"name": obj.Label, "solids": len(shape.Solids), "volume_mm3": shape.Volume}
            )
        if not components:
            raise RuntimeError("FreeCAD STEP import contains no solids")
        return components

    before = inspect(document)
    document.addObject("App::FeaturePython", "Provenance")
    provenance = document.getObject("Provenance")
    provenance.addProperty("App::PropertyString", "SourceOfTruth")
    provenance.SourceOfTruth = "fpv-frame build123d Python model; FCStd is an interchange artifact"
    document.recompute()
    document.saveAs(str(output))
    FreeCAD.closeDocument(document.Name)
    reopened = FreeCAD.openDocument(str(output))
    reopened.recompute()
    after = inspect(reopened)
    # OCCT recomputes mass properties on reopening: curved real-frame faces differed
    # by 2e-11 mm³ in FreeCAD 1.1.3. Identity and solid counts remain exact; compare
    # floating volumes with explicit numerical tolerances far below machining scale.
    before.sort(key=lambda item: item["name"])
    after.sort(key=lambda item: item["name"])
    relative_tolerance, absolute_tolerance = 1e-10, 1e-8
    if len(before) != len(after) or any(
        first["name"] != second["name"]
        or first["solids"] != second["solids"]
        or not math.isclose(
            first["volume_mm3"], second["volume_mm3"],
            rel_tol=relative_tolerance, abs_tol=absolute_tolerance,
        )
        for first, second in zip(before, after, strict=True)
    ):
        raise RuntimeError("FCStd reopen changed component names, solid counts, or volumes")
    FreeCAD.closeDocument(reopened.Name)
    report = {
        "status": "passed",
        "freecad_version": ".".join(FreeCAD.Version()[:3]),
        "reopened": True,
        "units": "mm",
        "components": after,
        "solid_count": sum(item["solids"] for item in after),
        "volume_mm3": sum(item["volume_mm3"] for item in after),
        "maximum_volume_change_mm3": max(
            abs(first["volume_mm3"] - second["volume_mm3"])
            for first, second in zip(before, after, strict=True)
        ),
        "volume_relative_tolerance": relative_tolerance,
        "volume_absolute_tolerance_mm3": absolute_tolerance,
    }
    Path(job["report"]).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


# FreeCADCmd imports .py files as modules rather than executing them as __main__.
run()
