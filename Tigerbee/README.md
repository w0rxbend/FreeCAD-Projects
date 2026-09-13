# Tigerbee CAD

Build123d reconstruction of the Tigerbee FPV frame. Work in progress: the target
is five individually buildable components followed by a located frame assembly.

This is a self-contained uv project inside the FreeCAD-Projects repository.
The original FreeCAD document, scans, and manual mesh exports are reference inputs.

## Development

```sh
uv sync --locked
uv run tigerbee list
uv run tigerbee build --all
uv run tigerbee build arm-type-1 --thickness 5.5 --output build/custom
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy src/tigerbee
```

See [the implementation plan](tasks/plan.md) for scope and outstanding measurements.

The three original components are implemented. Each build produces STEP, 3MF,
STL, SVG, DXF, and JSON metadata under `build/parts/`. The two arms use their motor
shaft centers as local origins and point toward +Y; the camera plate uses its
large circular opening as the origin. Each lower face is at Z=0.

Analytic profiles in `src/tigerbee/profiles/` preserve lines, arcs, and circles
from the saved FreeCAD solids. Normal builds need only Python and build123d.
`refs/baseline/` holds independently exported STEP references for geometry tests.
The optional `tools/extract_freecad.py` migration script runs in FreeCADCmd via
`runpy.run_path(..., run_name="__main__")`; it is not part of the build pipeline.
