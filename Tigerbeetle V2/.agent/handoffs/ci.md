# CI / release implementation handoff

Owner: ci_release. Owned files: `.github/workflows/{ci,cad,release}.yml`,
`tools/package_release.py`, `tests/exports/test_packaging.py`, `docs/ci.md`, this file.

Implemented quality pipeline, full native-FreeCAD CAD build, five preset checks,
complete artifacts and tagged publication dependent on both quality and CAD jobs.
Packaging validates all format inventories, checksums, FreeCAD reopen report,
parameter snapshot equality, five preset pass reports and both PNG/SVG overlays.
It rejects stale unmanifested CAD files and preexisting package destinations.
Archives and manifests include all requested release categories and checksums.

Verified locally: 11 packaging tests pass, ruff passes for owned Python files,
strict mypy passes for tools/package_release.py. Workflows parsed as YAML.
Hosted workflows / apt FreeCAD execution / real full-frame packaging are not yet
verified by this agent; coordinator owns the full integrated execution.

Required exporter metadata keys: project_version, git_commit, preset,
python_version, build123d_version, parameters, wheelbase_mm. Exporter manifest
formats/components/artifacts contract coordinated with export_finish. Each physical
component requires an SVG profile and dimensioned SVG (assembly agent now provides
profiles for all parts). Required preset reports are stdout from validate commands
at artifacts/reports/validate-{preset}.json.

IMPORTANT: actual Git root is parent FreeCAD-Projects. Nested project workflows
will not run there until installed in its root .github/workflows. All three jobs
auto-detect project root or Tigerbeetle V2 subdirectory once installed. No parent
filesystem, git metadata, remote or branch protection was modified. docs/ci.md
states the activation limitation and alternatives explicitly.

Official action interfaces verified via web: checkout v7, setup-uv pinned SHA
bec219d24cd3e171d82865faccec33120bb574f4 (v10.1.0), upload v7, download v8.
Local uv used UV_CACHE_DIR=/tmp/fpv-ci-uv-cache to keep cache writes in writable
temporary storage. No package dependencies added.
