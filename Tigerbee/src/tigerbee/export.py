"""Manufacturing exports and build provenance."""

import hashlib
import json
import subprocess
from dataclasses import asdict
from importlib.metadata import version
from pathlib import Path

from build123d import ExportDXF, ExportSVG, Mesher, export_gltf, export_step, export_stl

from tigerbee.inventory import source_digest
from tigerbee.mesh import audit_3mf
from tigerbee.models import (
    DEFAULT_PARAMETERS,
    PartParameters,
    build_part,
    build_profile,
    profile_data,
)
from tigerbee.references import MEASURED_WHEELBASE_RANGE_MM, MEASUREMENT_REFERENCE


def source_revision() -> str | None:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=False
    )
    return result.stdout.strip() if result.returncode == 0 else None


def export_component(
    name: str, directory: Path, parameters: PartParameters = DEFAULT_PARAMETERS
) -> dict:
    """Build and export a part; return a manifest only after all exports succeed."""
    part = build_part(name, parameters)
    profile = build_profile(name, parameters)
    directory.mkdir(parents=True, exist_ok=True)
    stem = directory / name
    if not export_step(part, stem.with_suffix(".step")):
        raise RuntimeError(f"STEP export failed for {name}")
    if not export_stl(part, stem.with_suffix(".stl"), tolerance=0.01, angular_tolerance=0.1):
        raise RuntimeError(f"STL export failed for {name}")
    mesh = Mesher()
    mesh.add_shape(part, linear_deflection=0.01, angular_deflection=0.1, part_number=name)
    mesh.write(stem.with_suffix(".3mf"))
    mesh_report = audit_3mf(stem.with_suffix(".3mf"))
    svg = ExportSVG(scale=3, margin=3, line_weight=0.25)
    svg.add_shape(profile)
    svg.write(stem.with_suffix(".svg"))
    dxf = ExportDXF()
    dxf.add_shape(profile)
    dxf.write(stem.with_suffix(".dxf"))
    outputs = [f"{name}.{extension}" for extension in ("step", "stl", "3mf", "svg", "dxf")]
    for output in outputs:
        if not (directory / output).is_file() or (directory / output).stat().st_size == 0:
            raise RuntimeError(f"Missing or empty export: {output}")
    effective = asdict(parameters)
    effective["thickness"] = part.bounding_box().size.Z
    reference = profile_data(name)
    assumptions = [
        f"{parameters.mounting_hole_diameter:g} mm nominal mounting bores; "
        "machining tolerances are not specified"
    ]
    if name in ("rear-plate", "top-plate"):
        assumptions.extend(
            [
                "Symmetric analytic dimensions inferred from Scan_2; "
                "physical dimensions unconfirmed",
                f"{effective['thickness']:g} mm selected plate thickness; "
                "verify against physical stock",
            ]
        )
    manifest = {
        "part": name,
        "units": "mm",
        "parameters": effective,
        "source_revision": source_revision(),
        "source_sha256": source_digest(),
        "build123d": version("build123d"),
        "reference_sha256": reference["source_sha256"],
        "reference_status": "symmetric-design-derived-from-reference",
        "authoritative_geometry_source": reference["source"],
        "reference_body": reference.get("source_body"),
        "measured_frame_wheelbase_range_mm": list(MEASURED_WHEELBASE_RANGE_MM),
        "measurement_reference": MEASUREMENT_REFERENCE,
        "reference_note": (
            "FreeCAD and supplied 3MF define the design foundation; symmetry and shared "
            "interfaces are engineered in Python. Original reference files are preserved."
            if reference["source"] == "Tigerbee.FCStd"
            else "Analytic nominal design informed by the near-1:1 tracing of a part "
            "absent from the original FreeCAD document; scan irregularities are not reproduced."
        ),
        "reference_assumptions": reference.get("assumptions", []),
        "assumptions": assumptions,
        "valid": part.is_valid,
        "solid_count": len(part.solids()),
        "mesh_validation": mesh_report,
        "volume_mm3": part.volume,
        "dimensions_mm": list(part.bounding_box().size),
        "mesh_linear_deflection_mm": 0.01,
        "mesh_angular_deflection_rad": 0.1,
        "files": outputs,
        "file_sha256": {
            name: hashlib.sha256((directory / name).read_bytes()).hexdigest() for name in outputs
        },
    }
    if name.endswith("-plate"):
        from tigerbee.layout import plate_mounting_holes
        from tigerbee.plates import DEFAULT_PLATE_DIMENSIONS

        manifest["design_dimensions_mm"] = asdict(DEFAULT_PLATE_DIMENSIONS)
        if name == "camera-plate" and parameters.center_hole_diameter is not None:
            manifest["design_dimensions_mm"]["camera_round_diameter"] = (
                parameters.center_hole_diameter
            )
        manifest["mounting_hole_centers_mm"] = plate_mounting_holes(name)
        manifest["datum"] = "Frame XY datum; X=0 is the bilateral symmetry axis; lower face Z=0"
    else:
        manifest["datum"] = (
            "Motor shaft center X=Y=0; shaft extends toward negative Y; lower face Z=0"
        )
    stem.with_suffix(".json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def export_frame(directory: Path, top_z: float = 35, require_fit: bool = False) -> dict:
    """Write a named assembly and its explicit dimensional/fit report."""
    from tigerbee.assembly import AssemblyParameters, build_assembly, require_final_fit
    from tigerbee.validation import require_frame_fit

    assembly, report = build_assembly(AssemblyParameters(top_z=top_z))
    require_frame_fit(report["geometry_audit"])
    if require_fit:
        require_final_fit(report)
    directory.mkdir(parents=True, exist_ok=True)
    if not export_step(assembly, directory / "tigerbee-assembly.step"):
        raise RuntimeError("Assembly STEP export failed")
    if not export_stl(assembly, directory / "tigerbee-assembly.stl", tolerance=0.01):
        raise RuntimeError("Assembly STL export failed")
    mesh = Mesher()
    for child in assembly.children:
        mesh.add_shape(child, linear_deflection=0.01, part_number=child.label)
    mesh.write(directory / "tigerbee-assembly.3mf")
    if not export_gltf(assembly, directory / "tigerbee-assembly.glb", binary=True):
        raise RuntimeError("Assembly GLB export failed")
    for name, view in (("isometric", (300, -400, 350)), ("top", (0, 0, 500))):
        up = (0, 1, 0) if name == "top" else (0, 0, 1)
        visible, _ = assembly.project_to_viewport(view, viewport_up=up, look_at=(0, 0, 0))
        svg = ExportSVG(scale=2, margin=5, line_weight=0.25)
        svg.add_shape(visible)
        svg.write(directory / f"tigerbee-{name}.svg")
    report["source_revision"] = source_revision()
    report["source_sha256"] = source_digest()
    report["build123d"] = version("build123d")
    report["file_sha256"] = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in directory.iterdir()
        if path.suffix in (".step", ".stl", ".3mf", ".glb", ".svg")
    }
    (directory / "assembly-report.json").write_text(json.dumps(report, indent=2) + "\n")
    return report
