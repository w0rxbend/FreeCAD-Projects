"""One handed canonical carbon arm, extruded from its manufacturing profile.

The local root-hole midpoint is (0, 0); motor center lies on +Y. The paddle and
shaft are mathematically symmetric. The two interlocking root fingers are handed.
Sparse root landmark ratios describe the observed lobes, not independent hole axes.
"""

from build123d import Edge, Face, Part, Plane, Wire, extrude

from fpv_frame.geometry.layout import build_layout
from fpv_frame.geometry.patterns import HolePattern
from fpv_frame.parameters.arms import ArmProfileParameters
from fpv_frame.parameters.frame import FrameParameters
from fpv_frame.validation.geometry import validate_profile, validate_solid


def _outline(dimensions: ArmProfileParameters) -> Wire:
    """Lines/circular arcs for the paddle; sparse cubic transitions at shaft/root."""
    length = dimensions.root_to_motor
    neck = length - dimensions.motor_neck_length
    shaft = dimensions.shaft_width / 2
    paddle = dimensions.motor_paddle_width / 2
    waist = dimensions.motor_waist_width / 2
    tip = length + dimensions.motor_tip_extension
    # Motor bolt-circle quadrants establish the two paddle lobes, at ±0.28 tip extension.
    lobe_offset = dimensions.motor_tip_extension * 0.28
    tip_half_width = dimensions.motor_paddle_width * 0.20
    cap_height = dimensions.motor_tip_extension * 0.12

    # Reference root envelope 38 x 31 mm. These sparse ratios preserve the handed
    # shoulder/outer-notch/finger/central-notch topology when root dimensions vary.
    def root(x: float, y: float) -> tuple[float, float]:
        return x / 38 * dimensions.root_width, y / 31 * dimensions.root_depth

    left_root, right_root = root(-11, -10), root(11, -10)
    left: list[Edge] = [
        Edge.make_bezier(left_root, root(-9, 20), (-shaft, neck - 30), (-shaft, neck)),
        Edge.make_bezier(
            (-shaft, neck),
            (-shaft, length - 14),
            (-paddle, length - 11),
            (-paddle, length - lobe_offset),
        ),
        Edge.make_three_point_arc(
            (-paddle, length - lobe_offset),
            (-waist, length),
            (-paddle, length + lobe_offset),
        ),
        Edge.make_line((-paddle, length + lobe_offset), (-tip_half_width, tip - cap_height)),
    ]
    right = [edge.mirror(Plane.YZ) for edge in reversed(left)]
    cap = Edge.make_three_point_arc(
        (-tip_half_width, tip - cap_height),
        (0, tip),
        (tip_half_width, tip - cap_height),
    )
    # Root sequence proceeds around the outside of the right shoulder and finger,
    # into the center relief, around the left finger, and back to the shaft.
    root_edges = [
        Edge.make_bezier(right_root, root(12, -15), root(16, -18), root(19, -20)),
        Edge.make_three_point_arc(root(19, -20), root(19, -21.5), root(17, -22.5)),
        Edge.make_bezier(root(17, -22.5), root(15, -23.5), root(14, -21.5), root(12, -23.5)),
        Edge.make_three_point_arc(root(12, -23.5), root(11, -25), root(12, -27)),
        Edge.make_bezier(root(12, -27), root(11, -29), root(9, -31), root(7.5, -30)),
        Edge.make_bezier(root(7.5, -30), root(6, -29), root(4, -23), root(2.5, -21)),
        Edge.make_line(root(2.5, -21), root(1.7, -16.5)),
        Edge.make_three_point_arc(root(1.7, -16.5), root(1, -15.8), root(0.3, -16.5)),
        Edge.make_bezier(root(0.3, -16.5), root(1, -20), root(-1.5, -24), root(-3.5, -29)),
        Edge.make_bezier(root(-3.5, -29), root(-5, -33), root(-7, -30), root(-9.5, -28)),
        Edge.make_three_point_arc(root(-9.5, -28), root(-10.5, -26.5), root(-10, -25)),
        Edge.make_bezier(root(-10, -25), root(-9, -22.5), root(-12, -22), root(-14, -23.5)),
        Edge.make_bezier(root(-14, -23.5), root(-16, -23), root(-18, -21), root(-19, -20)),
        Edge.make_bezier(root(-19, -20), root(-19.5, -19), root(-12, -16), left_root),
    ]
    return Wire([*left, cap, *right, *root_edges])


def _diamond(dimensions: ArmProfileParameters) -> Wire:
    center = dimensions.root_to_motor + dimensions.diamond_offset
    half_width = dimensions.diamond_width / 2
    half_height = dimensions.diamond_height / 2
    outline = Wire.make_polygon(
        [
            (0, center + half_height),
            (half_width, center),
            (0, center - half_height),
            (-half_width, center),
        ],
        close=True,
    )
    # Small rounded corners remove tracing kinks and give a machinable internal contour.
    face = Face(outline)
    return face.fillet_2d(min(half_width, half_height) * 0.18, face.vertices()).outer_wire()


def arm_profile(params: FrameParameters) -> Face:
    dimensions = params.arm.profile
    if dimensions is None:
        raise ValueError("Arm profile dimensions must be populated before building geometry")
    layout = build_layout(params)
    holes = [
        Wire.make_circle(
            layout.root_pattern.hole_diameter / 2, Plane(origin=(center.x, center.y, 0))
        )
        for center in layout.root_pattern.centers
    ]
    motor = HolePattern.bolt_circle(
        params.motor.bolt_circle_diameter,
        4,
        params.clearance_hole_diameter,
        angle_deg=45,
    )
    holes.extend(
        Wire.make_circle(
            motor.hole_diameter / 2,
            Plane(origin=(center.x, dimensions.root_to_motor + center.y, 0)),
        )
        for center in motor.centers
    )
    holes.append(
        Wire.make_circle(
            params.motor.center_bore_diameter / 2,
            Plane(origin=(0, dimensions.root_to_motor, 0)),
        )
    )
    holes.append(_diamond(dimensions))
    profile = Face(_outline(dimensions), holes)
    validate_profile(profile, expected_holes=8)
    return profile


def build_arm(params: FrameParameters) -> Part:
    part = extrude(arm_profile(params), amount=params.arm.thickness, dir=(0, 0, 1))
    part.label = "arm"
    validate_solid(part)
    return part
