# PLAN.md — Production-Grade Parametric FPV Drone Frame

## 1. Objective

Implement a production-grade, fully parametric FPV drone frame CAD project using:

- Python
- `build123d`
- `uv`
- OpenCascade/BREP geometry
- FreeCAD for `.FCStd` generation
- GitHub Actions for validation and artifact publishing
- agentic swarm development with specialized agents/subagents

The model must be reconstructed from:

```text
Scan_1.jpeg
Scan_2.jpeg
```

These are manually prepared 2D blueprints drawn over actual FPV frame parts.

The blueprints are the primary geometric reference but must not be blindly traced.

The final CAD geometry must:

- closely reproduce the reference frame;
- have mathematically correct symmetry;
- use shared datums and shared interface definitions;
- guarantee that corresponding slots, tabs, holes, standoffs and mounting interfaces align;
- remain valid when parameters change;
- be suitable for actual manufacturing;
- export reproducibly to STEP, STL, 3MF, FCStd and SVG;
- allow individual frame components and the complete assembled frame to be exported.

The result must represent a physically coherent FPV frame, not merely a visually similar 3D object.

---

# 2. Design Philosophy

Use CAD-as-code principles.

Do NOT create a large procedural script containing arbitrary coordinates extracted independently from the drawings.

Construct the model from:

1. global coordinate system;
2. engineering datums;
3. explicit primary parameters;
4. derived dimensions;
5. reusable mechanical interfaces;
6. symmetry constraints;
7. reusable geometric primitives;
8. deterministic validation.

Prefer:

```text
blueprint
    ↓
measurements
    ↓
parameters
    ↓
datums
    ↓
interfaces
    ↓
profiles
    ↓
parts
    ↓
assembly
    ↓
validation
    ↓
exports
```

Never define the two sides of the same mechanical interface independently.

---

# 3. Blueprint Inputs

Preserve the original reference files unchanged:

```text
references/
├── source/
│   ├── Scan_1.jpeg
│   └── Scan_2.jpeg
├── calibrated/
├── overlays/
└── measurements/
```

Files under:

```text
references/source/
```

must never be modified.

Any:

- rotation;
- cropping;
- rectification;
- perspective correction;
- calibration;
- annotation;

must create derived files under:

```text
references/calibrated/
```

---

# 4. Blueprint Interpretation

Both scans must be analyzed before detailed CAD implementation begins.

Determine:

- represented physical components;
- front/rear orientation;
- top/bottom orientation;
- centerlines;
- symmetry axes;
- exterior profiles;
- mounting holes;
- slots;
- tabs;
- bolt patterns;
- interfaces between components;
- known dimensions;
- known FPV standards;
- calibration anchors;
- probable raster/manual-drawing inaccuracies.

Establish this priority:

1. known physical dimensions;
2. known mechanical standards;
3. mating interfaces;
4. repeated geometry;
5. mathematical symmetry;
6. agreement between Scan_1 and Scan_2;
7. blueprint contours;
8. individual pixel-level irregularities.

Small accidental asymmetry must not propagate into CAD.

---

# 5. Blueprint Calibration

Create:

```text
references/measurements/
├── Scan_1.yaml
├── Scan_2.yaml
└── combined.yaml
```

Every measurement should contain metadata.

Example:

```yaml
front_arm_root_width:
  value: 18.4
  unit: mm
  source:
    - Scan_1.jpeg
  confidence: high
  method: calibrated_measurement
```

Possible confidence levels:

```text
known
high
medium
low
estimated
```

Possible methods:

```text
known_standard
direct_measurement
cross_scan_measurement
inferred_from_symmetry
inferred_from_interface
estimated
```

Do not treat JPEG pixels as millimeters directly.

---

# 6. Calibration Anchors

Prefer several independent anchors.

Examples:

- M3 hole diameter;
- M2 hole diameter;
- 20 × 20 mm electronics stack;
- 30.5 × 30.5 mm electronics stack;
- motor bolt pattern;
- wheelbase;
- known arm dimension;
- known plate dimension;
- standoff spacing.

If calibration anchors disagree, investigate instead of silently averaging them.

---

# 7. Shared Coordinate System

Use one authoritative coordinate system:

```text
origin = geometric center of frame

+X = right
-X = left

+Y = front
-Y = rear

+Z = up
-Z = down
```

Both scans must ultimately map into this coordinate system.

Do NOT model Scan_1 and Scan_2 as separate unrelated coordinate systems.

