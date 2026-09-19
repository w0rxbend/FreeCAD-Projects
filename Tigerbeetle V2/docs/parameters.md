# Parameters and Python API

The parameter tree uses frozen dataclasses; nested collections are tuples. Use
`dataclasses.replace` to create a variation. Dimensions are millimeters, layout
angles are degrees, and the exporter angular mesh tolerance is **radians**.
Dimension constructors reject non-finite values and invalid signs. A dimensionally
valid parameter tree must still pass geometry and assembly validation.

## Reference values

Start with `get_preset("reference")` or `get_preset("default")`. They have identical
geometry and differ in their preset evidence description.

| Parameter | Reference value | Meaning / evidence |
| --- | --- | --- |
| `arm.thickness` | 5 | User-confirmed stock |
| Each `plates[i].thickness` | 2 | User-confirmed stock for all three plates |
| `arm.profile.root_to_motor` | 115 | Rounded from A4 observations of 114.66 / 115.59 |
| `arm.profile.root_width`, `root_depth` | 35, 29 | Deliberate local correction from traced approximately 38 × 31 |
| `arm.profile.shaft_width` | 12 | A4-derived nominal shaft width |
| `arm.profile.motor_paddle_width` | 24 | A4-derived nominal paddle width |
| `arm.profile.root_hole_spacing` | 13.75 | Reconciled arm/plate shared axes |
| `motor.bolt_circle_diameter` | 19 | Four-hole opposite-hole distance; square side is 19/√2 |
| `motor.center_bore_diameter` | 6.5 | Nominal reconstruction assumption |
| `stack.primary_pitch`, `secondary_pitch` | 30.5, 20 | Shared electronics hole-pattern pitches |
| `hardware.bolt_diameter` | 3 | Nominal fastener diameter |
| `hardware.standoff_outer_diameter` | 5 | Provisional tubular support outside diameter |
| `vertical.top_clearance` | 25 | Face clearance H; inferred arrangement, unmeasured height |

The three stable source identities are `scan2_broad` (rear/bottom), `scan1_body`
(camera/front above the arms) and `scan2_long` (raised top). Retrieve them through
`params.plate(component_id)` rather than assuming tuple order.

`FrameParameters` derives `arm_elevation`, `plate_elevations`,
`short_standoff_height`, `rear_standoff_height` and `clearance_hole_diameter`.
For reference stock the Z intervals are 0–2, 2–7, 7–9 and 34–36 mm. Six supports
are H=25 mm; two rear supports are H + arm thickness + camera-plate thickness,
or 32 mm. Changing stock updates these relationships together.

`layout` contains shared root-row positions, splay angles, front/rear tip stations
and stack datums. Its XY dimensions refer to the central stack body datum; the
layout builder recenters the assembly on the four motor centers. +X is right,
+Y front and +Z up. `build_layout(params).wheelbase` reports the largest opposite
motor distance; the reference is approximately 303.39 mm. It is a derived result,
not an independent nominal 305 mm constraint.

Plate geometry has named outline stations and analytical transitions.
`nominal_plate_profile(component_id)` in `parts.plates` exposes its station set.
A non-`None` `PlateParameters.profile` may override named stations; unknown names
are rejected. Shared mounting axes still come from `layout`, not from those
outline overrides. Changing an outline can therefore invalidate an edge ligament
and must be validated. The legacy `FrameParameters.assembly` field is not an
override path for the concrete model: `build_layout` rejects a non-`None` value.

## Manufacturing and equipment

| `manufacturing` field | Reference | Applied meaning |
| --- | --- | --- |
| `general_clearance` | 0.2 mm | Required minimum gap between placed arms |
| `hole_clearance` | 0.2 mm | Total addition to nominal bolt diameter; reference hole is 3.2 mm |
| `slot_clearance` | 0.2 mm | Total dimensional addition in a tab/slot interface |
| `press_fit_clearance` | −0.05 mm | Signed allowance available for an explicit interference fit |
| `printed_part_clearance` | 0.3 mm | Available allowance for a modeled printed mating part |
| `edge_minimum` | 1.5 mm | Carbon opening-to-edge/material ligament gate |
| `hardware_wall_minimum` | 1.0 mm | Separate purchased tubular standoff wall gate |
| `fillet_radius` | 1.0 mm | Nominal policy value; analytical profile transitions retain their specified geometry |
| `linear_tolerance` | 0.05 mm | Mesh linear deflection |
| `angular_tolerance` | 0.1 rad | Mesh angular deflection |

