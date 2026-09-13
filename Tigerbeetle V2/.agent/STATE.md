# Current state

Updated2026-09-13. Core model/export/review complete. Final source refresh and
latest hosted checks are in progress; no tagged release has been published.

Confirmed evidence: original A4 tracings preserved, arms5mm, all3plates2mm.
Shared coordinate system+Xright,+Yfront,+Zup; motor-centroidXY. Reference plates
Z0–2,7–9,34–36mm. H25mm and nominal equipment remain explicit assumptions.

Implemented: shared immutable parameters/interfaces; canonical handed arm;
three symmetric plate builders; independent tubular standoff builder;15named
parts; actual BREP topology/features/bores/symmetry/interference/clearance gates;
nominal equipment envelopes; source overlays/fit report; all CLI commands;
STEP/STL/3MF/SVG/FCStd native reopen; hashed metadata and complete release package.

Evidence:
- Clean checkout1b9527d:193tests including nativeFreeCAD; frozen sync, Ruff, mypy,
  build, all5presets, full export/drawing/selectedarm subset, overlays, package,
  final gitstatusclean. Record:/tmp/tiger-v2-clean-7j5orqnn/summary.json.
- Hosted same commit: CI34780185009 and CAD34780184980 succeeded; downloadable
  complete CAD and release archives. CI191passed/2native skips; CAD ran native tests.
- Later standoff-builder refactor148785a:21geometry/assembly tests pass, all5presets.
- Independent acceptance review closes all critical geometry findings, including
  full profile inventory/count and profile-to-solid extrusion checks.
- Both overlays accepted with explicit root35×29mm departure from traced≈38×31mm.
  Source marks≤0.70mm hole residual; actual mating bores≤2.85e-14mm alignment error.

Latest source must get refreshed clean metadata and hostedchecks before final
acceptance. Exact all-format selected-arm and STEP-only CLI smokes remain to run.
PLAN audit covers all76sections and named outputs in .agent/handoffs/plan-audit.md.
Raw historical findings remain preserved; handoff-index.md identifies supersession.

Git root: parent FreeCAD-Projects. Local branchfeature/tigerbee-build123d;
remote delivery branchfeature/tigerbeetle-v2. Three active parenttigerbeetle-v2-*
workflows preserve existing tigerbee.yml. No merge or tag has been performed.

Baseline1b9527d export falsely recorded git_dirty=true because its own staging
directory existed during provenance capture. That metadata defect is now fixed;
18 export tests pass, including initially clean/dirty state and actualFreeCAD.
Final clean checkout must explicitly assert git_dirty=false before acceptance.
