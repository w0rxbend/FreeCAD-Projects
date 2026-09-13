# Tigerbee CAD

Five individually buildable build123d frame components and a provisional assembly,
managed as a locked Python 3.13 / uv project inside FreeCAD-Projects.

The target is the **Tiger Beetle 7-inch frame with a 330 mm diagonal wheelbase**.
The user-confirmed [final product photo](refs/product/tiger-beetle-7inch-330mm.png)
and both [Scan_1](refs/Scan_1.jpeg) and [Scan_2](refs/Scan_2.jpeg) are the sources
of truth. The earlier 295 mm product photo is superseded. Existing manual FreeCAD
solids are prior reconstructions to check against these references.

| Component | Current reconstruction | Default thickness |
| --- | --- | --- |
| `arm-type-1` | Saved FreeCAD solid corresponding to Scan_1 | 5 mm |
| `arm-type-2` | Saved FreeCAD solid corresponding to Scan_1 | 5 mm |
| `camera-plate` | Saved FreeCAD solid corresponding to Scan_1 | 3 mm |
| `rear-plate` | Scan_2 trace; metric calibration provisional | 2.5 mm |
| `top-plate` | Scan_2 trace; metric calibration provisional | 2.5 mm |

## Committed CAD files

[Individual components](exports/parts/) and the [assembly](exports/assembly/)
include **3MF, STL, and native FreeCAD `.FCStd` files committed as ordinary Git
files**. STEP, SVG, component DXF, assembly GLB, and JSON reports are included too.
GitHub Actions rebuilds and uploads these outputs as additional artifacts.

The `.FCStd` documents contain native solids and build metadata. Parametric design
is maintained in the build123d Python sources; generated FreeCAD documents do not
contain a reconstructed sketch/constraint history. Original manual CAD and mesh
files remain at the project root as references.

## Build and regenerate

Run from this directory:

```sh
uv sync --locked
uv run tigerbee list
uv run tigerbee build --all
uv run tigerbee assembly
uv run tigerbee native
uv run tigerbee verify-exports
```

The native step requires FreeCADCmd or the `org.freecad.FreeCAD` Flatpak. It saves
and reopens every document, verifies its solids, and writes the export inventory.
Normal build123d component and assembly builds do not require FreeCAD.

After changing CAD sources, run all four build/assembly/native/verify commands
and commit `exports/` together with the source change. CI checks the committed
files against source and output hashes before rebuilding them. This detects stale,
missing, or modified exports without relying on byte-identical CAD regeneration.

```sh
# Change selected dimensions without scaling mounting patterns.
uv run tigerbee build arm-type-1 --thickness 5.5 --length-extension 10 --output build/custom
# Earlier product-photo thickness assumptions; does not set the wheelbase.
uv run tigerbee build --all --preset product-7inch --output build/product-7inch
# Require confirmed assembly fit; currently fails with the documented issues.
uv run tigerbee assembly --require-fit --output build/validated
```

Millimeters are used throughout. Each component starts at Z=0. Arms use the motor
shaft center as their origin, with the shaft extending toward negative Y. Arm
extensions preserve mounting patterns; selected hole diameters and thicknesses
are independent parameters. Unsupported parameter changes fail explicitly.

## Assembly status

The assembly contains four arms, three plates, and eight simplified standoffs.
It uses assumed 2.5 mm plates, 5 mm arms, and top-plate underside Z=35 mm.
Its [fit report](exports/assembly/assembly-report.json) currently records:

- Diagonal wheelbases of approximately 302.59 and 303.99 mm, falling short of the
  confirmed 330 mm target by approximately 27.41 and 26.01 mm.
- Mounting offsets up to 0.753 mm and arm-root intersections totaling 77.70 mm³.
- Unconfirmed scan metric calibration, stacking dimensions, and arm placement;
  end brackets and fasteners still need modeling.

The scans define the intended shapes, but their physical scale and the assembly
placement must be reconciled with the confirmed wheelbase. Current exports preserve
reconstructed outlines; they are not yet a completed 330 mm frame. A passing
comparison with the old FreeCAD solids establishes reproduction of that model,
not agreement with all authoritative references.

## Verification and references

```sh
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy src/tigerbee
uv build
```

Tests compare the original three solids against independently exported STEP
baselines, exercise parameter changes, check mesh topology and export round trips,
and detect assembly alignment/interference errors. The workflow also audits runtime
dependencies and exports native FreeCAD documents headlessly.

`src/tigerbee/profiles/` contains analytic profiles from the original saved solids
and periodic spline profiles traced from Scan_2. `tools/extract_freecad.py` is a
one-time migration tool run inside FreeCADCmd; normal builds never import the
reference document. `uv run --group tracing python tools/trace_scan.py` regenerates
the provisional scan profiles, recording the inferred A4 scale and nominal holes.

See [reference authority](refs/SOURCES.md), [the implementation contract](tasks/plan.md),
and [remaining tasks](tasks/todo.md).
