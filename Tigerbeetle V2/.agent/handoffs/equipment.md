# Equipment clearance implementation handoff

Implemented in owned files only:

- `src/fpv_frame/parameters/equipment.py`: immutable configurable nominal FC, ESC,
  camera, board spacing, stack hardware, PCB keepouts and required clearance.
  Dimensions are finite positive; PCB keepout must provide radial clearance.
  Provenance explicitly says engineering assumption, not user-confirmed hardware.
- `src/fpv_frame/validation/equipment.py`: API
  `design_equipment_envelopes(model, parameters) -> tuple[ClearanceEnvelope, ...]`.
  Generates FC/ESC/camera plus four named stack hardware proxies. Board bore and
  hardware axes derive from shared `central_stack_square`. PCB footprint must
  contain full keepout circles. Z comes from the camera plate upper face, and XY
  from shared layout datums. Geometry is assessed by the existing solid-distance
  and overlap clearance gate; this factory does not alter frame production parts.
- `tests/assembly/test_equipment.py`: 12 passing tests covering nominal fit,
  reference elevations, oversized FC/camera collisions, lowered-top collision,
  changed stack pitch and bore/hardware separation, invalid dimensions, radial
  clearance and mounting-keepout containment.
- `docs/equipment.md`: baseline values, provenance, assessment bounds and explicit
  side-panel N/A justification (no scanned side-panel part supplied).

Root integration remaining: add `FrameParameters.equipment` default factory;
invoke envelope factory in normal clearance reporting; report the design-envelope
qualification and side panels as N/A instead of claiming measured compatibility.
No git operations performed.

Validation: `.venv/bin/pytest -q tests/assembly/test_equipment.py` → 12 passed in
11.55 seconds. Ruff on all three Python files passed. Mypy on both source files
passed. Root runs final full integration suite.

Collision tests use FC 80×80 and camera 50×40 footprints. Width-only enlargement
does not reach longitudinal standoffs and can legitimately fit the open frame.


## Retrospective handoff audit — 2026-09-13

This addendum was written after the original task. It preserves the observations
and test results above; it does not attribute later knowledge to the original
reviewer. Current disposition is indexed in [handoff-index.md](handoff-index.md).
Later evidence is in [acceptance-review.md](acceptance-review.md), the maintained
[reconstruction guide](../../docs/blueprint-reconstruction.md), and
[current state](../STATE.md). Historical follow-ups are not automatically current
blockers; use those records to determine which were completed or remain open.

STATUS: Equipment-envelope slice completed; the root integration noted above
was subsequently implemented, as inspected in acceptance-review.md.

FILES CHANGED: `src/fpv_frame/parameters/equipment.py`,
`src/fpv_frame/validation/equipment.py`, `tests/assembly/test_equipment.py`,
`docs/equipment.md` and this historical handoff. This addendum is an audit update.

RESULT: Configurable nominal equipment proxies follow shared axes and plate
faces, including PCB mounting keepouts and stack-hardware envelopes.

MEASUREMENTS/DECISIONS: Baseline FC/ESC envelopes are 40 × 40 × 8 mm, camera is
20 × 20 × 20 mm, stack hardware outside diameter is 5 mm and PCB keepouts are
6 mm. These are selected design bounds, not measured user hardware dimensions.

ASSUMPTIONS: Nominal envelope placement and required gaps are engineering inputs.
Side panels are not applicable to the supplied dimensioned three-plate model;
photo-visible accessory details are not inferred as manufactured profiles.

VALIDATION EXECUTED: Original slice passed 12 equipment tests in 11.55 seconds,
scoped Ruff and strict mypy. The later acceptance review inspected integrated
equipment collision/clearance checks. This audit ran no additional equipment tests.

KNOWN LIMITATIONS: Passing these solids does not establish fit of connectors,
wiring, exact camera mounts or other unspecified purchased equipment.

FOLLOW-UP TASKS: Use current integrated reports and STATE.md for release evidence;
replace nominal envelopes with measured geometry when specific equipment is chosen.
