# Tigerbeetle V2 parametric frame

Python/build123d reconstruction of an FPV frame from two A4 sheets traced directly
against the original parts. The model contains three carbon plates, four placed
instances of one handed arm, and eight standoffs. The user confirmed **5 mm arms
and 2 mm plates**. Source scans, measurements and the assembly photograph remain
available alongside the generated geometry.

The reference is an engineering reconstruction with explicit assumptions. The
25 mm top clearance and equipment envelopes are provisional. The canonical arm
root is deliberately 35 × 29 mm, compared with the approximately 38 × 31 mm tracing,
to clear adjacent arms while preserving the shared bolt axes. This departure is
documented in [blueprint reconstruction](docs/blueprint-reconstruction.md).

## Run locally

Run commands from this project directory. Python 3.12 and uv are required; the
committed `uv.lock` fixes dependency resolution.

```bash
uv sync --frozen
uv run --frozen fpv-frame inspect
uv run --frozen fpv-frame build
uv run --frozen fpv-frame overlay scan-1
uv run --frozen fpv-frame overlay scan-2
uv run --frozen fpv-frame export
```

The complete export requires a separate FreeCAD runtime. Detection tries
`FREECAD_CMD`, native `FreeCADCmd`/`freecadcmd`, then the installed
`org.freecad.FreeCAD` Flatpak. `FREECAD_CMD` must name an executable, without shell
arguments. A missing runtime fails the requested FreeCAD export. To generate an
explicit subset, use `export --format step --format svg`.

## Commands and outputs

Commands print JSON to stdout; validation or export errors return a nonzero exit
status. Global options precede the command, for example
`fpv-frame --preset tolerance_test validate` or `fpv-frame --root /path/to/project inspect`.

| Command after `uv run --frozen fpv-frame` | Result |
| --- | --- |
| `inspect` | Source integrity, A4 calibration and reconstruction assumptions |
| `parameters` | Full immutable parameter tree as JSON |
| `build` / `validate` | Build the frame and run mechanical gates; write `artifacts/reports/assembly.json` |
| `overlay scan-1` / `overlay scan-2` | CAD/source SVG and PNG in `artifacts/overlays`; fit report and registrations |
| `export` | STEP, binary STL, 3MF, SVG and FreeCAD bundle in `dist` |
| `export --format step` | Explicit format selection; repeat `--format` for additional formats |
| `export --part arm` | Canonical arm export in `dist/parts/arm` |
| `drawing` | Exact 1:1 profiles, dimensioned profiles and four assembly views in `artifacts/drawings` |

`export` and `drawing` accept `--output PATH`. A selected physical component can
also be exported by its model name, such as `scan1_body` or `arm_front_left`.
Selected exports omit the complete assembly. Full exports contain all 15 named
components and the frame; FreeCAD contains the assembled frame. STEP is the
canonical interchange format. The `.FCStd` document imports that STEP geometry;
the editable parametric source remains Python.

Each export directory has a manifest with file hashes, units, component inventory,
parameters and software/revision provenance. Exporting again to the same directory
replaces its previous declared inventory, including removal of formats omitted from
the new request. Use separate output directories to retain alternative selections
or presets. Original scans are never diagnostic output destinations.

## Model and evidence

Coordinates use millimeters: +X right, +Y front/camera, +Z up. Z=0 is the lower
face of the rear plate. The reference stack rises through rear plate 0–2 mm,
arms 2–7 mm, camera plate 7–9 mm, then top plate 34–36 mm. Its top clearance is
the adjustable 25 mm assumption. Wheelbase is derived from motor centers rather
than imposed independently.

`src/fpv_frame/parameters` defines dimensions and provenance; `geometry` defines
shared datums and mating interfaces; `parts` builds analytical profiles and
extrusions; `assembly` places them. `validation` measures topology, material gaps,
interference, mounting axes, symmetry and explicit equipment envelopes. `blueprint`
registers actual profiles to the scans; `export` and `drawing` consume the model.

- [Parameters and Python API](docs/parameters.md)
- [Architecture and shared interfaces](docs/architecture.md)
- [Scan calibration, interpretation and fit limitations](docs/blueprint-reconstruction.md)
- [Manufacturing assumptions and acceptance](docs/manufacturing.md)
- [Equipment design envelopes](docs/equipment.md)
- [CI and release packaging](docs/ci.md)

The five presets are regression cases, not a universal validated dimension range.
Passing CAD checks demonstrates the modeled conditions; it does not measure the
user's electronics or establish carbon strength, machining capability or flight
qualification. Read the current generated reports and their parameter provenance
when assessing a particular build.

## Development checks

```bash
uv run --frozen ruff check .
uv run --frozen mypy
uv run --frozen pytest
uv run --frozen fpv-frame --preset reference validate
uv run --frozen fpv-frame --preset minimum_supported validate
uv run --frozen fpv-frame --preset maximum_supported validate
uv run --frozen fpv-frame --preset tolerance_test validate
```

Keep source scans unchanged. Update parameter evidence when changing dimensions,
derive mating features from their common interface, and regenerate overlays and
reports after geometry changes. Review actual profiles and assembled geometry in
addition to test results. Release packaging and hosted-workflow requirements are
described in [the CI guide](docs/ci.md).
