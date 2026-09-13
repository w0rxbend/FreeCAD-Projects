"""Thickness presets for the symmetric design; original means source thicknesses."""

from dataclasses import replace

from tigerbee.models import PartParameters

PRESETS = ("original", "product-7inch")


def part_parameters(name: str, preset: str, **overrides: float | None) -> PartParameters:
    if preset not in PRESETS:
        raise ValueError(f"Unknown preset: {preset}")
    thickness = None
    if preset == "product-7inch":
        thickness = 5.0 if name.startswith("arm-type-") else 2.5
    parameters = PartParameters(thickness=thickness)
    changes = {key: value for key, value in overrides.items() if value is not None}
    return replace(parameters, **changes)
