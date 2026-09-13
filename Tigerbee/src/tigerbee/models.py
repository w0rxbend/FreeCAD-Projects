"""Build independent solids from analytic profiles; original CAD is never imported."""

import json
from dataclasses import dataclass
from importlib.resources import files
from math import isfinite

from build123d import Edge, Face, Part, Plane, ThreePointArc, Wire, extrude

PARTS = ("arm-type-1", "arm-type-2", "camera-plate")


@dataclass(frozen=True)
class PartParameters:
    """Dimensions in mm. None preserves the reference part's measured value."""

    thickness: float | None = None
    mounting_hole_diameter: float = 3.0
    center_hole_diameter: float | None = None

    def validate(self) -> None:
        for name in ("thickness", "mounting_hole_diameter", "center_hole_diameter"):
            value = getattr(self, name)
            if value is not None and (not isfinite(value) or value <= 0):
                raise ValueError(f"{name} must be finite and greater than zero")


def profile_data(name: str) -> dict:
    if name not in PARTS:
        raise ValueError(f"Unknown part {name!r}; choose from {', '.join(PARTS)}")
    return json.loads(files("tigerbee").joinpath("profiles", f"{name}.json").read_text())


DEFAULT_PARAMETERS = PartParameters()


def build_profile(name: str, parameters: PartParameters = DEFAULT_PARAMETERS) -> Face:
    """Recreate the outline and each opening using build123d geometry."""
    parameters.validate()
    data = profile_data(name)
    outer = None
    holes = []
    for loop in data["loops"]:
        edges = []
        for segment in loop["segments"]:
            match segment["kind"]:
                case "line":
                    edges.append(Edge.make_line(*segment["points"]))
                case "arc":
                    edges.append(ThreePointArc(*(tuple(p) for p in segment["points"])).edge())
                case "circle":
                    radius = segment["radius"]
                    if abs(radius - 1.5) < 1e-7:
                        radius = parameters.mounting_hole_diameter / 2
                    if segment["center"] == [0, 0] and parameters.center_hole_diameter:
                        radius = parameters.center_hole_diameter / 2
                    edges.append(Edge.make_circle(radius, Plane(origin=(*segment["center"], 0))))
                case _:
                    raise ValueError(f"Unsupported segment: {segment['kind']}")
        wire = Wire(edges)
        if not wire.is_closed:
            raise ValueError(f"Open profile loop in {name}")
        if loop["outer"]:
            outer = wire
        else:
            holes.append(wire)
    if outer is None:
        raise ValueError(f"Missing outer profile in {name}")
    face = Face(outer, holes)
    if not face.is_valid:
        raise ValueError(f"Parameters create an invalid profile in {name}")
    return face


def build_part(name: str, parameters: PartParameters = DEFAULT_PARAMETERS) -> Part:
    """Build one component at Z=0, with the datum hole at local X=Y=0."""
    profile = build_profile(name, parameters)
    thickness = parameters.thickness
    if thickness is None:
        thickness = profile_data(name)["thickness"]
    part = extrude(profile, amount=thickness, dir=(0, 0, 1))
    part.label = name
    if not part.is_valid or len(part.solids()) != 1 or part.volume <= 0:
        raise ValueError(f"Parameters do not produce one valid solid for {name}")
    return part
