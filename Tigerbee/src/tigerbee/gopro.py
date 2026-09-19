"""Top-plate adapter for a GoPro-style two-finger camera interface.

The seating surface is Z=0, matching the top of the carbon. XY retains the
frame datum. Finger dimensions are nominal compatible dimensions, not a claim
of camera-body or printed-material qualification.
"""

from dataclasses import dataclass
from math import isfinite, sqrt

from build123d import (
    Circle,
    Edge,
    Face,
    GeomType,
    Part,
    Plane,
    Pos,
    RectangleRounded,
    RegularPolygon,
    ThreePointArc,
    Wire,
    extrude,
)

from tigerbee.models import build_profile
from tigerbee.plates import _smooth_outline

GOPRO_HOLDER = "top-plate-gopro-holder"


@dataclass(frozen=True)
class GoProParameters:
    axle_height: float = 18.0

    def validate(self) -> None:
        if not isfinite(self.axle_height) or not 18 <= self.axle_height <= 30:
            raise ValueError("axle_height must be finite and between 18 and 30 mm")


DEFAULT_GOPRO = GoProParameters()


def mounting_centers() -> list[tuple[float, float]]:
    """Read the actual four front accessory circles, never a separate fitted pattern."""
    centers = []
    for wire in build_profile("top-plate").inner_wires():
        edges = wire.edges()
        if len(edges) == 1 and edges[0].geom_type == GeomType.CIRCLE:
            edge = edges[0]
            center = edge.arc_center
            if abs(edge.radius - 2.5) < 1e-6 and abs(center.X) > 20 and center.Y > 50:
                centers.append((center.X, center.Y))
    if len(centers) != 4:
        raise ValueError("Expected four front Ø5 mm top-plate accessory holes")
    return sorted(centers)


def holder_center_y() -> float:
    return sum(y for _, y in mounting_centers()) / 4


def _finger_face(height: float) -> Face:
    # Sketch axes are Y (horizontal) and Z (vertical), then mapped to Plane.YZ.
    edges = [
        Edge.make_line((-12, 4), (12, 4)),
        Edge.make_line((12, 4), (7.5, height)),
        ThreePointArc((7.5, height), (0, height + 7.5), (-7.5, height)).edge(),
        Edge.make_line((-7.5, height), (-12, 4)),
    ]
    face = Face(Wire(edges))
    if face.normal_at().Z < 0:
        face = -face
    # Smooth the two shoulder joins while retaining the circular crown.
    corners = [v for v in face.vertices() if abs(v.Y - height) < 1e-6]
    return face.fillet_2d(1, corners)


def build_gopro_holder(parameters: GoProParameters = DEFAULT_GOPRO) -> Part:
    parameters.validate()
    cy = holder_center_y()
    base = (Pos(0, cy) * RectangleRounded(68, 45, 5)).face()
    for x, y, radius in (
        (0.0, cy + 29.5, 14),
        (0.0, cy - 30.5, 13),
        (49.0, cy, 22),
        (-49.0, cy, 22),
    ):
        base = (base - Pos(x, y) * Circle(radius)).faces()[0]
    base = _smooth_outline(base, 1)
    part = extrude(base, amount=5)
    for x, y in mounting_centers():
        part += Pos(x, y, -2) * extrude(Circle(2.4), amount=2)
        part -= Pos(x, y, -3) * extrude(Circle(1.65), amount=12)
        part -= Pos(x, y, 2) * extrude(Circle(3.3), amount=10)
    profile = Plane.YZ * Pos(cy, 0) * _finger_face(parameters.axle_height)
    # Inner faces preserve the 3 / 3.2 / 3 / 3.2 / 3 compatible stack.
    # The last finger grows only outward to house a removable metal hex nut.
    for x, width in ((-7.7, 3), (-1.5, 3), (4.7, 6.5)):
        part += Pos(x, 0, 0) * extrude(profile, amount=width, dir=(1, 0, 0))
    roots = [
        edge
        for edge in part.edges()
        if all(abs(v.Z - 5) < 1e-6 for v in edge.vertices())
        and abs(edge.center().X) < 13
        and abs(edge.center().Y - cy) < 15
    ]
    part = Part(part.fillet(1, roots).wrapped)
    axle_plane = Plane.YZ * Pos(cy, parameters.axle_height)
    part -= extrude(axle_plane * Circle(2.75), amount=30, both=True)
    nut = axle_plane * RegularPolygon(8.4 / sqrt(3), 6, rotation=30)
    part -= Pos(7, 0, 0) * extrude(nut, amount=5, dir=(1, 0, 0))
    part.label = GOPRO_HOLDER
    if not part.is_valid or len(part.solids()) != 1:
        raise ValueError("GoPro holder must be one valid solid")
    return part
