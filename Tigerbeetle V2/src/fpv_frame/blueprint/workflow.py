"""Bind authoritative CAD profiles to each loose part's scan registration."""

import json
from dataclasses import asdict
from math import atan2, degrees
from pathlib import Path

from build123d import Face, GeomType, Plane

from fpv_frame.blueprint.calibration import Calibration, Point
from fpv_frame.blueprint.measurements import verify_sources
from fpv_frame.blueprint.overlay import ProfileOverlay, write_overlay
from fpv_frame.geometry.datums import Point2
from fpv_frame.geometry.layout import MASTER_CALIBRATION, PIXELS_PER_MM, build_layout
from fpv_frame.parameters.frame import FrameParameters
from fpv_frame.parts.arm import arm_profile
from fpv_frame.parts.plates import plate_profile


def circular_centers(face: Face) -> tuple[Point, ...]:
    centers = []
    for wire in face.inner_wires():
        edges = wire.edges()
        if len(edges) == 1 and edges[0].geom_type == GeomType.CIRCLE:
            center = Face(wire).center()
            centers.append((center.X, center.Y))
    return tuple(centers)


def reference_overlays(
    params: FrameParameters, root: Path
) -> dict[str, tuple[ProfileOverlay, ...]]:
    verify_sources(root)
    data = json.loads((root / "references/measurements/combined.yaml").read_text())
    layout = build_layout(params)
    zero = layout.global_to_master(Point2(0, 0))
    overlays: dict[str, list[ProfileOverlay]] = {"Scan_1": [], "Scan_2": []}
    for component_id in ("scan1_body", "scan2_broad", "scan2_long"):
        c, t = complex(1, 0), complex(0, 0)
        if component_id != "scan1_body":
            transform = data["transforms"][f"scan1_body_to_{component_id}"]
            c = complex(*transform["c"]["value"])
            t = complex(*transform["t"]["value"])
        origin = c * complex(zero.x, zero.y) + t
        calibration = Calibration(
            PIXELS_PER_MM * abs(c),
            (origin.real, origin.imag),
            MASTER_CALIBRATION.rotation_degrees + degrees(atan2(c.imag, c.real)),
        )
        profile = plate_profile(params, component_id)
        interfaces = tuple(
            (p.x, p.y)
            for group in layout.plate_hole_groups(component_id)
            for p in group.pattern.centers
        )
        scan = "Scan_1" if component_id == "scan1_body" else "Scan_2"
        overlays[scan].append(
            ProfileOverlay(
                component_id,
                profile,
                calibration,
                circular_centers(profile),
                interfaces,
            )
        )
    canonical = arm_profile(params)
    for name in ("a", "b"):
        observation = data["arms"][name]
        origin_px = observation["root_midpoint_uv"]["value"]
        motor_px = observation["motor_center_uv"]["value"]
        dx, dy = motor_px[0] - origin_px[0], motor_px[1] - origin_px[1]
        calibration = Calibration(PIXELS_PER_MM, tuple(origin_px), degrees(atan2(dx, -dy)))
        face = canonical if name == "a" else canonical.mirror(Plane.YZ)
        interfaces = tuple((p.x if name == "a" else -p.x, p.y) for p in layout.root_pattern.centers)
        overlays["Scan_1"].append(
            ProfileOverlay(
                f"arm_{name}",
                face,
                calibration,
                circular_centers(face),
                interfaces,
            )
        )
    return {name: tuple(parts) for name, parts in overlays.items()}


def write_diagnostics(params: FrameParameters, root: Path, scan: str) -> list[Path]:
    """Generate overlays and fit evidence from the same current profile snapshot."""
    from fpv_frame.blueprint.deviation import fit_report

    overlays = reference_overlays(params, root)
    paths = list(write_overlay(root, scan, overlays[scan], root / "artifacts/overlays"))
    report = fit_report(root, overlays)
    report["parameters"] = asdict(params)
    report_dir = root / "artifacts/reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / "blueprint-fit.json"
    report_path.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    calibration_dir = root / "references/calibrated"
    calibration_dir.mkdir(parents=True, exist_ok=True)
    calibration_path = calibration_dir / "registrations.json"
    calibration_path.write_text(json.dumps({
        name: {item.name: asdict(item.calibration) for item in items}
        for name, items in overlays.items()
    }, indent=2) + "\n")
    return [*paths, report_path, calibration_path]
