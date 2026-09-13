"""Manufacturing exports and build provenance."""

import hashlib
import json
import subprocess
import xml.etree.ElementTree as ET
from dataclasses import asdict
from importlib.metadata import version
from math import dist
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
from tigerbee.references import (
    ARM_THICKNESS_MM,
    MEASURED_WHEELBASE_RANGE_MM,
    MEASUREMENT_REFERENCE,
    NOMINAL_WHEELBASE_MM,
    PLATE_THICKNESS_MM,
)


def source_revision() -> str | None:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=False
    )
    return result.stdout.strip() if result.returncode == 0 else None


def export_motor_layout(directory: Path, report: dict) -> None:
    """Dimension the independently measured motor centers in the frame XY datum."""
    centers = report["geometry_audit"]["actual_motor_centers_mm"]
    root = ET.Element(
        "svg",
        {
            "xmlns": "http://www.w3.org/2000/svg",
            "viewBox": "-175 -175 350 350",
            "width": "900",
            "height": "900",
        },
    )
    ET.SubElement(root, "title").text = "Tigerbee motor axes: measured from CAD bores"
    ET.SubElement(
        root, "rect", {"x": "-175", "y": "-175", "width": "350", "height": "350", "fill": "white"}
    )
    geometry = ET.SubElement(
        root,
        "g",
        {"transform": "scale(1,-1)", "fill": "none", "stroke": "#2563eb", "stroke-width": "0.7"},
    )
    for a, b in (("front-left-arm", "rear-right-arm"), ("front-right-arm", "rear-left-arm")):
        p, q = centers[a], centers[b]
        ET.SubElement(
            geometry, "line", {"x1": str(p[0]), "y1": str(p[1]), "x2": str(q[0]), "y2": str(q[1])}
        )
    for label, (x, y) in centers.items():
        ET.SubElement(geometry, "circle", {"cx": str(x), "cy": str(y), "r": "3"})
        name = label.removesuffix("-arm").upper()
        label_y = -y - 14 if y > 0 else -y + 12
        for row, caption in enumerate((name, f"({x:.3f}, {y:.3f}) mm")):
            ET.SubElement(
                root,
                "text",
                {
                    "x": str(x),
                    "y": str(label_y + row * 7),
                    "text-anchor": "middle",
                    "font-family": "sans-serif",
                    "font-size": "5",
                },
            ).text = caption
    diagonals = [
        dist(centers[a], centers[b])
        for a, b in (("front-left-arm", "rear-right-arm"), ("front-right-arm", "rear-left-arm"))
    ]
    for y, caption in (
        (-153, "Motor centers · frame XY datum"),
        (145, f"Diagonals: {diagonals[0]:.3f} / {diagonals[1]:.3f} mm"),
        (157, "True X · perpendicular diagonals · common center (0, 0)"),
    ):
        ET.SubElement(
            root,
            "text",
            {
                "x": "0",
                "y": str(y),
                "text-anchor": "middle",
                "font-family": "sans-serif",
                "font-size": "6",
            },
        ).text = caption
    ET.SubElement(geometry, "circle", {"cx": "0", "cy": "0", "r": "1.5"})
    ET.indent(root)
    ET.ElementTree(root).write(
        directory / "tigerbee-motor-layout.svg", encoding="utf-8", xml_declaration=True
    )


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
        assumptions.append(
            "Symmetric analytic outline dimensions inferred from Scan_2; "
            "mounting interfaces follow the user-specified 305 mm X layout"
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
        "nominal_frame_wheelbase_mm": NOMINAL_WHEELBASE_MM,
        "nominal_thickness_mm": (
            ARM_THICKNESS_MM if name.startswith("arm-type-") else PLATE_THICKNESS_MM
        ),
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
        if name == "arm-type-2":
            from tigerbee.layout import (
                ROOT_CLAMP_FILLET_MM,
                ROOT_CLAMP_INSET_MM,
                ROOT_CLAMP_TRANSITION_Y_MM,
            )

            manifest["root_clamp_relief_mm"] = {
                "outline_inset": ROOT_CLAMP_INSET_MM,
                "blend_radius": ROOT_CLAMP_FILLET_MM,
                "transition_local_y": ROOT_CLAMP_TRANSITION_Y_MM - parameters.length_extension,
            }
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
    export_motor_layout(directory, report)
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