Slot, press-fit and printed-part allowances do not create an unobserved mating
part. No scanned aperture is classified as a tab joint merely because it is
rectangular. See [manufacturing assumptions](manufacturing.md) for gate scope.

`equipment` contains configurable clearance proxies: 40 × 40 × 8 mm FC and ESC,
20 × 20 × 20 mm camera, 3 mm initial board gap and inter-board gap, 2 mm camera
bottom gap, and four 5 mm stack-hardware cylinders inside 6 mm PCB keepouts.
FC/ESC/camera minimum gap is 0.2 mm. These are explicit engineering assumptions,
not identified purchased components. See [equipment placement and limits](equipment.md).

## Presets

| Preset | Arm / plate stock | Difference from reference |
| --- | --- | --- |
| `reference` | 5 / 2 mm | Source-oriented baseline |
| `default` | 5 / 2 mm | Same geometry as reference |
| `minimum_supported` | 3 / 1.5 mm | Thinner-stock regression case |
| `maximum_supported` | 7 / 3 mm | Thicker-stock regression case |
| `tolerance_test` | 5 / 2 mm | Hole allowance 0.3 mm; slot allowance 0.35 mm |

These names identify discrete test inputs. They do not establish that every
intermediate parameter combination fits or that altered stock was physically
measured. Inspect each current validation report for its exact parameters and
result. Changes to layout, arm length, board dimensions or H require another
validation run even when stock remains within these values.

## Build and validate a variation

The CLI selects named presets and serializes their parameters; custom dimensions
are supplied through the Python API. This example changes the top clearance while
retaining explicit assumption provenance:

```python
from dataclasses import asdict, replace
from pathlib import Path

from fpv_frame.assembly import build_assembly, validate_assembly
from fpv_frame.export import export_artifacts
from fpv_frame.parameters.evidence import ParameterEvidence
from fpv_frame.parameters.presets import get_preset

baseline = get_preset("reference")
params = replace(
    baseline,
    vertical=replace(
        baseline.vertical,
        top_clearance=27.0,
        evidence=ParameterEvidence(reason="Design variation: 27 mm top face clearance."),
    ),
)
model = build_assembly(params)
report = validate_assembly(model)
paths = export_artifacts(
    model.parts,
    model.profiles,
    model.compound,
    Path("artifacts/custom-frame"),
    formats=("step", "svg"),
    metadata={"preset": "custom", "parameters": asdict(params),
              "wheelbase_mm": model.layout.wheelbase},
)
```

`build_assembly` returns `FrameAssembly` with the parameter snapshot, shared
layout, named physical `parts`, planar `profiles` and a labeled `compound`.
Profiles are at Z=0. Plate profiles retain assembly XY coordinates; arm and
standoff manufacturing profiles use their local coordinates. Solid parts use
their assembled placements. The canonical arm is available separately through
`parts.arm.arm_profile(params)` and `parts.arm.build_arm(params)`.

`validate_assembly(model)` checks actual geometry and uses design envelopes from
`params.equipment`. To assess measured equipment, supply explicit
`ClearanceEnvelope` objects via `validate_assembly(model, envelopes=...)`.
Passing an empty tuple supplies no equipment evidence; it must not be read as
universal clearance approval. Exporters consume supplied geometry and do not
replace this validation step.

Each `ParameterEvidence` records a reason, sources, confidence, method and whether
it is verified. Stock has separate `thickness_evidence`. When replacing a measured
dimension, replace its evidence too; a frozen dataclass prevents mutation but
cannot infer that an old source claim no longer supports a new number.
