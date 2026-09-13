"""Compare original-size pen tracings with the CAD outlines and write SVG overlays.

Run from Tigerbee: uv run --group tracing python tools/compare_a4.py
The source JPEGs and original FreeCAD document are read without modification.
"""

import base64
import hashlib
import json
import math
import xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZipFile

import cv2
import numpy as np

from tigerbee.models import build_profile, profile_data

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "refs/analysis"


def ink_distances(points, distance, scale):
    pixels = np.rint(points).astype(int)
    h, w = distance.shape
    if not (
        (pixels[:, 0] >= 0).all()
        and (pixels[:, 0] < w).all()
        and (pixels[:, 1] >= 0).all()
        and (pixels[:, 1] < h).all()
    ):
        raise ValueError("CAD projection falls outside the scan")
    errors = distance[pixels[:, 1], pixels[:, 0]] * scale
    return {
        "median": float(np.median(errors)),
        "p95": float(np.quantile(errors, 0.95)),
        "max": float(errors.max()),
    }


def compare() -> None:
    source = ROOT / "Tigerbee.FCStd"
    with ZipFile(source) as archive:
        document = ET.fromstring(archive.read("Document.xml"))
        image = document.find(".//ObjectData/Object[@name='Scan_1']/Properties")
        width_mm = float(image.find("Property[@name='XSize']/Float").get("value"))
        height_mm = float(image.find("Property[@name='YSize']/Float").get("value"))
        placement = image.find("Property[@name='Placement']/PropertyPlacement")
        angle = 2 * math.atan2(float(placement.get("Q2")), float(placement.get("Q3")))
        center = np.array([float(placement.get("Px")), float(placement.get("Py"))])
        embedded_scan_matches = (
            archive.read("Scan_1.jpeg") == (ROOT / "refs/Scan_1.jpeg").read_bytes()
        )
    report = {
        "freecad_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "freecad_bodies": [
            obj.get("name")
            for obj in document.findall("./Objects/Object")
            if obj.get("type") == "PartDesign::Body"
        ],
        "embedded_scan_1_matches_reference": embedded_scan_matches,
        "nominal_a4_mm": [210, 297],
        "freecad_scan_1_size_mm": [width_mm, height_mm],
        "freecad_scan_1_center_mm": center.tolist(),
        "freecad_scan_1_rotation_deg": math.degrees(angle),
        "method": (
            "Project unmodified CAD outlines into scan pixels. Scan_1 registration uses "
            "the exact saved FreeCAD image-plane placement; Scan_2 uses its tracing origin. "
            "Distances are from sampled CAD outer boundaries to the original red ink."
        ),
        "limitations": (
            "Ink is a band, not an exact engineering boundary. CAD-to-ink distances are "
            "one-directional and do not validate every opening, physical hole diameter, "
            "thickness, or assembly fit. Scan_2 is a trace comparison, "
            "not independent CAD evidence."
        ),
        "scans": [],
    }
    OUTPUT.mkdir(exist_ok=True)
    for number, names in (
        (1, ("arm-type-1", "arm-type-2", "camera-plate")),
        (2, ("rear-plate", "top-plate")),
    ):
        scan_path = ROOT / f"refs/Scan_{number}.jpeg"
        raster = cv2.imread(str(scan_path))
        h, w = raster.shape[:2]
        blue, green, red = cv2.split(raster.astype(np.int16))
        mask = ((red - green > 25) & (red - blue > 15) & (red < 245)).astype(np.uint8) * 255
        distance = cv2.distanceTransform(255 - mask, cv2.DIST_L2, cv2.DIST_MASK_PRECISE)
        closed = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
        contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        outlines = sorted(contours, key=cv2.contourArea, reverse=True)[: len(names)]
        page = {
            "source": str(scan_path.relative_to(ROOT)),
            "sha256": hashlib.sha256(scan_path.read_bytes()).hexdigest(),
            "pixels": [w, h],
            "nominal_mm_per_pixel": [210 / w, 297 / h],
            "parts": [],
        }
        polylines = []
        for name in names:
            data = profile_data(name)
            if number == 1 and data["source_sha256"] != report["freecad_sha256"]:
                raise ValueError("FreeCAD profiles do not match the current reference document")
            profile = build_profile(name)

            def scan_points(edge, number=number, data=data, w=w, h=h):
                count = max(3, math.ceil(edge.length / 0.15))
                points = np.array(
                    [tuple(edge.position_at(t))[:2] for t in np.linspace(0, 1, count)]
                )
                if number == 1:
                    theta = math.radians(-data["rotation_deg"])
                    rotation = np.array(
                        [[math.cos(theta), -math.sin(theta)], [math.sin(theta), math.cos(theta)]]
                    )
                    world = points @ rotation.T + np.array(data["datum_source_xy"])
                    inverse = np.array(
                        [[math.cos(angle), math.sin(angle)], [-math.sin(angle), math.cos(angle)]]
                    )
                    local = (world - center) @ inverse.T
                    return np.column_stack(
                        ((local[:, 0] / width_mm + 0.5) * w, (0.5 - local[:, 1] / height_mm) * h)
                    )
                origin = data["scan_origin_px"]
                scale = data["scan_mm_per_pixel"]
                return np.column_stack(
                    (origin[0] + points[:, 0] / scale, origin[1] - points[:, 1] / scale)
                )

            outer = np.concatenate([scan_points(edge) for edge in profile.outer_wire().edges()])
            low, high = outer.min(axis=0), outer.max(axis=0)
            mid = (low + high) / 2
            contour = min(
                outlines,
                key=lambda c: np.linalg.norm(
                    np.array(cv2.boundingRect(c)[:2]) + np.array(cv2.boundingRect(c)[2:]) / 2 - mid
                ),
            )
            x, y, cw, ch = cv2.boundingRect(contour)
            openings = []
            for index, wire in enumerate(profile.inner_wires(), start=1):
                points = np.concatenate([scan_points(edge) for edge in wire.edges()])
                openings.append(
                    {
                        "index": index,
                        "cad_sheet_aligned_bounds_mm": (
                            (points.max(axis=0) - points.min(axis=0)) * [210 / w, 297 / h]
                        ).tolist(),
                        "cad_to_ink_distance_mm": ink_distances(points, distance, 210 / w),
                    }
                )
            page["parts"].append(
                {
                    "part": name,
                    "cad_sheet_aligned_bounds_mm": ((high - low) * [210 / w, 297 / h]).tolist(),
                    "ink_sheet_aligned_bounds_mm": [(cw - 1) * 210 / w, (ch - 1) * 297 / h],
                    "cad_outer_to_ink_distance_mm": ink_distances(outer, distance, 210 / w),
                    "openings": openings,
                }
            )
            for edge in profile.edges():
                points = " ".join(f"{px:.2f},{py:.2f}" for px, py in scan_points(edge))
                polylines.append(f'<polyline points="{points}"/>')
        encoded = base64.b64encode(scan_path.read_bytes()).decode()
        svg = (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h + 100}" '
            f'viewBox="0 0 {w} {h + 100}">'
            '<rect width="100%" height="100%" fill="white"/>'
            '<text x="30" y="40" font-family="sans-serif" font-size="28">'
            f"Scan {number} at nominal A4: red = original ink; blue = CAD outlines</text>"
            '<text x="30" y="78" font-family="sans-serif" font-size="25">'
            "Original JPEG preserved; see a4-comparison.json for registration and limits.</text>"
            f'<g transform="translate(0,100)"><image width="{w}" height="{h}" '
            f'href="data:image/jpeg;base64,{encoded}"/>'
            '<g fill="none" stroke="#0066dd" stroke-width="2.5" stroke-opacity="0.85">'
            + "".join(polylines)
            + "</g></g></svg>\n"
        )
        (OUTPUT / f"scan-{number}-cad-overlay.svg").write_text(svg)
        report["scans"].append(page)
    (OUTPUT / "a4-comparison.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    compare()
