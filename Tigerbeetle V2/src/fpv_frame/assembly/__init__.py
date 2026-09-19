"""Public assembly factory and measured mechanical validation report."""

from math import isclose

from fpv_frame.validation.clearances import ClearanceEnvelope, validate_clearances
from fpv_frame.validation.equipment import design_equipment_envelopes
from fpv_frame.validation.geometry import validate_profile, validate_solid
from fpv_frame.validation.interfaces import validate_interfaces
from fpv_frame.validation.interference import validate_interference
from fpv_frame.validation.manufacturing import validate_manufacturing
from fpv_frame.validation.symmetry import validate_symmetry

from .frame import FrameAssembly, build_assembly

__all__ = ["FrameAssembly", "build_assembly", "validate_assembly"]


def validate_assembly(
    model: FrameAssembly, *, envelopes: tuple[ClearanceEnvelope, ...] | None = None
) -> dict[str, object]:
    expected: set[str] = {plate.component_id for plate in model.params.plates}
    expected.update(arm.name for arm in model.layout.arms)
    expected.update(standoff.name for standoff in model.layout.standoffs)
    if (
        set(model.parts) != expected
        or set(model.profiles) != expected
        or len(model.compound.solids()) != len(expected)
    ):
        raise ValueError("Assembly component inventory differs from shared layout")
    # Opening counts encode the accepted physical feature inventory independently
    # of builders, so omitting a relief cannot silently redefine expected geometry.
    holes = {"scan1_body": 30, "scan2_broad": 32, "scan2_long": 30}
    holes.update({arm.name: 8 for arm in model.layout.arms})
    holes.update({standoff.name: 1 for standoff in model.layout.standoffs})
    thicknesses: dict[str, float] = {
        plate.component_id: plate.thickness for plate in model.params.plates
    }
    thicknesses.update({arm.name: model.params.arm.thickness for arm in model.layout.arms})
    thicknesses.update({datum.name: datum.height for datum in model.layout.standoffs})
    for name, profile in model.profiles.items():
        validate_profile(profile, expected_holes=holes[name])
        part = model.parts[name]
        validate_solid(part)
        if not isclose(part.volume, profile.area * thicknesses[name], rel_tol=1e-9, abs_tol=1e-6):
            raise ValueError(
                f"{name}: solid volume differs from its manufacturing profile extrusion"
            )
    interference = validate_interference(model)
    interfaces = validate_interfaces(model)
    symmetry = validate_symmetry(model)
    manufacturing = validate_manufacturing(model)
    if envelopes is None:
        envelopes = design_equipment_envelopes(model, model.params.equipment)
    clearances = validate_clearances(model, envelopes)
    return {
        "valid": True,
        "component_count": len(model.parts),
        "wheelbase_mm": model.layout.wheelbase,
        "profile_opening_counts": {
            name: len(profile.inner_wires()) for name, profile in model.profiles.items()
        },
        "interference": interference,
        "interfaces": interfaces,
        "symmetry": symmetry,
        "manufacturing": manufacturing,
        "clearances": clearances,
    }
