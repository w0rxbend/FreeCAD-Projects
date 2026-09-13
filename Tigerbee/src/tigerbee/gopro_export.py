"""Printable GoPro holder exports and measured interface checks."""

from dataclasses import asdict
from math import sqrt
from pathlib import Path

from build123d import (
    Axis,
    Circle,
    Color,
    Compound,
    GeomType,
    Mesher,
    Part,
    Plane,
    Pos,
    Rectangle,
    RegularPolygon,
    Shape,
    export_gltf,
    export_step,
    export_stl,
    extrude,
    import_step,
)

from tigerbee.export import export_view, write_build_report
from tigerbee.gopro import (
    DEFAULT_GOPRO,
    GOPRO_HOLDER,
    GoProParameters,
    build_gopro_holder,
    holder_center_y,
    mounting_centers,
)
from tigerbee.mesh import audit_3mf
from tigerbee.models import build_part


def _overlap(a: Shape, b: Shape) -> float:
    common = a & b
    return common.volume if common is not None else 0.0


def audit_holder(holder: Part, parameters: GoProParameters) -> dict:
    """Test the actual plate and independent nominal hardware/camera-finger witnesses."""
    plate = build_part("top-plate").translate((0, 0, -3))
    overlaps = {"carbon": _overlap(holder, plate)}
    for index, (x, y) in enumerate(mounting_centers()):
        shaft = Pos(x, y, -6) * extrude(Circle(1.55), amount=40)
        driver = Pos(x, y, 2) * extrude(Circle(3.15), amount=40)
        overlaps[f"mount-{index}-shaft"] = _overlap(holder, shaft)
        overlaps[f"mount-{index}-driver"] = _overlap(holder, driver)
    cy = holder_center_y()
    axle_plane = Plane.YZ * Pos(cy, parameters.axle_height)
    axle = extrude(axle_plane * Circle(2.6), amount=40, both=True)
    overlaps["M5-axle"] = _overlap(holder, axle)
    nut = Pos(7.1, 0, 0) * extrude(
        axle_plane * RegularPolygon(8 / sqrt(3), 6, rotation=30), amount=4, dir=(1, 0, 0)
    )
    overlaps["M5-nut-seat"] = _overlap(holder, nut)
    # Empty space is insufficient: require actual bearing material at each
    # interface and around the captive nut. R7 stays within the R7.5 crown and
    # its rounded shoulder transitions. The right bearing stops at the nut seat.
    missing_material = {}
    for name, x, width, inner_radius in (
        ("left-finger", -7.7, 3, 2.75),
        ("middle-finger", -1.5, 3, 2.75),
        ("right-finger", 4.7, 2.3, 2.75),
        ("nut-seat-wall", 7, 4.2, 5),
    ):
        bearing = Pos(x, 0, 0) * extrude(
            axle_plane * (Circle(7) - Circle(inner_radius)), amount=width, dir=(1, 0, 0)
        )
        missing_material[name] = (bearing - holder).volume
    face = (Circle(7.5) + Pos(0, 5.75) * Rectangle(15, 11.5)).faces()[0]
    fingers = [
        Pos(x, cy, parameters.axle_height) * extrude(Plane.YZ * face, amount=3, dir=(1, 0, 0))
        for x in (-4.6, 1.6)
    ]
    coupon = Compound(children=fingers)
    pitch = {}
    for angle in range(-15, 61, 5):
        witness = coupon.rotate(Axis((0, cy, parameters.axle_height), (1, 0, 0)), angle)
        pitch[str(angle)] = _overlap(holder, witness)
    bosses = [f for f in holder.faces().filter_by(Plane.XY) if abs(f.center().Z + 2) < 1e-6]
    walls = []
    for face in bosses:
        radii = [e.radius for e in face.edges() if e.geom_type == GeomType.CIRCLE]
        if len(radii) == 2:
            walls.append(max(radii) - min(radii))
    passed = (
        holder.is_valid
        and len(walls) == 4
        and min(walls) >= 0.7
        and len(holder.solids()) == 1
        and max([*overlaps.values(), *pitch.values()]) < 1e-6
        and max(missing_material.values()) < 1e-6
    )
    report = {
        "passed": passed,
        "obstructions_mm3": overlaps,
        "pivot_missing_material_mm3": missing_material,
        "nominal_finger_pitch_sweep_interference_mm3": pitch,
        "mounting_hole_centers_mm": mounting_centers(),
        "registration_radial_clearance_mm": 0.1,
        "registration_wall_thickness_mm": walls,
        "camera_body_fit": "Not assessed: exact GoPro and FPV-camera body CAD are unavailable",
    }
    if not passed:
        raise ValueError(f"Holder fit failed: {report}")
    return report


