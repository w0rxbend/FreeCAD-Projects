# Tigerbee symmetric design contract

## Objective

Refine all five frame components and their assembly into an analytic, symmetric,
parametric CAD design. Fix the visible top/rear/camera plate irregularities,
misaligned bores and protruding arm roots. Preserve the supplied FreeCAD/3MF
foundation and make every canonical export reflect the same current geometry.

## Reference and modeling requirements

- Tigerbee.FCStd and the three supplied arm/camera 3MF files outrank Scan_1/Scan_2.
- Preserve their design intent, camera central square opening and saved 5/3 mm thicknesses.
- Use Scan_2 for the missing rear/top plate silhouettes, with nominal analytic features.
- Do not use compare_a4 as an authority or a completion gate.
- Every plate and each arm pair must mirror exactly across frame X=0.
- Rear/top outlines and repeated openings use lines, tangent radii and circles.
- Shared mounting coordinates must produce coaxial holes through every mating layer.
- Four arms have equal diagonal wheelbases within the measured 303–304 mm interval.
- Preserve arm motor and root patterns; relieve colliding root tips deliberately.
- Keep dimensional parameters in Python, independent of generated CAD files.
- Reject invalid dimensions, lost holes, split solids or disconnected features.

## Acceptance evidence

- Independent Boolean reflection of complete plate solids and arm pairs.
- Actual circular bore edges and unobstructed shaft passages through all clamp/support layers.
- No positive-volume interference among any assembly components.
- Actual mounting-edge ligament and 7-inch motor-to-motor propeller-disc clearances.
- Exact intended opening counts and only analytic lines/circles in the engineered plates.
- Source reference regressions, parameter variants, mesh audit and STEP round trips.
- Regenerate all component and assembly STEP/3MF/STL/SVG/DXF/GLB outputs as applicable.
- Save and reopen all six generated FCStd documents and verify source/output hashes.
- Inspect freshly rendered component and assembled SVGs, not just test reports.
- Run the full pytest suite, Ruff, mypy and package build; exercise strict assembly fit in CI.

## Physical scope

The geometry gate establishes nominal CAD fit. The two 2.5 mm plates, top underside
Z=35 mm and simplified 6/3.2 mm standoffs are explicit design assumptions. Material,
layup, machining tolerances, purchased hardware and physical fit/load tests remain
necessary for a physical production release. Do not report those as measured or
validated. End brackets require dimensions beyond the five supplied plate designs.

## Boundaries

Preserve manual reference files and sibling projects. Canonical outputs go in
tracked exports/ with source and file hashes. Experiments go under ignored build/.
Do not publish a release or substitute an easier passing geometry for the actual
requested symmetric, faithful frame.
