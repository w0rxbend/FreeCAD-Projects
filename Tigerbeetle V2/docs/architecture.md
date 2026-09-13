# Parametric architecture

The Python model is authoritative. Reconstruction data, mechanical interfaces,
profiles, BREP parts, assemblies, validation and exporters have separate responsibilities.
No exporter may repair geometry or compensate for an incorrect interface.

## Evidence and identified components

Both scans have independent observation records in `references/measurements`.
`combined.yaml` reconciles their features into one body coordinate system; it is
not permission to copy raster noise into model coordinates. The A4 tracing-paper
provenance is user-confirmed. The resulting approximate 11.81 px/mm calibration is
supported independently by the nested electronics patterns; full-sheet coverage
remains an explicit calibration assumption.

There are three observed body plates, identified without changing source identity:

| Identity | Source | Photo-supported assembly role |
| --- | --- | --- |
| `scan1_body` | Scan 1 right-hand body | Main/camera plate above the arm roots |
| `scan2_broad` | Scan 2 left-hand body | Rear bottom plate below the arm roots |
| `scan2_long` | Scan 2 right-hand lattice | Raised top deck |
| `arm` | Scan 1 two arm drawings | One canonical handed profile, four placements |

The scan drawings show handed root geometry. Arm reflection is necessary; arbitrary
rotation alone cannot make the two handed roots identical. No vertical side panel,
separate carbon camera plate or matching tab part is invented from the cutouts.
The photograph also shows flexible camera/accessory mounts. Their unmeasured geometry is not a carbon component; nominal camera clearance is checked using a configurable solid envelope.

## Coordinates and vertical datums

Lengths are millimeters, angles degrees unless an exporter explicitly requires
radians. +X is right, +Y front and +Z up. In the accepted scan orientation the wide
camera fork points +Y (decreasing native image v). The calibrated datum transform,
not a local part builder, assigns source pixels to physical frame coordinates.
The XY origin is the shared frame-center datum. For practical stack construction,
Z=0 is the lower face of the rear bottom plate; this offset must be documented if
an exported coordinate system is subsequently centered vertically.

`geometry/datums.py` supplies immutable `Point2`, `Point3`, `PlanarTransform` and
`ComponentPlacement`. A transform reflects local X first, rotates about +Z second,
and translates last. The canonical arm local origin is its root-hole midpoint and
its +Y axis points toward the motor. Its contour, holes and mounting interface must
all receive the same transform. `geometry/layout.py` derives all four root placements from reconciled feature pairs and the shared canonical root pattern.

The photo-supported vertical stack is derived, not stored as unrelated offsets:

| Item | Lower Z |
| --- | --- |
| Rear bottom plate | 0 |
| Arms | Rear bottom plate thickness |
| Main/camera plate | Rear plate thickness + arm thickness |
| Top lattice plate | Main plate upper face + top clearance H |

Reference thicknesses are user-confirmed: arms 5 mm, all three plates 2 mm.
`VerticalStackParameters.top_clearance` is provisionally 25 mm, not a measured
height. Six short supports have length H. Two rear supports have length
H + main-plate thickness + arm thickness (H + 7 mm for the reference).
`FrameParameters.plate_elevations`, `arm_elevation`, `short_standoff_height` and
`rear_standoff_height` derive these relationships on every access. `build_layout()` derives XY placements on each build; explicit `FrameParameters.assembly` overrides are rejected to prevent conflicting placement authorities.

## Parameter contracts

The hierarchy is frozen dataclasses. Nested collections use tuples. Dimension
constructors reject NaN, infinities, booleans, zero where a positive dimension is
required, and negative ordinary clearances. Signed press-fit allowance is supported.

- `FrameParameters` composes three `PlateParameters`, one `ArmParameters`, stack,
  motor, hardware, manufacturing, vertical stack, nominal equipment envelopes and semantic layout dimensions.
- `ArmProfileParameters` contains semantic root-to-motor length, root width, shaft
  width, motor-paddle width and root-hole spacing. The canonical profile builder derives contour transitions from these dimensions and reconciled evidence.
