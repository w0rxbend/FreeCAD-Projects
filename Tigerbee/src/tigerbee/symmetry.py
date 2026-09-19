"""Derive exactly symmetric profiles without changing the saved reference geometry."""

from itertools import pairwise
from math import isfinite
from typing import Literal

from build123d import Edge, Face, GeomType, Keep, Plane, Wire, split
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeEdge  # type: ignore[import-untyped]


def _split_spline_spans(wire: Wire) -> Wire:
    """Keep exact curves, with one polynomial span per spline edge.

    OCCT mass-property quadrature does not reliably integrate the long, periodic
    scan splines as single edges. Exposing their existing knot spans fixes both
    planar areas and extruded volumes without tessellating the design outline.
    """
    edges = []
    for edge in wire.edges():
        if edge.geom_type != GeomType.BSPLINE:
            edges.append(edge)
            continue
        adaptor = edge.geom_adaptor()
        curve = adaptor.BSpline()
        first, last = adaptor.FirstParameter(), adaptor.LastParameter()
        parameters = [first]
        parameters.extend(
            curve.Knot(index)
            for index in range(1, curve.NbKnots() + 1)
            if first + 1e-10 < curve.Knot(index) < last - 1e-10
        )
        parameters.append(last)
        for start, end in pairwise(parameters):
            segment = BRepBuilderAPI_MakeEdge(curve, start, end).Edge()
            segment.Orientation(edge.wrapped.Orientation())
            edges.append(Edge(segment))
    return Wire(edges)


def stabilize_profile(profile: Face) -> Face:
    """Preserve a planar profile exactly while making spline mass properties reliable.

    Use this after Boolean edits to scan-derived faces: those operations may
    combine neighbouring spline edges again. Analytic circles and arcs remain
    analytic. Each resulting spline edge follows its original curve exactly.
    """
    if not profile.is_valid or not profile.is_planar:
        raise ValueError("Profile must be a valid planar face")
    result = Face(
        _split_spline_spans(profile.outer_wire()),
        [_split_spline_spans(wire) for wire in profile.inner_wires()],
    )
    if not result.is_valid or len(result.faces()) != 1:
        raise ValueError("Spline subdivision did not preserve one valid profile")
    return result


def symmetrize_profile(
    profile: Face,
    axis_x: float = 0.0,
    side: Literal["left", "right"] = "left",
) -> Face:
    """Mirror one selected half across x=axis_x, retaining its complete geometry.

    The face must lie in a plane parallel to XY and cross the symmetry axis.
    Off-axis openings are duplicated from the selected half; openings crossing
    the axis are halved and mirrored along with the outline. For assembly hole
    patterns, remove existing holes first and cut the shared pattern afterwards.
    The saved profile is never mutated.
    """
    if not isfinite(axis_x):
        raise ValueError("axis_x must be finite")
    if side not in ("left", "right"):
        raise ValueError("side must be 'left' or 'right'")
    if not profile.is_valid or not profile.is_planar:
        raise ValueError("Profile must be a valid planar face")
    bounds = profile.bounding_box()
    if bounds.size.Z > 1e-6:
        raise ValueError("Profile must be parallel to the XY plane")
    if not bounds.min.X < axis_x < bounds.max.X:
        raise ValueError("Symmetry axis must cross the profile")
    plane = Plane(origin=(axis_x, 0, 0), x_dir=(0, 1, 0), z_dir=(1, 0, 0))
    half = split(profile, plane, Keep.BOTTOM if side == "left" else Keep.TOP)
    joined = half.fuse(half.mirror(plane)).clean()
    faces = joined.faces()
    if len(faces) != 1 or not faces[0].is_valid:
        raise ValueError("Mirroring must produce one connected valid profile")
    return stabilize_profile(faces[0])
