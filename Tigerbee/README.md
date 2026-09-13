# Tigerbee CAD

Five independently buildable build123d components and a symmetric 7-inch FPV frame
assembly, in a locked Python 3.13 / uv project.

**Tigerbee.FCStd and the three supplied arm/camera 3MF files outrank the scans.**
The generated design preserves their foundation while correcting symmetry and
assembly interfaces. Scan_2 informs only the missing rear/top plates. Original
reference files and extracted profile data are preserved. `compare_a4` is not a
build step, geometry authority or acceptance gate.

| Component | Geometry | Thickness |
| --- | --- | --- |
| `arm-type-1` | FreeCAD foundation, front mirrored pair, local root relief | 5 mm |
| `arm-type-2` | FreeCAD foundation, rear mirrored pair, local root relief | 5 mm |
| `camera-plate` | Mirrored FreeCAD silhouette, tangent joins, nominal openings | 3 mm |
| `rear-plate` | Analytic symmetric silhouette and repeated features from Scan_2 | 3 mm |
| `top-plate` | Analytic symmetric silhouette, slots and matching support holes | 3 mm |

## Geometry and parameters

The user-specified diagonal wheelbase is **305 mm**. Motor centers form a square
X at (±107.833784131, ±107.833784131) mm, with perpendicular diagonals centered at
(0, 0). Front/rear arm rotations are 45°/135°; left copies are mirrored about X=0.
Motor pads and shaft geometry retain their saved CAD basis.
Root tips have a **0.6 mm left/right gap**, transverse root clearance and rounded
local electronics clearance notches. Camera/rear clamp shoulders are locally
reinforced for the new shared hole positions. Nominal structural bores are **3.2 mm** for the modeled 3 mm shafts.

All plate mounting holes derive from one shared interface in
[src/tigerbee/layout.py](src/tigerbee/layout.py); independent tracing fits are no
longer used. [PlateDimensions](src/tigerbee/plates.py) controls repeated opening
sizes, pitches and radii. Camera features retain the 15 × 15 mm R2 square,
18.5 mm round opening and 11.5 × 8.5 mm R2.5 slots from the CAD foundation.
Plate contours use only lines and circular arcs, with tangent perimeter joins.
Export reports keep historical tracing assumptions in `reference_assumptions`;
`assumptions` and effective dimensions describe the current generated design.

Plate profiles use the assembly XY datum, X=0 as their symmetry axis, and lower
face Z=0. Arms use the motor shaft center X=Y=0, extending toward negative Y.
Python parameters are the editable parametric source. Generated FreeCAD documents
contain native solids and dimensional metadata, without a reconstructed sketch
constraint history. Individual JSON reports include nominal dimensions and hole
coordinates; derived decimals do not imply equivalent measurement accuracy.

## Build and inspect

```sh
uv sync --locked
uv run tigerbee build --all
uv run tigerbee assembly --require-fit
uv run tigerbee native
uv run tigerbee verify-exports
```

The canonical [components](exports/parts/) and [assembly](exports/assembly/)
contain STEP, 3MF, STL, SVG and native FCStd files, plus component DXF, assembly
GLB and JSON reports. The [top view](exports/assembly/tigerbee-top.svg) and
[fit report](exports/assembly/assembly-report.json) describe the same geometry.
The [dimensioned motor layout](exports/assembly/tigerbee-motor-layout.svg) shows
the actual bore-center coordinates and both measured diagonals.
Every assembly export requires the actual-solid geometry audit to pass, including
when `--require-fit` is omitted. The explicit flag additionally enforces report
consistency. Native export saves and reopens every FCStd document; the final
inventory verifies source and output hashes.

Native conversion requires FreeCADCmd or the FreeCAD Flatpak. Normal component
and assembly builds do not import FreeCAD or the original reference document.
Regenerate all four build steps after source changes and commit their exports
together. CI checks freshness before rebuilding and applies strict fit validation.

```sh
# Custom parts go outside the canonical assembly output directory.
uv run tigerbee build arm-type-1 --thickness 5.5 --length-extension 10 --output build/custom
uv run tigerbee build camera-plate --center-hole-diameter 19 --output build/custom
# Historical photo thickness assumptions, with the current symmetric geometry.
uv run tigerbee build --all --preset product-7inch --output build/product-7inch
```

The default `frame` preset uses the confirmed 5 mm arms and 3 mm plates.
The explicitly selected `original` preset uses historical source **thicknesses**,
not original asymmetric geometry. `build_reference_profile` explicitly reconstructs the saved
profiles for independent historical regression tests. Custom standalone variants
are not automatically qualified as replacement parts in the default assembly.

## Verification and physical scope

```sh
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy src/tigerbee
uv build
```

Checks cover actual-solid reflection, coaxial through bores, shaft passage through
every intersected layer, opening counts, solid interference, minimum mounting
ligaments, equal motor-bore diagonals and nominal 7-inch propeller-disc gaps.
Tests also cover original FreeCAD baselines, dimensional variants, mesh topology
and exported STEP round trips. Inspect the current assembly report for measured
values and acceptance thresholds.

The assembly contains four arms, three plates and eight simplified standoffs.
All plate stock is confirmed at 3 mm, arms at 5 mm and standoff outside diameter
at 6 mm. The retained top underside Z=35 mm gives six 24 mm and two 32 mm
standoffs. Their modeled internal clearance is 3.2 mm. Bolt/nut
and camera/end-bracket solids are not modeled. Stock, layup, machining tolerances,
purchased hardware and physical fit/load tests remain necessary for a production
release; passing the geometry audit establishes nominal CAD fit.

See [reference authority](refs/SOURCES.md), [physical measurements](refs/measurements.md),
[design contract](tasks/plan.md) and [remaining tasks](tasks/todo.md).
