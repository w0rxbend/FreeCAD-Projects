# Handoff provenance and current disposition

STATUS: Historical handoff contract audit completed on 2026-09-13. This index
does not declare the full PLAN complete. The coordinator's [current state](../STATE.md)
owns the integration milestone and remaining work; active reviewers own their
current review records.

FILES CHANGED: This index was created. Retrospective addenda were appended to
`scan1.md`, `scan2.md`, `standards.md`, `reconciliation.md`, `calibration-review.md`,
`assembly-photo.md`, `architecture.md`, `assembly.md`, `geometry-review.md`,
`equipment.md`, `ci.md` and `final-review.md`. Original text was preserved verbatim.
The active/reserved `acceptance-review.md`, `plan-audit.md`, `release-audit.md` and
`exports.md` were not edited by this audit.

RESULT: Historical files now expose the PLAN §59 fields and point to superseding
evidence. Initial hypotheses, failed checks and implementation limitations remain
visible as historical records. They are neither silently rewritten as successful
results nor assumed to be current blockers.

MEASUREMENTS/DECISIONS: Later user evidence establishes A4 tracing-paper
provenance, 5 mm arms and 2 mm for all three plates. Reconciliation establishes
same-direction plate registration and handed arm placement. The adopted vertical
order is rear plate → arms → camera plate → raised top deck; H=25 mm remains
provisional. The analytical root is explicitly 35 × 29 mm versus the approximately
38 × 31 mm tracing. See the maintained
[reconstruction guide](../../docs/blueprint-reconstruction.md) and
[independent acceptance review](acceptance-review.md) for the resulting model and
its limitations. None of these later decisions is attributed retroactively to an
independent analyst who had not yet received that evidence.

| Handoff | Original task evidence | Superseding/current disposition |
| --- | --- | --- |
| [scan1.md](scan1.md) | Independent native-pixel observations; tentative scale and arm interpretation | Observations retained; A4/user stock evidence and reconciliation resolve later scale/placement decisions |
| [scan2.md](scan2.md) | Independent plate features, missing/asymmetric marks and unresolved roles | Observations retained; reconciliation/photo review establish registration and provisional roles |
| [standards.md](standards.md) | Candidate electronics/motor conventions and manufacturer examples | Standard-only calibration and reversal hypothesis superseded; no catalogue product is identified as user hardware |
| [reconciliation.md](reconciliation.md) | Serialized transforms, named correspondences and explicit later A4 update | Current source reconciliation; analytical idealization and fit review are separate subsequent evidence |
| [calibration-review.md](calibration-review.md) | Independent registration residuals and original conditional-scale limits | Later user A4 confirmation supersedes missing physical page anchor; exact hardware/physical qualification remains limited |
| [assembly-photo.md](assembly-photo.md) | Photo-supported roles, layer order and algebraic support-length difference | Adopted as explicit reconstruction interpretation; photograph remains unsuitable for measuring H |
| [architecture.md](architecture.md) | Immutable contracts, shared-interface primitives and initial 47-test foundation | Detailed profiles/layout/assembly now implemented; foundation-stage `None` statements are historical |
| [assembly.md](assembly.md) | Measured gates and original root/ligament failures; then four canonical profile aliases | Later fixes and 15-profile inventory accepted independently; original failure output remains useful causal evidence |
| [geometry-review.md](geometry-review.md) | Analytical contour fixes, 35 × 29 mm root decision and 54 geometry tests | Later acceptance reviews actual final overlays and geometry; root departure remains explicit |
| [equipment.md](equipment.md) | Nominal proxies, shared keepouts and 12 focused tests | Integrated into normal assembly validation; no claim of measured purchased-equipment compatibility |
| [ci.md](ci.md) | Initial workflow/package implementation and 11 packaging tests | Parent workflow installation, stronger integrity gates and pinned-runtime checks superseded by release audit |
| [final-review.md](final-review.md) | Three reproduced required defects in initial integration | Closure independently documented in acceptance review; initial “request changes” remains a historical verdict |
| [acceptance-review.md](acceptance-review.md) | Final overlay/mechanical review and runtime-gate correction verification | Active review record; full-goal conclusion still depends on current provenance and separate release/clean-checkout evidence |
| [exports.md](exports.md) | Export implementation, actual full-frame geometry, native reopen and rendering evidence | Export owner maintains this current handoff; coordinator refreshes final artifacts from the final revision |
| [release-audit.md](release-audit.md) | Packaging integrity, active workflow placement, pinned AppImage and headless native tests | Release owner maintains current audit; local verification does not itself prove hosted publication |
| [plan-audit.md](plan-audit.md) | Full sections 1–76 requirement map and concrete remaining actions at its inspected revision | Coordinator owns closure evidence and subsequent source/provenance refresh; this index addresses historical record clarity only |

ASSUMPTIONS: This audit reports what the inspected records prove and delegates
current mutable status to their owners. A date alone does not make a handoff newer
than another file. Source measurements retain their original confidence; tests
reported by an earlier agent are historical execution evidence, not an assertion
that this audit reran them against the current tree.

VALIDATION EXECUTED: Read PLAN §59 and every existing handoff; checked for the
eight exact required field labels; inspected current STATE and acceptance/release
records; added missing labels through retrospective summaries; verified that all
12 modified historical files retain their entire original byte sequence as a
prefix. Checked this index's local Markdown targets. No CAD, export, workflow,
web or physical test was executed by this documentation audit.

KNOWN LIMITATIONS: Several original narrative handoffs did not provide a complete
per-agent diff. Their addenda identify the files explicitly supported by the
original record and do not invent a complete edit history from a shared worktree.
The four reserved current review/export records remain under other owners;
missing exact field labels found there were reported to the coordinator for those
owners to complete. The separate full-plan audit records revision-specific
remaining actions; this index is not a substitute for requirement-by-requirement
acceptance.

FOLLOW-UP TASKS: Coordinator should refresh STATE/TASKS after current jobs,
recheck §59 labels across newly completed reserved handoffs, and inspect the final
plan/release evidence before changing the full goal's status. Future handoffs
should use the eight required fields when first written and link later corrections
as dated addenda rather than replacing original observations.

## Coordinator execution snapshot — 2026-09-13

The coordinator subsequently reported the following completed execution evidence
for committed revision `1b9527d`: clean pipeline with 193 tests under the native
FreeCAD runtime, all five presets, all export formats, independent drawings,
explicit selected-arm STEP/SVG export, both overlays, release packaging and a clean
Git worktree. Hosted CI run `34780185009` and CAD run `34780184980` were both
reported successful for that revision.

The coordinator also identified the newer source revision as `148785a`. The
successful `1b9527d` jobs are evidence for their tested revision; this index does
not transfer their status automatically to subsequent source or documentation
commits. Final hosted checks and STATE/TASKS refresh remain coordinator-owned.
These execution results were relayed by the coordinator and were not independently
rerun or queried by this documentation audit.