- `PlateProfileParameters` supplies named, ordered longitudinal `OutlineStation`
  values with half-widths. A canonical half-profile generates both plate sides.
- An unresolved arm profile is rejected. Reference plate contours use sparse semantic landmarks and shared layout deformation; explicit plate station profiles are also supported.
- There is no independent per-part profile scale. Outline dimensions may change,
  but all mating-feature locations must continue to come from shared interfaces.
- `StackParameters` distinguishes candidate 30.5 and 20 mm pitches from an actual
  board envelope. `MotorMountParameters` names a bolt-circle diameter explicitly;
  a 19 mm opposite-hole distance is not a 19 mm square side.
- `HardwareParameters` keeps nominal bolt diameter separate from manufacturing
  allowance. `FrameParameters.clearance_hole_diameter` adds the allowance once.

`ParameterEvidence` records source, reason, verification, confidence and method.
Thickness evidence is separate from overall profile evidence so confirmed material
thickness never silently certifies an uncertain contour. Parameter overrides must
update their evidence: changing a measured dimension invalidates its old provenance.
All other development defaults remain explicit assumptions.

Five presets are available through `get_preset`: `reference`, `default`,
`minimum_supported`, `maximum_supported`, `tolerance_test`. Reference/default use
confirmed thicknesses. Minimum/maximum vary thickness with provisional evidence;
tolerance_test varies fit allowances. These names identify software regression
cases, not a tested manufacturing envelope. Bounds must be re-evaluated against
real geometry and assembly validation as implementation proceeds.

## Shared interface contracts

`HolePattern` is an immutable nominal XY location set plus hole diameter. Its
rectangle factory uses explicit pitches; its bolt-circle factory uses diameter,
count and angular offset. `placed()` applies one canonical transform to all holes.

`PlateInterface` owns one hole pattern and explicit receiving plane elevations.
`holes_at()` generates every receiving plate's axes from that same pattern.
`ArmInterface` owns canonical root holes and one placement; both arm and plate
builders consume its `hole_axes` / `holes_at()` output. Builders must not introduce
independent coordinates for the opposite member of either joint.

`TabSlotInterface` generates a nominal rectangular tab and matching rectangular
cutout from one center/orientation. Slot clearance is a **total** addition to each
nominal dimension, therefore 0.2 mm clearance means 0.1 mm on either side when
centered. It is an available interface primitive; no current plate aperture has
been classified as a tab joint solely because it is rectangular.

## Implemented build and validation pipeline

`build_assembly()` returns 15 named physical parts: three carbon plates, four
instances of the canonical arm, and eight tubular standoffs. Its profile mapping
has the same inventory. Each manufacturing face lies at local Z=0; plate profiles
retain global XY, while arm and standoff profiles use their component coordinates.
The assembled solids carry their derived placements. Exporters copy solids before
building export assemblies so the original parent/child topology is preserved.

Validation checks actual BREP topology and material, not only matching parameter
values. It measures 88 interface bores at both surfaces and checks cylindrical
witness volumes for internal plugs. Bilateral comparisons use differences of
mirrored solids. Interference checks reject unintended positive-volume overlap;
intended plate/support contacts are explicit. Arm pair distances enforce the
configured clearance. Profile wire distances enforce carbon ligaments separately
from purchased standoff walls. Configurable FC, ESC, camera and stack hardware
solids must clear both frame material and each other. No separate side panels are
identified, so that category is explicitly not applicable.

The CLI validates before export, records the complete parameter snapshot and its
canonical SHA-256 hash, and writes all deliverables from the same model. SVG uses
the extrusion profiles; STEP is the CAD interchange source for FreeCAD documents.
Native FreeCAD conversion and reopening are separate checks. The release packager
checks inventory, checksums, validation reports and parameter consistency before
creating format-specific archives.

Scan overlays are diagnostic raster/curve comparisons, separate from exact CAD
interface checks. `blueprint-fit.json` reports the directed distance to source ink
and observed hole residuals, with its limitations. Physical load strength, exact
unmeasured equipment compatibility and stock/process qualification remain outside
what these geometric tests can establish; reconstruction departures and inferred
hardware dimensions are recorded in the manufacturing and reconstruction docs.
