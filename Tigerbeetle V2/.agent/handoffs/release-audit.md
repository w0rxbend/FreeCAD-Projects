# Release audit completion

Owner: release_audit. Reviewed PLAN sections 35–38. No remote writes, tags, or
releases were performed.

Changes:
- `tools/package_release.py` now requires every validation report to identify its
  named preset, contain a canonical SHA-256 parameter hash, and match the current
  preset definition. The selected report must also match exported parameters,
  wheelbase and component count. Export metadata must supply its correct hash.
- FreeCAD reopen evidence must enumerate exactly the exported component names,
  one solid each, with matching total solid count.
- Added regression coverage for missing identities, cross-preset reports, stale
  snapshots with internally consistent hashes, invalid export hashes, dimension
  and component-count disagreement, and native inventory disagreement.
- Installed parent repository workflows at
  `../.github/workflows/tigerbeetle-v2-{ci,cad,release}.yml`, preserving tigerbee.yml.
  Project `.github/workflows/{ci,cad,release}.yml` remain standalone templates.
  Parent release references the uniquely named parent reusable workflows.
- CAD workflows use checksum-pinned official FreeCAD 1.1.3 AppImage. Digest
  `3a853eb69ee595f779f2255dbf80a765926981d8ff68903cefee4dfb03a8f5ef`
  independently matches GitHub's FreeCAD/FreeCAD 1.1.3 release API asset digest.
  Runtime bundle is extracted to avoid FUSE. Native pytest conversion regressions
  run with FPV_TEST_FREECAD=1 before exports.
- docs/ci.md records concrete active/template paths and integrity gates.

Verification:
- 22 packaging tests pass; new negative tests first demonstrated failures against
  the original implementation before the integrity gates were added.
- ruff passes on owned Python files.
- strict mypy passes for src/fpv_frame/parameters + tools/package_release.py.
- actionlint 1.7.12 passes all three active workflows; standalone templates were
  checked in an isolated temporary standalone repository. ShellCheck was disabled
  because it is not installed; Actions expressions/reusable references were checked.

Remaining scope owned by coordinator:
- Regenerate final reports (must include wheelbase_mm), full export and clean
  checkout package using final current parameters.
- Actual hosted execution, branch protection and tagged publication are not proven
  by local workflow validation. No remote publication is implied by these changes.