Shared features visible in both scans must resolve to the same CAD datum.

---

# 8. Parameter Model

Use typed immutable parameter objects.

Suggested structure:

```text
src/fpv_frame/parameters/
├── frame.py
├── arms.py
├── plates.py
├── mounting.py
├── hardware.py
├── manufacturing.py
└── presets.py
```

Conceptual types:

```text
FrameParameters
ArmParameters
PlateParameters
StackParameters
MotorMountParameters
CameraMountParameters
SidePanelParameters
HardwareParameters
ManufacturingParameters
```

Use millimeters internally.

Avoid unexplained numeric literals.

Bad:

```python
Circle(1.55)
Pos(15.25, 15.25)
```

Good:

```python
Circle(params.hardware.m3_clearance_radius)

params.stack.fc.mount_points
```

---

# 9. Primary vs Derived Parameters

Separate primary engineering parameters from derived geometry.

Primary examples:

- wheelbase;
- arm width;
- arm thickness;
- carbon plate thickness;
- standoff spacing;
- electronics-stack pattern;
- motor bolt spacing;
- nominal tab width;
- manufacturing clearance.

Derived examples:

- arm angle;
- motor-center coordinates;
- mirrored coordinates;
- tab centers;
- slot centers;
- diagonal distances;
- body envelope;
- plate intersection coordinates.

Do not expose every coordinate as an independent parameter.

---

# 10. Mechanical Interface Abstractions

Mechanical interfaces are critical domain objects.

Implement abstractions such as:

```text
HolePattern
MountPattern
SlotPattern
TabSlotInterface
StandoffPattern
MotorPattern
ElectronicsStackPattern
PlateInterface
```

A shared interface should generate both sides of the relationship.

Example:

```python
interface.tabs()
interface.slot_cutouts()
interface.hole_locations()
```

A tab and its matching slot must never originate from unrelated measurements.

This rule is mandatory so that:

**усі пази сходились і всі деталі реально збиралися.**

---

# 11. Symmetry

Symmetry must be mathematical.

For a symmetric plate:

```text
canonical geometry
       ↓
half / quarter
       ↓
mirror
       ↓
complete geometry
```

For arms:

```text
canonical arm
      ↓
transform
      ↓
front-left
front-right
rear-left
rear-right
```

Do not model four arms independently.

Do not independently trace left/right blueprint noise.

---

# 12. Recommended Project Architecture

```text
src/fpv_frame/
├── __init__.py
├── cli.py
│
├── parameters/
│   ├── frame.py
│   ├── arms.py
│   ├── plates.py
│   ├── mounting.py
│   ├── hardware.py
│   ├── manufacturing.py
│   └── presets.py
│
├── blueprint/
│   ├── calibration.py
│   ├── measurements.py
│   ├── rectification.py
│   ├── overlay.py
│   └── deviation.py
│
├── geometry/
│   ├── datums.py
│   ├── primitives.py
│   ├── profiles.py
│   ├── patterns.py
│   └── interfaces.py
│
├── parts/
│   ├── arm.py
│   ├── top_plate.py
│   ├── bottom_plate.py
│   ├── camera_plate.py
│   ├── side_plate.py
│   ├── rear_plate.py
│   ├── braces.py
│   └── accessories.py
│
├── assembly/
│   ├── frame.py
│   └── placements.py
│
├── drawing/
│   ├── projections.py
│   ├── dimensions.py
│   └── svg.py
│
├── export/
│   ├── step.py
│   ├── stl.py
│   ├── three_mf.py
│   ├── freecad.py
│   └── svg.py
│
└── validation/
    ├── geometry.py
    ├── symmetry.py
    ├── interfaces.py
    ├── clearances.py
    ├── interference.py
    └── manufacturing.py
```

Adapt component modules to the actual frame.

---

# 13. 2D Profile First

For planar carbon components use:

```text
parametric 2D profile
        ↓
profile validation
        ↓
SVG
        ↓
extrusion
        ↓
BREP solid
```

This applies especially to:

- main plates;
- arms;
- side plates;
- camera plates;
- braces.

The same profile should drive both manufacturing geometry and SVG output.

---

# 14. Curves

Prefer analytical geometry:

- lines;
- circles;
- arcs;
- tangent arcs;
- fillets.

Avoid hundreds of traced polyline/spline points.

Use splines only when genuinely required by the physical design.

Spline control points must remain minimal and parameterized.

---

# 15. Manufacturing Parameters

Create configurable manufacturing parameters.

Example:

