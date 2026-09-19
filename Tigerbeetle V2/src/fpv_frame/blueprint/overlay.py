"""CAD-derived diagnostic overlays; original scans are never written."""

import base64
from dataclasses import dataclass
from math import ceil
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape

from build123d import Shape
from PIL import Image, ImageDraw

from fpv_frame.blueprint.calibration import Calibration, Point
from fpv_frame.blueprint.measurements import verify_sources
from fpv_frame.validation.geometry import validate_profile


@dataclass(frozen=True)
class ProfileOverlay:
    name: str
    profile: Shape[Any]
    calibration: Calibration
    hole_centers: tuple[Point, ...] = ()
    interface_centers: tuple[Point, ...] = ()


def profile_polylines(shape: Shape[Any], *, step_mm: float = 0.25) -> tuple[tuple[Point, ...], ...]:
    """Sample BREP edges for raster diagnostics; manufacturing SVG uses exact curves."""
    if not 0 < step_mm <= 1:
        raise ValueError("Diagnostic sampling step must be in (0, 1] mm")
    validate_profile(shape)
    lines = []
    for edge in shape.edges():
        count = max(2, ceil(edge.length / step_mm))
        points = tuple(edge.position_at(i / count) for i in range(count + 1))
        lines.append(tuple((point.X, point.Y) for point in points))
    return tuple(lines)


def write_overlay(
    root: Path, scan: str, profiles: tuple[ProfileOverlay, ...], output_dir: Path
) -> tuple[Path, Path]:
    """Render registered profiles, axes and shared feature centers over the raw scan."""
    if scan not in ("Scan_1", "Scan_2") or not profiles:
        raise ValueError("Overlay requires Scan_1 or Scan_2 and at least one CAD profile")
    verify_sources(root)
    source = root / "references" / "source" / f"{scan}.jpeg"
    output_dir = output_dir.resolve()
    protected = (root / "references" / "source").resolve()
    if output_dir == protected or protected in output_dir.parents:
        raise ValueError("Overlay cannot be written inside immutable source directory")
    output_dir.mkdir(parents=True, exist_ok=True)
    with Image.open(source) as original:
        canvas = original.convert("RGB")
    width, height = canvas.size
    draw = ImageDraw.Draw(canvas)
    encoded = base64.b64encode(source.read_bytes()).decode("ascii")
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">',
        "<title>CAD profile overlay: red source, blue CAD, green holes, magenta interfaces</title>",
        f'<image width="{width}" height="{height}" href="data:image/jpeg;base64,{encoded}"/>',
    ]
    for item in profiles:
        svg.append(f'<g id="{escape(item.name, {chr(34): "&quot;"})}">')
        for line in profile_polylines(item.profile):
            pixels = tuple(item.calibration.to_pixels(point) for point in line)
            draw.line(pixels, fill="#0066cc", width=3)
            coordinates = " ".join(f"{x:.3f},{y:.3f}" for x, y in pixels)
            svg.append(
                f'<polyline points="{coordinates}" fill="none" stroke="#0066cc" stroke-width="3"/>'
            )
        for axis in (((-15.0, 0.0), (15.0, 0.0)), ((0.0, -15.0), (0.0, 15.0))):
            start, end = (item.calibration.to_pixels(point) for point in axis)
            draw.line((start, end), fill="#777777", width=1)
            svg.append(
                f'<path d="M{start[0]},{start[1]} L{end[0]},{end[1]}" '
                'stroke="#777777" stroke-width="1" stroke-dasharray="8 5"/>'
            )
        for centers, color in ((item.hole_centers, "#00883c"), (item.interface_centers, "#c000c0")):
            for point in centers:
                x, y = item.calibration.to_pixels(point)
                draw.line(((x - 8, y), (x + 8, y)), fill=color, width=2)
                draw.line(((x, y - 8), (x, y + 8)), fill=color, width=2)
                svg.append(
                    f'<path d="M{x - 8},{y}h16 M{x},{y - 8}v16" stroke="{color}" stroke-width="2"/>'
                )
        svg.append("</g>")
    svg.append("</svg>")
    svg_path = output_dir / f"{scan}_overlay.svg"
    png_path = output_dir / f"{scan}_overlay.png"
    svg_path.write_text("\n".join(svg), encoding="utf-8")
    canvas.save(png_path)
    return svg_path, png_path
