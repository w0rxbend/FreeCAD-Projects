# Geometry review completed — bounded profile and clearance corrections

## Evidence and implementation

- Inspected both current source/CAD overlays with `view_image`, then rendered revised diagnostics under `/tmp/geometry-review-overlays` and inspected both again. No source scans or measured coordinates were changed.
- Scan 1 nose crown/valley and shoulder-to-root circular arcs overshot the traced boundary. Replaced those transitions with sparse, named cubic Bézier spans; top lobes retain a circular cap. The corrected outlines visually follow the ink closely.
- Scan 2 long plate paired diagonal apertures were too thin vertically. One wide and one narrow repeated primitive now use 16.5/14 mm longitudinal envelopes and matching diagonal edges. The forward vertical pair was translated rearward 3 mm. The accessory shoulder now uses a cubic transition to preserve minimum material around its bore.
- All plate outline landmarks and nonstructural aperture centers now follow shared longitudinal stations and lateral spans. Smoothstep interpolation of datum displacement preserves nominal reference geometry and dimensional offsets beyond the tips. Bore diameters and aperture shapes are preserved. Structural bores still originate exclusively from shared layout; no duplicate axes or source-pixel vertices were introduced.
- Added an actual BREP ligament regression covering every long-plate opening; all exceed the configured 1.5 mm edge minimum. Existing changed-datum tests reproduced three errors before the fix and pass afterward, including moving the large forward stack access bore with its datum.

## Canonical arm root: explicit engineering departure

The traced root envelope is approximately **38 × 31 mm**. With the accepted shared bolt axes and four reflected placements, that envelope causes **372.016 mm³ total arm overlap** at the user-confirmed 5 mm thickness. Collision bounds local to the canonical root were the left finger at x[-10.5,-3.6], y[-31,-25], outer left lobe x[-18.8,-13], y[-23.5,-18.2], and right lobe x[16.2,19.2], y[-22.5,-18].

The reference profile uses **35 × 29 mm** for the root envelope: a local analytical contour correction of roughly 1.5–2 mm per affected edge. Shared root bores, motor center, motor paddle and shaft dimensions remain unchanged. This produces zero arm overlap and a measured **0.291 mm minimum arm-to-arm gap**, above the configured 0.2 mm general clearance. One canonical arm is still reflected/rotated into all four placements. A regression uses the actual four transformed BREP solids and asserts both the gap and absence of intersection.

This root envelope is an engineering reconstruction that prioritizes shared interfaces and assembly feasibility. It is not claimed to be the exact traced root shape. Original scan measurements remain authoritative evidence, untouched; `reference_arm_profile().evidence` explicitly records the departure and need for physical confirmation.

## Checks and remaining integration

- Plate suite: 44 passed, including interface deformation and minimum top-plate ligament.
- Combined final arm/plate suite: **54 passed** in 15.19 s. Scoped Ruff check passed; strict mypy passed for all three changed/reviewed implementation modules.
- Parent should regenerate published overlays, STEP/STL/DXF/SVG and assembly/deviation reports from current source. Root scan deviation will increase locally and must remain visible in the report. Physical root fit, motor pattern assumptions and photo-inferred standoff heights still require explicit evidence status.
- No CLI/export implementation or Git operations were performed by this specialist.


## Retrospective handoff audit — 2026-09-13

This addendum was written after the original task. It preserves the observations
and test results above; it does not attribute later knowledge to the original
reviewer. Current disposition is indexed in [handoff-index.md](handoff-index.md).
Later evidence is in [acceptance-review.md](acceptance-review.md), the maintained
[reconstruction guide](../../docs/blueprint-reconstruction.md), and
[current state](../STATE.md). Historical follow-ups are not automatically current
blockers; use those records to determine which were completed or remain open.

STATUS: Bounded geometry corrections completed and reviewed; final integration
and provenance regeneration remained with the coordinator at handoff time.

FILES CHANGED: `src/fpv_frame/parts/plates.py`,
`src/fpv_frame/parameters/arms.py`, and arm/plate geometry regression tests were
reported for this slice. This audit adds only this retrospective summary and index.

RESULT: Improved analytical contour/aperture fit, shared-datum deformation and
actual material ligaments; corrected canonical root geometry to avoid overlap.

MEASUREMENTS/DECISIONS: Preserved the traced approximately 38 × 31 mm root evidence
while selecting 35 × 29 mm for the analytical reconstruction. The original slice
measured zero arm overlap and approximately 0.291 mm minimum gap; later independent
acceptance retains this explicit departure.

ASSUMPTIONS: The local root reduction needs physical confirmation. Height, motor
pattern and purchased hardware retain their separate provisional evidence.

VALIDATION EXECUTED: Original slice inspected both revised overlays, passed 44
plate tests and then 54 combined arm/plate tests, with scoped Ruff/mypy passing.
This audit inspected those results; it did not rerun geometry validation.

KNOWN LIMITATIONS: Overlay agreement is not exact replacement-part identity.
The historical mention of DXF in follow-ups was not an implemented or required
release format; the supported five formats are STEP, STL, 3MF, SVG and FreeCAD.

FOLLOW-UP TASKS: Use acceptance-review.md for subsequent visual/mechanical closure
and STATE.md for current artifact regeneration and release evidence.
