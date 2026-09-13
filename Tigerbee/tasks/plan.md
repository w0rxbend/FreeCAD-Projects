# Tigerbee implementation contract

## Objective

Recreate each of the five frame components shown in Scan_1 and Scan_2 as separate
build123d models, then build the final FPV frame assembly. Supply a modern Python
project, local CLI, parameter presets, geometry tests, and GitHub Actions artifacts.

## Capability map

| Module | Responsibility | Depends on |
| --- | --- | --- |
| project-tooling | Locked Python environment and developer checks | — |
| tigerbee-models | Independent parametric profiles and solids | project-tooling |
| cad-build | Selection, validation, exports and manifests | tigerbee-models |
| cad-ci | Automated checks and build artifacts | cad-build |

Build order: arm type 1 end to end, arm type 2, camera-side plate, Scan_2
plates, assembly. Verification and exports accompany each component.

## Modeling requirements

- Source geometry consists of lines, analytic arcs, circles, and explicit parameters.
- No FreeCAD runtime or reference-file imports during normal model builds.
- Existing FreeCAD solids provide the baseline for the first three components.
- Preserve the original saved geometry before addressing underconstraint or changing design.
- Millimeters throughout; local component datums and Z=0 lower face.
- Thickness and selected hole dimensions must be editable independently.
- Arm length changes must preserve mounting patterns rather than scale hole diameters.
- Unsupported dimensions must fail before export.
- Scan_2 profiles remain provisional until measurements establish their scale and fit.
- Assembly must use confirmed mounting interfaces, quantities, and plate spacing.
- An exploded layout alone does not satisfy the final assembly requirement.

## Verification

Test real CAD solids: validity, solid count, dimensions, hole locations, geometry
deviation from the reference, parameter variants, and exported file round trips.
Check tessellated exports independently for invalid indices, degeneracy, and edges.
Store readable build metadata and visual projections with outputs.
CI must run headlessly using the lockfile and the same CLI as local development.

## Current assumptions and open measurements

- Reproduce original geometry before redesigning parts.
- Keep tooling local to Tigerbee until broader repository scope is requested.
- Existing thicknesses: base plate 3 mm; arms 5 mm.
- Scan_1 is placed at 210 × 297.04 mm in FreeCAD; Scan_2 scale is unconfirmed.
- Need names, dimensions, and thicknesses for Scan_2 plates.
- Need stacking order, vertical spacing, arm quantities/positions, and hardware dimensions.
- Material and manufacturing process are not established; geometric validity does
  not establish mechanical strength or flight readiness.

## Boundaries

Preserve manual source files and sibling projects. Generated CAD outputs go under
ignored build/. GitHub workflow files live at the parent Git repository root.
Do not publish releases or fabricate confirmed measurements.
