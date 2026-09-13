# Full PLAN acceptance audit, sections 1–76

STATUS: Audit complete for inspected revision `1b9527da5e1e05c26b484109d132c9edcbda3fa7`; full acceptance remains pending. One narrow implementation omission and one state-structure omission identified below. Clean-checkout generation and hosted/tag publication are in progress or unproven, not assumed successful.

FILES CHANGED: This handoff only. Read-only inspection of source, tests, references, artifacts, documentation, historical handoffs and current local execution logs.

RESULT: The implemented geometry, mechanical gates, diagnostics, exports and tooling substantially cover the full plan. This is a requirement-by-requirement audit, not a claim that passing tests alone satisfy the plan. Prior numerical/visual adversarial findings and their independently verified corrections are recorded in `acceptance-review.md`.

## Concrete outstanding actions at this snapshot

1. **§16 independent component builders:** `assembly/frame.py` builds purchased standoff profiles/solids inline. The eight standoffs are included as physical components, so extract a reusable independent `standoff_profile` / `build_standoff` builder and have assembly apply shared placements. This is a responsibility separation correction; existing geometry need not change.
2. **§61 explicit dependency graph:** `.agent/TASKS.md` currently has a flat status checklist without prerequisite edges. Record scans → reconciliation → datums/interfaces → independent parts → assembly → validation/review → exports → release, with the actual remaining task dependencies. Chronological bullet order alone is not an explicit graph.
3. **§42/59/69 current records:** state and some historical handoffs still describe superseded failures or unperformed integration. Preserve original observations, but add a concise status addendum or current handoff index linking superseding evidence. The required handoff fields are status, files changed, result, measurements/decisions, assumptions, validation executed, known limitations, follow-up tasks. Some newer handoffs contain these semantically under different headings; `assembly.md` still opens with obsolete counts/failures, and `equipment.md` lists integration already completed. Do not present these as current blockers.
4. **§25/34/36–38/66/72/75 final actual output:** full-format integration output exists under `artifacts/export-integration`, but this workspace has no `dist` at inspection. The clean-checkout job is generating the final default output/package. Verify its actual completed files, hashes, reports, native reopen and final commit provenance before acceptance. Current hosted CI and tag publishing also need their own actual terminal evidence.

Physical assumptions are separate from these implementation/evidence tasks. User-confirmed A4 tracing and 5 mm arms / 2 mm plates are authoritative. H=25 mm, nominal hardware/equipment and the documented root contour departure remain explicitly provisional. The plan permits engineering interpretation rather than blind tracing; no request for additional physical measurements is introduced by this audit.

## Reading rules

“Implemented” means source and relevant tests/artifacts were inspected; it does not automatically certify a pending hosted run. “Process evidence” means retained handoffs, decisions, commits and independent review support the specified workflow. Historical exact concurrency/start times cannot be reconstructed from current files and are not fabricated here. Where the plan says “suggested”, “example”, “conceptual”, “prefer” or “such as”, the functional requirement is audited without requiring irrelevant filenames, fictitious side panels or every illustrative class name.

## Section-by-section matrix

