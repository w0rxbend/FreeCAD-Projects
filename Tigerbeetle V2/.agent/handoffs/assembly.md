# Assembly continuation handoff

Current builder creates 15 named physical parts (3 plates,4 arms,8 hollow standoffs)
and four canonical XY manufacturing profiles. Photo stack is0–2,2–7,7–9,34–36mm.
Shared datum transforms alone drive placements. No overlap exceptions are allowed.

Reference assembly test currently FAILS actual arm material collisions:
front L/R103.910568mm3; front-left/rear-left38.482256mm3;
front-right/rear-right38.482256mm3;rear L/R191.141394mm3.
Geometry owner notified; no arbitrary placement changes made.
Manufacturing wire-distance gate also finds scan2_long hole3/4 outer ligament
1.004252mm below configured1.5mm; geometry owner notified.

New manufacturing.py measures each outer/hole and every hole/hole distance.
New clearances.py accepts explicit placed ClearanceEnvelope solids and tests each
against every frame part, plus checks measured top face clearance. Missing
FC/ESC/camera/side-panel dimensions are reported unverified; never infer fit.
Tests/assembly/test_mechanical_gates.py first failed missing modules; implementation
is now under focused test. Not yet integrated into validate_assembly at this save.

Remaining bounded work: run focused test, integrate gates, extend actual bore gate
for motor holes and full bore void; run all assembly tests once geometry corrected.

## Implemented after initial save

Manufacturing/clearance gates now integrated in validate_assembly; optional keyword
`envelopes=(ClearanceEnvelope(name, placed_part, minimum_gap), ...)` validates both
frame/equipment and equipment/equipment distances and overlap. Missing equipment
stays listed explicitly. Four focused tests passed before adding fifth mutual-
equipment collision test (observed RED before implementation; final run active).
Bore gate now checks all88reference bores, including four motor mounts and center
bores, plus a full-volume witness cylinder so hidden internal plugs fail.
Independent reference interfaces PASS maxerror2.84e-14mm; symmetry PASS9pairs,0mm3.
Scoped Ruff check/format clean. Full assembly awaits geometry owner root fixes.

## Final bounded-slice verification

- `pytest tests/assembly/test_mechanical_gates.py -q`:5passed in5.51s.
- `pytest tests/assembly -q`:7passed,8failed in21.43s. Every failure is
  existing arm material overlap (including shifted-bore test whose expected
  bore message is preempted by collision gate); geometry_fix owns contour repair.
- Scoped Ruff validation:allchecks passed.
- No processes remain from this task.

Profile map contract remains canonical aliases ONLY:
`arm`, `scan1_body`, `scan2_broad`, `scan2_long`. Plate profiles live atZ0;
arm profile is canonical handed XY atZ0 before placement/mirroring. Physical
`parts` map and compound haveall15names. For per-part manufacturing export,
export owner must derive each arm's handed local profile via placement mirror
(and rotation if exporting assembly-plan orientation), and standoff annulus
from the built standoff or shared diameter parameters. Profiles map has NOT
been expanded silently because existing tests/export builder consume this
canonical contract. Parent explicitly permitted documenting this limitation.


## Retrospective handoff audit — 2026-09-13

This addendum was written after the original task. It preserves the observations
and test results above; it does not attribute later knowledge to the original
reviewer. Current disposition is indexed in [handoff-index.md](handoff-index.md).
Later evidence is in [acceptance-review.md](acceptance-review.md), the maintained
[reconstruction guide](../../docs/blueprint-reconstruction.md), and
[current state](../STATE.md). Historical follow-ups are not automatically current
blockers; use those records to determine which were completed or remain open.

STATUS: Historical assembly slice completed with the failures recorded above;
later geometry and integration work superseded those failure/status statements.

FILES CHANGED: The original record identifies `validation/manufacturing.py`,
`validation/clearances.py`, assembly validation integration, bore validation and
`tests/assembly/test_mechanical_gates.py` under `src/fpv_frame` / `tests` as
applicable. It did not enumerate a complete per-agent diff. This audit appends
only to this handoff and creates the index.

RESULT: Added measured assembly manufacturing, equipment-clearance and bore gates.
The then-failing root collisions and top-plate ligament were passed to the
geometry owner rather than excused by placement offsets or overlap exceptions.

MEASUREMENTS/DECISIONS: The original slice measured 88 bores and nine symmetry
comparisons. The later model provides 15 physical profiles matching its 15 parts;
the four-canonical-alias contract above is historical and superseded.

ASSUMPTIONS: Plate stock is user-confirmed 2 mm and arm stock 5 mm. H=25 mm and
purchased hardware details remain provisional. Nominal equipment envelopes were
integrated later and retain their engineering-assumption qualification.

VALIDATION EXECUTED: Original results were five focused tests passing, then seven
passing/eight failing assembly tests, plus scoped Ruff. Those failures are retained
above. Acceptance-review.md records subsequent closure; this audit ran no CAD tests.

KNOWN LIMITATIONS: This original slice did not prove a passing complete assembly;
its profile inventory contract and missing-equipment status were later changed.
No exact per-agent edit history is inferred from the current combined worktree.

FOLLOW-UP TASKS: Read acceptance-review.md for closed geometric defects and
STATE.md for remaining current integration/release work. Do not reopen the old
collision failures without reproducing them against the current model.
