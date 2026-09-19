"""Export the exact CAD wires; annotations never change manufacturing geometry."""

import xml.etree.ElementTree as ET
from collections.abc import Mapping
from pathlib import Path

from build123d import Color, Compound, ExportSVG, Face, GeomType, LineType, Unit

SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NS)


def _element(parent: ET.Element, tag: str, **attributes: str) -> ET.Element:
    return ET.SubElement(parent, f"{{{SVG_NS}}}{tag}", attributes)


def _annotate(path: Path, profile: Face, label: str) -> None:
    tree = ET.parse(path)
    root = tree.getroot()
    bounds = profile.bounding_box()
    x0, x1 = bounds.min.X, bounds.max.X
    y0, y1 = -bounds.max.Y, -bounds.min.Y
    # SVG drawing coordinates invert CAD Y. Text stays upright in this sibling group.
    group = _element(root, "g", stroke="#28547a", fill="none")
    group.set("stroke-width", "0.15")

    def line(a: float, b: float, c: float, d: float) -> None:
        _element(group, "line", x1=str(a), y1=str(b), x2=str(c), y2=str(d))

    def text(x: float, y: float, value: str, size: float = 2.5) -> None:
        node = _element(group, "text", x=str(x), y=str(y), fill="#28547a", stroke="none")
        node.set("font-size", str(size))
        node.set("font-family", "sans-serif")
        node.text = value

    line(x0, y1 + 5, x1, y1 + 5)
    for x in (x0, x1):
        line(x, y1 + 1, x, y1 + 7)
        line(x - 1, y1 + 6, x + 1, y1 + 4)
    text((x0 + x1) / 2 - 7, y1 + 4, f"{bounds.size.X:.2f} mm")
    line(x1 + 5, y0, x1 + 5, y1)
    for y in (y0, y1):
        line(x1 + 1, y, x1 + 7, y)
        line(x1 + 4, y + 1, x1 + 6, y - 1)
    text(x1 + 7, (y0 + y1) / 2, f"{bounds.size.Y:.2f} mm")
    line(-3, 0, 3, 0)
    line(0, -3, 0, 3)
    text(3, -2, "DATUM (0, 0)", 2)
    for wire in profile.inner_wires():
        edges = wire.edges()
        if len(edges) == 1 and edges[0].geom_type == GeomType.CIRCLE:
            edge = edges[0]
            center = edge.arc_center
            x, y, radius = center.X, -center.Y, edge.radius
            line(x - radius - 1, y, x + radius + 1, y)
            line(x, y - radius - 1, x, y + radius + 1)
            text(x + radius + 1, y - radius - 1, f"Ø{2 * radius:.2f}", 1.8)
    text(x0, y0 - 7, label)
    text(x0, y0 - 3, "mm · SCALE 1:1 · Print at 100%", 2)
    # Expand paper without scaling any geometry, including a datum outside the profile.
    left, top = min(x0 - 10, -6), min(y0 - 12, -6)
    right, bottom = max(x1 + 35, 27), max(y1 + 12, 6)
    root.set("viewBox", f"{left} {top} {right - left} {bottom - top}")
    root.set("width", f"{right - left}mm")
    root.set("height", f"{bottom - top}mm")
    tree.write(path, encoding="us-ascii", xml_declaration=True)


def export_drawings(
    profiles: Mapping[str, Face], assembly: Compound, output: Path, *, include_assembly: bool = True
) -> list[Path]:
    """Create analytic XY cutting paths and true orthographic assembly views in mm."""
    output.mkdir(parents=True, exist_ok=True)
    result = []
    for name, profile in profiles.items():
        if profile.bounding_box().size.Z > 1e-6:
            raise ValueError(f"Profile {name!r} must lie in an XY plane for 1:1 SVG export")
        drawing = ExportSVG(unit=Unit.MM, scale=1, margin=5, fit_to_stroke=False)
        drawing.add_shape(profile)
        path = output / f"{name}.svg"
        drawing.write(path)
        result.append(path)
        annotated = output / f"{name}.dimensioned.svg"
        drawing.write(annotated)
        _annotate(annotated, profile, name)
        result.append(annotated)
    if not include_assembly:
        return result
    views = {
        "top": ((0, 0, 1000), (0, 1, 0)),
        "bottom": ((0, 0, -1000), (0, 1, 0)),
        "front": ((0, 1000, 0), (0, 0, 1)),
        "side": ((1000, 0, 0), (0, 0, 1)),
    }
    for name, (origin, up) in views.items():
        visible, hidden = assembly.project_to_viewport(origin, up, look_at=(0, 0, 0))
        drawing = ExportSVG(unit=Unit.MM, scale=1, margin=5, fit_to_stroke=False)
        drawing.add_layer("hidden", line_color=Color(0.6, 0.6, 0.6), line_type=LineType.DASHED)
        drawing.add_layer("visible", line_weight=0.15)
        drawing.add_shape(hidden, "hidden")
        drawing.add_shape(visible, "visible")
        path = output / f"assembly_{name}.svg"
        drawing.write(path)
        result.append(path)
    return result
