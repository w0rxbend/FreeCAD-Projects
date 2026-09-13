"""Topology gates applied before accepting profiles and physical components."""

from typing import Any

from build123d import GeomType, Shape

GEOMETRY_TOLERANCE = 1e-7


def validate_profile(shape: Shape[Any], *, expected_holes: int | None = None) -> None:
    if len(shape.faces()) != 1:
        raise ValueError("A physical plate profile must contain exactly one face")
    if not shape.is_valid or shape.area <= GEOMETRY_TOLERANCE:
        raise ValueError("Profile must have valid topology and nonzero area")
    face = shape.faces()[0]
    # OCCT bounding boxes include a tolerance margin around spline edges. Check
    # the actual supporting plane instead of interpreting that padding as stock.
    if (
        face.geom_type != GeomType.PLANE
        or abs(face.center().Z) > GEOMETRY_TOLERANCE
        or abs(face.normal_at().X) > GEOMETRY_TOLERANCE
        or abs(face.normal_at().Y) > GEOMETRY_TOLERANCE
        or abs(abs(face.normal_at().Z) - 1) > GEOMETRY_TOLERANCE
    ):
        raise ValueError("Manufacturing profile must lie in the XY plane at Z=0")
    if any(not wire.is_valid or not wire.is_closed for wire in shape.wires()):
        raise ValueError("Profile wires must be valid and closed")
    hole_count = len(shape.faces()[0].inner_wires())
    if expected_holes is not None and hole_count != expected_holes:
        raise ValueError(f"Profile hole count {hole_count}; expected {expected_holes}")


def validate_solid(shape: Shape[Any]) -> None:
    if len(shape.solids()) != 1:
        raise ValueError("A physical component must contain exactly one solid")
    if not shape.is_valid or not shape.is_manifold or shape.volume <= GEOMETRY_TOLERANCE:
        raise ValueError("Component must be a valid closed manifold with nonzero volume")
