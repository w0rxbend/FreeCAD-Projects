"""One-time reference extraction, run with FreeCADCmd (not the build runtime).

Reads the saved BREP shapes directly, avoiding recomputation in a newer FreeCAD.
Writes analytic profile data and reference STEP solids for independent comparison.
"""

import hashlib
import json
import tempfile
import zipfile
from pathlib import Path

import FreeCAD as App
import Part

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "Tigerbee.FCStd"
PROFILES = ROOT / "src/tigerbee/profiles"
REFERENCES = ROOT / "refs/baseline"


def coordinates(point):
    return [round(point.x, 10), round(point.y, 10)]


def extract():
    PROFILES.mkdir(parents=True, exist_ok=True)
    REFERENCES.mkdir(parents=True, exist_ok=True)
    specs = [
        ("arm-type-1", "Body001", 3.5, 0),
        ("arm-type-2", "Body002", 3.62, 180),
        ("camera-plate", "Body", 9.25, 0),
    ]
    with zipfile.ZipFile(SOURCE) as archive, tempfile.TemporaryDirectory() as directory:
        for name, body, datum_radius, rotation in specs:
            brep = Path(directory) / f"{body}.brp"
            brep.write_bytes(archive.read(f"{body}.Shape.brp"))
            shape = Part.Shape()
            shape.read(str(brep))
            bottom = next(
                face
                for face in shape.Faces
                if face.BoundBox.ZLength < 1e-7 and abs(face.BoundBox.ZMin) < 1e-7
            )
            datum = next(
                edge.Curve.Center
                for edge in bottom.Edges
                if isinstance(edge.Curve, Part.Circle)
                and edge.isClosed()
                and abs(edge.Curve.Radius - datum_radius) < 1e-7
            )
            datum_values = coordinates(datum)
            shape.translate(App.Vector(-datum.x, -datum.y, 0))
            shape.rotate(App.Vector(), App.Vector(0, 0, 1), rotation)
            bottom = next(
                face
                for face in shape.Faces
                if face.BoundBox.ZLength < 1e-7 and abs(face.BoundBox.ZMin) < 1e-7
            )
            loops = []
            for wire in bottom.Wires:
                segments = []
                for edge in wire.Edges:
                    if isinstance(edge.Curve, Part.Circle) and edge.isClosed():
                        segments.append(
                            {
                                "kind": "circle",
                                "center": coordinates(edge.Curve.Center),
                                "radius": edge.Curve.Radius,
                            }
                        )
                    elif isinstance(edge.Curve, Part.Circle):
                        points = [
                            coordinates(
                                edge.valueAt(
                                    edge.FirstParameter
                                    + fraction * (edge.LastParameter - edge.FirstParameter)
                                )
                            )
                            for fraction in (0, 0.5, 1)
                        ]
                        segments.append({"kind": "arc", "points": points})
                    elif isinstance(edge.Curve, Part.Line):
                        segments.append(
                            {
                                "kind": "line",
                                "points": [
                                    coordinates(edge.Vertexes[0].Point),
                                    coordinates(edge.Vertexes[-1].Point),
                                ],
                            }
                        )
                    else:
                        raise ValueError(f"Unsupported curve: {type(edge.Curve)}")
                loops.append({"outer": wire.isSame(bottom.OuterWire), "segments": segments})
            bounds = shape.BoundBox
            data = {
                "part": name,
                "source": "Tigerbee.FCStd",
                "source_body": body,
                "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
                "datum_source_xy": datum_values,
                "rotation_deg": rotation,
                "thickness": bounds.ZLength,
                "reference_volume": shape.Volume,
                "reference_bounds": [bounds.XMin, bounds.YMin, bounds.XMax, bounds.YMax],
                "loops": loops,
            }
            (PROFILES / f"{name}.json").write_text(json.dumps(data, indent=2) + "\n")
            shape.exportStep(str(REFERENCES / f"{name}.step"))
            print(name, "valid", shape.isValid(), "loops", len(loops), "volume", shape.Volume)


if __name__ == "__main__":
    extract()
