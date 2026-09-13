"""Build independent solids from analytic profiles; original CAD is never imported."""

import json
from dataclasses import dataclass, replace
from importlib.resources import files
from math import isfinite

from build123d import Axis, Edge, Face, Keep, Part, Plane, Pos, ThreePointArc, Wire, extrude, split

from tigerbee.references import ARM_THICKNESS_MM, PLATE_THICKNESS_MM

PARTS = ("arm-type-1", "arm-type-2", "camera-plate", "rear-plate", "top-plate")


@dataclass(frozen=True)
class PartParameters:
    """Dimensions in mm. None uses the user-specified 5 mm arms / 3 mm plates."""

    thickness: float | None = None
    mounting_hole_diameter: float = 3.2
    center_hole_diameter: float | None = None
    length_extension: float = 0.0

    def validate(self) -> None:
        for name in ("thickness", "mounting_hole_diameter", "center_hole_diameter"):
            value = getattr(self, name)
            if value is not None and (not isfinite(value) or value <= 0):
                raise ValueError(f"{name} must be finite and greater than zero")
        if not isfinite(self.length_extension) or not 0 <= self.length_extension <= 50:
            raise ValueError("length_extension must be finite and between 0 and 50 mm")


def profile_data(name: str) -> dict:
    if name not in PARTS:
        raise ValueError(f"Unknown part {name!r}; choose from {', '.join(PARTS)}")
    return json.loads(files("tigerbee").joinpath("profiles", f"{name}.json").read_text())


DEFAULT_PARAMETERS = PartParameters()
REFERENCE_PARAMETERS = PartParameters(mounting_hole_diameter=3.0)


def build_profile(name: str, parameters: PartParameters = DEFAULT_PARAMETERS) -> Face:
    """Build the engineered profile: nominal mirrored plates and relieved CAD arms."""
    parameters.validate()
    profile_data(name)  # Validate the catalog before selecting the design builder.
    if name.endswith("-plate"):
        from tigerbee.layout import plate_mounting_holes
        from tigerbee.plates import build_plate_profile

        if parameters.length_extension:
            raise ValueError("length_extension is only supported for arms")
        if parameters.center_hole_diameter is not None and name != "camera-plate":
            raise ValueError(f"{name} has no center hole to resize")
        return build_plate_profile(
            name,
            plate_mounting_holes(name),
            parameters.mounting_hole_diameter,
            center_hole_diameter=parameters.center_hole_diameter,
        )
    from tigerbee.layout import trim_arm_profile

    reference = build_reference_profile(name, replace(parameters, length_extension=0))
    face = trim_arm_profile(reference, name)
    return extend_arm(face, parameters.length_extension) if parameters.length_extension else face


def build_reference_profile(name: str, parameters: PartParameters = REFERENCE_PARAMETERS) -> Face:
    """Reconstruct the preserved source for dimensional comparisons and provenance."""
    parameters.validate()
    data = profile_data(name)
    if parameters.center_hole_diameter is not None and not any(
        segment["kind"] == "circle" and segment["center"] == [0, 0]
        for loop in data["loops"]
        for segment in loop["segments"]
    ):
        raise ValueError(f"{name} has no center hole to resize")
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
                case "spline":
                    edges.append(
                        Edge.make_spline([tuple(p) for p in segment["points"]], periodic=True)
                    )
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
    if parameters.length_extension:
        if not name.startswith("arm-type-"):
            raise ValueError("length_extension is only supported for arms")
        face = extend_arm(face, parameters.length_extension)
    return face


def extend_arm(profile: Face, extension: float) -> Face:
    """Insert a constant-width shaft section, preserving both mounting ends."""
    seam_y = -60.0
    root, motor = split(profile, Plane.XZ.offset(-seam_y), Keep.BOTH).faces().sort_by(Axis.Y)
    seam = next(
        edge
        for edge in root.edges()
        if all(abs(vertex.Y - seam_y) < 1e-6 for vertex in edge.vertices())
    )
    xs = [vertex.X for vertex in seam.vertices()]
    corners = [
        (min(xs), seam_y),
        (max(xs), seam_y),
        (max(xs), seam_y - extension),
        (min(xs), seam_y - extension),
    ]
    if profile.normal_at().Z > 0:
        corners.reverse()
    bridge = Face(Wire.make_polygon(corners, close=True))
    joined = motor.fuse(Pos(0, -extension) * root, bridge)
    faces = joined.faces()
    if len(faces) != 1 or not faces[0].is_valid:
        raise ValueError("Arm extension did not produce one continuous profile")
    return faces[0]


def build_part(name: str, parameters: PartParameters = DEFAULT_PARAMETERS) -> Part:
    """Build at Z=0: plates use frame XY; arms retain their motor-hole datum."""
    profile = build_profile(name, parameters)
    thickness = parameters.thickness
    if thickness is None:
        thickness = ARM_THICKNESS_MM if name.startswith("arm-type-") else PLATE_THICKNESS_MM
    part = extrude(profile, amount=thickness, dir=(0, 0, 1))
    part.label = name
    if not part.is_valid or len(part.solids()) != 1 or part.volume <= 0:
        raise ValueError(f"Parameters do not produce one valid solid for {name}")
    return part
