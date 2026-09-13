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


## Retrospective handoff audit — 2026-09-13

This addendum was written after the original task. It preserves the observations
and test results above; it does not attribute later knowledge to the original
reviewer. Current disposition is indexed in [handoff-index.md](handoff-index.md).
Later evidence is in [acceptance-review.md](acceptance-review.md), the maintained
[reconstruction guide](../../docs/blueprint-reconstruction.md), and
[current state](../STATE.md). Historical follow-ups are not automatically current
blockers; use those records to determine which were completed or remain open.

STATUS: Original CI/packaging slice completed; release-audit.md supersedes its
initial workflow-location, packaging-test-count and FreeCAD-runtime limitations.

FILES CHANGED: `.github/workflows/{ci,cad,release}.yml`,
`tools/package_release.py`, `tests/exports/test_packaging.py`, `docs/ci.md` and this
handoff were the original owned files. Later parent workflow installation belongs
to the release audit, not to this original slice.

RESULT: Implemented quality/CAD/tagged-release workflow definitions and strict
artifact packaging. Subsequent work strengthened parameter/report freshness,
native inventory checks and the pinned FreeCAD runtime.

MEASUREMENTS/DECISIONS: Actual Git root is the parent FreeCAD-Projects repository.
The later release audit installed uniquely named active parent workflows while
preserving the sibling workflow; nested files remain standalone templates.

ASSUMPTIONS: Hosted execution requires the workflows to exist on the remote
revision under test. Local verification alone does not establish branch protection,
a successful hosted run or publication of a tagged release.

VALIDATION EXECUTED: Original slice passed 11 packaging tests, scoped Ruff/mypy and
YAML parsing. Later actionlint, expanded packaging tests and exact headless pinned
AppImage tests are recorded by release-audit.md. This audit ran no workflow job.

KNOWN LIMITATIONS: The original statement that parent workflows were uninstalled
is historical. Current hosted/build/release disposition is owned by STATE.md and
the release audit; no remote result is inferred from local file existence.

FOLLOW-UP TASKS: Consult current state and release/plan audits for clean-checkout,
artifact provenance and hosted execution requirements still awaiting evidence.