| § | Mandatory result or invariant | Authoritative evidence and disposition |
|---|---|---|
| 1 | Python/build123d/uv/BREP, FreeCAD, Actions, swarm; source-based coherent parametric frame; all part/frame exports | `pyproject.toml`, lock, `src/fpv_frame`, 15-part assembly, integration bundle, specialist handoffs; physical assumptions explicit. Hosted/release proof pending. |
| 2 | Shared coordinate→parameters→interfaces→profiles→assembly→validation/export, no separately invented mating axes | Separate packages; `geometry/layout.py`, `patterns.py`, `interfaces.py`; actual bore tests. Implemented. |
| 3 | Preserve both original sources; derived calibration outside originals | Root JPEGs equal `references/source` copies; hardcoded SHA256 checks and corruption tests; `references/calibrated/registrations.json`. Overlay destinations follow explicit §18. |
| 4 | Analyze both scans before geometry; identify components/orientation/features, prioritize interfaces/symmetry | `scan1.md`, `scan2.md`, `standards.md`, `reconciliation.md`, `calibration-review.md`, `assembly-photo.md`; measurement records preserve original alternatives. Process evidence plus current independent acceptance. |
| 5 | Three named measurement YAML files with provenance and calibrated units | `references/measurements/{Scan_1,Scan_2,combined}.yaml`, JSON-compatible YAML with value/unit/source/confidence/method. Original hypotheses intentionally retained; combined includes later A4 evidence. |
| 6 | Multiple independent calibration anchors; reject disagreements | `blueprint/calibration.py`, calibration negative tests; A4 axes plus nested 20/30.5 grids and independent calibration review. |
| 7 | One frame-centered coordinate authority, +X right/+Y front/+Z up, shared scan datums | `geometry/layout.py` centers XY on motor centroid; Z=0 documented bottom datum; registered plate transforms map to shared axes. `test_layout.py` and front-view test. |
| 8 | Typed immutable mm parameters; avoid unexplained mechanical literals | Frozen parameter dataclasses, tuples, dimensional validators and evidence; named contour stations and root ratios. Example camera/side-panel type names are not mandatory where no such physical parts exist. |
| 9 | Primary dimensions distinct from derived positions/angles/planes | Frame derived elevations and hole allowance, shared layout-derived arms/motor coordinates/wheelbase; parameter tests and changed-layout tests. |
| 10 | Shared domain interfaces generating mating features | HolePattern, PlateInterface, ArmInterface and TabSlotInterface; interface tests enforce same axes and one total clearance. Other example class names are optional. |
| 11 | Mathematical plate symmetry and one canonical arm transformed four ways | Mirrored half contours; arm mirror/rotate/translate; actual BREP symmetry checks. |
| 12 | Adapt modular architecture to actual frame | Required concerns separated into packages. Suggested per-part/per-format filenames are consolidated where appropriate; fictitious panels/braces are not required. |
| 13 | Validated 2D profiles drive extrusion and exact SVG | `parts/arm.py`, `plates.py`, assembly profiles, `drawing/svg.py`; new inventory/opening/volume checks and tests. Standoff extraction remains action 1. |
| 14 | Minimal analytical curves, parameterized sparse splines | Named lines/arcs/rounded openings plus sparse cubic transitions tied to semantic dimensions; no raster-polyline manufacturing trace. Actual overlay review accepted. |
| 15 | Configurable compensation separate from nominal sizes | `ManufacturingParameters`; one nominal bolt plus total hole allowance; generic tab/slot clearance test. Unused generic press-fit/printed allowances documented as available for future actual interfaces, not falsely applied to carbon. |
| 16 | Independent builders for every physical component; no exports in builders | Independent arm and three plate builders implemented; standoffs inline in assembly are action 1. No part builder performs export. |
| 17 | Named complete assembly, datum-computed placements | 15 named components, one layout, derived Z planes, inventory tests. No arbitrary assembly correction offsets. |
| 18 | Two overlay CLI commands, SVG+PNG outputs, source/CAD/datums/holes/interfaces, iterative review | All four files in `artifacts/overlays`; `blueprint/workflow.py`/`overlay.py`; independent original and revised image review in geometry/acceptance handoffs. |
| 19 | `blueprint-fit.json`, outline/hole residuals, honest precision | Actual report with per-part maximum/mean outlines, individual hole residuals, parameter snapshot and directed-ink limitations. Critical BREP interfaces use tighter exact mechanical checks than cosmetic ink acceptance. Example numbers are not acceptance limits. |
| 20 | Valid topology, wires, faces, closed solids, area/volume/extrusion and expected counts; fail invalid geometry | `validation/geometry.py`, assembly opening counts 30/32/30, arms8, hardware1, profile inventory/volume checks; negative tests independently passed. |
| 21 | Explicit mathematical symmetry tests including roots/edges/holes; document intended asymmetry | `validation/symmetry.py` measures reflected material both ways, nine comparisons; layout tests; handed-root asymmetry documented. Side panels N/A. |
| 22 | Deterministic all-mating-interface tests, bolt/standoff/plane/arm alignment | Actual 88 bore rim/witness checks; shifted plate and plugged-bore negative tests; shared-interface/vertical-stack tests. |
| 23 | Unexpected overlap failure, explicit exception policy, FC/ESC/hardware/camera/roots gaps | All 105 material pairs; allowed material overlaps empty; intentional zero-volume face contacts permitted. Six actual arm pair gaps and seven equipment envelopes checked against frame and each other. Side panels N/A with reason. |
| 24 | Five named presets and representative parameter regressions in CI | `PRESET_NAMES` exactly reference/default/minimum_supported/maximum_supported/tolerance_test; assembly preset tests and workflow loop, plus stock/layout/motor-length/stack-pitch/clearance changes. |
| 25 | Default dist format directories, every component STEP/STL/3MF/SVG, complete frame all formats/FCStd | CLI default path and actual integration inventory prove implementation; final `dist` default job output pending inspection, action 4. |
| 26 | Canonical STEP with names/mm where possible | Export detaches copies, names solids, sets units; actual reimported 15 component geometries/names and frame volume in export integration report. |
| 27 | Binary STL with explicit linear/angular tolerances | Export settings from manufacturing params, binary flag; actual triangle payload tests and integration audit. |
| 28 | build123d mesh-based 3MF with separate components | Mesher-based named individual objects; current integration report validates 15 aggregate object names and individual outputs. |
| 29 | STEP→native FreeCAD→FCStd, Python source authority, wrapper file | `tools/export_freecad.py`, `export/freecad.py`, `freecad_worker.py`; actual 1.1.3 save/reopen, real curved-frame regression. Flatpak/native AppImage both verified. |
| 30 | 1:1 exact planar SVG, contours/holes/marks/datums/dimensions/labels; assembly views | 15 plain +15 dimensioned profiles, four assembly views; exact path export, mm scale and front +Y regression; specialist rendered drawings. Suggested names adapted to source IDs. |
| 31 | All ten named CLI invocations and nonzero validation errors | Parser/dispatch implements build, validate, export, format selection, part arm, drawing, both overlays, inspect, parameters. Missing-source failure tests cover geometry commands; clean-job exact command outcomes pending, see command matrix. |
| 32 | uv/build123d/pytest/ruff/type checker, project files/src layout/frozen CI | `pyproject.toml`, `uv.lock`, `.python-version`3.12, strict mypy, Ruff, pytest; both CI workflows run `uv sync --frozen`. |
| 33 | Engineering invariant tests | `tests/unit`, blueprint, geometry, interfaces, assembly, exports; symmetry and regression tests live in those suites. Suggested folder names are not mandatory. |
| 34 | Clean checkout frozen setup/validate/export; avoid generated binaries in Git | `.gitignore` excludes dist/artifacts/env/cache; clean clone job ongoing, not yet proof of complete reproduction. |
| 35 | CI workflow checkout→uv frozen→lint/types/tests/assembly/export smoke | Project template `.github/workflows/ci.yml`; active parent `tigerbeetle-v2-ci.yml`; source and actionlint reviewed. Hosted terminal result pending. |
| 36 | CAD workflow uploaded complete cad-artifacts layout | Project/parent CAD workflow and `package_release.py`; format dirs, overlays, reports, parameters and hashes declared/validated. Actual final package/upload pending. |
| 37 | v* tag workflow publishes complete format/evidence/checksum artifacts | Project/parent release workflow calls quality+CAD then verifies downloads and creates release; tag publication remains unproven until actual run/assets. |
| 38 | Manifest version/revision/preset/dimensions/Python/build123d/files/hashes | Export metadata and complete parameter tree + wheelbase; package validates snapshot hashes, current presets and native inventory. Integration artifact hashes independently verified; final provenance pending. |
| 39 | Five named docs covering coordinate/calibration/parameters/interfaces/tolerances/exports/manufacturing | README and `docs/{parameters,architecture,blueprint-reconstruction,manufacturing}.md` all inspected; added equipment/CI docs clarify assumptions. |
| 40 | Explicit multi-agent development and orchestrator integration | Independent scan/reconciliation/architecture/geometry/assembly/equipment/export/CI/review handoffs and live delegated audit. Satisfied by actual specialists, not only a written plan. |
| 41 | Orchestrator backlog/dependencies/ownership/reconciliation/integration/final checks | `.agent` records, staged integration commits, reviewer fix loop, live clean job. Current record refresh remains action3. |
| 42 | Persistent concise state/decisions/assumptions/tasks/findings/handoffs | All named records exist; some status entries stale, action3. Conversation is not the only memory. |
| 43 | Independent separate Scan1/Scan2 analysis and equivalent outputs | Distinct analyst handoffs and source-only YAML observations; Scan2 explicitly records independence from Scan1. |
| 44 | Separate reconciliation preserving conflicting originals | `reconciliation.md` and combined.yaml; raw per-scan YAML remains preserved, orientation conflict corrected explicitly. |
| 45 | Mechanical standards specialist, documented corrections | `standards.md` includes manufacturer references and hypotheses; motor circle vs square correction retained in docs/evidence. |
| 46 | Architecture specialist before detailed modeling, architecture docs/types, review | `architecture.md` handoff, initial types/docs and commit sequence support staged architecture; later independent review verifies current contracts. Exact historical review-start timestamp is not recoverable from current files. |
| 47 | Independent component work after stable interfaces | Canonical arm/plate work and shared layout ownership recorded; no duplicated mating coordinate authority found in current code. |
| 48 | Dedicated canonical arm reconstruction with axes/root/motor/profile/overlay | `parts/arm.py`, arm source parameters, arm tests, both actual arm overlays, geometry-review handoff; four mathematical placements. |
| 49 | Dedicated interface/mechanical compatibility ownership and rejection authority | Shared interfaces/layout, architecture/assembly/final-review records; actual root collision and duplicated-datum concerns caused corrections rather than arbitrary moves. |
| 50 | Separate assembly integration with placement/collision/clearance review | `assembly.md`, shared model/layout and 15-part report; root collision returned to geometry owner and corrected at source. |
| 51 | Independent adversarial reviewers after generation | Calibration, geometry, initial final-review, acceptance-review and release-audit; concrete faults and subsequent fixes recorded. |
| 52 | Structured actual scan overlay review | Geometry-review and acceptance-review cover all five drawn components, exterior/interior features, holes, residuals and explicit root departure. |
| 53 | Independent data/model symmetry review | Acceptance review inspected reflection/transform sources and actual BREP symmetry implementation, not only pictures. |
| 54 | Numerical adversarial mechanical fit checks | Initial review reproduced 1 mm hardware-wall failure and ignored2 mm gap; acceptance reproduced empty-profile bypass; implemented negatives confirm closure. |
| 55 | Reject fake parameters/duplicated geometry/arbitrary assembly offsets | Shared semantic layout deformation, immutable primaries, canonical profiles; acceptance code review and changed-datum tests support current model. |
| 56 | Export specialist owns all formats/metadata/layout without changing geometry to appease exporter | exports handoff and own source/tests; fixed parenting and numeric native-reopen tolerance without modifying CAD geometry. |
| 57 | Infrastructure specialist owns locked CI/build/publish/checksum/manifest | ci/release-audit handoffs and active workflows, strict packager tests. Actual hosted execution remains distinct. |
| 58 | Delegated scope/inputs/outputs/ownership/invariants/tests/blockers | Specialist assignments/handoffs have bounded ownership and validation records. Exact suggested nine-field spelling is guidance (“should”), not a new artifact requirement. |
| 59 | Structured handoffs with eight required information categories and orchestrator inspection | Core analyst/architecture/reviewer handoffs carry fields; later handoffs use alternative headings and some outdated status. Current-status addendum/index needed, action3; preserve original evidence. |
| 60 | Parallelize independent work only, shared definitions first | Ownership decisions and shared interfaces retained; historical exact simultaneous start times cannot be proven from files, but no current competing interface authority found. |
| 61 | Explicit dependency graph | Missing explicit edges in current flat TASKS; action2. |
| 62 | Multiple-agent consensus on ambiguous important dimensions, decisions recorded | Standards/calibration/reconciliation/photo/geometry reviews disagree then reconcile; `.agent/DECISIONS.md`, retained source uncertainty and root departure. |
| 63 | Confidence metadata and independent review of weak assumptions | ParameterEvidence + measurement provenance; user-known thickness distinct from assumed height/motor/equipment; independent acceptance retains limits. |
| 64 | Fault-seeking independent review | Concrete replicated failures in final/acceptance/release audits, corrections and negative tests. |
| 65 | Implementation→tests→CAD/overlay→review→source correction→revalidation loop | Geometry-review before/after overlays; initial failed full-frame FreeCAD reopen then actual corrected run; runtime gates corrected after reviewer reproduction. |
| 66 | Six explicit integration gates, earlier unresolved gate blocks later acceptance | Detailed gate matrix below. Root clean/package/hosted evidence still pending; later success cannot erase actions1–3. |
| 67 | Preserve conflicting conclusions, compare evidence, review, canonical decision and reason | Raw scan hypotheses, calibration correction, same-orientation resolution, documented35×29 root correction. |
| 68 | Isolated worktrees where tooling permits; core interfaces have one owner | Shared workspace non-overlapping ownership decision documented during restricted setup; root integration branch and current isolated clean clone. Worktree names shown in PLAN are examples. |
| 69 | Dependency-aware task status and satisfied prerequisites | TASKS exists but needs graph and final status refresh, actions2–3. |
| 70 | Autonomous bounded work; integration authority for datums/tolerance policy | Agent ownership, direct testing and specialist corrections; root accepted shared root dimensions and separate hardware wall policy without weakening carbon criterion. |
| 71 | Capture/classify failure, retry bounded specialist rather than full restart | Retained collision, thin-ligament, native-reopen and gate-bypass findings with targeted corrections/tests. |
| 72 | All phases0–11: bootstrap, independent analysis/reconciliation, architecture, component/review/assembly/mechanical/export/infrastructure/final review, clean candidate | Process evidence maps to §§40–71. Final phase11 clean committed rebuild currently active. Suggested separate reviewer role names do not require one permanent agent per name if independent reviews cover them. |
| 73 | Continue inspect/delegate/integrate/review/update/gate loop until actual acceptance | Current root clean job and this independent full audit demonstrate ongoing loop; no full-completion declaration supported yet. |
| 74 | No noise tracing/independent datums/excessive clearances/artifact patching/render-only acceptance | Current source and review corrections satisfy geometric prohibitions; explicit0.2 mm gap not enlarged to hide conflict; exact source profiles drive exports; all defects corrected in code. |
| 75 | Every named final requirement, including hosted clean reproduction and tagged artifacts | Geometry/export evidence detailed in acceptance-review; present audit adds §16/61/records gaps; hosted/tag evidence remains pending. |
| 76 | Mechanically coherent, symmetric, parametric manufacturing geometry survives independent review | Geometry and assumptions reviewed; quantitative gates and exported artifacts support engineering reconstruction. Physical strength/exact replacement identity remain unclaimed; full final acceptance waits outstanding items. |

