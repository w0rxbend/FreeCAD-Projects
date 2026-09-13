"""Separate printable accessories, actual-solid fit checks and assembly previews."""

import hashlib
import json
from dataclasses import asdict
from itertools import combinations
from pathlib import Path

from build123d import (
    Color,
    Compound,
    ExportSVG,
    Face,
    Mesher,
    Plane,
    Shape,
    export_gltf,
    export_step,
    export_stl,
    extrude,
    import_step,
    offset,
)

from tigerbee.export import source_revision
from tigerbee.inventory import source_digest
from tigerbee.layout import frame_arm_layout
from tigerbee.mesh import audit_3mf
from tigerbee.models import build_part
from tigerbee.protectors import DEFAULT_PROTECTOR, ProtectorParameters, build_protector
from tigerbee.references import PLATE_THICKNESS_MM


def _overlap(a: Shape, b: Shape) -> float:
    common = a & b
    return common.volume if common is not None else 0.0


def audit_protector(part: Shape, arm: Shape, drop: float, flange: float) -> dict:
    """Measure carbon fit and tool passages from the supplied solids, in arm coordinates."""
    interference = _overlap(part, arm)
    ground_z = part.bounding_box().min.Z
    ground_area = sum(
        face.area
        for face in part.faces().filter_by(Plane.XY)
        if abs(face.center().Z - ground_z) < 1e-6
    )
    bottom = min(arm.faces().filter_by(Plane.XY), key=lambda face: face.center().Z)
    opening_interference = 0.0
    head_interference = 0.0
    for wire in bottom.inner_wires():
        center = wire.center()
        if center.Y < -30:
            continue
        hole = Face(wire)
        tool = extrude(hole, amount=drop + 6, dir=(0, 0, 1)).translate((0, 0, -drop))
        opening_interference += _overlap(part, tool)
        if abs(center.X) > 4 and abs(center.Y) < 10:
            head = offset(hole, amount=1.7).faces()[0]
            tool = extrude(head, amount=drop - flange, dir=(0, 0, 1))
            head_interference += _overlap(part, tool.translate((0, 0, -drop)))
    passed = (
        part.is_valid
        and len(part.solids()) == 1
        and abs(ground_z + drop) < 1e-6
        and ground_area > 200
        and max(interference, opening_interference, head_interference) < 1e-6
    )
    result = {
        "passed": passed,
        "carbon_intersection_mm3": interference,
        "opening_obstruction_mm3": opening_interference,
        "head_access_obstruction_mm3": head_interference,
        "contact_area_mm2": ground_area,
        "ground_z_in_arm_datum_mm": ground_z,
    }
    if not passed:
        raise ValueError(f"Protector fit failed: {result}")
    return result


def _view(shape: Shape, path: Path, view: tuple) -> None:
    visible, _ = shape.project_to_viewport(view, viewport_up=(0, 0, 1), look_at=(0, 0, 0))
    svg = ExportSVG(scale=3, margin=5, line_weight=0.2)
    svg.add_shape(visible)
    svg.write(path)


def _report(path: Path, report: dict, outputs: list[Path]) -> None:
    report.update(source_revision=source_revision(), source_sha256=source_digest(), units="mm")
    report["file_sha256"] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in outputs}
    path.write_text(json.dumps(report, indent=2) + "\n")