```python
ManufacturingParameters(
    general_clearance=...,
    slot_clearance=...,
    hole_clearance=...,
    press_fit_clearance=...,
    printed_part_clearance=...,
    edge_minimum=...,
    fillet_radius=...,
)
```

Keep nominal geometry separate from compensation.

Example:

```text
nominal_tab_width = 3.0 mm

actual_slot_width =
    nominal_tab_width
    + slot_clearance
```

---

# 16. Part Modeling

Each physical component must have an independent builder.

Example:

```python
def build_arm(params: ArmParameters) -> Part:
    ...

def build_top_plate(params: PlateParameters) -> Part:
    ...
```

Part builders must not perform export operations.

Separation:

```text
geometry
validation
assembly
drawing
export
```

---

# 17. Assembly

Construct a complete assembly with named components.

Example:

```text
frame
├── bottom_plate
├── top_plate
├── arm_front_left
├── arm_front_right
├── arm_rear_left
├── arm_rear_right
├── side_left
├── side_right
└── ...
```

Placements must be computed from shared datums.

Never manually move a component until it visually appears correct.

---

# 18. Blueprint Overlay Validation

Overlay generation is mandatory.

Provide commands such as:

```bash
uv run fpv-frame overlay scan-1
uv run fpv-frame overlay scan-2
```

Generate:

```text
artifacts/overlays/
├── Scan_1_overlay.svg
├── Scan_1_overlay.png
├── Scan_2_overlay.svg
└── Scan_2_overlay.png
```

Overlays should visualize:

- calibrated source;
- generated CAD profile;
- datum axes;
- hole centers;
- symmetry axes;
- important interfaces;
- optional deviation markers.

The swarm must use these overlays during iterative development.

---

# 19. Deviation Reporting

Generate:

```text
artifacts/reports/blueprint-fit.json
```

Example:

```json
{
  "Scan_1.jpeg": {
    "max_outline_deviation_mm": 0.42,
    "mean_outline_deviation_mm": 0.17,
    "critical_hole_max_deviation_mm": 0.08
  }
}
```

Critical mechanical features should use tighter thresholds than cosmetic contours.

Do not invent precision beyond what the scans support.

---

# 20. Geometry Validation

Validate:

- valid BREP topology;
- closed solids;
- non-zero volume;
- non-zero profile area;
- non-self-intersecting profiles;
- valid wires;
- valid faces;
- valid extrusions;
- expected feature counts.

Generation must fail if invalid geometry is produced.

---

# 21. Symmetry Validation

Implement explicit symmetry tests.

Examples:

```text
front_left_motor.x == -front_right_motor.x

front_left_motor.y == front_right_motor.y
```

Do the same for:

- arm roots;
- plate edges;
- stack mounts;
- side panels;
- mounting holes.

Intentional asymmetry must be explicitly documented.

---

# 22. Interface Validation

Every mating interface must have deterministic tests.

Example:

```text
slot_center == tab_center
```

and:

```text
slot_width =
    tab_width + configured_clearance
```

Also verify:

- bolt-axis alignment;
- standoff alignment;
- plate-plane alignment;
- arm mounting-hole alignment.

Interface correctness has higher priority than visual similarity.

---

# 23. Collision / Interference Validation

At assembly level detect unintended overlap.

Maintain explicit exceptions:

```python
allowed_contacts = {...}
```

Unexpected solid intersections must fail validation.

Also check required clearances around:

- FC;
- ESC;
- stack hardware;
- side panels;
- camera mounting area;
- arm roots.

---

# 24. Parametric Regression

Create several presets:

```text
reference
default
minimum_supported
maximum_supported
tolerance_test
```

CI must verify representative parameter modifications.

Changing one valid engineering parameter must not unexpectedly destroy unrelated geometry.

---

# 25. Export Targets

Generate:

```text
dist/
├── step/
├── stl/
├── 3mf/
├── freecad/
└── svg/
```

Individual physical components:

```text
<part>.step
<part>.stl
<part>.3mf
<part>.svg
```

Complete frame:

```text
fpv-frame.step
fpv-frame.stl
fpv-frame.3mf
fpv-frame.FCStd
```

---

# 26. STEP

STEP is the canonical CAD interchange artifact.

Preserve component naming and physical units where possible.

STEP/BREP remains preferred over mesh formats for downstream CAD work.

---

# 27. STL

Generate binary STL with explicit:

```text
linear_tolerance
angular_tolerance
```

Do not silently depend on exporter defaults.