def export_gopro_holder(
    directory: Path, parameters: GoProParameters = DEFAULT_GOPRO, *, preview: bool = True
) -> dict:
    directory = directory.resolve()
    directory.mkdir(parents=True, exist_ok=True)
    holder = build_gopro_holder(parameters)
    report = {
        "part": GOPRO_HOLDER,
        "parameters": asdict(parameters),
        "solid_count": 1,
        "status": "nominal-interface-fit-verified",
        "fit": audit_holder(holder, parameters),
        "datum": "Print bed Z=0; top-plate seating surface Z=2; XY retains the frame datum",
        "volume_mm3": holder.volume,
        "dimensions_mm": list(holder.bounding_box().size),
        "hardware": "4 M3 bolts, underside washers/nuts; M5 pivot bolt and 8 mm AF hex nut",
        "finger_dimensions_mm": {"thickness": 3, "gap": 3.2, "axle_bore": 5.5, "crown_radius": 7.5},
    }
    printable = holder.translate((0, 0, 2))
    printable.color = Color(0.1, 0.45, 0.95)
    paths = [directory / f"{GOPRO_HOLDER}.{ext}" for ext in ("step", "stl", "3mf", "svg")]
    export_step(printable, paths[0])
    if not export_stl(printable, paths[1], tolerance=0.01, angular_tolerance=0.1):
        raise RuntimeError("GoPro holder STL export failed")
    mesh = Mesher()
    mesh.add_shape(
        printable, linear_deflection=0.01, angular_deflection=0.1, part_number=GOPRO_HOLDER
    )
    mesh.write(paths[2])
    report["mesh_validation"] = audit_3mf(paths[2])
    actual = import_step(paths[0])
    if not actual.is_valid or len(actual.solids()) != 1:
        raise ValueError("GoPro holder STEP is invalid")
    if (actual - printable).volume + (printable - actual).volume > 1e-4:
        raise ValueError("GoPro holder STEP geometry changed")
    export_view(printable, paths[3], (90, -140, 110))
    write_build_report(directory / f"{GOPRO_HOLDER}.json", report, paths)
    if preview:
        _export_preview(holder, directory, parameters)
    return report


def _export_preview(holder: Part, directory: Path, parameters: GoProParameters) -> None:
    from tigerbee.assembly import build_assembly
    from tigerbee.layout import frame_arm_layout
    from tigerbee.protectors import build_protector

    frame, frame_report = build_assembly()
    parts = list(frame.children)
    top = next(part for part in parts if part.label == "top-plate")
    top_z = top.bounding_box().max.Z
    mounted = holder.translate((0, 0, top_z))
    mounted.color = Color(0.1, 0.45, 0.95)
    for placement in frame_arm_layout():
        foot = placement.place(build_protector(placement.part_name), z=3)
        foot.label = placement.label.replace("arm", "protector")
        foot.color = Color(0.95, 0.35, 0.08)
        parts.append(foot)
    collisions = {part.label: _overlap(mounted, part) for part in parts}
    if any(value > 1e-6 for value in collisions.values()):
        raise ValueError(f"GoPro holder assembly collision: {collisions}")
    assembly = Compound(label="Tigerbee with GoPro holder and feet", children=[*parts, mounted])
    stem = directory / "tigerbee-with-gopro-holder"
    export_step(assembly, stem.with_suffix(".step"))
    actual = import_step(stem.with_suffix(".step"))
    if not actual.is_valid or len(actual.solids()) != 20:
        raise ValueError("GoPro preview must contain 20 valid solids")
    if not export_gltf(assembly, stem.with_suffix(".glb"), binary=True):
        raise RuntimeError("GoPro preview GLB export failed")
    outputs = [stem.with_suffix(".step"), stem.with_suffix(".glb")]
    for suffix, view in (("isometric", (300, -400, 280)), ("side", (500, 0, 0))):
        path = directory / f"tigerbee-with-gopro-holder-{suffix}.svg"
        export_view(assembly, path, view)
        outputs.append(path)
    report = {
        "parameters": asdict(parameters),
        "solid_count": 20,
        "status": "nominal-interface-fit-verified",
        "holder_intersections_mm3": collisions,
        "top_plate_surface_z_mm": top_z,
        "pivot_frame_xyz_mm": [0, holder_center_y(), top_z + parameters.axle_height],
        "frame_geometry_audit_passed": frame_report["geometry_audit"]["passed"],
        "camera_body_fit": "Exact GoPro and FPV-camera bodies are not modeled",
    }
    write_build_report(stem.with_suffix(".json"), report, outputs)