def export_protector(
    arm: str, mirror: bool, directory: Path, parameters: ProtectorParameters = DEFAULT_PROTECTOR
) -> dict:
    directory = directory.resolve()
    directory.mkdir(parents=True, exist_ok=True)
    part = build_protector(arm, parameters, mirror=mirror)
    carbon = build_part(arm)
    if mirror:
        carbon = carbon.mirror(Plane.YZ)
    fit = audit_protector(part, carbon, parameters.drop, parameters.flange)
    name = part.label
    printable = part.translate((0, 0, parameters.drop))
    printable.color = Color(0.95, 0.35, 0.08)
    paths = [directory / f"{name}.{suffix}" for suffix in ("step", "stl", "3mf", "svg")]
    export_step(printable, paths[0])
    if not export_stl(printable, paths[1], tolerance=0.01, angular_tolerance=0.1):
        raise RuntimeError(f"STL export failed: {name}")
    mesh = Mesher()
    mesh.add_shape(printable, linear_deflection=0.01, angular_deflection=0.1, part_number=name)
    mesh.write(paths[2])
    mesh_report = audit_3mf(paths[2])
    reopened = import_step(paths[0])
    if not reopened.is_valid or abs(reopened.volume - printable.volume) > 1e-4:
        raise ValueError(f"STEP round trip failed: {name}")
    if (reopened - printable).volume + (printable - reopened).volume > 1e-4:
        raise ValueError(f"STEP geometry changed: {name}")
    _view(printable, paths[3], (80, -120, 90))
    report = {
        "part": name,
        "arm": arm,
        "mirror": mirror,
        "parameters": asdict(parameters),
        "solid_count": 1,
        "status": "nominal-cad-fit-verified",
        "material_intent": "TPU; physical print fit unverified",
        "datum": "Print bed Z=0; motor XY=(0,0); arm underside Z=drop; root toward -Y",
        "volume_mm3": printable.volume,
        "dimensions_mm": list(printable.bounding_box().size),
        "fit": fit,
        "mesh_validation": mesh_report,
        "additional_bolt_grip_mm": parameters.flange,
        "files": [p.name for p in paths],
    }
    _report(directory / f"{name}.json", report, paths)
    return report


def export_protectors(directory: Path, parameters: ProtectorParameters = DEFAULT_PROTECTOR) -> dict:
    from tigerbee.assembly import build_assembly

    directory = directory.resolve()
    for kind in (1, 2):
        for mirror in (False, True):
            export_protector(f"arm-type-{kind}", mirror, directory, parameters)
    frame, frame_report = build_assembly()
    parts = list(frame.children)
    feet = []
    for placement in frame_arm_layout():
        local = build_protector(placement.part_name, parameters)
        foot = placement.place(local, z=PLATE_THICKNESS_MM)
        foot.label = placement.label.replace("arm", "protector")
        foot.color = Color(0.95, 0.35, 0.08)
        feet.append(foot)
    intersections = {
        f"{a.label} / {b.label}": _overlap(a, b)
        for a, b in [*((foot, part) for foot in feet for part in parts), *combinations(feet, 2)]
    }
    if any(value > 1e-6 for value in intersections.values()):
        raise ValueError(f"Accessory assembly collision: {intersections}")
    ground = [foot.bounding_box().min.Z for foot in feet]
    if max(ground) - min(ground) > 1e-6:
        raise ValueError("Feet are not coplanar")
    combined = Compound(label="Tigerbee with landing protectors", children=[*parts, *feet])
    stem = directory / "tigerbee-with-protectors"
    export_step(combined, stem.with_suffix(".step"))
    if len(import_step(stem.with_suffix(".step")).solids()) != 19:
        raise ValueError("Accessory assembly STEP must contain 19 solids")
    if not export_gltf(combined, stem.with_suffix(".glb"), binary=True):
        raise RuntimeError("Protector assembly GLB export failed")
    outputs = [stem.with_suffix(".step"), stem.with_suffix(".glb")]
    for suffix, view in (("isometric", (300, -400, 250)), ("side", (0, -500, 0))):
        path = directory / f"tigerbee-with-protectors-{suffix}.svg"
        _view(combined, path, view)
        outputs.append(path)
    report = {
        "parameters": asdict(parameters),
        "solid_count": 19,
        "status": "nominal-cad-fit-verified",
        "ground_z_mm": ground,
        "lower_plate_ground_clearance_mm": -max(ground),
        "intersections_mm3": intersections,
        "frame_geometry_audit_passed": frame_report["geometry_audit"]["passed"],
        "diagonal_wheelbases_mm": frame_report["diagonal_wheelbases_mm"],
    }
    _report(stem.with_suffix(".json"), report, outputs)
    return report