## Exact command and artifact evidence

| Required command / artifact | Evidence at inspection |
|---|---|
| `uv sync --frozen` | Workflow source; clean-job progress has `END sync: 0`. |
| `fpv-frame build` / `validate` | Implemented dispatch to build+all mechanical gates; five real validation JSONs; root clean job will execute current committed versions. |
| `fpv-frame export` | Full actual CLI export to integration directory,84 artifacts; final default-path clean execution pending. |
| `fpv-frame export --format step` | CLI supported; export tests exercise subset formats. Exact installed-command end-to-end run should be retained in final clean evidence if not already recorded elsewhere. |
| `fpv-frame export --part arm` | CLI canonical-arm selection and separate output path; export tests exercise individual selection. Exact installed-command end-to-end run should be retained in final clean evidence. |
| `fpv-frame drawing` | Dispatch supports independent SVG output; specialist generated and viewed four assembly/profile views. Clean job independently invokes drawing. |
| `fpv-frame overlay scan-1`, `overlay scan-2` | Four real overlay files and fit/registration reports; both PNGs independently viewed and hashed in acceptance review. |
| `fpv-frame inspect` | Actual subprocess success test validates source dimensions/calibration/user stock. |
| `fpv-frame parameters` | Full immutable tree dispatch; `artifacts/parameters.json` and manifest compare; clean job retains current output. |
| Nonzero validation failure | Actual subprocess missing-source cases for build/validate/export/drawing/overlay; geometry/interface/collision failures propagate as ValueError→exit1. |
| Named measurement files / calibration output | All three YAMLs plus calibrated registrations inspected. No source changes. |
| Named format dirs and component/frame files | Actual integration inventory16STEP/16STL/16three-MF/34SVG/FCStd/reopen; defaultdist and final package pending. |
| `cad-artifacts/{step,stl,3mf,freecad,svg,overlays,reports,parameters.json}` | Packager builds/validates exact structure;22 packaging tests and workflow source; actual final package/upload pending. |
| Release STEP/STL/3MF/FreeCAD/SVG/overlays/reports/parameters/SHA256SUMS | Published as named ZIPs plus manifest/checksums by tag workflow; actual publication pending. |
| `manifest.json` | Integration real manifest includes required metadata, all84 sizes/hashes independently verified; current final revision provenance pending. |
| README + five named docs | All required paths exist and substantive content inspected; `docs/ci.md`/equipment add scope detail. |

## Integration-gate disposition

| Gate | Evidence | Disposition |
|---|---|---|
| 1 Blueprint | Both independent measurements, reconciler, A4 calibration, actual overlay review | Pass for documented interpretation. |
| 2 Architecture | Immutable parameters, shared datums/interfaces, modular builders | Narrow §16 standoff responsibility correction pending. |
| 3 Components | Valid profiles, expected counts, exact symmetry, all component overlays | Pass for current geometry; rerun relevant checks after builder extraction. |
| 4 Assembly | All15 components,88 actual bores,105 material pairs,6 arm gaps,9 mirrored comparisons | Pass in current tested model. |
| 5 Manufacturing |1.5 mm carbon ligaments/1 mm hardware walls, explicit envelopes, actual valid exports, dimensioned drawings | Pass for specified geometric assumptions; no physical stock/process qualification inferred. |
| 6 Release | Local suite185passed/1skipped, native export tests separately pass, complete integration artifacts/reviews/checksums/manifest | Final current-source clean package and hosted/tag evidence pending. |

VALIDATION EXECUTED: Entire PLAN text read, all76 sections mapped; required files/commands/validators/tests/workflows inspected; concrete local logs read. `/tmp/tiger-v2-full-tests.log` ends185 passed/1 skipped; `/tmp/tiger-v2-profile-final.log` ends13 passed; native FreeCAD coverage is separately recorded in exports/release-audit. Clean progress at this inspection ended at `START tests`, after successful clone/sync/lint/types. No hosted/tagged outcome is inferred from source files or this partial progress log.

MEASUREMENTS/DECISIONS: Interpret optional class/module/directory examples functionally. Treat mandatory independent component builders and explicit dependency graph as real requirements. Preserve physical assumptions and original observations rather than pretending every original handoff was always correct.

ASSUMPTIONS: Known/provisional dimensions are exactly those documented in `.agent/ASSUMPTIONS.md` and acceptance-review. No new dimensional assumption introduced.

KNOWN LIMITATIONS: Historical exact scheduling/ownership conversations are not reconstructed from retained files; current process artifacts and independent results are the available evidence. Root owns terminal clean-job/hosted/tag evidence and final current-state record updates. Any source change after this revision needs proportionate verification and a provenance refresh.

FOLLOW-UP TASKS: Resolve actions1–3; finish clean default export/package and exact CLI smoke evidence; inspect actual hosted CI/CAD/tag assets before declaring full PLAN complete. Update this audit with actual evidence, not intended actions.

## Coordinator follow-up (after this review snapshot)

- §16: independent standoff_profile/build_standoff added in commit148785a;21 component/assembly tests pass, including all five presets. Geometry dimensions and placements preserved.
- §61: prerequisite edges now recorded explicitly in .agent/TASKS.md.
- §59: historical handoff contract addenda and handoff-index.md preserve original observations and identify superseding evidence.
- Clean checkout1b9527d completed frozen sync, lint, strict types,193 tests including native FreeCAD, build, all five presets, full export, drawing, selected-arm STEP/SVG, both overlays, package, and a final empty git status. Raw record:/tmp/tiger-v2-clean-7j5orqnn/summary.json.
- Hosted1b9527d CI34780185009 and CAD34780184980 both succeeded and uploaded complete artifacts. Later standoff refactor still requires final hosted confirmation.
- Exact selected-arm default-all-format and STEP-only CLI smokes, latest-source provenance refresh, and any tagged publication remain coordinator follow-ups.

## Follow-up inspection: builder/dependencies and completed baseline clean job

After the matrix snapshot, revision `148785a34eb9c06e920188cfad494dd359ad4619`
extracts `parts/standoff.py`; assembly now calls its local profile/solid builders
and applies shared datum placements. Source and added geometry tests inspected.
`/tmp/tiger-standoff-green.log` records21 passing standoff+assembly tests. Action1
is closed. `.agent/TASKS.md` now contains an actual Mermaid prerequisite graph,
including geometry changes invalidating downstream evidence. Action2 is closed.
A documentation specialist is adding current-status indexes/contract fields to
historical handoffs; final record integration remains coordinator-owned.

The baseline clean job completed successfully for commit `1b9527d`:
`/tmp/tiger-v2-clean-7j5orqnn/summary.json` records all command return codes0,
including frozen sync, lint, types, full tests, build, all five validates, default
full export, default drawing, selected-arm STEP+SVG export, parameters, both
overlays and package. Final `git-clean.stdout.log` is empty. This is actual local
clean-checkout evidence for that revision, not proof for subsequent source edits.

Independent artifact inspection in that checkout found all84 dist artifact
hashes correct, all105 cad-artifacts checksum entries correct and all9
release-assets checksum entries correct. The selected-arm exact invocation
`export --part arm --format step --format svg --output artifacts/selected-arm`
returned0, supplying installed CLI selection/format evidence absent at the first
snapshot. Default format directories and full final packaging exist in this clean
checkout.

**New required provenance correction (§38):** Despite the clean checkout and empty
final status, its default `dist/manifest.json` records `git_dirty: true`.
`export/artifacts.py` calls `_provenance()` while its unignored temporary directory
`.fpv-export-*` exists under the project root (the parent of default `dist`). The
export therefore contaminates its own Git status measurement. Capture source
provenance before creating output/staging directories, or exclude only the known
exporter-owned temporary path; do not suppress real source modifications. Root
was notified with the exact source cause and actual artifact evidence. This is a
metadata defect, not failed CAD geometry, but clean-source release provenance
must be corrected and verified before completion.

Hosted CI/CAD and tag publication remain pending in this review. A successful
baseline local job does not establish those outcomes or waive verification of
the later standoff/provenance changes.

Coordinator provenance closure: snapshot now occurs before directory/staging writes; two negative regressions first failed then passed, and all18export tests (actualFreeCAD included) pass. Final cleanmanifest assertion remains in the clean-run acceptance script.
