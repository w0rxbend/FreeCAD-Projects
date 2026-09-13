# Tigerbee symmetric design contract

## Objective

Refine all five frame components and their assembly into an analytic, symmetric,
parametric CAD design. Fix the visible top/rear/camera plate irregularities,
misaligned bores and protruding arm roots. Preserve the supplied FreeCAD/3MF
foundation and make every canonical export reflect the same current geometry.

## Reference and modeling requirements

- Tigerbee.FCStd and the three supplied arm/camera 3MF files outrank Scan_1/Scan_2.
- Preserve their design intent, camera central square opening and confirmed 5 mm arms, 3 mm plates and 6 mm standoff outside diameter.
- Use Scan_2 for the missing rear/top plate silhouettes, with nominal analytic features.
- Do not use compare_a4 as an authority or a completion gate.
- Every plate and each arm pair must mirror exactly across frame X=0.
- Rear/top outlines and repeated openings use lines, tangent radii and circles.
- Shared mounting coordinates must produce coaxial holes through every mating layer.
- Four actual motor centers form a square X with both diagonals exactly 305 mm,
  perpendicular at frame (0,0), superseding the historical 303–304 mm estimate.
- Preserve arm motor and root patterns; relieve colliding root tips deliberately.
- Keep the clamped arm bases inside both lower plate outer silhouettes; distinguish
  the inward base from the shaft entry using the innermost clamp bore and its material margin.
  Blend any trimming tangentially into the original shaft, preserving mounting ligaments.
- Keep dimensional parameters in Python, independent of generated CAD files.
- Reject invalid dimensions, lost holes, split solids or disconnected features.

## Acceptance evidence

- Independent Boolean reflection of complete plate solids and arm pairs.
- Actual circular bore edges and unobstructed shaft passages through all clamp/support layers.
- No positive-volume interference among any assembly components.
- Measure arm-root projection outside each actual lower plate silhouette and reject
  protrusions, including symmetric protrusions that pass reflection checks.
- Actual mounting-edge ligament and 7-inch motor-to-motor propeller-disc clearances.
- Exact intended opening counts and only analytic lines/circles in the engineered plates.
- Source reference regressions, parameter variants, mesh audit and STEP round trips.
- Regenerate all component and assembly STEP/3MF/STL/SVG/DXF/GLB outputs as applicable.
- Save and reopen all six generated FCStd documents and verify source/output hashes.
- Inspect freshly rendered component and assembled SVGs, not just test reports.
- Run the full pytest suite, Ruff, mypy and package build; exercise strict assembly fit in CI.

## Physical scope

The geometry gate establishes nominal CAD fit. Plate stock 3 mm, arm stock 5 mm
and standoff outside diameter 6 mm are user-confirmed. Top underside Z=35 mm and
the standoff 3.2 mm bore are retained nominal choices. Material,
layup, machining tolerances, purchased hardware and physical fit/load tests remain
necessary for a physical production release. Do not report those as measured or
validated. End brackets require dimensions beyond the five supplied plate designs.

## Boundaries

Preserve manual reference files and sibling projects. Canonical outputs go in
tracked exports/ with source and file hashes. Experiments go under ignored build/.
Do not publish a release or substitute an easier passing geometry for the actual
requested symmetric, faithful frame.

## Additive accessories: arm protector feet

The [arm-protector design](arm-protectors.md) adds separately exported TPU-intent
motor-pad bumpers and 12 mm landing feet for both source arm types and both hands.
The carbon frame geometry, 305 mm layout and original assembly export remain
independent. `tigerbee protectors` generates four printable components and a
19-solid assembly preview, with actual-solid fit and mesh checks. Canonical
rebuilds now include this command before native export and inventory verification.
