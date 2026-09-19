"""Explicit equipment envelopes placed from the same datums as the physical frame."""

from typing import TYPE_CHECKING

from build123d import Box, Part, Plane, Solid

from fpv_frame.parameters.equipment import EquipmentParameters

from .clearances import ClearanceEnvelope

if TYPE_CHECKING:
    from fpv_frame.assembly.frame import FrameAssembly


def design_equipment_envelopes(
    model: "FrameAssembly", parameters: EquipmentParameters,
) -> tuple[ClearanceEnvelope, ...]:
    """Build supported nominal geometry, without claiming universal hardware compatibility.

    Board boxes include components but omit cylindrical mounting keepouts. Stack
    hardware is a conservative solid cylinder, with intended plate-face contact.
    Fit is assessed separately by validate_clearances against every actual solid.
    """
    center = model.layout.body_point(0, 0)
    camera_upper = (
        model.params.plate_elevations["scan1_body"]
        + model.params.plate("scan1_body").thickness
    )
    esc_lower = camera_upper + parameters.stack_bottom_gap
    fc_lower = esc_lower + parameters.esc_height + parameters.board_gap
    fc_upper = fc_lower + parameters.fc_height
    pattern = next(
        group.pattern for group in model.layout.hole_groups
        if group.name == "central_stack_square"
    )

    def board(width: float, length: float, height: float, lower: float) -> Part:
        shape = Box(width, length, height).translate((center.x, center.y, lower + height / 2))
        for axis in pattern.centers:
            radius = parameters.stack_keepout_diameter / 2
            if (abs(axis.x - center.x) + radius >= width / 2
                    or abs(axis.y - center.y) + radius >= length / 2):
                raise ValueError("Board footprint must contain all shared stack mounting keepouts")
            bore = Solid.make_cylinder(
                radius, height + 2,
                Plane(origin=(axis.x, axis.y, lower - 1)),
            )
            shape = shape - bore
        return shape

    camera_center = model.layout.body_point(
        0, model.layout.dimensions.front_tip_y - parameters.camera_front_inset,
    )
    camera = Box(
        parameters.camera_width, parameters.camera_length, parameters.camera_height,
    ).translate((
        camera_center.x, camera_center.y,
        camera_upper + parameters.camera_bottom_gap + parameters.camera_height / 2,
    ))
    envelopes = [
        ClearanceEnvelope("ESC", board(
            parameters.esc_width, parameters.esc_length, parameters.esc_height, esc_lower,
        ), parameters.minimum_gap),
        ClearanceEnvelope("FC", board(
            parameters.fc_width, parameters.fc_length, parameters.fc_height, fc_lower,
        ), parameters.minimum_gap),
        ClearanceEnvelope("camera", camera, parameters.minimum_gap),
    ]
    for index, axis in enumerate(pattern.centers):
        hardware = Part(Solid.make_cylinder(
            parameters.stack_hardware_diameter / 2, fc_upper - camera_upper,
            Plane(origin=(axis.x, axis.y, camera_upper)),
        ).wrapped)
        envelopes.append(ClearanceEnvelope(f"stack_hardware_{index + 1}", hardware, 0.0))
    return tuple(envelopes)
