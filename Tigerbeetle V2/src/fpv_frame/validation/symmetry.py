"""Bilateral symmetry compares actual material, including every relief and bore."""

from typing import TYPE_CHECKING

from build123d import Plane

if TYPE_CHECKING:
    from fpv_frame.assembly.frame import FrameAssembly


def validate_symmetry(model: "FrameAssembly") -> dict[str, object]:
    pairs: list[tuple[str, str]] = [
        (plate.component_id, plate.component_id) for plate in model.params.plates
    ]
    pairs.extend(
        (name, name.replace("_left", "_right")) for name in model.parts if name.endswith("_left")
    )
    maximum = 0.0
    plane = Plane(origin=(model.layout.body_origin.x, 0, 0), z_dir=(1, 0, 0))
    for left, right in pairs:
        mirrored = model.parts[left].mirror(plane)
        other = model.parts[right]
        difference = abs(mirrored.cut(other).volume) + abs(other.cut(mirrored).volume)
        maximum = max(maximum, difference)
        if difference > 1e-5:
            raise ValueError(f"bilateral symmetry failed: {left}/{right}: {difference:.8f} mm3")
    return {
        "checked_pairs": len(pairs),
        "maximum_difference_mm3": maximum,
        "intentional_asymmetry": "Individual arm roots are handed; left/right mates reflect.",
    }
