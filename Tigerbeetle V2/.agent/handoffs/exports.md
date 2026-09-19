# Export implementation handoff

Completed by finish_exports on 2026-09-13; owns export/, drawing/,
tools/export_freecad.py and export tests excluding packaging. No geometry changes.

## Implemented and verified

- All five formats supported by export_artifacts. Physical component names survive
  STEP and named 3MF mesh objects; units are explicitly millimeters. STL is binary
  with explicit linear and angular tolerances sourced from manufacturing parameters.
- Individual-part selection omits aggregate exports and assembly views. Exporting
  does not mutate the source model's parent/child tree or labels.
- SVG cutting profiles share analytic geometry with the solids; dimensioned variants
  include overall dimensions, circular hole diameters, centers, datum and labels.
  Four orthographic assembly views use +Y as front, +Z as up; regression test added.
- Staged generation preserves existing exports on generation failure. Publishing
  removes only stale files declared in the previous export manifest.
- Metadata includes project_version (plus backward-compatible version), Python and
  build123d versions, actual Git commit/dirty state, and caller parameter provenance.
- FreeCAD conversion uses a separate native/Flatpak FreeCADCmd, saves FCStd and
  reopens it. Shapes, exact component names and solid counts are checked before and
  after. The Python/build123d model remains the source of truth.

## Actual full-frame defect found and fixed

The initial FreeCAD worker compared floating volumes with exact dictionary equality.
Real curved frame geometry reproduced a 2.1827872842550278e-11 mm³ mass-property
change after reopening, although box fixtures passed. Comparison now uses explicit
1e-10 relative / 1e-8 mm³ absolute numerical tolerance; names/counts stay exact.
The reopen report records both tolerances and maximum observed volume change.
A real 15-part frame STEP→FCStd regression now runs under FPV_TEST_FREECAD=1.

## Evidence

- `FPV_TEST_FREECAD=1 .venv/bin/python -m pytest tests/exports/test_artifacts.py
  tests/exports/test_freecad.py -q`: **16 passed in 6.73 s**.
- Scoped Ruff passes; strict mypy passes for seven export/drawing/wrapper files.
- Actual CLI `export --output artifacts/export-integration` succeeds for all five
  formats. Output comprises **84 artifacts**: 16 STEP, 16 binary STL, 16 3MF,
  34 SVG (15 plain profiles, 15 dimensioned profiles, four views), FCStd and reopen JSON.
- `artifacts/reports/export-integration.json` records an independent actual-file
  audit: every export hash, valid reimported STEP geometry, all 15 names, unit tags,
  aggregate volume consistency, STL triangle payload lengths, named 3MF mesh
  objects, all SVGs at physical 1:1 scale, FreeCAD 1.1.3 reopen with 15 named solids.
- Assembly top/front and dimensioned top plate were rendered with rsvg-convert and
  visually inspected: geometry, layer visibility, vertical stack and annotations
  are legible; no clipping observed. PNG previews are temporary /tmp/tiger-* files.

The export integration manifest may predate root's metadata-only LayoutParameters
evidence wording update. Regenerate final dist and packaged evidence from the final
revision; geometry smoke evidence remains valid. STEP/3MF can contain runtime UUIDs;
model geometry is reproducible, byte-for-byte archive identity is not claimed.

Root owns CLI, final dist/release packaging, workflow activation and documentation.

## Contract index (integration addendum)

STATUS: Completed export implementation and native verification; final integrated provenance refresh is coordinator-owned.

FILES CHANGED: export/, drawing/, tools/export_freecad.py, tests/exports/test_artifacts.py and test_freecad.py, as detailed above.

RESULT: All five formats, 84 full-frame artifacts, and native15-solid save/reopen verified.

MEASUREMENTS/DECISIONS: Preserve nominal millimeter BREP and named components; explicit native-volume tolerance handles2.18e-11mm³ roundoff.

ASSUMPTIONS: See source parameter evidence and ../ASSUMPTIONS.md; no new measured hardware dimensions asserted.

VALIDATION EXECUTED:16 export tests with FreeCAD1.1.3, Ruff, strict mypy, actual full-frame file/hash/import/render audit described above.

KNOWN LIMITATIONS: STEP/3MF container byte identity is not promised; geometry and declared checksums are verified per build.

FOLLOW-UP TASKS: Coordinator's clean-checkout and hosted publication state is authoritative in ../STATE.md and plan-audit.md.

Provenance follow-up: Git state is captured before any output/staging mutation. Both initially clean and dirty states are regression-tested; all18export tests including actualFreeCAD pass after correction.
