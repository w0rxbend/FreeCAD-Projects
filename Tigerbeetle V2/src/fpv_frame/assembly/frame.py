"""Named physical assembly constructed only from the shared mechanical datums."""

from dataclasses import dataclass

from build123d import Axis, Compound, Face, Part, Plane, Vector

from fpv_frame.geometry.layout import FrameLayout, build_layout
from fpv_frame.parameters.frame import FrameParameters
from fpv_frame.parts.arm import arm_profile, build_arm
from fpv_frame.parts.plates import build_plate, plate_profile
from fpv_frame.parts.standoff import build_standoff, standoff_profile


@dataclass(frozen=True)
class FrameAssembly:
    params: FrameParameters
    parts: dict[str, Part]
    profiles: dict[str, Face]
    compound: Compound
    layout: FrameLayout


def build_assembly(params: FrameParameters) -> FrameAssembly:
    layout = build_layout(params)
    profiles: dict[str, Face] = {
        plate.component_id: plate_profile(params, plate.component_id) for plate in params.plates
    }
    canonical_profile = arm_profile(params)
    parts: dict[str, Part] = {
        plate.component_id: build_plate(params, plate.component_id).translate(
            Vector(0, 0, params.plate_elevations[plate.component_id])
        )
        for plate in params.plates
    }
    canonical_arm = build_arm(params)
    for placement in layout.arms:
        transform = placement.transform
        profiles[placement.name] = (
            canonical_profile.mirror(Plane.YZ) if transform.mirror_x else canonical_profile
        )
        arm = canonical_arm.mirror(Plane.YZ) if transform.mirror_x else canonical_arm
        arm = arm.rotate(Axis.Z, transform.angle_deg).translate(
            Vector(transform.origin.x, transform.origin.y, transform.origin.z)
        )
        parts[placement.name] = arm
    for datum in layout.standoffs:
        profiles[datum.name] = standoff_profile(params.hardware)
        parts[datum.name] = build_standoff(params.hardware, datum.height).translate(
            Vector(datum.center.x, datum.center.y, datum.lower_z)
        )
    for name, part in parts.items():
        part.label = name
    compound = Compound(children=list(parts.values()), label="Tigerbeetle_frame")
    return FrameAssembly(params, parts, profiles, compound, layout)
