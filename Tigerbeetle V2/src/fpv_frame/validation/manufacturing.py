"""Measure edge and inter-feature ligaments in the actual manufacturing faces."""

from itertools import combinations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fpv_frame.assembly.frame import FrameAssembly


def validate_manufacturing(model: "FrameAssembly") -> dict[str, object]:
    required = model.params.manufacturing.edge_minimum
    hardware_required = model.params.manufacturing.hardware_wall_minimum
    hardware_names = {datum.name for datum in model.layout.standoffs}
    measurements = {}
    checked = 0
    for name, profile in model.profiles.items():
        outer, holes = profile.outer_wire(), profile.inner_wires()
        distances = [outer.distance_to(hole) for hole in holes]
        distances.extend(a.distance_to(b) for a, b in combinations(holes, 2))
        minimum = min(distances, default=float("inf"))
        checked += len(distances)
        # Purchased tubular hardware has a wall criterion, while machined carbon
        # profiles retain their unchanged edge/inter-feature ligament criterion.
        threshold = hardware_required if name in hardware_names else required
        if minimum + 1e-6 < threshold:
            raise ValueError(
                f"{name}: minimum edge/inter-feature ligament {minimum:.6f} mm "
                f"is below required {threshold:.6f} mm"
            )
        measurements[name] = minimum if distances else None
    return {
        "required_ligament_mm": required,
        "required_hardware_wall_mm": hardware_required,
        "minimum_ligament_mm": measurements,
        "checked_wire_pairs": checked,
        "qualification": "Geometric ligaments only; carbon strength and cutter access unqualified.",
    }
