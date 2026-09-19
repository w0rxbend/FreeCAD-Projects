"""Measure the manufactured BREP, independently of matching parameter declarations."""

from math import hypot
from typing import TYPE_CHECKING

from build123d import GeomType, Part, Plane, Solid

from fpv_frame.geometry.datums import Point2
from fpv_frame.geometry.patterns import HolePattern

if TYPE_CHECKING:
    from fpv_frame.assembly.frame import FrameAssembly


def _check_bore(
    part: Part, x: float, y: float, lower: float, upper: float, diameter: float, name: str
) -> float:
    maximum = 0.0
    edges = [edge for edge in part.edges() if edge.geom_type == GeomType.CIRCLE]
    for z in (lower, upper):
        errors = [
            max(
                hypot(edge.arc_center.X - x, edge.arc_center.Y - y),
                abs(edge.arc_center.Z - z),
                abs(edge.radius * 2 - diameter),
            )
            for edge in edges
        ]
        error = min(errors, default=float("inf"))
        if error > 1e-6:
            raise ValueError(
                f"{name}: interface bore at ({x:.4f}, {y:.4f}, {z:.4f}) "
                f"diameter {diameter:.4f} missing or misaligned; error={error:.6f} mm"
            )
        maximum = max(maximum, error)
    witness = Solid.make_cylinder(diameter / 2 - 1e-6, upper - lower, Plane(origin=(x, y, lower)))
    common = part.intersect(witness)
    volume = 0.0 if common is None else sum(abs(shape.volume) for shape in common)
    if volume > 1e-6:
        raise ValueError(f"{name}: interface bore is blocked by {volume:.8f} mm3 of material")
    return maximum


def validate_interfaces(model: "FrameAssembly") -> dict[str, object]:
    params, layout = model.params, model.layout
    checked, maximum = 0, 0.0
    for group in layout.hole_groups:
        for name in group.members:
            lower = params.plate_elevations[name]
            upper = lower + params.plate(name).thickness
            for center in group.pattern.centers:
                maximum = max(
                    maximum,
                    _check_bore(
                        model.parts[name],
                        center.x,
                        center.y,
                        lower,
                        upper,
                        group.pattern.hole_diameter,
                        name,
                    ),
                )
                checked += 1
    for placement in layout.arms:
        for center in placement.interface.hole_axes:
            maximum = max(
                maximum,
                _check_bore(
                    model.parts[placement.name],
                    center.x,
                    center.y,
                    params.arm_elevation,
                    params.arm_elevation + params.arm.thickness,
                    params.clearance_hole_diameter,
                    placement.name,
                ),
            )
            checked += 1
    motor = HolePattern.bolt_circle(
        params.motor.bolt_circle_diameter, 4, params.clearance_hole_diameter, angle_deg=45
    )
    if params.arm.profile is None:
        raise ValueError("Motor bore validation requires arm dimensions")
    for placement in layout.arms:
        holes = [
            (Point2(p.x, p.y + params.arm.profile.root_to_motor), motor.hole_diameter)
            for p in motor.centers
        ]
        holes.append(
            (Point2(0, params.arm.profile.root_to_motor), params.motor.center_bore_diameter)
        )
        for point, diameter in holes:
            motor_center = placement.transform.apply(point)
            maximum = max(
                maximum,
                _check_bore(
                    model.parts[placement.name],
                    motor_center.x,
                    motor_center.y,
                    params.arm_elevation,
                    params.arm_elevation + params.arm.thickness,
                    diameter,
                    placement.name,
                ),
            )
            checked += 1
    for datum in layout.standoffs:
        maximum = max(
            maximum,
            _check_bore(
                model.parts[datum.name],
                datum.center.x,
                datum.center.y,
                datum.lower_z,
                datum.upper_z,
                params.hardware.bolt_diameter,
                datum.name,
            ),
        )
        checked += 1
    return {"checked_bores": checked, "maximum_axis_or_diameter_error_mm": maximum}