---

# 28. 3MF

Use build123d mesh functionality.

Preserve separately identifiable components where practical.

Do not unnecessarily flatten a multi-part frame into one anonymous mesh.

---

# 29. FreeCAD

The build123d Python model remains authoritative.

Generate:

```text
STEP
 ↓
FreeCADCmd
 ↓
FCStd
```

Create:

```text
tools/export_freecad.py
```

FCStd is an interoperability artifact, not the source of truth.

---

# 30. SVG

Generate 1:1 vector geometry for planar components.

Suggested outputs:

```text
top_plate.svg
bottom_plate.svg
arm.svg
side_plate.svg

assembly_top.svg
assembly_bottom.svg
assembly_front.svg
assembly_side.svg
```

Optionally generate dimensioned variants:

```text
top_plate.dimensioned.svg
```

SVG should support:

- contours;
- holes;
- center marks;
- datums;
- dimensions;
- labels.

---

# 31. CLI

Implement:

```bash
fpv-frame build
fpv-frame validate
fpv-frame export
fpv-frame export --format step
fpv-frame export --part arm
fpv-frame drawing
fpv-frame overlay scan-1
fpv-frame overlay scan-2
fpv-frame inspect
fpv-frame parameters
```

Commands must return non-zero status on validation failure.

---

# 32. Python Tooling

Use:

```text
uv
build123d
pytest
ruff
mypy or pyright
```

Required:

```text
pyproject.toml
uv.lock
.python-version
```

Use `src/` layout.

Use `uv sync --frozen` in CI.

---

# 33. Tests

Suggested structure:

```text
tests/
├── unit/
├── blueprint/
├── geometry/
├── symmetry/
├── interfaces/
├── assembly/
├── exports/
└── regression/
```

Test engineering invariants rather than implementation details.

---

# 34. Reproducibility

A clean checkout must reproduce the model:

```bash
git clone ...
uv sync --frozen
uv run fpv-frame validate
uv run fpv-frame export
```

Avoid committing generated binaries unless deliberately required.

---

# 35. GitHub Actions — CI

Create:

```text
.github/workflows/ci.yml
```

Pipeline:

```text
checkout
 ↓
setup uv
 ↓
uv sync --frozen
 ↓
ruff
 ↓
type check
 ↓
unit tests
 ↓
geometry tests
 ↓
symmetry tests
 ↓
interface tests
 ↓
assembly validation
 ↓
export smoke tests
```

---

# 36. GitHub Actions — CAD Build

Create:

```text
.github/workflows/cad.yml
```

Upload:

```text
cad-artifacts/
├── step/
├── stl/
├── 3mf/
├── freecad/
├── svg/
├── overlays/
├── reports/
└── parameters.json
```

---

# 37. GitHub Release

Create:

```text
.github/workflows/release.yml
```

Trigger:

```text
v*
```

Publish:

```text
STEP/
STL/
3MF/
FreeCAD/
SVG/
overlays/
reports/
parameters/
SHA256SUMS
```

---

# 38. Artifact Manifest

Generate:

```text
manifest.json
```

Include:

- project version;
- Git commit;
- parameter preset;
- primary dimensions;
- Python version;
- build123d version;
- artifact filenames;
- checksums.

---

# 39. Documentation

Maintain:

```text
README.md
docs/parameters.md
docs/architecture.md
docs/blueprint-reconstruction.md
docs/manufacturing.md
```

Document:

- coordinate system;
- scan calibration;
- parameterization;
- interfaces;
- tolerance assumptions;
- export workflow;
- manufacturing assumptions.

---

# 40. Agentic Swarm Requirement

This project MUST be implemented using an explicit multi-agent / subagent workflow.

A single agent must not attempt to perform blueprint analysis, parameter extraction, CAD implementation, validation, exports and CI sequentially without delegation when subagents are available.

Use a hierarchy:

```text
Orchestrator
│
├── Blueprint Analysis Swarm
├── CAD Architecture Agent
├── Geometry Modeling Swarm
├── Interface/Mechanical Agent
├── Assembly Agent
├── Validation Swarm
├── Export/Tooling Agent
├── CI/Release Agent
└── Independent Reviewer Agents
```

The orchestrator owns integration.

Specialists own narrow responsibilities.

---

# 41. Orchestrator Agent

The top-level agent acts as technical lead and integration coordinator.

Responsibilities:

- inspect repository state;
- maintain implementation backlog;
- decompose milestones;
- spawn specialist agents;
- assign non-overlapping tasks;
- identify dependencies;
- collect subagent reports;
- reconcile conflicting conclusions;
- integrate accepted changes;
- execute final validation;
- decide when another iteration is required.

The orchestrator should avoid performing work directly when a specialized subagent can handle it independently.

Its primary responsibility is coordination and correctness.

---

# 42. Persistent Swarm State

Maintain agent-readable project state.

Suggested directory:

```text
.agent/
├── STATE.md
├── DECISIONS.md
├── ASSUMPTIONS.md
├── TASKS.md
├── FINDINGS.md
└── handoffs/
```

These files must remain concise.

`STATE.md`:

```text
current milestone
completed components
current blockers
validation status
```

`DECISIONS.md`:

```text
accepted engineering decisions
rejected alternatives
reasoning
```

`ASSUMPTIONS.md`:

```text
uncertain dimensions
temporary assumptions
confidence levels
verification requirements
```

`TASKS.md`:

```text
pending
active
blocked
completed
```

Do not use agent conversation history as the only project memory.

---

# 43. Blueprint Analysis Swarm

Spawn separate analysis agents.

Suggested roles:

```text
scan-1-analysis-agent
scan-2-analysis-agent
cross-reference-agent
standards-agent
calibration-review-agent
```

## Scan 1 Agent

Analyze only:

```text
Scan_1.jpeg
```

Produce:

- identified components;
- measurements;
- symmetry candidates;
- calibration anchors;
- holes;
- slots;
- profiles;
- confidence levels;
- unresolved questions.

## Scan 2 Agent

Perform equivalent independent analysis for:

```text
Scan_2.jpeg
```

It should not initially depend on Scan 1 conclusions.

Independent interpretation reduces correlated errors.

---

# 44. Cross-Reference Agent

After Scan 1 and Scan 2 agents finish, spawn a separate reconciliation agent.

Its job is to compare:

```text
Scan_1 findings
vs
Scan_2 findings
```

Find:

- shared features;
- conflicting measurements;
- common datums;
- likely symmetry;
- scale inconsistencies;
- probable manual-drawing errors.

Produce a proposed:

```text
combined measurement model
```

Do not allow either scan agent to silently overwrite the other agent's measurement.

---

# 45. Mechanical Standards Agent

Spawn a specialist to identify whether observed dimensions correspond to established FPV standards.

Examples:

- M2/M3 fasteners;
- 20 × 20 stack;
- 30.5 × 30.5 stack;
- standard motor-hole patterns;
- conventional carbon thicknesses.

Known standards may be used to correct weak raster measurements.

All such corrections must be documented.

---

# 46. CAD Architecture Agent

Before detailed part modeling, assign one agent to design:

- parameter hierarchy;
- datum system;
- interface abstractions;
- module boundaries;
- assembly strategy.

This agent should NOT attempt to fully model individual parts.

Deliverable:

```text
docs/architecture.md
```

and initial parameter/interface types.

Architecture must be reviewed before geometry swarm work begins.

---

# 47. Geometry Modeling Swarm

Model independent physical components in parallel when possible.

Potential agents:

```text
bottom-plate-agent
top-plate-agent
arm-agent
side-panel-agent
camera-section-agent
rear-section-agent
```

Do not parallelize components whose shared interface definition has not yet stabilized.

Shared mechanical definitions must be implemented before dependent geometry agents begin.

---

# 48. Canonical Arm Agent

Use one dedicated agent for arm reconstruction.

Its output must be a single canonical arm.

The agent must:

- identify center axis;
- identify arm root;
- identify motor center;
- model motor mounting pattern;
- model exterior contour;
- validate against the corresponding scan;
- generate overlay.

Other arms are generated mathematically.

No separate agents should independently model front-left/front-right/etc.

---

# 49. Mechanical Interface Agent

Assign one dedicated agent to mechanical compatibility.

This agent owns:

- tab-slot abstractions;
- shared bolt patterns;
- plate interfaces;
- stack mounting;
- standoff positions;
- arm mounting;
- clearances.

It should inspect geometry produced by part agents and reject models that independently duplicate interface coordinates.

This agent has authority to require refactoring.

---

# 50. Assembly Agent

After major parts exist, spawn a separate assembly agent.

Responsibilities:

- component placements;
- transforms;
- full frame assembly;
- identifying missing interfaces;
- collision analysis;
- clearance analysis.

The assembly agent must not compensate for broken part geometry by arbitrary translation.

