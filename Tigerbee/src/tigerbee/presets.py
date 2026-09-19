"""Current frame dimensions and explicit historical thickness presets."""

from dataclasses import replace

from tigerbee.models import PartParameters, profile_data

PRESETS = ("frame", "original", "product-7inch")


def part_parameters(name: str, preset: str, **overrides: float | None) -> PartParameters:
    if preset not in PRESETS:
        raise ValueError(f"Unknown preset: {preset}")
    thickness = None
    if preset == "original":
        thickness = profile_data(name)["thickness"]
    elif preset == "product-7inch":
        thickness = 5.0 if name.startswith("arm-type-") else 2.5
    parameters = PartParameters(thickness=thickness)
    changes = {key: value for key, value in overrides.items() if value is not None}
    return replace(parameters, **changes)
