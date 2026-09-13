# Tigerbee implementation contract

## Objective

Recreate each of the five frame components shown in Scan_1 and Scan_2 as separate
build123d models, then build the final FPV frame assembly. Supply a modern Python
project, local CLI, parameter presets, geometry tests, and GitHub Actions artifacts.
Commit generated 3MF, STL, and native FCStd outputs as ordinary repository files.
The target is the physical 7-inch Tiger Beetle, measured at approximately 303–304 mm
between opposite motor-hole centers. Product-photo wheelbase labels are superseded.

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

- Physical measurements and near-1:1 pen tracings are authoritative; see refs/SOURCES.md.
- Geometry consists of lines, arcs, circles, periodic scan splines, and parameters.
- No FreeCAD runtime or reference-file imports during normal model builds.
- Existing FreeCAD solids provide a regression baseline for the first three components,
  subordinate to the authoritative scans and final product photo.
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
- User confirmed both scans are near-1:1 A4 pen tracings with small drawing errors.
- Scan_2 parts are named rear-plate and top-plate; local interface fit remains provisional.
- Unextended assembly diagonals are 302.592 and 303.986 mm, consistent with physical readings.
- Mounting offsets reach 0.753 mm; arm-root intersections total 77.70 mm³.
- Confirm stacking order, vertical spacing, arm placements, and hardware dimensions.
- Both 330 mm and 295 mm photo labels are superseded; thickness labels remain assumptions.
- Material and manufacturing process are not established; geometric validity does
  not establish mechanical strength or flight readiness.

## Boundaries

Preserve manual source files and sibling projects. Canonical CAD outputs go under
tracked exports/ as regular Git files with source and output hashes checked in CI.
Temporary variants go under ignored build/. GitHub artifacts supplement committed
outputs. Workflow files live at the parent Git repository root.
Do not publish releases or fabricate confirmed measurements.