If parts do not fit, return the defect to the responsible geometry/interface agent.

---

# 51. Blueprint Validation Swarm

Run independent reviewers after geometry generation.

Suggested reviewers:

```text
overlay-review-agent
symmetry-review-agent
mechanical-fit-review-agent
parameterization-review-agent
```

Each reviewer should attempt to find errors rather than simply confirm implementation.

This is an adversarial review stage.

---

# 52. Overlay Review Agent

Compare generated orthographic geometry against:

```text
Scan_1.jpeg
Scan_2.jpeg
```

Report:

- major profile mismatch;
- incorrect hole positions;
- incorrect scale;
- unexplained deviations;
- symmetry differences;
- suspected blueprint distortion.

Return structured findings.

---

# 53. Symmetry Review Agent

Independently inspect whether:

- symmetric geometry uses mathematical constraints;
- mirrored parts are actually mirrored;
- duplicated coordinates have accidentally diverged;
- arms share canonical geometry;
- matching features are centered correctly.

Visual symmetry is insufficient.

Inspect the parameter/data model.

---

# 54. Mechanical Fit Review Agent

Attempt to disprove assembly correctness.

Check:

- tabs vs slots;
- hole axes;
- bolt centers;
- plate spacing;
- side-panel mounting;
- arm attachment;
- stack mounting;
- physical clearances.

Produce failures with numerical evidence.

---

# 55. Parameterization Review Agent

Review code for fake parameterization.

Reject code where:

- hundreds of coordinates are hardcoded;
- mirrored geometry is manually duplicated;
- shared geometry is copied;
- derived values are stored independently;
- arbitrary offsets are used to force assembly.

The model must remain semantically parametric.

---

# 56. Export Agent

A specialized export agent owns:

- STEP;
- STL;
- 3MF;
- SVG;
- FCStd conversion;
- export metadata;
- deterministic output layout.

This agent should not alter model geometry to work around exporter issues unless the geometry itself is invalid.

---

# 57. CI / Release Agent

Assign an infrastructure-focused subagent.

Responsibilities:

- `uv` setup;
- locked dependencies;
- lint/type/test jobs;
- geometry validation jobs;
- CAD artifact generation;
- GitHub Actions artifacts;
- tagged releases;
- checksums;
- manifests.

Geometry agents should not independently implement CI infrastructure.

---

# 58. Swarm Task Contract

Every delegated task should specify:

```text
TASK
SCOPE
INPUTS
OUTPUTS
FILES OWNED
FILES READ-ONLY
INVARIANTS
VALIDATION COMMAND
BLOCKERS
```

Example:

```text
TASK:
Implement canonical arm geometry.

INPUTS:
- references/measurements/combined.yaml
- src/fpv_frame/geometry/interfaces.py

FILES OWNED:
- src/fpv_frame/parts/arm.py
- tests/geometry/test_arm.py

READ-ONLY:
- src/fpv_frame/geometry/interfaces.py

INVARIANTS:
- mathematical longitudinal symmetry
- motor pattern from shared MotorPattern
- arm root from shared ArmInterface

VALIDATION:
uv run pytest tests/geometry/test_arm.py
```

This prevents agents from stepping on each other's work.

---

# 59. Agent Handoff Contract

Every subagent must return a structured summary.

Required fields:

```text
STATUS
FILES CHANGED
RESULT
MEASUREMENTS/DECISIONS
ASSUMPTIONS
VALIDATION EXECUTED
KNOWN LIMITATIONS
FOLLOW-UP TASKS
```

The orchestrator must inspect results before declaring the task complete.

---

# 60. Parallelization Rules

Parallelize only independent work.

Good:

```text
Scan_1 analysis ─┐
                 ├─ parallel
Scan_2 analysis ─┘
```

Good after interfaces stabilize:

```text
top plate ───────┐
bottom plate ────┼─ parallel
side panel ──────┤
canonical arm ───┘
```

Bad:

```text
agent A invents slot coordinates
agent B independently invents matching tab coordinates
```

Shared definitions must be established first.

---

# 61. Dependency Graph

Use an explicit dependency graph.

Conceptually:

```text
Scan_1 ─┐
        ├→ measurement reconciliation
Scan_2 ─┘
                 ↓
        engineering datums
                 ↓
         shared interfaces
                 ↓
       ┌─────────┼─────────┐
       ↓         ↓         ↓
     arms      plates    panels
       └─────────┼─────────┘
                 ↓
              assembly
                 ↓
       validation swarm
                 ↓
              exports
                 ↓
             release
```

