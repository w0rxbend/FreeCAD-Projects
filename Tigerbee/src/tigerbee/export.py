"""Manufacturing exports and build provenance."""

import json
import subprocess
from dataclasses import asdict
from importlib.metadata import version
from pathlib import Path

from build123d import ExportDXF, ExportSVG, Mesher, export_step, export_stl

from tigerbee.models import (
    DEFAULT_PARAMETERS,
    PartParameters,
    build_part,
    build_profile,
    profile_data,
)


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
    svg = ExportSVG(scale=3)
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
    manifest = {
        "part": name,
        "units": "mm",
        "parameters": effective,
        "source_revision": source_revision(),
        "build123d": version("build123d"),
        "reference_sha256": profile_data(name)["source_sha256"],
        "valid": part.is_valid,
        "solid_count": len(part.solids()),
        "volume_mm3": part.volume,
        "dimensions_mm": list(part.bounding_box().size),
        "mesh_linear_deflection_mm": 0.01,
        "mesh_angular_deflection_rad": 0.1,
        "files": outputs,
    }
    stem.with_suffix(".json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest
