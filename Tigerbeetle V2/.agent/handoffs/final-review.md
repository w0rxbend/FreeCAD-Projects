# Independent final review — initial implementation audit

STATUS: Request changes. Bounded runtime and drawing defects found; completion is not proven.

FILES CHANGED: This handoff only. All implementation inspected read-only.

RESULT:

1. **Required, build blocker:** `src/fpv_frame/validation/manufacturing.py:14` applies carbon edge ligament policy to every profile, including purchased tubular standoffs added in `assembly/frame.py:45`. Direct `validate_assembly(build_assembly(get_preset()))` fails with `standoff_front_arm_outer_pair_left: minimum edge/inter-feature ligament 1.000000 mm is below required 1.500000 mm`. Distinguish carbon manufacturing profiles from stock hardware instead of weakening the carbon rule. Re-run nominal/all-preset validation.
2. **Required, clearance validation:** `src/fpv_frame/validation/clearances.py:41` never applies `ManufacturingParameters.general_clearance` to arm roots. Search finds its only geometry consumer in a nominal test. Reproduction below proves runtime reports valid with a 2 mm required gap while actual minimum arm gap is 0.2908530645592933 mm. Enforce/report all six arm pair gaps in runtime, separate from intentional face contacts.
3. **Required, drawing orientation:** `src/fpv_frame/drawing/svg.py:92` labels a camera on -Y as `front`. The accepted system puts front on +Y. Use +Y camera for `assembly_front.svg`; existing test only proves the file exists.

Clearance reproduction (edge_minimum=1 solely isolates defect 2 from defect 1; do not adopt that lowered value):

```python
from dataclasses import replace
from itertools import combinations
from fpv_frame.assembly import build_assembly, validate_assembly
from fpv_frame.parameters.presets import get_preset
p = get_preset()
p = replace(p, manufacturing=replace(p.manufacturing,
                                     general_clearance=2, edge_minimum=1))
m = build_assembly(p)
print(min(a.distance_to(b) for (na, a), (nb, b)
          in combinations(m.parts.items(), 2)
          if na.startswith('arm_') and nb.startswith('arm_')))
print(validate_assembly(m)['valid'])
# 0.2908530645592933
# True
```

MEASUREMENTS/DECISIONS:

- Runtime BREP symmetry genuinely compares reflected physical material both ways; it is not merely a coordinate assertion. Nominal isolated validation measured zero symmetric material difference, 88 bores with <=2.85e-14 mm error, and zero intersection volume across 105 material pairs.
- Matching carbon bores and standoff axes originate in shared layout. Arm copies originate in one canonical solid and explicit reflection/rotation. No independently invented mating tab/slot pair was found; no physical carbon tab joint is established by the source interpretation, so the unused generic TabSlotInterface alone is not a missing physical component.
- Planar profiles directly drive both extrusion and SVG. Arm export profiles are local mirrored manufacturing faces; assembly solids apply placement afterward. This is legitimate, not an SVG/solid mismatch.
- Plate station deformation follows shared mounting rows; structural bore sizes come from the shared layout. Nonstructural contour/aperture dimensions remain sparse semantic reconstruction constants, not pixel traces.
- Current FCStd worker imports STEP, validates shapes, saves, reopens, and compares names/counts/volumes. Actual full-frame conversion was not rerun by this reviewer.
- Repeated tiny-fixture export produced identical STL and SVG bytes; assembled STEP and 3MF bytes differed. Treat as a documented limitation unless byte identity is promised: PLAN explicitly requires clean rebuild/model reproducibility, not byte-identical archive containers.

ASSUMPTIONS / KNOWN LIMITATIONS:

- User confirms A4 physical tracing, 5 mm arm stock and 2 mm plates. Photo-based plate ordering and estimated H=25 mm remain recorded as assumptions.
- Accepted root correction from traced ~38x31 to 35x29 is explicitly documented in geometry-review.md; this review did not reverse that accepted integration decision.
- `validate_clearances` transparently reports FC/ESC/camera/side_panels unverified without supplied equipment envelopes. Current CLI has no envelope input. PLAN §23 and manufacturing gate cannot be presented as actual equipment-fit qualification without dimensions/envelopes. Supporting generic supplied-envelope validation is useful but does not prove a particular installed electronics/camera fit.
- Known XY plane versus padded OCCT bbox issue is owned by root and excluded from duplicate findings.
- Root is integrating CLI/deviation diagnostics and CI agent owns pending workflows/docs; those changing areas are not declared complete here.

VALIDATION EXECUTED:

- Inspected PLAN in full, relevant tests before source, then part/layout/interface/assembly/manufacturing/symmetry/clearance/export/drawing/CLI/deviation implementations.
- Executed direct full-assembly clearance reproduction twice: first exposed baseline stock-hardware gate failure; second isolated missing general-gap enforcement and passed with invalid requested clearance.
- Exported a named tiny fixture twice in separate temporary directories and compared every generated file hash (STEP/STL/3MF/SVG/manifest).
- No source edits, commits, or full-suite rerun by this reviewer.

FOLLOW-UP TASKS:

- Root: fix three required findings, add targeted regression for increased required arm gap, rerun assembly/preset gates.
- Root: complete regeneration and overlay review, full-frame all-format export/reopen, source manifest and clean-checkout CI/release validation before claiming PLAN completion.


## Retrospective handoff audit — 2026-09-13

This addendum was written after the original task. It preserves the observations
and test results above; it does not attribute later knowledge to the original
reviewer. Current disposition is indexed in [handoff-index.md](handoff-index.md).
Later evidence is in [acceptance-review.md](acceptance-review.md), the maintained
[reconstruction guide](../../docs/blueprint-reconstruction.md), and
[current state](../STATE.md). Historical follow-ups are not automatically current
blockers; use those records to determine which were completed or remain open.

ASSUMPTIONS: This initial review used the then-current explicit reconstruction
assumptions recorded above. Later nominal equipment envelopes are engineering
design inputs, not measurements of the user's FC, ESC or camera.

KNOWN LIMITATIONS: The three original required findings were historical defects.
Their closure and the later profile-inventory gate correction are independently
recorded in acceptance-review.md. This addendum does not rerun those checks;
release freshness and clean-checkout evidence belong to the current integration
and release records.