Do not start dependent swarm stages prematurely.

---

# 62. Consensus for Ambiguous Measurements

When an important dimension is ambiguous, use multiple agents.

Example:

```text
measurement-agent-A
measurement-agent-B
mechanical-consistency-agent
```

The orchestrator should compare conclusions.

Decision priority:

1. established physical standard;
2. mechanical consistency;
3. agreement across scans;
4. symmetry;
5. strongest calibrated measurement;
6. estimated interpretation.

Record the accepted decision in:

```text
.agent/DECISIONS.md
```

---

# 63. Confidence-Driven Work

High-confidence dimensions can be modeled directly.

Low-confidence dimensions should trigger additional review.

Example thresholds:

```text
KNOWN/HIGH
    → implementation allowed

MEDIUM
    → implementation + reviewer check

LOW/ESTIMATED
    → require independent agent verification
```

Do not allow uncertain measurements to silently become canonical parameters.

---

# 64. Adversarial Review

Review agents should be instructed to search for faults.

Prompts should conceptually say:

```text
Assume the current implementation may be wrong.

Find evidence of:
- geometric inconsistency;
- incorrect assumptions;
- broken symmetry;
- duplicated dimensions;
- interface mismatch;
- invalid parameterization.
```

Avoid reviewer prompts whose only objective is confirmation.

---

# 65. Automatic Feedback Loop

Use this loop:

```text
implementation agent
       ↓
tests
       ↓
CAD generation
       ↓
overlay
       ↓
review agent
       ↓
findings
       ↓
responsible implementation agent
       ↓
correction
       ↓
validation
```

Repeat until acceptance criteria pass.

The orchestrator must not treat the first valid CAD build as completion.

---

# 66. Integration Gates

Introduce explicit gates.

## Gate 1 — Blueprint Understanding

Requires:

- Scan 1 analysis;
- Scan 2 analysis;
- calibration;
- reconciled measurements.

## Gate 2 — Parametric Architecture

Requires:

- global datums;
- parameter hierarchy;
- interface abstractions.

## Gate 3 — Component Geometry

Requires:

- individual valid profiles;
- symmetry tests;
- blueprint overlays.

## Gate 4 — Assembly

Requires:

- all primary components;
- interface validation;
- collision checks.

## Gate 5 — Manufacturing

Requires:

- clearances;
- valid exports;
- dimensional drawings.

## Gate 6 — Release

Requires:

- complete test suite;
- artifact build;
- independent review;
- checksums;
- manifest.

A later gate cannot compensate for an unresolved earlier gate.

---

# 67. Swarm Conflict Handling

If agents disagree:

1. preserve both conclusions;
2. compare supporting evidence;
3. spawn an independent reviewer if necessary;
4. evaluate mechanical consequences;
5. choose one canonical decision;
6. document why.

Do not silently merge contradictory geometry.

---

# 68. Git / Worktree Strategy

Where agent tooling permits it, use isolated branches/worktrees for concurrent implementation agents.

Example:

```text
agent/arm-model
agent/top-plate
agent/side-panels
agent/export
```

The orchestrator integrates accepted changes.

Avoid multiple agents concurrently editing the same core interface module.

Shared architecture files should have one explicit owner at any given stage.

---

# 69. Swarm Progress Tracking

`TASKS.md` should represent dependency state.

Example:

```text
[x] analyze Scan_1
[x] analyze Scan_2
[x] reconcile calibration
[x] establish global datums

[x] implement MotorPattern
[x] implement StackPattern
[ ] implement ArmInterface

[blocked] canonical arm
    blocked_by: ArmInterface

[ready] bottom plate
[ready] top plate
```

Agents should select only tasks whose dependencies are satisfied.

---

# 70. Agent Autonomy

Agents should be allowed to:

- inspect relevant code;
- run tests;
- generate intermediate CAD;
- generate overlays;
- modify files within assigned scope;
- iterate on failures.

They should not require orchestrator approval after every trivial edit.

However, agents must not independently redefine:

- global coordinate system;
- accepted reference dimensions;
- shared mechanical interfaces;
- manufacturing tolerance policy.

Those require integration-level decisions.

---

# 71. Failure Recovery

When an agent fails:

```text
capture failure
↓
record current state
↓
classify failure
↓
retry with narrower scope
or
delegate to specialist
```

Do not restart the entire implementation unnecessarily.

Potential failure classes:

```text
blueprint ambiguity
invalid BREP
incorrect topology
interface mismatch
collision
export failure
CI/tooling failure
```

Delegate according to category.

---

# 72. Agentic Implementation Phases

## Phase 0 — Swarm Bootstrap

Orchestrator:

- inspect repository;
- create `.agent/`;
- create task graph;
- establish ownership rules.

## Phase 1 — Parallel Blueprint Analysis

Spawn simultaneously:

```text
Scan 1 Analyst
Scan 2 Analyst
FPV Standards Analyst
```

## Phase 2 — Reconciliation

Spawn:

```text
Calibration Reviewer
Cross-Scan Reconciliation Agent
```

Produce canonical measurements.

## Phase 3 — Architecture

Spawn:

```text
CAD Architecture Agent
Mechanical Interface Agent
```

Produce:

- datums;
- parameter hierarchy;
- interfaces.

Run architecture reviewer.

## Phase 4 — Parallel Geometry Modeling

Spawn component agents based on dependency readiness.

Example:

```text
Arm Agent
Bottom Plate Agent
Top Plate Agent
Side Panel Agent
```

## Phase 5 — Component Review

For every component run:

```text
geometry tests
overlay generation
symmetry review
parameterization review
```

## Phase 6 — Assembly

Assembly agent integrates all accepted components.

## Phase 7 — Mechanical Validation Swarm

Spawn:

```text
Mechanical Fit Reviewer
Collision Reviewer
Clearance Reviewer
Symmetry Reviewer
```

## Phase 8 — Export

Export agent implements all target formats.

## Phase 9 — Production Infrastructure

CI/release agent completes automation.

## Phase 10 — Final Adversarial Review

Spawn independent agents with no ownership of existing implementation.

Ask them to find flaws.

## Phase 11 — Release Candidate

Orchestrator runs complete clean-room rebuild and validates all outputs.

---

# 73. Orchestrator Loop

The orchestrator should effectively execute:

```text
while project_not_complete:

    inspect_state()

    ready_tasks = dependency_graph.ready()

    delegate_independent_tasks(ready_tasks)

    collect_agent_results()

    run_integration_tests()

    if failures:
        classify_failures()
        delegate_corrections()

    run_review_agents()

    update_project_state()

    verify_next_gate()
```

The workflow must continue autonomously until:

- completion criteria pass; or
- a genuinely impossible ambiguity requiring human physical measurement is identified.

---

# 74. Agent Restrictions

Agents MUST NOT:

- manually trace both symmetric halves;
- copy raster noise;
- redefine shared datums locally;
- duplicate interface positions;
- introduce unexplained constants;
- move components manually until they appear aligned;
- hide errors using excessive clearances;
- replace parametric relationships with fixed coordinates;
- independently modify shared interfaces without ownership;
- modify generated artifacts instead of source geometry;
- accept a model solely because it renders successfully.

---

# 75. Definition of Done

The project is complete only when:

- Scan_1.jpeg has been analyzed and calibrated;
- Scan_2.jpeg has been analyzed and calibrated;
- measurements from both have been reconciled;
- one coherent coordinate system is used;
- primary geometry is fully parametric;
- intended symmetry is mathematically exact;
- matching slots/tabs originate from shared interface definitions;
- mounting holes align;
- arms derive from canonical geometry;
- frame assembly fits mechanically;
- geometry validation passes;
- collision validation passes;
- parametric regression passes;
- overlay review passes;
- adversarial reviewer agents find no unresolved critical defects;
- STEP export works;
- STL export works;
- 3MF export works;
- FCStd generation works;
- SVG drawings are generated;
- CI reproduces everything from a clean checkout;
- tagged releases publish complete CAD artifacts.

---

# 76. Primary Engineering Principle

Treat this repository as a parametric mechanical CAD system, not a script that draws something resembling an FPV frame.

`Scan_1.jpeg` and `Scan_2.jpeg` define the target design intent.

The software must transform them into:

```text
accurate
+
symmetric
+
mechanically coherent
+
parametric
+
manufacturable
```

geometry.

The swarm architecture exists to improve correctness:

```text
independent observation
        +
specialized implementation
        +
cross-agent reconciliation
        +
adversarial validation
        =
high-confidence CAD model
```

When raster appearance and mechanical consistency disagree slightly, preserve the intended engineering geometry rather than reproducing blueprint noise.

No single agent's interpretation should become authoritative merely because it was produced first.

Critical dimensions, mechanical interfaces and final assembly correctness must survive independent agent review.